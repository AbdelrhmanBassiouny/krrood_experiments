# KRROOD SQLAlchemy setup
import os

import tqdm
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import krrood_experiments
from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.orm.ormatic_interface import Base
from krrood_experiments.owl2bench.sparql_queries import OWLProfile
from krrood_experiments.owl2bench.ontomatic.sqlalchemy_queries import all_queries

# engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
engine = create_engine(
    "postgresql+psycopg2://krrood_experiments:krrood_experiments@localhost:5432/krrood_experiments"
)
drop_database(engine)
Base.metadata.create_all(engine)
session = sessionmaker(engine)()
resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
unreasoned_owl2bench_file_path = os.path.join(
    resources_dir, "owl2bench_statements_unreasoned.rdf"
)
registry = load_instances_for_owl2bench_with_predicates(unreasoned_owl2bench_file_path)
for instance in registry._by_uri.values():
    dao = to_dao(instance)
    session.add(dao)
# dao: WorldDAO = to_dao(loader.world)
# session.add(dao)
session.commit()
session.expunge_all()


sparql_queries = [
    q
    for q in krrood_experiments.owl2bench.sparql_queries.all_queries
    if OWLProfile.RL in q.profile
]

pbar = tqdm.tqdm(all_queries)
for sqlalchemy_query in pbar:
    pbar.set_description(f"Evaluating query {sqlalchemy_query.sparql_query.number}")

    sql_results = list(session.execute(sqlalchemy_query.statement).all())
    print(f"SQLAlchemy results: {len(sql_results)}")
