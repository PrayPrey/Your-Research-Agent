---
hypothesis_id: h-m4
type: MECHANISM
phase: 3_logic
generated_at: 2026-08-21
author: yoon303@etri.re.kr
base_hypothesis: h-m2
---

# Logic: H-M4 — EvalPlus Checkpoint Evaluation

Applied: checkpoint-evaluation-loop pattern
Applied: resume-safe subprocess runner pattern
Applied: conditional-fallback training pattern

---

## Codebase Analysis (Serena)

**Analyzed**: `docs/youra_research/h-m2/code/`

Key findings from actual H-M2 code:
- `build_grpo_config()` in `train.py:26` hardcodes `save_strategy="no"` — fallback training MUST build GRPOConfig inline with `save_strategy="steps"` and `save_steps=10`
- `run_grpo(cfg, dataset, output_dir, condition) -> list` at `train.py:45` returns `trainer.state.log_history`
- `H_M2Config` at `config.py:6`: fields `model_id`, `learning_rate=5e-7`, `num_generations=4`, `generation_batch_size=4`, `max_steps=50`, `beta=0.0`, `logging_steps=1`, `use_vllm=False`, `save_steps=[10,20,50]`, `exec_timeout=5.0`
- `make_execution_reward(timeout: float)` at `reward.py` — returns TRL-compatible reward function
- `build_mbpp_dataset(cfg, condition) -> Dataset` at `dataset.py` — builds filtered MBPP dataset

---

## External Dependencies API

**Verified from actual H-M2 code** (`docs/youra_research/h-m2/code/`):

```python
# train.py:45
def run_grpo(
    cfg: H_M2Config,
    dataset: Dataset,          # HuggingFace Dataset with 'text', 'task_id', 'test_list' fields
    output_dir: str,           # e.g. "docs/youra_research/h-m2/results/variance50/"
    condition: str,            # e.g. "variance50"
) -> list:                     # trainer.state.log_history (list of dicts)

# train.py:26 — DO NOT USE in fallback training (save_strategy="no" hardcoded)
def build_grpo_config(cfg: H_M2Config, output_dir: str, condition: str) -> GRPOConfig:
    # Returns GRPOConfig with save_strategy="no" — NOT suitable for H-M4 fallback

# reward.py
def make_execution_reward(timeout: float = 5.0) -> Callable:
    # Returns TRL-compatible reward function: f(completions, test_list, **kwargs) -> list[float]

# dataset.py
def build_mbpp_dataset(cfg: H_M2Config, condition: str) -> Dataset:
    # condition: "variance50" | "random50" | "full374"
    # Returns filtered MBPP Dataset

# config.py:6
@dataclass
class H_M2Config:
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    learning_rate: float = 5e-7
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50
    beta: float = 0.0
    logging_steps: int = 1
    use_vllm: bool = False
    save_steps: List[int] = [10, 20, 50]
    exec_timeout: float = 5.0
    results_dir: str = "docs/youra_research/h-m2/results"
```

---

## Subtask Implementations

### A-9 Subtask 1: sys.path Injection + GRPOConfig Construction

**Purpose:** Load H-M2 modules without copying; build GRPOConfig with checkpoint saving enabled.

