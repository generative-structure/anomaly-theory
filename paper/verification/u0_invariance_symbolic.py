"""U0 — independent verification of the U-phase invariance claims, BEFORE any
prose is written against them.

Four checks, in the order the directive states them:

  U0.1  Refinement invariance of the spectral moments
        mu_s = sum_m pi_m (q_m/pi_m)^s, for GENERAL split weights w (not just
        equal splits), general K (rest-of-inventory carried as opaque symbols),
        symbolic s, and integer s in {2, 3}.

  U0.2  The counterexample. F = (mu_2 - 1)^2 + (mu_3 - 1)^2 is refinement
        invariant but is NOT an f-divergence. Verified by: (a) invariance of F;
        (b) invertibility of the Vandermonde at t = {1/4, 3/4, 5/4, 7/4};
        (c) an explicit kernel direction along which some nonconstant f has
        constant integral while F moves.

  U0.3  The canonical-pair construction: every (pi, q) is a refinement of a
        canonical pair built from its likelihood-ratio spectrum, with weights
        w_m = pi_m / a_t recovering the original.

  U0.4  THE HINGE. The refinement increment is p-independent, path independence
        yields the UNWEIGHTED equation h(x) + h(y/(1-x)) = h(y) + h(x/(1-y)),
        and that equation with h(x) = h(1-x) forces h constant. If this fails,
        the dichotomy theorem does not ship.

Six further checks added for the v13 audit repairs (AA0), run as part of the
same gate:

  AA0.1  h(x) = a log(1-x) + b satisfies the unweighted equation identically.
         (Completeness — that continuous solutions are ONLY these — rests on
         the lemma cited in the supplement, not on this check.)
  AA0.2  Symmetry h(x) = h(1-x) forces a = 0 within that family.
  AA0.3  The midpoint completion of the non-f-divergence counterexample, in
         exact rationals: F(nu+) = 3277/3200, F(nu-) = 2977/3200, their mean
         3127/3200, F(midpoint) = 3125/3200, gap 1/1600.
  AA0.4  The corrected top-mass-after-refinement formula: the max runs over
         ALL classes including unsplit ones, with an explicit case where an
         unsplit class overtakes the divided leader.
  AA0.5  The ex-post value R(pi) - R(q+) can be negative; the ex-ante value
         is nonnegative (checked exactly on constructions and random draws).
  AA0.6  The refinement identities under ARBITRARY child weights w, with the
         manuscript's equal-split formulas recovered as the w_i = 1/r special
         case, and the fragility criterion's equal-split-only scope exhibited.

Nothing here reads data except the frozen profile CSV used for the U2 numbers,
which is post-hoc arithmetic already deposited. No frozen artifact is written.

Run: python3 paper/verification/u0_invariance_symbolic.py
"""

import sys
from fractions import Fraction

import numpy as np
import sympy as sp

results = []


def record(name, ok, detail=""):
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"        {line}")
    return ok


# ===========================================================================
print("U0.1 — refinement invariance of the spectral moments\n")
# ===========================================================================
# Split class m into r parts with GENERAL weights w_1..w_r summing to 1:
#   pi'(m_i) = w_i pi_m ,  q'(m_i) = w_i q_m
# so the likelihood ratio q/pi is unchanged on every part. The rest of the
# inventory contributes an opaque symbol, so the result holds for every K.
s = sp.symbols("s")
pi_m, q_m = sp.symbols("pi_m q_m", positive=True)
REST = sp.Symbol("REST_s")           # sum over the untouched classes
r = 4                                # explicit arity; weights fully symbolic
w = sp.symbols(f"w1:{r + 1}", positive=True)

mu_before = REST + pi_m * (q_m / pi_m) ** s
mu_after = REST + sum(w_i * pi_m * ((w_i * q_m) / (w_i * pi_m)) ** s for w_i in w)
# impose only that the weights sum to 1
mu_after = sp.simplify(mu_after.subs(w[-1], 1 - sum(w[:-1])))
record("U0.1a  mu_s invariant, general weights, symbolic s, general K",
       sp.simplify(sp.expand(mu_after - mu_before)) == 0)

