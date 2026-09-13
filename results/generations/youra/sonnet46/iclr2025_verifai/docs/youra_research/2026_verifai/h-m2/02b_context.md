# Phase 2B Context: h-m2

**Generated:** 2026-03-18 (JIT by Phase 2C step-01)
**Hypothesis ID:** h-m2
**Type:** MECHANISM (Step 2 of 4)

---

## Hypothesis

### Statement
Under model-specific pass@1 stratification from H-M1, if problems are assigned to hard (pass@1=0.0) and easy (pass@1>=0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because problems that are structurally hard tend to be hard across different architectures.

### Rationale
Confirming cross-model tier overlap validates that difficulty tiers capture intrinsic problem properties rather than pure model idiosyncrasy. A Jaccard > 0.3 is a minimal signal that the self-contained bootstrap produces meaningful stratification beyond random assignment.

### Gate
- **Type:** SHOULD_WORK
- **Pass Condition:** At least 1 of 3 model pairs has Jaccard > 0.3 for hard-tier overlap
- **If Fail:** Proceed with model-specific tiers only; reframe contribution as "competence-boundary calibration"

---

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| IV | Independent | Model-specific pass@1 tier assignments per (problem, model) |
| DV | Dependent | Jaccard similarity of hard-tier sets between model pairs; 6-point histogram shape |
| CV | Controlled | EvalPlus oracle; hard threshold fixed at pass@1=0.0 |

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** EvalPlus (HumanEval+ 164 + MBPP+ 378)
- **Type:** standard (code benchmarks)
- **Source:** Liu et al. 2023; https://github.com/evalplus/evalplus
- **Path:** evalplus Python package (pip install evalplus)
- **Hypothesis Fit:** Provides 542 problems with augmented test oracle for reliable correctness labeling; pass@1 from H-M1 already computed

### Model
- **Name:** NousResearch/Meta-Llama-3-8B, codellama/CodeLlama-7b-hf, deepseek-ai/deepseek-coder-6.7b-base
- **Type:** HuggingFace decoder-only LLMs
- **Source:** HuggingFace Hub
- **Hypothesis Fit:** Three families (general/code-adapted/code-specialized) provide architectural diversity for cross-model Jaccard comparison

---

## Verification Protocol

1. Compute hard-tier problem sets per model from H-M1 pass@1 values.
2. Calculate Jaccard similarity for all 3 model pairs (Llama3/CodeLlama, Llama3/DeepSeek, CodeLlama/DeepSeek).
3. Report 6-point pass@1 histogram (0.0–1.0) for each model.
4. Document cross-model overlap statistics.
5. Label tier assignments: model-specific (primary) vs. consensus-hard (exploratory).

---

## Success Criteria

- **Primary:** At least 1 of 3 model pairs has Jaccard > 0.3 for hard-tier overlap
- **Secondary:** Bimodal or skewed pass@1 distribution (not uniform)

---

## Dependencies

- **Prerequisites:** h-m1 (COMPLETED, PASS)
- **Key Output from h-m1:** pass_at_1_hm1_verified.json (FR-5.1 compliant)
  - Contains pass@1 per (problem, model) for all 542 problems × 3 models
  - Located at: h-m1/results/pass_at_1_hm1_verified.json

---

## Baseline Comparisons

| Method | Description |
|--------|-------------|
| Random assignment | Jaccard expected ~0.1 for random tier assignment with similar tier sizes |
| Model-idiosyncratic | Jaccard ≈ 0 would indicate completely different hard sets |
| Cross-model consistency | Jaccard > 0.3 indicates structural difficulty signal |

---

*Source: 02b_verification_plan.md Section 2.2 (H-M2)*
