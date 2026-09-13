# Phase 2A Hypothesis: Bidirectional Alignment via Joint DPO + Attribute Training

**Hypothesis ID:** H-BD1-v1  
**Generated:** 2026-07-12  
**Workflow:** Phase 2A-Dialogue (Self-Play Loop, IC-Ablation)  
**Status:** CONVERGED (18 exchanges, all 6 criteria met)

---

## Executive Summary

This hypothesis proposes **joint optimization of Direct Preference Optimization (DPO) and attribute-conditioned generation** to achieve bidirectional human-AI alignment in a single training framework. By training with multi-task loss `L_total = 0.7·L_DPO + 0.3·L_attr`, the method simultaneously optimizes:

1. **AI-to-Human dimension:** Preference alignment (≥95% of DPO baseline win rate)
2. **Human-to-AI dimension:** User control via attributes (≥80% steering accuracy)  
3. **Emergent property:** Disentanglement of intrinsic quality from controllable attributes (ρ ≤0.3), outperforming sequential training by ≥5%

**Key Novelty:** First empirical validation of integrated bidirectional training. Joint approach creates emergent disentanglement superior to sequential (train DPO → fine-tune attributes), avoiding catastrophic forgetting.

**Avoids H-E1 Failure Modes:** Eliminates reward modeling (DPO's closed-form solution), uses verified real datasets (HH-RLHF 161k, OpenAssistant 88k), employs established metrics (IFEval, not custom AUC).

---

## Core Hypothesis Statement

**Under** LLM alignment settings with diverse user preferences,  
**If** we train a model using joint optimization of Direct Preference Optimization (DPO) and attribute-conditioned generation with `L_total = 0.7·L_DPO + 0.3·L_attr`,  
**Then** it will achieve:
- Preference win rate ≥95% of DPO baseline (AI-to-Human)
- Attribute steering accuracy ≥80% (Human-to-AI)  
- Disentanglement correlation ρ ≤0.3
- ≥5% improvement over sequential training on BOTH dimensions

**Because** joint training forces shared representations that separate intrinsic quality (DPO-optimized) from controllable attributes (user-steered) without catastrophic forgetting.

---

## Causal Mechanism (3 Steps)

1. **Multi-task joint training** forces model to learn shared representations satisfying both DPO (preference optimization) and attribute conditioning (user control) simultaneously via dual gradient pressure

2. **Shared representations disentangle** intrinsic quality (universally good features, captured by DPO) from controllable attributes (user-preference-specific dimensions, captured by attribute conditioning)

3. **Disentangled representations enable bidirectional alignment:** model produces high-quality outputs (DPO dimension) that users can steer via attributes (SteerLM dimension) without degrading either objective

**Evidence:** Multi-task learning theory (Caruana 1997), length-normalized DPO precedent (Park et al. 2024), catastrophic forgetting avoidance in joint vs sequential training.

---

## Testable Predictions (5 Primary)

**P1 (AI-to-Human Quality):** Preference win rate ≥95% of DPO baseline on held-out HH-RLHF test split  
- **Test:** GPT-4 judge on 1000 prompts  
- **Fail if:** <95% → joint degrades preference alignment

**P2 (Human-to-AI Control):** Attribute steering accuracy ≥80% (% matching requested levels ±0.5)  
- **Test:** Generate with 6 attribute combinations, measure via attribute predictor  
- **Fail if:** <80% → attribute conditioning ineffective

**P3 (Disentanglement):** Correlation ρ ≤0.3 between DPO scores and attribute scores  
- **Test:** Pearson correlation on 500 held-out responses  
- **Fail if:** ρ >0.5 → high entanglement, not truly bidirectional

**P4 (Generalization):** IFEval score drop ≤10% when trained on Alpaca/Dolly vs HH-RLHF  
- **Test:** Train on converted datasets, evaluate on IFEval  
- **Fail if:** >10% drop → method is dataset-specific

**P5 (Joint > Sequential):** Joint outperforms sequential baseline by ≥5% on BOTH win rate AND steering  
- **Test:** Direct comparison (same data splits, same metrics)  
- **Fail if:** Joint ≤ Sequential + 5% on ANY metric → no emergent benefit

---

## Experimental Setup

**Datasets:**
- Primary: Anthropic HH-RLHF (161k preference pairs, 80/20 split) ✅ VERIFIED ACCESSIBLE
- Attributes: OpenAssistant (88k with annotations) ✅ VERIFIED ACCESSIBLE  
- Fallback: Alpaca (52k) + Dolly (15k) via LLM-as-judge conversion  
- Evaluation: IFEval benchmark ✅ PUBLIC

**Model:** GPT-2 1.5B or Pythia 2.8B (matched to DPO paper scale)

**Baselines:**
1. DPO Standalone (AI-to-Human baseline)
2. SteerLM Standalone (Human-to-AI baseline)
3. Sequential (DPO → Attr) — key comparison for Prediction 5

**Training:** α=0.7 (DPO-weighted), learning rate 1e-5, batch 128, β=0.1 (DPO temperature)

---

## Novelty & Differentiation

| Prior Work | Our Contribution |
|------------|------------------|
| **DPO (Rafailov 2023)** | Adds Human-to-AI dimension via joint attribute training |
| **SteerLM (Dong 2023)** | Adds AI-to-Human dimension via joint DPO training |
| **Bidirectional Framework (Shen 2024)** | First empirical validation (framework paper had no implementation) |
| **Sequential Training** | Joint produces emergent disentanglement (≥5% better, Prediction 5) |

**Key Innovation:** Emergent disentanglement from joint training NOT achievable by sequential approaches. Enables users to have BOTH quality guarantees (DPO) AND personalized control (attributes) from single model.

---

## Key Assumptions & Risks

**A1:** Datasets accessible and sufficient quality  
- **Evidence:** Prof. Pax verified HuggingFace links (Exchange 15)  
- **If violated:** Fall back to Alpaca/Dolly (Prediction 4 tests this)

**A2:** DPO and attribute objectives compatible  
- **Evidence:** Multi-task learning standard practice  
- **If violated:** Training diverges (Predictions 1+2 test this)

**A3:** Attributes partially orthogonal to preferences (ρ < 0.7)  
- **Evidence:** Pre-training correlation test  
- **If violated:** Exclude redundant attributes (ρ > 0.9)

**A4:** Joint creates emergent benefit vs sequential  
- **Evidence:** Catastrophic forgetting theory  
- **If violated:** Contribution reduces to efficiency (Prediction 5 tests this)

**A5:** Metrics validly measure alignment  
- **Evidence:** IFEval uses verifiable criteria  
- **If violated:** Use multiple metrics to cross-validate

---

## Scope & Boundaries

**Applies to:**
- Text generation (instruction-following, dialogue, summarization)
- Preference-based optimization with offline datasets
- 3-5 interpretable attribute dimensions
- GPT-2 to GPT-J scale (1.5B-6B parameters)

**Does NOT apply to:**
- Multimodal alignment (vision+language)
- Real-time online preference collection
- Multi-stakeholder preference aggregation
- Constitutional AI constraint integration
- Production deployment >13B scale without additional validation

---

## Phase 2B Readiness

**Status:** ✅ READY

**Must Exist (H-E):** Datasets accessible (HH-RLHF, OpenAssistant), attribute orthogonality (ρ < 0.7)

**Mechanism to Test (H-M):** Multi-task joint training produces disentanglement (ρ ≤0.3) via shared representations

**Comparison (H-C):** Joint vs Sequential — must outperform by ≥5% on both dimensions

**Open Questions:**
- Optimal loss weight α (0.7 is starting point)
- Which specific attributes are orthogonal (pre-test required)
- Scaling to larger models

---

## Discussion Summary

**Exchanges:** 18 (MIN=15 satisfied)  
**Convergence:** All 6 criteria met + all personas participated  

**Key Refinements:**
- Exchange 6: Objective compatibility resolved via multi-task weighted sum  
- Exchange 11: Orthogonality concern raised, ρ < 0.7 test added  
- Exchange 12: Catastrophic forgetting argument for joint > sequential  
- Exchange 14: Five precise predictions consolidated  

**Final Verdict:** UNANIMOUS APPROVAL — hypothesis is rigorous, feasible, novel, and ready for Phase 2B planning.

---

**Next Phase:** Phase 2B — Verification Protocol Planning  
**Files Generated:**
- `03_refinement.yaml` (primary Phase 2B input)  
- `02_synthesis.yaml` (synthesis details)  
- `01_round_table/final_opinions.yaml` (persona verdicts)  
- `discussion_log.md` (complete 18-exchange transcript)
