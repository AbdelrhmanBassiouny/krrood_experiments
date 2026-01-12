"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing_extensions import Optional, Set, TypeVar, Type, Any, Union

from krrood.entity_query_language.predicate import Symbol
from krrood.ontomatic.property_descriptor.mixins import IsBaseClass
from krrood.class_diagrams.utils import Role

@dataclass(eq=False)
class OWL2BenchThing(Symbol, IsBaseClass):
    """Base class for OWL2Bench"""
    has_code: Optional[Any] = field(kw_only=True, default=None)
    has_id: Optional[Any] = field(kw_only=True, default=None)
    has_name: Optional[Any] = field(kw_only=True, default=None)
    has_office_number: Optional[Any] = field(kw_only=True, default=None)
    has_publication_date: Optional[Any] = field(kw_only=True, default=None)
    has_research_interest: Optional[Any] = field(kw_only=True, default=None)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)
    has_advisor: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    has_employee: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    has_head: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    has_same_home_town_with: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    has_women_college: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_affiliate_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_assistant_professor_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_associate_professor_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_clerical_staff_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_full_professor_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_lecturer_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_other_staff_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_post_doc_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_professor_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_research_assistant_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_supporting_staff_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_system_staff_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_visiting_professor_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    is_women_college_of: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    knows: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)

    def __hash__(self):
        return hash(id(self))


T = TypeVar('T', bound=OWL2BenchThing)