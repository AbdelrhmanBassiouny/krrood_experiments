"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import Type, List, Optional, Tuple

from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.ontomatic.property_descriptor.mixins import (
HasInverseProperty,
TransitiveProperty,
HasEquivalentProperties,
HasDisjointProperties,
SymmetricProperty,
ASymmetricProperty,
ReflexiveProperty,
IrreflexiveProperty,
RoleForMixin,
HasChainAxioms
)


# Property descriptor classes (object properties)
@dataclass(eq=False)
class Advisor(PropertyDescriptor):
    """is being advised by"""


@dataclass(eq=False)
class AffiliateOf(PropertyDescriptor):
    """is affiliated with"""


@dataclass(eq=False)
class AffiliatedOrganizationOf(PropertyDescriptor):
    """is affiliated with"""


@dataclass(eq=False)
class DegreeFrom(PropertyDescriptor, HasInverseProperty):
    """has a degree from"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAlumnus]]:
        if cls is DegreeFrom:
            return HasAlumnus
        return None


@dataclass(eq=False)
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """has as an alumnus"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[DegreeFrom]]:
        if cls is HasAlumnus:
            return DegreeFrom
        return None


@dataclass(eq=False)
class ListedCourse(PropertyDescriptor):
    """lists as a course"""


@dataclass(eq=False)
class Member(PropertyDescriptor, HasInverseProperty):
    """has as a member"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[MemberOf]]:
        if cls is Member:
            return MemberOf
        return None


@dataclass(eq=False)
class MemberOf(PropertyDescriptor, HasInverseProperty):
    """member of"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[Member]]:
        if cls is MemberOf:
            return Member
        return None


@dataclass(eq=False)
class OrgPublication(PropertyDescriptor):
    """publishes"""


@dataclass(eq=False)
class PublicationAuthor(PropertyDescriptor):
    """was written by"""


@dataclass(eq=False)
class PublicationResearch(PropertyDescriptor):
    """is about"""


@dataclass(eq=False)
class ResearchProject(PropertyDescriptor):
    """has as a research project"""


@dataclass(eq=False)
class RoleFor(PropertyDescriptor, RoleForMixin):
    """is a role for"""


@dataclass(eq=False)
class SoftwareDocumentation(PropertyDescriptor):
    """is documented in"""


@dataclass(eq=False)
class SubOrganizationOf(PropertyDescriptor, TransitiveProperty):
    """is part of"""


@dataclass(eq=False)
class TakesCourse(PropertyDescriptor):
    """is taking"""


@dataclass(eq=False)
class TeacherOf(PropertyDescriptor):
    """teaches"""


@dataclass(eq=False)
class TeachingAssistantOf(PropertyDescriptor):
    """is a teaching assistant for"""


@dataclass(eq=False)
class DoctoralDegreeFrom(DegreeFrom):
    """has a doctoral degree from"""


@dataclass(eq=False)
class MastersDegreeFrom(DegreeFrom):
    """has a masters degree from"""


@dataclass(eq=False)
class UndergraduateDegreeFrom(DegreeFrom):
    """has an undergraduate degree from"""


@dataclass(eq=False)
class WorksFor(MemberOf):
    """Works For"""


@dataclass(eq=False)
class HeadOf(WorksFor):
    """is the head of"""


