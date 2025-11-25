from typing import Set, Tuple, Any, Dict
from rdflib import Graph
from owlrl import OWLRL_Semantics, DeductiveClosure
#from rdflib.plugins.sparql.results import JSONResult

# RDFLIB requires an already inferred ontology (or maybe not, for me it took longer then an hour and i interrupted it.)
ONTO_PATH = r"owl2bench/resources/refactored_ontologies/owl2benchRlinferred.owl"

# Common SPARQL prefixes used by the OWL2Bench queries
PREFIXES = "\n".join([
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
    "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>",
    "PREFIX owl2bench: <http://benchmark/OWL2Bench#>",
]) + "\n"


def _load_graph(path: str = ONTO_PATH) -> Graph:
    """
    Load the ontology into an rdflib Graph. Returns the Graph.
    """
    g = Graph()
    # try common RDF formats; most OWL files are RDF/XML
    g.parse(path, format="xml")
    #DeductiveClosure(OWLRL_Semantics).expand(g)
    return g


def _run_sparql(g: Graph, query: str) -> Set[Tuple[str, ...]]:
    """
    Execute a SPARQL SELECT query (query should include PREFIX declarations).
    Returns a set of tuples of stringified bindings (in order of SELECT variables).
    """
    results = set()
    qres = g.query(query)
    # rdflib returns rows that can be accessed by position
    for row in qres:
        results.add(tuple(str(v) if v is not None else "" for v in row))
    return results


def query_one(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the instances who know some other instance.
    Construct Involved:
        knows is a Reflexive Object Property.
    Profile:
        EL, QL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:knows ?y }"
    return _run_sparql(g, q)


def query_two(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find Person instances who are member (Student or Employee) of some Organization.
    Construct Involved:
        ObjectPropertyChain.
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isMemberOf ?y }"
    return _run_sparql(g, q)


def query_three(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the instances of Organization which is a Part Of any other Organization.
    Construct Involved:
        isPartOf is a Transitive Object Property. Domain(Organization), Range(Organization).
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isPartOf ?y }"
    return _run_sparql(g, q)


def query_four(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the age of all the Person instances.
    Construct Involved:
        hasAge is a Functional Data Property. Domain(Person), Range(xsd:nonNegativeInteger).
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasAge ?y }"
    return _run_sparql(g, q)


def query_five(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class T20CricketFan. T20CricketFan is a Person who is crazy about T20Cricket.
    Construct Involved:
        ObjectHasValue.
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:T20CricketFan }"
    return _run_sparql(g, q)


def query_six(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class SelfAwarePerson. SelfAwarePerson is a Person who knows themselves.
    Construct Involved:
        ObjectHasSelf.
    Profile:
        EL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:SelfAwarePerson }"
    return _run_sparql(g, q)


def query_seven(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the alumni of a University.
    Construct Involved:
        hasAlumnus is an Inverse Object Property of hasDegreeFrom. Domain(University), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasAlumnus ?y }"
    return _run_sparql(g, q)


def query_eight(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find Affiliations of all the Organizations.
    Construct Involved:
        isAffiliatedOrganizationOf is an Asymmetric Object Property. Domain(Organization), Range(Organization).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isAffiliatedOrganizationOf ?y }"
    return _run_sparql(g, q)


def query_nine(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the colleges having Non-Science discipline.
    Construct Involved:
        ObjectComplementOf (NonScience is complement of Science).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x owl2bench:hasCollegeDiscipline owl2bench:NonScience }"
    return _run_sparql(g, q)


def query_ten(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who has Collaboration with any other instance.
    Construct Involved:
        hasCollaborationWith is a Symmetric Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasCollaborationWith ?y }"
    return _run_sparql(g, q)


def query_eleven(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who are advised by some other instance.
    Construct Involved:
        isAdvisedBy is an Irreflexive Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isAdvisedBy ?y }"
    return _run_sparql(g, q)


def query_twelve(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class Person. A Person is union of Man and Woman.
    Construct Involved:
        ObjectUnionOf.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:Person }"
    return _run_sparql(g, q)


def query_thirteen(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class WomanCollege. WomanCollege is a College which has only Woman Students.
    Construct Involved:
        AllValuesFrom.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:WomanCollege }"
    return _run_sparql(g, q)


