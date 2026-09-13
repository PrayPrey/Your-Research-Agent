---
title: "Phase 2B Verification Plan: Eviction-Aware LoRA"
hypothesis_id: "H-EvictionAwareLoRA-v1"
generated_at: "2026-05-04"
workflow: "phase2b-planning v6.0"
research_mode: "incremental"
scope_reduction: "50%"
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
completedAt: "2026-05-04T00:00:00"
---

# Verification Plan: Eviction-Aware LoRA for Long-Context LLMs

**Date:** 2026-05-04
**Hypothesis ID:** H-EvictionAwareLoRA-v1
**Confidence:** 0.75
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## Executive Summary

**Main Hypothesis:** Under long-context LLM fine-tuning with fixed KV cache budget constraints, training LoRA adapters with hard H2O-style KV eviction masks during the forward pass (r ∈ {25%, 50%, 75%}) produces per-category LongBench accuracy exceeding the sequential baseline (standard LoRA + H2O eviction at inference) by ≥2% at r=50% across ≥4/6 task categories on both LLaMA-2-7B and Mistral-7B-v0.1, because token-scarcity regularization produces more information-efficient attention representations.
- ID: H-EvictionAwareLoRA-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (50% scope reduction — BUILD_ON claims excluded)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: MUST_WORK, Gate 2: MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: R1 (eviction pattern inconsistency), R3 (model-specific results)

**Immediate Action:** Begin Phase 1 with H-E1 — verify gradient signal differentiation

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under long-context LLM fine-tuning with fixed KV cache budget constraints,
if LoRA adapters are trained with hard H2O-style KV eviction masks applied
during the forward pass (simulating budget ratio r ∈ {25%, 50%, 75%}),
then per-category LongBench accuracy will exceed the sequential baseline
(standard LoRA fine-tuning followed by H2O eviction at inference only)
by ≥2% at r=50% KV retention across ≥4/6 LongBench task categories on both
LLaMA-2-7B and Mistral-7B-v0.1,
because adapters trained under token-position scarcity learn more
information-efficient attention representations that extract higher utility
from surviving KV cache entries (token-scarcity regularization mechanism).

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in per-category LongBench
accuracy between eviction-aware LoRA fine-tuning and sequential baseline
(standard LoRA + H2O eviction at inference) at matched KV cache budget ratio r,
across LongBench task categories on LLaMA-2-7B and Mistral-7B-v0.1.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench + LongAlpaca-12k (standard) | LongBench is the canonical long-context NLP benchmark covering 21 tasks across 6 categories — directly tests the long-context accuracy claim. LongAlpaca-12k provides long-context fine-tuning signal without requiring new data collection. |
| **Model** | LLaMA-2-7B + Mistral-7B-v0.1 | Both are 7B-class open-weight models with available LoRA fine-tuning infrastructure; different attention implementations allow testing generality of eviction-aware training |

**Dataset Details:**
- Source: LongBench: THUDM/LongBench (HuggingFace); LongAlpaca-12k: Yukang/LongAlpaca (HuggingFace)
- Path: HuggingFace Hub — public datasets, no download restrictions
- Evaluation: Full LongBench test set (21 tasks, all samples per task — standard split)

**Model Details:**
- Type: decoder-only transformer LLM
- Source: meta-llama/Llama-2-7b-hf and mistralai/Mistral-7B-v0.1 on HuggingFace Hub

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard LoRA + H2O eviction (sequential) | ~1-3% accuracy degradation at r=50% vs. full cache on LLaMA-2-7B | LongBench |
| SnapKV + pre-trained model (no PEFT) | +2-5% over uniform eviction on multi-doc QA | LongBench |
| AdaLoRA full-cache fine-tuning | Competitive with full fine-tuning on GLUE; degrades under H2O post-hoc | GLUE / LongBench |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | H2O eviction patterns are consistent enough across inputs that training with simulated eviction provides meaningful signal | H2O paper: top-20% attention tokens are stable across sequences | Simulated eviction ≡ random masking → no specific benefit over standard dropout |
| A2 | Same eviction policy (H2O) used at both training simulation and inference evaluation | Experimental design constraint; H2O open-source implementation available | Policy mismatch introduces distribution shift, potentially reversing expected gain |
| A3 | LongBench per-category results are representative of general long-context task performance | LongBench covers 21 tasks across 6 categories — most comprehensive available | Results may not generalize to specific applications outside LongBench task distribution |
| A4 | LLaMA-2-7B and Mistral-7B-v0.1 have sufficiently different attention patterns for generality claim | Different RoPE variants and attention implementations; different heavy-hitter distributions | If results hold on only one model, contribution is model-specific |
| A5 | LongAlpaca-12k fine-tuning data provides sufficient long-context exposure | Long-context instruction pairs specifically designed for long-document tasks; publicly available | If data quality is the dominant factor, Alpaca-52k sanity check would reveal this |

