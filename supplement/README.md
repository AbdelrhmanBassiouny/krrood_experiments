# KRROOD: supplementary material

Code, data and scripts for the AAMAS 2027 submission "Implementing Knowledge Representation and Reasoning with
Object Oriented Design". Everything runs in Docker.

KRROOD is the paper's framework: the agent's Python program is its knowledge base. Its parts, as named in the paper,
are EQL (a query language embedded in Python), Ontomatic (compiles OWL 2 RL ontologies into Python classes and loads
their individuals) and ORMatic (stores the objects in a relational database and translates EQL to SQL).

There are two ways to run it:

| Command | Runs | Needs | Time |
|---------|------|-------|------|
| `quick` (the default) | the test suites, the paper's listings, the ablation on small data, the answers of EQL and SQL compared with GraphDB's, KRROOD's loading time and memory | Docker, 8 GB RAM | about 10 min, after a build of 5-15 min |
| `full` (or `all`) | everything in the paper (Sections 7.1-7.3) | Docker, 32 GB RAM, a free GraphDB license | 9-13 h |

Both end with a **report**: the results as numbered tables with titles and captions, next to the numbers of the
paper's run. It is printed in the terminal and written to `state/results/REPORT.md`. `full` without a GraphDB
license runs everything that does not need GraphDB, and the report lists the steps it skipped and says how to get
a license.

Our own results are in `results/` and can be read without running anything; `results/REPORT.md` is their report.

## Requirements

* **Docker with Compose v2** (`docker compose version` prints v2.x). On Linux, your user must be in the `docker`
  group (`sudo usermod -aG docker $USER`, then log out and back in). On Ubuntu, `run_ubuntu.sh` does this for you.
  Tested on Linux x86_64 (Ubuntu 24.04); the images also exist for arm64.
* **Memory:** `quick` needs about 8 GB, `full` about 28 GB with GraphDB's default heap of 8 GB (`GRAPHDB_HEAP=4g`
  lowers it). On Docker Desktop (macOS, Windows), raise the memory limit in Settings -> Resources accordingly.
* **Disk:** about 15 GB free. GraphDB stops answering when less than 10 % of the disk is free.
* **For the parts of `full` that use GraphDB, a GraphDB license file.** GraphDB 11 needs one even for its free
  edition, and we cannot distribute ours. Request GraphDB Free on https://graphdb.ontotext.com/; the license arrives
  by e-mail. Save it, e.g. as `~/graphdb.license`.

## Quick: about 10 minutes, no license

On Ubuntu, in the folder that contains the zip:

```bash
unzip -DD krrood-aamas27-supplement.zip && cd krrood-aamas27-supplement   # -DD: see Troubleshooting
bash run_ubuntu.sh
```

On any system with Docker:

```bash
unzip -DD krrood-aamas27-supplement.zip && cd krrood-aamas27-supplement
mkdir -p state                     # the results folder; create it yourself so that you own its files
docker compose build               # 5-15 min the first time (downloads about 1.5 GB)
docker compose run --rm experiments
docker compose down
```

Quick mode:

1. runs the tests of the measurement scripts (`24 passed`), the paper's listings and the formalization's examples
   (`25 passed`, then `1 passed` for the ORMatic listing of Section 6);
2. runs eager chaining, the ablation "KRROOD without step 5", on the OWL2Bench TBox with small synthetic data
   (`9 passed`: it terminates, derives the same facts as step 5, each fact once) and measures how its work grows
   with the size of a group of persons who share a home town (cubically; a table of the report);
3. loads OWL2Bench into KRROOD, runs the 18 queries in EQL (in working memory) and in SQL (over the objects that
   ORMatic persisted in PostgreSQL), and compares each answer set with the one GraphDB returned in our run
   (`results/check/answers/graphdb/`);
4. measures the loading and reasoning of KRROOD and of Nemo, an in-memory Datalog engine with the OWL 2 RL/RDF
   rules, from the raw data (5 runs each), and their memory increase.
