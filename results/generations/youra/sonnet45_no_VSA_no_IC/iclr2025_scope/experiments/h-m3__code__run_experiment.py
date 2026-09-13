"""Main experiment runner for H-M3: Query Complexity Stratification."""
import sys
import json
from pathlib import Path

# Add analysis module to path
sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from complexity import QueryComplexityClassifier
from attention import QueryTokenAttentionExtractor
from stratify import stratify_dataset
from metrics import run_attention_extraction
from stats import run_statistical_test
from visualize import (
    plot_bar_chart,
    plot_distributions,
    plot_scatter,
    plot_boxplots,
    write_validation_report
)


def main():
    print("=" * 60)
    print("H-M3: Query Complexity Attention Analysis")
    print("=" * 60)

    # Setup paths
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "code" / "data" / "longbench" / "data"
    output_dir = base_dir / "code" / "outputs"
    figures_dir = base_dir / "figures"

    output_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    # Step 1: Initialize classifier
    print("\n[1/6] Initializing complexity classifier...")
    classifier = QueryComplexityClassifier(spacy_model="en_core_web_sm")

    # Step 2: Stratify dataset
    print("\n[2/6] Stratifying dataset...")
    dataset = stratify_dataset(
        classifier,
        str(data_path),
        min_per_stratum=100  # Reduced from 300 for PoC
    )
    print(f"  Simple queries: {len(dataset[dataset['complexity'] == 'simple'])}")
    print(f"  Complex queries: {len(dataset[dataset['complexity'] == 'complex'])}")

    # Save stratified dataset
    dataset.to_csv(output_dir / "stratified_dataset.csv", index=False)

    # Step 3: Extract attention concentrations
    print("\n[3/6] Extracting attention concentrations...")
    print("  (This may take 10-30 minutes depending on GPU)")

    extractor = QueryTokenAttentionExtractor(None)  # Tokenizer set in run_attention_extraction

    dataset_with_attn = run_attention_extraction(
        dataset,
        extractor,
        model_name="meta-llama/Llama-2-7b-hf",
        max_samples=200  # PoC: 200 samples (100 per stratum)
    )

    # Save results
    dataset_with_attn.to_csv(output_dir / "results.csv", index=False)

    # Step 4: Statistical testing
    print("\n[4/6] Running statistical tests...")
    results = run_statistical_test(dataset_with_attn)

    print(f"  Simple mean: {results['simple_mean']:.3f}")
    print(f"  Complex mean: {results['complex_mean']:.3f}")
    print(f"  Difference: {results['delta']:.3f}")
    print(f"  p-value: {results['p_value']:.4f}")
    print(f"  Cohen's d: {results['cohen_d']:.3f}")

    # Save statistics
    with open(output_dir / "statistics.json", 'w') as f:
        json.dump(results, f, indent=2)

    # Step 5: Generate figures
    print("\n[5/6] Generating figures...")
    plot_bar_chart(results, str(figures_dir / "bar_chart.png"))
    plot_distributions(dataset_with_attn, str(figures_dir / "distributions.png"))
    plot_scatter(dataset_with_attn, str(figures_dir / "scatter.png"))
    plot_boxplots(dataset_with_attn, str(figures_dir / "boxplots.png"))
    print("  ✓ All figures saved")

    # Step 6: Write validation report
    print("\n[6/6] Writing validation report...")
    write_validation_report(
        dataset_with_attn,
        results,
        "../figures",
        str(base_dir / "04_validation.md")
    )

    # Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate: {'PASS' if results['p_value'] < 0.05 and results['delta'] > 0 else 'FAIL'}")
    print(f"p-value: {results['p_value']:.4f}")
    print(f"Effect: {results['delta']:.3f} ({results['cohen_d']:.2f}σ)")
    print("=" * 60)


if __name__ == "__main__":
    main()
