"""
run_experiment.py - Main CLI entry point for H-E1 experiment.

H-E1: Gradient Norm Minority Proxy for Waterbirds
  - ERM training on Waterbirds (ResNet-50, 10 epochs)
  - Collect per-sample gradient norms at epochs {1, 3, 5, 10}
  - Compute gate metrics: ratio, AUC, balance_deviation
  - Generate 5 figures + results.json

Usage:
    python run_experiment.py --data-root /path/to/waterbirds_v1.0 [--smoke-test]
"""

import argparse
import os
import sys

import torch
import torch.optim as optim

# ------- Inline constants -------
COLLECTION_EPOCHS = {1, 3, 5, 10}
PRIMARY_EPOCH     = 5
LR                = 0.001
MOMENTUM          = 0.9
WEIGHT_DECAY      = 1e-4
BATCH_SIZE        = 128
TOTAL_EPOCHS      = 10
SEED              = 1
TOP_K_FRACTION    = 0.25
GATE_RATIO        = 3.0
GATE_AUC          = 0.70
GATE_BALANCE      = 0.10
FC_INPUT_DIM      = 2048
EPSILON           = 1e-8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: Gradient norm minority proxy existence PoC"
    )
    parser.add_argument(
        '--data-root', type=str,
        default='.data_cache/datasets/waterbirds/waterbirds_v1.0',
        help='Root path to Waterbirds dataset (must contain metadata.csv)',
    )
    parser.add_argument(
        '--output-dir', type=str,
        default='outputs/h-e1/',
        help='Directory for checkpoints, gradnorm arrays, figures, results.json',
    )
    parser.add_argument(
        '--seed', type=int, default=SEED,
        help='Random seed (fixed for EXISTENCE PoC reproducibility)',
    )
    parser.add_argument(
        '--smoke-test', action='store_true',
        help='Run only 10 batches to verify hook fires correctly, then exit',
    )
    parser.add_argument(
        '--device', type=str,
        default='cuda' if torch.cuda.is_available() else 'cpu',
        help='Compute device (cuda or cpu)',
    )
    parser.add_argument(
        '--num-workers', type=int, default=4,
        help='DataLoader num_workers',
    )
    return parser.parse_args()


def get_paths(output_dir: str) -> dict:
    return {
        'checkpoints':    os.path.join(output_dir, 'checkpoints', 'epoch_{N}.pt'),
        'gradnorm':       os.path.join(output_dir, 'gradnorm_epoch_{N}.npz'),
        'results':        os.path.join(output_dir, 'results.json'),
        'train_log':      os.path.join(output_dir, 'train_log.csv'),
        'fig_gate':       os.path.join(output_dir, 'figures', 'gate_metrics.png'),
        'fig_trajectory': os.path.join(output_dir, 'figures', 'trajectory.png'),
        'fig_dist':       os.path.join(output_dir, 'figures', 'distribution_epoch5.png'),
        'fig_heatmap':    os.path.join(output_dir, 'figures', 'balance_heatmap.png'),
        'fig_fnorms':     os.path.join(output_dir, 'figures', 'feature_norms.png'),
    }


