# Verification Plan: Task-Conditioned Selective State Space (TC-SSM)

**Date:** 2026-08-28
**Hypothesis ID:** H-TCSSM-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the scope of transformer-to-SSM conversion for tasks where SSM achieves >80% of transformer baseline,
if state space parameters (Δ, B, C) are modulated by learned task embeddings during conversion training,
then the resulting sub-quadratic model will preserve adaptation capability (few-shot accuracy within 5% of original in <100 gradient steps),
because the task conditioning preserves the functional subspace relevant for rapid task specialization.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in adaptation capability between task-conditioned conversion
and standard sequential approaches (convert then fine-tune).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | SuperGLUE (standard) | Standard few-shot NLP benchmark with established protocols |
| **Model** | Mamba (TC-SSM variant) | Sub-quadratic architecture with input-dependent gating extensible to task conditioning |

**Dataset Details:**
- Source: https://super.gluebenchmark.com/
- Path: huggingface datasets: super_glue

**Model Details:**
- Type: selective state space model
- Source: state-spaces/mamba + custom task conditioning module

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Distillation + LoRA | Unknown — needs empirical measurement | SuperGLUE |
| Standard Distillation | Typically 2-5% degradation | Various NLP benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Task structure discoverable via self-supervised clustering | Language models learn latent topics without supervision | Requires task-labeled conversion data |
| A2 | Adaptation capability preserved in SSM's state dynamics | SSM achieves competitive performance on many NLP tasks | Some tasks fundamentally incompatible |
| A3 | Low-rank task embeddings (rank 16-64) sufficient | LoRA works with rank 8-64 across diverse tasks | Higher rank increases overhead |
| A4 | Joint conversion + adaptation training is stable | Multi-task learning and curriculum methods exist | May require curriculum training |

### 1.6 Research Gap & Novelty

**Key Innovation:** Task-Conditioned Selective State Space (TC-SSM) — first method to co-design conversion and adaptation.

**Differentiation:**
- vs Mamba: Adds task-dependent gating for adaptation (not just input-dependent)
- vs LoRA: Integrates during conversion (not post-training)
- vs Knowledge Distillation: Preserves adaptation manifold (not just outputs)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | READY |
| H-M2 | Mechanism | MUST_WORK | H-M1 | READY |
| H-M3 | Mechanism | MUST_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

#### H-E1: Task Embedding Structure Existence

**Statement**: Under transformer-to-SSM conversion training, if hidden states are clustered via self-supervised learning, then embeddings will show structure correlated with downstream task similarity, because latent task structure exists in transformer representations.

**Rationale**: Foundation hypothesis. Must prove task structure is discoverable before mechanism hypotheses make sense. Without clusterable task embeddings, the entire TC-SSM approach fails.

**Variables**:
- Independent: Clustering method (K-means, spectral, hierarchical)
- Dependent: Cluster-task correlation (adjusted Rand index, NMI)
- Controlled: Source transformer checkpoint, hidden layer selection

**Verification Protocol**:
1. Extract hidden states from transformer during forward pass on SuperGLUE tasks.
2. Apply self-supervised clustering (K-means, K=8 matching SuperGLUE task count).
3. Measure cluster purity and correlation with ground-truth task labels.

**Success Criteria** (PoC):
- Primary: Cluster purity > random baseline (>0.125 for 8 clusters)
- Secondary: NMI > 0.3 indicating meaningful structure

**Failure Response**: IF fails → PIVOT to supervised task embeddings

**Dependencies**: None

**Source**: Phase 2A SH1, Causal Step 1

---

#### H-M1: Task Embedding Encoding

**Statement**: Under the scope of conversion training, if task embeddings are learned from clustered hidden states, then they will encode functional specialization patterns useful for downstream adaptation, because transformer hidden states capture task-relevant features.

**Rationale**: First mechanism step. Validates that clustering produces usable embeddings, not just structure. Links existence (H-E1) to modulation (H-M2).

**Variables**:
- Independent: Task embedding dimension (16, 32, 64)
- Dependent: Embedding discriminability (linear probe accuracy)
- Controlled: Clustering algorithm, hidden layer

**Verification Protocol**:
1. Train task embedding layer on clustered hidden states.
2. Freeze embeddings and train linear probe on task classification.
3. Compare probe accuracy to random embeddings baseline.

**Success Criteria** (PoC):
- Primary: Linear probe accuracy > random baseline
- Secondary: Embedding dimensions show interpretable structure

**Failure Response**: IF fails → EXPLORE alternative embedding methods

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Low-Rank SSM Modulation

**Statement**: Under TC-SSM architecture, if low-rank projections (rank 16-64) modulate Mamba's Δ, B, C matrices based on task embeddings, then state space dynamics will be task-conditioned with <2x overhead, because LoRA-style modulation is efficient and effective.

**Rationale**: Core architectural mechanism. Proves task conditioning can be integrated into SSM without excessive overhead. Critical for practical viability.

**Variables**:
- Independent: Projection rank (16, 32, 64)
- Dependent: Task-conditioned state variance, computational overhead
- Controlled: Base Mamba architecture, embedding source

**Verification Protocol**:
1. Implement low-rank projection layers for Δ, B, C matrices.
2. Measure inference FLOPs vs vanilla Mamba.
3. Verify state dynamics change with different task embeddings.

**Success Criteria** (PoC):
- Primary: FLOPs overhead < 2x vanilla Mamba
- Secondary: State variance differs across task embeddings

**Failure Response**: IF fails → EXPLORE selective modulation (fewer matrices)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Adaptation Manifold Preservation

**Statement**: Under task-conditioned conversion, if TC-SSM integrates task conditioning during training, then the resulting model will preserve adaptation capability (few-shot accuracy within 5% of transformer in <100 steps), because task conditioning preserves the functional subspace for rapid specialization.

**Rationale**: Final mechanism step validating the core hypothesis. Proves the entire pipeline works end-to-end. Most critical hypothesis for research contribution.

**Variables**:
- Independent: Conversion method (TC-SSM vs baselines)
- Dependent: Few-shot accuracy, adaptation speed (steps to 95% ceiling)
- Controlled: Source transformer, fine-tuning protocol, shot count

**Verification Protocol**:
1. Convert transformer to TC-SSM using task-conditioned training.
2. Evaluate 8-shot and 16-shot accuracy on SuperGLUE subset.
3. Measure gradient steps to reach 95% of fine-tuned ceiling.

**Success Criteria** (PoC):
- Primary: Few-shot accuracy within 5% of transformer baseline
- Secondary: Adaptation in <100 gradient steps

**Failure Response**: IF fails → PIVOT hypothesis scope or mechanism design

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Cluster purity > random | STOP, reassess hypothesis |
| H-M1 | MUST_WORK | Embeddings discriminable | PIVOT to supervised method |
| H-M2 | MUST_WORK | Overhead < 2x | EXPLORE selective modulation |
| H-M3 | MUST_WORK | Accuracy within 5% | PIVOT scope or mechanism |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Foundation | H-E1 | 1-2 days |
| Mechanism | H-M1, H-M2, H-M3 | 3-5 days |

**Total Duration:** 4-7 days (PoC scope)

---
