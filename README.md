# Replication materials

Verification and build scripts for the manuscript *What an Anomaly Means:
Validity, Diagnosis, and the Limits of Semantic Identification*, together with
the bibliography and the preregistration that the frozen scorer commits
against. No manuscript text, figures, or data are included.

Archived at Zenodo, DOI
[10.5281/zenodo.21830924](https://doi.org/10.5281/zenodo.21830924), where the
paper carries its authorship and affiliation.

All paths are relative to the repository root, and every script resolves its
inputs and outputs relative to its own location.

## Contents

```
paper/
  build_tex.py                        markdown -> LaTeX build (gated)
  style_gate.py                       abstract length, spelling, dittography, PDF metadata
  check_references.py                 citation bijection: cited keys <-> bib entries
  check_xrefs.py                      cross-reference resolution within the document
  references.bib                      34 entries, all cited; provenance line on each
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
  prereg/
    cluster_paired_uncertainty.md     the preregistration the scorer commits against
    Response_to_cluster_paired_uncertainty.md
                                      the review of it that revisions 2-4 apply
```

## The preregistration

`paper/posthoc/cluster_paired.py` and `paper/prereg/cluster_paired_uncertainty.md`
commit together, before any run. The memo fixes every parameter the scorer
uses, the comparisons, and the clause each interval licenses, so that no
post-run discretion remains; the scorer holds those same values as module
constants. Read them side by side — either one alone is only half the record.

`Response_to_cluster_paired_uncertainty.md` is the review that the memo's
revisions 2 through 4 respond to. Its numbered items are cited throughout the
memo, so the revision history is not readable without it.

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

`references.bib` is here, but `build_tex.py`, `style_gate.py`,
`check_references.py`, and `check_xrefs.py` also read the manuscript source,
which is not distributed here. Place `draft_t1.md` in `paper/` and run from the
repository root:

```
python paper/style_gate.py
python paper/check_references.py
python paper/check_xrefs.py
python paper/build_tex.py && latexmk -pdf paper/anomaly_theory.tex
```

`build_tex.py` runs the style gate and the cross-reference check first and
refuses to write the `.tex` on any violation.

The author block, affiliation and any corresponding-author footnote are not
carried in this copy: `build_tex.py`'s preamble leaves `\author{}` and
`pdfauthor={}` empty, and `style_gate.py`'s `AUTHOR` constant is empty to
match. Set both to the author's name to build a named submission —
`style_gate.py` then requires the compiled PDF to carry exactly that name, so
losing attribution is a build failure rather than a silent omission.

## License

Not yet specified.
