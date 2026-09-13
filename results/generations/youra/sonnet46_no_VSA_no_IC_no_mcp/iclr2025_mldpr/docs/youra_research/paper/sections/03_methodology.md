# Methodology

Our pipeline operationalizes the following chain of reasoning: if benchmark-specific overfitting accumulates gradually over time, the score-over-time trajectory will exhibit S-curve dynamics; the logistic growth model formally captures S-curve dynamics; therefore, fitting a logistic model to leaderboard timeseries and testing its formal preference via AIC provides an automated saturation detection procedure. Each component of the pipeline maps directly to one link in this chain.

## Overview

Given a benchmark $b$ with a leaderboard timeseries $\{(t_i, y_i)\}_{i=1}^{N}$ — where $t_i$ is the submission date (in months from benchmark release) and $y_i$ is the normalized performance score — our pipeline:

1. **Preprocesses** the timeseries (normalization, deduplication, eligibility filtering).
2. **Fits** three competing growth models: logistic, linear, and power-law.
3. **Compares** models via AIC to identify the statistically preferred model.
4. **Detects** the saturation date using a dual-criterion threshold applied to the fitted logistic curve.

We describe each stage with its rationale.

## Stage 1: Data Preprocessing

**Input**: Raw leaderboard entries — $(model\_name, score, date)$ triples from Papers With Code (or curated historical fallback; see Section~\ref{sec:experiments}).

**Normalization**: Scores are divided by the maximum possible score (100 for percentage metrics) to map them to $[0, 1]$. This ensures the logistic asymptote $K$ is interpretable as a fraction of theoretical maximum, enabling physical plausibility checks.

**Deduplication**: Only the highest score per calendar month is retained. This prevents models with many submission variants from dominating early or late periods in the timeseries, which would distort the S-curve shape.

**Eligibility filter**: We require $N \geq 30$ entries after preprocessing (relaxed from the initially-planned $\geq 50$ based on H-C1 boundary condition evidence). Below this threshold, the logistic model lacks sufficient data to identify all three phases (growth, inflection, plateau).

**Temporal alignment**: Dates are converted to months since benchmark release, yielding a numeric $t$-axis. This ensures $t_0$ (the inflection point) is interpretable in calendar time and allows the critical finding of negative $t_0$ (pre-launch inflection) to emerge naturally.

## Stage 2: Growth Model Fitting

We fit three candidate models:

**Logistic model** (our primary hypothesis):
$$y(t) = \frac{K}{1 + \exp(-r(t - t_0))}$$
where $K$ is the asymptote (carrying capacity), $r$ is the growth rate, and $t_0$ is the inflection point (time of maximum growth rate). This model is the natural mathematical description of any process with initial rapid growth and eventual saturation.

**Linear model** (null hypothesis):
$$y(t) = at + b$$
The null hypothesis that scores improve at a constant rate, with no saturation.

**Power-law model** (sub-linear alternative):
$$y(t) = at^b$$
A decelerating growth model that lacks a formal asymptote — benchmark scores would continue to improve indefinitely, just more slowly.

**Fitting procedure**: We use bounded nonlinear least squares (`scipy.optimize.curve_fit`) for the logistic model, with parameter bounds derived from domain knowledge:

| Parameter | Lower | Upper | Rationale |
|-----------|-------|-------|-----------|
| $K$ | 0.8 | 1.05 | Normalized scores near human parity; slight overshoot allowed |
| $r$ | 0.01 | 3.0 | Positive growth rate; upper bound prevents physically implausible instantaneous jumps |
| $t_0$ | −24 | 72 | **Critical**: negative $t_0$ allowed — inflection may predate benchmark launch |

The negative-$t_0$ bound (lower = −24 months) is a critical design decision motivated by the initial H-E1 fitting experiments: without it, the optimizer diverges for GLUE and SuperGLUE, whose publicly-available leaderboard data represents primarily the plateau phase of a logistic curve whose growth phase preceded systematic tracking.

