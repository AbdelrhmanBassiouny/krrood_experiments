"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, Field
from functools import lru_cache

from krrood.class_diagrams.utils import Role
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
    has_advisor: Set[Any] = field(default_factory=set)
    has_same_home_town_with: Set[Any] = field(default_factory=set)
    is_affiliate_of: Set[Any] = field(default_factory=set)
    knows: Set[Any] = field(default_factory=set)


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
class Man(OWL2BenchOntology):
    ...


@dataclass(eq=False)
class Organization(OWL2BenchOntology):
    has_assistant_professor: Set[Person] = field(default_factory=set)
    has_associate_professor: Set[Person] = field(default_factory=set)
    has_college: Set[Organization] = field(default_factory=set)
    has_dean: Set[Person] = field(default_factory=set)
    has_department: Set[Organization] = field(default_factory=set)
    has_employee: Set[Person] = field(default_factory=set)
    has_employee_evaluation_committee: Set[EvaluationCommittee] = field(default_factory=set)
    has_evaluation_committee: Set[EvaluationCommittee] = field(default_factory=set)
    has_faculty: Set[Person] = field(default_factory=set)
    has_full_professor: Set[Person] = field(default_factory=set)
    has_head: Set[Person] = field(default_factory=set)
    has_lecturer: Set[Person] = field(default_factory=set)
    has_member: Set[Person] = field(default_factory=set)
    has_part: Set[Organization] = field(default_factory=set)
    has_post_doc: Set[Person] = field(default_factory=set)
    has_professor: Set[Person] = field(default_factory=set)
    has_research_assistant: Set[Person] = field(default_factory=set)
    has_research_group: Set[Organization] = field(default_factory=set)
    has_student: Set[Person] = field(default_factory=set)
    has_student_evaluation_committee: Set[EvaluationCommittee] = field(default_factory=set)
    has_sub_organization: Set[Organization] = field(default_factory=set)
    has_thesis_evaluation_committee: Set[EvaluationCommittee] = field(default_factory=set)
    has_visiting_professor: Set[Person] = field(default_factory=set)
    is_affiliated_organization_of: Set[Organization] = field(default_factory=set)
    is_college_of: Set[Organization] = field(default_factory=set)
    is_department_of: Set[Organization] = field(default_factory=set)
    is_part_of: Set[Organization] = field(default_factory=set)
    is_research_group_of: Set[Organization] = field(default_factory=set)
    is_sub_organization_of: Set[Organization] = field(default_factory=set)
    org_publication: Set[Publication] = field(default_factory=set)


@dataclass(eq=False)
class Person(OWL2BenchOntology):
    dislikes: Set[Interest] = field(default_factory=set)
    evaluated_by: Set[EvaluationCommittee] = field(default_factory=set)
    has_age: Optional[Any] = field(kw_only=True, default=None)
    has_collaboration_with: Set[Person] = field(default_factory=set)
    has_degree_from: Set[University] = field(default_factory=set)
    has_doctoral_degree_from: Set[University] = field(default_factory=set)
    has_email_address: Optional[Any] = field(kw_only=True, default=None)
    has_first_name: Optional[Any] = field(kw_only=True, default=None)
    has_last_name: Optional[Any] = field(kw_only=True, default=None)
    has_major: Set[Any] = field(default_factory=set)
    has_master_degree_from: Set[University] = field(default_factory=set)
    has_telephone: Optional[Any] = field(kw_only=True, default=None)
    has_title: Optional[Any] = field(kw_only=True, default=None)
    has_undergraduate_degree_from: Set[University] = field(default_factory=set)
    is_advised_by: Set[Professor] = field(default_factory=set)
    is_assistant_professor_of: Set[Organization] = field(default_factory=set)
    is_associate_professor_of: Set[Organization] = field(default_factory=set)
    is_crazy_about: Set[Interest] = field(default_factory=set)
    is_dean_of: Set[Organization] = field(default_factory=set)
    is_faculty_of: Set[Organization] = field(default_factory=set)
    is_full_professor_of: Set[Organization] = field(default_factory=set)
    is_head_of: Set[Organization] = field(default_factory=set)
    is_lecturer_of: Set[Organization] = field(default_factory=set)
    is_member_of: Set[Organization] = field(default_factory=set)
    is_post_doc_of: Set[Organization] = field(default_factory=set)
    is_professor_of: Set[Organization] = field(default_factory=set)
    is_research_assistant_of: Set[Organization] = field(default_factory=set)
    is_student_of: Set[Organization] = field(default_factory=set)
    is_visiting_professor_of: Set[Organization] = field(default_factory=set)
    likes: Set[Interest] = field(default_factory=set)
    loves: Set[Interest] = field(default_factory=set)
    works_for: Set[Organization] = field(default_factory=set)


