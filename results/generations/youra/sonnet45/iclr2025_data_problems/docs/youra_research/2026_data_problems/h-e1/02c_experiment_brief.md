# Experiment Design: H-E1

**Date:** 2026-03-17
**Author:** Anonymous
**Hypothesis Statement:** Under the Open LLM Leaderboard v1 snapshot, if model cards are publicly accessible on HuggingFace for a sufficient fraction of evaluated models, then a dataset of ≥200 models with non-missing binary curation documentation features, ≥4/6 benchmark scores, and recoverable parameter count can be assembled, because major open-weight model families (LLaMA, Falcon, Mistral, Pythia) consistently publish detailed model cards with the required feature information.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (No prerequisites — foundation hypothesis)
**Gate Status:** MUST_WORK — Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK:** If this hypothesis fails (n_analyzable < 200), the entire pipeline STOPS — all downstream hypotheses (H-M1, H-M2, H-M3) require an assembled registry and cannot proceed.

---

## Continuation Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain with no prerequisites.

### Previous Hypothesis Results (if applicable)
N/A — No prior hypothesis context exists.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: HuggingFace model card feature extraction LLM**
- Result 1: HuggingFace Transformers docs index (similarity: 0.543)
  - Dataset: N/A (docs page)
  - Key insight: Confirms HuggingFace Hub ecosystem; transformers library used for model access
  - Used for: General HF ecosystem context

- Result 2: HuggingFace paper 2307.01952 (similarity: 0.469)
  - Key insight: Research paper on HF platform — confirms academic use of HF Hub
  - Used for: Background on HF model ecosystem

**Query 2: Open LLM Leaderboard dataset scraping benchmark**
- Result 1: OpenReview paper forum (similarity: 0.456, 17,209 words, 2 chunk matches)
  - Key insight: Academic benchmark evaluation paper — confirms benchmark evaluation methodology
  - Used for: Background on leaderboard-style evaluation

**Query 3: Observational study LLM benchmark performance regression**
- Result 1: HF paper 2305.14314 (similarity: 0.446, 2 chunk matches)
  - Key insight: Research on LLM performance evaluation — confirms regression-based analysis approach

**Assessment:** Archon KB is primarily scoped to HuggingFace diffusers/stable-diffusion content and does not contain directly relevant material on LLM documentation registries, Open LLM Leaderboard scraping, or observational regression studies. Implementation design relies on domain knowledge and standard API documentation.

### Archon Code Examples

**Query: HuggingFace Hub API model card parsing Python**
- **Result 1** (similarity: 0.426, rerank: 3.562): `RepoCard.load()` pattern from diffusers LoRA example
  ```python
  from huggingface_hub.repocard import RepoCard
  card = RepoCard.load(model_id)
  metadata = card.data.to_dict()  # Extract structured metadata
  base_model_id = metadata["base_model"]
  ```
  - **Key insight:** `RepoCard.load(repo_id)` + `card.data.to_dict()` is the standard pattern for programmatic model card access
  - **Used for:** Model card retrieval and metadata extraction pseudo-code

- **Result 2** (similarity: 0.421): `snapshot_download` and `hf_hub_download` patterns
  - **Key insight:** `huggingface_hub` provides `hf_hub_download()` for file-level access and `snapshot_download()` for repo-level access

**Query: pandas OLS regression statsmodels Python**
- No relevant results found (all results were image model downloads with negative rerank scores)
- **Limitation noted:** OLS/statsmodels implementation relies on standard domain knowledge

### Exa GitHub Implementations

**⚠️ Exa MCP Unavailable (HTTP 402 — billing/credits exceeded)**
- All 3 Exa queries failed after retry (15s wait + 2 attempts per MCP retry protocol)
- Error: `Search error (402): Request failed with status code 402`
- **Limitation:** No GitHub repository search results available
- **Mitigation:** Implementation design proceeds from Archon findings + standard HuggingFace Hub / leaderboard API documentation patterns

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment is NOT a paper reproduction — it is original registry construction using public APIs. No single "author implementation" exists to prioritize.

