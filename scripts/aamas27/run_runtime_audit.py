"""
Runtime closure audit of the agent loop (:mod:`krrood_experiments.aamas27.runtime_audit`) for several seeds: every seed
runs in a fresh process, which runs the KRROOD variant's loop on the seed's scenario (the scenario of
``run_agent_loop.py --seed S --steps N --events-per-step E``) and compares the knowledge base with the OWL 2 RL closure
computed by Nemo at the checkpoints.

Results in ``--results-dir``: ``seed<S>.json`` (full report of a seed), ``runtime_audit.json`` (summary: per seed and
checkpoint the fact counts and the missing/extra facts per kind and per class or property) and ``provenance.txt``.

Example::

    python scripts/aamas27/run_runtime_audit.py --seeds 0,1,2,3,4 --results-dir results/aamas27/runtime_audit-20261007
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from krrood_experiments.aamas27.environment import EXPERIMENTS_ROOT, RESULTS_ROOT, write_json
from krrood_experiments.aamas27.runtime_audit import DEFAULT_CHECKPOINTS

TIMING_RUN_SCENARIO = "agent_loop-20261008-seed{seed}-200steps/scenario.json"
"""
Scenario file of the agent-loop timing run of a seed (under ``results/aamas27``), compared when it exists.
"""


def summarise(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    :param report: The report of a seed.
    :return: Per checkpoint: fact counts, and per kind the counts and the missing/extra facts per name.
    """
    rows = []
    for checkpoint in report["results"]:
        rows.append({
            "steps": checkpoint["steps"],
            "events": checkpoint["events"],
            "event_kinds": checkpoint["event_kinds"],
            "individuals": checkpoint["individuals"],
            "new_people": checkpoint["new_people"],
            "facts": checkpoint["facts"],
            "kinds": {
                kind: {key: value for key, value in entry.items() if not key.endswith("_examples")}
                for kind, entry in checkpoint["kinds"].items()
            },
            "missing_class_justifications": checkpoint["missing_class_justifications"],
            "on_demand_class_answers": {
                name: {key: value for key, value in entry.items() if not key.endswith("_examples")}
                for name, entry in checkpoint["on_demand_class_answers"].items()
            },
            "audit_seconds": checkpoint["seconds"]["total"],
        })
    return rows


def read_text(path: str) -> str:
    """
    :return: The stripped content of a file, or ``unavailable``.
    """
    try:
        return Path(path).read_text().strip()
    except OSError:
        return "unavailable"


def git(*arguments: str) -> str:
    """
    :return: The output of a git command in the repository, or the error.
    """
    completed = subprocess.run(["git", "-C", str(EXPERIMENTS_ROOT), *arguments], capture_output=True, text=True)
    return completed.stdout.strip() if completed.returncode == 0 else f"git failed: {completed.stderr.strip()}"


