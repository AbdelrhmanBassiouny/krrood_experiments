"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing_extensions import List, Optional, Union, Any, Set, Generic, TypeVar, Type

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
class PublicationAuthor(PropertyDescriptor):
    """was written by"""


@dataclass
class PublicationResearch(PropertyDescriptor):
    """is about"""


@dataclass
class ResearchProject(PropertyDescriptor):
    """has as a research project"""


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
@dataclass
class UnivBenchOntology(Symbol):
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

@dataclass
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

    def __hash__(self):
        return hash(id(self))



@dataclass
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

    def __hash__(self):
        return hash(id(self))



@dataclass
class Publication(UnivBenchOntology):
    """publication"""
    # was written by
    publication_author: Set[Person] = field(default_factory=set)
    # was written on
    publication_date: Optional[str] = field(kw_only=True, default=None)
    # is about
    publication_research: Set[Research] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Schedule(UnivBenchOntology):
    """schedule"""
    # lists as a course
    listed_course: Set[Course] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class UnivBenchOntologyRole(Role[T], UnivBenchOntology):
    """Role class which represents a role that a persistent identifier can take on in a certain context"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Work(UnivBenchOntology):
    """Work"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Article(Publication):
    """article"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Book(Publication):
    """book"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class College(Organization):
    """school"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Course(Work):
    """teaching course"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Department(Organization):
    """university department"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Director(Person):
    """director"""
    # is the head of
    head_of: Set[Program] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Employee(Person, UnivBenchOntologyRole[Person]):
    """Employee"""
    # Role taker
    person: Optional[Person] = field(kw_only=True, default=None)
    # Works For
    works_for: Set[Organization] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Institute(Organization):
    """institute"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Manual(Publication):
    """manual"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Program(Organization):
    """program"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Research(Work):
    """research work"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class ResearchGroup(Organization):
    """research group"""
    # has as a research project
    research_project: Set[Research] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Software(Publication):
    """software program"""
    # is documented in
    software_documentation: Set[Publication] = field(default_factory=set)
    # is version
    software_version: Optional[str] = field(kw_only=True, default=None)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Specification(Publication):
    """published specification"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Student(Person):
    """student"""
    # is taking
    takes_course: Set[Course] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class TeachingAssistant(Person, UnivBenchOntologyRole[Person]):
    """university teaching assistant"""
    # Role taker
    person: Optional[Person] = field(kw_only=True, default=None)
    # is a teaching assistant for
    teaching_assistant_of: Set[Course] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class University(Organization):
    """university"""
    # has as an alumnus
    has_alumnus: Set[Person] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class UnofficialPublication(Publication):
    """unnoficial publication"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class AdministrativeStaff(Employee):
    """administrative staff worker"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class ConferencePaper(Article):
    """conference paper"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Faculty(Employee):
    """faculty member"""
    # teaches
    teacher_of: Set[Course] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class GraduateCourse(Course):
    """Graduate Level Courses"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class GraduateStudent(Person, Student):
    """graduate student"""
    # is taking
    takes_course: Set[GraduateCourse] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class JournalArticle(Article):
    """journal article"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class ResearchAssistant(Person, Employee):
    """university research assistant"""
    # Works For
    works_for: Set[ResearchGroup] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class TechnicalReport(Article):
    """technical report"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class UndergraduateStudent(Student):
    """undergraduate student"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class ClericalStaff(AdministrativeStaff):
    """clerical staff worker"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Lecturer(Faculty):
    """lecturer"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class PostDoc(Faculty):
    """post doctorate"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Professor(Faculty):
    """professor"""
    # is tenured:
    tenured: Optional[bool] = field(kw_only=True, default=None)

    def __hash__(self):
        return hash(id(self))



@dataclass
class SystemsStaff(AdministrativeStaff):
    """systems staff worker"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class AssistantProfessor(Professor):
    """assistant professor"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class AssociateProfessor(Professor):
    """associate professor"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class Chair(Professor, Person):
    """chair"""
    # is the head of
    head_of: Set[Department] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class Dean(Professor):
    """dean"""
    # is the head of
    head_of: Set[College] = field(default_factory=set)

    def __hash__(self):
        return hash(id(self))



@dataclass
class FullProfessor(Professor):
    """full professor"""
    ...

    def __hash__(self):
        return hash(id(self))



@dataclass
class VisitingProfessor(Professor):
    """visiting professor"""
    ...

    def __hash__(self):
        return hash(id(self))





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
Director.head_of = HeadOf(Director, 'head_of')
Employee.works_for = WorksFor(Employee, 'works_for')
ResearchGroup.research_project = ResearchProject(ResearchGroup, 'research_project')
Software.software_documentation = SoftwareDocumentation(Software, 'software_documentation')
Student.takes_course = TakesCourse(Student, 'takes_course')
TeachingAssistant.teaching_assistant_of = TeachingAssistantOf(TeachingAssistant, 'teaching_assistant_of')
University.has_alumnus = HasAlumnus(University, 'has_alumnus')
Faculty.teacher_of = TeacherOf(Faculty, 'teacher_of')
GraduateStudent.takes_course = TakesCourse(GraduateStudent, 'takes_course')
ResearchAssistant.works_for = WorksFor(ResearchAssistant, 'works_for')
Chair.head_of = HeadOf(Chair, 'head_of')
Dean.head_of = HeadOf(Dean, 'head_of')
