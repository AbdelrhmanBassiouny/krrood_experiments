import os
import time
import SPARQLWrapper
import rdflib
import owlready2
import tqdm
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from owlrl import DeductiveClosure, OWLRL_Semantics
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, class_mapper

from krrood_experiments.owl2bench.ood.loader import WorldLoader
from krrood_experiments.owl2bench.ood.orm.ormatic_interface import Base, WorldDAO
from krrood_experiments.owl2bench.ood.performance_utils import (
    Backend,
    LoadingTiming,
    LatexPerformanceExporter,
)
from sqlalchemy.orm import selectinload

dir_path = os.path.dirname(os.path.realpath(__file__))
rdf_file_path = os.path.join(dir_path, "..", "resources", "statements.rdf")
rdf_unreasoned_file_path = os.path.join(
    dir_path, "..", "resources", "statements_unreasoned.rdf"
)


def load_everything_recursively(model):
    """
    Crawls all relationships starting from 'model' until the entire
    connected graph is covered by selectinload options.
    """
    options = []
    # Visited tracks (parent_model, relationship_key) to avoid redundant paths
    visited_paths = set()

    def _build_options(current_model, path=None):
        mapper = class_mapper(current_model)

        for rel in mapper.relationships:
            # Unique identifier for this specific link in the chain
            rel_identity = (current_model, rel.key)

            if rel_identity in visited_paths:
                continue

            visited_paths.add(rel_identity)

            # Chain the loader
            loader = selectinload(rel) if path is None else path.selectinload(rel)
            options.append(loader)

            # Recurse into the related class
            _build_options(rel.mapper.class_, loader)

    _build_options(model)
    return options


def prepare_raw_krrood():
    sparql = SPARQLWrapper.SPARQLWrapper(
        "http://localhost:7200/repositories/KRROOD_UNREASONED"
    )
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    loader = WorldLoader(sparql)
    loader.parse()
    dao = to_dao(loader.world)
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()
    session.add(dao)
    session.commit()
    session.expunge_all()


def prepare_reasoned_krrood():
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    loader = WorldLoader(sparql)
    loader.parse()
    dao = to_dao(loader.world)
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()
    session.add(dao)
    session.commit()
    session.expunge_all()


def load_sql() -> float:
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    session = sessionmaker(engine)()
    stmt = select(WorldDAO).options(*load_everything_recursively(WorldDAO))
    start = time.time()
    r = session.scalars(stmt).one()
    sqlalchemy_loading_time = time.time() - start
    return sqlalchemy_loading_time


def load_krrood() -> float:
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    session = sessionmaker(engine)()

    start = time.time()
    world_dao = session.scalars(select(WorldDAO)).one()
    world = world_dao.from_dao()
    krrood_loading_time = time.time() - start
    return krrood_loading_time


def load_raw_owlready2() -> float:

    start = time.time()
    owlready2_world = owlready2.World()
    owlready2_world.get_ontology(rdf_unreasoned_file_path).load()
    owlready2_loading_time = time.time() - start
    owlready2_world.close()
    return owlready2_loading_time


def reason_raw_owlready2() -> float:

    owlready2_world = owlready2.World()
    owlready2_world.get_ontology(rdf_unreasoned_file_path).load()
    start = time.time()
    owlready2.sync_reasoner_pellet(owlready2_world, infer_property_values=True)
    owlready2_loading_time = time.time() - start
    owlready2_world.close()
    return owlready2_loading_time


def loading_reasoned_owlready2() -> float:

    start = time.time()
    owlready2_world = owlready2.World()
    owlready2_world.get_ontology(rdf_file_path).load()
    owlready2_loading_time = time.time() - start
    owlready2_world.close()

    return owlready2_loading_time


def reason_reasoned_owlready2() -> float:

    owlready2_world = owlready2.World()
    owlready2_world.get_ontology(rdf_file_path).load()
    start = time.time()
    owlready2.sync_reasoner_pellet(owlready2_world, infer_property_values=True)
    owlready2_loading_time = time.time() - start
    owlready2_world.close()
    return owlready2_loading_time


def load_raw_rdflib() -> float:
    start = time.time()
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(rdf_unreasoned_file_path, format="xml")
    rdflib_loading_time = time.time() - start
    return rdflib_loading_time


def reason_raw_rdflib() -> float:
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(rdf_unreasoned_file_path, format="xml")
    start = time.time()
    DeductiveClosure(OWLRL_Semantics).expand(rdflib_graph)
    rdflib_loading_time = time.time() - start
    return rdflib_loading_time


def load_reasoned_rdflib() -> float:
    start = time.time()
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(rdf_file_path, format="xml")
    rdflib_loading_time = time.time() - start
    return rdflib_loading_time


def reason_reasoned_rdflib() -> float:
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(rdf_file_path, format="xml")
    start = time.time()
    DeductiveClosure(OWLRL_Semantics).expand(rdflib_graph)
    rdflib_loading_time = time.time() - start
    return rdflib_loading_time


def evaluate_loading(iterations: int = 1):

    raw_runtimes = {backend: [] for backend in Backend}
    reasoned_runtimes = {backend: [] for backend in Backend}

    prepare_raw_krrood()

    for _ in tqdm.trange(iterations, desc="Evaluating loading raw data"):
        raw_runtimes[Backend.Owlready2].append(load_raw_owlready2())
        raw_runtimes[Backend.RDFLib].append(load_raw_rdflib())
        raw_runtimes[Backend.SQLAlchemy].append(load_sql())
        raw_runtimes[Backend.EQL].append(load_krrood())

    prepare_reasoned_krrood()

    for _ in tqdm.trange(iterations, desc="Evaluating loading reasoned data"):
        reasoned_runtimes[Backend.Owlready2].append(loading_reasoned_owlready2())
        reasoned_runtimes[Backend.RDFLib].append(load_reasoned_rdflib())
        reasoned_runtimes[Backend.SQLAlchemy].append(load_sql())
        reasoned_runtimes[Backend.EQL].append(load_krrood())

    loading_timing = LoadingTiming(
        raw_runtimes=raw_runtimes, reasoned_runtimes=reasoned_runtimes
    )

    exporter = LatexPerformanceExporter(loading_timing=loading_timing)
    exporter.export_loading_performance()


if __name__ == "__main__":
    evaluate_loading()
