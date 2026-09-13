# Product Requirements Document: h-e1-v3
# Global Percentile Threshold Language Retention Disparity Analysis

---

## Frontmatter

```yaml
hypothesis_id: h-e1-v3
hypothesis_type: EXISTENCE
tier: LIGHT
version: 1.0
generated_at: "2026-07-30"
phase: Phase 3 - Implementation Planning
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - data_specification
  - evaluation_metrics
  - non_functional_requirements
  - dependencies
  - success_criteria
```

---

## 1. Executive Summary

This document specifies implementation requirements for hypothesis **h-e1-v3**: a statistical analysis demonstrating that global k-th percentile thresholding on `ccnet_perplexity` quality signals in the RedPajama-V2 dataset produces statistically significant language-group retention disparity. The experiment is a CPU-only PoC (~50 lines of pandas/scipy code) requiring no ML training. Gate criterion: Cramér's V ∈ [0.29, 0.41] and Holm-corrected p < 0.001 for all 5 threshold values (k ∈ {10, 20, 30, 40, 50}).

**Scope:** Single Python script (`run_h_e1_v3.py`) + supporting modules. No GPU required. Runtime < 5 minutes (< 30 seconds with Parquet cache hit).

---

## 2. Problem Statement

**Research question:** Does applying a single global perplexity threshold to a multilingual dataset systematically exclude documents from specific language groups?

**Root cause (known):** CCNet trains language-specific KenLM models on Wikipedia. English Wikipedia is the largest corpus → English LM is best calibrated → English text achieves lower perplexity → global threshold retains proportionally fewer English documents. Italian has the smallest Wikipedia → highest perplexity baseline → highest retention rate under global threshold.

