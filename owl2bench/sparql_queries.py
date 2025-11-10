from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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

    construct_involved: Optional[str]
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
    SELECT DISTINCT ?x WHERE { ?x :hasCollegeDiscipline :NonScience }
    """,
    description="Find all the colleges having Non-Science discipline. NonScience is something which is not Science",
    construct_involved="ObjectComplementOf",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q10 = SPARQLQuery(
    number=10,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE  { ?x  :hasCollaborationWith ?y  }
    """,
    description=" Find all the instances who has Collaboration with any other instance. The query performs search across universities.",
    construct_involved="hasCollaborationWith is a Symmetric Object Property. Domain(Person), Range(Person).",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q11 = SPARQLQuery(
    number=11,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE { ?x  :isAdvisedBy  ?y  }
    """,
    description="Find all the instances who are advised by some other instance.",
    construct_involved=" isAdvisedBy  is an Irreflexive Object Property. Domain(Person), Range(Person)",
    profile=[OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)


q12 = SPARQLQuery(
    number=12,
    query="""
    SELECT  DISTINCT  ?x  WHERE { ?x  rdf:type  :Person}
    """,
    description="Find all the instances of class Person. A Person is union of Man and Woman.",
    construct_involved="ObjectUnionOf",
    profile=[OWLProfile.RL, OWLProfile.DL],
)

q13 = SPARQLQuery(
    number=13,
    query="""
    SELECT  DISTINCT  ?x  WHERE { ?x  rdf:type  :WomanCollege}
    """,
    description="Find all the instances of class WomanCollege. WomanCollege is a College which has only Woman Students.",
    construct_involved="AllValuesFrom",
    profile=[OWLProfile.RL, OWLProfile.DL],
)

q14 = SPARQLQuery(
    number=14,
    query="""
    SELECT  DISTINCT  ?x  WHERE { ?x  rdf:type  :LeisureStudent}
    """,
    description="Find all the instances of class LeisureStudent. Leisure student is a Student who takes Maximum one course.",
    construct_involved="ObjectMaxCardinality",
    profile=[OWLProfile.RL, OWLProfile.DL],
)

q15 = SPARQLQuery(
    number=15,
    query="""
    SELECT  DISTINCT  ?x  WHERE {?x  :isHeadOf  ?y}
    """,
    description="Find the head of all the Organization.",
    construct_involved="isHeadOf is an Inverse Functional Object Property. Domain(Person), Range(Organization).",
    profile=[OWLProfile.RL, OWLProfile.DL],
)

q16 = SPARQLQuery(
    number=16,
    query="""
    SELECT  DISTINCT  ?x  WHERE {?x  :hasHead  ?y}
    """,
    description="Find all the Organizations who has head.",
    construct_involved="hasHead is a Functional Object Property. Domain(Organization), Range(Person).",
    profile=[OWLProfile.RL, OWLProfile.DL],
)

q17 = SPARQLQuery(
    number=17,
    query="""
    SELECT  DISTINCT  ?x  WHERE {?x  rdf:type  :UGStudent}
    """,
    description="Find all the instances of class UGStudent. UGStudent is a Student who enrolls in exactly one UGProgram.",
    construct_involved="ObjectExactCardinality",
    profile=[OWLProfile.DL],
)

q18 = SPARQLQuery(
    number=18,
    query="""
    SELECT DISTINCT ?x WHERE { ?x rdf:type :PeopleWithManyHobbies}
    """,
    description="Find all the instances of class PeopleWithManyHobbies. PeopleWithManyHobbies is a Person who has minimum 3 Hobbies.",
    construct_involved="ObjectMinCardinality",
    profile=[OWLProfile.DL],
)

q19 = SPARQLQuery(
    number=19,
    query="""
    SELECT  DISTINCT  ?x  WHERE { ?x  rdf:type  :Faculty  }
    """,
    description="Find all the instances of class Faculty. A Faculty is an Employee who teaches some Course.",
    construct_involved="ObjectSomeValuesFrom",
    profile=[OWLProfile.EL, OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q20 = SPARQLQuery(
    number=20,
    query="""
    SELECT  DISTINCT  ?x  ?y  WHERE  {?x  :hasSameHomeTownWith  ?y  }
    """,
    description="Find all the instances who have same home town with any other instance. The query performs search across universities.",
    construct_involved=None,
    profile=[OWLProfile.EL, OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q21 = SPARQLQuery(
    number=21,
    query="""
    SELECT DISTINCT ?x ?y WHERE {?x rdf:type :Student. ?x :isStudentOf ?y. ?y :isPartOf ?z . ?z :hasCollegeDiscipline :Engineering}
    """,
    description="Find all the Engineering Students. The Query performs search across all the universities.",
    construct_involved=None,
    profile=[OWLProfile.EL, OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

q22 = SPARQLQuery(
    number=22,
    query="""
    SELECT  DISTINCT  ?s  ?c  WHERE  {?s  rdf:type  :Student.  ?x rdf:type  :Organization.  ?x  :hasDean  ?z.  ?z  :teachesCourse  ?c.  ?s :takesCourse  ?c  }
    """,
    description="Find all the students who took course taught by the Dean of the Organization. The Query performs search across all the universities.",
    construct_involved=None,
    profile=[OWLProfile.EL, OWLProfile.QL, OWLProfile.RL, OWLProfile.DL],
)

all_queries = [
    q1,
    q2,
    q3,
    q4,
    q5,
    q6,
    q7,
    q8,
    q9,
    q10,
    q11,
    q12,
    q13,
    q14,
    q15,
    q16,
    q17,
    q18,
    q19,
    q20,
    q21,
    q22,
]
