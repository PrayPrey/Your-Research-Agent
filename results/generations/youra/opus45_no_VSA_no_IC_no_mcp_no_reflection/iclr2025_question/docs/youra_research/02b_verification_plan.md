# Verification Plan: Controlled Comparison of UQ Methods for Hallucination Detection

**Date:** 2026-08-29
**Hypothesis ID:** H-UQ-Compare-v1
**Confidence:** 0.75
**Total Hypotheses:** 7

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under decoder-only LLMs (7-13B parameters), if we compare token entropy, semantic entropy, P(True), and SelfCheckGPT on identical TruthfulQA/HaluEval splits, then (1) semantic entropy achieves highest overall AUROC, (2) method rankings vary across hallucination categories, and (3) semantic clustering produces more separable score distributions, because semantic entropy captures meaning-level consistency while token entropy only captures surface-level confidence.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference (>3 AUROC points) between UQ methods for hallucination detection, and method rankings are consistent across all hallucination categories.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + HaluEval (standard) | Standard factuality benchmarks with ground truth labels; no human evaluation needed |
| **Model** | Llama-3-8B-Instruct | Standard open-weight model; representative of 7-13B class |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: truthful_qa, halueval

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Meta-Llama-3-8B-Instruct

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Token Entropy | AUROC ~0.60-0.65 | TruthfulQA |
| Semantic Entropy | AUROC ~0.70-0.75 | Custom QA split |
| Random Baseline | AUROC = 0.5 | Any |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TruthfulQA and HaluEval labels are accurate ground truth | Both benchmarks are peer-reviewed and widely used | AUROC scores would be unreliable |
| A2 | 10 samples per query is sufficient for multi-sample methods | Kuhn 2023 uses 5-10 samples; SelfCheckGPT uses 5-20 | May underestimate multi-sample method performance |
| A3 | Method implementations from public repos are correct | semantic_uncertainty, selfcheckgpt are author-released | Results may not reflect true method performance |
| A4 | HaluEval subtask categories capture meaningful hallucination types | Categories based on task domain (QA, dialogue, summarization) | P2 (category variation) may not reveal hallucination-type patterns |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First controlled head-to-head comparison of four UQ methods on identical benchmark conditions.

**Key Innovation:** Tests whether method rankings vary by hallucination category, suggesting method-type correspondence.

**Differentiation:**
- vs Kuhn 2023: Compared only to token entropy on their own split; we add P(True), SelfCheckGPT on standard benchmarks
- vs Manakul 2023: Evaluated on WikiBio; we test on TruthfulQA/HaluEval with controlled comparison
- vs Kadavath 2022: Evaluated on proprietary data; we replicate on public benchmarks

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | NOT_STARTED |
| h-m2 | MECHANISM | SHOULD_WORK | h-m1 | NOT_STARTED |
| h-m3 | MECHANISM | SHOULD_WORK | h-m2 | NOT_STARTED |
| h-m4 | MECHANISM | SHOULD_WORK | h-m3 | NOT_STARTED |
| h-c1 | CONDITION | SHOULD_WORK | h-m4 | NOT_STARTED |
| h-c2 | CONDITION | SHOULD_WORK | h-m4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: UQ Methods Detect Hallucinations

**Type:** EXISTENCE
**Statement:** Under decoder-only LLMs, if we compute UQ scores for LLM outputs, then at least one method achieves AUROC > 0.55 on hallucination detection, because uncertainty signals correlate with output quality.

**Variables:**
- IV: UQ Method (token_entropy, semantic_entropy, p_true, selfcheckgpt)
- DV: AUROC for hallucination detection
- CV: LLM Model (Llama-3-8B), Sample Budget (10), Benchmark Splits

**Success Criteria:**
- Primary: At least one UQ method achieves AUROC > 0.55
- Secondary: All methods produce non-random uncertainty scores

**Gate:**
- Type: MUST_WORK
- If Fail: STOP - UQ methods do not work for hallucination detection

**Dependencies:** None

**Source:** Phase 2A SH1 (Existence)

---

#### H-M1: LLM Generates Variable Confidence Outputs

**Type:** MECHANISM
**Statement:** Under standard decoding, if LLM generates responses to factual queries, then output confidence (measured by logit entropy) varies meaningfully across queries, because model uncertainty reflects knowledge gaps.

**Variables:**
- IV: Query type/difficulty
- DV: Logit entropy distribution
- CV: Model, decoding parameters

**Success Criteria:**
- Primary: Entropy variance > 0 across queries
- Secondary: Entropy correlates with query difficulty

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT to different confidence measure

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: UQ Methods Extract Uncertainty Signals

