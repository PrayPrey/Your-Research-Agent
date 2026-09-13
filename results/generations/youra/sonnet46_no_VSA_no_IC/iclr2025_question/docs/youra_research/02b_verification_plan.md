---
hypothesis_id: H-TokenAgg-v1
confidence_level: 0.75
total_hypothesis_count: 4
research_mode: incremental
scope_reduction_percentage: 60
causal_chain_count: 3
condition_hypothesis_count: 0
include_condition_hypotheses: false
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
status: in_progress
---

# Verification Plan: Token-Level Aggregation Function Ablation for Hallucination Detection

**Date:** 2026-08-21
**Hypothesis ID:** H-TokenAgg-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under frozen open-weight LLMs (LLaMA-2-7B, Mistral-7B-v0.1) evaluated on existing factual QA benchmarks with binary correctness labels (Farquhar 2023 splits for TriviaQA/NQ; standard TruthfulQA generation subset), if we vary only the token-level log-probability aggregation function (min, mean, raw-sum) applied to single-forward-pass output probabilities, then the AUROC for hallucination detection will differ significantly across aggregation functions in a benchmark-type-dependent pattern: min log-prob achieves AUROC ≥ mean log-prob on factual recall benchmarks (TriviaQA, NQ) by ≥ 0.02, while mean log-prob achieves AUROC ≥ min log-prob on imitative-falsehood benchmarks (TruthfulQA) by ≥ 0.02, because hallucination signal concentrates at the single most uncertain fact-token in recall failures but is distributed uniformly across all tokens in imitative falsehoods.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AUROC between min log-prob, mean log-prob, and raw-sum log-prob aggregation functions across TriviaQA, NQ, and TruthfulQA benchmark splits; any observed AUROC differences are within bootstrap 95% confidence intervals and do not exceed 0.02 in either direction.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA + NQ + TruthfulQA (+ SciQ exploratory) [standard] | TriviaQA/NQ = Type B recall failures; TruthfulQA = Type A imitative falsehoods — directly tests core prediction |
| **Model** | LLaMA-2-7B + Mistral-7B-v0.1 | Open-weight models with full logprob access; 7B GPU-accessible (16GB VRAM); two distinct families for replication |

**Dataset Details:**
- Source: Farquhar et al. 2023 splits (jlko/semantic_uncertainty repo) for TriviaQA/NQ; standard HuggingFace splits for TruthfulQA generation and SciQ
- Path: jlko/semantic_uncertainty data splits; HuggingFace datasets: truthful_qa (generation), sciq

**Model Details:**
- Type: Open-weight decoder-only language model
- Source: HuggingFace model hub: meta-llama/Llama-2-7b-hf, mistralai/Mistral-7B-v0.1

### 1.4 Baseline Methods (for comparison context)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Farquhar 2023) | AUROC ~0.79 on TriviaQA | TriviaQA (Farquhar 2023 splits) |
| SelfCheckGPT NLI (Manakul 2023) | AUROC ~0.72-0.78 on WikiBio | WikiBio |
| CCP mean aggregation (Fadeeva 2024) | AUROC ~0.72-0.80 on TriviaQA/NQ | TriviaQA, NQ (7 models) |
| Predictive entropy (sum, Farquhar 2023) | AUROC ~0.72 on TriviaQA | TriviaQA (Farquhar 2023 splits) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TruthfulQA@7B exhibits imitative-falsehood pattern (flat high-prob wrong answers) | TruthfulQA inverse scaling (Lin 2021); hallucinations designed to match human misconceptions | P2 (mean > min on TruthfulQA) would not hold; TruthfulQA joins factual-recall group |
| A2 | TriviaQA/NQ@7B exhibit recall-failure pattern (peaked uncertainty at specific fact-token) | Farquhar 2023: SE outperforms predictive entropy (sum); consistent with concentrated semantic uncertainty | P1 (min > mean on TriviaQA/NQ) would not hold; hypothesis direction collapses |
| A3 | Token log-probs from greedy decoding are representative of model uncertainty | Standard assumption in white-box UQ literature; Fadeeva 2024, Moslonka 2025 use single-forward-pass logprobs | Greedy log-probs might not reflect true uncertainty; sampling-based estimates required |
| A4 | Exact-match/F1 labels from Farquhar 2023 provide sufficiently clean binary hallucination labels | Farquhar 2023 achieves AUROC ~0.79 with same labels; sufficient signal exists | Label noise ceiling limits AUROC; but relative comparisons between aggregation functions remain valid |
| A5 | lm-polygraph implements min, mean, raw-sum as distinct estimators on LLaMA-2-7B and Mistral-7B-v0.1 | lm-polygraph docs: token_entropy, token_prob, max_token_entropy listed; Mistral and LLaMA-2 supported | Minor implementation work needed; does not invalidate hypothesis |

