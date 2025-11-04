from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from .models import World, University, College, Department, Course, Person


class RelationshipError(Exception):
    """
    Raised when the object graph violates structural or referential invariants.
    """


@dataclass(frozen=True)
class WorldVerifier:
    """
    Verifies referential integrity and basic invariants across a ``World``.

    Raises ``RelationshipError`` if any violation is found.
    """

    def verify(self, world: World) -> None:
        problems: List[str] = []

        # 1) Uniqueness per type
        problems += self._check_unique([u.identifier for u in world.universities], "University")
        problems += self._check_unique([c.identifier for c in world.colleges], "College")
        problems += self._check_unique([d.identifier for d in world.departments], "Department")
        problems += self._check_unique([c.identifier for c in world.courses], "Course")
        problems += self._check_unique([p.identifier for p in world.persons], "Person")

        # 2) Non-empty display fields
        for u in world.universities:
            if not u.name:
                problems.append(f"University {u.identifier} has empty name")
        for c in world.colleges:
            if not c.name:
                problems.append(f"College {c.identifier} has empty name")
        for d in world.departments:
            if not d.name:
                problems.append(f"Department {d.identifier} has empty name")
        for crs in world.courses:
            if not crs.title:
                problems.append(f"Course {crs.identifier} has empty title")
        for p in world.persons:
            if not p.first_name or not p.last_name or not p.email:
                problems.append(f"Person {p.identifier} has missing required fields")
            if not isinstance(p.is_woman, bool):
                problems.append(f"Person {p.identifier} has non-boolean is_woman")

        # 3) Build parent maps from containment
        college_parent: Dict[str, University] = {}
        department_parent: Dict[str, College] = {}
        course_parent: Dict[str, Department] = {}

        # Universities → Colleges
        for u in world.universities:
            seen: Set[str] = set()
            for c in u.colleges:
                if c.identifier in seen:
                    problems.append(f"Duplicate college {c.identifier} under university {u.identifier}")
                seen.add(c.identifier)
                if c.identifier in college_parent:
                    problems.append(
                        f"College {c.identifier} appears under multiple universities: "
                        f"{college_parent[c.identifier].identifier} and {u.identifier}"
                    )
                else:
                    college_parent[c.identifier] = u

        # Colleges → Departments
        for c in world.colleges:
            seen: Set[str] = set()
            for d in c.departments:
                if d.identifier in seen:
                    problems.append(f"Duplicate department {d.identifier} under college {c.identifier}")
                seen.add(d.identifier)
                if d.identifier in department_parent:
                    problems.append(
                        f"Department {d.identifier} appears under multiple colleges: "
                        f"{department_parent[d.identifier].identifier} and {c.identifier}"
                    )
                else:
                    department_parent[d.identifier] = c

        # Departments → Courses
        for d in world.departments:
            seen: Set[str] = set()
            for crs in d.courses:
                if crs.identifier in seen:
                    problems.append(f"Duplicate course {crs.identifier} under department {d.identifier}")
                seen.add(crs.identifier)
                if crs.identifier in course_parent:
                    problems.append(
                        f"Course {crs.identifier} appears under multiple departments: "
                        f"{course_parent[crs.identifier].identifier} and {d.identifier}"
                    )
                else:
                    course_parent[crs.identifier] = d

        # 4) Cross-collection presence
        def idset(xs):
            return {x.identifier for x in xs}

        world_colleges = idset(world.colleges)
        world_depts = idset(world.departments)
        world_courses = idset(world.courses)
        for u in world.universities:
            for c in u.colleges:
                if c.identifier not in world_colleges:
                    problems.append(
                        f"College {c.identifier} under university {u.identifier} is not in world.colleges"
                    )
        for c in world.colleges:
            for d in c.departments:
                if d.identifier not in world_depts:
                    problems.append(
                        f"Department {d.identifier} under college {c.identifier} is not in world.departments"
                    )
        for d in world.departments:
            for crs in d.courses:
                if crs.identifier not in world_courses:
                    problems.append(
                        f"Course {crs.identifier} under department {d.identifier} is not in world.courses"
                    )

        # 5) Person relationship sanity
        person_ids = idset(world.persons)

        def check_person_list(owner: Person, rel_name: str, lst: Iterable[Person]) -> None:
            for other in lst:
                if other.identifier not in person_ids:
                    problems.append(
                        f"Person {owner.identifier} has {rel_name} that is not in world.persons: {other.identifier}"
                    )
                if other.identifier == owner.identifier:
                    problems.append(f"Person {owner.identifier} has self in {rel_name}")

        for p in world.persons:
            check_person_list(p, "knows", p.knows)
            check_person_list(p, "likes", p.likes)
            check_person_list(p, "loves", p.loves)
            check_person_list(p, "dislikes", p.dislikes)
            check_person_list(p, "is_crazy_about", p.is_crazy_about)

        if problems:
            raise RelationshipError("\n".join(problems))

    @staticmethod
    def _check_unique(ids: List[str], kind: str) -> List[str]:
        seen: Set[str] = set()
        dupes: List[str] = []
        for x in ids:
            if x in seen:
                dupes.append(f"Duplicate {kind} identifier: {x}")
            else:
                seen.add(x)
        return dupes
