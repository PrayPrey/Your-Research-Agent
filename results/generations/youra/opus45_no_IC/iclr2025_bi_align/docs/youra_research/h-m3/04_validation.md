# H-M3 Phase 4 Validation Report

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **Hypothesis ID** | H-M3 |
| **Title** | Lower Delta Signals Accommodation |
| **Type** | MECHANISM |
| **Gate Type** | SHOULD_WORK |
| **Gate Verdict** | FAIL |

## Statement

Under conversations where AI formality delta is small, if we measure perceived attentiveness proxies, then attentiveness indicators correlate with small deltas.

**Prediction:** Lowest delta tercile (T1) has highest continuation rate; monotonic trend T1 > T2 > T3.

## Execution Summary

| Metric | Value |
|--------|-------|
| **Tasks** | 15/15 completed |
| **Coder-Validator Cycles** | 1 |
| **Experiment Duration** | 461.3s |
| **Dataset** | Anthropic/hh-rlhf |
| **Sample Size** | 327,977 turn pairs from 111,333 conversations |

## Experiment Results

### Tercile Continuation Rates

| Tercile | Delta Range | Continuation Rate | Sample Count |
|---------|-------------|-------------------|--------------|
| **T1 (Low Δ)** | Δ < 0.0037 | 0.6592 | 109,315 |
| **T2 (Mid Δ)** | 0.0037 ≤ Δ < 0.0547 | **0.7139** | 109,347 |
| **T3 (High Δ)** | Δ ≥ 0.0547 | 0.6087 | 109,315 |

### Statistical Analysis

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Monotonic Trend** | FALSE | T2 > T1 > T3 (not T1 > T2 > T3) |
| **Spearman ρ** | -0.0451 | Weak negative correlation |
| **p_naive** | ~0 | Highly significant |
| **p_robust** | 0.0000 | Bootstrap confirmed |
| **Effect Size (T1-T3)** | 0.0505 | Small effect |

## Gate Evaluation

### Pass Condition
Lowest delta tercile has highest continuation rate; monotonic trend T1 > T2 > T3, p_robust < 0.05

### Actual Results
- **Monotonic:** FALSE (T2 highest, not T1)
- **Statistical significance:** TRUE (p_robust < 0.05)
- **Gate Satisfied:** FALSE

### Failed Checks
1. Monotonic trend T1 > T2 > T3 not satisfied (T2 highest)

## Key Findings

1. **Mid-delta conversations have highest continuation rate (71.4%)** - This contradicts the hypothesis prediction that low-delta conversations would have the highest rate.

2. **Inverted U-shape pattern observed** - Continuation rates peak at moderate formality deltas, not at minimal deltas.

3. **Low-delta conversations (T1) show 65.9% continuation** - Lower than both T2 (71.4%) and marginally higher than T3 (60.9%).

4. **Weak negative correlation (ρ = -0.0451)** - Higher deltas weakly associate with lower continuation, but relationship is non-monotonic.

5. **Large sample size (n=327,977)** provides statistical power but effect sizes are small.

## Interpretation

The hypothesis that "lower formality delta signals accommodation which increases continuation" is **not supported** by the data. Instead:

- **Moderate accommodation (T2)** shows the strongest engagement signal
- **Too little delta (T1)** may indicate either perfect matching OR lack of adaptive behavior
- **High delta (T3)** shows lowest continuation, suggesting mismatch deters engagement

This suggests accommodation is not purely linear - there may be an optimal "Goldilocks zone" of formality adjustment.

## Figures Generated

| Figure | Description |
|--------|-------------|
| `tercile_bar_chart.png` | Continuation rates by tercile |
| `delta_histogram.png` | Distribution of formality deltas |
| `scatter_delta_continuation.png` | Delta vs continuation scatter |
| `bootstrap_distribution.png` | Bootstrap rho distribution |

## Phase 2C Handoff Data

### Proven Components
- Data loading pipeline (Anthropic/hh-rlhf)
- DeBERTa formality scoring with caching
- Tercile analysis with cluster bootstrap
- Figure generation

### Hyperparameters Used
- `n_boot`: 2000
- `seed`: 42
- `alpha`: 0.05
- `min_turns`: 2
- `batch_size`: 64

### Lessons Learned
1. Linear accommodation hypothesis too simplistic
2. Consider quadratic or threshold-based models
3. Mid-range accommodation may be optimal signal

## Recommendations

### For Dependent Hypotheses
- H-M4 and subsequent hypotheses should account for non-monotonic relationship
- Consider reframing "accommodation" as "optimal adjustment" rather than "minimal delta"

### Alternative Directions
1. Test quadratic model: continuation ~ delta + delta²
2. Define "accommodation band" (T2 range) as success metric
3. Investigate why T2 (moderate delta) predicts highest continuation

## Conclusion

**Gate Verdict: FAIL**

The SHOULD_WORK gate failed because the monotonic trend prediction was not observed. The data reveals a more nuanced relationship where moderate (not minimal) formality accommodation correlates with highest conversation continuation. This finding, while contradicting the original hypothesis, provides valuable insight for refining the accommodation theory.

---

*Generated: 2026-08-10T10:48:12+00:00*
*Phase 4 Validation Complete*
