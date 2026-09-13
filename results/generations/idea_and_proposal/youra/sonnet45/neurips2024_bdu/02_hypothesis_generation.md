# Phase 2A Extended: Hypothesis Summary (Phase 2B Ready)

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-LSBI-LM-001
**Confidence:** 0.90 (HIGH)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:** Performing Gaussian Process (GP) based Bayesian inference over frozen Large Language Model (LLM) hidden state representations will yield calibrated uncertainty estimates (ECE < 0.10) with computational tractability (<200ms inference) for billion-parameter language models, outperforming existing UQ methods (MC Dropout, ensembles, temperature scaling).

**Core Innovation:** First application of GP-based Bayesian inference to text-only LLM hidden states, inspired by neuroscience predictive coding principle (uncertainty over latent representations, not parameters).

**Key Differentiator:** Operates in latent space (hidden states, 4K-8K dimensions) vs. parameter space (billions) or input space (prompts), enabling tractable Bayesian inference while preserving pretrained knowledge.

---

## Clarified Hypothesis

### Core Statement

**Hypothesis:** Extracting embeddings from middle layers (L/2 to 3L/4) of frozen pretrained LLMs and training sparse GPs with inducing points (m=100-500) will achieve:
1. **Calibration:** Expected Calibration Error (ECE) < 0.10 on text classification tasks
2. **Superiority:** Outperform MC Dropout and match/exceed Deep Ensemble calibration
3. **Efficiency:** Inference overhead < 200ms per query
4. **Robustness:** OOD detection AUROC > 0.80 via GP epistemic uncertainty

**Alternative Hypothesis (H0):** GP-based UQ on frozen LLM embeddings will NOT achieve ECE < 0.10 OR will NOT outperform existing baselines.

### Testable Predictions

**P1 (Primary):** ECE < 0.10 on SST-2 & MNLI, outperforming MC Dropout by 10%+ relative improvement
**P2:** OOD detection AUROC > 0.80 (in-distribution vs. medical/scientific text)
**P3:** Inference latency < 200ms per query on single A100/V100 GPU
**P4:** Middle layers (L/2 to 3L/4) optimal for GP-UQ (lowest ECE)

### Falsification Criteria

**Hard Falsification (REJECT):**
- ECE ≥ 0.10 on in-distribution tasks (calibration failure)
- Worse than ALL baselines on BOTH tasks (no improvement)
- Inference > 500ms per query (deployment impractical)

**Soft Falsification (REVISE):**
- Pilot (GPT-2) ECE ≥ 0.10 (cross-modal transfer assumption violated → revise kernel/method)
- OOD AUROC < 0.70 (epistemic uncertainty not capturing shift → revise OOD mechanism)

---

## Key Variables

| Variable | Type | Definition | Target/Range |
|----------|------|------------|--------------|
| **Layer Selection** | Independent | Transformer layer for embedding extraction | L/4, L/2, 3L/4 (validate) |
| **Inducing Points (m)** | Independent | Sparse GP approximation parameter | 100, 200, 500 |
| **Calibration Size** | Independent | Labeled examples for GP training | 1K, 5K, 10K |
| **ECE** | Dependent (Primary) | Expected Calibration Error | **Target: < 0.10** |
| **OOD AUROC** | Dependent | Distribution shift detection | **Target: > 0.80** |
| **Inference Time** | Dependent | Latency per query | **Target: < 200ms** |

---

## Causal Mechanism

```
Frozen LLM → Hidden State Extraction (L/2 to 3L/4) → Sparse GP Training
→ GP Posterior (Epistemic Uncertainty) → Calibrated Predictions (ECE < 0.10)
```

**Why It Works:**
1. **Dimensional Reduction:** 4K-8K embeddings (tractable) vs. billions of parameters (intractable)
2. **Information Preservation:** Hidden states encode task-relevant semantics + uncertainty (Zur et al. 2025)
3. **Bayesian Rigor:** GP provides exact posterior in function space (calibration guarantees)
4. **Knowledge Preservation:** Frozen LLM maintains pretrained capabilities

**Evidence:**
- GroVE (2025): GP-GPLVM on frozen CLIP embeddings → SOTA calibration (validates mechanism on multimodal)
- Zur et al. (2025): LLM hidden states encode uncertainty information (validates assumption)
- VAE-Bayesian (2024): 100ms latency on 1K-4K dimensions (validates tractability)

**Key Tension:** Text-only LLM embeddings (autoregressive training) may differ from multimodal CLIP embeddings (contrastive training) → **Pilot validation de-risks this**

---

## Key Assumptions

