# Methodology

The BAA detectability question requires measuring temporal trends in human behavioral engagement signals across a population of users whose AI interaction history spans multiple time points. This section explains the design decisions — each of which follows from a specific constraint or insight about what makes behavioral signals detectable in naturalistic interaction data.

## Dataset Selection

**WildChat-1M** (Zhao et al., 2024; `allenai/WildChat-1M` on HuggingFace) is the primary data source. It provides approximately 1 million ChatGPT conversation logs collected via a free-access proxy, with timestamps, hashed IP addresses, topic tags, toxicity flags, and full conversation text. The IP-hash pseudonymization allows approximate user-level longitudinal tracking without IRB-sensitive individual identification. We restrict to non-toxic English conversations (`toxic=False`) and the date range January 2023 – December 2024.

**LMSYS Chatbot Arena** was the intended source for Proxy 2 (vote entropy). The primary dataset (`lmsys/chatbot_arena_conversations`) requires approved research access on HuggingFace. The publicly available fallback (`lmsys/lmsys-arena-human-preference-55k`) contains no `tstamp` field, making temporal binning impossible. We use the fallback solely to document this infrastructure constraint; no vote entropy results are reported.

## Returning-User Cohort Construction

The key design choice — and the source of the paper's central limitation — is the returning-user filter. A user (IP-hash) is included in the analysis cohort if they appear in **≥3 distinct calendar months** within the analysis window. This filter serves two purposes: (1) it ensures sufficient within-user longitudinal data for trend detection, and (2) it filters out transient or one-time users whose single-session data cannot support intra-user behavioral change analysis.

The trade-off is selection: the ≥3 bin filter retains n = 27,902 users from the full WildChat population (Figure 3), systematically selecting for high-engagement users. The cohort construction pipeline proceeds as:

1. Stream WildChat-1M and extract per-user, per-month records.
2. For each user, count distinct months with ≥1 conversation; retain users with ≥3 such months.
3. For each retained user-month, compute per-turn proxy values.
4. Aggregate to monthly cohort means: one data point per calendar month per proxy.
5. Filter to monthly bins with ≥50 cohort members (to stabilize estimates); the analysis window yields 13 bins (April 2023 – April 2024).

Monthly bin sizes vary due to platform growth; minimum bin size is enforced at 50 users per month. The final analysis cohort has 13 monthly bins.

## Behavioral Proxy Computation

We operationalize three behavioral proxy signals, each measuring a distinct dimension of engagement:

**Proxy 1: Prompt Token Count.** For each user-turn (first turn of each conversation), tokenize the prompt using `tiktoken cl100k_base` (matching GPT-3.5/GPT-4 tokenization). Compute monthly mean prompt token count across all retained users. A declining trend (τ < 0) would be consistent with BAA disengagement (shorter prompts = reduced elaboration). This proxy is reliable because token count is directly computable from conversation text with no annotation requirement.

**Proxy 2: Preference Vote Shannon Entropy.** For each LMSYS monthly bin, compute H = −Σ pᵢ log₂ pᵢ over the win/lose/tie distribution of human preference votes. A declining entropy trend would indicate votes becoming more decisive/homogeneous — consistent with reduced discriminativeness. This proxy is **not computed** due to LMSYS primary dataset access restriction.

**Proxy 3: Correction/Negation Frequency.** For each user-turn, apply a regex pattern matching explicit verbal corrections: `r'\b(no[,.] |actually[,.] |that\'s wrong|please redo|i meant|wrong[,.] )\b'` (case-insensitive). Compute monthly mean correction frequency as the fraction of turns matching the pattern. A declining trend would be consistent with reduced willingness to explicitly correct AI errors.

## Statistical Testing

Monthly time series exhibit temporal autocorrelation that violates the independence assumption of the standard Mann-Kendall test. We diagnose autocorrelation via lag-1 ACF: if ACF lag-1 > 0.1, we apply the **Hamed-Rao modification** (Hamed & Rao, 1998), which adjusts the variance of the Mann-Kendall statistic for autocorrelated series using a data-adaptive correction factor. This correction is critical for Proxy 1, where ACF lag-1 = 0.634.

The test procedure:
1. Compute ACF lag-1 for the monthly time series.
2. If ACF lag-1 ≤ 0.1: apply standard Mann-Kendall (`scipy.stats.kendalltau`).
3. If ACF lag-1 > 0.1: apply Hamed-Rao modification (`pymannkendall.hamed_rao_modification_test`).
4. Report τ ∈ [−1, 1], two-sided p-value, and significance at α = 0.05.
5. Bootstrap 95% confidence intervals for τ (B = 1000 resamples, seed = 42).

**Gate criterion:** ≥2 of 3 proxies must show |τ| ≥ 0.2 with p < 0.05 for the BAA existence gate to pass and the pipeline to advance to causal mechanism testing. The direction (positive vs. negative τ) is analyzed post-hoc.

## Gate Evaluation and Error Rates

We pre-specify α = 0.05 as the significance threshold. With 3 independent tests and a gate requiring ≥2 significant, the family-wise false positive rate under H₀ (all τ = 0) is bounded above by 3α² − 2α³ ≈ 0.007 for independent tests — well below 0.05. We do not apply multiple testing correction beyond the gate criterion, as the proxies are not treated as independent confirmations of a single claim but as triangulating measures of distinct behavioral dimensions.

## Implementation

The analysis pipeline is implemented in Python as seven modules:

- `data_loader.py`: WildChat streaming (HuggingFace `datasets`) and LMSYS loading with fallback.
- `cohort_builder.py`: Returning-user filter, monthly aggregation, multiprocessing tokenization.
- `proxy_computer.py`: tiktoken tokenization (Proxy 1), Shannon entropy (Proxy 2), regex correction detection (Proxy 3).
- `stats_tester.py`: ACF diagnosis, Mann-Kendall variant selection, bootstrap CI, gate evaluation.
- `visualizer.py`: Figure generation (gate summary, proxy time series, cohort funnel, LMSYS votes).
- `main.py`: CLI entry point with full argument configuration.
- `smoke_test.py`: Synthetic data validation (increasing series → τ > 0 with p < 0.05; flat series → gate fails).

The complete implementation is available at [anonymous repository link].

## Reproducibility

All random operations use seed = 42. The WildChat-1M dataset is publicly available on HuggingFace without gating. The analysis window (April 2023 – April 2024) is determined by the ≥50 users/month filter applied to the ≥3 monthly bin cohort. Results are deterministic given the seed.