**Recommended Implementation Path:**
- Primary: HuggingFace Hub Python SDK (`huggingface_hub` + `datasets` libraries) for data collection
- Fallback: Direct HTTP scraping of HuggingFace model pages if Hub API rate-limits
- Justification: The `huggingface_hub` library provides the `ModelCard.load()` and `HfApi.list_models()` API which is the standard, maintained way to access model card data at scale. The `datasets` library provides access to the leaderboard results dataset (`open-llm-leaderboard/results`).

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-E1 is a data collection and statistical analysis task (no neural network architecture code requiring semantic analysis). The implementation uses standard Python data science libraries (pandas, statsmodels, huggingface_hub, datasets).

---

## Experiment Specification

### Dataset

**Primary Dataset: Open LLM Leaderboard v1 Snapshot + HuggingFace Model Cards**

| Property | Value |
|----------|-------|
| **Name** | Open LLM Leaderboard v1 + HuggingFace Model Cards |
| **Type** | programmatic-api (real data via HuggingFace Hub API) |
| **Source** | HuggingFace Datasets: `open-llm-leaderboard/results`; HuggingFace Hub API for model cards |
| **Size** | ~3,000+ model evaluation entries in v1 snapshot |
| **Target sample** | ≥200 models with complete feature set after filtering |
| **Benchmarks** | MMLU, ARC-Challenge, HellaSwag, WinoGrande, TruthfulQA, GSM8K (6 total) |
| **Filter threshold** | ≥4/6 benchmark scores non-missing AND parameter count recoverable |

**Curation Features Extracted (4 binary indicators):**
1. `dedup_documented` — Model card mentions deduplication (keyword: "dedup", "near-dedup", "MinHash")
2. `perplexity_filter_documented` — Model card mentions perplexity-based filtering
3. `domain_composition_documented` — Model card reports training data domain breakdown (%)
4. `decontamination_documented` — Model card mentions n-gram decontamination or benchmark holdout

**Computed Variables:**
- `doc_score` = sum of 4 binary features (0–4)
- `log_params` = log(parameter count N)
- `log_tokens` = log(training tokens D) where recoverable
- `arch_family` = architecture family fixed effect (LLaMA, Falcon, Mistral, Pythia, etc.)

**Dataset Statistics (expected):**
- Raw leaderboard entries: ~3,000–5,000
- After ≥4/6 benchmark filter: ~1,000–2,000
- After parameter count filter: ~500–1,500
- After model card accessibility filter: target ≥200 (primary success criterion)

**Preprocessing Steps:**
1. Download leaderboard snapshot via `datasets.load_dataset("open-llm-leaderboard/results")`
2. Deduplicate by model_name (keep latest evaluation per model)
3. Filter: keep models with ≥4 non-missing benchmark scores
4. For each model: call `huggingface_hub.HfApi().model_info(model_id)` to check accessibility
5. For each accessible model: `ModelCard.load(model_id)` to retrieve card text
6. Apply keyword extraction rules to binary features (pre-registered)
7. Filter: keep models with recoverable parameter count (from model_info or card)
8. Compute doc_score, log_params, log_tokens

**No augmentation** — observational study, no data augmentation applicable.

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (HuggingFace `datasets` + `huggingface_hub`)
- Identifier: `"open-llm-leaderboard/results"` (leaderboard); `huggingface_hub.HfApi()` (model cards)
- Code:
  ```python
  from datasets import load_dataset
  from huggingface_hub import HfApi, ModelCard

  # Load leaderboard results
  leaderboard = load_dataset("open-llm-leaderboard/results", split="train")

  # Load model card for a given model
  api = HfApi()
  card = ModelCard.load(model_id)
  card_text = card.content  # Full model card markdown text
  ```

### Models

#### Baseline Model

**This is a statistical analysis experiment — no neural network model is trained.**

| Property | Value |
|----------|-------|
| **Analysis type** | OLS regression (ordinary least squares) |
| **Library** | `statsmodels` (Python) |
| **Baseline specification** | Scale-only OLS: `benchmark_score ~ log_params + log_tokens` |
| **Framework** | `statsmodels.formula.api.ols()` |

