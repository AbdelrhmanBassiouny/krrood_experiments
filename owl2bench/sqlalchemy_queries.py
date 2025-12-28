from dataclasses import dataclass

from sqlalchemy import select, Select
from .orm.ormatic_interface import *

from . import sparql_queries
from sqlalchemy import func


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


sqlalchemy_q1 = select(persondao_knows_association)
q1 = SQLAlchemyQuery(sparql_queries.q1, sqlalchemy_q1)


sqlalchemy_q2 = select(organizationdao_members_association)
q2 = SQLAlchemyQuery(sparql_queries.q2, sqlalchemy_q2)
sqlalchemy_q3 = select(organizationdao_is_part_of_association)
q3 = SQLAlchemyQuery(sparql_queries.q3, sqlalchemy_q3)

sqlalchemy_q4 = select(PersonDAO.age).where(
    PersonDAO.age.is_not(None), PersonDAO.age != ""
)
q4 = SQLAlchemyQuery(sparql_queries.q4, sqlalchemy_q4)

sqlalchemy_q6 = select(persondao_knows_association).where(
    persondao_knows_association.c.source_persondao_id
    == persondao_knows_association.c.target_persondao_id
)
q6 = SQLAlchemyQuery(sparql_queries.q6, sqlalchemy_q6)

sqlalchemy_q7 = select(universitydao_alumni_association)
q7 = SQLAlchemyQuery(sparql_queries.q7, sqlalchemy_q7)

sqlalchemy_q8 = select(organizationdao_affiliated_organizations_association)
q8 = SQLAlchemyQuery(sparql_queries.q8, sqlalchemy_q8)

sqlalchemy_q9 = select(collegedao_disciplines_association).join(
    MaterialScienceEngineeringDAO
)
q9 = SQLAlchemyQuery(sparql_queries.q9, sqlalchemy_q9)

sqlalchemy_q10 = select(persondao_collaborates_with_association)
q10 = SQLAlchemyQuery(sparql_queries.q10, sqlalchemy_q10)

sqlalchemy_q11 = select(persondao_is_advised_by_association)
q11 = SQLAlchemyQuery(sparql_queries.q11, sqlalchemy_q11)

sqlalchemy_q12 = select(PersonDAO)
q12 = SQLAlchemyQuery(sparql_queries.q12, sqlalchemy_q12)

sqlalchemy_q13 = select(CollegeDAO).filter(
    ~CollegeDAO.members.any(PersonDAO.gender != "female")
)
q13 = SQLAlchemyQuery(sparql_queries.q13, sqlalchemy_q13)


sqlalchemy_q14 = (
    select(PersonDAO)
    .join(PersonDAO.takes_course)
    .group_by(PersonDAO)
    .having(func.count(CourseDAO.database_id) == 1)
)
q14 = SQLAlchemyQuery(sparql_queries.q14, sqlalchemy_q14)


sqlalchemy_q15 = select(OrganizationDAO.head_id).where(OrganizationDAO.head_id != None)
q15 = SQLAlchemyQuery(sparql_queries.q15, sqlalchemy_q15)

sqlalchemy_q16 = select(OrganizationDAO).where(OrganizationDAO.head_id != None)
q16 = SQLAlchemyQuery(sparql_queries.q16, sqlalchemy_q16)

sqlalchemy_q17 = (
    select(PersonDAO)
    .join(PersonDAO.enrolled_in.of_type(UndergraduateProgramDAO))
    .group_by(PersonDAO)
    .having(func.count(UndergraduateProgramDAO.database_id) == 1)
)
q17 = SQLAlchemyQuery(sparql_queries.q17, sqlalchemy_q17)

sqlalchemy_q18 = (
    select(PersonDAO)
    .join(PersonDAO.hobbies)
    .group_by(PersonDAO)
    .having(func.count(InterestDAO.database_id) >= 3)
)
q18 = SQLAlchemyQuery(sparql_queries.q18, sqlalchemy_q18)

all_queries = [
    q1,
    q2,
    q3,
    q4,
    q6,
    q7,
    q8,
    q9,
    q10,
    q11,
    q12,
    q13,
    #  q14,
    q15,
    q16,
    q17,
    # q18,
]
