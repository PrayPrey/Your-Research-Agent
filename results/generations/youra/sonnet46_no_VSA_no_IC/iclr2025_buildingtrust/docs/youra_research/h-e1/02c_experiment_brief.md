# Experiment Design: H-E1

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Published multi-model evaluation scores exist for 10+ overlapping LLMs across all required trustworthiness benchmark pairs (BBQ-Disambig/Ambig, GLUE/AdvGLUE, ANLI R1/R3) and MMLU, enabling partial Spearman ρ computation for cross-split predictive validity analysis.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (root hypothesis)
**Gate Status:** MUST_WORK — N_common ≥ 10 models with all required benchmark scores

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: N_common ≥ 10 models with all 7 required benchmark scores (BBQ-Disambig, BBQ-Ambig, GLUE, AdvGLUE, ANLI-R1, ANLI-R3, MMLU). Failure triggers PIVOT — supplement from additional sources or restrict scope.

---

## Continuation Context

First hypothesis in chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the root hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "Spearman rank correlation LLM benchmark evaluation"**
- No relevant results found in Archon KB (top similarity 0.39 — unrelated diffusion model content)
- KB is populated with computer vision / generative model literature; NLP evaluation methodology not represented

**Query 2: "benchmark score aggregation multi-model evaluation challenges"**
- Top result: openreview.net forum (similarity 0.43) — not relevant to LLM trustworthiness evaluation
- No actionable findings

**Query 3: "trustworthiness fairness OOD generalization predictive validity"**
- Top result: OOTDiffusion (similarity 0.34) — completely unrelated
- No actionable findings

**Query 4 (Code): "partial Spearman correlation pandas scipy statistics"**
- Results: PyTorch distributed ops, Stable Diffusion setup — not relevant
- No actionable code examples from Archon

**Assessment:** Archon KB contains no prior cases for this research domain. All experiment design grounded in Exa-sourced literature and standard statistical libraries.

### Archon Code Examples

No relevant code examples found in Archon KB for this domain. See Exa GitHub Implementations below.

### Exa GitHub Implementations

**Query 1: TrustLLM official repository**

**Repository 1**: HowieHwong/TrustLLM (⭐ 628)
- **URL**: https://github.com/HowieHwong/TrustLLM
- **Relevance**: Primary data source for BBQ-Disambig, BBQ-Ambig, ANLI scores for 16 LLMs (ICML 2024)
- **Architecture**: Python toolkit with JSON result files per model per task
- **Key Code**:
  ```python
  from trustllm.task.pipeline import run_truthfulness
  from trustllm.generation.generation import LLMGeneration
  # Results stored in JSON per model, organized by task type:
  # TrustLLM/Fairness/Json_File.json, TrustLLM/Robustness/Json_File.json
  ```
- **Data Structure**: `results/` directory, JSON per model per task; organized as `TrustLLM/{Dimension}/{task}.json`
- **Models evaluated**: 16 mainstream LLMs including LLaMA-2 variants, GPT-3.5, GPT-4, Mistral, Falcon, Vicuna, Alpaca
- **Benchmarks**: Fairness (BBQ, stereotype), Robustness (OOD/ANLI), Safety, Truthfulness, Privacy, Ethics
- **Dataset (HuggingFace)**: `TrustLLM/TrustLLM-dataset`
- **Leaderboard**: https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard

**Repository 2**: nyu-mll/BBQ (⭐ 141)
- **URL**: https://github.com/nyu-mll/BBQ
- **Relevance**: Official BBQ benchmark repository; confirms disambig/ambig split structure
- **Key Code** (bias score calculation, R):
  ```r
  # context_condition field: "ambig" | "disambig"
  # Disambig = adequately informative context (ID)
  # Ambig = under-informative context (OOD)
  dat_acc <- dat_with_metadata %>%
    group_by(category, model, context_condition) %>%
    summarise(accuracy = mean(acc))
  # accuracy reported separately for ambig and disambig conditions
  ```
