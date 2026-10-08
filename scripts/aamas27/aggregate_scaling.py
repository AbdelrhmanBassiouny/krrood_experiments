"""
Combines the scaling experiment (supplement README, "Scaling") into one JSON file and a LaTeX table: loading and
reasoning time and memory from the raw data of 1, 2, 4 and 8 OWL2Bench universities, for KRROOD, Nemo, reasonable and
GraphDB, and the scaling audit of KRROOD's knowledge base against Nemo's closure at every size.

Expected layout of the results folder (as written by ``reproduce.sh scaling``)::

    loading_inmemory_u{N}/loading.json   run_loading.py --systems krrood,nemo_owlrl,reasonable_owlrl --inputs raw
    loading_graphdb_u{N}/loading.json    run_loading.py --systems graphdb --inputs raw (N > 1)
    audit/u{N}.json                      python -m krrood_experiments.aamas27.scaling_audit

Memory is the peak resident set size minus that right after the imports (``import_memory.json`` of the main run),
as in Table 2 of the paper; for GraphDB it is the increase of the server's resident set size during the upload.

GraphDB's loading of one university is that of the main run (``--graphdb-one-university``, its loading.json).

Usage: python aggregate_scaling.py RESULTS_DIR IMPORT_MEMORY_JSON OUTPUT_JSON OUTPUT_TEX
    [--graphdb-one-university LOADING_JSON]
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

UNIVERSITIES = (1, 2, 4, 8)
SYSTEMS = ("krrood", "nemo_owlrl", "reasonable_owlrl", "graphdb")


def runs_of(path: Path) -> List[Dict[str, Any]]:
    """
    :param path: A loading.json file.
    :return: Its runs, or no runs if the file does not exist.
    """
    return json.loads(path.read_text())["runs"] if path.exists() else []


def summary(runs: List[Dict[str, Any]], import_mib: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """
    :param runs: The runs of one system on one input.
    :param import_mib: Resident set size after the imports, per system.
    :return: Status, mean time, standard deviation and memory increase of the runs.
    """
    if not runs:
        return None
    ok = [r for r in runs if r.get("status") == "ok"]
    if not ok:
        return {"status": runs[0].get("status"), "repetitions": 0, "peak_rss_mib": runs[0].get("peak_rss_mib"),
                "wall_seconds": runs[0].get("wall_seconds")}
    times = [r["worker_result"]["load_and_reasoning_seconds"] for r in ok]
    system = ok[0]["system"]
    if ok[0].get("peak_minus_before_mib") is not None:
        memory = max(r["peak_minus_before_mib"] for r in ok)
    else:
        memory = max(r["peak_rss_mib"] for r in ok) - import_mib.get(system, 0.0)
    result = {"status": "ok", "repetitions": len(ok), "mean_seconds": statistics.mean(times),
              "stdev_seconds": statistics.stdev(times) if len(times) > 1 else 0.0, "memory_increase_mib": memory}
    if system == "graphdb":
        result["statements"] = ok[0]["worker_result"].get("statements")
    return result


def import_memory(path: Path) -> Dict[str, float]:
    """
    :param path: import_memory.json of the main run.
    :return: Resident set size after the imports, per system (Nemo is a separate binary: 0).
    """
    record = json.loads(path.read_text())
    result = {name: entry["max_mib"] for name, entry in record.items() if "max_mib" in entry}
    result.setdefault("nemo_owlrl", 0.0)
    return result


def seconds(cell: Optional[Dict[str, Any]]) -> str:
    if cell is None:
        return "--"
    if cell["status"] != "ok":
        return {"memory_limit": "out of mem.", "timeout": "timeout"}.get(cell["status"], cell["status"])
    value = cell["mean_seconds"]
    return f"{value:,.0f}" if value >= 100 else f"{value:.1f}"


def memory(cell: Optional[Dict[str, Any]]) -> str:
    if cell is None or cell["status"] != "ok":
        return "--"
    mib = cell["memory_increase_mib"]
    return f"{mib / 1024:.1f}\\,GB" if mib >= 1024 else f"{mib:.0f}\\,MB"


def latex(record: Dict[str, Any]) -> str:
    """
    :return: The rows of the paper's scaling table.
    """
    rows = []
    for entry in record["sizes"]:
        cells = entry["systems"]
        audit = entry.get("audit")
        equal = "--" if audit is None else (
            "yes" if audit["facts"]["missing"] == 0 and audit["facts"]["extra"] == 0
            else f"{audit['facts']['missing']}/{audit['facts']['extra']}")
        facts = "--" if audit is None else f"{audit['facts']['reference'] / 1e6:.1f}\\,M"
        rows.append(" & ".join([
            str(entry["universities"]), ("--" if entry["raw_statements"] is None else f"{entry['raw_statements'] / 1000:.0f}\\,k"), facts,
            seconds(cells.get("krrood")), memory(cells.get("krrood")), equal,
            seconds(cells.get("nemo_owlrl")), seconds(cells.get("reasonable_owlrl")), seconds(cells.get("graphdb")),
        ]) + r" \\")
    return "\n".join(rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("results", "import_memory", "output_json", "output_tex"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--graphdb-one-university", type=Path, default=None)
    arguments = parser.parse_args()
    results, import_file = arguments.results, arguments.import_memory
    output_json, output_tex = arguments.output_json, arguments.output_tex
    import_mib = import_memory(import_file)
    sizes = []
    for universities in UNIVERSITIES:
        runs = runs_of(results / f"loading_inmemory_u{universities}" / "loading.json")
        runs += runs_of(results / f"loading_graphdb_u{universities}" / "loading.json")
        if universities == 1 and arguments.graphdb_one_university is not None:
            runs += [r for r in runs_of(arguments.graphdb_one_university)
                     if r["system"] == "graphdb" and r["input"] == "raw"]
        audit_file = results / "audit" / f"u{universities}.json"
        audit = json.loads(audit_file.read_text()) if audit_file.exists() else None
        systems = {system: summary([r for r in runs if r["system"] == system], import_mib) for system in SYSTEMS}
        raw_statements = audit["raw_statements"] if audit else None
        sizes.append({"universities": universities, "raw_statements": raw_statements,
                      "systems": {k: v for k, v in systems.items() if v is not None},
                      "audit": None if audit is None else {k: audit[k] for k in (
                          "named_individuals", "reference_statements", "facts", "kinds",
                          "krrood_load_and_reasoning_seconds")}})
    record = {"sizes": sizes, "import_memory_mib": import_mib}
    output_json.write_text(json.dumps(record, indent=1))
    output_tex.write_text(latex(record))
    print(output_tex.read_text())


if __name__ == "__main__":
    main()
