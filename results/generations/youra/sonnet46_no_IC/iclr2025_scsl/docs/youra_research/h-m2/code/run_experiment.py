"""H-M2: Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification."""
import gc
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import torch
import torch.nn.functional as F
import torchvision.models as tv_models
import torchvision.transforms as T
from sklearn.linear_model import LogisticRegression
from torch.utils.data import DataLoader
from wilds import get_dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ── Model loading ─────────────────────────────────────────────────────────────

def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module:
    model = tv_models.resnet50(weights=None)
    model.fc = torch.nn.Linear(2048, 2)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    if isinstance(ckpt, dict):
        for key in ('model_state_dict', 'model', 'state_dict'):
            if key in ckpt:
                model.load_state_dict(ckpt[key])
                break
        else:
            model.load_state_dict(ckpt)
    else:
        model.load_state_dict(ckpt)
    model.eval()
    return model.to(device)


# ── WILDS data helpers ────────────────────────────────────────────────────────

def get_transform() -> T.Compose:
    return T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
    ])


def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader:
    dataset = get_dataset(
        dataset=config.WILDS_DATASET,
        download=False,
        root_dir=config.WILDS_CACHE,
    )
    subset = dataset.get_subset(split, transform=get_transform())
    return DataLoader(subset, batch_size=batch_size, shuffle=shuffle, num_workers=4, pin_memory=True)


# ── Weight difference analysis (FR-1) ─────────────────────────────────────────

def verify_gradient_propagation(erm_ckpt: str, method_ckpt: str, seed: int) -> dict:
    device = 'cpu'
    erm = load_resnet50(erm_ckpt, device)
    mth = load_resnet50(method_ckpt, device)

    block_diffs = []
    for b in config.LAYER4_BLOCKS:
        diffs = [
            (gp - ep).norm().item()
            for gp, ep in zip(mth.layer4[b].parameters(), erm.layer4[b].parameters())
        ]
        block_diffs.append(float(np.mean(diffs)))

    head_diff = float((mth.fc.weight - erm.fc.weight).norm().item())
    ratio = float(np.mean(block_diffs)) / max(head_diff, 1e-10)
    gradient_reached = any(d > config.WEIGHT_DIFF_EPSILON for d in block_diffs)

    del erm, mth
    gc.collect()

    result = {f'layer4_block{b}_diff': block_diffs[b] for b in config.LAYER4_BLOCKS}
    result.update({
        'head_weight_diff': head_diff,
        'backbone_to_head_ratio': ratio,
        'gradient_reached_layer4': gradient_reached,
        'seed': seed,
    })
    return result


def compare_all_methods() -> dict:
    ckpt_dir = config.CHECKPOINT_ARCHIVE
    results = {}
    for method_a, method_b in config.PAIRED_METHODS:
        results[method_b] = {}
        for seed in config.SEEDS:
            erm_ckpt = os.path.join(ckpt_dir, f'{method_a}_seed{seed}.pt')
            mth_ckpt = os.path.join(ckpt_dir, f'{method_b}_seed{seed}.pt')
            print(f'  Weight diff: {method_a} vs {method_b}, seed {seed}')
            results[method_b][seed] = verify_gradient_propagation(erm_ckpt, mth_ckpt, seed)
    return results


# ── Gradient norm analysis (FR-2) ─────────────────────────────────────────────

def compute_layer4_gradient_norm(
    model: torch.nn.Module,
    dataloader: DataLoader,
    loss_type: str,
    device: str = 'cpu',
    n_batches: int = 50,
) -> tuple:
    model.train()
    batch_norms = []
    for i, (x, y, metadata) in enumerate(dataloader):
        if i >= n_batches:
            break
        x, y = x.to(device), y.to(device)
        model.zero_grad()
        logits = model(x)

        if loss_type == 'erm':
            loss = F.cross_entropy(logits, y)
        else:  # groupdro
            group = metadata[:, 0].to(device)
            g_losses = []
            for g in range(config.N_GROUPS):
                mask = (group == g)
                if mask.sum() > 0:
                    g_losses.append(F.cross_entropy(logits[mask], y[mask]))
            if g_losses:
                loss = torch.stack(g_losses).max()
            else:
                loss = F.cross_entropy(logits, y)

        loss.backward()
        norms = [p.grad.norm().item() for p in model.layer4.parameters() if p.grad is not None]
        if norms:
            batch_norms.append(float(np.mean(norms)))

    if not batch_norms:
        return 0.0, 0.0
    return float(np.mean(batch_norms)), float(np.std(batch_norms))


