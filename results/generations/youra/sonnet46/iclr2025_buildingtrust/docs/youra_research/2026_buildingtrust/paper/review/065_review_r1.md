# Adversarial Review - Round 1

**Paper:** Alignment Changes Answers, Not Just Confidence: Mechanistic Discrimination of RLHF Miscalibration
**Reviewed:** 2026-03-15T08:00:00Z
**Reviewer Version:** Adversary Agent v2.0

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 3 | NEEDS_WORK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 3 | NEEDS_WORK |
| **TOTAL** | **0** | **7** | NEEDS_WORK |

**Recommendation:** MAJOR_REVISION

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|-------------|-------------|--------|
| 1.4B-PPO Spearman ρ | −0.324 | −0.324 | YES |
| 1.4B-DPO Spearman ρ | 0.447 | 0.447 | YES |
| 6.9B-DPO Spearman ρ | 0.875 | 0.875 | YES |
| 1.4B-PPO argmax redistribution | 99.7% (44/14,042) | 99.7% (44/14,042) | YES |
| ΔReliability 1.4B-DPO | 0.1048 | 0.1048 | YES |
| ΔReliability 1.4B-PPO | 0.0406 | 0.0406 | YES |
| ECE_base 1.4B | 0.0849 | 0.0849 | YES |
| ECE_base 2.8B | 0.0597 | 0.0597 | YES |
| ECE_base 6.9B | 0.0792 | 0.0792 | YES |
| H3 ratios (SFT/DPO/PPO) | 0.32 / 0.26 / 0.73 | 0.32 / 0.26 / 0.73 | YES |
| Phase 5 baseline comparison | Not claimed | NOT_STARTED (skipped) | YES (correct omission) |
| 8/9 pairs ΔReliability > 0 | Claimed | Confirmed (EC7) | YES |

All core numerical claims match ground truth. No FATAL accuracy errors found.

### MAJOR Accuracy Issues

**ACC-MAJOR-001: Table 2 conflates ΔECE with ΔBrier Reliability**

