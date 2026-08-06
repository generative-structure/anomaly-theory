## Bottom line

**I would not approve the freeze in its current form.** The preregistration is unusually disciplined and transparent, but several licensed conclusions do not follow from the registered statistics. Three problems are load-bearing:

1. **C2 does not test the two-sided nonredundancy claim it purports to test.**
2. **C1 treats failure to reject a difference as evidence of comparability.**
3. **C3 identifies the interaction as the direct reversal statistic but does not use it coherently in the verdict rules.**

There are also unresolved questions about what uncertainty the bootstrap represents, whether the original out-of-fold predictions are cluster-independent, and whether the code is sufficiently specified to justify the statement that no runtime choices remain.

## What is strong

Several aspects are excellent and should remain:

- The loss of blindness is stated candidly rather than cosmetically reconstructed.
- The primary clustering rule is conservative and selects the widest previously observed interval rather than the most favorable result.
- The erroneous archived clustering artifact is preserved for provenance but excluded from computation.
- Pairing the two statistics within every cluster resample is exactly right for estimating uncertainty in their difference.
- The document precommits to reporting both clustering sensitivities.
- The unfavorable-result language is written before the run.
- The risk note identifies C2 and C3 as exposed claims rather than pretending that every outcome would be equally satisfactory.

This is a strong foundation. The problem is primarily **claim-statistic correspondence**, not lack of discipline.

# Required revisions before approval

## 1. C2 does not establish “neither subsumes the other”

The registered C2 statistic is:

## [ \operatorname{AUPRC}(\text{score+stratum})

\operatorname{AUPRC}(\text{stratum-only}).
]

A positive result establishes only that, under the fitted modeling procedure, **adding the score to the stratum improves predictive performance**. It addresses whether the score is redundant conditional on the stratum.

It does **not** test whether the stratum is redundant conditional on the score. That would require the second contrast:

## [ \operatorname{AUPRC}(\text{score+stratum})

\operatorname{AUPRC}(\text{score-only}).
]

Therefore, the sentence:

> “Neither the score nor the stratum subsumes the other.”

is not licensed by the registered analysis.

There are two defensible solutions:

- **Add the reciprocal contrast** for both score families before freezing; or
- Narrow the claim to:
  **“The score adds predictive performance beyond the stratum under this fitted specification.”**

The reciprocal comparison is preferable if two-sided nonredundancy is important to the paper. Otherwise, do not use “neither subsumes the other.”

C2-c also overreaches. If the combined fitted model has lower AUPRC than the stratum-only model, that does not prove that the score “contributes nothing” or contains no information. It may show that this particular combination procedure fails to exploit the score, overfits, or changes the ranking adversely.

The defensible negative-result sentence is:

> The fitted score-plus-stratum specification underperformed the stratum-only specification. This establishes that adding the score through this modeling procedure did not improve predictive ranking; it does not establish that the score contains no conditional information under every specification.

This is the most important correction.

## 2. C1 confuses an unresolved difference with equivalence

C1-a currently says that if the interval covers zero, the two predictors perform “about equally well” and carry “comparable information.”

That inference is invalid. A confidence interval containing zero shows only that the analysis **does not establish an ordering**. A wide interval can contain both substantively important positive and negative differences.

To claim equivalence or comparability, you need a preregistered equivalence margin (\varepsilon) and must require:

[
CI \subseteq [-\varepsilon,\varepsilon].
]

The margin must be substantively justified—for example, by the smallest AUPRC difference the paper regards as operationally meaningful. It cannot be selected after seeing the interval.

Without an equivalence margin, C1-a should say:

> The paired difference was +0.00089 AUPRC, with a 95% cluster-level interval of [LO, HI]. Because the interval includes zero, these data do not establish which specification has higher AUPRC.

You may describe the point difference as small. You cannot conclude comparable information from zero inclusion alone.

## 3. The C3 decision logic does not correspond to the stated claim

The document correctly recognizes that the direct statistic for budget dependence is:

[
I=\Delta_{200}-\Delta_{5905}.
]

