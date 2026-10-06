#!/usr/bin/env bash
# Sets up Docker on this PC (Ubuntu 24.04), builds the supplementary bundle and starts the measured run of the
# AAMAS 2027 experiments. Safe to call again: it skips what is already done and never starts a second run.
#
# Usage:
#   bash pc_run.sh             install Docker if needed, unzip and build the bundle, run the listing tests,
#                              then start the full run in the background (about 9-13 h)
#   bash pc_run.sh status      is the run going, which steps finished, and the end of its log
#   bash pc_run.sh tables      after saving protege.json: rebuild the tables and the results archive
#   bash pc_run.sh --dry-run   everything except starting the run
#
# Settings (environment variables):
#   AAMAS27_ZIP       the bundle zip [~/krrood-aamas27-supplement.zip, else the newest in ~/Downloads]
#   GRAPHDB_LICENSE   GraphDB license file [~/.graphdb/work/graphdb.license, else searched in ~ and /opt]
#   AAMAS27_PARENT    where the bundle is unzipped [~]
set -euo pipefail

MODE="${1:-start}"
PARENT="${AAMAS27_PARENT:-$HOME}"
BUNDLE="$PARENT/krrood-aamas27-supplement"
LOG="$HOME/aamas27_run.log"
RUN_MODE="${AAMAS27_RUN_MODE:-all}"   # only changed to test this script
PROJECT=krrood-aamas27-supplement

say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

run_is_going() {
    command -v docker >/dev/null && docker ps -q --filter "label=com.docker.compose.project=$PROJECT" \
        --filter "label=com.docker.compose.service=experiments" 2>/dev/null | grep -q .
}

# --- 1. Docker ---------------------------------------------------------------------------------------------
install_docker() {
    if ! command -v docker >/dev/null || ! docker compose version >/dev/null 2>&1; then
        say "Installing Docker from Ubuntu's packages (asks for your password)"
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose-v2
    fi
    if ! systemctl is-active --quiet docker; then
        say "Starting the Docker service"
        sudo systemctl enable --now docker
    fi
    if ! getent group docker | cut -d: -f4 | tr ',' '\n' | grep -qx "$USER"; then
        say "Adding $USER to the docker group"
        sudo usermod -aG docker "$USER"
    fi
    if ! docker info >/dev/null 2>&1; then
        # The group change applies only to new logins: continue in a shell that has the group.
        if [[ -z "${AAMAS27_IN_SG:-}" ]]; then
            say "Continuing with the docker group active (no need to log out)"
            exec env AAMAS27_IN_SG=1 sg docker -c "bash $(printf '%q' "$0") $(printf '%q ' "$@")"
        fi
        die "Docker still says permission denied. Log out and back in (or reboot), then run this script again."
    fi
    docker compose version
}

# --- 2. License, zip, disk ------------------------------------------------------------------------------
find_license() {
    LICENSE="${GRAPHDB_LICENSE:-$HOME/.graphdb/work/graphdb.license}"
    if [[ ! -f "$LICENSE" ]]; then
        LICENSE="$(find "$HOME" /opt -name graphdb.license -type f 2>/dev/null | head -1 || true)"
    fi
    [[ -n "$LICENSE" && -f "$LICENSE" ]] || die "No GraphDB license file found. Set GRAPHDB_LICENSE=/path/to/graphdb.license"
    say "GraphDB license: $LICENSE"
    export GRAPHDB_LICENSE="$LICENSE"
}

find_zip() {
    ZIP="${AAMAS27_ZIP:-}"
    if [[ -z "$ZIP" ]]; then
        if [[ -f "$HOME/krrood-aamas27-supplement.zip" ]]; then
            ZIP="$HOME/krrood-aamas27-supplement.zip"
        else
            ZIP="$(ls -t "$HOME"/Downloads/krrood-aamas27-supplement*.zip 2>/dev/null | head -1 || true)"
        fi
    fi
    [[ -n "$ZIP" && -f "$ZIP" ]] || die "krrood-aamas27-supplement.zip not found in ~ or ~/Downloads. Set AAMAS27_ZIP=/path/to/zip"
    say "Bundle zip: $ZIP"
}

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG "$PARENT" | tail -1 | tr -dc 0-9)
    (( free_gb >= 15 )) || die "only ${free_gb} GB free in $PARENT; at least 15 GB are needed"
}

