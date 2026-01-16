import time
from os.path import dirname
from pathlib import Path

import SPARQLWrapper
from krrood.entity_query_language.symbol_graph import SymbolGraph

from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
    evaluate_eql,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_eql_queries import (
    get_eql_queries,
    process_value_for_owl2bench_answer_comparison,
)


def test_queries():

    file_name = Path(
        f"{dirname(__file__)}",
        "",
        "..",
        "..",
        "..",
        "resources",
        "owl2bench_clean.owl",
    )
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates(str(file_name))
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    def instances_for_class(cls):
        for instance in SymbolGraph().get_instances_of_type(cls):
            yield instance

    start_time = time.time()
    queries_with_selectables = get_eql_queries(instances_for_class)
    counts, results, times = evaluate_eql(queries_with_selectables)
    end_time = time.time()
    for i, (r, count_) in enumerate(zip(results, counts)):
        print(f"{r}:{count_} ({times[i]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")
