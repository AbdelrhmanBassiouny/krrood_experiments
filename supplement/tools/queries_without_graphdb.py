"""
The query experiment without a GraphDB server: runs the given frameworks as run_queries.py does (each in a fresh,
measured worker process) and compares their answer sets with the answer sets of GraphDB that the paper's run
recorded (results/check/answers/graphdb of the bundle), instead of with those of a live GraphDB.

Writes queries_<framework>.json, answers/, queries.json (the format of run_queries.py, so that make_tables.py reads
it) and answer_check.json into the results folder. Exits with 1 if an answer set differs.

Usage (from code/earlier/experiments, with the earlier venv):
    python queries_without_graphdb.py --reference-answers DIR --results-dir DIR [--frameworks eql,sqlalchemy]
        [--repetitions 1]
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

from krrood_experiments.aamas27.answer_check import check_answers
from krrood_experiments.aamas27.environment import INPUT_FILES, write_json
from krrood_experiments.aamas27.memory import run_measured
from krrood_experiments.aamas27.query_worker import RL_QUERIES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reference-answers", required=True, help="folder with GraphDB's q<N>.tsv.gz")
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--frameworks", default="eql,sqlalchemy")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=float, default=6 * 3600)
    arguments = parser.parse_args()

    results = Path(arguments.results_dir)
    shutil.rmtree(results, ignore_errors=True)
    answers = results / "answers"
    shutil.copytree(arguments.reference_answers, answers / "graphdb")
    frameworks = [f for f in arguments.frameworks.split(",") if f]
    queries = list(RL_QUERIES)
    summary = {"experiment": "queries", "arguments": vars(arguments),
               "graphdb_reference": {"answers_of_the_paper_run": str(arguments.reference_answers)},
               "frameworks": {}}
    for framework in frameworks:
        output = results / f"queries_{framework}.json"
        command = [sys.executable, "-m", "krrood_experiments.aamas27.query_worker", "--framework", framework,
                   "--queries", ",".join(map(str, queries)), "--repetitions", str(arguments.repetitions),
                   "--answers-dir", str(answers), "--output", str(output),
                   "--raw-file", str(INPUT_FILES["raw"]), "--reasoned-file", str(INPUT_FILES["reasoned"])]
        print(f"[{time.strftime('%H:%M:%S')}] running {framework}", flush=True)
        run = run_measured(command, timeout_seconds=arguments.timeout_seconds, memory_limit_bytes=None,
                           environment=dict(os.environ)).to_json()
        run["status"] = ("timeout" if run["timed_out"] else "memory_limit" if run["memory_limit_exceeded"] else
                         "ok" if run["return_code"] == 0 else "failed")
        if output.exists():
            run["result"] = json.loads(output.read_text())
        summary["frameworks"][framework] = run
        write_json(results / "queries.json", summary)
        print(f"    {framework}: status={run['status']} wall={run['wall_seconds']:.1f}s", flush=True)
        if run["status"] != "ok":
            print(run["stderr_tail"][-3000:])
    report = check_answers(answers, queries, ["graphdb", *frameworks])
    report["reference_source"] = "answer sets of GraphDB recorded in the paper's run"
    write_json(results / "answer_check.json", report)
    shutil.rmtree(answers / "graphdb")
    print("answer sets equal to GraphDB's:", report["all_equal"])
    return 0 if report["all_equal"] and all(r["status"] == "ok" for r in summary["frameworks"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
