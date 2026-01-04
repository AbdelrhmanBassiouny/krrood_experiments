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
from rdflib import RDF, URIRef, Literal, OWL


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

        if instances and any(isinstance(inst, factory) for inst in instances):
            # If an instance of the desired factory already exists, return it
            return [i for i in instances if isinstance(i, factory)][0]

        role_taker_association, role_taker = OwlLoader.get_and_construct_role_taker(
            factory, uri, symbol_graph, **kwargs
        )
        if role_taker_association:
            kwargs[role_taker_association.field.public_name] = role_taker

        inst = factory(*args, **kwargs)

        # Set URI if not already set
        local = str(uri)
        if hasattr(inst, "uri") and getattr(inst, "uri") is None:
            setattr(inst, "uri", local)

        # Update instance mappings
        self._by_uri[uri].append(inst)
        self._by_class.setdefault(factory, []).append(inst)

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
    """Metadata about the Python model classes and their relationship to OWL.

    Maintains mappings from RDF class names to Python classes, and from RDF predicates to
    Python attributes and property descriptors.
    """

    def __init__(self, model_modules: Union[ModuleType, Iterable[ModuleType]]):
        """Initializes ModelMetadata by scanning the provided modules.

        Args:
            model_modules: A single module or an iterable of modules containing the model classes.
        """
        self.class_by_name: Dict[str, Type] = {}
        self.descriptor_by_name: Dict[str, Type] = {}
        self.field_by_predicate_local: Dict[Type, Dict[str, str]] = {}
        self.field_by_descriptor: Dict[Type, Dict[Type, str]] = {}
        self._collect(model_modules)

    def _collect(self, model_modules: Union[ModuleType, Iterable[ModuleType]]):
        """Orchestrates the collection of metadata from the model modules.

        Args:
            model_modules: Modules to scan for classes and descriptors.
        """
        if isinstance(model_modules, (ModuleType, type)):
            model_modules = [model_modules]
        self._collect_classes_and_descriptors(model_modules)
        self._map_predicates_and_descriptors()

    def _collect_classes_and_descriptors(self, model_modules: Iterable[ModuleType]):
        """Scans modules for dataclasses and PropertyDescriptor subclasses.

        Args:
            model_modules: Iterable of modules to scan.
        """
        modules_objects = {}
        for model_module in model_modules:
            modules_objects.update(
                {
                    attr_name: getattr(model_module, attr_name)
                    for attr_name in dir(model_module)
                }
            )

        for attr_name, obj in modules_objects.items():

            # Collect model classes (dataclasses used to represent OWL classes)
            if isinstance(obj, type) and is_dataclass(obj):
                self.class_by_name[attr_name] = obj

            # Collect descriptor classes available in the module for quick lookup by name
            if (
                isinstance(obj, type)
                and issubclass(obj, PropertyDescriptor)
                and obj is not PropertyDescriptor
            ):
                self.descriptor_by_name[obj.__name__] = obj

    def _map_predicates_and_descriptors(self):
        """Maps predicate local names and descriptors to attributes for each collected class."""
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
        """Returns the Python class corresponding to the given RDF class URI.

        Args:
            rdf_class: The URIRef of the RDF class.

        Returns:
            The Python class if found, otherwise None.
        """
        name = local_name(rdf_class)
        # Expect PascalCase names in model equal to RDF local name
        return self.class_by_name.get(name)

    def get_field_name(self, cls: Type, snake_name: str) -> Optional[str]:
        """Gets the attribute name for a given class and predicate (in snake_case).

        Args:
            cls: The Python class.
            snake_name: The snake_case name of the predicate.

        Returns:
            The attribute name if mapped, otherwise None.
        """
        return self.field_by_predicate_local.get(cls, {}).get(snake_name)

    def get_descriptor_base(
        self, pred_local: str
    ) -> Optional[Type[PropertyDescriptor]]:
        """Finds the PropertyDescriptor base class for a given predicate local name.

        Args:
            pred_local: The local name of the RDF predicate.

        Returns:
            The PropertyDescriptor subclass if found, otherwise None.
        """
        return self.descriptor_by_name.get(to_pascal(pred_local))


