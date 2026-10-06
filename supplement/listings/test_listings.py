"""Executable versions of the EQL listings of the AAMAS paper, run on the current KRROOD
(branch fix/eql-to-sql-collections of the CRAM fork, which merges fix/eql-correlated-quantifiers)."""
from __future__ import annotations

from dataclasses import dataclass, field

from krrood.entity_query_language.factories import (
    a, an, the, entity, set_of, variable, flat_variable, contains, not_, for_all, exists, count,
)
from krrood.patterns.role import Role
from krrood.symbol_graph.symbol_graph import Symbol
import pytest


# ---------------------------------------------------------------- running example (KR listing)
@dataclass(eq=False)
class Interest(Symbol):
    name: str


@dataclass(eq=False)
class Course(Symbol):
    name: str


@dataclass(eq=False)
class Person(Symbol):
    name: str
    is_crazy_about: set[Interest] = field(default_factory=set)
    teaches_course: set[Course] = field(default_factory=set)


@dataclass(eq=False)
class Student(Role[Person]):
    takes_course: set[Course] = field(default_factory=set)


@dataclass(eq=False)
class Organization(Symbol):
    name: str
    has_dean: set[Person] = field(default_factory=set)


T20_CRICKET = Interest("T20Cricket")


@dataclass(eq=False)
class SportsFan(Role[Person]):
    pass


@dataclass(eq=False)
class T20CricketFan(SportsFan):
    @classmethod
    def axiom(cls, p):  # T20CricketFan == exists isCrazyAbout.{T20Cricket}
        return contains(p.is_crazy_about, T20_CRICKET)


# ---------------------------------------------------------------- data
logic, ai, dbs = Course("Logic"), Course("AI"), Course("Databases")
dean = Person("Dean", teaches_course={logic})
prof = Person("Prof", teaches_course={ai})
alice, bob, carol = Person("Alice", is_crazy_about={T20_CRICKET}), Person("Bob"), Person("Carol")
s_alice = Student(role_taker=alice, takes_course={logic, ai})
s_bob = Student(role_taker=bob, takes_course={ai})
s_carol = Student(role_taker=carol, takes_course={logic, dbs})
cs = Organization("CS", has_dean={dean})
people = [dean, prof, alice, bob, carol]
students = [s_alice, s_bob, s_carol]
organizations = [cs]


def names(rows):
    return sorted(rows)


# ---------------------------------------------------------------- tests
def test_role_delegates_to_taker():
    assert s_alice.name == "Alice"
    assert s_alice is not alice


def test_q22_core_form():
    s = variable(Student, domain=students)
    o = variable(Organization, domain=organizations)
    c = flat_variable(flat_variable(o.has_dean).teaches_course)
    q22 = an(set_of(s, c).where(contains(s.takes_course, c)))
    got = sorted((r[s].name, r[c].name) for r in q22.evaluate())
    assert got == [("Alice", "Logic"), ("Carol", "Logic")]


def test_axiom_as_query_condition():
    p = variable(Person, domain=people)
    fans = an(entity(p).where(T20CricketFan.axiom(p)))
    assert [x.name for x in fans.evaluate()] == ["Alice"]


def test_negation_as_failure():
    p = variable(Person, domain=people)
    q = an(entity(p).where(not_(contains(p.is_crazy_about, T20_CRICKET))))
    assert sorted(x.name for x in q.evaluate()) == ["Bob", "Carol", "Dean", "Prof"]


def test_the_uniqueness():
    o = variable(Organization, domain=organizations)
    assert the(entity(o).where(o.name == "CS")).first() is cs


def test_match_form_scalar():
    q = an(Organization)(name="CS").from_(organizations)
    assert [x.name for x in q.evaluate()] == ["CS"]


def test_universal_quantifier():
    s = variable(Student, domain=students)
    c = flat_variable(s.takes_course)
    q = an(entity(s).where(for_all(c, c.name != "Databases")))
    assert sorted(x.name for x in q.evaluate()) == ["Alice", "Bob"]


# ---------------------------------------------------------------- Q21-style nested match, Q22 variant, rule
@dataclass(eq=False)
class College(Symbol):
    name: str
    discipline: str


@dataclass(eq=False)
class Department(Symbol):
    name: str
    is_part_of: College


@dataclass(eq=False)
class Enrolment(Symbol):
    student: Student
    department: Department


eng, arts = College("TU", "Engineering"), College("FA", "FineArts")
d_cs, d_paint = Department("CS", eng), Department("Painting", arts)
enrolments = [Enrolment(s_alice, d_cs), Enrolment(s_bob, d_paint), Enrolment(s_carol, d_cs)]


def test_q22_named_dean():
    s = variable(Student, domain=students)
    o = variable(Organization, domain=organizations)
    dean = flat_variable(o.has_dean)
    c = flat_variable(dean.teaches_course)
    q22 = an(set_of(s, c).where(contains(s.takes_course, c)))
    got = sorted((r[s].name, r[c].name) for r in q22.evaluate())
    assert got == [("Alice", "Logic"), ("Carol", "Logic")]


def test_nested_match():
    q = an(Enrolment)(department=an(Department)(is_part_of=an(College)(discipline="Engineering"))).from_(enrolments)
    assert sorted(e.student.name for e in q.evaluate()) == ["Alice", "Carol"]


def test_rule_derives_roles():
    from krrood.entity_query_language.factories import inference
    p = variable(Person, domain=people)
    fan = inference(T20CricketFan)(role_taker=p)
    derived = list(an(entity(fan).where(T20CricketFan.axiom(p))).evaluate())
    assert [f.role_taker.name for f in derived] == ["Alice"]
    assert isinstance(derived[0], T20CricketFan) and derived[0].name == "Alice"


