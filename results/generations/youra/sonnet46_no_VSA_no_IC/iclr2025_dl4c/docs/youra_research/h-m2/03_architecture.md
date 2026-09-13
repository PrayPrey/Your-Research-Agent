---
hypothesis_id: h-m2
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# Architecture: H-M2 — Variance Selection Reduces Zero-Gradient Groups in GRPO

Applied: TRL GRPOTrainer direct usage pattern (minimal wrapper)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/compare_variance_selection.py`
**Findings**: H-M1 is a single-file script using `@dataclass` config, standalone functions (no classes), matplotlib Agg backend, direct JSON loading from `docs/youra_research/h-e1/results/mbpp_variance_profile.json`. H-M2 follows the same single-file pattern with added TRL training loop.

---

## File Structure

- `docs/youra_research/h-m2/code/`
  - `config.py` — experiment config dataclass
  - `dataset.py` — MBPP subset construction (variance-50 and random-50)
  - `reward.py` — binary execution reward function
  - `train.py` — GRPO training runner for one condition
  - `analyze.py` — log extraction, gate metrics, JSON output
  - `visualize.py` — 4 figures
  - `run_experiment.py` — orchestrates both training runs + analysis
- `docs/youra_research/h-m2/results/` — outputs (variance50/, random50/, gate_results.json)
- `docs/youra_research/h-m2/figures/` — 4 PNG files

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class H_M2Config:
    # paths
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    # model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    # grpo
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50
    learning_rate: float = 5e-7
    beta: float = 0.0
    logging_steps: int = 1
    save_steps: list = None  # default: [10, 20, 50]
    use_vllm: bool = False
    seed: int = 42
    max_new_tokens: int = 512
    # experiment
    k: int = 50
    checkpoint_steps: list = None  # default: [10, 20, 50]
    exec_timeout: float = 5.0
```

---

### Dataset (`code/dataset.py`)

**Dependencies**: Config

```python
def load_variance_50_ids(profiling_json: str, k: int = 50) -> list[int]: ...
    # loads h-e1 JSON, sorts by variance_i desc, returns top-k task_ids

def load_random_50_ids(mbpp_train, k: int = 50, seed: int = 42) -> list[int]: ...
    # numpy.random.default_rng(seed).choice over all task_ids

def build_subset(mbpp_train, task_ids: list[int]) -> Dataset: ...
    # mbpp_train.filter(lambda x: x["task_id"] in set(task_ids))
    # validates len == k

def load_mbpp_subsets(cfg: H_M2Config) -> tuple[Dataset, Dataset, list[int], list[int]]: ...
    # returns (variance_50_ds, random_50_ds, variance_50_ids, random_50_ids)
```

---

### Reward (`code/reward.py`)

**Dependencies**: none

```python
def _execute_code(code: str, test_list: list[str], timeout: float) -> bool: ...
    # runs subprocess; returns True iff all tests pass; catches timeout/error

def make_execution_reward(timeout: float = 5.0):
    # returns reward_fn(completions, prompts, **kwargs) -> list[float]
    # compatible with TRL GRPOTrainer reward_funcs interface
    # reward: 1.0 all pass, 0.0 otherwise
    def reward_fn(completions: list[str], prompts: list[str], **kwargs) -> list[float]: ...
    return reward_fn
```

---

### Train (`code/train.py`)

**Dependencies**: Config, Dataset (ds passed in), Reward

```python
def format_prompt(example: dict) -> dict: ...
    # adds "prompt" field from example["text"] for GRPOTrainer

def run_grpo(
    cfg: H_M2Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,          # "variance50" | "random50"
) -> list[dict]: ...
    # loads model + tokenizer
    # builds GRPOConfig from cfg
    # calls GRPOTrainer(model, config, dataset, reward_funcs=[reward_fn]).train()
    # returns trainer.state.log_history
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: Config

```python
def extract_frac_zero_std(log_history: list[dict]) -> list[float]: ...
    # filters log entries with "frac_reward_zero_std" key, returns values 1-50

def compute_gate_metrics(
    frac_var: list[float],
    frac_rnd: list[float],
    checkpoints: list[int],
) -> dict: ...
    # returns mean_frac by condition/checkpoint, gate booleans, gap_at_10

def save_results(
    cfg: H_M2Config,
    gate_metrics: dict,
    frac_var: list[float],
    frac_rnd: list[float],
    variance_50_ids: list[int],
    random_50_ids: list[int],
) -> None: ...
    # writes gate_results.json per FR-11 schema
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: Config

```python
def plot_gate_bar_chart(gate_metrics: dict, figures_dir: str) -> None: ...
    # Fig 1: grouped bar at checkpoints 10, 20, 50

def plot_learning_curves(frac_var: list[float], frac_rnd: list[float], figures_dir: str) -> None: ...
    # Fig 2: per-step line plot steps 1-50

def plot_gap_trajectory(frac_var: list[float], frac_rnd: list[float], figures_dir: str) -> None: ...
    # Fig 3: gap per step, hlines at 0.0 and 0.05

def plot_reward_std_histogram(log_var: list[dict], log_rnd: list[dict], figures_dir: str) -> None: ...
    # Fig 4: group reward std histogram at steps 10, 20, 50

def generate_all_figures(cfg: H_M2Config, gate_metrics: dict, frac_var: list[float], frac_rnd: list[float], log_var: list[dict], log_rnd: list[dict]) -> None: ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: Config, Dataset, Train, Analyze, Visualize

```python
def main(cfg: H_M2Config = None) -> None: ...
    # 1. load_mbpp_subsets
    # 2. run_grpo(variance50) -> log_var
    # 3. run_grpo(random50) -> log_rnd
    # 4. extract + compute gate metrics
    # 5. save_results
    # 6. generate_all_figures
    # 7. print gate result + assert gap > 0

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-E1 profiling JSON | `docs/youra_research/h-e1/results/mbpp_variance_profile.json` | local artifact, no import |
| H-M1 comparison script (reference) | N/A — not imported | `docs/youra_research/h-m1/code/compare_variance_selection.py` |

**Verified from**: `docs/youra_research/h-m1/code/compare_variance_selection.py` (actual implementation)
**Note**: H-M2 does not import H-M1 code. It reads the same H-E1 JSON artifact directly. H-M1 `load_profiling_output` logic is replicated in `dataset.py::load_variance_50_ids`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create dir structure, config.py, results/figures dirs | 4 | 1+1+1+1 |
| A-2 | Dataset Construction | dataset.py: load H-E1 JSON, build variance-50 and random-50 subsets with validation | 8 | 2+2+2+2 |
| A-3 | Reward Function | reward.py: subprocess execution reward compatible with TRL interface | 10 | 2+1+4+3 |
| A-4 | GRPO Training Runner | train.py: format prompt, GRPOConfig, GRPOTrainer.train(), return log_history | 14 | 3+3+4+4 |
| A-5 | Analysis & Gate | analyze.py: extract frac_zero_std, compute gate metrics, save JSON | 9 | 2+2+3+2 |
| A-6 | Visualization | visualize.py: 4 figures (bar, line, gap, histogram) | 8 | 2+1+3+2 |
| A-7 | Orchestrator | run_experiment.py: wire all modules, run both conditions sequentially | 7 | 1+3+2+1 |
| A-8 | End-to-End Validation | Smoke test both training runs complete, frac_zero_std logged, gate asserts pass | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-5, A-8], Low(4-8): [A-1, A-2, A-6, A-7]
