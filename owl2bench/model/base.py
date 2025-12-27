from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass
class World:
    persons: List[Person] = field(default_factory=list)
    organizations: List[Organization] = field(default_factory=list)
    college_disciplines: List[CollegeDiscipline] = field(default_factory=list)


@dataclass
class IdentifiedEntity:
    identifier: str


@dataclass
class CollegeDiscipline(IdentifiedEntity): ...


@dataclass
class Interest(IdentifiedEntity): ...


@dataclass
class Organization(IdentifiedEntity):
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


@dataclass
class ResearchProject(Work): ...


@dataclass
class Publication(IdentifiedEntity):
    authors: List[Person] = field(default_factory=list)


@dataclass
class Person(IdentifiedEntity):
    first_name: str
    last_name: str
    telephone_number: str
    age: Optional[str]
    e_mail_address: str
    title: Optional[str]
    knows: List[Person] = field(default_factory=list)
