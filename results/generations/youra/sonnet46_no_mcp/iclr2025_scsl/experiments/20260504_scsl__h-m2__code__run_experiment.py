import argparse
import json
import os
import sys
import traceback
from datetime import datetime

import numpy as np


def make_serializable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(x) for x in obj]
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    return obj

from config import load_config, ExperimentConfig
from data_pipeline.patch_extractor import PatchExtractor
from data_pipeline.waterbirds_loader import extract_waterbirds_patches, get_waterbirds_feature_loader
from data_pipeline.celeba_loader import extract_celeba_patches, get_celeba_feature_loader
from feature_extractor.resnet_extractor import ResNetExtractor
from complexity_metrics.fft_metric import compute_fft_metric
from complexity_metrics.variance_metric import compute_variance_metric
from complexity_metrics.separability_metric import compute_separability_metric
from analysis.statistical_tests import evaluate_gate, compute_complexity_delta_ci
from analysis.mechanism_verifier import verify_mechanism_activated
from visualization.figures import generate_all_figures


def run_dataset(cfg: ExperimentConfig, dataset: str, extractor_model: ResNetExtractor) -> dict:
    patch_extractor = PatchExtractor(patch_size=cfg.data.patch_size)
    n_samples_list = cfg.metric.n_samples_list
    seeds = cfg.metric.seeds

    print(f"\n{'='*60}")
    print(f"Processing dataset: {dataset.upper()}")
    print(f"{'='*60}")

    if dataset == "waterbirds":
        print("Extracting Waterbirds patches...")
        patches = extract_waterbirds_patches(
            root=cfg.data.waterbirds_root,
            extractor=patch_extractor,
            split="train",
            use_masks=cfg.data.use_segmentation_masks,
        )
    elif dataset == "celeba":
        print("Extracting CelebA patches...")
        patches = extract_celeba_patches(
            root=cfg.data.celeba_root,
            extractor=patch_extractor,
            samples_per_group=cfg.data.celeba_samples_per_group,
            split="train",
        )
    else:
        raise ValueError(f"Unknown dataset: {dataset}")

    spurious_patches = patches["spurious_patches"]
    core_patches = patches["core_patches"]
    spurious_labels = patches["spurious_labels"]
    core_labels = patches["core_labels"]

    print(f"Patches: spurious={spurious_patches.shape}, core={core_patches.shape}")

    # Metric 1: FFT
    print("Computing FFT complexity metric...")
    fft_result = compute_fft_metric(spurious_patches, core_patches)
    print(f"  FFT: spurious_mean={fft_result['spurious_mean_freq']:.4f}, "
          f"core_mean={fft_result['core_mean_freq']:.4f}, "
          f"p={fft_result['p_value']:.4f}, direction_correct={fft_result['direction_correct']}")

    # Feature extraction for metrics 2 & 3
    print("Extracting ResNet-50 layer-4 features...")
    spurious_feats, core_feats = extractor_model.extract_split_features(
        spurious_patches, core_patches, batch_size=cfg.data.batch_size
    )
    print(f"  Features: spurious={spurious_feats.shape}, core={core_feats.shape}")

    # Metric 2: Intra-class variance
    print("Computing intra-class variance metric...")
    variance_result = compute_variance_metric(spurious_feats, core_feats)
    print(f"  Variance: spurious={variance_result['var_spurious']:.2f}, "
          f"core={variance_result['var_core']:.2f}, "
          f"p={variance_result['p_value']:.4f}, direction_correct={variance_result['direction_correct']}")

    # Metric 3: Linear separability
    print("Computing linear separability metric (this may take a while)...")
    all_feats = np.concatenate([spurious_feats, core_feats], axis=0)
    all_spurious_labels = np.concatenate([
        spurious_labels,
        spurious_labels[:len(core_feats)]  # pad if needed
    ], axis=0)[:len(all_feats)]
    all_core_labels = np.concatenate([
        core_labels,
        core_labels[:len(spurious_feats)]
    ], axis=0)[:len(all_feats)]

    separability_result = compute_separability_metric(
        features=all_feats,
        spurious_labels=all_spurious_labels,
        core_labels=all_core_labels,
        n_samples_list=n_samples_list,
        seeds=seeds,
    )
    print(f"  Separability: spurious_auc={separability_result['spurious_auc']:.4f}, "
          f"core_auc={separability_result['core_auc']:.4f}, "
          f"p={separability_result['p_value']:.4f}, direction_correct={separability_result['direction_correct']}")

    # Bootstrap CI for FFT delta
    fft_ci = compute_complexity_delta_ci(
        np.array(fft_result["spurious_freqs"]),
        np.array(fft_result["core_freqs"]),
    )

    return {
        "fft": fft_result,
        "variance": variance_result,
        "separability": separability_result,
        "fft_ci": fft_ci,
        "n_spurious_patches": len(spurious_patches),
        "n_core_patches": len(core_patches),
        "spurious_feats_shape": list(spurious_feats.shape),
        "core_feats_shape": list(core_feats.shape),
        "patches": patches,
        "spurious_feats": spurious_feats,
        "core_feats": core_feats,
    }


