import os


from krrood_experiments.owl2bench.ontomatic.helpers import (
    generate_owl2bench_with_predicates,
)

# generate_lubm_with_predicates(clean=True)
resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
profile = "DL"
# profile = "RL"
file_path = None
out_file_name = None
if profile == "RL":
    file_path = os.path.join(resources_dir, "owl2bench_statements_unreasoned.rdf")
    out_file_name = "owl2bench_with_predicates.py"
elif profile == "DL":
    file_path = os.path.join(resources_dir, "OWL2DL-1_clean.owl")
    out_file_name = "owl2bench_with_predicates_dl.py"
output_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "src",
    "krrood_experiments",
    "owl2bench",
    "ontomatic",
    out_file_name,
)
generate_owl2bench_with_predicates(file_path, output_path)