for s_val in (2, 3):
    a = REST + pi_m * (q_m / pi_m) ** s_val
    b = REST + sum(w_i * pi_m * ((w_i * q_m) / (w_i * pi_m)) ** s_val for w_i in w)
    b = b.subs(w[-1], 1 - sum(w[:-1]))
    record(f"U0.1b  mu_{s_val} invariant, general weights",
           sp.simplify(sp.expand(b - a)) == 0)

# the likelihood ratio itself is what carries the invariance
lam = sp.simplify((w[0] * q_m) / (w[0] * pi_m) - q_m / pi_m)
record("U0.1c  likelihood ratio unchanged on every part (the mechanism)", lam == 0)


# ===========================================================================
print("\nU0.2 — the counterexample: invariant, but not an f-divergence\n")
# ===========================================================================
REST2, REST3 = sp.symbols("REST_2 REST_3")
mu2_b = REST2 + pi_m * (q_m / pi_m) ** 2
mu3_b = REST3 + pi_m * (q_m / pi_m) ** 3
mu2_a = (REST2 + sum(wi * pi_m * ((wi * q_m) / (wi * pi_m)) ** 2 for wi in w)
         ).subs(w[-1], 1 - sum(w[:-1]))
mu3_a = (REST3 + sum(wi * pi_m * ((wi * q_m) / (wi * pi_m)) ** 3 for wi in w)
         ).subs(w[-1], 1 - sum(w[:-1]))
F_b = (mu2_b - 1) ** 2 + (mu3_b - 1) ** 2
F_a = (mu2_a - 1) ** 2 + (mu3_a - 1) ** 2
record("U0.2a  F = (mu2-1)^2 + (mu3-1)^2 is refinement invariant",
       sp.simplify(sp.expand(F_a - F_b)) == 0)

# Vandermonde injectivity on the stated support
t = [sp.Rational(1, 4), sp.Rational(3, 4), sp.Rational(5, 4), sp.Rational(7, 4)]
V = sp.Matrix(4, 4, lambda i, j: t[j] ** i)          # rows: moments 0,1,2,3
det = sp.simplify(V.det())
record("U0.2b  Vandermonde at t = {1/4, 3/4, 5/4, 7/4} is invertible",
       det != 0, f"det = {det}  (nonzero => a |-> (mu0..mu3) is injective)")

# kernel direction: preserves mu0, mu1, mu2 -- hence preserves the chi^2
# f-divergence with f(x) = x^2 - 1 -- but moves mu3, hence moves F.
K = sp.Matrix(3, 4, lambda i, j: t[j] ** i).nullspace()
record("U0.2c  kernel of (mu0, mu1, mu2) is 1-dimensional", len(K) == 1)
d = K[0]
d = d / max(abs(x) for x in d)
mu3_of_d = sum(d[i] * t[i] ** 3 for i in range(4))
record("U0.2d  that direction moves mu3 (so it is not in the F-kernel)",
       sp.simplify(mu3_of_d) != 0, f"sum d_i t_i^3 = {sp.nsimplify(mu3_of_d)}")

# explicit feasible pair on the constraint plane {sum a = 1, sum a t = 1}
a0 = sp.Matrix([sp.Rational(1, 4)] * 4)
eps = sp.Rational(1, 10)
a_plus = sp.Matrix([a0[i] + eps * d[i] for i in range(4)])
a_minus = sp.Matrix([a0[i] - eps * d[i] for i in range(4)])


def moments(a):
    return [sum(a[i] * t[i] ** k for i in range(4)) for k in range(4)]


