---
title: "PRD: Behavioral Proxy Trend Detection — h-e1-v2"
hypothesis_id: h-e1-v2
type: EXISTENCE
tier: LIGHT
stepsCompleted: ["phase2c", "phase3-prd"]
date: "2026-08-31"
author: "Anonymous"
---

# Product Requirements Document: h-e1-v2

## 1. Executive Summary

This PRD defines the implementation requirements for **h-e1-v2**: a behavioral proxy trend detection experiment that tests whether statistically significant temporal trends (Mann-Kendall τ ≠ 0) exist in three behavioral proxies computed from WildChat-1M and LMSYS Arena interaction logs over 2023-2024. This is a versioned retry of h-e1, using stricter returning-user cohorts (≥3 monthly appearances) and explicit LMSYS fallback handling.

**Gate:** MUST_WORK — ≥2/3 proxies must show p < 0.05 for the BAA framework pipeline to continue.

---

## 2. Problem Statement

Human behavioral adaptation to AI systems (the BAA hypothesis) requires empirical evidence of temporal trend in interaction metadata. h-e1 (v1) failed its gate, likely due to lenient cohort construction allowing transient users to dilute signal. h-e1-v2 refines the cohort filter and makes explicit the LMSYS Arena as a second independent data source for Proxy 2.

**Research Question:** Do behavioral proxies (prompt length, preference vote entropy, correction frequency) show monotonic temporal trends over 2023-2024 in real user-AI interaction logs?

---

## 3. Functional Requirements

### FR-1: WildChat-1M Data Pipeline
- Load `allenai/WildChat-1M` via HuggingFace `datasets` in streaming mode
- Filter: 2023-01 ≤ timestamp ≤ 2024-12; drop `toxic=True` conversations
- Construct returning-user cohort: retain `hashed_ip` values appearing in ≥3 distinct monthly bins
- Drop monthly bins with < 50 cohort members
- Output: monthly aggregate DataFrame with columns `[month, prompt_tokens_mean, correction_freq_mean, cohort_size]`

### FR-2: Proxy 1 — Prompt Token Count
- Tokenize `conversation[0]['content']` (first user turn) using `tiktoken` with `cl100k_base` encoding
- Parallelize tokenization with `multiprocessing.Pool(n_workers=4)`
- Aggregate: monthly mean prompt token count per cohort member
- Time series length: 24 monthly bins (Jan 2023 – Dec 2024)

### FR-3: LMSYS Arena Data Pipeline
- Load `lmsys/chatbot_arena_conversations` (primary); fallback to `lmsys/lmsys-arena-human-preference-55k` if unavailable
- Filter: 2023-01 ≤ tstamp ≤ 2024-12 (convert Unix timestamp to datetime)
- Normalize `winner`: map `"tie (bothbad)"` → `"tie"`
- Select top-5 model pairs by total vote count over 2023-2024
- Filter: retain only monthly bins with ≥100 votes per model pair
- Output: monthly DataFrame `[month, model_pair, win_count, lose_count, tie_count]`

### FR-4: Proxy 2 — Vote Shannon Entropy
- Compute H(win, lose, tie) = -Σ p_i log2(p_i) per (model_pair × monthly_bin)
- Aggregate entropy across model pairs per monthly bin (mean)
- Time series length: up to 24 bins; bins missing from LMSYS filtered at ≥100 votes floor
- Library: `scipy.stats.entropy` with `base=2`

### FR-5: Proxy 3 — Correction/Negation Frequency
- Regex pattern: `r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'` (case-insensitive)
- Apply to ALL turns (not just first) of each conversation
- Normalize: count of matching turns / total turn count per conversation
- Aggregate: monthly mean correction_freq across cohort members
- Validate regex construct on 100-sample manual inspection (log agreement rate)

### FR-6: Mann-Kendall Trend Test
- Apply Mann-Kendall τ test to each of the 3 proxy time series
- Primary: `scipy.stats.kendalltau(time_idx, proxy_series)`
- Fallback: `pymannkendall.hamed_rao_modification_test()` if lag-1 autocorrelation ACF > 0.1
- Significance threshold: p < 0.05 (uncorrected); gate requires ≥2/3 proxies
- Compute 95% bootstrap CI for τ (B=1000 bootstrap samples, seed=42)

