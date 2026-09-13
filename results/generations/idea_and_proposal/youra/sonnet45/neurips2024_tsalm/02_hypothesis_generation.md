# Phase 2A Extended Summary: TSCP Hypothesis

**Date:** 2026-02-06
**Researcher:** Pray
**Hypothesis ID:** H1-TSCP
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis Title:** Time Series Complexity Profiling (TSCP): A Triage Framework for Foundation Model Necessity Prediction

**Core Claim:**
A lightweight XGBoost classifier trained on 6-8 information-theoretic complexity metrics can predict foundation model performance gains over linear baselines BEFORE training, achieving ≥80% accuracy in <10 seconds per series, enabling resource-efficient model selection through a 3-tier triage system.

**Gap Addressed:** Gap 1 (P0 Priority) - Principled Guidelines for When to Use Foundation Models vs Simple Approaches

**Confidence Level:** 0.85 (High)

---

## Key Innovation

**Paradigm Shift:** POST-training comparative benchmarking → PRE-training predictive characterization

**Inspiration:** Medical Emergency Severity Index (ESI) triage protocol

**Mechanism:**
```
Time Series → Complexity Metrics (6-8 features) → XGBoost Classifier → Tier (1/2/3) → Model Recommendation
```

**Tiers:**
- **Tier 1 (Linear Sufficient):** <5% performance gap → Recommend linear models (LTSF-Linear, ARIMA)
- **Tier 2 (Marginal Benefit):** 5-15% gap → User decision based on resources
- **Tier 3 (Foundation Needed):** >15% gap → Recommend foundation models (PatchTST, MOMENT)

---

## Variables

### Independent Variables (Complexity Metrics)
1. **Entropy Rate** - Shannon entropy of distribution
2. **Sample Entropy** - Regularity measure
3. **Largest Lyapunov Exponent** - Chaos indicator
4. **Hurst Exponent** - Long-range dependence
5. **Fractal Dimension** - Geometric complexity
6. **Autocorrelation Decay** - Temporal structure

### Dependent Variable
- **Foundation Model Performance Gain:** (FM Accuracy - Linear Accuracy) / Linear Accuracy × 100%

### Control Variables
- Series length (≥200 points)
- Forecast horizon
- Domain (weather/traffic/energy/medical/financial)

---

## Testable Predictions

**P1 (Primary):** Prediction accuracy ≥80%, correlation r≥0.7, computation <10 sec, training <1 GPU-hour

**P2 (Baseline Superiority):** ≥20 percentage point improvement over heuristics (length/domain rules at ~60%)

**P3 (Metric Contribution):** Top-3 metrics (Lyapunov, Hurst, Entropy) account for ≥60% feature importance

**P4 (Generalization):** Out-of-domain accuracy ≥60% zero-shot, ≥75% with 20-shot adaptation

**P5 (Efficiency):** 95% computational cost reduction vs. training foundation model for each problem

**Falsification:**
- Null: Accuracy <60% (no better than random)
- Weak: Accuracy 60-70% (marginal improvement)
- Strong: Accuracy ≥85% (exceeds target)

---

## Sub-Hypotheses for Phase 2B

**SH1 (Existence):** Complexity metrics correlate with performance gaps (|r| ≥ 0.5)

**SH2 (Mechanism):** XGBoost learns complexity-performance mapping (80% test accuracy)

**SH3 (Comparison):** TSCP outperforms heuristics by ≥20 percentage points

**SH4 (Efficiency):** Metric computation <10 seconds on CPU

**SH5 (Generalization):** Out-of-domain accuracy ≥60% with ≤20 pp degradation

---

## Contributions

**Theoretical:**
- Formalize complexity-performance relationship for time series foundation models
- Cross-domain framework transfer methodology (medical triage → ML model selection)

**Methodological:**
- Triage-style predictive characterization (first PRE-training model selection framework)
- Information-theoretic model selection using intrinsic data properties
- Adaptive threshold learning for user-specific cost-benefit preferences

**Practical:**
- Resource optimization tool (10³-10⁵× computational savings)
- Democratization of foundation model access (know when NOT to use expensive models)
- Cost-benefit analysis framework (breakeven after 20 problems)

**Empirical:**
- Validation of complexity-performance hypothesis across 100+ benchmarks
- Rigorous baseline comparison (20-30 pp improvement over heuristics)

---

## Evidence Base

**Phase 1 Sources (100% utilization):**
1. Zeng (3024 cit): Linear models competitive with transformers → Motivates selection framework
2. Tan (173 cit): LLM components often detrimental → Questions universal complexity
3. Goswami (337 cit): MOMENT demonstrates foundation model power → Foundation model baseline
4. Yao (24 cit): Scaling laws exist → But when is scaling worthwhile?

**Supplementary Sources (Resolved evidence gap):**
1. arXiv 2507.13556 (2025): **SMOKING GUN** - "Lyapunov and spectral predictability assess forecastability PRIOR to training and correlate strongly with performance"
2. Tian et al. (2025): Hurst, Lyapunov, entropy directly affect accuracy (R²=0.9922)
3. Karaca & Baleanu (2020): Hurst + Wavelet Entropy improve forecasting
4. Zhang (2025): Complexity metrics differentiate time series types

---

## Implementation Overview

**Training Phase (One-Time Setup):**
1. Select 60-80 benchmark datasets (ETTh, Weather, Traffic, Electricity)
2. Train foundation model (PatchTST) + linear baseline (LTSF-Linear) on each
3. Compute performance gaps (ground truth labels)
4. Extract 6-8 complexity metrics from each dataset
5. Train XGBoost classifier (max_depth=5, n_estimators=100)
6. **Cost:** <1 GPU-hour for classifier training (excluding benchmark model training)

