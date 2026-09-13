# Phase 2A Extended: CS-AITE Hypothesis Summary

**Date:** 2026-02-06
**Hypothesis ID:** H1-CS-AITE-v1.1
**Confidence:** 8.5/10 (High)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Core Hypothesis:** Applying compressed sensing-inspired random projections to high-dimensional brain data (fMRI/EEG) before information-theoretic estimation enables scalable mutual information computation with explicit finite-sample error bounds for Gaussian/linear dependencies, achieving 10-50x reduction in sample complexity (N=1,000 vs. N=50,000) while preserving ±0.05 bit accuracy through RIP guarantees.

**Gap Addressed:** Gap 2 - Scalable Estimation Methods for High-Dimensional Cognitive Data

**Key Innovation:** First framework combining compressed sensing theory (RIP-based dimensionality reduction) with information-theoretic estimation, providing theoretically grounded finite-sample error bounds for whole-brain MI analysis.

---

## Clarified Hypothesis Statement

### Main Claim

CS-AITE with compression ratio m/n = 0.05 estimates mutual information within ±0.05 bits using N = 1,000 samples, whereas full-dimensional methods require N = 50,000 samples for comparable accuracy, on Gaussian brain data with n = 10,000 dimensions.

### Alternative Hypothesis (H0)

Compressed sensing projections do NOT preserve information-theoretic quantities, resulting in errors >20% worse than baseline methods and requiring equal or greater sample sizes (N ≥ 50,000).

---

## Causal Mechanism (If-Then-Because)

**IF** high-D brain data compressed via RIP-satisfying projections (δ < 0.3)
**AND** data is Gaussian/Gaussianizable
**AND** signal is sparse (s/n < 0.2)

**THEN** compressed MI estimates preserve accuracy: |MI(X;Y) - MI(Φx;Φy)| ≤ ε(δ,m,s,n)

**BECAUSE:**
1. RIP preserves second moments → preserves correlation ρ
2. Gaussian MI = -½log(1-ρ²) → ρ preserved → MI preserved
3. Sample complexity reduces: O(n²) → O(m²) where m = O(s log n)
4. Adaptive method selection maintains accuracy across sparsity regimes

---

## Key Variables

| Variable | Type | Range | Measurement |
|----------|------|-------|-------------|
| Data dimensionality (n) | IV | 100-100,000 | Direct count |
| Compression ratio (m/n) | IV | 0.01-0.20 | Controlled |
| Signal sparsity (s) | IV | 10-5,000 | L0 norm |
| Sample size (N) | IV | 100-100,000 | Direct count |
| RIP constant (δ) | IV | 0.01-0.30 | Theoretical/empirical |
| MI estimation error | DV | 0.001-1.0 bits | |MI_true - MI_est| |
| Computational time | DV | 0.1-1000 sec | Wall-clock |
| Sample complexity | DV | 100-100,000 | Binary search for ±0.05 bit @ 95% CI |

---

## Testable Predictions

**PP1 (Primary):** CS-AITE (m/n=0.05) achieves ±0.05 bit accuracy with N=1,000 vs. N=50,000 for baseline

**SP1:** Error bound |MI_true - MI_est| ≤ 0.01·√(s·log(n)/m) holds with probability ≥ 0.99

**SP2:** Adaptive L1-penalized estimator outperforms kernel MI by ≥20% MSE for sparse data (s/m < 0.1)

**SP3:** HCP motor task: MI correlates with behavior at ρ > 0.8, computes in <10 seconds (vs. >300 sec baseline)

**SP4:** Sparsity threshold s/n > 0.2 triggers <50% accuracy improvement (automatic fallback)

**SP5:** Non-Gaussian data (D_KL > 0.1) causes error >0.2 bits (demonstrating Gaussian necessity)

---

## Scope & Limitations

**Applies To:**
- Gaussian/Gaussianizable high-D brain data (fMRI n>10K, EEG n>32)
- Sparse signals (s/n < 0.2) in wavelet/Fourier/spatial basis
- Linear/Gaussian dependencies in cognitive tasks
- Medium-large samples (N=1K-10K after compression)

**Does NOT Apply To:**
- Non-Gaussian non-Gaussianizable data (D_KL > 0.1)
- Non-sparse signals (s/n > 0.2)
- Nonlinear MI (XOR-like cognitive gating)
- Ultra-fast cognitive switching (<100ms regime changes)

**Known Limitations:**
- Gaussian constraint (~50% of use cases)
- RIP verification probabilistic (1-5% failure rate)
- Cascaded CS error accumulation (multi-modal data)
- Real brain data lacks ground truth MI

---

## Contributions

**Theoretical:**
1. **IT-RIP Condition:** Prove RIP preserves MI for Gaussian case with error ε = δ/(1-ρ²)
2. **Finite-Sample Bounds:** Explicit formula combining CS complexity O(s log n) with MI estimation O(m²)
3. **Sample Complexity Theory:** 10-50x reduction for typical brain data (s/n ~ 0.1)

**Methodological:**
1. **CS-AITE Framework:** 4-stage architecture (acquisition → profiling → estimation → validation)
2. **Cascaded CS:** Multi-modal brain data compression (spatial → temporal → spectral)
3. **Adaptive Selection:** Data-driven estimator choice (L1/kernel/neural) with <30ms overhead

