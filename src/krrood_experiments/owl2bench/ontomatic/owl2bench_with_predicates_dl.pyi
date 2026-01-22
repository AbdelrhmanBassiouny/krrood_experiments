"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from .owl2bench_with_predicates_dl_properties import *
from .owl2bench_with_predicates_dl_base import *


# Generated classes
@dataclass(eq=False)
class OWL2BenchThing(Symbol):
    """Base class for OWL2Bench"""
    has_code: Optional[str] = field(kw_only=True, default=None)
    has_id: Optional[str] = field(kw_only=True, default=None)
    has_name: Optional[str] = field(kw_only=True, default=None)
    has_office_number: Optional[str] = field(kw_only=True, default=None)
    has_research_interest: Optional[str] = field(kw_only=True, default=None)
    has_work: Set[Work] = field(default_factory=set)
    is_affiliate_of: Set[OWL2BenchThing] = field(default_factory=set)
    knows: Set[OWL2BenchThing] = field(default_factory=set)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)
    advises: Set[OWL2BenchThing] = field(default_factory=set)



@dataclass(eq=False)
class CollegeDiscipline(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Interest(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Organization(OWL2BenchThing):
    has_dean: Set[Person] = field(default_factory=set)
    has_employee: Set[Employee] = field(default_factory=set)
    has_faculty: Set[Faculty] = field(default_factory=set)
    has_member: Set[Person] = field(default_factory=set)
    has_part: Set[Organization] = field(default_factory=set)
    has_student: Set[Student] = field(default_factory=set)
    has_sub_organization: Set[Organization] = field(default_factory=set)
    is_affiliated_organization_of: Set[Organization] = field(default_factory=set)
    is_part_of: Set[Organization] = field(default_factory=set)
    is_sub_organization_of: Set[Organization] = field(default_factory=set)
    org_publication: Set[Publication] = field(default_factory=set)



@dataclass(eq=False)
class PersonMixinProtocol(OWL2BenchThing):
    dislikes: Set[OWL2BenchThing]
    has_advisor: Set[Person]
    has_age: Optional[str]
    has_collaboration_with: Set[Person]
    has_degree_from: Set[University]
    has_doctoral_degree_from: Set[University]
    has_email_address: Optional[str]
    has_first_name: Optional[str]
    has_last_name: Optional[str]
    has_major: Set[Union[Engineering, FineArts, HumanitiesAndSocialScience, Management, Science]]
    has_master_degree_from: Set[University]
    has_same_home_town_with: Set[Person]
    has_telephone: Optional[str]
    has_title: Optional[str]
    has_undergraduate_degree_from: Set[University]
    is_advised_by: Set[Person]
    is_advisor_of: Set[Person]
    is_crazy_about: Set[OWL2BenchThing]
    is_dean_of: Set[Organization]
    is_member_of: Set[Organization]
    likes: Set[OWL2BenchThing]
    loves: Set[OWL2BenchThing]


@dataclass(eq=False)
class Person(PersonMixinProtocol):
    ...


@dataclass(eq=False)
class Program(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Publication(OWL2BenchThing):
    has_author: Set[Person] = field(default_factory=set)
    has_publication_date: Optional[str] = field(kw_only=True, default=None)
    publication_research: Set[OWL2BenchThing] = field(default_factory=set)



@dataclass(eq=False)
class SelfAwarePerson(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Thing(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Work(OWL2BenchThing):
    ...



@dataclass(eq=False)
class Article(Publication):
    ...



@dataclass(eq=False)
class Book(Publication):
    ...



@dataclass(eq=False)
class College(Organization):
    has_college_discipline: Set[CollegeDiscipline] = field(default_factory=set)
    has_department: Set[Department] = field(default_factory=set)
    is_college_of: Set[University] = field(default_factory=set)
    is_women_college_of: Set[University] = field(default_factory=set)



@dataclass(eq=False)
class Course(Work):
    is_taught_by: Set[Faculty] = field(default_factory=set)



@dataclass(eq=False)
class Department(Organization):
    has_assistant_professor: Set[AssistantProfessor] = field(default_factory=set)
    has_associate_professor: Set[AssociateProfessor] = field(default_factory=set)
    has_clerical_staff: Set[ClericalStaff] = field(default_factory=set)
    has_full_professor: Set[FullProfessor] = field(default_factory=set)
    has_head: Set[FullProfessor] = field(default_factory=set)
    has_lecturer: Set[Lecturer] = field(default_factory=set)
    has_other_staff: Set[OtherStaff] = field(default_factory=set)
    has_pg_program: Set[PGProgram] = field(default_factory=set)
    has_ph_d_program: Set[PhDProgram] = field(default_factory=set)
    has_post_doc: Set[PostDoc] = field(default_factory=set)
    has_professor: Set[Professor] = field(default_factory=set)
    has_program: Set[Program] = field(default_factory=set)
    has_supporting_staff: Set[SupportingStaff] = field(default_factory=set)
    has_system_staff: Set[SystemStaff] = field(default_factory=set)
    has_ug_program: Set[UGProgram] = field(default_factory=set)
    has_visiting_professor: Set[VisitingProfessor] = field(default_factory=set)
    is_department_of: Set[College] = field(default_factory=set)
    offer_course: Set[Course] = field(default_factory=set)



@dataclass(eq=False)
class Employee(PersonMixinProtocol, Symbol):
    is_clerical_staff_of: Set[Organization] = field(default_factory=set)
    is_other_staff_of: Set[Organization] = field(default_factory=set)
    is_supporting_staff_of: Set[Organization] = field(default_factory=set)
    is_system_staff_of: Set[Organization] = field(default_factory=set)
    works_for: Set[Organization] = field(default_factory=set)



@dataclass(eq=False)
class Engineering(CollegeDiscipline):
    ...



@dataclass(eq=False)
class FineArts(CollegeDiscipline):
    ...



@dataclass(eq=False)
class Game(Interest):
    ...



@dataclass(eq=False)
class HumanitiesAndSocialScience(CollegeDiscipline):
    ...



@dataclass(eq=False)
class Institute(Organization):
    ...



@dataclass(eq=False)
class Man(Person):
    ...



@dataclass(eq=False)
class Management(CollegeDiscipline):
    ...



@dataclass(eq=False)
class Manual(Publication):
    ...



@dataclass(eq=False)
class Movie(Interest):
    ...



@dataclass(eq=False)
class Music(Interest):
    ...



@dataclass(eq=False)
class NonScience(CollegeDiscipline):
    ...



@dataclass(eq=False)
class PGProgram(Program):
    ...



@dataclass(eq=False)
class Painting(Interest):
    ...



@dataclass(eq=False)
class PeopleWithHobby(PersonMixinProtocol, Symbol):



@dataclass(eq=False)
class PhDProgram(Program):
    ...



@dataclass(eq=False)
class Reading(Interest):
    ...



@dataclass(eq=False)
class ResearchGroup(Organization):
    has_research_assistant: Set[ResearchAssistant] = field(default_factory=set)
    has_research_project: Set[ResearchProject] = field(default_factory=set)
    is_research_group_of: Set[University] = field(default_factory=set)



@dataclass(eq=False)
class ResearchProject(Work):
    ...



@dataclass(eq=False)
class Science(CollegeDiscipline):
    ...



@dataclass(eq=False)
class Software(Publication):
    ...



@dataclass(eq=False)
class Specification(Publication):
    ...



@dataclass(eq=False)
class Sports(Interest):
    ...



@dataclass(eq=False)
class StudentMixinProtocol(PersonMixinProtocol, Symbol):
    enroll_for: Set[Program]
    enroll_in: Set[Department]
    is_student_of: Set[Organization]
    takes_course: Set[Course]


@dataclass(eq=False)
class Student(StudentMixinProtocol):
    ...


@dataclass(eq=False)
class Travelling(Interest):
    ...



@dataclass(eq=False)
class UGProgram(Program):
    ...



@dataclass(eq=False)
class University(Organization):
    has_alumnus: Set[Person] = field(default_factory=set)
    has_college: Set[College] = field(default_factory=set)
    has_research_group: Set[ResearchGroup] = field(default_factory=set)
    has_women_college: Set[College] = field(default_factory=set)



@dataclass(eq=False)
class UnofficialPublication(Publication):
    ...



@dataclass(eq=False)
class Woman(Person):
    ...



@dataclass(eq=False)
class AeronauticalEngineering(Engineering):
    ...



@dataclass(eq=False)
class Anthropology(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class Architecture(FineArts):
    ...



@dataclass(eq=False)
class AsianArts(FineArts):
    ...



@dataclass(eq=False)
class Astronomy(Science):
    ...



@dataclass(eq=False)
class Badminton(Sports):
    ...



@dataclass(eq=False)
class BasketBall(Sports):
    ...



@dataclass(eq=False)
class Biology(Science):
    ...



@dataclass(eq=False)
class BiomedicalEngineering(Engineering):
    ...



@dataclass(eq=False)
class ChemicalEngineering(Engineering):
    ...



@dataclass(eq=False)
class Chemistry(Science):
    ...



@dataclass(eq=False)
class CivilEngineering(Engineering):
    ...



@dataclass(eq=False)
class CoEdCollege(College):
    ...



@dataclass(eq=False)
class ComputerEngineering(Engineering):
    ...



@dataclass(eq=False)
class ComputerScience(Science):
    ...



@dataclass(eq=False)
class ConferencePaper(Article):
    ...



@dataclass(eq=False)
class Cricket(Sports):
    ...



@dataclass(eq=False)
class DesignManagement(Management):
    ...



@dataclass(eq=False)
class Drama(FineArts):
    ...



@dataclass(eq=False)
class Economics(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class ElectiveCourse(Course):
    ...



@dataclass(eq=False)
class ElectricalEngineering(Engineering):
    ...



@dataclass(eq=False)
class English(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class FacultyMixinProtocol(Employee):
    is_faculty_of: Set[Organization]
    teaches_course: Set[Course]


@dataclass(eq=False)
class Faculty(FacultyMixinProtocol):
    ...


@dataclass(eq=False)
class FinancialAndAccountingManagement(Management):
    ...



@dataclass(eq=False)
class Football(Sports):
    ...



@dataclass(eq=False)
class Geosciences(Science):
    ...



@dataclass(eq=False)
class History(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class HumanResourceManagement(Management):
    ...



@dataclass(eq=False)
class Humanities(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class IndustryEngineering(Engineering):
    ...



@dataclass(eq=False)
class JournalArticle(Article):
    ...



@dataclass(eq=False)
class LatinArts(FineArts):
    ...



@dataclass(eq=False)
class LeisureStudent(StudentMixinProtocol, Symbol):



@dataclass(eq=False)
class Linguistics(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class MarineScience(Science):
    ...



@dataclass(eq=False)
class MarketingManagement(Management):
    ...



@dataclass(eq=False)
class MaterialScienceEngineering(Engineering):
    ...



@dataclass(eq=False)
class MaterialsScience(Science):
    ...



@dataclass(eq=False)
class Mathematics(Science):
    ...



@dataclass(eq=False)
class MechanicalEngineering(Engineering):
    ...



@dataclass(eq=False)
class MediaArtsAndSciences(FineArts):
    ...



@dataclass(eq=False)
class MedievalArts(FineArts):
    ...



@dataclass(eq=False)
class ModernArts(FineArts):
    ...



@dataclass(eq=False)
class ModernLanguages(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class MusicsClass(FineArts):
    ...



@dataclass(eq=False)
class OperationsManagement(Management):
    ...



@dataclass(eq=False)
class PGStudent(Student):
    ...



@dataclass(eq=False)
class PeopleWithManyHobbies(PeopleWithHobby):



@dataclass(eq=False)
class PerformingArts(FineArts):
    ...



@dataclass(eq=False)
class PetroleumlEngineering(Engineering):
    ...



@dataclass(eq=False)
class PhDStudent(Student):
    ...



@dataclass(eq=False)
class Philosophy(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class Physics(Science):
    ...



@dataclass(eq=False)
class ProjectManagement(Management):
    ...



@dataclass(eq=False)
class Psychology(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class PublicRelationsManagement(Management):
    ...



@dataclass(eq=False)
class Religions(HumanitiesAndSocialScience):
    ...



@dataclass(eq=False)
class ResearchAssistant(Employee):
    is_research_assistant_of: Set[ResearchGroup] = field(default_factory=set)



@dataclass(eq=False)
class RiskManagement(Management):
    ...



@dataclass(eq=False)
class SalesManagement(Management):
    ...



@dataclass(eq=False)
class Soccer(Sports):
    ...



@dataclass(eq=False)
class Statistics(Science):
    ...



@dataclass(eq=False)
class SupplyChainManagement(Management):
    ...



@dataclass(eq=False)
class SupportingStaff(Employee):
    ...



@dataclass(eq=False)
class Swimming(Sports):
    ...



@dataclass(eq=False)
class T20CricketFan(PeopleWithHobby):



@dataclass(eq=False)
class TeachingAssistant(StudentMixinProtocol, Symbol):
    is_teaching_assistant_of: Set[Course] = field(default_factory=set)



@dataclass(eq=False)
class TechnicalReport(Article):
    ...



@dataclass(eq=False)
class Tennis(Sports):
    ...



@dataclass(eq=False)
class TheatreAndDance(FineArts):
    ...



@dataclass(eq=False)
class UGCourse(Course):
    ...



@dataclass(eq=False)
class UGStudent(Student):
    ...



@dataclass(eq=False)
class WomenCollege(College):
    ...



@dataclass(eq=False)
class ClericalStaff(SupportingStaff):
    ...



@dataclass(eq=False)
class Lecturer(FacultyMixinProtocol, Symbol):
    is_lecturer_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class OtherStaff(SupportingStaff):
    ...



@dataclass(eq=False)
class PostDoc(Faculty):
    is_post_doc_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class Professor(Faculty):
    is_professor_of: Set[Department] = field(default_factory=set)
    tenured: Set[OWL2BenchThing] = field(default_factory=set)



@dataclass(eq=False)
class SystemStaff(SupportingStaff):
    ...



@dataclass(eq=False)
class AssistantProfessor(Professor):
    is_assistant_professor_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class AssociateProfessor(Professor):
    is_associate_professor_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class FullProfessorMixinProtocol(Professor):
    is_full_professor_of: Set[Department]
    is_head_of: Set[Department]


@dataclass(eq=False)
class FullProfessor(FullProfessorMixinProtocol):
    ...


@dataclass(eq=False)
class VisitingProfessor(Professor):
    is_visiting_professor_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class Chair(FullProfessorMixinProtocol, Symbol):



@dataclass(eq=False)
class Dean(FullProfessorMixinProtocol, Symbol):



@dataclass(eq=False)
class Director(FullProfessorMixinProtocol, Symbol):



