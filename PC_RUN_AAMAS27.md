# AAMAS 2027: running the experiments on the PC

Instructions for running the OWL2Bench experiments of the KRROOD paper on the original machine
(i7-11700K, 32 GB RAM, Ubuntu 24.04). A person or a Claude Code session can follow them step by step. The
detailed reference is `RUNBOOK_AAMAS27.md` in this repository; this file says what to do, in which order, what
to check, and what to hand back.

## Rules (for a Claude Code session on the PC)

* Do not change any code, configuration, query or data file. The point of this run is to measure exactly the
  pinned code: krrood_experiments branch `aamas27-experiments`, CRAM commit `ec7c922b9f`, ripple_down_rules
  `3b994bb`. If something fails, stop, report the error and the last 50 lines of `~/aamas27_run.log`, and ask.
* Do not commit or push anything. Results are not committed; they are packed into an archive (step 5).
* Do not pass `--allow-mismatch`, and do not change the time or memory caps.
* Do not run anything heavy while the run is going (no builds, no browser with many tabs, no second experiment):
  these are the timings that go into the paper.
* Use only the `aamas27_*` GraphDB repositories; never delete the other repositories (e.g. `KRROOD`).

## 0. Prerequisites (5-10 min)

Run these checks and fix whatever fails before starting:

```bash
python3.12 --version                     # Python 3.12 (the results were verified with 3.12.3)
docker info > /dev/null && echo docker ok # the user must be in the docker group
java -version                            # OpenJDK 17 or 21 (owlready2 starts Pellet with it)
ls /opt/graphdb-desktop/lib/app /opt/graphdb-desktop/lib/runtime/bin/java   # GraphDB Desktop 11.x installed
ls ~/.graphdb/work/graphdb.license       # GraphDB license file
df -h ~                                  # at least 12 % free (GraphDB stops answering below 10 %)
pgrep -fa graphdb-desktop || echo "GraphDB Desktop closed"   # must be closed
```

The virtual environment is built from source for one package (`pygraphviz`, needed by ripple_down_rules), so
these system packages must be installed (the script checks them and stops with the command to run):

```bash
sudo apt install python3.12-venv python3.12-dev build-essential graphviz libgraphviz-dev pkg-config
```

If Docker needs `sudo`: `sudo usermod -aG docker $USER`, then log out and in again. If Java is missing:
`sudo apt install openjdk-17-jre`. If GraphDB is installed elsewhere, set `GRAPHDB_APP`, `GRAPHDB_JAVA` and
`GRAPHDB_LICENSE` (see the top of `scripts/aamas27/run_all.sh`). Close all other applications. Plug in the
power cable.

### Code and environment that the run uses

`run_all.sh` sets these up itself; nothing has to be installed by hand. Do not use any other checkout or
virtual environment (for example an older `~/cram` clone or `~/.virtualenvs/krrood_experiments`).

| What | Where | Version |
|------|-------|---------|
| krrood_experiments (scripts, queries, generated model, data) | `~/krrood_experiments_aamas27` | branch `aamas27-experiments` of `https://github.com/AbdelrhmanBassiouny/krrood_experiments.git` |
| CRAM (contains `krrood`: EQL, Ontomatic, ORMatic) | `~/cram_aamas27` | commit `ec7c922b9ff66ae49f380f044e6e50db883264f1` (branch `aamas27-experiments` of `https://github.com/AbdelrhmanBassiouny/cognitive_robot_abstract_machine.git`), checked out detached |
| ripple_down_rules | `~/ripple_down_rules_aamas27` | commit `3b994bb` of `https://github.com/AbdelrhmanBassiouny/ripple_down_rules.git` |
| Python environment | `~/venvs/krrood_aamas27` | `krrood`, `ripple_down_rules` and `krrood_experiments` installed editable from the three directories above; every other package at the version of `scripts/aamas27/requirements-aamas27-lock.txt` |

The script clones the three repositories, or updates existing clones from the URLs above (whatever their
remote `origin` points to). It stops if a clone has uncommitted changes or if CRAM does not end up at the pinned
commit. It installs the packages with the lock file as a constraint and writes the installed versions into
`pip_freeze.txt` of the results directory. If they differ from the lock file, the log shows `WARNING: the virtual
environment differs` with the differences.