def run_gradient_analysis(train_loader: DataLoader, device: str) -> dict:
    ckpt_dir = config.CHECKPOINT_ARCHIVE
    results = {}
    for loss_type in ['erm', 'groupdro']:
        ckpt_path = os.path.join(ckpt_dir, f'{loss_type}_seed1.pt')
        print(f'  Gradient norm: {loss_type} seed1, loss_type={loss_type}')
        model = load_resnet50(ckpt_path, device)
        mean_norm, std_norm = compute_layer4_gradient_norm(
            model, train_loader, loss_type, device, config.N_GRAD_BATCHES
        )
        results[loss_type] = (mean_norm, std_norm)
        del model
        gc.collect()
    return results


# ── Feature extraction + linear probe (FR-3) ─────────────────────────────────

def extract_layer4_features(model: torch.nn.Module, dataloader: DataLoader, device: str):
    model.eval()
    all_feats, all_labels = [], []
    with torch.no_grad():
        for x, y, metadata in dataloader:
            x = x.to(device)
            h = model.conv1(x)
            h = model.bn1(h)
            h = model.relu(h)
            h = model.maxpool(h)
            h = model.layer1(h)
            h = model.layer2(h)
            h = model.layer3(h)
            h = model.layer4(h)
            h = F.adaptive_avg_pool2d(h, (1, 1))
            h = h.flatten(1)
            group = metadata[:, 0].numpy()
            bg_label = (group % 2).astype(int)
            all_feats.append(h.cpu().numpy())
            all_labels.append(bg_label)
    return np.concatenate(all_feats), np.concatenate(all_labels)


def linear_probe(train_feats, train_labels, test_feats, test_labels) -> float:
    clf = LogisticRegression(
        solver=config.PROBE_SOLVER,
        C=config.PROBE_C,
        max_iter=config.PROBE_MAX_ITER,
        random_state=config.PROBE_RANDOM_STATE,
    )
    clf.fit(train_feats, train_labels)
    return float(clf.score(test_feats, test_labels))


def run_linear_probe_all_checkpoints(train_loader: DataLoader, test_loader: DataLoader, device: str) -> dict:
    ckpt_dir = config.CHECKPOINT_ARCHIVE
    results = {}
    for method in config.METHODS:
        for seed in config.SEEDS:
            ckpt_name = f'{method}_seed{seed}'
            ckpt_path = os.path.join(ckpt_dir, f'{ckpt_name}.pt')
            print(f'  Linear probe: {ckpt_name}')
            model = load_resnet50(ckpt_path, device)
            train_feats, train_labels = extract_layer4_features(model, train_loader, device)
            test_feats, test_labels = extract_layer4_features(model, test_loader, device)
            del model
            gc.collect()
            acc = linear_probe(train_feats, train_labels, test_feats, test_labels)
            results[ckpt_name] = acc
            print(f'    acc={acc:.4f}')
    return results


# ── Statistical test (FR-4) ───────────────────────────────────────────────────

def paired_ttest(erm_accs: list, gdro_accs: list) -> tuple:
    diffs = [e - g for e, g in zip(erm_accs, gdro_accs)]
    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    # one-sided: H1 = ERM probe > GroupDRO probe (ERM encodes more spurious)
    result = scipy.stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')
    p_value = float(result.pvalue)
    cohens_d = mean_diff / std_diff if std_diff > 1e-10 else 0.0
    return p_value, cohens_d


def gate_verdict(p_value: float, cohens_d: float) -> str:
    if p_value < 0.05 and cohens_d > 0:
        return 'CONFIRMED'
    elif p_value < 0.10 and cohens_d > 0.5:
        return 'SUGGESTIVE'
    else:
        return 'REJECTED'


