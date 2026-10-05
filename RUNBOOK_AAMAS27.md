# Runbook: OWL2Bench experiments for the AAMAS 2027 KRROOD paper

This runbook re-runs the OWL2Bench (OWL 2 RL profile, 1 university) experiments of the paper on the original machine
(i7-11700K, 32 GB RAM, Ubuntu 24.04). The commands can be copied and pasted. Every script writes machine-readable
results (JSON) into `results/aamas27/<hostname>-<timestamp>-<label>/` (or the directory given with `--results-dir`),
together with an `environment.json`. That file records the git commits of both repositories (and whether the working
trees were modified), the Python and package versions, the CPU, RAM, OS, the GraphDB version, license (CPU-core limit)
and repository rulesets, the GraphDB JVM options, and the PostgreSQL version.

Do not mix timings measured on another machine (for example the numbers in section 11) with the timings of the
original machine.

## 0. Overview

| # | Experiment | Command (section) | Duration on the original machine (estimate) | Peak RAM |
|---|------------|-------------------|---------------------------------------------|----------|
| 0 | Set-up (venv, PostgreSQL, GraphDB, data) | sections 2-5 | 1.5 h (mostly GraphDB OWL 2 RL reasoning, about 30-45 min) | 3 GB |
| 1 | Tests for the soundness fixes and provenance | 6.1 | 1 min | 1.5 GB |
| 2 | Hard answer-set check, 18 RL queries, 5 frameworks | 6.2 | 15-25 min | 4 GB (RDFLib) |
| 3 | Query timing, 18 RL queries x 10 repetitions | 6.3 | 1-4 h (owlready2 reloads the reasoned file before every repetition, as in January) | 4 GB |
| 4 | Loading + reasoning: time and peak memory | 6.4 | about 5-6 h (RDFLib on the reasoned data runs into its 3 h cap; GraphDB 2 x 30-45 min) | owlready2/Pellet and RDFLib up to their limits |
| 5 | Ablation without the connected-components step | 6.5 | up to 2 h (cap) | unknown, use `--memory-limit-gib 24` |
| 6 | Protégé + Pellet (manual) | 7 | 30-60 min | up to 25 GB |
| 7 | LaTeX tables | 8 | seconds | - |

Recommended order: 1, 2, then 3 and 4 (overnight, see 6.6), 5, 6, 7. Close other applications while measuring.

## 1. What changed compared to the January 2026 run

Code base: krrood_experiments `Tom/main` (0d53ec7) and cognitive_robot_abstract_machine (CRAM) `origin/dl`
(b38a6673a, includes the distinct-cache fix f7205b4acd and the cyclic-import fix). `origin/dl` does not import
(`ImportError: cannot import name 'issubclass_or_role' from krrood.class_diagrams.wrapped_field`); the branch
therefore starts with a cherry-pick of the author's one-line fix afd7f7d8fc (from `dl2`).

Soundness fixes in Ontomatic (CRAM branch `aamas27-experiments`, one commit each, each with a test):

1. Only sufficient conditions classify individuals (e2ed0c8c4b). Restrictions in superclass position
   (`LeisureStudent SubClassOf (Student and takesCourse max 1 Course)`, `WomanCollege SubClassOf (College and
   hasStudent only not Man)`) were turned into classification axioms: 53 students were typed LeisureStudent although
   OWL 2 RL entails none (Q14 returned 53 instead of 0). They are now generated as `necessary_conditions_python`
   (documentation and validation only). `owl:equivalentClass` definitions (T20CricketFan, Q5) and general class axioms
   remain classification axioms; general class axioms now keep their named conjunct (`Student and (hasMajor some
   Science) SubClassOf ScienceStudent` checks Student). The loader no longer types an individual with a specialised
   domain because a value matches the specialised range (reverse use of a restriction) and no longer evaluates an
   axiom inherited from a superclass for a subclass.
2. No classification axioms synthesised from inverse properties (8cd06f4fa3): e.g. `Organization <- hasEmployee some
   Employee`, `Course <- isTaughtBy some Faculty`, `Department/College/Program <- hasHead some Chair/Dean/Director`.
