"""
Combine agent-loop runs with different seeds (one results directory of run_agent_loop.py per seed) into one
summary: per variant, the median step time and the median of each phase over all steps of all seeds, the range of
the per-seed medians, a 95% bootstrap confidence interval of the median over all steps (resampling seeds, then
steps), whether the variant made the reference's decisions in every step of every seed, and its boundary code.

Usage: python aggregate_agent_loop_seeds.py OUTPUT_JSON RESULTS_DIR [RESULTS_DIR ...]
"""
from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

PHASES = ("mapping", "update", "reasoning", "push", "query", "procedures", "decide", "act")
BOOTSTRAP_SAMPLES = 2000


def step_records(directory: Path, variant: str) -> List[Dict[str, Any]]:
    """
    :return: The per-step measurements of the variant in one run.
    """
    return json.loads((directory / f"agent_loop_{variant}.json").read_text())["steps"]


def bootstrap_median(per_seed: List[List[float]], rng: random.Random) -> List[float]:
    """
    :param per_seed: The step times of every seed.
    :return: The 2.5 and 97.5 percentiles of the median, resampling seeds and then the steps within each seed.
    """
    medians = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = []
        for times in rng.choices(per_seed, k=len(per_seed)):
            sample.extend(rng.choices(times, k=len(times)))
        medians.append(statistics.median(sample))
    medians.sort()
    return [medians[int(0.025 * BOOTSTRAP_SAMPLES)], medians[int(0.975 * BOOTSTRAP_SAMPLES) - 1]]


def main() -> None:
    output, directories = Path(sys.argv[1]), [Path(d) for d in sys.argv[2:]]
    summaries = {d: json.loads((d / "agent_loop.json").read_text()) for d in directories}
    variants = sorted({v for s in summaries.values() for v in s["variants"]})
    rng = random.Random(0)
    result: Dict[str, Any] = {"seeds": {str(d): s["arguments"]["seed"] for d, s in summaries.items()},
                              "steps_per_seed": {str(d): s["arguments"]["steps"] for d, s in summaries.items()},
                              "variants": {}}
    for variant in variants:
        runs = [d for d in directories if variant in summaries[d]["variants"]]
        records = {d: step_records(d, variant) for d in runs}
        per_seed = [[r["total_seconds"] * 1000 for r in records[d]] for d in runs]
        every = [t for times in per_seed for t in times]
        entry = summaries[runs[0]]["variants"][variant]
        agreements = [summaries[d]["variants"][variant].get("agreement") for d in runs]
        result["variants"][variant] = {
            "seeds": [summaries[d]["arguments"]["seed"] for d in runs],
            "steps": len(every),
            "median_step_ms": statistics.median(every),
            "median_step_ms_95ci": bootstrap_median(per_seed, rng) if len(runs) > 1 else None,
            "per_seed_median_step_ms": [statistics.median(times) for times in per_seed],
            "p95_step_ms": statistics.quantiles(every, n=20)[-1],
            "median_phase_ms": {phase: statistics.median(r["seconds"].get(phase, 0.0) * 1000
                                                         for d in runs for r in records[d]) for phase in PHASES},
            "all_agree": None if agreements[0] is None else all(a["all_agree"] for a in agreements),
            "equal_actions": None if agreements[0] is None else sum(a["equal_actions"] for a in agreements),
            "steps_compared": None if agreements[0] is None else sum(a["steps_compared"] for a in agreements),
            "boundary_lines": entry["code"]["boundary_lines"],
            "setup_seconds": [summaries[d]["variants"][variant]["setup"].get("total_seconds") for d in runs],
        }
    output.write_text(json.dumps(result, indent=1))
    for variant, entry in result["variants"].items():
        print(f"{variant:18} seeds {entry['seeds']} median {entry['median_step_ms']:.1f} ms "
              f"ci {entry['median_step_ms_95ci']} per seed {[round(x, 1) for x in entry['per_seed_median_step_ms']]} "
              f"update {entry['median_phase_ms']['update']:.2f} query {entry['median_phase_ms']['query']:.1f} "
              f"agree {entry['equal_actions']}/{entry['steps_compared']}")


if __name__ == "__main__":
    main()
