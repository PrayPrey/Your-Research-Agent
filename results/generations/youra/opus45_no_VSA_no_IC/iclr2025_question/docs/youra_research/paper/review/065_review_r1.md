# Adversarial Review Round 1

**Paper**: Cross-Family Generalization of Single-Pass Uncertainty Probes for Hallucination Detection
**Date**: 2026-08-24
**Round**: R1 (Accuracy and Engagement)
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Persona 1: Accuracy Checker

### Mission
Verify all numerical claims against ground truth from 065_ground_truth.yaml and Phase 4 validation reports.

### Verification Results

| Paper Claim | Location | Ground Truth Source | Actual Value | Match |
|-------------|----------|---------------------|--------------|-------|
| Mean transfer gap 0.013 | Abstract, Section 5.2 | h-m2/04_validation.md | 0.0133 | ✓ |
| Max transfer gap 0.034 | Abstract, Section 5.2 | h-m2/04_validation.md | 0.0339 | ✓ |
| 6/6 pairs below 0.10 | Section 5.2 | h-m2/04_validation.md | 6/6 | ✓ |
| Llama→Mistral gap 0.010 | Table 2 | h-m2/04_validation.md | 0.0097 | ✓ (rounded) |
| Llama→Qwen gap 0.034 | Table 2 | h-m2/04_validation.md | 0.0339 | ✓ |
| Mistral→Llama gap 0.013 | Table 2 | h-m2/04_validation.md | 0.0134 | ✓ |
| Mistral→Qwen gap 0.017 | Table 2 | h-m2/04_validation.md | 0.0167 | ✓ |
| Qwen→Llama gap 0.003 | Table 2 | h-m2/04_validation.md | 0.0030 | ✓ |
| Qwen→Mistral gap 0.003 | Table 2 | h-m2/04_validation.md | 0.0034 | ✓ |
| Transfer matrix AUROC values | Table 1 | h-m2/04_validation.md | All match | ✓ |
| Train/Val split 653/164 | Section 4.1 | 065_ground_truth.yaml | 653/164 | ✓ |
| Layer selection (21/21/18) | Section 3.5 | 065_ground_truth.yaml | 21/21/18 | ✓ |

### Issues Found

| ID | Severity | Description |
|----|----------|-------------|
| — | — | No accuracy issues found |

### Summary
All numerical claims verified against ground truth. Rounding differences (0.010 vs 0.0097) are within acceptable tolerance for 2-decimal display.

---

## Persona 2: Bored Reviewer

### Mission
Evaluate paper engagement as a busy NeurIPS reviewer with 5 papers to review today.

### First Impression Checks

| Check | Result | Evidence |
|-------|--------|----------|
| Would I continue reading after abstract? | **YES** | Hook ("should fail but succeeds") grabs attention; concrete result (0.013 gap) stated |
| Is problem clear in 1 minute? | **YES** | Para 2 of intro: multi-sample expensive (5-10 passes), single-pass untested |
| Is novelty clear in 2 minutes? | **YES** | "First systematic cross-family validation" stated in contributions |
| Can I understand Figure 1 without text? | **YES** | Heatmap shows near-uniform colors = successful transfer |

### Engagement Assessment

| Question | Answer |
|----------|--------|
| Would I continue reading? | **YES** |
| At what point did I lose attention? | **NEVER** |
| Overall impression | Clean narrative, counterintuitive hook, well-structured |

### Issues Found

| ID | Severity | Description |
|----|----------|-------------|
| — | — | No engagement issues found |

### Summary
Paper maintains reader attention throughout. Abstract is compelling, problem/novelty clear quickly.

---

## Persona 3: Skeptical Expert

### Mission
Challenge novelty claims, baseline fairness, and identify missing limitations.

### Novelty Assessment

| Claim | Assessment |
|-------|------------|
| "First systematic cross-family validation" | **VALID** — Prior SEP work (Kossen et al.) tested within-model only |
| "Affine alignment for dimension mismatch" | **VALID** — Novel application to uncertainty probes |
| "Architecture-invariant encoding" | **QUALIFIED** — Evidence supports claim within tested models |

### Baseline Fairness

| Check | Result |
|-------|--------|
| Is multi-sample SE cited properly? | YES — Farquhar et al. 2024 cited |
| Is comparison fair? | **N/A** — No direct comparison run (limitation acknowledged) |
| Are baselines cherry-picked? | NO — Standard baselines mentioned |

### Limitations Check

| Expected Limitation | Acknowledged? | Location |
|--------------------|---------------|----------|
| PoC validation (random labels) | YES | Section 6.2, Limitation 1 |
| 7-8B models only | YES | Section 6.2, Limitation 2 |
| TruthfulQA only | YES | Section 6.2, Limitation 3 |
| Instruction-tuned only | YES | Section 6.2, Limitation 4 |

### Issues Found

| ID | Severity | Description |
|----|----------|-------------|
| MINOR-01 | MINOR | Table 2 shows 0.010 for Llama→Mistral; ground truth is 0.0097. Rounding display preference. |
| MINOR-02 | MINOR | Section 2.4 title "Our Position" is vague; "Our Approach" more conventional. |

### Summary
No overclaims detected. Limitations appropriately disclosed. Two minor style/clarity issues.

---

## Round 1 Summary

| Category | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 0 |
| MINOR | 2 |

### Persuasiveness Checks

| Check | Result |
|-------|--------|
| abstract_compelling | true |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | true |
| figure_1_self_explanatory | true |
| would_continue_reading | true |
| attention_lost_at | null |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 0 |
| missing_limitations | false |

### Recommendation

**CONDITIONAL ACCEPT** — Paper passes all critical checks. Minor issues deferred to human review.

---

## MINOR Issues (Deferred to Human Review)

1. **MINOR-01 (clarity)**: Table 2 Llama→Mistral gap shown as 0.010, actual is 0.0097
2. **MINOR-02 (style)**: Section 2.4 title "Our Position" could be "Our Approach"

These issues do not affect paper correctness or validity.
