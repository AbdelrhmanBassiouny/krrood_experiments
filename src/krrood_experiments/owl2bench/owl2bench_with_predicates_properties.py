"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import Type, List

from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.ontomatic.property_descriptor.mixins import (
HasInverseProperty,
TransitiveProperty,
HasEquivalentProperties,
HasDisjointProperties,
SymmetricProperty,
ASymmetricProperty,
ReflexiveProperty,
IrreflexiveProperty
)


# Property descriptor classes (object properties)
@dataclass(eq=False)
class Dislikes(PropertyDescriptor, HasDisjointProperties):
    """Dislikes"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Likes]


@dataclass(eq=False)
class EnrollFor(PropertyDescriptor):
    """EnrollFor"""


@dataclass(eq=False)
class EvaluatedBy(PropertyDescriptor, HasInverseProperty):
    """EvaluatedBy"""

    @classmethod
    def get_inverse(cls) -> Type[Evaluates]:
        return Evaluates


@dataclass(eq=False)
class Evaluates(PropertyDescriptor, HasInverseProperty):
    """Evaluates"""

    @classmethod
    def get_inverse(cls) -> Type[EvaluatedBy]:
        return EvaluatedBy


@dataclass(eq=False)
class HasAdvisor(PropertyDescriptor, HasEquivalentProperties):
    """HasAdvisor"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsAdvisedBy]


@dataclass(eq=False)
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """HasAlumnus"""

    @classmethod
    def get_inverse(cls) -> Type[HasDegreeFrom]:
        return HasDegreeFrom


@dataclass(eq=False)
class HasAuthor(PropertyDescriptor):
    """HasAuthor"""


@dataclass(eq=False)
class HasCollaborationWith(PropertyDescriptor, SymmetricProperty, IrreflexiveProperty):
    """HasCollaborationWith"""


@dataclass(eq=False)
class HasCollegeDiscipline(PropertyDescriptor, HasDisjointProperties):
    """HasCollegeDiscipline"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasMajor]


@dataclass(eq=False)
class HasDean(PropertyDescriptor, HasInverseProperty):
    """HasDean"""

    @classmethod
    def get_inverse(cls) -> Type[IsDeanOf]:
        return IsDeanOf


@dataclass(eq=False)
class HasDegreeFrom(PropertyDescriptor, HasInverseProperty):
    """HasDegreeFrom"""

    @classmethod
    def get_inverse(cls) -> Type[HasAlumnus]:
        return HasAlumnus


@dataclass(eq=False)
class HasEvaluationCommittee(PropertyDescriptor):
    """HasEvaluationCommittee"""


@dataclass(eq=False)
class HasMajor(PropertyDescriptor, HasDisjointProperties):
    """HasMajor"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasCollegeDiscipline]


@dataclass(eq=False)
class HasMember(PropertyDescriptor, HasInverseProperty):
    """HasMember"""

    @classmethod
    def get_inverse(cls) -> Type[IsMemberOf]:
        return IsMemberOf


@dataclass(eq=False)
class HasPart(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasPart"""

    @classmethod
    def get_inverse(cls) -> Type[IsPartOf]:
        return IsPartOf

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasSubOrganization]


@dataclass(eq=False)
class HasProgram(PropertyDescriptor):
    """HasProgram"""


@dataclass(eq=False)
class HasSameHomeTownWith(PropertyDescriptor, TransitiveProperty, SymmetricProperty):
    """HasSameHomeTownWith"""


@dataclass(eq=False)
class HasSubOrganization(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasSubOrganization"""

    @classmethod
    def get_inverse(cls) -> Type[IsSubOrganizationOf]:
        return IsSubOrganizationOf

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasPart]


@dataclass(eq=False)
class HasWork(PropertyDescriptor):
    """HasWork"""


@dataclass(eq=False)
class IsAdvisedBy(PropertyDescriptor, HasEquivalentProperties):
    """IsAdvisedBy"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasAdvisor]


@dataclass(eq=False)
class IsAffiliateOf(PropertyDescriptor):
    """IsAffiliateOf"""


@dataclass(eq=False)
class IsAffiliatedOrganizationOf(PropertyDescriptor, ASymmetricProperty, IrreflexiveProperty):
    """IsAffiliatedOrganizationOf"""


@dataclass(eq=False)
class IsDeanOf(PropertyDescriptor, HasInverseProperty):
    """IsDeanOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasDean]:
        return HasDean


@dataclass(eq=False)
class IsMemberOf(PropertyDescriptor, HasInverseProperty):
    """IsMemberOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasMember]:
        return HasMember


@dataclass(eq=False)
class IsPartOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsPartOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasPart]:
        return HasPart

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsSubOrganizationOf]


@dataclass(eq=False)
class IsStudentOf(PropertyDescriptor, HasInverseProperty):
    """IsStudentOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasStudent]:
        return HasStudent


@dataclass(eq=False)
class IsSubOrganizationOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsSubOrganizationOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasSubOrganization]:
        return HasSubOrganization

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsPartOf]


