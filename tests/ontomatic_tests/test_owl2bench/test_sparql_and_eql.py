import os
import time

import pytest

from krrood_experiments.owl2bench.ontomatic.helpers import (
    load_instances_for_owl2bench_with_predicates,
)
from krrood_experiments.owl2bench.ontomatic.owl2bench_eql_queries import (
    evaluate_eql_and_sparql_queries,
)


@pytest.fixture
def resources_dir():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "resources"
    )


@pytest.fixture
def unreasoned_owl2bench_file_path(resources_dir):
    return os.path.join(resources_dir, "owl2bench_statements_unreasoned.rdf")


@pytest.fixture
def reasoned_owl2bench_file_path(resources_dir):
    return os.path.join(resources_dir, "owl2bench_statements_reasoned.rdf")


def test_owl2bench_statements_reasoned(reasoned_owl2bench_file_path):
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates(
        reasoned_owl2bench_file_path
    )
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    evaluate_eql_and_sparql_queries()


def test_owl2bench_statements_unreasoned(unreasoned_owl2bench_file_path):
    loading_start_time = time.time()
    registry = load_instances_for_owl2bench_with_predicates(
        unreasoned_owl2bench_file_path
    )
    loading_time = time.time() - loading_start_time
    print(f"Loading time: {loading_time} seconds")

    evaluate_eql_and_sparql_queries()