Table 2 presents ΔECE and ΔReliability in separate columns, yet the values listed are identical for every row (e.g., Pythia-1.4B DPO: ΔECE = +0.1048, ΔReliability = +0.1048). These are not the same quantity. ECE (Expected Calibration Error, 15-bin) and Brier Reliability (the overconfidence component of Murphy's Brier decomposition) have different formulas, different scales, and different sensitivity to resolution changes. The paper's Section 3.4 describes them as distinct metrics. A reviewer checking the Brier decomposition will immediately notice this — either the paper is presenting two identical numbers for different metrics (a methodology error), or the column labeling is wrong (a presentation error). Either way, this undermines the claim that "Brier decomposition enables clean attribution." This needs correction: either show distinct ΔECE and ΔReliability values computed from the correct formulas, or rename one column.

Evidence: Table 2 rows: Pythia-1.4B DPO ΔECE = +0.1048, ΔReliability = +0.1048; Pythia-2.8B DPO ΔECE = +0.0437, ΔReliability = +0.0437; etc.

**ACC-MAJOR-002: Table 2 is incomplete — SFT rows are entirely missing**

The paper evaluates SFT for all three model sizes (H-E1 validation, verification_state.yaml records SFT delta metrics: delta_sft_1.4b = 0.133409, delta_sft_2.8b = 0.011046, delta_sft_6.9b = 0.026653 for margin; SFT ΔReliability values from H-E1 data exist). Table 2 omits SFT rows for all three sizes, leaving 3 of 9 alignment–size pairs undocumented in the primary results table. Table 3 (Spearman ρ summary) includes SFT rows, creating an internal inconsistency: Table 3 is complete but Table 2 is not. A reviewer will notice that SFT is discussed as one of three alignment methods throughout but disappears from the primary quantitative summary.

Severity: MAJOR — incomplete reporting of primary experimental results.

**ACC-MAJOR-003: The pre-registered ordering prediction is misrepresented in Section 5.2**

Section 5.2 states: "The pre-registered ordering prediction (PPO ≥ DPO > SFT, based on reward optimization pressure) is empirically reversed: DPO produces larger calibration degradation than PPO in all three model sizes."

However, reviewing the main hypothesis statement in verification_state.yaml (H-AlignCalib-v1), the stated prediction is: "the Brier reliability component of Expected Calibration Error will increase monotonically in the same order (PPO >= DPO > SFT)." This is a pre-registered directional prediction that the paper correctly identifies as falsified. The problem is the framing: the paper presents this as merely a "counter-intuitive" finding and contribution rather than explicitly acknowledging it as a pre-registered prediction that was falsified. The pre-registration framework is central to the paper's credibility claims — any pre-registered prediction that failed should be clearly labeled as such (falsified), not softened to "empirically reversed." The paper does acknowledge the DPO ≥ PPO result in Limitations (Section 6.1) but does not explicitly state "our pre-registered calibration ordering prediction was falsified."

This is not a data accuracy error but is an accuracy-of-representation error that touches methodological integrity.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | YES | 99.7% argmax redistribution is genuinely striking; ρ = −0.324 is immediately interpretable |
| Introduction hook? | YES | Opens with a concrete, vivid description; mechanism triangle (H1/H2/H3) is clear within 2 minutes |
| Problem clarity? | YES | The "temperature scaling targets the wrong mechanism" framing is crisp and motivating |
| Novelty clear in 2 minutes? | YES | Pre-registered H1/H2/H3 discrimination as a framework is a clean novel contribution |
| Figure 1 self-explanatory? | PARTIAL | Figure 1 (delta_reliability_bar.png) is described adequately in caption; however, SFT bars are absent from Table 2, which is the companion table — inconsistency will frustrate the reviewer who looks at both |
| Results meaningful? | YES | 8/9 pairs, 99.7% redistribution, ρ = −0.324 are all substantial effect sizes |
| Comparison fair? | PARTIAL | See Credibility section — baselines are within-family paired, which is appropriate, but aligned model checkpoint provenance (fallback vs. primary) reduces confidence in the DPO > PPO ordering |
| Attention loss point? | Table 2 | A reviewer scanning Table 2 will immediately notice it has only 7 rows for 9 pairs, misses SFT entirely, and has identical ΔECE / ΔReliability columns — this will trigger credibility concerns at a critical moment |

**At what point does attention drop?** Section 5.1, specifically Table 2. The incomplete table and the ΔECE = ΔReliability coincidence will raise doubts about the rigor of the Brier decomposition claim before the reader reaches the mechanism discrimination results. This is unfortunate because the mechanism results (Section 5.3, Table 3) are the paper's strongest contribution and are well-presented.

### MAJOR Engagement Issues

**ENG-MAJOR-001: Table 2 failure at the critical first-results moment**

Table 2 is the first quantitative results table. It is missing the SFT rows (3 of 9 pairs) and shows identical ΔECE and ΔReliability values for all rows. A bored reviewer scanning this table in the first pass will either (a) think the SFT results are being suppressed, or (b) assume the analysis pipeline did not actually compute a proper Brier decomposition. Either interpretation undermines engagement at precisely the moment when the paper needs to build confidence for the subsequent mechanistic claims. Fix: Complete Table 2 with all 9 rows and verify that ΔECE and ΔBrier Reliability are distinct computed values.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Verdict | Issue |
|-------|---------|-------|
| "First pre-registered mechanistic discrimination" between H1/H2/H3 | LIKELY VALID but unverifiable from paper | The paper does not cite any prior work that explicitly pre-registered H1/H2/H3 mechanism discrimination in calibration. However, the "first" claim is not verifiable from the paper alone — a reviewer familiar with the calibration literature may know of similar pre-registration efforts. The paper qualifies it as "in this setting" which helps, but the claim remains bold. |
| "Definitively refutes" H1 | OVERCLAIM | 0/9 is strong evidence, but "definitively" implies cross-family generality that the paper explicitly limits to Pythia 1.4B–6.9B. Section 6.4 (Limitations) acknowledges single-family restriction. The word "definitively" is inconsistent with the paper's own Limitation 2. |
| "Definitively excluded" H3 | OVERCLAIM | Same issue — "definitively" is not warranted for a single model family on two benchmarks. |
| "Alignment changes answers, not just confidence" in title | PROPORTIONATE | This is a precise, accurate description of H2 dominance. Appropriate. |

### Baseline Fairness Audit

| Dimension | Assessment |
|-----------|-----------|
| Within-family paired baseline | FAIR — using base model as comparison for same-size aligned model is the correct causal design |
| Checkpoint provenance (Risk R1) | ADEQUATELY DISCLOSED in Section 3.2 and 6.4 — fallback checkpoints are acknowledged, and the paper appropriately hedges the DPO ≥ PPO ordering claim |
| Primary checkpoints (RLHFlow) not used | This is the central baseline fairness concern — the paper cannot rule out that the DPO > PPO ordering is an artifact of different training data/duration in the fallback checkpoints rather than a genuine algorithmic property. The paper acknowledges this in Limitation 1 but still calls it a "contribution" in the abstract. |
| MMLU 4-shot vs TruthfulQA 0-shot comparison | MINOR CONCERN — comparing ΔECE across benchmarks with different shot settings is a potential confound for the H3 diagnostic. If 4-shot MMLU shows more calibration degradation than 0-shot TruthfulQA, part of the ratio could reflect shot-count effects rather than purely framing effects. This is not discussed. |

### MAJOR Credibility Issues

**CRED-MAJOR-001: "Definitively" language is not warranted for single-family, 1.4B–6.9B study**

The abstract states "H1 is definitively refuted" and "H3 is excluded by cross-benchmark diagnostic." The Discussion opens with "H2 boundary restructuring is the dominant mechanism." These claims are used with very strong language throughout despite the paper's own Limitation 2 explicitly stating: "Whether H2 dominates in LLaMA-2, Mistral, or Falcon is an open empirical question." The word "definitively" cannot coexist with this limitation. A skeptical expert reviewer will flag this inconsistency immediately.

Fix: Replace "definitively refuted" with "refuted in Pythia 1.4B–6.9B" and replace "definitively excluded" with "excluded in the softmax-ECE MMLU/TruthfulQA setting." The mechanism discrimination is strong within its scope; the language just needs to match the scope.

**CRED-MAJOR-002: DPO ≥ PPO ordering presented as contribution despite checkpoint non-equivalence**

Contribution 2 in the Introduction claims: "We find that DPO produces larger calibration degradation than PPO — ΔReliability_DPO > ΔReliability_PPO in all three Pythia sizes." This is listed as a contribution in the Abstract and Introduction. However, Section 3.2 acknowledges "the DPO ≥ PPO ordering should be interpreted as a checkpoint-level observation pending replication with matched checkpoints."

A contribution that requires immediate hedging in the same paper is not a validated contribution — it is a provisional observation. Presenting it as a contribution (rather than as an interesting secondary finding requiring replication) in the abstract and introduction misrepresents the strength of evidence. The fallback checkpoints may have been trained with different data amounts, learning rates, or reward models for DPO vs. PPO, which could fully explain the ordering difference.

Fix: Downgrade DPO ≥ PPO from "contribution" to "exploratory secondary finding" in the Abstract and Introduction, with the replication caveat moved earlier (from Section 3.2 to the abstract/intro where the claim is first made).

**CRED-MAJOR-003: The pre-softmax margin analysis (H-M2) is confounded with the Spearman ρ analysis (H-M3) but presented as independent evidence**

Section 5.2 presents "Pre-softmax logit margin inflation (H-M2)" as independent confirmation that "the confidence increase is encoded at the pre-softmax level." However, H-M2 and H-M3 are measuring the same logit vectors — the margin analysis (max − second_max log-prob) and the Spearman ρ analysis both operate on the same 4-option log-probability vectors extracted from lm-eval. They are not independent measurements from different data; they are two statistics computed from the same per-item vectors. Presenting them as cross-validating evidence ("Key observation 3: ... confirming that the confidence increase is encoded at the pre-softmax level") overstates independence. A skeptical reviewer will note that both effects being present in the same data does not constitute independent replication.

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Abstract | "All 9 Spearman rank correlations... fall below ρ = 0.90; 8/9 fall below 0.85" — correct, but two sentences later says "8 of 9 Spearman ρ values fall below 0.85" (referring to EC2) — EC2's exception (6.9B-DPO ρ = 0.875) should be named in abstract for precision | CLARITY |
| Section 3.6, Table (Hypothesis Gate) | H-M3 gate criterion listed as "Spearman ρ ≥ 0.90 for all 9 pairs (H1 confirmation)" — this is the SHOULD_WORK gate that FAILED. The table presents it without flagging that this gate FAILED, which may confuse readers who use tables as quick summaries | CLARITY |
| Section 5.1 | "Figure 1 shows ΔBrier Reliability across all 9 alignment–size pairs with bootstrap 95% CIs" — Figure 1 file is figures/delta_reliability_bar.png; actual existence of this file is unverifiable from the manuscript. If figure files were not generated, this is a broken reference | TECHNICAL |
| Section 4.3, Baselines | "The theoretical reward optimization pressure gradient is SFT < DPO < PPO" — this is a contested characterization. DPO's effective reward optimization pressure depends on the KL divergence, which is not independently measured. This should be qualified as "conventional characterization" | PRECISION |
| Section 4.2 | "We do not include HellaSwag in primary analysis" — the main hypothesis statement in verification_state.yaml included HellaSwag as a planned benchmark. This exclusion is justified but should explicitly reference the pre-registration modification | COMPLETENESS |
| Section 5.1, Figure 2 caption | "Resolution changes moderately — confirming overconfidence, not discriminability collapse" — if ΔECE = ΔReliability as shown in Table 2, Resolution changes were apparently not computed. Caption implies Brier decomposition was computed but Table 2 does not show it | CONSISTENCY |
| Section 3.5 | "For each MMLU item, we compute the Spearman rank correlation between the base model's 4-option log-probability vector" — Spearman ρ on a 4-element vector has very low power (n=4 per item). Mean ρ across 14,042 items is used, but this should be noted — per-item ρ is noisy for n=4 | METHODOLOGY NOTE |
| Section 6.2 | "ATS may partially succeed in this direction because hidden-state temperatures can be learned to undo token-level redistribution patterns, but this remains untested (H-M4, not executed)" — sentence should end at "untested" rather than speculating about ATS mechanism after acknowledging it is untested | OVERCLAIMING MINOR |
| Table 3, footnote | The ~approximation symbols on argmax changed rates (e.g., ~38.8%, ~55.3%) indicate these are estimated. The source of these estimates should be noted — are they derived from Spearman ρ analytically or from actual per-item argmax computation? 99.7% is exact (44/14,042 stated), but the others are approximate | PRECISION |
| Section 7, closing | "what has it learned to prefer, and can we correct it?" — engaging ending; the narrative blueprint shows the intended closing was "what has it learned to prefer, and why?" The current version substitutes "why" with "and can we correct it" — both work, this is stylistic | STYLE |

---

## Summary for Revision Agent

### Priority Fix List

**MAJOR Issues (ordered by impact):**

1. **ACC-MAJOR-001 + ENG-MAJOR-001** (linked): Fix Table 2 — add missing SFT rows for all 3 sizes; verify that ΔECE and ΔBrier Reliability are separately computed values. If they are identical, the Brier decomposition claim needs to be reconsidered or the methodology re-executed. This is the single most damaging issue.

2. **CRED-MAJOR-001**: Replace "definitively" with scoped language throughout Abstract, Introduction, and Results. Specifically: "definitively refuted" → "refuted in Pythia 1.4B–6.9B"; "definitively excluded" → "excluded in the softmax-ECE evaluation setting."

3. **CRED-MAJOR-002**: Downgrade the DPO ≥ PPO ordering from abstract/introduction "contribution" status to "exploratory finding pending matched-checkpoint replication." Move the checkpoint caveat from Section 3.2 to the first mention in the Abstract or Introduction.

4. **ACC-MAJOR-003**: In Section 5.2, explicitly state that the DPO ≥ PPO > SFT ordering is a falsification of the pre-registered calibration ordering prediction (PPO ≥ DPO > SFT). The paper acknowledges this is counter-intuitive but does not clearly label it as a pre-registered prediction failure.

5. **CRED-MAJOR-003**: Clarify in Section 5.2 that H-M2 (margin analysis) and H-M3 (Spearman ρ) are computed from the same log-probability vectors and are therefore correlated, not independent, evidence streams. Remove language claiming they "independently confirm" each other.

### Key Concerns

- The Brier decomposition (Table 2 showing ΔECE = ΔReliability) is the most technically suspicious element. If the decomposition was not properly computed, it undermines the methodological claim that ECE attribution via Brier components was the approach.
- The DPO ≥ PPO ordering, while interesting, rests on non-matched checkpoints. Its elevation to a named contribution creates credibility risk that outweighs the benefit.
- "Definitively" language used three times in a single-family study with acknowledged generalization limitations will draw reviewer fire.

### What's Working

- The core H2 mechanism finding is strong: 0/9 above H1 threshold, 8/9 below H2 threshold, 1.4B-PPO ρ = −0.324 with 99.7% argmax redistribution. This is a clean, internally consistent, numerically precise result that matches ground truth exactly.
- The pre-registered H1/H2/H3 discrimination framework is genuinely novel in this space and well-operationalized.
- The H3 exclusion via TruthfulQA diagnostic is a clean negative result that the paper handles honestly.
- The limitations section (Section 6.4) is honest and complete, covering all known limitations in the ground truth file.
- Abstract and Introduction are compelling — the opening hook and problem framing will engage reviewers in the first 2 minutes.
- The "Phase 5 baseline comparison was skipped" situation is handled correctly — the paper makes no claims about baseline comparison performance, consistent with verification_state.yaml showing this was explicitly skipped.
