---
title: "Verification Plan: Semantic Mode Consistency (SMC) as Black-Box Hallucination Predictor"
hypothesis_id: "H-SMC-v1"
date: "2026-08-31"
status: in_progress
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
completedAt: "2026-08-31T00:00:00Z"
research_mode: incremental
total_hypothesis_count: 4
---

# Verification Plan: Semantic Mode Consistency (SMC) as Black-Box Hallucination Predictor

**Date:** 2026-08-31
**Hypothesis ID:** H-SMC-v1
**Confidence:** 0.78
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do NOT Re-Verify)

| Claim | Evidence | Status |
|-------|----------|--------|
| Sampling-based NLI consistency correlates with factual accuracy on TriviaQA and NQ | Kuhn et al. 2023 (Semantic Uncertainty); Manakul et al. 2023 (SelfCheckGPT) | BUILD_ON |
| SelfCheckGPT NLI consistency detects hallucination in black-box open-ended generation | Manakul et al. 2023 on WikiBio/GPT-3 | BUILD_ON |
| AUROC is a valid metric for binary hallucination prediction | Xiong et al. 2023, Lin et al. 2024 | BUILD_ON |

### 0.2 PROVE_NEW Claims (Require Hypothesis Generation)

| Claim | Gap |
|-------|-----|
| No controlled comparison of sampling-based consistency vs. token-probability baselines across TriviaQA + NQ + HaluEval + TruthfulQA exists | Literature covers ≤2 benchmarks per paper with inconsistent baselines |
| DeBERTa-v3-large NLI scorer is OOD for very short factual answers | Identified concern — requires empirical validation via parallel SMC-Embed |

### 0.3 Scope Reduction

- **Total claims:** 5
- **BUILD_ON (skip):** 3
- **PROVE_NEW (verify):** 2
- **Scope reduction:** 50%
- **Phase 2B-4 instruction:** Build on established SelfCheckGPT/Semantic Uncertainty methodology. Main experimental contribution is multi-benchmark comparison. Do not re-prove that sampling-based consistency works in principle.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under factual question-answering with black-box LLMs (no logit access), if we compute NLI-based Semantic Mode Consistency (SMC) across N=10 stochastic samples per question using a local DeBERTa-v3-large NLI scorer, then this consistency score will serve as a reliable hallucination predictor (AUROC ≥ 0.70) across all four existing factual QA benchmarks (TriviaQA, NaturalQuestions, HaluEval, and TruthfulQA), because factually grounded answers produce semantically convergent sample distributions while hallucinated answers exhibit semantic divergence, reflecting the model's internal uncertainty manifesting as multimodal semantic output.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in hallucination prediction AUROC between NLI-based Semantic Mode Consistency (N=10 samples) and verbalized confidence baseline across TriviaQA, NaturalQuestions, HaluEval, and TruthfulQA. Equivalently: SMC AUROC < 0.65 on ≥ 2 of 4 benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HaluEval (primary) + TriviaQA + NaturalQuestions + TruthfulQA (standard) | HaluEval has balanced binary hallucination labels (50/50) making it ideal as primary benchmark. TriviaQA/NQ provide open-domain factual QA with verifiable ground truth. TruthfulQA provides adversarial hard case. All four cover the spectrum from easy to hard for SMC signal. |
| **Model** | Llama-3-8B-Instruct | Fully local (no API cost), supports sampling with temperature control, achieves ~60-70% factual accuracy on TriviaQA (both hallucination and correct regimes populated) |

**Dataset Details:**
- Source: HuggingFace datasets hub
- Path:
  - HaluEval: datasets: HaluEval/halueval_qa_samples.json (public)
  - TriviaQA: datasets: trivia_qa (HuggingFace)
  - NaturalQuestions: datasets: natural_questions (HuggingFace)
  - TruthfulQA: github: sylinrl/TruthfulQA (MC format)

**Model Details:**
- Type: decoder-only autoregressive LLM
- Source: HuggingFace: meta-llama/Meta-Llama-3-8B-Instruct

