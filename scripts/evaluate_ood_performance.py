import enum
import os
import time
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import SPARQLWrapper
import rdflib
import owlready2
import tqdm
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from owl2bench.orm.ormatic_interface import Base, WorldDAO
from owl2bench.loader import WorldLoader
import owl2bench.sqlalchemy_queries
import owl2bench.eql_queries
import owl2bench.sparql_queries
from owl2bench.sparql_queries import OWLProfile


class Backend(enum.Enum):
    SQLAlchemy = "SQLAlchemy"
    SPARQLWrapper = "SPARQLWrapper"
    EQL = "EQL"
    RDFLib = "RDFLib"
    Owlready2 = "owlready2"


@dataclass
class QueryTiming:
    query_id: int
    backend_runtimes: Dict[Backend, List[float]]
    results_count: int

    @property
    def label(self) -> str:
        """
        Returns the label for this query.
        """
        return f"Q{self.query_id}"

    def get_average_runtime(self, backend: Backend) -> float:
        """
        Returns the average runtime for a given backend.
        """
        runtimes = self.backend_runtimes.get(backend, [])
        if not runtimes:
            return float("nan")
        return float(np.mean(runtimes))

    def get_runtime_standard_deviation(self, backend: Backend) -> float:
        """
        Returns the standard deviation of the runtime for a given backend.
        """
        runtimes = self.backend_runtimes.get(backend, [])
        if not runtimes:
            return float("nan")
        return float(np.std(runtimes))


