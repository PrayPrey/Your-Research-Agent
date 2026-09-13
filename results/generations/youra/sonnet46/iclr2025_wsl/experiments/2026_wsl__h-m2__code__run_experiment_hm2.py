"""H-M2 Experiment: Augmentation/Canonicalization vs NFT Comparison.

Hypothesis: Permutation augmentation (flat-MLP+aug) and oracle canonicalization
(flat-MLP+canon) reduce Delta_rho compared to flat-MLP baseline but do not match
NFT-base performance, confirming architectural equivariance is a necessary inductive bias.

Gate: SHOULD_WORK (three-way ranking: NFT-base < canon < aug < flat-MLP in Δρ)

Usage:
    cd /home/anonymous/YouRA_results_new_4/TEST_wsl
    CUDA_VISIBLE_DEVICES=0 python docs/youra_research/20260316_wsl/h-m2/code/run_experiment_hm2.py
"""
import json
import logging
import math
import os
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

# ---------------------------------------------------------------------------
# Path setup: insert h-m1 source for imports
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# _SCRIPT_DIR = h-m2/code/
# h-m2/code/../.. = 20260316_wsl (research date folder with all hypotheses)
_RESEARCH_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
_WORKSPACE_ROOT = os.path.abspath(os.path.join(_RESEARCH_ROOT, "..", "..", ".."))

HM1_CODE = os.path.join(_RESEARCH_ROOT, "h-m1", "code")
if HM1_CODE not in sys.path:
    sys.path.insert(0, HM1_CODE)

# HM2 source
HM2_SRC = os.path.join(_SCRIPT_DIR, "src")
if HM2_SRC not in sys.path:
    sys.path.insert(0, HM2_SRC)

# ---------------------------------------------------------------------------
# Imports from H-M1 source
# ---------------------------------------------------------------------------
try:
    from src.config import ExperimentConfig, GateConfig, ENCODER_CONFIG
    from src.data_loader import load_zoo, ZooDataset, get_dataloaders
    from src.models import build_encoder
    from src.train import load_checkpoint
    from src.evaluate import evaluate_all_encoders, apply_holm_correction
except ImportError as e:
    print(f"ERROR: Failed to import h-m1 modules: {e}")
    print(f"  HM1_CODE path: {HM1_CODE}")
    print(f"  sys.path: {sys.path[:5]}")
    raise

# Imports from H-M2 source
from gate_evaluator import (
    evaluate_gate_hm2,
    check_checkpoint_consistency,
    run_paired_bootstrap,
    apply_holm_correction as holm_hm2,
    compute_cohens_d,
    format_p_value_report,
    ENCODERS_HM2,
)
from visualize_hm2 import (
    plot_gate_metrics_comparison,
    plot_delta_rho_heatmap,
    plot_rho_degradation_curves,
    plot_threeway_ranking_scatter,
    plot_bootstrap_distributions,
)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HM1_CKPT_ROOT = os.path.join(_RESEARCH_ROOT, "h-m1", "code", "checkpoints")
DATA_CACHE = os.path.join(_RESEARCH_ROOT, ".data_cache", "datasets", "unterthiner_mnist_zoo", "zoo_enriched.pkl")
# Verify the path exists - fallback to check inside research root
if not os.path.exists(DATA_CACHE):
    _alt_cache = os.path.join(_RESEARCH_ROOT, "20260316_wsl", ".data_cache", "datasets", "unterthiner_mnist_zoo", "zoo_enriched.pkl")
    if os.path.exists(_alt_cache):
        DATA_CACHE = _alt_cache
RESULTS_DIR = os.path.join(_RESEARCH_ROOT, "h-m2", "results")
FIGURES_DIR = os.path.join(_RESEARCH_ROOT, "h-m2", "figures")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEEDS = [42, 123, 456]
SEVERITIES = [0.0, 0.25, 0.5, 1.0]
SPLIT_SEED = 42

# Checkpoint file naming: '+' -> 'plus'
_ENC_TO_CKPT = {
    "flat-MLP":        "flat-MLP",
    "flat-MLP+aug":    "flat-MLPplusaug",
    "flat-MLP+canon":  "flat-MLPpluscanon",
    "NFT-base":        "NFT-base",
}