### 1.6 Research Gap & Novelty

**Gap:** The field has developed KV cache eviction (H2O, SnapKV, StreamingLLM) and PEFT (LoRA, AdaLoRA, DoRA) independently. No prior work closes the gap by making fine-tuning aware of deployment-time KV constraints. Existing KV cache methods are deployment-time techniques applied to pre-trained or sequentially fine-tuned models. Existing PEFT methods assume full KV cache at inference.

**Innovation:** Token-scarcity regularization — applying H2O eviction masks during LoRA forward pass as a training-time constraint that produces inference-efficient adapters, eliminating the training-inference distribution mismatch for evicted-cache deployment. First systematic study of KV cache eviction-aware PEFT fine-tuning.

**Established Facts (BUILD_ON — not re-verified):**
- H2O heavy-hitter eviction improves inference throughput (Zhang et al. 2023)
- SnapKV query-aware clustering improves LongBench accuracy vs. uniform eviction (Li et al. 2024)
- AdaLoRA achieves competitive NLU accuracy with fewer parameters (Zhang et al. 2023)

**Claims to Prove (PROVE_NEW — scope of this plan):**
- Joint eviction-aware fine-tuning outperforms sequential baseline
- Token-scarcity regularization mechanism improves information efficiency

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Eviction Mask Produces Distinct Gradient Signal

**Type:** EXISTENCE
**Statement:** Under identical LoRA training conditions on LongAlpaca-12k, if H2O eviction masks are applied during the forward pass at KV budget ratio r=50%, then the resulting LoRA adapter weight matrices will differ significantly from the sequential baseline adapter weights (cosine similarity < 0.95 on at least one layer), because the masked forward pass changes the gradient signal reaching the LoRA parameters.

**Rationale (2-3 sentences):**
This hypothesis validates the mechanistic foundation of the entire research program — if eviction-aware training does not change adapter weights, the mechanism cannot engage, and all downstream hypotheses are invalid. It tests the most basic causal link: does the training perturbation (eviction mask) actually modify the learned parameters? A positive result is necessary (though not sufficient) for the token-scarcity regularization mechanism to operate.

**Variables (from Phase 2A):**
- Independent: Training eviction simulation (eviction-aware vs. sequential baseline)
- Dependent: Cosine similarity of LoRA weight matrices (adapter_A, adapter_B) per layer; weight norm difference per layer
- Controlled: LongAlpaca-12k dataset, LoRA rank=16/alpha=32/dropout=0.05, same gradient steps and learning rate schedule

**Verification Protocol (3-5 steps):**
1. Fine-tune sequential baseline LoRA on LongAlpaca-12k for both LLaMA-2-7B and Mistral-7B-v0.1; save adapter checkpoints.
2. Fine-tune eviction-aware LoRA with H2O hard-mask at r=50% on identical data/hyperparameters; save adapter checkpoints.
3. Compute per-layer cosine similarity between eviction-aware and sequential adapter weight matrices (adapter_A, adapter_B for all LoRA layers).
4. Compute per-layer L2 norm difference of adapter weight matrices as supplementary statistic.
5. Report: minimum cosine similarity across layers; percentage of layers with cosine similarity < 0.95.

**Success Criteria (PoC: Direction-based):**
- Primary: Cosine similarity < 0.95 in at least one LoRA layer (confirming distinct gradient signal)
- Secondary: Mean cosine similarity across all layers < 0.99 (confirming systematic weight differentiation, not isolated perturbation)

**Failure Response:**
- IF fails (all layers cosine similarity ≥ 0.95): PIVOT — investigate whether eviction mask is correctly injected into the forward pass; check gradient flow through masked positions; consider that H2O mask may need to be applied at attention score level rather than KV cache level.

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.3 (Causal Step 1), Section 5 (SH1)

---

#### H-M1: Token-Scarcity Regularization Changes Attention Distribution

