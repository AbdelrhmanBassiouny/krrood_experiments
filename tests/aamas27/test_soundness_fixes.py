"""
Soundness of the OWL2Bench RL classification in KRROOD (Ontomatic model + instance loader) and provenance of the
inferred facts. The tests load the raw OWL2Bench RL data once (about 15-30 s).

Run with::

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/aamas27
"""

from __future__ import annotations

import inspect
from collections import Counter

import pytest
import rdflib

from krrood.class_diagrams.utils import Role, issubclass_or_role
from krrood.entity_query_language.symbol_graph import SymbolGraph
from krrood.ontomatic.ontology_to_python.owl_instances_loader import (
    OwlLoader,
    TypeInferredThrough,
)
from krrood.ontomatic.property_descriptor.property_descriptor_relation import (
    InferredThrough,
    PropertyDescriptorRelation,
)

from krrood_experiments.aamas27.environment import UNREASONED_FILE
from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates as model
from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates_properties as properties
from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)

NAMESPACE = "http://benchmark/OWL2Bench#"
T20_CRICKET = NAMESPACE + "T20Cricket"


@pytest.fixture(scope="module")
def registry():
    registry = load_instances_for_owl2bench_with_predicates(str(UNREASONED_FILE))
    yield registry
    SymbolGraph().clear()


def objects_of_type(registry, cls):
    return [o for objects in registry._by_uri.values() for o in objects if isinstance(o, cls)]


def test_necessary_conditions_do_not_classify(registry):
    """
    LeisureStudent SubClassOf (Student and takesCourse max 1 Course) and WomanCollege SubClassOf
    (College and hasStudent only (not Man)) are necessary conditions. Before the fix, every student that takes at most
    one course was classified as LeisureStudent (53 on the RL data, Q14 returned 53); OWL 2 RL entails none.
    """
    graph = rdflib.Graph()
    graph.parse(str(UNREASONED_FILE))
    takes_course = rdflib.URIRef(NAMESPACE + "takesCourse")

    def model_types(subject):
        return [
            getattr(model, str(o)[len(NAMESPACE) :], None)
            for o in graph.objects(subject, rdflib.RDF.type)
            if str(o).startswith(NAMESPACE)
        ]

    satisfying = 0
    for student in set(graph.subjects(takes_course, None)):
        if not any(t and issubclass_or_role(t, model.Student) for t in model_types(student)):
            continue
        courses = [
            course
            for course in graph.objects(student, takes_course)
            if any(t and issubclass_or_role(t, model.Course) for t in model_types(course))
        ]
        satisfying += len(courses) <= 1
    assert satisfying == 53
    assert objects_of_type(registry, model.LeisureStudent) == []
    assert objects_of_type(registry, model.WomanCollege) == []
    assert "axiom_python" not in vars(model.LeisureStudent)
    assert "axiom_python" not in vars(model.WomanCollege)


def test_t20_cricket_fan_definition_still_classifies(registry):
    """
    T20CricketFan EquivalentTo (isCrazyAbout value T20Cricket) is a definition and must keep classifying (Q5).
    """
    fans = objects_of_type(registry, model.T20CricketFan)
    assert len(fans) == 20
    for fan in fans:
        assert T20_CRICKET in {str(v.uri) for v in fan.person.is_crazy_about} | {
            str(v.uri) for v in fan.is_crazy_about
        }
        explanation = registry.explain_type(fan.uri, model.T20CricketFan)
        assert explanation.rule == TypeInferredThrough.AXIOM
        assert explanation.premises == (model.T20CricketFan,)


def test_no_classification_axioms_from_inverse_restrictions():
    for cls in [model.Organization, model.Program, model.College, model.Course, model.Department]:
        assert "axiom_python" not in vars(cls), cls


def test_general_class_axioms_keep_their_named_conjunct():
    source = inspect.getsource(model.ScienceStudent.axiom_python)
    assert "issubclass_or_role(t, Student) for t in candidate.types" in source
    assert "issubclass_or_role(t, Science)" in source


def test_no_implicit_subsumptions():
    assert not issubclass(model.T20CricketFan, model.SportsFan)
    assert not issubclass(model.SportsFan, model.SportsLover)
    assert not issubclass(model.SportsLover, model.PeopleWithHobby)
    assert issubclass(model.SportsLover, Role) and model.SportsLover.get_role_taker_type() is model.Person
    assert not issubclass(model.EvaluationCommittee, Role)


