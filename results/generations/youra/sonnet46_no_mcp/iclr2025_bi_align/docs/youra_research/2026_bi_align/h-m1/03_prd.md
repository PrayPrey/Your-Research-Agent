# Product Requirements Document (PRD)
# H-M1: Automation-Bias-Mediated Ambiguity-Modulated AI-Norm Internalization

**Generated:** 2026-05-03
**Phase:** 3 - Implementation Planning
**Hypothesis:** H-M1 (MECHANISM / INCREMENTAL / MUST_WORK)
**Tier:** FULL (max 30 tasks)
**Author:** Anonymous
**Base Hypothesis:** H-E1 (COMPLETED, MUST_WORK gate PASSED)

stepsCompleted: [step-01, step-02, step-03, step-04, step-05]

---

## 1. Executive Summary

This PRD specifies implementation requirements for H-M1, the first mechanism test in the Human→AI Annotation Drift pipeline. H-M1 tests whether annotators with higher cumulative AI-text exposure exhibit stronger AI-typicality geometric projection of their preference decisions, with the strongest effect in high-ambiguity prompts — the core automation-bias prediction. H-M1 introduces two novel components over H-E1: (1) AI-typicality geometric projection via frozen all-MiniLM-L6-v2 encoder, and (2) WebGPT panel regression with worker fixed effects for genuine within-annotator dose-response identification.

**Core Question:** Does cumulative AI-text exposure cause annotators to project their preference decisions more strongly onto the AI-typicality direction in embedding space, with the effect moderated by prompt ambiguity?

**Gate:** MUST_WORK — code executes end-to-end; projection scores computable for all samples; WebGPT panel regression estimable. Scientific significance of β_exposure is not required for gate pass.

**Failure Response:** β_exposure ≤ 0 or non-significant → PIVOT to calendar-time cohort explanation (drop individual automation-bias framing, retain general drift observation).

---

## 2. Problem Statement

### 2.1 Research Gap

H-E1 demonstrated that the stylistic coefficient extraction pipeline works end-to-end but found no statistically significant directional drift under equal-partition round stratification (interaction p=1.0). This null result suggests HH-RLHF round-by-index proxy lacks genuine temporal signal. H-M1 pivots to the stronger identification strategy: within-annotator dose-response via WebGPT worker IDs (genuine temporal exposure), combined with a novel geometric measurement — AI-typicality projection in embedding space — that captures stylistic adaptation more directly than coefficient regression.

### 2.2 Hypothesis

Under conditions of verified temporal stylistic drift (H-E1 passed), if annotators with higher cumulative AI-text exposure (operationalized as later rounds in HH-RLHF; cumulative tokens viewed in WebGPT) are faced with high-ambiguity prompts, then their within-round preference patterns will show stronger AI-typicality geometric projection than low-exposure or low-ambiguity counterparts, because automation bias theory predicts strongest AI-norm internalization precisely when annotation uncertainty is highest.

### 2.3 Gate Condition

MUST_WORK: Code must execute end-to-end; AI-typicality geometric projection scores must be computable for all samples; β_exposure coefficient must be estimable in WebGPT panel regression. Scientific significance of results does not determine gate pass/fail.

---

## 3. Scope

### 3.1 In Scope

- WebGPT Comparisons loading with worker_id and timestamp fields (fixing H-E1 deprecated loading)
- HH-RLHF loading (reused from H-E1 validated `data_loader.py`)
- AI-typicality vector construction: centroid difference between AI-generated and human-written texts in frozen all-MiniLM-L6-v2 embedding space
- Geometric projection score computation: cosine projection of preference residuals onto AI-typicality unit vector, after Q_early partialing
- WebGPT panel regression with worker fixed effects: `proj_score_z ~ cumulative_tokens_k + EntityEffects` (linearmodels PanelOLS)
- Ambiguity-modulation interaction test: projection increase in high-ambiguity (κ < 0.4) vs. low-ambiguity stratum (HH-RLHF secondary)
- Discriminant validity: parallel regression on topic-axis projection (first PCA component); verify stylistic > topical
- Placebo test: permute AI/human labels within matched prompt groups (1000 permutations); verify AI-typicality vector dissipates
- Bootstrap 95% CI on β_exposure (1000 iterations)
- 6 figures: dose-response plot, ambiguity-modulation plot, placebo histogram, worker FE distribution, discriminant validity, gate metrics bar chart

