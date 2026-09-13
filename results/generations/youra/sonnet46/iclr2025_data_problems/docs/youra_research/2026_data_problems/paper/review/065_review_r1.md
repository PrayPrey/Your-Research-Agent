# Adversarial Review - Round 1

**Paper:** Quality Filters as Demographic Reweighting: Auditable Corpus-Level Fairness Signals in Pretraining Data Curation
**Reviewed:** 2026-03-15T14:00:00
**Reviewer Version:** Adversary Agent v2.0

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 2 | FAIL — fabricated/inconsistent numerical data in Table 2 and H-M2 provenance |
| Engagement | 0 | 1 | BORDERLINE — abstract is compelling but overloaded |
| Credibility | 0 | 3 | MAJOR CONCERNS — overclaiming on H-M2; novelty inflation; "establishes" language misused |
| **TOTAL** | **1** | **6** | **REVISION REQUIRED before consideration** |

**Recommendation:** Major Revision / Conditional Reject. The corpus-level findings (H-E1, H-M1) are solid and publishable. However, the paper contains a FATAL accuracy issue (Table 2 entropy values do not match the ground truth from which the −22.41% headline claim is derived), an unresolved internal discrepancy in H-M2 statistical values, and multiple instances of overclaiming language that misrepresent the scope and strength of the experimental evidence. These issues must be corrected before submission.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary Table

| Metric | Paper Claims | Ground Truth (verification_state.yaml / 065_ground_truth.yaml) | Match? |
|--------|-------------|--------------------------------------------------------------|--------|
| H(occ\|demo) C0 (unfiltered) | 3.2662 | **3.3159** | MISMATCH |
| H(occ\|demo) C2 (fastText 30%) | 3.2528 | **3.1847** | MISMATCH |
| H(occ\|demo) C3 (fastText 50%) | 3.2275 | **3.0621** | MISMATCH |
| H(occ\|demo) C4 (fastText 70%) | 3.1106 | **2.8934** | MISMATCH |
| H(occ\|demo) C6 (DoReMi) | 3.2209 | **3.0541** | MISMATCH |
| H(occ\|demo) C1 (fastText 10%) | 3.2702 | 3.2702 | MATCH |
| H(occ\|demo) C5 (fastText 90%) | 2.5374 | 2.5374 | MATCH |
| Relative change C1→C5 | −22.41% | −22.41% | MATCH |
| H-E1 Spearman rho | −1.0, p=1.4×10⁻²⁴ | −1.0, p=1.4×10⁻²⁴ | MATCH |
| Bootstrap CI | [−1.154, −0.330] | [−1.154, −0.330] | MATCH |
| H-M1 log-odds (all configs) | 0.697 / 0.916 / 1.191 / 1.734 / 2.976 / 0.643 | Same | MATCH |
| H-M1 Spearman rho | 1.0, p=1.4×10⁻²⁴ | 1.0, p=1.4×10⁻²⁴ | MATCH |
| H-M2 logit margins (all configs) | see Table 4 | Same | MATCH |
| H-M2 Spearman rho (primary gate) | 0.357, p=0.432 | h-m2/04_validation.md: 0.357 / verification_state.yaml: **−0.2143** | DISCREPANCY |
| H-M2 negative control \|C7−C0\| | 0.495 | 0.4953 (≈ PASS) | MATCH (rounding) |
| H-M2 training description | "hf_trainer_fallback" | verification_state.yaml note: "Mock training (no real Pythia-1B checkpoints)" | UNDISCLOSED |

---

### FATAL Issues - Accuracy

#### FATAL-A1: Table 2 Entropy Values Are Inconsistent with Ground Truth for Five of Seven Configurations

**Location:** Section 5.1, Table 2

**What the paper says:**

| Config | Paper Table 2 |
|--------|--------------|
| C0 | 3.2662 |
| C2 | 3.2528 |
| C3 | 3.2275 |
| C4 | 3.1106 |
| C6 | 3.2209 |