**Hypothesis to validate:** The statistical association between language identity and retention outcome (measured by Cramér's V) falls in the range [0.29, 0.41] for k ∈ {10, 20, 30, 40, 50}, and this association is statistically significant after Holm-Bonferroni correction.

---

## 3. Functional Requirements

### FR-1: Data Loading

**FR-1.1 Cache Detection**
- System MUST check for Parquet cache at `docs/youra_research/redpajama_sample.parquet` before any HuggingFace download.
- Cache is valid if: file exists AND row count ≥ 190,000 AND columns `['language', 'ccnet_perplexity']` both present.
- If cache valid: load directly (skip FR-1.2 through FR-1.4).

**FR-1.2 HuggingFace Download (cache miss only)**
- Load via: `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
- Extract from each document:
  - `ccnet_perplexity` = `json.loads(sample["quality_signals"])["ccnet_perplexity"][0][2]`
  - `language` = `json.loads(sample["meta"])["language"]`

**FR-1.3 Data Validation**
- MUST assert: `len(df) >= 190_000`
- MUST assert: `df['language'].nunique() == 5` (languages: en, de, fr, es, it)
- MUST assert: `df['ccnet_perplexity'].isna().mean() < 0.01`

**FR-1.4 Cache Save**
- After HuggingFace download: save cleaned DataFrame as Parquet to `docs/youra_research/redpajama_sample.parquet`.

---

### FR-2: Global Threshold Disparity Analysis

**FR-2.1 Percentile Thresholds**
- For each k ∈ {10, 20, 30, 40, 50}:
  - Compute: `threshold_k = df['ccnet_perplexity'].quantile(k / 100)` (pooled across all 5 languages)
  - Label: `retained = (df['ccnet_perplexity'] < threshold_k).astype(int)`

**FR-2.2 Contingency Table**
- For each k: compute `pd.crosstab(df['language'], retained)` → shape (5, 2)

**FR-2.3 Cramér's V**
- `from scipy.stats.contingency import association`
- `v = association(contingency.values, method='cramer')`
- Standard (uncorrected) V — bias correction NOT required (N=208,263 >> 100)

**FR-2.4 Chi-square P-value**
- `chi2, p, dof, expected = chi2_contingency(contingency.values)`
- Store raw p-value per k for Holm correction

**FR-2.5 Holm-Bonferroni Correction**
- `from statsmodels.stats.multitest import multipletests`
- `reject, p_holm, _, _ = multipletests([p_k10, p_k20, p_k30, p_k40, p_k50], method='holm')`

**FR-2.6 Per-language Retention Rates**
- `retention_rates = df.assign(retained=retained).groupby('language')['retained'].mean()`
- Compute `max_min_gap = retention_rates.max() - retention_rates.min()`

---

### FR-3: Gate Check

**FR-3.1 Gate Evaluation**
- Evaluate for all 5 k values simultaneously:
  - Condition A: `all(0.29 <= results[k]['cramers_v'] <= 0.41 for k in k_values)` 
  - Condition B: `all(p_holm[i] < 0.001 for i in range(5))`
- Gate passes only if BOTH conditions are TRUE.

**FR-3.2 Gate Result Output**
- Write gate result to `results.json` and `experiment_results.json`
- Log: `"GATE: PASS"` or `"GATE: FAIL"` with specific values

---

### FR-4: Output Files

**FR-4.1 Results JSON**
- Write `docs/youra_research/h-e1-v3/results.json`:
  ```json
  {
    "hypothesis_id": "h-e1-v3",
    "gate_result": "PASS/FAIL",
    "k_values": [10, 20, 30, 40, 50],
    "results": {
      "10": {"threshold": ..., "cramers_v": ..., "chi2": ..., "p_value": ..., "p_holm": ..., "retention_rates": {...}, "max_min_gap": ...},
      ...
    }
  }
  ```

**FR-4.2 Experiment Results JSON**
- Write `docs/youra_research/h-e1-v3/experiment_results.json` (Phase 4.5 compatible format):
  ```json
  {
    "hypothesis_id": "h-e1-v3",
    "status": "COMPLETED",
    "gate_passed": true/false,
    "primary_metric": "cramers_v",
    "results_by_k": {...}
  }
  ```

**FR-4.3 Mechanism Verification**
- Call `verify_mechanism_activated(df, results, k_values)` — log all 5 indicator results

---

### FR-5: Visualization

**FR-5.1 Gate Metrics Bar Chart (mandatory)**
- File: `docs/youra_research/h-e1-v3/figures/gate_metrics.png`
- x-axis: k values {10, 20, 30, 40, 50}
- y-axis: Cramér's V (0.0–0.5)
- Green bars for V ∈ [0.29, 0.41], red bars outside
- Dashed green reference lines at 0.29 and 0.41

**FR-5.2 Per-language Retention Rate Heatmap**
- File: `docs/youra_research/h-e1-v3/figures/retention_heatmap.png`
- Rows: languages (en, de, fr, es, it); Columns: k values; Color: retention rate

**FR-5.3 Perplexity Distribution KDE Plot**
- File: `docs/youra_research/h-e1-v3/figures/perplexity_kde.png`
- Overlaid KDE for each of 5 languages

**FR-5.4 Max–Min Retention Gap vs k**
- File: `docs/youra_research/h-e1-v3/figures/gap_vs_k.png`
- Line chart: x=k values, y=max-min retention gap

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | RedPajama-Data-V2 (sample split) |
| Source | `togethercomputer/RedPajama-Data-V2` (HuggingFace) |
| Split | `sample` |
| Size | 208,263 documents |
| Languages | en, de, fr, es, it |
| Load method | HuggingFace `datasets` library OR Parquet cache |
| Cache path | `docs/youra_research/redpajama_sample.parquet` |
| Cache status | **PRESENT** — verified from h-e1 run |

### 4.2 Key Fields

| Column | Type | Extraction |
|--------|------|-----------|
| `language` | str | `json.loads(sample["meta"])["language"]` |
| `ccnet_perplexity` | float | `json.loads(sample["quality_signals"])["ccnet_perplexity"][0][2]` |

### 4.3 Download Strategy

**Priority 1: Parquet cache** (`docs/youra_research/redpajama_sample.parquet`)
- Already confirmed present from h-e1 run
- Validate: row_count ≥ 190,000, columns `['language', 'ccnet_perplexity']`

**Priority 2: HuggingFace API** (cache miss or corrupted only)
- `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
- No manual download required — auto-download via datasets library

**No static datasets to download manually** → No `data-preparation` tasks needed.

---

## 5. Evaluation Metrics

### 5.1 Primary Metrics

| Metric | Target | Expected Value |
|--------|--------|----------------|
| Cramér's V (k=10) | ∈ [0.29, 0.41] | ~0.29 |
| Cramér's V (k=20) | ∈ [0.29, 0.41] | ~0.33 |
| Cramér's V (k=30) | ∈ [0.29, 0.41] | ~0.37 |
| Cramér's V (k=40) | ∈ [0.29, 0.41] | ~0.40 |
| Cramér's V (k=50) | ∈ [0.29, 0.41] | ~0.41 |
| Holm-corrected p (all k) | < 0.001 | ≈ 0 |
| English retention (k=30) | — | ~36.5% |
| Italian retention (k=30) | — | ~88.1% |
| Max–min gap (k=30) | — | ~51.6pp |

### 5.2 Metric Implementation

```python
from scipy.stats.contingency import association
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests

v = association(contingency_table, method='cramer')
chi2, p, dof, expected = chi2_contingency(contingency_table)
reject, p_holm, _, _ = multipletests([p1, p2, p3, p4, p5], method='holm')
```

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **NFR-1: Runtime** | < 5 minutes total; < 30 seconds with Parquet cache hit |
| **NFR-2: Hardware** | CPU-only — no GPU required |
| **NFR-3: Reproducibility** | Fixed seed=42; deterministic pandas/scipy operations |
| **NFR-4: scipy version** | >= 1.7 (required for `contingency.association` with method='cramer') |
| **NFR-5: Memory** | < 2GB RAM (208k rows × 2 columns is trivially small) |
| **NFR-6: Script entrypoint** | `code/run_h_e1_v3.py` — must be runnable with `python run_h_e1_v3.py` |

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=1.5
scipy>=1.7
numpy>=1.21
datasets>=2.0
statsmodels>=0.13
matplotlib>=3.5
seaborn>=0.11
```

**Note:** `datasets` only needed if Parquet cache is absent or corrupted.

### 7.2 External Repositories (Reference Only)

| Repo | URL | Purpose |
|------|-----|---------|
| togethercomputer/RedPajama-Data | https://github.com/togethercomputer/RedPajama-Data | Dataset schema reference |
| scipy/scipy | https://github.com/scipy/scipy/blob/main/scipy/stats/contingency.py | Cramér's V implementation |

No code from these repositories is imported. Reference only for understanding data schema.

### 7.3 Local Dependencies

| Path | Purpose |
|------|---------|
| `docs/youra_research/redpajama_sample.parquet` | Pre-built Parquet cache (confirmed present) |

---

## 8. Success Criteria

### 8.1 Gate Pass Conditions (ALL required)

| # | Criterion | Threshold |
|---|-----------|-----------|
| 1 | Data loads successfully | ≥190,000 rows, 5 languages, < 1% NaN |
| 2 | Cramér's V within range | V ∈ [0.29, 0.41] for ALL 5 k values |
| 3 | Statistical significance | Holm-corrected p < 0.001 for ALL 5 k values |
| 4 | Script completes without error | No unhandled exceptions |

### 8.2 Downstream Unblocking

Gate PASS unblocks: h-m1, h-c1, h-c2, h-m2
Gate FAIL: blocks all downstream hypotheses

---

## 9. File Structure

```
docs/youra_research/h-e1-v3/
├── 02c_experiment_brief.md    (input — Phase 2C)
├── 03_prd.md                  (this file)
├── 03_architecture.md         (Phase 3 output)
├── 03_logic.md                (Phase 3 output)
├── 03_config.md               (Phase 3 output)
├── 03_tasks.yaml              (Phase 3 output)
├── results.json               (Phase 4 output)
├── experiment_results.json    (Phase 4 output)
└── figures/
    ├── gate_metrics.png
    ├── retention_heatmap.png
    ├── perplexity_kde.png
    └── gap_vs_k.png

code/
└── run_h_e1_v3.py             (main experiment script)
```

---

*Document generated: 2026-07-30 | Phase 3 Implementation Planning | Hypothesis: h-e1-v3*
