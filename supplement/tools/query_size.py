"""
The size of the benchmark's queries in EQL, SPARQL and SQLAlchemy, in lexical tokens, as the benchmark code writes
them (code/earlier/experiments). It measures how long a query is to write, not how easy it is to read or to get right.

* EQL and SQLAlchemy: the Python tokens of the statements that build the query (names, operators, brackets,
  literals), without comments. For EQL, the tokens of ``domain=None``, which this version of KRROOD needs and the
  current one does not, are counted separately. The wrapper that hands a query to the benchmark is not counted.
* SPARQL: the tokens of the query without its PREFIX declarations: variables, prefixed names, IRIs, literals,
  keywords and punctuation.

Usage: python query_size.py OWL2BENCH_PACKAGE_DIR OUTPUT_JSON
"""
from __future__ import annotations

import io
import json
import math
import re
import sys
import tokenize
from pathlib import Path
from typing import Dict, List

QUERIES = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22]
"""The 18 queries of the RL profile, as in the paper."""

LAYOUT = {tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER}


def python_tokens(code: str) -> List[str]:
    """
    :param code: Python statements.
    :return: Their tokens, without layout and comments.
    """
    return [token.string for token in tokenize.generate_tokens(io.StringIO(code).readline) if token.type not in LAYOUT]


def sparql_tokens(query: str) -> List[str]:
    """
    :param query: A SPARQL query without PREFIX declarations.
    :return: Its tokens.
    """
    return re.findall(r"\?\w+|\w+:\w+|<[^>]*>|\"[^\"]*\"|\w+|[{}.;,()]", query)


def eql_queries(source: str) -> Dict[int, str]:
    """
    :param source: owl2bench_eql_queries.py.
    :return: For every query, the statements that build it.
    """
    body = source.split("def get_eql_queries")[1].split("eql_queries = [")[0]
    queries, statements = {}, []
    for line in body.splitlines()[3:]:
        match = re.match(r"\s*q(\d+) = QueryWithSelectables", line)
        if match:
            queries[int(match.group(1))], statements = "\n".join(statements), []
        elif line.strip() and not line.strip().startswith("#"):
            statements.append(line.strip())
    return queries


def sqlalchemy_queries(source: str) -> Dict[int, str]:
    """
    :param source: sqlalchemy_queries.py of the generated model.
    :return: For every query, the statements that build it, including the aliases defined for it.
    """
    blocks = re.split(r"\nq(\d+) = SQLAlchemyQuery\([^\n]*\)\n", source.split("# Columns in the order")[1])
    queries = {}
    for i in range(0, len(blocks) - 1, 2):
        lines = [line for line in blocks[i].splitlines()
                 if not line.strip().startswith("#") and "CricketAlias" not in line]  # an alias no query uses
        queries[int(blocks[i + 1])] = "\n".join(lines).strip()
    return queries


def sparql_queries(source: str) -> Dict[int, str]:
    """
    :param source: sparql_queries.py.
    :return: For every query, its text after the PREFIX declarations.
    """
    return {int(m.group(1)): m.group(2).strip()
            for m in re.finditer(r"q(\d+) = SPARQLQuery\(.*?\"\"\"(.*?)\"\"\"", source, re.S)}


def geometric_mean(values: List[int]) -> float:
    return math.exp(sum(map(math.log, values)) / len(values))


def main() -> None:
    package, output = Path(sys.argv[1]), Path(sys.argv[2])
    eql = eql_queries((package / "ontomatic/owl2bench_eql_queries.py").read_text())
    sql = sqlalchemy_queries((package / "ontomatic/sqlalchemy_queries.py").read_text())
    sparql = sparql_queries((package / "sparql_queries.py").read_text())
    rows = []
    for number in QUERIES:
        eql_count = len(python_tokens(eql[number]))
        domain_count = eql_count - len(python_tokens(eql[number].replace(", domain=None", "").replace(", None)", ")")))
        rows.append({"query": number, "sparql": len(sparql_tokens(sparql[number])), "eql": eql_count,
                     "eql_domain_none": domain_count, "sqlalchemy": len(python_tokens(sql[number]))})
    summary = {name: {"total": sum(r[name] for r in rows), "geometric_mean": geometric_mean([r[name] for r in rows])}
               for name in ("sparql", "eql", "sqlalchemy")}
    without = [r["eql"] - r["eql_domain_none"] for r in rows]
    summary["eql_without_domain_none"] = {"total": sum(without), "geometric_mean": geometric_mean(without)}
    output.write_text(json.dumps({"unit": "lexical tokens", "queries": rows, "summary": summary}, indent=2))
    print(f"query sizes written to {output}")


if __name__ == "__main__":
    main()
