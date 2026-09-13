"""Learning curve plots and efficiency ratio bar charts."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as cfg

ENCODER_COLORS = {
    "flat_mlp": "gray",
    "flat_mlp_perm_aug": "orange",
    "gnn_nfn": "steelblue",
    "dwsnets": "green",
}
ENCODER_LABELS = {
    "flat_mlp": "FlatMLP",
    "flat_mlp_perm_aug": "FlatMLP+PermAug",
    "gnn_nfn": "GNN-NFN",
    "dwsnets": "DWSNets",
}


def _size_to_num(s):
    return 3402 if s == "full" else int(s)


def plot_learning_curves(results, zoo_name, out_path):
    """Line plot: R² vs training size for all encoders with 95% CI bands."""
    sizes_ordered = cfg.TRAINING_SIZES
    x_numeric = [_size_to_num(s) for s in sizes_ordered]
    x_labels = ["100", "250", "500", "1K", "Full"]

    fig, ax = plt.subplots(figsize=(8, 5))

    for enc in cfg.ENCODER_NAMES + ["dwsnets"]:
        if enc not in results or zoo_name not in results[enc]:
            continue
        zoo_data = results[enc][zoo_name]
        xs, ys, lo_errs, hi_errs = [], [], [], []
        for s, xn in zip(sizes_ordered, x_numeric):
            k = str(s)
            if k not in zoo_data:
                continue
            cell = zoo_data[k]
            xs.append(xn)
            ys.append(cell["mean_r2"])
            lo_errs.append(cell.get("ci_lo", cell["mean_r2"]))
            hi_errs.append(cell.get("ci_hi", cell["mean_r2"]))

        if not xs:
            continue
        color = ENCODER_COLORS.get(enc, "black")
        label = ENCODER_LABELS.get(enc, enc)
        ax.plot(xs, ys, marker="o", color=color, label=label, linewidth=2)
        ax.fill_between(xs, lo_errs, hi_errs, alpha=0.2, color=color)

    ax.set_xscale("log")
    ax.set_xticks(x_numeric)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Training Size (# zoo models)")
    ax.set_ylabel("R² (test set)")
    ax.set_ylim(-0.3, 1.05)
    ax.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax.set_title(f"Learning Curves — {zoo_name.upper()} Zoo")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_efficiency_bar(efficiency_ratios, out_path):
    """Grouped bar chart of efficiency ratios per (encoder, zoo)."""
    equivariant = [e for e in efficiency_ratios if e in ("gnn_nfn", "dwsnets")]
    if not equivariant:
        print("  No equivariant encoders to plot efficiency bar.")
        return

    zoos = cfg.ZOO_NAMES
    n_enc = len(equivariant)
    n_zoo = len(zoos)
    bar_width = 0.35
    x = np.arange(n_enc)

    fig, ax = plt.subplots(figsize=(7, 4))
    zoo_colors = {"mnist": "steelblue", "cifar10": "coral"}

    for i, zoo in enumerate(zoos):
        vals = [efficiency_ratios.get(enc, {}).get(zoo, 0.0) for enc in equivariant]
        # Cap inf for display
        vals_display = [min(v, 10.0) if not np.isinf(v) else 10.0 for v in vals]
        offset = (i - n_zoo / 2 + 0.5) * bar_width
        bars = ax.bar(x + offset, vals_display, bar_width,
                      label=zoo.upper(), color=zoo_colors.get(zoo, "blue"), alpha=0.8)
        for bar, val in zip(bars, vals):
            label_str = f"{val:.2f}×" if not np.isinf(val) else "∞"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    label_str, ha="center", va="bottom", fontsize=9)

    ax.axhline(2.0, color="red", linestyle="--", linewidth=1.5, label="Gate threshold (2.0×)")
    ax.set_xticks(x)
    ax.set_xticklabels([ENCODER_LABELS.get(e, e) for e in equivariant])
    ax.set_ylabel("Efficiency Ratio (N_plain / N_equiv at 90% peak R²)")
    ax.set_title("Sample Efficiency Ratio (N_plain(90%peak) / N_equiv(90%peak))")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_seed_traces(results, zoo_name, out_path):
    """Individual seed R² traces (alpha=0.2) + mean curve overlay."""
    sizes_ordered = cfg.TRAINING_SIZES
    x_numeric = [_size_to_num(s) for s in sizes_ordered]

    fig, ax = plt.subplots(figsize=(8, 5))

    for enc in cfg.ENCODER_NAMES:
        if enc not in results or zoo_name not in results[enc]:
            continue
        color = ENCODER_COLORS.get(enc, "black")
        label = ENCODER_LABELS.get(enc, enc)
        zoo_data = results[enc][zoo_name]
        mean_xs, mean_ys = [], []
        for s, xn in zip(sizes_ordered, x_numeric):
            k = str(s)
            if k not in zoo_data:
                continue
            cell = zoo_data[k]
            mean_xs.append(xn)
            mean_ys.append(cell["mean_r2"])
            for r2 in cell.get("seed_r2s", []):
                ax.plot([xn], [r2], "o", color=color, alpha=0.2, markersize=4)
        ax.plot(mean_xs, mean_ys, color=color, linewidth=2, label=label)

    ax.set_xscale("log")
    ax.set_xlabel("Training Size")
    ax.set_ylabel("R² (test)")
    ax.set_title(f"Per-Seed Traces — {zoo_name.upper()} Zoo")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")
