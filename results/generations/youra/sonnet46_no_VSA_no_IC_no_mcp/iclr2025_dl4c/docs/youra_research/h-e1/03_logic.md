---
title: "Logic: H-E1 — RLEF-Fraction Difficulty-Scaling Existence Proof"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-26"
author: yoon303@ust.ac.kr
source: 03_architecture.md, 03_prd.md
---

Applied: Reward-function-as-pure-function pattern (stateless, batchable, testable in isolation)
Applied: Bootstrap-CI-over-per-problem-binary pattern (standard for pass@k evaluation)
Applied: Callback-based monitoring pattern (zero-overhead training observability)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — new implementation from scratch.
**Planned API surface**: 6 modules (data_utils, reward, train_sft, train_rlef, evaluate, analyze). All APIs specified below from architecture design and PRD requirements. No inheritance hierarchy; flat functions + one callback class.

---

## Subtask L-2-1: Reward Function Implementation

**Parent: E-2** (Reward Function, complexity 10)

### API Signatures

```python
# code/reward.py

import subprocess
import tempfile
import os
from typing import Optional

def fraction_reward_fn(
    completions: list[str],       # model-generated code strings, len = batch_size * G
    prompts: list[str],           # input prompts (unused in reward, kept for TRL compat)
    metadata: list[dict],         # each dict has key "test_cases": list[tuple[str, str]]
) -> list[float]:
    """
    Compute fraction-of-tests-passing reward for each completion.

    Returns: rewards in [0.0, 1.0], len = len(completions)
    TRL GRPOTrainer passes completions of shape [batch_size * G]; rewards same shape.
    """
    ...

def _execute_code(
    code: str,
    stdin: str,
    timeout: float = 3.0,
) -> str:
    """
    Execute code string in subprocess with stdin injection.

    Returns: stdout string (stripped)
    Raises: subprocess.TimeoutExpired if execution exceeds timeout
    Raises: subprocess.CalledProcessError if process crashes (caught by caller)
    """
    ...
```

### Tensor / Data Shapes

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| `completions` | `[B*G]` | list[str] | B=batch_size, G=8 rollouts |
| `metadata` | `[B*G]` | list[dict] | each has `test_cases: list[tuple[str,str]]` |
| `rewards` (return) | `[B*G]` | list[float] | values in [0.0, 1.0] |

### Pseudo-code

```
function fraction_reward_fn(completions, prompts, metadata):
    rewards = []
    for code, meta in zip(completions, metadata):
        test_cases = meta.get("test_cases", [])
        if len(test_cases) == 0:
            rewards.append(0.0)
            continue
        passed = 0
        for (stdin, expected_out) in test_cases:
            try:
                actual_out = _execute_code(code, stdin, timeout=3.0)
                if actual_out.strip() == expected_out.strip():
                    passed += 1
            except (subprocess.TimeoutExpired, Exception):
                pass  # counts as failed test
        rewards.append(passed / len(test_cases))
    return rewards

function _execute_code(code, stdin, timeout):
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        proc = subprocess.run(
            ["python", fname],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.stdout
    finally:
        os.unlink(fname)  # always clean up temp file
```

### Key Implementation Notes

- `delete=False` required: file must persist until subprocess reads it
- `os.unlink` in `finally` block: cleanup even on exception/timeout
- stdout comparison is strip()-normalized: handles trailing newline differences
- Empty test_cases → reward=0.0, not None (TRL expects float)
- Exception catch is broad intentionally: syntax errors, import errors all → 0 for that test

---

## Subtask L-3-1: SFT Training — Ceiling Check + Trainer Setup

**Parent: E-3** (SFT Training, complexity 11)

### API Signatures

```python
# code/train_sft.py

import json
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset

def run_ceiling_check(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    n_problems: int = 20,
    threshold: float = 0.90,
) -> tuple[float, bool]:
    """
    Estimate zero-shot HumanEval pass@1 on n_problems subset.

    Returns: (estimated_pass_rate, should_switch_to_smaller_model)
    If estimated_pass_rate >= threshold: log warning, return True
    """
    ...

def train(
    config: dict,
) -> str:
    """
    Run SFT training on APPS dataset.

    Args:
        config: full experiment config dict (loaded from config.yaml)
    Returns:
        checkpoint_path: str path to saved checkpoint
    Side effects:
        - Dumps config to logs/config_dump.json
        - Saves checkpoint to config["paths"]["sft_checkpoint_dir"]
    """
    ...
```

