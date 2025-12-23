import textwrap
from pathlib import Path
import warnings

import pytest
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

from owl2bench.loader import WorldLoader, OntologyLoadError


@pytest.fixture(scope="session")
def sparql_wrapper():
    """
    Load the OWL2Bench ontology from owl2bench_RL_1.brf
    """
    sparql = SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(JSON)
    return sparql


def test_get_persons(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    persons = loader._get_persons()