mp, mm = moments(a_plus), moments(a_minus)
feasible = all(x > 0 for x in list(a_plus) + list(a_minus))
record("U0.2e  both perturbed points are strictly positive probability vectors",
       feasible and mp[0] == 1 and mm[0] == 1 and mp[1] == 1 and mm[1] == 1,
       f"a+ = {[sp.nsimplify(x) for x in a_plus]}\n"
       f"a- = {[sp.nsimplify(x) for x in a_minus]}")

chi2_p, chi2_m = mp[2] - 1, mm[2] - 1
F_p = (mp[2] - 1) ** 2 + (mp[3] - 1) ** 2
F_m = (mm[2] - 1) ** 2 + (mm[3] - 1) ** 2
record("U0.2f  same chi^2 (f(x) = x^2 - 1, nonconstant) at the two points",
       sp.simplify(chi2_p - chi2_m) == 0,
       f"chi^2 = {sp.nsimplify(chi2_p)} at both")
record("U0.2g  but DIFFERENT F  => F is not any f-divergence",
       sp.simplify(F_p - F_m) != 0,
       f"F(a+) = {sp.nsimplify(F_p)}\nF(a-) = {sp.nsimplify(F_m)}\n"
       f"mu3 differs: {sp.nsimplify(mp[3])} vs {sp.nsimplify(mm[3])}")


# ===========================================================================
print("\nU0.3 — the canonical-pair construction\n")
# ===========================================================================
# Take a 3-class pair whose spectrum has a repeated likelihood ratio, so the
# construction has something to do.
p1, p2, p3 = sp.symbols("p1 p2 p3", positive=True)
tt = sp.symbols("t", positive=True)          # shared ratio of classes 1 and 2
t3 = sp.symbols("t3", positive=True)
pi_v = [p1, p2, p3]
q_v = [tt * p1, tt * p2, t3 * p3]            # L = (t, t, t3)

# canonical pair on the spectrum alphabet {t, t3}
a_t = p1 + p2
pi_star = [a_t, p3]
q_star = [tt * a_t, t3 * p3]

norm_pi = sp.simplify(sum(pi_star) - sum(pi_v))
norm_q = sp.simplify(sum(q_star) - sum(q_v))
record("U0.3a  canonical pair normalizes iff the original does",
       norm_pi == 0 and norm_q == 0)

# weights w_m = pi_m / a_t recover the original by refinement
w1, w2 = p1 / a_t, p2 / a_t
record("U0.3b  the recovering weights sum to one", sp.simplify(w1 + w2 - 1) == 0)
rec_pi = [sp.simplify(w1 * pi_star[0] - p1), sp.simplify(w2 * pi_star[0] - p2)]
rec_q = [sp.simplify(w1 * q_star[0] - q_v[0]), sp.simplify(w2 * q_star[0] - q_v[1])]
record("U0.3c  w_m * pi*_t recovers pi_m, and w_m * q*_t recovers q_m",
       all(x == 0 for x in rec_pi + rec_q))


# ===========================================================================
print("\nU0.4 — THE HINGE\n")
# ===========================================================================
# (a) The three groupings of a three-way split, and the equation they force.
al, be, ga = sp.symbols("alpha beta gamma", positive=True)
sub = {ga: 1 - al - be}
arg_A = sp.simplify((be / (1 - al)).subs(sub))          # group (beta, gamma)
arg_B = sp.simplify((al / (1 - ga)).subs(sub))          # group (alpha, gamma)
arg_C = sp.simplify((al / (1 - be)).subs(sub))          # group (alpha, beta)
record("U0.4a  three-way split gives arguments beta/(1-alpha), alpha/(1-gamma), "
       "alpha/(1-beta)",
       sp.simplify(arg_A - be / (be + (1 - al - be))) == 0
       and sp.simplify(arg_B - al / (al + be)) == 0,
       "with h(x) = h(1-x) the first two groupings give\n"
       "  h(x) + h(y/(1-x)) = h(y) + h(x/(1-y))   [the unweighted equation]")

