import os


from krrood_experiments.owl2bench.ontomatic.helpers import (
    generate_owl2bench_with_predicates,
)

# generate_lubm_with_predicates(clean=True)
resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
file_path = os.path.join(resources_dir, "owl2bench_statements_unreasoned.rdf")
output_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "src",
    "krrood_experiments",
    "owl2bench",
    "ontomatic",
    "owl2bench_with_predicates.py",
)
generate_owl2bench_with_predicates(file_path, output_path)
