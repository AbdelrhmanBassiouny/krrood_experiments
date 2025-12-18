import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path for imports during tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from owl2bench.loader import WorldLoader


@pytest.fixture(scope="session")
def owl2_dl1():

    path = Path("../resources/generated_ontologies/OWL2DL-1.owl")
    if not path.exists():
        pytest.skip("OWL2DL-1 not available")

    loader = WorldLoader()
    world = loader.load(path)
    return world