**Type:** MECHANISM
**Statement:** Under the same evaluation inputs with H2O eviction at r=50%, if eviction-aware LoRA adapters are compared to sequential baseline adapters, then per-layer attention entropy and heavy-hitter concentration (top-20% attention token score ratio) will differ significantly (paired t-test p < 0.05 on at least 50% of transformer layers), because token-scarcity regularization during training causes adapters to develop qualitatively different attention patterns calibrated to the evicted-cache distribution.

**Rationale (2-3 sentences):**
This hypothesis tests the second causal step — that the weight differentiation observed in H-E1 manifests as a functional change in attention behavior, specifically the distribution of attention mass across token positions. Verifying attention entropy difference provides mechanistic evidence that training under token scarcity produces adapters that genuinely re-distribute attention, not merely store different noise. This distinguishes token-scarcity regularization from random dropout, which would produce isotropic weight differences without systematic attention redistribution.

**Variables (from Phase 2A):**
- Independent: Adapter type (eviction-aware vs. sequential baseline)
- Dependent: Per-layer attention entropy at r=50% evaluation; per-layer heavy-hitter concentration ratio
- Controlled: Same evaluation inputs (LongBench subset, ≥500 samples per category), same H2O eviction at r=50% applied identically at inference

**Verification Protocol (3-5 steps):**
1. Load both adapter variants (eviction-aware and sequential) for LLaMA-2-7B and Mistral-7B-v0.1.
2. Run forward pass on ≥500 LongBench samples per category with H2O eviction at r=50%; record per-layer attention score matrices.
3. Compute attention entropy (H = -Σ p_i log p_i) per layer per head; aggregate to mean per-layer entropy.
4. Compute heavy-hitter concentration: ratio of attention mass on top-20% tokens (by cumulative attention score) per layer.
5. Apply paired t-test across layers for both metrics; report percentage of layers with p < 0.05.

**Success Criteria (PoC: Direction-based):**
- Primary: Paired t-test p < 0.05 on attention entropy in ≥50% of transformer layers (at least one of LLaMA-2-7B or Mistral-7B-v0.1)
- Secondary: Heavy-hitter concentration ratio differs by ≥5% in mean across layers (directional evidence)

**Failure Response:**
- IF fails (no significant attention entropy difference): EXPLORE — check whether attention difference appears at later layers (deeper layers may be more sensitive); examine whether the effect is present in the model with higher baseline heavy-hitter stability; consider that attention-level analysis may require looking at specific task categories where long-range dependencies matter most.

**Dependencies:** H-E1 (existence of weight differentiation must be confirmed)

**Source:** Phase 2A Section 1.3 (Causal Step 2), Section 1.2 (Variables)

---

#### H-M2: Monotonically Increasing Accuracy Advantage Under Tighter Budget

**Type:** MECHANISM
**Statement:** When both eviction-aware and sequential LoRA adapters are evaluated on LongBench at r ∈ {25%, 50%, 75%}, the accuracy advantage of eviction-aware training (per-category accuracy gap: eviction-aware minus sequential) will increase monotonically as r decreases (Spearman ρ < -0.8 between r and mean accuracy gap across categories), because the distribution mismatch penalty for sequential adapters grows as the cache budget tightens, amplifying the benefit of eviction-aware training.

**Rationale (2-3 sentences):**
This hypothesis tests the dose-response relationship between eviction severity and the performance benefit of eviction-aware training — a key mechanistic prediction that distinguishes the token-scarcity regularization theory from alternative explanations. A monotonic relationship would confirm that the mechanism scales predictably with the degree of training-inference alignment, providing stronger evidence of the distribution-mismatch theory. This also provides practical guidance on when eviction-aware training is most valuable (tightest budgets).

**Variables (from Phase 2A):**
- Independent: KV cache budget ratio r ∈ {25%, 50%, 75%}
- Dependent: Per-category accuracy gap (eviction-aware minus sequential) at each r; Spearman rank correlation between r and mean accuracy gap
- Controlled: Both adapter variants trained on LongAlpaca-12k; H2O eviction policy fixed; evaluation on full LongBench 21 tasks

**Verification Protocol (3-5 steps):**
1. Evaluate both adapter variants (eviction-aware and sequential) at all three budget ratios r ∈ {25%, 50%, 75%} on LongBench full test set (all 21 tasks, all samples).
2. Compute per-category accuracy for each combination of (adapter type × budget ratio r × model).
3. Compute accuracy gap = eviction-aware accuracy minus sequential baseline accuracy for each category × r.
4. Aggregate gaps to mean accuracy gap across all 6 categories at each r value.
5. Compute Spearman rank correlation ρ between r-values and mean accuracy gaps; report with 95% CI.

