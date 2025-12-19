from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass
class IdentifiedEntity:
    identifier: str


@dataclass
class CollegeDiscipline(IdentifiedEntity): ...


@dataclass
class Interest(IdentifiedEntity): ...


@dataclass
class Organization(IdentifiedEntity): ...


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
    age: int
    e_mail_address: str
    title: Optional[str]
