# Replication scripts

Verification and build scripts for the manuscript *What an Anomaly Means*
(anonymous submission). This repository contains scripts only. No manuscript
text, bibliography, figures, or data are included.

All paths are relative to the repository root, and every script resolves its
inputs and outputs relative to its own location.

## Contents

```
paper/
  build_tex.py                        markdown -> LaTeX build (gated)
  style_gate.py                       abstract length, spelling, dittography, PDF metadata
  check_references.py                 citation bijection: cited keys <-> bib entries
  check_xrefs.py                      cross-reference resolution within the document
  verification/
    u0_invariance_symbolic.py         refinement invariance, the non-f-divergence
                                      counterexample, canonical-pair construction,
                                      the functional-equation hinge
    r1_r2_symbolic.py                 inventory-refinement invariance; binary-fire
                                      information decomposition
    o7_pseudoconformity_bound.py      admissible range of the pseudo-conformity
                                      construction
  posthoc/
    cluster_paired.py                 cluster-aware paired bootstrap scorer (frozen)
```

## Requirements

Python 3.11 or later.

```
pip install -r requirements.txt
```

`pypdf` is optional: `style_gate.py` checks the compiled PDF's metadata when it
is installed and falls back to a source-level check when it is not.

The LaTeX build additionally requires `pandoc` and `latexmk` on `PATH`.

## Running the verification suites

These four are self-contained. They read no data and no manuscript, and can be
run directly from a clone:

```
python paper/verification/u0_invariance_symbolic.py     # 46 checks
python paper/verification/r1_r2_symbolic.py             # 26 checks
python paper/verification/o7_pseudoconformity_bound.py  # 16 checks
python paper/posthoc/cluster_paired.py --smoke          # synthetic self-test
```

Each exits `0` when every check passes and non-zero otherwise. Claims are
checked symbolically where a symbolic statement is available and in exact
rational arithmetic otherwise; no check depends on floating-point tolerance
except where a tolerance is stated as a frozen constant.

`cluster_paired.py` has no command-line options and no free parameters at run
time: every parameter is a module constant fixed before any run. Invoked
without `--smoke` it refuses to run, because the real run is gated on recorded
approval of the preregistered freeze.

## Running the build and the source gates

`build_tex.py`, `style_gate.py`, `check_references.py`, and `check_xrefs.py`
operate on the manuscript sources, which are not distributed here. Place
`draft_t1.md` and `references.bib` in `paper/` and run from the repository
root:

```
python paper/style_gate.py
python paper/check_references.py
python paper/check_xrefs.py
python paper/build_tex.py && latexmk -pdf paper/anomaly_theory.tex
```

`build_tex.py` runs the style gate and the cross-reference check first and
refuses to write the `.tex` on any violation. The generated preamble sets an
empty `pdfauthor` and empty `pdfsubject`; `style_gate.py` verifies this in the
generated source and, when `pypdf` is available, against the compiled PDF.

## License

Not yet specified.