### 3.2 Out of Scope

- Neural network fine-tuning (H-M3/H-M4 scope)
- Reward model training (H-M3 scope)
- RLHF PPO training (H-M4 scope)
- New logistic regression (Q_early reused from H-E1 validated code)
- New HH-RLHF data loader (reused from H-E1 `data_loader.py`)

---

## 4. Data Specification

### 4.1 Primary Dataset: OpenAI WebGPT Comparisons

| Field | Value |
|-------|-------|
| Name | OpenAI WebGPT Comparisons |
| Source | HuggingFace Hub: `openai/webgpt_comparisons` |
| Scale | ~19,578 pairwise preference comparisons |
| Fields | `question` (prompt), `answer_0`/`answer_1` (response texts), `score_0`/`score_1` (preference), worker metadata (worker_id, timestamps) |
| Download | `load_dataset("openai/webgpt_comparisons", trust_remote_code=False)` — **auto-download via HuggingFace** |
| Fallback | Direct parquet download if script-based loading fails |
| Cache | `~/.cache/huggingface/datasets/` |
| Role | PRIMARY identification dataset — worker IDs enable within-annotator panel regression |

**Pre-condition check:** At least 100 unique workers with ≥ 3 sessions each required for panel FE power.

**Session construction:** Sort by `worker_id` + timestamp; compute `cumulative_tokens_k` as cumulative sum of token counts viewed per session.

### 4.2 Secondary Dataset: Anthropic HH-RLHF

| Field | Value |
|-------|-------|
| Name | Anthropic HH-RLHF (Human Feedback) |
| Source | HuggingFace Hub: `Anthropic/hh-rlhf` |
| Scale | ~169,000 pairwise preference comparisons (3 rounds, ~53,600 each) |
| Fields | `chosen`, `rejected` (preference pairs); round stratification by equal-partition index |
| Download | `load_dataset("Anthropic/hh-rlhf")` — **auto-download via HuggingFace** (reused from H-E1) |
| Cache | `~/.cache/huggingface/datasets/` (already cached from H-E1) |
| Role | SECONDARY corroboration — ambiguity-modulation interaction test |

**Note:** Both datasets auto-download via HuggingFace. No manual download task required.

### 4.3 Encoder Model

| Field | Value |
|-------|-------|
| Name | all-MiniLM-L6-v2 |
| Source | HuggingFace: `sentence-transformers/all-MiniLM-L6-v2` |
| Architecture | 6-layer MiniLM, 384-dimensional embeddings |
| Usage | FROZEN (eval mode, no gradient updates) |
| Download | `SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")` — auto-download |
| Batch size | 256 for efficient encoding |

---

## 5. Functional Requirements

### FR-1: WebGPT Data Loading (NEW)

- FR-1.1: Load WebGPT Comparisons dataset with `trust_remote_code=False`; fall back to parquet download if loading fails
- FR-1.2: Extract `worker_id`, `question`, `answer_0`, `answer_1`, `score_0`, `score_1`, and timestamp fields
- FR-1.3: Compute `cumulative_tokens_k` per worker: sort by `worker_id` + timestamp; cumsum token counts / 1000
- FR-1.4: Compute `session_order` index per worker for panel multi-index
- FR-1.5: EDA check: verify ≥ 100 unique workers with ≥ 3 sessions each; warn if median sessions < 3
- FR-1.6: Compute ambiguity proxy: `|score_0 - score_1|` < threshold → high ambiguity (where inter-rater agreement not available)

### FR-2: HH-RLHF Loading (REUSED from H-E1)

