"""
Compare the closure materialised by an OWL 2 RL engine (an N-Triples or Turtle file, for example the output of
``loading_worker --system nemo_owlrl --closure-output ...``) with a reference closure, with the normalisation of
:mod:`krrood_experiments.aamas27.soundness_audit`:

* individuals: the explicitly declared ``owl:NamedIndividual`` subjects of the raw input;
* class memberships: ``rdf:type`` triples of individuals whose class is a named OWL2Bench class (``Role`` excluded);
* object-property assertions: pairs of individuals for the OWL2Bench object properties declared in the raw input;
* data-property assertions: (individual, value) pairs for the declared OWL2Bench data properties, the value
  normalised with ``Literal.toPython()``.

* ``missing``: in the reference but not derived by the engine.
* ``extra``: derived by the engine but not in the reference.

Example::

    python -m krrood_experiments.aamas27.closure_comparison --raw resources/owl2bench_statements_unreasoned.rdf \\
        --reference resources/owl2bench_statements_reasoned.rdf --candidate nemo=closure.nt --output comparison.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from .environment import UNREASONED_FILE, REASONED_FILE, write_json
from .soundness_audit import EXAMPLES, IGNORED_CLASSES, NAMESPACE

Fact = Tuple[str, str, str, str]
"""
A normalised fact: kind (``class``, ``object`` or ``data``), local name of the class or property, individual, and the
object individual or the normalised value (empty for class memberships).
"""

FORMATS = {".nt": "nt", ".ttl": "turtle", ".rdf": "xml", ".owl": "xml"}
"""
RDFLib parser per file extension.
"""


def load(path: Path):
    """
    :param path: An RDF file.
    :return: The parsed RDFLib graph.
    """
    import rdflib

    graph = rdflib.Graph()
    graph.parse(str(path), format=FORMATS.get(path.suffix, "turtle"))
    return graph


def vocabulary(raw) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    :param raw: The graph of the raw input.
    :return: The declared named individuals, OWL2Bench object properties and OWL2Bench data properties.
    """
    from rdflib import OWL, RDF

    individuals = {str(s) for s in raw.subjects(RDF.type, OWL.NamedIndividual)}
    object_properties = {str(s) for s in raw.subjects(RDF.type, OWL.ObjectProperty) if str(s).startswith(NAMESPACE)}
    data_properties = {str(s) for s in raw.subjects(RDF.type, OWL.DatatypeProperty) if str(s).startswith(NAMESPACE)}
    return individuals, object_properties, data_properties


def normalised_facts(graph, individuals: Set[str], object_properties: Set[str], data_properties: Set[str]) -> Set[Fact]:
    """
    :return: The facts about individuals in a closure, normalised as described in the module documentation.
    """
    from rdflib import RDF, Literal, URIRef

    facts: Set[Fact] = set()
    for subject, predicate, value in graph:
        subject_text = str(subject)
        if subject_text not in individuals:
            continue
        predicate_text = str(predicate)
        if predicate == RDF.type:
            class_uri = str(value)
            if isinstance(value, URIRef) and class_uri.startswith(NAMESPACE):
                if class_uri[len(NAMESPACE):] not in IGNORED_CLASSES:
                    facts.add(("class", class_uri[len(NAMESPACE):], subject_text, ""))
        elif predicate_text in object_properties:
            if not isinstance(value, Literal) and str(value) in individuals:
                facts.add(("object", predicate_text[len(NAMESPACE):], subject_text, str(value)))
        elif predicate_text in data_properties and isinstance(value, Literal):
            facts.add(("data", predicate_text[len(NAMESPACE):], subject_text, str(value.toPython())))
    return facts


def compare(candidate: Set[Fact], reference: Set[Fact]) -> Dict[str, Any]:
    """
    :return: Per kind of fact: sizes of both sets, of their intersection and of both differences, the differences
        counted per class or property, and examples.
    """
    report = {}
    for kind in ("class", "object", "data"):
        reference_facts = {fact for fact in reference if fact[0] == kind}
        candidate_facts = {fact for fact in candidate if fact[0] == kind}
        missing = reference_facts - candidate_facts
        extra = candidate_facts - reference_facts
        report[kind] = {
            "reference": len(reference_facts),
            "candidate": len(candidate_facts),
            "matching": len(reference_facts & candidate_facts),
            "missing": len(missing),
            "extra": len(extra),
            "missing_by_name": dict(Counter(fact[1] for fact in missing).most_common()),
            "extra_by_name": dict(Counter(fact[1] for fact in extra).most_common()),
            "missing_examples": sorted(missing)[:EXAMPLES],
            "extra_examples": sorted(extra)[:EXAMPLES],
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw", default=str(UNREASONED_FILE), help="the raw input (defines the vocabulary)")
    parser.add_argument("--reference", default=str(REASONED_FILE), help="the reference closure")
    parser.add_argument("--candidate", action="append", required=True,
                        help="NAME=PATH of an engine's closure (N-Triples or Turtle); repeatable")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    individuals, object_properties, data_properties = vocabulary(load(Path(arguments.raw)))
    reference = normalised_facts(load(Path(arguments.reference)), individuals, object_properties, data_properties)
    report: Dict[str, Any] = {
        "raw": arguments.raw,
        "reference": arguments.reference,
        "individuals": len(individuals),
        "object_properties": len(object_properties),
        "data_properties": len(data_properties),
        "candidates": {},
    }
    for entry in arguments.candidate:
        name, path = entry.split("=", 1)
        graph = load(Path(path))
        candidate = normalised_facts(graph, individuals, object_properties, data_properties)
        report["candidates"][name] = {"path": path, "triples": len(graph), **compare(candidate, reference)}
    write_json(Path(arguments.output), report)
    for name, entry in report["candidates"].items():
        for kind in ("class", "object", "data"):
            counts = entry[kind]
            print(f"{name} {kind}: reference={counts['reference']} candidate={counts['candidate']} "
                  f"matching={counts['matching']} missing={counts['missing']} extra={counts['extra']}")
            for label in ("missing_by_name", "extra_by_name"):
                if counts[label]:
                    print(f"    {label}: {json.dumps(dict(list(counts[label].items())[:10]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
