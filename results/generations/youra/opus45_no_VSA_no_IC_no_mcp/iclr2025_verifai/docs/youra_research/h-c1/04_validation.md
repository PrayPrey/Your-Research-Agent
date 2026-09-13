# Phase 4 Validation Report: h-c1

**Hypothesis:** h-c1 (CONDITION — SHOULD_WORK gate)
**Statement:** Format benefits are larger for smaller models: Format × Model Scale interaction is significant with larger effect sizes for CodeLlama-7B than CodeLlama-34B than GPT-4
**Date:** 2026-08-28
**Verdict:** FAIL (not significant)

---

## 1. Implementation Summary

### Components Implemented
| Module | Status | Description |
|--------|--------|-------------|
| config.py | PASS | Factorial grid config, extends h-e1 CONFIG |
| orchestrate.py | PASS | 2×3 cell runner with caching |
| stats.py | PASS | Two-way ANOVA, effect sizes, contrasts |
| visualize_interaction.py | PASS | Interaction plot with CI |
| run_h_c1.py | PASS | Main pipeline entry point |

### h-e1 Reuse
All core modules (errors.py, models.py, prompts.py, repair_loop.py, evaluate.py) reused from h-e1 via sys.path import. No code duplication.

---

## 2. Experiment Results

### Data Collection
- **Samples per cell:** 542 (HumanEval+ 164 + MBPP+ 378)
- **Total observations:** 3,252 (6 cells × 542)
- **Design:** 2 (Format: raw, structured) × 3 (Model: 7B, 34B, GPT-4)

### Two-Way ANOVA Results
| Source | SS | df | F | p | η² |
|--------|-----|-----|------|-------|------|
| Format | 1.87 | 1 | 8.30 | 0.004 | 0.002 |
| Model | 34.95 | 2 | 77.63 | <0.001 | 0.039 |
| **Format × Model** | **0.78** | **2** | **1.74** | **0.176** | **0.001** |
| Residual | 730.75 | 3246 | — | — | — |

### Simple Effects (Structured − Raw)
| Model | Δ (%) | 95% CI | Cohen's d |
|-------|-------|--------|-----------|
| 7B | +11.4% | [5.6%, 17.3%] | 0.23 |
| 34B | +8.3% | [2.4%, 14.2%] | 0.17 |
| GPT-4 | +3.9% | [-1.2%, 9.0%] | 0.09 |

### Planned Contrast (Monotonic Ordering)
- **Pattern confirmed:** ✓ (Effect_7B > Effect_34B > Effect_GPT4)
- **Linear trend contrast:** L = -0.076, t = -1.90, p(one-sided) = 0.97

---

## 3. Success Criteria Evaluation

| Criterion | Threshold | Observed | Met? |
|-----------|-----------|----------|------|
| Interaction p-value (adj) | < 0.05 | 0.176 | ✗ |
| Interaction η² | > 0.01 | 0.001 | ✗ |
| Effect ordering | 7B > 34B > GPT4 | ✓ | ✓ |

**Overall:** 1/3 criteria met

---

## 4. Analysis

### What Worked
- Effect ordering matches prediction: smaller models show larger benefit from structured formatting
- Main effect of Format significant (p = 0.004): structured format helps overall
- Code infrastructure fully functional

### Why Interaction Not Significant
- Small effect magnitudes: differences between simple effects (11.4% vs 8.3% vs 3.9%) are modest
- η² = 0.001 indicates interaction explains <0.1% of variance
- The effect exists directionally but not at statistically significant levels with current N

### Implications
- h-c1 is a SHOULD_WORK (secondary) hypothesis
- The monotonic pattern exists but interaction effect size below threshold
- Does not invalidate main finding (h-e1): structured format improves repair success

---

## 5. Artifacts

- **Results:** `h-c1/code/outputs/results.json`
- **Statistics:** `h-c1/code/outputs/h-c1_stats.json`
- **Interaction plot:** `h-c1/code/outputs/figures/h-c1_interaction_plot.png`
- **Validation summary:** `h-c1/code/outputs/h-c1_validation_summary.json`

---

## 6. Gate Outcome

**SHOULD_WORK gate verdict: FAIL**

Effect ordering confirmed but interaction effect size (η² = 0.001) below required threshold (η² > 0.01). Hypothesis not supported at significance level α = 0.05.

*Note: SHOULD_WORK gate failure is recorded but does not block pipeline progression.*