def test_every_inferred_relation_is_explained(registry):
    rules = Counter()
    for relation in SymbolGraph().relations():
        if not relation.inferred:
            continue
        assert relation.inference_explanation, relation
        rules[relation.rule] += 1
        if relation.rule == InferredThrough.TRANSITIVE:
            first, second = relation.premises
            assert first.target.instance is second.source.instance
            assert first.source.instance is relation.source.instance
            assert second.target.instance is relation.target.instance
        elif relation.rule == InferredThrough.CHAIN:
            chain = relation.premises
            assert len(chain) >= 2
            for left, right in zip(chain, chain[1:]):
                assert left.target.instance is right.source.instance
    for rule in [
        InferredThrough.INVERSE,
        InferredThrough.SUPER,
        InferredThrough.EQUIVALENT,
        InferredThrough.SYMMETRY,
        InferredThrough.TRANSITIVE,
        InferredThrough.CHAIN,
    ]:
        assert rules[rule] > 0, rule


def test_symmetric_transitive_component_facts_are_explained_by_their_component(registry):
    """
    hasSameHomeTownWith implies no other property, so its component facts are stored only in the attributes and
    explained by their weakly connected component (one record per member instead of one relation per fact).
    """
    assert not OwlLoader.implies_other_properties(properties.HasSameHomeTownWith)
    persons = [o for o in objects_of_type(registry, model.Person) if o.has_same_home_town_with]
    assert persons
    rules = Counter()
    for person in persons[:50]:
        for other in person.has_same_home_town_with:
            relation = PropertyDescriptorRelation.find(person, "has_same_home_town_with", other)
            assert relation is not None, (person.uri, other.uri)
            rules[relation.rule] += 1
            if relation.rule == InferredThrough.SYMMETRIC_TRANSITIVE_COMPONENT:
                name, component_id, size = relation.premises
                assert name == "HasSameHomeTownWith"
                assert size >= 2
    assert rules[InferredThrough.SYMMETRIC_TRANSITIVE_COMPONENT] > 0
    assert not any(
        relation.rule == InferredThrough.SYMMETRIC_TRANSITIVE_COMPONENT for relation in SymbolGraph().relations()
    )


def test_properties_that_imply_other_properties():
    assert OwlLoader.implies_other_properties(properties.IsStudentOf)  # sub-property of isMemberOf
    assert OwlLoader.implies_other_properties(properties.HasSubOrganization)  # inverse of isSubOrganizationOf
    assert OwlLoader.implies_other_properties(properties.EnrollIn)  # occurs in property chains


def test_relation_explanation_api(registry):
    relation = next(r for r in SymbolGraph().relations() if r.rule == InferredThrough.TRANSITIVE)
    found = PropertyDescriptorRelation.find(
        relation.source.instance, relation.wrapped_field.name, relation.target.instance
    )
    assert found is relation
    explanation = relation.explain()
    assert explanation["rule"] == "transitive"
    assert len(explanation["premises"]) == 2


def test_every_type_rule_is_recorded(registry):
    rules = Counter(
        explanation.rule
        for explanations in registry.type_explanations.values()
        for explanation in explanations.values()
    )
    for rule in [
        TypeInferredThrough.ASSERTED,
        TypeInferredThrough.DOMAIN,
        TypeInferredThrough.RANGE,
        TypeInferredThrough.AXIOM,
    ]:
        assert rules[rule] > 0, rule
    for uri, explanations in registry.type_explanations.items():
        for cls, explanation in explanations.items():
            if explanation.rule in (TypeInferredThrough.DOMAIN, TypeInferredThrough.RANGE):
                subject, property_name, value = explanation.premises[0]
                assert property_name and subject is not None
            if explanation.rule == TypeInferredThrough.AXIOM:
                assert issubclass_or_role(cls, explanation.premises[0])


def test_types_entailed_through_inferred_types_and_super_properties(registry):
    """
    Completeness checks against the OWL 2 RL closure (GraphDB, owl2-rl-optimized):

    * UGStudent <- Student and (enrollFor some UGProgram): the Student type is itself inferred (enrollIn domain), so
      the axiom must see inferred types (765 UGStudents in the closure).
    * ResearchGroup individuals are Employees: hasResearchProject SubPropertyOf hasWork, hasWork rdfs:domain Employee
      (prp-spo1 + prp-dom), hence also Persons (Q12 returns 2494 in GraphDB).
    """
    assert len({o.uri for o in objects_of_type(registry, model.UGStudent)}) == 765
    research_groups = {o.uri for o in objects_of_type(registry, model.ResearchGroup)}
    assert len(research_groups) == 7
    employees = {o.uri for o in objects_of_type(registry, model.Employee)}
    assert research_groups <= employees
    for uri in research_groups:
        explanation = registry.explain_type(uri, model.Employee)
        assert explanation.rule == TypeInferredThrough.DOMAIN
        assert explanation.premises[0][1] == "HasWork"
    persons = {
        uri
        for uri, objects in registry._by_uri.items()
        if any(issubclass_or_role(type(o), model.Person) for o in objects)
    }
    assert len(persons) == 2494


