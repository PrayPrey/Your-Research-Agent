# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-09
**Author:** Pray
**Hypothesis ID:** H1-iclr2024-setllm
**Confidence Level:** 0.85 (HIGH)
**Status:** ✅ READY for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
A modular three-layer architecture integrating (1) LoRA-based federated learning with client-aware adaptive differential privacy, (2) runtime unified attack detection with exponential moving average threat learning, and (3) mechanistic attention-based interpretability for security event explanation achieves simultaneous privacy preservation (ε≤5 differential privacy), adversarial robustness (≥90% detection rate), and human-comprehensible explanations (≥80% comprehension score) with end-to-end latency <200ms, while maintaining model performance within 5% of centralized non-private baseline.

**Gap Addressed:** Gap 2 - Unified Privacy-Security-Interpretability Framework

**Key Innovation:** First integration of all three trustworthiness dimensions with adaptive mechanisms inspired by biological immune systems and defense-in-depth principles from systems engineering.

---

## Core Contributions

**Theoretical:**
1. Synergistic multi-objective LLM trustworthiness framework proving privacy, security, and interpretability can be mutually reinforcing
2. Adaptive privacy budget allocation theory extending cryptography trade-offs to heterogeneous federated learning
3. Latency complexity bounds showing <200ms achievable via layered orchestration

**Methodological:**
1. Stable continuous threat learning protocol (EMA-based) with drift detection safeguards
2. Mechanistic attention-based security explanations bridging opaque detections and human analysts
3. Latency-budgeted orchestration architecture (Privacy: 30ms, Security: 100ms, Interpretability: 50ms)

**Practical:**
1. Production-ready unified LLM trustworthiness framework (open-source)
2. Comprehensive trustworthiness evaluation benchmark testing integration
3. Federated learning adaptive privacy toolkit for heterogeneous data sensitivity

---

## Testable Predictions

**P1 (Primary):** Framework achieves <200ms latency, ≥90% attack detection, ε≤5 privacy on LLaMA-7B
- **Falsification:** Latency >250ms OR detection <85% OR ε>8

**P2 (Secondary):** Adaptive privacy budgets improve utility by 15-25% over static budgets on non-IID data
- **Falsification:** <10% improvement (within noise)

**P3 (Secondary):** Mechanistic attention explanations achieve ≥80% human comprehension, >15pp better than SHAP/LIME
- **Falsification:** <75% comprehension OR <10pp improvement

---

## Sub-Hypotheses (Phase 2B Decomposition Preview)

**SH1 (Existence):** Component integration introduces <10% overhead vs. isolated implementations
**SH2 (Mechanism):** Adaptive privacy budgets achieve 15-25% utility improvement via client-aware allocation
**SH3 (Comparison):** Orchestrated framework achieves ≥50% latency reduction vs. naive sequential integration
**SH4 (Robustness):** EMA threat learning adapts to novel attacks (10% accuracy gain) without drift (FP <10% increase)
**SH5 (Utility):** Mechanistic attention explanations exceed SHAP/LIME by >15pp comprehension

---

## Implementation Scope

**In Scope:**
- LLaMA-7B/13B decoder-only transformers
- Federated learning: 10-100 clients, IID/non-IID
- Privacy: Differential privacy (ε∈[1,10]), adaptive budgets
- Security: Prompt injection, backdoor, adversarial attacks
- Interpretability: Attention-based mechanistic analysis (on-demand)
- Deployment: Inference-time <200ms latency

**Out of Scope:**
- Vision-language models, multimodal beyond text
- MPC, homomorphic encryption (complexity beyond MEDIUM)
- Training-time security, edge devices
- Domain-specific customization (medical, legal)

**Resources:**
- Compute: 4x A100 GPUs
- Timeline: 3-4 months (architecture 2w + implementation 6w + evaluation 4w)
- Data: HuggingFace (public), TrojAI (backdoor), 500-1000 security event annotations

---

## Baselines & Benchmarks

| Dimension | SOTA Baseline | Our Improvement |
|-----------|---------------|-----------------|
| Privacy | FL-DPLoRA (static DP) | +15-25% utility via adaptive budgets |
| Security | UniGuardian (multi-attack) | +Continuous threat learning (EMA) |
| Interpretability | SHAP/LIME | +>15pp comprehension via mechanistic attention |
| Integration | Naive sequential (~400ms) | -50% latency via orchestration (<200ms) |

**No Direct Unified Baseline:** First integration of all three dimensions

---

## Key Assumptions

**A1:** Clients can self-report data sensitivity scores (0-1) - federated institutions have data classification policies
**A2:** Attack types share detectable features - UniGuardian precedent validates
**A3:** Attention flow reveals causal triggers - mechanistic interpretability literature supports
**A4:** Latency budget achievable (30+100+50+20ms) - requires profiling-driven optimization
**A5:** Model utility degradation <5% acceptable - FL-DPLoRA maintains competitive performance
**A6:** Human comprehension ≥80% realistic - domain experts (security analysts), not general users
**A7:** EMA stability (α=0.1) prevents drift - standard online learning + anomaly detection safeguards

---

## Causal Mechanisms (Key Highlights)