@dataclass(eq=False)
class Program(OWL2BenchOntology):
    """Different programs offered in a department. UG, PG or PhD"""
    ...


@dataclass(eq=False)
class Publication(OWL2BenchOntology):
    has_author: Set[Person] = field(default_factory=set)
    publication_research: Set[Any] = field(default_factory=set)


@dataclass(eq=False)
class Thing(OWL2BenchOntology):
    ...


@dataclass(eq=False)
class Woman(OWL2BenchOntology):
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
    is_women_college_of: Set[Organization] = field(default_factory=set)


@dataclass(eq=False)
class Department(Organization):
    has_clerical_staff: Set[Person] = field(default_factory=set)
    has_other_staff: Set[Person] = field(default_factory=set)
    has_pg_program: Set[Program] = field(default_factory=set)
    has_ph_d_program: Set[Program] = field(default_factory=set)
    has_program: Set[Program] = field(default_factory=set)
    has_supporting_staff: Set[Person] = field(default_factory=set)
    has_system_staff: Set[Person] = field(default_factory=set)
    has_ug_program: Set[Program] = field(default_factory=set)
    offer_course: Set[Course] = field(default_factory=set)


@dataclass(eq=False)
class ElectiveCourse(Course):
    ...


@dataclass(eq=False)
class Employee(Person):
    has_work: Set[Work] = field(default_factory=set)
    is_clerical_staff_of: Set[Organization] = field(default_factory=set)
    is_other_staff_of: Set[Organization] = field(default_factory=set)
    is_supporting_staff_of: Set[Organization] = field(default_factory=set)
    is_system_staff_of: Set[Organization] = field(default_factory=set)


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
    has_research_project: Set[Work] = field(default_factory=set)


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
    enroll_in: Set[Organization] = field(default_factory=set)
    takes_course: Set[Course] = field(default_factory=set)


@dataclass(eq=False)
class StudentEvaluationCommittee(EvaluationCommittee):
    ...


@dataclass(eq=False)
class T20CricketFan(Person):
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
    has_women_college: Set[Organization] = field(default_factory=set)


@dataclass(eq=False)
class UnofficialPublication(Publication):
    ...


@dataclass(eq=False)
class Work(Course):
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
    teaches_course: Set[Union[Course, Work]] = field(default_factory=set)


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
class LeisureStudent(Student):
    ...


@dataclass(eq=False)
class Linguistics(HumanitiesAndSocial):
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
    ...


@dataclass(eq=False)
class ResearchProject(Work):
    ...


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
class TeachingCourse(Work):
    ...


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
class WomanCollege(College):
    ...


@dataclass(eq=False)
class ClericalStaff(SupportingStaff):
    ...


@dataclass(eq=False)
class Lecturer(Faculty):
    ...


@dataclass(eq=False)
class OtherStaff(SupportingStaff):
    ...


@dataclass(eq=False)
class PostDoc(Faculty):
    ...


@dataclass(eq=False)
class Professor(Faculty):
    tenured: Optional[bool] = field(kw_only=True, default=None)


@dataclass(eq=False)
class SystemStaff(SupportingStaff):
    ...


@dataclass(eq=False)
class AssistantProfessor(Professor):
    ...


@dataclass(eq=False)
class AssociateProfessor(Professor):
    ...


@dataclass(eq=False)
class FullProfessor(Professor):
    ...


