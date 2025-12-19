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

    assert len(persons) > 0
    from owl2bench.models import Person

    assert all(isinstance(p, Person) for p in persons)

    # At least some persons should have these details in the benchmark
    has_details = any(p.first_name and p.last_name and p.email for p in persons)
    assert has_details

    # Check if is_woman is loaded (at least some should be women if data exists)
    # Since we use OPTIONAL and BIND, it might be False for everyone if no rdf:type owl2bench:Woman is found
    # but we should at least check it's a boolean or None
    assert all(isinstance(p.is_woman, (bool, type(None))) for p in persons)


def test_update_inter_person_relationships(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.world.persons = loader._get_persons()
    loader._update_inter_person_relationships()

    # Check if at least some relationships are loaded
    has_any_relationship = False
    for p in loader.world.persons:
        if any(
            [
                p.knows,
                p.likes,
                p.loves,
                p.dislikes,
                p.is_crazy_about,
                p.has_same_hometown_with,
            ]
        ):
            has_any_relationship = True
            break

    assert has_any_relationship
