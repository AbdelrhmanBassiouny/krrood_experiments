"""
Load a TBox plus n persons linked by hasSameHomeTownWith, in eager or component mode, and print measurements as JSON.

Usage: python probe.py TBOX N MODE TOPOLOGY OUT_DIR   (MODE: eager|component, TOPOLOGY: chain|star)
"""
import json, sys, time
import rdflib
from rdflib.namespace import OWL, RDF

tbox, n, mode, topology, out_dir = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
BENCH = rdflib.Namespace("http://benchmark/OWL2Bench#")
DATA = rdflib.Namespace("http://example.org/data#")

graph = rdflib.Graph()
graph.parse(tbox)
persons = [DATA[f"p{i}"] for i in range(n)]
for person in persons:
    graph.add((person, RDF.type, OWL.NamedIndividual))
    graph.add((person, RDF.type, BENCH.Person))
if topology == "chain":
    edges = [(persons[i], persons[i + 1]) for i in range(n - 1)]
else:
    edges = [(persons[0], persons[i]) for i in range(1, n)]
for source, target in edges:
    graph.add((source, BENCH.hasSameHomeTownWith, target))
data_file = f"{out_dir}/data_{topology}_{n}.rdf"
graph.serialize(data_file, format="xml")

from krrood_experiments.aamas27 import loading_worker
loading_worker._import_krrood()
from krrood.ontomatic.property_descriptor.property_descriptor_relation import PropertyDescriptorRelation
from krrood.entity_query_language.symbol_graph import SymbolGraph  # noqa: F401  (location checked below)
from krrood_experiments.owl2bench.ontomatic.helpers import load_instances_for_owl2bench_with_predicates

PropertyDescriptorRelation.eager_symmetric_transitive_closure = mode == "eager"
calls = {"update_source": 0, "added": 0}
original_update_source = PropertyDescriptorRelation.update_source
def counting_update_source(self):
    calls["update_source"] += 1
    added = original_update_source(self)
    calls["added"] += bool(added)
    return added
PropertyDescriptorRelation.update_source = counting_update_source

start = time.perf_counter()
registry = load_instances_for_owl2bench_with_predicates(data_file)
seconds = time.perf_counter() - start

partners = {}
for uri, objects in registry._by_uri.items():
    if not uri.startswith(str(DATA)):
        continue
    values = set()
    for obj in objects:
        for other in getattr(obj, "has_same_home_town_with", None) or []:
            values.add(other.uri)
    partners[uri.split("#")[1]] = sorted(v.split("#")[1] for v in values)
home_town_relations = sum(
    1 for relation in SymbolGraph().relations() if type(relation).__name__ and
    getattr(relation, "wrapped_field", None) is not None and relation.wrapped_field.name == "has_same_home_town_with"
)
print(json.dumps({
    "n": n, "mode": mode, "topology": topology, "seconds": round(seconds, 4),
    "update_source_calls": calls["update_source"], "values_added": calls["added"],
    "home_town_relations_in_graph": home_town_relations, "partners": partners,
}))