But the licensed verdicts are controlled principally by the two marginal intervals. The interaction interval is reported but does not determine the conclusion.

Three distinct claims must be separated:

### Full directional reversal

This requires establishing both:

[
\Delta_{200}>0
\quad\text{and}\quad
\Delta_{5905}<0.
]

The two marginal intervals must exclude zero with those respective signs.

### Budget-dependent comparative effect

This requires:

[
I=\Delta_{200}-\Delta_{5905}>0,
]

with the interaction interval excluding zero. This can survive even when one marginal difference is individually unresolved.

### Point-estimate sign change only

If the interaction interval covers zero and one or both marginal intervals cover zero, the evidence supports only a descriptive sign difference in the observed sample—not demonstrated budget contingency.

I recommend the following verdict hierarchy:

1. **Both marginal signs established:** full reversal established.
2. **Interaction established but one marginal sign unresolved:** the comparison changes significantly with budget, but a two-direction reversal is not established.
3. **Interaction unresolved:** budget dependence is not established; only the observed point estimates differ.
4. **An interval lies entirely opposite its observed point estimate:** invoke an integrity/calibration review rather than automatically making the opposite substantive claim.

The current C3-b says that if either marginal interval covers zero, the section may still “claim the contingency.” That is justified only when the interaction interval excludes zero.

## 4. The licensed outcomes are not exhaustive

C2 has two score families, but the document provides only broad outcomes corresponding roughly to:

- both positive,
- both unresolved,
- negative.

It does not address mixed results, such as:

- Density positive; digit-law unresolved.
- Density unresolved; digit-law positive.
- One positive; one negative.
- One negative; one unresolved.

Similarly, C3 does not fully handle:

- One budget established in the claimed direction and the other established in the opposite-to-claimed direction.
- Interaction significant but one marginal interval unresolved.
- Marginal reversal established but interaction interval unexpectedly unresolved.

Rather than writing every combinatorial sentence, preregister **family-specific clauses** that are assembled according to each interval’s result. For example:

- “The density increment was positive and resolved.”
- “The digit-law increment was positive in point estimate but unresolved.”
- “The density increment was negative and resolved.”

That produces exhaustive result handling without allowing post-run rhetorical discretion.

## 5. State the estimand more precisely

The document says the estimand concerns differences between statistics computed on the same OOF predictions. That describes the calculation, but not the inferential target.

The bootstrap appears to estimate variation from resampling empirical clusters while treating the following as fixed:

- model specifications,
- fitted models,
- hyperparameters,
- fold assignments,
- random seeds,
- generated OOF predictions,
- stratum construction,
- score construction.

It therefore does **not** estimate total uncertainty from retraining the entire procedure on another sample. The conclusions should be explicitly conditional:

> The intervals quantify cluster-resampling uncertainty conditional on the frozen out-of-fold predictions, fitted specifications, folds, and algorithm seeds.

That limitation should appear in C1 and C2, not only in C3.

Statements such as “predicts the outcome better” should preferably be written as:

> produced higher out-of-fold AUPRC under the frozen fitted specifications.

That is narrower but exactly supported.

## 6. Confirm that the OOF construction was cluster-disjoint

This is potentially load-bearing.

Cluster bootstrapping the final predictions accounts for dependence in the **evaluation statistics**. It does not correct leakage introduced during model fitting.

The preregistration should state whether rows sharing `card1` were ever divided between training and held-out folds. If they were, the model may have been trained on other observations from the same primary cluster before predicting a held-out row.

Three cases are possible:

- **Folds were already group-disjoint under `card1`:** state and verify this with an assertion.
- **Clusters crossed folds, but the analysis is deliberately conditional and descriptive:** state that the results are row-level OOF predictions with cluster-resampled evaluation, not cluster-level out-of-sample performance.
- **The manuscript wants generalization to unseen clusters:** grouped refitting is necessary; bootstrapping frozen predictions is insufficient.

The rationale rejecting grouped repeated CV is valid only after resolving this issue. Fold noise may not be the target, but group leakage can still make refitting necessary.

