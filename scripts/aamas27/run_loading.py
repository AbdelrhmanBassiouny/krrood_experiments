"""
Experiment (a)+(b): loading + reasoning time and peak memory per system, for the raw and the reasoned OWL2Bench data.

Every measurement of a Python-based system runs in a fresh interpreter; the peak RSS of its whole process tree
(including the Java process that owlready2 starts for Pellet) is sampled every 50 ms. GraphDB runs as a separate
server: for every repetition a fresh managed repository with the requested ruleset is created, the file is uploaded
in one request, and the RSS of the server JVM is sampled during the upload.

Results are appended to ``<results-dir>/loading.json`` after every single measurement.

Example (original machine)::

    python scripts/aamas27/run_loading.py --repetitions 5 --rdflib-timeout-seconds 10800
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from krrood_experiments.aamas27.environment import (
    INPUT_FILES,
    resolve_results_directory,
    write_json,
)
from krrood_experiments.aamas27.graphdb import GraphDBClient, RULESETS
from krrood_experiments.aamas27.memory import measure_server_during, run_measured

ALL_SYSTEMS = [
    "krrood",
    "owlready2_pellet",
    "rdflib_owlrl",
    "graphdb",
    "krrood_ormatic",
]
"""
Systems of the main loading experiment, in execution order. The ablation system
``krrood_eager_symmetric_transitive`` is run by ``run_symmetric_transitive_ablation.py``.
"""


def status_of(run: Dict[str, Any]) -> str:
    """
    :param run: A measured run.
    :return: ``ok``, ``timeout``, ``memory_limit`` or ``failed``.
    """
    if run.get("timed_out"):
        return "timeout"
    if run.get("memory_limit_exceeded"):
        return "memory_limit"
    if run.get("return_code") != 0 or run.get("worker_result") is None:
        return "failed"
    return "ok"


def measure_worker(
    system: str,
    input_file: Path,
    timeout_seconds: float,
    memory_limit_gib: float | None,
    java_memory_mb: int,
) -> Dict[str, Any]:
    """
    Run one measurement of a Python-based system in a fresh interpreter.
    """
    command = [
        sys.executable,
        "-m",
        "krrood_experiments.aamas27.loading_worker",
        "--system",
        system,
        "--input-file",
        str(input_file),
        "--java-memory-mb",
        str(java_memory_mb),
    ]
    run = run_measured(
        command,
        timeout_seconds=timeout_seconds,
        memory_limit_bytes=int(memory_limit_gib * 2**30) if memory_limit_gib else None,
        environment=dict(os.environ),
    ).to_json()
    run["status"] = status_of(run)
    run["timeout_seconds"] = timeout_seconds
    return run


def measure_graphdb(
    client: GraphDBClient, input_name: str, input_file: Path, ruleset: str
) -> Dict[str, Any]:
    """
    Load a file into a fresh managed GraphDB repository and observe the server memory.
    """
    repository_id = f"aamas27_load_{input_name}_{ruleset.replace('-', '_')}"
    if repository_id in client.repository_ids():
        client.delete_repository(repository_id)
    client.create_repository(repository_id, ruleset)
    server = client.server_process()
    if server is None:
        raise RuntimeError(
            "The GraphDB server process was not found on this machine; memory cannot be measured."
        )
    measurement, upload_seconds = measure_server_during(
        server, lambda: client.load_file(repository_id, input_file)
    )
    counts = client.count_statements(repository_id)
    configured_ruleset = client.ruleset(repository_id)
    client.delete_repository(repository_id)
    run = measurement.to_json()
    run.update(
        {
            "status": "ok",
            "repository": repository_id,
            "ruleset": configured_ruleset,
            "ruleset_label": RULESETS.get(configured_ruleset),
            "worker_result": {
                "load_and_reasoning_seconds": upload_seconds,
                "statements": counts,
            },
            "server_pid": server.pid,
            "server_java_options": client.server_java_options(),
        }
    )
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--systems", default=",".join(ALL_SYSTEMS),
                        help=f"comma separated subset of {ALL_SYSTEMS} (default: all)")
    parser.add_argument("--inputs", default="raw,reasoned", help="comma separated subset of raw,reasoned")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=3 * 3600,
                        help="wall-clock cap per measurement of every worker-based system (default 3 h)")
    parser.add_argument("--rdflib-timeout-seconds", type=float, default=None,
                        help="separate cap for RDFLib+owlrl (default: --timeout-seconds); after a timeout, further "
                             "repetitions of the same system and input are skipped")
    parser.add_argument("--memory-limit-gib", type=float, default=None,
                        help="kill a worker when its process tree exceeds this RSS (default: no limit)")
    parser.add_argument("--java-memory-mb", type=int, default=2000,
                        help="Java heap for Pellet via owlready2 (owlready2 default 2000, as in January 2026)")
    parser.add_argument("--graphdb-ruleset", default="owl2-rl-optimized", choices=sorted(RULESETS))
    parser.add_argument("--graphdb-url", default=None)
    parser.add_argument("--raw-file", default=str(INPUT_FILES["raw"]))
    parser.add_argument("--reasoned-file", default=str(INPUT_FILES["reasoned"]))
    parser.add_argument("--results-dir", default=None, help="existing results directory to append to")
    arguments = parser.parse_args()

    results_directory = resolve_results_directory(arguments.results_dir, "loading")
    output = results_directory / "loading.json"
    files = {"raw": Path(arguments.raw_file), "reasoned": Path(arguments.reasoned_file)}
    systems = [s for s in arguments.systems.split(",") if s]
    inputs = [i for i in arguments.inputs.split(",") if i]
    client = GraphDBClient(arguments.graphdb_url) if arguments.graphdb_url else GraphDBClient()

    record: Dict[str, Any] = {
        "experiment": "loading_and_reasoning",
        "arguments": vars(arguments),
        "input_files": {name: str(path) for name, path in files.items()},
        "runs": [],
    }
    if output.exists():
        import json

        record["runs"] = json.loads(output.read_text())["runs"]

    for system in systems:
        for input_name in inputs:
            input_file = files[input_name]
            for repetition in range(arguments.repetitions):
                print(f"[{time.strftime('%H:%M:%S')}] {system} / {input_name} / repetition {repetition + 1}",
                      flush=True)
                if system == "graphdb":
                    run = measure_graphdb(client, input_name, input_file, arguments.graphdb_ruleset)
                else:
                    timeout = arguments.timeout_seconds
                    if system == "rdflib_owlrl" and arguments.rdflib_timeout_seconds:
                        timeout = arguments.rdflib_timeout_seconds
                    run = measure_worker(system, input_file, timeout, arguments.memory_limit_gib,
                                         arguments.java_memory_mb)
                run.update({"system": system, "input": input_name, "repetition": repetition})
                record["runs"].append(run)
                write_json(output, record)
                summary = run.get("worker_result") or {}
                print(f"    status={run['status']} wall={run.get('wall_seconds', 0):.1f}s "
                      f"load+reasoning={summary.get('load_and_reasoning_seconds')} "
                      f"peak_rss={run.get('peak_rss_mib', 0):.0f} MiB", flush=True)
                if run["status"] != "ok":
                    print(f"    skipping remaining repetitions of {system}/{input_name} ({run['status']})")
                    if run.get("stderr_tail"):
                        print(run["stderr_tail"][-2000:])
                    break
    print(f"results written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
