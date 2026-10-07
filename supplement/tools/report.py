"""
The report of a run: what was run, what was skipped and why, and the results as numbered tables with titles and
captions, next to the numbers of the paper's run (results/ of the bundle). Printed to the terminal and written as
Markdown.

Usage: python report.py RUN_DIR PAPER_RESULTS_DIR MODE OUTPUT_MARKDOWN
"""
from __future__ import annotations

import json
import math
import re
import shutil
import statistics
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

RUN, PAPER, MODE, OUTPUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
OWN = MODE == "paper"
"""The report of the paper's run itself: no columns that repeat it as "paper"."""

LOADING_SYSTEMS = [
    ("krrood", "KRROOD"),
    ("krrood_ormatic", "KRROOD (with ORMatic)"),
    ("owlready2_pellet", "Owlready2 + Pellet"),
    ("rdflib_owlrl", "RDFLib + owlrl"),
    ("graphdb", "GraphDB"),
    ("protege", "Protégé + Pellet (by hand)"),
    ("nemo_owlrl", "Nemo (OWL 2 RL/RDF rules)"),
    ("reasonable_owlrl", "reasonable (OWL 2 RL, Rust)"),
    ("krrood_eager_symmetric_transitive", "KRROOD without step 5"),
]
QUERY_FRAMEWORKS = [("sqlalchemy", "SQL"), ("graphdb", "GraphDB"), ("eql", "EQL"), ("rdflib", "RDFLib"),
                    ("owlready2", "Owlready2")]
SUITES = [
    ("measurement_tests", "Tests of the measurement scripts", "38 passed, 2 skipped"),
    ("listings", "The paper's listings and the formalization's examples", "25 passed"),
    ("ormatic_listing", "The ORMatic listing (Section 6)", "1 passed"),
    ("ablation_tests", "Eager chaining on small data (the ablation)", "9 passed"),
]
LICENSE_HELP = (
    "GraphDB 11 needs a license file even for its free edition, and we cannot distribute ours. Request "
    "GraphDB Free on https://graphdb.ontotext.com/ (the license arrives by e-mail), save it, e.g. as "
    "~/graphdb.license, and run again with GRAPHDB_LICENSE=~/graphdb.license (run_ubuntu.sh also finds it in "
    "~/graphdb.license and ~/Downloads/). Finished steps are not repeated."
)