**Type:** MECHANISM
**Statement:** Under multiple UQ methods, if we apply each method to LLM outputs, then each produces distinct uncertainty scores, because methods use different algorithmic approaches (logits vs. samples vs. NLI).

**Variables:**
- IV: UQ Method algorithm
- DV: Score distribution characteristics
- CV: LLM outputs, query set

**Success Criteria:**
- Primary: Score distributions differ between methods (KS test p < 0.05)
- Secondary: Methods capture different aspects of uncertainty

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document method overlap, proceed

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Uncertainty Correlates with Hallucination Status

**Type:** MECHANISM
**Statement:** Under computed UQ scores, if we correlate scores with ground truth hallucination labels, then correlation is negative (higher uncertainty = more hallucination), because uncertainty reflects output unreliability.

**Variables:**
- IV: UQ score
- DV: Hallucination status (binary)
- CV: Dataset, model

**Success Criteria:**
- Primary: Point-biserial correlation < 0 for at least one method
- Secondary: AUROC > 0.5 confirms direction

**Gate:**
- Type: SHOULD_WORK
- If Fail: Check score polarity, document limitation

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Semantic Entropy Captures Meaning-Level Consistency

**Type:** MECHANISM
**Statement:** Under semantic entropy vs token entropy comparison, if we compare score distributions, then semantic entropy produces more separable distributions (higher KL divergence between correct/hallucinated), because semantic clustering captures meaning beyond surface tokens.

**Variables:**
- IV: Entropy type (semantic vs token)
- DV: KL divergence between P(score|correct) and P(score|hallucinated)
- CV: Same outputs, same model

**Success Criteria:**
- Primary: KL_semantic > KL_token
- Secondary: Semantic entropy AUROC > Token entropy AUROC

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document that semantic clustering adds no benefit

**Dependencies:** H-M3

**Source:** Phase 2A Key Tension + P3

---

#### H-C1: Semantic Entropy Achieves Target Performance

**Type:** CONDITION
**Statement:** Under TruthfulQA mc1 evaluation, if semantic entropy is applied to Llama-3-8B outputs, then AUROC ≥ 0.70 AND outperforms token entropy by ≥ 3 points, because meaning-level consistency is stronger than token-level confidence for factuality.

**Variables:**
- IV: Semantic entropy implementation
- DV: AUROC on TruthfulQA mc1
- CV: Model, sample count

**Success Criteria:**
- Primary: Semantic entropy AUROC ≥ 0.70
- Secondary: (Semantic AUROC - Token AUROC) ≥ 0.03

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document actual performance, analyze gap

**Dependencies:** H-M4

**Source:** Phase 2A Prediction P1

---

#### H-C2: Method Rankings Vary by Category

**Type:** CONDITION
**Statement:** Under HaluEval subtask evaluation, if we rank methods by AUROC within each category (QA, dialogue, summarization), then different methods rank #1 in at least 2 of 3 categories, because hallucination types differ by task domain.

**Variables:**
- IV: HaluEval subtask category
- DV: Method rankings by AUROC
- CV: Model, sample count

**Success Criteria:**
- Primary: Different #1 method in at least 2/3 categories
- Secondary: No single method dominates all categories by >3 points

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document that one method dominates uniformly

**Dependencies:** H-M4

**Source:** Phase 2A Prediction P2

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
                                  ↘ H-C2
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC > 0.55 for any method | STOP, reassess |
| H-M1 | MUST_WORK | Entropy variance > 0 | PIVOT measure |
| H-M2 | SHOULD_WORK | KS test p < 0.05 | Document, proceed |
| H-M3 | SHOULD_WORK | Correlation < 0 | Check polarity |
| H-M4 | SHOULD_WORK | KL_semantic > KL_token | Document finding |
| H-C1 | SHOULD_WORK | AUROC ≥ 0.70, gap ≥ 0.03 | Analyze gap |
| H-C2 | SHOULD_WORK | 2/3 different winners | Document pattern |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Foundation | H-E1 | 2 weeks |
| Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |
| Conditions | H-C1, H-C2 | 2 weeks |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Benchmark labels inaccurate | A1 | High | All | Use only high-agreement subsets |
| R2 | Sample budget insufficient | A2 | Medium | H-M4, H-C1 | Test sensitivity to sample count |
| R3 | Implementation bugs | A3 | Medium | All | Unit test against paper results |
| R4 | Categories not meaningful | A4 | Low | H-C2 | Report per-category regardless |

### 4.2 Mitigation Strategies

**R1 (Label Quality):**
- Prevention: Use only TruthfulQA mc1 (highest agreement)
- Detection: Check inter-annotator agreement metrics
- Response: Report results on high-confidence subset separately

**R2 (Sample Budget):**
- Prevention: Run ablation on sample count (5, 10, 20)
- Detection: Check if performance plateaus
- Response: Report optimal sample count