## 1. Start the automated run (one command, unattended)

```bash
cd ~ && { git clone -b aamas27-experiments https://github.com/AbdelrhmanBassiouny/krrood_experiments.git \
    krrood_experiments_aamas27 || git -C krrood_experiments_aamas27 pull --ff-only; } \
  && nohup systemd-inhibit --what=sleep:idle --why="AAMAS27 experiments" \
       bash krrood_experiments_aamas27/scripts/aamas27/run_all.sh > ~/aamas27_run.log 2>&1 &
```

`systemd-inhibit` keeps the machine from suspending during the run. The script clones CRAM and
ripple_down_rules into `~/cram_aamas27` and `~/ripple_down_rules_aamas27`, checks out the pinned commits, and
creates the virtual environment `~/venvs/krrood_aamas27`. It then starts PostgreSQL (Docker container
`krrood-pg`) and GraphDB (headless, port 7200), and runs every step below. If the existing clones have uncommitted
changes, the script stops; tell the user rather than discarding them.

If the run stops (error, reboot), start the same command again: finished steps are skipped (marker files
`.done-<step>` in the results directory), and the interrupted step starts over.

## 2. Check the set-up (after about 10 min), then monitor

As soon as the log shows `start data`, check that the run uses the right code and environment:

```bash
grep -E "experiments |CRAM |rdr |virtual environment" ~/aamas27_run.log
git -C ~/cram_aamas27 rev-parse HEAD      # ec7c922b9ff66ae49f380f044e6e50db883264f1
git -C ~/ripple_down_rules_aamas27 rev-parse --short HEAD   # 3b994bb
~/venvs/krrood_aamas27/bin/python -c "import krrood, ripple_down_rules, krrood_experiments as e; print(krrood.__file__, ripple_down_rules.__file__, e.__file__)"
```

Expected: the log line `the virtual environment matches .../requirements-aamas27-lock.txt` (no `WARNING`), the
two commits above, and the three paths inside `~/cram_aamas27`, `~/ripple_down_rules_aamas27` and
`~/krrood_experiments_aamas27`. If anything differs, stop the run (`pkill -f run_all.sh`; then
`pkill -f GraphDBWorkbench` if GraphDB is still up) and report it.

Then monitor:

```bash
tail -f ~/aamas27_run.log
ls ~/krrood_experiments_aamas27/results/aamas27/$(hostname)-run/.done-*     # finished steps
```

Expected steps and durations (estimates, mostly from the January run on this machine):

| Step | What | Duration |
|------|------|----------|
| set-up | code, venv, PostgreSQL, GraphDB | 5-10 min |
| `data` | GraphDB OWL 2 RL materialization of the raw data (1 core), export of the reasoned file, query repositories | 40-60 min |
| `tests` | experiment tests | 1 min |
| `answer_check` | every system's answers vs GraphDB, 18 queries | 10-25 min |
| `soundness_audit` | KRROOD's knowledge base vs GraphDB's closure, assertion by assertion | 2-5 min |
| `query_timing` | 18 queries x 10 repetitions x 5 systems | 1-2 h |
| `loading_krrood` | 5 repetitions x (raw, reasoned) | 15-20 min |
| `loading_owlready2_pellet` | 5 x raw; reasoned ran out of memory in January | 20-40 min |
| `loading_rdflib_owlrl` | raw and reasoned, 3 h cap each; the reasoned run hit the cap in January | 3-6 h |
| `loading_graphdb` | fresh repository per input, raw and reasoned | about 1 h |
| `loading_krrood_ormatic` | KRROOD + persisting into PostgreSQL, 5 x (raw, reasoned) | 30-60 min |
| `ablation` | eager chaining instead of step 5, 2 h cap (about 100 min in January) | up to 2 h |
| tables | `loading_table.tex`, `query_table.tex`, archive | seconds |

Total: about 9-13 hours. The log ends with `all automated steps finished`.

## 3. Check the results

Results directory: `R=~/krrood_experiments_aamas27/results/aamas27/$(hostname)-run`. Check each of these and
report any deviation:

