# Configuration: H-E2 — SFT Training Source Ablation

**Applied: minimal hardcoded-dict pattern (LIGHT tier)**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing code to analyze
**Config Files Found**: None — new config
**Pattern Used**: hardcoded dict (LIGHT tier: argparse + print+CSV, no YAML/dataclass)

---

## Experiment Constants

```python
# prepare_data.py
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
DEDUP_THRESHOLD = 0.95
TARGET_PROBLEMS = 164  # limited by HumanEval-only post-dedup
EMBED_MODEL = "all-MiniLM-L6-v2"
UNIFORM_TEMPLATE = "# Complete the following Python function:\n{docstring}\n{function_signature}"
HF_DATASET_IDS = {
    "humaneval_only": ("openai/openai_humaneval", "train"),
    "mbpp_only":      ("google-research-datasets/mbpp", "train"),  # sanitized config
    "leetcode_only":  ("newfacade/LeetCodeDataset", "train"),
}

# train.py
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"
SEEDS = [42, 123, 777]

FIXED_HPARAMS = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "completion_only_loss": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,  # non-standard: DeepSeek-Coder official recommendation
}

EPOCHS_PER_CONDITION = {
    "humaneval_only": 6,
    "mbpp_only":      3,
    "leetcode_only":  1,
    "equal_mix":      2,
}

BASE_HUMANEVAL = 0.15
BASE_MBPP = 0.45
ACTIVATION_MARGIN = 0.03  # require pass@1 > base + margin on >=1 benchmark before proceeding

ALL_RUNS = [
    {"condition": c, "seed": s}
    for c in CONDITIONS
    for s in SEEDS
]  # 12 total

# evaluate.py
BENCHMARKS = ["humaneval", "mbpp"]
BENCHMARK_N_PROBLEMS = {"humaneval": 164, "mbpp": 378}
EVALPLUS_BACKEND = "hf"
EVALPLUS_GREEDY = True

# analyze.py
N_COMPARISONS = 12          # C(4,2)=6 per benchmark x 2 benchmarks
ALPHA = 0.05                # after Holm-Bonferroni correction
MIN_CONTRAST_PP = 2.0       # minimum meaningful absolute contrast
FAIL_THRESHOLD_PP = 1.5     # all contrasts within ±1.5 pp on both benchmarks = FAIL
FIGURES_DIR = "docs/youra_research/h-e2/figures"
REPORT_PATH = "docs/youra_research/h-e2/results/statistical_report.txt"
```

---

## DeepSpeed ZeRO-3 Config (`ds_zero3_config.json`)

```json
{
  "zero_optimization": {
    "stage": 3,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "reduce_bucket_size": 5e8,
    "stage3_prefetch_bucket_size": 5e8,
    "stage3_param_persistence_threshold": 1e6,
    "stage3_gather_16bit_weights_on_model_save": true
  },
  "bf16": {"enabled": true},
  "gradient_clipping": 1.0,
  "train_micro_batch_size_per_gpu": 4,
  "gradient_accumulation_steps": 4
}
```

---

## A-4: Statistical Analysis [Complexity: 13, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A4-1 | MixedLM Configuration | Formula, DataFrame schema, aggregation from 12 checkpoints, gate thresholds |
| C-A4-2 | Holm-Bonferroni Configuration | 12-comparison correction, contrast extraction, report format |

---

## C-A4-1: MixedLM Configuration

### Results DataFrame Schema

```python
# Shape per benchmark:
#   humaneval: 12 checkpoints x 164 problems = 1,968 rows
#   mbpp:      12 checkpoints x 378 problems = 4,536 rows
RESULTS_COLUMNS = ["pass1", "source_condition", "solution_length", "problem_id", "seed", "benchmark"]
# pass1: float 0.0 or 1.0 (per-problem binary)
# solution_length: int, token count of ground-truth solution from EvalPlus data
# problem_id: str, e.g. "HumanEval/0" or "Mbpp/1"
```

### Aggregation

```python
# evaluate.py writes one row per (condition, seed, benchmark, problem_id) to results CSV.
# analyze.py::load_results() reads CSV → DataFrame; adds solution_length from EvalPlus data.
# solution_length fallback if EvalPlus tokens unavailable: len(solution.split())
```

