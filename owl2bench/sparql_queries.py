from dataclasses import dataclass
from enum import Enum
from typing import List


class OWLProfile(Enum):
    DL = 0
    """
    Description Logic
    """

    RL = 1
    """
    Expressive Language
    """

    QL = 2
    """
    Query Language
    """

    EL = 3
    """
    Rule Language
    """


@dataclass
class SPARQLQuery:

    number: int
    """
    The SPARQL query number.
    """

    query: str
    """
    The sparql query to be executed.
    """

    description: str
    """
    Description of the query's meaning .
    """

    construct_involved: str
    """
    OWL 2 language construct involved during reasoning
    """

    profile: List[OWLProfile]
    """
    The OWL 2 profiles to which the SPARQL Query is applicable.
    """


q1 = SPARQLQuery(
    number=1,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :knows  ?y  }
    """,
    description="Find the instances who know some other instance.",
    construct_involved="knows is a Reflexive Object Property.",
    profile=[OWLProfile.EL, OWLProfile.QL, OWLProfile.DL],
)

q2 = SPARQLQuery(
    number=2,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :isMemberOf  ?y  }
    """,
    description="Find Person instances who are member (Student or Employee) of some Organization.",
    construct_involved="ObjectPropertyChain.",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)

q3 = SPARQLQuery(
    number=3,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :isPartOf  ?y  }
    """,
    description="Find the instances of Organization which is a Part Of any other Organization.",
    construct_involved="isPartOf is a Transitive Object Property. Domain(Organization), Range(Organization).",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)

q4 = SPARQLQuery(
    number=4,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :hasAge  ?y  }
    """,
    description="Find the age of all the Person instances.",
    construct_involved="hasAge is a Functional Data Property. Domain(Person), Range(xsd:nonNegativeInteger).",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)

q5 = SPARQLQuery(
    number=5,
    query="""
    SELECT  DISTINCT  ?x  WHERE { ?x  rdf:type  :T20CricketFan  }
    """,
    description="Find all the instances of class T20CricketFan. T20CricketFan is a Person who is crazy about T20Cricket. {T20Cricket} is an instance of Class Cricket.",
    construct_involved="ObjectHasValue.",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)

q6 = SPARQLQuery(
    number=6,
    query="""
    SELECT DISTINCT ?x ?y WHERE { ?x rdf:type :SelfAwarePerson  }
    """,
    description="Find all the instances of class SelfAwarePerson. SelfAwarePerson is a Person who knows themselves.",
    construct_involved="ObjectHasSelf.",
    profile=[OWLProfile.EL, OWLProfile.DL],
)

q7 = SPARQLQuery(
    number=7,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :hasAlumnus  ?y  }
    """,
    description="Find all the alumni of a University.",
    construct_involved=" hasAlumnus is an Inverse Object Property of hasDegreeFrom. Domain(University), Range(Person).",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q8 = SPARQLQuery(
    number=8,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE  {  ?x  :isAffiliatedOrganizationOf  ?y  }
    """,
    description="Find Affiliations of all the Organizations.",
    construct_involved="isAffiliatedOrganizationOf is an Asymmetric Object Property. Domain(Organization), Range(Organization).",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q9 = SPARQLQuery(
    number=9,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE  {  ?x  :isAffiliatedOrganizationOf  ?y  }
    """,
    description="Find Affiliations of all the Organizations.",
    construct_involved="isAffiliatedOrganizationOf is an Asymmetric Object Property. Domain(Organization), Range(Organization).",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)