@dataclass(eq=False)
class IsTaughtBy(PropertyDescriptor, HasInverseProperty):
    """IsTaughtBy"""

    @classmethod
    def get_inverse(cls) -> Type[TeachesCourse]:
        return TeachesCourse


@dataclass(eq=False)
class IsTeachingAssistantOf(PropertyDescriptor):
    """IsTeachingAssistantOf"""


@dataclass(eq=False)
class Knows(PropertyDescriptor):
    """Knows"""


@dataclass(eq=False)
class Likes(PropertyDescriptor, HasDisjointProperties, IrreflexiveProperty):
    """Likes"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Dislikes]


@dataclass(eq=False)
class OfferCourse(PropertyDescriptor):
    """OfferCourse"""


@dataclass(eq=False)
class OrgPublication(PropertyDescriptor):
    """OrgPublication"""


@dataclass(eq=False)
class PlaysRole(PropertyDescriptor, HasInverseProperty):
    """plays a role of"""

    @classmethod
    def get_inverse(cls) -> Type[RoleFor]:
        return RoleFor


@dataclass(eq=False)
class PublicationResearch(PropertyDescriptor):
    """PublicationResearch"""


@dataclass(eq=False)
class RoleFor(PropertyDescriptor, HasInverseProperty):
    """is a role for"""

    @classmethod
    def get_inverse(cls) -> Type[PlaysRole]:
        return PlaysRole


@dataclass(eq=False)
class TakesCourse(PropertyDescriptor):
    """TakesCourse"""


@dataclass(eq=False)
class WorksFor(PropertyDescriptor, HasInverseProperty):
    """WorksFor"""

    @classmethod
    def get_inverse(cls) -> Type[HasEmployee]:
        return HasEmployee


@dataclass(eq=False)
class EnrollIn(IsStudentOf):
    """EnrollIn"""


@dataclass(eq=False)
class HasCollege(HasSubOrganization, HasInverseProperty):
    """HasCollege"""

    @classmethod
    def get_inverse(cls) -> Type[IsCollegeOf]:
        return IsCollegeOf


@dataclass(eq=False)
class HasCommitteeMembers(HasMember):
    """HasCommitteeMembers"""


@dataclass(eq=False)
class HasDepartment(HasSubOrganization, HasInverseProperty):
    """HasDepartment"""

    @classmethod
    def get_inverse(cls) -> Type[IsDepartmentOf]:
        return IsDepartmentOf


@dataclass(eq=False)
class HasDoctoralDegreeFrom(HasDegreeFrom):
    """HasDoctoralDegreeFrom"""


@dataclass(eq=False)
class HasEmployee(HasMember, HasInverseProperty):
    """HasEmployee"""

    @classmethod
    def get_inverse(cls) -> Type[WorksFor]:
        return WorksFor


@dataclass(eq=False)
class HasEmployeeEvaluationCommittee(HasEvaluationCommittee):
    """HasEmployeeEvaluationCommittee"""


@dataclass(eq=False)
class HasMasterDegreeFrom(HasDegreeFrom):
    """HasMasterDegreeFrom"""


@dataclass(eq=False)
class HasPGProgram(HasProgram):
    """HasPGProgram"""


@dataclass(eq=False)
class HasPhDProgram(HasProgram):
    """HasPhDProgram"""


@dataclass(eq=False)
class HasResearchGroup(HasSubOrganization, HasInverseProperty):
    """HasResearchGroup"""

    @classmethod
    def get_inverse(cls) -> Type[IsResearchGroupOf]:
        return IsResearchGroupOf


@dataclass(eq=False)
class HasResearchProject(HasWork):
    """HasResearchProject"""


@dataclass(eq=False)
class HasStudent(HasMember, HasInverseProperty):
    """HasStudent"""

    @classmethod
    def get_inverse(cls) -> Type[IsStudentOf]:
        return IsStudentOf


@dataclass(eq=False)
class HasStudentEvaluationCommittee(HasEvaluationCommittee):
    """HasStudentEvaluationCommittee"""


@dataclass(eq=False)
class HasUGProgram(HasProgram):
    """HasUGProgram"""


@dataclass(eq=False)
class HasUndergraduateDegreeFrom(HasDegreeFrom):
    """HasUndergraduateDegreeFrom"""


@dataclass(eq=False)
class IsCollegeOf(IsSubOrganizationOf, HasInverseProperty):
    """IsCollegeOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasCollege]:
        return HasCollege


@dataclass(eq=False)
class IsDepartmentOf(IsSubOrganizationOf, HasInverseProperty):
    """IsDepartmentOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasDepartment]:
        return HasDepartment


@dataclass(eq=False)
class IsFacultyOf(WorksFor, HasInverseProperty):
    """IsFacultyOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasFaculty]:
        return HasFaculty


@dataclass(eq=False)
class IsResearchAssistantOf(WorksFor, HasInverseProperty):
    """IsResearchAssistantOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasResearchAssistant]:
        return HasResearchAssistant


@dataclass(eq=False)
class IsResearchGroupOf(IsSubOrganizationOf, HasInverseProperty):
    """IsResearchGroupOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasResearchGroup]:
        return HasResearchGroup