- **Key insight**: BBQ-Disambig and BBQ-Ambig are two `context_condition` splits of the SAME dataset (not separate datasets). TrustLLM reports accuracy for each split separately.

**Query 2: GLUE-X repository**

**Repository 3**: YangLinyi/GLUE-X (ACL 2023)
- **URL**: https://github.com/YangLinyi/GLUE-X
- **Relevance**: Primary source for GLUE (ID) and OOD robustness scores for 21 PLMs
- **Key data**: Table 3 reports average GLUE ID accuracy and GLUE-X OOD accuracy per model
- **Models**: ELECTRA-large (best: 89.18% ID, 74.62% OOD), T5-large, RoBERTa-large, BART-large, T5-base, XLNet-large, GPT-2 variants, BERT variants, ALBERT, DistilBERT
- **IMPORTANT**: GLUE-X evaluates PLMs (encoder/encoder-decoder models), NOT decoder-only LLMs from TrustLLM. Model overlap with TrustLLM set is likely LIMITED — requires careful disambiguation during data audit.
- **OOD data**: https://drive.google.com/drive/folders/1BcwjmVOqq96igfbB2MCXwLzthFX7XEhy

**Query 3: HuggingFace Open LLM Leaderboard (MMLU)**

**Source 4**: HuggingFace Open LLM Leaderboard
- **URL**: https://huggingface.co/datasets/open-llm-leaderboard/results
- **Relevance**: MMLU-PRO scores for open LLMs; historical MMLU 5-shot scores
- **Access method**:
  ```python
  import pandas as pd
  # Pre-aggregated cross-benchmark data:
  df = pd.read_parquet(
      "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet"
  )
  # Or via API:
  from huggingface_hub import HfApi
  api = HfApi()
  leaderboard = api.get_dataset_leaderboard("open-llm-leaderboard/results")
  ```
- **NOTE**: Current leaderboard uses MMLU-PRO (10-choice), not original MMLU (4-choice). Historical MMLU scores for LLaMA-2, GPT models available in paper appendices and older leaderboard snapshots.

**Query 4: Partial correlation implementation**

**Source 5**: pingouin library (raphaelvallat/pingouin)
- **URL**: https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Relevance**: Provides `partial_corr()` with `method='spearman'` and `alternative='greater'` (one-tailed) — exactly what H-M1 requires
- **Key Code**:
  ```python
  import pingouin as pg
  result = pg.partial_corr(
      data=df, x='BBQ_Disambig', y='BBQ_Ambig',
      covar='MMLU', method='spearman', alternative='greater'
  )
  # Returns: n, r, CI95, p-val, BF10, power
  ```
- **Advantage over manual formula**: Handles edge cases, returns 95% CI, BF10 Bayes factor

**Serena Analysis Needed**: false (no existing codebase to analyze)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a data audit experiment — no model training or reproduction. Priority hierarchy:
1. TrustLLM GitHub (HowieHwong/TrustLLM) for BBQ and ANLI scores — 16 LLMs, consistent protocol
2. GLUE-X GitHub (YangLinyi/GLUE-X) for GLUE/AdvGLUE scores — 21 PLMs (NOTE: limited LLM overlap)
3. HuggingFace Open LLM Leaderboard for MMLU scores
4. Manual extraction from paper tables as fallback (DecodingTrust appendices)

**Recommended Implementation Path:**
- Primary: TrustLLM repo (BBQ + ANLI) + HuggingFace leaderboard (MMLU); GLUE-X for robustness pair
- Fallback: Manual PDF table extraction from TrustLLM paper (arXiv 2401.05561) + GLUE-X paper (ACL 2023)
- Justification: TrustLLM is the only single source with consistent protocol across BBQ-Disambig/Ambig AND ANLI for decoder-only LLMs. GLUE-X covers PLMs; overlap with TrustLLM's decoder-only LLMs must be verified.