### 1.6 Research Gap & Novelty

**Gap:** No study has ablated max vs. mean vs. sum token log-prob aggregation in isolation on fixed factual QA splits. Fadeeva 2024 uses mean implicitly; Farquhar 2023 uses sum within semantic clusters; no directional predictions grounded in hallucination taxonomy.

**Novelty:** First paper to isolate token-level log-probability aggregation function as sole experimental variable, with benchmark-type-dependent directional predictions grounded in hallucination taxonomy (Type A imitative vs. Type B recall failure). Scope reduction 60%: claims 1-3 established (BUILD_ON), claims 4-5 novel (PROVE_NEW).

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
**H-E1: Aggregation Function Choice Produces Measurably Different AUROC**

**Statement**: Under frozen open-weight LLMs (LLaMA-2-7B, Mistral-7B-v0.1) with single greedy forward pass, if we vary only the token-level log-probability aggregation function (min, mean, raw-sum) on factual QA benchmarks (TriviaQA, NQ, TruthfulQA; Farquhar 2023 splits), then AUROC for hallucination detection will differ by ≥ 0.02 between at least one pair of aggregation functions on at least one benchmark, because different aggregation functions have different mathematical sensitivities to token-level uncertainty distributions.

**Rationale**: This establishes the existence claim — that aggregation function choice is not arbitrary. Without this, mechanism testing (H-M1-3) is moot. It tests PROVE_NEW claim 4 from Phase 2A directly.

**Variables**:
- Independent: Aggregation function (min / mean / raw-sum)
- Dependent: AUROC for hallucination detection
- Controlled: Frozen LLM weights, Farquhar 2023 splits, greedy decoding, exact-match/F1 labels

**Verification Protocol**:
1. Load frozen LLaMA-2-7B and Mistral-7B-v0.1; run single greedy forward pass on all test samples from TriviaQA, NQ, TruthfulQA (full standard test splits, ≥500 samples each per Farquhar 2023).
2. Apply min, mean, raw-sum aggregation to token log-prob sequences; compute AUROC against binary correctness labels.
3. Bootstrap 95% CI (n=1000) on pairwise AUROC differences across all aggregation function pairs and benchmarks.
4. Confirm at least one AUROC difference ≥ 0.02 with CI lower bound > 0.

**Success Criteria**:
- Primary: At least one pair (min, mean, raw-sum) shows AUROC difference ≥ 0.02 with non-overlapping bootstrap 95% CI on at least one benchmark for at least one model
- Secondary: Effect replicates on both models (LLaMA-2-7B and Mistral-7B-v0.1)

**Failure Response**:
- IF fails: PIVOT — investigate whether label noise ceiling (A4) or lm-polygraph implementation issue (A5) is responsible; if both models show < 0.01 differences across all benchmarks, ABANDON — hypothesis collapses to H0

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 SH1; PROVE_NEW Claim 4

---

---
**H-M1: Recall-Failure Hallucinations Produce Peaked Token Uncertainty Distributions**

**Statement**: Under frozen LLMs (LLaMA-2-7B, Mistral-7B-v0.1) generating hallucinated answers on TriviaQA and NQ (recall-failure benchmarks), if we analyze token log-probability sequences, then hallucinated answers will show a significantly higher peakedness ratio (max log-prob / mean log-prob) than correct answers, because recall failures manifest as a single unknown fact-token surrounded by high-probability function words.

**Rationale**: This is the first causal step: hallucination type determines token distribution shape. Without this, the mechanism hypothesis (that min is optimal for recall failures) lacks causal foundation. Directly tests PROVE_NEW claim 5 partially.

**Variables**:
- Independent: Answer correctness (hallucinated vs. correct) × Benchmark type (TriviaQA/NQ)
- Dependent: Token distribution peakedness (max log-prob / mean log-prob per answer)
- Controlled: Frozen model weights, same greedy decoding, same benchmark splits

