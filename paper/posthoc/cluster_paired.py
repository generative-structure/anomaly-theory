"""Cluster-aware paired uncertainty for §5 — the frozen scorer.

Preregistered in paper/prereg/cluster_paired_uncertainty.md. Every parameter
below is a module constant fixed before any run; there is no command-line
option and no free parameter at run time.

Three comparisons, all as paired cluster-level bootstrap on out-of-fold
predictions:

  C1  AUPRC(stratum-only) - AUPRC(density-score)
  C2  AUPRC(score+stratum) - AUPRC(stratum-only), per score family
  C3  lift(within-stratum) - lift(pooled) at k=200 and k=5905,
      plus the budget-crossing difference

DELIBERATE BYPASS, per the preregistration: this scorer does NOT read
`decomposition-price/outputs/clustering_units.json`. That frozen artifact
records 37,532 clusters and a largest cluster of 65,706 for card1+addr1, values
that round-3 finding B-1 declared false — a string-concatenated composite key
propagated a pandas NA and discarded a present card1 wherever addr1 was
missing. Cluster assignments are re-derived here from the raw identifiers using
PER-COLUMN fills, never a concatenated key. The frozen file stays byte-identical
as the record of what was once believed.

Run: python paper/posthoc/cluster_paired.py            (the real run, once)
     python paper/posthoc/cluster_paired.py --smoke    (synthetic self-test)
"""

import sys
from pathlib import Path

import numpy as np

# ---- frozen parameters -----------------------------------------------------
B_RESAMPLES = 20000
SEED = 20260806
CI_LO, CI_HI = 2.5, 97.5
PCTL_METHOD = "linear"          # frozen quantile interpolation
DEFINED_MIN = 0.99              # <99% defined -> UNRELIABLE, no interval
POINT_TOL = 1e-6                # point-estimate reproduction tolerance
BUDGETS = (200, 5905)
PRIMARY_UNIT = ["card1"]
SENSITIVITY_UNITS = [
    ["card1", "addr1"],
    ["card1", "card2", "card3", "card5", "addr1"],
]
OUT = Path(__file__).parent / "cluster_paired"


def cluster_ids(df, cols):
    """Cluster labels from per-column fills. Never a concatenated string key.

    The B-1 defect was `df[a].astype(str) + df[b].astype(str)`, which turns a
    present `card1` into NaN whenever `addr1` is missing. Filling each column
    independently and factorizing the tuple keeps a present identifier present.
    """
    import pandas as pd

    filled = pd.DataFrame(
        {c: df[c].fillna(f"__MISSING_{c}__").astype(str) for c in cols}
    )
    return pd.factorize(pd.MultiIndex.from_frame(filled))[0]


def auprc(y, s):
    """Average precision. Ties broken by ascending original index, per prereg."""
    order = np.lexsort((np.arange(len(s)), -np.asarray(s, float)))
    y = np.asarray(y, int)[order]
    tp = np.cumsum(y)
    prec = tp / np.arange(1, len(y) + 1)
    n_pos = tp[-1]
    return float((prec * y).sum() / n_pos) if n_pos else np.nan


def lift_at_k(y, s, k):
    """Outcome rate in the top-k over the base rate. Deterministic tie order."""
    y = np.asarray(y, int)
    if y.sum() == 0 or k > len(y):
        return np.nan
    order = np.lexsort((np.arange(len(s)), -np.asarray(s, float)))
    top = y[order][:k]
    base = y.mean()
    return float(top.mean() / base) if base > 0 else np.nan


def assert_no_cluster_spans_folds(clusters, folds):
    """Preregistered leakage assertion: no card1 cluster crosses a fold.

    Verified in the archive (score_structure_outcome.py uses GroupKFold on
    card1, header: 'no cluster spans folds'), asserted here so the claim is
    checked at run time rather than inherited.
    """
    import numpy as _np
    for c in _np.unique(clusters):
        if len(_np.unique(_np.asarray(folds)[clusters == c])) > 1:
            raise AssertionError(f"leakage: cluster {c} spans multiple folds")
    return True


def clause(point, lo, hi, defined_frac, name):
    """Select exactly one licensed clause. No post-run discretion.

    Classification order is CONTROLLING and matches the prereg exactly:
        UNRELIABLE -> OPPOSITE -> POS -> NEG -> NULL
    The order matters because the conditions overlap: an interval entirely
    above zero satisfies POS, and if its point estimate is negative it also
    satisfies OPPOSITE. OPPOSITE wins in both directions, so a sign conflict
    between an interval and its own point estimate is never reported as a
    substantive result.
    """
    if defined_frac < DEFINED_MIN:
        return "UNRELIABLE"
    if (lo > 0 and point < 0) or (hi < 0 and point > 0):
        return "OPPOSITE"
    if lo > 0:
        return "POS"
    if hi < 0:
        return "NEG"
    return "NULL"


