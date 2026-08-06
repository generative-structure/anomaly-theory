"""Symbolic verification of the two R-phase propositions, before any prose is
written against them (directive R7).

R1 — inventory-refinement invariance. Split mechanism m of a K-class inventory
into r observationally identical subclasses (same response rate lambda_j(m)),
with the prior mass of m divided equally among them. Claims:

    H(pi')            = H(pi) + pi_m  * log2(r)
    H(q')             = H(q)  + q_m   * log2(r)
    MWF' - MWF        = (pi_m - q_m) * log2(r)          [MWF = H(pi) - H(q)]
    2^H(q')           = 2^H(q) * r^(q_m)
    KL(q' || pi')     = KL(q || pi)                      [invariant]
    c_j'              = c_j                              [invariant]

R2 — binary-fire information decomposition. With
    q+(m) = pi(m) lambda_j(m) / c_j
    q-(m) = pi(m) {1 - lambda_j(m)} / (1 - c_j)
    c_j   = sum_m pi(m) lambda_j(m)
the claim is the exact identity

    I(M; F_j) = c_j KL(q+ || pi) + (1 - c_j) KL(q- || pi)

with I(M; F_j) = H(M) - H(M | F_j) computed directly, i.e.
H(M | F_j) = c_j H(q+) + (1 - c_j) H(q-).

R2b — the two propositions meet: I(M; F_j) is refinement-invariant, because it
is a c-weighted mixture of two invariant divergences and c is invariant. The
per-fire concentration H(pi) - H(q+) is NOT, by R1.

Nothing here reads data. Run: python3 paper/verification/r1_r2_symbolic.py
"""

import sys

import sympy as sp

log2 = lambda x: sp.log(x, 2)  # noqa: E731
ok = []


def check(name, expr_zero, assumptions=None):
    """Assert an expression simplifies to exactly zero; record the outcome."""
    simplified = sp.simplify(sp.expand_log(sp.simplify(expr_zero), force=True))
    passed = simplified == 0
    ok.append((name, passed, simplified))
    print(f"{'PASS' if passed else 'FAIL'}  {name}")
    if not passed:
        print(f"      residual: {simplified}")
    return passed


# ---------------------------------------------------------------------------
# R1, general r: the "rest of the inventory" contributions are opaque symbols,
# so the identities below hold for every K and every r > 0, not for a sampled few.
# ---------------------------------------------------------------------------
print("R1 — inventory refinement, general r (rest-of-inventory terms opaque)\n")

r = sp.symbols("r", positive=True)
pi_m, q_m = sp.symbols("pi_m q_m", positive=True)
H_rest_pi, H_rest_q, KL_rest = sp.symbols("H_rest_pi H_rest_q KL_rest", real=True)

# Original: class m contributes -pi_m log2 pi_m to H(pi), -q_m log2 q_m to H(q),
# and q_m log2(q_m/pi_m) to KL(q||pi).
H_pi = H_rest_pi - pi_m * log2(pi_m)
H_q = H_rest_q - q_m * log2(q_m)
KL_qp = KL_rest + q_m * log2(q_m / pi_m)

# Refined: r subclasses, each with prior pi_m/r and posterior q_m/r (established
# explicitly in the concrete block below).
H_pi_ref = H_rest_pi - r * (pi_m / r) * log2(pi_m / r)
H_q_ref = H_rest_q - r * (q_m / r) * log2(q_m / r)
KL_qp_ref = KL_rest + r * (q_m / r) * log2((q_m / r) / (pi_m / r))

check("R1.1  H(pi') - H(pi) = pi_m log2 r", (H_pi_ref - H_pi) - pi_m * log2(r))
check("R1.2  H(q')  - H(q)  = q_m  log2 r", (H_q_ref - H_q) - q_m * log2(r))
check(
    "R1.3  MWF' - MWF = (pi_m - q_m) log2 r",
    ((H_pi_ref - H_q_ref) - (H_pi - H_q)) - (pi_m - q_m) * log2(r),
)
check(
    "R1.4  2^H(q') = 2^H(q) * r^(q_m)",
    sp.simplify(sp.powsimp(2 ** H_q_ref / (2 ** H_q * r ** q_m), force=True) - 1),
)
check("R1.5  KL(q'||pi') - KL(q||pi) = 0", KL_qp_ref - KL_qp)

# ---------------------------------------------------------------------------
# R1, concrete: K = 3 with every prior and response symbolic, class 3 split into
# r = 2, 3, 4 subclasses. This is what establishes q'(m_i) = q_m / r and c' = c
# from the definitions rather than assuming them.
# ---------------------------------------------------------------------------
print("\nR1 — inventory refinement, explicit construction (K = 3, r in {2,3,4})\n")

p1, p2, p3 = sp.symbols("p1 p2 p3", positive=True)
l1, l2, l3 = sp.symbols("lam1 lam2 lam3", positive=True)


def profile(prior, lam):
    """(fire rate c, fired posterior q) from a prior and a response row."""
    c = sum(p * l for p, l in zip(prior, lam))
    q = [p * l / c for p, l in zip(prior, lam)]
    return c, q


def entropy(v):
    return -sum(x * log2(x) for x in v)


def kl(a, b):
    return sum(x * log2(x / y) for x, y in zip(a, b))


