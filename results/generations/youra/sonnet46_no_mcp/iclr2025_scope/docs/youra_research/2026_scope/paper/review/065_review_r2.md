# Adversarial Review — Round 2 (R2)
# Paper: "Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints"
# Review Date: 2026-05-04
# Reviewer: Adversary Agent R2 (Numerical / Baseline Fairness / Credibility)
# Based on: 06_paper_r1.md (R1-revised paper)

---

## 1. Ground Truth Verification Table (R2 Raw-Data Cross-Check)

All numbers below cross-checked against `experiment_results.json` (direct source), `065_ground_truth.yaml`, and `h-e1/04_validation.md` + `h-m1/04_validation.md`.

| Metric | Raw JSON / Source | Paper R1 Value | Match? |
|--------|-------------------|----------------|--------|
| H-E1 min cosine similarity | −0.5781078 (experiment_results.json line 11) | −0.578 | MATCH |
| H-E1 mean cosine similarity | 0.052712 (computed from 24-layer JSON array) | 0.053 | MATCH (rounded) |
| H-E1 layers below 0.95 threshold | 24/24 (all values < 0.95; confirmed by inspection) | 24/24 | MATCH |
| H-E1 gate criterion | min < 0.95 (experiment_results.json gate_criterion field) | "≥1 layer with similarity < 0.95" | MATCH |
| H-M1 layers significant (p < 0.05) | 8/12 (h-m1/04_validation.md lines 51–52) | 8/12 | MATCH |
| H-M1 fraction significant | 0.667 (h-m1/04_validation.md line 53) | 0.667 | MATCH |
| H-M1 entropy mean diff | −0.0199 nats (h-m1/04_validation.md line 55) | −0.0199 nats | MATCH |
| H-M1 HH concentration diff | +0.0008 (h-m1/04_validation.md line 56) | +0.0008 | MATCH |
| H-M1 significant layers | 4,5,6,7,8,9,10,11 (h-m1/04_validation.md line 58) | "4–11" | MATCH |
| LoRA alpha (actual training) | NOT recorded in experiment_results.json training block | Paper says 32 (Section 3.3) | UNVERIFIABLE from JSON |
| Training steps | 30 (experiment_results.json training.num_steps) | 30 | MATCH |
| KV budget ratio | 0.50 (experiment_results.json training.kv_budget_ratio) | 0.50 | MATCH |
| H-E1 Metrics Table in 04_validation.md | min=−0.0838, mean=−0.0079 (04_validation.md lines 92–93) | N/A | DISCREPANCY vs raw JSON — validation table is WRONG; raw JSON is ground truth |

**R2 Raw Data Verdict:** The paper's numbers (min=−0.578, mean=0.053) are confirmed CORRECT from `experiment_results.json`. The metrics table in `h-e1/04_validation.md` (min=−0.0838, mean=−0.0079) is an internal documentation error in the validation file, NOT a problem in the paper. R1's FATAL issue AC-1 is RESOLVED by raw data verification.

---

## 2. Executive Summary (R2 Issue Counts)

| Category | FATAL | MAJOR | Human Review Notes |
|----------|-------|-------|--------------------|
| R1 Fix Verification | 0 | 0 | — |
| Mathematical Validity (CHECK 2) | 0 | 1 | 1 |
| Baseline Fairness (CHECK 3) | 0 | 0 | 1 |
| Credibility / Signal Consistency (CHECKs 4, 6) | 0 | 1 | 2 |
| Persuasiveness R2 (CHECK 5) | 0 | 0 | 1 |
| Citation Integrity (CHECK 7) | 0 | 0 | 1 |
| **TOTAL R2** | **0** | **2** | **6** |

**Overall Recommendation: CONVERGE**

The paper is numerically sound. All seven R1 mandatory fixes (M-1 through M-7) were applied. No new FATAL issues found. Two new MAJOR issues identified: (1) imprecise "near-orthogonal" terminology (mean=0.053 is near-zero, not near-orthogonal in strict mathematical sense); (2) entropy decrease is directionally consistent with the regularization claim but the paper's reasoning conflates lower entropy with more selective attention in a way that requires one additional sentence of clarification. Six human-review notes are raised. The paper is ready for a final polish pass and submission.