def test_match_on_set_valued_attribute():
    q = an(Student)(takes_course=an(Course)(name="Databases")).from_(students)
    assert [x.name for x in q.evaluate()] == ["Carol"]


def test_negated_correlated_exists():
    s = variable(Student, domain=students)
    c = flat_variable(s.takes_course)
    q = an(entity(s).where(not_(exists(c, c.name == "Logic"))))
    assert [x.name for x in q.evaluate()] == ["Bob"]


# ---------------------------------------------------------------- exact paper forms (no explicit domain -> symbol graph)
def test_paper_q22_listing():
    s = variable(Student, domain=students)
    o = variable(Organization)
    dean = flat_variable(o.has_dean)
    c = flat_variable(dean.teaches_course)
    q22 = an(set_of(s, c).where(contains(s.takes_course, c)))
    got = sorted((r[s].name, r[c].name) for r in q22.evaluate())
    assert got == [("Alice", "Logic"), ("Carol", "Logic")]


def test_paper_the_pattern_without_domain():
    assert the(Organization)(name="CS").first() is cs


def test_paper_axiom_rule_listing_without_domain():
    from krrood.entity_query_language.factories import inference
    p = variable(Person)
    fan = inference(T20CricketFan)(role_taker=p)
    fans = an(entity(fan).where(T20CricketFan.axiom(p)))
    assert [f.role_taker.name for f in fans.evaluate()] == ["Alice"]


# ---------------------------------------------------------------- agent loop listing (perceive -> decide)
from krrood.entity_query_language.predicate import symbolic_function


@dataclass(eq=False)
class TimedCourse(Symbol):
    name: str
    slot: str


@symbolic_function
def clashes(course, courses):
    return any(course.slot == other.slot for other in courses)


def test_agent_loop_listing():
    algebra, robotics, ethics, logic2 = (TimedCourse("Algebra", "Mon9"), TimedCourse("Robotics", "Tue9"),
                                         TimedCourse("Ethics", "Mon9"), TimedCourse("Logic", "Wed9"))
    offered = [algebra, robotics, ethics, logic2]
    alice_courses = set()
    # perceive: the agent observes an enrolment
    alice_courses.add(algebra)
    # decide: suggest courses that fit the timetable
    c = variable(TimedCourse, domain=offered)
    suggestions = an(entity(c).where(
        not_(contains(alice_courses, c)),
        not_(clashes(c, alice_courses))))
    assert sorted(x.name for x in suggestions.evaluate()) == ["Logic", "Robotics"]


def test_agent_loop_listing_exact_paper_form():
    algebra, robotics, ethics, logic2 = (TimedCourse("Algebra", "Mon9"), TimedCourse("Robotics", "Tue9"),
                                         TimedCourse("Ethics", "Mon9"), TimedCourse("Logic", "Wed9"))
    offered = [algebra, robotics, ethics, logic2]
    alice = Student(role_taker=Person("Alice"))
    # --- paper listing ---
    alice.takes_course.add(algebra)  # perceive
    c = variable(TimedCourse, domain=offered)  # decide
    suggestions = an(entity(c).where(
        not_(contains(alice.takes_course, c)),
        not_(clashes(c, alice.takes_course))))
    assert sorted(x.name for x in suggestions.evaluate()) == ["Logic", "Robotics"]


# ---------------------------------------------------------------- KR listing (lst:kr): descriptors and sub-properties
def _kr_listing_classes():
    """The classes of lst:kr, with the attributes that the paper's sub-property example needs."""
    from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
    from krrood.symbol_graph.symbol_graph import SymbolGraph

    @dataclass(eq=False)
    class KRPerson(Symbol):
        likes: set[Interest] = field(default_factory=set)
        loves: set[Interest] = field(default_factory=set)
        is_crazy_about: set[Interest] = field(default_factory=set)

    @dataclass(eq=False)
    class Likes(PropertyDescriptor): ...

    # --- paper listing ---
    class Loves(Likes): ...
    class IsCrazyAbout(Loves): ...  # sub-property

    # IsCrazyAbout manages Person.is_crazy_about
    KRPerson.is_crazy_about = IsCrazyAbout(KRPerson, "is_crazy_about")
    # --- end of paper listing ---
    KRPerson.likes = Likes(KRPerson, "likes")
    KRPerson.loves = Loves(KRPerson, "loves")
    SymbolGraph().clear()
    SymbolGraph()
    return KRPerson


def test_paper_kr_listing_sub_property_rules_fire_on_assignment():
    """Section 3: adding T20 cricket to p.is_crazy_about also adds it to p.loves and p.likes."""
    KRPerson = _kr_listing_classes()
    p = KRPerson()
    p.is_crazy_about.add(T20_CRICKET)
    assert T20_CRICKET in p.loves
    assert T20_CRICKET in p.likes


from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor as _PropertyDescriptor
from krrood.ontomatic.property_descriptor.mixins import TransitiveProperty as _TransitiveProperty


@dataclass(eq=False)
class KROrganization(Symbol):
    name: str
    is_part_of: set[KROrganization] = field(default_factory=set)


# --- paper listing (lst:kr) ---
class IsPartOf(_PropertyDescriptor, _TransitiveProperty): ...
# --- end of paper listing ---


def test_paper_kr_listing_transitive_descriptor():
    """lst:kr: a transitive property descriptor (OWL2Bench isPartOf) chains its facts on assignment."""
    from krrood.symbol_graph.symbol_graph import SymbolGraph

    KROrganization.is_part_of = IsPartOf(KROrganization, "is_part_of")
    SymbolGraph().clear()
    SymbolGraph()
    university, college, department = (KROrganization("University"), KROrganization("College"),
                                        KROrganization("Department"))
    college.is_part_of.add(university)
    department.is_part_of.add(college)
    assert university in department.is_part_of
