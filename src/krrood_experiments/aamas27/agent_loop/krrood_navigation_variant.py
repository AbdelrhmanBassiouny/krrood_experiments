"""
Variant 1b, KRROOD with navigation: like :mod:`~krrood_experiments.aamas27.agent_loop.krrood_variant`, but the handout
query starts from the requested college object, as an object-oriented developer would write it, instead of scanning
all students and testing their membership.

The college's ``has_student`` attribute is the inverse of ``isStudentOf`` and a sub-property of ``has_member``; it is
maintained by the descriptors (``enrollIn o isSubOrganizationOf`` implies ``isStudentOf``). Since ``isPartOf`` and
``isSubOrganizationOf`` are equivalent properties in OWL2Bench, the students of a college are exactly the students
that are members of it (``enrollIn o isPartOf``), so the query asks the same question as the scan form. ``has_member``
itself holds the ``Person`` objects, which do not have ``takes_course`` (it belongs to the ``Student`` role).

The ticket query is unchanged: no object leads to the fans (``T20Cricket`` has no inverse of ``isCrazyAbout``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from krrood.entity_query_language.entity import set_of, variable, variable_from
from krrood.entity_query_language.entity_result_processors import an

from ...owl2bench.ontomatic import owl2bench_with_predicates as model
from .krrood_variant import CanReach, KrroodVariant, travel_time


@dataclass
class KrroodNavigationVariant(KrroodVariant):
    """
    The handout query navigates from the college to its students.
    """

    name: ClassVar[str] = "krrood_navigation"
    description: ClassVar[str] = (
        "KRROOD as in krrood, but the handout query starts from the requested college (its has_student values) "
        "instead of scanning all students."
    )

    def handout_query(self, college: model.Organization):
        """
        :param college: The requested college.
        :return: The students of the college, the courses they take whose room the robot can reach, and the driving
         times.
        """
        student = variable(model.Student, domain=college.has_student)
        course = variable_from(student.takes_course)
        driving_time = travel_time(self.robot, course.taught_in)
        query = an(set_of(student, course, driving_time).where(CanReach(self.robot, course.taught_in)))
        return query, student, course, driving_time

