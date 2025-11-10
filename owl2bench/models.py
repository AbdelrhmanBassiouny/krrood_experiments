from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from krrood.entity_query_language.predicate import Symbol


@dataclass
class Course(Symbol):
    """Represents a course with a generated identifier and title."""

    identifier: str
    title: str


@dataclass
class Publication(Symbol):
    """Represents a publication affiliated with a university."""

    identifier: str
    title: str
    year: int
    authors: List["Person"] = field(default_factory=list)


@dataclass
class Person(Symbol):
    """Represents a person and their basic attributes."""

    identifier: str
    first_name: str
    last_name: str
    email: str
    is_woman: bool
    hometown: Optional[str] = None
    knows: List["Person"] = field(default_factory=list)
    likes: List["Person"] = field(default_factory=list)
    loves: List["Person"] = field(default_factory=list)
    dislikes: List["Person"] = field(default_factory=list)
    is_crazy_about: List["Person"] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Returns the full name for display purposes."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class Student(Symbol):
    """Represents a student with a study level and advisory links."""

    person: Person
    level: str  # one of: "ug", "pg", "phd"
    advisors: List[Person] = field(default_factory=list)

    # Convenience read-only projections to keep interfaces easy to use
    @property
    def identifier(self) -> str:
        return self.person.identifier

    @property
    def first_name(self) -> str:
        return self.person.first_name

    @property
    def last_name(self) -> str:
        return self.person.last_name

    @property
    def email(self) -> str:
        return self.person.email

    @property
    def is_woman(self) -> bool:
        return self.person.is_woman

    @property
    def full_name(self) -> str:
        return self.person.full_name


@dataclass
class Employee(Symbol):
    """Represents an employee with a role and optional rank."""

    person: Person
    role: str  # faculty, staff, postdoc, lecturer, etc.
    rank: Optional[str] = None  # assistant/associate/full/visiting, or staff type


@dataclass
class Program(Symbol):
    """Represents a degree program offered by a department."""

    identifier: str
    name: str


@dataclass
class ResearchGroup(Symbol):
    """Represents a research group with members and publications."""

    identifier: str
    name: str
    members: List[Person] = field(default_factory=list)
    publications: List[Publication] = field(default_factory=list)


@dataclass
class Department(Symbol):
    """Represents an academic department."""

    identifier: str
    name: str
    courses: List[Course] = field(default_factory=list)
    programs: List[Program] = field(default_factory=list)
    undergraduate_students: List[Student] = field(default_factory=list)
    postgraduate_students: List[Student] = field(default_factory=list)
    phd_students: List[Student] = field(default_factory=list)
    employees: List[Employee] = field(default_factory=list)
    research_groups: List[ResearchGroup] = field(default_factory=list)


@dataclass
class College(Symbol):
    """Represents a college that can be women-only or co-educational."""

    identifier: str
    name: str
    is_women_only: bool
    departments: List[Department] = field(default_factory=list)


@dataclass
class University(Symbol):
    """Represents a university that aggregates colleges and publications."""

    identifier: str
    name: str
    colleges: List[College] = field(default_factory=list)
    publications: List[Publication] = field(default_factory=list)


@dataclass
class World(Symbol):
    """Aggregates all generated entities for easy cross-linking and queries."""

    universities: List[University] = field(default_factory=list)
    colleges: List[College] = field(default_factory=list)
    departments: List[Department] = field(default_factory=list)
    programs: List[Program] = field(default_factory=list)
    courses: List[Course] = field(default_factory=list)
    persons: List[Person] = field(default_factory=list)
    students: List[Student] = field(default_factory=list)
    employees: List[Employee] = field(default_factory=list)
    research_groups: List[ResearchGroup] = field(default_factory=list)
    publications: List[Publication] = field(default_factory=list)