1. `grep -E "passed|failed" ~/aamas27_run.log` shows `24 passed`.
2. `$R/graphdb_status.json`: `aamas27_rl` has `explicit` 54901 and `total` 1467912, and `aamas27_noinf` has
   `explicit` 1431635.
3. `$R/check/answer_check.json`: `"all_equal": true`, `"mismatches": []`, `"known_differences": {}`.
4. `$R/audit/audit.json`, with this summary:

   ```bash
   python3 - "$R/audit/audit.json" <<'EOF'
   import json, sys
   d = json.load(open(sys.argv[1]))
   print("individuals", d["individuals_in_reference"], d["individuals_in_krrood"])
   for s in ("classes", "object_properties", "data_properties"):
       print(s, {f: sum(x[f] for x in d[s].values()) for f in ("krrood", "reference", "unsound", "missing")})
   print({k: v for k, v in d["owl2_rl_check"].items() if k in ("passed", "equalities", "inconsistencies")})
   EOF
   ```

   Expected: 3667 3667; classes 17558 / 17558 / 0 / 0; object properties 1385869 / 1385869 / 0 / 0; data properties
   20933 / 20933 / 0 / 0; `passed True, equalities 0, inconsistencies 0`.
5. Every `environment.json` under `$R` (`find $R -name environment.json`): the krrood commit is
   `ec7c922b9ff66ae49f380f044e6e50db883264f1`, and `dirty` is `false` for both repositories.
6. `$R/loading/loading.json`: note every run whose `status` is not `ok` (`timeout`, `memory_limit`, `failed`). A
   timeout of RDFLib or of the ablation is an expected result, not an error.

## 4. Protégé + Pellet (by hand, after step 1 finished, about 1 h)

This needs the reasoned file that the run created, and must not overlap with the automated measurements. Follow
`RUNBOOK_AAMAS27.md` section 7 exactly:

1. Install the Pellet plug-in and "Snap SPARQL Query" once (File -> Check for plugins).
2. Set `max_heap_size=28G` in `~/.Protege/conf/jvm.conf`.
3. For `resources/owl2bench_statements_unreasoned.rdf` and then `resources/owl2bench_statements_reasoned.rdf`, start
   a fresh Protégé with `/usr/bin/time -v -o ~/protege_raw_time.txt ./run.sh` (`protege_reasoned_time.txt` for the
   second file). Open the file, select Reasoner -> Pellet, then Reasoner -> Start reasoner, and write down the
   loading and reasoning time from the log. Then quit.
4. In a new session on the reasoned file, after Start reasoner, run the 18 SPARQL queries of
   `src/krrood_experiments/owl2bench/sparql_queries.py` in Snap SPARQL. Note the time and the number of results;
   stop a query after 60 s and record "timeout".
5. Fill in `scripts/aamas27/protege_template.json`, save it as `$R/protege.json`, then run:

   ```bash
   cd ~/krrood_experiments_aamas27 && bash scripts/aamas27/run_all.sh tables
   ```

## 5. Hand back

The archive `~/krrood_experiments_aamas27/aamas27_results_$(hostname).tgz` contains everything: the results
directory, the tables, the logs and the Protégé time files. Copy it to the laptop, for example with
`scp ~/krrood_experiments_aamas27/aamas27_results_*.tgz <laptop>:~/Projects/krrood_aamas/planning/`. Also copy
`~/aamas27_run.log`. Then give the paper session the path, with the summary below.

Summary to write (a Claude Code session on the PC writes it as `~/aamas27_summary.md`):

* start and end time of the run, and whether it was interrupted or resumed;
* the results of the 6 checks of step 3, with the deviations quoted;
* for each system and input, the mean loading time, its standard deviation, the peak memory and the status, taken
  from `$R/loading/loading.json`;
* anything unusual in the log (warnings, retries, a step that was started more than once).

## 6. Clean up (after the archive is copied)

```bash
docker stop krrood-pg          # keep the container if a step may need to be repeated
```

GraphDB stops when the script ends. Leave the `aamas27_*` repositories in place until the paper is submitted.
