#!/usr/bin/env bash
# Runs the experiments of the paper inside the container (see README.md).
#
#   quick     (the default) the test suites, the paper's listings, the ablation on small data, the answers of EQL
#             and SQL compared with the answers GraphDB gave in the paper's run, and the loading time and
#             memory of KRROOD and of Nemo from the raw data (about 10 min; no GraphDB license needed)
#   check     the correctness part of the paper (Section 7.1): with a GraphDB license, the answers of all systems
#             compared with a live GraphDB, and KRROOD's knowledge base compared with GraphDB's OWL 2 RL closure
#             (about 1-1.5 h); without one, as quick
#   full      everything in the paper (Sections 7.1-7.3, about 9-13 h); "all" is the same. Without a GraphDB
#             license, the steps that need GraphDB are skipped and listed in the report
#   listings  only the tests of the paper's listings and of the formalization's examples
#   tables    the LaTeX tables, the report and the results archive, e.g. after adding protege.json (README.md)
#   report    only the report of the results so far
#   fingerprint  the fingerprint of the code in the image; equals environment/BUNDLE of the bundle it was built from
#
# Everything is written to /state (./state on the host); the report also to ./state/results/REPORT.md. In check and
# full, a second call resumes after the last finished step.
set -euo pipefail

MODE="${1:-quick}"
[[ "$MODE" == all ]] && MODE=full
TOOLS=/opt/aamas27/tools
PAPER_RESULTS=/paper_results      # results/ of the bundle (compose.yaml mounts it): the numbers of the paper's run
REPORT=/state/results/REPORT.md
EXPERIMENTS=/opt/aamas27/code/earlier/experiments
RUN=/state/results/aamas27/run
GRAPHDB_HEAP="${GRAPHDB_HEAP:-8g}"
QUERY_REPETITIONS="${QUERY_REPETITIONS:-10}"
LOADING_REPETITIONS="${LOADING_REPETITIONS:-5}"
RDFLIB_TIMEOUT_SECONDS="${RDFLIB_TIMEOUT_SECONDS:-10800}"
ABLATION_TIMEOUT_SECONDS="${ABLATION_TIMEOUT_SECONDS:-7200}"
BASELINE_MEMORY_LIMIT_GIB="${BASELINE_MEMORY_LIMIT_GIB:-24}"
RAW_FILE=resources/owl2bench_statements_unreasoned.rdf
REASONED_FILE=resources/owl2bench_statements_reasoned.rdf

log() { printf '\n[%s] %s\n' "$(date '+%F %T')" "$*"; }
fail() { log "FAILED: $*"; exit 1; }

# Runs a test suite, keeping its output for the report when there is a results folder.
suite() {
    local name="$1"; shift
    if [[ -d "${RUN_TESTS:-}" ]]; then
        "$@" 2>&1 | tee "$RUN_TESTS/$name.log"
    else
        "$@"
    fi
}

listings() {
    log "listing tests (current version of KRROOD)"
    cd /opt/aamas27/listings
    suite listings env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /opt/venvs/current/bin/python -m pytest -q -o addopts="" \
        -p no:cacheprovider --rootdir=. test_listings.py test_formalization_examples.py
    cd ormatic
    suite ormatic_listing env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /opt/venvs/current/bin/python -m pytest -q \
        -o addopts="" -p no:cacheprovider --rootdir=. test_ormatic_listing.py
    cd "$EXPERIMENTS"
}

# The fingerprint of the code in the image, computed as make_supplement.py computes environment/BUNDLE. It shows
# whether Docker built the image from files of an earlier version of the bundle (README.md, Troubleshooting).
code_fingerprint() {
    /opt/venvs/earlier/bin/python - <<'PY'
import hashlib
import os
from pathlib import Path
root = Path("/opt/aamas27")
paths = []
# The build adds *.egg-info folders and two symbolic links into /state; the bundle has neither.
for directory, folders, files in os.walk(root / "code"):
    folders[:] = [f for f in folders if not f.endswith(".egg-info") and f != "__pycache__"]
    paths += [Path(directory, f) for f in files if not os.path.islink(os.path.join(directory, f))]
digest = hashlib.sha256()
for path in sorted(paths):
    digest.update(str(path.relative_to(root)).encode())
    digest.update(path.read_bytes())
print(digest.hexdigest()[:16])
PY
}

if [[ "$MODE" == fingerprint ]]; then
    code_fingerprint
    exit 0
