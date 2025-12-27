from dataclasses import dataclass

from sqlalchemy import select, Select
from .orm.ormatic_interface import *

from . import sparql_queries


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


all_queries = [
    q1,
    q2,
    q3,
    q4,
]
