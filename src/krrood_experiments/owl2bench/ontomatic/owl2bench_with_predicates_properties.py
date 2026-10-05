"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import Type, List, Optional, Tuple, ClassVar

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Interest", )

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Likes]


@dataclass(eq=False)
class EnrollFor(PropertyDescriptor):
    """EnrollFor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Student", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Program", )


@dataclass(eq=False)
class EvaluatedBy(PropertyDescriptor, HasInverseProperty):
    """EvaluatedBy"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("EvaluationCommittee", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[Evaluates]]:
        if cls is EvaluatedBy:
            return Evaluates
        return None


@dataclass(eq=False)
class Evaluates(PropertyDescriptor, HasInverseProperty):
    """Evaluates"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("EvaluationCommittee", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[EvaluatedBy]]:
        if cls is Evaluates:
            return EvaluatedBy
        return None


@dataclass(eq=False)
class HasAdvisor(PropertyDescriptor, HasEquivalentProperties):
    """HasAdvisor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is HasAdvisor:
            return [IsAdvisedBy]
        return []


@dataclass(eq=False)
class HasAlumnus(PropertyDescriptor, HasInverseProperty):
    """HasAlumnus"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("University", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasDegreeFrom]]:
        if cls is HasAlumnus:
            return HasDegreeFrom
        return None


@dataclass(eq=False)
class HasAuthor(PropertyDescriptor):
    """HasAuthor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Publication", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )


@dataclass(eq=False)
class HasCollaborationWith(PropertyDescriptor, SymmetricProperty, IrreflexiveProperty):
    """HasCollaborationWith"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )


@dataclass(eq=False)
class HasCollegeDiscipline(PropertyDescriptor, HasDisjointProperties):
    """HasCollegeDiscipline"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("College", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("CollegeDiscipline", )

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasMajor]


@dataclass(eq=False)
class HasDean(PropertyDescriptor, HasInverseProperty):
    """HasDean"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsDeanOf]]:
        if cls is HasDean:
            return IsDeanOf
        return None


@dataclass(eq=False)
class HasDegreeFrom(PropertyDescriptor, HasInverseProperty):
    """HasDegreeFrom"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAlumnus]]:
        if cls is HasDegreeFrom:
            return HasAlumnus
        return None


@dataclass(eq=False)
class HasEvaluationCommittee(PropertyDescriptor):
    """HasEvaluationCommittee"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("EvaluationCommittee", )


@dataclass(eq=False)
class HasMajor(PropertyDescriptor, HasDisjointProperties):
    """HasMajor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [HasCollegeDiscipline]


@dataclass(eq=False)
class HasMember(PropertyDescriptor, HasInverseProperty):
    """HasMember"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsMemberOf]]:
        if cls is HasMember:
            return IsMemberOf
        return None


@dataclass(eq=False)
class HasPart(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasPart"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Program", )


@dataclass(eq=False)
class HasSameHomeTownWith(PropertyDescriptor, TransitiveProperty, SymmetricProperty):
    """HasSameHomeTownWith"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class HasSubOrganization(PropertyDescriptor, TransitiveProperty, HasInverseProperty, HasEquivalentProperties):
    """HasSubOrganization"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Employee", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Work", )


@dataclass(eq=False)
class IsAdvisedBy(PropertyDescriptor, HasEquivalentProperties):
    """IsAdvisedBy"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Professor", )

    @classmethod
    def get_equivalent_properties(cls) -> List[Type[PropertyDescriptor]]:
        if cls is IsAdvisedBy:
            return [HasAdvisor]
        return []


@dataclass(eq=False)
class IsAffiliateOf(PropertyDescriptor):
    """IsAffiliateOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class IsAffiliatedOrganizationOf(PropertyDescriptor, ASymmetricProperty, IrreflexiveProperty):
    """IsAffiliatedOrganizationOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )


