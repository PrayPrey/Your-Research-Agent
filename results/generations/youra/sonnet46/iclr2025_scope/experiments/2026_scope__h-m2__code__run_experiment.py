import json
import os
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compute_metrics import (
    compute_cross_dist_tau,
    compute_cross_epsilon_tau,
    compute_cv_per_epsilon,
    evaluate_gate,
    verify_mechanism_activated,
)
from config import ExperimentConfig
from data_utils import load_alpaca_dataloader, load_wikitext_dataloader
from measure_sparsity import measure_all_epsilons
from visualize import generate_all_figures


def load_model_and_tokenizer(cfg: ExperimentConfig):
    """Load LLaMA-3-8B model and tokenizer using local cache."""
    import glob as _glob
    hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
    model_dir_pattern = os.path.join(
        hf_cache,
        "models--" + cfg.model_name.replace("/", "--"),
        "snapshots",
        "*",
    )
    snapshots = _glob.glob(model_dir_pattern)
    if snapshots:
        local_path = snapshots[0]
        print(f"Using local snapshot: {local_path}")
    else:
        local_path = cfg.model_name
        print(f"No local snapshot found, using remote: {local_path}")

    model = AutoModelForCausalLM.from_pretrained(
        local_path,
        torch_dtype=torch.float16,
        device_map="auto",
        local_files_only=True,
    )
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


def save_results(
    cv_per_epsilon,
    tau_matrix,
    cross_dist_tau,
    gate_result: bool,
    gate_details: dict,
    alpaca_sparsity,
    cfg: ExperimentConfig,
) -> None:
    """Save structured results JSON."""
    output = {
        "hypothesis": "h-m2",
        "gate_result": gate_details["gate_result"],
        "cv_per_epsilon": {str(k): v for k, v in cv_per_epsilon.items()},
        "cv_pass_count": gate_details["cv_pass_count"],
        "max_adjacent_tau": gate_details["max_adjacent_tau"],
        "adjacent_pair_results": gate_details["adjacent_pair_results"],
        "tau_matrix": tau_matrix,
        "cross_dist_tau": {str(k): v for k, v in cross_dist_tau.items()},
        "failed_conditions": gate_details["failed_conditions"],
        "sparsity_profiles": {
            str(eps): sv.tolist() for eps, sv in alpaca_sparsity.items()
        },
    }

    os.makedirs(os.path.dirname(os.path.abspath(cfg.results_path)), exist_ok=True)
    with open(cfg.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✓ Results saved to {cfg.results_path}")


def main():
    cfg = ExperimentConfig()
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("Loading model and tokenizer...")
    model, tokenizer = load_model_and_tokenizer(cfg)

    print("Loading dataloaders...")
    alpaca_dl = load_alpaca_dataloader(tokenizer, cfg, cfg.max_length)
    wikitext_dl = load_wikitext_dataloader(tokenizer, cfg, cfg.max_length)

    print("Measuring sparsity across all epsilon values and datasets...")
    alpaca_sparsity, wikitext_sparsity = measure_all_epsilons(
        model, alpaca_dl, wikitext_dl, cfg
    )

    print("Verifying mechanism activated...")
    mechanism_ok, indicators = verify_mechanism_activated(alpaca_sparsity, {}, cfg.epsilons)
    assert mechanism_ok, f"Mechanism not activated: {indicators}"
    print(f"  ✓ Mechanism check: {indicators}")

    print("Computing metrics...")
    cv_per_epsilon = compute_cv_per_epsilon(alpaca_sparsity, cfg.epsilons)
    tau_matrix = compute_cross_epsilon_tau(alpaca_sparsity, cfg.epsilons)
    cross_dist_tau = compute_cross_dist_tau(alpaca_sparsity, wikitext_sparsity, cfg.epsilons)

    gate_pass, gate_details = evaluate_gate(cv_per_epsilon, tau_matrix, cfg)

    print("Generating figures...")
    generate_all_figures(alpaca_sparsity, cv_per_epsilon, tau_matrix, cfg)

    save_results(
        cv_per_epsilon, tau_matrix, cross_dist_tau,
        gate_pass, gate_details, alpaca_sparsity, cfg
    )

    # Print gate summary
    print(f"\n=== GATE: {gate_details['gate_result']} ===")
    print(f"CV robustness: {gate_details['cv_pass_count']}/4 epsilons pass CV > {cfg.cv_threshold}")
    for eps, cv in cv_per_epsilon.items():
        status = "PASS" if cv > cfg.cv_threshold else "FAIL"
        print(f"  epsilon={eps}: CV={cv:.4f} [{status}]")
    print(f"Max adjacent tau: {gate_details['max_adjacent_tau']:.4f} (threshold >= {cfg.cross_epsilon_tau_threshold})")
    if gate_details["failed_conditions"]:
        for cond in gate_details["failed_conditions"]:
            print(f"FAILED: {cond}")

    return gate_details["gate_result"]


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result == "PASS" else 1)
