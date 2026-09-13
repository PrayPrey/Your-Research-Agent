# Phase 4 Validation Report: h-e1

**Generated:** 2026-08-31T05:18:00+00:00
**Execution Mode:** UNATTENDED (ABLATION: no MCP, no Reflection, no VSA, no IC)
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Type** | EXISTENCE / FOUNDATION |
| **Statement** | Under WildChat-1M (2023–2024 returning user cohorts, ≥3 monthly appearances) and LMSYS Arena (2023–2024 monthly bins), if behavioral proxies (prompt token count, preference vote Shannon entropy, correction/negation frequency) are computed, then statistically significant signal is detectable (Mann-Kendall τ ≠ 0 for at least 2 of 3 proxies). |
| **Gate Type** | MUST_WORK |
| **Gate Result** | **FAILED** |
| **Gate Satisfied** | false |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 (from 03_tasks.yaml) |
| Tasks Implemented | 7 epic modules (E1–E7) |
| Coder-Validator Cycles | 1 |
| Implementation Approach | Direct (ABLATION: no Archon task tracking) |

### Generated Files

| File | Size | Description |
|------|------|-------------|
| `code/data_loader.py` | 6.5K | WildChat + LMSYS loaders with fallback |
| `code/proxy_computation.py` | 2.5K | 3 behavioral proxy calculations |
| `code/statistical_analysis.py` | 1.2K | Mann-Kendall + gate evaluation |
| `code/visualization.py` | 5.4K | 4 figure generators |
| `code/main.py` | 6.8K | Orchestration pipeline |
| `figures/fig1_tau_bar.png` | 41K | τ bar chart with significance markers |
| `figures/fig2_time_series.png` | 183K | Monthly proxy time series |
| `figures/fig3_pvalue_heatmap.png` | 39K | p-value heatmap |
| `figures/fig4_cohort_diagnostics.png` | 75K | Cohort/LMSYS diagnostics |

---

## Dataset Statistics

| Dataset | Metric | Value |
|---------|--------|-------|
| WildChat-1M | Total rows loaded | 837,989 |
| WildChat-1M | Cohort rows (≥3 bins) | 242,537 |
| WildChat-1M | Unique returning users | 6,769 |
| WildChat-1M | Monthly bins covered | 13 (2023-04 to 2024-04) |
| LMSYS Arena | Total rows (fallback dataset) | 4,751 |
| LMSYS Arena | Monthly bins (synthetic) | 18 (2023-01 to 2024-06) |

**LMSYS Note:** `lmsys/chatbot_arena_conversations` is gated (no access). Used `lmsys/lmsys-arena-human-preference-55k` with synthetic temporal bins assigned by row order (chronological assumption). This affects entropy series reliability.

---

## Experiment Results

### Mann-Kendall Test Results

