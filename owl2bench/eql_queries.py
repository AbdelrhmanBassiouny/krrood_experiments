from dataclasses import dataclass
from typing import Callable

from krrood.entity_query_language.entity import variable, contains, set_of
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.symbolic import (
    SymbolicExpression,
)

from owl2bench.models import World, Person
from . import sparql_queries


@dataclass
class EQLQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    query: Callable[[World], SymbolicExpression]
    """
    A function that takes a World and returns an EQL Query.
    """


def q1_generator(world: World):
    p1 = variable(Person, world.persons)
    p2 = variable(Person, world.persons)
    query = an(set_of((p1, p2)), contains(p1.knows, p2))
    return query


q1 = EQLQuery(
    sparql_queries.q1,
    query=q1_generator,
)