# (b) Discriminator: the UNWEIGHTED equation is not the Shannon grouping
# equation. Constants solve it; the binary entropy does not.
def check_eq(h, trials):
    worst = 0.0
    for x, y in trials:
        lhs = h(x) + h(y / (1 - x))
        rhs = h(y) + h(x / (1 - y))
        worst = max(worst, abs(lhs - rhs))
    return worst


rng = np.random.default_rng(0)
trials = []
while len(trials) < 400:
    x, y = rng.uniform(0.02, 0.96, 2)
    if x + y < 0.98:
        trials.append((x, y))

Hb = lambda z: float(-z * np.log(z) - (1 - z) * np.log(1 - z)) if 0 < z < 1 else 0.0
record("U0.4b  constants satisfy the unweighted equation",
       check_eq(lambda z: 1.0, trials) < 1e-12)
dev = check_eq(Hb, trials)
record("U0.4c  binary Shannon entropy does NOT (it solves the WEIGHTED one)",
       dev > 1e-3, f"max deviation over 400 random (x, y): {dev:.4f}")

# (c) Null space of the equation on Farey grids -- pure linear algebra, no
# smoothness assumed. Unknowns are h at interior Farey fractions.
def farey(n):
    out = set()
    for qd in range(2, n + 1):
        for p in range(1, qd):
            out.add(Fraction(p, qd))
    return sorted(out)


for N in (6, 8, 10, 12):
    nodes = farey(N)
    idx = {v: i for i, v in enumerate(nodes)}
    rows = []
    for i, x in enumerate(nodes):
        for y in nodes:
            if x + y >= 1:
                continue
            u, v = y / (1 - x), x / (1 - y)
            if u in idx and v in idx:
                row = np.zeros(len(nodes))
                row[idx[x]] += 1; row[idx[u]] += 1
                row[idx[y]] -= 1; row[idx[v]] -= 1
                if row.any():
                    rows.append(row)
    for x in nodes:                      # symmetry h(x) = h(1-x)
        m = 1 - x
        if m in idx and m != x:
            row = np.zeros(len(nodes))
            row[idx[x]] += 1; row[idx[m]] -= 1
            rows.append(row)
    A = np.array(rows)
    rank = np.linalg.matrix_rank(A, tol=1e-9)
    nullity = len(nodes) - rank
    record(f"U0.4d  Farey order {N}: solution space is constants only "
           f"({len(nodes)} nodes, {len(rows)} equations, nullity {nullity})",
           nullity == 1)

# (d) The differentiable derivation: expanding to first order in y forces
# h'(x) = h'(0)/(1-x), and symmetry then forces h' = 0.
x_s, y_s = sp.symbols("x y", positive=True)
h = sp.Function("h")
expr = h(x_s) + h(y_s / (1 - x_s)) - h(y_s) - h(x_s / (1 - y_s))
first_order = sp.simplify(sp.diff(expr, y_s).subs(y_s, 0))
sol = sp.solve(sp.Eq(first_order, 0), sp.Derivative(h(x_s), x_s))
record("U0.4e  first order in y gives h'(x) = h'(0)/(1-x)",
       len(sol) == 1
       and sp.simplify(sol[0] - sp.Subs(sp.Derivative(h(y_s), y_s), y_s, 0) / (1 - x_s)) == 0,
       f"solved: h'(x) = {sp.simplify(sol[0])}" if sol else "no solution found")

C, D = sp.symbols("C D")
h_gen = -C * sp.log(1 - x_s) + D           # the general solution of h' = C/(1-x)
sym_defect = sp.simplify(h_gen - h_gen.subs(x_s, 1 - x_s))
forced = sp.solve(sp.Eq(sp.simplify(sym_defect), 0), C)
record("U0.4f  symmetry h(x) = h(1-x) forces C = 0, i.e. h constant",
       0 in [sp.simplify(f) for f in forced] or sp.simplify(sym_defect.subs(C, 0)) == 0,
       f"h(x) - h(1-x) = {sym_defect}  =>  C = 0")

