# Verification Plan: Complementary Entropy-Consistency Hallucination Detection

**Date:** 2026-08-19
**Hypothesis ID:** H-EntropyConsistency-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under QA task conditions with pretrained instruction-tuned LLMs,
if we combine token-level entropy and semantic consistency into a single hallucination prediction score,
then prediction accuracy (AUROC) improves by ≥2 percentage points over the best single metric,
because entropy and consistency capture complementary failure modes (internal confusion vs. output instability).

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AUROC between the combined entropy-consistency metric
and the best single metric (entropy alone or consistency alone) on QA benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA (standard) | Large-scale factual QA with ground-truth answers, standard benchmark for hallucination evaluation |
| **Model** | Llama-2-7B-chat | Open-source model with logit access, representative of deployed LLMs |

**Dataset Details:**
- Source: mandarjoshi/trivia_qa (HuggingFace)
- Path: trivia_qa/rc.nocontext

**Model Details:**
- Type: instruction-tuned LLM
- Source: meta-llama/Llama-2-7b-chat-hf (HuggingFace)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Kuhn et al., 2023) | AUROC ~0.75-0.85 | Various QA benchmarks |
| SelfCheckGPT (Manakul et al., 2023) | Not reported on TriviaQA/NQ | WikiBio, custom datasets |
| Verbalized Confidence (Xiong et al., 2023) | Poor calibration | Multiple benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Token entropy is accessible (model provides logits) | Open-source models like Llama expose logits | Cannot compute entropy; must use alternative uncertainty proxy |
| A2 | Semantic similarity captures meaning equivalence adequately | NLI models and embedding similarity are well-validated | Consistency metric becomes unreliable |
| A3 | Ground-truth labels in benchmarks are reliable | TriviaQA/NQ are established with verified answers | Evaluation is noisy, may require larger sample sizes |
| A4 | Entropy and consistency are sufficiently uncorrelated | Theoretically different signals (internal vs. output) | Combination provides no benefit over single metric |
| A5 | Results generalize across question difficulty levels | Benchmarks contain varied difficulty | Must stratify results by difficulty |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic combination of entropy and consistency on QA benchmarks

**Key Innovation:** Complementary failure modes framework - entropy as internal confusion, consistency as output instability

**Differentiation:**
- Kuhn et al. (2023): Uses semantic clustering + entropy; we add consistency signal
- Manakul et al. (2023): Uses consistency only; we add entropy signal
- Xiong et al. (2023): Relies on model self-report; we use token-level signals

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Entropy and Consistency Signal Existence

**Type:** EXISTENCE
**Statement:** Under QA task conditions with Llama-2-7B-chat, if we generate multiple responses per question and access token logits, then token entropy and semantic consistency can be computed for every response, because the model provides logit access and semantic similarity is computable via embedding models.

**Variables:**
- IV: Generation of N samples per question with logit access
- DV: Successful computation of (entropy, consistency) pair for each question
- CV: Model (Llama-2-7B-chat), samples (10), temperature (0.7)

**Verification Protocol:**
1. Load TriviaQA validation set (full ~11K questions for statistically meaningful evaluation)
2. Generate 10 responses per question with temperature 0.7
3. Compute token entropy from logit distributions
4. Compute semantic consistency via embedding cosine similarity
5. Verify both metrics computed successfully for >99% of questions

**Success Criteria (PoC):**
- Primary: Both entropy and consistency computed for >99% of questions
- Secondary: Variance in both metrics across questions (not constant)

**Failure Response:**
- IF fails: PIVOT to alternative uncertainty estimation (e.g., verbalized)

**Dependencies:** None

**Source:** Phase 2A SH1

---

#### H-M1: Token Entropy Captures Internal Uncertainty

**Type:** MECHANISM
**Statement:** Under QA task conditions, if we measure token entropy from softmax logit distributions, then entropy values correlate with model uncertainty, because flat distributions (high entropy) indicate the model has low confidence in any particular token.

**Variables:**
- IV: Token entropy measurement method
- DV: Correlation between entropy and question difficulty/correctness
- CV: Same as H-E1

**Verification Protocol:**
1. Compute entropy for all TriviaQA validation questions (~11K)
2. Split by ground-truth correctness (correct vs. incorrect)
3. Compute correlation between entropy and correctness
4. Test: mean entropy for incorrect > mean entropy for correct

**Success Criteria (PoC):**
- Primary: Higher entropy for incorrect answers (t-test p < 0.05)
- Secondary: AUROC > 0.55 for correctness prediction using entropy alone

