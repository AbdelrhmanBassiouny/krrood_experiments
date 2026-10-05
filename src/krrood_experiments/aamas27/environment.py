"""
Paths, result directories and the ``environment.json`` record for the AAMAS 2027 OWL2Bench experiments.
"""

from __future__ import annotations

import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import psutil

EXPERIMENTS_ROOT = Path(__file__).resolve().parents[3]
"""
Root of the krrood_experiments repository.
"""

RESOURCES = EXPERIMENTS_ROOT / "resources"
"""
Directory containing the OWL2Bench data files.
"""

UNREASONED_FILE = RESOURCES / "owl2bench_statements_unreasoned.rdf"
"""
OWL2Bench RL (1 university) TBox and ABox without materialised inferences.
"""

REASONED_FILE = RESOURCES / "owl2bench_statements_reasoned.rdf"
"""
The same data with materialised inferences.
"""

INPUT_FILES = {"raw": UNREASONED_FILE, "reasoned": REASONED_FILE}
"""
The two inputs of the loading experiment.
"""

RESULTS_ROOT = EXPERIMENTS_ROOT / "results" / "aamas27"
"""
Directory under which every run creates its own sub-directory.
"""

PACKAGES = [
    "krrood",
    "krrood_experiments",
    "ripple_down_rules",
    "rdflib",
    "owlrl",
    "owlready2",
    "SQLAlchemy",
    "SPARQLWrapper",
    "psycopg2-binary",
    "rustworkx",
    "numpy",
    "psutil",
]
"""
Packages whose versions are recorded.
"""


def new_results_directory(label: Optional[str] = None) -> Path:
    """
    Create ``results/aamas27/<hostname>-<timestamp>[-label]``.

    :param label: Optional suffix.
    :return: The created directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{socket.gethostname()}-{timestamp}" + (f"-{label}" if label else "")
    directory = RESULTS_ROOT / name
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def resolve_results_directory(directory: Optional[str], label: str) -> Path:
    """
    :param directory: An existing results directory to reuse, or None to create a new one.
    :param label: Suffix for a new directory.
    :return: The results directory, with an ``environment.json`` written into it if missing.
    """
    path = Path(directory) if directory else new_results_directory(label)
    path.mkdir(parents=True, exist_ok=True)
    if not (path / "environment.json").exists():
        write_environment(path)
    return path


def git_state(repository: Path) -> Dict[str, Any]:
    """
    :param repository: A path inside a git working tree.
    :return: The commit, branch and dirty flag of the working tree.
    """

    def git(*arguments: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repository), *arguments],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

    status = git("status", "--porcelain", "--untracked-files=no")
    return {
        "path": str(repository),
        "commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(status),
        "dirty_files": status.splitlines()[:50],
    }


def krrood_repository() -> Path:
    """
    :return: The source directory of the installed krrood package.
    """
    import krrood

    return Path(krrood.__file__).resolve().parent


def cpu_model() -> str:
    """
    :return: The CPU model name.
    """
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def operating_system() -> str:
    """
    :return: The pretty name of the Linux distribution, or the platform string.
    """
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip('"')
    except OSError:
        pass
    return platform.platform()


def package_versions() -> Dict[str, Optional[str]]:
    """
    :return: Installed versions of the relevant packages.
    """
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def sha256(path: Path) -> Optional[str]:
    """
    :param path: A file.
    :return: The SHA-256 hex digest, or None if the file does not exist.
    """
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            digest.update(block)
    return digest.hexdigest()


def graphdb_information() -> Dict[str, Any]:
    """
    :return: Version, license and repository rulesets of the GraphDB server, or the error if it is unreachable.
    """
    from .graphdb import GraphDBClient

    client = GraphDBClient()
    try:
        repositories = {}
        for repository_id in client.repository_ids():
            try:
                repositories[repository_id] = client.repository_configuration(
                    repository_id
                )
            except Exception as error:  # the information is best effort
                repositories[repository_id] = {"error": str(error)}
        return {
            "url": client.base_url,
            "version": client.version(),
            "license": client.license(),
            "java_options": client.server_java_options(),
            "repositories": {
                repository_id: {
                    key: configuration.get(key)
                    for key in (
                        "ruleset",
                        "disableSameAs",
                        "checkForInconsistencies",
                    )
                }
                for repository_id, configuration in repositories.items()
            },
        }
    except Exception as error:
        return {"url": client.base_url, "error": str(error)}


def postgresql_information() -> Dict[str, Any]:
    """
    :return: The PostgreSQL server version, or the error if the database is unreachable.
    """
    uri = os.environ.get("KRROOD_EXPERIMENTS_DATABASE_URI")
    if not uri:
        return {"error": "KRROOD_EXPERIMENTS_DATABASE_URI is not set"}
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(uri)
        with engine.connect() as connection:
            version = connection.execute(text("SELECT version()")).scalar()
        engine.dispose()
        return {"uri_without_password": _strip_password(uri), "version": version}
    except Exception as error:
        return {"uri_without_password": _strip_password(uri), "error": str(error)}


def _strip_password(uri: str) -> str:
    if "@" not in uri or "://" not in uri:
        return uri
    scheme, rest = uri.split("://", 1)
    credentials, host = rest.split("@", 1)
    user = credentials.split(":", 1)[0]
    return f"{scheme}://{user}:***@{host}"


def java_version() -> str:
    """
    :return: The version of the ``java`` executable on the PATH (used by owlready2 for Pellet).
    """
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=False
        )
        return (result.stderr or result.stdout).strip().splitlines()[0]
    except OSError as error:
        return f"unavailable: {error}"


def environment_record() -> Dict[str, Any]:
    """
    :return: The full environment record.
    """
    memory = psutil.virtual_memory()
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "cpu_model": cpu_model(),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "ram_total_gib": round(memory.total / 2**30, 2),
        "ram_available_gib_at_start": round(memory.available / 2**30, 2),
        "swap_total_gib": round(psutil.swap_memory().total / 2**30, 2),
        "os": operating_system(),
        "kernel": platform.release(),
        "python": sys.version,
        "python_executable": sys.executable,
        "packages": package_versions(),
        "java": java_version(),
        "git": {
            "krrood_experiments": git_state(EXPERIMENTS_ROOT),
            "krrood": git_state(krrood_repository()),
        },
        "data_files": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in INPUT_FILES.items()
        },
        "graphdb": graphdb_information(),
        "postgresql": postgresql_information(),
    }


def write_environment(directory: Path) -> Path:
    """
    Write ``environment.json`` into a results directory.

    :param directory: The results directory.
    :return: The written file.
    """
    path = directory / "environment.json"
    path.write_text(json.dumps(environment_record(), indent=2, default=str))
    return path


def write_json(path: Path, data: Any) -> None:
    """
    Write JSON atomically (write to a temporary file, then rename).

    :param path: The target file.
    :param data: JSON-serialisable data.
    """
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, default=str))
    temporary.replace(path)
