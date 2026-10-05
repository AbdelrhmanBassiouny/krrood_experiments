#!/usr/bin/env bash
# Regenerate the Ontomatic OWL2Bench (RL) model from resources/owl2bench_statements_unreasoned.rdf with the installed
# krrood generator, format it with black, and re-apply the one manual edit of the committed model
# (SportsLover.loves is typed Set[Interest], the generator produces Set[Sports]).
set -euo pipefail
cd "$(dirname "$0")/../.."
python scripts/generate_model_using_ontomatic.py
target=src/krrood_experiments/owl2bench/ontomatic
python -m black -q "$target/owl2bench_with_predicates.py"
python - <<'PY'
import re
from pathlib import Path
path = Path("src/krrood_experiments/owl2bench/ontomatic/owl2bench_with_predicates.py")
source = path.read_text()
block = re.search(r"class SportsLover\(.*?(?=\n@dataclass)", source, re.S)
fixed = block.group(0).replace("loves: Set[Sports]", "loves: Set[Interest]")
path.write_text(source.replace(block.group(0), fixed))
PY
git --no-pager diff --stat -- "$target"
