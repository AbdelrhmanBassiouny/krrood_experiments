#!/usr/bin/env bash
# Run every automated AAMAS 2027 OWL2Bench experiment of RUNBOOK_AAMAS27.md on this machine with one command:
# code and Python environment, PostgreSQL and GraphDB, the data files, the tests, the answer-set check, query timing,
# loading + reasoning, the ablation, the LaTeX tables and the results archive. Only Protégé (runbook section 7) stays
# manual.
#
# Usage:
#   bash scripts/aamas27/run_all.sh          # all steps; a second call resumes after the last finished step
#   bash scripts/aamas27/run_all.sh tables   # only the tables and the archive (after adding protege.json)
#
# Settings (environment variables, defaults in brackets):
#   AAMAS27_RUN            results directory [results/aamas27/<hostname>-run]
#   AAMAS27_CRAM_DIR       CRAM clone [~/cram_aamas27]
#   AAMAS27_RDR_DIR        ripple_down_rules clone [~/ripple_down_rules_aamas27]
#   AAMAS27_VENV           virtual environment [~/venvs/krrood_aamas27]
#   AAMAS27_PYTHON         interpreter for a new virtual environment [python3.12]
#   GRAPHDB_APP            GraphDB Desktop application directory [/opt/graphdb-desktop/lib/app]
#   GRAPHDB_JAVA           Java of GraphDB [/opt/graphdb-desktop/lib/runtime/bin/java]
#   GRAPHDB_HOME_DIR       GraphDB home [~/.graphdb]
#   GRAPHDB_HEAP           GraphDB maximum heap [8g]
#   GRAPHDB_PORT           GraphDB port [7200]
#   POSTGRES_PORT          PostgreSQL port of the container [5432]
#   QUERY_REPETITIONS      [10]   LOADING_REPETITIONS [5]
set -euo pipefail

EXPERIMENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CRAM_DIR="${AAMAS27_CRAM_DIR:-$HOME/cram_aamas27}"
RDR_DIR="${AAMAS27_RDR_DIR:-$HOME/ripple_down_rules_aamas27}"
VENV="${AAMAS27_VENV:-$HOME/venvs/krrood_aamas27}"
PYTHON="${AAMAS27_PYTHON:-python3.12}"
RUN="${AAMAS27_RUN:-$EXPERIMENTS_DIR/results/aamas27/$(hostname)-run}"
GRAPHDB_APP="${GRAPHDB_APP:-/opt/graphdb-desktop/lib/app}"
GRAPHDB_JAVA="${GRAPHDB_JAVA:-/opt/graphdb-desktop/lib/runtime/bin/java}"
GRAPHDB_HOME_DIR="${GRAPHDB_HOME_DIR:-$HOME/.graphdb}"
GRAPHDB_HEAP="${GRAPHDB_HEAP:-8g}"
GRAPHDB_PORT="${GRAPHDB_PORT:-7200}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
QUERY_REPETITIONS="${QUERY_REPETITIONS:-10}"
LOADING_REPETITIONS="${LOADING_REPETITIONS:-5}"
BRANCH=aamas27-experiments
RDR_COMMIT=3b994bb
POSTGRES_CONTAINER=krrood-pg
RAW_FILE=resources/owl2bench_statements_unreasoned.rdf
REASONED_FILE=resources/owl2bench_statements_reasoned.rdf

mkdir -p "$RUN"
exec > >(tee -a "$RUN/run_all.log") 2>&1
cd "$EXPERIMENTS_DIR"

log() { printf '\n[%s] %s\n' "$(date '+%F %T')" "$*"; }
fail() { log "STOPPED: $*"; exit 1; }
done_marker() { echo "$RUN/.done-$1"; }
is_done() { [[ -f "$(done_marker "$1")" ]]; }
mark_done() { date '+%F %T' > "$(done_marker "$1")"; }

# Runs a step unless it finished in an earlier call; a step that did not finish starts over.
step() {
    local name="$1"; shift
    if is_done "$name"; then
        log "skip $name (finished $(cat "$(done_marker "$name")"))"
        return
    fi
    log "start $name"
    "$@"
    mark_done "$name"
    log "finished $name"
}

check_prerequisites() {
    command -v "$PYTHON" >/dev/null || [[ -x "$VENV/bin/python" ]] || fail "$PYTHON not found (set AAMAS27_PYTHON)"
    command -v docker >/dev/null || fail "docker not found"
    docker info >/dev/null 2>&1 || fail "docker is not usable by $(whoami) (add the user to the docker group)"
    command -v java >/dev/null || fail "java not found (owlready2 starts Pellet with the java on the PATH)"
    command -v curl >/dev/null || fail "curl not found"
    if ! graphdb_is_up; then
        [[ -d "$GRAPHDB_APP" && -x "$GRAPHDB_JAVA" ]] || fail "GraphDB is not running on port $GRAPHDB_PORT and \
$GRAPHDB_APP was not found (set GRAPHDB_APP and GRAPHDB_JAVA, or start GraphDB yourself)"
    fi
    if pgrep -f "graphdb-desktop/lib/app" >/dev/null && ! graphdb_is_up; then
        fail "GraphDB Desktop seems to run on another port; close it first"
    fi
}

