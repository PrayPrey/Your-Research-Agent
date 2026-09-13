---
title: "Phase 4 Validation Report: h-e1-v2"
hypothesis_id: h-e1-v2
phase: Phase4
date: "2026-08-31"
gate_result: FAILED
---

# Phase 4 Validation Report: h-e1-v2

## 1. Executive Summary

**Gate: FAILED** (1/3 proxies significant; threshold ≥2/3)

Hypothesis h-e1-v2 tests whether behavioral proxies show statistically significant Mann-Kendall trends over 2023-2024. Only Proxy 1 (prompt token count) passed at p < 0.05; Proxy 3 (correction frequency) failed; Proxy 2 (vote Shannon entropy) could not be computed due to LMSYS dataset access restrictions.

---

## 2. Experimental Setup

| Parameter | Value |
|-----------|-------|
| WildChat date range | 2023-01 to 2024-12 |
| Returning-user criterion | ≥3 distinct monthly bins |
| Min cohort size per bin | 50 unique IPs |
| Monthly bins obtained | 13 (Apr 2023 – Apr 2024) |
| Analysis cohort size | 27,902 returning users |
| Mann-Kendall method | Hamed-Rao (ACF lag-1 > 0.1 for all proxies) |
| Bootstrap CI | B=1000, seed=42 |

---

## 3. Proxy Results

### Proxy 1: Prompt Token Count (WildChat)
- **τ = 0.744**, p = 0.0005 → **SIGNIFICANT**
- Method: Hamed-Rao (ACF lag-1 = 0.634, high autocorrelation)
- 95% CI: [0.415, 0.972]
- Monthly mean: 180 tokens (Apr 2023) → 832 tokens (Apr 2024)
- Strong monotonic increase in prompt length over the cohort period.

### Proxy 2: Vote Shannon Entropy (LMSYS)
- **NOT COMPUTED** — LMSYS primary dataset (`lmsys/chatbot_arena_conversations`) is gated; fallback (`lmsys/lmsys-arena-human-preference-55k`) contains no timestamps
- τ = N/A, p = N/A → **NOT SIGNIFICANT** (marked as insufficient data)

### Proxy 3: Correction/Negation Frequency (WildChat)
- **τ = 0.051**, p = 0.855 → **not significant**
- Method: Hamed-Rao (ACF lag-1 = 0.168)
- 95% CI: [-0.441, 0.536]
- No detectable temporal trend in correction/negation patterns.

---

## 4. Gate Evaluation

| Proxy | τ | p | Significant |
|-------|---|---|-------------|
| prompt_tokens | 0.744 | 0.0005 | **YES** |
| vote_entropy | N/A | N/A | NO (no data) |
| correction_freq | 0.051 | 0.855 | NO |

**n_significant = 1 / 3** → Gate threshold (≥2) **NOT MET** → **GATE FAILED**

---

## 5. Figures Generated

- `figures/fig1_gate_summary.png` — τ ± 95% CI bar chart, PASS/FAIL color
- `figures/fig2_proxy_timeseries.png` — Monthly time series for Proxies 1 and 3
- `figures/fig3_cohort_funnel.png` — WildChat retention funnel

---

## 6. Key Findings

1. **Prompt length shows strong temporal trend** (τ=0.744): returning users compose progressively longer prompts over 2023-2024. This is a robust signal, but it may reflect selection bias in the returning-user cohort (power users who return tend to engage more deeply over time).

2. **Correction frequency shows no trend**: the regex-based proxy detects essentially zero temporal signal. Possible explanations: (a) base rate of explicit corrections is very low (~0.05%), making it noise-dominated; (b) the returning-user cohort changes behavior qualitatively, not in correction frequency.

3. **LMSYS data unavailable**: the gated dataset prevents Proxy 2 evaluation entirely. This is a critical blocking factor.

---

## 7. Failure Analysis

### Root Causes of Gate Failure

1. **Data access**: LMSYS primary is gated. Proxy 2 cannot be evaluated without requesting access or finding an alternative timestamped preference dataset.

2. **Proxy 3 signal strength**: correction/negation frequency is an extremely sparse signal (~0.05% of turns match). The Mann-Kendall test has no power over a near-zero series. The regex pattern (`no,.`, `actually,.`, etc.) may be too restrictive or may not capture the behavioral signal intended.

3. **13 bins vs. expected 24**: Only Apr 2023–Apr 2024 had sufficient cohort size (≥50 returning users). Pre-April 2023 data may not be present in WildChat-1M, and post-April 2024 data may be absent or sparse. Reduced time series reduces Mann-Kendall power.

---

## 8. Recommendations for v3

1. **LMSYS access**: request access to `lmsys/chatbot_arena_conversations` or identify an alternative preference dataset with timestamps (e.g., AlpacaEval, MT-Bench with dates).

2. **Proxy 3 redesign**: broaden correction regex to capture more implicit negation patterns, or replace with a different proxy (e.g., message revision rate, follow-up question rate).

3. **Cohort relaxation**: consider min_bins=2 to extend the time series; or use all WildChat users (not just returning) for Proxy 1 to get more months.

4. **Partial evidence**: Proxy 1 result (τ=0.744, p<0.001) is strong and consistent with the BAA hypothesis direction. A modified hypothesis focusing only on prompt length evolution may be testable.

---

## 9. Code Artifacts

| File | Description |
|------|-------------|
| `code/main.py` | Entry point, orchestration |
| `code/data_loader.py` | WildChat + LMSYS loading |
| `code/cohort_builder.py` | Returning-user cohort construction |
| `code/proxy_computer.py` | Proxy computations |
| `code/stats_tester.py` | Mann-Kendall + bootstrap CI |
| `code/visualizer.py` | Figure generation |
| `code/smoke_test.py` | Synthetic data validation (all PASS) |
| `results/wildchat_monthly.csv` | 13-bin monthly aggregate |
| `results/results.json` | Full statistical results |
