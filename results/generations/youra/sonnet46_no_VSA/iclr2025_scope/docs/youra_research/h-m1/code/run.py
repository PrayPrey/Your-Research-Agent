import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from experiment import Experiment
from analysis import compute_scaling_metrics


def main() -> None:
    cfg = Config()
    # Scale down for feasibility: 50 samples × 2000 steps per fit
    # Statistical note: 50 samples × 32 layers = 1600 measurements per N, sufficient for robust slope regression
    cfg.n_samples = 50
    cfg.n_opt_steps = 500
    # N=8192 OOMs with eager attention on H100 (requires ~200GB+ for N×N all-heads softmax)
    # Use N up to 4096 — sufficient for slope estimation over 4 points
    cfg.target_lengths = [512, 1024, 2048, 4096]

    # Use absolute paths relative to h-m1 dir
    import os
    h_m1_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg.results_dir = os.path.join(h_m1_dir, "results")
    cfg.figures_dir = os.path.join(h_m1_dir, "figures")

    exp = Experiment(cfg)
    results = exp.run()
    gate_result = compute_scaling_metrics(
        results["errors_by_N"],
        slope_threshold=cfg.gate_slope_threshold,
        pct90_threshold=cfg.gate_pct90_threshold,
    )
    exp.save_and_report(results, gate_result)


if __name__ == "__main__":
    main()
