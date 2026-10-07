"""
What GraphDB's SPARQL update costs in the agent loop (Section 7.4), split into the cost of a request and its commit
and the cost of the OWL 2 RL inference that the inserted statements trigger. Run on the repository that the agent
loop's GraphDB variants use, in its state right after loading (graphdb_repository_state.json); every statement
written here is deleted again and the statement counts are checked to be those after loading.

Updates measured, each repeated for the first N steps of a scenario of the agent loop:

* ``empty``: ``INSERT DATA {}``, a request and a commit that change nothing.
* ``unrelated``: one statement of a predicate that no rule of the ruleset uses, so nothing is inferred.
* ``step``: the step's perceived facts in one update, as the graphdb variant sends them.
* ``batched``: the perceived facts of all N steps in one update, which the agent cannot do, as it decides after
  every step; it shows how the cost per update is shared when updates are batched.

Usage: python graphdb_update_cost.py SCENARIO_JSON STATE_JSON OUTPUT_JSON [--steps 30]
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from krrood_experiments.aamas27.agent_loop.graphdb_variant import REPOSITORY
from krrood_experiments.aamas27.agent_loop.rdf_mirror import delete_data, event_triples, insert_data
from krrood_experiments.aamas27.agent_loop.scenario import Scenario
from krrood_experiments.aamas27.graphdb import GraphDBClient

UNRELATED = "https://example.org/agent-loop#updateCostProbe"
"""A predicate that occurs in no rule, so a statement of it triggers no inference."""


def timed_update(client: GraphDBClient, update: str) -> float:
    """
    :return: The wall time of the update in milliseconds.
    """
    start = time.perf_counter()
    client.update(REPOSITORY, update)
    return (time.perf_counter() - start) * 1000


def summary(values: list) -> dict:
    return {"count": len(values), "median_ms": statistics.median(values), "mean_ms": statistics.mean(values),
            "min_ms": min(values), "max_ms": max(values)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    parser.add_argument("state")
    parser.add_argument("output")
    parser.add_argument("--steps", type=int, default=30)
    arguments = parser.parse_args()
    client = GraphDBClient()
    baseline = json.loads(Path(arguments.state).read_text())["statements"]
    if client.count_statements(REPOSITORY) != baseline:
        raise SystemExit("the repository is not in its state right after loading")
    perceptions = Scenario.read(Path(arguments.scenario)).perceptions[:arguments.steps]
    step_triples = [[t for event in p.knowledge_events for t in event_triples(event)] for p in perceptions]
    results = {}
    results["empty"] = summary([timed_update(client, "INSERT DATA {}") for _ in step_triples])
    unrelated = [(f"https://example.org/agent-loop#probe{i}", UNRELATED, '"1"') for i in range(len(step_triples))]
    results["unrelated"] = summary([timed_update(client, insert_data([triple])) for triple in unrelated])
    client.update(REPOSITORY, delete_data(unrelated))
    results["step"] = summary([timed_update(client, insert_data(triples)) for triples in step_triples])
    results["step"]["statements_per_update"] = statistics.mean(len(t) for t in step_triples)
    written = [t for triples in step_triples for t in triples]
    client.update(REPOSITORY, delete_data(written))
    batched = timed_update(client, insert_data(written))
    results["batched"] = {"steps": len(step_triples), "statements": len(written), "total_ms": batched,
                          "per_step_ms": batched / len(step_triples)}
    client.update(REPOSITORY, delete_data(written))
    after = client.count_statements(REPOSITORY)
    results["repository_restored"] = after == baseline
    Path(arguments.output).write_text(json.dumps({"steps": len(step_triples), "updates": results}, indent=1))
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
