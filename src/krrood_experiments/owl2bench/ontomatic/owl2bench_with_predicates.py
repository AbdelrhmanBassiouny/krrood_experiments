"""
Auto-generated Python classes from OWL ontology
Generated using custom converter
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, Field
from functools import lru_cache
from typing_extensions import Tuple, ClassVar

from krrood.class_diagrams.utils import Role
from krrood.entity_query_language.entity import contains, ConditionType, variable_from, length, variable, exists, for_all, to_str
from krrood.entity_query_language.entity_result_processors import count
import krrood.entity_query_language.entity as eql
from krrood.entity_query_language.predicate import HasAttribute, IsSubClassOf, IsSubClassOrRole
from krrood.class_diagrams.utils import Role, issubclass_or_role
from .utils import AnonymousClass, get_super_axiom_and_candidate_var
from .owl2bench_with_predicates_properties import *
from .owl2bench_with_predicates_base import *

# Generated classes
@dataclass(eq=False)
class CollegeDiscipline(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#CollegeDiscipline"


@dataclass(eq=False)
class EvaluationCommittee(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#EvaluationCommittee"
    evaluates: Set[Person] = field(kw_only=True, default_factory=set)
    has_committee_members: Set[Person] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class Interest(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Interest"


@dataclass(eq=False)
class Organization(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Organization"
    has_dean: Set[Person] = field(kw_only=True, default_factory=set)
    has_employee_evaluation_committee: Set[EmployeeEvaluationCommittee] = field(kw_only=True, default_factory=set)
    has_employee: Set[Employee] = field(kw_only=True, default_factory=set)
    has_evaluation_committee: Set[EvaluationCommittee] = field(kw_only=True, default_factory=set)
    has_faculty: Set[Faculty] = field(kw_only=True, default_factory=set)
    has_head: Set[Person] = field(kw_only=True, default_factory=set)
    has_member: Set[Person] = field(kw_only=True, default_factory=set)
    has_part: Set[Organization] = field(kw_only=True, default_factory=set)
    has_student: Set[Student] = field(kw_only=True, default_factory=set)
    has_student_evaluation_committee: Set[StudentEvaluationCommittee] = field(kw_only=True, default_factory=set)
    has_sub_organization: Set[Organization] = field(kw_only=True, default_factory=set)
    has_thesis_evaluation_committee: Set[ThesisEvaluationCommittee] = field(kw_only=True, default_factory=set)
    has_women_college: Set[Organization] = field(kw_only=True, default_factory=set)
    is_affiliated_organization_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_part_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_sub_organization_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_women_college_of: Set[Organization] = field(kw_only=True, default_factory=set)
    org_publication: Set[Publication] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Organization, cls, candidate)
        
        return (HasAttribute(candidate_var, 'works_for'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.works_for.types), Employee))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'works_for') and any(issubclass(t, Employee) for attr in candidate.works_for for t in attr.types)


@dataclass(eq=False)
class Person(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Person"
    dislikes: Set[Interest] = field(kw_only=True, default_factory=set)
    evaluated_by: Set[EvaluationCommittee] = field(kw_only=True, default_factory=set)
    has_advisor: Set[Professor] = field(kw_only=True, default_factory=set)
    has_age: Optional[Any] = field(kw_only=True, default=None)
    has_collaboration_with: Set[Person] = field(kw_only=True, default_factory=set)
    has_degree_from: Set[University] = field(kw_only=True, default_factory=set)
    has_doctoral_degree_from: Set[University] = field(kw_only=True, default_factory=set)
    has_email_address: Optional[Any] = field(kw_only=True, default=None)
    has_first_name: Optional[Any] = field(kw_only=True, default=None)
    has_last_name: Optional[Any] = field(kw_only=True, default=None)
    has_major: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)
    has_master_degree_from: Set[University] = field(kw_only=True, default_factory=set)
    has_telephone: Optional[Any] = field(kw_only=True, default=None)
    has_title: Optional[Any] = field(kw_only=True, default=None)
    has_undergraduate_degree_from: Set[University] = field(kw_only=True, default_factory=set)
    is_advised_by: Set[Professor] = field(kw_only=True, default_factory=set)
    is_crazy_about: Set[Interest] = field(kw_only=True, default_factory=set)
    is_dean_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_head_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_member_of: Set[Organization] = field(kw_only=True, default_factory=set)
    likes: Set[Interest] = field(kw_only=True, default_factory=set)
    loves: Set[Interest] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class Program(OWL2BenchThing):
    """Different programs offered in a department. UG, PG or PhD"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Program"
    has_head: Set[Director] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Program, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), Director))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, Director) for attr in candidate.is_head_of for t in attr.types)


