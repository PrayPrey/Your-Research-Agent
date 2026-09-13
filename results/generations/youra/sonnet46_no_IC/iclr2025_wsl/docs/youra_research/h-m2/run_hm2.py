"""
H-M2 Ablation Pipeline: Scale vs Permutation Equivariance.
Orchestrates steps D-1 through A-7 per 03_tasks.yaml.
"""
import os
import sys
import json
import numpy as np
import torch

PROJECT_ROOT = os.environ.get('PROJECT_ROOT',
    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
HM1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
HM2_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m2/code')
if HM1_CODE not in sys.path:
    sys.path.insert(0, HM1_CODE)
if HM2_CODE not in sys.path:
    sys.path.insert(0, HM2_CODE)

from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split

# Import h-m2 specific config/stats via direct path to avoid collision with h-m1 'evaluation'
import importlib.util as _ilu

def _load_module(name, path):
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_cfg_mod = _load_module('config_hm2', os.path.join(HM2_CODE, 'config_hm2.py'))
HM2PathConfig = _cfg_mod.HM2PathConfig
AblationConfig = _cfg_mod.AblationConfig

_delta_mod = _load_module('delta_r2_analysis',
    os.path.join(HM2_CODE, 'evaluation', 'delta_r2_analysis.py'))
compute_delta_r2_stats = _delta_mod.compute_delta_r2_stats


def _get_paired_split(n, seed, test_frac=0.2):
    rng = np.random.RandomState(seed)
    idx = np.arange(n)
    train_idx, test_idx = train_test_split(idx, test_size=test_frac, random_state=rng)
    return train_idx, test_idx


def _probe_with_split(z, labels, train_idx, test_idx, alphas=None):
    if alphas is None:
        alphas = [0.1, 1.0, 10.0, 100.0]
    ridge = RidgeCV(alphas=alphas)
    ridge.fit(z[train_idx], labels[train_idx])
    return float(ridge.score(z[test_idx], labels[test_idx]))


def get_perm_ckpt_path(seed, paths: HM2PathConfig):
    if seed == 0:
        return os.path.join(paths.hm1_checkpoint_dir, 'equi_perm_seed0.pt')
    return os.path.join(paths.checkpoint_dir, f'equi_perm_seed{seed}.pt')


def get_equi_ckpt_path(seed, paths: HM2PathConfig):
    # h-e1 checkpoints use subdirectory structure: seed{i}/equissl_lam0.1_seed{i}_best.pt
    return os.path.join(paths.he1_checkpoint_dir,
                        f'seed{seed}', f'equissl_lam0.1_seed{seed}_best.pt')


def train_missing_perm_seeds(seeds, paths: HM2PathConfig, device='cuda', epochs=100):
    """Train EquiSSL-perm for seeds that don't have checkpoints yet."""
    from training.train_equi_perm import train_equi_perm
    trained = []
    for seed in seeds:
        ckpt_path = get_perm_ckpt_path(seed, paths)
        if os.path.exists(ckpt_path):
            print(f"[A-2] Seed {seed}: checkpoint exists, skip training")
            trained.append(ckpt_path)
            continue
        if not os.path.exists(paths.multizoo_root):
            print(f"[A-2] WARNING: multizoo_root {paths.multizoo_root} missing — skip seed {seed}")
            continue
        print(f"[A-2] Training EquiSSL-perm seed {seed}...")
        result = train_equi_perm(
            seed=seed,
            checkpoint_dir=paths.checkpoint_dir,
            results_dir=paths.results_dir,
            multizoo_root=paths.multizoo_root,
            device=device,
            epochs=epochs,
        )
        trained.append(result)
    return trained


def run_hm2_ablation(seeds, paths: HM2PathConfig, device='cuda'):
    """Full H-M2 ablation. Returns results dict."""
    from evaluation.extract_embeddings import extract_graph_embeddings, load_equissl_encoder, get_accuracy_labels
    from data.vitzoo_graph_dataset import ViTZooGraphDataset

    print("[D-2] Loading ViT Model Zoo dataset...")
    vit_dataset = ViTZooGraphDataset(root=paths.vit_zoo_root)
    labels = np.array(get_accuracy_labels(vit_dataset))
    n_vit = len(vit_dataset)
    print(f"  Loaded {n_vit} ViT models")

    r2_equissl = {}
    r2_perm = {}
    z_equi_seed0 = None
    z_perm_seed0 = None

    valid_seeds = []
    for seed in seeds:
        equi_ckpt = get_equi_ckpt_path(seed, paths)
        perm_ckpt = get_perm_ckpt_path(seed, paths)

        if not os.path.exists(equi_ckpt):
            print(f"[A-3] WARNING: EquiSSL ckpt missing for seed {seed}: {equi_ckpt} — skip")
            continue
        if not os.path.exists(perm_ckpt):
            print(f"[A-3] WARNING: EquiSSL-perm ckpt missing for seed {seed}: {perm_ckpt} — skip")
            continue

        valid_seeds.append(seed)
        print(f"[A-3] Extracting embeddings for seed {seed}...")
        enc_equi = load_equissl_encoder(equi_ckpt, symmetry='monomial', device=device)
        z_equi = extract_graph_embeddings(enc_equi, vit_dataset, device=device)

        enc_perm = load_equissl_encoder(perm_ckpt, symmetry='permutation', device=device)
        z_perm = extract_graph_embeddings(enc_perm, vit_dataset, device=device)

        if seed == 0:
            z_equi_seed0 = z_equi
            z_perm_seed0 = z_perm

        train_idx, test_idx = _get_paired_split(n_vit, seed)
        r2_equissl[seed] = _probe_with_split(z_equi, labels, train_idx, test_idx)
        r2_perm[seed] = _probe_with_split(z_perm, labels, train_idx, test_idx)
        print(f"  seed {seed}: EquiSSL R²={r2_equissl[seed]:.4f}, EquiSSL-perm R²={r2_perm[seed]:.4f}")

    if not valid_seeds:
        raise RuntimeError("No valid seeds found — missing checkpoints")

    r2_equi_list = [r2_equissl[s] for s in valid_seeds]
    r2_perm_list = [r2_perm[s] for s in valid_seeds]

    stats = compute_delta_r2_stats(r2_equi_list, r2_perm_list)
    print(f"\n[A-5] ΔR² mean={stats['mean']:.4f} ± {stats['std']:.4f}")
    print(f"  95% CI: [{stats['ci_low']:.4f}, {stats['ci_high']:.4f}]")
    print(f"  t={stats['t_stat']:.4f}, p={stats['p_value']:.4f}")
    print(f"  Gate: {stats['gate']}")

    # MMD subpop comparison (A-6)
    mmd_results = {}
    if z_equi_seed0 is not None and z_perm_seed0 is not None:
        mmd_results = compute_mmd_subpop_comparison(z_equi_seed0, z_perm_seed0, labels)
        print(f"[A-6] MMD equi={mmd_results['mmd_equi']:.4f}, perm={mmd_results['mmd_perm']:.4f}")

    return {
        'seeds': valid_seeds,
        'r2_equissl': r2_equissl,
        'r2_perm': r2_perm,
        'r2_equi_list': r2_equi_list,
        'r2_perm_list': r2_perm_list,
        'delta_r2_stats': stats,
        'mmd': mmd_results,
        'z_equi_seed0': z_equi_seed0,
        'z_perm_seed0': z_perm_seed0,
        'labels': labels,
    }


def compute_mmd_subpop_comparison(z_equi, z_perm, labels):
    """MMD between high/low accuracy subpopulations for both encoders."""
    try:
        from evaluation.mmd_eval import compute_mmd
        threshold = float(np.median(labels))

        def subpop_mmd(z, threshold):
            z_high = z[labels >= threshold]
            z_low = z[labels < threshold]
            if len(z_high) < 2 or len(z_low) < 2:
                return float('nan')
            t_high = torch.from_numpy(z_high).float()
            t_low = torch.from_numpy(z_low).float()
            return compute_mmd(t_high, t_low)

        mmd_equi = subpop_mmd(z_equi, threshold)
        mmd_perm = subpop_mmd(z_perm, threshold)
        ratio = mmd_perm / mmd_equi if mmd_equi > 0 else float('nan')
        return {'mmd_equi': mmd_equi, 'mmd_perm': mmd_perm, 'ratio': ratio}
    except Exception as e:
        print(f"  MMD warning: {e}")
        return {}


def generate_figures(results, paths: HM2PathConfig, cfg: AblationConfig):
    """Generate 4 ablation figures (A-7)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.manifold import TSNE

    os.makedirs(paths.figures_dir, exist_ok=True)
    stats = results['delta_r2_stats']
    seeds = results['seeds']
    r2_equi_list = results['r2_equi_list']
    r2_perm_list = results['r2_perm_list']
    labels = results['labels']

    r2_equi_mean = float(np.mean(r2_equi_list))
    r2_equi_std = float(np.std(r2_equi_list, ddof=1)) if len(r2_equi_list) > 1 else 0.0
    r2_perm_mean = float(np.mean(r2_perm_list))
    r2_perm_std = float(np.std(r2_perm_list, ddof=1)) if len(r2_perm_list) > 1 else 0.0

    # Fig 1: Gate Metrics Bar
    fig, ax = plt.subplots(figsize=(7, 5))
    models_names = ['EquiSSL\n(scale+perm)', 'EquiSSL-perm\n(perm only)']
    means = [r2_equi_mean, r2_perm_mean]
    stds = [r2_equi_std, r2_perm_std]
    bars = ax.bar(models_names, means, yerr=stds, capsize=5,
                  color=['#2196F3', '#FF9800'], alpha=0.8)
    ax.axhline(cfg.sane_r2, color='gray', linestyle='--', label=f'SANE R²={cfg.sane_r2:.4f}')
    ax.axhline(cfg.sane_r2 + cfg.gate_threshold, color='red', linestyle=':',
               label=f'Gate threshold ({cfg.sane_r2:.4f}+0.05)')
    ax.set_ylabel('R² (ViT Zoo Accuracy Prediction)')
    ax.set_title('H-M2: EquiSSL vs EquiSSL-perm Linear Probe R²')
    ax.legend(fontsize=8)
    ax.set_ylim(0, max(means) + max(stds) + 0.05)
    plt.tight_layout()
    plt.savefig(os.path.join(paths.figures_dir, 'gate_metrics_bar.png'), dpi=150)
    plt.close()

    # Fig 2: ΔR² distribution
    delta = np.array(stats['delta_r2'])
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(seeds[:len(delta)], delta, color='steelblue', s=80, zorder=3, label='Per-seed ΔR²')
    ax.axhline(stats['mean'], color='blue', linestyle='-', label=f'Mean ΔR²={stats["mean"]:.4f}')
    if len(delta) > 1:
        ax.fill_between([-0.3, len(seeds) - 0.7],
                        stats['mean'] - stats['std'],
                        stats['mean'] + stats['std'],
                        alpha=0.2, color='blue', label='±1 std')
    ax.axhline(cfg.gate_threshold, color='red', linestyle='--',
               label=f'Gate threshold (Δ=0.05)')
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    gate_label = stats['gate']
    ax.text(0.98, 0.05, f'Gate: {gate_label}', transform=ax.transAxes,
            ha='right', fontsize=12, color='red' if gate_label == 'DOCUMENT' else 'green')
    ax.set_xlabel('Seed')
    ax.set_ylabel('ΔR² = R²(EquiSSL) − R²(EquiSSL-perm)')
    ax.set_title('H-M2: Per-Seed ΔR² Distribution')
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(paths.figures_dir, 'delta_r2_distribution.png'), dpi=150)
    plt.close()

    # Fig 3: t-SNE 2x2 panel
    z_equi = results.get('z_equi_seed0')
    z_perm = results.get('z_perm_seed0')
    if z_equi is not None and z_perm is not None:
        print("[A-7] Computing t-SNE (seed 0 embeddings)...")
        tsne = TSNE(n_components=2, max_iter=1000, random_state=0)
        z_all = np.concatenate([z_equi, z_perm], axis=0)
        proj = tsne.fit_transform(z_all)
        proj_equi = proj[:len(z_equi)]
        proj_perm = proj[len(z_equi):]

        l2_norms = np.linalg.norm(z_equi, axis=-1)  # use equi norms for scale proxy

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        cmap_acc = plt.cm.viridis
        cmap_norm = plt.cm.plasma

        for col, (proj, name) in enumerate([(proj_equi, 'EquiSSL'), (proj_perm, 'EquiSSL-perm')]):
            sc1 = axes[0, col].scatter(proj[:, 0], proj[:, 1], c=labels, cmap=cmap_acc, s=40)
            axes[0, col].set_title(f'{name}\n(colored by accuracy)')
            plt.colorbar(sc1, ax=axes[0, col], label='Accuracy')

            sc2 = axes[1, col].scatter(proj[:, 0], proj[:, 1], c=l2_norms, cmap=cmap_norm, s=40)
            axes[1, col].set_title(f'{name}\n(colored by L2 norm)')
            plt.colorbar(sc2, ax=axes[1, col], label='L2 norm')

        plt.suptitle('H-M2: t-SNE Latent Geometry (seed 0)', fontsize=13)
        plt.tight_layout()
        plt.savefig(os.path.join(paths.figures_dir, 'tsne_2x2_panel.png'), dpi=150)
        plt.close()

    # Fig 4: Ablation ladder
    fig, ax = plt.subplots(figsize=(9, 4))
    models = ['SANE\n(baseline)', 'EquiSSL-perm\n(perm only)', 'EquiSSL\n(scale+perm)']
    r2_vals = [cfg.sane_r2, r2_perm_mean, r2_equi_mean]
    r2_errs = [0.0, r2_perm_std, r2_equi_std]
    colors = ['#9E9E9E', '#FF9800', '#2196F3']
    bars = ax.barh(models, r2_vals, xerr=r2_errs, color=colors, alpha=0.85, capsize=4)
    for bar, val in zip(bars, r2_vals):
        ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                f'{val:.4f}', va='center', fontsize=10)
    ax.set_xlabel('R² (ViT Zoo Accuracy Prediction)')
    ax.set_title('H-M1+H-M2 Ablation Ladder: SANE → EquiSSL-perm → EquiSSL')
    ax.set_xlim(0, max(r2_vals) + 0.06)
    plt.tight_layout()
    plt.savefig(os.path.join(paths.figures_dir, 'ablation_ladder.png'), dpi=150)
    plt.close()

    print(f"[A-7] 4 figures saved to {paths.figures_dir}")


def save_results(results, paths: HM2PathConfig, cfg: AblationConfig):
    """Save hm2_results.json."""
    os.makedirs(paths.results_dir, exist_ok=True)
    stats = results['delta_r2_stats']
    r2_equi_list = results['r2_equi_list']
    r2_perm_list = results['r2_perm_list']

    out = {
        'hypothesis_id': 'h-m2',
        'gate_type': 'SHOULD_WORK',
        'gate_result': stats['gate'],
        'seeds': results['seeds'],
        'n_vit_models': len(results['labels']),
        'models': {
            'equissl': {
                'r2_per_seed': r2_equi_list,
                'r2_mean': float(np.mean(r2_equi_list)),
                'r2_std': float(np.std(r2_equi_list, ddof=1)) if len(r2_equi_list) > 1 else 0.0,
            },
            'equissl_perm': {
                'r2_per_seed': r2_perm_list,
                'r2_mean': float(np.mean(r2_perm_list)),
                'r2_std': float(np.std(r2_perm_list, ddof=1)) if len(r2_perm_list) > 1 else 0.0,
            },
        },
        'delta_r2': {
            'per_seed': stats['delta_r2'],
            'mean': stats['mean'],
            'std': stats['std'],
            'ci_95': [stats['ci_low'], stats['ci_high']],
            't_stat': stats['t_stat'],
            'p_value': stats['p_value'],
        },
        'sane_r2': cfg.sane_r2,
    }
    if results.get('mmd'):
        out['mmd'] = results['mmd']

    out_path = os.path.join(paths.results_dir, 'hm2_results.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"[A-8] Results saved to {out_path}")
    return out


def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[H-M2] Using device: {device}")

    paths = HM2PathConfig()
    cfg = AblationConfig()

    # D-1/D-2/D-3: Data and checkpoint verification
    print("[D-3] Checking existing checkpoints...")
    print(f"  h-m1 EquiSSL-perm seed0: {os.path.exists(paths.hm1_checkpoint_dir + '/equi_perm_seed0.pt')}")
    for s in cfg.seeds:
        p = get_equi_ckpt_path(s, paths)
        print(f"  EquiSSL seed{s}: {os.path.exists(p)} ({p})")

    # A-2: Train missing EquiSSL-perm seeds (1,2 if using seeds [0,1,2])
    # For seeds other than 0, train or copy from h-m1
    missing_perm = [s for s in cfg.seeds if s != 0 and
                    not os.path.exists(get_perm_ckpt_path(s, paths))]

    # Check if h-m1 has seeds 1,2 from its experiment run
    for s in missing_perm[:]:
        hm1_seed_path = os.path.join(paths.hm1_checkpoint_dir, f'equi_perm_seed{s}.pt')
        hm2_ckpt = get_perm_ckpt_path(s, paths)
        if os.path.exists(hm1_seed_path):
            import shutil
            shutil.copy2(hm1_seed_path, hm2_ckpt)
            print(f"[A-2] Copied h-m1 seed{s} checkpoint to h-m2/checkpoints/")
            missing_perm.remove(s)

    if missing_perm:
        print(f"[A-2] Training EquiSSL-perm for seeds: {missing_perm}")
        train_missing_perm_seeds(missing_perm, paths, device=device)

    # A-3/A-4/A-5: Extract embeddings, probe, stats
    results = run_hm2_ablation(cfg.seeds, paths, device=device)

    # A-6: MMD already computed inside run_hm2_ablation

    # A-7: Figures
    generate_figures(results, paths, cfg)

    # A-8: Save results
    out = save_results(results, paths, cfg)

    print(f"\n[H-M2] COMPLETE — Gate: {out['gate_result']}")
    print(f"  EquiSSL R²: {out['models']['equissl']['r2_mean']:.4f} ± {out['models']['equissl']['r2_std']:.4f}")
    print(f"  EquiSSL-perm R²: {out['models']['equissl_perm']['r2_mean']:.4f} ± {out['models']['equissl_perm']['r2_std']:.4f}")
    print(f"  ΔR² mean: {out['delta_r2']['mean']:.4f}")


if __name__ == '__main__':
    main()