3. No subclass or role relations guessed from shared properties (7ce1541932): SportsLover, SportsFan,
   BasketBallLover, BasketBallFan and T20CricketFan are now `Role[Person]` (they were a chain of subclasses of
   PeopleWithHobby), EvaluationCommittee is a plain class (it was `Role[Organization]`). This changes the class
   structure and the ORM schema (regenerated). Revert this commit together with EXP 29b72a3 to get the January
   class structure back.
4. Complete OWL 2 RL type inference (a4b5c8f755): inferred types are visible to the classification axioms (fixpoint);
   values implied through super-, equivalent and inverse properties and symmetry are taken into account before
   typing (prp-spo1, prp-eqp, prp-inv, prp-symp); prp-dom/prp-rng use the `rdfs:domain`/`rdfs:range` declared in the
   ontology (the generator now emits them as `rdfs_domains`/`rdfs_ranges` on every property descriptor). As a
   consequence the 7 ResearchGroup individuals are typed Employee/Person exactly as in the OWL 2 RL closure
   (`hasResearchProject SubPropertyOf hasWork`, `hasWork rdfs:domain Employee`, `Employee SubClassOf Person`), and Q12
   now has the same answer set as GraphDB (2494).

5. Individuals are no longer typed with the class they are named after (a6d22a95aa): the loader typed every
   property-less individual whose local name equals a class name (e.g. `owl2bench:Engineering`, a value of
   hasCollegeDiscipline) with that class (14 non-entailed memberships). Untyped individuals are now represented by
   the ontology base class. EQL and SQLAlchemy Q21 therefore compare the discipline's URI with
   `owl2bench:Engineering`, as the SPARQL query does (EXP 0d84891).

Further CRAM changes: provenance of every inferred fact and type (46830ff78a: `PropertyDescriptorRelation.explain()`,
`.find()`, `OwlInstancesRegistry.explain_type()`), symmetric-transitive component facts added through the relation
path so that super-property/inverse/chain/equivalence implications apply (2f721b0fbc; this roughly doubles the KRROOD
loading time on OWL2Bench, see section 11, without changing any query answer), and an ablation flag
`PropertyDescriptorRelation.eager_symmetric_transitive_closure` (42563662af).

Experiment changes (EXP branch `aamas27-experiments`):

* All 18 OWL 2 RL queries are run (Q9, Q12, Q13, Q14 added for EQL and SQLAlchemy).
* Hard answer-set check: every framework's answer set of every query is compared with GraphDB (raw data,
  OWL2-RL (Optimized) ruleset) and the script fails unless they are equal. January only compared counts.
* SQLAlchemy queries now return the SPARQL projection: Q4 also selects the person (it selected only the age), Q2
  selects (member, organization), Q15/Q16 select DISTINCT ?x only, Q22 no longer restricts students to the
  polymorphic types PG/PhD/UGStudent (that filter returned 12 of the 106 answers once the student roles were
  complete).
* Every framework of the query experiment runs in its own process (January: one process, interleaved). The timed
  operation per framework is unchanged.
* The reasoned data file is regenerated as the OWL 2 RL closure computed by GraphDB (section 5). The local January file
  (sha256 5d30e2c0..., 2026-01-03, exported from Protégé) contains no T20CricketFan assertion at all, so RDFLib and
  owlready2 cannot answer Q5 with it.
* Loading experiment: peak memory of every system (process tree, 50 ms sampling; GraphDB: server JVM RSS), GraphDB
  with OWL2-RL (Optimized) on both inputs, KRROOD + ORMatic (persisting into PostgreSQL), and the ablation.

## 2. Known limitations (to state in the paper)

* No equality reasoning: KRROOD adopts the unique-name assumption; `owl:sameAs`, and the OWL 2 RL rules that derive
  it (functional/inverse-functional properties, keys, max cardinality 1), are not supported. On this data set the
  OWL 2 RL closure (GraphDB, sameAs enabled) contains no `owl:sameAs` between two different individuals (only the
  4212 reflexive ones), so this does not affect any answer.
