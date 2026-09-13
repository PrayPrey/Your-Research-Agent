import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def fig1_gate_summary(results: dict, out_dir: str) -> None:
    proxies = ["prompt_tokens", "vote_entropy", "correction_freq"]
    labels = ["Prompt Tokens", "Vote Entropy", "Correction Freq"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for ax, proxy, label in zip(axes, proxies, labels):
        r = results["proxies"].get(proxy, {})
        tau = r.get("tau", 0.0)
        p = r.get("p", 1.0)
        ci_low = r.get("ci_low", tau)
        ci_high = r.get("ci_high", tau)
        sig = r.get("significant", False)
        color = "#2ecc71" if sig else "#e74c3c"

        ax.bar([0], [tau], color=color, width=0.4,
               yerr=[[tau - ci_low], [ci_high - tau]],
               ecolor="black", capsize=5)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        offset = 0.03 if tau >= 0 else -0.06
        ax.text(0, tau + offset, f"p={p:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks([0])
        ax.set_xticklabels([label])
        ax.set_ylabel("Kendall τ" if proxy == "prompt_tokens" else "")
        ax.set_title(label)

    gate = results.get("gate", {})
    n_sig = gate.get("n_significant", 0)
    passed = gate.get("gate_passed", False)
    plt.suptitle(f"Gate Summary: τ by Proxy | n_significant={n_sig} | {'PASS' if passed else 'FAIL'}",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f"{out_dir}/fig1_gate_summary.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig2_proxy_timeseries(wildchat_monthly: pd.DataFrame, proxy2: pd.Series, results: dict, out_dir: str) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    months = wildchat_monthly["month"].values
    x = np.arange(len(months))

    panels = [
        ("prompt_tokens_mean", "Proxy 1: Prompt Tokens", "Mean Tokens"),
        ("correction_freq_mean", "Proxy 3: Correction Freq", "Freq"),
    ]

    for i, (col, title, ylabel) in enumerate(panels):
        ax = axes[i]
        vals = wildchat_monthly[col].values
        ax.plot(x, vals, marker="o", linewidth=1.5, label=ylabel)
        # trend line
        valid_mask = ~np.isnan(vals)
        if valid_mask.sum() > 1:
            z = np.polyfit(x[valid_mask], vals[valid_mask], 1)
            ax.plot(x, np.polyval(z, x), "r--", linewidth=1, label="trend")
        ax.set_xticks(x[::4])
        ax.set_xticklabels(months[::4], rotation=45, fontsize=7)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=7)

    # proxy2 panel
    ax = axes[2]
    p2_months = proxy2.index.tolist()
    p2_vals = proxy2.values
    x2 = np.arange(len(p2_months))
    ax.plot(x2, p2_vals, marker="o", linewidth=1.5, color="purple", label="entropy")
    valid_mask = ~np.isnan(p2_vals)
    if valid_mask.sum() > 1:
        z = np.polyfit(x2[valid_mask], p2_vals[valid_mask], 1)
        ax.plot(x2, np.polyval(z, x2), "r--", linewidth=1, label="trend")
    ax.set_xticks(x2[::4])
    ax.set_xticklabels(p2_months[::4], rotation=45, fontsize=7)
    ax.set_title("Proxy 2: Vote Entropy")
    ax.set_ylabel("Shannon H (bits)")
    ax.legend(fontsize=7)

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f"{out_dir}/fig2_proxy_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig3_cohort_funnel(funnel_counts: dict, out_dir: str) -> None:
    labels = ["Total IPs", "≥1 monthly bin", "≥3 monthly bins", "Analysis cohort"]
    keys = ["total_ips", "ips_ge1_bin", "ips_ge3_bins", "analysis_cohort_size"]
    values = [funnel_counts.get(k, 0) for k in keys]
    total = values[0] if values[0] > 0 else 1

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]
    bars = ax.barh(labels, values, color=colors)
    for bar, val in zip(bars, values):
        pct = 100 * val / total
        ax.text(bar.get_width() + total * 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:,} ({pct:.1f}%)", va="center", fontsize=9)
    ax.set_xlabel("Count")
    ax.set_title("WildChat Cohort Retention Funnel")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f"{out_dir}/fig3_cohort_funnel.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig4_lmsys_votes(lmsys_monthly: pd.DataFrame, proxy2: pd.Series, out_dir: str) -> None:
    if lmsys_monthly.empty:
        return

    monthly_agg = lmsys_monthly.groupby("month")[["win_count", "lose_count", "tie_count"]].sum()
    monthly_agg["total"] = monthly_agg.sum(axis=1)
    for col in ["win_count", "lose_count", "tie_count"]:
        monthly_agg[col] = monthly_agg[col] / monthly_agg["total"]

    fig, ax1 = plt.subplots(figsize=(12, 4))
    x = np.arange(len(monthly_agg))
    ax1.bar(x, monthly_agg["win_count"], label="Win (A)", color="#3498db")
    ax1.bar(x, monthly_agg["lose_count"], bottom=monthly_agg["win_count"], label="Lose (B)", color="#e74c3c")
    ax1.bar(x, monthly_agg["tie_count"],
            bottom=monthly_agg["win_count"] + monthly_agg["lose_count"], label="Tie", color="#95a5a6")
    ax1.set_xticks(x[::2])
    ax1.set_xticklabels(monthly_agg.index[::2], rotation=45, fontsize=7)
    ax1.set_ylabel("Proportion")
    ax1.legend(loc="upper left", fontsize=7)

    ax2 = ax1.twinx()
    common = [m for m in monthly_agg.index if m in proxy2.index]
    if common:
        xi = [list(monthly_agg.index).index(m) for m in common]
        ax2.plot(xi, proxy2[common].values, "k-o", markersize=4, linewidth=1.5, label="Entropy")
        ax2.set_ylabel("Shannon H (bits)")
        ax2.legend(loc="upper right", fontsize=7)

    ax1.set_title("LMSYS Monthly Vote Distribution + Entropy Overlay")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f"{out_dir}/fig4_lmsys_votes.png", dpi=150, bbox_inches="tight")
    plt.close()