5. runs KRROOD's two variants of the agent loop (the delivery robot of Section 7.4) for 20 steps.

The run succeeded if it ends with `finished mode quick`. A failure stops it with a line starting with `FAILED:`,
which says what went wrong, followed by the report of what was finished.

## Full: everything in the paper (Sections 7.1-7.3)

Run it on an otherwise idle machine: it measures time. Screen lock is fine; logging out stops it.

### On Ubuntu: one command

In the unpacked folder:

```bash
bash run_ubuntu.sh full        # set up, then start the full run in the background
bash run_ubuntu.sh status      # any time: is the run going, finished steps, the end of the log
bash run_ubuntu.sh report      # any time: the report of the results so far
```

The script (tested on Ubuntu 24.04):

1. installs Docker from Ubuntu's packages if needed (it asks for your password), adds you to the `docker` group
   and continues with the group active, so you don't need to log out;
2. builds the image and checks that it holds this bundle's code; checks for 15 GB of free disk;
3. finds the GraphDB license: `GRAPHDB_LICENSE` if set, else `~/graphdb.license`, `~/Downloads/graphdb.license`,
   `~/.graphdb/work/graphdb.license`, else a `*.license` file under `~` or `/opt` with "graphdb" in its path, and
   starts GraphDB once to check that it accepts the license. Without a license, or with one that GraphDB rejects,
   it warns, says how to get one, and continues without GraphDB;
4. records the machine in `state/results/aamas27/run/host/`: `host.json` (CPU, frequency governor, turbo, power
   profile, memory, disk, OS, kernel, Docker version; no hostname or user name) and `graphdb_license.json`
   (what the license allows, e.g. its CPU core limit; not the licensee);
5. starts the run in the background, blocks suspend while it runs, and writes every 30 s to `host/monitor.csv`:
   load, memory and swap, mean CPU frequency, maximum temperature, and the programs outside Docker that used at
   least 5 % of a CPU (`busy_outside_docker`, which should stay empty).

If it stops with an error, the message says what is missing or shows the end of the log. Fix it and call the
script again: it never starts a second run, and a stopped run resumes after its last finished step.
`bash run_ubuntu.sh --dry-run` does everything except starting the run.

### On any system: by hand

```bash
export GRAPHDB_LICENSE=~/graphdb.license       # leave out without a license
nohup docker compose run --rm -T experiments full > all.log 2>&1 &
tail -f state/reproduce.log                    # Ctrl+C stops watching, not the run
```

`check` runs only the correctness part (Section 7.1, about 1-1.5 h with GraphDB).

### What it measures

With a GraphDB license, `full`:

* lets GraphDB compute the OWL 2 RL closure of the raw data (repository `aamas27_rl`: 54,901 explicit and
  1,467,912 total statements, 30-60 min); its export is the pre-reasoned input of the other systems (1,431,635
  statements);
* **answer-set check** (Section 7.1): for each of the 18 queries, the answers of EQL, SQL over ORMatic, RDFLib and
  Owlready2, normalized to sets of tuples, are compared with GraphDB's; the step fails on any difference
  (`check/answer_check.json`);
* **knowledge base vs. closure** (Section 7.1): the knowledge base that Ontomatic loads is compared with GraphDB's
  closure, assertion by assertion, and the OWL 2 RL rules that derive equalities or inconsistencies are checked
  (`audit/audit.json`);
* **query time** (Table 4): 18 queries x 10 repetitions, for EQL, SQL (SQLAlchemy over the ORMatic schema in
  PostgreSQL), GraphDB, RDFLib and Owlready2 (`queries/queries.json`);
