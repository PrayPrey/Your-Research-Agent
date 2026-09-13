import os
import sys
import json
import logging
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
import config
from data import get_eval_loader, WaterbirdsDataset
from train_erm import run_training, build_model, load_checkpoint
from compute_traces import compute_traces_for_checkpoint
from evaluate_trajectory import (
    evaluate_seed, check_gate,
    plot_gate_metrics, plot_R_trajectory, plot_auroc_trajectory,
    plot_trace_distribution, plot_spearman_rising,
    compute_auroc,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def run_pilot(device: str) -> bool:
    """seed=1, train 5 epochs, compute trace at t=0, check AUROC(t=0) < 0.70."""
    logger.info("=== PILOT RUN (seed=1, checking t=0 AUROC) ===")
    run_training(seed=config.PILOT_SEED, n_epochs=config.PILOT_EPOCHS,
                 checkpoint_epochs=[0], device=device)

    loader = get_eval_loader(config.DATA_ROOT, split=0, batch_size=config.BATCH_SIZE)
    # Rebuild minority_mask from train dataset
    from data import WaterbirdsDataset, _eval_transform
    ds = WaterbirdsDataset(config.DATA_ROOT, split=0, transform=_eval_transform())
    minority_mask = ds.minority_mask

    traces = compute_traces_for_checkpoint(config.PILOT_SEED, 0, loader,
                                           K=config.K_HUTCHINSON, device=device)
    auroc_t0 = compute_auroc(traces, minority_mask)
    logger.info(f"Pilot AUROC(t=0) = {auroc_t0:.4f}")

    if auroc_t0 >= 0.70:
        logger.error(f"ABORT: AUROC(t=0)={auroc_t0:.4f} >= 0.70. Pretrained artifact detected.")
        return False
    logger.info("Pilot passed: AUROC(t=0) < 0.70. Proceeding to full experiment.")
    return True


def main() -> None:
    device = config.DEVICE
    config.ensure_dirs()
    logger.info(f"Device: {device}")

    # 1. Pilot gate
    if not run_pilot(device):
        sys.exit(1)

    # 2. Full training for all seeds
    logger.info("=== FULL TRAINING (5 seeds × 50 epochs) ===")
    for seed in config.SEEDS:
        logger.info(f"Training seed={seed}...")
        run_training(seed=seed, n_epochs=config.N_EPOCHS,
                     checkpoint_epochs=config.CHECKPOINT_EPOCHS, device=device)

    # 3. Evaluation
    logger.info("=== EVALUATION ===")
    from data import _eval_transform
    ds_train = WaterbirdsDataset(config.DATA_ROOT, split=0, transform=_eval_transform())
    minority_mask = ds_train.minority_mask
    loader = get_eval_loader(config.DATA_ROOT, split=0, batch_size=config.BATCH_SIZE)

    all_seed_results = {}
    for seed in config.SEEDS:
        logger.info(f"Evaluating seed={seed}...")
        result = evaluate_seed(seed, loader, minority_mask, config.CHECKPOINT_EPOCHS, device)
        all_seed_results[seed] = result

    # 4. Gate check
    gate_satisfied, per_seed_pass = check_gate(all_seed_results)
    n_passing = sum(1 for v in per_seed_pass.values() if v)
    logger.info(f"Gate: {n_passing}/5 seeds pass → satisfied={gate_satisfied}")

    # 5. Save results
    out = {
        "hypothesis_id": "H-E3",
        "run_date": str(date.today()),
        "config": {
            "lr": config.LR, "momentum": config.MOMENTUM,
            "weight_decay": config.WEIGHT_DECAY, "batch_size": config.BATCH_SIZE,
            "n_epochs": config.N_EPOCHS, "checkpoint_epochs": config.CHECKPOINT_EPOCHS,
            "seeds": config.SEEDS, "k_hutchinson": config.K_HUTCHINSON,
        },
        "seeds": {},
        "gate": {"n_seeds_passing": n_passing, "satisfied": gate_satisfied,
                 "per_seed_pass": per_seed_pass},
    }
    for seed, r in all_seed_results.items():
        seed_entry = {
            "checkpoints": r["checkpoints"],
            "t_star": r["t_star"],
            "spearman_rho": r["spearman_rho"],
            "spearman_p": r["spearman_p"],
            "hutchinson_cv": r["hutchinson_cv"],
            "gate_auroc_tstar": r["gate_auroc_tstar"],
            "gate_auroc_t0": r["gate_auroc_t0"],
            "gate_spearman": r["gate_spearman"],
            "seed_passes": r["seed_passes"],
        }
        out["seeds"][str(seed)] = seed_entry

    os.makedirs(os.path.dirname(config.RESULTS_PATH), exist_ok=True)
    with open(config.RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    logger.info(f"Results saved to {config.RESULTS_PATH}")

    # 6. Figures
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    plot_gate_metrics(all_seed_results, config.FIGURES_DIR)
    plot_R_trajectory(all_seed_results, config.FIGURES_DIR)
    plot_auroc_trajectory(all_seed_results, config.FIGURES_DIR)
    plot_trace_distribution(all_seed_results, minority_mask, config.FIGURES_DIR)
    plot_spearman_rising(all_seed_results, config.FIGURES_DIR)
    logger.info("Figures saved.")

    logger.info(f"=== COMPLETE. Gate satisfied: {gate_satisfied} ===")


if __name__ == "__main__":
    main()
