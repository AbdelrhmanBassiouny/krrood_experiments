"""
Variant 3, GraphDB "push": like :mod:`~krrood_experiments.aamas27.agent_loop.graphdb_variant`, but the application also
writes the results of its procedures into GraphDB, so that one SPARQL query per decision does the whole selection,
including reachability and the ordering by driving time.

* At setup it writes the application data (``agent:taughtIn`` for every course, ``agent:mailbox`` for every person).
* Every step it writes the perceived facts (plus the mail box of a new person) and then, in a second request,
  replaces the procedure results: ``DELETE WHERE { ?room agent:travelSeconds ?seconds }`` followed by
  ``INSERT DATA`` of the driving time to every room the robot can reach now (an unreachable room has none). Since the
  pose changes with every move, nearly every value changes every step; the push has to cover every room a decision
  might need, because the store cannot ask for a value when it needs it.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Tuple

from .campus import Place
from .events import Enrollment, StepPerception
from .graphdb_variant import PREFIXES, REPOSITORY, GraphDBMirror
from .measurement import MAPPING, SYNCHRONIZATION, StepMeter, boundary, query_size
from .rdf_mirror import (
    AGENT_LOOP,
    Triple,
    event_triples,
    insert_data,
    object_term,
    place_identifier,
    place_iri,
)
from .robot import HandoutCandidate, TicketCandidate, can_reach, travel_seconds

AGENT_PREFIX = f"PREFIX agent: <{AGENT_LOOP}>\n"

PUSH_HANDOUT_QUERY = (
    PREFIXES
    + AGENT_PREFIX
    + """\
SELECT ?student ?course ?room ?seconds WHERE {
  ?student a owl2bench:Student ;
           owl2bench:isMemberOf ?college ;
           owl2bench:takesCourse ?course .
  ?course agent:taughtIn ?room .
  ?room agent:travelSeconds ?seconds .
}
ORDER BY ?seconds ?course ?student"""
)
"""
The students who are members of ``?college`` (bound per request), the courses they take whose room the robot can reach,
and the driving times, nearest first.
"""

PUSH_TICKET_QUERY = (
    PREFIXES
    + AGENT_PREFIX
    + """\