**Additional Components:**
- NLI Scorer: cross-encoder/nli-deberta-v3-large (primary consistency metric, SMC-NLI)
- Embedding Model: sentence-transformers/all-mpnet-base-v2 (secondary, SMC-Embed — robustness check for NLI OOD concern)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Insufficiency |
|--------|-------------|---------|---------------|
| SelfCheckGPT-NLI | AUROC ~0.65-0.75 (estimated) | WikiBio only (open-ended biographical generation) | Single model (GPT-3), no factual QA benchmarks |
| Semantic Uncertainty | AUROC ~0.75-0.80 | TriviaQA, NaturalQuestions | Requires token log-probabilities (not black-box); no HaluEval or TruthfulQA |
| Verbalized confidence | AUROC ~0.55-0.65 (estimated) | Various | Known poorly calibrated; weak black-box baseline |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Hallucinated LLM outputs are semantically diverse across stochastic samples | Manakul et al. 2023; Kuhn et al. 2023. TruthfulQA may violate (confident consistent wrong answers) | SMC AUROC low for TruthfulQA specifically; main study predicts this as hardest case |
| A2 | DeBERTa-v3-large NLI scorer provides meaningful signal for short factual QA answer pairs | Used in SelfCheckGPT for sentence-level consistency | SMC-NLI scores uninformative; SMC-Embed serves as fallback |
| A3 | 1000 questions per benchmark sufficient for reliable AUROC estimation | Standard sample size in NLP evaluation; TriviaQA/NQ/HaluEval have thousands available | Wide AUROC CIs; may need to increase to 2000+ |
| A4 | Temperature=0.7 produces sufficient semantic diversity without excessive noise | SelfCheckGPT used similar range; Wang et al. 2022 used 0.7 | Temperature sensitivity analysis can be added as supplementary |
| A5 | Llama-3-8B-Instruct is suitable representative model (~60-70% factual accuracy) | Estimated from benchmark reports | If near-perfect or near-random, use subset with balanced correct/incorrect |

### 1.6 Research Gap & Novelty

**Gap:** No controlled comparison of sampling-based consistency vs. token-probability baselines exists across TriviaQA + NQ + HaluEval + TruthfulQA simultaneously under identical controlled conditions. Each existing paper covers ≤2 benchmarks with different baselines.

**Novelty:**
- First systematic multi-benchmark evaluation of sampling-based NLI consistency as hallucination predictor across all four factual QA benchmarks under identical controlled conditions
- SMC framing: characterizes LLM output distribution as unimodal (factual) vs. multimodal (hallucinating)
- N-efficiency analysis on factual QA (not done before)
- Dual NLI+embedding consistency comparison: first empirical assessment of which is more reliable for short factual QA
- AUROC ordering prediction converts TruthfulQA failure mode into falsifiable claim

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: SMC Signal Existence — Meaningful Consistency Variation Across Questions**

**Statement**: Under factual QA with black-box Llama-3-8B-Instruct at temperature=0.7, if we compute SMC-NLI (fraction of entailment/neutral pairs among N=10 sample pairs) for 1000 HaluEval questions, then the SMC-NLI score distribution will show meaningful variation across questions (not uniformly high or low), enabling AUROC > 0.60 on HaluEval binary hallucination labels, because correct answers concentrate samples while hallucinated answers spread them.

**Rationale:**
This is the foundational existence check: before testing AUROC across all benchmarks, we must confirm that SMC produces a discriminative signal at all. HaluEval's balanced binary labels (50/50) make it the cleanest environment for this check. Failure here means the NLI scorer is OOD and SMC-Embed must be used as primary metric.

**Variables:**
- Independent: SMC-NLI score per question (fraction of 45 NLI-consistent pairs)
- Dependent: AUROC for binary hallucination classification on HaluEval
- Controlled: Llama-3-8B-Instruct, temperature=0.7, DeBERTa-v3-large NLI, N=10, 1000 HaluEval questions

**Verification Protocol:**
1. Sample N=10 responses per question for 1000 HaluEval QA pairs from Llama-3-8B-Instruct at temperature=0.7.
2. Compute all C(10,2)=45 pairwise NLI labels using DeBERTa-v3-large; compute SMC-NLI = (entailment + neutral) / 45.
3. Compute SMC-Embed as mean pairwise cosine similarity using all-mpnet-base-v2 (parallel robustness check).
4. Compute AUROC for SMC-NLI and SMC-Embed against HaluEval binary labels; bootstrap 95% CIs.
5. Check variance of SMC-NLI distribution: std > 0.05 indicates meaningful variation.

**Success Criteria (PoC):**
- Primary: SMC-NLI AUROC > 0.60 on HaluEval (existence confirmed)
- Secondary: SMC-NLI distribution std > 0.05 (not degenerate)

**Failure Response:**
- IF SMC-NLI AUROC < 0.60 but SMC-Embed AUROC > 0.60: NLI is OOD, switch to SMC-Embed as primary metric; continue to H-M1 with SMC-Embed.
- IF both < 0.60: PIVOT — reassess whether 1000 HaluEval questions, sampling temperature, or model choice is the issue. STOP main experiment.

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 (sh1_existence), Section 1.3 (causal steps 1-3)

---

---
**H-M1: Causal Step 1 — Factual Certainty Produces Concentrated Semantic Distribution**

**Statement**: Under factual QA with Llama-3-8B-Instruct on TriviaQA (1000 questions), if we separate correctly answered questions from hallucinated ones using exact-match/F1≥0.5 labels, then questions answered correctly will show significantly lower inter-sample NLI contradiction rates (higher SMC-NLI scores) than incorrectly answered questions, because strong parametric knowledge concentrates the conditional distribution over a narrow semantic cluster.

