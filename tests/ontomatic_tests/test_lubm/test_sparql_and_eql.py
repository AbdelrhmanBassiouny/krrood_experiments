from __future__ import annotations

import time

import pytest

from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_lubm_with_predicates,
    get_lubm_answers,
)
from krrood_experiments.lubm.lubm_eql_queries import (
    evaluate_eql,
    get_eql_queries,
    process_value_for_lubm_answer_comparison,
)


@pytest.mark.skip("unclean ontologies are not supported anymore")
def test_eql_counts_match_sparql():
    registry = load_instances_for_lubm_with_predicates()
    start_time = time.time()
    queries_with_selectables = get_eql_queries(registry)
    counts, results, times = evaluate_eql(queries_with_selectables)
    end_time = time.time()
    for i, n in enumerate(counts, 1):
        print(f"{i}:{n} ({times[i - 1]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")

    lubm_answers = get_lubm_answers()
    for i, query_results in results.items():
        uri_results = []
        for res in query_results:
            uri_results.append(
                {k: process_value_for_lubm_answer_comparison(v) for k, v in res.items()}
            )
        for sol in uri_results:
            assert (
                sol in lubm_answers[i]
            ), f"{sol} not found in LUBM answers, for query {i}"
        for gt_sol in lubm_answers[i]:
            assert (
                gt_sol in uri_results
            ), f"{gt_sol} not found in EQL answers, for query {i}"
        assert len(lubm_answers[i]) == len(
            uri_results
        ), f"Number of results mismatch for query {i}"