**Success Criteria (PoC: Direction-based):**
- Primary: Spearman ρ < -0.8 (strong negative correlation — larger benefit at smaller r) on at least one model
- Secondary: Mean accuracy gap is positive (eviction-aware > sequential) at r=25% for both models (directional consistency)

**Failure Response:**
- IF fails (ρ ≥ -0.8 or no monotonic trend): EXPLORE — the mechanism may be non-linear (threshold effect rather than monotonic); examine whether the trend holds within specific task categories (e.g., summarization may show stronger budget sensitivity than few-shot tasks); document as a scope limitation if r=50% shows benefit but monotonicity fails.

**Dependencies:** H-M1 (attention distribution change must be confirmed as mechanism)

**Source:** Phase 2A Section 1.6 (Prediction P2), Section 1.3 (Causal Step 2-3)

---

#### H-M3: Inference Distribution Mismatch Elimination Yields Accuracy Gain

**Type:** MECHANISM
**Statement:** Under LongBench evaluation with H2O eviction at r=50%, eviction-aware LoRA fine-tuning achieves ≥2% higher per-category accuracy than sequential baseline (standard LoRA + H2O eviction at inference) in ≥4/6 LongBench task categories on both LLaMA-2-7B and Mistral-7B-v0.1 (paired t-test p < 0.05, Bonferroni-corrected), because eviction-aware training eliminates the training-inference distribution mismatch that causes sequential adapters to underperform when evaluated on evicted KV cache.

**Rationale (2-3 sentences):**
This is the primary empirical hypothesis and the central claim of the research — it directly tests whether the joint optimization advantage materializes as measurable accuracy improvement on the canonical long-context benchmark. The ≥4/6 category requirement ensures the benefit is robust and not concentrated in a single task type, which would suggest task-specific overfitting rather than a general mechanism. Requiring results on both base models guards against a model-specific artifact, strengthening the generality claim.

**Variables (from Phase 2A):**
- Independent: Training eviction simulation (eviction-aware vs. sequential)
- Dependent: LongBench per-category accuracy (6 categories, 21 tasks total; full test set for each task)
- Controlled: r=50% H2O eviction applied identically at inference for both variants; LongAlpaca-12k training data; LoRA rank=16/alpha=32

**Verification Protocol (3-5 steps):**
1. Evaluate eviction-aware and sequential LoRA adapters on full LongBench test set (all 21 tasks, all evaluation samples) with H2O eviction at r=50%.
2. Compute per-task accuracy for all 21 tasks; aggregate to 6 per-category mean accuracies.
3. Compute per-category accuracy difference (eviction-aware minus sequential) for both LLaMA-2-7B and Mistral-7B-v0.1.
4. Apply paired t-test across tasks within each category; apply Bonferroni correction across 6 categories (corrected α = 0.05/6 ≈ 0.0083).
5. Report: number of categories with ≥2% improvement and p < 0.0083; aggregate LongBench score; throughput at r=50% vs. r=100% (Prediction P3 verification).

**Success Criteria (PoC: Direction-based):**
- Primary: ≥2% per-category accuracy improvement in ≥4/6 LongBench categories on both LLaMA-2-7B and Mistral-7B-v0.1 (Bonferroni-corrected p < 0.0083)
- Secondary: Aggregate LongBench score improvement ≥1.5% on both models; ≥1.8× throughput at r=50% vs. full-cache (Prediction P3)

**Failure Response:**
- IF fails (improvement in <4/6 categories or on only one model): EXPLORE — examine which specific task categories show improvement vs. regression; if improvement concentrated in long-range tasks (multi-doc QA, summarization) but not few-shot tasks, narrow the scope claim; consider whether 2% threshold is too high given LongBench task variance; if single model shows benefit, reduce generality claim accordingly.

**Dependencies:** H-M2 (budget sensitivity mechanism confirmed), H-M1 (attention mechanism confirmed)

