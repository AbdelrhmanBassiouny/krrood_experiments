"""
Compare everything KRROOD derives from the raw OWL2Bench data with the OWL 2 RL closure computed by GraphDB.

For every named OWL2Bench class, the set of individuals KRROOD types with that class (through Python inheritance and
role-taker chains) is compared with the individuals that have that ``rdf:type`` in the reference repository. For every
object property, the set of (subject, object) pairs stored in the corresponding attribute is compared with the
property assertions in the reference repository, and for every data property the (subject, value) pairs. The report
also contains the result of KRROOD's check of the OWL 2 RL rules that derive equality or inconsistency
(``OwlInstancesRegistry.check_owl2_rl``).

* ``unsound``: derived by KRROOD but not entailed by OWL 2 RL (according to the reference repository).
* ``missing``: entailed by OWL 2 RL but not derived by KRROOD.

Example::

    python -m krrood_experiments.aamas27.soundness_audit --output audit.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

from .environment import UNREASONED_FILE, write_json
from .graphdb import GraphDBClient

NAMESPACE = "http://benchmark/OWL2Bench#"
"""
Namespace of the OWL2Bench vocabulary.
"""

EXAMPLES = 10
"""
Number of example differences stored per class or property.
"""


def model_classes() -> Dict[str, type]:
    """
    :return: Mapping from OWL class URI to the generated Python class.
    """
    from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates as model

    classes = {}
    for name, value in vars(model).items():
        uri = getattr(value, "cls_uri", None) if isinstance(value, type) else None
        if isinstance(uri, str) and uri.startswith(NAMESPACE):
            classes[uri] = value
            # owl:equivalentClass aliases (e.g. School = College) are module attributes with another name
            classes.setdefault(NAMESPACE + name, value)
    return classes


IGNORED_CLASSES = {"Role"}
"""
OWL classes that only encode the role pattern in the ontology (``Role``, ``roleFor``) and have no counterpart class
in the generated model; they are excluded from the comparison.
"""


@lru_cache(maxsize=None)
def class_uris_of_type(python_type: type) -> frozenset:
    """
    :param python_type: The Python class of a KRROOD object.
    :return: URIs of all OWL classes the object is an instance of, through inheritance or role-taker chains.
    """
    from krrood.class_diagrams.utils import issubclass_or_role

    return frozenset(
        uri
        for uri, owl_class in model_classes().items()
        if issubclass_or_role(python_type, owl_class)
    )


def krrood_types(registry) -> Dict[str, Set[str]]:
    """
    :param registry: The KRROOD instance registry.
    :return: Mapping from individual URI to the set of OWL class URIs KRROOD assigns to it.
    """
    types: Dict[str, Set[str]] = defaultdict(set)
    for uri, objects in registry._by_uri.items():
        for instance in objects:
            types[str(uri)].update(class_uris_of_type(type(instance)))
    return types


def krrood_property_pairs(registry, property_local_names: Iterable[str]) -> Dict[str, Set[Tuple[str, str]]]:
    """
    :param registry: The KRROOD instance registry.
    :param property_local_names: Local names of the OWL object properties to collect.
    :return: Mapping from property local name to the set of (subject URI, object URI) pairs stored by KRROOD.
    """
    from krrood.ontomatic.ontology_to_python.owl_instances_loader import to_snake

    field_by_property = {name: to_snake(name) for name in property_local_names}
    pairs: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)
    for uri, objects in registry._by_uri.items():
        for instance in objects:
            for property_name, field_name in field_by_property.items():
                values = getattr(instance, field_name, None)
                if values is None:
                    continue
                if not isinstance(values, (set, list, tuple, frozenset)) and not hasattr(values, "__iter__"):
                    values = [values]
                for value in values:
                    value_uri = getattr(value, "uri", None)
                    if value_uri is not None:
                        pairs[property_name].add((str(uri), str(value_uri)))
    return pairs


def reference_types(client: GraphDBClient, repository: str, individuals: Set[str]) -> Dict[str, Set[str]]:
    """
    :return: Mapping from individual URI to its OWL2Bench class URIs in the reference repository.
    """
    result = client.select(
        repository,
        f"SELECT ?s ?c WHERE {{ ?s a ?c . FILTER(STRSTARTS(STR(?c), \"{NAMESPACE}\")) }}",
    )
    types: Dict[str, Set[str]] = defaultdict(set)
    for binding in result["results"]["bindings"]:
        subject = binding["s"]["value"]
        if subject in individuals:
            types[subject].add(binding["c"]["value"])
    return types


def reference_individuals(client: GraphDBClient, repository: str) -> Set[str]:
    """
    :return: URIs of the explicitly declared named individuals in the reference repository.
    """
    result = client.select(
        repository,
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
        "SELECT DISTINCT ?s FROM <http://www.ontotext.com/explicit> WHERE { ?s a owl:NamedIndividual }",
    )
    return {binding["s"]["value"] for binding in result["results"]["bindings"]}


def object_properties(client: GraphDBClient, repository: str) -> List[str]:
    """
    :return: Local names of the OWL2Bench object properties declared in the reference repository.
    """
    result = client.select(
        repository,
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
        f"SELECT DISTINCT ?p FROM <http://www.ontotext.com/explicit> WHERE {{ ?p a owl:ObjectProperty . "
        f"FILTER(STRSTARTS(STR(?p), \"{NAMESPACE}\")) }}",
    )
    return sorted(binding["p"]["value"][len(NAMESPACE):] for binding in result["results"]["bindings"])


def data_properties(client: GraphDBClient, repository: str) -> List[str]:
    """
    :return: Local names of the OWL2Bench data properties declared in the reference repository.
    """
    result = client.select(
        repository,
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
        f"SELECT DISTINCT ?p FROM <http://www.ontotext.com/explicit> WHERE {{ ?p a owl:DatatypeProperty . "
        f"FILTER(STRSTARTS(STR(?p), \"{NAMESPACE}\")) }}",
    )
    return sorted(binding["p"]["value"][len(NAMESPACE):] for binding in result["results"]["bindings"])


def normalized_value(value: Any) -> str:
    """
    :return: The value of a literal or a Python attribute value as a comparable string.
    """
    return str(value.toPython() if hasattr(value, "toPython") else value)


def reference_data_pairs(client: GraphDBClient, repository: str, property_local_name: str,
                         individuals: Set[str]) -> Set[Tuple[str, str]]:
    """
    :return: The (subject, value) pairs of a data property of individuals in the reference repository.
    """
    import rdflib

    result = client.select(
        repository, f"SELECT ?s ?o WHERE {{ ?s <{NAMESPACE}{property_local_name}> ?o . FILTER(isLiteral(?o)) }}"
    )
    pairs = set()
    for binding in result["results"]["bindings"]:
        if binding["s"]["value"] not in individuals:
            continue
        datatype = binding["o"].get("datatype")
        literal = rdflib.Literal(binding["o"]["value"], datatype=rdflib.URIRef(datatype) if datatype else None)
        pairs.add((binding["s"]["value"], normalized_value(literal)))
    return pairs


def krrood_data_pairs(registry, property_local_names: Iterable[str]) -> Dict[str, Set[Tuple[str, str]]]:
    """
    :return: Mapping from data property local name to the (subject URI, value) pairs stored by KRROOD.
    """
    from krrood.ontomatic.ontology_to_python.owl_instances_loader import to_snake

    pairs: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)
    for uri, objects in registry._by_uri.items():
        for instance in objects:
            for name in property_local_names:
                value = getattr(instance, to_snake(name), None)
                if value is None:
                    continue
                for member in value if isinstance(value, (set, list, tuple)) else (value,):
                    pairs[name].add((str(uri), normalized_value(member)))
    return pairs


def reference_pairs(client: GraphDBClient, repository: str, property_local_name: str,
                    individuals: Set[str]) -> Set[Tuple[str, str]]:
    """
    :return: The (subject, object) pairs of a property between individuals in the reference repository.
    """
    result = client.select(
        repository, f"SELECT ?s ?o WHERE {{ ?s <{NAMESPACE}{property_local_name}> ?o }}"
    )
    return {
        (binding["s"]["value"], binding["o"]["value"])
        for binding in result["results"]["bindings"]
        if binding["s"]["value"] in individuals and binding["o"]["value"] in individuals
    }


def difference_entry(krrood: Set, reference: Set) -> Dict[str, Any]:
    """
    :return: Sizes and examples of the two set differences.
    """
    unsound = krrood - reference
    missing = reference - krrood
    return {
        "krrood": len(krrood),
        "reference": len(reference),
        "unsound": len(unsound),
        "missing": len(missing),
        "unsound_examples": sorted(map(str, unsound))[:EXAMPLES],
        "missing_examples": sorted(map(str, missing))[:EXAMPLES],
    }


def audit(registry, client: GraphDBClient, repository: str, include_properties: bool = True) -> Dict[str, Any]:
    """
    :param registry: The KRROOD instance registry loaded from the raw data.
    :param client: The GraphDB client.
    :param repository: The reference repository (raw data with the OWL 2 RL ruleset).
    :param include_properties: Whether to also compare object property assertions.
    :return: The audit report.
    """
    individuals = reference_individuals(client, repository)
    krrood_type_map = krrood_types(registry)
    individuals_in_both = individuals & set(krrood_type_map)
    reference_type_map = reference_types(client, repository, individuals_in_both)

    by_class_krrood: Dict[str, Set[str]] = defaultdict(set)
    by_class_reference: Dict[str, Set[str]] = defaultdict(set)
    for individual in individuals_in_both:
        for class_uri in krrood_type_map.get(individual, ()):
            by_class_krrood[class_uri].add(individual)
        for class_uri in reference_type_map.get(individual, ()):
            by_class_reference[class_uri].add(individual)
    classes = {}
    for class_uri in sorted(set(by_class_krrood) | set(by_class_reference)):
        if class_uri[len(NAMESPACE):] in IGNORED_CLASSES:
            continue
        classes[class_uri[len(NAMESPACE):]] = difference_entry(
            by_class_krrood[class_uri], by_class_reference[class_uri]
        )

    report: Dict[str, Any] = {
        "reference_repository": repository,
        "individuals_in_reference": len(individuals),
        "individuals_in_krrood": len(krrood_type_map),
        "individuals_only_in_reference": sorted(individuals - set(krrood_type_map))[:EXAMPLES],
        "individuals_only_in_krrood": sorted(set(krrood_type_map) - individuals)[:EXAMPLES],
        "classes": classes,
        "class_totals": {
            "unsound": sum(entry["unsound"] for entry in classes.values()),
            "missing": sum(entry["missing"] for entry in classes.values()),
        },
    }
    if include_properties:
        names = object_properties(client, repository)
        krrood_pairs = krrood_property_pairs(registry, names)
        properties = {}
        for name in names:
            krrood_pairs_between_shared_individuals = {
                pair
                for pair in krrood_pairs.get(name, set())
                if pair[0] in individuals_in_both and pair[1] in individuals_in_both
            }
            properties[name] = difference_entry(
                krrood_pairs_between_shared_individuals,
                reference_pairs(client, repository, name, individuals_in_both),
            )
        report["object_properties"] = properties
        report["object_property_totals"] = {
            "unsound": sum(entry["unsound"] for entry in properties.values()),
            "missing": sum(entry["missing"] for entry in properties.values()),
        }
        names = data_properties(client, repository)
        krrood_values = krrood_data_pairs(registry, names)
        values = {
            name: difference_entry(
                {pair for pair in krrood_values.get(name, set()) if pair[0] in individuals_in_both},
                reference_data_pairs(client, repository, name, individuals_in_both),
            )
            for name in names
        }
        report["data_properties"] = values
        report["data_property_totals"] = {
            "unsound": sum(entry["unsound"] for entry in values.values()),
            "missing": sum(entry["missing"] for entry in values.values()),
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input-file", default=str(UNREASONED_FILE))
    parser.add_argument("--graphdb-repository", default="aamas27_rl")
    parser.add_argument("--graphdb-url", default=None)
    parser.add_argument("--no-properties", action="store_true", help="only compare class memberships")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    from krrood_experiments.owl2bench.ontomatic.helpers import load_instances_for_owl2bench_with_predicates

    start = time.perf_counter()
    registry = load_instances_for_owl2bench_with_predicates(arguments.input_file)
    loading_seconds = time.perf_counter() - start
    client = GraphDBClient(arguments.graphdb_url) if arguments.graphdb_url else GraphDBClient()
    report = audit(registry, client, arguments.graphdb_repository, not arguments.no_properties)
    report["krrood_loading_seconds"] = loading_seconds
    start = time.perf_counter()
    owl2_rl_check = registry.check_owl2_rl()
    report["owl2_rl_check"] = owl2_rl_check.summary()
    report["owl2_rl_check"]["seconds"] = time.perf_counter() - start
    report["owl2_rl_check"]["findings"] = [
        [finding.rule.value, list(finding.individuals), finding.detail]
        for finding in (owl2_rl_check.equalities + owl2_rl_check.inconsistencies)[:EXAMPLES]
    ]
    write_json(Path(arguments.output), report)
    print(json.dumps({"class_totals": report["class_totals"],
                      "object_property_totals": report.get("object_property_totals"),
                      "data_property_totals": report.get("data_property_totals"),
                      "owl2_rl_check": {key: report["owl2_rl_check"][key]
                                        for key in ("passed", "equalities", "inconsistencies", "seconds")}},
                     indent=2))
    for name, entry in report["classes"].items():
        if entry["unsound"] or entry["missing"]:
            print(f"class {name}: krrood={entry['krrood']} reference={entry['reference']} "
                  f"unsound={entry['unsound']} missing={entry['missing']}")
    for name, entry in list(report.get("object_properties", {}).items()) + list(
        report.get("data_properties", {}).items()
    ):
        if entry["unsound"] or entry["missing"]:
            print(f"property {name}: krrood={entry['krrood']} reference={entry['reference']} "
                  f"unsound={entry['unsound']} missing={entry['missing']}")
    sys.stdout.flush()
    import os

    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