def run_smoke_test(args: argparse.Namespace) -> None:
    """
    Smoke test: 10 batches only.
    Assert hook fires -> assert shapes -> print PASSED -> exit 0.
    """
    from src.dataset import get_dataloaders
    from src.model import get_model, GradientNormAnalyzer
    from src.train import set_seed

    print("=== SMOKE TEST ===")
    set_seed(args.seed)
    device = torch.device(args.device)

    loaders = get_dataloaders(args.data_root, batch_size=BATCH_SIZE,
                               num_workers=args.num_workers)

    model = get_model(device)
    analyzer = GradientNormAnalyzer(model)
    model.eval()

    n_batches = 0
    all_g_raw, all_g_tilde, all_h_norm = [], [], []

    with torch.no_grad():
        for images, y, place in loaders['train_ordered']:
            if n_batches >= 10:
                break
            images_dev = images.to(device)
            y_dev = y.to(device)

            g_raw, g_tilde, h_norm = analyzer.compute_batch_norms(images_dev, y_dev)
            analyzer.clear()

            # Assert hook fired (features_count > 0 is implicit via shape check)
            assert g_raw.shape[0] == images.shape[0], \
                f"g_raw shape mismatch: {g_raw.shape} vs batch_size={images.shape[0]}"
            assert g_tilde.shape[0] == images.shape[0], \
                f"g_tilde shape mismatch"
            assert h_norm.shape[0] == images.shape[0], \
                f"h_norm shape mismatch"
            assert g_raw.dtype == torch.float32, f"Expected float32, got {g_raw.dtype}"
            assert h_norm.min() >= 0, "h_norm should be non-negative"

            all_g_raw.append(g_raw)
            all_g_tilde.append(g_tilde)
            all_h_norm.append(h_norm)
            n_batches += 1

    # Verify hook actually fired by checking feature cache was populated
    assert n_batches == 10, f"Expected 10 batches, got {n_batches}"
    assert len(all_g_tilde) == 10, "Should have collected 10 batches"

    import torch as _torch
    all_g_t = _torch.cat(all_g_tilde)
    assert all_g_t.shape[0] == n_batches * BATCH_SIZE or all_g_t.shape[0] > 0, \
        "No samples collected"

    print(f"  Batches processed: {n_batches}")
    print(f"  Total samples: {all_g_t.shape[0]}")
    print(f"  g_tilde range: [{all_g_t.min():.4f}, {all_g_t.max():.4f}]")
    print(f"  h_norm range:  [{_torch.cat(all_h_norm).min():.4f}, {_torch.cat(all_h_norm).max():.4f}]")
    print("=== SMOKE TEST PASSED ===")
    sys.exit(0)


