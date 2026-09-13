# Logic: H-M1
## Ratio vs Binary Reward Policy Target Shift in GRPO Training

**Hypothesis:** H-M1 | **Type:** MECHANISM (INCREMENTAL from H-E1)
**Date:** 2026-08-31

Applied: Incremental extension pattern (reuse H-E1, minimal new code)
Applied: Multi-checkpoint evaluation loop
Applied: Percentile bootstrap CI (non-parametric)
Applied: Subprocess sandbox with timeout
Applied: Stratified sampling for evaluation datasets

---

## Codebase Analysis (Serena)

**Project Type**: INCREMENTAL — extends H-E1 codebase
**Analyzed Path**: `docs/youra_research/h-e1/code/`

**Key symbols discovered from H-E1 actual code:**

| Symbol | File | Verified Signature |
|--------|------|-------------------|
| `GRPOConfig` | config.py | dataclass with fields: model_name, dtype, dataset_name, min_test_cases, max_prompt_tokens, group_size, prompt_batch_size, max_new_tokens, temperature, learning_rate, clip_ratio, kl_beta, warmup_steps, train_steps, checkpoint_step, output_dir, sandbox_timeout, reward_mode, seed |
| `GradNormCallback` | train.py | `__init__(self, output_csv: str)`, `on_log(self, args, state, control, logs=None, **kwargs)` |
| `build_trainer` | train.py | `build_trainer(cfg: GRPOConfig, condition: str, model, tokenizer, dataset) -> GRPOTrainer` |
| `execute_code` | rewards.py | `execute_code(code: str, test_input: str, expected_output: str, timeout: int = 5) -> bool` |
| `binary_reward` | rewards.py | `binary_reward(completion: str, test_cases: list) -> float` |
| `ratio_reward` | rewards.py | `ratio_reward(completion: str, test_cases: list) -> float` |
| `make_reward_fn` | rewards.py | `make_reward_fn(mode: str, test_cases_lookup: dict) -> Callable` |
| `build_dataset` | data.py | `build_dataset(cfg: GRPOConfig, tokenizer) -> Dataset` |
| `load_apps` | data.py | `load_apps(min_test_cases: int = 5) -> Dataset` |
| `format_prompt` | data.py | `format_prompt(problem_description: str, tokenizer, max_tokens: int = 1024) -> str` |

**Import pattern (verified from train.py):**
```python
sys.path.insert(0, os.path.dirname(__file__))
from config import GRPOConfig, load_config, save_config
from data import build_dataset
from rewards import make_reward_fn
```

**Key field names verified from actual H-E1 config.py:**
- `checkpoint_step: int = 200` (singular — H-M1 changes this to `checkpoint_steps: list[int]`)
- `kl_beta: float = 0.01` (H-M1 overrides to 0.04)
- `warmup_steps: int = 10` (H-M1 overrides to 100)
- `max_new_tokens: int = 256` (H-M1 overrides to 512)
- `max_prompt_tokens: int = 1024` (H-M1 overrides to 512)
- `sandbox_timeout: int = 5` (H-M1 overrides to 3)
- `train_steps: int = 500` (H-M1 overrides to 1000)

---

## External Dependencies API

Verified from H-E1 actual code (`docs/youra_research/h-e1/code/`):

```python
# rewards.py — reuse unchanged
def execute_code(code: str, test_input: str, expected_output: str, timeout: int = 5) -> bool: ...
def binary_reward(completion: str, test_cases: list) -> float: ...
def ratio_reward(completion: str, test_cases: list) -> float: ...
def make_reward_fn(mode: str, test_cases_lookup: dict) -> Callable[[list[str], list], list[float]]: ...

# data.py — reuse unchanged
def load_apps(min_test_cases: int = 5) -> Dataset: ...
def build_dataset(cfg: "GRPOConfig", tokenizer) -> Dataset: ...

# train.py — extend GradNormCallback pattern
class GradNormCallback(TrainerCallback):
    def __init__(self, output_csv: str) -> None: ...
    def on_log(self, args: TrainingArguments, state: TrainerState,
               control: TrainerControl, logs: dict = None, **kwargs) -> None: ...
def build_trainer(cfg: GRPOConfig, condition: str, model, tokenizer, dataset) -> GRPOTrainer: ...
```

---

## A-2 Subtask 1: FractionPartialCallback

Extension of H-E1's `GradNormCallback` pattern — logs ratio reward degeneracy signal.

### API Signatures

