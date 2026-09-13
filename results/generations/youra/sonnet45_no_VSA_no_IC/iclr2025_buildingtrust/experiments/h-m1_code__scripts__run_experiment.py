"""Main experiment: difficulty-controlled coupling analysis."""

import sys
import os
import importlib.util

# Get research directory path
research_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, research_dir)

import pandas as pd
import numpy as np
import json
from pathlib import Path


# Direct file imports for h-e1 modules (hyphens in directory names)
def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# h-e1 imports
h_e1_data_loader = load_module_from_file('h_e1_data_loader', os.path.join(research_dir, 'h-e1_code/src/data_loader.py'))
h_e1_coupling_analyzer = load_module_from_file('h_e1_coupling_analyzer', os.path.join(research_dir, 'h-e1_code/src/coupling_analyzer.py'))

load_multitrust = h_e1_data_loader.load_multitrust
extract_binary_labels = h_e1_data_loader.extract_binary_labels
generate_model_variant = h_e1_data_loader.generate_model_variant
CouplingAnalyzer = h_e1_coupling_analyzer.CouplingAnalyzer

# h-m1 imports
h_m1_difficulty_generator = load_module_from_file('h_m1_difficulty_generator', os.path.join(research_dir, 'h-m1_code/src/difficulty_generator.py'))
h_m1_partial_correlation = load_module_from_file('h_m1_partial_correlation', os.path.join(research_dir, 'h-m1_code/src/partial_correlation.py'))
h_m1_stratified_analyzer = load_module_from_file('h_m1_stratified_analyzer', os.path.join(research_dir, 'h-m1_code/src/stratified_analyzer.py'))
h_m1_visualization = load_module_from_file('h_m1_visualization', os.path.join(research_dir, 'h-m1_code/src/visualization.py'))
h_m1_config = load_module_from_file('h_m1_config', os.path.join(research_dir, 'h-m1_code/config.py'))

generate_difficulty_scores = h_m1_difficulty_generator.generate_difficulty_scores
validate_independence = h_m1_difficulty_generator.validate_independence
compute_partial_correlation = h_m1_partial_correlation.compute_partial_correlation
analyze_all_pairs = h_m1_partial_correlation.analyze_all_pairs
bin_by_quartiles = h_m1_stratified_analyzer.bin_by_quartiles
compute_quartile_phi = h_m1_stratified_analyzer.compute_quartile_phi
validate_persistence = h_m1_stratified_analyzer.validate_persistence
compare_validation_methods = h_m1_stratified_analyzer.compare_validation_methods
plot_partial_vs_raw_phi = h_m1_visualization.plot_partial_vs_raw_phi
plot_quartile_stratified_phi = h_m1_visualization.plot_quartile_stratified_phi
plot_difficulty_independence = h_m1_visualization.plot_difficulty_independence
plot_effect_size_retention = h_m1_visualization.plot_effect_size_retention
CONFIG = h_m1_config.CONFIG