**Failure Response:**
- IF fails: EXPLORE alternative entropy definitions (sequence-level vs. token-level)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Semantic Consistency Captures Output Stability

**Type:** MECHANISM
**Statement:** Under QA task conditions, if we measure pairwise semantic similarity across N generated responses, then low consistency indicates hallucination-prone questions, because unstable outputs reflect the model's inability to reliably converge on an answer.

**Variables:**
- IV: Semantic consistency (avg pairwise embedding cosine similarity)
- DV: Correlation between consistency and correctness
- CV: Same as H-E1

**Verification Protocol:**
1. For each question, compute pairwise embedding similarity across 10 samples
2. Average to get consistency score per question
3. Split by correctness, compare distributions
4. Test: mean consistency for correct > mean consistency for incorrect

**Success Criteria (PoC):**
- Primary: Higher consistency for correct answers (t-test p < 0.05)
- Secondary: AUROC > 0.55 for correctness prediction using consistency alone

**Failure Response:**
- IF fails: EXPLORE alternative similarity metrics (NLI-based, BERTScore)

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Signal Combination via Linear Fusion

**Type:** MECHANISM
**Statement:** Under QA conditions, if we combine inverse entropy and consistency via linear fusion (α·(1-entropy) + β·consistency), then the combined score is more predictive than either alone, because the signals capture complementary failure modes.

**Variables:**
- IV: Combination method (linear fusion weights α, β)
- DV: AUROC for correctness prediction
- CV: Same as H-E1, baseline metrics

**Verification Protocol:**
1. Normalize entropy and consistency to [0,1] range
2. Grid search α, β on held-out validation set (10% of data)
3. Evaluate combined score AUROC on test set (~10K questions)
4. Compare: AUROC_combined vs. max(AUROC_entropy, AUROC_consistency)

**Success Criteria (PoC):**
- Primary: AUROC_combined > max(single metrics) by any margin
- Secondary: Improvement visible without extensive tuning (α=β=0.5 baseline)

**Failure Response:**
- IF fails: EXPLORE quadrant-based classification or learned combination

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Hallucination Prediction Improvement

**Type:** MECHANISM
**Statement:** Under QA conditions with TriviaQA (and validated on NQ, TruthfulQA), if we use the linear fusion score for hallucination prediction, then AUROC improves by ≥2pp over the best single metric, because the complementary signals fill each other's blind spots.

**Variables:**
- IV: Prediction method (single metric vs. combined)
- DV: AUROC improvement (Δ ≥ 0.02)
- CV: Same evaluation procedure across all conditions

**Verification Protocol:**
1. Evaluate on TriviaQA test set (~10K questions)
2. Compute AUROC: entropy_only, consistency_only, combined
3. Calculate improvement: AUROC_combined - max(single)
4. Validate on NQ (~3K) and TruthfulQA (~817) for robustness

**Success Criteria (PoC):**
- Primary: AUROC improvement ≥ 2pp OR AUROC_combined > 0.97 (ceiling)
- Secondary: Improvement replicates on at least 2/3 datasets

**Failure Response:**
- IF fails: EXPLORE quadrant analysis for interpretable partial success

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Logit access unavailable | A1 | H-E1, H-M1 | Critical |
| R2: Semantic similarity unreliable | A2 | H-M2 | High |
| R3: Noisy ground-truth labels | A3 | H-M4 | Medium |
| R4: Signals highly correlated | A4 | H-M3, H-M4 | High |
| R5: Difficulty confound | A5 | All | Medium |

### 3.2 Mitigation Strategies

**R1: Logit Access**
- Prevention: Verify Llama-2-7B-chat logit access before experiment
- Detection: Check for NaN/null entropy values
- Response: PIVOT to open-source model with confirmed logit access

**R2: Semantic Similarity**
- Prevention: Use validated embedding model (SentenceTransformers)
- Detection: Check for degenerate similarity (all ~1.0 or ~0.0)
- Response: EXPLORE NLI-based similarity as backup

**R3: Noisy Labels**
- Prevention: Use established benchmarks with verified answers
- Detection: Sample-check disagreements manually
- Response: Increase sample size if needed

**R4: Signal Correlation**
- Prevention: Check correlation before combination
- Detection: Pearson r > 0.7 indicates high correlation
- Response: If correlated, document as limitation; combination may still help

**R5: Difficulty Confound**
- Prevention: Stratify analysis by question difficulty
- Detection: Check if improvement varies by difficulty
- Response: Report stratified results alongside aggregate