# --- 3. Unzip, build, listing tests ---------------------------------------------------------------------
prepare_bundle() {
    command -v unzip >/dev/null || sudo apt-get install -y unzip
    say "Unzipping into $PARENT (the results in $BUNDLE/state are kept)"
    unzip -q -o "$ZIP" -d "$PARENT"
    mkdir -p "$BUNDLE/state"
    say "BUNDLE id: $(cat "$BUNDLE/environment/BUNDLE")   (write this down)"
    cd "$BUNDLE"
    say "Building the Docker image (about 5-10 min the first time)"
    docker compose build
    say "Listing tests (expected: 19 passed, then 1 passed)"
    docker run --rm krrood-aamas27 listings
}

# --- 4. Start the run -----------------------------------------------------------------------------------
start_run() {
    cd "$BUNDLE"
    local inhibit=(systemd-inhibit --what=sleep:idle --why="AAMAS27 experiments")
    if ! systemd-inhibit --what=sleep:idle --why=test true 2>/dev/null; then
        say "WARNING: cannot block suspend; switch off automatic suspend in Settings -> Power"
        inhibit=()
    fi
    say "Starting the full run ($RUN_MODE); log: $BUNDLE/state/reproduce.log"
    local new_lines   # only the lines that this run writes, not those of an earlier run
    new_lines=$(( $(wc -l < "$BUNDLE/state/reproduce.log" 2>/dev/null || echo 0) + 1 ))
    nohup "${inhibit[@]}" docker compose run --rm -T experiments "$RUN_MODE" >> "$LOG" 2>&1 &
    disown || true
    for _ in $(seq 90); do
        if tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" 2>/dev/null | grep -q "FAILED"; then
            tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" | tail -20; die "the run failed, see above"
        fi
        if tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" 2>/dev/null | grep -q "GraphDB started\|finished mode"; then
            tail -5 "$BUNDLE/state/reproduce.log"
            say "The run is going. Leave the PC alone until tomorrow (screen lock is fine, don't log out)."
            say "Check it any time with: bash $(printf '%q' "$0") status"
            return
        fi
        sleep 2
    done
    tail -20 "$LOG"
    die "the run did not report that GraphDB started within 3 min; see $LOG"
}

status() {
    if run_is_going; then say "The run is going."; else say "No run is going."; fi
    local run="$BUNDLE/state/results/aamas27/run"
    say "Finished steps:"
    ls "$run"/.done-* 2>/dev/null | sed 's|.*/.done-|  |' || echo "  none"
    say "End of the log:"
    tail -15 "$BUNDLE/state/reproduce.log" 2>/dev/null || echo "  no log yet"
}

tables() {
    find_license
    cd "$BUNDLE"
    [[ -f state/results/aamas27/run/protege.json ]] \
        || say "WARNING: no state/results/aamas27/run/protege.json yet; the tables will have no Protégé rows"
    docker compose run --rm -T experiments tables
    docker compose down
    say "Results archive: $BUNDLE/state/aamas27_results.tgz"
}

case "$MODE" in
    status) status; exit 0 ;;
    tables) install_docker "$@"; tables; exit 0 ;;
    start | --dry-run) ;;
    *) die "unknown mode $MODE (use: no argument, status, tables, --dry-run)" ;;
esac

if run_is_going; then
    say "A run is already going; not starting another."
    status
    exit 0
fi
install_docker "$@"
find_license
find_zip
check_disk
prepare_bundle
if [[ "$MODE" == --dry-run ]]; then
    say "Dry run: everything is ready; the run was not started."
    exit 0
fi
start_run
