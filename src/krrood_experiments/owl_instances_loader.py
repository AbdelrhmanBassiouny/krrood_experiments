from __future__ import annotations

from collections import defaultdict
from dataclasses import fields, is_dataclass
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

import rdflib
from krrood.class_diagrams.class_diagram import Association, ClassDiagram
from krrood.entity_query_language.predicate import Symbol
from krrood.entity_query_language.symbol_graph import SymbolGraph
from krrood.ontomatic.property_descriptor.attribute_introspector import (
    DescriptorAwareIntrospector,
)
from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.ormatic.utils import classes_of_module
from krrood.utils import inheritance_path_length
from rdflib import RDF, URIRef, Literal


class OwlInstancesRegistry:
    """Registry of instances created from an OWL/RDF instances file.

    Provides access to instances per Python model class and tracks URIRef to instance mapping.
    """

    def __init__(self, symbol_graph: Optional[SymbolGraph] = None) -> None:
        self._by_uri: Dict[URIRef, List[Any]] = defaultdict(list)
        self._by_class: Dict[Type, List[Any]] = {}

    def get_or_create_for(
        self, uri: URIRef, factory: Type, symbol_graph, *args, **kwargs
    ) -> Any:
        instances = self.resolve(uri)
        if (instances is None) or (
            not any(isinstance(inst, factory) for inst in instances)
        ):
            # kwargs["uri"] = str(uri)
            role_taker_association, role_taker = get_and_construct_role_taker(
                factory, uri, symbol_graph, **kwargs
            )
            if role_taker_association:
                kwargs[role_taker_association.field.public_name] = role_taker
            inst = factory(*args, **kwargs)

            # Fill a best-effort human-readable name if available
            # local = local_name(uri)
            local = str(uri)
            if hasattr(inst, "uri"):
                if getattr(inst, "uri") is None:
                    setattr(inst, "uri", local)
                for k, v in kwargs.items():
                    if hasattr(v, "uri") and getattr(v, "uri") is None:
                        setattr(v, "uri", local)
            self._by_uri[uri].append(inst)
            self._by_class.setdefault(factory, []).append(inst)
        else:
            inst = [i for i in instances if isinstance(i, factory)][0]
        return inst

    def get(self, cls: Type) -> List[Any]:
        return list(self._by_class.get(cls, []))

    def resolve(self, uri: URIRef) -> Optional[Any]:
        if isinstance(uri, str):
            uri = URIRef(uri)
        return self._by_uri.get(uri)


def local_name(uri: Union[str, URIRef]) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    return s.rstrip("/").rsplit("/", 1)[-1]


