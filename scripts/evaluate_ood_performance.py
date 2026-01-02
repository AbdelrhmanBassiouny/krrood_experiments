import enum
import os
import time
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import SPARQLWrapper
from krrood.ormatic.dao import to_dao
from krrood.ormatic.utils import create_engine, drop_database
from sqlalchemy.orm import sessionmaker

from owl2bench.orm.ormatic_interface import Base, WorldDAO
from owl2bench.loader import WorldLoader
import owl2bench.sqlalchemy_queries


class Backend(enum.Enum):
    SQLAlchemy = "sqlalchemy"
    SPARQLWrapper = "SPARQLWrapper"


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
        return float(np.mean(self.backend_runtimes[backend]))

    def get_runtime_standard_deviation(self, backend: Backend) -> float:
        """
        Returns the standard deviation of the runtime for a given backend.
        """
        return float(np.std(self.backend_runtimes[backend]))


class TypstTableExporter:
    def __init__(self, timings: List[QueryTiming]):
        self.timings = timings

    def export(self, output_path: str = "ood_performance.typ") -> None:
        """
        Exports the timing results to a Typst table.
        """
        content = [
            "#table(",
            "  columns: (auto, auto, auto),",
            "  inset: 10pt,",
            "  align: horizon,",
            "  [*Query*], [*SQLAlchemy (ms)*], [*SPARQLWrapper (ms)*],",
        ]

        for timing in self.timings:
            sql_mean = timing.get_average_runtime(Backend.SQLAlchemy) * 1000
            sql_std = timing.get_runtime_standard_deviation(Backend.SQLAlchemy) * 1000
            sparql_mean = timing.get_average_runtime(Backend.SPARQLWrapper) * 1000
            sparql_std = (
                timing.get_runtime_standard_deviation(Backend.SPARQLWrapper) * 1000
            )

            content.append(
                f"  [{timing.label}], [{sql_mean:.2f} ± {sql_std:.2f}], [{sparql_mean:.2f} ± {sparql_std:.2f}],"
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

for query in owl2bench.sqlalchemy_queries.all_queries:
    current_sqlalchemy_runtimes = []
    current_sparqlwrapper_runtimes = []

    for _ in range(iterations_per_query):
        start = time.time()
        sql_results = session.execute(query.statement)
        current_sqlalchemy_runtimes.append(time.time() - start)

        # Execute query
        sparql.setQuery(query.sparql_query.raw_sparql_string)
        start = time.time()
        sparql_results = sparql.query().convert()
        current_sparqlwrapper_runtimes.append(time.time() - start)

    query_timings.append(
        QueryTiming(
            query_id=query.sparql_query.number,
            backend_runtimes={
                Backend.SQLAlchemy: current_sqlalchemy_runtimes,
                Backend.SPARQLWrapper: current_sparqlwrapper_runtimes,
            },
        )
    )


exporter = TypstTableExporter(query_timings)
exporter.export()