fi
[[ "$(code_fingerprint)" == "$(cat /opt/aamas27/environment/BUNDLE)" ]] \
    || fail "the code in the image does not match its BUNDLE id; see Troubleshooting in README.md"

if [[ "$MODE" == listings ]]; then
    listings
    exit 0
fi

# Files written into /state belong to the owner of ./state on the host, not to the container's root user.
fix_ownership() { chown -R "$(stat -c %u:%g /state)" /state 2>/dev/null || true; }
if [[ "$(stat -c %u /state)" == 0 ]]; then
    echo "note: ./state belongs to root; create it yourself first (mkdir state) to own the results"
fi
trap fix_ownership EXIT
mkdir -p "$RUN"
exec > >(tee -a /state/reproduce.log) 2>&1
cd "$EXPERIMENTS"
# shellcheck disable=SC1091
source /opt/venvs/earlier/bin/activate
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
cp /opt/aamas27/environment/BUNDLE "$RUN/BUNDLE"
RUN_TESTS="$RUN/tests"
mkdir -p "$RUN_TESTS"

report() {
    if [[ -d "$PAPER_RESULTS" ]]; then
        # tables and report describe the results of the last run, so they take its mode.
        local mode="$MODE"
        [[ "$MODE" == tables || "$MODE" == report ]] && mode="$(cat "$RUN/mode" 2>/dev/null || echo full)"
        python "$TOOLS/report.py" "$RUN" "$PAPER_RESULTS" "$mode" "$REPORT" || log "the report could not be written"
    else
        log "no paper results mounted at $PAPER_RESULTS (compose.yaml mounts ./results); no report"
    fi
}

# In check and full, a finished step is not run again (marker files); quick always runs everything again.
done_marker() { echo "$RUN/.done-$1"; }
step() {
    local name="$1"; shift
    if [[ "$MODE" != quick && -f "$(done_marker "$name")" ]]; then
        log "skip $name (finished $(cat "$(done_marker "$name")"))"
        return
    fi
    log "start $name"
    "$@"
    [[ "$MODE" == quick ]] || date '+%F %T' > "$(done_marker "$name")"
    log "finished $name"
}

# A step that this mode would run but cannot, recorded for the report.
not_run() {
    log "SKIPPED $1: $2"
    echo "$1|$2" >> "$RUN/skipped.txt"
}

# The license mount is /dev/null when GRAPHDB_LICENSE is not set (compose.yaml), which is not a regular file.
have_license() { [[ -f /license/graphdb.license && -s /license/graphdb.license ]]; }
NO_LICENSE="no GraphDB license"

graphdb_is_up() {
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:7200/rest/info/version', timeout=5)" \
        2>/dev/null
}

# GraphDB writes a G1 GC log (one file per start), from which its heap in use while loading is measured.
start_graphdb() {
    [[ -d /license/graphdb.license ]] && fail "GRAPHDB_LICENSE names a folder, not a license file (see README.md)"
    mkdir -p /state/graphdb-home "$RUN/memory/graphdb_gc"
    GDB_HEAP_SIZE="$GRAPHDB_HEAP" \
        GDB_JAVA_OPTS="-Xlog:gc:file=$RUN/memory/graphdb_gc/gc_$(date +%Y%m%d_%H%M%S).log:time,uptime:filecount=0" \
        /opt/graphdb/dist/bin/graphdb -d -p /state/graphdb.pid \
        -Dgraphdb.home=/state/graphdb-home -Dgraphdb.license.file=/license/graphdb.license \
        -Dgraphdb.connector.port=7200 > /state/graphdb.log 2>&1
    for _ in $(seq 150); do
        graphdb_is_up && { log "GraphDB started (heap $GRAPHDB_HEAP)"; touch "$RUN/graphdb_used"; return; }
        sleep 2
    done
    fail "GraphDB did not start, see /state/graphdb.log and /state/graphdb-home/logs (a rejected license is the usual cause)"
}

stop_graphdb() {
    [[ -f /state/graphdb.pid ]] && kill "$(cat /state/graphdb.pid)" 2>/dev/null || true
}

graphdb_status() {
    python scripts/aamas27/graphdb_setup.py --status > "$RUN/graphdb_status.json" \
        || fail "GraphDB does not answer the status request"
}