**R3 (Implementation):**
- Prevention: Unit test each method on paper examples
- Detection: Compare our baseline to reported baselines
- Response: Debug, re-run if discrepancy > 2 points

**R4 (Category Meaning):**
- Prevention: Report all per-category results
- Detection: Check if category patterns make semantic sense
- Response: Interpret as task-type variation, not hallucination-type

---

## 5. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 7 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - MUST_WORK)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 (Confidence variance - MUST_WORK)
         │
         ▼
    H-M2 (Signal extraction - SHOULD_WORK)
         │
         ▼
    H-M3 (Correlation direction - SHOULD_WORK)
         │
         ▼
    H-M4 (Semantic vs token - SHOULD_WORK)
         │
    ┌────┴────┐
    ▼         ▼
[Level 5 - Conditions]
   H-C1      H-C2
(Target)   (Categories)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1/H-C2
═══════════════════════════════════════════════════════════
```

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 7 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3 │ W4 │ W5 │ W6 │ W7-8 │
─────────────────┼──────┼────┼────┼────┼────┼──────┤
PHASE 1: Foundation
  H-E1           │██████│    │    │    │    │      │
  [Gate 1]       │    ◆│    │    │    │    │      │
─────────────────┼──────┼────┼────┼────┼────┼──────┤
PHASE 2: Mechanisms
  H-M1           │      │████│    │    │    │      │
  H-M2           │      │    │████│    │    │      │
  H-M3           │      │    │    │████│    │      │
  H-M4           │      │    │    │    │████│      │
  [Gate 2]       │      │    │    │    │   ◆│      │
─────────────────┼──────┼────┼────┼────┼────┼──────┤
PHASE 3: Conditions
  H-C1           │      │    │    │    │    │██████│
  H-C2           │      │    │    │    │    │██████│
  [Gate 3]       │      │    │    │    │    │    ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Semantic entropy achieves highest AUROC because meaning-level clustering captures consistency better than surface-level metrics.

**Supporting Evidence:**
1. Kuhn 2023 showed semantic entropy beats token entropy on their split
2. SelfCheckGPT works via self-consistency (similar principle)
3. P(True) probes model's own confidence (different approach)

**Strengths:**
- Clear causal mechanism (meaning > surface)
- Testable with standard metrics (AUROC)
- Builds on established methods

### 6.2 Antithesis (H0)

**Null Position:** All UQ methods perform similarly (<3 point AUROC difference) because they all capture the same underlying signal: model confidence.

**Counter-Arguments:**
1. Methods may be highly correlated despite algorithmic differences
2. Benchmark labels may not distinguish fine-grained hallucination types
3. Sample budget may favor simpler methods (token entropy)

**Conditions for H0 Support:**
- All methods within 3 AUROC points
- Same method ranks #1 in all HaluEval categories
- KL_semantic ≤ KL_token

### 6.3 Synthesis

The verification plan addresses this dialectic through sequential testing:

1. **H-E1** establishes baseline: If no method works (AUROC ~0.5), both thesis and antithesis are moot
2. **H-M1-4** test mechanism: If semantic entropy shows no advantage at component level, H0 gains support
3. **H-C1-2** test predictions: Final arbitration between thesis (different methods excel differently) and antithesis (uniform performance)

**Resolution:** Data will determine. Plan designed to detect both outcomes fairly.

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Methods detect hallucinations | May be random | H-E1 AUROC > 0.55 |
| Mechanism | Semantic > token | Same signal | H-M4 KL comparison |
| Category | Methods differ by type | Uniform ranking | H-C2 ranking test |
| Performance | ≥0.70 AUROC | <0.70 | H-C1 threshold |

**Overall Robustness:** Medium - well-designed tests but single model/dataset combo

---

## 7. Executive Summary

**Main Hypothesis:** H-UQ-Compare-v1 (Confidence: 0.75)
- Semantic entropy achieves highest AUROC for hallucination detection

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 7 total (H-E: 1, H-M: 4, H-C: 2)
- Phases: 3 phases over 8 weeks
- Critical Gates: 3 decision points

**Risk Assessment:** Medium
- Primary concerns: Label quality (R1), implementation correctness (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (existence verification)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-UQ-Compare-v1)
- **Scope Reduction:** 40% (BUILD_ON claims excluded)

### B. Established Facts (BUILD_ON)
- Semantic entropy outperforms token entropy on Kuhn et al.'s test set
- SelfCheckGPT detects hallucinations via self-consistency
- P(True) provides calibrated uncertainty for LLMs

### C. PROVE_NEW Claims (Verification Targets)
- No controlled head-to-head comparison exists
- Different UQ methods detect different hallucination types
