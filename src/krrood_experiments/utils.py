from __future__ import annotations

from typing import Set, Type, List

from krrood.class_diagrams.utils import Role, issubclass_or_role
from krrood.entity_query_language.entity import variable
from krrood.entity_query_language.symbolic import Variable
from krrood.utils import inheritance_path_length
from rdflib import URIRef
from typing_extensions import Type, Set, List, Iterable
from dataclasses import fields, dataclass, field


def get_non_class_attribute_names_of_instance(instance: Type) -> Set[str]:
    """Get non-class fields of an instance."""
    return {f for f in dir(instance) if not f.startswith("_")} - set(
        [f for f in dir(type(instance)) if not f.startswith("_")]
        + [f.name for f in fields(type(instance))]
    )


def get_most_specific_types(types: Iterable[type]) -> List[type]:
    ts = list(dict.fromkeys(types))  # stable unique
    keep = []
    for t in ts:
        # drop t if there exists u that is a strict subtype of t
        if not any(u is not t and issubclass_or_role(u, t) for u in ts):
            keep.append(t)
    return keep


def not_none_inheritance_path_length(child: Type, parent: Type) -> int:
    length = inheritance_path_length(child, parent)
    if length is None:
        return float("inf")
    return length


@dataclass
class AnonymousClass:
    """Represents an anonymous class that is yet to be identified"""

    uri: URIRef
    types: Set[Type] = field(default_factory=set)
    final_sorted_types: List[Type] = field(default_factory=list)

    def add_type(self, cls: Type):
        self.types.add(cls)

    def __hash__(self):
        return hash(self.uri)

    def __eq__(self, other):
        return self.uri == other.uri


def get_super_axiom_and_candidate_var(
    owner: Type, cls: Type, candidate
) -> tuple[list, Variable]:
    candidate_var = (
        candidate
        if isinstance(candidate, Variable)
        else variable(AnonymousClass, [candidate])
    )

    sup = super(owner, cls)
    axiom = getattr(sup, "axiom", None)
    super_axiom = axiom(candidate_var) if axiom else ()

    return super_axiom, candidate_var
