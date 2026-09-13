"""
H-M1 experiment launcher. Called from conda env with env vars set.
"""
import sys, os

H_M1_CODE = os.environ['H_M1_CODE']
H_E1_CODE = os.environ['H_E1_CODE']
CNN_ZOO   = os.environ['CNN_ZOO']
PROJ_ROOT = os.environ['PROJECT_ROOT']

# H_M1_CODE must come FIRST so its modules shadow H_E1's
# H_E1_CODE second so shared modules (data, models) fall back to it
sys.path.insert(0, H_E1_CODE)  # fallback for data/, models/, training/ base
sys.path.insert(0, H_M1_CODE)  # priority: config.py, training/train_equi_perm.py
os.environ['H_E1_CODE'] = H_E1_CODE

import config  # resolves from H_M1_CODE (inserted first)
config.H_E1_CODE      = H_E1_CODE
config.MULTIZOO_ROOT  = CNN_ZOO

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--skip-training', action='store_true')
parser.add_argument('--epochs', type=int, default=config.EPOCHS)
parser.add_argument('--seeds', nargs='+', type=int, default=config.SEEDS)
parser.add_argument('--device', default='cuda')
args = parser.parse_args()

seeds  = args.seeds
device = args.device
epochs = args.epochs

print(f'\n{"="*60}')
print(f'H-M1: Graph Representation Mechanism (Linear Probe R²)')
print(f'Seeds={seeds}  Epochs={epochs}  Device={device}')
print(f'{"="*60}\n')

# ── 1. Train EquiSSL-perm ─────────────────────────────────────────────────────
if not args.skip_training:
    print('=== Step 1: Train EquiSSL-perm (perm-only augmentation) ===')
    from training.train_equi_perm import train_all_seeds
    train_all_seeds(seeds, config.CHECKPOINT_DIR, config.RESULTS_DIR,
                    CNN_ZOO, device=device, epochs=epochs)
else:
    print('=== Step 1: Skipped (--skip-training) ===')

# ── 2. Extract embeddings ─────────────────────────────────────────────────────
print('\n=== Step 2: Extract embeddings ===')
from evaluation.extract_embeddings import extract_all_embeddings, get_accuracy_labels
embeddings_dict, vit_dataset = extract_all_embeddings(
    seeds=seeds,
    vit_zoo_root=config.VIT_ZOO_ROOT,
    he1_ckpt_dir=config.H_E1_CKPT_DIR,
    hm1_ckpt_dir=config.CHECKPOINT_DIR,
    results_dir=config.RESULTS_DIR,
    device=device,
)
labels = get_accuracy_labels(vit_dataset)
print(f'  Embeddings: {list(embeddings_dict.keys())}')
print(f'  Labels: N={len(labels)} range=[{labels.min():.3f}, {labels.max():.3f}]')

# ── 3. Linear probe ───────────────────────────────────────────────────────────
print('\n=== Step 3: Linear probe R² ===')
from evaluation.linear_probe import evaluate_all_models, run_significance_tests, evaluate_gate
results = evaluate_all_models(embeddings_dict, labels, seeds,
                              alphas=config.RIDGE_ALPHAS)

# ── 4. Significance tests ─────────────────────────────────────────────────────
print('\n=== Step 4: Significance tests ===')
stat_tests = run_significance_tests(results)

# ── 5. Gate ───────────────────────────────────────────────────────────────────
print('\n=== Step 5: MUST_WORK gate ===')
gate_result = evaluate_gate(results, stat_tests)
print(f'  Gate: {gate_result}')

# ── 6. Figures ────────────────────────────────────────────────────────────────
print('\n=== Step 6: Figures ===')
from evaluation.figures import generate_all_figures
generate_all_figures(results, stat_tests, embeddings_dict, labels,
                     config.FIGURES_DIR, n_seeds=len(seeds))

# ── 7. Save results ───────────────────────────────────────────────────────────
import json, time
os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
exp_results = {
    'hypothesis_id': 'h-m1',
    'gate_result': gate_result,
    'seeds': seeds,
    'n_vit_models': int(len(vit_dataset)),
    'models': {
        m: {'r2_mean': float(r.r2_mean), 'r2_std': float(r.r2_std),
            'r2_per_seed': [float(x) for x in r.r2_per_seed]}
        for m, r in results.items()
    },
    'significance_tests': {
        m: {'t_stat': float(t.t_stat), 'p_value': float(t.p_value),
            'significant': bool(t.significant)}
        for m, t in stat_tests.items()
    },
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
}

results_path = os.path.join(PROJ_ROOT, 'docs/youra_research/h-m1/experiment_results.json')
with open(results_path, 'w') as f:
    json.dump(exp_results, f, indent=2)
print(f'\nResults: {results_path}')

csv_path = os.path.join(config.OUTPUTS_DIR, 'results.csv')
with open(csv_path, 'w') as f:
    f.write('model,r2_mean,r2_std,significant\n')
    for m, r in results.items():
        sig = stat_tests.get(m)
        f.write(f'{m},{r.r2_mean:.6f},{r.r2_std:.6f},'
                f'{sig.significant if sig else False}\n')

print(f'\n{"="*60}')
print(f'EXPERIMENT COMPLETE — Gate: {gate_result}')
for m, r in results.items():
    print(f'  {m:15s}: R²={r.r2_mean:.4f} ± {r.r2_std:.4f}')
print(f'{"="*60}')
