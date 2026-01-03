import rdflib
import pytest
from krrood_experiments.owl_to_python import NamingRegistry

def test_uri_to_python_name():
    # URIRef with fragment
    assert NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org#MyClass")) == "MyClass"
    # URIRef with slash
    assert NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org/myProperty")) == "myProperty"
    # URIRef with special characters
    assert NamingRegistry.uri_to_python_name(rdflib.URIRef("http://example.org#my-class")) == "my_class"
    # Non-URIRef
    assert NamingRegistry.uri_to_python_name("JustAString") == "JustAString"

def test_to_snake_case():
    assert NamingRegistry.to_snake_case("worksFor") == "works_for"
    assert NamingRegistry.to_snake_case("WorksFor") == "works_for"
    assert NamingRegistry.to_snake_case("already_snake") == "already_snake"
    assert NamingRegistry.to_snake_case("CamelCaseWithNumbers123") == "camel_case_with_numbers123"

def test_to_pascal_case():
    assert NamingRegistry.to_pascal_case("worksFor") == "WorksFor"
    assert NamingRegistry.to_pascal_case("works_for") == "WorksFor"
    assert NamingRegistry.to_pascal_case("WorksFor") == "WorksFor"
    assert NamingRegistry.to_pascal_case("some-dash-name") == "SomeDashName"
