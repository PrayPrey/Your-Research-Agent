# Product Requirements Document: H-E1
# Behavioral Proxy Signal Detection in Human-AI Interaction Logs

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)  
**Date:** 2026-08-31  
**Author:** Anonymous  
**Phase 2C Source:** 02c_experiment_brief.md  
**Tier:** LIGHT (≤15 tasks)

---

## 1. Executive Summary

Detect whether statistically significant monotonic trends exist in behavioral proxy signals computed from WildChat-1M and LMSYS Chatbot Arena interaction logs (2023-2024). Success (≥2 of 3 proxies with Mann-Kendall τ ≠ 0, p < 0.05) validates that behavioral engagement signals are detectable — a prerequisite for the YOURA behavioral alignment assessment (BAA) framework.

---

## 2. Problem Statement

The YOURA hypothesis chain requires evidence that user behavioral proxies in real interaction logs carry temporal signal reflecting model quality evolution. Without detectable signal, downstream alignment measurement (H-M1, H-M2, H-M3) has no empirical foundation.

**Null hypothesis (H0):** All proxy time series are stationary (τ ≈ 0) over 2023-2024.  
**Alternative (H-E1):** ≥2 of 3 proxies show monotonic trend (τ ≠ 0, p < 0.05).

---

## 3. Functional Requirements

### FR-1: WildChat-1M Data Loading and Filtering
- Load `allenai/WildChat-1M` via HuggingFace `datasets` library
- Filter to timestamp range 2023-01-01 through 2024-12-31
- Extract fields: `conversation[0].content` (first turn = prompt), `timestamp`, `model`, `hashed_ip`
- Assign `monthly_bin` = YYYY-MM from timestamp

### FR-2: WildChat Cohort Construction
- Group interactions by `hashed_ip`
- Retain only IP-hashes appearing in ≥3 distinct monthly bins within 2023-2024
- Output: cohort DataFrame with columns [monthly_bin, hashed_ip, prompt_token_count, correction_freq]

### FR-3: Proxy 1 — Prompt Token Count Computation
- Compute `prompt_token_count` per interaction: `len(prompt.split()) × 1.3` (word-piece approximation)
- Aggregate: monthly mean per cohort bin
- Output: time series `token_series[monthly_bin → mean_token_count]`

### FR-4: Proxy 3 — Correction/Negation Frequency Computation
- For each session, count turns containing correction markers: ["actually", "that's wrong", "no, I meant", "please redo", "that is incorrect", "you're wrong"]
- Normalize by `turn_count` per session
- Aggregate: monthly mean `correction_freq` per cohort bin
- Output: time series `correction_series[monthly_bin → mean_correction_freq]`

### FR-5: LMSYS Chatbot Arena Data Loading and Filtering
- Load `lmsys/chatbot_arena_conversations` via HuggingFace `datasets`
- Filter to timestamp range 2023-01 through 2024-12 from `tstamp`
- Extract fields: `model_a`, `model_b`, `winner`, `tstamp`
- Assign `monthly_bin` = YYYY-MM from tstamp
- Select top-5 models by vote count
- Filter to model pairs with ≥100 votes per monthly bin

### FR-6: Proxy 2 — Shannon Entropy Computation
- Per monthly bin: compute win/lose/tie counts per model pair
- Compute Shannon entropy: `entropy([p_win, p_lose, p_tie], base=2)` via `scipy.stats.entropy`
- Aggregate: mean entropy per monthly bin across top-5 model pairs
- Output: time series `entropy_series[monthly_bin → mean_entropy]`

### FR-7: Mann-Kendall Trend Tests
- Run `scipy.stats.kendalltau(time_index, proxy_series)` for all 3 proxies
- Compute: τ (Kendall's tau), p-value (two-sided, H0: τ=0), |τ| effect size
- Output: results dict `{proxy_name: (tau, p_value)}`

### FR-8: Success Evaluation
- Count proxies with p < 0.05 (τ ≠ 0)
- Pass condition: ≥2 of 3 proxies pass
- Secondary condition: |τ| > 0.2 for ≥1 proxy
- Output: pass/fail verdict with per-proxy breakdown

### FR-9: Visualization Generation
- **Required figure:** Bar chart of τ values for all 3 proxies; significance markers (p<0.05 highlighted); horizontal τ=0 line
- **Additional figures:**
  - Time series plots: monthly mean per proxy overlaid with trend line (2023-2024)
  - P-value heatmap: 3 proxies × 2 datasets
  - Cohort size histogram: WildChat IP-hash cohort sizes (validate ≥3 bin filter)
  - LMSYS vote count per bin (validate ≥100 votes/bin filter)
- Save all figures to `h-e1/figures/`

### FR-10: Results Reporting
- Print per-proxy results: proxy name, τ, p-value, |τ|, pass/fail
- Print overall verdict: PASS / FAIL with count
- Save results to `h-e1/results/results.json`

---

## 4. Data Specification

| Dataset | Identifier | Load Method | Split | Est. Sample Size | Manual Download? |
|---------|-----------|-------------|-------|------------------|-----------------|
| WildChat-1M | `allenai/WildChat-1M` | HuggingFace datasets | Full → filter 2023-2024 | 50K-200K qualifying interactions from ~5K-20K cohort IP-hashes | No (auto) |
| LMSYS Arena | `lmsys/chatbot_arena_conversations` | HuggingFace datasets | Full → filter 2023-2024 | 300K-600K pairwise comparisons; top-5 models | No (auto) |

No data augmentation — real behavioral data; augmentation corrupts validity.

---

## 5. Non-Functional Requirements

- **Reproducibility:** Fixed seed 42 for any bootstrap resampling
- **Hardware:** CPU-only (no GPU required)
- **Language:** Python 3.10+
- **Performance:** Full dataset processing must complete in <2 hours on standard research hardware
- **Caching:** Cache HuggingFace datasets to disk to avoid re-download

---

## 6. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Proxies with p < 0.05 | ≥2 of 3 | PRIMARY (gate condition) |
| Effect size |τ| > 0.2 | ≥1 proxy | SECONDARY |
| Code runs without error | Required | REQUIRED |
| All 4 figures generated | Required | REQUIRED |

Gate: MUST_WORK — failure blocks entire pipeline.

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.14.0
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
```

### 7.2 External Repositories (Reference Only)

| Repository | Purpose | URL |
|-----------|---------|-----|
| allenai/WildChat-1M | Official dataset | https://huggingface.co/datasets/allenai/WildChat-1M |
| lmsys/chatbot_arena_conversations | Official dataset | https://huggingface.co/datasets/lmsys/chatbot_arena_conversations |

---

## 8. Out of Scope

- Neural model training or fine-tuning
- GPU/CUDA usage
- Real-time inference
- Comparison with deep learning baselines
- Dataset augmentation

---

## 9. Assumptions and Risks

| Assumption/Risk | Mitigation |
|----------------|-----------|
| WildChat IP-hash approximates user identity | Require ≥3 monthly appearances to reduce noise |
| LMSYS vote sparsity | Filter to ≥100 votes per model pair per monthly bin |
| Token count decline may reflect expertise gain not engagement loss | Composite of 3 proxies required; direction flexible (p < 0.05 either direction) |
| HuggingFace datasets access required | Fallback: direct CSV/JSONL from lm-sys/FastChat GitHub |
