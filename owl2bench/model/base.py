from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass
class World:
    persons: List[Person] = field(default_factory=list)
    organizations: List[Organization] = field(default_factory=list)
    college_disciplines: List[CollegeDiscipline] = field(default_factory=list)
    courses: List[Course] = field(default_factory=list)
    programs: List[Program] = field(default_factory=list)
    interests: List[Interest] = field(default_factory=list)


@dataclass
class IdentifiedEntity:
    identifier: str


@dataclass
class CollegeDiscipline(IdentifiedEntity): ...


@dataclass
class Interest(IdentifiedEntity): ...


@dataclass
class Organization(IdentifiedEntity):
    head: Optional[Person] = None
    members: List[Person] = field(default_factory=list)
    is_part_of: List[Organization] = field(default_factory=list)
    affiliated_organizations: List[Organization] = field(default_factory=list)


@dataclass
class Program(IdentifiedEntity): ...


@dataclass
class Work(IdentifiedEntity):
    organization: Organization


@dataclass
class Course(Work):
    topic: CollegeDiscipline
    teachers: List[Person] = field(default_factory=list)


@dataclass
class ResearchProject(Work): ...


@dataclass
class Publication(IdentifiedEntity):
    authors: List[Person] = field(default_factory=list)


@dataclass
class Person(IdentifiedEntity):
    first_name: str
    last_name: str
    gender: Optional[str] = field(repr=False)
    telephone_number: str = field(repr=False)
    age: Optional[str] = field(repr=False)
    e_mail_address: str = field(repr=False)
    title: Optional[str] = field(repr=False)
    knows: List[Person] = field(default_factory=list)
    collaborates_with: List[Person] = field(default_factory=list)
    is_advised_by: List[Person] = field(default_factory=list)
    takes_course: List[Course] = field(default_factory=list)
    enrolled_in: List[Program] = field(default_factory=list)
    hobbies: List[Interest] = field(default_factory=list)
    has_same_hometown_as: List[Person] = field(default_factory=list)