**Source:** Phase 2A Section 1.6 (Prediction P1), Section 1.1 (Core Statement), Section 5 (SH1-SH2)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Cosine similarity < 0.95 in ≥1 LoRA layer | STOP — eviction mask not engaging; reassess injection method |
| H-M1 | MUST_WORK | Attention entropy p < 0.05 in ≥50% layers on ≥1 model | PIVOT — examine deeper layers; check task-specific effects |
| H-M2 | SHOULD_WORK | Spearman ρ < -0.8 (monotonic advantage vs. r) | EXPLORE — document as non-linear scope; continue to H-M3 |
| H-M3 | MUST_WORK | ≥2% improvement in ≥4/6 categories on both models | EXPLORE — narrow scope by category/model; document limitations |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 Decision | — | Week 2 end |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |
| Gate 2 Decision | — | Week 5 end |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

| ID | Risk | Source Assumption | Severity | Likelihood | Affected Hypotheses |
|----|------|-------------------|----------|------------|---------------------|
| R1 | Eviction pattern inconsistency — masks provide noisy signal | A1 | High | Medium | H-E1, H-M1, H-M3 |
| R2 | Policy mismatch at evaluation — different eviction policy used | A2 | Critical | Low | All (design constraint) |
| R3 | Model-specific results — benefit on only one base model | A4 | High | Medium | H-M3 |
| R4 | LongBench distribution narrow — results don't generalize | A3 | Medium | Low | H-M3 |
| R5 | Data confound — LongAlpaca-12k distribution drives results | A5 | Medium | Low | H-E1, H-M3 |

### 4.2 Detailed Mitigation Strategies

**Risk R1: Eviction Pattern Inconsistency**
- **Source Assumption:** A1 — H2O eviction patterns are consistent across inputs
- **Description:** If heavy-hitter tokens vary substantially across sequences, the eviction mask during training introduces random noise equivalent to standard dropout, producing no specific benefit
- **Affected Hypotheses:** H-E1, H-M1, H-M3
- **Severity:** High
- **Mitigation:**
  1. Prevention: Use LongAlpaca-12k (long-context data with consistent document structure) — heavy hitters are more stable on long-context tasks than short-context tasks
  2. Detection: At H-E1 stage, analyze per-layer eviction mask stability across training batches — if mask correlation across sequences < 0.5, flag as risk materializing
  3. Response: PIVOT — if instability detected, apply moving-average eviction mask (smooth across recent sequences) instead of per-sample mask; reduces noise while preserving distributional training signal

**Risk R2: Policy Mismatch at Evaluation**
- **Source Assumption:** A2 — same H2O policy at training simulation and inference
- **Description:** If a different eviction policy (SnapKV, StreamingLLM) is used at inference, the eviction-aware training provides no advantage and may even degrade performance due to mismatch
- **Affected Hypotheses:** All
- **Severity:** Critical
- **Mitigation:**
  1. Prevention: Lock H2O as eviction policy in all experiment scripts; add assertion checks that policy is consistent
  2. Detection: Cross-check eviction policy in training config and inference config before each run
  3. Response: ABORT H-M3 SnapKV comparison if policy consistency cannot be maintained; scope claim explicitly to H2O policy only

**Risk R3: Model-Specific Results**
- **Source Assumption:** A4 — LLaMA-2-7B and Mistral-7B-v0.1 provide generality
- **Description:** If the eviction-aware benefit appears on only one model, the contribution is model-specific rather than a general technique
- **Affected Hypotheses:** H-M3
- **Severity:** High
- **Mitigation:**
  1. Prevention: Run full experiments on both models from the start; do not skip one model to save compute
  2. Detection: Compare results across models after H-M3; if gap > 3% in number of benefiting categories, flag divergence
  3. Response: SCOPE — if one model benefits and the other does not, narrow generality claim to the specific model class; investigate whether attention implementation differences (GQA in Mistral vs. MHA in LLaMA-2) explain the divergence; document as a limitation

**Risk R4: LongBench Distribution Narrow**
- **Source Assumption:** A3 — LongBench is representative
- **Description:** Results may be specific to LongBench task types and not generalize to deployment scenarios outside this benchmark
- **Affected Hypotheses:** H-M3
- **Severity:** Medium
- **Mitigation:**
  1. Prevention: Report per-category results (not just aggregate) to expose category-level heterogeneity
  2. Detection: If improvement concentrated in 1-2 categories only (< 4/6), flag narrow generalization
  3. Response: SCOPE — narrow claims to specific categories; acknowledge as a limitation in paper

