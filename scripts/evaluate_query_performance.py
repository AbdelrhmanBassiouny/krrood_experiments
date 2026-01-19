import os
import time
from typing import List
import SPARQLWrapper
import rdflib
import owlready2
import tqdm
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy.orm import sessionmaker

from krrood_experiments.owl2bench.ood.orm.ormatic_interface import Base, WorldDAO
from krrood_experiments.owl2bench.ood.loader import WorldLoader
from krrood_experiments.owl2bench.sparql_queries import OWLProfile
import krrood_experiments.owl2bench.sparql_queries
import krrood_experiments.owl2bench.ood.eql_queries
import krrood_experiments.owl2bench.ood.sqlalchemy_queries
from krrood_experiments.owl2bench.ood.performance_utils import (
    Backend,
    QueryTiming,
    LatexPerformanceExporter,
)


def evaluate_queries(iterations_per_query: int = 10):
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    rdf_file_path = os.path.join(
        dir_path, "..", "resources", "owl2bench_statements_reasoned.rdf"
    )

    print("Setting up backends for query evaluation...")

    # RDFLib setup
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(
        rdf_file_path,
        format="xml",
    )

    # KRROOD EQL setup
    loader = WorldLoader(sparql)
    loader.parse()

    # KRROOD SQLAlchemy setup
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)()
    dao: WorldDAO = to_dao(loader.world)
    session.add(dao)
    session.commit()
    session.expunge_all()

    query_timings: List[QueryTiming] = []

    sparql_queries = [
        q
        for q in krrood_experiments.owl2bench.sparql_queries.all_queries
        if OWLProfile.RL in q.profile
    ]

    pbar = tqdm.tqdm(sparql_queries)
    for sparql_query in pbar:
        pbar.set_description(f"Evaluating query {sparql_query.number}")

        # Find the corresponding sqlalchemy query
        sqlalchemy_query = [
            q
            for q in krrood_experiments.owl2bench.ood.sqlalchemy_queries.all_queries
            if q.sparql_query == sparql_query
        ][0]

        # Find the corresponding eql query
        eql_query = [
            q
            for q in krrood_experiments.owl2bench.ood.eql_queries.all_queries
            if q.sparql_query == sparql_query
        ][0]

        current_sqlalchemy_runtimes = []
        current_sparqlwrapper_runtimes = []
        current_eql_runtimes = []
        current_rdflib_runtimes = []
        current_owlready2_runtimes = []

        for _ in range(iterations_per_query):

            # reset sqlalchemy loadings
            session.expunge_all()

            # Owlready2 setup to reset the cache everytime
            owlready2_world = owlready2.World()
            owlready2_world.get_ontology(rdf_file_path).load()

            # Execute SQLAlchemy query
            start = time.time()
            sql_results = list(session.execute(sqlalchemy_query.statement).all())
            current_sqlalchemy_runtimes.append((time.time() - start) * 1000)

            # Execute SPARQL query
            sparql.setQuery(sparql_query.raw_sparql_string)
            start = time.time()
            sparql_results = list(sparql.query().convert()["results"]["bindings"])
            current_sparqlwrapper_runtimes.append((time.time() - start) * 1000)

            # Execute EQL query
            start = time.time()
            eql_results = list(eql_query.query(loader.world).evaluate())
            current_eql_runtimes.append((time.time() - start) * 1000)

            # Execute RDFLib query
            start = time.time()
            rdflib_results = list(rdflib_graph.query(sparql_query.raw_sparql_string))
            current_rdflib_runtimes.append((time.time() - start) * 1000)

            # Execute Owlready2 query
            start = time.time()
            owlready2_results = list(
                owlready2_world.sparql(
                    sparql_query.raw_sparql_string, error_on_undefined_entities=False
                )
            )
            current_owlready2_runtimes.append((time.time() - start) * 1000)
            print(f"Owlready2 results: {len(owlready2_results)}")
            print(f"Sparql results: {len(sparql_results)}")
            print(f"EQL results: {len(eql_results)}")
            print(f"RDFLib results: {len(rdflib_results)}")
            print(f"SQLAlchemy results: {len(sql_results)}")
            assert (
                len(sql_results)
                == len(sparql_results)
                == len(eql_results)
                == len(rdflib_results)
                == len(owlready2_results)
            )
            owlready2_world.close()

        backend_runtimes = {
            Backend.SPARQLWrapper: current_sparqlwrapper_runtimes,
            Backend.SQLAlchemy: current_sqlalchemy_runtimes,
            Backend.EQL: current_eql_runtimes,
            Backend.RDFLib: current_rdflib_runtimes,
            Backend.Owlready2: current_owlready2_runtimes,
        }

        query_timings.append(
            QueryTiming(
                query_id=sparql_query.number,
                backend_runtimes=backend_runtimes,
                results_count=len(sql_results),
            )
        )

    exporter = LatexPerformanceExporter(timings=query_timings)
    exporter.export_query_performance()


if __name__ == "__main__":
    evaluate_queries(1)
