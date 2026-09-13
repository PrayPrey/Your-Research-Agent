# Experiment Design: h-e1-v3

**Date:** 2026-07-30
**Author:** Anonymous
**Hypothesis Statement:** Global k-th percentile thresholding on RedPajama-V2 ccnet_perplexity produces statistically significant language-group retention disparity (Cramér's V = 0.29–0.41, Holm p ≈ 0 for all 5 k values).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)
**Version:** 3 (SELF_MODIFY — re-run of h-e1 existence baseline)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1-v3
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None (first in chain)
- **Version:** 3 (SELF_MODIFY from h-e1 — same hypothesis, modified implementation approach)

### Gate Condition
MUST_WORK: Cramér's V ∈ [0.29, 0.41] for k ∈ {10, 20, 30, 40, 50} using global percentile threshold on the 208,263-row RedPajama-V2 sample. V < 0.10 or data load failure = gate violation, blocks h-m1/h-c1/h-c2/h-m2.

---

## Continuation Context

h-e1-v3 is a SELF_MODIFY version of h-e1. The hypothesis statement is identical.
The modification attempt (version 3) reflects a pipeline restart after prior iteration.

**Lessons from h-e1 (v1/v2):**
- Parquet cache exists at `docs/youra_research/redpajama_sample.parquet` — confirmed present
- quality_signals schema: `signals["ccnet_perplexity"][0][2]` (start, end, score tuple)
- Dataset load via HuggingFace `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
- Phase 4 MUST detect and reuse Parquet cache; re-download only if cache is corrupted
- Phase 4 must NOT inherit code from `docs/youra_research/_archive/` (unrelated MMLU study)

### Previous Hypothesis Results (if applicable)
h-e1 (v1): Existence baseline — same hypothesis. Results: gate passed (V ∈ [0.29, 0.41]).
Parquet cache from that run is available at `docs/youra_research/redpajama_sample.parquet`.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Assessment:** Archon KB returned no domain-relevant results for this hypothesis (similarity scores 0.31–0.36, all unrelated — vision/CUDA/diffusion model content).
No Archon findings applicable to text quality filtering or statistical disparity analysis.

**Queries executed:**
1. `"perplexity threshold language filtering bias"` → top result: OpenAI instruction-following blog (similarity 0.36) — irrelevant
2. `"Cramér's V contingency table statistical disparity"` → top result: Wikipedia binocular disparity (similarity 0.38) — irrelevant
3. `"pandas groupby contingency chi2 Cramér V"` (code search) → top result: cuBLAS GEMM — irrelevant

**Conclusion:** KB is populated with vision/GPU content only. All implementation details sourced from Exa.

### Archon Code Examples

No relevant code examples found in Archon KB.

### Exa GitHub Implementations

**Source 1: together.ai/blog/redpajama-data-v2**
- **URL:** https://www.together.ai/blog/redpajama-data-v2
- **Relevance:** Official RedPajama-V2 announcement — quality signal schema, CCNet pipeline description
- **Key schema:**
  ```python
  # quality_signals is a dict of {signal_name: [(start, end, score)]}
  # Document-level ccnet_perplexity accessed as:
  signals = json.loads(sample["quality_signals"])
  perplexity = signals["ccnet_perplexity"][0][2]  # (start=0, end=doc_len, score=value)
  ```
- **Key insight:** ccnet_perplexity = perplexity of Wikipedia-trained LM per language.
  CCNet splits data into head/middle/tail buckets; sample split = head+middle documents.

**Source 2: huggingface.co/datasets/togethercomputer/RedPajama-Data-V2 (README)**
- **URL:** https://huggingface.co/datasets/togethercomputer/RedPajama-Data-V2
- **Relevance:** Official HuggingFace dataset card — loading API and quality signal format
- **Loading pattern:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")
  ```
- **Signal schema confirmed:** `[(start, end, score)]` tuples; document-level = `[0][2]`

**Source 3: github.com/togethercomputer/RedPajama-Data**
- **URL:** https://github.com/togethercomputer/RedPajama-Data
- **Relevance:** Official repository — pipeline, quality signal computation
- **Key annotation fields confirmed:**
  - `ccnet_bucket`: head/middle/tail perplexity bucket
  - `ccnet_language_score`: LID model confidence
  - `ccnet_perplexity`: Wikipedia LM perplexity (core signal for this experiment)

**Source 4: docs.scipy.org — scipy.stats.contingency.association**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html
- **Relevance:** Primary metric implementation — Cramér's V via scipy
- **Key code:**
  ```python
  from scipy.stats.contingency import association
  # observed: 2D array (n_categories × n_outcomes) — our case: (5 languages × 2 retained/excluded)
  v = association(observed, method='cramer')
  # Returns float [0, 1]; 0 = independence, 1 = perfect association
  ```
- **Note from application-architect.com source:** With N=208,263 rows, bias correction is unnecessary (large-sample regime). Standard Cramér's V is appropriate. Bias correction recommended only for N < 100 or sparse tables.

**Source 5: github.com/scipy/scipy — contingency.py**
- **URL:** https://github.com/scipy/scipy/blob/main/scipy/stats/contingency.py
- **Cramér's V formula confirmed:**
  ```python
  phi2 = chi2 / n
  v = sqrt(phi2 / min(n_rows - 1, n_cols - 1))
  # For our 5×2 table: min(5-1, 2-1) = 1 → V = sqrt(phi2)
  ```

**Serena Analysis Needed:** False — pure pandas/scipy pipeline, no complex ML architecture.

### 🎯 Implementation Priority Assessment

This is NOT a paper-reproduction experiment. Original statistical analysis of pre-computed quality signals.

**No author implementation to follow.** The mechanism is novel:
- Apply global k-th percentile threshold to `ccnet_perplexity`
- Compute Cramér's V on resulting 5×2 contingency table (language × retained/excluded)

**Recommended Implementation Path:**
- Primary: Custom pandas + scipy implementation (the only correct approach)
- Fallback: N/A — no existing implementation to fall back to
- Justification: Standard statistical pipeline; scipy provides Cramér's V directly;
  pandas groupby handles per-language retention rate computation.
  Parquet cache available → skip HuggingFace download if cache valid.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results is sufficiently clear. Statistical pipeline (~50 lines
pandas/scipy) has no complex architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** RedPajama-Data-V2 (sample split)
**Type:** standard (programmatic-api via HuggingFace datasets)
**Source:** `togethercomputer/RedPajama-Data-V2`
**Split:** `sample` (pre-built 208,263-document subset, 5 languages)
**Languages:** en, de, fr, es, it
**Key Fields:**
- `ccnet_perplexity` (float): Wikipedia LM perplexity extracted from `quality_signals` JSON
- `language` (str): language tag {en, de, fr, es, it}
**Size:** 208,263 documents

**Preprocessing:**
1. Check for Parquet cache at `docs/youra_research/redpajama_sample.parquet`
2. If cache valid (≥190,000 rows, columns `[language, ccnet_perplexity]`): load directly
3. Else: `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`
4. Parse `quality_signals` JSON → extract `ccnet_perplexity` = `signals["ccnet_perplexity"][0][2]`
5. Extract `language` from `metadata["language"]`
6. Drop rows where `ccnet_perplexity` is None/NaN (expected < 1%)
7. Save cleaned DataFrame as Parquet for future runs

**Cache strategy:** `docs/youra_research/redpajama_sample.parquet` (already exists from h-e1 run)

**Expected distribution:**
- English: largest group, lowest perplexity median (large English Wikipedia → well-calibrated LM)
- Italian: highest perplexity baseline (smaller Italian Wikipedia → less calibrated LM)
- Cross-language perplexity ranges differ substantially → root cause of global threshold bias

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (with Parquet cache fallback)
- Identifier: `"togethercomputer/RedPajama-Data-V2"`
- Code: `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")`

### Models

#### Baseline Model

**Architecture:** No ML model — CPU-only statistical analysis
**Baseline "model":** Global k-th percentile threshold on ccnet_perplexity

For k ∈ {10, 20, 30, 40, 50}:
- Threshold: k-th percentile of ALL documents (pooled across all 5 languages)
- Retention rule: `retained = df['ccnet_perplexity'] < threshold_k`
- Output: per-language retention rates, 5×2 contingency table, Cramér's V

**Loading Information** (for Phase 4 download):
- Method: stdlib (pandas, scipy, numpy — no download needed)
- Identifier: N/A
- Code: `import pandas as pd; from scipy.stats.contingency import association`

#### Proposed Model

**Architecture:** Baseline statistical pipeline (no change for h-e1-v3)

h-e1-v3 IS the baseline — it measures global threshold disparity.
The "proposed model" (per-language threshold) is tested in h-m1, not here.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Global k-th Percentile Threshold Disparity Measurement
# Based on: RedPajama-V2 official docs (togethercomputer/RedPajama-Data-V2)
# Source: scipy.stats.contingency.association (Cramér's V), Exa/scipy docs

import pandas as pd
import numpy as np
from scipy.stats.contingency import association
from scipy.stats import chi2_contingency

def compute_global_threshold_disparity(df: pd.DataFrame, k_values: list) -> dict:
    """
    Args:
        df: DataFrame with columns ['language', 'ccnet_perplexity']
            shape: (208263,) — full RedPajama-V2 sample
        k_values: list of percentile values, e.g. [10, 20, 30, 40, 50]
    Returns:
        dict mapping k → {cramers_v, p_value, retention_rates, threshold}
    """
    results = {}
    languages = sorted(df['language'].unique())  # ['de', 'en', 'es', 'fr', 'it']

    for k in k_values:
        # Step 1: Global threshold — pooled across all 5 languages
        threshold = df['ccnet_perplexity'].quantile(k / 100)

        # Step 2: Binary retain/exclude label
        retained = (df['ccnet_perplexity'] < threshold).astype(int)

        # Step 3: 5×2 contingency table (language × retained)
        contingency = pd.crosstab(df['language'], retained)
        # Shape: (5, 2) — rows=languages, cols=[excluded=0, retained=1]

        # Step 4: Cramér's V (measures language-retention association strength)
        v = association(contingency.values, method='cramer')

        # Step 5: Chi-square p-value (for Holm correction across 5 k values)
        chi2, p, _, _ = chi2_contingency(contingency.values)

        # Step 6: Per-language retention rates
        retention = df.assign(retained=retained).groupby('language')['retained'].mean()

        results[k] = {
            'threshold': threshold,
            'cramers_v': round(v, 4),
            'chi2': round(chi2, 2),
            'p_value': p,
            'retention_rates': retention.reindex(languages).to_dict(),
            'max_min_gap': retention.max() - retention.min()
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

- **Script:** `code/run_h_e1_v3.py`
- **Runtime:** CPU-only, <5 minutes (cache hit: <30 seconds; cache miss: ~3 minutes for HuggingFace download)
- **Seed:** 42 (fixed, for reproducibility of any bootstrap operations)
- **k values:** {10, 20, 30, 40, 50}
- **Dependencies:**
  - `pandas>=1.5` — DataFrame operations, groupby, crosstab
  - `scipy>=1.7` — `scipy.stats.contingency.association` (Cramér's V), `chi2_contingency`
  - `numpy>=1.21` — array operations
  - `datasets>=2.0` — HuggingFace dataset loading (only if cache miss)
  - `statsmodels>=0.13` — Holm-Bonferroni correction (`multipletests`)

**Execution steps:**
1. Check Parquet cache → load if valid, else download from HuggingFace
2. Validate: ≥190,000 rows, 5 languages, < 1% NaN in ccnet_perplexity
3. For each k ∈ {10, 20, 30, 40, 50}: compute global threshold → contingency → Cramér's V
4. Apply Holm-Bonferroni correction to 5 p-values
5. Compute per-language retention rates and max–min gap at k=30
6. Write results to `results.json` and `experiment_results.json`
7. Generate figures (see Visualization Requirements)
8. Apply gate check: all V ∈ [0.29, 0.41] AND all Holm-p < 0.001

### Evaluation

**Primary Metrics:**

| Metric | Definition | Expected Value (from Phase 2B baseline) |
|--------|-----------|------------------------------------------|
| Cramér's V (k=10) | Association strength, 5×2 contingency | ~0.29 |
| Cramér's V (k=20) | " | ~0.33 |
| Cramér's V (k=30) | " | ~0.37 |
| Cramér's V (k=40) | " | ~0.40 |
| Cramér's V (k=50) | " | ~0.41 |
| Holm-corrected p (all k) | Multiple comparison corrected | ≈ 0 (< 0.001) |
| English retention (k=30) | % English docs retained | ~36.5% |
| Italian retention (k=30) | % Italian docs retained | ~88.1% |
| Max–min gap (k=30) | max(retention_l) - min(retention_l) | ~51.6pp |

**Success Criteria (PoC):**
1. Data loads successfully: ≥190,000 rows, all 5 languages present
2. `ccnet_perplexity` column populated (< 1% NaN)
3. Cramér's V ∈ [0.29, 0.41] for all 5 k values
4. Holm-corrected p < 0.001 for all 5 k values

**Gate pass = ALL 4 criteria satisfied**

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: scipy.stats.contingency + statsmodels
- Code:
  ```python
  from scipy.stats.contingency import association
  from scipy.stats import chi2_contingency
  from statsmodels.stats.multitest import multipletests
  v = association(contingency_table, method='cramer')
  chi2, p, dof, expected = chi2_contingency(contingency_table)
  reject, p_holm, _, _ = multipletests([p1, p2, p3, p4, p5], method='holm')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Cramér's V per k value vs. expected range [0.29, 0.41]
  - x-axis: k values {10, 20, 30, 40, 50}
  - y-axis: Cramér's V (0.0–0.5)
  - Reference lines: 0.29 (lower bound, dashed green) and 0.41 (upper bound, dashed green)
  - Color: green bars within range [0.29, 0.41], red bars outside range
  - Save to: `docs/youra_research/h-e1-v3/figures/gate_metrics.png`

#### Additional Figures (LLM Autonomous)
1. **Per-language retention rate heatmap** — languages × k values, retention rate as color intensity
   - Shows disparity pattern across all conditions
2. **Perplexity distribution per language** — overlaid KDE plots, 5 languages
   - Explains WHY global threshold creates disparity (different distribution shapes)
3. **Max–min retention gap vs k** — line chart
   - Context for h-c2 (≥15pp reduction target at k=30)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-e1-v3/figures/`.

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
| Mechanism Exists | Global percentile threshold computable on pandas DataFrame | TRUE — pandas quantile is stdlib |
| Mechanism Isolatable | Baseline (global) vs. treatment (per-language) are distinct code paths | TRUE — separate functions |
| Baseline Measurable | Global threshold produces measurable per-language retention rates | TRUE — `df.groupby('language')['retained'].mean()` |

### Architecture Compatibility Check

No ML architecture involved. Pure statistical pipeline.

**Required Features:**
- pandas DataFrame with `language` (str) and `ccnet_perplexity` (float) columns
- scipy >= 1.7 (for `contingency.association` with method='cramer')
- statsmodels (for Holm-Bonferroni correction via `multipletests`)
- Parquet cache at `docs/youra_research/redpajama_sample.parquet` (already confirmed present)

**Incompatible Configurations:**
- Dataset with < 5 languages → contingency table shape mismatch (5×2 assumed)
- Missing `ccnet_perplexity` field → KeyError at threshold computation
- `scipy < 1.7` → `contingency.association` not available (method='cramer' added in 1.7)

> ⚠️ Phase 4 MUST validate column presence and language count before proceeding.
> ⚠️ Phase 4 MUST use Parquet cache; re-download from HuggingFace only if cache invalid.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"Loaded 208263 rows, 5 languages"` | data_loader.py:load() |
| Shape Check | `contingency.shape == (5, 2)` for each k | analysis.py:compute_contingency() |
| Metric Delta | V ∈ [0.29, 0.41] — nonzero effect proves mechanism activates | analysis.py:compute_disparity() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(df, results, k_values):
    indicators = {
        "data_loaded": len(df) >= 190_000,
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
| Cache corrupted | Row count < 190,000 on load | WARN + re-download from HuggingFace |
| Wrong row count after download | `len(df) < 190,000` | FAIL: dataset access issue |
| ccnet_perplexity missing | KeyError on quality_signals parse | FAIL: dataset schema changed |
| V < 0.10 for all k | Gate violation | FAIL: pipeline regression, block downstream |
| V > 0.45 for any k | Unexpected result | WARN: investigate data contamination |
| scipy version mismatch | AttributeError on `association` | FAIL: upgrade scipy to >= 1.7 |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | All 5 indicators in verify_mechanism_activated() |
| Effect Measurable | V > 0.10 for all k | Cramér's V computation |
| Hypothesis Supported | V ∈ [0.29, 0.41] for all 5 k values | scipy.stats.contingency.association |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No domain-relevant sources found in Archon KB across 3 queries (2 knowledge + 1 code).
KB contains vision/diffusion/CUDA content — not applicable to text quality filtering.

### B. GitHub Implementations (Exa)

**Repository 1: togethercomputer/RedPajama-Data** (official)
- **URL:** https://github.com/togethercomputer/RedPajama-Data
- **Query Used:** "RedPajama V2 ccnet_perplexity quality signals pandas filtering language retention"
- **Relevance:** Official repository — quality signal schema, pipeline, ccnet_perplexity definition
- **Key Code** (annotated):
  ```python
  # Official quality signal access pattern (from HuggingFace README):
  signals = json.loads(sample["quality_signals"])
  # ccnet_perplexity accessed as: signals["ccnet_perplexity"][0][2]
  # Format: [(start_char, end_char, value)] — document-level = index [0], value = [2]
  ```
- **Used For:** Dataset loading code, quality signal schema, ccnet_perplexity extraction

**Repository 2: together.ai/blog/redpajama-data-v2** (official blog)
- **URL:** https://www.together.ai/blog/redpajama-data-v2
- **Query Used:** "RedPajama V2 ccnet_perplexity quality signals pandas filtering language retention"
- **Relevance:** CCNet pipeline description; explains perplexity as Wikipedia LM score per language
- **Key insight:** CCNet trains language-specific KenLM models on Wikipedia. Corpus size varies
  by language → English model best calibrated → English text scores lower perplexity →
  global threshold systematically excludes more English. Root-cause confirmation.
- **Used For:** Root-cause justification for why global threshold creates disparity

**Repository 3: scipy/scipy — contingency.py**
- **URL:** https://github.com/scipy/scipy/blob/main/scipy/stats/contingency.py
- **Query Used:** "scipy contingency association Cramers V multilingual corpus perplexity threshold"
- **Relevance:** Primary metric implementation — Cramér's V formula and scipy API
- **Key Code:**
  ```python
  from scipy.stats.contingency import association
  # For 5×2 table: min(n_rows-1, n_cols-1) = min(4,1) = 1
  # V = sqrt(chi2 / (n * 1)) = sqrt(phi2) — simplified for 2-column tables
  v = association(observed, method='cramer')
  ```
- **Used For:** Primary metric (Cramér's V), pseudo-code generation

**Reference 4: application-architect.com — Cramér's V bias correction**
- **URL:** https://www.application-architect.com/posts/how-to-calculate-cram%C3%A9rs-v-in-python/
- **Query Used:** "scipy contingency association Cramers V multilingual corpus perplexity threshold"
- **Key insight:** With N=208,263 rows, bias correction is unnecessary.
  Standard Cramér's V is appropriate (bias correction needed only for N < 100 or sparse tables).
- **Used For:** Justification for NOT using bias-corrected V in experiment

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results was sufficiently clear.
Statistical pipeline (~50 lines pandas/scipy) has no complex architecture.

### D. Previous Hypothesis Context

**Source:** h-e1 (v1) — same hypothesis, prior pipeline iteration
- Parquet cache confirmed present at `docs/youra_research/redpajama_sample.parquet`
- h-e1/04_validation.md confirmed gate pass (V ∈ [0.29, 0.41])
- h-e1/02c_experiment_brief.md confirmed quality signal schema and loading approach
- **Reused:** Dataset schema, loading approach, metric computation
- **Modified:** Output paths now use `h-e1-v3/` prefix; script renamed `run_h_e1_v3.py`

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (RedPajama-V2 sample) | GitHub + HuggingFace | B.1 (togethercomputer/RedPajama-Data) |
| quality_signals schema | Blog/official docs | B.2 (together.ai blog) |
| ccnet_perplexity extraction | GitHub | B.1 (`signals["ccnet_perplexity"][0][2]`) |
| Cross-language bias root cause | Blog | B.2 (Wikipedia LM size differences) |
| Global threshold formula | Phase 2B | 02b_verification_plan.md §h-e1 |
| Cramér's V computation | scipy docs | B.3 (scipy.stats.contingency.association) |
| Bias correction decision | Reference | B.4 (N=208,263 → no correction needed) |
| k values {10,20,30,40,50} | Phase 2B | 02b_verification_plan.md §h-e1 |
| Expected V range [0.29,0.41] | Phase 2B | 02b_verification_plan.md h-e1 success criterion |
| Holm correction | statsmodels | stdlib (multipletests, method='holm') |
| Parquet cache path | Previous run | h-e1 experiment (docs/youra_research/redpajama_sample.parquet) |

---

## State Information

**State File:** verification_state.yaml (managed by pipeline harness — ABLATION MODE)
**Date:** 2026-07-30

### Workflow History for This Hypothesis
- 2026-07-30T07:29:11: h-e1-v3 set to IN_PROGRESS (external hypothesis loop)
- 2026-07-30: Phase 2C experiment design — IN_PROGRESS
- 2026-07-30: Phase 2C experiment design — COMPLETED

---

*MCP Tools Used: Archon (no relevant results — 3 queries), Exa (GitHub + web search — 2 queries)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
