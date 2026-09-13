# Architecture: H-E1
## Binary vs Ratio Reward Signal in GRPO Training

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC)  
**Date:** 2026-08-31

Applied: Flat-script PoC pattern (one script per concern, shared config)
Applied: Subprocess sandbox pattern (isolated code execution with timeout)
Applied: Callback-based gradient logging (trainer hook → CSV)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field experiment: no existing codebase. Serena analysis skipped.  
**Analyzed Path**: N/A  
**Findings**: New implementation from scratch.

---

## File Organization

```
h-e1/
  code/
    data.py          # APPS loading, filtering, prompt formatting
    rewards.py       # binary_reward, ratio_reward, sandbox executor
    train.py         # GRPO training loop for one condition (CLI arg selects condition)
    evaluate.py      # HumanEval eval at step-200 checkpoint
    analyze.py       # bootstrap CI, visualization (4 figures)
    config.py        # single GRPOConfig dataclass, all hyperparameters
  configs/
    experiment_config.yaml   # serialized config snapshot for reproducibility
  outputs/
    gradient_norms_binary.csv
    gradient_norms_ratio.csv
    checkpoints/
      binary/step-200/
      ratio/step-200/
  figures/           # -> docs/youra_research/h-e1/figures/ (symlink or direct)
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class GRPOConfig:
    model_id: str = "deepseek-ai/deepseek-coder-6.7b-instruct"
    dataset_id: str = "codeparrot/apps"
    min_test_cases: int = 5
    group_size: int = 8
    prompt_batch_size: int = 64
    max_new_tokens: int = 512
    temperature: float = 1.0
    learning_rate: float = 1e-6
    weight_decay: float = 0.01
    warmup_steps: int = 10
    clip_ratio: float = 0.2
    kl_beta: float = 0.01
    train_steps: int = 500
    checkpoint_step: int = 200
    sandbox_timeout: int = 5
    seed: int = 42
    output_dir: str = "outputs"

def load_config() -> GRPOConfig: ...
def save_config(cfg: GRPOConfig, path: str) -> None: ...
```

---

### Data (`code/data.py`)

**Dependencies**: Config

```python
from datasets import Dataset

def load_apps(min_test_cases: int = 5) -> Dataset: ...
    # loads codeparrot/apps train split, filters ≥5 test cases

def format_prompt(example: dict) -> str: ...
    # "{problem_description}\n\nWrite a Python solution:"
    # truncates description at 1024 tokens

def get_test_cases(example: dict) -> list[dict]: ...
    # parses input_output JSON, returns list of {input, output} dicts
```

---

### Rewards (`code/rewards.py`)

**Dependencies**: none (stdlib only)

```python
def execute_code(code: str, test_input: str, timeout: int = 5) -> bool: ...
    # subprocess.run with timeout; catches TimeoutExpired, errors → False

def binary_reward(completion: str, test_cases: list[dict]) -> float: ...
    # 1.0 if all pass, else 0.0

def ratio_reward(completion: str, test_cases: list[dict]) -> float: ...
    # k/n where k = number of passing test cases

def make_reward_fn(mode: str):
    # returns binary_reward or ratio_reward callable
    # mode: "binary" | "ratio"
    def reward_fn(completions: list[str], test_cases: list[dict]) -> list[float]: ...
    return reward_fn
```

---

### Train (`code/train.py`)

**Dependencies**: Config, Data, Rewards

```python
import argparse
from trl import GRPOTrainer, GRPOConfig as TRLGRPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

class GradNormCallback:
    # trl TrainerCallback subclass
    def __init__(self, output_csv: str): ...
    def on_step_end(self, args, state, control, **kwargs) -> None: ...
        # logs: global_step, grad_norm, mean_reward, std_reward → CSV

def build_trainer(cfg: GRPOConfig, condition: str) -> GRPOTrainer: ...
    # condition: "binary" | "ratio"
    # wires reward_fn, GradNormCallback, checkpoint saving at step 200

def main() -> None: ...
    # argparse: --condition {binary,ratio}
    # loads config, builds trainer, trainer.train()

if __name__ == "__main__":
    main()
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config

```python
def load_checkpoint(checkpoint_path: str): ...
    # returns (model, tokenizer) from saved step-200 checkpoint

def eval_humaneval(model, tokenizer) -> float: ...
    # greedy decode 164 HumanEval problems
    # returns pass@1 score
    # uses human_eval.evaluation.evaluate_functional_correctness

def main() -> None: ...
    # argparse: --condition {binary,ratio}
    # loads step-200 checkpoint, runs eval_humaneval, prints pass@1
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: numpy, scipy, matplotlib, pandas

```python
def load_grad_norms(csv_path: str) -> pd.DataFrame: ...
    # columns: global_step, grad_norm, mean_reward, std_reward

def bootstrap_ci(binary_norms: np.ndarray, ratio_norms: np.ndarray,
                 n_bootstrap: int = 1000, ci: float = 0.95
                 ) -> dict: ...
    # returns {mean_diff, ci_lower, ci_upper, excludes_zero}

def plot_bar_humaneval(binary_score: float, ratio_score: float) -> None: ...
def plot_grad_norm_trajectory(df_binary: pd.DataFrame, df_ratio: pd.DataFrame) -> None: ...
def plot_reward_histograms(df_binary: pd.DataFrame, df_ratio: pd.DataFrame) -> None: ...
def plot_mean_reward(df_binary: pd.DataFrame, df_ratio: pd.DataFrame) -> None: ...

def main() -> None: ...
    # loads CSVs, runs bootstrap_ci, prints gate evaluation, saves 4 figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data pipeline | APPS loading, ≥5 test case filter, prompt formatter, test case parser | 5 | 2+1+1+1 |
| E-2 | Reward functions | Subprocess sandbox, binary_reward, ratio_reward, make_reward_fn | 5 | 1+1+2+1 |
| E-3 | GRPO training loop | GRPOTrainer wiring, GradNormCallback, checkpoint at step 200, CLI condition arg | 7 | 2+2+2+1 |
| E-4 | HumanEval evaluation | Checkpoint loading, greedy decode 164 problems, pass@1 reporting | 4 | 1+1+1+1 |
| E-5 | Analysis and visualization | Bootstrap CI, gate evaluation, 4 figures | 4 | 1+1+1+1 |

**Total Complexity**: 25  
**Distribution**: High(14-17): [], Medium(9-13): [], Low(4-8): [E-1, E-2, E-3, E-4, E-5]

---

## Run Order

```bash
# 1. Train both conditions (can run in parallel on separate GPUs)
python code/train.py --condition binary
python code/train.py --condition ratio

# 2. Evaluate checkpoints
python code/evaluate.py --condition binary
python code/evaluate.py --condition ratio

# 3. Analyze and plot
python code/analyze.py
```
