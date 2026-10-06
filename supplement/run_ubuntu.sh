#!/usr/bin/env bash
# Level 3 on Ubuntu (24.04) in one command: installs Docker if needed, builds the image, runs the listing tests,
# checks the GraphDB license, records the machine's details and starts the full run in the background, with a
# monitor of the machine's load. Run it from the unpacked bundle. Safe to call again: it never starts a second run,
# and a stopped run resumes after its last finished step. See README.md.
#
# Usage:
#   bash run_ubuntu.sh             set up, then start the full run (about 9-13 h)
#   bash run_ubuntu.sh status      is the run going, which steps finished, and the end of its log
#   bash run_ubuntu.sh tables      after saving protege.json: rebuild the tables and the results archive
#   bash run_ubuntu.sh --dry-run   everything except starting the run
#
# Settings (environment variables):
#   GRAPHDB_LICENSE   GraphDB license file [~/graphdb.license, ~/Downloads/graphdb.license, ~/.graphdb/...,
#                     else any *.license file under ~ and /opt with "graphdb" in its path]
set -euo pipefail

MODE="${1:-start}"
BUNDLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$BUNDLE/state/run.log"
RUN_MODE="${AAMAS27_RUN_MODE:-all}"   # only changed to test this script
PROJECT=krrood-aamas27                # the project name in compose.yaml

say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

# Stops instead of answering "no" when Docker can't be asked: the caller would then start a second run on top of
# the one that is going.
run_is_going() {
    command -v docker >/dev/null || return 1   # no Docker, so no run
    local containers
    containers="$(docker ps -q --filter "label=com.docker.compose.project=$PROJECT" \
        --filter "label=com.docker.compose.service=experiments")" \
        || die "can't ask Docker whether a run is going (docker ps failed, see above). If it says permission denied:
       log out and back in, or run 'newgrp docker' in this terminal, then run this script again."
    [[ -n "$containers" ]]
}

# The docker group applies only to new logins: continue in a shell that has it.
use_docker_group() {
    if command -v docker >/dev/null && ! docker info >/dev/null 2>&1 && [[ -z "${AAMAS27_IN_SG:-}" ]] \
        && getent group docker | cut -d: -f4 | tr ',' '\n' | grep -qx "$USER"; then
        say "Continuing with the docker group active (no need to log out)"
        exec env AAMAS27_IN_SG=1 sg docker -c "bash $(printf '%q' "$0") $(printf '%q ' "$@")"
    fi
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
    use_docker_group "$@"
    docker info >/dev/null 2>&1 \
        || die "Docker still says permission denied. Log out and back in (or reboot), then run this script again."
    docker compose version
}

# --- 2. License, disk ------------------------------------------------------------------------------
find_license() {
    LICENSE="${GRAPHDB_LICENSE:-}"
    if [[ -z "$LICENSE" ]]; then
        for candidate in "$HOME/graphdb.license" "$HOME/Downloads/graphdb.license" \
                         "$HOME/.graphdb/work/graphdb.license" "$HOME/.graphdb/conf/graphdb.license"; do
            [[ -f "$candidate" ]] && { LICENSE="$candidate"; break; }
        done
    fi
    if [[ -z "$LICENSE" ]]; then
        # Any *.license file whose name or folder mentions GraphDB, e.g. a downloaded GRAPHDB_FREE*.license.
        LICENSE="$(find "$HOME" /opt -type f -iname '*.license' 2>/dev/null | grep -i graphdb | head -1 || true)"
    fi
    if [[ -z "$LICENSE" || ! -f "$LICENSE" ]]; then
        die "No GraphDB license file found. GraphDB 11 needs one, even the free edition: request GraphDB Free on
       https://graphdb.ontotext.com/ (the license arrives by e-mail), save it as ~/graphdb.license and run this
       script again, or run it with GRAPHDB_LICENSE=/path/to/file.license."
    fi
    say "GraphDB license: $LICENSE"
    export GRAPHDB_LICENSE="$LICENSE"
}

# Starts GraphDB in the container with the license and asks it whether the license is valid (about 30 s).
check_license() {
    say "Checking the GraphDB license with GraphDB itself"
    local answer
    answer="$(docker run --rm -v "$GRAPHDB_LICENSE:/license/graphdb.license:ro" --entrypoint bash krrood-aamas27 -c '
        GDB_HEAP_SIZE=1g /opt/graphdb/dist/bin/graphdb -d -p /tmp/g.pid -Dgraphdb.home=/tmp/gh \
            -Dgraphdb.license.file=/license/graphdb.license -Dgraphdb.connector.port=7200 >/dev/null 2>&1
        /opt/venvs/earlier/bin/python - <<PY
import json, time, urllib.request
for _ in range(90):
    try:
        print(json.dumps(json.load(urllib.request.urlopen("http://localhost:7200/rest/graphdb-settings/license"))))
        break
    except Exception:
        time.sleep(1)
PY' 2>/dev/null || true)"
    if [[ "$answer" != *'"valid": true'* ]]; then
        echo "  $answer"
        die "GraphDB does not accept the license $GRAPHDB_LICENSE (answer above). Use another license file."
    fi
    # What the license allows matters for GraphDB's times (e.g. the free edition's core limit); not the licensee.
    mkdir -p "$BUNDLE/$HOST_DIR_RELATIVE"
    python3 -c 'import json, sys
answer = json.loads(sys.argv[1])
record = {key: answer.get(key) for key in ("product", "productType", "version", "maxCpuCores", "expiryDate")}
json.dump(record, open(sys.argv[2], "w"), indent=2)
print("  GraphDB accepts the license:", record)' "$answer" "$BUNDLE/$HOST_DIR_RELATIVE/graphdb_license.json"
}

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG "$BUNDLE" | tail -1 | tr -dc 0-9)
    (( free_gb >= 15 )) || die "only ${free_gb} GB free in $BUNDLE; at least 15 GB are needed"
}

