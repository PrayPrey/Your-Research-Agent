---
title: "Phase 2B Verification Plan: Semantic Entropy UQ Comparison"
hypothesis_id: "H-SemanticEntropyUQ-v1"
confidence_level: 0.78
total_hypothesis_count: 4
phase: "Phase 2B"
generated_at: "2026-05-11"
research_mode: "incremental"
scope_reduction_percentage: 50
causal_chain_count: 3
condition_hypotheses: false
stepsCompleted:
  - "step-00-init-environment"
  - "step-01-init-parsing"
  - "step-02-input-hypothesis"
  - "step-03-hypothesis-generation"
  - "step-04-hypothesis-inventory"
  - "step-05-risk-analysis"
  - "step-06-dependency-graph"
  - "step-07-timeline-planning"
  - "step-08-dialectical-analysis"
  - "step-09-summary"
  - "step-10-finalize"
status: complete
completedAt: "2026-05-11T00:00:00"
---

# Verification Plan: Semantic Entropy Superiority for Hallucination Detection

**Date:** 2026-05-11
**Hypothesis ID:** H-SemanticEntropyUQ-v1
**Confidence:** 0.78
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)
**Research Mode:** Incremental (Phase 2A loaded)
**Scope Reduction:** 50% (3 BUILD_ON claims excluded from verification)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (DO NOT RE-VERIFY)

| ID | Claim | Evidence | Status |
|----|-------|----------|--------|
| EF-1 | Semantic entropy (Kuhn 2023) outperforms token entropy on TriviaQA/NQ | Kuhn et al. 2023 arXiv:2302.09664 | BUILD_ON |
| EF-2 | SelfCheckGPT achieves strong hallucination detection on WikiBio (BERTScore) | Manakul et al. 2023 arXiv:2303.08896 | BUILD_ON |
| EF-3 | HaluEval-QA provides binary hallucination labels for ~10K QA examples | Li et al. 2023 arXiv:2305.11747 | BUILD_ON |

**These claims are accepted as pre-validated. Phase 2B–4 focus exclusively on PROVE_NEW claims.**

### 0.2 PROVE_NEW Claims (Empirical Targets)

| ID | Claim | Target Hypothesis |
|----|-------|------------------|
| PN-1 | No prior work compares all three UQ signal families on HaluEval under matched conditions | H-E1 (existence of gap) |
| PN-2 | Semantic entropy achieves higher AUROC than token entropy on HaluEval-QA (LLaMA-2-7B-chat) | H-M3 (cleaner signal → better AUROC) |
| PN-3 | AUROC ranking order is cross-model stable (LLaMA-2 and Mistral) | H-E1 + H-M3 secondary |

### 0.3 Scope Reduction Summary

- Total claims: 6 | BUILD_ON: 3 | PROVE_NEW: 3
- **Efficiency gain: 50% scope reduction** — 3 claims require no experimental verification
- Remaining target: 3 PROVE_NEW claims → decomposed into 4 sub-hypotheses (H-E1, H-M1, H-M2, H-M3)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under fixed-budget inference conditions on HaluEval-QA (2,000 stratified examples), if three uncertainty quantification signals — token-level entropy (mean aggregation), semantic entropy [Kuhn et al., 2023], and SelfCheckGPT-BERTScore [Manakul et al., 2023] with N=5 stochastic samples — are applied to the same open-source LLM (LLaMA-2-7B-chat and Mistral-7B-Instruct), then semantic entropy will achieve statistically significantly higher AUROC for binary hallucination detection than both token entropy and SelfCheckGPT-BERTScore, because semantic entropy captures uncertainty at the semantic-meaning level by clustering NLI-equivalent responses, filtering the surface-form noise that inflates token entropy's variance and reduces its discriminative power on multi-token factual QA responses.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in AUROC for binary hallucination detection on HaluEval-QA among token-level entropy (mean aggregation), semantic entropy, and SelfCheckGPT-BERTScore (N=5) when applied to the same LLM under matched inference conditions (bootstrap CI, p ≥ 0.05 for all pairwise comparisons).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HaluEval-QA (standard, 2,000 stratified examples) | Binary hallucination labels enable AUROC computation; QA subset has highest label reliability; 2,000 examples provide stable AUROC estimates (SE < 0.02) |
| **Model** | LLaMA-2-7B-chat + Mistral-7B-Instruct-v0.2 | Accessible logits via HuggingFace generate(output_scores=True); both known to hallucinate on factual QA; 7B scale feasible on single A100 |

**Dataset Details:**
- Source: Li et al. (2023) arXiv:2305.11747
- Path: HuggingFace datasets: pminervini/HaluEval or RUCAIBox/HaluEval (QA subset)

**Model Details:**
- Type: Decoder-only causal LM (HuggingFace Transformers)
- Source: meta-llama/Llama-2-7b-chat-hf, mistralai/Mistral-7B-Instruct-v0.2

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Semantic Entropy [Kuhn et al., 2023] | AUROC ~0.78 on TriviaQA | TriviaQA, NQ | Different benchmark; no SelfCheckGPT comparison; single LLM family |
| SelfCheckGPT-BERTScore [Manakul et al., 2023] | AUC-PR ~0.85 on WikiBio | WikiBio, MedQA | Different benchmark+task (biography generation); no entropy comparison |
| Token Entropy (Kadavath 2022 P(True)) | ECE ~0.05 on factual QA | Various (Anthropic proprietary) | Measures calibration not hallucination AUROC; proprietary models |

