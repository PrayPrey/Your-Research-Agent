"""FR-6: Figure generation for H-M1 orbit invariance probe."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch


FIG_DIR = os.path.join(os.path.dirname(__file__), "../../figures")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def fig_gate_metrics(gate: dict, out_dir: str = FIG_DIR):
    """FR-6.1: Bar chart of mean within vs cross similarity with CI error bars."""
    _ensure_dir(out_dir)
    orbit_types = ["scaling", "signflip"]
    labels = ["Scaling", "Sign-flip"]
    x = np.arange(len(orbit_types))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (ot, lab) in enumerate(zip(orbit_types, labels)):
        r = gate[ot]
        # Within sim
        within_err = r["within_stats"]["ci_high"] - r["within_stats"]["mean"]
        ax.bar(x[i] - width/2, r["mean_within_sim"], width, label="Within-orbit sim" if i == 0 else "",
               color="#2196F3", alpha=0.8,
               yerr=[[r["mean_within_sim"] - r["within_stats"]["ci_low"]], [within_err]])
        # Cross sim
        cross_err = r["cross_stats"]["ci_high"] - r["cross_stats"]["mean"]
        ax.bar(x[i] + width/2, r["mean_cross_sim"], width, label="Cross-orbit sim" if i == 0 else "",
               color="#FF9800", alpha=0.8,
               yerr=[[r["mean_cross_sim"] - r["cross_stats"]["ci_low"]], [cross_err]])

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean Cosine Similarity")
    ax.set_title("NFT Orbit Invariance Probe: Within vs Cross-Orbit Similarity\n"
                 f"Overall: {'PASS' if gate['overall_pass'] else 'FAIL'}")
    ax.legend()
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    out = os.path.join(out_dir, "fig_gate_metrics.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


def fig_sim_distributions(results_scaling: dict, results_signflip: dict, out_dir: str = FIG_DIR):
    """FR-6.2: Overlapping histograms of within vs cross similarity per orbit type."""
    _ensure_dir(out_dir)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, res, title in zip(axes,
                               [results_scaling, results_signflip],
                               ["Scaling Orbit", "Sign-flip Orbit"]):
        within = res["within_sim"].numpy()
        cross  = res["cross_sim"].numpy()
        bins = np.linspace(min(within.min(), cross.min()) - 0.05,
                           max(within.max(), cross.max()) + 0.05, 50)
        ax.hist(within, bins=bins, alpha=0.6, label="Within-orbit", color="#2196F3", density=True)
        ax.hist(cross,  bins=bins, alpha=0.6, label="Cross-orbit",  color="#FF9800", density=True)
        ax.axvline(within.mean(), color="#2196F3", linestyle="--", label=f"Within mean={within.mean():.3f}")
        ax.axvline(cross.mean(),  color="#FF9800", linestyle="--", label=f"Cross mean={cross.mean():.3f}")
        ax.set_xlabel("Cosine Similarity")
        ax.set_ylabel("Density")
        ax.set_title(title)
        ax.legend(fontsize=8)
    plt.suptitle("NFT Embedding Similarity Distributions")
    plt.tight_layout()
    out = os.path.join(out_dir, "fig_sim_distributions.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


def fig_per_model_scatter(results_scaling: dict, results_signflip: dict, zoo_properties: torch.Tensor,
                           base_idx_scaling: list, base_idx_signflip: list, out_dir: str = FIG_DIR):
    """FR-6.3: Within-orbit similarity vs test_accuracy scatter."""
    _ensure_dir(out_dir)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, res, bidx, title in zip(
        axes,
        [results_scaling, results_signflip],
        [base_idx_scaling, base_idx_signflip],
        ["Scaling Orbit", "Sign-flip Orbit"],
    ):
        within = res["within_sim"].numpy()
        acc = zoo_properties[bidx, 0].numpy()
        ax.scatter(acc, within, alpha=0.3, s=5, color="#2196F3")
        ax.set_xlabel("Test Accuracy")
        ax.set_ylabel("Within-orbit Cosine Similarity")
        ax.set_title(title)
        # Linear fit
        if len(acc) > 2:
            z = np.polyfit(acc, within, 1)
            p = np.poly1d(z)
            xs = np.linspace(acc.min(), acc.max(), 100)
            ax.plot(xs, p(xs), "r--", linewidth=1, label=f"slope={z[0]:.3f}")
            ax.legend(fontsize=8)
    plt.suptitle("Within-orbit Similarity vs Model Test Accuracy")
    plt.tight_layout()
    out = os.path.join(out_dir, "fig_per_model_scatter.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


def fig_embedding_pca(
    emb_base: torch.Tensor, emb_orbit: torch.Tensor,
    n_show: int = 50, title_suffix: str = "Scaling", out_dir: str = FIG_DIR
):
    """FR-6.4: 2D PCA of base and orbit embeddings."""
    from sklearn.decomposition import PCA
    _ensure_dir(out_dir)
    n = min(n_show, emb_base.shape[0])
    all_emb = torch.cat([emb_base[:n], emb_orbit[:n]], dim=0).numpy()
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(all_emb)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(coords[:n, 0], coords[:n, 1], c="#2196F3", alpha=0.7, s=30, label="Base", zorder=3)
    ax.scatter(coords[n:, 0], coords[n:, 1], c="#FF9800", alpha=0.7, s=30, label="Orbit member", marker="^", zorder=3)
    # Draw lines connecting pairs
    for i in range(n):
        ax.plot([coords[i, 0], coords[n+i, 0]], [coords[i, 1], coords[n+i, 1]],
                "gray", alpha=0.2, linewidth=0.5)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title(f"NFT Embedding PCA — {title_suffix} Orbit Pairs (n={n})")
    ax.legend()
    plt.tight_layout()
    out = os.path.join(out_dir, f"fig_embedding_pca_{title_suffix.lower()}.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


def fig_similarity_heatmap(
    emb_base: torch.Tensor, emb_orbit: torch.Tensor,
    n_show: int = 25, title_suffix: str = "Scaling", out_dir: str = FIG_DIR
):
    """FR-6.5: N×N cosine similarity heatmap for base + orbit members."""
    import torch.nn.functional as F
    _ensure_dir(out_dir)
    n = min(n_show, emb_base.shape[0])
    all_emb = F.normalize(torch.cat([emb_base[:n], emb_orbit[:n]], dim=0), dim=-1)
    sim_mat = (all_emb @ all_emb.T).numpy()

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(sim_mat, aspect="auto", vmin=-1, vmax=1, cmap="RdBu_r")
    plt.colorbar(im, ax=ax, label="Cosine Similarity")
    ax.axvline(n - 0.5, color="black", linewidth=2)
    ax.axhline(n - 0.5, color="black", linewidth=2)
    ax.set_title(f"NFT Similarity Heatmap — {title_suffix} (first {n} base + {n} orbit)")
    ax.set_xlabel("Model index (0-{n-1}: base, {n}-{2n-1}: orbit)")
    ax.set_ylabel("Model index")
    plt.tight_layout()
    out = os.path.join(out_dir, f"fig_similarity_heatmap_{title_suffix.lower()}.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


def generate_all_figures(
    results_scaling: dict, results_signflip: dict,
    zoo_properties: torch.Tensor, gate: dict,
    emb_base_s: torch.Tensor, emb_orbit_s: torch.Tensor,
    emb_base_sf: torch.Tensor, emb_orbit_sf: torch.Tensor,
    out_dir: str = FIG_DIR,
):
    """Generate all 5 required figures."""
    fig_gate_metrics(gate, out_dir)
    fig_sim_distributions(results_scaling, results_signflip, out_dir)
    fig_per_model_scatter(
        results_scaling, results_signflip, zoo_properties,
        results_scaling["base_indices"], results_signflip["base_indices"], out_dir
    )
    fig_embedding_pca(emb_base_s,  emb_orbit_s,  title_suffix="Scaling",   out_dir=out_dir)
    fig_embedding_pca(emb_base_sf, emb_orbit_sf, title_suffix="Signflip",  out_dir=out_dir)
    fig_similarity_heatmap(emb_base_s,  emb_orbit_s,  title_suffix="Scaling",  out_dir=out_dir)
    fig_similarity_heatmap(emb_base_sf, emb_orbit_sf, title_suffix="Signflip", out_dir=out_dir)
    print(f"All figures saved to {out_dir}")
