"""
owlready2_queries.py

Bindings and convenience query functions for the OWL2Bench SPARQL queries implemented
using Owlready2 object-oriented access.

Each query function includes a brief documentation block with:
- Description: meaning of the original SPARQL query.
- Construct Involved: OWL 2 language construct required for reasoning.
- Profile: OWL 2 profile(s) applicable to the query.

Source of descriptions: `owl2bench/resources/OWL2BENCH_SPARQL_Queries.txt`
"""
import time

from owlready2 import get_ontology, sync_reasoner_pellet, sync_reasoner

path_to_owl = r"/home/sorin/dev/krrood_experiments/owl2bench/resources/refactored_ontologies/owl2benchRlFixed.owl"

start_time = time.time()
onto = get_ontology(path_to_owl).load()
loading_time = time.time() - start_time

def perform_reasoning(reasoner, onto):
    start_time = time.time()
    with onto:
        if reasoner == "pellet":
            sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=True)
        elif reasoner == "hermit":
            sync_reasoner(infer_property_values=True)
    reasoning_time = time.time() - start_time
    return reasoning_time


def query_one(onto):
    """
    Description:
        Find the instances who know some other instance.
    Construct Involved:
        knows is a Reflexive Object Property.
    Profile:
        EL, QL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.knows:
            results.add((x, y))

    return results


def query_two(onto):
    """
    Description:
        Find Person instances who are member (Student or Employee) of some Organization.
    Construct Involved:
        ObjectPropertyChain (isMemberOf).
    Profile:
        EL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.isMemberOf:
            results.add((x, y))

    return results


def query_three(onto):
    """
    Description:
        Find the instances of Organization which is a Part Of any other Organization.
    Construct Involved:
        isPartOf is a Transitive Object Property. Domain(Organization), Range(Organization).
    Profile:
        EL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.isPartOf:
            results.add((x, y))

    return results


def query_four(onto):
    """
    Description:
        Find the age of all the Person instances.
    Construct Involved:
        hasAge is a Functional Data Property. Domain(Person), Range(xsd:nonNegativeInteger).
    Profile:
        EL, RL, DL
    """
    results = set()  # to mimic SELECT DISTINCT
    for x in onto.individuals():
        if x.hasAge:
            results.add((x, x.hasAge))

    return results


def query_five(onto):
    """
    Description:
        Find all the instances of class T20CricketFan. T20CricketFan is a Person who is crazy about T20Cricket.
    Construct Involved:
        ObjectHasValue
    Profile:
        EL, RL, DL
    """
    results = set()

    T20CricketFan = onto.T20CricketFan
    for individual in T20CricketFan.instances():
        results.add(individual)

    return results


def query_six(onto):
    """
    Description:
        Find all the instances of class SelfAwarePerson. SelfAwarePerson is a Person who knows themselves.
    Construct Involved:
        ObjectHasSelf
    Profile:
        EL, DL
    """
    results = set()

    for x in onto.SelfAwarePerson.instances():
        results.add(x)

    return results


def query_seven(onto):
    """
    Description:
        Find all the alumni of a University.
    Construct Involved:
        hasAlumnus is an Inverse Object Property of hasDegreeFrom. Domain(University), Range(Person).
    Profile:
        QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.hasAlumnus:
            results.add((x, y))
    return results


def query_eight(onto):
    """
    Description:
        Find Affiliations of all the Organizations.
    Construct Involved:
        isAffiliatedOrganizationOf is an Asymmetric Object Property. Domain(Organization), Range(Organization).
    Profile:
        QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.isAffiliatedOrganizationOf:
            results.add((x, y))

    return results


def query_nine(onto):
    """
    Description:
        Find all the colleges having Non-Science discipline.
    Construct Involved:
        ObjectComplementOf (NonScience is complement of Science).
    Profile:
        QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        if x in onto.NonScience.hasCollegeDiscipline:
            results.add(x)

    return results


def query_ten(onto):
    """
    Description:
        Find all the instances who has Collaboration with any other instance.
    Construct Involved:
        hasCollaborationWith is a Symmetric Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.hasCollaborationWith:
            results.add((x, y))

    return results


def query_eleven(onto):
    """
    Description:
        Find all the instances who are advised by some other instance.
    Construct Involved:
        isAdvisedBy is an Irreflexive Object Property. Domain(Person), Range(Person).
    Profile:
        QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.isAdvisedBy:
            results.add((x, y))

    return results


def query_twelve(onto):
    """
    Description:
        Find all the instances of class Person. A Person is union of Man and Woman.
    Construct Involved:
        ObjectUnionOf
    Profile:
        RL, DL
    """
    results = set()

    for x in onto.Person.instances():
        results.add(x)

    return results


def query_thirteen(onto):
    """
    Description:
        Find all the instances of class WomanCollege. WomanCollege is a College which has only Woman Students.
    Construct Involved:
        AllValuesFrom
    Profile:
        RL, DL
    """
    results = set()

    for x in onto.WomanCollege.instances():
        results.add(x)

    return results


def query_fourteen(onto):
    """
    Description:
        Find all the instances of class LeisureStudent. LeisureStudent is a Student who takes maximum one course.
    Construct Involved:
        ObjectMaxCardinality
    Profile:
        RL, DL
    """
    results = set()

    for x in onto.LeisureStudent.instances():
        results.add(x)

    return results


