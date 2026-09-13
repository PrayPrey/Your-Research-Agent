# Hypothesis Refinement Summary

**Generated:** 2026-08-20T01:51:25Z  
**Workflow:** Phase 2A-Dialogue (Self-Contained Tikitaka Loop)  
**Gap:** Gap 3 - Attribution effectiveness for unknown spurious features  
**Hypothesis ID:** H-GradAbn-v1

---

## Core Hypothesis

**Under** deep neural networks trained on datasets with spurious correlations (e.g., Waterbirds with 90% background-class correlation),

**If** we compute gradient abnormality metrics (GAIA zero-deflation, channel-wise variance) for test samples,

**Then** minority group samples (waterbird-land, landbird-water) will exhibit significantly higher abnormality scores than majority group samples (waterbird-water, landbird-land),

**Because** spurious reliance creates gradient scattering when the spurious shortcut conflicts with core features in minority samples.

---

## Causal Mechanism (4 Steps)

1. **Spurious Learning:** Model learns spurious shortcut during training (landbird→land 90%, waterbird→water 90%)
2. **Conflict:** Minority sample (waterbird-land) creates conflict between spurious shortcut (land→landbird) and core feature (waterbird)
3. **Gradient Scattering:** Conflict manifests as dense, noisy gradients (attempts to attribute to both spurious background and core bird shape)
4. **Detection:** GAIA metrics (zero-deflation, channel-wise variance) quantify scattering → unsupervised minority detection

---

## Testable Predictions (5)

**P1 (Primary - Detection):** Minority GAIA-Z scores ≥0.2 higher than majority (p<0.01)
- Test: ResNet-50 on Waterbirds, t-test comparing minority vs majority scores
- Success: Mean difference ≥0.2, p<0.01, Cohen's d ≥0.8

**P2 (Primary - Correlation):** GAIA divergence correlates with WGA across models (ρ>0.7)
- Test: Train 10 models with 50%-95% correlation, measure WGA + GAIA gap, Pearson correlation
- Success: ρ>0.7, p<0.05

**P3 (Causality):** Background augmentation reduces GAIA-Z by ≥30%
- Test: Swap minority→majority backgrounds, measure GAIA-Z reduction
- Success: Mean reduction ≥30%

**P4 (Primary - MNIST Toy):** Color-only regularization WGA ≥ Baseline+10%
- Test: MNIST+Color 80% correlation, 4 conditions (baseline, all-pixels, color-only, digit-only)
- Success: Color-only WGA ≥ Baseline+10%, ≥ All-pixels+5%, Digit-only WGA ≤ Baseline-5%

**P5 (Primary - Waterbirds Mitigation):** Spatial regularization WGA ≥ GroupDRO+5%
- Test: Train with GradCAM-based masking + adaptive penalty, compare to GroupDRO
- Success: WGA ≥ GroupDRO+5%, average accuracy drop ≤2%

---

## Key Assumptions (5)

**A1:** Minority classification accuracy ≥60% (enables GradCAM difference to highlight core features)  
**A2:** Percentile-based normalization avoids majority bias in adaptive penalty  
**A3:** Gradient scattering caused by spurious conflict, not image complexity  
**A4:** Regularization reduces spurious reliance (not just smooths gradients)  
**A5:** GroupDRO/JTT baselines sufficient (SCER code unavailable)

---

## Novel Contributions

1. **First** application of gradient abnormality (GAIA) to minority group detection within ID distribution
2. **First** gradient-based regularization for spurious mitigation (complement to embedding methods like SCER)
3. **Automatic** spurious localization via GradCAM difference maps (no feature engineering)
4. **Unified** framework: same abnormality mechanism for OOD detection (GAIA) and spurious detection (ours)

---

## Experimental Setup

**Datasets:**
- Waterbirds (primary): 4 groups, background-class spurious correlation
- MNIST+Color (toy validation): controlled spurious, known ground truth
- CelebA (generalization): gender spurious, different type

**Models:**
- ResNet-50 (Waterbirds, CelebA)
- ResNet-18 (MNIST toy)

**Baselines:**
- GroupDRO: 85-88% WGA (reproducible)
- JTT: ~88% WGA (reproducible)
- SCER: ~90% WGA (estimated, code unavailable)

---

## Decision Gates (3)

**Gate 1 (Week 1 - MNIST Toy):**
- Success: WGA +10% → Proceed to Waterbirds
- Partial: WGA +5-10% → Proceed with caution
- Fail: WGA <+5% → Pivot to detection-only

**Gate 2 (Week 2 - Waterbirds Detection):**
- Success: P1 confirmed (minority abnormality) + spatial masking works → Proceed to mitigation
- Partial: P1 confirmed but spatial masking fails → Global regularization
- Fail: P1 false → Abandon gradient approach

**Gate 3 (Week 3-4 - Waterbirds Mitigation):**
- Tier 2: WGA ≥GroupDRO+5% → Gradient-based alternative validated
- Tier 3: WGA +3-5% → Detection-focused contribution
- Fail: WGA <+3% → Reframe as "promising approach, embedding methods remain SOTA"

---

## Remaining Concerns & Mitigations

**Concern 1:** GradCAM difference may fail if minority accuracy <60%  
**Mitigation:** Empirical check in Phase 2B. Fallback: global regularization

**Concern 2:** SCER code unavailable — cannot claim Tier 1 SOTA  
**Mitigation:** Position as Tier 2 "gradient-based alternative", compare to GroupDRO/JTT

**Concern 3:** Conditional OOD argument potentially circular  
**Mitigation:** Activation clustering (t-SNE) to validate minority representation as "between-class"

---

## Phase 2B Readiness

✅ **READY**

**SH1 (Existence):** Baseline WGA <80% confirms spurious reliance. GAIA metrics computable (gradients, backprop infrastructure available).

**SH2 (Mechanism):** Validate minority abnormality (P1). If true, mechanism empirically supported. MNIST toy validates regularization (P4).

**SH3 (Comparison):** Compare to GroupDRO, JTT (P5). SCER deferred to Phase 5 (code may become available).

**Open Questions:**
- Does spatial masking hold? (A1 check)
- Will MNIST toy succeed? (P4 validation)
- Can we beat GroupDRO by ≥5%? (Tier 2 vs 3 positioning)
- Does it generalize to CelebA? (Week 5 optional)

---

## Timeline

**Week 1:** MNIST toy (4 days) → Decision Gate 1  
**Week 2:** Waterbirds detection (3 days) → Decision Gate 2  
**Week 3-4:** Waterbirds mitigation (2 weeks) → Decision Gate 3  
**Week 5:** CelebA generalization (optional, if Gate 3 strong success)

**Total:** 4-5 weeks, ~250 GPU-hours

---

## Persona Verdicts

🔭 **Dr. Nova (Novelty):** STRONG — Unified OOD+spurious framework, automatic localization  
🔬 **Prof. Vera (Falsifiability):** STRONG — 5 testable predictions, 3 decision gates, rigorous MNIST protocol  
🎯 **Dr. Sage (Significance):** MODERATE — Addresses Adebayo 2022 gap, but Tier 2-3 (not Tier 1 SOTA)  
⚙️ **Prof. Pax (Feasibility):** STRONG — All tools available, realistic timeline, clear blockers/mitigations  
🛡️ **Dr. Ally (Synthesis):** STRONG — Execution-ready, failure contingencies defined  
🔍 **Prof. Rex (Critique):** MODERATE — 3 flaws identified, all addressed via implementation fixes

**Consensus:** Validated hypothesis ready for Phase 2B execution with clear success/failure criteria.
