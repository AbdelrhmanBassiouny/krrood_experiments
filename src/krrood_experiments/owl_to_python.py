import os
import re
from collections import defaultdict
from copy import copy, deepcopy
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


class NamingRegistry:
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
    def __init__(self, graph: rdflib.Graph):
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
    def __init__(self, graph: rdflib.Graph, metadata_extractor: MetadataExtractor):
        self.graph = graph
        self.metadata_extractor = metadata_extractor

    def extract_info(self, class_uri: Any) -> Dict[str, Any]:
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

        return {
            "name": class_name,
            "uri": str(class_uri),
            "superclasses": unique_superclasses or ["Symbol"],
            "label": label,
            "comment": self.metadata_extractor.get_comment(class_uri),
            "add_role_taker": True,
        }


class PropertyExtractor:
    def __init__(self, graph: rdflib.Graph, metadata_extractor: MetadataExtractor):
        self.graph = graph
        self.metadata_extractor = metadata_extractor

    def extract_info(self, property_uri: Any) -> Dict[str, Any]:
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

        return {
            "name": prop_local,
            "uri": str(property_uri),
            "type": prop_type,
            "domains": domains,
            "ranges": ranges,
            "range_uris": range_uris,
            "label": self.metadata_extractor.get_label(property_uri),
            "comment": self.metadata_extractor.get_comment(property_uri),
            "field_name": NamingRegistry.to_snake_case(prop_local),
            "descriptor_name": NamingRegistry.to_pascal_case(prop_local),
            "superproperties": superproperties,
            "inverses": sorted(set(inverses)),
            "inverse_of": inverse_of,
            "is_transitive": is_transitive,
            "is_specialized": False,
        }


class OntologyLoader:
    def __init__(self, graph: Optional[rdflib.Graph] = None):
        self.graph = graph if graph is not None else rdflib.Graph()

    def load(self, owl_file_path: str) -> rdflib.Graph:
        """Load OWL file using RDFLib"""
        path = owl_file_path
        # If a relative path was provided and does not exist relative to CWD, try repository resources
        if not os.path.isabs(path) and not os.path.exists(path):
            repo_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "", "..", "..")
            )
            candidate = os.path.join(
                repo_root, "lubm", "resources", os.path.basename(path)
            )
            if os.path.exists(candidate):
                path = candidate
        self.graph.parse(path)
        return self.graph


