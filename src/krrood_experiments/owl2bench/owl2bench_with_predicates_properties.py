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
class Dislikes(PropertyDescriptor):
    ...


@dataclass
class EnrollFor(PropertyDescriptor):
    ...


@dataclass
class EvaluatedBy(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[Evaluates]:
        return Evaluates


@dataclass
class Evaluates(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[EvaluatedBy]:
        return EvaluatedBy


@dataclass
class HasAdvisor(PropertyDescriptor):
    ...


@dataclass
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasDegreeFrom]:
        return HasDegreeFrom


@dataclass
class HasAuthor(PropertyDescriptor):
    ...


@dataclass
class HasCollaborationWith(PropertyDescriptor):
    ...


@dataclass
class HasCollegeDiscipline(PropertyDescriptor):
    ...


@dataclass
class HasDean(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsDeanOf]:
        return IsDeanOf


@dataclass
class HasDegreeFrom(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasAlumnus]:
        return HasAlumnus


@dataclass
class HasEvaluationCommittee(PropertyDescriptor):
    ...


@dataclass
class HasMajor(PropertyDescriptor):
    ...


@dataclass
class HasMember(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsMemberOf]:
        return IsMemberOf


@dataclass
class HasPart(PropertyDescriptor, TransitiveProperty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsPartOf]:
        return IsPartOf


@dataclass
class HasProgram(PropertyDescriptor):
    ...


@dataclass
class HasSameHomeTownWith(PropertyDescriptor, TransitiveProperty):
    ...


@dataclass
class HasSubOrganization(PropertyDescriptor, TransitiveProperty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsSubOrganizationOf]:
        return IsSubOrganizationOf


@dataclass
class HasWork(PropertyDescriptor):
    ...


@dataclass
class IsAdvisedBy(PropertyDescriptor):
    ...


@dataclass
class IsAffiliateOf(PropertyDescriptor):
    ...


@dataclass
class IsAffiliatedOrganizationOf(PropertyDescriptor):
    ...


@dataclass
class IsDeanOf(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasDean]:
        return HasDean


@dataclass
class IsMemberOf(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasMember]:
        return HasMember


@dataclass
class IsPartOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasPart]:
        return HasPart


@dataclass
class IsStudentOf(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasStudent]:
        return HasStudent


@dataclass
class IsSubOrganizationOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasSubOrganization]:
        return HasSubOrganization


