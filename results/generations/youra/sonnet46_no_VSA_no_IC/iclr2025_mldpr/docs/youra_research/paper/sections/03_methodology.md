# 3. Methodology

## 3.1 Overview

Our methodology follows directly from the key insight: benchmark saturation is a structural break, not a monotonic trend. This guides a three-stage pipeline — (1) remove the global trend, (2) detect the structural break in the residuals, and (3) validate the break with independent tests. Figure 8 shows the regime separation in a scatter plot of N=115 benchmarks; Figure 9 shows the PELT penalty sensitivity confirming a single robust breakpoint across a wide penalty range.

The full pipeline is:

```
(i)  Data ingestion: PwC leaderboard → N=115 benchmarks with CoV and paper_count
(ii) OLS detrending: residual_CoV = CoV - (slope × paper_count + intercept)
(iii) PELT detection: structural break at paper_count* from residual CoV series
(iv) Validation: permutation test (p < 0.05) + piecewise F-test (model comparison)
(v)  Regime characterization: F-test (pre-segment vs. global) + Brown-Forsythe (pre vs. post)
```

**Rationale:** Without detrending, PELT would detect the known global CoV-paper_count correlation (rho direction is dataset-sensitive; see Section 5.3) as a spurious change-point. Detrending isolates the structural break component from the linear trend component, making the detection robust to the global trend's direction and magnitude.

## 3.2 Data

We use the PwC benchmark archive (HuggingFace `paperswithcode/paperswithcode-data`, Aug 2026 snapshot) accessed via Arrow IPC. For each benchmark, coefficient of variation is computed as:

$$\text{CoV}_b = \frac{\sigma_b}{\mu_b}$$

where σ_b and μ_b are the standard deviation and mean of all result metric values for benchmark b. Benchmarks with fewer than 38 papers are excluded (min_papers=38) to ensure reliable CoV estimation, yielding N=115 benchmarks with paper_count ∈ [38, 352].

## 3.3 OLS Detrending

**Rationale:** The global CoV-paper_count relationship confounds change-point detection. We remove it via OLS:

$$\text{residual\_CoV}_b = \text{CoV}_b - (\hat{\beta}_0 + \hat{\beta}_1 \cdot \text{paper\_count}_b)$$

The OLS slope and intercept are estimated on all N=115 benchmarks. Residuals are sorted by paper_count before PELT application. This design removes whatever linear trend exists (positive or negative) without assuming its direction, ensuring the structural break detection is trend-agnostic.

## 3.4 PELT Change-Point Detection

**Rationale:** We use PELT (Pruned Exact Linear Time) [CITE:Killick2012UNVERIFIED] with an L2 cost function to detect a structural break in the residual CoV series. L2 cost is appropriate for detecting mean shifts in a continuous 1D signal. We apply a BIC-based penalty to select the number of breakpoints:

$$\text{pen} = \hat{\sigma}^2 \cdot \log(N)$$

**Penalty sensitivity:** We sweep penalties across [1, 50] on a log scale (20 values) and confirm that the number of detected breakpoints is 1 across the relevant penalty range (see Figure 9). The BIC-selected penalty consistently yields exactly one structural break.

**Key parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| model | L2 | Mean-shift detection in continuous 1D signal |
| min_size | 3 | Minimum segment size per VPWBS recommendations [CITE:Wang2019] |
| jump | 1 | Exact search (no subsampling) for N=115 |
| pen_range | [1, 50] | Sensitivity sweep; BIC within range |
| N_permutations | 1000 | Standard for permutation test power |
| N_bootstrap | 1000 | Standard for CI estimation |

## 3.5 Statistical Validation

Two independent validation tests confirm the detected structural break:

**Permutation test (primary):** The paper_count labels are shuffled 1000 times; PELT is rerun on each permuted series. The permutation p-value is the fraction of permutations where the detected breakpoint index ≤ the observed breakpoint index. This directly tests whether the observed breakpoint position is consistent with random noise under the null hypothesis (no structural break).

**Piecewise F-test (corroboration):** We compare a two-segment linear model (fitted separately on pre- and post-breakpoint segments) to a single linear model on the full series using an F-test. A significant F-test confirms that the two-segment model explains substantially more variance, providing a model-comparison-based corroboration independent of the permutation approach.

The gate requires: permutation p < 0.05 AND paper_count* ∈ [10, 120].

## 3.6 Regime Characterization

After detecting paper_count* = 39 (breakpoint_idx = 8 in the sorted N=115 series), we characterize the two regimes:

**H-M1 (exploration regime):** Levene/F-test comparing pre-breakpoint segment variance (n_pre=8) to global variance. Confirms that pre-segment exhibits significantly higher variance than the population.

**H-M2 (saturation regime):** Brown-Forsythe test comparing pre-breakpoint variance to post-breakpoint variance. Confirms that post-segment exhibits significantly lower variance than pre-segment.

**H-M3 (directional concentration):** Four directional metrics on the pre-vs-post comparison: (M1) skewness direction, (M2) 10th percentile comparison, (M3) permutation test on skewness difference, (M4) Mann-Whitney rank dominance test. Gate: ≥ 2/4 metrics pass at p < 0.10.

## 3.7 Implementation

All code is implemented in Python with `ruptures` (PELT), `scipy` (permutation test, Brown-Forsythe), and `statsmodels` (OLS). Data loading uses Arrow IPC via HuggingFace datasets library. The pipeline is fully automated: `run_experiment.py` ingests data, runs all analyses, generates figures, and writes `experiment_results.json`. All hyperparameters are centralized in `config.py` for reproducibility.
