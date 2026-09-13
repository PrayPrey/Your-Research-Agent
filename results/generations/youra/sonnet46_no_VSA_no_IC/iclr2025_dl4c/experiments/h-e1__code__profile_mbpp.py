"""H-E1: Frozen-model variance profiling on MBPP training split."""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml
from datasets import load_dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class ProfileConfig:
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"
    k: int = 8
    temperature: float = 1.0
    top_p: float = 0.95
    max_new_tokens: int = 512
    do_sample: bool = True
    timeout: int = 10
    seed: int = 42
    variance_threshold: float = 0.1
    min_count: int = 50
    dataset_id: str = "google-research-datasets/mbpp"
    dataset_config: str = "full"
    split: str = "train"
    expected_size: int = 374
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    checkpoint_every: int = 50
    max_problems: int = 0  # 0 = no limit

    @classmethod
    def from_yaml(cls, path: str) -> "ProfileConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


def load_mbpp_train(cfg: ProfileConfig):
    ds = load_dataset(cfg.dataset_id, cfg.dataset_config, split=cfg.split)
    assert len(ds) == cfg.expected_size, f"Expected {cfg.expected_size} problems, got {len(ds)}"
    return ds


def format_mbpp_prompt(problem: dict) -> str:
    text = problem["text"]
    return (
        f"### Instruction:\nWrite a Python function to solve the following problem.\n\n"
        f"{text}\n\n### Response:\n"
    )


def load_frozen_model(cfg: ProfileConfig):
    dtype = torch.bfloat16 if cfg.torch_dtype == "bfloat16" else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=dtype,
        device_map=cfg.device_map,
        trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def generate_one(model, tokenizer, prompt: str, seed: int, cfg: ProfileConfig) -> str:
    torch.manual_seed(seed)
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)
    prompt_len = input_ids.shape[1]

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=cfg.max_new_tokens,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            do_sample=cfg.do_sample,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = output_ids[0, prompt_len:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def extract_code(completion: str) -> str:
    if "```python" in completion:
        return completion.split("```python")[1].split("```")[0].strip()
    elif "```" in completion:
        return completion.split("```")[1].split("```")[0].strip()
    return completion.strip()


def execute_and_test(code_str: str, test_cases: list, timeout: int = 10) -> bool:
    code_str = extract_code(code_str)
    full_code = code_str + "\n" + "\n".join(test_cases)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(full_code)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp],
            timeout=timeout,
            capture_output=True,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def load_checkpoint(results_dir: Path) -> dict:
    ckpt = results_dir / "checkpoint_latest.json"
    if ckpt.exists():
        with open(ckpt) as f:
            data = json.load(f)
        # keys are strings in JSON, convert to int
        return {int(k): v for k, v in data.items()}
    return {}


def save_checkpoint(results: dict, path: Path) -> None:
    with open(path, "w") as f:
        json.dump({str(k): v for k, v in results.items()}, f, indent=2)


def profile_all_problems(model, tokenizer, problems, cfg: ProfileConfig) -> dict:
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    results = load_checkpoint(results_dir)
    already_done = set(results.keys())
    remaining = [p for p in problems if p["task_id"] not in already_done]

    if cfg.max_problems > 0 and len(remaining) > cfg.max_problems:
        remaining = remaining[:cfg.max_problems]

    print(f"Resuming from {len(already_done)} completed, {len(remaining)} remaining.")

    for problem_idx, problem in enumerate(tqdm(remaining, desc="Profiling MBPP")):
        task_id = problem["task_id"]
        prompt = format_mbpp_prompt(problem)
        test_cases = problem["test_list"]
        pass_count = 0

        for comp_idx in range(cfg.k):
            seed = cfg.seed + problem_idx * cfg.k + comp_idx
            code_str = generate_one(model, tokenizer, prompt, seed, cfg)
            passed = execute_and_test(code_str, test_cases, cfg.timeout)
            pass_count += int(passed)

        p_i = pass_count / cfg.k
        variance_i = p_i * (1 - p_i)
        results[task_id] = {
            "p_i": p_i,
            "variance_i": variance_i,
            "pass_count": pass_count,
            "k": cfg.k,
        }

        if (problem_idx + 1) % cfg.checkpoint_every == 0:
            save_checkpoint(results, results_dir / "checkpoint_latest.json")
            torch.cuda.empty_cache()

    # final checkpoint
    save_checkpoint(results, results_dir / "checkpoint_latest.json")
    return results


def compute_gate(results: dict, cfg: ProfileConfig):
    count_above = sum(
        1 for v in results.values() if v["variance_i"] > cfg.variance_threshold
    )
    sorted_ids = sorted(results.keys(), key=lambda t: results[t]["variance_i"], reverse=True)
    top50_ids = sorted_ids[:50]
    gate_passed = count_above >= cfg.min_count

    p_values = [results[t]["p_i"] for t in top50_ids]
    metrics = {
        "count_nonzero_variance": count_above,
        "threshold_count": cfg.min_count,
        "mean_p_top50": float(np.mean(p_values)) if p_values else 0.0,
        "gate_passed": gate_passed,
        "total_problems": len(results),
    }
    return gate_passed, metrics, top50_ids


