"""
The examples of the EQL formalization (formalization/eql_formalization.tex, Section 4), run on the current version
of KRROOD, and its statements about result quantifiers (Section 3.5).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest

from krrood.entity_query_language.exceptions import MultipleSolutionFound, NoSolutionFound, \
    QuantificationNotSatisfiedError
from krrood.entity_query_language.factories import an, entity, inference, not_, the, variable
from krrood.entity_query_language.predicate import symbolic_function


@dataclass
class Task:
    name: str
    completed: bool


@dataclass
class Robot:
    name: str
    battery: int
    tasks: List[Task]


@dataclass
class HighLoadRobot:
    robot: Robot


@symbolic_function
def has_incomplete_task(robot):
    return any(not t.completed for t in robot.tasks)


clean, fetch = Task("clean", False), Task("fetch", True)
robots = [Robot("R1", 80, [clean]), Robot("R2", 20, [clean, fetch]), Robot("R3", 60, [fetch])]


def test_example_query():
    r = variable(Robot, domain=robots)
    results = an(entity(r).where(r.battery > 50, not_(r.tasks[0].completed))).tolist()
    assert [x.name for x in results] == ["R1"]


def test_example_rule_derives_one_instance_per_binding():
    r = variable(Robot, domain=robots)
    high_load = inference(HighLoadRobot)(robot=r)
    rule = an(entity(high_load).where(r.battery < 30, has_incomplete_task(r)))
    first, second = rule.tolist(), rule.tolist()
    assert [h.robot.name for h in first] == ["R2"]
    assert first[0] is second[0]


def test_the_raises_on_none_and_on_several():
    r = variable(Robot, domain=robots)
    with pytest.raises(MultipleSolutionFound):
        the(entity(r).where(r.battery > 50)).tolist()
    with pytest.raises(NoSolutionFound):
        the(entity(r).where(r.battery > 100)).tolist()
    assert issubclass(MultipleSolutionFound, QuantificationNotSatisfiedError)
    assert issubclass(NoSolutionFound, QuantificationNotSatisfiedError)


def test_the_checks_incrementally():
    r = variable(Robot, domain=robots)
    assert the(entity(r).where(r.battery > 50)).first().name == "R1"
