# KRROOD: supplementary material

Code, data and scripts for the AAMAS 2027 submission "Implementing Knowledge Representation and Reasoning with
Object Oriented Design". Everything runs in Docker, with one command per experiment.

## Contents

| Path | What |
|------|------|
| `code/earlier/krrood` | The earlier version of KRROOD: EQL, Ontomatic (Section 5, Algorithm 1) and ORMatic. All experiments (Section 7) use this version. |
| `code/earlier/ripple_down_rules` | Rule-base library that Ontomatic's model generator uses (Section 5, TBox compilation). |
| `code/earlier/experiments` | The experiments: the generated OWL2Bench model, the 18 queries of every system (`src/krrood_experiments/owl2bench/`), the measurement scripts (`scripts/aamas27/`) and their tests. |
| `code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf` | OWL2Bench, OWL 2 RL profile, one university, with the role markers and the `T20CricketFan` definition (Section 7). |
| `code/current/krrood` | The current version of KRROOD. The paper's listings use it. Its EQL API differs from the earlier version in the names of some constructors, and its translator from EQL to SQL (Section 6) handles collection-valued attributes. |
| `listings/` | Executable versions of the paper's listings, as tests on the current version. `listings/ormatic/` tests the listing of Section 6 (one query in working memory and translated to SQL). |
| `results/` | The results of the measured run reported in the paper: raw measurements (JSON), the answer-set check, the comparison with the OWL 2 RL closure, the environment record and the LaTeX tables. |
| `Dockerfile`, `compose.yaml`, `reproduce.sh` | The container: GraphDB 11.2 (official image, Ubuntu 24.04, Java 21), Python 3.12.3 with both versions of KRROOD in separate virtual environments, and PostgreSQL 18.1 in a second container. |
| `environment/` | The exact versions of all Python packages of both environments. |

## Requirements

* Docker with Compose (Docker Engine 24 or later). 32 GB RAM for the full run (`all`); 8 GB suffice for `listings`
  and `check`. About 15 GB of free disk space.
* For `check` and `all`: a GraphDB license file. GraphDB 11 needs one even for its free edition; a free license
  can be requested from the GraphDB website. We cannot distribute one.

## Running

```bash
unzip krrood-aamas27-supplement.zip && cd krrood-aamas27-supplement && mkdir -p state
docker compose build                                  # about 5-10 min
docker run --rm krrood-aamas27 listings              # the listing tests, a few seconds, no license needed
export GRAPHDB_LICENSE=/path/to/graphdb.license
docker compose run --rm experiments check             # about 1-1.5 h
docker compose run --rm experiments all               # about 9-13 h, includes check
docker compose down
```

All output goes to `./state`: the log `reproduce.log`, the results in `results/aamas27/run/`, and the archive
`aamas27_results.tgz`. A second call resumes after the last finished step; delete `./state` to start over.

### What `check` verifies (Section 7.1)

1. The tests of the measurement scripts and the listing tests pass.
2. GraphDB computes the OWL 2 RL closure of the raw data (`aamas27_rl`: 54,901 explicit statements); its export is
   the pre-reasoned input of the other systems (1,431,635 statements).
3. Answer-set check: for each of the 18 queries, the answers of EQL, SQL over ORMatic, RDFLib and Owlready2 are
   normalized to sets of tuples and compared with GraphDB's. The script fails on any difference
   (`results/aamas27/run/check/answer_check.json`).
4. The knowledge base that Ontomatic loads is compared with GraphDB's closure, assertion by assertion
   (`results/aamas27/run/audit/audit.json`). Expected: 3,667 individuals; 17,558 class memberships, 1,385,869
   object-property and 20,933 data-property assertions, none missing and none extra; the check of the equality and
   inconsistency rules passes.

### What `all` measures (Sections 7.2 and 7.3)

* Query time, 18 queries x 10 repetitions, for EQL, SQL (SQLAlchemy over the ORMatic schema in PostgreSQL),
  GraphDB, RDFLib and Owlready2 (`queries/queries.json`, Table 4).
* Loading and reasoning time and peak memory, from raw and from pre-reasoned data, for KRROOD, KRROOD + ORMatic,
  Owlready2 + Pellet, RDFLib + owlrl (3 h limit) and GraphDB (`loading/loading.json`, Table 3). Peak memory is the
  peak resident set size of the process tree, sampled every 50 ms; for GraphDB, that of its server.
* The ablation that replaces step 5 of Algorithm 1 by eager chaining (2 h limit).

Protégé with Pellet has a graphical interface and was measured by hand: the loading and reasoning time from its log
and the peak memory with `/usr/bin/time -v`, using `./state/owl2bench_statements_reasoned.rdf` and the raw data
file. Its numbers are in `results/aamas27/run/protege.json`; with this file in `./state/results/aamas27/run/`,
`docker compose run --rm experiments tables` adds them to the tables.

Timings depend on the machine. The paper's numbers were measured with this container on an Intel Core i7-11700K
with 32 GB RAM under Ubuntu 24.04, with nothing else running.

## Settings

Environment variables of `docker compose run`: `GRAPHDB_HEAP` (default `8g`), `QUERY_REPETITIONS` (10),
`LOADING_REPETITIONS` (5), `RDFLIB_TIMEOUT_SECONDS` (10800).
