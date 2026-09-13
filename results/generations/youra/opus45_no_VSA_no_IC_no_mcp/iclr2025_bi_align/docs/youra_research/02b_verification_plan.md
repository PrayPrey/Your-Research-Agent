# Verification Plan: Dimensional Alignment Signatures

**Date:** 2026-08-26
**Hypothesis ID:** H-DimensionalAlignmentSignatures-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled conditions (same base model, same preference data, same compute budget), if we compare PPO-based RLHF and Direct Preference Optimization (DPO), then we will observe differential performance profiles across alignment benchmarks (TruthfulQA, HHH-helpful, HHH-harmless), because the methods' mechanistic differences (explicit reward model smoothing vs direct closed-form optimization) create distinct alignment signatures detectable on existing evaluation infrastructure.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in cross-benchmark performance profiles between DPO and RLHF-trained models. All pairwise benchmark comparisons will show Cohen's d < 0.15.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic HH-RLHF (standard) | Standard preference dataset used in both RLHF and DPO papers; enables controlled comparison |
| **Model** | Llama-2-7B | Open-weight 7B model with established fine-tuning protocols; sufficient scale for alignment effects |

**Dataset Details:**
- Source: huggingface.co/datasets/Anthropic/hh-rlhf
- Path: Anthropic/hh-rlhf

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Llama-2-7b-hf

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| DPO (Rafailov et al. 2023) | Matches or exceeds RLHF on single benchmarks | Various preference datasets |
| RLHF-PPO (Ouyang et al. 2022) | Established alignment improvements over SFT | Human preference data |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Existing benchmarks measure sufficiently distinct alignment dimensions | Benchmarks designed to target different aspects | Cross-benchmark patterns may be artifacts of shared variance |
| A2 | 7B model scale sufficient to observe method differences | Both methods show effects at 7B scale in prior work | Results may not generalize to larger models |
| A3 | HH-RLHF dataset quality equally supports both methods | Dataset used successfully for both in published work | One method may be disadvantaged |
| A4 | Reward model training quality can be controlled | Standard practices exist (held-out validation) | Poor reward model creates unfair comparison |
| A5 | Benchmark sample sizes provide sufficient statistical power | TruthfulQA ~800 samples sufficient for d=0.3 at 80% power | May miss real effects |

### 1.6 Research Gap & Novelty

Prior work compares RLHF vs DPO on single benchmarks (aggregate performance). This work examines cross-benchmark patterns to reveal dimensional signatures, shifting alignment evaluation from monolithic scoring to multi-dimensional profiling.

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

#### H-E1: Benchmark Independence Validation

**Statement**: Under standard evaluation conditions, if we compute correlations between TruthfulQA, HHH-helpful, and HHH-harmless scores on base Llama-2-7B, then pairwise correlations will be < 0.5, because these benchmarks were designed to measure distinct alignment dimensions.

**Rationale**: Before testing whether methods create different profiles, we must verify the benchmarks actually measure distinct things. High inter-benchmark correlation would mean "profiles" are artifacts.

**Variables**:
- Independent: Benchmark type (TruthfulQA, HHH-helpful, HHH-harmless)
- Dependent: Pairwise Pearson correlation coefficients
- Controlled: Base model (Llama-2-7B, no alignment training), evaluation protocol

**Verification Protocol**:
1. Evaluate base Llama-2-7B on all three benchmarks using full test sets
2. Compute pairwise Pearson correlations between benchmark scores
3. Verify all correlations < 0.5

**Success Criteria**:
- Primary: All pairwise correlations < 0.5
- Secondary: Clear separation in benchmark score distributions

**Failure Response**: IF fails → STOP (benchmarks too correlated for profile analysis)

**Dependencies**: None

**Source**: Phase 2A SH1

---

#### H-M1: RLHF Reward Model Smoothing

**Statement**: Under standard RLHF training, if we train a reward model on HH-RLHF preference pairs, then the reward model will produce smooth, interpolating reward predictions, because explicit reward model training learns a continuous approximation of discrete preference labels.

**Rationale**: This is the first mechanistic claim: RLHF's explicit reward model creates smoothing. Must verify before claiming this affects alignment profiles.

**Variables**:
- Independent: Training method (RLHF reward model training)
- Dependent: Reward prediction smoothness (gradient magnitude statistics)
- Controlled: Dataset (HH-RLHF), model architecture, training hyperparameters

**Verification Protocol**:
1. Train reward model on HH-RLHF using standard protocol
2. Evaluate reward predictions on held-out preference pairs
3. Compute gradient statistics and reward distribution continuity

**Success Criteria**:
- Primary: Reward model shows interpolating behavior (smooth reward landscape)
- Secondary: Validation accuracy > 65% on held-out pairs

**Failure Response**: IF fails → PIVOT to alternative RLHF formulation

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

#### H-M2: DPO Boundary Preservation

**Statement**: Under DPO training, if we directly optimize from preferences without intermediate reward model, then the policy will preserve sharper preference boundaries, because DPO's closed-form objective directly encodes preference rankings without smoothing.

**Rationale**: Second mechanistic claim: DPO preserves sharp boundaries. Comparison with H-M1 establishes the mechanistic difference.

**Variables**:
- Independent: Training method (DPO)
- Dependent: Policy preference boundary sharpness
- Controlled: Dataset (HH-RLHF), base model, compute budget

**Verification Protocol**:
1. Train Llama-2-7B with DPO on HH-RLHF
2. Evaluate policy on boundary cases (near-tie preferences)
3. Compare decision sharpness to RLHF model from H-M1

**Success Criteria**:
- Primary: DPO shows sharper preference boundaries than RLHF
- Secondary: Measurable difference in boundary case handling

**Failure Response**: IF fails → Document as limitation

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Optimization Landscape Attractors

