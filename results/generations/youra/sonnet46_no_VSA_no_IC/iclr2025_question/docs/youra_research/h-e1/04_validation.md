# Phase 4 Validation Report: H-E1

**Generated:** 2026-08-21T12:00:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5
**Status:** EXPERIMENT IN PROGRESS — gate verdict pending

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-E1 |
| **Type** | EXISTENCE / LIGHT |
| **Statement** | Token-level log-probability aggregation function choice (min vs. mean vs. raw-sum) produces measurably different AUROC for hallucination detection on factual QA benchmarks |
| **Gate Type** | MUST_WORK |
| **Gate Criterion** | ≥1 pairwise AUROC diff ≥ 0.02 with bootstrap 95% CI lower bound > 0 |
| **Models** | LLaMA-2-7B, Mistral-7B-v0.1 |
| **Datasets** | TriviaQA (2000 samples), NQ (2000 samples), TruthfulQA (817 samples, full) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 (from 03_tasks.yaml) |
| Code Files Generated | 7 |
| Test Files Generated | 3 |
| Unit Tests | 22 passed / 22 total |
| Coder-Validator Cycles | 1 |
| SDD Violations | 0 |

### Generated Files

| File | Lines | Description |
|------|-------|-------------|
| `code/config.py` | 25 | Model IDs, dataset names, seed, paths |
| `code/data_loader.py` | 131 | TriviaQA/NQ/TruthfulQA loaders with label extraction |
| `code/inference.py` | 128 | fp16 model loading, greedy log-prob extraction |
| `code/aggregation.py` | 46 | min/mean/sum aggregation functions |
| `code/evaluation.py` | 162 | AUROC/AUPRC/ECE, bootstrap CI, gate check |
| `code/visualization.py` | 67 | ROC curves and score histograms |
| `code/run_experiment.py` | 215 | Full pipeline orchestration |
| `code/tests/test_aggregation.py` | — | 9 unit tests |
| `code/tests/test_evaluation.py` | — | 8 unit tests |
| `code/tests/test_data_loader.py` | — | 5 unit tests |

### Test Results

```
22 passed in 7.59s
tests/test_aggregation.py::test_aggregate_min PASSED
tests/test_aggregation.py::test_aggregate_mean PASSED
tests/test_aggregation.py::test_aggregate_sum PASSED
tests/test_aggregation.py::test_aggregate_single_token PASSED
tests/test_aggregation.py::test_aggregate_raises_unknown_method PASSED
tests/test_aggregation.py::test_aggregate_raises_empty PASSED
tests/test_aggregation.py::test_compute_all_scores_shape PASSED
tests/test_aggregation.py::test_compute_all_scores_negated PASSED
tests/test_aggregation.py::test_compute_all_scores_order PASSED
tests/test_evaluation.py::test_compute_auroc_perfect PASSED
tests/test_evaluation.py::test_compute_auroc_single_class PASSED
tests/test_evaluation.py::test_compute_auprc_positive PASSED
tests/test_evaluation.py::test_bootstrap_auroc_diff_structure PASSED
tests/test_evaluation.py::test_length_stratified_auroc PASSED
tests/test_evaluation.py::test_check_gate_pass PASSED
tests/test_evaluation.py::test_check_gate_fail PASSED
tests/test_data_loader.py::test_normalize_answer PASSED
tests/test_data_loader.py::test_score_answer_exact_match_correct PASSED
tests/test_data_loader.py::test_score_answer_exact_match_wrong PASSED
tests/test_data_loader.py::test_score_answer_rouge_threshold PASSED
tests/test_data_loader.py::test_get_dataset_raises_unknown PASSED
tests/test_data_loader.py::test_load_truthful_qa_structure PASSED
```

---

## Code Quality Checklist

- [✓] Syntax validation passed (all files import without error)
- [✓] Unit tests pass (22/22)
- [✓] API signatures match 03_logic.md exactly
- [✓] Type hints on all public functions
- [✓] Empty generation guard in inference pipeline
- [✓] Negation applied correctly (higher score = more uncertain = predicted hallucinated)
- [✓] Bootstrap CI uses percentile method with seed=42
- [✓] Gate check implements exact H-E1 criterion (diff ≥ 0.02 AND ci_lower > 0)
- [✓] fp16 model loading with Flash Attention 2 fallback
- [✓] TruthfulQA labels resolved at inference time via ROUGE-L ≥ 0.3

---

## Environment

| Setting | Value |
|---------|-------|
| Conda Env | `youra-h-e1` |
| Python | 3.10 |
| GPU | NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=0) |
| Transformers | 4.53.2 |
| CUDA | Available |
| Batch Size | 1 (required for log-prob correctness) |
| Max New Tokens | 30 |
| Subsample | 2000 TriviaQA, 2000 NQ, 817 TruthfulQA (full) |

---

## Experiment Results

**Status:** RUNNING (PID 3561219, nohup+disown, background)

Current progress at report generation time:
- llama2 / trivia_qa: ~100/2000 samples (~5% complete)
- Estimated completion: ~2 hours from start

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AUROC table (18 cells) | PENDING | All populated | ⏳ |
| Bootstrap CI (9 pairs) | PENDING | CI computed | ⏳ |
| Gate PASS criterion | PENDING | ≥1 diff ≥ 0.02, CI_lower > 0 | ⏳ |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | PENDING (experiment running) |
| **Satisfied** | null |
| **Experiment PID** | 3561219 |
| **Log** | `h-e1/experiment.log` |

