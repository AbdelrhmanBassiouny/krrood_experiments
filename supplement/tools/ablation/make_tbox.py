"""Write the OWL2Bench TBox (the raw data without its individuals) to a file."""
import sys
import rdflib
from rdflib.namespace import OWL, RDF

source, target = sys.argv[1], sys.argv[2]
graph = rdflib.Graph()
graph.parse(source)
individuals = set(graph.subjects(RDF.type, OWL.NamedIndividual))
for subject in individuals:
    graph.remove((subject, None, None))
    graph.remove((None, None, subject))
graph.serialize(target, format="xml")
print(f"removed {len(individuals)} individuals, kept {len(graph)} triples")