**Risk R5: Data Confound**
- **Source Assumption:** A5 — LongAlpaca-12k drives eviction-aware benefit
- **Description:** If LongAlpaca-12k's distribution aligns with LongBench tasks, the improvement may reflect data quality rather than eviction simulation
- **Affected Hypotheses:** H-E1, H-M3
- **Severity:** Medium
- **Mitigation:**
  1. Prevention: H-E1 directly checks whether adapter weights differ — weight difference is a data-independent signal of eviction mask engagement
  2. Detection: If H-E1 shows large weight differences but H-M3 shows no accuracy benefit, data confound is unlikely (mechanism engaged but task transfer failed)
  3. Response: EXPLORE — run optional Alpaca-52k sanity check (short-context data, lower long-context alignment); if eviction-aware still outperforms, data confound ruled out

### 4.3 Risk Summary

| ID | Risk | Severity | Critical? | Mitigation Strategy |
|----|------|----------|-----------|---------------------|
| R1 | Eviction pattern inconsistency | High | No | Moving-average mask fallback |
| R2 | Policy mismatch at evaluation | Critical | YES | Assertion-locked H2O policy |
| R3 | Model-specific results | High | No | Full dual-model experiments; scope narrowing |
| R4 | LongBench distribution narrow | Medium | No | Per-category reporting; scope narrowing |
| R5 | Data confound (LongAlpaca-12k) | Medium | No | H-E1 data-independent check; optional Alpaca-52k |

Critical Risks: 1 (R2)
High Risks: 2 (R1, R3)
Medium Risks: 2 (R4, R5)
Low Risks: 0

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE — no dependencies)
         │  Gate 1: MUST_WORK
         ▼
[Level 1 - Mechanism: Attention Distribution]
    H-M1 ← H-E1
         │  Gate 2a: MUST_WORK
         ▼
[Level 2 - Mechanism: Budget Sensitivity]
    H-M2 ← H-M1
         │  Gate 2b: SHOULD_WORK
         ▼
[Level 3 - Mechanism: Primary Accuracy Claim]
    H-M3 ← H-M2
         │  Gate 2c: MUST_WORK
         ▼
    [TERMINAL]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ W1-2    │ W3-4    │ W5      │
───────────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1                 │ ████████│         │         │
  [Gate 1 — MUST_WORK] │         │ ◆       │         │
───────────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1                 │         │ ████████│         │
  H-M2                 │         │         │ ████    │
  H-M3                 │         │         │ ████    │
  [Gate 2 — MUST_WORK] │         │         │       ◆ │
───────────────────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2+H-M3 parallel analysis)
Slack Available: 0 weeks (all sequential chain)

Note: H-M2 and H-M3 share the same evaluation run (LongBench at
r ∈ {25%, 50%, 75%}) — they can be computed simultaneously in Week 5.
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
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1) — Weeks 1-2
2. Mechanisms (H-M1 → H-M3) — Weeks 3-5

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

Compute Requirements:
- 2× base models (LLaMA-2-7B, Mistral-7B-v0.1) — LoRA fine-tuning × 4 variants
  (sequential baseline + eviction-aware × r={25%, 50%, 75%})
- LongBench full evaluation: 21 tasks × all samples × 2 models × 4 variants
- Single A100 GPU (per CUDA_VISIBLE_DEVICES policy)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-E1 (Foundation) — Weeks 1-2
- Fine-tune sequential baseline + eviction-aware LoRA on LongAlpaca-12k
- Compare adapter weights (cosine similarity analysis)

**Step 2:** Evaluate Gate 1 → If PASS, proceed; if FAIL, STOP and reassess eviction mask injection

**Step 3:** Execute H-M1 (Attention Distribution) — Weeks 3-4
- Analyze per-layer attention entropy and heavy-hitter concentration on LongBench subset (≥500 samples/category)

**Step 4:** Evaluate Gate 2a → If PASS (or document scope), proceed

**Step 5:** Execute H-M2 + H-M3 simultaneously — Week 5
- Full LongBench evaluation at r ∈ {25%, 50%, 75%} for both models
- H-M2: Spearman correlation analysis across r values
- H-M3: Per-category accuracy comparison with Bonferroni-corrected t-test

**Step 6:** Evaluate Gate 2b (H-M2, SHOULD_WORK) and Gate 2c (H-M3, MUST_WORK)

**Final:** Verification complete → Proceed to Phase 5 baseline comparison (or paper writing if skip_baseline_comparison=true)

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: Eviction-aware LoRA fine-tuning (joint optimization with
simulated H2O KV eviction) outperforms the sequential baseline on
LongBench per-category accuracy at matched KV budget, because joint
training eliminates training-inference distribution mismatch.

