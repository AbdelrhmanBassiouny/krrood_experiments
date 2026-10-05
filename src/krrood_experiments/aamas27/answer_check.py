"""
Hard answer-set equality check of the query experiment: every framework's answer set of every query is compared with
the answer set of the reference framework (GraphDB on the OWL 2 RL closure of the raw data).
"""

from __future__ import annotations

import gzip
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

DIFFERENCE_EXAMPLES = 20
"""
Number of example answers stored per side of a symmetric difference.
"""


def read_lines(path: Path) -> Iterator[str]:
    """
    :param path: A sorted answer file.
    :return: Its lines without the trailing newline.
    """
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield line.rstrip("\n")


def compare_sorted(reference: Path, candidate: Path) -> Dict[str, Any]:
    """
    Compare two sorted, de-duplicated answer files by merging them.

    :param reference: The answer file of the reference framework.
    :param candidate: The answer file of the compared framework.
    :return: Set sizes, sizes of the two differences and example elements of both differences.
    """
    only_reference: List[str] = []
    only_candidate: List[str] = []
    counts = {"reference": 0, "candidate": 0, "only_in_reference": 0, "only_in_candidate": 0}
    reference_lines, candidate_lines = read_lines(reference), read_lines(candidate)
    left: Optional[str] = next(reference_lines, None)
    right: Optional[str] = next(candidate_lines, None)
    while left is not None or right is not None:
        if right is None or (left is not None and left < right):
            counts["reference"] += 1
            counts["only_in_reference"] += 1
            if len(only_reference) < DIFFERENCE_EXAMPLES:
                only_reference.append(left)
            left = next(reference_lines, None)
        elif left is None or right < left:
            counts["candidate"] += 1
            counts["only_in_candidate"] += 1
            if len(only_candidate) < DIFFERENCE_EXAMPLES:
                only_candidate.append(right)
            right = next(candidate_lines, None)
        else:
            counts["reference"] += 1
            counts["candidate"] += 1
            left, right = next(reference_lines, None), next(candidate_lines, None)
    counts["equal"] = counts["only_in_reference"] == 0 and counts["only_in_candidate"] == 0
    counts["only_in_reference_examples"] = [line.split("\t") for line in only_reference]
    counts["only_in_candidate_examples"] = [line.split("\t") for line in only_candidate]
    return counts


def check_answers(
    answers_directory: Path,
    queries: List[int],
    frameworks: List[str],
    reference: str = "graphdb",
) -> Dict[str, Any]:
    """
    :param answers_directory: Directory with one sub-directory of answer files per framework.
    :param queries: Query numbers.
    :param frameworks: Frameworks to compare with the reference.
    :param reference: The reference framework.
    :return: The report, with ``all_equal`` and a per-query, per-framework comparison.
    """
    report: Dict[str, Any] = {"reference": reference, "queries": {}, "mismatches": []}
    for number in queries:
        reference_file = answers_directory / reference / f"q{number}.tsv.gz"
        entry: Dict[str, Any] = {}
        for framework in frameworks:
            if framework == reference:
                continue
            candidate_file = answers_directory / framework / f"q{number}.tsv.gz"
            if not reference_file.exists() or not candidate_file.exists():
                entry[framework] = {"equal": False, "missing_answer_file": True}
            else:
                entry[framework] = compare_sorted(reference_file, candidate_file)
            if not entry[framework]["equal"]:
                report["mismatches"].append({"query": number, "framework": framework})
        report["queries"][str(number)] = entry
    report["all_equal"] = not report["mismatches"]
    return report
