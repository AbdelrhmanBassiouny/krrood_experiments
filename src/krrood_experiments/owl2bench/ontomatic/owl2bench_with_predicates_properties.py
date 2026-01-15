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
    def get_inverse(cls) -> Optional[Type[Evaluates]]:
        if cls is EvaluatedBy:
            return Evaluates
        return None


@dataclass(eq=False)
class Evaluates(PropertyDescriptor, HasInverseProperty):
    """Evaluates"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[EvaluatedBy]]:
        if cls is Evaluates:
            return EvaluatedBy
        return None


@dataclass(eq=False)
class HasAdvisor(PropertyDescriptor, HasEquivalentProperties):
    """HasAdvisor"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is HasAdvisor:
            return [IsAdvisedBy]
        return []


@dataclass(eq=False)
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """HasAlumnus"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasDegreeFrom]]:
        if cls is HasAlumnus:
            return HasDegreeFrom
        return None


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
    def get_inverse(cls) -> Optional[Type[IsDeanOf]]:
        if cls is HasDean:
            return IsDeanOf
        return None


@dataclass(eq=False)
class HasDegreeFrom(PropertyDescriptor, HasInverseProperty):
    """HasDegreeFrom"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAlumnus]]:
        if cls is HasDegreeFrom:
            return HasAlumnus
        return None


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
    def get_inverse(cls) -> Optional[Type[IsMemberOf]]:
        if cls is HasMember:
            return IsMemberOf
        return None


@dataclass(eq=False)
class HasPart(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasPart"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsPartOf]]:
        if cls is HasPart:
            return IsPartOf
        return None

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is HasPart:
            return [HasSubOrganization]
        return []


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
    def get_inverse(cls) -> Optional[Type[IsSubOrganizationOf]]:
        if cls is HasSubOrganization:
            return IsSubOrganizationOf
        return None

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is HasSubOrganization:
            return [HasPart]
        return []


@dataclass(eq=False)
class HasWork(PropertyDescriptor):
    """HasWork"""


@dataclass(eq=False)
class IsAdvisedBy(PropertyDescriptor, HasEquivalentProperties):
    """IsAdvisedBy"""

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is IsAdvisedBy:
            return [HasAdvisor]
        return []


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
    def get_inverse(cls) -> Optional[Type[HasDean]]:
        if cls is IsDeanOf:
            return HasDean
        return None


@dataclass(eq=False)
class IsMemberOf(PropertyDescriptor, HasInverseProperty, HasChainAxioms):
    """IsMemberOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasMember]]:
        if cls is IsMemberOf:
            return HasMember
        return None

    @classmethod
    def get_chain_axioms(cls) -> List[Tuple[Type[PropertyDescriptor], ...]]:
        if cls is IsMemberOf:
            return [
                (EnrollIn, IsPartOf),
                (WorksFor, IsPartOf),
            ]
        return []


@dataclass(eq=False)
class IsPartOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsPartOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasPart]]:
        if cls is IsPartOf:
            return HasPart
        return None

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is IsPartOf:
            return [IsSubOrganizationOf]
        return []


@dataclass(eq=False)
class IsStudentOf(PropertyDescriptor, HasInverseProperty, HasChainAxioms):
    """IsStudentOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasStudent]]:
        if cls is IsStudentOf:
            return HasStudent
        return None

    @classmethod
    def get_chain_axioms(cls) -> List[Tuple[Type[PropertyDescriptor], ...]]:
        if cls is IsStudentOf:
            return [
                (EnrollIn, IsSubOrganizationOf),
            ]
        return []


