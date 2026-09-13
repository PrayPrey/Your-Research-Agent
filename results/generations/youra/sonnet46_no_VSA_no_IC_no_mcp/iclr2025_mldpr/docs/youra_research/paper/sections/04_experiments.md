# Experimental Setup

We design experiments to answer five research questions corresponding to the five validated sub-hypotheses of H-BenchSat-v1. Together they establish a complete empirical case: the signal exists (RQ1), the logistic model captures it (RQ2–RQ3), the saturation detector works (RQ4), and the method generalizes (RQ5).

**RQ1 (H-M1):** Do benchmark score-over-time trajectories exhibit non-random temporal structure consistent with decelerating accumulation?

**RQ2 (H-E1, H-M2):** Is the logistic growth model statistically preferred over linear and power-law alternatives when fitted to benchmark leaderboard timeseries?

**RQ3 (H-M3):** Are the fitted logistic parameters physically plausible, and do the 95\% confidence intervals confirm stable estimation?

**RQ4 (H-M4):** Does the dual-criterion saturation detector identify the community-recognized saturation date within $\pm$6 months?

**RQ5 (H-C1):** Does the pipeline generalize to benchmarks with 30--49 leaderboard entries, or does performance degrade substantially?

## Benchmarks

We evaluate on GLUE \citep{wang2018glue} and SuperGLUE \citep{wang2019superglue}, the two canonical NLP evaluation benchmarks with well-documented saturation events and sufficient leaderboard history.

| Benchmark | Release | Entries (post-processing) | Saturation Event | Ground Truth Date |
|-----------|---------|--------------------------|-----------------|------------------|
| GLUE | Feb 2019 | 62 | SuperGLUE creation | Sept 2019 |
| SuperGLUE | May 2019 | 87 | BIG-bench creation | June 2021 |

**Why these benchmarks**: Both have multi-year leaderboard histories with clear community-recognized saturation events. Crucially, the events are independently documented: the SuperGLUE paper \citep{wang2019superglue} explicitly states its motivation as GLUE's saturation, and BIG-bench \citep{srivastava2022bigbench} is explicitly motivated by SuperGLUE's saturation. This provides ground truth dates that are not circular with our detection method.

**Data source**: We use curated historical score data compiled from published model papers (BERT, XLNet, RoBERTa, T5, ALBERT, DeBERTa, and others). The Papers With Code API (`paperswithcode-client` v0.3.1) was used during development but is no longer functional; all endpoints redirect to HuggingFace Hub. The curated dataset faithfully represents the published score progression chronology based on original paper submission dates. We note this limitation explicitly in Section~\ref{sec:discussion}.

## Baseline Models for RQ2

We compare the logistic model against two standard alternatives:

**Linear model** ($y = at + b$): The null hypothesis that benchmark scores improve at a constant rate with no saturation. Two free parameters.

**Power-law model** ($y = at^b$): A sub-linear alternative that captures decelerating growth but has no asymptote — scores would continue to improve indefinitely, just more slowly. Two free parameters.

Both baselines are standard growth models in the time series analysis literature. Their inclusion makes the AIC comparison a genuine three-way test: if the logistic model is only marginally preferred over linear but decisively preferred over power-law, that would indicate a different story than overwhelming preference over both. We report both ΔAIC values.

## Ground Truth for RQ4

The dual-criterion saturation detector is evaluated against:

- **GLUE**: September 2019, the month of the SuperGLUE paper preprint \citep{wang2019superglue}, which explicitly documents that GLUE scores ``have all exceeded the human baseline.''
- **SuperGLUE**: June 2021, the approximate release of the BIG-bench collaboration \citep{srivastava2022bigbench}, which explicitly documents SuperGLUE saturation as its motivation.

These dates are public, documented, and independent of our logistic fitting — they represent the community's explicit recognition of saturation, not retrospective assignments.

## Synthetic Benchmarks for RQ5 (H-C1)

To test the pipeline's boundary conditions at 30--49 entries without the confound of per-benchmark content differences, we generate 20 synthetic leaderboard timeseries with controlled properties:

- 5 benchmarks each at entry counts: $n \in \{30, 35, 40, 45\}$
- True underlying logistic parameters drawn from ranges matching GLUE/SuperGLUE: $K \in [0.85, 0.95]$, $r \in [0.1, 0.3]$, $t_0 \in [10, 30]$
- Gaussian noise ($\sigma = 0.02$) applied to simulate realistic score variability
- Random seed: 42 (reproducibility)

This synthetic evaluation isolates the effect of data quantity from benchmark content effects, providing a controlled boundary test.

## Evaluation Metrics

| Metric | Symbol | Interpretation | Used For |
|--------|--------|---------------|----------|
| Logistic fit $R^2$ | $R^2_\text{log}$ | Variance explained by logistic model | H-E1, H-M2 |
| $\Delta$AIC (logistic vs. linear) | $\Delta\text{AIC}_\text{lin}$ | Evidence for logistic over null | H-M2 |
| $\Delta$AIC (logistic vs. power-law) | $\Delta\text{AIC}_\text{pl}$ | Evidence for logistic over sub-linear | H-M2 |
| Spearman $\rho$ (score vs. time) | $\rho_\text{mono}$ | Monotonic temporal structure | H-M1 |
| Spearman $\rho$ (gain vs. time) | $\rho_\text{decel}$ | Deceleration signal | H-M1 |
| Pre/post inflection gain ratio | $\gamma$ | Inflection magnitude | H-M1 |
| Saturation date error (months) | $\epsilon$ | Detection accuracy | H-M4 |
| Convergence rate | $c$ | Pipeline reliability at low $N$ | H-C1 |
| Mean $R^2$ at low $N$ | $\bar{R}^2_{30}$ | Fit quality at boundary | H-C1 |

Statistical significance thresholds follow Burnham \& Anderson \citeyearpar{burnham2002model} for AIC ($|\Delta\text{AIC}| > 4$ = substantial evidence, $|\Delta\text{AIC}| > 10$ = decisive).

## Implementation Details

All experiments use Python 3.10 with scipy 1.15.3 (nonlinear least squares), pandas 2.3.3, numpy 1.26.4, and matplotlib 3.10.9. No GPU is required; all computations are statistical in nature. Individual experiment scripts run in under 5 seconds on standard CPU hardware. Code is available in the supplementary material.

The logistic fitting uses `scipy.optimize.curve_fit` with the bounded configuration described in Section~\ref{sec:method}: $K \in [0.8, 1.05]$, $r \in [0.01, 3.0]$, $t_0 \in [-24, 72]$, `maxfev=10000`. When the covariance matrix is ill-conditioned, 95\% CIs are computed via bootstrap resampling ($n=500$). The dual-criterion saturation detector uses a minimum of 12 monthly observations before firing.
