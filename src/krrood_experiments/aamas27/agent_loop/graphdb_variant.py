"""
Variant 2, Python objects + GraphDB: the application keeps its own objects (robot, campus map, course rooms and mail
boxes by IRI) and mirrors every perceived fact into GraphDB 11.2 (ruleset ``owl2-rl-optimized``) with one SPARQL
``INSERT DATA`` per step; GraphDB materialises the consequences incrementally inside the update. A SPARQL query returns
the IRIs that satisfy the logical part of a decision, the IRIs are mapped back to application objects, and the robot's
procedures, which SPARQL cannot call, are evaluated in Python on the candidates (once per distinct room).
"""

from __future__ import annotations

import json
import time
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from ..graphdb import DEFAULT_GRAPHDB_URL
from ..environment import UNREASONED_FILE
from .campus import Place
from .events import StepPerception
from .loop import AgentVariant
from .measurement import MAPPING, PROCEDURE_INTEGRATION, StepMeter, boundary, query_size
from .rdf_mirror import GraphDBSession, Triple, delete_data, event_triples, insert_data, object_term
from .robot import HandoutCandidate, TicketCandidate, can_reach, travel_seconds

REPOSITORY = "aamas27_agent_loop"
"""
The GraphDB repository of the agent loop (re-created by every GraphDB variant at setup, deleted at the end).
"""

RULESET = "owl2-rl-optimized"
"""
The GraphDB ruleset.
"""

PREFIXES = """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl2bench: <http://benchmark/OWL2Bench#>
"""

HANDOUT_QUERY = (
    PREFIXES
    + """\
SELECT ?student ?course WHERE {
  ?student a owl2bench:Student ;
           owl2bench:isMemberOf ?college ;
           owl2bench:takesCourse ?course .
}"""
)
"""
The students who are members of ``?college`` (bound per request) and the courses they take.
"""

TICKET_QUERY = (
    PREFIXES
    + """\
SELECT ?person WHERE {
  ?person a owl2bench:T20CricketFan .
}"""
)
"""
The T20 cricket fans.
"""


@dataclass
class GraphDBMirror(AgentVariant, ABC):
    """
    What both GraphDB variants share: the repository, the application's lookup from IRIs to its objects, mirroring
    the perceived facts, and sending requests.
    """

    graphdb_url: str = DEFAULT_GRAPHDB_URL
    """
    Base URL of the GraphDB server.
    """
    state_file: Optional[Path] = None
    """
    A JSON file that records the state of the repository right after loading. If given, the repository is kept after
    the run, the statements the variant wrote are deleted again, and the next GraphDB variant reuses the repository
    when its statement counts equal the recorded ones (loading the raw data takes about 20 minutes). Without it, the
    repository is re-created and deleted at the end.
    """
    client: GraphDBSession = field(default=None, init=False)
    """
    The GraphDB client.
    """
    course_rooms: Dict[str, Place] = field(default_factory=dict, init=False)
    """
    Course IRI to its room (application data).
    """
    mailboxes: Dict[str, Place] = field(default_factory=dict, init=False)
    """
    Person IRI to the room of the mail box (application data).
    """
    written: List[Triple] = field(default_factory=list, init=False)
    """
    The explicit statements this variant wrote, deleted again at the end when the repository is kept.
    """

    def setup(self) -> Dict[str, Any]:
        self.client = GraphDBSession(self.graphdb_url)
        baseline = self._reusable_baseline()
        reused = baseline is not None
        if not reused:
            baseline = self._create_and_load()
        start = time.perf_counter()
        self._application_data()
        seconds = {
            "create_repository": baseline["create_repository_seconds"],
            "load_and_reasoning": baseline["load_and_reasoning_seconds"],
            "application_data": time.perf_counter() - start,
        }
        seconds.update(self._extra_setup())
        return {
            "seconds": seconds,
            "total_seconds": sum(seconds.values()),
            "repository_reused": reused,
            "statements_after_loading": baseline["statements"],
            "statements": self.client.count_statements(REPOSITORY),
            "graphdb_version": self.client.version(),
            "graphdb_license": self.client.license(),
            "graphdb_java_options": self.client.server_java_options(),
        }

    def _create_and_load(self) -> Dict[str, Any]:
        """
        Re-create the repository and load the raw data (GraphDB materialises the closure during the load).

        :return: The baseline record: wall times and statement counts right after loading.
        """
        if REPOSITORY in self.client.repository_ids():
            self.client.delete_repository(REPOSITORY)
        start = time.perf_counter()
        self.client.create_repository(REPOSITORY, RULESET)
        create_seconds = time.perf_counter() - start
        load_seconds = self.client.load_file(REPOSITORY, UNREASONED_FILE)
        baseline = {
            "create_repository_seconds": create_seconds,
            "load_and_reasoning_seconds": load_seconds,
            "statements": self.client.count_statements(REPOSITORY),
            "loaded_by": self.name,
        }
        if self.state_file is not None:
            self.state_file.write_text(json.dumps(baseline, indent=1))
        return baseline

    def _reusable_baseline(self) -> Optional[Dict[str, Any]]:
        """
        :return: The baseline record if the repository is in the state right after loading, otherwise None.
        """
        if self.state_file is None or not self.state_file.exists():
            return None
        if REPOSITORY not in self.client.repository_ids():
            return None
        baseline = json.loads(self.state_file.read_text())
        if self.client.count_statements(REPOSITORY) != baseline["statements"]:
            return None
        return baseline

    def _extra_setup(self) -> Dict[str, float]:
        """
        :return: Wall times of setup phases of subclasses.
        """
        return {}

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
            triples = [triple for event in perception.knowledge_events for triple in event_triples(event)]
            update = insert_data(triples)
        with meter.phase("update"):
            self._send(update, meter)
        meter.statements_inserted += len(triples)
        self.written.extend(triples)

    def _send(self, update: str, meter: StepMeter) -> None:
        """
        :param update: A SPARQL update to execute.
        :param meter: The step meter.
        """
        self.client.update(REPOSITORY, update)
        meter.round_trips += 1

    def _select(self, query: str, meter: StepMeter, **bindings: str) -> List[Dict[str, str]]:
        """
        :param query: A SPARQL SELECT query.
        :param meter: The step meter.
        :param bindings: Variable name to IRI.
        :return: The solutions.
        """
        meter.round_trips += 1
        return self.client.select_bindings(REPOSITORY, query, bindings)

    def final_measurements(self) -> Dict[str, Any]:
        """
        :return: The statement counts after the last step and, when the repository is kept, the result of deleting
         the statements this variant wrote.
        """
        measurements: Dict[str, Any] = {"statements": self.client.count_statements(REPOSITORY)}
        if self.state_file is not None:
            measurements["restore"] = self._restore()
        return measurements

    def _restore(self) -> Dict[str, Any]:
        """
        Delete the explicit statements this variant wrote, and check that the statement counts are those right after
        loading.

        :return: The wall time of the deletion and whether the repository is back in its loaded state.
        """
        start = time.perf_counter()
        self.client.update(REPOSITORY, self._restore_update())
        seconds = time.perf_counter() - start
        statements = self.client.count_statements(REPOSITORY)
        baseline = json.loads(self.state_file.read_text())
        return {"seconds": seconds, "statements": statements, "clean": statements == baseline["statements"]}

    def _restore_update(self) -> str:
        """
        :return: The SPARQL update that deletes what this variant wrote.
        """
        return delete_data(self.written)

    def close(self) -> None:
        if self.client is not None and self.state_file is None and REPOSITORY in self.client.repository_ids():
            self.client.delete_repository(REPOSITORY)