### 3.3 Risk Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Logit unavailability | Critical | Verify before start |
| R2 | Poor semantic similarity | High | Use validated embeddings |
| R3 | Label noise | Medium | Use established benchmarks |
| R4 | Signal correlation | High | Check correlation, document |
| R5 | Difficulty confound | Medium | Stratified analysis |

---

## 4. Dependency Graph

### 4.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanisms]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 4.3 Gate Conditions

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Compute entropy + consistency | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, cannot proceed without metrics.

**Phase 2 - Core Mechanisms**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | Should pass |
| H-M3 | H-M2 | Should pass |
| H-M4 | H-M3 | Should pass |

→ **Gate 2**: H-M1 must pass. Later H-M failures = document as limitations.

---

## 5. Timeline

### 5.1 Gantt Visualization

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │     ████│         │
  H-M4           │         │         │         │ ████    │
  [Gate 2]       │         │         │         │     ◆   │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
**Total Duration:** 6 weeks (2 + 2 + 1 + 0.5 + 0.5)
**Slack:** 0 weeks (all sequential)

### 5.3 Execution Order

1. **Week 1-2**: H-E1 (Foundation) - Verify metrics computable
2. **Gate 1**: If pass → Proceed
3. **Week 3-4**: H-M1 (Entropy validates) - Test entropy correlation
4. **Week 5**: H-M2 + H-M3 (Consistency + Combination) - Test consistency, fusion
5. **Week 6**: H-M4 (Final improvement) - Full evaluation on 3 datasets
6. **Gate 2**: Evaluate all results

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Combining token entropy and semantic consistency improves hallucination detection AUROC by ≥2pp because the signals capture complementary failure modes.

**Supporting Evidence:**
1. Entropy captures internal model uncertainty (logit distribution)
2. Consistency captures output stability (multi-sample agreement)
3. Prior work validates each signal separately; combination untested

**Strengths:**
- Clear theoretical basis (complementary failure modes)
- Testable with existing tools and benchmarks
- Immediately deployable if successful

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant AUROC difference between combined metric and best single metric.

**Counter-Arguments:**
1. Signals may be redundant (high correlation eliminates benefit)
2. Optimal weights may be dataset-specific (overfitting)
3. Improvement may be marginal (<2pp) and not practically significant

**Conditions for H0 Support:**
- If entropy and consistency correlation r > 0.8
- If combined AUROC improvement < 2pp and not at ceiling
- If results do not replicate across datasets

### 6.3 Synthesis

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Confirms signals are computable
2. **Independent validation (H-M1, H-M2):** Tests each signal separately
3. **Combination test (H-M3, H-M4):** Tests complementarity

**Possible Outcomes:**
1. **Full Support:** All pass, ≥2pp improvement → Thesis validated
2. **Partial Support:** Improvement <2pp but consistent → Document as marginal
3. **No Support:** H-M1 or H-M2 fail → Signals not predictive individually

### 6.4 Robustness Assessment

| Aspect | Thesis | Antithesis | Resolution |
|--------|--------|------------|------------|
| Existence | Metrics computable | May fail silently | H-E1 test |
| Mechanism | Each signal predictive | May not correlate with correctness | H-M1, H-M2 tests |
| Combination | Complementary | May be redundant | H-M3 correlation check |
| Improvement | ≥2pp gain | Marginal/none | H-M4 multi-dataset test |

**Overall Robustness:** High (clear tests for each component)
**Confidence:** 0.80

---

## 7. Executive Summary

**Main Hypothesis:** Combining entropy + consistency improves hallucination detection by ≥2pp AUROC
- ID: H-EntropyConsistency-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (80% scope reduction from established facts)
- Sub-Hypotheses: 5 total (H-E1, H-M1-4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Signal correlation (R4), semantic similarity reliability (R2)

**Evaluation Scale:**
- TriviaQA: ~11K validation + ~10K test questions
- Natural Questions: ~3K questions
- TruthfulQA: ~817 questions
- Total: ~25K evaluation samples (statistically robust)

**Immediate Action:** Begin Phase 1 with H-E1

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-EntropyConsistency-v1)
- **Scope Reduction:** 80% (4/5 established facts)

### B. Established Facts (BUILD_ON - not re-verified)
1. Token entropy correlates with model uncertainty
2. Semantic clustering improves over token-level entropy
3. Multi-sample consistency detects hallucinations
4. ECE is measurable on QA benchmarks

### C. PROVE_NEW Claim (verification target)
- Combination of entropy and consistency is optimal

---

**Document Status:** Complete
**Generated:** 2026-08-19
**Steps Completed:** step-00 through step-10
