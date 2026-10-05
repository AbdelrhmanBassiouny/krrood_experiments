"""
Create, load, verify and export the GraphDB repositories used by the AAMAS 2027 OWL2Bench experiments.

Only repositories whose name starts with ``aamas27_`` are touched. Examples::

    # create the two repositories and load the data used by the query experiment
    python scripts/aamas27/graphdb_setup.py --setup-query-repositories

    # show rulesets and statement counts
    python scripts/aamas27/graphdb_setup.py --status

    # regenerate the reasoned data file from the OWL 2 RL closure computed by GraphDB (explicit statements plus the
    # materialised class and property assertions of the named individuals)
    python scripts/aamas27/graphdb_setup.py --export-reasoned resources/owl2bench_statements_reasoned.rdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

from krrood_experiments.aamas27.environment import UNREASONED_FILE, REASONED_FILE
from krrood_experiments.aamas27.graphdb import GraphDBClient

RL_REPOSITORY = "aamas27_rl"
"""
Raw data loaded with the OWL2-RL (Optimized) ruleset. Reference for the answer-set check.
"""

NO_INFERENCE_REPOSITORY = "aamas27_noinf"
"""
Reasoned data loaded with the No-inference (empty) ruleset.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=None, help="GraphDB base URL (default: $KRROOD_GRAPHDB_URL or http://localhost:7200)")
    parser.add_argument("--setup-query-repositories", action="store_true",
                        help=f"create {RL_REPOSITORY} (owl2-rl-optimized, raw data) and {NO_INFERENCE_REPOSITORY} "
                             f"(empty ruleset, reasoned data) if missing and load them if empty")
    parser.add_argument("--create", nargs=2, metavar=("REPOSITORY", "RULESET"), help="create a managed repository")
    parser.add_argument("--load", nargs=2, metavar=("REPOSITORY", "FILE"), help="load an RDF/XML file into a managed repository")
    parser.add_argument("--clear", metavar="REPOSITORY", help="remove all statements of a managed repository")
    parser.add_argument("--delete", metavar="REPOSITORY", help="delete a managed repository")
    parser.add_argument("--status", action="store_true", help="print rulesets and statement counts")
    parser.add_argument("--export-reasoned", metavar="FILE",
                        help=f"write the reasoned data file: explicit statements of {RL_REPOSITORY} plus the "
                             f"materialised class and property assertions of its named individuals (RDF/XML)")
    parser.add_argument("--export-full-closure", metavar="FILE",
                        help=f"export every statement of {RL_REPOSITORY}, including axiomatic triples (RDF/XML)")
    parser.add_argument("--unreasoned-file", default=str(UNREASONED_FILE))
    parser.add_argument("--reasoned-file", default=str(REASONED_FILE))
    arguments = parser.parse_args()

    client = GraphDBClient(arguments.url) if arguments.url else GraphDBClient()

    if arguments.delete:
        client.delete_repository(arguments.delete)
    if arguments.create:
        client.create_repository(*arguments.create)
    if arguments.clear:
        client.clear(arguments.clear)
    if arguments.load:
        seconds = client.load_file(arguments.load[0], Path(arguments.load[1]))
        print(f"loaded {arguments.load[1]} into {arguments.load[0]} in {seconds:.1f} s")
    if arguments.setup_query_repositories:
        for repository_id, ruleset, data_file in [
            (RL_REPOSITORY, "owl2-rl-optimized", Path(arguments.unreasoned_file)),
            (NO_INFERENCE_REPOSITORY, "empty", Path(arguments.reasoned_file)),
        ]:
            client.create_repository(repository_id, ruleset)
            if client.count_statements(repository_id)["explicit"] == 0:
                if not data_file.exists():
                    print(f"skipping {repository_id}: {data_file} does not exist", file=sys.stderr)
                    continue
                seconds = client.load_file(repository_id, data_file)
                print(f"loaded {data_file} into {repository_id} ({ruleset}) in {seconds:.1f} s")
    if arguments.export_reasoned:
        export(client, Path(arguments.export_reasoned))
    if arguments.export_full_closure:
        export_full(client, Path(arguments.export_full_closure))
    if arguments.status or arguments.setup_query_repositories:
        status = {}
        for repository_id in client.repository_ids():
            entry = {"ruleset": client.ruleset(repository_id)}
            if repository_id.startswith("aamas27_"):
                entry.update(client.count_statements(repository_id))
            status[repository_id] = entry
        print(json.dumps({"version": client.version(), "repositories": status}, indent=2))
    return 0


INFERRED_ABOX_QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT { ?s ?p ?o }
WHERE {
  ?s a owl:NamedIndividual .
  ?s ?p ?o .
  FILTER ((?p = rdf:type && STRSTARTS(STR(?o), "http://benchmark/OWL2Bench#"))
          || STRSTARTS(STR(?p), "http://benchmark/OWL2Bench#"))
}
"""
"""
The materialised assertions about the named individuals: their OWL2Bench class memberships and their OWL2Bench
object and data property values. Axiomatic and schema-level triples of the closure (e.g. classes typed as
rdfs:Resource, properties typed as rdf:Property) are left out, owlready2 cannot load them (punning).
"""


def export(client: GraphDBClient, target: Path) -> None:
    """
    Write the reasoned data file: all explicit statements of the raw data (ontology and assertions) plus the
    materialised assertions of the OWL 2 RL closure about the named individuals (:data:`INFERRED_ABOX_QUERY`), as
    RDF/XML.

    :param client: The GraphDB client.
    :param target: The output file.
    """
    import rdflib

    graph = rdflib.Graph()
    explicit = requests.get(
        f"{client.endpoint(RL_REPOSITORY)}/statements",
        params={"infer": "false"},
        headers={"Accept": "application/n-triples"},
        timeout=client.timeout_seconds,
    )
    explicit.raise_for_status()
    graph.parse(data=explicit.text, format="nt")
    explicit_count = len(graph)
    inferred = requests.post(
        client.endpoint(RL_REPOSITORY),
        data={"query": INFERRED_ABOX_QUERY},
        headers={"Accept": "application/n-triples"},
        timeout=client.timeout_seconds,
    )
    inferred.raise_for_status()
    graph.parse(data=inferred.text, format="nt")
    graph.serialize(destination=str(target), format="xml")
    print(f"exported {explicit_count} explicit statements and {len(graph) - explicit_count} materialised individual "
          f"assertions of {RL_REPOSITORY} ({len(graph)} statements) to {target}")


def export_full(client: GraphDBClient, target: Path) -> None:
    """
    Export all statements (explicit and inferred, including axiomatic triples) of the OWL 2 RL repository as RDF/XML.

    :param client: The GraphDB client.
    :param target: The output file.
    """
    response = requests.get(
        f"{client.endpoint(RL_REPOSITORY)}/statements",
        params={"infer": "true"},
        headers={"Accept": "application/rdf+xml"},
        stream=True,
        timeout=client.timeout_seconds,
    )
    response.raise_for_status()
    with open(target, "wb") as stream:
        for block in response.iter_content(2**20):
            stream.write(block)
    print(f"exported {RL_REPOSITORY} (explicit + inferred) to {target}")


if __name__ == "__main__":
    sys.exit(main())
