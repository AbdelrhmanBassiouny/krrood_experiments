# KRROOD SQLAlchemy setup
import os

import tqdm
from krrood.entity_query_language.symbol_graph import SymbolGraph
from krrood.ormatic.dao import to_dao, ToDataAccessObjectState
from krrood.ormatic.utils import drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import krrood_experiments
from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.orm.ormatic_interface import (
    Base,
    ChairDAO,
    WomanDAO,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates import (
    Chair,
    Woman,
    SportsLover,
    Game,
)
from krrood_experiments.owl2bench.sparql_queries import OWLProfile
from krrood_experiments.owl2bench.ontomatic.sqlalchemy_queries import all_queries

engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])

drop_database(engine)
Base.metadata.create_all(engine)
session = sessionmaker(engine)()
resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
unreasoned_owl2bench_file_path = os.path.join(
    resources_dir, "owl2bench_statements_unreasoned.rdf"
)
registry = load_instances_for_owl2bench_with_predicates(unreasoned_owl2bench_file_path)
state = ToDataAccessObjectState()
pbar = tqdm.tqdm([v for uri_vs in registry._by_uri.values() for v in uri_vs])
for instance in pbar:
    # if isinstance(instance, SportsLover) and any(
    #     isinstance(l, Game) for l in instance.loves
    # ):
    #     import pdbpp
    #
    #     pdbpp.set_trace()
    dao = to_dao(instance, state)
    session.add(dao)
# for wrapped_instance in SymbolGraph().wrapped_instances:
#     dao = to_dao(wrapped_instance.instance)
#     session.add(dao)
# dao: WorldDAO = to_dao(loader.world)
# session.add(dao)

print("Committing initial data...")
session.commit()
session.expunge_all()
print("Done commiting.")


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
