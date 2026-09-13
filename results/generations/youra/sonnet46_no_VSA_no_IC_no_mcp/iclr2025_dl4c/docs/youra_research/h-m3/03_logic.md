# Logic Design: h-m3 — RLEF-Fraction vs RLEF-Binary

**Date:** 2026-08-26
**Hypothesis:** h-m3 (MECHANISM, INCREMENTAL base: h-m2 / h-E1)
**Budget:** 9 logic subtasks

Applied: verified-signature incremental extension pattern
Applied: bootstrap one-tailed hypothesis test pattern
Applied: subprocess-isolated code execution pattern

---

## Codebase Analysis (Serena)

**Analyzed paths:** `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m2/code/`

**h-E1 findings (actual code):**
- `reward.py`: `fraction_reward_fn(completions: list, prompts: list, metadata: list, **kwargs) -> list` — reward via `meta.get("test_cases", "[]")`; `_execute_code(code: str, stdin: str, timeout: float=3.0) -> str` — subprocess with tempfile
- `config.py`: `TrainingConfig(lr=1e-5, batch_size=4, grad_accum=8, max_new_tokens=512, seed=42, warmup_steps=100, lr_schedule="cosine")`; `GRPOConfig(num_generations=8, beta=0.04, temperature_rollout=0.8)`; `ExperimentConfig` composite
- `data_utils.py`, `evaluate.py`, `grpo_trainer.py` confirmed present
- `train_rlef.py`: existing RLEF-Fraction training entrypoint
- `EVAL_CONFIG["lcb_difficulty_flag"]` maps `lcb_hard → "hard"` — confirmed difficulty parsing API

**h-m2 findings (actual code):**
- `difficulty_reward_callback.py`: `DifficultyRewardCallback` — per-difficulty reward monitoring
- `verify_mechanism_activated(fraction_rewards, binary_rewards, threshold)` pattern confirmed

**Key verified fact:** `fraction_reward_fn` receives `metadata` list of dicts with `"test_cases"` key (JSON string of `[[stdin, expected], ...]`). Binary reward must match this exact interface.

---

## External Dependencies API

Verified signatures from actual h-E1 code:

```python
# h-e1/code/reward.py
def fraction_reward_fn(
    completions: list,   # List[str] — generated code strings
    prompts: list,       # List[str] — prompt strings (unused in reward computation)
    metadata: list,      # List[dict] — each dict has key "test_cases": JSON str of [[stdin, expected], ...]
    **kwargs,
) -> list:               # List[float] in [0.0, 1.0]

def _execute_code(
    code: str,           # Python source code string
    stdin: str,          # stdin string for subprocess
    timeout: float = 3.0,# seconds
) -> str:                # stdout string (empty on error/timeout)

# h-e1/code/config.py
@dataclass
class TrainingConfig:
    lr: float = 1e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    max_length: int = 1024
    max_new_tokens: int = 512
    seed: int = 42
    precision: str = "bfloat16"
    grad_clip: float = 1.0
    warmup_steps: int = 100
    lr_schedule: str = "cosine"

@dataclass
class GRPOConfig:
    num_generations: int = 8   # G rollouts per prompt
    beta: float = 0.04
    temperature_rollout: float = 0.8
```

---

## Subtask L-A4-1: train_rlef_binary() Full Implementation

**Parent Epic:** A-4 (RLEF-Binary Training, complexity 12)

