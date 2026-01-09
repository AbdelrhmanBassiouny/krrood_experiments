from dataclasses import dataclass
from typing import Callable

from doc.eql.test_tmp.result_quantifiers import world
from krrood.entity_query_language.entity import (
    variable,
    contains,
    set_of,
    entity,
    variable_from,
    and_,
    for_all,
    exists,
)
from krrood.entity_query_language.entity_result_processors import an, count, a
from krrood.entity_query_language.predicate import HasType, symbolic_function
from krrood.entity_query_language.symbolic import (
    SymbolicExpression,
)
from typing_extensions import Iterable

from .model.interests import Cricket
from .model.base import Course
from .model.programs import UndergraduateProgram
from .model.organizations import College
from .model.college_disciplines import MaterialScienceEngineering, Engineering
from .model.organizations import University
from .model.base import World, Person, Organization
from . import sparql_queries


@dataclass
class PythonQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    query: Callable[[World], Iterable]
    """
    A function that takes a World and returns an EQL Query.
    """


def python_query_1(world: World):
    return ((p1, p2) for p1 in world.persons for p2 in p1.knows)


q1 = PythonQuery(sparql_queries.q1, python_query_1)


def eql2(world: World):
    o1 = variable(Organization, world.organizations)
    p = variable_from(o1.members)
    return an(entity(p))


def python_query_2(world: World):
    return (p for o1 in world.organizations for p in o1.members)


q2 = PythonQuery(sparql_queries.q2, python_query_2)


def python_query_3(world: World):
    return ((o1, o2) for o1 in world.organizations for o2 in o1.is_part_of)


q3 = PythonQuery(sparql_queries.q3, python_query_3)


def python_query_4(world: World):
    return (p.age for p in world.persons if p.age)


q4 = PythonQuery(sparql_queries.q4, python_query_4)


def python_query_5(world: World):
    return (p for p in world.persons if isinstance(p.is_crazy_about, Cricket))


q5 = PythonQuery(sparql_queries.q5, python_query_5)


def python_query_6(world: World):
    return (p for p in world.persons if p in p.knows)


q6 = PythonQuery(sparql_queries.q6, python_query_6)


def python_query_7(world: World):
    return (
        (u, p)
        for u in world.organizations
        if isinstance(u, University)
        for p in u.alumni
    )


q7 = PythonQuery(sparql_queries.q7, python_query_7)


def python_query_8(world: World):
    return (
        (o1, o2)
        for o1 in world.organizations
        if isinstance(o1, Organization)
        for o2 in o1.affiliated_organizations
    )


q8 = PythonQuery(sparql_queries.q8, python_query_8)


def python_query_9(world: World):
    return (
        (o1, c)
        for o1 in world.organizations
        if isinstance(o1, Organization)
        for c in o1.courses
        if isinstance(c.topic, MaterialScienceEngineering)
    )


q9 = PythonQuery(sparql_queries.q9, python_query_9)


def python_query_10(world: World):
    return (
        (p1, p2)
        for p1 in world.persons
        if isinstance(p1, Person)
        for p2 in p1.collaborates_with
    )


q10 = PythonQuery(sparql_queries.q10, python_query_10)


def python_query_11(world: World):
    return (
        (p1, p2)
        for p1 in world.persons
        if isinstance(p1, Person)
        for p2 in p1.is_advised_by
    )


q11 = PythonQuery(sparql_queries.q11, python_query_11)


def python_query_12(world: World):
    return (p for p in world.persons if isinstance(p, Person))


q12 = PythonQuery(sparql_queries.q12, python_query_12)


def python_query_13(world: World):
    return (
        c
        for c in world.organizations
        if isinstance(c, College) and all(p.gender == "female" for p in c.members)
    )


q13 = PythonQuery(sparql_queries.q13, python_query_13)


def python_query_14(world: World):
    return (p for p in world.persons if len(p.takes_course) == 1)


q14 = PythonQuery(sparql_queries.q14, python_query_14)


def python_query_15(world: World):
    return (
        o
        for o in world.organizations
        if isinstance(o, Organization) and o.head is not None
    )


q15 = PythonQuery(sparql_queries.q15, python_query_15)


def python_query_16(world: World):
    return (
        o.head
        for o in world.organizations
        if isinstance(o, Organization) and o.head is not None
    )


q16 = PythonQuery(sparql_queries.q16, python_query_16)


@symbolic_function
def is_undergraduate_student(person: Person) -> bool:
    return len(person.enrolled_in) == 1 and isinstance(
        person.enrolled_in[0], UndergraduateProgram
    )


def eql17(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(is_undergraduate_student(p)))


q17 = PythonQuery(sparql_queries.q17, eql17)


@symbolic_function
def length(x) -> int:
    return len(x)


def eql18(world: World):
    p = variable(Person, world.persons)
    return an(entity(p).where(length(p.hobbies) >= 3))


q18 = PythonQuery(sparql_queries.q18, eql18)


def eql19(world: World):
    c = variable(Course, world.courses)
    p = variable_from(c.teachers)
    return an(entity(p).distinct())


q19 = PythonQuery(sparql_queries.q19, eql19)


def eql20(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable_from(p1.has_same_hometown_as)
    return an(set_of(p1, p2))


q20 = PythonQuery(sparql_queries.q20, eql20)


def python_query_21(world: World):
    p = variable(Person, world.persons)
    c = variable_from(p.takes_course)
    return an(entity(p).where(exists(p, HasType(c.topic, Engineering))))


q21 = PythonQuery(sparql_queries.q21, python_query_21)


def python_query_22(world: World):
    return (
        (p, sc)
        for p in world.persons
        if isinstance(p, Person)
        for org in world.organizations
        if isinstance(org, Organization) and org.dean is not None
        for sc in p.takes_course
        if org.dean in sc.teachers
    )


q22 = PythonQuery(sparql_queries.q22, python_query_22)

all_queries = [
    q1,
    q2,
    q3,
    q4,
    q5,
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
