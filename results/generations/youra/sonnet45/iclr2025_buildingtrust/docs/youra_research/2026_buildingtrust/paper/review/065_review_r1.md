# Adversarial Review — Round 1
**Paper**: Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Argmax Instability After RLHF
**Round**: R1 — Accuracy and Engagement
**Completed**: 2026-03-17T07:10:00Z
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Verification Table

| Claim | Paper Says | Ground Truth | Match |
|-------|-----------|--------------|-------|
| β₁ (DPO/tulu-2-7b) | −4.33 | −4.3295 | PASS (acceptable rounding) |
| p-value (DPO) | ~10⁻²²⁷ | 4.13e-227 | PASS |
| η² | 0.289 | 0.2892 | PASS (acceptable rounding) |
| AUROC MMLU (pair2) | 0.8668 | 0.8668 | PASS (exact) |
| AUROC TruthfulQA (pair2) | 0.8034 | 0.8034 | PASS (exact) |
| AUROC ARC (pair2) | 0.9086 | 0.9086 | PASS (exact) |
| Abstract AUROC=0.91 | 0.91 | 0.9086 → rounds to 0.91 | PASS (acceptable simplification) |
| Flip rate | 12.5% | 0.125 | PASS |
| N items MMLU | 14,042 | 14042 | PASS (exact) |
| β₁ SFT (pair4) | −0.062 | −0.062 | PASS (exact) |
| p-value SFT | 0.00195 | 0.00195 | PASS (exact) |
| AUROC MMLU (pair4) | 0.609 | 0.609 | PASS (exact) |
| Anisotropy ratio pair2 (DPO) | 2.8996 | 2.8996 | PASS (exact) |
| Anisotropy p-value pair2 | 0.0028 | 0.0028 | PASS (exact) |
| Anisotropy ratio pair4 (SFT) | 4.5789 | 4.5789 | PASS (exact) |
| Anisotropy p-value pair4 | 0.0047 | 0.0047 | PASS (exact) |
| Isotropic Gaussian control | ~1.13 | 1.13 | PASS |
| Abstract "2.9–4.6×" range | 2.9–4.6× | 2.8996→2.90, 4.5789→4.58 | PASS (acceptable rounding) |
| DPO Q1 variance | 0.707 | 0.707 | PASS (exact) |
| DPO Q2 variance | 0.996 | 0.996 | PASS (exact) |
| DPO Q3 variance | 1.194 | 1.194 | PASS (exact) |
| DPO Q4 variance | 2.611 | 2.611 | PASS (exact) |
| DPO Q5 variance | 3.384 | 3.384 | PASS (exact) |
| DPO Q5/Q1 ratio | 4.79× | 4.785 | PASS (acceptable rounding) |
| SFT Q1 variance | 0.223 | 0.223 | PASS (exact) |
| SFT Q5 variance | 0.281 | 0.281 | PASS (exact) |
| SFT Q5/Q1 ratio | 1.26× | 1.26 | PASS (exact) |
| H-M2 one-tailed p-value | 1.000 | 1.000 | PASS (exact) |
| H-M2 Cohen's d MMLU | −0.490 | −0.490 | PASS (exact) |
| H-M2 Cohen's d TruthfulQA | −1.536 | −1.536 | PASS (exact) |
| Conclusion anisotropy range | 2.90–4.58× | 2.8996–4.5789 | PASS (correct) |
| Intro AUROC range | 0.803–0.909 | 0.8034–0.9086 | PASS (acceptable) |
| L1 PPO unavailable | Disclosed (Discussion §1) | Required | PASS |
| L2 H-M2 null result | Disclosed (Results RQ3 + Discussion) | Required | PASS |
| L3 H-M3/H-M4 not executed | Disclosed (Discussion §3) | Required | PASS |
| L4 Single DPO pair primary evidence | Disclosed (Discussion §2) | Required | PASS |
| L5 MCQ-only scope | Disclosed (Discussion §4) | Required | PASS |

**Overall: All quantitative claims match ground truth within acceptable rounding. All required limitations are disclosed.**

---

## PERSONA 1: Accuracy Checker

