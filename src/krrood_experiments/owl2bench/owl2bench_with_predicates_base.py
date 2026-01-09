"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing_extensions import Optional, Set, TypeVar, Type, Any, Union

from krrood.entity_query_language.predicate import Symbol
from krrood.ontomatic.property_descriptor.mixins import IsBaseClass


@dataclass(eq=False)
class OWL2BenchOntology(Symbol, IsBaseClass):
    """Base class for OWL2Bench"""
    has_code: Optional[Any] = field(kw_only=True, default=None)
    has_id: Optional[Any] = field(kw_only=True, default=None)
    has_name: Optional[Any] = field(kw_only=True, default=None)
    has_office_number: Optional[Any] = field(kw_only=True, default=None)
    has_publication_date: Optional[Any] = field(kw_only=True, default=None)
    has_research_interest: Optional[Any] = field(kw_only=True, default=None)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)
    has_same_home_town_with: Set[OWL2BenchOntology] = field(kw_only=True, default_factory=set)
    is_affiliate_of: Set[OWL2BenchOntology] = field(kw_only=True, default_factory=set)
    knows: Set[OWL2BenchOntology] = field(kw_only=True, default_factory=set)

    def __hash__(self):
        return hash(id(self))


T = TypeVar('T', bound=OWL2BenchOntology)