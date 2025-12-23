from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import Organization

if TYPE_CHECKING:
    from .base import Person


@dataclass
class College(Organization): ...


@dataclass
class Department(Organization): ...


@dataclass
class ResearchGroup(Organization): ...


@dataclass
class University(Organization):
    alumni: list[Person] = field(default_factory=list)