@dataclass(eq=False)
class Publication(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Publication"
    has_author: Set[Person] = field(kw_only=True, default_factory=set)
    publication_research: Set[OWL2BenchThing] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class Thing(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://www.w3.org/2002/07/owl#Thing"


@dataclass(eq=False)
class Work(OWL2BenchThing):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Work"


@dataclass(eq=False)
class Article(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Article"


@dataclass(eq=False)
class Book(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Book"


@dataclass(eq=False)
class College(Organization):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#College"
    has_college_discipline: Set[CollegeDiscipline] = field(kw_only=True, default_factory=set)
    has_department: Set[Department] = field(kw_only=True, default_factory=set)
    has_head: Set[Dean] = field(kw_only=True, default_factory=set)
    is_college_of: Set[University] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(College, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), Dean))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, Dean) for attr in candidate.is_head_of for t in attr.types)


School = College


@dataclass(eq=False)
class Course(Work):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Course"
    is_taught_by: Set[Faculty] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Course, cls, candidate)
        
        return (HasAttribute(candidate_var, 'teaches_course'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.teaches_course.types), Faculty))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'teaches_course') and any(issubclass(t, Faculty) for attr in candidate.teaches_course for t in attr.types)


TeachingCourse = Course


@dataclass(eq=False)
class Department(Organization):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Department"
    has_assistant_professor: Set[AssistantProfessor] = field(kw_only=True, default_factory=set)
    has_associate_professor: Set[AssociateProfessor] = field(kw_only=True, default_factory=set)
    has_clerical_staff: Set[ClericalStaff] = field(kw_only=True, default_factory=set)
    has_full_professor: Set[FullProfessor] = field(kw_only=True, default_factory=set)
    has_head: Set[Chair] = field(kw_only=True, default_factory=set)
    has_lecturer: Set[Lecturer] = field(kw_only=True, default_factory=set)
    has_other_staff: Set[OtherStaff] = field(kw_only=True, default_factory=set)
    has_pg_program: Set[PGProgram] = field(kw_only=True, default_factory=set)
    has_ph_d_program: Set[PhDProgram] = field(kw_only=True, default_factory=set)
    has_post_doc: Set[PostDoc] = field(kw_only=True, default_factory=set)
    has_professor: Set[Professor] = field(kw_only=True, default_factory=set)
    has_program: Set[Program] = field(kw_only=True, default_factory=set)
    has_supporting_staff: Set[SupportingStaff] = field(kw_only=True, default_factory=set)
    has_system_staff: Set[SystemStaff] = field(kw_only=True, default_factory=set)
    has_ug_program: Set[UGProgram] = field(kw_only=True, default_factory=set)
    has_visiting_professor: Set[VisitingProfessor] = field(kw_only=True, default_factory=set)
    is_department_of: Set[College] = field(kw_only=True, default_factory=set)
    offer_course: Set[Course] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Department, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), Chair))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, Chair) for attr in candidate.is_head_of for t in attr.types)


@dataclass(eq=False)
class Employee(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Employee"
    # Role taker
    person: Person
    has_work: Set[Work] = field(kw_only=True, default_factory=set)
    is_clerical_staff_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_head_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_other_staff_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_supporting_staff_of: Set[Organization] = field(kw_only=True, default_factory=set)
    is_system_staff_of: Set[Organization] = field(kw_only=True, default_factory=set)
    works_for: Set[Organization] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Employee, cls, candidate)
        
        return (HasAttribute(candidate_var, 'works_for'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.works_for.types), Organization))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'works_for') and any(issubclass(t, Organization) for attr in candidate.works_for for t in attr.types)


@dataclass(eq=False)
class EmployeeEvaluationCommittee(EvaluationCommittee):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#EmployeeEvaluationCommittee"


@dataclass(eq=False)
class Engineering(CollegeDiscipline):
    """Engineering"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Engineering"


@dataclass(eq=False)
class FineArts(CollegeDiscipline):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#FineArts"


@dataclass(eq=False)
class Game(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Game"


@dataclass(eq=False)
class HumanitiesAndSocial(CollegeDiscipline):
    """HumanitiesAndSocial"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#HumanitiesAndSocial"


