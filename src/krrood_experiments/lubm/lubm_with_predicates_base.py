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
class UnivBenchOntologyThing(Symbol, IsBaseClass):
    """Base class for Univ-bench Ontology"""
    # name
    name: Optional[str] = field(kw_only=True, default=None)
    # office room No.
    office_number: Optional[int] = field(kw_only=True, default=None)
    # is researching
    research_interest: Optional[str] = field(kw_only=True, default=None)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)

    def __hash__(self):
        return hash(id(self))


T = TypeVar('T', bound=UnivBenchOntologyThing)