* **loading and reasoning** (Table 3), from the raw and the pre-reasoned data: KRROOD (5 runs), KRROOD + ORMatic
  (5 runs), Owlready2 + Pellet (5 runs), RDFLib + owlrl (1 run, 3 h limit), GraphDB (1 run), and two in-memory
  baselines (5 runs, 24 GiB limit, `BASELINE_MEMORY_LIMIT_GIB`): Nemo 0.10.1, a Datalog engine, with the OWL 2 RL/RDF
  rules written for it (`code/earlier/experiments/src/krrood_experiments/aamas27/owl2rl.rls`), and reasonable 0.4.4,
  an OWL 2 RL reasoner written in Rust (`loading/loading.json`). Memory is the increase during loading: the peak resident set size of the process tree,
  sampled every 50 ms, minus that of a fresh worker after its imports (`memory/import_memory.json`); for KRROOD +
  ORMatic without the PostgreSQL server, which runs in its own container. GraphDB's server has a fixed heap, so
  for GraphDB it is the increase of its Java heap in use, from its GC log (`memory/graphdb_heap.json`);
* **the closures of Nemo and reasonable** from the raw data, compared with GraphDB's closure as KRROOD's knowledge
  base is (`baselines/closure_comparison.json`). Nemo's equals it. reasonable 0.4.4 applies the rule prp-ifp to any
  two subjects of an inverse-functional property, even with different objects, and so merges the heads of
  organizations, and it derives no facts from property chains. Nemo's rules follow the specification
  (Section 4.3 of OWL 2 Profiles) with two rewrites, commented in the file, without which Nemo did not finish:
  rule bodies use one predicate per RDF vocabulary term instead of a single triple predicate, and transitivity is
  written as a linear recursion. Neither changes what is derived;
* **the agent loop** (Section 7.4), about 1 h: a delivery robot on the OWL2Bench campus, 200 steps
  (`agent_loop/agent_loop.json`; the code is in `src/krrood_experiments/aamas27/agent_loop/`). OWL2Bench has no
  rooms, so a seeded campus map is generated (a building per college, a floor per department, classrooms, offices,
  two charging docks). The robot has a path planner (Dijkstra), a predicate `can_reach` (it can drive to a room and
  on to a dock with its remaining battery) and a function `travel_seconds`; its pose and battery are read live. Each
  step perceives three additions (a person enrolls in a department, a student takes a course, a person becomes crazy
  about T20 cricket), decides with two queries that need inferred facts (membership of a college through the chain
  `enrollIn` o `isPartOf`, and the class `T20CricketFan`) and call the planner, and acts (drives, delivers or
  charges). The same robot is built five ways: KRROOD, with the handout query scanning the students or navigating
  from the college; Python objects mirrored into GraphDB, with SPARQL for the logical part and the planner on the
  candidates; the same, but writing the planner's results into GraphDB so that SPARQL decides alone; and Python
  objects with reasonable, which recomputes the closure. The others carry out KRROOD's actions, so all see the same
  states, and their own decisions and candidates are compared with KRROOD's in every step: both GraphDB variants
  agree in all 200 steps; reasonable finds no handout candidates, as it derives no property chains. Facts are never
  removed, as KRROOD does not retract inferred facts. reasonable needs about 17 GB. Quick mode runs KRROOD's two
  variants for 20 steps; without a license, the GraphDB variants are skipped;
* **the ablation** that replaces step 5 of Algorithm 1 by forward chaining on every assignment (raw data, 1 run,
  2 h limit), and the same on small data as in quick mode.