**Mechanism 1 (Privacy-Utility):** Adaptive DP budgets (ε_client = ε_base × (1 + sensitivity)) optimize trade-off
- **Evidence Strength:** STRONG (FL-DPLoRA precedent + cryptography theory)

**Mechanism 4 (Security Integration):** Unified detection via shared feature extraction in single forward pass
- **Evidence Strength:** STRONG (UniGuardian published results)

**Mechanism 5 (Threat Learning):** EMA updates (α=0.1) enable stable continuous adaptation
- **Evidence Strength:** MEDIUM (standard ML, applied to new context)

**Mechanism 7 (Interpretability):** Mechanistic attention traces trigger token concentration
- **Evidence Strength:** MEDIUM (established technique, security application novel)

**Mechanism 10 (Orchestration):** Layered latency budgeting enables <200ms total
- **Evidence Strength:** STRONG (architectural principle, needs empirical validation)

**Key Tension:** Interpretability (O(L²) complexity) vs. latency (<200ms) → Resolution: On-demand + 50ms budget

---

## Phase 2B Readiness

**Readiness Score: 90% (READY with minor open questions)**

**✅ Complete:**
- Main hypothesis fully specified with quantitative targets
- 5 sub-hypotheses (SH1-5) defined with verification methods
- Variables (independent, dependent, control) identified
- 12 causal mechanisms mapped with evidence strength
- SOTA baselines + differentiation clear
- 3 testable predictions (P1, P2, P3) with statistical tests
- Scope boundaries defined
- Resource estimates realistic (4 GPUs, 3-4 months)

**⚠️ Open Questions (to resolve in Phase 2B):**
- **OQ1:** Data sensitivity validation protocol (affects SH2)
- **OQ2:** Interpretability latency optimization (50ms feasible?)
- **OQ3:** Human study comprehension question design (affects P3)
- **OQ4:** Novel attack generation for EMA evaluation (affects SH4)
- **OQ5:** Federated infrastructure simulation strategy (10-100 clients on 4 GPUs)
- **OQ6:** Integration testing protocol (end-to-end validation)

---

## Statistical Verification Design

**Sample Sizes:**
- Latency: N=1000 inference runs (detect <200ms with 95% CI)
- Detection: N=500 test samples (detect ≥90% rate with ±3% margin)
- Adaptive Privacy: N=5 federated runs × 10 clients (detect 15-25% utility gain)
- Human Study: N=20 analysts × 3 conditions (detect >15pp comprehension improvement)

**Statistical Tests:**
- P1: One-sample t-test (latency), binomial test (detection), DP accounting (privacy) - Bonferroni α=0.017
- P2: Paired t-test (adaptive vs. static DP) - α=0.05
- P3: ANOVA + Tukey HSD (mechanistic vs. SHAP/LIME vs. control) - α=0.05

**Expected Power:** ≥0.80 for all tests

**Falsification Criteria:**
- **Critical Failure:** Latency >250ms OR detection <85% OR utility degradation >10%
- **Major Concern:** Privacy ε>8 OR comprehension <70% with no SHAP/LIME improvement
- **Integration Failure:** Adaptive privacy <5% improvement over static

---

## Related Work Differentiation

**Foundational Surveys:**
- Yao et al. (2023, 971 cites): Established LLM security taxonomy → We address integration gap
- Friha et al. (2024, 121 cites): Identified lack of unified framework → We implement missing framework

**Component SOTA:**
- FL-DPLoRA (Yang et al., 2025): Privacy layer foundation → We add adaptive budgets + integration
- UniGuardian (Lin et al., 2025): Security architecture → We add threat learning + integration
- Mechanistic Interpretability (Pastor et al., 2025): Guided design → We apply to security explanations

**Benchmarks:**
- TrustLLM (ICML 2024): Evaluates dimensions separately → We test integration
- OpenFedLLM (452★): FL implementation → We add DP guarantees + adaptive allocation

**Cross-Domain:**
- Immunology → Adaptive threat learning (EMA)
- Systems Engineering → Layered orchestration (defense-in-depth)
- Cryptography → Privacy-utility trade-offs (adaptive budgets)

**Timeline:** 2023 (surveys) → 2024 (components) → 2025 (unified attempts) → 2026 (our integration)

---

## Next Steps: Phase 2B Verification Planning

**Objectives:**
1. Decompose main hypothesis into detailed sub-hypotheses with verification experiments
2. Design comprehensive evaluation protocol addressing all 6 open questions
3. Create implementation roadmap with milestones and risk mitigation
4. Finalize statistical analysis plan with power calculations

**Expected Deliverables:**
- Sub-hypothesis dependency graph (SH1-5 execution order)
- Detailed experiment specifications (datasets, metrics, baselines)
- Implementation timeline with checkpoints
- Risk mitigation strategies for each open question

**Timeline:** Phase 2B planning estimated 1-2 weeks

---

*Full detailed documentation available in: 02a_extended_hypothesis_full.md*

*Generated using YouRA Phase 2A Extended Workflow (YOLO MODE)*
*Date: 2026-02-09*
*Status: ✅ READY FOR PHASE 2B*
