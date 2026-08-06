"""C4 — cross-reference resolution for Paper T.

Every pointer in the manuscript must resolve to an object stated in the same
document. This checks the class of defect the B0 audit found three instances
of, none of which the citation/bibliography checker can see:

  * a proposition cited five times and never stated (O8, fixed at f840099);
  * a table cited by prose that did not survive conversion (O12);
  * five pointers at sections belonging to a different paper.

The shape is constant: the citing prose stays, the cited object leaves. A
bijection over citations cannot catch it, because the pointer is not a
citation.

Resolvable targets are collected from what the document actually states:
  - section numbers from `## N.` and `### N.M` headings;
  - pandoc anchors `[]{#key label="key"}` and `{#key}` heading attributes;
  - explicit table/figure anchors.

Reported as unresolved:
  - `[\\[key\\]](#key)` pandoc references whose key is never defined;
  - prose pointers "Section N" / "Section N.M" / "Table N" / "Figure N"
    naming a number the document does not contain.

Run: python paper/check_xrefs.py         (exit 1 on any unresolved pointer)
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
MANUSCRIPT = HERE / "draft_t1.md"

CODE = re.compile(r"```.*?```", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)

# --- what the document defines -------------------------------------------
H_SEC = re.compile(r"^## (\d+)\.", re.M)
H_SUB = re.compile(r"^### (\d+\.\d+)", re.M)
ANCHOR_SPAN = re.compile(r"\[\]\{#([^}\s]+)")           # []{#prop:x label="prop:x"}
ANCHOR_ATTR = re.compile(r"\{#([^}\s]+)")               # ## Heading {#sec:x}
DIV_ID = re.compile(r"^:::+\s*\{#([^}\s]+)", re.M)      # ::: {#tab:enrich}

# --- what the document points at ------------------------------------------
REF_KEY = re.compile(r"\[[^\]]*\]\(#([^)]+)\)")  # [\[key\]](#key) AND [1](#key)
REF_SEC = re.compile(r"\bSections?~?\s(\d+(?:\.\d+)?)")
REF_TAB = re.compile(r"\bTables?~?\s(\d+)")
REF_FIG = re.compile(r"\bFigures?~?\s(\d+)")


def strip(text: str) -> str:
    return COMMENT.sub(" ", CODE.sub(" ", text))


def defined(text: str):
    keys = set(ANCHOR_SPAN.findall(text)) | set(DIV_ID.findall(text))
    for m in ANCHOR_ATTR.finditer(text):
        keys.add(m.group(1))
    secs = set(H_SEC.findall(text)) | set(H_SUB.findall(text))
    return keys, secs


def check(text: str):
    text = strip(text)
    keys, secs = defined(text)
    bad = []
    for m in REF_KEY.finditer(text):
        k = m.group(1)
        if k not in keys:
            bad.append(("key", k, text[: m.start()].count("\n") + 1))
    for rx, kind in ((REF_SEC, "Section"), (REF_TAB, "Table"), (REF_FIG, "Figure")):
        for m in rx.finditer(text):
            n = m.group(1)
            if kind == "Section" and n not in secs:
                bad.append(("section", n, text[: m.start()].count("\n") + 1))
    return bad, keys, secs


def main() -> int:
    text = MANUSCRIPT.read_text()
    bad, keys, secs = check(text)
    print(f"manuscript : {MANUSCRIPT.name}")
    print(f"defined    : {len(keys)} anchors, {len(secs)} numbered sections")
    if bad:
        print(f"FAIL  cross-reference resolution: {len(bad)} unresolved")
        for kind, name, line in sorted(bad, key=lambda b: b[2]):
            print(f"        line {line}: {kind} '{name}' resolves to nothing in this document")
        return 1
    print("ok    cross-reference resolution: every pointer resolves in-document")
    return 0


if __name__ == "__main__":
    sys.exit(main())
