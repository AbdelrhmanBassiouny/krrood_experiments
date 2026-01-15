import time
import weakref
from typing import List

import SPARQLWrapper
import rdflib
from krrood.entity_query_language.entity import (
    entity,
    variable,
    set_of,
    contains,
    variable_from,
    flatten,
)
from krrood.entity_query_language.entity_result_processors import (
    a,
    an,
)
from krrood.entity_query_language.predicate import symbolic_function
from krrood.entity_query_language.symbol_graph import SymbolGraph
from ripple_down_rules.utils import recursive_subclasses
from typing_extensions import Any, Optional, Callable, Iterable

from krrood_experiments.owl2bench.ontomatic.helpers import (
    evaluate_eql,
    QueryWithSelectables,
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates import (
    Department,
    Student,
    University,
    Publication,
    Professor,
    Person,
    Chair,
    AssociateProfessor,
    ResearchGroup,
    Organization,
    T20CricketFan,
    Science,
    College,
    WomanCollege,
    LeisureStudent,
    UGStudent,
    Faculty,
    Engineering,
)


def get_eql_queries(
    registry: Optional[Callable[[type], Iterable]] = None,
) -> List[QueryWithSelectables]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    p = variable(Person, domain=None)
    o1 = variable_from(p.is_member_of)
    q2 = a(set_of(p, o1).distinct(p.uri, o1.uri))
    q2 = QueryWithSelectables(q2, {"x": p, "y": o1}, 2)

    o1 = variable(Organization, domain=None)
    o2 = variable_from(o1.is_part_of)
    q3 = an(set_of(o1, o2).distinct(o1.uri, o2.uri))
    q3 = QueryWithSelectables(q3, {"x": o1, "y": o2}, 3)

    p = variable(Person, domain=None)
    q4 = an(set_of(p, p.has_age).where(p.has_age))
    q4 = QueryWithSelectables(q4, {"x": p, "y": p.has_age}, 4)

    p = variable(T20CricketFan, None)
    q5 = an(entity(p))
    q5 = QueryWithSelectables(q5, {"x": p}, 5)

    u = variable(University, domain=None)
    p = variable_from(u.has_alumnus)
    q7 = an(set_of(u, p))
    q7 = QueryWithSelectables(q7, {"x": u, "y": p}, 7)

    o1 = variable(Organization, domain=None)
    o2 = variable_from(o1.is_affiliated_organization_of)
    q8 = an(set_of(o1, o2))
    q8 = QueryWithSelectables(q8, {"x": o1, "y": o2}, 8)

    p1 = variable(Person, domain=None)
    p2 = variable_from(p1.has_collaboration_with)
    q10 = an(set_of(p1, p2))
    q10 = QueryWithSelectables(q10, {"x": p1, "y": p2}, 10)

    p1 = variable(Person, domain=None)
    p2 = variable_from(p1.is_advised_by)
    q11 = an(set_of(p1, p2))
    q11 = QueryWithSelectables(q11, {"x": p1, "y": p2}, 11)

    p1 = variable(Person, domain=None)
    q12 = an(entity(p1).distinct(p1.uri))
    q12 = QueryWithSelectables(q12, {"x": p1}, 12)

    @symbolic_function
    def length(lst):
        return len(lst)

    p = variable(Person, domain=None)
    q15 = an(entity(p).where(length(p.is_head_of) > 0))
    q15 = QueryWithSelectables(q15, {"x": p}, 15)

    o = variable(Organization, domain=None)
    q16 = an(entity(o).where(length(o.has_head) > 0).distinct(o.uri))
    q16 = QueryWithSelectables(q16, {"x": o}, 16)

    p1 = variable(Faculty, domain=None)
    q19 = an(entity(p1).distinct(p1.uri))
    q19 = QueryWithSelectables(q19, {"x": p1}, 19)

    p1 = variable(Person, domain=None)
    p2 = variable_from(p1.has_same_home_town_with)
    q20 = an(set_of(p1, p2))
    q20 = QueryWithSelectables(q20, {"x": p1, "y": p2}, 20)

    s = variable(Student, domain=None)
    so = flatten(s.is_student_of)
    po = flatten(so.is_part_of)
    q21 = an(
        set_of(s, so).where(contains(po.has_college_discipline.uri, "Engineering"))
    )
    q21 = QueryWithSelectables(q21, {"x": s, "y": so}, 21)

    s = variable(Student, domain=None)
    o = variable(Organization, domain=None)
    z = flatten(o.has_dean)
    c = flatten(z.teaches_course)
    q22 = an(set_of(s, c).where(contains(s.takes_course, c)).distinct(s.uri, c.uri))
    q22 = QueryWithSelectables(q22, {"s": s, "c": c}, 22)

    eql_queries = [
        q2,
        q3,
        q4,
        q5,
        q7,
        q8,
        q10,
        q11,
        q12,
        q15,
        q16,
        q19,
        q20,
        q21,
        q22,
    ]
    return eql_queries


def q10_python_equivalent(registry: Callable[[type], Iterable]):
    results = []
    for p1 in registry(Person):
        for p2 in p1.has_collaboration_with:
            results.append({"x": p1, "y": p2})
    print(f"Q10 results count: {len(results)}")
    return results


def process_value_for_owl2bench_answer_comparison(value: Any):
    if isinstance(value, weakref.ReferenceType):
        value = value()
    if hasattr(value, "uri"):
        return value.uri
    elif isinstance(value, rdflib.Literal):
        return value.value
    else:
        if not isinstance(value, str):
            import pdbpp

            pdbpp.set_trace()
        return value
