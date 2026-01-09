import pytest
from SPARQLWrapper import SPARQLWrapper, JSON

from owl2bench.loader import WorldLoader
from owl2bench.model.base import (
    Person,
    Organization,
    CollegeDiscipline,
    Course,
    Program,
    Interest,
)
from owl2bench.model.organizations import University, College, Department, ResearchGroup
from owl2bench.model.interests import Cricket

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
    any_specific_disciplines = False
    for college in colleges:
        if len(college.disciplines) > 0:
            any_disciplines = True
            for discipline in college.disciplines:
                assert isinstance(discipline, CollegeDiscipline)
                if type(discipline) is not CollegeDiscipline:
                    any_specific_disciplines = True

    assert any_disciplines, "No college disciplines found in the loaded data"
    # We expect some specific subclasses to be present in the loaded disciplines globally
    any_specific_disciplines_global = False
    for discipline in loader.world.college_disciplines:
        if type(discipline) is not CollegeDiscipline:
            any_specific_disciplines_global = True
            break
    assert (
        any_specific_disciplines_global
    ), "No specific college discipline subclasses found in the loaded data"


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


def test_get_person_hometown_relationships(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    persons = loader.world.persons
    assert len(persons) > 0
    any_hometown_relationships = False
    for person in persons:
        if len(person.has_same_hometown_as) > 0:
            any_hometown_relationships = True
            for other_person in person.has_same_hometown_as:
                assert isinstance(other_person, Person)

    assert (
        any_hometown_relationships
    ), "No person hometown relationships found in the loaded data"


def test_get_courses(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    courses = loader.world.courses
    assert len(courses) > 0
    any_person_takes_course = False
    any_teacher = False
    for course in courses:
        assert isinstance(course, Course)
        assert isinstance(course.identifier, str)
        assert isinstance(course.organization, Organization)
        assert isinstance(course.topic, CollegeDiscipline)
        assert isinstance(course.teachers, list)
        if len(course.teachers) > 0:
            any_teacher = True
            for teacher in course.teachers:
                assert isinstance(teacher, Person)

    assert any_teacher, "No Course.teachers relationships found in the loaded data"

    any_specific_topic = False
    for course in courses:
        if type(course.topic) is not CollegeDiscipline:
            any_specific_topic = True
            break
    assert any_specific_topic, "No Course.topic with a specific subclass found"

    for person in loader.world.persons:
        if len(person.takes_course) > 0:
            any_person_takes_course = True
            for course in person.takes_course:
                assert isinstance(course, Course)

    assert any_person_takes_course, "No person takes_course relationships found"

    any_organization_course = False
    for org in loader.world.organizations:
        if len(org.courses) > 0:
            any_organization_course = True
            for course in org.courses:
                assert isinstance(course, Course)
                assert course.organization == org
    assert any_organization_course, "No organization courses found in the loaded data"


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


def test_get_interests(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    interests = loader.world.interests
    assert len(interests) > 0
    any_hobbies = False
    for interest in interests:
        assert isinstance(interest, Interest)
        assert isinstance(interest.identifier, str)

    for person in loader.world.persons:
        if len(person.hobbies) > 0:
            any_hobbies = True
            for interest in person.hobbies:
                assert isinstance(interest, Interest)

    assert any_hobbies, "No person hobbies found in the loaded data"


def test_t20_cricket_interest_exists(sparql_wrapper):


    # We manually add a Cricket individual to the graph for this test
    # because the base ontology has Cricket as a class, and Cricket as an individual
    # of type Cricket.
    loader = WorldLoader(sparql_wrapper)

    # We use a mocked or intercepted graph if we wanted to be pure,
    # but here we just check if it IS there after parse.
    # The previous issue description said:
    # 'Why is the loader parsing the interest 'http://benchmark/OWL2Bench#T20Cricket' as Sports and not as Cricket?'
    # This implies Cricket should be a CLASS in the model that the individual http://benchmark/OWL2Bench#T20Cricket
    # is an instance of (or should be mapped to).

    loader.parse()
    interests = loader.world.interests

    # Find the specific interest by its identifier
    t20_interest = next(
        (
            i
            for i in interests
            if i.identifier == "http://benchmark/OWL2Bench#T20Cricket"
        ),
        None,
    )

    assert (
        t20_interest is not None
    ), "Interest http://benchmark/OWL2Bench#T20Cricket not found in loaded interests"
    assert isinstance(
        t20_interest, Cricket
    ), f"Interest Cricket should be an instance of Cricket class, but got {type(t20_interest)}"


def test_organizations_match_graphdb(sparql_wrapper):
    loader = WorldLoader(sparql_wrapper)
    loader.parse()
    loaded_organizations = loader.world.organizations

    # Get organizations from GraphDB directly
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl2bench: <http://benchmark/OWL2Bench#>
    SELECT DISTINCT ?x ?type WHERE {
        ?x rdf:type ?type .
        FILTER(?type IN (owl2bench:University, owl2bench:College, owl2bench:Department, owl2bench:ResearchGroup))
    }
    """
    sparql_wrapper.setQuery(query)
    results = sparql_wrapper.query().convert()
    bindings = results["results"]["bindings"]

    type_mapping = {
        "http://benchmark/OWL2Bench#University": University,
        "http://benchmark/OWL2Bench#College": College,
        "http://benchmark/OWL2Bench#Department": Department,
        "http://benchmark/OWL2Bench#ResearchGroup": ResearchGroup,
    }

    graphdb_orgs = {}
    for b in bindings:
        identifier = str(b["x"]["value"])
        org_type = b["type"]["value"]
        cls = type_mapping.get(org_type, Organization)
        graphdb_orgs[identifier] = cls

    assert len(loaded_organizations) == len(graphdb_orgs)

    for org in loaded_organizations:
        assert org.identifier in graphdb_orgs
        assert isinstance(org, graphdb_orgs[org.identifier])
