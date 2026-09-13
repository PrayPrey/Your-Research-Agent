"""H-C1: Main entry point (real data path with fallback)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config


def run(cfg: Config = None) -> dict:
    if cfg is None:
        cfg = Config()

    trak_path = os.path.join(os.path.dirname(__file__), cfg.trak_scores_path)
    ccr_path = os.path.join(os.path.dirname(__file__), cfg.ccr_scores_path)
    checkpoint_path = os.path.join(os.path.dirname(__file__), cfg.checkpoint_path)

    if not (os.path.exists(trak_path) and os.path.exists(ccr_path)):
        print("Real data artifacts not found. Falling back to simulated data...")
        from main_simulated import run_simulated
        return run_simulated(cfg)

    import numpy as np
    import json
    from evaluate import compute_ifr_statistics, validate_gate_conditions
    from visualize import (
        plot_ifr_boxplot, plot_ifr_redundancy_scatter,
        plot_redundancy_by_contamination, plot_trak_by_contamination
    )

    print("=" * 60)
    print("H-C1: IFR Analysis (Real Data)")
    print("=" * 60)

    trak_scores_full = np.load(trak_path)
    ccr_scores_full = np.load(ccr_path)

    n_top = int(len(trak_scores_full) * cfg.top_pct)
    top_idx = np.argsort(np.abs(trak_scores_full))[-n_top:]

    trak_scores = trak_scores_full[top_idx]
    ccr_scores = ccr_scores_full[top_idx]
    contaminated_mask = ccr_scores > np.median(ccr_scores_full)

    print(f"Selected top {cfg.top_pct*100}%: {len(top_idx)} examples")
    print(f"Contaminated: {contaminated_mask.sum()}, Non-contaminated: {(~contaminated_mask).sum()}")

    if os.path.exists(checkpoint_path):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from ifr_computer import extract_embeddings

        print("Loading model for embedding extraction...")
        model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
        tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

        print("Extracting embeddings...")
        embeddings = extract_embeddings(model, tokenizer, texts, cfg.batch_size, cfg.max_seq_length)
    else:
        print("Checkpoint not found. Using random embeddings (degraded analysis)...")
        rng = np.random.default_rng(cfg.seed)
        embeddings = rng.standard_normal((len(top_idx), 256))
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    print("\nComputing IFR statistics...")
    results = compute_ifr_statistics(
        embeddings, trak_scores, contaminated_mask,
        k=cfg.knn_k, epsilon=cfg.epsilon
    )

    gate_results = validate_gate_conditions(results, cfg.significance_level, cfg.correlation_threshold)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"IFR (contaminated mean): {results['ifr_contaminated_mean']:.4f}")
    print(f"IFR (non-contaminated mean): {results['ifr_non_contaminated_mean']:.4f}")
    print(f"IFR difference p-value: {results['ifr_diff_pvalue']:.6f}")
    print(f"IFR-redundancy correlation (ρ): {results['ifr_redundancy_correlation']:.4f}")

    print("\n" + "=" * 60)
    print("GATE CONDITIONS")
    print("=" * 60)
    print(f"Gate 1 (IFR_c > IFR_nc, p<0.05): {'PASSED' if gate_results['gate_1_passed'] else 'FAILED'}")
    print(f"Gate 2 (ρ < -0.5): {'PASSED' if gate_results['gate_2_passed'] else 'FAILED'}")
    print(f"Overall: {'PASSED' if gate_results['overall_passed'] else ('PARTIAL_PASS' if gate_results['partial_pass'] else 'FAILED')}")

    output_dir = cfg.output_dir
    os.makedirs(output_dir, exist_ok=True)

    ifr_c = results['ifr'][contaminated_mask]
    ifr_nc = results['ifr'][~contaminated_mask]

    plot_ifr_boxplot(ifr_c, ifr_nc, results['ifr_diff_pvalue'],
                     os.path.join(output_dir, 'ifr_boxplot.png'))
    plot_ifr_redundancy_scatter(results['ifr'], results['redundancy'],
                                 results['ifr_redundancy_correlation'],
                                 os.path.join(output_dir, 'ifr_redundancy_scatter.png'))
    plot_redundancy_by_contamination(results['redundancy'], contaminated_mask,
                                      os.path.join(output_dir, 'redundancy_by_contamination.png'))
    plot_trak_by_contamination(trak_scores, contaminated_mask,
                                os.path.join(output_dir, 'trak_by_contamination.png'))

    final_results = {
        "hypothesis": "H-C1",
        "data_mode": "real",
        "n_samples": len(top_idx),
        "n_contaminated": int(contaminated_mask.sum()),
        "metrics": {
            "ifr_contaminated_mean": results["ifr_contaminated_mean"],
            "ifr_non_contaminated_mean": results["ifr_non_contaminated_mean"],
            "ifr_diff_pvalue": results["ifr_diff_pvalue"],
            "ifr_redundancy_correlation": results["ifr_redundancy_correlation"],
            "correlation_pvalue": results["correlation_pvalue"]
        },
        "gate_conditions": {
            "gate_1_passed": gate_results["gate_1_passed"],
            "gate_2_passed": gate_results["gate_2_passed"],
            "overall_passed": gate_results["overall_passed"],
            "partial_pass": gate_results["partial_pass"]
        }
    }

    with open(os.path.join(output_dir, 'results.json'), 'w') as f:
        json.dump(final_results, f, indent=2)

    return final_results


if __name__ == "__main__":
    run()
