# Verification Plan: Entropy vs. Consistency Hallucination Detection

**Date:** 2026-08-28
**Hypothesis ID:** H-EntropyConsistency-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under closed-book QA conditions (TruthfulQA), if we compute both token-level entropy and N-sample consistency for each LLM response, then a hybrid detector combining both signals will outperform either method alone by ≥3 percentage points AUROC, because the methods capture orthogonal failure modes — entropy reflects epistemic uncertainty while consistency reflects generation stability.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in hallucination detection performance between a hybrid entropy+consistency detector and the best single-method detector (AUROC improvement < 3 percentage points).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | Provides ground truth factuality labels for closed-book QA, exactly what hypothesis requires |
| **Model** | LLaMA-2-7B | Publicly available model with accessible logits for entropy computation |

**Dataset Details:**
- Source: Lin et al. 2022
- Path: sylinrl/TruthfulQA

**Model Details:**
- Type: decoder-only autoregressive LLM
- Source: meta-llama/llama

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Token Entropy Only | AUROC ~0.60-0.70 estimated | Various NLG benchmarks |
| SelfCheckGPT Consistency | AUROC ~0.65-0.75 | WikiBio generation |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TruthfulQA ground truth labels are reliable | Benchmark widely used (~500 citations) | All AUROC measurements unreliable |
| A2 | Token entropy is valid proxy for model uncertainty | Standard in UQ literature | Entropy predictions invalid |
| A3 | Embedding cosine similarity captures semantic consistency | SelfCheckGPT validated | Consistency scores invalid |
| A4 | LLaMA-2-7B behavior generalizes to other models | Partial evidence | Findings limited to LLaMA-2-7B |
| A5 | N=5 samples sufficient for consistency estimation | SelfCheckGPT used similar | Estimates may be noisy |

### 1.6 Research Gap & Novelty

**Gap:** Entropy and consistency methods have never been systematically compared on the same factuality benchmark. Prior work evaluated each method in isolation on different tasks.

**Novelty:** First head-to-head comparison of entropy vs. consistency methods on TruthfulQA. Tests the orthogonality hypothesis — that these methods capture different failure modes and provide additive value when combined.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M2 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M3 | MECHANISM | MUST_WORK | H-M1, H-M2 | READY |

---

### 2.2 Hypothesis Specifications

#### H-E1: Individual Method Predictive Validity

**Statement**: Under closed-book QA conditions (TruthfulQA), if we compute token entropy and N-sample consistency for LLM responses, then both methods individually predict factual correctness above chance (AUROC > 0.5), because each captures a distinct uncertainty signal.

**Rationale**: This existence hypothesis validates that both uncertainty quantification methods work before testing their combination. Without individual predictive validity, combining them would be meaningless.

**Variables**:
- Independent: UQ method (token_entropy | consistency)
- Dependent: Hallucination detection AUROC
- Controlled: Model (LLaMA-2-7B), Dataset (TruthfulQA), N=5 samples

**Verification Protocol**:
1. Compute mean token entropy for each TruthfulQA response from logits
2. Compute N=5 sample consistency via embedding cosine similarity
3. Calculate AUROC for each method against ground truth labels
4. Verify both methods exceed chance level (AUROC > 0.5)

**Success Criteria** (PoC: Direction-based):
- Primary: Both entropy_AUROC > 0.5 AND consistency_AUROC > 0.5
- Secondary: Individual AUROC > 0.55 (meaningful effect)

**Failure Response**:
- IF fails: ABANDON — fundamental assumption violated

**Dependencies**: None

**Source**: Phase 2A sh1_existence, Prediction P1

---

#### H-M1: Entropy-Uncertainty Link

**Statement**: Under closed-book QA conditions, if model lacks knowledge about an answer, then token entropy is elevated because the logit distribution becomes diffuse when the model is uncertain.

**Rationale**: Validates the first causal step — that entropy reflects epistemic uncertainty. This mechanism underpins why entropy should predict hallucination.

**Variables**:
- Independent: Model knowledge state (known vs. unknown facts)
- Dependent: Mean token entropy
- Controlled: Model, dataset, temperature