# --- 3. Build, listing tests ---------------------------------------------------------------------------
prepare_bundle() {
    [[ -f "$BUNDLE/environment/BUNDLE" && -f "$BUNDLE/compose.yaml" ]] \
        || die "run this script from the unpacked bundle (the folder with compose.yaml); it is in $BUNDLE"
    cd "$BUNDLE"
    mkdir -p state
    # All files in the zip have the same time, so Docker would take a changed file of an earlier version of the
    # bundle with the same size for unchanged. Giving them the current time makes Docker read them again.
    find . -path ./state -prune -o -exec touch -h {} +
    local bundle_id built_id
    bundle_id="$(cat environment/BUNDLE)"
    say "Building the Docker image of BUNDLE $bundle_id (5-15 min the first time)"
    docker compose build
    built_id="$(docker run --rm krrood-aamas27 fingerprint)"
    [[ "$built_id" == "$bundle_id" ]] \
        || die "the image holds other code ($built_id) than this bundle ($bundle_id): run 'docker builder prune -af', then this script again"
    say "The image holds the code of BUNDLE $built_id"
    say "Listing tests (expected: 24 passed, then 1 passed)"
    docker run --rm krrood-aamas27 listings
    check_license
}

# --- Host details and monitoring (no hostname or user name: the results are shipped anonymized) ----------
HOST_DIR_RELATIVE=state/results/aamas27/run/host

record_host() {
    mkdir -p "$BUNDLE/$HOST_DIR_RELATIVE"
    python3 - "$BUNDLE/$HOST_DIR_RELATIVE/host.json" "$BUNDLE/state" <<'PY'
import json, os, platform, subprocess, sys, datetime
def run(*command):
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as error:
        return f"unavailable: {error}"
def read(path):
    try:
        return open(path).read().strip()
    except Exception:
        return None
lscpu = {}
for line in run("lscpu").splitlines():
    key, _, value = line.partition(":")
    if key.strip() in ("Architecture", "Model name", "CPU(s)", "Thread(s) per core", "Core(s) per socket",
                       "Socket(s)", "CPU max MHz", "CPU min MHz", "L1d cache", "L2 cache", "L3 cache",
                       "Virtualization"):
        lscpu[key.strip()] = value.strip()
os_release = dict(line.split("=", 1) for line in (read("/etc/os-release") or "").splitlines() if "=" in line)
memory = {line.split(":")[0]: line.split(":")[1].strip() for line in (read("/proc/meminfo") or "").splitlines()
          if line.split(":")[0] in ("MemTotal", "SwapTotal", "MemAvailable")}
source = run("findmnt", "-n", "-o", "SOURCE", "-T", sys.argv[2])
disk = run("lsblk", "-d", "-n", "-o", "NAME,MODEL,ROTA,TRAN,SIZE", "/dev/" + run("lsblk", "-n", "-o", "PKNAME", source).splitlines()[0]
           if run("lsblk", "-n", "-o", "PKNAME", source) else source)
record = {
    "recorded_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "cpu": lscpu,
    "cpu_frequency_governor": read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
    "cpufreq_boost": read("/sys/devices/system/cpu/cpufreq/boost"),
    "intel_pstate_no_turbo": read("/sys/devices/system/cpu/intel_pstate/no_turbo"),
    "power_profile": run("powerprofilesctl", "get"),
    "memory": memory,
    "disk_of_results": disk,
    "board": {k: read(f"/sys/class/dmi/id/{k}") for k in ("sys_vendor", "board_vendor", "board_name")},
    "os": os_release.get("PRETTY_NAME", "").strip('"'),
    "kernel": platform.release(),
    "virtualization": run("systemd-detect-virt") or "none",
    "docker": run("docker", "version", "--format", "{{.Server.Version}}"),
    "docker_cgroup": run("docker", "info", "--format", "{{.CgroupDriver}} cgroup v{{.CgroupVersion}}"),
}
json.dump(record, open(sys.argv[1], "w"), indent=2)
print(json.dumps(record, indent=2))
PY
}

