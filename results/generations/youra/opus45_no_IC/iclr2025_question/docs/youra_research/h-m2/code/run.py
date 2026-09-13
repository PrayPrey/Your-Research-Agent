"""H-M2 Main Pipeline - Statistical Analysis of Error Family Hypothesis"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    BENCHMARK_NAMES,
    FIGURES_DIR,
    P_VALUE_THRESHOLD,
    SAME_FAMILY_MEAN_THRESHOLD
)
from data import load_js_matrix
from analysis import test_error_family_hypothesis
from visualize import (
    plot_family_boxplot,
    plot_family_violin,
    plot_js_heatmap_with_families,
    plot_effect_size_forest
)


def main():
    print("=" * 60)
    print("H-M2: Error Family Hypothesis Test")
    print("=" * 60)

    # Ensure figures directory exists
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load JS-divergence matrix from H-E1
    print("\n[1/4] Loading JS-divergence matrix from H-E1...")
    js_matrix = load_js_matrix()
    print(f"  Matrix shape: {js_matrix.shape}")

    # Run statistical analysis
    print("\n[2/4] Running Mann-Whitney U test + Cliff's delta...")
    result = test_error_family_hypothesis(js_matrix, BENCHMARK_NAMES)

    print(f"  Same-family (n={result['n_same']}): mean={result['same_family_mean']:.4f} ± {result['same_family_std']:.4f}")
    print(f"  Cross-family (n={result['n_cross']}): mean={result['cross_family_mean']:.4f} ± {result['cross_family_std']:.4f}")
    print(f"  Mann-Whitney U p-value: {result['p_value']:.6f}")
    print(f"  Cliff's delta: {result['effect_size_cliffs_d']:.3f} (CI: {result['effect_size_ci'][0]:.3f}, {result['effect_size_ci'][1]:.3f})")

    # Generate visualizations
    print("\n[3/4] Generating visualizations...")
    plot_family_boxplot(
        result['same_family_values'],
        result['cross_family_values'],
        FIGURES_DIR / 'boxplot.png'
    )
    print("  Saved: boxplot.png")

    plot_family_violin(
        result['same_family_values'],
        result['cross_family_values'],
        FIGURES_DIR / 'violin.png'
    )
    print("  Saved: violin.png")

    plot_js_heatmap_with_families(
        js_matrix,
        BENCHMARK_NAMES,
        FIGURES_DIR / 'heatmap.png'
    )
    print("  Saved: heatmap.png")

    plot_effect_size_forest(
        result['effect_size_cliffs_d'],
        result['effect_size_ci'],
        FIGURES_DIR / 'forest.png'
    )
    print("  Saved: forest.png")

    # Gate decision
    print("\n[4/4] Gate Decision...")
    p_pass = result['p_value'] < P_VALUE_THRESHOLD
    mean_pass = result['same_family_mean'] < SAME_FAMILY_MEAN_THRESHOLD
    gate_pass = p_pass and mean_pass

    print(f"  p < {P_VALUE_THRESHOLD}: {p_pass} ({result['p_value']:.6f})")
    print(f"  mean < {SAME_FAMILY_MEAN_THRESHOLD}: {mean_pass} ({result['same_family_mean']:.4f})")
    print(f"  GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")

    # Save results
    output = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_condition": f"p < {P_VALUE_THRESHOLD} AND same_family_mean < {SAME_FAMILY_MEAN_THRESHOLD}",
        "gate_result": "PASS" if gate_pass else "FAIL",
        "p_value": result['p_value'],
        "same_family_mean": result['same_family_mean'],
        "same_family_std": result['same_family_std'],
        "cross_family_mean": result['cross_family_mean'],
        "cross_family_std": result['cross_family_std'],
        "same_family_values": result['same_family_values'],
        "cross_family_values": result['cross_family_values'],
        "effect_size_cliffs_d": result['effect_size_cliffs_d'],
        "effect_size_ci": list(result['effect_size_ci']),
        "n_same": result['n_same'],
        "n_cross": result['n_cross'],
        "timestamp": datetime.now().isoformat()
    }

    results_path = Path(__file__).parent.parent / "results.json"
    with open(results_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print("\n" + "=" * 60)
    print(f"H-M2 COMPLETE: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    return output


if __name__ == "__main__":
    main()