class OwlLoader:
    """Loader for OWL/RDF instances into Python model instances."""

    def __init__(
        self,
        owl_path: str,
        model_modules: Union[ModuleType, Iterable[ModuleType]],
        symbol_graph: SymbolGraph,
        registry: OwlInstancesRegistry,
    ):
        """Initializes OwlLoader.

        Args:
            owl_path: Path to the OWL/RDF file.
            model_modules: Modules containing model classes.
            symbol_graph: The symbol graph representing the model.
            registry: Registry to store created instances.
        """
        self.owl_path = owl_path
        self.model_modules = model_modules
        self.symbol_graph = symbol_graph
        self.registry = registry
        self.metadata = ModelMetadata(model_modules)
        self.graph = rdflib.Graph()

    def load(self) -> OwlInstancesRegistry:
        """Parses the OWL file and loads instances into the registry.

        Returns:
            The populated OwlInstancesRegistry.
        """
        self.graph.parse(self.owl_path)
        self._create_explicit_instances()
        self._assign_all_properties()
        return self.registry

    def _create_explicit_instances(self):
        """Creates instances for all subjects with an explicit rdf:type in the graph."""
        for s, _, o_class in self.graph.triples((None, RDF.type, None)):
            if not isinstance(s, URIRef):
                continue
            py_cls = self.metadata.get_python_class(o_class)
            if py_cls is None:
                continue
            if o_class in [
                OWL.SymmetricProperty,
                OWL.DatatypeProperty,
                OWL.ObjectProperty,
                OWL.IrreflexiveProperty,
                OWL.AsymmetricProperty,
                OWL.TransitiveProperty,
                OWL.InverseFunctionalProperty,
                OWL.Class,
            ]:
                continue
            existing_roles = self.registry.resolve(s)
            kwargs = self._get_common_role_taker_kwargs(existing_roles, py_cls)
            self.registry.get_or_create_for(s, py_cls, self.symbol_graph, **kwargs)

    def _get_common_role_taker_kwargs(
        self, existing_roles: Optional[List[Any]], target_cls: Type
    ) -> Dict[str, Any]:
        """Finds common role-taker associations between existing roles and a target class.

        Args:
            existing_roles: List of already created roles for the same URI.
            target_cls: The class of the new role to be created.

        Returns:
            A dictionary of keyword arguments for the target class constructor.
        """
        kwargs = {}
        if not existing_roles:
            return kwargs
        for er in existing_roles:
            (
                assoc1,
                assoc2,
            ) = self.symbol_graph.class_diagram.get_common_role_taker_associations(
                type(er), target_cls
            )
            if not assoc1 or not assoc2 or assoc2.field.public_name in kwargs:
                continue
            kwargs[assoc2.field.public_name] = getattr(er, assoc1.field.public_name)
        return kwargs

    def _ensure_instance(self, uri: URIRef) -> Optional[List[Any]]:
        """Ensures that at least one instance exists for the given URI.

        Attempts to infer the class from rdf:type triples if no instance exists.

        Args:
            uri: The URIRef of the instance.

        Returns:
            A list of instances for the URI, or None if none could be found or created.
        """
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
        """Iterates through all triples in the graph and assigns properties to instances."""
        for s, p, o in self.graph:
            if p == RDF.type or not isinstance(s, URIRef):
                continue

            subj_roles = self._get_subject_roles(s)
            if not subj_roles:
                continue

            subj = subj_roles[0]
            predicate_name = to_snake(local_name(p))
            self._assign_property(subj, predicate_name, o)

    def _assign_property(
        self,
        subj: Any,
        predicate_name: str,
        obj_uri: Union[URIRef, Literal],
    ):
        """Assigns a property to an instance based on the predicate name and object URI. It handles both data and
         object properties.
        Args:
            subj: The subject instance.
            predicate_name: The snake_case name of the predicate.
            obj_uri: The RDF node of the object.
        """
        field_name = self._determine_field_name(subj, predicate_name)
        if isinstance(obj_uri, Literal):
            self._assign_data_property(subj, field_name, obj_uri)
        else:
            self._assign_object_property(subj, field_name, predicate_name, obj_uri)

    def _get_subject_roles(self, subject_uri: URIRef) -> Optional[List[Any]]:
        """Resolves or ensures instances for a given subject URI.

        Args:
            subject_uri: The URIRef of the subject.

        Returns:
            A list of subject roles if found or created, otherwise None.
        """
        subj_roles = self.registry.resolve(subject_uri)
        if subj_roles is None:
            # Subject without explicit type known to model; try infer
            subj_roles = self._ensure_instance(subject_uri)
        return subj_roles

    def _determine_field_name(self, subj: Any, snake_name: str) -> Optional[str]:
        """Determines the appropriate attribute name on the subject for a given predicate.

        Args:
            subj: The subject instance.
            snake_name: The snake_case name of the predicate.

        Returns:
            The field name if determined, otherwise None.
        """
        subj_cls = type(subj)
        field_name = self.metadata.get_field_name(subj_cls, snake_name)
        if not field_name:
            if snake_name in [f.name for f in fields(subj_cls)]:
                field_name = snake_name
            elif hasattr(subj, snake_name):
                field_name = snake_name
        return field_name

    def _get_role_taker_val(self, subj: Any, subj_cls: Type) -> Optional[Any]:
        """Retrieves the role-taker instance for a given subject, if it exists.

        Args:
            subj: The subject instance.
            subj_cls: The class of the subject instance.

        Returns:
            The role-taker instance or None.
        """
        role_taker_association = (
            self.symbol_graph.class_diagram.get_role_taker_associations_of_cls(subj_cls)
        )
        return (
            getattr(subj, role_taker_association.field.public_name, None)
            if role_taker_association
            else None
        )

    def _assign_data_property(
        self,
        subj: Any,
        field_name: Optional[str],
        literal: Literal,
    ):
        """Assigns a data property to an instance, coercing the literal value if possible.

        Args:
            subj: The subject instance.
            field_name: The determined field name on the subject.
            literal: The RDF literal value.
        """
        if field_name and hasattr(subj, field_name):
            # Coerce to field annotated type
            try:
                ftypes = {f.name: f.type for f in fields(type(subj))}
            except TypeError:
                ftypes = {}
            coerced = self._coerce_literal(literal, ftypes.get(field_name))
            setattr(subj, field_name, coerced)

    def _get_matching_role(
        self, roles: Optional[List[Any]], target_type: Type
    ) -> Optional[Any]:
        """Finds a role among the given roles that matches the target type.

        Also searches through the role-taker chain.

        Args:
            roles: List of roles to search.
            target_type: The desired Python type.

        Returns:
            The matching role instance if found, otherwise None.
        """
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
            obj_role = getattr(obj_role, role_taker_assoc.field.public_name)
            role_taker_assoc = (
                self.symbol_graph.class_diagram.get_role_taker_associations_of_cls(
                    role_taker_assoc.target.clazz
                )
            )
        return None

    def _assign_object_property(
        self,
        subj: Any,
        field_name: Optional[str],
        snake: str,
        obj_node: Union[URIRef, Literal],
    ):
        """Assigns an object property by resolving the object node and finding the correct attribute.

        Args:
            subj: The subject instance.
            field_name: The determined field name on the subject.
            snake: The snake_case name of the predicate.
            obj_node: The RDF node of the object.
        """
        obj_roles = (
            self._ensure_instance(obj_node) if isinstance(obj_node, URIRef) else None
        )
        obj = obj_roles[0] if obj_roles else None
        matched_obj = None
        if field_name and hasattr(subj, field_name):
            class_diagram = self.symbol_graph.class_diagram
            try:
                subj_wrapped_field = (
                    assoc.field
                    for assoc in class_diagram.associations
                    if assoc.field.public_name == field_name
                ).__next__()

                req_obj_type = subj_wrapped_field.type_endpoint
                matched_obj = self._get_matching_role(obj_roles, req_obj_type)
            except StopIteration:
                pass

            obj = matched_obj or obj

            if self._assign_to_attribute(subj, field_name, obj):
                return

        self._handle_descriptor_based_property(subj, snake, obj)

    def _assign_to_attribute(self, target: Any, attr_name: str, value: Any) -> bool:
        """Assigns a value to an attribute, or adds to it if it's a collection.

        Args:
            target: The object to assign the value to.
            attr_name: The name of the attribute.
            value: The value to assign.

        Returns:
            True if assigned, False otherwise.
        """
        if value is None:
            return False

        attr_val = getattr(target, attr_name, None)
        if hasattr(attr_val, "add"):
            attr_val.add(value)
        else:
            setattr(target, attr_name, value)
        return True

    def _handle_descriptor_based_property(self, subj: Any, snake: str, obj: Any):
        """Handles properties that require creating a new role based on a PropertyDescriptor.

        Args:
            subj: The subject instance.
            snake: The snake_case name of the predicate.
            obj: The object instance.

        Raises:
            ValueError: If the property could not be assigned.
        """
        base_desc = self.metadata.get_descriptor_base(snake)
        if not base_desc:
            raise ValueError(f"Could not find descriptor for {snake}")

        new_role_class = self._find_best_role_class(base_desc, obj, snake)
        new_role = self._get_or_create_role_instance(subj, new_role_class)

        if hasattr(new_role, snake) and self._assign_to_attribute(new_role, snake, obj):
            return

        raise ValueError(f"Could not assign {obj} to {subj} ({snake})")

    @staticmethod
    def _find_best_role_class(
        base_desc: Type[PropertyDescriptor],
        obj: Any,
        snake: str,
    ) -> Type:
        """Determines the most appropriate role class for a given descriptor and object.

        Args:
            base_desc: The base PropertyDescriptor class.
            obj: The object instance.
            snake: The snake_case name of the predicate.

        Returns:
            The selected role class.

        Raises:
            ValueError: If no suitable role class can be determined.
        """
        possible_roles = list(PropertyDescriptor.all_domains[base_desc])
        if len(possible_roles) == 1:
            return possible_roles[0]

        o_type = type(obj)
        wrapped_field_types = {
            pr: getattr(pr, snake).range
            for pr in possible_roles
            if hasattr(pr, snake) and issubclass(o_type, getattr(pr, snake).range)
        }

        if not wrapped_field_types:
            raise ValueError(
                f"Could not determine role for {obj} ({o_type}) and predicate {snake} ({base_desc})"
            )

        # choose the nearest wrapped field type
        chosen_role = min(
            wrapped_field_types.keys(),
            key=lambda k: inheritance_path_length(wrapped_field_types[k], o_type),
        )

        if chosen_role is None:
            raise ValueError(
                f"Could not determine role for {obj} ({o_type}) and predicate {snake} ({base_desc})"
            )
        return chosen_role

    def _get_or_create_role_instance(self, subj: Any, role_class: Type) -> Any:
        """Retrieves an existing role instance for the subject or creates a new one.

        Args:
            subj: The subject instance.
            role_class: The class of the role to find or create.

        Returns:
            The role instance.
        """
        s_uri = subj.uri
        existing_roles = self.registry.resolve(s_uri)
        for er in existing_roles:
            if type(er) is role_class:
                return er

        kwargs = self._get_common_role_taker_kwargs([subj], role_class)
        role_taker_inst = next(iter(kwargs.values()), None) if kwargs else None

        if role_taker_inst is None:
            uri = s_uri
        else:
            uri = getattr(role_taker_inst, "uri", s_uri)

        return self.registry.get_or_create_for(
            URIRef(uri) if isinstance(uri, str) else uri,
            role_class,
            self.symbol_graph,
            **kwargs,
        )

    @staticmethod
    def _coerce_literal(val: Literal, target_type: Optional[Type]) -> Any:
        """Coerces an RDF literal to a Python type.

        Args:
            val: The RDF literal.
            target_type: The target Python type.

        Returns:
            The coerced Python value.
        """
        if target_type is None:
            return val.toPython()
        try:
            # Unwrap Optional[T]
            origin = getattr(target_type, "__origin__", None)
            if origin is Union:
                args = [
                    a
                    for a in getattr(target_type, "__args__", ())
                    if a is not type(None)
                ]  # noqa: E721
                if args:
                    target_type = args[0]
            if target_type in (str, int, float, bool):
                return target_type(val.toPython())
        except Exception:
            pass
        return val.toPython()

    @staticmethod
    def get_and_construct_role_taker(
        cls_: Type, uri_ref: URIRef, symbol_graph: SymbolGraph, **kwargs
    ) -> Tuple[Optional[Association], Optional[Symbol]]:
        """Recursively finds or constructs role-takers for a given class.

        Args:
            cls_: The target class.
            uri_ref: The URI of the instance.
            symbol_graph: The symbol graph for lookups.
            **kwargs: Additional arguments for constructor.

        Returns:
            A tuple of (Association, RoleTakerInstance) if found/created, else (None, None).
        """
        role_taker_association = (
            symbol_graph.class_diagram.get_role_taker_associations_of_cls(cls_)
        )
        if not role_taker_association:
            return None, None

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

        (
            inner_role_taker_association,
            inner_role_taker,
        ) = OwlLoader.get_and_construct_role_taker(
            role_taker_association.target.clazz, uri_ref, symbol_graph
        )
        if inner_role_taker_association:
            kwargs[inner_role_taker_association.field.public_name] = inner_role_taker
        role_taker = role_taker_association.target.clazz(**kwargs)
        role_taker.uri = str(uri_ref)

        return role_taker_association, role_taker

    @staticmethod
    def create_symbol_graph(
        model_modules: Iterable[Union[str, ModuleType]],
    ) -> SymbolGraph:
        """Creates and initializes a SymbolGraph from model modules.

        Args:
            model_modules: Iterable of modules or module names.

        Returns:
            The initialized SymbolGraph.
        """
        modules = [
            (__import__(m, fromlist=["*"]) if isinstance(m, str) else m)
            for m in model_modules
        ]

        SymbolGraph().clear()
        classes = set()
        for model_module in modules:
            classes.update(classes_of_module(model_module))
        class_diagram = ClassDiagram(
            list(classes), introspector=DescriptorAwareIntrospector()
        )
        return SymbolGraph(_class_diagram=class_diagram)

    @staticmethod
    def load_instances(
        owl_path: str,
        classes_module: Union[str, ModuleType],
        properties_module: Union[str, ModuleType],
        symbol_graph: Optional[SymbolGraph] = None,
        registry: Optional[OwlInstancesRegistry] = None,
    ) -> OwlInstancesRegistry:
        """Loads OWL instances into a registry.

        Args:
            owl_path: Path to the OWL file.
            classes_module: Module containing model classes.
            properties_module: Module containing property descriptors.
            symbol_graph: Optional existing SymbolGraph.
            registry: Optional existing registry.

        Returns:
            The populated OwlInstancesRegistry.
        """
        model_modules = [classes_module, properties_module]
        if not symbol_graph:
            symbol_graph = OwlLoader.create_symbol_graph(model_modules)

        # Ensure model_modules are modules, not just names, for OwlLoader
        modules = [
            (__import__(m, fromlist=["*"]) if isinstance(m, str) else m)
            for m in model_modules
        ]

        if registry is None:
            registry = OwlInstancesRegistry()

        loader = OwlLoader(owl_path, modules, symbol_graph, registry)
        return loader.load()

    @staticmethod
    def load_multi_file_instances(
        owl_paths: Iterable[str],
        classes_module: Union[str, ModuleType],
        properties_module: Union[str, ModuleType],
    ) -> OwlInstancesRegistry:
        """Loads instances from multiple OWL files into a single registry.

        Args:
            owl_paths: Iterable of OWL file paths.
            classes_module: Module containing model classes.
            properties_module: Module containing property descriptors.

        Returns:
            The populated OwlInstancesRegistry.
        """
        combined_registry = OwlInstancesRegistry()
        model_modules = [classes_module, properties_module]
        symbol_graph = OwlLoader.create_symbol_graph(model_modules)

        for path in owl_paths:
            OwlLoader.load_instances(
                path,
                classes_module,
                properties_module,
                symbol_graph=symbol_graph,
                registry=combined_registry,
            )
        return combined_registry