@dataclass(eq=False)
class IsSupportingStaffOf(WorksFor):
    """IsSupportingStaffOf"""


@dataclass(eq=False)
class Loves(Likes):
    """Loves"""


@dataclass(eq=False)
class TeachesCourse(HasWork, HasInverseProperty):
    """TeachesCourse"""

    @classmethod
    def get_inverse(cls) -> Type[IsTaughtBy]:
        return IsTaughtBy


@dataclass(eq=False)
class HasFaculty(HasEmployee, HasInverseProperty):
    """HasFaculty"""

    @classmethod
    def get_inverse(cls) -> Type[IsFacultyOf]:
        return IsFacultyOf


@dataclass(eq=False)
class HasResearchAssistant(HasEmployee, HasInverseProperty):
    """HasResearchAssistant"""

    @classmethod
    def get_inverse(cls) -> Type[IsResearchAssistantOf]:
        return IsResearchAssistantOf


@dataclass(eq=False)
class HasSupportingStaff(HasEmployee):
    """HasSupportingStaff"""


@dataclass(eq=False)
class HasThesisEvaluationCommittee(HasStudentEvaluationCommittee):
    """HasThesisEvaluationCommittee"""


@dataclass(eq=False)
class HasWomenCollege(HasCollege):
    """HasWomenCollege"""


@dataclass(eq=False)
class IsClericalStaffOf(IsSupportingStaffOf):
    """IsClericalStaffOf"""


@dataclass(eq=False)
class IsCrazyAbout(Loves):
    """IsCrazyAbout"""


@dataclass(eq=False)
class IsLecturerOf(IsFacultyOf, HasInverseProperty):
    """IsLecturerOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasLecturer]:
        return HasLecturer


@dataclass(eq=False)
class IsOtherStaffOf(IsSupportingStaffOf):
    """IsOtherStaffOf"""


@dataclass(eq=False)
class IsPostDocOf(IsFacultyOf, HasInverseProperty):
    """IsPostDocOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasPostDoc]:
        return HasPostDoc


@dataclass(eq=False)
class IsProfessorOf(IsFacultyOf, HasInverseProperty):
    """IsProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasProfessor]:
        return HasProfessor


@dataclass(eq=False)
class IsSystemStaffOf(IsSupportingStaffOf):
    """IsSystemStaffOf"""


@dataclass(eq=False)
class IsWomenCollegeOf(IsCollegeOf):
    """IsWomenCollegeOf"""


@dataclass(eq=False)
class HasClericalStaff(HasSupportingStaff):
    """HasClericalStaff"""


@dataclass(eq=False)
class HasLecturer(HasFaculty, HasInverseProperty):
    """HasLecturer"""

    @classmethod
    def get_inverse(cls) -> Type[IsLecturerOf]:
        return IsLecturerOf


@dataclass(eq=False)
class HasOtherStaff(HasSupportingStaff):
    """HasOtherStaff"""


@dataclass(eq=False)
class HasPostDoc(HasFaculty, HasInverseProperty):
    """HasPostDoc"""

    @classmethod
    def get_inverse(cls) -> Type[IsPostDocOf]:
        return IsPostDocOf


@dataclass(eq=False)
class HasProfessor(HasFaculty, HasInverseProperty):
    """HasProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsProfessorOf]:
        return IsProfessorOf


@dataclass(eq=False)
class HasSystemStaff(HasSupportingStaff):
    """HasSystemStaff"""


@dataclass(eq=False)
class IsAssistantProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssistantProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasAssistantProfessor]:
        return HasAssistantProfessor


@dataclass(eq=False)
class IsAssociateProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssociateProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasAssociateProfessor]:
        return HasAssociateProfessor


@dataclass(eq=False)
class IsFullProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsFullProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasFullProfessor]:
        return HasFullProfessor


@dataclass(eq=False)
class IsVisitingProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsVisitingProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasVisitingProfessor]:
        return HasVisitingProfessor


@dataclass(eq=False)
class HasAssistantProfessor(HasProfessor, HasInverseProperty):
    """HasAssistantProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsAssistantProfessorOf]:
        return IsAssistantProfessorOf


@dataclass(eq=False)
class HasAssociateProfessor(HasProfessor, HasInverseProperty):
    """HasAssociateProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsAssociateProfessorOf]:
        return IsAssociateProfessorOf


@dataclass(eq=False)
class HasFullProfessor(HasProfessor, HasInverseProperty):
    """HasFullProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsFullProfessorOf]:
        return IsFullProfessorOf


@dataclass(eq=False)
class HasVisitingProfessor(HasProfessor, HasInverseProperty):
    """HasVisitingProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsVisitingProfessorOf]:
        return IsVisitingProfessorOf


@dataclass(eq=False)
class IsHeadOf(IsFullProfessorOf, HasInverseProperty):
    """IsHeadOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasHead]:
        return HasHead


@dataclass(eq=False)
class HasHead(HasFullProfessor, HasInverseProperty):
    """HasHead"""

    @classmethod
    def get_inverse(cls) -> Type[IsHeadOf]:
        return IsHeadOf


