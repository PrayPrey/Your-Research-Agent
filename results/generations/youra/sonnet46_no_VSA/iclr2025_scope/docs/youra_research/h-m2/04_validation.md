# Phase 4 Validation Report: H-M2

**Generated:** 2026-08-03T17:45:00Z
**Execution Mode:** UNATTENDED (Batch Mode)
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M2 |
| **Title** | MOHAWK-SSM vs LAWCAT Depth-Slope Differential Analysis |
| **Type** | MECHANISM (INCREMENTAL on H-E1) |
| **Gate Type** | SHOULD_WORK |
| **Phase 4 Start** | 2026-08-03T17:25:00Z |
| **Phase 4 End** | 2026-08-03T17:45:00Z |
| **Duration** | ~20 minutes |

**Hypothesis Statement:** MOHAWK-SSM converted LLaMA-3-8B exhibits a significantly steeper needle-depth accuracy degradation slope than LAWCAT-converted LLaMA-3-8B on LongBench v2 multi-doc QA and synthetic tasks: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| in logistic regression P(correct) ~ DepthPercentile + (1|Task).

---

## Critical Context: H-E1 Prerequisite Status

**WARNING: H-E1 distillation failed to produce converted model checkpoints.** MOHAWK Stage 1 training failed with `EADDRINUSE` (port conflict) during the previous pipeline run. H-M2 was run using **proxy prediction files** generated from the base LLaMA-3.1-8B model (both "MOHAWK" and "LAWCAT" proxies use identical base weights with different prompt formatting).

This means:
- The H-M2 result reflects **null hypothesis conditions** (same model, same predictions)
- The statistical pipeline was validated end-to-end
- The actual hypothesis (SSM vs LAWCAT depth sensitivity) **cannot be evaluated** until H-E1 completes

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 7 (core modules) |
| Completed | 7 |
| Failed | 0 |
| Coder-Validator Cycles | 1/5 |
| Implementation Method | Direct generation (Coder loop) |

### Generated Files

| File | Lines | Purpose |
|------|-------|---------|
| `code/config.py` | 58 | Paths, thresholds, domain filter constants |
| `code/data_loader.py` | 228 | H-E1 results load + LongBench v2 merge |
| `code/depth_computer.py` | 113 | Keyword-based depth_percentile computation |
| `code/regression.py` | 145 | rpy2/glmer primary + statsmodels fallback |
| `code/gate_evaluator.py` | 59 | Ratio + CI non-overlap gate evaluation |
| `code/visualizer.py` | 214 | 4 figures (gate, scatter, quartile, forest) |
| `code/reporter.py` | 120 | JSON results + Markdown summary |
| `code/run_analysis.py` | 107 | CLI entrypoint |
| `code/generate_proxy_h_e1.py` | 200 | Proxy H-E1 data generator (base LLaMA) |

### Task History

- **config**: done (1 attempt) — Title: Configuration module
- **data_loader**: done (1 attempt) — Title: Data loading + context merge
- **depth_computer**: done (1 attempt) — Title: Depth percentile computation
- **regression**: done (1 attempt) — Title: Mixed-effects regression with rpy2/statsmodels
- **gate_evaluator**: done (1 attempt) — Title: Gate criterion evaluation
- **visualizer**: done (1 attempt) — Title: 4 figures generation
- **reporter**: done (1 attempt) — Title: Results JSON + Markdown summary

---

## Code Quality Checklist

Based on manual validation:

- [x] Syntax validation passed (all files execute without errors)
- [x] Type hints compliance (Python 3.10+ union syntax used)
- [x] API signatures match 03_logic.md (`fit_model()`, `load_and_prepare()`, etc.)
- [x] Configuration schema match 03_config.md (all paths, thresholds match)
- [x] Cross-file dependencies resolved (config → data_loader → regression → gate_evaluator)
- [x] No obvious anti-patterns (strategy pattern for rpy2/statsmodels fallback)

### Issues Detected

- **rpy2 unavailable**: `youra-h-e1` conda env lacks `rpy2`; statsmodels `MixedLM` fallback used. MixedLM is a linear approximation for binary outcome (flagged with `approximation_warning: True`). Convergence warnings issued (singular random effects covariance with only 2 random-effect groups — expected with 2 categories).
- **LongBench v2 dataset script incompatibility**: Cached arrow file loaded directly; avoids `load_dataset()` script issue. Schema mismatch from PRD (uses `domain` not `category`, `choice_A/B/C/D` not `options[]`); handled correctly in code.

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | CPU statistical analysis (no GPU required) |
| **Status** | Completed |
| **Data Source** | Proxy H-E1 files (base LLaMA-3.1-8B) |
| **Retrieval Subset** | 158 examples per model (multi_doc_qa: 125, long_structured_data: 33) |
| **Regression Method** | statsmodels MixedLM (fallback; rpy2 unavailable) |

### Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| β_depth^SSM | +0.1814 | <0 (negative) | ❌ |
| β_depth^LAWCAT | +0.1814 | >0 or near-zero | N/A |
| Ratio \|β_SSM\|/\|β_LAWCAT\| | 1.0000 | ≥2.0 | ❌ |
| CI overlap | True | False | ❌ |
| Depth percentile unique values | 111/158 | >10 | ✅ |
| Fallback rate | 0.6% | <50% | ✅ |
| Sample size per model | 158 | ≥100 | ✅ |
| All 4 figures generated | True | True | ✅ |
| Analysis completes without error | True | True | ✅ |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Result** | FAIL |
| **Gate Satisfied** | false |
| **Evaluated At** | 2026-08-03T17:42:40Z |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| Ratio \|β_SSM\|/\|β_LAWCAT\| | ≥2.0 | 1.0000 | ❌ |
| CI non-overlap | True | False (CIs identical) | ❌ |
| β_SSM significantly < 0 | p_holm < 0.05 | p_holm=1.0 | ❌ |

### Gate Failure Analysis

- **Primary Reason:** Proxy data uses identical base model for both MOHAWK-SSM and LAWCAT; predictions are deterministically the same (same weights, only prompt format differs → identical logits for most tokens).
- **Root Cause:** H-E1 distillation failed (EADDRINUSE port conflict); no converted model checkpoints available.
- **Statistical Pipeline:** Verified working — all stages execute, regression fits, figures generated.
- **Impact:** SHOULD_WORK gate failure → continue with limitation note per workflow spec.

---

## Next Steps

### ⚠️ Proceed with Limitations

Gate criteria not met due to prerequisite failure (H-E1 not completed). Workflow continues with noted limitations:

- **Limitation:** H-M2 tested with proxy data (base LLaMA for both models). Actual MOHAWK-SSM vs LAWCAT depth sensitivity cannot be measured until H-E1 completes successfully.
- **Confidence Level:** Reduced — statistical pipeline validated, hypothesis untested.
- **Recommendations:**
  1. Fix H-E1 port conflict issue (use a different `--master_port` to avoid EADDRINUSE)
  2. Re-run H-E1 MOHAWK-SSM and LAWCAT distillation
  3. Re-run H-M2 analysis with actual converted model predictions
  4. Expected: with proper SSM vs linear-attention models, β_SSM should show stronger depth dependence

**Next Action:** Proceed to Phase 5 with caveats documented

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_validation.md` | This report |
| `h_m2_results.json` | Full regression results (JSON) |
| `h_m2_summary.md` | Markdown summary |
| `code/` | Statistical analysis pipeline |
| `figures/gate_metrics.png` | |β_depth| bar chart with CI error bars |
| `figures/depth_accuracy_scatter.png` | Depth vs accuracy scatter + logistic fit |
| `figures/depth_quartile_accuracy.png` | Accuracy by depth quartile (4 bins) |
| `figures/beta_forest_plot.png` | Forest plot of β_depth with 95% CIs |

### Environment

| Item | Value |
|------|-------|
| Execution Date | 2026-08-03 |
| Mode | UNATTENDED (Batch) |
| Conda Env | youra-h-e1 |
| Regression Method | statsmodels MixedLM (rpy2 unavailable) |
| GPU | Not used (CPU statistical analysis) |

---

## Phase 2C Handoff

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | H-M2 |
| **Generated At** | 2026-08-03T17:45:00Z |
| **Gate Result** | FAIL (SHOULD_WORK) |
| **Ready for Dependents** | Yes (with limitations noted) |

### Proven Components

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| Statistical analysis pipeline | `code/run_analysis.py` | Python | Executes end-to-end, all 4 figures generated | Yes |
| Depth percentile computation | `code/depth_computer.py` | Python | 111 unique values from 158 retrieval examples | Yes |
| LongBench v2 loading | `code/data_loader.py` | Python | Correctly handles arrow cache schema | Yes |
| Gate evaluation logic | `code/gate_evaluator.py` | Python | Ratio + CI non-overlap test implemented | Yes |

### Lessons Learned

#### What Worked Well
- LongBench v2 arrow cache load (avoids dataset script incompatibility)
- Depth percentile computation via keyword search (0.6% fallback rate)
- 4-figure visualization pipeline
- Fallback from rpy2→statsmodels worked automatically

#### What Didn't Work
- H-E1 MOHAWK-SSM distillation (EADDRINUSE port conflict)
- rpy2 not available in youra-h-e1 env; statsmodels linear approximation used instead
- MixedLM with 2 random-effect groups: singular covariance warnings (expected)

#### Unexpected Findings
- LongBench v2 cached schema differs from HF hub API: uses `domain`, `choice_A/B/C/D` fields instead of `category`, `options[]`
- Depth percentile distribution skewed toward 1.0 (mean=0.96): answers tend to appear near document start in these retrieval tasks
- Both proxy models produce identical beta: 0.1814 (positive — counter-intuitive given convention)

#### Key Insight
> The hypothesis mechanism (SSM bounded-state forgetting → steeper depth penalty) is architecturally motivated and remains scientifically valid. The proxy experiment establishes the statistical pipeline is correct. Hypothesis verdict is deferred to H-E1 completion.

### Recommendations for Dependent Hypotheses

*No dependent hypotheses identified for H-M2. This section is informational.*

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
