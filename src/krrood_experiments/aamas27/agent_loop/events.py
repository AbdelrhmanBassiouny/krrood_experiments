"""
The perceptions of the agent loop. Knowledge events only add facts: removals are deliberately excluded, because KRROOD
does not retract facts it inferred from a removed fact (its property descriptors forward-chain on assignment only).

Every event names individuals by IRI, so that exactly the same input reaches every variant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Union

OWL2BENCH = "http://benchmark/OWL2Bench#"
"""
Namespace of the OWL2Bench ontology and data.
"""

T20_CRICKET = OWL2BENCH + "T20Cricket"
"""
The individual that defines the class ``T20CricketFan`` (``T20CricketFan == isCrazyAbout value T20Cricket``).
"""


class EventKind(str, Enum):
    """
    The kinds of knowledge events.
    """

    ENROLLMENT = "enrollment"
    COURSE_TAKING = "course_taking"
    CRICKET_ENTHUSIASM = "cricket_enthusiasm"


@dataclass(frozen=True)
class Enrollment:
    """
    A new person enrolls in a department (``person a Person ; enrollIn department``). OWL2Bench then implies that the
    person is a student (domain of ``enrollIn``), a student of the department, its college and the university (property
    chain ``enrollIn o isSubOrganizationOf``) and a member of them (chain ``enrollIn o isPartOf`` with the transitive
    ``isPartOf``).
    """

    person: str
    """
    IRI of the new person.
    """
    department: str
    """
    IRI of the department.
    """
    kind: EventKind = field(default=EventKind.ENROLLMENT, init=False)


@dataclass(frozen=True)
class CourseTaking:
    """
    A student takes a course (``student takesCourse course``).
    """

    student: str
    """
    IRI of the student.
    """
    course: str
    """
    IRI of the course.
    """
    kind: EventKind = field(default=EventKind.COURSE_TAKING, init=False)


@dataclass(frozen=True)
class CricketEnthusiasm:
    """
    A person becomes crazy about T20 cricket (``person isCrazyAbout T20Cricket``), which makes the person a
    ``T20CricketFan`` (a ``hasValue`` class definition) and implies ``loves`` and ``likes`` (sub-properties).
    """

    person: str
    """
    IRI of the person.
    """
    kind: EventKind = field(default=EventKind.CRICKET_ENTHUSIASM, init=False)


KnowledgeEvent = Union[Enrollment, CourseTaking, CricketEnthusiasm]
"""
Any knowledge event.
"""


@dataclass(frozen=True)
class StepPerception:
    """
    What the agent perceives at the start of one step besides its own pose and battery, which it reads from its state.
    """

    step: int
    """
    The step number, starting at 0.
    """
    knowledge_events: List[KnowledgeEvent]
    """
    The facts added in this step.
    """
    requested_college: str
    """
    IRI of the college whose course handouts the robot is asked to deliver in this step.
    """

    def to_json(self) -> Dict[str, Any]:
        """
        :return: A JSON-serialisable representation.
        """
        return {
            "step": self.step,
            "requested_college": self.requested_college,
            "knowledge_events": [event_to_json(event) for event in self.knowledge_events],
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> StepPerception:
        """
        :param data: The output of :meth:`to_json`.
        :return: The perception.
        """
        return cls(
            step=data["step"],
            requested_college=data["requested_college"],
            knowledge_events=[event_from_json(event) for event in data["knowledge_events"]],
        )


def event_to_json(event: KnowledgeEvent) -> Dict[str, Any]:
    """
    :param event: A knowledge event.
    :return: A JSON-serialisable representation.
    """
    if isinstance(event, Enrollment):
        return {"kind": event.kind.value, "person": event.person, "department": event.department}
    if isinstance(event, CourseTaking):
        return {"kind": event.kind.value, "student": event.student, "course": event.course}
    return {"kind": event.kind.value, "person": event.person}


def event_from_json(data: Dict[str, Any]) -> KnowledgeEvent:
    """
    :param data: The output of :func:`event_to_json`.
    :return: The knowledge event.
    """
    kind = EventKind(data["kind"])
    if kind is EventKind.ENROLLMENT:
        return Enrollment(data["person"], data["department"])
    if kind is EventKind.COURSE_TAKING:
        return CourseTaking(data["student"], data["course"])
    return CricketEnthusiasm(data["person"])