update_repository() {
    local directory="$1" url="$2"
    if [[ ! -d "$directory/.git" && ! -f "$directory/.git" ]]; then
        git clone --branch "$BRANCH" "$url" "$directory"
    else
        git -C "$directory" diff --quiet || fail "$directory has uncommitted changes"
        git -C "$directory" fetch origin "$BRANCH"
        git -C "$directory" checkout -q "$BRANCH" 2>/dev/null \
            || git -C "$directory" checkout -q -b "$BRANCH" "origin/$BRANCH"
        git -C "$directory" merge -q --ff-only "origin/$BRANCH"
    fi
}

get_code() {
    git -C "$EXPERIMENTS_DIR" diff --quiet || fail "$EXPERIMENTS_DIR has uncommitted changes"
    update_repository "$CRAM_DIR" https://github.com/AbdelrhmanBassiouny/cognitive_robot_abstract_machine.git
    if [[ ! -d "$RDR_DIR/.git" ]]; then
        git clone https://github.com/AbdelrhmanBassiouny/ripple_down_rules.git "$RDR_DIR"
    fi
    git -C "$RDR_DIR" checkout -q "$RDR_COMMIT"
    log "experiments $(git -C "$EXPERIMENTS_DIR" log -1 --format='%h %s')"
    log "CRAM        $(git -C "$CRAM_DIR" log -1 --format='%h %s')"
    log "rdr         $(git -C "$RDR_DIR" log -1 --format='%h %s')"
}

python_environment() {
    [[ -x "$VENV/bin/python" ]] || "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install -q --upgrade pip
    "$VENV/bin/pip" install -q -e "$CRAM_DIR/krrood" -e "$RDR_DIR" -e "$EXPERIMENTS_DIR"
    "$VENV/bin/pip" install -q -r "$EXPERIMENTS_DIR/scripts/aamas27/requirements-aamas27.txt"
    local location
    location="$("$VENV/bin/python" -c 'import krrood, ripple_down_rules; from ripple_down_rules import RDRDecorator; print(krrood.__file__)')"
    [[ "$location" == "$CRAM_DIR"* ]] || fail "krrood is imported from $location, not from $CRAM_DIR"
}

activate() {
    unset PYTHONPATH
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
    export KRROOD_GRAPHDB_URL="http://localhost:$GRAPHDB_PORT"
    export KRROOD_EXPERIMENTS_DATABASE_URI="postgresql+psycopg2://krrood_experiments:krrood_experiments@localhost:$POSTGRES_PORT/krrood_experiments"
}

start_postgres() {
    if [[ "$(docker inspect -f '{{.State.Running}}' "$POSTGRES_CONTAINER" 2>/dev/null)" == "true" ]]; then
        log "PostgreSQL container $POSTGRES_CONTAINER is running"
    elif docker inspect "$POSTGRES_CONTAINER" >/dev/null 2>&1; then
        docker start "$POSTGRES_CONTAINER" >/dev/null
    else
        docker run -d --name "$POSTGRES_CONTAINER" -e POSTGRES_USER=krrood_experiments \
            -e POSTGRES_PASSWORD=krrood_experiments -e POSTGRES_DB=krrood_experiments \
            -p "127.0.0.1:$POSTGRES_PORT:5432" --shm-size=256m postgres:18.1 >/dev/null
    fi
    for _ in $(seq 60); do
        docker exec "$POSTGRES_CONTAINER" pg_isready -U krrood_experiments -d krrood_experiments >/dev/null 2>&1 \
            && return
        sleep 2
    done
    fail "PostgreSQL did not become ready"
}

graphdb_is_up() { curl -sf "http://localhost:$GRAPHDB_PORT/rest/info/version" >/dev/null; }

STARTED_GRAPHDB_PID=""
start_graphdb() {
    if graphdb_is_up; then
        log "GraphDB is running on port $GRAPHDB_PORT"
        return
    fi
    local license=()
    [[ -f "$GRAPHDB_HOME_DIR/work/graphdb.license" ]] \
        && license=("-Dgraphdb.license.file=$GRAPHDB_HOME_DIR/work/graphdb.license")
    nohup "$GRAPHDB_JAVA" -Xms1g "-Xmx$GRAPHDB_HEAP" -Djava.awt.headless=true \
        --add-exports jdk.management.agent/jdk.internal.agent=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED \
        --enable-native-access=ALL-UNNAMED -cp "$GRAPHDB_APP/lib/*" "-Dgraphdb.dist=$GRAPHDB_APP" \
        "-Dgraphdb.home=$GRAPHDB_HOME_DIR" "-Dgraphdb.connector.port=$GRAPHDB_PORT" "${license[@]}" \
        com.ontotext.graphdb.server.GraphDBWorkbench > "$RUN/graphdb.log" 2>&1 &
    STARTED_GRAPHDB_PID=$!
    for _ in $(seq 120); do
        graphdb_is_up && { log "GraphDB started (pid $STARTED_GRAPHDB_PID, heap $GRAPHDB_HEAP)"; return; }
        sleep 2
    done
    fail "GraphDB did not start, see $RUN/graphdb.log"
}