*Role: Cross-check every number in the paper against the ground truth record. Flag discrepancies, overclaiming, and silent omissions.*

### FATAL Issues

None found.

All quantitative claims verified against `065_ground_truth.yaml`. No fabrication, inflation, or silent rounding that changes meaning detected. The abstract's AUROC=0.91 correctly rounds ARC-Challenge=0.9086. The "2.9–4.6×" range accurately brackets 2.8996 and 4.5789. Every table entry matches the verified data exactly.

### MAJOR Issues

**M-AC-1: Abstract AUROC=0.91 is accurate but potentially misleading without inline disclosure**

The abstract states AUROC=0.91 as a single anchor value. The actual range across three benchmarks is 0.8034–0.9086 — a spread of almost 0.11 AUROC units. TruthfulQA (0.8034) is notably lower than the advertised figure. While the abstract correctly identifies this as cross-benchmark and 0.91 legitimately rounds from the ARC result, a reader skimming only the abstract and conclusion will form an impression of a single strong AUROC rather than a range anchored at a weaker TruthfulQA result.

The paper does disclose the full range in the introduction (0.803–0.909) and in Table 1, but the abstract does not include even a parenthetical noting "range 0.80–0.91." This is within acceptable practice for an abstract but is the most likely attack vector from a hostile reviewer: "the authors advertise 0.91 but their weakest benchmark scores only 0.80."

**Severity: MAJOR** — not a fabrication, but creates an exploitable gap between abstract impression and results section reality. Recommend adding "(range 0.80–0.91)" inline in abstract.

**M-AC-2: Conclusion anisotropy range "2.90–4.58×" versus abstract "2.9–4.6×"**

The abstract states "dominant eigenvalue 2.9–4.6 times larger" while the conclusion states "2.90–4.58 times larger." Both are correct — 4.5789 rounds to 4.6 in the abstract and 4.58 in the conclusion. However, 4.58 and 4.6 differ by 0.02 and a careful reader comparing abstract to conclusion may flag this as inconsistency. The paper should use a single consistent rounding (either 4.6 everywhere at one decimal place, or 4.58 everywhere at two).

**Severity: MINOR** (see Minor section) — no factual error, purely a consistency presentation issue. Flagged here for completeness before downgrading to Minor.

**M-AC-3: Results section contains an internal inconsistency in the anisotropy interpretation text**

In the RQ2 results text (Results section, second-to-last paragraph), the paper states: "The observed non-isotropy (ratios 2.6× to 4.1× above the isotropic reference)."

The actual ratios are 2.8996 (pair2) and 4.5789 (pair4), against an isotropic control of 1.13. The ratios relative to the isotropic control are therefore: 2.8996/1.13 ≈ 2.57× and 4.5789/1.13 ≈ 4.05×. The text's parenthetical "(2.6× to 4.1× above the isotropic reference)" is computing a ratio-of-ratios that does not appear in Table 2 and is not how anisotropy was defined in the methodology. Table 2 reports the raw λ₁/mean(λ₂,λ₃,λ₄) ratios (2.8996 and 4.5789), not ratios relative to the isotropic control.

This is an accuracy issue: the in-text "(2.6× to 4.1× above the isotropic reference)" is a derived number that is approximately correct (2.57 rounds to 2.6; 4.05 rounds to 4.1) but is presented as if it appears in the data, when it does not. The phrasing "above the isotropic reference" is also ambiguous — it could mean subtraction (2.90 − 1.13 = 1.77×, not 2.6×) or ratio division. A reviewer will ask: where do 2.6 and 4.1 come from?

**Severity: MAJOR** — this number is not in the ground truth and could be flagged as a fabricated intermediate statistic by a hostile reviewer, even though it is approximately derivable. The sentence should be rewritten to reference the table values directly.

### MINOR Issues (for human review)