@dataclass(eq=False)
class Institute(Organization):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Institute"


@dataclass(eq=False)
class Man(Person):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Man"


@dataclass(eq=False)
class Management(CollegeDiscipline):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Management"


@dataclass(eq=False)
class Manual(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Manual"


@dataclass(eq=False)
class Movie(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Movie"


@dataclass(eq=False)
class Music(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Music"


@dataclass(eq=False)
class PGProgram(Program):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PGProgram"


@dataclass(eq=False)
class Painting(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Painting"


@dataclass(eq=False)
class PeopleWithHobby(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PeopleWithHobby"
    # Role taker
    person: Person

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(PeopleWithHobby, cls, candidate)
        
        return (exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.types), Person)),
				HasAttribute(candidate_var, 'likes'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.likes.types), Interest))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return any(issubclass_or_role(t, Person) for t in candidate.types) and hasattr(candidate, 'likes') and any(issubclass(t, Interest) for attr in candidate.likes for t in attr.types)


@dataclass(eq=False)
class PhDProgram(Program):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PhDProgram"


@dataclass(eq=False)
class Reading(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Reading"


@dataclass(eq=False)
class ResearchGroup(Organization):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ResearchGroup"
    has_research_assistant: Set[ResearchAssistant] = field(kw_only=True, default_factory=set)
    has_research_project: Set[ResearchProject] = field(kw_only=True, default_factory=set)
    is_research_group_of: Set[University] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class ResearchProject(Work):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ResearchProject"


@dataclass(eq=False)
class Science(CollegeDiscipline):
    """Science"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Science"


@dataclass(eq=False)
class Software(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Software"


@dataclass(eq=False)
class Specification(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Specification"


@dataclass(eq=False)
class Sports(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Sports"


@dataclass(eq=False)
class SportsFan(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SportsFan"
    # Role taker
    person: Person
    is_crazy_about: Set[Sports] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(SportsFan, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_crazy_about'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_crazy_about.types), Sports))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_crazy_about') and any(issubclass(t, Sports) for attr in candidate.is_crazy_about for t in attr.types)


@dataclass(eq=False)
class SportsLover(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SportsLover"
    # Role taker
    person: Person
    loves: Set[Sports] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(SportsLover, cls, candidate)
        
        return (HasAttribute(candidate_var, 'loves'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.loves.types), Sports))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'loves') and any(issubclass(t, Sports) for attr in candidate.loves for t in attr.types)


@dataclass(eq=False)
class Student(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Student"
    # Role taker
    person: Person
    enroll_for: Set[Program] = field(kw_only=True, default_factory=set)
    enroll_in: Set[Department] = field(kw_only=True, default_factory=set)
    is_student_of: Set[Organization] = field(kw_only=True, default_factory=set)
    takes_course: Set[Course] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Student, cls, candidate)
        
        return (HasAttribute(candidate_var, 'enroll_in'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.enroll_in.types), Department))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'enroll_in') and any(issubclass(t, Department) for attr in candidate.enroll_in for t in attr.types)


@dataclass(eq=False)
class StudentEvaluationCommittee(EvaluationCommittee):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#StudentEvaluationCommittee"


@dataclass(eq=False)
class T20CricketFan(Role[Person], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#T20CricketFan"
    # Role taker
    person: Person

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "person"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(T20CricketFan, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_crazy_about'),
				exists(candidate_var, to_str(candidate_var.is_crazy_about.uri) == 'http://benchmark/OWL2Bench#T20Cricket')
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_crazy_about') and ('http://benchmark/OWL2Bench#T20Cricket' in map(lambda x: str(x.uri), candidate.is_crazy_about))


@dataclass(eq=False)
class Travelling(Interest):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Travelling"


@dataclass(eq=False)
class UGProgram(Program):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#UGProgram"


@dataclass(eq=False)
class University(Organization):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#University"
    has_alumnus: Set[Person] = field(kw_only=True, default_factory=set)
    has_college: Set[College] = field(kw_only=True, default_factory=set)
    has_research_group: Set[ResearchGroup] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class UnofficialPublication(Publication):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#UnofficialPublication"


@dataclass(eq=False)
class Woman(Person):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Woman"


@dataclass(eq=False)
class AeronauticalEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#AeronauticalEngineering"


@dataclass(eq=False)
class Anthropology(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Anthropology"


@dataclass(eq=False)
class Architecture(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Architecture"


@dataclass(eq=False)
class AsianArts(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#AsianArts"


@dataclass(eq=False)
class Astronomy(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Astronomy"


@dataclass(eq=False)
class Badminton(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Badminton"


@dataclass(eq=False)
class BasketBall(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#BasketBall"


@dataclass(eq=False)
class BasketBallFan(SportsFan):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#BasketBallFan"
    is_crazy_about: Set[BasketBall] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(BasketBallFan, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_crazy_about'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_crazy_about.types), BasketBall))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_crazy_about') and any(issubclass(t, BasketBall) for attr in candidate.is_crazy_about for t in attr.types)


@dataclass(eq=False)
class BasketBallLover(SportsLover):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#BasketBallLover"
    loves: Set[BasketBall] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(BasketBallLover, cls, candidate)
        
        return (HasAttribute(candidate_var, 'loves'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.loves.types), BasketBall))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'loves') and any(issubclass(t, BasketBall) for attr in candidate.loves for t in attr.types)


@dataclass(eq=False)
class Biology(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Biology"


@dataclass(eq=False)
class BiomedicalEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#BiomedicalEngineering"


@dataclass(eq=False)
class ChemicalEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ChemicalEngineering"


@dataclass(eq=False)
class Chemistry(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Chemistry"


@dataclass(eq=False)
class CivilEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#CivilEngineering"


@dataclass(eq=False)
class CoEdCollege(College):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#CoEdCollege"


@dataclass(eq=False)
class ComputerEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ComputerEngineering"


@dataclass(eq=False)
class ComputerScience(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ComputerScience"


@dataclass(eq=False)
class ConferencePaper(Article):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ConferencePaper"


@dataclass(eq=False)
class Cricket(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Cricket"


@dataclass(eq=False)
class DesignManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#DesignManagement"


@dataclass(eq=False)
class Drama(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Drama"


@dataclass(eq=False)
class Economics(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Economics"


@dataclass(eq=False)
class ElectiveCourse(Course):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ElectiveCourse"


@dataclass(eq=False)
class ElectricalEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ElectricalEngineering"


@dataclass(eq=False)
class English(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#English"


@dataclass(eq=False)
class Faculty(Employee):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Faculty"
    is_faculty_of: Set[Organization] = field(kw_only=True, default_factory=set)
    teaches_course: Set[Course] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Faculty, cls, candidate)
        
        return (HasAttribute(candidate_var, 'teaches_course'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.teaches_course.types), Course))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'teaches_course') and any(issubclass(t, Course) for attr in candidate.teaches_course for t in attr.types)


@dataclass(eq=False)
class FinancialAndAccountingManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#FinancialAndAccountingManagement"


@dataclass(eq=False)
class FootBall(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#FootBall"


@dataclass(eq=False)
class Geosciences(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Geosciences"


@dataclass(eq=False)
class History(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#History"


@dataclass(eq=False)
class HumanResourceManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#HumanResourceManagement"


@dataclass(eq=False)
class Humanities(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Humanities"


@dataclass(eq=False)
class IndustryEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#IndustryEngineering"


@dataclass(eq=False)
class JournalArticle(Article):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#JournalArticle"


@dataclass(eq=False)
class LatinArts(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#LatinArts"


@dataclass(eq=False)
class LeisureStudent(Role[Student], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#LeisureStudent"
    # Role taker
    student: Student

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "student"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(LeisureStudent, cls, candidate)
        
        return (exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.types), Student)),
				HasAttribute(candidate_var, 'takes_course'),
				count(IsSubClassOrRole(variable_from(candidate_var.takes_course.types), Course)) <= 1
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return any(issubclass_or_role(t, Student) for t in candidate.types) and hasattr(candidate, 'takes_course') and (len([v for v in candidate.takes_course if any(issubclass(t, Course) for t in v.types) ]) <= 1)


@dataclass(eq=False)
class Linguistics(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Linguistics"


@dataclass(eq=False)
class MarineScience(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MarineScience"


@dataclass(eq=False)
class MarketingManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MarketingManagement"


@dataclass(eq=False)
class MaterialScienceEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MaterialScienceEngineering"


@dataclass(eq=False)
class MaterialsScience(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MaterialsScience"


@dataclass(eq=False)
class Mathematics(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Mathematics"


@dataclass(eq=False)
class MechanicalEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MechanicalEngineering"


@dataclass(eq=False)
class MediaArtsAndSciences(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MediaArtsAndSciences"


@dataclass(eq=False)
class MedievalArts(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MedievalArts"


@dataclass(eq=False)
class ModernArts(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ModernArts"


@dataclass(eq=False)
class ModernLanguages(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ModernLanguages"


@dataclass(eq=False)
class MusicsClass(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#MusicsClass"


@dataclass(eq=False)
class OperationsManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#OperationsManagement"


@dataclass(eq=False)
class PGStudent(Student):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PGStudent"
    enroll_for: Set[PGProgram] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(PGStudent, cls, candidate)
        
        return (HasAttribute(candidate_var, 'enroll_for'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.enroll_for.types), PGProgram))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'enroll_for') and any(issubclass(t, PGProgram) for attr in candidate.enroll_for for t in attr.types)


@dataclass(eq=False)
class PerformingArts(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PerformingArts"


@dataclass(eq=False)
class PetroleumlEngineering(Engineering):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PetroleumlEngineering"


@dataclass(eq=False)
class PhDStudent(Student):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PhDStudent"
    enroll_for: Set[PhDProgram] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(PhDStudent, cls, candidate)
        
        return (HasAttribute(candidate_var, 'enroll_for'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.enroll_for.types), PhDProgram))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'enroll_for') and any(issubclass(t, PhDProgram) for attr in candidate.enroll_for for t in attr.types)


@dataclass(eq=False)
class Philosophy(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Philosophy"


@dataclass(eq=False)
class Physics(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Physics"


@dataclass(eq=False)
class ProjectManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ProjectManagement"


@dataclass(eq=False)
class Psychology(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Psychology"


@dataclass(eq=False)
class PublicRelationsManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PublicRelationsManagement"


@dataclass(eq=False)
class Religions(HumanitiesAndSocial):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Religions"


@dataclass(eq=False)
class ResearchAssistant(Employee):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ResearchAssistant"
    is_research_assistant_of: Set[ResearchGroup] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class RiskManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#RiskManagement"


@dataclass(eq=False)
class SalesManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SalesManagement"


@dataclass(eq=False)
class ScienceStudent(Student):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ScienceStudent"
    has_major: Set[Science] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(ScienceStudent, cls, candidate)
        
        return (HasAttribute(candidate_var, 'has_major'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.has_major.types), Science))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'has_major') and any(issubclass(t, Science) for attr in candidate.has_major for t in attr.types)


@dataclass(eq=False)
class Statistics(Science):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Statistics"


@dataclass(eq=False)
class SupplyChainManagement(Management):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SupplyChainManagement"


@dataclass(eq=False)
class SupportingStaff(Employee):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SupportingStaff"


@dataclass(eq=False)
class Swimming(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Swimming"


@dataclass(eq=False)
class TeachingAssistant(Role[Student], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#TeachingAssistant"
    # Role taker
    student: Student
    is_teaching_assistant_of: Set[Course] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "student"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(TeachingAssistant, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_teaching_assistant_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_teaching_assistant_of.types), Course))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_teaching_assistant_of') and any(issubclass(t, Course) for attr in candidate.is_teaching_assistant_of for t in attr.types)


@dataclass(eq=False)
class TechnicalReport(Article):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#TechnicalReport"


@dataclass(eq=False)
class Tennis(Sports):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Tennis"


@dataclass(eq=False)
class TheatreAndDance(FineArts):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#TheatreAndDance"


@dataclass(eq=False)
class ThesisEvaluationCommittee(StudentEvaluationCommittee):
    """Evaluates PhD students"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ThesisEvaluationCommittee"


@dataclass(eq=False)
class UGCourse(Course):
    """Mandatory courses for all UG students"""
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#UGCourse"


@dataclass(eq=False)
class UGStudent(Student):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#UGStudent"
    enroll_for: Set[UGProgram] = field(kw_only=True, default_factory=set)

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(UGStudent, cls, candidate)
        
        return (HasAttribute(candidate_var, 'enroll_for'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.enroll_for.types), UGProgram))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'enroll_for') and any(issubclass(t, UGProgram) for attr in candidate.enroll_for for t in attr.types)