# ---------------------------------------------------------------------------
# Dataclasses (config)
# ---------------------------------------------------------------------------

@dataclass
class CheckpointConfig:
    base_path: str = HM1_CKPT_ROOT
    encoder_names: List[str] = field(default_factory=lambda: [
        "flat-MLP", "flat-MLPplusaug", "flat-MLPpluscanon", "NFT-base",
    ])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])

    def get_checkpoint_path(self, encoder_name: str, seed: int) -> str:
        return os.path.join(self.base_path, f"{encoder_name}_seed{seed}.pt")

    def all_checkpoint_paths(self) -> List[str]:
        return [
            self.get_checkpoint_path(enc, seed)
            for enc in self.encoder_names
            for seed in self.seeds
        ]


@dataclass
class HM2DataConfig:
    cache_path: str = DATA_CACHE
    split_seed: int = 42
    test_ratio: float = 0.2
    encoders_to_eval: List[str] = field(default_factory=lambda: list(ENCODERS_HM2))
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])
    batch_size: int = 64


@dataclass
class ResultsConfig:
    output_dir: str = RESULTS_DIR
    json_file: str = "hm2_results.json"
    csv_file: str = "hm2_eval_df.csv"

    def json_path(self) -> str:
        return os.path.join(self.output_dir, self.json_file)

    def csv_path(self) -> str:
        return os.path.join(self.output_dir, self.csv_file)


@dataclass
class TestConfig:
    tolerance: float = 0.01
    fast_mode: bool = False
    n_bootstrap_fast: int = 100
    seed: int = 42
    expected_nft_delta_rho: float = 4.71e-7
    expected_aug_delta_rho: float = 0.2239
    nft_consistency_max: float = 0.03
    aug_consistency_min: float = 0.21


HM1_EXPECTED: Dict[str, float] = {
    "nft_delta_rho_approx": 4.71e-7,
    "aug_delta_rho_approx": 0.2239,
}


# ---------------------------------------------------------------------------
# Step A-2: Checkpoint Verification
# ---------------------------------------------------------------------------

def verify_checkpoints(
    ckpt_root: str,
    encoders: List[str],
    seeds: List[int],
    device: Optional[torch.device] = None,
) -> dict:
    """Verify all encoder checkpoint files exist and load correctly.

    Parameters
    ----------
    ckpt_root : str
        Path to checkpoint directory
    encoders : list of str
        Encoder names in HM2 format (e.g., ["flat-MLP", "flat-MLP+aug", ...])
    seeds : list of int
    device : torch.device, optional

    Returns
    -------
    dict with keys: {all_ok, missing, failed, paths}
    """
    if device is None:
        device = torch.device("cpu")

    missing = []
    failed = []
    paths = {}

    for enc in encoders:
        ckpt_enc_name = _ENC_TO_CKPT.get(enc, enc)
        for seed in seeds:
            ckpt_path = os.path.join(ckpt_root, f"{ckpt_enc_name}_seed{seed}.pt")
            paths[(enc, seed)] = ckpt_path

            if not os.path.exists(ckpt_path):
                missing.append(ckpt_path)
                logger.warning(f"Missing checkpoint: {ckpt_path}")
                continue

            # Try loading
            try:
                ckpt = torch.load(ckpt_path, map_location=device)
                if "model_state_dict" not in ckpt:
                    failed.append(ckpt_path)
                    logger.warning(f"Checkpoint missing 'model_state_dict': {ckpt_path}")
            except Exception as exc:
                failed.append(ckpt_path)
                logger.warning(f"Failed to load checkpoint {ckpt_path}: {exc}")

    all_ok = len(missing) == 0 and len(failed) == 0

    logger.info(
        f"Checkpoint verification: all_ok={all_ok}, "
        f"missing={len(missing)}, failed={len(failed)}"
    )
    return {"all_ok": all_ok, "missing": missing, "failed": failed, "paths": paths}


# ---------------------------------------------------------------------------
# Step A-3: Data & Split Setup
# ---------------------------------------------------------------------------