**Best Baseline Performance:** Semantic entropy AUROC ~0.78 on TriviaQA (serves as primary reference; HaluEval-QA AUROC is the unknown experimental target)

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | Consequence if Violated |
|----|------------|---------------------|------------------------|
| A1 | HaluEval-QA binary labels (ChatGPT-generated) have sufficient quality to discriminate hallucinated from factual responses | Li et al. (2023) report high inter-annotator agreement on QA subset | AUROC values attenuated toward 0.5; comparison remains valid (same noise for all methods) but absolute values cannot generalize |
| A2 | deberta-large-mnli correctly identifies semantic equivalence for short factual QA responses (1–3 sentences) from LLaMA-2 and Mistral | Kuhn et al. (2023) use this NLI model for TriviaQA/NQ responses of similar length | Semantic entropy clustering noisy; advantage over token entropy may vanish or reverse; falsifies Step 2 of causal mechanism |
| A3 | N=5 stochastic samples for SelfCheckGPT provides stable consistency estimates (low variance in AUROC) | Manakul et al. (2023) report stable results with N=5–20; N=5 is lower bound of tested range | SelfCheckGPT AUROC estimates have high variance; bootstrap CIs overlap; cross-method comparisons inconclusive |
| A4 | LLaMA-2-7B-chat and Mistral-7B-Instruct exhibit meaningful uncertainty variation on HaluEval-QA questions | Both models are known to hallucinate on factual QA; HaluEval-QA designed to elicit hallucinations | If models answer all questions confidently, UQ signals do not vary and AUROC ≈ 0.5 for all methods |
| A5 | The AUROC ranking order (semantic entropy ≥ SelfCheckGPT ≥ token entropy) generalizes from LLaMA-2 to Mistral | Cross-model stability is the key high-impact question; assumption: mechanism is model-architecture-independent | Ranking reverses for Mistral → model-dependent finding; limits practical guidance but remains scientifically interesting |

### 1.6 Research Gap & Novelty

**Core Gap:** No prior work compares all three UQ signal families (token entropy, semantic entropy, SelfCheckGPT) on the same LLM under identical experimental conditions. Kuhn (2023) evaluated semantic entropy on TriviaQA/NQ only. Manakul (2023) evaluated SelfCheckGPT on WikiBio only. Both used different models and metrics, making comparison impossible.

**Key Innovation:** First controlled head-to-head comparison eliminating benchmark and model confounds. Additional novelties: (1) all SelfCheckGPT variants on HaluEval, (2) all 3 token entropy aggregations pre-specified, (3) stratification by HaluEval question type (QA/dialogue/summarization), (4) signal efficiency analysis (single-pass vs. N-pass).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

**Note:** H-CP (Comparison) hypotheses are handled exclusively in Phase 5 Baseline Comparison, not Phase 2B.

---

### 2.2 Hypothesis Specifications

---

**H-E1: UQ Signal Performance Gap Exists on HaluEval-QA**

**Type:** EXISTENCE
**Statement:** Under fixed-budget inference conditions, if token-level entropy, semantic entropy, and SelfCheckGPT-BERTScore (N=5) are applied to LLaMA-2-7B-chat on the 2,000-example stratified HaluEval-QA sample, then semantic entropy will achieve statistically significantly higher AUROC (≥ 0.05 difference, non-overlapping 95% bootstrap CIs) than at least one baseline UQ method, because a discrimination gap between UQ methods must exist for the comparative hypothesis to be meaningful.

**Rationale:**
This existence hypothesis establishes that differential UQ performance is detectable on HaluEval-QA — a prerequisite for all mechanism hypotheses. Without this gap, the remaining causal chain cannot be validated. Phase 2A (SH1) identifies this as the foundational empirical claim that bridges Kuhn 2023's TriviaQA findings to HaluEval-QA.

**Variables:**
- Independent: UQ Signal Type (token_entropy_mean, semantic_entropy, selfcheckgpt_bertscore_n5) × LLM (LLaMA-2-7B-chat)
- Dependent: AUROC for binary hallucination detection on HaluEval-QA (bootstrap 95% CI, N=1000)
- Controlled: Inference parameters (temp=0 greedy + temp=1.0 stochastic), dataset sample (fixed 2,000 stratified), NLI model (deberta-large-mnli), N=5 SelfCheckGPT samples

**Verification Protocol:**
1. Load HaluEval-QA QA subset; stratified sample 2,000 examples (balanced hallucination/factual labels by question type).
2. Generate LLaMA-2-7B-chat responses: 1 greedy pass (temp=0) for token entropy + 5 stochastic samples (temp=1.0) for SelfCheckGPT; save all logits and samples.
3. Compute token_entropy_mean, semantic_entropy (lorenzkuhn/semantic_uncertainty + deberta-large-mnli), and selfcheckgpt_bertscore_n5 (potsawee/selfcheckgpt).
4. Compute AUROC per method vs. HaluEval binary labels; bootstrap 1,000 resamples for 95% CI; apply Bonferroni correction for 3 pairwise comparisons.
5. Report all AUROC values with CIs; confirm gap ≥ 0.05 with non-overlapping CIs for at least the top vs. bottom ranked methods.

**Success Criteria:**
- Primary: At least one pairwise AUROC difference ≥ 0.05 with non-overlapping 95% bootstrap CIs (p < 0.05 after Bonferroni correction)
- Secondary: Semantic entropy AUROC > token_entropy_mean AUROC (directional confirmation of P1)

**Failure Response:**
- IF fails: EXPLORE — investigate whether HaluEval label quality (A1) or model uncertainty collapse (A4) explain null result; document as bounds on benchmark utility

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Prediction P1 (primary), Established Fact PN-1

---

**H-M1: Token Entropy Conflates Surface-Form and Semantic Uncertainty**