@dataclass(eq=False)
class WomanCollege(College):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#WomanCollege"

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(WomanCollege, cls, candidate)
        candidate_has_student = variable_from(candidate_var.has_student)
        return (exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.types), College)),
				HasAttribute(candidate_var, 'has_student'),
				for_all(candidate_has_student, exists(candidate_var, IsSubClassOrRole(variable_from(candidate_has_student.types), Woman)))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return any(issubclass_or_role(t, College) for t in candidate.types) and hasattr(candidate, 'has_student') and all(any(issubclass(t, Woman) for t in attr.types) for attr in candidate.has_student)


@dataclass(eq=False)
class ClericalStaff(SupportingStaff):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#ClericalStaff"


@dataclass(eq=False)
class Lecturer(Role[Faculty], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Lecturer"
    # Role taker
    faculty: Faculty
    is_lecturer_of: Set[Department] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "faculty"))


@dataclass(eq=False)
class OtherStaff(SupportingStaff):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#OtherStaff"


@dataclass(eq=False)
class PostDoc(Faculty):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#PostDoc"
    is_post_doc_of: Set[Department] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class Professor(Faculty):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Professor"
    is_professor_of: Set[Department] = field(kw_only=True, default_factory=set)
    tenured: Optional[bool] = field(kw_only=True, default=None)


