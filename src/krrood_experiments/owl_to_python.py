"""
This module provides functionality to convert OWL ontologies into Python source code.
It includes classes for extracting information from RDF graphs, performing inference,
and generating Python code using Jinja2 templates.
"""

import os
import re
from collections import defaultdict
from copy import copy, deepcopy
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Callable, Optional, Any

import rdflib
from jinja2 import Environment, FileSystemLoader
from krrood import logger
from rdflib.namespace import RDF, RDFS, OWL, XSD
from sqlalchemy.util import OrderedSet


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
    type: str  # "ObjectProperty" or "DataProperty"
    domains: List[str] = field(default_factory=list)
    ranges: List[str] = field(default_factory=list)
    range_uris: List[Any] = field(default_factory=list)
    label: Optional[str] = None
    comment: Optional[str] = None
    field_name: str = ""
    descriptor_name: str = ""
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

        # Determine property type
        prop_type = "ObjectProperty"
        is_transitive = False
        for prop_type_uri in self.graph.objects(property_uri, RDF.type):
            if prop_type_uri == OWL.DatatypeProperty:
                prop_type = "DataProperty"
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


class InferenceEngine:
    """Engine for performing ontological inference and computing class/property relationships."""

    def __init__(self, graph: rdflib.Graph):
        """
        Initialize the inference engine.
        :param graph: The rdflib graph.
        """
        self.graph = graph

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

    def compute_ancestors(self, classes: Dict[str, ClassInfo]):
        """
        Compute full ancestor sets for each class (transitive closure).
        :param classes: Dictionary mapping class names to ClassInfo.
        """
        # Compute full ancestor sets for each class (transitive closure)
        name_to_bases = {name: set(info.base_classes) for name, info in classes.items()}
        for info in classes.values():
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
        properties: Dict[str, PropertyInfo],
        classes: Dict[str, ClassInfo],
        role_cls_name: str,
    ):
        """
        Main entry point for property inference.
        Propagates domains, ranges, and handles restrictions and inverses.
        :param properties: Dictionary of PropertyInfo.
        :param classes: Dictionary of ClassInfo.
        :param role_cls_name: The name of the base Role class.
        :return: A dictionary of property restrictions found.
        """
        dom_map, rng_map, rng_uri_map, super_map, inverse_pairs = (
            self._init_inference_maps(properties)
        )

        property_restrictions: Dict[str, Dict[str, set]] = {}

        def _handle_restriction(for_class: str, node):
            if not node:
                return
            on_prop = self.graph.value(node, OWL.onProperty)
            if not on_prop:
                return
            prop_name = NamingRegistry.uri_to_python_name(on_prop)
            if prop_name in properties:
                dom_map[prop_name].add(for_class)
            some = self.graph.value(node, OWL.someValuesFrom) or self.graph.value(
                node, OWL.allValuesFrom
            )
            if some:
                try:
                    rng_name = NamingRegistry.uri_to_python_name(some)
                    if prop_name == "roleFor":
                        cls_info = classes.get(for_class)
                        if cls_info:
                            cls_info.role_taker = RoleTakerInfo(
                                rng_name, NamingRegistry.to_snake_case(rng_name)
                            )
                        return
                    rng_map[prop_name].add(rng_name)
                    rng_uri_map[prop_name].add(some)
                    property_restrictions.setdefault(for_class, {}).setdefault(
                        prop_name, set()
                    ).add(rng_name)
                except Exception:
                    pass

        declared_dom_map = {
            name: set(info.domains) for name, info in properties.items()
        }
        RestrictionWalker.walk(self.graph, declared_dom_map, _handle_restriction)

        for info in classes.values():
            if "Role" in info.base_classes:
                info.base_classes.remove("Role")
                info.base_classes.append(role_cls_name)

        self._propagate_types(dom_map, rng_map, rng_uri_map, super_map, inverse_pairs)
        self._finalize_properties(
            properties, dom_map, rng_map, rng_uri_map, declared_dom_map
        )

        return property_restrictions

    def _init_inference_maps(self, properties: Dict[str, PropertyInfo]):
        """
        Initialize maps used for property type propagation.
        :param properties: Dictionary of PropertyInfo.
        :return: Tuple of maps (domain, range, range_uri, superproperty, inverses).
        """
        dom_map = {n: set(p.domains) for n, p in properties.items()}
        rng_map = {n: set(p.ranges) for n, p in properties.items()}
        rng_uri_map = {n: set(p.range_uris) for n, p in properties.items()}
        super_map = {n: list(p.superproperties) for n, p in properties.items()}
        inverse_pairs = [
            (n, inv)
            for n, p in properties.items()
            for inv in p.inverses
            if inv in properties
        ]
        return dom_map, rng_map, rng_uri_map, super_map, inverse_pairs

    def _propagate_types(self, dom_map, rng_map, rng_uri_map, super_map, inverse_pairs):
        """
        Perform iterative propagation of domains and ranges along property hierarchy and inverses.
        """
        changed = True
        while changed:
            changed = False
            for name, supers in super_map.items():
                for sp in supers:
                    if sp not in dom_map:
                        continue
                    before_r, before_ru = len(rng_map[name]), len(rng_uri_map[name])
                    rng_map[name].update(rng_map[sp])
                    rng_uri_map[name].update(rng_uri_map[sp])
                    if (
                        len(rng_map[name]) != before_r
                        or len(rng_uri_map[name]) != before_ru
                    ):
                        changed = True
            for a, b in inverse_pairs:
                before_da, before_ra = len(dom_map[a]), len(rng_map[a])
                before_db, before_rb = len(dom_map[b]), len(rng_map[b])
                dom_map[a].update(rng_map[b])
                rng_map[a].update(dom_map[b])
                dom_map[b].update(rng_map[a])
                rng_map[b].update(dom_map[a])
                if (
                    len(dom_map[a]) != before_da
                    or len(rng_map[a]) != before_ra
                    or len(dom_map[b]) != before_db
                    or len(rng_map[b]) != before_rb
                ):
                    changed = True

    def _finalize_properties(
        self, properties, dom_map, rng_map, rng_uri_map, declared_dom_map
    ):
        """
        Update PropertyInfo objects with inferred domain and range information.
        """
        for name, info in properties.items():
            info.domains = sorted(dom_map[name])
            info.ranges = sorted(rng_map[name])
            info.range_uris = list(rng_uri_map[name])
            info.declared_domains = sorted(declared_dom_map[name])

    def create_specialized_properties(
        self,
        properties: Dict[str, PropertyInfo],
        property_restrictions: Dict[str, Dict[str, set]],
        original_properties: Dict[str, PropertyInfo],
    ):
        """
        Create specialized versions of properties based on class-level restrictions.
        Used for narrowing property ranges in specific subclasses.
        """
        specialized_props: Dict[str, PropertyInfo] = {}
        for cls_name, props in property_restrictions.items():
            for prop_name, rng_names in props.items():
                base = properties.get(prop_name)
                if not base or base.type != "ObjectProperty":
                    continue
                if rng_names.issubset(set(original_properties[prop_name].ranges)):
                    continue
                if cls_name in base.declared_domains:
                    base.declared_domains.remove(cls_name)
                for rng_name in sorted(rng_names):
                    spec_key = f"{prop_name}{{{rng_name}}}"
                    if spec_key in properties or spec_key in specialized_props:
                        continue
                    specialized_props[spec_key] = PropertyInfo(
                        name=prop_name,
                        uri=base.uri,
                        type="ObjectProperty",
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
        properties.update(specialized_props)

    def apply_predefined_overrides(
        self,
        classes: Dict[str, ClassInfo],
        properties: Dict[str, PropertyInfo],
        predefined_data_types: Dict[str, Dict[str, str]],
    ):
        """
        Apply manual type overrides for specific class properties.
        :param classes: Dictionary of ClassInfo.
        :param properties: Dictionary of PropertyInfo.
        :param predefined_data_types: Nested dictionary mapping class names to field names and their target types.
        """
        for cls_name, overrides in (predefined_data_types or {}).items():
            for field_snake, py_type in overrides.items():
                target_prop_name = next(
                    (n for n, p in properties.items() if p.field_name == field_snake),
                    None,
                )
                if not target_prop_name:
                    logger.info(
                        f"[owl_to_python] Override not applied: property '{field_snake}' not found"
                    )
                    continue
                p = properties[target_prop_name]
                p.type = "DataProperty"
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

    def compute_type_hints(
        self, classes: Dict[str, ClassInfo], properties: Dict[str, PropertyInfo]
    ):
        """
        Compute Python type hints for all properties.
        Handles both object properties (referencing classes) and data properties (XSD types).
        :param classes: Dictionary of ClassInfo.
        :param properties: Dictionary of PropertyInfo.
        :return: Ancestor map for classes.
        """
        xsd_to_py = {
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
        ancestors_map = {
            name: set(info.all_base_classes) for name, info in classes.items()
        }
        for name, info in properties.items():
            bases = [
                properties[sp].descriptor_name
                for sp in info.superproperties
                if sp in properties
            ] or ["PropertyDescriptor"]
            if info.is_transitive:
                bases.append("TransitiveProperty")
            if info.inverse_of:
                bases.append("HasInverseProperty")
            info.base_descriptors = bases

            if info.type == "ObjectProperty":
                ranges = list(info.ranges)
                if ranges:
                    rng_set = set(ranges)
                    simplified = [
                        r
                        for r in sorted(rng_set)
                        if not any(a in rng_set for a in ancestors_map.get(r, set()))
                    ]
                    ranges = simplified or ranges
                if len(ranges) > 1:
                    info.object_range_hint = f"Union[{', '.join(sorted(set(ranges)))}]"
                elif len(ranges) == 1:
                    info.object_range_hint = ranges[0]
                else:
                    logger.warning(
                        f"[owl_to_python]: Could not infer object range type for property '{name}'. Using Any."
                    )
                    info.object_range_hint = "Any"
            elif not (info._predefined_data_type and info.data_type_hint_inner):
                py_types: List[str] = []
                for uri in info.range_uris:
                    try:
                        if isinstance(uri, rdflib.URIRef) and uri in xsd_to_py:
                            py_types.append(xsd_to_py[uri])
                    except Exception:
                        pass
                if not py_types:
                    textual = [r.lower() for r in info.ranges]
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
                    if not py_types:
                        logger.warning(
                            f"[owl_to_python]: Could not infer data type for property '{name}'. Using Any."
                        )
                        py_types.append("Any")
                unique_types = list(OrderedSet(py_types))
                info.data_type_hint_inner = (
                    f"Union[{', '.join(unique_types)}]"
                    if len(unique_types) > 1
                    else unique_types[0]
                )
        return ancestors_map

    def find_implicit_subtypes(
        self,
        classes: Dict[str, ClassInfo],
        properties: Dict[str, PropertyInfo],
        ancestors_map: Dict,
        ontology_base_class_name: str,
        role_cls_name: str,
    ):
        """
        Identify implicit subtype or role relationships between classes based on property commonality.
        :param classes: Dictionary of ClassInfo.
        :param properties: Dictionary of PropertyInfo.
        :param ancestors_map: Map of class ancestors.
        :param ontology_base_class_name: Name of the root ontology class.
        :param role_cls_name: Name of the Role class.
        """
        for parent_cls_name, parent_cls_info in classes.items():
            parent_props_names = parent_cls_info.declared_properties
            parent_props_names_filtered = {
                prop.split("{")[0] for prop in parent_props_names
            }
            for child_cls_name, child_cls_info in classes.items():
                if parent_cls_name == child_cls_name:
                    continue
                if (
                    parent_cls_name
                    in child_cls_info.all_base_classes_including_role_takers
                ):
                    continue
                if (
                    child_cls_name
                    in parent_cls_info.all_base_classes_including_role_takers
                ):
                    continue
                child_props_names = child_cls_info.declared_properties
                child_props_names_filtered = {
                    prop.split("{")[0] for prop in child_props_names
                }
                matched_prop_names = parent_props_names_filtered.intersection(
                    child_props_names_filtered
                )
                for parent_prop_name in parent_props_names:
                    for child_prop_name in child_props_names:
                        child_prop_info, parent_prop_info = properties.get(
                            child_prop_name
                        ), properties.get(parent_prop_name)
                        parent_prop_filtered_name = parent_prop_name.split("{")[0]
                        if not child_prop_info or not parent_prop_info:
                            continue
                        if (
                            child_prop_info.type == "DataProperty"
                            or parent_prop_info.type == "DataProperty"
                        ):
                            continue
                        if (
                            parent_prop_filtered_name
                            not in child_prop_info.all_superproperties
                        ):
                            continue
                        child_prop_range, parent_prop_range = (
                            child_prop_info.object_range_hint,
                            parent_prop_info.object_range_hint,
                        )
                        if parent_prop_range not in ancestors_map.get(
                            child_prop_range, set()
                        ):
                            if parent_prop_filtered_name in matched_prop_names:
                                matched_prop_names.remove(parent_prop_filtered_name)
                            continue
                        matched_prop_names.add(parent_prop_filtered_name)
                if not matched_prop_names:
                    continue
                if matched_prop_names == parent_props_names_filtered:
                    if parent_cls_info.role_taker:
                        if child_cls_info.role_taker:
                            if (
                                child_cls_info.role_taker.class_name
                                != parent_cls_info.role_taker.class_name
                            ):
                                continue
                        else:
                            continue
                    subsumption_type = SubsumptionType.SUBTYPE
                else:
                    subsumption_type = SubsumptionType.ROLE
                if not matched_prop_names:
                    continue
                if ontology_base_class_name in child_cls_info.base_classes:
                    child_cls_info.base_classes.remove(ontology_base_class_name)
                if subsumption_type == SubsumptionType.ROLE:
                    child_cls_info.role_taker = RoleTakerInfo(
                        parent_cls_name, NamingRegistry.to_snake_case(parent_cls_name)
                    )
                    if role_cls_name not in child_cls_info.all_base_classes:
                        child_cls_info.base_classes = [
                            role_cls_name
                        ] + child_cls_info.base_classes
                        child_cls_info.all_base_classes = [
                            role_cls_name
                        ] + child_cls_info.all_base_classes
                    child_cls_info.all_base_classes_including_role_takers.append(
                        parent_cls_name
                    )
                else:
                    child_cls_info.base_classes = []
                    if parent_cls_name not in child_cls_info.base_classes:
                        child_cls_info.base_classes.append(parent_cls_name)
                        child_cls_info.all_base_classes.append(parent_cls_name)
                        child_cls_info.all_base_classes_including_role_takers.append(
                            parent_cls_name
                        )
                    for prop in copy(child_cls_info.declared_properties):
                        if prop in parent_cls_info.declared_properties:
                            child_cls_info.declared_properties.remove(prop)


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


class RestrictionWalker:
    """Utility for walking OWL restrictions in an RDF graph."""

    @staticmethod
    def walk(
        graph: rdflib.Graph,
        declared_dom_map: Optional[Dict[str, set]] = None,
        restrictions_handler: Optional[Callable] = None,
    ):
        """
        Walk through all classes and their restrictions in the graph.
        :param graph: The rdflib graph.
        :param declared_dom_map: Optional map to populate with declared domains.
        :param restrictions_handler: Optional callback for each restriction found.
        """
        if declared_dom_map is None:
            declared_dom_map: Dict[str, set] = defaultdict(set)
        # Walk class restrictions
        for cls_uri in graph.subjects(RDF.type, OWL.Class):
            cls_name = NamingRegistry.uri_to_python_name(cls_uri)
            # direct subclass restrictions
            for restr in graph.objects(cls_uri, RDFS.subClassOf):
                if restrictions_handler:
                    restrictions_handler(cls_name, restr)
                # If restriction mentions a property, count this class as declared domain for that property
                on_prop = graph.value(restr, OWL.onProperty)
                if on_prop:
                    declared_dom_map[NamingRegistry.uri_to_python_name(on_prop)].add(
                        cls_name
                    )

            # restrictions inside intersectionOf
            for coll in graph.objects(cls_uri, OWL.intersectionOf):
                node = coll
                while node and node != RDF.nil:
                    first = graph.value(node, RDF.first)
                    if restrictions_handler:
                        restrictions_handler(cls_name, first)
                    on_prop = graph.value(first, OWL.onProperty) if first else None
                    if on_prop:
                        declared_dom_map[
                            NamingRegistry.uri_to_python_name(on_prop)
                        ].add(cls_name)
                    node = graph.value(node, RDF.rest)


class CodeGenerator:
    """Orchestrates the generation of Python code from extracted ontology information."""

    def __init__(
        self,
        graph: rdflib.Graph,
        classes: Dict[str, ClassInfo],
        properties: Dict[str, PropertyInfo],
        ontology_label: str,
        predefined_data_types: Dict,
    ):
        """
        Initialize the code generator.
        :param graph: The rdflib graph.
        :param classes: Extracted classes.
        :param properties: Extracted properties.
        :param ontology_label: Label for the ontology.
        :param predefined_data_types: Manual type overrides.
        """
        (
            self.graph,
            self.classes,
            self.properties,
            self.ontology_label,
            self.predefined_data_types,
        ) = (graph, classes, properties, ontology_label, predefined_data_types)
        self.engine, self.renderer = InferenceEngine(graph), JinjaRenderer(
            os.path.dirname(__file__)
        )

    def generate(self, base_file_name: str) -> Dict[str, str]:
        """
        Execute the full generation pipeline.
        :param base_file_name: Base name for generated files.
        :return: Dictionary mapping filenames to their rendered content.
        """
        role_cls_name = "Role"
        classes, properties, orig_props, base_cls_name = self._prepare_initial_state(
            role_cls_name
        )
        restrs, ancestors_map = self._execute_inference_pipeline(
            classes, properties, orig_props, role_cls_name, base_cls_name
        )
        self._determine_class_properties(classes, properties)
        self._finalize_and_sort(
            classes, properties, ancestors_map, base_cls_name, role_cls_name
        )
        return self._perform_rendering(
            base_file_name, classes, properties, base_cls_name, role_cls_name
        )

    def _prepare_initial_state(self, role_cls_name: str):
        """
        Prepare initial ClassInfo and PropertyInfo copies and setup base classes.
        """
        classes = {n: deepcopy(info) for n, info in self.classes.items()}
        properties = {n: deepcopy(info) for n, info in self.properties.items()}
        orig_props = {n: deepcopy(info) for n, info in self.properties.items()}

        base_cls_name = NamingRegistry.to_pascal_case(
            re.sub(r"\W+", " ", self.ontology_label).strip()
        )
        if not base_cls_name.endswith("Ontology"):
            base_cls_name += "Ontology"

        if base_cls_name not in classes:
            classes[base_cls_name] = ClassInfo(
                base_cls_name,
                "",
                ["Symbol", "ABC"],
                ["Symbol", "ABC"],
                label=f"Base class for {self.ontology_label}",
            )

        for n, info in classes.items():
            if n == base_cls_name:
                continue
            info.base_classes = [b for b in info.superclasses if b != "Symbol"] or [
                base_cls_name
            ]
            if len(info.base_classes) == 1 and info.base_classes[0] == role_cls_name:
                info.base_classes.append("Symbol")

        return classes, properties, orig_props, base_cls_name

    def _execute_inference_pipeline(
        self, classes, properties, orig_props, role_cls_name, base_cls_name
    ):
        """
        Run the inference engine to propagate types and specialized properties.
        """
        self.engine.compute_ancestors(classes)
        restrs = self.engine.infer_properties(properties, classes, role_cls_name)
        self.engine.create_specialized_properties(properties, restrs, orig_props)

        if "uri" not in properties:
            properties["uri"] = PropertyInfo(
                "uri",
                "",
                "DataProperty",
                domains=[base_cls_name],
                ranges=["str"],
                range_uris=[XSD.anyURI],
                label="URI of the ontology element",
                comment="The unique resource identifier (URI) of the ontology element.",
                field_name="uri",
                descriptor_name="Uri",
                declared_domains=[base_cls_name],
            )

        for p in properties.values():
            if p.type == "DataProperty" and not p.declared_domains:
                p.declared_domains = [base_cls_name]

        self.engine.apply_predefined_overrides(
            classes, properties, self.predefined_data_types
        )
        ancestors_map = self.engine.compute_type_hints(classes, properties)
        return restrs, ancestors_map

    def _determine_class_properties(self, classes, properties):
        """
        Decide which properties belong to which class based on inheritance and overrides.
        """
        for cls_name, info in classes.items():
            ancestors = set(info.all_base_classes)
            declared: List[str] = []
            for pn, p in properties.items():
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
            info.declared_properties = declared

    def _finalize_and_sort(
        self, classes, properties, ancestors_map, base_cls_name, role_cls_name
    ):
        """
        Compute transitive closures and prepare topological sort for output.
        """
        for p in properties.values():
            p.all_superproperties = self._compute_closure(
                p.superproperties, properties, "superproperties"
            )
        for info in classes.values():
            initial = set(info.all_base_classes)
            if info.role_taker:
                initial.add(info.role_taker.class_name)
            info.all_base_classes_including_role_takers = self._compute_closure(
                list(initial), classes, "all_base_classes", "role_taker"
            )

        self.engine.find_implicit_subtypes(
            classes, properties, ancestors_map, base_cls_name, role_cls_name
        )
        for info in classes.values():
            info.base_classes_for_topological_sort = info.base_classes[:]
            if info.role_taker:
                info.base_classes_for_topological_sort.append(
                    info.role_taker.class_name
                )

    def _perform_rendering(
        self, base_file_name, classes, properties, base_cls_name, role_cls_name
    ):
        """
        Render the final Python modules and stubs.
        :return: Dictionary of filename to content.
        """
        classes_order = self.engine.topological_order(
            classes, "base_classes_for_topological_sort"
        )
        prop_classes = {k: v for k, v in properties.items() if not v.is_specialized}
        props_order = self.engine.topological_order(prop_classes, "superproperties")
        idx_map = {n: i for i, n in enumerate(props_order)}
        for info in prop_classes.values():
            info.inverse_target_is_prior = (
                info.inverse_of in prop_classes
                and idx_map.get(info.inverse_of, 1e9) < idx_map.get(info.name, 1e9)
            )

        stubs_classes = deepcopy(classes)
        for cls_name, info in classes.items():
            if role_cls_name in info.base_classes:
                info.base_classes.remove(role_cls_name)
                info.base_classes.insert(
                    0, f"{role_cls_name}[{info.role_taker.class_name}]"
                )
                stubs_classes[cls_name].base_classes.remove(role_cls_name)
            else:
                info.add_role_taker = stubs_classes[cls_name].add_role_taker = False

        if "Role" in classes:
            del classes["Role"]
        if "Role" in classes_order:
            classes_order.remove("Role")

        render_classes = {k: asdict(v) for k, v in classes.items()}
        for c in render_classes.values():
            if c["role_taker"] is None:
                c["role_taker"] = {}
        render_props = {k: asdict(v) for k, v in properties.items()}
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
                cls=render_classes[base_cls_name],
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
                ontology_base_class_name=base_cls_name,
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
                ontology_base_class_name=base_cls_name,
            ),
        }

    def _compute_closure(
        self,
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

    def load_ontology(self, path: str):
        """
        Load an OWL ontology from a file.
        :param path: Path to the .owl file.
        """
        self.graph.parse(path)
        self._extract()

    def _extract(self):
        """
        Extract classes and properties from the loaded graph.
        """
        self.ontology_label = next(
            (
                self.metadata.get_label(s)
                for s in self.graph.subjects(RDF.type, OWL.Ontology)
            ),
            "Ontology",
        )
        for cls_uri in self.graph.subjects(RDF.type, OWL.Class):
            info = self.class_ext.extract_info(cls_uri)
            self.classes[info.name] = info

        for p_type in [
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.TransitiveProperty,
        ]:
            for p_uri in self.graph.subjects(RDF.type, p_type):
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

    def generate_python_code_external(self, base_file_name: str) -> Dict[str, str]:
        """
        Generate Python code without saving to disk.
        :param base_file_name: Base name for the generated files.
        :return: Dictionary of filename to content.
        """
        gen = CodeGenerator(
            self.graph,
            self.classes,
            self.properties,
            getattr(self, "ontology_label", "Ontology"),
            self.predefined_data_types,
        )
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
    from krrood_experiments.helpers import generate_lubm_with_predicates

    generate_lubm_with_predicates(clean=True)
    # generate_owl2bench_with_predicates(clean=False)