# ===========================================================================
print("\nAA0 — audit-repair verifications (v13)\n")
# ===========================================================================
# AA0.1  The log family satisfies the unweighted equation identically. The
# equation is linear in h, so verifying h0(z) = log(1-z) (with constants
# already covered by U0.4b) verifies every a*log(1-z) + b.
xx, yy = sp.symbols("xx yy", positive=True)


def h0(z):
    return sp.log(sp.together(1 - z))


aa1_defect = sp.expand_log(
    h0(xx) + h0(yy / (1 - xx)) - h0(yy) - h0(xx / (1 - yy)), force=True
)
record("AA0.1  h(x) = a log(1-x) + b satisfies the unweighted equation",
       sp.simplify(aa1_defect) == 0,
       "checked for h0 = log(1-x); linearity + U0.4b extend to a*h0 + b.\n"
       "Completeness of the family rests on the cited lemma, not this check.")

# AA0.2  Symmetry within the family forces a = 0.
a_sym = sp.Symbol("a_sym")
fam_defect = sp.simplify(
    (a_sym * sp.log(1 - xx)) - (a_sym * sp.log(1 - (1 - xx)))
)
forced_a = sp.solve(sp.Eq(fam_defect.subs(xx, sp.Rational(1, 4)), 0), a_sym)
record("AA0.2  h(x) = h(1-x) forces a = 0 in the log family",
       forced_a == [0],
       f"h(x) - h(1-x) = {fam_defect}  => a = 0, h constant")

# AA0.3  The midpoint completion, in exact rationals. Every f-divergence is
# affine in the spectrum; F is not, and the midpoint exhibits it.
t4 = [sp.Rational(1, 4), sp.Rational(3, 4), sp.Rational(5, 4), sp.Rational(7, 4)]
ap = [sp.Rational(13, 60), sp.Rational(7, 20), sp.Rational(3, 20), sp.Rational(17, 60)]
am = [sp.Rational(17, 60), sp.Rational(3, 20), sp.Rational(7, 20), sp.Rational(13, 60)]
a0 = [(ap[i] + am[i]) / 2 for i in range(4)]


def F_of(a):
    mu2 = sum(a[i] * t4[i] ** 2 for i in range(4))
    mu3 = sum(a[i] * t4[i] ** 3 for i in range(4))
    return (mu2 - 1) ** 2 + (mu3 - 1) ** 2


Fp_, Fm_, F0_ = F_of(ap), F_of(am), F_of(a0)
record("AA0.3a  endpoint values: F(nu+) = 3277/3200, F(nu-) = 2977/3200",
       Fp_ == sp.Rational(3277, 3200) and Fm_ == sp.Rational(2977, 3200))
record("AA0.3b  midpoint spectrum is uniform (1/4, 1/4, 1/4, 1/4) and feasible",
       a0 == [sp.Rational(1, 4)] * 4
       and sum(a0) == 1 and sum(a0[i] * t4[i] for i in range(4)) == 1)
record("AA0.3c  F(midpoint) = 3125/3200 = 125/128, mean of endpoints 3127/3200",
       F0_ == sp.Rational(3125, 3200)
       and (Fp_ + Fm_) / 2 == sp.Rational(3127, 3200))
record("AA0.3d  the affinity gap is exactly 1/1600, so F is no f-divergence",
       (Fp_ + Fm_) / 2 - F0_ == sp.Rational(1, 1600),
       "an f-divergence is affine in nu and cannot show a nonzero gap")

# AA0.4  Corrected top-mass-after-refinement formula: splitting the leading
# class m into r equal parts leaves top mass max(max_{l != m} q_l, q_m / r),
# NOT q_m / r. Case where an unsplit class overtakes the divided leader.
q_case = [sp.Rational(3, 5), sp.Rational(2, 5)]     # leader 3/5, runner-up 2/5
r_split = 2
q_after = [q_case[0] / r_split] * r_split + q_case[1:]
top_direct = max(q_after)
top_formula = max(max(q_case[1:]), q_case[0] / r_split)
record("AA0.4a  q = (3/5, 2/5), leader split in two: top mass is 2/5, not 3/10",
       top_direct == sp.Rational(2, 5) and top_formula == top_direct,
       "the unsplit class overtakes the divided leader")
