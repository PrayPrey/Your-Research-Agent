"""
H-M1 Experiment: Graph representation as cross-architecture generalization mechanism.
Compares SANE, EquiSSL (monomial), EquiSSL-perm (permutation) via linear probe R² on ViT zoo.
"""
import argparse
import json
import os
import sys
import time

# Setup paths
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.environ.get('PROJECT_ROOT',
    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_E1_CODE = os.environ.get('H_E1_CODE',
    os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/code'))
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, H_E1_CODE)
os.environ['H_E1_CODE'] = H_E1_CODE

import config

DEVICE = 'cuda'


def main():
    parser = argparse.ArgumentParser(description='H-M1 experiment')
    parser.add_argument('--skip-training', action='store_true',
                        help='Skip EquiSSL-perm training, use existing checkpoints')
    parser.add_argument('--seeds', nargs='+', type=int, default=config.SEEDS,
                        help='Seeds to use')
    parser.add_argument('--device', default=DEVICE)
    args = parser.parse_args()

    device = args.device
    seeds = args.seeds
    print(f'\n{"="*60}')
    print(f'H-M1 Experiment: Linear Probe R² on ViT Zoo')
    print(f'Seeds: {seeds}, Device: {device}')
    print(f'{"="*60}\n')

    # ── Step 1: Train EquiSSL-perm (permutation-only) ────────────────────────
    if not args.skip_training:
        print('Step 1: Training EquiSSL-perm (permutation-only augmentation)...')
        from training.train_equi_perm import train_all_seeds
        multizoo_root = os.path.join(PROJECT_ROOT, 'data/multizoo')
        if not os.path.isdir(multizoo_root):
            # Try H-E1's data directory
            multizoo_root = os.path.join(H_E1_CODE, 'data/multizoo')
        if not os.path.isdir(multizoo_root):
            # Use SANE MultiZoo from known location
            multizoo_root = os.environ.get('MULTIZOO_ROOT', multizoo_root)
        train_all_seeds(seeds, config.CHECKPOINT_DIR, config.RESULTS_DIR,
                        multizoo_root, device=device)
    else:
        print('Step 1: Skipped (--skip-training)')

    # ── Step 2: Extract all embeddings ───────────────────────────────────────
    print('\nStep 2: Extracting embeddings...')
    from evaluation.extract_embeddings import extract_all_embeddings, get_accuracy_labels

    embeddings_dict, vit_dataset = extract_all_embeddings(
        seeds=seeds,
        vit_zoo_root=config.VIT_ZOO_ROOT,
        he1_ckpt_dir=config.H_E1_CKPT_DIR,
        hm1_ckpt_dir=config.CHECKPOINT_DIR,
        results_dir=config.RESULTS_DIR,
        device=device,
    )
    print(f'  Extracted {len(embeddings_dict)} embedding arrays')
    labels = get_accuracy_labels(vit_dataset)
    print(f'  Labels: {len(labels)} models, '
          f'range=[{labels.min():.3f}, {labels.max():.3f}]')

    # ── Step 3: Linear probe evaluation ──────────────────────────────────────
    print('\nStep 3: Linear probe evaluation...')
    from evaluation.linear_probe import evaluate_all_models, run_significance_tests, evaluate_gate

    results = evaluate_all_models(embeddings_dict, labels, seeds,
                                  alphas=config.RIDGE_ALPHAS)

    # ── Step 4: Significance tests ────────────────────────────────────────────
    print('\nStep 4: Significance tests...')
    stat_tests = run_significance_tests(results)

    # ── Step 5: Gate evaluation ───────────────────────────────────────────────
    print('\nStep 5: Gate evaluation (MUST_WORK)...')
    gate_result = evaluate_gate(results, stat_tests)
    print(f'  Gate result: {gate_result}')

    # ── Step 6: Generate figures ──────────────────────────────────────────────
    print('\nStep 6: Generating figures...')
    from evaluation.figures import generate_all_figures
    generate_all_figures(results, stat_tests, embeddings_dict, labels,
                         config.FIGURES_DIR, n_seeds=len(seeds))

    # ── Step 7: Save experiment results ───────────────────────────────────────
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    exp_results = {
        'hypothesis_id': 'h-m1',
        'gate_result': gate_result,
        'seeds': seeds,
        'n_vit_models': int(len(vit_dataset)),
        'models': {
            m: {
                'r2_mean': float(r.r2_mean),
                'r2_std': float(r.r2_std),
                'r2_per_seed': [float(x) for x in r.r2_per_seed],
            }
            for m, r in results.items()
        },
        'significance_tests': {
            m: {
                't_stat': float(t.t_stat),
                'p_value': float(t.p_value),
                'significant': bool(t.significant),
            }
            for m, t in stat_tests.items()
        },
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }

    results_path = os.path.join(
        PROJECT_ROOT, 'docs/youra_research/h-m1/experiment_results.json')
    with open(results_path, 'w') as f:
        json.dump(exp_results, f, indent=2)
    print(f'  Saved results: {results_path}')

    # Also save CSV
    csv_path = os.path.join(config.OUTPUTS_DIR, 'results.csv')
    with open(csv_path, 'w') as f:
        f.write('model,r2_mean,r2_std,significant\n')
        for m, r in results.items():
            sig = stat_tests.get(m, None)
            f.write(f'{m},{r.r2_mean:.6f},{r.r2_std:.6f},'
                    f'{sig.significant if sig else False}\n')
    print(f'  Saved CSV: {csv_path}')

    # ── Step 8: Print summary ─────────────────────────────────────────────────
    print(f'\n{"="*60}')
    print(f'H-M1 EXPERIMENT COMPLETE')
    print(f'Gate: {gate_result}')
    print(f'{"="*60}')
    for m, r in results.items():
        print(f'  {m:15s}: R²={r.r2_mean:.4f} ± {r.r2_std:.4f}')

    return exp_results


if __name__ == '__main__':
    main()
