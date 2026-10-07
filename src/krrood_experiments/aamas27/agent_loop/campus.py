"""
The campus map of the agent-loop experiment: application data that OWL2Bench lacks, generated deterministically from a
seed and identical for every variant.

Layout (all lengths in metres; an elevator ride counts as an equivalent walking length that includes waiting):

* Every college of the university is one building. The buildings stand on a grid of ``columns`` columns, ``column_spacing``
  by ``row_spacing`` metres apart. A service hub with the robot's main charging dock and the university mail room stands
  in the middle of the campus.
* Outdoor walkways connect the entrances of neighbouring buildings (left/right and front/back) and connect the hub with
  the buildings of the two middle columns. Walkways are not straight: the length of each one is its straight-line
  distance times a seeded detour factor.
* Inside a building, a lobby is connected to the entrance and to an elevator shaft. Every department of the college
  occupies one floor (in the order of the department identifiers); a floor has a corridor that starts at the elevator,
  with rooms on both sides: the department office (where the department's mail is delivered), one laboratory and as many
  classrooms as are needed to hold the department's courses (``courses_per_classroom`` courses share a classroom over
  the week).
* The first building also has a secondary charging dock in its lobby.

The map is a weighted, undirected graph. :class:`PathPlanner` computes shortest paths on it with Dijkstra's algorithm.
"""

from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


class PlaceKind(str, Enum):
    """
    The kind of a place on the campus map.
    """

    WALKWAY = "walkway"
    ENTRANCE = "entrance"
    LOBBY = "lobby"
    ELEVATOR = "elevator"
    CORRIDOR = "corridor"
    CLASSROOM = "classroom"
    OFFICE = "office"
    LABORATORY = "laboratory"
    MAIL_ROOM = "mail_room"
    DOCK = "dock"


ROOM_KINDS = frozenset(
    {PlaceKind.CLASSROOM, PlaceKind.OFFICE, PlaceKind.LABORATORY, PlaceKind.MAIL_ROOM}
)
"""
Kinds of places the robot delivers to.
"""


@dataclass(eq=False)
class Place:
    """
    A node of the campus map: a room, a corridor segment, an elevator stop, an entrance or a dock.
    """

    identifier: str
    """
    Unique identifier, for example ``U0C0D0-classroom-3``.
    """
    kind: PlaceKind
    """
    The kind of place.
    """
    building: str
    """
    Identifier of the building (the college identifier, or ``hub`` / ``outdoor``).
    """
    x: float
    """
    East coordinate in metres.
    """
    y: float
    """
    North coordinate in metres.
    """
    floor: int = 0
    """
    Floor number, 0 for the ground floor and outdoor places.
    """

    @property
    def is_room(self) -> bool:
        """
        :return: Whether the robot delivers to this place.
        """
        return self.kind in ROOM_KINDS

    def __repr__(self) -> str:
        return f"Place({self.identifier})"


@dataclass
class CampusLayout:
    """
    Parameters of the generated campus.
    """

    columns: int = 3
    """
    Number of building columns.
    """
    column_spacing: float = 150.0
    """
    East-west distance between neighbouring buildings.
    """
    row_spacing: float = 120.0
    """
    North-south distance between neighbouring buildings.
    """
    corridor_spacing: float = 8.0
    """
    Distance between neighbouring corridor segments on a floor.
    """
    door_length: float = 4.0
    """
    Distance from a corridor segment into a room.
    """
    lobby_length: float = 12.0
    """
    Distance from a building entrance through the lobby to the elevator.
    """
    elevator_metres_per_floor: float = 15.0
    """
    Equivalent walking length of riding the elevator one floor, waiting included.
    """
    courses_per_classroom: int = 5
    """
    Number of courses that share a classroom.
    """
    detour_range: Tuple[float, float] = (1.0, 1.3)
    """
    Range of the factor by which a walkway is longer than the straight line.
    """