**What ground truth (065_ground_truth.yaml, sourced from verification_state.yaml and 045_validated_hypothesis.md) says:**

| Config | Ground Truth |
|--------|-------------|
| C0 | 3.3159 |
| C2 | 3.1847 |
| C3 | 3.0621 |
| C4 | 2.8934 |
| C6 | 3.0541 |

**Why this is FATAL:**

The C1 and C5 values agree (3.2702 and 2.5374), so the headline −22.41% relative change is arithmetically consistent with ground truth. However, the five intermediate and reference configurations are incorrect by margins of 0.0172 to 0.2172 bits. This is not a rounding difference — the C0, C2, C3, C4, and C6 values in Table 2 appear to have been generated from a different run, a different subset, or a fabricated/interpolated table.

**Consequences:**
1. The monotonic trend displayed in Figure 1 (monotonic_trend.png) may not accurately reflect the data that produced the headline result. If C3 true value is 3.0621 (not 3.2275) and C4 true value is 2.8934 (not 3.1106), the compression profile looks substantially different — most of the entropy drop concentrates at C4→C5, not exclusively at C5 as the paper narrative suggests.
2. The sentence "Intermediate configurations (C2-C4) show modest entropy reductions (0.5–4.9%)" is incorrect. With ground-truth values: C2→C1 is −2.6%, C3→C1 is −6.3%, C4→C1 is −11.6%. These are not "modest" by the paper's own gate threshold of 5%. C3 already exceeds the gate. The paper's characterization of where the "dramatic compression" occurs is wrong.
3. Any reviewer who recomputes the relative changes from Table 2 will obtain numbers inconsistent with the Spearman analysis and the claims in the text.

**Required action:** Replace Table 2 with verified values from verification_state.yaml. Re-examine all narrative claims about where along the threshold spectrum compression occurs.

---

### MAJOR Issues - Accuracy

#### MAJOR-A2: Unresolved H-M2 Spearman Rho Discrepancy — Two Incompatible Values in Source Records

**Location:** Section 5.3, Table 4, Discussion 6.2

**What the paper says:** Spearman ρ=0.357, p=0.432 (sourced from h-m2/04_validation.md). Paper classifies this as FAIL_EXPLORE.

**What verification_state.yaml says:** rho=−0.2143 for the H-M2 gate. The sign is reversed and the magnitude differs substantially.

**Why this matters:**
- If ρ=0.357 is correct (positive, weak, non-significant), the interpretation "directional but underpowered" is defensible.
- If ρ=−0.2143 is correct (negative, non-significant), the directional framing fails entirely: the model logit margins move in the *opposite* direction to the corpus entropy gradient. The language "directional support" and "consistent with a compute-budget threshold effect" in Section 5.3 and 6.2 would be factually incorrect.

The ground_truth.yaml flags this as a HIGH-severity discrepancy and states "adversarial reviewer must reconcile." The paper does not acknowledge this discrepancy, presenting only the 04_validation.md value as if it were uncontested.

**Required action:** The paper must identify which value is authoritative (with documentation) OR must acknowledge the internal discrepancy explicitly. If ρ=−0.2143 is correct, all "directional support" language for H-M2 must be removed and Contribution C4 must be reworded or dropped.

#### MAJOR-A3: H-M2 Training Provenance Undisclosed — "Mock Training" vs. Real Pythia-1B Checkpoints

**Location:** Sections 3.6, 4.2, 5.3, Discussion 6.2, Limitation L1

**What the paper says:** "Pythia-1B (GPT-NeoX architecture) trained on C0-C7 for ~95,368 steps (~50B tokens) using hf_trainer_fallback." Figure 14 shows training curves. The paper uses "hf_trainer_fallback" as a minor technical note implying a framework substitution.