**CRITICAL RISK**: GLUE-X evaluates encoder/encoder-decoder PLMs (ELECTRA, RoBERTa, T5, BERT, XLNet, BART, GPT-2), while TrustLLM evaluates decoder-only instruction-tuned LLMs (LLaMA-2, GPT-3.5/4, Mistral, Falcon). The overlap is likely very small or zero for the GLUE/AdvGLUE dimension — this is the primary data availability risk for H-E1 and must be the first thing checked.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a data collection and statistical analysis experiment with no existing codebase to analyze.

---

## Experiment Specification

### Dataset

**Type:** programmatic-api (real data via GitHub repos, HuggingFace datasets API, and paper tables)

**Name:** Aggregated Multi-Model Trustworthiness Benchmark Scores (H-E1 Audit Matrix)
**Version:** As of 2024 paper releases

**Primary Sources (in priority order):**

| Source | Benchmarks | Models | Type |
|--------|-----------|--------|------|
| TrustLLM (Huang et al., ICML 2024) | BBQ-Disambig, BBQ-Ambig, ANLI-R1, ANLI-R3 | 16 decoder-only LLMs | programmatic-api |
| GLUE-X (Yang et al., ACL 2023) | GLUE avg, AdvGLUE avg | 21 PLMs (encoder/decoder) | programmatic-api |
| OOD_NLP (Yuan et al., NeurIPS 2023) | ANLI-R1, ANLI-R3 (supplement) | Various | programmatic-api |
| DecodingTrust (Wang et al., NeurIPS 2023) | AdvGLUE++, fairness, OOD | GPT-3.5, GPT-4 | programmatic-api |
| HuggingFace Open LLM Leaderboard | MMLU (5-shot) | Broad coverage | programmatic-api |

**Target Model Set (expected TrustLLM models):**
- LLaMA-2-7B, LLaMA-2-13B, LLaMA-2-70B (base)
- LLaMA-2-7B-Chat, LLaMA-2-13B-Chat, LLaMA-2-70B-Chat
- Mistral-7B, Mistral-7B-Instruct
- Falcon-7B, Falcon-40B
- GPT-3.5-Turbo, GPT-4
- Vicuna-13B, Alpaca-13B
- Additional models from TrustLLM paper

**Target Benchmark Columns (7 required):**
1. BBQ-Disambig (accuracy in disambiguated/informative context — ID fairness)
2. BBQ-Ambig (accuracy in ambiguous/underspecified context — OOD fairness)
3. GLUE average (SST-2, MNLI, QNLI, RTE, MRPC, QQP, STS-B — ID robustness)
4. AdvGLUE average (adversarial perturbations of GLUE tasks — OOD robustness)
5. ANLI-R1 (Adversarial NLI Round 1 — ID adversarial robustness)
6. ANLI-R3 (Adversarial NLI Round 3 — OOD adversarial robustness)
7. MMLU (5-shot accuracy — general capability covariate)

**Preprocessing Steps:**
1. Clone/download TrustLLM results JSON; extract per-model BBQ and ANLI scores
2. Download GLUE-X Table 3 data (CSV from Google Drive or paper extraction)
3. Fetch MMLU scores from HuggingFace leaderboard API or paper appendices
4. Build canonical model name mapping (aliases → canonical ID)
5. Construct model × 7-benchmark matrix; fill cells by source priority
6. Flag incomplete rows; count N_common (complete rows) and N_per_pair (per benchmark pair)
7. Check protocol consistency: for shared models, compare cross-source scores (flag >5pp deviation)

