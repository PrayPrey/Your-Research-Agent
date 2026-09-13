# Results

Our empirical findings demonstrate a clear separation between measurement feasibility and construct validity: linguistic markers can be reliably extracted from RLHF data with high variance (H-E1 validated), but they fail comprehensively to measure agency preservation (H-M refuted across all four validation criteria). We present results in the order designed to build this argument: extraction validation first, then effect size failure, internal consistency failure, and replication failure.

## H-E1: Measurement Feasibility Validated

**Q1: Can linguistic markers be reliably extracted with sufficient variance?**

Linguistic agency markers demonstrate high distributional variance across HH-RLHF responses, validating measurement infrastructure feasibility:

| Marker Type | Mean (per 100 words) | SD | CV | Threshold | Pass? |
|-------------|---------------------|----|----|-----------|-------|
| Modal verbs | 2.911 | 2.272 | **0.781** | >0.3 | ✓ |
| Hedging | 0.542 | 0.416 | 0.768 | >0.2 | ✓ |
| Alternatives | 0.089 | 0.112 | 1.258 | >0.2 | ✓ |

**Interpretation:** Modal verb CV=0.781 exceeds threshold by 161% (0.781 vs. 0.3), indicating substantial distributional variance. This high variance enables correlation testing with RLHF preference status—without sufficient variance, marker frequencies would be near-constant, precluding association detection.

**Extraction Precision:** Manual validation on 100-response random sample yields:
- **Precision:** 100% (0 false positives)
- **Recall:** 98.5% (3/200 modals missed due to POS tagging edge cases)
- **Inter-annotator agreement (κ):** 0.94 (>0.9 threshold)

**Cross-Split Consistency:** Modal verb CV is stable across data splits:
- Train split (N=321,600 responses): CV = 0.783
- Test split (N=17,104 responses): CV = 0.781
- Absolute difference: 0.002 (<1% variation)

**H-E1 Conclusion:** ✅ **VALIDATED**. Linguistic markers are extractable with high precision (100%), acceptable recall (98.5%), and sufficient distributional variance (CV=0.781, 161% above threshold) to enable correlation analysis. Measurement infrastructure validated—proxy construct validity testing can proceed.

---

## H-M: Proxy Construct Validity Refuted

While markers are measurable (H-E1 pass), they fail comprehensive construct validation across all four criteria: effect size, internal consistency, replication, and practical significance.

### Effect Size: Statistically Significant but Practically Negligible

**Q2: Do markers systematically differ between chosen/rejected with meaningful effect?**

Paired t-test results on 169,352 preference pairs:

| Metric | Chosen Mean | Rejected Mean | Difference | Cohen's d | p-value | d Threshold | Pass? |
|--------|------------|--------------|-----------|-----------|---------|-------------|-------|
| Modal verbs | 2.894 | 2.928 | -0.034 | **-0.0181** | <0.001 | ≥0.15 | ✗ |
| Hedging | 0.538 | 0.546 | -0.008 | -0.0192 | <0.001 | ≥0.15 | ✗ |
| Alternatives | 0.087 | 0.091 | -0.004 | -0.0356 | <0.001 | ≥0.15 | ✗ |

**Statistical Significance Paradox:** All three markers achieve p<0.001 (highly statistically significant) despite effect sizes 88-76% below meaningful threshold (d≥0.15). With N=169,352 pairs, even 1.2% frequency differences (modal verbs: 2.894 vs. 2.928) become "statistically significant" through massive statistical power—demonstrating that p-values alone are uninformative for practical significance with large samples.

**Effect Size Interpretation:**
- Cohen's d=-0.0181 represents only **12% of threshold effect** (0.0181 vs. 0.15)
- Absolute frequency difference: 0.034 per 100 words = **1.2% difference**
- For a 200-word response: chosen=5.79 modals, rejected=5.86 modals (0.07 difference)