@dataclass(eq=False)
class IsSubOrganizationOf(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """IsSubOrganizationOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasSubOrganization]]:
        if cls is IsSubOrganizationOf:
            return HasSubOrganization
        return None

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is IsSubOrganizationOf:
            return [IsPartOf]
        return []


@dataclass(eq=False)
class IsTaughtBy(PropertyDescriptor, HasInverseProperty):
    """IsTaughtBy"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[TeachesCourse]]:
        if cls is IsTaughtBy:
            return TeachesCourse
        return None


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
class PublicationResearch(PropertyDescriptor):
    """PublicationResearch"""


@dataclass(eq=False)
class TakesCourse(PropertyDescriptor):
    """TakesCourse"""


@dataclass(eq=False)
class WorksFor(PropertyDescriptor, HasInverseProperty, HasChainAxioms):
    """WorksFor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasEmployee]]:
        if cls is WorksFor:
            return HasEmployee
        return None

    @classmethod
    def get_chain_axioms(cls) -> List[Tuple[Type[PropertyDescriptor], ...]]:
        if cls is WorksFor:
            return [
                (WorksFor, IsSubOrganizationOf),
            ]
        return []


@dataclass(eq=False)
class EnrollIn(IsStudentOf):
    """EnrollIn"""


@dataclass(eq=False)
class HasCollege(HasSubOrganization, HasInverseProperty):
    """HasCollege"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsCollegeOf]]:
        if cls is HasCollege:
            return IsCollegeOf
        return None


@dataclass(eq=False)
class HasCommitteeMembers(HasMember):
    """HasCommitteeMembers"""


@dataclass(eq=False)
class HasDepartment(HasSubOrganization, HasInverseProperty):
    """HasDepartment"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsDepartmentOf]]:
        if cls is HasDepartment:
            return IsDepartmentOf
        return None


@dataclass(eq=False)
class HasDoctoralDegreeFrom(HasDegreeFrom):
    """HasDoctoralDegreeFrom"""


@dataclass(eq=False)
class HasEmployee(HasMember, HasInverseProperty):
    """HasEmployee"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[WorksFor]]:
        if cls is HasEmployee:
            return WorksFor
        return None


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
    def get_inverse(cls) -> Optional[Type[IsResearchGroupOf]]:
        if cls is HasResearchGroup:
            return IsResearchGroupOf
        return None


@dataclass(eq=False)
class HasResearchProject(HasWork):
    """HasResearchProject"""


@dataclass(eq=False)
class HasStudent(HasMember, HasInverseProperty):
    """HasStudent"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsStudentOf]]:
        if cls is HasStudent:
            return IsStudentOf
        return None


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
    def get_inverse(cls) -> Optional[Type[HasCollege]]:
        if cls is IsCollegeOf:
            return HasCollege
        return None


@dataclass(eq=False)
class IsDepartmentOf(IsSubOrganizationOf, HasInverseProperty):
    """IsDepartmentOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasDepartment]]:
        if cls is IsDepartmentOf:
            return HasDepartment
        return None


@dataclass(eq=False)
class IsFacultyOf(WorksFor, HasInverseProperty):
    """IsFacultyOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasFaculty]]:
        if cls is IsFacultyOf:
            return HasFaculty
        return None


@dataclass(eq=False)
class IsResearchAssistantOf(WorksFor, HasInverseProperty):
    """IsResearchAssistantOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasResearchAssistant]]:
        if cls is IsResearchAssistantOf:
            return HasResearchAssistant
        return None


@dataclass(eq=False)
class IsResearchGroupOf(IsSubOrganizationOf, HasInverseProperty):
    """IsResearchGroupOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasResearchGroup]]:
        if cls is IsResearchGroupOf:
            return HasResearchGroup
        return None


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
    def get_inverse(cls) -> Optional[Type[IsTaughtBy]]:
        if cls is TeachesCourse:
            return IsTaughtBy
        return None


@dataclass(eq=False)
class HasFaculty(HasEmployee, HasInverseProperty):
    """HasFaculty"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsFacultyOf]]:
        if cls is HasFaculty:
            return IsFacultyOf
        return None