**Sample Size:** All available models from source intersection. Expected N_common = 10–16 (TrustLLM set); N_GLUE/AdvGLUE likely much smaller due to model family mismatch.

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (GitHub + HuggingFace datasets)
- Identifier: HowieHwong/TrustLLM, YangLinyi/GLUE-X, OpenEvals/leaderboard-data
- Code:
```python
import pandas as pd
import json
import glob
from huggingface_hub import HfApi

# TrustLLM: clone repo, parse results JSONs
# git clone https://github.com/HowieHwong/TrustLLM
def load_trustllm_bbq_anli(results_dir):
    """Extract per-model BBQ and ANLI scores from TrustLLM results."""
    scores = {}
    # BBQ results: look for fairness dimension JSONs
    for f in glob.glob(f"{results_dir}/Fairness/**/*.json", recursive=True):
        with open(f) as fp:
            data = json.load(fp)
        # Each JSON contains per-example results with context_condition field
        # Aggregate: accuracy for context_condition='disambig' and 'ambig' separately
    return scores

# HuggingFace leaderboard (MMLU)
df_leaderboard = pd.read_parquet(
    "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet"
)
# Filter for MMLU column and target models
```

### Models

#### Baseline Model

**Type:** No ML model training. Statistical analysis experiment only.

**Baseline Metric (pre-existing reference):**
- Raw Spearman ρ (no MMLU control) between each benchmark pair — the comparison point for partial ρ
- Reference: Gevers & Daelemans (2026) commonsense predictive validity study; GLUE-X Friedman rank analysis (Yang et al. 2023)

**PoC "model" = data audit script:** `run_h_e1_audit(matrix)` returning N_common and N_per_pair

**Loading Information** (for Phase 4 download):
- Method: pip install (standard libraries)
- Identifier: scipy>=1.7.0, pingouin>=0.5.0, pandas>=1.3.0
- Code:
```python
# pip install scipy pingouin pandas numpy
from scipy.stats import spearmanr
import pingouin as pg
import pandas as pd
import numpy as np
```

#### Proposed Model

**Architecture:** N/A — no proposed ML architecture. The "proposed analysis" is:
- Partial Spearman ρ (MMLU-controlled) vs. raw Spearman ρ (uncontrolled)
- N_common audit (proposed) vs. assumed sufficiency (prior assumption)

**Core Mechanism Implementation:**

```python
import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr, norm

# ── Model Name Standardization ──────────────────────────────────────────
CANONICAL_MAP = {
    "llama-2-7b": "LLaMA-2-7B", "llama2-7b": "LLaMA-2-7B",
    "meta-llama/llama-2-7b-hf": "LLaMA-2-7B",
    "llama-2-7b-chat": "LLaMA-2-7B-Chat", "llama2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "mistral-7b": "Mistral-7B", "mistral-7b-instruct": "Mistral-7B-Instruct",
    "gpt-3.5-turbo": "GPT-3.5-Turbo", "gpt-4": "GPT-4",
    # ... extend as needed
}

def standardize_model_name(raw_name: str) -> str:
    return CANONICAL_MAP.get(raw_name.lower().strip(), raw_name)

# ── Matrix Construction ──────────────────────────────────────────────────
REQUIRED_COLS = ["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE",
                 "ANLI-R1", "ANLI-R3", "MMLU"]
BENCHMARK_PAIRS = [
    ("BBQ-Disambig", "BBQ-Ambig"),
    ("GLUE", "AdvGLUE"),
    ("ANLI-R1", "ANLI-R3"),
]

def build_matrix(score_dicts: dict) -> pd.DataFrame:
    """Build model × benchmark matrix from source dicts."""
    all_models = set()
    for src in score_dicts.values():
        all_models.update(src.keys())
    rows = []
    for model in all_models:
        row = {"model": model}
        for col in REQUIRED_COLS:
            # Source priority: TrustLLM > DecodingTrust > GLUE-X > OOD_NLP > HF-Leaderboard
            for src_name in ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]:
                val = score_dicts.get(src_name, {}).get(model, {}).get(col)
                if val is not None:
                    row[col] = val; break
        rows.append(row)
    return pd.DataFrame(rows).set_index("model")[REQUIRED_COLS]

# ── H-E1 Audit ───────────────────────────────────────────────────────────
def run_h_e1_audit(matrix: pd.DataFrame) -> dict:
    complete = matrix.dropna()
    n_common = len(complete)
    pair_counts = {f"{a}/{b}": matrix[[a, b]].dropna().shape[0]
                   for a, b in BENCHMARK_PAIRS}
    return {
        "N_common": n_common,
        "pair_counts": pair_counts,
        "complete_matrix": complete,
        "gate_passed": n_common >= 10,
        "protocol_warnings": []  # filled by consistency check
    }
```