| Assumption | Risk Level | Testability | Contingency |
|------------|-----------|-------------|-------------|
| **Hidden states encode sufficient info** | LOW | Pilot: GPT-2 ECE < 0.10 | Multi-layer GP if single layer fails |
| **Text-only embeddings support GP** | MEDIUM | Cross-domain evidence (GroVE) + pilot | Kernel engineering, BNN alternative |
| **Sparse GP maintains calibration** | LOW | Full GP vs. sparse comparison | Increase m or SVGP variants |
| **1K-10K data sufficient** | LOW | Learning curves | Few-shot GP methods |

---

## Scope

**In-Scope:**
- Tasks: Text classification (sentiment, NLI), extractive QA
- LLMs: Frozen pretrained transformers (GPT-2, Llama-2, GPT-3.5)
- Uncertainty: Epistemic, calibration, OOD detection
- Hardware: Single GPU/8-GPU node (standard research)

**Out-of-Scope:**
- Generative tasks (open-ended text generation)
- Multi-turn dialogue (sequential uncertainty)
- Multimodal (covered by GroVE 2025)
- Fine-tuned models (focus on frozen)

---

## Contribution Summary

**Theoretical (C1-C3):**
- First GP-based Bayesian inference on text-only LLM hidden states
- Cross-domain transfer from neuroscience predictive coding
- Formal characterization of latent-space UQ for frozen models

**Methodological (C4-C7):**
- Sparse GP framework for scalable LLM UQ (<200ms overhead)
- Validation-based layer selection protocol
- Pilot validation de-risking strategy (1 week GPT-2 + SST-2)
- OOD detection via GP epistemic uncertainty

**Practical (C8-C10):**
- Frozen LLM knowledge preservation (no retraining)
- Comprehensive baseline comparison (ensemble, dropout, Textual Bayes)
- Open-source implementation (BoTorch, GPyTorch)

**Novelty:** No existing work combines GP + text-only LLM hidden states
- Textual Bayes (2025): Prompt-level, not latent
- GroVE (2025): Multimodal CLIP, not text-only
- SAL-GP (2025): Vision CNNs, not language

---

## Related Work

**Direct LLM UQ:**
1. Textual Bayes (2025): Bayesian prompting (input space) - complementary
2. LLM-SSM (2025): Hybrid LLM-Bayesian for time-series - validates integration
3. Linear Probes (2025): Hidden states encode uncertainty - validates assumption

**Cross-Domain Latent UQ:**
4. GroVE (2025): GP-GPLVM on frozen CLIP - closest analog, validates mechanism
5. SAL-GP (2025): Layer-wise GP calibration for CNNs - validates layer selection
6. Latent BO (2025): Posterior inference in latent space - validates tractability

**Foundations:**
7. Predictive Coding (2024): Neuroscience motivation - theoretical foundation
8. UQ Review (2020): Landscape of UQ methods - positions LSBI-LM
9. Conformal Prediction (2021): Alternative UQ paradigm - complementary
10. VAE-Bayesian (2024): 100ms on 1K-4K dims - computational benchmark

**Implementation:**
11. BoTorch (3.4K⭐): Sparse GP implementation tool
12. Uncertainty-toolbox: Calibration metrics (ECE, Brier, NLL)

---

## Phase 2B Readiness

### Sub-Hypothesis Decomposition (Preview)

**SH1 (Existence):** Frozen LLM hidden states encode sufficient uncertainty information
- **Verify:** Extract L/4, L/2, 3L/4 → Train GPs → At least one achieves ECE < 0.10
- **Dependencies:** None (foundational)

**SH2 (Mechanism):** Sparse GP provides tractable Bayesian inference
- **Verify:** Sparse (m=500) vs. full GP (ECE degradation < 0.02), Inference < 200ms, Training < 4h
- **Dependencies:** Requires SH1

**SH3 (Comparison):** LSBI-LM outperforms existing methods
- **Verify:** ECE vs. MC Dropout, Ensemble, Temp Scaling, Textual Bayes on SST-2, MNLI
- **Dependencies:** Requires SH1 + SH2

**Additional SH4-SH8:**
- SH4: Layer selection validates middle layers optimal
- SH5: GP uncertainty → OOD detection (AUROC > 0.80)
- SH6: Text-only embeddings support GP (pilot validation)
- SH7: Kernel choice impacts calibration (ablation)
- SH8: Calibration data size affects ECE (learning curves)

### Readiness Checklist

