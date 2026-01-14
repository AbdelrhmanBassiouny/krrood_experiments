import pytest
from dataclasses import dataclass, is_dataclass
from typing import Optional

from krrood.entity_query_language.predicate import Symbol
from rdflib import URIRef, Literal, RDF


import importlib
from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor


import krrood_experiments.owl_instances_loader

importlib.reload(krrood_experiments.owl_instances_loader)

from krrood_experiments.owl_instances_loader import (
    ModelMetadata,
    OwlLoader,
    OwlInstancesRegistry,
    local_name,
)
from krrood.entity_query_language.symbol_graph import SymbolGraph


@dataclass(eq=False)
class Name(Symbol):
    value: Optional[str] = None


@dataclass(eq=False)
class Age(Symbol):
    value: Optional[int] = None


@dataclass(eq=False)
class MockPerson(Symbol):
    uri: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    name_attr: Optional[Name] = None
    age_attr: Optional[Age] = None


class NameAttr(PropertyDescriptor):
    pass


class AgeAttr(PropertyDescriptor):
    pass


MockPerson.name_attr = NameAttr(domain=MockPerson, field_name="name_attr")
MockPerson.age_attr = AgeAttr(domain=MockPerson, field_name="age_attr")


class MockModule:
    Name = Name
    Age = Age
    MockPerson = MockPerson
    NameAttr = NameAttr
    AgeAttr = AgeAttr


def test_model_metadata_collection():
    module = MockModule
    metadata = ModelMetadata(module, SymbolGraph())

    assert metadata.class_by_name["MockPerson"] == MockPerson
    assert metadata.descriptor_by_name["NameAttr"] == NameAttr
    assert metadata.descriptor_by_name["AgeAttr"] == AgeAttr

    assert (
        metadata.get_python_class(URIRef("http://example.org#MockPerson")) == MockPerson
    )
    assert metadata.get_descriptor_base("name_attr") == NameAttr


def test_owl_loader_basic():
    module = MockModule

    SymbolGraph().clear()
    symbol_graph = SymbolGraph()
    registry = OwlInstancesRegistry()

    # Create a small RDF graph in memory
    import rdflib

    g = rdflib.Graph()
    person_uri = URIRef("http://example.org/person1")
    alice_uri = URIRef("http://example.org#Alice")
    age_uri = URIRef("http://example.org#age")
    g.add((person_uri, RDF.type, URIRef("http://example.org#MockPerson")))
    g.add((alice_uri, RDF.type, URIRef("http://example.org#Name")))
    g.add((age_uri, RDF.type, URIRef("http://example.org#Age")))

    # Add values for the intermediate nodes
    g.add((alice_uri, URIRef("http://example.org#value"), Literal("Alice")))
    g.add((age_uri, URIRef("http://example.org#value"), Literal(30)))

    # Link person to the intermediate nodes
    g.add((person_uri, URIRef("http://example.org#name_attr"), alice_uri))
    g.add((person_uri, URIRef("http://example.org#age_attr"), age_uri))

    # We need to save this to a file because OwlLoader expects a path
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as f:
        g.serialize(destination=f.name, format="xml")
        temp_path = f.name

    try:
        loader = OwlLoader(temp_path, module, symbol_graph, registry)
        loader.load()

        instances = registry.resolve(person_uri)
        assert instances is not None
        person = instances[0]
        assert isinstance(person, MockPerson)

        # Accessing via descriptors
        assert person.name_attr is not None
        assert person.name_attr.value == "Alice"
        assert person.age_attr is not None
        assert person.age_attr.value == 30
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])