### Training Protocol

**N/A — No model training.** Data collection and statistical analysis only.

**Analysis Protocol (ordered steps):**

1. **Clone/download all source repositories** (~30 min):
   - `git clone https://github.com/HowieHwong/TrustLLM`
   - Download GLUE-X OOD data from Google Drive link
   - `git clone https://github.com/lifan-yuan/OOD_NLP`
   - `git clone https://github.com/AI-secure/DecodingTrust`

2. **Extract per-model benchmark scores** (~60 min):
   - Parse TrustLLM JSON results for BBQ (disambig/ambig accuracy) and ANLI (R1/R3 accuracy)
   - Extract GLUE-X Table 3 model scores (ID avg, OOD avg per task)
   - Fetch MMLU from HuggingFace `OpenEvals/leaderboard-data` parquet

3. **Build model name canonical mapping** (~30 min):
   - Enumerate all model names across sources
   - Apply CANONICAL_MAP; flag ambiguous cases for manual resolution

4. **Construct model × 7-benchmark matrix** (~15 min):
   - Apply source priority; record which source filled each cell

5. **Run H-E1 audit** (<5 min):
   - Count N_common (all 7 cols present)
   - Count N_per_pair (each benchmark pair)
   - Check protocol consistency (cross-source >5pp deviations)

6. **Gate decision** (<5 min):
   - N_common ≥ 10 → PASS
   - N_common < 10 → PIVOT: supplement from HuggingFace individual model eval pages; restrict scope per Risk R1 mitigation

**Total runtime:** ~2.5–3 hours (dominated by data extraction)

**Seeds:** 1 (deterministic computation — no randomness)

### Evaluation

**Primary Success Criterion:**
- N_common ≥ 10 models with all 7 benchmark scores (gate condition)

**Secondary Criteria:**
- BBQ-Disambig/Ambig cell: N ≥ 10 (critical for H-M1)
- GLUE/AdvGLUE cell: N ≥ 10 (required for H-M2)
- ANLI-R1/R3 cell: N ≥ 10 (required for H-M2)
- MMLU coverage: ≥ 80% of models in intersection

**Metrics:**

| Metric | Definition | Success |
|--------|-----------|---------|
| N_common | Count of models with all 7 scores | ≥ 10 |
| N_BBQ | Count with BBQ-Disambig AND BBQ-Ambig | ≥ 10 |
| N_GLUE | Count with GLUE AND AdvGLUE | ≥ 10 |
| N_ANLI | Count with ANLI-R1 AND ANLI-R3 | ≥ 10 |
| protocol_consistency | Fraction of cross-source pairs within 5pp | ≥ 0.8 |

**PoC Pass Condition:**
1. Audit script runs without error
2. N_common ≥ 10 (gate satisfied)

