# Verification Plan: Data Curation Transfer Taxonomy

**Date:** 2026-08-24
**Hypothesis ID:** H-CurationTransferTaxonomy-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under foundation model training (pre-training → fine-tuning → RLHF), if we apply curation heuristics discovered during pre-training to downstream stages, then low-level quality filters (deduplication, perplexity-based outlier removal) will transfer robustly while high-level strategies (domain mixing, task-specific filters) will require stage-specific tuning, because low-level operations address universal data hygiene properties independent of stage objectives while high-level strategies are objective-dependent.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in downstream task performance between models trained with transferred pre-training curation thresholds versus models trained with stage-specific tuned thresholds.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Pre-training: C4 or RedPajama; Fine-tuning: Dolly-15k or Alpaca (standard) | Widely-used datasets allow replication. C4/RedPajama have documented filtering |
| **Model** | Llama-2-7B or Pythia-6.9B | Mid-size models balance feasibility with meaningful measurement |

**Dataset Details:**
- Source: Public datasets with established curation pipelines
- Path: To be determined based on availability

**Model Details:**
- Type: Causal language model
- Source: Public checkpoints (Meta/EleutherAI)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| DataComp pre-training filtering | Varies by scale | LAION-5B | Stage-specific only, doesn't address transfer |
| Instruction dataset filtering (Alpagasus, LIMA) | Improves instruction following | Alpaca-52k | Fine-tuning-specific, doesn't leverage pre-training insights |
| RLHF preference data selection | Improves alignment | Various | RLHF-specific, treats each stage independently |

**Best Baseline:** Stage-tuned curation at each phase (current practice)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pre-training curation thresholds were optimized | None currently - identified gap | Transferring suboptimal thresholds would yield poor baseline |
| A2 | Distribution shift doesn't fundamentally change outlier definitions | Proposed but not validated | Transferred thresholds could hurt performance |
| A3 | Low-level curation operations are objective-independent | Prof. Pax reasoning about hygiene universality | All techniques might show transfer sensitivity |
| A4 | Performance differences attributable to curation | Prof. Vera identified required controls | Measured effects could be noise |
| A5 | Benchmarks sensitive enough to detect 1-2% differences | Prof. Vera's success criteria threshold | True transfer effects might be undetectable |

### 1.6 Research Gap & Novelty

**Gap:** Prior work treats curation as stage-specific optimization (DataComp for pre-training, instruction filtering for fine-tuning). No systematic characterization of which curation components transfer across stages and which require re-tuning.

**Novelty:** First systematic characterization of curation transfer behavior creating empirically-grounded taxonomy. Differentiates from meta-learning for hyperparameters by applying transfer analysis to data curation domain.

**Scope Reduction:** 25% (3 BUILD_ON claims excluded from verification: data curation techniques exist in isolation, stage objectives differ, best practices help at all stages)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-E1, H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-E1, H-M1, H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Transfer-Stable Curation Category Exists

**Type:** EXISTENCE

**Statement:** Under foundation model training (pre-training → fine-tuning → RLHF), if low-level quality filters (deduplication, perplexity-based outlier removal) are applied across stages, then they will transfer robustly with ≤1% performance delta compared to stage-tuned thresholds, because these operations address universal data hygiene properties independent of stage objectives.

**Rationale:** This hypothesis validates the existence of a category of curation techniques that transfer across FM training stages. If validated, it establishes that not all curation must be stage-specific.

**Variables:**
- Independent: Curation Strategy Source (Transferred, Stage-Tuned, Baseline-None)
- Dependent: Downstream Task Performance (MMLU, HellaSwag accuracy)
- Controlled: Model architecture (Llama-7B), hyperparameters, pre-training checkpoint

**Success Criteria (PoC - Direction-based):**
- Primary: Performance delta ≤ 1% (transferred vs. stage-tuned)
- Secondary: Both transferred and stage-tuned > baseline by >2%

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT (category may be "partially-stable" not "transfer-stable")

**Prerequisites:** None (foundation hypothesis)

**Verification Protocol:**
1. Extract pre-training dedup and perplexity thresholds from C4/RedPajama filtering logs
2. Apply transferred thresholds to fine-tuning data (Dolly/Alpaca) vs. stage-tuned vs. no-curation
3. Fine-tune Llama-2-7B on each dataset variant with fixed hyperparameters
4. Evaluate on MMLU and HellaSwag benchmarks
5. Measure performance delta between transferred and stage-tuned conditions

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P1

---

#### H-M1: Low-Level Operations Address Universal Data Hygiene

**Type:** MECHANISM

**Statement:** Under foundation model training, if low-level curation operations (deduplication, perplexity-based outlier removal) are tested across pre-training and fine-tuning stages, then optimal thresholds will not vary significantly (>10% performance delta when mismatched), because these operations address data quality properties independent of training objectives.

**Rationale:** This mechanism step tests the theoretical foundation for transfer stability - that hygiene operations don't depend on stage goals.