**Rationale:**
This tests the first causal step directly: does factual certainty manifest as concentrated samples? This is the mechanism that makes SMC meaningful. It must hold on TriviaQA (open-domain factual QA with verifiable answers) for the hypothesis to have a valid mechanistic foundation beyond an empirical observation.

**Variables:**
- Independent: Ground truth label (correct vs. hallucinated, binary, from exact-match/F1 scoring)
- Dependent: SMC-NLI score per question (continuous, 0–1)
- Controlled: Llama-3-8B-Instruct, temperature=0.7, N=10, DeBERTa-v3-large, TriviaQA 1000 questions

**Verification Protocol:**
1. Run N=10 sampling for 1000 TriviaQA questions; compute SMC-NLI scores.
2. Label each question as correct (F1 ≥ 0.5 with gold answer) or hallucinated (F1 < 0.5).
3. Compare mean SMC-NLI(correct) vs. mean SMC-NLI(hallucinated) using Wilcoxon rank-sum test.
4. Compute effect size (Cohen's d) and 95% CI on score difference.
5. Check: if mean(SMC-NLI|correct) > mean(SMC-NLI|hallucinated) with p < 0.05, causal step 1 is supported.

**Success Criteria (PoC):**
- Primary: mean(SMC-NLI|correct) > mean(SMC-NLI|hallucinated), p < 0.05 (Wilcoxon)
- Secondary: Cohen's d > 0.3 (small-to-medium effect)

**Failure Response:**
- IF p ≥ 0.05 (no discrimination): Causal step 1 falsified. H-M2 and H-M3 blocked. PIVOT: investigate whether temperature is too low (model not exploring) or too high (too much noise). May need temperature ablation before proceeding.
- IF effect direction reversed (hallucinated > correct): Fundamental mechanism failure. STOP. Route to Phase 0.

**Dependencies:** H-E1 (existence check must pass first)

**Source:** Phase 2A Section 1.3 Step 1

---

---
**H-M2: Causal Step 2 — Hallucination Produces Multimodal Semantic Distribution**

**Statement**: Under factual QA with Llama-3-8B-Instruct on TriviaQA and NaturalQuestions (1000 questions each), if we examine hallucinated questions (F1 < 0.5), then their inter-sample NLI contradiction rates will be significantly higher than for correctly answered questions, because lack of factual grounding causes sampling to spread across multiple incompatible semantic clusters, except for adversarially consistent wrong answers (TruthfulQA key tension).

**Rationale:**
This tests the complementary second causal step: hallucination = semantic diversity. The key_tension from Phase 2A is that TruthfulQA's adversarial design may produce confident, consistent wrong answers — this step explicitly tests whether the mechanism holds on TriviaQA/NQ where this tension is less pronounced. Failure here with high NLI-contradiction on correct answers would indicate noise from temperature.

**Variables:**
- Independent: Ground truth label (correct vs. hallucinated)
- Dependent: Fraction of NLI-contradiction pairs per question (inverse of SMC-NLI; continuous 0–1)
- Controlled: Llama-3-8B-Instruct, temperature=0.7, N=10, DeBERTa-v3-large, TriviaQA + NQ 1000 each

**Verification Protocol:**
1. Reuse N=10 samples from H-M1 (TriviaQA); collect new samples for NQ (1000 questions).
2. Compute NLI-contradiction fraction = (contradiction pairs) / 45 for each question.
3. Compare contradiction fraction: hallucinated vs. correct on TriviaQA, then on NQ.
4. Bootstrap 95% CI on mean contradiction fraction for both groups.
5. Verify ordering: mean(contradiction|hallucinated) > mean(contradiction|correct) on both datasets.

**Success Criteria (PoC):**
- Primary: mean(NLI-contradiction|hallucinated) > mean(NLI-contradiction|correct) on TriviaQA, p < 0.05
- Secondary: Same ordering holds on NQ with p < 0.05

**Failure Response:**
- IF TriviaQA fails but NQ holds: Document as dataset-specific limitation; proceed with NQ data.
- IF both fail: Core mechanism step 2 invalid for these benchmarks. PIVOT to SMC-Embed. If SMC-Embed also fails: STOP, route to Phase 0.

**Dependencies:** H-M1 (directional signal must exist before testing multimodality)

**Source:** Phase 2A Section 1.3 Step 2

---

---
**H-M3: Causal Step 3 — NLI Pairwise Agreement → Discriminative SMC Score Across All Benchmarks**

**Statement**: Under factual QA with Llama-3-8B-Instruct across all four benchmarks (TriviaQA, NQ, HaluEval, TruthfulQA; 1000 questions each), if we compute SMC-NLI = (entailment + neutral pairs) / 45 for N=10 samples, then SMC-NLI will achieve AUROC ≥ 0.70 on TriviaQA, NQ, and HaluEval, with TruthfulQA predicted to be the hardest case (potentially below 0.70), because the NLI pairwise agreement score operationalizes the factual certainty signal from H-M1/H-M2 into a scalar that discriminates hallucinated from correct answers.

**Rationale:**
This is the primary hypothesis test (P1). H-M1 and H-M2 established the directional mechanism; this step tests whether the NLI operationalization is discriminative enough to achieve the AUROC ≥ 0.70 threshold across all benchmarks. The key novel element is simultaneous evaluation under identical controlled conditions. TruthfulQA's adversarial design (confident consistent wrong answers) is predicted to suppress SMC signal — this is a testable prediction (P2) rather than a confound.

**Variables:**
- Independent: Benchmark (TriviaQA / NQ / HaluEval / TruthfulQA-MC) × Method (SMC-NLI / SMC-Embed / Verbalized confidence / SelfCheckGPT-NLI)
- Dependent: AUROC for binary hallucination classification (primary), AUPRC (secondary)
- Controlled: Llama-3-8B-Instruct, temperature=0.7, N=10, DeBERTa-v3-large, 1000 questions/benchmark

**Verification Protocol:**
1. Collect N=10 samples for all 4000 questions (4 benchmarks × 1000); compute SMC-NLI, SMC-Embed, verbalized confidence, SelfCheckGPT-NLI replication.
2. Compute AUROC and AUPRC for each method × benchmark combination (3 × 4 = 12 AUROC values).
3. Bootstrap 95% CIs for all AUROC values (1000 bootstrap samples).
4. Test AUROC ordering prediction: HaluEval > TriviaQA ≈ NQ > TruthfulQA (non-overlapping CIs for HaluEval > TruthfulQA).
5. Run one-sided Wilcoxon test: SMC-NLI vs. verbalized confidence per benchmark.

**Success Criteria (PoC):**
- Primary (P1): SMC-NLI AUROC ≥ 0.70 on TriviaQA, NQ, HaluEval (3 of 4; TruthfulQA allowed below threshold per key_tension prediction)
- Secondary (P2): AUROC(HaluEval) > AUROC(TruthfulQA) with non-overlapping 95% CIs
- Falsification: AUROC < 0.65 on ≥ 2 benchmarks OR < 0.60 on any single benchmark

**Failure Response:**
- IF AUROC < 0.65 on 2 benchmarks but SMC-Embed ≥ 0.65: NLI OOD confirmed; switch to SMC-Embed as primary metric; revise main claim accordingly.
- IF both metrics fail on ≥ 2 benchmarks: Main hypothesis rejected. Document as partial result. Route to Phase 0 for hypothesis revision.

**Dependencies:** H-M2 (mechanism must be validated before claiming discrimination)

**Source:** Phase 2A Section 1.3 Step 3, Section 1.6 Predictions P1-P2

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SMC-NLI or SMC-Embed AUROC > 0.60 on HaluEval | STOP main experiment; reassess NLI scorer / temperature |
| H-M1 | MUST_WORK | mean(SMC-NLI\|correct) > mean(SMC-NLI\|hallucinated), p < 0.05 | PIVOT temperature ablation; if both metrics fail STOP → Phase 0 |
| H-M2 | SHOULD_WORK | mean(contradiction\|hallucinated) > mean(contradiction\|correct) on TriviaQA | Document limitation; proceed if NQ holds |
| H-M3 | SHOULD_WORK | SMC-NLI AUROC ≥ 0.70 on TriviaQA, NQ, HaluEval | If NLI fails but Embed holds: revise claim; if both fail ≥ 2 benchmarks: Phase 0 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (1 wk H-M1, 1 wk H-M2, 1 wk H-M3) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Consistent Hallucination Risk (from A1)**

**Source Assumption:** A1 — Hallucinated outputs are semantically diverse across stochastic samples.

**Description:** TruthfulQA is specifically designed to elicit confident, consistent wrong answers. If Llama-3-8B-Instruct consistently hallucinates the same wrong answer across N=10 samples (high SMC-NLI despite being wrong), the consistency score will fail to discriminate on TruthfulQA.

**Affected Hypotheses:** H-E1 (partially), H-M2, H-M3

**Severity:** Medium (predicted and incorporated into P2 ordering hypothesis; TruthfulQA failure is expected and documented as a feature not a bug)

**Mitigation Strategy:**
1. Prevention: Pre-register that TruthfulQA is the hardest case; set separate threshold (AUROC > 0.60 acceptable for TruthfulQA).
2. Detection: Monitor SMC-NLI distribution on TruthfulQA; if bimodal between "confidently wrong" and "uncertain" questions, the mechanism partially holds.
3. Response: If TruthfulQA AUROC < 0.60, document as predicted failure of SMC for adversarial-consistency hallucinations; this is itself a published finding.

**Early Warning:** TruthfulQA SMC-NLI scores clustered near 1.0 (high consistency) regardless of correctness.

---

**Risk R2: NLI OOD Risk (from A2)**

**Source Assumption:** A2 — DeBERTa-v3-large NLI provides meaningful signal for short factual QA answer pairs.

**Description:** DeBERTa-v3-large is trained on SNLI/MultiNLI paragraph-level NLI. For very short factual answers (<5 words), NLI labels may default to "neutral" regardless of semantic equivalence, collapsing SMC-NLI variation and reducing AUROC to ~0.50.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3

**Severity:** High (most impactful risk; affects all hypotheses)

**Mitigation Strategy:**
1. Prevention: Run SMC-Embed in parallel from the start as robustness check.
2. Detection: Monitor distribution of NLI labels (entailment/neutral/contradiction fractions); if >90% "neutral" on all question types, OOD is confirmed.
3. Response: If SMC-NLI AUROC ≤ 0.55 on HaluEval but SMC-Embed ≥ 0.60: NLI OOD confirmed; switch primary metric to SMC-Embed; revise hypothesis claim to SMC-Embed. If both fail: STOP, reassess.

**Early Warning:** H-E1 shows SMC-NLI scores uniformly >0.90 across all questions (NLI classifying everything as neutral/entailment).

---

**Risk R3: Sample Size Risk (from A3)**

**Source Assumption:** A3 — 1000 questions per benchmark is sufficient for reliable AUROC estimation.

**Description:** If AUROC point estimates are accurate but confidence intervals are too wide (e.g., ±0.10), we cannot reliably determine whether AUROC ≥ 0.70 is achieved. This is especially concerning for TruthfulQA-MC (smaller dataset, specific format).

**Affected Hypotheses:** H-M3 (primary AUROC across all benchmarks)

**Severity:** Medium

**Mitigation Strategy:**
1. Prevention: Compute bootstrap 95% CIs early; if CI width > 0.08, plan to increase to 2000 questions.
2. Detection: After H-E1 validation on HaluEval, check CI width of AUROC estimate.
3. Response: Increase to 2000 questions on any benchmark where CI width > 0.08 (one additional week of inference).

**Early Warning:** CI width > 0.08 on HaluEval during H-E1 validation.

---

**Risk R4: Temperature Sensitivity Risk (from A4)**

**Source Assumption:** A4 — Temperature=0.7 produces sufficient semantic diversity without excessive noise.

**Description:** If temperature=0.7 is too low, all samples may be near-identical regardless of factual certainty (low SMC variance). If too high, even correct answers may produce diverse samples (high false negative rate).

**Affected Hypotheses:** H-M1, H-M2

**Severity:** Low-Medium (N-ablation prerequisite partially addresses this; temperature is less critical than N choice)

**Mitigation Strategy:**
1. Prevention: N-ablation prerequisite (200 TriviaQA questions, N ∈ {1,3,5,10,20}) run before main experiment; inspect per-N AUROC to assess temperature indirectly.
2. Detection: If N-ablation shows AUROC plateau already at N=3, temperature may be too low (little diversity).
3. Response: Add temperature sensitivity analysis (0.5, 0.7, 1.0) on 200-question TriviaQA subset as supplementary experiment.

**Early Warning:** N-ablation shows AUROC(N=3) ≈ AUROC(N=10) (suggesting low diversity from temperature).

---

**Risk R5: Model Representativeness Risk (from A5)**

**Source Assumption:** A5 — Llama-3-8B-Instruct is a suitable representative model (~60-70% accuracy on TriviaQA).

**Description:** If Llama-3-8B-Instruct achieves >85% or <40% factual accuracy on any benchmark, the class balance becomes severely skewed, making AUROC estimation unreliable (very few examples of one class).

**Affected Hypotheses:** All hypotheses

**Severity:** Low (Llama-3-8B well-characterized; estimated accuracy range is reasonable)

**Mitigation Strategy:**
1. Prevention: Before main experiment, compute factual accuracy on 100-question sample per benchmark.
2. Detection: If accuracy > 85% or < 30% on any benchmark, re-sample with stratified label selection.
3. Response: Use stratified sampling to enforce ≥ 200 examples per class (correct/hallucinated) per benchmark.

**Early Warning:** Accuracy check shows <30% or >85% factual accuracy on any benchmark.

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Consistent Hallucination (TruthfulQA) | A1 | H-M2, H-M3 | Medium |
| R2: NLI OOD for Short Answers | A2 | H-E1, H-M1, H-M2, H-M3 | High |
| R3: Sample Size / CI Width | A3 | H-M3 | Medium |
| R4: Temperature Sensitivity | A4 | H-M1, H-M2 | Low-Medium |
| R5: Model Representativeness | A5 | All | Low |

**Risk Summary:**
- Critical: 0
- High: 1 (R2)
- Medium: 2 (R1, R3)
- Low-Medium: 1 (R4)
- Low: 1 (R5)

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: SMC Signal Existence
    (Existence — no dependencies)
         │
         ▼ [Gate 1: MUST_WORK — if fails: STOP]
[Level 1 - Core Mechanism Step 1]
    H-M1: Factual Certainty → Concentrated Distribution
    (Mechanism Step 1 ← H-E1)
         │
         ▼ [Gate 2: MUST_WORK — if fails: PIVOT/STOP]
[Level 2 - Core Mechanism Step 2]
    H-M2: Hallucination → Multimodal Distribution
    (Mechanism Step 2 ← H-M1)
         │
         ▼ [Gate 2b: SHOULD_WORK — failure narrows not invalidates]
[Level 3 - Core Mechanism Step 3 / Primary Test]
    H-M3: NLI Pairwise Agreement → Discriminative AUROC
    (Mechanism Step 3 ← H-M2)
         │
         ▼ [Gate 3: SHOULD_WORK — failure → metric switch or Phase 0]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
All paths sequential (no parallelization)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │  W1-2   │  W3-4   │   W5    │
──────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1            │ ████████│         │         │
  Prerequisite:   │  N-abl  │         │         │
  [Gate 1] ◆     │       ◆ │         │         │
──────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms (Steps 1-3)
  H-M1            │         │ ████    │         │
  H-M2            │         │     ████│         │
  H-M3            │         │         │ ████████│
  [Gate 2] ◆     │         │   ◆     │         │
  [Gate 3] ◆     │         │         │        ◆│
══════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision | N-abl = N-ablation prerequisite
Total Duration: 5 weeks
Note: N-ablation (200 TriviaQA questions, N ∈ {1,3,5,10,20}) runs during W1 before main H-E1
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3)

