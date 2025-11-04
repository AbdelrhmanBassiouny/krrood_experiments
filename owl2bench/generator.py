from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence
import random

from .config import InstanceConfig, Range
from .models import University, College, Department, Course, Person, Student


@dataclass(frozen=True)
class RandomSource:
    """
    Deterministic random source.

    :param seed: Seed for deterministic generation
    """
    seed: int

    def rng(self) -> random.Random:
        return random.Random(self.seed)


class InstanceGenerator:
    """
    Generates a lightweight object graph similar to the Java InstanceGenerator.

    Instances include universities, colleges, departments, courses, and students.
    """

    def __init__(self, config: InstanceConfig, seed: int = 1) -> None:
        self.config = config
        self.random = RandomSource(seed).rng()
        self.first_names: Sequence[str] = self._default_first_names()
        self.last_names: Sequence[str] = self._default_last_names()
        self.department_names: Sequence[str] = self._default_departments()
        self.course_titles: Sequence[str] = self._default_courses()

    def generate(self, universities: int) -> List[University]:
        """
        Builds a list of universities and their nested instances.

        :param universities: Number of universities to generate
        :returns: List of `University` instances
        """
        result: List[University] = []
        for u_index in range(1, universities + 1):
            u_id = f"U{u_index}"
            uni = University(identifier=u_id, name=f"University {u_index}")
            colleges = self._gen_colleges(u_id)
            object.__setattr__(uni, "colleges", colleges)
            result.append(uni)
        return result

    # Internal helpers

    def _rand_in_range(self, r: Range) -> int:
        return self.random.randint(r.minimum, r.maximum)

    def _gen_colleges(self, u_id: str) -> List[College]:
        colleges: List[College] = []
        count = self._rand_in_range(self.config.colleges)
        for c_index in range(1, count + 1):
            c_id = f"{u_id}_C{c_index}"
            is_women_only = self.random.random() < self.config.women_college_ratio
            college = College(identifier=c_id, name=f"College {c_index}", is_women_only=is_women_only)
            departments = self._gen_departments(college)
            object.__setattr__(college, "departments", departments)
            colleges.append(college)
        return colleges

    def _gen_departments(self, college: College) -> List[Department]:
        departments: List[Department] = []
        count = self._rand_in_range(self.config.departments)
        for d_index in range(1, count + 1):
            d_id = f"{college.identifier}_D{d_index}"
            name = self.department_names[(d_index - 1) % len(self.department_names)]
            dept = Department(identifier=d_id, name=name)
            courses = self._gen_courses(dept)
            ug = self._gen_students(dept, level="ug", count=self._rand_in_range(self.config.undergraduate_students), women_only=college.is_women_only)
            pg = self._gen_students(dept, level="pg", count=self._rand_in_range(self.config.postgraduate_students), women_only=college.is_women_only)
            phd = self._gen_students(dept, level="phd", count=self._rand_in_range(self.config.phd_students), women_only=college.is_women_only)
            object.__setattr__(dept, "courses", courses)
            object.__setattr__(dept, "undergraduate_students", ug)
            object.__setattr__(dept, "postgraduate_students", pg)
            object.__setattr__(dept, "phd_students", phd)
            departments.append(dept)
        return departments

    def _gen_courses(self, department: Department) -> List[Course]:
        courses: List[Course] = []
        count = self._rand_in_range(self.config.courses)
        for i in range(1, count + 1):
            title = self.course_titles[(i - 1) % len(self.course_titles)]
            c_id = f"{department.identifier}_CRS{i}"
            courses.append(Course(identifier=c_id, title=title))
        return courses

    def _gen_students(self, department: Department, level: str, count: int, women_only: bool) -> List[Person]:
        people: List[Person] = []
        for i in range(1, count + 1):
            pid = f"{department.identifier}_{level.upper()}{i}"
            first = self.random.choice(self.first_names)
            last = self.random.choice(self.last_names)
            is_woman = women_only or (self.random.randint(0, 1) == 0)
            email = f"{pid.lower()}@bench.com"
            person = Person(identifier=pid, first_name=first, last_name=last, email=email, is_woman=is_woman)
            people.append(person)
        return people

    @staticmethod
    def _default_first_names() -> Sequence[str]:
        return (
            "Alex", "Jamie", "Taylor", "Jordan", "Casey", "Riley", "Morgan", "Avery",
            "Quinn", "Cameron", "Drew", "Hayden",
        )

    @staticmethod
    def _default_last_names() -> Sequence[str]:
        return (
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia",
            "Rodriguez", "Wilson", "Martinez", "Anderson",
        )

    @staticmethod
    def _default_departments() -> Sequence[str]:
        return (
            "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Psychology",
        )

    @staticmethod
    def _default_courses() -> Sequence[str]:
        return (
            "Intro", "Advanced Topics", "Seminar", "Laboratory", "Workshop", "Capstone",
        )
