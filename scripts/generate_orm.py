import os
from dataclasses import is_dataclass

from krrood.class_diagrams.class_diagram import ClassDiagram
from krrood.ormatic.dao import AlternativeMapping
from krrood.ormatic.ormatic import ORMatic
from krrood.ormatic.utils import classes_of_module
from krrood.utils import recursive_subclasses

import owl2bench.model.base
import owl2bench.model.college_disciplines
import owl2bench.model.interests

import owl2bench.model.programs
import owl2bench.model.publications
import owl2bench.model.roles
import owl2bench.model.organizations


def generate_orm() -> None:
    all_classes = classes_of_module(owl2bench.model.base)
    all_classes += classes_of_module(owl2bench.model.college_disciplines)
    all_classes += classes_of_module(owl2bench.model.interests)
    all_classes += classes_of_module(owl2bench.model.organizations)
    all_classes += classes_of_module(owl2bench.model.programs)
    all_classes += classes_of_module(owl2bench.model.publications)
    all_classes += classes_of_module(owl2bench.model.roles)

    # only keep dataclasses
    all_classes = {c for c in all_classes if is_dataclass(c)}

    class_diagram = ClassDiagram(
        list(sorted(all_classes, key=lambda c: c.__name__, reverse=True))
    )

    instance = ORMatic(
        class_dependency_graph=class_diagram,
        alternative_mappings=recursive_subclasses(AlternativeMapping),
    )

    instance.make_all_tables()

    file_path = os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "owl2bench",
                "orm",
                "ormatic_interface.py",
            )
        )
    )

    with open(file_path, "w") as f:
        instance.to_sqlalchemy_file(f)


if __name__ == "__main__":
    generate_orm()