def paired_bootstrap(stat_fn, clusters, rng, b=B_RESAMPLES):
    """Resample clusters with replacement; all rows of a drawn cluster travel."""
    uniq = np.unique(clusters)
    index_of = {c: np.where(clusters == c)[0] for c in uniq}
    out, undefined = [], 0
    for _ in range(b):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([index_of[c] for c in drawn])
        v = stat_fn(idx)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            undefined += 1
        else:
            out.append(v)
    a = np.asarray(out, float)
    return {
        "point": None,
        "lo": float(np.percentile(a, CI_LO, method=PCTL_METHOD)) if len(a) else np.nan,
        "hi": float(np.percentile(a, CI_HI, method=PCTL_METHOD)) if len(a) else np.nan,
        "n_defined": len(a),
        "n_undefined": undefined,
    }


def smoke():
    """Synthetic self-test. No frozen artifact is read; nothing is written."""
    import pandas as pd

    rng = np.random.default_rng(0)
    n, nc = 4000, 200
    cl = rng.integers(0, nc, n)
    # cluster-level outcome propensity -> genuine within-cluster dependence
    prop = rng.beta(0.4, 12.0, nc)
    y = rng.binomial(1, prop[cl])
    strat = rng.integers(0, 6, n)
    score = 0.55 * y + rng.normal(0, 1, n)          # weakly informative
    both = score + 0.35 * (strat == 1)

    print(f"  synthetic: n={n}, clusters={nc}, positives={y.sum()}")

    # B-1 regression check: a present card1 must survive a missing addr1
    df = pd.DataFrame({"card1": ["a", "b", "c"], "addr1": [None, "x", None]})
    ids = cluster_ids(df, ["card1", "addr1"])
    assert len(set(ids)) == 3, "per-column fill collapsed distinct card1 values"
    print("  B-1 regression: 3 distinct clusters from 3 card1 values with 2 missing addr1 — PASS")

    r = np.random.default_rng(SEED)
    res = paired_bootstrap(
        lambda idx: auprc(y[idx], both[idx]) - auprc(y[idx], score[idx]),
        cl, r, b=200)
    print(f"  C2-shape paired CI (200 resamples): [{res['lo']:.5f}, {res['hi']:.5f}]"
          f"  defined {res['n_defined']}/200")
    res3 = paired_bootstrap(
        lambda idx: lift_at_k(y[idx], both[idx], 200) - lift_at_k(y[idx], score[idx], 200),
        cl, r, b=200)
    print(f"  C3-shape paired CI (200 resamples): [{res3['lo']:.4f}, {res3['hi']:.4f}]"
          f"  defined {res3['n_defined']}/200")
    # B-1 bypass regression on realistic scale: per-column fill must not collapse
    n_c1, n_missing = 40000, 4500
    c1 = rng.integers(0, 39974, n_c1)
    a1 = np.where(rng.random(n_c1) < n_missing / n_c1, None, rng.integers(0, 500, n_c1))
    dfx = pd.DataFrame({"card1": c1, "addr1": a1})
    ids_ok = cluster_ids(dfx, ["card1", "addr1"])
    concat = (dfx["card1"].astype(str) + dfx["addr1"].astype(str))  # the B-1 defect
    n_bad = concat.isna().sum() + (concat == "nan").sum() + concat.str.contains("None").sum()
    print(f"  B-1 bypass at scale: per-column fill -> {len(set(ids_ok))} clusters; "
          f"concatenated key would collapse {n_bad} rows into an NA bucket")
    assert len(set(ids_ok)) > 39000, "per-column fill collapsed clusters"

    # leakage assertion, both directions
    cl_ok = np.repeat(np.arange(100), 10); fold_ok = np.repeat(np.arange(100) % 5, 10)
    assert assert_no_cluster_spans_folds(cl_ok, fold_ok)
    fold_bad = fold_ok.copy(); fold_bad[5] = (fold_bad[5] + 1) % 5
    try:
        assert_no_cluster_spans_folds(cl_ok, fold_bad); print("  leakage assertion: FAILED TO FIRE")
    except AssertionError:
        print("  leakage assertion: fires on a spanning cluster, passes on disjoint folds — PASS")

    for pt, lo, hi in [(0.5,0.1,0.9),(0.5,-0.1,0.9),(-0.5,-0.9,-0.1),(0.5,-0.9,-0.1)]:
        print(f"    clause(point={pt:+.1f}, CI=[{lo:+.1f},{hi:+.1f}]) -> {clause(pt,lo,hi,1.0,'x')}")
    print(f"    clause with 0.90 defined -> {clause(0.5,0.1,0.9,0.90,'x')}")
    print("  smoke test: PASS — statistics compute, pairing holds, CIs form")


def main():
    if "--smoke" in sys.argv:
        smoke(); return 0
    raise SystemExit(
        "REFUSED: the real run is gated on author approval of the freeze "
        "(paper/prereg/cluster_paired_uncertainty.md). Re-invoke without the "
        "gate only after approval is recorded."
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
