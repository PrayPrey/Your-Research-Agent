import sys
import os
import logging

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.linear_model import LogisticRegression
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# H-E2 config (loaded first so this module's config is active)
import config as cfg

# Inject H-E1 code into sys.path for reuse of model_utils, stats_utils, viz_utils
_H_E1_CODE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
sys.path.insert(0, _H_E1_CODE)

from model_utils import LOADERS
from stats_utils import run_anova, pairwise_tests, check_gate, export_results
import viz_utils

from data.celeba_loader import get_celeba_loaders, get_balanced_celeba_indices


def setup_logging():
    os.makedirs(cfg.LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, cfg.LOG_LEVEL),
        format=cfg.LOG_FORMAT,
        handlers=[
            logging.FileHandler(cfg.LOG_PATH),
            logging.StreamHandler(),
        ],
    )


def extract_features_celeba(model, loader, device, blond_attr, male_attr):
    feats, task_lbls, spur_lbls = [], [], []
    model.eval()
    with torch.no_grad():
        for imgs, attrs in loader:
            f = model(imgs.to(device))
            feats.append(f.cpu())
            task_lbls.append(attrs[:, blond_attr])
            spur_lbls.append(attrs[:, male_attr])
    features = torch.cat(feats)
    assert features.shape[1] == cfg.FEATURE_DIM, f"Feature dim: {features.shape}"
    return features, torch.cat(task_lbls).long(), torch.cat(spur_lbls).long()


def get_or_extract_features_celeba(model, loader, device, cache_key):
    os.makedirs(cfg.CACHE_DIR, exist_ok=True)
    path = os.path.join(cfg.CACHE_DIR, f"{cache_key}.pt")
    if os.path.exists(path):
        logging.info(f"Loading cached features: {path}")
        return torch.load(path)
    logging.info(f"Extracting features for {cache_key}...")
    result = extract_features_celeba(model, loader, device, cfg.BLOND_ATTR, cfg.MALE_ATTR)
    torch.save(result, path)
    logging.info(f"Cached: {path}")
    return result


def compute_ratio_celeba(feats_train, task_lbls_train, spur_lbls_train,
                         feats_test, task_lbls_test, spur_lbls_test,
                         seed, paradigm):
    np.random.seed(seed)
    torch.manual_seed(seed)
    X_tr = feats_train.numpy()
    X_te = feats_test.numpy()
    y_task_tr = task_lbls_train.numpy()
    y_spur_tr = spur_lbls_train.numpy()

    clf_task = LogisticRegression(
        C=cfg.PROBE_C, max_iter=cfg.PROBE_MAX_ITER, solver=cfg.PROBE_SOLVER
    ).fit(X_tr, y_task_tr)
    clf_spur = LogisticRegression(
        C=cfg.PROBE_C, max_iter=cfg.PROBE_MAX_ITER, solver=cfg.PROBE_SOLVER
    ).fit(X_tr, y_spur_tr)

    acc_task = clf_task.score(X_te, task_lbls_test.numpy())
    acc_spur = clf_spur.score(X_te, spur_lbls_test.numpy())

    assert acc_task > 0.5, f"Degenerate probe: task_acc={acc_task}"
    assert acc_spur > 0.5, f"Degenerate probe: spur_acc={acc_spur}"

    ratio = acc_spur / acc_task
    logging.info(
        f"CelebA: paradigm={paradigm}, seed={seed}, "
        f"task_acc={acc_task:.4f}, spur_acc={acc_spur:.4f}, ratio={ratio:.4f}"
    )
    return {
        'paradigm': paradigm,
        'seed': seed,
        'task_acc': acc_task,
        'spurious_acc': acc_spur,
        'ratio': ratio,
        'dataset': 'celeba',
    }


