# KRROOD: supplementary material

Code, data and scripts for the AAMAS 2027 submission "Implementing Knowledge Representation and Reasoning with
Object Oriented Design". Everything runs in Docker.

KRROOD is the paper's framework: the agent's Python program is its knowledge base. Its parts, as named in the paper,
are EQL (a query language embedded in Python), Ontomatic (compiles OWL 2 RL ontologies into Python classes and loads
their individuals) and ORMatic (stores the objects in a relational database and translates EQL to SQL).

There are three levels, from a few minutes to a night:

| Level | Command | Needs | Time | Reproduces |
|-------|---------|-------|------|------------|
| 1 | `listings` | Docker | 5-15 min (the first build downloads about 1.5 GB) | the paper's listings and the formalization's examples, as tests |
| 2 | `check` | Docker, a free GraphDB license, 16 GB RAM | 1-1.5 h | Section 7.1: answers of all 18 queries, and the knowledge base compared with the OWL 2 RL closure |
| 3 | `all` | as level 2, 32 GB RAM | 9-13 h | also Sections 7.2-7.3: query time, loading time and memory, the ablation |

Our own results are in `results/` and can be read without running anything. Without a GraphDB license, level 1
and these results are what you can check.

## Requirements

* **Docker with Compose v2** (`docker compose version` prints v2.x). On Linux, your user must be in the `docker`
  group (`sudo usermod -aG docker $USER`, then log out and back in). Tested on Linux x86_64 (Ubuntu 24.04); the
  images also exist for arm64.
* **Memory:** `check` needs about 12 GB for Docker with `GRAPHDB_HEAP=4g` (so a 16 GB machine is enough), and
  `all` about 28 GB with the default heap of 8 GB. On Docker Desktop (macOS, Windows), raise the memory limit in
  Settings -> Resources accordingly.
