# Architecture: H-M4 — Step-Matched vs Token-Count-Matched Robustness Check

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 (MECHANISM — robustness check extending H-M3)

Applied: scipy.stats correlation comparison pattern
Applied: checkpoint revision selection pattern (EleutherAI/pythia)
Applied: lm-evaluation-harness programmatic evaluation pattern (inherited H-M3)

---

## Codebase Analysis (Serena)

**Project Type:** incremental extension of H-M3 (no code/ dir exists for H-M3)
**Status:** H-M3 code not yet implemented; H-M3 architecture spec used as reference
**Analyzed Path:** `docs/youra_research/h-m3/` (architecture spec only)
**Findings:** H-M3 defines 6 modules (data_loader, correlation, ablations, visualize, report_generator, analyze). H-M4 reuses the correlation/visualization patterns but introduces new checkpoint evaluation modules. Since no H-M3 code/ exists, H-M4 is effectively green-field but must mirror H-M3's interface conventions for result file compatibility.

---

## File Organization

```
docs/youra_research/h-m4/code/
├── checkpoint_selector.py   # Step-matched + token-count-matched pair construction + verification
├── eval_runner.py           # lm-evaluation-harness runner for step-matched condition
├── results_aggregator.py    # Merge H-M3 token-matched results + H-M4 step-matched results
├── analysis.py              # r_token_matched vs r_step_matched, bias_delta computation
├── visualize.py             # 5 figures
└── run.py                   # Entry point orchestrating full pipeline

docs/youra_research/h-m4/
├── results/
│   ├── step_matched_raw.json          # lm-eval outputs for step-matched condition
│   ├── aggregated_differentials.json  # Both conditions merged
│   ├── correlation_comparison.json    # r_token, r_step, delta_r, bias_delta
│   └── gate_verdict.json
└── figures/
    ├── correlation_comparison_bar.png
    ├── scatter_two_panel.png
    ├── differential_bar_chart.png
    ├── bias_decomposition.png
    └── correlation_summary_table.png
```

---

## Module Structure

### CheckpointSelector (`code/checkpoint_selector.py`)

**Dependencies:** json, numpy

```python
# Constants
PILE_TOTAL_TOKENS = 244e9
DEDUP_TOTAL_TOKENS = 207e9
TOTAL_STEPS = 143000
PILE_TPS = PILE_TOTAL_TOKENS / TOTAL_STEPS        # tokens per step
DEDUP_TPS = DEDUP_TOTAL_TOKENS / TOTAL_STEPS
AVAILABLE_STEPS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000,
                   2000, 4000, 8000, 16000, 32000, 64000, 128000, 143000]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

def get_step_matched_pair(dedup_step: int = 143000) -> tuple[int, int]: ...
    # Returns (pile_step=143000, dedup_step=143000)

def get_token_count_matched_pair(
    dedup_step: int,
    available_pile_steps: list[int] = AVAILABLE_STEPS
) -> tuple[int, int]: ...
    # Returns (pile_step, dedup_step) where pile cumulative tokens ≈ dedup cumulative tokens

def verify_checkpoint_pair(
    pile_step: int,
    dedup_step: int,
    condition: str  # "step_matched" | "token_matched"
) -> bool: ...
    # Asserts token_ratio in [1.10,1.20] for step_matched; ratio ≈ 1.0 ±3% for token_matched
    # Prints verification log; raises AssertionError on failure

def get_all_pairs() -> dict[str, tuple[int, int]]: ...
    # Returns {"step_matched": (143000, 143000), "token_matched": (pile_step, 143000)}
```

---

### EvalRunner (`code/eval_runner.py`)

**Dependencies:** lm_eval, json, pathlib, checkpoint_selector

```python
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
FEW_SHOT = {"mmlu": 5, "hellaswag": 10, "arc_challenge": 25, "winogrande": 5}
ACC_KEYS = {
    "mmlu": "acc,none",
    "hellaswag": "acc_norm,none",
    "arc_challenge": "acc_norm,none",
    "winogrande": "acc,none"
}

def run_model(
    model_id: str,
    revision: str,
    out_path: str,
    device: str = "cuda",
    dtype: str = "float16"
) -> dict: ...
    # Calls lm_eval.simple_evaluate; returns raw results dict; saves JSON

def run_step_matched_condition(
    model_sizes: list[str],
    cache_dir: str,
    out_dir: str
) -> dict[str, dict]: ...
    # For each size: run Pile step143000 + dedup step143000
    # Returns {size: {pile: results, dedup: results}}

def extract_accuracy(results: dict, benchmark: str) -> float: ...
    # Returns results["results"][benchmark][ACC_KEYS[benchmark]]

def compute_differentials(
    pile_results: dict,
    dedup_results: dict
) -> dict[str, float]: ...
    # Returns {benchmark: dedup_acc - pile_acc}
```

---

### ResultsAggregator (`code/results_aggregator.py`)

**Dependencies:** json, pathlib

```python
def load_hm3_differentials(hm3_results_dir: str) -> dict[str, dict[str, float]]: ...
    # Loads h-m3/results/accuracy_differentials.json
    # Returns {model_size: {benchmark: float}} — token-count-matched condition

def load_hm4_step_matched(hm4_results_dir: str) -> dict[str, dict[str, float]]: ...
    # Loads step_matched_raw.json, computes differentials per size
    # Returns {model_size: {benchmark: float}}

def aggregate(
    token_matched: dict,
    step_matched: dict
) -> dict: ...
    # Returns {"token_matched": {size: {bench: diff}}, "step_matched": {size: {bench: diff}}}

def save_aggregated(aggregated: dict, out_path: str) -> None: ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** numpy, scipy.stats, json

```python
def load_contamination_estimates(hm1_path: str) -> dict[str, float]: ...
    # Returns {benchmark: contamination_score}

