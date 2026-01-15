import pytest
from krrood.entity_query_language.symbol_graph import SymbolGraph


@pytest.fixture(autouse=True, scope="function")
def cleanup_after_test():
    # runs BEFORE each ontomatic_tests
    yield
    # runs AFTER each ontomatic_tests (even if the ontomatic_tests fails or errors)
    SymbolGraph().clear()
