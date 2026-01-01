from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import Organization, CollegeDiscipline

if TYPE_CHECKING:
    from .base import Person, Course


@dataclass
class College(Organization):
    disciplines: list[CollegeDiscipline] = field(default_factory=list)


@dataclass
class Department(Organization):
    courses: list[Course] = field(default_factory=list)


@dataclass
class ResearchGroup(Organization): ...


@dataclass
class University(Organization):
    alumni: list[Person] = field(default_factory=list)
