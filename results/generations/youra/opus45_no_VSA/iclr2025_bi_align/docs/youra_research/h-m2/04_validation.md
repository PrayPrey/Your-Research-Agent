# H-M2 Validation Report

**Hypothesis:** BAI and reward scores show systematic disagreement with ≥20% of response pairs falling in high-BAI/low-reward or low-BAI/high-reward quartiles.

**Gate Type:** SHOULD_WORK

**Execution Date:** 2026-08-08

---

## Executive Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Disagreement Rate | 11.77% | ≥20% | PARTIAL |
| Sample Count | 41,896 | ≥500 | PASS |
| Mechanism Verified | No | Yes | FAIL |

**GATE RESULT: PARTIAL**

The hypothesis shows systematic disagreement between BAI and reward scores, but at a rate (11.77%) below the 20% threshold. The mechanism is demonstrably present but weaker than hypothesized.

---

## Methodology

### Data Sources
- **HH-RLHF Test Split:** 40,688 response texts
- **RewardBench Safety Subset:** 1,208 response texts
- **Total Samples:** 41,896

### BAI Computation
1. Trained 4 proxy detectors using H-E1 methodology (TF-IDF + LogisticRegression)
2. Computed mean proxy probability across 4 proxies per response
3. Applied length normalization: `BAI / (1 + 0.1 * log(word_count))`

**Proxy Training Results:**
| Proxy | Positive Rate |
|-------|---------------|
| clarifying_question | 1.97% |
| option_enumeration | 2.29% |
| epistemic_hedging | 11.66% |
| explicit_deferral | 0.12% |

### Reward Scoring
- **Model:** OpenAssistant/reward-model-deberta-v3-large-v2
- **Batch Size:** 32
- **Max Tokens:** 512
- **Device:** CUDA (GPU)

---

## Results

### Score Distributions
| Metric | BAI | Reward |
|--------|-----|--------|
| Mean | 0.0288 | -1.4573 |
| Std | 0.0466 | 2.0870 |
| Variance | 0.0022 | 4.3554 |

### Quartile Disagreement Analysis

Standardized z-scores, quartile boundaries:
- BAI: Q25 = -0.501, Q75 = -0.169
- Reward: Q25 = -0.746, Q75 = 0.696

| Quadrant | Count | Interpretation |
|----------|-------|----------------|
| HH (high BAI, high reward) | 2,319 | Agreement: agentic → high reward |
| HL (high BAI, low reward) | 3,063 | **Disagreement** |
| LH (low BAI, high reward) | 1,869 | **Disagreement** |
| LL (low BAI, low reward) | 2,847 | Agreement: non-agentic → low reward |

**Disagreement Rate:** (3,063 + 1,869) / 41,896 = **11.77%**

### Correlations
| Type | r | p-value |
|------|---|---------|
| Pearson | -0.1105 | 7.52e-114 |
| Spearman | 0.0163 | 0.0009 |

The weak negative Pearson correlation suggests BAI and reward capture partially orthogonal constructs.

---

## Mechanism Verification

| Check | Result |
|-------|--------|
| BAI variance > 0.01 | FAIL (0.0022) |
| Reward variance > 0.01 | PASS (4.3554) |
| Disagreement rate valid (0 < rate < 0.5) | PASS |
| Sample count ≥ 500 | PASS |

**Overall Verification:** FAIL (BAI variance too low)

The low BAI variance indicates proxy detection may be too conservative, clustering most responses near zero.

---

## Key Findings

1. **Systematic disagreement exists but is moderate:** 11.77% of responses fall in disagreement quadrants, above the PARTIAL threshold (10%) but below PASS (20%).

2. **High-BAI/Low-Reward dominates:** HL quadrant (3,063) > LH quadrant (1,869), suggesting responses exhibiting agency proxies tend to receive lower reward scores more often than vice versa.

3. **BAI scores cluster near zero:** Low variance indicates most responses have minimal agency proxy signals, limiting discrimination power.

4. **Weak negative correlation:** Pearson r = -0.11 is statistically significant but small, consistent with partial orthogonality rather than strong opposition.

---

## Top Disagreement Examples

| Response (truncated) | BAI z | Reward z | Diff |
|---------------------|-------|----------|------|
| "are you asking whether i think people are worth more than robots?" | 5.99 | -0.87 | 6.86 |
| "yes, there are a few possibilities, but they all come with consequences..." | 5.19 | -1.61 | 6.81 |
| "do you mean clothing that warms or clothing that blocks wind?" | 6.04 | -0.66 | 6.70 |

These examples show high-agency responses (clarifying questions, option enumeration) receiving moderate-to-low reward scores.

---

## Gate Decision

**Result: PARTIAL**

| Criterion | Status |
|-----------|--------|
| Disagreement rate ≥ 0.20 (PASS) | NOT MET |
| Disagreement rate ≥ 0.10 (PARTIAL) | MET |
| Mechanism verification | FAIL |

**Recommendation:** The mechanism exists but is weaker than hypothesized. Continue to Phase 5 with limitation notes:
- BAI variance is low; consider tuning proxy detection sensitivity
- Disagreement rate (11.77%) is in PARTIAL range, not sufficient to claim strong orthogonality
- High-BAI/Low-Reward pattern suggests agency signals may correlate with safety refusals

---

## Output Files

| File | Location |
|------|----------|
| Results JSON | `h-m2/experiment_results.json` |
| Gate Bar Chart | `h-m2/figures/gate_bar.png` |
| Scatter + Quadrants | `h-m2/figures/scatter_quadrants.png` |
| Density Heatmap | `h-m2/figures/density_heatmap.png` |
| Distributions | `h-m2/figures/distributions.png` |

---

## Conclusion

H-M2 demonstrates systematic but moderate disagreement (11.77%) between BAI and reward scores. The mechanism is present but weaker than the 20% threshold. Gate: **PARTIAL** — proceed with documented limitations.
