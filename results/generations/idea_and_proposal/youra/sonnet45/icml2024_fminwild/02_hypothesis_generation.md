# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-FedPEFT-001
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Federated parameter-efficient fine-tuning (FedPEFT) with FedProx proximal regularization enables foundation models to adapt to aligned domain-specific tasks across institutional boundaries without data centralization, achieving <5% performance degradation compared to centralized baselines while maintaining differential privacy guarantees (ε=1-10) through secure aggregation of low-rank adapter updates.

**Confidence Level:** 0.8/1.0

**Target Impact:** Enable foundation model deployment in regulated industries (healthcare, finance) where data cannot be centralized, resolving critical deployment barrier.

---

## Core Components

### 1. Main Variables

| Variable | Type | Range | Target |
|----------|------|-------|--------|
| LoRA rank (r) | Independent | 8-64 | 16-32 optimal |
| Privacy budget (ε) | Independent | 1-10 | ≥5 for <5% gap |
| Data heterogeneity (δ) | Independent | 0.1-2.0 | ≤1.5 manageable |
| Institution count (K) | Independent | 3-20 | ≥10 optimal |
| Proximal term (μ) | Independent | 0.01-0.1 | 0.05 default |
| **Performance gap (Δ)** | **Dependent** | **Target <5%** | **Primary metric** |
| Communication rounds (T) | Controlled | 50-200 | 100-150 expected |

### 2. Causal Mechanism

**Chain:** Foundation Model → Local Adapter Training → DP Noise → Secure Aggregation → FedProx Regularization → Convergence → Domain-Adapted Model

**Key Tension:** Privacy-utility tradeoff (stronger privacy = larger noise = worse performance)

**Critical Prediction:** ε≥5 enables Δ<5%; ε<3 may cause Δ>10% (hypothesis rejection zone)

### 3. Primary Predictions

**P1 (Main):** IF ε≥5, r≥16, μ=0.05, K≥5, δ≤1.0 THEN Δ<5% after T≤150 rounds

**P2 (Privacy-Utility):** Δ(ε=10)≤2%, Δ(ε=5)≤5%, Δ(ε=3)≤8%, Δ(ε=1)≤12%

**P3 (Rank Efficiency):** Performance saturates at r≈32 (diminishing returns beyond)

**P4 (Heterogeneity Robustness):** FedProx maintains Δ<8% for δ≤1.5 (vs FedAvg degrading to 10%+)

**P5 (Scalability):** K=10 optimal balance; K>20 shows diminishing returns

**Falsification:** Δ≥10% for ε≥5, K≥5, δ≤1.0 → REJECT hypothesis

---

## Contributions

### Theoretical
- Convergence rate bounds: Δ scales as O(σ² × r × d / (K × T))
- FedProx-LoRA extension for non-IID low-rank subspace learning
- Adapter aggregation bias analysis: O(δ² × r / d)

### Methodological
- **FedPEFT Algorithm:** Federated LoRA + DP-SGD + FedProx + Secure Aggregation
- Innovations: Adaptive clipping, privacy budget scheduling, proximal term annealing
- Implementation: pytorch-fedpeft extending pytorch-adapt + APPFL + Opacus

### Practical
- **Use Cases:** Multi-hospital clinical adaptation, multi-bank fraud detection
- **Compliance:** HIPAA/GDPR regulatory support via ε-DP guarantees
- **Toolkit:** Privacy accounting dashboard, communication cost estimator, heterogeneity analyzer

### Empirical
- **3 Domains:** Medical imaging, financial fraud, computer vision
- **6 Models:** ViT-B/L, ConvNeXt-B, BERT-base, RoBERTa, CLIP
- **Full Factorial:** {ε, r, μ, K, δ} with 4 baselines and privacy attack evaluation

---

## Key Related Work

### Foundation Model Adaptation
- **LoRA (Hu et al., 2021):** Core technique - FedPEFT extends to federated setting
- **VFMSeg (Xu et al., 2025):** Demonstrates adaptation effectiveness, FedPEFT adds privacy
- **MsHeCare (Hou et al., 2025):** Motivates clinical use case, assumes centralized data

### Federated Learning & Privacy
- **Privacy ML (Fang & Qian, 2021, 344 cit):** FL+Privacy foundation, pre-FM era
- **FedProx (Li et al., 2020):** Proximal term for heterogeneity - directly adopted
- **DP-SGD (Abadi et al., 2016):** Core privacy mechanism - applied to adapters

### Gap Positioning
**No prior work combines:** Foundation model + LoRA + Federated Learning + Differential Privacy at scale

---

## Phase 2B Readiness

### Sub-Hypothesis Decomposition

