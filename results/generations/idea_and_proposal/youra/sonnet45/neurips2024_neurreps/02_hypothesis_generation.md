# Phase 2B Summary: Clarified Hypothesis

**Date:** 2026-02-06
**Researcher:** Pray
**Hypothesis ID:** H-NEURREPS-001
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis:** Topological-Geometric Neural Networks (TGNNs) unify differentiable persistent homology layers with E(n)-equivariant architectures to learn both local geometric symmetries and global topological structure. This dual constraint will improve accuracy by 10-15% and sample efficiency by 2-3× on topologically-structured tasks (molecular ring detection, 3D genus classification, neural circuit analysis) compared to purely geometric or topological approaches.

**Confidence:** 0.85 (High)

**Key Innovation:** First end-to-end learnable architecture enforcing both group-theoretic equivariance (local symmetries) and topological invariants (global structure) simultaneously, enabled by category theory framework and differentiable persistent homology.

**Feasibility:** Medium difficulty (4-5 months implementation), building on existing libraries (e3nn, giotto-tda, PyTorch) with phased validation approach.

---

## Core Hypothesis Statement

**Main Hypothesis (H1):**

Neural networks integrating differentiable persistent homology layers with E(n)-equivariant convolutions will achieve 10-15% higher accuracy and 2-3× sample efficiency on tasks with topological structure (molecular rings, 3D genus, neural circuits) compared to geometric-only baselines, because topological priors reduce hypothesis space by encoding global structural constraints that local geometric features cannot capture.

**Alternative Hypothesis (H0):**

Geometric features alone are sufficient—adding topology provides <5% improvement and <1.5× sample efficiency because local geometry already captures relevant structure, and topological computation overhead outweighs benefits.

---

## Key Variables

| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | Architecture Type | Geometric-only / Topological-only / Unified TGNN |
| **Independent** | Local Sampling k | k ∈ {100, 200, 500, 1000} nearest neighbors |
| **Independent** | Filtration Temperature τ | τ ∈ {0.01, 0.05, 0.1, 0.5} (soft-sorting smoothness) |
| **Dependent** | Task Accuracy | Classification % or Regression MAE on test set |
| **Dependent** | Sample Efficiency | Training samples to reach 90% max performance |
| **Dependent** | Betti Number Recovery | % correct β₀, β₁, β₂ on synthetic topology-labeled data |
| **Dependent** | Robustness | Accuracy drop under Gaussian noise σ ∈ {0.05, 0.1, 0.2} |
| **Controlled** | Dataset | QM9 (molecules), ModelNet40 (3D shapes), Connectome (circuits) |
| **Controlled** | Training | AdamW, cosine schedule, batch 32, 200 epochs |

---

## Causal Mechanism

**Chain:**

1. **Topological Constraint Encoding** → Persistent homology layers compute multi-scale topological signatures (Betti numbers β₀, β₁, β₂) across filtration
2. **Hypothesis Space Reduction** → Topological features constrain representations to favor correct topology (e.g., ring detection benefits from β₁ loop constraint)
3. **Complementary Fusion** → Topological (global) + Geometric (local) features concatenated and processed by fusion MLP
4. **Performance Improvement** → Sample efficiency ↑ (topological supervision signal) and accuracy ↑ (disambiguates similar local geometries)

**Key Evidence:**
- Persistence stability theorem guarantees topological features are stable under perturbations → regularization effect
- Maruyama (2025) category theory proves topological + geometric constraints are compositional (no conflict)
- perslay (2020) empirical evidence shows topology improves shape classification

---

## Testable Predictions

**P1 (Primary):** TGNN achieves 10-15% higher test accuracy on topological tasks vs. geometric baseline (p < 0.05, 5-fold CV)

**P2:** TGNN requires 2-3× fewer training samples to reach 90% max accuracy (learning curve analysis)

**P3:** Topological layers show high gradient magnitude (top 20%) when topology is task-relevant (gradient attribution)

**P4:** Local topology (k=100-500) achieves ≥95% of global topology performance (validates local sampling)

**P5:** TGNN shows +20% robustness under noise perturbations (persistence stability effect)

**P6:** Betti number recovery >90% on synthetic data (validates differentiable approximation quality)

**Falsification Criteria:**
- <5% accuracy improvement (P1 fail)
- No sample efficiency gain (P2 fail)
- Topological features unused (P3 fail)
- >5× training time overhead (impractical)
- <70% Betti recovery (approximation too lossy)

