# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T04:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Lack of Systematic Embedding Method Comparison on Property Prediction
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All convergence criteria met — SPECIFIC core claim, MECHANISM explained, PREDICTIONS defined, NOVELTY articulated, FEASIBILITY confirmed, OBJECTIONS addressed

### Key Insights
- Benchmark comparison reframed as structured ablation study isolating structural inductive biases
- Effect size thresholds need calibration against baseline measurement variance
- Reference model selection for Git Re-Basin affects fairness of comparison
- Either outcome (equivariance matters / doesn't matter) is publishable and redirects field

### Breakthrough Moments
- Exchange 7 (Dr. Nova): Progressive addition design proposed — transforms benchmark into ablation study
- Exchange 8 (Prof. Vera): Experimental protocol formalized with 4-step ladder
- Exchange 11 (Dr. Ally): Final hypothesis synthesized with three testable predictions

---

## Final Hypothesis

### Title
Structural Inductive Biases in Weight Embeddings for Property Prediction

### Hypothesis ID
H-WeightStructure-v1

### Core Claim
Under the Model Zoo benchmark with accuracy labels as ground truth, if we compare four embedding methods with increasing structural sophistication (Flatten+MLP → Layer-wise → Layer-wise+GRB → NFN), then Pearson correlation with ground-truth accuracy will increase monotonically across steps, because structural biases capture weight-space patterns that encode functional model properties.

### Mechanism
1. Layer-wise processing preserves per-layer statistics that correlate with layer functionality
2. Permutation alignment (GRB) removes symmetry-induced variance, revealing functional equivalence
3. Permutation equivariance (NFN) directly operates on symmetry-reduced representations

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Layer-wise > Flatten+MLP | Δr > 0.1, p < 0.05 | Δr ≤ 0.1 |
| P2 | Layer-wise+GRB > Layer-wise | Δr > 0.05, p < 0.05 | Δr ≤ 0.05 |
| P3 | NFN > Layer-wise+GRB | Δr > 0.05, p < 0.05 | Δr ≤ 0.05 |

---

## Novelty

**Key Innovation**: First systematic ablation isolating structural inductive biases for weight embedding quality on standardized benchmark.

**Differentiation**:
- Prior work (Hyper-Representations): Evaluated single method on custom metrics
- Prior work (NFN): Focused on weight processing/generation, not property prediction
- Prior work (Git Re-Basin): Focused on model merging, not embedding preprocessing

---

## Experimental Design

### Dataset
- **Name**: Model Zoos (Schurholt et al. 2022)
- **Type**: Standard benchmark with ground-truth accuracy labels
- **Validation**: Requires σ > 10% accuracy variance to proceed

### Methods (Ablation Ladder)
| Step | Method | Structure | Alignment | Equivariant |
|------|--------|-----------|-----------|-------------|
| 1 | Flatten+MLP | ❌ | ❌ | ❌ |
| 2 | Layer-wise | ✅ | ❌ | ❌ |
| 3 | Layer-wise+GRB | ✅ | ✅ | ❌ |
| 4 | NFN | ✅ | ❌ | ✅ |

### Protocol
- **Phase 0**: Validate dataset variance (σ > 10%)
- **Phase 1**: Calibrate effect size thresholds with 10-seed baseline
- **Phase 2**: Run 4-step ablation with 5 seeds each, paired t-tests

---

## Limitations

- Results specific to Model Zoo dataset and accuracy prediction
- May not generalize to cross-architecture settings (train ResNets, test ViTs)
- NFN adaptation may not preserve all equivariance properties
- Compute constraints limit explorable model zoo sizes

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 17 exchanges, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed in protocol) |

---

## Phase 2B Readiness

| Criterion | Status |
|-----------|--------|
| Core hypothesis defined | ✅ |
| Null hypothesis defined | ✅ |
| Testable predictions (P1-P3) | ✅ |
| Experimental protocol | ✅ |
| Falsification criteria | ✅ |
| Technical feasibility confirmed | ✅ |

**Status**: READY for Phase 2B
