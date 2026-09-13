"""
run_experiment.py — Orchestrate 4 training runs + weight divergence analysis for H-E1.

Usage:
    CUDA_VISIBLE_DEVICES=1 python run_experiment.py
"""
import os
import sys
import json
import logging
from datetime import datetime

# GPU selection must happen before any CUDA import
# Set by caller (pipeline) or default to GPU 1
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["WANDB_DISABLED"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from config import get_all_configs, TrainingConfig
from train import run_training
from evaluate import (
    load_adapter_state_dict,
    compute_layer_cosine_similarity,
    evaluate_gate,
    save_results,
)
from visualize import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("outputs/h-e1/experiment.log"),
    ],
)
logger = logging.getLogger(__name__)

FIGURES_DIR = "docs/youra_research/20260504_scope/h-e1/figures"
OUTPUTS_DIR = "outputs/h-e1"


def run_model_pair(
    model_name: str,
    baseline_cfg: TrainingConfig,
    eviction_cfg: TrainingConfig,
) -> dict:
    """Run one baseline + eviction-aware training pair and compute weight divergence."""
    short_name = "llama2" if "llama" in model_name.lower() else "mistral"
    logger.info(f"=== Starting model pair: {model_name} ===")

    logger.info(f"[{short_name}] Training BASELINE...")
    baseline_adapter = run_training(baseline_cfg)

    logger.info(f"[{short_name}] Training EVICTION-AWARE...")
    eviction_adapter = run_training(eviction_cfg)

    logger.info(f"[{short_name}] Loading adapter weights for comparison...")
    baseline_sd = load_adapter_state_dict(baseline_adapter)
    eviction_sd = load_adapter_state_dict(eviction_adapter)

    logger.info(f"[{short_name}] Computing cosine similarities...")
    cosine_results = compute_layer_cosine_similarity(baseline_sd, eviction_sd)
    gate = evaluate_gate(cosine_results, threshold=0.95)

    result = {
        "model_name": model_name,
        "short_name": short_name,
        "baseline_adapter": baseline_adapter,
        "eviction_adapter": eviction_adapter,
        "cosine_similarity": cosine_results,
        "gate": gate,
        "timestamp": datetime.now().isoformat(),
    }

    # Save per-model results
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    save_results(result, os.path.join(OUTPUTS_DIR, f"weight_analysis_{short_name}.json"))
    logger.info(f"[{short_name}] Gate: {'PASS' if gate['gate_pass'] else 'FAIL'} "
                f"(min_sim={gate['min_sim']:.4f})")
    return result


def main() -> None:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    logger.info("=" * 60)
    logger.info("H-E1 EXPERIMENT: Eviction-Aware LoRA Weight Divergence")
    logger.info("=" * 60)
    logger.info(f"Started: {datetime.now().isoformat()}")

    configs = get_all_configs()
    # configs = [llama_baseline, llama_eviction, mistral_baseline, mistral_eviction]
    llama_baseline, llama_eviction, mistral_baseline, mistral_eviction = configs

    # Run LLaMA-2-7B pair
    llama_result = run_model_pair(
        "meta-llama/Llama-2-7b-hf",
        llama_baseline,
        llama_eviction,
    )

    # Run Mistral-7B pair
    mistral_result = run_model_pair(
        "mistralai/Mistral-7B-v0.1",
        mistral_baseline,
        mistral_eviction,
    )

    # Generate figures
    logger.info("Generating figures...")
    generate_all_figures(
        llama2_results=llama_result["cosine_similarity"],
        mistral_results=mistral_result["cosine_similarity"],
        figures_dir=FIGURES_DIR,
    )

    # Overall gate result (PASS if either model passes)
    llama_pass = llama_result["gate"]["gate_pass"]
    mistral_pass = mistral_result["gate"]["gate_pass"]
    overall_pass = llama_pass or mistral_pass

    gate_result = {
        "hypothesis_id": "h-e1",
        "gate_type": "MUST_WORK",
        "gate_pass": overall_pass,
        "llama2_gate": llama_result["gate"],
        "mistral_gate": mistral_result["gate"],
        "criterion": "min(cosine_similarity) < 0.95 in at least one model",
        "timestamp": datetime.now().isoformat(),
    }

    gate_path = os.path.join(OUTPUTS_DIR, "gate_result.json")
    save_results(gate_result, gate_path)

    # Also save to hypothesis folder for pipeline
    hyp_gate_path = "docs/youra_research/20260504_scope/h-e1/experiment_results.json"
    save_results({
        "hypothesis_id": "h-e1",
        "gate_result": "PASS" if overall_pass else "FAIL",
        "gate_type": "MUST_WORK",
        "llama2": {
            "min_cosine_similarity": llama_result["gate"]["min_sim"],
            "mean_cosine_similarity": llama_result["gate"]["mean_sim"],
            "layers_below_threshold": llama_result["gate"]["layers_below_threshold"],
            "gate_pass": llama_pass,
        },
        "mistral": {
            "min_cosine_similarity": mistral_result["gate"]["min_sim"],
            "mean_cosine_similarity": mistral_result["gate"]["mean_sim"],
            "layers_below_threshold": mistral_result["gate"]["layers_below_threshold"],
            "gate_pass": mistral_pass,
        },
        "timestamp": datetime.now().isoformat(),
    }, hyp_gate_path)

    logger.info("=" * 60)
    logger.info(f"EXPERIMENT COMPLETE")
    logger.info(f"Overall Gate: {'PASS' if overall_pass else 'FAIL'}")
    logger.info(f"  LLaMA-2-7B: {'PASS' if llama_pass else 'FAIL'} "
                f"(min_sim={llama_result['gate']['min_sim']:.4f})")
    logger.info(f"  Mistral-7B: {'PASS' if mistral_pass else 'FAIL'} "
                f"(min_sim={mistral_result['gate']['min_sim']:.4f})")
    logger.info(f"Results: {gate_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
