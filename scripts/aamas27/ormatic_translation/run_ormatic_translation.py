"""
ORMatic's translation of the 18 OWL2Bench OWL 2 RL queries from EQL to SQL (paper, Section 6), checked on the
benchmark's knowledge.

The translator belongs to the current version of KRROOD, whose EQL syntax and model differ from those of the earlier
version that the experiments use. This script therefore

1. reads the OWL 2 RL closure of the benchmark that GraphDB computed (the pre-reasoned input of the experiments) and
   builds from it the objects of owl2bench_translation_model.py, the part of the OWL2Bench model that the queries use:
   every individual of a class of the model, its roles (Student, LeisureStudent, Faculty, T20CricketFan) and every
   statement of a property of the model;
2. stores the objects with ORMatic in a database (PostgreSQL in the run of the paper);
3. writes the 18 queries in the current EQL, as close as possible to the queries of the experiments
   (owl2bench_eql_queries.py), evaluates each in working memory, translates it with ``eql_to_sql`` and evaluates the
   translation in the database;
4. compares, per query, the answer set of the translation with that of EQL in working memory and with GraphDB's answer
   set of the paper's run, normalised as the query experiment does (sorted, de-duplicated tuples of IRIs and lexical
   forms);
5. measures the time of the translated query: of ``evaluate`` (translation, execution and the answers as EQL returns
   them) and of the translated statement alone, as the hand-written SQLAlchemy queries of the query experiment are
   measured (``session.execute(statement).all()`` after ``expunge_all``). Relationships are loaded lazily, as in the
   interface of the experiments (see ``lazy_translation``).

Usage (current KRROOD environment; psycopg2 for PostgreSQL)::

    python run_ormatic_translation.py --reasoned-file owl2bench_statements_reasoned.rdf \
        --reference-answers results/run/check/answers/graphdb --database-uri postgresql+psycopg2://... \
        --output-dir results/aamas27/ormatic_translation-20261008
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import platform
import statistics
import sys
import time
import traceback
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

import rdflib
from rdflib.namespace import RDF
from sqlalchemy import select
from sqlalchemy.orm import Session, configure_mappers, lazyload

sys.path.insert(0, str(Path(__file__).resolve().parent))

from krrood.entity_query_language.factories import (  # noqa: E402
    a,
    an,
    contains,
    entity,
    exists,
    flat_variable,
    set_of,
    variable,
)
from krrood.ormatic.data_access_objects.helper import to_dao  # noqa: E402
from krrood.ormatic.data_access_objects.to_dao import ToDataAccessObjectState  # noqa: E402
from krrood.ormatic.eql_interface import eql_to_sql  # noqa: E402
from krrood.ormatic.utils import create_engine, drop_database  # noqa: E402

import owl2bench_translation_interface as interface  # noqa: E402
from owl2bench_translation_model import (  # noqa: E402
    College,
    CollegeDiscipline,
    Course,
    Faculty,
    Interest,
    LeisureStudent,
    Man,
    Organization,
    Person,
    Student,
    T20CricketFan,
    Thing,
    University,
    Woman,
    WomanCollege,
)

NAMESPACE = "http://benchmark/OWL2Bench#"

INDIVIDUAL_CLASSES: List[List[Tuple[str, type]]] = [
    [("WomanCollege", WomanCollege), ("College", College), ("University", University),
     ("Organization", Organization)],
    [("Woman", Woman), ("Man", Man), ("Person", Person)],
    [("Course", Course)],
    [("Interest", Interest)],
    [("CollegeDiscipline", CollegeDiscipline)],
]
"""
The classes of the model whose instances are individuals, in branches of the class hierarchy, most specific first. An
individual gets one object per branch among its types, of the first class of the branch among them. An individual of
two branches, such as a research group that the closure also makes a person, thus gets two objects that share their
IRI, as Ontomatic gives it (paper, Section 7.1); every fact is stored on the object whose class declares the property.
"""

ROLE_CLASSES = ["Student", "LeisureStudent", "Faculty", "T20CricketFan"]
"""
The classes of the model that are roles: an individual of such a type gets the role object.
"""


@dataclass(frozen=True)
class PropertyMapping:
    """
    How the statements of one OWL property become elements of a collection or the value of an attribute.
    """

    owl_property: str
    """The local name of the property in the OWL2Bench namespace."""
    attribute: str
    """The attribute of the model."""
    subject_kind: str
    """``individual`` or the name of a role class: what the subject's object is."""
    object_kind: str
    """``individual``, a role class name or ``literal``."""
    object_class: Optional[type] = None
    """For individual objects: the class to create an individual of when the object has no class of the model."""
    subject_class: type = Thing
    """The class of the model that declares the attribute."""


