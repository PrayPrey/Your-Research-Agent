"""
Main Experiment Orchestrator for h-m1
Threshold Transfer Robustness Testing per 03_logic.md L-6
"""
from datasets import load_dataset
from typing import Dict, List
import json
import logging

from config import CONFIG
from threshold_sweep import generate_threshold_grid, apply_threshold_sweep, select_optimal_threshold
from cross_stage_transfer import cross_apply_thresholds, compute_transfer_delta
from visualize import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["paths"]["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_datasets() -> tuple[List[Dict], List[Dict]]:
    """Load C4 + Dolly datasets per 03_logic.md L-6-1"""
    logger.info("Loading datasets...")

    # C4 (pretrain)
    logger.info(f"Loading C4 dataset (num_samples={CONFIG['dataset']['pretrain']['num_samples']})")
    c4 = load_dataset(
        CONFIG["dataset"]["pretrain"]["name"],
        "en",
        split="train",
        streaming=True
    )
    c4_samples = []
    for i, sample in enumerate(c4):
        if i >= CONFIG["dataset"]["pretrain"]["num_samples"]:
            break
        # Convert to instruction format
        c4_samples.append({
            "instruction": sample["text"][:200],  # First 200 chars as instruction
            "input": "",
            "output": sample["text"][200:400] if len(sample["text"]) > 200 else ""
        })
    logger.info(f"Loaded {len(c4_samples)} C4 samples")

    # Dolly (finetune)
    logger.info(f"Loading Dolly dataset (num_samples={CONFIG['dataset']['finetune']['num_samples']})")
    dolly = load_dataset(
        CONFIG["dataset"]["finetune"]["name"],
        split="train"
    )
    dolly_samples = []
    for i, sample in enumerate(dolly):
        if i >= CONFIG["dataset"]["finetune"]["num_samples"]:
            break
        dolly_samples.append({
            "instruction": sample["instruction"],
            "input": sample.get("context", ""),
            "output": sample["response"]
        })
    logger.info(f"Loaded {len(dolly_samples)} Dolly samples")

    return c4_samples, dolly_samples


def mock_evaluate_variant(variant_name: str, sample_count: int) -> Dict[str, float]:
    """
    Mock evaluation (PoC mode) per 03_prd.md NFR2.

    Performance correlates with sample count (more data = better score).
    Introduces small delta between optimal and transferred.
    """
    # Base scores
    base_mmlu = 0.42
    base_hellaswag = 0.76

    # Bonus for optimal configs (stage-tuned)
    if "on_pretrain" in variant_name and "pretrain_on" in variant_name:
        # Pretrain thresholds on pretrain data (optimal)
        mmlu = base_mmlu + 0.03
        hellaswag = base_hellaswag + 0.02
    elif "on_finetune" in variant_name and "finetune_on" in variant_name:
        # Finetune thresholds on finetune data (optimal)
        mmlu = base_mmlu + 0.04
        hellaswag = base_hellaswag + 0.03
    else:
        # Transferred (cross-stage) - small penalty
        mmlu = base_mmlu + 0.01
        hellaswag = base_hellaswag + 0.01

    # Sample count correlation (normalized)
    sample_factor = min(1.0, sample_count / 10000)
    mmlu *= sample_factor
    hellaswag *= sample_factor

    logger.info(f"Mock eval {variant_name}: MMLU={mmlu:.3f}, HellaSwag={hellaswag:.3f}")
    return {"mmlu": mmlu, "hellaswag": hellaswag}


def run_threshold_transfer_experiment(
    pretrain_dataset_name: str = None,
    finetune_dataset_name: str = None,
    dedup_range: List[float] = None,
    ppl_range: List[int] = None,
    poc_mode: bool = True
) -> Dict:
    """
    Execute threshold transfer experiment per 03_prd.md.

    Returns:
        {
            "gate_result": "PASS" | "FAIL",
            "pretrain_optimal": (dedup, ppl),
            "finetune_optimal": (dedup, ppl),
            "transfer_deltas": {...},
            "max_delta": float,
            "artifacts": {...}
        }
    """
    logger.info("=" * 80)
    logger.info("Starting h-m1 Threshold Transfer Experiment")
    logger.info("=" * 80)

    # Use config defaults if not provided
    dedup_range = dedup_range or CONFIG["thresholds"]["dedup_thresholds"]
    ppl_range = ppl_range or CONFIG["thresholds"]["perplexity_thresholds"]

    # Step 1: Load datasets
    c4_samples, dolly_samples = load_datasets()

    # Step 2: Generate threshold grid
    logger.info("\nGenerating threshold grid...")
    threshold_grid = generate_threshold_grid(dedup_range, ppl_range)
    logger.info(f"Grid size: {len(threshold_grid)} combinations")

    # Step 3: Sweep thresholds on each stage
    logger.info("\nSweeping thresholds on pretrain stage (C4)...")
    pretrain_sweep = apply_threshold_sweep(c4_samples, threshold_grid, stage="pretrain")

    logger.info("\nSweeping thresholds on finetune stage (Dolly)...")
    finetune_sweep = apply_threshold_sweep(dolly_samples, threshold_grid, stage="finetune")

    # Step 4: Select optimal thresholds per stage
    logger.info("\nSelecting optimal thresholds...")
    pretrain_optimal = select_optimal_threshold(pretrain_sweep, metric="sample_count")
    finetune_optimal = select_optimal_threshold(finetune_sweep, metric="sample_count")

    # Step 5: Cross-apply thresholds
    logger.info("\nCross-applying thresholds (transfer testing)...")
    cross_variants = cross_apply_thresholds(
        pretrain_optimal,
        finetune_optimal,
        c4_samples,
        dolly_samples
    )

    # Step 6: Evaluate variants (mock for PoC)
    logger.info("\nEvaluating variants (mock mode)...")
    evaluation_results = {}
    for variant_name, (curated_samples, stats) in cross_variants.items():
        evaluation_results[variant_name] = mock_evaluate_variant(
            variant_name,
            stats["final_count"]
        )

    # Step 7: Compute transfer deltas
    logger.info("\nComputing transfer deltas...")

    # Pretrain→Finetune transfer
    delta_pretrain_to_finetune = compute_transfer_delta(
        evaluation_results["finetune_on_finetune"],  # optimal
        evaluation_results["pretrain_on_finetune"],  # transferred
        metrics=["mmlu", "hellaswag"]
    )

    # Finetune→Pretrain transfer
    delta_finetune_to_pretrain = compute_transfer_delta(
        evaluation_results["pretrain_on_pretrain"],  # optimal
        evaluation_results["finetune_on_pretrain"],  # transferred
        metrics=["mmlu", "hellaswag"]
    )

    transfer_deltas = {
        "pretrain_to_finetune": delta_pretrain_to_finetune["max_delta"],
        "finetune_to_pretrain": delta_finetune_to_pretrain["max_delta"],
    }

    max_delta = max(transfer_deltas.values())
    logger.info(f"Max transfer delta: {max_delta:.4f}")

    # Step 8: Gate decision
    gate_threshold = CONFIG["evaluation"]["max_delta"]
    gate_result = "PASS" if max_delta < gate_threshold else "FAIL"
    logger.info(f"\nGate decision: {gate_result} (threshold={gate_threshold}, actual={max_delta:.4f})")

    # Step 9: Prepare results
    results = {
        "gate_result": gate_result,
        "pretrain_optimal": pretrain_optimal,
        "finetune_optimal": finetune_optimal,
        "transfer_deltas": transfer_deltas,
        "max_delta": max_delta,
        "max_delta_threshold": gate_threshold,
        "evaluation_results": evaluation_results,
        "cross_variants_stats": {k: v[1] for k, v in cross_variants.items()},
    }

    # Step 10: Save results
    output_dir = CONFIG["paths"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_path}")

    # Step 11: Generate visualizations
    logger.info("\nGenerating visualizations...")
    generate_all_figures(
        results,
        pretrain_sweep,
        finetune_sweep,
        str(CONFIG["paths"]["figures_dir"])
    )

    logger.info("\n" + "=" * 80)
    logger.info("Experiment complete")
    logger.info("=" * 80)

    return results


if __name__ == "__main__":
    results = run_threshold_transfer_experiment(poc_mode=True)
    print(f"\nFinal Gate Result: {results['gate_result']}")
    print(f"Max Delta: {results['max_delta']:.4f}")
