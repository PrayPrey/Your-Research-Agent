"""Main experiment orchestration for H-E1: LLaMA-3-8B activation sparsity measurement."""

import json
import sys
import os
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Allow running from code/ directory
sys.path.insert(0, str(Path(__file__).parent))

from config import ExperimentConfig
from data_utils import load_alpaca_dataloader, load_wikitext_dataloader
from measure_sparsity import run_all_conditions, verify_mechanism
from compute_metrics import compute_all_metrics, check_gate_conditions
from visualize import generate_all_figures


def verify_environment(cfg: ExperimentConfig = None):
    """Check CUDA, VRAM, and package versions."""
    import transformers
    import datasets
    import scipy
    import matplotlib

    print(f"  torch: {torch.__version__}")
    print(f"  transformers: {transformers.__version__}")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        if vram_gb < 15:
            print("  WARNING: Less than 15GB VRAM — may OOM on LLaMA-3-8B float16")
    else:
        print("  GPU: not available — running on CPU (slow!)")
    print("  Environment OK")


def setup_model_and_tokenizer(cfg: ExperimentConfig):
    """Load LLaMA-3-8B float16, eval mode, device_map='auto'. Validates 32 layers + gate_proj."""
    # Use snapshot path directly if available (avoids auth issues when hub is inaccessible)
    import os
    hf_home = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    model_id_path = cfg.model_name.replace("/", "--")
    snapshot_base = os.path.join(hf_home, "hub", f"models--{model_id_path}", "snapshots")
    model_path = cfg.model_name  # default: use HF ID
    if os.path.isdir(snapshot_base):
        snapshots = [s for s in os.listdir(snapshot_base) if os.path.isdir(os.path.join(snapshot_base, s))]
        if snapshots:
            model_path = os.path.join(snapshot_base, snapshots[0])
            print(f"Using local snapshot: {model_path}")

    print(f"Loading tokenizer: {cfg.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    torch_dtype = dtype_map[cfg.torch_dtype]

    print(f"Loading model: {cfg.model_name} ({cfg.torch_dtype})")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        device_map=cfg.device_map,
        local_files_only=True,
    )
    model.eval()

    n_layers = len(model.model.layers)
    if n_layers != cfg.n_layers:
        raise RuntimeError(f"Expected {cfg.n_layers} layers, got {n_layers}. Not LLaMA-3-8B.")

    for i in range(cfg.n_layers):
        if not hasattr(model.model.layers[i].mlp, "gate_proj"):
            raise RuntimeError(f"Layer {i} MLP has no gate_proj. Architecture mismatch.")

    print(f"Model loaded: {cfg.n_layers} layers, gate_proj verified.")
    return model, tokenizer


def save_results(condition_results: dict, metrics: dict, gate_pass: bool, cfg: ExperimentConfig) -> None:
    """Save results.json to cfg.results_dir."""
    results_path = Path(cfg.results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    layer_arrays = {}
    for (dataset, eps, length), arr in condition_results.items():
        key = f"{dataset}_eps{eps}_len{length}"
        layer_arrays[key] = arr.tolist()

    summary = {
        "hypothesis": "H-E1",
        "gate_pass": gate_pass,
        "primary_metrics": {
            "cv_primary": metrics["cv_primary"],
            "tau_calibration": metrics["tau_calibration"],
            "tau_length": metrics.get("tau_length"),
            "cv_primary_pass": metrics["cv_primary"] > cfg.cv_threshold,
            "tau_calibration_pass": metrics["tau_calibration"] >= cfg.tau_threshold,
        },
        "all_metrics": {k: v for k, v in metrics.items() if isinstance(v, float)},
        "layer_sparsity_conditions": layer_arrays,
    }

    out_path = results_path / "results.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {out_path}")