Slack Available: 0 weeks (fully sequential)

Prerequisite: N-ablation experiment (200 TriviaQA, <1 day) runs
  in Week 1 before H-E1 main data collection.
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
- Condition: 0 (scope boundaries documented as constraints)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks

Inference load:
- Prerequisite N-ablation: 200 × 20 = 4,000 inference calls
- Main study: 4,000 questions × 10 samples = 40,000 inference calls
- NLI scoring: 40,000 × 45 pairs = 1,800,000 NLI pair evaluations
  (~1,000 pairs/hour on A100 ≈ 1,800 hours → parallelizable)
- Embedding scoring: 40,000 × 45 = 1,800,000 pairs (faster)

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Run N-ablation prerequisite (200 TriviaQA, N ∈ {1,3,5,10,20}) — Week 1
Step 2: Confirm N=10 elbow from ablation (P3 check); proceed if AUROC(N=10) ≥ 0.95×AUROC(N=20)
Step 3: Execute H-E1 — Week 1-2
  - 1000 HaluEval questions, SMC-NLI + SMC-Embed, AUROC computation
Step 4: Evaluate Gate 1 — End of Week 2
  - PASS: proceed to H-M1
  - FAIL (NLI only): switch to SMC-Embed primary, continue
  - FAIL (both): STOP