**Verification Protocol**:
1. Separate model outputs into hallucinated vs. correct answer groups using Farquhar 2023 binary labels.
2. For each answer, compute token log-prob sequence and peakedness ratio (max token log-prob / mean token log-prob).
3. Compare peakedness distributions between hallucinated and correct groups on TriviaQA and NQ using Mann-Whitney U test.
4. Verify directional effect: hallucinated answers have significantly higher peakedness than correct answers.

**Success Criteria**:
- Primary: Hallucinated answers show significantly higher peakedness ratio than correct answers on TriviaQA and NQ (Mann-Whitney p < 0.05, directional)
- Secondary: Effect consistent across both LLaMA-2-7B and Mistral-7B-v0.1

**Failure Response**:
- IF fails: EXPLORE — assumption A2 violated; may need to test at larger model scale; if consistent null result, PIVOT to treat all benchmarks as same type

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 1; Assumption A2

---

---
**H-M2: Aggregation Function Sensitivity Aligns with Token Distribution Shape**

**Statement**: Under frozen LLMs on TriviaQA/NQ (peaked distributions per H-M1), min log-prob achieves higher rank-order correlation with hallucination labels than mean log-prob; conversely, on TruthfulQA (flat high-probability distributions), mean log-prob achieves higher rank-order correlation with hallucination labels than min log-prob, because min is maximally sensitive to single worst-case tokens while mean integrates signal across all tokens.

**Rationale**: This is the second causal step: distribution shape determines which aggregation function captures the most discriminative signal. Links the mechanism (H-M1) to the observable outcome (H-M3).

**Variables**:
- Independent: Aggregation function (min vs. mean) × Token distribution shape (peaked/TriviaQA-NQ vs. flat/TruthfulQA)
- Dependent: Spearman rank correlation between aggregation score and hallucination label
- Controlled: Same frozen models, same greedy decoding, same splits

**Verification Protocol**:
1. For TriviaQA and NQ: compute Spearman ρ between min log-prob scores and correctness labels; compute Spearman ρ between mean log-prob scores and correctness labels.
2. For TruthfulQA: repeat step 1.
3. Verify: ρ(min, TriviaQA/NQ) > ρ(mean, TriviaQA/NQ) and ρ(mean, TruthfulQA) > ρ(min, TruthfulQA).
4. Report correlation differentials with 95% CI.

**Success Criteria**:
- Primary: Rank correlation direction matches prediction on at least TriviaQA and TruthfulQA for at least one model
- Secondary: Effect replicates on NQ and on Mistral-7B-v0.1

**Failure Response**:
- IF fails: EXPLORE — rank correlation and AUROC may decouple due to label noise or distribution shape not as predicted; document as limitation

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 2; mathematical properties of min vs. mean aggregation

---

---
**H-M3: AUROC Differential Reflects Aggregation-Distribution Alignment (Directional Pattern)**

**Statement**: Under frozen LLMs (LLaMA-2-7B, Mistral-7B-v0.1), AUROC(min) - AUROC(mean) ≥ 0.02 on TriviaQA and NQ (factual recall benchmarks) AND AUROC(mean) - AUROC(min) ≥ 0.02 on TruthfulQA (imitative falsehood benchmark), with bootstrap 95% CI lower bounds > 0 for both directions, because AUROC directly measures ranking ability and the aggregation-distribution alignment determines signal quality.

**Rationale**: This is the final causal step and the operationalized core of the main hypothesis. Tests PROVE_NEW claims 4 and 5 jointly. H-E1 proves existence; H-M1 and H-M2 explain the mechanism; H-M3 confirms the directional pattern matches mechanistic predictions.

**Variables**:
- Independent: Aggregation function (min vs. mean) × Benchmark type (TriviaQA/NQ vs. TruthfulQA)
- Dependent: AUROC difference (min - mean per benchmark)
- Controlled: Same as H-E1; additionally raw-sum included as additional comparison

**Verification Protocol**:
1. Use AUROC table computed in H-E1; extract min and mean AUROC per benchmark per model.
2. Compute AUROC(min) - AUROC(mean) for TriviaQA, NQ, TruthfulQA separately.
3. Bootstrap 95% CI (n=1000) on each difference.
4. Verify: CI lower bound > 0 for TriviaQA/NQ (P1) and CI upper bound < 0 for TruthfulQA (P2, equivalently mean > min with CI lower > 0).
5. Additionally verify P3: raw-sum AUROC < min and < mean on all three benchmarks (directional, no threshold).