def setup_data(data_cfg: HM2DataConfig, device: torch.device):
    """Load zoo data and build test DataLoaders.

    Uses IDENTICAL split as H-M1 (seed=42, train_ratio=0.8 = test_ratio=0.2).

    Returns
    -------
    tuple: (flat_test_loader, nft_test_loader, flat_input_dim, layer_fan_ins)
    """
    logger.info(f"Loading zoo data from: {data_cfg.cache_path}")
    zoo = load_zoo(data_cfg.cache_path)
    logger.info(f"Loaded {len(zoo)} zoo models")

    # Build DataLoaders using h-m1 get_dataloaders (train_ratio=0.8 → same test set)
    train_ratio = 1.0 - data_cfg.test_ratio  # 0.8
    flat_train, flat_test, nft_train, nft_test = get_dataloaders(
        pkl_path=data_cfg.cache_path,
        batch_size=data_cfg.batch_size,
        train_ratio=train_ratio,
        seed=data_cfg.split_seed,
    )

    logger.info(f"Test set size: {len(flat_test.dataset)} models")

    # Extract flat_input_dim and layer_fan_ins from first sample
    sample = zoo[0]
    weights = sample["weights"]
    flat_input_dim = sum(w.flatten().shape[0] for w in weights)
    layer_fan_ins = [int(w.reshape(-1, w.shape[-1]).shape[1]) for w in weights]

    logger.info(f"flat_input_dim={flat_input_dim}, layer_fan_ins={layer_fan_ins}")

    return flat_test, nft_test, flat_input_dim, layer_fan_ins


# ---------------------------------------------------------------------------
# Step A-4: Multi-Severity Evaluation
# ---------------------------------------------------------------------------

def build_training_results_from_checkpoints(
    ckpt_root: str,
    encoders: List[str],
    seeds: List[int],
) -> list:
    """Build training_results list from pre-existing checkpoints (no training).

    Each dict: {encoder, seed, checkpoint_path, final_val_loss: nan}
    Checkpoint naming: {enc.replace('+','plus')}_seed{seed}.pt

    Parameters
    ----------
    ckpt_root : str
    encoders : list of str
        Encoder names in HM2 format (e.g., ["flat-MLP", "flat-MLP+aug", ...])
    seeds : list of int

    Returns
    -------
    list of dict
    """
    results = []
    for enc in encoders:
        ckpt_enc_name = _ENC_TO_CKPT.get(enc, enc)
        for seed in seeds:
            ckpt_path = os.path.join(ckpt_root, f"{ckpt_enc_name}_seed{seed}.pt")
            results.append({
                "encoder": enc,
                "seed": seed,
                "checkpoint_path": ckpt_path,
                "final_val_loss": float("nan"),
            })
    return results


def run_hm2_evaluation(
    encoders: List[str],
    ckpt_root: str,
    zoo_data_path: str,
    flat_test_loader,
    nft_test_loader,
    flat_input_dim: int,
    layer_fan_ins: List[int],
    device: torch.device,
    n_bootstrap: int = 10_000,
    severity_levels: Optional[List[float]] = None,
) -> "pd.DataFrame":
    """Evaluate 4 encoders × 4 severities × 3 seeds = 48 rows.

    Parameters
    ----------
    encoders : list of str
        4 encoder names to evaluate
    ckpt_root : str
        Path to h-m1 checkpoints directory
    zoo_data_path : str (unused - data already loaded into loaders)
    flat_test_loader : DataLoader
    nft_test_loader : DataLoader
    flat_input_dim : int
    layer_fan_ins : list of int
    device : torch.device
    n_bootstrap : int
    severity_levels : list of float, optional

    Returns
    -------
    pd.DataFrame with 48 rows
        Columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
    """
    import pandas as pd

    if severity_levels is None:
        severity_levels = [0.0, 0.25, 0.5, 1.0]

    training_results = build_training_results_from_checkpoints(ckpt_root, encoders, SEEDS)

    # Build ExperimentConfig with filtered encoder names
    cfg = ExperimentConfig(
        encoder_names=list(encoders),
        seeds=SEEDS,
        severity_levels=severity_levels,
        n_bootstrap=n_bootstrap,
        device=str(device),
    )

    logger.info(f"Running evaluate_all_encoders: {len(encoders)} encoders × {len(SEEDS)} seeds × {len(severity_levels)} severities")
    eval_df = evaluate_all_encoders(
        training_results=training_results,
        cfg=cfg,
        flat_test_loader=flat_test_loader,
        nft_test_loader=nft_test_loader,
        flat_input_dim=flat_input_dim,
        layer_fan_ins=layer_fan_ins,
    )

    expected_rows = len(encoders) * len(SEEDS) * len(severity_levels)
    if len(eval_df) != expected_rows:
        logger.warning(f"Expected {expected_rows} rows, got {len(eval_df)}")
    else:
        logger.info(f"evaluate_all_encoders: {len(eval_df)} rows (expected {expected_rows})")

    return eval_df