Step 5: Execute H-M1 — Week 3 (first half)
  - TriviaQA 1000 questions, group by correct/hallucinated, compare SMC-NLI
Step 6: Evaluate Gate 2 — Mid-Week 3
Step 7: Execute H-M2 — Week 3 (second half)
  - TriviaQA + NQ contradiction rates
Step 8: Execute H-M3 — Week 4-5
  - All 4 benchmarks, all methods, full AUROC+AUPRC, bootstrap CIs
Step 9: Evaluate Gate 3 — End of Week 5
Step 10: Verification complete → Phase 4.5 Synthesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim:
NLI-based Semantic Mode Consistency (SMC) across N=10 stochastic
samples from a black-box LLM is a reliable hallucination predictor
(AUROC ≥ 0.70) across factual QA benchmarks, because factual certainty
concentrates the sampling distribution (unimodal) while hallucination
spreads it (multimodal).

Supporting Evidence:
1. Causal mechanism supported by Kuhn et al. 2023 (semantic entropy
   lower for correct answers) and Manakul et al. 2023 (NLI consistency
   higher for non-hallucinated sentences on WikiBio).
2. HaluEval balanced labels (50/50) provide clean ground truth;
   AUROC ≥ 0.70 is achievable if signal exists.
3. Three testable predictions (P1: AUROC threshold; P2: ordering;
   P3: N-efficiency) make the hypothesis rigorously falsifiable.