---

## Contributions

### Theoretical
Category theory framework unifying algebraic topology (persistent homology) with geometric deep learning (group equivariance). Proves topological and geometric constraints are compositional via functorial composition. Theoretical sample complexity bound explains 2-3× efficiency gain.

### Methodological
1. **Differentiable Persistent Homology Layers:** First fully differentiable PH compatible with PyTorch autodiff (soft-sorting, chain complex gradients, landscape vectorization)
2. **Integration Protocol:** Architecture pattern combining equivariant layers → local sampling → persistence layers → fusion
3. **Local Sampling Strategy:** Scalable PH via k-NN (O(k³) vs. O(n³) global)

### Practical
Applications to molecular property prediction (QM9), 3D shape classification (ModelNet40), neural circuit analysis (connectomes). Target 10-15% accuracy improvement with 2-3× sample efficiency. Open-source library (`tgnn`) built on PyTorch + e3nn + giotto-tda.

---

## Sub-Hypotheses for Phase 2B

**SH1 (Existence):** Differentiable PH layers compute topological features with >90% Betti number recovery and stable gradients (SNR > 10)

**SH2 (Mechanism):** Topological and geometric features are complementary (correlation < 0.7), and fusion outperforms either alone by ≥5%

**SH3 (Comparison):** TGNN outperforms geometric (E3nn, SchNet) and topological (perslay) baselines by ≥10% accuracy with 2-3× sample efficiency (p < 0.05)

---

## Scope & Limitations

**Applies To:**
- Tasks with topological structure (molecular rings, 3D genus, circuit connectivity)
- Point clouds, graphs, 3D meshes (finite metric spaces)
- Medium scale (10K-500K samples, 100-5K points per sample)

**Does NOT Apply To:**
- Purely local tasks (texture, pointwise regression)
- Images (no natural topological space)
- Very large point clouds (>10K points without subsampling)
- Tasks where topology is constant or irrelevant

**Limitations:**
- 2-3× training time overhead
- Local topology approximation (k-NN, not global)
- Approximation error from differentiable persistence (bounded but non-zero)
- Requires domain knowledge to identify topological tasks

---

## Related Work

| Work | Relation | Differentiation |
|------|----------|----------------|
| **Bronstein et al. (2021) GDL** | Foundation | We add topology to geometric framework |
| **Maruyama (2025) Categorical Equiv.** | Foundation | We apply category theory to unify topology + geometry |
| **e3nn (Geiger & Smidt)** | Baseline + Extension | We add topological layers to e3nn backbone |
| **perslay (Carrière 2020)** | Comparison | We learn topology end-to-end, not precompute |
| **TopoReg (2021, inferred)** | Comparison | We extract topological features, not just regularize |
| **SchNet, GemNet** | Comparison | Geometric baselines lacking topology |

---

## Phase 2B Readiness

**Technical:** ✅ Math foundations, prior art, implementation tools, datasets, resources identified

**Theoretical:** ✅ Hypothesis clear, assumptions explicit, scope defined, falsification criteria specified

**Experimental:** ✅ Sub-hypotheses, metrics, statistical plan, baselines all defined

**Readiness Score:** 10/10

---

## Open Questions (Medium Priority)

1. **Fusion Architecture:** Concatenate vs. add vs. attention? (Ablation study in SH2)
2. **Topological Loss:** Explicit Betti regularization or task loss only? (Test in SH1)
3. **Scalability:** Larger point clouds (>5K points)? (Defer to Phase 3)
4. **Advanced Descriptors:** Beyond Betti numbers? (Exploratory Phase 4)
5. **Cross-Domain Transfer:** Molecule → 3D shape? (Transfer learning Phase 4)

---

## Next Steps

**Phase 2B:** Decompose main hypothesis into detailed sub-hypotheses (SH1, SH2, SH3) with verification protocols, success criteria, and experimental designs for each component.

**Phase 2C:** Generate experiment specifications for each sub-hypothesis (datasets, architectures, training procedures, evaluation metrics).

**Phase 3:** Create implementation plan (PRD, Architecture, PRP) for TGNN codebase.

**Phase 4:** Implement and validate through Coder-Validator loop.

---

*Full details in: `02a_extended_hypothesis_full.md`*
*Generated: 2026-02-06 | YouRA Phase 2A-Extended (YOLO Mode)*