@dataclass(eq=False)
class VisitingProfessor(Professor):
    ...


@dataclass(eq=False)
class Chair(FullProfessor):
    ...


@dataclass(eq=False)
class Dean(FullProfessor):
    ...


@dataclass(eq=False)
class Director(FullProfessor):
    ...




# Descriptor assignments
OWL2BenchOntology.has_advisor = HasAdvisor(OWL2BenchOntology, 'has_advisor')
OWL2BenchOntology.has_same_home_town_with = HasSameHomeTownWith(OWL2BenchOntology, 'has_same_home_town_with')
OWL2BenchOntology.is_affiliate_of = IsAffiliateOf(OWL2BenchOntology, 'is_affiliate_of')
OWL2BenchOntology.knows = Knows(OWL2BenchOntology, 'knows')
Course.is_taught_by = IsTaughtBy(Course, 'is_taught_by')
EvaluationCommittee.evaluates = Evaluates(EvaluationCommittee, 'evaluates')
EvaluationCommittee.has_committee_members = HasCommitteeMembers(EvaluationCommittee, 'has_committee_members')
Organization.has_assistant_professor = HasAssistantProfessor(Organization, 'has_assistant_professor')
Organization.has_associate_professor = HasAssociateProfessor(Organization, 'has_associate_professor')
Organization.has_college = HasCollege(Organization, 'has_college')
Organization.has_dean = HasDean(Organization, 'has_dean')
Organization.has_department = HasDepartment(Organization, 'has_department')
Organization.has_employee = HasEmployee(Organization, 'has_employee')
Organization.has_employee_evaluation_committee = HasEmployeeEvaluationCommittee(Organization, 'has_employee_evaluation_committee')
Organization.has_evaluation_committee = HasEvaluationCommittee(Organization, 'has_evaluation_committee')
Organization.has_faculty = HasFaculty(Organization, 'has_faculty')
Organization.has_full_professor = HasFullProfessor(Organization, 'has_full_professor')
Organization.has_head = HasHead(Organization, 'has_head')
Organization.has_lecturer = HasLecturer(Organization, 'has_lecturer')
Organization.has_member = HasMember(Organization, 'has_member')
Organization.has_part = HasPart(Organization, 'has_part')
Organization.has_post_doc = HasPostDoc(Organization, 'has_post_doc')
Organization.has_professor = HasProfessor(Organization, 'has_professor')
Organization.has_research_assistant = HasResearchAssistant(Organization, 'has_research_assistant')
Organization.has_research_group = HasResearchGroup(Organization, 'has_research_group')
Organization.has_student = HasStudent(Organization, 'has_student')
Organization.has_student_evaluation_committee = HasStudentEvaluationCommittee(Organization, 'has_student_evaluation_committee')
Organization.has_sub_organization = HasSubOrganization(Organization, 'has_sub_organization')
Organization.has_thesis_evaluation_committee = HasThesisEvaluationCommittee(Organization, 'has_thesis_evaluation_committee')
Organization.has_visiting_professor = HasVisitingProfessor(Organization, 'has_visiting_professor')
Organization.is_affiliated_organization_of = IsAffiliatedOrganizationOf(Organization, 'is_affiliated_organization_of')
Organization.is_college_of = IsCollegeOf(Organization, 'is_college_of')
Organization.is_department_of = IsDepartmentOf(Organization, 'is_department_of')
Organization.is_part_of = IsPartOf(Organization, 'is_part_of')
Organization.is_research_group_of = IsResearchGroupOf(Organization, 'is_research_group_of')
Organization.is_sub_organization_of = IsSubOrganizationOf(Organization, 'is_sub_organization_of')
Organization.org_publication = OrgPublication(Organization, 'org_publication')
Person.dislikes = Dislikes(Person, 'dislikes')
Person.evaluated_by = EvaluatedBy(Person, 'evaluated_by')
Person.has_collaboration_with = HasCollaborationWith(Person, 'has_collaboration_with')
Person.has_degree_from = HasDegreeFrom(Person, 'has_degree_from')
Person.has_doctoral_degree_from = HasDoctoralDegreeFrom(Person, 'has_doctoral_degree_from')
Person.has_major = HasMajor(Person, 'has_major')
Person.has_master_degree_from = HasMasterDegreeFrom(Person, 'has_master_degree_from')
Person.has_undergraduate_degree_from = HasUndergraduateDegreeFrom(Person, 'has_undergraduate_degree_from')
Person.is_advised_by = IsAdvisedBy(Person, 'is_advised_by')
Person.is_assistant_professor_of = IsAssistantProfessorOf(Person, 'is_assistant_professor_of')
Person.is_associate_professor_of = IsAssociateProfessorOf(Person, 'is_associate_professor_of')
Person.is_crazy_about = IsCrazyAbout(Person, 'is_crazy_about')
Person.is_dean_of = IsDeanOf(Person, 'is_dean_of')
Person.is_faculty_of = IsFacultyOf(Person, 'is_faculty_of')
Person.is_full_professor_of = IsFullProfessorOf(Person, 'is_full_professor_of')
Person.is_head_of = IsHeadOf(Person, 'is_head_of')
Person.is_lecturer_of = IsLecturerOf(Person, 'is_lecturer_of')
Person.is_member_of = IsMemberOf(Person, 'is_member_of')
Person.is_post_doc_of = IsPostDocOf(Person, 'is_post_doc_of')
Person.is_professor_of = IsProfessorOf(Person, 'is_professor_of')
Person.is_research_assistant_of = IsResearchAssistantOf(Person, 'is_research_assistant_of')
Person.is_student_of = IsStudentOf(Person, 'is_student_of')
Person.is_visiting_professor_of = IsVisitingProfessorOf(Person, 'is_visiting_professor_of')
Person.likes = Likes(Person, 'likes')
Person.loves = Loves(Person, 'loves')
Person.works_for = WorksFor(Person, 'works_for')
Publication.has_author = HasAuthor(Publication, 'has_author')
Publication.publication_research = PublicationResearch(Publication, 'publication_research')
College.has_college_discipline = HasCollegeDiscipline(College, 'has_college_discipline')
College.is_women_college_of = IsWomenCollegeOf(College, 'is_women_college_of')
Department.has_clerical_staff = HasClericalStaff(Department, 'has_clerical_staff')
Department.has_other_staff = HasOtherStaff(Department, 'has_other_staff')
Department.has_pg_program = HasPGProgram(Department, 'has_pg_program')
Department.has_ph_d_program = HasPhDProgram(Department, 'has_ph_d_program')
Department.has_program = HasProgram(Department, 'has_program')
Department.has_supporting_staff = HasSupportingStaff(Department, 'has_supporting_staff')
Department.has_system_staff = HasSystemStaff(Department, 'has_system_staff')
Department.has_ug_program = HasUGProgram(Department, 'has_ug_program')
Department.offer_course = OfferCourse(Department, 'offer_course')
Employee.has_work = HasWork(Employee, 'has_work')
Employee.is_clerical_staff_of = IsClericalStaffOf(Employee, 'is_clerical_staff_of')
Employee.is_other_staff_of = IsOtherStaffOf(Employee, 'is_other_staff_of')
Employee.is_supporting_staff_of = IsSupportingStaffOf(Employee, 'is_supporting_staff_of')
Employee.is_system_staff_of = IsSystemStaffOf(Employee, 'is_system_staff_of')
ResearchGroup.has_research_project = HasResearchProject(ResearchGroup, 'has_research_project')
Student.enroll_for = EnrollFor(Student, 'enroll_for')
Student.enroll_in = EnrollIn(Student, 'enroll_in')
Student.takes_course = TakesCourse(Student, 'takes_course')
University.has_alumnus = HasAlumnus(University, 'has_alumnus')
University.has_women_college = HasWomenCollege(University, 'has_women_college')
Faculty.teaches_course = TeachesCourse(Faculty, 'teaches_course')
TeachingAssistant.is_teaching_assistant_of = IsTeachingAssistantOf(TeachingAssistant, 'is_teaching_assistant_of')