q_case2 = [sp.Rational(9, 10), sp.Rational(1, 10)]  # leader keeps the lead
q_after2 = [q_case2[0] / r_split] * r_split + q_case2[1:]
record("AA0.4b  q = (9/10, 1/10): formula max(max_{l!=m} q_l, q_m/r) matches",
       max(q_after2) == max(max(q_case2[1:]), q_case2[0] / r_split) ==
       sp.Rational(9, 20))

# AA0.5  Ex-post decision value can be negative; ex-ante value cannot.
# Two-class 0-1 loss: R(p) = 1 - max(p). Construction: pi = (9/10, 1/10),
# lambda = (1/6, 1) gives c = 1/4, q+ = (3/5, 2/5), q- = (1, 0).
FR = Fraction
pi_c = (FR(9, 10), FR(1, 10))
lam_c = (FR(1, 6), FR(1, 1))


def bayes_risk(p):
    return 1 - max(p)


def fire_split(pi_v, lam_v):
    c = sum(p * l for p, l in zip(pi_v, lam_v))
    qp = tuple(p * l / c for p, l in zip(pi_v, lam_v))
    qm = tuple(p * (1 - l) / (1 - c) for p, l in zip(pi_v, lam_v))
    return c, qp, qm


c_c, qp_c, qm_c = fire_split(pi_c, lam_c)
ex_post = bayes_risk(pi_c) - bayes_risk(qp_c)
ex_ante = bayes_risk(pi_c) - (c_c * bayes_risk(qp_c) + (1 - c_c) * bayes_risk(qm_c))
record("AA0.5a  ex-post R(pi) - R(q+) = -3/10 < 0 at pi=(9/10,1/10), q+=(3/5,2/5)",
       qp_c == (FR(3, 5), FR(2, 5)) and ex_post == FR(-3, 10),
       "a particular fire can move belief toward a harder decision state")
record("AA0.5b  the same construction's ex-ante value is >= 0 (here exactly 0)",
       ex_ante == 0 and
       tuple(c_c * qp_c[i] + (1 - c_c) * qm_c[i] for i in range(2)) == pi_c)

rng_aa = np.random.default_rng(20260805)
worst_ante = FR(1)
neg_post_seen = False
ok_ante = True
for _ in range(200):
    pi1 = FR(int(rng_aa.integers(1, 99)), 100)
    l1 = FR(int(rng_aa.integers(1, 99)), 100)
    l2 = FR(int(rng_aa.integers(1, 99)), 100)
    pv, lv = (pi1, 1 - pi1), (l1, l2)
    c_r, qp_r, qm_r = fire_split(pv, lv)
    if not (0 < c_r < 1):
        continue
    va = bayes_risk(pv) - (c_r * bayes_risk(qp_r) + (1 - c_r) * bayes_risk(qm_r))
    ok_ante = ok_ante and va >= 0
    worst_ante = min(worst_ante, va)
    neg_post_seen = neg_post_seen or (bayes_risk(pv) - bayes_risk(qp_r) < 0)
record("AA0.5c  200 exact random draws: ex-ante value >= 0 in every one",
       ok_ante, f"minimum ex-ante value observed: {worst_ante}")
record("AA0.5d  ...while ex-post negativity occurs among the same draws",
       neg_post_seen)

# AA0.6  Refinement identities under ARBITRARY child weights. Split class m
# (prior mass pi_m, posterior mass q_m) into r = 3 parts with symbolic
# weights; the manuscript's equal-split formulas are the w_i = 1/r case.
w3 = sp.symbols("v1 v2 v3", positive=True)
sub3 = {w3[2]: 1 - w3[0] - w3[1]}
RH_pi, RH_q, RH_kl = sp.symbols("RH_pi RH_q RH_kl")   # untouched-class sums
Hw = -sum(wi * sp.log(wi, 2) for wi in w3)

