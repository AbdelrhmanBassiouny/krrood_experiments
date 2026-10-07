"""
Measures how the work of eager chaining grows with the size of a group of individuals that share a home town, as in
the ablation "KRROOD without step 5": for each n, probe.py loads the OWL2Bench TBox plus n persons linked in a chain
by hasSameHomeTownWith, in eager mode, in a fresh process. Writes one JSON object per n.

Usage: python scaling.py TBOX OUT_DIR N...   (from code/earlier/experiments, with the earlier venv)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
tbox, out_dir, sizes = sys.argv[1], sys.argv[2], [int(n) for n in sys.argv[3:]]
rows = []
for n in sizes:
    output = subprocess.run([sys.executable, str(HERE / "probe.py"), tbox, str(n), "eager", "chain", out_dir],
                            capture_output=True, text=True, check=True).stdout
    result = json.loads(output.strip().splitlines()[-1])
    complete = all(len(partners) == n for partners in result["partners"].values())
    rows.append({"n": n, "seconds": result["seconds"], "attempts": result["update_source_calls"],
                 "facts": result["values_added"], "complete": complete})
    print(json.dumps(rows[-1]), flush=True)
Path(out_dir, "scaling.json").write_text(json.dumps(rows, indent=2))
