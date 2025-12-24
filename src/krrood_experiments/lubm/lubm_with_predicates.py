"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field, Field, fields
from abc import ABC
from typing_extensions import Optional, Set, TypeVar, Type
from functools import lru_cache

from krrood.entity_query_language.predicate import Symbol
from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.ontomatic.property_descriptor.mixins import HasInverseProperty, TransitiveProperty
from krrood.class_diagrams.utils import Role


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



# Generated classes
@dataclass(eq=False)
class UnivBenchOntology(Symbol, ABC):
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


T = TypeVar('T', bound=UnivBenchOntology)


@dataclass(eq=False)
class Organization(UnivBenchOntology):
    """organization"""
    # is affiliated with
    affiliated_organization_of: Set[Organization] = field(default_factory=set)
    # is affiliated with
    affiliate_of: Set[Person] = field(default_factory=set)
    # has as a member
    member: Set[Person] = field(default_factory=set)
    # publishes
    org_publication: Set[Publication] = field(default_factory=set)
    # is part of
    sub_organization_of: Set[Organization] = field(default_factory=set)


@dataclass(eq=False)
class Person(UnivBenchOntology):
    """person"""
    # is being advised by
    advisor: Set[Professor] = field(default_factory=set)
    # has a degree from
    degree_from: Set[University] = field(default_factory=set)
    # has a doctoral degree from
    doctoral_degree_from: Set[University] = field(default_factory=set)
    # has a masters degree from
    masters_degree_from: Set[University] = field(default_factory=set)
    # member of
    member_of: Set[Organization] = field(default_factory=set)
    # has an undergraduate degree from
    undergraduate_degree_from: Set[University] = field(default_factory=set)
    # is age
    age: Optional[int] = field(kw_only=True, default=None)
    # can be reached at
    email_address: Optional[str] = field(kw_only=True, default=None)
    # telephone number
    telephone: Optional[str] = field(kw_only=True, default=None)
    # title
    title: Optional[str] = field(kw_only=True, default=None)


@dataclass(eq=False)
class Publication(UnivBenchOntology):
    """publication"""
    # was written by
    publication_author: Set[Person] = field(default_factory=set)
    # was written on
    publication_date: Optional[str] = field(kw_only=True, default=None)
    # is about
    publication_research: Set[Research] = field(default_factory=set)


@dataclass(eq=False)
class Schedule(UnivBenchOntology):
    """schedule"""
    # lists as a course
    listed_course: Set[Course] = field(default_factory=set)


@dataclass(eq=False)
class UnivBenchOntologyRole(Role[T], UnivBenchOntology, ABC):
    """Role class which represents a role that a persistent identifier can take on in a certain context"""
    ...


@dataclass(eq=False)
class Work(UnivBenchOntology):
    """Work"""
    ...


@dataclass(eq=False)
class Article(Publication):
    """article"""
    ...


@dataclass(eq=False)
class Book(Publication):
    """book"""
    ...


@dataclass(eq=False)
class College(Organization):
    """school"""
    ...


@dataclass(eq=False)
class Course(Work):
    """teaching course"""
    ...


@dataclass(eq=False)
class Department(Organization):
    """university department"""
    ...


@dataclass(eq=False)
class Employee(UnivBenchOntologyRole[Person]):
    """Employee"""
    # Role taker
    person: Person
    # Works For
    works_for: Set[Organization] = field(default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))


@dataclass(eq=False)
class Institute(Organization):
    """institute"""
    ...


@dataclass(eq=False)
class Manual(Publication):
    """manual"""
    ...


@dataclass(eq=False)
class Program(Organization):
    """program"""
    ...


@dataclass(eq=False)
class Research(Work):
    """research work"""
    ...


@dataclass(eq=False)
class ResearchGroup(Organization):
    """research group"""
    # has as a research project
    research_project: Set[Research] = field(default_factory=set)


@dataclass(eq=False)
class Software(Publication):
    """software program"""
    # is documented in
    software_documentation: Set[Publication] = field(default_factory=set)
    # is version
    software_version: Optional[str] = field(kw_only=True, default=None)


@dataclass(eq=False)
class Specification(Publication):
    """published specification"""
    ...


@dataclass(eq=False)
class Student(UnivBenchOntologyRole[Person]):
    """student"""
    # Role taker
    person: Person
    # is taking
    takes_course: Set[Course] = field(default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))


@dataclass(eq=False)
class TeachingAssistant(UnivBenchOntologyRole[Person]):
    """university teaching assistant"""
    # Role taker
    person: Person
    # is a teaching assistant for
    teaching_assistant_of: Set[Course] = field(default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))


@dataclass(eq=False)
class University(Organization):
    """university"""
    # has as an alumnus
    has_alumnus: Set[Person] = field(default_factory=set)


@dataclass(eq=False)
class UnofficialPublication(Publication):
    """unnoficial publication"""
    ...


