# Product Requirements Document: H-E1
# AIFS Conditional Preference Shift Detection in HH-RLHF

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-05-12
**Author:** Anonymous
**Source:** 02c_experiment_brief.md
**Gate:** MUST_WORK — β₄ > 0, OR ≥ 1.10, p < 0.01

---

## Executive Summary

This PRD specifies the implementation requirements for H-E1: verifying that deployed-condition RLHF annotators (helpful-online split) show significantly higher conditional preference for AI-idiomatic features (AIFS) compared to naive annotators (helpful-base split). The experiment uses the HH-RLHF dataset, automated regex-based AIFS feature extraction, semantic prompt clustering via all-MiniLM-L6-v2, and conditional logistic regression (statsmodels ConditionalLogit) with an annotator-condition interaction term β₄. This is a statistical analysis experiment — no neural network training is required.

**Success Gate (MUST_WORK):** β₄ > 0, OR ≥ 1.10, 95% CI excludes 1.0, p < 0.01

---

## Problem Statement

Standard RLHF literature measures AI-to-human alignment only. H-E1 tests the reverse: whether annotators adapt toward AI-native discourse norms (human-to-AI stylistic adaptation). No prior implementation exists for β₄ annotator condition interaction in preference corpora — this is a novel analysis. The null hypothesis is β₄ = 0 (no annotator condition effect).

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**Priority:** P0 (Critical)

- FR-1.1: Load HH-RLHF helpful-base split via `load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")`
- FR-1.2: Load HH-RLHF helpful-online split via `load_dataset("Anthropic/hh-rlhf", data_dir="helpful-online")`
- FR-1.3: Assign split labels: `split=0` (helpful-base, naive annotators), `split=1` (helpful-online, deployed-condition)
- FR-1.4: Extract final assistant turn from chosen/rejected using common-prefix dialogue parsing (TRL pattern)
- FR-1.5: Filter pairs — keep only where both chosen and rejected have ≥ 20 tokens
- FR-1.6: Combine both splits into single DataFrame with `split` column
- FR-1.7: Expected sizes: helpful-base ~43,835 train pairs; helpful-online ~36,169 train pairs

### FR-2: AIFS Feature Extraction

**Priority:** P0 (Critical)

- FR-2.1: Implement regex-based AIFS score extraction with 4 feature categories:
  - `structured_list`: `^\s*(\d+\.|\*|-)\s` (bullet/numbered list patterns)
  - `safety_preface`: `\b(I (cannot|should not|must not)|please note|important:)\b`
  - `cot_marker`: `\b(step \d+|first,|second,|finally,|let('s| us))\b`
  - `hedging`: `\b(however,|that said,|it depends|on the other hand)\b`
- FR-2.2: Compute normalized AIFS score = total pattern hits / token count × 100
- FR-2.3: Compute `delta_aifs` = AIFS(chosen) - AIFS(rejected) for each pair
- FR-2.4: Compute `delta_length` = len(chosen.split()) - len(rejected.split())

### FR-3: Semantic Prompt Clustering

**Priority:** P0 (Critical)

- FR-3.1: Encode all unique prompts using `sentence-transformers/all-MiniLM-L6-v2` (frozen, no fine-tuning)
- FR-3.2: Use batch_size=512 for encoding; max_seq_length=256
- FR-3.3: Compute cosine similarity matrix using `util.cos_sim()`
- FR-3.4: Assign cluster IDs via greedy clustering at cosine threshold 0.85
- FR-3.5: Validate: ≥ 100 clusters with ≥ 2 preference pairs each (required for conditional logit)
- FR-3.6: Log cluster count and size distribution

### FR-4: Conditional Logistic Regression

**Priority:** P0 (Critical)