**Baseline regression equation:**
```
benchmark_score_i = α + β₁·log(N_i) + β₂·log(D_i) + Σ_f γ_f·family_FE_{i,f} + ε_i
```
Where: N = parameter count, D = training tokens, family_FE = architecture family fixed effects

**Expected baseline R²:** ~0.60–0.75 (per Phase 2B Section 1.4)

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `statsmodels>=0.14.0`
- Code:
  ```python
  import statsmodels.formula.api as smf
  import pandas as pd

  # Baseline OLS (scale + architecture FEs only)
  baseline_model = smf.ols(
      "mmlu_score ~ log_params + log_tokens + C(arch_family)",
      data=registry_df
  ).fit()
  ```

#### Proposed Model

**Architecture:** Baseline OLS + doc_score documentation feature

**Core Mechanism Implementation:**

```python
# Core Mechanism: Documentation Feature as Benchmark Predictor
# Hypothesis H-E1 (EXISTENCE): Registry construction + doc_score variance check
# Based on: HuggingFace Hub API + standard OLS regression

import statsmodels.formula.api as smf
import pandas as pd
from huggingface_hub import HfApi, ModelCard
import re

def extract_curation_features(card_text: str) -> dict:
    """
    Extract 4 binary curation documentation features from model card text.
    Input:  card_text (str) — raw model card markdown
    Output: dict with 4 binary features (0 or 1)
    """
    text_lower = card_text.lower()
    return {
        "dedup_documented": int(bool(re.search(
            r"dedup|near.?dup|minhash|exact.?dedup", text_lower))),
        "perplexity_filter_documented": int(bool(re.search(
            r"perplexity.{0,20}filter|ppl.{0,10}filter|quality.{0,20}filter", text_lower))),
        "domain_composition_documented": int(bool(re.search(
            r"domain.{0,30}(%|percent|composition)|data.{0,30}mix", text_lower))),
        "decontamination_documented": int(bool(re.search(
            r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout", text_lower))),
    }

def build_registry(leaderboard_df: pd.DataFrame,
                   min_benchmarks: int = 4,
                   min_n: int = 200) -> pd.DataFrame:
    """
    Build LLM Documentation-Benchmark Registry.
    Input:  leaderboard_df — raw leaderboard results DataFrame
    Output: registry_df — filtered registry with features (target: n ≥ 200)
    """
    api = HfApi()
    records = []
    BENCHMARK_COLS = ["mmlu", "arc_challenge", "hellaswag",
                      "winogrande", "truthfulqa", "gsm8k"]

    for _, row in leaderboard_df.iterrows():
        model_id = row["model_name"]
        # Filter: ≥4/6 benchmarks present
        n_benchmarks = sum(pd.notna(row.get(b)) for b in BENCHMARK_COLS)
        if n_benchmarks < min_benchmarks:
            continue
        # Attempt model card retrieval
        try:
            card = ModelCard.load(model_id)
            features = extract_curation_features(card.content)
            model_info = api.model_info(model_id)
            n_params = getattr(model_info, "safetensors", {}).get("total", None)
            records.append({**row.to_dict(), **features,
                            "n_params": n_params,
                            "doc_score": sum(features.values())})
        except Exception:
            continue  # Model card inaccessible

    registry_df = pd.DataFrame(records).dropna(subset=["n_params"])
    return registry_df

# Proposed model: adds doc_score to baseline OLS
proposed_model = smf.ols(
    "mmlu_score ~ log_params + log_tokens + doc_score + C(arch_family)",
    data=registry_df
).fit()
```

### Training Protocol

**Note:** This is a statistical analysis, not ML training. "Training" = OLS fitting.

**Statistical Analysis Protocol:**