SELECT ?person ?room ?seconds WHERE {
  ?person a owl2bench:T20CricketFan ;
          agent:mailbox ?room .
  ?room agent:travelSeconds ?seconds .
}
ORDER BY ?seconds ?person"""
)
"""
The T20 cricket fans whose mail box the robot can reach, and the driving times, nearest first.
"""

DELETE_PROCEDURE_RESULTS = AGENT_PREFIX + "DELETE WHERE { ?room agent:travelSeconds ?seconds }"
"""
Removes the procedure results of the previous step.
"""

DOUBLE = "http://www.w3.org/2001/XMLSchema#double"


@dataclass
class GraphDBPushVariant(GraphDBMirror):
    """
    The procedure results are written into GraphDB every step, and one SPARQL query decides.
    """

    name: ClassVar[str] = "graphdb_push"
    description: ClassVar[str] = (
        "GraphDB with pushed procedure results: every step the driving time to every reachable room is written into "
        "GraphDB (after deleting the previous values), and one SPARQL query per decision selects and orders."
    )
    boundary_helpers: ClassVar[Tuple] = (event_triples, insert_data, object_term, place_iri, place_identifier)
    target_rooms: List[Place] = field(default_factory=list, init=False)
    """
    The rooms a decision may need a driving time for (course rooms and mail boxes).
    """
    pushed_statements: int = field(default=0, init=False)
    """
    Number of procedure results currently in the store.
    """

    def _extra_setup(self) -> Dict[str, float]:
        start = time.perf_counter()
        application_triples = self._application_triples()
        self.client.update(REPOSITORY, insert_data(application_triples))
        self.written.extend(application_triples)
        rooms = set(self.course_rooms.values()) | set(self.mailboxes.values())
        self.target_rooms = sorted(rooms, key=lambda room: room.identifier)
        return {"application_data_push": time.perf_counter() - start}

    @boundary(SYNCHRONIZATION)
    def _application_triples(self) -> List[Triple]:
        """
        :return: The course rooms and the mail boxes of the people that exist at the start.
        """
        new_people = {
            event.person
            for perception in self.scenario.perceptions
            for event in perception.knowledge_events
            if isinstance(event, Enrollment)
        }
        triples = [(iri, AGENT_LOOP + "taughtIn", place_iri(room.identifier)) for iri, room in self.course_rooms.items()]
        triples += [
            (iri, AGENT_LOOP + "mailbox", place_iri(room.identifier))
            for iri, room in self.mailboxes.items()
            if iri not in new_people
        ]
        return triples

    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        with meter.phase("mapping"):
            triples = self._knowledge_triples(perception)
            update = insert_data(triples)
        with meter.phase("update"):
            self._send(update, meter)
        meter.statements_inserted += len(triples)
        self.written.extend(triples)
        with meter.phase("push"):
            values = self._procedure_results()
            self._send(DELETE_PROCEDURE_RESULTS + " ;\n" + insert_data(values), meter)
        meter.statements_deleted += self.pushed_statements
        meter.statements_inserted += len(values)
        self.pushed_statements = len(values)

    @boundary(SYNCHRONIZATION)
    def _knowledge_triples(self, perception: StepPerception) -> List[Triple]:
        """
        :param perception: The perception of a step.
        :return: The statements of the perceived facts and the mail boxes of new people.
        """
        triples = [triple for event in perception.knowledge_events for triple in event_triples(event)]
        triples += [
            (event.person, AGENT_LOOP + "mailbox", place_iri(self.mailboxes[event.person].identifier))
            for event in perception.knowledge_events
            if isinstance(event, Enrollment)
        ]
        return triples

    @boundary(SYNCHRONIZATION)
    def _procedure_results(self) -> List[Triple]:
        """
        :return: The driving time to every target room the robot can reach now.
        """
        return [
            (place_iri(room.identifier), AGENT_LOOP + "travelSeconds", f'"{travel_seconds(self.robot, room)!r}"^^<{DOUBLE}>')
            for room in self.target_rooms
            if can_reach(self.robot, room)
        ]

    def _restore_update(self) -> str:
        return DELETE_PROCEDURE_RESULTS + " ;\n" + super()._restore_update()

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("query"):
            solutions = self._select(PUSH_HANDOUT_QUERY, meter, college=college)
        with meter.phase("mapping"):
            return self._handout_records(solutions)

    @boundary(MAPPING)
    def _handout_records(self, solutions: List[Dict[str, str]]) -> List[HandoutCandidate]:
        """
        :param solutions: The solutions of :data:`PUSH_HANDOUT_QUERY`.
        :return: The handout candidates.
        """
        return [
            HandoutCandidate(s["student"], s["course"], place_identifier(s["room"]), float(s["seconds"]))
            for s in solutions
        ]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("query"):
            solutions = self._select(PUSH_TICKET_QUERY, meter)
        with meter.phase("mapping"):
            return self._ticket_records(solutions)

    @boundary(MAPPING)
    def _ticket_records(self, solutions: List[Dict[str, str]]) -> List[TicketCandidate]:
        """
        :param solutions: The solutions of :data:`PUSH_TICKET_QUERY`.
        :return: The ticket candidates.
        """
        return [TicketCandidate(s["person"], place_identifier(s["room"]), float(s["seconds"])) for s in solutions]

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "handouts": query_size(PUSH_HANDOUT_QUERY, "sparql"),
            "tickets": query_size(PUSH_TICKET_QUERY, "sparql"),
            "push_delete": query_size(DELETE_PROCEDURE_RESULTS, "sparql"),
        }
