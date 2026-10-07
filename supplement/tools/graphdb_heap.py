"""
GraphDB's Java heap in use while it loads each input, from its G1 GC log (reproduce.sh starts GraphDB with
-Xlog:gc) and the marks that reproduce.sh writes around each load (after a forced GC before it, before a forced GC
after it): the heap after the last GC pause before the load ("before"), the largest heap after a GC pause during the
load ("peak"; an upper bound, as it may include garbage), and their difference ("increase"). GraphDB's server has a
fixed heap, so its RSS says little about the memory that loading needs.

Usage: python graphdb_heap.py MARKS OUTPUT_JSON GC_LOG...  (one GC log per start of GraphDB)
MARKS has lines "start <input> <unix time>" and "end <input> <unix time>".
"""
import json
import re
import sys
from datetime import datetime

PAUSE = re.compile(r"^\[([^\]]+)\].*GC\(\d+\) (Pause .*?) (\d+)M->(\d+)M\((\d+)M\)")
marks_file, output, gc_logs = sys.argv[1], sys.argv[2], sys.argv[3:]
events = []
for gc_log in gc_logs:
    for line in open(gc_log):
        match = PAUSE.search(line)
        if match:
            stamp = datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
            events.append((stamp, match[2], int(match[4])))
events.sort()
marks = {}
for line in open(marks_file):
    kind, input_name, stamp = line.split()
    marks.setdefault(input_name, {})[kind] = float(stamp)
result = {}
for input_name, mark in marks.items():
    if "end" not in mark:
        continue
    before = [heap for stamp, _, heap in events if stamp <= mark["start"]]
    during = [heap for stamp, _, heap in events if mark["start"] < stamp < mark["end"]]
    if before and during:
        result[input_name] = {"heap_before_mib": before[-1], "heap_peak_mib": max(during),
                              "heap_increase_mib": max(during) - before[-1], "pauses_during_load": len(during)}
with open(output, "w") as file:
    json.dump(result, file, indent=2)
print(json.dumps(result))