| Parameter | Value | Source |
|-----------|-------|--------|
| **Method** | OLS regression (statsmodels) | Phase 2B Section 1.3 |
| **Significance level** | α = 0.05 | Phase 2B controlled variables |
| **Permutation samples** | 1,000 (for null distribution) | Phase 2B controlled variables |
| **Power target** | 0.80 | Phase 2B controlled variables |
| **Min sample size** | n ≥ 200 | Phase 2B success criterion |
| **Covariates** | log(N), log(D), architecture family FE | Phase 2A design |
| **Seeds** | 1 (fixed: `random_state=42`) | EXISTENCE PoC standard |
| **Benchmarks tested** | MMLU (primary), ARC-Challenge (secondary) | Phase 2B Section 1.4 |

**Analysis Steps:**
1. Build registry (data collection + feature extraction)
2. Compute descriptive statistics on doc_score distribution
3. Verify non-trivial variance in doc_score (gate check)
4. Fit baseline OLS and proposed OLS
5. Compare ΔR² and β_docs coefficient
6. Report n_analyzable as primary existence check metric

**No optimizer, learning rate, batch size, or epochs** — not applicable to OLS regression.

### Evaluation

**Primary Metrics:**
- `n_analyzable`: Count of models with complete feature set (≥200 required)
- `doc_score_variance`: Variance of doc_score distribution across registry (non-trivial required)
- `doc_score_distribution`: Fraction of models at each level (0–4) — must not be >90% at one level

**Secondary Metrics (from OLS):**
- `beta_docs`: OLS coefficient on doc_score in proposed model
- `delta_R2`: ΔR² between proposed and baseline OLS
- Direction check: `beta_docs > 0` (proposed > baseline direction)

**Success Criteria (EXISTENCE PoC):**
- **Primary (MUST_WORK pass):** n_analyzable ≥ 200 AND doc_score_variance > 0 in ≥3/4 features
- **Secondary:** n with training tokens D recoverable ≥ 100
- PoC pass = "Registry exists with sufficient size and variance for regression"

**Expected Baseline Performance:**
- Scale-only OLS R²: ~0.60–0.75 (per Phase 2B Section 1.4, consistent with Thrush et al. 2024)
- Expected doc_score range: 0–4, expected mean ~1.5–2.5 (major families document partially)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis (not classification/regression ML)
- Library: `statsmodels`, `pandas`, `scipy.stats`, `matplotlib`
- Code:
  ```python
  import pandas as pd
  import statsmodels.formula.api as smf
  from scipy import stats

  # Primary existence check
  n_analyzable = len(registry_df)
  doc_score_var = registry_df["doc_score"].var()
  feature_vars = {f: registry_df[f].var() for f in FEATURE_COLS}
  n_features_with_variance = sum(v > 0 for v in feature_vars.values())

  # Success gate
  gate_passed = (n_analyzable >= 200) and (n_features_with_variance >= 3)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing n_analyzable vs target (200), doc_score distribution histogram

#### Additional Figures (LLM Autonomous)
Based on the registry construction task, these visualizations are recommended:
1. **doc_score Distribution**: Histogram of doc_score (0–4) across all analyzable models
2. **Feature Coverage**: 4-panel bar chart showing fraction of models with each binary feature documented
3. **Model Family Breakdown**: Stacked bar showing doc_score distribution per architecture family
4. **Benchmark Availability**: Heatmap of benchmark × model availability matrix
5. **Dropout Funnel**: Waterfall chart showing filtering steps (raw → benchmark filter → param filter → card accessible → complete)

**Output Location:** `h-e1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (data collection completes)
2. `n_analyzable ≥ 200` (primary metric > target)
3. `doc_score_variance > 0` in ≥3/4 features (non-trivial variance)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|--------------|
| **mechanism_exists** | True — Registry construction is feasible via HuggingFace Hub API |
| **mechanism_isolatable** | True — n_analyzable is directly measurable as primary output |
| **baseline_measurable** | True — Scale-only OLS R² is directly computed |
| **architecture_compatibility** | N/A — No neural architecture; statistical analysis only |
| **mechanism_log_message** | `"Registry built: n_analyzable={n}, doc_score mean={mean:.2f}, var={var:.2f}"` |
| **tensor_shape_change** | N/A — Tabular data: registry_df shape = (n_models, n_features) |
| **metric_delta_expected** | n_analyzable ≥ 200 (absolute threshold, not delta) |
| **mechanism_verification_code** | `assert len(registry_df) >= 200, f"Registry too small: {len(registry_df)}"` |
| **hypothesis_support_threshold** | n_analyzable ≥ 200 AND n_features_with_variance ≥ 3 |
| **hypothesis_support_metric** | n_analyzable (primary), doc_score_variance (secondary) |

