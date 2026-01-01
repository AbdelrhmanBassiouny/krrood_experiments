from __future__ import annotations
from dataclasses import dataclass

from .base import Publication


@dataclass(eq=False)
class Article(Publication): ...


@dataclass(eq=False)
class ConferencePaper(Article): ...


@dataclass(eq=False)
class JournalArticle(Article): ...


@dataclass(eq=False)
class TechnicalReport(Article): ...


@dataclass(eq=False)
class Book(Publication): ...


@dataclass(eq=False)
class Manual(Publication): ...


@dataclass(eq=False)
class Software(Publication): ...


@dataclass(eq=False)
class Specification(Publication): ...


@dataclass(eq=False)
class UnofficialPublication(Publication): ...