```python
# evaluate.py — run_fallback_training()

import sys
import os
from pathlib import Path

def run_fallback_training(cfg: "H_M4Config", missing: dict) -> None:
    """
    Injects H-M2 code into sys.path, imports its modules,
    and runs GRPO with save_strategy='steps' for missing conditions.

    Args:
        cfg: H_M4Config instance
        missing: dict[condition: str, missing_steps: list[str]]
                 from verify_checkpoints() — only conditions with missing checkpoints
    """
    # Step 1: sys.path injection
    h_m2_code = str(Path(cfg.h_m2_code_dir).resolve())
    if h_m2_code not in sys.path:
        sys.path.insert(0, h_m2_code)

    # Step 2: Import H-M2 modules (after path injection)
    from config import H_M2Config          # h-m2/code/config.py:6
    from dataset import build_mbpp_dataset  # h-m2/code/dataset.py
    from reward import make_execution_reward # h-m2/code/reward.py
    from trl import GRPOConfig, GRPOTrainer
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    h_m2_cfg = H_M2Config()
    reward_fn = make_execution_reward(timeout=h_m2_cfg.exec_timeout)

    for condition, missing_steps in missing.items():
        if not missing_steps:
            continue

        output_dir = f"{cfg.h_m2_results_dir}/{condition}"
        dataset = build_mbpp_dataset(h_m2_cfg, condition)

        # Step 3: Build GRPOConfig inline (NOT via build_grpo_config — that hardcodes save_strategy="no")
        grpo_cfg = GRPOConfig(
            output_dir=output_dir,
            num_generations=h_m2_cfg.num_generations,           # 4
            generation_batch_size=h_m2_cfg.generation_batch_size, # 4
            max_steps=h_m2_cfg.max_steps,                       # 50
            learning_rate=h_m2_cfg.learning_rate,               # 5e-7
            beta=h_m2_cfg.beta,                                 # 0.0
            logging_steps=h_m2_cfg.logging_steps,               # 1
            save_strategy="steps",   # OVERRIDE: saves checkpoints
            save_steps=10,           # saves at 10, 20, 30, 40, 50
            use_vllm=h_m2_cfg.use_vllm,                         # False
            seed=h_m2_cfg.seed,                                  # 42
            max_completion_length=h_m2_cfg.max_new_tokens,       # 512
            per_device_train_batch_size=1,
            report_to="none",
        )

        # Step 4: Load model and train
        model = AutoModelForCausalLM.from_pretrained(
            h_m2_cfg.model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(h_m2_cfg.model_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        trainer = GRPOTrainer(
            model=model,
            args=grpo_cfg,
            train_dataset=dataset,
            reward_funcs=[reward_fn],
            processing_class=tokenizer,
        )
        trainer.train()
        print(f"[H-M4 fallback] {condition} training complete. Checkpoints in {output_dir}")
```

### A-9 Subtask 2: Conditional Training Loop for Missing Conditions

```python
def verify_checkpoints(cfg: "H_M4Config") -> dict:
    """
    Check which checkpoints exist for all (condition, step) pairs.
    step_0 always OK (HuggingFace Hub model, no local file needed).

    Returns:
        dict[condition: str, list[str]]: missing steps per condition
        e.g. {"variance50": ["step_10", "step_50"], "random50": []}
    """
    missing = {}
    for condition in cfg.conditions:
        missing[condition] = []
        for step in cfg.steps:  # ["step_10", "step_20", "step_50"]
            ckpt_path = cfg.checkpoint_path(condition, step)
            # checkpoint_path returns "docs/youra_research/h-m2/results/{condition}/checkpoint-{N}"
            if not Path(ckpt_path).exists():
                missing[condition].append(step)
    return missing

# Orchestrator usage:
missing = verify_checkpoints(cfg)
needs_training = {c: s for c, s in missing.items() if s}
if needs_training:
    print(f"[H-M4] Missing checkpoints: {needs_training}. Running fallback training.")
    run_fallback_training(cfg, needs_training)
else:
    print("[H-M4] All H-M2 checkpoints present. Skipping training.")
```

---

### A-8 Subtask 3: Fig 1 — Improvement Bar Chart with Threshold Lines

```python
# visualize.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_improvement_bar(results: dict, cfg: "H_M4Config") -> str:
    """
    Fig 1 (mandatory): Bar chart — pass@1 improvement (pp) at step 50 for all 3 conditions.
    Horizontal threshold lines at p1_improvement_pp (2pp) and p1_gap_pp (1pp).

    Args:
        results: gate_results dict from compute_metrics() — has 'improvement' key
        cfg: H_M4Config

    Returns:
        str: saved figure path
    """
    conditions = cfg.conditions  # ["variance50", "random50", "full374"]
    labels = ["Variance-50", "Random-50", "Full-374"]
    colors = ["#2196F3", "#FF9800", "#4CAF50"]

    improvements_pp = [
        results["improvement"].get(c, {}).get("step_50", 0.0) * 100
        for c in conditions
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, improvements_pp, color=colors, alpha=0.85, edgecolor="black")

    # Threshold lines
    ax.axhline(cfg.p1_improvement_pp * 100, color="red", linestyle="--",
               linewidth=1.5, label=f"P1 threshold: {cfg.p1_improvement_pp*100:.0f}pp")
    ax.axhline(cfg.p1_gap_pp * 100, color="orange", linestyle=":",
               linewidth=1.5, label=f"Gap threshold: {cfg.p1_gap_pp*100:.0f}pp")
    ax.axhline(0, color="black", linewidth=0.8)

    # Value labels on bars
    for bar, val in zip(bars, improvements_pp):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{val:.2f}pp", ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("pass@1 Improvement (pp) at Step 50")
    ax.set_title("H-M4: HumanEval+ pass@1 Improvement Over Frozen Baseline")
    ax.legend(loc="upper right")
    ax.set_ylim(bottom=min(min(improvements_pp) - 1, -0.5))

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.figures_dir}/fig1_improvement_bar.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
```