@dataclass
class IsTaughtBy(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[TeachesCourse]:
        return TeachesCourse


@dataclass
class IsTeachingAssistantOf(PropertyDescriptor):
    ...


@dataclass
class Knows(PropertyDescriptor):
    ...


@dataclass
class Likes(PropertyDescriptor):
    ...


@dataclass
class OfferCourse(PropertyDescriptor):
    ...


@dataclass
class OrgPublication(PropertyDescriptor):
    ...


@dataclass
class PublicationResearch(PropertyDescriptor):
    ...


@dataclass
class TakesCourse(PropertyDescriptor):
    ...


@dataclass
class WorksFor(PropertyDescriptor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasEmployee]:
        return HasEmployee


@dataclass
class EnrollIn(IsStudentOf):
    ...


@dataclass
class HasCollege(HasSubOrganization, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsCollegeOf]:
        return IsCollegeOf


@dataclass
class HasCommitteeMembers(HasMember):
    ...


@dataclass
class HasDepartment(HasSubOrganization, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsDepartmentOf]:
        return IsDepartmentOf


@dataclass
class HasDoctoralDegreeFrom(HasDegreeFrom):
    ...


@dataclass
class HasEmployee(HasMember, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[WorksFor]:
        return WorksFor


@dataclass
class HasEmployeeEvaluationCommittee(HasEvaluationCommittee):
    ...


@dataclass
class HasMasterDegreeFrom(HasDegreeFrom):
    ...


@dataclass
class HasPGProgram(HasProgram):
    ...


@dataclass
class HasPhDProgram(HasProgram):
    ...


@dataclass
class HasResearchGroup(HasSubOrganization, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsResearchGroupOf]:
        return IsResearchGroupOf


@dataclass
class HasResearchProject(HasWork):
    ...


@dataclass
class HasStudent(HasMember, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsStudentOf]:
        return IsStudentOf


@dataclass
class HasStudentEvaluationCommittee(HasEvaluationCommittee):
    ...


@dataclass
class HasUGProgram(HasProgram):
    ...


@dataclass
class HasUndergraduateDegreeFrom(HasDegreeFrom):
    ...


@dataclass
class IsCollegeOf(IsSubOrganizationOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasCollege]:
        return HasCollege


@dataclass
class IsDepartmentOf(IsSubOrganizationOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasDepartment]:
        return HasDepartment


@dataclass
class IsFacultyOf(WorksFor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasFaculty]:
        return HasFaculty


@dataclass
class IsResearchAssistantOf(WorksFor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasResearchAssistant]:
        return HasResearchAssistant


@dataclass
class IsResearchGroupOf(IsSubOrganizationOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasResearchGroup]:
        return HasResearchGroup


@dataclass
class IsSupportingStaffOf(WorksFor):
    ...


@dataclass
class Loves(Likes):
    ...


@dataclass
class TeachesCourse(HasWork, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsTaughtBy]:
        return IsTaughtBy


@dataclass
class HasFaculty(HasEmployee, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsFacultyOf]:
        return IsFacultyOf


@dataclass
class HasResearchAssistant(HasEmployee, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsResearchAssistantOf]:
        return IsResearchAssistantOf


@dataclass
class HasSupportingStaff(HasEmployee):
    ...


@dataclass
class HasThesisEvaluationCommittee(HasStudentEvaluationCommittee):
    ...


@dataclass
class HasWomenCollege(HasCollege):
    ...


@dataclass
class IsClericalStaffOf(IsSupportingStaffOf):
    ...


@dataclass
class IsCrazyAbout(Loves):
    ...


@dataclass
class IsLecturerOf(IsFacultyOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasLecturer]:
        return HasLecturer


@dataclass
class IsOtherStaffOf(IsSupportingStaffOf):
    ...


@dataclass
class IsPostDocOf(IsFacultyOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasPostDoc]:
        return HasPostDoc


@dataclass
class IsProfessorOf(IsFacultyOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasProfessor]:
        return HasProfessor


@dataclass
class IsSystemStaffOf(IsSupportingStaffOf):
    ...


@dataclass
class IsWomenCollegeOf(IsCollegeOf):
    ...


@dataclass
class HasClericalStaff(HasSupportingStaff):
    ...


@dataclass
class HasLecturer(HasFaculty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsLecturerOf]:
        return IsLecturerOf


@dataclass
class HasOtherStaff(HasSupportingStaff):
    ...


@dataclass
class HasPostDoc(HasFaculty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsPostDocOf]:
        return IsPostDocOf


@dataclass
class HasProfessor(HasFaculty, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsProfessorOf]:
        return IsProfessorOf


@dataclass
class HasSystemStaff(HasSupportingStaff):
    ...


@dataclass
class IsAssistantProfessorOf(IsProfessorOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasAssistantProfessor]:
        return HasAssistantProfessor


@dataclass
class IsAssociateProfessorOf(IsProfessorOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasAssociateProfessor]:
        return HasAssociateProfessor


@dataclass
class IsFullProfessorOf(IsProfessorOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasFullProfessor]:
        return HasFullProfessor


@dataclass
class IsVisitingProfessorOf(IsProfessorOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasVisitingProfessor]:
        return HasVisitingProfessor


@dataclass
class HasAssistantProfessor(HasProfessor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsAssistantProfessorOf]:
        return IsAssistantProfessorOf


@dataclass
class HasAssociateProfessor(HasProfessor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsAssociateProfessorOf]:
        return IsAssociateProfessorOf


@dataclass
class HasFullProfessor(HasProfessor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsFullProfessorOf]:
        return IsFullProfessorOf


@dataclass
class HasVisitingProfessor(HasProfessor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsVisitingProfessorOf]:
        return IsVisitingProfessorOf


@dataclass
class IsHeadOf(IsFullProfessorOf, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[HasHead]:
        return HasHead


@dataclass
class HasHead(HasFullProfessor, HasInverseProperty):
    ...
    @classmethod
    def get_inverse(cls) -> Type[IsHeadOf]:
        return IsHeadOf