**Success Criteria**:
- Primary (P1): AUROC(min) - AUROC(mean) ≥ 0.02, bootstrap CI lower > 0 on TriviaQA AND NQ for both models
- Primary (P2): AUROC(mean) - AUROC(min) ≥ 0.02, bootstrap CI lower > 0 on TruthfulQA for both models
- Secondary (P3): raw-sum AUROC < both min and mean across all three benchmarks

**Failure Response**:
- IF P1 fails but P2 holds: PIVOT — partial support; publish with narrowed claim (mean generally better, or null on recall benchmarks)
- IF both P1 and P2 fail: EXPLORE — mechanism may be model-scale-dependent; escalate to 70B models if resources allow; else ABANDON and document as negative result

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3; Predictions P1, P2, P3; PROVE_NEW Claim 5

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
| H-E1 | MUST_WORK | ≥1 pair of aggregation functions shows AUROC diff ≥ 0.02 with non-overlapping CI | STOP pipeline; investigate A3/A4/A5 |
| H-M1 | MUST_WORK | Hallucinated answers on TriviaQA/NQ show significantly higher peakedness than correct answers | PIVOT: revisit A2; document if consistent null |
| H-M2 | SHOULD_WORK | Rank correlation direction matches prediction on ≥1 benchmark per model | EXPLORE: document as mechanistic limitation; proceed to H-M3 |
| H-M3 | SHOULD_WORK | P1 and/or P2 directional pattern confirmed with bootstrap CI | PIVOT/EXPLORE based on pattern; publish with narrowed claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumptions → Risk Mapping

**Risk R1 (Source: A1) — TruthfulQA imitative pattern absent at 7B scale**
- Description: 7B models may not exhibit flat high-probability wrong-answer pattern; inverse scaling is more pronounced at 70B+
- Severity: High
- Likelihood: Medium
- Affected Hypotheses: H-M1, H-M3 (P2 direction)
- Mitigation:
  1. Prevention: Test LLaMA-2-7B first; if TruthfulQA distribution is peaked rather than flat, add 70B analysis as supplementary
  2. Detection: Monitor peakedness ratios on TruthfulQA during H-M1 analysis
  3. Response: PIVOT — reclassify TruthfulQA as ambiguous; report P2 as null; narrow claim to TriviaQA/NQ directional result only

**Risk R2 (Source: A2) — Recall-failure peaked pattern absent on TriviaQA/NQ at 7B**
- Description: 7B models may not systematically show peaked uncertainty at fact-tokens; semantic entropy advantage may stem from other sources
- Severity: Critical
- Likelihood: Low
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3 (P1 direction)
- Mitigation:
  1. Prevention: Validate via token-level histogram inspection in H-M1 before committing to full AUROC analysis
  2. Detection: If AUROC(min) ≤ AUROC(mean) on both TriviaQA and NQ, flag A2 violation
  3. Response: ABANDON P1; reframe as exploratory finding; report as negative result with mechanistic diagnosis

**Risk R3 (Source: A3) — Greedy log-probs insufficiently representative**
- Description: Single-forward-pass greedy log-probs may not capture model uncertainty accurately; sampling-based estimates may be required
- Severity: Medium
- Likelihood: Low
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3 (all depend on greedy log-prob quality)
- Mitigation:
  1. Prevention: Use N=5 sample temperature-scaled log-prob average as sanity check on 10% of data
  2. Detection: If all three aggregation functions cluster within 0.01 AUROC of each other, A3 may be the culprit
  3. Response: Add sampling-based baseline comparison; reframe as "zero-cost single-pass" scope limitation

**Risk R4 (Source: A4) — Label noise ceiling limits discriminability**
- Description: Exact-match/F1 labels may be too noisy to reveal aggregation-function differences; ceiling at ~0.79 AUROC
- Severity: Low
- Likelihood: Low
- Affected Hypotheses: H-M3 (primary AUROC measurements)
- Mitigation:
  1. Prevention: Use full Farquhar 2023 test splits (not subsets) to maximize statistical power
  2. Detection: If best AUROC across all functions is < 0.65, label noise is likely dominant
  3. Response: Report relative differences even if absolute values are low; note ceiling in limitations

