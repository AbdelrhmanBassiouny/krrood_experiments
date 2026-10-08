"""
The part of the OWL2Bench model that the 18 OWL 2 RL queries of the KRROOD experiments use, in the syntax of the
current KRROOD version, whose ORMatic translates EQL to SQL (paper, Section 6). It is the model of the paper's
ORMatic listing (supplement listings/ormatic/owl2bench_like.py) with ``has_age`` a string, as the benchmark's ages
are (the value ``"x"``); run_ormatic_translation.py fills it with the OWL 2 RL closure of the benchmark.

It contains exactly the classes and attributes that the 18 OWL2Bench OWL 2 RL queries of
the KRROOD experiments touch.  Class and attribute names follow the Ontomatic-generated
model (``owl2bench_with_predicates.py``); roles are used where the generated model uses
roles (Student, Employee/Faculty, LeisureStudent, T20CricketFan).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing_extensions import Optional, Set

from krrood.patterns.role import Role
from krrood.symbol_graph.symbol_graph import Symbol


@dataclass(eq=False)
class Thing(Symbol):
    """OWL2BenchThing: every individual carries its URI."""

    uri: str
    has_same_home_town_with: Set[Thing] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class Interest(Thing): ...


@dataclass(eq=False)
class CollegeDiscipline(Thing): ...


@dataclass(eq=False)
class Course(Thing): ...


@dataclass(eq=False)
class Organization(Thing):
    has_dean: Set[Faculty] = field(default_factory=set, kw_only=True)
    has_head: Set[Person] = field(default_factory=set, kw_only=True)
    is_affiliated_organization_of: Set[Organization] = field(
        default_factory=set, kw_only=True
    )
    is_part_of: Set[Organization] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class University(Organization):
    has_alumnus: Set[Person] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class College(Organization):
    has_college_discipline: Set[CollegeDiscipline] = field(
        default_factory=set, kw_only=True
    )


@dataclass(eq=False)
class WomanCollege(College): ...


@dataclass(eq=False)
class Person(Thing):
    has_age: Optional[str] = field(default=None, kw_only=True)  # the benchmark's ages are the string "x"
    has_collaboration_with: Set[Person] = field(default_factory=set, kw_only=True)
    is_advised_by: Set[Faculty] = field(default_factory=set, kw_only=True)
    is_crazy_about: Set[Interest] = field(default_factory=set, kw_only=True)
    is_head_of: Set[Organization] = field(default_factory=set, kw_only=True)
    is_member_of: Set[Organization] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class Man(Person): ...


@dataclass(eq=False)
class Woman(Person): ...


@dataclass(eq=False)
class Student(Role[Person]):
    is_student_of: Set[Organization] = field(default_factory=set, kw_only=True)
    takes_course: Set[Course] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class LeisureStudent(Role[Student]): ...


@dataclass(eq=False)
class Employee(Role[Person]): ...


@dataclass(eq=False)
class Faculty(Employee):
    teaches_course: Set[Course] = field(default_factory=set, kw_only=True)


@dataclass(eq=False)
class T20CricketFan(Role[Person]): ...
