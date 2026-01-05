"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

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
    affiliate_of: Set[Person] = field(default_factory=set)
    # is affiliated with
    affiliated_organization_of: Set[Organization] = field(default_factory=set)
    # has as a member
    member: Set[Person] = field(default_factory=set)
    # publishes
    org_publication: Set[Publication] = field(default_factory=set)
    # is part of
    sub_organization_of: Set[Organization] = field(default_factory=set)



@dataclass(eq=False)
class PersonMixinProtocol(UnivBenchOntology):
    """person"""
    # is being advised by
    advisor: Set[Professor]
    # is age
    age: Optional[int]
    # has a degree from
    degree_from: Set[University]
    # has a doctoral degree from
    doctoral_degree_from: Set[University]
    # can be reached at
    email_address: Optional[str]
    # has a masters degree from
    masters_degree_from: Set[University]
    # member of
    member_of: Set[Organization]
    # telephone number
    telephone: Optional[str]
    # title
    title: Optional[str]
    # has an undergraduate degree from
    undergraduate_degree_from: Set[University]


@dataclass(eq=False)
class Person(PersonMixinProtocol):
    ...


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
class Employee(PersonMixinProtocol, Symbol):
    """Employee"""
    # Works For
    works_for: Set[Organization] = field(default_factory=set)



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
class Student(PersonMixinProtocol, Symbol):
    """student"""
    # is taking
    takes_course: Set[Course] = field(default_factory=set)



@dataclass(eq=False)
class TeachingAssistant(PersonMixinProtocol, Symbol):
    """university teaching assistant"""
    # is a teaching assistant for
    teaching_assistant_of: Set[Course] = field(default_factory=set)



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
class FacultyMixinProtocol(Employee):
    """faculty member"""
    # teaches
    teacher_of: Set[Course]


@dataclass(eq=False)
class Faculty(FacultyMixinProtocol):
    ...


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
class Lecturer(FacultyMixinProtocol, Symbol):
    """lecturer"""



@dataclass(eq=False)
class PostDoc(FacultyMixinProtocol, Symbol):
    """post doctorate"""



@dataclass(eq=False)
class ProfessorMixinProtocol(FacultyMixinProtocol, Symbol):
    """professor"""
    # is tenured:
    tenured: Optional[bool]


@dataclass(eq=False)
class Professor(ProfessorMixinProtocol):
    ...


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
class Chair(ProfessorMixinProtocol, Symbol):
    """chair"""
    # is the head of
    head_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class Dean(ProfessorMixinProtocol, Symbol):
    """dean"""
    # is the head of
    head_of: Set[College] = field(default_factory=set)



@dataclass(eq=False)
class FullProfessor(Professor):
    """full professor"""
    ...



@dataclass(eq=False)
class VisitingProfessor(ProfessorMixinProtocol, Symbol):
    """visiting professor"""