**Direction Verified:** All three markers show chosen < rejected (negative Cohen's d), aligning with theoretical prediction (RLHF reduces agency markers). However, correct direction with negligible magnitude suggests weak confounds or measurement noise rather than robust mechanism.

**Figure 1: Effect Size Comparison** (see figures/paired_differences.png)
Forest plot visualizes Cohen's d with 95% confidence intervals for each marker. All three intervals exclude d=0.15 threshold, demonstrating comprehensive magnitude failure despite statistical significance.

### Internal Consistency: Markers Don't Form Unified Construct

**Q3: Do markers form unified agency construct (convergent validity)?**

Cronbach's alpha analysis tests whether three marker types correlate as expected if measuring single latent construct:

| Construct Test | Result | Threshold | Pass? |
|---------------|--------|-----------|-------|
| Cronbach's α | **0.4200** | >0.7 | ✗ |
| Mean inter-item correlation | 0.2861 | ~0.5 expected | ✗ |
| All items negatively correlated with chosen status | No (mixed signs) | Yes expected | ✗ |

**Interpretation:** α=0.42 falls **40% below acceptable threshold** (0.42 vs. 0.7), indicating poor internal consistency. The three linguistic markers do not converge on a unified "agency preservation" construct—instead, they tap disparate dimensions.

**Inter-Item Correlation Matrix:**

| | Modal Verbs | Hedging | Alternatives |
|---|------------|---------|--------------|
| **Modal Verbs** | 1.00 | 0.31 | 0.22 |
| **Hedging** | 0.31 | 1.00 | 0.35 |
| **Alternatives** | 0.22 | 0.35 | 1.00 |

Weak correlations (r=0.22-0.35, mean r=0.29) suggest markers measure different phenomena rather than converging on agency. For comparison, validated psychometric scales typically achieve inter-item correlations r>0.5 and Cronbach's α>0.8.

**Construct Invalidity Implication:** Low internal consistency indicates the markers likely measure confounded constructs (politeness, text quality, stylistic variation, uncertainty) rather than agency preservation. Validated proxies should show strong inter-item correlations if tapping the same underlying dimension.

###Cross-Split Replication: Effect Doesn't Replicate

**Q4: Does effect replicate across train/test splits?**

Separate paired t-tests for each data split reveal replication failure:

| Split | N Pairs | Cohen's d | p-value | d≥0.15? | p<0.05? | Overall |
|-------|---------|-----------|---------|---------|---------|---------|
| **Train** | 160,800 | -0.0187 | <0.001 | ✗ | ✓ | **FAIL** |
| **Test** | 8,552 | -0.0067 | 0.536 | ✗ | ✗ | **FAIL** |

**Replication Criterion:** ≥2/2 splits must pass both thresholds (d≥0.15 AND p<0.05)
**Actual Result:** 0/2 splits passed → **Zero replication**

**Critical Finding:** Train split shows tiny but statistically significant effect (d=-0.019, p<0.001) while test split shows neither magnitude nor significance (d=-0.007, p=0.54). This pattern indicates the train-split "effect" is a statistical artifact of massive sample size (N=160K) rather than a robust phenomenon that replicates in independent data.

**Power Analysis Verification:** Test split (N=8,552) achieves 95% power for d=0.15 effect, so replication failure cannot be attributed to insufficient statistical power. The test split is adequately powered to detect meaningful effects—yet observes d=-0.007 (95% below threshold).

**Figure 2: Cross-Split Forest Plot** (see figures/forest_plot.png)
Forest plot shows Cohen's d with 95% CIs for train and test splits separately. Train split CI barely excludes zero (due to massive N), while test split CI includes zero widely, visualizing replication failure.

### Summary: Comprehensive Proxy Validity Refutation

All four validation criteria failed:

| Criterion | Metric | Result | Threshold | Gap | Status |
|-----------|--------|--------|-----------|-----|--------|
| **Effect Size** | Cohen's d | -0.0181 | ≥0.15 | **-88%** | ✗ REFUTED |
| **Internal Consistency** | Cronbach's α | 0.42 | >0.7 | **-40%** | ✗ REFUTED |
| **Replication** | Splits passed | 0/2 | ≥2/2 | **Zero** | ✗ REFUTED |
| **Practical Significance** | Frequency diff | 1.2% | ~5% expected | **-76%** | ✗ REFUTED |

**Convergent Evidence:** Four independent validation criteria converge on the same conclusion—linguistic markers do not validly operationalize agency preservation in RLHF contexts. This is not a marginal failure (e.g., α=0.68 barely below 0.7) but comprehensive refutation with large gaps across all metrics.

## Unexpected Finding: Correct Direction Despite Negligible Magnitude

**Observation:** All three markers consistently show chosen < rejected (negative Cohen's d) despite negligible magnitude (d=-0.018 to -0.036). This pattern is unexpected because random noise would produce 50% positive, 50% negative directions.

**Competing Explanations:**
1. **Weak Mechanism:** Causal chain exists but operates at ~10% predicted strength (d=0.018 vs. 0.15)
2. **Confounded Variable:** Directness reduces markers, but RLHF only weakly selects for directness
3. **Measurement Bias:** Chosen responses systematically shorter/clearer, reducing markers as artifact

**Most Plausible:** Explanation #2 (confounded variable). Chosen responses may be slightly more direct/concise (quality confound), mechanically reducing all linguistic markers. Effect too small for agency interpretation but consistent enough to produce directional bias.

**Implication:** Markers may capture response quality/conciseness rather than agency preservation—a construct confound that invalidates agency interpretation even if correlations exist.

## Distribution Visualizations

**Figure 3: Modal Verb Density Plots** (see figures/density_plots.png)
Kernel density plots for chosen (blue) vs. rejected (red) modal verb frequencies show near-perfect overlap with negligible shift (mean difference 0.034/100 words). Overlap visualizes why effect size is trivial despite statistical significance.

**Figure 4: Marker Correlation Heatmap** (see figures/marker_correlations.png)
Heatmap of inter-marker correlations shows weak relationships (r=0.22-0.35), visualizing internal consistency failure. Validated constructs show r>0.5 across items; our markers show r<0.35, indicating disparate measurement.

## Statistical Power Paradox Demonstration

Our results provide a textbook demonstration of the statistical power paradox in large-scale NLP:

- **Massive Power:** N=169K yields >0.99 power for d=0.15 (threshold effect)
- **Trivial Significance:** d=-0.018 achieves p<0.001 despite being 88% below threshold
- **Misleading p-value:** Without effect size reporting, p<0.001 suggests "strong evidence" when actual effect is negligible
- **Lesson:** With N>100K, effect size is the primary validity criterion; p-values become uninformative for practical significance

This finding has methodological implications beyond our specific hypothesis: large-scale NLP studies must preregister effect size thresholds and report confidence intervals for practical significance, not rely solely on p-value thresholds.

---

## Results Summary

**H-E1 (Existence):** ✅ **VALIDATED** — Markers reliably extractable (precision=100%, CV=0.781, 161% above threshold)

**H-M (Mechanism):** ✗ **COMPREHENSIVELY REFUTED** — Effect size 88% below threshold (d=-0.018 vs. 0.15), internal consistency 40% below threshold (α=0.42 vs. 0.7), zero cross-split replication (0/2 splits passed), practical significance failed (1.2% frequency difference)

**Key Contribution:** Demonstrated separation between measurement feasibility (markers extractable) and construct validity (markers don't measure agency). Established precedent for multi-criterion proxy validation in AI alignment research, preventing deployment of statistically significant but practically invalid metrics.
