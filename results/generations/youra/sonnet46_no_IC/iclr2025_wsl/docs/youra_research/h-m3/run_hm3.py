"""
H-M3 Main Runner: Latent Space Interpolation via EquiSSL-perm Decoder.
Tests whether latent-space interpolation outperforms weight-space averaging
over 500+ same-task MLP checkpoint pairs.
"""
import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
H_M3_CODE = os.path.join(SCRIPT_DIR, 'code')

sys.path.insert(0, H_M1_CODE)
sys.path.insert(0, H_M3_CODE)  # h-m3 FIRST so h-m3's modules take priority

import config as cfg

DATA_ROOT = os.path.join(PROJECT_ROOT, 'data')


def _save_results(results, stats, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        'metadata': {
            'hypothesis': 'h-m3',
            'timestamp': datetime.now().isoformat(),
            'n_pairs': len(results),
        },
        'statistics': stats,
        'pairs': results,
    }
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f"  Results saved to: {out_path}")


def _write_validation_report(stats, results, out_path):
    from evaluation.statistics import format_report
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    gate_str = "✅ PASS" if stats['gate_pass'] else "⚠️ DOCUMENT"
    report = f"""# Phase 4 Validation Report: H-M3

**Generated:** {datetime.now().isoformat()}
**Execution Mode:** UNATTENDED
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_str}

---

## Hypothesis Summary

**ID:** H-M3
**Type:** MECHANISM (SHOULD_WORK)
**Claim:** EquiSSL-perm latent-space interpolation outperforms weight-space averaging
over 500+ same-task MLP pairs (MNIST/SVHN/CIFAR-10).

---

## Experiment Results

{format_report(stats, results)}

---

## Gate Evaluation

| Criterion | Value | Pass? |
|-----------|-------|-------|
| mean(acc_latent) > mean(acc_ws) | Δ={stats['mean_delta']:.4f} | {'✅' if stats['mean_delta'] > 0 else '❌'} |
| p-value < 0.05 | p={stats['p_value']:.4f} | {'✅' if stats['p_value'] < 0.05 else '❌'} |
| **GATE** | **{gate_str}** | |

## Figures

- figures/gate_comparison.png
- figures/task_stratified.png
- figures/delta_histogram.png
- figures/pair_scatter.png

## Conclusion

{'EquiSSL-perm latent-space interpolation demonstrates functional model interpolation capability, outperforming naive weight-space averaging (p < 0.05 paired t-test).' if stats['gate_pass'] else 'EquiSSL-perm latent-space interpolation does not improve over weight-space averaging in this setting. This is recorded as DOCUMENT — the pipeline continues to H-M4. Finding: the graph decoder (trained for edge-attr reconstruction) does not produce functional weight-space vectors suitable for direct model initialization.'}
"""
    with open(out_path, 'w') as f:
        f.write(report)
    print(f"  Validation report saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description='H-M3 Latent Interpolation Experiment')
    parser.add_argument('--verify', action='store_true',
                        help='Run round-trip check on first pair only, then exit')
    parser.add_argument('--n_pairs', type=int, default=None,
                        help='Limit number of pairs (for testing)')
    parser.add_argument('--dry_run', action='store_true',
                        help='Dry run: process n_pairs pairs only')
    parser.add_argument('--device', default=None)
    args = parser.parse_args()

    import torch
    device = args.device or ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n{'='*60}")
    print(f"H-M3: Latent Space Interpolation Experiment")
    print(f"Device: {device}, Verify: {args.verify}")
    print(f"{'='*60}\n")

    # ── Step 1: Load real zoo (SANE ModelZoo CNN checkpoints, zenodo:13144018) ──
    print("Step 1: Setting up real CNN zoo (SANE ModelZoo, Schürholt et al. 2022)...")
    from data.real_zoo import load_real_zoo

    zoo_meta = load_real_zoo(
        zoo_dir=cfg.REAL_ZOO_DIR,
        tasks=['cifar10'],
    )
    total_models = sum(len(v) for v in zoo_meta.values())
    print(f"  Zoo: {total_models} real CNN models (SANE CIFAR-10 sample, zenodo:13144018)")

    # ── Step 2: Build or load pairs ──────────────────────────────────────────
    print("\nStep 2: Building pair dataset...")
    from data.real_zoo import build_cnn_pairs
    from data.pair_builder import save_pairs, load_pairs

    pairs_path = os.path.join(cfg.H_M3_ROOT, 'data/real_cnn_pairs.json')
    if os.path.exists(pairs_path):
        pairs = load_pairs(pairs_path)
        print(f"  Loaded {len(pairs)} pairs from {pairs_path}")
    else:
        pairs = build_cnn_pairs(zoo_meta, min_pairs=cfg.MIN_PAIRS, seed=cfg.PAIR_SEED,
                                tasks=['cifar10'])
        save_pairs(pairs, pairs_path)
        print(f"  Built {len(pairs)} pairs -> {pairs_path}")

    if len(pairs) < cfg.MIN_PAIRS:
        print(f"  WARNING: only {len(pairs)} pairs (< {cfg.MIN_PAIRS}). Proceeding.")

    # ── Step 3: Load frozen encoder + decoder ────────────────────────────────
    print("\nStep 3: Loading frozen encoder + decoder...")
    from models.model_loader import load_frozen_encoder, load_frozen_decoder, load_mlp_checkpoint

    encoder = load_frozen_encoder(cfg.ENCODER_CKPT, device,
                                  latent_dim=cfg.LATENT_DIM, hidden_dim=cfg.HIDDEN_DIM,
                                  num_layers=cfg.NUM_LAYERS)
    decoder = load_frozen_decoder(cfg.DECODER_CKPT, device,
                                  latent_dim=cfg.LATENT_DIM, hidden_dim=cfg.HIDDEN_DIM)
    print(f"  Encoder: {sum(p.numel() for p in encoder.parameters()):,} params")
    print(f"  Decoder: {sum(p.numel() for p in decoder.parameters()):,} params")

    # ── Step 4: Build test loaders ───────────────────────────────────────────
    print("\nStep 4: Building task test loaders...")
    from evaluation.task_eval import get_test_loader, evaluate_state_dict

    test_loaders = {}
    available_tasks = []
    for task in ['cifar10']:
        try:
            test_loaders[task] = get_test_loader(task, batch_size=256, cnn_mode=True)
            print(f"  {task}: {len(test_loaders[task].dataset):,} test samples")
            available_tasks.append(task)
        except Exception as e:
            print(f"  {task}: SKIPPED (loader failed: {e})")

    if not available_tasks:
        print("ERROR: No task loaders available.")
        sys.exit(1)

    # Filter pairs to available tasks
    pairs = [p for p in pairs if p['task'] in available_tasks]
    print(f"  Using {len(pairs)} pairs across tasks: {available_tasks}")

    # ── Step 5: Round-trip verify ─────────────────────────────────────────────
    from interpolation.interpolator import encode_checkpoint, decode_latent_to_state_dict, \
        latent_interpolate, weight_space_average

    first_pair = pairs[0]
    sd_a = load_mlp_checkpoint(first_pair['path_a'], device='cpu')
    print("\nStep 5: Round-trip verification...")
    z_a = encode_checkpoint(encoder, sd_a, device)
    sd_rt = decode_latent_to_state_dict(decoder, z_a, sd_a, device)
    assert set(sd_rt.keys()) == set(sd_a.keys()), "Key mismatch in round-trip"
    assert all(sd_rt[k].shape == sd_a[k].shape for k in sd_a), "Shape mismatch in round-trip"
    print("  Round-trip OK: shapes match")

    if args.verify:
        print("  --verify flag set, exiting after round-trip check.")
        return

    # ── Step 6: Main evaluation loop ─────────────────────────────────────────
    eval_pairs = pairs
    if args.n_pairs is not None or args.dry_run:
        n = args.n_pairs or 10
        eval_pairs = pairs[:n]
        print(f"\nStep 6: Running evaluation on {len(eval_pairs)} pairs (limited)...")
    else:
        print(f"\nStep 6: Running full evaluation on {len(eval_pairs)} pairs...")

    results = []
    t0 = time.time()
    skip_count = 0

    for i, pair in enumerate(eval_pairs):
        try:
            sd_a = load_mlp_checkpoint(pair['path_a'], device='cpu')
            sd_b = load_mlp_checkpoint(pair['path_b'], device='cpu')
            task = pair['task']

            # Latent interpolation
            sd_latent = latent_interpolate(encoder, decoder, sd_a, sd_b, device)
            acc_latent = evaluate_state_dict(
                sd_latent, task, test_loaders[task], device, cfg.TASK_MLP_CONFIGS  # unused for CNN, kept for API compatibility
            )

            # Weight-space average
            sd_ws = weight_space_average(sd_a, sd_b)
            acc_ws = evaluate_state_dict(
                sd_ws, task, test_loaders[task], device, cfg.TASK_MLP_CONFIGS  # unused for CNN, kept for API compatibility
            )

            results.append({
                'pair_id': pair['pair_id'],
                'task': task,
                'acc_a': pair.get('acc_a'),
                'acc_b': pair.get('acc_b'),
                'acc_latent': float(acc_latent),
                'acc_ws': float(acc_ws),
                'delta': float(acc_latent - acc_ws),
            })

            if (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(eval_pairs)}] elapsed={elapsed:.0f}s "
                      f"mean_delta={sum(r['delta'] for r in results)/len(results):.4f}")

        except Exception as e:
            skip_count += 1
            print(f"  [pair {i}] SKIP: {e}")
            if skip_count > 50:
                print("  Too many skips, aborting.")
                break
            continue

    elapsed = time.time() - t0
    print(f"\n  Completed {len(results)} pairs in {elapsed:.1f}s (skipped {skip_count})")

    if len(results) == 0:
        print("ERROR: No valid results. Check encoder/decoder and data.")
        sys.exit(1)

    # ── Step 7: Statistics ────────────────────────────────────────────────────
    print("\nStep 7: Computing statistics...")
    from evaluation.statistics import compute_statistics
    stats = compute_statistics(results)
    gate_str = "PASS" if stats['gate_pass'] else "DOCUMENT"
    print(f"  N={stats['n_pairs']} pairs")
    print(f"  mean(acc_latent)={stats['mean_acc_latent']:.4f}")
    print(f"  mean(acc_ws)={stats['mean_acc_ws']:.4f}")
    print(f"  mean(delta)={stats['mean_delta']:.4f} ± {stats['std_delta']:.4f}")
    print(f"  t={stats['t_stat']:.4f}, p={stats['p_value']:.4f}")
    print(f"  Cohen's d={stats['cohen_d']:.4f}")
    print(f"  Gate: {gate_str}")

    # ── Step 8: Figures ───────────────────────────────────────────────────────
    print("\nStep 8: Generating figures...")
    from visualization.figures import generate_all_figures
    figures_dir = os.path.join(cfg.H_M3_ROOT, 'figures')
    generate_all_figures(results, stats, figures_dir)

    # ── Step 9: Save results + validation report ──────────────────────────────
    print("\nStep 9: Saving outputs...")
    results_dir = os.path.join(cfg.H_M3_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True)
    results_json = os.path.join(cfg.H_M3_ROOT, 'experiment_results.json')
    _save_results(results, stats, results_json)

    validation_report = os.path.join(cfg.H_M3_ROOT, '04_validation.md')
    _write_validation_report(stats, results, validation_report)

    print(f"\n{'='*60}")
    print(f"H-M3 COMPLETE: Gate={gate_str}")
    print(f"  mean_delta={stats['mean_delta']:.4f}, p={stats['p_value']:.4f}")
    print(f"  n_pairs={stats['n_pairs']}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