### A-8 Subtask 4: Fig 2/3/4 — Learning Curves, Heatmap, Mechanistic Scatter

```python
def plot_learning_curves(results: dict, cfg: "H_M4Config") -> str:
    """
    Fig 2: Line plot — pass@1 improvement trajectory at steps 10, 20, 50 for all conditions.
    """
    step_labels = [10, 20, 50]
    step_keys = ["step_10", "step_20", "step_50"]
    colors = {"variance50": "#2196F3", "random50": "#FF9800", "full374": "#4CAF50"}
    labels = {"variance50": "Variance-50", "random50": "Random-50", "full374": "Full-374"}

    fig, ax = plt.subplots(figsize=(8, 5))
    for cond in cfg.conditions:
        vals = [results["improvement"].get(cond, {}).get(s, 0.0) * 100 for s in step_keys]
        ax.plot(step_labels, vals, marker="o", color=colors[cond], label=labels[cond])

    ax.axhline(cfg.p1_improvement_pp * 100, color="red", linestyle="--",
               linewidth=1.2, label="P1 threshold (2pp)")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("pass@1 Improvement (pp)")
    ax.set_title("H-M4: Learning Curve — pass@1 Improvement Trajectory")
    ax.legend()

    out = f"{cfg.figures_dir}/fig2_learning_curves.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_pass_at_1_heatmap(results: dict, cfg: "H_M4Config") -> str:
    """
    Fig 3: Heatmap — absolute pass@1 at (condition × step), 3 conditions × 4 steps.
    """
    import numpy as np

    step_keys = ["step_0", "step_10", "step_20", "step_50"]
    step_labels = ["Step 0\n(baseline)", "Step 10", "Step 20", "Step 50"]
    cond_labels = ["Variance-50", "Random-50", "Full-374"]

    data = np.array([
        [results["pass_at_1"].get(c, {}).get(s, 0.0) * 100 for s in step_keys]
        for c in cfg.conditions
    ])

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(data, cmap="YlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(step_labels)))
    ax.set_xticklabels(step_labels)
    ax.set_yticks(range(len(cond_labels)))
    ax.set_yticklabels(cond_labels)

    for i in range(len(cond_labels)):
        for j in range(len(step_labels)):
            ax.text(j, i, f"{data[i,j]:.1f}%", ha="center", va="center", fontsize=9)

    plt.colorbar(im, ax=ax, label="pass@1 (%)")
    ax.set_title("H-M4: HumanEval+ pass@1 by Condition and Training Step")

    out = f"{cfg.figures_dir}/fig3_heatmap.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_mechanistic_scatter(results: dict, cfg: "H_M4Config") -> str:
    """
    Fig 4: Scatter — mean frac_reward_zero_std (from H-M2 gate_results.json)
    vs pass@1 improvement per condition at step 50.
    Tests mechanistic-capability correlation.
    """
    import json

    h_m2_gate = f"{cfg.h_m2_results_dir}/gate_results.json"
    try:
        with open(h_m2_gate) as f:
            h_m2_data = json.load(f)
        frac_zero_std = h_m2_data.get("mean_frac_zero_std", {})
    except FileNotFoundError:
        print("[H-M4] H-M2 gate_results.json not found; skipping Fig 4.")
        return ""

    colors = {"variance50": "#2196F3", "random50": "#FF9800", "full374": "#4CAF50"}
    labels = {"variance50": "Variance-50", "random50": "Random-50", "full374": "Full-374"}

    fig, ax = plt.subplots(figsize=(6, 5))
    for cond in ["variance50", "random50"]:  # full374 may not have frac data
        x = frac_zero_std.get(cond, {}).get("at_50", None)
        y = results["improvement"].get(cond, {}).get("step_50", None)
        if x is not None and y is not None:
            ax.scatter([x], [y * 100], color=colors[cond], s=120,
                       label=labels[cond], zorder=5)
            ax.annotate(labels[cond], (x, y * 100), textcoords="offset points",
                        xytext=(5, 5), fontsize=9)

    ax.set_xlabel("Mean frac_reward_zero_std at Step 50 (H-M2)")
    ax.set_ylabel("pass@1 Improvement at Step 50 (pp)")
    ax.set_title("H-M4: Gradient Concentration vs Capability Transfer")
    ax.legend()

    out = f"{cfg.figures_dir}/fig4_scatter.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_all_figures(results: dict, cfg: "H_M4Config") -> list:
    """Generates all 4 figures. Returns list of saved paths."""
    paths = []
    paths.append(plot_improvement_bar(results, cfg))
    paths.append(plot_learning_curves(results, cfg))
    paths.append(plot_pass_at_1_heatmap(results, cfg))
    scatter_path = plot_mechanistic_scatter(results, cfg)
    if scatter_path:
        paths.append(scatter_path)
    return paths
```

