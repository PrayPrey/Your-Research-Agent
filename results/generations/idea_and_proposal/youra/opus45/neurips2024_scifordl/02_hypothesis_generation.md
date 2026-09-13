# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ICL-AlgoSelect-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under decoder-only transformer architectures performing in-context learning tasks (C), if we track circuit activations during inference as context examples accumulate (X), then we will observe specific algorithm selection circuits whose activation patterns quantitatively correlate with theoretical gradient descent predictions (Y), because transformers implement gradient descent through discoverable circuit mechanisms that progressively encode task-relevant algorithms (Z).

**Alternative Hypothesis (H0):**
Circuit activations during ICL do NOT correlate with gradient descent theoretical predictions; ICL operates through mechanisms unrelated to those predicted by Bai et al. and Ahn et al., or the relevant circuits are not localizable via activation patching.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Context example count | Independent | Number of (input, output) demonstration pairs in prompt | 0-32 examples |
| Circuit activation strength | Dependent | Causal effect on output logits via activation patching (TransformerLens) | 0.0-1.0 (normalized) |
| Task performance | Dependent | Accuracy on held-out test examples following ICL demonstrations | 0-100% |
| Model architecture | Controlled | Fixed transformer model | GPT-2 small/medium, Llama-7B |
| Task type | Controlled | Standardized ICL benchmark tasks | Linear regression, classification |
| Context format | Controlled | Consistent prompt template | Fixed delimiter tokens |

### 1.3 Causal Mechanism

**Step 1 → Step 2:** Context examples accumulate → Algorithm selection circuits activate
- *Mechanism:* ICL requires the model to identify task pattern from demonstrations before selecting appropriate algorithm (Bai et al. post-ICL validation mechanism)
- *Falsification:* Flat activation regardless of example count

**Step 2 → Step 3:** Algorithm selection circuits activate → Gradient descent operations execute
- *Mechanism:* Selected algorithm implements preconditioned GD on in-context data (Ahn et al. transformer-as-optimizer)
- *Falsification:* No correlation between circuit activations and GD operation predictions

**Step 3 → Outcome:** Gradient descent operations → Task performance improves
- *Mechanism:* Iterative optimization on context data yields better predictions (GD convergence)
- *Falsification:* Performance doesn't improve with more context despite circuit activation

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Bai et al. 2023 (270 cit.) | Post-ICL validation mechanism proves algorithm selection | Strong |
| Step2 → Step3 | Ahn et al. 2023 (252 cit.) | Global minimum implements preconditioned gradient descent | Strong |
| Step3 → Outcome | Nanda et al. 2023 (667 cit.) | Progress measures track circuit formation and performance | Strong |

**Key Tension:**
- *Tension:* Bai et al. proves algorithm selection theoretically exists, but Minegishi et al. 2025 and Singh et al. 2024 have already studied ICL circuits (induction heads) - risking novelty overlap
- *Resolution:* This verification plan explicitly targets algorithm SELECTION circuits (not induction heads) and validates GRADIENT DESCENT theory (not exploratory discovery), establishing clear differentiation from prior circuit work

### 1.4 Key Assumptions

1. **Algorithm selection is localizable to circuits**
   - Supporting evidence: Nanda et al. 2023 successfully localized grokking circuits to specific attention heads
   - Consequence if violated: Hypothesis becomes untestable via activation patching

2. **TransformerLens can identify ICL circuits**
   - Supporting evidence: Successfully used for induction heads, grokking, and other transformer behaviors
   - Consequence if violated: Need alternative mechanistic interpretability framework

3. **Theoretical predictions are circuit-testable**
   - Supporting evidence: Both Bai and Ahn papers provide specific computational predictions
   - Consequence if violated: Theory-circuit bridge is impossible; hypothesis becomes unfalsifiable

4. **ICL emerges consistently across models/runs**
   - Supporting evidence: Chan et al. 2022 showed ICL emergence is driven by distributional properties
   - Consequence if violated: Results won't replicate; need larger sample sizes

### 1.5 Scope & Boundaries

**Applies to:**
- Decoder-only transformers with demonstrated ICL capability (GPT-2, Llama-7B)
- Tasks: Linear regression ICL, classification ICL with controlled complexity
- Inference-time analysis (not training dynamics)

**Does NOT apply to:**
- Encoder-only models (BERT-style)
- Very small models without ICL capability
- Vision transformers or multimodal models

**Known Limitations:**
- May require multiple model sizes to validate generality
- Synthetic ICL tasks may not capture real-world ICL complexity

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Circuit-Theory Correlation):**
Circuit activation patterns will show statistically significant correlation (r > 0.5, p < 0.05) with gradient descent operation predictions from Ahn et al.

*Measurement:* Pearson correlation between circuit activation trajectory and theoretical GD loss curve
*Success Criteria:* r > 0.5 with p < 0.05 across n ≥ 20 task instances

**Secondary Predictions:**
**P2 (Existence):** Activation patching will identify specific attention heads/MLPs (≤10% of model parameters) whose ablation causes >50% drop in ICL performance.

**P3 (Progress Measure Validity):** Algorithm selection progress measures will predict task performance (R² > 0.6) better than simple context length (R² baseline).

**Falsification Criteria:**
1. **Primary Failure:** Correlation r < 0.3 between circuit activations and GD predictions
2. **Existence Failure:** No localizable circuits found (distributed representation)
3. **Mechanism Failure:** Circuit activations do not change with context accumulation

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do specific algorithm selection circuits exist in decoder-only transformers that activate during in-context learning?"
- Maps to: Primary prediction P1
- Critical: MUST PASS for verification to proceed

**SH2 (Mechanism):**
"Is the context-to-circuit-to-GD-to-performance pathway the actual causal mechanism?"
- Maps to: Causal mechanism (3 steps → H-M1, H-M2, H-M3)
  - H-M1: Context accumulation → Algorithm selection circuit activation
  - H-M2: Circuit activation → Gradient descent operation execution
  - H-M3: GD operations → Task performance improvement

**SH3 (Comparison):**
"Do algorithm selection progress measures predict task performance better than simple context length?"
- Maps to: Secondary prediction P3

**Total Sub-Hypotheses in Phase 2B:** 5 (SH1 + 3×H-M + SH3)

### Readiness Checklist

| Requirement | Status |
|-------------|--------|
| Hypothesis in "Under [C], if [X], then [Y] because [Z]" format | ✅ |
| Hypothesis ID assigned | ✅ |
| Confidence level specified | ✅ |
| Alternative hypothesis (H0) defined | ✅ |
| All variables have operationalization | ✅ |
| Causal mechanism has evidence at each step | ✅ |
| Causal chain length determined (N=3) | ✅ |
| Key tension identified with resolution | ✅ |
| Key assumptions list consequences | ✅ |
| At least 2 testable predictions | ✅ |
| Falsification criteria defined | ✅ |
| Baselines identified | ✅ |
| SH1, SH2, SH3 clear | ✅ |

**Result: 13/13 PASS** ✅

### Open Questions

1. **Resource Requirements:** GPT-2 small on single GPU feasible; Llama-7B may require multi-GPU. Estimate 2-4 hours per model/task.

2. **Data Availability:** Standard ICL benchmark tasks readily available. Verify TransformerLens compatibility for target models.

3. **Priority Verification Order:** SH1 → H-M1 → H-M2 → H-M3 → SH3 (existence first, then mechanism in causal order)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
