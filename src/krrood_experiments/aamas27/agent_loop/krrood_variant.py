"""
Variant 1, KRROOD: the agent's objects are its knowledge base.

* Setup loads the OWL2Bench data with the Ontomatic instance loader exactly as the loading benchmark does
  (:func:`~krrood_experiments.owl2bench.ontomatic.helpers.load_instances_for_owl2bench_with_predicates`) and attaches
  the application data to the loaded objects (``course.taught_in``, ``person.mailbox``).
* Perceiving a fact is an assignment through a property descriptor, which forward-chains the property characteristics
  (sub-properties, inverses, chains, transitivity) on the spot. A new person is a new ``Person`` object with a
  ``Student`` role.
* The decision queries are EQL queries over the live objects that call the robot's procedures directly: the predicate
  :class:`CanReach` and the symbolic function :func:`travel_time`. ``T20CricketFan`` membership is derived on request
  by evaluating the class axiom of the generated model (``T20CricketFan.axiom(person)``) inside the query, because this
  version creates role objects for defined classes only when loading.

Events name individuals by IRI, so the variant resolves IRIs to objects (the registry of the loader); this is the only
mapping code it has. ``order_by`` of this KRROOD version sorts only within one binding group, so the candidates are
ordered by the shared policy, as in the other variants.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Tuple, Type

from krrood.entity_query_language.entity import contains, set_of, variable, variable_from
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.predicate import Predicate, symbolic_function
from rdflib import URIRef

from ...owl2bench.ontomatic import owl2bench_with_predicates as model
from ...owl2bench.ontomatic.helpers import load_instances_for_owl2bench_with_predicates
from ..environment import UNREASONED_FILE
from .campus import Place
from .events import T20_CRICKET, CourseTaking, CricketEnthusiasm, Enrollment, StepPerception
from .loop import AgentVariant
from .measurement import (
    MAPPING,
    PROCEDURE_INTEGRATION,
    StepMeter,
    boundary,
    function_body_source,
    query_size,
)
from .robot import HandoutCandidate, Robot, TicketCandidate, can_reach, travel_seconds


@boundary(PROCEDURE_INTEGRATION)
@dataclass(eq=False)
class CanReach(Predicate):
    """
    The robot can drive to the room and from there to a charging dock with its remaining battery.
    """

    robot: Robot
    """
    The robot, whose pose and battery are read when the predicate is evaluated.
    """
    room: Place
    """
    The room.
    """

    def __call__(self) -> bool:
        return can_reach(self.robot, self.room)


@boundary(PROCEDURE_INTEGRATION)
@symbolic_function
def travel_time(robot: Robot, room: Place) -> float:
    """
    :param robot: The robot.
    :param room: A room.
    :return: The driving time in seconds.
    """
    return travel_seconds(robot, room)


@dataclass
class KrroodVariant(AgentVariant):
    """
    The knowledge is the application's own objects.
    """

    name: ClassVar[str] = "krrood"
    description: ClassVar[str] = (
        "KRROOD objects are the knowledge base: descriptor assignment with forward chaining, EQL queries that call "
        "the robot's predicate and function on the live objects."
    )
    boundary_helpers: ClassVar[Tuple] = (CanReach, travel_time)
    registry: Any = field(default=None, init=False)
    """
    The loader's registry from IRI to the objects of an individual.
    """
    t20_cricket: Any = field(default=None, init=False)
    """
    The ``T20Cricket`` individual.
    """

    def setup(self) -> Dict[str, Any]:
        start = time.perf_counter()
        self.registry = load_instances_for_owl2bench_with_predicates(str(UNREASONED_FILE))
        load_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self._attach_application_data()
        self.t20_cricket = self._resolve(T20_CRICKET, model.Interest)
        attach_seconds = time.perf_counter() - start
        return {
            "seconds": {"load_and_reasoning": load_seconds, "application_data": attach_seconds},
            "total_seconds": load_seconds + attach_seconds,
            "individuals": len(self.registry._by_uri),
        }

    @boundary(MAPPING)
    def _attach_application_data(self) -> None:
        """
        Attach the course rooms and the mail boxes to the loaded objects.
        """
        campus = self.scenario.campus
        for iri, instances in self.registry._by_uri.items():
            for instance in instances:
                if isinstance(instance, model.Course):
                    instance.taught_in = campus.place(self.scenario.course_rooms[str(iri)])
                elif isinstance(instance, model.Person):
                    instance.mailbox = campus.place(self.scenario.mailbox_of(str(iri)))

    @boundary(MAPPING)
    def _resolve(self, iri: str, cls: Type) -> Any:
        """
        :param iri: The IRI of an individual.
        :param cls: The class of the wanted object.
        :return: The first object of the individual that is an instance of the class.
        """
        return next(instance for instance in self.registry.resolve(iri) if isinstance(instance, cls))

    @boundary(MAPPING)
    def _register(self, iri: str, *instances: Any) -> None:
        """
        Make new objects findable by their IRI.

        :param iri: The IRI.
        :param instances: The objects of the individual.
        """
        self.registry._by_uri[URIRef(iri)].extend(instances)

    def perceive(self, perception: StepPerception, meter: StepMeter) -> None:
        for event in perception.knowledge_events:
            if isinstance(event, Enrollment):
                with meter.phase("mapping"):
                    department = self._resolve(event.department, model.Department)
                with meter.phase("update"):
                    person = model.Person(uri=event.person)
                    student = model.Student(person=person)
                    person.mailbox = self.scenario.campus.place(self.scenario.mailbox_of(event.person))
                    student.enroll_in.add(department)
                meter.statements_inserted += 3
                with meter.phase("mapping"):
                    self._register(event.person, person, student)
            elif isinstance(event, CourseTaking):
                with meter.phase("mapping"):
                    student = self._resolve(event.student, model.Student)
                    course = self._resolve(event.course, model.Course)
                with meter.phase("update"):
                    student.takes_course.add(course)
                meter.statements_inserted += 1
            elif isinstance(event, CricketEnthusiasm):
                with meter.phase("mapping"):
                    person = self._resolve(event.person, model.Person)
                with meter.phase("update"):
                    person.is_crazy_about.add(self.t20_cricket)
                meter.statements_inserted += 1

    def handout_query(self, college: model.Organization):
        """
        :param college: The requested college.
        :return: The students who are members of the college, the courses they take whose room the robot can reach,
         and the driving times.
        """
        student = variable(model.Student, domain=None)
        course = variable_from(student.takes_course)
        driving_time = travel_time(self.robot, course.taught_in)
        query = an(
            set_of(student, course, driving_time).where(
                contains(student.is_member_of, college),
                CanReach(self.robot, course.taught_in),
            )
        )
        return query, student, course, driving_time

    def ticket_query(self):
        """
        :return: The T20 cricket fans whose mail box the robot can reach, and the driving times.
        """
        person = variable(model.Person, domain=None)
        driving_time = travel_time(self.robot, person.mailbox)
        query = an(
            set_of(person, driving_time).where(
                *model.T20CricketFan.axiom(person),
                CanReach(self.robot, person.mailbox),
            )
        )
        return query, person, driving_time

    def handout_candidates(self, college: str, meter: StepMeter) -> List[HandoutCandidate]:
        with meter.phase("mapping"):
            college_object = self._resolve(college, model.Organization)
        with meter.phase("query"):
            query, student, course, driving_time = self.handout_query(college_object)
            return [
                HandoutCandidate(
                    result[student].uri,
                    result[course].uri,
                    result[course].taught_in.identifier,
                    result[driving_time],
                )
                for result in query.evaluate()
            ]

    def ticket_candidates(self, meter: StepMeter) -> List[TicketCandidate]:
        with meter.phase("query"):
            query, person, driving_time = self.ticket_query()
            return [
                TicketCandidate(result[person].uri, result[person].mailbox.identifier, result[driving_time])
                for result in query.evaluate()
            ]

    @classmethod
    def query_texts(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "handouts": query_size(function_body_source(cls.handout_query, drop_last=True), "eql"),
            "tickets": query_size(function_body_source(cls.ticket_query, drop_last=True), "eql"),
        }
