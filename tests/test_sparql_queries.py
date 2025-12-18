import pytest
from owl2bench.sparql_queries import *
from SPARQLWrapper import SPARQLWrapper, JSON


@pytest.mark.parametrize(
    "query_obj",
    [
        pytest.param(q, id=f"q{q.number}")
        for q in all_queries
        if OWLProfile.RL in q.profile
    ],
)
def test_query(query_obj):
    # Initialize connection to GraphDB
    sparql = SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(JSON)

    # Execute query
    sparql.setQuery(query_obj.raw_sparql_string)
    results = sparql.query().convert()

    # Verify results
    assert results is not None
    # assert len(results["results"]["bindings"]) > 0
    print(
        f"Query {query_obj.number} results count: {len(results['results']['bindings'])}"
    )
