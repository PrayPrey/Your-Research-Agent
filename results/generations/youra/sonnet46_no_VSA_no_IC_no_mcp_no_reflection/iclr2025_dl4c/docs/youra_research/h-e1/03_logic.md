# Logic: H-E1
## Binary vs Ratio Reward Signal in GRPO Training

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC)
**Date:** 2026-08-31

Applied: Flat-script PoC pattern
Applied: Subprocess sandbox with timeout
Applied: Trainer callback CSV logging
Applied: Percentile bootstrap CI (non-parametric)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field: no existing codebase. Serena skipped.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E-1: Data Pipeline

### API Signatures

```python
# data.py
from datasets import Dataset

def load_apps(min_test_cases: int = 5) -> Dataset:
    """Load APPS train split, filter to problems with >= min_test_cases."""
    ...

def format_prompt(problem_description: str, tokenizer, max_tokens: int = 1024) -> str:
    """Truncate description to max_tokens, return formatted prompt string."""
    ...

def get_test_cases(example: dict) -> list[dict]:
    """Parse example['input_output'] JSON -> list of {'input': str, 'output': str}."""
    ...

def build_dataset(cfg: "GRPOConfig", tokenizer) -> Dataset:
    """Load, filter, format APPS. Returns dataset with 'prompt' and 'test_cases' columns."""
    ...
```

### Pseudo-code: load_apps

```
1. ds = load_dataset("codeparrot/apps", split="train")
2. def has_enough_tests(ex):
       tc = json.loads(ex["input_output"] or "{}")
       return len(tc.get("inputs", [])) >= min_test_cases
3. return ds.filter(has_enough_tests)
```

### Pseudo-code: format_prompt

```
1. token_ids = tokenizer.encode(description)
2. if len(token_ids) > max_tokens:
       description = tokenizer.decode(token_ids[:max_tokens])
3. return f"{description}\n\nWrite a Python solution:"
```

---

## E-2: Reward Functions

### API Signatures

```python
# rewards.py
import subprocess
from typing import Optional

def execute_code(
    code: str,
    test_input: str,
    expected_output: str,
    timeout: int = 5
) -> bool:
    """Run code in subprocess, compare stdout to expected_output. Returns pass/fail."""
    ...

def binary_reward(
    completion: str,
    test_cases: list[dict]
) -> float:
    """Return 1.0 if all test cases pass, else 0.0."""
    ...

def ratio_reward(
    completion: str,
    test_cases: list[dict]
) -> float:
    """Return k/n where k = number of passing test cases, n = total."""
    ...

def make_reward_fn(mode: str):
    """
    mode: 'binary' | 'ratio'
    Returns trl-compatible reward function:
      reward_fn(completions, prompts, **kwargs) -> list[float]
    The returned fn reads test_cases from kwargs['test_cases'].
    """
    def reward_fn(
        completions: list[str],
        prompts: list[str],
        test_cases: list[list[dict]],
        **kwargs
    ) -> list[float]:
        ...
    return reward_fn
```

### Pseudo-code: execute_code

```
1. script = f"import sys\n{code}\n"
2. result = subprocess.run(
       ["python", "-c", script],
       input=test_input, capture_output=True, text=True,
       timeout=timeout
   )
3. return result.stdout.strip() == expected_output.strip()
4. except (subprocess.TimeoutExpired, Exception): return False
```

### Pseudo-code: binary_reward

```
1. for tc in test_cases:
       if not execute_code(completion, tc["input"], tc["output"]): return 0.0
2. return 1.0
```

### Pseudo-code: ratio_reward

```
1. passes = sum(execute_code(completion, tc["input"], tc["output"]) for tc in test_cases)
2. return passes / len(test_cases)
```

---

## E-3: GRPO Training Loop

### API Signatures

```python
# train.py
import csv
from transformers import TrainerCallback, TrainerState, TrainerControl, TrainingArguments
from trl import GRPOTrainer

class GradNormCallback(TrainerCallback):
    def __init__(self, output_csv: str) -> None:
        """Open CSV at output_csv, write header: global_step,grad_norm,mean_reward,std_reward."""
        ...

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ) -> None:
        """
        Read grad_norm from kwargs['model'] or state logs.
        Write row to CSV: state.global_step, grad_norm, mean_reward, std_reward.
        """
        ...

def build_trainer(
    cfg: "GRPOConfig",
    condition: str,
    model,
    tokenizer,
    dataset: "Dataset"
) -> GRPOTrainer:
    """
    condition: 'binary' | 'ratio'
    Wires reward_fn from make_reward_fn(condition).
    Attaches GradNormCallback -> outputs/gradient_norms_{condition}.csv
    Sets save_steps=cfg.checkpoint_step.
    Returns configured GRPOTrainer.
    """
    ...

def main() -> None:
    """CLI: --condition {binary,ratio}. Loads cfg, model, tokenizer, dataset, trains."""
    ...
```

### Pseudo-code: GradNormCallback.on_step_end

```
1. model = kwargs.get("model")
2. grad_norm = compute_grad_norm(model)  # torch.nn.utils.clip_grad_norm_ returns norm
   # OR read from state.log_history[-1].get("grad_norm", float("nan"))
3. rewards = kwargs.get("rewards", [])
4. mean_r = np.mean(rewards) if rewards else float("nan")
5. std_r = np.std(rewards) if rewards else float("nan")
6. writer.writerow([state.global_step, grad_norm, mean_r, std_r])
```

