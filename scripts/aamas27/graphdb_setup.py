"""
Create, load, verify and export the GraphDB repositories used by the AAMAS 2027 OWL2Bench experiments.

Only repositories whose name starts with ``aamas27_`` are touched. Examples::

    # create the two repositories and load the data used by the query experiment
    python scripts/aamas27/graphdb_setup.py --setup-query-repositories

    # show rulesets and statement counts
    python scripts/aamas27/graphdb_setup.py --status

    # regenerate the reasoned data file from the OWL 2 RL closure computed by GraphDB
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
                        help=f"export explicit and inferred statements of {RL_REPOSITORY} as RDF/XML")
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
    if arguments.status or arguments.setup_query_repositories:
        status = {}
        for repository_id in client.repository_ids():
            entry = {"ruleset": client.ruleset(repository_id)}
            if repository_id.startswith("aamas27_"):
                entry.update(client.count_statements(repository_id))
            status[repository_id] = entry
        print(json.dumps({"version": client.version(), "repositories": status}, indent=2))
    return 0


def export(client: GraphDBClient, target: Path) -> None:
    """
    Export all statements (explicit and inferred) of the OWL 2 RL repository as RDF/XML.

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
