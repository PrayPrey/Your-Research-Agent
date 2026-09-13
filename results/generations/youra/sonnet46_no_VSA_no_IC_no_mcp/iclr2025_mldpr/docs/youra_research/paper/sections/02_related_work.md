# Related Work

Our work sits at the intersection of three research threads: empirical studies of benchmark overfitting and saturation, qualitative critiques of ML evaluation practices, and the application of mathematical growth models to characterize technological progress. We survey each thread, identifying the limitations that motivate our automated logistic detection approach.

## Benchmark Overfitting and Generalization Gaps

The most direct precedent for our work is \citet{recht2019imagenet}, who collected a new independent test set (ImageNet-v2) and demonstrated an 11–14 percentage point accuracy gap between the original ImageNet test set and the new collection. This established empirically that models trained and evaluated on the same benchmark overfit to benchmark-specific features. \citet{engstrom2020identifying} and related work extended this cross-sectional approach to other vision benchmarks.

The cross-sectional approach is rigorous but fundamentally limited for our purposes: it requires collecting a new independent test set for each benchmark, making it resource-intensive, domain-specific, and impossible to apply retrospectively at scale. The approach also measures the *magnitude* of overfitting at a single point in time, not the *temporal dynamics* through which overfitting accumulates.

\citet{chen2021evaluating} and \citet{gururangan2018annotation} examined dataset artifacts and hypothesis-only baselines as alternative signals of benchmark exploitation, focusing on static structural properties rather than temporal progression. \citet{ethayarajh2020utility} proposed a utility measure for benchmarks but did not address temporal saturation detection.

In contrast, our approach requires only the historical leaderboard timeseries already available in Papers With Code — no new data collection, no domain-specific test set construction. The temporal signal (score-over-time) is always present and always free to access.

## Qualitative Saturation Discourse and Goodhart's Law

A substantial body of work discusses benchmark saturation qualitatively. \citet{wang2019superglue} explicitly motivated SuperGLUE by GLUE's saturation within one year. \citet{srivastava2022bigbench} similarly motivated BIG-bench by SuperGLUE's saturation. Both papers acknowledge the saturation event as a community judgment rather than providing a formal detection criterion.

\citet{goodhart1975problems}'s observation — ``when a measure becomes a target, it ceases to be a good measure'' — provides the theoretical framing for why benchmarks saturate: once models are explicitly optimized against a fixed test set, benchmark-specific features are incrementally exploited until genuine capability signal is exhausted. \citet{manheim2019categorizing} operationalizes Goodhart's Law in the ML context. However, neither work provides a quantitative temporal characterization of how benchmark-specific optimization accumulates.

\citet{bender2021stochastic} and \citet{birhane2021misogyny} offer qualitative critiques of benchmark over-reliance but without automated detection machinery. \citet{kapoor2023leakage} documents leakage and reproducibility failures in ML benchmarking, further motivating the need for automated monitoring infrastructure.

The gap in this thread is the absence of a formal, reproducible measurement procedure. We address this by operationalizing the saturation concept as an AIC model comparison test — transforming qualitative community judgment into a statistically principled criterion.

## Growth Models for Technological Progress

Logistic growth models have a long history in modeling processes with initial rapid growth followed by a carrying-capacity asymptote: population dynamics \citep{verhulst1838notice}, technology adoption curves \citep{bass1969new_product}, and epidemiological spread. The logistic function K/(1 + exp(−r(t−t₀))) cleanly captures the three-phase dynamics (rapid growth → inflection → plateau) that characterize these processes.

In the ML context, \citet{rosenfeld2020constructive} and \citet{kaplan2020scaling} studied power-law scaling of model performance with compute and data, but focused on aggregate trends rather than per-benchmark temporal saturation. \citet{owen2019hyperparameter} studied performance curves during training, but not across leaderboard time.

We are not aware of prior work applying logistic growth models to benchmark leaderboard timeseries for saturation detection. The closest conceptually is the Bass diffusion model in technology adoption \citep{bass1969new_product}, which also uses logistic-family dynamics to model adoption curves — but applied to market penetration, not scientific benchmark performance.

The standard model comparison framework we employ — Akaike Information Criterion (AIC) with the Burnham \& Anderson \citeyearpar{burnham2002model} interpretation (ΔAIC > 4 as substantial evidence, ΔAIC > 10 as decisive) — is well-established in ecology and statistics. We transfer this framework to benchmark dynamics, where it provides an information-theoretic foundation absent from prior benchmark evaluation work.

## Positioning

Our work occupies a unique intersection: (1) longitudinal (temporal) rather than cross-sectional analysis of benchmark exploitation; (2) automated and benchmark-agnostic rather than requiring domain-specific new test sets; (3) formal information-theoretic validation of the growth model rather than qualitative discussion. The three prior threads each address one or two of these requirements; our contribution addresses all three simultaneously, using only existing public leaderboard data.
