"""Lightweight Python instance generator inspired by OWL2Bench Java Generator.

Public API:
- InstanceConfig, Range
- InstanceGenerator
- Loader: WorldLoader, OntologyLoadError, MappingError
- Models: University, College, Department, Program, Course, Publication,
  Person, Student, Employee, ResearchGroup, World
"""

from .config import InstanceConfig, Range
from .generator import InstanceGenerator
from .loader import WorldLoader, OntologyLoadError, MappingError
from .verifier import WorldVerifier, RelationshipError
from .models import (
    University,
    College,
    Department,
    Program,
    Course,
    Publication,
    Person,
    Student,
    Employee,
    ResearchGroup,
    World,
)

__all__ = [
    "InstanceConfig",
    "Range",
    "InstanceGenerator",
    "WorldLoader",
    "OntologyLoadError",
    "MappingError",
    "WorldVerifier",
    "RelationshipError",
    "University",
    "College",
    "Department",
    "Program",
    "Course",
    "Publication",
    "Person",
    "Student",
    "Employee",
    "ResearchGroup",
    "World",
]
