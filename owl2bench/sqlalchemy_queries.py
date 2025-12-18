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

    query: Select
    """
    The sqlalchemy query to be executed.
    """


sqlalchemy_q1 = select(persondao_knows_association)
q1 = SQLAlchemyQuery(sparql_queries.q1, sqlalchemy_q1)

sqlalchemy_q2 = select(researchgroupdao_members_association)
q2 = SQLAlchemyQuery(sparql_queries.q2, sqlalchemy_q2)