Strengths:
- Strictly black-box (no logit access required) — practically deployable
- Multi-benchmark scope closes known literature gap
- Dual NLI+embedding comparison provides robustness check
- SMC framing is theoretically grounded in semantic distribution theory

Expected Outcomes:
- P1: AUROC ≥ 0.70 on TriviaQA, NQ, HaluEval; potentially lower on TruthfulQA
- P2: AUROC ordering HaluEval > TriviaQA ≈ NQ > TruthfulQA
- P3: N-efficiency elbow at N≤10 on TriviaQA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0):
There is no significant difference in hallucination prediction AUROC
between SMC-NLI (N=10) and verbalized confidence across TriviaQA, NQ,
HaluEval, and TruthfulQA. Equivalently: SMC AUROC < 0.65 on ≥ 2 benchmarks.

Counter-Arguments:
1. DeBERTa-NLI was trained on paragraph-level NLI (SNLI/MultiNLI); short
   factual answers (<5 words) may fall OOD, causing SMC-NLI to classify
   all pairs as "neutral" regardless of semantic equivalence.
2. TruthfulQA adversarial design: some questions are specifically crafted to
   elicit confident, consistent wrong answers — violating A1. SMC would
   classify these as factual (high consistency) even though they are wrong.
3. Verbalized confidence from sufficiently capable models may be well-
   calibrated on factual QA, closing the gap (Xiong et al. 2023 shows
   verbalized confidence can achieve AUROC ~0.65+ on some tasks).

