"""
Measurement helpers of the agent-loop experiment: per-step phase timers, the marker of code that exists only to
synchronise a second representation or to map between representations, and the counts of that code and of the query
texts.

Phases of a step (wall time in seconds):

* ``mapping``: translating between the application's objects and another representation (IRIs to objects, objects to
  IRIs, query results to application records).
* ``update``: writing the perceived facts into the knowledge, including the inference that happens on insertion
  (descriptor forward chaining in KRROOD, GraphDB's incremental materialisation inside the update request).
* ``reasoning``: a separate materialisation call (the ``reasonable`` and ``nemo`` variants).
* ``push``: writing procedure results into the store (only the GraphDB push variant).
* ``query``: evaluating the queries, without the time spent inside the robot's procedures.
* ``procedures``: time inside :func:`~krrood_experiments.aamas27.agent_loop.robot.can_reach` and
  :func:`~krrood_experiments.aamas27.agent_loop.robot.travel_seconds`, wherever they are called from (inside an EQL
  query, on the candidates of a SPARQL query, or before a push).
* ``decide`` and ``act``: the shared policy and the robot's motion.
"""

from __future__ import annotations

import ast
import inspect
import io
import math
import re
import statistics
import textwrap
import time
import tokenize
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Sequence, Type, TypeVar

from .robot import ProcedureMeter

PHASES = ("mapping", "update", "reasoning", "push", "query", "procedures", "decide", "act")
"""
The phases of a step, in report order.
"""

BOUNDARY_ATTRIBUTE = "__agent_loop_boundary__"
"""
Attribute set by :func:`boundary` on the functions it marks.
"""

SYNCHRONIZATION = "synchronization"
"""
Boundary category of code that writes the application's facts into a second representation.
"""

MAPPING = "mapping"
"""
Boundary category of code that translates between the application's objects and another representation.
"""

PROCEDURE_INTEGRATION = "procedure_integration"
"""
Boundary category of code that makes the robot's procedures usable in a decision: a predicate class or symbolic
function wrapping a procedure, or the Python filter applied to the candidates of a query that cannot call it.
"""

CATEGORIES = (SYNCHRONIZATION, MAPPING, PROCEDURE_INTEGRATION)
"""
All boundary categories.
"""

FunctionType = TypeVar("FunctionType", bound=Callable)


def boundary(category: str) -> Callable[[FunctionType], FunctionType]:
    """
    Mark a function as code that exists only because the knowledge lives in a second representation. The lines of the
    marked functions are counted by :func:`boundary_lines`.

    :param category: One of :data:`CATEGORIES`.
    :return: The decorator.
    """

    def mark(function: FunctionType) -> FunctionType:
        setattr(function, BOUNDARY_ATTRIBUTE, category)
        return function

    return mark


@dataclass
class StepMeter:
    """
    Times the phases of one step and counts its synchronisation work.
    """

    procedure_meter: ProcedureMeter
    """
    The robot's procedure meter; time spent in procedures is moved from the enclosing phase to ``procedures``.
    """
    seconds: Dict[str, float] = field(default_factory=lambda: {phase: 0.0 for phase in PHASES})
    """
    Wall time per phase.
    """
    statements_inserted: int = 0
    """
    Statements (or descriptor assignments) written.
    """
    statements_deleted: int = 0
    """
    Statements deleted (only the push variant deletes the previous procedure results).
    """
    round_trips: int = 0
    """
    Requests to a server.
    """
    reasoner_calls: int = 0
    """
    Calls into an in-process reasoner.
    """

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        """
        Time a phase; time spent inside the robot's procedures is booked to ``procedures`` instead.

        :param name: One of :data:`PHASES`.
        """
        procedure_seconds_before = self.procedure_meter.seconds
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            inside_procedures = self.procedure_meter.seconds - procedure_seconds_before
            self.seconds[name] += elapsed - inside_procedures
            self.seconds["procedures"] += inside_procedures

    @property
    def total_seconds(self) -> float:
        """
        :return: The wall time of the step.
        """
        return sum(self.seconds.values())

    def to_json(self) -> Dict[str, Any]:
        """
        :return: A JSON-serialisable representation.
        """
        return {
            "seconds": dict(self.seconds),
            "total_seconds": self.total_seconds,
            "statements_inserted": self.statements_inserted,
            "statements_deleted": self.statements_deleted,
            "round_trips": self.round_trips,
            "reasoner_calls": self.reasoner_calls,
        }


def distribution(values: Sequence[float]) -> Dict[str, float]:
    """
    :param values: Measurements.
    :return: Their total, mean, median, 95th percentile (nearest rank), minimum and maximum.
    """
    if not values:
        return {"count": 0}
    ordered = sorted(values)
    rank = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "count": len(ordered),
        "total": sum(ordered),
        "mean": statistics.fmean(ordered),
        "median": statistics.median(ordered),
        "p95": ordered[rank],
        "min": ordered[0],
        "max": ordered[-1],
    }


