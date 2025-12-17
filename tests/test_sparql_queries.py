from owl2bench.sparql_queries import *
from SPARQLWrapper import SPARQLWrapper, JSON


def test_q1():
    # Initialize connection to GraphDB
    sparql = SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(JSON)

    # Execute q1 query
    sparql.setQuery(q1.query)
    results = sparql.query().convert()

    # Verify results
    assert results is not None
    assert len(results["results"]["bindings"]) > 0
    print(len(results["results"]["bindings"]))