PROPERTIES = [
    PropertyMapping("isMemberOf", "is_member_of", "individual", "individual", Organization, Person),
    PropertyMapping("isPartOf", "is_part_of", "individual", "individual", Organization, Organization),
    PropertyMapping("hasAge", "has_age", "individual", "literal", None, Person),
    PropertyMapping("hasAlumnus", "has_alumnus", "individual", "individual", Person, University),
    PropertyMapping("isAffiliatedOrganizationOf", "is_affiliated_organization_of", "individual", "individual",
                    Organization, Organization),
    PropertyMapping("hasCollegeDiscipline", "has_college_discipline", "individual", "individual", CollegeDiscipline,
                    College),
    PropertyMapping("hasCollaborationWith", "has_collaboration_with", "individual", "individual", Person, Person),
    PropertyMapping("isAdvisedBy", "is_advised_by", "individual", "Faculty", None, Person),
    PropertyMapping("isHeadOf", "is_head_of", "individual", "individual", Organization, Person),
    PropertyMapping("hasHead", "has_head", "individual", "individual", Person, Organization),
    PropertyMapping("isCrazyAbout", "is_crazy_about", "individual", "individual", Interest, Person),
    PropertyMapping("hasSameHomeTownWith", "has_same_home_town_with", "individual", "individual", Person, Thing),
    PropertyMapping("isStudentOf", "is_student_of", "Student", "individual", Organization, Student),
    PropertyMapping("takesCourse", "takes_course", "Student", "individual", Course, Student),
    PropertyMapping("hasDean", "has_dean", "individual", "Faculty", None, Organization),
    PropertyMapping("teachesCourse", "teaches_course", "Faculty", "individual", Course, Faculty),
]
"""
The properties of the model and their OWL counterparts.
"""


@dataclass
class Knowledge:
    """
    The objects built from the closure, with what could not be represented in the model.
    """

    individuals: Dict[str, List[Thing]] = field(default_factory=dict)
    """The objects of every IRI that has one, by IRI: one per branch of INDIVIDUAL_CLASSES."""
    roles: Dict[str, Dict[str, Any]] = field(default_factory=lambda: defaultdict(dict))
    """The role objects by role class name and IRI of the individual that takes the role."""
    statistics: Dict[str, Any] = field(default_factory=lambda: defaultdict(Counter))
    """Counts of what was built and of statements that were dropped, with the reason."""

    def instances(self, cls: type) -> List[Any]:
        """
        :param cls: A class of the model.
        :return: All objects that are instances of the class, individuals and roles.
        """
        return [o for o in self.all_objects() if isinstance(o, cls)]

    def all_objects(self) -> List[Any]:
        """
        :return: Every individual and every role object.
        """
        return [o for objects in self.individuals.values() for o in objects] + [
            r for by_iri in self.roles.values() for r in by_iri.values()]

    def object_of(self, iri: str, cls: type) -> Optional[Thing]:
        """
        :param iri: The IRI of an individual.
        :param cls: A class of the model.
        :return: The object of the individual that is an instance of the class, or None.
        """
        return next((o for o in self.individuals.get(iri, []) if isinstance(o, cls)), None)


