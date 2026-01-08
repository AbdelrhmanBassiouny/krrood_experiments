import os

import SPARQLWrapper
import pytest
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database, create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from owl2bench.orm.ormatic_interface import *
import owl2bench.sqlalchemy_queries  # type: ignore


@pytest.fixture(scope="session")
def sqlalchemy_session(world_from_graph_db):
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()

    dao: WorldDAO = to_dao(world_from_graph_db)

    session.add(dao)
    session.commit()
    return session


@pytest.mark.parametrize(
    "sql_query_obj",
    [
        pytest.param(q, id=f"q{q.sparql_query.number}")
        for q in owl2bench.sqlalchemy_queries.all_queries
        # if owl2bench.sparql_queries.OWLProfile.RL in q.sparql_query.profile
    ],
)
def test_query(sqlalchemy_session, sql_query_obj):

    # Initialize connection to GraphDB
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    # Execute query
    sparql.setQuery(sql_query_obj.sparql_query.raw_sparql_string)
    sparql_results = sparql.query().convert()
    sparql_result_len = len(sparql_results["results"]["bindings"])

    sqlalchemy_result = sqlalchemy_session.scalars(sql_query_obj.statement).all()
    sqlalchemy_result_len = len(sqlalchemy_result)
    assert sparql_result_len == sqlalchemy_result_len


def test_db_setup(sqlalchemy_session):
    assert sqlalchemy_session.query(WorldDAO).count() == 1
    r = sqlalchemy_session.scalars(
        select(IdentifiedEntityDAO.polymorphic_type).where(
            IdentifiedEntityDAO.identifier == "http://benchmark/OWL2Bench#U0C3D2"
        )
    ).all()
