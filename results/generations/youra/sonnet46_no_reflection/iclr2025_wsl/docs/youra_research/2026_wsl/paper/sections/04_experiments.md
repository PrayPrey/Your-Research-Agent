# Experimental Setup

Our experimental design tests three sequential questions corresponding to the three
necessary preconditions for orbit-PE to enable cross-architecture weight representation.
The experiments are structured as a prerequisite chain: we test existence before mechanism
before variance dominance, gate each step with a MUST_WORK criterion, and design H-M2
with an explicit pivot path if the variance gate fails.

## 4.1 Experimental Questions

**Q1 (H-E1, Existence):** Is the input/output channel permutation group a functionally
exact symmetry for all linear operator types — Conv2d, Linear, and MultiheadAttention?
*Gate:* Mean |Δacc| < 0.1% across all layer types and architectures.

**Q2 (H-M1, Mechanism — Computability):** Is orbit-PE computable for all layer types
with practical overhead (≤ 1.2× sequential PE), using a unified codebase without
architecture-specific branches?
*Gate:* overhead_ratio_mean ≤ 1.2×, HAS_ARCH_BRANCHES = False, dim_consistent = True.

**Q3 (H-M2, Mechanism — Variance):** Does the permutation orbit explain the majority
(> 60%) of weight-space variance, compared to GL-orbit variance, measured on CNN Zoo
checkpoint trajectories?
*Gate:* Var_perm / (Var_perm + Var_GL) > 0.60 (pre-specified pivot if gate fails).

## 4.2 Datasets

**Small CNN Zoo (CIFAR-10-GS)** [Unterthiner et al., 2020]: 10,000+ small CNNs trained on
the CIFAR-10 grayscale variant, with full training trajectories at epochs 0–50 and final
test accuracy. We use:
- H-E1: 200 checkpoints (random sample) for symmetry validation
- H-M1: 100 checkpoints for overhead benchmarking
- H-M2: 1,000 models × 50 epochs (50,000 checkpoints) for variance decomposition

*Rationale:* Standard weight space learning benchmark; available with training trajectories
essential for H-M2's trajectory analysis; sufficient scale for statistical robustness.

**Small Transformer Zoo** [Tran-Viet et al., 2024]: 125,000 small transformer checkpoints
trained on MNIST and AGNews tasks. We use:
- H-E1: 250 checkpoints for cross-architecture symmetry validation
- H-M1: 100 checkpoints for cross-architecture overhead benchmarking

*Rationale:* Provides transformer architecture coverage required for cross-architecture
symmetry validation; standard benchmark in the NFN literature.

**Note:** SVHN-GS cross-dataset stability (planned for H-M2) was not performed — SVHN Zoo
data was unavailable at experiment time. The CIFAR-10-GS result (n = 1,000 models × 50 epochs)
provides sufficient statistical confidence for the refutation regardless.

## 4.3 Baselines and Controls

**Sequential PE (H-E1 control):** The null baseline — applying the same channel permutation
without orbit-PE shows the functional symmetry directly (|Δacc| = 0 iff the permutation
is a valid symmetry).

**Sequential PE timing (H-M1 baseline):** Wall-clock time of sequential positional encoding
as the reference for overhead ratio computation.

**GL orbit variance (H-M2 baseline):** The competing explanation — if GL orbit variance
dominates permutation orbit variance (ratio < 0.60), pure orbit-PE is insufficient and
hybrid encoding is required.

**Random permutation ablation (planned for H-M3, not executed):** SANE+random-PE as a
control to distinguish orbit-PE signal from random positional encoding. This ablation was
not run because H-M3 was blocked by H-M2's MUST_WORK failure.

## 4.4 Evaluation Metrics

| Metric | Hypothesis | Threshold | Rationale |
|--------|------------|-----------|-----------|
| Mean \|Δacc\| | H-E1 | < 0.1% | Functional symmetry criterion |
| Orbit-PE success rate | H-E1 | = 1.0 | All layer types must be handled |
| Overhead ratio (mean) | H-M1 | ≤ 1.2× | Practical efficiency bound |
| HAS_ARCH_BRANCHES | H-M1 | False | Unified codebase requirement |
| dim_consistent | H-M1 | True | Consistent output dimensionality |
| Var_perm/(Var_perm+Var_GL) | H-M2 | > 0.60 | Variance dominance criterion |
| Layer-type breakdown | H-M2 | Diagnostic | Conv2d vs. Linear stratification |

## 4.5 Implementation Details

All experiments run on CPU (single core) to isolate encoding computation from GPU variance.
H-E1 and H-M1 use PyTorch 2.x with the SANE tokenization framework as a base. H-M2 uses
SVD-based orbit projectors (scipy.linalg.svd) and polar decomposition for GL projection.
Orbit basis dimensionality d_pe = 64 = token_dim throughout. Seeds: fixed at 42 for all
sampling; H-E1 uses 10 permutation seeds per checkpoint to verify per-seed stability.

Code infrastructure:
- `h-e1/code/orbit_pe.py`: Core orbit-PE computation (dispatch dict, no branches)
- `h-m1/code/orbit_pe_computer.py`: OrbitPEComputer nn.Module wrapper + timing benchmark
- `h-m2/code/orbit_projector.py`: Orbit basis (SVD) + GL projection (polar decomp)
- `h-m2/code/variance_decomposer.py`: Trajectory variance decomposition
- `h-m2/code/evaluate.py`: Zoo-scale pipeline (1,000 models)
