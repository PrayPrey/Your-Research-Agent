# Architecture: h-e1 Prescreening Validation

**Hypothesis:** h-e1 (EXISTENCE)
**Type:** Prescreening inference pipeline — NO training
**Gate:** fraction_k_pass_ge1 ≥ 0.10 AND pct_groups_above_1.5x ≥ 0.80
**Generated:** 2026-03-15

Applied: subprocess-sandbox-with-timeout, batched-inference-pipeline, fail-early-validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4/TEST_dl4c/docs/youra_research/20260315_dl4c/h-e1/code/` — directory does not exist
**Findings:** New implementation from scratch. No base hypothesis. Archon KB contains only image generation content (similarity 0.35–0.48, no semantic match for GRPO/APPS domain).

---

## File Organization

```
h-e1/code/
├── prescreening.py        # Entry point — main orchestration
├── data_loader.py         # APPS loading, filtering, test case parsing
├── execution_sandbox.py   # Subprocess code execution with timeout
├── reward_fn.py           # R_ratio and R_binary computation
├── evaluate.py            # Gate metric computation
├── visualization.py       # Figure generation
└── sft_checkpoint/        # SFT checkpoint (optional, fallback to base)

h-e1/results/
├── gate_metrics.json
├── per_problem_results.csv
└── rollouts.json          # Optional

h-e1/figures/
├── gate_metrics.png
├── s_term_distribution.png
├── variance_ratio_scatter.png
├── t_distribution.png
└── empirical_vs_theoretical.png
```

---

## Module Structure

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies:** datasets, json

```python
class APPSDataLoader:
    def __init__(self, dataset_id: str = "codeparrot/apps", split: str = "train"): ...
    def load_and_filter(self, min_test_cases: int = 3) -> list[dict]: ...
    def parse_test_cases(self, raw_tests: str) -> list[dict]: ...
    # Returns list of {problem_id, prompt, test_cases: [{input, output}], T}

def load_apps_introductory(min_test_cases: int = 3) -> list[dict]: ...
```

### ExecutionSandbox (`h-e1/code/execution_sandbox.py`)

**Dependencies:** subprocess, tempfile

```python
def execute_code(
    code: str,
    stdin: str,
    timeout: float = 5.0
) -> tuple[str, bool]: ...
# Returns (stdout, success)

def run_against_test_cases(
    code: str,
    test_cases: list[dict],
    timeout: float = 5.0
) -> int: ...
# Returns tests_passed count (0..T)
```

### RewardFn (`h-e1/code/reward_fn.py`)

**Dependencies:** execution_sandbox

```python
def compute_r_ratio(tests_passed: int, T: int) -> float: ...
# tests_passed / T

def compute_r_binary(tests_passed: int, T: int) -> float: ...
# float(tests_passed == T)

def compute_group_rewards(
    rollouts: list[str],
    test_cases: list[dict],
    reward_type: str = "ratio"
) -> list[float]: ...
# Returns k=8 reward scalars for one problem group

def compute_s_term(rollouts: list[str], test_cases: list[dict]) -> float: ...
# fraction of rollouts where tests_passed >= 1
```

### Evaluate (`h-e1/code/evaluate.py`)

**Dependencies:** reward_fn, numpy

```python
def compute_gate_metrics(
    per_problem_results: list[dict]
) -> dict: ...
# Returns {fraction_k_pass_ge1, mean_var_ratio, pct_groups_above_1_5x, gate_pass}

def compute_variance_ratio_per_group(
    r_ratio_vec: list[float],
    r_binary_vec: list[float]
) -> float | None: ...
# Returns var_ratio/var_binary or None if var_binary <= 1e-8

def check_gate(metrics: dict) -> tuple[bool, str]: ...
# Returns (pass, message)
```

### Prescreening (`h-e1/code/prescreening.py`)

**Dependencies:** data_loader, execution_sandbox, reward_fn, evaluate, visualization, torch, transformers

```python
def load_model(
    sft_checkpoint_path: str,
    base_model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    dtype: torch.dtype = torch.bfloat16
) -> tuple[Any, Any]: ...
# Returns (model, tokenizer); auto-fallback to base if sft_checkpoint missing