**Expected Benchmark Performance (from literature):**
- TrustLLM BBQ: 16 models evaluated; BBQ-disambig accuracy ~50–90% depending on model
- GLUE-X: 21 PLMs; GLUE avg 65–89%, AdvGLUE avg 37–75% per model (Table 3, GLUE-X paper)
- ANLI-R1: ~40–65% for decoder-only LLMs per TrustLLM results
- MMLU: ~40–80% for target model set (from HF leaderboard historical data)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Data audit / statistical counting
- Library: pandas, scipy, pingouin (all pip-installable)
- Code:
```python
import pingouin as pg

# For H-M1 preview (partial Spearman ρ, one-tailed):
result = pg.partial_corr(
    data=complete_matrix.reset_index(),
    x='BBQ-Disambig', y='BBQ-Ambig',
    covar='MMLU', method='spearman', alternative='greater'
)
print(f"Partial ρ_fairness = {result['r'].values[0]:.3f}, p = {result['p-val'].values[0]:.4f}")

# H-E1 gate check:
audit = run_h_e1_audit(matrix)
print(f"N_common = {audit['N_common']} → {'PASS' if audit['gate_passed'] else 'FAIL'}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Bar Chart**: Bar chart of N per benchmark pair (BBQ, GLUE/AdvGLUE, ANLI) with horizontal dashed line at N=10, annotated with PASS/FAIL per cell

#### Additional Figures (LLM Autonomous)
- **Model Coverage Heatmap**: model × 7-benchmark matrix; color = score value (white = missing); reveals completeness pattern and model family clustering
- **Source Attribution Treemap or Stacked Bar**: Fraction of scores from each source (TrustLLM / GLUE-X / OOD_NLP / HF-Leaderboard) per benchmark column
- **Protocol Consistency Scatter**: For models scored in multiple sources on same benchmark, scatter of source-A vs source-B score (should cluster near y=x diagonal); identifies cross-paper aggregation bias

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `N_common >= 10` (gate satisfied — proposed metric exceeds baseline threshold)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Overall finding:** Archon KB contains no relevant prior cases for LLM trustworthiness evaluation or predictive validity methodology. KB is populated with computer vision / generative diffusion model content. This is a novel research application area not represented in the KB.

**Queries executed (3 knowledge + 1 code):**
- "Spearman rank correlation LLM benchmark evaluation" → top similarity 0.39 (unrelated)
- "benchmark score aggregation multi-model evaluation challenges" → top similarity 0.43 (unrelated)
- "trustworthiness fairness OOD generalization predictive validity" → top similarity 0.34 (unrelated)
- Code: "partial Spearman correlation pandas scipy statistics" → top similarity 0.29 (unrelated)

**Used for:** Establishing that no prior Archon-stored experiment design exists for this domain; all design grounded in Exa-sourced literature.

### B. GitHub Implementations (Exa)

**Repository B.1**: HowieHwong/TrustLLM (⭐ 628)
- **URL**: https://github.com/HowieHwong/TrustLLM
- **Query**: "TrustLLM HowieHwong benchmark evaluation scores JSON extraction Python"
- **Relevance**: Primary data source — 16 LLMs evaluated across BBQ, ANLI, and 4 other dimensions with consistent protocol
- **Key insight**: Results stored as JSON per model per task in `results/` directory; BBQ-Disambig and BBQ-Ambig are `context_condition` splits within the same BBQ evaluation task
- **Used for**: Dataset specification (primary data source for BBQ and ANLI scores); model list specification

**Repository B.2**: nyu-mll/BBQ (⭐ 141)
- **URL**: https://github.com/nyu-mll/BBQ
- **Query**: "BBQ bias benchmark ANLI dataset score extraction Python pandas"
- **Key insight** (from BBQ_calculate_bias_score.R): `context_condition` field values are "ambig" and "disambig"; accuracy computed per condition using `group_by(category, model, context_condition)`
- **3.4pp finding**: "Models average up to 3.4 percentage points higher accuracy when the correct answer aligns with a social bias" — confirms fairness dimension's bias-signal robustness
- **Used for**: Understanding BBQ-Disambig/Ambig split structure; bias score formula

**Repository B.3**: YangLinyi/GLUE-X (ACL 2023)
- **URL**: https://github.com/YangLinyi/GLUE-X
- **Query**: "GLUE-X YangLinyi OOD benchmark LLM evaluation leaderboard score extraction"
- **Key insight**: "ID and OOD performance holds a linear correlation in most cases for text classifications" (GLUE-X paper) — provides prior evidence for cross-split rank correlation in NLU
- **WARNING**: GLUE-X evaluates PLMs (ELECTRA, RoBERTa, T5, BERT), not decoder-only LLMs. Model overlap with TrustLLM set is likely minimal — this is Risk R1's primary manifestation for the GLUE/AdvGLUE dimension
- **Friedman rank**: GLUE-X uses Friedman rank across tasks (same concept as Spearman rank correlation across models) — methodological precedent
- **OOD data**: Google Drive link in README
- **Used for**: GLUE/AdvGLUE dimension data source; methodological precedent for cross-split rank analysis

**Source B.4**: HuggingFace Open LLM Leaderboard
- **URL**: https://huggingface.co/datasets/open-llm-leaderboard/results
- **Query**: "HuggingFace open_llm_leaderboard datasets API MMLU scores download Python"
- **Key code**: `pd.read_parquet("hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet")` for pre-aggregated cross-benchmark data
- **NOTE**: Current leaderboard uses MMLU-PRO (10-choice). Historical MMLU (4-choice, 5-shot) scores available in individual model result JSONs under `open-llm-leaderboard/results` dataset
- **Used for**: MMLU capability covariate scores; model coverage verification

**Source B.5**: pingouin library
- **URL**: https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Query**: "scipy pingouin partial Spearman rank correlation Python implementation Fisher z-test"
- **Key code**: `pg.partial_corr(data=df, x='BBQ-Disambig', y='BBQ-Ambig', covar='MMLU', method='spearman', alternative='greater')` — one-tailed partial Spearman ρ with 95% CI and Bayes factor
- **Used for**: Core statistical analysis implementation for H-M1 (partial ρ computation); experiment design validation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. This is a data collection and statistical analysis experiment; no complex existing codebase requires semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset sources (TrustLLM, GLUE-X) | GitHub (Exa) | B.1, B.3 |
| BBQ-Disambig/Ambig split structure | GitHub (Exa) | B.1, B.2 |
| MMLU loading via HuggingFace API | HuggingFace (Exa) | B.4 |
| Model name standardization | Literature + B.1 | B.1 |
| Model × 7-benchmark matrix design | Phase 2B roadmap | 02b_verification_plan.md §2.2 |
| N_common gate threshold (≥10) | Phase 2B roadmap | §1.5 Assumption A1; §3.2 Gate Summary |
| Source priority (TrustLLM first) | Risk mitigation R3 | 02b_verification_plan.md §4.2 |
| Protocol consistency check (5pp) | Risk mitigation R3/R5 | 02b_verification_plan.md §4.2 |
| Partial Spearman ρ implementation | GitHub/docs (Exa) | B.5 (pingouin) |
| GLUE-X model family warning | GitHub (Exa) | B.3 |
| Visualization requirements | Step 6 synthesis | This document |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-20T00:00:00+00:00

### Workflow History for This Hypothesis
- 2026-08-20: H-E1 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-08-20: Phase 2C experiment_design.status = IN_PROGRESS
- 2026-08-20: Phase 2C experiment_design.status = COMPLETED (all steps executed)

---

## Quality Validation Results

```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified (N/A — statistical analysis, no training hyperparams)
✅ Dataset choice justified (TrustLLM primary, GLUE-X secondary; Risk R1 documented)
✅ Mechanism grounded in code (partial_corr from pingouin; matrix from pandas; audit logic explicit)
✅ No unsupported assumptions (all N thresholds from Phase 2B; Risk R1 documented)
✅ Full traceability (all specs traced to B.1-B.5 and Phase 2B roadmap)
⚠️  GLUE/AdvGLUE model overlap risk documented (PLM vs LLM family mismatch — Risk R1)

Overall: PASSED (with documented risk)
```

---

*MCP Tools Used: Archon (3 KB queries + 1 code query — no relevant results), Exa (4 GitHub/web queries — 5 sources identified), Serena (not required)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