**Verification Protocol**:
1. Partition TruthfulQA into correct vs. incorrect model responses
2. Compute mean token entropy for each partition
3. Compare entropy distributions between partitions
4. Verify higher entropy correlates with incorrect (hallucinated) responses

**Success Criteria** (PoC: Direction-based):
- Primary: Mean entropy (incorrect) > Mean entropy (correct)
- Secondary: Effect size d > 0.2 (small but detectable)

**Failure Response**:
- IF fails: PIVOT — entropy may need different aggregation

**Dependencies**: H-E1

**Source**: Phase 2A causal_mechanism step 1

---

#### H-M2: Consistency-Stability Link

**Statement**: Under closed-book QA conditions, if the model's generation process is unstable for a question, then N-sample consistency is low because different sampling runs yield semantically divergent answers.

**Rationale**: Validates the second causal step — that consistency reflects generation stability. Unstable generation indicates the model is not confident in its response.

**Variables**:
- Independent: Response correctness (correct vs. hallucinated)
- Dependent: N-sample consistency score
- Controlled: Model, dataset, N=5, temperature

**Verification Protocol**:
1. Generate N=5 responses per TruthfulQA question
2. Compute pairwise embedding cosine similarity
3. Calculate mean consistency per question
4. Verify lower consistency correlates with incorrect responses

**Success Criteria** (PoC: Direction-based):
- Primary: Mean consistency (incorrect) < Mean consistency (correct)
- Secondary: Effect size d > 0.2

**Failure Response**:
- IF fails: PIVOT — consistency metric may need refinement

**Dependencies**: H-E1

**Source**: Phase 2A causal_mechanism step 2

---

#### H-M3: Orthogonal Signals Enable Complementary Detection

**Statement**: Under closed-book QA conditions, if entropy and consistency capture different failure modes, then their correlation is low (r < 0.3) and discordant cases (where methods disagree) show differential predictive value.

**Rationale**: Validates the core orthogonality hypothesis — that the two methods are not redundant. If they capture the same signal, combining them adds no value.

**Variables**:
- Independent: Uncertainty signal type (entropy vs. consistency)
- Dependent: Pearson correlation, discordant case proportion
- Controlled: Model, dataset

**Verification Protocol**:
1. Compute entropy and consistency scores for all questions
2. Calculate Pearson correlation between scores
3. Identify discordant cases (rank difference > 50 percentile points)
4. Verify discordant proportion > 15% and each method wins on its subset

**Success Criteria** (PoC: Direction-based):
- Primary: correlation(entropy, consistency) < 0.3
- Secondary: Discordant proportion > 0.15 AND winning-method AUROC > 0.6 per subset

**Failure Response**:
- IF fails: EXPLORE — signals may be orthogonal only for subset of questions

**Dependencies**: H-M1, H-M2

**Source**: Phase 2A causal_mechanism step 3, Prediction P2, P3

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

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
       ↑       ↑
       └───────┘ (H-M1, H-M2 feed into H-M3)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Both AUROC > 0.5 | ABANDON |
| H-M1 | MUST_WORK | Entropy higher for incorrect | PIVOT to semantic entropy |
| H-M2 | MUST_WORK | Consistency lower for incorrect | PIVOT to alternative metric |
| H-M3 | MUST_WORK | r < 0.3, discordant > 15% | EXPLORE subset analysis |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 1-2 days |
| Phase 2: Mechanism | H-M1, H-M2, H-M3 | 3-5 days |

**Total Duration:** 4-7 days (PoC verification)

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source | Description | Severity |
|----|------|--------|-------------|----------|
| R1 | Ground Truth Unreliability | A1 | TruthfulQA labels may have errors or ambiguity | Medium |
| R2 | Entropy-Uncertainty Disconnect | A2 | Token entropy may not reflect actual model uncertainty | High |
| R3 | Embedding Similarity Failure | A3 | Cosine similarity may not capture semantic consistency | High |
| R4 | Model-Specific Results | A4 | Findings may not generalize beyond LLaMA-2-7B | Medium |
| R5 | Sample Size Insufficiency | A5 | N=5 may yield noisy consistency estimates | Low |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1, H-M1, H-M2, H-M3 | All AUROC measurements become unreliable |
| R2 | H-E1 (entropy), H-M1 | Entropy-based predictions fail |
| R3 | H-E1 (consistency), H-M2 | Consistency-based predictions fail |
| R4 | All (generalizability) | Results limited in scope, not fatal |
| R5 | H-M2, H-M3 | Consistency estimates noisy, effect sizes reduced |

