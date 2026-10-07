"""
Peak RSS (MiB) of a fresh Python process after the imports that a loading worker performs before it loads any data,
for the systems that run_loading.py measures in a worker process. The memory increase during loading is the peak RSS
of a run minus this value. Each measurement runs in its own process, three times.

Usage: python import_memory.py OUTPUT_JSON   (from code/earlier/experiments, with the earlier venv)
"""
import json
import subprocess
import sys

IMPORTS = {
    "krrood": "from krrood_experiments.aamas27 import loading_worker as w; w._import_krrood()",
    "owlready2_pellet": "import krrood_experiments.aamas27.loading_worker, owlready2",
    "rdflib_owlrl": "import krrood_experiments.aamas27.loading_worker, owlrl, rdflib",
    "reasonable_owlrl": "import krrood_experiments.aamas27.loading_worker, rdflib, reasonable",
    # The Nemo worker imports nothing beyond the worker module; the nmo child process is part of the measured tree.
    "nemo_owlrl": "import krrood_experiments.aamas27.loading_worker",
}
PROBE = "; import resource; print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)"
result = {}
for system, code in IMPORTS.items():
    values = [float(subprocess.run([sys.executable, "-c", code + PROBE], capture_output=True, text=True,
                                   check=True).stdout.split()[-1]) for _ in range(3)]
    result[system] = {"import_rss_mib": values, "max_mib": max(values), "imports": code}
result["krrood_ormatic"] = result["krrood_eager_symmetric_transitive"] = {"same_as": "krrood"}
with open(sys.argv[1], "w") as file:
    json.dump(result, file, indent=2)
print({system: entry.get("max_mib", entry.get("same_as")) for system, entry in result.items()})