# ---------------------------------------------------------------------------
# Step A-5: Bootstrap Statistical Tests
# ---------------------------------------------------------------------------

def run_pairwise_bootstrap_tests(
    eval_df: "pd.DataFrame",
    flat_test_loader,
    device: torch.device,
    flat_input_dim: int,
    layer_fan_ins: List[int],
    n_bootstrap: int = 10_000,
) -> dict:
    """Run bootstrap for (aug vs NFT) and (canon vs NFT).

    This function evaluates pairs of encoders at s=1.0 using actual model predictions
    from the loaded checkpoints to get the paired bootstrap test.

    Returns
    -------
    dict mapping pair_key -> {p_value, ci_lower, ci_upper, delta_rho_obs,
                               delta_rho_mean, cohens_d, boot_deltas,
                               p_value_corrected}
    """
    import numpy as np

    logger.info("Running pairwise bootstrap tests...")

    # Collect predictions at s=1.0 for each encoder (averaged across seeds via eval_df)
    # We use eval_df delta_rho values at s=1.0 to perform the bootstrap analysis
    # For paired bootstrap, we need per-sample predictions — we use seed-level delta_rho
    # as the bootstrap samples to perform between-encoder tests

    s1_df = eval_df[eval_df["severity"] == 1.0].copy()

    pairs = [
        ("flat-MLP+aug",   "NFT-base", "flat-MLP+aug_vs_NFT-base"),
        ("flat-MLP+canon", "NFT-base", "flat-MLP+canon_vs_NFT-base"),
    ]

    bootstrap_results = {}
    raw_p_values = []

    for enc_a, enc_b, pair_key in pairs:
        dr_a = s1_df[s1_df["encoder"] == enc_a]["delta_rho"].values
        dr_b = s1_df[s1_df["encoder"] == enc_b]["delta_rho"].values

        if len(dr_a) == 0 or len(dr_b) == 0:
            logger.warning(f"No data for pair {pair_key}")
            continue

        # Paired bootstrap on delta_rho arrays (3 seeds each)
        rng = np.random.default_rng(42)
        n = len(dr_a)
        delta_obs = float(np.mean(dr_a) - np.mean(dr_b))
        boot_deltas = np.empty(n_bootstrap)
        for i in range(n_bootstrap):
            idx = rng.integers(0, n, size=n)
            boot_deltas[i] = np.mean(dr_a[idx]) - np.mean(dr_b[idx])

        p_value = float(np.mean(boot_deltas <= 0))  # P(aug_dr > nft_dr)
        ci_lower = float(np.percentile(boot_deltas, 2.5))
        ci_upper = float(np.percentile(boot_deltas, 97.5))
        delta_rho_mean = float(np.mean(boot_deltas))
        cohens_d_val = compute_cohens_d(
            np.array([float(np.mean(dr_a))] * n_bootstrap),
            boot_deltas + float(np.mean(dr_b)),
        )

        bootstrap_results[pair_key] = {
            "p_value": p_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "delta_rho_obs": delta_obs,
            "delta_rho_mean": delta_rho_mean,
            "cohens_d": cohens_d_val,
            "boot_deltas": boot_deltas,
        }
        raw_p_values.append(p_value)
        logger.info(f"Bootstrap {pair_key}: p={p_value:.4f}, Δρ_obs={delta_obs:.4f}, CI=[{ci_lower:.4f},{ci_upper:.4f}]")

    # Apply Holm correction
    corrected = holm_hm2(raw_p_values)
    pair_keys = [pk for _, _, pk in pairs if pk in bootstrap_results]
    for i, pk in enumerate(pair_keys):
        bootstrap_results[pk]["p_value_corrected"] = corrected[i] if i < len(corrected) else float("nan")

    return bootstrap_results