* **Disk:** about 15 GB free. GraphDB stops answering when less than 10 % of the disk is free.
* **For levels 2 and 3, a GraphDB license file.** GraphDB 11 needs one even for its free edition, and we cannot
  distribute ours. Request GraphDB Free on the download page of the GraphDB website (https://graphdb.ontotext.com/);
  the license arrives by e-mail. Save it anywhere, e.g. `~/graphdb.license`.

## Level 1: the listing tests (no license)

In a terminal, in the folder that contains the zip:

```bash
unzip -DD krrood-aamas27-supplement.zip && cd krrood-aamas27-supplement   # -DD: see Troubleshooting
mkdir -p state                       # the results folder; create it yourself so that you own its files
docker compose build                 # 5-15 min the first time (downloads about 1.5 GB)
docker run --rm krrood-aamas27 listings   # krrood-aamas27 is the image that the build created
```

Expected: `24 passed`, then `1 passed`. All later commands are run in the same folder
(`krrood-aamas27-supplement`).

## Level 2: the correctness check (Section 7.1)

```bash
export GRAPHDB_LICENSE=~/graphdb.license      # the path of your license file
GRAPHDB_HEAP=4g docker compose run --rm experiments check
docker compose down
```

With 32 GB RAM or more, leave out `GRAPHDB_HEAP=4g` (the default heap is 8 GB). Most of the time goes into
GraphDB computing the OWL 2 RL closure (30-60 min). The log is printed and also written to `state/reproduce.log`.
It ends like this (`...` stands for lines left out here):

```
...
individuals 3667 3667
classes {'krrood': 17558, 'reference': 17558, 'unsound': 0, 'missing': 0}
object_properties {'krrood': 1385869, 'reference': 1385869, 'unsound': 0, 'missing': 0}
data_properties {'krrood': 20933, 'reference': 20933, 'unsound': 0, 'missing': 0}
{'passed': True, 'equalities': 0, 'inconsistencies': 0}
...
finished mode check
```

The run succeeded if its last line is `finished mode check`. Any failure stops the run with a line starting with
`FAILED:`, which says what went wrong. A failed or interrupted run does no harm: fix the cause and run the same
command again; it resumes after the last finished step.

What `check` does:

1. It runs the tests of the measurement scripts (`24 passed`) and the listing tests.
2. GraphDB computes the OWL 2 RL closure of the raw data (repository `aamas27_rl`: 54,901 explicit and 1,467,912
   total statements). Its export is the pre-reasoned input of the other systems (1,431,635 statements).
3. **Answer-set check:** for each of the 18 queries, the answers of EQL, SQL over ORMatic, RDFLib and Owlready2 are
   normalized to sets of tuples and compared with GraphDB's. The step fails on any difference; details are in
   `state/results/aamas27/run/check/answer_check.json`.
4. **Knowledge base vs. closure:** the knowledge base that Ontomatic loads is compared with GraphDB's closure,
   assertion by assertion, and the OWL 2 RL rules that derive equalities or inconsistencies are checked
   (`state/results/aamas27/run/audit/audit.json`).

## Level 3: everything (Sections 7.1-7.3)

Run it in the background so that it survives closing the terminal, on an otherwise idle machine:

```bash
export GRAPHDB_LICENSE=~/graphdb.license
nohup docker compose run --rm -T experiments all > all.log 2>&1 &
tail -f state/reproduce.log                    # Ctrl+C stops watching, not the run
```

`all` includes `check` (finished steps are skipped). It then measures:

* query time, 18 queries x 10 repetitions, for EQL, SQL (SQLAlchemy over the ORMatic schema in PostgreSQL),
  GraphDB, RDFLib and Owlready2 (`queries/queries.json`, Table 4);
* loading and reasoning time and peak memory, from the raw and from the pre-reasoned data, for KRROOD,
  KRROOD + ORMatic, Owlready2 + Pellet, RDFLib + owlrl (3 h limit) and GraphDB (`loading/loading.json`, Table 3).
  Peak memory is the peak resident set size of the process tree, sampled every 50 ms; for GraphDB, of its server;
* the ablation that replaces step 5 of Algorithm 1 by eager chaining (2 h limit).

The LaTeX tables are written to `state/results/aamas27/run/tables/`, and everything is packed into
`state/aamas27_results.tgz`. Afterwards run `docker compose down`. Timings depend on the machine; ours are from an
Intel Core i7-11700K with 32 GB RAM under Ubuntu 24.04.

### Protégé (by hand)

Protégé 5.6 with Pellet has a graphical interface, so it runs outside Docker. It needs the pre-reasoned file that
`check` (or `all`) writes:

1. Install the Pellet plug-in and "Snap SPARQL Query" (File -> Check for plugins), and set `max_heap_size=28G` in
   `~/.Protege/conf/jvm.conf`.
2. For `code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf`, and then for
   `state/owl2bench_statements_reasoned.rdf` (written by `check`), start a fresh Protégé with
   `/usr/bin/time -v -o protege_time.txt ./run.sh`, open the file, select Reasoner -> Pellet and Reasoner -> Start
   reasoner. The log gives the loading and reasoning time; `Maximum resident set size` in `protege_time.txt` gives
   the peak memory.
3. On the reasoned file, after Start reasoner, run the 18 SPARQL queries of
   `code/earlier/experiments/src/krrood_experiments/owl2bench/sparql_queries.py` in Snap SPARQL (60 s limit each).
4. Fill in `code/earlier/experiments/scripts/aamas27/protege_template.json`, save it as
   `state/results/aamas27/run/protege.json`, and run `docker compose run --rm experiments tables` to add the rows to
   the tables.

## Settings

Set them before `docker compose run`, e.g. `GRAPHDB_HEAP=4g docker compose run --rm experiments check`:
`GRAPHDB_HEAP` (8g), `QUERY_REPETITIONS` (10), `LOADING_REPETITIONS` (5), `RDFLIB_TIMEOUT_SECONDS` (10800).

A second call of `check` or `all` resumes after the last finished step. To start over, delete `state/`.

## Troubleshooting

| Message | Fix |
|---------|-----|
| `permission denied ... docker.sock` | Your user is not in the `docker` group yet: `sudo usermod -aG docker $USER`, then log out and back in. |
| `FAILED: no GraphDB license mounted` | Set `GRAPHDB_LICENSE` to the full path of your license file, in the same terminal as the `docker compose run`. |
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
| `code/earlier/experiments` | The experiments: the generated OWL2Bench model, the 18 queries of every system (`src/krrood_experiments/owl2bench/`), the measurement scripts (`scripts/aamas27/`) and their tests. |
| `code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf` | OWL2Bench, OWL 2 RL profile, one university, with the role markers and the `T20CricketFan` definition (Section 7). |
| `code/current/krrood` | The current version of KRROOD, which the paper's listings use. Its EQL API differs from the earlier version in the names of some constructors, and its translator from EQL to SQL (Section 6) handles collection-valued attributes. |
| `listings/` | Executable versions of the paper's listings, as tests on the current version. `listings/ormatic/` tests the listing of Section 6 (one query in working memory and translated to SQL). |
| `results/` | Our measured run: raw measurements (JSON), the answer-set check, the comparison with the closure, the environment record, the LaTeX tables, and in `host/` the machine's details and a 30-second record of its load during the run. Of the answer sets, `check/answers/graphdb/` holds GraphDB's, the reference; the other systems' sets are equal to them (`check/answer_check.json`) and are left out for size. |
| `Dockerfile`, `compose.yaml`, `reproduce.sh` | The container: GraphDB 11.2 (official image, Ubuntu 24.04, Java 21), Python 3.12.3 with both versions of KRROOD in separate virtual environments, and PostgreSQL 18.1 in a second container. `reproduce.sh` runs inside it. |
| `environment/` | The exact versions of all Python packages of both environments. |
| `formalization/` | The formalization of EQL: the full definitions of its syntax and semantics, and its complexity with references, which the paper's Section 4 summarizes (`eql_formalization.pdf`, and its LaTeX source). |
| `AI_USE.md` | How AI tools were used, as the AAMAS 2027 policy asks. |
