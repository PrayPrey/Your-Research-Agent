# Experimental Setup

We design experiments to answer three research questions that map directly to the BAA detectability claims:

**RQ1:** Does prompt complexity in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024? (Proxy 1 — prompt token count)

**RQ2:** Does preference vote entropy in LMSYS Chatbot Arena show a statistically significant trend over 2023–2024? (Proxy 2 — vote Shannon entropy)

**RQ3:** Does correction/negation frequency in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024? (Proxy 3 — correction frequency)

For BAA existence to be confirmed, ≥2 of 3 proxies must satisfy |τ| ≥ 0.2 with p < 0.05 (Mann-Kendall, Hamed-Rao corrected where ACF lag-1 > 0.1). This gate criterion is pre-specified; direction is analyzed post-hoc.

## Datasets

**WildChat-1M** (`allenai/WildChat-1M`; Zhao et al., 2024). Approximately 1 million ChatGPT conversation logs collected via a free-access proxy service, with timestamps, IP-hash pseudonymization, topic tags, and toxicity flags. We restrict to non-toxic English conversations from January 2023 – December 2024. WildChat-1M is publicly available without access gating, enabling full reproducibility.

**LMSYS Chatbot Arena** (Zheng et al., 2023). The primary dataset (`lmsys/chatbot_arena_conversations`) provides timestamped human preference votes across AI model pairs. We attempted to load this dataset for Proxy 2 computation; it requires approved research access on HuggingFace and is unavailable without credentials. The publicly available fallback (`lmsys/lmsys-arena-human-preference-55k`) contains 55,000 preference records but no `tstamp` field, making temporal binning impossible.

| Dataset | Records | Time Range | Access | Use |
|---------|---------|------------|--------|-----|
| WildChat-1M | ~1M conversations | 2023-01 to 2024-12 | Public | Proxies 1, 3 |
| LMSYS Arena (primary) | ~1M votes | 2023-2024 | Gated | Proxy 2 (blocked) |
| LMSYS Arena (fallback) | 55K records | N/A (no timestamps) | Public | Not usable |

## Baselines

This study tests BAA existence (detection), not model comparison. The statistical baseline is the null hypothesis H₀: τ = 0 for each proxy (no monotonic temporal trend). We do not compare against prior behavioral trend detection methods because, to our knowledge, no prior work has applied Mann-Kendall trend analysis to returning-user behavioral proxies in AI interaction logs. The h-e1 (version 1) result serves as an internal replication baseline:

**h-e1 (internal replication).** The same pipeline with a less strict cohort filter (monthly bin minimum not enforced). h-e1 produced τ = +0.564 (p = 0.007) for prompt tokens and non-significant results for correction frequency. h-e1-v2 provides a more rigorous replication with the Hamed-Rao autocorrelation correction and a stricter bin-size floor.

## Implementation Details

The analysis pipeline is implemented in Python 3.10 using seven modules (see Section 3 for architecture). Key hyperparameters:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| min_bins | 3 | Minimum monthly appearances per user for longitudinal tracking |
| min_cohort_size | 50 users/bin | Stabilize monthly mean estimates |
| date_start | 2023-01 | WildChat coverage start |
| date_end | 2024-12 | WildChat coverage end |
| tokenizer | tiktoken cl100k_base | Matches GPT-3.5/GPT-4 tokenization |
| n_workers | 4 | Multiprocessing for tokenization |
| Bootstrap B | 1000 | Bootstrap CI replications |
| Bootstrap seed | 42 | Reproducibility |
| ACF threshold | 0.1 | Switch from standard to Hamed-Rao Mann-Kendall |
| α | 0.05 | Significance threshold |
| min_votes | 100 | LMSYS minimum votes per monthly bin per model pair |

The analysis window yields 13 monthly bins (April 2023 – April 2024) after the ≥50 users/bin filter, reflecting WildChat data density in the returning-user cohort.

## Evaluation Metrics

**Mann-Kendall τ.** Non-parametric rank correlation between time index and proxy value; τ ∈ [−1, 1], where τ < 0 indicates a monotonic decreasing trend and τ > 0 indicates monotonic increase. Chosen for robustness to non-normality and outliers, which are expected in interaction log aggregates.

**p-value (two-sided).** Significance of the trend against H₀: τ = 0. We use the Hamed-Rao modification when ACF lag-1 > 0.1 to correct for autocorrelation-inflated false positive rates.

**Bootstrap 95% CI for τ.** Resampling from the monthly time series (B = 1000, seed = 42) provides a non-parametric confidence interval for the trend magnitude.

**Gate pass criterion.** ≥2 of 3 proxies: |τ| ≥ 0.2 and p < 0.05. The directional BAA prediction (τ < 0 for all proxies) is evaluated post-hoc; the gate tests existence only.