def test_individuals_are_not_typed_with_the_class_they_are_named_after(registry):
    """
    owl2bench:Engineering (and Science, Management, ...) are individuals used as values of hasCollegeDiscipline. OWL 2
    RL types them CollegeDiscipline (rdfs:range of hasCollegeDiscipline) but not with the class of the same name. The
    loader used to type every property-less individual with its namesake class (14 non-entailed memberships).
    """
    for name in ["Engineering", "Science", "Management", "FineArts", "HumanitiesAndSocial", "HumanResourceManagement"]:
        objects = registry._by_uri[rdflib.URIRef(NAMESPACE + name)]
        assert objects, name
        assert not any(isinstance(o, getattr(model, name)) for o in objects), name
    engineering = registry._by_uri[rdflib.URIRef(NAMESPACE + "Engineering")]
    assert any(isinstance(o, model.CollegeDiscipline) for o in engineering)
    for uri, explanations in registry.type_explanations.items():
        for explanation in explanations.values():
            assert explanation.rule.value != "name"


def objects_of(registry, local_name):
    return registry._by_uri[rdflib.URIRef(NAMESPACE + local_name)]


def uris(objects):
    return {str(o.uri).removeprefix(NAMESPACE) for o in objects}


def test_chain_facts_are_stored_on_the_role_that_declares_the_property(registry):
    """
    isStudentOf <- enrollIn o isSubOrganizationOf: U0C0D0UGS0 is enrolled in department U0C0D0, which is a
    sub-organization of college U0C0 and university U0. The enrollIn fact is a node of the student's root object (a
    Woman), while isStudentOf is declared by the student's UGStudent role, where the chain facts must be stored.
    """
    student = next(o for o in objects_of(registry, "U0C0D0UGS0") if isinstance(o, model.UGStudent))
    assert {"U0C0D0", "U0C0", "U0"} <= uris(student.is_student_of)
    woman = PropertyDescriptorRelation.root_role_taker(student)
    college = objects_of(registry, "U0C0")[0]
    relation = PropertyDescriptorRelation.find(woman, "is_student_of", college)
    assert relation is not None and relation.rule == InferredThrough.CHAIN
    university = objects_of(registry, "U0")[0]
    assert any(o.uri == student.uri for o in university.has_student)


def test_research_assistants_work_for_the_university_of_their_research_group(registry):
    """worksFor <- worksFor o isSubOrganizationOf through a research group (37 facts were missing)."""
    assistant = next(o for o in objects_of(registry, "U0RG0RA0") if isinstance(o, model.ResearchAssistant))
    assert {"U0RG0", "U0"} <= uris(assistant.works_for)


def test_research_groups_have_their_projects_as_work(registry):
    """
    hasResearchProject is a sub-property of hasWork, which only the Employee role declares. A research group's
    Employee role has its own root (a Person), linked to the ResearchGroup object as the same individual.
    """
    for local_name in [f"U0RG{index}" for index in range(7)]:
        objects = objects_of(registry, local_name)
        group = next(o for o in objects if isinstance(o, model.ResearchGroup))
        employee = next(o for o in objects if isinstance(o, model.Employee))
        assert uris(group.has_research_project) <= uris(employee.has_work)
        assert any(o is employee for o in PropertyDescriptorRelation.objects_of_individual(group))


def test_relations_by_descriptor_class_are_yielded_once(registry):
    """Fields of the same name declared by several classes share their relations and must not repeat them."""
    graph = SymbolGraph()
    assistant = PropertyDescriptorRelation.root_role_taker(objects_of(registry, "U0RG0RA0")[0])
    node = graph.get_wrapped_instance(assistant)
    relations = list(graph.get_outgoing_relations_by_descriptor_class(node, properties.WorksFor))
    assert relations
    assert len(relations) == len({id(relation) for relation in relations})
