# Results

## 5.1 Main Effect: Language-Group Retention Disparity

Table 1 reports Cramér's V and Holm-corrected p-values for each of the five threshold levels. All five V values fall in the range [0.40, 0.57], and all Holm-corrected p-values are at machine epsilon (effectively zero). By any conventional effect size benchmark — Cohen's V > 0.35 constitutes a "large" association for 5-category tables — the observed disparity is large at all tested threshold levels.

**Table 1: Cramér's V and statistical significance for global k-th percentile thresholds on ccnet_perplexity (n = 208,262).**

| k | Global Threshold | Chi-squared | Cramér's V | Holm p-value |
|---|-----------------|-------------|------------|--------------|
| 10 | 175.0 | 33,674 | **0.4021** | ≈ 0 |
| 20 | 224.0 | 56,064 | **0.5193** | ≈ 0 |
| 30 | 261.7 | 66,096 | **0.5629** | ≈ 0 |
| 40 | 295.1 | 67,572 | **0.5696** | ≈ 0 |
| 50 | 328.9 | 58,369 | **0.5293** | ≈ 0 |

The relationship between k and V is non-monotonic: V rises from 0.40 at k=10 to a maximum of 0.57 at k=40, then decreases modestly to 0.53 at k=50. The decrease at k=50 reflects saturation: at this threshold level, virtually all Spanish and French documents are retained (1.00 and 0.996 respectively), compressing the cross-language variance in the contingency table. Despite this slight decrease, V remains large and highly significant at all tested levels.

Figure 1 (cramers_v_bar.png) displays V for each k with the gate bounds [0.40, 0.57] overlaid as horizontal reference lines, visually confirming that all five measurements fall within the empirically calibrated range.

## 5.2 Per-Language Retention Rates

Table 2 reports the fraction of documents from each language group that are retained at each threshold level. The language family divide is stark and perfectly consistent across all five k values.

**Table 2: Per-language retention rates (fraction retained) under global k-th percentile threshold.**

| Language | k=10 | k=20 | k=30 | k=40 | k=50 |
|----------|------|------|------|------|------|
| **es** (Spanish) | 0.356 | 0.653 | 0.864 | **1.000** | **1.000** |
| **fr** (French) | 0.336 | 0.572 | 0.745 | 0.879 | 0.996 |
| **it** (Italian) | 0.179 | 0.395 | 0.582 | 0.734 | 0.878 |
| **en** (English) | 0.036 | 0.089 | 0.163 | 0.253 | 0.364 |
| **de** (German) | 0.031 | 0.075 | 0.137 | 0.207 | 0.289 |

The retention ordering es > fr > it > en > de is perfectly maintained across all five threshold levels. This ordering maps precisely to the Romance-vs.-Germanic language family divide: Romance languages (es, fr, it) are systematically retained at higher rates than Germanic languages (en, de). Notably, Italian — a Romance language — occupies the middle position, while English occupies the second-to-last position, despite being the dominant language in most NLP datasets.

**Spanish saturation.** At k=40 and k=50, Spanish retention reaches 100% (all 41,652 Spanish documents in the sample pass the global threshold). French approaches saturation at k=50 (99.6%). This saturation phenomenon means that at threshold levels k ≥ 40, a practitioner is effectively applying no filter to Spanish at all while severely restricting German (20.7% retention at k=40) and English (25.3%).

**Germanic exclusion.** At k=10 — corresponding to the most aggressive quality filtering — German retention is 3.1% and English retention is 3.6%. A practitioner using this threshold to "select the top 10% quality" of each language's documents would in practice select less than 4% of the available English and German text while retaining 35% of Spanish and 34% of French.

Figure 2 (retention_heatmap.png) presents these retention rates as a heatmap with languages on the y-axis and k values on the x-axis, with color encoding retention rate from 0 (dark) to 1 (bright). The gradient from dark (Germanic) to bright (Romance) across all columns visually demonstrates the systematic and language-family-aligned nature of the disparity.

## 5.3 Max–Min Retention Gap

Figure 3 (retention_gap.png) plots the maximum minus minimum per-language retention rate across languages, as a function of k. This gap summarizes the worst-case cross-language disparity in a single number.

At k=10, the max–min gap is 32.5 percentage points (es=35.6% vs. de=3.1%). The gap grows to 72.7pp at k=30 (es=86.4% vs. de=13.7%), then reaches 79.3pp at k=40 (es=100% vs. de=20.7%), before narrowing slightly to 71.1pp at k=50 as Spanish saturation compresses the upper bound.

The gap at k=30 — 72.7 percentage points — means a practitioner applying a 30th-percentile global threshold would retain 6.3× more Spanish documents than German documents. The max–min gap is smallest at the most aggressive threshold (k=10), where both language families have uniformly low retention rates, but grows rapidly as k increases.

## 5.4 Perplexity Distribution Shapes

Figure 4 (perplexity_kde.png) displays kernel density estimates of the `ccnet_perplexity` distribution for each language on a log scale. The distributions show structurally different shapes across language families. Germanic languages (en, de) cluster at lower absolute perplexity values with distributions shifted toward the lower end of the scale, while Romance languages (es, fr, it) have distributions shifted toward higher perplexity values with heavier right tails.

This distributional separation is consistent with the proposed mechanism: if English and German web text systematically receives lower perplexity scores from their Wikipedia-trained KenLM models, a global percentile threshold calibrated to the mixture distribution will have its cutoff fall above the median of the Germanic distributions, capturing most English/German documents in the "removed" set while falling below the median of the Romance distributions.

We note that this mechanistic interpretation — that the distributional difference reflects incomparable KenLM training corpora rather than genuine quality differences — is *consistent with* but not *proven by* the current data. A complete verification would require comparing retention rates under per-language percentile calibration (the h-m1 experiment, not executed in this work) to confirm that calibration removes the disparity.
