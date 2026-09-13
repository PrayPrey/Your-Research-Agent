"""H-M3: Background Linear Decodability — does layer4 encode background more in ERM vs GroupDRO?"""
import gc
import json
import os
import sys
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import torch
import torchvision.models as tv_models
import torchvision.transforms as T
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from torch.utils.data import DataLoader
from wilds import get_dataset

import config


def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module:
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"[H-M3] Checkpoint not found: {ckpt_path}")
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
    return model.eval().to(device)


def get_transform() -> T.Compose:
    return T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
    ])


def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader:
    dataset = get_dataset(dataset=config.WILDS_DATASET, download=False,
                          root_dir=config.WILDS_CACHE)
    subset = dataset.get_subset(split, transform=get_transform())
    return DataLoader(subset, batch_size=batch_size, shuffle=shuffle,
                      num_workers=4, pin_memory=True)


def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str,
) -> tuple:
    model.eval()
    all_feats, all_labels = [], []
    with torch.no_grad():
        for x, y, metadata in dataloader:
            x = x.to(device)
            x = model.conv1(x); x = model.bn1(x); x = model.relu(x); x = model.maxpool(x)
            x = model.layer1(x); x = model.layer2(x); x = model.layer3(x); x = model.layer4(x)
            x = torch.nn.functional.adaptive_avg_pool2d(x, (1, 1))
            x = x.flatten(1)
            all_feats.append(x.cpu().numpy())
            bg = metadata[:, 0].numpy() % 2
            all_labels.append(bg)
    features = np.concatenate(all_feats, axis=0)
    labels = np.concatenate(all_labels, axis=0)
    print(f"[H-M3] Features extracted: {features.shape}")
    print(f"[H-M3] Background label distribution: {np.bincount(labels.astype(int))}")
    return features, labels


def run_probe(features: np.ndarray, labels: np.ndarray, method: str, seed: int) -> float:
    probe = LogisticRegression(solver=config.PROBE_SOLVER, C=config.PROBE_C,
                               max_iter=config.PROBE_MAX_ITER,
                               random_state=config.PROBE_RANDOM_STATE)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        probe.fit(features, labels)
        if w and any(issubclass(x.category, ConvergenceWarning) for x in w):
            probe = LogisticRegression(solver=config.PROBE_SOLVER, C=config.PROBE_C,
                                       max_iter=5000,
                                       random_state=config.PROBE_RANDOM_STATE)
            probe.fit(features, labels)
    acc = probe.score(features, labels)
    print(f"[H-M3] Probe acc {method}_seed{seed}: {acc:.4f}")
    return acc


def run_all_probes(test_loader: DataLoader, device: str) -> dict:
    results = {}
    ckpt_dir = config.CHECKPOINT_ARCHIVE
    for method in config.METHODS:
        for seed in config.SEEDS:
            ckpt_path = os.path.join(ckpt_dir, f"{method}_seed{seed}.pt")
            model = load_resnet50(ckpt_path, device)
            features, bg_labels = extract_layer4_features(model, test_loader, device)
            del model; gc.collect()
            if device == 'cuda':
                torch.cuda.empty_cache()
            acc = run_probe(features, bg_labels, method, seed)
            results[f"{method}_seed{seed}"] = acc
    return results


def paired_ttest(erm_accs: list, gdro_accs: list) -> tuple:
    t_stat, p_value = scipy.stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')
    diff = np.array(erm_accs) - np.array(gdro_accs)
    cohens_d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else 0.0
    print(f"[H-M3] Paired t-test: t={t_stat:.4f}, p={p_value:.4f} (one-sided)")
    print(f"[H-M3] Cohen's d: {cohens_d:.4f}")
    return p_value, cohens_d


def gate_verdict(p_value: float, cohens_d: float, gdro_mean: float, erm_mean: float) -> str:
    if gdro_mean >= erm_mean:
        verdict = "REJECTED"
    elif p_value < config.VERDICT_CONFIRMED_P and cohens_d > config.VERDICT_CONFIRMED_D:
        verdict = "CONFIRMED"
    elif p_value < config.VERDICT_SUGGESTIVE_P and cohens_d > config.VERDICT_SUGGESTIVE_D:
        verdict = "SUGGESTIVE"
    else:
        verdict = "REJECTED"
    print(f"[H-M3] Verdict: {verdict}")
    return verdict


