from typing import Set, Tuple, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
import time

# Common SPARQL prefixes used by the OWL2Bench queries
PREFIXES = "\n".join([
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
    "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>",
    "PREFIX owl2bench: <http://benchmark/OWL2Bench#>",
]) + "\n"


def _run_sparql(endpoint: str, query: str) -> Set[Tuple[str, ...]]:
    """
    Execute a SPARQL SELECT query against the given endpoint.
    Returns a set of tuples of stringified bindings (in order of SELECT variables).
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except Exception:
        return set()

    vars_order = results.get('head', {}).get('vars', [])
    res_set = set()
    for binding in results.get('results', {}).get('bindings', []):
        row = tuple(binding.get(var, {}).get('value', '') for var in vars_order)
        res_set.add(row)
    return res_set


def query_one(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the instances who know some other instance.
    Construct Involved:
        knows is a Reflexive Object Property.
    Profile:
        EL, QL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:knows ?y }"
    return _run_sparql(endpoint, q)


def query_two(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find Person instances who are member (Student or Employee) of some Organization.
    Construct Involved:
        ObjectPropertyChain.
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isMemberOf ?y }"
    return _run_sparql(endpoint, q)


def query_three(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the instances of Organization which is a Part Of any other Organization.
    Construct Involved:
        isPartOf is a Transitive Object Property. Domain(Organization), Range(Organization).
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isPartOf ?y }"
    return _run_sparql(endpoint, q)


def query_four(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the age of all the Person instances.
    Construct Involved:
        hasAge is a Functional Data Property. Domain(Person), Range(xsd:nonNegativeInteger).
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasAge ?y }"
    return _run_sparql(endpoint, q)


def query_five(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class T20CricketFan. T20CricketFan is a Person who is crazy about T20Cricket.
    Construct Involved:
        ObjectHasValue.
    Profile:
        EL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:T20CricketFan }"
    return _run_sparql(endpoint, q)


def query_six(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class SelfAwarePerson. SelfAwarePerson is a Person who knows themselves.
    Construct Involved:
        ObjectHasSelf.
    Profile:
        EL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:SelfAwarePerson }"
    return _run_sparql(endpoint, q)


def query_seven(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the alumni of a University.
    Construct Involved:
        hasAlumnus is an Inverse Object Property of hasDegreeFrom. Domain(University), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasAlumnus ?y }"
    return _run_sparql(endpoint, q)


def query_eight(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find Affiliations of all the Organizations.
    Construct Involved:
        isAffiliatedOrganizationOf is an Asymmetric Object Property. Domain(Organization), Range(Organization).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isAffiliatedOrganizationOf ?y }"
    return _run_sparql(endpoint, q)


def query_nine(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the colleges having Non-Science discipline.
    Construct Involved:
        ObjectComplementOf (NonScience is complement of Science).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x owl2bench:hasCollegeDiscipline owl2bench:NonScience }"
    return _run_sparql(endpoint, q)


def query_ten(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who has Collaboration with any other instance.
    Construct Involved:
        hasCollaborationWith is a Symmetric Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasCollaborationWith ?y }"
    return _run_sparql(endpoint, q)


def query_eleven(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who are advised by some other instance.
    Construct Involved:
        isAdvisedBy is an Irreflexive Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isAdvisedBy ?y }"
    return _run_sparql(endpoint, q)


def query_twelve(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class Person. A Person is union of Man and Woman.
    Construct Involved:
        ObjectUnionOf.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:Person }"
    return _run_sparql(endpoint, q)


def query_thirteen(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class WomanCollege. WomanCollege is a College which has only Woman Students.
    Construct Involved:
        AllValuesFrom.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:WomanCollege }"
    return _run_sparql(endpoint, q)


def query_fourteen(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class LeisureStudent. LeisureStudent is a Student who takes maximum one course.
    Construct Involved:
        ObjectMaxCardinality.
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:LeisureStudent }"
    return _run_sparql(endpoint, q)


def query_fifteen(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find the head of all the Organization.
    Construct Involved:
        isHeadOf is an Inverse Functional Object Property. Domain(Person), Range(Organization).
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:isHeadOf ?y }"
    return _run_sparql(endpoint, q)


def query_sixteen(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the Organizations who has head.
    Construct Involved:
        hasHead is a Functional Object Property. Domain(Organization), Range(Person).
    Profile:
        RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasHead ?y }"
    return _run_sparql(endpoint, q)


def query_seventeen(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class UGStudent. UGStudent is a Student who enrolls in exactly one UGProgram.
    Construct Involved:
        ObjectExactCardinality.
    Profile:
        DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:UGStudent }"
    return _run_sparql(endpoint, q)


def query_eighteen(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class PeopleWithManyHobbies. PeopleWithManyHobbies is a Person who has minimum 3 Hobbies.
    Construct Involved:
        ObjectMinCardinality.
    Profile:
        DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:PeopleWithManyHobbies }"
    return _run_sparql(endpoint, q)


def query_nineteen(endpoint: str) -> Set[Tuple[str]]:
    """
    Description:
        Find all the instances of class Faculty. A Faculty is an Employee who teaches some Course.
    Construct Involved:
        ObjectSomeValuesFrom.
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x WHERE { ?x rdf:type owl2bench:Faculty }"
    return _run_sparql(endpoint, q)


def query_twenty(endpoint: str) -> Set[Tuple[str, str]]:
    """
    Description:
        Find all the instances who have same home town with any other instance.
    Construct Involved:
        hasSameHomeTownWith (likely symmetric).
    Profile:
        EL, QL, RL, DL
    """
    q = PREFIXES + "SELECT DISTINCT ?x ?y WHERE { ?x owl2bench:hasSameHomeTownWith ?y }"
    return _run_sparql(endpoint, q)


def query_twenty_one(endpoint: str) -> Set[Tuple[str, str, str]]:
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
    return _run_sparql(endpoint, q)


def query_twenty_two(endpoint: str) -> Set[Tuple[str, str]]:
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
    return _run_sparql(endpoint, q)


def run_all_queries_rl(endpoint: str) -> Dict[str, Tuple[int, float]]:
    """
    Run the subset of queries intended for the RL profile and return counts with execution times.
    """
    queries = {
        "two": query_two,
        "three": query_three,
        "four": query_four,
        "five": query_five,
        "seven": query_seven,
        "eight": query_eight,
        "ten": query_ten,
        "eleven": query_eleven,
        "twelve": query_twelve,
        "fifteen": query_fifteen,
        "sixteen": query_sixteen,
        "nineteen": query_nineteen,
        "twenty": query_twenty,
        "twenty_one": query_twenty_one,
        "twenty_two": query_twenty_two,
    }
    results = {}
    for qname, qfunc in queries.items():
        start = time.time()
        res = qfunc(endpoint)
        t = time.time() - start
        results[qname] = (len(res), t)
    return results


# Convenience: run queries and print RL-run summary when module executed
if __name__ == "__main__":
    # Replace with your actual GraphDB or SPARQL endpoint URL
    ENDPOINT = "http://sorin-System-Product-Name:7200/repositories/owl2benchRL_2"

    start_time = time.time()
    query_results = run_all_queries_rl(ENDPOINT)
    total_query_time = sum(t for count, t in query_results.values())
    print("Counts:")
    for q, (count, t) in query_results.items():
        print(f"{q}: {count}")
    print("\nLoading time: 0.0000 seconds (no local loading; assumes pre-loaded endpoint)")
    print("Query times:")
    for q, (count, t) in query_results.items():
        print(f"{q}: {t:.4f} seconds")
    print(f"Total query time: {total_query_time:.4f} seconds")