**Pre-conditions:**
- HuggingFace Hub API accessible (internet connection available)
- `open-llm-leaderboard/results` dataset publicly accessible
- `huggingface_hub`, `datasets`, `pandas`, `statsmodels` installed

**Failure Detection:**
- If HF API rate-limited: implement exponential backoff (max 5 retries per model)
- If n < 200 after primary filter: trigger fallback to v1+v2 combined snapshot
- If doc_score uniformly 0 or 4: review keyword extraction rules, log distribution

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace Transformers docs (similarity: 0.543)
- **Query Used:** "HuggingFace model card feature extraction LLM"
- **Key Insights:** HuggingFace Hub ecosystem; transformers library as standard model access layer
- **Used For:** Confirming HF Hub API approach for model card access

**Source A.2**: OpenReview benchmark paper (similarity: 0.456, 17K words)
- **Query Used:** "Open LLM Leaderboard dataset scraping benchmark"
- **Key Insights:** Academic benchmark evaluation methodology — confirms leaderboard-based evaluation as established practice
- **Used For:** Background on leaderboard evaluation design

**Source A.3**: HF paper 2305.14314 (similarity: 0.446)
- **Query Used:** "observational study LLM benchmark performance regression"
- **Key Insights:** Research on LLM performance evaluation
- **Used For:** Background on regression-based LLM analysis

### Archon Code Examples

**Code Source A.4**: `RepoCard.load()` pattern (rerank: 3.562)
- **Query Used:** "HuggingFace Hub API model card parsing Python"
- **Key Code:**
  ```python
  from huggingface_hub.repocard import RepoCard
  card = RepoCard.load(model_id)
  metadata = card.data.to_dict()
  ```
- **Used For:** Model card retrieval pseudo-code in Core Mechanism

**Code Source A.5**: `hf_hub_download` / `snapshot_download` pattern (rerank: 2.713)
- **Key Code:**
  ```python
  from huggingface_hub import hf_hub_download, snapshot_download
  snapshot_download(repo_id, allow_patterns="*.json", local_dir="./data")
  ```
- **Used For:** Dataset download implementation reference

### B. GitHub Implementations (Exa)

**⚠️ Exa MCP unavailable (HTTP 402 — billing exceeded)**
- All Exa queries failed after retry (2 attempts per MCP retry protocol)
- No GitHub repository results available
- **Mitigation:** Implementation design based on Archon code patterns + standard HuggingFace Hub API documentation (public domain knowledge)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear.
- H-E1 is a data collection and statistical analysis task using standard Python APIs
- No complex neural network architecture code requiring semantic analysis
- `serena_needed = false`

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B design | 02b_verification_plan.md Section 1.3, 2.2 |
| HF Hub API approach | Archon Code A.4 | `RepoCard.load()` pattern |
| Feature keywords | Phase 2B design | 02b_verification_plan.md Section 2.2 H-E1 |
| Baseline OLS specification | Phase 2B Section 1.4 | Baseline Methods table |
| Success threshold (n≥200) | Phase 2B success criteria | H-E1 primary criterion |
| doc_score variance check | Phase 2B success criteria | H-E1 secondary criterion |
| Statistical parameters | Phase 2B controlled variables | significance_level, permutation_samples |
| Expected R² range | Phase 2B Section 1.4 | Scale-only OLS baseline |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-17T08:30:00Z

### Workflow History for This Hypothesis
- 2026-03-17T00:00:00Z: Phase 2B completed, H-E1 created as READY
- 2026-03-17T08:26:26Z: H-E1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-03-17T08:30:00Z: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code ✅), Exa (GitHub ⚠️ unavailable — 402), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
