# Phase 2A Extended: Hypothesis Summary for Phase 2B

**Date:** 2026-02-06
**Hypothesis ID:** H1-CompilerRL-LLM
**Confidence:** 0.82 (FEASIBLE)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
A reinforcement learning agent with validated LLM-guided exploration can optimize compiler partitioning strategies for production-scale LLM training (1000+ GPUs) more effectively than hand-tuned heuristics, achieving >10% end-to-end training speedup.

**Research Gap Addressed:**
Gap 2 - Production-Ready ML-Driven Compiler Optimization for LLM Scale (from Phase 1 Research)

**Key Innovation:**
Two-phase LLM-guided RL with pre-validation: validates LLM knowledge about SPMD partitioning before deployment, falls back to expert heuristics if validation fails, achieving risk mitigation while maintaining learning benefits.

---

## Quick Reference

### Core Variables

| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | RL policy parameters | Neural network weights |
| **Independent** | LLM guidance mode | Enabled/Disabled based on validation |
| **Dependent** | Training speedup | End-to-end time reduction (%) |
| **Controlled** | Hardware topology | 1024 H100 GPUs standardized |

### Primary Prediction

**P1:** Trained RL policy achieves >10% speedup on >70% of hold-out test models (10 models × 3 runs, p<0.05)

### Success Criteria (Falsification)

- **F1:** If speedup <5% on >50% of test models → HYPOTHESIS REJECTED
- **F3:** If RL training cost > deployment savings over 100 runs → PRACTICALLY INFEASIBLE

---

## Phase 2B Decomposition Preview

**SH1 (Existence):** Can LLM-guided RL learn effective compiler partitioning?
- Validate RL+LLM convergence and performance improvement over random initialization
- Dependency: None

**SH2 (Mechanism):** Do learned strategies generalize across workloads?
- Test policy generalization from 25 training models to 10 unseen test models
- Dependency: Requires SH1

**SH3 (Comparison):** Does RL+LLM outperform all baselines?
- Head-to-head benchmark: RL+LLM vs. torchtitan vs. Alpa vs. TePDist vs. Pure RL vs. Pure LLM
- Dependency: Requires SH2

---

## Key Contributions

### Theoretical
First empirical characterization of learned compiler partitioning generalization at production scale (1000+ GPUs), establishing bounds on cross-workload transfer learning.

### Methodological
Novel two-phase approach: (1) LLM knowledge pre-validation via prompting, (2) Conditional LLM-guided RL with expert fallback. Turns risk (LLM uncertainty) into methodological contribution.

### Practical
- **Cost Savings:** $1.2M per training run for Llama-3-405B scale (15% speedup)
- **Carbon Impact:** ~500 tons CO₂ reduction per major LLM training
- **ROI:** 100× return after 100 production deployments (breakeven at 3 runs)

---

## Related Work Summary

**Foundation Papers:**
- **DeCOS (2025):** RL+LLM for single-node compiler optimization → We extend to production-scale distributed
- **PartIR (2024):** Composable SPMD strategies theory → We empirically validate with learned policies

**Primary Baselines:**
- **torchtitan (2024):** Hand-tuned 3D parallelism → Our integration target and main comparison
- **Alpa (2022):** Heuristic-based automatic parallelism → State-of-the-art non-learned baseline

---

## Open Questions for Phase 2B

**Q1:** Does PartIR action space need extensions for LLM-specific patterns? (Medium Risk)
**Q2:** What is optimal LLM validation quality threshold? (Low Risk)
**Q4:** What features enable generalization vs. require retraining? (Medium Risk)

---

## Implementation Scope

**IN SCOPE:**
- Production LLM training: 1000-2048 GPUs, 70B-175B parameters
- PyTorch/torchtitan integration
- Transformer architectures (GPT, Llama, PaLM)
- Offline RL training with deployment inference

**OUT OF SCOPE:**
- Small-scale (<100 GPUs), inference-only, non-transformers
- Online RL adaptation (future work)
- Non-NVIDIA hardware without retraining

---

## Statistical Design Summary

- **Training Set:** 25 diverse LLM architectures
- **Test Set:** 10 hold-out unseen models
- **Runs:** 3 independent runs per model (n=30)
- **Primary Test:** One-tailed paired t-test (α=0.05, power>0.80)
- **Effect Size:** Target Cohen's d > 0.8 (large effect)

---

## Next Steps

**Phase 2B Tasks:**
1. Decompose hypothesis into detailed sub-hypotheses (SH1-SH3)
2. Design verification experiments with success criteria
3. Plan resource requirements (GPU clusters, model access)
4. Identify dependencies and critical path
5. Assess remaining risks and mitigation strategies

**Phase 2C Readiness:**
After Phase 2B completion, proceed to experiment design with:
- Detailed experiment specifications
- Implementation search for RL training infrastructure
- Code analysis for torchtitan integration
- Resource allocation planning

---

**Full Technical Details:** See `02a_extended_hypothesis_full.md`

*Generated by YouRA Phase 2A Extended Workflow*
*Auto-detected from Round 1 FEASIBLE hypothesis*
*YOLO Mode: Fully automated execution (no user interaction)*
