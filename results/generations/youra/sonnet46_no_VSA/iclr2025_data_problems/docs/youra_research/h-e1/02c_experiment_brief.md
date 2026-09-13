# Experiment Design: h-e1

**Date:** 2026-07-30
**Author:** Anonymous
**Hypothesis Statement:** Global k-th percentile thresholding on RedPajama-V2 ccnet_perplexity produces statistically significant language-group retention disparity (Cramér's V = 0.29–0.41, Holm p ≈ 0 for all 5 k values).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition
MUST_WORK: Cramér's V ∈ [0.29, 0.41] for k ∈ {10, 20, 30, 40, 50} using global percentile threshold on the 208,263-row RedPajama-V2 sample. V < 0.10 or data load failure = gate violation, blocks h-m1/h-c1/h-c2/h-m2.

---

## Continuation Context

This is the first sub-hypothesis in the chain. No prior hypothesis results to inherit.

**Note:** If a Parquet cache from a prior h-m1 run exists at `docs/youra_research/`, Phase 4 should detect and reuse it to avoid re-downloading from HuggingFace.

### Previous Hypothesis Results (if applicable)
None — first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Assessment:** Archon KB returned no domain-relevant results for this hypothesis.
The KB contains diffusion/vision model content (LAION-5B, Stable Diffusion) with
low similarity scores (0.35–0.44) — unrelated to text quality filtering or statistical
disparity analysis. No Archon findings applicable.

**Fallback:** All implementation details sourced from Exa (official repos + scipy docs).

### Archon Code Examples

No relevant code examples found. KB does not contain RedPajama, CCNet, pandas
filtering, or Cramér's V implementations.

### Exa GitHub Implementations

**Repository 1: togethercomputer/RedPajama-Data (⭐ 4947)**
- **URL:** https://github.com/togethercomputer/redpajama-data
- **Relevance:** Official RedPajama-V2 repository — ground truth for dataset structure and quality signals
- **Dataset Loading:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")
  ```
- **Quality Signal Schema:** `quality_signals` field is JSON string containing nested
  `(start, end, score)` tuples. `ccnet_perplexity` accessed as `signals["ccnet_perplexity"][0][2]`
- **Key Insight:** `ccnet_perplexity` is a 5-gram Kneser-Ney LM perplexity trained on
  Wikipedia, computed per-language. CCNet originally buckets data into head/middle/tail
  using language-specific thresholds — the `sample` split contains head+middle documents.

**Repository 2: rakseli/redpajama-v2-processing**
- **URL:** https://github.com/rakseli/redpajama-v2-processing
- **Relevance:** Real-world per-language percentile filtering of RedPajama-V2
- **Key Pattern:** Used language-specific p-quantile thresholds (different percentiles
  per language: 0.02% for English, 0.05% for other languages) — validates that
  language-adaptive thresholding is the standard practice and global thresholding is
  the non-standard baseline our hypothesis tests.
- **Configuration extracted:**
  ```
  Regular:  p1=10, p3=90
  Strict:   p1=20, p3=80
  Even stricter: p1=30, p3=70
  Strictest: p1=40, p3=60
  ```
  Used stricter filtering for English, regular for other languages → corroborates
  that English requires different thresholds due to distributional differences.

**Repository 3: facebookresearch/cc_net**
- **URL:** https://github.com/facebookresearch/cc_net
- **Relevance:** Original CCNet pipeline — source of ccnet_perplexity
- **Key Insight:** Perplexity is computed by language-specific KenLM models (5-gram
  Kneser-Ney on Wikipedia). Each language's Wikipedia has different size/vocabulary →
  perplexity distributions are NOT comparable across languages. This is the root
  cause of global-threshold bias that h-e1 confirms.

**Scipy Reference:**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html
- **Cramér's V:** `scipy.stats.contingency.association(observed, method='cramer')`
  where `observed` is a contingency table (shape: n_languages × 2 for retained/excluded)

**Serena Analysis Needed:** False — pure pandas/scipy pipeline, no complex ML architecture

### 🎯 Implementation Priority Assessment

This is NOT a paper-reproduction experiment. It is an original statistical analysis
of pre-computed quality signals.

**No author implementation to follow.** The mechanism is novel:
- Apply global k-th percentile threshold to `ccnet_perplexity`
- Compute Cramér's V on resulting 5×2 contingency table

**Recommended Implementation Path:**
- Primary: Custom pandas + scipy implementation (only correct approach)
- Fallback: N/A — no existing implementation to fall back to
- Justification: Standard statistical pipeline; scipy provides Cramér's V directly;
  pandas groupby handles per-language retention rate computation

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The mechanism is a
~50-line pandas/scipy script with no complex architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** RedPajama-Data-V2 (sample split)
**Type:** standard (programmatic-api via HuggingFace datasets)
**Source:** `togethercomputer/RedPajama-Data-V2`
**Split:** `sample` (pre-built 208,263-document subset)
**Languages:** en, de, fr, es, it (5 languages)
**Key Fields:**
- `ccnet_perplexity` (float): Wikipedia LM perplexity (from quality_signals JSON)
- `language` (str): language tag {en, de, fr, es, it}
**Size:** 208,263 documents
**Source:** huggingface.co/datasets/togethercomputer/RedPajama-Data-V2

**Preprocessing:**
1. Load via `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
2. Parse `quality_signals` JSON field → extract `ccnet_perplexity` value
3. Extract `language` from metadata
4. Drop rows where `ccnet_perplexity` is None/NaN
5. Produce flat DataFrame: `[doc_id, language, ccnet_perplexity]`

**Cache strategy:** Save as Parquet to `docs/youra_research/redpajama_sample.parquet`
after first load; subsequent runs load from cache.

**Expected distribution (from Phase 2B baseline):**
- English: largest group, lowest perplexity median (well-represented in Wikipedia LM)
- Italian: smallest representation in Wikipedia LM → highest perplexity baseline
- Cross-language perplexity ranges differ substantially → source of global threshold bias

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"togethercomputer/RedPajama-Data-V2"`
- Code: `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`

### Models

#### Baseline Model

**Architecture:** No ML model — CPU-only statistical analysis
**Baseline "model":** Global k-th percentile threshold on ccnet_perplexity
**Computation:** `threshold_k = df['ccnet_perplexity'].quantile(k/100)`

For k ∈ {10, 20, 30, 40, 50}:
- Threshold: k-th percentile of ALL documents (pooled across languages)
- Retention rule: `retained = df['ccnet_perplexity'] < threshold_k`
- Result: per-language retention rates, 5×2 contingency table

**Loading Information** (for Phase 4 download):
- Method: stdlib (pandas, scipy, numpy — no download needed)
- Identifier: N/A
- Code: `import pandas as pd; from scipy.stats.contingency import association`

#### Proposed Model

**Architecture:** Baseline statistical pipeline (no change for h-e1)

h-e1 IS the baseline — it measures the global threshold disparity.
The "proposed model" (per-language threshold) is tested in h-m1, not here.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Global k-th Percentile Threshold Disparity Measurement
# Based on: CCNet perplexity design (Wenzek et al. 2020), scipy.stats.contingency
# Source: rakseli/redpajama-v2-processing (per-language contrast), official RedPajama docs

import pandas as pd
import numpy as np
from scipy.stats.contingency import association, chi2_contingency

def compute_global_threshold_disparity(df: pd.DataFrame, k_values: list) -> dict:
    """
    Args:
        df: DataFrame with columns ['language', 'ccnet_perplexity']
            shape: (208263,) — full sample
        k_values: list of percentile values, e.g. [10, 20, 30, 40, 50]
    Returns:
        dict mapping k → {cramers_v, p_value, retention_rates_per_lang}
    """
    results = {}
    languages = sorted(df['language'].unique())  # ['de', 'en', 'es', 'fr', 'it']

    for k in k_values:
        # Step 1: Compute global threshold (pooled across all languages)
        threshold = df['ccnet_perplexity'].quantile(k / 100)

        # Step 2: Apply threshold → binary retained/excluded label
        df['retained'] = (df['ccnet_perplexity'] < threshold).astype(int)

        # Step 3: Build 5×2 contingency table (language × retained)
        contingency = pd.crosstab(df['language'], df['retained'])
        # Shape: (5, 2) — rows=languages, cols=[excluded=0, retained=1]

        # Step 4: Cramér's V
        v = association(contingency.values, method='cramer')

        # Step 5: Chi-square p-value (for Holm correction across k values)
        chi2, p, _, _ = chi2_contingency(contingency.values)

        # Step 6: Per-language retention rates
        retention = (
            df.groupby('language')['retained'].mean()
            .reindex(languages)
        )

        results[k] = {
            'threshold': threshold,
            'cramers_v': v,
            'chi2': chi2,
            'p_value': p,
            'retention_rates': retention.to_dict()
        }

    return results

# After computing all k values, apply Holm-Bonferroni correction:
# from statsmodels.stats.multitest import multipletests
# p_values = [results[k]['p_value'] for k in k_values]
# reject, p_corrected, _, _ = multipletests(p_values, method='holm')
```

### Training Protocol

**No ML training involved.** This is a pure statistical analysis.

**Execution Protocol:**

- **Script:** `code/run_h_e1.py`
- **Runtime:** CPU-only, <5 minutes (mostly dataset load time)
- **Seed:** 42 (fixed, for any bootstrap operations)
- **k values:** {10, 20, 30, 40, 50}
- **Dependencies:**
  - `pandas>=1.5` — DataFrame operations, groupby, crosstab
  - `scipy>=1.7` — `scipy.stats.contingency.association` (Cramér's V)
  - `numpy>=1.21` — array ops
  - `datasets>=2.0` — HuggingFace dataset loading
  - `statsmodels>=0.13` — Holm-Bonferroni correction (`multipletests`)

**Execution steps:**
1. Load/cache dataset → flat DataFrame `[language, ccnet_perplexity]`
2. Validate: 208,263 rows, 5 languages, no NaN in ccnet_perplexity
3. For each k ∈ {10, 20, 30, 40, 50}: compute global threshold → contingency → Cramér's V
4. Apply Holm-Bonferroni correction to 5 p-values
5. Compute per-language retention rates and max–min gap
6. Write results to JSON + generate figures
7. Apply gate check: all V ∈ [0.29, 0.41] AND all Holm-p ≈ 0

### Evaluation

**Primary Metrics:**

| Metric | Definition | Expected Value (from Phase 2B baseline) |
|--------|-----------|------------------------------------------|
| Cramér's V (k=10) | Association strength, 5×2 contingency | ~0.29 |
| Cramér's V (k=20) | " | ~0.33 |
| Cramér's V (k=30) | " | ~0.37 |
| Cramér's V (k=40) | " | ~0.40 |
| Cramér's V (k=50) | " | ~0.41 |
| Holm-corrected p (all k) | Multiple comparison corrected | ≈ 0 |
| English retention (k=30) | % English docs retained | ~36.5% |
| Italian retention (k=30) | % Italian docs retained | ~88.1% |
| Max–min gap (k=30) | max(retention_l) - min(retention_l) | ~51.6pp |

**Success Criteria (PoC):**
1. Data loads successfully: 208,263 rows, 5 languages present
2. `ccnet_perplexity` column populated (no NaN > 1%)
3. Cramér's V ∈ [0.29, 0.41] for all 5 k values
4. Holm-corrected p < 0.001 for all 5 k values

**Gate pass = ALL 4 criteria satisfied**

**Expected Baseline Performance:**
- V range 0.29–0.41 (previously observed, per Phase 2B)
- English most excluded (lowest perplexity → most documents above threshold)
- Italian least excluded (highest baseline perplexity → fewer documents above threshold)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: scipy.stats.contingency + statsmodels
- Code:
  ```python
  from scipy.stats.contingency import association, chi2_contingency
  from statsmodels.stats.multitest import multipletests
  v = association(contingency_table, method='cramer')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Cramér's V per k value vs. expected range [0.29, 0.41]
  - x-axis: k values {10, 20, 30, 40, 50}
  - y-axis: Cramér's V
  - Reference lines: 0.29 (lower bound) and 0.41 (upper bound)
  - Color: green bars within range, red bars outside range

#### Additional Figures (LLM Autonomous)
1. **Per-language retention rate heatmap** — languages × k values, retention rate as color
   - Shows the disparity pattern visually
2. **Perplexity distribution per language** — overlaid KDE plots, 5 languages
   - Explains WHY global threshold creates disparity (different distributions)
3. **Max–min retention gap vs k** — line chart showing gap at each k value
   - Context for h-c2 (≥15pp reduction target)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All Cramér's V values ∈ [0.29, 0.41]
3. All Holm-corrected p-values < 0.001

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Global percentile threshold is computable on pandas DataFrame | TRUE — pandas quantile is stdlib |
| Mechanism Isolatable | Baseline (global) vs. treatment (per-language) are distinct code paths | TRUE — separate functions |
| Baseline Measurable | Global threshold produces measurable per-language retention rates | TRUE — `df.groupby('language')['retained'].mean()` |

### Architecture Compatibility Check

No ML architecture involved. Statistical pipeline only.

**Required Features:**
- pandas DataFrame with `language` (str) and `ccnet_perplexity` (float) columns
- scipy >= 1.7 (for `contingency.association` method='cramer')
- statsmodels (for Holm correction)

**Incompatible Configurations:**
- Dataset with < 5 languages → contingency table shape mismatch
- Missing `ccnet_perplexity` field → KeyError at threshold computation

> ⚠️ Phase 4 MUST validate column presence and language count before proceeding.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"Loaded 208263 rows, 5 languages"` | data_loader.py:load() |
| Shape Check | `contingency.shape == (5, 2)` for all k | analysis.py:compute_contingency() |
| Metric Delta | V ∈ [0.29, 0.41] — nonzero effect proves mechanism activates | analysis.py:compute_disparity() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(df, results, k_values):
    indicators = {
        "data_loaded": len(df) == 208263,
        "five_languages": df['language'].nunique() == 5,
        "no_nan_perplexity": df['ccnet_perplexity'].isna().mean() < 0.01,
        "disparity_nonzero": all(
            results[k]['cramers_v'] > 0.10 for k in k_values
        ),
        "disparity_in_range": all(
            0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values
        )
    }
    activated = all(indicators.values())
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Dataset not found | `load_dataset` throws or returns 0 rows | FAIL: re-download from HuggingFace |
| Wrong row count | `len(df) != 208263` (±5% tolerance) | WARN: log difference, continue if >190000 |
| ccnet_perplexity missing | KeyError on quality_signals parse | FAIL: dataset schema changed |
| V < 0.10 all k | Gate violation | FAIL: pipeline regression, block downstream |
| V > 0.45 any k | Unexpected — possible data contamination | WARN: investigate |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | All 5 indicators in verify_mechanism_activated() |
| Effect Measurable | V > 0.10 for all k | Cramér's V computation |
| Hypothesis Supported | V ∈ [0.29, 0.41] for all 5 k values | scipy.stats.contingency.association |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No domain-relevant sources found in Archon KB. KB is populated with diffusion model
and vision content — not applicable to text quality filtering experiments.

### B. GitHub Implementations (Exa)

**Repository 1: togethercomputer/RedPajama-Data** (⭐ 4947)
- **URL:** https://github.com/togethercomputer/redpajama-data
- **Query Used:** "RedPajama quality signals ccnet_perplexity language filtering pandas Python"
- **Relevance:** Official dataset source — schema, loading API, quality signal structure
- **Key Code** (annotated):
  ```python
  # Official loading pattern (from HuggingFace README):
  from datasets import load_dataset
  ds = load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")
  # Sample = 208,263 docs across 5 languages with quality_signals
  
  # Quality signal extraction pattern (from blog post):
  def gopher_rules_pass(sample) -> bool:
      signals = json.loads(sample["quality_signals"])
      # ccnet_perplexity accessed as: signals["ccnet_perplexity"][0][2]
      # Format: [(start, end, value)] — document-level signal = [0][2]
  ```
- **Configuration Extracted:** `name="sample"` for 208,263-doc subset
- **Used For:** Dataset loading code, quality signal schema

**Repository 2: rakseli/redpajama-v2-processing**
- **URL:** https://github.com/rakseli/redpajama-v2-processing
- **Query Used:** "RedPajama quality signals ccnet_perplexity language filtering pandas Python"
- **Relevance:** Real per-language percentile filtering pipeline — validates hypothesis setup
- **Key Insight:**
  Used stricter percentile filters for English (p=0.02) vs. other languages (p=0.05),
  confirming that English requires different thresholds than other languages.
  This directly supports the hypothesis that global thresholds create language disparity.
- **Used For:** Confirms that per-language adaptive thresholds are the correct approach;
  validates that global threshold is the non-standard, biased alternative we measure.

**Repository 3: facebookresearch/cc_net**
- **URL:** https://github.com/facebookresearch/cc_net
- **Query Used:** "CCNet perplexity threshold multilingual filtering language disparity"
- **Relevance:** Original perplexity computation — explains cross-language incomparability
- **Key Insight:**
  CCNet's `pp()` function: `10.0 ** (-log_score / length)` — trained on language-specific
  Wikipedia corpora. English Wikipedia is ~6× larger than Italian → English model is
  better calibrated → English text scores lower perplexity than equivalent-quality
  Italian text → global threshold systematically excludes more English.
- **Used For:** Root-cause justification for why global threshold creates disparity

**Repository 4: scipy documentation**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html
- **Query Used:** "scipy contingency association Cramér V language retention bias bootstrap pandas"
- **Key Code:**
  ```python
  from scipy.stats.contingency import association
  # observed: 2D array — contingency table (rows=categories, cols=outcomes)
  v = association(observed, method='cramer')
  # Returns float in [0, 1]; 0=independence, 1=perfect association
  ```
- **Used For:** Primary metric computation (Cramér's V)

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results was sufficiently clear.
Statistical pipeline (~50 lines pandas/scipy) has no complex architecture.

### D. Previous Hypothesis Context

This is the first sub-hypothesis. No prior hypothesis context.

**Note:** An unrelated archived h-e1 exists at `docs/youra_research/_archive/` from
a prior pipeline iteration (MMLU contamination study) — this is NOT a predecessor.
Phase 4 must NOT inherit any code from that archive.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (RedPajama-V2 sample) | GitHub/HuggingFace | B.1 (togethercomputer/RedPajama-Data) |
| quality_signals schema | GitHub | B.1 (official README) |
| ccnet_perplexity extraction | GitHub | B.1 (gopher_rules_pass pattern) |
| Per-language threshold rationale | GitHub | B.2 (rakseli/redpajama-v2-processing) |
| Perplexity incomparability root cause | GitHub | B.3 (facebookresearch/cc_net, pp() function) |
| Global threshold formula | Phase 2B | 02b_verification_plan.md Section 2.5 |
| Cramér's V computation | Scipy docs | B.4 (scipy.stats.contingency.association) |
| k values {10,20,30,40,50} | Phase 2B | 02b_verification_plan.md Section 2.5 |
| Expected V range [0.29,0.41] | Phase 2B | 02b_verification_plan.md h-e1 success criterion |
| Holm correction | statsmodels | stdlib (multipletests) |

---

## State Information

**State File:** verification_state.yaml (managed by pipeline harness)
**Date:** 2026-07-30

### Workflow History for This Hypothesis
- 2026-07-30: h-e1 set to IN_PROGRESS (external hypothesis loop)
- 2026-07-30: Phase 2C experiment design — IN_PROGRESS
- 2026-07-30: Phase 2C experiment design — COMPLETED

---

*MCP Tools Used: Archon (no relevant results), Exa (GitHub + web search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
