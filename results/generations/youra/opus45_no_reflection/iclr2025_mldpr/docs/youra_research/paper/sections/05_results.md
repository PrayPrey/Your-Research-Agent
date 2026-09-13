# Results

We report results for each sub-hypothesis, proceeding from existence signal through mechanism verification chain. Five of six hypotheses passed their gates; one (h-m5) was refuted, yielding an important unexpected finding.

## Phase Transition Signal (h-e1)

Our primary research question asks whether aggregate Gini exhibits structural breaks. PELT detected two change points at April 2019 and March 2021, with the segmented model substantially outperforming the monotonic baseline.

| Model | BIC | Δ from Monotonic |
|-------|-----|------------------|
| Monotonic | -480.49 | — |
| Segmented (2 breaks) | -497.63 | **+17.13** |

The BIC improvement of 17.13 provides strong evidence for structural breaks over monotonic trend. Both detected change points fall within the 2019-2022 window, aligning with foundation model milestones (GPT-2/BERT proliferation in 2019, GPT-3/ViT in 2020-2021).

Figure 1 shows the monthly Gini time series with detected change points marked. The segmented fit captures distinct concentration regimes: a baseline period (2018-2019), transition period (2019-2021), and post-transition regime (2021-2024).

**Interpretation:** This result confirms that foundation model emergence coincided with measurable structural breaks in benchmark concentration dynamics. The phase transition is not gradual drift but discrete regime changes.

## Foundation Model Emergence (h-m1)

All five foundation papers exceeded the 2σ impact threshold, with z-scores ranging from 117 to 703:

| Paper | Year | Z-score | Passes 2σ |
|-------|------|---------|-----------|
| BERT | 2019 | 703.4 | ✓ |
| GPT-3 | 2020 | 425.1 | ✓ |
| ViT | 2020 | 287.3 | ✓ |
| T5 | 2020 | 201.5 | ✓ |
| CLIP | 2021 | 117.2 | ✓ |

The field distribution had mean 53.5 citations and standard deviation 170.6 (sample size: 3,000 papers). Foundation papers exceeded this baseline by 100-700 standard deviations.

**Interpretation:** Foundation model papers achieved exceptional impact, validating the premise that they represented a paradigm shift capable of affecting the broader research ecosystem.

## Emergent Benchmark Creation (h-m2)

Of 1,439 emergent-capability benchmarks in PWC, 85.13% (1,225) were created post-2020:

| Period | Count | Proportion |
|--------|-------|------------|
| Pre-2020 | 214 | 14.87% |
| Post-2020 | 1,225 | **85.13%** |

The creation rate accelerated dramatically: 10.7 benchmarks/year pre-2020 vs 204.2 benchmarks/year post-2020, a **19x acceleration**.

Figure 4 shows the benchmark creation timeline, with a clear inflection point at 2020.

**Interpretation:** The research community responded to foundation model capabilities with an explosion of new evaluation paradigms. This supply-side response created the benchmarks that would later attract researcher attention.

## Researcher Attention Shift (h-m3)

Emergent benchmark share increased from 7.53% pre-2021 to 26.54% post-2021, a shift of +19.02 percentage points:

| Period | Emergent Share | Traditional Share |
|--------|---------------|-------------------|
| Pre-2021 | 7.53% | 92.47% |
| Post-2021 | 26.54% | 73.46% |

Chi-square test: χ² = 1025.23, p < 10⁻²²⁴

This is one of the largest effect sizes in our analysis—the attention shift is statistically unambiguous.

**Interpretation:** Researcher behavior changed dramatically. The demand side complements the supply side: new benchmarks were not only created but actively adopted.

## Traditional Benchmark Persistence (h-m4)

Traditional benchmarks (ImageNet, CIFAR, etc.) showed reduced dominance but strong persistence:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Share | 11.70% | Reduced dominance (<50%) |
| Papers | 47,068 | Strong persistence (>10k) |
| Dominance shift | 0.34 | From majority to minority |

Chi-square for share change: χ² = 16,447.83, p ≈ 0

Figure 8 shows the stacked area plot of traditional benchmark paper counts over time.

**Interpretation:** The ecosystem restructured without abandoning established evaluation. Traditional benchmarks remain important (47k papers) but no longer dominate research attention.

## Modality Divergence (h-m5): REFUTED

This hypothesis predicted that pre-2020 CV-NLP Gini correlation (>0.6) would drop post-2021 (<0.4), indicating modality fragmentation. The actual results refuted this premise:

| Period | CV-NLP Correlation r | n |
|--------|---------------------|---|
| Pre-2020 | **-0.131** | 24 |
| Post-2021 | 0.226 | 47 |

Fisher z-test: z = -1.361, p = 0.173 (not significant)

The pre-2020 correlation was *negative*, not >0.6 as hypothesized. Modalities were never unified to begin with.

**Interpretation:** This refutation yields an important finding: CV and NLP benchmark dynamics were always independent. Foundation models did not fragment a unified ecosystem; they restructured an already-siloed one. If anything, post-2021 correlation *increased* (though not significantly), suggesting foundation models may have synchronized rather than fragmented modality dynamics.

## Aggregate Results

| Hypothesis | Gate Type | Result | Key Metric |
|------------|-----------|--------|------------|
| h-e1 | MUST_WORK | **PASS** | BIC Δ = 17.13 |
| h-m1 | MUST_WORK | **PASS** | 5/5 papers >2σ |
| h-m2 | SHOULD_WORK | **PASS** | 85.13% post-2020 |
| h-m3 | SHOULD_WORK | **PASS** | χ² = 1025, p<10⁻²²⁴ |
| h-m4 | SHOULD_WORK | **PASS** | 11.7% share, 47k papers |
| h-m5 | SHOULD_WORK | **FAIL** | r_pre = -0.131 |

Overall: 5/6 hypotheses validated (83.3%). Both MUST_WORK gates passed. The single failure (h-m5) invalidates the modality divergence claim but yields the novel finding of inherent modality independence.