### Pseudo-code

```
function run_ceiling_check(model, tokenizer, n_problems=20, threshold=0.90):
    # Load HumanEval subset
    he_dataset = load_dataset("openai_humaneval", split="test").select(range(n_problems))
    passed = 0
    for problem in he_dataset:
        prompt = problem["prompt"]
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512).to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=256, do_sample=False)
        code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Run against test (use bigcode-style execution)
        result = _quick_execute(code, problem["test"])
        if result:
            passed += 1
    rate = passed / n_problems
    should_switch = rate >= threshold
    if should_switch:
        log(f"WARNING: Ceiling check {rate:.2f} >= {threshold}. Switch to 1.3B model.")
    return rate, should_switch

function train(config):
    # Dump config
    Path("logs/").mkdir(parents=True, exist_ok=True)
    json.dump(config, open("logs/config_dump.json", "w"), indent=2)

    # Load tokenizer + model
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"], torch_dtype=torch.bfloat16
    )

    # Ceiling check
    rate, should_switch = run_ceiling_check(model, tokenizer)
    if should_switch:
        config["model_name"] = config["fallback_model"]
        model = AutoModelForCausalLM.from_pretrained(config["model_name"], torch_dtype=torch.bfloat16)

    # Load data
    sft_dataset = load_apps_train(tokenizer)["sft"]

    # Training args — matched gradient steps
    steps_per_epoch = len(sft_dataset) // config["training"]["batch_size"]
    total_steps = steps_per_epoch * config["training"]["epochs"]

    training_args = TrainingArguments(
        output_dir=config["paths"]["sft_checkpoint_dir"],
        learning_rate=config["training"]["lr"],
        per_device_train_batch_size=config["training"]["batch_size"],
        gradient_accumulation_steps=config["training"]["grad_accum"],
        num_train_epochs=config["training"]["epochs"],
        lr_scheduler_type="cosine",
        warmup_steps=config["training"]["warmup_steps"],
        max_grad_norm=config["training"]["grad_clip"],
        bf16=True,
        seed=config["training"]["seed"],
        save_strategy="epoch",
        logging_steps=50,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=sft_dataset)
    trainer.train()
    trainer.save_model(config["paths"]["sft_checkpoint_dir"])
    return config["paths"]["sft_checkpoint_dir"]
```

---

## Subtask L-4-1: GRPOTrainer Setup

**Parent: E-4** (RLEF Training, complexity 14)

### API Signatures

```python
# code/train_rlef.py

from trl import GRPOConfig, GRPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer

def build_grpo_config(config: dict) -> GRPOConfig:
    """
    Build GRPOConfig from experiment config dict.
    Returns fully-specified GRPOConfig with all hyperparameters.
    """
    ...

def train(config: dict) -> str:
    """
    Run GRPO training with fraction_reward_fn.

    Args:
        config: full experiment config dict
    Returns:
        checkpoint_path: str
    Side effects:
        - Logs per-step rewards to logs/reward_monitoring.jsonl (via RewardMonitorCallback)
        - Saves checkpoint to config["paths"]["rlef_checkpoint_dir"]
    """
    ...
```

### Pseudo-code

```
function build_grpo_config(config):
    return GRPOConfig(
        model_name_or_path=config["model_name"],
        learning_rate=config["training"]["lr"],
        per_device_train_batch_size=config["training"]["batch_size"],
        gradient_accumulation_steps=config["training"]["grad_accum"],
        num_train_epochs=config["training"]["epochs"],
        max_new_tokens=config["training"]["max_new_tokens"],
        num_generations=config["grpo"]["num_generations"],   # G=8
        beta=config["grpo"]["beta"],                         # KL=0.04
        max_grad_norm=config["training"]["grad_clip"],
        lr_scheduler_type="cosine",
        warmup_steps=config["training"]["warmup_steps"],
        temperature=config["grpo"]["temperature_rollout"],   # 0.8
        seed=config["training"]["seed"],
        output_dir=config["paths"]["rlef_checkpoint_dir"],
        bf16=True,
        save_strategy="epoch",
        logging_steps=50,
    )

function train(config):
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"], torch_dtype=torch.bfloat16
    )
    rlef_dataset = load_apps_train(tokenizer)["rlef"]
    grpo_config = build_grpo_config(config)
    callback = RewardMonitorCallback(log_path="logs/reward_monitoring.jsonl")
    trainer = GRPOTrainer(
        model=model,
        reward_funcs=fraction_reward_fn,
        args=grpo_config,
        train_dataset=rlef_dataset,
        callbacks=[callback],
    )
    trainer.train()
    trainer.save_model(config["paths"]["rlef_checkpoint_dir"])
    return config["paths"]["rlef_checkpoint_dir"]
```

