import pytest
import rdflib
from krrood_experiments.owl_to_python import (
    ClassInfo, PropertyInfo, InferenceEngine, NamingRegistry
)

def test_topological_order_dataclasses():
    items = {
        "A": ClassInfo(name="A", uri="", base_classes=["B"]),
        "B": ClassInfo(name="B", uri="", base_classes=[]),
        "C": ClassInfo(name="C", uri="", base_classes=["A", "B"])
    }
    order = InferenceEngine.topological_order(items, "base_classes")
    assert order == ["B", "A", "C"]

def test_ancestor_computation():
    engine = InferenceEngine(rdflib.Graph())
    classes = {
        "Child": ClassInfo(name="Child", uri="", base_classes=["Parent"]),
        "Parent": ClassInfo(name="Parent", uri="", base_classes=["GrandParent"]),
        "GrandParent": ClassInfo(name="GrandParent", uri="", base_classes=[])
    }
    engine.compute_ancestors(classes)
    assert classes["Child"].all_base_classes == ["GrandParent", "Parent"]
    assert classes["Parent"].all_base_classes == ["GrandParent"]

def test_naming_registry():
    assert NamingRegistry.to_snake_case("WorksFor") == "works_for"
    assert NamingRegistry.to_pascal_case("works_for") == "WorksFor"
    assert NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org#MyClass")) == "MyClass"
