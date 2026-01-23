import numpy as np
from krrood.class_diagrams import ClassDiagram
from krrood.class_diagrams.utils import classes_of_module
from krrood.entity_query_language.symbol_graph import SymbolGraph
from krrood.utils import recursive_subclasses
from random_events.interval import closed, SimpleInterval, Bound
from random_events.product_algebra import SimpleEvent

from krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates_base import *
import krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates
from random_events.variable import Symbolic, Set, Integer

classes = classes_of_module(
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates
) + [OWL2BenchThing, Symbol]

class_diagram = ClassDiagram(classes)
symbol_graph = SymbolGraph(class_diagram)

# get all leaves


inheritance_graph = class_diagram.inheritance_subgraph_without_unreachable_nodes
symbol_graph.to_dot(graph=inheritance_graph, filepath="inheritance_graph.svg")

leaves = [
    node.clazz
    for node in inheritance_graph.nodes()
    if inheritance_graph.out_degree(node.index) == 0
]

class_variable = Symbolic("type", Set.from_iterable(leaves))

possible_sets = {}
for node in inheritance_graph.nodes():
    current_possible_sets = []
    for leaf in leaves:
        if issubclass(leaf, node.clazz):
            current_possible_sets.append(leaf)
    if len(current_possible_sets) > 0:
        possible_sets[node.clazz] = class_variable.make_value(current_possible_sets)
# print(*[f"{k.__name__} = {v}" for k, v in possible_sets.items()], sep="\n")


college_discipline = possible_sets[
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.CollegeDiscipline
]
student = possible_sets[
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Student
]
non_science = (
    ~possible_sets[
        krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Science
    ]
    & college_discipline
)
engineering = possible_sets[
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Engineering
]
science = possible_sets[
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Science
]
leisure_student = possible_sets[
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.LeisureStudent
]
print(
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.LeisureStudent.axiom(
        None
    )
)

# IsSubClassOrRole(variable_from(candidate_var.types), Student) >= 1
#
exists = Integer("exists")
types_with_student = [
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Lecturer,
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.UGStudent,
]
types_without_student = [
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Lecturer,
    krrood_experiments.owl2bench.ontomatic.owl2bench_with_predicates.Professor,
]

candidate_var_types = possible_sets[types_without_student[0]]
for type_ in types_without_student[1:]:
    candidate_var_types |= possible_sets[type_]
candidate_var_types &= student

print(not candidate_var_types.is_empty())

print(
    any(
        not (possible_sets[type_] & student).is_empty()
        for type_ in types_without_student
    )
)

print(
    all(
        not (possible_sets[type_] & student).is_empty()
        for type_ in types_without_student
    )
)

course_length = Integer("course_length")
course_length_restriction = SimpleInterval(
    lower=-np.inf, upper=1, left=Bound.OPEN, right=Bound.CLOSED
)