### 4.3 Mitigation Strategies

**R1: Ground Truth Unreliability**
- **Prevention:** Use only high-agreement subset of TruthfulQA
- **Detection:** Check inter-annotator agreement scores where available
- **Response:** If questionable, use GPT-4 judge as secondary validation

**R2: Entropy-Uncertainty Disconnect**
- **Prevention:** Test multiple entropy aggregations (mean, max, weighted)
- **Detection:** Sanity check: entropy should be higher for wrong answers
- **Response:** PIVOT to semantic entropy (Kuhn et al. method) if token entropy fails

**R3: Embedding Similarity Failure**
- **Prevention:** Use validated embedding model (e.g., sentence-transformers)
- **Detection:** Manual inspection of low-consistency examples
- **Response:** PIVOT to BERTScore or ROUGE-based consistency

**R4: Model-Specific Results**
- **Prevention:** Document as scope limitation upfront
- **Detection:** N/A (inherent to single-model study)
- **Response:** SCOPE: Acknowledge limitation, suggest multi-model follow-up

**R5: Sample Size Insufficiency**
- **Prevention:** Run variance analysis on N=5 vs N=10 subset
- **Detection:** Check confidence intervals on consistency scores
- **Response:** Increase to N=10 if variance is unacceptable

### 4.4 Risk Summary

| ID | Risk | Severity | Likelihood | Overall | Mitigation Ready |
|----|------|----------|------------|---------|------------------|
| R1 | Ground truth issues | Medium | Low | Low | Yes |
| R2 | Entropy disconnect | High | Medium | High | Yes (pivot) |
| R3 | Similarity failure | High | Low | Medium | Yes (pivot) |
| R4 | Model-specific | Medium | High | Medium | Yes (scope) |
| R5 | Sample size | Low | Medium | Low | Yes |

**Summary:** Critical: 0 | High: 1 | Medium: 2 | Low: 2

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────┐
    │  H-E1: Individual Method        │
    │  Predictive Validity            │
    │  Gate: MUST_WORK                │
    └───────────────┬─────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
[Level 1 - Independent Mechanisms]
┌─────────────────────┐  ┌─────────────────────┐
│  H-M1: Entropy-     │  │  H-M2: Consistency- │
│  Uncertainty Link   │  │  Stability Link     │
│  Gate: MUST_WORK    │  │  Gate: MUST_WORK    │
└─────────┬───────────┘  └───────────┬─────────┘
          │                          │
          └────────────┬─────────────┘
                       ▼
[Level 2 - Integration]
    ┌─────────────────────────────────┐
    │  H-M3: Orthogonal Signals       │
    │  Enable Complementary Detection │
    │  Gate: MUST_WORK                │
    └─────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1/H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 1 | H-M2 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M3 | H-M1, H-M2 | MUST_WORK | Integration |

**Note:** H-M1 and H-M2 are at same level (parallel opportunity), both required for H-M3.

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════
GANTT TIMELINE - PoC Verification (4-7 days)
═══════════════════════════════════════════════════════════

Day:    1    2    3    4    5    6    7
        │    │    │    │    │    │    │
H-E1    ████████░░░░░░░░░░░░░░░░░░░░░░░
        [Foundation: 1-2 days]
              │
              ▼ Gate 1
H-M1    ░░░░░░████████░░░░░░░░░░░░░░░░░
        [Entropy mechanism: 2 days]
              │
H-M2    ░░░░░░████████░░░░░░░░░░░░░░░░░
        [Consistency mechanism: 2 days]
        (parallel with H-M1)
                    │
                    ▼ Gate 2
H-M3    ░░░░░░░░░░░░░░████████████░░░░░
        [Integration: 2-3 days]
                              │
                              ▼ Complete

