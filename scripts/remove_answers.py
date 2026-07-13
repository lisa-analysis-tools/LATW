#!/usr/bin/env python
"""Generate student notebooks from the answer keys (dev-branch layout).

Answer notebooks are the SOURCE OF TRUTH and live at::

    tutorials/further/answers/<Name>-complete.ipynb

This script writes the student version of each to::

    tutorials/further/<Name>.ipynb

Markers (in answer-notebook code cells):

* a line containing ``# clear``       -> the WHOLE cell is blanked in the
  student copy (consecutive blanked cells are collapsed to one);
* a line ending with ``# clear-line`` -> only that line is removed
  (fill-in-the-blank; the surrounding scaffolding survives).

Output policy: the ANSWER notebooks keep their executed outputs (the Sphinx
docs import renders them with ``nbsphinx_execute = "never"``); the STUDENT
copies have all outputs and execution counts stripped.

Run from the repo root (idempotent — regenerating with unchanged answers
produces byte-identical student notebooks)::

    python scripts/remove_answers.py

Note: the legacy main-branch layout (``tutorials/tutorial_answers`` +
``# special clear``) is handled by the main branch's own copy of this
script; this dev version only knows the ``further/answers`` layout.
"""

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSWERS_DIR = os.path.join(ROOT, "tutorials", "further", "answers")
STUDENT_DIR = os.path.join(ROOT, "tutorials", "further")
SUFFIX = "-complete.ipynb"

CLEAR = "# clear"
CLEAR_LINE = "# clear-line"


def strip_cell(cell):
    """Return (student_cell, blanked_flag) for one answer cell."""
    if cell.get("cell_type") != "code":
        return cell, False
    cell = dict(cell)
    cell["outputs"] = []
    cell["execution_count"] = None
    source = cell.get("source", [])
    if isinstance(source, str):
        source = source.splitlines(keepends=True)
    if any(CLEAR in line and CLEAR_LINE not in line for line in source):
        cell["source"] = ["\n"]
        return cell, True
    cell["source"] = [
        line for line in source if not line.rstrip().endswith(CLEAR_LINE)
    ]
    return cell, False


def convert(answer_path, student_path):
    with open(answer_path) as f:
        nb = json.load(f)

    cells = []
    previous_blanked = False
    for cell in nb.get("cells", []):
        stripped, blanked = strip_cell(cell)
        if blanked and previous_blanked:
            continue  # collapse consecutive blanked cells
        previous_blanked = blanked
        cells.append(stripped)
    nb["cells"] = cells

    with open(student_path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    answers = sorted(glob.glob(os.path.join(ANSWERS_DIR, "*" + SUFFIX)))
    if not answers:
        print(f"no answer notebooks under {ANSWERS_DIR}", file=sys.stderr)
        return 1
    for answer_path in answers:
        name = os.path.basename(answer_path)[: -len(SUFFIX)] + ".ipynb"
        student_path = os.path.join(STUDENT_DIR, name)
        convert(answer_path, student_path)
        print(f"{os.path.relpath(answer_path, ROOT)} -> "
              f"{os.path.relpath(student_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
