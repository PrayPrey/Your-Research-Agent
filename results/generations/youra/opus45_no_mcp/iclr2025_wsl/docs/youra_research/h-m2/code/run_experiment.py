"""H-M2 Experiment: Git Re-Basin Alignment + Layer-wise Encoding vs Layer-wise Baseline"""
import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from config import Config
from data import download_model_zoo, load_model_zoo, make_dataloaders, ModelZooDataset, collate_weights
from models import LayerWiseEncoder, AccuracyPredictor, FullModel, flatten_weights
from train import set_seed, train_model
from evaluate import predict, compute_pearson, compare_methods, plot_scatter, plot_per_seed, plot_loss_curves
from alignment import compute_alignment_batch, verify_alignment, detect_permutable_layers
from torch.utils.data import DataLoader


def get_input_dim_and_num_layers(sample):
    weights = sample['weights']
    flat = flatten_weights(weights)
    return flat.numel(), len(weights.keys())


def apply_alignment_to_samples(samples, aligned_sds):
    """Replace weights in samples with aligned state dicts."""
    aligned_samples = []
    for i, sample in enumerate(samples):
        aligned_samples.append({
            'weights': aligned_sds[i],
            'accuracy': sample['accuracy']
        })
    return aligned_samples


def plot_gate_metrics_h_m2(baseline_r, grb_r, save_path):
    """Bar chart comparing Layer-wise baseline vs Layer-wise+GRB."""
    fig, ax = plt.subplots(figsize=(8, 6))
    means = [np.mean(baseline_r), np.mean(grb_r)]
    stds = [np.std(baseline_r), np.std(grb_r)]
    bars = ax.bar(['Layer-wise (Baseline)', 'Layer-wise + GRB'], means, yerr=stds,
                  capsize=5, color=['#3498db', '#9b59b6'])
    ax.set_ylabel('Pearson r')
    ax.set_title('H-M2 Gate: Layer-wise vs Layer-wise+GRB')
    ax.set_ylim(0, 1)
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{mean:.3f}', ha='center')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_alignment_diagnostic(pre_sims, post_sims, save_path):
    """Histogram of pre/post alignment similarities."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(pre_sims, bins=30, alpha=0.5, label='Pre-alignment', color='#e74c3c')
    ax.hist(post_sims, bins=30, alpha=0.5, label='Post-alignment', color='#2ecc71')
    ax.set_xlabel('Cosine Similarity to Reference')
    ax.set_ylabel('Count')
    ax.set_title('Alignment Diagnostic: Pre vs Post')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def run_seed(method, seed, train_loader, val_loader, test_loader, cfg, num_layers):
    """Run single seed for a method (layerwise or layerwise_grb)."""
    set_seed(seed)
    device = cfg.device if torch.cuda.is_available() else "cpu"

    encoder = LayerWiseEncoder(num_layers, cfg.stats_per_layer, cfg.hidden_dim, cfg.embed_dim)
    predictor = AccuracyPredictor(cfg.embed_dim, cfg.predictor_hidden)
    model = FullModel(encoder, predictor, "layerwise").to(device)

    model, history = train_model(model, train_loader, val_loader, cfg.lr, cfg.weight_decay,
                                  cfg.max_epochs, cfg.early_stop_patience, device, "layerwise", None)

    preds, targets = predict(model, test_loader, device, "layerwise", None)
    metrics = compute_pearson(preds, targets)

    return {'pearson_r': metrics['pearson_r'], 'history': history, 'preds': preds, 'targets': targets}


def main():
    cfg = Config()
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.alignment_cache_dir, exist_ok=True)

    print("=" * 60)
    print("H-M2: Git Re-Basin Alignment + Layer-wise Encoding Experiment")
    print("=" * 60)

    print("\nDownloading dataset...")
    download_model_zoo()

    print("Loading dataset...")
    train_raw, val_raw, test_raw = load_model_zoo(cfg.data_path)
    print(f"Train: {len(train_raw)}, Val: {len(val_raw)}, Test: {len(test_raw)}")

    _, num_layers = get_input_dim_and_num_layers(train_raw[0])
    print(f"Num layers: {num_layers}")

    # Compute alignment (or load from cache)
    print("\n--- Alignment Preprocessing ---")
    train_sds = [s['weights'] for s in train_raw]
    val_sds = [s['weights'] for s in val_raw]
    test_sds = [s['weights'] for s in test_raw]

    # Reference model is from train set
    reference_sd = train_sds[cfg.alignment_reference_idx]
    perm_layers = detect_permutable_layers(reference_sd)
    print(f"Reference: train[{cfg.alignment_reference_idx}], Algorithm: {cfg.alignment_algorithm}")
    print(f"Permutable layers: {perm_layers}")

    # Collect pre-alignment similarities for diagnostic
    print("Computing pre-alignment similarities...")
    pre_sims = []
    for sd in train_sds[:1000]:  # Sample for diagnostic
        pre_sims.append(verify_alignment(sd, reference_sd))

    # Align each split
    train_aligned, train_conv = compute_alignment_batch(
        train_sds, cfg.alignment_reference_idx, cfg.alignment_algorithm,
        cache_path=os.path.join(cfg.alignment_cache_dir, "train_aligned.pt")
    )
    val_aligned, val_conv = compute_alignment_batch(
        val_sds, 0, cfg.alignment_algorithm,
        cache_path=os.path.join(cfg.alignment_cache_dir, "val_aligned.pt")
    )
    test_aligned, test_conv = compute_alignment_batch(
        test_sds, 0, cfg.alignment_algorithm,
        cache_path=os.path.join(cfg.alignment_cache_dir, "test_aligned.pt")
    )

    convergence_rate = train_conv
    print(f"\nOverall convergence rate: {convergence_rate:.2%}")

    # Collect post-alignment similarities for diagnostic
    print("Computing post-alignment similarities...")
    post_sims = []
    for sd in train_aligned[:1000]:
        post_sims.append(verify_alignment(sd, reference_sd))

    # Plot alignment diagnostic
    plot_alignment_diagnostic(pre_sims, post_sims, os.path.join(cfg.figures_dir, "alignment_diagnostic.png"))

    # Create aligned samples
    train_samples_aligned = apply_alignment_to_samples(train_raw, train_aligned)
    val_samples_aligned = apply_alignment_to_samples(val_raw, val_aligned)
    test_samples_aligned = apply_alignment_to_samples(test_raw, test_aligned)

    # Create dataloaders
    train_loader_raw, val_loader_raw, test_loader_raw = make_dataloaders(train_raw, val_raw, test_raw, cfg.batch_size)
    train_loader_aligned, val_loader_aligned, test_loader_aligned = make_dataloaders(
        train_samples_aligned, val_samples_aligned, test_samples_aligned, cfg.batch_size
    )

    # Run experiments
    baseline_results = []
    grb_results = []

    print("\n=== Baseline (Layer-wise, no alignment) ===")
    for seed in cfg.seeds:
        print(f"  Seed {seed}...")
        result = run_seed("layerwise", seed, train_loader_raw, val_loader_raw, test_loader_raw, cfg, num_layers)
        r = result['pearson_r']
        print(f"    Pearson r: {r:.4f}")
        baseline_results.append(r)

        plot_loss_curves(result['history'], f"baseline_seed{seed}",
                        os.path.join(cfg.figures_dir, f"loss_baseline_seed{seed}.png"))
        if seed == 0:
            plot_scatter(result['preds'], result['targets'], "Baseline (Layer-wise)",
                        os.path.join(cfg.figures_dir, "scatter_baseline.png"))

    print("\n=== Proposed (Layer-wise + GRB Alignment) ===")
    for seed in cfg.seeds:
        print(f"  Seed {seed}...")
        result = run_seed("layerwise_grb", seed, train_loader_aligned, val_loader_aligned, test_loader_aligned, cfg, num_layers)
        r = result['pearson_r']
        print(f"    Pearson r: {r:.4f}")
        grb_results.append(r)

        plot_loss_curves(result['history'], f"grb_seed{seed}",
                        os.path.join(cfg.figures_dir, f"loss_grb_seed{seed}.png"))
        if seed == 0:
            plot_scatter(result['preds'], result['targets'], "Layer-wise + GRB",
                        os.path.join(cfg.figures_dir, "scatter_grb.png"))

    # Compare methods
    comparison = compare_methods(baseline_results, grb_results)

    # Gate check (H-M2: Δr > 0.05, p < 0.05, SHOULD_WORK)
    delta_r = comparison['delta_r']
    p_value = comparison['p_value']
    gate_pass = delta_r > 0.05 and p_value < 0.05
    convergence_pass = convergence_rate > cfg.convergence_threshold
    seeds_improved = sum(g > b for g, b in zip(grb_results, baseline_results))

    # Generate figures
    plot_gate_metrics_h_m2(baseline_results, grb_results, os.path.join(cfg.figures_dir, "gate_metrics.png"))
    plot_per_seed(baseline_results, grb_results, os.path.join(cfg.figures_dir, "per_seed.png"))

    # Determine gate result
    if gate_pass:
        gate_result = "PASS"
    elif delta_r > 0:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"

    results = {
        'hypothesis': 'H-M2',
        'gate_type': 'SHOULD_WORK',
        'baseline_results': baseline_results,
        'grb_results': grb_results,
        'baseline_mean': float(np.mean(baseline_results)),
        'grb_mean': float(np.mean(grb_results)),
        'delta_r': float(delta_r),
        't_stat': float(comparison['t_stat']),
        'p_value': float(p_value),
        'convergence_rate': float(convergence_rate),
        'convergence_pass': convergence_pass,
        'seeds_improved': seeds_improved,
        'gate_pass': gate_pass,
        'gate_result': gate_result,
        'alignment_algorithm': cfg.alignment_algorithm,
        'reference_idx': cfg.alignment_reference_idx,
    }

    with open(os.path.join(cfg.output_dir, "results.json"), 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Baseline (Layer-wise) mean r: {results['baseline_mean']:.4f}")
    print(f"Proposed (Layer-wise+GRB) mean r: {results['grb_mean']:.4f}")
    print(f"Delta r: {results['delta_r']:.4f} (threshold: 0.05)")
    print(f"p-value: {results['p_value']:.4f} (threshold: 0.05)")
    print(f"Convergence rate: {results['convergence_rate']:.2%} (threshold: 95%)")
    print(f"Seeds improved: {seeds_improved}/5")
    print(f"\nGate Type: SHOULD_WORK")
    print(f"Gate Result: {gate_result}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
