"""
Worker process of the agent-loop experiment: runs the loop of one variant on a scenario file in a fresh interpreter, so
that the variants do not share memory, caches or the global symbol graph, and writes its measurements to the results
directory. Started by ``scripts/aamas27/run_agent_loop.py``.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Type

from ..memory import print_worker_result
from .loop import run_agent_loop
from .robot import Action, Robot
from .scenario import Scenario

VARIANTS: Dict[str, str] = {
    "krrood": "krrood_experiments.aamas27.agent_loop.krrood_variant:KrroodVariant",
    "krrood_navigation": "krrood_experiments.aamas27.agent_loop.krrood_navigation_variant:KrroodNavigationVariant",
    "graphdb": "krrood_experiments.aamas27.agent_loop.graphdb_variant:GraphDBVariant",
    "graphdb_push": "krrood_experiments.aamas27.agent_loop.graphdb_push_variant:GraphDBPushVariant",
    "reasonable": "krrood_experiments.aamas27.agent_loop.reasonable_variant:ReasonableVariant",
    "nemo": "krrood_experiments.aamas27.agent_loop.nemo_variant:NemoVariant",
}
"""
Variant name to ``module:class``. Modules are imported only in the worker that runs the variant.
"""

GRAPHDB_VARIANTS = frozenset({"graphdb", "graphdb_push"})
"""
The variants that need a GraphDB server.
"""


def variant_class(name: str) -> Type:
    """
    :param name: A variant name.
    :return: Its class.
    """
    module_name, class_name = VARIANTS[name].split(":")
    return getattr(importlib.import_module(module_name), class_name)


def read_performed_actions(step_file: Path) -> List[Action]:
    """
    :param step_file: The step file of a variant's run.
    :return: The actions its robot carried out, in step order.
    """
    steps = json.loads(step_file.read_text())["steps"]
    return [Action.from_json(step["performed_action"]) for step in steps]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    parser.add_argument("--scenario", required=True, help="scenario JSON file")
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--reference-steps", default=None,
                        help="step file of the reference variant, whose actions the robot carries out")
    parser.add_argument("--graphdb-url", default=None)
    parser.add_argument("--graphdb-state", default=None,
                        help="state file of the GraphDB repository: keep, restore and reuse it across variants")
    arguments = parser.parse_args()
    os.environ.setdefault("TQDM_DISABLE", "1")

    scenario = Scenario.read(Path(arguments.scenario))
    reference_actions: Optional[List[Action]] = (
        read_performed_actions(Path(arguments.reference_steps)) if arguments.reference_steps else None
    )
    start = time.perf_counter()
    cls = variant_class(arguments.variant)
    import_seconds = time.perf_counter() - start
    options = {}
    if arguments.variant in GRAPHDB_VARIANTS and arguments.graphdb_url:
        options["graphdb_url"] = arguments.graphdb_url
    if arguments.variant in GRAPHDB_VARIANTS and arguments.graphdb_state:
        options["state_file"] = Path(arguments.graphdb_state)
    variant = cls(scenario=scenario, robot=Robot.at_start(scenario.robot, scenario.campus), **options)

    def progress(step: int, record: Dict) -> None:
        if step % 20 == 0 or step == scenario.steps - 1:
            print(f"[{arguments.variant}] step {step}: {record['total_seconds']:.4f} s", file=sys.stderr, flush=True)

    result = run_agent_loop(variant, reference_actions, progress)
    result.setup["import_seconds"] = import_seconds
    result.setup["follows_reference_actions"] = reference_actions is not None
    step_file, candidates_file = result.write(Path(arguments.results_dir))
    print_worker_result(
        {
            "variant": arguments.variant,
            "description": cls.description,
            "setup": result.setup,
            "step_file": step_file.name,
            "candidates_file": candidates_file.name,
            "code": cls.code_report(),
        }
    )
    sys.stdout.flush()
    sys.stderr.flush()
    # Skip interpreter tear-down of large object graphs, it is not part of the measurement.
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