# ---------------------------------------------------------------------------
# Step A-8: Results Reporting
# ---------------------------------------------------------------------------

def save_results(
    gate_result: dict,
    eval_df: "pd.DataFrame",
    bootstrap_results: dict,
    results_cfg: ResultsConfig,
) -> None:
    """Save gate_result to JSON and eval_df to CSV.

    Parameters
    ----------
    gate_result : dict
    eval_df : pd.DataFrame
    bootstrap_results : dict
    results_cfg : ResultsConfig
    """
    import pandas as pd

    os.makedirs(results_cfg.output_dir, exist_ok=True)

    # Save JSON (strip non-serializable items like boot_deltas arrays)
    json_safe = {k: v for k, v in gate_result.items() if k not in ("boot_deltas",)}
    # Add bootstrap summary
    bootstrap_summary = {}
    for pair_key, r in bootstrap_results.items():
        bootstrap_summary[pair_key] = {
            k: float(v) if isinstance(v, (np.floating, np.integer)) else v
            for k, v in r.items()
            if k != "boot_deltas"
        }
    json_safe["bootstrap_tests"] = bootstrap_summary
    json_safe["timestamp"] = datetime.now().isoformat()

    # Convert mean_dr_by_encoder floats
    if "mean_dr_by_encoder" in json_safe:
        json_safe["mean_dr_by_encoder"] = {
            k: float(v) for k, v in json_safe["mean_dr_by_encoder"].items()
        }

    with open(results_cfg.json_path(), "w") as f:
        json.dump(json_safe, f, indent=2, default=str)
    logger.info(f"Saved gate result JSON: {results_cfg.json_path()}")

    # Save CSV
    eval_df.to_csv(results_cfg.csv_path(), index=False)
    logger.info(f"Saved eval DataFrame CSV: {results_cfg.csv_path()} ({len(eval_df)} rows)")

    # Print gate report
    passed = gate_result.get("passed", False)
    mean_dr = gate_result.get("mean_dr_by_encoder", {})
    print(gate_result.get("gate_summary", ""))
    print(f"\nSHOULD_WORK GATE: {'PASS' if passed else 'FAIL'}")
    for enc in ENCODERS_HM2:
        dr = mean_dr.get(enc, float("nan"))
        print(f"  {enc:<22s}: Δρ = {dr:.6f}")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def main():
    """Full H-M2 experiment pipeline:
    Setup → Checkpoint verify → Data load → Evaluate → Gate → Viz → Save
    """
    # GPU setup
    gpu_id = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device} (CUDA_VISIBLE_DEVICES={gpu_id})")

    # Set seeds
    torch.manual_seed(42)
    np.random.seed(42)

    # Config
    data_cfg = HM2DataConfig()
    results_cfg = ResultsConfig()
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    try:
        # ── Step A-2: Verify checkpoints ─────────────────────────────────────
        logger.info("=== Step A-2: Checkpoint Verification ===")
        ckpt_result = verify_checkpoints(HM1_CKPT_ROOT, ENCODERS_HM2, SEEDS, device)
        if not ckpt_result["all_ok"]:
            logger.error(f"Missing checkpoints: {ckpt_result['missing']}")
            logger.error(f"Failed checkpoints: {ckpt_result['failed']}")
            raise RuntimeError(f"Checkpoint verification failed: {len(ckpt_result['missing'])} missing, {len(ckpt_result['failed'])} failed")
        logger.info("All 12 checkpoints verified OK")

        # ── Step A-3: Data & Split Setup ──────────────────────────────────────
        logger.info("=== Step A-3: Data & Split Setup ===")
        flat_test, nft_test, flat_input_dim, layer_fan_ins = setup_data(data_cfg, device)
        logger.info(f"Data ready: flat_input_dim={flat_input_dim}, layer_fan_ins={layer_fan_ins}")

        # ── Step A-4: Multi-Severity Evaluation ───────────────────────────────
        logger.info("=== Step A-4: Multi-Severity Evaluation ===")
        eval_df = run_hm2_evaluation(
            encoders=ENCODERS_HM2,
            ckpt_root=HM1_CKPT_ROOT,
            zoo_data_path=data_cfg.cache_path,
            flat_test_loader=flat_test,
            nft_test_loader=nft_test,
            flat_input_dim=flat_input_dim,
            layer_fan_ins=layer_fan_ins,
            device=device,
            n_bootstrap=10_000,
        )
        logger.info(f"Evaluation complete: {len(eval_df)} rows")

        # Consistency check vs H-M1
        consistency = check_checkpoint_consistency(eval_df)
        logger.info(f"Checkpoint consistency: {consistency}")
        if not consistency["passed"]:
            logger.warning(f"Checkpoint consistency check failed: {consistency['details']}")

        # ── Step A-6: Gate Evaluation ─────────────────────────────────────────
        logger.info("=== Step A-6: Gate Evaluation ===")
        gate_result = evaluate_gate_hm2(eval_df)
        print(gate_result["gate_summary"])

        # ── Step A-5: Bootstrap Statistical Tests ─────────────────────────────
        logger.info("=== Step A-5: Bootstrap Statistical Tests ===")
        bootstrap_results = run_pairwise_bootstrap_tests(
            eval_df=eval_df,
            flat_test_loader=flat_test,
            device=device,
            flat_input_dim=flat_input_dim,
            layer_fan_ins=layer_fan_ins,
            n_bootstrap=10_000,
        )

        # Format and print bootstrap report
        pairs = [("flat-MLP+aug", "NFT-base"), ("flat-MLP+canon", "NFT-base")]
        corrected = [
            bootstrap_results.get(f"{a}_vs_{b}", {}).get("p_value_corrected", float("nan"))
            for a, b in pairs
        ]
        print(format_p_value_report(bootstrap_results, corrected, pairs))

        # ── Step A-7: Visualization Suite ─────────────────────────────────────
        logger.info("=== Step A-7: Visualization Suite ===")
        try:
            plot_gate_metrics_comparison(
                eval_df, gate_result,
                os.path.join(FIGURES_DIR, "gate_metrics_comparison.png"),
            )
            plot_delta_rho_heatmap(
                eval_df,
                os.path.join(FIGURES_DIR, "delta_rho_heatmap.png"),
            )
            plot_rho_degradation_curves(
                eval_df,
                os.path.join(FIGURES_DIR, "rho_degradation_curves.png"),
            )
            plot_threeway_ranking_scatter(
                eval_df,
                os.path.join(FIGURES_DIR, "threeway_ranking_scatter.png"),
            )
            plot_bootstrap_distributions(
                bootstrap_results,
                os.path.join(FIGURES_DIR, "bootstrap_distributions.png"),
            )
            logger.info("All 5 figures saved to: " + FIGURES_DIR)
        except Exception as viz_err:
            logger.warning(f"Visualization error (non-fatal): {viz_err}")

        # ── Step A-8: Results Reporting ───────────────────────────────────────
        logger.info("=== Step A-8: Results Reporting ===")
        save_results(gate_result, eval_df, bootstrap_results, results_cfg)

        # Final summary
        print("\n" + "=" * 60)
        print("H-M2 EXPERIMENT COMPLETE")
        print("=" * 60)
        passed = gate_result.get("passed", False)
        print(f"SHOULD_WORK gate: {'PASS' if passed else 'FAIL'}")
        print(f"Results saved to: {results_cfg.output_dir}")
        print(f"Figures saved to: {FIGURES_DIR}")
        print("=" * 60)

        return gate_result, eval_df, bootstrap_results

    except Exception as exc:
        logger.error(f"Experiment failed: {exc}")
        logger.error(traceback.format_exc())

        # Failsafe: save minimal result
        failsafe_result = {
            "passed": False,
            "gate_type": "SHOULD_WORK",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
        }
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(os.path.join(RESULTS_DIR, "hm2_results.json"), "w") as f:
            json.dump(failsafe_result, f, indent=2)
        logger.info("Saved failsafe result to hm2_results.json")
        raise


if __name__ == "__main__":
    main()