```python
# train_hm1.py (new file, imports from h-e1 via sys.path)
import csv, os
from transformers import TrainerCallback, TrainerState, TrainerControl, TrainingArguments

class FractionPartialCallback(TrainerCallback):
    """Logs fraction of completions with reward in (0,1) exclusive — monitors ratio degeneracy."""

    def __init__(self, output_csv: str, alert_threshold: float = 0.05) -> None:
        """
        Args:
            output_csv: path for CSV log
            alert_threshold: if fraction_partial < threshold, print degeneracy warning
        """
        ...

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict = None,
        **kwargs,
    ) -> None:
        """Extract fraction_partial from logs, write to CSV, alert if below threshold."""
        # CSV columns: global_step, reward_mean, reward_std, fraction_partial, grad_norm, kl
        ...
```

### Pseudo-code

```
on_log(logs):
    step = state.global_step
    reward_mean = logs.get("rewards/.../mean", nan)
    reward_std  = logs.get("rewards/.../std", nan)
    grad_norm   = logs.get("grad_norm", nan)
    kl          = logs.get("kl", nan)
    
    # fraction_partial: rewards strictly between 0 and 1
    # trl logs individual reward values in "rewards" key as list
    rewards_list = logs.get("rewards", [])
    if rewards_list:
        partial = [r for r in rewards_list if 0.0 < r < 1.0]
        fraction_partial = len(partial) / len(rewards_list)
    else:
        fraction_partial = nan
    
    writer.writerow([step, reward_mean, reward_std, fraction_partial, grad_norm, kl])
    
    if not isnan(fraction_partial) and fraction_partial < alert_threshold:
        print(f"⚠ Step {step}: fraction_partial={fraction_partial:.3f} < {alert_threshold} — ratio degeneracy?")
```

---

## A-2 Subtask 2: Extended Training Loop

### API Signatures

```python
# train_hm1.py

from dataclasses import dataclass
from typing import NamedTuple

class TrainingResult(NamedTuple):
    condition: str                          # "binary" | "ratio"
    checkpoint_paths: dict[int, str]        # {step: checkpoint_dir_path}
    training_log_path: str                  # path to CSV log
    final_step: int

def run_condition(
    condition: str,                         # "binary" | "ratio"
    cfg: "HM1Config",
    model_name: str,
) -> TrainingResult:
    """
    Full training run for one condition to cfg.train_steps.
    Saves checkpoints at each step in cfg.checkpoint_steps.
    Returns TrainingResult with checkpoint paths.
    
    Args:
        condition: reward mode — "binary" or "ratio"
        cfg: HM1Config with all hyperparameters
        model_name: HuggingFace model identifier
    Returns:
        TrainingResult
    """
    ...
```

### Pseudo-code

```
run_condition(condition, cfg, model_name):
    set_seed(cfg.seed)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=bfloat16, device_map="auto")
    dataset = build_dataset(cfg, tokenizer)   # reuse H-E1 data.py
    reward_fn = make_reward_fn(condition, ...)  # reuse H-E1 rewards.py
    
    callbacks = [
        GradNormCallback(f"{cfg.output_dir}/gradient_norms_{condition}.csv"),  # H-E1
        FractionPartialCallback(f"{cfg.output_dir}/training_log_{condition}.csv")  # new
    ]
    
    trainer = build_trainer(cfg, condition, model, tokenizer, dataset)  # H-E1 extended
    # Override: trainer saves checkpoint at each step in cfg.checkpoint_steps
    
    trainer.train()
    
    checkpoint_paths = {}
    for step in cfg.checkpoint_steps:
        path = f"{cfg.output_dir}/checkpoints/{condition}/checkpoint-{step}"
        if os.path.exists(path):
            checkpoint_paths[step] = path
    
    return TrainingResult(condition, checkpoint_paths, training_log_path, cfg.train_steps)
```

---

## A-3 Subtask: HumanEval Multi-Checkpoint Evaluator

### API Signatures