### Tensor Shapes

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| Input tokens | `[B, L]` | int64 | L ≤ 1024 |
| Rollout tokens | `[B*G, max_new_tokens]` | int64 | G=8, max_new_tokens=512 |
| Rewards | `[B*G]` | float32 | fraction in [0,1] |
| KL penalty | scalar | float32 | β=0.04 × KL(π‖π_ref) |

---

## Subtask L-4-2: RewardMonitorCallback

**Parent: E-4** (RLEF Training, complexity 14)

### API Signatures

```python
# code/train_rlef.py (inline class)

import json
from pathlib import Path
from transformers import TrainerCallback, TrainerState, TrainerControl

class RewardMonitorCallback(TrainerCallback):
    """
    Logs per-batch fraction rewards stratified by APPS difficulty to JSONL.
    Required for H-M2 data collection.
    """

    def __init__(self, log_path: str = "logs/reward_monitoring.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def on_step_end(
        self,
        args,                     # TrainingArguments
        state: TrainerState,
        control: TrainerControl,
        rewards: list[float] = None,      # per-sample rewards from GRPOTrainer
        metadata: list[dict] = None,      # per-sample metadata with "difficulty"
        **kwargs,
    ) -> None:
        """
        Called by GRPOTrainer after each gradient step.
        Computes mean reward per difficulty bucket and appends to JSONL.
        """
        ...
```

### Pseudo-code

```
class RewardMonitorCallback:
    def on_step_end(self, args, state, control, rewards=None, metadata=None, **kwargs):
        if rewards is None or metadata is None:
            return
        # Group rewards by difficulty
        buckets = {"intro": [], "interview": [], "competition": []}
        for r, meta in zip(rewards, metadata):
            difficulty = meta.get("difficulty", "interview")
            if difficulty in buckets:
                buckets[difficulty].append(r)
        record = {
            "step": state.global_step,
            "intro_reward": mean(buckets["intro"]) if buckets["intro"] else None,
            "interview_reward": mean(buckets["interview"]) if buckets["interview"] else None,
            "competition_reward": mean(buckets["competition"]) if buckets["competition"] else None,
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
```

### Key Notes

- `rewards` and `metadata` are passed by GRPOTrainer via `**kwargs` — names must match TRL's keyword arguments exactly
- `None` guard: callback called even on non-reward steps; skip silently
- JSONL append mode: safe for resumable training

---

## Subtask L-4-3: Matched Gradient Steps

**Parent: E-4** (RLEF Training, complexity 14)

### API Signatures

```python
# code/train_rlef.py

def compute_gradient_steps(
    dataset_size: int,
    batch_size: int,
    grad_accum: int,
    epochs: int,
) -> int:
    """
    Compute total optimizer steps = floor(dataset_size / (batch_size * grad_accum)) * epochs.
    Used to verify SFT and RLEF have same gradient step count.
    """
    ...

def verify_matched_steps(sft_steps: int, rlef_steps: int) -> None:
    """
    Assert SFT and RLEF gradient steps are equal. Logs warning if not.
    Raises ValueError if difference > 5% (unacceptable divergence).
    """
    ...
```

### Pseudo-code

```
function compute_gradient_steps(dataset_size, batch_size, grad_accum, epochs):
    steps_per_epoch = dataset_size // (batch_size * grad_accum)
    return steps_per_epoch * epochs

function verify_matched_steps(sft_steps, rlef_steps):
    diff = abs(sft_steps - rlef_steps)
    pct = diff / sft_steps
    if pct > 0.05:
        raise ValueError(f"Step mismatch too large: SFT={sft_steps}, RLEF={rlef_steps} ({pct:.1%})")
    if diff > 0:
        log(f"WARNING: Step mismatch {diff} steps ({pct:.1%}) — acceptable for PoC")
```