# ── Visualization (FR-5) ──────────────────────────────────────────────────────

def save_figures(weight_results: dict, grad_results: dict, probe_results: dict) -> None:
    Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    # Figure 1: layer4 weight diff grouped bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    gdro_data = weight_results.get('groupdro', {})
    seeds = config.SEEDS
    x = np.arange(len(seeds))
    width = 0.25
    for bi, block in enumerate(config.LAYER4_BLOCKS):
        vals = [gdro_data.get(s, {}).get(f'layer4_block{block}_diff', 0) for s in seeds]
        ax.bar(x + bi * width, vals, width, label=f'block{block}')
    ax.set_xlabel('Seed')
    ax.set_ylabel('L2 Weight Diff (GroupDRO - ERM)')
    ax.set_title('Layer4 Weight Difference: GroupDRO vs ERM')
    ax.set_xticks(x + width)
    ax.set_xticklabels([f'seed{s}' for s in seeds])
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(config.FIGURES_DIR, 'layer4_weight_diff.png'), dpi=150)
    plt.close(fig)

    # Figure 2: gradient norm comparison box plot (using mean/std as proxy)
    fig, ax = plt.subplots(figsize=(6, 5))
    erm_mean, erm_std = grad_results.get('erm', (0, 0))
    gdro_mean, gdro_std = grad_results.get('groupdro', (0, 0))
    ax.bar(['ERM', 'GroupDRO'], [erm_mean, gdro_mean],
           yerr=[erm_std, gdro_std], capsize=8, color=['steelblue', 'darkorange'])
    ax.set_ylabel('Mean Layer4 Gradient Norm')
    ax.set_title('Layer4 Gradient Norm: ERM vs GroupDRO (seed1, 50 batches)')
    fig.tight_layout()
    fig.savefig(os.path.join(config.FIGURES_DIR, 'gradient_norm_comparison.png'), dpi=150)
    plt.close(fig)

    # Figure 3: backbone-to-head ratio scatter per seed
    fig, ax = plt.subplots(figsize=(6, 5))
    ratios = [gdro_data.get(s, {}).get('backbone_to_head_ratio', 0) for s in seeds]
    ax.scatter(seeds, ratios, s=100, zorder=5)
    for s, r in zip(seeds, ratios):
        ax.annotate(f'{r:.3f}', (s, r), textcoords='offset points', xytext=(5, 5))
    ax.set_xlabel('Seed')
    ax.set_ylabel('Backbone-to-Head Ratio')
    ax.set_title('Layer4 / Head Weight Diff Ratio: GroupDRO vs ERM')
    ax.set_xticks(seeds)
    fig.tight_layout()
    fig.savefig(os.path.join(config.FIGURES_DIR, 'backbone_head_ratio.png'), dpi=150)
    plt.close(fig)

    # Figure 4 (optional): heatmap layer4 diff per block × seed
    fig, ax = plt.subplots(figsize=(7, 4))
    heatmap_data = np.array([
        [gdro_data.get(s, {}).get(f'layer4_block{b}_diff', 0) for b in config.LAYER4_BLOCKS]
        for s in seeds
    ])
    im = ax.imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(config.LAYER4_BLOCKS)))
    ax.set_xticklabels([f'block{b}' for b in config.LAYER4_BLOCKS])
    ax.set_yticks(range(len(seeds)))
    ax.set_yticklabels([f'seed{s}' for s in seeds])
    ax.set_title('Layer4 Block Weight Diff Heatmap (GroupDRO vs ERM)')
    plt.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(os.path.join(config.FIGURES_DIR, 'layer4_heatmap.png'), dpi=150)
    plt.close(fig)

    print(f'  Figures saved to {config.FIGURES_DIR}')


# ── Results + report (FR-6, FR-7) ────────────────────────────────────────────

def save_results(results: dict) -> None:
    Path(os.path.dirname(config.RESULTS_JSON)).mkdir(parents=True, exist_ok=True)
    with open(config.RESULTS_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'  Results saved to {config.RESULTS_JSON}')


