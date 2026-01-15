from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import Organization, CollegeDiscipline

if TYPE_CHECKING:
    from .base import Person, Course


@dataclass(eq=False)
class College(Organization):
    disciplines: list[CollegeDiscipline] = field(default_factory=list)


@dataclass(eq=False)
class Department(Organization): ...


@dataclass(eq=False)
class ResearchGroup(Organization): ...


@dataclass(eq=False)
class University(Organization):
    alumni: list[Person] = field(default_factory=list)
