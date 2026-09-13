"""4 required figures for H-M1."""
from __future__ import annotations

import os
import numpy as np
import pandas as pd


def _setup_style(style: str = "seaborn-v0_8-whitegrid") -> None:
    import matplotlib.pyplot as plt
    try:
        plt.style.use(style)
    except OSError:
        plt.style.use("seaborn-whitegrid")


def plot_domain_proxy_comparison(
    summary: pd.DataFrame,
    out_path: str,
    dpi: int = 150,
    fig_width: float = 14.0,
    fig_height: float = 6.0,
) -> None:
    """Bar chart mean ± 95CI, 3 proxies × 22 domains, sorted by entity_density."""
    import matplotlib.pyplot as plt
    _setup_style()

    proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
    entity_order = (
        summary[summary["proxy"] == "entity_density"]
        .sort_values("mean", ascending=False)["domain"]
        .tolist()
    )

    fig, axes = plt.subplots(1, 3, figsize=(fig_width * 3 / 2, fig_height))
    for ax, proxy in zip(axes, proxies):
        sub = summary[summary["proxy"] == proxy].set_index("domain").reindex(entity_order)
        means = sub["mean"].values
        yerr = np.array([
            sub["mean"].values - sub["ci_lower"].values,
            sub["ci_upper"].values - sub["mean"].values,
        ])
        ax.bar(range(len(entity_order)), means, yerr=yerr, capsize=4, color="steelblue", alpha=0.8)
        ax.set_xticks(range(len(entity_order)))
        ax.set_xticklabels(entity_order, rotation=90, fontsize=7)
        ax.set_title(proxy.replace("_", " ").title())
        ax.set_ylabel("Mean score")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def plot_focal_domain_violins(
    domain_scores: dict[str, dict[str, list[float]]],
    focal_domains: list[str],
    out_path: str,
    dpi: int = 150,
    fig_width: float = 10.0,
    fig_height: float = 8.0,
) -> None:
    """Violin plots for 3 focal domains × 3 proxies."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    _setup_style()

    proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
    rows = []
    for domain in focal_domains:
        if domain not in domain_scores:
            continue
        for proxy in proxies:
            for val in domain_scores[domain].get(proxy, []):
                rows.append({"domain": domain, "proxy": proxy, "value": val})

    df = pd.DataFrame(rows)
    if df.empty:
        return

    fig, axes = plt.subplots(1, 3, figsize=(fig_width, fig_height))
    for ax, proxy in zip(axes, proxies):
        sub = df[df["proxy"] == proxy]
        if sub.empty:
            continue
        sns.violinplot(data=sub, x="domain", y="value", ax=ax, inner="box")
        ax.set_title(proxy.replace("_", " ").title())
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, fontsize=8)
        ax.set_xlabel("")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def plot_tukey_heatmap(
    tukey_result,
    out_path: str,
    dpi: int = 150,
    fig_size: float = 10.0,
) -> None:
    """22×22 Tukey HSD reject matrix heatmap for entity_density."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    _setup_style()

    data = tukey_result._results_table.data
    df = pd.DataFrame(data[1:], columns=data[0])
    domains = sorted(set(df["group1"].tolist() + df["group2"].tolist()))
    n = len(domains)
    matrix = pd.DataFrame(False, index=domains, columns=domains)

    for _, row in df.iterrows():
        matrix.loc[row["group1"], row["group2"]] = bool(row["reject"])
        matrix.loc[row["group2"], row["group1"]] = bool(row["reject"])

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(
        matrix.astype(int), ax=ax,
        cmap="RdYlGn", vmin=0, vmax=1,
        xticklabels=True, yticklabels=True,
        linewidths=0.5,
    )
    ax.set_title("Tukey HSD Reject Matrix — entity_density")
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def plot_proxy_correlation_scatter(
    domain_scores: dict[str, dict[str, list[float]]],
    out_path: str,
    dpi: int = 150,
    fig_width: float = 8.0,
    fig_height: float = 6.0,
) -> None:
    """entity_density vs narrative_coherence scatter, colored by domain."""
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    _setup_style()

    domains = list(domain_scores.keys())
    cmap = cm.get_cmap("tab20", len(domains))
    color_map = {d: cmap(i) for i, d in enumerate(domains)}

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    for domain, scores in domain_scores.items():
        ed = scores.get("entity_density", [])
        nc = scores.get("narrative_coherence", [])
        n = min(len(ed), len(nc))
        if n == 0:
            continue
        ax.scatter(
            ed[:n], nc[:n],
            alpha=0.3, s=5,
            color=color_map[domain],
            label=domain,
        )

    ax.set_xlabel("Entity Density")
    ax.set_ylabel("Narrative Coherence")
    ax.set_title("Entity Density vs Narrative Coherence by Domain")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=6, markerscale=3, loc="upper right",
               ncol=2, framealpha=0.7)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()
