import os
import time
import SPARQLWrapper
import rdflib
import owlready2
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from owl2bench.orm.ormatic_interface import Base, WorldDAO
from owl2bench.loader import WorldLoader
from owl2bench.performance_utils import Backend, LoadingTiming, LatexPerformanceExporter


def evaluate_loading():
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    rdf_file_path = os.path.join(dir_path, "..", "resources", "statements.rdf")

    print("Loading data into owlready2...")
    owlready2_world = owlready2.World()
    start = time.time()
    owlready2_world.get_ontology(rdf_file_path).load()
    owlready2_loading_time = time.time() - start

    print("Loading data into rdflib...")
    rdflib_graph = rdflib.Graph()
    start = time.time()
    rdflib_graph.parse(rdf_file_path, format="xml")
    rdflib_loading_time = time.time() - start

    print("Loading data into KRROOD from GraphDB...")
    start = time.time()
    loader = WorldLoader(sparql)
    loader.parse()
    krrood_graphdb_loading_time = time.time() - start

    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker(engine)()

    dao: WorldDAO = to_dao(loader.world)

    session.add(dao)
    session.commit()
    session.expunge_all()

    print("Loading data into KRROOD from SQLAlchemy...")

    start = time.time()
    world_dao: WorldDAO = session.scalars(select(WorldDAO)).one()
    # _ = world_dao.from_dao()
    krrood_sqlalchemy_loading_time = time.time() - start

    loading_timing = LoadingTiming(
        backend_runtimes={
            Backend.Owlready2: owlready2_loading_time,
            Backend.RDFLib: rdflib_loading_time,
            Backend.EQL: krrood_graphdb_loading_time,
            Backend.SQLAlchemy: krrood_sqlalchemy_loading_time,
        }
    )

    exporter = LatexPerformanceExporter(loading_timing=loading_timing)
    exporter.export_loading_performance()


if __name__ == "__main__":
    evaluate_loading()
