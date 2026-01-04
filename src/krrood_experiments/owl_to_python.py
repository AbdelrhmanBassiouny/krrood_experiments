"""
This module provides functionality to convert OWL ontologies into Python source code.
It includes classes for extracting information from RDF graphs, performing inference,
and generating Python code using Jinja2 templates.
"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import cached_property
from typing import Dict, List, Optional, Any, Set, ClassVar

import rdflib
from jinja2 import Environment, FileSystemLoader
from jinja2.ext import loopcontrols
from krrood import logger
from rdflib.namespace import RDF, RDFS, OWL, XSD
from sqlalchemy.util import OrderedSet
from typing_extensions import Tuple


class SubsumptionType(Enum):
    SUBTYPE = "subtype"
    """
    It is a subtype of the given class (e.g. Math is a subtype of Course). This is the equivalent to OOP 
    inheritance..
    """
    ROLE = "role"
    """
    It is a role that a persistent identifier can take on in a certain context 
    (e.g. Student is a role that a Person can take on in the context of taking a course).
    Thi is the equivalent to OOP composition.
    """


class PropertyType(str, Enum):
    """Enumeration of OWL property types."""

    OBJECT_PROPERTY = "ObjectProperty"
    DATA_PROPERTY = "DataProperty"


@dataclass
class RoleTakerInfo:
    """
    Information about a class that acts as a role taker.
    Used when a class is determined to be a 'role' of another class.
    """

    class_name: str
    field_name: str


@dataclass
class ClassInfo:
    """
    Maintains all metadata, inheritance, and property associations for an OWL class.
    Used during the code generation process to represent a Python class.
    """

    name: str
    uri: str
    superclasses: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    all_base_classes: List[str] = field(default_factory=list)
    all_base_classes_including_role_takers: List[str] = field(default_factory=list)
    base_classes_for_topological_sort: List[str] = field(default_factory=list)
    label: Optional[str] = None
    comment: Optional[str] = None
    add_role_taker: bool = True
    role_taker: Optional[RoleTakerInfo] = None
    declared_properties: List[str] = field(default_factory=list)


@dataclass
class PropertyInfo:
    """
    Maintains metadata, domains, ranges, and inheritance for an OWL property.
    Used during the code generation process to represent a Python property or descriptor.
    """

    name: str
    uri: str
    type: PropertyType
    domains: List[str] = field(default_factory=list)
    ranges: List[str] = field(default_factory=list)
    range_uris: List[Any] = field(default_factory=list)
    label: Optional[str] = None
    comment: Optional[str] = None
    field_name: str = ""
    descriptor_name: str = ""
    equivalent_properties: List[str] = field(default_factory=list)
    superproperties: List[str] = field(default_factory=list)
    all_superproperties: List[str] = field(default_factory=list)
    inverses: List[str] = field(default_factory=list)
    inverse_of: Optional[str] = None
    inverse_target_is_prior: bool = False
    is_transitive: bool = False
    is_specialized: bool = False
    declared_domains: List[str] = field(default_factory=list)
    _overrides_for: List[str] = field(default_factory=list)
    _predefined_data_type: bool = False
    data_type_hint_inner: Optional[str] = None
    object_range_hint: Optional[str] = None
    base_descriptors: List[str] = field(default_factory=list)
    equivalent_properties_descriptor_names: List[str] = field(default_factory=list)


@dataclass
class OntologyInfo:
    """Information about the ontology."""

    graph: rdflib.Graph
    classes: Dict[str, ClassInfo] = field(default_factory=dict)
    original_properties: Dict[str, PropertyInfo] = field(default_factory=dict)
    predefined_data_types: Optional[Dict[str, Dict[str, str]]] = None
    ontology_label: str = "Ontology"
    role_cls_name: str = "Role"
    _properties: Optional[Dict[str, PropertyInfo]] = None
    property_restrictions: Dict[str, Dict[str, set]] = field(default_factory=dict)

    @property
    def properties(self):
        if not self._properties:
            self._properties = {
                n: deepcopy(info) for n, info in self.original_properties.items()
            }
        return self._properties

    @cached_property
    def base_cls_name(self):
        base_cls_name = NamingRegistry.to_pascal_case(
            re.sub(r"\W+", " ", self.ontology_label).strip()
        )
        if not base_cls_name.endswith("Ontology"):
            base_cls_name += "Ontology"
        return base_cls_name

    @cached_property
    def class_ancestors(self) -> Dict[str, Set[str]]:
        """
        The class ancestors map as a dictionary mapping class names to their ancestors.
        """
        return {name: set(info.all_base_classes) for name, info in self.classes.items()}


class NamingRegistry:
    """Registry for converting OWL URIs and names to Python-compatible identifiers."""

    @staticmethod
    def uri_to_python_name(uri: Any) -> str:
        """Convert URI to valid Python identifier"""
        if isinstance(uri, rdflib.URIRef):
            # Extract local name from URI
            uri_str = str(uri)
            if "#" in uri_str:
                local_name = uri_str.split("#")[-1]
            else:
                local_name = uri_str.split("/")[-1]

            # Convert to PascalCase for classes, camelCase for properties
            local_name = re.sub(r"[^a-zA-Z0-9_]", "_", local_name)
            return local_name
        return str(uri)

    @staticmethod
    def to_snake_case(name: str) -> str:
        """Convert a name like 'worksFor' or 'WorksFor' to 'works_for'"""
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()

    @staticmethod
    def to_pascal_case(name: str) -> str:
        """Convert a name like 'worksFor' or 'works_for' to 'WorksFor'"""
        # If it contains underscores or hyphens, split and capitalize parts
        parts = re.split(r"[_\-\s]+", name)
        if len(parts) > 1:
            return "".join(p.capitalize() for p in parts if p)
        # Otherwise just capitalize first char
        return name[:1].upper() + name[1:]


class MetadataExtractor:
    """Helper for extracting metadata (labels, comments) from an RDF graph."""

    def __init__(self, graph: rdflib.Graph):
        """
        Initialize the metadata extractor.
        :param graph: The rdflib graph to extract metadata from.
        """
        self.graph = graph

    def get_label(self, uri: Any) -> Optional[str]:
        """Get rdfs:label for a URI"""
        for label in self.graph.objects(uri, RDFS.label):
            return str(label)
        return None

    def get_comment(self, uri: Any) -> Optional[str]:
        """Get rdfs:comment for a URI"""
        for comment in self.graph.objects(uri, RDFS.comment):
            return str(comment)
        return None


class ClassExtractor:
    """Extractor for OWL Class information from an RDF graph."""

    def __init__(self, graph: rdflib.Graph, metadata_extractor: MetadataExtractor):
        """
        Initialize the class extractor.
        :param graph: The rdflib graph.
        :param metadata_extractor: Extractor for labels and comments.
        """
        self.graph = graph
        self.metadata_extractor = metadata_extractor

    def extract_info(self, class_uri: Any) -> ClassInfo:
        """Extract information about a class"""
        class_name = NamingRegistry.uri_to_python_name(class_uri)

        # Get superclasses from explicit rdfs:subClassOf
        superclasses: List[str] = []
        for superclass in self.graph.objects(class_uri, RDFS.subClassOf):
            if not isinstance(superclass, rdflib.URIRef):
                continue
            superclasses.append(NamingRegistry.uri_to_python_name(superclass))

        # De-duplicate while preserving order
        seen = set()
        unique_superclasses: List[str] = []
        for sc in superclasses:
            if sc not in seen:
                unique_superclasses.append(sc)
                seen.add(sc)

        # Get label
        label = self.metadata_extractor.get_label(class_uri)

        return ClassInfo(
            name=class_name,
            uri=str(class_uri),
            superclasses=unique_superclasses or ["Symbol"],
            label=label,
            comment=self.metadata_extractor.get_comment(class_uri),
            add_role_taker=True,
        )


class PropertyExtractor:
    """Extractor for OWL Property information from an RDF graph."""

    def __init__(self, graph: rdflib.Graph, metadata_extractor: MetadataExtractor):
        """
        Initialize the property extractor.
        :param graph: The rdflib graph.
        :param metadata_extractor: Extractor for labels and comments.
        """
        self.graph = graph
        self.metadata_extractor = metadata_extractor

    def extract_info(self, property_uri: Any) -> PropertyInfo:
        """Extract information about a property"""
        prop_local = NamingRegistry.uri_to_python_name(property_uri)

        # Get domain and range
        domains: List[str] = []
        ranges: List[str] = []
        superproperties: List[str] = []
        inverses: List[str] = []
        equivalent_properties: List[str] = []

        for domain in self.graph.objects(property_uri, RDFS.domain):
            domains.append(NamingRegistry.uri_to_python_name(domain))

        range_uris: List[rdflib.term.Identifier] = []
        for range_val in self.graph.objects(property_uri, RDFS.range):
            ranges.append(NamingRegistry.uri_to_python_name(range_val))
            range_uris.append(range_val)

        # Inheritance between properties
        for super_prop in self.graph.objects(property_uri, RDFS.subPropertyOf):
            if isinstance(super_prop, rdflib.URIRef):
                superproperties.append(NamingRegistry.uri_to_python_name(super_prop))

        # Inverses
        for inv in self.graph.objects(property_uri, OWL.inverseOf):
            if isinstance(inv, rdflib.URIRef):
                inverses.append(NamingRegistry.uri_to_python_name(inv))
        # Also collect when current property is the object of inverseOf
        for inv_subj in self.graph.subjects(OWL.inverseOf, property_uri):
            if isinstance(inv_subj, rdflib.URIRef):
                inverses.append(NamingRegistry.uri_to_python_name(inv_subj))

        # Equivalent properties
        for eq_prop in self.graph.objects(property_uri, OWL.equivalentProperty):
            if isinstance(eq_prop, rdflib.URIRef):
                equivalent_properties.append(NamingRegistry.uri_to_python_name(eq_prop))
        for eq_prop_subj in self.graph.subjects(OWL.equivalentProperty, property_uri):
            if isinstance(eq_prop_subj, rdflib.URIRef):
                equivalent_properties.append(
                    NamingRegistry.uri_to_python_name(eq_prop_subj)
                )

        # Determine property type
        prop_type = PropertyType.OBJECT_PROPERTY
        is_transitive = False
        for prop_type_uri in self.graph.objects(property_uri, RDF.type):
            if prop_type_uri == OWL.DatatypeProperty:
                prop_type = PropertyType.DATA_PROPERTY
            if prop_type_uri == OWL.TransitiveProperty:
                is_transitive = True

        # Choose a single inverse if any (stable order)
        inverse_of = None
        if inverses:
            inverse_of = sorted(set(inverses))[0]

        return PropertyInfo(
            name=prop_local,
            uri=str(property_uri),
            type=prop_type,
            domains=domains,
            ranges=ranges,
            range_uris=range_uris,
            equivalent_properties=equivalent_properties,
            label=self.metadata_extractor.get_label(property_uri),
            comment=self.metadata_extractor.get_comment(property_uri),
            field_name=NamingRegistry.to_snake_case(prop_local),
            descriptor_name=NamingRegistry.to_pascal_case(prop_local),
            superproperties=superproperties,
            inverses=sorted(set(inverses)),
            inverse_of=inverse_of,
            is_transitive=is_transitive,
            is_specialized=False,
        )


@dataclass
class PropertyMaps:
    """
    Dataclass for storing property inference maps for domain, range, superclasses, and inverse property pairs.
    """

    dom_map: Dict[str, Set[str]] = field(default_factory=dict)
    """
    Map of property names to sets of domain class names.
    """
    declared_dom_map: Dict[str, Set[str]] = field(default_factory=dict)
    """
    Map of property names to sets of declared domain class names. These are the classes where the property is declared.
    """
    rng_map: Dict[str, Set[str]] = field(default_factory=dict)
    """
    Map of property names to sets of range class names.
    """
    rng_uri_map: Dict[str, Set[rdflib.term.URIRef]] = field(default_factory=dict)
    """
    Map of property names to sets of range URIs.
    """
    super_map: Dict[str, List[str]] = field(default_factory=dict)
    """
    Map of property names to lists of superclass names.
    """
    inverse_pairs: List[Tuple[str, str]] = field(default_factory=list)
    """
    List of tuples representing inverse property pairs (property_name, inverse_property_name).
    """
    equivalent_map: Dict[str, List[str]] = field(default_factory=dict)
    """
    Map of property names to lists of equivalent property names.
    """
    properties: Dict[str, PropertyInfo] = field(default_factory=dict)
    """
    Map of property names to PropertyInfo objects.
    """

    @classmethod
    def from_properties(cls, properties: Dict[str, PropertyInfo]) -> PropertyMaps:
        """
        Create a PropertyMaps object from a dictionary of PropertyInfo objects.

        :param properties: A dictionary of PropertyInfo objects.
        :return: A PropertyMaps object.
        """
        dom_map = {n: set(p.domains) for n, p in properties.items()}
        declared_dom_map = {n: set(p.domains) for n, p in properties.items()}
        rng_map = {n: set(p.ranges) for n, p in properties.items()}
        rng_uri_map = {n: set(p.range_uris) for n, p in properties.items()}
        super_map = {n: list(p.superproperties) for n, p in properties.items()}
        inverse_pairs = [
            (n, inv)
            for n, p in properties.items()
            for inv in p.inverses
            if inv in properties
        ]
        equivalent_map = {
            n: list(p.equivalent_properties) for n, p in properties.items()
        }
        return cls(
            dom_map,
            declared_dom_map,
            rng_map,
            rng_uri_map,
            super_map,
            inverse_pairs,
            equivalent_map,
            properties,
        )


@dataclass
class InferenceEngine:
    """Engine for performing ontological inference and computing class/property relationships."""

    onto: OntologyInfo
    property_maps: PropertyMaps = field(init=False)
    XSD_TO_PYTHON_TYPES: ClassVar[Dict[rdflib.term.URIRef, str]] = {
        XSD.string: "str",
        XSD.normalizedString: "str",
        XSD.token: "str",
        XSD.language: "str",
        XSD.boolean: "bool",
        XSD.decimal: "float",
        XSD.float: "float",
        XSD.double: "float",
        XSD.integer: "int",
        XSD.nonPositiveInteger: "int",
        XSD.negativeInteger: "int",
        XSD.long: "int",
        XSD.int: "int",
        XSD.short: "int",
        XSD.byte: "int",
        XSD.nonNegativeInteger: "int",
        XSD.unsignedLong: "int",
        XSD.unsignedInt: "int",
        XSD.unsignedShort: "int",
        XSD.unsignedByte: "int",
        XSD.positiveInteger: "int",
        XSD.date: "str",
        XSD.dateTime: "str",
        XSD.time: "str",
        XSD.anyURI: "str",
    }

    def __post_init__(self):
        self.property_maps = PropertyMaps.from_properties(self.onto.properties)

    @staticmethod
    def topological_order(items: Dict[str, Any], dep_key: str) -> List[str]:
        """Return a topological order based on dependency names in dep_key; if cycles, append remaining alphabetically."""

        def get_deps(item):
            if hasattr(item, dep_key):
                return getattr(item, dep_key, [])
            return item.get(dep_key, [])

        remaining = {
            name: set(get_deps(items[name])) & set(items.keys()) for name in items
        }
        ordered: List[str] = []
        while remaining:
            ready = sorted([name for name, deps in remaining.items() if not deps])
            if not ready:
                ordered.extend(sorted(remaining.keys()))
                break
            for name in ready:
                ordered.append(name)
                del remaining[name]
            for deps in remaining.values():
                deps.difference_update(ready)
        return ordered

    def compute_ancestors(self):
        """
        Compute full ancestor sets for each class (transitive closure).
        """
        # Compute full ancestor sets for each class (transitive closure)
        name_to_bases = {
            name: set(info.base_classes) for name, info in self.onto.classes.items()
        }
        for info in self.onto.classes.values():
            ancestors = set()
            stack = list(info.base_classes)
            while stack:
                base = stack.pop()
                if base in ancestors:
                    continue
                ancestors.add(base)
                stack.extend(name_to_bases.get(base, []))
            info.all_base_classes = sorted(ancestors)

    def infer_properties(
        self,
    ):
        """
        Main entry point for property inference.
        Propagates domains, ranges, and handles restrictions and inverses.
        """
        self._infer_properties_data_from_restrictions()
        self._propagate_types()
        self._finalize_properties()
        self._create_specialized_properties()

    def _infer_properties_data_from_restrictions(self):
        """
        Walk through all classes and their restrictions in the graph and update declared_dom_map accordingly.
        """
        # Walk class restrictions
        for cls_uri in self.onto.graph.subjects(RDF.type, OWL.Class):
            if isinstance(cls_uri, rdflib.BNode):
                continue
            cls_name = NamingRegistry.uri_to_python_name(cls_uri)
            # direct subclass restrictions
            for restr in self.onto.graph.objects(cls_uri, RDFS.subClassOf):
                self._restrictions_handler(cls_name, restr)
                # If restriction mentions a property, count this class as declared domain for that property
                on_prop = self.onto.graph.value(restr, OWL.onProperty)
                if on_prop:
                    self.property_maps.declared_dom_map[
                        NamingRegistry.uri_to_python_name(on_prop)
                    ].add(cls_name)

            # restrictions inside intersectionOf
            for coll in self.onto.graph.objects(cls_uri, OWL.intersectionOf):
                node = coll
                while node and node != RDF.nil:
                    first = self.onto.graph.value(node, RDF.first)
                    self._restrictions_handler(cls_name, first)
                    on_prop = (
                        self.onto.graph.value(first, OWL.onProperty) if first else None
                    )
                    if on_prop:
                        self.property_maps.declared_dom_map[
                            NamingRegistry.uri_to_python_name(on_prop)
                        ].add(cls_name)
                    node = self.onto.graph.value(node, RDF.rest)

    def _restrictions_handler(self, for_class: str, node: rdflib.term.Node):
        """
        Handle restrictions for a given class and node in the ontology graph.

        :param for_class: The class name.
        :param node: The restriction node.
        """
        if not node:
            return
        on_prop = self.onto.graph.value(node, OWL.onProperty)
        if not on_prop:
            return
        prop_name = NamingRegistry.uri_to_python_name(on_prop)
        if prop_name in self.onto.properties:
            self.property_maps.dom_map[prop_name].add(for_class)
        some = self.onto.graph.value(node, OWL.someValuesFrom) or self.onto.graph.value(
            node, OWL.allValuesFrom
        )
        if some:
            try:
                rng_name = NamingRegistry.uri_to_python_name(some)
                if prop_name == "roleFor":
                    cls_info = self.onto.classes.get(for_class)
                    if cls_info:
                        cls_info.role_taker = RoleTakerInfo(
                            rng_name, NamingRegistry.to_snake_case(rng_name)
                        )
                    return
                self.property_maps.rng_map[prop_name].add(rng_name)
                self.property_maps.rng_uri_map[prop_name].add(some)
                self.onto.property_restrictions.setdefault(for_class, {}).setdefault(
                    prop_name, set()
                ).add(rng_name)
            except Exception as e:
                logger.warning(f"[owl_to_python] Error processing restriction: {e}")

    def _propagate_types(self):
        """
        Perform iterative propagation of domains and ranges along property hierarchy and inverses.
        """
        changed = True
        while changed:
            changed = False
            for name, supers in self.property_maps.super_map.items():
                supers_and_equivalents = set(supers).union(
                    self.property_maps.equivalent_map[name]
                )
                for sp in supers_and_equivalents:
                    if sp not in self.property_maps.dom_map:
                        continue
                    before_range_len, before_range_uri_len, before_domain_len = (
                        len(self.property_maps.rng_map[name]),
                        len(self.property_maps.rng_uri_map[name]),
                        len(self.property_maps.dom_map[name]),
                    )
                    self.property_maps.rng_map[name].update(
                        self.property_maps.rng_map[sp]
                    )
                    self.property_maps.rng_uri_map[name].update(
                        self.property_maps.rng_uri_map[sp]
                    )
                    if not before_domain_len:
                        self.property_maps.dom_map[name].update(
                            self.property_maps.dom_map[sp]
                        )
                    if (
                        len(self.property_maps.rng_map[name]) != before_range_len
                        or len(self.property_maps.rng_uri_map[name])
                        != before_range_uri_len
                        or len(self.property_maps.dom_map[name]) != before_domain_len
                    ):
                        changed = True
            for a, b in self.property_maps.inverse_pairs:
                before_da, before_ra = len(self.property_maps.dom_map[a]), len(
                    self.property_maps.rng_map[a]
                )
                before_db, before_rb = len(self.property_maps.dom_map[b]), len(
                    self.property_maps.rng_map[b]
                )
                self.property_maps.dom_map[a].update(self.property_maps.rng_map[b])
                self.property_maps.rng_map[a].update(self.property_maps.dom_map[b])
                self.property_maps.dom_map[b].update(self.property_maps.rng_map[a])
                self.property_maps.rng_map[b].update(self.property_maps.dom_map[a])
                if (
                    len(self.property_maps.dom_map[a]) != before_da
                    or len(self.property_maps.rng_map[a]) != before_ra
                    or len(self.property_maps.dom_map[b]) != before_db
                    or len(self.property_maps.rng_map[b]) != before_rb
                ):
                    changed = True

    def _finalize_properties(self):
        """
        Update PropertyInfo objects with inferred domain and range information.
        """
        for name, info in self.onto.properties.items():
            info.domains = sorted(self.property_maps.dom_map[name])
            info.ranges = sorted(self.property_maps.rng_map[name])
            info.range_uris = list(self.property_maps.rng_uri_map[name])
            info.declared_domains = sorted(self.property_maps.declared_dom_map[name])

    def _create_specialized_properties(self):
        """
        Create specialized versions of properties based on class-level restrictions.
        Used for narrowing property ranges in specific subclasses.
        """
        specialized_props: Dict[str, PropertyInfo] = {}
        for cls_name, props in self.onto.property_restrictions.items():
            for prop_name, rng_names in props.items():
                base = self.onto.properties.get(prop_name)
                if not base or base.type != PropertyType.OBJECT_PROPERTY:
                    continue
                if rng_names.issubset(
                    set(self.onto.original_properties[prop_name].ranges)
                ):
                    continue
                if cls_name in base.declared_domains:
                    base.declared_domains.remove(cls_name)
                for rng_name in sorted(rng_names):
                    spec_key = f"{prop_name}{{{rng_name}}}"
                    if (
                        spec_key in self.onto.properties
                        or spec_key in specialized_props
                    ):
                        continue
                    specialized_props[spec_key] = PropertyInfo(
                        name=prop_name,
                        uri=base.uri,
                        type=PropertyType.OBJECT_PROPERTY,
                        domains=[cls_name],
                        ranges=[rng_name],
                        label=base.label,
                        comment=base.comment,
                        field_name=base.field_name,
                        descriptor_name=NamingRegistry.to_pascal_case(
                            base.descriptor_name or prop_name
                        ),
                        superproperties=[prop_name],
                        inverses=[],
                        inverse_of=None,
                        is_transitive=base.is_transitive,
                        declared_domains=[cls_name],
                        is_specialized=True,
                    )
        self.onto.properties.update(specialized_props)

    def apply_predefined_overrides(
        self,
    ):
        """
        Apply manual type overrides for specific class properties.
        """
        for cls_name, overrides in (self.onto.predefined_data_types or {}).items():
            if cls_name == "Thing":
                cls_name = self.onto.base_cls_name
            for field_snake, py_type in overrides.items():
                target_prop_name = next(
                    (
                        n
                        for n, p in self.onto.properties.items()
                        if p.field_name == field_snake
                    ),
                    None,
                )
                if not target_prop_name:
                    logger.info(
                        f"[owl_to_python] Override not applied: property '{field_snake}' not found"
                    )
                    continue
                p = self.onto.properties[target_prop_name]
                p.type = PropertyType.DATA_PROPERTY
                p.data_type_hint_inner = py_type
                p._predefined_data_type = True
                ov = set(p._overrides_for)
                ov.add(cls_name)
                p._overrides_for = sorted(ov)
                if cls_name not in p.declared_domains:
                    p.declared_domains.append(cls_name)
                logger.info(
                    f"[owl_to_python] Applied override: {cls_name}.{field_snake} -> {py_type}"
                )

    def compute_type_hints(self):
        """
        Compute Python type hints for all properties.
        Handles both object properties (referencing classes) and data properties (XSD types).
        """
        for info in self.onto.properties.values():
            self._set_base_descriptors(info)
            if info.type == PropertyType.OBJECT_PROPERTY:
                self._set_object_range_hint(info)
            elif not (info._predefined_data_type and info.data_type_hint_inner):
                self._set_data_type_hint(info)

    def _set_base_descriptors(self, info: PropertyInfo):
        """
        Determine the base descriptor classes for a property.
        :param info: The PropertyInfo to update.
        """
        bases = [
            self.onto.properties[sp].descriptor_name
            for sp in info.superproperties
            if sp in self.onto.properties
        ] or ["PropertyDescriptor"]
        if info.is_transitive:
            bases.append("TransitiveProperty")
        if info.inverse_of:
            bases.append("HasInverseProperty")
        if info.equivalent_properties:
            bases.append("HasEquivalentProperty")
        info.base_descriptors = bases

    def _set_object_range_hint(self, info: PropertyInfo):
        """
        Compute and set the object_range_hint for an ObjectProperty.
        :param info: The PropertyInfo to update.
        """
        ranges = list(info.ranges)
        if ranges:
            rng_set = set(ranges)
            simplified = [
                r
                for r in sorted(rng_set)
                if not any(
                    a in rng_set for a in self.onto.class_ancestors.get(r, set())
                )
            ]
            ranges = simplified or ranges

        if len(ranges) > 1:
            info.object_range_hint = f"Union[{', '.join(sorted(set(ranges)))}]"
        elif len(ranges) == 1:
            info.object_range_hint = ranges[0]
        else:
            logger.warning(
                f"[owl_to_python]: Could not infer object range type for property '{info.name}'. Using Any."
            )
            info.object_range_hint = "Any"

    def _set_data_type_hint(self, info: PropertyInfo):
        """
        Compute and set the data_type_hint_inner for a DataProperty.
        :param info: The PropertyInfo to update.
        """
        py_types: List[str] = []
        # 1. Try mapping from XSD URIs
        for uri in info.range_uris:
            try:
                if isinstance(uri, rdflib.URIRef) and uri in self.XSD_TO_PYTHON_TYPES:
                    py_types.append(self.XSD_TO_PYTHON_TYPES[uri])
            except Exception:
                pass

        # 2. Try mapping from range names if URI mapping failed
        if not py_types:
            py_types = self._map_range_names_to_python_types(info.ranges)

        if not py_types:
            logger.warning(
                f"[owl_to_python]: Could not infer data type for property '{info.name}'. Using Any."
            )
            py_types.append("Any")

        unique_types = list(OrderedSet(py_types))
        info.data_type_hint_inner = (
            f"Union[{', '.join(unique_types)}]"
            if len(unique_types) > 1
            else unique_types[0]
        )

    @staticmethod
    def _map_range_names_to_python_types(range_names: List[str]) -> List[str]:
        """Map OWL range names (as strings) to Python types."""
        py_types = []
        textual = [r.lower() for r in range_names]
        for t in textual:
            if t in (
                "string",
                "normalizedstring",
                "token",
                "language",
                "anyuri",
                "datetime",
                "date",
                "time",
            ):
                py_types.append("str")
            elif t in (
                "integer",
                "int",
                "long",
                "short",
                "byte",
                "nonnegativeinteger",
                "positiveinteger",
                "unsignedlong",
                "unsignedint",
                "unsignedshort",
                "unsignedbyte",
            ):
                py_types.append("int")
            elif t in ("float", "double", "decimal"):
                py_types.append("float")
            elif t == "boolean":
                py_types.append("bool")
        return py_types

    def find_implicit_subtypes(self):
        """
        Identify implicit subtype or role relationships between classes based on property commonality.
        """
        for parent_name, parent_info in self.onto.classes.items():
            for child_name, child_info in self.onto.classes.items():
                if not self._is_subsumption_candidate(
                    parent_name, parent_info, child_name, child_info
                ):
                    continue

                matched_props = self._get_matched_properties(parent_info, child_info)
                if not matched_props:
                    continue

                subsumption_type = self._determine_subsumption_type(
                    matched_props, parent_info, child_info
                )
                if subsumption_type:
                    self._apply_implicit_subsumption(
                        child_info,
                        parent_name,
                        parent_info,
                        subsumption_type,
                    )

    @staticmethod
    def _is_subsumption_candidate(
        parent_name: str,
        parent_info: ClassInfo,
        child_name: str,
        child_info: ClassInfo,
    ) -> bool:
        """Check if parent and child are candidates for implicit subsumption."""
        if parent_name == child_name:
            return False
        if parent_name in child_info.all_base_classes_including_role_takers:
            return False
        if child_name in parent_info.all_base_classes_including_role_takers:
            return False
        return True

    def _get_matched_properties(
        self,
        parent_info: ClassInfo,
        child_info: ClassInfo,
    ) -> Set[str]:
        """
        Find property base names that are compatible between parent and child.
        """
        parent_props = parent_info.declared_properties
        child_props = child_info.declared_properties

        parent_props_filtered = {p.split("{")[0] for p in parent_props}
        child_props_filtered = {p.split("{")[0] for p in child_props}

        matched_prop_names = parent_props_filtered.intersection(child_props_filtered)

        # Re-verify based on original logic: check all combinations of parent/child properties
        # and remove/add base name based on range and superproperty compatibility.
        for parent_p_name in parent_props:
            parent_base_name = parent_p_name.split("{")[0]
            for child_p_name in child_props:
                child_p_info, parent_p_info = self.onto.properties.get(
                    child_p_name
                ), self.onto.properties.get(parent_p_name)
                if not child_p_info or not parent_p_info:
                    continue
                if (
                    child_p_info.type == PropertyType.DATA_PROPERTY
                    or parent_p_info.type == PropertyType.DATA_PROPERTY
                ):
                    continue
                if parent_base_name not in child_p_info.all_superproperties:
                    continue

                child_prop_range, parent_prop_range = (
                    child_p_info.object_range_hint,
                    parent_p_info.object_range_hint,
                )
                if parent_prop_range not in self.onto.class_ancestors.get(
                    child_prop_range, set()
                ):
                    if parent_base_name in matched_prop_names:
                        matched_prop_names.remove(parent_base_name)
                    continue
                matched_prop_names.add(parent_base_name)

        return matched_prop_names

    @staticmethod
    def _determine_subsumption_type(
        matched_props: Set[str], parent_info: ClassInfo, child_info: ClassInfo
    ) -> Optional[SubsumptionType]:
        """Determine if the relationship is a SUBTYPE or a ROLE."""
        parent_props_filtered = {
            p.split("{")[0] for p in parent_info.declared_properties
        }

        if matched_props == parent_props_filtered:
            if parent_info.role_taker:
                if (
                    not child_info.role_taker
                    or child_info.role_taker.class_name
                    != parent_info.role_taker.class_name
                ):
                    return None
            return SubsumptionType.SUBTYPE
        return SubsumptionType.ROLE

    def _apply_implicit_subsumption(
        self,
        child_info: ClassInfo,
        parent_name: str,
        parent_info: ClassInfo,
        subsumption_type: SubsumptionType,
    ):
        """Apply the determined subsumption to the child class."""
        if self.onto.base_cls_name in child_info.base_classes:
            child_info.base_classes.remove(self.onto.base_cls_name)

        if subsumption_type == SubsumptionType.ROLE:
            self._apply_role_subsumption(child_info, parent_name)
        else:
            self._apply_subtype_subsumption(child_info, parent_name, parent_info)

    def _apply_role_subsumption(self, child_info: ClassInfo, parent_name: str):
        """Add a role taker relationship to the class."""
        child_info.role_taker = RoleTakerInfo(
            parent_name, NamingRegistry.to_snake_case(parent_name)
        )
        if self.onto.role_cls_name not in child_info.all_base_classes:
            child_info.base_classes = [
                self.onto.role_cls_name
            ] + child_info.base_classes
            child_info.all_base_classes = [
                self.onto.role_cls_name
            ] + child_info.all_base_classes
        child_info.all_base_classes_including_role_takers.append(parent_name)

    @staticmethod
    def _apply_subtype_subsumption(
        child_info: ClassInfo, parent_name: str, parent_info: ClassInfo
    ):
        """Make the class a subtype of another class."""
        child_info.base_classes = []
        if parent_name not in child_info.base_classes:
            child_info.base_classes.append(parent_name)
            child_info.all_base_classes.append(parent_name)
            child_info.all_base_classes_including_role_takers.append(parent_name)

        # Remove redundant properties already declared in the parent
        parent_props = set(parent_info.declared_properties)
        child_info.declared_properties = [
            p for p in child_info.declared_properties if p not in parent_props
        ]


class JinjaRenderer:
    """Renderer for generating Python code using Jinja2 templates."""

    def __init__(self, template_dir: str):
        """
        Initialize the renderer.
        :param template_dir: Directory containing Jinja2 templates.
        """
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=[loopcontrols],
        )

    def render(self, template_name: str, **context) -> str:
        """
        Render a template with the given context.
        :param template_name: Name of the template file.
        :param context: Keyword arguments for the template context.
        :return: Rendered string.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)