**Variables:**
- Independent: Curation threshold (pre-training-optimal vs. fine-tuning-optimal)
- Dependent: Downstream task performance
- Controlled: Model, hyperparameters, dataset

**Success Criteria (PoC - Direction-based):**
- Primary: Performance delta <10% when thresholds mismatched
- Secondary: Degradation significantly less than high-level techniques (domain mixing >5%)

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE (hygiene may not be universal; distribution shift effects)

**Prerequisites:** H-E1

**Verification Protocol:**
1. Tune dedup/perplexity thresholds independently for pre-training and fine-tuning stages
2. Cross-apply thresholds (pre-training-tuned on fine-tuning data, fine-tuning-tuned on pre-training data)
3. Measure performance degradation from mismatch
4. Compare degradation to stage-objective-dependent techniques (domain mixing)

**Source:** Phase 2A Section 1.3 Causal Step 1

---

#### H-M2: Transfer Stability Correlates with Objective-Independence

**Type:** MECHANISM

**Statement:** Under foundation model training, if curation techniques are categorized by their dependence on stage objectives, then objective-independent techniques (deduplication, outlier removal) will show robust transfer (≤1% delta) while objective-dependent techniques (domain mixing, task filters) will show poor transfer (>5% degradation), because optimal configurations for objective-dependent techniques vary with each stage's distinct optimization target.

**Rationale:** This mechanism step tests the classification principle - that objective-dependence predicts transfer behavior.

**Variables:**
- Independent: Curation Technique Category (Transfer-Stable vs. Transfer-Sensitive)
- Dependent: Performance delta (transferred vs. stage-tuned)
- Controlled: Model, hyperparameters, dataset

**Success Criteria (PoC - Direction-based):**
- Primary: Objective-independent techniques ≤1% delta; objective-dependent >5% delta
- Secondary: Clear separation between categories (non-overlapping confidence intervals)

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT (taxonomy may need refinement; categories may overlap)

**Prerequisites:** H-E1, H-M1

**Verification Protocol:**
1. Classify techniques into objective-independent (dedup, perplexity) vs. objective-dependent (domain mixing, task filters)
2. Transfer pre-training configurations to fine-tuning for both categories
3. Measure performance delta for each category
4. Test correlation between objective-dependence and transfer degradation

**Source:** Phase 2A Section 1.3 Causal Step 2

---

#### H-M3: Transferred Low-Level Thresholds Match Stage-Tuned Performance

**Type:** MECHANISM

**Statement:** Under foundation model training, if pre-training-derived low-level thresholds (deduplication, perplexity cutoffs) are applied to fine-tuning data, then resulting model performance will be equivalent to stage-specific threshold optimization (within 1% delta), because these thresholds capture universal data quality criteria rather than stage-specific optima.

**Rationale:** This is the final mechanism step validating that transfer-stable techniques achieve practical equivalence to stage-tuned approaches.

**Variables:**
- Independent: Threshold source (Transferred vs. Stage-Tuned vs. Baseline-None)
- Dependent: Downstream task performance
- Controlled: Model, hyperparameters, dataset

**Success Criteria (PoC - Direction-based):**
- Primary: Transferred within 1% of stage-tuned (demonstrates equivalence)
- Secondary: Both transferred and stage-tuned >2% above baseline (validates curation benefit)

**Gate:**
- Type: SHOULD_WORK
- If Fail: EXPLORE (may require threshold adaptation strategies)

**Prerequisites:** H-E1, H-M1, H-M2

**Verification Protocol:**
1. Create three fine-tuning dataset variants (transferred thresholds, stage-tuned thresholds, no curation)
2. Fine-tune Llama-2-7B on each variant with identical hyperparameters
3. Evaluate on MMLU, HellaSwag, TruthfulQA benchmarks
4. Conduct three-way statistical comparison (transferred vs. stage-tuned vs. baseline)

**Source:** Phase 2A Section 1.3 Causal Step 3, Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 (READY)
  ↓
H-M1 (wait for H-E1)
  ↓
H-M2 (wait for H-E1, H-M1)
  ↓
