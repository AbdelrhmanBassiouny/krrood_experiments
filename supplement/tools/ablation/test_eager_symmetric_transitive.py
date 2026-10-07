"""
Eager closure of symmetric-transitive properties (the ablation "KRROOD without step 5") on small synthetic data:
the OWL2Bench TBox plus n persons linked by hasSameHomeTownWith. Each load runs in a fresh process (probe.py),
because the loader keeps class-level state. ABLATION_WORK is the folder with tbox.rdf (make_tbox.py) that the
synthetic data files are written to; reproduce.sh sets it.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
WORK = Path(os.environ.get("ABLATION_WORK", HERE))
TBOX = WORK / "tbox.rdf"


def load(n: int, mode: str, topology: str = "chain") -> dict:
    output = subprocess.run(
        [sys.executable, str(HERE / "probe.py"), str(TBOX), str(n), mode, topology, str(WORK)],
        capture_output=True, text=True, check=True, timeout=600,
    ).stdout
    return json.loads(output.strip().splitlines()[-1])


def everyone_related_to_everyone(result: dict) -> bool:
    names = {f"p{i}" for i in range(result["n"])}
    return all(set(partners) == names for partners in result["partners"].values())


@pytest.mark.parametrize("topology", ["chain", "star"])
def test_eager_mode_terminates(topology):
    assert load(8, "eager", topology)["seconds"] < 60


@pytest.mark.parametrize("topology", ["chain", "star"])
def test_eager_closure_is_complete(topology):
    assert everyone_related_to_everyone(load(8, "eager", topology))


@pytest.mark.parametrize("topology", ["chain", "star"])
def test_eager_and_component_mode_give_the_same_facts(topology):
    assert load(8, "eager", topology)["partners"] == load(8, "component", topology)["partners"]


def test_eager_mode_adds_each_fact_once():
    result = load(8, "eager")
    assert result["values_added"] == 8 * 8


def test_eager_mode_records_one_relation_per_fact():
    result = load(8, "eager")
    assert result["home_town_relations_in_graph"] == 8 * 8


def test_eager_work_grows_cubically_not_faster():
    small, large = load(16, "eager"), load(32, "eager")
    ratio = large["update_source_calls"] / small["update_source_calls"]
    assert 6 < ratio < 10, ratio