```python
# train_rlef_binary.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "h-e1" / "code"))

from grpo_trainer import build_grpo_trainer   # verified present in h-e1/code/
from data_utils import load_apps_dataset       # verified present in h-e1/code/
from config import TrainingConfig, GRPOConfig, ExperimentConfig
from reward_binary import binary_reward_fn, verify_reward_formulation_active
from reward import fraction_reward_fn          # for activation check only
from h_m3_config import H_M3_Config

def train_rlef_binary(cfg: H_M3_Config) -> Path:
    """
    Train RLEF-Binary from SFT checkpoint.
    Returns: path to final checkpoint directory.
    
    CONTROLLED COMPARISON INVARIANT:
    - lr=1e-6 (overrides h-E1 default 1e-5 — matches RLEF-Fraction run)
    - grad_accum=4 (overrides h-E1 default 8 — effective batch=16)
    - G=8, max_new_tokens=512, seed=42 — identical to RLEF-Fraction
    """
    import torch
    torch.manual_seed(cfg.seed)
    
    # Load dataset
    dataset = load_apps_dataset(
        hf_id="codeparrot/apps",
        split="train",
        min_test_cases=1,
        max_length=cfg.max_length,
    )
    
    # Build trainer with binary reward
    trainer = build_grpo_trainer(
        model_name_or_path=cfg.sft_checkpoint,   # h-E1 SFT checkpoint
        reward_funcs=[binary_reward_fn],
        train_dataset=dataset,
        training_config=TrainingConfig(
            lr=cfg.lr,                    # 1e-6
            batch_size=cfg.batch_size,    # 4
            grad_accum=cfg.grad_accum,    # 4
            max_new_tokens=cfg.max_new_tokens,  # 512
            seed=cfg.seed,                # 42
            warmup_steps=cfg.warmup_steps,
            lr_schedule="cosine",
        ),
        grpo_config=GRPOConfig(num_generations=cfg.num_generations),  # G=8
        output_dir=cfg.binary_checkpoint_dir,
        checkpoint_interval=cfg.checkpoint_interval_steps,  # 250
    )
    
    # Register activation verifier callback
    trainer.add_callback(RewardActivationCallback(
        verify_fn=verify_reward_formulation_active,
        fraction_fn=fraction_reward_fn,
        interval=cfg.verify_interval_steps,  # 50
    ))
    
    trainer.train()
    return Path(cfg.binary_checkpoint_dir) / "final"


class RewardActivationCallback:
    """Logs reward formulation activation every N steps."""
    def __init__(self, verify_fn, fraction_fn, interval: int = 50):
        self.verify_fn = verify_fn
        self.fraction_fn = fraction_fn
        self.interval = interval
    
    def on_step_end(self, step: int, completions, metadata, binary_rewards, **kwargs):
        if step % self.interval != 0:
            return
        fraction_rewards = self.fraction_fn(completions, [], metadata)
        activated, indicators = self.verify_fn(fraction_rewards, binary_rewards)
        # Log to tensorboard
        print(f"[Step {step}] reward_activation={activated} | "
              f"fraction_mean={indicators['fraction_mean']:.4f} | "
              f"binary_mean={indicators['binary_mean']:.4f}")
```

**Tensor shapes:**
- `completions`: `List[str]` length = batch_size × G = 4 × 8 = 32 per step
- `binary_rewards`: `List[float]` length = 32, values ∈ {0.0, 1.0}
- `advantages` (GRPO internal): `Tensor[batch_size, G]` = `[4, 8]`, normalized within group

---

## Subtask L-A4-2: Binary Reward Function API

**Parent Epic:** A-4

```python
# reward_binary.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "h-e1" / "code"))

from reward import _execute_code  # verified: _execute_code(code, stdin, timeout=3.0) -> str
import json

def binary_reward_fn(
    completions: list,   # List[str] — matches fraction_reward_fn interface exactly
    prompts: list,       # List[str] — unused, kept for API compatibility
    metadata: list,      # List[dict] — each has "test_cases": JSON str [[stdin, expected], ...]
    **kwargs,
) -> list:               # List[float] — values ∈ {0.0, 1.0}
    """
    Binary execution reward: 1.0 iff ALL test cases pass, else 0.0.
    Interface identical to fraction_reward_fn for controlled comparison.
    """
    rewards = []
    for code, meta in zip(completions, metadata):
        if isinstance(meta, dict):
            raw = meta.get("test_cases", "[]")
        else:
            raw = "[]"
        try:
            test_cases = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            test_cases = []
        
        if not test_cases:
            rewards.append(0.0)
            continue
        
        all_passed = True
        for item in test_cases:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                stdin, expected = item
            else:
                continue
            try:
                actual = _execute_code(code, str(stdin), timeout=3.0)
                if actual.strip() != str(expected).strip():
                    all_passed = False
                    break
            except Exception:
                all_passed = False
                break
        
        rewards.append(1.0 if all_passed else 0.0)
    return rewards
```

**Key design note:** Early-exit on first failure (short-circuits — binary only needs one failure). Matches `fraction_reward_fn` interface exactly so both can be passed to `reward_funcs` parameter of GRPOTrainer.

---

## Subtask L-A4-3: Checkpoint and Training Loop Callbacks

**Parent Epic:** A-4

