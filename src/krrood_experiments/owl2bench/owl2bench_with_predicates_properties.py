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
@dataclass
class Dislikes(PropertyDescriptor, HasDisjointProperties):
    """Dislikes"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Likes]


@dataclass
class EnrollFor(PropertyDescriptor):
    """EnrollFor"""


@dataclass
class EvaluatedBy(PropertyDescriptor, HasInverseProperty):
    """EvaluatedBy"""

    @classmethod
    def get_inverse(cls) -> Type[Evaluates]:
        return Evaluates


@dataclass
class Evaluates(PropertyDescriptor, HasInverseProperty):
    """Evaluates"""

    @classmethod
    def get_inverse(cls) -> Type[EvaluatedBy]:
        return EvaluatedBy


@dataclass
class HasAdvisor(PropertyDescriptor, HasEquivalentProperties):
    """HasAdvisor"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsAdvisedBy]


@dataclass
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """HasAlumnus"""

    @classmethod
    def get_inverse(cls) -> Type[HasDegreeFrom]:
        return HasDegreeFrom


@dataclass
class HasAuthor(PropertyDescriptor):
    """HasAuthor"""


@dataclass
class HasCollaborationWith(PropertyDescriptor, SymmetricProperty, IrreflexiveProperty):
    """HasCollaborationWith"""


@dataclass
class HasCollegeDiscipline(PropertyDescriptor, HasDisjointProperties):
    """HasCollegeDiscipline"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasMajor]


@dataclass
class HasDean(PropertyDescriptor, HasInverseProperty):
    """HasDean"""

    @classmethod
    def get_inverse(cls) -> Type[IsDeanOf]:
        return IsDeanOf


@dataclass
class HasDegreeFrom(PropertyDescriptor, HasInverseProperty):
    """HasDegreeFrom"""

    @classmethod
    def get_inverse(cls) -> Type[HasAlumnus]:
        return HasAlumnus


@dataclass
class HasEvaluationCommittee(PropertyDescriptor):
    """HasEvaluationCommittee"""


@dataclass
class HasMajor(PropertyDescriptor, HasDisjointProperties):
    """HasMajor"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasCollegeDiscipline]


@dataclass
class HasMember(PropertyDescriptor, HasInverseProperty):
    """HasMember"""

    @classmethod
    def get_inverse(cls) -> Type[IsMemberOf]:
        return IsMemberOf


@dataclass
class HasPart(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasPart"""

    @classmethod
    def get_inverse(cls) -> Type[IsPartOf]:
        return IsPartOf

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasSubOrganization]


@dataclass
class HasProgram(PropertyDescriptor):
    """HasProgram"""


@dataclass
class HasSameHomeTownWith(PropertyDescriptor, TransitiveProperty, SymmetricProperty):
    """HasSameHomeTownWith"""


@dataclass
class HasSubOrganization(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasSubOrganization"""

    @classmethod
    def get_inverse(cls) -> Type[IsSubOrganizationOf]:
        return IsSubOrganizationOf

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasPart]


@dataclass
class HasWork(PropertyDescriptor):
    """HasWork"""


@dataclass
class IsAdvisedBy(PropertyDescriptor, HasEquivalentProperties):
    """IsAdvisedBy"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasAdvisor]


@dataclass
class IsAffiliateOf(PropertyDescriptor):
    """IsAffiliateOf"""


@dataclass
class IsAffiliatedOrganizationOf(PropertyDescriptor, ASymmetricProperty, IrreflexiveProperty):
    """IsAffiliatedOrganizationOf"""


@dataclass
class IsDeanOf(PropertyDescriptor, HasInverseProperty):
    """IsDeanOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasDean]:
        return HasDean


@dataclass
class IsMemberOf(PropertyDescriptor, HasInverseProperty):
    """IsMemberOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasMember]:
        return HasMember


@dataclass
class IsPartOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsPartOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasPart]:
        return HasPart

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsSubOrganizationOf]


@dataclass
class IsStudentOf(PropertyDescriptor, HasInverseProperty):
    """IsStudentOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasStudent]:
        return HasStudent


@dataclass
class IsSubOrganizationOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsSubOrganizationOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasSubOrganization]:
        return HasSubOrganization

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [IsPartOf]


@dataclass
class IsTaughtBy(PropertyDescriptor, HasInverseProperty):
    """IsTaughtBy"""

    @classmethod
    def get_inverse(cls) -> Type[TeachesCourse]:
        return TeachesCourse


