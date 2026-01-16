from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass
from os.path import dirname
from pathlib import Path
from typing import List, Any, Tuple

from krrood.entity_query_language.symbolic import An, UnificationDict
from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import Graph
from sqlalchemy.sql.operators import contains
from typing_extensions import Dict

from .owl_instances_loader import (
    OwlLoader,
    OwlInstancesRegistry,
)
from .owl_to_python import OwlToPythonConverter


def generate_lubm_with_predicates(clean: bool = False):
    # Provide default overrides for common LUBM datatype properties
    _default_overrides = {
        "Person": {
            "age": "int",
            "telephone": "str",
            "title": "str",
            "email_address": "str",
        },
        "Professor": {
            "tenured": "bool",
        },
        "Publication": {
            "publication_date": "str",
        },
        "Software": {
            "software_version": "str",
        },
        "Thing": {
            "name": "str",
            "office_number": "int",
            "research_interest": "str",
        },
    }
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    resources_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "lubm", "resources"
    )
    file_name = f"lubm_clean.owl" if clean else "lubm.owl"
    converter.load_ontology(os.path.join(resources_path, file_name))
    # Save into the package module so tests import the updated code
    output_path = os.path.join(
        os.path.dirname(__file__), "lubm/lubm_with_predicates.py"
    )
    converter.save_to_file(output_path)


def generate_owl2bench_with_predicates(clean: bool = False, save_to_file: bool = True):
    # Provide default overrides for common LUBM datatype properties
    _default_overrides = {
        "Person": {
            "age": "int",
            "telephone": "str",
            "title": "str",
            "email_address": "str",
        },
        "Professor": {
            "tenured": "bool",
        },
        "Publication": {
            "publication_date": "str",
        },
        "Software": {
            "software_version": "str",
        },
        "Thing": {
            "name": "str",
            "office_number": "int",
            "research_interest": "str",
        },
    }
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    resources_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "owl2bench",
        "resources",
        "refactored_ontologies",
    )
    # base_name = "OWL2RL-1"
    base_name = "owl2benchRlFixed"
    suffix = ".owl"
    suffix_reasoned = ".rdf"
    file_name = f"{base_name}_clean.owl" if clean else f"{base_name}.owl"
    converter.load_ontology(os.path.join(resources_path, file_name))
    if save_to_file:
        # Save into the package module so tests import the updated code
        output_path = os.path.join(
            os.path.dirname(__file__), "owl2bench/owl2bench_with_predicates.py"
        )
        converter.save_to_file(output_path)
    return


def make_rdf_graph(instances_path: str):
    g = Graph()
    g.parse(instances_path)
    return g


def evaluate_sparql(rdf_graph: Graph, sparql_queries: List[str]):
    DeductiveClosure(OWLRL_Semantics, rdfs_closure=True, axiomatic_triples=True).expand(
        rdf_graph
    )
    counts: List[int] = []
    for q in sparql_queries:
        res = rdf_graph.query(q)
        counts.append(len(res))
    return counts


def evaluate_eql(
    eql_queries: List[QueryWithSelectables],
) -> Tuple[List[int], Dict[int, List[Any]], List[float]]:
    """Load instances and evaluate 14 EQL queries, returning counts per query."""
    counts: List[int] = []
    results: Dict[int, List[Any]] = {}
    times: List[float] = []
    for i, q in enumerate(eql_queries):
        start_time = time.time()
        result = list(q.evaluate())
        times.append(time.time() - start_time)
        counts.append(len(result))
        results[q.id_] = result
    return counts, results, times


def load_instances_for_lubm_with_predicates() -> OwlInstancesRegistry:
    """Load instances from the given path and add them to the given model module."""
    from ...lubm import (
        lubm_with_predicates,
        lubm_with_predicates_properties,
        lubm_with_predicates_base,
    )

    folder_path = Path(
        f"{dirname(__file__)}",
        "..",
        "..",
        "..",
        "..",
        "lubm",
        "resources",
        "instances",
    )
    files = [f.name for f in folder_path.iterdir() if f.is_file()]
    files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    registry = OwlLoader.load_multi_file_instances(
        [os.path.join(folder_path, file) for file in files],
        base_module=lubm_with_predicates_base,
        classes_module=lubm_with_predicates,
        properties_module=lubm_with_predicates_properties,
    )
    return registry


def load_instances_for_owl2bench_with_predicates(
    file_name: str,
) -> OwlInstancesRegistry:
    """Load instances from the given path and add them to the given model module."""

    from . import (
        owl2bench_with_predicates,
    )
    from . import owl2bench_with_predicates_properties
    from . import owl2bench_with_predicates_base

    registry = OwlLoader.load_multi_file_instances(
        [file_name],
        base_module=owl2bench_with_predicates_base,
        classes_module=owl2bench_with_predicates,
        properties_module=owl2bench_with_predicates_properties,
    )
    return registry


def get_lubm_answers():
    queries_answers = defaultdict(list)
    answers_path = os.path.join(
        os.path.dirname(__file__),
        "",
        "..",
        "..",
        "lubm",
        "resources",
        "query_answers",
    )
    for i in range(1, 15):
        first_line = True
        with open(os.path.join(answers_path, f"answers_query{i}.txt")) as f:
            for line in f:
                if first_line:
                    first_line = False
                    var_names = line.strip().split()
                else:
                    var_values = line.strip().split()
                    assert len(var_names) == len(var_values)
                    queries_answers[i].append(dict(zip(var_names, var_values)))
    return queries_answers


@dataclass
class QueryWithSelectables:
    """
    This class is for being able to compare LUBM query answers with eql query answers.
    """

    query: An
    """
    The query to evaluate.
    """
    selectables: dict
    """
    A dictionary mapping variable names to selectables.
    """
    id_: int = 0
    """
    The query id.
    """

    def evaluate(self):
        for value in self.query.evaluate():
            if isinstance(value, UnificationDict):
                yield {k: value[v] for k, v in self.selectables.items()}
            else:
                yield {k: value for k, v in self.selectables.items()}
