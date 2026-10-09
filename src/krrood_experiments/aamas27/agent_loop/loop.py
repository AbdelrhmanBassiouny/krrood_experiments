"""
The perceive -> decide -> act loop that every variant runs with the same robot, the same policy and the same scenario.
A variant only implements how the knowledge is kept up to date and how the two decision queries are answered.

The two decision queries of a step:

* handouts: the students who are members of the requested college (``isMemberOf``, inferred through the property chain
  ``enrollIn o isPartOf`` and the transitive ``isPartOf``) together with the courses they take, where the robot can
  reach the course room (:func:`~krrood_experiments.aamas27.agent_loop.robot.can_reach`), with the driving time
  (:func:`~krrood_experiments.aamas27.agent_loop.robot.travel_seconds`);
* tickets: the T20 cricket fans (``T20CricketFan``, defined by ``isCrazyAbout value T20Cricket``) whose mail box the robot
  can reach, with the driving time.

When reference actions are given (the actions of the reference variant), the robot carries them out instead of its own
decision, so that every variant sees exactly the same states even if one of them decides differently; its own decision
is still recorded and compared.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, List, Optional, Sequence, Tuple

from .events import StepPerception
from .measurement import StepMeter, boundary_lines
from .robot import Action, DeliveryPolicy, HandoutCandidate, Robot, TicketCandidate
from .scenario import Scenario


@dataclass
class AgentVariant(ABC):
    """
    One way of keeping and querying the agent's knowledge.
    """

    scenario: Scenario
    """
    The scenario.
    """
    robot: Robot
    """
    The robot, whose procedures the decision queries need.
    """

    name: ClassVar[str]
    """
    The variant name used on the command line and in the results.
    """
    description: ClassVar[str]
    """
    One sentence on what the variant does.
    """
    boundary_helpers: ClassVar[Tuple[Callable, ...]] = ()
    """
    Module-level functions marked with :func:`~krrood_experiments.aamas27.agent_loop.measurement.boundary` that the
    variant uses, for the line count.
    """

    @abstractmethod
    def setup(self) -> Dict[str, Any]:
        """
        Load the knowledge and the application data.

        :return: Wall times of the setup phases in seconds, and sizes.
        """

    @abstractmethod
    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        """
        Bring the knowledge up to date with the perceived facts and the robot's new state.

        :param perception: The perception of this step.
        :param meter: The step meter.
        """

    @abstractmethod
    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        """
        :param college: IRI of the requested college.
        :param meter: The step meter.
        :return: The handout candidates.
        """

    @abstractmethod
    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        """
        :param meter: The step meter.
        :return: The ticket candidates.
        """

    @classmethod
    @abstractmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        """
        :return: For every query the variant evaluates in a step, its text and size
         (:func:`~krrood_experiments.aamas27.agent_loop.measurement.query_size`).
        """

    def final_measurements(self) -> Dict[str, Any]:
        """
        :return: Measurements taken once after the last step.
        """
        return {}

    def close(self) -> None:
        """
        Release external resources.
        """

    @classmethod
    def code_report(cls) -> Dict[str, Any]:
        """
        :return: The lines of synchronisation and mapping code and the query texts.
        """
        return {"boundary_lines": boundary_lines(cls), "queries": cls.query_texts()}


def candidates_digest(handouts: Sequence[HandoutCandidate], tickets: Sequence[TicketCandidate]) -> Dict[str, Any]:
    """
    :param handouts: The handout candidates of a step.
    :param tickets: The ticket candidates of a step.
    :return: Sorted, de-duplicated candidate rows and a digest of them (driving times rounded to microseconds).
    """
    handout_rows = sorted({(h.student, h.course, h.room, round(h.travel_seconds, 6)) for h in handouts})
    ticket_rows = sorted({(t.person, t.room, round(t.travel_seconds, 6)) for t in tickets})
    text = json.dumps([handout_rows, ticket_rows])
    return {
        "handout_rows": handout_rows,
        "ticket_rows": ticket_rows,
        "digest": hashlib.sha256(text.encode()).hexdigest(),
    }


@dataclass
class LoopResult:
    """
    The measurements of one variant's run.
    """

    variant: str
    """
    The variant name.
    """
    setup: Dict[str, Any]
    """
    The setup report of the variant.
    """
    steps: List[Dict[str, Any]] = field(default_factory=list)
    """
    One record per step.
    """
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    """
    The candidate rows of every step (written to a separate compressed file).
    """

    def write(self, directory: Path) -> Tuple[Path, Path]:
        """
        :param directory: The results directory.
        :return: The step file and the candidates file.
        """
        step_file = directory / f"agent_loop_{self.variant}.json"
        step_file.write_text(json.dumps({"variant": self.variant, "setup": self.setup, "steps": self.steps}, indent=1))
        candidates_file = directory / f"agent_loop_{self.variant}_candidates.json.gz"
        with gzip.open(candidates_file, "wt", encoding="utf-8") as stream:
            json.dump(self.candidates, stream)
        return step_file, candidates_file


def run_agent_loop(
    variant: AgentVariant,
    reference_actions: Optional[List[Action]] = None,
    progress: Optional[Callable[[int, Dict[str, Any]], None]] = None,
) -> LoopResult:
    """
    Run the loop of a variant over all steps of its scenario.

    :param variant: The variant, not yet set up.
    :param reference_actions: Actions to carry out instead of the variant's own decisions.
    :param progress: Called after every step with the step number and its record.
    :return: The measurements.
    """
    robot = variant.robot
    result = LoopResult(variant=variant.name, setup=variant.setup())
    policy = DeliveryPolicy()
    for perception in variant.scenario.perceptions:
        meter = StepMeter(robot.procedure_meter)
        calls_before = dict(robot.procedure_meter.calls)
        false_results_before = dict(robot.procedure_meter.false_results)
        variant.perceive(perception, meter)
        start = time.perf_counter()
        handouts = variant.handout_candidates(perception.requested_college, meter)
        handout_seconds = time.perf_counter() - start
        start = time.perf_counter()
        tickets = variant.ticket_candidates(meter)
        ticket_seconds = time.perf_counter() - start
        with meter.phase("decide"):
            action = policy.decide(robot, perception.requested_college, handouts, tickets)
        performed = reference_actions[perception.step] if reference_actions else action
        with meter.phase("act"):
            policy.act(robot, performed)
        digest = candidates_digest(handouts, tickets)
        record = {
            "step": perception.step,
            **meter.to_json(),
            "decision_seconds": {"handouts": handout_seconds, "tickets": ticket_seconds},
            "procedure_calls": {
                name: count - calls_before.get(name, 0) for name, count in robot.procedure_meter.calls.items()
            },
            "procedure_false_results": {
                name: count - false_results_before.get(name, 0)
                for name, count in robot.procedure_meter.false_results.items()
            },
            "handout_candidates": len(digest["handout_rows"]),
            "ticket_candidates": len(digest["ticket_rows"]),
            "candidates_digest": digest["digest"],
            "action": action.to_json(),
            "performed_action": performed.to_json(),
            "robot_place": robot.place.identifier,
            "robot_battery_metres": robot.battery_metres,
        }
        result.steps.append(record)
        result.candidates.append(
            {"step": perception.step, "handouts": digest["handout_rows"], "tickets": digest["ticket_rows"]}
        )
        if progress:
            progress(perception.step, record)
    result.setup["after_last_step"] = variant.final_measurements()
    variant.close()
    return result