**Statement**: Under alignment training, if RLHF produces smooth and DPO produces sharp optimization landscapes, then models will converge to different stable configurations (attractors), because landscape geometry determines convergence behavior.

**Rationale**: Bridge from mechanistic differences (H-M1, H-M2) to observable outcomes. Different attractors = different final model behaviors.

**Variables**:
- Independent: Optimization landscape type (smooth RLHF vs sharp DPO)
- Dependent: Model behavior clustering / convergence patterns
- Controlled: Training seeds, compute budget, evaluation protocol

**Verification Protocol**:
1. Train multiple seeds of both methods
2. Analyze final model behavior similarity within vs across methods
3. Verify within-method similarity > cross-method similarity

**Success Criteria**:
- Primary: Models cluster by training method, not by seed
- Secondary: Distinct behavioral signatures per method

**Failure Response**: IF fails → Document as limitation

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

#### H-M4: Differential Benchmark Profiles

**Statement**: Under controlled comparison, if RLHF and DPO converge to different attractors, then they will show differential performance profiles across TruthfulQA, HHH-helpful, and HHH-harmless benchmarks, because different attractors emphasize different alignment dimensions.

**Rationale**: Core novel claim. Tests whether mechanistic differences manifest as measurable benchmark profile differences.

**Variables**:
- Independent: Training method (RLHF-PPO vs DPO)
- Dependent: Cross-benchmark performance profile (3 benchmark scores)
- Controlled: Base model, preference data, compute budget, evaluation protocol

**Verification Protocol**:
1. Evaluate both methods on all three benchmarks (full test sets)
2. Compute Cohen's d for each benchmark comparison
3. Test for differential profile: at least one d > 0.3 AND at least one d < 0.15

**Success Criteria**:
- Primary: At least one benchmark shows d > 0.3 AND at least one shows d < 0.15
- Secondary: Cross-benchmark correlations differ between methods (p < 0.05)

**Failure Response**: IF fails → H0 supported (no dimensional signatures)

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, P1

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | All correlations < 0.5 | STOP pipeline |
| H-M1 | MUST_WORK | Smooth reward landscape | PIVOT formulation |
| H-M2 | SHOULD_WORK | Sharper than RLHF | Document limitation |
| H-M3 | SHOULD_WORK | Method clustering | Document limitation |
| H-M4 | SHOULD_WORK | Differential profile | H0 supported |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

### 3.4 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - benchmark independence)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 (RLHF smoothing) ← H-E1
         │
         ▼
    H-M2 (DPO boundaries) ← H-M1
         │
         ▼
    H-M3 (Attractors) ← H-M2
         │
         ▼
    H-M4 (Differential profiles) ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 3.5 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3 │ W4 │ W5 │ W6
─────────────────┼──────┼────┼────┼────┼────
PHASE 1: Foundation
  H-E1           │ ████ │    │    │    │
  [Gate 1]       │    ◆ │    │    │    │
─────────────────┼──────┼────┼────┼────┼────
PHASE 2: Mechanisms
  H-M1           │      │ ██ │    │    │
  H-M2           │      │    │ ██ │    │
  H-M3           │      │    │    │ ██ │
  H-M4           │      │    │    │    │ ██
  [Gate 2]       │      │    │    │    │  ◆
═══════════════════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 4. Risk Analysis

### 4.1 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Benchmarks too correlated | A1 | Critical | H-E1, All | Pre-test validation in H-E1 |
| R2 | 7B scale insufficient | A2 | Medium | H-M4 | Document as scope limitation |
| R3 | Dataset bias toward one method | A3 | Medium | H-M1-M4 | Cross-validate with subset |
| R4 | Poor reward model quality | A4 | High | H-M1, H-M4 | Validation metrics, early stopping |
| R5 | Insufficient statistical power | A5 | Medium | H-M4 | Use full benchmark sets (800+ samples) |

### 4.2 Mitigation Strategies

**R1 (Benchmark Correlation):** H-E1 directly tests this. If correlations > 0.5, stop pipeline.

**R4 (Reward Model Quality):** Document training metrics, use held-out validation, ensure fair comparison.

---

## 5. Dialectical Analysis

### 5.1 Thesis

Different preference learning methods (RLHF vs DPO) produce measurably different alignment profiles, revealing alignment as multi-dimensional.

**Supporting Evidence:**
- Mechanistic differences established in literature (reward model vs direct optimization)
- Benchmarks designed for distinct alignment dimensions
- Controlled comparison eliminates confounds

### 5.2 Antithesis (H0)

No significant difference in cross-benchmark profiles. Methods are functionally equivalent despite algorithmic differences.

**Counter-Arguments:**
- Both optimize same objective (human preferences)
- 7B scale may not reveal differences visible at larger scale
- Benchmark variance may mask real differences

### 5.3 Synthesis

The verification plan addresses this dialectic through sequential hypothesis testing with gate conditions. H-E1 establishes benchmark distinctness. H-M1-M4 test the causal chain. If all pass, thesis supported. If H-E1 or H-M1 fails, antithesis supported.

---

## 6. Executive Summary

**Main Hypothesis:** Dimensional Alignment Signatures
- ID: H-DimensionalAlignmentSignatures-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-seeded)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Benchmark correlation (R1), Reward model quality (R4)

**Immediate Action:** Begin Phase 1 with H-E1

---

## 7. Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-DimensionalAlignmentSignatures-v1)

### B. Evaluation Sample Sizes
- TruthfulQA: ~800 questions (full set)
- HHH-helpful: Full evaluation subset
- HHH-harmless: Full evaluation subset
- Statistical power: 80% for d=0.3

---

*Generated by Phase 2B Planning Workflow*
*Status: Complete*
*Completed At: 2026-08-26*