def local_name(term: Any) -> Optional[str]:
    """
    :param term: An RDF term.
    :return: Its local name if it is an IRI of the OWL2Bench namespace, else None.
    """
    if isinstance(term, rdflib.URIRef) and str(term).startswith(NAMESPACE):
        return str(term)[len(NAMESPACE):]
    return None


def read_statements(reasoned_file: Path, cache: Optional[Path]) -> Tuple[Dict[str, Set[str]], List[Tuple[str, str, Any]]]:
    """
    Read the types of every individual and the statements of the properties of the model from the closure.

    :param reasoned_file: The closure as RDF/XML.
    :param cache: A gzipped JSON file in which the result is kept between runs, or None.
    :return: The types (local names of OWL2Bench classes) per IRI, and the statements (subject IRI, local name of the
        property, object IRI or lexical form).
    """
    if cache is not None and cache.exists():
        with gzip.open(cache, "rt", encoding="utf-8") as stream:
            data = json.load(stream)
        return {k: set(v) for k, v in data["types"].items()}, [tuple(s) for s in data["statements"]]
    graph = rdflib.Graph()
    graph.parse(str(reasoned_file), format="xml")
    wanted = {m.owl_property for m in PROPERTIES}
    types: Dict[str, Set[str]] = defaultdict(set)
    statements: List[Tuple[str, str, Any]] = []
    for subject, predicate, value in graph:
        if not isinstance(subject, rdflib.URIRef):
            continue
        if predicate == RDF.type:
            name = local_name(value)
            if name is not None:
                types[str(subject)].add(name)
            continue
        name = local_name(predicate)
        if name not in wanted:
            continue
        if isinstance(value, rdflib.Literal):
            statements.append((str(subject), name, str(value.toPython())))
        elif isinstance(value, rdflib.URIRef):
            statements.append((str(subject), name, str(value)))
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(cache, "wt", encoding="utf-8") as stream:
            json.dump({"types": {k: sorted(v) for k, v in types.items()}, "statements": statements}, stream)
    return types, statements


def build_knowledge(types: Dict[str, Set[str]], statements: List[Tuple[str, str, Any]]) -> Knowledge:
    """
    Build the objects of the model from the closure.

    :param types: The types per IRI.
    :param statements: The statements of the properties of the model.
    :return: The objects.
    """
    knowledge = Knowledge()
    for iri, names in types.items():
        for branch in INDIVIDUAL_CLASSES:
            for name, cls in branch:
                if name in names:
                    knowledge.individuals.setdefault(iri, []).append(cls(iri))
                    knowledge.statistics["individuals"][cls.__name__] += 1
                    break
        if len(knowledge.individuals.get(iri, [])) > 1:
            knowledge.statistics["individuals_with_several_objects"][
                " and ".join(type(o).__name__ for o in knowledge.individuals[iri])] += 1
    for iri, names in types.items():
        person = knowledge.object_of(iri, Person)
        for role in ROLE_CLASSES:
            if role not in names:
                continue
            if not isinstance(person, Person):
                knowledge.statistics["roles_without_person"][role] += 1
                continue
            if role == "LeisureStudent":
                continue
            cls = {"Student": Student, "Faculty": Faculty, "T20CricketFan": T20CricketFan}[role]
            knowledge.roles[role][iri] = cls(role_taker=person)
            knowledge.statistics["roles"][role] += 1
    for iri, names in types.items():
        if "LeisureStudent" in names and iri in knowledge.roles["Student"]:
            knowledge.roles["LeisureStudent"][iri] = LeisureStudent(role_taker=knowledge.roles["Student"][iri])
            knowledge.statistics["roles"]["LeisureStudent"] += 1
        elif "LeisureStudent" in names:
            knowledge.statistics["roles_without_person"]["LeisureStudent (no Student role)"] += 1
    mappings = {m.owl_property: m for m in PROPERTIES}
    for subject, name, value in statements:
        mapping = mappings[name]
        owner = resolve(knowledge, subject, mapping.subject_kind, mapping.subject_class, None)
        if owner is None or not isinstance(owner, mapping.subject_class):
            knowledge.statistics["dropped_statements"][f"{name}: subject has no {mapping.subject_class.__name__}"] += 1
            continue
        if mapping.object_kind == "literal":
            if getattr(owner, mapping.attribute) not in (None, value):
                knowledge.statistics["dropped_statements"][f"{name}: second value"] += 1
                continue
            setattr(owner, mapping.attribute, value)
        else:
            target = resolve(knowledge, value, mapping.object_kind, mapping.object_class or Thing, mapping.object_class)
            if target is None:
                knowledge.statistics["dropped_statements"][f"{name}: object has no {mapping.object_kind}"] += 1
                continue
            getattr(owner, mapping.attribute).add(target)
        knowledge.statistics["statements"][name] += 1
    knowledge.statistics = {k: dict(v) for k, v in knowledge.statistics.items()}
    return knowledge


