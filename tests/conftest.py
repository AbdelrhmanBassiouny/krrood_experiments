import os.path
import runpy
import sys

import SPARQLWrapper
import pytest

from owl2bench.loader import WorldLoader


def pytest_sessionstart(session) -> None:
    """
    Generate the ORM at the start of the test run.
    """

    this_file_path = os.path.abspath(__file__)
    runpy.run_path(
        os.path.join(this_file_path, "..", "..", "scripts", "generate_orm.py"),
        run_name="__main__",
    )


@pytest.fixture(scope="session")
def world_from_graph_db():
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    loader = WorldLoader(sparql)
    loader.parse()
    return loader.world
