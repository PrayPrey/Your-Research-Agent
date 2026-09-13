# Phase 4 Validation Report: h-e1

**Generated:** 2026-05-12T10:51:00Z
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Type** | EXISTENCE / FOUNDATION |
| **Statement** | Under RLHF preference annotation with multi-condition collection (deployed vs. naive annotators), if AIFS features are measured via automated regex extraction and preference pairs are matched by semantic cluster, then deployed-condition annotators show significantly higher conditional selection preference for AI-idiomatic features (β₄ > 0, OR ≥ 1.10, p < 0.01). |
| **Gate Type** | MUST_WORK |
| **Gate Result** | **FAIL** |
| **Duration** | ~34 minutes (2037.7s) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 |
| Completed | 15 |
| Coder-Validator Cycles | 1/5 |
| Tests Written | 34 |
| Tests Passed | 34/34 |
| SDD Compliance | ✓ |

### Generated Files

| File | Lines | Purpose |
|------|-------|---------|
| `code/data_prep.py` | 215 | Data loading, AIFS extraction, clustering |
| `code/experiment.py` | 141 | ConditionalLogit model fitting, mechanism verification |
| `code/evaluate.py` | 114 | Metrics extraction, gate check, output saving |
| `code/visualize.py` | 191 | 5 research figures |
| `code/run_experiment.py` | 199 | End-to-end pipeline orchestration |
| `code/tests/test_data_prep.py` | 146 | 15 spec compliance tests |
| `code/tests/test_evaluate.py` | ~80 | 10 gate/metrics tests |
| `code/tests/test_experiment.py` | ~90 | 9 model fitting tests |

---

## Code Quality Checklist

- [✓] All 34 unit tests pass
- [✓] API signatures match `03_logic.md` exactly
- [✓] Constants match `03_config.md` specifications
- [✓] Type hints implemented throughout
- [✓] Error handling with informative messages
- [✓] AIFS_PATTERNS: 4 regex patterns (structured_list, safety_preface, cot_marker, hedging)
- [✓] ConditionalLogit with groups=cluster_id implemented
- [✓] Mechanism verification (5 indicators) implemented
- [✓] Gate logic: β₄>0 AND OR≥1.10 AND pval<0.01 AND CI_lo>1.0

---

## Data Setup

| Item | Value |
|------|-------|
| **Dataset** | Anthropic/hh-rlhf (HuggingFace) |
| **helpful-base (train)** | 43,835 rows → 20,108 after filtering |
| **helpful-online (train)** | 22,007 rows → 20,063 after filtering |
| **Total pairs** | 40,171 prompts clustered |
| **df_pairs shape** | 80,342 rows × 6 columns |
| **Clustering** | sentence-transformers/all-MiniLM-L6-v2, cosine threshold=0.85 |
| **Unique clusters** | 27,034 |
| **Cluster validation** | PASSED (>100 clusters with ≥2 pairs) |

---

## Experiment Results

### Mechanism Verification (All 5 Passed ✓)

| Indicator | Result |
|-----------|--------|
| beta4_fitted | ✓ True |
| data_variance | ✓ True |
| split_balanced | ✓ True |
| clusters_valid | ✓ True |
| effect_nonzero | ✓ True |

### Model Summary (Conditional Logit — Proposed Model)

```
Conditional Logit Model Regression Results
==========================================
No. Observations:  80,342
No. groups:        27,034
Min group size:    2
Max group size:    78
Mean group size:   3.0
Method:            newton (BFGS fallback)

Coefficients:
  x1 (delta_aifs):          β = 0.0246  (p < 0.001) ***
  x2 (delta_length):        β = 0.0008  (p < 0.001) ***
  x3 (delta_aifs_x_split):  β = -0.0016 (p = 0.796)  [not significant]
```

### Key Metrics

| Metric | Value | Gate Threshold | Status |
|--------|-------|----------------|--------|
| **β₄ (delta_aifs_x_split)** | -0.0016 | > 0 | ❌ FAIL |
| **OR = exp(β₄)** | 0.9984 | ≥ 1.10 | ❌ FAIL |
| **p-value** | 0.7958 | < 0.01 | ❌ FAIL |
| **CI_lo = exp(CI_lower)** | 0.9861 | > 1.0 | ❌ FAIL |
| **CI_hi = exp(CI_upper)** | 1.0108 | — | — |
| **LRT statistic** | 0.067 | — | — |
| **LRT p-value** | 0.7957 | — | — |
| **McFadden R² (baseline)** | NaN | — | — |
| **McFadden R² (proposed)** | NaN | — | — |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | **FAIL** |
| **Satisfied** | False |
| **Failed Criteria** | β₄ ≤ 0, OR < 1.10, p > 0.01, CI_lo < 1.0 (all 4 criteria failed) |

### Gate Failure Analysis

The proposed model shows **no statistically significant interaction effect** between AIFS feature density and annotator condition (online vs. base). Key observations:

1. **β₄ is negative** (-0.0016): The direction is opposite to the hypothesis. Online annotators show *no preference increase* for AI-idiomatic features relative to base annotators.
2. **OR = 0.998**: Essentially null (1.0 = no effect); far below the 1.10 threshold.
3. **p = 0.796**: No statistical signal whatsoever.
4. **x1 (delta_aifs) is significant** (β=0.025, p<0.001): AIFS scores do predict preference overall (chosen responses have higher AIFS scores), but this effect does **not differ between online and base annotators**.
5. **Convergence issues**: BFGS failed, Newton optimizer used; Hessian inversion warning for some models.

### Interpretation

