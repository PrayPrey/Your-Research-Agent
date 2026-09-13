# Phase 2A Extended: Hypothesis Clarification (Summary for Phase 2B)

**Date:** 2026-02-08
**Author:** Pray
**Hypothesis ID:** H-PPML-FHE-001
**Confidence Level:** 85%
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Variable-precision homomorphic encryption applied adaptively across neural network layers—where privacy-sensitive layers (input, output, embeddings) use high-precision CKKS parameters and intermediate layers use reduced precision—can achieve **3-5× latency reduction (24s → 5-10s)** for encrypted deep learning inference while maintaining **>95% of plaintext model accuracy** and preserving privacy against membership inference attacks.

**Key Innovation:**
First layer-wise adaptive precision allocation for FHE neural networks, treating encryption precision as an allocatable resource based on privacy-sensitivity analysis.

**Research Gap Addressed:**
Gap 2 - Computational Feasibility of FHE for Real-Time ML Inference at Scale

---

## 1. Hypothesis Statement

### Core Claim
Layer-wise adaptive CKKS scale parameter assignment (HIGH precision for input/output layers, LOW precision for intermediate layers) reduces encrypted inference latency by 3-5× compared to uniform-precision baseline, while maintaining accuracy within 5% of plaintext and preserving privacy guarantees (MIA success rate <55%).

### Alternative Hypothesis (H0)
Adaptive precision will fail by either:
1. Achieving <2× speedup (bottleneck in high-precision layers), OR
2. Causing >5% accuracy degradation (noise accumulation), OR
3. Weakening privacy >10 percentage points (information leakage from variable precision)

### Variables

| Type | Variable | Measurement | Expected Range |
|------|----------|-------------|----------------|
| **Independent** | Precision tier (HIGH/MEDIUM/LOW) | Categorical | 3 levels |
| **Independent** | CKKS scale reduction % | Percentage | 0%, 30%, 50% |
| **Independent** | Model architecture | Categorical | DLRM, ResNet-18, Transformer |
| **Dependent** | Inference latency | Seconds | 5-10s (target) |
| **Dependent** | Accuracy | % of plaintext | >95% |
| **Dependent** | MIA success rate | Percentage | <55% |
| **Controlled** | Hardware, baseline FHE params, attack methodology | Fixed | GPU A100, TenSEAL defaults |

---

## 2. Causal Mechanism

```
Offline Profiling (plaintext)
  ↓ Gradient-based sensitivity analysis
Layer categorization (HIGH/MEDIUM/LOW privacy sensitivity)
  ↓ CKKS scale parameter assignment
LOW tier: 50% scale reduction → 2-5× per-layer speedup
  ↓ Weighted across all layers
Overall 3-5× inference speedup
  ↓ Maintained by
HIGH precision on sensitive layers preserves privacy + accuracy
```

**Key Assumptions:**
1. Noise accumulation is layer-independent (or manageable via bootstrapping)
2. Plaintext sensitivity correlates with encrypted sensitivity
3. CKKS scale reduction yields proportional latency reduction
4. Variable precision does not create exploitable privacy vulnerabilities

---

## 3. Testable Predictions

**P1 (Primary - DLRM Speedup):**
IF adaptive precision applied to HE-LRM DLRM model,
THEN latency: 24s → 5-8s (3-4×) AND accuracy: within 2% of plaintext (AUC)

**P2 (Medical Imaging):**
IF ResNet-18 kidney CT uses adaptive precision,
THEN latency: 90s → 18-30s (3-5×) AND AUC: >0.95 (plaintext 0.99, uniform 0.97)

**P3 (Privacy Preservation):**
IF MIA applied to both uniform and adaptive models,
THEN difference in attack success <5 pp AND both <55%

**Falsification:**
- Speedup <2× (latency >12s for DLRM)
- Accuracy loss >5% relative to plaintext
- MIA success rate >10 pp higher than uniform baseline
- Bootstrapping required >3 times per inference (adds ~30s overhead)

---

## 4. Contribution Summary

### Theoretical
**Multi-Objective Resource Allocation Formulation:** First treatment of FHE inference as optimization problem with encryption precision as allocatable resource. Enables cross-pollination with QoS management and Level-of-Detail rendering literature.

### Methodological
**Heuristic Layer-Wise Precision Assignment:** 3-tier allocation (HIGH/MEDIUM/LOW) based on offline plaintext sensitivity profiling. Novel per-layer precision control vs. existing global parameter frameworks (TenSEAL, Concrete ML).

