"""H-M4: Main experiment - compare SNR between fine-always and fine-gated policies."""
import sys
import os
import json
import torch
import numpy as np
import importlib.util

H_M4_CODE = os.path.dirname(os.path.abspath(__file__))
H_M3_CODE = os.path.join(H_M4_CODE, '../../h-m3/code')
sys.path.insert(0, H_M4_CODE)
sys.path.insert(0, H_M3_CODE)

from transformers import T5ForConditionalGeneration, RobertaTokenizer
from datasets import load_dataset

# Import H-M4 modules directly to avoid H-M2/M3 conflicts
_spec = importlib.util.spec_from_file_location("h_m4_config", os.path.join(H_M4_CODE, "config.py"))
h_m4_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h_m4_config)
get_config = h_m4_config.get_config
setup_dirs = h_m4_config.setup_dirs
SEED = h_m4_config.SEED

_spec = importlib.util.spec_from_file_location("h_m4_snr", os.path.join(H_M4_CODE, "snr_analysis.py"))
h_m4_snr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h_m4_snr)
compare_policies = h_m4_snr.compare_policies
SNRResult = h_m4_snr.SNRResult

_spec = importlib.util.spec_from_file_location("h_m4_stats", os.path.join(H_M4_CODE, "stats_tests.py"))
h_m4_stats = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h_m4_stats)
bootstrap_snr_ci = h_m4_stats.bootstrap_snr_ci
permutation_test = h_m4_stats.permutation_test
compute_improvement = h_m4_stats.compute_improvement

_spec = importlib.util.spec_from_file_location("h_m4_viz", os.path.join(H_M4_CODE, "visualization.py"))
h_m4_viz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h_m4_viz)
plot_snr_comparison = h_m4_viz.plot_snr_comparison
plot_snr_bootstrap_distribution = h_m4_viz.plot_snr_bootstrap_distribution
plot_signal_noise_scatter = h_m4_viz.plot_signal_noise_scatter
plot_error_type_contribution = h_m4_viz.plot_error_type_contribution

from sample_builder import collect_synthetic_samples
from noise_analysis import run_noise_analysis


def main():
    cfg = get_config()
    setup_dirs(cfg)

    np.random.seed(SEED)
    torch.manual_seed(SEED)

    print("Loading model and tokenizer...")
    model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-small")
    tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
    model.eval()

    print(f"Collecting samples (n={cfg.n_samples})...")
    samples = collect_synthetic_samples(n_per_category=cfg.n_per_category, seed=SEED)
    print(f"Collected {len(samples)} samples")

    print("Running noise analysis (via H-M3)...")
    results = run_noise_analysis(model, tokenizer, samples)
    u_line_results = results["u_line"]
    u_ignore_results = results["u_ignore"]
    print(f"U_line: {len(u_line_results)}, U_ignore: {len(u_ignore_results)}")

    print("Comparing policies...")
    policy_results = compare_policies(u_line_results, u_ignore_results)
    snr_always = policy_results["fine_always"]
    snr_gated = policy_results["fine_gated"]

    print(f"SNR fine-always: {snr_always.snr:.4f} (n={snr_always.n_samples})")
    print(f"SNR fine-gated: {snr_gated.snr:.4f} (n={snr_gated.n_samples})")

    print("Computing bootstrap CIs...")
    ci_always = bootstrap_snr_ci(
        snr_always.signals, snr_always.noises,
        n_boot=cfg.bootstrap.n_bootstrap, seed=SEED
    )
    ci_gated = bootstrap_snr_ci(
        snr_gated.signals, snr_gated.noises,
        n_boot=cfg.bootstrap.n_bootstrap, seed=SEED
    )

    print(f"CI fine-always: [{ci_always[0]:.4f}, {ci_always[1]:.4f}]")
    print(f"CI fine-gated: [{ci_gated[0]:.4f}, {ci_gated[1]:.4f}]")

    print("Running permutation test...")
    p_value = permutation_test(snr_gated, snr_always, n_perm=cfg.permutation.n_permutation, seed=SEED)
    improvement = compute_improvement(snr_gated.snr, snr_always.snr)

    print(f"Improvement: {improvement:.2f}%")
    print(f"p-value: {p_value:.6f}")

    ci_overlap = not (ci_gated[0] > ci_always[1] or ci_always[0] > ci_gated[1])
    poc_pass = (snr_gated.snr > snr_always.snr) and (p_value < cfg.permutation.significance_threshold)

    print("\n=== PoC Check ===")
    print(f"SNR_gated > SNR_always: {snr_gated.snr > snr_always.snr}")
    print(f"p < 0.05: {p_value < 0.05}")
    print(f"95% CI overlap: {ci_overlap}")
    print(f"PoC PASS: {poc_pass}")

    print("\nGenerating figures...")
    plot_snr_comparison(snr_always, snr_gated, ci_always[:2], ci_gated[:2], cfg.viz.snr_comparison_path)
    plot_snr_bootstrap_distribution(ci_always[2], ci_gated[2], cfg.viz.bootstrap_dist_path)
    plot_signal_noise_scatter(u_line_results, u_ignore_results, cfg.viz.scatter_path)
    plot_error_type_contribution(u_line_results, u_ignore_results, cfg.viz.contribution_path)
    print(f"Figures saved to {cfg.figures_dir}/")

    metrics = {
        "hypothesis_id": "h-m4",
        "snr_fine_always": snr_always.snr,
        "snr_fine_gated": snr_gated.snr,
        "improvement_pct": improvement,
        "p_value": p_value,
        "ci_always": [ci_always[0], ci_always[1]],
        "ci_gated": [ci_gated[0], ci_gated[1]],
        "ci_overlap": ci_overlap,
        "n_u_line": len(u_line_results),
        "n_u_ignore": len(u_ignore_results),
        "poc_pass": poc_pass,
        "poc_criteria": {
            "snr_gated_greater": snr_gated.snr > snr_always.snr,
            "p_value_significant": p_value < 0.05
        }
    }

    metrics_path = os.path.join(cfg.output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {metrics_path}")

    return metrics


if __name__ == "__main__":
    main()