Gate verdict will be filled by monitor agent (h-e1-monitor) upon experiment completion.

---

## Implementation: Key Design Decisions

### Aggregation Implementation

```python
# min: most uncertain token (captures worst-case)
def aggregate(logprobs, method="min"):
    lp = np.array(logprobs)
    if method == "min": return float(np.min(lp))
    elif method == "mean": return float(np.mean(lp))
    elif method == "sum": return float(np.sum(lp))

# Negation: higher negated score = more uncertain = predicted hallucinated
scores = -raw  # applied in compute_all_scores()
```

### Log-Prob Extraction (L-2-2)

- `model.generate(do_sample=False, return_dict_in_generate=True, output_scores=True)`
- Per-token: `log_softmax(scores[t], dim=-1)[0, token_ids[t]]`
- Stop at first newline token
- Empty generations (T=0) filtered before aggregation

### TruthfulQA Label Resolution

- Labels resolved at inference time (not load time)
- ROUGE-L ≥ 0.3 vs. `best_answer + correct_answers`
- Max over all reference answers (most generous correct match)

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| Token log-prob extraction | `inference.py:extract_token_logprobs` | ✓ Implemented | Core mechanism; batch=1 required |
| Aggregation functions | `aggregation.py:aggregate` | ✓ Tested | min/mean/sum all correct |
| Bootstrap CI | `evaluation.py:bootstrap_auroc_diff` | ✓ Tested | Percentile, seed=42 |
| Gate check | `evaluation.py:check_gate` | ✓ Tested | Exact H-E1 criterion |

### Optimal Configuration

```yaml
model_loading:
  torch_dtype: float16
  device_map: auto
  attn_implementation: flash_attention_2  # with fallback

inference:
  do_sample: false
  max_new_tokens: 30
  batch_size: 1  # mandatory for log-prob correctness

evaluation:
  bootstrap_n: 1000
  bootstrap_method: percentile
  seed: 42
  gate_diff_threshold: 0.02
  gate_ci_lower_threshold: 0.0

datasets:
  subsample_trivia_qa: 2000
  subsample_nq: 2000
  subsample_truthful_qa: null  # full (817)
  rouge_l_threshold: 0.3  # TruthfulQA correctness
```

### Lessons Learned

**What Worked:**
- Single flat-file architecture (no abstraction layers) — fast to implement and test
- Guard-clause pattern for empty generation filter
- Negation at `compute_all_scores()` rather than per-function — single point of truth

**What to Watch:**
- `sum` aggregation is length-biased; length stratification ablation (T≤5 vs T>5) controls for this
- Flash Attention 2 compilation adds startup overhead; not worth pre-compiling for measurement study
- Batch=1 is slow (0.9s/sample on H100); 2000 samples/dataset is a practical tradeoff

**Key Insight:**
H-E1 tests whether aggregation choice *matters* as a prerequisite for downstream mechanism hypotheses (H-M1–H-M3). Even a null result (no difference) is informative — it means the mechanism signal is independent of aggregation choice.

### Recommendations for Dependents (H-M1, H-M2, H-M3)

- Use `mean` aggregation as default (standard in literature; avoids length bias of `sum`, less noisy than `min`)
- If H-E1 PASS: the winning aggregation function from AUROC table should be used in dependent hypotheses
- Bootstrap CI infrastructure in `evaluation.py` is directly reusable for H-M1–H-M3
- Inference pipeline (`inference.py`) is directly reusable — frozen model + single forward pass

---

## Next Steps

### If Gate PASS:
- Proceed to Phase 5 (Baseline Comparison)
- Use best-performing aggregation function from AUROC table
- All code in `h-e1/code/` ready for Phase 5 reuse

### If Gate FAIL:
- Route to Phase 2A redesign
- Review whether `sum` length bias caused all methods to be equivalent
- Consider normalizing by sequence length before evaluation
- Check TruthfulQA ROUGE-L threshold (may need tuning)

---

## Appendix

### Files Reference

```
h-e1/
├── code/
│   ├── config.py
│   ├── data_loader.py
│   ├── inference.py
│   ├── aggregation.py
│   ├── evaluation.py
│   ├── visualization.py
│   ├── run_experiment.py
│   └── tests/
│       ├── test_aggregation.py
│       ├── test_evaluation.py
│       └── test_data_loader.py
├── results/           (populated by experiment)
│   ├── auroc_table.csv
│   ├── bootstrap_ci_table.csv
│   └── gate_decision_h-e1.md
├── figures/           (populated by experiment)
├── experiment.log
├── experiment.err
└── 04_validation.md   (this file)
```

### Checkpoint State

- `current_step`: 7 (report generation)
- `coder_validator_cycles`: 1
- `tasks.summary.completed`: 15/15
- `conda.env_name`: youra-h-e1
- `gpu.available`: true
- `experiment_status`: running (PID 3561219)

*NOTE: This report will be updated with actual AUROC/gate results upon experiment completion.*
