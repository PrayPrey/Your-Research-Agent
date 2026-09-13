# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T09:45:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: GAP-1
- **Gap Title**: No Systematic Benchmark Comparison of Equivariant vs Non-Equivariant Weight Embeddings
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Data efficiency is the right comparison axis—equivariance may not improve ceiling R² but should improve small-N performance
- Three-way comparison (Statistics/MLP/NFN) reveals whether equivariance matches handcrafted domain knowledge
- Crossing point analysis provides outcome-agnostic contribution regardless of which method wins

### Breakthrough Moments
- Exchange 1: Nova reframes comparison from final performance to data efficiency
- Exchange 5: Ally synthesizes quantified three-way comparison with falsification thresholds
- Exchange 7: Nova identifies crossing point as novel metric for characterizing data-efficiency landscape

---

## Final Hypothesis

### Title
Data Efficiency of Permutation-Equivariant Weight Embeddings

### Hypothesis ID
H-EquivariantDataEfficiency-v1

### Core Claim
Under fixed-architecture homogeneous model zoos (ResNet-20/CIFAR-10), if we train weight embedding models with varying dataset sizes (N=100 to 5000), then permutation-equivariant architectures (NFN) will achieve equivalent accuracy prediction R² with ≤50% of training samples compared to MLP baselines, because equivariance eliminates the need to learn permutation invariance from data.

### Mechanism
1. Weight matrices have hidden-unit permutation symmetry (reordering neurons preserves function)
2. Non-equivariant methods (MLP) must learn this invariance from data, consuming sample complexity
3. Equivariant methods (NFN) enforce invariance architecturally, freeing capacity for prediction task

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | NFN R² > MLP R² + 0.1 at N=500 | t-test p<0.05 | p≥0.05 or gap<0.1 |
| **P2** | All methods within R² ±0.03 at N=5000 | Max pairwise diff <0.03 | Any diff ≥0.03 |
| **P3** | Crossing point N* < 2500 | NFN matches Statistics R² | N*≥2500 or no crossing |

---

## Novelty

**Key Innovation**: First systematic data efficiency comparison for weight embeddings. Introduces "crossing point" analysis to characterize when learned embeddings match handcrafted statistics.

**Differentiation from Prior Work**:
- Unterthiner et al. 2020: Demonstrated achievable R², but no learning curve analysis
- Zhou et al. 2023 (NFN): Introduced architecture, but no non-equivariant baseline comparison
- Schürholt et al. 2024 (SANE): Focused on scalability, not sample complexity

---

## Experimental Design

### Dataset
- **Name**: Model Zoo ResNet-20/CIFAR-10
- **Size**: 5360 models
- **Source**: github.com/ModelZoos/ModelZooDataset

### Methods
| Method | Description |
|--------|-------------|
| Statistics | Unterthiner per-layer stats (mean, std, spectral norm) → Ridge regression |
| MLP | Flattened weights → 3-layer MLP → accuracy prediction |
| NFN | Neural Functional Network (nfn library) → accuracy prediction |

### Protocol
- Training sizes: N ∈ {100, 250, 500, 1000, 2500, 5000}
- Test set: 500 held-out models (fixed)
- Random seeds: 10 per (N, method) pair
- Metrics: R² mean ± std, crossing point N*

---

## Limitations

- **Homogeneous Zoo**: Results may not generalize to heterogeneous architecture collections
- **R² Ceiling**: At large N, all methods approach ceiling (~0.98), limiting sensitivity
- **Single Task**: Accuracy prediction only; other property prediction tasks not evaluated
- **Single Architecture**: ResNet-20/CIFAR-10 only; other architectures deferred

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 10 exchanges, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed in discussion) |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Fixed-architecture model zoos have learnable weight-accuracy relationships
- **SH2 (Mechanism)**: Equivariance provides measurable inductive bias at small N
- **SH3 (Comparison)**: Deferred to Phase 5 baseline adaptation

**Status**: READY for Phase 2B verification protocol design
