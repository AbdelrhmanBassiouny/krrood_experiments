"""
Derives the raw input for N universities from OWL2Bench's generator output (java -jar OWL2Bench.jar N RL), with the
same changes as the paper's one-university raw file: raw(N) = raw(1) + (gen(N) - gen(1)) - (gen(1) - gen(N)), on
the triples without blank nodes, with xsd:string literals written as plain literals as in raw(1). The blank-node
triples (class expressions of the TBox) are those of raw(1); the generator's are checked to be the same for every N.
The generator is OWL2Bench.jar of github.com/kracr/owl2bench at commit 0730bdddfb2d (sha256 1f2d6013cfdc...), run
in its folder next to RandomNames.xlsx and UNIV-BENCH-OWL2RL.owl (with Java 17 or later:
``java --add-opens java.base/java.lang=ALL-UNNAMED -jar OWL2Bench.jar N RL``). Its output is deterministic; the
sha256 of OWL2RL-N.owl begins with 80632f95896a (N = 1), a1a4300baac4 (2), 48f5fae88dd4 (4) and 9fb265df0088 (8).
For N = 1 the result has the same triples as the paper's raw file. The paper's file adds 23 statements to the
generator's output (16 rdfs:subClassOf, 4 rdf:type, 2 rdfs:label, 1 rdfs:domain, among them the T20CricketFan
axiom) and removes none.

Usage: python derive_scaled_owl2bench.py RAW1 GEN1 GENN OUTPUT
"""
import collections, json, sys
import rdflib
from rdflib.namespace import XSD

def parse(path):
    g = rdflib.Graph(); g.parse(path, format="xml"); return g

def plain(t):
    return tuple(rdflib.Literal(str(x)) if isinstance(x, rdflib.Literal) and x.datatype == XSD.string else x for x in t)

def split(g):
    ground, blank = set(), 0
    for t in g:
        if any(isinstance(x, rdflib.BNode) for x in t): blank += 1
        else: ground.add(plain(t))
    return ground, blank

raw1, gen1, genn = parse(sys.argv[1]), parse(sys.argv[2]), parse(sys.argv[3])
r1, rb = split(raw1); g1, g1b = split(gen1); gn, gnb = split(genn)
assert g1b == gnb, (g1b, gnb)
edits_removed, edits_added = g1 - r1, r1 - g1
print("paper's edits of gen(1): removed", len(edits_removed), "added", len(edits_added))
print("  removed", collections.Counter(str(p) for _, p, _ in edits_removed).most_common(8))
print("  added", collections.Counter(str(p) for _, p, _ in edits_added).most_common(8))
out = rdflib.Graph()
for t in raw1: out.add(t)
for t in gn - g1: out.add(t)
for t in g1 - gn: out.remove(t)
out.serialize(sys.argv[4], format="xml")
print(json.dumps({"output": sys.argv[4], "statements": len(out), "added": len(gn - g1), "removed": len(g1 - gn)}))
