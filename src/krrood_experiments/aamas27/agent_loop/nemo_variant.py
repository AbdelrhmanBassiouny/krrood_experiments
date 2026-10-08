"""
Variant 5, Python objects + the rule engine Nemo (0.10.1) with the OWL 2 RL/RDF rules ``owl2rl.rls``.

Nemo materialises a program in one batch run of its command-line tool and has no incremental mode, so every step:

* the perceived facts are appended to an N-Triples file that holds all facts perceived so far (synchronisation);
* Nemo runs the OWL 2 RL rules on the raw data plus that file, together with two decision rules that select the
  candidates of the step's requested college and the T20 cricket fans, and exports only those two predicates as CSV;
* the exported IRIs are mapped to application objects, and the robot's procedures, which Nemo's rules cannot call,
  are evaluated in Python on the candidates (once per distinct room).

Restarting from the previous step's closure instead of the raw data was slower (319 s against 6 s for one university
and one new fact, Nemo treats every input fact as new), so every step starts from the raw data.
"""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple

from ..environment import UNREASONED_FILE
from ..loading_worker import NEMO_REPORT_LINE, NEMO_RULES
from .campus import Place
from .events import StepPerception
from .loop import AgentVariant
from .measurement import (
    MAPPING,
    PROCEDURE_INTEGRATION,
    SYNCHRONIZATION,
    StepMeter,
    boundary,
    distribution,
    query_size,
)
from .rdf_mirror import event_triples, object_term
from .robot import HandoutCandidate, TicketCandidate, can_reach, travel_seconds

DECISION_RULES = """\
handout(?student, ?course) :- rdf_type(?student, owl2bench:Student),
    triple(?student, owl2bench:isMemberOf, $college), triple(?student, owl2bench:takesCourse, ?course) .
fan(?person) :- rdf_type(?person, owl2bench:T20CricketFan) .
"""
"""
The two decisions as Nemo rules over the closure ``triple/3`` and its view ``rdf_type/2`` of ``owl2rl.rls``; the
requested college is the parameter ``$college``.
"""

PROGRAM_HEADER = """\
@parameter $input = "input.rdf" .
@parameter $perceived = "perceived.nt" .
@parameter $college = <http://benchmark/OWL2Bench#College> .
@import raw :- rdf{resource = $input} .
@import perceived :- ntriples{resource = $perceived} .
input(?s, ?p, ?o) :- raw(?s, ?p, ?o) .
input(?s, ?p, ?o) :- perceived(?s, ?p, ?o) .
"""
"""
Replaces the import and export declarations of ``owl2rl.rls``: the raw data and the perceived facts are both input.
"""

PROGRAM_FOOTER = """\
@prefix owl2bench: <http://benchmark/OWL2Bench#> .
@export handout :- csv{resource = "handout.csv"} .
@export fan :- csv{resource = "fan.csv"} .
"""
"""
Only the answers of the decision rules are exported, not the closure.
"""


def step_program(rules: str) -> str:
    """
    :param rules: The text of ``owl2rl.rls``.
    :return: The program of a step: the OWL 2 RL rules with the inputs of :data:`PROGRAM_HEADER`, the decision rules
        and the exports of :data:`PROGRAM_FOOTER`.
    """
    body = re.sub(r"^@(parameter|import|export) .*\n", "", rules, flags=re.MULTILINE)
    return PROGRAM_HEADER + body + "\n" + PROGRAM_FOOTER + DECISION_RULES


