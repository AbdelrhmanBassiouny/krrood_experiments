from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass(eq=False)
class World:
    persons: List[Person] = field(default_factory=list)
    organizations: List[Organization] = field(default_factory=list)
    college_disciplines: List[CollegeDiscipline] = field(default_factory=list)
    courses: List[Course] = field(default_factory=list)
    programs: List[Program] = field(default_factory=list)
    interests: List[Interest] = field(default_factory=list)


@dataclass(eq=False)
class IdentifiedEntity:
    identifier: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IdentifiedEntity):
            return NotImplemented
        return self.identifier == other.identifier

    def __hash__(self) -> int:
        return hash(self.identifier)


@dataclass(eq=False)
class CollegeDiscipline(IdentifiedEntity): ...


@dataclass(eq=False)
class Interest(IdentifiedEntity): ...


@dataclass(eq=False)
class Organization(IdentifiedEntity):
    name: Optional[str] = None
    head: Optional[Person] = None
    members: List[Person] = field(default_factory=list, repr=False)
    is_part_of: List[Organization] = field(default_factory=list, repr=False)
    affiliated_organizations: List[Organization] = field(
        default_factory=list, repr=False
    )
    courses: List[Course] = field(default_factory=list, repr=False)


@dataclass(eq=False)
class Program(IdentifiedEntity): ...


@dataclass(eq=False)
class Work(IdentifiedEntity):
    organization: Organization = field(repr=False)


@dataclass(eq=False)
class Course(Work):
    topic: CollegeDiscipline
    teachers: List[Person] = field(default_factory=list, repr=False)


@dataclass(eq=False)
class ResearchProject(Work): ...


@dataclass(eq=False)
class Publication(IdentifiedEntity):
    authors: List[Person] = field(default_factory=list, repr=False)


@dataclass(eq=False)
class Person(IdentifiedEntity):
    first_name: str
    last_name: str
    gender: Optional[str] = field(repr=False)
    telephone_number: str = field(repr=False)
    age: Optional[str] = field(repr=False)
    e_mail_address: str = field(repr=False)
    title: Optional[str] = field(repr=False)
    knows: List[Person] = field(default_factory=list, repr=False)
    collaborates_with: List[Person] = field(default_factory=list, repr=False)
    is_advised_by: List[Person] = field(default_factory=list, repr=False)
    takes_course: List[Course] = field(default_factory=list, repr=False)
    enrolled_in: List[Program] = field(default_factory=list, repr=False)
    hobbies: List[Interest] = field(default_factory=list, repr=False)
    has_same_hometown_as: List[Person] = field(default_factory=list, repr=False)