def plot_cross_dataset_bar(ratios_celeba, out_dir, h_e1_means=None):
    if h_e1_means is None:
        h_e1_means = {'erm': 1.052, 'moco': 1.027, 'dino': 1.050, 'barlowtwins': 1.033}
    paradigms = cfg.PARADIGMS
    celeba_means = [np.mean(ratios_celeba[p]) for p in paradigms]
    celeba_stds = [np.std(ratios_celeba[p], ddof=1) for p in paradigms]
    wb_means = [h_e1_means[p] for p in paradigms]

    x = np.arange(len(paradigms))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, wb_means, width, label='Waterbirds (H-E1)', color='steelblue', alpha=0.8)
    ax.bar(x + width / 2, celeba_means, width, yerr=celeba_stds,
           capsize=4, label='CelebA (H-E2)', color='darkorange', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([p.upper() for p in paradigms])
    ax.set_ylabel('Spurious / Task Probe Accuracy Ratio')
    ax.set_title('Cross-Dataset Spurious Ratio: Waterbirds vs CelebA')
    ax.legend()
    ax.set_ylim(0.9, 1.2)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'cross_dataset_bar.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    logging.info(f"Figure saved: {path}")


def main(device=None):
    setup_logging()
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"H-E2 experiment starting on device={device}")

    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)

    train_loader, test_ds = get_celeba_loaders(cfg.DATA_ROOT, cfg.BATCH_SIZE,
                                                download=cfg.DATASET_DOWNLOAD)
    logging.info(f"CelebA train={len(train_loader.dataset)}, test={len(test_ds)}")

    ratios = {p: [] for p in cfg.PARADIGMS}
    acc_records = []

    for paradigm in cfg.PARADIGMS:
        logging.info(f"=== Paradigm: {paradigm} ===")
        model = LOADERS[paradigm](device)

        feats_train, task_tr, spur_tr = get_or_extract_features_celeba(
            model, train_loader, device, f"{paradigm}_train"
        )
        # Extract full test features once (balanced subset selected per seed)
        test_full_loader = DataLoader(test_ds, batch_size=cfg.BATCH_SIZE,
                                      shuffle=False, num_workers=4, pin_memory=True)
        feats_test_full, _, _ = get_or_extract_features_celeba(
            model, test_full_loader, device, f"{paradigm}_test_full"
        )

        del model
        if device == 'cuda':
            torch.cuda.empty_cache()

        for seed in cfg.SEEDS:
            bal_idx = get_balanced_celeba_indices(
                test_ds, cfg.BLOND_ATTR, cfg.MALE_ATTR, cfg.N_PER_GROUP, seed
            )
            task_te = test_ds.attr[bal_idx, cfg.BLOND_ATTR].long()
            spur_te = test_ds.attr[bal_idx, cfg.MALE_ATTR].long()
            feats_te = feats_test_full[bal_idx]

            result = compute_ratio_celeba(
                feats_train, task_tr, spur_tr,
                feats_te, task_te, spur_te,
                seed, paradigm,
            )
            ratios[paradigm].append(result['ratio'])
            acc_records.append(result)

    # Save CSV
    csv_path = os.path.join(cfg.RESULTS_DIR, 'results.csv')
    pd.DataFrame(acc_records).to_csv(csv_path, index=False)
    logging.info(f"Results CSV saved: {csv_path}")

    # Stats
    anova_result = run_anova(ratios)
    pair_results = pairwise_tests(ratios)
    gate_ok, passing = check_gate(pair_results, cfg.GATE_ALPHA, cfg.GATE_MIN_DIFF)
    export_results(ratios, anova_result, pair_results, gate_ok, passing,
                   os.path.join(cfg.RESULTS_DIR, 'stats.json'))

    # Visualizations
    viz_utils.plot_ratio_bar(ratios, pair_results, cfg.FIGURES_DIR)
    viz_utils.plot_acc_heatmap(acc_records, cfg.FIGURES_DIR)
    viz_utils.plot_pvalue_matrix(pair_results, cfg.PARADIGMS, cfg.FIGURES_DIR)
    viz_utils.plot_ratio_violin(ratios, cfg.FIGURES_DIR)
    plot_cross_dataset_bar(ratios, cfg.FIGURES_DIR)

    logging.info(f"Gate satisfied: {gate_ok}, passing pairs: {[r['pair'] for r in passing]}")
    logging.info(f"Ratio means: { {p: round(float(np.mean(v)), 4) for p, v in ratios.items()} }")
    logging.info("H-E2 COMPLETE")
    return gate_ok, ratios, pair_results


if __name__ == '__main__':
    main()