### Pseudo-code: build_trainer

```
1. trl_cfg = GRPOConfig(
       num_train_epochs=1,
       max_steps=cfg.train_steps,
       per_device_train_batch_size=cfg.prompt_batch_size,
       num_generations=cfg.group_size,
       max_new_tokens=cfg.max_new_tokens,
       temperature=cfg.temperature,
       learning_rate=cfg.learning_rate,
       weight_decay=cfg.weight_decay,
       warmup_steps=cfg.warmup_steps,
       epsilon=cfg.clip_ratio,
       beta=cfg.kl_beta,
       save_steps=cfg.checkpoint_step,
       output_dir=f"{cfg.output_dir}/checkpoints/{condition}",
       seed=cfg.seed,
   )
2. reward_fn = make_reward_fn(condition)
3. callback = GradNormCallback(f"{cfg.output_dir}/gradient_norms_{condition}.csv")
4. return GRPOTrainer(
       model=model, args=trl_cfg, tokenizer=tokenizer,
       train_dataset=dataset, reward_funcs=[reward_fn],
       callbacks=[callback]
   )
```

### Model I/O Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L_prompt] | B = prompt_batch_size * group_size = 512 |
| attention_mask | [B, L_prompt] | |
| generated_ids | [B, L_prompt + L_gen] | L_gen <= 512 |
| logits | [B, L_gen, V] | V = vocab size ~32k |
| log_probs | [B, L_gen] | per-token log prob for ratio loss |
| rewards | [B] | scalar reward per completion |

---

## E-4: HumanEval Evaluation

### API Signatures

```python
# evaluate.py
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_checkpoint(
    checkpoint_path: str,
    dtype=torch.bfloat16
) -> tuple["AutoModelForCausalLM", "AutoTokenizer"]:
    """Load model and tokenizer from checkpoint_path."""
    ...

def generate_completion(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 512
) -> str:
    """Greedy decode (do_sample=False, temperature=1.0). Returns generated text only."""
    ...

def eval_humaneval(
    model,
    tokenizer,
    problems: list[dict],
    max_new_tokens: int = 512
) -> float:
    """
    Greedy decode all 164 HumanEval problems.
    Returns pass@1 as float in [0, 1].
    Uses human_eval.evaluation.evaluate_functional_correctness internally.
    """
    ...

def main() -> None:
    """CLI: --condition {binary,ratio} [--checkpoint-step 200]."""
    ...
```

### Pseudo-code: eval_humaneval

```
1. samples = []
2. for problem in problems:
       prompt = problem["prompt"]
       completion = generate_completion(model, tokenizer, prompt)
       samples.append({"task_id": problem["task_id"], "completion": completion})
3. write samples to temp JSONL
4. results = evaluate_functional_correctness(temp_jsonl)
5. return results["pass@1"]
```

---

## E-5: Analysis and Visualization

### API Signatures

```python
# analyze.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_grad_norms(csv_path: str) -> pd.DataFrame:
    """Load CSV with columns: global_step, grad_norm, mean_reward, std_reward."""
    ...

def bootstrap_ci(
    binary_norms: np.ndarray,  # [400] steps 100-500
    ratio_norms: np.ndarray,   # [400] steps 100-500
    n_bootstrap: int = 1000,
    ci: float = 0.95
) -> dict:
    """
    Bootstrap CI on mean(ratio_norms - binary_norms).
    Returns: {mean_diff, ci_lower, ci_upper, excludes_zero: bool}
    """
    ...

def plot_bar_humaneval(
    binary_score: float,
    ratio_score: float,
    out_path: str
) -> None:
    """Bar chart: binary vs ratio pass@1 at step 200."""
    ...

def plot_grad_norm_trajectory(
    df_binary: pd.DataFrame,
    df_ratio: pd.DataFrame,
    ci_result: dict,
    out_path: str
) -> None:
    """Line plot steps 1-500, shaded 95% CI band on difference."""
    ...

def plot_reward_histograms(
    df_binary: pd.DataFrame,
    df_ratio: pd.DataFrame,
    steps: list[int],
    out_path: str
) -> None:
    """Histograms of reward distribution at steps 50, 100, 200, 500."""
    ...

def plot_mean_reward(
    df_binary: pd.DataFrame,
    df_ratio: pd.DataFrame,
    out_path: str
) -> None:
    """Line plot of mean_reward over training steps for both conditions."""
    ...

def main() -> None:
    """Load CSVs, run bootstrap_ci on steps 100-500, print gate result, save 4 figures."""
    ...
```

### Pseudo-code: bootstrap_ci

```
1. diff = ratio_norms - binary_norms          # [T]
2. boot_means = np.empty(n_bootstrap)
3. for i in range(n_bootstrap):
       sample = np.random.choice(diff, size=len(diff), replace=True)
       boot_means[i] = sample.mean()
4. alpha = (1 - ci) / 2
5. ci_lower = np.percentile(boot_means, 100 * alpha)
6. ci_upper = np.percentile(boot_means, 100 * (1 - alpha))
7. return {
       "mean_diff": diff.mean(),
       "ci_lower": ci_lower,
       "ci_upper": ci_upper,
       "excludes_zero": not (ci_lower <= 0 <= ci_upper)
   }
```