def cpu_model() -> str:
    """
    :return: The CPU model name.
    """
    for line in read_text("/proc/cpuinfo").splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def provenance(arguments: argparse.Namespace, started: datetime.datetime, seconds: float,
               seeds: Dict[str, Any]) -> str:
    """
    :return: The text of ``provenance.txt``.
    """
    memory_total = next((line.split(":", 1)[1].strip() for line in read_text("/proc/meminfo").splitlines()
                         if line.startswith("MemTotal")), "unknown")
    lines = [
        "Runtime closure audit of the KRROOD agent loop (scripts/aamas27/run_runtime_audit.py)",
        f"date (UTC): started {started.isoformat(timespec='seconds')}, "
        f"finished {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
        f"wall time: {seconds:.0f} s",
        f"machine: {arguments.machine or socket.gethostname()}; CPU {cpu_model()}, {os.cpu_count()} logical CPUs, "
        f"MemTotal {memory_total}; {platform.platform()}",
        f"container: {arguments.container or 'unknown'}; cgroup cpuset {read_text('/sys/fs/cgroup/cpuset.cpus.effective')}, "
        f"cgroup memory.max {read_text('/sys/fs/cgroup/memory.max')} bytes",
        f"python: {sys.executable} {platform.python_version()}",
        f"commit: {git('rev-parse', 'HEAD')} (branch {git('rev-parse', '--abbrev-ref', 'HEAD')})",
        "working tree: the audit's own files (src/krrood_experiments/aamas27/runtime_audit.py, "
        "scripts/aamas27/run_runtime_audit.py, tests/aamas27/test_runtime_audit.py) were not committed yet; "
        "git status --porcelain:",
        *("    " + line for line in git("status", "--porcelain").splitlines()),
        f"nemo: {seeds and next(iter(seeds.values())).get('nemo_version', 'unknown')}",
        f"arguments: {json.dumps(vars(arguments))}",
        f"concurrency: {arguments.note}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--events-per-step", type=int, default=3)
    parser.add_argument("--checkpoints", default=",".join(map(str, DEFAULT_CHECKPOINTS)))
    parser.add_argument("--results-dir", default=None,
                        help="default: results/aamas27/runtime_audit-<date>")
    parser.add_argument("--work-dir", default=None, help="scratch directory for the Nemo files (default: results dir)")
    parser.add_argument("--nemo-binary", default=os.environ.get("NEMO_BINARY", "nmo"))
    parser.add_argument("--machine", default=None, help="name of the host machine, for provenance.txt")
    parser.add_argument("--container", default=None, help="container name, image and limits, for provenance.txt")
    parser.add_argument("--note", default="other experiments ran on the machine at the same time",
                        help="concurrency note for provenance.txt")
    arguments = parser.parse_args()

    started = datetime.datetime.now(datetime.timezone.utc)
    start = time.perf_counter()
    results_directory = Path(arguments.results_dir or RESULTS_ROOT / f"runtime_audit-{started:%Y%m%d}")
    results_directory.mkdir(parents=True, exist_ok=True)
    work_directory = Path(arguments.work_dir) if arguments.work_dir else results_directory / "work"
    summary: Dict[str, Any] = {"experiment": "runtime_audit", "arguments": vars(arguments), "seeds": {}}
    for seed in [int(s) for s in arguments.seeds.split(",") if s != ""]:
        output = results_directory / f"seed{seed}.json"
        command = [
            sys.executable, "-m", "krrood_experiments.aamas27.runtime_audit", "--seed", str(seed),
            "--steps", str(arguments.steps), "--events-per-step", str(arguments.events_per_step),
            "--checkpoints", arguments.checkpoints, "--nemo-binary", arguments.nemo_binary,
            "--work-dir", str(work_directory / f"seed{seed}"), "--output", str(output),
        ]
        print(f"seed {seed} ...", flush=True)
        seed_start = time.perf_counter()
        completed = subprocess.run(command, env=dict(os.environ, TQDM_DISABLE="1"), stderr=subprocess.PIPE,
                                   text=True)
        audit_lines = [line for line in completed.stderr.splitlines() if line.startswith("[audit]")]
        print("\n".join(audit_lines), flush=True)
        if completed.returncode != 0 or not output.exists():
            print(completed.stderr[-5000:], file=sys.stderr)
            raise RuntimeError(f"seed {seed} failed with return code {completed.returncode}")
        report = json.loads(output.read_text())
        timing_scenario = RESULTS_ROOT / TIMING_RUN_SCENARIO.format(seed=seed)
        timing_digest = (hashlib.sha256(timing_scenario.read_bytes()).hexdigest()
                         if timing_scenario.exists() else None)
        summary["seeds"][str(seed)] = {
            "scenario_sha256": report["scenario_sha256"],
            "timing_run_scenario": str(timing_scenario.relative_to(EXPERIMENTS_ROOT)),
            "same_scenario_as_timing_run": None if timing_digest is None else timing_digest == report["scenario_sha256"],
            "raw_input_serialisation_check": report.get("raw_input_serialisation_check"),
            "nemo_version": report["results"][0]["nemo"]["nemo_version"] if report["results"] else None,
            "loop": report["loop"],
            "wall_seconds": time.perf_counter() - seed_start,
            "checkpoints": summarise(report),
        }
        write_json(results_directory / "runtime_audit.json", summary)
    seconds = time.perf_counter() - start
    summary["wall_seconds"] = seconds
    write_json(results_directory / "runtime_audit.json", summary)
    (results_directory / "provenance.txt").write_text(provenance(arguments, started, seconds, summary["seeds"]))
    if not arguments.work_dir:
        for path in sorted(work_directory.rglob("*"), reverse=True):
            path.unlink() if path.is_file() else path.rmdir()
        work_directory.rmdir()
    print(f"results written to {results_directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
