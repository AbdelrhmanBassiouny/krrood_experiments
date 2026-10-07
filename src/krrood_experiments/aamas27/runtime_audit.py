"""
Runtime closure audit: does the knowledge base of the running KRROOD agent stay equal to the OWL 2 RL closure?

The soundness audit (:mod:`krrood_experiments.aamas27.soundness_audit`) compares the knowledge base right after
Ontomatic loaded the raw OWL2Bench data. This audit compares it while the delivery robot of the agent loop
(:mod:`krrood_experiments.aamas27.agent_loop`) runs: the KRROOD variant asserts the perceived facts through its own
``perceive`` (property-descriptor assignments), the loop runs unchanged (decision queries, actions), and at every
checkpoint (after ``k`` steps) the objects and attribute values are compared with the OWL 2 RL closure of the raw data
plus the statements of the events of the first ``k`` steps.

* Reference: Nemo with ``owl2rl.rls`` (:func:`~krrood_experiments.aamas27.loading_worker.run_nemo_owlrl`) on the raw
  data serialised as N-Triples plus the events' statements exactly as the GraphDB variant inserts them
  (:func:`~krrood_experiments.aamas27.agent_loop.rdf_mirror.event_triples`).
* Normalisation of both sides as :mod:`~krrood_experiments.aamas27.closure_comparison` does it (class memberships,
  object-property pairs and data-property values of individuals, OWL2Bench vocabulary only, ``Role`` excluded), with
  KRROOD's side read from the registry with the functions of the soundness audit. The individuals are the declared
  ``owl:NamedIndividual`` subjects of the raw data plus the people created by the enrollment events so far.
* Application data is excluded on both sides: the campus places are not individuals (they are not in the registry and
  have no statements in the reference), and the attributes that link to them (``taught_in``, ``mailbox``) are not
  OWL2Bench properties.

For every fact the reference has and KRROOD does not store (``missing``), the audit records which OWL 2 RL rules derive
it in one step from the reference closure (cls-hv2, cls-svf1, cls-int1, cls-uni via cax-eqc/cax-sco, cax-sco from a
named class, prp-dom, prp-rng), and for missing class memberships whether KRROOD answers them on demand with the
class axioms of the generated model (``model.C.axiom(x)``, as the agent's ticket query does for ``T20CricketFan``).

* ``missing``: in the reference closure, not stored by KRROOD.
* ``extra``: stored by KRROOD, not in the reference closure.

Run one seed in a fresh process (the loader's global state is not reset between runs)::

    python -m krrood_experiments.aamas27.runtime_audit --seed 0 --steps 200 --checkpoints 0,10,50,100,200 \\
        --output seed0.json --work-dir /tmp/runtime_audit
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .agent_loop.events import Enrollment, StepPerception
from .agent_loop.krrood_variant import KrroodVariant
from .agent_loop.loop import run_agent_loop
from .agent_loop.rdf_mirror import event_triples, object_term
from .agent_loop.robot import Robot
from .agent_loop.scenario import Scenario, generate_scenario
from .closure_comparison import Fact, compare, load, normalised_facts, vocabulary
from .environment import UNREASONED_FILE, write_json
from .loading_worker import run_nemo_owlrl
from .soundness_audit import (
    EXAMPLES,
    IGNORED_CLASSES,
    NAMESPACE,
    krrood_data_pairs,
    krrood_property_pairs,
    krrood_types,
    model_classes,
)

APPLICATION_ATTRIBUTES = ("taught_in", "mailbox")
"""
Attributes the agent loop attaches to the loaded objects; they hold campus places, which are not OWL2Bench individuals.
"""

DEFAULT_CHECKPOINTS = (0, 10, 50, 100, 200)
"""
Numbers of completed steps after which the knowledge base is compared.
"""


def local(uri: str) -> str:
    """
    :param uri: An OWL2Bench IRI.
    :return: Its local name.
    """
    return uri[len(NAMESPACE):] if uri.startswith(NAMESPACE) else uri


def triples_of_steps(perceptions: Sequence[StepPerception]) -> List[Tuple[str, str, str]]:
    """
    :param perceptions: The perceptions of the completed steps.
    :return: The statements of their knowledge events, as the GraphDB variant inserts them.
    """
    return [triple for perception in perceptions for event in perception.knowledge_events
            for triple in event_triples(event)]


def new_people(perceptions: Sequence[StepPerception]) -> Set[str]:
    """
    :param perceptions: The perceptions of the completed steps.
    :return: The IRIs of the people created by their enrollment events.
    """
    return {event.person for perception in perceptions for event in perception.knowledge_events
            if isinstance(event, Enrollment)}


@dataclass
class Vocabulary:
    """
    What the normalisation of both sides needs.
    """

    named_individuals: Set[str]
    """
    The declared ``owl:NamedIndividual`` subjects of the raw data.
    """
    object_properties: Set[str]
    """
    IRIs of the OWL2Bench object properties.
    """
    data_properties: Set[str]
    """
    IRIs of the OWL2Bench data properties.
    """

    def individuals(self, perceptions: Sequence[StepPerception]) -> Set[str]:
        """
        :param perceptions: The perceptions of the completed steps.
        :return: The individuals compared after these steps.
        """
        return self.named_individuals | new_people(perceptions)


def krrood_facts(registry, individuals: Set[str], vocabulary_: Vocabulary) -> Set[Fact]:
    """
    :param registry: The KRROOD instance registry (with the objects created at runtime registered).
    :param individuals: The compared individuals.
    :param vocabulary_: The vocabulary.
    :return: KRROOD's stored facts, normalised like :func:`~krrood_experiments.aamas27.closure_comparison.normalised_facts`.
    """
    facts: Set[Fact] = set()
    for individual, class_uris in krrood_types(registry).items():
        if individual not in individuals:
            continue
        for class_uri in class_uris:
            if class_uri.startswith(NAMESPACE) and local(class_uri) not in IGNORED_CLASSES:
                facts.add(("class", local(class_uri), individual, ""))
    object_names = sorted(local(p) for p in vocabulary_.object_properties)
    for name, pairs in krrood_property_pairs(registry, object_names).items():
        for subject, value in pairs:
            if subject in individuals and value in individuals:
                facts.add(("object", name, subject, value))
    data_names = sorted(local(p) for p in vocabulary_.data_properties)
    for name, pairs in krrood_data_pairs(registry, data_names).items():
        for subject, value in pairs:
            if subject in individuals:
                facts.add(("data", name, subject, value))
    return facts


def restriction_label(graph, node) -> str:
    """
    :param graph: The reference closure.
    :param node: A class expression (blank node) of the ontology.
    :return: The OWL 2 RL rule that types individuals with it, and the expression in short form.
    """
    from rdflib import OWL, BNode
    from rdflib.collection import Collection

    prop = graph.value(node, OWL.onProperty)
    for predicate, rule in ((OWL.hasValue, "cls-hv2"), (OWL.someValuesFrom, "cls-svf1"),
                            (OWL.allValuesFrom, "cls-avf"), (OWL.maxCardinality, "cls-maxc"),
                            (OWL.maxQualifiedCardinality, "cls-maxqc")):
        value = graph.value(node, predicate)
        if value is not None:
            return f"{rule} {predicate.split('#')[-1]}({local(str(prop))}, {local(str(value))})"
    for predicate, rule in ((OWL.intersectionOf, "cls-int1"), (OWL.unionOf, "cls-uni")):
        members = graph.value(node, predicate)
        if members is not None:
            rendered = [local(str(m)) if not isinstance(m, BNode) else restriction_label(graph, m)
                        for m in Collection(graph, members)]
            return f"{rule} {predicate.split('#')[-1]}({', '.join(rendered)})"
    if graph.value(node, OWL.oneOf) is not None:
        return "cls-oo oneOf"
    return "class expression"


def class_justifications(graph, class_name: str, individual: str, stored: Set[Fact]) -> List[str]:
    """
    Find the OWL 2 RL rules that derive ``individual rdf:type class`` in one step from the reference closure.

    :param graph: The reference closure.
    :param class_name: Local name of the class.
    :param individual: The individual.
    :param stored: KRROOD's stored facts (to tell whether a premise class membership is stored).
    :return: One label per applicable rule instance.
    """
    from rdflib import OWL, RDF, RDFS, BNode, URIRef

    cls = URIRef(NAMESPACE + class_name)
    subject = URIRef(individual)
    types = set(graph.objects(subject, RDF.type))
    labels = set()
    premises = ([(c, "cax-eqc") for c in graph.subjects(OWL.equivalentClass, cls)]
                + [(c, "cax-eqc") for c in graph.objects(cls, OWL.equivalentClass)]
                + [(c, "cax-sco") for c in graph.subjects(RDFS.subClassOf, cls)])
    for premise, link in premises:
        if premise == cls or premise not in types:
            continue
        if isinstance(premise, BNode):
            labels.add(f"{restriction_label(graph, premise)} + {link}")
        elif str(premise).startswith(NAMESPACE) and local(str(premise)) not in IGNORED_CLASSES:
            state = "stored" if ("class", local(str(premise)), individual, "") in stored else "not stored"
            labels.add(f"{link} from {local(str(premise))} ({state} in KRROOD)")
    for prop in graph.subjects(RDFS.domain, cls):
        if (subject, prop, None) in graph:
            labels.add(f"prp-dom {local(str(prop))}")
    for prop in graph.subjects(RDFS.range, cls):
        if (None, prop, subject) in graph:
            labels.add(f"prp-rng {local(str(prop))}")
    return sorted(labels) or ["no one-step justification found"]


def axiom_taker_type(owl_class: type) -> type:
    """
    :param owl_class: A generated class with an ``axiom``.
    :return: The type of the objects its axiom is evaluated on (the role taker of a role, else the superclass).
    """
    from krrood.class_diagrams.utils import Role

    if issubclass(owl_class, Role):
        return owl_class.get_role_taker_type()
    return owl_class.__bases__[0]


def axiom_answers(registry, owl_class: type, individuals: Set[str]) -> Set[str]:
    """
    Answer the class membership on demand: the individuals one of whose objects satisfies the class axiom.

    :param registry: The KRROOD instance registry.
    :param owl_class: A generated class with its own ``axiom``.
    :param individuals: The compared individuals.
    :return: Their IRIs.
    """
    from krrood.entity_query_language.entity import entity, variable
    from krrood.entity_query_language.entity_result_processors import an

    taker = axiom_taker_type(owl_class)
    domain = [instance for uri, instances in registry._by_uri.items() if str(uri) in individuals
              for instance in instances if isinstance(instance, taker)]
    candidate = variable(taker, domain=domain)
    query = an(entity(candidate).where(*owl_class.axiom(candidate)))
    return {str(result.uri) for result in query.evaluate()}


def classes_with_own_axiom() -> Dict[str, type]:
    """
    :return: Local name to generated class, for the classes that define their own ``axiom``.
    """
    return {local(uri): cls for uri, cls in model_classes().items()
            if "axiom" in vars(cls) and cls.cls_uri == uri}


def on_demand_report(registry, class_names: Iterable[str], individuals: Set[str], stored: Set[Fact],
                     reference: Set[Fact], missing: Set[Fact]) -> Dict[str, Any]:
    """
    For every class with missing memberships: stored memberships plus the answers of the axiom queries of the class and
    of its subclasses (``model.C.axiom(x)``), compared with the reference.

    :return: Per class: the axiom classes queried, sizes, the missing facts the queries answer, and the differences of
     the on-demand view with the reference.
    """
    from krrood.class_diagrams.utils import issubclass_or_role

    by_uri = model_classes()
    axioms = classes_with_own_axiom()
    report = {}
    answers_cache: Dict[str, Set[str]] = {}
    for name in sorted(class_names):
        owl_class = by_uri.get(NAMESPACE + name)
        queried = sorted(d for d, cls in axioms.items() if owl_class is not None and issubclass_or_role(cls, owl_class))
        answered: Set[str] = set()
        seconds = 0.0
        for axiom_class in queried:
            if axiom_class not in answers_cache:
                start = time.perf_counter()
                answers_cache[axiom_class] = axiom_answers(registry, axioms[axiom_class], individuals)
                seconds += time.perf_counter() - start
            answered |= answers_cache[axiom_class]
        stored_members = {f[2] for f in stored if f[0] == "class" and f[1] == name}
        reference_members = {f[2] for f in reference if f[0] == "class" and f[1] == name}
        missing_members = {f[2] for f in missing if f[0] == "class" and f[1] == name}
        on_demand = stored_members | answered
        report[name] = {
            "axiom_classes_queried": queried,
            # The loader evaluates the axioms on its AnonymousClass candidates, which have a ``types`` attribute; the
            # live objects do not, so an axiom that tests ``candidate.types`` has no solution on them.
            "axiom_classes_testing_types_attribute": [
                d for d in queried if ".types" in inspect.getsource(axioms[d].axiom)],
            "reference": len(reference_members),
            "stored": len(stored_members),
            "missing_stored": len(missing_members),
            "axiom_query_answers": len(answered),
            "axiom_query_answers_not_in_reference": len(answered - reference_members),
            "missing_answered_by_axiom_query": len(missing_members & answered),
            "on_demand": len(on_demand),
            "on_demand_missing": len(reference_members - on_demand),
            "on_demand_extra": len(on_demand - reference_members),
            "on_demand_missing_examples": sorted(reference_members - on_demand)[:EXAMPLES],
            "on_demand_extra_examples": sorted(on_demand - reference_members)[:EXAMPLES],
            "query_seconds": seconds,
        }
    return report


@dataclass
class CheckpointAuditor:
    """
    Computes the reference closure and compares it with KRROOD's knowledge base after a number of steps.
    """

    scenario: Scenario
    """
    The scenario of the loop.
    """
    vocabulary: Vocabulary
    """
    The vocabulary of the raw data.
    """
    raw_ntriples: Path
    """
    The raw data serialised as N-Triples.
    """
    work_directory: Path
    """
    Where the Nemo input and closure files are written (overwritten at every checkpoint).
    """
    nemo_binary: str
    """
    The ``nmo`` executable.
    """
    checkpoints: Set[int]
    """
    The checkpoints.
    """
    results: List[Dict[str, Any]] = field(default_factory=list)
    """
    One report per checkpoint.
    """

    def audit(self, registry, steps: int) -> Dict[str, Any]:
        """
        :param registry: KRROOD's registry after ``steps`` completed steps.
        :param steps: Number of completed steps.
        :return: The checkpoint report (also appended to :attr:`results`).
        """
        start = time.perf_counter()
        perceptions = self.scenario.perceptions[:steps]
        triples = triples_of_steps(perceptions)
        individuals = self.vocabulary.individuals(perceptions)
        nemo_input = self.work_directory / "input.nt"
        closure_file = self.work_directory / "closure.nt"
        with open(nemo_input, "wb") as stream:
            stream.write(self.raw_ntriples.read_bytes())
            for subject, predicate, value in triples:
                stream.write(f"<{subject}> <{predicate}> {object_term(value)} .\n".encode())
        nemo = run_nemo_owlrl(nemo_input, self.nemo_binary, closure_file)
        reference_start = time.perf_counter()
        graph = load(closure_file)
        reference = normalised_facts(graph, individuals, self.vocabulary.object_properties,
                                     self.vocabulary.data_properties)
        reference_seconds = time.perf_counter() - reference_start
        krrood_start = time.perf_counter()
        stored = krrood_facts(registry, individuals, self.vocabulary)
        krrood_seconds = time.perf_counter() - krrood_start
        comparison = compare(stored, reference)
        missing = reference - stored
        extra = stored - reference
        justification_start = time.perf_counter()
        justifications: Dict[str, Counter] = defaultdict(Counter)
        justification_examples: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        for fact in sorted(missing):
            if fact[0] != "class":
                continue
            for label in class_justifications(graph, fact[1], fact[2], stored):
                justifications[fact[1]][label] += 1
                justification_examples[fact[1]].setdefault(label, [])
                if len(justification_examples[fact[1]][label]) < 3:
                    justification_examples[fact[1]][label].append(fact[2])
        justification_seconds = time.perf_counter() - justification_start
        on_demand_start = time.perf_counter()
        missing_classes = {fact[1] for fact in missing | extra if fact[0] == "class"}
        on_demand = on_demand_report(registry, missing_classes, individuals, stored, reference, missing)
        on_demand_seconds = time.perf_counter() - on_demand_start
        registry_individuals = {str(uri) for uri in registry._by_uri}
        report = {
            "steps": steps,
            "events": sum(len(p.knowledge_events) for p in perceptions),
            "event_kinds": dict(Counter(e.kind.value for p in perceptions for e in p.knowledge_events)),
            "event_statements": len(triples),
            "event_statements_distinct": len(set(triples)),
            "individuals": len(individuals),
            "new_people": len(individuals - self.vocabulary.named_individuals),
            "individuals_without_krrood_objects": sorted(individuals - registry_individuals)[:EXAMPLES],
            "registry_individuals_not_compared": len(registry_individuals - individuals),
            "reference_triples": len(graph),
            "facts": {"krrood": len(stored), "reference": len(reference), "matching": len(stored & reference),
                      "missing": len(missing), "extra": len(extra)},
            "kinds": comparison,
            "missing_class_justifications": {name: dict(counter.most_common())
                                             for name, counter in sorted(justifications.items())},
            "missing_class_justification_examples": dict(sorted(justification_examples.items())),
            "on_demand_class_answers": on_demand,
            "nemo": nemo,
            "seconds": {
                "total": time.perf_counter() - start,
                "nemo_process": nemo["nemo_process_wall_seconds"],
                "reference_parse_and_normalise": reference_seconds,
                "krrood_normalise": krrood_seconds,
                "justifications": justification_seconds,
                "on_demand_queries": on_demand_seconds,
            },
        }
        del graph
        self.results.append(report)
        print(f"[audit] after {steps} steps: krrood={len(stored)} reference={len(reference)} "
              f"missing={len(missing)} extra={len(extra)} "
              f"by kind={ {k: (v['missing'], v['extra']) for k, v in comparison.items()} } "
              f"({report['seconds']['total']:.1f} s)", file=sys.stderr, flush=True)
        return report


@dataclass
class AuditedKrroodVariant(KrroodVariant):
    """
    The KRROOD variant of the agent loop, unchanged, with an audit of the freshly loaded knowledge base at the end of
    its setup (the step-0 baseline).
    """

    auditor: Optional[CheckpointAuditor] = None
    """
    The auditor.
    """

    def setup(self) -> Dict[str, Any]:
        report = super().setup()
        if self.auditor is not None and 0 in self.auditor.checkpoints:
            self.auditor.audit(self.registry, 0)
        return report


def check_application_attributes(vocabulary_: Vocabulary) -> None:
    """
    Make sure that the application attributes cannot be mistaken for OWL2Bench properties by the normalisation.
    """
    from krrood.ontomatic.ontology_to_python.owl_instances_loader import to_snake

    names = {to_snake(local(p)) for p in vocabulary_.object_properties | vocabulary_.data_properties}
    clashes = names & set(APPLICATION_ATTRIBUTES)
    if clashes:
        raise RuntimeError(f"application attributes clash with OWL2Bench properties: {sorted(clashes)}")


def scenario_digest(scenario: Scenario) -> str:
    """
    :return: SHA-256 of the scenario's JSON (as ``run_agent_loop.py`` writes it to ``scenario.json``).
    """
    return hashlib.sha256(json.dumps(scenario.to_json()).encode()).hexdigest()


def run(seed: int, steps: int, events_per_step: int, checkpoints: Sequence[int], work_directory: Path,
        nemo_binary: str, raw_file: Path = UNREASONED_FILE, compare_rdfxml_input: bool = True) -> Dict[str, Any]:
    """
    Run the agent loop of the KRROOD variant on the scenario of a seed and audit the knowledge base at the checkpoints.

    :return: The report of the seed.
    """
    started = time.perf_counter()
    work_directory.mkdir(parents=True, exist_ok=True)
    scenario = generate_scenario(raw_file, steps, seed, events_per_step)
    raw_graph = load(raw_file)
    individuals, object_properties, data_properties = vocabulary(raw_graph)
    vocabulary_ = Vocabulary(individuals, object_properties, data_properties)
    check_application_attributes(vocabulary_)
    raw_ntriples = work_directory / "raw.nt"
    raw_graph.serialize(str(raw_ntriples), format="nt", encoding="utf-8")
    del raw_graph
    report: Dict[str, Any] = {
        "seed": seed,
        "steps": steps,
        "events_per_step": events_per_step,
        "checkpoints": sorted(checkpoints),
        "raw_file": str(raw_file),
        "scenario_sha256": scenario_digest(scenario),
        "scenario_statistics": scenario.statistics(),
        "named_individuals": len(individuals),
        "object_properties": len(object_properties),
        "data_properties": len(data_properties),
    }
    if compare_rdfxml_input:
        # The reference is computed from an N-Triples serialisation of the raw data, so that the event statements can
        # be appended; its closure must equal the closure Nemo computes from the RDF/XML file itself.
        rdfxml_closure = work_directory / "closure_rdfxml.nt"
        run_nemo_owlrl(raw_file, nemo_binary, rdfxml_closure)
        from_rdfxml = normalised_facts(load(rdfxml_closure), individuals, object_properties, data_properties)
        ntriples_closure = work_directory / "closure_raw_nt.nt"
        run_nemo_owlrl(raw_ntriples, nemo_binary, ntriples_closure)
        from_ntriples = normalised_facts(load(ntriples_closure), individuals, object_properties, data_properties)
        report["raw_input_serialisation_check"] = {
            "facts_from_rdfxml": len(from_rdfxml),
            "facts_from_ntriples": len(from_ntriples),
            "equal": from_rdfxml == from_ntriples,
        }
        rdfxml_closure.unlink()
        ntriples_closure.unlink()
    auditor = CheckpointAuditor(scenario, vocabulary_, raw_ntriples, work_directory, nemo_binary, set(checkpoints))
    variant = AuditedKrroodVariant(scenario=scenario, robot=Robot.at_start(scenario.robot, scenario.campus),
                                   auditor=auditor)

    def progress(step: int, record: Dict[str, Any]) -> None:
        if step + 1 in auditor.checkpoints:
            auditor.audit(variant.registry, step + 1)

    loop_start = time.perf_counter()
    result = run_agent_loop(variant, progress=progress)
    report["loop"] = {
        "setup": result.setup,
        "steps_run": len(result.steps),
        "step_seconds_total": sum(s["total_seconds"] for s in result.steps),
        "statements_inserted": sum(s["statements_inserted"] for s in result.steps),
        "wall_seconds_including_audits": time.perf_counter() - loop_start,
    }
    report["results"] = auditor.results
    report["wall_seconds"] = time.perf_counter() - started
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--events-per-step", type=int, default=3)
    parser.add_argument("--checkpoints", default=",".join(map(str, DEFAULT_CHECKPOINTS)),
                        help="comma-separated numbers of completed steps (0 = right after loading)")
    parser.add_argument("--raw-file", default=str(UNREASONED_FILE))
    parser.add_argument("--nemo-binary", default=os.environ.get("NEMO_BINARY", "nmo"))
    parser.add_argument("--work-dir", required=True, help="scratch directory for the Nemo input and closure")
    parser.add_argument("--no-rdfxml-check", action="store_true",
                        help="skip the check that the N-Triples serialisation of the raw data has the same closure")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    os.environ.setdefault("TQDM_DISABLE", "1")
    checkpoints = sorted({int(c) for c in arguments.checkpoints.split(",") if c != ""})
    if any(c < 0 or c > arguments.steps for c in checkpoints):
        parser.error("checkpoints must lie between 0 and --steps")
    report = run(arguments.seed, arguments.steps, arguments.events_per_step, checkpoints, Path(arguments.work_dir),
                 arguments.nemo_binary, Path(arguments.raw_file), not arguments.no_rdfxml_check)
    write_json(Path(arguments.output), report)
    sys.stdout.flush()
    sys.stderr.flush()
    # Skip interpreter tear-down of large object graphs.
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