@dataclass(eq=False)
class IsDeanOf(PropertyDescriptor, HasInverseProperty):
    """IsDeanOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasDean]]:
        if cls is IsDeanOf:
            return HasDean
        return None


@dataclass(eq=False)
class IsMemberOf(PropertyDescriptor, HasInverseProperty, HasChainAxioms):
    """IsMemberOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Student", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Course", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Faculty", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[TeachesCourse]]:
        if cls is IsTaughtBy:
            return TeachesCourse
        return None


@dataclass(eq=False)
class IsTeachingAssistantOf(PropertyDescriptor):
    """IsTeachingAssistantOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("TeachingAssistant", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Course", )


@dataclass(eq=False)
class Knows(PropertyDescriptor):
    """Knows"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class Likes(PropertyDescriptor, HasDisjointProperties, IrreflexiveProperty):
    """Likes"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Interest", )

    @classmethod
    def get_disjoint_properties(cls) -> List[Type[PropertyDescriptor]]:
        return [Dislikes]


@dataclass(eq=False)
class OfferCourse(PropertyDescriptor):
    """OfferCourse"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Course", )


@dataclass(eq=False)
class OrgPublication(PropertyDescriptor):
    """OrgPublication"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Publication", )


@dataclass(eq=False)
class PublicationResearch(PropertyDescriptor):
    """PublicationResearch"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Publication", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class TakesCourse(PropertyDescriptor):
    """TakesCourse"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Student", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Course", )


@dataclass(eq=False)
class Tenured(PropertyDescriptor):
    """Tenured"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Professor", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class WorksFor(PropertyDescriptor, HasInverseProperty, HasChainAxioms):
    """WorksFor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Employee", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

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

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Student", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Department", )


@dataclass(eq=False)
class HasCollege(HasSubOrganization, HasInverseProperty):
    """HasCollege"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("University", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("College", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsCollegeOf]]:
        if cls is HasCollege:
            return IsCollegeOf
        return None


@dataclass(eq=False)
class HasCommitteeMembers(HasMember):
    """HasCommitteeMembers"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("EvaluationCommittee", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Person", )


@dataclass(eq=False)
class HasDepartment(HasSubOrganization, HasInverseProperty):
    """HasDepartment"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("College", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Department", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsDepartmentOf]]:
        if cls is HasDepartment:
            return IsDepartmentOf
        return None


@dataclass(eq=False)
class HasDoctoralDegreeFrom(HasDegreeFrom):
    """HasDoctoralDegreeFrom"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )


@dataclass(eq=False)
class HasEmployee(HasMember, HasInverseProperty):
    """HasEmployee"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[WorksFor]]:
        if cls is HasEmployee:
            return WorksFor
        return None


@dataclass(eq=False)
class HasEmployeeEvaluationCommittee(HasEvaluationCommittee):
    """HasEmployeeEvaluationCommittee"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("EmployeeEvaluationCommittee", )


@dataclass(eq=False)
class HasMasterDegreeFrom(HasDegreeFrom):
    """HasMasterDegreeFrom"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )


@dataclass(eq=False)
class HasPGProgram(HasProgram):
    """HasPGProgram"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("PGProgram", )


@dataclass(eq=False)
class HasPhDProgram(HasProgram):
    """HasPhDProgram"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("PhDProgram", )


@dataclass(eq=False)
class HasResearchGroup(HasSubOrganization, HasInverseProperty):
    """HasResearchGroup"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("University", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("ResearchGroup", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsResearchGroupOf]]:
        if cls is HasResearchGroup:
            return IsResearchGroupOf
        return None


@dataclass(eq=False)
class HasResearchProject(HasWork):
    """HasResearchProject"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("ResearchGroup", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("ResearchProject", )


@dataclass(eq=False)
class HasStudent(HasMember, HasInverseProperty):
    """HasStudent"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Student", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsStudentOf]]:
        if cls is HasStudent:
            return IsStudentOf
        return None


@dataclass(eq=False)
class HasStudentEvaluationCommittee(HasEvaluationCommittee):
    """HasStudentEvaluationCommittee"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("StudentEvaluationCommittee", )