The AIFS feature density predicts human preference (β₁ = 0.025, p < 0.001) — annotators generally prefer AI-idiomatic responses. However, the critical interaction term (β₄, online vs. base condition) is near-zero and non-significant. This means:

- **The adaptation effect hypothesis is not supported**: Deployed-condition annotators do not show measurably stronger preference for AIFS features than naive annotators.
- This could indicate: (a) the effect is real but underpowered, (b) helpful-base/helpful-online splits do not cleanly separate naive vs. deployed annotators, or (c) the adaptation effect operates through a different mechanism.

---

## Next Steps

**Gate Type:** MUST_WORK → **FAIL** routes to **Phase 0** (hypothesis redesign)

Per the failure routing protocol:
- `phase4_must_work_fail` → route to Phase 0
- Hypothesis h-e1 marked as **FAILED**
- Dependent hypotheses (h-m1 through h-m4) remain BLOCKED

### Recommendations for Redesign (Phase 0/2A)

1. **Annotator condition proxy**: The helpful-base/helpful-online split may not reliably capture naive vs. deployed-AI-exposed annotators. Consider using explicit annotator metadata if available.
2. **Alternative datasets**: UltraFeedback or LMSYS-Chat-1M with explicit annotator familiarity data.
3. **Coarser AIFS granularity**: Aggregate AIFS patterns to document-level rather than response-level to reduce noise.
4. **Longitudinal design**: The adaptation hypothesis requires temporal data (same annotators before/after AI exposure) which HH-RLHF lacks.
5. **Effect size reduction**: Relax OR threshold from 1.10 to 1.05 for initial feasibility test.

---

## Phase 2C Handoff

### Proven Components (Reusable)

| Component | File | Status | Evidence |
|-----------|------|--------|----------|
| AIFS regex extractor | `code/data_prep.py` | ✓ Validated | β₁=0.025, p<0.001 — AIFS predicts preference |
| Semantic clustering | `code/data_prep.py` | ✓ Validated | 27,034 clusters from 40K prompts |
| ConditionalLogit pipeline | `code/experiment.py` | ✓ Validated | Converges on 80K rows |
| Mechanism verifier | `code/experiment.py` | ✓ Validated | All 5 indicators pass |
| Gate evaluator | `code/evaluate.py` | ✓ Validated | Correctly reports FAIL |
| Figure generator | `code/visualize.py` | ✓ Validated | All 5 figures produced |

### Optimal Configuration (for dependent hypotheses)

```yaml
dataset:
  name: Anthropic/hh-rlhf
  verification_mode: no_checks  # Required to bypass metadata mismatch
  helpful_base_rows: 43835
  helpful_online_rows: 22007
  after_filter_base: 20108
  after_filter_online: 20063

clustering:
  model: sentence-transformers/all-MiniLM-L6-v2
  cosine_threshold: 0.85
  batch_size: 512
  unique_clusters: 27034  # at threshold=0.85 on full dataset

model:
  optimizer: newton  # BFGS fails on full dataset; newton more stable
  max_iter: 200
  groups: cluster_id
  runtime: ~11 minutes (model fitting on 80K rows)
```

### Lessons Learned

**What Worked:**
- AIFS regex extraction is fast and produces meaningful signal (β₁ significant)
- Sentence-transformer clustering at 0.85 threshold produces adequate cluster diversity
- ConditionalLogit with newton optimizer converges reliably on 80K+ rows
- `verification_mode="no_checks"` needed for HH-RLHF dataset loading

**What Didn't Work:**
- The online/base split does not capture annotator AI-exposure as intended
- BFGS optimizer fails to compute Hessian on large dataset; fallback to newton required
- McFadden R² unavailable from ConditionalLogit (no llnull attribute)
- Results path was relative to working directory; must run from correct directory

**Key Insight:**
The AIFS signal is real (β₁ = 0.025, p < 0.001) — AI-idiomatic features genuinely predict preference. The adaptation hypothesis (interaction effect) is the missing piece. Future experiments should directly measure annotator AI exposure rather than using dataset split as a proxy.

### Warnings for Dependent Hypotheses

- h-m1 through h-m4 are all BLOCKED pending h-e1 gate satisfaction
- The AIFS regex pipeline is reusable as-is for h-m1 (RLHF vs pre-LLM comparison)
- Clustering code is directly reusable

---

## Figures Generated

| Figure | File | Description |
|--------|------|-------------|
| Fig 1 | `figures/fig1_or_comparison.png` | OR comparison (proposed vs null) with 95% CI |
| Fig 2 | `figures/fig2_forest_plot.png` | β₄ forest plot across 4 model specifications |
| Fig 3 | `figures/fig3_aifs_distribution.png` | Δ AIFS violin plot by annotator condition |
| Fig 4 | `figures/fig4_cluster_histogram.png` | Semantic cluster size distribution |
| Fig 5 | `figures/fig5_or_sensitivity.png` | OR sensitivity across cosine thresholds [0.75–0.90] |

---

## Appendix

### Output Files

| File | Path | Status |
|------|------|--------|
| Metrics JSON | `results/metrics.json` | ✓ Written |
| Model summary | `results/model_summary.txt` | ✓ Written |
| Pairs DataFrame | `results/pairs_df.parquet` | ✓ Written |
| Experiment log | `results/experiment.log` | ✓ Written |
| Figures (5) | `figures/fig*.png` | ✓ Written |
| Validation report | `04_validation.md` | ✓ This file |

### Checkpoint State

```yaml
hypothesis_id: h-e1
current_step: 8
gate_result: FAIL
gate_type: MUST_WORK
experiment_status: completed
tasks_completed: 15/15
coder_validator_cycles: 1
```