* FunctionalProperty detection in the generator compares `prop_type == OWL.FunctionalProperty` where `prop_type_uri`
  is meant, so functional properties are not recognised (not needed by any query).
* Property-assertion completeness: 4037 object-property facts of the OWL 2 RL closure are not materialised by
  KRROOD (isStudentOf/hasStudent from the chain `enrollIn o isSubOrganizationOf` 1978 each, worksFor/hasEmployee from
  `worksFor o isSubOrganizationOf` 37 each, hasWork of the 7 research groups). None of them is asked by the 18 queries.
  KRROOD derives no property fact that is not in the closure (section 11).
* Q22: EQL and SQLAlchemy return 141 rows for 106 distinct answers (several role objects per individual); the answer
  sets are equal to GraphDB's. Report 106 in the "Results" column (the table script uses the distinct count of GraphDB).

## 3. Get the code

Assuming the two branches were pushed to the authors' remotes as `aamas27-experiments`:

```bash
cd ~
git clone git@github.com:AbdelrhmanBassiouny/krrood_experiments.git krrood_experiments_aamas27
cd ~/krrood_experiments_aamas27 && git fetch origin aamas27-experiments && git checkout aamas27-experiments
git log -1 --format='%H %s'   # expected: the commit that contains this runbook, or later

cd ~
git clone git@github.com:AbdelrhmanBassiouny/cognitive_robot_abstract_machine.git cram_aamas27
cd ~/cram_aamas27 && git fetch origin aamas27-experiments && git checkout aamas27-experiments
git log -1 --format='%H %s'   # expected: a6d22a95aa

cd ~
git clone https://github.com/AbdelrhmanBassiouny/ripple_down_rules.git ripple_down_rules_aamas27
cd ~/ripple_down_rules_aamas27 && git checkout 3b994bb
```

If you already have clones, use `git worktree add -b aamas27-experiments <dir> origin/aamas27-experiments` instead.
CRAM has git submodules that are not needed (`krrood` has no submodule dependency); do not run `git submodule update`.

Commits of the code that was verified locally (section 11): CRAM a6d22a95aa, EXP 0d84891 (code), runbook commits on top,
ripple_down_rules 3b994bb.

## 4. Python environment

Python 3.12 (the January runs used 3.12.3). The ROS set-up of the shell must not leak into the environment.

```bash
unset PYTHONPATH
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python3.12 -m venv ~/venvs/krrood_aamas27
source ~/venvs/krrood_aamas27/bin/activate
pip install --upgrade pip
pip install -e ~/cram_aamas27/krrood
pip install -e ~/ripple_down_rules_aamas27          # editable: a non-editable install misses sub-packages
pip install -e ~/krrood_experiments_aamas27
pip install -r ~/krrood_experiments_aamas27/scripts/aamas27/requirements-aamas27.txt
python -c "import krrood, ripple_down_rules; from ripple_down_rules import RDRDecorator; print(krrood.__file__)"
```

The last line must print a path inside `~/cram_aamas27`. owlready2 starts Pellet with the `java` on the PATH
(OpenJDK 17 or 21; check with `java -version`).

## 5. Services and data

### 5.1 PostgreSQL 18.1 (Docker, no sudo needed if your user is in the docker group)

```bash
docker run -d --name krrood-pg -e POSTGRES_USER=krrood_experiments -e POSTGRES_PASSWORD=krrood_experiments \
    -e POSTGRES_DB=krrood_experiments -p 127.0.0.1:5432:5432 --shm-size=256m postgres:18.1
export KRROOD_EXPERIMENTS_DATABASE_URI="postgresql+psycopg2://krrood_experiments:krrood_experiments@localhost:5432/krrood_experiments"
docker exec krrood-pg psql -U krrood_experiments -c "select version()"
```

If port 5432 is taken by a local PostgreSQL, either use it (create the database as in the main README) or map the
container to another port (`-p 127.0.0.1:5433:5432` and `...@localhost:5433/...`).

