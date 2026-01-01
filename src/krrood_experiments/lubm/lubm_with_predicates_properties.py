"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import Type

from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.ontomatic.property_descriptor.mixins import HasInverseProperty, TransitiveProperty


# Property descriptor classes (object properties)
@dataclass
class Advisor(PropertyDescriptor):
    """is being advised by"""


@dataclass
class AffiliateOf(PropertyDescriptor):
    """is affiliated with"""


@dataclass
class AffiliatedOrganizationOf(PropertyDescriptor):
    """is affiliated with"""


@dataclass
class DegreeFrom(PropertyDescriptor, HasInverseProperty):
    """has a degree from"""
    @classmethod
    def get_inverse(cls) -> Type[HasAlumnus]:
        return HasAlumnus


@dataclass
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """has as an alumnus"""
    @classmethod
    def get_inverse(cls) -> Type[DegreeFrom]:
        return DegreeFrom


@dataclass
class ListedCourse(PropertyDescriptor):
    """lists as a course"""


@dataclass
class Member(PropertyDescriptor, HasInverseProperty):
    """has as a member"""
    @classmethod
    def get_inverse(cls) -> Type[MemberOf]:
        return MemberOf


@dataclass
class MemberOf(PropertyDescriptor, HasInverseProperty):
    """member of"""
    @classmethod
    def get_inverse(cls) -> Type[Member]:
        return Member


@dataclass
class OrgPublication(PropertyDescriptor):
    """publishes"""


@dataclass
class PlaysRole(PropertyDescriptor, HasInverseProperty):
    """plays a role of"""
    @classmethod
    def get_inverse(cls) -> Type[RoleFor]:
        return RoleFor


@dataclass
class PublicationAuthor(PropertyDescriptor):
    """was written by"""


@dataclass
class PublicationResearch(PropertyDescriptor):
    """is about"""


@dataclass
class ResearchProject(PropertyDescriptor):
    """has as a research project"""


@dataclass
class RoleFor(PropertyDescriptor, HasInverseProperty):
    """is a role for"""
    @classmethod
    def get_inverse(cls) -> Type[PlaysRole]:
        return PlaysRole


@dataclass
class SoftwareDocumentation(PropertyDescriptor):
    """is documented in"""


@dataclass
class SubOrganizationOf(PropertyDescriptor, TransitiveProperty):
    """is part of"""


@dataclass
class TakesCourse(PropertyDescriptor):
    """is taking"""


@dataclass
class TeacherOf(PropertyDescriptor):
    """teaches"""


@dataclass
class TeachingAssistantOf(PropertyDescriptor):
    """is a teaching assistant for"""


@dataclass
class DoctoralDegreeFrom(DegreeFrom):
    """has a doctoral degree from"""


@dataclass
class MastersDegreeFrom(DegreeFrom):
    """has a masters degree from"""


@dataclass
class UndergraduateDegreeFrom(DegreeFrom):
    """has an undergraduate degree from"""


@dataclass
class WorksFor(MemberOf):
    """Works For"""


@dataclass
class HeadOf(WorksFor):
    """is the head of"""