def resolve(knowledge: Knowledge, iri: str, kind: str, cls: type, create: Optional[type]) -> Optional[Any]:
    """
    :param knowledge: The objects built so far.
    :param iri: The IRI of an individual.
    :param kind: ``individual`` or the name of a role class.
    :param cls: The class of the model that the object must be an instance of.
    :param create: The class of which an object is created when the IRI has none of ``cls``, or None to create none.
    :return: The object of the individual or its role object, or None.
    """
    if kind != "individual":
        return knowledge.roles[kind].get(iri)
    individual = knowledge.object_of(iri, cls)
    if individual is None and create is not None:
        individual = create(iri)
        knowledge.individuals.setdefault(iri, []).append(individual)
        knowledge.statistics["individuals_created_from_range"][create.__name__] += 1
    return individual


@dataclass
class BenchmarkQuery:
    """
    One of the 18 queries in the current EQL.
    """

    number: int
    query: Any
    selected: List[Any]
    """The selected variables in the order of the SPARQL projection."""
    rewrite: str = ""
    """How the query differs from the one of the experiments, beyond the syntax of the current version."""


def benchmark_queries(knowledge: Knowledge) -> List[BenchmarkQuery]:
    """
    The 18 queries of owl2bench_eql_queries.py in the current EQL. ``variable_from`` over a collection of the earlier
    version is ``flat_variable`` in the current one; the domains are the objects built from the closure.

    :param knowledge: The objects.
    :return: The queries, in the order of the experiments.
    """
    persons, organizations = knowledge.instances(Person), knowledge.instances(Organization)
    queries: List[BenchmarkQuery] = []

    p = variable(Person, domain=persons)
    y = flat_variable(p.is_member_of)
    queries.append(BenchmarkQuery(2, a(set_of(p, y)), [p, y]))

    o = variable(Organization, domain=organizations)
    y = flat_variable(o.is_part_of)
    queries.append(BenchmarkQuery(3, an(set_of(o, y)), [o, y]))

    p = variable(Person, domain=persons)
    queries.append(BenchmarkQuery(4, an(set_of(p, p.has_age).where(p.has_age)), [p, p.has_age]))

    f = variable(T20CricketFan, domain=knowledge.instances(T20CricketFan))
    queries.append(BenchmarkQuery(5, an(entity(f)), [f]))

    u = variable(University, domain=knowledge.instances(University))
    y = flat_variable(u.has_alumnus)
    queries.append(BenchmarkQuery(7, an(set_of(u, y)), [u, y]))

    o = variable(Organization, domain=organizations)
    y = flat_variable(o.is_affiliated_organization_of)
    queries.append(BenchmarkQuery(8, an(set_of(o, y)), [o, y]))

    c = variable(College, domain=knowledge.instances(College))
    d = flat_variable(c.has_college_discipline)
    queries.append(BenchmarkQuery(9, an(entity(c).where(d.uri == NAMESPACE + "NonScience").distinct(c.uri)), [c]))

    p = variable(Person, domain=persons)
    y = flat_variable(p.has_collaboration_with)
    queries.append(BenchmarkQuery(10, an(set_of(p, y)), [p, y]))

    p = variable(Person, domain=persons)
    y = flat_variable(p.is_advised_by)
    queries.append(BenchmarkQuery(11, an(set_of(p, y)), [p, y]))

    p = variable(Person, domain=persons)
    queries.append(BenchmarkQuery(12, an(entity(p).distinct(p.uri)), [p]))

    w = variable(WomanCollege, domain=knowledge.instances(WomanCollege))
    queries.append(BenchmarkQuery(13, an(entity(w)), [w]))

    s = variable(LeisureStudent, domain=knowledge.instances(LeisureStudent))
    queries.append(BenchmarkQuery(14, an(entity(s)), [s]))

    p = variable(Person, domain=persons)
    queries.append(BenchmarkQuery(15, an(entity(p).where(p.is_head_of)), [p]))

    o = variable(Organization, domain=organizations)
    queries.append(BenchmarkQuery(16, an(entity(o).where(o.has_head)), [o]))

    f = variable(Faculty, domain=knowledge.instances(Faculty))
    queries.append(BenchmarkQuery(19, an(entity(f)), [f]))

    p = variable(Person, domain=persons)
    y = flat_variable(p.has_same_home_town_with)
    queries.append(BenchmarkQuery(20, an(set_of(p, y)), [p, y]))

    s = variable(Student, domain=knowledge.instances(Student))
    so = flat_variable(s.is_student_of)
    po = flat_variable(so.is_part_of)
    cd = flat_variable(po.has_college_discipline)
    queries.append(BenchmarkQuery(
        21, an(set_of(s, so).where(exists(cd, cd.uri == NAMESPACE + "Engineering"))), [s, so],
        "exists_on(so, condition) of the earlier version is exists(cd, condition)"))

    s = variable(Student, domain=knowledge.instances(Student))
    o = variable(Organization, domain=organizations)
    z = flat_variable(o.has_dean)
    c = flat_variable(z.teaches_course)
    queries.append(BenchmarkQuery(
        22, an(set_of(s, c).where(contains(s.takes_course, c)).distinct(s.uri, c.uri)), [s, c]))
    return queries