class InferenceEngine:
    def __init__(self, graph: rdflib.Graph):
        self.graph = graph

    @staticmethod
    def topological_order(items: Dict[str, Dict], dep_key: str) -> List[str]:
        """Return a topological order based on dependency names in dep_key; if cycles, append remaining alphabetically."""
        remaining = {
            name: set(items[name].get(dep_key, [])) & set(items.keys())
            for name in items
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

    def compute_ancestors(self, classes: Dict[str, Dict]):
        # Compute full ancestor sets for each class (transitive closure)
        name_to_bases = {
            name: set(info["base_classes"]) for name, info in classes.items()
        }
        for name, info in classes.items():
            ancestors = set()
            stack = list(info["base_classes"])
            while stack:
                base = stack.pop()
                if base in ancestors:
                    continue
                ancestors.add(base)
                stack.extend(name_to_bases.get(base, []))
            info["all_base_classes"] = sorted(ancestors)

    def infer_properties(self, properties: Dict[str, Dict], classes: Dict[str, Dict], role_cls_name: str):
        # Infer domains and ranges using subPropertyOf, inverseOf, and restrictions
        # Initialize maps
        dom_map = {
            name: set(info.get("domains", [])) for name, info in properties.items()
        }
        rng_map = {
            name: set(info.get("ranges", [])) for name, info in properties.items()
        }
        rng_uri_map = {
            name: set(info.get("range_uris", []))
            for name, info in properties.items()
        }
        super_map = {
            name: list(info.get("superproperties", []))
            for name, info in properties.items()
        }
        inverse_pairs = []
        for name, info in properties.items():
            for inv in info.get("inverses", []) or []:
                if inv in properties:
                    inverse_pairs.append((name, inv))

        # Restriction parser helpers
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
                        for_class_info = classes.get(for_class)
                        if for_class_info:
                            for_class_info['role_taker'] = {
                                "class_name": rng_name,
                                "field_name": NamingRegistry.to_snake_case(rng_name)
                            }
                        return
                    rng_map[prop_name].add(rng_name)
                    rng_uri_map[prop_name].add(some)
                    # Track per-class restriction to specialize properties later
                    cdict = property_restrictions.setdefault(for_class, {})
                    s = cdict.setdefault(prop_name, set())
                    s.add(rng_name)
                except Exception:
                    pass

        # Track declared domains that originate explicitly (rdfs:domain) or via class restrictions only
        declared_dom_map = {
            name: set(info.get("domains", [])) for name, info in properties.items()
        }

        # Walk class restrictions
        RestrictionWalker.walk(self.graph, declared_dom_map, _handle_restriction)

        for info in classes.values():
            if "Role" in info.get("base_classes", []):
                info["base_classes"].remove("Role")
                info["base_classes"].append(role_cls_name)

        # Fixed-point propagate via subPropertyOf and inverseOf (for types/ranges)
        changed = True
        while changed:
            changed = False
            for name, supers in super_map.items():
                for sp in supers:
                    if sp not in dom_map:
                        continue
                    before_r, before_ru = (
                        len(rng_map[name]),
                        len(rng_uri_map[name]),
                    )
                    rng_map[name].update(rng_map.get(sp, set()))
                    rng_uri_map[name].update(rng_uri_map.get(sp, set()))
                    if (
                        len(rng_map[name]) != before_r
                        or len(rng_uri_map[name]) != before_ru
                    ):
                        changed = True
            for a, b in inverse_pairs:
                before_da, before_ra = len(dom_map[a]), len(rng_map[a])
                before_db, before_rb = len(dom_map[b]), len(rng_map[b])
                dom_map[a].update(rng_map.get(b, set()))
                rng_map[a].update(dom_map.get(b, set()))
                dom_map[b].update(rng_map.get(a, set()))
                rng_map[b].update(dom_map.get(a, set()))
                if (
                    len(dom_map[a]) != before_da
                    or len(rng_map[a]) != before_ra
                    or len(dom_map[b]) != before_db
                    or len(rng_map[b]) != before_rb
                ):
                    changed = True

        # Write back inferred domains/ranges
        for name, info in properties.items():
            info["domains"] = sorted(dom_map.get(name, set()))
            info["ranges"] = sorted(rng_map.get(name, set()))
            info["range_uris"] = list(rng_uri_map.get(name, set()))
            info["declared_domains"] = sorted(declared_dom_map.get(name, set()))

        return property_restrictions

    def create_specialized_properties(self, properties: Dict[str, Dict], property_restrictions: Dict[str, Dict[str, set]], original_properties: Dict[str, Dict]):
        specialized_props: Dict[str, Dict] = {}
        for cls_name, props in property_restrictions.items():
            for prop_name, rng_names in props.items():
                base = properties.get(prop_name)
                if not base or base.get("type") != "ObjectProperty":
                    continue
                if rng_names.issubset(
                    set(original_properties[prop_name].get("ranges", []))
                ):
                    continue
                base_dd = list(base.get("declared_domains", []))
                if cls_name in base_dd:
                    base_dd.remove(cls_name)
                    base["declared_domains"] = base_dd
                for rng_name in sorted(rng_names):
                    spec_key = prop_name + "{" + rng_name + "}"
                    if spec_key in properties or spec_key in specialized_props:
                        continue
                    spec = {
                        "name": prop_name,
                        "uri": base.get("uri", ""),
                        "type": "ObjectProperty",
                        "domains": [cls_name],
                        "ranges": [rng_name],
                        "range_uris": [],
                        "label": base.get("label"),
                        "comment": base.get("comment"),
                        "field_name": base.get("field_name"),
                        "descriptor_name": NamingRegistry.to_pascal_case(
                            base.get("descriptor_name", prop_name)
                        ),
                        "superproperties": [prop_name],
                        "inverses": [],
                        "inverse_of": None,
                        "is_transitive": base.get("is_transitive", False),
                        "declared_domains": [cls_name],
                        "is_specialized": True,
                    }
                    specialized_props[spec_key] = spec
        properties.update(specialized_props)


    def apply_predefined_overrides(self, classes: Dict[str, Dict], properties: Dict[str, Dict], predefined_data_types: Dict[str, Dict[str, str]]):
        for cls_name, overrides in (predefined_data_types or {}).items():
            for field_snake, py_type in overrides.items():
                target_prop_name = None
                for prop_name, p in properties.items():
                    if p.get("field_name") == field_snake:
                        target_prop_name = prop_name
                        break
                if not target_prop_name:
                    logger.info(f"[owl_to_python] Override not applied: property '{field_snake}' not found")
                    continue
                p = properties[target_prop_name]
                p["type"] = "DataProperty"
                p["data_type_hint_inner"] = py_type
                p["_predefined_data_type"] = True
                ov = set(p.get("_overrides_for", []))
                ov.add(cls_name)
                p["_overrides_for"] = sorted(ov)
                dd = list(p.get("declared_domains", []))
                if cls_name not in dd:
                    dd.append(cls_name)
                p["declared_domains"] = dd
                logger.info(f"[owl_to_python] Applied override: {cls_name}.{field_snake} -> {py_type}")

    def compute_type_hints(self, classes: Dict[str, Dict], properties: Dict[str, Dict]):
        xsd_to_py = {
            XSD.string: "str", XSD.normalizedString: "str", XSD.token: "str", XSD.language: "str",
            XSD.boolean: "bool", XSD.decimal: "float", XSD.float: "float", XSD.double: "float",
            XSD.integer: "int", XSD.nonPositiveInteger: "int", XSD.negativeInteger: "int",
            XSD.long: "int", XSD.int: "int", XSD.short: "int", XSD.byte: "int",
            XSD.nonNegativeInteger: "int", XSD.unsignedLong: "int", XSD.unsignedInt: "int",
            XSD.unsignedShort: "int", XSD.unsignedByte: "int", XSD.positiveInteger: "int",
            XSD.date: "str", XSD.dateTime: "str", XSD.time: "str", XSD.anyURI: "str",
        }
        ancestors_map = {name: set(info["all_base_classes"]) for name, info in classes.items()}
        for name, info in properties.items():
            bases: List[str] = []
            for sp in info.get("superproperties", []):
                if sp in properties:
                    bases.append(properties[sp]["descriptor_name"])
            if not bases:
                bases.append("PropertyDescriptor")
            if info["is_transitive"]:
                bases.append("TransitiveProperty")
            if info["inverse_of"]:
                bases.append("HasInverseProperty")
            info["base_descriptors"] = bases

            if info["type"] == "ObjectProperty":
                ranges = list(info.get("ranges", []))
                if ranges:
                    rng_set = set(ranges)
                    simplified = []
                    for r in sorted(rng_set):
                        r_ancestors = ancestors_map.get(r, set())
                        if any(a in rng_set for a in r_ancestors):
                            continue
                        simplified.append(r)
                    ranges = simplified or ranges
                if len(ranges) > 1:
                    info["object_range_hint"] = "Union[" + ", ".join(sorted(set(ranges))) + "]"
                elif len(ranges) == 1:
                    info["object_range_hint"] = ranges[0]
                else:
                    logger.warning(f"[owl_to_python]: Could not infer object range type for property '{name}'. Using Any.")
                    info["object_range_hint"] = "Any"
            else:
                if info.get("_predefined_data_type") and info.get("data_type_hint_inner"):
                    continue
                py_types: List[str] = []
                for uri in info.get("range_uris", []) or []:
                    try:
                        if isinstance(uri, rdflib.URIRef) and uri in xsd_to_py:
                            py_types.append(xsd_to_py[uri])
                    except Exception: pass
                if not py_types:
                    textual = [r.lower() for r in info.get("ranges", [])]
                    for t in textual:
                        if t in ("string", "normalizedstring", "token", "language", "anyuri", "datetime", "date", "time"): py_types.append("str")
                        elif t in ("integer", "int", "long", "short", "byte", "nonnegativeinteger", "positiveinteger", "unsignedlong", "unsignedint", "unsignedshort", "unsignedbyte"): py_types.append("int")
                        elif t in ("float", "double", "decimal"): py_types.append("float")
                        elif t in ("boolean",): py_types.append("bool")
                    if not py_types:
                        logger.warning(f"[owl_to_python]: Could not infer data type for property '{name}'. Using Any.")
                        py_types.append("Any")
                seen = set()
                py_types_unique = []
                for t in py_types:
                    if t not in seen:
                        py_types_unique.append(t)
                        seen.add(t)
                if len(py_types_unique) > 1:
                    info["data_type_hint_inner"] = "Union[" + ", ".join(py_types_unique) + "]"
                else:
                    info["data_type_hint_inner"] = py_types_unique[0]
        return ancestors_map

    def find_implicit_subtypes(self, classes: Dict[str, Dict], properties: Dict[str, Dict], ancestors_map: Dict, ontology_base_class_name: str, role_cls_name: str):
        for parent_cls_name, parent_cls_info in classes.items():
            parent_props_names = parent_cls_info.get("declared_properties", [])
            parent_props_names_filtered = {prop.split("{")[0] for prop in parent_props_names}
            for child_cls_name, child_cls_info in classes.items():
                if parent_cls_name == child_cls_name: continue
                if parent_cls_name in child_cls_info.get("all_base_classes_including_role_takers", []): continue
                if child_cls_name in parent_cls_info.get("all_base_classes_including_role_takers", []): continue
                child_props_names = child_cls_info.get("declared_properties", [])
                child_props_names_filtered = {prop.split("{")[0] for prop in child_props_names}
                matched_prop_names = parent_props_names_filtered.intersection(child_props_names_filtered)
                for parent_prop_name in parent_props_names:
                    for child_prop_name in child_props_names:
                        child_prop_info = properties.get(child_prop_name)
                        parent_prop_info = properties.get(parent_prop_name)
                        parent_prop_filtered_name = parent_prop_name.split("{")[0]
                        if not child_prop_info or not parent_prop_info: continue
                        if child_prop_info["type"] == "DataProperty" or parent_prop_info["type"] == "DataProperty": continue
                        if parent_prop_filtered_name not in child_prop_info["all_superproperties"]: continue
                        child_prop_range = child_prop_info["object_range_hint"]
                        parent_prop_range = parent_prop_info["object_range_hint"]
                        if parent_prop_range not in ancestors_map.get(child_prop_range, set()):
                            if parent_prop_filtered_name in matched_prop_names: matched_prop_names.remove(parent_prop_filtered_name)
                            continue
                        matched_prop_names.add(parent_prop_filtered_name)
                if not matched_prop_names: continue
                if matched_prop_names == parent_props_names_filtered:
                    if "role_taker" in parent_cls_info and parent_cls_info["role_taker"]:
                        if "role_taker" in child_cls_info and child_cls_info["role_taker"]:
                            if child_cls_info["role_taker"]["class_name"] != parent_cls_info["role_taker"]["class_name"]: continue
                        else: continue
                    subsumption_type = SubsumptionType.SUBTYPE
                else:
                    subsumption_type = SubsumptionType.ROLE
                if not matched_prop_names: continue
                child_info = classes[child_cls_name]
                parent_info = classes[parent_cls_name]
                if ontology_base_class_name in child_info["base_classes"]: child_info["base_classes"].remove(ontology_base_class_name)
                if subsumption_type == SubsumptionType.ROLE:
                    child_info["role_taker"] = {"class_name": parent_cls_name, "field_name": NamingRegistry.to_snake_case(parent_cls_name)}
                    if role_cls_name not in child_info["all_base_classes"]:
                        child_info["base_classes"] = [role_cls_name] + child_info["base_classes"]
                        child_info["all_base_classes"] = [role_cls_name] + child_info["all_base_classes"]
                    child_info["all_base_classes_including_role_takers"].append(parent_cls_name)
                else:
                    child_info["base_classes"] = []
                    if parent_cls_name not in child_info["base_classes"]:
                        child_info["base_classes"].append(parent_cls_name)
                        child_info["all_base_classes"].append(parent_cls_name)
                        child_info["all_base_classes_including_role_takers"].append(parent_cls_name)
                    for prop in copy(child_info["declared_properties"]):
                        if prop in parent_info["declared_properties"]: child_info["declared_properties"].remove(prop)

class JinjaRenderer:
    def __init__(self, template_dir: str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)


class RestrictionWalker:
    @staticmethod
    def walk(
        graph: rdflib.Graph,
        declared_dom_map: Optional[Dict[str, set]] = None,
        restrictions_handler: Optional[Callable] = None,
    ):
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
                    declared_dom_map[NamingRegistry.uri_to_python_name(on_prop)].add(cls_name)

            # restrictions inside intersectionOf
            for coll in graph.objects(cls_uri, OWL.intersectionOf):
                node = coll
                while node and node != RDF.nil:
                    first = graph.value(node, RDF.first)
                    if restrictions_handler:
                        restrictions_handler(cls_name, first)
                    on_prop = graph.value(first, OWL.onProperty) if first else None
                    if on_prop:
                        declared_dom_map[NamingRegistry.uri_to_python_name(on_prop)].add(
                            cls_name
                        )
                    node = graph.value(node, RDF.rest)


class CodeGenerator:
    def __init__(self, graph: rdflib.Graph, classes: Dict, properties: Dict, ontology_label: str, predefined_data_types: Dict):
        self.graph = graph
        self.classes = classes
        self.properties = properties
        self.ontology_label = ontology_label
        self.predefined_data_types = predefined_data_types
        self.engine = InferenceEngine(graph)
        self.renderer = JinjaRenderer(os.path.dirname(__file__))

    def generate(self, base_file_name: str) -> Dict[str, str]:
        """Generate Python code using the external Jinja2 template with proper class/property inheritance."""
        classes_copy: Dict[str, Dict] = {name: dict(info) for name, info in self.classes.items()}
        properties_copy: Dict[str, Dict] = {name: dict(info) for name, info in self.properties.items()}
        original_properties = {name: dict(info) for name, info in self.properties.items()}

        ontology_base_class_name = NamingRegistry.to_pascal_case(
            re.sub(r"\W+", " ", self.ontology_label).strip()
        )
        if not ontology_base_class_name.endswith("Ontology"):
            ontology_base_class_name += "Ontology"
        
        role_cls_name = "Role"

        # We need synthetic base class before some inference steps
        if ontology_base_class_name not in classes_copy:
            classes_copy[ontology_base_class_name] = {
                "name": ontology_base_class_name, "uri": "", "superclasses": ["Symbol", "ABC"],
                "base_classes": ["Symbol", "ABC"], "label": f"Base class for {self.ontology_label}", "comment": None,
            }

        # Initial class prep
        for name, info in classes_copy.items():
            if name == ontology_base_class_name: continue
            info["base_classes"] = [b for b in info.get("superclasses", []) if b != "Symbol"]
            if not info["base_classes"]: info["base_classes"] = [ontology_base_class_name]
            elif len(info["base_classes"]) == 1 and info["base_classes"][0] == role_cls_name:
                info["base_classes"].append("Symbol")
        
        self.engine.compute_ancestors(classes_copy)
        
        property_restrictions = self.engine.infer_properties(properties_copy, classes_copy, role_cls_name)
        self.engine.create_specialized_properties(properties_copy, property_restrictions, original_properties)

        if "uri" not in properties_copy:
            properties_copy["uri"] = {
                "name": "uri", "uri": "", "type": "DataProperty", "domains": [ontology_base_class_name],
                "ranges": ["str"], "range_uris": [XSD.anyURI], "label": "URI of the ontology element",
                "comment": "The unique resource identifier (URI) of the ontology element.", "field_name": "uri",
                "descriptor_name": "Uri", "superproperties": [], "inverses": [], "inverse_of": None,
                "is_transitive": False, "declared_domains": [ontology_base_class_name], "is_specialized": False,
            }

        for info in properties_copy.values():
            if info.get("type") == "DataProperty" and not info.get("declared_domains"):
                info["declared_domains"] = [ontology_base_class_name]

        self.engine.apply_predefined_overrides(classes_copy, properties_copy, self.predefined_data_types)
        ancestors_map = self.engine.compute_type_hints(classes_copy, properties_copy)

        # Decide which properties to declare on each class
        for cls_name, cls_info in classes_copy.items():
            ancestors = set(cls_info.get("all_base_classes", []))
            declared: List[str] = []
            for prop_name, p in properties_copy.items():
                if prop_name == "roleFor": continue
                declared_domains = p.get("declared_domains", [])
                domains = p.get("domains", [])
                applies_to_cls = cls_name in (declared_domains or domains)
                if not applies_to_cls: continue
                overrides_for = set(p.get("_overrides_for", []))
                skip = False
                if ancestors and cls_name not in overrides_for:
                    for a in ancestors:
                        if a in (declared_domains or domains):
                            skip = True; break
                if not skip:
                    if p["is_specialized"]:
                        for super_prop in p.get("superproperties", []):
                            if super_prop in declared: declared.remove(super_prop)
                    declared.append(prop_name)
            cls_info["declared_properties"] = declared

        for name, info in properties_copy.items():
            info["all_superproperties"] = self._compute_transitive_closure(info["superproperties"], properties_copy, "superproperties")

        for name, info in classes_copy.items():
            initial = set(info["all_base_classes"])
            if "role_taker" in info and info["role_taker"]: initial.add(info["role_taker"]["class_name"])
            info["all_base_classes_including_role_takers"] = self._compute_transitive_closure(list(initial), classes_copy, "all_base_classes", "role_taker")

        self.engine.find_implicit_subtypes(classes_copy, properties_copy, ancestors_map, ontology_base_class_name, role_cls_name)

        for cls_name, cls_info in classes_copy.items():
            cls_info["base_classes_for_topological_sort"] = cls_info["base_classes"][:]
            if "role_taker" in cls_info and cls_info["role_taker"]:
                cls_info["base_classes_for_topological_sort"].append(cls_info["role_taker"]["class_name"])
        
        classes_order = self.engine.topological_order(classes_copy, dep_key="base_classes_for_topological_sort")
        property_classes = {k: v for k, v in properties_copy.items() if not v["is_specialized"]}
        properties_order = self.engine.topological_order(property_classes, dep_key="superproperties")

        index_map = {name: idx for idx, name in enumerate(properties_order)}
        for name, info in property_classes.items():
            inv = info.get("inverse_of")
            info["inverse_target_is_prior"] = inv in property_classes and index_map.get(inv, 10**9) < index_map.get(name, 10**9)

        classes_for_stubs = deepcopy(classes_copy)
        for cls_name, info in classes_copy.items():
            if role_cls_name in info["base_classes"]:
                info["base_classes"].remove(role_cls_name)
                info["base_classes"] = [f"{role_cls_name}[{info['role_taker']['class_name']}]"] + info["base_classes"]
                classes_for_stubs[cls_name]["base_classes"].remove(role_cls_name)
            else:
                info["add_role_taker"] = False
                classes_for_stubs[cls_name]["add_role_taker"] = False
        
        if "Role" in classes_copy: del classes_copy["Role"]
        if "Role" in classes_order: classes_order.remove("Role")

        properties_file_name = f"{base_file_name}_properties.py"
        ontology_base_file_name = f"{base_file_name}_base.py"
        classes_file_name = f"{base_file_name}.py"
        stub_file_name = f"{base_file_name}.pyi"

        properties_module_name = properties_file_name.replace(".py", "")
        ontology_module_name = ontology_base_file_name.replace(".py", "")

        properties_file = self.renderer.render("onto_properties.j2", properties=properties_copy, properties_order=properties_order)
        ontology_base_file = self.renderer.render("onto_base.j2", cls=classes_copy[ontology_base_class_name], properties=properties_copy)
        classes_file = self.renderer.render("onto_classes.j2", ontology_base_module_name=ontology_module_name, properties_module_name=properties_module_name,
                                       classes=classes_copy, properties=properties_copy, classes_order=classes_order, properties_order=properties_order,
                                       ontology_base_class_name=ontology_base_class_name)
        role_takers = list(OrderedSet([c["role_taker"]["class_name"] for c in classes_copy.values() if "role_taker" in c and c["role_taker"]]))
        stub_file = self.renderer.render("onto_stubs.j2", ontology_base_module_name=ontology_module_name, properties_module_name=properties_module_name,
                                    role_takers=role_takers, classes=classes_for_stubs, properties=properties_copy, classes_order=classes_order,
                                    ontology_base_class_name=ontology_base_class_name)

        return {properties_file_name: properties_file, ontology_base_file_name: ontology_base_file, classes_file_name: classes_file, stub_file_name: stub_file}

    def _compute_transitive_closure(self, initial_elements: List[str], items_map: Dict[str, Dict], dep_key: str, role_taker_key: Optional[str] = None) -> List[str]:
        closure = set()
        stack = list(initial_elements)
        while stack:
            curr = stack.pop()
            if curr in closure: continue
            closure.add(curr)
            if curr in items_map:
                stack.extend(items_map[curr].get(dep_key, []))
                if role_taker_key and role_taker_key in items_map[curr] and items_map[curr][role_taker_key]:
                    stack.append(items_map[curr][role_taker_key]["class_name"])
        return sorted(closure)


class OwlToPythonConverter:
    def __init__(self, predefined_data_types: Dict[str, Dict[str, str]] | None = None):
        self.graph = rdflib.Graph()
        self.classes = {}
        self.properties = {}
        self.predefined_data_types: Dict[str, Dict[str, str]] = predefined_data_types or {}
        self.metadata_extractor = MetadataExtractor(self.graph)
        self.class_extractor = ClassExtractor(self.graph, self.metadata_extractor)
        self.property_extractor = PropertyExtractor(self.graph, self.metadata_extractor)
        self.loader = OntologyLoader(self.graph)

    def load_ontology(self, owl_file_path: str):
        """Load OWL file using RDFLib"""
        self.loader.load(owl_file_path)
        self._extract_ontology_info()

    def _extract_ontology_info(self):
        """Extract classes, properties, and ontology metadata from ontology"""
        ontology_label = None
        for onto in self.graph.subjects(RDF.type, OWL.Ontology):
            ontology_label = self.metadata_extractor.get_label(onto)
            if ontology_label:
                break
        self.ontology_label = ontology_label or "Ontology"

        for cls in self.graph.subjects(RDF.type, OWL.Class):
            class_info = self.class_extractor.extract_info(cls)
            self.classes[class_info["name"]] = class_info

        for cls_name, cls_info in self.classes.items():
            if ("role_taker" not in cls_info) or (not cls_info["role_taker"]):
                continue
            if any(
                cls_info["role_taker"][0] in self.classes[sc]["role_taker"]
                for sc in cls_info["superclasses"]
                if sc in self.classes
            ):
                cls_info["role_taker"] = []

        for prop_type in [OWL.ObjectProperty, OWL.DatatypeProperty, OWL.TransitiveProperty]:
            for prop in self.graph.subjects(RDF.type, prop_type):
                prop_info = self.property_extractor.extract_info(prop)
                existing = self.properties.get(prop_info["name"])
                if existing:
                    if prop_type == OWL.TransitiveProperty:
                        existing["is_transitive"] = True
                    if not existing.get("inverse_of"):
                        existing["inverse_of"] = prop_info.get("inverse_of")
                    for k in ("domains", "ranges", "range_uris", "superproperties", "inverses"):
                        if k in prop_info:
                            existing[k] = sorted(set(existing.get(k, [])) | set(prop_info.get(k, [])))
                else:
                    self.properties[prop_info["name"]] = prop_info

    def generate_python_code_external(self, base_file_name: str) -> Dict[str, str]:
        """Generate Python code using CodeGenerator"""
        generator = CodeGenerator(self.graph, self.classes, self.properties, getattr(self, "ontology_label", "Ontology"), self.predefined_data_types)
        return generator.generate(base_file_name)

    def save_to_file(self, output_path: str):
        """Generate and save Python code to file"""
        base_file_name = os.path.splitext(os.path.basename(output_path))[0]
        dir_name = os.path.dirname(output_path)
        file_name_map = self.generate_python_code_external(base_file_name)
        for file_name, file_content in file_name_map.items():
            with open(os.path.join(dir_name, file_name), "w", encoding="utf-8") as f:
                f.write(file_content)
        logger.info(f"Generated Python classes saved to: {output_path}")


# Usage
if __name__ == "__main__":
    from krrood_experiments.helpers import generate_lubm_with_predicates

    generate_lubm_with_predicates(clean=True)
    # generate_owl2bench_with_predicates(clean=False)