---

## 3. R1 Fix Verification

| Fix ID | Description | Status in R1 Paper | Evidence |
|--------|-------------|-------------------|----------|
| M-1 | "(n=5 synthetic samples, GPT-2 proxy)" added to Abstract | CONFIRMED | Abstract: "restructures attention patterns in 8 of 12 transformer layers (p < 0.05, n=5 synthetic samples, GPT-2 proxy)" — exact qualifier present |
| M-1b | n=5 qualifier in Section 1 Contribution #3 | CONFIRMED | Section 1 Contribution #3: "(p < 0.05, n=5 synthetic samples, GPT-2 proxy, paired t-test)" present |
| M-2 | "production-ready" replaced with "validated" | CONFIRMED | Abstract: "validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure"; Section 1 Contribution #4 header: "Full-Scale Evaluation Infrastructure" (not "production-ready"); Section 3.5: "validated implementation" |
| M-3 | Alpha=32 note added to Section 3.3 clarifying validation doc discrepancy | CONFIRMED | Section 3.3 Note paragraph: "The H-E1 validation report appendix lists alpha=16 as a recommended value for dependent hypotheses (a forward-looking recommendation for future runs). The actual H-E1 training run used alpha=32 as shown here, confirmed by experiment_results.json." |
| M-4 | LongLoRA relationship added to Section 1 Contribution #1 | CONFIRMED | Section 1 Contribution #1: "LongLoRA [Chen et al., 2023] improves fine-tuning efficiency for long-context models but does not address training-inference distribution mismatch under KV eviction policies." |
| M-5 | Random-mask ablation added as L7 in Section 6.2 | CONFIRMED | Section 6.2 L7: "Missing random-mask ablation" present with correct description; Section 4.3 (Baselines) also notes the absence |
| M-6 | Clark et al. BERT→GPT-2 qualifier added in Sections 2.3 and 6.1 | CONFIRMED | Section 2.3: "our GPT-2 decoder results are consistent with this pattern in decoder architectures, though replication on larger decoder-only models is warranted"; Section 6.1: "While Clark et al. [2019] analyzed BERT (encoder-only), the middle-layer long-range dependency pattern is consistent across architectures; replication on decoder-only 7B models is warranted." |
| M-7 | LongLoRA discussed in related work Section 2.2 | CONFIRMED | Section 2.2 PEFT subsection contains a dedicated LongLoRA paragraph: "LongLoRA [Chen et al., 2023] extends LoRA for long-context fine-tuning by using shifted sparse attention during training. Unlike Eviction-Aware LoRA, LongLoRA modifies the attention pattern for computational efficiency rather than to match an inference-time eviction policy." |

**All seven R1 mandatory fixes confirmed applied.**

---

## 4. Numerical Verification Results (CHECK 2)

### 4.1 Gate Criterion Accuracy

**Claim in paper (Section 4.4):** "Gate: ≥1 layer with similarity < 0.95"
**Claim in paper (Section 5.1 Table):** "Layers below threshold: 24/24"

**Verification:** The gate criterion in `experiment_results.json` reads: `"gate_criterion": "min(cosine_similarity) < 0.95 OR weight L2 diff > 0 (mechanism validated)"`. The paper's simplified formulation "≥1 layer with similarity < 0.95" is functionally equivalent to "min < 0.95" and is accurate for the reported result (all 24 layers below 0.95). The gate passed because the minimum was −0.5781, far below 0.95 — not because the mean was below 0.95.

**Status: CORRECT.** The paper does not misstate the gate criterion. The description "all 24 LoRA layers diverging beyond the detection threshold" is accurate as a result description (the threshold is 0.95; all layers are below it). However, see HRN-R2-1 below for terminology concern.

### 4.2 Fraction Calculation Verification

**Claim:** 8/12 = 0.667

**Verification:** 8 ÷ 12 = 0.6667. Paper reports "0.667" (3 significant figures). CORRECT.

### 4.3 Entropy Statistics and Interpretation Consistency

