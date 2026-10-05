"""
Optional ablation: KRROOD loading of the raw OWL2Bench data WITHOUT the weakly-connected-components post-processing
of symmetric-transitive properties (hasSameHomeTownWith). Relations of such properties are closed eagerly, one
relation at a time, as before the optimisation (krrood commit 3b72ec1001, 2026-01-14). The measurement runs in a fresh
process with a wall-clock cap (default 2 h); a run that hits the cap is reported as ``timeout`` with the cap as lower
bound.

Results are appended to ``<results-dir>/loading.json`` with system ``krrood_eager_symmetric_transitive``; run
``run_loading.py --systems krrood --inputs raw`` into the same directory for the comparison.

Example::

    python scripts/aamas27/run_symmetric_transitive_ablation.py --results-dir results/aamas27/<run>
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeout-seconds", type=float, default=2 * 3600)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--memory-limit-gib", type=float, default=None)
    parser.add_argument("--results-dir", default=None)
    arguments = parser.parse_args()
    command = [
        sys.executable, str(Path(__file__).with_name("run_loading.py")),
        "--systems", "krrood_eager_symmetric_transitive",
        "--inputs", "raw",
        "--repetitions", str(arguments.repetitions),
        "--timeout-seconds", str(arguments.timeout_seconds),
    ]
    if arguments.memory_limit_gib:
        command += ["--memory-limit-gib", str(arguments.memory_limit_gib)]
    if arguments.results_dir:
        command += ["--results-dir", arguments.results_dir]
    return subprocess.call(command)


if __name__ == "__main__":
    sys.exit(main())
