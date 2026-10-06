"""
The OWL 2 RL/RDF rules that Ontomatic applies to superclass expressions (cls-hv1, cls-avf), the closure used for typing
(prp-trp, prp-spo2 on the anonymous instances), and the check of the equality and inconsistency rules, on the
OWL2Bench model with a few added triples. Each load with added triples runs in its own process (about 20 s), so that
it does not share the global symbol graph with other tests.

Run with::

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/aamas27/test_owl2rl_rules.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap

import pytest
import rdflib

from krrood.ontomatic.ontology_to_python.owl_instances_loader import OwlLoader, OwlInstancesRegistry
from krrood.ontomatic.utils import AnonymousClass
from krrood.entity_query_language.symbol_graph import SymbolGraph

from krrood_experiments.aamas27.environment import UNREASONED_FILE
from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates as model
from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates_base as base
from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates_properties as properties

NAMESPACE = "http://benchmark/OWL2Bench#"

ADDED_TRIPLES = """
@prefix : <http://benchmark/OWL2Bench#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:NewFan a owl:NamedIndividual, :Person, :T20CricketFan .
:Department rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :hasHead ; owl:allValuesFrom :VisitingProfessor ] .
:NewDepartment a owl:NamedIndividual, :Department ; :hasHead :NewHead .
:NewHead a owl:NamedIndividual, :Woman, :FullProfessor .
:U0C0D0UGS0 :enrollIn :U0C0D1 .
:U0C0D0UGS1 :likes :U0C0D0UGS1 .
"""

LOAD_AND_REPORT = textwrap.dedent(
    """
    import json, os, sys
    from krrood.ontomatic.property_descriptor.property_descriptor_relation import PropertyDescriptorRelation
    from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates as model
    from krrood_experiments.owl2bench.ontomatic.helpers import load_instances_for_owl2bench_with_predicates

    NAMESPACE = "http://benchmark/OWL2Bench#"
    registry = load_instances_for_owl2bench_with_predicates(sys.argv[1])
    fan = registry.resolve(NAMESPACE + "NewFan")
    fan_values = sorted({str(v.uri) for o in fan for v in getattr(o, "is_crazy_about", None) or ()})
    t20 = registry.resolve(NAMESPACE + "T20Cricket")[0]
    relation = PropertyDescriptorRelation.find(
        PropertyDescriptorRelation.root_role_taker(fan[0]), "is_crazy_about", t20
    )
    head = registry.resolve(NAMESPACE + "NewHead")
    head_explanation = registry.explain_type(NAMESPACE + "NewHead", model.VisitingProfessor)
    report = registry.check_owl2_rl()
    print(json.dumps({
        "fan_values": fan_values,
        "fan_rule": relation.rule.value if relation and relation.rule else None,
        "head_classes": sorted(type(o).__name__ for o in head),
        "head_rule": head_explanation.rule.value if head_explanation else None,
        "equalities": [[f.rule.value, list(f.individuals)] for f in report.equalities],
        "inconsistencies": [[f.rule.value, list(f.individuals)] for f in report.inconsistencies],
    }))
    sys.stdout.flush()
    os._exit(0)
    """
)


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    graph = rdflib.Graph()
    graph.parse(str(UNREASONED_FILE))
    graph.parse(data=ADDED_TRIPLES, format="turtle")
    path = tmp_path_factory.mktemp("owl2rl") / "owl2bench_with_added_triples.rdf"
    graph.serialize(str(path), format="xml")
    completed = subprocess.run(
        [sys.executable, "-c", LOAD_AND_REPORT, str(path)],
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    return json.loads(completed.stdout.strip().splitlines()[-1])


def test_has_value_restriction_adds_the_value(result):
    """cls-hv1: NewFan is a T20CricketFan (equivalent to isCrazyAbout value T20Cricket) without the property."""
    assert result["fan_values"] == [NAMESPACE + "T20Cricket"]
    assert result["fan_rule"] == "has_value"


def test_all_values_from_restriction_types_the_values(result):
    """
    cls-avf: the head of a department is a VisitingProfessor by the added axiom Department SubClassOf (hasHead only
    VisitingProfessor); no sufficient condition makes anyone a VisitingProfessor.
    """
    assert "VisitingProfessor" in result["head_classes"]
    assert result["head_rule"] == "all_values_from"


def test_equality_and_inconsistency_rules_fire(result):
    """
    enrollIn is functional (prp-fp: U0C0D0 = U0C0D1); likes is irreflexive (prp-irp) and has the range Interest, which
    is disjoint with Person (prp-rng, then cax-adc).
    """
    assert result["equalities"] == [["prp-fp", [NAMESPACE + "U0C0D0", NAMESPACE + "U0C0D1"]]]
    assert sorted(result["inconsistencies"]) == [
        ["cax-dw, cax-adc", [NAMESPACE + "U0C0D0UGS1"]],
        ["prp-irp", [NAMESPACE + "U0C0D0UGS1"]],
    ]


def test_chain_and_transitive_values_are_added_to_the_anonymous_instances():
    """
    prp-spo2 with prp-trp on the anonymous instances: isStudentOf <- enrollIn o isSubOrganizationOf, with
    isSubOrganizationOf transitive, so the types implied by these values are inferred before the objects exist.
    """
    loader = OwlLoader(
        str(UNREASONED_FILE), [base, model, properties], SymbolGraph(), OwlInstancesRegistry()
    )
    loader.graph.parse(str(UNREASONED_FILE))
    student, department, college, university = (
        AnonymousClass(rdflib.URIRef(NAMESPACE + name)) for name in ("S", "D", "C", "U")
    )
    for instance in (student, department, college, university):
        loader.anonymous_instances[instance.uri] = instance
    loader.add_anonymous_fact(student, properties.EnrollIn, department)
    loader.add_anonymous_fact(department, properties.IsSubOrganizationOf, college)
    loader.add_anonymous_fact(college, properties.IsSubOrganizationOf, university)
    loader.close_type_relevant_properties_of_anonymous_instances()
    assert university in department.is_sub_organization_of
    assert {college, university} <= set(student.is_student_of)
    assert student in university.has_student