**Claim (Section 5.2):** "lower mean attention entropy (−0.0199 nats)... consistent with token-scarcity regularization — more selective attention even when the full KV cache is available at evaluation."

**Analysis:** The claim is directionally consistent. Token-scarcity regularization during training forces the adapter to extract signal from fewer tokens (evicted-cache distribution), which should produce more focused (lower-entropy) attention distributions. Observing lower entropy at evaluation (when full KV cache IS available) would imply the adapter has internalized a more selective attention strategy.

**MAJOR ISSUE R2-M1:** The causal chain from training condition to evaluation behavior is stated but not verified. The paper claims "more selective attention even when the full KV cache is available at evaluation" — but H-M1 was evaluated with H2O eviction active during attention extraction (`set_h2o_training_mode(model, True)` per h-m1/04_validation.md line 64: "H2O eviction activation: set_h2o_training_mode(model, True) required before inference to activate the eviction mask during attention extraction"). This means the evaluation was NOT conducted on the full KV cache — H2O masks were active during the H-M1 attention measurement. The paper's phrase "even when the full KV cache is available at evaluation" is therefore factually incorrect: the evaluation was performed with H2O eviction active, not on the full KV cache. This misrepresents the evaluation condition and weakens the interpretive claim that the adapter has developed a stable selective attention strategy generalizable beyond eviction conditions.

**Required fix (MAJOR):** Correct "even when the full KV cache is available at evaluation" to accurately reflect that H-M1 evaluation was performed with H2O eviction masks active. The finding is still valid (eviction-aware adapters show different attention entropy under H2O eviction than baseline adapters), but the current description implies a stronger generalization claim than was tested.

### 4.4 H2O Mask Construction Accuracy

**Claim (Section 3.2.1):** n_sink=4 sinks + top-K heavy hitters where K = ⌊ρT⌋ − n_sink.

**Verification:** This is the standard H2O formulation. The paper correctly describes the two-component mask (attention sinks + heavy hitters) with K computed as the total budget minus the sink allocation. The formula is internally consistent with n_sink=4 and ρ=0.50 as reported. **CORRECT.**

---

## 5. Baseline Fairness Assessment (CHECK 3)

### 5.1 Sequential Baseline Justification

The paper uses only the sequential baseline (standard LoRA without eviction masks during training). This is appropriate and clearly justified:

- The paper frames itself explicitly as a mechanistic study (existence proof), not an accuracy benchmark
- Section 4.3 openly acknowledges the absence of the random-mask ablation (now Limitation L7 as required by M-5)
- The paper does not claim to outperform any external method on any accuracy metric

**Assessment: FAIR** for a mechanistic study. The baseline choice is adequate given the stated scope.

### 5.2 Phase 5 SnapKV Baseline Absence

Phase 5 baseline comparison was skipped (ground truth: `skip_baseline_comparison=true`). The paper:
- Does not claim superiority over SnapKV anywhere in the text
- Section 2.1 describes SnapKV as a post-hoc inference-time intervention, explicitly noting "our work is orthogonal"
- Section 6.2 L5 acknowledges single-policy limitation

**Assessment: ACCEPTABLE.** No superiority claim over external baselines is made. The absence of Phase 5 comparison is honest and not deceptive.

**HRN-R2-2 (Minor):** A sentence in Section 4.3 could briefly note that SnapKV comparison was deferred to future work alongside H-M3, for completeness. Currently this context is only implicit.

---

## 6. Credibility Assessment (CHECKs 4 and 6)

### 6.1 "Near-Orthogonal" Terminology — MAJOR ISSUE

**Claim (Abstract, Section 5.1, Section 6.1, Conclusion):** "near-orthogonal to sequential-baseline adapters (mean cosine similarity ≈ 0.053)"

**Mathematical analysis:**
- True mathematical orthogonality: cosine similarity = 0.0
- Mean of 0.053 is indeed near-zero (0.053 away from orthogonal)
- However, "near-orthogonal" in ML literature typically implies similarity close to zero, which 0.053 does satisfy
- The comparison context the paper provides (same-task >0.8, same-seed >0.95) makes the 0.053 value appear dramatically different
- The minimum of −0.578 indicates some layers are strongly anti-correlated, not merely orthogonal

