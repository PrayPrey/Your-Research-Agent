# Phase 2A Extended: Hypothesis Summary for Phase 2B Planning

**Date:** 2026-02-08
**Hypothesis ID:** H-RegML-001
**Confidence:** 0.80 (FEASIBLE)
**Source:** Round 2 - Cryptographically-Amortized Privacy-Preserving Explainability via SMPC Aggregation

---

## Core Hypothesis

**Main Claim:** Cryptographic aggregation of model predictions via Secure Multi-Party Computation (SMPC) enables privacy-preserving explainability (LIME/SHAP) with **constant privacy budget cost O(1)** rather than linear cost O(N), achieving explanation fidelity **>0.8 at ε=1.0** compared to **<0.3 for traditional per-query differential privacy**.

**Key Innovation:** Budget amortization through cryptographic confidentiality (SMPC) instead of statistical noise (per-query DP), enabling 2-3× fidelity improvement at regulatory privacy levels (GDPR ε ≤ 1.0).

---

## Testable Predictions (Phase 2B Decomposition)

### Primary Prediction (P1): Budget Amortization Advantage

**Prediction:** For fixed ε_total = 1.0 and N ∈ {1000, 5000, 10000}, SMPC-LIME achieves Spearman ρ ≥ 0.75, while per-query DP-LIME achieves ρ < 0.40.

**Sub-Hypotheses for Phase 2B:**

**SH1 (Existence):** SMPC achieves ε-DP with O(1) privacy cost independent of N
- **Verification:** Privacy auditing (membership inference attacks), theoretical proof via DP composition
- **Metric:** ε_total remains constant (±10% variance) across N ∈ {1000, 5000, 10000}

**SH2 (Mechanism):** Fidelity degradation is determined by final DP noise ε_explanation, not SMPC aggregation
- **Verification:** Ablation study (SMPC-no-noise vs. noise-only vs. full pipeline)
- **Metric:** ρ_SMPC-no-noise > 0.95 (confirms SMPC introduces <5% fidelity loss)

**SH3 (Comparison):** SMPC-LIME achieves ≥2× fidelity vs. per-query DP at ε_total = 1.0, N ≥ 5000
- **Verification:** Controlled experiment with statistical significance testing (paired t-test, p < 0.01)
- **Metric:** ρ_SMPC / ρ_DP ≥ 2.0 on ImageNet (ResNet-18, 1000 images)

### Secondary Predictions

**P2 (Hardware Acceleration):** POTA FPGA reduces latency by ≥30× vs. CPU (target: 100×)
- **SH4:** Speedup ≥ 30×, latency_POTA ≤ 3 seconds for N=5000
- **Verification:** Benchmark on CPU (Intel Xeon) vs. POTA FPGA

**P3 (Adaptive Optimization):** Mutual information minimization reduces privacy budget by ≥20% for ρ = 0.75
- **SH5:** Budget reduction = (ε_fixed - ε_adaptive) / ε_fixed ≥ 20%
- **Verification:** Paired t-test comparing fixed vs. MI-optimized noise allocation

**P4 (Generalization):** Fidelity advantage (ρ_SMPC / ρ_DP ≥ 2.0) holds across architectures
- **SH6:** Maintained for ResNet-18 (vision) AND BERT-base (NLP), degradation <30% between architectures
- **Verification:** Cross-architecture validation on ImageNet + GLUE SST-2

---

## Implementation Specification (Phase 2C/3 Inputs)

### Technical Stack

**Frameworks:**
- SMPC: CrypTen (PyTorch-based, CPU/GPU support)
- XAI: LIME, SHAP (Python libraries, drop-in API compatibility)
- Hardware: POTA FPGA (optional, 10x overhead) vs. CPU fallback (100x overhead)

**Datasets & Models:**
- Vision: ResNet-18 (25M params, pretrained ImageNet) on ImageNet validation (1000 images)
- NLP: BERT-base (110M params, pretrained) on GLUE SST-2 (872 validation sentences)

**Baselines:**
- Per-Query DP-LIME (primary comparison)
- Federated SHAP (different threat model, reference)
- Non-Private LIME (upper bound fidelity)

### Experimental Design

