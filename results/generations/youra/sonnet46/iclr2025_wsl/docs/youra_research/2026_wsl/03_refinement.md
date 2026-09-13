# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-16T10:55:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Free-Parse)
- **Gap ID**: gap_1_nft_vs_flat_mlp
- **Gap Title**: No Controlled Comparison of NFT vs Flat-MLP on FC-MLP Model Zoo Generalization Gap Prediction
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 convergence criteria met at exchange 16: hypothesis specific with pre-registered quantitative thresholds, mechanism causal chain specified (4 steps), 3 testable predictions with falsifiers, novelty confirmed as literature gap, feasibility verified on existing data, all major objections addressed.

### Key Insights

- The comparison should be framed as a **scientific probe** of weight-space structure: whether NFT wins or loses tells us something fundamental about what generalization gap encodes in FC-MLP weight space.
- **Neuron non-identifiability** in overparameterized MLPs makes architectural equivariance theoretically preferable to canonicalization — equivariant architectures process the quotient space directly without requiring bijective neuron alignment.
- The **three-tier experiment structure** (invariant statistics → augmentation baseline → architectural equivariance) creates publishable findings at each tier, regardless of outcome direction.
- The **alignment diagnostic** is a mandatory pre-modeling step that makes interpretation robust to either high-entropy or low-entropy zoo findings.

### Breakthrough Moments

- **Exchange 4** (Prof. Rex): Introduced the alignment diagnostic requirement — this became a mandatory pre-experiment step preventing false interpretation.
- **Exchange 8** (Prof. Rex): Identified the cross-layer attention ablation as non-negotiable — became Experiment 5 in the final suite.
- **Exchange 13** (Prof. Pax): Identified neuron non-identifiability as a theoretical scope condition on canonicalization.
- **Exchange 14** (Dr. Nova): Reframed non-identifiability as a STRENGTH of equivariant architectures — they don't need bijective alignment.
- **Exchange 15** (Prof. Vera): Formalized all pre-registered thresholds: Δρ < 0.02, R² ≥ 0.40, ΔR² ≥ 0.10, Δ_transfer < 0.05.

---

## Final Hypothesis

### Title
**NFT vs. Flat-MLP for FC-MLP Model Zoo Generalization Gap Prediction: Structural Equivariance as a Necessary Inductive Bias**

**Hypothesis ID:** H-NFT-GenGap-v1

### Core Claim (Under-If-Then-Because)

> **Under** FC-MLP model zoo conditions (Unterthiner benchmark, 2-4 layer networks, MNIST/CIFAR),
> **if** Neural Functional Transformers (NFT; Zhou et al. 2023) are used as weight-space encoders instead of flat-MLP baselines,
> **then** generalization gap prediction will show improved robustness to neuron permutation (flat Δρ curve) and superior cross-pipeline transfer,
> **because** NFT's within-layer permutation equivariance combined with cross-layer attention aggregates neuron influence concentration signals that are functionally meaningful and invariant to the permutation symmetry group of FC-MLP weight spaces.

### Null Hypothesis (H0)

> There is no significant difference in generalization gap prediction performance between NFT encoders and flat-MLP baselines on the Unterthiner FC-MLP model zoo. Any observed differences are attributable to post-hoc canonicalization or permutation augmentation achieving equivalent invariance.

### Mechanism (4-Step Causal Chain)

1. **Permutation Symmetry**: FC-MLP weight spaces have inherent permutation symmetry — any neuron permutation (consistent row/column) yields equivalent function.
2. **Flat-MLP Symmetry-Breaking**: Flat-MLP treats neuron positions as meaningful, making performance dependent on statistical regularities in neuron ordering (low permutation entropy → higher performance from alignment artifacts).
3. **NFT Equivariant Aggregation**: NFT's within-layer equivariant attention aggregates neuron influence concentration statistics (Gini coefficient, spectral decay) that are invariant to ordering and correlate with overfitting risk (high concentration = overfitting).
4. **Cross-Layer Robustness**: NFT's cross-layer attention captures inter-layer co-adaptation; under distribution shift (different training pipelines), structural invariance preserves predictive fidelity while flat-MLP representations degrade.

---

## Predictions

### P1 (PRIMARY): Permutation Robustness
- **Statement**: NFT achieves permutation-robust performance (Δρ(s=1.0) < 0.02, CI includes zero); flat-MLP shows significant degradation (Δρ > 0.02, CI excludes zero)
- **Test**: Permutation severity curves s ∈ {0, 0.25, 0.5, 1.0}, bootstrap CIs
- **Success**: NFT Δρ < 0.02; flat-MLP Δρ > 0.02; NFT ρ(s=0) ≥ flat-MLP ρ(s=0)
- **Falsifier**: NFT shows permutation sensitivity, or flat-MLP achieves permutation robustness without equivariance