**Practical:**
1. **Whole-Brain IT Mapping:** 100K voxels at 1K-5K voxel cost
2. **Real-Time BCI:** <100ms latency for closed-loop brain-computer interfaces
3. **Clinical Biomarkers:** Scale MS detection, meditation states to population studies (N>1,000)
4. **Benchmarking Framework:** 19,200 synthetic datasets with known MI for community validation

---

## SOTA Comparison

| Method | Sample Complexity | Bounds | Nonlinear | Real-Time | Theoretical Guarantee |
|--------|------------------|--------|-----------|-----------|---------------------|
| Kernel MI (Azarmi 2023) | O(N²)~50K | ✗ | ✓ | ✗ | ✗ |
| infomeasure (Büth 2025) | Unknown | ✗ | ✓ | ~ | ✗ |
| MINE (Belghazi 2018) | O(N)~10K+ | ✗ | ✓ | ✗ | ✗ |
| Symbolic MI (Potash 2025) | O(N)~1K | ✗ | ✓ | ✓ | ✗ |
| PCA + Gaussian MI | O(n²+m²) | ✗ | ✗ | ✓ | ~ (variance) |
| **CS-AITE (Ours)** | **O(s log n + m²)~1K** | **✓** | **✗ (v1.1)** | **✓** | **✓ (Gaussian)** |

**Unique Value:** Only method with finite-sample error bounds + 10-50x sample reduction + real-time capability for Gaussian MI regime.

---

## Key Related Work

**Foundations:**
- Candès et al. (2006) - CS theory, RIP definition
- Baraniuk et al. (2008) - RIP probabilistic proofs
- Tishby et al. (1999) - Information Bottleneck principle
- Cover & Thomas (2006) - Data Processing Inequality

**IT Estimation:**
- Kraskov et al. (2004) - k-NN MI estimator
- Belghazi et al. (2018) - MINE neural estimator
- Büth et al. (2025) - infomeasure Python package

**CS Applications (Cross-Domain):**
- Chen et al. (2022) - Minimax covariance estimation under CS ⭐
- Park & Gao (2023) - Cascaded CS optical imaging
- Li et al. (2024) - CS for non-stationary stochastic systems

**IT Cognitive Neuroscience:**
- Ibáñez-Molina et al. (2020) - MIMR for EEG (low-dimensional)
- Azarmi et al. (2023) - Kernel MI for fMRI (sample complexity bottleneck)
- Potash et al. (2025) - Symbolic MI meditation (single-subject)
- Weingarten et al. (2024) - IB tighter bounds (compression + preservation)

---

## Phase 2B Sub-Hypotheses Preview

**SH1 (Existence):** CS compression preserves MI within ±0.05 bits
**SH2 (Mechanism):** Error bounded by ε = δ/(1-ρ²) + O(δ²)
**SH3 (Comparison):** ≥10x sample reduction vs. baselines with accuracy parity
**SH4 (Boundaries):** Predictable failure at s/n>0.2, D_KL>0.1, δ>0.3
**SH5 (Real-World):** HCP validation ρ>0.8, ±15% ROI agreement, <10s compute

**Execution Order:** SH1 → SH2 → SH3 → SH4 → SH5 (sequential dependency)

---

## Falsification Criteria

Hypothesis **FALSIFIED** if:
1. CS-AITE requires N ≥ 40,000 (vs. predicted 1,000) for ±0.05 bit accuracy
2. MSE exceeds baseline by >20% on >30% of datasets
3. RIP empirical failure rate >10% on datasets meeting sparsity criterion
4. HCP motor task correlation ρ < 0.5 (vs. predicted >0.8)
5. Sample complexity reduction <5x (vs. predicted 10-50x)

---

## Open Questions for Phase 2B

**Technical:**
1. Cascaded CS error: additive or multiplicative?
2. Optimal δ threshold: can relax <0.3 to <0.5?
3. Copula selection for Gaussianization: which type?
4. Basis selection: wavelet, Fourier, spatial, or data-driven?

**Theoretical (v2.0):**
5. Can IT-RIP extend to nonlinear MI via copulas?
6. Distributed CS for privacy-preserving population studies?

**Experimental (Phase 2C):**
7. HCP sample size for adequate power?
8. Fair baseline hyperparameter tuning protocol?

**Scope (User Decision):**
9. v1.1 (Gaussian, 6 months) vs. v2.0 (nonlinear, 12 months)?
10. Application priority: BCI, clinical, or population neuroscience?

---

## Readiness Status

- [x] Falsifiable with explicit criteria
- [x] Variables operationalized with measurement protocols
- [x] Mechanism decomposed with evidence
- [x] Assumptions testable
- [x] Predictions quantitative with statistical tests
- [x] Baselines identified
- [x] Statistical design specified
- [x] Sub-hypotheses decomposable
- [x] Success criteria defined
- [x] Dependencies mapped

**✅ READY FOR PHASE 2B**

---

## Next Steps

**Phase 2B - Research Planning:**
1. Decompose H1-CS-AITE into 5 sub-hypotheses (SH1-SH5)
2. Design experiments for each SH with quantitative success criteria
3. Establish verification order and dependencies
4. Plan resources (datasets, compute, timeline)

**Expected Output:** Verification roadmap with prioritized experiments ready for Phase 2C experiment design specification.

---

*Full Documentation: 02a_extended_hypothesis_full.md*
*Source Round: 02a_round_1_discussion_CS-AITE.md*
*Generated: 2026-02-06 via YouRA Phase 2A Extended (YOLO Mode)*
