import itertools
import time
from typing import List

import rdflib
from krrood.entity_query_language.entity import (
    entity,
    variable,
    set_of,
    contains,
    variable_from,
)
from krrood.entity_query_language.entity_result_processors import (
    a,
    an,
    the,
)
from krrood.entity_query_language.predicate import HasType
from typing_extensions import Any, Optional

from krrood_experiments.helpers import (
    evaluate_eql,
    load_instances_for_lubm_with_predicates,
    get_lubm_answers,
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
)
from krrood_experiments.owl_instances_loader import OwlInstancesRegistry


def get_eql_queries(
    registry_: Optional[OwlInstancesRegistry] = None,
) -> List[QueryWithSelectables]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    p = variable(Person, domain=None)
    p2 = variable_from(p.knows)
    q1 = a(set_of(p, p2).where(contains(p2.knows, p2)))
    q1 = QueryWithSelectables(q1, {"X": p, "Y": p2})

    eql_queries = [q1]
    return eql_queries


def process_value_for_owl2bench_answer_comparison(value: Any):
    if hasattr(value, "uri"):
        return value.uri
    elif isinstance(value, rdflib.Literal):
        return value.value
    else:
        return value


if __name__ == "__main__":
    registry = load_instances_for_owl2bench_with_predicates()
    start_time = time.time()
    queries_with_selectables = get_eql_queries(registry)
    counts, results, times = evaluate_eql(queries_with_selectables)
    end_time = time.time()
    for i, n in enumerate(counts, 1):
        print(f"{i}:{n} ({times[i - 1]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")

    # sparql_answers = get_lubm_answers()
    # for i, query_results in enumerate(results, 1):
    #     uri_results = []
    #     for res in query_results:
    #         uri_results.append(
    #             {k: process_value_for_owl2bench_answer_comparison(v) for k, v in res.items()}
    #         )
    #     for sol in uri_results:
    #         assert (
    #             sol in sparql_answers[i]
    #         ), f"{sol} not found in SPARQL answers, for query {i}"
    #     for gt_sol in sparql_answers[i]:
    #         assert (
    #             gt_sol in uri_results
    #         ), f"{gt_sol} not found in EQL answers, for query {i}"
    #     assert len(sparql_answers[i]) == len(
    #         uri_results
    #     ), f"Number of results mismatch for query {i}"