- FR-2.1: Reuse `h-e1/code/data_loader.py::load_hh_rlhf()` and `stratify_rounds()` — extend for WebGPT, do not rewrite HH-RLHF loading
- FR-2.2: Reuse `h-e1/code/features.py::build_feature_matrix()` for stylistic feature extraction (β_L, β_H, β_S)
- FR-2.3: Reuse `h-e1/code/q_early.py::QEarlyModel` for Q_early covariate (retrain on round-1 HH-RLHF)

### FR-3: AI-Typicality Vector Construction (NEW)

- FR-3.1: Load frozen `all-MiniLM-L6-v2` encoder in eval mode
- FR-3.2: Encode AI-generated texts (HH-RLHF `chosen` texts from round-1) → `ai_embs: [N_ai, 384]`
- FR-3.3: Encode human-written texts (HH-RLHF `rejected` texts from round-1) → `human_embs: [N_human, 384]`
- FR-3.4: Compute centroid difference: `ai_typicality_vec = mean(ai_embs) - mean(human_embs)`; L2-normalize to unit vector
- FR-3.5: Placebo validation: permute AI/human labels within matched prompt groups (1000 permutations); verify centroid difference dissipates (placebo projection near zero)

### FR-4: Geometric Projection Score Computation (NEW)

- FR-4.1: Encode all preference texts (concatenate chosen+rejected or chosen-only as specified) with frozen encoder → `embs: [N, 384]`
- FR-4.2: Compute raw projection: `raw_proj = embs @ ai_typicality_vec` → `[N,]` scalar scores
- FR-4.3: Partial out Q_early: compute residual by regressing raw_proj on q_early_scores; take residuals
- FR-4.4: Z-score normalize residuals: `proj_score_z = (residual - mean) / std`
- FR-4.5: Compute for BOTH WebGPT and HH-RLHF datasets

### FR-5: WebGPT Panel Regression (NEW)

- FR-5.1: Construct panel DataFrame indexed by `(worker_id, session_order)`
- FR-5.2: Fit PanelOLS: `proj_score_z ~ cumulative_tokens_k + EntityEffects` via `linearmodels.panel.PanelOLS`
- FR-5.3: Clustered standard errors by worker: `cov_type="clustered"`, `cluster_entity=True`
- FR-5.4: Extract `β_exposure = res.params["cumulative_tokens_k"]` and `p_exposure = res.pvalues["cumulative_tokens_k"]`
- FR-5.5: Fallback: if `linearmodels` install fails, use `statsmodels` LSDV (Least Squares Dummy Variables)
- FR-5.6: Bootstrap 95% CI on β_exposure (1000 iterations, seed=42)

### FR-6: Ambiguity-Modulation Interaction Test (NEW, HH-RLHF secondary)

- FR-6.1: Compute ambiguity stratum per prompt using Fleiss κ proxy (reuse `h-e1/code/features.py::compute_fleiss_kappa` or score-magnitude proxy)
- FR-6.2: Fit interaction model: `proj_score_z ~ round + high_ambiguity + round × high_ambiguity + q_early` via statsmodels Logit
- FR-6.3: Extract interaction coefficient and p-value; direction: high-ambiguity stratum should show larger projection increase
- FR-6.4: Report: interaction p < 0.05 with positive coefficient = ambiguity modulation confirmed

### FR-7: Discriminant Validity Check (NEW)

- FR-7.1: Compute topic-axis projection: fit PCA on all prompt embeddings; take first PC as topic direction
- FR-7.2: Compute topic projection scores analogously to stylistic projection (FR-4)
- FR-7.3: Run parallel panel regression with topic projection as outcome
- FR-7.4: Assert: `β_exposure_stylistic > β_exposure_topic` — stylistic captures adaptation, not topical drift

### FR-8: Evaluation Metrics