@dataclass
class GraphDBVariant(GraphDBMirror):
    """
    The knowledge is mirrored into GraphDB; the procedures run in Python on the candidates of a SPARQL query.
    """

    name: ClassVar[str] = "graphdb"
    description: ClassVar[str] = (
        "Python objects + GraphDB 11.2 (owl2-rl-optimized): facts mirrored with SPARQL INSERT DATA, SPARQL returns "
        "candidate IRIs, mapped back to objects, the procedures run in Python on the candidates."
    )
    boundary_helpers: ClassVar[Tuple] = (event_triples, insert_data, object_term)

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("query"):
            solutions = self._select(HANDOUT_QUERY, meter, college=college)
        with meter.phase("mapping"):
            rows = self._handout_rows(solutions)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, _, room in rows})
            return [
                HandoutCandidate(student, course, room.identifier, reachable[room])
                for student, course, room in rows
                if room in reachable
            ]

    @boundary(MAPPING)
    def _handout_rows(self, solutions: List[Dict[str, str]]) -> List[Tuple[str, str, Place]]:
        """
        :param solutions: The solutions of :data:`HANDOUT_QUERY`.
        :return: (student IRI, course IRI, course room) rows.
        """
        return [(s["student"], s["course"], self.course_rooms[s["course"]]) for s in solutions]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("query"):
            solutions = self._select(TICKET_QUERY, meter)
        with meter.phase("mapping"):
            rows = self._ticket_rows(solutions)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, room in rows})
            return [TicketCandidate(person, room.identifier, reachable[room]) for person, room in rows if room in reachable]

    @boundary(MAPPING)
    def _ticket_rows(self, solutions: List[Dict[str, str]]) -> List[Tuple[str, Place]]:
        """
        :param solutions: The solutions of :data:`TICKET_QUERY`.
        :return: (person IRI, mail box room) rows.
        """
        default = self.scenario.campus.place(self.scenario.default_mailbox)
        return [(s["person"], self.mailboxes.get(s["person"], default)) for s in solutions]

    @boundary(PROCEDURE_INTEGRATION)
    def _reachable_driving_times(self, rooms: set) -> Dict[Place, float]:
        """
        :param rooms: Rooms.
        :return: The driving time to every room the robot can reach.
        """
        return {room: travel_seconds(self.robot, room) for room in rooms if can_reach(self.robot, room)}

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "handouts": query_size(HANDOUT_QUERY, "sparql"),
            "tickets": query_size(TICKET_QUERY, "sparql"),
        }