### MixedLM Fit

```python
import statsmodels.formula.api as smf

MIXEDLM_FORMULA = "pass1 ~ C(source_condition) + solution_length"
MIXEDLM_GROUPS_COL = "problem_id"

def fit_mixedlm(df: pd.DataFrame, benchmark: str):
    sub = df[df["benchmark"] == benchmark].copy()
    # Force humaneval_only as reference level
    sub["source_condition"] = pd.Categorical(
        sub["source_condition"], categories=CONDITIONS, ordered=False
    )
    model = smf.mixedlm(MIXEDLM_FORMULA, data=sub, groups=sub[MIXEDLM_GROUPS_COL])
    return model.fit(reml=True)
```

### Gate Logic

```python
# PASS requires ALL:
#   1. source_condition main-effect p < ALPHA (Holm-corrected) on >=1 benchmark
#   2. >=1 pairwise |contrast_pp| >= MIN_CONTRAST_PP (2.0 pp)
#   3. Direction of top contrast consistent across >=2/3 seeds
# FAIL if all contrasts within ±FAIL_THRESHOLD_PP (1.5 pp) on both benchmarks
```

---

## C-A4-2: Holm-Bonferroni Multiple Comparison Configuration

### Condition Pairs

```python
from itertools import combinations

CONDITION_PAIRS = list(combinations(CONDITIONS, 2))
# [("humaneval_only","mbpp_only"), ("humaneval_only","leetcode_only"),
#  ("humaneval_only","equal_mix"), ("mbpp_only","leetcode_only"),
#  ("mbpp_only","equal_mix"), ("leetcode_only","equal_mix")]
# 6 pairs x 2 benchmarks = 12 p-values submitted jointly
```

### Correction Procedure

```python
from statsmodels.stats.multitest import multipletests

# p_values: flat list of 12 raw p-values (humaneval pairs first, then mbpp)
reject, p_adjusted, _, _ = multipletests(p_values, alpha=ALPHA, method="holm")
```

### Extracting Pairwise Contrasts from MixedLM

```python
import numpy as np

def get_contrast_pvalue(result, cond_a: str, cond_b: str) -> tuple[float, float]:
    """Returns (contrast_pp, p_raw) for cond_a vs cond_b."""
    params = result.params
    ref = CONDITIONS[0]  # "humaneval_only"

    def coef(c):
        if c == ref:
            return 0.0
        return params[f"C(source_condition)[T.{c}]"]

    # Build contrast vector for t_test
    param_names = list(result.params.index)
    vec = np.zeros(len(param_names))
    for i, name in enumerate(param_names):
        if f"[T.{cond_a}]" in name:
            vec[i] = 1.0
        elif f"[T.{cond_b}]" in name:
            vec[i] = -1.0
    t_res = result.t_test(vec)
    contrast_pp = float(t_res.effect) * 100
    p_raw = float(t_res.pvalue)
    return contrast_pp, p_raw
```

### Output: `statistical_report.txt` Format

```
H-E2 Statistical Analysis Report
==================================
Date: {datetime}
Model: deepseek-ai/deepseek-coder-1.3b-base

=== MixedLM Results ===
Benchmark: humaneval
  Formula: pass1 ~ C(source_condition) + solution_length | problem_id
  source_condition main effect p = {p_raw:.4f} (raw), {p_adj:.4f} (Holm-corrected)
  solution_length coef = {coef:.4f} (p={p:.4f})

Benchmark: mbpp
  [same structure]

=== Pairwise Contrasts (Holm-Bonferroni, 12 total comparisons) ===
Pair                              | Benchmark | Contrast (pp) | p_raw  | p_adj  | Reject
humaneval_only vs mbpp_only       | humaneval |  +X.X         | X.XXXX | X.XXXX | True/False
...

=== Gate Evaluation ===
Result: PASS / FAIL / AMBIGUOUS

  [x/] Criterion 1: main effect p < 0.05 corrected on >=1 benchmark
  [x/] Criterion 2: >=1 contrast >= 2.0 pp absolute
  [x/] Criterion 3: direction consistent >=2/3 seeds
  [ /x] FAIL condition: all contrasts within ±1.5 pp on both benchmarks
```