- FR-4.1: Build pairwise feature DataFrame with columns: `chosen`, `delta_aifs`, `delta_length`, `delta_aifs_x_split`, `split`, `cluster_id`
- FR-4.2: Fit baseline model (no interaction): `chosen ~ delta_aifs + delta_length` with cluster groups
- FR-4.3: Fit proposed model (with interaction): `chosen ~ delta_aifs + delta_length + delta_aifs_x_split` with cluster groups
- FR-4.4: Use `statsmodels.discrete.conditional_models.ConditionalLogit`; optimizer = scipy BFGS (default)
- FR-4.5: Fit extended model with supply control covariate (`supply_prop` per cluster)

### FR-5: Mechanism Verification

**Priority:** P0 (Critical)

- FR-5.1: Verify mechanism activation before model fitting:
  - `beta4_fitted`: `delta_aifs_x_split` in result.params.index
  - `data_variance`: df_pairs["delta_aifs"].std() > 0.01
  - `split_balanced`: df_pairs["split"].value_counts().min() > 1000
  - `clusters_valid`: df_pairs["cluster_id"].nunique() >= 100
  - `effect_nonzero`: abs(result.params["delta_aifs_x_split"]) > 1e-6
- FR-5.2: Abort with informative error if any pre-condition fails

### FR-6: Evaluation Metrics

**Priority:** P0 (Critical)

- FR-6.1: Extract β₄ (interaction coefficient `delta_aifs_x_split`)
- FR-6.2: Compute OR = exp(β₄)
- FR-6.3: Compute 95% CI: [exp(β₄ - 1.96·SE), exp(β₄ + 1.96·SE)]
- FR-6.4: Extract p-value from `result.pvalues["delta_aifs_x_split"]`
- FR-6.5: Compute McFadden R² = 1 - (llf / llnull) for both models
- FR-6.6: Apply success gate check: β₄ > 0 AND OR ≥ 1.10 AND p < 0.01 AND CI_lo > 1.0
- FR-6.7: Save results to `h-e1/results/metrics.json`

### FR-7: Visualization

**Priority:** P1 (High)

- FR-7.1: **Required figure** — Gate Metrics Comparison: bar chart of OR (proposed) vs OR=1.0 (null), with 95% CI error bars
- FR-7.2: β₄ Forest Plot: coefficient estimate with CI across model specifications (baseline, supply-control, perplexity)
- FR-7.3: AIFS Score Distribution: violin plot of AIFS scores for chosen vs rejected, split by annotator condition
- FR-7.4: Cluster Size Distribution: histogram of semantic cluster sizes
- FR-7.5: OR Sensitivity Plot: OR estimates across cosine thresholds (0.75, 0.80, 0.85, 0.90)
- FR-7.6: Save all figures to `h-e1/figures/`

### FR-8: Baseline Model (Ablation)

**Priority:** P1 (High)

- FR-8.1: Null model (no interaction term): `chosen ~ delta_aifs + delta_length` with cluster FE
- FR-8.2: Supply-control model: add `supply_prop` covariate per cluster
- FR-8.3: Perplexity model: add `delta_perplexity` covariate (compute via token length proxy)
- FR-8.4: Report LRT (Likelihood Ratio Test) comparing baseline vs proposed model

### FR-9: Reproducibility

**Priority:** P1 (High)

- FR-9.1: Fix random seed = 1 for any stochastic operations
- FR-9.2: Save full model results to `h-e1/results/model_summary.txt`
- FR-9.3: Save DataFrame to `h-e1/results/pairs_df.parquet` for reproducibility
- FR-9.4: Log all experiment steps with timestamps to `h-e1/results/experiment.log`

---

## Non-Functional Requirements

### NFR-1: Performance
- NFR-1.1: Full pipeline (data loading → clustering → model fitting → evaluation) completes within 60 minutes on CPU
- NFR-1.2: Sentence-transformer encoding uses batch_size=512 for efficiency
- NFR-1.3: No GPU required (statistical model); GPU optional for sentence-transformer encoding

