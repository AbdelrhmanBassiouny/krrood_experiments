import textwrap
from pathlib import Path
import warnings

import pytest
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

from owl2bench.loader import WorldLoader, OntologyLoadError
from owl2bench.model.base import (
    Person,
    Organization,
    CollegeDiscipline,
    Course,
    Program,
)
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
    any_gender = False
    for person in persons:
        assert isinstance(person.identifier, str)
        assert isinstance(person.first_name, str)
        assert isinstance(person.last_name, str)
        assert person.gender is None or person.gender in ["Man", "Woman"]
        if person.gender:
            any_gender = True
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
    assert any_gender, "No gender information found in the loaded data"


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


def test_get_person_collaborations(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    persons = loader.world.persons
    assert len(persons) > 0
    any_collaborations = False
    for person in persons:
        if len(person.collaborates_with) > 0:
            any_collaborations = True
            for collaborator in person.collaborates_with:
                assert isinstance(collaborator, Person)

    assert any_collaborations, "No person collaborations found in the loaded data"


def test_get_person_advisors(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    persons = loader.world.persons
    assert len(persons) > 0
    any_advisors = False
    for person in persons:
        if len(person.is_advised_by) > 0:
            any_advisors = True
            for advisor in person.is_advised_by:
                assert isinstance(advisor, Person)

    assert any_advisors, "No person advisors found in the loaded data"


def test_get_courses(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    courses = loader.world.courses
    assert len(courses) > 0
    any_person_takes_course = False
    for course in courses:
        assert isinstance(course, Course)
        assert isinstance(course.identifier, str)
        assert isinstance(course.organization, Organization)
        assert isinstance(course.topic, CollegeDiscipline)

    for person in loader.world.persons:
        if len(person.takes_course) > 0:
            any_person_takes_course = True
            for course in person.takes_course:
                assert isinstance(course, Course)

    assert any_person_takes_course, "No person takes_course relationships found"


def test_get_organization_heads(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    organizations = loader.world.organizations
    assert len(organizations) > 0
    any_heads = False
    for org in organizations:
        if org.head is not None:
            any_heads = True
            assert isinstance(org.head, Person)

    assert any_heads, "No organization heads found in the loaded data"


def test_get_programs(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    programs = loader.world.programs
    assert len(programs) > 0
    any_enrolled = False
    for program in programs:
        assert isinstance(program.identifier, str)

    for person in loader.world.persons:
        if len(person.enrolled_in) > 0:
            any_enrolled = True
            for program in person.enrolled_in:
                assert isinstance(program, Program)

    assert any_enrolled, "No person enrolled_in relationships found"