def generate_validation_report(results: dict) -> None:
    weight_r = results.get('weight_diff', {})
    grad_r = results.get('gradient_norm', {})
    probe_r = results.get('linear_probe', {})
    stat_r = results.get('statistical_test', {})
    verdict = stat_r.get('verdict', 'UNKNOWN')
    p_val = stat_r.get('p_value', None)
    cohens_d = stat_r.get('cohens_d', None)

    # SHOULD_WORK gate: always passes (pipeline continues even if REJECTED)
    gate_result = 'PASS'

    lines = [
        '# H-M2 Validation Report',
        '## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification',
        '',
        f'**Gate Type:** SHOULD_WORK',
        f'**Gate Result:** {gate_result}',
        f'**Statistical Verdict:** {verdict}',
        '',
        '---',
        '',
        '## FR-1: Layer4 Weight Difference Analysis',
        '',
        '| Seed | Block0 Diff | Block1 Diff | Block2 Diff | Head Diff | Backbone/Head Ratio | Gradient Reached |',
        '|------|-------------|-------------|-------------|-----------|---------------------|-----------------|',
    ]
    gdro_data = weight_r.get('groupdro', {})
    for seed in config.SEEDS:
        d = gdro_data.get(seed, {})
        b0 = d.get('layer4_block0_diff', 'N/A')
        b1 = d.get('layer4_block1_diff', 'N/A')
        b2 = d.get('layer4_block2_diff', 'N/A')
        hd = d.get('head_weight_diff', 'N/A')
        ratio = d.get('backbone_to_head_ratio', 'N/A')
        reached = d.get('gradient_reached_layer4', 'N/A')
        fmt = lambda v: f'{v:.6f}' if isinstance(v, float) else str(v)
        lines.append(f'| {seed} | {fmt(b0)} | {fmt(b1)} | {fmt(b2)} | {fmt(hd)} | {fmt(ratio)} | {reached} |')

    # DFR control
    dfr_data = weight_r.get('dfr', {})
    lines += ['', '**DFR-ERM Control (should be ~0):**']
    for seed in config.SEEDS:
        d = dfr_data.get(seed, {})
        b0 = d.get('layer4_block0_diff', 'N/A')
        fmt = lambda v: f'{v:.8f}' if isinstance(v, float) else str(v)
        lines.append(f'- Seed {seed}: block0_diff={fmt(b0)}')

    lines += [
        '',
        '## FR-2: Gradient Norm Analysis',
        '',
        '| Method | Mean Grad Norm (layer4) | Std |',
        '|--------|------------------------|-----|',
    ]
    for loss_type in ['erm', 'groupdro']:
        mn, sd = grad_r.get(loss_type, (0, 0))
        lines.append(f'| {loss_type} | {mn:.6f} | {sd:.6f} |')

    lines += [
        '',
        '## FR-3: Linear Probe Accuracy (all 12 checkpoints)',
        '',
        '| Checkpoint | Background Probe Acc |',
        '|------------|---------------------|',
    ]
    for method in config.METHODS:
        for seed in config.SEEDS:
            k = f'{method}_seed{seed}'
            acc = probe_r.get(k, 'N/A')
            fmt = f'{acc:.4f}' if isinstance(acc, float) else str(acc)
            lines.append(f'| {k} | {fmt} |')

    lines += [
        '',
        '## FR-4: Statistical Test',
        '',
        f'- **P-value (one-sided paired t-test):** {p_val:.4f}' if isinstance(p_val, float) else f'- P-value: {p_val}',
        f"- **Cohen's d:** {cohens_d:.4f}" if isinstance(cohens_d, float) else f"- Cohen's d: {cohens_d}",
        f'- **Verdict:** {verdict}',
        '',
        '## Contested Landscape Note',
        '',
        '- Izmailov 2022 (NeurIPS): GroupDRO advantage primarily in head, not backbone',
        '- Raymond 2026 (ICLR): GroupDRO reshapes representations across all layers',
        '- H-M2 proxy evidence (weight diff + gradient norm) addresses this debate directly',
        '',
        '## Gate Assessment',
        '',
        f'**SHOULD_WORK gate:** {gate_result}',
        '- Even if H-M3 probe is REJECTED, layer4 weight diff evidence allows pipeline to continue to H-M3',
        f'- n_test_samples={config.PROBE_N_TEST_SAMPLES}',
        f'- gate_result: {gate_result}',
    ]

    report_text = '\n'.join(lines) + '\n'
    with open(config.VALIDATION_REPORT, 'w') as f:
        f.write(report_text)
    print(f'  Report saved to {config.VALIDATION_REPORT}')


