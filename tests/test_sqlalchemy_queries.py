import os
import sys
from tempfile import NamedTemporaryFile

import SPARQLWrapper
import pytest
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database, create_engine
from rdflib import Graph
from sqlalchemy.orm import sessionmaker

import owl2bench.sqlalchemy_queries  # type: ignore
import owl2bench.sparql_queries  # type: ignore
from owl2bench.loader import WorldLoader
from owl2bench.orm.ormatic_interface import *


def get_world_from_graph_db():
    sys.setrecursionlimit(10000)
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    loader = WorldLoader(sparql)
    loader.parse()
    return loader.world


@pytest.fixture(scope="session")
def sqlalchemy_session():
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()

    world = get_world_from_graph_db()

    dao: WorldDAO = to_dao(world)

    session.add(dao)
    session.commit()
    return session


@pytest.mark.parametrize(
    "sql_query_obj",
    [
        pytest.param(q, id=f"q{q.sparql_query.number}")
        for q in owl2bench.sqlalchemy_queries.all_queries
        if owl2bench.sparql_queries.OWLProfile.RL in q.sparql_query.profile
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