@dataclass
class IsTeachingAssistantOf(PropertyDescriptor):
    """IsTeachingAssistantOf"""


@dataclass
class Knows(PropertyDescriptor):
    """Knows"""


@dataclass
class Likes(PropertyDescriptor, HasDisjointProperties, IrreflexiveProperty):
    """Likes"""

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Dislikes]


@dataclass
class OfferCourse(PropertyDescriptor):
    """OfferCourse"""


@dataclass
class OrgPublication(PropertyDescriptor):
    """OrgPublication"""


@dataclass
class PublicationResearch(PropertyDescriptor):
    """PublicationResearch"""


@dataclass
class TakesCourse(PropertyDescriptor):
    """TakesCourse"""


@dataclass
class WorksFor(PropertyDescriptor, HasInverseProperty):
    """WorksFor"""

    @classmethod
    def get_inverse(cls) -> Type[HasEmployee]:
        return HasEmployee


@dataclass
class EnrollIn(IsStudentOf):
    """EnrollIn"""


@dataclass
class HasCollege(HasSubOrganization, HasInverseProperty):
    """HasCollege"""

    @classmethod
    def get_inverse(cls) -> Type[IsCollegeOf]:
        return IsCollegeOf


@dataclass
class HasCommitteeMembers(HasMember):
    """HasCommitteeMembers"""


@dataclass
class HasDepartment(HasSubOrganization, HasInverseProperty):
    """HasDepartment"""

    @classmethod
    def get_inverse(cls) -> Type[IsDepartmentOf]:
        return IsDepartmentOf


@dataclass
class HasDoctoralDegreeFrom(HasDegreeFrom):
    """HasDoctoralDegreeFrom"""


@dataclass
class HasEmployee(HasMember, HasInverseProperty):
    """HasEmployee"""

    @classmethod
    def get_inverse(cls) -> Type[WorksFor]:
        return WorksFor


@dataclass
class HasEmployeeEvaluationCommittee(HasEvaluationCommittee):
    """HasEmployeeEvaluationCommittee"""


@dataclass
class HasMasterDegreeFrom(HasDegreeFrom):
    """HasMasterDegreeFrom"""


@dataclass
class HasPGProgram(HasProgram):
    """HasPGProgram"""


@dataclass
class HasPhDProgram(HasProgram):
    """HasPhDProgram"""


@dataclass
class HasResearchGroup(HasSubOrganization, HasInverseProperty):
    """HasResearchGroup"""

    @classmethod
    def get_inverse(cls) -> Type[IsResearchGroupOf]:
        return IsResearchGroupOf


@dataclass
class HasResearchProject(HasWork):
    """HasResearchProject"""


@dataclass
class HasStudent(HasMember, HasInverseProperty):
    """HasStudent"""

    @classmethod
    def get_inverse(cls) -> Type[IsStudentOf]:
        return IsStudentOf


@dataclass
class HasStudentEvaluationCommittee(HasEvaluationCommittee):
    """HasStudentEvaluationCommittee"""


@dataclass
class HasUGProgram(HasProgram):
    """HasUGProgram"""


@dataclass
class HasUndergraduateDegreeFrom(HasDegreeFrom):
    """HasUndergraduateDegreeFrom"""


@dataclass
class IsCollegeOf(IsSubOrganizationOf, HasInverseProperty):
    """IsCollegeOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasCollege]:
        return HasCollege


@dataclass
class IsDepartmentOf(IsSubOrganizationOf, HasInverseProperty):
    """IsDepartmentOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasDepartment]:
        return HasDepartment


@dataclass
class IsFacultyOf(WorksFor, HasInverseProperty):
    """IsFacultyOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasFaculty]:
        return HasFaculty


@dataclass
class IsResearchAssistantOf(WorksFor, HasInverseProperty):
    """IsResearchAssistantOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasResearchAssistant]:
        return HasResearchAssistant