---

### A-7 Subtask 5: Improvement/Gap Computation + P1 Gate

```python
# metrics.py

def compute_metrics(pass_at_1: dict, cfg: "H_M4Config") -> dict:
    """
    Computes all H-M4 gate metrics from pass@1 evaluation results.

    Args:
        pass_at_1: dict[condition: str, dict[step: str, float]]
                   e.g. {"variance50": {"step_0": 0.732, "step_10": 0.739, ...}}
        cfg: H_M4Config

    Returns:
        gate_results dict matching FR-9 JSON schema
    """
    # Frozen baseline: step_0 is same model for all conditions — use variance50 value
    baseline = pass_at_1["variance50"]["step_0"]

    improvement = {}
    for cond in cfg.conditions:
        improvement[cond] = {}
        for step in cfg.steps:  # step_10, step_20, step_50
            improvement[cond][step] = pass_at_1[cond][step] - baseline

    # P1 primary gate at step 50
    improvement_variance50_50 = improvement["variance50"]["step_50"]
    improvement_random50_50   = improvement["random50"]["step_50"]
    gap_vs_random50 = improvement_variance50_50 - improvement_random50_50

    p1_pass = (
        improvement_variance50_50 >= cfg.p1_improvement_pp and
        gap_vs_random50 >= cfg.p1_gap_pp
    )

    return {
        "gate_passed": p1_pass,
        "p1_pass": p1_pass,
        "p3_pass": None,  # computed in Subtask 6
        "baseline_pass_at_1": baseline,
        "pass_at_1": pass_at_1,
        "improvement": improvement,
        "gap_vs_random50_at_50": gap_vs_random50,
        "efficiency_ratio": None,  # computed in Subtask 6
        "thresholds": {
            "p1_improvement_pp": cfg.p1_improvement_pp * 100,
            "p1_gap_pp": cfg.p1_gap_pp * 100,
            "p3_efficiency": cfg.p3_efficiency,
        },
        "n_samples_per_problem": cfg.n_samples,
        "n_problems": 164,
        "dataset": "humaneval_plus",
    }
```

### A-7 Subtask 6: P3 Conditional + gate_results.json

