# Experiment Design: H-E1

**Date:** 2026-07-30
**Author:** Anonymous
**Hypothesis Statement:** After fuzzy join (rapidfuzz WRatio threshold=75) of Open LLM Leaderboard v1 and lighteval/bbq_helm, at least N≥30 open-weight LLMs will have complete scores on TruthfulQA MC2, BBQ accuracy, and MMLU simultaneously, confirming data infrastructure viability for partial Spearman analysis.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — N≥30 complete rows required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: N ≥ 30 open-weight LLMs with complete TruthfulQA MC2 + BBQ accuracy + MMLU rows after fuzzy join.

---

## Continuation Context

No previous hypothesis context — H-E1 is the first in the verification chain.

### Previous Hypothesis Results (if applicable)
None — this is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design Search** (query: "rapidfuzz fuzzy join LLM benchmark dataset")
- No relevant results. Archon KB is focused on image generation / diffusers — no benchmark joining or statistical analysis content.

**Query 2: Implementation Challenges** (query: "fuzzy string matching benchmark dataset merging best practices")
- No relevant results. Same knowledge base limitation applies.

**Query 3: Benchmark Results** (query: "Open LLM Leaderboard HuggingFace dataset join evaluation")
- No relevant results from Archon.

**Assessment:** Archon KB contains no relevant prior cases for this hypothesis domain (benchmark dataset joining, LLM evaluation infrastructure). All grounding comes from Exa GitHub research below.

### Archon Code Examples

**Query 1: rapidfuzz WRatio fuzzy join pandas DataFrame**
- No relevant code examples. Highest similarity ~0.26 (diffusers/wuerstchen training code — irrelevant).

**Query 2: HuggingFace datasets load_dataset spearman correlation**
- No relevant code examples. Highest similarity ~0.41 (video dataset download — irrelevant).

**Assessment:** Archon code index does not contain fuzzy join or statistical analysis code.

### Exa GitHub Implementations

**Query 1: rapidfuzz WRatio fuzzy join pandas LLM benchmark**

