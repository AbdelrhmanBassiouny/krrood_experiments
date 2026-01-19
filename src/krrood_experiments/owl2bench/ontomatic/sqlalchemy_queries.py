from dataclasses import dataclass

from sqlalchemy import select, Select
from sqlalchemy.orm import aliased

from krrood_experiments.owl2bench.ontomatic.orm.ormatic_interface import *

from krrood_experiments.owl2bench import sparql_queries
from sqlalchemy import func

from krrood_experiments.owl2bench.ood.orm.ormatic_interface import (
    persondao_knows_association,
)


@dataclass
class SQLAlchemyQuery:

    sparql_query: sparql_queries.SPARQLQuery
    """
    The sparql query this represents.
    """

    statement: Select
    """
    The sqlalchemy query to be executed.
    """


sqlalchemy_q2 = select(organizationdao_has_member_association)
q2 = SQLAlchemyQuery(sparql_queries.q2, sqlalchemy_q2)

sqlalchemy_q3 = select(organizationdao_is_part_of_association)
q3 = SQLAlchemyQuery(sparql_queries.q3, sqlalchemy_q3)

sqlalchemy_q4 = select(PersonDAO.has_age).where(
    PersonDAO.has_age.is_not(None), PersonDAO.has_age != ""
)
q4 = SQLAlchemyQuery(sparql_queries.q4, sqlalchemy_q4)

CricketAlias = aliased(CricketDAO, flat=True)

sqlalchemy_q5 = select(T20CricketFanDAO)
q5 = SQLAlchemyQuery(sparql_queries.q5, sqlalchemy_q5)

sqlalchemy_q6 = select(persondao_knows_association).where(
    persondao_knows_association.c.source_persondao_id
    == persondao_knows_association.c.target_persondao_id
)
q6 = SQLAlchemyQuery(sparql_queries.q6, sqlalchemy_q6)

sqlalchemy_q7 = select(universitydao_has_alumnus_association)
q7 = SQLAlchemyQuery(sparql_queries.q7, sqlalchemy_q7)

sqlalchemy_q8 = select(organizationdao_is_affiliated_organization_of_association)
q8 = SQLAlchemyQuery(sparql_queries.q8, sqlalchemy_q8)

sqlalchemy_q9 = select(collegedao_has_college_discipline_association).join(
    MaterialScienceEngineeringDAO
)
q9 = SQLAlchemyQuery(sparql_queries.q9, sqlalchemy_q9)

sqlalchemy_q10 = select(persondao_has_collaboration_with_association)
q10 = SQLAlchemyQuery(sparql_queries.q10, sqlalchemy_q10)

sqlalchemy_q11 = select(persondao_is_advised_by_association)
q11 = SQLAlchemyQuery(sparql_queries.q11, sqlalchemy_q11)

sqlalchemy_q12 = select(PersonDAO)
q12 = SQLAlchemyQuery(sparql_queries.q12, sqlalchemy_q12)

sqlalchemy_q13 = select(WomanCollegeDAO)
q13 = SQLAlchemyQuery(sparql_queries.q13, sqlalchemy_q13)


sqlalchemy_q14 = select(LeisureStudentDAO)
q14 = SQLAlchemyQuery(sparql_queries.q14, sqlalchemy_q14)


sqlalchemy_q15 = select(persondao_is_head_of_association)
q15 = SQLAlchemyQuery(sparql_queries.q15, sqlalchemy_q15)

sqlalchemy_q16 = select(organizationdao_has_head_association)
q16 = SQLAlchemyQuery(sparql_queries.q16, sqlalchemy_q16)

sqlalchemy_q17 = select(UGStudentDAO)
q17 = SQLAlchemyQuery(sparql_queries.q17, sqlalchemy_q17)

sqlalchemy_q19 = select(FacultyDAO)
q19 = SQLAlchemyQuery(sparql_queries.q19, sqlalchemy_q19)

sqlalchemy_q20 = select(owl2benchthingdao_has_same_home_town_with_association)
q20 = SQLAlchemyQuery(sparql_queries.q20, sqlalchemy_q20)


sqlalchemy_q21 = (
    select(StudentDAO, OrganizationDAO)
    .join(OrganizationDAO, StudentDAO.is_student_of)
    .join(CollegeDAO, OrganizationDAO.is_part_of)
    .join(EngineeringDAO, CollegeDAO.has_college_discipline)
    .distinct()
)
q21 = SQLAlchemyQuery(sparql_queries.q21, sqlalchemy_q21)


student = aliased(StudentDAO)
course = aliased(CourseDAO)
faculty = aliased(FacultyDAO)
person = aliased(PersonDAO)
organization = aliased(OrganizationDAO)

sqlalchemy_q22 = (
    select(student, course)
    .distinct()
    .select_from(student)
    .join(course, student.takes_course)
    .join(faculty, course.is_taught_by)
    .join(person, faculty.person)
    .join(
        organizationdao_has_dean_association,
        person.database_id
        == organizationdao_has_dean_association.c.target_persondao_id,
    )
    .join(
        organization,
        organization.database_id
        == organizationdao_has_dean_association.c.source_organizationdao_id,
    )
    .where(
        student.polymorphic_type.in_(["PGStudentDAO", "PhDStudentDAO", "UGStudentDAO"])
    )
)
q22 = SQLAlchemyQuery(sparql_queries.q22, sqlalchemy_q22)

all_queries = [
    # q1,
    q2,
    q3,
    q4,
    q5,
    # q6,
    q7,
    q8,
    # q9,
    q10,
    q11,
    q12,
    # q13,
    # q14,
    q15,
    q16,
    # q17,
    # q18,
    q19,
    q20,
    q21,
    q22,
]