## 7. `card1` must be shown to be a defensible dependence unit

The conservative principle is reasonable, but “coarsest” is not sufficient. A coarser grouping can also combine unrelated observations, producing unnecessary conservatism and changing the implied population.

The document should explain substantively why shared `card1` values plausibly create dependence. At present it establishes only that `card1` produces:

- fewer clusters,
- a larger maximum cluster,
- wider intervals in a prior analysis.

Those facts show conservatism; they do not establish that `card1` is an actual dependence unit.

Also revise:

> “Nothing empirical discriminates among the candidates.”

The interval widths themselves empirically differ, and one outcome-variance statistic is not a complete dependence diagnostic. A more accurate statement would be:

> The prespecified between-cluster outcome-variance diagnostic differed little across the three nested candidates and did not provide a compelling basis for choosing among them.

I would also avoid “most dependence absorbed” unless an intracluster-correlation or design-effect analysis supports that phrase.

## 8. The claim that no free runtime parameter exists is currently too strong

Several implementation choices are not specified in the document:

- The exact AUPRC definition and software function. Average precision and trapezoidal PR area are not identical.
- The exact definition of `lift`.
- The reference prevalence used in the lift denominator.
- Integer allocation of the within-stratum worklist.
- Rounding and remainder distribution among strata.
- Treatment of strata receiving zero slots.
- Treatment of clusters drawn more than once.
- Tie-breaking between duplicate bootstrap copies having the same original row index.
- Quantile interpolation method for the 2.5th and 97.5th percentiles.
- Handling of missing predictions, outcomes, strata, or cluster values.
- Positive-class encoding.
- Whether the reported point estimates are recomputed by the scorer or merely inserted as constants.
- Numerical tolerances used by validation assertions.

These should be frozen either in the preregistration or in a code specification referenced by exact commit hash.

At minimum, the scorer should assert before resampling that it reproduces all original point estimates within a frozen tolerance.

## 9. The degenerate-resample rule needs a validity threshold

The phrase “no positive outcome in either arm” is confusing because the AUPRC comparisons use the same outcome vector for both prediction systems. There are not separate outcome arms.

Specify separately:

- AUPRC is undefined if the complete bootstrap resample contains no positive observations.
- Worklist yield of zero is ordinarily defined if a selected worklist contains no positives.
- Lift may be undefined if the resample-wide reference prevalence is zero, depending on its definition.

More importantly, calculating the interval only over defined resamples conditions on nondegeneracy. That may be harmless if there are zero or one such cases, but not if a meaningful proportion is omitted.

Preregister a rule such as:

- Report effective (B).
- If fewer than 99% of resamples are defined for a statistic, do not issue its planned confidence interval or verdict; classify the bootstrap result as unreliable.

The exact threshold is a design choice, but some threshold is needed.

## 10. Increase the bootstrap count

(B=2{,}000) is not inherently invalid, but it is light for irreversible decisions based on whether an endpoint crosses zero.

At (B=2{,}000), each 2.5% tail contains only about 50 resamples. The Monte Carlo standard error of the percentile probability is approximately:

[
\sqrt{\frac{0.025(0.975)}{2000}}\approx 0.0035.
]

That is material when a verdict may turn on a narrowly positive or negative endpoint.

Because nothing has been run, I would increase this to at least **10,000**, preferably **20,000**, assuming computation is feasible. A fixed seed still produces one completely reproducible result.

The increased (B) does not create analytic flexibility; it reduces simulation noise.

## 11. Specify the meaning of fixed (k) under cluster resampling

Resampling unequal-sized clusters produces a bootstrap dataset whose total number of rows varies. The document should explicitly state whether:

- (k=200) and (k=5{,}905) remain fixed absolute worklist capacities in every resample; or
- the budgets are scaled to preserve their original sampling fractions.

Either can be defensible, but they estimate different operational questions.

Given the manuscript’s worklist framing, **fixed absolute (k)** is probably preferable: the auditor can inspect 200 cases regardless of the population realization. State that explicitly and explain that the bootstrap therefore targets uncertainty at fixed operational capacities, not fixed review percentages.