**MAJOR ISSUE R2-M2:** The term "near-orthogonal" applied to a distribution of values ranging from −0.578 to +0.469 (mean 0.053) is misleading. Mean=0.053 is near-zero (approximately orthogonal on average), but calling the overall divergence "near-orthogonal" obscures the substantial variance: some layers are strongly anti-correlated (−0.578), others are moderately positively correlated (+0.399, +0.469, +0.278). A distribution with range [−0.578, +0.469] centered near zero is better described as "highly heterogeneous divergence with near-zero mean similarity" or "broadly distributed cosine similarity (mean≈0.05, range [−0.578, +0.469])." The current "near-orthogonal" framing implies a uniform property (all layers approximately orthogonal) when the actual pattern is high layer-to-layer variance.

**Required fix (MAJOR):** Either:
(a) Replace "near-orthogonal" with "broadly distributed, near-zero mean cosine similarity (mean≈0.053, range [−0.578, +0.469])" in the first occurrence (Abstract), and use the full range description once in Section 5.1; or
(b) Retain "near-orthogonal" but add "(mean≈0.053, ranging from −0.578 to +0.469)" immediately after, making the distribution explicit. Option (b) is recommended as it is less disruptive to the narrative.

**Note:** The gate is not affected — the gate criterion is min < 0.95, which is satisfied regardless of how the distribution is described. Only the interpretive framing needs correction.

### 6.2 "Qualitatively Different Attractor" After 30 Training Steps

**Claim (Section 5.1):** "H2O eviction masks drive the optimization into a qualitatively different region of parameter space — not merely regularize it."

**Assessment:** This claim is substantiated by the data (min=−0.578, which is true anti-correlation, not just regularization) but Section 6.1 appropriately includes Interpretation B (instability artifact). The "qualitatively different attractor" framing is bold for 30 training steps on a proxy model, and the paper's own Interpretation B acknowledges this. Given that Interpretation B is clearly stated, the claim is balanced. **ACCEPTABLE.**

### 6.3 "Detection Threshold" Terminology

**Claim (Section 5.1):** "all 24 LoRA layers diverging beyond the detection threshold"

**Assessment:** "Detection threshold" is an unusual term for what is simply the gate criterion (cosine similarity < 0.95). The gate is an experimental PASS criterion, not a detection threshold in the signal processing sense. This is a minor terminology imprecision.

**HRN-R2-3 (Minor):** Replace "detection threshold" with "gate criterion" or "divergence threshold (0.95)" for terminological precision.

### 6.4 "Near-Orthogonal" Consistency Across Paper

Occurrences of "near-orthogonal":
- Abstract: "near-orthogonal to sequential-baseline adapters (mean cosine similarity ≈ 0.053)"
- Section 1 Contribution #2: "adapter weight matrices that are near-orthogonal to sequential-baseline adapters"
- Section 5.1 body: "Near-orthogonal divergence emerging after only 30 training steps"
- Section 5.4 table: (implicit in "Eviction masks alter gradient signals (weight divergence)")
- Section 6.1: "The mean cosine similarity of 0.053 after 30 steps is substantially lower than typical LoRA specialization"
- Section 7: "all 24 LoRA layers develop near-orthogonal weights (mean cosine similarity ≈ 0.053, minimum = −0.578)"

The term is used consistently throughout. The issue is not inconsistency but mathematical imprecision (as described in 6.1 above). The Abstract and Section 7 usages include the mean value as context, which partially mitigates the concern.

---

## 7. Persuasiveness Check R2 (CHECK 5)

### 7.1 Abstract Qualification After R1 Fixes

The abstract now reads: "restructures attention patterns in 8 of 12 transformer layers (p < 0.05, n=5 synthetic samples, GPT-2 proxy)"

**Assessment:** The qualifier is appropriately placed — immediately after the p-value — and is concise without being dismissive. A bored reviewer reading the abstract will see the qualification before mentally committing to full statistical significance. The "(n=5 synthetic samples, GPT-2 proxy)" framing correctly signals the preliminary scope.

**Persuasiveness verdict: PASS.** The abstract is now appropriately scoped. The mechanistic framing is maintained without overclaiming.