def code_lines(source: str) -> int:
    """
    :param source: The source of a function or class.
    :return: The number of lines that hold code: no blank lines, comments, docstrings (of the function and of
     attributes) or decorators.
    """
    source = textwrap.dedent(source)
    tree = ast.parse(source)
    definition = tree.body[0]
    excluded = set()
    for node in ast.walk(definition):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            excluded.update(range(node.lineno, node.end_lineno + 1))
    for decorator in getattr(definition, "decorator_list", []):
        excluded.update(range(decorator.lineno, decorator.end_lineno + 1))
    lines = source.splitlines()
    return sum(
        1
        for number, line in enumerate(lines, start=1)
        if number not in excluded and line.strip() and not line.strip().startswith("#")
    )


def function_body_source(function: Callable, drop_last: bool = False) -> str:
    """
    :param function: A function.
    :param drop_last: Leave out the last statement (a ``return`` that only hands the query to its caller).
    :return: The source of the statements of its body, without the docstring.
    """
    source = textwrap.dedent(inspect.getsource(function))
    definition = ast.parse(source).body[0]
    statements = list(definition.body)
    if (
        statements
        and isinstance(statements[0], ast.Expr)
        and isinstance(statements[0].value, ast.Constant)
        and isinstance(statements[0].value.value, str)
    ):
        statements = statements[1:]
    if drop_last:
        statements = statements[:-1]
    lines = source.splitlines()
    return textwrap.dedent("\n".join(lines[statements[0].lineno - 1 : statements[-1].end_lineno]))


def boundary_functions(variant_class: Type) -> Dict[str, Callable]:
    """
    :param variant_class: A variant class.
    :return: The functions marked with :func:`boundary` that the class uses (methods of the class and its bases, the
     most derived definition of each name, and the module-level functions listed in its ``boundary_helpers``).
    """
    found: Dict[str, Callable] = {}
    for name in dir(variant_class):
        attribute = inspect.getattr_static(variant_class, name)
        function = getattr(attribute, "__func__", attribute)
        if callable(function) and hasattr(function, BOUNDARY_ATTRIBUTE):
            found[f"{_defining_class(variant_class, name)}.{name}"] = function
    for helper in getattr(variant_class, "boundary_helpers", ()):
        found[f"{helper.__module__.rsplit('.', 1)[-1]}.{helper.__name__}"] = helper
    return found


def _defining_class(variant_class: Type, name: str) -> str:
    """
    :param variant_class: A class.
    :param name: An attribute name.
    :return: The name of the class in the method resolution order that defines the attribute.
    """
    for klass in variant_class.__mro__:
        if name in vars(klass):
            return klass.__name__
    return variant_class.__name__


def boundary_lines(variant_class: Type) -> Dict[str, Any]:
    """
    Count the lines of synchronisation and mapping code of a variant with :func:`code_lines`.

    :param variant_class: A variant class.
    :return: The lines per category, per function, and in total.
    """
    per_function = {}
    per_category = {category: 0 for category in CATEGORIES}
    for name, function in sorted(boundary_functions(variant_class).items()):
        lines = code_lines(inspect.getsource(function))
        category = getattr(function, BOUNDARY_ATTRIBUTE)
        per_function[name] = {"category": category, "lines": lines}
        per_category[category] += lines
    return {"total": sum(per_category.values()), "per_category": per_category, "per_function": per_function}


LAYOUT_TOKENS = {
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.COMMENT,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENDMARKER,
}


def python_tokens(code: str) -> List[str]:
    """
    The tokenisation of ``supplement/tools/query_size.py``.

    :param code: Python statements.
    :return: Their tokens, without layout and comments.
    """
    return [
        token.string
        for token in tokenize.generate_tokens(io.StringIO(textwrap.dedent(code)).readline)
        if token.type not in LAYOUT_TOKENS
    ]


def sparql_tokens(query: str) -> List[str]:
    """
    The tokenisation of ``supplement/tools/query_size.py``, applied to the query without PREFIX declarations.

    :param query: A SPARQL query or update.
    :return: Its tokens.
    """
    body = "\n".join(line for line in query.splitlines() if not line.strip().upper().startswith("PREFIX"))
    return re.findall(r"\?\w+|\w+:\w+|<[^>]*>|\"[^\"]*\"|\w+|[{}.;,()]", body)


def query_size(text: str, language: str) -> Dict[str, Any]:
    """
    :param text: A query text.
    :param language: ``eql`` or ``python`` (Python tokens), ``sparql`` or ``nemo`` (Nemo rules, tokenised as SPARQL).
    :return: The text and its size in tokens, lines and characters.
    """
    tokens = sparql_tokens(text) if language in ("sparql", "nemo") else python_tokens(text)
    lines = [line for line in textwrap.dedent(text).splitlines() if line.strip()]
    return {
        "language": language,
        "text": textwrap.dedent(text).strip(),
        "tokens": len(tokens),
        "lines": len(lines),
        "characters": sum(len(line.strip()) for line in lines),
    }
