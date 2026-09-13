# Product Requirements Document: h-e1-v3-v4
# Global k-th Percentile Threshold Disparity Analysis (Updated Gate)

**Date:** 2026-07-30
**Hypothesis:** h-e1-v3-v4 (EXISTENCE / PoC)
**Phase:** 3 — Implementation Planning
**Gate:** MUST_WORK
**Version:** 4 (gate bounds updated from [0.29, 0.41] → [0.40, 0.57] per h-e1 empirical results)

---

## 1. Objective

Verify that applying a global k-th percentile threshold on `ccnet_perplexity` to the
RedPajama-V2 sample dataset produces statistically significant language-group retention
disparity, quantified as Cramér's V ∈ [0.40, 0.57] for k ∈ {10, 20, 30, 40, 50}.

This is a pure statistical analysis — no ML training involved. Runtime target: <5 min, CPU-only.

**Key change from h-e1:** Gate range updated from [0.29, 0.41] to [0.40, 0.57] based on
empirical results from h-e1 (k=10: V=0.4021, k=20: V=0.5193, k=30: V=0.5629,
k=40: V=0.5696, k=50: V=0.5293).

---

## 2. Scope

**In scope:**
- Load RedPajama-V2 sample from parquet cache (208,262 rows, pre-existing)
- Apply global k-th percentile thresholds for k ∈ {10, 20, 30, 40, 50}
- Compute Cramér's V and Holm-corrected chi-square p-values
- Generate 4 required figures
- Write results JSON and gate verdict

**Out of scope:**
- Per-language thresholds (h-m1)
- ML model training
- Full RedPajama-V2 (non-sample splits)
- HuggingFace download (parquet cache already exists)

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load from parquet cache: `docs/youra_research/redpajama_sample.parquet`
- Code: `df = pd.read_parquet("docs/youra_research/redpajama_sample.parquet")`
- Fallback: Arrow IPC cache via `pyarrow.ipc` if parquet missing
- Validate: ≥190,000 rows, exactly 5 languages {en, de, fr, es, it}, NaN rate < 1%
- **No HuggingFace download needed — parquet cache VERIFIED EXISTING**

### FR-2: Data Validation
- Validate: `len(df) > 190_000`
- Validate: `df['language'].nunique() == 5`
- Validate: `df['ccnet_perplexity'].isna().mean() < 0.01`
- Drop rows where `ccnet_perplexity` is NaN before analysis
- Output: flat DataFrame with columns `[language, ccnet_perplexity]`

### FR-3: Global Threshold Analysis
- For each k ∈ {10, 20, 30, 40, 50}:
  - Compute `threshold_k = df['ccnet_perplexity'].quantile(k / 100)` (pooled global)
  - Label `retained = ccnet_perplexity < threshold_k` (binary)
  - Build 5×2 contingency table via `pd.crosstab(language, retained)`
  - Compute Cramér's V via `scipy.stats.contingency.association(table, method='cramer')`
  - Compute chi-square p-value via `scipy.stats.chi2_contingency(table)`
  - Compute per-language retention rates via `df.groupby('language')['retained'].mean()`

### FR-4: Multiple Testing Correction
- Collect 5 p-values (one per k value)
- Apply Holm-Bonferroni via `statsmodels.stats.multitest.multipletests(p_values, method='holm')`
- Record corrected p-values alongside raw

### FR-5: Gate Check (UPDATED)
- ALL conditions must be TRUE for gate pass:
  1. `len(df) > 190_000` — data loaded
  2. `df['language'].nunique() == 5` — all 5 languages present
  3. `df['ccnet_perplexity'].isna().mean() < 0.01` — <1% NaN
  4. `all(0.40 <= results[k]['cramers_v'] <= 0.57 for k in k_values)` — V in updated range
  5. `all(results[k]['p_holm'] < 0.001 for k in k_values)` — all Holm p significant
- Write gate verdict to `docs/youra_research/h-e1-v3-v4/gate_verdict.json`

