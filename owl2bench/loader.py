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
        self._update_person_knows_relationships()

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
        Retrieves all persons with their attributes.

        :return: A list of Person objects.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?firstName ?lastName ?telephone ?age ?email ?title WHERE {
                ?x rdf:type owl2bench:Person .
                OPTIONAL { ?x owl2bench:hasFirstName ?firstName }
                OPTIONAL { ?x owl2bench:hasLastName ?lastName }
                OPTIONAL { ?x owl2bench:hasTelephone ?telephone }
                OPTIONAL { ?x owl2bench:hasAge ?age }
                OPTIONAL { ?x owl2bench:hasEmailAddress ?email }
                OPTIONAL { ?x owl2bench:hasTitle ?title }
            }
            """
        )

        # Execute query
        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        persons = []
        for b in bindings:
            age_value = b.get("age", {}).get("value", "0")
            try:
                age = int(age_value)
            except ValueError:
                age = 0
            persons.append(
                Person(
                    identifier=str(b["x"]["value"]),
                    first_name=b.get("firstName", {}).get("value", ""),
                    last_name=b.get("lastName", {}).get("value", ""),
                    telephone_number=b.get("telephone", {}).get("value", ""),
                    age=age,
                    e_mail_address=b.get("email", {}).get("value", ""),
                    title=b.get("title", {}).get("value"),
                )
            )
        return persons

    def _update_person_knows_relationships(self):
        """
        Updates the knows relationship between persons.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?y WHERE {
                ?x owl2bench:knows ?y .
            }
            """
        )

        # Execute query
        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        person_map = {p.identifier: p for p in self.world.persons}

        for b in bindings:
            subj_id = str(b["x"]["value"])
            obj_id = str(b["y"]["value"])

            if subj_id in person_map and obj_id in person_map:
                person_map[subj_id].knows.append(person_map[obj_id])
