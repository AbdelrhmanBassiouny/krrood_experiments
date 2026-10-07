"""
Variant 4, Python objects + the in-memory OWL 2 RL reasoner ``reasonable`` (0.4.4, ``PyReasoner``).

* Setup parses the raw data with RDFLib, hands it to the reasoner and materialises the closure (a full
  materialisation; this is also what re-materialising from scratch after every step would cost).
* Every step the perceived facts are added with ``from_graph`` and ``reason()`` is called. ``reasonable`` 0.4.4
  materialises additions incrementally, but ``reason()`` always returns the whole closure as a list of RDFLib triples,
  so the step cost includes building that list.
* The candidates are found by one pass over the returned triples (the logical part), then mapped to application
  objects, and the robot's procedures are evaluated in Python on them (once per distinct room).

``reasonable`` 0.4.4 does not implement the property-chain rule (``prp-spo2``), so it does not infer ``isMemberOf``
of a college (``enrollIn o isPartOf``); the handout decision therefore differs. This is recorded, not repaired.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

import rdflib
from rdflib import RDF, URIRef

from ..environment import UNREASONED_FILE
from .campus import Place
from .events import OWL2BENCH, StepPerception
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
from .rdf_mirror import event_triples
from .robot import HandoutCandidate, TicketCandidate, can_reach, travel_seconds

STUDENT = URIRef(OWL2BENCH + "Student")
T20_CRICKET_FAN = URIRef(OWL2BENCH + "T20CricketFan")
IS_MEMBER_OF = URIRef(OWL2BENCH + "isMemberOf")
TAKES_COURSE = URIRef(OWL2BENCH + "takesCourse")


@dataclass
class ClosureIndex:
    """
    What the two decisions need from the materialised closure, collected in one pass over its triples.
    """

    students: Set[URIRef] = field(default_factory=set)
    """
    Individuals of type ``Student``.
    """
    fans: Set[URIRef] = field(default_factory=set)
    """
    Individuals of type ``T20CricketFan``.
    """
    members: Dict[URIRef, Set[URIRef]] = field(default_factory=lambda: defaultdict(set))
    """
    Organization to the individuals that are members of it.
    """
    courses: Dict[URIRef, List[URIRef]] = field(default_factory=lambda: defaultdict(list))
    """
    Student to the courses taken.
    """

    @classmethod
    def of(cls, triples: List[Tuple[URIRef, URIRef, Any]]) -> ClosureIndex:
        """
        :param triples: The materialised closure.
        :return: The index.
        """
        index = cls()
        for subject, predicate, value in triples:
            if predicate == RDF.type:
                if value == STUDENT:
                    index.students.add(subject)
                elif value == T20_CRICKET_FAN:
                    index.fans.add(subject)
            elif predicate == IS_MEMBER_OF:
                index.members[value].add(subject)
            elif predicate == TAKES_COURSE:
                index.courses[subject].append(value)
        return index

    def handout_pairs(self, college: str) -> List[Tuple[URIRef, URIRef]]:
        """
        :param college: IRI of a college.
        :return: (student, course) pairs of the students who are members of the college.
        """
        members = self.members.get(URIRef(college), set()) & self.students
        return [(student, course) for student in members for course in self.courses.get(student, ())]


@dataclass
class ReasonableVariant(AgentVariant):
    """
    The knowledge is mirrored into an in-memory reasoner whose closure is filtered for the candidates.
    """

    name: ClassVar[str] = "reasonable"
    description: ClassVar[str] = (
        "Python objects + reasonable 0.4.4 (in-memory OWL 2 RL): facts added with from_graph, reason() every step, "
        "candidates by filtering the returned closure, the procedures run in Python on the candidates."
    )
    boundary_helpers: ClassVar[Tuple] = (event_triples,)
    reasoner: Any = field(default=None, init=False)
    """
    The ``reasonable.PyReasoner``.
    """
    closure: List[Tuple] = field(default_factory=list, init=False)
    """
    The triples returned by the last ``reason()`` call.
    """
    index: Optional[ClosureIndex] = field(default=None, init=False)
    """
    The index of the current closure, built on the first query of a step.
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
        import reasonable

        start = time.perf_counter()
        graph = rdflib.Graph()
        graph.parse(str(UNREASONED_FILE), format="xml")
        parse_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self.reasoner = reasonable.PyReasoner()
        self.reasoner.from_graph(graph)
        load_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self.closure = self.reasoner.reason()
        reasoning_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self._application_data()
        application_seconds = time.perf_counter() - start
        seconds = {
            "parse": parse_seconds,
            "load": load_seconds,
            "reasoning": reasoning_seconds,
            "application_data": application_seconds,
        }
        return {
            "seconds": seconds,
            "total_seconds": sum(seconds.values()),
            "explicit_statements": len(graph),
            "closure_statements": len(self.closure),
            "full_materialisation_seconds": reasoning_seconds,
            "reasonable_version": getattr(reasonable, "__version__", None),
        }

    @boundary(MAPPING)
    def _application_data(self) -> None:
        """
        Build the application's lookup from IRIs to its own objects (course rooms and mail boxes).
        """
        campus = self.scenario.campus
        self.course_rooms = {iri: campus.place(room) for iri, room in self.scenario.course_rooms.items()}
        self.mailboxes = {iri: campus.place(room) for iri, room in self.scenario.mailboxes.items()}

    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        with meter.phase("mapping"):
            triples = self._rdf_triples(perception)
        with meter.phase("update"):
            self.reasoner.from_graph(triples)
        with meter.phase("reasoning"):
            # Release the previous closure first, so that two closures (about 1.5 million triples each) are never
            # held at once.
            self.closure, self.index = [], None
            self.closure = self.reasoner.reason()
        meter.reasoner_calls += 2
        meter.statements_inserted += len(triples)

    @boundary(SYNCHRONIZATION)
    def _rdf_triples(self, perception: StepPerception) -> List[Tuple[URIRef, URIRef, URIRef]]:
        """
        :param perception: The perception of a step.
        :return: The RDFLib statements of the perceived facts.
        """
        return [
            (URIRef(subject), URIRef(predicate), URIRef(value))
            for event in perception.knowledge_events
            for subject, predicate, value in event_triples(event)
        ]

    def _closure_index(self) -> ClosureIndex:
        """
        :return: The index of the current closure.
        """
        if self.index is None:
            self.index = ClosureIndex.of(self.closure)
        return self.index

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("query"):
            pairs = self._closure_index().handout_pairs(college)
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
    def _handout_rows(self, pairs: List[Tuple[URIRef, URIRef]]) -> List[Tuple[str, str, Place]]:
        """
        :param pairs: (student, course) pairs of the closure.
        :return: (student IRI, course IRI, course room) rows.
        """
        return [(str(student), str(course), self.course_rooms[str(course)]) for student, course in pairs]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("query"):
            fans = list(self._closure_index().fans)
        with meter.phase("mapping"):
            rows = self._ticket_rows(fans)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, room in rows})
            return [TicketCandidate(person, room.identifier, reachable[room]) for person, room in rows if room in reachable]

    @boundary(MAPPING)
    def _ticket_rows(self, fans: List[URIRef]) -> List[Tuple[str, Place]]:
        """
        :param fans: The fans in the closure.
        :return: (person IRI, mail box room) rows.
        """
        default = self.scenario.campus.place(self.scenario.default_mailbox)
        return [(str(person), self.mailboxes.get(str(person), default)) for person in fans]

    @boundary(PROCEDURE_INTEGRATION)
    def _reachable_driving_times(self, rooms: set) -> Dict[Place, float]:
        """
        :param rooms: Rooms.
        :return: The driving time to every room the robot can reach.
        """
        return {room: travel_seconds(self.robot, room) for room in rooms if can_reach(self.robot, room)}

    def final_measurements(self) -> Dict[str, Any]:
        """
        :return: The wall time of materialising the final base triples from scratch (``reason_full``), which is what
         every step would cost without incremental materialisation.
        """
        self.closure, self.index = [], None
        start = time.perf_counter()
        closure = self.reasoner.reason_full()
        return {"full_rematerialisation_seconds": time.perf_counter() - start, "closure_statements": len(closure)}

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "closure_index": query_size(function_body_source(ClosureIndex.of.__func__, drop_last=True), "python"),
            "handouts": query_size(function_body_source(ClosureIndex.handout_pairs), "python"),
            "tickets": query_size("fans = list(self._closure_index().fans)", "python"),
        }
