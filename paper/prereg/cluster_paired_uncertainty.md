# Preregistration — cluster-aware paired uncertainty for §5 (revision 4)

**Status: FROZEN PENDING AUTHOR APPROVAL. Nothing has been run.** Revision 4
applies the six blocking corrections and is the first revision in which the
composition system in §5 matches what this memo says it is — revision 3 claimed
three of them and shipped none, because the edit script aborted before writing.
Revision 3 nominally applied: controlling clause precedence, an
exhaustive C3 hierarchy with OPPOSITE overriding, the narrowed subsumption
sentence, reciprocal point estimates in assertion 9, and two rerun safeguards.
Revision 2 applied `Response_to_cluster_paired_uncertainty.md` in full. Revision 1's four
rulings survive untouched; what changed is claim–statistic correspondence,
which was the review's central finding: *the discipline was stronger than the
inferential logic.*

---

## 1. Rulings (settled, unchanged from revision 1)

**Unit.** `card1` primary. Sensitivities, both preregistered and both reported
whatever they show: `card1`+`addr1` (corrected derivation) and the five-field
composite `card1`+`card2`+`card3`+`card5`+`addr1`.

> **Rule.** Where candidate dependence units nest and nothing empirical
> discriminates among them, the primary is the coarsest defensible unit,
> because underestimating dependence is the error that manufactures false
> precision.

*Substantive justification, added per review item 7.* `card1` is a payment-card
identifier. Records sharing it are transactions on one instrument, so they
share cardholder behavior, merchant mix, credit limit, and — decisively for an
outcome model — a common compromise event: when a card is compromised, its
transactions become outcome-positive together. That is a mechanism for
within-cluster outcome dependence, not merely a coarser partition. The
correction to revision 1's wording: **not** "nothing empirical discriminates,"
but *the prespecified between-cluster outcome-variance diagnostic differed
little across the three nested candidates (0.0203, 0.0220, 0.0228) and did not
provide a compelling basis for choosing among them.* The phrase "most
dependence absorbed" is withdrawn; no intracluster-correlation or design-effect
analysis supports it.

**B-1 bypass.** The scorer does not read
`decomposition-price/outputs/clustering_units.json`. That frozen artifact
records 37,532 clusters and a largest cluster of 65,706 for `card1`+`addr1`,
values round-3 finding B-1 declared false: a string-concatenated composite key
propagated a pandas NA and discarded a present `card1` wherever `addr1` was
missing. The corrected re-derivation is **39,974 clusters, largest 9,928**.
Assignments are re-derived at run time from frozen raw identifiers using
per-column fills, never a concatenated key. The frozen artifact stays
byte-identical as the record of what was once believed. **Per review item 13, a
new corrected clustering summary is written to `paper/posthoc/cluster_paired/`,
hash-manifested with its own manifest row**, so the correction has a canonical
record and runtime re-derivation is not its only home.

**Blindness declaration.** The unit was chosen with the interval consequences
already documented — [2.741, 6.391] under `card1` against [3.357, 5.764] and
[3.410, 5.762] under the alternatives. Blindness was lost historically, in the
A27 re-derivation, not in this act. The compensating fact: **the choice rule
selects against self-interest.** `card1` yields the widest of the three known
intervals, so the primary unit is the one least favorable to tight claims, and
a narrower sensitivity strengthens rather than embarrasses the result.

**Method.** Paired cluster-level bootstrap for all three comparisons. Chosen
over grouped repeated CV because the estimand is uncertainty in a *difference
between two statistics computed on the same frozen out-of-fold predictions*;
resampling clusters and recomputing both statistics inside each resample
preserves pairing exactly, where repeated CV would re-introduce fold-assignment
noise into a comparison that is not about folds. **This rationale is valid only
because the fold construction was already group-disjoint — see §2.**

---

## 2. Estimand (review items 5 and 6)

Verbatim, and reproduced in the manuscript wherever these intervals appear:

> The intervals quantify cluster-resampling uncertainty conditional on the
> frozen out-of-fold predictions, fitted specifications, hyperparameters, fold
> assignments, and algorithm seeds. They do not estimate total uncertainty from
> retraining the procedure on another sample.

**Group-leakage status, verified from the archive, case 1.** The frozen
predictions come from `score_structure_outcome.py`, which uses `GroupKFold` on
`card1` and documents in its own header that *no cluster spans folds*. Fold
assignment is therefore group-disjoint under the primary unit, and the scorer
asserts this before resampling.

**But the pipeline is not wholly out-of-fold**, per reviewer B's recorded
non-finding on the source program: density scores and digit-bin frequencies are
computed once on all records before folds are formed. Both constructions are
unsupervised, so no outcome information crosses; the construction is
transductive. Consequently these are **row-level out-of-fold predictions with
cluster-resampled evaluation, not cluster-level out-of-sample performance**, and
no clause below claims generalization to unseen clusters.