**Prediction Phase (Zero-Cost):**
1. New problem arrives
2. Extract complexity metrics (<10 seconds on CPU)
3. XGBoost predicts tier (Linear/Marginal/Foundation)
4. Return recommendation
5. **Cost:** Effectively zero after setup

**Amortization:** Setup cost amortizes across all future problems; breakeven after ~20 problems

---

## Scope & Boundaries

**In Scope:**
✅ Univariate/multivariate time series forecasting
✅ Weather, traffic, energy, medical, financial domains
✅ Transformer-based foundation models (MOMENT, PatchTST, Time-MoE)
✅ Linear baselines (LTSF-Linear, ARIMA)
✅ Series length ≥200 points
✅ Pre-training model selection

**Out of Scope:**
❌ Anomaly detection / classification tasks
❌ Very short series (<200 points)
❌ Highly non-stationary series (regime changes)
❌ Real-time inference optimization
❌ Multimodal time series (text + numerical)
❌ Post-training model comparison

---

## Novelty Differentiation

| Work | Timing | Purpose | TSCP Advantage |
|------|--------|---------|----------------|
| **FoundTS, TSFM-Bench** | POST-training | Compare models | TSCP: PRE-training prediction |
| **arXiv 2507.13556** | PRE-training | Assess difficulty | TSCP: Predict MODEL NECESSITY |
| **Tian, Karaca** | WITHIN-training | Feature engineering | TSCP: SELECT model class |
| **Heuristics (length/domain)** | Instant | Simple rules (60%) | TSCP: Learned framework (80%) |

**Unique Value:** Only framework providing PRE-training MODEL CLASS SELECTION at near-zero marginal cost

---

## Risk Assessment

**Anti-Pattern Status:** ✅ ALL 12 CLEAR
- No approximation issues, hardware punts, complexity shell games, data mirages, baseline dodges, metric shopping, scale illusions, hyperparameter hell, reproducibility roulette, novelty veneers, assumption avalanches, or domain lock-ins

**Key Assumptions (Validated):**
1. ✅ Complexity metrics predict performance (arXiv 2507.13556, Tian 2025, Karaca 2020)
2. ⚠️ Metrics are domain-agnostic (REQUIRES VALIDATION - OOD testing planned)
3. ✅ XGBoost can learn mapping (standard ML practice, tabular data strength)
4. ✅ One-time setup amortizes (acknowledged limitation, justified by breakeven analysis)

**Implementation Difficulty:** LOW-MEDIUM
- Standard libraries (nolds, pyEEG, entropy, XGBoost)
- Public benchmarks (ETTh, Weather, Traffic)
- Reasonable costs (<1 GPU-hour training, <10 sec inference)

---

## Next Steps

**Immediate Action:** Proceed to Phase 2B - Verification Planning

**Phase 2B Goals:**
1. Decompose main hypothesis into detailed sub-hypotheses (SH1-SH5)
2. Design experiments to verify each sub-hypothesis
3. Establish success criteria and gate conditions
4. Create dependency graph (which experiments must complete before others)
5. Estimate timelines and resource requirements

**Phase 2C Input:** Detailed verification roadmap from Phase 2B

**Expected Timeline:**
- Phase 2B (Verification Planning): 20-30 minutes
- Phase 2C (Experiment Design): 30-45 minutes
- Phase 3 (Implementation Planning): 60-90 minutes
- Phase 4 (Coding & Validation): 2-4 hours

---

## Open Questions (For Phase 2B)

1. **Metric Subset:** Can we reduce 6-8 metrics to core set without accuracy loss?
2. **Threshold Learning:** Should tier boundaries be learned from data or remain fixed?
3. **Domain Adaptation:** How many labeled examples for few-shot adaptation in new domains?
4. **Foundation Model Sensitivity:** Does choice of FM (PatchTST vs. MOMENT) change ground truth?
5. **Preprocessing:** What is the canonical preprocessing pipeline?
6. **Confidence Calibration:** Can we provide uncertainty estimates for predictions?
7. **Multi-Horizon:** Does optimal model depend on forecast horizon?
8. **Cost-Benefit Personalization:** How to incorporate user-specific preferences?
9. **Multivariate Handling:** Unified framework or separate classifier?
10. **Streaming Data:** Can TSCP handle online scenarios?

---

## Key Deliverables

**Phase 2B → 2C → 3 → 4 Pipeline:**

1. **Phase 2B Output:** Verification roadmap with SH1-SH5 experiments
2. **Phase 2C Output:** Detailed experiment specifications (Level 1.5 implementation brief)
3. **Phase 3 Output:** PRD, Architecture, PRP, Archon project (implementation-ready package)
4. **Phase 4 Output:** Working code + validation report (04_validation.md)

**Final Artifacts:**
- `tscp` Python package (open-source)
- Command-line tool: `tscp characterize data.csv`
- Jupyter notebooks (tutorials)
- Benchmark results (100+ datasets)
- Paper-ready figures and tables

---

**Status:** ✅ READY FOR PHASE 2B

**Confidence:** 0.85 (High) - Strong evidence, fixable flaws, clear implementation path

**Recommendation:** Proceed to Phase 2B Verification Planning

---

*Full details in: 02a_extended_hypothesis_full.md*
*Generated: 2026-02-06 (YOLO Mode - Fully Automated)*
*Next Command: `/phase2b-planning --input "02a_extended_hypothesis.md"`*