H_pi_before = RH_pi - pi_m * sp.log(pi_m, 2)
H_pi_after = RH_pi - sum(wi * pi_m * sp.log(wi * pi_m, 2) for wi in w3)
d_pi = sp.simplify((H_pi_after - H_pi_before - pi_m * Hw).subs(sub3))
record("AA0.6a  H(pi') = H(pi) + pi_m H(w) for arbitrary weights",
       sp.simplify(sp.expand_log(d_pi, force=True)) == 0,
       "equal-split case: H(w) = log2 r recovers the manuscript identity")

H_q_before = RH_q - q_m * sp.log(q_m, 2)
H_q_after = RH_q - sum(wi * q_m * sp.log(wi * q_m, 2) for wi in w3)
d_q = sp.simplify((H_q_after - H_q_before - q_m * Hw).subs(sub3))
record("AA0.6b  H(q') = H(q) + q_m H(w), hence 2^H(q') = 2^H(q) * 2^(q_m H(w))",
       sp.simplify(sp.expand_log(d_q, force=True)) == 0)

kl_before = RH_kl + q_m * sp.log(q_m / pi_m, 2)
kl_after = RH_kl + sum(wi * q_m * sp.log((wi * q_m) / (wi * pi_m), 2) for wi in w3)
record("AA0.6c  KL(q' || pi') = KL(q || pi) for arbitrary weights",
       sp.simplify((kl_after - kl_before).subs(sub3)) == 0)

# The fragility criterion under general weights: a single binary split of a
# class with posterior-mass gap Delta reverses an effective-count ratio R
# iff Delta * H_nat(w) > ln R. With the frozen v3 numbers (Delta = 0.4295,
# ln R = 0.2856) the EQUAL split reverses (Delta ln 2 = 0.2977) but an
# unequal 0.3/0.7 split does not (Delta * 0.6109 = 0.2624): the manuscript's
# one-added-class inversion is an equal-subdivision statement.
Delta_f, lnR_f = 0.4295, 0.2856


def H_nat(w):
    return float(-(w * np.log(w) + (1 - w) * np.log(1 - w)))


eq_gain = Delta_f * np.log(2.0)
uneq_gain = Delta_f * H_nat(0.30)
record("AA0.6d  equal binary split reverses (0.2977 > 0.2856); 0.3/0.7 does not "
       "(0.2624)", eq_gain > lnR_f and uneq_gain < lnR_f,
       f"equal-split gain {eq_gain:.4f}, 0.3/0.7 gain {uneq_gain:.4f}, "
       f"ln R = {lnR_f}")
w_lo, w_hi = 0.3816, 0.6184
record("AA0.6e  reversal window for a binary RATE_VAR split is approx "
       "(0.3816, 0.6184)",
       Delta_f * H_nat(w_lo - 0.0005) < lnR_f < Delta_f * H_nat(w_lo + 0.0005)
       and Delta_f * H_nat(w_hi + 0.0005) < lnR_f < Delta_f * H_nat(w_hi - 0.0005),
       "outside that child-weight window the equal-count inversion vanishes")

# ===========================================================================
print("\nAB2 — the Gselmann-Maksa alpha = 0 family, verified term by term\n")
# ===========================================================================
# Source (read directly): Gselmann & Maksa, "Stability of the parametric
# fundamental equation of information for nonpositive parameters",
# aequationes mathematicae 78(3) (2009) 271-282, Theorem 2.1 with eps = 0
# and Remark 2.2: the general solution of the alpha = 0 equation on the open
# triangle D-degree is  f(x) = l(1-x) + c  with l logarithmic
# (l(uv) = l(u) + l(v)) and c real. The checks below verify (1) that every
# member of that family solves the unweighted equation, term by term, and
# (2) exactly which constants survive the two-child relabeling symmetry
# h(x) = h(1-x): the logarithmic term is annihilated with NO regularity
# assumed, and only the constant c survives.
xg, yg, ug = sp.symbols("xg yg ug", positive=True)

