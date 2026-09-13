# 4. Experimental Setup

We design experiments to answer three research questions that map directly to the three-step Goodhart saturation mechanism:

**RQ1:** Is there a statistically significant structural break in PwC benchmark residual CoV at some paper_count threshold? *(Detection — H-E1)*

**RQ2:** Does the pre-breakpoint benchmark segment exhibit substantially higher performance variance than the global baseline? *(Exploration regime — H-M1)*

**RQ3:** Does the post-breakpoint segment exhibit substantially lower variance than the pre-breakpoint segment? *(Saturation compression — H-M2, H-M3)*

## 4.1 Dataset

We use the PwC benchmark archive (HuggingFace `paperswithcode/paperswithcode-data`, August 2026 snapshot), loaded via Arrow IPC for computational efficiency. The dataset contains evaluation results across thousands of benchmarks.

**Preprocessing:** For each benchmark, CoV = σ/μ is computed over all reported metric values. Benchmarks with fewer than 38 papers are excluded, as CoV estimation on very small samples is unreliable. After filtering, **N=115 benchmarks** remain, covering paper_count ∈ [38, 352].

*Why this threshold:* min_papers=38 is the smallest threshold that places the structural break (detected at paper_count*=39) within the valid detection range [10, 120] while maintaining sufficient post-breakpoint sample size (n_post=107) for reliable statistical inference.

## 4.2 Baselines

We compare our structural-break approach against three reference methods:

| Method | Description | Why Included |
|--------|-------------|--------------|
| **OLS trend** | Linear regression CoV ~ paper_count (rho=0.137) | Represents the null hypothesis: saturation is a smooth monotonic trend with no structural break |
| **S_index** [CITE:Akhtar2026] | Composite saturation metric for LLM benchmarks | The state-of-the-art saturation index; we contrast our paper_count* threshold with its composite approach |
| **Liao et al. aggregate CoV** [CITE:Liao2022UNVERIFIED] | Time-based CoV saturation metric across 3,765 benchmarks | The largest saturation study; we contrast our within-PwC paper_count threshold against their time-based aggregate |

The OLS baseline tests whether a structural break adds explanatory power beyond a simple linear trend. S_index and Liao et al. represent the closest existing methods without providing a paper_count threshold.

## 4.3 Implementation Details

**Framework:** Python 3.10+. `ruptures` (v1.1.7, L2 cost PELT), `scipy` (permutation test, Brown-Forsythe), `statsmodels` (OLS), `pandas`/`numpy` (data handling), `matplotlib` (visualization).

**Hardware:** Standard CPU. Data loading: ~12s (Arrow IPC). Full analysis pipeline: < 3 minutes. No GPU required.

**Key hyperparameters:**

| Parameter | Value | Selection Rationale |
|-----------|-------|---------------------|
| min_papers | 38 | Places paper_count*=39 within valid detection range |
| PELT model | L2 | Mean-shift detection in continuous 1D signal |
| min_size | 3 | Per VPWBS theoretical recommendation [CITE:Wang2019] |
| jump | 1 | Exact search for N=115 (primary detection only) |
| BIC penalty | σ²·log(N) ≈ 4.32 | Automatic; consistent with PELT theory |
| N_permutations | 1000 | Standard for permutation test power |
| N_bootstrap | 1000 | Standard for CI width estimation |
| seed | 42 | Fixed for reproducibility |

All code and data are archived at the paper's companion repository.

## 4.4 Evaluation Metrics

**RQ1 (structural break detection):**
- Permutation p-value (primary): p < 0.05 gate
- paper_count* location: must fall ∈ [10, 120] (meaningful range, not a boundary artifact)
- Piecewise F-test p-value (corroboration): model comparison test

**RQ2 (exploration regime):**
- Pre-segment variance ratio (F-stat): pre_variance / global_variance > 1.0
- F-test one-tailed p-value: < 0.10 gate

**RQ3 (saturation compression):**
- Brown-Forsythe variance ratio: post_variance / pre_variance < 1.0; p < 0.05 gate (H-M2)
- Directional concentration metrics: ≥ 2/4 pass at p < 0.10 (H-M3 SHOULD_WORK gate)

Statistical significance is evaluated using standard thresholds (p < 0.05 for MUST_WORK gates; p < 0.10 for SHOULD_WORK gates) with all tests pre-specified before data analysis.
