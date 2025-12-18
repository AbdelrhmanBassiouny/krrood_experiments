import os

import pytest
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database, create_engine

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, aliased
from owl2bench import eql_queries, sparql_queries
from owl2bench.orm.ormatic_interface import *
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph
from tempfile import NamedTemporaryFile
from owl2bench.loader import WorldLoader
import owl2bench.sqlalchemy_queries


def get_world_from_graph_db():

    ENDPOINT = "http://localhost:7200/repositories/KRROOD"

    # 1) Pull all triples; enable reasoning if you want inferred triples too
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(
        """
        CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }
    """
    )
    sparql.setReturnFormat(TURTLE)
    # GraphDB-specific optional flags
    sparql.addParameter("infer", "true")  # include inferred statements (if desired)
    sparql.addParameter("sameAs", "false")  # control sameAs expansion

    raw_ttl = sparql.query().convert()  # returns bytes in TURTLE

    # 2) Parse into an RDFLib graph (optional step, useful for validation)
    g = Graph()
    g.parse(data=raw_ttl.decode("utf-8"), format="turtle")

    # 3) Serialize to a temp file and let WorldLoader read it
    with NamedTemporaryFile(suffix=".ttl", delete=False) as tmp:
        g.serialize(destination=tmp.name, format="turtle")
        world = WorldLoader().load(tmp.name)
    return world


@pytest.fixture(scope="session")
def sqlalchemy_session():
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()

    world = get_world_from_graph_db()

    dao = to_dao(world)
    session.add(dao)
    session.commit()
    return session


def test_q1(sqlalchemy_session):

    q = owl2bench.sqlalchemy_queries.q1
    sqlalchemy_session.scalars(q.query).all()

    assert len(result) > 0


def test_q2(sqlalchemy_session):
    stmt = select(researchgroupdao_members_association)