```python
# eval_humaneval.py

from typing import Optional
from datasets import Dataset

def load_humaneval() -> Dataset:
    """Load full HumanEval test set (164 problems)."""
    # load_dataset("openai_humaneval", split="test")
    ...

def evaluate_humaneval_checkpoint(
    checkpoint_path: str,
    tokenizer,
    problems: Dataset,
    timeout: float = 10.0,
) -> float:
    """
    Evaluate one checkpoint on HumanEval.
    Args:
        checkpoint_path: path to saved checkpoint dir
        tokenizer: tokenizer (reuse, don't reload)
        problems: HumanEval dataset (164 problems)
        timeout: per-problem execution timeout
    Returns:
        pass@1 (float in [0,1])
    """
    ...

def batch_evaluate_humaneval(
    checkpoint_paths: dict[int, str],
    model_name: str,
    problems: Optional[Dataset] = None,
) -> dict[int, float]:
    """
    Evaluate multiple checkpoints sequentially.
    Args:
        checkpoint_paths: {step: checkpoint_path} from TrainingResult
        model_name: base model name for tokenizer
        problems: preloaded HumanEval dataset (loads once if None)
    Returns:
        {step: pass@1} for each checkpoint
    """
    ...
```

### Pseudo-code

```
batch_evaluate_humaneval(checkpoint_paths, model_name, problems=None):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if problems is None:
        problems = load_humaneval()
    
    results = {}
    for step, ckpt_path in sorted(checkpoint_paths.items()):
        model = AutoModelForCausalLM.from_pretrained(ckpt_path, dtype=bfloat16, device_map="auto")
        results[step] = evaluate_humaneval_checkpoint(ckpt_path, tokenizer, problems)
        del model  # free GPU memory between checkpoints
        torch.cuda.empty_cache()
    
    return results  # {200: 0.46, 400: 0.48, ..., 1000: 0.51}

evaluate_humaneval_checkpoint(checkpoint_path, tokenizer, problems, timeout):
    model = AutoModelForCausalLM.from_pretrained(checkpoint_path, ...)
    completions = []
    for problem in problems:
        prompt = problem["prompt"]
        tokens = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**tokens, max_new_tokens=512,
                                  do_sample=False, temperature=1.0)  # greedy
        completion = tokenizer.decode(out[0][tokens.input_ids.shape[1]:])
        completions.append(completion)
    
    # Use HuggingFace code_eval metric
    code_eval = load("code_eval")
    pass_at_k, _ = code_eval.compute(
        references=[p["test"] for p in problems],
        predictions=[[c] for c in completions],
        k=[1], num_workers=4
    )
    return pass_at_k["pass@1"]
```

---

## A-5 Subtask 1: APPS Validation Stratified Sampler

### API Signatures

```python
# eval_apps_allpass.py

from datasets import Dataset

def stratify_apps_val(
    dataset: Dataset,
    n: int = 500,
    difficulty_key: str = "difficulty",
) -> Dataset:
    """
    Sample n problems stratified by difficulty from APPS validation split.
    Args:
        dataset: full APPS validation split
        n: number of problems to sample
        difficulty_key: column name for difficulty label
    Returns:
        Dataset with n problems, difficulty-stratified
    """
    ...
```

### Pseudo-code

```
stratify_apps_val(dataset, n=500):
    difficulty_groups = {}
    for ex in dataset:
        d = ex[difficulty_key]
        difficulty_groups.setdefault(d, []).append(ex)
    
    total = len(dataset)
    sampled = []
    for d, group in difficulty_groups.items():
        proportion = len(group) / total
        k = max(1, round(proportion * n))
        sampled.extend(random.sample(group, min(k, len(group))))
    
    # Trim or pad to exactly n
    return Dataset.from_list(sampled[:n])
```

---

## A-5 Subtask 2: APPS All-Pass Evaluator

### API Signatures

```python
# eval_apps_allpass.py

from dataclasses import dataclass

@dataclass
class AppsAllPassResult:
    allpass_fraction: float          # fraction of problems where ALL tests pass
    per_problem_rates: list[float]   # k/n rate per problem (for Figure 3 distribution)
    n_problems: int

def evaluate_apps_allpass(
    checkpoint_path: str,
    model_name: str,
    apps_val_dataset: Dataset,       # pre-stratified 500 problems
    sandbox_timeout: float = 3.0,
) -> AppsAllPassResult:
    """
    Evaluate checkpoint on APPS validation all-pass rate.
    Args:
        checkpoint_path: path to checkpoint dir
        model_name: for tokenizer
        apps_val_dataset: stratified APPS val (500 problems)
        sandbox_timeout: per-test execution timeout
    Returns:
        AppsAllPassResult with allpass_fraction and per_problem_rates
    """
    ...
```

### Pseudo-code