### Notes

- APPS train size after filter ≈ 4,900–5,000 problems (filter: ≥1 test case)
- With batch=4, grad_accum=8, epochs=3: steps ≈ floor(4900/32) × 3 ≈ 459 steps
- Log actual step count to `logs/config_dump.json` under key `"gradient_steps"`

---

## Subtask L-6-1: Bootstrap CI Implementation

**Parent: E-6** (Analysis & Figures, complexity 11)

### API Signatures

```python
# code/analyze.py

import numpy as np
from typing import TypedDict

class BenchmarkResults(TypedDict):
    humaneval: np.ndarray       # shape [164], binary {0,1} per problem
    mbpp: np.ndarray            # shape [374], binary {0,1}
    lcb_easy: np.ndarray        # shape [~400], binary {0,1}
    lcb_medium: np.ndarray      # shape [~400], binary {0,1}
    lcb_hard: np.ndarray        # shape [~200], binary {0,1}

def compute_deltas(
    rlef_results: BenchmarkResults,
    sft_results: BenchmarkResults,
) -> dict:
    """
    Compute Δ = RLEF - SFT for each benchmark (mean pass@1).
    Returns: {
        "delta_humaneval": float,
        "delta_lcb_medium": float,
        "delta_lcb_hard": float,
        "delta_lcb_medium_hard": float,  # mean of medium+hard
        "delta_ratio": float,            # delta_lcb_medium_hard / delta_humaneval
    }
    """
    ...

def bootstrap_ci(
    rlef_results: BenchmarkResults,
    sft_results: BenchmarkResults,
    n_boot: int = 1000,
    seed: int = 42,
    ci_level: float = 0.95,
    gate_ratio: float = 1.5,
) -> dict:
    """
    Bootstrap confidence interval on delta_ratio.

    Returns: {
        "ci_lo": float,      # lower bound of CI (e.g. 2.5th percentile)
        "ci_hi": float,      # upper bound
        "mean_ratio": float,
        "p_value": float,    # fraction of bootstrap samples where ratio >= gate_ratio
        "gate_pass": bool,   # ci_lo > 1.0 AND mean_ratio >= gate_ratio
        "ratios": np.ndarray # shape [n_boot], all bootstrap ratio samples
    }
    """
    ...
```

### Tensor / Data Shapes

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| per-benchmark results | `[n_problems]` | float32 {0,1} | binary pass/fail |
| bootstrap ratios | `[n_boot]` | float64 | ratio samples |
| CI | `(2,)` | float64 | [lo, hi] |

### Pseudo-code

```
function compute_deltas(rlef_results, sft_results):
    d_he = mean(rlef_results["humaneval"]) - mean(sft_results["humaneval"])
    d_lcb_med = mean(rlef_results["lcb_medium"]) - mean(sft_results["lcb_medium"])
    d_lcb_hard = mean(rlef_results["lcb_hard"]) - mean(sft_results["lcb_hard"])
    d_lcb_med_hard = (d_lcb_med + d_lcb_hard) / 2
    ratio = d_lcb_med_hard / d_he if d_he > 0 else float("nan")
    return {"delta_humaneval": d_he, "delta_lcb_medium": d_lcb_med,
            "delta_lcb_hard": d_lcb_hard, "delta_lcb_medium_hard": d_lcb_med_hard,
            "delta_ratio": ratio}

function bootstrap_ci(rlef_results, sft_results, n_boot=1000, seed=42, ...):
    rng = np.random.default_rng(seed)
    ratios = []
    he_n = len(rlef_results["humaneval"])
    lcb_n = len(rlef_results["lcb_medium"])  # same for lcb_hard (resample independently)

    for _ in range(n_boot):
        # Resample HumanEval
        idx_he = rng.integers(0, he_n, size=he_n)
        d_he_boot = (rlef_results["humaneval"][idx_he].mean()
                     - sft_results["humaneval"][idx_he].mean())

        # Resample LCB medium+hard (independently)
        idx_med = rng.integers(0, len(rlef_results["lcb_medium"]),
                               size=len(rlef_results["lcb_medium"]))
        idx_hard = rng.integers(0, len(rlef_results["lcb_hard"]),
                                size=len(rlef_results["lcb_hard"]))
        d_lcb_boot = (
            (rlef_results["lcb_medium"][idx_med].mean() - sft_results["lcb_medium"][idx_med].mean()
             + rlef_results["lcb_hard"][idx_hard].mean() - sft_results["lcb_hard"][idx_hard].mean())
            / 2
        )
        if d_he_boot > 0:
            ratios.append(d_lcb_boot / d_he_boot)

    ratios = np.array(ratios)
    alpha = (1 - ci_level) / 2
    ci_lo, ci_hi = np.percentile(ratios, [alpha*100, (1-alpha)*100])
    p_val = np.mean(ratios >= gate_ratio)
    return {
        "ci_lo": ci_lo, "ci_hi": ci_hi,
        "mean_ratio": float(ratios.mean()),
        "p_value": float(p_val),
        "gate_pass": bool(ci_lo > 1.0 and ratios.mean() >= gate_ratio),
        "ratios": ratios,
    }
```

