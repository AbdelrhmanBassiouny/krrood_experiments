import os
import time
from typing import List

import SPARQLWrapper
import owlready2
import rdflib
import tqdm
from krrood.ormatic.dao import to_dao, ToDataAccessObjectState
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy.orm import sessionmaker

import krrood_experiments.owl2bench.ontomatic.sqlalchemy_queries
import krrood_experiments.owl2bench.sparql_queries
from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_eql_queries import get_eql_queries
from krrood_experiments.owl2bench.ontomatic.orm.ormatic_interface import Base
from krrood_experiments.owl2bench.ood.performance_utils import (
    Backend,
    QueryTiming,
    LatexPerformanceExporter,
)
from krrood_experiments.owl2bench.sparql_queries import OWLProfile


def evaluate_queries(iterations_per_query: int = 10):
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    rdf_file_path = os.path.join(
        dir_path, "..", "resources", "owl2bench_statements_reasoned.rdf"
    )
    unreasoned_owl2bench_file_path = os.path.join(
        dir_path, "..", "resources", "owl2bench_statements_unreasoned.rdf"
    )

    print("Setting up backends for query evaluation...")

    # RDFLib setup
    rdflib_graph = rdflib.Graph()
    rdflib_graph.parse(
        rdf_file_path,
        format="xml",
    )

    # KRROOD EQL setup
    registry = load_instances_for_owl2bench_with_predicates(
        unreasoned_owl2bench_file_path
    )

    # KRROOD SQLAlchemy setup
    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)()

    state = ToDataAccessObjectState()
    for instance in tqdm.tqdm(
        [v for uri_vs in registry._by_uri.values() for v in uri_vs]
    ):
        dao = to_dao(instance, state)
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
            for q in krrood_experiments.owl2bench.ontomatic.sqlalchemy_queries.all_queries
            if q.sparql_query == sparql_query
        ][0]

        # Find the corresponding eql query
        eql_query = [q for q in get_eql_queries() if q.id_ == sparql_query.number][0]

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
            eql_results = list(eql_query.evaluate())
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