@dataclass(eq=False)
class HasUGProgram(HasProgram):
    """HasUGProgram"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("UGProgram", )


@dataclass(eq=False)
class HasUndergraduateDegreeFrom(HasDegreeFrom):
    """HasUndergraduateDegreeFrom"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )


@dataclass(eq=False)
class IsCollegeOf(IsSubOrganizationOf, HasInverseProperty):
    """IsCollegeOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("College", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasCollege]]:
        if cls is IsCollegeOf:
            return HasCollege
        return None


@dataclass(eq=False)
class IsDepartmentOf(IsSubOrganizationOf, HasInverseProperty):
    """IsDepartmentOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("College", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasDepartment]]:
        if cls is IsDepartmentOf:
            return HasDepartment
        return None


@dataclass(eq=False)
class IsFacultyOf(WorksFor, HasInverseProperty):
    """IsFacultyOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Faculty", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Organization", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasFaculty]]:
        if cls is IsFacultyOf:
            return HasFaculty
        return None


@dataclass(eq=False)
class IsResearchAssistantOf(WorksFor, HasInverseProperty):
    """IsResearchAssistantOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasResearchAssistant]]:
        if cls is IsResearchAssistantOf:
            return HasResearchAssistant
        return None


@dataclass(eq=False)
class IsResearchGroupOf(IsSubOrganizationOf, HasInverseProperty):
    """IsResearchGroupOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("ResearchGroup", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("University", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasResearchGroup]]:
        if cls is IsResearchGroupOf:
            return HasResearchGroup
        return None


@dataclass(eq=False)
class IsSupportingStaffOf(WorksFor):
    """IsSupportingStaffOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class Loves(Likes):
    """Loves"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Interest", )


@dataclass(eq=False)
class TeachesCourse(HasWork, HasInverseProperty):
    """TeachesCourse"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Faculty", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Course", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsTaughtBy]]:
        if cls is TeachesCourse:
            return IsTaughtBy
        return None


@dataclass(eq=False)
class HasFaculty(HasEmployee, HasInverseProperty):
    """HasFaculty"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Faculty", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsFacultyOf]]:
        if cls is HasFaculty:
            return IsFacultyOf
        return None


@dataclass(eq=False)
class HasResearchAssistant(HasEmployee, HasInverseProperty):
    """HasResearchAssistant"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("ResearchGroup", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("ResearchAssistant", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsResearchAssistantOf]]:
        if cls is HasResearchAssistant:
            return IsResearchAssistantOf
        return None


@dataclass(eq=False)
class HasSupportingStaff(HasEmployee):
    """HasSupportingStaff"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("SupportingStaff", )


@dataclass(eq=False)
class HasThesisEvaluationCommittee(HasStudentEvaluationCommittee):
    """HasThesisEvaluationCommittee"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Organization", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("ThesisEvaluationCommittee", )


@dataclass(eq=False)
class HasWomenCollege(HasCollege):
    """HasWomenCollege"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class IsClericalStaffOf(IsSupportingStaffOf):
    """IsClericalStaffOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class IsCrazyAbout(Loves):
    """IsCrazyAbout"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Person", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Interest", )


@dataclass(eq=False)
class IsLecturerOf(IsFacultyOf, HasInverseProperty):
    """IsLecturerOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasLecturer]]:
        if cls is IsLecturerOf:
            return HasLecturer
        return None


@dataclass(eq=False)
class IsOtherStaffOf(IsSupportingStaffOf):
    """IsOtherStaffOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class IsPostDocOf(IsFacultyOf, HasInverseProperty):
    """IsPostDocOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasPostDoc]]:
        if cls is IsPostDocOf:
            return HasPostDoc
        return None