def load(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def first(*paths: Path) -> Optional[Any]:
    for path in paths:
        value = load(path)
        if value is not None:
            return value
    return None


# --- Tables ------------------------------------------------------------------------------------------------------

CELL_WIDTH = 60
"""Longer cells wrap in the terminal."""


class Table:
    count = 0

    def __init__(self, title: str, caption: str, header: List[str], rows: List[List[str]],
                 right: Optional[List[int]] = None):
        Table.count += 1
        self.number, self.title, self.caption = Table.count, title, caption
        self.header, self.rows = header, [[str(cell) for cell in row] for row in rows]
        self.right = set(right or [])

    def without(self, columns: List[int]) -> "Table":
        """The table without the given columns (the paper's, in the report of the paper's run)."""
        keep = [i for i in range(len(self.header)) if i not in columns]
        self.header = [self.header[i] for i in keep]
        self.rows = [[row[i] for i in keep] for row in self.rows]
        self.right = {keep.index(i) for i in self.right if i in keep}
        return self

    def _cell(self, text: str, width: int, column: int) -> str:
        return text.rjust(width) if column in self.right else text.ljust(width)

    def terminal(self, width: int) -> str:
        # Long cells wrap within their column, so that a table fits a terminal.
        wrapped = [[textwrap.wrap(cell, CELL_WIDTH) or [""] for cell in row] for row in [self.header, *self.rows]]
        widths = [max(len(line) for row in wrapped for line in row[i]) for i in range(len(self.header))]
        line = lambda left, middle, right: left + middle.join("─" * (w + 2) for w in widths) + right

        def render(cells: List[List[str]]) -> List[str]:
            height = max(len(cell) for cell in cells)
            return ["│" + "│".join(f" {self._cell(cell[k] if k < len(cell) else '', w, i)} "
                                   for i, (cell, w) in enumerate(zip(cells, widths))) + "│" for k in range(height)]

        out = [f"Table {self.number}. {self.title}", line("┌", "┬", "┐"), *render(wrapped[0]), line("├", "┼", "┤")]
        out += [text for row in wrapped[1:] for text in render(row)]
        out.append(line("└", "┴", "┘"))
        out += textwrap.wrap(self.caption, width=min(width, max(90, len(out[1]))))
        return "\n".join(out)

    def markdown(self) -> str:
        align = ["---:" if i in self.right else ":---" for i in range(len(self.header))]
        escape = lambda c: c.replace("|", "\\|")
        out = [f"### Table {self.number}. {self.title}", "",
               "| " + " | ".join(map(escape, self.header)) + " |", "| " + " | ".join(align) + " |"]
        out += ["| " + " | ".join(map(escape, row)) + " |" for row in self.rows]
        out += ["", f"*{self.caption}*"]
        return "\n".join(out)


def seconds(value: float) -> str:
    return f"{value:.0f}" if value >= 100 else f"{value:.1f}" if value >= 10 else f"{value:.2f}"


def milliseconds(value: float) -> str:
    return f"{value:.0f}" if value >= 100 else f"{value:.1f}" if value >= 10 else f"{value:.2f}"


def memory(mib: Optional[float]) -> str:
    if mib is None:
        return "–"
    return f"{mib / 1024:.2f} GB" if mib >= 1024 else f"{mib:.0f} MB"


# --- Tests -------------------------------------------------------------------------------------------------------

def test_table() -> Optional[Table]:
    rows = []
    for name, label, expected in SUITES:
        log = RUN / "tests" / f"{name}.log"
        if not log.exists():
            continue
        lines = [l for l in log.read_text().splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
        result = re.sub(r" in [\d.]+s.*$", "", re.sub(r"=+", "", lines[-1]).strip()) if lines else "did not finish"
        rows.append([label, result, expected])
    if not rows:
        return None
    return Table("Test suites", "Each suite is run with pytest in the container; \"Expected\" is the result with this "
                 "bundle. A failed test means that the code in the image does not behave as in the paper.",
                 ["Suite", "This run", "Expected"], rows)


# --- Answers -----------------------------------------------------------------------------------------------------

def answer_table() -> Optional[Table]:
    live = load(RUN / "check" / "answer_check.json")
    check = live or load(RUN / "reference_check" / "answer_check.json")
    if not check:
        return None
    present = [(key, label) for key, label in QUERY_FRAMEWORKS
               if key != "graphdb" and any(key in entry for entry in check["queries"].values())]
    rows = []
    for number, entry in sorted(check["queries"].items(), key=lambda item: int(item[0])):
        reference = next((c["reference"] for c in entry.values() if "reference" in c), None)
        cells = []
        for key, _ in present:
            comparison = entry.get(key)
            if comparison is None or comparison.get("missing_answer_file"):
                cells.append("–")
            elif comparison["equal"]:
                cells.append("equal")
            else:
                cells.append(f"DIFFERS (-{comparison['only_in_reference']}, +{comparison['only_in_candidate']})")
        rows.append([f"Q{number}", f"{reference:,}" if reference is not None else "–", *cells])
    source = ("a GraphDB server started in this run, with the OWL 2 RL ruleset" if live else
              "the answer sets that GraphDB returned in the paper's run (results/check/answers/graphdb), as no "
              "GraphDB license was available or the mode was quick")
    caption = (f"Each system's answers to the 18 OWL 2 RL queries of OWL2Bench, normalized to sets of tuples, "
               f"compared with GraphDB's, from {source}. \"Answers\" is the number of GraphDB's answers; \"equal\" "
               f"means the same set; \"DIFFERS (-a, +b)\" gives the answers missing and extra. In the paper (Section "
               f"7.1), all systems are equal on all queries. Result: "
               f"{'all equal' if check['all_equal'] else 'DIFFERENCES FOUND'}.")
    return Table("Answers compared with GraphDB's (paper, Section 7.1)", caption,
                 ["Query", "Answers", *[label for _, label in present]], rows, right=[1])


def audit_table() -> Optional[Table]:
    audit = load(RUN / "audit" / "audit.json")
    if not audit:
        return None
    paper = load(PAPER / "audit" / "audit.json") or {}
    rows = []
    for part, label in (("classes", "Class memberships"), ("object_properties", "Object-property assertions"),
                        ("data_properties", "Data-property assertions")):
        totals = {f: sum(x[f] for x in audit[part].values()) for f in ("krrood", "reference", "unsound", "missing")}
        paper_total = sum(x["reference"] for x in paper.get(part, {}).values()) if paper else None
        rows.append([label, f"{totals['krrood']:,}", f"{totals['reference']:,}", str(totals["unsound"]),
                     str(totals["missing"]), f"{paper_total:,}" if paper_total is not None else "–"])
    check = audit["owl2_rl_check"]
    caption = ("KRROOD's knowledge base, loaded from the raw data, compared assertion by assertion with GraphDB's OWL 2 "
               "RL closure: \"extra\" are assertions only in KRROOD (unsound), \"missing\" only in the closure. The "
               "paper reports 0 and 0 for all three. The OWL 2 RL rules that derive equalities or inconsistencies: "
               f"{'passed' if check.get('passed') else 'FAILED'}, {check.get('equalities')} equalities, "
               f"{check.get('inconsistencies')} inconsistencies (paper: 0 and 0).")
    table = Table("Knowledge base compared with the OWL 2 RL closure (paper, Section 7.1)", caption,
                  ["Assertions", "KRROOD", "Closure", "Extra", "Missing", "Closure (paper)"], rows,
                  right=[1, 2, 3, 4, 5])
    return table.without([5]) if OWN else table


def baseline_closure_table() -> Optional[Table]:
    comparison = load(RUN / "baselines" / "closure_comparison.json")
    if not comparison:
        return None
    labels = dict(LOADING_SYSTEMS)
    rows = []
    for name, candidate in comparison["candidates"].items():
        for part, label in (("class", "Class memberships"), ("object", "Object-property assertions"),
                            ("data", "Data-property assertions")):
            counts = candidate[part]
            rows.append([labels.get(name, name), label, f"{counts['candidate']:,}", f"{counts['reference']:,}",
                         f"{counts['extra']:,}", f"{counts['missing']:,}"])
    caption = ("The closures that the in-memory baselines compute from the raw data, compared with GraphDB's OWL 2 RL "
               "closure as KRROOD's knowledge base is (previous table), for the same individuals and properties. "
               "\"Extra\": only in the baseline's closure; \"missing\": only in GraphDB's. reasonable 0.4.4 applies "
               "prp-ifp to any two subjects of an inverse-functional property, also with different objects, and so "
               "merges the 21 heads of organizations (isHeadOf); and it derives no facts from property chains.")
    return Table("Closures of the in-memory baselines compared with the OWL 2 RL closure", caption,
                 ["System", "Assertions", "Baseline", "Closure", "Extra", "Missing"], rows, right=[2, 3, 4, 5])


# --- Loading -----------------------------------------------------------------------------------------------------

def import_mib(imports: Optional[Dict[str, Any]], system: str) -> Optional[float]:
    if not imports or system not in imports:
        return None
    entry = imports[system]
    return imports[entry["same_as"]]["max_mib"] if "same_as" in entry else entry["max_mib"]


def loading_cells(folder: Path, system: str, input_name: str) -> Optional[Dict[str, str]]:
    if system == "protege":
        protege = load(folder / "protege.json")
        entry = (protege or {}).get("loading", {}).get(input_name)
        if not entry:
            return None
        return {"time": seconds(entry["seconds"]) if entry.get("seconds") else entry.get("status", "–"),
                "memory": memory(entry.get("heap_increase_mib"))}
    loading = load(folder / "loading" / "loading.json")
    runs = [r for r in (loading or {}).get("runs", []) if r["system"] == system and r.get("input") == input_name]
    if not runs:
        return None
    finished = [r for r in runs if r["status"] == "ok"]
    if finished:
        # As make_tables.py: the worker's own time of loading and reasoning (and persisting, with ORMatic).
        values = [r["worker_result"].get("load_reasoning_and_persist_seconds",
                                         r["worker_result"]["load_and_reasoning_seconds"]) for r in finished]
        mean = statistics.mean(values)
        time = seconds(mean) + (f" ± {seconds(statistics.stdev(values))}" if len(values) > 1 else "")
    else:
        status = runs[0]["status"]
        limit = runs[0].get("timeout_seconds")
        time = (f"> {limit:.0f}" if status == "timeout" and limit else
                "out of memory" if status in ("memory_limit",) or runs[0].get("return_code") == -9 else status)
    peak = max(r["peak_rss_mib"] for r in finished) if finished else runs[0]["peak_rss_mib"]
    if system == "graphdb":
        heap = first(folder / "memory" / "graphdb_heap.json", folder / "memory" / "graphdb_heap" / "graphdb_heap.json")
        increase = (heap or {}).get(input_name, {}).get("heap_increase_mib")
    else:
        base = import_mib(first(folder / "memory" / "import_memory.json"), system)
        increase = peak - base if base is not None else None
    return {"time": time, "memory": memory(increase)}


def loading_table() -> Optional[Table]:
    if not (RUN / "loading" / "loading.json").exists():
        return None
    rows = []
    for system, label in LOADING_SYSTEMS:
        for input_name in ("raw", "reasoned"):
            this = loading_cells(RUN, system, input_name)
            paper = loading_cells(PAPER, system, input_name)
            if this is None and (paper is None or MODE == "quick"):
                continue
            this = this or {"time": "not run", "memory": "–"}
            paper = paper or {"time": "–", "memory": "–"}
            rows.append([label, "raw" if input_name == "raw" else "pre-reasoned", this["time"], paper["time"],
                         this["memory"], paper["memory"]])
    caption = ("Time in seconds to load the ontology and compute its consequences (mean ± standard deviation over "
               "the repetitions), from the raw data (54,901 statements) and from the pre-reasoned data (1,431,635). "
               "Memory is the increase during loading: the peak resident set size of the process tree minus that of "
               "a fresh worker after its imports; for GraphDB, the increase of its Java heap in use (GC log). "
               "\"> N\" means stopped at the time limit, \"out of memory\" at the memory limit (24 GiB for Nemo and reasonable). "
               "Nemo's time is its own data import plus reasoning, without exporting the closure; its memory includes "
               "the Python worker that starts it. Times depend on the machine; the paper's are from an Intel "
               "Core i7-13700 with 64 GB RAM. ")
    caption += ("Protégé was run by hand, once per input (protege/README.txt)." if OWN else
                "Protégé was run by hand in the paper and is not run here.")
    table = Table("Loading and reasoning (paper, Table 3)", caption,
                  ["System", "Input", "Time [s]", "Paper", "Memory", "Paper"], rows, right=[2, 3, 4, 5])
    return table.without([3, 5]) if OWN else table


# --- Queries -----------------------------------------------------------------------------------------------------

def query_means(summary: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    means: Dict[str, Dict[str, float]] = {}
    for framework, run in (summary or {}).get("frameworks", {}).items():
        for number, entry in ((run.get("result") or {}).get("queries") or {}).items():
            if entry.get("status") == "ok" and entry.get("mean_ms") is not None:
                means.setdefault(framework, {})[number] = entry["mean_ms"]
    return means


def query_table() -> Optional[Table]:
    summary = load(RUN / "queries" / "queries.json")
    repetitions_note = ""
    if summary is None:
        summary = load(RUN / "reference_check" / "queries.json")
        repetitions_note = (" In quick mode, each query runs once, so the times include the first run's warm-up "
                            "and are not comparable with the paper's means over 10 runs.")
    if summary is None:
        return None
    this, paper = query_means(summary), query_means(load(PAPER / "queries" / "queries.json"))
    present = [(key, label) for key, label in QUERY_FRAMEWORKS if key in this]
    counts = (load(RUN / "check" / "answer_check.json") or load(RUN / "reference_check" / "answer_check.json")
              or {"queries": {}})["queries"]
    numbers = sorted({n for values in this.values() for n in values}, key=int)
    rows = []
    for number in numbers:
        reference = next((c["reference"] for c in counts.get(number, {}).values() if "reference" in c), None)
        cells = [milliseconds(this[key][number]) if number in this[key] else "–" for key, _ in present]
        rows.append([f"Q{number}", f"{reference:,}" if reference is not None else "–", *cells])
    common = [n for n in numbers if all(n in this[key] and n in paper.get(key, {}) for key, _ in present)]
    geometric = lambda values: math.exp(statistics.mean(math.log(max(v, 1e-6)) for v in values)) if values else None
    for label, source in (("Geom. mean", this),) + ((("Geom. mean, paper", paper),) if not OWN else ()):
        values = [geometric([source[key][n] for n in common]) if key in source else None for key, _ in present]
        rows.append([label, "", *[milliseconds(v) if v is not None else "–" for v in values]])
    caption = (f"Query times in milliseconds on the loaded data (mean over the repetitions of this run): EQL over "
               f"the objects in working memory, SQL (SQLAlchemy) over the objects that ORMatic persisted in "
               f"PostgreSQL, the others over their own stores. \"Answers\" is the number of GraphDB's answers. The "
               f"geometric means are over the {len(common)} queries that every listed system completed, in this "
               f"run{'' if OWN else ' and in the paper' + chr(39) + 's run'}.{repetitions_note}")
    return Table("Query times (paper, Table 4)", caption, ["Query", "Answers", *[l for _, l in present]], rows,
                 right=list(range(1, 2 + len(present))))


# --- Ablation ----------------------------------------------------------------------------------------------------

def scaling_table() -> Optional[Table]:
    paper: Dict[int, List[str]] = {}
    text = PAPER / "ablation_scaling" / "scaling.txt"
    if text.exists():
        for line in text.read_text().splitlines():
            parts = line.split()
            if len(parts) == 6 and parts[0] == "chain" and parts[1].isdigit():
                paper[int(parts[1])] = parts
    rows_this = load(RUN / "ablation" / "scaling.json")
    if not rows_this and OWN:
        rows_this = [{"n": n, "seconds": float(parts[2]), "attempts": int(parts[3]), "facts": int(parts[4]),
                      "complete": parts[5] == "yes"} for n, parts in sorted(paper.items())]
    if not rows_this:
        return None
    rows = [[str(r["n"]), seconds(r["seconds"]), f"{r['attempts']:,}", f"{r['facts']:,}",
             "yes" if r["complete"] else "NO",
             paper[r["n"]][2] if r["n"] in paper else "–",
             f"{int(paper[r['n']][3]):,}" if r["n"] in paper else "–"] for r in rows_this]
    caption = ("Eager chaining (the ablation \"KRROOD without step 5\") on the OWL2Bench TBox plus n persons who share "
               "a home town, linked in a chain: load time, attempts to add a fact, facts (n², everyone with everyone) "
               "and whether the closure is complete. The attempts grow about 8-fold per doubling of n, i.e. cubically; "
               "OWL2Bench's largest such group has 1,145 persons, which explains why the ablation does not finish "
               "within two hours on the benchmark (Table 3).")
    table = Table("Why the ablation does not finish: eager chaining on small data", caption,
                  ["n", "Time [s]", "Attempts", "Facts", "Complete", "Time, paper", "Attempts, paper"], rows,
                  right=[0, 1, 2, 3, 5, 6])
    return table.without([5, 6]) if OWN else table


# --- Agent loop --------------------------------------------------------------------------------------------------

AGENT_LOOP_VARIANTS = [("krrood", "KRROOD (scan)"), ("krrood_navigation", "KRROOD (navigation)"),
                       ("graphdb", "GraphDB (mirror)"), ("graphdb_push", "GraphDB (push)"),
                       ("reasonable", "reasonable (recompute)")]


def agent_loop_table() -> Optional[Table]:
    loop = load(RUN / "agent_loop" / "agent_loop.json")
    if not loop:
        return None
    paper = load(PAPER / "agent_loop" / "agent_loop.json") or {}
    rows = []
    ms = lambda summary: f"{summary['median'] * 1000:.1f} / {summary['p95'] * 1000:.0f}"
    for name, label in AGENT_LOOP_VARIANTS:
        variant = loop["variants"].get(name)
        if not variant:
            continue
        steps, phases = variant["steps"], variant["steps"]["phases"]
        # At most one of the two is not zero: reasonable reasons after the update, GraphDB (push) pushes after it.
        after = phases["push"] if phases["push"]["total"] else phases["reasoning"]
        agreement = variant.get("agreement")
        agrees = ("reference" if not agreement else
                  f"{agreement['equal_actions']}/{agreement['steps_compared']} actions, "
                  f"{agreement['equal_candidate_sets']}/{agreement['steps_compared']} candidate sets")
        paper_variant = paper.get("variants", {}).get(name)
        rows.append([label, seconds(variant["setup"]["total_seconds"]), ms(steps["total_seconds"]), ms(phases["update"]),
                     ms(after) if after["total"] else "–", ms(phases["query"]), f"{steps['statements_inserted']['mean'] + steps['statements_deleted']['mean']:.1f}",
                     f"{steps['round_trips']['mean']:.0f}", str(variant["code"]["boundary_lines"]["total"]), agrees,
                     ms(paper_variant["steps"]["total_seconds"]) if paper_variant else "–"])
    caption = (f"The delivery robot on the OWL2Bench campus, {loop['arguments']['steps']} steps (seed "
               f"{loop['arguments']['seed']}). Each step perceives 3 additions (an enrolment, a course taken, a new "
               "T20 cricket fan), decides with two queries that need inferred facts and call the robot's path planner "
               "(handouts to students of a college, tickets to T20 cricket fans), and acts. Times in ms, median / 95th "
               "percentile. \"Update\": asserting the perceived facts, with KRROOD's and GraphDB's inference; "
               "\"reasoning / push\": reasonable's materialization, or GraphDB (push) writing the planner's results "
               "into the store. \"Written\": statements inserted plus deleted per step; \"boundary code\": lines of code "
               "that only synchronize, map identifiers to objects or connect the planner to the queries. The other "
               "variants carry out KRROOD's actions; \"agrees\" compares their own decisions and candidates with "
               "KRROOD's. reasonable 0.4.4 derives no property chains, so it finds no member of a college and no "
               "handout candidate. Removals are not perceived, as KRROOD does not retract inferred facts.")
    table = Table("Agent loop: a delivery robot that perceives, reasons with its own procedures and acts", caption,
                  ["Variant", "Setup [s]", "Step [ms]", "Update [ms]", "Reasoning / push [ms]", "Query [ms]", "Written", "Round trips",
                   "Boundary code", "Agrees with KRROOD", "Step, paper"], rows, right=[1, 2, 3, 4, 5, 6, 7, 8])
    return table.without([10]) if OWN else table


def agent_loop_seeds_table() -> Optional[Table]:
    seeds = load(RUN / "agent_loop" / "agent_loop_seeds.json")
    if not seeds:
        return None
    rows = []
    for name, label in AGENT_LOOP_VARIANTS:
        variant = seeds["variants"].get(name)
        if not variant:
            continue
        interval = variant["median_step_ms_95ci"]
        per_step = variant["median_per_step"]
        agrees = ("reference" if variant["equal_actions"] is None
                  else f"{variant['equal_actions']}/{variant['steps_compared']}")
        rows.append([label, ", ".join(map(str, variant["seeds"])), str(variant["steps"]),
                     f"{variant['median_step_ms']:.1f}",
                     f"{interval[0]:.1f}-{interval[1]:.1f}" if interval else "–",
                     "-".join(f"{x:.1f}" for x in (min(variant["per_seed_median_step_ms"]),
                                                   max(variant["per_seed_median_step_ms"]))),
                     f"{variant['median_phase_ms']['update']:.2f}", f"{variant['median_phase_ms']['query']:.1f}",
                     f"{per_step['round_trips']:.0f}",
                     (f"0 ({per_step['statements_inserted']:.0f} assigned)" if name.startswith("krrood")
                      else f"{per_step['statements_inserted'] + per_step['statements_deleted']:.0f}"),
                     "/".join(str(variant["boundary_lines"]["per_category"][c])
                              for c in ("synchronization", "mapping", "procedure_integration")), agrees])
    caption = ("The agent loop over all seeds (scripts/aamas27/aggregate_agent_loop_seeds.py): medians over all steps of "
               "all seeds, a 95% bootstrap interval of the median step (seeds resampled, then steps), the range of the "
               "seeds' medians, the median update and query phases, round trips and statements written to another store "
               "per step, boundary lines (synchronization/mapping/procedure integration), and the steps in which the "
               "variant took KRROOD's action.")
    return Table("Agent loop over five seeds (paper, Section 7.4)", caption,
                 ["Variant", "Seeds", "Steps", "Step [ms]", "95% interval", "Seed medians", "Update [ms]", "Query [ms]",
                  "Round trips", "Written", "Boundary lines", "Same action"], rows, right=[2, 3, 4, 5, 6, 7, 8, 9])


# --- Query size ----------------------------------------------------------------------------------------------------

def query_size_table() -> Optional[Table]:
    sizes = load(RUN / "query_size.json")
    if not sizes:
        return None
    rows = [[f"Q{r['query']}", str(r["sparql"]), str(r["eql"] - r["eql_domain_none"]), str(r["eql"]),
             str(r["sqlalchemy"])] for r in sizes["queries"]]
    summary = sizes["summary"]
    for label, key in (("Total", "total"), ("Geometric mean", "geometric_mean")):
        rows.append([label, *(f"{summary[name][key]:.1f}" if key == "geometric_mean" else str(summary[name][key])
                              for name in ("sparql", "eql_without_domain_none", "eql", "sqlalchemy"))])
    caption = ("Lexical tokens of each benchmark query as the benchmark code writes it (tools/query_size.py): SPARQL "
               "without its PREFIX declarations; EQL and SQLAlchemy as the Python statements that build the query. "
               "\"EQL\" counts domain=None, which the version of KRROOD of the experiments needs and the current one "
               "does not; \"EQL without domain=None\" omits it. The EQL queries are longer than SPARQL's on every "
               "query, mostly because every variable is declared with its class; they are shorter than SQLAlchemy's "
               "on Q2, Q4, Q9, Q21 and Q22, where SQLAlchemy names join tables, keys or conditions on columns. Size "
               "says nothing about how easy a query is to read or to get right; the paper makes no claim about it.")
    return Table("Query size in EQL, SPARQL and SQLAlchemy (supplement only)", caption,
                 ["Query", "SPARQL", "EQL without domain=None", "EQL", "SQLAlchemy"], rows, right=[1, 2, 3, 4])


# --- Skipped steps -------------------------------------------------------------------------------------------------

def skipped_table() -> Optional[Table]:
    path = RUN / "skipped.txt"
    if not path.exists() or not path.read_text().strip():
        return None
    rows = [line.split("|", 1) for line in path.read_text().splitlines() if "|" in line]
    return Table("Steps not run", "What this run did not do, and why. A step skipped for want of a GraphDB license "
                 "runs when the same command is called again with one; finished steps are not repeated.",
                 ["Step", "Why"], rows)


def main() -> None:
    width = shutil.get_terminal_size((100, 40)).columns
    bundle = (RUN / "BUNDLE").read_text().strip() if (RUN / "BUNDLE").exists() else "?"
    graphdb = (RUN / "graphdb_used").exists()
    tables = [t for t in (test_table(), answer_table(), audit_table(), baseline_closure_table(), loading_table(), query_table(),
                          scaling_table(), agent_loop_table(), agent_loop_seeds_table(), query_size_table(), skipped_table()) if t]
    skipped = (RUN / "skipped.txt").read_text() if (RUN / "skipped.txt").exists() else ""
    title = f"KRROOD supplementary material: results of mode {MODE}"
    intro = [f"Bundle {bundle}, {datetime.now().astimezone():%Y-%m-%d %H:%M %Z}. GraphDB: "
             f"{'used' if graphdb else 'not needed in quick mode' if MODE == 'quick' else 'not used, as no license was given'}. "
             f"All results: {RUN} (on the host: ./state/results/aamas27/run). "
             "The paper's numbers are those of our run, in results/ of the bundle."]
    if MODE == "paper":
        title = "KRROOD supplementary material: results of the paper's run"
        intro = [f"Bundle {bundle} (code/earlier as in this bundle), Intel Core i7-13700, 64 GB RAM, Ubuntu 24.04. "
                 "These are the numbers in the paper; a run of this bundle writes the same report with its own numbers "
                 "next to them. See provenance.txt for which numbers come from which run."]
    if MODE == "quick":
        intro.append("Quick mode checks correctness without GraphDB and measures KRROOD's loading. "
                     "'full' (or 'all') runs everything in the paper, 9-13 h.")
    terminal = ["", "=" * min(width, 100), title, "=" * min(width, 100)]
    terminal += [line for paragraph in intro for line in textwrap.wrap(paragraph, min(width, 100))]
    markdown = [f"# {title}", "", *intro, ""]
    for table in tables:
        terminal += ["", table.terminal(min(width, 120))]
        markdown += [table.markdown(), ""]
    if "license" in skipped.lower():
        help_lines = textwrap.wrap("How to get a GraphDB license: " + LICENSE_HELP, min(width, 100))
        terminal += ["", *help_lines]
        markdown += ["## How to get a GraphDB license", "", LICENSE_HELP, ""]
    OUTPUT.write_text("\n".join(markdown) + "\n")
    terminal += ["", f"This report is also in {OUTPUT} (on the host: ./state/results/{OUTPUT.name}).", ""]
    print("\n".join(terminal))


if __name__ == "__main__":
    main()
