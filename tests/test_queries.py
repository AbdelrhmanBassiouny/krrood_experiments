import os

from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, aliased

from owl2bench import eql_queries, sparql_queries
from owl2bench.orm.ormatic_interface import *


def test_q1(owl2_dl1):
    # eql_q1 = eql_queries.q1
    # sparql_q1 = sparql_queries.q1

    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)()
    dao = to_dao(owl2_dl1)

    session.add(dao)
    session.commit()
    # Create aliases for the self-join
    p1 = aliased(PersonDAO, name="knower")
    p2 = aliased(PersonDAO, name="known")

    # Construct the query using a join condition derived from the relationship structure
    query = select(p1, p2).join(p2, p1.persondao_knows_id == p2.database_id)
    result = session.scalars(query).all()
    print(len(result))