### Practical
**Near-Real-Time FHE Deployment:** Enables 5-10s encrypted inference for medical diagnosis (10s SLA), fraud detection (15s alerts), personalized recommendations (8s acceptable). Unlocks applications currently infeasible with 24-90s latency.

---

## 5. SOTA Baseline & Comparison

**Target Benchmark:** HE-LRM (Garimella et al., 2025)
- DLRM on Criteo CTR dataset
- Latency: 24-489s (current SOTA with 77× embedding compression)
- Accuracy: Within 3% of plaintext
- **Our Expected Improvement:** 24s → 5-8s (additional 3-4× on top of HE-LRM's optimizations)

**Secondary Baselines:**
- Kidney CT (Lee et al., 2025): 90s GPU → Our target: 18-30s
- Fingerprint auth (Sumalatha et al., 2025): 0.025s (simple ops) → Inspiration for what's possible

---

## 6. Related Work Positioning

**Extends:**
- HE-LRM: Orthogonal to embedding compression (can combine both techniques)
- Kidney CT: Generalizes precision tuning from global to per-layer

**Differentiates From:**
- Existing FHE frameworks (TenSEAL, Concrete ML): Global vs. per-layer precision
- Differential Privacy (Opacus): Training vs. inference, statistical vs. cryptographic privacy

**Inspired By:**
- LOD Rendering (graphics): Hierarchical precision management
- QoS Management (real-time systems): Dynamic resource allocation under constraints

---

## 7. Phase 2B Sub-Hypothesis Preview

**SH1 (Existence):** Adaptive precision achieves ≥3× speedup
- **Verification:** Empirical benchmarking, paired t-test (α=0.01)

**SH2 (Mechanism):** Low-precision layers cause <5% accuracy loss
- **Verification:** Ablation study, TOST equivalence test (±5% margin)

**SH3 (Comparison):** Privacy preserved vs. uniform baseline
- **Verification:** MIA testing with ML Privacy Meter, <5 pp difference

---

## 8. Statistical Design Summary

- **Design:** 4×3×3 factorial (Precision Policy × Architecture × Dataset)
- **Replication:** 30 runs per condition (1,080 total measurements)
- **Primary Tests:** Paired t-test (latency), TOST (accuracy), Chi-square (privacy)
- **Power:** 80% to detect d=0.5 effect at α=0.01
- **Confound Control:** Fixed hardware, framework versions, random seeds

---

## 9. Readiness Assessment

**✅ Hypothesis Clarity:**
- Falsifiable claims with numerical thresholds
- Variables and causal mechanism explicit
- Assumptions documented with mitigation strategies

**✅ Measurement Readiness:**
- Standard metrics (latency, AUC/F1, MIA success rate)
- Existing tools (TenSEAL, ML Privacy Meter)
- Defined baselines (HE-LRM, plaintext, uniform-precision)

**✅ Resource Availability:**
- Public datasets (Criteo, UCI, Kidney CT)
- Open-source frameworks (TenSEAL, Concrete ML)
- Accessible compute (single GPU A100)

**✅ Evidence Foundation:**
- CKKS theory well-established
- Empirical precedent (Kidney CT 2% loss, HE-LRM 77× speedup)
- Cross-domain validation (LOD/QoS patterns)

**✅ Risk Mitigation:**
- Noise accumulation: bootstrapping thresholds + ablation
- Privacy: 3 MIA attack types
- Generalization: 3 architectures × 3 datasets
- Reproducibility: Statistical design with power analysis

---

## 10. Open Questions for Phase 2B

1. **Bootstrapping Strategy:** How frequently triggered? Include in latency reporting?
2. **Sensitivity Analysis:** Vanilla vs. adversarial gradient methods?
3. **Attack Realism:** Black-box vs. white-box MIA?
4. **Transformer Generalization:** Attention mechanism noise propagation different?
5. **Optimal Tier Count:** Why 3 (not 2 or 5)? Ablation study needed?
6. **Hardware Variability:** Test on V100/A100/H100 for generalization?

---

**Phase 2B Input Status:** ✅ **READY**

All prerequisites satisfied:
- Hypothesis decomposable into verifiable sub-hypotheses
- Experimental protocols defined
- Success/failure criteria quantified
- Resource requirements identified
- Risk factors documented with mitigation plans

**Recommended Next Step:** Proceed to `/phase2b-planning` for verification roadmap generation.

---

*Full documentation: 02a_extended_hypothesis_full.md*
*Generated: 2026-02-08 (YOLO Mode - Automated)*
