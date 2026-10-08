"""
Scaling audit: is the knowledge base that Ontomatic loads from the raw data of N universities equal to the OWL 2 RL
closure of that data?

The soundness audit (:mod:`krrood_experiments.aamas27.soundness_audit`) compares KRROOD's knowledge base with
GraphDB's closure of one university. For the larger inputs of the scaling experiment, the reference is Nemo with
``owl2rl.rls`` (:func:`~krrood_experiments.aamas27.loading_worker.run_nemo_owlrl`), whose closure of one university
equals GraphDB's (the baseline closures of the main run, ``baselines/closure_comparison.json``). Both sides are
normalised as :mod:`~krrood_experiments.aamas27.closure_comparison` and
:func:`~krrood_experiments.aamas27.runtime_audit.krrood_facts` do it.

The closures have tens of millions of facts (32 million triples for four universities), more than sets of tuples or
an RDFLib graph hold in the memory of the audit. Both sides are therefore streamed: Nemo's closure line by line with
RDFLib's N-Triples parser, KRROOD's facts object by object. Every fact is stored as a 64-bit hash (BLAKE2b) in a
sorted array per kind; the arrays are compared, and the facts whose hashes differ are recovered by a second pass for
the examples. Two different facts with the same hash would hide a difference; for 10^8 facts the probability is
below 10^-3.

* ``missing``: in the reference closure, not stored by KRROOD.
* ``extra``: stored by KRROOD, not in the reference closure.

Run each input in a fresh process (the loader's global state is not reset between runs)::

    python -m krrood_experiments.aamas27.scaling_audit --raw-file raw_u2.rdf --work-dir /tmp/scaling --output u2.json
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from array import array
from pathlib import Path
from typing import Any, Dict, Iterator, Set

import numpy

from .closure_comparison import Fact, load, vocabulary
from .environment import write_json
from .loading_worker import run_nemo_owlrl
from .soundness_audit import EXAMPLES, IGNORED_CLASSES, NAMESPACE, class_uris_of_type, normalized_value

KINDS = ("class", "object", "data")


def fact_hash(fact: Fact) -> int:
    """
    :param fact: A normalised fact.
    :return: Its 64-bit hash.
    """
    return int.from_bytes(hashlib.blake2b("\x1f".join(fact).encode(), digest_size=8).digest(), "little")


def reference_facts(closure_file: Path, individuals: Set[str], object_properties: Set[str],
                    data_properties: Set[str]) -> Iterator[Fact]:
    """
    :param closure_file: Nemo's closure as N-Triples.
    :return: The facts of the closure, normalised as
        :func:`~krrood_experiments.aamas27.closure_comparison.normalised_facts` does it, one triple at a time.
    """
    from rdflib import RDF, Literal, URIRef
    from rdflib.plugins.parsers.ntriples import W3CNTriplesParser

    class Sink:
        triple_value = None

        def triple(self, subject, predicate, value) -> None:
            self.triple_value = (subject, predicate, value)

    sink = Sink()
    parser = W3CNTriplesParser(sink)
    with open(closure_file, encoding="utf-8") as stream:
        for line in stream:
            sink.triple_value = None
            parser.parsestring(line)
            if sink.triple_value is None:
                continue
            subject, predicate, value = sink.triple_value
            subject_text = str(subject)
            if subject_text not in individuals:
                continue
            predicate_text = str(predicate)
            if predicate == RDF.type:
                class_uri = str(value)
                if isinstance(value, URIRef) and class_uri.startswith(NAMESPACE):
                    if class_uri[len(NAMESPACE):] not in IGNORED_CLASSES:
                        yield "class", class_uri[len(NAMESPACE):], subject_text, ""
            elif predicate_text in object_properties:
                if not isinstance(value, Literal) and str(value) in individuals:
                    yield "object", predicate_text[len(NAMESPACE):], subject_text, str(value)
            elif predicate_text in data_properties and isinstance(value, Literal):
                yield "data", predicate_text[len(NAMESPACE):], subject_text, str(value.toPython())


def stored_facts(registry, individuals: Set[str], object_properties: Set[str],
                 data_properties: Set[str]) -> Iterator[Fact]:
    """
    :param registry: The KRROOD instance registry.
    :return: KRROOD's stored facts, as :func:`~krrood_experiments.aamas27.runtime_audit.krrood_facts` collects
        them, one object at a time (a fact can be produced more than once).
    """
    from krrood.ontomatic.ontology_to_python.owl_instances_loader import to_snake

    object_fields = {p[len(NAMESPACE):]: to_snake(p[len(NAMESPACE):]) for p in object_properties}
    data_fields = {p[len(NAMESPACE):]: to_snake(p[len(NAMESPACE):]) for p in data_properties}
    for uri, objects in registry._by_uri.items():
        individual = str(uri)
        if individual not in individuals:
            continue
        for instance in objects:
            for class_uri in class_uris_of_type(type(instance)):
                name = class_uri[len(NAMESPACE):]
                if class_uri.startswith(NAMESPACE) and name not in IGNORED_CLASSES:
                    yield "class", name, individual, ""
            for name, field_name in object_fields.items():
                values = getattr(instance, field_name, None)
                if values is None:
                    continue
                if not isinstance(values, (set, list, tuple, frozenset)) and not hasattr(values, "__iter__"):
                    values = [values]
                for value in values:
                    value_uri = getattr(value, "uri", None)
                    if value_uri is not None and str(value_uri) in individuals:
                        yield "object", name, individual, str(value_uri)
            for name, field_name in data_fields.items():
                value = getattr(instance, field_name, None)
                if value is None:
                    continue
                for member in value if isinstance(value, (set, list, tuple)) else (value,):
                    yield "data", name, individual, normalized_value(member)


def hashed(facts: Iterator[Fact]) -> Dict[str, numpy.ndarray]:
    """
    :return: Per kind, the sorted distinct hashes of the facts.
    """
    hashes = {kind: array("Q") for kind in KINDS}
    for fact in facts:
        hashes[fact[0]].append(fact_hash(fact))
    return {kind: numpy.unique(numpy.frombuffer(values, dtype=numpy.uint64)) for kind, values in hashes.items()}


def examples(facts: Iterator[Fact], wanted: numpy.ndarray) -> list:
    """
    :return: Up to ``EXAMPLES`` facts whose hashes are among ``wanted``.
    """
    if len(wanted) == 0:
        return []
    wanted_set = {int(h) for h in wanted[:10 * EXAMPLES]}
    found = []
    for fact in facts:
        if fact_hash(fact) in wanted_set:
            found.append(fact)
            if len(found) >= EXAMPLES:
                break
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw-file", required=True)
    parser.add_argument("--nemo-binary", default=os.environ.get("NEMO_BINARY", "nmo"))
    parser.add_argument("--work-dir", required=True, help="scratch directory for Nemo's closure")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    os.environ.setdefault("TQDM_DISABLE", "1")
    raw_file = Path(arguments.raw_file)
    work_directory = Path(arguments.work_dir)
    work_directory.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    raw_graph = load(raw_file)
    individuals, object_properties, data_properties = vocabulary(raw_graph)
    raw_statements = len(raw_graph)
    del raw_graph
    closure_file = work_directory / f"{raw_file.stem}_closure.nt"
    nemo = run_nemo_owlrl(raw_file, arguments.nemo_binary, closure_file)
    reference_start = time.perf_counter()
    reference = hashed(reference_facts(closure_file, individuals, object_properties, data_properties))
    reference_seconds = time.perf_counter() - reference_start
    from krrood_experiments.owl2bench.ontomatic.helpers import load_instances_for_owl2bench_with_predicates

    load_start = time.perf_counter()
    registry = load_instances_for_owl2bench_with_predicates(str(raw_file))
    load_seconds = time.perf_counter() - load_start
    stored = hashed(stored_facts(registry, individuals, object_properties, data_properties))
    kinds: Dict[str, Any] = {}
    for kind in KINDS:
        missing = numpy.setdiff1d(reference[kind], stored[kind], assume_unique=True)
        extra = numpy.setdiff1d(stored[kind], reference[kind], assume_unique=True)
        kinds[kind] = {
            "reference": len(reference[kind]), "candidate": len(stored[kind]),
            "matching": len(numpy.intersect1d(reference[kind], stored[kind], assume_unique=True)),
            "missing": len(missing), "extra": len(extra),
            "missing_examples": examples(reference_facts(closure_file, individuals, object_properties,
                                                         data_properties), missing),
            "extra_examples": examples(stored_facts(registry, individuals, object_properties, data_properties),
                                       extra),
        }
    closure_file.unlink()
    totals = {name: sum(kinds[kind][field] for kind in KINDS) for name, field in (
        ("krrood", "candidate"), ("reference", "reference"), ("matching", "matching"), ("missing", "missing"),
        ("extra", "extra"))}
    report = {
        "raw_file": raw_file.name,
        "raw_statements": raw_statements,
        "named_individuals": len(individuals),
        "reference_statements": nemo.get("triples_after_reasoning"),
        "krrood_load_and_reasoning_seconds": load_seconds,
        "reference_normalise_seconds": reference_seconds,
        "facts": totals,
        "kinds": kinds,
        "comparison": "64-bit BLAKE2b hashes of the normalised facts",
        "nemo": nemo,
        "wall_seconds": time.perf_counter() - started,
    }
    write_json(Path(arguments.output), report)
    print(f"{raw_file.name}: krrood={totals['krrood']} reference={totals['reference']} "
          f"missing={totals['missing']} extra={totals['extra']}", flush=True)
    sys.stdout.flush()
    # Skip interpreter tear-down of large object graphs.
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