c0, q0 = profile([p1, p2, p3], [l1, l2, l3])
for r_val in (2, 3, 4):
    # split class 3 into r_val observationally identical subclasses
    prior_ref = [p1, p2] + [p3 / r_val] * r_val
    lam_ref = [l1, l2] + [l3] * r_val
    c1, q1 = profile(prior_ref, lam_ref)

    check(f"R1.6  r={r_val}: c' = c (fire rate invariant)", sp.simplify(c1 - c0))
    check(
        f"R1.7  r={r_val}: q'(m_i) = q(m)/r for each subclass",
        sum(sp.simplify(q1[2 + i] - q0[2] / r_val) for i in range(r_val)),
    )
    check(
        f"R1.8  r={r_val}: H(pi') - H(pi) = pi_3 log2 r",
        sp.simplify(entropy(prior_ref) - entropy([p1, p2, p3]) - p3 * log2(r_val)),
    )
    check(
        f"R1.9  r={r_val}: H(q') - H(q) = q_3 log2 r",
        sp.simplify(entropy(q1) - entropy(q0) - q0[2] * log2(r_val)),
    )
    check(
        f"R1.10 r={r_val}: KL(q'||pi') = KL(q||pi)",
        sp.simplify(kl(q1, prior_ref) - kl(q0, [p1, p2, p3])),
    )

# ---------------------------------------------------------------------------
# R2: the binary-fire decomposition, fully symbolic in K = 3 and K = 4.
# lambda in (0, 1) so that both q+ and q- exist.
# ---------------------------------------------------------------------------
print("\nR2 — binary-fire information decomposition (K = 3 and K = 4)\n")

for K in (3, 4):
    prior = sp.symbols(f"P1:{K + 1}", positive=True)
    lam = sp.symbols(f"L1:{K + 1}", positive=True)

    c = sum(p * l for p, l in zip(prior, lam))
    q_plus = [p * l / c for p, l in zip(prior, lam)]
    q_minus = [p * (1 - l) / (1 - c) for p, l in zip(prior, lam)]

    # I(M; F) computed directly as H(M) - H(M | F)
    H_M = entropy(prior)
    H_M_given_F = c * entropy(q_plus) + (1 - c) * entropy(q_minus)
    I_direct = H_M - H_M_given_F

    # I(M; F) as the claimed two-term divergence decomposition
    I_decomp = c * kl(q_plus, prior) + (1 - c) * kl(q_minus, prior)

    check(f"R2.1  K={K}: I(M;F) = c KL(q+||pi) + (1-c) KL(q-||pi)",
          sp.simplify(sp.expand(sp.expand_log(I_direct - I_decomp, force=True))))

    # R4 leans on this: the two fire-conditional posteriors mix back to the
    # prior, which with concavity of the Bayes risk R gives V_j >= 0.
    check(f"R4.1  K={K}: c q+ + (1-c) q- = pi termwise",
          sum(sp.simplify(c * qp + (1 - c) * qm - p)
              for qp, qm, p in zip(q_plus, q_minus, prior)))

    # the fire term alone is NOT the mutual information
    residual = sp.simplify(I_direct - c * kl(q_plus, prior))
    print(f"      (K={K}) I - c*KL(q+||pi) is the silence term, not zero: "
          f"{'confirmed nonzero' if residual != 0 else 'UNEXPECTEDLY ZERO'}")

# ---------------------------------------------------------------------------
# R2b: I(M; F_j) is refinement-invariant; the per-fire concentration is not.
# ---------------------------------------------------------------------------
print("\nR2b — refinement behaviour of the two scalars (K = 3, r = 2)\n")

prior0 = [p1, p2, p3]
lam0 = [l1, l2, l3]
r_val = 2
prior1 = [p1, p2] + [p3 / r_val] * r_val
lam1 = [l1, l2] + [l3] * r_val


def mutual_information(prior, lam):
    c = sum(p * l for p, l in zip(prior, lam))
    qp = [p * l / c for p, l in zip(prior, lam)]
    qm = [p * (1 - l) / (1 - c) for p, l in zip(prior, lam)]
    return entropy(prior) - (c * entropy(qp) + (1 - c) * entropy(qm))


def concentration(prior, lam):
    c = sum(p * l for p, l in zip(prior, lam))
    qp = [p * l / c for p, l in zip(prior, lam)]
    return entropy(prior) - entropy(qp)


check("R2b.1 I(M;F) is refinement-invariant",
      sp.simplify(sp.expand_log(mutual_information(prior1, lam1)
                                - mutual_information(prior0, lam0), force=True)))

conc_shift = sp.simplify(sp.expand_log(
    concentration(prior1, lam1) - concentration(prior0, lam0), force=True))
c_sym = sum(p * l for p, l in zip(prior0, lam0))
predicted = sp.simplify((p3 - p3 * l3 / c_sym) * log2(r_val))
matches = sp.simplify(conc_shift - predicted) == 0
ok.append(("R2b.2 concentration shifts by (pi_m - q_m) log2 r", matches, conc_shift))
print(f"{'PASS' if matches else 'FAIL'}  R2b.2 concentration shifts by "
      f"(pi_m - q_m) log2 r  [not invariant]")

# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
failed = [n for n, passed, _ in ok if not passed]
print(f"{len(ok) - len(failed)} / {len(ok)} symbolic checks passed")
if failed:
    for n in failed:
        print(f"  FAILED: {n}")
sys.exit(1 if failed else 0)