```
evaluate_apps_allpass(checkpoint_path, model_name, apps_val_dataset, sandbox_timeout):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(checkpoint_path, ...)
    
    per_problem_rates = []
    for problem in apps_val_dataset:
        test_cases = get_test_cases(problem)    # reuse H-E1 data.py
        prompt = format_prompt(problem["question"], tokenizer, max_tokens=512)
        
        tokens = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**tokens, max_new_tokens=512, do_sample=False)
        completion = tokenizer.decode(out[0][tokens.input_ids.shape[1]:])
        
        # Compute k/n using H-E1 execute_code
        k = sum(execute_code(completion, tc["input"], tc["output"], sandbox_timeout)
                for tc in test_cases)
        n = len(test_cases)
        rate = k / n if n > 0 else 0.0
        per_problem_rates.append(rate)
    
    allpass_fraction = sum(r == 1.0 for r in per_problem_rates) / len(per_problem_rates)
    return AppsAllPassResult(allpass_fraction, per_problem_rates, len(per_problem_rates))
```

---

## A-6 Subtask 1: Bootstrap CI

### API Signatures

```python
# analyze.py

from dataclasses import dataclass
import numpy as np

@dataclass
class BootstrapResult:
    mean_diff: float         # mean(a) - mean(b)
    ci_lower: float          # 95% CI lower bound
    ci_upper: float          # 95% CI upper bound
    excludes_zero: bool      # True if ci_lower > 0

def bootstrap_ci(
    values_a: list[float],   # per-problem pass/fail for condition A (ratio)
    values_b: list[float],   # per-problem pass/fail for condition B (binary)
    n_bootstrap: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """
    Paired bootstrap CI on mean(a) - mean(b).
    Args:
        values_a: per-problem 0/1 results for condition a (ratio), len=164
        values_b: per-problem 0/1 results for condition b (binary), len=164
        n_bootstrap: number of bootstrap samples
        ci_level: confidence level (0.95 → 95% CI)
        seed: RNG seed for reproducibility
    Returns:
        BootstrapResult
    """
    ...
```

### Pseudo-code

```
bootstrap_ci(values_a, values_b, n_bootstrap=1000, ci_level=0.95, seed=42):
    rng = np.random.default_rng(seed)
    a = np.array(values_a)  # shape (164,)
    b = np.array(values_b)  # shape (164,)
    n = len(a)
    
    boot_diffs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)   # resample with replacement
        boot_diffs.append(a[idx].mean() - b[idx].mean())
    
    boot_diffs = np.array(boot_diffs)
    alpha = 1 - ci_level
    ci_lower = np.percentile(boot_diffs, 100 * alpha / 2)
    ci_upper = np.percentile(boot_diffs, 100 * (1 - alpha / 2))
    mean_diff = a.mean() - b.mean()
    
    return BootstrapResult(mean_diff, ci_lower, ci_upper, excludes_zero=(ci_lower > 0))
```

---

## A-6 Subtask 2: Mechanism Verifier

### API Signatures

```python
# analyze.py

from dataclasses import dataclass

@dataclass
class MechanismResult:
    gate_satisfied: bool
    p1_humaneval_gap: float           # ratio_he - binary_he
    p1_ci_lower: float                # 95% bootstrap CI lower bound
    p1_satisfied: bool
    p2_policy_shift: bool             # ratio_apps_allpass <= binary_apps_allpass
    p2_apps_allpass_ratio: float
    p2_apps_allpass_binary: float
    mechanism_confirmed: bool
    result: str                       # "GATE_SATISFIED" | "GATE_FAILED"

def verify_h_m1_mechanism(
    ratio_humaneval_pass1: float,
    binary_humaneval_pass1: float,
    ratio_apps_allpass: float,
    binary_apps_allpass: float,
    bootstrap_ci_lower: float,
    threshold_gap: float = 0.03,
) -> MechanismResult:
    """
    Verify H-M1 gate conditions.
    P1: HumanEval gap >= threshold AND CI lower > 0
    P2: ratio_apps_allpass <= binary_apps_allpass (policy target shift)
    GATE = P1 AND P2
    """
    ...

def check_ratio_degeneracy(rewards_per_group: list[float]) -> bool:
    """Returns True if ratio reward has degenerated (all values 0.0 or 1.0)."""
    return all(r in (0.0, 1.0) for r in rewards_per_group)

def check_gradient_health(grad_norm: float, threshold: float = 10.0) -> bool:
    """Returns True if gradient norm is healthy."""
    return grad_norm < threshold
```

### Pseudo-code

