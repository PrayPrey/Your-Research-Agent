# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-05T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: Gap-1
- **Gap Title**: No Standardized Δρ Benchmark Comparing Matched-Capacity NFN vs Flat MLP on Schurholt Zoos
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 14
- **Hypothesis ID**: H-NFNDeltaRho-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 14

**Convergence Reason**: All 6 criteria met at Exchange 14 — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS confirmed by Prof. Vera

### Key Insights
- The research question was sharpened from "does equivariance help?" to "how much, at matched capacity, with bootstrap CI?" — a more rigorously scientific formulation
- The Δρ ≥ 0.05 threshold is conservative and justified by the 0.05–0.15 range implied by existing heterogeneous comparisons (Navon et al. 2023 vs Unterthiner et al. 2020)
- CIFAR-10 statistical power analysis (n≈1,500, CI width ≈±0.03) reveals marginal detection threshold — asymmetric success criteria are scientifically appropriate
- The symmetrized MLP baseline granularity (neuron-level, not layer-level) is determined by the group action structure of feedforward weight spaces, not an arbitrary choice

### Breakthrough Moments
- **Exchange 4** (Prof. Pax): Formalized the three-step causal mechanism (orbit size → capacity allocation → ρ improvement), each step independently falsifiable — elevated the hypothesis from empirical claim to mechanistic theory
- **Exchange 6** (Prof. Rex): Identified CIFAR-10 power limitation and required Navon et al. (not Zhou et al.) as primary NFN to avoid attention-mechanism confound
- **Exchange 12** (Prof. Rex): Raised capacity-matching efficiency concern (A3) and proposed capacity curves as mitigation — converting a potential weakness into P4 (exploratory prediction)

---

## Final Hypothesis

### Title
Permutation-Equivariant Inductive Bias Advantage in Weight-Space Accuracy Prediction: A Controlled Δρ Benchmark

### Core Claim (Under-If-Then-Because)
Under conditions of matched encoder capacity (~500K parameters, ±5% via per-architecture width grid search) on the Schurholt et al. MNIST-CNN and CIFAR-10 model zoo benchmarks, **if** we replace a flat MLP encoder with a permutation-equivariant NFN encoder (Navon et al. 2023 equivariant architecture), **then** the Spearman rank correlation in test accuracy prediction increases by Δρ ≥ 0.05 on the MNIST-CNN zoo (bootstrap 95% CI lower bound > 0), **because** NFN encoders operate on the permutation-quotient weight space and direct all encoder capacity toward accuracy-predictive features rather than navigating the factorial-sized permutation orbits that confuse flat MLP encoders.

### Null Hypothesis (H0)
There is no significant difference (Δρ = 0) in Spearman rank correlation between matched-capacity NFN (Navon et al. equivariant, ~500K parameters) and flat MLP encoders for test accuracy prediction on the Schurholt MNIST-CNN and CIFAR-10 model zoos.

### Mechanism
Three-step causal chain:
1. **Orbit structure** (mathematical fact): Feedforward networks have |S_{n_1}| × ... × |S_{n_L}| equivalent weight configurations per function (neuron-permutation symmetry). Each layer width n_l contributes a factor of n_l! to the orbit size.
2. **Capacity allocation** (core mechanistic claim): Flat MLP encoders must partition capacity between learning accuracy-predictive features AND mapping equivalent permutations to consistent outputs. NFN encoders are equivariant by construction — all capacity goes to accuracy-predictive features.
3. **Rank correlation improvement** (empirical prediction): At matched capacity, NFN produces more consistent embeddings for functionally equivalent models → higher Spearman ρ on test accuracy prediction.

---

## Predictions

| ID | Type | Statement | Success Criterion | Falsification |
|----|------|-----------|------------------|---------------|
| P1 | Primary | NFN achieves Δρ ≥ 0.05 over flat MLP on MNIST-CNN; Δρ > 0 on CIFAR-10, both with 95% CI lower bound > 0 | Δρ(MNIST) ≥ 0.05 ∧ CI_lower(MNIST) > 0 ∧ Δρ(CIFAR) > 0 ∧ CI_lower(CIFAR) > 0 | Δρ(MNIST) < 0.05 OR CI crosses zero on either zoo |
| P2 | Secondary | Monotone symmetry spectrum: ρ(flat) < ρ(Deep Sets invariant) < ρ(NFN equivariant) on MNIST-CNN | Strict ordering holds on MNIST-CNN zoo | Any ordering violation |
| P3 | Mechanistic | Δρ largest in mid-accuracy tier (40th–60th percentile) of MNIST-CNN zoo | Δρ(mid) > Δρ(low) ∧ Δρ(mid) > Δρ(high) | Uniform or inverted pattern |
| P4 | Exploratory | NFN advantage largest at ≤100K params, decreasing toward 500K | Δρ(100K) > Δρ(500K) by >0.02 on MNIST-CNN | Constant Δρ across capacity levels |

