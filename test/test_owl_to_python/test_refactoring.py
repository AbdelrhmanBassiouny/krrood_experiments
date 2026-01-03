import pytest
import rdflib
from rdflib.namespace import XSD
from krrood_experiments.owl_to_python import (
    ClassInfo,
    PropertyInfo,
    InferenceEngine,
    NamingRegistry,
    PropertyType,
    SubsumptionType,
    RoleTakerInfo,
)


def test_topological_order_dataclasses():
    items = {
        "A": ClassInfo(name="A", uri="", base_classes=["B"]),
        "B": ClassInfo(name="B", uri="", base_classes=[]),
        "C": ClassInfo(name="C", uri="", base_classes=["A", "B"]),
    }
    order = InferenceEngine.topological_order(items, "base_classes")
    assert order == ["B", "A", "C"]


def test_ancestor_computation():
    engine = InferenceEngine(rdflib.Graph())
    classes = {
        "Child": ClassInfo(name="Child", uri="", base_classes=["Parent"]),
        "Parent": ClassInfo(name="Parent", uri="", base_classes=["GrandParent"]),
        "GrandParent": ClassInfo(name="GrandParent", uri="", base_classes=[]),
    }
    engine.compute_ancestors(classes)
    assert classes["Child"].all_base_classes == ["GrandParent", "Parent"]
    assert classes["Parent"].all_base_classes == ["GrandParent"]


def test_naming_registry():
    assert NamingRegistry.to_snake_case("WorksFor") == "works_for"
    assert NamingRegistry.to_pascal_case("works_for") == "WorksFor"
    assert (
        NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org#MyClass"))
        == "MyClass"
    )


def test_property_type_enum():
    p = PropertyInfo(name="test", uri="", type=PropertyType.OBJECT_PROPERTY)
    assert p.type == "ObjectProperty"
    assert p.type == PropertyType.OBJECT_PROPERTY


def test_compute_type_hints_object_property_simplification():
    engine = InferenceEngine(rdflib.Graph())
    # A is subtype of B, so A is more specific. Simplified ranges should only keep B.
    classes = {
        "A": ClassInfo(name="A", uri="", all_base_classes=["B"]),
        "B": ClassInfo(name="B", uri="", all_base_classes=[]),
    }
    properties = {
        "p": PropertyInfo(
            name="p", uri="", type=PropertyType.OBJECT_PROPERTY, ranges=["A", "B"]
        )
    }
    engine.compute_type_hints(classes, properties)
    assert properties["p"].object_range_hint == "B"


def test_compute_type_hints_data_property_xsd():
    engine = InferenceEngine(rdflib.Graph())
    properties = {
        "age": PropertyInfo(
            name="age",
            uri="",
            type=PropertyType.DATA_PROPERTY,
            range_uris=[XSD.integer],
        )
    }
    engine.compute_type_hints({}, properties)
    assert properties["age"].data_type_hint_inner == "int"


def test_find_implicit_subtypes_basic():
    engine = InferenceEngine(rdflib.Graph())
    # Parent and Child have same properties, Child should become subtype of Parent
    classes = {
        "Parent": ClassInfo(name="Parent", uri="", declared_properties=["p"]),
        "Child": ClassInfo(
            name="Child", uri="", declared_properties=["p"], base_classes=["Ontology"]
        ),
    }
    properties = {
        "p": PropertyInfo(
            name="p",
            uri="",
            type=PropertyType.OBJECT_PROPERTY,
            object_range_hint="Thing",
        )
    }
    ancestors_map = {"Thing": set()}
    engine.find_implicit_subtypes(
        classes, properties, ancestors_map, "Ontology", "Role"
    )

    assert "Parent" in classes["Child"].base_classes
    assert "Ontology" not in classes["Child"].base_classes
    assert "p" not in classes["Child"].declared_properties


def test_find_implicit_subtypes_role():
    engine = InferenceEngine(rdflib.Graph())
    # Child has subset of Parent properties, Child should become a Role of Parent
    classes = {
        "Parent": ClassInfo(name="Parent", uri="", declared_properties=["p1", "p2"]),
        "Child": ClassInfo(
            name="Child", uri="", declared_properties=["p1"], base_classes=["Ontology"]
        ),
    }
    properties = {
        "p1": PropertyInfo(
            name="p1",
            uri="",
            type=PropertyType.OBJECT_PROPERTY,
            object_range_hint="Thing",
        ),
        "p2": PropertyInfo(
            name="p2",
            uri="",
            type=PropertyType.OBJECT_PROPERTY,
            object_range_hint="Thing",
        ),
    }
    ancestors_map = {"Thing": set()}
    engine.find_implicit_subtypes(
        classes, properties, ancestors_map, "Ontology", "Role"
    )

    assert classes["Child"].role_taker.class_name == "Parent"
    assert "Role" in classes["Child"].base_classes


def test_class_info_dataclass():
    ci = ClassInfo(
        name="TestClass",
        uri="http://test.org#TestClass",
        label="Test Label",
        comment="Test Comment",
    )
    assert ci.name == "TestClass"
    assert ci.uri == "http://test.org#TestClass"
    assert ci.label == "Test Label"
    assert ci.comment == "Test Comment"
    assert ci.superclasses == []
    assert ci.base_classes == []


def test_property_info_dataclass():
    pi = PropertyInfo(
        name="testProp", uri="http://test.org#testProp", type=PropertyType.DATA_PROPERTY
    )
    assert pi.name == "testProp"
    assert pi.type == PropertyType.DATA_PROPERTY
    assert pi.domains == []
    assert pi.ranges == []


def test_propagate_types():
    engine = InferenceEngine(rdflib.Graph())
    dom_map = {"p1": {"D1"}, "p2": {"D2"}, "p1_inv": set()}
    rng_map = {"p1": {"R1"}, "p2": set(), "p1_inv": set()}
    rng_uri_map = {"p1": set(), "p2": set(), "p1_inv": set()}
    super_map = {"p1": ["p2"], "p2": [], "p1_inv": []}
    inverse_pairs = [("p1", "p1_inv"), ("p1_inv", "p1")]

    engine._propagate_types(dom_map, rng_map, rng_uri_map, super_map, inverse_pairs)

    assert "D1" in rng_map["p1_inv"]
    assert "R1" in dom_map["p1_inv"]


def test_compute_closure():
    from krrood_experiments.owl_to_python import CodeGenerator

    cg = CodeGenerator(rdflib.Graph(), {}, {}, "Ontology", {})
    items = {"A": {"supers": ["B"]}, "B": {"supers": ["C"]}, "C": {"supers": []}}
    closure = cg._compute_closure(["A"], items, "supers")
    assert closure == ["A", "B", "C"]