def main():
    """Execute difficulty-controlled coupling analysis.

    Pipeline:
        1. Load h-e1 coupling data via load_multitrust()
        2. Generate difficulty scores (independent)
        3. Validate difficulty independence
        4. Compute partial correlations (6 pairs)
        5. Run stratified quartile analysis
        6. Dual validation comparison
        7. Generate 4 visualizations
        8. Save results + gate evaluation
    """
    print("=" * 60)
    print("H-M1: Difficulty-Controlled Coupling Analysis")
    print("=" * 60)

    # Create output directories
    os.makedirs(CONFIG['paths']['results'], exist_ok=True)
    os.makedirs(CONFIG['paths']['figures'], exist_ok=True)

    # 1. Load h-e1 coupling data (3 models)
    print("\n[1/8] Loading h-e1 coupling data...")
    models = {
        'gpt-4': load_multitrust(samples=CONFIG['dataset']['samples'], seed=42),
        'claude-3-sonnet': generate_model_variant(
            load_multitrust(samples=CONFIG['dataset']['samples'], seed=42),
            seed_offset=1
        ),
        'llama-3-70b': generate_model_variant(
            load_multitrust(samples=CONFIG['dataset']['samples'], seed=42),
            seed_offset=2
        )
    }
    print(f"Loaded {len(models)} model variants, {CONFIG['dataset']['samples']} instances each")

    # 2. Generate difficulty scores (independent)
    print("\n[2/8] Generating difficulty scores...")
    difficulty_scores = generate_difficulty_scores(
        n_samples=CONFIG['dataset']['samples'],
        seed=CONFIG['difficulty']['seed']
    )
    print(f"Generated {len(difficulty_scores)} scores: mean={difficulty_scores.mean():.3f}, "
          f"std={difficulty_scores.std():.3f}, range=[{difficulty_scores.min():.3f}, {difficulty_scores.max():.3f}]")

    # 3. Validate difficulty independence
    print("\n[3/8] Validating difficulty independence...")
    # Use first model for validation (all use same difficulty scores)
    base_labels = extract_binary_labels(models['gpt-4'], CONFIG['dataset']['dimensions'])
    independence_valid = validate_independence(
        difficulty_scores,
        base_labels,
        threshold=CONFIG['difficulty']['independence_threshold']
    )

    if not independence_valid:
        print("ERROR: Difficulty scores not independent of dimensions!")
        sys.exit(1)
    print("✓ Difficulty independence validated")

    # 4. Compute raw phi coefficients (for comparison)
    print("\n[4/8] Computing raw phi coefficients...")
    analyzer = CouplingAnalyzer(CONFIG['dataset']['dimensions'])
    raw_results = []

    for model_name, df in models.items():
        labels = extract_binary_labels(df, CONFIG['dataset']['dimensions'])
        model_results = analyzer.analyze_model(labels)
        model_results['model'] = model_name
        raw_results.append(model_results)

    raw_df = pd.concat(raw_results, ignore_index=True)

    # Get significant pairs from h-e1 (phi >= 0.3, p < 0.01)
    significant_pairs = raw_df[
        (raw_df['phi'] >= 0.3) & (raw_df['p_value'] < 0.01)
    ][['dim1', 'dim2']].drop_duplicates().values.tolist()

    print(f"Found {len(significant_pairs)} significant pairs from h-e1:")
    for dim1, dim2 in significant_pairs:
        print(f"  - {dim1} × {dim2}")

    # Build raw phi lookup
    raw_phi_lookup = {}
    for model_name in models.keys():
        model_raw = raw_df[raw_df['model'] == model_name]
        for _, row in model_raw.iterrows():
            raw_phi_lookup[(row['dim1'], row['dim2'])] = row['phi']

    # 5. Compute partial correlations
    print("\n[5/8] Computing partial correlations...")
    partial_results_all = []

    for model_name, df in models.items():
        df_with_difficulty = df.copy()
        df_with_difficulty['difficulty_score'] = difficulty_scores

        partial_results = analyze_all_pairs(df_with_difficulty, significant_pairs)
        partial_results['model'] = model_name
        partial_results_all.append(partial_results)

    partial_df = pd.concat(partial_results_all, ignore_index=True)
    partial_df.to_csv(CONFIG['paths']['results'] + 'partial_correlation.csv', index=False)
    print(f"✓ Computed partial correlations for {len(partial_df)} pairs × models")

    # 6. Run stratified quartile analysis
    print("\n[6/8] Running stratified quartile analysis...")
    quartile_results_all = []

    for model_name, df in models.items():
        df_with_difficulty = df.copy()
        df_with_difficulty['difficulty_score'] = difficulty_scores

        # Bin by quartiles
        df_binned = bin_by_quartiles(
            df_with_difficulty,
            n_quartiles=CONFIG['analysis']['n_quartiles']
        )

        # Compute phi per quartile for each significant pair
        for dim1, dim2 in significant_pairs:
            quartile_phi = compute_quartile_phi(df_binned, dim1, dim2)
            quartile_phi['dim1'] = dim1
            quartile_phi['dim2'] = dim2
            quartile_phi['model'] = model_name
            quartile_results_all.append(quartile_phi)

    quartile_df = pd.concat(quartile_results_all, ignore_index=True)
    quartile_df.to_csv(CONFIG['paths']['results'] + 'stratified_analysis.csv', index=False)
    print(f"✓ Computed quartile phi for {len(quartile_df)} quartiles × pairs × models")

    # 7. Dual validation comparison
    print("\n[7/8] Dual validation comparison...")
    validation_results = {}

    for model_name in models.keys():
        model_partial = partial_df[partial_df['model'] == model_name]
        model_quartile = quartile_df[quartile_df['model'] == model_name]

        # Compare methods
        comparison = compare_validation_methods(
            model_partial,
            model_quartile,
            threshold=CONFIG['analysis']['partial_phi_threshold']
        )

        validation_results[model_name] = comparison

        print(f"\n{model_name}:")
        print(f"  Agreement: {len(comparison['agreement'])} pairs")
        print(f"  Partial only: {len(comparison['partial_only'])} pairs")
        print(f"  Quartile only: {len(comparison['quartile_only'])} pairs")

    # 8. Gate evaluation
    print("\n[8/8] Gate evaluation...")
    gate_passing_pairs = set()

    for model_name in models.keys():
        model_partial = partial_df[partial_df['model'] == model_name]

        for _, row in model_partial.iterrows():
            partial_phi = abs(row['partial_r'])
            dim_pair = (row['dim1'], row['dim2'])

            # Check partial threshold
            if partial_phi >= CONFIG['gate']['partial_phi_threshold']:
                # Check quartile persistence
                pair_quartiles = quartile_df[
                    (quartile_df['model'] == model_name) &
                    (quartile_df['dim1'] == row['dim1']) &
                    (quartile_df['dim2'] == row['dim2'])
                ]

                if validate_persistence(
                    pair_quartiles,
                    threshold=CONFIG['gate']['partial_phi_threshold'],
                    min_quartiles=CONFIG['gate']['quartile_persistence_threshold']
                ):
                    gate_passing_pairs.add(dim_pair)
                    print(f"  ✓ {model_name}: {dim_pair[0]} × {dim_pair[1]} (partial phi={partial_phi:.3f})")

    gate_satisfied = len(gate_passing_pairs) >= CONFIG['gate']['min_pairs_passing']

    print(f"\nGate Result: {'PASS' if gate_satisfied else 'FAIL'}")
    print(f"  Pairs passing: {len(gate_passing_pairs)} / {CONFIG['gate']['min_pairs_passing']} required")
    print(f"  Passing pairs: {gate_passing_pairs}")

    # Save gate metrics
    gate_metrics = {
        'gate_satisfied': gate_satisfied,
        'pairs_passing': len(gate_passing_pairs),
        'min_pairs_required': CONFIG['gate']['min_pairs_passing'],
        'passing_pairs': [f"{d1}×{d2}" for d1, d2 in gate_passing_pairs],
        'partial_phi_threshold': CONFIG['gate']['partial_phi_threshold'],
        'quartile_persistence_threshold': CONFIG['gate']['quartile_persistence_threshold']
    }

    with open(CONFIG['paths']['results'] + 'gate_metrics.json', 'w') as f:
        json.dump(gate_metrics, f, indent=2)

    # 9. Generate visualizations
    print("\n[9/9] Generating visualizations...")

    # Use gpt-4 model for visualization (representative)
    model_for_viz = 'gpt-4'
    viz_partial = partial_df[partial_df['model'] == model_for_viz]
    viz_quartile = quartile_df[quartile_df['model'] == model_for_viz]

    plot_partial_vs_raw_phi(
        viz_partial,
        raw_phi_lookup,
        CONFIG['paths']['figures'] + 'partial_vs_raw_phi.png'
    )

    plot_quartile_stratified_phi(
        viz_quartile,
        CONFIG['paths']['figures'] + 'quartile_stratified_phi.png'
    )

    df_viz = models[model_for_viz].copy()
    df_viz['difficulty_score'] = difficulty_scores
    plot_difficulty_independence(
        df_viz,
        CONFIG['dataset']['dimensions'],
        CONFIG['paths']['figures'] + 'difficulty_independence.png'
    )

    plot_effect_size_retention(
        viz_partial,
        raw_phi_lookup,
        CONFIG['paths']['figures'] + 'effect_size_retention.png'
    )

    print("✓ Generated 4 visualization figures")

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate: {'PASS' if gate_satisfied else 'FAIL'}")
    print(f"Results saved to: {CONFIG['paths']['results']}")
    print(f"Figures saved to: {CONFIG['paths']['figures']}")


if __name__ == "__main__":
    main()
