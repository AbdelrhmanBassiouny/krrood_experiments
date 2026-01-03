"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC
from typing_extensions import Optional, Set, TypeVar, Type, Any, Union

from krrood.entity_query_language.predicate import Symbol


@dataclass(eq=False)
class OWL2BenchOntology(Symbol, ABC):
    """Base class for OWL2Bench"""
    has_code: Optional[Any] = field(kw_only=True, default=None)
    has_id: Optional[Any] = field(kw_only=True, default=None)
    has_name: Optional[Any] = field(kw_only=True, default=None)
    has_office_number: Optional[Any] = field(kw_only=True, default=None)
    has_publication_date: Optional[Any] = field(kw_only=True, default=None)
    has_research_interest: Optional[Any] = field(kw_only=True, default=None)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)

    def __hash__(self):
        return hash(id(self))


T = TypeVar('T', bound=OWL2BenchOntology)