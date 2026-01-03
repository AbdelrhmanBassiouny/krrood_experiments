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
    ResultQuantifier,
)

from .owl2bench_with_predicates import *
from . import sparql_queries


@dataclass
class EQLQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    query: ResultQuantifier
    """
    A function that takes a World and returns an EQL Query.
    """


p1 = variable(Person, domain=None)
p2 = variable_from(p1.knows)
eql1 = an(set_of(p1, p2).where(contains(p1.knows, p2)))

q1 = EQLQuery(sparql_queries.q1, eql1)

o1 = variable(Organization, domain=None)
p = variable_from(o1.members)
eql2 = an(entity(p).where(contains(o1.members, p)))

q2 = EQLQuery(sparql_queries.q2, eql2)


o1 = variable(Organization, domain=None)
o2 = variable_from(o1.is_part_of)
eql3 = an(set_of(o1, o2).where(contains(o1.is_part_of, o2)))

q3 = EQLQuery(sparql_queries.q3, eql3)


p = variable(Person, domain=None)
eql4 = an(entity(p.age).where(p.age))


q4 = EQLQuery(sparql_queries.q4, eql4)


p = variable(Person, domain=None)
eql6 = an(entity(p).where(contains(p.knows, p)))


q6 = EQLQuery(sparql_queries.q6, eql6)


u = variable(University, domain=None)
p = variable_from(u.alumni)
eql7 = an(set_of(u, p).where(contains(u.alumni, p)))


q7 = EQLQuery(sparql_queries.q7, eql7)


o1 = variable(Organization, domain=None)
o2 = variable_from(o1.affiliated_organizations)
eql8 = an(set_of(o1, o2).where(contains(o1.affiliated_organizations, o2)))


q8 = EQLQuery(sparql_queries.q8, eql8)


o1 = variable(Organization, domain=None)
c = variable_from(o1.courses)
eql9 = an(
    set_of(o1, c).where(
        and_(HasType(c.topic, MaterialScienceEngineering), contains(o1.courses, c))
    )
)


q9 = EQLQuery(sparql_queries.q9, eql9)


p1 = variable(Person, domain=None)
p2 = variable_from(p1.collaborates_with)
eql10 = an(set_of(p1, p2).where(contains(p1.collaborates_with, p2)))


q10 = EQLQuery(sparql_queries.q10, eql10)


p1 = variable(Person, domain=None)
p2 = variable_from(p1.is_advised_by)
eql11 = an(set_of(p1, p2).where(contains(p1.is_advised_by, p2)))


q11 = EQLQuery(sparql_queries.q11, eql11)


p = variable(Person, domain=None)
eql12 = an(entity(p))


q12 = EQLQuery(sparql_queries.q12, eql12)


p1 = variable(Person, domain=None)
c = variable(College, domain=None)
p = variable_from(c.members)
eql13 = an(entity(c).where(for_all(c.members, p.gender == "female")))


q13 = EQLQuery(sparql_queries.q13, eql13)


p1 = variable(Person, domain=None)
c = variable_from(p1.takes_course)
eql14 = an(entity(p1).where(count(c) == 1))


q14 = EQLQuery(sparql_queries.q14, eql14)


p = variable(Person, domain=None)
eql15 = an(entity(p.head).where(p.head))


q15 = EQLQuery(sparql_queries.q15, eql15)


o = variable(Organization, domain=None)
eql16 = an(entity(o).where(o.head))


q16 = EQLQuery(sparql_queries.q16, eql16)


@symbolic_function
def is_undergraduate_student(person: Person) -> bool:
    return len(person.enrolled_in) == 1 and isinstance(person.enrolled_in[0], Program)


p = variable(Person, domain=None)
eql17 = an(entity(p).where(is_undergraduate_student(p)))


q17 = EQLQuery(sparql_queries.q17, eql17)


@symbolic_function
def length(x) -> int:
    return len(x)


p = variable(Person, domain=None)
eql18 = an(entity(p).where(length(p.hobbies) >= 3))


q18 = EQLQuery(sparql_queries.q18, eql18)


c = variable(Course, domain=None)
p = variable_from(c.teachers)
eql19 = an(entity(p).distinct())


q19 = EQLQuery(sparql_queries.q19, eql19)


p1 = variable(Person, domain=None)
p2 = variable_from(p1.has_same_hometown_as)
eql20 = an(set_of(p1, p2).where(contains(p1.has_same_hometown_as, p2)))


q20 = EQLQuery(sparql_queries.q20, eql20)


p = variable(Person, domain=None)
c = variable_from(p.takes_course)
eql21 = an(entity(p).where(exists(p, HasType(c.topic, Engineering))))


q21 = EQLQuery(sparql_queries.q21, eql21)


p = variable(Person, domain=None)
org = variable(Organization, domain=None)
sc = variable_from(p.takes_course)
eql22 = a(set_of(p, sc).where(org.dean, contains(sc.teachers, org.dean)))


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
