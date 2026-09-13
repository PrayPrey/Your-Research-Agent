# Product Requirements Document: H-E1
# Fuzzy Join Data Infrastructure Viability for LLM Alignment Analysis

---
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Data Specification
  - Success Criteria
  - Dependencies
---

## 1. Executive Summary

This PRD defines implementation requirements for H-E1: verifying that a rapidfuzz WRatio fuzzy join of Open LLM Leaderboard v1 and HELM Lite v1.9.0 BBQ scores yields N≥30 open-weight LLMs with complete TruthfulQA MC2, BBQ accuracy, and MMLU scores simultaneously. This is a MUST_WORK EXISTENCE hypothesis — the entire downstream analysis chain depends on this data infrastructure being viable.

**Hypothesis Gate:** N_complete ≥ 30 AND match_rate ≥ 0.55

---

## 2. Problem Statement

To investigate whether LLM truthfulness (TruthfulQA MC2) correlates with social bias (BBQ accuracy) and general capability (MMLU), we need a unified dataset joining two separate benchmark sources. The primary technical challenge is model name normalization across sources (e.g., "meta-llama/Llama-2-7b-hf" vs "meta-llama/Llama-2-7B-hf"). This experiment validates that fuzzy string matching can achieve sufficient coverage (N≥30 models) to enable downstream Spearman partial correlation analysis.

---

## 3. Functional Requirements

### FR-1: Data Acquisition — LLM Leaderboard v1
- Download LLM LB v1 CSV from `fboulnois/llm-leaderboard-csv` GitHub release v1.3.0
- URL pre-flight HEAD check (requests.head) — abort with descriptive error if non-200
- Extract columns: `model_name`, `TruthfulQA_MC2`, `MMLU`
- Filter: open-weight models only (exclude GPT-4, Claude, Gemini API-only models)
- Expected rows: ~300+ open-weight LLMs

### FR-2: Data Acquisition — BBQ Scores (HELM Lite)
- Load HELM Lite v1.9.0 per-model BBQ accuracy scores
- Source: `stanford-crfm/helm-lite` HuggingFace dataset OR direct HELM results CSV
- **NOTE:** `lighteval/bbq_helm` is a QA item corpus (11,864 rows of questions), NOT per-model scores — do NOT use it as BBQ score source
- Extract columns: `model_name`, `bbq_accuracy` (mean across BBQ bias subsets)
- Expected rows: ~79 models

### FR-3: Exact-Match Baseline Join
- Perform exact `pd.merge(df_llm, df_bbq, on='model_name', how='inner')` as baseline
- Record N_exact for comparison with fuzzy join
- Demonstrating fuzzy > exact validates the mechanism

### FR-4: Fuzzy Join (Primary Mechanism)
- Apply rapidfuzz WRatio fuzzy join at threshold=75
- Use `process.extractOne` with `scorer=fuzz.WRatio`, `processor=utils.default_process`
- Match each BBQ model name to best LLM LB model name candidate
- Build match DataFrame; merge with both source DataFrames

### FR-5: Fallback Mechanism
- If match_rate < 0.55 after WRatio join: retry with `token_set_ratio` at threshold=70, then 65
- Log which fallback was triggered

### FR-6: Completeness Count
- After join, apply `dropna(subset=["TruthfulQA_MC2", "bbq_accuracy", "MMLU"])`
- Count N_complete = len(df_complete)
- Gate evaluation: N_complete ≥ 30 AND match_rate ≥ 0.55

### FR-7: Mechanism Verification
- Log match activation indicators:
  - "Fuzzy join completed: N_matched=X, match_rate=Y.YYY"
  - fuzzy_beats_exact: N_complete > N_exact
  - gate_passed: N_complete ≥ 30
- Call `verify_mechanism_activated()` function

### FR-8: Threshold Sensitivity Analysis (Ablation)
- Run join at thresholds: [65, 70, 75, 80]
- Record N_complete at each threshold
- Output sensitivity table

### FR-9: Visualization Output
- **Figure 1 (Mandatory):** Bar chart — N_complete vs gate threshold=30, match_rate vs gate threshold=0.55
- **Figure 2:** Histogram of WRatio scores for matched pairs
- **Figure 3:** Venn diagram — LLM LB v1 models vs BBQ models vs matched set
- **Figure 4:** Line plot — N_complete vs threshold (65, 70, 75, 80)
- Save all figures to `docs/youra_research/h-e1/figures/`

---

## 4. Data Specification

### Primary Dataset: LLM Leaderboard v1
- **Source:** `https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv`
- **Type:** Static CSV (GitHub release asset)
- **Cache Path:** `./data/llm_leaderboard_v1/llm.csv`
- **Key Columns:** `model_name`, `TruthfulQA_MC2` (0-100), `MMLU` (0-100)
- **Filter:** Open-weight only (exclude proprietary API models)
- **Download Method:** `requests.get(url)` — manual download required

### Secondary Dataset: HELM Lite BBQ Scores
- **Source:** `stanford-crfm/helm-lite` (HuggingFace) OR HELM results page CSV
- **Type:** Programmatic API (`datasets.load_dataset` or direct CSV)
- **Cache Path:** `./data/bbq_scores/bbq_per_model.csv`
- **Key Columns:** `model_name`, `bbq_accuracy` (mean across BBQ subsets)
- **Expected Size:** ~79 models
- **Download Method:** `datasets.load_dataset("stanford-crfm/helm-lite")` — manual setup required

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=42 for any randomized steps
- All data cached locally after first download
- Script idempotent: re-runs produce identical output if data unchanged

### NFR-2: Performance
- Total execution time ≤ 5 minutes on CPU (data pipeline, no ML training)
- rapidfuzz `process.extractOne` is O(n×m) — acceptable for ~300×79 pairs

### NFR-3: Error Handling
- URL pre-flight check MUST run before any download attempt
- Descriptive error messages for: non-200 URL, dataset unavailable, N < 30 gate failure
- Data availability failure (HELM Lite unavailable) is reported as explicit failure, not silently handled

### NFR-4: Logging
- Print N_complete, match_rate, gate pass/fail at completion
- Print threshold sensitivity table

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate Pass | N_complete ≥ 30 | `len(df_complete)` after dropna |
| Match Rate | match_rate ≥ 0.55 | N_matched / N_bbq |
| Mechanism Activated | fuzzy_beats_exact | N_complete > N_exact |
| Code Runs Clean | No exceptions | End-to-end execution |

**MUST_WORK gate:** Both N_complete ≥ 30 AND match_rate ≥ 0.55 must hold.

---

## 7. Dependencies

### 7.1 Python Packages
```
rapidfuzz>=3.0
pandas>=1.5
datasets>=2.0
requests>=2.28
matplotlib>=3.5
matplotlib-venn>=0.11
scipy>=1.9
numpy>=1.21
PyYAML>=6.0
```

### 7.2 External Data Sources
- `fboulnois/llm-leaderboard-csv` v1.3.0 (GitHub release — static, archived)
- `stanford-crfm/helm-lite` (HuggingFace dataset — HELM Lite v1.9.0 BBQ scores)

### 7.3 Reference Repositories
- `rapidfuzz/RapidFuzz` — WRatio algorithm reference (Issue #359)

---

## 8. Out of Scope

- Running LLM evaluations to produce BBQ scores (H-E1 uses pre-computed scores only)
- Spearman partial correlation analysis (downstream Phase 4+ hypotheses)
- Fine-tuning or training any model

---

*Generated: 2026-07-30 | Hypothesis: H-E1 | Phase: 3 - Implementation Planning*
*Source: Phase 2C experiment brief (02c_experiment_brief.md)*