---

## Novelty

**What's new:**
1. **Standardized Δρ with bootstrap CI** — first controlled matched-capacity comparison; resolves capacity-confound in all prior NFN vs flat MLP comparisons
2. **Cross-zoo consistency analysis** — first single-experiment comparison of Δρ on MNIST-CNN vs CIFAR-10 zoos
3. **Symmetry spectrum benchmark** — first Deep Sets intermediate baseline on Schurholt model zoos, completing the flat → invariant → equivariant spectrum

**How it differs from prior work:**
- Navon et al. (2023): no matched-capacity control, no bootstrap CI on Δρ, no cross-zoo analysis
- Zhou et al. (2023): same confounds; transformer attention adds additional variable beyond pure equivariance
- Schurholt et al. (2023): multi-encoder benchmark but capacity not standardized, no CI, no Deep Sets baseline
- Unterthiner et al. (2020): canonical flat MLP baseline only; different dataset, no equivariant comparison

---

## Experimental Design

**Datasets:**
- Schurholt ModelZooDataset: MNIST-CNN zoo (~4,000 checkpoints) and CIFAR-10 zoo (~1,500 checkpoints) with ground-truth test accuracies

**Encoders:**
- Flat MLP: concatenated weights → standard dense layers, ~500K params (primary baseline)
- Symmetrized MLP: Deep Sets neuron-level aggregation (ρ(Σφ(x_i))), ~500K params (intermediate baseline)
- NFN (Navon et al.): equivariant weight-space encoder, ~500K params (primary test)
- NFT (Zhou et al.): Neural Functional Transformer (robustness check only)

**Capacity Matching:** Width grid search per architecture to reach ~500K ±5% total parameters

**Metric:** Spearman rank correlation ρ; Δρ = ρ(NFN) − ρ(flat MLP); bootstrap 95% CI (n=1000 resamples)

**Pre-experiment checks:**
- Verify CIFAR-10 zoo architecture (no batch normalization)
- Verify minimum NFN parameter count for Schurholt weight tensor shapes

---

## Limitations

- CIFAR-10 zoo (n≈1,500) has marginal statistical power for detecting Δρ = 0.05 — primary success criterion relaxed to Δρ > 0 for CIFAR-10
- Results specific to Schurholt zoo generation procedure; external validity to other model populations not claimed
- Capacity matching (total parameter count ±5%) may not equalize per-parameter efficiency between encoder types — mitigated by capacity curves (P4)
- CIFAR-10 zoo architecture (BN presence) must be verified before Phase 4

---

## Key Assumptions

| ID | Assumption | Consequence if Violated | Mitigation |
|----|-----------|------------------------|------------|
| A1 | CIFAR-10 (n≈1,500) sufficient power for Δρ=0.05 | CIFAR-10 CI may cross zero at true Δρ=0.04 | Relaxed threshold: Δρ>0 (not ≥0.05) for CIFAR-10 |
| A2 | MNIST-CNN zoo trained without BN (permutation symmetry intact) | Mechanism prediction invalid if BN breaks symmetry | Verify from Schurholt et al. (2022) supp. before Phase 4 |
| A3 | Matching total params (±5%) is fair capacity comparison | NFN and flat MLP have different per-param efficiency | Report capacity curves as supplementary analysis |
| A4 | Schurholt zoo diversity sufficient for the prediction task | Internal validity only; no external generalizability claim | Scope hypothesis explicitly to Schurholt zoo |
| A5 | Navon et al. NFN tunable to ~500K params for Schurholt weight shapes | Capacity matching procedure fails | Pre-check parameter counts before experiments |

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria confirmed at Exchange 14 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Verify CIFAR-10 zoo BN status; pre-check NFN min param count |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Hypothesis ID: H-NFNDeltaRho-v1 | Gap: Gap-1 | Exchanges: 14 | Mode: UNATTENDED*
