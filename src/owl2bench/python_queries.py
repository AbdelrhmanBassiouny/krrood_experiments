from dataclasses import dataclass
from typing import Callable

from krrood.entity_query_language.entity import (
    variable,
    entity,
    variable_from,
)
from krrood.entity_query_language.entity_result_processors import an
from typing_extensions import Iterator

from . import sparql_queries
from .model.base import World, Person, Organization
from .model.college_disciplines import MaterialScienceEngineering, Engineering
from .model.interests import Cricket
from .model.organizations import College
from .model.organizations import University
from .model.programs import UndergraduateProgram


@dataclass
class PythonQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    query: Callable[[World], Iterator]
    """
    A function that takes a World and returns an iterator of answers.
    """


def python_query_1(world: World):
    yield from ((p1, p2) for p1 in world.persons for p2 in p1.knows)


q1 = PythonQuery(sparql_queries.q1, python_query_1)


def python_query_2(world: World):
    yield from (p for o1 in world.organizations for p in o1.members)


q2 = PythonQuery(sparql_queries.q2, python_query_2)


def python_query_3(world: World):
    yield from ((o1, o2) for o1 in world.organizations for o2 in o1.is_part_of)


q3 = PythonQuery(sparql_queries.q3, python_query_3)


def python_query_4(world: World):
    yield from (p.age for p in world.persons if p.age)


q4 = PythonQuery(sparql_queries.q4, python_query_4)


def python_query_5(world: World):
    yield from (p for p in world.persons if isinstance(p.is_crazy_about, Cricket))


q5 = PythonQuery(sparql_queries.q5, python_query_5)


def python_query_6(world: World):
    yield from (p for p in world.persons if p in p.knows)


q6 = PythonQuery(sparql_queries.q6, python_query_6)


def python_query_7(world: World):
    yield from (
        (u, p)
        for u in world.organizations
        if isinstance(u, University)
        for p in u.alumni
    )


q7 = PythonQuery(sparql_queries.q7, python_query_7)


def python_query_8(world: World):
    yield from (
        (o1, o2)
        for o1 in world.organizations
        if isinstance(o1, Organization)
        for o2 in o1.affiliated_organizations
    )


q8 = PythonQuery(sparql_queries.q8, python_query_8)


def python_query_9(world: World):
    yield from (
        (o1, c)
        for o1 in world.organizations
        if isinstance(o1, Organization)
        for c in o1.courses
        if isinstance(c.topic, MaterialScienceEngineering)
    )


q9 = PythonQuery(sparql_queries.q9, python_query_9)


def python_query_10(world: World):
    yield from (
        (p1, p2)
        for p1 in world.persons
        if isinstance(p1, Person)
        for p2 in p1.collaborates_with
    )


q10 = PythonQuery(sparql_queries.q10, python_query_10)


def python_query_11(world: World):
    yield from (
        (p1, p2)
        for p1 in world.persons
        if isinstance(p1, Person)
        for p2 in p1.is_advised_by
    )


q11 = PythonQuery(sparql_queries.q11, python_query_11)


def python_query_12(world: World):
    yield from (p for p in world.persons if isinstance(p, Person))


q12 = PythonQuery(sparql_queries.q12, python_query_12)


def python_query_13(world: World):
    yield from (
        c
        for c in world.organizations
        if isinstance(c, College) and all(p.gender == "female" for p in c.members)
    )


q13 = PythonQuery(sparql_queries.q13, python_query_13)


def python_query_14(world: World):
    yield from (p for p in world.persons if len(p.takes_course) == 1)


q14 = PythonQuery(sparql_queries.q14, python_query_14)


def python_query_15(world: World):
    yield from (
        o
        for o in world.organizations
        if isinstance(o, Organization) and o.head is not None
    )


q15 = PythonQuery(sparql_queries.q15, python_query_15)


def python_query_16(world: World):
    yield from (
        o.head
        for o in world.organizations
        if isinstance(o, Organization) and o.head is not None
    )


q16 = PythonQuery(sparql_queries.q16, python_query_16)


def python_query_17(world: World):
    yield from (
        p
        for p in world.persons
        if len(p.enrolled_in) == 1
        and isinstance(p.enrolled_in[0], UndergraduateProgram)
    )


q17 = PythonQuery(sparql_queries.q17, python_query_17)


def python_query_18(world: World):
    yield from (p for p in world.persons if len(p.hobbies) >= 3)


q18 = PythonQuery(sparql_queries.q18, python_query_18)


def python_query_19(world: World):
    seen_persons = set()
    for c in world.courses:
        for p in c.teachers:
            if p not in seen_persons:
                yield p
                seen_persons.add(p)


q19 = PythonQuery(sparql_queries.q19, python_query_19)


def python_query_20(world: World):
    yield from ((p1, p2) for p1 in world.persons for p2 in p1.has_same_hometown_as)


q20 = PythonQuery(sparql_queries.q20, python_query_20)


def python_query_21(world: World):
    yield from (
        p
        for p in world.persons
        if isinstance(p, Person)
        and any(isinstance(c.topic, Engineering) for c in p.takes_course)
    )


q21 = PythonQuery(sparql_queries.q21, python_query_21)


def python_query_22(world: World):
    yield from (
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