Potential Failure Points:
- R2 (NLI OOD): SMC-NLI degenerate → AUROC collapses to ~0.50 on all benchmarks
- R1 (TruthfulQA consistency): AUROC < 0.65 on TruthfulQA and possibly NQ
- N=10 insufficient: SMC plateau not reached, AUROC noisier than expected

Conditions Under Which H0 Would Be Supported:
- AUROC < 0.65 on ≥ 2 of 4 benchmarks for SMC-NLI
- AUROC < 0.60 on any single benchmark
- SMC-NLI not significantly better than verbalized confidence (p ≥ 0.05)
- Both SMC-NLI and SMC-Embed fail on ≥ 2 benchmarks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-SMC-v1 presents a theoretically grounded claim with strong prior
evidence from SelfCheckGPT and Semantic Uncertainty. However, the null
hypothesis raises two valid empirical concerns: NLI OOD behavior on
short answers and TruthfulQA's adversarial design.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Tests NLI OOD concern directly on
   HaluEval before committing to full 4-benchmark evaluation. SMC-Embed
   runs in parallel as fallback.
2. Sequential mechanism testing (H-M1→H-M2→H-M3): Tests causal chain
   step-by-step, with TruthfulQA explicitly designated as hardest case.
3. Pre-registered predictions: TruthfulQA degradation (P2 ordering) is
   a testable prediction rather than a confound — converting antithesis
   concern into a scientific finding.
4. Gate conditions: H-E1 and H-M1 gates allow early detection of H0
   support before full experiment commitment.

Conditions for Thesis Support:
- H-E1 MUST_WORK gate passes (AUROC > 0.60 on HaluEval)
- H-M1 MUST_WORK gate passes (directional discrimination on TriviaQA)
- SMC-NLI AUROC ≥ 0.70 on ≥ 3 of 4 benchmarks
- AUROC(HaluEval) > AUROC(TruthfulQA) with non-overlapping CIs

Conditions for Antithesis Support:
- H-E1 fails (both SMC-NLI and SMC-Embed AUROC < 0.60)
- H-M1 fails (no directional discrimination on TriviaQA)
- SMC-NLI AUROC < 0.65 on ≥ 2 benchmarks AND SMC-Embed also < 0.65

Nuanced Outcome Possibilities:
1. Full Support: All hypotheses pass → SMC-NLI validated; paper claim: reliable across 4 benchmarks
2. Metric Switch: SMC-NLI fails but SMC-Embed passes → Revised claim: embedding consistency preferable for short QA
3. Partial Support: H-M1/H-M2 pass but H-M3 fails on TruthfulQA only → Confirmed predicted scope limitation
4. No Support: H-E1 or H-M1 fail → Antithesis supported; route to Phase 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (H-E1) | SMC produces meaningful variation | NLI OOD → degenerate scores | H-E1 MUST_WORK gate + SMC-Embed parallel |
| Mechanism Step 1 (H-M1) | Correct answers show higher SMC | Low temperature → all samples similar | H-M1 Wilcoxon test; N-ablation diagnoses |
| Mechanism Step 2 (H-M2) | Hallucinated answers show more contradiction | TruthfulQA adversarial consistent errors | H-M2 tests on TriviaQA/NQ (less adversarial) |
| Full Discrimination (H-M3) | AUROC ≥ 0.70 across 4 benchmarks | TruthfulQA and NLI OOD both suppress | Pre-registered ordering prediction (P2); SMC-Embed fallback |
| Performance vs. Baselines | SMC > verbalized confidence | Verbalized confidence increasingly calibrated | Phase 5 handles white-box baseline comparison |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SMC-v1 — SMC as Black-Box Hallucination Predictor
- ID: H-SMC-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (builds on Kuhn et al. 2023, Manakul et al. 2023)
- Sub-Hypotheses: 4 total
  - H-E: 1 (existence check on HaluEval)
  - H-M: 3 (causal chain steps, multi-benchmark AUROC)
