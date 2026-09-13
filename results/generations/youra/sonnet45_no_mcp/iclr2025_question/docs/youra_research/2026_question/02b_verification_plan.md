---
stepsCompleted: [step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08, step-09, step-10]
status: complete
completedAt: "2026-04-22T00:00:00Z"
pipeline_project_title: "Anonymous Pipeline: Uncertainty Quantification in Foundation Models"
---

# Verification Plan: Mechanistic Decomposition of Uncertainty Method Performance

**Date:** 2026-04-22
**Hypothesis ID:** H-UncertaintyMechanisms-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under systematic empirical evaluation on factual QA benchmarks (NaturalQuestions, TruthfulQA), if we compare four uncertainty estimation methods (semantic entropy, self-consistency, token variance, verbalized confidence) with matched sample sizes and controlled experimental conditions, then method performance rankings will differ significantly across error types (knowledge gaps vs confident misconceptions), because each method captures a distinct uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration) that responds differently to different error signatures.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in uncertainty method performance rankings across error types. All methods measure the same underlying uncertainty signal with equivalent effectiveness, and observed performance differences are solely attributable to computational budget (number of samples) rather than method-specific mechanisms.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | NaturalQuestions (100 examples) + TruthfulQA (100 examples) (standard) | NaturalQuestions provides knowledge-gap errors with 'unanswerable' category, TruthfulQA provides confident-misconception errors (memorized falsehoods), enabling error-type comparison per H-ERROR-TYPE |
| **Model** | Mistral-7B-v0.1 | 7B scale achieves >50% accuracy on factual QA (avoiding h-e1 failure where GPT-2 had 0.9%), open-source enables replication, output-based methods work across architectures |

**Dataset Details:**
- Source: Public benchmarks - NaturalQuestions from Google, TruthfulQA from Lin et al. 2022
- Path: Loaded via HuggingFace datasets library

**Model Details:**
- Type: Open-source decoder-only transformer LLM
- Source: HuggingFace model hub, fully open weights

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Kuhn 2023) | Strong performance on NLG hallucination detection | Generation tasks, not specifically factual QA |
| Self-Consistency (Wang 2022) | Improved chain-of-thought reasoning accuracy | Math reasoning tasks, commonsense QA |
| Verbalized Confidence (Kadavath 2022) | Models can self-report with reasonable calibration | Various QA tasks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Error types can be objectively partitioned using model's verbalized confidence scores: >80% confident but wrong = confident misconception, <50% confident and wrong = knowledge gap | Prof. Rex raised partitioning concern in Exchange 12, mitigation proposed using model's own confidence as objective criterion | If partition is subjective or unreliable, error-type comparisons become confounded and H-ERROR-TYPE cannot be properly tested |
| A2 | Semantic entropy implementation (embedding model, clustering algorithm, similarity threshold) matches Kuhn 2023 methodology sufficiently to reproduce their findings | Kuhn 2023 provides implementation details, code availability mentioned in Phase 1 | If clustering implementation differs significantly, semantic entropy results may not be comparable to published baselines, requiring sensitivity analysis across configurations |
| A3 | K=10 samples is sufficient for semantic entropy to demonstrate clustering advantage and for self-consistency to show agreement patterns, while not being excessive | Wang 2022 used K=5-40 for self-consistency, discussion chose K=10 as middle ground, Prof. Rex requested K-sensitivity analysis | If K=10 is too small or too large, method comparisons become unfair, requiring K-sensitivity analysis across {5, 10, 20} |
| A4 | Mistral-7B achieves >50% accuracy on NaturalQuestions and >20% on TruthfulQA, providing sufficient correct/incorrect examples for AUROC calculation | Prof. Pax cited ~65% accuracy on NaturalQuestions in Exchange 9, avoiding previous failure where GPT-2 had 0.9% on TruthfulQA | If model accuracy too low, insufficient positive examples make AUROC unreliable, requiring model substitution or dataset change |
| A5 | Verbalized confidence calibration depends on presence of metacognitive training signals (e.g., 'unanswerable' category in NaturalQuestions) rather than model size or architecture | Dr. Nova's mechanistic analysis in Exchange 7 - NaturalQuestions trains models to say 'I don't know', TruthfulQA does not | If calibration differences arise from other factors (model size, architecture, dataset difficulty), H-CALIBRATION attribution becomes uncertain |

### 1.6 Research Gap & Novelty

**Gap:** Systematic comparison of uncertainty methods on same benchmarks using consistent protocols is missing. Each method has been validated independently on different benchmarks with different experimental setups.

