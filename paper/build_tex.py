r"""Build anomaly_theory.tex/pdf from draft_t1.md.

Adapted from the anomaly-meaning build. Differences, all forced by T's
mixed-provenance source:

  * T's markdown is half AM markdown and half pandoc-converted PD LaTeX, so the
    preprocessor normalizes three PD artifacts: fenced divs (::: definition)
    become bold-led paragraphs, stray pandoc label spans are dropped, and
    pandoc @-citations are rendered as literal bracketed keys because T has no
    merged bibliography yet (M2.3). Unresolved keys are meant to be visible.
  * Block seam markers are gone from the source (all fifteen resolved at H2);
    the rule-rendering branch is retained so that reintroducing a marker makes
    it visible rather than silently invisible.
  * No figure floats: T carries none yet.

The style gate runs first and aborts the build on violation.

Run: python paper/build_tex.py && latexmk -pdf paper/anomaly_theory.tex
"""

import re
import subprocess
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "draft_t1.md"
BIB = HERE / "references.bib"

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=1.15in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{textcomp}
\usepackage{booktabs,longtable,array,calc}
\usepackage{amsmath,amssymb}
\usepackage[hyphens]{url}
\usepackage{needspace}
\usepackage{xcolor}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black]{hyperref}
\hypersetup{
  pdfauthor={},
  pdfsubject={},
  pdfcreator={},
  pdfkeywords={mechanism diagnosis; nonidentifiability; mixture models;
    information measures; preregistration; anomaly detection}
}
\newcounter{none}     % pandoc longtable + hyperref workaround
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setcounter{secnumdepth}{0}
\setlength{\emergencystretch}{3em}
\newcommand{\seam}[1]{%
  \par\medskip\noindent\textcolor{gray}{\rule{\linewidth}{0.4pt}}\par
  \nopagebreak\noindent{\footnotesize\textcolor{gray}{\textsf{#1}}}\par
  \nopagebreak\noindent\textcolor{gray}{\rule{\linewidth}{0.4pt}}\par\medskip}
\title{\bfseries What an Anomaly Means\\[2pt]
  \large\normalfont\itshape Working title}
\author{Anonymous submission}
\date{}
% --- citeproc bibliography support -----------------------------------------
% Verbatim from `pandoc --citeproc -s -t latex` (pandoc's own template block).
% T hand-rolls its preamble rather than using pandoc's template, so these
% definitions have to be carried explicitly or CSLReferences is undefined.
\NewDocumentCommand\citeproctext{}{}
\NewDocumentCommand\citeproc{mm}{%
  \begingroup\def\citeproctext{#2}\cite{#1}\endgroup}
\makeatletter
 \let\@cite@ofmt\@firstofone
 \def\@biblabel#1{}
 \def\@cite#1#2{{#1\if@tempswa , #2\fi}}
\makeatother
\newlength{\cslhangindent}
\setlength{\cslhangindent}{1.5em}
\newlength{\csllabelwidth}
\setlength{\csllabelwidth}{3em}
\newenvironment{CSLReferences}[2]
 {\begin{list}{}{%
  \setlength{\itemindent}{0pt}
  \setlength{\leftmargin}{0pt}
  \setlength{\parsep}{0pt}
  \ifodd #1
   \setlength{\leftmargin}{\cslhangindent}
   \setlength{\itemindent}{-1\cslhangindent}
  \fi
  \setlength{\itemsep}{#2\baselineskip}}}
 {\end{list}}
\newcommand{\CSLBlock}[1]{\hfill\break\parbox[t]{\linewidth}{\strut\ignorespaces#1\strut}}
\newcommand{\CSLLeftMargin}[1]{\parbox[t]{\csllabelwidth}{\strut#1\strut}}
\newcommand{\CSLRightInline}[1]{\parbox[t]{\linewidth - \csllabelwidth}{\strut#1\strut}}
\newcommand{\CSLIndent}[1]{\hspace{\cslhangindent}#1}
% ---------------------------------------------------------------------------

\begin{document}
\maketitle
\thispagestyle{empty}
"""

POST_PANDOC_UNICODE = {
    "\u0131\u0301": "\u00ed",  # dotless-i + combining acute (BibTeX's D\'{\i}az)
    "\u2032": "$'$",       # prime
    "\u2033": "$''$",      # double prime
    "\u2212": "--",        # minus sign
    "\u2264": "$\\le$",
    "\u2265": "$\\ge$",
    "\u00d7": "$\\times$",
}

UNICODE_MAP = {
    "‖": r"\ensuremath{\Vert}", "⊥": r"\ensuremath{\perp}",
    "χ²": r"\ensuremath{\chi^2}", "χ": r"\ensuremath{\chi}",
    "Σ": r"\ensuremath{\Sigma}", "ε": r"\ensuremath{\varepsilon}",
    "α": r"\ensuremath{\alpha}", "ρ": r"\ensuremath{\rho}",
    "ν": r"\ensuremath{\nu}", "θ": r"\ensuremath{\theta}",
    "π": r"\ensuremath{\pi}", "λ": r"\ensuremath{\lambda}",
    "μ": r"\ensuremath{\mu}", "δ": r"\ensuremath{\delta}",
    "Φ": r"\ensuremath{\Phi}", "Γ": r"\ensuremath{\Gamma}",
    "→": r"\ensuremath{\rightarrow}", "←": r"\ensuremath{\leftarrow}",
    "≥": r"\ensuremath{\geq}", "≤": r"\ensuremath{\leq}",
    "≈": r"\ensuremath{\approx}", "≠": r"\ensuremath{\neq}",
    "×": r"\ensuremath{\times}", "·": r"\ensuremath{\cdot}",
    "∞": r"\ensuremath{\infty}", "∈": r"\ensuremath{\in}",
    "∎": r"\ensuremath{\blacksquare}", "−": "-", "¢": r"\textcent{}",
    "—": r"\textemdash{}", "–": r"\textendash{}",
    "◻": r"\ensuremath{\square}", " ": r"\,",
}

DIV_LABEL = {
    "definition": "Definition", "theorem": "Theorem",
    "proposition": "Proposition", "corollary": "Corollary",
    "proof": "Proof", "lemma": "Lemma", "remark": "Remark",
}


def preprocess(md: str) -> str:
    # title block is supplied by the preamble
    md = re.sub(r"^# What an Anomaly Means\n+\*Working title\.\*\n+\*Anonymous submission\.\*\n",
                "", md, flags=re.M)
    # seams become visible rules rather than being silently dropped as HTML
    def seam(m):
        body = m.group(1).strip()
        body = body.replace("|", "---").replace("_", r"\_")
        return f"\n\n```{{=latex}}\n\\seam{{{body}}}\n```\n\n"
    md = re.sub(r"<!--\s*(BLOCK .*?)\s*-->", seam, md, flags=re.S)
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)          # other comments drop
    # pandoc fenced divs -> bold-led paragraphs (no theorem counters in a draft)
    def open_div(m):
        cls = m.group(1).lower()
        return f"\n**{DIV_LABEL.get(cls, cls.title())}.** "
    md = re.sub(r"^:::+\s*\{?\.?(\w+)\}?\s*$", open_div, md, flags=re.M)
    md = re.sub(r"^:::+\s*$", "\n", md, flags=re.M)
    # stray pandoc label spans and heading attributes
    md = re.sub(r"\[\]\{#[^}]*\}", "", md)
    md = re.sub(r"\s*\{#[^}]*\}", "", md)
    # citations: rendered by citeproc against BIB when it exists, otherwise
    # shown as literal bracketed keys so unresolved ones stay visible.
    if not BIB.exists():
        def cite(m):
            keys = re.findall(r"@([A-Za-z0-9_:.\-]+)", m.group(0))
            return "[" + "; ".join(keys) + "]" if keys else m.group(0)
        md = re.sub(r"\[@[^\]]+\]", cite, md)
        md = re.sub(r"(?<![\[\w])@([A-Za-z][A-Za-z0-9_:.\-]{3,})", r"[\1]", md)
    else:
        n_head = md.count("\n## References")
        assert n_head == 1, f"expected exactly one References heading, found {n_head}"
        md = md.replace("\n## References", "\n## References\n\n::: {#refs}\n:::\n", 1)
    for k, v in UNICODE_MAP.items():
        md = md.replace(k, v)
    return md


def main():
    from style_gate import check_sources
    from check_xrefs import check as check_xrefs_fn
    xbad, _, _ = check_xrefs_fn(SRC.read_text())
    failures = check_sources()
    failures += [f"unresolved {k} '{n}' (line {l})" for k, n, l in xbad]
    if failures:
        print(f"BUILD ABORTED — style gate: {len(failures)} violation(s)")
        for f in failures:
            print(f"        {f}")
        raise SystemExit(1)

    tmp = HERE / "_t_build.md"
    tmp.write_text(preprocess(SRC.read_text()))
    body = subprocess.run(
        ["pandoc", "-f", "markdown+raw_attribute", "-t", "latex", str(tmp)]
        + (["--citeproc", f"--bibliography={BIB}"] if BIB.exists() else []),
        capture_output=True, text=True, check=True).stdout
    # citeproc output bypasses preprocess(), so normalize it here. NFC composes
    # combining accents (Acz + U+0301 -> Aczel-with-acute) that pdflatex's utf8
    # inputenc cannot render decomposed; the map catches what NFC leaves behind.
    body = unicodedata.normalize("NFC", body)
    for k, v in POST_PANDOC_UNICODE.items():
        body = body.replace(k, v)
    stray = sorted({c for c in body
                    if (0x300 <= ord(c) <= 0x36F)          # combining marks
                    or (ord(c) > 0x2000
                        and c not in "\u2013\u2014\u2018\u2019\u201c\u201d\u2026")})
    if stray:
        raise SystemExit("BUILD ABORTED - unmapped unicode in pandoc output: "
                         + ", ".join(f"U+{ord(c):04X}" for c in stray))
    (HERE / "anomaly_theory.tex").write_text(PREAMBLE + body + "\n\\end{document}\n")
    tmp.unlink()
    print("wrote paper/anomaly_theory.tex")


if __name__ == "__main__":
    main()