- Phases: 2 phases over 5 weeks
- Critical Gates: 3 decision points (Gate 1: MUST_WORK, Gate 2: MUST_WORK, Gate 3: SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: NLI OOD for short answers (R2, High); TruthfulQA consistent-hallucination suppression (R1, Medium)
- Both mitigated: SMC-Embed parallel metric; P2 ordering prediction pre-registers TruthfulQA degradation

**Scope Reduction:** 50% of claims are BUILD_ON (already validated); only 2 PROVE_NEW claims require new experiments

**Immediate Action:** Run N-ablation prerequisite (200 TriviaQA, N ∈ {1,3,5,10,20}, <1 day) then begin H-E1

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- Prerequisite: N-ablation on 200 TriviaQA questions (<1 day, Week 1)
- H-E1: SMC signal existence on 1000 HaluEval questions
- Gate 1: MUST PASS (both SMC-NLI and SMC-Embed evaluated; either passing is sufficient)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Factual certainty → concentrated distribution on TriviaQA (1 week)
- H-M2: Hallucination → multimodal distribution on TriviaQA + NQ (1 week, overlapping)
- H-M3: NLI pairwise agreement → AUROC ≥ 0.70 across all 4 benchmarks (1 week, main experiment)
- Gate 2: H-M1 MUST_WORK (mechanism must show directional signal)
- Gate 3: H-M3 SHOULD_WORK (primary AUROC threshold; metric switch acceptable)

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation — H-E1):** SMC must produce discriminative signal
   - PASS → Proceed to Phase 2 with NLI (or Embed) as primary metric
   - FAIL (NLI only) → Switch to SMC-Embed as primary; continue
   - FAIL (both) → STOP; reassess methodology

2. **Gate 2 (Mechanism — H-M1):** Directional discrimination must hold
   - PASS → Proceed to H-M2 and H-M3
   - FAIL → PIVOT: temperature ablation or model change; if still fails → Phase 0

3. **Gate 3 (Primary — H-M3):** AUROC threshold across benchmarks
   - PASS (≥ 3 benchmarks at ≥ 0.70) → Thesis supported; proceed to Phase 4.5
   - PARTIAL (NLI fails, Embed holds) → Revised claim with SMC-Embed; Phase 4.5
   - FAIL (both < 0.65 on ≥ 2) → Antithesis supported; Phase 0

### 7.4 Open Questions

- Does NLI-based consistency outperform embedding-based consistency on short factual answers? (H-E1 will provide first data)
- What is the minimum N for reliable SMC? (N-ablation prerequisite answers this)
- Does TruthfulQA's adversarial design suppress SMC signal below AUROC 0.70? (P2 ordering test)
- Is AUROC(HaluEval) > AUROC(TruthfulQA) ordering confirmed empirically? (H-M3 direct test)

### 7.5 Recommendations

1. **Immediate Actions:**
   - Run N-ablation prerequisite before any main data collection
   - Set up Llama-3-8B-Instruct local inference + DeBERTa NLI scorer + all-mpnet-base-v2
   - Pre-register falsification criteria: AUROC < 0.65 on ≥ 2 benchmarks

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path (40,000 inference calls main study)
   - Reserve 1 additional week if CI width exceeds 0.08 (increase to 2000 questions)

3. **Failure Management:**
   - Document all gate decisions with metric values and CIs
   - Execute SMC-Embed PIVOT if SMC-NLI fails at H-E1
   - Pre-register that TruthfulQA AUROC < 0.70 is expected and is a finding, not failure

---

## Appendices

### A. Phase 2A Reference
- **Source:** docs/youra_research/03_refinement.yaml (ID: H-SMC-v1)
- **Convergence:** Exchange 8, unanimous (Prof. Vera convergence vote), all 6 criteria met
- **Architecture:** Self-Contained Tikitaka Loop (independent-controller ablation)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 0 (ablation mode — no MCP available in this session)
- **Reasoning approach:** Phase 2A structured data used directly for causal chain detection (3 steps) and risk mapping (A1-A5)
- **Ablation note:** ClearThought scientificmethod and structuredargumentation replaced by internal systematic analysis using Phase 2A outputs

### C. Hypothesis Count Determination
- causal_chain_count: 3 → H-M1, H-M2, H-M3
- existence_count: 1 → H-E1 (from sh1_existence)
- condition_count: 0 (no quantitative boundary conditions requiring separate hypothesis)
- Total: 4 hypotheses (3 + 1)
- Duration formula: 2 (H-E1) + 3 (H-M) + 0 (H-C) = 5 weeks