class AnswerNormalizer:
    """
    Normalises answers of EQL and of translated queries to the strings of the query experiment.
    """

    def __init__(self, session: Session):
        self.session = session
        self.iri_by_database_id: Dict[int, str] = {}

    def iri_of_object(self, value: Any) -> str:
        """
        :param value: An object of the model, a role, a data access object or a literal value.
        :return: The IRI of the individual (of the role taker for a role) or the lexical form.
        """
        while hasattr(value, "role_taker") and not hasattr(type(value), "uri"):
            value = value.role_taker
        uri = getattr(value, "uri", None)
        if uri is not None:
            return str(uri)
        return str(value)

    def iri_of_database_id(self, database_id: int) -> str:
        """
        The translation returns the database id instead of the data access object for a variable that is selected
        together with one of its attributes; this resolves it.

        :param database_id: The database id of a symbol.
        :return: Its IRI.
        """
        if database_id not in self.iri_by_database_id:
            dao = self.session.get(interface.SymbolDAO, database_id)
            self.iri_by_database_id[database_id] = self.iri_of_object(dao)
        return self.iri_by_database_id[database_id]

    def row(self, result: Any, selected: List[Any], from_database: bool) -> Tuple[str, ...]:
        """
        :param result: One result of a query: an object, or a mapping from variables to values.
        :param selected: The selected variables.
        :param from_database: Whether the result comes from a translated query.
        :return: The normalised answer tuple.
        """
        values = [result] if len(selected) == 1 and not hasattr(result, "keys") else [result[v] for v in selected]
        normalized = []
        for value in values:
            if from_database and isinstance(value, int) and not isinstance(value, bool):
                normalized.append(self.iri_of_database_id(value))
            else:
                normalized.append(self.iri_of_object(value))
        return tuple(normalized)