- FR-8.1: **β_exposure**: coefficient from WebGPT panel regression; target β_exposure > 0 (directional, p < 0.05)
- FR-8.2: **Effect size**: ≥ 0.1 SD increase per 1000 cumulative tokens viewed
- FR-8.3: **Ambiguity-modulation interaction**: p < 0.05 with positive interaction coefficient
- FR-8.4: **Discriminant validity**: stylistic β_exposure > topic β_exposure
- FR-8.5: **Placebo test**: projection near zero under AI/human label permutation
- FR-8.6: **HH-RLHF monotonicity**: projection scores increase monotonically across rounds 1→3 (corroborative)

### FR-9: Visualizations (6 figures)

- FR-9.1: **Dose-Response Plot**: scatter of proj_score_z vs. cumulative_tokens_k per worker (WebGPT) with regression line and worker-level means
- FR-9.2: **Ambiguity-Modulation Plot**: side-by-side projection distributions for high- vs. low-ambiguity strata across rounds (HH-RLHF)
- FR-9.3: **AI-Typicality Vector Placebo**: histogram of projection scores under label permutation vs. observed (specificity check)
- FR-9.4: **Worker Fixed Effects Distribution**: distribution of worker-level intercepts from panel regression
- FR-9.5: **Discriminant Validity Plot**: side-by-side β_exposure for stylistic vs. topic-axis projection
- FR-9.6: **Gate Metrics Bar Chart**: target vs. actual β_exposure, p-value, effect size vs. thresholds
- All figures saved to `h-m1/figures/`

### FR-10: Pipeline Integration

- FR-10.1: Main entry point `run_experiment.py::main()` orchestrates full pipeline
- FR-10.2: Gate logic: MUST_WORK gate PASSES if code executes end-to-end and projection scores are computable
- FR-10.3: Results serialized to `h-m1/results/results.yaml` with all metrics
- FR-10.4: Mechanism log message: `"AI-typicality projection computed: mean={:.3f}, std={:.3f}; β_exposure={:.4f} (p={:.4f})"`

---

## 6. Non-Functional Requirements

### 6.1 Performance

- Wall-clock estimate: ~1–2 hours (encoder pass: ~19K WebGPT + ~169K HH-RLHF, panel regression, bootstrap)
- Batch encoding: `batch_size=256` for all-MiniLM-L6-v2 to fit memory
- Single GPU: use `CUDA_VISIBLE_DEVICES=<empty_gpu>` if GPU available; CPU fallback for encoder if needed

### 6.2 Reproducibility

- Fixed random seed: `random_state=42` everywhere
- Bootstrap seed: `seed=42`
- Permutation seed: `seed=42`

### 6.3 Reusability (H-E1 Components)

| Component | File | Usage in H-M1 |
|-----------|------|---------------|
| HH-RLHF loader | `h-e1/code/data_loader.py` | Import `load_hh_rlhf`, `stratify_rounds` |
| Feature extraction | `h-e1/code/features.py` | Import `build_feature_matrix`, `partition_by_ambiguity` |
| Q_early model | `h-e1/code/q_early.py` | Import `QEarlyModel`; retrain on round-1 |
| Bootstrap CI | `h-e1/code/analysis.py` | Import `bootstrap_coefficient_ci` pattern |
| Visualization utilities | `h-e1/code/visualize.py` | Extend for projection-specific plots |

**Import paths (verified from actual H-E1 code):**
```python
import sys
sys.path.insert(0, "../h-e1/code")
from data_loader import load_hh_rlhf, stratify_rounds
from features import build_feature_matrix, partition_by_ambiguity, compute_fleiss_kappa
from q_early import QEarlyModel
from analysis import apply_bonferroni, bootstrap_coefficient_ci
```

---

## 7. Dependencies

### 7.1 Python Packages (NEW for H-M1)

| Package | Version | Usage |
|---------|---------|-------|
| `sentence-transformers` | ≥2.2.2 | all-MiniLM-L6-v2 frozen encoder |
| `linearmodels` | ≥4.28 | PanelOLS with entity FE, clustered SE |
| `datasets` (HuggingFace) | ≥2.14.0 | WebGPT loading (already in H-E1) |

