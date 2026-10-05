"""
Turn the result files of the AAMAS 2027 OWL2Bench experiments into the LaTeX tables of the paper.

Inputs (any subset):

* ``--loading``: ``loading.json`` written by ``run_loading.py``.
* ``--queries``: ``queries.json`` written by ``run_queries.py`` (``answer_check.json`` next to it is used for the
  result counts and to mark queries whose answer sets differ from GraphDB).
* ``--protege``: a JSON file with the manually measured Protégé numbers, see ``protege_template.json``.

Outputs ``loading_table.tex``, ``query_table.tex`` and ``summary.csv`` into ``--output-dir`` (default: the directory of
the first input) and prints the tables.

Example::

    python scripts/aamas27/make_tables.py --loading results/aamas27/<run>/loading.json \\
        --queries results/aamas27/<run>/queries.json --protege results/aamas27/<run>/protege.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOADING_ROWS = [
    ("krrood", "KRROOD"),
    ("rdflib_owlrl", "RDFLib"),
    ("owlready2_pellet", "Owlready2"),
    ("protege", "Prot\\'eg\\'e"),
    ("graphdb", "GraphDB"),
    ("krrood_ormatic", "KRROOD + ORMatic"),
    ("krrood_eager_symmetric_transitive", "KRROOD, eager chaining (ablation)"),
]
"""
Systems of the loading table in display order (system key, label).
"""

QUERY_COLUMNS = [
    ("sqlalchemy", "SQLAlchemy"),
    ("graphdb", "GraphDB"),
    ("eql", "EQL"),
    ("rdflib", "RDFLib"),
    ("owlready2", "Owlready2"),
    ("protege", "Prot\\'eg\\'e"),
]
"""
Frameworks of the query table in display order (framework key, label).
"""


def mean_std(values: List[float]) -> Tuple[float, float]:
    return statistics.mean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def format_seconds(value: float) -> str:
    return f"{value:.1f}" if value >= 10 else f"{value:.2f}"


def format_memory(mib: float) -> str:
    return f"{mib / 1024:.2f}\\,GB" if mib >= 1024 else f"{mib:.0f}\\,MB"


def loading_cells(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate the repetitions of one system and input.

    :return: Mapping with ``time`` (mean, std) or ``status``, and ``memory`` (max peak RSS in MiB).
    """
    ok = [r for r in runs if r.get("status") == "ok"]
    failed = [r for r in runs if r.get("status") != "ok"]
    cells: Dict[str, Any] = {"repetitions": len(ok)}
    if ok:
        times = [
            r["worker_result"].get(
                "load_reasoning_and_persist_seconds", r["worker_result"]["load_and_reasoning_seconds"]
            )
            for r in ok
        ]
        cells["time"] = mean_std(times)
        cells["memory_mib"] = max(r["peak_rss_mib"] for r in ok)
        if ok[0].get("peak_minus_before_mib") is not None:
            cells["memory_note"] = "server JVM"
    if failed and not ok:
        status = failed[0]["status"]
        cells["status"] = status
        if status == "timeout":
            cells["timeout_seconds"] = failed[0].get("timeout_seconds")
        cells["memory_mib"] = failed[0].get("peak_rss_mib")
    return cells


