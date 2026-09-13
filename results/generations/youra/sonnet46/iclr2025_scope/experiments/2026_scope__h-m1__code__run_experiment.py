"""Main experiment orchestration for H-M1: Cross-Distribution Stability of MLP Activation Sparsity."""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Allow running from code/ directory
sys.path.insert(0, str(Path(__file__).parent))

from config import ExperimentConfig
from data_utils import load_all_dataloaders
from measure_sparsity import measure_all_distributions
from compute_icc import compute_icc3k, compute_icc_sensitivity
from compute_metrics import compute_pairwise_tau, compute_tau_sensitivity, evaluate_gate
from visualize import generate_all_figures


def setup_environment(cfg: ExperimentConfig) -> None:
    """Set seeds (numpy=42, torch=42), create output dirs."""
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(os.path.dirname(cfg.results_path) if os.path.dirname(cfg.results_path) else ".", exist_ok=True)

    import transformers
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
    else:
        print("  GPU: not available — running on CPU (slow!)")
    print(f"  torch: {torch.__version__}")
    print(f"  transformers: {transformers.__version__}")
    print("  Environment OK")


def load_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load LLaMA-3.1-8B float16 device_map=auto, set eval mode."""
    hf_home = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    model_id_path = cfg.model_name.replace("/", "--")
    snapshot_base = os.path.join(hf_home, "hub", f"models--{model_id_path}", "snapshots")
    model_path = cfg.model_name
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
        raise RuntimeError(f"Expected {cfg.n_layers} layers, got {n_layers}.")
    for i in range(cfg.n_layers):
        if not hasattr(model.model.layers[i].mlp, "gate_proj"):
            raise RuntimeError(f"Layer {i} MLP has no gate_proj.")
    print(f"Model loaded: {cfg.n_layers} layers, gate_proj verified.")
    return model, tokenizer


def run_sparsity_measurement(
    model,
    dataloaders: Dict,
    cfg: ExperimentConfig,
) -> Dict[float, Dict[str, np.ndarray]]:
    """Measure sparsity for all 4 distributions × 4 epsilons.
    Returns: {epsilon: {dist_name: array(32,)}}"""
    sparsity_by_epsilon = {}
    for eps in cfg.epsilons:
        print(f"  Measuring epsilon={eps} across 4 distributions...")
        sparsity_by_epsilon[eps] = measure_all_distributions(model, dataloaders, eps, cfg)
    return sparsity_by_epsilon


def run_statistical_analysis(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Compute ICC3k, pairwise tau, sensitivity, gate evaluation.
    Returns full results dict."""
    primary = sparsity_by_epsilon[cfg.primary_epsilon]
    icc_result = compute_icc3k(primary)
    tau_results = compute_pairwise_tau(primary)
    gate = evaluate_gate(icc_result["icc3k"], tau_results, cfg)
    icc_sensitivity = compute_icc_sensitivity(sparsity_by_epsilon)
    tau_sensitivity = compute_tau_sensitivity(sparsity_by_epsilon)

    return {
        "gate": gate,
        "icc": icc_result,
        "tau": tau_results,
        "icc_sensitivity": icc_sensitivity,
        "tau_sensitivity": tau_sensitivity,
        "sparsity_profiles": {
            str(k): {dk: dv.tolist() for dk, dv in v.items()}
            for k, v in sparsity_by_epsilon.items()
        },
    }


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """Save experiment_results.json."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    gate = results["gate"]
    icc = results["icc"]

    output = {
        "hypothesis": "h-m1",
        "gate_result": gate["gate_result"],
        "primary_epsilon": 0.01,
        "icc3k": icc["icc3k"],
        "icc_ci_lower": icc["ci_lower"],
        "icc_ci_upper": icc["ci_upper"],
        "tau_min": gate["tau_min"],
        "tau_results": results["tau"],
        "icc_sensitivity": {str(k): v for k, v in results["icc_sensitivity"].items()},
        "tau_sensitivity": {
            str(k): {
                "tau_min": v["tau_min"],
                "tau_results": v["tau_results"],
            }
            for k, v in results["tau_sensitivity"].items()
        },
        "sparsity_profiles": results["sparsity_profiles"],
        "figures_generated": results.get("figures_generated", []),
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {output_path}")


def main() -> None:
    """Orchestrate full pipeline: setup → load → measure → analyze → visualize → save."""
    cfg = ExperimentConfig()

    print("=" * 60)
    print("H-M1: Cross-Distribution Stability of MLP Activation Sparsity")
    print("=" * 60)

    print("\n[1/5] Setting up environment...")
    setup_environment(cfg)

    print("\n[2/5] Loading model and tokenizer...")
    model, tokenizer = load_model_and_tokenizer(cfg)

    print("\n[3/5] Loading datasets (4 distributions)...")
    dataloaders = load_all_dataloaders(tokenizer, cfg)
    for name, dl in dataloaders.items():
        print(f"  {name}: {len(dl.dataset)} samples")

    print("\n[4/5] Running sparsity measurements (4 distributions × 4 epsilons = 16 runs)...")
    sparsity_by_epsilon = run_sparsity_measurement(model, dataloaders, cfg)

    print("\n[5/5] Statistical analysis, figures, and saving...")
    results = run_statistical_analysis(sparsity_by_epsilon, cfg)

    primary_profiles = sparsity_by_epsilon[cfg.primary_epsilon]
    figs = generate_all_figures(
        primary_profiles,
        results["icc"],
        results["tau"],
        results["gate"],
        results["icc_sensitivity"],
        results["tau_sensitivity"],
        cfg.figures_dir,
    )
    results["figures_generated"] = figs

    save_results(results, cfg.results_path)

    gate = results["gate"]
    print(f"\n{'='*60}")
    print(f"=== GATE EVALUATION: {gate['gate_result']} ===")
    print(f"ICC(3,k) = {gate['icc3k']:.4f} (threshold: > {cfg.icc_threshold})")
    print(f"tau_min  = {gate['tau_min']:.4f} (threshold: >= {cfg.tau_threshold})")
    for pair, vals in gate["tau_results"].items():
        print(f"  {pair}: tau={vals['tau']:.4f}, p={vals['pval']:.4f}")
    if gate["failed_conditions"]:
        for fc in gate["failed_conditions"]:
            print(f"FAILED: {fc}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
