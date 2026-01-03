import os
import shutil
import pytest
from krrood_experiments.owl_to_python import OwlToPythonConverter

def test_lubm_regression(tmp_path):
    repo_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    resources_path = os.path.join(repo_dir, "lubm", "resources")
    owl_file = os.path.join(resources_path, "lubm_clean.owl")
    
    _default_overrides = {
        "Person": {
            "age": "int",
            "telephone": "str",
            "title": "str",
            "email_address": "str",
        },
        "Professor": {
            "tenured": "bool",
        },
        "Publication": {
            "publication_date": "str",
        },
        "Software": {
            "software_version": "str",
        },
        "Thing": {
            "name": "str",
            "office_number": "int",
            "research_interest": "str",
        },
    }
    
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    converter.load_ontology(owl_file)
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_base = output_dir / "lubm_with_predicates"
    
    converter.save_to_file(str(output_base) + ".py")
    
    existing_dir = os.path.join(repo_dir, "src", "krrood_experiments", "lubm")
    files_to_compare = [
        "lubm_with_predicates.py",
        "lubm_with_predicates_properties.py",
        "lubm_with_predicates_base.py",
        "lubm_with_predicates.pyi"
    ]
    
    for filename in files_to_compare:
        generated_file = output_dir / filename
        existing_file = os.path.join(existing_dir, filename)
        
        with open(generated_file, "r") as f:
            generated_content = f.read()
        with open(existing_file, "r") as f:
            existing_content = f.read()
            
        assert generated_content == existing_content, f"Content mismatch in {filename}"

@pytest.mark.skip(reason="OWL2Bench ontology is not stable enough yet.")
def test_owl2bench_regression(tmp_path):
    repo_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    resources_path = os.path.join(repo_dir, "owl2bench", "resources", "refactored_ontologies")
    owl_file = os.path.join(resources_path, "owl2benchRlFixed.owl")
    
    _default_overrides = {
        "Person": {
            "age": "int",
            "telephone": "str",
            "title": "str",
            "email_address": "str",
        },
        "Professor": {
            "tenured": "bool",
        },
        "Publication": {
            "publication_date": "str",
        },
        "Software": {
            "software_version": "str",
        },
        "Thing": {
            "name": "str",
            "office_number": "int",
            "research_interest": "str",
        },
    }
    
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    converter.load_ontology(owl_file)
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_base = output_dir / "owl2bench_with_predicates"
    
    converter.save_to_file(str(output_base) + ".py")
    
    existing_dir = os.path.join(repo_dir, "src", "krrood_experiments", "owl2bench")
    files_to_compare = [
        "owl2bench_with_predicates.py",
        "owl2bench_with_predicates_properties.py",
        "owl2bench_with_predicates_base.py",
        "owl2bench_with_predicates.pyi"
    ]
    
    for filename in files_to_compare:
        generated_file = output_dir / filename
        existing_file = os.path.join(existing_dir, filename)
        
        with open(generated_file, "r") as f:
            generated_content = f.read()
        with open(existing_file, "r") as f:
            existing_content = f.read()
            
        assert generated_content == existing_content, f"Content mismatch in {filename}"