@dataclass(eq=False)
class HasResearchAssistant(HasEmployee, HasInverseProperty):
    """HasResearchAssistant"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsResearchAssistantOf]]:
        if cls is HasResearchAssistant:
            return IsResearchAssistantOf
        return None


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
    def get_inverse(cls) -> Optional[Type[HasLecturer]]:
        if cls is IsLecturerOf:
            return HasLecturer
        return None


@dataclass(eq=False)
class IsOtherStaffOf(IsSupportingStaffOf):
    """IsOtherStaffOf"""


@dataclass(eq=False)
class IsPostDocOf(IsFacultyOf, HasInverseProperty):
    """IsPostDocOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasPostDoc]]:
        if cls is IsPostDocOf:
            return HasPostDoc
        return None


@dataclass(eq=False)
class IsProfessorOf(IsFacultyOf, HasInverseProperty):
    """IsProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasProfessor]]:
        if cls is IsProfessorOf:
            return HasProfessor
        return None


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
    def get_inverse(cls) -> Optional[Type[IsLecturerOf]]:
        if cls is HasLecturer:
            return IsLecturerOf
        return None


@dataclass(eq=False)
class HasOtherStaff(HasSupportingStaff):
    """HasOtherStaff"""


@dataclass(eq=False)
class HasPostDoc(HasFaculty, HasInverseProperty):
    """HasPostDoc"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsPostDocOf]]:
        if cls is HasPostDoc:
            return IsPostDocOf
        return None


@dataclass(eq=False)
class HasProfessor(HasFaculty, HasInverseProperty):
    """HasProfessor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsProfessorOf]]:
        if cls is HasProfessor:
            return IsProfessorOf
        return None


@dataclass(eq=False)
class HasSystemStaff(HasSupportingStaff):
    """HasSystemStaff"""


@dataclass(eq=False)
class IsAssistantProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssistantProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAssistantProfessor]]:
        if cls is IsAssistantProfessorOf:
            return HasAssistantProfessor
        return None


@dataclass(eq=False)
class IsAssociateProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssociateProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAssociateProfessor]]:
        if cls is IsAssociateProfessorOf:
            return HasAssociateProfessor
        return None


@dataclass(eq=False)
class IsFullProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsFullProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasFullProfessor]]:
        if cls is IsFullProfessorOf:
            return HasFullProfessor
        return None


@dataclass(eq=False)
class IsVisitingProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsVisitingProfessorOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasVisitingProfessor]]:
        if cls is IsVisitingProfessorOf:
            return HasVisitingProfessor
        return None


@dataclass(eq=False)
class HasAssistantProfessor(HasProfessor, HasInverseProperty):
    """HasAssistantProfessor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsAssistantProfessorOf]]:
        if cls is HasAssistantProfessor:
            return IsAssistantProfessorOf
        return None


@dataclass(eq=False)
class HasAssociateProfessor(HasProfessor, HasInverseProperty):
    """HasAssociateProfessor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsAssociateProfessorOf]]:
        if cls is HasAssociateProfessor:
            return IsAssociateProfessorOf
        return None


@dataclass(eq=False)
class HasFullProfessor(HasProfessor, HasInverseProperty):
    """HasFullProfessor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsFullProfessorOf]]:
        if cls is HasFullProfessor:
            return IsFullProfessorOf
        return None


@dataclass(eq=False)
class HasVisitingProfessor(HasProfessor, HasInverseProperty):
    """HasVisitingProfessor"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsVisitingProfessorOf]]:
        if cls is HasVisitingProfessor:
            return IsVisitingProfessorOf
        return None


@dataclass(eq=False)
class IsHeadOf(IsFullProfessorOf, HasInverseProperty):
    """IsHeadOf"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasHead]]:
        if cls is IsHeadOf:
            return HasHead
        return None


@dataclass(eq=False)
class HasHead(HasFullProfessor, HasInverseProperty):
    """HasHead"""

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsHeadOf]]:
        if cls is HasHead:
            return IsHeadOf
        return None


