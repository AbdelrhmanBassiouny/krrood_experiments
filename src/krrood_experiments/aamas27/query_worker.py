"""
Worker process for the query experiment: sets up one framework, executes the OWL 2 RL queries of OWL2Bench a number
of times, and writes the timings and the normalised answer set of every query.

Answer sets are written as sorted, de-duplicated, tab-separated lines (one answer tuple per line, columns in the
order of the SPARQL ``SELECT`` variables) into ``<answers-dir>/<framework>/q<N>.tsv.gz`` so that the answer check can
compare them by streaming.
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import statistics
import sys
import time
import weakref
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import rdflib

from .environment import REASONED_FILE, UNREASONED_FILE, write_json
from .memory import print_worker_result

FRAMEWORKS = ["graphdb", "eql", "sqlalchemy", "rdflib", "owlready2"]
"""
Frameworks of the query experiment.
"""

RL_QUERIES = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22]
"""
The 18 OWL2Bench queries applicable to the OWL 2 RL profile.
"""


def sparql_queries() -> Dict[int, Any]:
    """
    :return: All OWL2Bench SPARQL queries by number, including the ones commented out of ``all_queries``.
    """
    from krrood_experiments.owl2bench import sparql_queries as module

    return {
        value.number: value
        for value in vars(module).values()
        if isinstance(value, module.SPARQLQuery)
    }


def select_variables(sparql: str) -> List[str]:
    """
    :param sparql: A SPARQL SELECT query.
    :return: The projected variable names in order.
    """
    projection = re.search(r"SELECT\s+(?:DISTINCT\s+)?(.*?)\s+WHERE", sparql, re.S | re.I).group(1)
    return re.findall(r"\?(\w+)", projection)


def normalize(value: Any) -> str:
    """
    Normalise one answer value to a string: the URI of an individual, or the lexical form of the Python value of a
    literal.

    :param value: A value returned by any of the frameworks.
    :return: The normalised string.
    """
    if isinstance(value, weakref.ReferenceType):
        value = value()
    if isinstance(value, rdflib.Literal):
        return str(value.toPython())
    if isinstance(value, rdflib.URIRef):
        return str(value)
    iri = getattr(value, "iri", None)  # owlready2 entities
    if isinstance(iri, str):
        return iri
    uri = getattr(value, "uri", None)
    if uri is not None:
        return str(uri)
    return str(value)


def write_answers(path: Path, answers: Iterable[Tuple[str, ...]]) -> int:
    """
    Write a sorted, de-duplicated answer set.

    :param path: Target ``.tsv.gz`` file.
    :param answers: Answer tuples of normalised strings.
    :return: The number of distinct answers.
    """
    lines = sorted({"\t".join(answer) for answer in answers})
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        for line in lines:
            stream.write(line + "\n")
    return len(lines)


class Framework:
    """
    Interface of a framework under test.
    """

    name: str = ""

    def setup(self) -> Dict[str, Any]:
        """
        Prepare the framework and return setup measurements.
        """
        return {}

    def before_repetition(self) -> None:
        """
        Reset caches before every repetition (outside of the measured time).
        """

    def execute(self, number: int) -> Any:
        """
        Execute a query and return its raw result (inside the measured time).
        """
        raise NotImplementedError

    def answers(self, number: int, result: Any, variables: List[str]) -> List[Tuple[str, ...]]:
        """
        Normalise the raw result of a query into answer tuples (outside of the measured time).
        """
        raise NotImplementedError


class GraphDBFramework(Framework):
    """
    SPARQL over HTTP to GraphDB through SPARQLWrapper, as in the January 2026 run.
    """

    name = "graphdb"

    def __init__(self, endpoint: str):
        import SPARQLWrapper

        self.sparql = SPARQLWrapper.SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(SPARQLWrapper.JSON)
        self.endpoint = endpoint
        self.queries = sparql_queries()

    def setup(self) -> Dict[str, Any]:
        return {"endpoint": self.endpoint}

    def execute(self, number: int) -> Any:
        self.sparql.setQuery(self.queries[number].raw_sparql_string)
        return list(self.sparql.query().convert()["results"]["bindings"])

    def answers(self, number, result, variables):
        def value(binding: Dict[str, str]) -> str:
            if binding["type"] == "literal":
                datatype = binding.get("datatype")
                return normalize(
                    rdflib.Literal(binding["value"], datatype=rdflib.URIRef(datatype) if datatype else None)
                )
            return binding["value"]

        return [tuple(value(row[v]) for v in variables) for row in result]


class EQLFramework(Framework):
    """
    KRROOD: Ontomatic loading of the raw data and EQL queries over the Python objects.
    """

    name = "eql"

    def __init__(self, input_file: Path):
        self.input_file = input_file

    def setup(self) -> Dict[str, Any]:
        from krrood_experiments.owl2bench.ontomatic.helpers import (
            load_instances_for_owl2bench_with_predicates,
        )
        from krrood_experiments.owl2bench.ontomatic.owl2bench_eql_queries import get_eql_queries

        start = time.perf_counter()
        self.registry = load_instances_for_owl2bench_with_predicates(str(self.input_file))
        loading_seconds = time.perf_counter() - start
        self.queries = {query.id_: query for query in get_eql_queries()}
        return {"krrood_loading_seconds": loading_seconds, "input_file": str(self.input_file)}

    def execute(self, number: int) -> Any:
        return list(self.queries[number].evaluate())

    def answers(self, number, result, variables):
        return [tuple(normalize(row[v]) for v in variables) for row in result]


class SQLAlchemyFramework(EQLFramework):
    """
    KRROOD objects persisted through ORMatic into PostgreSQL and queried with SQLAlchemy.
    """

    name = "sqlalchemy"

    def setup(self) -> Dict[str, Any]:
        measurements = super().setup()
        from krrood.ormatic.utils import create_engine
        from sqlalchemy.orm import sessionmaker
        from krrood_experiments.aamas27.loading_worker import persist_registry
        from krrood_experiments.owl2bench.ontomatic import sqlalchemy_queries

        start = time.perf_counter()
        persist_registry(self.registry)
        measurements["persist_seconds"] = time.perf_counter() - start
        self.engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
        self.session = sessionmaker(self.engine)()
        self.statements = {
            query.sparql_query.number: query.statement for query in sqlalchemy_queries.all_queries
        }
        self.resolver = SQLAnswerResolver(self.session)
        return measurements

    def before_repetition(self) -> None:
        self.session.expunge_all()

    def execute(self, number: int) -> Any:
        return list(self.session.execute(self.statements[number]).all())

    def answers(self, number, result, variables):
        statement = self.statements[number]
        return [self.resolver.resolve_row(statement, row) for row in result]


class SQLAnswerResolver:
    """
    Maps rows returned by the ORMatic SQLAlchemy queries (DAO objects, association rows with database identifiers,
    or plain values) to URIs.
    """

    def __init__(self, session):
        from sqlalchemy import select, inspect as sqlalchemy_inspect
        from krrood_experiments.owl2bench.ontomatic.orm import ormatic_interface as orm

        self.session = session
        self.uri_by_thing_id = dict(
            session.execute(select(orm.OWL2BenchThingDAO.database_id, orm.OWL2BenchThingDAO.uri)).all()
        )
        self.dao_by_table: Dict[str, type] = {}
        for value in vars(orm).values():
            if isinstance(value, type) and hasattr(value, "__tablename__") and hasattr(value, "__mapper__"):
                self.dao_by_table[value.__table__.name] = value
        self.inspect = sqlalchemy_inspect

    def uri_of_dao(self, dao: Any) -> str:
        """
        :param dao: A DAO object of a thing or of a role.
        :return: The URI of the individual, following role takers.
        """
        while getattr(dao, "uri", None) is None:
            role_taker = None
            for relationship in self.inspect(type(dao)).relationships:
                if not relationship.uselist and relationship.direction.name == "MANYTOONE":
                    candidate = getattr(dao, relationship.key)
                    if candidate is not None and relationship.key in _ROLE_TAKER_KEYS:
                        role_taker = candidate
                        break
            if role_taker is None:
                raise ValueError(f"Cannot resolve the URI of {dao!r}")
            dao = role_taker
        return dao.uri

    def uri_of_id(self, table: str, database_id: int) -> str:
        """
        :param table: The DAO table the identifier refers to.
        :param database_id: The identifier.
        :return: The URI of the individual.
        """
        if database_id in self.uri_by_thing_id and self._is_thing_table(table):
            return self.uri_by_thing_id[database_id]
        dao = self.session.get(self.dao_by_table[table], database_id)
        return self.uri_of_dao(dao)

    def _is_thing_table(self, table: str) -> bool:
        from krrood_experiments.owl2bench.ontomatic.orm import ormatic_interface as orm

        dao = self.dao_by_table.get(table)
        return dao is not None and issubclass(dao, orm.OWL2BenchThingDAO)

    def resolve_row(self, statement, row) -> Tuple[str, ...]:
        values = []
        for column, value in zip(statement.selected_columns, row):
            if hasattr(value, "__mapper__") or hasattr(type(value), "__mapper__"):
                values.append(self.uri_of_dao(value))
                continue
            foreign_keys = list(getattr(column, "foreign_keys", []))
            if foreign_keys:
                values.append(self.uri_of_id(foreign_keys[0].column.table.name, value))
            elif getattr(column, "key", None) == "database_id" and getattr(column, "table", None) is not None:
                values.append(self.uri_of_id(column.table.name, value))
            else:
                values.append(normalize(value))
        return tuple(values)


_ROLE_TAKER_KEYS = {
    "person",
    "student",
    "faculty",
    "professor",
    "full_professor",
    "organization",
    "employee",
}
"""
Names of the role-taker relationships in the generated ORM (``Role[Person]`` is stored as ``person`` etc.).
"""


class RDFLibFramework(Framework):
    """
    SPARQL with RDFLib over the reasoned data file.
    """

    name = "rdflib"

    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.queries = sparql_queries()

    def setup(self) -> Dict[str, Any]:
        start = time.perf_counter()
        self.graph = rdflib.Graph()
        self.graph.parse(str(self.input_file), format="xml")
        return {"parse_seconds": time.perf_counter() - start, "triples": len(self.graph),
                "input_file": str(self.input_file)}

    def execute(self, number: int) -> Any:
        return list(self.graph.query(self.queries[number].raw_sparql_string))

    def answers(self, number, result, variables):
        return [tuple(normalize(value) for value in row) for row in result]


class Owlready2Framework(Framework):
    """
    SPARQL with owlready2 over the reasoned data file. By default the world is reloaded before every repetition, as in
    the January 2026 run, so that no query result is served from a cache.
    """

    name = "owlready2"

    def __init__(self, input_file: Path, reload_world: bool):
        self.input_file = input_file
        self.reload_world = reload_world
        self.queries = sparql_queries()
        self.world = None

    def _load(self) -> float:
        import owlready2

        if self.world is not None:
            self.world.close()
        start = time.perf_counter()
        self.world = owlready2.World()
        self.world.get_ontology(str(self.input_file)).load()
        return time.perf_counter() - start

    def setup(self) -> Dict[str, Any]:
        return {"load_seconds": self._load(), "reload_world_every_repetition": self.reload_world,
                "input_file": str(self.input_file)}

    def before_repetition(self) -> None:
        if self.reload_world:
            self._load()

    def execute(self, number: int) -> Any:
        return list(self.world.sparql(self.queries[number].raw_sparql_string, error_on_undefined_entities=False))

    def answers(self, number, result, variables):
        return [tuple(normalize(value) for value in row) for row in result]


def build_framework(arguments: argparse.Namespace) -> Framework:
    if arguments.framework == "graphdb":
        return GraphDBFramework(arguments.graphdb_endpoint)
    if arguments.framework == "eql":
        return EQLFramework(Path(arguments.raw_file))
    if arguments.framework == "sqlalchemy":
        return SQLAlchemyFramework(Path(arguments.raw_file))
    if arguments.framework == "rdflib":
        return RDFLibFramework(Path(arguments.reasoned_file))
    return Owlready2Framework(Path(arguments.reasoned_file), not arguments.owlready2_keep_world)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", choices=FRAMEWORKS, required=True)
    parser.add_argument("--queries", default=",".join(map(str, RL_QUERIES)))
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--answers-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--graphdb-endpoint", default=None)
    parser.add_argument("--raw-file", default=str(UNREASONED_FILE))
    parser.add_argument("--reasoned-file", default=str(REASONED_FILE))
    parser.add_argument("--owlready2-keep-world", action="store_true",
                        help="do not reload the owlready2 world before every repetition")
    arguments = parser.parse_args()

    framework = build_framework(arguments)
    queries = [int(q) for q in arguments.queries.split(",") if q]
    texts = sparql_queries()
    setup = framework.setup()
    print(f"[{framework.name}] setup done: {setup}", flush=True)
    report: Dict[str, Any] = {"framework": framework.name, "setup": setup, "repetitions": arguments.repetitions,
                              "queries": {}}
    answers_directory = Path(arguments.answers_dir) / framework.name
    for number in queries:
        variables = select_variables(texts[number].raw_sparql_string)
        times_ms: List[float] = []
        entry: Dict[str, Any] = {"variables": variables}
        try:
            for repetition in range(arguments.repetitions):
                framework.before_repetition()
                start = time.perf_counter()
                result = framework.execute(number)
                times_ms.append((time.perf_counter() - start) * 1000)
                if repetition == 0:
                    entry["raw_rows"] = len(result)
                    answers = framework.answers(number, result, variables)
                    entry["distinct_answers"] = write_answers(answers_directory / f"q{number}.tsv.gz", answers)
                else:
                    entry.setdefault("raw_rows_per_repetition", []).append(len(result))
                del result
            entry["status"] = "ok"
        except Exception as error:  # a failing query must not hide the results of the others
            entry["status"] = "error"
            entry["error"] = f"{type(error).__name__}: {error}"
        entry["times_ms"] = times_ms
        if times_ms:
            entry["mean_ms"] = statistics.mean(times_ms)
            entry["std_ms"] = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
        report["queries"][str(number)] = entry
        print(f"[{framework.name}] Q{number}: {entry.get('status')} rows={entry.get('raw_rows')} "
              f"distinct={entry.get('distinct_answers')} mean={entry.get('mean_ms', float('nan')):.2f} ms",
              flush=True)
        write_json(Path(arguments.output), report)
    print_worker_result({"output": arguments.output})
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