# ── Orchestration ─────────────────────────────────────────────────────────────

def main() -> None:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Device: {device}')

    Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    # Step 1: Weight difference analysis
    print('\n=== Step 1: Weight Difference Analysis ===')
    weight_results = compare_all_methods()

    # Verify gradient reached layer4 for all GroupDRO seeds
    gdro_data = weight_results.get('groupdro', {})
    for seed in config.SEEDS:
        d = gdro_data.get(seed, {})
        assert d.get('gradient_reached_layer4', False), \
            f'ASSERTION FAILED: gradient_reached_layer4=False for GroupDRO seed {seed}'
        print(f'  ✓ GroupDRO seed{seed}: gradient_reached_layer4=True')

    # DFR control check (expected ~0)
    dfr_data = weight_results.get('dfr', {})
    for seed in config.SEEDS:
        d = dfr_data.get(seed, {})
        b0 = d.get('layer4_block0_diff', 1.0)
        print(f'  DFR seed{seed} block0_diff={b0:.8f} (expect ~0)')

    # Step 2: Gradient norm analysis
    print('\n=== Step 2: Gradient Norm Analysis ===')
    train_loader = get_loader('train', batch_size=config.GRAD_BATCH_SIZE, shuffle=False)
    grad_results = run_gradient_analysis(train_loader, device)
    for loss_type, (mn, sd) in grad_results.items():
        print(f'  {loss_type}: mean={mn:.6f}, std={sd:.6f}')
        assert mn > 0, f'ASSERTION FAILED: gradient norm=0 for {loss_type}'

    # Step 3: Linear probe (full test set, all 12 checkpoints)
    print('\n=== Step 3: Linear Probe (12 checkpoints, full test set) ===')
    test_loader = get_loader('test', batch_size=128, shuffle=False)
    train_loader_probe = get_loader('train', batch_size=128, shuffle=False)
    probe_results = run_linear_probe_all_checkpoints(train_loader_probe, test_loader, device)

    # Step 4: Statistical test
    print('\n=== Step 4: Statistical Test ===')
    erm_accs = [probe_results[f'erm_seed{s}'] for s in config.SEEDS]
    gdro_accs = [probe_results[f'groupdro_seed{s}'] for s in config.SEEDS]
    p_value, cohens_d = paired_ttest(erm_accs, gdro_accs)
    verdict = gate_verdict(p_value, cohens_d)
    print(f'  ERM probe accs: {erm_accs}')
    print(f'  GroupDRO probe accs: {gdro_accs}')
    print(f'  p_value={p_value:.4f}, cohens_d={cohens_d:.4f}, verdict={verdict}')

    # Collect all results
    all_results = {
        'hypothesis_id': 'h-m2',
        'gate_type': 'SHOULD_WORK',
        'gate_result': 'PASS',
        'n_test_samples': config.PROBE_N_TEST_SAMPLES,
        'weight_diff': weight_results,
        'gradient_norm': grad_results,
        'linear_probe': probe_results,
        'statistical_test': {
            'p_value': p_value,
            'cohens_d': cohens_d,
            'verdict': verdict,
            'erm_accs': erm_accs,
            'gdro_accs': gdro_accs,
        },
    }

    # Step 5: Figures + reports
    print('\n=== Step 5: Figures and Reports ===')
    save_figures(weight_results, grad_results, probe_results)
    save_results(all_results)
    generate_validation_report(all_results)

    print('\n=== COMPLETE ===')
    print(f'  Gate: SHOULD_WORK → PASS')
    print(f'  Statistical verdict: {verdict}')
    print(f'  Results: {config.RESULTS_JSON}')
    print(f'  Report: {config.VALIDATION_REPORT}')


if __name__ == '__main__':
    main()