Without a license, it runs the test suites, the ablation, EQL and SQL (answers compared with GraphDB's of our run,
and their query times), and the loading of KRROOD, KRROOD + ORMatic, Owlready2 and RDFLib from the raw data. The
rest needs GraphDB (the pre-reasoned data are GraphDB's closure); the report lists it.

Every mode also counts the lexical tokens of the 18 queries in EQL, SPARQL and SQLAlchemy as the benchmark writes
them (`tools/query_size.py`, `query_size.json`, a table of the report). The paper makes no claim about query size:
the EQL queries are about 2.4 times as long as SPARQL's in geometric mean, mostly because every variable is
declared with its class, and shorter than SQLAlchemy's on five of the 18 queries.

The run succeeded if `state/reproduce.log` ends with `finished mode full`. The LaTeX tables are written to
`state/results/aamas27/run/tables/` (the paper names two rows of the loading table differently: "KRROOD + ORMatic"
is "KRROOD (with ORMatic)", and "Eager chaining" is "KRROOD without step 5"), and everything is packed into
`state/aamas27_results.tgz`. Afterwards run `docker compose down`. Timings depend on the machine; ours are from an
Intel Core i7-13700 with 64 GB RAM under Ubuntu 24.04.

### Protégé (by hand)

Protégé has a graphical interface, so it runs outside Docker, and its numbers in the paper come from one session
each, by hand. It needs the pre-reasoned file that `full` (or `check`) writes. `results/protege/` holds our
sessions, the scripts we used and a README; in short:

1. Protégé 5.6.7 (Linux build with its own Java 11) with the plug-ins "Pellet Reasoner Plug-in" 2.2.0 and "Snap
   SPARQL Query" 6.0.0 from Protégé's plug-in registry (File -> Check for plugins, or copy the jars into
   `plugins/`; `results/protege/plugins.sha256` lists their checksums). In `~/.Protege/conf/jvm.conf`:
   `max_heap_size=28G` and `append=-Xlog:gc:file=<folder>/gc.log:time,uptime`.
2. For the raw data (`code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf`) and then for the
   pre-reasoned data (`state/owl2bench_statements_reasoned.rdf`), start a fresh Protégé
   (`results/protege/measure.sh` does this and records its memory), open the file, select Reasoner -> Pellet and
   Reasoner -> Start reasoner, and quit. Protégé's log (`~/.Protege/logs/protege.log`) gives the loading time
   ("completed in ... ms") and Pellet's ("Ontologies processed in ... ms"); the memory is the increase of the Java
   heap in use from the GC log (`results/protege/protege_heap_from_gc.py`).
3. In a fresh Protégé on the pre-reasoned data, after Start reasoner, run the 18 queries of
   `results/protege/queries_for_snap_sparql.txt` in Window -> Views -> Query views -> Snap SPARQL Query, once each,
   with a 60 s limit. Snap SPARQL shows the number of results, and Protégé's log has its time ("Evaluated BGP in
   ... ms"). Snap SPARQL rejects Q9, whose object `NonScience` is declared as a class.
4. Write the numbers into `state/results/aamas27/run/protege.json` (format: `results/protege.json`), and run
   `bash run_ubuntu.sh tables` (or `docker compose run --rm experiments tables`) to add them to the tables, the
   report and the results archive.

## Settings

Set them before `docker compose run`, e.g. `GRAPHDB_HEAP=4g docker compose run --rm experiments full`:
`GRAPHDB_HEAP` (8g), `QUERY_REPETITIONS` (10), `LOADING_REPETITIONS` (5), `RDFLIB_TIMEOUT_SECONDS` (10800),
`ABLATION_TIMEOUT_SECONDS` (7200). The paper's numbers use the defaults.

A second call of `check` or `full` resumes after the last finished step; `quick` always runs everything again.
To start over, delete `state/`.

## Troubleshooting

| Message | Fix |
|---------|-----|
| `permission denied ... docker.sock` | Your user is not in the `docker` group yet: `sudo usermod -aG docker $USER`, then log out and back in. |
| `WARNING: no GraphDB license` | Request GraphDB Free on https://graphdb.ontotext.com/ (the license arrives by e-mail) and set `GRAPHDB_LICENSE` to the full path of the file, in the same terminal as the `docker compose run`. Without it, the steps that need GraphDB are skipped. |
| `bind source path does not exist` | The path in `GRAPHDB_LICENSE` does not exist; check it with `ls -l "$GRAPHDB_LICENSE"`. |
| `GraphDB did not start` | See `state/graphdb.log` and `state/graphdb-home/logs/`. A rejected license or less than 10 % free disk are the usual causes. |
| A step is killed, or `status: memory_limit` / `failed` with return code -9 in `loading.json` | Not enough memory: lower `GRAPHDB_HEAP`, or raise Docker Desktop's memory limit. A baseline that runs out of memory within the limits is itself a result, recorded as such. |
| `FAILED: the code in the image does not match its BUNDLE id`, or `docker run --rm krrood-aamas27 fingerprint` prints another id than `cat environment/BUNDLE` | Docker built the image partly from files of an earlier version of this bundle: all files in the zip have the same time, so Docker takes a changed file of the same size for unchanged. Unzip with `-DD` (files get the current time), or run `docker builder prune -af`; then `docker compose build` again. |
| `state/` belongs to root | Create `state/` yourself before the first run (`mkdir -p state`), or `sudo chown -R $USER state`. |

