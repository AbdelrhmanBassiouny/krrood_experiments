"""
Test of the runtime closure audit (:mod:`krrood_experiments.aamas27.runtime_audit`): a few steps of the KRROOD agent
loop, compared with the OWL 2 RL closure that Nemo computes. Right after loading (step 0) the knowledge base must equal
the closure; after the steps no fact may be extra, and every property fact must be stored.

The audit runs in its own process (it loads the OWL2Bench data, about 15 s, and runs Nemo three times, about 1.5 min in
all). It needs the Nemo command-line client (``$NEMO_BINARY`` or ``nmo`` on the PATH).

Run with::

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/aamas27/test_runtime_audit.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

NEMO_BINARY = os.environ.get("NEMO_BINARY") or shutil.which("nmo")


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    directory = tmp_path_factory.mktemp("runtime_audit")
    output = directory / "seed0.json"
    completed = subprocess.run(
        [sys.executable, "-m", "krrood_experiments.aamas27.runtime_audit", "--seed", "0", "--steps", "3",
         "--checkpoints", "0,3", "--no-rdfxml-check", "--nemo-binary", NEMO_BINARY,
         "--work-dir", str(directory / "work"), "--output", str(output)],
        capture_output=True, text=True, timeout=1800, env=dict(os.environ, TQDM_DISABLE="1"),
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    return json.loads(output.read_text())


pytestmark = pytest.mark.skipif(NEMO_BINARY is None, reason="needs the Nemo command-line client nmo")


def test_loaded_knowledge_base_equals_the_closure(report):
    baseline = report["results"][0]
    assert baseline["steps"] == 0
    assert baseline["facts"]["missing"] == 0
    assert baseline["facts"]["extra"] == 0
    assert baseline["facts"]["krrood"] == baseline["facts"]["reference"] > 0


def test_the_steps_add_facts_and_people(report):
    after = report["results"][1]
    assert after["steps"] == 3
    assert after["events"] == 9
    assert after["new_people"] > 0
    assert after["facts"]["reference"] > report["results"][0]["facts"]["reference"]


def test_no_extra_facts_and_property_facts_are_complete_after_the_steps(report):
    after = report["results"][1]
    assert after["facts"]["extra"] == 0
    assert after["kinds"]["object"]["missing"] == 0
    assert after["kinds"]["data"]["missing"] == 0
