"""
Build the anonymized supplementary material of the AAMAS 2027 KRROOD submission.

The code is exported from pinned commits (no git metadata), identifying metadata is removed, the Docker set-up
and the README are added, every file is scanned for identifying strings, and the result is zipped. The build
fails if the scan finds anything or if the zip exceeds 25 MB.

Usage: python make_supplement.py OUTPUT_DIRECTORY [--results RESULTS_DIRECTORY] [--code-from BUNDLE_ZIP_OR_DIR]

--code-from takes code/ from an earlier bundle instead of exporting it from the clones below (on a machine without
them); the build then checks that the code is unchanged (same BUNDLE id), as only the files around it change.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The clones of the pinned commits on the authors' machine. Every commit below is on the authors' forks:
# CRAM branch aamas27-experiments (earlier version) and fix/eql-to-sql-collections (current version),
# krrood_experiments branch aamas27-experiments, ripple_down_rules 3b994bb.
SCRATCH = Path("/tmp/claude-1000/-home-bass-Projects-krrood-aamas/33ba4645-d3a6-450c-b474-694a7d4a326f/scratchpad")
NAME = "krrood-aamas27-supplement"

# (repository, commit, paths, destination inside the bundle, prefix to strip)
SOURCES = [
    (SCRATCH / "exp/cram", "ec7c922b9ff66ae49f380f044e6e50db883264f1",
     ["krrood/pyproject.toml", "krrood/requirements.txt", "krrood/src"], "code/earlier", ""),
    (Path("/tmp/claude-1000/-home-bass-Projects-krrood-aamas/6a40da36-2e3b-49ed-8542-7c82a0754f58/scratchpad/pcsim/rdr"),
     "3b994bb4bd8f5c7852f747df6732f8f8adf081ad",
     ["pyproject.toml", "requirements.txt", "src", "LICENSE"], "code/earlier/ripple_down_rules", ""),
    (SCRATCH / "exp/exp", "HEAD",
     ["pyproject.toml", "requirements.txt", "src", "scripts/aamas27", "tests/aamas27",
      "resources/owl2bench_statements_unreasoned.rdf"], "code/earlier/experiments", ""),
    (Path("/home/bass/Projects/cram-eql-sql-fix"), "3308cb252f",
     ["krrood/pyproject.toml", "krrood/src", "krrood/LICENSE"], "code/current", ""),
]
# Files of the experiment repository that only serve the authors' own machines.
EXCLUDE = {
    "code/earlier/experiments/scripts/aamas27/run_all.sh",
}
LISTINGS = HERE / "listings"   # executable versions of the paper's listings, run on the current version

IDENTIFYING = re.compile(
    r"bassiouny|bassioun|abdelrhman|ms-7d32|schierenbeck|tomsch|sorinar|sorin|\barion\b|beetz|bremen|aicor|vasantak|hoanggia"
    r"|\bnaren\b|\bgiang\b|cram2|github\.com|gitlab\.com|/home/|/tmp/claude|@[a-z0-9.-]+\.(de|com|org|net)\b"
    r"|\bbass\b|tom_sch|ec7c922b9f|eeeb2e48db|3308cb252f|3b994bb|b0b59087a6|ccf8367709",
    re.IGNORECASE,
)
# Matches that are not identifying: generated person names of the OWL2Bench data (e.g. "Jamarion").
ALLOWED = re.compile(r"[a-z]arion\b", re.IGNORECASE)
# Synthetic e-mail addresses of the OWL2Bench data and the OWL API link in the header of the data file.
BENIGN = re.compile(r"@bench\.com|github\.com/owlcs/owlapi|>Bremen</hasFirstName>|>Bremen And</hasName>")


def export(repository: Path, commit: str, paths, destination: Path) -> None:
    archive = subprocess.run(["git", "-C", str(repository), "archive", "--format=tar", commit, *paths],
                             check=True, capture_output=True).stdout
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination, filter="data")


def strip_pyproject(path: Path) -> None:
    """Remove the authors, maintainers and URLs of a pyproject.toml."""
    text = path.read_text()
    text = re.sub(r"^(authors|maintainers)\s*=\s*\[.*?^\]\s*$\n?", "", text, flags=re.M | re.S)
    text = re.sub(r"^(authors|maintainers)\s*=\s*\[[^\n]*\]\s*$\n?", "", text, flags=re.M)
    text = re.sub(r"^\[project\.urls\]\s*\n(?:^(?!\[).*\n?)*", "", text, flags=re.M)
    path.write_text(text)


def sanitize(bundle: Path) -> None:
    for pyproject in bundle.rglob("pyproject.toml"):
        strip_pyproject(pyproject)
    for lock in [*bundle.rglob("requirements-aamas27-lock.txt"), *bundle.rglob("requirements-aamas27.txt")]:
        lock.write_text("".join(line for line in lock.read_text().splitlines(keepends=True)
                                if not line.startswith("#")))
    for path in bundle.rglob("*.py"):
        text = path.read_text()
        new = re.sub(r"https://github\.com/tomsch420/random-events/\S*", "the random-events library (MIT license)",
                     text)
        new = new.replace("cram2 main's test conftest", "the test set-up of KRROOD")
        new = new.replace("cram2 ``main`` syntax", "the syntax of the current version of KRROOD")
        new = new.replace("(cram2 main, krrood.ormatic.eql_interface.eql_to_sql)",
                          "(current version, krrood.ormatic.eql_interface.eql_to_sql)")
        new = re.sub(r"\(branch fix/eql-to-sql-collections of the CRAM fork, which merges\s+"
                     r"fix/eql-correlated-quantifiers\)", "(see README.md)", new)
        if new != text:
            path.write_text(new)


def scan(bundle: Path) -> list:
    hits = []
    for path in sorted(bundle.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        if path.suffix.lower() == ".pdf":  # PDF text is compressed; scan the extracted text and the metadata
            text += subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True).stdout
            text += subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
        for match in IDENTIFYING.finditer(text):
            context = text[max(0, match.start() - 3):match.end() + 3]
            if ALLOWED.search(context) and match.group(0).lower() == "arion":
                continue
            if match.group(0).lower() in ("@bench.com", "github.com", "bremen") and BENIGN.search(
                    text[max(0, match.start() - 20):match.end() + 20]):
                continue
            line = text.count("\n", 0, match.start()) + 1
            hits.append(f"{path.relative_to(bundle)}:{line}: {text[max(0, match.start() - 40):match.end() + 40]!r}")
    return hits


HOME_PATH = re.compile(r"/home/[^/\s\"']+")
TEXT_SUFFIXES = {".txt", ".log", ".json", ".sh", ".py", ".conf", ".csv", ".md", ".tex"}


def copy_results(source: Path, destination: Path) -> None:
    """
    Copy the measured results. Of the answer sets, only GraphDB's (the reference of the answer-set check) are kept:
    the other systems' sets are equal to them (check/answer_check.json), and all of them would exceed 25 MB.
    Home folders in paths of logs (e.g. of the Protégé sessions) are replaced by "~".
    """
    def ignore(directory: str, names) -> set:
        directory = Path(directory)
        if directory.name == "answers":
            return {name for name in names if not (directory.parent.name == "check" and name == "graphdb")}
        return {name for name in names if name in ("__pycache__",) or name.startswith(".done-")}
    shutil.copytree(source, destination, ignore=ignore)
    for path in destination.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(errors="surrogateescape")
            new = HOME_PATH.sub("~", text)
            new = re.sub(r"(semanticweb\.org/)[^/]+(/ontologies)", r"\1user\2", new)
            if path.name == "host.json":   # the board's model is rare enough to identify the machine
                record = json.loads(new)
                record.pop("board", None)
                new = json.dumps(record, indent=2) + "\n"
            if new != text:
                path.write_text(new, errors="surrogateescape")


def code_from(source: Path, bundle: Path) -> None:
    """Copy code/ of an earlier bundle (a zip or an unpacked folder)."""
    if source.suffix == ".zip":
        with zipfile.ZipFile(source) as zipped:
            for name in zipped.namelist():
                parts = Path(name).parts
                if len(parts) > 2 and parts[1] == "code" and not name.endswith("/"):
                    target = bundle / Path(*parts[1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zipped.read(name))
    else:
        shutil.copytree(source / "code", bundle / "code")


def fingerprint(bundle: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in (bundle / "code").rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(bundle)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--results", help="results directory of the measured run, copied to results/")
    parser.add_argument("--code-from", help="take code/ from this earlier bundle (zip or folder)")
    parser.add_argument("--draft", action="store_true",
                        help="allow TODO-AUTHORS markers (for the measured run; not for submission)")
    arguments = parser.parse_args()
    if not arguments.draft and not arguments.results:
        sys.exit("the submission bundle needs the measured results: pass --results (or --draft for a test bundle)")
    output = Path(arguments.output).resolve()
    bundle = output / NAME
    if bundle.exists():
        shutil.rmtree(bundle)
    if arguments.code_from:
        code_from(Path(arguments.code_from).resolve(), bundle)
    else:
        for repository, commit, paths, destination, _ in SOURCES:
            export(repository, commit, paths, bundle / destination)
        # git archive keeps the "krrood/" prefix; the experiments and ripple_down_rules exports have none.
        for excluded in EXCLUDE:
            (bundle / excluded).unlink(missing_ok=True)
    shutil.copytree(LISTINGS, bundle / "listings",
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "probe_*.py"))
    for name in ("Dockerfile", "compose.yaml", "reproduce.sh", "run_ubuntu.sh", "README.md", "AI_USE.md", ".dockerignore"):
        shutil.copy(HERE / name, bundle / name)
    shutil.copytree(HERE / "environment", bundle / "environment")
    shutil.copytree(HERE / "tools", bundle / "tools", ignore=shutil.ignore_patterns("__pycache__", "*.rdf"))
    # The formalization of EQL: LaTeX source and the PDF compiled from it.
    (bundle / "formalization").mkdir()
    for name in ("eql_formalization.tex", "eql_formalization.pdf"):
        shutil.copy(HERE / "formalization" / name, bundle / "formalization" / name)
    if arguments.results:
        copy_results(Path(arguments.results), bundle / "results")
        subprocess.run([sys.executable, str(HERE / "tools" / "query_size.py"),
                        str(bundle / "code/earlier/experiments/src/krrood_experiments/owl2bench"),
                        str(bundle / "results" / "query_size.json")], check=True, capture_output=True)
        # The report of the paper's run, as a run of the bundle writes it for its own results.
        subprocess.run([sys.executable, str(HERE / "tools" / "report.py"), str(bundle / "results"),
                        str(bundle / "results"), "paper", str(bundle / "results" / "REPORT.md")],
                       check=True, capture_output=True)
    sanitize(bundle)
    (bundle / "environment" / "BUNDLE").write_text(fingerprint(bundle) + "\n")
    if arguments.code_from:
        source = Path(arguments.code_from)
        earlier = (zipfile.ZipFile(source).read(f"{NAME}/environment/BUNDLE").decode() if source.suffix == ".zip"
                   else (source / "environment" / "BUNDLE").read_text()).strip()
        if fingerprint(bundle) != earlier:
            sys.exit(f"the code differs from that of {source} ({fingerprint(bundle)} instead of {earlier})")
    hits = scan(bundle)
    # A GraphDB license names its licensee; it must never be shipped.
    hits += [f"{p.relative_to(bundle)}: license file" for p in bundle.rglob("*")
             if p.is_file() and (p.suffix.lower() == ".license" or "graphdb-home" in p.parts)]
    if not arguments.draft:
        hits += [f"{p.relative_to(bundle)}: unresolved TODO-AUTHORS" for p in bundle.rglob("*.md")
                 if "TODO-AUTHORS" in p.read_text()]
    if hits:
        print("identifying strings found:", *hits, sep="\n  ")
        sys.exit(1)
    archive = output / f"{NAME}.zip"
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in sorted(bundle.rglob("*")):
            info = zipfile.ZipInfo.from_file(path, path.relative_to(output))
            info.date_time = (2026, 10, 8, 0, 0, 0)
            if path.is_dir():
                continue
            with open(path, "rb") as source:
                zipped.writestr(info, source.read(), zipfile.ZIP_DEFLATED)
    size = archive.stat().st_size
    print(f"{archive} {size / 2**20:.1f} MB, bundle {fingerprint(bundle)}")
    if size > 25 * 10**6:
        sys.exit("the zip exceeds 25 MB")


if __name__ == "__main__":
    main()