def loading_table(loading: Optional[Dict[str, Any]], protege: Optional[Dict[str, Any]]) -> Tuple[str, List[List[str]]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for run in (loading or {}).get("runs", []):
        grouped.setdefault((run["system"], run["input"]), []).append(run)
    table: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for (system, input_name), runs in grouped.items():
        table.setdefault(system, {})[input_name] = loading_cells(runs)
    if protege:
        for input_name, entry in protege.get("loading", {}).items():
            seconds = entry.get("seconds")
            cells: Dict[str, Any] = {"memory_mib": entry.get("peak_rss_mib")}
            if isinstance(seconds, list):
                cells["time"] = mean_std(seconds)
            elif seconds is not None:
                cells["time"] = (float(seconds), 0.0)
            else:
                cells["status"] = entry.get("status", "n/a")
            table.setdefault("protege", {})[input_name] = cells

    best = {}
    for input_name in ("raw", "reasoned"):
        candidates = [
            (cells[input_name]["time"][0], system)
            for system, cells in table.items()
            if input_name in cells and "time" in cells[input_name] and system in ("krrood", "rdflib_owlrl", "owlready2_pellet", "protege", "graphdb")
        ]
        best[input_name] = min(candidates)[1] if candidates else None

    def cell(system: str, input_name: str) -> Tuple[str, str]:
        cells = table.get(system, {}).get(input_name)
        if not cells:
            return "n/a", "n/a"
        memory = format_memory(cells["memory_mib"]) if cells.get("memory_mib") else "n/a"
        if "time" in cells:
            mean, std = cells["time"]
            text = f"{format_seconds(mean)} \\pm {format_seconds(std)}" if std else format_seconds(mean)
            if best.get(input_name) == system:
                text = f"\\mathbf{{{text}}}"
            return f"${text}$", memory
        status = cells.get("status")
        if status == "timeout":
            return f"$>{cells.get('timeout_seconds', 0):.0f}$", memory
        if status == "memory_limit":
            return "o.o.m.", memory
        return str(status), memory

    rows = []
    csv_rows = []
    for system, label in LOADING_ROWS:
        if system not in table:
            continue
        raw_time, raw_memory = cell(system, "raw")
        reasoned_time, reasoned_memory = cell(system, "reasoned")
        rows.append(f"{label} & {raw_time} & {raw_memory} & {reasoned_time} & {reasoned_memory}\\\\")
        csv_rows.append(["loading", label, raw_time, raw_memory, reasoned_time, reasoned_memory])
    latex = "\n".join(
        [
            "\\begin{tabular}{lllll}",
            "\\toprule",
            "\\textbf{Framework} & \\multicolumn{2}{l}{\\textbf{Loading + Reasoning Raw}} & "
            "\\multicolumn{2}{l}{\\textbf{Loading + Reasoning Reasoned}}\\\\",
            " & \\textbf{Time [s]} & \\textbf{Peak memory} & \\textbf{Time [s]} & \\textbf{Peak memory}\\\\",
            "\\midrule",
            *rows,
            "\\bottomrule",
            "\\end{tabular}",
        ]
    )
    return latex, csv_rows


def query_table(queries: Dict[str, Any], check: Optional[Dict[str, Any]], protege: Optional[Dict[str, Any]]) -> Tuple[str, List[List[str]]]:
    per_framework: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for framework, run in queries.get("frameworks", {}).items():
        per_framework[framework] = (run.get("result") or {}).get("queries", {})
    if protege and protege.get("queries"):
        per_framework["protege"] = {
            number: (
                {"status": "ok", **entry}
                if entry.get("mean_ms") is not None
                else {"status": entry.get("status", "n/a")}
            )
            for number, entry in protege["queries"].items()
        }
    numbers = sorted({int(n) for entries in per_framework.values() for n in entries})
    columns = [(key, label) for key, label in QUERY_COLUMNS if key in per_framework]

    def completed(framework: str, number: int) -> bool:
        entry = per_framework[framework].get(str(number))
        return bool(entry) and entry.get("status") == "ok" and "mean_ms" in entry

    rows, csv_rows = [], []
    for number in numbers:
        reference = per_framework.get("graphdb", {}).get(str(number), {})
        count = reference.get("distinct_answers", reference.get("raw_rows"))
        count_text = f"{count}" if count is not None else "n/a"
        differing = []
        if check:
            for framework, comparison in check.get("queries", {}).get(str(number), {}).items():
                if not comparison.get("equal", False) and not comparison.get("missing_answer_file"):
                    differing.append(f"{framework}: {comparison['candidate']}")
        if differing:
            count_text += "$^\\dagger$"
        means = {key: per_framework[key][str(number)]["mean_ms"] for key, _ in columns if completed(key, number)}
        fastest = min(means, key=means.get) if means else None
        cells = []
        for key, _ in columns:
            entry = per_framework[key].get(str(number))
            if key in means:
                text = f"{entry['mean_ms']:.2f} \\pm {entry.get('std_ms', 0.0):.2f}"
                cells.append(f"$\\mathbf{{{text}}}$" if key == fastest else f"${text}$")
            elif entry:
                cells.append(str(entry.get("status", "n/a")))
            else:
                cells.append("n/a")
        rows.append(f"Q{number} & {count_text} & " + " & ".join(cells) + "\\\\")
        csv_rows.append(["query", f"Q{number}", count_text, *cells, "; ".join(differing)])

    all_completed = [n for n in numbers if all(completed(key, n) for key, _ in columns)]
    geometric = {}
    for key, _ in columns:
        values = [per_framework[key][str(n)]["mean_ms"] for n in all_completed]
        if values:
            geometric[key] = math.exp(statistics.mean(math.log(max(v, 1e-9)) for v in values))
    best = min(geometric, key=geometric.get) if geometric else None
    geometric_cells = [
        (f"$\\mathbf{{{geometric[key]:.2f}}}$" if key == best else f"${geometric[key]:.2f}$") if key in geometric else "n/a"
        for key, _ in columns
    ]
    header = "\\textbf{Query} & \\textbf{Results} & " + " & ".join(f"\\textbf{{{label}}}" for _, label in columns) + "\\\\"
    latex = "\n".join(
        [
            "\\begin{tabular}{l" + "l" * (len(columns) + 1) + "}",
            "\\toprule",
            header,
            "\\midrule",
            *rows,
            "\\midrule",
            "\\textbf{Geom. Mean} & --- & " + " & ".join(geometric_cells) + "\\\\",
            "\\bottomrule",
            "\\end{tabular}",
            f"% geometric mean over the {len(all_completed)} queries completed by all frameworks: "
            + ", ".join(f"Q{n}" for n in all_completed),
        ]
    )
    csv_rows.append(["query", "geometric_mean", "", *geometric_cells, f"over {all_completed}"])
    return latex, csv_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--loading")
    parser.add_argument("--queries")
    parser.add_argument("--protege")
    parser.add_argument("--output-dir")
    arguments = parser.parse_args()
    inputs = [p for p in (arguments.loading, arguments.queries) if p]
    if not inputs:
        parser.error("give --loading and/or --queries")
    output_directory = Path(arguments.output_dir or Path(inputs[0]).parent)
    output_directory.mkdir(parents=True, exist_ok=True)
    protege = json.loads(Path(arguments.protege).read_text()) if arguments.protege else None
    csv_rows: List[List[str]] = []
    if arguments.loading:
        latex, rows = loading_table(json.loads(Path(arguments.loading).read_text()), protege)
        (output_directory / "loading_table.tex").write_text(latex + "\n")
        csv_rows += rows
        print(latex, "\n")
    if arguments.queries:
        queries_path = Path(arguments.queries)
        check_path = queries_path.parent / "answer_check.json"
        check = json.loads(check_path.read_text()) if check_path.exists() else None
        latex, rows = query_table(json.loads(queries_path.read_text()), check, protege)
        (output_directory / "query_table.tex").write_text(latex + "\n")
        csv_rows += rows
        print(latex)
    with open(output_directory / "summary.csv", "w", newline="") as stream:
        csv.writer(stream).writerows(csv_rows)
    print(f"\nwritten to {output_directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
