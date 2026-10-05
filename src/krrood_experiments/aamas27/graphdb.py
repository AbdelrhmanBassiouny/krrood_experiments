"""
Thin REST client for the GraphDB server used in the AAMAS 2027 OWL2Bench experiments.

Only repositories whose identifier starts with :data:`REPOSITORY_PREFIX` are ever created, cleared or deleted by this
module, so that existing user repositories (for example ``KRROOD``) are never modified.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import psutil
import requests

DEFAULT_GRAPHDB_URL = os.environ.get("KRROOD_GRAPHDB_URL", "http://localhost:7200")
"""
Base URL of the GraphDB server. Overridable with the environment variable ``KRROOD_GRAPHDB_URL``.
"""

REPOSITORY_PREFIX = "aamas27_"
"""
Prefix of every repository managed by the experiment scripts.
"""

RULESETS = {
    "owl2-rl-optimized": "OWL2-RL (Optimized)",
    "owl2-rl": "OWL2-RL",
    "owl-max-optimized": "OWL-Max (Optimized)",
    "owl-max": "OWL-Max",
    "empty": "No inference",
}
"""
GraphDB ruleset identifiers and the labels shown for them in the GraphDB Workbench.
"""

REPOSITORY_CONFIG_TEMPLATE = """\
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rep: <http://www.openrdf.org/config/repository#>.
@prefix sr: <http://www.openrdf.org/config/repository/sail#>.
@prefix sail: <http://www.openrdf.org/config/sail#>.
@prefix graphdb: <http://www.ontotext.com/config/graphdb#>.

[] a rep:Repository ;
    rep:repositoryID "{repository_id}" ;
    rdfs:label "AAMAS 2027 OWL2Bench experiment repository (ruleset {ruleset})" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
            graphdb:read-only "false" ;
            graphdb:ruleset "{ruleset}" ;
            graphdb:disable-sameAs "{disable_same_as}" ;
            graphdb:check-for-inconsistencies "{check_for_inconsistencies}" ;
            graphdb:entity-id-size "32" ;
            graphdb:enable-context-index "false" ;
            graphdb:enablePredicateList "true" ;
            graphdb:enable-fts-index "false" ;
            graphdb:query-timeout "0" ;
            graphdb:throw-QueryEvaluationException-on-timeout "false" ;
            graphdb:query-limit-results "0" ;
            graphdb:base-URL "http://example.org/owlim#" ;
            graphdb:repository-type "file-repository" ;
            graphdb:storage-folder "storage" ;
            graphdb:entity-index-size "10000000" ;
            graphdb:in-memory-literal-properties "true" ;
            graphdb:enable-literal-index "true" ;
        ]
    ].
