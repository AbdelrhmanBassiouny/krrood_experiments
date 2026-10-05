"""
Experiments (c)+(d): query times of the 18 OWL 2 RL queries of OWL2Bench for GraphDB, EQL, SQLAlchemy, RDFLib and
owlready2, followed by the hard answer-set equality check against GraphDB.

Every framework runs in its own fresh process (its peak memory is recorded as well). Each process executes every
query ``--repetitions`` times and writes its timings to ``queries_<framework>.json`` and its normalised answer sets
to ``answers/<framework>/q<N>.tsv.gz``. Afterwards every framework's answer set of every query is compared with the
GraphDB answer set; the report is written to ``answer_check.json``. The script exits with status 1 if any answer set
differs, unless ``--allow-mismatch`` is given.

Data used per framework:

* GraphDB: repository ``aamas27_rl`` (raw data, OWL2-RL (Optimized) ruleset) -- the reference.
* EQL and SQLAlchemy: KRROOD objects loaded from the raw data (and persisted to PostgreSQL for SQLAlchemy).
* RDFLib and owlready2: the reasoned data file (they do not reason at query time).

Example::

    python scripts/aamas27/run_queries.py --repetitions 10
    python scripts/aamas27/run_queries.py --check-only --frameworks graphdb,eql,sqlalchemy
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

from krrood_experiments.aamas27.answer_check import check_answers
from krrood_experiments.aamas27.environment import (
    INPUT_FILES,
    resolve_results_directory,
    write_json,
)
from krrood_experiments.aamas27.graphdb import GraphDBClient
from krrood_experiments.aamas27.memory import run_measured
from krrood_experiments.aamas27.query_worker import FRAMEWORKS, RL_QUERIES

KNOWN_DIFFERENCES = {}
"""
Differences that are expected and explained in the paper, by query number. Since the type-inference fixes of krrood
aamas27-experiments, all 18 queries have equal answer sets in every framework (Q12 included), so none is expected.
They would still be reported and make the check fail unless ``--allow-mismatch`` is given.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--frameworks", default=",".join(FRAMEWORKS))
    parser.add_argument("--queries", default=",".join(map(str, RL_QUERIES)))
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--check-only", action="store_true",
                        help="one repetition per query, only to collect the answer sets")
    parser.add_argument("--allow-mismatch", action="store_true",
                        help="exit with status 0 even if answer sets differ")
    parser.add_argument("--graphdb-url", default=None)
    parser.add_argument("--graphdb-repository", default="aamas27_rl")
    parser.add_argument("--raw-file", default=str(INPUT_FILES["raw"]))
    parser.add_argument("--reasoned-file", default=str(INPUT_FILES["reasoned"]))
    parser.add_argument("--owlready2-keep-world", action="store_true",
                        help="do not reload the owlready2 world before every repetition (January: reload)")
    parser.add_argument("--memory-limit-gib", type=float, default=None,
                        help="kill a framework process whose RSS exceeds this value (default: no limit)")
    parser.add_argument("--timeout-seconds", type=float, default=6 * 3600)
    parser.add_argument("--results-dir", default=None)
    arguments = parser.parse_args()

    results_directory = resolve_results_directory(arguments.results_dir, "queries")
    answers_directory = results_directory / "answers"
    frameworks = [f for f in arguments.frameworks.split(",") if f]
    queries = [int(q) for q in arguments.queries.split(",") if q]
    repetitions = 1 if arguments.check_only else arguments.repetitions
    client = GraphDBClient(arguments.graphdb_url) if arguments.graphdb_url else GraphDBClient()
    ruleset = client.ruleset(arguments.graphdb_repository)
    statements = client.count_statements(arguments.graphdb_repository)
    if statements["explicit"] == 0:
        raise SystemExit(f"GraphDB repository {arguments.graphdb_repository} is empty, run graphdb_setup.py first")

    summary: Dict[str, Any] = {
        "experiment": "queries",
        "arguments": vars(arguments),
        "graphdb_reference": {"repository": arguments.graphdb_repository, "ruleset": ruleset,
                              "statements": statements},
        "frameworks": {},
    }
    if "graphdb" in frameworks:
        frameworks.remove("graphdb")
    frameworks.insert(0, "graphdb")  # the reference must always be collected
    for framework in frameworks:
        output = results_directory / f"queries_{framework}.json"
        command = [
            sys.executable, "-m", "krrood_experiments.aamas27.query_worker",
            "--framework", framework,
            "--queries", ",".join(map(str, queries)),
            "--repetitions", str(repetitions),
            "--answers-dir", str(answers_directory),
            "--output", str(output),
            "--graphdb-endpoint", client.endpoint(arguments.graphdb_repository),
            "--raw-file", arguments.raw_file,
            "--reasoned-file", arguments.reasoned_file,
        ]
        if arguments.owlready2_keep_world:
            command.append("--owlready2-keep-world")
        print(f"[{time.strftime('%H:%M:%S')}] running {framework}", flush=True)
        run = run_measured(
            command,
            timeout_seconds=arguments.timeout_seconds,
            memory_limit_bytes=int(arguments.memory_limit_gib * 2**30) if arguments.memory_limit_gib else None,
            environment=dict(os.environ),
        ).to_json()
        run["status"] = (
            "timeout" if run["timed_out"] else
            "memory_limit" if run["memory_limit_exceeded"] else
            "ok" if run["return_code"] == 0 else "failed"
        )
        if output.exists():
            run["result"] = json.loads(output.read_text())
        summary["frameworks"][framework] = run
        write_json(results_directory / "queries.json", summary)
        print(f"    {framework}: status={run['status']} wall={run['wall_seconds']:.1f}s "
              f"peak_rss={run['peak_rss_mib']:.0f} MiB", flush=True)
        if run["status"] != "ok":
            print(run["stderr_tail"][-3000:])

    report = check_answers(answers_directory, queries, frameworks)
    report["known_differences"] = {str(k): v for k, v in KNOWN_DIFFERENCES.items()}
    write_json(results_directory / "answer_check.json", report)
    print("\nAnswer-set check against GraphDB (reference):")
    for number in queries:
        cells = []
        for framework, comparison in report["queries"][str(number)].items():
            if comparison.get("missing_answer_file"):
                cells.append(f"{framework}=n/a")
            elif comparison["equal"]:
                cells.append(f"{framework}=OK({comparison['candidate']})")
            else:
                cells.append(f"{framework}=DIFF(ref {comparison['reference']}, got {comparison['candidate']}, "
                             f"-{comparison['only_in_reference']}/+{comparison['only_in_candidate']})")
        print(f"  Q{number}: " + "  ".join(cells))
    print(f"results in {results_directory}")
    if not report["all_equal"]:
        print(f"ANSWER SETS DIFFER for {len(report['mismatches'])} (query, framework) pairs: "
              f"{report['mismatches']}", file=sys.stderr)
        if not arguments.allow_mismatch:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