- **Minor-AC-1**: Conclusion uses "2.90–4.58×" while abstract uses "2.9–4.6×." Recommend standardizing to one decimal place (2.9–4.6×) throughout for readability consistency.
- **Minor-AC-2**: Introduction section says "Section 4 reports results for all three hypotheses. Section 5 discusses implications..." but the paper structure appears to be: §3 Methodology, §4 Experiments, §5 Results, §6 Discussion, §7 Conclusion. The section numbering in the navigation paragraph may be off by one (calling Results "Section 4" when it is §5). Should be verified against the final compiled document section numbers.
- **Minor-AC-3**: Table 1 header says "AUROC (ARC)" — should be "AUROC (ARC-Challenge)" to match benchmark name as used throughout the paper body.
- **Minor-AC-4**: The paper states Q5/Q1 ratio = "4.79×" in both Table 3 and in summaries; the ground truth gives the exact ratio as 4.785. 4.785 rounds to 4.79, not 4.8, so this is correct — but the rounding to two decimal places while quoting Q1=0.71 and Q5=3.38 (both two significant figures) produces a mild inconsistency: 3.38/0.71 = 4.76×, not 4.79×. The discrepancy arises because Q1=0.707 (not 0.71) and Q5=3.384 (not 3.38). The ratio should be either computed from the displayed rounded values (3.38/0.71 = 4.76×) or the full precision values (3.384/0.707 = 4.785 ≈ 4.79×) should be stated. A reader who recomputes from the table will get 4.76× and be confused. Recommend either (a) display Q1=0.707 and Q5=3.384 in the table, or (b) note the ratio is computed from full-precision values.

---

## PERSONA 2: Bored Reviewer

*Role: A reviewer who has read 300 ML papers this year. Will stop reading if bored. Assesses hook, clarity, novelty signaling, and whether the paper earns continued attention.*

### Persuasiveness Assessment

- **abstract_compelling**: PASS — The opening frame (a single number computed before fine-tuning predicts what alignment will change) is genuinely surprising and stated crisply. The abstract does not oversell. The practical "pre-deployment auditing" punchline is well-placed at the end. Most abstracts in alignment papers spend two sentences on motivation before getting to any result; this one frontloads the result.

- **problem_clear_in_1_minute**: PASS — The introduction opens with the AUROC result in the first sentence, then contextualizes the problem. The 12.5% flip rate on 14,042 MMLU items is a concrete, memorable anchor. A reader one minute in knows exactly what was asked and what was found.

- **novelty_clear_in_2_minutes**: PASS — The related work section executes a clean three-thread literature synthesis and ends with a crisp gap statement: no existing work "poses this prediction problem, operationalizes it as a classification task (flip vs. no-flip), or evaluates it with cross-benchmark generalization." The gap statement is specific enough to be falsifiable.

- **figure_1_self_explanatory**: PASS with caveat — The paper refers to Figure 1 as "fig1_gate_metrics.png" in the results section and separately to "fig1_anisotropy_gate_metrics.png" later in the same section. These appear to be two different Figure 1 references — either there are two figures both called Figure 1 (a numbering error), or the file references are internal labels that do not correspond to the compiled figure numbers. A reader cannot tell from the text which figure is which. This is a presentation-level issue that would confuse any reader not looking at the raw manuscript files.

- **would_continue_reading**: true — The paper moves at a good pace. The quintile flip rate curve (Figure 2 as referenced in RQ1) is the strongest engagement hook: the concrete numbers (Q1 flips 25%, Q5 flips 1.5%, 16× ratio) are memorable and give the abstract result a physical feel. The unexpected null-result-turned-novel-finding in RQ3 is handled with intellectual honesty that makes the paper more, not less, credible.

- **attention_lost_at**: never — The writing is clear and dense without being impenetrable. The discussion reframes findings with good intellectual structure. The conclusion is tight and does not pad.

### FATAL Issues

None found.

### MAJOR Issues

**M-BR-1: Two figures both labeled "Figure 1" in the Results section**

The RQ1 results text reads: "The gate summary visualization (Figure 1, fig1_gate_metrics.png)..." and the RQ2 results text reads: "The anisotropy ratio gate metric visualization (Figure 1, fig1_anisotropy_gate_metrics.png)..." These are two distinct PNG files but both are called "Figure 1." This is almost certainly a figure numbering error in the draft — one should be Figure 1 and one should be Figure 2 (or they should be Figure 1a/1b). A reviewer seeing this will flag it immediately and it undermines the impression of a polished manuscript.

