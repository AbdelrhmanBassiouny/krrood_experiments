import textwrap
from pathlib import Path
import warnings

import pytest

from owl2bench.loader import WorldLoader, MappingError, OntologyLoadError


def write_temp_ttl(tmp_path: Path) -> Path:
    ttl = textwrap.dedent(
        """
        @prefix bench: <http://benchmark/OWL2Bench#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        bench:U1 a bench:University ;
            rdfs:label "Demo University" ;
            bench:hasCollege bench:U1_C1 .

        bench:U1_C1 a bench:College , bench:WomenCollege ;
            rdfs:label "Demo College" ;
            bench:hasDepartment bench:U1_C1_D1 .

        bench:U1_C1_D1 a bench:Department ;
            rdfs:label "Computer Science" ;
            bench:offerCourse bench:U1_C1_D1_CRS1 .

        bench:U1_C1_D1_CRS1 a bench:Course ;
            rdfs:label "Intro to CS" .

        bench:P1 a bench:Person , bench:Woman ;
            bench:hasFirstName "Ada" ;
            bench:hasLastName "Lovelace" ;
            bench:hasEmailAddress "ada@bench.com" ;
            bench:isFrom "London" .
        """
    )
    p = tmp_path / "mini.ttl"
    p.write_text(ttl, encoding="utf-8")
    return p


def test_world_loader_minimal_abox(tmp_path: Path):
    path = write_temp_ttl(tmp_path)
    loader = WorldLoader()
    world = loader.load(path)

    assert len(world.universities) == 1
    uni = world.universities[0]
    assert uni.name == "Demo University"
    assert len(uni.colleges) == 1
    col = uni.colleges[0]
    assert col.is_women_only is True
    assert len(col.departments) == 1
    dept = col.departments[0]
    assert dept.name == "Computer Science"
    assert len(dept.courses) == 1
    assert dept.courses[0].title == "Intro to CS"

    # persons are loaded globally
    assert any(
        p.first_name == "Ada" and p.last_name == "Lovelace" for p in world.persons
    )


def test_world_loader_missing_required_raises(tmp_path: Path):
    # Missing email
    ttl = textwrap.dedent(
        """
        @prefix bench: <http://benchmark/OWL2Bench#> .
        bench:P2 a bench:Person , bench:Man ;
            bench:hasFirstName "Alan" ;
            bench:hasLastName "Turing" .
        """
    )
    p = tmp_path / "bad.ttl"
    p.write_text(ttl, encoding="utf-8")

    loader = WorldLoader()
    with pytest.raises(MappingError):
        loader.load(p)


@pytest.mark.skipif(
    not Path("../resources/instances.owl").exists(), reason="instances.owl not present"
)
def test_world_loader_smoke_instances_file():
    loader = WorldLoader()
    world = loader.load(Path("../resources/instances.owl"))

    # Smoke assertions: ensure we loaded at least one university
    assert len(world.universities) >= 1
    # Optional: if persons are present, basic field integrity
    for person in world.persons[:10]:
        assert person.first_name
        assert person.last_name
        assert person.email
        assert isinstance(person.is_woman, bool)