@dataclass
class IsResearchGroupOf(IsSubOrganizationOf, HasInverseProperty):
    """IsResearchGroupOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasResearchGroup]:
        return HasResearchGroup


@dataclass
class IsSupportingStaffOf(WorksFor):
    """IsSupportingStaffOf"""


@dataclass
class Loves(Likes):
    """Loves"""


@dataclass
class TeachesCourse(HasWork, HasInverseProperty):
    """TeachesCourse"""

    @classmethod
    def get_inverse(cls) -> Type[IsTaughtBy]:
        return IsTaughtBy


@dataclass
class HasFaculty(HasEmployee, HasInverseProperty):
    """HasFaculty"""

    @classmethod
    def get_inverse(cls) -> Type[IsFacultyOf]:
        return IsFacultyOf


@dataclass
class HasResearchAssistant(HasEmployee, HasInverseProperty):
    """HasResearchAssistant"""

    @classmethod
    def get_inverse(cls) -> Type[IsResearchAssistantOf]:
        return IsResearchAssistantOf


@dataclass
class HasSupportingStaff(HasEmployee):
    """HasSupportingStaff"""


@dataclass
class HasThesisEvaluationCommittee(HasStudentEvaluationCommittee):
    """HasThesisEvaluationCommittee"""


@dataclass
class HasWomenCollege(HasCollege):
    """HasWomenCollege"""


@dataclass
class IsClericalStaffOf(IsSupportingStaffOf):
    """IsClericalStaffOf"""


@dataclass
class IsCrazyAbout(Loves):
    """IsCrazyAbout"""


@dataclass
class IsLecturerOf(IsFacultyOf, HasInverseProperty):
    """IsLecturerOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasLecturer]:
        return HasLecturer


@dataclass
class IsOtherStaffOf(IsSupportingStaffOf):
    """IsOtherStaffOf"""


@dataclass
class IsPostDocOf(IsFacultyOf, HasInverseProperty):
    """IsPostDocOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasPostDoc]:
        return HasPostDoc


@dataclass
class IsProfessorOf(IsFacultyOf, HasInverseProperty):
    """IsProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasProfessor]:
        return HasProfessor


@dataclass
class IsSystemStaffOf(IsSupportingStaffOf):
    """IsSystemStaffOf"""


@dataclass
class IsWomenCollegeOf(IsCollegeOf):
    """IsWomenCollegeOf"""


@dataclass
class HasClericalStaff(HasSupportingStaff):
    """HasClericalStaff"""


@dataclass
class HasLecturer(HasFaculty, HasInverseProperty):
    """HasLecturer"""

    @classmethod
    def get_inverse(cls) -> Type[IsLecturerOf]:
        return IsLecturerOf


@dataclass
class HasOtherStaff(HasSupportingStaff):
    """HasOtherStaff"""


@dataclass
class HasPostDoc(HasFaculty, HasInverseProperty):
    """HasPostDoc"""

    @classmethod
    def get_inverse(cls) -> Type[IsPostDocOf]:
        return IsPostDocOf


@dataclass
class HasProfessor(HasFaculty, HasInverseProperty):
    """HasProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsProfessorOf]:
        return IsProfessorOf


@dataclass
class HasSystemStaff(HasSupportingStaff):
    """HasSystemStaff"""


@dataclass
class IsAssistantProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssistantProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasAssistantProfessor]:
        return HasAssistantProfessor


@dataclass
class IsAssociateProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssociateProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasAssociateProfessor]:
        return HasAssociateProfessor


@dataclass
class IsFullProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsFullProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasFullProfessor]:
        return HasFullProfessor


@dataclass
class IsVisitingProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsVisitingProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasVisitingProfessor]:
        return HasVisitingProfessor


@dataclass
class HasAssistantProfessor(HasProfessor, HasInverseProperty):
    """HasAssistantProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsAssistantProfessorOf]:
        return IsAssistantProfessorOf


@dataclass
class HasAssociateProfessor(HasProfessor, HasInverseProperty):
    """HasAssociateProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsAssociateProfessorOf]:
        return IsAssociateProfessorOf


@dataclass
class HasFullProfessor(HasProfessor, HasInverseProperty):
    """HasFullProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsFullProfessorOf]:
        return IsFullProfessorOf


@dataclass
class HasVisitingProfessor(HasProfessor, HasInverseProperty):
    """HasVisitingProfessor"""

    @classmethod
    def get_inverse(cls) -> Type[IsVisitingProfessorOf]:
        return IsVisitingProfessorOf


@dataclass
class IsHeadOf(IsFullProfessorOf, HasInverseProperty):
    """IsHeadOf"""

    @classmethod
    def get_inverse(cls) -> Type[HasHead]:
        return HasHead


@dataclass
class HasHead(HasFullProfessor, HasInverseProperty):
    """HasHead"""

    @classmethod
    def get_inverse(cls) -> Type[IsHeadOf]:
        return IsHeadOf