## Contents

| Path | What |
|------|------|
| `code/earlier/krrood` | The earlier version of KRROOD: EQL, Ontomatic (Section 5, Algorithm 1) and ORMatic. All experiments (Section 7) use this version. |
| `code/earlier/ripple_down_rules` | Rule-base library that Ontomatic's model generator uses (Section 5, TBox compilation). |
| `code/earlier/experiments` | The experiments: the generated OWL2Bench model, the 18 queries of every system (`src/krrood_experiments/owl2bench/`), the measurement scripts (`scripts/aamas27/`) and their tests. `src/krrood_experiments/lubm/` holds a model generated from LUBM in earlier work; the paper does not evaluate LUBM, whose ontology uses class expressions outside OWL 2 RL (existential restrictions on the right-hand side of its class equivalences, such as `Chair`), and no step of this bundle uses it. |
| `code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf` | OWL2Bench, OWL 2 RL profile, one university, with the role markers and the `T20CricketFan` definition (Section 7). |
| `code/current/krrood` | The current version of KRROOD, which the paper's listings use. Its EQL API differs from the earlier version in the names of some constructors, and its translator from EQL to SQL (Section 6) handles collection-valued attributes. |
| `listings/` | Executable versions of the paper's listings, as tests on the current version. `listings/ormatic/` tests the listing of Section 6 (one query in working memory and translated to SQL). |
| `results/` | Our measured run: `REPORT.md` (its report), raw measurements (JSON), the answer-set check, the comparison with the closure, the environment record, the LaTeX tables, in `host/` the machine's details and a 30-second record of its load during the run, in `memory/` the memory after imports and GraphDB's heap from a separate load with a GC log, in `ablation_scaling/` the ablation on small data, in `protege/` the Protégé sessions, and `provenance.txt`, which says which numbers come from which run (KRROOD's loading was measured again in a clean rerun, as a browser had run during the first). Its `BUNDLE` id, `ae0b139a90267579`, differs from this bundle's because of three files in `code/current/` (the version the listing tests use, which gained idempotent rules); `code/earlier/`, which every measurement uses, is identical. Of the answer sets, `check/answers/graphdb/` holds GraphDB's, the reference; the other systems' sets are equal to them (`check/answer_check.json`) and are left out for size. |
| `run_ubuntu.sh` | The quick check and the full run on Ubuntu, in one command each (above). |
| `tools/` | Scripts of the container around the measurement scripts: the report (`report.py`), the size of the queries (`query_size.py`), EQL and SQL without a GraphDB server (`queries_without_graphdb.py`), the memory after imports (`import_memory.py`), GraphDB's heap from its GC log (`graphdb_heap.py`), and the ablation on small data with its tests (`ablation/`). |
| `Dockerfile`, `compose.yaml`, `reproduce.sh` | The container: GraphDB 11.2 (official image, Ubuntu 24.04, Java 21), Python 3.12.3 with both versions of KRROOD in separate virtual environments, and PostgreSQL 18.1 in a second container. `reproduce.sh` runs inside it. |
| `environment/` | The exact versions of all Python packages of both environments. |
| `formalization/` | The formalization of EQL: the full definitions of its syntax and semantics, and its complexity with references, which the paper's Section 4 summarizes (`eql_formalization.pdf`, and its LaTeX source). |
| `AI_USE.md` | How AI tools were used, as the AAMAS 2027 policy asks. |
