# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HDRL-v1
**Confidence Level:** 0.81

**Main Hypothesis:**
Under condition [instruction-following LLM training with CoT-derived decomposition annotations], if [HDRL objective supervises hidden states to encode hierarchical sub-task structure], then [compositional generalization accuracy on novel instruction combinations improves] because [internal representations aligned with compositional structure enable generalization per Li (2025) theoretical requirement that computational graph must match compositional structure].

**Alternative Hypothesis (H0):**
HDRL training does not improve compositional generalization beyond standard instruction tuning; any observed improvements are attributable to increased training compute or data augmentation effects rather than the hierarchical representation structure.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| HDRL Training Objective | Independent | Contrastive loss on hidden states + behavioral probe; L = L_instruction + λ₁*L_HDRL + λ₂*L_probe | λ₁ ∈ [0.1, 1.0], λ₂ ∈ [0.01, 0.1] |
| Compositional Generalization Accuracy | Dependent | SCAN length split accuracy, Chain-of-Instructions novel chain success rate | Baseline ~16% (CoT), Target >90% |
| Model Architecture | Controlled | LLaMA-7B base model | Fixed architecture |
| Training Data | Controlled | FLAN-CoT, GSM8K-CoT with auto-parsed decomposition annotations | ~100K examples |
| Baseline Method | Controlled | Standard instruction tuning, Least-to-Most prompting | Fixed comparison |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[HDRL Contrastive Loss]
    → [Hierarchical Hidden State Structure]
    → [Decomposition-Aware Processing]
    → [Improved Compositional Generalization]
```

**Step 1: HDRL Contrastive Loss → Hierarchical Hidden State Structure**
- Mechanism: Contrastive learning pulls together representations of related sub-tasks while pushing apart unrelated ones
- Evidence: Probing studies, SimCLR/CLIP demonstrate contrastive learning shapes representations effectively

**Step 2: Hierarchical Hidden State Structure → Decomposition-Aware Processing**
- Mechanism: Graded activation patterns enable model to internally process instructions as sub-task sequences
- Evidence: Behmer et al. (2023) - motor neuroscience competitive queuing

**Step 3: Decomposition-Aware Processing → Improved Compositional Generalization**
- Mechanism: Internal decomposition aligns computational graph with compositional structure
- Evidence: Li (2025) proves this is necessary and sufficient for generalization

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Probing literature, SimCLR | Contrastive learning creates separable clusters | Strong |
| Step2 → Step3 | Behmer et al. (2023) | Competitive queuing shows graded activation patterns | Medium |
| Step3 → Outcome | Li (2025) Theoretical | Computational graph must match compositional structure | Strong |

**Key Tension:**
- **Tension:** Least-to-Most prompting achieves 99% on SCAN via explicit decomposition prompts, but the question is whether REPRESENTATION-level supervision provides additional benefit beyond prompting.
- **Resolution:** This verification plan tests whether internal hierarchical structure provides robustness and efficiency advantages over prompting-based approaches.

### 1.4 Key Assumptions

1. **Hidden state representations can be supervised via contrastive learning**
   - Consequence if violated: HDRL loss will not create meaningful hierarchical clusters

2. **Decomposition-aware representations transfer to downstream tasks**
   - Consequence if violated: Good probing but no downstream improvement (representation-behavior gap)

3. **Sufficient decomposition-annotated data exists in CoT datasets**
   - Consequence if violated: Data construction becomes separate research problem

4. **Auxiliary HDRL loss does not destabilize language modeling**
   - Consequence if violated: Performance degrades; need careful loss weighting

### 1.5 Scope & Boundaries

**Applies to:** Instruction-following LLMs, compositional generalization tasks, models with accessible hidden states

**Does NOT apply to:** Non-compositional tasks, API-only models, inference-time-only interventions

**Limitations:** Requires CoT data, ~20% compute overhead, layer selection needs tuning

### 1.6 Testable Predictions

**Primary Prediction:**
**P1**: HDRL-trained models achieve >90% SCAN length split accuracy (vs ~16% baseline)
- Measurement: Paired t-test, n ≥ 25 runs, p < 0.05
- Falsification: Accuracy ≤ 25% triggers rejection

**Secondary Predictions:**
**P2**: Probing accuracy for sub-task identification >70% (vs <50% baseline)
**P3**: 50-70% inference token reduction vs Least-to-Most prompting

**Falsification Criteria:**
1. SCAN accuracy ≤ 25% (no improvement)
2. Probing accuracy < 60% (no hierarchical structure)
3. Good probing but downstream < 50% (no transfer)

### 1.7 SOTA Baseline (Optional)

*Not applicable - mechanism validation, not SOTA comparison.*

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 25 runs
- **Effect Size:** Cohen's d > 0.8 (large)
- **Test:** Paired t-test, α = 0.05 (one-tailed)
- **Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does HDRL training cause hidden states to exhibit hierarchical structure detectable by probing?"
- Verification type: Empirical (probing experiments)
- Critical: MUST PASS for mechanism validation

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism valid?"
- Will decompose to H-M1, H-M2, H-M3 in Phase 2B
- Verification type: Causal analysis with ablations

**SH3 (Comparison):**
"Does HDRL outperform baselines and provide efficiency advantages?"
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 5 (SH1 + SH2×3 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-HDRL-v1
- [x] Confidence level: 0.81
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified
- [x] Assumptions with consequences
- [x] Testable predictions (P1-primary, P2, P3)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. Compute cost for HDRL training on LLaMA-7B?
2. Which transformer layers for HDRL supervision?
3. Optimal λ₁, λ₂ loss balance?
4. Priority: SH1 (existence) first recommended

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
