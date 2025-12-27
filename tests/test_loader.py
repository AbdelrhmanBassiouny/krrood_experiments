import textwrap
from pathlib import Path
import warnings

import pytest
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

from owl2bench.loader import WorldLoader, OntologyLoadError
from owl2bench.model.base import Person, Organization, CollegeDiscipline
from owl2bench.model.organizations import University, College


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
        assert isinstance(person.age, str)
        assert isinstance(person.e_mail_address, str)
        assert person.title is None or isinstance(person.title, str)
        assert isinstance(person.knows, list)
        if len(person.knows) > 0:
            any_knows = True
            for known_person in person.knows:
                assert isinstance(known_person, Person)

    assert any_knows, "No 'knows' relationships found in the loaded data"


def test_get_organization_members(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    organizations = loader.world.organizations
    assert len(organizations) > 0
    any_members = False
    for org in organizations:
        assert isinstance(org, Organization)
        if len(org.members) > 0:
            any_members = True
            for member in org.members:
                assert isinstance(member, Person)

    assert any_members, "No organization members found in the loaded data"


def test_get_university_alumni(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    universities = [
        org for org in loader.world.organizations if isinstance(org, University)
    ]
    assert len(universities) > 0
    any_alumni = False
    for university in universities:
        if len(university.alumni) > 0:
            any_alumni = True
            for alumnus in university.alumni:
                assert isinstance(alumnus, Person)

    assert any_alumni, "No university alumni found in the loaded data"


def test_get_organization_affiliations(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    organizations = loader.world.organizations
    assert len(organizations) > 0
    any_affiliations = False
    for org in organizations:
        if len(org.affiliated_organizations) > 0:
            any_affiliations = True
            for affiliated_org in org.affiliated_organizations:
                assert isinstance(affiliated_org, Organization)

    assert any_affiliations, "No organization affiliations found in the loaded data"


def test_get_college_disciplines(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    colleges = [org for org in loader.world.organizations if isinstance(org, College)]
    assert len(colleges) > 0
    any_disciplines = False
    for college in colleges:
        if len(college.disciplines) > 0:
            any_disciplines = True
            for discipline in college.disciplines:
                assert isinstance(discipline, CollegeDiscipline)

    assert any_disciplines, "No college disciplines found in the loaded data"