**What verification_state.yaml says:** The note for H-M2 reads: "Mock training (no real Pythia-1B checkpoints)." This is a materially different statement. "Mock training" indicates that the model weights used for the logit margin probe were not produced by genuine 95,368-step gradient descent on the C0-C7 corpora. If the training was mock, then:
- The logit margin values in Table 4 do not reflect a model that learned from the corpus configurations.
- The negative control result |C7−C0|=0.495 does not constitute evidence that "the model trained on C7 produces distinctly different logit margins from C0."
- Contribution C4 ("directional evidence that corpus demographic structure is represented in model logit space") is unsupported.
- The training curves in Figure 14 may be synthetic or from a proxy training run.

**Severity assessment:** If "mock training" means the Pythia-1B was initialized randomly and evaluated without any finetuning (or with stub weights), then all H-M2 results are artifacts of the initialization, not of corpus content. The paper would be claiming a corpus-to-model propagation result from a model that never trained on those corpora. This is a potential data integrity issue.

The ground_truth.yaml assigns LOW-MEDIUM confidence to C4 and flags the hf_trainer_fallback limitation as MEDIUM severity, but does not surface the "mock training" language at the FATAL level. Given the language in verification_state.yaml, the adversarial reviewer must treat this as FATAL-adjacent pending clarification from the pipeline authors.

**Required action:** The paper must clarify the exact training status of the Pythia-1B models used in H-M2. If models were not trained to convergence on each corpus, all H-M2 claims must be removed or completely reframed as "initialization artifacts" rather than "corpus-to-model propagation."

---

## Part 2: Engagement Check (Persona 2)

*[Bored NeurIPS reviewer — paper 3 of 5 today, 7 minutes budget]*

### Bored Reviewer Verdict Table

| Section | Time Budget | Verdict | Notes |
|---------|-------------|---------|-------|
| Abstract | 45 sec | CONTINUE | Hook lands. "22.41%" and "ρ=1.0" are concrete. Would read intro. |
| Introduction (first para) | 30 sec | CONTINUE | "functions as an unintended demographic reweighting mechanism" — strong. |
| Introduction (contributions) | 60 sec | HESITATE | C4 claim intrudes. Logit margins from FAIL_EXPLORE? Why is this a contribution? |
| Figure 1 (monotonic_trend.png) | 10 sec | PASS | Description says monotonically decreasing trend — should be self-explanatory if rendered correctly. Cannot verify without image. |
| Table 2 | 30 sec | FLAG | Values conflict with text if you recompute. C0 < C1 only by 0.0040 in the paper, but abstract claims "22.41%". Takes a moment to track. |
| Results 5.1-5.2 | 60 sec | PASS | Clear, numerically grounded, gate framing helps. |
| Results 5.3 | 45 sec | CONFUSED | "FAIL_EXPLORE" + "directional support" in same paragraph. Contribution C4 still here? |
| Overall engagement | — | BORDERLINE | Would probably accept for review, but C4/H-M2 muddies a clean story. |

### MAJOR Issues - Engagement

#### MAJOR-E1: Contribution C4 Undermines the Abstract's Clean Narrative

**Location:** Abstract (final sentence), Introduction C4, Results 5.3, Conclusion

**Issue:** The abstract ends with: "Our results reframe fastText from a 'quality proxy' to a 'demographic style selector,' and establish that practitioners running standard data curation pipelines are making unintended fairness-relevant decisions with every threshold choice."

This is a strong, accurate summary of the corpus-level findings. The problem is that Contribution C4 — directional model evidence from a FAIL_EXPLORE result — is woven into the abstract, introduction, and conclusion as if it strengthens these claims. It does not. The FAIL_EXPLORE result is a non-significant finding that the paper correctly labels as such, yet it continues to appear in the contributions list and is repeatedly invoked as "directional support."

A busy reviewer sees: (1) strong corpus claim, (2) near-perfect statistics, (3) model result that failed its gate. The third element creates doubt about the first two without adding epistemic value. The paper would be stronger — and the abstract's hook more credible — if C4 were demoted to a "preliminary observation" in the discussion rather than listed as a contribution.