### P2: Cross-Pipeline Transfer Robustness
- **Statement**: NFT transfer degradation Δ_transfer < 0.05; flat baselines Δ_transfer > 0.10
- **Test**: Partition zoo by regularization regime (KS test p < 0.01 confirms structural shift)
- **Success**: Significant difference in Δ_transfer between NFT and flat baselines (Holm-corrected)
- **Falsifier**: NFT and flat-MLP+perm-aug show indistinguishable Δ_transfer

### P3: Mechanism Mediation
- **Statement**: NFT embeddings add ΔR² ≥ 0.10 beyond structural concentration metrics (Gini, σ₁/Σσᵢ), significantly exceeding flat-MLP ΔR²
- **Test**: Hierarchical regression: concentration metrics (block 1) → encoder embeddings (block 2); compare ΔR²
- **Success**: Concentration metrics R² ≥ 0.40; NFT ΔR² ≥ 0.10 and > flat-MLP ΔR²
- **Falsifier**: NFT ΔR² < 0.05, or not significantly greater than flat-MLP ΔR²

---

## Novelty

**What's New**: First controlled comparison of NFT (permutation-equivariant weight encoder) vs. flat-MLP for property prediction on the Unterthiner FC-MLP model zoo. This comparison provably does not exist in the current literature:
- Zhou et al. (2023) evaluated NFT only on INR (implicit neural representation) classification tasks
- Unterthiner et al. (2020) predates NFT by 3 years
- No bridging study connects them

**Key Innovation**: Using this comparison as a scientific probe — framed so that any outcome direction (NFT wins, ties, or loses) tells us something fundamental about weight-space meta-modeling.

**Differentiation from Prior Work**:
- vs. NFT (Zhou 2023): Applied to property prediction task, not INR classification
- vs. Unterthiner (2020): Introduces equivariant encoder comparison to flat-MLP baseline
- vs. Schürholt (2021): Architectural equivariance vs. augmentation-based invariance on the same benchmark
- vs. DWSNets (Navon 2023): FC-MLP-compatible alternative; DWSNets excluded (runtime incompatible)

---

## Experimental Design

**Dataset**: Unterthiner FC-MLP Model Zoo (MNIST + CIFAR-10 subsets), publicly available, 120K models

**Full Experiment Suite (7 experiments, all on existing Unterthiner data)**:

| Experiment | Purpose | Key Metric |
|---|---|---|
| 1. Alignment diagnostic | Measure pairwise neuron alignment — determine permutation entropy | Hungarian + cosine similarity distributions |
| 2. Main comparison | NFT vs. all baselines for generalization gap + accuracy | Spearman ρ, MSE |
| 3. Permutation stress test | ρ(s) degradation curves | Δρ(s=1.0) with bootstrap CIs |
| 4. Canonicalization ablation | Compare ℓ2-sort, Hungarian, CKA, spectral alignment | Spearman ρ per variant, Holm correction |
| 5. Cross-layer ablation | Full NFT vs. NFT-within-layer-only | Δ_transfer comparison |
| 6. Cross-pipeline transfer | Structural pipeline shift robustness | Δ_transfer for all encoders |
| 7. Mechanism mediation | Concentration metrics → encoder embeddings hierarchical regression | ΔR² |

**Baselines**: Flat-MLP (raw), Flat-MLP+perm-aug, Flat-MLP+ℓ2-sort, Flat-MLP+oracle-Hungarian (multi-objective), Permutation-invariant statistics regressor (ceiling), NFT-ablated (within-layer only), NFT (full)

---

## Limitations

- Bounded to FC-MLP zoo with fixed architecture dimensions (2-4 layers, consistent hidden width)
- Neuron non-identifiability means oracle canonicalization is theoretically underpowered — acknowledged scope condition
- NFT cross-layer architecture must be confirmed from implementation; if absent, compositional mechanism claim is dropped
- Prediction ceiling must be ≥ 0.40 R² for architecture comparisons to be meaningful
- Extension to CNNs, transformers, or heterogeneous model hubs requires separate validation (explicit future work)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 16 with pre-registered thresholds |
| **Clarity Verified** | Yes |
| **Feasibility** | All experiments on existing Unterthiner data; no new benchmarks, synthetic data, or human evaluation |
| **Remaining Objections** | 3 scope conditions (all mitigated in experiment suite) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Participants: Dr. Nova 🔭 · Prof. Vera 🔬 · Dr. Sage 🎯 · Prof. Pax ⚙️ · Dr. Ally 🛡️ · Prof. Rex 🔍*
