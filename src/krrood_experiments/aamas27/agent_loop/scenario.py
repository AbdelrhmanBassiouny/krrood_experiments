"""
The scenario of the agent-loop experiment, generated deterministically from the raw OWL2Bench file and a seed, and
identical for every variant:

* the campus map (:mod:`krrood_experiments.aamas27.agent_loop.campus`),
* the room in which every course is taught (a classroom of the department that offers it, ``courses_per_classroom``
  courses per classroom), and the mail box of every person (the office of the person's department, the university
  mail room for people without one),
* the robot (start at the hub dock with a full battery),
* the perceptions of every step: ``events_per_step`` knowledge events and the college whose handouts are requested.

Knowledge events are drawn so that every one adds a new fact: enrollments create new people (so the functional
``enrollIn`` never gets a second value), a student takes a course they do not take yet (preferably one of their own
department), and a person who is not yet crazy about T20 cricket (and does not dislike it, since ``likes`` and
``dislikes`` are disjoint) becomes crazy about it.

The scenario is read from the raw data with RDFLib only (no reasoning), independently of every variant.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import rdflib
from rdflib import RDF, RDFS, URIRef

from .campus import CampusLayout, CampusMap, generate_campus
from .events import (
    OWL2BENCH,
    T20_CRICKET,
    CourseTaking,
    CricketEnthusiasm,
    Enrollment,
    KnowledgeEvent,
    StepPerception,
)

NEW_PERSON_PREFIX = OWL2BENCH + "AgentLoopPerson"
"""
IRI prefix of the people created by enrollment events.
"""


@dataclass
class EventMix:
    """
    Relative frequencies of the knowledge events.
    """

    enrollment: float = 0.25
    """
    Weight of :class:`Enrollment`.
    """
    course_taking: float = 0.6
    """
    Weight of :class:`CourseTaking`.
    """
    cricket_enthusiasm: float = 0.15
    """
    Weight of :class:`CricketEnthusiasm`.
    """
    own_department_course_probability: float = 0.7
    """
    Probability that a student takes a course of their own department.
    """


@dataclass
class RobotSpecification:
    """
    The delivery robot.
    """

    start_place: str = "hub-dock"
    """
    The place where the robot starts.
    """
    battery_capacity_metres: float = 2500.0
    """
    How far the robot can drive on a full battery (elevator rides count with their equivalent length).
    """
    speed_metres_per_second: float = 1.2
    """
    Average driving speed.
    """
    charge_threshold: float = 0.25
    """
    Fraction of the capacity below which the robot goes to charge.
    """


@dataclass
class UniversityData:
    """
    What the scenario generator reads from the raw OWL2Bench data.
    """

    departments_by_college: Dict[str, List[str]]
    """
    College IRI to the IRIs of its departments.
    """
    courses_by_department: Dict[str, List[str]]
    """
    Department IRI to the IRIs of the courses it offers.
    """
    department_of_person: Dict[str, Optional[str]]
    """
    Person IRI to the IRI of the person's department (None if the person has none).
    """
    students: List[str]
    """
    IRIs of the people who are enrolled in a department, sorted.
    """
    courses_taken: Set[Tuple[str, str]]
    """
    The explicit (student, course) pairs.
    """
    cricket_enthusiasts: Set[str]
    """
    People who are already crazy about T20 cricket.
    """
    cricket_haters: Set[str]
    """
    People who dislike T20 cricket.
    """


@dataclass
class Scenario:
    """
    Everything that is identical for every variant.
    """

    seed: int
    """
    The seed of the random generator.
    """
    steps: int
    """
    Number of steps of the loop.
    """
    events_per_step: int
    """
    Number of knowledge events per step.
    """
    campus: CampusMap
    """
    The campus map.
    """
    course_rooms: Dict[str, str]
    """
    Course IRI to the identifier of the classroom where it is taught.
    """
    mailboxes: Dict[str, str]
    """
    Person IRI to the identifier of the room where the person's mail is delivered (people created by enrollments
    included).
    """
    robot: RobotSpecification
    """
    The robot.
    """
    perceptions: List[StepPerception]
    """
    The perceptions of every step.
    """

    @property
    def default_mailbox(self) -> str:
        """
        :return: The room of people the scenario has no mail box for (the university mail room).
        """
        return self.campus.mail_room

    def mailbox_of(self, person: str) -> str:
        """
        :param person: A person IRI.
        :return: The identifier of the person's mail box room.
        """
        return self.mailboxes.get(person, self.default_mailbox)

    def to_json(self) -> Dict[str, Any]:
        """
        :return: A JSON-serialisable representation.
        """
        return {
            "seed": self.seed,
            "steps": self.steps,
            "events_per_step": self.events_per_step,
            "campus": self.campus.to_json(),
            "course_rooms": self.course_rooms,
            "mailboxes": self.mailboxes,
            "robot": self.robot.__dict__,
            "perceptions": [perception.to_json() for perception in self.perceptions],
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Scenario:
        """
        :param data: The output of :meth:`to_json`.
        :return: The scenario.
        """
        return cls(
            seed=data["seed"],
            steps=data["steps"],
            events_per_step=data["events_per_step"],
            campus=CampusMap.from_json(data["campus"]),
            course_rooms=dict(data["course_rooms"]),
            mailboxes=dict(data["mailboxes"]),
            robot=RobotSpecification(**data["robot"]),
            perceptions=[StepPerception.from_json(p) for p in data["perceptions"]],
        )

    def write(self, path: Path) -> None:
        """
        :param path: The JSON file to write.
        """
        path.write_text(json.dumps(self.to_json()))

    @classmethod
    def read(cls, path: Path) -> Scenario:
        """
        :param path: A JSON file written by :meth:`write`.
        :return: The scenario.
        """
        return cls.from_json(json.loads(path.read_text()))

    def statistics(self) -> Dict[str, Any]:
        """
        :return: Sizes of the scenario, for the results.
        """
        kinds: Dict[str, int] = {}
        for perception in self.perceptions:
            for event in perception.knowledge_events:
                kinds[event.kind.value] = kinds.get(event.kind.value, 0) + 1
        return {
            "places": len(self.campus.places),
            "edges": self.campus.edge_count(),
            "rooms": len(self.campus.rooms()),
            "docks": len(self.campus.docks),
            "courses_with_room": len(self.course_rooms),
            "people_with_mailbox": len(self.mailboxes),
            "knowledge_events": kinds,
        }


def read_university_data(raw_file: Path) -> UniversityData:
    """
    Read the departments, courses, people and the facts the events depend on from the raw OWL2Bench data.

    :param raw_file: The raw OWL2Bench RDF/XML file.
    :return: The university data.
    """
    graph = rdflib.Graph()
    graph.parse(str(raw_file), format="xml")

    def iri(name: str) -> URIRef:
        return URIRef(OWL2BENCH + name)

    departments = {str(s) for s in graph.subjects(RDF.type, iri("Department"))}
    departments_by_college: Dict[str, List[str]] = {}
    for department in sorted(departments):
        for college in graph.objects(URIRef(department), iri("isPartOf")):
            departments_by_college.setdefault(str(college), []).append(department)
    courses_by_department = {
        department: sorted(str(c) for c in graph.objects(URIRef(department), iri("offerCourse")))
        for department in sorted(departments)
    }
    # People are typed explicitly with a subclass of Person, or only through the domain of a property they have
    # (most are typed Man or Woman, which are not declared subclasses of Person).
    person_classes = set(graph.transitive_subjects(RDFS.subClassOf, iri("Person")))
    person_properties = {p for c in person_classes for p in graph.subjects(RDFS.domain, c)}
    people = sorted(
        {str(s) for s, o in graph.subject_objects(RDF.type) if o in person_classes}
        | {str(s) for s, p, _ in graph if p in person_properties}
    )
    department_of_person: Dict[str, Optional[str]] = {}
    for person in people:
        linked = sorted(
            (str(predicate), str(value))
            for predicate, value in graph.predicate_objects(URIRef(person))
            if str(value) in departments
        )
        department_of_person[person] = linked[0][1] if linked else None
    students = sorted(str(s) for s in graph.subjects(iri("enrollIn"), None))
    courses_taken = {(str(s), str(o)) for s, o in graph.subject_objects(iri("takesCourse"))}
    t20 = URIRef(T20_CRICKET)
    return UniversityData(
        departments_by_college=departments_by_college,
        courses_by_department=courses_by_department,
        department_of_person=department_of_person,
        students=students,
        courses_taken=courses_taken,
        cricket_enthusiasts={str(s) for s in graph.subjects(iri("isCrazyAbout"), t20)},
        cricket_haters={str(s) for s in graph.subjects(iri("dislikes"), t20)},
    )


def generate_scenario(
    raw_file: Path,
    steps: int,
    seed: int,
    events_per_step: int = 3,
    event_mix: Optional[EventMix] = None,
    layout: Optional[CampusLayout] = None,
    robot: Optional[RobotSpecification] = None,
    university: Optional[UniversityData] = None,
) -> Scenario:
    """
    Generate the scenario.

    :param raw_file: The raw OWL2Bench RDF/XML file.
    :param steps: Number of steps.
    :param seed: Seed of the random generator.
    :param events_per_step: Knowledge events per step.
    :param event_mix: Relative frequencies of the events.
    :param layout: Campus layout parameters.
    :param robot: Robot parameters.
    :param university: The data read from ``raw_file``, if already read.
    :return: The scenario.
    """
    random_generator = random.Random(seed)
    event_mix = event_mix or EventMix()
    university = university or read_university_data(raw_file)
    campus = generate_campus(
        university.departments_by_college, university.courses_by_department, random_generator, layout
    )
    course_rooms = _assign_course_rooms(campus, university, random_generator)
    mailboxes = {
        person: campus.department_offices[department] if department else campus.mail_room
        for person, department in university.department_of_person.items()
    }
    for person in sorted(university.cricket_enthusiasts - set(mailboxes)):
        mailboxes[person] = campus.mail_room
    generator = _EventGenerator(university, event_mix, random_generator)
    colleges = sorted(university.departments_by_college)
    perceptions = []
    for step in range(steps):
        events = [generator.next_event() for _ in range(events_per_step)]
        for event in events:
            if isinstance(event, Enrollment):
                mailboxes[event.person] = campus.department_offices[event.department]
        perceptions.append(StepPerception(step, events, random_generator.choice(colleges)))
    return Scenario(
        seed=seed,
        steps=steps,
        events_per_step=events_per_step,
        campus=campus,
        course_rooms=course_rooms,
        mailboxes=mailboxes,
        robot=robot or RobotSpecification(),
        perceptions=perceptions,
    )


def _assign_course_rooms(
    campus: CampusMap, university: UniversityData, random_generator: random.Random
) -> Dict[str, str]:
    """
    :return: Course IRI to a classroom of the department that offers the course, filled round robin in seeded order.
    """
    course_rooms: Dict[str, str] = {}
    for department, courses in sorted(university.courses_by_department.items()):
        shuffled = list(courses)
        random_generator.shuffle(shuffled)
        classrooms = campus.department_classrooms[department]
        for index, course in enumerate(shuffled):
            course_rooms.setdefault(course, classrooms[index % len(classrooms)])
    return course_rooms


@dataclass
class _EventGenerator:
    """
    Draws knowledge events that each add a new fact.
    """

    university: UniversityData
    event_mix: EventMix
    random_generator: random.Random
    students: List[str] = field(init=False)
    department_of_student: Dict[str, Optional[str]] = field(init=False)
    courses_taken: Set[Tuple[str, str]] = field(init=False)
    possible_enthusiasts: List[str] = field(init=False)
    all_courses: List[str] = field(init=False)
    all_departments: List[str] = field(init=False)
    new_people: int = 0

    def __post_init__(self):
        self.students = list(self.university.students)
        self.department_of_student = {
            student: self.university.department_of_person.get(student) for student in self.students
        }
        self.courses_taken = set(self.university.courses_taken)
        excluded = self.university.cricket_enthusiasts | self.university.cricket_haters
        self.possible_enthusiasts = [
            person for person in sorted(self.university.department_of_person) if person not in excluded
        ]
        self.all_courses = sorted(
            {course for courses in self.university.courses_by_department.values() for course in courses}
        )
        self.all_departments = sorted(self.university.courses_by_department)

    def next_event(self) -> KnowledgeEvent:
        """
        :return: The next knowledge event.
        """
        kind = self.random_generator.choices(
            ("enrollment", "course_taking", "cricket_enthusiasm"),
            weights=(
                self.event_mix.enrollment,
                self.event_mix.course_taking,
                self.event_mix.cricket_enthusiasm,
            ),
        )[0]
        if kind == "cricket_enthusiasm" and self.possible_enthusiasts:
            return self._cricket_enthusiasm()
        if kind == "course_taking":
            event = self._course_taking()
            if event is not None:
                return event
        return self._enrollment()

    def _enrollment(self) -> Enrollment:
        person = f"{NEW_PERSON_PREFIX}{self.new_people}"
        self.new_people += 1
        department = self.random_generator.choice(self.all_departments)
        self.students.append(person)
        self.department_of_student[person] = department
        self.possible_enthusiasts.append(person)
        return Enrollment(person, department)

    def _course_taking(self) -> Optional[CourseTaking]:
        for _ in range(20):
            student = self.random_generator.choice(self.students)
            department = self.department_of_student.get(student)
            if department and self.random_generator.random() < self.event_mix.own_department_course_probability:
                course = self.random_generator.choice(self.university.courses_by_department[department])
            else:
                course = self.random_generator.choice(self.all_courses)
            if (student, course) not in self.courses_taken:
                self.courses_taken.add((student, course))
                return CourseTaking(student, course)
        return None

    def _cricket_enthusiasm(self) -> CricketEnthusiasm:
        index = self.random_generator.randrange(len(self.possible_enthusiasts))
        return CricketEnthusiasm(self.possible_enthusiasts.pop(index))