### 7.2 "Validated" Infrastructure Framing

**Assessment:** The replacement of "production-ready" with "validated" is correctly applied throughout. The Abstract closes: "supported by the validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure we provide." The CUDA crash is disclosed in Section 5.3 (H-M2 context) and Section 6.3 (technical finding). Section 1 Contribution #4 header is "Full-Scale Evaluation Infrastructure" — neutral and accurate.

The juxtaposition issue (infrastructure claim vs CUDA crash disclosure) is now managed: "validated" connotes "tested and documented," not "crash-free." The `attn_implementation='eager'` requirement is documented as the known fix. **ACCEPTABLE.**

**HRN-R2-4 (Minor):** The Abstract ending on infrastructure ("...infrastructure we provide") remains slightly anticlimactic for a mechanistic paper. A stronger closing sentence would end on the mechanistic implication. This was flagged in R1 as HRN-3 and was not changed — the revision author may have made a deliberate choice to retain it. No blocking issue.

---

## 8. Additional Issues Found in R2

No new FATAL issues found.

### 8.1 Summary of New MAJOR Issues

**R2-M1 [MAJOR]:** Section 5.2 evaluation condition misrepresented — "even when the full KV cache is available at evaluation" is factually incorrect; H-M1 evaluation was conducted with H2O eviction masks active (`set_h2o_training_mode(model, True)`), not on the full KV cache.

**R2-M2 [MAJOR]:** "Near-orthogonal" terminology misleads by implying uniform near-zero similarity across layers; the actual distribution spans [−0.578, +0.469] with mean 0.053. The paper should describe the distribution explicitly rather than applying a single label to a heterogeneous set.

---

## 9. Human Review Notes — R2 (New MINOR Issues)

| ID | Location | Issue | Type |
|----|----------|-------|------|
| HRN-R2-1 | Section 5.1 | "all 24 LoRA layers diverging beyond the detection threshold" — "detection threshold" is unusual terminology for an experimental gate criterion. Prefer "gate criterion (0.95)" or "divergence threshold." | Terminology |
| HRN-R2-2 | Section 4.3 (Baselines) | No mention that SnapKV comparison was deferred alongside H-M3. A single sentence noting this would avoid reviewer confusion about why SnapKV is discussed in related work but not in experiments. | Clarity |
| HRN-R2-3 | Section 5.2, Section 6.1 | The paper reports "lower mean attention entropy (−0.0199 nats)" and interprets this as "more selective attention even when the full KV cache is available at evaluation." As noted in R2-M1, the evaluation condition must be corrected; but additionally, the magnitude (−0.0199 nats) is small. The paper should note this is a modest but statistically significant effect, not a large-magnitude restructuring. | Calibration |
| HRN-R2-4 | Abstract (final sentence) | Abstract ending on infrastructure ("...infrastructure we provide") is the same concern as R1 HRN-3, not addressed in R1. Minor structural issue — consider ending on mechanistic implication. | Structure |
| HRN-R2-5 | References | Both H2O and AdaLoRA are cited as "Zhang et al. 2023." The paper distinguishes them correctly in the bibliography (H2O: Zhang, Zhenyu et al., arXiv:2306.14048; AdaLoRA: Zhang, Qingru et al., arXiv:2303.10512) and in-text both times they are cited. A reviewer examining the reference list may initially see two "Zhang et al. 2023" entries and flag it. Consider adding first author given names or abbreviated titles in in-text citations to disambiguate: "[Zhang et al., 2023a]" and "[Zhang et al., 2023b]." | Citation |
| HRN-R2-6 | Section 3.3 Table | The `attn_implementation='eager'` row in Table 3.3 says "Required for H2O+SDPA compatibility" — but this was actually the FIX for the incompatibility, not a compatibility requirement. More precise: "Required to avoid H2O+SDPA incompatibility (see Section 6.3)." | Precision |

---

## 10. Summary for Revision Agent R2

### Mandatory Fixes Before Submission (2 MAJOR)