"""
"""
Repository configuration. The settings other than the ruleset mirror the ``KRROOD`` repository used for the
January 2026 runs (``owl:sameAs`` enabled, consistency checks enabled).
"""


class UnmanagedRepositoryError(RuntimeError):
    """
    Raised when an operation would modify a repository that is not managed by the experiment scripts.
    """


class RulesetMismatchError(RuntimeError):
    """
    Raised when an existing managed repository uses a different ruleset than requested.
    """


@dataclass
class GraphDBClient:
    """
    Client for the GraphDB REST and RDF4J protocol endpoints.
    """

    base_url: str = DEFAULT_GRAPHDB_URL
    """
    Base URL of the GraphDB server, without a trailing slash.
    """
    timeout_seconds: float = 6 * 3600
    """
    Timeout for a single HTTP request.
    """

    def endpoint(self, repository_id: str) -> str:
        """
        :param repository_id: The repository identifier.
        :return: The SPARQL endpoint URL of the repository.
        """
        return f"{self.base_url}/repositories/{repository_id}"

    def version(self) -> Dict:
        """
        :return: The version information reported by the server.
        """
        return requests.get(f"{self.base_url}/rest/info/version", timeout=30).json()

    def license(self) -> Dict:
        """
        :return: The license information reported by the server (product type, CPU core limit, ...).
        """
        response = requests.get(f"{self.base_url}/rest/graphdb-settings/license", timeout=30)
        information = response.json()
        return {
            key: information.get(key)
            for key in ("productType", "product", "version", "maxCpuCores", "valid")
        }

    def repository_ids(self) -> list[str]:
        """
        :return: The identifiers of all repositories on the server.
        """
        response = requests.get(f"{self.base_url}/rest/repositories", timeout=30)
        response.raise_for_status()
        return [repository["id"] for repository in response.json()]

    def repository_configuration(self, repository_id: str) -> Dict[str, str]:
        """
        :param repository_id: The repository identifier.
        :return: A flat mapping from configuration parameter name to value.
        """
        response = requests.get(
            f"{self.base_url}/rest/repositories/{repository_id}", timeout=30
        )
        response.raise_for_status()
        parameters = response.json().get("params", {})
        return {name: value.get("value") for name, value in parameters.items()}

    def ruleset(self, repository_id: str) -> str:
        """
        :param repository_id: The repository identifier.
        :return: The ruleset configured for the repository.
        """
        return self.repository_configuration(repository_id)["ruleset"]

    @staticmethod
    def ensure_managed(repository_id: str) -> None:
        """
        :param repository_id: The repository identifier.
        :raises UnmanagedRepositoryError: If the repository is not managed by the experiment scripts.
        """
        if not repository_id.startswith(REPOSITORY_PREFIX):
            raise UnmanagedRepositoryError(
                f"Refusing to modify repository '{repository_id}': only repositories starting with "
                f"'{REPOSITORY_PREFIX}' are managed by the experiment scripts."
            )

    def create_repository(
        self,
        repository_id: str,
        ruleset: str,
        disable_same_as: bool = False,
        check_for_inconsistencies: bool = True,
    ) -> None:
        """
        Create a managed repository, or verify the ruleset of an existing one.

        :param repository_id: The repository identifier, must start with :data:`REPOSITORY_PREFIX`.
        :param ruleset: The GraphDB ruleset identifier, one of :data:`RULESETS`.
        :param disable_same_as: Whether to disable the ``owl:sameAs`` optimisation.
        :param check_for_inconsistencies: Whether to enable consistency checking.
        :raises RulesetMismatchError: If the repository exists with a different ruleset.
        """
        self.ensure_managed(repository_id)
        if ruleset not in RULESETS:
            raise ValueError(f"Unknown ruleset {ruleset}, expected one of {list(RULESETS)}")
        if repository_id in self.repository_ids():
            existing_ruleset = self.ruleset(repository_id)
            if existing_ruleset != ruleset:
                raise RulesetMismatchError(
                    f"Repository {repository_id} exists with ruleset {existing_ruleset}, requested {ruleset}. "
                    f"Delete it first (python scripts/aamas27/graphdb_setup.py --delete {repository_id})."
                )
            return
        configuration = REPOSITORY_CONFIG_TEMPLATE.format(
            repository_id=repository_id,
            ruleset=ruleset,
            disable_same_as=str(disable_same_as).lower(),
            check_for_inconsistencies=str(check_for_inconsistencies).lower(),
        )
        response = requests.post(
            f"{self.base_url}/rest/repositories",
            files={"config": ("config.ttl", configuration, "text/turtle")},
            timeout=120,
        )
        response.raise_for_status()

    def delete_repository(self, repository_id: str) -> None:
        """
        :param repository_id: The managed repository to delete.
        """
        self.ensure_managed(repository_id)
        requests.delete(
            f"{self.base_url}/rest/repositories/{repository_id}", timeout=600
        ).raise_for_status()

    def clear(self, repository_id: str) -> None:
        """
        Remove all statements from a managed repository.

        :param repository_id: The managed repository to clear.
        """
        self.ensure_managed(repository_id)
        requests.delete(
            f"{self.endpoint(repository_id)}/statements", timeout=self.timeout_seconds
        ).raise_for_status()

    def load_file(self, repository_id: str, file_path: Path) -> float:
        """
        Upload an RDF/XML file into a managed repository in a single transaction. The server performs the
        materialisation of the configured ruleset before the request returns.

        :param repository_id: The managed repository.
        :param file_path: The RDF/XML file to upload.
        :return: The wall-clock time of the upload request in seconds.
        """
        self.ensure_managed(repository_id)
        with open(file_path, "rb") as stream:
            start = time.perf_counter()
            response = requests.post(
                f"{self.endpoint(repository_id)}/statements",
                data=stream,
                headers={"Content-Type": "application/rdf+xml"},
                timeout=self.timeout_seconds,
            )
            elapsed = time.perf_counter() - start
        response.raise_for_status()
        return elapsed

    def select(self, repository_id: str, query: str) -> Dict:
        """
        :param repository_id: The repository to query.
        :param query: A SPARQL SELECT query.
        :return: The SPARQL JSON results.
        """
        response = requests.post(
            self.endpoint(repository_id),
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def count_statements(self, repository_id: str) -> Dict[str, int]:
        """
        :param repository_id: The repository.
        :return: The number of explicit statements and the total number of statements including inferred ones.
        """
        explicit = int(
            requests.get(f"{self.endpoint(repository_id)}/size", timeout=600).text
        )
        result = self.select(
            repository_id, "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        )
        total = int(result["results"]["bindings"][0]["count"]["value"])
        return {"explicit": explicit, "total": total}

    def server_process(self) -> Optional[psutil.Process]:
        """
        :return: The local process listening on the server port, if it can be found.
        """
        port = int(self.base_url.rsplit(":", 1)[-1].split("/")[0])
        for process in psutil.process_iter(["name", "cmdline"]):
            try:
                if "java" not in (process.info["name"] or ""):
                    continue
                for connection in process.net_connections(kind="tcp"):
                    if (
                        connection.status == psutil.CONN_LISTEN
                        and connection.laddr.port == port
                    ):
                        return process
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return None

    def server_java_options(self) -> list[str]:
        """
        :return: The JVM options of the local server process (heap size etc.), if it can be found.
        """
        process = self.server_process()
        if process is None:
            return []
        return [
            argument
            for argument in process.cmdline()
            if argument.startswith("-X") or argument.startswith("-Dgraphdb.")
        ]
