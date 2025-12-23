from dataclasses import dataclass
from typing import Callable

from krrood.entity_query_language.entity import variable, contains, set_of
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.symbolic import (
    SymbolicExpression,
)


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