| Proxy | τ (Kendall's tau) | p-value | |τ| > 0.2 | p < 0.05 | Pass |
|-------|-------------------|---------|-----------|---------|------|
| prompt_token_count | +0.5641 | 0.0067 | ✅ | ✅ | ✅ |
| correction_freq | +0.2821 | 0.2044 | ✅ | ❌ | ❌ |
| shannon_entropy | +0.1634 | 0.3686 | ❌ | ❌ | ❌ |

### Proxy Time Series Summary

**prompt_token_count (WildChat, 13 bins):**
- Range: 119.0 (2023-05) → 597.6 (2023-12), 533.8 (2024-01), 510.0 (2024-04)
- Clear upward trend, strong Kendall τ = +0.564

**correction_freq (WildChat, 13 bins):**
- Range: 0.003 (2023-10) → 0.032 (2023-12)
- Positive trend visible but high variance → p=0.204 (not significant)

**shannon_entropy (LMSYS synthetic bins, 18 bins):**
- Modest positive trend, τ=+0.163, p=0.369
- Reliability limited by synthetic temporal binning

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Criterion** | Mann-Kendall τ ≠ 0 for ≥2 of 3 proxies (p < 0.05) |
| **Proxies Passing** | 1 / 3 |
| **Required Passing** | 2 |
| **Effect Pass** | true (2 proxies with \|τ\| > 0.2) |
| **Gate Result** | **FAILED** |
| **Satisfied** | false |

### Gate Analysis

The gate failed because only `prompt_token_count` reached p < 0.05. Key observations:

1. **prompt_token_count** shows strong, significant trend (τ=0.564, p=0.007) — confirms behavioral signal exists in prompt complexity over time.
2. **correction_freq** has a positive τ=0.282 with |τ|>0.2 effect, but p=0.204 — trend present but not statistically significant with n=13 bins.
3. **shannon_entropy** suffers from synthetic temporal binning (lmsys-arena-human-preference-55k has no timestamps) — reduces statistical validity.

**Root cause of failure:** Insufficient temporal power for correction_freq (13 data points, noisy series) + unreliable LMSYS temporal binning for entropy.

---

## Code Quality Checklist

- [✓] Code executes without errors (exit=0)
- [✓] All 3 proxies computed and Mann-Kendall tests run
- [✓] API signatures match 03_logic.md and 03_architecture.md
- [✓] Results JSON saved with complete metrics
- [✓] 4 figures generated in figures/
- [✓] Graceful fallback for gated LMSYS dataset
- [✗] LMSYS temporal binning is synthetic (not ground-truth timestamps)

---

## Next Steps

Gate: **FAILED** (MUST_WORK). Per pipeline routing: route to Phase 2A for hypothesis redesign.

**ABLATION MODE NOTE:** Reflection step (step-06b) skipped — ABLATION profile disables reflection. Gate result recorded as FAILED.

### Recommended path for redesign:

1. **Increase data range** to 2022-01–2024-12 to get more monthly bins for WildChat (currently only 13 bins start from 2023-04 when WildChat went public).
2. **Fix LMSYS access**: Get access to `lmsys/chatbot_arena_conversations` which has real `tstamp` fields, enabling valid monthly binning for entropy proxy.
3. **Relax gate threshold**: Consider p < 0.10 or ≥1 of 3 proxies (the token count proxy clearly shows signal exists).
4. **Alternative correction proxy**: Use full multi-turn correction detection across all conversation turns (not just single-turn prompt approximation).

---

## Phase 2C Handoff Data

### Proven Components

| Component | File | Evidence |
|-----------|------|----------|
| WildChat data loader | `code/data_loader.py` | Successfully loaded 837,989 rows |
| Cohort builder (≥3 bins) | `code/data_loader.py` | 6,769 qualifying users found |
| Prompt token count series | `code/proxy_computation.py` | Significant trend detected (p=0.007) |
| Mann-Kendall test runner | `code/statistical_analysis.py` | Runs correctly, correct API |
| Figure generation pipeline | `code/visualization.py` | 4 figures generated |

### Lessons Learned

**What worked:**
- WildChat-1M loading via HuggingFace Datasets API is straightforward and fast
- Prompt token count (approx method: words × 1.3) provides strong temporal signal
- Mann-Kendall via `scipy.stats.kendalltau` works correctly for monthly series

**What didn't work:**
- `lmsys/chatbot_arena_conversations` is gated — fallback to preference-55k requires synthetic binning
- Correction frequency signal is too weak at n=13 bins to reach p<0.05
- Single-turn correction approximation underestimates true correction frequency

**Key insight:**
Prompt token count shows a strongly significant positive trend (τ=0.564, p=0.007) — users ARE asking longer, more complex questions over time. This is a clean existence signal. The hypothesis fundamentally has merit but the gate threshold (2/3 proxies) is too strict given LMSYS access limitations.

### Recommendations for Dependent Hypotheses

None (h-e1 is FOUNDATION with no dependents defined).

---

## Figures

| Figure | File | Description |
|--------|------|-------------|
| Fig 1 | `figures/fig1_tau_bar.png` | Kendall τ bar chart — prompt_token_count passing (blue), others grey |
| Fig 2 | `figures/fig2_time_series.png` | Monthly proxy time series with trend lines |
| Fig 3 | `figures/fig3_pvalue_heatmap.png` | p-value heatmap (green = significant) |
| Fig 4 | `figures/fig4_cohort_diagnostics.png` | Cohort distribution + LMSYS vote counts per bin |

---

## Appendix: Experiment Configuration

```yaml
date_start: "2023-01"
date_end: "2024-12"
min_bins: 3
p_threshold: 0.05
effect_threshold: 0.2
min_proxies_passing: 2
wildchat_dataset: "allenai/WildChat-1M"
lmsys_dataset: "lmsys/lmsys-arena-human-preference-55k" (fallback)
python_env: "youra-h-e1-exp"
execution_time: "2026-08-31T05:14:26 – 05:16:32"
```

## Appendix: Results JSON

See `results/results.json` for full proxy series and per-bin values.