@dataclass(eq=False)
class SystemStaff(SupportingStaff):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#SystemStaff"


@dataclass(eq=False)
class AssistantProfessor(Professor):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#AssistantProfessor"
    is_assistant_professor_of: Set[Department] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class AssociateProfessor(Professor):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#AssociateProfessor"
    is_associate_professor_of: Set[Department] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class FullProfessor(Professor):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#FullProfessor"
    is_full_professor_of: Set[Department] = field(kw_only=True, default_factory=set)


@dataclass(eq=False)
class VisitingProfessor(Role[Professor], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#VisitingProfessor"
    # Role taker
    professor: Professor
    is_visiting_professor_of: Set[Department] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "professor"))


@dataclass(eq=False)
class Chair(Role[FullProfessor], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Chair"
    # Role taker
    full_professor: FullProfessor
    is_head_of: Set[Department] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "full_professor"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Chair, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), Department))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, Department) for attr in candidate.is_head_of for t in attr.types)


@dataclass(eq=False)
class Dean(Role[FullProfessor], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Dean"
    # Role taker
    full_professor: FullProfessor
    is_head_of: Set[College] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "full_professor"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Dean, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), College))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, College) for attr in candidate.is_head_of for t in attr.types)


@dataclass(eq=False)
class Director(Role[FullProfessor], Symbol):
    cls_uri: ClassVar[str] = "http://benchmark/OWL2Bench#Director"
    # Role taker
    full_professor: FullProfessor
    is_head_of: Set[Program] = field(kw_only=True, default_factory=set)

    @classmethod
    @lru_cache(maxsize=None)
    def role_taker_field(cls) -> Field:
        return next(iter(f for f in fields(cls) if f.name == "full_professor"))

    @classmethod
    def axiom(cls, candidate: AnonymousClass) -> Tuple[ConditionType, ...]:
        super_axiom, candidate_var = get_super_axiom_and_candidate_var(Director, cls, candidate)
        
        return (HasAttribute(candidate_var, 'is_head_of'),
				exists(candidate_var, IsSubClassOrRole(variable_from(candidate_var.is_head_of.types), Program))
        )

    @classmethod
    def axiom_python(cls, candidate: AnonymousClass) -> bool:
        return hasattr(candidate, 'is_head_of') and any(issubclass(t, Program) for attr in candidate.is_head_of for t in attr.types)