**Risk R5 (Source: A5) — lm-polygraph implementation gaps**
- Description: min log-prob (as distinct from max entropy) may not be directly implemented; custom implementation required
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-E1 (implementation prerequisite for all downstream tests)
- Mitigation:
  1. Prevention: Audit lm-polygraph estimator list before running experiments; implement custom min aggregation if needed (< 20 lines of Python)
  2. Detection: Run lm-polygraph dry run on 10 samples to verify all three aggregation variants output distinct scores
  3. Response: Implement custom aggregation wrapper; no hypothesis invalidation

### 4.2 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | TruthfulQA@7B may not show imitative pattern | A1 | High | H-M1, H-M3 | Escalate to 70B; narrow claim |
| R2 | TriviaQA/NQ peaked pattern absent | A2 | Critical | All | H-M1 histogram check; negative result |
| R3 | Greedy log-probs insufficiently representative | A3 | Medium | All | Sampling-based sanity check |
| R4 | Label noise ceiling limits AUROC discriminability | A4 | Low | H-M3 | Use full splits; report relative diffs |
| R5 | lm-polygraph missing min aggregation variant | A5 | Medium | H-E1 | Custom wrapper implementation |

Critical Risks: 1 (R2)
High Risks: 1 (R1)
Medium Risks: 2 (R3, R5)
Low Risks: 1 (R4)

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| CCP uses mean implicitly; no comparison to min/sum | If mean is globally optimal, min advantage may not hold | H-M1 distribution check before committing |
| SE uses sum within clusters; not single-pass | If multi-sample is required for signal, single-pass may ceiling at low AUROC | Sanity check: SE AUROC ~0.79 vs. our best should confirm feasibility |
| SelfCheckGPT probability baselines are ad-hoc | No systematic comparison baseline for raw-sum | Implement raw-sum cleanly; compare to ad-hoc baselines |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE — MUST_WORK — no dependencies)
         │
         ▼
[Level 1 - Mechanism Foundation]
    H-M1 ← H-E1 (MUST_WORK)
    Distribution shape verification
         │
         ▼
[Level 2 - Mechanism Link]
    H-M2 ← H-M1 (SHOULD_WORK)
    Aggregation sensitivity alignment
         │
         ▼
[Level 3 - Mechanism Outcome]
    H-M3 ← H-M2 (SHOULD_WORK)
    AUROC directional pattern (P1 + P2 + P3)
         │
         ▼
[Terminal - Phase 5 Baseline Comparison]
    [Deferred to Phase 5 per pipeline_options.skip_baseline_comparison=true → skipped]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation (H-E1)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Aggregation function produces different AUROC on ≥1 benchmark | MUST_WORK |

→ Gate 1: If H-E1 fails → STOP, reassess assumptions A3/A4/A5.

**Phase 2 — Core Mechanisms (H-M1, H-M2, H-M3)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | SHOULD_WORK |

→ Gate 2: H-M1 must pass. H-M2/H-M3 failures narrow claim but do not block Phase 4.5.

### 5.3 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type   |
|-------|-----------|---------------|-------------|
| 0     | H-E1      | None          | MUST_WORK   |
| 1     | H-M1      | H-E1          | MUST_WORK   |
| 2     | H-M2      | H-M1          | SHOULD_WORK |
| 3     | H-M3      | H-M2          | SHOULD_WORK |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Gantt Timeline (ASCII)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2     │ W3-4     │ W5       │ W6-7
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1            │ ████████ │          │          │
  [Gate 1]        │        ◆ │          │          │
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms
  H-M1            │          │ ████████ │          │
  H-M2            │          │          │ ████     │
  H-M3            │          │          │ ████     │
  [Gate 2]        │          │          │        ◆ │
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 4.5/6:      │          │          │          │ ████████
(Synthesis/Paper)
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) ≈ 5 weeks
  Note: H-M2 and H-M3 share data from H-E1 run; can overlap weeks 5-6

