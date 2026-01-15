import rdflib
from rdflib.namespace import XSD
from krrood_experiments.owl2bench.ontomatic.owl_to_python import (
    ClassInfo,
    PropertyInfo,
    InferenceEngine,
    NamingRegistry,
    PropertyType,
    OntologyInfo,
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
    classes = {
        "Child": ClassInfo(name="Child", uri="", base_classes=["Parent"]),
        "Parent": ClassInfo(name="Parent", uri="", base_classes=["GrandParent"]),
        "GrandParent": ClassInfo(name="GrandParent", uri="", base_classes=[]),
    }
    onto = OntologyInfo(rdflib.Graph(), classes=classes)
    engine = InferenceEngine(onto)
    engine.compute_ancestors()
    assert onto.classes["Child"].all_base_classes == ["GrandParent", "Parent"]
    assert onto.classes["Parent"].all_base_classes == ["GrandParent"]


def test_naming_registry():
    assert NamingRegistry.to_snake_case("WorksFor") == "works_for"
    assert NamingRegistry.to_pascal_case("works_for") == "WorksFor"
    assert (
        NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org#MyClass"))
        == "MyClass"
    )


def test_property_type_enum():
    p = PropertyInfo(name="ontomatic_tests", uri="", type=PropertyType.OBJECT_PROPERTY)
    assert p.type == "ObjectProperty"
    assert p.type == PropertyType.OBJECT_PROPERTY


def test_compute_type_hints_object_property_simplification():
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
    onto = OntologyInfo(rdflib.Graph(), classes=classes, original_properties=properties)
    engine = InferenceEngine(onto)
    engine.compute_type_hints()
    assert onto.properties["p"].object_range_hint == "B"


def test_compute_type_hints_data_property_xsd():
    properties = {
        "age": PropertyInfo(
            name="age",
            uri="",
            type=PropertyType.DATA_PROPERTY,
            range_uris=[XSD.integer],
        )
    }
    onto = OntologyInfo(rdflib.Graph(), original_properties=properties)
    engine = InferenceEngine(onto)
    engine.compute_type_hints()
    assert onto.properties["age"].data_type_hint_inner == "int"


def test_find_implicit_subtypes_basic():
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
    onto = OntologyInfo(rdflib.Graph(), classes=classes, original_properties=properties)
    engine = InferenceEngine(onto)
    engine.find_implicit_subtypes()
    assert "Parent" in onto.classes["Child"].base_classes
    assert "Ontology" not in onto.classes["Child"].base_classes
    assert "p" not in onto.classes["Child"].declared_properties


def test_find_implicit_subtypes_role():
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
    onto = OntologyInfo(rdflib.Graph(), classes=classes, original_properties=properties)
    engine = InferenceEngine(onto)
    engine.find_implicit_subtypes()

    assert onto.classes["Child"].role_taker.class_name == "Parent"
    assert "Role" in onto.classes["Child"].base_classes


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
    properties = {
        "p1": PropertyInfo(
            name="p1",
            uri="",
            type=PropertyType.OBJECT_PROPERTY,
            domains=["D1"],
            ranges=["R1"],
            superproperties=["p2"],
            inverses=["p1_inv"],
        ),
        "p2": PropertyInfo(
            name="p2", uri="", type=PropertyType.OBJECT_PROPERTY, domains=["D2"]
        ),
        "p1_inv": PropertyInfo(
            name="p1_inv", uri="", type=PropertyType.OBJECT_PROPERTY
        ),
    }
    onto = OntologyInfo(rdflib.Graph(), original_properties=properties)
    engine = InferenceEngine(onto)
    engine._propagate_types()
    assert "D1" in engine.property_maps.rng_map["p1_inv"]
    assert "R1" in engine.property_maps.dom_map["p1_inv"]


def test_compute_closure():
    from krrood_experiments.owl2bench.ontomatic.owl_to_python import CodeGenerator

    onto = OntologyInfo(rdflib.Graph())
    cg = CodeGenerator(onto)
    items = {"A": {"supers": ["B"]}, "B": {"supers": ["C"]}, "C": {"supers": []}}
    closure = cg._compute_closure(["A"], items, "supers")
    assert closure == ["A", "B", "C"]