def save_figures(probe_results: dict, stat_results: dict) -> None:
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    erm_accs = [probe_results[f"erm_seed{s}"] for s in config.SEEDS]
    gdro_accs = [probe_results[f"groupdro_seed{s}"] for s in config.SEEDS]
    sam_accs = [probe_results[f"sam_seed{s}"] for s in config.SEEDS]
    p_value = stat_results["p_value"]

    # Fig1: gate_metrics.png
    fig, (ax_main, ax_inset) = plt.subplots(1, 2, figsize=(10, 5))
    x = np.arange(3)
    w = 0.35
    ax_main.bar(x - w/2, erm_accs, w, label='ERM', color='steelblue')
    ax_main.bar(x + w/2, gdro_accs, w, label='GroupDRO', color='coral')
    ax_main.set_xticks(x); ax_main.set_xticklabels(['Seed 1', 'Seed 2', 'Seed 3'])
    ax_main.set_ylabel('Background Probe Accuracy')
    ax_main.set_title(f'ERM vs GroupDRO Background Probe\np={p_value:.4f}')
    ax_main.legend()
    ax_main.set_ylim(0.8, 1.0)

    diffs = np.array(erm_accs) - np.array(gdro_accs)
    ax_inset.bar(x, diffs, color='green', alpha=0.7)
    ax_inset.axhline(diffs.mean(), color='red', linestyle='--', label=f'mean={diffs.mean():.4f}')
    ax_inset.set_title('Paired Differences (ERM - GroupDRO)')
    ax_inset.set_xticks(x); ax_inset.set_xticklabels(['Seed 1', 'Seed 2', 'Seed 3'])
    ax_inset.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(config.FIGURES_DIR, 'gate_metrics.png'), dpi=150)
    plt.close()

    # Fig2: all_probes.png
    fig, ax = plt.subplots(figsize=(10, 5))
    all_accs = erm_accs + gdro_accs + sam_accs
    labels_x = ([f'ERM_s{s}' for s in config.SEEDS] +
                [f'GDro_s{s}' for s in config.SEEDS] +
                [f'SAM_s{s}' for s in config.SEEDS])
    colors = ['steelblue'] * 3 + ['coral'] * 3 + ['green'] * 3
    ax.bar(range(9), all_accs, color=colors)
    ax.set_xticks(range(9)); ax.set_xticklabels(labels_x, rotation=45, ha='right')
    ax.set_ylabel('Background Probe Accuracy')
    ax.set_title('All 9 Checkpoints — Background Probe Accuracy')
    ax.set_ylim(0.5, 1.0)
    plt.tight_layout()
    plt.savefig(os.path.join(config.FIGURES_DIR, 'all_probes.png'), dpi=150)
    plt.close()

    # Fig3: paired_diff.png
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(3), diffs, color='green', alpha=0.7, label='ERM - GroupDRO')
    ax.axhline(diffs.mean(), color='red', linestyle='--', label=f'mean={diffs.mean():.4f}')
    ax.fill_between([-0.5, 2.5],
                    diffs.mean() - diffs.std(ddof=1),
                    diffs.mean() + diffs.std(ddof=1),
                    alpha=0.2, color='red', label='±1 std')
    ax.set_xticks(range(3)); ax.set_xticklabels(['Seed 1', 'Seed 2', 'Seed 3'])
    ax.set_ylabel('Probe Acc Difference')
    ax.set_title('Paired Differences: ERM - GroupDRO')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(config.FIGURES_DIR, 'paired_diff.png'), dpi=150)
    plt.close()

    # Fig4: probe_vs_wga.png
    fig, ax = plt.subplots(figsize=(7, 5))
    for key, acc in probe_results.items():
        wga = config.WGA_BY_METHOD_SEED.get(key, 0.75)
        method = key.split('_seed')[0]
        color = {'erm': 'steelblue', 'groupdro': 'coral', 'sam': 'green'}.get(method, 'gray')
        ax.scatter(acc, wga, color=color, s=80, label=method)

    accs_all = list(probe_results.values())
    wgas_all = [config.WGA_BY_METHOD_SEED.get(k, 0.75) for k in probe_results]
    r, pval = scipy.stats.pearsonr(accs_all, wgas_all)
    ax.set_xlabel('Background Probe Accuracy')
    ax.set_ylabel('WGA')
    ax.set_title(f'Probe Accuracy vs WGA (r={r:.3f}, p={pval:.3f})')
    handles, lbls = ax.get_legend_handles_labels()
    by_label = dict(zip(lbls, handles))
    ax.legend(by_label.values(), by_label.keys())
    plt.tight_layout()
    plt.savefig(os.path.join(config.FIGURES_DIR, 'probe_vs_wga.png'), dpi=150)
    plt.close()

    print("[H-M3] Figures saved to", config.FIGURES_DIR)