Supporting Evidence:
1. H2O heavy-hitter persistence across sequences supports the consistency
   of eviction simulation as a training signal (A1 evidence)
2. Distribution mismatch between training (full KV cache) and inference
   (evicted cache) is established as a performance degradation mechanism
   in domain adaptation literature
3. Token-scarcity regularization analogy to dropout (Srivastava et al. 2014)
   provides theoretical basis for generalization under systematic token absence

Strengths:
- Clear causal mechanism: mask → gradient change → attention redistribution → accuracy
- Testable at each causal step (4 hypotheses with independent falsifiers)
- All components are publicly available for reproducibility

Expected Outcomes:
- Primary (P1): ≥2% LongBench per-category improvement at r=50%
- Secondary (P2): Monotonically increasing advantage as r decreases (ρ < -0.8)
- Tertiary (P3): ≥1.8× throughput at r=50% vs. full-cache
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): There is no statistically significant difference
in per-category LongBench accuracy between eviction-aware LoRA and
sequential baseline at matched KV budget ratio r.

Counter-Arguments:
1. Eviction pattern variability (A1 violation): if heavy-hitter tokens are
   input-dependent and not persistent, training eviction = random masking =
   standard dropout without H2O-specific benefit; the sequential baseline
   may be equivalent at the adapter weight level
2. Training data confound (A5 risk): LongAlpaca-12k's long-context alignment
   with LongBench may give eviction-aware training an artifactual advantage;
   short-context Alpaca-52k training may show no eviction-aware benefit
3. Model-specificity (A4 risk): if LLaMA-2-7B and Mistral-7B-v0.1 differ
   significantly in heavy-hitter stability, results may hold on one model
   only, undermining the generality claim

Potential Failure Points:
- H-E1 FAIL: Eviction mask does not produce distinct gradient signal
  (all cosine similarities ≥ 0.95) → entire mechanism collapses
- H-M1 FAIL: Attention distribution unchanged → token-scarcity
  regularization theory is wrong; mechanism is not engaging
- H-M3 FAIL: Accuracy improvement < 2% or in < 4/6 categories → the
  distribution-mismatch mechanism exists but is too weak to be practically significant

Conditions Under Which H0 Would Be Supported:
- If per-layer cosine similarity ≥ 0.95 across all layers (H-E1 falsifier)
- If attention entropy is statistically identical between adapter types (H-M1 falsifier)
- If per-category improvement < 2% or concentrated in < 4/6 categories (P1 falsifier)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:
The hypothesis H-EvictionAwareLoRA-v1 presents a mechanistically grounded
claim that joint eviction-aware training eliminates a real distribution mismatch.
However, the null hypothesis raises valid concerns: if heavy-hitter patterns
are sufficiently variable, the eviction mask reduces to a task-agnostic
regularizer with no policy-specific benefit, and the sequential baseline
would perform equivalently.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Data-independent weight analysis confirms
   the mechanism is engaging before any accuracy claims are made
2. Mechanism verification (H-M1): Attention entropy analysis distinguishes
   systematic attention redistribution from random noise
3. Budget sensitivity test (H-M2): Monotonicity requirement prevents
   accepting marginal or noise-level improvements as confirmation
4. Gate conditions: H-E1 and H-M3 are MUST_WORK — failure terminates or
   narrows the research direction, preventing false confirmation

Conditions for Thesis Support:
- H-E1 PASS: Distinct adapter weights (cosine similarity < 0.95)
- H-M1 PASS: Significant attention entropy difference in ≥50% of layers
- H-M3 PASS: ≥2% improvement in ≥4/6 categories on both models

Conditions for Antithesis Support (H0 retained):
- H-E1 FAIL: Identical adapter weights → eviction mask not engaging
- H-M1 FAIL: Identical attention distributions → no regularization effect
- H-M3 FAIL: < 2% improvement or < 4/6 categories → mechanism too weak

Nuanced Outcome Possibilities:
1. Full Support: All hypotheses pass → Thesis validated, proceed to Phase 6
2. Partial Support: H-E1+H-M1 pass, H-M3 narrowly passes (3/6 categories) →
   Refined thesis with task-specific scope (e.g., "long-range tasks only")