**Novelty:** Mechanistic decomposition approach transforming method comparison from 'which wins' to 'what mechanisms explain performance when'. Introduces uncertainty fingerprinting concept: each benchmark has characteristic multi-method signature revealing error type. Key innovation: Ablation design isolating semantic clustering contribution from sampling effect (comparing semantic entropy vs ensemble baseline at matched K=10), plus error-type partitioning enabling method-specificity analysis.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Status |
|----|------|-------------------|---------------|--------|
| H-E1 | Existence | Semantic entropy clustering effect exists (ablation vs ensemble baseline) | None | TODO |
| H-M1 | Mechanism | Uncertainty methods probe orthogonal dimensions | H-E1 | TODO |
| H-M2 | Mechanism | Error types generate distinct uncertainty signatures | H-M1 | TODO |
| H-M3 | Mechanism | Method-error matching determines effectiveness | H-M2 | TODO |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Semantic Entropy Clustering Effect Exists

**Statement**: Under controlled experimental conditions on knowledge-gap errors (NaturalQuestions unanswerable subset), if we compare semantic entropy (K=10 with clustering) against ensemble baseline (K=10 majority vote without clustering), then semantic entropy will outperform by ≥0.07 AUROC, because semantic clustering captures answer diversity beyond simple sampling frequency.

**Rationale**: This hypothesis validates that semantic entropy's clustering mechanism adds value beyond multiple sampling alone. The ablation design isolates the clustering contribution from the sampling effect by matching K=10 across both methods.

**Variables**:
- Independent: Method type (semantic entropy vs ensemble baseline)
- Dependent: AUROC (error detection discrimination)
- Controlled: Model (Mistral-7B), Sample count (K=10), Temperature (0.7), Dataset (NaturalQuestions 100 examples)

**Verification Protocol**:
1. Generate K=10 answers for each question using Mistral-7B at T=0.7
2. Apply semantic entropy (embed + cluster + entropy) and ensemble baseline (majority vote) to same samples
3. Compute AUROC for both methods on knowledge-gap errors
4. Calculate AUROC difference and test statistical significance

**Success Criteria**:
- Primary: AUROC_semantic - AUROC_ensemble ≥ 0.07
- Secondary: Semantic entropy absolute AUROC ≥ 0.70

**Failure Response**:
- IF fails: PIVOT to simpler uncertainty methods (no clustering advantage demonstrated)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Prediction P1, Section 1.6

---

#### H-M1: Uncertainty Methods Probe Orthogonal Dimensions

**Statement**: Under systematic evaluation, if we analyze the four uncertainty methods (semantic entropy, self-consistency, token variance, verbalized confidence) using their distinct computational mechanisms, then each method will capture a different uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration), because the methods are algorithmically designed to measure different statistical properties of model outputs.

**Rationale**: This hypothesis validates the first step in the causal chain—that methods differ mechanistically, not just computationally. Establishes the foundation for why methods should perform differently across error types.

**Variables**:
- Independent: Method mechanism (clustering, sampling, probability, introspection)
- Dependent: Uncertainty dimension measured
- Controlled: Model, dataset, sample size K=10

**Verification Protocol**:
1. Implement all four methods following published specifications
2. Compute uncertainty scores for same set of model outputs
3. Analyze correlation matrix between method scores
4. Verify low correlation (methods measure different signals)

**Success Criteria**:
- Primary: Pairwise correlation between methods < 0.7 (demonstrating orthogonality)
- Secondary: Each method shows distinct response patterns

**Failure Response**:
- IF fails: EXPLORE whether methods measure same signal with different scales

**Dependencies**: H-E1 (clustering mechanism validated)

**Source**: Phase 2A Causal Mechanism Step 1, Section 1.3

---

#### H-M2: Error Types Generate Distinct Uncertainty Signatures

**Statement**: Under comparison between NaturalQuestions (knowledge gaps) and TruthfulQA (confident misconceptions), if we measure semantic diversity and sampling agreement for correct vs incorrect answers, then knowledge gaps will show high semantic diversity + low agreement while confident misconceptions will show low diversity + high agreement on wrong answer, because different error types arise from different failure modes in the model.

**Rationale**: This hypothesis validates the second causal step—that error types have characteristic uncertainty signatures. Connects error taxonomy to observable uncertainty patterns.

**Variables**:
- Independent: Error type (knowledge gap vs confident misconception)
- Dependent: Semantic diversity, sampling agreement
- Controlled: Model, sample size, temperature

**Verification Protocol**:
1. Partition errors using model's verbalized confidence (>80% = misconception, <50% = gap)
2. Measure semantic diversity (answer variety) for each error type
3. Measure sampling agreement (consistency) for each error type
4. Compare signatures across error types

**Success Criteria**:
- Primary: Knowledge gaps show higher diversity than misconceptions (statistically significant)
- Secondary: Misconceptions show higher agreement than knowledge gaps

**Failure Response**:
- IF fails: EXPLORE alternative error type partitioning methods

**Dependencies**: H-M1 (orthogonal dimensions established)

**Source**: Phase 2A Causal Mechanism Step 2, Section 1.3

---

#### H-M3: Method-Error Matching Determines Effectiveness

**Statement**: Under error-type specific evaluation, if we measure each method's AUROC separately on knowledge gaps vs confident misconceptions, then method performance rankings will differ significantly across error types (rank correlation < 0.7), because methods designed to detect diversity excel on knowledge gaps while methods measuring confidence excel on misconceptions.