def generate_rollouts(
    model: Any,
    tokenizer: Any,
    problems: list[dict],
    k: int = 8,
    temperature: float = 0.8,
    max_new_tokens: int = 1024,
    batch_size: int = 4,
    seed: int = 42
) -> dict[int, list[str]]: ...
# Returns {problem_id: [rollout_0, ..., rollout_k-1]}

def run_prescreening(
    problems: list[dict],
    rollouts: dict,
    s_term_range: tuple[float, float] = (0.3, 0.55)
) -> tuple[list[dict], list[dict]]: ...
# Returns (prescreened_problems, per_problem_results)

def main(seed: int = 42, batch_size: int = 4) -> None: ...
```

### Visualization (`h-e1/code/visualization.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_gate_metrics(
    metrics: dict,
    thresholds: dict,
    output_path: str
) -> None: ...

def plot_s_term_distribution(
    s_terms_all: list[float],
    s_terms_filtered: list[float],
    output_path: str
) -> None: ...

def plot_variance_ratio_scatter(
    per_problem_results: list[dict],
    output_path: str
) -> None: ...

def plot_t_distribution(
    t_counts: list[int],
    output_path: str
) -> None: ...

def plot_empirical_vs_theoretical(
    per_problem_results: list[dict],
    output_path: str
) -> None: ...

def generate_all_figures(
    metrics: dict,
    per_problem_results: list[dict],
    figures_dir: str
) -> None: ...
```

---

## Data Flow

- `data_loader` loads APPS, filters difficulty=0 and T≥3, returns problem dicts
- `prescreening.main` loads model with SFT fallback, calls `generate_rollouts` in batches
- For each problem: `execution_sandbox.run_against_test_cases` → `reward_fn.compute_group_rewards` (both ratio and binary)
- `reward_fn.compute_s_term` → S_term filter [0.3, 0.55] → prescreened subset
- `evaluate.compute_gate_metrics` → gate check
- `visualization.generate_all_figures` → saves to `h-e1/figures/`
- Results serialized to `h-e1/results/`

---

## Critical Constraints

- Single GPU; set `CUDA_VISIBLE_DEVICES` before launch
- dtype=bfloat16, batch_size=4-8 (H100 NVL ~40GB VRAM, ~15GB for 7B model)
- Subprocess sandbox: 5-second timeout per test case
- Fail early if T≥3 filter yields <50 problems
- Resume: skip already-processed problem_ids if partial results exist

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Loading | Implement APPSDataLoader: HuggingFace load, difficulty=0 filter, T≥3 filter, test case JSON parsing | 8 | 2+1+2+3 |
| E-2 | Execution Sandbox | Implement subprocess harness: tempfile code execution, stdin injection, stdout capture, timeout, error handling | 11 | 3+1+4+3 |
| E-3 | Reward Functions | Implement R_ratio, R_binary, S_term computation; group reward vectors | 7 | 2+2+2+1 |
| E-4 | Inference Pipeline | Model load with SFT fallback, batched k=8 rollout generation, seed, tqdm progress | 13 | 3+3+4+3 |
| E-5 | Gate Metric Evaluation | Variance ratio per group, fraction_k_pass_ge1, pct_groups_above_1.5x, gate check, fail-early logic | 10 | 2+2+3+3 |
| E-6 | Main Orchestration | prescreening.py: wire all modules, S_term filtering, resume logic, results persistence (JSON/CSV) | 12 | 3+3+3+3 |
| E-7 | Visualization | 5 mandatory figures: gate metrics bar, S_term histogram, variance scatter, T histogram, empirical vs theoretical | 8 | 2+1+3+2 |

**Distribution**: VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [E-2, E-4, E-5, E-6] | Low(4-8): [E-1, E-3, E-7]

**Run command:** `python h-e1/code/prescreening.py --seed 42 --batch_size 4`