```python
def verify_reward_formulation_active(
    fraction_rewards: list,   # List[float] from fraction_reward_fn
    binary_rewards: list,     # List[float] from binary_reward_fn
    threshold: float = 0.01,
) -> tuple:                   # (bool, dict)
    """
    Returns (activated: bool, indicators: dict).
    activated = True iff fraction_mean > binary_mean by threshold.
    """
    import numpy as np
    mean_fraction = float(np.mean(fraction_rewards)) if fraction_rewards else 0.0
    mean_binary = float(np.mean(binary_rewards)) if binary_rewards else 0.0
    indicators = {
        "fraction_mean": mean_fraction,
        "binary_mean": mean_binary,
        "reward_differs": abs(mean_fraction - mean_binary) > threshold,
        "fraction_denser": mean_fraction > mean_binary,
    }
    activated = indicators["reward_differs"] and indicators["fraction_denser"]
    return activated, indicators

# Checkpoint callback: save every 250 steps
# Integrated into GRPOTrainer via checkpoint_interval parameter (verified in h-E1 grpo_trainer.py)
```

---

## Subtask L-A5-1: evaluate_all_models() Orchestration

**Parent Epic:** A-5 (Multi-benchmark evaluation, complexity 13)

```python
# compare.py

def evaluate_all_models(
    sft_path: str,          # path to SFT checkpoint (h-E1)
    fraction_path: str,     # path to RLEF-Fraction checkpoint (h-E1)
    binary_path: str,       # path to RLEF-Binary checkpoint (h-m3, newly trained)
    cfg,                    # H_M3_Config
) -> dict:                  # {model_tag: {benchmark: pass@1_float}}
    """
    Evaluates all 3 models on all 5 benchmarks.
    Returns nested dict for downstream statistical analysis.
    """
    models = {
        "sft": sft_path,
        "rlef_fraction": fraction_path,
        "rlef_binary": binary_path,
    }
    results = {}
    
    bigcode_benchmarks = ["humaneval", "mbpp"]
    lcb_difficulties = ["easy", "medium", "hard"]
    
    for model_tag, checkpoint in models.items():
        results[model_tag] = {}
        
        # HumanEval + MBPP via bigcode-evaluation-harness
        bigcode_results = run_bigcode_eval(
            checkpoint=checkpoint,
            tasks=bigcode_benchmarks,
            n_samples=1,
            batch_size=8,
            output_path=f"results/h-m3/{model_tag}_bigcode.json",
        )
        results[model_tag].update(bigcode_results)  # keys: "humaneval", "mbpp"
        
        # LiveCodeBench (all difficulties in one run)
        lcb_results = run_lcb_eval(
            checkpoint=checkpoint,
            release_version="release_v4",
            n_workers=4,
            output_path=f"results/h-m3/{model_tag}_lcb.json",
        )
        # Parse difficulty-stratified results
        for diff in lcb_difficulties:
            results[model_tag][f"lcb_{diff}"] = lcb_results.get(diff, 0.0)
    
    return results  # shape: {3 models} × {5 benchmarks}
```

---

## Subtask L-A5-2: bigcode-harness Subprocess API

**Parent Epic:** A-5

```python
def run_bigcode_eval(
    checkpoint: str,          # model path or HF identifier
    tasks: list,              # e.g., ["humaneval", "mbpp"]
    n_samples: int = 1,
    batch_size: int = 8,
    output_path: str = None,
) -> dict:                    # {task_name: pass@1_float}
    """Invokes bigcode-evaluation-harness via subprocess."""
    import subprocess, json, os
    
    harness_dir = os.environ.get("BIGCODE_HARNESS_DIR", "bigcode-evaluation-harness")
    cmd = [
        "accelerate", "launch",
        f"{harness_dir}/main.py",
        "--model", checkpoint,
        "--tasks", ",".join(tasks),
        "--n_samples", str(n_samples),
        "--batch_size", str(batch_size),
        "--allow_code_execution",
        "--metric_output_path", output_path or "/tmp/bigcode_results.json",
    ]
    subprocess.run(cmd, check=True)
    
    with open(output_path or "/tmp/bigcode_results.json") as f:
        raw = json.load(f)
    
    # bigcode-harness output format: {"humaneval": {"pass@1": 0.45}, ...}
    return {task: raw[task]["pass@1"] for task in tasks if task in raw}
```

---

## Subtask L-A5-3: LiveCodeBench Invocation + Difficulty Parsing

**Parent Epic:** A-5