**Severity: MAJOR** — figure numbering errors in a final submission are the kind of careless error that causes rejection at ICLR/NeurIPS on grounds of manuscript quality. Must be fixed before submission.

**M-BR-2: Related work paragraph ends with identical boilerplate sentence three times**

The phrase "However, none of these works predict per-item vulnerability before alignment runs." appears verbatim at the end of three consecutive subsections in the Related Work section (end of "LLM Calibration and Reliability Under Alignment," end of "Pre-Alignment Predictors of Post-Alignment Behavior," and end of "Geometric Analysis of Model Representations"). The repeated sentence is clearly a structural device to drive home the gap, but reading it three times in a row feels formulaic and slightly condescending — as if the reader cannot form the conclusion themselves after the first two instances. By the third repetition, any bored reviewer will have noticed the repetition and will mark it as lazy writing.

**Severity: MAJOR** — this is a writing craft issue that signals to experienced reviewers that the paper was not carefully edited. The gap statement at the end of the section already summarizes the point; the repeated boilerplate in each subsection is redundant and weakens the rhetorical effect.

### MINOR Issues (for human review)

- **Minor-BR-1**: The introduction says "That such a signal exists at all is surprising; that it generalizes across benchmarks without retraining is more surprising still." This is good writing but "more surprising still" is a stylistic intensifier that some reviewers find unscientific. Consider replacing with a factual comparative: "that it generalizes to TruthfulQA and ARC-Challenge without domain adaptation is a strictly stronger result."
- **Minor-BR-2**: Discussion Finding 3 discusses DPO confidence-dependent amplification at length but does not include a forward reference to Table 3 within the finding description — readers wanting to verify the numbers must hunt for the table. Add "(Table 3)" inline when the Q5/Q1 ratio is cited.
- **Minor-BR-3**: The broader impact section references "all code, data, and model checkpoints used in this study are released publicly." If this is a submission and the data/code is not yet publicly released (e.g., the release is contingent on publication), this statement may be premature or violate double-blind review if it links to a repository identifying the authors.

---

## PERSONA 3: Skeptical Expert

*Role: An expert in RLHF, model calibration, and geometric analysis of neural networks. Will probe methodological choices, alternative explanations, and whether conclusions follow from evidence.*

### FATAL Issues

None found.

The core experimental design is internally consistent. The mixed-effects logistic regression with random intercepts per benchmark is an appropriate model for the pooled analysis. The AUROC values are computed on held-out benchmarks (TruthfulQA, ARC) relative to the MMLU training set, which constitutes a legitimate cross-benchmark generalization test. The anisotropy analysis uses a principled spectral method (λ₁/mean(λ₂,λ₃,λ₄)) with an isotropic Gaussian null distribution. No claim requires data the paper does not have.

### MAJOR Issues

**M-SE-1: Model identity confound in the DPO vs. SFT quintile comparison is noted but not fully quantified**

The paper's central behavioral claim — DPO exhibits confidence-dependent amplification while SFT is flat — rests on a comparison between pair2 (tulu-2-7b, 7B, DPO) and pair4 (pythia-6.9b, 6.9B, SFT). These are not only different alignment methods; they are different base model architectures, different training data, and different parameter scales. The paper notes this in Discussion Limitation 2 and in the ground truth as "model identity confound possible." However, the limitation section does not quantify the confound or bound its plausible effect size.