@dataclass(eq=False)
class IsProfessorOf(IsFacultyOf, HasInverseProperty):
    """IsProfessorOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasProfessor]]:
        if cls is IsProfessorOf:
            return HasProfessor
        return None


@dataclass(eq=False)
class IsSystemStaffOf(IsSupportingStaffOf):
    """IsSystemStaffOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class IsWomenCollegeOf(IsCollegeOf):
    """IsWomenCollegeOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()


@dataclass(eq=False)
class HasClericalStaff(HasSupportingStaff):
    """HasClericalStaff"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("ClericalStaff", )


@dataclass(eq=False)
class HasLecturer(HasFaculty, HasInverseProperty):
    """HasLecturer"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Lecturer", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsLecturerOf]]:
        if cls is HasLecturer:
            return IsLecturerOf
        return None


@dataclass(eq=False)
class HasOtherStaff(HasSupportingStaff):
    """HasOtherStaff"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("OtherStaff", )


@dataclass(eq=False)
class HasPostDoc(HasFaculty, HasInverseProperty):
    """HasPostDoc"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("PostDoc", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsPostDocOf]]:
        if cls is HasPostDoc:
            return IsPostDocOf
        return None


@dataclass(eq=False)
class HasProfessor(HasFaculty, HasInverseProperty):
    """HasProfessor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("Professor", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsProfessorOf]]:
        if cls is HasProfessor:
            return IsProfessorOf
        return None


@dataclass(eq=False)
class HasSystemStaff(HasSupportingStaff):
    """HasSystemStaff"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("SystemStaff", )


@dataclass(eq=False)
class IsAssistantProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssistantProfessorOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAssistantProfessor]]:
        if cls is IsAssistantProfessorOf:
            return HasAssistantProfessor
        return None


@dataclass(eq=False)
class IsAssociateProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsAssociateProfessorOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasAssociateProfessor]]:
        if cls is IsAssociateProfessorOf:
            return HasAssociateProfessor
        return None


@dataclass(eq=False)
class IsFullProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsFullProfessorOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasFullProfessor]]:
        if cls is IsFullProfessorOf:
            return HasFullProfessor
        return None


@dataclass(eq=False)
class IsVisitingProfessorOf(IsProfessorOf, HasInverseProperty):
    """IsVisitingProfessorOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasVisitingProfessor]]:
        if cls is IsVisitingProfessorOf:
            return HasVisitingProfessor
        return None


@dataclass(eq=False)
class HasAssistantProfessor(HasProfessor, HasInverseProperty):
    """HasAssistantProfessor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("AssistantProfessor", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsAssistantProfessorOf]]:
        if cls is HasAssistantProfessor:
            return IsAssistantProfessorOf
        return None


@dataclass(eq=False)
class HasAssociateProfessor(HasProfessor, HasInverseProperty):
    """HasAssociateProfessor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("AssociateProfessor", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsAssociateProfessorOf]]:
        if cls is HasAssociateProfessor:
            return IsAssociateProfessorOf
        return None


@dataclass(eq=False)
class HasFullProfessor(HasProfessor, HasInverseProperty):
    """HasFullProfessor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("FullProfessor", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsFullProfessorOf]]:
        if cls is HasFullProfessor:
            return IsFullProfessorOf
        return None


@dataclass(eq=False)
class HasVisitingProfessor(HasProfessor, HasInverseProperty):
    """HasVisitingProfessor"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ("Department", )
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ("VisitingProfessor", )

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsVisitingProfessorOf]]:
        if cls is HasVisitingProfessor:
            return IsVisitingProfessorOf
        return None


@dataclass(eq=False)
class IsHeadOf(IsFullProfessorOf, HasInverseProperty):
    """IsHeadOf"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[HasHead]]:
        if cls is IsHeadOf:
            return HasHead
        return None


@dataclass(eq=False)
class HasHead(HasFullProfessor, HasInverseProperty):
    """HasHead"""

    rdfs_domains: ClassVar[Tuple[str, ...]] = ()
    rdfs_ranges: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def get_inverse(cls) -> Optional[Type[IsHeadOf]]:
        if cls is HasHead:
            return IsHeadOf
        return None


