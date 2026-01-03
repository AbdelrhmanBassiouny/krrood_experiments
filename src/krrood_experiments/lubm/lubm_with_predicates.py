"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, Field
from functools import lru_cache

from krrood.class_diagrams.utils import Role
from .lubm_with_predicates_properties import *
from .lubm_with_predicates_base import *

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
class Employee(Role[Person], Symbol):
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
class Student(Role[Person], Symbol):
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
class TeachingAssistant(Role[Person], Symbol):
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
class Lecturer(Role[Faculty], Symbol):
    """lecturer"""
    # Role taker
    faculty: Faculty

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class PostDoc(Role[Faculty], Symbol):
    """post doctorate"""
    # Role taker
    faculty: Faculty

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class Professor(Role[Faculty], Symbol):
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
class Chair(Role[Professor], Symbol):
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
class Dean(Role[Professor], Symbol):
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
class VisitingProfessor(Role[Professor], Symbol):
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
