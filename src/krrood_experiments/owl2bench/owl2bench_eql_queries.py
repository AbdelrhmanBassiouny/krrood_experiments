import itertools
import json
import pickle
import time
from typing import List

import SPARQLWrapper
import rdflib
from krrood.entity_query_language.entity import (
    entity,
    variable,
    set_of,
    contains,
    variable_from,
    not_,
    exists,
)
from krrood.entity_query_language.entity_result_processors import (
    a,
    an,
    the,
)
from krrood.entity_query_language.predicate import HasType, symbolic_function
from krrood.entity_query_language.symbol_graph import SymbolGraph
from ripple_down_rules.utils import recursive_subclasses
from typing_extensions import Any, Optional, Callable, Iterable

from krrood_experiments.helpers import (
    evaluate_eql,
    QueryWithSelectables,
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.owl2bench_with_predicates import (
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
)
from krrood_experiments.owl_instances_loader import OwlInstancesRegistry


def get_eql_queries(
    registry: Optional[Callable[[type], Iterable]] = None,
) -> List[QueryWithSelectables]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    p = variable(Person, domain=None)
    o1 = variable_from(p.is_member_of)
    q2 = a(set_of(p, o1))
    q2 = QueryWithSelectables(q2, {"x": p, "y": o1}, 2)

    o1 = variable(Organization, domain=None)
    o2 = variable_from(o1.is_part_of)
    q3 = an(set_of(o1, o2))
    q3 = QueryWithSelectables(q3, {"x": o1, "y": o2}, 3)

    p = variable(Person, domain=None)
    q4 = an(entity(p.has_age).where(p.has_age))
    q4 = QueryWithSelectables(q4, {"x": p}, 4)

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

    o1 = variable(College, domain=None)
    c = variable_from(o1.has_college_discipline)
    q9 = an(set_of(o1, c).where(not_(HasType(c, Science))))
    q9 = QueryWithSelectables(q9, {"x": o1, "y": c}, 9)

    # p1 = variable(Person, domain=None)
    # p2 = variable_from(p1.has_collaboration_with)
    # q10 = an(set_of(p1, p2))
    #
    # p1 = variable(Person, domain=None)
    # p2 = variable_from(p1.is_advised_by)
    # q11 = an(set_of(p1, p2))
    #
    # p1 = variable(Person, domain=None)
    # q12 = an(entity(p1))
    #
    # wc = variable(WomanCollege, domain=None)
    # q13 = an(entity(wc))

    # ls = variable(LeisureStudent, domain=None)
    # q14 = an(entity(ls))
    #
    # o = variable(Organization, domain=None)
    # heads = variable_from(o.has_head)
    # q15 = an(entity(heads))
    #
    # o = variable(Organization, domain=None)
    # head = variable_from(o.has_h)
    # q16 = an(entity(o).where(exists(o, o.has_head)))
    #
    # ugs = variable(UGStudent, domain=None)
    # q17 = an(entity(ugs))
    # q17 = QueryWithSelectables(q17, {"X": ugs}, 17)

    eql_queries = [q2, q3, q4, q5, q7, q8, q9]  # , q10, q11, q12, q13]
    return eql_queries


def process_value_for_owl2bench_answer_comparison(value: Any):
    if hasattr(value, "uri"):
        return value.uri
    elif isinstance(value, rdflib.Literal):
        return value.value
    else:
        return value


if __name__ == "__main__":
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates()
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    def instances_for_class(cls):
        all_classes = [cls] + recursive_subclasses(cls)
        for clazz in all_classes:
            if cls not in registry._by_class:
                continue
            yield from registry._by_class[clazz]

    start_time = time.time()
    queries_with_selectables = get_eql_queries(instances_for_class)
    counts, results, times = evaluate_eql(queries_with_selectables)
    end_time = time.time()
    for i, count_ in enumerate(counts, 1):
        print(f"{i}:{count_} ({times[i - 1]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")

    # Initialize connection to GraphDB
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    # Execute query
    from krrood_experiments.owl2bench.sparql_queries import (
        all_queries as sparql_queries,
    )

    sparql_answers = {}
    for q in sparql_queries:
        if q.number not in results:
            continue
        sparql.setQuery(q.raw_sparql_string)
        res = sparql.query().convert()
        sparql_answers[q.number] = []
        for r in res["results"]["bindings"]:
            flat_r = {k: v["value"] for k, v in r.items()}
            sparql_answers[q.number].append(set(tuple(flat_r.items())))
    for i, query_results in results.items():
        uri_results = []
        for res in query_results:
            for k, v in res.items():
                res[k] = process_value_for_owl2bench_answer_comparison(v)
            uri_results.append(set(tuple(res.items())))
        for sol in uri_results:
            assert (
                sol in sparql_answers[i]
            ), f"{sol} not found in SPARQL answers, for query {i}"
        for gt_sol in sparql_answers[i]:
            try:
                assert (
                    gt_sol in uri_results
                ), f"{gt_sol} not found in EQL answers, for query {i}"
            except AssertionError:
                print(f"{gt_sol} not found in EQL answers, for query {i}")
                import pdbpp

                pdbpp.set_trace()
        assert len(sparql_answers[i]) == len(
            uri_results
        ), f"Number of results mismatch for query {i}"
