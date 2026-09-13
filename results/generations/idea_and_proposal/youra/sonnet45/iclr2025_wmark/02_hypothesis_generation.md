# Phase 2A Extended: Hypothesis Summary

**Date:** 2026-02-06
**Hypothesis ID:** H-WMARK-001
**Confidence:** 0.85 (HIGH)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Core Hypothesis Statement

**Main Hypothesis:**
Applying randomized smoothing with adaptive variance selection to watermark detectors provides provable ℓ₂ robustness certificates that guarantee watermark detectability under adversarial perturbations within a certified radius, enabling formal verification across all generative AI modalities.

**Alternative Hypothesis (H0):**
Randomized smoothing fails to provide practical certification either due to insufficient certified radius (r < 0.05) or unacceptable accuracy degradation (< 80%).

---

## Key Variables

| Type | Variable | Range | Target |
|------|----------|-------|--------|
| Independent | Smoothing variance (σ) | 0.1 - 1.0 | Optimize per application |
| Independent | Watermark strength (SNR) | 5-15 dB | ≥10 dB for strong certification |
| Independent | Monte Carlo samples (N) | 1K - 100K | 10K (balance cost/accuracy) |
| Dependent | Certified radius (r) | 0 - ∞ | ≥ 0.15 (practical threshold) |
| Dependent | Clean accuracy | 0 - 100% | ≥ 85% (usability threshold) |
| Dependent | Certification success rate | 0 - 100% | ≥ 90% (reliability) |

---

## Causal Mechanism Summary

1. **Watermark Embedding** → Content contains detectable signal
2. **Base Detector Training** → Neural network learns watermark classification
3. **Randomized Smoothing** → Gaussian noise injection creates smoothed detector D̄(z) = E[D(z + δ)]
4. **Monte Carlo Estimation** → N samples approximate class probabilities
5. **Certified Radius Computation** → r = (σ/2)(Φ⁻¹(p̂_A) - Φ⁻¹(p̂_B))
6. **Robustness Guarantee** → ∀ ||δ||₂ ≤ r: detection succeeds with probability ≥ (1-α)

**Critical Trade-off:** Larger σ → larger r BUT lower clean accuracy (Pareto optimization problem)

---

## Testable Predictions

**P1 (Trade-off):** Doubling σ increases r by ≥0.2 but decreases accuracy by ≤10%

**P2 (Watermark Strength):** 2× watermark strength → 30% increase in certified radius

**P3 (Certification Guarantee - Axiomatic):** Attack success rate ≥ 95% for ||δ||₂ ≤ r (α=0.05)

**P4 (Monte Carlo Convergence):** 100× more samples → 5× lower certification variance

**P5 (Cross-Modality):** Certified radius variance ≤ 20% across modalities (SNR-normalized)

**Falsification Criteria:**
- r < 0.05 for strong watermark + σ=0.5
- Accuracy < 80% for any σ ≥ 0.1
- Empirical attack success < 90% within certified radius
- Framework fails for any modality
- Certification time > 10 minutes per sample

---

## Contribution Summary

### Theoretical
**First ℓ₂ certification framework for watermark detection** - Adapts randomized smoothing from adversarial robustness (Cohen et al., 2019) to provide provable guarantees for ANY neural watermark detector across ALL modalities. Unigram (2024) provides provable text watermarking but is watermark-specific; this work is detector-agnostic.

### Methodological
**Adaptive certification protocol** - Combines smoothed detector construction, adaptive σ selection, efficient Monte Carlo sampling, and unified multi-modality framework. Enables practical offline certification (~2 minutes per sample) balancing accuracy-robustness trade-offs.

### Practical
**Regulatory compliance enablement** - First certifiable watermarking for EU AI Act Art. 52 and California AB 3211 requirements. Provides auditable robustness certificates for high-stakes applications (deepfake detection, IP protection, content authentication).

---

## Scope & Boundaries

**✅ IN SCOPE:**
- Modalities: Images, text, audio, video
- Attack model: ℓ₂-bounded adversarial perturbations
- Deployment: Offline certification for regulatory compliance
- Detectors: Any neural network with probabilistic outputs

**❌ OUT OF SCOPE:**
- Non-ℓ₂ attacks (spatial, compression, re-generation)
- Real-time certification (computational constraint)
- Hash-based watermarks (not neural classifiers)
- Zero-shot detection (requires trained detector)

---

## Key Related Work

| Work | Relation | Key Differentiation |
|------|----------|---------------------|
| **Cohen et al. (2019)** | Foundation | Source of randomized smoothing theory; we adapt to watermarking |
| **Unigram (2024)** | Comparison | Text-specific provable watermarking; ours is modality-agnostic |
| **ROBIN (2024)** | Inspiration | Empirical robustness; we provide formal ℓ₂ certificates |
| **RAWatermark (2024)** | Comparison | Claims "provable" but empirical only; we have mathematical guarantees |
| **IP Protection (2023)** | Foundation | Threat model framework for certification requirements |