def build_vectors(
    differentials: dict[str, dict[str, float]],
    cont_est: dict[str, float]
) -> tuple[np.ndarray, np.ndarray]: ...
    # Returns (cont_vec (16,), diff_vec (16,)) — 4 benchmarks × 4 model sizes flattened

def compute_pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float]: ...
    # Returns (r, p)

def compute_uniform_bias(differentials: dict[str, dict[str, float]]) -> float: ...
    # Mean of all differentials across benchmarks and model sizes

def run_comparison(
    aggregated: dict,
    cont_est: dict
) -> dict: ...
    # Returns {
    #   r_token_matched, p_token_matched,
    #   r_step_matched, p_step_matched,
    #   delta_r,        # r_token - r_step (expected > 0)
    #   uniform_bias_token, uniform_bias_step,
    #   bias_delta,     # bias_step - bias_token (expected < 0)
    #   gate_verdict    # "PASS" | "FAIL_AS_ROBUSTNESS_CONFIRMATION"
    # }

def determine_gate(delta_r: float, bias_delta: float) -> str: ...
    # "PASS" if delta_r > 0 AND bias_delta < 0
    # "ROBUSTNESS_CONFIRMATION" if |delta_r| < 0.05 AND |bias_delta| < 0.01
    # else "PARTIAL"
```

---

### Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_correlation_comparison_bar(
    r_token: float, r_step: float,
    ci_token: tuple, ci_step: tuple,
    out_path: str
) -> None: ...

def plot_scatter_two_panel(
    cont_est: dict,
    token_differentials: dict,
    step_differentials: dict,
    r_token: float, r_step: float,
    out_path: str
) -> None: ...

def plot_differential_bar_chart(
    aggregated: dict,
    out_path: str
) -> None: ...
    # Per-benchmark, side-by-side token vs step conditions, 4 model sizes

def plot_bias_decomposition(
    aggregated: dict,
    out_path: str
) -> None: ...
    # Per model size: volume bias vs contamination component

def plot_correlation_summary_table(
    comparison_results: dict,
    out_path: str
) -> None: ...
    # Table figure: r, p, CI for both conditions + delta_r
```

---

### Main Pipeline (`code/run.py`)

**Dependencies:** all modules above, pathlib, argparse

```python
BASE_DIR = Path("docs/youra_research")
HM3_RESULTS = BASE_DIR / "h-m3/results"
HM4_DIR     = BASE_DIR / "h-m4"
HM1_CONT    = BASE_DIR / "h-m1/results/contamination_estimates.json"

def run_pipeline(
    cache_dir: str = "./pythia_cache",
    skip_eval: bool = False  # skip if step_matched_raw.json already exists
) -> None: ...
    # 1. CheckpointSelector: verify pairs
    # 2. EvalRunner: run step-matched condition (4 sizes × 2 variants)
    # 3. ResultsAggregator: merge H-M3 + H-M4 step-matched
    # 4. Analysis: compute r_token, r_step, delta_r, bias_delta, gate
    # 5. Visualizer: 5 figures
    # 6. Save gate_verdict.json

if __name__ == "__main__":
    run_pipeline()
```

---

## External Dependencies

| File | Path | Required |
|------|------|----------|
| H-M3 token-matched differentials | `docs/youra_research/h-m3/results/accuracy_differentials.json` | MUST EXIST |
| H-M1 contamination estimates | `docs/youra_research/h-m1/results/contamination_estimates.json` | MUST EXIST |
| Pythia checkpoints (HuggingFace) | `EleutherAI/pythia-{size}` + `EleutherAI/pythia-{size}-deduped` at step143000 | Downloaded at runtime |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Checkpoint Selector | Implement checkpoint_selector.py: step/token pair logic, token ratio verification, AVAILABLE_STEPS mapping | 8 | 2+1+3+2 |
| B-2 | Eval Runner — Step-Matched | Implement eval_runner.py: lm_eval.simple_evaluate for 4 sizes × 2 variants at step143000, extract differentials | 12 | 3+3+3+3 |
| B-3 | Results Aggregator | Implement results_aggregator.py: load H-M3 JSONs + H-M4 step-matched, merge into unified structure | 7 | 2+2+1+2 |
| B-4 | Comparative Analysis | Implement analysis.py: Pearson for both conditions, delta_r, uniform_bias, bias_delta, gate verdict logic | 11 | 2+2+4+3 |
| B-5 | Visualization | Implement visualize.py: 5 figures (bar, 2-panel scatter, differential bar, bias decomposition, summary table) | 12 | 3+2+4+3 |
| B-6 | Pipeline Orchestration | Implement run.py: wire all modules, --skip_eval flag, error handling for missing H-M3 results | 8 | 2+3+1+2 |
| B-7 | Verification & Gate Report | gate_verdict.json with all metrics, gate pass/fail/robustness-confirmation verdict, assertion logging | 7 | 1+2+2+2 |

**Distribution**: High(10-13): [B-2, B-4, B-5], Medium(7-9): [B-1, B-3, B-6, B-7], Low(4-6): []

**Total budget allocation:** 7 epics. Dominant cost = B-2 (GPU inference for 8 checkpoints × 4 benchmarks) and B-5 (5 figures). Analysis runtime <10s post-eval.