stop_services() {
    if [[ -n "$STARTED_GRAPHDB_PID" ]]; then
        kill "$STARTED_GRAPHDB_PID" 2>/dev/null || true
        log "stopped GraphDB"
    fi
    docker stop "$POSTGRES_CONTAINER" >/dev/null 2>&1 && log "stopped PostgreSQL container" || true
}

explicit_statements() {
    python scripts/aamas27/graphdb_setup.py --status | python -c "
import json, sys
print(json.load(sys.stdin)['repositories'].get('$1', {}).get('explicit', 0))"
}

prepare_data() {
    if [[ "$(explicit_statements aamas27_rl)" != 54901 ]]; then
        log "loading the raw data into aamas27_rl (OWL 2 RL materialisation, 30-45 min)"
        python scripts/aamas27/graphdb_setup.py --delete aamas27_rl 2>/dev/null || true
        python scripts/aamas27/graphdb_setup.py --create aamas27_rl owl2-rl-optimized --load aamas27_rl "$RAW_FILE"
    fi
    if [[ ! -f "$REASONED_FILE" ]] || ! grep -q T20CricketFan "$REASONED_FILE"; then
        [[ -f "$REASONED_FILE" ]] && mv "$REASONED_FILE" "${REASONED_FILE%.rdf}_old_$(date +%s).rdf"
        python scripts/aamas27/graphdb_setup.py --export-reasoned "$REASONED_FILE"
    fi
    if [[ "$(explicit_statements aamas27_noinf)" == 0 ]]; then
        python scripts/aamas27/graphdb_setup.py --setup-query-repositories
    fi
    python scripts/aamas27/graphdb_setup.py --status | tee "$RUN/graphdb_status.json"
    [[ "$(explicit_statements aamas27_rl)" == 54901 ]] || fail "aamas27_rl does not hold the 54901 raw statements"
    [[ "$(explicit_statements aamas27_noinf)" -gt 1400000 ]] || fail "aamas27_noinf is not loaded"
    sha256sum resources/*.rdf > "$RUN/checksums.txt"
}

run_tests() { python -m pytest -q -o addopts="" tests/aamas27; }

answer_check() {
    rm -rf "$RUN/check"
    python scripts/aamas27/run_queries.py --check-only --results-dir "$RUN/check" \
        || fail "an answer set differs from GraphDB, see $RUN/check/answer_check.json"
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
    [[ "$1" == rdflib_owlrl ]] && extra=(--rdflib-timeout-seconds 10800)
    python scripts/aamas27/run_loading.py --systems "$1" --repetitions "$LOADING_REPETITIONS" "${extra[@]}" \
        --results-dir "$RUN/loading"
}

ablation() {
    forget_loading_runs krrood_eager_symmetric_transitive
    python scripts/aamas27/run_symmetric_transitive_ablation.py --memory-limit-gib 24 --results-dir "$RUN/loading"
}

tables_and_archive() {
    local protege=()
    if [[ -f "$RUN/protege.json" ]]; then
        protege=(--protege "$RUN/protege.json")
    else
        log "no $RUN/protege.json yet: the tables have no Protégé rows (runbook section 7, then run: $0 tables)"
    fi
    local inputs=()
    [[ -f "$RUN/loading/loading.json" ]] && inputs+=(--loading "$RUN/loading/loading.json")
    [[ -f "$RUN/queries/queries.json" ]] && inputs+=(--queries "$RUN/queries/queries.json")
    [[ ${#inputs[@]} -gt 0 ]] || fail "no results to tabulate yet"
    python scripts/aamas27/make_tables.py "${inputs[@]}" "${protege[@]}" --output-dir "$RUN/tables"
    local archive="$EXPERIMENTS_DIR/aamas27_results_$(hostname).tgz"
    tar czf "$archive" -C "$(dirname "$RUN")" "$(basename "$RUN")" $(ls "$HOME"/protege_*_time.txt 2>/dev/null)
    log "results archive: $archive"
}

main() {
    if [[ "${1:-all}" == tables ]]; then
        activate
        tables_and_archive
        return
    fi
    log "AAMAS 2027 experiments, results in $RUN"
    check_prerequisites
    get_code
    python_environment
    activate
    trap stop_services EXIT
    start_postgres
    start_graphdb
    step data prepare_data
    step tests run_tests
    step answer_check answer_check
    step query_timing query_timing
    for system in krrood owlready2_pellet rdflib_owlrl graphdb krrood_ormatic; do
        step "loading_$system" loading_system "$system"
    done
    step ablation ablation
    tables_and_archive
    log "all automated steps finished. Remaining: Protégé (RUNBOOK_AAMAS27.md section 7), then: $0 tables"
}

main "$@"