**AIC computation**: For each model, we compute
$$\text{AIC} = 2k - 2\ln(\hat{L})$$
where $k$ is the number of free parameters (logistic: 3; linear: 2; power-law: 2) and $\hat{L}$ is the maximized likelihood (equivalent to $N \ln(RSS/N)$ under Gaussian noise assumption). We report $\Delta\text{AIC} = \text{AIC}_\text{logistic} - \text{AIC}_\text{alternative}$; negative values indicate logistic preference.

**Bootstrap confidence intervals**: When `pcov` (the covariance matrix from `curve_fit`) is infinite or ill-conditioned, we compute 95\% CIs via bootstrap resampling ($n=500$), drawing with replacement from the timeseries and refitting. This provides robust uncertainty quantification even for benchmarks with irregular submission patterns.

## Stage 3: Model Selection via AIC

Following \citet{burnham2002model}, we interpret $\Delta\text{AIC}$ as evidence against the null (linear or power-law) hypothesis:

- $|\Delta\text{AIC}| < 4$: Substantial support for both models; no clear preference.
- $4 \leq |\Delta\text{AIC}| < 10$: Substantial evidence for the preferred model.
- $|\Delta\text{AIC}| \geq 10$: Decisive evidence for the preferred model.

Negative $\Delta\text{AIC}$ values in our results are ≈−194 to −357, indicating overwhelming (decisive) evidence in favor of the logistic model — well beyond the threshold for any interpretive ambiguity.

**Parameter plausibility check**: We apply post-hoc physical plausibility criteria to the fitted logistic parameters: $K \in [0.8, 1.0]$ (near-human-parity asymptote), $r > 0$ (positive growth rate). We explicitly do not require $t_0 > 0$, as the pre-launch inflection is a valid physical outcome (see Section~\ref{sec:results}).

## Stage 4: Dual-Criterion Saturation Detection

A saturation date is detected when two conditions are simultaneously satisfied on the monthly-resampled timeseries:

$$\underbrace{\bar{y}_{\text{top-3}} \geq 0.99 \cdot K}_{\text{Asymptote proximity}} \quad \text{AND} \quad \underbrace{\Delta\bar{y}_{\text{monthly}} \leq 0.05 \cdot \max_t(\Delta\bar{y})}_{\text{Rate criterion}}$$

where $\bar{y}_{\text{top-3}}$ is the mean of the three highest scores observed up to month $t$, and $\Delta\bar{y}_{\text{monthly}}$ is the average monthly gain rate in a trailing window.

**Rationale for dual-criterion design**: The asymptote proximity criterion alone can trigger spuriously during noise fluctuations on the plateau; the rate criterion alone can trigger during brief growth pauses in the pre-saturation phase. Requiring both conditions simultaneously improves robustness:

- Asymptote proximity ($\bar{y}_{\text{top-3}} \geq 0.99 \cdot K$): Ensures benchmark performance has converged to within 1\% of the estimated ceiling.
- Rate criterion ($\leq 5\%$ of peak monthly gain): Ensures the improvement rate has fallen to negligible levels — ruling out temporary plateaus that precede a second growth phase.

**Empirically optimal variant**: We also report a variant with a relaxed asymptote threshold ($0.95 \times K$, 5\% rate), which achieves approximately one-month accuracy on both GLUE and SuperGLUE. The standard threshold (0.99×K) is more conservative and achieves three- and five-month accuracy.

## Scope and Eligibility

The pipeline requires: (1) $\geq 30$ leaderboard entries post-preprocessing; (2) date coverage from at least 2019 onward (to capture the modern pretraining era); (3) a known benchmark release date for temporal alignment. These criteria define the scope of the method. Prospective forecasting (detecting saturation before it occurs) is explicitly out of scope with the current 6-month-early truncation window, as demonstrated by the P3 negative result (Section~\ref{sec:results}).

## Figure Reference

Figure~\ref{fig:pipeline_overview} illustrates the complete pipeline, annotated with parameter roles and the dual-criterion activation logic. Figure~\ref{fig:logistic_fits} shows the fitted logistic curves for GLUE and SuperGLUE with the detected saturation dates marked.
