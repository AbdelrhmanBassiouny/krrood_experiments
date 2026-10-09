"""
Tests that one EQL evaluation calls each predicate and symbolic function once per distinct argument object, with the
answers unchanged (the earlier KRROOD version, patched by earlier_krrood_memoization.patch).
"""

from dataclasses import dataclass

from krrood.entity_query_language.entity import entity, variable
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.predicate import Predicate, symbolic_function

REACH = 10.0

CALLS = []


@dataclass(eq=False)
class Place:
    distance: float


@dataclass(eq=False)
class Visit:
    place: Place


@dataclass(eq=False)
class IsNear(Predicate):
    place: Place

    def __call__(self):
        CALLS.append(self.place)
        return self.place.distance <= REACH


@symbolic_function
def travel_time(place):
    CALLS.append(place)
    return place.distance


def visits():
    CALLS.clear()
    places = [Place(REACH - 1), Place(REACH), Place(REACH + 1)]
    return [Visit(place) for place in places for _ in range(2)]


def test_predicate_is_called_once_per_distinct_argument():
    domain = visits()
    v = variable(Visit, domain=domain)
    answers = list(an(entity(v).where(IsNear(v.place))).evaluate())
    assert answers == [visit for visit in domain if visit.place.distance <= REACH]
    assert len(CALLS) == len({id(visit.place) for visit in domain})


def test_symbolic_function_is_called_once_per_distinct_argument():
    domain = visits()
    v = variable(Visit, domain=domain)
    answers = list(an(entity(v).where(travel_time(v.place) < REACH)).evaluate())
    assert answers == [visit for visit in domain if visit.place.distance < REACH]
    assert len(CALLS) == len({id(visit.place) for visit in domain})
