"""
H-M3: Transition Epoch t* Reproducibility Analysis
Orchestrates: load -> analyze -> validate -> visualize -> export
"""
import argparse
import json
import logging
import os
import sys
import time

# Ensure the code directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, validate_config
from data_loader import DeltaCurveLoader
from analyzer import TransitionEpochAnalyzer
from statistical_validator import StatisticalValidator
from visualizer import Visualizer
from results_exporter import ResultsExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("h-m3")


def main(config_path: str = "configs/waterbirds.yaml") -> dict:
    t0 = time.time()
    logger.info(f"=== H-M3: Transition Epoch t* Reproducibility Analysis ===")
    logger.info(f"Config: {config_path}")

    # Stage 1: Load and validate config
    t1 = time.time()
    cfg = load_config(config_path)
    validate_config(cfg)
    logger.info(f"[1/6] Config loaded in {time.time()-t1:.2f}s")

    # Stage 2: Load delta(t) curves from H-E1
    t2 = time.time()
    loader = DeltaCurveLoader(cfg)
    delta_curves = loader.load()
    logger.info(f"[2/6] Delta curves loaded ({len(delta_curves)} seeds) in {time.time()-t2:.2f}s")

    # Stage 3: Analyze t* across seeds
    t3 = time.time()
    analyzer = TransitionEpochAnalyzer(cfg)
    analysis_results = analyzer.analyze_across_seeds(delta_curves)
    logger.info(
        f"[3/6] Analysis complete: mean_t*={analysis_results['mean_t_star']:.2f}, "
        f"std_t*={analysis_results['std_t_star']:.2f} in {time.time()-t3:.2f}s"
    )

    # Stage 4: Statistical validation and gate evaluation
    t4 = time.time()
    validator = StatisticalValidator(cfg)
    validation_results = validator.run_full_validation(analysis_results)
    logger.info(
        f"[4/6] Gate: {validation_results['gate_decision']} "
        f"(std={validation_results['std_t_star']:.2f} < {cfg.analysis.std_gate_threshold}) "
        f"in {time.time()-t4:.2f}s"
    )

    # Stage 5: Visualize
    t5 = time.time()
    os.makedirs(cfg.paths.figures_dir, exist_ok=True)
    viz = Visualizer(cfg)
    figure_paths = viz.save_all(delta_curves, analysis_results, validation_results)
    logger.info(f"[5/6] {len(figure_paths)} figures saved in {time.time()-t5:.2f}s")

    # Stage 6: Export results
    t6 = time.time()
    exporter = ResultsExporter(cfg)
    json_path = exporter.save_json(analysis_results, validation_results, figure_paths)
    csv_path = exporter.save_csv(delta_curves, cfg.analysis.checkpoint_interval)
    exporter.print_summary(analysis_results, validation_results)
    logger.info(f"[6/6] Results exported in {time.time()-t6:.2f}s")

    total = time.time() - t0
    logger.info(f"=== EXPERIMENT COMPLETE in {total:.2f}s ===")

    results = {
        "analysis": analysis_results,
        "validation": validation_results,
        "figures": figure_paths,
        "json_path": json_path,
        "csv_path": csv_path,
    }

    # Also save to outputs/ for pipeline compatibility
    os.makedirs("outputs", exist_ok=True)
    outputs_json = os.path.join("outputs", "h-m3_results.json")
    with open(outputs_json, "w") as f:
        def conv(o):
            import numpy as np
            if isinstance(o, (np.integer,)): return int(o)
            if isinstance(o, (np.floating,)): return float(o)
            if isinstance(o, np.ndarray): return o.tolist()
            if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
            if isinstance(o, list): return [conv(v) for v in o]
            return o
        json.dump(conv(results["validation"] | {"analysis": conv(analysis_results)}), f, indent=2)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M3: t* Reproducibility Analysis")
    parser.add_argument("--config", default="configs/waterbirds.yaml",
                        help="Path to config YAML file")
    args = parser.parse_args()
    main(args.config)