def read_answer_set(path: Path) -> Set[Tuple[str, ...]]:
    """
    :param path: A sorted answer file of the query experiment.
    :return: The answer tuples.
    """
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return {tuple(line.rstrip("\n").split("\t")) for line in stream if line.strip()}


def reference_file(directory: Path, number: int) -> Path:
    """
    :param directory: GraphDB's answer files.
    :param number: The query number.
    :return: The answer file of the query (the file names of some runs are capitalised).
    """
    for name in (f"q{number}.tsv.gz", f"Q{number}.tsv.gz"):
        if (directory / name).exists():
            return directory / name
    raise FileNotFoundError(directory / f"q{number}.tsv.gz")


def compare(left: Set[Tuple[str, ...]], right: Set[Tuple[str, ...]]) -> Dict[str, Any]:
    """
    :return: Whether two answer sets are equal, with the sizes of both differences and a few examples.
    """
    only_left, only_right = left - right, right - left
    return {"equal": not only_left and not only_right, "only_in_translation": len(only_left),
            "only_in_other": len(only_right), "examples_only_in_translation": sorted(only_left)[:5],
            "examples_only_in_other": sorted(only_right)[:5]}


def timed(function: Callable[[], Any]) -> Tuple[float, Any]:
    """
    :return: The wall time of the call in milliseconds and its result.
    """
    start = time.perf_counter()
    result = function()
    return (time.perf_counter() - start) * 1000, result


def median_without_first(times: List[float]) -> Optional[float]:
    """
    :return: The median without the first run (warm-up), as the query experiment reports it.
    """
    rest = times[1:] if len(times) > 1 else times
    return statistics.median(rest) if rest else None


def paper_sql_medians(path: Optional[Path]) -> Dict[int, float]:
    """
    :param path: queries_sqlalchemy.json of the paper's query run, or None.
    :return: The median time without the first run of every hand-written SQLAlchemy query.
    """
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {int(k): median_without_first(v["times_ms"]) for k, v in data["queries"].items() if v.get("times_ms")}


def lazy_translation(query: Any, session: Session) -> Any:
    """
    Translate a query and load the relationships of the selected data access objects lazily. The generated interface
    of the current version loads every relationship eagerly (``selectin``), so that loading one answer loads every
    object reachable from it, here the whole benchmark; the interface of the query experiment loads lazily.

    :param query: An EQL query.
    :param session: The session of the database.
    :return: The translator, whose statement loads lazily.
    """
    translator = eql_to_sql(query, session)
    translator.sql_query = translator.sql_query.options(lazyload("*"))
    return translator


