import pytest

import krrood_experiments.owl2bench.eql_queries as eql_queries
import SPARQLWrapper

from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)


@pytest.mark.skip(reason="Requires local GraphDB instance with OWL2Bench data loaded")
@pytest.mark.parametrize(
    "eql_query_obj",
    [
        pytest.param(q, id=f"q{q.sparql_query.number}")
        for q in eql_queries.all_queries
        # if owl2bench.sparql_queries.OWLProfile.RL in q.sparql_query.profile
    ],
)
def test_query(eql_query_obj):

    # Initialize connection to GraphDB
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    # Execute query
    sparql.setQuery(eql_query_obj.sparql_query.raw_sparql_string)
    sparql_results = sparql.query().convert()
    sparql_result_len = len(sparql_results["results"]["bindings"])

    # eql_result = list(eql_query_obj.query(world_from_graph_db).evaluate())
    # eql_result_len = len(eql_result)
    # assert sparql_result_len == eql_result_len
    print(sparql_result_len)


def test_reasoning():
    registry = load_instances_for_owl2bench_with_predicates()

    # queries_with_selectables = eql_queries.get_eql_queries(instances_for_class)
    # assert len(queries_with_selectables) == len(eql_queries.all_queries)