# Samples the machine every 30 s while the run's container exists: load, memory, CPU frequency, temperature, and
# the busiest processes outside Docker (process names only), to show afterwards whether anything interfered.
start_monitor() {
    local pidfile="$BUNDLE/state/monitor.pid"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
        return
    fi
    nohup python3 - "$BUNDLE/$HOST_DIR_RELATIVE/monitor.csv" "$PROJECT" > /dev/null 2>&1 <<'PY' &
import csv, glob, os, subprocess, sys, time, datetime
path, project = sys.argv[1], sys.argv[2]
def running():
    return bool(subprocess.run(["docker", "ps", "-q", "--filter", f"label=com.docker.compose.project={project}",
                                "--filter", "label=com.docker.compose.service=experiments"],
                               capture_output=True, text=True).stdout.strip())
def cpu_mhz():
    values = [int(open(f).read()) / 1000 for f in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq")]
    return round(sum(values) / len(values)) if values else ""
def temperature():
    values = []
    for f in glob.glob("/sys/class/thermal/thermal_zone*/temp") + glob.glob("/sys/class/hwmon/hwmon*/temp*_input"):
        try:
            values.append(int(open(f).read()) / 1000)
        except Exception:
            pass
    return max(values) if values else ""
TICKS = os.sysconf("SC_CLK_TCK")
previous = {}
def outside_docker(interval):
    """Processes outside Docker that used at least 5 % of one CPU since the last sample (names only)."""
    global previous
    current, busy = {}, []
    for stat in glob.glob("/proc/[0-9]*/stat"):
        try:
            pid = stat.split("/")[2]
            fields = open(stat).read().rsplit(")", 1)
            name = fields[0].split("(", 1)[1]
            values = fields[1].split()
            current[pid] = (name, int(values[11]) + int(values[12]))
        except Exception:
            continue
    for pid, (name, ticks) in current.items():
        if pid in previous and previous[pid][0] == name:
            percent = 100 * (ticks - previous[pid][1]) / TICKS / interval
            if percent >= 5:
                try:
                    if "docker" in open(f"/proc/{pid}/cgroup").read():
                        continue
                except Exception:
                    continue
                busy.append((percent, name))
    previous = current
    return " ".join(f"{name}:{percent:.0f}" for percent, name in sorted(busy, reverse=True)[:5])
new = not os.path.exists(path)
with open(path, "a", newline="") as handle:
    writer = csv.writer(handle)
    if new:
        writer.writerow(["time", "load1", "mem_used_gib", "swap_used_gib", "cpu_mhz_mean", "temp_max_c",
                         "busy_outside_docker"])
    time.sleep(60)
    outside_docker(1)
    last = time.time()
    while running():
        time.sleep(30)
        now = time.time()
        busy = outside_docker(now - last)
        last = now
        meminfo = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
        writer.writerow([
            datetime.datetime.now().isoformat(timespec="seconds"),
            os.getloadavg()[0],
            round((meminfo["MemTotal"] - meminfo["MemAvailable"]) / 2**20, 2),
            round((meminfo["SwapTotal"] - meminfo["SwapFree"]) / 2**20, 2),
            cpu_mhz(), temperature(), busy,
        ])
        handle.flush()
PY
    echo $! > "$pidfile"
    say "Monitoring the machine every 30 s into $HOST_DIR_RELATIVE/monitor.csv"
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
    record_host > /dev/null
    nohup "${inhibit[@]}" docker compose run --rm -T experiments "$RUN_MODE" >> "$LOG" 2>&1 &
    disown || true
    start_monitor
    for _ in $(seq 90); do
        if tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" 2>/dev/null | grep -q "FAILED"; then
            tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" | tail -20; die "the run failed, see above"
        fi
        if tail -n +"$new_lines" "$BUNDLE/state/reproduce.log" 2>/dev/null | grep -q "GraphDB started\|finished mode"; then
            tail -5 "$BUNDLE/state/reproduce.log"
            say "The run is going (9-13 h). Leave the machine idle until it has finished: screen lock is fine,
    but don't log out, and don't run anything else, since the run measures time."
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
    if [[ -f "$BUNDLE/$HOST_DIR_RELATIVE/monitor.csv" ]]; then
        say "Machine (last samples; busy_outside_docker should stay empty):"
        tail -3 "$BUNDLE/$HOST_DIR_RELATIVE/monitor.csv"
    fi
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
    status) use_docker_group "$@"; status; exit 0 ;;
    tables)
        install_docker "$@"
        if run_is_going; then die "the run is still going; make the tables after it has finished"; fi
        tables
        exit 0
        ;;
    start | --dry-run) ;;
    *) die "unknown mode $MODE (use: no argument, status, tables, --dry-run)" ;;
esac

install_docker "$@"
if run_is_going; then
    say "A run is already going; not starting another."
    status
    exit 0
fi
find_license
check_disk
prepare_bundle
if [[ "$MODE" == --dry-run ]]; then
    say "Dry run: everything is ready; the run was not started."
    exit 0
fi
start_run