def run_query(benchmark: BenchmarkQuery, session: Session, normalizer: AnswerNormalizer, reference: Path,
              repetitions: int) -> Dict[str, Any]:
    """
    Evaluate one query in working memory and through its translation, compare and time the translation.

    :return: The record of the query.
    """
    record: Dict[str, Any] = {"query": benchmark.number, "rewrite": benchmark.rewrite}
    memory_ms, memory_results = timed(lambda: list(benchmark.query.evaluate()))
    memory = {normalizer.row(r, benchmark.selected, False) for r in memory_results}
    del memory_results
    graphdb = read_answer_set(reference_file(reference, benchmark.number))
    record.update({"eql_in_memory_ms_single_run": memory_ms, "eql_answers": len(memory),
                   "graphdb_answers": len(graphdb), "eql_equal_to_graphdb": memory == graphdb})
    try:
        translator = eql_to_sql(benchmark.query, session)
    except Exception as error:
        record.update({"translated": False, "error": f"{type(error).__name__}: {error}",
                       "traceback": traceback.format_exc(limit=4)})
        return record
    record["translated"] = True
    record["sql"] = str(translator.sql_query.compile(session.get_bind(), compile_kwargs={"literal_binds": True}))
    try:
        session.expunge_all()
        first_ms, results = timed(lambda: list(lazy_translation(benchmark.query, session).evaluate()))
        database = {normalizer.row(r, benchmark.selected, True) for r in results}
        record["raw_rows"] = len(results)
        del results
    except Exception as error:
        record.update({"evaluated": False, "error": f"{type(error).__name__}: {error}",
                       "traceback": traceback.format_exc(limit=4)})
        return record
    record.update({"evaluated": True, "translation_answers": len(database),
                   "equal_to_eql": compare(database, memory), "equal_to_graphdb": compare(database, graphdb)})
    evaluate_ms, execute_ms = [first_ms], []
    statement = lazy_translation(benchmark.query, session).sql_query
    for repetition in range(repetitions):
        if repetition > 0:
            session.expunge_all()
            evaluate_ms.append(timed(lambda: list(lazy_translation(benchmark.query, session).evaluate()))[0])
        session.expunge_all()
        execute_ms.append(timed(lambda: session.execute(statement).all())[0])
    session.expunge_all()
    record.update({"evaluate_ms": evaluate_ms, "execute_ms": execute_ms,
                   "evaluate_median_ms": median_without_first(evaluate_ms),
                   "execute_median_ms": median_without_first(execute_ms)})
    return record


def persist(knowledge: Knowledge, engine: Any) -> Dict[str, float]:
    """
    Store all objects with ORMatic.

    :return: The seconds of the conversion to data access objects and of the commit.
    """
    drop_database(engine)
    interface.Base.metadata.create_all(engine)
    session = Session(engine)
    state = ToDataAccessObjectState()
    convert_seconds, daos = timed(lambda: [to_dao(o, state) for o in knowledge.all_objects()])
    session.add_all(daos)
    commit_ms, _ = timed(session.commit)
    session.close()
    return {"to_dao_seconds": convert_seconds / 1000, "commit_seconds": commit_ms / 1000}


