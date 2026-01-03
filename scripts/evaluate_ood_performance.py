import enum
import os
import time
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import SPARQLWrapper
import tqdm
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy.orm import sessionmaker

from owl2bench.orm.ormatic_interface import Base, WorldDAO
from owl2bench.loader import WorldLoader
import owl2bench.sqlalchemy_queries
import owl2bench.eql_queries
import owl2bench.sparql_queries
from owl2bench.sparql_queries import OWLProfile


class Backend(enum.Enum):
    SQLAlchemy = "sqlalchemy"
    SPARQLWrapper = "SPARQLWrapper"
    EQL = "EQL"


@dataclass
class QueryTiming:
    query_id: int
    backend_runtimes: Dict[Backend, List[float]]

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


class TypstTableExporter:
    def __init__(self, timings: List[QueryTiming]):
        self.timings = timings

    def _format_timing(self, mean: float, std: float) -> str:
        if np.isnan(mean):
            return "---"
        return f"{mean * 1000:.2f} ± {std * 1000:.2f}"

    def export(self, output_path: str = "ood_performance.typ") -> None:
        """
        Exports the timing results to a Typst table.
        """
        content = [
            "#table(",
            "  columns: (auto, auto, auto, auto),",
            "  inset: 10pt,",
            "  align: horizon,",
            "  [*Query*], [*SQLAlchemy (ms)*], [*SPARQLWrapper (ms)*], [*EQL (ms)*],",
        ]

        for timing in self.timings:
            sql_mean = timing.get_average_runtime(Backend.SQLAlchemy)
            sql_std = timing.get_runtime_standard_deviation(Backend.SQLAlchemy)
            sparql_mean = timing.get_average_runtime(Backend.SPARQLWrapper)
            sparql_std = timing.get_runtime_standard_deviation(Backend.SPARQLWrapper)
            eql_mean = timing.get_average_runtime(Backend.EQL)
            eql_std = timing.get_runtime_standard_deviation(Backend.EQL)

            content.append(
                f"  [{timing.label}], [{self._format_timing(sql_mean, sql_std)}], [{self._format_timing(sparql_mean, sparql_std)}], [{self._format_timing(eql_mean, eql_std)}],"
            )

        content.append(")")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        print(f"Typst table saved to {output_path}")


iterations_per_query = 10

sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
sparql.setReturnFormat(SPARQLWrapper.JSON)
loader = WorldLoader(sparql)
loader.parse()

engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
drop_database(engine)
Base.metadata.create_all(engine)

session = sessionmaker(engine)()

dao: WorldDAO = to_dao(loader.world)

session.add(dao)
session.commit()

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

    for _ in range(iterations_per_query):

        # Execute SQLAlchemy query
        start = time.time()
        sql_results = session.execute(sqlalchemy_query.statement)
        current_sqlalchemy_runtimes.append(time.time() - start)

        # Execute SPARQL query
        sparql.setQuery(sparql_query.raw_sparql_string)
        start = time.time()
        sparql_results = sparql.query().convert()
        current_sparqlwrapper_runtimes.append(time.time() - start)

        # Execute EQL query
        start = time.time()
        eql_results = eql_query.query(loader.world).evaluate()
        current_eql_runtimes.append(time.time() - start)

    backend_runtimes = {
        Backend.SPARQLWrapper: current_sparqlwrapper_runtimes,
        Backend.SQLAlchemy: current_sqlalchemy_runtimes,
        Backend.EQL: current_eql_runtimes,
    }

    query_timings.append(
        QueryTiming(
            query_id=sparql_query.number,
            backend_runtimes=backend_runtimes,
        )
    )


exporter = TypstTableExporter(query_timings)
exporter.export()