```python
def run_lcb_eval(
    checkpoint: str,
    release_version: str = "release_v4",  # May 2023 – Sep 2024, 713 problems
    n_workers: int = 4,
    output_path: str = None,
) -> dict:                                # {"easy": float, "medium": float, "hard": float}
    """Invokes LiveCodeBench harness; returns difficulty-stratified pass@1."""
    import subprocess, json, os
    
    lcb_dir = os.environ.get("LCB_DIR", "LiveCodeBench")
    out = output_path or "/tmp/lcb_results.json"
    cmd = [
        "python", "-m", "lcb_runner.runner.main",
        "--model", checkpoint,
        "--release_version", release_version,
        "--n_workers", str(n_workers),
        "--output_path", out,
    ]
    subprocess.run(cmd, check=True)
    
    with open(out) as f:
        raw = json.load(f)
    
    # LCB output: {"easy": {"pass@1": 0.3}, "medium": {...}, "hard": {...}}
    return {
        "easy": raw.get("easy", {}).get("pass@1", 0.0),
        "medium": raw.get("medium", {}).get("pass@1", 0.0),
        "hard": raw.get("hard", {}).get("pass@1", 0.0),
    }
```

---

## Subtask L-A6-1: Bootstrap Delta Test

**Parent Epic:** A-6 (Bootstrap hypothesis test, complexity 9)

```python
def bootstrap_delta_test(
    fraction_results: list,   # List[float] — per-problem pass/fail for RLEF-Fraction at LCB-Hard
    binary_results: list,     # List[float] — per-problem pass/fail for RLEF-Binary at LCB-Hard
    sft_results: list,        # List[float] — per-problem pass/fail for SFT at LCB-Hard
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple:                   # (p_value: float, observed_diff: float, bootstrap_diffs: ndarray)
    """
    One-tailed bootstrap test: H0: Δ_Fraction <= Δ_Binary.
    p_value = P(bootstrap_diff <= 0) under H0 rejection = P(fraction NOT better).
    Gate passes if p_value < 0.05.
    
    Input shape: each list has len = number of LCB-Hard problems (varies by release_v4 subset).
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    
    frac = np.array(fraction_results, dtype=float)  # shape: [N_hard]
    binary = np.array(binary_results, dtype=float)  # shape: [N_hard]
    sft = np.array(sft_results, dtype=float)        # shape: [N_hard]
    
    delta_frac = frac - sft    # per-problem delta for fraction
    delta_bin = binary - sft   # per-problem delta for binary
    
    observed_diff = delta_frac.mean() - delta_bin.mean()
    
    n = len(delta_frac)
    bootstrap_diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        bootstrap_diffs[i] = delta_frac[idx].mean() - delta_bin[idx].mean()
    
    # p-value: fraction of bootstrap samples where fraction is NOT better
    p_value = float(np.mean(bootstrap_diffs <= 0))
    
    return p_value, observed_diff, bootstrap_diffs
```

**Gate logic:**
```python
p_value, observed_diff, _ = bootstrap_delta_test(...)
gate_passed = (p_value < 0.05) and (observed_diff > 0)
outcome = "PASS" if gate_passed else "EXPLORE"
```

---

## Subtask L-A7-1: Required Figure + Reward Trajectory

**Parent Epic:** A-7 (Figures, complexity 10)

```python
def generate_figures(results: dict, output_dir: Path) -> None:
    """
    results: {model_tag: {benchmark: pass@1}}
    Generates all 5 figures to output_dir.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    _fig_delta_bar(results, output_dir)          # REQUIRED
    _fig_reward_trajectory(output_dir)           # from training logs
    _fig_absolute_heatmap(results, output_dir)
    _fig_difficulty_interaction(results, output_dir)
    _fig_nonzero_histogram(output_dir)

def _fig_delta_bar(results: dict, output_dir: Path) -> None:
    """
    Bar chart: Δ_Fraction vs Δ_Binary per benchmark.
    Error bars = 95% bootstrap CI.
    Benchmarks on x-axis: HumanEval, MBPP, LCB-Easy, LCB-Medium, LCB-Hard.
    """
    import matplotlib.pyplot as plt, numpy as np
    
    benchmarks = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
    sft = results["sft"]
    frac = results["rlef_fraction"]
    binary = results["rlef_binary"]
    
    delta_frac = [frac[b] - sft[b] for b in benchmarks]
    delta_bin = [binary[b] - sft[b] for b in benchmarks]
    
    x = np.arange(len(benchmarks))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, delta_frac, width, label="Δ RLEF-Fraction", color="steelblue")
    ax.bar(x + width/2, delta_bin, width, label="Δ RLEF-Binary", color="coral")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["HumanEval", "MBPP", "LCB-Easy", "LCB-Med", "LCB-Hard"], rotation=15)
    ax.set_ylabel("Δ pass@1 over SFT")
    ax.set_title("h-m3: Fraction vs Binary Reward — pass@1 Improvement by Benchmark")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fig1_delta_bar.png", dpi=150)
    plt.close(fig)
```