✅ **All Phase 2A-Extended Requirements Met:**
- [x] Core statement with quantitative predictions
- [x] Variables, causal mechanism, assumptions identified
- [x] Scope/boundaries, testable predictions, falsification criteria
- [x] Statistical design (hypothesis tests, controls, power analysis)
- [x] Contribution summary (theoretical, methodological, practical)
- [x] Related work (12 key papers mapped)
- [x] Sub-hypothesis decomposition preview (SH1-SH3)
- [x] Pilot validation de-risking protocol (GPT-2 + SST-2)
- [x] 100% Phase 1 evidence utilization (7/7 sources)

**Status:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

### Open Questions for Phase 2B

**HIGH PRIORITY:**
- Q1: Single-layer vs. multi-layer GP investigation strategy?
- Q2: Kernel engineering depth (RBF → Matérn → Spectral → Deep)?
- Q6: Pilot failure recovery plan (deep kernels, BNN, multi-layer)?
- Q7: Expand to 6+ tasks for statistical power (meta-analysis)?

**MEDIUM PRIORITY:**
- Q3: Calibration data requirements per task type (learning curves)?
- Q4: OOD threshold setting (adaptive vs. fixed percentile)?
- Q5: Hardware profiling (A100, V100, T4 latency distribution)?

**LOW PRIORITY (Future Work):**
- Q8: Production deployment integration (vLLM, TensorRT-LLM)?
- Q9-Q12: Scope extensions (generation, dialogue, multilingual, few-shot)?

---

## Statistical Verification Design

**Primary Test:**
- H1: μ_ECE(LSBI-LM) < 0.10 vs. H0: μ_ECE ≥ 0.10
- One-sample t-test, α = 0.05, bootstrap 95% CI

**Comparative Test:**
- H1: μ_ECE(LSBI-LM) < μ_ECE(Best Baseline)
- Paired t-test, Bonferroni α = 0.0125 (4 baselines)

**Controls:**
- Random seed variance (5 seeds, report mean ± std)
- Hyperparameter sensitivity (ANOVA on m, kernel, layer)
- Dataset artifacts (evaluate on 4+ diverse tasks)
- LLM architecture effects (GPT-2, Llama-2, BERT)

**Reproducibility:**
- Fixed seeds, public datasets, standard splits
- Open-source code (BoTorch/GPyTorch/HuggingFace)
- Detailed hyperparameters, full results released

---

## SOTA Baseline Comparison

| Method | Typical ECE | Computational Cost | Target |
|--------|-------------|-------------------|--------|
| Deep Ensemble | 0.08-0.12 | 5× inference | **Match calibration, lower cost** |
| MC Dropout | 0.12-0.15 | 10× inference | **10%+ improvement, lower cost** |
| Temperature Scaling | 0.10-0.12 | ~1× inference | **Match/exceed, richer uncertainty** |
| Textual Bayes (2025) | Unknown | Multiple prompts | **Match/exceed, lower cost** |
| **LSBI-LM (Ours)** | **< 0.10** | **1× + GP (~200ms)** | **Bayesian rigor + efficiency** |

---

## Pilot Validation Protocol (Phase 0)

**Purpose:** De-risk assumption that text-only embeddings support GP-based UQ

**Setup:**
- Model: GPT-2 (117M params)
- Task: Sentiment analysis (SST-2)
- Method: Extract all layers → Train lightweight GPs (m=100) → Measure ECE

**Success Criterion:** ECE < 0.10 AND beats MC Dropout

**Duration:** ~1 week, single GPU

**Go/No-Go Decision:**
- ✅ **GO:** ECE < 0.10 → Proceed to full implementation (Llama-2-7B)
- ⛔ **NO-GO:** ECE ≥ 0.10 → Investigate kernel engineering, BNN alternatives, multi-layer combination

**Rationale:** 1 week investment ($3K) prevents 3+ month waste ($30K+) if core assumption fails. ROI: 10:1

---

## Next Steps → Phase 2B

**Phase 2B will:**
1. Expand SH1-SH3 into detailed verification plans with experimental protocols
2. Identify SH4-SH8 additional sub-hypotheses (layer, OOD, kernel, data scaling)
3. Establish dependency graph between sub-hypotheses
4. Prioritize verification order (SH1 → SH6 pilot → SH2 → SH3)
5. Design experiments for each SH with success/failure criteria, statistical tests

**Deliverable:** Verification roadmap with prioritized experiments, resource estimates, timeline

---

**Full Document:** See `02a_extended_hypothesis_full.md` for complete details (variables, assumptions, related work, open questions)

---

*Generated: 2026-02-06 | Phase 2A-Extended | YOLO Mode | Confidence: 0.90*
*Ready for: Phase 2B Verification Planning*