# Descriptor assignments
OWL2BenchThing.has_same_home_town_with = HasSameHomeTownWith(OWL2BenchThing, 'has_same_home_town_with')
OWL2BenchThing.is_affiliate_of = IsAffiliateOf(OWL2BenchThing, 'is_affiliate_of')
OWL2BenchThing.knows = Knows(OWL2BenchThing, 'knows')
EvaluationCommittee.evaluates = Evaluates(EvaluationCommittee, 'evaluates')
EvaluationCommittee.has_committee_members = HasCommitteeMembers(EvaluationCommittee, 'has_committee_members')
Organization.has_dean = HasDean(Organization, 'has_dean')
Organization.has_employee_evaluation_committee = HasEmployeeEvaluationCommittee(Organization, 'has_employee_evaluation_committee')
Organization.has_employee = HasEmployee(Organization, 'has_employee')
Organization.has_evaluation_committee = HasEvaluationCommittee(Organization, 'has_evaluation_committee')
Organization.has_faculty = HasFaculty(Organization, 'has_faculty')
Organization.has_head = HasHead(Organization, 'has_head')
Organization.has_member = HasMember(Organization, 'has_member')
Organization.has_part = HasPart(Organization, 'has_part')
Organization.has_student = HasStudent(Organization, 'has_student')
Organization.has_student_evaluation_committee = HasStudentEvaluationCommittee(Organization, 'has_student_evaluation_committee')
Organization.has_sub_organization = HasSubOrganization(Organization, 'has_sub_organization')
Organization.has_thesis_evaluation_committee = HasThesisEvaluationCommittee(Organization, 'has_thesis_evaluation_committee')
Organization.has_women_college = HasWomenCollege(Organization, 'has_women_college')
Organization.is_affiliated_organization_of = IsAffiliatedOrganizationOf(Organization, 'is_affiliated_organization_of')
Organization.is_part_of = IsPartOf(Organization, 'is_part_of')
Organization.is_sub_organization_of = IsSubOrganizationOf(Organization, 'is_sub_organization_of')
Organization.is_women_college_of = IsWomenCollegeOf(Organization, 'is_women_college_of')
Organization.org_publication = OrgPublication(Organization, 'org_publication')
Person.dislikes = Dislikes(Person, 'dislikes')
Person.evaluated_by = EvaluatedBy(Person, 'evaluated_by')
Person.has_advisor = HasAdvisor(Person, 'has_advisor')
Person.has_collaboration_with = HasCollaborationWith(Person, 'has_collaboration_with')
Person.has_degree_from = HasDegreeFrom(Person, 'has_degree_from')
Person.has_doctoral_degree_from = HasDoctoralDegreeFrom(Person, 'has_doctoral_degree_from')
Person.has_major = HasMajor(Person, 'has_major')
Person.has_master_degree_from = HasMasterDegreeFrom(Person, 'has_master_degree_from')
Person.has_undergraduate_degree_from = HasUndergraduateDegreeFrom(Person, 'has_undergraduate_degree_from')
Person.is_advised_by = IsAdvisedBy(Person, 'is_advised_by')
Person.is_crazy_about = IsCrazyAbout(Person, 'is_crazy_about')
Person.is_dean_of = IsDeanOf(Person, 'is_dean_of')
Person.is_head_of = IsHeadOf(Person, 'is_head_of')
Person.is_member_of = IsMemberOf(Person, 'is_member_of')
Person.likes = Likes(Person, 'likes')
Person.loves = Loves(Person, 'loves')
Program.has_head = HasHead(Program, 'has_head')
Publication.has_author = HasAuthor(Publication, 'has_author')
Publication.publication_research = PublicationResearch(Publication, 'publication_research')
College.has_college_discipline = HasCollegeDiscipline(College, 'has_college_discipline')
College.has_department = HasDepartment(College, 'has_department')
College.has_head = HasHead(College, 'has_head')
College.is_college_of = IsCollegeOf(College, 'is_college_of')
Course.is_taught_by = IsTaughtBy(Course, 'is_taught_by')
Department.has_assistant_professor = HasAssistantProfessor(Department, 'has_assistant_professor')
Department.has_associate_professor = HasAssociateProfessor(Department, 'has_associate_professor')
Department.has_clerical_staff = HasClericalStaff(Department, 'has_clerical_staff')
Department.has_full_professor = HasFullProfessor(Department, 'has_full_professor')
Department.has_head = HasHead(Department, 'has_head')
Department.has_lecturer = HasLecturer(Department, 'has_lecturer')
Department.has_other_staff = HasOtherStaff(Department, 'has_other_staff')
Department.has_pg_program = HasPGProgram(Department, 'has_pg_program')
Department.has_ph_d_program = HasPhDProgram(Department, 'has_ph_d_program')
Department.has_post_doc = HasPostDoc(Department, 'has_post_doc')
Department.has_professor = HasProfessor(Department, 'has_professor')
Department.has_program = HasProgram(Department, 'has_program')
Department.has_supporting_staff = HasSupportingStaff(Department, 'has_supporting_staff')
Department.has_system_staff = HasSystemStaff(Department, 'has_system_staff')
Department.has_ug_program = HasUGProgram(Department, 'has_ug_program')
Department.has_visiting_professor = HasVisitingProfessor(Department, 'has_visiting_professor')
Department.is_department_of = IsDepartmentOf(Department, 'is_department_of')
Department.offer_course = OfferCourse(Department, 'offer_course')
Employee.has_work = HasWork(Employee, 'has_work')
Employee.is_clerical_staff_of = IsClericalStaffOf(Employee, 'is_clerical_staff_of')
Employee.is_head_of = IsHeadOf(Employee, 'is_head_of')
Employee.is_other_staff_of = IsOtherStaffOf(Employee, 'is_other_staff_of')
Employee.is_supporting_staff_of = IsSupportingStaffOf(Employee, 'is_supporting_staff_of')
Employee.is_system_staff_of = IsSystemStaffOf(Employee, 'is_system_staff_of')
Employee.works_for = WorksFor(Employee, 'works_for')
ResearchGroup.has_research_assistant = HasResearchAssistant(ResearchGroup, 'has_research_assistant')
ResearchGroup.has_research_project = HasResearchProject(ResearchGroup, 'has_research_project')
ResearchGroup.is_research_group_of = IsResearchGroupOf(ResearchGroup, 'is_research_group_of')
SportsFan.is_crazy_about = IsCrazyAbout(SportsFan, 'is_crazy_about')
SportsLover.loves = Loves(SportsLover, 'loves')
Student.enroll_for = EnrollFor(Student, 'enroll_for')
Student.enroll_in = EnrollIn(Student, 'enroll_in')
Student.is_student_of = IsStudentOf(Student, 'is_student_of')
Student.takes_course = TakesCourse(Student, 'takes_course')
University.has_alumnus = HasAlumnus(University, 'has_alumnus')
University.has_college = HasCollege(University, 'has_college')
University.has_research_group = HasResearchGroup(University, 'has_research_group')
BasketBallFan.is_crazy_about = IsCrazyAbout(BasketBallFan, 'is_crazy_about')
BasketBallLover.loves = Loves(BasketBallLover, 'loves')
Faculty.is_faculty_of = IsFacultyOf(Faculty, 'is_faculty_of')
Faculty.teaches_course = TeachesCourse(Faculty, 'teaches_course')
PGStudent.enroll_for = EnrollFor(PGStudent, 'enroll_for')
PhDStudent.enroll_for = EnrollFor(PhDStudent, 'enroll_for')
ResearchAssistant.is_research_assistant_of = IsResearchAssistantOf(ResearchAssistant, 'is_research_assistant_of')
ScienceStudent.has_major = HasMajor(ScienceStudent, 'has_major')
TeachingAssistant.is_teaching_assistant_of = IsTeachingAssistantOf(TeachingAssistant, 'is_teaching_assistant_of')
UGStudent.enroll_for = EnrollFor(UGStudent, 'enroll_for')
Lecturer.is_lecturer_of = IsLecturerOf(Lecturer, 'is_lecturer_of')
PostDoc.is_post_doc_of = IsPostDocOf(PostDoc, 'is_post_doc_of')
Professor.is_professor_of = IsProfessorOf(Professor, 'is_professor_of')
AssistantProfessor.is_assistant_professor_of = IsAssistantProfessorOf(AssistantProfessor, 'is_assistant_professor_of')
AssociateProfessor.is_associate_professor_of = IsAssociateProfessorOf(AssociateProfessor, 'is_associate_professor_of')
FullProfessor.is_full_professor_of = IsFullProfessorOf(FullProfessor, 'is_full_professor_of')
VisitingProfessor.is_visiting_professor_of = IsVisitingProfessorOf(VisitingProfessor, 'is_visiting_professor_of')
Chair.is_head_of = IsHeadOf(Chair, 'is_head_of')
Dean.is_head_of = IsHeadOf(Dean, 'is_head_of')
Director.is_head_of = IsHeadOf(Director, 'is_head_of')