---

## Subtask L-6-2: Figure Generation

**Parent: E-6** (Analysis & Figures, complexity 11)

### API Signatures

```python
# code/analyze.py

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def make_figures(
    rlef_results: BenchmarkResults,
    sft_results: BenchmarkResults,
    deltas: dict,
    bootstrap: dict,
    reward_log_path: str = "logs/reward_monitoring.jsonl",
    figures_dir: str = "docs/youra_research/h-e1/figures",
) -> None:
    """
    Generate all 4 required figures and save to figures_dir.
    Figures: gate_metrics.png, difficulty_scaling.png, reward_curve.png, bootstrap_ratio.png
    """
    ...

def print_gate_decision(deltas: dict, bootstrap: dict) -> bool:
    """
    Print PASS/FAIL summary. Returns True if gate condition met.
    Gate: delta_ratio >= 1.5 AND ci_lo > 1.0
    """
    ...
```

### Pseudo-code per Figure

```
# Figure 1: gate_metrics.png (MANDATORY)
benchmarks = ["HumanEval", "MBPP", "LCB-Easy", "LCB-Med", "LCB-Hard"]
delta_values = [delta_humaneval, delta_mbpp, delta_lcb_easy, delta_lcb_medium, delta_lcb_hard]
# compute per-benchmark CI from bootstrap
fig, ax = plt.subplots()
ax.bar(benchmarks, delta_values, yerr=ci_per_benchmark, capsize=5)
ax.axhline(y=gate_threshold_line, color="red", linestyle="--", label="1.5× threshold")
ax.set_ylabel("Δ pass@1 (RLEF-Fraction − SFT)")
fig.savefig(figures_dir / "gate_metrics.png", dpi=150, bbox_inches="tight")

# Figure 2: difficulty_scaling.png
x = [0, 1, 2, 3, 4]  # 5 difficulty levels
sft_vals = [mean(sft["humaneval"]), mean(sft["mbpp"]), mean(sft["lcb_easy"]), ...]
rlef_vals = [mean(rlef["humaneval"]), ...]
ax.plot(x, sft_vals, label="SFT", marker="o")
ax.plot(x, rlef_vals, label="RLEF-Fraction", marker="s")
ax.set_xticks(x); ax.set_xticklabels(benchmarks)
fig.savefig(figures_dir / "difficulty_scaling.png", dpi=150)

# Figure 3: reward_curve.png
# Load logs/reward_monitoring.jsonl line by line
records = [json.loads(line) for line in open(reward_log_path)]
steps = [r["step"] for r in records]
for bucket in ["intro", "interview", "competition"]:
    vals = [r.get(f"{bucket}_reward") for r in records]
    ax.plot(steps, vals, label=bucket)
fig.savefig(figures_dir / "reward_curve.png", dpi=150)

# Figure 4: bootstrap_ratio.png
ax.hist(bootstrap["ratios"], bins=50, density=True)
ax.axvline(x=1.5, color="red", linestyle="--", label="Gate: 1.5×")
ax.axvline(x=bootstrap["ci_lo"], color="orange", linestyle=":", label="95% CI lo")
fig.savefig(figures_dir / "bootstrap_ratio.png", dpi=150)
```