def save_results(results: dict, top50_ids: list, gate_result: bool, metrics: dict, path: Path) -> None:
    sorted_ids = sorted(results.keys(), key=lambda t: results[t]["variance_i"], reverse=True)
    rank_map = {task_id: rank + 1 for rank, task_id in enumerate(sorted_ids)}

    problems_out = {}
    for task_id, v in results.items():
        problems_out[str(task_id)] = {**v, "rank_by_variance": rank_map[task_id]}

    out = {
        "gate_passed": gate_result,
        "metrics": metrics,
        "top50_ids": [int(t) for t in top50_ids],
        "problems": problems_out,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Results saved to {path}")


def generate_figures(results: dict, top50_ids: list, metrics: dict, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)

    p_values = [v["p_i"] for v in results.values()]
    var_values = [v["variance_i"] for v in results.values()]
    task_ids = list(results.keys())
    sorted_ids = sorted(task_ids, key=lambda t: results[t]["variance_i"], reverse=True)
    top50_set = set(top50_ids)

    # Fig 1: gate metrics bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        ["count_nonzero_var", "threshold"],
        [metrics["count_nonzero_variance"], metrics["threshold_count"]],
        color=["green" if metrics["gate_passed"] else "red", "gray"],
    )
    ax.set_title("Gate Metrics vs Threshold")
    ax.set_ylabel("Count")
    ax.legend(["actual", "threshold"])
    fig.tight_layout()
    fig.savefig(figures_dir / "fig1_gate_metrics.png", dpi=150)
    plt.close(fig)

    # Fig 2: pass rate histogram
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(p_values, bins=20, color="steelblue", edgecolor="white")
    ax.axvspan(0.25, 0.75, alpha=0.2, color="green", label="target zone [0.25, 0.75]")
    ax.set_xlabel("Pass rate p_i")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Pass Rates (374 problems)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "fig2_pass_rate_histogram.png", dpi=150)
    plt.close(fig)

    # Fig 3: variance histogram
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(var_values, bins=20, color="steelblue", edgecolor="white")
    ax.axvline(0.1, color="red", linestyle="--", label="threshold=0.1")
    ax.set_xlabel("Variance p_i*(1-p_i)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Variances")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "fig3_variance_histogram.png", dpi=150)
    plt.close(fig)

    # Fig 4: top-50 scatter
    fig, ax = plt.subplots(figsize=(8, 5))
    for rank_idx, task_id in enumerate(sorted_ids):
        p_i = results[task_id]["p_i"]
        color = "red" if task_id in top50_set else "gray"
        alpha = 0.8 if task_id in top50_set else 0.3
        ax.scatter(rank_idx + 1, p_i, color=color, alpha=alpha, s=15)
    ax.axhspan(0.25, 0.75, alpha=0.1, color="green", label="target p_i zone")
    ax.scatter([], [], color="red", label="top-50")
    ax.scatter([], [], color="gray", label="rest")
    ax.set_xlabel("Rank by variance (1=highest)")
    ax.set_ylabel("Pass rate p_i")
    ax.set_title("All 374 problems ranked by variance")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "fig4_top50_scatter.png", dpi=150)
    plt.close(fig)

    print(f"Figures saved to {figures_dir}")


def main() -> None:
    # locate config relative to repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent.parent  # code/ -> h-e1/ -> youra_research/ -> docs/ -> repo root
    config_path = script_dir.parent / "config.yaml"

    if config_path.exists():
        cfg = ProfileConfig.from_yaml(str(config_path))
        print(f"Loaded config from {config_path}")
    else:
        cfg = ProfileConfig()
        print("Using default config")

    # resolve paths relative to repo root
    cfg.results_dir = str(repo_root / cfg.results_dir)
    cfg.figures_dir = str(repo_root / cfg.figures_dir)

    torch.manual_seed(cfg.seed)

    print("Loading MBPP train split...")
    problems = load_mbpp_train(cfg)
    print(f"Loaded {len(problems)} problems")

    print(f"Loading model {cfg.model_id}...")
    model, tokenizer = load_frozen_model(cfg)
    print("Model loaded")

    results = profile_all_problems(model, tokenizer, problems, cfg)

    gate_passed, metrics, top50_ids = compute_gate(results, cfg)

    print(f"\n=== Gate Result ===")
    print(f"count_nonzero_variance: {metrics['count_nonzero_variance']} (threshold: {cfg.min_count})")
    print(f"mean_p_top50: {metrics['mean_p_top50']:.3f}")
    print(f"Gate PASSED: {gate_passed}")

    results_path = Path(cfg.results_dir) / "mbpp_variance_profile.json"
    save_results(results, top50_ids, gate_passed, metrics, results_path)

    generate_figures(results, top50_ids, metrics, Path(cfg.figures_dir))

    # save run config
    import dataclasses
    with open(Path(cfg.results_dir) / "run_config.yaml", "w") as f:
        yaml.dump(dataclasses.asdict(cfg), f, default_flow_style=False)

    sys.exit(0 if gate_passed else 1)


if __name__ == "__main__":
    main()
