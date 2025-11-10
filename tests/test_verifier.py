from pathlib import Path
import textwrap
import pytest

from owl2bench.loader import WorldLoader
from owl2bench.models import World, University, College
from owl2bench.verifier import WorldVerifier, RelationshipError


def write_temp_ttl(tmp_path: Path) -> Path:
    ttl = textwrap.dedent(
        """
        @prefix bench: <http://benchmark/OWL2Bench#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        bench:U1 a bench:University ;
            rdfs:label "Demo University" ;
            bench:hasCollege bench:U1_C1 .

        bench:U1_C1 a bench:College ;
            rdfs:label "Demo College" .
        """
    )
    p = tmp_path / "mini_for_verifier.ttl"
    p.write_text(ttl, encoding="utf-8")
    return p


def test_verifier_passes_on_minimal_world(tmp_path: Path):
    world = WorldLoader().load(write_temp_ttl(tmp_path))
    WorldVerifier().verify(world)  # should not raise


def test_verifier_detects_duplicate_parentage():
    c = College(identifier="C1", name="C1", is_women_only=False)
    u1 = University(identifier="U1", name="U1", colleges=[c])
    u2 = University(identifier="U2", name="U2", colleges=[c])
    world = World(universities=[u1, u2], colleges=[c])

    with pytest.raises(RelationshipError) as exc:
        WorldVerifier().verify(world)
    assert "appears under multiple universities" in str(exc.value)


def test_verifier_on_instances_owl(owl2_dl1):
    WorldVerifier().verify(owl2_dl1)  # should not raise