explicit_statements() {
    python - "$RUN/graphdb_status.json" "$1" <<'PY'
import json, sys
repository = json.load(open(sys.argv[1]))["repositories"].get(sys.argv[2])
print("missing" if repository is None else repository.get("explicit", 0))
PY
}

prepare_data() {
    graphdb_status
    local raw_statements
    raw_statements="$(explicit_statements aamas27_rl)"
    if [[ "$raw_statements" == missing || "$raw_statements" == 0 ]]; then
        log "loading the raw data into aamas27_rl (OWL 2 RL materialization by GraphDB, 30-60 min)"
        python scripts/aamas27/graphdb_setup.py --create aamas27_rl owl2-rl-optimized --load aamas27_rl "$RAW_FILE"
    elif [[ "$raw_statements" != 54901 ]]; then
        fail "aamas27_rl holds $raw_statements explicit statements instead of 54901; remove ./state/graphdb-home"
    fi
    if [[ ! -f "$REASONED_FILE" ]] || ! grep -q T20CricketFan "$REASONED_FILE"; then
        python scripts/aamas27/graphdb_setup.py --export-reasoned "$REASONED_FILE"
    fi
    python scripts/aamas27/graphdb_setup.py --setup-query-repositories
    graphdb_status
    [[ "$(explicit_statements aamas27_rl)" == 54901 ]] || fail "aamas27_rl does not hold the 54901 raw statements"
    local reasoned_statements
    reasoned_statements="$(explicit_statements aamas27_noinf)"
    [[ "$reasoned_statements" != missing && "$reasoned_statements" -gt 1400000 ]] \
        || fail "aamas27_noinf holds $reasoned_statements statements"
    cat "$RUN/graphdb_status.json"
    sha256sum resources/*.rdf > "$RUN/checksums.txt"
}

run_tests() { suite measurement_tests python -m pytest -q -o addopts="" -p no:cacheprovider tests/aamas27; }

# The size of the benchmark's queries in EQL, SPARQL and SQLAlchemy (the supplement's README, "Query size").
query_size() {
    python "$TOOLS/query_size.py" "$EXPERIMENTS/src/krrood_experiments/owl2bench" "$RUN/query_size.json"
}

answer_check() {
    rm -rf "$RUN/check"
    python scripts/aamas27/run_queries.py --check-only --results-dir "$RUN/check" \
        || fail "an answer set differs from GraphDB, see $RUN/check/answer_check.json"
}

# Without GraphDB: EQL and SQL compared with the answer sets that GraphDB returned in the paper's run.
reference_check() {
    python "$TOOLS/queries_without_graphdb.py" --reference-answers "$PAPER_RESULTS/check/answers/graphdb" \
        --results-dir "$RUN/reference_check" --frameworks eql,sqlalchemy --repetitions 1 \
        || fail "an answer set differs from GraphDB's, see $RUN/reference_check/answer_check.json"
}

soundness_audit() {
    mkdir -p "$RUN/audit"
    python -m krrood_experiments.aamas27.soundness_audit --output "$RUN/audit/audit.json"
    python - "$RUN/audit/audit.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("individuals", d["individuals_in_reference"], d["individuals_in_krrood"])
for s in ("classes", "object_properties", "data_properties"):
    print(s, {f: sum(x[f] for x in d[s].values()) for f in ("krrood", "reference", "unsound", "missing")})
print({k: v for k, v in d["owl2_rl_check"].items() if k in ("passed", "equalities", "inconsistencies")})
PY
}

query_timing() {
    rm -rf "$RUN/queries"
    python scripts/aamas27/run_queries.py --repetitions "$QUERY_REPETITIONS" --results-dir "$RUN/queries"
}

# Without GraphDB: query times of EQL and SQL only (RDFLib and Owlready2 query the pre-reasoned data, which GraphDB
# computes); their answers are compared with GraphDB's of the paper's run.
query_timing_without_graphdb() {
    python "$TOOLS/queries_without_graphdb.py" --reference-answers "$PAPER_RESULTS/check/answers/graphdb" \
        --results-dir "$RUN/queries" --frameworks sqlalchemy,eql --repetitions "$QUERY_REPETITIONS"
}

# Removes the measurements of a system from loading.json, so that an interrupted system is measured again.
forget_loading_runs() {
    local file="$RUN/loading/loading.json"
    [[ -f "$file" ]] || return 0
    python - "$file" "$1" <<'PY'
import json, sys
path, system = sys.argv[1], sys.argv[2]
record = json.load(open(path))
record["runs"] = [run for run in record["runs"] if run["system"] != system]
json.dump(record, open(path, "w"), indent=2)
PY
}

# loading_system SYSTEM [INPUTS]: INPUTS is raw,reasoned (the default) or raw.
loading_system() {
    forget_loading_runs "$1"
    local extra=()
    [[ "$1" == rdflib_owlrl ]] && extra=(--rdflib-timeout-seconds "$RDFLIB_TIMEOUT_SECONDS")
    # The in-memory baselines exceed any memory on the pre-reasoned data; they are stopped at the ablation's limit.
    [[ "$1" == reasonable_owlrl || "$1" == nemo_owlrl ]] && extra=(--memory-limit-gib "$BASELINE_MEMORY_LIMIT_GIB")
    python scripts/aamas27/run_loading.py --systems "$1" --inputs "${2:-raw,reasoned}" \
        --repetitions "$LOADING_REPETITIONS" "${extra[@]}" --results-dir "$RUN/loading"
}

# GraphDB's loading, with a forced GC before and after each input and marks in between, from which graphdb_heap.py
# computes the increase of its heap in use from its GC log.
loading_graphdb() {
    forget_loading_runs graphdb
    local marks="$RUN/memory/graphdb_marks.txt" pid
    pid="$(cat /state/graphdb.pid)"
    : > "$marks"
    for input in raw reasoned; do
        jcmd "$pid" GC.run > /dev/null
        echo "start $input $(date +%s.%N)" >> "$marks"
        python scripts/aamas27/run_loading.py --systems graphdb --inputs "$input" --repetitions 1 \
            --results-dir "$RUN/loading"
        echo "end $input $(date +%s.%N)" >> "$marks"
        jcmd "$pid" GC.run > /dev/null
    done
    python "$TOOLS/graphdb_heap.py" "$marks" "$RUN/memory/graphdb_heap.json" "$RUN"/memory/graphdb_gc/gc_*.log
}

# The closures of the in-memory baselines (Nemo, reasonable) from the raw data, compared with GraphDB's closure as
# the knowledge base of KRROOD is (audit/audit.json).
baseline_closures() {
    local folder="$RUN/baselines" system candidates=()
    mkdir -p "$folder"
    for system in nemo_owlrl reasonable_owlrl; do
        python -m krrood_experiments.aamas27.loading_worker --system "$system" --input-file "$RAW_FILE" \
            --closure-output "$folder/$system.nt" > /dev/null
        candidates+=(--candidate "$system=$folder/$system.nt")
    done
    python -m krrood_experiments.aamas27.closure_comparison --raw "$RAW_FILE" --reference "$REASONED_FILE" \
        "${candidates[@]}" --output "$folder/closure_comparison.json"
    rm -f "$folder"/*.nt
}

# The delivery robot (README.md, "Agent loop"): VARIANTS STEPS. KRROOD's variants are the reference; the others carry
# out its actions, and their decisions and candidates are compared with KRROOD's in every step.
agent_loop() {
    [[ "$MODE" == quick ]] && rm -rf "$RUN/agent_loop"
    python scripts/aamas27/run_agent_loop.py --variants "$1" --steps "$2" --seed 0 --results-dir "$RUN/agent_loop" \
        --resume
}

import_memory() {
    mkdir -p "$RUN/memory"
    python "$TOOLS/import_memory.py" "$RUN/memory/import_memory.json"
}

ablation() {
    forget_loading_runs krrood_eager_symmetric_transitive
    python scripts/aamas27/run_symmetric_transitive_ablation.py --memory-limit-gib 24 \
        --timeout-seconds "$ABLATION_TIMEOUT_SECONDS" --results-dir "$RUN/loading"
}

# The ablation's eager chaining on small synthetic data: 9 tests, and its growth with the size of a group.
ablation_small() {
    local work="$RUN/ablation"
    rm -rf "$work" && mkdir -p "$work"
    python "$TOOLS/ablation/make_tbox.py" "$RAW_FILE" "$work/tbox.rdf"
    ABLATION_WORK="$work" suite ablation_tests python -m pytest -q -o addopts="" -p no:cacheprovider \
        --rootdir="$TOOLS/ablation" "$TOOLS/ablation/test_eager_symmetric_transitive.py"
    python "$TOOLS/ablation/scaling.py" "$work/tbox.rdf" "$work" "$@"
    rm -f "$work"/data_*.rdf
}

tables_and_archive() {
    local inputs=()
    [[ -f "$RUN/loading/loading.json" ]] && inputs+=(--loading "$RUN/loading/loading.json")
    [[ -f "$RUN/queries/queries.json" ]] && inputs+=(--queries "$RUN/queries/queries.json")
    [[ -f "$RUN/protege.json" ]] && inputs+=(--protege "$RUN/protege.json")
    if [[ ${#inputs[@]} -gt 0 ]]; then
        python scripts/aamas27/make_tables.py "${inputs[@]}" --output-dir "$RUN/tables" > /dev/null
    fi
    report
    tar czf /state/aamas27_results.tgz -C /state/results aamas27 REPORT.md -C /state reproduce.log 2>/dev/null \
        || tar czf /state/aamas27_results.tgz -C /state/results aamas27 -C /state reproduce.log
    log "results archive: ./state/aamas27_results.tgz"
}

case "$MODE" in
    tables) tables_and_archive; exit 0 ;;
    report) report; exit 0 ;;
    quick | check | full) ;;
    *) fail "unknown mode $MODE (quick, check, full or all, listings, tables, report, fingerprint)" ;;
esac

log "bundle $(cat /opt/aamas27/environment/BUNDLE), mode $MODE, results in ./state/results/aamas27/run"
rm -f "$RUN/skipped.txt" "$RUN/graphdb_used"
echo "$MODE" > "$RUN/mode"
if [[ "$MODE" != quick ]] && ! have_license; then
    log "WARNING: no GraphDB license (GRAPHDB_LICENSE is not set, or names an empty file). The steps that need
    GraphDB are skipped and listed in the report, which also says how to get a free license."
fi
# If a step fails, the report still shows what was finished.
trap 'status=$?; stop_graphdb; [[ $status == 0 ]] || report; fix_ownership' EXIT

step tests run_tests
step listings listings
step query_size query_size
if [[ "$MODE" == quick ]]; then
    step ablation_small ablation_small 8 16 32 64 128
    step reference_check reference_check
    step import_memory import_memory
    step loading_krrood_raw loading_system krrood raw
    step loading_nemo_owlrl_raw loading_system nemo_owlrl raw
    step agent_loop agent_loop krrood,krrood_navigation 20
    not_run "everything else in the paper" "quick mode; run 'full' (or 'all') for all experiments, 9-13 h"
elif have_license; then
    start_graphdb
    step data prepare_data
    step answer_check answer_check
    step soundness_audit soundness_audit
    step baseline_closures baseline_closures
else
    step reference_check reference_check
    not_run "answers of RDFLib and Owlready2" "$NO_LICENSE; they query the pre-reasoned data, which GraphDB computes"
    not_run "knowledge base vs. OWL 2 RL closure" "$NO_LICENSE; GraphDB computes the closure"
    not_run "closures of Nemo and reasonable vs. OWL 2 RL closure" "$NO_LICENSE; GraphDB computes the closure"
fi
if [[ "$MODE" == full ]]; then
    step ablation_small ablation_small 8 16 32 64 128 256
    step import_memory import_memory
    if have_license; then
        step query_timing query_timing
        for system in krrood owlready2_pellet rdflib_owlrl krrood_ormatic nemo_owlrl reasonable_owlrl; do
            step "loading_$system" loading_system "$system"
        done
        step loading_graphdb loading_graphdb
        step agent_loop agent_loop krrood,krrood_navigation,graphdb,graphdb_push,reasonable 200
    else
        step query_timing_without_graphdb query_timing_without_graphdb
        not_run "query times of GraphDB, RDFLib and Owlready2" "$NO_LICENSE"
        for system in krrood owlready2_pellet rdflib_owlrl krrood_ormatic nemo_owlrl reasonable_owlrl; do
            step "loading_${system}_raw" loading_system "$system" raw
        done
        not_run "loading from the pre-reasoned data, all systems" "$NO_LICENSE; GraphDB computes the pre-reasoned data"
        not_run "loading of GraphDB" "$NO_LICENSE"
        step agent_loop agent_loop krrood,krrood_navigation,reasonable 200
        not_run "agent loop with GraphDB (two variants)" "$NO_LICENSE"
    fi
    step ablation ablation
fi
tables_and_archive
log "finished mode $MODE"
