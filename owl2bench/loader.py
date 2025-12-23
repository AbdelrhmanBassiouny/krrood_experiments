from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

from .model.base import *


class OntologyLoadError(Exception):
    """
    Raised when an OWL/RDF file cannot be parsed.
    """


class MappingError(Exception):
    """
    Raised when required data is missing for constructing model objects.
    """


PREFIXES = (
    "\n".join(
        [
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>",
            "PREFIX owl2bench: <http://benchmark/OWL2Bench#>",
        ]
    )
    + "\n"
)


@dataclass
class WorldLoader:

    sparql_wrapper: SPARQLWrapper

    world: World = field(default_factory=World)

    def parse(self):
        # get all person data
        self.world.persons = self._get_persons()

        # get all relationships between persons
        self._update_inter_person_relationships()

        # get all Courses

        # get all Programs

        # get all Publications

        # get all Students

        # get all employees

        # get all research groups

        # get all departments

        # get all colleges

        # get all universities

    def _get_persons(self) -> List[Person]:
        """
        Retrieves all persons with their first name, last name, email, gender and hometown.

        :return: A list of Person objects.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?firstName ?lastName ?email ?isWoman ?hometown WHERE {
                ?x rdf:type owl2bench:Person .
                OPTIONAL { ?x owl2bench:hasFirstName ?firstName }
                OPTIONAL { ?x owl2bench:hasLastName ?lastName }
                OPTIONAL { ?x owl2bench:hasEmailAddress ?email }
                OPTIONAL { ?x rdf:type owl2bench:Woman . BIND(true AS ?isWoman) }
            }
            """
        )

        # Execute query
        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        persons = []
        for b in bindings:
            persons.append(
                Person(
                    identifier=str(b["x"]["value"]),
                    first_name=b.get("firstName", {}).get("value"),
                    last_name=b.get("lastName", {}).get("value"),
                    email=b.get("email", {}).get("value"),
                    is_woman=b.get("isWoman", {}).get("value") == "true",
                )
            )
        return persons