A skeptical expert will ask: given that tulu-2-7b is a far more capable model with significantly more alignment-specific training (allenai/tulu-2 vs. EleutherAI/pythia-6.9b-oasst), could the quintile variance pattern (4.79× gradient in DPO vs. 1.26× in SFT) be entirely explained by model capability differences, dataset quality differences, or the scale mismatch — rather than by the DPO vs. SFT algorithmic distinction? The paper offers a mechanistic interpretation (DPO's pairwise preference objective reinforces confident decisions) but cannot rule out that a tulu-2-7b model trained with SFT would show a similar gradient. The paper acknowledges this but does not strengthen the claim with any bounding argument.

**Severity: MAJOR** — this is the paper's most significant inferential gap. The finding is labeled "novel" and given its own contribution slot. Without controlling for model identity, the DPO-specific attribution is at best MEDIUM confidence (as the ground truth itself notes). The paper should either soften the causal language around Finding 3 or add a brief discussion of plausible confound magnitude. The current discussion does say "controlled experiment required" but does so briefly without walking through why the confound might or might not be dominant.

**M-SE-2: The SFT AUROC=0.609 result is correctly reported but its theoretical interpretation is potentially circular**

The paper explains the SFT pair4 weak result (AUROC=0.609) as follows: "SFT does not optimize a pairwise preference objective, reducing the extent to which the alignment procedure reshapes the confidence geometry near the decision boundary." This explanation is plausible but partially circular: if we already believe that margin predicts flip probability because alignment reshapes confidence geometry, and SFT produces less geometric reshaping, then AUROC=0.609 is explained by SFT producing smaller effects — but we are then predicting that SFT should show weaker margin-flip correlation from the same hypothesis that we are using the SFT result to support. The SFT result is used both as supporting evidence (direction replicates) and explained away as a method difference, but the explanation is post-hoc. A skeptical reviewer will ask whether there is an independent prediction of AUROC for SFT that the paper could have made prior to observing 0.609.

This is not a fatal flaw — the directional replication under SFT is genuinely informative and the AUROC threshold (0.75) was pre-specified. But the interpretive framing should acknowledge that the SFT weak result is consistent with multiple explanations (method, scale, architecture) and is not diagnostic of any single one.

**Severity: MAJOR** — the SFT result is the only replication attempt and its weakness cannot be attributed cleanly to method. Weaken the interpretive claim from "SFT does not optimize a pairwise preference objective, reducing..." to "the weaker SFT result is consistent with method, scale, or architecture differences, and does not allow attribution to any single factor."

**M-SE-3: The "dominant eigenvalue 2.9–4.6× larger than remaining axes" claim needs clearer definition of the denominator**

The paper defines the anisotropy ratio as λ₁/mean(λ₂,λ₃,λ₄), which is the dominant eigenvalue divided by the mean of the three non-dominant eigenvalues of a 4×4 perturbation covariance matrix. The abstract states this as "dominant eigenvalue 2.9–4.6 times larger than remaining axes." The phrase "larger than remaining axes" is ambiguous — it could mean λ₁ is 2.9× the size of each remaining eigenvalue, or 2.9× the mean, or 2.9 units larger. The paper's methodology defines it as the ratio to the mean, which is the correct reading, but the abstract's phrasing "times larger than remaining axes" (plural) suggests the comparison is to individual axes, not their mean. A careful reader will notice this and ask whether the 2.9–4.6 range represents the ratio to the mean or the ratio to the smallest eigenvalue.

**Severity: MINOR** (see Minor section) — the methodology section defines the ratio correctly; this is a precision issue in the abstract's wording. Flagged here before downgrading.

**M-SE-4: Cross-benchmark generalization requires clarification of what "without retraining" means**

The paper claims "cross-benchmark generalization without retraining." The methodology states that the logistic regression predictor was trained on MMLU and evaluated on TruthfulQA and ARC-Challenge. However, the model being evaluated (tulu-2-dpo-7b) was presumably exposed to data spanning all three benchmark domains during its training, and the base model (tulu-2-7b) was also trained on diverse academic data. The "without retraining" refers to the logistic regression predictor, not to the underlying language model. A reviewer might argue that this is a weak form of cross-benchmark generalization: the scalar threshold (β₁ = −4.33) learned on MMLU margins is applied to TruthfulQA and ARC margins, which is genuinely impressive, but the paper should explicitly state this in the abstract or introduction to avoid the impression that the language model itself was zero-shot transferred. The introduction does clarify this correctly ("The predictor was trained on MMLU and evaluated on TruthfulQA and ARC-Challenge without retraining"), but the abstract's "generalizing cross-benchmark without retraining" is still ambiguous about what is being retrained.

**Severity: MINOR** (see Minor section) — the paper body clarifies correctly, but abstract ambiguity is an attack surface.

### MINOR Issues (for human review)

- **Minor-SE-1**: Abstract says "2.9–4.6 times larger than remaining axes." Should specify "times larger than the mean of the remaining axes" to match the formal definition λ₁/mean(λ₂,λ₃,λ₄). The current phrasing could be read as each remaining axis, not the mean.
- **Minor-SE-2**: The H-M2 null result discussion states Cohen's d = −0.490 on MMLU, which indicates a medium-to-large effect in the wrong direction. The paper correctly reports this. However, the paper does not report confidence intervals for the quintile variances in Table 3. Given that Q4 DPO = 2.611 and Q5 DPO = 3.384 are the most important cells for the amplification claim, confidence intervals or standard errors for these cells would strengthen the novel finding's credibility.
- **Minor-SE-3**: The anisotropy p-values (0.0028 for pair2, 0.0047 for pair4) both pass α=0.05 but do not pass a Bonferroni correction for two tests (α_corrected = 0.025). The paper does not apply multiple comparisons correction to the anisotropy tests. This is defensible given the confirmatory rather than exploratory nature of H-M1, but should be explicitly acknowledged (even a single sentence: "We do not apply Bonferroni correction to H-M1 as these are two planned confirmatory tests of the same structural hypothesis across two model pairs").
- **Minor-SE-4**: The paper refers to the pre-alignment margin as "z-scored" in the methodology description but does not specify the z-scoring procedure: z-scored per item across all choices, per benchmark, or per model? The exact normalization matters for reproducibility.
- **Minor-SE-5**: Conclusion states "the original PPO comparison remains unrealized and is high priority" — this is honest and appropriate. However, the broader impact section's claim that "the findings are presented under open science principles" and that "all code, data, and model checkpoints used in this study are released publicly" is a promise that should be tracked against actual repository state. If code is not yet released, this claim is premature.

---

## Round 1 Summary

| Severity | Accuracy Checker | Bored Reviewer | Skeptical Expert | Total |
|----------|-----------------|----------------|-----------------|-------|
| FATAL    | 0 | 0 | 0 | **0** |
| MAJOR    | 2 | 2 | 2 | **6** |
| MINOR    | 4 | 3 | 5 | **12** (→ human review) |

**Recommendation**: PASS_TO_R2 with MAJOR revisions required before submission.

The paper's core empirical claims are fully accurate and all required limitations are properly disclosed. No FATAL issues were found. The six MAJOR issues are addressable revisions:

1. **M-AC-1** (AUROC abstract impression): Add "(range 0.80–0.91)" to abstract.
2. **M-AC-3** (in-text ratio "2.6× to 4.1×" not defined in table): Rewrite to reference table values directly.
3. **M-BR-1** (Figure 1 referenced twice for two different figures): Fix figure numbering throughout manuscript.
4. **M-BR-2** (repeated boilerplate sentence in related work): Remove the repetitive sentence from subsections 1 and 2; keep only in subsection 3 or in the gap statement.
5. **M-SE-1** (model identity confound under-bounded): Expand Discussion Limitation 2 with plausible bound on confound magnitude.
6. **M-SE-2** (SFT weak-result interpretation is partially circular): Weaken causal language; attribute to "method, scale, or architecture" rather than method alone.

**Return Summary**:
- fatal_count: 0
- major_count: 6
- human_review_notes_count: 12
- key_concerns:
  - Figure numbering error (two Figure 1s in Results section) — must fix before submission
  - Repeated boilerplate sentence in related work damages writing quality impression
  - In-text derived ratio "2.6× to 4.1×" not traceable to table values — attack surface for accuracy challenge
  - Model identity confound in DPO vs SFT quintile comparison needs stronger bounding in Discussion
  - Abstract AUROC=0.91 single anchor vs actual range 0.80–0.91 is exploitable by hostile reviewer
  - SFT result interpretation partially circular; causal attribution to method difference is not cleanly supported
- persuasiveness_passed: true