### NFR-2: Infrastructure (LIGHT Tier)
- NFR-2.1: Configuration via hardcoded constants or argparse (no YAML config required)
- NFR-2.2: Logging via print statements + CSV/JSON output (no WandB required)
- NFR-2.3: Testing via smoke test (verify data loads, model fits, results non-null)

### NFR-3: Dependencies
- NFR-3.1: Python ≥ 3.9
- NFR-3.2: `datasets` (HuggingFace)
- NFR-3.3: `sentence-transformers` ≥ 2.2
- NFR-3.4: `statsmodels` ≥ 0.14
- NFR-3.5: `pandas`, `numpy`, `scipy`, `matplotlib`, `scikit-learn`
- NFR-3.6: No GPU-specific packages required (torch CPU-only acceptable)

---

## Success Criteria

| Criterion | Threshold | Measurement Method |
|-----------|-----------|-------------------|
| β₄ > 0 | Positive interaction coefficient | `result.params["delta_aifs_x_split"]` |
| OR ≥ 1.10 | Odds ratio at least 10% above null | `np.exp(beta4)` |
| p < 0.01 | Statistically significant | `result.pvalues["delta_aifs_x_split"]` |
| 95% CI excludes 1.0 | CI lower bound > 1.0 | `np.exp(beta4 - 1.96*se)` |
| Mechanism activated | All 5 indicators pass | `verify_mechanism_activated()` |
| Code runs without error | Zero exceptions in full pipeline | Smoke test pass |

**Gate Type:** MUST_WORK — failure triggers pipeline pivot (reframe as population heterogeneity study or investigate AIFS construct validity)

---

## Data Specifications

| Item | Specification |
|------|--------------|
| Primary Dataset | HH-RLHF (`Anthropic/hh-rlhf`) |
| Splits Used | helpful-base (naive, split=0), helpful-online (deployed, split=1) |
| Total Pairs | ~80,004 train pairs (43,835 base + 36,169 online) |
| Format | JSONL: `{"chosen": "...", "rejected": "..."}` |
| Preprocessing | Dialogue extraction (TRL pattern), ≥20 token filter |
| License | MIT |

---

## Dependencies and Assumptions

- HH-RLHF dataset publicly accessible via HuggingFace `datasets`
- helpful-online split correctly represents deployed-condition annotators (confirmed via anthropics/hh-rlhf dataset documentation)
- Sufficient semantic overlap between helpful-base and helpful-online prompts to form ≥ 100 clusters at cosine ≥ 0.85
- statsmodels ConditionalLogit converges within 200 iterations for cluster-grouped data

---

## Out of Scope

- Neural network training or fine-tuning
- GPU-dependent operations (GPU optional for encoding only)
- Real-time inference or deployment
- Hypotheses H-M1 through H-M4 (handled in subsequent phases)
- WandB/MLflow experiment tracking
- Docker containerization

---

## File Structure

```
h-e1/
├── 02c_experiment_brief.md      # Phase 2C input (exists)
├── 03_prd.md                    # This document
├── 03_architecture.md           # Phase 3 architecture (to be created)
├── 03_logic.md                  # Phase 3 logic (to be created)
├── 03_config.md                 # Phase 3 config (to be created)
├── 03_tasks.yaml                # Phase 3 tasks (to be created)
├── code/
│   ├── data_prep.py             # FR-1, FR-2, FR-3
│   ├── experiment.py            # FR-4, FR-5
│   ├── evaluate.py              # FR-6
│   └── visualize.py             # FR-7
├── figures/                     # FR-7 output
└── results/                     # FR-6, FR-9 output
    ├── metrics.json
    ├── model_summary.txt
    ├── pairs_df.parquet
    └── experiment.log
```

---

*Generated by Phase 3 Implementation Planning — Step 2 (PRD)*
*Hypothesis: H-E1 | Type: EXISTENCE | Budget Tier: LIGHT (max 15 tasks)*
*Source: 02c_experiment_brief.md | Gate: MUST_WORK*