@dataclass
class NemoVariant(AgentVariant):
    """
    The knowledge is the raw data plus a file of the perceived facts; Nemo recomputes the closure and the decision
    rules every step.
    """

    name: ClassVar[str] = "nemo"
    description: ClassVar[str] = (
        "Python objects + Nemo 0.10.1 (OWL 2 RL rules): perceived facts appended to an N-Triples file, Nemo re-run "
        "from the raw data every step with two decision rules, the procedures run in Python on the candidates."
    )
    boundary_helpers: ClassVar[Tuple] = (event_triples, object_term)
    nemo_binary: str = field(default_factory=lambda: os.environ.get("NEMO_BINARY", "nmo"))
    """
    Path of the ``nmo`` executable.
    """
    work_directory: Path = field(default=None, init=False)
    """
    Holds the program, the perceived facts and Nemo's exports.
    """
    handout_rows: List[Tuple[str, str]] = field(default_factory=list, init=False)
    """
    The (student, course) answers of the last run.
    """
    fan_rows: List[str] = field(default_factory=list, init=False)
    """
    The fans of the last run.
    """
    nemo_seconds: List[Dict[str, float]] = field(default_factory=list, init=False)
    """
    Nemo's own report of every step's run: import, reasoning and export.
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
        self.work_directory = Path(tempfile.mkdtemp(prefix="agent_loop_nemo_"))
        (self.work_directory / "step.rls").write_text(step_program(NEMO_RULES.read_text()))
        (self.work_directory / "perceived.nt").write_text("")
        start = time.perf_counter()
        first_college = next(iter(self.scenario.perceptions)).requested_college
        reasoning = self._run_nemo(first_college)
        reasoning_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self._application_data()
        application_seconds = time.perf_counter() - start
        seconds = {"reasoning": reasoning_seconds, "application_data": application_seconds}
        return {
            "seconds": seconds,
            "total_seconds": sum(seconds.values()),
            "full_materialisation_seconds": reasoning_seconds,
            "nemo_report": reasoning,
            "nemo_version": subprocess.run([self.nemo_binary, "--version"], capture_output=True,
                                           text=True).stdout.strip(),
        }

    @boundary(MAPPING)
    def _application_data(self) -> None:
        """
        Build the application's lookup from IRIs to its own objects (course rooms and mail boxes).
        """
        campus = self.scenario.campus
        self.course_rooms = {iri: campus.place(room) for iri, room in self.scenario.course_rooms.items()}
        self.mailboxes = {iri: campus.place(room) for iri, room in self.scenario.mailboxes.items()}

    def _run_nemo(self, college: str) -> Dict[str, float]:
        """
        Run the step program and read its answers.

        :param college: IRI of the requested college.
        :return: Nemo's report of the run, in seconds.
        """
        export_directory = self.work_directory / "export"
        command = [
            self.nemo_binary, "--overwrite-results", "--export-dir", str(export_directory), "--report", "short",
            "--param", f'input="{Path(UNREASONED_FILE).resolve()}"',
            "--param", f'perceived="{self.work_directory / "perceived.nt"}"',
            "--param", f"college=<{college}>",
            str(self.work_directory / "step.rls"),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=True)
        report = {}
        for line in (completed.stdout + completed.stderr).splitlines():
            match = NEMO_REPORT_LINE.match(line)
            if match:
                value = float(match.group(2))
                report[match.group(1)] = value / 1000 if match.group(3) == "ms" else value
        with open(export_directory / "handout.csv", newline="") as stream:
            self.handout_rows = [(row[0], row[1]) for row in csv.reader(stream)]
        with open(export_directory / "fan.csv", newline="") as stream:
            self.fan_rows = [row[0] for row in csv.reader(stream)]
        return report

    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        with meter.phase("update"):
            written = self._append_facts(perception)
        with meter.phase("reasoning"):
            self.nemo_seconds.append(self._run_nemo(perception.requested_college))
        meter.reasoner_calls += 1
        meter.statements_inserted += written

    @boundary(SYNCHRONIZATION)
    def _append_facts(self, perception: StepPerception) -> int:
        """
        :param perception: The perception of a step.
        :return: The number of statements appended to the file of perceived facts.
        """
        lines = [
            f"<{subject}> <{predicate}> {object_term(value)} .\n"
            for event in perception.knowledge_events
            for subject, predicate, value in event_triples(event)
        ]
        with open(self.work_directory / "perceived.nt", "a") as stream:
            stream.writelines(lines)
        return len(lines)

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("mapping"):
            rows = self._handout_rows(self.handout_rows)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, _, room in rows})
            return [
                HandoutCandidate(student, course, room.identifier, reachable[room])
                for student, course, room in rows
                if room in reachable
            ]

    @boundary(MAPPING)
    def _handout_rows(self, pairs: List[Tuple[str, str]]) -> List[Tuple[str, str, Place]]:
        """
        :param pairs: (student, course) answers of the handout rule.
        :return: (student IRI, course IRI, course room) rows.
        """
        return [(student, course, self.course_rooms[course]) for student, course in pairs]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("mapping"):
            rows = self._ticket_rows(self.fan_rows)
        with meter.phase("query"):
            reachable = self._reachable_driving_times({room for _, room in rows})
            return [TicketCandidate(person, room.identifier, reachable[room]) for person, room in rows if room in reachable]

    @boundary(MAPPING)
    def _ticket_rows(self, fans: List[str]) -> List[Tuple[str, Place]]:
        """
        :param fans: The answers of the fan rule.
        :return: (person IRI, mail box room) rows.
        """
        default = self.scenario.campus.place(self.scenario.default_mailbox)
        return [(person, self.mailboxes.get(person, default)) for person in fans]

    @boundary(PROCEDURE_INTEGRATION)
    def _reachable_driving_times(self, rooms: set) -> Dict[Place, float]:
        """
        :param rooms: Rooms.
        :return: The driving time to every room the robot can reach.
        """
        return {room: travel_seconds(self.robot, room) for room in rooms if can_reach(self.robot, room)}

    def final_measurements(self) -> Dict[str, Any]:
        """
        :return: The distributions of Nemo's own report over the steps (import, reasoning, export).
        """
        phases = sorted({phase for report in self.nemo_seconds for phase in report})
        return {"nemo_report": {phase: distribution([report.get(phase, 0.0) for report in self.nemo_seconds])
                                for phase in phases}}

    def close(self) -> None:
        if self.work_directory is not None:
            shutil.rmtree(self.work_directory, ignore_errors=True)

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        handout, fan = DECISION_RULES.strip().split("\nfan")
        return {
            "handouts": query_size(handout, "nemo"),
            "tickets": query_size("fan" + fan, "nemo"),
        }
