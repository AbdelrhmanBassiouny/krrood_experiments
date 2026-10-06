"""Generate the ORMatic DAOs for owl2bench_like.py the way cram2 main's test conftest does."""

import os
from types import FunctionType
from dataclasses import is_dataclass

from krrood.class_diagrams.class_diagram import ClassDiagram
from krrood.ormatic.data_access_objects.alternative_mappings import *  # noqa: F401,F403
from krrood.ormatic.helper import OrmaticInterfaceInformation
from krrood.ormatic.ormatic import ORMatic
from krrood.ormatic.utils import classes_of_module
from krrood.patterns.role import Role
from krrood.symbol_graph.symbol_graph import Symbol, SymbolGraph
from krrood.utils import recursive_subclasses

import owl2bench_like


def main():
    SymbolGraph.clear()
    classes = set(classes_of_module(owl2bench_like)) | {Symbol, Role}
    classes |= {m.original_class() for m in recursive_subclasses(AlternativeMapping)}
    classes = {c for c in classes if is_dataclass(c) and not issubclass(c, AlternativeMapping)}
    classes |= {FunctionType}
    class_diagram = ClassDiagram(sorted(classes, key=lambda c: c.__name__, reverse=True))
    instance = ORMatic(
        class_dependency_graph=class_diagram,
        interface_information=OrmaticInterfaceInformation(
            alternative_mappings=recursive_subclasses(AlternativeMapping),
        ),
    )
    instance.make_all_tables()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ormatic_interface.py")
    with open(path, "w") as f:
        instance.to_sqlalchemy_file(f)
    print("wrote", path)


if __name__ == "__main__":
    main()