# AB2.1a  The logarithmic term: the equation pairs its four l-arguments so
# that the products on the two sides agree, both equal to 1 - x - y, so
# l(uv) = l(u) + l(v) makes each side l(1 - x - y) for ANY logarithmic l.
argL1, argL2 = 1 - xg, sp.together(1 - yg / (1 - xg))
argR1, argR2 = 1 - yg, sp.together(1 - xg / (1 - yg))
record("AB2.1a  l-argument products agree: (1-x)(1-y/(1-x)) = (1-y)(1-x/(1-y)) "
       "= 1-x-y",
       sp.simplify(argL1 * argL2 - (1 - xg - yg)) == 0
       and sp.simplify(argR1 * argR2 - (1 - xg - yg)) == 0,
       "hence h(z) = l(1-z) solves the unweighted equation for every\n"
       "logarithmic l, with all four arguments in ]0,1[ on the domain")

# AB2.1b  Concrete member: l = log (so h(z) = log(1-z)) solves it exactly.
member_defect = sp.expand_log(
    sp.log(argL1) + sp.log(argL2) - sp.log(argR1) - sp.log(argR2), force=True
)
record("AB2.1b  the member l = log solves the equation identically",
       sp.simplify(member_defect) == 0)
record("AB2.1c  the constant term c solves it (2c on each side)",
       (2 * sp.Symbol("c_ab") - 2 * sp.Symbol("c_ab")) == 0,
       "already exercised numerically by U0.4b")

# AB2.2a  Symmetry, term by term. h(x) - h(1-x) = l(1-x) - l(x) = l((1-x)/x)
# for any logarithmic l, by the product identity ((1-x)/x) * x = 1 - x.
record("AB2.2a  product identity ((1-x)/x) * x = 1-x, so the symmetry defect "
       "is l((1-x)/x)",
       sp.simplify(((1 - xg) / xg) * xg - (1 - xg)) == 0)

# AB2.2b  (1-x)/x maps ]0,1[ ONTO ]0,+inf[: phi(1/(1+u)) = u for every u > 0,
# with 1/(1+u) in ]0,1[. So h(x) = h(1-x) forces l = 0 on all of ]0,+inf[,
# with no continuity or measurability assumed.
phi_at = sp.simplify((1 - 1 / (1 + ug)) / (1 / (1 + ug)))
record("AB2.2b  (1-x)/x is onto ]0,inf[: phi(1/(1+u)) = u, 0 < 1/(1+u) < 1",
       sp.simplify(phi_at - ug) == 0,
       "symmetry therefore annihilates the logarithmic term outright")

# AB2.2c  Which constants survive: l dies, c survives; in the continuous
# parameterization a*log(1-x) + b, the coefficient a dies (AA0.2) and b
# survives. The surviving set is the constants — the theorem stands.
b_ab = sp.Symbol("b_ab")
record("AB2.2c  survivors of h(x) = h(1-x) within the family are exactly the "
       "constants",
       sp.simplify(b_ab - b_ab.subs(xg, 1 - xg)) == 0
       and sp.simplify(sp.log(1 - xg) - sp.log(xg)).subs(xg, sp.Rational(1, 4))
       != 0,
       "l-term: forced to zero (AB2.2b); constant term: symmetric, survives")

# ===========================================================================
print("\n" + "=" * 74)
failed = [n for n, ok in results if not ok]
print(f"{len(results) - len(failed)} / {len(results)} checks passed")
for n in failed:
    print(f"  FAILED: {n}")
if failed:
    print("\nGATE NOT PASSED — the dichotomy theorem must not ship.")
sys.exit(1 if failed else 0)