### 5.2 GraphDB 11.2 (Desktop installation, started without GUI)

GraphDB Desktop contains a normal server. Start it headless (the Free license allows one CPU core; the license file
of the Desktop installation is reused). Use the heap you used in January if you know it; otherwise `-Xmx8g`:

```bash
A=/opt/graphdb-desktop/lib/app
nohup /opt/graphdb-desktop/lib/runtime/bin/java -Xms1g -Xmx8g -Djava.awt.headless=true \
  --add-exports jdk.management.agent/jdk.internal.agent=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED \
  --enable-native-access=ALL-UNNAMED -cp "$A/lib/*" -Dgraphdb.dist=$A -Dgraphdb.home=$HOME/.graphdb \
  -Dgraphdb.connector.port=7200 -Dgraphdb.license.file=$HOME/.graphdb/work/graphdb.license \
  com.ontotext.graphdb.server.GraphDBWorkbench > ~/graphdb_aamas27.log 2>&1 &
echo $! > ~/graphdb_aamas27.pid
until curl -sf http://localhost:7200/rest/info/version; do sleep 2; done; echo
curl -s http://localhost:7200/rest/graphdb-settings/license | head -c 300; echo
export KRROOD_GRAPHDB_URL=http://localhost:7200
```

(Close GraphDB Desktop first if it is running; it uses the same port and home directory. Alternatively start the
Desktop application and skip the java command. With `-Dgraphdb.home=$HOME/.graphdb` the existing repository `KRROOD`
stays untouched; the scripts only create, clear or delete repositories whose name starts with `aamas27_`.)
Stop it at the end with `kill $(cat ~/graphdb_aamas27.pid)`.

Create the two query repositories and load the data (`aamas27_rl`: raw data with ruleset `owl2-rl-optimized`, the
reference of the answer-set check; `aamas27_noinf`: reasoned data with ruleset `empty` = "No inference"). Loading the
raw data into `aamas27_rl` performs the OWL 2 RL materialisation and takes 30-45 min:

```bash
cd ~/krrood_experiments_aamas27
python scripts/aamas27/graphdb_setup.py --create aamas27_rl owl2-rl-optimized \
    --load aamas27_rl resources/owl2bench_statements_unreasoned.rdf --status
```

