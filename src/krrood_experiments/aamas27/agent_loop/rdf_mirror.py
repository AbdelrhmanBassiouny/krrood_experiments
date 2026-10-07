"""
What the RDF-based variants share: the RDF statements of a perceived fact, the vocabulary of the application data
written to a store by the push variant, and a GraphDB client that keeps its HTTP connection open (``requests.Session``)
and passes query parameters as SPARQL bindings, so that the query texts stay constant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import requests

from ..graphdb import GraphDBClient
from .events import OWL2BENCH, T20_CRICKET, CourseTaking, CricketEnthusiasm, Enrollment, KnowledgeEvent
from .measurement import MAPPING, SYNCHRONIZATION, boundary

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
"""
The ``rdf:type`` property.
"""

AGENT_LOOP = "https://example.org/agent-loop#"
"""
Namespace of the application data that the push variant writes into the store.
"""

PLACE_PREFIX = AGENT_LOOP + "place-"
"""
IRI prefix of the places of the campus map.
"""

Triple = Tuple[str, str, str]
"""
A statement of three IRIs.
"""


@boundary(SYNCHRONIZATION)
def event_triples(event: KnowledgeEvent) -> List[Triple]:
    """
    :param event: A perceived fact.
    :return: Its RDF statements.
    """
    if isinstance(event, Enrollment):
        return [
            (event.person, RDF_TYPE, OWL2BENCH + "Person"),
            (event.person, OWL2BENCH + "enrollIn", event.department),
        ]
    if isinstance(event, CourseTaking):
        return [(event.student, OWL2BENCH + "takesCourse", event.course)]
    if isinstance(event, CricketEnthusiasm):
        return [(event.person, OWL2BENCH + "isCrazyAbout", T20_CRICKET)]
    raise TypeError(f"Unknown event {event}")


@boundary(SYNCHRONIZATION)
def insert_data(triples: Iterable[Tuple[str, str, str]]) -> str:
    """
    :param triples: Statements whose objects are IRIs, or literals already written in N-Triples syntax (starting
     with a quote).
    :return: A SPARQL ``INSERT DATA`` update.
    """
    lines = [f"<{subject}> <{predicate}> {object_term(value)} ." for subject, predicate, value in triples]
    return "INSERT DATA {\n" + "\n".join(lines) + "\n}"


def delete_data(triples: Iterable[Tuple[str, str, str]]) -> str:
    """
    Used only to restore a repository after a run, not by the agent.

    :param triples: Statements as for :func:`insert_data`.
    :return: A SPARQL ``DELETE DATA`` update.
    """
    lines = [f"<{subject}> <{predicate}> {object_term(value)} ." for subject, predicate, value in triples]
    return "DELETE DATA {\n" + "\n".join(lines) + "\n}"


@boundary(SYNCHRONIZATION)
def object_term(value: str) -> str:
    """
    :param value: An IRI, or a literal in N-Triples syntax.
    :return: The value in N-Triples syntax.
    """
    return value if value.startswith('"') else f"<{value}>"


@boundary(MAPPING)
def place_iri(identifier: str) -> str:
    """
    :param identifier: A place identifier.
    :return: Its IRI.
    """
    return PLACE_PREFIX + identifier


@boundary(MAPPING)
def place_identifier(iri: str) -> str:
    """
    :param iri: The IRI of a place.
    :return: Its identifier.
    """
    return iri[len(PLACE_PREFIX) :]


@dataclass
class GraphDBSession(GraphDBClient):
    """
    A GraphDB client for many small requests: it keeps one HTTP connection open and counts its round trips.
    """

    session: requests.Session = field(default_factory=requests.Session, repr=False)
    """
    The HTTP session.
    """
    round_trips: int = 0
    """
    Number of requests sent.
    """

    def select_bindings(
        self, repository_id: str, query: str, bindings: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        :param repository_id: The repository.
        :param query: A SPARQL SELECT query.
        :param bindings: Variable name to IRI, bound before evaluation (RDF4J protocol ``$name`` parameters).
        :return: The solutions, as variable name to value.
        """
        data = {"query": query}
        for name, iri in (bindings or {}).items():
            data[f"${name}"] = f"<{iri}>"
        response = self.session.post(
            self.endpoint(repository_id),
            data=data,
            headers={"Accept": "application/sparql-results+json"},
            timeout=self.timeout_seconds,
        )
        self.round_trips += 1
        response.raise_for_status()
        return [
            {name: value["value"] for name, value in solution.items()}
            for solution in response.json()["results"]["bindings"]
        ]

    def update(self, repository_id: str, update: str) -> None:
        """
        Execute a SPARQL update in one transaction; GraphDB materialises its consequences before it returns.

        :param repository_id: A managed repository.
        :param update: The SPARQL update.
        """
        self.ensure_managed(repository_id)
        response = self.session.post(
            f"{self.endpoint(repository_id)}/statements",
            data={"update": update},
            timeout=self.timeout_seconds,
        )
        self.round_trips += 1
        response.raise_for_status()
