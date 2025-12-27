import textwrap
from pathlib import Path
import warnings

import pytest
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

from owl2bench.loader import WorldLoader, OntologyLoadError
from owl2bench.model.base import Person


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
    loader.parse()
    persons = loader.world.persons
    assert len(persons) > 0
    any_knows = False
    for person in persons:
        assert isinstance(person.identifier, str)
        assert isinstance(person.first_name, str)
        assert isinstance(person.last_name, str)
        assert isinstance(person.telephone_number, str)
        assert isinstance(person.age, int)
        assert isinstance(person.e_mail_address, str)
        assert person.title is None or isinstance(person.title, str)
        assert isinstance(person.knows, list)
        if len(person.knows) > 0:
            any_knows = True
            for known_person in person.knows:
                assert isinstance(known_person, Person)

    assert any_knows, "No 'knows' relationships found in the loaded data"
