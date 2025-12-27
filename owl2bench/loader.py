from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

from .model.base import *
from .model.organizations import *


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

        # get all organizations
        self.world.organizations = self._get_organizations()

        # get all organization members
        self._update_organization_members()

        # get all organization isPartOf relationships
        self._update_organization_is_part_of_relationships()

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

    def _get_organizations(self) -> List[Organization]:
        """
        Retrieves all organizations.

        :return: A list of Organization objects.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?type WHERE {
                ?x rdf:type ?type .
                FILTER(?type IN (owl2bench:University, owl2bench:College, owl2bench:Department, owl2bench:ResearchGroup))
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        organizations = []
        type_mapping = {
            "http://benchmark/OWL2Bench#University": University,
            "http://benchmark/OWL2Bench#College": College,
            "http://benchmark/OWL2Bench#Department": Department,
            "http://benchmark/OWL2Bench#ResearchGroup": ResearchGroup,
        }

        for b in bindings:
            organization_type = b["type"]["value"]
            cls = type_mapping.get(organization_type, Organization)
            organizations.append(cls(identifier=str(b["x"]["value"])))
        return organizations

    def _update_organization_members(self):
        """
        Updates the members relationship for organizations.
        """
        query = (
            PREFIXES
            + """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?person ?org WHERE {
                ?p rdfs:subPropertyOf* owl2bench:isMemberOf .
                ?person ?p ?org .
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        person_map = {p.identifier: p for p in self.world.persons}
        org_map = {o.identifier: o for o in self.world.organizations}

        for b in bindings:
            person_identifier = str(b["person"]["value"])
            organization_identifier = str(b["org"]["value"])

            if person_identifier in person_map and organization_identifier in org_map:
                org_map[organization_identifier].members.append(
                    person_map[person_identifier]
                )

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
            subject_identifier = str(b["x"]["value"])
            object_identifier = str(b["y"]["value"])

            if subject_identifier in person_map and object_identifier in person_map:
                person_map[subject_identifier].knows.append(
                    person_map[object_identifier]
                )

    def _update_organization_is_part_of_relationships(self):
        """
        Updates the isPartOf relationship between organizations.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?y WHERE {
                ?x owl2bench:isPartOf ?y .
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        org_map = {o.identifier: o for o in self.world.organizations}

        for b in bindings:
            subject_identifier = str(b["x"]["value"])
            object_identifier = str(b["y"]["value"])

            if subject_identifier in org_map and object_identifier in org_map:
                org_map[subject_identifier].is_part_of.append(
                    org_map[object_identifier]
                )
