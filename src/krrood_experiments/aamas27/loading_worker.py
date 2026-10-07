"""
Worker process for one loading + reasoning measurement. It is started in a fresh interpreter by
``scripts/aamas27/run_loading.py`` so that every measurement starts from a cold process and its peak memory can be
attributed to a single system.

The worker reports its internal phase timings on stdout through
:func:`krrood_experiments.aamas27.memory.print_worker_result`.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict

from .memory import print_worker_result

SYSTEMS: Dict[str, str] = {
    "krrood": "Ontomatic instance loader (parsing, object creation and reasoning).",
    "krrood_ormatic": "KRROOD loading followed by persisting all objects into PostgreSQL through ORMatic.",
    "krrood_eager_symmetric_transitive": "KRROOD loading without the connected-components post-processing; "
    "symmetric and transitive properties are closed eagerly (ablation).",
    "owlready2_pellet": "owlready2 loading followed by sync_reasoner_pellet(infer_property_values=True).",
    "rdflib_owlrl": "RDFLib parsing followed by owlrl DeductiveClosure(OWLRL_Semantics).expand.",
    "reasonable_owlrl": "RDFLib parsing of the RDF/XML file, then the Rust OWL 2 RL materialiser reasonable "
    "(PyReasoner.from_graph + reason; reasonable itself only parses Turtle/N3).",
    "nemo_owlrl": "The Nemo rule engine (nmo binary, a child process of the worker) importing the RDF/XML file and "
    "materialising the OWL 2 RL/RDF rules of owl2rl.rls.",
}
"""
Systems measured in a worker process. GraphDB is measured on the server side by the driver.
"""


def timed(function: Callable[[], Any]) -> tuple[float, Any]:
    """
    :param function: The function to call.
    :return: The elapsed wall time in seconds and the return value.
    """
    start = time.perf_counter()
    value = function()
    return time.perf_counter() - start, value


def run_krrood(input_file: Path, eager_symmetric_transitive: bool = False) -> Dict[str, Any]:
    """
    Load and reason with the Ontomatic instance loader.

    :param input_file: The OWL2Bench RDF/XML file.
    :param eager_symmetric_transitive: Disable the connected-components post-processing (ablation).
    :return: Phase timings and counts.
    """
    import_seconds, _ = timed(_import_krrood)
    from krrood.ontomatic.property_descriptor.property_descriptor_relation import (
        PropertyDescriptorRelation,
    )
    from krrood_experiments.owl2bench.ontomatic.helpers import (
        load_instances_for_owl2bench_with_predicates,
    )

    PropertyDescriptorRelation.eager_symmetric_transitive_closure = (
        eager_symmetric_transitive
    )
    load_seconds, registry = timed(
        lambda: load_instances_for_owl2bench_with_predicates(str(input_file))
    )
    instances = [i for instances in registry._by_uri.values() for i in instances]
    return {
        "import_seconds": import_seconds,
        "load_and_reasoning_seconds": load_seconds,
        "individuals": len(registry._by_uri),
        "objects": len(instances),
        "eager_symmetric_transitive_closure": eager_symmetric_transitive,
        "_registry": registry,
    }


def _import_krrood() -> None:
    import krrood_experiments.owl2bench.ontomatic.helpers  # noqa: F401
    import krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates  # noqa: F401


def run_krrood_ormatic(input_file: Path) -> Dict[str, Any]:
    """
    Load and reason with KRROOD, then persist every object into PostgreSQL using the ORMatic interface.

    :param input_file: The OWL2Bench RDF/XML file.
    :return: Phase timings and counts.
    """
    result = run_krrood(input_file)
    registry = result.pop("_registry")
    persist_seconds, _ = timed(lambda: persist_registry(registry))
    result["persist_seconds"] = persist_seconds
    result["load_reasoning_and_persist_seconds"] = (
        result["load_and_reasoning_seconds"] + persist_seconds
    )
    return result


def persist_registry(registry) -> None:
    """
    Drop and recreate the ORMatic schema and insert all objects of a registry.

    :param registry: The KRROOD instance registry.
    """
    from krrood.ormatic.dao import to_dao, ToDataAccessObjectState
    from krrood.ormatic.utils import create_engine, drop_database
    from sqlalchemy.orm import sessionmaker
    from krrood_experiments.owl2bench.ontomatic.orm.ormatic_interface import Base

    engine = create_engine(os.environ["KRROOD_EXPERIMENTS_DATABASE_URI"])
    drop_database(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)()
    state = ToDataAccessObjectState()
    for instances in registry._by_uri.values():
        for instance in instances:
            session.add(to_dao(instance, state))
    session.commit()
    session.close()
    engine.dispose()


def run_owlready2_pellet(input_file: Path, java_memory_mb: int) -> Dict[str, Any]:
    """
    Load with owlready2 and reason with Pellet.

    :param input_file: The OWL2Bench RDF/XML file.
    :param java_memory_mb: Maximum Java heap for Pellet (owlready2.reasoning.JAVA_MEMORY).
    :return: Phase timings.
    """
    import_seconds, owlready2 = timed(lambda: __import__("owlready2"))
    import owlready2.reasoning

    owlready2.reasoning.JAVA_MEMORY = java_memory_mb
    world = owlready2.World()
    load_seconds, _ = timed(lambda: world.get_ontology(str(input_file)).load())
    reasoning_seconds, _ = timed(
        lambda: owlready2.sync_reasoner_pellet(world, infer_property_values=True)
    )
    world.close()
    return {
        "import_seconds": import_seconds,
        "load_seconds": load_seconds,
        "reasoning_seconds": reasoning_seconds,
        "load_and_reasoning_seconds": load_seconds + reasoning_seconds,
        "java_memory_mb": java_memory_mb,
    }


def run_rdflib_owlrl(input_file: Path) -> Dict[str, Any]:
    """
    Parse with RDFLib and materialise the OWL 2 RL closure with owlrl.

    :param input_file: The OWL2Bench RDF/XML file.
    :return: Phase timings and triple counts.
    """
    import_seconds, _ = timed(lambda: __import__("owlrl"))
    import rdflib
    from owlrl import DeductiveClosure, OWLRL_Semantics

    graph = rdflib.Graph()
    load_seconds, _ = timed(lambda: graph.parse(str(input_file), format="xml"))
    triples_before = len(graph)
    reasoning_seconds, _ = timed(
        lambda: DeductiveClosure(OWLRL_Semantics).expand(graph)
    )
    return {
        "import_seconds": import_seconds,
        "load_seconds": load_seconds,
        "reasoning_seconds": reasoning_seconds,
        "load_and_reasoning_seconds": load_seconds + reasoning_seconds,
        "triples_before_reasoning": triples_before,
        "triples_after_reasoning": len(graph),
    }


def run_reasonable_owlrl(input_file: Path, closure_output: Path | None = None) -> Dict[str, Any]:
    """
    Parse with RDFLib and materialise the OWL 2 RL closure with reasonable.

    :param input_file: The OWL2Bench RDF/XML file.
    :param closure_output: If given, the closure is written there as N-Triples after the measurement.
    :return: Phase timings and triple counts.
    """
    import_seconds, _ = timed(lambda: (__import__("rdflib"), __import__("reasonable")))
    import rdflib
    import reasonable

    graph = rdflib.Graph()
    parse_seconds, _ = timed(lambda: graph.parse(str(input_file), format="xml"))
    reasoner = reasonable.PyReasoner()
    from_graph_seconds, _ = timed(lambda: reasoner.from_graph(graph))
    reasoning_seconds, triples = timed(reasoner.reason)
    load_seconds = parse_seconds + from_graph_seconds
    if closure_output is not None:
        closure = rdflib.Graph()
        for triple in triples:
            closure.add(triple)
        closure.serialize(str(closure_output), format="nt", encoding="utf-8")
    return {
        "import_seconds": import_seconds,
        "parse_seconds": parse_seconds,
        "from_graph_seconds": from_graph_seconds,
        "load_seconds": load_seconds,
        "reasoning_seconds": reasoning_seconds,
        "load_and_reasoning_seconds": load_seconds + reasoning_seconds,
        "triples_before_reasoning": len(graph),
        "triples_after_reasoning": len(triples),
    }


NEMO_RULES = Path(__file__).with_name("owl2rl.rls")
"""
The OWL 2 RL/RDF rules (W3C OWL 2 Profiles, Section 4.3) in Nemo's rule language.
"""

NEMO_REPORT_LINE = re.compile(r"^\s*(Data import|Reasoning|Data export):\s*([0-9.]+)\s*(ms|s)\s*$")
"""
A phase line of Nemo's ``--report short`` output, for example ``   Reasoning:   1234ms``.
"""


def run_nemo_owlrl(input_file: Path, nemo_binary: str, closure_output: Path | None = None) -> Dict[str, Any]:
    """
    Materialise the OWL 2 RL closure with Nemo. The closure is exported as N-Triples into a temporary directory that
    is deleted afterwards; Nemo reports import, reasoning and export time separately.

    :param input_file: The OWL2Bench file (RDF/XML, read by Nemo's own parser).
    :param nemo_binary: Path of the ``nmo`` executable.
    :param closure_output: If given, the exported closure is copied there.
    :return: Phase timings reported by Nemo and the size of the exported closure.
    """
    with tempfile.TemporaryDirectory(prefix="nemo_owlrl_") as export_directory:
        command = [
            nemo_binary, "--overwrite-results", "--export-dir", export_directory, "--report", "short",
            "--param", f'input="{input_file.resolve()}"', str(NEMO_RULES),
        ]
        wall_seconds, completed = timed(
            lambda: subprocess.run(command, capture_output=True, text=True, check=True)
        )
        phases = {}
        for line in (completed.stdout + completed.stderr).splitlines():
            match = NEMO_REPORT_LINE.match(line)
            if match:
                value = float(match.group(2))
                phases[match.group(1)] = value / 1000 if match.group(3) == "ms" else value
        export = Path(export_directory)
        with open(export / "closure.nt", "rb") as closure:
            closure_triples = sum(1 for _ in closure)
        with open(export / "inconsistent.csv", "rb") as inconsistent:
            inconsistencies = sum(1 for _ in inconsistent)
        if closure_output is not None:
            shutil.copyfile(export / "closure.nt", closure_output)
    return {
        "nemo_version": subprocess.run([nemo_binary, "--version"], capture_output=True, text=True).stdout.strip(),
        "load_seconds": phases["Data import"],
        "reasoning_seconds": phases["Reasoning"],
        "export_seconds": phases["Data export"],
        "load_and_reasoning_seconds": phases["Data import"] + phases["Reasoning"],
        "nemo_process_wall_seconds": wall_seconds,
        "triples_after_reasoning": closure_triples,
        "inconsistency_facts": inconsistencies,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", choices=sorted(SYSTEMS), required=True)
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--java-memory-mb", type=int, default=2000,
                        help="Java heap for Pellet (owlready2 default: 2000)")
    parser.add_argument("--nemo-binary", default=os.environ.get("NEMO_BINARY", "nmo"),
                        help="the Nemo command-line client (default: $NEMO_BINARY or nmo on the PATH)")
    parser.add_argument("--closure-output", default=None,
                        help="reasonable_owlrl and nemo_owlrl: write the materialised closure to this N-Triples file "
                             "(after the measured phases; for closure_comparison.py)")
    arguments = parser.parse_args()
    input_file = Path(arguments.input_file)
    closure_output = Path(arguments.closure_output) if arguments.closure_output else None
    if arguments.system == "krrood":
        result = run_krrood(input_file)
    elif arguments.system == "krrood_eager_symmetric_transitive":
        result = run_krrood(input_file, eager_symmetric_transitive=True)
    elif arguments.system == "krrood_ormatic":
        result = run_krrood_ormatic(input_file)
    elif arguments.system == "owlready2_pellet":
        result = run_owlready2_pellet(input_file, arguments.java_memory_mb)
    elif arguments.system == "reasonable_owlrl":
        result = run_reasonable_owlrl(input_file, closure_output)
    elif arguments.system == "nemo_owlrl":
        result = run_nemo_owlrl(input_file, arguments.nemo_binary, closure_output)
    else:
        result = run_rdflib_owlrl(input_file)
    result.pop("_registry", None)
    result["system"] = arguments.system
    result["input_file"] = str(input_file)
    print_worker_result(result)
    # Skip interpreter tear-down of large object graphs, it is not part of the measurement.
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