Comparative language throughout is written as *produced higher out-of-fold
AUPRC under the frozen fitted specifications*, never *predicts the outcome
better*.

---

## 3. Frozen parameters — zero free parameters at run time

| Parameter | Value |
|---|---|
| Resamples | **B = 20,000** (review item 10: at B = 2,000 the Monte Carlo SE of a tail probability is ≈0.0035, material when a verdict turns on an endpoint crossing zero) |
| Seed | 20260806 |
| Scheme | Clusters drawn with replacement to the original cluster count; all rows of a drawn cluster enter together; a cluster drawn *m* times contributes its rows *m* times |
| CI type / level | **Percentile**, pointwise, 2.5th and 97.5th, **linear interpolation** (`numpy.percentile` default, `method="linear"`) |
| Interval family | **Pointwise 95%**. **Eight** intervals per clustering unit (1 C1 + 4 C2 + 3 C3) × three units. No simultaneous or joint coverage is claimed (review item 15) |
| AUPRC | **Average precision**: `sum over ranked positives of precision-at-that-rank / n_positives`. Not trapezoidal PR area |
| Ranking / ties | Descending score; boundary ties broken by **ascending original row index**. Bootstrap duplicates of one row carry the same original index and are ordered by their draw position, deterministically |
| Lift at *k* | `(outcome rate in top-k) / (outcome rate in the resample)`. Reference prevalence is **resample-wide**, not the original population's |
| Budgets | **Fixed absolute** *k* = 200 and *k* = 5,905 in every resample (review item 11). The bootstrap targets uncertainty at fixed operational capacities — an auditor inspects 200 cases regardless of population realization — not at fixed review percentages. A resample with fewer than *k* rows yields an undefined statistic and is counted |
| Within-stratum allocation | Size-proportional; slots by `floor(k · n_stratum / n_total)`; the remainder distributed by **largest fractional part, ties by ascending stratum index**; a stratum receiving zero slots contributes nothing |
| Positive class | Outcome label `== 1` |
| Missing data | Rows with missing prediction, outcome, stratum, or all cluster identifiers are excluded before resampling; the count is asserted equal to the frozen original |
| Degeneracy | A statistic is undefined in a resample with zero positives (AUPRC, lift). Undefined resamples are counted, not silently dropped |
| **Degeneracy threshold** | **If fewer than 99% of resamples yield a defined statistic, no interval and no verdict is issued for it; the result is classified unreliable** (review item 9) |

---

## 4. The comparisons

All statistics are paired: both quantities are recomputed inside each resample
and their difference is the reported quantity.

**C1 — ordering, not equivalence.** `AUPRC(stratum-only) − AUPRC(density-score)`.
Point difference +0.00089. **No equivalence margin is declared**, therefore no
equivalence claim is licensed under any outcome (review item 2).

**C2 — incremental value, four intervals.** For each score family
*f* ∈ {density, digit-law}, **both** directions:

- `add_f` = `AUPRC(score_f + stratum) − AUPRC(stratum-only)` — does the score add beyond the stratum?
- `strat_f` = `AUPRC(score_f + stratum) − AUPRC(score_f only)` — does the stratum add beyond the score?

The reciprocal contrast is new in revision 2. "Neither subsumes the other" is
licensed **for a family only when both of that family's intervals exclude zero
positive** — two intervals, not one (review item 1).

**C3 — two distinct claims.** Δ₂₀₀ and Δ₅₉₀₅ = `lift(within-stratum) −
lift(pooled)` at each budget, and the interaction `I = Δ₂₀₀ − Δ₅₉₀₅`.

- **Budget dependence** is carried by **I**.
- **Full directional reversal** is carried by **both marginals** excluding zero with signs Δ₂₀₀ > 0 and Δ₅₉₀₅ < 0.

These are not synonyms and are never reported as one (review item 3).

---

## 5. Licensed clauses and the composition rule

The 3 × 3 grid of revision 1 is withdrawn: it did not cover mixed outcomes
(review item 4). Verdicts are **assembled from per-interval clauses by a fixed
rule, leaving zero post-run discretion.**

### Per-interval clause set

**Classification precedence.** Statuses overlap: an interval entirely above
zero is POS, and is *also* OPPOSITE when its point estimate is negative;
likewise below zero. Precedence is therefore controlling and is stated here:

> **UNRELIABLE first, then OPPOSITE, then POS or NEG, then NULL. Once a
> higher-precedence status applies, no lower-precedence status fires.**

Without this sentence "exactly one clause fires" is not guaranteed. For any
interval, exactly one clause fires, selected by the interval alone:

- **POS** — "*[quantity]* was *[point]* with 95% pointwise cluster-level interval [LO, HI], excluding zero above."
- **NULL** — "*[quantity]* was *[point]* in point estimate, with 95% pointwise cluster-level interval [LO, HI]; the interval includes zero, so the ordering is not established."
- **NEG** — "*[quantity]* was *[point]*, with 95% pointwise cluster-level interval [LO, HI], excluding zero below."
- **OPPOSITE** — fires when an interval lies entirely opposite the sign of its own point estimate. "*[quantity]*'s interval [LO, HI] lies entirely opposite its point estimate *[point]*. **No substantive verdict is issued**; this triggers a calibration and integrity review of the input and the resampling before any claim is made." (review item 3, hierarchy level 4)
- **UNRELIABLE** — fires when <99% of resamples are defined. "Fewer than 99% of resamples yielded a defined *[quantity]*; no interval or verdict is issued."

### Composition, C1

The clause for C1's single interval is installed as written. **No outcome
licenses a comparability or equivalence claim.** The manuscript's existing
"comparable information" sentence is deleted regardless of outcome, because no
margin was declared.

### Composition, C2

Four clauses install, one per interval. Then exactly one summary sentence, by rule:

- Both `add_f` and `strat_f` POS → "For the *f* family, under the frozen fitted specifications, each produced incremental out-of-fold AUPRC beyond the other; neither was redundant in these fitted comparisons." *The unqualified "neither subsumes the other" is withdrawn: it reads as a general information-theoretic conclusion, which the conditional estimand of §2 does not support.*
- `add_f` POS, `strat_f` not POS → "For the *f* family, the score added out-of-fold AUPRC beyond the stratum under this fitted specification; whether the stratum adds beyond the score is not established."
- `strat_f` POS, `add_f` not POS → the mirror sentence.
- Neither POS → "For the *f* family, no incremental contribution in either direction is established."
- Any NEG → append: "The combined fitted specification underperformed the *[stratum-only / score-only]* specification. This establishes that adding *[the score / the stratum]* through this modeling procedure did not improve predictive ranking; **it does not establish that it contains no conditional information under every specification**." (review item 1)

**OPPOSITE is controlling in C2.** *If either interval for a family is
OPPOSITE, no family-level summary sentence is issued.* The integrity review
supersedes all substantive composition rules; the four rules above are keyed on
"not POS" and would otherwise emit a substantive conclusion alongside a clause
that declines to issue one. This case is not a variant of "not established" and
is not reported as one.

**UNRELIABLE is not "not established".** Where a direction's interval is
UNRELIABLE, the summary says *that direction was not evaluable reliably —
fewer than 99% of resamples yielded a defined statistic* — never that its
contribution "is not established," which would imply an evaluation that
returned an inconclusive answer rather than one that could not be made.

Families are reported independently; a mixed result across families is stated
as such and never averaged.

### Composition, C3 — the verdict hierarchy

**Exhaustive over all 64 feasible classifications** of Δ₂₀₀, Δ₅₉₀₅ and I, each
in {POS, NEG, NULL, UNRELIABLE, OPPOSITE}. Applied in order; the first matching
level fires and no other. Levels are ordered so that **integrity and
evaluability precede every substantive verdict** — a substantive rule can never
preempt them.

**Level 0 — any of the three intervals is OPPOSITE.** "One or more C3 intervals
lie entirely opposite the sign of their own point estimate. No budget-dependence
or reversal verdict is issued; this triggers a calibration and integrity review
of the inputs and the resampling." No substantive C3 sentence is installed.

**Level 1 — the interaction is UNRELIABLE (and no OPPOSITE).** "Fewer than 99%
of resamples yielded a defined interaction statistic; no verdict on budget
dependence or full reversal is issued." Any marginal clause that is itself valid
is reported **descriptively only**, and no comparative claim is assembled from
the marginals.

**Level 2 — interaction POS *and* both marginals carry the claimed signs**
(Δ₂₀₀ POS, Δ₅₉₀₅ NEG). "Budget dependence and full directional reversal are
established: within-stratum scoring produced higher out-of-fold yield at
*k* = 200 and lower yield at *k* = 5,905, intervals [LO, HI] and [LO, HI], with
the interaction interval [LO, HI] excluding zero."

**Level 3 — interaction POS, one *or both* marginals NULL or UNRELIABLE.**
"Budget dependence is established (interaction interval [LO, HI]); full
directional reversal is not, because *[the k = 200 difference / the k = 5,905
difference / both marginal differences]* *[is / are]* *[unresolved /
not evaluable reliably]*." The slot names every unresolved marginal, including
the case where both are.

**Level 4 — interaction NULL.** "Neither budget dependence nor full reversal is
established. The interaction interval [LO, HI] includes zero. **This holds even
if the two marginal intervals individually show opposite signs**, which is a
descriptive sign difference in this sample rather than demonstrated budget
contingency." Marginal clauses are reported descriptively.