**Rationale**: This hypothesis validates the complete causal chain—that matching method mechanisms to error signatures determines detection effectiveness. Delivers the actionable insight for method selection.

**Variables**:
- Independent: (Method × Error Type) interaction
- Dependent: AUROC performance ranking
- Controlled: Model, dataset, sample size

**Verification Protocol**:
1. Compute AUROC for all methods on knowledge-gap errors (NaturalQuestions)
2. Compute AUROC for all methods on confident-misconception errors (TruthfulQA)
3. Rank methods by performance within each error type
4. Calculate Spearman rank correlation between error types

**Success Criteria**:
- Primary: Rank correlation < 0.7 (demonstrating error-type specificity)
- Secondary: Self-consistency AUROC < 0.55 on TruthfulQA but ≥ 0.65 on NaturalQuestions

**Failure Response**:
- IF fails: ABANDON method-specificity claim (methods measure general uncertainty)

**Dependencies**: H-M2 (error signatures characterized)

**Source**: Phase 2A Causal Mechanism Step 3, Prediction P2, Section 1.3

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 2.3 Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Description | Affected Hypotheses | Severity |
|------|--------|-------------|---------------------|----------|
| R1 | A1 | Error type partitioning unreliable if verbalized confidence miscalibrated | H-M2, H-M3 | High |
| R2 | A2 | Semantic entropy results not comparable if clustering differs from Kuhn 2023 | H-E1, H-M1 | High |
| R3 | A3 | K=10 samples insufficient or excessive for fair comparison | H-E1, H-M1, H-M3 | Medium |
| R4 | A4 | Model accuracy too low (<50%), insufficient positive examples for AUROC | All hypotheses | Critical |
| R5 | A5 | Calibration differences from non-training factors, not metacognitive signals | H-M3 | Medium |

### Mitigation Strategies

**Risk R1: Error Type Partitioning Unreliable**
- **Prevention:** Use model's own verbalized confidence as objective criterion (>80% = confident, <50% = uncertain) rather than assuming all TruthfulQA = misconceptions
- **Detection:** Check distribution of confidence scores, verify partitions make semantic sense
- **Response:** If partition unreliable → PIVOT to alternative partitioning using answer diversity metrics

**Risk R2: Clustering Implementation Mismatch**
- **Prevention:** Follow Kuhn 2023 implementation details exactly (embedding model, clustering algorithm, similarity threshold)
- **Detection:** Compare semantic entropy AUROC to published baselines on validation set
- **Response:** If results differ significantly → SCOPE to test 2-3 clustering configurations for robustness analysis

**Risk R3: Sample Size Not Optimal**
- **Prevention:** Include K-sensitivity analysis across {5, 10, 20} samples
- **Detection:** Check if performance plateaus or degrades at K=10
- **Response:** If K=10 unfair → PIVOT to report K-sensitivity curves instead of fixed-K comparison

**Risk R4: Model Accuracy Too Low**
- **Prevention:** Pre-validate Mistral-7B accuracy on small NaturalQuestions subset before full experiment
- **Detection:** Monitor accuracy during pilot runs
- **Response:** If accuracy <50% → ABORT and substitute model (Llama-3.1-8B) or change dataset

**Risk R5: Calibration Attribution Uncertain**
- **Prevention:** Control for model size and architecture (use same Mistral-7B across benchmarks)
- **Detection:** Compare calibration across multiple models if possible
- **Response:** If attribution unclear → SCOPE to report correlation, avoid causal claim about training signals

### Risk Summary

**Critical Risks:** 1 (R4 - Model accuracy)
**High Risks:** 2 (R1 - Partitioning, R2 - Clustering)
**Medium Risks:** 2 (R3 - Sample size, R5 - Calibration)
**Low Risks:** 0

**Top Mitigation Priority:**
1. Pre-validate Mistral-7B accuracy (R4)
2. Follow exact clustering implementation (R2)
3. Verify partitioning distribution (R1)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```
<!-- Sequential verification: clustering effect → orthogonal dimensions → error signatures → method-error matching -->

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC_semantic - AUROC_ensemble ≥ 0.07 | PIVOT to simpler methods |
| H-M1 | SHOULD_WORK | Method correlation < 0.7 | EXPLORE alternative analysis |
| H-M2 | SHOULD_WORK | Diversity differs across error types | EXPLORE partitioning |
| H-M3 | DETERMINES_SUCCESS | Rank correlation < 0.7 | ABANDON method-specificity claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration | Key Activities |
|-------|------------|----------|----------------|
| Phase 1 | H-E1 | 2-3 days | Implement ablation study, validate clustering |
| Phase 2 | H-M1 | 1-2 days | Compute correlation matrix, verify orthogonality |
| Phase 3 | H-M2 | 2-3 days | Partition errors, measure signatures |
| Phase 4 | H-M3 | 3-4 days | Full evaluation across error types, statistical analysis |

**Total Duration:** 8-12 days (pilot study)

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 (sequential dependencies)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-04-22*