```python
def finalize_p3(results: dict, cfg: "H_M4Config") -> dict:
    """
    Compute P3 efficiency ratio if both variance50 and full374 achieve >= p1_improvement_pp.
    Updates results dict in-place.
    """
    improvement_variance50 = results["improvement"]["variance50"]["step_50"]
    improvement_full374    = results["improvement"].get("full374", {}).get("step_50", None)

    if improvement_full374 is not None:
        if improvement_variance50 >= cfg.p1_improvement_pp and improvement_full374 >= cfg.p1_improvement_pp:
            if improvement_full374 > 0:
                efficiency_ratio = improvement_variance50 / improvement_full374
                results["efficiency_ratio"] = efficiency_ratio
                results["p3_pass"] = efficiency_ratio >= cfg.p3_efficiency
            else:
                results["efficiency_ratio"] = None
                results["p3_pass"] = None  # full374 = 0 improvement → undefined
        else:
            results["p3_pass"] = None  # P3 condition not met
    return results


def save_gate_results(results: dict, cfg: "H_M4Config") -> None:
    """Write gate_results.json to cfg.results_dir."""
    import json
    from pathlib import Path
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.results_dir}/gate_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[H-M4] gate_results.json saved to {out}")


def print_gate_summary(results: dict) -> None:
    """FR-8 asserts + human-readable summary."""
    baseline = results["baseline_pass_at_1"]
    imp_var  = results["improvement"]["variance50"]["step_50"]
    gap      = results["gap_vs_random50_at_50"]
    p1       = results["p1_pass"]

    # FR-8 asserts
    for cond in results["pass_at_1"]:
        for step, val in results["pass_at_1"][cond].items():
            assert val is not None, f"Missing eval: {cond}/{step}"
            assert 0.0 <= val <= 1.0, f"Invalid pass@1 {val}: {cond}/{step}"

    print(f"[H-M4] baseline pass@1 = {baseline:.4f} ({baseline*100:.2f}%)")
    print(f"[H-M4] improvement_variance50 at step50 = {imp_var*100:.2f}pp")
    print(f"[H-M4] gap_vs_random50 at step50 = {gap*100:.2f}pp")
    print(f"[H-M4] P1 gate: {'PASS' if p1 else 'FAIL'}")
    if results.get("p3_pass") is not None:
        print(f"[H-M4] P3 efficiency_ratio = {results['efficiency_ratio']:.3f} "
              f"({'PASS' if results['p3_pass'] else 'FAIL'})")
```

---

### A-4 Subtask 7: EvalPlus Subprocess CLI Invocation

```python
# evaluate.py

import subprocess
from pathlib import Path

def generate_samples(
    checkpoint_path: str,
    condition: str,
    step: str,
    cfg: "H_M4Config",
) -> str:
    """
    Run evalplus.codegen for one (condition, step) checkpoint.
    Generates k=8 samples per HumanEval+ problem (164 problems).

    Args:
        checkpoint_path: HuggingFace model ID or local checkpoint directory
        condition: "variance50" | "random50" | "full374"
        step: "step_0" | "step_10" | "step_20" | "step_50"
        cfg: H_M4Config

    Returns:
        str: output_dir where samples.jsonl was written
    """
    output_dir = f"{cfg.eval_output_root}/{condition}/{step}"

    # Subtask 8 resume check (inline)
    samples_path = Path(output_dir) / "samples.jsonl"
    if samples_path.exists():
        print(f"[H-M4] Skipping generation (resume): {condition}/{step}")
        return output_dir

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "-m", "evalplus.codegen",
        "--model", checkpoint_path,
        "--dataset", cfg.dataset,           # "humaneval"
        "--backend", cfg.backend,           # "hf"
        "--n_samples", str(cfg.n_samples),  # 8
        "--temperature", str(cfg.temperature),  # 0.8
        "--root", output_dir,
    ]
    print(f"[H-M4] Generating samples: {condition}/{step} → {output_dir}")
    subprocess.run(cmd, check=True)
    return output_dir


def evaluate_samples(output_dir: str, cfg: "H_M4Config") -> float:
    """
    Run evalplus.evaluate on generated samples.jsonl.
    Parses pass@1 from stdout.

    Args:
        output_dir: directory containing samples.jsonl (from generate_samples)
        cfg: H_M4Config (for dataset name)

    Returns:
        float: pass@1 on humaneval_plus (0.0–1.0)
    """
    samples_path = f"{output_dir}/samples.jsonl"
    cmd = [
        "python", "-m", "evalplus.evaluate",
        "--dataset", cfg.dataset,
        "--samples", samples_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return parse_pass_at_1(result.stdout)


def parse_pass_at_1(stdout: str) -> float:
    """
    Parse evalplus.evaluate stdout for humaneval_plus pass@1.
    Expected line: "humaneval_plus pass@1: 0.7317"

    Raises:
        ValueError if pattern not found.
    """
    import re
    # Try humaneval_plus first, then humaneval (fallback)
    patterns = [
        r"humaneval_plus\s+pass@1:\s*([\d.]+)",
        r"humaneval\s+pass@1:\s*([\d.]+)",
    ]
    for pat in patterns:
        m = re.search(pat, stdout, re.IGNORECASE)
        if m:
            return float(m.group(1))
    raise ValueError(
        f"Could not parse pass@1 from evalplus output.\nStdout:\n{stdout[:500]}"
    )
```