Also ensure that a bootstrap sample containing fewer than (k) rows has a predefined treatment, even if that event is practically impossible.

## 12. Replace “one run, verdicts final” with “one valid run”

The discipline is admirable, but a result should not become final if:

- the input hash is wrong,
- an assertion fails,
- the old NA-concatenation error recurs,
- point estimates are not reproduced,
- the script handles duplicate clusters incorrectly,
- a software-version difference changes the calculation.

The protocol should distinguish empirical disappointment from technical invalidity:

> The scorer is executed once after all validation tests pass. A run failing a preregistered data-integrity, point-estimate, cluster-count, or implementation assertion is invalid and produces no verdict. Any correction and rerun are versioned and fully disclosed.

Otherwise the “one run” rule could force acceptance of a known erroneous computation—the opposite of scientific discipline.

## 13. Add hard validation assertions around the corrected clustering

Routing around the bad artifact is appropriate, but the runtime re-derivation should assert the expected quantities before continuing:

- `card1`: 13,553 clusters; maximum size 14,932.
- `card1+addr1`: 39,974 clusters; maximum size 9,928.
- Corresponding counts for the five-field composite.
- Total row count.
- Outcome-positive count.
- No unintended NA cluster keys.
- Nesting relationships among the three assignments.
- Input file hashes.
- Exact point-statistic reproduction.

I would also create a new, hash-manifested corrected clustering summary. Preserve the erroneous file unchanged, but do not make runtime re-derivation the only canonical record of the correction.

## 14. Precommit how sensitivity disagreement affects the prose

The document says both sensitivity results will be reported, but it does not say what happens if they disagree materially with `card1`.

Precommit something like:

> The `card1` result determines the registered primary verdict. If either sensitivity changes the sign classification or whether zero is included, the manuscript will state that the conclusion is sensitive to the assumed dependence unit. A sensitivity result will not replace the primary result.

That preserves primacy while preventing a formally reported but rhetorically buried contradiction.

## 15. Label intervals as pointwise unless you add simultaneous control

The procedure will produce multiple intervals:

- one for C1,
- two for C2,
- two marginal C3 intervals,
- one C3 interaction interval,
- repeated under three clustering definitions.

The preregistration should call these **pointwise 95% intervals**. That is probably sufficient if each claim is interpreted exactly as registered and no favorable result is selected from the family. Do not describe the collection as having a joint 95% confidence level.

# Recommended revised claim structure

The cleanest architecture would be:

### C1: Ordering, not equivalence

- CI excludes zero positive: stratum-only has higher conditional OOF AUPRC.
- CI includes zero: ordering not established.
- CI excludes zero negative despite a positive original estimate: no automatic substantive verdict; trigger calibration/integrity language.

### C2: Incremental value, separately by family

For each score family independently:

- Positive interval: adding that score to the stratum improved fitted OOF ranking.
- Interval includes zero: incremental improvement not established.
- Negative interval: the combined fitted specification underperformed stratum-only.

Use “neither subsumes the other” only if the reciprocal score-only contrasts are added and supported.

### C3: Two levels of claim

- **Budget effect:** determined by the interaction interval.
- **Full reversal:** determined by both marginal intervals having the claimed signs.

This gives the interaction a genuine inferential role and avoids treating “budget dependence” and “two-direction reversal” as synonyms.

# Approval recommendation

**Revise before author approval and before any resampling.** I would classify the changes as follows:

- **Mandatory for validity:** C1 equivalence correction; C2 logic correction; C3 interaction/verdict correction; exhaustive mixed-result handling; conditional-estimand statement; group leakage check.
- **Mandatory for reproducibility:** exact statistic definitions, validation assertions, valid-run rule, degeneracy threshold.
- **Strongly recommended:** increase (B), precommit sensitivity-disagreement wording, and state fixed-(k) semantics.

After those revisions, this would be a very strong preregistration. In its present form, the discipline is stronger than the inferential logic: it risks irrevocably freezing conclusions that the registered comparisons cannot support.