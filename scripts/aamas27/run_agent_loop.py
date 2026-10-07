"""
Agent-loop experiment: a delivery robot on the OWL2Bench campus runs ``--steps`` perceive -> decide -> act steps, with
its knowledge kept and queried by each variant in turn:

* ``krrood``: KRROOD objects are the knowledge base; EQL queries call the robot's predicate and function directly.
* ``krrood_navigation``: the same, but the handout query starts from the requested college object (its
  ``has_student`` values) instead of scanning all students.
* ``graphdb``: Python objects + GraphDB 11.2 (owl2-rl-optimized); facts mirrored with SPARQL updates, SPARQL returns
  candidate IRIs, mapped back, the procedures run in Python on the candidates.
* ``graphdb_push``: GraphDB, with the procedure results written into the store every step so that one SPARQL query
  decides.
* ``reasonable``: Python objects + reasonable 0.4.4 (in-memory OWL 2 RL), ``reason()`` after every step's additions.

The scenario (campus map, course rooms, mail boxes, robot, perceptions) is generated once from ``--seed`` and is
identical for every variant. Every variant runs in its own process (peak memory recorded). The first variant is the
reference: the others carry out its actions, so they see the same states, and their own decisions and candidate sets
are compared with the reference's step by step.

Results in ``--results-dir``: ``scenario.json``, ``agent_loop_<variant>.json`` (per-step records),
``agent_loop_<variant>_candidates.json.gz`` (candidate rows per step) and ``agent_loop.json`` (summary: setup cost,
per-step distributions, synchronisation work, lines of synchronisation/mapping code, query texts, agreement).

Example::

    python scripts/aamas27/run_agent_loop.py --steps 200 --seed 0 --results-dir results/aamas27/agent_loop
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from krrood_experiments.aamas27.agent_loop.graphdb_variant import REPOSITORY
from krrood_experiments.aamas27.agent_loop.measurement import PHASES, distribution
from krrood_experiments.aamas27.agent_loop.scenario import generate_scenario
from krrood_experiments.aamas27.agent_loop.worker import GRAPHDB_VARIANTS, VARIANTS
from krrood_experiments.aamas27.environment import UNREASONED_FILE, resolve_results_directory, write_json
from krrood_experiments.aamas27.graphdb import GraphDBClient
from krrood_experiments.aamas27.memory import run_measured

DEFAULT_VARIANTS = ("krrood", "krrood_navigation", "graphdb", "graphdb_push", "reasonable")
"""
The variants in run order; the first is the reference.
"""

KNOWN_DISAGREEMENT_CAUSES = {
    "reasonable": "reasonable 0.4.4 does not implement the OWL 2 RL property-chain rule prp-spo2, so it does not infer "
    "isMemberOf of a college (enrollIn o isPartOf): its handout candidates are empty or incomplete.",
}
"""
Explanations of disagreements found while developing the experiment. A disagreement is reported whether or not a
cause is listed here.
"""

DIFFERENCE_EXAMPLES = 5
"""
Example rows per side of a differing candidate set.
"""


def run_variant(
    variant: str,
    scenario_file: Path,
    results_directory: Path,
    reference_steps: Optional[Path],
    arguments: argparse.Namespace,
) -> Dict[str, Any]:
    """
    Run one variant in a fresh process.

    :return: The worker result with the process measurements.
    """
    command = [
        sys.executable,
        "-m",
        "krrood_experiments.aamas27.agent_loop.worker",
        "--variant",
        variant,
        "--scenario",
        str(scenario_file),
        "--results-dir",
        str(results_directory),
    ]
    if reference_steps is not None:
        command += ["--reference-steps", str(reference_steps)]
    if variant in GRAPHDB_VARIANTS:
        command += ["--graphdb-state", str(results_directory / "graphdb_repository_state.json")]
        if arguments.graphdb_url:
            command += ["--graphdb-url", arguments.graphdb_url]
    environment = dict(os.environ, TQDM_DISABLE="1")
    print(f"running {variant} ...", flush=True)
    run = run_measured(command, timeout_seconds=arguments.timeout_seconds, environment=environment)
    record = run.to_json()
    if run.return_code != 0 or run.worker_result is None:
        raise RuntimeError(f"{variant} failed (return code {run.return_code}):\n{run.stderr_tail}")
    return record


def summarise_steps(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    :param steps: The step records of a variant.
    :return: Distributions of the per-step measurements.
    """
    summary: Dict[str, Any] = {
        "total_seconds": distribution([s["total_seconds"] for s in steps]),
        "phases": {phase: distribution([s["seconds"][phase] for s in steps]) for phase in PHASES},
        "decisions": {
            decision: distribution([s["decision_seconds"][decision] for s in steps])
            for decision in ("handouts", "tickets")
        },
    }
    for counter in ("statements_inserted", "statements_deleted", "round_trips", "reasoner_calls"):
        summary[counter] = distribution([s[counter] for s in steps])
    procedures = sorted({name for s in steps for name in s["procedure_calls"]})
    summary["procedure_calls"] = {
        name: distribution([s["procedure_calls"].get(name, 0) for s in steps]) for name in procedures
    }
    summary["handout_candidates"] = distribution([s["handout_candidates"] for s in steps])
    summary["ticket_candidates"] = distribution([s["ticket_candidates"] for s in steps])
    summary["actions"] = {}
    for s in steps:
        summary["actions"][s["action"][0]] = summary["actions"].get(s["action"][0], 0) + 1
    return summary


