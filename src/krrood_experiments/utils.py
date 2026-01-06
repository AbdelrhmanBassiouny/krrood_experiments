from krrood.class_diagrams.utils import Role
from typing_extensions import Type, Set, List, Iterable
from dataclasses import fields


def get_non_class_attribute_names_of_instance(instance: Type) -> Set[str]:
    """Get non-class fields of an instance."""
    return {f for f in dir(instance) if not f.startswith("_")} - set(
        [f for f in dir(type(instance)) if not f.startswith("_")]
        + [f.name for f in fields(type(instance))]
    )


def issubclass_or_role(subtype: Type, supertype: Type) -> bool:
    return issubclass(subtype, supertype) or (
        issubclass(subtype, Role)
        and issubclass(subtype.get_role_taker_type(), supertype)
    )


def get_most_specific_types(types: Iterable[type]) -> List[type]:
    ts = list(dict.fromkeys(types))  # stable unique
    keep = []
    for t in ts:
        # drop t if there exists u that is a strict subtype of t
        if not any(u is not t and issubclass_or_role(u, t) for u in ts):
            keep.append(t)
    return keep