### FR-6: Output Files
- `docs/youra_research/h-e1-v3-v4/results.json` — full results dict keyed by k
- `docs/youra_research/h-e1-v3-v4/gate_verdict.json` — `{gate_passed: bool, indicators: dict}`
- `docs/youra_research/h-e1-v3-v4/figures/cramers_v_bar.png` — Cramér's V vs k with updated bounds [0.40, 0.57]
- `docs/youra_research/h-e1-v3-v4/figures/retention_heatmap.png` — language × k heatmap
- `docs/youra_research/h-e1-v3-v4/figures/perplexity_kde.png` — KDE per language
- `docs/youra_research/h-e1-v3-v4/figures/retention_gap.png` — max−min gap vs k

### FR-7: Mechanism Verification
Implement `verify_mechanism_activated(results)` as specified in 02c_experiment_brief.md:
```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    indicators = {
        "data_loaded": results.get("n_rows", 0) >= 190_000,
        "five_languages": results.get("n_languages", 0) == 5,
        "no_nan_perplexity": results.get("nan_rate", 1.0) < 0.01,
        "cramers_v_in_range": all(
            0.38 <= r["cramers_v"] <= 0.60
            for r in results["per_k_results"]
        ),
        "holm_p_significant": all(
            r["p_holm"] < 0.001
            for r in results["per_k_results"]
        ),
    }
    return all(indicators.values()), indicators
```

---

## 4. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | <5 minutes on CPU (parquet cache avoids download) |
| Memory | <4 GB RAM for full sample DataFrame |
| Python | >=3.9 |
| Reproducibility | Deterministic pandas/scipy; no random operations needed |
| Code location | `docs/youra_research/h-e1-v3-v4/code/run_experiment.py` (single script) |

---

## 5. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=1.5 | DataFrame, groupby, crosstab, quantile, parquet I/O |
| scipy | >=1.7 | `contingency.association` (Cramér's V), `chi2_contingency` |
| numpy | >=1.21 | Array ops, numpy.bool_ → bool conversion |
| statsmodels | >=0.13 | Holm-Bonferroni (`multipletests`) |
| matplotlib | >=3.5 | Figure generation |
| seaborn | >=0.11 | Heatmap figure |
| pyarrow | >=6.0 | Parquet I/O fallback (Arrow IPC) |

**Note:** `datasets` library NOT required — parquet cache eliminates HF download.

---

## 6. Success Criteria (Gate Pass — UPDATED)

| Criterion | Threshold |
|-----------|-----------|
| Cramér's V (k=10) | 0.40 ≤ V ≤ 0.57 |
| Cramér's V (k=20) | 0.40 ≤ V ≤ 0.57 |
| Cramér's V (k=30) | 0.40 ≤ V ≤ 0.57 |
| Cramér's V (k=40) | 0.40 ≤ V ≤ 0.57 |
| Cramér's V (k=50) | 0.40 ≤ V ≤ 0.57 |
| Holm-corrected p (all k) | < 0.001 |
| Data rows loaded | > 190,000 |
| Languages present | == 5 |

**Expected from h-e1 empirical results:**
- k=10: V≈0.40 ✓, k=20: V≈0.52 ✓, k=30: V≈0.56 ✓, k=40: V≈0.57 ✓, k=50: V≈0.53 ✓

---

## 7. File Structure

```
docs/youra_research/
  redpajama_sample.parquet         # Existing parquet cache (208,262 rows)
  h-e1-v3-v4/
    03_prd.md                      # This file
    03_architecture.md
    03_logic.md
    03_config.md
    03_tasks.yaml
    code/
      run_experiment.py            # Single-script experiment
    results.json                   # Full analysis results
    gate_verdict.json              # Gate pass/fail + indicators
    figures/
      cramers_v_bar.png
      retention_heatmap.png
      perplexity_kde.png
      retention_gap.png
```

---

## 8. Ablation Variants

| Variant | Description | FR Reference |
|---------|-------------|--------------|
| Gate bounds [0.40, 0.57] | Primary variant — updated from h-e1 [0.29, 0.41] | FR-5.4 |
| Mechanism check [0.38, 0.60] | Wider range for mechanism activation check | FR-7 |

---

## 9. Validation Approach (Phase 4)

Phase 4 Coder implements `docs/youra_research/h-e1-v3-v4/code/run_experiment.py`.
Phase 4 Validator runs it and checks:
1. Script exits with code 0
2. `gate_verdict.json` contains `gate_passed: true`
3. All 4 figure files exist and are non-empty
4. `results.json` contains all 5 k values with `cramers_v` in [0.40, 0.57]
5. All Holm p-values < 0.001