═══════════════════════════════════════════════════════════
Legend: ████ Active  ░░░░ Waiting
═══════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1/H-M2 → H-M3

| Segment | Duration | Slack | Critical? |
|---------|----------|-------|-----------|
| H-E1 | 1-2 days | 0 | Yes |
| H-M1 | 2 days | 0 | Yes (tied) |
| H-M2 | 2 days | 0 | Yes (tied) |
| H-M3 | 2-3 days | 0 | Yes |

**Parallel Opportunity:** H-M1 and H-M2 can run simultaneously after H-E1 passes.

### 5.5 Resource Summary

| Resource | H-E1 | H-M1 | H-M2 | H-M3 |
|----------|------|------|------|------|
| GPU hours | 2-4 | 1-2 | 4-6 | 1-2 |
| LLaMA-2-7B | ✓ | ✓ | ✓ | ✓ |
| TruthfulQA | ✓ | ✓ | ✓ | ✓ |
| N=5 samples | - | - | ✓ | ✓ |

**Total GPU:** 8-14 hours estimated

### 5.6 Execution Order

1. **H-E1** (Foundation) — Validate both methods work individually
2. **H-M1 || H-M2** (Parallel) — Test entropy and consistency mechanisms
3. **H-M3** (Integration) — Verify orthogonality and complementary value

**Gates:**
- Gate 1 (after H-E1): Both AUROC > 0.5 → proceed
- Gate 2 (after H-M1/M2): Mechanisms validated → proceed to integration
- Final: All gates passed → proceed to Phase 5 baseline comparison

---

## 6. Dialectical Analysis

### 6.1 Overview

This section evaluates the hypothesis through thesis-antithesis-synthesis dialectic, using the null hypothesis (H0) from Phase 2A as the foundation for opposing arguments.

### 6.2 Thesis Statement

**Core Claim:** A hybrid detector combining token entropy and N-sample consistency outperforms single-method detectors by ≥3 percentage points AUROC because the methods capture orthogonal failure modes.

**Supporting Evidence:**
1. Token entropy correlates with model uncertainty (Kadavath et al. 2022)
2. N-sample consistency detects generation instability (Manakul et al. 2023)
3. The two signals should capture different phenomena — epistemic uncertainty vs. generation stability

**Strengths:**
- Both component methods have prior validation in isolation
- Clear mechanistic hypothesis (orthogonality)
- Quantitative success criteria (≥3pp AUROC improvement)

**Expected Outcomes:**
- Primary: Hybrid AUROC ≥ max(entropy, consistency) + 0.03
- Secondary: Correlation(entropy, consistency) < 0.3
- Tertiary: Discordant cases >15% with differential predictive value

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in hallucination detection performance between a hybrid entropy+consistency detector and the best single-method detector (AUROC improvement < 3 percentage points).

**Counter-Arguments:**
1. **Redundancy:** Entropy and consistency may capture the same underlying uncertainty signal, making combination redundant
2. **Noise amplification:** Combining two noisy signals may not improve prediction
3. **Domain mismatch:** Prior work validated methods on different tasks — may not transfer to TruthfulQA

**Potential Failure Points:**
- R2: Entropy may not reflect uncertainty for factuality tasks
- R3: Embedding similarity may miss semantic consistency
- Methods may be correlated (r > 0.7), negating orthogonality claim

**Conditions Under Which H0 Would Be Supported:**
- Hybrid AUROC improvement < 0.03 over best single method
- Correlation between entropy and consistency > 0.3
- Discordant cases < 15% (methods agree, no complementary value)

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-EntropyConsistency-v1 presents a testable claim that combining two uncertainty signals improves hallucination detection. However, the null hypothesis raises valid concerns about potential redundancy and domain transfer.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **H-E1 (Foundation):** First verify both methods individually predict factual correctness — if either fails, orthogonality is moot
2. **H-M1/H-M2 (Mechanism):** Test each signal's mechanism independently before assuming complementarity
3. **H-M3 (Integration):** Directly test orthogonality claim via correlation and discordant case analysis