**SH1 (Existence):** Privacy-preserving adapter learning is feasible (Δ<10% for some ε, r)
- **Validation:** Single domain, K=10, vary ε and r
- **Effort:** 2-3 weeks

**SH2 (Mechanism):** Causal links function as predicted
- **Validation:** Ablation experiments (no DP, no FedProx, no secure aggregation)
- **Effort:** 3-4 weeks

**SH3 (Comparison):** FedPEFT achieves <5% gap vs centralized baseline
- **Validation:** Full comparisons across 3 domains vs 4 baselines
- **Effort:** 4-6 weeks

**SH4 (Scalability):** Performance holds across configurations
- **Validation:** Fractional factorial ~50 configs
- **Effort:** 5-6 weeks

**SH5 (Robustness):** Secondary predictions validated statistically
- **Validation:** Targeted experiments for P2-P6 with hypothesis tests
- **Effort:** 4-5 weeks

**Critical Path:** SH1 → SH2 → SH3 → SH4 → Main Hypothesis (18-24 weeks total)

### Readiness Status

✅ **Ready:**
- Foundation models accessible (ViT, BERT, CLIP)
- Datasets available (CheXpert, MIMIC-CXR, Kaggle fraud, Office-31, VisDA)
- Implementation infrastructure (PEFT, Opacus, pytorch-adapt, APPFL)
- Theoretical foundation solid (FL, DP, LoRA understood)
- Related work mapped (59 Phase 1 sources + 12 Phase 2A papers)

⚠️ **Risks:**
- **High:** APPFL scaling uncertain (may need custom FL implementation)
- **Medium:** Privacy-utility tradeoff might be worse (mitigation: expand ε target to 8-10)
- **Medium:** Heterogeneity beyond FedProx (mitigation: limit initial δ≤1.0)

⚠️ **Resource Needs:**
- Compute: 4-8 A100 GPUs × 200 hours (need allocation)
- Timeline: 18-24 weeks (longer than typical, prioritize critical path)
- Data agreements: CheXpert/MIMIC DUA (~2 weeks, initiate now)

### Open Questions (High Priority)

**Q1:** Optimal gradient clipping threshold C for LoRA adapters?
→ Resolve via hyperparameter search in SH1

**Q4:** Precise convergence criterion? (early stopping vs fixed rounds)
→ Define before experiments start

**Q6:** Baseline hyperparameters (same as FedPEFT vs separately tuned)?
→ Report both for fairness

---

## Next Steps

### Immediate Actions

1. **Secure Compute Resources:** Apply for GPU cluster allocation (4-8 A100s)
2. **Initiate Data Agreements:** Submit DUA applications for CheXpert, MIMIC-CXR
3. **Prototype FedPEFT:** Implement core algorithm with PyTorch DDP + Opacus (2 weeks)
4. **Define Convergence Criteria:** Establish consistent evaluation protocol

### Phase 2B Planning

**Entry Conditions:**
- ✅ Hypothesis clarified with testable predictions
- ✅ Sub-hypotheses decomposed with validation plans
- ✅ Related work positioned
- ⚠️ Compute resources secured (in progress)

**Expected Phase 2B Output:**
- Detailed verification plan for each sub-hypothesis (SH1-SH5)
- Experimental protocols (datasets, baselines, metrics, statistical tests)
- Resource allocation (timeline, compute, personnel)
- Risk mitigation strategies
- Success criteria and gate validation checkpoints

**Command:** `/phase2b-planning --hypothesis "H-FedPEFT-001" --input "02a_extended_hypothesis_full.md"`

---

## Appendix: Quick Reference

**Hypothesis Statement (1-sentence):**
FedPEFT enables foundation model domain adaptation across institutions with <5% performance gap vs centralized baselines while maintaining ε-differential privacy (ε=1-10).

**Primary Innovation:**
First integration of parameter-efficient fine-tuning (LoRA) with federated learning, differential privacy, and secure aggregation for foundation models at scale.

**Target Impact:**
Enable regulated industry deployment (healthcare HIPAA, finance GDPR) where data centralization is blocked.

**Key Technical Challenge:**
Achieve privacy-utility tradeoff allowing strong privacy (ε≥5) with minimal performance loss (Δ<5%) under realistic heterogeneity (δ≤1.5).

**Implementation Difficulty:** MEDIUM-HIGH (6-9 months PhD timeline)

**Publication Venues:**
- Primary: MLSys, ICLR (systems/ML), NeurIPS (federated learning track)
- Domain-specific: Medical imaging (MICCAI), Financial ML (ICAIF)

---

**Full Document:** `02a_extended_hypothesis_full.md` (comprehensive version with all sections)

**Status:** ✅ Phase 2A Extended Complete → Ready for Phase 2B Verification Planning

**Date:** 2026-02-06