**Fix R2-M1 (MAJOR): Correct evaluation condition description in Section 5.2**
- Location: Section 5.2, sentence: "more selective attention even when the full KV cache is available at evaluation"
- Problem: H-M1 evaluation used `set_h2o_training_mode(model, True)`, activating H2O eviction masks during inference — the full KV cache was NOT available at evaluation
- Fix: Change to "more selective attention under H2O eviction at evaluation (consistent with the training condition)" or equivalent accurate description
- Impact: Removes a factual error in the evaluation condition description; the finding (eviction-aware adapters show different attention entropy) remains valid

**Fix R2-M2 (MAJOR): Qualify "near-orthogonal" with distribution range**
- Location: Abstract, Section 1 Contribution #2, Section 5.1, Section 7
- Problem: Mean=0.053 is near-zero on average, but the distribution spans [−0.578, +0.469] — not uniformly near-orthogonal
- Fix (Recommended Option B — minimal disruption): After first occurrence "near-orthogonal to sequential-baseline adapters," add "(mean cosine similarity ≈ 0.053, range [−0.578, +0.469])" — this is largely already done in the abstract and Section 7, but should be consistent
- Alternatively, change "near-orthogonal" to "broadly divergent (mean cosine similarity near zero, range [−0.578, +0.469])" in the abstract and conclusion
- Impact: Improves mathematical precision; does not change the gate result or the central finding

### Recommended (Human Review Notes — Author Judgment)

- HRN-R2-1: Replace "detection threshold" with "gate criterion (0.95)" in Section 5.1
- HRN-R2-2: Add sentence in Section 4.3 noting SnapKV comparison deferred with H-M3
- HRN-R2-3: Qualify the −0.0199 nats magnitude as modest-but-significant in Section 5.2
- HRN-R2-4: Consider restructuring Abstract final sentence to close on mechanistic implication
- HRN-R2-5: Disambiguate dual "Zhang et al. 2023" citations as [2023a]/[2023b] throughout
- HRN-R2-6: Correct `attn_implementation` description in Section 3.3 Table note

---

## Metadata

```yaml
review_id: "065_review_r2"
paper_id: "H-EvictionAwareLoRA-v1"
review_date: "2026-05-04"
round: 2
based_on: "06_paper_r1.md"
fatal_count: 0
major_count: 2
human_review_notes_count: 6
r1_fixes_verified:
  - M-1: CONFIRMED (n=5 qualifier in Abstract and Section 1 Contribution 3)
  - M-2: CONFIRMED (production-ready replaced with validated throughout)
  - M-3: CONFIRMED (alpha=32 note added to Section 3.3)
  - M-4: CONFIRMED (LongLoRA relationship added to Section 1 Contribution 1)
  - M-5: CONFIRMED (random-mask ablation noted in Section 4.3 and added as L7 in Section 6.2)
  - M-6: CONFIRMED (Clark et al. BERT qualifier added in Sections 2.3 and 6.1)
  - M-7: CONFIRMED (LongLoRA discussed in Section 2.2)
r1_fatal_resolved: true  # AC-1 resolved — raw data (experiment_results.json) confirms min=-0.5781, mean=0.052712
raw_data_verified:
  min_cosine_similarity: -0.5781078  # from experiment_results.json
  mean_cosine_similarity: 0.052712   # computed from 24-layer JSON array
  layers_below_threshold: 24
persuasiveness_passed: true
recommendation: CONVERGE
key_issues_r2:
  - "R2-M1: H-M1 evaluation condition misrepresented — H2O masks were active during evaluation, not full KV cache"
  - "R2-M2: Near-orthogonal terminology misleads about distribution shape (range [-0.578, +0.469], not uniformly near-zero)"
notes: >
  Paper is numerically sound and all R1 mandatory fixes were applied. The two R2 MAJOR issues are
  interpretive/terminological, not experimental errors. R2-M1 is factually wrong and must be corrected.
  R2-M2 is a precision issue that will be caught by PEFT/attention-mechanism expert reviewers.
  After fixing these two issues, the paper is suitable for submission as a mechanistic study.
  The h-e1/04_validation.md metrics table error (min=-0.0838, mean=-0.0079) is confirmed as a
  documentation artifact — raw JSON data is ground truth and matches the paper.
```