**Inherited from H-E1 (already installed):**
- `numpy`, `scipy`, `pandas`, `scikit-learn`, `statsmodels`, `matplotlib`, `seaborn`, `pytest`, `pyyaml`, `tqdm`

### 7.2 External Repositories (Reference Only)

| Repository | Usage |
|-----------|-------|
| `UKPLab/sentence-transformers` | Primary encoder library |
| `bashtage/linearmodels` | Panel regression with worker FE |
| `openai/webgpt_comparisons` (HuggingFace) | Primary dataset |
| `Anthropic/hh-rlhf` (HuggingFace) | Secondary dataset (reused from H-E1) |

---

## 8. Success Criteria

### 8.1 MUST_WORK Gate (PoC)

| Criterion | Requirement |
|-----------|-------------|
| Code executes end-to-end | No uncaught exceptions |
| AI-typicality projection scores computable | All WebGPT + HH-RLHF samples have proj_score_z |
| WebGPT panel regression estimable | β_exposure coefficient is a finite float |

### 8.2 Scientific Success (PoC direction-based)

| Criterion | Target |
|-----------|--------|
| β_exposure direction | > 0 |
| β_exposure significance | p < 0.05 (one-sided) |
| Effect size | ≥ 0.1 SD per 1000 cumulative tokens viewed |
| Ambiguity-modulation interaction | p < 0.05, positive coefficient |
| Discriminant validity | Stylistic β > Topic β |
| Placebo specificity | Near-zero projection under permutation |

### 8.3 Failure Response

| Condition | Action |
|-----------|--------|
| β_exposure ≤ 0 or non-significant | PIVOT: test calendar-time cohort prediction |
| WebGPT worker IDs unavailable | FALLBACK: between-worker tercile comparison |
| Ambiguity interaction absent | DOCUMENT: boundary condition failure; narrow scope |
| Low panel power (< 3 sessions/worker) | WARN: report as PoC limitation |

---

## 9. File Structure

```
docs/youra_research/20260503_bi_align/h-m1/
├── code/
│   ├── config.py              # H-M1 hyperparameters, paths, encoder settings
│   ├── data_loader_webgpt.py  # WebGPT loading, session construction, cumulative tokens
│   ├── encoder.py             # Frozen all-MiniLM-L6-v2 encoder wrapper
│   ├── projection.py          # AI-typicality vector, projection scores, Q_early partialing
│   ├── panel_regression.py    # PanelOLS + LSDV fallback, clustered SE
│   ├── interaction_test.py    # Ambiguity-modulation interaction, discriminant validity
│   ├── visualize.py           # 6 figures for H-M1 (extends h-e1/visualize.py patterns)
│   └── run_experiment.py      # Main pipeline entry point
├── figures/                   # 6 saved figures
├── results/
│   └── results.yaml           # Serialized experiment results
├── tests/
│   └── test_*.py              # Unit tests for all modules
├── 02b_context.md
├── 02c_experiment_brief.md
├── 03_prd.md                  # This file
├── 03_architecture.md         # To be generated
├── 03_logic.md                # To be generated
├── 03_config.md               # To be generated
└── 03_tasks.yaml              # To be generated
```

---

## 10. Ablation Variants

| Variant | Description | Implementation |
|---------|-------------|----------------|
| **Between-worker fallback** | Replace panel FE with between-worker tercile comparison if worker_id unavailable | `panel_regression.py::run_tercile_comparison()` |
| **Calendar-time pivot** | Use calendar date as exposure proxy instead of cumulative tokens | `panel_regression.py::run_calendar_time_regression()` |
| **LSDV fallback** | statsmodels LSDV if linearmodels install fails | `panel_regression.py::run_lsdv_fallback()` |
| **Topic-only baseline** | PCA topic projection without stylistic projection | `projection.py::compute_topic_projection()` |
| **HH-RLHF projection only** | Run projection pipeline on HH-RLHF only (no WebGPT panel) | `run_experiment.py` `--hh-only` flag |