**Design Type:** Mixed factorial (between: Privacy Mechanism, within: N, ε)
- **Factors:** Privacy ∈ {SMPC, Per-Query-DP, Non-Private}, N ∈ {1000, 5000, 10000}, ε ∈ {0.5, 1.0, 2.0}
- **Sample Size:** 1000 (ImageNet) + 872 (GLUE) - power > 0.95 for detecting d ≥ 0.5 at α=0.01
- **Primary Metric:** Spearman ρ with Integrated Gradients (ground truth)
- **Secondary Metrics:** Total privacy cost ε_total, latency (seconds), overhead (ratio)

**Statistical Tests:**
- SH3 (Comparison): Paired t-test (ρ_SMPC vs. ρ_DP at ε=1.0, N=5000), α=0.01, expected d ≥ 1.5
- SH4 (Hardware): Welch's t-test (latency_POTA vs. latency_CPU), α=0.01, expected speedup 30-100×
- SH5 (Adaptive): Paired t-test (ε_adaptive vs. ε_fixed for ρ=0.75), α=0.01, expected reduction 20-40%

---

## Contributions Summary

### Theoretical
1. **Budget Amortization Theorem:** Prove ε_total_SMPC = ε_explanation = O(1) vs. ε_total_DP = N × ε_query = O(N)
2. **Privacy-Utility Pareto Frontier:** Characterize achievable (ε, ρ, N) region for SMPC vs. DP
3. **Information-Theoretic Optimization:** Extend Zamani et al. (2025) MI-minimization to SMPC-XAI
4. **Security Analysis:** Formal proofs under honest-but-curious + adaptive adversary models

### Methodological
1. **SMPC-LIME Protocol:** Complete specification with communication complexity O(N × d × log(1/δ))
2. **SMPC-SHAP Protocol:** TreeSHAP-compatible variant for neural networks
3. **Hardware Integration API:** POTA FPGA pipeline architecture
4. **Adaptive Budget Algorithm:** MI-minimization heuristic with convergence guarantees

### Practical
1. **Open-Source Implementation:** CrypTen backend + LIME/SHAP API compatibility + POTA module
2. **Benchmark Suite:** ResNet-18/ImageNet + BERT-base/GLUE with statistical validation
3. **Regulatory Compliance Guide:** GDPR checklist (Articles 5, 22, 32) + DPIA template
4. **Deployment Guides:** CPU-only (offline), POTA (near-real-time), threshold crypto (distributed trust)

---

## Scope & Boundaries

### In Scope
- **Models:** Differentiable NNs ≤ 1B params (ResNet-18, BERT-base validated)
- **Tasks:** Image classification (ImageNet), text classification (GLUE)
- **XAI:** Model-agnostic post-hoc (LIME, SHAP)
- **Privacy Threat:** Single-model query attacks (membership inference, model extraction)
- **Deployment:** Offline batch (CPU, 10-20s) + near-real-time (POTA, 1-2s)

### Out of Scope
- **Very Large Models:** >1B params (GPT-4 scale) - SMPC complexity unclear, future work
- **Federated Learning:** Cross-silo data privacy (different threat model)
- **Black-Box APIs:** Model-inaccessible scenarios (SMPC requires model owner participation)
- **Malicious Adversaries:** Active protocol deviation (honest-but-curious is baseline)
- **Real-Time Latency:** <100ms requirements (minimum 1-2s even with POTA)

---

## Key Assumptions

1. **Honest-but-Curious Adversary:** Parties follow SMPC protocol but try to infer private information from protocol views
   - **Relaxation:** Malicious model via verifiable secret sharing (2-3× overhead increase)

2. **Trusted Aggregator:** Single party trusted by data + model owners for secure aggregation
   - **Relaxation:** Threshold cryptography (K parties, K-1 collusion needed) removes single point of trust

3. **Differential Privacy Composition:** DP noise on aggregate provides ε-DP for full explanation process
   - **Validity:** Post-processing immunity (Dwork & Roth 2014) applies if aggregation is deterministic

4. **Hardware Acceleration (Optional):** POTA FPGA available for near-real-time deployment
   - **Fallback:** CPU acceptable for offline explanations (100x overhead, 10-20s latency)

---

## Falsification Criteria

Hypothesis is **FALSIFIED** if ANY condition holds:

1. **Fidelity Failure:** ρ_SMPC < 0.65 at ε=1.0 (not significantly better than DP at ρ ~ 0.3)
2. **Privacy Cost Equivalence:** ε_total_SMPC = Θ(N) (no amortization benefit)
3. **Impractical Overhead:** latency_POTA > 30s for N=5000 (prevents practical deployment)
4. **Security Breakdown:** SMPC leaks ≥10% of individual predictions M(x_i) to adversary
5. **Generalization Failure:** Fidelity degrades >30% from ResNet-18 to BERT-base (model-specific, not generalizable)

---

## Phase 2B Readiness

### Readiness Status: ✅ READY

**Decomposition:** 6 sub-hypotheses (SH1-SH6) covering existence, mechanism, comparison, hardware, optimization, generalization

**Baselines:** 4 SOTA methods identified with differentiation matrix

**Metrics:** Quantitative (Spearman ρ, ε_total, latency) with statistical tests (t-tests, ANOVA, power analysis)

**Resources:** Datasets (ImageNet, GLUE), models (ResNet-18, BERT-base), frameworks (CrypTen, LIME/SHAP), hardware (CPU + optional POTA)

**Timeline:** 6-9 months (CPU-only) or 9-12 months (with POTA), MEDIUM difficulty

### Open Questions for Phase 2B/2C

1. **Q4 (HIGH):** Privacy auditing empirical validation - MIA attack confirmation of ε-DP guarantee
2. **Q1 (HIGH):** Adaptive adversary analysis - query correlation leakage quantification
3. **Q6 (MEDIUM):** Regulatory interpretation - acceptable ε for GDPR Article 5 compliance
4. **Q5 (MEDIUM):** Deployment constraints - resource profiling (memory, bandwidth, energy)
5. **Q2-Q3, Q7 (LOW/FUTURE):** Threshold crypto overhead, large model approximation, alternative aggregation strategies

---

## Key Related Work Comparison

| Work | Privacy Approach | Utility | Our Difference |
|------|------------------|---------|----------------|
| **Strobel & Shokri (2022)** | Problem identification only | - | Provides SMPC solution with DP guarantees |
| **Per-Query DP-LIME** | Statistical noise O(N) | ρ < 0.3 at ε=1.0 | Cryptographic O(1), ρ > 0.8 |
| **Zhang et al. (2025) POTA** | SMPC hardware (inference) | - | Apply to XAI workload (N=5000 queries) |
| **Zamani et al. (2025)** | LDP with MI optimization | - | Extend to SMPC-XAI budget allocation |
| **Federated SHAP** | Cross-silo privacy (FL) | - | Single-model query privacy (different threat) |
| **Hummel et al. (2025)** | EU AI Act + XAI (no privacy) | - | Privacy-preserving implementation (GDPR 5+22) |

**Novelty:** Cryptographic budget amortization for explainability - fundamentally different from statistical privacy (per-query DP), enabling 2-3× fidelity at regulatory ε ≤ 1.0

---

## Regulatory Alignment

**GDPR Compliance:**
- ✅ Article 22 (Right to Explanation): High-fidelity explanations (ρ > 0.8) satisfy interpretability requirement
- ✅ Article 5 (Privacy by Design): ε=1.0 DP guarantee meets data minimization principle
- ✅ Article 32 (Security): SMPC provides confidentiality against honest-but-curious adversaries

**EU AI Act:**
- High-risk systems: Use ε ≤ 1.0 with POTA (near-real-time) for conformity assessment
- Standard compliance: Use ε ≤ 2.0 with CPU (batch processing acceptable)

**DPIA Template Provided:** Privacy risks (query correlation, aggregator trust), mitigations (DP perturbation, threshold crypto), residual risks (adaptive attacks - future work)

---

## Next Steps: Phase 2B Sub-Hypothesis Verification Planning

1. **SH1-SH3:** Core validation (existence, mechanism, comparison) - highest priority
2. **SH4-SH5:** Optimization validation (hardware, adaptive budget) - medium priority
3. **SH6:** Generalization validation (cross-architecture) - ensures practical applicability
4. **Open Questions Q1, Q4:** Privacy auditing + adaptive adversary - integrate into Phase 4 validation
5. **Open Question Q6:** Regulatory ε range - inform Phase 2C experiment design (ε ∈ {0.1, 0.5, 1.0, 2.0})

**Phase 2B Output:** Verification roadmap with prioritized experiments, dependencies, success criteria, expected timeline

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*Full technical specification available in: 02a_extended_hypothesis_full.md*
*2026-02-08*
