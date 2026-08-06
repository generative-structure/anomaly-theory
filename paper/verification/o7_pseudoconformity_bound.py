"""I3 — the pseudo-conformity bound, verified.

Section 3's pseudo-conformity construction takes two component streams with
opposite deviation vectors,

    eps_1 = ( delta, -delta, 0, ..., 0 ),   eps_2 = -eps_1,

at equal weights, so the aggregate deviation is exactly zero: the pool conforms
to the first-digit law and NEITHER component does.

The construction is only legitimate while both B + eps_1 and B + eps_2 are
probability vectors. Placing O7 into T' corrected the admissible range from the
delta < B(1) that circulates in some presentations to

    0 < delta <= B(2) = log10(3/2) ~ 0.176.

That correction is a mathematical change, so it ships verified or not at all.
This file demonstrates, symbolically where possible and by exact rational
arithmetic elsewhere:

  1. the aggregate really is exactly zero (pseudo-conformity holds);
  2. neither component conforms, for every admissible delta;
  3. at delta = B(2) the vector is still valid -- the endpoint is INCLUDED;
  4. for ANY delta in (B(2), B(1)) the wider bound admits, B + eps_1 has a
     NEGATIVE entry -- so the wider bound licenses non-probability vectors;
  5. the binding constraint is the second digit under eps_1, not the first;
  6. requiring strictly positive digit probabilities would give the OPEN
     interval, as the manuscript states.

Run: python paper/verification/o7_pseudoconformity_bound.py
"""

import sys

import sympy as sp

d = sp.symbols("d", positive=True)
delta = sp.symbols("delta", positive=True)

# first-digit reference law
B = [sp.log(1 + sp.Rational(1, k), 10) for k in range(1, 10)]
B1, B2 = B[0], B[1]

checks = []


def check(name, cond):
    ok = bool(cond)
    checks.append((name, ok))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    return ok


print("O7 pseudo-conformity bound\n")

# --- the reference law is a probability vector -------------------------------
check("B sums to 1 exactly", sp.simplify(sum(B) - 1) == 0)
check("B(2) = log10(3/2)", sp.simplify(B2 - sp.log(sp.Rational(3, 2), 10)) == 0)
check("B(2) < B(1), so B(2) is the tighter bound",
      sp.simplify(B1 - B2) > 0)

# --- 1. the aggregate is exactly zero ----------------------------------------
eps1 = [delta, -delta] + [sp.Integer(0)] * 7
eps2 = [-e for e in eps1]
agg = [sp.simplify(sp.Rational(1, 2) * a + sp.Rational(1, 2) * b)
       for a, b in zip(eps1, eps2)]
check("aggregate deviation is identically zero (pseudo-conformity)",
      all(sp.simplify(x) == 0 for x in agg))

# --- 2. neither component conforms, for every admissible delta ---------------
mad1 = sp.simplify(sum(sp.Abs(e) for e in eps1) / 9)
check("component MAD = 2*delta/9 > 0 for all delta > 0",
      sp.simplify(mad1 - 2 * delta / 9) == 0)

# --- 3. the endpoint delta = B(2) is INCLUDED --------------------------------
p1_at_B2 = [sp.simplify(b + e.subs(delta, B2)) for b, e in zip(B, eps1)]
p2_at_B2 = [sp.simplify(b + e.subs(delta, B2)) for b, e in zip(B, eps2)]
check("at delta = B(2): B+eps_1 sums to 1", sp.simplify(sum(p1_at_B2) - 1) == 0)
check("at delta = B(2): B+eps_2 sums to 1", sp.simplify(sum(p2_at_B2) - 1) == 0)
check("at delta = B(2): every entry of B+eps_1 is >= 0",
      all(sp.simplify(x) >= 0 for x in p1_at_B2))
check("at delta = B(2): the second entry of B+eps_1 is EXACTLY zero "
      "(endpoint included, not approached)",
      sp.simplify(p1_at_B2[1]) == 0)
check("at delta = B(2): every entry of B+eps_2 is >= 0",
      all(sp.simplify(x) >= 0 for x in p2_at_B2))

# --- 4. the wider bound admits negative probabilities ------------------------
# For any delta in (B(2), B(1)) -- the range delta < B(1) admits and
# delta <= B(2) excludes -- the second entry of B + eps_1 is negative.
second = B2 - delta
check("for delta > B(2), the second entry of B+eps_1 is negative "
      "(the wider bound admits non-probability vectors)",
      sp.simplify(second.subs(delta, (B1 + B2) / 2)) < 0)
# sample the whole open interval, exactly
lo, hi = sp.nsimplify(B2), sp.nsimplify(B1)
bad = 0
for k in range(1, 20):
    t = lo + sp.Rational(k, 20) * (hi - lo)
    if sp.simplify(B2 - t) < 0:
        bad += 1
check(f"all 19 sampled delta in (B(2), B(1)) give a negative entry "
      f"({bad}/19)", bad == 19)

# --- 5. the binding constraint is the SECOND digit under eps_1 ---------------
# Under eps_1 the perturbed entries are B(1)+delta (grows) and B(2)-delta
# (shrinks); under eps_2 they are B(1)-delta and B(2)+delta. The first
# constraint to bind as delta grows is whichever shrinking entry is smaller.
check("B(2) - delta binds before B(1) - delta, so the eps_1 second digit "
      "is the binding constraint", sp.simplify(B2 - B1) < 0)
check("B(1) + delta <= 1 is slack at delta = B(2)",
      sp.simplify(B1 + B2 - 1) < 0)

# --- 6. strict positivity would give the OPEN interval -----------------------
check("requiring strictly positive digit probabilities excludes "
      "delta = B(2) exactly", sp.simplify(p1_at_B2[1]) == 0)

# --- numeric sanity ----------------------------------------------------------
print(f"\n  B(2) = log10(3/2) = {float(B2):.6f}   (manuscript states ~0.176)")
print(f"  B(1) = log10(2)    = {float(B1):.6f}   (the circulating wider bound)")
check("B(2) rounds to 0.176 as the manuscript states",
      abs(float(B2) - 0.176) < 5e-4)

n_ok = sum(1 for _, ok in checks if ok)
print(f"\n{n_ok} / {len(checks)} checks passed")
sys.exit(0 if n_ok == len(checks) else 1)
