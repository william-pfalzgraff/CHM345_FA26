#!/usr/bin/env python3
"""Unlock nbgrader-released notebooks: make every cell editable and deletable.

nbgrader's release step stamps cells with "editable": false / "deletable":
false, which Jupyter's UI enforces. This removes those flags (leaving the
rest of the metadata untouched) so the instructor can edit freely.

Usage:  python3 unlock_notebook.py notebook1.ipynb [notebook2.ipynb ...]
"""
import json
import sys

for path in sys.argv[1:]:
    with open(path) as f:
        nb = json.load(f)
    n = 0
    for cell in nb.get("cells", []):
        md = cell.get("metadata", {})
        for key in ("editable", "deletable"):
            if md.get(key) is False:
                del md[key]
                n += 1
    with open(path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{path}: removed {n} lock flag(s)")