**A positive interaction is required for the full-reversal verdict**, at
level 2. §4 declares that budget dependence is carried by I, so a reversal
sentence resting on the marginals while I is NULL, UNRELIABLE or OPPOSITE would
contradict the document's own estimand. Two marginals with the claimed signs are
necessary and not sufficient.

### Frozen §5 headings

The manuscript edit is mechanical, so the replacement headings are frozen here
rather than chosen after the run:

| Firing level | §5 heading installed |
|---|---|
| 2 | *Stratification is not a remedy: the budget reversal* (unchanged) |
| 3 | *Stratification is not a remedy: the comparison depends on the budget* |
| 4 | *Stratification is not a remedy: a sign difference across budgets* |
| 1 | *Stratification is not a remedy: the budget comparison* |
| 0 | **No heading change.** The existing heading stands and the section carries a stated integrity-review status until the review resolves; no newly interpreted substantive heading is installed on an unresolved integrity signal. |

### Sensitivity disagreement (review item 14)

> The `card1` result determines the registered primary verdict. If either
> sensitivity changes the sign classification, or changes whether zero is
> included, the manuscript states that the conclusion is sensitive to the
> assumed dependence unit. **A sensitivity result never replaces the primary
> result.**

---

## 6. One *valid* run (review item 12)

> The scorer executes once after all validation assertions pass. A run failing
> a preregistered data-integrity, point-estimate, cluster-count, leakage, or
> implementation assertion is **invalid, produces no verdict, and is
> rerunnable**. Any correction and rerun are versioned and fully disclosed. A
> **valid** run's verdicts are final.

Empirical disappointment is not technical invalidity, and the discipline must
not force acceptance of a known-erroneous computation.

**Two safeguards on the rerun path**, so that "versioned and fully disclosed"
cannot become a route to running a silently altered analysis rule:

- **The executed scorer's hash must match the author-approved committed
  version.** The run records the hash it executed; a mismatch is itself an
  invalidity condition.
- **Any correction following an invalid run must be committed, documented, and
  re-approved before another resampling attempt.** Approval is of a specific
  scorer hash, not of the analysis in general, so a corrected script requires a
  fresh approval confirming the correction did not alter the analysis rule.

**Preregistered assertions, all before resampling** (review items 8, 13):

1. Input file hashes match frozen values.
2. Total row count and outcome-positive count match frozen values.
3. `card1`: 13,553 clusters, largest 14,932.
4. `card1`+`addr1`: **39,974 clusters, largest 9,928** — the B-1 corrected values, from re-derivation.
5. Five-field composite: 42,946 clusters, largest 9,900.
6. Nesting holds: composite refines `card1`+`addr1` refines `card1`.
7. No cluster key is NA-derived.
8. **Leakage assertion: no `card1` cluster spans two folds.**
9. **Point-estimate reproduction, from full-precision frozen inputs.** The scorer recomputes **every quantity a clause will report**, and matches each within tolerance 1e-6:
   - the C1 components, AUPRC(stratum-only) and AUPRC(density-score);
   - the **five unique C2 component AUPRCs**, enumerated rather than counted: `AUPRC(density+stratum)`, `AUPRC(digit+stratum)`, `AUPRC(stratum-only)` — common to both families — `AUPRC(density-only)`, `AUPRC(digit-only)`; from which `add_density`, `add_digit`, `strat_density` and `strat_digit` are derived;
   - the C3 marginal lifts at both budgets, pooled and within-stratum.

   **The reference is independently frozen, not recomputed by the same code
   path.** Comparing the scorer against values the scorer itself produced would
   be circular and would validate nothing. Before any resampling, the expected
   full-precision component values are generated once, written to
   `paper/posthoc/cluster_paired/point_reference.json`, **hash-manifested with
   its own manifest row, and committed as part of the freeze**. Assertion 9
   compares the scorer's recomputation against that fixed reference file at
   tolerance 1e-6. The comparison is never against the rounded figures displayed
   in the manuscript: a 1e-6 tolerance applied to a value printed as +0.0088
   would pass or fail for the wrong reason. The reciprocal contrasts have no
   previously published point estimate, so the reference file anchors their
   components and the derivation is checked against it.

Assertion 9 answers the review's question of whether reported point estimates
are recomputed or inserted as constants: **recomputed, and asserted.**

---

## 7. Discipline

This document and `paper/posthoc/cluster_paired.py` commit before any run. No
sensitivity is promoted to primary after the fact. No clause is edited after
seeing an interval. The post-run manuscript edit consists only of installing
the clauses the verdicts select, plus their intervals, plus any §5 heading
change level 2/3/4 requires.
