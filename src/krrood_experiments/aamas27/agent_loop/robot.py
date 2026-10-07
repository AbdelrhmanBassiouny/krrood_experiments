"""
The delivery robot, its own procedures and its decision policy. All of this is the same code in every variant: only how
the knowledge is kept, updated and queried differs.

The robot's pose and battery level are plain state of the :class:`Robot` object; the procedures read them at call time
(they are computables, not stored facts), so they change whenever the robot moves or charges.

The two procedures that reasoning has to call are

* :func:`can_reach` (reachable with the remaining battery: the robot must be able to drive to the room and from there
  to the nearest charging dock), and
* :func:`travel_seconds` (driving time to the room),

both on top of the path planner (Dijkstra's algorithm on the campus map). Their calls are counted and timed by a
:class:`ProcedureMeter`.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Sequence, Set, Tuple

from .campus import CampusMap, PathPlanner, Place
from .scenario import RobotSpecification


@dataclass
class ProcedureMeter:
    """
    Counts and times the calls of the robot's procedures.
    """

    calls: Dict[str, int] = field(default_factory=dict)
    """
    Number of calls per procedure.
    """
    seconds: float = 0.0
    """
    Total wall time spent in the procedures.
    """

    def record(self, procedure: str, elapsed: float) -> None:
        """
        :param procedure: The procedure name.
        :param elapsed: The wall time of the call.
        """
        self.calls[procedure] = self.calls.get(procedure, 0) + 1
        self.seconds += elapsed

    @property
    def total_calls(self) -> int:
        """
        :return: The number of calls of all procedures.
        """
        return sum(self.calls.values())


@dataclass(eq=False)
class Robot:
    """
    The delivery robot: its state changes every step.
    """

    specification: RobotSpecification
    """
    The robot's parameters.
    """
    planner: PathPlanner
    """
    The path planner on the campus map.
    """
    place: Place
    """
    The current pose (the robot is always at a place of the map).
    """
    battery_metres: float
    """
    The remaining battery, as the distance the robot can still drive.
    """
    procedure_meter: ProcedureMeter = field(default_factory=ProcedureMeter)
    """
    Counts and times the calls of :func:`can_reach` and :func:`travel_seconds`.
    """
    driven_metres: float = 0.0
    """
    Total distance driven.
    """

    @classmethod
    def at_start(cls, specification: RobotSpecification, campus: CampusMap) -> Robot:
        """
        :param specification: The robot's parameters.
        :param campus: The campus map.
        :return: A robot at its start place with a full battery.
        """
        return cls(
            specification=specification,
            planner=PathPlanner(campus),
            place=campus.place(specification.start_place),
            battery_metres=specification.battery_capacity_metres,
        )

    @property
    def needs_charging(self) -> bool:
        """
        :return: Whether the battery is below the charge threshold.
        """
        return (
            self.battery_metres
            < self.specification.charge_threshold * self.specification.battery_capacity_metres
        )

    def drive_to(self, goal: Place) -> float:
        """
        Drive to a place along a shortest path.

        :param goal: The place to drive to.
        :return: The distance driven.
        """
        distance = self.planner.distance(self.place, goal)
        self.battery_metres -= distance
        self.driven_metres += distance
        self.place = goal
        return distance

    def charge(self) -> None:
        """
        Charge the battery fully (the robot must be at a dock).
        """
        assert self.place.identifier in self.planner.campus.docks
        self.battery_metres = self.specification.battery_capacity_metres


def can_reach(robot: Robot, room: Place) -> bool:
    """
    :param robot: The robot (its current pose and battery are read now).
    :param room: A room.
    :return: Whether the robot can drive to the room and from there to the nearest charging dock with its battery.
    """
    start = time.perf_counter()
    needed = robot.planner.distance(robot.place, room) + robot.planner.distance_to_nearest_dock(room)
    result = needed <= robot.battery_metres
    robot.procedure_meter.record("can_reach", time.perf_counter() - start)
    return result


def travel_seconds(robot: Robot, room: Place) -> float:
    """
    :param robot: The robot (its current pose is read now).
    :param room: A room.
    :return: The driving time to the room in seconds.
    """
    start = time.perf_counter()
    result = robot.planner.distance(robot.place, room) / robot.specification.speed_metres_per_second
    robot.procedure_meter.record("travel_seconds", time.perf_counter() - start)
    return result


@dataclass(frozen=True)
class HandoutCandidate:
    """
    A student of the requested college who takes a course whose room the robot can reach.
    """

    student: str
    """
    IRI of the student.
    """
    course: str
    """
    IRI of the course.
    """
    room: str
    """
    Identifier of the course room.
    """
    travel_seconds: float
    """
    Driving time to the room.
    """


@dataclass(frozen=True)
class TicketCandidate:
    """
    A T20 cricket fan whose mail box the robot can reach.
    """

    person: str
    """
    IRI of the fan.
    """
    room: str
    """
    Identifier of the mail box room.
    """
    travel_seconds: float
    """
    Driving time to the room.
    """


class ActionKind(str, Enum):
    """
    What the robot does in a step.
    """

    DELIVER_HANDOUTS = "deliver_handouts"
    DELIVER_TICKET = "deliver_ticket"
    CHARGE = "charge"
    WAIT = "wait"


@dataclass(frozen=True)
class Action:
    """
    The decision of one step.
    """

    kind: ActionKind
    """
    What the robot does.
    """
    target: str
    """
    Identifier of the place the robot drives to.
    """
    subject: Tuple[str, ...] = ()
    """
    What is delivered: (college, course) for handouts, (person,) for a ticket.
    """

    def to_json(self) -> List:
        """
        :return: A JSON-serialisable representation.
        """
        return [self.kind.value, self.target, list(self.subject)]

    @classmethod
    def from_json(cls, data: Sequence) -> Action:
        """
        :param data: The output of :meth:`to_json`.
        :return: The action.
        """
        return cls(ActionKind(data[0]), data[1], tuple(data[2]))


@dataclass
class DeliveryPolicy:
    """
    The robot's decision policy, identical in every variant. It remembers what has been delivered (application state,
    not knowledge).

    * Below the charge threshold the robot drives to the nearest dock and charges.
    * Otherwise it drives to the nearest room with an undelivered item: a match ticket for a fan, or the handouts of
      the requested college for a course (one delivery per college and course). Ties go to the ticket, then to the
      smaller IRI.
    * Without such a room it charges if the battery is not full, and waits otherwise.
    """

    delivered_tickets: Set[str] = field(default_factory=set)
    """
    Fans that got a ticket.
    """
    delivered_handouts: Set[Tuple[str, str]] = field(default_factory=set)
    """
    (college, course) pairs whose handouts were delivered.
    """

    def decide(
        self,
        robot: Robot,
        requested_college: str,
        handouts: Sequence[HandoutCandidate],
        tickets: Sequence[TicketCandidate],
    ) -> Action:
        """
        :param robot: The robot.
        :param requested_college: The college whose handouts are requested.
        :param handouts: The handout candidates.
        :param tickets: The ticket candidates.
        :return: The action of this step.
        """
        if robot.needs_charging:
            return self.charge_action(robot)
        ticket = min(
            (t for t in tickets if t.person not in self.delivered_tickets),
            key=lambda t: (t.travel_seconds, t.person),
            default=None,
        )
        handout = min(
            (h for h in handouts if (requested_college, h.course) not in self.delivered_handouts),
            key=lambda h: (h.travel_seconds, h.course, h.student),
            default=None,
        )
        if ticket is not None and (handout is None or ticket.travel_seconds <= handout.travel_seconds):
            return Action(ActionKind.DELIVER_TICKET, ticket.room, (ticket.person,))
        if handout is not None:
            return Action(ActionKind.DELIVER_HANDOUTS, handout.room, (requested_college, handout.course))
        if robot.battery_metres < robot.specification.battery_capacity_metres:
            return self.charge_action(robot)
        return Action(ActionKind.WAIT, robot.place.identifier)

    @staticmethod
    def charge_action(robot: Robot) -> Action:
        """
        :param robot: The robot.
        :return: Drive to the nearest dock and charge.
        """
        return Action(ActionKind.CHARGE, robot.planner.nearest_dock(robot.place).identifier)

    def act(self, robot: Robot, action: Action) -> float:
        """
        Carry out an action.

        :param robot: The robot.
        :param action: The action.
        :return: The distance driven.
        """
        distance = robot.drive_to(robot.planner.campus.place(action.target))
        if action.kind is ActionKind.CHARGE:
            robot.charge()
        elif action.kind is ActionKind.DELIVER_TICKET:
            self.delivered_tickets.add(action.subject[0])
        elif action.kind is ActionKind.DELIVER_HANDOUTS:
            self.delivered_handouts.add((action.subject[0], action.subject[1]))
        if math.isinf(distance):
            raise RuntimeError(f"{action.target} cannot be reached")
        return distance
