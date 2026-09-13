"""A-7: 1.3B model evaluation + delta ratio computation."""
import json
import os
import subprocess
from pathlib import Path

from config import H_M4_Config, BENCHMARK_ORDER


def run_bigcode_eval(checkpoint_path: str, model_tag: str, cfg: H_M4_Config) -> dict:
    """Run bigcode-evaluation-harness for HumanEval + MBPP."""
    harness_dir = os.environ.get("BIGCODE_HARNESS_DIR", "bigcode-evaluation-harness")
    out_path = f"{cfg.paths.results_dir}/{model_tag}_bigcode.json"
    os.makedirs(cfg.paths.results_dir, exist_ok=True)

    cmd = [
        "accelerate", "launch", f"{harness_dir}/main.py",
        "--model", checkpoint_path,
        "--tasks", "humaneval,mbpp",
        "--n_samples", str(cfg.n_samples),
        "--temperature", str(cfg.temperature),
        "--batch_size", "8",
        "--allow_code_execution",
        "--metric_output_path", out_path,
    ]
    subprocess.run(cmd, check=True)

    with open(out_path) as f:
        raw = json.load(f)
    return {
        "humaneval": raw.get("humaneval", {}).get("pass@1", 0.0),
        "mbpp": raw.get("mbpp", {}).get("pass@1", 0.0),
    }


def run_lcb_eval(checkpoint_path: str, model_tag: str, cfg: H_M4_Config) -> dict:
    """Run LiveCodeBench harness, return difficulty-stratified pass@1."""
    lcb_dir = os.environ.get("LCB_DIR", "LiveCodeBench")
    out_path = f"{cfg.paths.results_dir}/{model_tag}_lcb.json"
    os.makedirs(cfg.paths.results_dir, exist_ok=True)

    cmd = [
        "python", "-m", "lcb_runner.runner.main",
        "--model", checkpoint_path,
        "--release_version", cfg.lcb_release,
        "--n_workers", "4",
        "--output_path", out_path,
    ]
    subprocess.run(cmd, check=True)

    with open(out_path) as f:
        raw = json.load(f)
    return {
        "lcb_easy":   raw.get("easy",   {}).get("pass@1", 0.0),
        "lcb_medium": raw.get("medium", {}).get("pass@1", 0.0),
        "lcb_hard":   raw.get("hard",   {}).get("pass@1", 0.0),
    }


def evaluate_model(checkpoint_path: str, model_tag: str, cfg: H_M4_Config) -> dict:
    bigcode = run_bigcode_eval(checkpoint_path, model_tag, cfg)
    lcb = run_lcb_eval(checkpoint_path, model_tag, cfg)
    return {**bigcode, **lcb}


def compute_delta_ratio_1_3b(rlef_results: dict, sft_results: dict) -> tuple:
    """Δ ratio: delta_lcb_hard / delta_humaneval. Gate: >= 1.0."""
    delta = {bm: rlef_results[bm] - sft_results[bm] for bm in BENCHMARK_ORDER}
    delta_lcb = delta.get("lcb_hard", 0.0)
    delta_he = delta.get("humaneval", 0.0)

    if abs(delta_he) < 1e-6:
        delta_ratio = float("inf") if delta_lcb > 0 else 0.0
    else:
        delta_ratio = delta_lcb / delta_he

    gate_passed = delta_ratio >= 1.0
    print(f"[1.3B Gate] Δ_ratio = {delta_ratio:.3f} ({'PASS' if gate_passed else 'FAIL'} — threshold: >= 1.0)")
    return delta_ratio, delta