@dataclass(eq=False)
class AdministrativeStaff(Employee):
    """administrative staff worker"""
    ...


@dataclass(eq=False)
class ConferencePaper(Article):
    """conference paper"""
    ...


@dataclass(eq=False)
class Director(Employee):
    """director"""
    # is the head of
    head_of: Set[Program] = field(default_factory=set)


@dataclass(eq=False)
class Faculty(Employee):
    """faculty member"""
    # teaches
    teacher_of: Set[Course] = field(default_factory=set)


@dataclass(eq=False)
class GraduateCourse(Course):
    """Graduate Level Courses"""
    ...


@dataclass(eq=False)
class GraduateStudent(Student):
    """graduate student"""
    # is taking
    takes_course: Set[GraduateCourse] = field(default_factory=set)


@dataclass(eq=False)
class JournalArticle(Article):
    """journal article"""
    ...


@dataclass(eq=False)
class ResearchAssistant(Employee):
    """university research assistant"""
    # Works For
    works_for: Set[ResearchGroup] = field(default_factory=set)


@dataclass(eq=False)
class TechnicalReport(Article):
    """technical report"""
    ...


@dataclass(eq=False)
class UndergraduateStudent(Student):
    """undergraduate student"""
    ...


@dataclass(eq=False)
class ClericalStaff(AdministrativeStaff):
    """clerical staff worker"""
    ...


@dataclass(eq=False)
class Lecturer(UnivBenchOntologyRole[Faculty]):
    """lecturer"""
    # Role taker
    faculty: Faculty

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class PostDoc(UnivBenchOntologyRole[Faculty]):
    """post doctorate"""
    # Role taker
    faculty: Faculty

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class Professor(UnivBenchOntologyRole[Faculty]):
    """professor"""
    # Role taker
    faculty: Faculty
    # is tenured:
    tenured: Optional[bool] = field(kw_only=True, default=None)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class SystemsStaff(AdministrativeStaff):
    """systems staff worker"""
    ...


@dataclass(eq=False)
class AssistantProfessor(Professor):
    """assistant professor"""
    ...


@dataclass(eq=False)
class AssociateProfessor(Professor):
    """associate professor"""
    ...


@dataclass(eq=False)
class Chair(UnivBenchOntologyRole[Professor]):
    """chair"""
    # Role taker
    professor: Professor
    # is the head of
    head_of: Set[Department] = field(default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "professor"))


@dataclass(eq=False)
class Dean(UnivBenchOntologyRole[Professor]):
    """dean"""
    # Role taker
    professor: Professor
    # is the head of
    head_of: Set[College] = field(default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "professor"))


@dataclass(eq=False)
class FullProfessor(Professor):
    """full professor"""
    ...


@dataclass(eq=False)
class VisitingProfessor(UnivBenchOntologyRole[Professor]):
    """visiting professor"""
    # Role taker
    professor: Professor

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "professor"))




# Descriptor assignments
Organization.affiliated_organization_of = AffiliatedOrganizationOf(Organization, 'affiliated_organization_of')
Organization.affiliate_of = AffiliateOf(Organization, 'affiliate_of')
Organization.member = Member(Organization, 'member')
Organization.org_publication = OrgPublication(Organization, 'org_publication')
Organization.sub_organization_of = SubOrganizationOf(Organization, 'sub_organization_of')
Person.advisor = Advisor(Person, 'advisor')
Person.degree_from = DegreeFrom(Person, 'degree_from')
Person.doctoral_degree_from = DoctoralDegreeFrom(Person, 'doctoral_degree_from')
Person.masters_degree_from = MastersDegreeFrom(Person, 'masters_degree_from')
Person.member_of = MemberOf(Person, 'member_of')
Person.undergraduate_degree_from = UndergraduateDegreeFrom(Person, 'undergraduate_degree_from')
Publication.publication_author = PublicationAuthor(Publication, 'publication_author')
Publication.publication_research = PublicationResearch(Publication, 'publication_research')
Schedule.listed_course = ListedCourse(Schedule, 'listed_course')
Employee.works_for = WorksFor(Employee, 'works_for')
ResearchGroup.research_project = ResearchProject(ResearchGroup, 'research_project')
Software.software_documentation = SoftwareDocumentation(Software, 'software_documentation')
Student.takes_course = TakesCourse(Student, 'takes_course')
TeachingAssistant.teaching_assistant_of = TeachingAssistantOf(TeachingAssistant, 'teaching_assistant_of')
University.has_alumnus = HasAlumnus(University, 'has_alumnus')
Director.head_of = HeadOf(Director, 'head_of')
Faculty.teacher_of = TeacherOf(Faculty, 'teacher_of')
GraduateStudent.takes_course = TakesCourse(GraduateStudent, 'takes_course')
ResearchAssistant.works_for = WorksFor(ResearchAssistant, 'works_for')
Chair.head_of = HeadOf(Chair, 'head_of')
Dean.head_of = HeadOf(Dean, 'head_of')
