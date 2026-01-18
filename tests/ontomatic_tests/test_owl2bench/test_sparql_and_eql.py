import os
import time

import pytest
from krrood.entity_query_language.entity import (
    variable,
    to_str,
    exists,
    entity,
    variable_from,
    and_,
    has_solution_for,
)
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.enums import PredicateType
from krrood.entity_query_language.predicate import HasAttribute, IsSubClassOrRole
from krrood.entity_query_language.symbolic import Variable
from krrood.ontomatic.property_descriptor.property_descriptor import HasProperty

from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_eql_queries import (
    evaluate_eql_and_sparql_queries,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates import *
from krrood_experiments.owl2bench.ontomatic.utils import (
    AnonymousClass,
)
from krrood.ontomatic.property_descriptor.property_descriptor import (
    is_class_axiomatized_on_property,
)


@pytest.fixture
def resources_dir():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "resources"
    )


@pytest.fixture
def unreasoned_owl2bench_file_path(resources_dir):
    return os.path.join(resources_dir, "owl2bench_statements_unreasoned.rdf")


@pytest.fixture
def reasoned_owl2bench_file_path(resources_dir):
    return os.path.join(resources_dir, "owl2bench_statements_reasoned.rdf")


def test_owl2bench_statements_reasoned(reasoned_owl2bench_file_path):
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates(
        reasoned_owl2bench_file_path
    )
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    evaluate_eql_and_sparql_queries()


def test_owl2bench_statements_unreasoned(unreasoned_owl2bench_file_path):
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates(
        unreasoned_owl2bench_file_path
    )
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    evaluate_eql_and_sparql_queries()


def test_eql_value_axiom():
    t20_fan = AnonymousClass(uri="T20Fan")
    t20_fan.is_crazy_about = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#T20Cricket")
    }
    candidate_var = variable(AnonymousClass, [t20_fan])
    query = an(
        entity(candidate_var).where(
            HasAttribute(candidate_var, "is_crazy_about"),
            exists(
                candidate_var,
                to_str(candidate_var.is_crazy_about.uri)
                == "http://benchmark/OWL2Bench#T20Cricket",
            ),
        )
    )
    assert len(list(query.evaluate())) == 1
    assert has_solution_for(t20_fan, T20CricketFan.axiom)
    assert T20CricketFan.axiom_python(t20_fan)
    not_t20_fan = AnonymousClass(uri="NotT20Fan")
    not_t20_fan.is_crazy_about = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#NotT20Cricket")
    }
    assert not has_solution_for(not_t20_fan, T20CricketFan.axiom)
    assert not T20CricketFan.axiom_python(not_t20_fan)

    loves_cricket = AnonymousClass(uri="LovesT20Cricket")
    loves_cricket.loves = {AnonymousClass(uri="http://benchmark/OWL2Bench#T20Cricket")}
    assert not has_solution_for(loves_cricket, T20CricketFan.axiom)
    assert not T20CricketFan.axiom_python(loves_cricket)


def test_quantified_axiom():
    takes_1_course = AnonymousClass(uri="takes_1_course")
    takes_1_course.types = {Student}
    takes_1_course.takes_course = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#Course1", types={Course})
    }
    assert has_solution_for(takes_1_course, LeisureStudent.axiom)
    assert LeisureStudent.axiom_python(takes_1_course)
    takes_2_courses = AnonymousClass(uri="takes_2_courses")
    takes_2_courses.types = {Student}
    takes_2_courses.takes_course = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#Course1", types={Course}),
        AnonymousClass(uri="http://benchmark/OWL2Bench#Course2", types={Course}),
    }
    assert not has_solution_for(takes_2_courses, LeisureStudent.axiom)
    assert not LeisureStudent.axiom_python(takes_2_courses)
    not_a_student = AnonymousClass(uri="not_a_student")
    not_a_student.types = {Person}
    not_a_student.takes_course = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#Course1", types={Course})
    }
    candidate_var = variable(AnonymousClass, [not_a_student])
    candidate_types = variable_from(candidate_var.types)
    existential = exists(
        candidate_var,
        IsSubClassOrRole(candidate_types, Student),
    )
    assert not list(existential._evaluate__())
    assert not has_solution_for(not_a_student, LeisureStudent.axiom)
    assert not LeisureStudent.axiom_python(not_a_student)
    not_a_course = AnonymousClass(uri="not_a_course")
    not_a_course.types = {Person}
    takes_1_course_not_course = AnonymousClass(uri="takes_1_course_not_course")
    takes_1_course_not_course.types = {Student}
    takes_1_course_not_course.takes_course = {not_a_course}
    candidate_var = variable(AnonymousClass, [takes_1_course_not_course])
    existential = exists(
        candidate_var,
        IsSubClassOrRole(variable_from(candidate_var.takes_course.types), Course),
    )
    assert not list(existential._evaluate__())
    assert LeisureStudent.axiom_python(takes_1_course_not_course)
    assert has_solution_for(takes_1_course_not_course, LeisureStudent.axiom)
    takes_1_course_and_1_not_course = AnonymousClass(
        uri="takes_1_course_and_1_not_course"
    )
    takes_1_course_and_1_not_course.types = {Student}
    takes_1_course_and_1_not_course.takes_course = {
        AnonymousClass(uri="http://benchmark/OWL2Bench#Course1", types={Course}),
        not_a_course,
    }
    candidate_var = variable(AnonymousClass, [takes_1_course_and_1_not_course])
    existential = exists(
        candidate_var,
        IsSubClassOrRole(variable_from(candidate_var.takes_course.types), Course),
    )
    assert list(existential._evaluate__())
    assert LeisureStudent.axiom_python(takes_1_course_and_1_not_course)
    assert has_solution_for(takes_1_course_and_1_not_course, LeisureStudent.axiom)


def test_eql_axiom_descriptor_participation_detection():
    assert is_class_axiomatized_on_property(T20CricketFan, IsCrazyAbout)


def test_axiomatized_classes_are_domains_of_properties():
    assert T20CricketFan in PropertyDescriptor.domain_range_map[IsCrazyAbout]
    assert LeisureStudent in PropertyDescriptor.domain_range_map[TakesCourse]
    assert PropertyDescriptor.domain_range_map[TakesCourse][LeisureStudent] is Course
    assert PropertyDescriptor.domain_range_map[IsCrazyAbout][T20CricketFan] is Interest
    assert T20CricketFan in PropertyDescriptor.all_domains[IsCrazyAbout]
    assert LeisureStudent in PropertyDescriptor.all_domains[TakesCourse]
    assert ScienceStudent not in PropertyDescriptor.all_domains[TakesCourse]
