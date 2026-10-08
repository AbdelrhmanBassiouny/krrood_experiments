"""
Tests of the hashed comparison of the scaling audit (:mod:`krrood_experiments.aamas27.scaling_audit`): the
reference side is read from N-Triples as :func:`~krrood_experiments.aamas27.closure_comparison.normalised_facts`
reads a graph, and a fact on one side only is found as missing or extra, with the fact itself as an example.
"""

from __future__ import annotations

import numpy
import rdflib

from krrood_experiments.aamas27.closure_comparison import normalised_facts
from krrood_experiments.aamas27.scaling_audit import examples, hashed, reference_facts

B = "http://benchmark/OWL2Bench#"
CLOSURE = f"""<{B}ann> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{B}Student> .
<{B}ann> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{B}Role> .
<{B}ann> <{B}isMemberOf> <{B}cs> .
<{B}ann> <{B}isMemberOf> <http://example.org/outside> .
<{B}ann> <{B}hasAge> "30"^^<http://www.w3.org/2001/XMLSchema#integer> .
<{B}ann> <{B}hasName> "Ann" .
<{B}cs> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{B}Department> .
"""
INDIVIDUALS = {f"{B}ann", f"{B}cs"}
OBJECT_PROPERTIES = {f"{B}isMemberOf"}
DATA_PROPERTIES = {f"{B}hasAge", f"{B}hasName"}


def test_streamed_reference_equals_the_graph_normalisation(tmp_path):
    closure = tmp_path / "closure.nt"
    closure.write_text(CLOSURE)
    graph = rdflib.Graph()
    graph.parse(str(closure), format="nt")
    streamed = set(reference_facts(closure, INDIVIDUALS, OBJECT_PROPERTIES, DATA_PROPERTIES))
    assert streamed == normalised_facts(graph, INDIVIDUALS, OBJECT_PROPERTIES, DATA_PROPERTIES)
    assert ("data", "hasAge", f"{B}ann", "30") in streamed
    assert len(streamed) == 5


def test_a_fact_on_one_side_only_is_found_with_its_example():
    reference = [("class", "Student", "a", ""), ("object", "isMemberOf", "a", "b"), ("data", "hasName", "a", "A")]
    stored = reference[:2] + [reference[0], ("object", "isMemberOf", "b", "a")]
    reference_hashes, stored_hashes = hashed(iter(reference)), hashed(iter(stored))
    assert len(stored_hashes["class"]) == 1
    missing = numpy.setdiff1d(reference_hashes["data"], stored_hashes["data"], assume_unique=True)
    extra = numpy.setdiff1d(stored_hashes["object"], reference_hashes["object"], assume_unique=True)
    assert examples(iter(reference), missing) == [("data", "hasName", "a", "A")]
    assert examples(iter(stored), extra) == [("object", "isMemberOf", "b", "a")]