Verify: `"aamas27_rl": {"ruleset": "owl2-rl-optimized", "explicit": 54901, "total": 1467912}`. In the Workbench
(http://localhost:7200, Setup -> Repositories -> aamas27_rl -> edit) the ruleset is shown as "OWL2-RL (Optimized)".

### 5.3 Data files

* `resources/owl2bench_statements_unreasoned.rdf` (tracked): OWL2Bench RL, 1 university, with the KRROOD role
  modifications and the T20CricketFan definition. sha256 `8d387e661daa2883f8208e4012169a5f7819472f40d2b055612734931160998c`,
  54,901 statements in GraphDB.
* `resources/owl2bench_statements_reasoned.rdf` (not tracked): regenerate it from the OWL 2 RL closure computed by
  GraphDB: all explicit statements of the raw data plus the materialised OWL2Bench class and property assertions of
  the named individuals. (The full closure also contains axiomatic triples, e.g. classes typed `rdfs:Resource` and
  properties typed `rdf:Property`; owlready2 cannot load those and fails on 10 queries with `TypeError:
  FusionClass2() takes no arguments`. `--export-full-closure FILE` writes the full closure if needed.) Then load it
  into `aamas27_noinf`:

```bash
cd ~/krrood_experiments_aamas27
mv resources/owl2bench_statements_reasoned.rdf resources/owl2bench_statements_reasoned_jan.rdf 2>/dev/null
python scripts/aamas27/graphdb_setup.py --export-reasoned resources/owl2bench_statements_reasoned.rdf
# expected: "exported 54901 explicit statements and 1376734 materialised individual assertions ... (1431635 statements)"
grep -c T20CricketFan resources/owl2bench_statements_reasoned.rdf     # must be > 0 (21 locally)
python scripts/aamas27/graphdb_setup.py --setup-query-repositories    # creates/loads aamas27_noinf
sha256sum resources/*.rdf > results_checksums.txt
```

Verify: `"aamas27_noinf": {"ruleset": "empty", "explicit": 1431635, "total": 1431635}`. Locally the file has
118,437,767 bytes and sha256 `d80109621a494383a28a752064e76d0a9b3ae1b16a1f68e602c4e0b083bd1c1c`; the order of a
GraphDB export is not guaranteed, so compare the statement count rather than the checksum. The paper states
1,502,966 statements for the January file. The local copy of the January file (2026-01-03, a Protégé export,
sha256 `5d30e2c0cd851c929fa2ddaaf5dab5164fb8103f89b768209dfbdb2c914b68ef`) contains no T20CricketFan assertion; if
that was the file used in January, RDFLib and owlready2 cannot have returned 20 answers for Q5 with it (the nextcloud
download in README.md may be a different version).

### 5.4 With or without the component-propagation commit

The CRAM branch head (a6d22a95aa) sits on top of 2f721b0fbc, the commit that adds the facts of symmetric-transitive
components through the relation path (complete propagation and provenance). On OWL2Bench it changes no query answer,
but it raises the KRROOD loading time from about 17 s to 36 s and the peak memory from about 340 MB to 960 MB
(section 11). Run the experiments at the branch head. To report KRROOD without the component-propagation commit as well,
revert it on a temporary branch and repeat only the KRROOD loading measurements (with the environment of section 6):

```bash
cd ~/cram_aamas27 && git checkout -b aamas27-without-component-propagation && git revert --no-edit 2f721b0fbc
cd ~/krrood_experiments_aamas27
python scripts/aamas27/run_loading.py --systems krrood,krrood_ormatic --repetitions 5 --results-dir $RUN/loading_without_component_propagation
cd ~/cram_aamas27 && git checkout aamas27-experiments && cd ~/krrood_experiments_aamas27
```

## 6. Experiments

Always in the activated venv, with `PYTHONPATH` unset and the two environment variables set:

```bash
source ~/venvs/krrood_aamas27/bin/activate; unset PYTHONPATH; export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export KRROOD_GRAPHDB_URL=http://localhost:7200
export KRROOD_EXPERIMENTS_DATABASE_URI="postgresql+psycopg2://krrood_experiments:krrood_experiments@localhost:5432/krrood_experiments"
cd ~/krrood_experiments_aamas27
RUN=results/aamas27/$(hostname)-$(date +%Y%m%d)
```

### 6.1 Tests (1 min)

```bash
python -m pytest -q -o addopts="" tests/aamas27
```

Expected: `9 passed`.

### 6.2 Hard answer-set check (15-25 min)

```bash
python scripts/aamas27/run_queries.py --check-only --results-dir $RUN/check
```

Expected: every framework equal to GraphDB for all 18 queries (exit status 0); this is the result of the final
local check (section 11, `results/aamas27/bass-final-check-2`, about 7 min including set-up). If RDFLib or owlready2 differ, see `$RUN/check/answer_check.json`
(set sizes and the first 20 elements of both differences); `--allow-mismatch` lets the script exit with 0.

### 6.3 Query timing (10 repetitions)

```bash
python scripts/aamas27/run_queries.py --repetitions 10 --results-dir $RUN/queries
```

This repeats the answer-set check on the first repetition. owlready2 reloads the reasoned file before every
repetition (January behaviour, so that no result comes from a cache); `--owlready2-keep-world` loads it once.

### 6.4 Loading + reasoning, time and peak memory

```bash
python scripts/aamas27/run_loading.py --repetitions 5 --rdflib-timeout-seconds 10800 --results-dir $RUN/loading
```

Systems (in this order): `krrood` (Ontomatic loader, parsing + object creation + reasoning), `owlready2_pellet`
(load + `sync_reasoner_pellet(infer_property_values=True)`, Java heap 2000 MB as January, `--java-memory-mb` to
change), `rdflib_owlrl` (parse + `DeductiveClosure(OWLRL_Semantics).expand`), `graphdb` (fresh repository
`aamas27_load_<input>_owl2_rl_optimized`, upload in one request, ruleset recorded; deleted afterwards), and
`krrood_ormatic` (KRROOD + persisting all objects into PostgreSQL). Each input is `raw` and `reasoned`. GraphDB and
RDFLib run once per input (`--repetitions-per-system`), the others 5 times. A run that times out or fails is recorded
with its status and the remaining repetitions of that system/input are skipped. Memory: `peak_rss_mib` is the peak of
the summed RSS of the worker process and all its children (Pellet's JVM), sampled every 50 ms; for GraphDB it is the
peak RSS of the server JVM during the upload (`rss_before_bytes` and `peak_minus_before_mib` are recorded too; the
JVM's RSS mostly reflects its heap size and rarely shrinks, so report GraphDB memory with the -Xmx you used).

### 6.5 Ablation: no weakly-connected-components step (cap 2 h)

```bash
python scripts/aamas27/run_symmetric_transitive_ablation.py --memory-limit-gib 24 --results-dir $RUN/loading
```

Closes hasSameHomeTownWith (symmetric and transitive) eagerly while the facts are added, as before krrood commit
3b72ec1001 ("15 sec reasoning", 2026-01-14), instead of from the connected components. The paper's "100 minutes"
has no recorded source; report the measured time, or ">7200 s" if the run hits the cap.

### 6.6 Running 6.3-6.5 overnight

```bash
nohup bash -c "python scripts/aamas27/run_queries.py --repetitions 10 --results-dir $RUN/queries; \
  python scripts/aamas27/run_loading.py --repetitions 5 --rdflib-timeout-seconds 10800 --results-dir $RUN/loading; \
  python scripts/aamas27/run_symmetric_transitive_ablation.py --memory-limit-gib 24 --results-dir $RUN/loading" \
  > $RUN.log 2>&1 &
```

## 7. Protégé 5.6.7 + Pellet (manual)

1. Install the Pellet plug-in once: start Protégé (`~/Downloads/Protege-5.6.7-linux/Protege-5.6.7/run.sh`), File ->
   Check for plugins -> select "Pellet Reasoner Plug-in" (and "Snap SPARQL Query") -> Install, restart.
2. Heap: set `max_heap_size=28G` in `~/.Protege/conf/jvm.conf` (or `conf/jvm.conf` of the installation) and write the
   value into `protege.json` (`java_options`). The default is a quarter of the RAM (8 GB).
3. For each input (`resources/owl2bench_statements_unreasoned.rdf`, then `resources/owl2bench_statements_reasoned.rdf`)
   start a fresh Protégé under `/usr/bin/time` so that the peak RSS of the JVM is recorded:

   ```bash
   cd ~/Downloads/Protege-5.6.7-linux/Protege-5.6.7
   /usr/bin/time -v -o ~/protege_raw_time.txt ./run.sh
   ```

   File -> Open -> the file; Reasoner -> Pellet; Reasoner -> Start reasoner. Open the log (rightmost button in the
   status bar next to "Show Inferences") and write down the loading time and the reasoning time ("Ontologies
   processed in ... ms" or the Pellet timing lines). Do not run queries or export in this session. Quit Protégé;
   `Maximum resident set size (kbytes)` in `~/protege_raw_time.txt` is the peak memory of loading + reasoning.
   Repeat with `protege_reasoned_time.txt` for the reasoned file.
4. Queries (a separate session on the reasoned file, after Start reasoner): Window -> Views -> Query views -> Snap
   SPARQL Query; run each SPARQL query of `src/krrood_experiments/owl2bench/sparql_queries.py` (Q2-5, 7-16, 19-22) and
   note the time and the number of results; stop a query after 60 s and record "timeout".
5. Fill `scripts/aamas27/protege_template.json` (seconds = loading + reasoning, peak_rss_mib = kbytes / 1024, query
   times in ms) and save it as `$RUN/protege.json`.

## 8. LaTeX tables

```bash
python scripts/aamas27/make_tables.py --loading $RUN/loading/loading.json --queries $RUN/queries/queries.json \
    --protege $RUN/protege.json --output-dir $RUN/tables
```

Produces `loading_table.tex` (time mean ± std and peak memory, raw and reasoned), `query_table.tex` (results =
distinct GraphDB answers, a dagger marks queries whose answer sets differ between frameworks, mean ± std in ms, the
fastest in bold, geometric mean over the queries all frameworks completed, listed in a comment) and `summary.csv`.

## 9. What to send back

```bash
tar czf aamas27_results_$(hostname).tgz $RUN $RUN.log results_checksums.txt ~/protege_*_time.txt
```

That is: every `environment.json`, `loading.json`, `queries.json`, `queries_<framework>.json`,
`answer_check.json`, the `answers/` directories (gzipped answer sets, about 40 MB), `protege.json`, the tables and the
logs.

## 10. Troubleshooting

* `ImportError: cannot import name 'issubclass_or_role' from 'krrood.class_diagrams.wrapped_field'`: krrood is not the
  `aamas27-experiments` branch (plain `origin/dl` has this bug).
* `ImportError: cannot import name 'RDRDecorator' from 'ripple_down_rules'`: ripple_down_rules was installed
  non-editable; reinstall with `pip install -e`.
* `ModuleNotFoundError` for ROS packages or wrong package versions: `unset PYTHONPATH`.
* `RulesetMismatchError`: an `aamas27_*` repository exists with another ruleset; delete it with
  `python scripts/aamas27/graphdb_setup.py --delete <repository>`.
* GraphDB upload fails with a license error: check `curl -s localhost:7200/rest/graphdb-settings/license`.
* `psycopg2.OperationalError`: the container is not running (`docker start krrood-pg`) or the URI is wrong.
* A worker is killed with `status: memory_limit` only when `--memory-limit-gib` was given; `failed` with return code
  -9 means the kernel OOM killer stopped it (report "o.o.m.").
* The answer-set check exits with 1: read `answer_check.json`; do not use `--allow-mismatch` for the paper numbers
  without explaining the difference.
* Clean up: `docker rm -f krrood-pg`; `kill $(cat ~/graphdb_aamas27.pid)`; delete the `aamas27_*` repositories in the
  Workbench if no longer needed.

## 11. Results on the development machine (correctness, memory and same-machine deltas only)

Machine: hostname `bass`, 12th Gen Intel Core i7-12700H, 15.3 GB RAM (about 9 GB used by other work), Ubuntu
24.04.4, Python 3.12.3, GraphDB 11.2.0 Free (1 core, -Xmx3g, port 7333), PostgreSQL 18.1 (Docker). These timings
are not comparable with the original machine. Result files: `results/aamas27/bass-*` in the EXP worktree used for
the development (not committed).

Code states: before = CRAM 3685d1e0c3 (`origin/dl` + import fix) with EXP 0d53ec7 (`Tom/main` model); after =
CRAM a6d22a95aa with EXP 0d84891 (and the new query definitions in both cases).

**Hard answer-set check** (one repetition, reference GraphDB `aamas27_rl`, 18 queries):

| Query | GraphDB | before: EQL / SQLAlchemy | after: EQL / SQLAlchemy | after: RDFLib / owlready2 |
|-------|---------|--------------------------|-------------------------|---------------------------|
| Q2, Q3, Q4, Q5, Q7, Q8, Q9, Q10, Q11, Q13, Q15, Q16, Q19, Q20, Q21, Q22 | 7421, 55, 2486, 20, 1684, 6, 0, 666, 2422, 0, 21, 21, 858, 1311932, 145, 106 | equal | equal | equal |
| Q12 | 2494 | 2487 (missing U0RG0 ... U0RG6) | equal | equal |
| Q14 | 0 | 53 (unsound LeisureStudent) | equal | equal |

SQLAlchemy "before" already uses the corrected projections (section 1); with the January statements Q2, Q15, Q16
differ in shape and Q22 returned 12 of 106 answers. EQL and SQLAlchemy return 141 rows for the 106 distinct answers
of Q22.

**Soundness audit** (`python -m krrood_experiments.aamas27.soundness_audit`): every class membership and object
property assertion of KRROOD compared with the OWL 2 RL closure of GraphDB.

| | class memberships not entailed | entailed memberships missing | property facts not entailed | entailed property facts missing |
|-|--------------------------------|------------------------------|-----------------------------|---------------------------------|
| before | 67 (53 LeisureStudent, 14 class-name heuristic) | 226 (PeopleWithHobby 181, BasketBallLover 31, Employee 7, Person 7) | 0 | 4037 |
| after (a6d22a95aa) | 0 | 0 | 0 | 4037 (section 2) |

All 3667 named individuals of the closure are represented in KRROOD.

**KRROOD loading (raw data), 5 fresh processes per state, interleaved, nothing else running:**

| State (CRAM commit) | Loading + reasoning [s] | Peak RSS |
|---------------------|-------------------------|----------|
| before (3685d1e0c3) | 15.00 ± 0.33 | 335 MB |
| soundness fixes 1-3 + implicit subsumptions (7ce1541932) | 15.01 ± 0.19 | 335 MB |
| + provenance (46830ff78a) | 15.22 ± 0.26 | 337 MB |
| + complete type inference (a4b5c8f755) | 16.81 ± 0.07 | 339 MB |
| + component facts through the relation path (2f721b0fbc) | 35.94 ± 0.19 | 961 MB |
| + no class-name typing (a6d22a95aa, branch head; separate 5 runs) | 35.69 ± 0.38 | 961 MB |

**Loading + reasoning of the raw data, one fresh process each (peak RSS of the process tree):**

| System | Time [s] | Peak memory |
|--------|----------|-------------|
| KRROOD (branch head) | 35.9 (see above) | 961 MB |
| KRROOD + ORMatic, persisting into PostgreSQL (branch head)* | 34.6 loading + 44.1 persisting | 2.16 GB |
| owlready2 + Pellet (Java heap 2000 MB)* | 61.1 | 2.26 GB |
| RDFLib + owlrl* | did not finish within the 30 min cap | 860 MB when stopped |
| GraphDB, owl2-rl-optimized (server JVM, -Xmx3g, 1 core) | 2552 (a second load: 2583) | 2.55 GB peak RSS, +0.86 GB during the load |

\* measured while the GraphDB measurement ran on another core (CPU contention possible; memory unaffected).
The paper reports 36.0 s for RDFLib + owlrl on the raw data; on this machine owlrl did not finish in 30 min. Measure
it on the original machine with the 3 h cap. The reasoned input was not measured here (memory).

**Ablation** (eager closure of hasSameHomeTownWith, no connected components): stopped by the 30 min cap after 75 % of the
property assignments (single hasSameHomeTownWith assignments took up to 387 s), peak RSS 651 MB. The connected-
components version needs 15-17 s. Measure the full run on the original machine with the 2 h cap.

**ResearchGroup typing (Q12):** the OWL 2 RL closure types the 7 ResearchGroups as Employee and Person through
`U0RG0 hasResearchProject U0RG0RP` (asserted), `hasResearchProject rdfs:subPropertyOf hasWork` (prp-spo1:
`U0RG0 hasWork U0RG0RP`), `hasWork rdfs:domain Employee` (prp-dom: `U0RG0 a Employee`), `Employee rdfs:subClassOf
Person` (cax-sco: `U0RG0 a Person`). Verified in GraphDB (`aamas27_rl`: `U0RG0 hasWork U0RG0RP` and `U0RG0 a
Employee, Person` are inferred) and with owlrl on exactly these four TBox/ABox triples. This is plain RDFS reasoning,
not specific to the owl-max ruleset. KRROOD after the fixes derives the same types (the ResearchGroup individual gets
an Organization object and, as a role, an Employee/Person object).