def query_fourteen(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class LeisureStudent. LeisureStudent is a Student who takes maximum one course.
    Construct Involved:
        ObjectMaxCardinality.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:LeisureStudent }"
    return _run_sparql(g, q)


def query_fifteen(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the head of all the Organization.
    Construct Involved:
        isHeadOf is an Inverse Functional Object Property. Domain(Person), Range(Organization).
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isHeadOf ?y }"
    return _run_sparql(g, q)


def query_sixteen(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the Organizations who has head.
    Construct Involved:
        hasHead is a Functional Object Property. Domain(Organization), Range(Person).
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasHead ?y }"
    return _run_sparql(g, q)


def query_seventeen(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class UGStudent. UGStudent is a Student who enrolls in exactly one UGProgram.
    Construct Involved:
        ObjectExactCardinality.
    Profile:
        DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:UGStudent }"
    return _run_sparql(g, q)


def query_eighteen(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class PeopleWithManyHobbies. PeopleWithManyHobbies is a Person who has minimum 3 Hobbies.
    Construct Involved:
        ObjectMinCardinality.
    Profile:
        DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:PeopleWithManyHobbies }"
    return _run_sparql(g, q)


def query_nineteen(g: Graph) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class Faculty. A Faculty is an Employee who teaches some Course.
    Construct Involved:
        ObjectSomeValuesFrom.
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:Faculty }"
    return _run_sparql(g, q)


def query_twenty(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who have same home town with any other instance.
    Construct Involved:
        hasSameHomeTownWith (likely symmetric).
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasSameHomeTownWith ?y }"
    return _run_sparql(g, q)


def query_twenty_one(g: Graph) -> Set[Tuple[str, str, str]]:
    """
    Description:
        Find all the Engineering Students:
        ?s rdf:type :Student .
        ?s :isStudentOf ?y .
        ?y :isPartOf ?z .
        ?z :hasCollegeDiscipline :Engineering
    Construct Involved:
        ObjectProperty chain + class membership (Student, Engineering).
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + (
        "SELECT DISTINCT ?s ?org ?z WHERE {"
        " ?s rdf:type owl2bench:Student ."
        " ?s owl2bench:isStudentOf ?org ."
        " ?org owl2bench:isPartOf ?z ."
        " ?z owl2bench:hasCollegeDiscipline owl2bench:Engineering ."
        " }"
    )
    return _run_sparql(g, q)


def query_twenty_two(g: Graph) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the students who took course taught by the Dean of the Organization.
        ?s rdf:type :Student .
        ?x rdf:type :Organization .
        ?x :hasDean ?z .
        ?z :teachesCourse ?c .
        ?s :takesCourse ?c
    Construct Involved:
        Property chain between Organization.hasDean -> Person.teachesCourse and Student.takesCourse.
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + (
        "SELECT DISTINCT ?s ?c WHERE {"
        " ?s rdf:type owl2bench:Student ."
        " ?x rdf:type owl2bench:Organization ."
        " ?x owl2bench:hasDean ?z ."
        " ?z owl2bench:teachesCourse ?c ."
        " ?s owl2bench:takesCourse ?c ."
        " }"
    )
    return _run_sparql(g, q)


def run_all_queries_rl(g: Graph) -> Dict[str, int]:
    """
    Run the subset of queries intended for the RL profile run and return counts.
    """
    return {
        "two": len(query_two(g)),
        "three": len(query_three(g)),
        "four": len(query_four(g)),
        "five": len(query_five(g)),
        "seven": len(query_seven(g)),
        "eight": len(query_eight(g)),
        "ten": len(query_ten(g)),
        "eleven": len(query_eleven(g)),
        "twelve": len(query_twelve(g)),
        "fifteen": len(query_fifteen(g)),
        "sixteen": len(query_sixteen(g)),
        "nineteen": len(query_nineteen(g)),
        "twenty": len(query_twenty(g)),
        "twenty_one": len(query_twenty_one(g)),
        "twenty_two": len(query_twenty_two(g)),
    }


# Convenience: load graph and print RL-run summary when module executed
if __name__ == "__main__":
    g = _load_graph()
    print(run_all_queries_rl(g))