def query_fifteen(onto):
    """
    Description:
        Find the head of all the Organization.
    Construct Involved:
        isHeadOf is an Inverse Functional Object Property. Domain(Person), Range(Organization).
    Profile:
        RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.isHeadOf:
            results.add((x, y))

    return results


def query_sixteen(onto):
    """
    Description:
        Find all the Organizations who has head.
    Construct Involved:
        hasHead is a Functional Object Property. Domain(Organization), Range(Person).
    Profile:
        RL, DL
    """
    results = set()

    for x in onto.individuals():
        if x.hasHead:
            results.add((x, x.hasHead))

    return results


def query_seventeen(onto):
    """
    Description:
        Find all the instances of class UGStudent. UGStudent is a Student who enrolls in exactly one UGProgram.
    Construct Involved:
        ObjectExactCardinality
    Profile:
        DL
    """
    results = set()

    for x in onto.UGStudent.instances():
        results.add(x)

    return results


def query_eighteen(onto):
    """
    Description:
        Find all the instances of class PeopleWithManyHobbies. PeopleWithManyHobbies is a Person who has minimum 3 Hobbies.
    Construct Involved:
        ObjectMinCardinality
    Profile:
        DL
    """
    results = set()

    for x in onto.PeopleWithManyHobbies.instances():
        results.add(x)

    return results


def query_nineteen(onto):
    """
    Description:
        Find all the instances of class Faculty. A Faculty is an Employee who teaches some Course.
    Construct Involved:
        ObjectSomeValuesFrom
    Profile:
        EL, QL, RL, DL
    """
    results = set()

    for x in onto.Faculty.instances():
        results.add(x)

    return results


def query_twenty(onto):
    """
    Description:
        Find all the instances who have same home town with any other instance.
    Construct Involved:
        hasSameHomeTownWith (likely symmetric).
    Profile:
        EL, QL, RL, DL
    """
    results = set()

    for x in onto.individuals():
        for y in x.hasSameHomeTownWith:
            results.add((x, y))

    return results


def query_twenty_one(onto):
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
    results = set()

    for x in onto.Student.instances():
        for y in x.isStudentOf:
            for z in y.isPartOf:
                if onto.Engineering in z.hasCollegeDiscipline:
                    results.add((x, y))

    return results


def query_twenty_two(onto):
    """
    Description:
        Find students who took a course taught by the Dean of an Organization:
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
    results = set()

    for s in onto.Student.instances():
        for x in onto.Organization.instances():
            for z in x.hasDean:
                for c in z.teachesCourse:
                    if c in s.takesCourse:
                        results.add((s, c))

    return results

# Function to run all queries and capture individual and total execution time
def run_all_queries_with_timing(onto):
    query_functions = [
        query_one, query_two, query_three, query_four, query_five, query_seven,
        query_eight, query_ten, query_eleven, query_twelve, query_fifteen, query_sixteen,
        query_nineteen, query_twenty, query_twenty_one, query_twenty_two,
    ]
    query_times = {}
    total_query_time = 0

    for query_func in query_functions:
        query_name = query_func.__name__
        start_time = time.time()
        results = query_func(onto)  # Execute the query
        query_time = time.time() - start_time
        query_times[query_name] = query_time
        total_query_time += query_time

    return query_times, total_query_time

# Perform reasoning with Pellet and measure time
#pellet_reasoning_time = perform_reasoning("pellet", onto)
# Run and time all queries for Pellet
#pellet_query_times, pellet_total_query_time = run_all_queries_with_timing(onto)

# Perform reasoning with HermiT and measure time
hermit_reasoning_time = perform_reasoning("hermit", onto)
# Run and time all queries for HermiT
hermit_query_times, hermit_total_query_time = run_all_queries_with_timing(onto)

# Print timings
print(f"Ontology Loading Time: {loading_time:.4f} seconds")
#print(f"Pellet Reasoning Time: {pellet_reasoning_time:.4f} seconds")
print(f"HermiT Reasoning Time: {hermit_reasoning_time:.4f} seconds")
print("\nQuery Execution Times:")
print("Pellet:")
#for query, time_taken in pellet_query_times.items():
#    print(f"{query}: {time_taken:.4f} seconds")
#print(f"Total Query Execution Time (Pellet): {pellet_total_query_time:.4f} seconds")
print("\nHermiT:")
for query, time_taken in hermit_query_times.items():
    print(f"{query}: {time_taken:.4f} seconds")
print(f"Total Query Execution Time (HermiT): {hermit_total_query_time:.4f} seconds")


def run_all_queries_rl(onto):
    """
    Run a selected subset of queries intended for the RL profile reasoning run.
    Returns a mapping from query identifier to result cardinality.
    """
    return {
        "two": len(query_two(onto)),
        "three": len(query_three(onto)),
        "four": len(query_four(onto)),
        "five": len(query_five(onto)),
        "seven": len(query_seven(onto)),
        "eight": len(query_eight(onto)),
        "ten": len(query_ten(onto)),
        "eleven": len(query_eleven(onto)),
        "twelve": len(query_twelve(onto)),
        "fifteen": len(query_fifteen(onto)),
         "sixteen": len(query_sixteen(onto)),
        "nineteen": len(query_nineteen(onto)),
        "twenty": len(query_twenty(onto)),
        "twenty_one": len(query_twenty_one(onto)),
        "twenty_two": len(query_twenty_two(onto)),
    }


print(run_all_queries_rl(onto))