def markdown_summary(report: Dict[str, Any]) -> str:
    """
    :return: A short summary table of the report.
    """
    lines = ["# ORMatic's translation of the 18 OWL2Bench queries", "",
             f"Data: {report['data']}", "",
             "| Query | Translated | = EQL | = GraphDB | Answers | Translated SQL [ms] | Hand-written SQL, paper [ms] "
             "| evaluate [ms] |",
             "|---|---|---|---|---|---|---|---|"]
    for r in report["queries"]:
        def mark(key: str) -> str:
            value = r.get(key)
            return "-" if value is None else ("yes" if value["equal"] else "NO")
        number = r["query"]
        fmt = lambda v: "-" if v is None else f"{v:,.2f}"
        lines.append(f"| Q{number} | {'yes' if r.get('translated') else 'NO'} | {mark('equal_to_eql')} "
                     f"| {mark('equal_to_graphdb')} | {r.get('translation_answers', '-')} "
                     f"| {fmt(r.get('execute_median_ms'))} "
                     f"| {fmt(report['paper_sqlalchemy_median_ms'].get(str(number)))} "
                     f"| {fmt(r.get('evaluate_median_ms'))} |")
    lines += ["", f"Translated: {report['summary']['translated']}/18; equal to EQL: {report['summary']['equal_to_eql']}"
              f"/18; equal to GraphDB: {report['summary']['equal_to_graphdb']}/18."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--reasoned-file", required=True)
    parser.add_argument("--reference-answers", required=True, help="GraphDB's answer files of the paper's run")
    parser.add_argument("--database-uri", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--statements-cache", default=None)
    parser.add_argument("--paper-sqlalchemy-times", default=None, help="queries_sqlalchemy.json of the paper's run")
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--queries", default=None, help="comma separated query numbers (default: all 18)")
    arguments = parser.parse_args()
    output = Path(arguments.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    read_ms, (types, statements) = timed(lambda: read_statements(
        Path(arguments.reasoned_file), Path(arguments.statements_cache) if arguments.statements_cache else None))
    print(f"read {len(types)} typed IRIs and {len(statements)} statements in {read_ms / 1000:.1f} s", flush=True)
    build_ms, knowledge = timed(lambda: build_knowledge(types, statements))
    print(f"built {len(knowledge.all_objects())} objects in {build_ms / 1000:.1f} s", flush=True)
    configure_mappers()
    engine = create_engine(arguments.database_uri)
    persist_seconds = persist(knowledge, engine)
    print(f"stored: {persist_seconds}", flush=True)

    session = Session(engine)
    normalizer = AnswerNormalizer(session)
    wanted = None if arguments.queries is None else {int(q) for q in arguments.queries.split(",")}
    records = []
    for benchmark in benchmark_queries(knowledge):
        if wanted is not None and benchmark.number not in wanted:
            continue
        record = run_query(benchmark, session, normalizer, Path(arguments.reference_answers),
                           arguments.repetitions)
        records.append(record)
        print(f"Q{record['query']}: translated={record.get('translated')} "
              f"=EQL={record.get('equal_to_eql', {}).get('equal')} "
              f"=GraphDB={record.get('equal_to_graphdb', {}).get('equal')} "
              f"answers={record.get('translation_answers')} eql={record['eql_answers']} "
              f"graphdb={record['graphdb_answers']} execute={record.get('execute_median_ms')} "
              f"error={record.get('error', '')[:200]}", flush=True)

    report = {
        "data": "the OWL 2 RL closure of OWL2Bench (one university) computed by GraphDB, the pre-reasoned input of "
                "the experiments, restricted to the classes and properties of owl2bench_translation_model.py and "
                f"stored by ORMatic in {engine.dialect.name}",
        "reasoned_file": str(arguments.reasoned_file),
        "database": engine.dialect.name,
        "typed_iris": len(types), "statements_of_model_properties": len(statements),
        "objects": len(knowledge.all_objects()), "knowledge_statistics": knowledge.statistics,
        "read_seconds": read_ms / 1000, "build_seconds": build_ms / 1000, "persist": persist_seconds,
        "repetitions": arguments.repetitions,
        "timing": "relationships loaded lazily (lazyload('*')), as in the interface of the query experiment; "
                  "execute: session.execute(translated statement).all() after expunge_all, as the hand-written "
                  "SQLAlchemy queries are measured; evaluate: eql_to_sql(query).evaluate() including translation; "
                  "medians without the first run",
        "paper_sqlalchemy_median_ms": {str(k): v for k, v in paper_sql_medians(
            Path(arguments.paper_sqlalchemy_times) if arguments.paper_sqlalchemy_times else None).items()},
        "environment": {"python": platform.python_version(), "machine": platform.machine(),
                        "cpus_available": len(os.sched_getaffinity(0))},
        "queries": records,
    }
    report["summary"] = {
        "translated": sum(1 for r in records if r.get("translated")),
        "equal_to_eql": sum(1 for r in records if r.get("equal_to_eql", {}).get("equal")),
        "equal_to_graphdb": sum(1 for r in records if r.get("equal_to_graphdb", {}).get("equal")),
        "eql_equal_to_graphdb": sum(1 for r in records if r.get("eql_equal_to_graphdb")),
    }
    (output / "ormatic_translation.json").write_text(json.dumps(report, indent=1, default=str))
    (output / "summary.md").write_text(markdown_summary(report))
    print(json.dumps(report["summary"]), flush=True)


if __name__ == "__main__":
    main()