def to_snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and (not name[i - 1].isupper()):
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def to_pascal(name: str) -> str:
    parts = []
    cur = []
    for ch in name:
        if ch == "_":
            if cur:
                parts.append("".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return "".join(p.capitalize() for p in parts)


class ModelMetadata:
    def __init__(self, model_modules: Union[ModuleType, Iterable[ModuleType]]):
        self.class_by_name: Dict[str, Type] = {}
        self.descriptor_by_name: Dict[str, Type] = {}
        self.field_by_predicate_local: Dict[Type, Dict[str, str]] = {}
        self.field_by_descriptor: Dict[Type, Dict[Type, str]] = {}
        self._collect(model_modules)

    def _collect(self, model_modules: Union[ModuleType, Iterable[ModuleType]]):
        if isinstance(model_modules, (ModuleType, type)):
            model_modules = [model_modules]
        for model_module in model_modules:
            # Collect model classes (dataclasses used to represent OWL classes)
            for attr_name in dir(model_module):
                obj = getattr(model_module, attr_name)
                if isinstance(obj, type) and is_dataclass(obj):
                    self.class_by_name[attr_name] = obj
                # Collect descriptor classes available in the module for quick lookup by name
                if isinstance(obj, type):
                    try:
                        if (
                            issubclass(obj, PropertyDescriptor)
                            and obj is not PropertyDescriptor
                        ):
                            self.descriptor_by_name[obj.__name__] = obj
                    except TypeError:
                        # obj is not a class we can check issubclass on
                        pass

        # For each model class, map predicate local names to attribute names and descriptors to attributes
        for _, cls in list(self.class_by_name.items()):
            pred_map: Dict[str, str] = {}
            desc_map: Dict[Type, str] = {}

            # Descriptors are class attributes, not dataclass fields. Iterate attributes and
            # pick those that are instances of PropertyDescriptor (including subclasses).
            for attr in dir(cls):
                if attr.startswith("_"):
                    continue
                val = getattr(cls, attr)
                if isinstance(val, PropertyDescriptor):
                    # Map snake local predicate name to the class attribute name
                    pred_map.setdefault(attr, attr)
                    # Map descriptor class to attribute name for inverse lookups
                    desc_map[type(val)] = attr

            self.field_by_predicate_local[cls] = pred_map
            self.field_by_descriptor[cls] = desc_map

    def get_python_class(self, rdf_class: URIRef) -> Optional[Type]:
        name = local_name(rdf_class)
        # Expect PascalCase names in model equal to RDF local name
        return self.class_by_name.get(name)

    def get_field_name(self, cls: Type, snake_name: str) -> Optional[str]:
        return self.field_by_predicate_local.get(cls, {}).get(snake_name)

    def get_descriptor_base(
        self, pred_local: str
    ) -> Optional[Type[PropertyDescriptor]]:
        return self.descriptor_by_name.get(to_pascal(pred_local))


class OwlLoader:
    def __init__(
        self,
        owl_path: str,
        model_modules: Union[ModuleType, Iterable[ModuleType]],
        symbol_graph: SymbolGraph,
        registry: OwlInstancesRegistry,
    ):
        self.owl_path = owl_path
        self.model_modules = model_modules
        self.symbol_graph = symbol_graph
        self.registry = registry
        self.metadata = ModelMetadata(model_modules)
        self.graph = rdflib.Graph()

    def load(self) -> OwlInstancesRegistry:
        self.graph.parse(self.owl_path)
        self._create_explicit_instances()
        self._assign_all_properties()
        return self.registry

    def _create_explicit_instances(self):
        for s, _, o_class in self.graph.triples((None, RDF.type, None)):
            if not isinstance(s, URIRef):
                continue
            py_cls = self.metadata.get_python_class(o_class)
            if py_cls is None:
                continue
            existing_roles = self.registry.resolve(s)
            kwargs = self._get_common_role_taker_kwargs(existing_roles, py_cls)
            self.registry.get_or_create_for(s, py_cls, self.symbol_graph, **kwargs)

    def _get_common_role_taker_kwargs(
        self, existing_roles: Optional[List[Any]], target_cls: Type
    ) -> Dict[str, Any]:
        kwargs = {}
        if existing_roles:
            for er in existing_roles:
                (
                    assoc1,
                    assoc2,
                ) = self.symbol_graph.class_diagram.get_common_role_taker_associations(
                    type(er), target_cls
                )
                if assoc1 and assoc2:
                    if assoc2.field.public_name not in kwargs:
                        kwargs[assoc2.field.public_name] = getattr(
                            er, assoc1.field.public_name
                        )
        return kwargs

    def _ensure_instance(self, uri: URIRef) -> Optional[List[Any]]:
        inst = self.registry.resolve(uri)
        if inst is not None:
            return inst
        # Try to infer class from rdf:type triples
        for _, _, o_class in self.graph.triples((uri, RDF.type, None)):
            py_cls = self.metadata.get_python_class(o_class)
            if py_cls is not None:
                return [self.registry.get_or_create_for(uri, py_cls, self.symbol_graph)]
        return None

    def _assign_all_properties(self):
        for s, p, o in self.graph:
            if p == RDF.type:
                continue
            if not isinstance(s, URIRef):
                continue
            subj_roles = self.registry.resolve(s)
            if subj_roles is None:
                # Subject without explicit type known to model; try infer
                subj_roles = self._ensure_instance(s)
                if subj_roles is None:
                    continue
            subj = subj_roles[0]
            pred_local = local_name(p)
            snake = to_snake(pred_local)
            subj_cls = type(subj)

            # Determine the appropriate field name on the subject
            field_name = self.metadata.get_field_name(subj_cls, snake)
            if not field_name:
                if snake in [f.name for f in fields(subj_cls)]:
                    field_name = snake
                elif hasattr(subj, snake):
                    field_name = snake

            role_taker_association = (
                self.symbol_graph.class_diagram.get_role_taker_associations_of_cls(
                    subj_cls
                )
            )
            role_taker_val = (
                getattr(subj, role_taker_association.field.public_name, None)
                if role_taker_association
                else None
            )

            if isinstance(o, Literal):
                self._assign_data_property(
                    subj, subj_cls, field_name, snake, role_taker_val, o
                )
            else:
                self._assign_object_property(
                    subj, subj_cls, field_name, snake, role_taker_val, p, o
                )

    def _assign_data_property(
        self, subj, subj_cls, field_name, snake, role_taker_val, literal
    ):
        if field_name and hasattr(subj, field_name):
            # Coerce to field annotated type
            try:
                ftypes = {f.name: f.type for f in fields(subj_cls)}
            except TypeError:
                ftypes = {}
            coerced = _coerce_literal(literal, ftypes.get(field_name))
            setattr(subj, field_name, coerced)
        elif role_taker_val and hasattr(role_taker_val, snake):
            setattr(role_taker_val, snake, literal)

    def _assign_object_property(
        self, subj, subj_cls, field_name, snake, role_taker_val, pred_uri, obj_node
    ):
        obj_roles = (
            self._ensure_instance(obj_node) if isinstance(obj_node, URIRef) else None
        )
        obj = obj_roles[0] if obj_roles else None

        if field_name and hasattr(subj, field_name):
            class_diagram = self.symbol_graph.class_diagram
            matching_assocs = [
                assoc.field
                for assoc in class_diagram.associations
                if assoc.field.public_name == field_name
            ]
            if matching_assocs:
                subj_wrapped_field = matching_assocs[0]
                req_obj_type = subj_wrapped_field.type_endpoint
                matched_obj = self._get_matching_role(obj_roles, req_obj_type)

                if matched_obj:
                    obj = matched_obj
                
                lst = getattr(subj, field_name, None)
                if obj is not None:
                    if hasattr(lst, "add"):
                        lst.add(obj)
                    else:
                        setattr(subj, field_name, obj)
                    return

        if role_taker_val and hasattr(role_taker_val, snake):
            lst = getattr(role_taker_val, snake)
            if obj is not None:
                if hasattr(lst, "add"):
                    lst.add(obj)
                else:
                    setattr(role_taker_val, snake, obj)
                return

        self._handle_descriptor_based_property(subj, subj_cls, pred_uri, snake, obj)

    def _get_matching_role(
        self, roles: Optional[List[Any]], target_type: Type
    ) -> Optional[Any]:
        if not roles:
            return None
        for role in roles:
            if issubclass(type(role), target_type):
                return role

        # Try to find via role-taker chain
        obj_role = roles[0]
        role_taker_assoc = (
            self.symbol_graph.class_diagram.get_role_taker_associations_of_cls(
                type(obj_role)
            )
        )
        while role_taker_assoc:
            if role_taker_assoc.target.clazz is target_type:
                return getattr(obj_role, role_taker_assoc.field.public_name)
            else:
                obj_role = getattr(obj_role, role_taker_assoc.field.public_name)
                role_taker_assoc = (
                    self.symbol_graph.class_diagram.get_role_taker_associations_of_cls(
                        role_taker_assoc.target.clazz
                    )
                )
        return None

    def _handle_descriptor_based_property(self, subj, subj_cls, pred_uri, snake, obj):
        base_desc = self.metadata.get_descriptor_base(snake)
        if base_desc is not None:
            possible_roles = list(PropertyDescriptor.all_domains[base_desc])
            if len(possible_roles) == 1:
                new_role_class = possible_roles[0]
            else:
                o_type = type(obj)
                wrapped_field_types = {}
                chosen_role = None
                for pr in possible_roles:
                    try:
                        pr_wrapped_field = getattr(pr, snake)
                    except AttributeError:
                        continue
                    if issubclass(o_type, pr_wrapped_field.range):
                        wrapped_field_types[pr] = pr_wrapped_field.range
                # choose the nearest wrapped field type
                if wrapped_field_types:
                    chosen_role = min(
                        wrapped_field_types.keys(),
                        key=lambda k: inheritance_path_length(
                            wrapped_field_types[k], o_type
                        ),
                    )
                if chosen_role is None:
                    raise ValueError(
                        f"Could not determine role for {obj} ({o_type}) and predicate {pred_uri} ({base_desc})"
                    )
                new_role_class = chosen_role

            s_uri = subj.uri
            existing_roles = self.registry.resolve(s_uri)
            new_role = None
            for er in existing_roles:
                if type(er) is new_role_class:
                    new_role = er
                    break
            if new_role is None:
                kwargs = self._get_common_role_taker_kwargs([subj], new_role_class)
                role_taker_inst = next(iter(kwargs.values()), None) if kwargs else None

                if role_taker_inst is None:
                    uri = s_uri
                else:
                    uri = getattr(role_taker_inst, "uri", s_uri)

                new_role = self.registry.get_or_create_for(
                    URIRef(uri) if isinstance(uri, str) else uri,
                    new_role_class,
                    self.symbol_graph,
                    **kwargs,
                )
            if hasattr(new_role, snake):
                lst = getattr(new_role, snake)
                if obj is not None:
                    if hasattr(lst, "add"):
                        lst.add(obj)
                    else:
                        setattr(new_role, snake, obj)
                    return

        raise ValueError(f"Could not assign {obj} to {subj} ({pred_uri})")


def _coerce_literal(val: Literal, target_type: Optional[Type]) -> Any:
    if target_type is None:
        return val.toPython()
    try:
        # Unwrap Optional[T]
        origin = getattr(target_type, "__origin__", None)
        if origin is Union:
            args = [
                a for a in getattr(target_type, "__args__", ()) if a is not type(None)
            ]  # noqa: E721
            if args:
                target_type = args[0]
        if target_type in (str, int, float, bool):
            return target_type(val.toPython())
    except Exception:
        pass
    return val.toPython()


def load_multi_file_instances(
    owl_paths: Iterable[str],
    classes_module: Union[str, ModuleType],
    properties_module: Union[str, ModuleType],
) -> OwlInstancesRegistry:
    """Load OWL/RDF instances into the provided generated Python model module."""
    combined_registry = OwlInstancesRegistry()

    # Create symbol graph once
    model_modules = [classes_module, properties_module]
    model_modules = [
        (__import__(m, fromlist=["*"]) if isinstance(m, str) else m)
        for m in model_modules
    ]

    SymbolGraph().clear()
    classes = set()
    for model_module in model_modules:
        classes.update(classes_of_module(model_module))
    class_diagram = ClassDiagram(
        list(classes), introspector=DescriptorAwareIntrospector()
    )
    symbol_graph = SymbolGraph(_class_diagram=class_diagram)

    for path in owl_paths:
        load_instances(
            path,
            classes_module,
            properties_module,
            symbol_graph=symbol_graph,
            registry=combined_registry,
        )
    return combined_registry


def get_and_construct_role_taker(
    cls_: Type, uri_ref: URIRef, symbol_graph: SymbolGraph, **kwargs
) -> Tuple[Optional[Association], Optional[Symbol]]:
    role_taker_association = (
        symbol_graph.class_diagram.get_role_taker_associations_of_cls(cls_)
    )
    if role_taker_association:
        role_taker_field = role_taker_association.field
        if role_taker_field.public_name in kwargs:
            return None, None
        instances_of_role_taker_type = symbol_graph.get_instances_of_type(
            role_taker_association.target.clazz
        )
        role_taker = next(
            (inst for inst in instances_of_role_taker_type if inst.uri == str(uri_ref)),
            None,
        )
        if role_taker:
            return role_taker_association, role_taker
        inner_role_taker_association, inner_role_taker = get_and_construct_role_taker(
            role_taker_association.target.clazz, uri_ref, symbol_graph
        )
        if inner_role_taker_association:
            kwargs[inner_role_taker_association.field.public_name] = inner_role_taker
        role_taker = role_taker_association.target.clazz(**kwargs)
        role_taker.uri = str(uri_ref)
        return role_taker_association, role_taker
    else:
        return None, None


def load_instances(
    owl_path: str,
    classes_module: Union[str, ModuleType],
    properties_module: Union[str, ModuleType],
    symbol_graph: Optional[SymbolGraph] = None,
    registry: Optional[OwlInstancesRegistry] = None,
) -> OwlInstancesRegistry:
    """Load OWL/RDF instances into the provided generated Python model module.

    This function is generic and can be reused with other OWL instance files that
    correspond to the given model module.
    """
    model_modules = [classes_module, properties_module]
    model_modules = [
        (
            __import__(model_module, fromlist=["*"])
            if isinstance(model_module, str)
            else model_module
        )
        for model_module in model_modules
    ]
    if not symbol_graph:
        SymbolGraph().clear()
        classes = set()
        for model_module in model_modules:
            classes.update(classes_of_module(model_module))
        class_diagram = ClassDiagram(
            list(classes), introspector=DescriptorAwareIntrospector()
        )
        symbol_graph = SymbolGraph(_class_diagram=class_diagram)

    if registry is None:
        registry = OwlInstancesRegistry()

    loader = OwlLoader(owl_path, model_modules, symbol_graph, registry)
    return loader.load()
