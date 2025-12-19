from dataclasses import dataclass

from .base import Publication


@dataclass
class Article(Publication): ...


@dataclass
class ConferencePaper(Article): ...


@dataclass
class JournalArticle(Article): ...


@dataclass
class TechnicalReport(Article): ...


@dataclass
class Book(Publication): ...


@dataclass
class Manual(Publication): ...


@dataclass
class Software(Publication): ...


@dataclass
class Specification(Publication): ...


@dataclass
class UnofficialPublication(Publication): ...
