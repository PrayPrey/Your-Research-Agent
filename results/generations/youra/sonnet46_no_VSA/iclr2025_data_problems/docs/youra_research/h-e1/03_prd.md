# Product Requirements Document: h-e1
# Global k-th Percentile Threshold Disparity Analysis

**Date:** 2026-07-30
**Hypothesis:** h-e1 (EXISTENCE / PoC)
**Phase:** 3 — Implementation Planning
**Gate:** MUST_WORK

---

## 1. Objective

Verify that applying a global k-th percentile threshold on `ccnet_perplexity` to the
RedPajama-V2 sample dataset produces statistically significant language-group retention
disparity, quantified as Cramér's V ∈ [0.29, 0.41] for k ∈ {10, 20, 30, 40, 50}.

This is a pure statistical analysis — no ML training involved. Runtime target: <5 min, CPU-only.

---

## 2. Scope

**In scope:**
- Load RedPajama-Data-V2 `sample` split (208,263 docs, 5 languages)
- Extract `ccnet_perplexity` from `quality_signals` JSON field
- Apply global k-th percentile thresholds for k ∈ {10, 20, 30, 40, 50}
- Compute Cramér's V and Holm-corrected chi-square p-values
- Generate 4 required figures
- Write results JSON and gate verdict

**Out of scope:**
- Per-language thresholds (h-m1)
- ML model training
- Full RedPajama-V2 (non-sample splits)
- Archive code from prior pipeline iterations

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load via `datasets.load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
- Cache to `docs/youra_research/redpajama_sample.parquet` on first load
- Reuse parquet cache if it exists (avoids re-download)
- Validate: 208,263 rows ±5% tolerance (>190,000 rows acceptable), exactly 5 languages {en, de, fr, es, it}

### FR-2: Quality Signal Extraction
- Parse `quality_signals` JSON string field per row
- Extract `ccnet_perplexity` as `signals["ccnet_perplexity"][0][2]` (float)
- Extract `language` from dataset metadata field
- Drop rows where `ccnet_perplexity` is None/NaN (must be <1% of total)
- Output: flat DataFrame with columns `[language, ccnet_perplexity]`

### FR-3: Global Threshold Analysis
- For each k ∈ {10, 20, 30, 40, 50}:
  - Compute `threshold_k = df['ccnet_perplexity'].quantile(k / 100)` (pooled)
  - Label `retained = ccnet_perplexity < threshold_k` (binary)
  - Build 5×2 contingency table via `pd.crosstab(language, retained)`
  - Compute Cramér's V via `scipy.stats.contingency.association(table, method='cramer')`
  - Compute chi-square p-value via `scipy.stats.chi2_contingency(table)`
  - Compute per-language retention rates via `df.groupby('language')['retained'].mean()`

### FR-4: Multiple Testing Correction
- Collect 5 p-values (one per k value)
- Apply Holm-Bonferroni via `statsmodels.stats.multitest.multipletests(p_values, method='holm')`
- Record corrected p-values alongside raw

### FR-5: Gate Check
- ALL 4 conditions must be TRUE for gate pass:
  1. `len(df) > 190_000` — data loaded
  2. `df['language'].nunique() == 5` — all 5 languages present
  3. `df['ccnet_perplexity'].isna().mean() < 0.01` — <1% NaN
  4. `all(0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values)` — V in range
- Write gate verdict to `docs/youra_research/h-e1/gate_verdict.json`

### FR-6: Output Files
- `docs/youra_research/h-e1/results.json` — full results dict keyed by k
- `docs/youra_research/h-e1/gate_verdict.json` — `{gate_passed: bool, indicators: dict}`
- `docs/youra_research/h-e1/figures/cramers_v_bar.png` — Cramér's V vs k with bounds
- `docs/youra_research/h-e1/figures/retention_heatmap.png` — language × k heatmap
- `docs/youra_research/h-e1/figures/perplexity_kde.png` — KDE per language
- `docs/youra_research/h-e1/figures/retention_gap.png` — max−min gap vs k

---

## 4. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | <5 minutes on CPU (excluding first-time HuggingFace download) |
| Memory | <4 GB RAM for full sample DataFrame |
| Python | >=3.9 |
| Reproducibility | Fixed seed=42 for any random operations; deterministic pandas/scipy |
| Code location | `code/run_h_e1.py` (single script) |

---

## 5. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=1.5 | DataFrame, groupby, crosstab, quantile |
| scipy | >=1.7 | `contingency.association` (Cramér's V), `chi2_contingency` |
| numpy | >=1.21 | Array ops |
| datasets | >=2.0 | HuggingFace dataset loading |
| statsmodels | >=0.13 | Holm-Bonferroni (`multipletests`) |
| matplotlib | >=3.5 | Figure generation |
| seaborn | >=0.11 | Heatmap figure |

---

## 6. Success Criteria (Gate Pass)

| Criterion | Threshold |
|-----------|-----------|
| Cramér's V (k=10) | 0.29 ≤ V ≤ 0.45 |
| Cramér's V (k=20) | 0.29 ≤ V ≤ 0.45 |
| Cramér's V (k=30) | 0.29 ≤ V ≤ 0.45 |
| Cramér's V (k=40) | 0.29 ≤ V ≤ 0.45 |
| Cramér's V (k=50) | 0.29 ≤ V ≤ 0.45 |
| Holm-corrected p (all k) | < 0.001 |
| Data rows loaded | > 190,000 |
| Languages present | == 5 |

---

## 7. File Structure

```
code/
  run_h_e1.py              # Single-script experiment
docs/youra_research/
  redpajama_sample.parquet # Cached dataset (created on first run)
  h-e1/
    results.json           # Full analysis results
    gate_verdict.json      # Gate pass/fail + indicators
    figures/
      cramers_v_bar.png
      retention_heatmap.png
      perplexity_kde.png
      retention_gap.png
```

---

## 8. Validation Approach (Phase 4)

Phase 4 Coder implements `code/run_h_e1.py`.
Phase 4 Validator runs it and checks:
1. Script exits with code 0
2. `gate_verdict.json` contains `gate_passed: true`
3. All 4 figure files exist and are non-empty
4. `results.json` contains all 5 k values with `cramers_v` in [0.29, 0.45]
