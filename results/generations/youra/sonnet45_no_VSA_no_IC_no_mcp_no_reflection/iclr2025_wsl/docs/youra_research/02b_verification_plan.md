# Phase 2B: Verification Plan
**Generated**: 2026-08-28T22:03:50Z  
**Main Hypothesis**: H-WeightOrthogonality-v1  
**Execution Mode**: UNATTENDED

---

## Main Hypothesis

**ID**: H-WeightOrthogonality-v1  
**Title**: Orthogonal Expressivity of Weight-Processing Backbones

**Statement**: Under the domain of neural network weight-space learning, if we process weights with multiple backbone architectures (transformer, equivariant GNN, MLP) that target orthogonal structural properties (global dependencies, permutation symmetry, local patterns), then combining their learned representations will significantly outperform individual backbones on weight-to-property prediction and anomaly detection tasks (>5% on property prediction, >10% on backdoor detection), because each architecture captures complementary aspects of weight structure that individual backbones miss.

**Source**: `03_refinement.yaml` (Phase 2A Dialogue output)

---

## Sub-Hypothesis Decomposition

### H-E1: Foundation (EXISTENCE)
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Statement**: Layer-wise weight tokenization preserves sufficient structural signal for backbone comparison tasks (property prediction, symmetry tests)

**Prerequisites**: None  
**Status**: READY (no prerequisites)

**Rationale**: Before testing backbone complementarity, must verify that layer-wise processing doesn't destroy the signal. This is Assumption A1 from Phase 2A.

**Test Plan**:
- Train single backbone (Transformer or GNN) on layer-wise tokenized weights
- Measure property prediction accuracy on held-out models
- Success: Accuracy significantly above random baseline (e.g., >60% on test accuracy prediction)
- Failure: Accuracy near random (layer-wise processing loses too much information)

---

### H-M1: Symmetry Mechanism (MECHANISM)
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Statement**: Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%)

**Prerequisites**: H-E1  
**Status**: NOT_STARTED (depends on H-E1)

**Rationale**: Tests Prediction P2 from Phase 2A. Core mechanism claim: architectural inductive biases lead to preferential property capture.

**Test Plan**:
- Train Transformer and GNN backbones on unperturbed weights
- Apply within-layer permutations (symmetry-preserving)
- Apply across-layer permutations (symmetry-breaking)
- Measure prediction accuracy under each perturbation
- Success: GNN shows >30% differential, Transformer <10%
- Failure: No differential OR both show similar differential

---

### H-M2: Orthogonality Mechanism (MECHANISM)
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Statement**: Reconstruction errors between Transformer and GNN weight embeddings show orthogonal failure modes (Pearson correlation <0.7), indicating complementary information capture

**Prerequisites**: H-E1  
**Status**: NOT_STARTED (depends on H-E1)

**Rationale**: Tests Prediction P3 from Phase 2A. Orthogonality claim: what one backbone fails to reconstruct, the other succeeds at.

**Test Plan**:
- Train autoencoder backbones: Transformer→embedding→reconstruct, GNN→embedding→reconstruct
- For each test model, compute per-weight reconstruction errors
- Calculate Pearson correlation of error vectors between backbones
- Success: Correlation <0.7 across test set
- Failure: Correlation >0.7 (errors are not orthogonal)

---

### H-C1: Practical Complementarity (CONDITION)
**Type**: CONDITION  
**Gate**: SHOULD_WORK  
**Statement**: Concatenated Transformer+GNN embeddings achieve >5% accuracy improvement over best single backbone on property prediction and >10% improvement on backdoor detection, demonstrating practical complementarity

**Prerequisites**: H-M1, H-M2  
**Status**: NOT_STARTED (depends on H-M1 and H-M2)

**Rationale**: Tests Prediction P1 from Phase 2A. Practical validation of complementarity hypothesis. SHOULD_WORK gate: failure doesn't block Phase 5, but weakens main hypothesis.

**Test Plan**:
- Train concatenated system: Concatenate[Transformer_emb, GNN_emb]→predictor
- Compare against single-backbone baselines
- Measure improvement on property prediction and backdoor detection
- Success: Concatenated >5% on property prediction, >10% on backdoor detection
- Failure: Gains <5% on property prediction OR <10% on backdoor detection

---

## Dependency Graph

```
H-E1 (READY)
  ├── H-M1 (NOT_STARTED) ─┐
  └── H-M2 (NOT_STARTED) ─┤
                          └── H-C1 (NOT_STARTED)
```

**Execution Order**:
1. H-E1 (foundation check)
2. H-M1 + H-M2 (parallel execution after H-E1 passes)
3. H-C1 (after both H-M1 and H-M2 pass)

---

## Risk Analysis

### High Risk: H-E1
- **Risk**: Layer-wise processing loses critical cross-layer dependencies
- **Impact**: Blocks all downstream hypotheses (H-M1, H-M2, H-C1)
- **Mitigation**: Two-stage validation (synthetic networks with known structure → real model zoo)
- **Contingency**: If failed, route to Phase 2A-Dialogue for hypothesis modification (consider full-network processing alternatives)

### Medium Risk: H-M1, H-M2
- **Risk**: Architectural priors don't align with weight-space properties as predicted
- **Impact**: Blocks H-C1, weakens main hypothesis
- **Mitigation**: Theory-grounded taxonomy (permutation equivariance, locality/globality)
- **Contingency**: If failed, route to Phase 0 (fundamental mechanism assumption violated)

