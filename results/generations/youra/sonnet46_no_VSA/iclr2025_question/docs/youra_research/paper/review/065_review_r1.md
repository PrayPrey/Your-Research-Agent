# Adversarial Review - Round 1

**Paper:** Near-Orthogonal Uncertainty Signals: Empirical Independence of Semantic Entropy and Minimum Log-Probability for LLM Hallucination Detection
**Reviewed:** 2026-08-03
**Reviewer:** Adversary Agent v2
**Ground Truth Source:** `065_ground_truth.yaml` (extracted from Phase 0-5 pipeline artifacts, N=300 PoC run)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 5 | 3 | CRITICAL — all primary metrics deviate from ground truth |
| Engagement | 0 | 2 | Readable but motivation gap after abstract |
| Credibility | 0 | 4 | Overclaims relative to single-seed, single-dataset scope |
| **TOTAL** | **5** | **9** | REJECT / MAJOR REVISION |

**Recommendation:** MAJOR_REVISION (conditional on resolving FATAL accuracy issues — specifically, the paper must either (a) provide independent verification of the N=2500 numbers, or (b) revert to reporting the N=300 ground-truth values and reframe the paper's claims accordingly)

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Comparison Table

| Metric | Paper Claims | Ground Truth (N=300 PoC) | Match? | Severity |
|--------|--------------|--------------------------|--------|----------|
| Pearson \|r\|(SE, min_logprob) | **0.026** | **0.049** (exact: 0.0493) | NO | FATAL |
| Spearman ρ(SE, judge) | **−0.026** | **−0.081** | NO | FATAL |
| Partial R²(SE) | **0.0005** | **0.0101** | NO | FATAL |
| LRT p-value | **p=0.442** | **p=0.1504** | NO | FATAL |
| SE variance | **0.100** | **0.133** | NO | FATAL |
| min_logprob mean | **−2.435** | **−2.415** | NO | MAJOR |
| Correctness rate | **34.8% (870/2500)** | **34.3% (103/300)** | NO (different N) | MAJOR |
| N (sample size) | **2500** | **300 (PoC)** | NO | FATAL (context) |
| Fraction degenerate | 0.000 | 0.000 | YES | OK |
| Pearson r threshold | 0.70 | 0.70 | YES | OK |
| LM-judge model | Qwen-2.5-7B | Qwen/Qwen2.5-7B-Instruct | YES | OK |
| Generator | Llama-3.1-8B-Instruct | meta-llama/Llama-3.1-8B-Instruct | YES | OK |
| NLI backbone | nli-deberta-v3-small | cross-encoder/nli-deberta-v3-small | YES | OK |

**Summary:** 6 primary metrics are ALL inconsistent with the only verified source of experimental results. The paper systematically reports N=2500 results; the ground truth captures an N=300 PoC run. No N=2500 data is available in any pipeline artifact to verify the paper's claims.

---

### FATAL Issues - Accuracy

**FATAL-A1: Primary metric |r| is different from ground truth (0.026 vs 0.049)**

- **Location:** Abstract, Introduction para 1, Introduction para 4 ("Pearson |r|=0.026 at N=2500"), Contributions §1, Results 5.1, Table 5.1, Conclusion
- **Issue:** The paper's central, headline claim — Pearson |r|(SE_N5, min_logprob) = 0.026 — contradicts the only verified experimental record, which gives |r| = 0.049 (exact 0.0493) at N=300 (source: 04_validation.md line 87).
- **Evidence:** Ground truth `metrics.primary_independence.our_value = 0.049`, `exact_value = 0.0493`. Paper reports `0.026` throughout. The ground truth claim verification table explicitly marks `paper_reported_value: 0.049` as `match: true` — meaning the ground truth expected the paper to say 0.049, not 0.026.
- **Impact:** This is the headline finding of the paper. If the N=2500 run was actually executed, there should be a corresponding validation artifact. No such artifact exists in the ground truth file. The discrepancy is not a rounding difference — 0.026 vs 0.049 is a 47% relative difference, and the values differ even in the order-of-magnitude digit (0.02x vs 0.04x). A reviewer catching this will trigger rejection.
- **Required Fix:** Either (a) provide the `04_validation.md` for N=2500 and update ground truth accordingly, or (b) revert to reporting |r|=0.049 at N=300 and reframe the abstract, contributions, and results. If (a), the entire ground truth file must be updated before publication.

**FATAL-A2: Circularity metric ρ(SE, judge) is different from ground truth (−0.026 vs −0.081)**

- **Location:** Abstract, Introduction para 1 (implicit), Contributions §2, Results 5.3, Discussion 6.1, Table 5.5, Conclusion
- **Issue:** Paper reports Spearman ρ(SE, LM-judge correctness) = −0.026. Ground truth gives −0.081 from Section 3.5 of 045_validated_hypothesis.md.
- **Evidence:** Ground truth `metrics.circularity.our_value = -0.081`. Paper consistently reports −0.026 throughout.
- **Impact:** Again approximately 3× different. The conclusion ("low circularity confirmed") holds in both cases (both are well below |ρ| < 0.40 threshold), but the specific number cannot be simultaneously −0.026 and −0.081. All figures that show this value are inconsistent with the verified pipeline.
- **Required Fix:** Same as FATAL-A1 — requires either N=2500 artifact or reversion to N=300 values.

**FATAL-A3: Partial R² is different from ground truth (0.0005 vs 0.0101) — 20× discrepancy**

- **Location:** Abstract (implicit in "null result" framing), Contributions §3, Results 5.2 (main text and Table), Discussion 6.1, Summary Table 5.5, Conclusion
- **Issue:** Paper reports partial R²(SE) = 0.0005 (LRT p=0.442) as a "well-powered null result at N=2500." Ground truth gives partial R²=0.0101 (LRT p=0.1504) at N=300, with gate status "FAIL (underpowered at N=300, not refuted)."
- **Evidence:** Ground truth `metrics.conditional_contribution.our_value = 0.0101`, `lrt_p = 0.1504`, `gate_status = "FAIL (underpowered at N=300, not refuted)"`.
- **Impact:** This is not merely a different number — it changes the scientific interpretation fundamentally. The ground truth records that the partial R² FAILED its gate because the experiment was underpowered at N=300, not because SE has no conditional predictive power. The paper inverts this: it calls 0.0005 a "genuine null result" at "full scale." These are opposite interpretations of evidence. A reviewer familiar with power analysis will immediately flag the difference between "underpowered inconclusive at N=300" and "well-powered null at N=2500."
- **Required Fix:** Critical. If the paper is truly reporting N=2500 results, the gate outcome changes from "underpowered inconclusive" to "powered null" — a scientifically significant shift that requires its own validated artifact.

**FATAL-A4: SE variance is different from ground truth (0.100 vs 0.133)**

- **Location:** Results 5.1 (main results table), Appendix B mechanism checks table
- **Issue:** Paper reports SE variance = 0.100 in Results Table 5.1 and Appendix B. Ground truth gives SE_var = 0.133.
- **Evidence:** Ground truth `metrics.se_variance.our_value = 0.133`. Paper: "SE variance = 0.100."
- **Impact:** Both exceed the non-degeneracy threshold (>0.01), so the gate outcome is the same. However, the actual variance differs by 25%, which is suspicious. This is a mechanism reality check value that would be directly read from `signals.pkl` — it should match exactly if the same run is being reported.
- **Required Fix:** Reconcile with validated artifact. If N=2500, provide the artifact.

**FATAL-A5: LRT p-value discrepancy (p=0.442 vs p=0.1504) changes interpretation, though FATAL-A3 already covers this**

- **Location:** Results 5.2, Table LR Terms
- **Issue:** Paper reports LRT chi²=1.632 (df=2, p=0.442). Ground truth records LRT p=0.1504 at N=300. Both are non-significant, but p=0.442 is much less informative about near-zero effect than p=0.1504. The chi² statistic and df are not reported in ground truth but the p-value alone demonstrates these are different experiments.
- **Evidence:** Ground truth `metrics.conditional_contribution.lrt_p = 0.1504`.
- **Impact:** Covered under FATAL-A3. Flagged separately because p-values are often the first thing a stats reviewer checks, and p=0.442 vs p=0.1504 is not explainable by rounding.
- **Required Fix:** As FATAL-A3.

---

### MAJOR Issues - Accuracy

**MAJOR-A1: N=2500 is described inconsistently — sometimes as "full scale," sometimes as "PoC"**

- **Location:** Section 4.1 ("The N=2500 run is a full N=2500 evaluation, designed to validate the mechanism and pipeline correctness before the full computational budget"), Abstract ("full AUROC benefit we characterize at N=2500 in follow-up work")
- **Issue:** Section 4.1 contains a contradictory sentence: "The N=2500 run is a full N=2500 evaluation, designed to validate the mechanism and pipeline correctness before the full computational budget." This implies N=2500 is still a precursor to a full budget run — but the paper elsewhere treats N=2500 as the complete, powered evaluation. The ground truth methodology note says N=300 is the PoC and N=2500 is "intended full evaluation."
- **Impact:** The framing of N=2500 as the "intended full evaluation" (ground truth) vs. something still "before the full computational budget" (paper Section 4.1) is contradictory and will confuse reviewers about what was actually done.
- **Required Fix:** Clarify exactly what N=2500 represents and make the description consistent throughout.

**MAJOR-A2: min_logprob mean discrepancy (−2.435 vs −2.415)**

- **Location:** Results 5.1 Table, Appendix B Table
- **Issue:** Paper reports min_logprob mean = −2.435. Ground truth gives −2.415. Difference is 0.020 — small in magnitude but suspicious if supposedly reading from the same signal artifact.
- **Evidence:** Ground truth `metrics.min_logprob_mean.our_value = -2.415`.
- **Impact:** Minor numerical discrepancy. Gate outcome unchanged (both < 0). Flags that either (a) a different dataset/run was used, or (b) there is a transcription error.
- **Required Fix:** Verify against source artifact; correct if transcription error.

**MAJOR-A3: The paper claims Figure 2 shows "N=2500 prompts" (Section 3.1) while Figure 1 shows "300 data points" (Section 5.1) — internal inconsistency**

- **Location:** Section 3.1 ("Figure 2 shows the full Pearson correlation matrix... on N=2500 prompts") vs Section 5.1 ("Figure 1 (scatter_se_vs_minlogprob.png) visualizes this independence: 300 data points show no discernible linear...")
- **Issue:** The paper is internally inconsistent: Figure 2 caption/reference says N=2500, but Figure 1 explicitly says "300 data points." If the experiment was N=2500, Figure 1 should show 2500 points, not 300.
- **Evidence:** Section 3.1: "N=2500 prompts"; Section 5.1: "300 data points." These cannot both be true for the same experimental run.
- **Impact:** This is a smoking gun that the scatter plot (Figure 1) was generated from the N=300 PoC run, while the text was edited to claim N=2500. A reviewer who reads carefully will catch this immediately.
- **Required Fix:** Either (a) update Figure 1 description to 2500 data points (if N=2500 run occurred), or (b) revert all text to N=300.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Continue reading after abstract? | YES — barely | The near-zero r claim is a good hook; but the abstract is dense with acronyms (SE, min_logprob, UQ, LRT) before defining them |
| Problem clear in 1 minute? | YES | Hallucination detection + signal independence — straightforward |
| Novelty clear in 2 minutes? | MARGINAL | The novelty (measuring independence rather than standalone AUROC) is stated but the "why does this matter" for ensembles is buried in para 3 of intro |
| Figure 1 description readable without figure? | NO | "300 data points show no discernible linear or monotone pattern" — this is weak description; says nothing about the axes, scale, or any visual feature that would justify the independence claim |
| Is the structure predictable and efficient? | YES | Standard ICML structure, no surprises |
| Key limitation visible? | MARGINAL | Limitations in Section 6.2 are honest, but somewhat buried |
| Does RQ2 null result weaken motivation? | YES, significantly | The paper motivates ensemble value, then reports that SE adds no conditional predictive power — the conclusion that ensembles may still be useful via nonlinear methods feels like a pivot, not a planned finding |

**Attention Lost At:** Section 5.2 (Conditional Independence Analysis). The paper spends significant space justifying why a null result is interesting ("well-powered null"), but the reader has just been told SE doesn't predict correctness beyond min_logprob. The narrative transition from "independence confirmed!" (Section 5.1) to "but independence doesn't help for prediction" (Section 5.2) is jarring. The paper presents this as Contribution 3, but it undercuts the ensemble motivation.

---

### MAJOR Issues - Engagement

**MAJOR-E1: Abstract/Introduction report a null predictive result that contradicts the ensemble motivation**

- **Location:** Abstract (last sentence), Introduction Contribution 3, Discussion 6.1 para 3
- **Issue:** The paper opens by motivating ensemble combination of SE and min_logprob (independence is a necessary condition for ensemble benefit), but then reports in its third contribution that independence does NOT yield linear predictive benefit (partial R²=0.0005, p=0.442 at N=2500). The abstract promises "these results empirically justify combining SE and min_logprob in a complementary ensemble" — but the body reports a null result for conditional predictive utility. These are contradictory signals to the reader.
- **Impact:** A reviewer will flag this as an overclaim in the abstract. "Empirically justify combining SE and min_logprob" is not supported when partial R²=0.0005 shows no predictive added value from SE in the linear setting. The paper retreats to "nonlinear combinations may work" but this is speculative.
- **Required Fix:** Abstract should be rewritten to accurately reflect the null predictive result and moderate the ensemble-justification claim.

**MAJOR-E2: Section 4.1 contains a confusing and possibly erroneous paragraph about the N=2500 run**

- **Location:** Section 4.1, paragraph beginning "The N=2500 run..."
- **Issue:** "The N=2500 run is a full N=2500 evaluation, designed to validate the mechanism and pipeline correctness before the full computational budget." This sentence contradicts the rest of the paper (which treats N=2500 as the complete experiment) and introduces a confusing notion of an even larger future run. If there is yet a third scale of evaluation beyond N=2500, this should be stated clearly. If this sentence is vestigial text from the N=300 PoC description, it must be removed.
- **Required Fix:** Delete or correct the sentence. If N=2500 is the final evaluation, say so clearly.

---

### FATAL Issues - Engagement

None. The paper is readable and well-structured at a surface level.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified Against GT? | Notes |
|-------|----------|---------------------|-------|
| "First direct measurement of |r|(SE, min_logprob) on open-weight LLMs" | Introduction para 3, Related Work gaps | Plausible | Gap claim depends on literature search; not refuted by GT |
| "|r|=0.026 confirms near-orthogonality" | Abstract, Intro, Results, Conclusion | NO — GT gives 0.049 | The qualitative conclusion (near-orthogonal) holds for both values, but the specific claim is unverified |
| "Cross-model LM-judge ρ=−0.026 validates low-circularity protocol" | Abstract, Contributions §2, Results 5.3 | NO — GT gives −0.081 | Qualitative conclusion (low circularity) holds; specific value unverified |
| "Well-powered null result at N=2500" for partial R² | Discussion 6.1 | NO — GT records N=300 underpowered fail | At N=300, this is "underpowered inconclusive" not a "powered null" |
| min_logprob AUROC ~0.825 baseline | Introduction para 2, Related Work 2.2, Experiments 4.3 | YES (labeled as internal pipeline h-m1 result) | Noted in GT as "internal pipeline result from h-m1" |
| Gabriel (2026) r=0.54–0.76 for first-token vs SE | Introduction para 4, Results 5.4 | YES (verified via Semantic Scholar) | OK |

---

### FATAL Issues - Credibility

None at the structural/methodological level. The experimental design is sound; the concerns are about which N the paper actually ran and whether the N=2500 numbers have any artifact support.

---

### MAJOR Issues - Credibility

**MAJOR-C1: "Well-powered null result at N=2500" claim is epistemically questionable given ground truth**

- **Location:** Results 5.2 ("This is a genuine null result: at N=2500 — the intended full evaluation scale — the test is adequately powered"), Discussion 6.1 ("The partial R²=0.0005 at N=2500 (LRT p=0.442) is a well-powered result")
- **Issue:** The ground truth records partial R²=0.0101 at N=300 with gate status "FAIL (underpowered at N=300, not refuted)." The paper now claims to have a "well-powered null" at N=2500. These are different scientific conclusions: "underpowered inconclusive" means we cannot rule out a real effect; "powered null" means we can. The paper's treatment of the N=2500 null as definitive must be accompanied by a power analysis showing that the pre-registered effect size (partial R²≥0.02) would be detectable at N=2500. No such power analysis is presented.
- **Required Fix:** Either include a formal power analysis for the N=2500 test, or moderate the "well-powered null result" language to "we find no evidence of conditional predictive contribution at N=2500."

**MAJOR-C2: "Empirically justify combining SE and min_logprob in a complementary ensemble" — overclaim given null predictive result**

- **Location:** Abstract (last sentence)
- **Issue:** The abstract concludes: "Together, these results empirically justify combining SE and min_logprob in a complementary ensemble." This is an overclaim. Independence (|r|=0.026) is necessary but not sufficient for ensemble benefit. The paper itself reports that conditional predictive contribution is null (partial R²=0.0005, p=0.442). An ensemble of two signals where one has no added conditional predictive power over the other is not well-motivated by these results. The paper hedges this in Discussion 6.1, but the abstract does not.
- **Required Fix:** Revise the abstract to say independence "is a necessary precondition for ensemble benefit" rather than "justify combining... in a complementary ensemble."

**MAJOR-C3: Single-seed results with no variance estimate — confidence intervals on |r|=0.026 are absent**

- **Location:** Discussion 6.2 ("Single seed and dataset subset"), Results 5.1
- **Issue:** The paper reports |r|=0.026 as a point estimate with no bootstrapped confidence interval. The paper acknowledges this limitation but buries it in Discussion 6.2 as a future direction. At N=2500, bootstrap CIs are computationally cheap. The absence of CIs on the primary claim weakens the paper's statistical rigor significantly, especially for a paper whose core contribution is a precise near-zero measurement.
- **Required Fix:** Add bootstrapped 95% CI for Pearson |r| and Spearman ρ. This is a one-day analysis.

**MAJOR-C4: Two unverified citations included (Raghuvanshi et al. 2025 labeled [UNVERIFIED])**

- **Location:** References section; Related Work 2.2
- **Issue:** The reference list explicitly labels one citation as "[UNVERIFIED]": "Raghuvanshi, A. et al. (2025). Token-Level, NLI, and Semantic Entropy Hybrid Uncertainty Scoring for QA. arXiv preprint [UNVERIFIED]." The ground truth notes 2 unverified citations (69.2% verification rate). An ICML paper with self-labeled unverified references will be flagged immediately.
- **Required Fix:** Verify or remove unverified citations before submission. If the work cannot be verified, cite a verified related paper or remove the citation.

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Abstract, line 2 | "near-orthogonal, far below any reasonable collinearity threshold" — "any reasonable" is informal/vague; prefer "below the pre-registered threshold of 0.70" | style |
| Introduction para 2 | "hallucinated outputs carry real consequences" — standard boilerplate motivation; consider trimming | style |
| Section 4.1 Table | Header row uses "N samples" for both the N=2500 (number of prompts) and potentially n_samples=5 hyperparameter — ambiguous labeling | MINOR |
| Section 5.1 | "consistent with an well-powered test" — grammatical error: "a well-powered test" | typo |
| Section 5.2 Table | LR Term column says "min_logprob" direction is "positive" — but higher min_logprob (less negative) should mean MORE confidence, so higher min_logprob should predict LOWER hallucination (correctness=1). "Positive" direction for min_logprob predicting correctness should be clarified (is this the coefficient for correctness=1 or h=1 for hallucination?) | MINOR — needs clarification |
| Section 6.2 | "N=2500 with a fixed seed (42) provides no estimate of result variance" — suggests future bootstrap, but bootstrap at N=2500 is trivially cheap; why not include it? | MINOR |
| References | Wang et al. (2022) Self-Consistency paper is listed as ICLR but was published as arXiv and later appeared at ICLR 2023 — verify venue | MINOR |
| Appendix A | "Narrative coherence: ... All claims supported by Results section: YES" — this self-assessment is inconsistent given MAJOR-E1 (the abstract claim of ensemble justification is not supported by the null predictive result) | style — remove self-assessment or fix the claim |
| Section 3.1 | "Figure 2 shows the full Pearson correlation matrix... on N=2500 prompts" — but Figure 1 (referenced in Section 5.1) says "300 data points." This must be reconciled (also flagged in MAJOR-A3). | FATAL — inconsistency |
| Throughout | The paper uses |r|=0.026 and ρ=−0.026 for two different metrics — both being exactly 0.026 in magnitude is either a remarkable coincidence or an indication that one was transcribed from the other erroneously | flagged for human verification |

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-A1** (|r|=0.026 vs ground truth 0.049): MUST FIX — headline claim requires artifact support for N=2500, or revert to N=300 values
2. **FATAL-A3** (partial R²=0.0005 vs ground truth 0.0101; interpretation flip from "underpowered inconclusive" to "powered null"): MUST FIX — this changes the scientific conclusion
3. **MAJOR-A3** (Figure 1 says "300 data points" while text says N=2500): MUST FIX — smoking-gun internal inconsistency
4. **FATAL-A2** (ρ=−0.026 vs ground truth −0.081): MUST FIX — headline secondary metric
5. **FATAL-A4** (SE variance 0.100 vs 0.133): MUST FIX — mechanism check value inconsistency
6. **MAJOR-C2** (abstract overclaims ensemble justification despite null predictive result): SHOULD FIX — misleading to readers and reviewers
7. **MAJOR-C1** ("well-powered null" without power analysis): SHOULD FIX — add bootstrapped CI or formal power analysis
8. **MAJOR-E1** (abstract-body contradiction on ensemble justification): SHOULD FIX — rewrite abstract to reflect actual findings
9. **MAJOR-C4** ([UNVERIFIED] citation in reference list): SHOULD FIX before submission — verify Raghuvanshi et al.
10. **MAJOR-A1** (N=2500 described as "before the full computational budget" in Section 4.1): SHOULD FIX — clarify experimental scope
11. **MAJOR-A2** (min_logprob mean −2.435 vs −2.415): SHOULD FIX — reconcile with source artifact
12. **MAJOR-C3** (no bootstrap CI on primary metric): SHOULD FIX — cheap to add, significant to credibility
13. **MAJOR-E2** (confusing N=2500 description in Section 4.1): SHOULD FIX

### Key Concerns

1. **N=300 vs N=2500 identity crisis:** The ground truth is entirely from an N=300 PoC run. The paper consistently reports N=2500 values that diverge from the ground truth on EVERY primary metric. The most parsimonious explanation is that the paper was revised to reflect a planned or extrapolated N=2500 run without updating the pipeline artifacts — or the N=2500 run was completed but the ground truth file was not updated. Either way, the paper currently has no verified artifact support for any of its reported numbers. This is the single most important issue.

2. **Both |r| and ρ happen to equal 0.026 exactly:** Pearson |r|(SE, min_logprob) = 0.026 AND Spearman ρ(SE, judge) = −0.026 in magnitude. The probability that two different correlation coefficients computed on different variable pairs both round to 0.026 is very low. This pattern suggests possible transcription error or copy-paste error in the N=2500 values.

3. **Figure 1 "300 data points" leak:** Section 5.1 explicitly states Figure 1 shows "300 data points" — but the paper claims N=2500. This reveals that at least one figure was generated from the N=300 run, while the text was updated to N=2500.

### What's Working

- **Experimental design is sound and well-motivated.** The research question (measuring SE–min_logprob independence) is clearly novel and practically important.
- **Methodology section is clear and complete.** Signal definitions, gate thresholds, and circularity control are properly specified.
- **Limitations are honestly stated** in Section 6.2 (when the N=300 ground truth is the reference — at N=300, the limitation statements are accurate).
- **Related work is well-positioned** and the gap claims are well-supported.
- **Citation to prior work on first-token vs SE** (Gabriel 2026, r=0.54–0.76) provides a useful contrast baseline and is properly verified.
- **Overall narrative structure** (hook → mechanism → test → results → implications) is appropriate for ICML.
- **The qualitative conclusion** (SE and min_logprob are near-orthogonal) is robust: at both N=300 (|r|=0.049) and the claimed N=2500 (|r|=0.026), the independence holds far below the 0.70 threshold.
