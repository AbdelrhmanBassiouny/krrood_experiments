from dataclasses import dataclass
from typing import Callable

from krrood.entity_query_language import predicate
from krrood.entity_query_language.entity import (
    variable,
    contains,
    set_of,
    entity,
    variable_from,
    and_,
    for_all,
    flatten,
    exists,
)
from krrood.entity_query_language.entity_result_processors import an, count, a
from krrood.entity_query_language.predicate import HasType, symbolic_function
from krrood.entity_query_language.symbolic import (
    SymbolicExpression,
)

from .model.interests import Cricket
from .model.base import Course
from .model.programs import UndergraduateProgram
from .model.organizations import College
from .model.college_disciplines import MaterialScienceEngineering, Engineering
from .model.organizations import University
from .model.base import World, Person, Organization
from . import sparql_queries


@dataclass
class EQLQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    query: Callable[[World], SymbolicExpression]
    """
    A function that takes a World and returns an EQL Query.
    """


def eql1(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable_from(p1.knows)
    q = an(set_of(p1, p2))
    return q


q1 = EQLQuery(sparql_queries.q1, eql1)


def eql2(world: World):
    o1 = variable(Organization, world.organizations)
    p = variable_from(o1.members)
    return an(entity(p))


q2 = EQLQuery(sparql_queries.q2, eql2)


def eql3(world: World):
    o1 = variable(Organization, world.organizations)
    o2 = variable_from(o1.is_part_of)
    return an(set_of(o1, o2))


q3 = EQLQuery(sparql_queries.q3, eql3)


def eql4(world: World):
    p = variable(Person, world.persons)
    return an(entity(p.age).where(p.age))


q4 = EQLQuery(sparql_queries.q4, eql4)


def eql5(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(HasType(p.is_crazy_about, Cricket)))


def eql6(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(contains(p.knows, p)))


q6 = EQLQuery(sparql_queries.q6, eql6)


def eql7(world: World):
    u = variable(University, world.organizations)
    p = variable_from(u.alumni)
    return an(set_of(u, p))


q7 = EQLQuery(sparql_queries.q7, eql7)


def eql8(world: World):
    o1 = variable(Organization, world.organizations)
    o2 = variable_from(o1.affiliated_organizations)
    return an(set_of(o1, o2))


q8 = EQLQuery(sparql_queries.q8, eql8)


def eql9(world: World):
    o1 = variable(Organization, world.organizations)
    c = variable_from(o1.courses)
    return an(set_of(o1, c).where(and_(HasType(c.topic, MaterialScienceEngineering))))


q9 = EQLQuery(sparql_queries.q9, eql9)


def eql10(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable_from(p1.collaborates_with)
    return an(set_of(p1, p2))


q10 = EQLQuery(sparql_queries.q10, eql10)


def eql11(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable_from(p1.is_advised_by)
    return an(set_of(p1, p2))


q11 = EQLQuery(sparql_queries.q11, eql11)


def eql12(world: World):
    p = variable(Person, world.persons)
    return an(entity(p))


q12 = EQLQuery(sparql_queries.q12, eql12)


def eql13(world: World):
    c = variable(College, world.organizations)
    p = variable_from(c.members)
    return an(entity(c).where(for_all(c.members, p.gender == "female")))


q13 = EQLQuery(sparql_queries.q13, eql13)


def eql14(world: World):
    p = variable(Person, world.persons)
    c = variable_from(p.takes_course)
    return an(entity(p).where(count(c) == 1))


q14 = EQLQuery(sparql_queries.q14, eql14)


def eql15(world: World):
    o = variable(Organization, world.organizations)
    return an(entity(o.head).where(o.head))


q15 = EQLQuery(sparql_queries.q15, eql15)


def eql16(world: World):
    o = variable(Organization, world.organizations)
    return an(entity(o).where(o.head))


q16 = EQLQuery(sparql_queries.q16, eql16)


@symbolic_function
def is_undergraduate_student(person: Person) -> bool:
    return len(person.enrolled_in) == 1 and isinstance(
        person.enrolled_in[0], UndergraduateProgram
    )


def eql17(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(is_undergraduate_student(p)))


q17 = EQLQuery(sparql_queries.q17, eql17)


@symbolic_function
def length(x) -> int:
    return len(x)


def eql18(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(length(p.hobbies) >= 3))


q18 = EQLQuery(sparql_queries.q18, eql18)


def eql19(world: World):
    c = variable(Course, world.courses)
    p = variable_from(c.teachers)
    return an(entity(p).distinct())


q19 = EQLQuery(sparql_queries.q19, eql19)


def eql20(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable_from(p1.has_same_hometown_as)
    return an(set_of(p1, p2))


q20 = EQLQuery(sparql_queries.q20, eql20)


def eql21(world: World):
    p = variable(Person, world.persons)
    c = variable_from(p.takes_course)
    return an(entity(p).where(exists(p, HasType(c.topic, Engineering))))


q21 = EQLQuery(sparql_queries.q21, eql21)


def eql22(world: World):
    p = variable(Person, world.persons)
    org = variable(Organization, world.organizations)
    sc = variable_from(p.takes_course)
    return a(set_of(p, sc).where(org.dean, contains(sc.teachers, org.dean)))


q22 = EQLQuery(sparql_queries.q22, eql22)

all_queries = [
    q1,
    q2,
    q3,
    q4,
    q6,
    q7,
    q8,
    q9,
    q10,
    q11,
    q12,
    q13,
    q14,
    q15,
    q16,
    q17,
    # q18,
    q19,
    q20,
    q21,
    q22,
]
