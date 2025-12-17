import os

from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database, create_engine

from sqlalchemy import select
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

    p1 = aliased(PersonDAO)
    p2 = aliased(PersonDAO)

    stmt = select(p1, p2).select_from(
        persondao_knows_association.join(
            p1, p1.database_id == persondao_knows_association.c.source_persondao_id
        ).join(p2, p2.database_id == persondao_knows_association.c.target_persondao_id)
    )

    print(session.execute(stmt).fetchall())
