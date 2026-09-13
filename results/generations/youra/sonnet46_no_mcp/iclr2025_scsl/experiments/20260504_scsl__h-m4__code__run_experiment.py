import argparse
import os
import sys

from config import load_config, ExperimentConfig
from train_backbone import BackboneTrainer
from feature_extractor import FeatureExtractor
from dfr_module import DFRModule
from correlation_analyzer import CorrelationAnalyzer
from visualizer import Visualizer
from results_exporter import ResultsExporter

DEFAULT_CONFIG = "configs/waterbirds.yaml"
DEFAULT_DEVICE = "cuda"


def run(config_path: str, device: str) -> dict:
    cfg = load_config(config_path)

    # Create output directories
    os.makedirs(cfg.paths.results_dir, exist_ok=True)
    os.makedirs(cfg.paths.figures_dir, exist_ok=True)
    os.makedirs(cfg.paths.checkpoint_dir, exist_ok=True)

    trainer = BackboneTrainer(cfg, device)
    extractor = FeatureExtractor(device=device)
    dfr = DFRModule(cfg)
    analyzer = CorrelationAnalyzer(cfg)
    viz = Visualizer(cfg)
    exporter = ResultsExporter(cfg)

    results_per_seed = {}
    feature_cache = {}  # (seed, epoch) -> (val_feats, val_labels, val_groups, test_feats, test_labels, test_groups)

    # Phase A: Training
    print("\n=== Phase A: Training Backbones ===")
    for seed in cfg.train.seeds:
        print(f"\nTraining seed {seed}...")
        ckpt_map = trainer.train_seed(seed)
        results_per_seed[seed] = {}
        print(f"Seed {seed} checkpoints: {list(ckpt_map.keys())}")

    # Phase B: Feature extraction + DFR evaluation
    print("\n=== Phase B: Feature Extraction + DFR Evaluation ===")
    for seed in cfg.train.seeds:
        extractor_seed = FeatureExtractor(device=device)
        for epoch in cfg.analysis.conditions:
            ckpt_path = os.path.abspath(os.path.join(
                cfg.paths.checkpoint_dir, f"seed_{seed}", f"epoch_{epoch:03d}.pt"
            ))
            if not os.path.exists(ckpt_path):
                print(f"WARNING: checkpoint missing: {ckpt_path}, skipping")
                continue

            key = (seed, epoch)
            if key not in feature_cache:
                print(f"Extracting features: seed={seed}, epoch={epoch}")
                val_feats, val_labels, val_groups = extractor_seed.extract_split(
                    cfg.train.data_root, "val", cfg, ckpt_path
                )
                test_feats, test_labels, test_groups = extractor_seed.extract_split(
                    cfg.train.data_root, "test", cfg, ckpt_path
                )
                feature_cache[key] = (val_feats, val_labels, val_groups,
                                      test_feats, test_labels, test_groups)

            val_feats, val_labels, val_groups, test_feats, test_labels, test_groups = feature_cache[key]
            metrics = dfr.evaluate_checkpoint(
                ckpt_path,
                val_feats, val_labels,
                test_feats, test_labels, test_groups,
                device,
            )
            results_per_seed[seed][epoch] = metrics

    # Phase C: Analysis
    print("\n=== Phase C: Correlation Analysis ===")
    aggregated = analyzer.aggregate_across_seeds(results_per_seed)
    # Skip Pearson if fewer than 2 conditions (e.g. dry run)
    if len(aggregated) < 2:
        print("WARNING: fewer than 2 conditions — skipping Pearson r (dry run mode)")
        epochs = sorted(aggregated.keys())
        corr = {
            "pearson_r": float("nan"),
            "pearson_p_twotailed": float("nan"),
            "pearson_p_onetailed": float("nan"),
            "epochs_past_tstar": [e - cfg.analysis.t_star_mean for e in epochs],
            "improvements": [aggregated[e]["mean_wga_improvement"] for e in epochs],
            "epochs": epochs,
        }
        gate = {"gate_passed": None, "pearson_r": float("nan"),
                "threshold": cfg.analysis.pearson_r_threshold,
                "decision": "SKIPPED_DRY_RUN", "note": "Dry run: only 1 condition"}
        monotonicity = {"is_monotonic": None, "n_positive_diffs": 0, "n_diffs": 0, "positive_fraction": 0.0}
    else:
        corr = analyzer.compute_pearson(aggregated, cfg.analysis.t_star_mean)
        gate = analyzer.evaluate_gate(corr["pearson_r"])
        monotonicity = analyzer.verify_monotonicity(corr["improvements"])
    print(f"Pearson r={corr['pearson_r']:.4f}, p(one-tailed)={corr['pearson_p_onetailed']:.4f}")
    print(f"Gate: {gate['decision']}")
    print(f"Monotonic: {monotonicity['is_monotonic']} ({monotonicity['n_positive_diffs']}/{monotonicity['n_diffs']} positive diffs)")

    # Phase D: Visualize + Export
    print("\n=== Phase D: Visualization + Export ===")
    fig_paths = viz.save_all(results_per_seed, aggregated, corr, cfg.analysis.t_star_mean)
    json_path = exporter.save_json(results_per_seed, aggregated, corr, gate, fig_paths)
    exporter.print_summary(corr, gate)

    return {
        "results_per_seed": results_per_seed,
        "aggregated": aggregated,
        "correlation": corr,
        "gate": gate,
        "monotonicity": monotonicity,
        "figure_paths": fig_paths,
        "json_path": json_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M4: DFR Efficacy vs Backbone Training Depth")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    args = parser.parse_args()
    run(args.config, args.device)
