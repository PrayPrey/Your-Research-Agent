"""
H-E1 EquiSSL Distribution Shift PoC
Entry point: trains EquiSSL + SANE baseline, computes MMD ratio, exports results.

Usage:
  python run_experiment.py --data_root /path/to/cnn_zoo --vit_root /path/to/vit
  python run_experiment.py --data_root /path/to/cnn_zoo --smoke_test
"""
import os
import sys
import json
import argparse
import time
import torch
import numpy as np
from torch.utils.data import DataLoader as TorchDataLoader
from torch_geometric.data import Batch

# Add code dir to path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import config
from data.multizoo_graph_dataset import MultiZooGraphDataset
from data.vitzoo_graph_dataset import ViTZooGraphDataset
from training.train_equissl import (
    run_lambda_sweep, select_best_lambda, load_encoder_from_checkpoint
)
from training.train_sane_baseline import train_sane, extract_sane_latents, load_sane_encoder
from evaluation.mmd_eval import compute_mmd_ratio, gate_check
from evaluation.visualize import (
    plot_tsne, plot_mmd_comparison, plot_distance_histogram, plot_training_curves
)


def get_parser():
    p = argparse.ArgumentParser(description='H-E1 EquiSSL Distribution Shift PoC')
    p.add_argument('--data_root', type=str, required=True,
                   help='Root dir containing MLP/CNN model zoo checkpoints')
    p.add_argument('--vit_root', type=str, required=True,
                   help='Root dir containing real ViT Model Zoo .ckpt files. '
                        'Download with: modelzoo fetch --zoo vit --dataset_pt imagenet --config sl --dir <dir>')
    p.add_argument('--checkpoint_dir', type=str, default='checkpoints/h-e1/')
    p.add_argument('--results_dir', type=str, default=None,
                   help='Override results output dir (default: from config.py)')
    p.add_argument('--figures_dir', type=str, default=None,
                   help='Override figures output dir')
    p.add_argument('--device', type=str,
                   default='cuda' if torch.cuda.is_available() else 'cpu')
    p.add_argument('--gpu_id', type=int, default=1,
                   help='GPU device ID to use (for multi-GPU systems)')
    p.add_argument('--lam', type=float, default=None,
                   help='Single lambda override (skips sweep)')
    p.add_argument('--seed', type=int, default=None,
                   help='Single seed override (skips 5-seed loop)')
    p.add_argument('--smoke_test', action='store_true',
                   help='Quick smoke test: 2 epochs, 50 train + 50 ViT models')
    p.add_argument('--n_train_models', type=int, default=None,
                   help='Limit training zoo size (default: use all)')
    p.add_argument('--n_vit_models', type=int, default=None,
                   help='Limit ViT test zoo size (default: 250)')
    p.add_argument('--epochs', type=int, default=None,
                   help='Override epochs (default: from config.py)')
    p.add_argument('--skip_sane', action='store_true',
                   help='Skip SANE baseline training (for debugging)')
    return p


def extract_equissl_latents(encoder, dataset, device, batch_size=64):
    """Encode all models in dataset with EquiSSL encoder."""
    loader = TorchDataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=2,
                              collate_fn=lambda graphs: Batch.from_data_list(graphs))
    all_z = []
    encoder.eval()
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            z = encoder(batch)
            all_z.append(z.cpu())
    return torch.cat(all_z, dim=0)