def main(cfg: ExperimentConfig = None):
    """Full pipeline: setup → data → measure → metrics → figures → save."""
    if cfg is None:
        cfg = ExperimentConfig()

    print("=" * 60)
    print("H-E1: LLaMA-3-8B Activation Sparsity Experiment")
    print("=" * 60)

    # 1. Verify environment
    print("\n[1/6] Verifying environment...")
    verify_environment(cfg)

    # 2. Setup model & tokenizer
    print("\n[2/6] Loading model and tokenizer...")
    model, tokenizer = setup_model_and_tokenizer(cfg)

    # 3. Load datasets
    print("\n[3/6] Loading datasets...")
    print(f"  Alpaca short (max_length={cfg.short_length})...")
    alpaca_short  = load_alpaca_dataloader(tokenizer, cfg, max_length=cfg.short_length)
    print(f"  Alpaca long (max_length={cfg.long_length})...")
    alpaca_long   = load_alpaca_dataloader(tokenizer, cfg, max_length=cfg.long_length)
    print(f"  WikiText-103 (max_length={cfg.long_length})...")
    wikitext_long = load_wikitext_dataloader(tokenizer, cfg, max_length=cfg.long_length)
    print(f"  Datasets ready: {len(alpaca_short.dataset)} + {len(alpaca_long.dataset)} + {len(wikitext_long.dataset)} samples")

    # 4. Run all measurement conditions
    print("\n[4/6] Running sparsity measurements (3 datasets × 4 epsilons = 12 conditions)...")
    condition_results = run_all_conditions(model, alpaca_short, alpaca_long, wikitext_long, cfg)
    print(f"  {len(condition_results)} conditions measured.")

    # Verify mechanism on primary condition
    primary_sparsity = condition_results[("alpaca", cfg.primary_epsilon, cfg.long_length)]
    mech_ok, mech_info = verify_mechanism(primary_sparsity, cfg)
    print(f"  Mechanism check: {'PASS' if mech_ok else 'WARN'} — {mech_info}")

    # 5. Compute metrics
    print("\n[5/6] Computing metrics...")
    metrics = compute_all_metrics(condition_results, cfg)
    gate_pass, gate_details = check_gate_conditions(metrics, cfg)

    print(f"\n  Results table:")
    print(f"  {'Epsilon':>10} {'CV':>8} {'tau_cal':>10} {'tau_len':>10}")
    print(f"  {'-'*42}")
    for eps in cfg.epsilons:
        eps_key = str(eps)
        cv_v   = metrics.get(f"cv_alpaca_long_eps{eps_key}", 0.0)
        tau_v  = metrics.get(f"tau_calibration_eps{eps_key}", 0.0)
        taul_v = metrics.get(f"tau_length_eps{eps_key}", 0.0)
        marker = " <-- primary" if eps == cfg.primary_epsilon else ""
        print(f"  {eps:>10.3f} {cv_v:>8.3f} {tau_v:>10.3f} {taul_v:>10.3f}{marker}")

    print(f"\n  Gate Conditions:")
    print(f"    CV = {gate_details['cv_value']:.3f} > {cfg.cv_threshold} → {'PASS' if gate_details['cv_pass'] else 'FAIL'}")
    print(f"    tau = {gate_details['tau_value']:.3f} >= {cfg.tau_threshold} → {'PASS' if gate_details['tau_pass'] else 'FAIL'}")
    print(f"\n  Gate Result: {'PASS ✓' if gate_pass else 'FAIL ✗'}")

    # 6. Generate figures
    print("\n[6/6] Generating figures...")
    generate_all_figures(condition_results, metrics, cfg)

    # 7. Save results
    save_results(condition_results, metrics, gate_pass, cfg)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE — Gate: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    return gate_pass, metrics, condition_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="H-E1 Activation Sparsity Experiment")
    parser.add_argument("--model-name", default="meta-llama/Meta-Llama-3-8B")
    parser.add_argument("--n-samples", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--figures-dir", default="h-e1/figures")
    parser.add_argument("--results-dir", default="h-e1/results")
    args = parser.parse_args()

    cfg = ExperimentConfig(
        model_name=args.model_name,
        n_samples=args.n_samples,
        batch_size=args.batch_size,
        figures_dir=args.figures_dir,
        results_dir=args.results_dir,
    )

    gate_pass, metrics, _ = main(cfg)
    sys.exit(0 if gate_pass else 1)
