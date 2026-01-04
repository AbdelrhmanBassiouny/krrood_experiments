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
    has_advisor: Set[Any] = field(default_factory=set)
    has_same_home_town_with: Set[Any] = field(default_factory=set)
    has_women_college: Set[Organization] = field(default_factory=set)
    is_affiliate_of: Set[Any] = field(default_factory=set)
    is_clerical_staff_of: Set[Organization] = field(default_factory=set)
    is_other_staff_of: Set[Organization] = field(default_factory=set)
    is_supporting_staff_of: Set[Organization] = field(default_factory=set)
    is_system_staff_of: Set[Organization] = field(default_factory=set)
    is_women_college_of: Set[Organization] = field(default_factory=set)
    knows: Set[Any] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))


T = TypeVar('T', bound=OWL2BenchOntology)