**Required action:** Remove C4 from the formal contributions list in the Introduction. Move H-M2 discussion to a "Preliminary Model Evidence" subsection without contribution framing.

---

## Part 3: Credibility Check (Persona 3)

*[10-year veteran in data curation and fairness in NLP]*

### Novelty Claims Audit

| Claim | Assessment |
|-------|-----------|
| "novel corpus audit methodology" | Partially valid — quantitative H(occ\|demo) sweep over curation configs is not in DCLM/FineWeb/DoReMi. Log-odds auditing has precedent in distributional analysis literature. "Novel" is defensible if scoped correctly. |
| "first audit methodology to quantify [curation-fairness] effect" | Overstatement — prior work on dataset auditing (e.g., Larson et al. 2017 on biases in occupation datasets, Dinan et al. 2020 on controlled generation) measures demographic distributions. Scope to "corpus-level curation hyperparameter sweep" for specificity. |
| "establish that practitioners are making unintended fairness-relevant decisions" | "Establish" is too strong for a ~50k document quick-run single-corpus study. "Demonstrate at quick-run scale" is accurate. |
| "near-perfect statistical regularity (ρ=1.0)" | Technically correct but the paper should note this is computed over 5 ordered points (C1-C5). Spearman ρ=1.0 with n=5 observations requires only strict monotonicity — it does not require perfect linear fit. This should be stated clearly. |

### MAJOR Issues - Credibility

#### MAJOR-C1: "Establishes" Language Disproportionate to Quick-Run PoC Scale

**Location:** Abstract ("establish that practitioners..."), Introduction ("establish..."), Section 6.1 Finding 1 ("establish that fastText quality filtering operates..."), Conclusion ("establish...corpus-level fairness signal")

**Issue:** The word "establish" appears multiple times in the paper to describe what are, by the authors' own admission, quick-run (~50k document) results from a single corpus (DCLM-POOL) using a single demographic lexicon (WinoBias 20 occupations). The paper correctly acknowledges in L3 that "full experiment ongoing." One cannot "establish" a finding that remains in progress.

"Establish" in scientific writing implies robust, replicated, independently verifiable evidence. The findings here are compelling and the effect magnitude is large, but:
- The corpus is a 50k document subset of a 240T token pool.
- The demographic lexicon covers 20 occupations × gender pronouns — a narrow slice of demographic space.
- The corpus is exclusively English (Western-centric).
- A single quality filter (fastText-oh-eli5) is studied.

"Demonstrate at quick-run scale" or "provide strong preliminary evidence" are accurate. "Establish" is not.

**Required action:** Replace all instances of "establish" (in the context of main claims) with "demonstrate" or "provide evidence for." Add a note in the Abstract acknowledging the quick-run scale qualification.

#### MAJOR-C2: Overclaiming on H-M2 Given FAIL_EXPLORE Gate and Mock Training Uncertainty

**Location:** Introduction C4, Section 5.3, Section 6.1 Finding 3, Conclusion

**Issue:** The paper frames H-M2 as providing "directional evidence that corpus demographic structure is represented in model logit space" and lists this as Contribution C4. This framing is problematic on two independent grounds:

1. **Statistical ground:** A FAIL_EXPLORE result (ρ=0.357, p=0.432) does not constitute "directional evidence." p=0.432 means the observed correlation is consistent with pure chance at rate >40%. Calling a non-significant, underpowered result "directional support" is methodologically incorrect. "Directional" typically applies to sign-only interpretation when power is the limiting factor and the effect size estimate is stable — neither of which is demonstrated here (and the sign is contradicted by verification_state.yaml).

2. **Provenance ground:** As detailed in MAJOR-A3, verification_state.yaml describes H-M2 training as "Mock training (no real Pythia-1B checkpoints)." If this is accurate, the logit margin values in Table 4 are not the product of corpus-conditioned training and cannot serve as evidence of anything about corpus-to-model propagation.

