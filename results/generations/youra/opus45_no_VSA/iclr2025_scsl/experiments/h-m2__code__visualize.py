import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_sr_trajectory(results_by_variant: dict, out_path: str):
    plt.figure(figsize=(10, 6))
    for variant, results in results_by_variant.items():
        srs = [r["sr"] for r in results if r.get("sr") is not None]
        if srs:
            mean_sr = np.mean(srs)
            plt.bar(variant, mean_sr, yerr=np.std(srs), capsize=5, label=variant)
    plt.axhline(y=1.2, color='r', linestyle='--', label='Baseline threshold (1.2)')
    plt.axhline(y=1.1, color='g', linestyle='--', label='Parity target (1.1)')
    plt.ylabel('Sharpness Ratio (SR)')
    plt.title('SR Comparison Across Variants')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_group_accuracy_trajectories(results_by_variant: dict, out_path: str):
    plt.figure(figsize=(12, 6))
    for i, (variant, results) in enumerate(results_by_variant.items()):
        all_accs = {}
        for r in results:
            for g, acc in r.get("per_group_acc", {}).items():
                all_accs.setdefault(g, []).append(acc)
        x = np.arange(len(all_accs))
        width = 0.25
        for j, (g, accs) in enumerate(sorted(all_accs.items())):
            offset = (i - 1) * width
            plt.bar(j + offset, np.mean(accs), width, yerr=np.std(accs),
                    label=f'{variant} G{g}' if i == 0 else '', capsize=3)
    plt.xlabel('Group')
    plt.ylabel('Accuracy')
    plt.title('Per-Group Accuracy by Variant')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_update_norm_boxplot(results_by_variant: dict, out_path: str):
    plt.figure(figsize=(10, 6))
    data = []
    labels = []
    for variant, results in results_by_variant.items():
        norms = []
        for r in results:
            for log in r.get("update_norms", []):
                if log.get("orig_norm"):
                    norms.append(log["orig_norm"])
        if norms:
            data.append(norms[:100])
            labels.append(variant)
    if data:
        plt.boxplot(data, labels=labels)
    plt.ylabel('Update Norm')
    plt.title('Update Norm Distribution by Variant')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_wga_comparison(results_by_variant: dict, out_path: str):
    plt.figure(figsize=(8, 6))
    variants = []
    means = []
    stds = []
    for variant, results in results_by_variant.items():
        wgas = [r["wga"] for r in results]
        variants.append(variant)
        means.append(np.mean(wgas))
        stds.append(np.std(wgas))
    plt.bar(variants, means, yerr=stds, capsize=5)
    plt.ylabel('Worst-Group Accuracy')
    plt.title('WGA Comparison Across Variants')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
