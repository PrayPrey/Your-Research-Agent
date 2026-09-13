# Introduction

Every major LLM pipeline uses data curation, yet optimal filtering parameters remain undiscovered. A 10% miscalibration in perplexity thresholds can waste millions in compute or leave noise in training data that dilutes learning signals. RedPajama, Dolma, and C4 all employ perplexity filtering, but each chose different thresholds with no controlled ablation to justify their choices. Without systematic guidance, practitioners must guess at parameters—an expensive proposition when each training run costs thousands of GPU-hours.

## The Problem of Curation Calibration

At the surface level, the machine learning community acknowledges that data quality affects LLM training, and that filtering helps. Most papers note that perplexity filtering and deduplication improve downstream benchmark performance. Yet this understanding remains remarkably shallow.

The deeper problem emerges when we examine how curation parameters are actually chosen. Current practice treats thresholds as discrete configuration choices—p30 versus p50 versus p70—rather than as continuous variables with quantifiable dose-response relationships. Pipeline papers compare final configurations (RedPajama versus Dolma versus C4) without isolating individual parameter effects. This methodological gap means we cannot attribute performance gains to specific curation decisions.

The core gap is straightforward: no controlled ablation study has isolated individual curation parameters while holding all other factors constant. The computational cost of systematic sweeps—each configuration requires a full training run—has deterred such investigation. As a result, the field lacks the foundational empirical work needed to transform curation from art to science.

## Key Insight: Dose-Response Relationships

Our central insight is that perplexity filtering exhibits a concave dose-response relationship with benchmark performance. Too permissive filtering includes noise that dilutes gradient signals; too strict filtering removes diversity that enables generalization. This creates a characteristic inverted-U response curve with an identifiable optimum.

Prior work missed this pattern because curation pipelines have been compared holistically rather than parameter-by-parameter. By treating perplexity thresholds as continuous variables and applying controlled experimental design—fixing token budget, architecture, and evaluation protocol while varying only the parameter under study—we can map the effect surface and identify the peak.

## Contributions

Building on this insight, we make three contributions:

1. We establish the existence of non-monotonic dose-response relationships between perplexity filtering thresholds and benchmark performance. Using polynomial regression with model selection (AIC/BIC), we confirm that quadratic models fit significantly better than linear ones (R² = 0.985), with peaks consistently occurring in the p40-p60 range.

2. We validate the underlying mechanism through convergence dynamics analysis. Training on unfiltered data (p0) shows 40% higher convergence AUC (worse) compared to intermediate filtering (p50), directly demonstrating noise dilution effects. Conversely, over-strict filtering (p90) underperforms moderate thresholds, confirming diversity loss at high stringency.

3. We provide practical guidance for practitioners. CPDR-optimized configurations outperform RedPajama defaults by 1.32%, and our scale transfer analysis shows that optimal thresholds identified at 125M scale transfer to 1B scale with ratio 0.85—meaning small-scale sweeps can inform large-scale training with approximately 15% discount.

This work represents the first controlled dose-response study for LLM curation parameters with proper confound control through fixed-token experimental design. We organize the paper as follows: Section 2 discusses related work in data curation and quality filtering, Section 3 presents our methodology, Section 4 describes our experimental setup, Section 5 presents results, and Section 6 discusses implications and limitations before concluding in Section 7.