```
verify_h_m1_mechanism(ratio_he, binary_he, ratio_apps, binary_apps, ci_lower, threshold=0.03):
    gap = ratio_he - binary_he
    p1 = (gap >= threshold) and (ci_lower > 0)
    p2 = ratio_apps <= binary_apps
    gate = p1 and p2
    
    return MechanismResult(
        gate_satisfied=gate,
        p1_humaneval_gap=gap,
        p1_ci_lower=ci_lower,
        p1_satisfied=p1,
        p2_policy_shift=p2,
        p2_apps_allpass_ratio=ratio_apps,
        p2_apps_allpass_binary=binary_apps,
        mechanism_confirmed=gate,
        result="GATE_SATISFIED" if gate else "GATE_FAILED"
    )
```

---

## A-8 Subtask: Orchestrator CLI

### API Signatures

```python
# run_experiment.py

def parse_args() -> argparse.Namespace:
    """
    CLI arguments:
      --condition {binary,ratio,both}  default: both
      --resume_from_step int           default: None (start from scratch)
      --skip_eval bool                 default: False
      --config_path str                default: None (use HM1Config defaults)
      --output_dir str                 default: "outputs/h-m1"
    """
    ...

def main() -> None:
    """
    End-to-end pipeline:
    1. Load config
    2. Run binary condition (or skip if --condition=ratio)
    3. Run ratio condition (or skip if --condition=binary)
    4. Evaluate all checkpoints (HumanEval)
    5. Evaluate step 1000 (MBPP, APPS all-pass)
    6. Statistical analysis (bootstrap CI, verify mechanism)
    7. Visualize (4 figures)
    8. Write results JSON
    """
    ...
```

### Results JSON Schema

```json
{
  "hypothesis": "H-M1",
  "condition": "both",
  "checkpoint_results": {
    "binary": {200: 0.46, 400: 0.47, 600: 0.48, 800: 0.48, 1000: 0.49},
    "ratio":  {200: 0.47, 400: 0.49, 600: 0.50, 800: 0.51, 1000: 0.52}
  },
  "final": {
    "binary": {
      "humaneval_pass1": 0.49,
      "mbpp_pass1": 0.55,
      "apps_allpass_rate": 0.18
    },
    "ratio": {
      "humaneval_pass1": 0.52,
      "mbpp_pass1": 0.57,
      "apps_allpass_rate": 0.15
    }
  },
  "analysis": {
    "humaneval_gap": 0.03,
    "bootstrap_ci_lower": 0.002,
    "bootstrap_ci_upper": 0.058,
    "ci_excludes_zero": true,
    "p1_satisfied": true,
    "p2_policy_shift": true,
    "gate_satisfied": true,
    "result": "GATE_SATISFIED"
  }
}
```

### Pseudo-code: main

```
main():
    args = parse_args()
    cfg = load_config(args.config_path) or HM1Config(output_dir=args.output_dir)
    
    results = {}
    for condition in get_conditions(args.condition):  # ["binary"], ["ratio"], or both
        if args.resume_from_step:
            # Find existing checkpoints, skip training before resume_step
            ckpt_paths = find_checkpoints(cfg, condition, from_step=args.resume_from_step)
        else:
            training_result = run_condition(condition, cfg, cfg.model_name)
            ckpt_paths = training_result.checkpoint_paths
        
        if not args.skip_eval:
            humaneval_scores = batch_evaluate_humaneval(ckpt_paths, cfg.model_name)
            results[condition] = {"checkpoint_results": humaneval_scores}
    
    if not args.skip_eval and "binary" in results and "ratio" in results:
        # Step-1000 evaluations
        for condition in ["binary", "ratio"]:
            ckpt_1000 = ckpt_paths_by_condition[condition][1000]
            mbpp = evaluate_mbpp(ckpt_1000, cfg.model_name)
            apps = evaluate_apps_allpass(ckpt_1000, cfg.model_name, apps_val_dataset)
            results[condition]["final"] = {mbpp_pass1: mbpp, apps_allpass_rate: apps.allpass_fraction}
        
        # Bootstrap CI on per-problem HumanEval results
        ci = bootstrap_ci(ratio_per_problem, binary_per_problem, n_bootstrap=cfg.bootstrap_n)
        mechanism = verify_h_m1_mechanism(
            ratio_he=results["ratio"]["final"]["humaneval_pass1"],
            binary_he=results["binary"]["final"]["humaneval_pass1"],
            ratio_apps=results["ratio"]["final"]["apps_allpass_rate"],
            binary_apps=results["binary"]["final"]["apps_allpass_rate"],
            bootstrap_ci_lower=ci.ci_lower,
        )
        
        visualize(results, cfg)
        write_json(results_json_path, {hypothesis: "H-M1", ...mechanism fields...})
```
