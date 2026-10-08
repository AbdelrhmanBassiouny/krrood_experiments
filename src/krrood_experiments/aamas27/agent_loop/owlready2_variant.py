"""
Variant 7, Owlready2 0.49 with Pellet: the knowledge is Owlready2's quadstore, which the program reads and writes
through Owlready2's Python objects, and inference is Pellet's, run through ``sync_reasoner_pellet``.

* Setup loads the raw data into an Owlready2 world and runs Pellet with ``infer_property_values=True``, which writes
  the inferred class memberships and property values back into the world, in an ontology of their own.
* Perceiving a fact is an assignment on Owlready2's objects (``enrollIn[person].append(department)``), which writes the
  asserted statement into the quadstore but infers nothing. To decide on the new facts, every step deletes the
  previous inferences and runs Pellet again on the asserted facts: Owlready2 exports the world to Pellet, a Java
  process, and writes its inferences back. Keeping the previous inferences would make Pellet re-read the whole closure,
  which takes about 19 minutes and a 22 GB heap (the loading benchmark's pre-reasoned input).
* The decisions use Owlready2's Python API (``world.search``), so the developer writes Python only; the IRIs of the
  answers are mapped to the application's rooms, and the robot's procedures run in Python on the candidates (once per
  distinct room), as in the GraphDB variant.

The application's rooms and mail boxes are kept in dictionaries by IRI rather than as attributes of Owlready2's
objects, because these objects are proxies that Owlready2 may discard and re-create from the quadstore.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Tuple

import owlready2
import owlready2.reasoning

from ..environment import UNREASONED_FILE
from .campus import Place
from .events import OWL2BENCH, T20_CRICKET, CourseTaking, CricketEnthusiasm, Enrollment, StepPerception
from .loop import AgentVariant
from .measurement import (
    MAPPING,
    PROCEDURE_INTEGRATION,
    SYNCHRONIZATION,
    StepMeter,
    boundary,
    function_body_source,
    query_size,
)
from .robot import HandoutCandidate, TicketCandidate, can_reach, travel_seconds

INFERRED_ONTOLOGY = "https://example.org/agent-loop/inferred-{}#"
"""
IRI of the ontology that holds the inferences of one Pellet run.
"""

JAVA_MEMORY_MB = 8000
"""
Java heap of Pellet (Owlready2's default, 2000 MB, also suffices for the raw data).
"""


@dataclass
class Owlready2Variant(AgentVariant):
    """
    The knowledge is Owlready2's quadstore, inferred by Pellet every step.
    """

    name: ClassVar[str] = "owlready2"
    description: ClassVar[str] = (
        "Owlready2 0.49 + Pellet: facts asserted on Owlready2's objects, previous inferences deleted and Pellet run "
        "again every step, candidates by world.search, the procedures run in Python on the candidates."
    )
    world: Any = field(default=None, init=False)
    """
    The Owlready2 world.
    """
    ontology: Any = field(default=None, init=False)
    """
    The loaded ontology, which receives the asserted facts.
    """
    inferred: Any = field(default=None, init=False)
    """
    The ontology of the last Pellet run's inferences.
    """
    pellet_runs: int = field(default=0, init=False)
    """
    Number of Pellet runs so far.
    """
    pellet_steps: List[Dict[str, float]] = field(default_factory=list, init=False)
    """
    Per step: the seconds of deleting the previous inferences and of Pellet's run, and the statements deleted and
    written back.
    """
    course_rooms: Dict[str, Place] = field(default_factory=dict, init=False)
    """
    Course IRI to its room (application data).
    """
    mailboxes: Dict[str, Place] = field(default_factory=dict, init=False)
    """
    Person IRI to the room of the mail box (application data).
    """

    def setup(self) -> Dict[str, Any]:
        owlready2.reasoning.JAVA_MEMORY = JAVA_MEMORY_MB
        start = time.perf_counter()
        self.world = owlready2.World()
        self.ontology = self.world.get_ontology(str(UNREASONED_FILE)).load()
        load_seconds = time.perf_counter() - start
        explicit_statements = len(self.world.graph)
        report = self._reason()
        start = time.perf_counter()
        self._application_data()
        application_seconds = time.perf_counter() - start
        seconds = {"load": load_seconds, "reasoning": report["pellet_seconds"], "application_data": application_seconds}
        return {
            "seconds": seconds,
            "total_seconds": sum(seconds.values()),
            "explicit_statements": explicit_statements,
            "statements_after_reasoning": len(self.world.graph),
            "java_memory_mb": JAVA_MEMORY_MB,
            "owlready2_version": owlready2.VERSION if hasattr(owlready2, "VERSION") else None,
        }

    @boundary(MAPPING)
    def _application_data(self) -> None:
        """
        Build the application's lookup from IRIs to its own objects (course rooms and mail boxes).
        """
        campus = self.scenario.campus
        self.course_rooms = {iri: campus.place(room) for iri, room in self.scenario.course_rooms.items()}
        self.mailboxes = {iri: campus.place(room) for iri, room in self.scenario.mailboxes.items()}

    def _reason(self) -> Dict[str, float]:
        """
        Delete the previous inferences and run Pellet on the asserted facts.

        :return: The seconds of both phases and the statements deleted and written back.
        """
        deleted = len(self.inferred.graph) if self.inferred is not None else 0
        start = time.perf_counter()
        self._delete_inferences()
        delete_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self._run_pellet()
        return {
            "delete_seconds": delete_seconds,
            "pellet_seconds": time.perf_counter() - start,
            "deleted": deleted,
            "written_back": len(self.inferred.graph),
        }

    @boundary(SYNCHRONIZATION)
    def _delete_inferences(self) -> None:
        """
        Delete the inferences of the previous Pellet run, so that Pellet reads only the asserted facts.
        """
        if self.inferred is not None:
            self.inferred.destroy()

    @boundary(SYNCHRONIZATION)
    def _run_pellet(self) -> None:
        """
        Run Pellet on the world; Owlready2 exports the world to Pellet and writes the inferences back into an ontology
        of their own.
        """
        self.inferred = self.world.get_ontology(INFERRED_ONTOLOGY.format(self.pellet_runs))
        self.pellet_runs += 1
        with self.inferred:
            owlready2.sync_reasoner_pellet(self.world, infer_property_values=True, debug=0)

    @boundary(MAPPING)
    def _individual(self, iri: str) -> Any:
        """
        :param iri: The IRI of an individual.
        :return: Owlready2's object of the individual.
        """
        return self.world[iri]

    @boundary(MAPPING)
    def _new_individual(self, iri: str, class_iri: str) -> Any:
        """
        :param iri: The IRI of a new individual.
        :param class_iri: The IRI of its class.
        :return: Owlready2's object of the new individual, in the loaded ontology.
        """
        namespace_iri, name = iri.rsplit("#", 1)
        namespace = self.ontology.get_namespace(namespace_iri + "#")
        return self.world[class_iri](name, namespace=namespace)

    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        for event in perception.knowledge_events:
            if isinstance(event, Enrollment):
                with meter.phase("mapping"):
                    department = self._individual(event.department)
                with meter.phase("update"):
                    person = self._new_individual(event.person, OWL2BENCH + "Person")
                    self.world[OWL2BENCH + "enrollIn"][person].append(department)
                meter.statements_inserted += 2
            elif isinstance(event, CourseTaking):
                with meter.phase("mapping"):
                    student = self._individual(event.student)
                    course = self._individual(event.course)
                with meter.phase("update"):
                    self.world[OWL2BENCH + "takesCourse"][student].append(course)
                meter.statements_inserted += 1
            elif isinstance(event, CricketEnthusiasm):
                with meter.phase("mapping"):
                    person = self._individual(event.person)
                    cricket = self._individual(T20_CRICKET)
                with meter.phase("update"):
                    self.world[OWL2BENCH + "isCrazyAbout"][person].append(cricket)
                meter.statements_inserted += 1
        with meter.phase("reasoning"):
            report = self._reason()
        self.pellet_steps.append(report)
        meter.reasoner_calls += 1
        meter.statements_inserted += report["written_back"]
        meter.statements_deleted += report["deleted"]

    def handout_pairs(self, college: Any) -> List[Tuple[Any, Any]]:
        """
        :param college: Owlready2's object of the requested college.
        :return: (student, course) pairs of the students who are members of the college.
        """
        students = self.world.search(type=self.world[OWL2BENCH + "Student"], isMemberOf=college)
        return [(student, course) for student in students for course in self.world[OWL2BENCH + "takesCourse"][student]]

    def fans(self) -> List[Any]:
        """
        :return: The T20 cricket fans.
        """
        return list(self.world.search(type=self.world[OWL2BENCH + "T20CricketFan"]))

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("mapping"):
            college_object = self._individual(college)
        with meter.phase("query"):
            pairs = self.handout_pairs(college_object)
        with meter.phase("mapping"):
            rows = self._handout_rows(pairs)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, _, room in rows})
            return [
                HandoutCandidate(student, course, room.identifier, reachable[room])
                for student, course, room in rows
                if room in reachable
            ]

    @boundary(MAPPING)
    def _handout_rows(self, pairs: List[Tuple[Any, Any]]) -> List[Tuple[str, str, Place]]:
        """
        :param pairs: (student, course) pairs of Owlready2's objects.
        :return: (student IRI, course IRI, course room) rows.
        """
        return [(student.iri, course.iri, self.course_rooms[course.iri]) for student, course in pairs]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("query"):
            fans = self.fans()
        with meter.phase("mapping"):
            rows = self._ticket_rows(fans)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, room in rows})
            return [TicketCandidate(person, room.identifier, reachable[room]) for person, room in rows if room in reachable]

    @boundary(MAPPING)
    def _ticket_rows(self, fans: List[Any]) -> List[Tuple[str, Place]]:
        """
        :param fans: Owlready2's objects of the fans.
        :return: (person IRI, mail box room) rows.
        """
        default = self.scenario.campus.place(self.scenario.default_mailbox)
        return [(person.iri, self.mailboxes.get(person.iri, default)) for person in fans]

    @boundary(PROCEDURE_INTEGRATION)
    def _reachable_driving_times(self, rooms: set) -> Dict[Place, float]:
        """
        :param rooms: Rooms.
        :return: The driving time to every room the robot can reach.
        """
        return {room: travel_seconds(self.robot, room) for room in rooms if can_reach(self.robot, room)}

    def final_measurements(self) -> Dict[str, Any]:
        """
        :return: Per step, the seconds of deleting the previous inferences and of Pellet's run, and the statements
         deleted and written back.
        """
        return {"pellet_steps": self.pellet_steps, "statements": len(self.world.graph)}

    def close(self) -> None:
        if self.world is not None:
            self.world.close()

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "handouts": query_size(function_body_source(cls.handout_pairs), "python"),
            "tickets": query_size(function_body_source(cls.fans), "python"),
        }
