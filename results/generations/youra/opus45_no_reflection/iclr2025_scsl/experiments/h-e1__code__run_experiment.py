import os
import yaml
import torch
import numpy as np

from config import ExperimentConfig
from data import download_waterbirds, WaterbirdsDataset
from features import load_clip_model, extract_features, cache_features, load_cached_features
from cv_probe import run_cv_analysis
from evaluate import compute_metrics, check_gate
from visualize import plot_gate_comparison, plot_cv_distribution, plot_roc_curve, plot_trajectories


def main(config_path: str = "config.yaml") -> dict:
    cfg = ExperimentConfig.from_yaml(config_path)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)

    device = cfg.features.device if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    data_root = download_waterbirds(cfg.data.data_dir)

    model, preprocess = load_clip_model(device)

    cache_path = cfg.features.cache_path
    os.makedirs(os.path.dirname(cache_path) if os.path.dirname(cache_path) else ".", exist_ok=True)

    if os.path.exists(cache_path):
        print(f"Loading cached features from {cache_path}")
        features, y, place = load_cached_features(cache_path)
    else:
        print("Extracting CLIP features...")
        dataset = WaterbirdsDataset(data_root, "train", preprocess)
        features, y, place = extract_features(dataset, model, device, cfg.features.batch_size)
        cache_features(cache_path, features, y, place)
        print(f"Cached features to {cache_path}")

    print(f"Features shape: {features.shape}, y: {y.shape}, place: {place.shape}")

    print("Running CV analysis...")
    result = run_cv_analysis(
        features, y, place,
        n_subsets=cfg.cv_probe.n_subsets,
        subset_frac=cfg.cv_probe.subset_frac,
        n_epochs=cfg.cv_probe.n_epochs,
        seed=cfg.seed,
    )

    print(f"Background CV: {result['background_cv']:.4f}")
    print(f"Bird Type CV: {result['bird_type_cv']:.4f}")

    cv_values = [result["background_cv"], result["bird_type_cv"]]
    ground_truth_spurious = [1, 0]

    metrics = compute_metrics(cv_values, ground_truth_spurious)
    gate_pass = check_gate(metrics, cfg.evaluate.auc_threshold)

    print(f"AUC: {metrics['auc']:.4f}")
    print(f"Best F1: {metrics['best_f1']:.4f}")
    print(f"Gate Pass (AUC >= {cfg.evaluate.auc_threshold}): {gate_pass}")

    os.makedirs(cfg.output.figures_dir, exist_ok=True)

    plot_gate_comparison(
        metrics["auc"],
        cfg.evaluate.auc_threshold,
        os.path.join(cfg.output.figures_dir, "gate_comparison.png")
    )

    plot_cv_distribution(
        {"background": result["background_cv"], "bird_type": result["bird_type_cv"]},
        os.path.join(cfg.output.figures_dir, "cv_distribution.png")
    )

    plot_roc_curve(
        cv_values,
        ground_truth_spurious,
        os.path.join(cfg.output.figures_dir, "roc_curve.png")
    )

    plot_trajectories(
        result["trajectories"],
        os.path.join(cfg.output.figures_dir, "trajectories.png")
    )

    results = {
        "auc": metrics["auc"],
        "best_f1": metrics["best_f1"],
        "gate_pass": gate_pass,
        "background_cv": result["background_cv"],
        "bird_type_cv": result["bird_type_cv"],
        "threshold": cfg.evaluate.auc_threshold,
    }

    with open(cfg.output.results_path, "w") as f:
        yaml.dump(results, f)

    print(f"Results saved to {cfg.output.results_path}")
    print(f"Figures saved to {cfg.output.figures_dir}/")

    return results


if __name__ == "__main__":
    main()