@dataclass
class CodeGenerator:
    """Orchestrates the generation of Python code from extracted ontology information."""

    onto: OntologyInfo
    engine: InferenceEngine = field(init=False)
    renderer: JinjaRenderer = field(init=False)

    def __post_init__(self):
        """
        Initialize the code generator.
        """
        self._ensure_ontology_base_class_in_classes()

        self._ensure_uri_in_ontology_properties()

        self._replace_ontology_role_class_with_current_role_class_name()

        self._update_base_classes()

        self.engine, self.renderer = InferenceEngine(self.onto), JinjaRenderer(
            os.path.dirname(__file__)
        )

    def generate(self, base_file_name: str) -> Dict[str, str]:
        """
        Execute the full generation pipeline.
        :param base_file_name: Base name for generated files.
        :return: Dictionary mapping filenames to their rendered content.
        """

        self._execute_inference_pipeline()

        self._determine_class_properties()

        self.attach_domainless_properties_to_ontology_base_class()

        classes_order, props_order = self._finalize_and_sort()

        return self._perform_rendering(
            base_file_name,
            classes_order,
            props_order,
        )

    def attach_domainless_properties_to_ontology_base_class(self):
        """
        Attach properties without declared domains to the ontology base class.
        """
        for p in self.onto.properties.values():
            if p.field_name == "plays_role" or p.declared_domains or p.domains:
                continue
            p.declared_domains = [self.onto.base_cls_name]
            base_class_info = self.onto.classes[self.onto.base_cls_name]
            if p.name not in base_class_info.declared_properties:
                base_class_info.declared_properties.append(p.name)

    def _replace_ontology_role_class_with_current_role_class_name(self):
        """
        Replace ontology role class name with current role class name.
        """
        for info in self.onto.classes.values():
            if "Role" not in info.base_classes:
                continue
            info.base_classes.remove("Role")
            info.base_classes.append(self.onto.role_cls_name)

    def _ensure_uri_in_ontology_properties(self):
        """
        Ensures that the 'uri' property is present in the ontology properties.
        If not present, adds it with appropriate configuration.
        """
        if "uri" in self.onto.properties:
            return
        self.onto.properties["uri"] = PropertyInfo(
            "uri",
            "",
            PropertyType.DATA_PROPERTY,
            domains=[self.onto.base_cls_name],
            ranges=["str"],
            range_uris=[XSD.anyURI],
            label="URI of the ontology element",
            comment="The unique resource identifier (URI) of the ontology element.",
            field_name="uri",
            descriptor_name="Uri",
            declared_domains=[self.onto.base_cls_name],
        )

    def _update_base_classes(self):
        for n, info in self.onto.classes.items():
            if n == self.onto.base_cls_name:
                continue
            info.base_classes = [b for b in info.superclasses if b != "Symbol"] or [
                self.onto.base_cls_name
            ]
            if (
                len(info.base_classes) == 1
                and info.base_classes[0] == self.onto.role_cls_name
            ):
                info.base_classes.append("Symbol")

    def _ensure_ontology_base_class_in_classes(self):
        if self.onto.base_cls_name in self.onto.classes:
            return
        self.onto.classes[self.onto.base_cls_name] = ClassInfo(
            self.onto.base_cls_name,
            "",
            ["Symbol", "ABC"],
            ["Symbol", "ABC"],
            label=f"Base class for {self.onto.ontology_label}",
        )

    def _execute_inference_pipeline(self):
        """
        Run the inference engine to propagate types and specialized properties.
        """
        self.engine.compute_ancestors()

        self.engine.infer_properties()

        self.engine.apply_predefined_overrides()

        self.attach_domainless_data_properties_to_ontology_base_class()

        self.engine.compute_type_hints()

    def attach_domainless_data_properties_to_ontology_base_class(self):
        """
        Attach properties without declared domains to the ontology base class.
        """
        for p in self.onto.properties.values():
            if p.type == PropertyType.DATA_PROPERTY and not p.declared_domains:
                p.declared_domains = [self.onto.base_cls_name]

    def _determine_class_properties(self):
        """
        Decide which properties belong to which class based on inheritance and overrides.
        """
        for cls_name, info in self.onto.classes.items():
            ancestors = set(info.all_base_classes)
            declared: List[str] = []
            for pn, p in self.onto.properties.items():
                if pn == "roleFor":
                    continue
                if cls_name not in (set(p.declared_domains) | set(p.domains)):
                    continue
                if (
                    ancestors
                    and cls_name not in p._overrides_for
                    and any(
                        a in (set(p.declared_domains) | set(p.domains))
                        for a in ancestors
                    )
                ):
                    continue
                if p.is_specialized:
                    for sp in p.superproperties:
                        if sp in declared:
                            declared.remove(sp)
                declared.append(pn)
            info.declared_properties = sorted(set(declared))

    def _finalize_and_sort(self):
        """
        Compute transitive closures and determine final topological order for classes and properties.
        """
        for p in self.onto.properties.values():
            p.all_superproperties = self._compute_closure(
                p.superproperties, self.onto.properties, "superproperties"
            )

        for info in self.onto.classes.values():
            initial = set(info.all_base_classes)
            if info.role_taker:
                initial.add(info.role_taker.class_name)
            info.all_base_classes_including_role_takers = self._compute_closure(
                list(initial), self.onto.classes, "all_base_classes", "role_taker"
            )

        self.engine.find_implicit_subtypes()

        for info in self.onto.classes.values():
            info.base_classes_for_topological_sort = info.base_classes[:]
            if info.role_taker:
                info.base_classes_for_topological_sort.append(
                    info.role_taker.class_name
                )

        classes_order = self.engine.topological_order(
            self.onto.classes, "base_classes_for_topological_sort"
        )
        prop_classes = {
            k: v for k, v in self.onto.properties.items() if not v.is_specialized
        }
        props_order = self.engine.topological_order(prop_classes, "superproperties")

        idx_map = {n: i for i, n in enumerate(props_order)}
        for info in prop_classes.values():
            if info.inverse_of in prop_classes:
                info.inverse_target_is_prior = idx_map.get(
                    info.inverse_of, 1e9
                ) < idx_map.get(info.name, 1e9)

        return classes_order, props_order

    def _perform_rendering(
        self,
        base_file_name,
        classes_order,
        props_order,
    ):
        """
        Render all templates and produce the final Python files and stubs.
        """
        stubs_classes = deepcopy(self.onto.classes)
        for cls_name, info in self.onto.classes.items():
            if self.onto.role_cls_name in info.base_classes:
                info.base_classes.remove(self.onto.role_cls_name)
                info.base_classes.insert(
                    0, f"{self.onto.role_cls_name}[{info.role_taker.class_name}]"
                )
                stubs_classes[cls_name].base_classes.remove(self.onto.role_cls_name)
            else:
                info.add_role_taker = stubs_classes[cls_name].add_role_taker = False

        if "Role" in self.onto.classes:
            del self.onto.classes["Role"]

        # topological_order might still have 'Role' name if it was in the items keys
        # We need to filter the order as well
        classes_order = [c for c in classes_order if c != "Role"]

        render_classes = {k: asdict(v) for k, v in self.onto.classes.items()}
        for c in render_classes.values():
            if c["role_taker"] is None:
                c["role_taker"] = {}

        for p_name, p_info in self.onto.properties.items():
            for eq_prop_name in p_info.equivalent_properties:
                p_info.equivalent_properties_descriptor_names.append(
                    self.onto.properties[eq_prop_name].descriptor_name
                )

        render_props = {k: asdict(v) for k, v in self.onto.properties.items()}
        render_stubs = {k: asdict(v) for k, v in stubs_classes.items()}
        for c in render_stubs.values():
            if c["role_taker"] is None:
                c["role_taker"] = {}

        p_mod, b_mod = f"{base_file_name}_properties", f"{base_file_name}_base"
        return {
            f"{p_mod}.py": self.renderer.render(
                "onto_properties.j2",
                properties=render_props,
                properties_order=props_order,
            ),
            f"{b_mod}.py": self.renderer.render(
                "onto_base.j2",
                cls=render_classes[self.onto.base_cls_name],
                properties=render_props,
            ),
            f"{base_file_name}.py": self.renderer.render(
                "onto_classes.j2",
                ontology_base_module_name=b_mod,
                properties_module_name=p_mod,
                classes=render_classes,
                properties=render_props,
                classes_order=classes_order,
                properties_order=props_order,
                ontology_base_class_name=self.onto.base_cls_name,
            ),
            f"{base_file_name}.pyi": self.renderer.render(
                "onto_stubs.j2",
                ontology_base_module_name=b_mod,
                properties_module_name=p_mod,
                role_takers=list(
                    OrderedSet(
                        c["role_taker"]["class_name"]
                        for c in render_classes.values()
                        if c["role_taker"]
                    )
                ),
                classes=render_stubs,
                properties=render_props,
                classes_order=classes_order,
                ontology_base_class_name=self.onto.base_cls_name,
            ),
        }

    @staticmethod
    def _compute_closure(
        initial: List[str],
        items: Dict[str, Any],
        key: str,
        role_key: Optional[str] = None,
    ) -> List[str]:
        """
        Compute the transitive closure of a relationship.
        """
        res, stack = set(), list(initial)
        while stack:
            curr = stack.pop()
            if curr not in res:
                res.add(curr)
                if curr in items:
                    item = items[curr]
                    stack.extend(
                        getattr(item, key, [])
                        if hasattr(item, key)
                        else item.get(key, [])
                    )
                    rt = (
                        getattr(item, role_key, None)
                        if role_key and hasattr(item, role_key)
                        else (item.get(role_key) if role_key else None)
                    )
                    if rt:
                        stack.append(
                            rt.class_name
                            if hasattr(rt, "class_name")
                            else rt["class_name"]
                        )
        return sorted(res)


