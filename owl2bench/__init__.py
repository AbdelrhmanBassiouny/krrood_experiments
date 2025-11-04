"""Lightweight Python instance generator inspired by OWL2Bench Java Generator.

Public API:
- InstanceConfig, Range
- InstanceGenerator
- Models: University, College, Department, Program, Course, Publication,
  Person, Student, Employee, ResearchGroup, World
"""

from .config import InstanceConfig, Range
from .generator import InstanceGenerator
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