---

## Phase 2B Decomposition Preview

### SH1 (Existence)
Can smoothed detector achieve r ≥ 0.15 with accuracy ≥ 85%?
- 1.1: Strong watermark (SNR=15dB) + σ=0.5 achieves targets
- 1.2: Certified radius scales with watermark strength (ρ > 0.8)
- 1.3: Accuracy degradation bounded by ≤15% across all modalities

### SH2 (Mechanism)
Does mechanism match theoretical predictions?
- 2.1: Certified radius formula accuracy within 5% error
- 2.2: Adaptive σ improves Pareto frontier by ≥20%
- 2.3: Certification guarantee holds empirically (≥93% success rate)

### SH3 (Comparison)
Advantages over SOTA baselines?
- 3.1: Generalizes to ≥3 modalities with ≤20% variance
- 3.2: Provides r > 0 where ROBIN provides 0 (empirical only)
- 3.3: Certification time ≤ 2 minutes per sample (practical)

---

## Validation Strategy

**3-Phase Approach:**

**Phase 1: Toy Scale** (2 weeks)
- MNIST with synthetic watermarks
- Validate implementation + certification guarantee
- Target: P3 holds (success rate ≥ 93%)

**Phase 2: Medium Scale** (1 month)
- CIFAR-10 (images), SST-2 (text), Common Voice (audio)
- Cross-modality consistency + adaptive σ optimization
- Target: r ≥ 0.1, P5 variance ≤ 20%

**Phase 3: Realistic Scale** (1 month)
- ImageNet, GPT-2 text, AudioSet, YouTube-VIS video
- SOTA comparison + practical feasibility
- Target: Accuracy ≥ 85%, r ≥ 0.15, no falsification

---

## Statistical Design

**Experimental Design:** Factorial (σ × watermark_strength × modality × N)

**Sample Sizes:**
- Training: 20K samples per condition (10K watermarked + 10K clean)
- Certification: 1K samples per condition
- Attack evaluation: 5K samples per condition

**Key Tests:**
- **P1:** Pearson ρ(σ, r) > 0.8; ρ(σ, accuracy) < -0.7
- **P3:** One-sample proportion test (success rate ≥ 95%)
- **P5:** ANOVA for cross-modality certified radius (α=0.05)

**Metrics:**
- Certified radius r (ℓ₂ units)
- Clean accuracy (%)
- Certification success rate (%)
- Attack success rate within r (%)
- Certification time (seconds)

---

## Open Questions for Phase 2B

**Q1:** Per-sample vs. per-application adaptive σ selection strategy?

**Q2:** Expected certified radius magnitude for realistic watermark strengths (SNR=10dB)?

**Q3:** Cross-modality SNR normalization method (ensure fair comparison)?

**Q4:** Certification API design for industry adoption (input/output format)?

**Q5:** Extension to non-ℓ₂ attacks via alternative smoothing distributions (future work)?

---

## Readiness Checklist

✅ Core hypothesis with quantitative H0 and falsification criteria
✅ Variables defined with measurement units and targets
✅ Causal mechanism explained with evidence
✅ 5 key assumptions stated with risk assessment
✅ Scope bounded (IN/OUT explicit)
✅ 5 testable predictions with quantitative targets
✅ SOTA baselines identified with differentiation
✅ Statistical design with sample sizes and power analysis
✅ 3 contributions (theoretical, methodological, practical) clarified
✅ 15+ related work sources mapped with relations
✅ Sub-hypotheses outlined (3 main × 3 specific = 9 tests)

**Status:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

---

## Next Steps

1. **Phase 2B:** Decompose into detailed sub-hypotheses with experiments
   - Input: This extended hypothesis (02a_extended_hypothesis.md)
   - Process: Systematic decomposition of SH1-SH3 into testable experiments
   - Output: Verification roadmap with prioritized experiments and success criteria

2. **Phase 2C (if prioritized):** Design specific experiments
   - For each sub-hypothesis: detailed protocol, datasets, metrics, baselines
   - Output: Implementation-ready experiment specifications

3. **Phase 3-4 (if selected):** Implementation and validation
   - Estimated timeline: 2-3 months
   - Resources: 1 GPU (A100), standard DL environment
   - Validation: Toy → Medium → Realistic scale

---

**Full Details:** See `02a_extended_hypothesis_full.md` for complete clarification with all sections expanded.

*Generated by YouRA Phase 2A Extended*
*2026-02-06*
*YOLO Mode: Fully Automated Execution*