def read_candidates(path: Path) -> List[Dict[str, Any]]:
    """
    :param path: A candidates file.
    :return: The candidate rows of every step.
    """
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def compare_with_reference(
    reference: Dict[str, Any], candidate: Dict[str, Any], results_directory: Path
) -> Dict[str, Any]:
    """
    :param reference: The worker result of the reference variant.
    :param candidate: The worker result of a compared variant.
    :param results_directory: The results directory.
    :return: The number of steps whose decision and candidate sets agree, and the differences of the others.
    """
    reference_steps = json.loads((results_directory / reference["step_file"]).read_text())["steps"]
    candidate_steps = json.loads((results_directory / candidate["step_file"]).read_text())["steps"]
    reference_rows = read_candidates(results_directory / reference["candidates_file"])
    candidate_rows = read_candidates(results_directory / candidate["candidates_file"])
    disagreements = []
    equal_actions = equal_candidates = 0
    for reference_step, candidate_step, reference_row, candidate_row in zip(
        reference_steps, candidate_steps, reference_rows, candidate_rows
    ):
        same_action = reference_step["action"] == candidate_step["action"]
        same_candidates = reference_step["candidates_digest"] == candidate_step["candidates_digest"]
        equal_actions += same_action
        equal_candidates += same_candidates
        if same_action and same_candidates:
            continue
        difference = {"step": reference_step["step"], "reference_action": reference_step["action"],
                      "action": candidate_step["action"]}
        for kind in ("handouts", "tickets"):
            expected = {tuple(row) for row in reference_row[kind]}
            found = {tuple(row) for row in candidate_row[kind]}
            difference[kind] = {
                "reference": len(expected),
                "variant": len(found),
                "only_in_reference": len(expected - found),
                "only_in_variant": len(found - expected),
                "only_in_reference_examples": sorted(expected - found)[:DIFFERENCE_EXAMPLES],
                "only_in_variant_examples": sorted(found - expected)[:DIFFERENCE_EXAMPLES],
            }
        disagreements.append(difference)
    steps = len(reference_steps)
    return {
        "reference": reference["variant"],
        "steps": steps,
        "steps_compared": min(steps, len(candidate_steps)),
        "equal_actions": equal_actions,
        "equal_candidate_sets": equal_candidates,
        "all_agree": equal_actions == steps and equal_candidates == steps and len(candidate_steps) == steps,
        "known_cause": KNOWN_DISAGREEMENT_CAUSES.get(candidate["variant"]) if disagreements else None,
        "first_disagreements": disagreements[:10],
        "disagreeing_steps": [d["step"] for d in disagreements],
    }