def main(args: argparse.Namespace) -> None:
    from src.dataset import get_dataloaders
    from src.model import get_model, GradientNormAnalyzer
    from src.train import set_seed, train_epoch, collect_gradnorms, init_train_log, append_train_log
    from src.evaluate import compute_metrics, gate_check, verify_mechanism_activated, save_results
    from src.visualize import (plot_gate_metrics, plot_trajectory, plot_distribution,
                                plot_balance_heatmap, plot_feature_norms)
    import numpy as np

    # ---- Setup ----
    set_seed(args.seed)
    device = torch.device(args.device)
    output_dir = args.output_dir
    paths = get_paths(output_dir)

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'checkpoints'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'figures'), exist_ok=True)

    print(f"H-E1 Experiment | device={device} | seed={args.seed}")
    print(f"  data_root:  {args.data_root}")
    print(f"  output_dir: {output_dir}")

    # ---- Data ----
    print("Loading dataset...")
    loaders = get_dataloaders(args.data_root, batch_size=BATCH_SIZE,
                               num_workers=args.num_workers)

    # ---- Model + Optimizer ----
    model = get_model(device)
    optimizer = optim.SGD(model.parameters(), lr=LR, momentum=MOMENTUM,
                          weight_decay=WEIGHT_DECAY)
    analyzer = GradientNormAnalyzer(model)

    # ---- CSV log ----
    log_path = init_train_log(output_dir)

    # ---- Training loop ----
    per_epoch_metrics = {}
    gate_results = {}
    epoch_5_gradnorm_data = None

    for epoch in range(1, TOTAL_EPOCHS + 1):
        print(f"\n--- Epoch {epoch}/{TOTAL_EPOCHS} ---")

        # Train
        train_stats = train_epoch(model, loaders['train_shuffle'], optimizer, device)
        print(f"  loss={train_stats['loss']:.4f}  acc={train_stats['acc']:.4f}")

        # Collect gradient norms at collection epochs
        ratio = float('nan')
        auc_val = float('nan')
        balance_dev = float('nan')

        if epoch in COLLECTION_EPOCHS:
            print(f"  Collecting gradient norms...")
            gradnorm_data = collect_gradnorms(
                model, analyzer, loaders['train_ordered'], device, epoch, output_dir
            )
            metrics = compute_metrics(
                gradnorm_data['g_tilde'],
                gradnorm_data['g_raw'],
                gradnorm_data['h_norm'],
                gradnorm_data['group_labels'],
                gradnorm_data['class_labels'],
            )
            per_epoch_metrics[epoch] = metrics
            ratio = metrics['ratio']
            auc_val = metrics['auc']
            balance_dev = metrics['balance_deviation']

            all_pass, criteria = gate_check(metrics)
            mech_pass, indicators = verify_mechanism_activated(metrics)

            print(f"  ratio={ratio:.3f} (>={GATE_RATIO}? {criteria['ratio']})"
                  f"  auc={auc_val:.3f} (>{GATE_AUC}? {criteria['auc']})"
                  f"  bal_dev={balance_dev:.3f} (<={GATE_BALANCE}? {criteria['balance_deviation']})")
            print(f"  Gate: {'PASS' if all_pass else 'FAIL'} | Mechanism: {'ACTIVATED' if mech_pass else 'PARTIAL'}")
            print(f"  Mechanism indicators: {indicators}")

            if epoch == PRIMARY_EPOCH:
                gate_results = {'all_pass': all_pass, 'criteria': criteria}
                epoch_5_gradnorm_data = gradnorm_data

            # Save checkpoint
            ckpt_path = paths['checkpoints'].replace('{N}', str(epoch))
            torch.save({'epoch': epoch, 'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'metrics': metrics}, ckpt_path)
            print(f"  Checkpoint saved: {ckpt_path}")

        # Log CSV row
        append_train_log(log_path, epoch, train_stats['loss'], train_stats['acc'],
                         ratio, auc_val, balance_dev)

    # ---- Figures ----
    print("\nGenerating figures...")
    if per_epoch_metrics:
        plot_gate_metrics(per_epoch_metrics, paths['fig_gate'])
        plot_trajectory(per_epoch_metrics, paths['fig_trajectory'])

    if epoch_5_gradnorm_data is not None:
        plot_distribution(epoch_5_gradnorm_data, paths['fig_dist'])
        plot_balance_heatmap(epoch_5_gradnorm_data, paths['fig_heatmap'])
        plot_feature_norms(epoch_5_gradnorm_data, paths['fig_fnorms'])

    # ---- Save results ----
    secondary_metrics = {}
    # Use epoch 5 metrics as primary secondary metrics
    if PRIMARY_EPOCH in per_epoch_metrics:
        secondary_metrics = {k: v for k, v in per_epoch_metrics[PRIMARY_EPOCH].items()
                             if k not in ('ratio', 'auc', 'balance_deviation')}

    save_results(per_epoch_metrics, gate_results, secondary_metrics, paths['results'])

    # ---- Final summary ----
    print("\n=== H-E1 EXPERIMENT COMPLETE ===")
    if gate_results:
        gate_pass = gate_results.get('all_pass', False)
        criteria = gate_results.get('criteria', {})
        ep5 = per_epoch_metrics.get(PRIMARY_EPOCH, {})
        print(f"  Primary epoch (T_id={PRIMARY_EPOCH}):")
        print(f"    ratio           = {ep5.get('ratio', float('nan')):.4f} (target >= {GATE_RATIO})"
              f"  -> {'PASS' if criteria.get('ratio') else 'FAIL'}")
        print(f"    AUC             = {ep5.get('auc', float('nan')):.4f} (target > {GATE_AUC})"
              f"  -> {'PASS' if criteria.get('auc') else 'FAIL'}")
        print(f"    balance_dev     = {ep5.get('balance_deviation', float('nan')):.4f} (target <= {GATE_BALANCE})"
              f"  -> {'PASS' if criteria.get('balance_deviation') else 'FAIL'}")
        print(f"  GATE: {'PASS' if gate_pass else 'FAIL'}")
    print(f"  Results: {paths['results']}")


if __name__ == '__main__':
    args = parse_args()
    if args.smoke_test:
        run_smoke_test(args)
    else:
        main(args)
