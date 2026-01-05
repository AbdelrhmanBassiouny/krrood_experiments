"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from .owl2bench_with_predicates_properties import *
from .owl2bench_with_predicates_base import *


# Generated classes
@dataclass(eq=False)
class OWL2BenchOntology(Symbol, ABC):
    """Base class for OWL2Bench"""
    has_code: Optional[Any] = field(kw_only=True, default=None)
    has_id: Optional[Any] = field(kw_only=True, default=None)
    has_name: Optional[Any] = field(kw_only=True, default=None)
    has_office_number: Optional[Any] = field(kw_only=True, default=None)
    has_publication_date: Optional[Any] = field(kw_only=True, default=None)
    has_research_interest: Optional[Any] = field(kw_only=True, default=None)
    # URI of the ontology element - The unique resource identifier (URI) of the ontology element.
    uri: Optional[str] = field(kw_only=True, default=None)
    has_same_home_town_with: Set[Any] = field(default_factory=set)
    is_affiliate_of: Set[Any] = field(default_factory=set)
    knows: Set[Any] = field(default_factory=set)



@dataclass(eq=False)
class CollegeANDhasStudentALLAnonymousClass(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class CollegeDiscipline(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class Course(OWL2BenchOntology):
    is_taught_by: Set[Faculty] = field(default_factory=set)



@dataclass(eq=False)
class EvaluationCommittee(OWL2BenchOntology):
    evaluates: Set[Person] = field(default_factory=set)
    has_committee_members: Set[Person] = field(default_factory=set)



@dataclass(eq=False)
class Interest(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class Organization(OWL2BenchOntology):
    has_dean: Set[Person] = field(default_factory=set)
    has_employee: Set[Employee] = field(default_factory=set)
    has_employee_evaluation_committee: Set[EmployeeEvaluationCommittee] = field(default_factory=set)
    has_evaluation_committee: Set[EvaluationCommittee] = field(default_factory=set)
    has_member: Set[Person] = field(default_factory=set)
    has_part: Set[Organization] = field(default_factory=set)
    has_student: Set[Student] = field(default_factory=set)
    has_student_evaluation_committee: Set[StudentEvaluationCommittee] = field(default_factory=set)
    has_sub_organization: Set[Organization] = field(default_factory=set)
    has_thesis_evaluation_committee: Set[ThesisEvaluationCommittee] = field(default_factory=set)
    is_affiliated_organization_of: Set[Organization] = field(default_factory=set)
    is_part_of: Set[Organization] = field(default_factory=set)
    is_sub_organization_of: Set[Organization] = field(default_factory=set)
    org_publication: Set[Publication] = field(default_factory=set)



@dataclass(eq=False)
class PersonMixinProtocol(OWL2BenchOntology):
    dislikes: Set[Interest]
    evaluated_by: Set[EvaluationCommittee]
    has_advisor: Set[Professor]
    has_age: Optional[Any]
    has_collaboration_with: Set[Person]
    has_degree_from: Set[University]
    has_doctoral_degree_from: Set[University]
    has_email_address: Optional[Any]
    has_first_name: Optional[Any]
    has_last_name: Optional[Any]
    has_major: Set[Any]
    has_master_degree_from: Set[University]
    has_telephone: Optional[Any]
    has_title: Optional[Any]
    has_undergraduate_degree_from: Set[University]
    is_advised_by: Set[Professor]
    is_crazy_about: Set[Interest]
    is_dean_of: Set[Organization]
    is_member_of: Set[Organization]
    likes: Set[Interest]
    loves: Set[Interest]


@dataclass(eq=False)
class Person(PersonMixinProtocol):
    ...


@dataclass(eq=False)
class Program(OWL2BenchOntology):
    """Different programs offered in a department. UG, PG or PhD"""
    ...



@dataclass(eq=False)
class Publication(OWL2BenchOntology):
    has_author: Set[Person] = field(default_factory=set)
    publication_research: Set[Any] = field(default_factory=set)



@dataclass(eq=False)
class StudentANDAnonymousClass(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class Thing(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class Work(OWL2BenchOntology):
    ...



@dataclass(eq=False)
class Article(Publication):
    ...



@dataclass(eq=False)
class BasketBallFan(Person):
    ...



@dataclass(eq=False)
class BasketBallLover(Person):
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
class Department(Organization):
    has_assistant_professor: Set[AssistantProfessor] = field(default_factory=set)
    has_associate_professor: Set[AssociateProfessor] = field(default_factory=set)
    has_clerical_staff: Set[ClericalStaff] = field(default_factory=set)
    has_faculty: Set[Faculty] = field(default_factory=set)
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
class ElectiveCourse(Course):
    ...



@dataclass(eq=False)
class Employee(PersonMixinProtocol, Symbol):
    has_work: Set[Work] = field(default_factory=set)
    is_clerical_staff_of: Set[Organization] = field(default_factory=set)
    is_other_staff_of: Set[Organization] = field(default_factory=set)
    is_supporting_staff_of: Set[Organization] = field(default_factory=set)
    is_system_staff_of: Set[Organization] = field(default_factory=set)
    works_for: Set[Organization] = field(default_factory=set)



@dataclass(eq=False)
class EmployeeEvaluationCommittee(EvaluationCommittee):
    ...



@dataclass(eq=False)
class Engineering(CollegeDiscipline):
    """Engineering"""
    ...



@dataclass(eq=False)
class FineArts(CollegeDiscipline):
    ...



@dataclass(eq=False)
class Game(Interest):
    ...



@dataclass(eq=False)
class HumanitiesAndSocial(CollegeDiscipline):
    """HumanitiesAndSocial"""
    ...



@dataclass(eq=False)
class Institute(Organization):
    ...



@dataclass(eq=False)
class ManORWoman(Person):
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
class PGProgram(Program):
    ...



@dataclass(eq=False)
class Painting(Interest):
    ...



@dataclass(eq=False)
class PeopleWithHobby(Person):
    ...



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
class School(Organization):
    ...



@dataclass(eq=False)
class Science(CollegeDiscipline):
    """Science"""
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
class SportsFan(Person):
    ...



@dataclass(eq=False)
class SportsLover(Person):
    ...



@dataclass(eq=False)
class Student(Person):
    enroll_for: Set[Program] = field(default_factory=set)
    enroll_in: Set[Department] = field(default_factory=set)
    is_student_of: Set[Organization] = field(default_factory=set)
    takes_course: Set[Course] = field(default_factory=set)



@dataclass(eq=False)
class StudentEvaluationCommittee(EvaluationCommittee):
    ...



@dataclass(eq=False)
class T20CricketFan(Person):
    ...



@dataclass(eq=False)
class TeachingCourse(Work):
    ...



@dataclass(eq=False)
class Travelling(Interest):
    ...



@dataclass(eq=False)
class UGCourse(Course):
    """Mandatory courses for all UG students"""
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
class AeronauticalEngineering(Engineering):
    ...



@dataclass(eq=False)
class Anthropology(HumanitiesAndSocial):
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
class Economics(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class ElectricalEngineering(Engineering):
    ...



@dataclass(eq=False)
class English(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class Faculty(Employee):
    is_faculty_of: Set[Organization] = field(default_factory=set)
    teaches_course: Set[Course] = field(default_factory=set)



@dataclass(eq=False)
class FinancialAndAccountingManagement(Management):
    ...



@dataclass(eq=False)
class FootBall(Sports):
    ...



@dataclass(eq=False)
class Geosciences(Science):
    ...



@dataclass(eq=False)
class History(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class HumanResourceManagement(Management):
    ...



@dataclass(eq=False)
class Humanities(HumanitiesAndSocial):
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
class LeisureStudent(Student, StudentANDAnonymousClass):
    ...



@dataclass(eq=False)
class Linguistics(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class Man(ManORWoman):
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
class ModernLanguages(HumanitiesAndSocial):
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
class PerformingArts(FineArts):
    ...



@dataclass(eq=False)
class PersonANDenrollInSOMEDepartment(Student):
    ...



@dataclass(eq=False)
class PersonANDisCrazyAboutSOMEBasketBall(BasketBallFan):
    ...



@dataclass(eq=False)
class PersonANDisCrazyAboutSOMESports(SportsFan):
    ...



@dataclass(eq=False)
class PersonANDlikesSOMEInterest(PeopleWithHobby):
    ...



@dataclass(eq=False)
class PersonANDlovesSOMEBasketBall(BasketBallLover):
    ...



@dataclass(eq=False)
class PersonANDlovesSOMESports(SportsLover):
    ...



@dataclass(eq=False)
class PersonANDworksForSOMEOrganization(Employee):
    ...



@dataclass(eq=False)
class PetroleumlEngineering(Engineering):
    ...



@dataclass(eq=False)
class PhDStudent(Student):
    ...



@dataclass(eq=False)
class Philosophy(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class Physics(Science):
    ...



@dataclass(eq=False)
class ProjectManagement(Management):
    ...



@dataclass(eq=False)
class Psychology(HumanitiesAndSocial):
    ...



@dataclass(eq=False)
class PublicRelationsManagement(Management):
    ...



@dataclass(eq=False)
class Religions(HumanitiesAndSocial):
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
class ScienceStudent(Student):
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
class TeachingAssistant(Student):
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
class ThesisEvaluationCommittee(StudentEvaluationCommittee):
    """Evaluates PhD students"""
    ...



@dataclass(eq=False)
class UGStudent(Student):
    ...



@dataclass(eq=False)
class Woman(ManORWoman):
    ...



@dataclass(eq=False)
class WomanCollege(College, CollegeANDhasStudentALLAnonymousClass):
    ...



@dataclass(eq=False)
class ClericalStaff(SupportingStaff):
    ...



@dataclass(eq=False)
class EmployeeANDteachesCourseSOMECourse(Faculty):
    ...



@dataclass(eq=False)
class Lecturer(Faculty):
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
    tenured: Optional[bool] = field(kw_only=True, default=None)



@dataclass(eq=False)
class StudentANDenrollForSOMEPGProgram(PGStudent):
    ...



@dataclass(eq=False)
class StudentANDenrollForSOMEPhDProgram(PhDStudent):
    ...



@dataclass(eq=False)
class StudentANDenrollForSOMEUGProgram(UGStudent):
    ...



@dataclass(eq=False)
class StudentANDhasMajorSOMEScience(ScienceStudent):
    ...



@dataclass(eq=False)
class StudentANDisTeachingAssistantOfSOMECourse(TeachingAssistant):
    ...



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
class FullProfessor(Professor):
    is_full_professor_of: Set[Department] = field(default_factory=set)
    is_head_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class VisitingProfessor(Professor):
    is_visiting_professor_of: Set[Department] = field(default_factory=set)



@dataclass(eq=False)
class Chair(FullProfessor):
    ...



@dataclass(eq=False)
class Dean(FullProfessor):
    ...



@dataclass(eq=False)
class Director(FullProfessor):
    ...