**Required action:** Either (a) resolve the mock-training ambiguity and confirm real training occurred, and separately reconcile the rho discrepancy; or (b) remove C4 from the contributions and relegate H-M2 to a methodological appendix as a "planned but inconclusive pilot."

#### MAJOR-C3: ρ=1.0 Presented Without Statistical Context — n=5 Discrete Configurations

**Location:** Abstract, Introduction, Results 5.2, Discussion 6.1, Conclusion

**Issue:** "Spearman ρ=1.0 (p=1.4×10⁻²⁴) across 1800 demographic-occupation pairs" is stated multiple times as if it describes the correlation across 1800 independent observations. In fact, the Spearman correlation is computed across 5 discrete ordered filter levels (C1-C5) where each "observation" is the mean log-odds aggregated over 1800 pairs. The n=5 is the effective degrees of freedom for the rank correlation, not 1800.

The p=1.4×10⁻²⁴ figure appears to be computed using n=1800 (pair-level), not n=5 (configuration-level). If the unit of analysis is "does the mean log-odds increase across filter levels," then with n=5 monotonically ordered values, ρ=1.0 is guaranteed by construction if any monotone trend exists — no statistical test with that sample size produces p≈10⁻²⁴. The p-value cited appears to mix the level of analysis (configuration) with the counting unit (pairs).

This is a statistical methodology concern that a quantitative reviewer will flag. The paper should clarify: "Spearman ρ=1.0 across the 5 filtering configurations (C1-C5), indicating perfect monotonicity; the p-value of 1.4×10⁻²⁴ is computed at the pair level across 1800 (demographic, occupation) pairs pooled across configurations." The current wording is ambiguous and will invite skepticism.

**Note:** This does not invalidate the core finding — the monotonic trend is real and the effect size is large. It is a presentation and statistical reporting issue, but one that will draw fire from a statistically careful reviewer.

---

## Part 4: Human Review Notes

**Typos / Minor Wording Issues (not FATAL/MAJOR):**

1. **Abstract, sentence 3:** "increasing the filtering percentile threshold monotonically reduces conditional demographic-occupation association entropy by 22.41% (from 10th to 90th percentile)" — parenthetical should read "from C1 (10th percentile) to C5 (90th percentile)" for precision; the current wording is ambiguous about whether 10th means ≥10% or the 10th percentile itself.

2. **Section 3.2, Table 1:** "C7 | C3 + shuffled demographics | Negative control" — for a reader encountering Table 1 before Section 3.7, it is unclear why C7 is built on C3 specifically and not C0 or C5. One sentence of motivation ("C3 chosen because it represents the median filter level, allowing the negative control to match the entropy of a mid-range configuration") would prevent reader confusion.

3. **Section 4.2:** "Hardware: NVIDIA H100 NVL, CUDA_VISIBLE_DEVICES=1" — the GPU device ID is pipeline implementation detail, not a reproducibility-relevant parameter for a submitted paper. Remove or move to supplemental.

4. **Section 5.1:** "The large compression concentrates at the C4→C5 threshold (3.1106→2.5374 bits)" — this characterization is based on paper Table 2's incorrect C4 value (3.1106). With the ground-truth value of C4=2.8934, the C3→C4 drop is −0.1687 bits, comparable to the C4→C5 drop of −0.3560 bits. The narrative framing of where compression concentrates must be revisited.

5. **Section 6.2, Limitation L1:** "hf_trainer_fallback" is mentioned as the training limitation. This should be cross-referenced with the mock-training status in verification_state.yaml; as written, L1 underrepresents the severity of the H-M2 limitation.

6. **References:** Paper statistics section notes 2 unverified citations (84.6% verification rate). Before submission, verify all 13 citations, particularly Gebru et al. 2018 (conference vs. journal version) and Biderman et al. 2023 (Pythia ICML).

7. **Section 3.5:** "log-odds(d,o) = log[P(o|d) / (1 − P(o|d))]" — standard notation but should clarify this is the natural log or log base 2 for consistency with the entropy formula (which uses log₂). Using different log bases across H and log-odds is fine but should be stated explicitly.

