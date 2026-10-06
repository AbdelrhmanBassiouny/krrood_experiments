#!/usr/bin/env bash
# Runs the experiments of the paper inside the container (see README.md).
#
#   listings  the tests of the paper's listings, on the current version of KRROOD (seconds, no services)
#   check     tests, answer-set check of the 18 queries against GraphDB, and comparison of KRROOD's knowledge base
#             with GraphDB's OWL 2 RL closure, assertion by assertion (about 1-1.5 h, mostly GraphDB reasoning)
#   all       check, then query timing, loading and reasoning time and memory, the ablation and the tables
#             (about 9-13 h; RDFLib and the ablation run into their time limits)
#   tables    the LaTeX tables and the results archive, e.g. after adding protege.json (see README.md)
#
# Everything is written to /state (./state on the host). A second call resumes after the last finished step.
set -euo pipefail

MODE="${1:-check}"
EXPERIMENTS=/opt/aamas27/code/earlier/experiments
RUN=/state/results/aamas27/run
GRAPHDB_HEAP="${GRAPHDB_HEAP:-8g}"
QUERY_REPETITIONS="${QUERY_REPETITIONS:-10}"
LOADING_REPETITIONS="${LOADING_REPETITIONS:-5}"
RDFLIB_TIMEOUT_SECONDS="${RDFLIB_TIMEOUT_SECONDS:-10800}"
RAW_FILE=resources/owl2bench_statements_unreasoned.rdf
REASONED_FILE=resources/owl2bench_statements_reasoned.rdf

log() { printf '\n[%s] %s\n' "$(date '+%F %T')" "$*"; }
fail() { log "FAILED: $*"; exit 1; }

listings() {
    log "listing tests (current version of KRROOD)"
    cd /opt/aamas27/listings
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /opt/venvs/current/bin/python -m pytest -q -o addopts="" -p no:cacheprovider \
        --rootdir=. test_listings.py
    cd ormatic
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /opt/venvs/current/bin/python -m pytest -q -o addopts="" -p no:cacheprovider \
        --rootdir=. test_ormatic_listing.py
    cd "$EXPERIMENTS"
}

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

done_marker() { echo "$RUN/.done-$1"; }
step() {
    local name="$1"; shift
    if [[ -f "$(done_marker "$name")" ]]; then
        log "skip $name (finished $(cat "$(done_marker "$name")"))"
        return
    fi
    log "start $name"
    "$@"
    date '+%F %T' > "$(done_marker "$name")"
    log "finished $name"
}

graphdb_is_up() {
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:7200/rest/info/version', timeout=5)" \
        2>/dev/null
}

start_graphdb() {
    if [[ -d /license/graphdb.license ]]; then
        fail "GRAPHDB_LICENSE names a folder, not a license file (see README.md)"
    fi
    [[ -f /license/graphdb.license ]]         || fail "no GraphDB license mounted: set GRAPHDB_LICENSE to the full path of your license file (see README.md)"
    mkdir -p /state/graphdb-home
    GDB_HEAP_SIZE="$GRAPHDB_HEAP" /opt/graphdb/dist/bin/graphdb -d -p /state/graphdb.pid \
        -Dgraphdb.home=/state/graphdb-home -Dgraphdb.license.file=/license/graphdb.license \
        -Dgraphdb.connector.port=7200 > /state/graphdb.log 2>&1
    for _ in $(seq 150); do
        graphdb_is_up && { log "GraphDB started (heap $GRAPHDB_HEAP)"; return; }
        sleep 2
    done
    fail "GraphDB did not start, see /state/graphdb.log and /state/graphdb-home/logs"
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

run_tests() { python -m pytest -q -o addopts="" -p no:cacheprovider tests/aamas27; }

answer_check() {
    rm -rf "$RUN/check"
    python scripts/aamas27/run_queries.py --check-only --results-dir "$RUN/check" \
        || fail "an answer set differs from GraphDB, see $RUN/check/answer_check.json"
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

loading_system() {
    forget_loading_runs "$1"
    local extra=()
    [[ "$1" == rdflib_owlrl ]] && extra=(--rdflib-timeout-seconds "$RDFLIB_TIMEOUT_SECONDS")
    python scripts/aamas27/run_loading.py --systems "$1" --repetitions "$LOADING_REPETITIONS" "${extra[@]}" \
        --results-dir "$RUN/loading"
}

ablation() {
    forget_loading_runs krrood_eager_symmetric_transitive
    python scripts/aamas27/run_symmetric_transitive_ablation.py --memory-limit-gib 24 --results-dir "$RUN/loading"
}

tables_and_archive() {
    local inputs=()
    [[ -f "$RUN/loading/loading.json" ]] && inputs+=(--loading "$RUN/loading/loading.json")
    [[ -f "$RUN/queries/queries.json" ]] && inputs+=(--queries "$RUN/queries/queries.json")
    [[ -f "$RUN/protege.json" ]] && inputs+=(--protege "$RUN/protege.json")
    if [[ ${#inputs[@]} -gt 0 ]]; then
        python scripts/aamas27/make_tables.py "${inputs[@]}" --output-dir "$RUN/tables"
    fi
    tar czf /state/aamas27_results.tgz -C /state/results aamas27 -C /state reproduce.log
    log "results archive: ./state/aamas27_results.tgz"
}

case "$MODE" in
    tables)
        tables_and_archive
        exit 0
        ;;
    check | all) ;;
    *) fail "unknown mode $MODE (listings, check, all, tables)" ;;
esac

log "bundle $(cat /opt/aamas27/environment/BUNDLE), mode $MODE, results in ./state/results/aamas27/run"
trap 'stop_graphdb; fix_ownership' EXIT
start_graphdb
step data prepare_data
step tests run_tests
step listings listings
step answer_check answer_check
step soundness_audit soundness_audit
if [[ "$MODE" == all ]]; then
    step query_timing query_timing
    for system in krrood owlready2_pellet rdflib_owlrl graphdb krrood_ormatic; do
        step "loading_$system" loading_system "$system"
    done
    step ablation ablation
fi
tables_and_archive
log "finished mode $MODE"