**Type:** MECHANISM (Causal Step 1)
**Statement:** Under fixed-budget inference conditions on HaluEval-QA, if token-level entropy (mean aggregation) and semantic entropy are computed on the same LLaMA-2-7B-chat responses, then their Pearson correlation will be significantly below 1.0 (r < 0.9 across all 2,000 examples), because LLM token probability distributions simultaneously encode surface-form variation (word choice, phrasing) and semantic variation (factual uncertainty), and these two sources contribute differentially to total token entropy on factual QA tasks where lexical diversity is high.

**Rationale:**
This hypothesis tests the first causal step: that token entropy and semantic entropy diverge because they capture different variance sources. If r > 0.9, token entropy and semantic entropy are essentially measuring the same thing, invalidating the mechanism explanation for semantic entropy's claimed superiority. The correlation threshold (r < 0.9) is a necessary (not sufficient) condition for the mechanism to hold.

**Variables:**
- Independent: UQ Signal Type (token_entropy_mean vs. semantic_entropy) computed on identical responses
- Dependent: Pearson correlation r between token_entropy_mean and semantic_entropy scores across 2,000 examples; distribution of score divergence by example
- Controlled: Same LLM (LLaMA-2-7B-chat), same 2,000-example sample, same NLI model (deberta-large-mnli)

**Verification Protocol:**
1. Use the 2,000-example responses and logits generated in H-E1 (no additional generation needed).
2. Compute token_entropy_mean and semantic_entropy for each of the 2,000 examples.
3. Compute Pearson r between the two score vectors; compute Spearman ρ as robustness check.
4. Identify examples with largest divergence (|token_entropy - semantic_entropy| > 1 SD); analyze their lexical diversity (type-token ratio of 5 stochastic samples).
5. Report r, ρ, and divergence distribution; confirm r < 0.9 as evidence of surface/semantic conflation.

**Success Criteria:**
- Primary: Pearson r < 0.9 between token_entropy_mean and semantic_entropy score vectors (p < 0.05, bootstrap CI)
- Secondary: High-divergence examples show high lexical diversity (many distinct surface forms with same factual answer)

**Failure Response:**
- IF r ≥ 0.9: PIVOT — document that surface-form filtering is not the mechanism; explore whether semantic entropy advantage arises from a different source (e.g., cluster entropy regularization)

**Dependencies:** H-E1 (existence of performance gap)

**Source:** Phase 2A Causal Step 1, Key Tension (NLI quality), Assumption A2

---

**H-M2: NLI Clustering Successfully Filters Surface-Form Noise in HaluEval-QA Responses**

**Type:** MECHANISM (Causal Step 2)
**Statement:** Under fixed-budget inference conditions on HaluEval-QA, if deberta-large-mnli NLI clustering is applied to the 5 stochastic samples per example from LLaMA-2-7B-chat, then the semantic cluster count distribution will show meaningful aggregation (fewer clusters than samples for at least 50% of examples), because NLI-equivalent responses to the same factual question share semantic meaning despite surface variation, and deberta-large-mnli accurately identifies this equivalence for short factual QA responses.

**Rationale:**
This hypothesis tests the second causal step: that NLI clustering actually produces distinct, non-trivial semantic groupings on HaluEval-QA. If clustering produces singleton clusters for most examples (all 5 samples semantically distinct), semantic entropy collapses to token diversity and the filtering advantage disappears. This is the key assumption A2 test and addresses the falsifier for Causal Step 2.

**Variables:**
- Independent: NLI clustering applied (deberta-large-mnli on 5 stochastic samples per example)
- Dependent: Semantic cluster count per example (1–5 clusters); fraction of examples with cluster_count < N=5 (aggregation rate); correlation between cluster_count and hallucination label
- Controlled: Same LLM (LLaMA-2-7B-chat), same 2,000-example sample, NLI model fixed to official lorenzkuhn/semantic_uncertainty implementation

**Verification Protocol:**
1. Use the 5 stochastic samples per example from H-E1 generation.
2. Apply lorenzkuhn/semantic_uncertainty NLI clustering to obtain semantic cluster assignments and cluster counts per example.
3. Compute: (a) mean cluster count across 2,000 examples; (b) fraction with cluster_count < 5 (aggregation rate); (c) fraction with cluster_count = 1 (full collapse rate).
4. Compute correlation between cluster_count and HaluEval binary label (hallucinated=1, factual=0); test if lower cluster count correlates with factual responses (interpretability check).
5. Stratify by question type (QA/dialogue/summarization); report aggregation rate per type.

**Success Criteria:**
- Primary: Aggregation rate ≥ 50% (majority of examples have cluster_count < 5, confirming semantic grouping occurs)
- Secondary: Full collapse rate < 20% (singleton-only clustering is not dominant); correlation between cluster_count and hallucination label ≥ 0.1

**Failure Response:**
- IF aggregation rate < 50%: PIVOT — deberta-large-mnli may not generalize to HaluEval-QA response styles; explore alternative NLI models or threshold tuning; document as A2 violation

**Dependencies:** H-M1 (confirmation that surface/semantic conflation exists and is worth filtering)

**Source:** Phase 2A Causal Step 2, Assumption A2 (deberta-large-mnli generalization), Key Tension

---

**H-M3: Semantic Signal Produces Higher AUROC Discrimination on HaluEval-QA**

**Type:** MECHANISM (Causal Step 3)
**Statement:** Under fixed-budget inference conditions on HaluEval-QA (2,000 stratified examples), if semantic entropy is compared to token_entropy_mean and selfcheckgpt_bertscore_n5 on both LLaMA-2-7B-chat and Mistral-7B-Instruct, then semantic entropy will achieve the highest AUROC for binary hallucination detection on both models (≥ 0.05 advantage over token_entropy_mean with non-overlapping 95% bootstrap CIs), and the AUROC ranking order (semantic entropy ≥ SelfCheckGPT ≥ token entropy) will be preserved across both LLMs (Spearman ρ ≥ 0.8), because the cleaner semantic uncertainty signal produced by NLI clustering provides better discrimination between hallucinated (high uncertainty) and factual (low uncertainty) responses than surface-contaminated token entropy or the computationally expensive multi-pass SelfCheckGPT approach.

