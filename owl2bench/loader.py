from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

from .model.base import *
from .model.organizations import *
from .model.college_disciplines import *


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
        self._update_person_collaborations()
        self._update_person_advisors()

        # get all organizations
        self.world.organizations = self._get_organizations()

        # get all organization members
        self._update_organization_members()

        # get all organization isPartOf relationships
        self._update_organization_is_part_of_relationships()

        # get all university alumni
        self._update_university_alumni()

        # get all organization affiliations
        self._update_organization_affiliations()

        # get all college disciplines
        self.world.college_disciplines = self._get_college_disciplines()
        self._update_college_disciplines()

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
            SELECT DISTINCT ?x ?firstName ?lastName ?gender ?telephone ?age ?email ?title WHERE {
                ?x rdf:type owl2bench:Person .
                OPTIONAL { ?x owl2bench:hasFirstName ?firstName }
                OPTIONAL { ?x owl2bench:hasLastName ?lastName }
                OPTIONAL { ?x owl2bench:hasTelephone ?telephone }
                OPTIONAL { ?x owl2bench:hasAge ?age }
                OPTIONAL { ?x owl2bench:hasEmailAddress ?email }
                OPTIONAL { ?x owl2bench:hasTitle ?title }
                OPTIONAL {
                    ?x rdf:type ?type .
                    FILTER (?type IN (owl2bench:Man, owl2bench:Woman))
                    BIND (REPLACE(STR(?type), "^.*#", "") AS ?gender)
                }
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
                    first_name=b.get("firstName", {}).get("value", ""),
                    last_name=b.get("lastName", {}).get("value", ""),
                    gender=b.get("gender", {}).get("value"),
                    telephone_number=b.get("telephone", {}).get("value", ""),
                    age=b.get("age", {}).get("value", ""),
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

    def _update_person_collaborations(self):
        """
        Updates the collaboratesWith relationship between persons.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?y WHERE {
                ?x owl2bench:hasCollaborationWith ?y .
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
                person_map[subject_identifier].collaborates_with.append(
                    person_map[object_identifier]
                )

    def _update_person_advisors(self):
        """
        Updates the isAdvisedBy relationship between persons.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?y WHERE {
                ?x owl2bench:isAdvisedBy ?y .
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
                person_map[subject_identifier].is_advised_by.append(
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

    def _update_university_alumni(self):
        """
        Updates the alumni relationship for universities.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?university ?person WHERE {
                ?university owl2bench:hasAlumnus ?person .
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        person_map = {p.identifier: p for p in self.world.persons}
        org_map = {o.identifier: o for o in self.world.organizations}

        for b in bindings:
            university_identifier = str(b["university"]["value"])
            person_identifier = str(b["person"]["value"])

            if university_identifier in org_map and person_identifier in person_map:
                organization = org_map[university_identifier]
                if isinstance(organization, University):
                    organization.alumni.append(person_map[person_identifier])

    def _update_organization_affiliations(self):
        """
        Updates the affiliated organizations relationship.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?y WHERE {
                ?x owl2bench:isAffiliatedOrganizationOf ?y .
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
                org_map[subject_identifier].affiliated_organizations.append(
                    org_map[object_identifier]
                )

    def _get_college_disciplines(self) -> List[CollegeDiscipline]:
        """
        Retrieves all college disciplines.

        :return: A list of CollegeDiscipline objects.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?x ?type WHERE {
                ?x rdf:type ?type .
                ?type rdfs:subClassOf* owl2bench:CollegeDiscipline .
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        disciplines = []
        # Map of RDF type to Python class
        type_mapping = {
            "http://benchmark/OWL2Bench#Engineering": Engineering,
            "http://benchmark/OWL2Bench#AeronauticalEngineering": AeronauticalEngineering,
            "http://benchmark/OWL2Bench#BiomedicalEngineering": BiomedicalEngineering,
            "http://benchmark/OWL2Bench#ChemicalEngineering": ChemicalEngineering,
            "http://benchmark/OWL2Bench#CivilEngineering": CivilEngineering,
            "http://benchmark/OWL2Bench#ComputerEngineering": ComputerEngineering,
            "http://benchmark/OWL2Bench#ElectricalEngineering": ElectricalEngineering,
            "http://benchmark/OWL2Bench#IndustryEngineering": IndustryEngineering,
            "http://benchmark/OWL2Bench#MaterialScienceEngineering": MaterialScienceEngineering,
            "http://benchmark/OWL2Bench#MechanicalEngineering": MechanicalEngineering,
            "http://benchmark/OWL2Bench#PetroleumlEngineering": PetroleumlEngineering,
            "http://benchmark/OWL2Bench#FineArts": FineArts,
            "http://benchmark/OWL2Bench#Architecture": Architecture,
            "http://benchmark/OWL2Bench#AsianArts": AsianArts,
            "http://benchmark/OWL2Bench#Drama": Drama,
            "http://benchmark/OWL2Bench#LatinArts": LatinArts,
            "http://benchmark/OWL2Bench#MediaArtsAndSciences": MediaArtsAndSciences,
            "http://benchmark/OWL2Bench#MedievalArts": MedievalArts,
            "http://benchmark/OWL2Bench#ModernArts": ModernArts,
            "http://benchmark/OWL2Bench#MusicsClass": MusicsClass,
            "http://benchmark/OWL2Bench#PerformingArts": PerformingArts,
            "http://benchmark/OWL2Bench#TheatreAndDance": TheatreAndDance,
            "http://benchmark/OWL2Bench#HumanitiesAndSocial": HumanitiesAndSocial,
            "http://benchmark/OWL2Bench#Anthropology": Anthropology,
            "http://benchmark/OWL2Bench#Economics": Economics,
            "http://benchmark/OWL2Bench#English": English,
            "http://benchmark/OWL2Bench#History": History,
            "http://benchmark/OWL2Bench#Humanities": Humanities,
            "http://benchmark/OWL2Bench#Linguistics": Linguistics,
            "http://benchmark/OWL2Bench#ModernLanguages": ModernLanguages,
            "http://benchmark/OWL2Bench#Philosophy": Philosophy,
            "http://benchmark/OWL2Bench#Psychology": Psychology,
            "http://benchmark/OWL2Bench#Religions": Religions,
            "http://benchmark/OWL2Bench#Management": Management,
            "http://benchmark/OWL2Bench#DesignManagement": DesignManagement,
            "http://benchmark/OWL2Bench#FinancialAndAccountingManagement": FinancialAndAccountingManagement,
            "http://benchmark/OWL2Bench#HumanResourceManagement": HumanResourceManagement,
            "http://benchmark/OWL2Bench#MarketingManagement": MarketingManagement,
            "http://benchmark/OWL2Bench#OperationsManagement": OperationsManagement,
            "http://benchmark/OWL2Bench#ProjectManagement": ProjectManagement,
            "http://benchmark/OWL2Bench#PublicRelationsManagement": PublicRelationsManagement,
            "http://benchmark/OWL2Bench#RiskManagement": RiskManagement,
            "http://benchmark/OWL2Bench#SalesManagement": SalesManagement,
            "http://benchmark/OWL2Bench#SupplyChainManagement": SupplyChainManagement,
        }

        for b in bindings:
            discipline_type = b["type"]["value"]
            cls = type_mapping.get(discipline_type, CollegeDiscipline)
            disciplines.append(cls(identifier=str(b["x"]["value"])))
        return disciplines

    def _update_college_disciplines(self):
        """
        Updates the disciplines relationship for colleges.
        """
        query = (
            PREFIXES
            + """
            SELECT DISTINCT ?college ?discipline WHERE {
                ?college owl2bench:hasCollegeDiscipline ?discipline .
            }
            """
        )

        self.sparql_wrapper.setQuery(query)
        results = self.sparql_wrapper.query().convert()
        bindings = results["results"]["bindings"]

        college_map = {
            o.identifier: o for o in self.world.organizations if isinstance(o, College)
        }
        discipline_map = {d.identifier: d for d in self.world.college_disciplines}

        for b in bindings:
            college_identifier = str(b["college"]["value"])
            discipline_identifier = str(b["discipline"]["value"])

            if (
                college_identifier in college_map
                and discipline_identifier in discipline_map
            ):
                college_map[college_identifier].disciplines.append(
                    discipline_map[discipline_identifier]
                )