Slack Available: 0 weeks (all sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 4
  Existence: 1 (H-E1)
  Mechanism: 3 (H-M1, H-M2, H-M3)
  Condition: 0

Verification Phases: 2
  1. Foundation (H-E1)
  2. Mechanisms (H-M1, H-M2, H-M3)

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

Computational Resources:
  - 2× LLMs @ 7B (16GB VRAM each): LLaMA-2-7B, Mistral-7B-v0.1
  - Full test splits: TriviaQA (~7.0k Farquhar splits), NQ (~3.6k Farquhar splits), TruthfulQA generation (~817 samples)
  - Bootstrap n=1000 resamples per AUROC comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
Step 2: Evaluate Gate 1 → If pass, proceed
Step 3: Execute H-M1 (Distribution shape) — Week 3-4
Step 4: Evaluate Gate 2a → H-M1 must pass (MUST_WORK)
Step 5: Execute H-M2 (Sensitivity alignment) — Week 5
Step 6: Execute H-M3 (AUROC directional pattern) — Week 5-6 (data reuse from H-E1)
Step 7: Evaluate Gate 2b → Document H-M2/3 outcomes; proceed regardless
Final:  Verification complete → Phase 4.5 Synthesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Token-level log-probability aggregation function choice is non-trivial
and benchmark-type-dependent, with min log-prob optimal for recall-failure hallucinations
and mean log-prob optimal for imitative-falsehood hallucinations.

Supporting Evidence:
1. Causal mechanism: hallucination type → distribution shape → aggregation optimality
   (3-step chain with mathematical and empirical grounding)
2. Consistent with Fadeeva 2024 (mean works on recall benchmarks when combined
   with correction) and TruthfulQA inverse scaling (Lin 2021)
3. Direct gap in literature: no paper has ablated these three aggregation functions
   in isolation with directional predictions (Liu et al. 2025 survey confirms)

Strengths:
- Zero compute overhead (single forward pass; no sampling required)
- Directly reproducible (Farquhar 2023 splits are public; lm-polygraph is open-source)
- Clear falsification criteria (P1, P2, P3 with threshold ≥ 0.02 and bootstrap CI)

Expected Outcomes:
- Primary (P1): AUROC(min) ≥ AUROC(mean) + 0.02 on TriviaQA and NQ
- Primary (P2): AUROC(mean) ≥ AUROC(min) + 0.02 on TruthfulQA
- Secondary (P3): raw-sum AUROC < both min and mean on all benchmarks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant AUROC difference between min/mean/raw-sum
across TriviaQA, NQ, and TruthfulQA; differences within bootstrap 95% CI and ≤ 0.02.

Counter-Arguments:
1. CCP (Fadeeva 2024) uses mean aggregation and achieves AUROC 0.72-0.80 on TriviaQA/NQ
   — if mean were inferior to min, CCP would not have been competitive
2. TruthfulQA inverse scaling is weak at 7B scale (Lin 2021 shows it mainly at 70B+)
   — A1 assumption may be violated, collapsing P2
3. Scope limitations: long answers confound min vs. mean (length-dependent biases)
   — raw-sum confound affects all benchmarks

Potential Failure Points:
- R2 (Critical): TriviaQA/NQ recall-failure peaked pattern absent at 7B scale → P1 fails
- R1 (High): TruthfulQA imitative pattern absent at 7B scale → P2 fails
- R3 (Medium): Greedy log-probs insufficiently discriminative → all functions cluster

Conditions Under Which H0 Would Be Supported:
- AUROC(min) - AUROC(mean) < 0.02 AND bootstrap CI includes 0 on TriviaQA/NQ
- AUROC(mean) - AUROC(min) < 0.02 AND bootstrap CI includes 0 on TruthfulQA
- Distribution shape analysis (H-M1) shows no peakedness difference between benchmark types
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
H-TokenAgg-v1 presents a mechanistically grounded, zero-cost, directly reproducible
claim about aggregation function optimality. However, the antithesis raises valid
empirical concerns: 7B model scale may be insufficient for imitative-falsehood
pattern (TruthfulQA P2) and prior work using mean aggregation competitively suggests
the advantage of min may be marginal on recall benchmarks.

Resolution Path:
1. Foundation verification (H-E1): establishes existence before mechanism is assumed
2. Distribution shape verification (H-M1): tests the causal root before AUROC comparison
3. Sequential gate conditions: H-M1 (MUST_WORK) ensures causal mechanism confirmed
   before P1/P2 AUROC pattern is interpreted as mechanistically explained

Conditions for Thesis Support:
- H-M1 passes: distribution shape differences confirmed between benchmark types
- H-M3 P1 confirmed: min > mean on TriviaQA/NQ with CI lower > 0
- H-M3 P2 confirmed (secondary): mean > min on TruthfulQA

Conditions for Antithesis Support:
- H-M1 fails: no distribution shape difference (assumption A1 or A2 violated)
- H-M3 P1 and P2 both fail: all aggregation functions produce equivalent AUROC

Nuanced Outcome Possibilities:
1. Full Support: All hypotheses pass → both P1 and P2 confirmed → paper published
2. Partial Support: P1 passes, P2 fails → narrowed claim: min optimal for recall-failure;
   TruthfulQA requires larger scale or different approach
3. No Support: H-E1 or H-M1 fails → negative result paper; antithesis supported;
   route to Phase 2A-Dialogue for hypothesis redesign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect     | Thesis Position                        | Antithesis Challenge                        | Resolution         |
|------------|----------------------------------------|---------------------------------------------|--------------------|
| Existence  | Aggregation function choice matters    | Functions may be empirically equivalent     | H-E1 test          |
| Mechanism  | Distribution shape drives optimality   | 7B scale may not show shape differences     | H-M1 histogram test|
| Scope      | Works on recall + imitative benchmarks | P2 (TruthfulQA) weak at 7B scale            | Treat P2 secondary |
| Performance| Competitive with zero-sample cost      | Multi-sample SE outperforms (AUROC ~0.79)   | Phase 5 (skipped)  |

Overall Robustness Score: Medium
Confidence in Verification Plan: 0.75
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** Aggregation function choice (min/mean/raw-sum) is benchmark-type-dependent for hallucination detection via token log-probs.
- ID: H-TokenAgg-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available; 60% scope reduction applied)
- Sub-Hypotheses: 4 total — H-E: 1, H-M: 3
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 (Gate 1: H-E1 MUST_WORK; Gate 2: H-M1 MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: R2 (peaked distribution absent at 7B scale, Critical), R1 (TruthfulQA imitative pattern weak at 7B, High)

**Immediate Action:** Begin Phase 1 with H-E1 — run lm-polygraph with all three aggregation variants on Farquhar 2023 splits for TriviaQA and NQ with LLaMA-2-7B.

### Key Achievements
- 4 hypotheses across 2 verification phases
- H0 addressed: No significant AUROC difference within bootstrap 95% CI
- Scope reduced 60%: Claims 1-3 BUILD_ON (not re-verified); Claims 4-5 PROVE_NEW (verified here)

### Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Aggregation function choice produces measurably different AUROC on ≥1 benchmark
- Gate 1: MUST PASS — STOP if fails

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Recall-failure hallucinations show peaked token uncertainty distributions
- H-M2: Aggregation sensitivity aligns with distribution shape
- H-M3: AUROC differential matches directional prediction (P1 + P2 + P3)
- Gate 2: H-M1 must pass — H-M2/H-M3 failures narrow claim but do not block

### Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP; investigate A3/A4/A5; route to Phase 2A-Dialogue
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - FAIL (H-M1) → PIVOT: A2 violated; narrow claim or negative result
   - FAIL (H-M2/H-M3 only) → Document as limitation; proceed to Phase 4.5

### Open Questions
- Does hallucination type classification (peaked vs. flat) hold at 7B scale, or only at 70B+?
- Is SciQ Type A or Type B? Exploratory analysis in H-E1 will begin to reveal this.
- What is the minimum practical significance threshold (≥ 0.02 AUROC) in terms of downstream deployment impact?
- Does the min log-prob advantage on TriviaQA survive controlling for answer length?

### Recommendations
1. **Immediate:** Start Phase 1 with H-E1; audit lm-polygraph estimator list first (R5 mitigation)
2. **Resources:** Allocate 5 weeks for critical path; reserve 1 week buffer for implementation issues (R5)
3. **Failure Management:** Run H-M1 histogram analysis before committing to full AUROC table computation

### Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-TokenAgg-v1)
- Gap: gap-2-token-aggregation (Systematic Comparison of Token-Level Uncertainty Aggregation Strategies Without Fine-Tuning)
- Discussion: 8 exchanges, 6 convergence criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (scientificmethod: 2 inquiries × hypothesis+experiment stages)
- Tools: mcp__clearThought__scientificmethod (H-E1-verification, H-M-integrated)

**C. Established Baselines (BUILD_ON — not re-verified)**
- Semantic Entropy (Farquhar 2023): AUROC ~0.79 on TriviaQA
- SelfCheckGPT NLI (Manakul 2023): AUROC ~0.72-0.78 on WikiBio
- CCP mean aggregation (Fadeeva 2024): AUROC ~0.72-0.80 on TriviaQA/NQ
- Predictive entropy (Farquhar 2023): AUROC ~0.72 on TriviaQA