**Conditions for Thesis Support:**
- H-E1 passes: Both methods individually predict above chance
- H-M3 passes: Correlation < 0.3, discordant cases show differential value
- Phase 5: Hybrid outperforms by ≥3pp AUROC

**Conditions for Antithesis Support:**
- H-E1 fails: One or both methods don't predict factual correctness
- H-M3 fails: Correlation > 0.3 (signals redundant)
- Phase 5: Improvement < 3pp

**Nuanced Outcome Possibilities:**
1. **Full Support:** All pass → Orthogonality validated, hybrid effective
2. **Partial Support:** Weak orthogonality (0.3 < r < 0.5) → Modest improvement possible
3. **No Support:** High correlation or single-method dominance → Antithesis supported

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Both methods predict factuality | May fail on TruthfulQA | H-E1 test |
| Mechanism | Entropy=uncertainty, Consistency=stability | May measure same thing | H-M1, H-M2 tests |
| Orthogonality | r < 0.3, distinct failure modes | May be correlated | H-M3 correlation test |
| Performance | ≥3pp AUROC improvement | Marginal or no improvement | Phase 5 comparison |

**Overall Robustness Score:** Medium

The verification plan is robust — it tests existence before mechanism, mechanism before integration, and includes clear falsification criteria at each gate. However, the orthogonality hypothesis is speculative until tested.

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Hybrid entropy+consistency detector outperforms single methods by ≥3pp AUROC
- ID: H-EntropyConsistency-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 4-7 days
- Critical Gates: 3 decision points (MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: Entropy-uncertainty disconnect (R2), embedding similarity failure (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (validate both methods individually)

### 7.2 Final Summary

**Verification Execution Order:**

**Phase 1: Foundation** (1-2 days)
- H-E1: Both methods predict factuality above chance
- Gate 1: MUST PASS — if fails, ABANDON

**Phase 2: Mechanisms** (3-5 days)
- H-M1: Entropy reflects uncertainty (higher for incorrect responses)
- H-M2: Consistency reflects stability (lower for incorrect responses)
- H-M3: Orthogonality (r<0.3, discordant >15%)
- Gate 2: All MUST_WORK

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL: STOP, hypothesis invalid
   - PASS: Proceed to Phase 2

2. **Gate 2 (Mechanisms):**
   - H-M1 FAIL: PIVOT to semantic entropy
   - H-M2 FAIL: PIVOT to alternative consistency metric
   - H-M3 FAIL: EXPLORE subset analysis

### 7.3 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases defined
- H0 addressed: No significant hybrid improvement vs. best single method
- 60% scope reduction from Phase 2A established facts

**Open Questions:**
- Optimal weighting for hybrid combination
- Whether semantic entropy outperforms token entropy
- Generalization to larger models (13B, 70B)

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up TruthfulQA evaluation pipeline

2. **Resource Allocation:**
   - Allocate 4-7 days for PoC verification
   - 8-14 GPU hours estimated

3. **Failure Management:**
   - PIVOT strategies defined for each hypothesis
   - Document all findings regardless of outcome

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-EntropyConsistency-v1)

**B. Workflow Summary**
- Total hypotheses: 4 (H-E1, H-M1, H-M2, H-M3)
- MCP calls: 0 (ablation mode)
- Scope reduction: 60%

---

## 8. State Generation

### 8.1 Verification State Status

✅ verification_state.yaml generated with 4 sub-hypotheses:
- h-e1: EXISTENCE (READY)
- h-m1: MECHANISM (NOT_STARTED, prereq: h-e1)
- h-m2: MECHANISM (NOT_STARTED, prereq: h-e1)
- h-m3: MECHANISM (NOT_STARTED, prereq: h-m1, h-m2)

### 8.2 Pipeline Tasks Updated

- Phase 2B: COMPLETE
- Phase 2C: READY (next phase)

### 8.3 Hypothesis Tasks Created

| Hypothesis | Type | Gate | Status |
|------------|------|------|--------|
| H-E1 | EXISTENCE | MUST_WORK | READY |
| H-M1 | MECHANISM | MUST_WORK | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | NOT_STARTED |

---

**Phase 2B Complete** | Generated: 2026-08-28