H-M3 (wait for H-E1, H-M1, H-M2)
```

**Execution Order:** Sequential (H-E1 → H-M1 → H-M2 → H-M3)

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Transfer-stable category exists with ≤1% delta | PIVOT to partial-stability model |
| H-M1 | MUST_WORK | Universal hygiene validated (<10% threshold sensitivity) | EXPLORE distribution shift effects |
| H-M2 | SHOULD_WORK | Objective-independence predicts transfer | PIVOT taxonomy refinement |
| H-M3 | SHOULD_WORK | Transferred matches stage-tuned (≤1% delta) | EXPLORE adaptation strategies |

### 3.3 Timeline

| Phase | Hypotheses | Duration | Notes |
|-------|------------|----------|-------|
| Phase 2C | 4 experiment designs | 2-3 days | Sequential design process |
| Phase 3 | 4 implementation plans | 3-4 days | Can parallelize |
| Phase 4 | 4 PoC validations | 5-7 days | Sequential (dependencies) |
| Phase 5 | Baseline comparison | 2-3 days | After all hypotheses validated |

**Total Duration:** 12-17 days (assuming no MUST_WORK failures)

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 (all gates must pass before Phase 5)

---

## 4. Risk Analysis

### 4.1 Identified Risks

| Risk ID | Source | Risk Description | Impact | Mitigation |
|---------|--------|------------------|--------|------------|
| R1 | A1 | Pre-training thresholds suboptimal | Poor baseline masks true transfer potential | Validate pre-training thresholds before transfer tests |
| R2 | A2 | Distribution shift changes outlier definitions | Transferred thresholds hurt performance | Test on multiple dataset pairs (C4→Dolly, RedPajama→Alpaca) |
| R3 | A3 | Low-level operations not objective-independent | Taxonomy collapses, all techniques stage-specific | Measure objective-dependence directly via ablation |
| R4 | A4 | Performance differences from confounds | Effects are noise, not curation signal | Fix architecture, hyperparameters, pre-training checkpoint |
| R5 | A5 | Benchmarks insensitive to 1-2% differences | True effects undetectable | Use multiple benchmarks (MMLU, HellaSwag, TruthfulQA) |

### 4.2 Risk-Hypothesis Mapping

| Hypothesis | Primary Risks | Secondary Risks |
|------------|---------------|-----------------|
| H-E1 | R1, R2, R5 | R4 |
| H-M1 | R2, R3 | R4 |
| H-M2 | R3 | R2 |
| H-M3 | R1, R2, R5 | R4 |

---

## 5. Dialectical Analysis

### 5.1 Thesis

Transfer-stable curation exists: low-level quality filters (deduplication, perplexity-based outlier removal) transfer robustly across FM training stages because they address universal data hygiene properties independent of stage objectives.

### 5.2 Antithesis (H0)

All curation is stage-specific: there is no significant difference between transferred and stage-tuned thresholds because optimal curation configurations are determined by distribution characteristics and training objectives unique to each stage.

### 5.3 Synthesis

Categorical transfer stability: curation techniques exhibit varying degrees of transfer robustness based on their dependence on stage-specific optimization targets. Objective-independent operations (hygiene-focused) transfer while objective-dependent strategies (goal-aligned) require stage-specific tuning. The taxonomy emerges from empirical characterization, not a priori theory.

### 5.4 Robustness Assessment

**Strengths:**
- Builds on established facts (3 BUILD_ON claims reduce scope by 25%)
- Clear falsification criteria (quantitative performance deltas)
- Systematic ablation across technique categories

**Weaknesses:**
- Assumes pre-training thresholds were optimized (A1 - no validation yet)
- Text-only scope limits generalization to multimodal models
- Taxonomy is proposed classification, not theory-derived

**Key Tension:** Distinguishing transfer stability from trivial "best practices work everywhere" - must show differential transfer behavior across categories.

---

## 6. Executive Summary

### 6.1 Achievements

✅ Decomposed main hypothesis into 4 sub-hypotheses (H-E1, H-M1-3)
✅ 25% scope reduction via Established Facts (3 BUILD_ON claims excluded)
✅ Sequential dependency chain with clear gate conditions
✅ Risk analysis covering all 5 key assumptions
✅ Dialectical evaluation (Thesis-Antithesis-Synthesis)

### 6.2 Execution Order

1. **H-E1 (READY):** Validate transfer-stable category exists
2. **H-M1:** Test universal hygiene hypothesis
3. **H-M2:** Correlate transfer stability with objective-independence
4. **H-M3:** Demonstrate practical equivalence (transferred ≈ stage-tuned)
5. **Phase 5:** Baseline comparison (deferred, separate gate)

### 6.3 Decision Points

- **After H-E1:** If MUST_WORK fails, PIVOT to partial-stability model
- **After H-M1:** If MUST_WORK fails, EXPLORE distribution shift effects
- **After H-M2/M3:** If SHOULD_WORK fails, refine taxonomy or explore adaptation

### 6.4 Open Questions

1. How to validate pre-training thresholds were optimal before testing transfer?
2. What degree of distribution shift breaks transfer for stable category?
3. Can transfer taxonomy extend to multimodal curation?

---

## 7. Next Steps

✅ **Phase 2B Complete**

**Immediate Next Actions:**
1. Run Phase 2C to design experiment for H-E1 (first READY hypothesis)
2. Create 02c_experiment_design_h-e1.md with full experimental specification
3. After H-E1 completes Phase 2C→3→4, proceed to H-M1

**Commands:**
- `/phase2c-experiment-design` or `/hypothesis-next` to start
- `verification_state.yaml` tracks progress through hypothesis loop

---

**Phase 2B Generated:** 2026-08-24
**Status:** Complete
**Ready for Phase 2C:** Yes (H-E1 READY)