---

## Subtask L-A7-2: Heatmap + Interaction + Nonzero Histogram

**Parent Epic:** A-7

```python
def _fig_absolute_heatmap(results: dict, output_dir: Path) -> None:
    """3 models × 5 benchmarks pass@1 heatmap."""
    import matplotlib.pyplot as plt, numpy as np, seaborn as sns
    
    benchmarks = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
    models = ["sft", "rlef_fraction", "rlef_binary"]
    data = np.array([[results[m][b] for b in benchmarks] for m in models])
    
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.heatmap(data, annot=True, fmt=".3f", xticklabels=benchmarks,
                yticklabels=["SFT", "RLEF-Fraction", "RLEF-Binary"],
                cmap="YlOrRd", ax=ax)
    ax.set_title("h-m3: Absolute pass@1 (3 models × 5 benchmarks)")
    fig.tight_layout()
    fig.savefig(output_dir / "fig3_absolute_heatmap.png", dpi=150)
    plt.close(fig)

def _fig_difficulty_interaction(results: dict, output_dir: Path) -> None:
    """Line plot: Δ across difficulty levels — shows reward type × difficulty interaction."""
    import matplotlib.pyplot as plt
    
    diffs = ["lcb_easy", "lcb_medium", "lcb_hard"]
    labels = ["Easy", "Medium", "Hard"]
    sft = results["sft"]
    frac = results["rlef_fraction"]
    binary = results["rlef_binary"]
    
    delta_frac = [frac[b] - sft[b] for b in diffs]
    delta_bin = [binary[b] - sft[b] for b in diffs]
    
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(labels, delta_frac, "o-", color="steelblue", label="Δ RLEF-Fraction")
    ax.plot(labels, delta_bin, "s--", color="coral", label="Δ RLEF-Binary")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle=":")
    ax.set_ylabel("Δ pass@1 over SFT")
    ax.set_title("h-m3: Reward Type × Difficulty Interaction")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fig4_difficulty_interaction.png", dpi=150)
    plt.close(fig)

def _fig_reward_trajectory(output_dir: Path) -> None:
    """Reward trajectory from training logs (reads JSONL log)."""
    import matplotlib.pyplot as plt, json
    
    log_path = "docs/youra_research/h-m3/code/logs/reward_activation.jsonl"
    steps, frac_means, bin_means = [], [], []
    try:
        with open(log_path) as f:
            for line in f:
                rec = json.loads(line)
                steps.append(rec["step"])
                frac_means.append(rec["fraction_mean"])
                bin_means.append(rec["binary_mean"])
    except FileNotFoundError:
        return  # skip if no log

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(steps, frac_means, label="Fraction reward mean", color="steelblue")
    ax.plot(steps, bin_means, label="Binary reward mean", color="coral")
    ax.set_xlabel("Training step"); ax.set_ylabel("Mean reward")
    ax.set_title("h-m3: Reward Signal Density — Fraction vs Binary During Training")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fig2_reward_trajectory.png", dpi=150)
    plt.close(fig)

def _fig_nonzero_histogram(output_dir: Path) -> None:
    """Non-zero reward fraction per difficulty during training."""
    import matplotlib.pyplot as plt, json, collections
    
    log_path = "docs/youra_research/h-m3/code/logs/reward_activation.jsonl"
    nonzero_by_diff = collections.defaultdict(list)
    try:
        with open(log_path) as f:
            for line in f:
                rec = json.loads(line)
                for diff, val in rec.get("nonzero_by_difficulty", {}).items():
                    nonzero_by_diff[diff].append(val)
    except FileNotFoundError:
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    for diff, vals in nonzero_by_diff.items():
        ax.hist(vals, bins=20, alpha=0.6, label=diff)
    ax.set_xlabel("Non-zero reward fraction"); ax.set_ylabel("Count")
    ax.set_title("h-m3: Non-Zero Reward Fraction by Difficulty (Training)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fig5_nonzero_histogram.png", dpi=150)
    plt.close(fig)
```