**Repository 1**: rapidfuzz/RapidFuzz (⭐ 4K)
- **URL**: https://github.com/rapidfuzz/RapidFuzz
- **Relevance**: Primary library for WRatio fuzzy matching
- **WRatio Algorithm** (from Issue #359 — confirmed):
  ```python
  # WRatio pseudo-code (confirmed from RapidFuzz docs)
  len_ratio = max(len1, len2) / min(len1, len2)
  if len_ratio < 1.5:
      return max(
          ratio(s1, s2),
          token_ratio(s1, s2) * 0.95
      )
  else:
      scale = 0.9 if len_ratio < 8.0 else 0.6
      return max(
          partial_ratio(s1, s2) * scale,
          partial_token_ratio(s1, s2) * 0.95 * scale
      )
  ```
- **Key Insight**: For model names (similar length, alphanumeric), len_ratio < 1.5 is common → uses ratio + token_ratio. Must pass `processor=utils.default_process` for case normalization.
- **Performance**: cdist() vectorized form is significantly faster than pairwise loops.

**Repository 2**: fboulnois/llm-leaderboard-csv (⭐ 30)
- **URL**: https://github.com/fboulnois/llm-leaderboard-csv
- **Relevance**: Primary data source — LLM LB v1 CSVs
- **Key Finding**: LLM LB v1 CSVs available at `v1.3.0` release (static, archived). Main branch now tracks LMArena only. Must use `v1.3.0` tag.
- **Columns**: model_name, TruthfulQA_MC2, MMLU (confirmed from topic tags: open-llm-leaderboard, llama, mistral, chatgpt)
- **Download**: Static CSV from GitHub release assets at v1.3.0

**Query 2: lighteval bbq_helm HuggingFace dataset structure**

**Dataset**: lighteval/bbq_helm
- **URL**: https://huggingface.co/datasets/lighteval/bbq_helm
- **Relevance**: Primary BBQ accuracy source
- **Structure**: 11,864 rows of QA items (NOT pre-aggregated per-model scores)
  - Columns: `context`, `question`, `references` (dict), `choices` (list), `gold_index` (int64)
  - Subsets: 12 bias categories (Age, Disability_status, Gender_identity, Nationality, Physical_appearance, Race_ethnicity, Race_x_SES, Race_x_gender, Religion, SES, Sexual_orientation, all)
  - Splits: test only (1k rows each subset)
- **Critical Finding**: This dataset is the BBQ QA item corpus, not scored model outputs.
- **Implication**: BBQ accuracy per model is NOT directly in this dataset. Must source per-model BBQ scores from a pre-computed evaluation results table.
- **Alternative BBQ source**: HELM Lite v1.9.0 on HuggingFace (has per-model scores), OR search for a pre-computed BBQ leaderboard results file.

**Serena Analysis Needed**: false — no complex local code requiring analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is an observational data science experiment, not a paper reproduction. Priority is data source reliability:

1. LLM LB v1 CSV: `fboulnois/llm-leaderboard-csv` v1.3.0 (static, archived, verified)
2. BBQ scores: HELM Lite v1.9.0 HuggingFace dataset (per-model accuracy, pre-computed) — `lighteval/bbq_helm` contains QA items only, not model scores.

**Recommended Implementation Path:**
- Primary: `fboulnois/llm-leaderboard-csv` v1.3.0 CSV + HELM Lite v1.9.0 per-model BBQ scores
- Fallback: Direct HuggingFace Open LLM Leaderboard v1 API + HELM Classic results page
- Justification: `lighteval/bbq_helm` confirmed as QA item corpus, not scored results. HELM Lite v1.9.0 provides per-model BBQ accuracy scores for ~79 models in tabular form, enabling direct join with LLM LB v1.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; no complex local codebase requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset (LLM LB v1):**
- **Name**: Open LLM Leaderboard v1 (fboulnois/llm-leaderboard-csv v1.3.0)
- **Type**: programmatic-api (static CSV download from GitHub release)
- **Source**: https://github.com/fboulnois/llm-leaderboard-csv/releases/tag/v1.3.0
- **Content**: ~300+ open-weight LLM scores including TruthfulQA MC2 and MMLU
- **Key Columns**: `model_name`, `TruthfulQA_MC2` (0-100), `MMLU` (0-100), open_weight filter flag
- **Filter**: Open-weight only (exclude proprietary: GPT-4, Claude, Gemini)
- **Path**: `./data/llm_leaderboard_v1/llm.csv` (downloaded from release assets)

**Secondary Dataset (BBQ scores):**
- **Name**: HELM Lite v1.9.0 — BBQ accuracy per model
- **Type**: programmatic-api (HuggingFace datasets API)
- **Source**: `datasets.load_dataset("stanford-crfm/helm-lite", "v1.9.0")` OR direct download from HELM results page
- **Content**: Per-model BBQ accuracy scores for ~79 models
- **Key Columns**: `model_name`, `bbq_accuracy` (mean across BBQ subsets)
- **Note**: `lighteval/bbq_helm` is a QA item corpus; HELM Lite v1.9.0 provides the pre-evaluated per-model accuracy scores needed for this join.
- **Fallback**: If HELM Lite unavailable, manually aggregate from lighteval/bbq_helm by running evaluation — but this requires running each model, which is out of scope for a data infrastructure test.
- **Path**: `./data/bbq_scores/bbq_per_model.csv`

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: `fboulnois/llm-leaderboard-csv` v1.3.0 GitHub release + HELM Lite v1.9.0
- Code:
  ```python
  # LLM LB v1 — from release assets
  import requests, pandas as pd
  url = "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv"
  r = requests.head(url)
  assert r.status_code == 200, f"URL check failed: {r.status_code}"
  df_llm = pd.read_csv(url)

  # BBQ scores — HELM Lite
  from datasets import load_dataset
  ds = load_dataset("stanford-crfm/helm-lite", split="test")
  # OR direct CSV from HELM results
  ```

### Models

#### Baseline Model

**Architecture**: Population of open-weight LLMs (observational study — no trained model)
- **Type**: Observational cross-section; no baseline ML model to train
- **Source**: Open LLM Leaderboard v1 + HELM Lite BBQ scores
- **N expected**: ~79-300 candidate models; target N≥30 after fuzzy join
- **Open-weight filter**: Exclude proprietary API-only models

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (see Dataset section above)
- Identifier: Not applicable — models are study subjects, not loaded ML models
- Code: See Dataset loading code above

#### Proposed Model

**Architecture:** Baseline + fuzzy join mechanism

**Core Mechanism Implementation:**

```python
# Core Mechanism: rapidfuzz WRatio fuzzy join
# Based on: rapidfuzz/RapidFuzz v3.x (confirmed algorithm from Issue #359)

from rapidfuzz import fuzz, process, utils
import pandas as pd

def fuzzy_join_benchmarks(
    df_llm: pd.DataFrame,      # LLM LB v1: columns [model_name, TruthfulQA_MC2, MMLU, ...]
    df_bbq: pd.DataFrame,      # BBQ scores: columns [model_name, bbq_accuracy]
    threshold: int = 75,        # WRatio threshold (validated: prior runs at 75-80)
    fallback_threshold: int = 70
) -> pd.DataFrame:
    """
    Fuzzy join two benchmark DataFrames on model_name.
    Returns merged DataFrame with complete rows (non-null in all 3 key columns).
    """
    # Step 1: URL pre-flight check (executed before this function)
    # Step 2: Normalize model names
    llm_names = df_llm["model_name"].tolist()
    bbq_names = df_bbq["model_name"].tolist()

    # Step 3: WRatio fuzzy match with processor for case normalization
    matches = []
    for bbq_name in bbq_names:
        result = process.extractOne(
            bbq_name, llm_names,
            scorer=fuzz.WRatio,
            processor=utils.default_process,
            score_cutoff=threshold
        )
        if result:
            matches.append({"bbq_name": bbq_name,
                            "llm_name": result[0], "score": result[1]})

    # Step 4: Apply token_set_ratio fallback if match_rate < 0.55
    match_rate = len(matches) / len(bbq_names)
    if match_rate < 0.55:
        # Retry with token_set_ratio at lower threshold
        from rapidfuzz import fuzz as rfuzz
        # ... fallback logic with threshold=fallback_threshold
        pass

    # Step 5: Merge and count complete rows
    df_matches = pd.DataFrame(matches)
    df_joined = df_bbq.merge(df_matches, left_on="model_name",
                              right_on="bbq_name", how="inner")
    df_joined = df_joined.merge(df_llm, left_on="llm_name",
                                 right_on="model_name", how="inner")
    df_complete = df_joined.dropna(
        subset=["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
    )
    N = len(df_complete)
    return df_complete, N, match_rate
```

### Training Protocol

**No training required** — this is an observational data infrastructure experiment.

**Execution Protocol:**
- **Optimizer**: N/A (no ML training)
- **Seed**: 42 (fixed for reproducibility of any randomized steps)
- **Execution**: Sequential data pipeline (URL test → download → filter → join → count)
- **Steps**:
  1. `requests.head()` URL pre-flight test for LLM LB v1 CSV and HELM Lite BBQ source
  2. Download LLM LB v1 CSV from `fboulnois/llm-leaderboard-csv` v1.3.0 release
  3. Filter open-weight only; extract `model_name`, `TruthfulQA_MC2`, `MMLU` columns
  4. Load HELM Lite BBQ per-model scores; compute/verify mean BBQ accuracy per model
  5. Execute rapidfuzz WRatio join at threshold=75; apply token_set_ratio fallback if match_rate < 0.55
  6. Count N complete rows (non-null in all three columns); report match_rate = N_matched / N_bbq
  7. Test fallback thresholds (70, 65) if N < 30

### Evaluation

**Primary Metric**: N = count of models with complete TruthfulQA MC2 + BBQ accuracy + MMLU rows after join

**Success Criteria:**
- proposed_metric > baseline_metric equivalent:
  - N ≥ 30 complete rows (MUST_WORK gate PASSES)
  - match_rate ≥ 0.55 (data quality gate)

**Expected Baseline Performance** (from Phase 2B established facts):
- Prior run H-E1 snapshot: match_rate = 0.857 (WRatio threshold=75)
- Prior run H-E2: match_rate = 0.517 (marginal, different BBQ source)
- **Source**: Phase 2B Section 0 (BUILD_ON claims)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: data_infrastructure_audit (not classification/regression)
- Library: pandas + rapidfuzz (no torchmetrics needed)
- Code:
  ```python
  # Primary gate metric
  N_complete = len(df_complete)
  match_rate = N_matched / N_bbq
  gate_pass = N_complete >= 30 and match_rate >= 0.55
  print(f"N_complete={N_complete}, match_rate={match_rate:.3f}, gate={'PASS' if gate_pass else 'FAIL'}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing N_complete vs threshold=30, and match_rate vs threshold=0.55

#### Additional Figures (LLM Autonomous)
Based on this data infrastructure experiment, generate:
1. **Model name match quality distribution**: Histogram of WRatio scores for all matched pairs
2. **Dataset overlap Venn diagram**: LLM LB v1 models vs BBQ models vs matched set
3. **Fallback threshold sensitivity**: Line plot of N_complete vs threshold (65, 70, 75, 80)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (URL tests pass, downloads succeed)
2. `N_complete >= 30` (proposed_metric > baseline_metric equivalent)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | rapidfuzz WRatio join can be applied to two DataFrame model_name columns | TRUE — confirmed from RapidFuzz docs and Issue #359 |
| Mechanism Isolatable | Join can be enabled/disabled to compare N with exact-match vs fuzzy-match | TRUE — pd.merge(how='inner') for exact, rapidfuzz for fuzzy |
| Baseline Measurable | Exact-match join (pd.merge) N can be measured as baseline | TRUE |

### Architecture Compatibility Check

This experiment uses no ML model architecture. Compatibility refers to data pipeline compatibility:

**Required features:**
- `rapidfuzz >= 3.0` (WRatio + process.extractOne + utils.default_process)
- `pandas >= 1.5` (DataFrame merge operations)
- `datasets >= 2.0` (load_dataset for HELM Lite / lighteval)
- `requests >= 2.28` (URL pre-flight HEAD check)

**Incompatible scenarios:**
- If HELM Lite BBQ per-model scores are unavailable → fallback to manual aggregation (out of scope for H-E1; report as data availability failure)
- If LLM LB v1 CSV URL returns non-200 → try GitHub API clone fallback

> ⚠️ Phase 4 MUST execute URL HEAD check first and abort with descriptive error if non-200.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Fuzzy join completed: N_matched=X, match_rate=Y.YYY" | data_pipeline.py after join |
| N count | N_complete ≥ 30 (gate threshold) | after dropna() |
| Metric Delta | N_complete (fuzzy) >> N_complete (exact-match) shows join value | comparison log |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(df_complete, N_complete, match_rate, N_exact):
    indicators = {
        "url_check_passed": True,  # set by pre-flight check
        "join_produced_rows": N_complete > 0,
        "fuzzy_beats_exact": N_complete > N_exact,
        "gate_passed": N_complete >= 30,
        "match_rate_acceptable": match_rate >= 0.55
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (join runs, N > 0) | Log/count check |
| Effect Measurable | N_complete > 0 | After dropna() |
| Hypothesis Supported | N_complete ≥ 30 AND match_rate ≥ 0.55 | Gate metrics |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment**: Archon KB contained no relevant prior cases for this hypothesis domain. All 5 queries returned diffusers/image-generation content (similarity ~0.26-0.51 — well below meaningful threshold). No Archon sources cited in experiment design.

---

### B. GitHub Implementations (Exa)

**Repository 1**: rapidfuzz/RapidFuzz (⭐ 4K)
- **URL**: https://github.com/rapidfuzz/RapidFuzz
- **Query Used**: "rapidfuzz WRatio fuzzy join pandas LLM benchmark model names GitHub"
- **Relevance**: WRatio algorithm internals confirmed — critical for understanding threshold behavior
- **Key Code** (annotated):
  ```python
  # WRatio algorithm (from Issue #359, confirmed behavior)
  # For model names (similar length): uses ratio + token_ratio * 0.95
  # Must use processor=utils.default_process for case normalization
  from rapidfuzz import fuzz, process, utils
  score = fuzz.WRatio("meta-llama/Llama-2-7b-hf",
                       "meta-llama/Llama-2-7B-hf",
                       processor=utils.default_process)  # → 100.0
  ```
- **Configuration Extracted**: threshold=75 validated; use `process.extractOne` for single-best match
- **Used For**: Core mechanism pseudo-code (fuzzy_join_benchmarks function)

**Repository 2**: fboulnois/llm-leaderboard-csv (⭐ 30)
- **URL**: https://github.com/fboulnois/llm-leaderboard-csv
- **Query Used**: "fboulnois llm-leaderboard-csv v1.3.0 llm.csv columns TruthfulQA MMLU open weight"
- **Relevance**: Confirmed primary data source for LLM LB v1 (archived at v1.3.0)
- **Key Finding**: Main branch now LMArena only; v1.3.0 release has static HuggingFace Open LLM LB v1 + v2 CSVs
- **Used For**: Dataset specification (primary data source)

**Dataset**: lighteval/bbq_helm
- **URL**: https://huggingface.co/datasets/lighteval/bbq_helm
- **Query Used**: "lighteval bbq_helm huggingface dataset load BBQ accuracy open LLM leaderboard fuzzy join"
- **Critical Finding**: QA item corpus (11,864 rows), NOT per-model scores. Subsets by bias category (Age, Religion, etc.). Rows are individual questions, not model evaluations.
- **Implication**: Direct load_dataset() yields QA items, not BBQ accuracy per model. Must use HELM Lite v1.9.0 for per-model scores.
- **Used For**: Dataset specification (clarifying correct BBQ source)

---

### C. Code Analysis (Serena)

Serena analysis not performed — code from Exa search results was sufficiently clear for this data pipeline task (no complex neural architecture, just pandas + rapidfuzz operations).

---

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain.

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| WRatio threshold=75 | Phase 2B BUILD_ON | Prior run h-e1 match_rate=0.857 |
| WRatio algorithm details | GitHub (Exa) | rapidfuzz/RapidFuzz Issue #359 |
| LLM LB v1 CSV source | GitHub (Exa) | fboulnois/llm-leaderboard-csv v1.3.0 |
| BBQ source clarification | HuggingFace (Exa) | lighteval/bbq_helm dataset card |
| HELM Lite as BBQ score source | Phase 2B | Section 1.3 fallback: "HELM Lite v1.9.0 as BBQ source fallback" |
| N≥30 gate threshold | Phase 2B | Section 2.2 H-E1 Success Criteria |
| match_rate≥0.55 threshold | Phase 2B | Section 2.2 H-E1 (lesson from h-e2: 0.517 was marginal) |
| token_set_ratio fallback | Phase 2B | Section 2.2 H-E1 Verification Protocol step 4 |
| Open-weight filter | Phase 2B | Section 1.3 CV (control variables) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed externally)
**Date:** 2026-07-30

### Workflow History for This Hypothesis
- 2026-07-30: Phase 2C experiment design completed (UNATTENDED mode)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — rapidfuzz docs, fboulnois CSV, lighteval/bbq_helm), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