def main(config_path: str, device: str) -> dict:
    print(f"Loading config from {config_path}")
    cfg = load_config(config_path)
    cfg.device = device

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    partial_results = {
        "hypothesis_id": "h-m2",
        "started_at": datetime.now().isoformat(),
        "completed_metrics": [],
        "failure_reason": None,
    }

    try:
        print(f"Initializing ResNet-50 extractor on {device}...")
        extractor_model = ResNetExtractor(device=device)

        # Run Waterbirds
        wb_result = run_dataset(cfg, "waterbirds", extractor_model)
        partial_results["completed_metrics"].append("waterbirds")
        partial_results["waterbirds"] = {k: v for k, v in wb_result.items()
                                          if k not in ("patches", "spurious_feats", "core_feats")}

        # Run CelebA
        try:
            cb_result = run_dataset(cfg, "celeba", extractor_model)
            partial_results["completed_metrics"].append("celeba")
            partial_results["celeba"] = {k: v for k, v in cb_result.items()
                                          if k not in ("patches", "spurious_feats", "core_feats")}
        except Exception as e:
            print(f"WARNING: CelebA failed: {e}. Continuing with Waterbirds only.")
            cb_result = {
                "fft": {"direction_correct": False, "p_value": 1.0, "spurious_mean_freq": 0, "core_mean_freq": 0},
                "variance": {"direction_correct": False, "p_value": 1.0, "var_spurious": 0, "var_core": 0},
                "separability": {"direction_correct": False, "p_value": 1.0, "spurious_auc": 0, "core_auc": 0,
                                 "spurious_curve": {}, "core_curve": {}},
                "n_spurious_patches": 0,
                "n_core_patches": 0,
                "spurious_feats_shape": [0, 2048],
                "spurious_feats": np.zeros((1, 2048)),
                "core_feats": np.zeros((1, 2048)),
                "patches": {"spurious_patches": np.zeros((1, 64, 64, 3), dtype=np.uint8),
                            "core_patches": np.zeros((1, 64, 64, 3), dtype=np.uint8)},
            }

        # Gate evaluation
        print("\nEvaluating gate...")
        gate_result = evaluate_gate(wb_result, cb_result, alpha=cfg.metric.alpha)
        print(f"Gate: {gate_result['gate_label']} "
              f"({gate_result['n_metrics_pass_waterbirds']}/3 metrics pass on Waterbirds)")

        # Mechanism verification
        mechanism_input = {
            "n_spurious_patches": wb_result["n_spurious_patches"],
            "n_core_patches": wb_result["n_core_patches"],
            "spurious_feats_shape": wb_result["spurious_feats_shape"],
            "fft": wb_result["fft"],
        }
        activated, indicators = verify_mechanism_activated(mechanism_input)
        print(f"Mechanism activated: {activated}, indicators: {indicators}")

        # Generate figures
        print("\nGenerating figures...")
        # Prepare serializable results for figures
        wb_for_figs = {k: v for k, v in wb_result.items() if k not in ("patches", "spurious_feats", "core_feats")}
        cb_for_figs = {k: v for k, v in cb_result.items() if k not in ("patches", "spurious_feats", "core_feats")}

        figure_paths = generate_all_figures(
            waterbirds_patches=wb_result["patches"],
            celeba_patches=cb_result["patches"],
            spurious_feats=wb_result["spurious_feats"],
            core_feats=wb_result["core_feats"],
            waterbirds_results=wb_for_figs,
            celeba_results=cb_for_figs,
            gate_result=gate_result,
            figures_dir=cfg.figures_dir,
        )
        print(f"Figures saved: {list(figure_paths.keys())}")

        # Build full results
        full_results = {
            "hypothesis_id": "h-m2",
            "completed_at": datetime.now().isoformat(),
            "gate_pass": gate_result["gate_pass"],
            "gate_label": gate_result["gate_label"],
            "n_metrics_pass_waterbirds": gate_result["n_metrics_pass_waterbirds"],
            "n_metrics_pass_celeba": gate_result["n_metrics_pass_celeba"],
            "mechanism_activated": activated,
            "mechanism_indicators": indicators,
            "waterbirds": make_serializable(wb_for_figs),
            "celeba": make_serializable(cb_for_figs),
            "gate_result": make_serializable(gate_result),
            "figure_paths": figure_paths,
        }

        results_path = os.path.join(cfg.results_dir, "results_h_m2.json")
        with open(results_path, "w") as f:
            json.dump(full_results, f, indent=2)
        print(f"\nResults saved to {results_path}")
        print("\nEXPERIMENT COMPLETE")
        return full_results

    except Exception as e:
        partial_results["failure_reason"] = str(e)
        partial_results["traceback"] = traceback.format_exc()
        os.makedirs(cfg.results_dir, exist_ok=True)
        partial_path = os.path.join(cfg.results_dir, "partial_results_h_m2.json")
        with open(partial_path, "w") as f:
            json.dump(make_serializable(partial_results), f, indent=2)
        print(f"ERROR: {e}")
        print(f"Partial results saved to {partial_path}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M2: Feature Complexity Measurement")
    parser.add_argument("--config", default="configs/experiment.yaml")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    main(args.config, args.device)