### A-4 Subtask 8: Resume-Safe Skip Logic + Full Eval Loop

```python
def run_all_evaluations(cfg: "H_M4Config") -> dict:
    """
    Evaluates all (condition × step) combinations.
    step_0 (frozen baseline) evaluated ONCE, reused for all conditions.

    Returns:
        dict: {condition: {step: pass@1_float}}
              e.g. {"variance50": {"step_0": 0.732, "step_10": 0.738, ...}}
    """
    results = {cond: {} for cond in cfg.conditions}

    # Evaluate frozen baseline ONCE (step_0 is same model for all conditions)
    print("[H-M4] Evaluating frozen baseline (step_0)...")
    baseline_dir = generate_samples(
        checkpoint_path=cfg.baseline_model,
        condition="baseline",
        step="step_0",
        cfg=cfg,
    )
    baseline_pass_at_1 = evaluate_samples(baseline_dir, cfg)
    print(f"[H-M4] Baseline pass@1 = {baseline_pass_at_1:.4f}")

    # Reuse baseline for all conditions
    for cond in cfg.conditions:
        results[cond]["step_0"] = baseline_pass_at_1

    # Evaluate fine-tuned checkpoints
    all_steps = cfg.steps  # ["step_10", "step_20", "step_50"]
    for cond in cfg.conditions:
        for step in all_steps:
            ckpt_path = cfg.checkpoint_path(cond, step)
            if not Path(ckpt_path).exists():
                print(f"[H-M4] WARNING: checkpoint missing {cond}/{step}. Skipping.")
                results[cond][step] = None
                continue
            out_dir = generate_samples(ckpt_path, cond, step, cfg)  # resume-safe
            results[cond][step] = evaluate_samples(out_dir, cfg)
            print(f"[H-M4] {cond}/{step} pass@1 = {results[cond][step]:.4f}")

    return results
```

---

## Orchestrator Logic

```python
# run_experiment.py

def main() -> None:
    from pathlib import Path
    from config import H_M4Config
    from evaluate import verify_checkpoints, run_fallback_training, run_all_evaluations
    from metrics import compute_metrics, finalize_p3, save_gate_results, print_gate_summary
    from visualize import generate_all_figures

    cfg = H_M4Config()

    # Step 1: Verify H-M2 checkpoints; fallback train if missing
    missing = verify_checkpoints(cfg)
    needs_training = {c: s for c, s in missing.items() if s}
    if needs_training:
        print(f"[H-M4] Missing checkpoints detected: {needs_training}")
        run_fallback_training(cfg, needs_training)

    # Step 2: Run all EvalPlus evaluations
    pass_at_1 = run_all_evaluations(cfg)

    # Step 3: Compute metrics and gate
    results = compute_metrics(pass_at_1, cfg)
    results = finalize_p3(results, cfg)

    # Step 4: Save results and print summary
    save_gate_results(results, cfg)
    print_gate_summary(results)

    # Step 5: Generate figures
    fig_paths = generate_all_figures(results, cfg)
    print(f"[H-M4] Figures saved: {fig_paths}")

    # Final verdict
    gate = results["gate_passed"]
    print(f"\n{'='*60}")
    print(f"H-M4 GATE: {'PASS ✓' if gate else 'FAIL ✗'}")
    print(f"P1: improvement_variance50 >= 2pp AND gap_vs_random50 >= 1pp")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
```