### FR-7: Gate Evaluation
- Count proxies with p < 0.05 AND |τ| > 0.0 as significant
- Gate passed: n_significant ≥ 2
- Output gate result in `results.json` and summary printed to stdout

### FR-8: Visualization
- **Figure 1 (Required):** 3-panel bar chart of τ values ± 95% CI; p-value annotations; dashed τ=0 line; PASS (green)/FAIL (red) color coding
- **Figure 2:** 3-panel time series of monthly means ± 95% CI for all 3 proxies; Mann-Kendall trend line overlay
- **Figure 3:** Cohort retention funnel (total WildChat → ≥1 monthly → ≥3 monthly → analysis cohort)
- **Figure 4:** LMSYS stacked bar chart of win/lose/tie proportions per monthly bin; entropy overlay
- Save all figures to `docs/youra_research/h-e1-v2/figures/`

---

## 4. Data Specification

### Dataset 1: WildChat-1M
- **HuggingFace ID:** `allenai/WildChat-1M`
- **Size:** ~1M conversations
- **Loading:** `load_dataset("allenai/WildChat-1M", streaming=True)`
- **Key fields:** `hashed_ip`, `model`, `timestamp`, `conversation` (list of dicts with `role`/`content`), `toxic`
- **Manual download:** No (auto-download via HuggingFace datasets)
- **Temporal coverage:** 2023-2024 (ISO timestamp string)

### Dataset 2: LMSYS Arena
- **HuggingFace ID (primary):** `lmsys/chatbot_arena_conversations`
- **HuggingFace ID (fallback):** `lmsys/lmsys-arena-human-preference-55k`
- **Loading:** `load_dataset("lmsys/chatbot_arena_conversations")`
- **Key fields:** `model_a`, `model_b`, `winner`, `tstamp`
- **Manual download:** No (auto-download via HuggingFace datasets)
- **Size:** ~55K rows

**Note:** Both datasets auto-download via HuggingFace `datasets` library. No manual download tasks required.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- WildChat streaming mode (memory-efficient for ~1M conversations)
- Multiprocessing tokenization: `n_workers=4`
- Estimated runtime: 2-4 hours on CPU (WildChat streaming + tokenization)

### NFR-2: Reproducibility
- Random seed: `np.random.seed(42)` for bootstrap CI
- All intermediate aggregates saved to `results/` as CSV
- All results serialized to `results.json`

### NFR-3: Correctness
- Regex construct validity: manual inspection on 100-sample (agreement rate logged)
- Autocorrelation check: compute ACF(lag-1) for each proxy; switch to Hamed-Rao if > 0.1
- LMSYS vote normalization: verify "tie (bothbad)" → "tie" mapping

### NFR-4: Infrastructure (LIGHT tier)
- Configuration via command-line argparse (no YAML config required)
- Logging: print statements + CSV output (no WandB required)
- Testing: smoke test only (not full unit test suite)

---

## 6. Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Gate passed | ≥2/3 proxies p < 0.05 | MUST (gate) |
| Code runs without error | Zero runtime errors | MUST |
| Effect size | \|τ\| > 0.2 for significant proxies | SHOULD |
| All 4 figures generated | Saved to figures/ | SHOULD |
| Results serialized | results.json exists | MUST |

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
pandas>=2.0.0
scipy>=1.11.0
numpy>=1.24.0
tiktoken>=0.5.0
tqdm>=4.65.0
pymannkendall>=1.4.3
matplotlib>=3.7.0
seaborn>=0.12.0
multiprocess>=0.70.15
```

### 7.2 External Repositories (Reference Only)
- `allenai/WildChat` — field structure reference
- `lm-sys/FastChat` — LMSYS Arena vote normalization reference
- `mmhs013/pymannkendall` — autocorrelation-robust Mann-Kendall variants

---

## 8. Out of Scope

- Model training or fine-tuning
- Real-time or online data processing
- Production deployment
- Cross-platform support beyond Linux/CPU
- Bonferroni correction (gate uses uncorrected p < 0.05 for ≥2/3 PoC)

---

## 9. Assumptions and Constraints

- **A1:** IP-hash cohort tracking is approximate (NAT multi-user collisions acknowledged)
- **A2:** Monthly bin granularity (24 bins) is sufficient for Mann-Kendall power
- **A3:** WildChat-1M HuggingFace access available in execution environment
- **A4:** CPU-only execution (no GPU required)
- **Constraint:** Total implementation tasks ≤ 15 (LIGHT tier)