**Rationale:**
This is the core empirical hypothesis of the entire study — the third causal step where mechanism translates to measurable performance. It tests both the absolute performance claim (P1: semantic entropy wins) and the cross-model stability claim (P3: ranking preserved across LLMs). Success here validates the complete causal chain from Steps 1–3. This is a MUST_WORK gate because failure would negate the study's primary contribution.

**Variables:**
- Independent: UQ Signal Type (7 levels: all 3 token entropy variants, semantic entropy, 3 SelfCheckGPT variants) × LLM (LLaMA-2-7B-chat, Mistral-7B-Instruct)
- Dependent (primary): AUROC for binary hallucination detection; pairwise AUROC differences with bootstrap 95% CI; Spearman ρ of method rankings across LLMs
- Controlled: Fixed 2,000-example stratified sample, inference parameters, NLI model, N=5 SelfCheckGPT budget

**Verification Protocol:**
1. Replicate full pipeline on Mistral-7B-Instruct: greedy generation + 5 stochastic samples → all 7 UQ signals computed using same implementations.
2. Compute AUROC for all 7 UQ signals vs. HaluEval-QA labels for each LLM independently; bootstrap 1,000 resamples; apply Bonferroni correction (3 primary pairwise comparisons per LLM).
3. Report pairwise AUROC differences (semantic_entropy − token_entropy_mean, semantic_entropy − selfcheckgpt_bertscore_n5) with 95% CI for each LLM.
4. Compute Spearman ρ of method AUROC rankings across the two LLMs; test H3: ρ ≥ 0.8.
5. Stratify AUROC results by HaluEval question type (QA/dialogue/summarization); report best UQ signal per question type per LLM.

**Success Criteria:**
- Primary (P1): AUROC(semantic_entropy) > AUROC(token_entropy_mean) by ≥ 0.05 with non-overlapping 95% CIs for both LLMs independently (both directions required)
- Secondary (P2): AUROC(token_entropy_mean) ≤ AUROC(selfcheckgpt_bertscore_n5) ≤ AUROC(semantic_entropy) OR SelfCheckGPT not significantly different from semantic entropy (both > token entropy)
- Tertiary (P3): Spearman ρ ≥ 0.8 for method AUROC rankings across LLaMA-2-7B-chat and Mistral-7B-Instruct

**Failure Response:**
- IF primary fails (semantic_entropy ≤ token_entropy_mean for either LLM): EXPLORE — diagnose whether A2 (NLI quality) or A1 (label noise) explains null; the negative result (token entropy sufficient) is itself a publishable cost-saving finding
- IF P3 fails (ρ < 0.8 or ranking reverses for Mistral): SCOPE — document as model-dependent finding; limit claims to LLaMA-2; explore Mistral-specific factors

**Dependencies:** H-M2 (NLI clustering confirmed to work on HaluEval-QA)

**Source:** Phase 2A Causal Step 3, Predictions P1/P2/P3, Phase 2B SH3

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥1 pairwise AUROC gap ≥ 0.05 (non-overlapping CIs) | STOP — reassess if HaluEval useful for UQ comparison |
| H-M1 | MUST_WORK | Pearson r < 0.9 between token entropy and semantic entropy | PIVOT — mechanism explanation invalid; explore alternative |
| H-M2 | SHOULD_WORK | Aggregation rate ≥ 50% (NLI clustering effective) | PIVOT — deberta-large-mnli generalization fails; try alternatives |
| H-M3 | MUST_WORK | P1 confirmed for both LLMs + Spearman ρ ≥ 0.8 | EXPLORE/SCOPE — diagnose; negative result still publishable |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |
| **Total** | 4 hypotheses | **5 weeks** |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): HaluEval Label Noise**
- **Description:** ChatGPT-generated binary labels may have insufficient quality to discriminate hallucinated from factual responses, attenuating all AUROC values toward 0.5.
- **Severity:** High | **Likelihood:** Medium
- **Affected Hypotheses:** H-E1 (existence), H-M3 (primary performance claim)
- **Mitigation:**
  1. Prevention: Focus on QA subset (highest reliability of 3 HaluEval tasks per Li et al. 2023)
  2. Detection: Check if all AUROC values are ≤ 0.6; bootstrap CI widths indicate signal clarity
  3. Response: If all AUROC ≈ 0.5, document as HaluEval limitation; report as secondary finding (all UQ methods perform poorly on noisy-label benchmarks); SCOPE reduction to publishable noise analysis
- **Early Warning:** AUROC < 0.6 for ALL methods on LLaMA-2

**Risk R2 (from A2): NLI Model Generalization Failure**
- **Description:** deberta-large-mnli may not correctly identify semantic equivalence for HaluEval-QA response styles (shorter, more factual than WikiBio biographies), causing noisy clustering that erases semantic entropy's advantage.
- **Severity:** High | **Likelihood:** Medium
- **Affected Hypotheses:** H-M2 (NLI clustering), H-M3 (AUROC performance)
- **Mitigation:**
  1. Prevention: Use official lorenzkuhn/semantic_uncertainty implementation (validated on similar-length TriviaQA/NQ responses)
  2. Detection: H-M2 aggregation rate < 50% = early warning signal
  3. Response (PIVOT): Try alternative NLI models (e.g., facebook/bart-large-mnli); try lower similarity thresholds; document NLI sensitivity as a research finding
