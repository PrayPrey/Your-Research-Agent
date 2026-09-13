"""H-M3 experiment orchestrator."""
import os
import sys
import json
import argparse
import numpy as np
import torch
from sklearn.linear_model import Ridge
from pathlib import Path

from config import ExperimentConfig, DEFAULT_CONFIG
from data_prep import load_and_flatten, make_splits, CONDITION_FNS, verify_canonicalization_activated
from model import CanonicalWeightEncoder
from train import set_seed, make_dataloaders, train_condition, run_frozen_encoder_experiment
from evaluate import bootstrap_spearman, aggregate_seeds, check_p1, check_p2
from figures import generate_all_figures


def run_experiment(config: ExperimentConfig):
    print("=" * 60)
    print(f"H-M3: NFT with Weight Symmetry Canonicalization")
    print("=" * 60)

    # Load data
    X, Y, label_names = load_and_flatten()
    X_train, Y_train, X_val, Y_val, X_test, Y_test = make_splits(
        X, Y, val_fraction=config.val_fraction, test_fraction=config.test_fraction
    )
    print(f"Split: train={X_train.shape[0]}, val={X_val.shape[0]}, test={X_test.shape[0]}")

    # Verify canonicalization on small sample
    print("\nVerifying canonicalization:")
    for cond in ['A', 'B', 'C', 'D', 'E']:
        X_sample = X_train[:8]
        X_canon = CONDITION_FNS[cond](X_sample)
        ok, indicators = verify_canonicalization_activated(cond, X_sample, X_canon)
        print(f"  Condition {cond}: {ok} {indicators}")

    # Filter conditions to run
    conditions_to_run = config.conditions

    # Per-seed results
    per_seed_rhos = []
    cond_a_checkpoint = None

    for seed in config.seeds:
        print(f"\n--- Seed {seed} ---")
        seed_rhos = {}

        for cond in conditions_to_run:
            print(f"  Condition {cond}...")
            set_seed(seed)

            if cond == 'F':
                # Linear regressor baseline (no NFT)
                X_tr_c = CONDITION_FNS['D'](X_train)
                X_te_c = CONDITION_FNS['D'](X_test)
                reg = Ridge(alpha=1.0)
                reg.fit(X_tr_c, Y_train)
                preds = reg.predict(X_te_c)
            else:
                encoder = CanonicalWeightEncoder(
                    condition=cond,
                    embed_dim=config.embed_dim, n_layers=config.n_layers,
                    nhead=config.nhead, dim_feedforward=config.dim_feedforward,
                    dropout=config.dropout,
                )
                ckpt_dir = os.path.join(os.path.dirname(__file__), config.checkpoint_dir)
                ckpt_path = os.path.join(ckpt_dir, f"cond_{cond}_seed{seed}.pt")
                loader_train, loader_val = make_dataloaders(
                    X_train, Y_train, X_val, Y_val,
                    batch_size=config.batch_size, seed=seed
                )
                train_result = train_condition(
                    encoder, loader_train, loader_val, config,
                    seed=seed, checkpoint_path=ckpt_path
                )
                print(f"    best_val_rho={train_result['best_val_rho']:.4f} "
                      f"epochs={train_result['best_epoch']}")

                if cond == 'A' and seed == config.seeds[0]:
                    cond_a_checkpoint = ckpt_path

                # Evaluate on test
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                encoder.eval()
                with torch.no_grad():
                    X_te_t = torch.tensor(X_test, dtype=torch.float32)
                    # Batch to avoid OOM
                    preds_list = []
                    for i in range(0, len(X_te_t), config.batch_size):
                        batch = X_te_t[i:i + config.batch_size].to(device)
                        preds_list.append(encoder(batch).cpu().numpy())
                    preds = np.concatenate(preds_list, axis=0)

            seed_rhos[cond] = {}
            for i, label in enumerate(label_names):
                rho, ci_lo, ci_hi = bootstrap_spearman(
                    preds[:, i], Y_test[:, i],
                    n_boot=config.n_boot, seed=config.boot_seed
                )
                seed_rhos[cond][label] = (rho, ci_lo, ci_hi)
                print(f"    {label}: ρ={rho:.4f} [{ci_lo:.4f}, {ci_hi:.4f}]")

        per_seed_rhos.append(seed_rhos)

    # Aggregate across seeds
    agg_results = aggregate_seeds(per_seed_rhos)

    print("\n=== Aggregated Results ===")
    for cond in conditions_to_run:
        for label in label_names:
            r = agg_results[cond][label]
            print(f"  {cond} {label}: ρ_mean={r['rho_mean']:.4f} "
                  f"[{r['ci_lo']:.4f}, {r['ci_hi']:.4f}]")

    # Gate checks
    p1_results = {}
    for label in label_names:
        rho_D = agg_results['D'][label]['rho_mean']
        ci_D = (agg_results['D'][label]['ci_lo'], agg_results['D'][label]['ci_hi'])
        rho_A = agg_results['A'][label]['rho_mean']
        ci_A = (agg_results['A'][label]['ci_lo'], agg_results['A'][label]['ci_hi'])
        p1_results[label] = check_p1(rho_D, ci_D, rho_A, ci_A,
                                      delta_threshold=config.delta_threshold)

    p2_result = check_p2({c: {l: agg_results[c][l]['rho_mean']
                               for l in label_names}
                           for c in conditions_to_run})

    print("\n=== Gate Check P1 (Δρ_D-A ≥ 0.05, CI excl 0) ===")
    for label, p1 in p1_results.items():
        print(f"  {label}: pass={p1['pass']} Δρ={p1['delta_rho']:+.4f} "
              f"CI_excl0={p1['ci_excludes_zero']}")

    print(f"\n=== Gate Check P2 (ρ_D > ρ_E on ≥2/3 tasks) ===")
    print(f"  pass={p2_result['pass']} n_pass={p2_result['n_pass']}/3 "
          f"per_task={p2_result['per_task']}")

    gate_pass = any(p1['pass'] for p1 in p1_results.values()) and p2_result['pass']
    print(f"\n>>> GATE (SHOULD_WORK): {'PASS' if gate_pass else 'FAIL'} <<<")

    # Frozen encoder sub-experiment
    frozen_results = {}
    if config.run_frozen_experiment and cond_a_checkpoint and os.path.exists(cond_a_checkpoint):
        print("\n--- Frozen Encoder Sub-Experiment ---")
        full_rhos = {c: {l: agg_results[c][l]['rho_mean']
                         for l in label_names}
                     for c in conditions_to_run}
        frozen_results = run_frozen_encoder_experiment(
            cond_a_checkpoint, X_train, Y_train, X_val, Y_val, X_test, Y_test,
            config, full_rhos
        )
        for cond, res in frozen_results.items():
            print(f"  {cond}: frozen={res['rho_frozen']} full={res['rho_full']}")
    else:
        print("Skipping frozen encoder experiment (no checkpoint or disabled).")

    # Save results
    results_output = {
        'agg_results': agg_results,
        'per_seed_rhos': [
            {c: {l: list(v) for l, v in cond_rhos.items()}
             for c, cond_rhos in seed_r.items()}
            for seed_r in per_seed_rhos
        ],
        'p1_results': p1_results,
        'p2_result': p2_result,
        'gate_pass': gate_pass,
        'frozen_results': {
            c: {
                'rho_frozen': v['rho_frozen'],
                'rho_full': v['rho_full'],
            } for c, v in frozen_results.items()
        } if frozen_results else {},
        'config': {
            'conditions': config.conditions,
            'seeds': config.seeds,
            'n_labels': config.n_labels,
            'label_names': config.label_names,
        },
    }
    results_path = os.path.join(os.path.dirname(__file__), config.results_path)
    with open(results_path, 'w') as f:
        json.dump(results_output, f, indent=2, default=float)
    print(f"\nResults saved to {results_path}")

    # Generate figures
    figures_dir = os.path.join(os.path.dirname(__file__), config.figures_dir)
    generate_all_figures(agg_results, label_names, p1_results, p2_result,
                         frozen_results, figures_dir)

    return results_output


def parse_args():
    parser = argparse.ArgumentParser(description="H-M3 experiment")
    parser.add_argument('--conditions', nargs='+',
                        default=['A', 'B', 'C', 'D', 'E', 'F'])
    parser.add_argument('--seeds', nargs='+', type=int, default=[42, 123, 456])
    parser.add_argument('--max-epochs', type=int, default=100)
    parser.add_argument('--no-frozen', action='store_true')
    parser.add_argument('--batch-size', type=int, default=64)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = ExperimentConfig(
        conditions=args.conditions,
        seeds=args.seeds,
        max_epochs=args.max_epochs,
        run_frozen_experiment=not args.no_frozen,
        batch_size=args.batch_size,
    )
    run_experiment(config)