3. No Support: H-E1 or H-M1 fail → Mechanism does not engage; route to Phase 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Eviction mask changes adapter weights | Mask may equal random noise | H-E1 cosine similarity test |
| Mechanism | Attention redistribution under scarcity | Dropout analogy may not hold at token-position level | H-M1 attention entropy test |
| Dose-response | Stronger benefit at tighter budgets | Non-linear or absent relationship | H-M2 Spearman correlation |
| Accuracy | ≥2% LongBench improvement at r=50% | < 2% or model-specific only | H-M3 paired t-test with Bonferroni |
| Performance | ≥1.8× throughput at r=50% | H2O throughput already demonstrated | Throughput measurement (P3) |

**Overall Robustness Score:** Medium-High (mechanism well-specified, individual steps falsifiable, primary empirical claim has clear quantitative criterion)

**Confidence in Verification Plan:** 0.75

---

## 7. Conclusions

### Key Achievements
- 4 hypotheses across 2 phases (H-E1, H-M1, H-M2, H-M3)
- H0 addressed: No significant accuracy difference between joint and sequential approaches
- 50% scope reduction from Phase 2A: BUILD_ON claims (H2O, SnapKV, AdaLoRA) treated as established
- All hypotheses have independent falsifiers and clear success criteria

### Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Adapter weight differentiation under eviction-aware training
- Gate 1: MUST PASS — if fail, STOP entire verification

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Attention entropy distribution change (MUST_WORK) — Weeks 3-4
- H-M2: Monotonic accuracy advantage vs. budget ratio (SHOULD_WORK) — Week 5
- H-M3: Primary accuracy claim ≥2% in ≥4/6 categories (MUST_WORK) — Week 5
- Gate 2: H-M1 and H-M3 must pass for full thesis support

### Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - PASS → Proceed to Phase 2
   - FAIL → STOP; investigate eviction mask injection; route to Phase 0 if fundamental

2. **Gate 2a (Mechanism):** H-M1 MUST_WORK
   - PASS → Proceed to H-M2/H-M3
   - FAIL → PIVOT — explore deeper layers, task-specific effects; EXPLORE alternative evidence for mechanism

3. **Gate 2b (Budget Sensitivity):** H-M2 SHOULD_WORK
   - FAIL → Document as limitation; continue to H-M3 (does not block)

4. **Gate 2c (Primary Accuracy):** H-M3 MUST_WORK
   - FAIL → EXPLORE scope narrowing; if <2% overall, document as insufficient effect size

### Open Questions
- Does the accuracy advantage generalize beyond H2O to other eviction policies (SnapKV, StreamingLLM)?
- Is rank-budget coupling (AdaLoRA rank allocation guided by eviction scores) complementary or redundant to eviction-aware training?
- Does the Alpaca-52k sanity check confirm that long-context fine-tuning data is necessary for the eviction-aware benefit?

### Recommendations

1. **Immediate Actions:**
   - Begin Phase 1 with H-E1 weight analysis (set CUDA_VISIBLE_DEVICES to single empty GPU)
   - Implement eviction mask injection at attention score level, not post-softmax
   - Set up measurement infrastructure for adapter weight comparison and LongBench evaluation harness

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve 1 week buffer for debugging eviction mask injection (R1 risk)
   - H-M2 and H-M3 share the same evaluation run — schedule Week 5 as combined LongBench sweep

3. **Failure Management:**
   - Document all intermediate results regardless of pass/fail
   - Execute PIVOT strategies (R1 moving-average mask) before declaring FAIL
   - Ensure Bonferroni correction is applied before reporting H-M3 results

---

## Appendices

### A. Phase 2A Reference
- **Source:** `03_refinement.yaml` (ID: H-EvictionAwareLoRA-v1)
- **Generated:** 2026-05-04 | Workflow: phase2a-dialogue v10.0.0
- **Schema:** v10.0.0 Free-Parse | Convergence: 7 exchanges, all 6 criteria met

### B. Established Baselines (BUILD_ON — not re-verified)
- H2O eviction: Zhang et al. 2023 (arXiv:2306.14048)
- SnapKV clustering: Li et al. 2024 (arXiv:2404.14469)
- AdaLoRA PEFT: Zhang et al. 2023 (arXiv:2303.10512)

### C. Experiment Scale Note
- LongBench evaluation uses **full standard test set** for all 21 tasks (not subsets)
- Attention analysis in H-M1 uses ≥500 samples per LongBench category
- Both base models (LLaMA-2-7B, Mistral-7B-v0.1) run for all hypotheses — no single-model shortcuts

---

*Generated by YouRA Phase 2B (v6.0) | 2026-05-04*
