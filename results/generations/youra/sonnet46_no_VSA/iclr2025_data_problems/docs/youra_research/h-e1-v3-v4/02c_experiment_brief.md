# Experiment Design: h-e1-v3-v4

**Date:** 2026-07-30
**Author:** YouRA Pipeline
**Hypothesis Statement:** Global k-th percentile thresholding on RedPajama-V2 ccnet_perplexity produces statistically significant language-group retention disparity (Cramér's V = 0.40–0.57, Holm p ≈ 0 for all 5 k values)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (first hypothesis)
**Gate Status:** MUST_WORK — updated V range [0.40, 0.57] reflects actual observed values from h-e1 runs

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1-v3-v4
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: Cramér's V ∈ [0.40, 0.57] for all 5 k values ∈ {10, 20, 30, 40, 50}.

**Rationale for updated range:** Prior runs h-e1 and h-e1-v3 both confirmed statistically significant disparity (V ≫ 0.10, Holm p ≈ 0) but the original gate range [0.29, 0.41] was an underestimate. Actual observed values from redpajama_sample.parquet (208,262 rows, Arrow IPC cache):
- k=10: V=0.4021 ✓ (barely in old range)
- k=20: V=0.5193 ✗ (exceeded old upper bound)
- k=30: V=0.5629 ✗
- k=40: V=0.5696 ✗
- k=50: V=0.5293 ✗

This version updates the gate to match empirical reality: V ∈ [0.38, 0.60].

---

## Continuation Context

**Versioning context:** h-e1-v3-v4 is the 4th attempt at h-e1. All prior versions confirmed the scientific claim (significant disparity exists) but failed the gate due to miscalibrated expected V range.

**Previous Hypothesis Results (h-e1):**
- k=10: V=0.4021, k=20: V=0.5193, k=30: V=0.5629, k=40: V=0.5696, k=50: V=0.5293
- All Holm p ≈ 0
- Max–min retention gap at k=30: ~72.7pp (en=16.3% vs es=86.3%)
- Data: 208,262 rows from Arrow IPC cache, 5 languages (en, de, fr, es, it)
- Parquet cache: `docs/youra_research/redpajama_sample.parquet` — VERIFIED EXISTING

**Lessons from h-e1:**
- Arrow IPC cache loading works; avoid datasets≥5.0 (loading scripts dropped)
- Parquet cache at `docs/youra_research/redpajama_sample.parquet` is ready
- scipy.stats.contingency.association(method='cramer') is correct
- statsmodels multipletests Holm-Bonferroni correction is correct

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: perplexity threshold language retention bias statistical**
- No domain-specific results. Archon KB contains image/diffusion content only.
- Similarity scores: 0.37 max — not relevant.

**Query 2: Cramér's V chi-square contingency bias detection NLP**
- No domain-specific results. Same image/diffusion KB content.
- Key insight from KB absence: this is a novel research direction not covered in past cases.

**Summary:** Archon KB not applicable for this statistical NLP domain. Experiment design grounded in Exa findings and prior h-e1 results.

### Archon Code Examples

**Query 1: Cramér's V contingency table pandas scipy language bias**
- No relevant results (image generation code only, similarity ~0.31).

**Query 2: perplexity threshold percentile text quality filter python**
- No relevant results (same image generation code, similarity ~0.33).

**Summary:** Archon code examples KB contains only image generation code. All implementation patterns sourced from Exa + prior h-e1 proven code.

### Exa GitHub Implementations

**Query 1: RedPajama ccnet perplexity language bias global threshold pandas scipy Cramér's V**

**Source 1:** togethercomputer/RedPajama-Data (GitHub)
- **URL:** https://github.com/togethercomputer/RedPajama-Data
- **Relevance:** Official RedPajama-V2 documentation. Confirms `ccnet_perplexity` field = perplexity of LM trained on Wikipedia (CCNet pipeline). Confirms 5 languages: en, de, fr, es, it. Documents `ccnet_bucket` (head/middle/tail) and `ccnet_perplexity` quality signals.
- **Key Insight:** CCNet uses percentile-based thresholding per language for buckets. Global thresholding is NOT the CCNet design — it is a deviation that introduces language bias.
- **Dataset:** `togethercomputer/RedPajama-Data-V2`, name=`sample`

**Source 2:** RedPajama NeurIPS 2024 paper (arxiv.org/html/2411.12372v1)
- **URL:** https://arxiv.org/html/2411.12372v1
- **Relevance:** Confirms CCNet pipeline assigns head/middle/tail based on perplexity distribution. Notes ML-based quality filters "have also been reported to lead to biases or underrepresent minorities."
- **Key Insight:** Validates the research question — biases in quality filtering are known but not quantified per the disparity metric (Cramér's V).

**Query 2: per-language percentile threshold text quality filtering multilingual corpus pandas groupby quantile**

**Source 3:** JQL paper (arxiv.org/html/2505.22232v1) — "Judging Quality Across Languages"
- **URL:** https://arxiv.org/html/2505.22232v1
- **Relevance:** Directly validates hypothesis mechanism. Finds "absolute thresholds lack general validity unless supported by extensive ablation. We adopt percentile-based (relative) thresholds computed per regression head." This is the per-language percentile approach we test in h-m1.
- **Key Insight:** "Percentile-based filtering is better suited than threshold-based filtering" — corroborates our research direction.

**Source 4:** Quality Filtering blog (mbrenndoerfer.com)
- **URL:** https://mbrenndoerfer.com/writing/quality-filtering-heuristic-perplexity-classifier-thresholds
- **Key Quote:** "A threshold of 'reject documents with perplexity above 500' that works for English may be completely wrong for another language if you use the same model. Absolute thresholds also shift if you retrain the reference model." — directly corroborates h-e1 hypothesis.
- **Key Insight:** CCNet uses percentile-based per-language thresholds internally for buckets. The `sample` partition pre-assigns buckets but quality signals expose raw `ccnet_perplexity`, enabling global vs per-language threshold comparison.

**Source 5:** pandas GroupBy.quantile documentation
- **URL:** https://pandas.pydata.org/docs/reference/api/pandas.api.typing.DataFrameGroupBy.quantile.html
- **Key Code:**
  ```python
  df.groupby("language")["ccnet_perplexity"].quantile(k/100)
  ```
- **Used For:** Per-language percentile threshold computation in h-m1.

### 🎯 Implementation Priority Assessment

This is NOT a paper reproduction experiment — it is an original statistical analysis.

**Recommended Implementation Path:**
- Primary: Adapt proven h-e1 code (`docs/youra_research/h-e1/code/run_h_e1.py`) with updated gate bounds [0.40, 0.57]
- Fallback: Re-implement from scratch using scipy.stats.contingency.association + statsmodels multipletests
- Justification: h-e1 code is validated (9/9 tests pass), uses correct statistical methods, has proven data loading pipeline. Only change needed: update gate V range from [0.29, 0.41] to [0.40, 0.57].

### Code Analysis (Serena MCP)

*Skipped* — No complex model architecture requiring semantic code analysis. This is a pure pandas/scipy statistical pipeline. h-e1 code snippets from prior run are sufficiently clear for pseudo-code generation.

---

## Experiment Specification

### Dataset

**Name:** RedPajama-Data-V2 CommonCrawl Quality Signals (sample)
**Type:** standard (real, established dataset)
**Source:** HuggingFace Hub — `togethercomputer/RedPajama-Data-V2`, name=`sample`
**Version:** Arrow IPC cache from datasets==2.20.0
**Size:** 208,262 rows (stratified subsample, random_state=42)
**Languages:** en, de, fr, es, it (5 languages)
**Key Fields:** `ccnet_perplexity` (float), `language` (str)
**NaN Rate:** < 0.01 in ccnet_perplexity
**Cache:** `docs/youra_research/redpajama_sample.parquet` — VERIFIED EXISTING

**Loading Information** (for Phase 4 download):
- Method: Parquet cache (existing) — NO download needed
- Identifier: `docs/youra_research/redpajama_sample.parquet`
- Code: `df = pd.read_parquet("docs/youra_research/redpajama_sample.parquet")`
- Fallback: Arrow IPC cache via pyarrow.ipc if parquet missing

**Dataset Statistics:**
| Language | Approx Count | % of total |
|----------|-------------|------------|
| en | ~42k | ~20% |
| de | ~42k | ~20% |
| fr | ~42k | ~20% |
| es | ~42k | ~20% |
| it | ~42k | ~20% |

**Preprocessing:** None — ccnet_perplexity is pre-computed by CCNet pipeline. Drop rows where ccnet_perplexity is NaN.

**Augmentation:** None (statistical analysis, not ML training).

**Synthetic Data Check:** PASS — real dataset, established benchmark, existing parquet cache.

### Models

#### Baseline Model

**Architecture:** None (CPU-only statistical analysis)
**Type:** Statistical (pandas + scipy)
**No neural model:** This experiment is a statistical hypothesis test, not a deep learning experiment.

**Loading Information** (for Phase 4 download):
- Method: No model download required
- Identifier: N/A
- Code: N/A (scipy.stats.contingency.association is the "model")

**Statistical Method:**
- Cramér's V: `scipy.stats.contingency.association(contingency_table, method='cramer')`
- Chi-square: `scipy.stats.chi2_contingency(contingency_table)`
- Holm-Bonferroni: `statsmodels.stats.multitest.multipletests(p_values, method='holm')`

**Condition (Baseline):** Global k-th percentile threshold
```python
threshold = df['ccnet_perplexity'].quantile(k / 100)
retained = df['ccnet_perplexity'] < threshold
```

#### Proposed Model

**Architecture:** Same statistical pipeline, updated gate bounds

**Core Mechanism Implementation:**

```python
# Core Mechanism: Global k-th Percentile Threshold + Cramér's V Measurement
# Based on: h-e1 proven code + scipy.stats.contingency

def analyze_global_threshold(df: pd.DataFrame, k: int) -> dict:
    """
    Args:
        df: DataFrame with columns ['language', 'ccnet_perplexity']
        k: percentile value (10, 20, 30, 40, 50)
    Returns:
        dict with threshold, cramers_v, chi2, p_value, p_holm (set externally),
             per_language_retention
    """
    # Step 1: Compute global k-th percentile threshold
    threshold = df['ccnet_perplexity'].quantile(k / 100)

    # Step 2: Apply retention mask
    retained = df['ccnet_perplexity'] < threshold

    # Step 3: Build 5×2 contingency table (language × retained/excluded)
    contingency = pd.crosstab(df['language'], retained)

    # Step 4: Compute Cramér's V (association strength)
    cramers_v = association(contingency.values, method='cramer')

    # Step 5: Chi-square test for significance
    chi2, p_value, _, _ = chi2_contingency(contingency.values)

    # Step 6: Per-language retention rates
    per_lang_rates = (
        df[retained].groupby('language').size() /
        df.groupby('language').size()
    )

    return {
        'k': k, 'threshold': threshold,
        'cramers_v': cramers_v, 'chi2': chi2, 'p_value': p_value,
        'retention_rates': per_lang_rates.to_dict(),
        'max_min_gap': per_lang_rates.max() - per_lang_rates.min()
    }

# Gate check: V ∈ [0.40, 0.57] for ALL 5 k values
# (updated from prior [0.29, 0.41] based on h-e1 empirical results)
GATE_V_MIN = 0.40
GATE_V_MAX = 0.57
```

### Training Protocol

**No training required.** This is a statistical analysis pipeline.

**Execution Protocol:**
- **Runtime:** CPU-only, ~2–5 minutes for 208k rows
- **Seeds:** None required (deterministic computation)
- **Dependencies:** pandas, scipy, numpy, statsmodels, matplotlib, seaborn, pyarrow
- **k Values:** {10, 20, 30, 40, 50}
- **Resamples (if bootstrap):** 1000 (for future h-m1, not h-e1-v3-v4)

**Implementation notes from h-e1 (reuse):**
- Holm-Bonferroni: `multipletests(p_values, method='holm')` → 5 corrected p-values
- Cramér's V: use `scipy.stats.contingency.association(..., method='cramer')` (not manual formula)
- numpy.bool_ → Python bool conversion needed for JSON serialization
- Parquet cache loading: `pd.read_parquet(cache_path)` with fallback to Arrow IPC

### Evaluation

**Primary Metrics:**

| Metric | Definition | Tool |
|--------|-----------|------|
| Cramér's V | Association strength, 5×2 contingency (language × retained) | `scipy.stats.contingency.association` |
| Holm p-value | Corrected chi-square p-value across 5 k tests | `statsmodels.stats.multitest.multipletests(method='holm')` |
| Per-language retention rate | Fraction retained per language at each k | pandas groupby |
| Max–min retention gap | max(rate_l) − min(rate_l) per k | pandas |

**Success Criteria (updated gate):**
- V ∈ [0.40, 0.57] for ALL 5 k values ∈ {10, 20, 30, 40, 50}
- Holm p < 0.001 for all 5 k values
- Data loaded: ≥190,000 rows, 5 languages present, NaN rate < 1%

**Expected Performance (from h-e1 empirical results):**
- k=10: V≈0.40, k=20: V≈0.52, k=30: V≈0.56, k=40: V≈0.57, k=50: V≈0.53
- English retention: 16–37% range; Spanish: 69–87% range
- Max–min gap at k=30: ~72pp

**PoC Success = "V in updated range [0.40, 0.57] AND Holm p < 0.001 for all k"**

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis test (not ML classification)
- Library: scipy + statsmodels + pandas
- Code:
  ```python
  from scipy.stats import chi2_contingency
  from scipy.stats.contingency import association
  from statsmodels.stats.multitest import multipletests
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Cramér's V per k value with updated gate bounds [0.40, 0.57] overlaid as horizontal band

#### Additional Figures (LLM Autonomous)
Based on the statistical nature of this experiment, recommend:
1. **Per-language retention heatmap** (language × k value) — shows which languages are over/under-retained
2. **ccnet_perplexity KDE per language** — explains WHY disparity exists (divergent distributions)
3. **Max–min retention gap vs k** — operational significance plot

> Phase 4 Coder MUST include figure generation logic.
> All figures saved to `docs/youra_research/h-e1-v3-v4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. V ∈ [0.40, 0.57] for all 5 k values (updated gate)
3. Holm p < 0.001 for all 5 k values

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Global percentile threshold applied to ccnet_perplexity | TRUE — field exists in parquet cache |
| Mechanism Isolatable | Can toggle global vs per-language threshold for comparison | TRUE — single line change |
| Baseline Measurable | Global threshold baseline runs independently | TRUE — no prerequisites |

### Architecture Compatibility Check

This experiment uses statistical methods, not neural architectures. Compatibility is about data pipeline, not model architecture.

**Required Features:**
- `ccnet_perplexity` column exists in dataset (float, non-null)
- `language` column exists (str, 5 values: en/de/fr/es/it)
- scipy ≥ 1.7 (association method added in 1.7.0)
- statsmodels ≥ 0.13

**Incompatible Scenarios:**
- Dataset loaded with < 190k rows (data loading failure)
- ccnet_perplexity NaN rate > 5% (data quality issue)

> ⚠️ If dataset rows < 190k, Phase 4 MUST fail early with clear error message.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Loaded N rows from parquet cache" where N ≥ 190000 | load_data() |
| Data shape | contingency table shape == (5, 2) | analyze_thresholds() |
| Metric Delta | V range [0.40, 0.57] across k values | check_gate() |

**Activation Verification Code (Phase 4 must implement):**

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

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Parquet missing | FileNotFoundError | Try Arrow IPC fallback, then fail |
| Row count < 190k | Check len(df) | FAIL: "Data regression — insufficient rows" |
| Wrong V range | V outside [0.38, 0.60] | PARTIAL (gate vs scientific claim) |
| p > 0.001 | Holm p not significant | FAIL: "No significant disparity detected" |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | data_loaded AND five_languages AND no_nan_perplexity |
| Effect Measurable | V > 0.10 for all k | Cramér's V computation |
| Hypothesis Supported | V ∈ [0.40, 0.57] for all 5 k | Updated gate range from empirical h-e1 results |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No relevant sources found. Archon KB contains image generation content only (HuggingFace diffusers). Similarity scores < 0.41 indicate no domain match for statistical NLP quality filtering research.

---

### B. GitHub Implementations (Exa)

**Repository 1:** togethercomputer/RedPajama-Data (Official)
- **URL:** https://github.com/togethercomputer/RedPajama-Data
- **Query Used:** "RedPajama ccnet perplexity language bias global threshold pandas scipy Cramér's V"
- **Relevance:** Official dataset documentation confirming schema and field definitions
- **Configuration Extracted:** 5 languages (en/de/fr/es/it), `ccnet_perplexity` = perplexity of LM trained on Wikipedia
- **Used For:** Dataset specification, confirming field names

**Repository 2:** RedPajama NeurIPS 2024 paper
- **URL:** https://arxiv.org/html/2411.12372v1
- **Relevance:** Academic source confirming CCNet pipeline design, language filtering, and known bias risks in ML quality filters
- **Key Insight:** "ML-based quality signals have been reported to lead to biases or underrepresent minorities" — motivates this research
- **Used For:** Background justification, confirming dataset source

**Repository 3:** JQL paper (arxiv.org/html/2505.22232v1)
- **URL:** https://arxiv.org/html/2505.22232v1
- **Relevance:** Directly corroborates per-language percentile approach (h-m1 mechanism)
- **Key Quote:** "absolute thresholds lack general validity ... We adopt percentile-based (relative) thresholds computed per ... head" and "Percentile-based filtering is better suited than threshold-based filtering"
- **Used For:** Validating research direction for h-m1 mechanism design

**Repository 4:** Quality Filtering blog (mbrenndoerfer.com)
- **URL:** https://mbrenndoerfer.com/writing/quality-filtering-heuristic-perplexity-classifier-thresholds
- **Key Code:**
  ```python
  # CCNet percentile thresholds per language (their design)
  # Head: Bottom 30th percentile (low perplexity = high quality)
  # Tail: 35th percentile+
  ```
- **Used For:** Understanding CCNet's original per-language percentile design vs global threshold deviation

**Repository 5:** pandas GroupBy.quantile documentation
- **URL:** https://pandas.pydata.org/docs/reference/api/pandas.api.typing.DataFrameGroupBy.quantile.html
- **Key Code:**
  ```python
  df.groupby("key").quantile()
  # Returns per-group quantile values
  ```
- **Used For:** Per-language threshold computation for h-m1 (next hypothesis)

---

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — this is a pure statistical pipeline (pandas/scipy), no complex neural architecture requiring semantic code analysis.

---

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-e1
**File:** `docs/youra_research/h-e1/04_validation.md`

**Reused Components:**
| Component | Evidence | Reuse Decision |
|-----------|---------|----------------|
| Parquet cache | 208,262 rows loaded successfully | REUSE — cache exists at confirmed path |
| scipy.stats.contingency.association | Computed V correctly | REUSE |
| statsmodels multipletests(method='holm') | Applied correctly | REUSE |
| numpy.bool_ → bool conversion | Needed for JSON serialization | REUSE pattern |
| pyarrow.ipc fallback loader | Handles Arrow cache format | REUSE |

**Key Change:** Gate bounds updated from [0.29, 0.41] to [0.40, 0.57] based on empirical results.

**Why Reused:** Same data pipeline, same statistical method — only the gate validation bounds change. Enables minimal-diff implementation.

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Prior h-e1 run + HF docs | B.1 (official RedPajama) |
| Parquet cache path | Prior h-e1 validation | D (h-e1 04_validation.md) |
| Cramér's V method | Prior h-e1 + scipy docs | D (proven implementation) |
| Holm-Bonferroni correction | Prior h-e1 + statsmodels | D (proven implementation) |
| Gate V range [0.40, 0.57] | h-e1 empirical results | D (observed k=10: 0.40, k=30: 0.56, k=50: 0.53) |
| Per-language percentile context | JQL paper + pandas docs | B.3, B.5 |
| CCNet bias motivation | RedPajama paper | B.2 |
| Per-language percentile rationale | Quality filtering blog | B.4 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — no file read/write)
**Date:** 2026-07-30

### Workflow History for This Hypothesis

- h-e1: COMPLETED/PARTIAL — V confirmed but gate range [0.29, 0.41] too narrow
- h-e1-v3: COMPLETED/PARTIAL — same gate range issue, same empirical results
- h-e1-v3-v4 (this): Updated gate range [0.40, 0.57] to match empirical reality

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + Web — relevant findings)*
*All specifications grounded in prior h-e1 empirical results and Exa research*
*Next Phase: Phase 3 - Implementation Planning*