@dataclass
class CampusMap:
    """
    The campus as a weighted undirected graph of places.
    """

    places: Dict[str, Place] = field(default_factory=dict)
    """
    The places by identifier.
    """
    neighbours: Dict[str, Dict[str, float]] = field(default_factory=dict)
    """
    For every place, the lengths of the edges to its neighbours.
    """
    docks: List[str] = field(default_factory=list)
    """
    Identifiers of the charging docks.
    """
    mail_room: Optional[str] = None
    """
    Identifier of the university mail room (for people without a department).
    """
    department_offices: Dict[str, str] = field(default_factory=dict)
    """
    Department IRI to the identifier of its office.
    """
    department_classrooms: Dict[str, List[str]] = field(default_factory=dict)
    """
    Department IRI to the identifiers of its classrooms.
    """

    def add_place(self, place: Place) -> Place:
        """
        :param place: The place to add.
        :return: The added place.
        """
        self.places[place.identifier] = place
        self.neighbours.setdefault(place.identifier, {})
        return place

    def connect(self, first: Place, second: Place, length: Optional[float] = None) -> None:
        """
        Add an undirected edge.

        :param first: One end.
        :param second: The other end.
        :param length: The edge length; the horizontal straight-line distance if not given.
        """
        if length is None:
            length = math.hypot(first.x - second.x, first.y - second.y)
        self.neighbours[first.identifier][second.identifier] = length
        self.neighbours[second.identifier][first.identifier] = length

    def place(self, identifier: str) -> Place:
        """
        :param identifier: A place identifier.
        :return: The place.
        """
        return self.places[identifier]

    def rooms(self) -> List[Place]:
        """
        :return: All places the robot delivers to, sorted by identifier.
        """
        return sorted(
            (place for place in self.places.values() if place.is_room),
            key=lambda place: place.identifier,
        )

    def edge_count(self) -> int:
        """
        :return: The number of undirected edges.
        """
        return sum(len(edges) for edges in self.neighbours.values()) // 2

    def to_json(self) -> Dict[str, Any]:
        """
        :return: A JSON-serialisable representation.
        """
        return {
            "places": [
                [p.identifier, p.kind.value, p.building, p.x, p.y, p.floor]
                for p in self.places.values()
            ],
            "edges": [
                [first, second, length]
                for first, edges in self.neighbours.items()
                for second, length in edges.items()
                if first < second
            ],
            "docks": self.docks,
            "mail_room": self.mail_room,
            "department_offices": self.department_offices,
            "department_classrooms": self.department_classrooms,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> CampusMap:
        """
        :param data: The output of :meth:`to_json`.
        :return: The campus map.
        """
        campus = cls(
            docks=list(data["docks"]),
            mail_room=data["mail_room"],
            department_offices=dict(data["department_offices"]),
            department_classrooms={k: list(v) for k, v in data["department_classrooms"].items()},
        )
        for identifier, kind, building, x, y, floor in data["places"]:
            campus.add_place(Place(identifier, PlaceKind(kind), building, x, y, floor))
        for first, second, length in data["edges"]:
            campus.connect(campus.places[first], campus.places[second], length)
        return campus


def generate_campus(
    departments_by_college: Dict[str, List[str]],
    courses_by_department: Dict[str, List[str]],
    random_generator: random.Random,
    layout: Optional[CampusLayout] = None,
) -> CampusMap:
    """
    Generate the campus map (see the module documentation for the layout).

    :param departments_by_college: College IRI to the IRIs of its departments.
    :param courses_by_department: Department IRI to the IRIs of the courses it offers.
    :param random_generator: The seeded random generator.
    :param layout: Layout parameters.
    :return: The campus map.
    """
    layout = layout or CampusLayout()
    campus = CampusMap()
    colleges = sorted(departments_by_college)
    rows = math.ceil(len(colleges) / layout.columns)
    entrances: Dict[Tuple[int, int], Place] = {}
    for index, college in enumerate(colleges):
        row, column = divmod(index, layout.columns)
        entrance = _add_building(
            campus,
            college,
            sorted(departments_by_college[college]),
            courses_by_department,
            column * layout.column_spacing,
            row * layout.row_spacing,
            layout,
        )
        entrances[(row, column)] = entrance
    _add_hub(campus, rows, layout)
    _add_walkways(campus, entrances, rows, layout, random_generator)
    first_building = local_name(colleges[0])
    first_lobby = campus.place(f"{first_building}-lobby")
    secondary_dock = campus.add_place(
        Place(f"{first_building}-dock", PlaceKind.DOCK, first_building, first_lobby.x - 6, first_lobby.y, 0)
    )
    campus.connect(first_lobby, secondary_dock)
    campus.docks.append(secondary_dock.identifier)
    return campus


def _add_building(
    campus: CampusMap,
    college: str,
    departments: List[str],
    courses_by_department: Dict[str, List[str]],
    x: float,
    y: float,
    layout: CampusLayout,
) -> Place:
    """
    Add the building of a college: entrance, lobby, elevator stops and one floor per department.

    :return: The entrance of the building.
    """
    name = local_name(college)
    entrance = campus.add_place(Place(f"{name}-entrance", PlaceKind.ENTRANCE, name, x, y, 0))
    lobby = campus.add_place(Place(f"{name}-lobby", PlaceKind.LOBBY, name, x, y + 6, 0))
    campus.connect(entrance, lobby)
    previous_stop = campus.add_place(
        Place(f"{name}-elevator-0", PlaceKind.ELEVATOR, name, x, y + layout.lobby_length, 0)
    )
    campus.connect(lobby, previous_stop)
    for floor_index, department in enumerate(departments, start=1):
        stop = campus.add_place(
            Place(f"{name}-elevator-{floor_index}", PlaceKind.ELEVATOR, name, x, y + layout.lobby_length, floor_index)
        )
        campus.connect(previous_stop, stop, layout.elevator_metres_per_floor)
        previous_stop = stop
        _add_department_floor(campus, name, department, courses_by_department.get(department, []), stop, layout)
    return entrance


def _add_department_floor(
    campus: CampusMap,
    building: str,
    department: str,
    courses: List[str],
    elevator_stop: Place,
    layout: CampusLayout,
) -> None:
    """
    Add the corridor and the rooms of a department on its floor.
    """
    department_name = local_name(department)
    classroom_count = max(1, math.ceil(len(courses) / layout.courses_per_classroom))
    rooms = [(PlaceKind.OFFICE, f"{department_name}-office"), (PlaceKind.LABORATORY, f"{department_name}-laboratory")]
    rooms += [(PlaceKind.CLASSROOM, f"{department_name}-classroom-{i}") for i in range(classroom_count)]
    previous = elevator_stop
    floor = elevator_stop.floor
    for segment_index in range(math.ceil(len(rooms) / 2)):
        segment = campus.add_place(
            Place(
                f"{department_name}-corridor-{segment_index}",
                PlaceKind.CORRIDOR,
                building,
                elevator_stop.x + (segment_index + 1) * layout.corridor_spacing,
                elevator_stop.y,
                floor,
            )
        )
        campus.connect(previous, segment)
        previous = segment
        for side, (kind, identifier) in zip((1, -1), rooms[2 * segment_index : 2 * segment_index + 2]):
            room = campus.add_place(
                Place(identifier, kind, building, segment.x, segment.y + side * layout.door_length, floor)
            )
            campus.connect(segment, room)
    campus.department_offices[department] = f"{department_name}-office"
    campus.department_classrooms[department] = [
        identifier for kind, identifier in rooms if kind is PlaceKind.CLASSROOM
    ]


def _add_hub(campus: CampusMap, rows: int, layout: CampusLayout) -> None:
    """
    Add the service hub with the main dock and the mail room in the middle of the campus.
    """
    x = (layout.columns - 1) * layout.column_spacing / 2
    y = (rows - 1) * layout.row_spacing / 2
    entrance = campus.add_place(Place("hub-entrance", PlaceKind.ENTRANCE, "hub", x, y, 0))
    dock = campus.add_place(Place("hub-dock", PlaceKind.DOCK, "hub", x + 5, y, 0))
    mail_room = campus.add_place(Place("hub-mail-room", PlaceKind.MAIL_ROOM, "hub", x - 5, y, 0))
    campus.connect(entrance, dock)
    campus.connect(entrance, mail_room)
    campus.docks.append(dock.identifier)
    campus.mail_room = mail_room.identifier


def _add_walkways(
    campus: CampusMap,
    entrances: Dict[Tuple[int, int], Place],
    rows: int,
    layout: CampusLayout,
    random_generator: random.Random,
) -> None:
    """
    Connect neighbouring building entrances, and the hub with the buildings of the middle column(s).
    """

    def walkway(first: Place, second: Place) -> None:
        straight = math.hypot(first.x - second.x, first.y - second.y)
        campus.connect(first, second, straight * random_generator.uniform(*layout.detour_range))

    for (row, column), entrance in sorted(entrances.items()):
        for neighbour_position in ((row, column + 1), (row + 1, column)):
            neighbour = entrances.get(neighbour_position)
            if neighbour is not None:
                walkway(entrance, neighbour)
    hub = campus.place("hub-entrance")
    middle_columns = {(layout.columns - 1) // 2, layout.columns // 2}
    for (row, column), entrance in sorted(entrances.items()):
        if column in middle_columns:
            walkway(hub, entrance)


def local_name(iri: str) -> str:
    """
    :param iri: An IRI.
    :return: The part after the last ``#`` or ``/``.
    """
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


@dataclass
class PathPlanner:
    """
    Shortest paths on the campus map with Dijkstra's algorithm. The distance field from a start place is computed once
    and kept, since a robot plans from the same few places again and again (every variant uses the same planner).
    """

    campus: CampusMap
    """
    The campus map.
    """
    distance_fields: Dict[str, Dict[str, float]] = field(default_factory=dict, repr=False)
    """
    Start place identifier to the shortest distances to every place.
    """
    nearest_dock_distances: Optional[Dict[str, float]] = field(default=None, repr=False)
    """
    For every place, the distance to the nearest charging dock.
    """

    def distance(self, start: Place, goal: Place) -> float:
        """
        :param start: The start place.
        :param goal: The goal place.
        :return: The length of a shortest path, infinite if the goal cannot be reached.
        """
        field_from_start = self.distance_fields.get(start.identifier)
        if field_from_start is None:
            field_from_start = self.dijkstra([start.identifier])
            self.distance_fields[start.identifier] = field_from_start
        return field_from_start.get(goal.identifier, math.inf)

    def distance_to_nearest_dock(self, place: Place) -> float:
        """
        :param place: A place.
        :return: The length of a shortest path from the place to the nearest charging dock.
        """
        if self.nearest_dock_distances is None:
            self.nearest_dock_distances = self.dijkstra(self.campus.docks)
        return self.nearest_dock_distances.get(place.identifier, math.inf)

    def nearest_dock(self, place: Place) -> Place:
        """
        :param place: A place.
        :return: The charging dock nearest to the place (ties broken by identifier).
        """
        return min(
            (self.campus.place(dock) for dock in self.campus.docks),
            key=lambda dock: (self.distance(place, dock), dock.identifier),
        )

    def dijkstra(self, sources: Iterable[str]) -> Dict[str, float]:
        """
        :param sources: Identifiers of the start places (distance 0).
        :return: The shortest distance from the nearest source to every reachable place.
        """
        distances: Dict[str, float] = {}
        queue: List[Tuple[float, str]] = [(0.0, source) for source in sources]
        heapq.heapify(queue)
        while queue:
            distance, identifier = heapq.heappop(queue)
            if identifier in distances:
                continue
            distances[identifier] = distance
            for neighbour, length in self.campus.neighbours[identifier].items():
                if neighbour not in distances:
                    heapq.heappush(queue, (distance + length, neighbour))
        return distances