- **Early Warning:** H-M2 aggregation rate < 30%; singleton cluster rate > 60%

**Risk R3 (from A3): SelfCheckGPT Sample Instability**
- **Description:** N=5 stochastic samples may provide unstable consistency estimates for SelfCheckGPT, resulting in high AUROC variance and inconclusive pairwise comparisons.
- **Severity:** Medium | **Likelihood:** Low
- **Affected Hypotheses:** H-M3 (comparison with SelfCheckGPT)
- **Mitigation:**
  1. Prevention: Bootstrap 1,000 resamples for stable CI estimates; Bonferroni correction prevents false positives
  2. Detection: Bootstrap CI width > 0.1 for SelfCheckGPT AUROC = instability indicator
  3. Response: If N=5 too noisy, increase to N=10 for SelfCheckGPT (additional compute); report N sensitivity
- **Early Warning:** SelfCheckGPT bootstrap CI width > 0.1

**Risk R4 (from A4): Model Uncertainty Collapse**
- **Description:** LLaMA-2-7B-chat or Mistral-7B-Instruct may answer HaluEval-QA questions with uniformly high or low confidence, causing UQ signals to not vary across examples.
- **Severity:** Medium | **Likelihood:** Low
- **Affected Hypotheses:** H-E1 (existence of gap), H-M3 (cross-model performance)
- **Mitigation:**
  1. Prevention: Verify both models hallucinate on HaluEval-QA (expected given benchmark design)
  2. Detection: Compute entropy variance across examples; low variance (< 0.1 SD) = warning signal
  3. Response: If one model shows collapse, drop it from analysis; focus on the functional model; document as scope limitation
- **Early Warning:** Mean entropy for all examples within 1 SD of maximum

**Risk R5 (from A5): Cross-Model Ranking Instability**
- **Description:** The AUROC ranking order observed for LLaMA-2-7B-chat may not hold for Mistral-7B-Instruct, producing a model-dependent rather than universal finding.
- **Severity:** Medium | **Likelihood:** Medium
- **Affected Hypotheses:** H-M3 (P3 cross-model stability test)
- **Mitigation:**
  1. Prevention: Pre-specify P3 threshold (Spearman ρ ≥ 0.8) to avoid post-hoc interpretation
  2. Detection: Compute rankings for each LLM independently before comparing
  3. Response: If ρ < 0.8, this IS the result — reframe as "model-dependent UQ signal performance" which is equally valuable as practitioner guidance; do NOT abort
- **Early Warning:** LLaMA-2 and Mistral AUROC vectors differ by > 0.1 for any single method

### 4.2 Risk-Hypothesis Mapping Table

| Risk | Source | Affected Hypotheses | Severity | Priority |
|------|--------|---------------------|----------|----------|
| R1: HaluEval label noise | A1 | H-E1, H-M3 | High | 1 |
| R2: NLI generalization failure | A2 | H-M2, H-M3 | High | 2 |
| R3: SelfCheckGPT sample instability | A3 | H-M3 | Medium | 4 |
| R4: Model uncertainty collapse | A4 | H-E1, H-M3 | Medium | 3 |
| R5: Cross-model ranking instability | A5 | H-M3 | Medium | 5 |

**Risk Summary:** 0 Critical | 2 High | 3 Medium | 0 Low

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Derived Risk | Mitigation |
|---------------------|-------------|------------|
| Kuhn 2023: Only TriviaQA/NQ, different LLM family | Benchmark transfer failure (R2 related) | Fixed by design: HaluEval-QA is the common ground benchmark |
| Manakul 2023: Only WikiBio, only SelfCheckGPT variants | No entropy comparison baseline | Fixed by design: all three UQ families evaluated together |
| Kadavath 2022: Calibration metric (ECE), not AUROC | Metric incompatibility | Fixed by design: AUROC is the unified metric for all methods |

---

## 5. Execution Plan

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: UQ Signal Performance Gap Exists on HaluEval-QA
    (Existence - no prerequisites)
         │
         ▼ [Gate 1: MUST_WORK — ≥0.05 AUROC gap detected]
         │
[Level 1 - Mechanism Step 1]
    H-M1: Token Entropy Conflates Surface/Semantic Uncertainty
    (Mechanism - prerequisite: H-E1)
         │
         ▼ [Gate 2: MUST_WORK — Pearson r < 0.9]
         │
[Level 2 - Mechanism Step 2]
    H-M2: NLI Clustering Filters Surface-Form Noise
    (Mechanism - prerequisite: H-M1)
         │
         ▼ [Gate 3: SHOULD_WORK — Aggregation rate ≥ 50%]
         │
[Level 3 - Mechanism Step 3]
    H-M3: Cleaner Signal → Higher AUROC Discrimination
    (Mechanism - prerequisite: H-M2)
         │
         ▼ [Gate 4: MUST_WORK — P1+P3 confirmed on both LLMs]
         │
   [VERIFICATION COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels | All sequential
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Status |
|-------|-----------|---------------|-----------|--------|
| 0 | H-E1 | None | MUST_WORK | READY |
| 1 | H-M1 | H-E1 | MUST_WORK | NOT_STARTED |
| 2 | H-M2 | H-M1 | SHOULD_WORK | NOT_STARTED |
| 3 | H-M3 | H-M2 | MUST_WORK | NOT_STARTED |

### 5.3 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (5 Weeks Total)
═══════════════════════════════════════════════════════════════════

Phase/Hypothesis  │ W1      │ W2      │ W3      │ W4      │ W5
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1           │ ████████│ ████████│         │         │
  [Gate 1]       │         │        ◆│         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Core Mechanisms
  H-M1           │         │         │ ████████│         │
  H-M2           │         │         │         │ ████    │
  H-M3           │         │         │         │     ████│ ████
  [Gate 2/3/4]   │         │         │        ◆│        ◆│        ◆
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

**Note on H-E1 duration (2 weeks):** H-E1 requires generating responses for 2,000 examples × 2 models × 6 forward passes (1 greedy + 5 stochastic) and computing all UQ signals — the most compute-intensive step. H-M1 and H-M2 reuse H-E1 data (no additional generation). H-M3 requires Mistral inference (additional compute ~equivalent to H-E1 LLaMA portion).

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  - H-E1 (Foundation): 2 weeks (data generation + all signal computation)
  - H-M1 (Correlation analysis): 1 week (reuses H-E1 data)
  - H-M2 (Clustering analysis): 1 week (reuses H-E1 stochastic samples)
  - H-M3 (Full comparison + Mistral): 1 week (Mistral inference + final stats)

Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) = 5 weeks