class OwlToPythonConverter:
    """High-level converter for transforming an OWL ontology into Python source code."""

    def __init__(
        self, predefined_data_types: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the converter.
        :param predefined_data_types: Manual type overrides for properties.
        """
        self.graph = rdflib.Graph()
        self.classes: Dict[str, ClassInfo] = {}
        self.properties: Dict[str, PropertyInfo] = {}
        self.predefined_data_types = predefined_data_types or {}
        self.metadata = MetadataExtractor(self.graph)
        self.class_ext = ClassExtractor(self.graph, self.metadata)
        self.prop_ext = PropertyExtractor(self.graph, self.metadata)
        self.ontology_label = None
        self.ontology_info: Optional[OntologyInfo] = None

    def load_ontology(self, path: str):
        """
        Load an OWL ontology from a file.
        :param path: Path to the .owl file.
        """
        self.graph.parse(path)
        self._extract_ontology_info()

    def _extract_ontology_info(self):
        """
        Extract classes and properties from the loaded graph.
        """
        for s in self.graph.subjects(RDF.type, OWL.Ontology):
            self.ontology_label = self.metadata.get_label(s)
            if not self.ontology_label:
                self.ontology_label = NamingRegistry.uri_to_python_name(s)
            break

        if not self.ontology_label:
            self.ontology_label = "Ontology"

        for cls_uri in self.graph.subjects(RDF.type, OWL.Class):
            if isinstance(cls_uri, rdflib.term.BNode):
                continue
            info = self.class_ext.extract_info(cls_uri)
            self.classes[info.name] = info

        for p_type in [
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.TransitiveProperty,
        ]:
            for p_uri in self.graph.subjects(RDF.type, p_type):
                if isinstance(p_uri, rdflib.term.BNode):
                    continue
                info = self.prop_ext.extract_info(p_uri)
                if info.name in self.properties:
                    existing = self.properties[info.name]
                    if p_type == OWL.TransitiveProperty:
                        existing.is_transitive = True
                    existing.domains = sorted(set(existing.domains) | set(info.domains))
                    existing.ranges = sorted(set(existing.ranges) | set(info.ranges))
                    if not existing.inverse_of:
                        existing.inverse_of = info.inverse_of
                else:
                    self.properties[info.name] = info

        self.ontology_info = OntologyInfo(
            self.graph,
            self.classes,
            self.properties,
            self.predefined_data_types,
            self.ontology_label,
        )

    def generate_python_code_external(self, base_file_name: str) -> Dict[str, str]:
        """
        Generate Python code without saving to disk.
        :param base_file_name: Base name for the generated files.
        :return: Dictionary of filename to content.
        """
        gen = CodeGenerator(self.ontology_info)
        return gen.generate(base_file_name)

    def save_to_file(self, output_path: str):
        """
        Generate Python code and save it to the specified output path.
        :param output_path: Base path (filename) for the main output file.
        """
        base = os.path.splitext(os.path.basename(output_path))[0]
        for name, content in self.generate_python_code_external(base).items():
            with open(
                os.path.join(os.path.dirname(output_path), name), "w", encoding="utf-8"
            ) as f:
                f.write(content)


# Usage
if __name__ == "__main__":
    from krrood_experiments.helpers import (
        generate_lubm_with_predicates,
        generate_owl2bench_with_predicates,
    )

    # generate_lubm_with_predicates(clean=True)
    generate_owl2bench_with_predicates(clean=False)