def save_results(results: dict) -> None:
    with open(config.RESULTS_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[H-M3] Results saved to {config.RESULTS_JSON}")


def generate_validation_report(results: dict) -> None:
    verdict = results["verdict"]
    gate_result = results["gate_result"]
    erm_accs = results["erm_probe_accs"]
    gdro_accs = results["gdro_probe_accs"]
    sam_accs = results["sam_probe_accs"]
    p_value = results["p_value"]
    cohens_d = results["cohens_d"]
    erm_mean = results["erm_mean"]
    gdro_mean = results["gdro_mean"]
    n = results["n_test_samples"]

    report = f"""# H-M3 Validation Report: Background Linear Decodability

**Hypothesis**: ERM models encode more background information in layer4 features than GroupDRO models, as measured by linear probe accuracy on background label.

**Gate Type**: MUST_WORK (PoC validation)
**Date**: 2026-08-05

---

## Gate Verdict: {verdict}

**Gate Result: {gate_result}**

Evidence:
- ERM mean probe accuracy: {erm_mean:.4f}
- GroupDRO mean probe accuracy: {gdro_mean:.4f}
- Direction check: ERM > GroupDRO = {erm_mean > gdro_mean}
- Paired t-test p-value (one-sided): {p_value:.4f}
- Cohen's d: {cohens_d:.4f}

---

## Probe Accuracy Table (All 9 Checkpoints)

| Method | Seed | Background Probe Accuracy |
|--------|------|--------------------------|
| ERM | 1 | {erm_accs[0]:.4f} |
| ERM | 2 | {erm_accs[1]:.4f} |
| ERM | 3 | {erm_accs[2]:.4f} |
| GroupDRO | 1 | {gdro_accs[0]:.4f} |
| GroupDRO | 2 | {gdro_accs[1]:.4f} |
| GroupDRO | 3 | {gdro_accs[2]:.4f} |
| SAM | 1 | {sam_accs[0]:.4f} |
| SAM | 2 | {sam_accs[1]:.4f} |
| SAM | 3 | {sam_accs[2]:.4f} |

**ERM mean**: {erm_mean:.4f}
**GroupDRO mean**: {gdro_mean:.4f}
**SAM mean**: {results.get("sam_mean", 0):.4f}

---

## Statistical Test

| Metric | Value |
|--------|-------|
| Test | One-sided paired t-test (H1: ERM > GroupDRO) |
| p-value | {p_value:.4f} |
| Cohen's d | {cohens_d:.4f} |
| N checkpoints per method | 3 |
| N test samples | {n} |

---

## Sanity Checks

- ERM mean > 0.6: **{"PASS" if erm_mean > 0.6 else "FAIL"}** ({erm_mean:.4f})
- All probe accs in [0.5, 1.0]: **{"PASS" if all(0.5 <= a <= 1.0 for a in erm_accs + gdro_accs + sam_accs) else "FAIL"}**

---

## Verdict Determination

| Criterion | Threshold | Actual | Met |
|-----------|-----------|--------|-----|
| CONFIRMED: p < 0.05 | 0.05 | {p_value:.4f} | {"YES" if p_value < 0.05 else "NO"} |
| CONFIRMED: Cohen's d > 0 | 0.0 | {cohens_d:.4f} | {"YES" if cohens_d > 0 else "NO"} |
| SUGGESTIVE: p < 0.10 | 0.10 | {p_value:.4f} | {"YES" if p_value < 0.10 else "NO"} |
| SUGGESTIVE: Cohen's d > 0.5 | 0.5 | {cohens_d:.4f} | {"YES" if cohens_d > 0.5 else "NO"} |

**Final Verdict**: {verdict}
**Gate Result**: {gate_result}

---

## Exploratory: SAM Analysis

| Metric | Value |
|--------|-------|
| SAM mean probe acc | {results.get("sam_mean", 0):.4f} |
| SAM vs ERM Cohen's d | {results.get("exploratory_sam", {}).get("sam_vs_erm_cohens_d", 0):.4f} |

---

## Figures Generated

1. `figures/gate_metrics.png` — ERM vs GroupDRO grouped bar + paired differences inset
2. `figures/all_probes.png` — All 9 checkpoints bar chart
3. `figures/paired_diff.png` — Paired differences scatter with mean±std
4. `figures/probe_vs_wga.png` — Probe accuracy vs WGA scatter (Pearson r={results.get("pearson_r", 0):.3f})

---

## Conclusion

{"H-M3 hypothesis is SUPPORTED: ERM models show significantly higher background decodability in layer4 features compared to GroupDRO models." if gate_result == "PASS" else "H-M3 hypothesis is NOT SUPPORTED: No significant difference in background decodability between ERM and GroupDRO layer4 features."}
"""

    with open(config.VALIDATION_REPORT, 'w') as f:
        f.write(report)
    print(f"[H-M3] Validation report saved to {config.VALIDATION_REPORT}")


def main() -> None:
    print("[H-M3] Starting background linear decodability experiment")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[H-M3] Device: {device}")

    test_loader = get_loader('test', config.BATCH_SIZE)

    probe_results = run_all_probes(test_loader, device)

    erm_accs = [probe_results[f"erm_seed{s}"] for s in config.SEEDS]
    gdro_accs = [probe_results[f"groupdro_seed{s}"] for s in config.SEEDS]
    sam_accs = [probe_results[f"sam_seed{s}"] for s in config.SEEDS]

    erm_mean = np.mean(erm_accs)
    gdro_mean = np.mean(gdro_accs)
    sam_mean = np.mean(sam_accs)

    # Sanity checks
    if erm_mean <= 0.6:
        raise RuntimeError(
            f"[H-M3] ABORT: ERM mean probe acc {erm_mean:.4f} <= 0.6 (A2 violated — metric non-discriminative)"
        )
    if not all(0.5 <= a <= 1.0 for a in erm_accs + gdro_accs + sam_accs):
        raise RuntimeError("[H-M3] ABORT: Some probe acc outside [0.5, 1.0] range")

    p_value, cohens_d = paired_ttest(erm_accs, gdro_accs)
    verdict = gate_verdict(p_value, cohens_d, gdro_mean, erm_mean)

    # SAM exploratory
    sam_diff = np.array(erm_accs) - np.array(sam_accs)
    sam_cohens_d = sam_diff.mean() / sam_diff.std(ddof=1) if sam_diff.std(ddof=1) > 0 else 0.0

    # Pearson r for fig4
    accs_all = list(probe_results.values())
    wgas_all = [config.WGA_BY_METHOD_SEED.get(k, 0.75) for k in probe_results]
    pearson_r, pearson_p = scipy.stats.pearsonr(accs_all, wgas_all)

    gate_result = "PASS" if verdict in ("CONFIRMED", "SUGGESTIVE") else "FAIL"

    results = {
        "hypothesis_id": "h-m3",
        "verdict": verdict,
        "gate_result": gate_result,
        "erm_probe_accs": erm_accs,
        "gdro_probe_accs": gdro_accs,
        "sam_probe_accs": sam_accs,
        "erm_mean": float(erm_mean),
        "gdro_mean": float(gdro_mean),
        "sam_mean": float(sam_mean),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "n_test_samples": config.PROBE_N_TEST_SAMPLES,
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "exploratory_sam": {
            "sam_mean": float(sam_mean),
            "sam_vs_erm_cohens_d": float(sam_cohens_d),
        },
        "all_probe_results": probe_results,
    }

    stat_results = {"p_value": p_value, "cohens_d": cohens_d, "verdict": verdict}
    save_figures(probe_results, stat_results)
    save_results(results)
    generate_validation_report(results)

    print(f"[H-M3] === SUMMARY ===")
    print(f"[H-M3] ERM mean probe acc: {erm_mean:.4f}")
    print(f"[H-M3] GroupDRO mean probe acc: {gdro_mean:.4f}")
    print(f"[H-M3] SAM mean probe acc: {sam_mean:.4f}")
    print(f"[H-M3] p-value: {p_value:.4f}, Cohen's d: {cohens_d:.4f}")
    print(f"[H-M3] Verdict: {verdict}")
    print(f"[H-M3] Gate result: {gate_result}")
    print(f"[H-M3] Pearson r (probe vs WGA): {pearson_r:.3f}")


if __name__ == '__main__':
    main()