Slack Available: 0 weeks (all sequential, strictly dependent)

Key Efficiency Note: H-M1 and H-M2 are analysis-only steps reusing H-E1
generated data. Actual compute burden is front-loaded in H-E1 and H-M3.

Gate Decision Points:
- Gate 1 (Week 2): H-E1 MUST_WORK — proceed or stop
- Gate 2 (Week 3): H-M1 MUST_WORK — confirm mechanism or pivot
- Gate 3 (Week 4): H-M2 SHOULD_WORK — confirm NLI or note limitation
- Gate 4 (Week 5): H-M3 MUST_WORK — confirm performance + cross-model
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (none required)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Core Mechanisms (H-M1 → H-M2 → H-M3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain (strict dependency order)

Compute Requirements:
- LLaMA-2-7B-chat: 2,000 examples × 6 passes = ~12,000 inference calls
- Mistral-7B-Instruct: 2,000 examples × 6 passes = ~12,000 inference calls
- Estimated total GPU time: < 48 hours on single A100 (80GB)
- All implementations: pip-installable (lorenzkuhn/semantic_uncertainty,
  potsawee/selfcheckgpt, HuggingFace Transformers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1–2
  → Setup: Download HaluEval-QA, LLaMA-2-7B-chat, Mistral-7B-Instruct, NLI model
  → Generate: LLaMA-2 responses (greedy + stochastic) for all 2,000 examples; save logits
  → Compute: token_entropy_mean/first/logprob, semantic_entropy, selfcheckgpt_bertscore/nli/ngram (N=5)
  → Evaluate: AUROC per method vs. HaluEval labels; bootstrap CIs; pairwise comparisons

Step 2: Evaluate Gate 1 (End of Week 2)
  → IF H-E1 PASS: AUROC gap ≥ 0.05 exists → proceed to H-M1
  → IF H-E1 FAIL: Gap not detected → investigate label noise (R1) or uncertainty collapse (R4) → STOP

Step 3: Execute H-M1 (Mechanism Step 1) — Week 3
  → Reuse: LLaMA-2 token entropy and semantic entropy scores from H-E1 (no new generation)
  → Compute: Pearson r and Spearman ρ between token_entropy_mean and semantic_entropy vectors
  → Analyze: High-divergence examples; lexical diversity check

Step 4: Evaluate Gate 2 (End of Week 3)
  → IF H-M1 PASS: r < 0.9 confirmed → mechanism holds → proceed to H-M2
  → IF H-M1 FAIL: r ≥ 0.9 → surface/semantic conflation not the mechanism → PIVOT explanation

Step 5: Execute H-M2 (Mechanism Step 2) — Week 4
  → Reuse: 5 stochastic samples per example from H-E1 (no new generation)
  → Apply: lorenzkuhn/semantic_uncertainty NLI clustering; compute cluster counts
  → Analyze: Aggregation rate, collapse rate, correlation with hallucination labels

Step 6: Evaluate Gate 3 (End of Week 4)
  → IF H-M2 PASS: Aggregation rate ≥ 50% → NLI filtering confirmed → proceed to H-M3
  → IF H-M2 FAIL: Rate < 50% → PIVOT (try alternative NLI models); document as A2 violation

Step 7: Execute H-M3 (Mechanism Step 3 + Cross-Model) — Week 5
  → Generate: Mistral-7B-Instruct responses (greedy + stochastic) for all 2,000 examples
  → Compute: All 7 UQ signals for Mistral; full AUROC comparison for both LLMs
  → Evaluate: P1 (AUROC gap for both LLMs), P2 (SelfCheckGPT intermediate), P3 (Spearman ρ)
  → Stratify: AUROC by question type (QA/dialogue/summarization)

Step 8: Evaluate Gate 4 (End of Week 5)
  → IF H-M3 PASS: P1 + P3 confirmed → proceed to Phase 4.5 synthesis → Phase 6 paper
  → IF P1 partial: One LLM fails → SCOPE (LLM-specific findings) → document
  → IF P3 fails: Model-dependent ranking → reframe as practitioner guidance finding
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Semantic entropy achieves statistically significantly higher AUROC
for binary hallucination detection on HaluEval-QA than token-level entropy and
SelfCheckGPT-BERTScore (N=5), because NLI clustering filters surface-form noise
from token distributions, producing a cleaner semantic uncertainty signal.

Supporting Evidence:
1. Causal Step 1 (EF-1): Kuhn et al. (2023) demonstrate semantic > token entropy
   on TriviaQA/NQ — mechanism established on similar task type
2. Causal Step 2 (A2): deberta-large-mnli NLI clustering validated on short
   factual QA responses of similar length in Kuhn 2023 implementation
3. Causal Step 3 (P1): Mechanism predicts ≥ 0.05 AUROC advantage; threshold
   pre-registered to prevent post-hoc inflation

Strengths:
- Mechanism-grounded with 3-step falsifiable causal chain
- All predictions quantified with pre-specified statistical thresholds
- All implementations public and validated in prior literature
- 50% scope reduction — 3 BUILD_ON claims already established

Expected Outcomes:
- Primary (P1): AUROC(semantic) > AUROC(token_mean) by ≥ 0.05 for both LLMs
- Secondary (P2): AUROC(SelfCheckGPT) intermediate between token and semantic
- Tertiary (P3): Spearman ρ ≥ 0.8 cross-model AUROC ranking stability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no statistically significant difference in AUROC
for binary hallucination detection among the three UQ signal families on
HaluEval-QA (all pairwise bootstrap 95% CIs overlap; p ≥ 0.05 after Bonferroni).

Counter-Arguments:
1. HaluEval label noise (R1): ChatGPT-generated labels introduce systematic noise
   that attenuates all AUROC values toward 0.5, making all methods appear equivalent
2. NLI generalization failure (R2): deberta-large-mnli trained on NLI datasets may
   not generalize to HaluEval-QA's specific QA response style and length distribution
3. Scope limitation: Prior evidence for semantic entropy's advantage is benchmark-
   specific (TriviaQA/NQ); mechanism may not transfer to HaluEval-QA question types

Potential Failure Points:
- R1 (label noise): All AUROC ≈ 0.5; no method discriminates → H0 supported by floor effect
- R2 (NLI failure): Singleton clustering → semantic entropy degenerates to token diversity
- R4 (uncertainty collapse): Models too confident or too uncertain → no signal variance

Conditions Under Which H0 Would Be Supported:
- If AUROC difference < 0.05 for all pairwise comparisons with overlapping CIs (P1 falsified)
- If NLI clustering produces singleton clusters for > 80% of examples (R2 + H-M2 fails)
- If Pearson r ≥ 0.9 between token and semantic entropy (H-M1 fails → mechanism absent)
- If label noise so severe that all AUROC values ≤ 0.6 (R1 → benchmark invalidity)

Equally Valuable Null Results (Prof. Rex's framing):
- "Token entropy achieves equivalent AUROC to semantic entropy" → major cost-saving finding
  (simpler single-pass method with no NLI overhead achieves same discrimination)
- "All UQ methods perform similarly on HaluEval-QA" → benchmark invalidity discovery
  → guides community toward better hallucination detection benchmarks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-SemanticEntropyUQ-v1 presents a well-mechanized, theoretically
grounded claim that semantic entropy's NLI filtering advantage translates from
TriviaQA/NQ to HaluEval-QA. However, H0 raises valid concerns: the mechanism
depends critically on NLI model generalization (A2) and HaluEval label quality
(A1), both of which are untested on this specific benchmark.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Empirically establishes that a UQ performance
   gap EXISTS on HaluEval-QA before attributing it to any mechanism
2. Sequential mechanism testing (H-M1 → H-M2): Isolates the specific mechanism
   (surface/semantic conflation + NLI filtering) with independent falsifiability
3. Gate conditions: Allow early detection of H0 support at each stage without
   requiring full pipeline execution if early gates fail
4. Positive null framing: Pre-specified interpretations for null results ensure
   scientific value regardless of direction

Conditions for Thesis Support:
- H-E1 PASS: Gap ≥ 0.05 confirmed on HaluEval-QA
- H-M1 PASS: r < 0.9 confirms surface/semantic conflation
- H-M2 PASS: Aggregation rate ≥ 50% confirms NLI filtering works
- H-M3 PASS: P1 + P3 confirmed → semantic entropy universally recommended

Conditions for Antithesis Support:
- H-E1 FAIL: No performance gap → H0 supported; HaluEval-QA too noisy to discriminate
- H-M1 FAIL: r ≥ 0.9 → methods measure same construct; semantic clustering redundant
- H-M3 P1 FAIL: Token entropy ≥ semantic entropy → simpler method preferred

Nuanced Outcome Possibilities:
1. Full Support: All 4 hypotheses pass → Semantic entropy universally recommended for
   hallucination detection deployments with 7B-class models on HaluEval-style tasks
2. Partial Support: H-E1/H-M3 pass but P3 fails → Model-specific guidance (LLaMA-2 only)
3. Method Equivalence: H-E1 passes but semantic ≈ SelfCheckGPT → compute-efficiency finding
4. No Support: H-E1 fails → Token entropy sufficient; semantic entropy adds no value;
   major cost-saving result for practitioners

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | UQ performance gap exists on HaluEval-QA | Label noise attenuates all signals | H-E1: Empirical AUROC gap test (≥0.05 threshold) |
| Mechanism | NLI filtering cleanly isolates semantic uncertainty | deberta-large-mnli may fail on short QA responses | H-M1+H-M2: Direct correlation + clustering analysis |
| Signal Efficiency | Semantic entropy achieves this in single pass vs. N-pass SelfCheckGPT | N=5 may be too few for stable SelfCheckGPT estimates | H-M3: Bootstrap CI widths diagnose variance |
| Cross-Model Scope | Mechanism is model-architecture-independent | Instruction-tuning differences (LLaMA-2 chat vs. Mistral instruct) affect token distributions | H-M3: P3 Spearman ρ test; null = model-specific finding |
| Benchmark Validity | HaluEval-QA labels reliable enough for AUROC | ChatGPT-generated labels introduce systematic bias | A1 mitigation: QA subset focus; question-type stratification |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.78 (matches Phase 2A Phase 2B readiness: READY)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SemanticEntropyUQ-v1 (Confidence: 0.78)
- Claim: Semantic entropy achieves highest AUROC for hallucination detection on HaluEval-QA vs. token entropy and SelfCheckGPT-BERTScore (N=5)

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 50% scope reduction applied)
- Sub-Hypotheses: 4 total — H-E1 (Existence), H-M1–H-M3 (Mechanism Steps 1–3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 4 decision points (Gates 1–4)

**Risk Assessment:** Medium-High
- Primary concerns: R1 (HaluEval label noise), R2 (NLI generalization)
- Both addressed via detection criteria and PIVOT strategies

**Immediate Action:** Begin Phase 1 with H-E1 — set up HaluEval-QA + LLaMA-2-7B-chat inference pipeline, compute all 7 UQ signals on 2,000-example stratified sample

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases planned with full scientific rigor
- H0 explicitly addressed: all null result scenarios have pre-specified interpretations
- Scope reduction: 3 BUILD_ON claims excluded from verification (50% efficiency gain)
- All implementations available and pip-installable; < 48 hours GPU time required

**Verification Execution Order:**

**Phase 1: Foundation (2 weeks)**
- H-E1: Establish that semantic UQ performance gap exists on HaluEval-QA
- Gate 1: MUST PASS — if no gap detected, stop and diagnose R1/R4

**Phase 2: Core Mechanisms (3 weeks)**
- H-M1: Confirm token entropy conflates surface/semantic variance (r < 0.9)
- H-M2: Confirm NLI clustering effectively filters noise on HaluEval-QA responses
- H-M3: Confirm semantic entropy achieves highest AUROC on both LLMs; cross-model stability
- Gate 2: H-M1 MUST PASS — mechanism broken → PIVOT on explanation
- Gate 3: H-M2 SHOULD PASS — NLI failure → pivot to alternative NLI
- Gate 4: H-M3 MUST PASS — primary empirical contribution confirmed

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP: No UQ performance gap on HaluEval-QA; investigate R1 (label noise) or R4 (uncertainty collapse)
   - PASS → Continue to H-M1

2. **Gate 2 (Mechanism Step 1):** H-M1 must pass
   - CRITICAL FAIL (r ≥ 0.9) → PIVOT: Surface/semantic conflation not the mechanism; explore alternative explanations for semantic entropy advantage
   - PASS → Continue to H-M2

3. **Gate 3 (Mechanism Step 2):** H-M2 should pass
   - FAIL (aggregation rate < 50%) → PIVOT: Try alternative NLI models; document as A2 scope limitation; continue to H-M3 with caveat
   - PASS → NLI filtering confirmed; proceed to H-M3

4. **Gate 4 (Core Result):** H-M3 must pass
   - P1 FAIL for one LLM → SCOPE: Limit claims to single LLM; model-specific finding
   - P3 FAIL (ρ < 0.8) → REFRAME: Model-dependent guidance; equally valuable practitioner finding
   - FULL PASS → Proceed to Phase 4.5 synthesis → Phase 6 paper writing

**Open Questions (from Phase 2A):**
- Does deberta-large-mnli generalize to HaluEval-QA response styles (shorter, more factual than WikiBio)?
- Is N=5 SelfCheckGPT sampling sufficient for stable AUROC on HaluEval-QA, or does variance require N=10–20?
- Does the AUROC advantage of semantic entropy hold for Mistral (instruction-tuned) as well as LLaMA-2-chat?
- What is the practical compute cost ratio: single-pass entropy vs. N=5 SelfCheckGPT on 7B models?

**Recommendations:**

1. **Immediate Actions:**
   - Set `CUDA_VISIBLE_DEVICES=<empty_gpu>` before launching any inference
   - Clone and install: lorenzkuhn/semantic_uncertainty, potsawee/selfcheckgpt, HuggingFace Transformers
   - Pre-download: meta-llama/Llama-2-7b-chat-hf, mistralai/Mistral-7B-Instruct-v0.2, microsoft/deberta-large-mnli
   - Stratified sample 2,000 HaluEval-QA examples; save sample indices for reproducibility

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve extra compute buffer: H-M2 NLI pivot (alternative NLI models) or H-M3 SelfCheckGPT N=10 fallback
   - Pre-register analysis choices (token entropy aggregation strategy, Bonferroni correction) before executing H-E1

3. **Failure Management:**
   - Document ALL gate outcomes (pass/fail/partial) regardless of direction
   - H0 support = equally publishable as H1 support — do not discard null results
   - If H-E1 fails: submit as "Benchmark Validity Analysis of HaluEval-QA for UQ Comparison"

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `docs/youra_research/20260510_question/03_refinement.yaml` (Schema v10.0.0)
- Hypothesis ID: H-SemanticEntropyUQ-v1 | Discussion: 8 exchanges, 6 personas | Convergence: All criteria met
- Related: `02_synthesis.yaml` (measurement plan), `01_round_table/final_opinions.yaml` (per-agent assessments)

**Appendix B: MCP Tool Usage Summary**
- MCP Status: Unavailable in TEST_question_2 no-mcp configuration
- Scientific method reasoning applied natively (LLM-inline)
- All hypothesis generation, risk analysis, dialectical analysis performed via LLM reasoning
- In production pipelines: mcp__clearThought__scientificmethod (1–3x), mcp__clearThought__collaborativereasoning (1x)

**Appendix C: Implementation Resources**
- Semantic entropy: `lorenzkuhn/semantic_uncertainty` (GitHub, pip)
- SelfCheckGPT: `potsawee/selfcheckgpt` (pip: `pip install selfcheckgpt`)
- NLI model: `microsoft/deberta-large-mnli` (HuggingFace)
- Dataset: `pip install datasets; load_dataset("pminervini/HaluEval", "qa_samples")`

---

*Generated by YouRA Phase 2B Planning | 2026-05-11 | UNATTENDED mode | Incremental (Phase 2A loaded)*