class LatexTableExporter:
    def __init__(self, timings: List[QueryTiming]):
        self.timings = timings

    def _format_timing(self, mean: float, std: float, is_best: bool = False) -> str:
        """
        Formats the timing results for LaTeX.
        """
        if np.isnan(mean):
            return "---"
        formatted = f"{mean * 1000:.2f} \\pm {std * 1000:.2f}"
        if is_best:
            return f"\\mathbf{{{formatted}}}"
        return formatted

    def export(self, output_path: str = "ood_performance.tex") -> None:
        """
        Exports the timing results to a LaTeX table.
        """
        backend_names = [backend.value.replace("_", "\\_") for backend in Backend]
        columns = ["Query", "Results"] + [f"{name}" for name in backend_names]

        # Escape underscores in column headers if any
        header = " & ".join([f"\\textbf{{{col}}}" for col in columns]) + " \\\\"

        column_spec = "l" * len(columns)
        content = [
            "\\begin{tabular}{" + column_spec + "}",
            "\\hline",
            header,
            "\\hline",
        ]

        for timing in self.timings:
            means = {
                backend: timing.get_average_runtime(backend) for backend in Backend
            }
            stds = {
                backend: timing.get_runtime_standard_deviation(backend)
                for backend in Backend
            }

            valid_means = [m for m in means.values() if not np.isnan(m)]
            min_mean = min(valid_means) if valid_means else float("inf")

            row_cells = [timing.label, str(timing.results_count)]
            for backend in Backend:
                is_best = not np.isnan(means[backend]) and means[backend] == min_mean
                formatted = self._format_timing(means[backend], stds[backend], is_best)
                row_cells.append(f"${formatted}$")

            content.append(" & ".join(row_cells) + " \\\\")

        content.append("\\hline")

        # Add geometric mean summary row
        backend_geomeans = {}
        for backend in Backend:
            runtimes = [timing.get_average_runtime(backend) for timing in self.timings]
            valid_runtimes = [r for r in runtimes if not np.isnan(r) and r > 0]
            if valid_runtimes:
                # Calculate geometric mean using log average: exp(mean(log(x)))
                backend_geomeans[backend] = float(
                    np.exp(np.mean(np.log(valid_runtimes)))
                )
            else:
                backend_geomeans[backend] = float("nan")

        valid_geomeans = [m for m in backend_geomeans.values() if not np.isnan(m)]
        min_geomean = min(valid_geomeans) if valid_geomeans else float("inf")

        summary_cells = ["\\textbf{Geom. Mean}", "---"]
        for backend in Backend:
            val = backend_geomeans[backend]
            is_best = not np.isnan(val) and val == min_geomean
            if np.isnan(val):
                formatted = "---"
            else:
                formatted = f"{val * 1000:.2f}"
                if is_best:
                    formatted = f"\\mathbf{{{formatted}}}"
                formatted = f"${formatted}$"
            summary_cells.append(formatted)

        content.append(" & ".join(summary_cells) + " \\\\")
        content.append("\\hline")
        content.append("\\end{tabular}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        print(f"LaTeX table saved to {output_path}")


iterations_per_query = 1

sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
sparql.setReturnFormat(SPARQLWrapper.JSON)

dir_path = os.path.dirname(os.path.realpath(__file__))
rdf_file_path = os.path.join(dir_path, "..", "resources", "statements.rdf")

print("Loading data into owlready2...")
owlready2_world = owlready2.World()
owlready2_world.get_ontology(rdf_file_path).load()

print("Loading data into rdflib...")
rdflib_graph = rdflib.Graph()
rdflib_graph.parse(rdf_file_path, format="xml")

print("Loading data into KRROOD from GraphDB...")
loader = WorldLoader(sparql)
loader.parse()

engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
drop_database(engine)
Base.metadata.create_all(engine)

session = sessionmaker(engine)()

dao: WorldDAO = to_dao(loader.world)

session.add(dao)
session.commit()
session.expunge_all()

print("Loading data into KRROOD from SQLAlchemy...")
world_dao: WorldDAO = session.scalars(select(WorldDAO)).one()
world = world_dao.from_dao()

query_timings: List[QueryTiming] = []

sparql_queries = [
    q for q in owl2bench.sparql_queries.all_queries if OWLProfile.RL in q.profile
]

pbar = tqdm.tqdm(sparql_queries)
for sparql_query in pbar:
    pbar.set_description(f"Evaluating query {sparql_query.number}")

    # Find the corresponding sqlalchemy query
    sqlalchemy_query = [
        q
        for q in owl2bench.sqlalchemy_queries.all_queries
        if q.sparql_query == sparql_query
    ][0]

    # Find the corresponding eql query
    eql_query = [
        q for q in owl2bench.eql_queries.all_queries if q.sparql_query == sparql_query
    ][0]

    current_sqlalchemy_runtimes = []
    current_sparqlwrapper_runtimes = []
    current_eql_runtimes = []
    current_rdflib_runtimes = []
    current_owlready2_runtimes = []

    for _ in range(iterations_per_query):

        # Execute SQLAlchemy query
        start = time.time()
        sql_results = session.execute(sqlalchemy_query.statement).all()
        current_sqlalchemy_runtimes.append(time.time() - start)

        # Execute SPARQL query
        sparql.setQuery(sparql_query.raw_sparql_string)
        start = time.time()
        sparql_results = sparql.query().convert()
        current_sparqlwrapper_runtimes.append(time.time() - start)

        # Execute EQL query
        start = time.time()
        eql_results = list(eql_query.query(loader.world).evaluate())
        current_eql_runtimes.append(time.time() - start)

        # Execute RDFLib query
        start = time.time()
        rdflib_results = list(rdflib_graph.query(sparql_query.raw_sparql_string))
        current_rdflib_runtimes.append(time.time() - start)

        # Execute Owlready2 query
        start = time.time()
        owlready2_results = list(
            owlready2_world.sparql(
                sparql_query.raw_sparql_string, error_on_undefined_entities=False
            )
        )
        current_owlready2_runtimes.append(time.time() - start)

        assert (
            len(sql_results)
            == len(sparql_results["results"]["bindings"])
            == len(eql_results)
            == len(rdflib_results)
            == len(owlready2_results)
        )

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


exporter = LatexTableExporter(query_timings)
exporter.export()
