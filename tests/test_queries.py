import os

from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database, create_engine

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, aliased
from owl2bench import eql_queries, sparql_queries
from owl2bench.orm.ormatic_interface import *


def test_q1(owl2_dl1):

    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)()
    dao = to_dao(owl2_dl1)

    session.add(dao)
    session.commit()

    stmt = select(persondao_knows_association)

    result = session.scalars(stmt)
    assert len(list(result)) > 0