### Low Risk: H-C1
- **Risk**: Complementarity gains don't meet thresholds despite orthogonality
- **Impact**: Weakens practical significance, but doesn't invalidate mechanism
- **Mitigation**: SHOULD_WORK gate (failure doesn't block Phase 5)
- **Contingency**: If failed, can still proceed to Phase 5 with reduced claims

---

## Timeline Estimation

| Hypothesis | Phase 2C | Phase 3 | Phase 4 | Total |
|-----------|----------|---------|---------|-------|
| H-E1      | 1 day    | 1 day   | 1 day   | 3 days |
| H-M1      | 1 day    | 2 days  | 2 days  | 5 days |
| H-M2      | 1 day    | 2 days  | 2 days  | 5 days |
| H-C1      | 1 day    | 1 day   | 2 days  | 4 days |

**Critical Path**: H-E1 → H-M1/H-M2 (parallel) → H-C1  
**Estimated Total**: 10-14 days (accounting for parallel execution)

---

## Controlled Variables (from Phase 2A)

| Variable | Control Method |
|----------|----------------|
| Dataset | timm Model Zoo (standard pre-trained models) + Backdoor Benchmark |
| Model | Transformer, Equivariant GNN, MLP backbones |
| Architecture Capacity | Parameter-matched (same model size) |
| Training Procedure | Same optimizer, learning rate schedule, epochs |
| Input Preprocessing | Layer-wise weight tokenization (consistent) |

---

## Success Criteria Summary

| Hypothesis | Gate Type | Success Criterion |
|-----------|-----------|-------------------|
| H-E1 | MUST_WORK | Property prediction accuracy >60% (significantly above random) |
| H-M1 | MUST_WORK | GNN symmetry differential >30%, Transformer <10% |
| H-M2 | MUST_WORK | Reconstruction error correlation <0.7 |
| H-C1 | SHOULD_WORK | Concatenated >5% on property prediction, >10% on backdoor detection |

---

## Dialectical Analysis

### Thesis
Weight-processing backbone architectures capture orthogonal structural properties due to their inductive biases (transformers = global attention, GNNs = local message-passing with permutation equivariance).

### Antithesis
Backbones trained on the same objective (e.g., predicting model accuracy) will converge to similar representations regardless of architectural differences. Shared training signal overrides inductive biases.

### Synthesis
Architectural inductive biases operate at the representational level (how patterns are encoded), while training objectives operate at the output level (what is predicted). For weight-space tasks where structure matters (permutation patterns, locality), architectural priors should dominate. However, empirical validation required to confirm this hypothesis.

**Key Tension**: Does layer-wise processing preserve enough structure for architectural differences to manifest, or does dimensionality reduction wash out the signal?

**Resolution Strategy**: H-E1 tests signal preservation directly. If H-E1 passes but H-M1/H-M2 fail, the tension is resolved in favor of the antithesis (training objective dominates). If all pass, synthesis is validated.

---

## Phase 2C Handoff

**Next Action**: Begin Phase 2C with H-E1 (first READY hypothesis)

**Required Inputs for Phase 2C**:
- Sub-hypothesis statement: H-E1
- Success criteria: Property prediction >60% on held-out models
- Experimental setup: timm model zoo, layer-wise tokenization, single backbone training
- Gate type: MUST_WORK

**Expected Phase 2C Output**:
- `02c_experiment_design_h-e1.md` with detailed experimental protocol
- Measurement plan, data collection procedure, statistical tests
- Falsification criteria and expected results

---

## Archon Project Initialization

**Pipeline Project ID**: mock-pipeline-proj-001  
**Project Title**: Anonymous Pipeline: Orthogonal Expressivity of Weight-Processing Backbones

**Hypothesis Task Mapping**:
- H-E1 → mock-task-e1-001
- H-M1 → mock-task-m1-001
- H-M2 → mock-task-m2-001
- H-C1 → mock-task-c1-001

**Phase Task IDs**:
- Phase 2B → mock-phase2b-task
- Phase 2C → mock-phase2c-task
- Phase 3 → mock-phase3-task
- Phase 4 → mock-phase4-task
- Phase 5 → mock-phase5-task

(Note: Mock IDs used in ablation mode; production system creates real Archon tasks)

---

## Key Related Work (from Phase 2A)

**Baselines to Compare**:
1. Transformer-based weight embeddings (lacks permutation equivariance)
2. Equivariant GNN weight processors (limited global dependency modeling)
3. Model stitching (Lenc & Vedaldi, 2015) - validates layer-wise assumption but not a weight-processing backbone

**Best Baseline Performance**: To be established in Phase 4 (synthetic networks) → Phase 5 (real model zoo comparison)

---

## Open Questions (to be resolved in subsequent phases)

1. Are three properties (permutation, locality/globality, frequency) exhaustive? (Phase 4 ablation studies)
2. Does layer-wise processing lose critical cross-layer signals? (H-E1 validation)
3. Do capacity-matched architectures differ in fundamental expressivity ceilings? (H-M1, H-M2 validation)
4. Does backdoor detection complementarity generalize to other anomaly types? (Phase 5 extension)

---

**End of Phase 2B Verification Plan**
