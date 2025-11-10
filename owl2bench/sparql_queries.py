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
    description=" Find Person instances who are member (Student or Employee) of some Organization.",
    construct_involved="ObjectPropertyChain.",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)

q3 = SPARQLQuery(
    number=3,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :isMemberOf  ?y  }
    """,
    description=" Find Person instances who are member (Student or Employee) of some Organization.",
    construct_involved="ObjectPropertyChain.",
    profile=[OWLProfile.EL, OWLProfile.RL, OWLProfile.DL],
)