def main():
    args = get_parser().parse_args()

    # GPU selection
    if args.device == 'cuda' and torch.cuda.is_available():
        gpu_id = min(args.gpu_id, torch.cuda.device_count() - 1)
        device = torch.device(f'cuda:{gpu_id}')
        print(f'Using GPU {gpu_id}: {torch.cuda.get_device_name(gpu_id)}')
    else:
        device = torch.device('cpu')
        print('Using CPU')

    # Smoke test overrides
    if args.smoke_test:
        config.EPOCHS = 2
        config.SEEDS = [0]
        n_train_models = 50
        n_vit_models = 50
        lambda_list = [0.1]
        print('[SMOKE TEST] epochs=2, 50 train + 50 ViT models, lambda=[0.1]')
    else:
        n_train_models = args.n_train_models
        n_vit_models = args.n_vit_models or 250
        lambda_list = [args.lam] if args.lam is not None else config.LAMBDA_SWEEP

    epochs = args.epochs
    seed_list = [args.seed] if args.seed is not None else config.SEEDS

    # Paths
    results_dir = args.results_dir or config.RESULTS_DIR
    figures_dir = args.figures_dir or config.FIGURES_DIR
    checkpoint_dir = args.checkpoint_dir
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)

    print(f'\n=== H-E1 EquiSSL Distribution Shift PoC ===')
    print(f'Data root: {args.data_root}')
    print(f'Seeds: {seed_list}, Lambda: {lambda_list}')
    print(f'Epochs: {epochs or config.EPOCHS}')

    # --- Setup ViT test zoo ---
    vit_root = args.vit_root
    if vit_root is None or not os.path.exists(vit_root):
        raise RuntimeError(
            f'--vit_root must point to real ViT Model Zoo directory. '
            f'Got: {vit_root!r}. '
            f'Download with: modelzoo fetch --zoo vit --dataset_pt imagenet --config sl --dir <dir>'
        )

    # Build datasets (full, no split — for MMD eval we encode all models)
    print(f'\n[Step 1] Loading datasets...')
    train_dataset_full = MultiZooGraphDataset(
        root=args.data_root, normalize=True, split='train',
        val_fraction=0.0, seed=0, max_models=n_train_models
    )
    vit_dataset = ViTZooGraphDataset(
        root=vit_root, normalize=True, max_models=n_vit_models
    )
    # Unnormalized versions for SANE baseline (SANE uses raw weight stats, not scale-normalized)
    train_dataset_raw = MultiZooGraphDataset(
        root=args.data_root, normalize=False, split='train',
        val_fraction=0.0, seed=0, max_models=n_train_models
    )
    vit_dataset_raw = ViTZooGraphDataset(
        root=vit_root, normalize=False, max_models=n_vit_models
    )
    print(f'  Train zoo: {len(train_dataset_full)} models')
    print(f'  ViT zoo:   {len(vit_dataset)} models')

    if len(train_dataset_full) < 2:
        raise RuntimeError(f'Too few training models in {args.data_root}. Check --data_root.')
    if len(vit_dataset) < 2:
        raise RuntimeError(f'Too few ViT models in {vit_root}.')

    # Per-seed results
    seed_results = {}

    for seed in seed_list:
        print(f'\n=== Seed {seed} ===')

        # --- EquiSSL Training ---
        print(f'[Step 2] Training EquiSSL (lambda sweep: {lambda_list})...')
        sweep_results = run_lambda_sweep(
            seed=seed,
            data_root=args.data_root,
            checkpoint_dir=os.path.join(checkpoint_dir, f'seed{seed}'),
            device=str(device),
            lambda_list=lambda_list,
            epochs=epochs,
            n_train_models=n_train_models
        )

        # Select best lambda
        val_dataset = MultiZooGraphDataset(
            root=args.data_root, normalize=True, split='val',
            val_fraction=config.VAL_FRACTION, seed=seed, max_models=n_train_models
        )
        best_lam, best_equi_ckpt = select_best_lambda(
            sweep_results, val_dataset, device=str(device)
        )
        print(f'  Best lambda: {best_lam}, checkpoint: {best_equi_ckpt}')

        # Load best encoder
        equi_encoder = load_encoder_from_checkpoint(best_equi_ckpt, device=str(device))

        # --- SANE Training ---
        if not args.skip_sane:
            print(f'[Step 3] Training SANE baseline...')
            sane_ckpt = train_sane(
                seed=seed,
                data_root=args.data_root,
                checkpoint_dir=os.path.join(checkpoint_dir, f'sane_seed{seed}'),
                device=str(device),
                epochs=epochs,
                n_train_models=n_train_models
            )
            sane_encoder = load_sane_encoder(sane_ckpt, device=str(device))
        else:
            print('  [Skipping SANE training]')
            sane_encoder = None

        # --- Encoding ---
        print(f'[Step 4] Encoding all models...')
        equi_train_z = extract_equissl_latents(equi_encoder, train_dataset_full, device)
        equi_vit_z = extract_equissl_latents(equi_encoder, vit_dataset, device)

        if sane_encoder is not None:
            # Use unnormalized datasets for SANE (SANE trained on raw weight stats)
            sane_train_z = extract_sane_latents(sane_ckpt, train_dataset_raw, device=str(device))
            sane_vit_z = extract_sane_latents(sane_ckpt, vit_dataset_raw, device=str(device))
        else:
            raise RuntimeError(
                'SANE encoder is None. Do not use --skip_sane: SANE baseline is required for MMD ratio.'
            )

        print(f'  EquiSSL train_z: {equi_train_z.shape}, vit_z: {equi_vit_z.shape}')
        print(f'  SANE train_z:   {sane_train_z.shape}, vit_z: {sane_vit_z.shape}')

        # --- MMD Evaluation ---
        print(f'[Step 5] Computing MMD ratio...')
        result = compute_mmd_ratio(
            sane_train_z=sane_train_z,
            equi_train_z=equi_train_z,
            vit_z=equi_vit_z,  # Use EquiSSL-encoded ViT for both (same latent space via separate paths)
            n_kernels=config.N_MMD_KERNELS
        )
        # Also compute SANE MMD in SANE's own latent space
        sane_result = compute_mmd_ratio(
            sane_train_z=sane_train_z,
            equi_train_z=equi_train_z,
            vit_z=sane_vit_z,
            n_kernels=config.N_MMD_KERNELS
        )

        # Use SANE MMD in SANE space, EquiSSL MMD in EquiSSL space
        mmd_sane = sane_result['mmd_sane']
        mmd_equi = result['mmd_equi']
        ratio = mmd_sane / mmd_equi if mmd_equi > 1e-10 else float('inf')
        gate = gate_check(ratio)

        print(f'  MMD_SANE  = {mmd_sane:.6f}')
        print(f'  MMD_EquiSSL = {mmd_equi:.6f}')
        print(f'  Ratio = {ratio:.4f} → Gate: {gate}')

        seed_results[str(seed)] = {
            'mmd_sane': mmd_sane,
            'mmd_equi': mmd_equi,
            'ratio': ratio,
            'best_lam': best_lam,
        }

        # Generate per-seed t-SNE
        if not args.smoke_test or seed == seed_list[-1]:
            plot_tsne(
                equi_train_z[:500], equi_vit_z[:250],
                title=f'EquiSSL Latent Space (seed={seed})',
                save_path=os.path.join(figures_dir, f'tsne_equissl_seed{seed}.png')
            )
            plot_tsne(
                sane_train_z[:500], sane_vit_z[:250],
                title=f'SANE Latent Space (seed={seed})',
                save_path=os.path.join(figures_dir, f'tsne_sane_seed{seed}.png')
            )

    # --- Summary ---
    ratios = [v['ratio'] for v in seed_results.values() if v['ratio'] != float('inf')]
    mmd_sanes = [v['mmd_sane'] for v in seed_results.values()]
    mmd_equis = [v['mmd_equi'] for v in seed_results.values()]

    summary = {
        'mmd_sane_mean': float(np.mean(mmd_sanes)),
        'mmd_sane_std':  float(np.std(mmd_sanes)),
        'mmd_equi_mean': float(np.mean(mmd_equis)),
        'mmd_equi_std':  float(np.std(mmd_equis)),
        'ratio_mean':    float(np.mean(ratios)) if ratios else 0.0,
        'ratio_std':     float(np.std(ratios))  if len(ratios) > 1 else 0.0,
        'gate_result':   gate_check(float(np.mean(ratios)) if ratios else 0.0),
        'lambda_sweep':  lambda_list,
    }

    full_results = {
        'hypothesis_id': 'h-e1',
        'seeds': seed_results,
        'summary': summary,
    }

    results_path = os.path.join(results_dir, 'experiment_results.json')
    with open(results_path, 'w') as f:
        json.dump(full_results, f, indent=2)
    print(f'\n[Step 6] Results saved to {results_path}')

    # --- Figures ---
    print('[Step 7] Generating figures...')
    # MMD comparison bar chart (using summary values)
    plot_mmd_comparison(
        mmd_sane=summary['mmd_sane_mean'],
        mmd_equi=summary['mmd_equi_mean'],
        ratio=summary['ratio_mean'],
        save_path=os.path.join(figures_dir, 'mmd_comparison.png')
    )
    # Training curves
    plot_training_curves(
        log_dir=os.path.join(checkpoint_dir, f'seed{seed_list[0]}'),
        lambda_list=lambda_list,
        seed=seed_list[0],
        save_path=os.path.join(figures_dir, 'training_curves.png')
    )
    print(f'  Figures saved to {figures_dir}')

    # Final gate result
    gate_result = summary['gate_result']
    print(f'\n=== FINAL GATE RESULT: {gate_result} ===')
    print(f'  Ratio mean = {summary["ratio_mean"]:.4f} ± {summary["ratio_std"]:.4f}')
    print(f'  MUST_WORK gate (ratio >= 2.0): {gate_result}')

    return full_results


if __name__ == '__main__':
    main()
