"""H-E1: Frozen-model variance profiling on MBPP — vLLM batch version."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from datasets import load_dataset
from vllm import LLM, SamplingParams

# --- Config ---
MODEL_ID = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
K = 4                        # completions per problem
MAX_NEW_TOKENS = 128         # short: just need function body
TEMPERATURE = 1.0
TOP_P = 0.95
SEED = 42
TIMEOUT = 10
VARIANCE_THRESHOLD = 0.1
MIN_COUNT = 15               # gate: >=15/60 problems with var>0.1 (proportional to 50/374)
RESULTS_DIR = Path("docs/youra_research/h-e1/results")
FIGURES_DIR = Path("docs/youra_research/h-e1/figures")


def load_mbpp():
    ds = load_dataset("google-research-datasets/mbpp", "full", split="train")
    print(f"Loaded {len(ds)} MBPP problems")
    return ds


def format_prompt(problem: dict) -> str:
    return (
        f"### Instruction:\nWrite a Python function to solve the following problem.\n\n"
        f"{problem['text']}\n\n### Response:\n"
    )


def extract_code(completion: str) -> str:
    if "```python" in completion:
        return completion.split("```python")[1].split("```")[0].strip()
    elif "```" in completion:
        return completion.split("```")[1].split("```")[0].strip()
    return completion.strip()


def execute_and_test(code_str: str, test_cases: list) -> bool:
    code_str = extract_code(code_str)
    full_code = code_str + "\n" + "\n".join(test_cases)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(full_code)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp],
            timeout=TIMEOUT,
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def compute_gate(results: dict):
    count_above = sum(1 for v in results.values() if v["variance_i"] > VARIANCE_THRESHOLD)
    sorted_ids = sorted(results.keys(), key=lambda t: results[t]["variance_i"], reverse=True)
    top_n = min(50, len(sorted_ids))
    top_ids = sorted_ids[:top_n]
    gate_passed = count_above >= MIN_COUNT
    p_top = [results[t]["p_i"] for t in top_ids]
    metrics = {
        "n_problems": len(results),
        "count_nonzero_variance": count_above,
        "threshold_count": MIN_COUNT,
        "mean_p_top": float(np.mean(p_top)) if p_top else 0.0,
        "gate_passed": gate_passed,
        "k": K,
        "variance_threshold": VARIANCE_THRESHOLD,
    }
    return gate_passed, metrics, top_ids


def save_results(results, top_ids, gate_passed, metrics, path):
    sorted_ids = sorted(results.keys(), key=lambda t: results[t]["variance_i"], reverse=True)
    rank_map = {tid: r + 1 for r, tid in enumerate(sorted_ids)}
    problems_out = {str(tid): {**v, "rank_by_variance": rank_map[tid]} for tid, v in results.items()}
    out = {
        "gate_passed": gate_passed,
        "metrics": metrics,
        "top_ids": [int(t) for t in top_ids],
        "problems": problems_out,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Results saved to {path}")


def generate_figures(results, top_ids, metrics, figures_dir):
    figures_dir.mkdir(parents=True, exist_ok=True)
    top_set = set(top_ids)
    p_vals = [v["p_i"] for v in results.values()]
    var_vals = [v["variance_i"] for v in results.values()]
    sorted_ids = sorted(results.keys(), key=lambda t: results[t]["variance_i"], reverse=True)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["count_nonzero_var", "threshold"], [metrics["count_nonzero_variance"], metrics["threshold_count"]],
           color=["green" if metrics["gate_passed"] else "red", "gray"])
    ax.set_title("Gate Metrics vs Threshold")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(figures_dir / "fig1_gate_metrics.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(p_vals, bins=min(20, len(p_vals)), color="steelblue", edgecolor="white")
    ax.axvspan(0.25, 0.75, alpha=0.2, color="green", label="target zone")
    ax.set_xlabel("Pass rate p_i"); ax.set_ylabel("Count")
    ax.set_title(f"Pass Rate Distribution ({len(results)} problems)")
    ax.legend(); fig.tight_layout()
    fig.savefig(figures_dir / "fig2_pass_rate_histogram.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(var_vals, bins=min(20, len(var_vals)), color="steelblue", edgecolor="white")
    ax.axvline(VARIANCE_THRESHOLD, color="red", linestyle="--", label=f"threshold={VARIANCE_THRESHOLD}")
    ax.set_xlabel("Variance p_i*(1-p_i)"); ax.set_ylabel("Count")
    ax.set_title("Variance Distribution")
    ax.legend(); fig.tight_layout()
    fig.savefig(figures_dir / "fig3_variance_histogram.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for rank_idx, tid in enumerate(sorted_ids):
        p_i = results[tid]["p_i"]
        color = "red" if tid in top_set else "gray"
        alpha = 0.8 if tid in top_set else 0.3
        ax.scatter(rank_idx + 1, p_i, color=color, alpha=alpha, s=15)
    ax.axhspan(0.25, 0.75, alpha=0.1, color="green", label="target p_i zone")
    ax.scatter([], [], color="red", label=f"top-{len(top_ids)}")
    ax.scatter([], [], color="gray", label="rest")
    ax.set_xlabel("Rank by variance"); ax.set_ylabel("Pass rate p_i")
    ax.set_title(f"All {len(results)} problems ranked by variance")
    ax.legend(); fig.tight_layout()
    fig.savefig(figures_dir / "fig4_top_scatter.png", dpi=150)
    plt.close(fig)
    print(f"Figures saved to {figures_dir}")


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    problems = load_mbpp()

    print(f"Loading model {MODEL_ID} via vLLM...")
    llm = LLM(
        model=MODEL_ID,
        dtype="bfloat16",
        trust_remote_code=True,
        seed=SEED,
        max_model_len=1024,
        gpu_memory_utilization=0.75,
        max_num_seqs=64,
    )
    sampling_params = SamplingParams(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_tokens=MAX_NEW_TOKENS,
        n=K,
        seed=SEED,
    )
    print("Model loaded. Generating completions...")

    prompts = [format_prompt(p) for p in problems]
    outputs = llm.generate(prompts, sampling_params)
    print(f"Generated {len(outputs)} × {K} completions. Running tests...")

    results = {}
    for i, (problem, output) in enumerate(zip(problems, outputs)):
        task_id = problem["task_id"]
        test_cases = problem["test_list"]
        pass_count = sum(
            int(execute_and_test(o.text, test_cases))
            for o in output.outputs
        )
        p_i = pass_count / K
        variance_i = p_i * (1 - p_i)
        results[task_id] = {"p_i": p_i, "variance_i": variance_i, "pass_count": pass_count, "k": K}
        if (i + 1) % 50 == 0:
            print(f"  Tested {i+1}/{len(problems)} problems")

    gate_passed, metrics, top_ids = compute_gate(results)

    print(f"\n=== Gate Result ===")
    print(f"count_nonzero_variance: {metrics['count_nonzero_variance']} / {metrics['threshold_count']} threshold")
    print(f"mean_p_top: {metrics['mean_p_top']:.3f}")
    print(f"Gate PASSED: {gate_passed}")

    save_results(results, top_ids, gate_passed, metrics, RESULTS_DIR / "mbpp_variance_profile.json")
    generate_figures(results, top_ids, metrics, FIGURES_DIR)

    sys.exit(0 if gate_passed else 1)


if __name__ == "__main__":
    main()
