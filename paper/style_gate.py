"""AC0 — the four style checks that failed under attention, now mechanized.

Rules enforced by proofreading have regressed repeatedly: the abstract has
drifted past its limit three times, UK spellings have come back twice, and the
Z-phase read missed four dittographies that a regex finds instantly. Those
four classes are checks now, and the build fails on violation.

  1. Abstract word count <= 250, counted from the markdown source.
  2. UK-spelling denylist over manuscript and supplement.
  3. Dittography scan (repeated adjacent word or word-pair, prose only).
  4. PDF metadata: keywords present, author field empty. Checked at source
     level in the generated preamble, and against the compiled PDF when one
     is present.

Run: .venv/bin/python paper/style_gate.py
Exits non-zero on any violation. build_tex.py calls check_sources() and
refuses to write the .tex if it fails.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
MANUSCRIPT = HERE / "draft_t1.md"
SUPPLEMENT = HERE / "supplement_t.md"
TEX = HERE / "anomaly_theory.tex"
PDF = HERE / "anomaly_theory.pdf"

ABSTRACT_LIMIT = 250

# UK spellings and their inflections. The manuscript is US-spelled throughout;
# these are the forms that have actually regressed, not a general list.
UK_STEMS = [
    "favour", "modelling", "modelled", "programme", "behaviour", "licence",
    "colour", "organise", "organis", "analyse", "analys", "centre",
    "recognise", "recognis", "summarise", "summaris", "generalise",
    "generalis", "normalise", "normalis", "labelled", "labelling",
]
UK_ALLOW = {"analyses", "analysed_by_nothing"}  # "analyses" is the US plural noun
UK_RE = re.compile(r"\b(" + "|".join(UK_STEMS) + r")(s|d|ing|es|ed|ment|ments)?\b", re.I)

DITTO_ALLOW = {"had", "that"}

CODE_FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
MATH_BLOCK = re.compile(r"\$\$.*?\$\$", re.S)
MATH_INLINE = re.compile(r"\$[^$\n]*\$")
WORD = r"[A-Za-z][A-Za-z'’-]*"
# Only whitespace may separate the repeats: a sentence boundary ("the detector.
# The detector") carries punctuation and is therefore not a dittography.
DITTO_SINGLE = re.compile(rf"\b({WORD})\s+\1\b", re.I)
DITTO_BIGRAM = re.compile(rf"\b({WORD}\s+{WORD})\s+\1\b", re.I)


def _blank(m: re.Match) -> str:
    """Erase a span but keep its newlines, so line numbers stay truthful.

    A middot stands in for the erased span: without it, stripping inline math
    from "and $\\pi$ and $q$ range" would juxtapose the two "and"s and forge a
    dittography that is not in the prose.
    """
    return "·" + "\n" * m.group(0).count("\n")


def prose_of(text: str) -> str:
    """Markdown reduced to prose: no code, no math, no table rows.

    Line numbering is preserved so reported positions match the source file.
    """
    text = CODE_FENCE.sub(_blank, text)
    text = MATH_BLOCK.sub(_blank, text)
    text = INLINE_CODE.sub(_blank, text)
    text = MATH_INLINE.sub(_blank, text)
    keep = ["" if ln.lstrip().startswith("|") else ln for ln in text.splitlines()]
    return "\n".join(keep)


def abstract_of(text: str) -> str:
    m = re.search(r"^## Abstract\s*$(.*?)^## ", text, re.S | re.M)
    if not m:
        raise SystemExit("style gate: no '## Abstract' section found")
    return m.group(1)


def check_abstract(text: str) -> list[str]:
    words = re.findall(WORD, prose_of(abstract_of(text)))
    n = len(words)
    if n > ABSTRACT_LIMIT:
        return [f"abstract is {n} words, limit {ABSTRACT_LIMIT} (cut {n - ABSTRACT_LIMIT})"]
    print(f"        abstract: {n} words (limit {ABSTRACT_LIMIT})")
    return []


def check_spelling(name: str, text: str) -> list[str]:
    out = []
    for ln_no, line in enumerate(prose_of(text).splitlines(), 1):
        for m in UK_RE.finditer(line):
            if m.group(0).lower() in UK_ALLOW:
                continue
            out.append(f"{name}:{ln_no}: UK spelling '{m.group(0)}'")
    return out


def check_dittography(name: str, text: str) -> list[str]:
    prose = prose_of(text)
    out = []
    for rx, kind in ((DITTO_BIGRAM, "bigram"), (DITTO_SINGLE, "word")):
        for m in rx.finditer(prose):
            hit = m.group(1)
            if kind == "word" and hit.lower() in DITTO_ALLOW:
                continue
            line = prose[: m.start()].count("\n") + 1
            out.append(f"{name}:{line}: repeated {kind} '{m.group(0).strip()}'")
    return out


def check_pdf_metadata() -> list[str]:
    out = []
    if TEX.exists():
        tex = TEX.read_text()
        if "pdfkeywords" not in tex:
            out.append("anomaly_meaning.tex: no pdfkeywords in the preamble")
        if not re.search(r"pdfauthor\s*=\s*\{\s*\}", tex):
            out.append("anomaly_meaning.tex: pdfauthor is not set to empty")
    if PDF.exists():
        try:
            from pypdf import PdfReader

            meta = PdfReader(str(PDF)).metadata or {}
            author = (meta.get("/Author") or "").strip()
            keywords = (meta.get("/Keywords") or "").strip()
            if author:
                out.append(f"anomaly_meaning.pdf: /Author is non-empty ({author!r})")
            if not keywords:
                out.append("anomaly_meaning.pdf: /Keywords is empty")
            if not out:
                print(f"        pdf metadata: author empty, keywords set ({keywords[:40]}...)")
        except ImportError:
            print("        pdf metadata: pypdf not installed, source check only")
    return out


def check_sources() -> list[str]:
    """The three source-level checks. Used by build_tex.py as a build gate."""
    failures = []
    man = MANUSCRIPT.read_text()
    failures += check_abstract(man)
    targets = [(MANUSCRIPT, man)]
    if SUPPLEMENT.exists():
        targets.append((SUPPLEMENT, SUPPLEMENT.read_text()))
    for path, text in targets:
        failures += check_spelling(path.name, text)
        failures += check_dittography(path.name, text)
    return failures


def main() -> int:
    failures = check_sources() + check_pdf_metadata()
    if failures:
        print(f"FAIL  style gate: {len(failures)} violation(s)")
        for f in failures:
            print(f"        {f}")
        return 1
    print("ok    style gate: abstract, spelling, dittography, PDF metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