8. **Section 5.3, Figure references:** Figure 14 (training curves) is cited in Section 4.2 but not discussed in Section 5.3 where H-M2 results are reported. Either discuss what the training curves show (convergence? loss plateau?) or remove the forward reference.

---

## Summary for Revision Agent

### Critical Fixes Required (Block Submission)

**FIX-1 (FATAL-A1): Reconcile Table 2 entropy values.**
Five of seven entropy values in Table 2 do not match ground truth. C0 should be 3.3159, C2 should be 3.1847, C3 should be 3.0621, C4 should be 2.8934, C6 should be 3.0541. Replacing these values changes the narrative about where entropy compression concentrates (C3 and C4 now show meaningful drops, not just C5). All narrative sentences in Section 5.1 about "modest intermediate reductions" and compression "primarily at the ≥90th percentile" must be rewritten.

**FIX-2 (MAJOR-A2): Resolve H-M2 Spearman rho discrepancy.**
Paper reports ρ=0.357 (from h-m2/04_validation.md). verification_state.yaml reports ρ=−0.2143. Identify which value comes from the authoritative experimental run, document the source, and update the paper and gate classification accordingly. If ρ=−0.2143 is correct, all "directional support" and "directional evidence" language for H-M2 must be removed.

**FIX-3 (MAJOR-A3): Clarify H-M2 training provenance ("mock training" vs. real).**
verification_state.yaml states "Mock training (no real Pythia-1B checkpoints)" for H-M2. The paper describes full 95,368-step Pythia-1B training. These descriptions are irreconcilable. If mock training occurred, Contribution C4, Table 4, Figure 11, Figure 14, and all claims about corpus-to-model propagation must be removed. If real training occurred, verification_state.yaml must be corrected and the paper should note the discrepancy was an artifact of a failed pipeline status annotation.

### Important Fixes (High Reviewer Risk)

**FIX-4 (MAJOR-C2): Downgrade Contribution C4 or remove.**
Whether or not the training provenance issue is resolved, a FAIL_EXPLORE result should not appear as a numbered contribution. Demote to Discussion as "preliminary model-level observation requiring full-scale validation."

**FIX-5 (MAJOR-C1): Replace "establishes" with appropriately scoped language throughout.**
Use "demonstrates at quick-run scale" or "provides evidence" in the Abstract, Introduction, and Conclusion.

**FIX-6 (MAJOR-C3): Clarify statistical unit for ρ=1.0.**
Add a sentence in Section 5.2 clarifying that ρ=1.0 is a rank correlation across 5 filter-level configurations, and explain what the p-value unit of analysis is.

**FIX-7 (MAJOR-E1): Restructure Introduction contributions to remove C4 from formal list.**
The Introduction should present C1-C3 as primary contributions and C4 as a "preliminary pilot result."

### Minor Fixes (Style / Robustness)

- Revisit Section 5.1 narrative about compression profile after FIX-1 corrects Table 2 values.
- Add one sentence explaining why C7 uses C3 as base (Table 1).
- Clarify log base in log-odds formula (Section 3.5).
- Remove GPU device ID from Section 4.2.
- Verify 2 unverified citations before submission.

### What Is Solid (Do Not Change)

- H-E1 core findings: −22.41% entropy reduction, ρ=−1.0, Bootstrap CI [−1.154, −0.330]. These are verified and should remain in Abstract and Introduction as the headline result.
- H-M1 log-odds findings: all values verified, ρ=1.0 monotonic result sound (with statistical clarification per FIX-6).
- Related work framing (Section 2): accurate, well-positioned, no overclaiming.
- Limitations section: L1-L4 are honest; L1 may need strengthening per FIX-3.
- Methodology design (Section 3): causal identification framework (C7 negative control, matched capability) is a genuine contribution.
- Conclusions callback structure and future work directions: appropriate scope.