def result_files(variant: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    :param variant: A variant name.
    :param entry: The summary entry of the variant.
    :return: The parts of its worker result that :func:`compare_with_reference` needs.
    """
    return {"variant": variant, "step_file": entry["files"]["steps"], "candidates_file": entry["files"]["candidates"]}


def print_table(summary: Dict[str, Any]) -> None:
    """
    Print the main numbers of every variant.

    :param summary: The experiment summary.
    """
    header = (f"{'variant':<14}{'setup s':>10}{'step med ms':>13}{'step p95 ms':>13}{'stmts/step':>12}"
              f"{'trips/step':>12}{'bnd LOC':>10}{'agree':>8}")
    print(header)
    for name, variant in summary["variants"].items():
        steps = variant["steps"]
        agreement = variant.get("agreement")
        agree = "ref" if agreement is None else f"{agreement['equal_actions']}/{agreement['steps']}"
        print(
            f"{name:<14}{variant['setup']['total_seconds']:>10.1f}"
            f"{steps['total_seconds']['median'] * 1000:>13.2f}{steps['total_seconds']['p95'] * 1000:>13.2f}"
            f"{steps['statements_inserted']['mean']:>12.1f}{steps['round_trips']['mean']:>12.1f}"
            f"{variant['code']['boundary_lines']['total']:>10}{agree:>8}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-dir", default=None)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--events-per-step", type=int, default=3)
    parser.add_argument("--variants", default=",".join(DEFAULT_VARIANTS),
                        help="comma-separated, the first is the reference")
    parser.add_argument("--graphdb-url", default=None)
    parser.add_argument("--raw-file", default=str(UNREASONED_FILE))
    parser.add_argument("--timeout-seconds", type=float, default=6 * 3600)
    parser.add_argument("--resume", action="store_true",
                        help="keep every variant already in the summary of --results-dir and run only the missing "
                             "ones of --variants")
    arguments = parser.parse_args()

    variants = [v for v in arguments.variants.split(",") if v]
    unknown = [v for v in variants if v not in VARIANTS]
    if unknown:
        parser.error(f"unknown variants {unknown}, expected some of {sorted(VARIANTS)}")
    results_directory = resolve_results_directory(arguments.results_dir, "agent_loop")
    scenario = generate_scenario(Path(arguments.raw_file), arguments.steps, arguments.seed, arguments.events_per_step)
    scenario_file = results_directory / "scenario.json"
    summary_file = results_directory / "agent_loop.json"
    summary: Dict[str, Any] = {
        "experiment": "agent_loop",
        "arguments": vars(arguments),
        "scenario": scenario.statistics(),
        "reference": variants[0],
        "variants": {},
    }
    if arguments.resume and summary_file.exists():
        previous = json.loads(summary_file.read_text())
        if json.loads(scenario_file.read_text()) != json.loads(json.dumps(scenario.to_json())):
            parser.error("--resume: the scenario of the results directory differs from the requested one")
        if previous["reference"] != variants[0]:
            parser.error("--resume: the results directory has another reference variant")
        summary["variants"] = dict(previous["variants"])
        summary["previous_arguments"] = previous.get("previous_arguments", []) + [previous["arguments"]]
    else:
        scenario.write(scenario_file)
        (results_directory / "graphdb_repository_state.json").unlink(missing_ok=True)

    reference_result: Optional[Dict[str, Any]] = None
    if variants[0] in summary["variants"]:
        reference_result = result_files(variants[0], summary["variants"][variants[0]])
    try:
        for variant in variants:
            if variant in summary["variants"]:
                print(f"{variant}: kept from the previous run", flush=True)
                continue
            reference_steps = results_directory / reference_result["step_file"] if reference_result else None
            record = run_variant(variant, scenario_file, results_directory, reference_steps, arguments)
            result = record.pop("worker_result")
            steps = json.loads((results_directory / result["step_file"]).read_text())["steps"]
            summary["variants"][variant] = {
                "description": result["description"],
                "setup": result["setup"],
                "steps": summarise_steps(steps),
                "code": result["code"],
                "process": record,
                "files": {"steps": result["step_file"], "candidates": result["candidates_file"]},
            }
            if reference_result is None:
                reference_result = result
            else:
                summary["variants"][variant]["agreement"] = compare_with_reference(
                    reference_result, result, results_directory
                )
            write_json(summary_file, summary)
    finally:
        if any(v in GRAPHDB_VARIANTS for v in variants):
            client = GraphDBClient(arguments.graphdb_url) if arguments.graphdb_url else GraphDBClient()
            if REPOSITORY in client.repository_ids():
                client.delete_repository(REPOSITORY)
    write_json(summary_file, summary)
    print_table(summary)
    print(f"results written to {results_directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
