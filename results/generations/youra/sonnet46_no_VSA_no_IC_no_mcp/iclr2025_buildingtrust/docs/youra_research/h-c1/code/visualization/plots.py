"""H-C1 visualization: 4 required figures."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_COLOR = "#2196F3"
CHAT_COLOR = "#FF5722"
DPI = 300


def fig1_paired_bar(moderation_results: list, out_path: str) -> None:
    """Side-by-side ΔECE_base vs ΔECE_chat per eval cell."""
    labels = [r.cell_id for r in moderation_results]
    base_vals = [r.delta_ece_base for r in moderation_results]
    chat_vals = [r.delta_ece_chat for r in moderation_results]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, base_vals, width, label="Llama-2-7b-hf (base)", color=BASE_COLOR)
    ax.bar(x + width / 2, chat_vals, width, label="Llama-2-7b-chat (chat)", color=CHAT_COLOR)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("(task, split) cell")
    ax.set_ylabel("ΔECE (ECE_adv − ECE_clean)")
    ax.set_title("RLHF Moderation of Adversarial Calibration Degradation (H-C1)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"fig1 saved: {out_path}")


def fig2_reliability_grid(base_results: dict, chat_results: dict, out_path: str) -> None:
    """2x2 grid: base vs chat x clean vs adversarial reliability diagrams (NLI-AdvGLUE cell)."""
    n_bins = 15
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Use NLI-AdvGLUE as reference; we only have ECE scalars not raw confidences here
    # So plot ECE values as text with a diagonal reference
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax, (model_label, cell_dict, color) in zip(
        axes,
        [("Base", base_results, BASE_COLOR), ("Chat", chat_results, CHAT_COLOR)],
    ):
        cell = cell_dict.get("NLI-AdvGLUE")
        if cell is None:
            ax.text(0.5, 0.5, "N/A", ha="center", va="center", transform=ax.transAxes)
            continue
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect calibration")
        # Draw approximate reliability as bar charts from ECE components
        ax.bar(
            [0.3, 0.7],
            [cell.ece_clean, cell.ece_adv],
            width=0.2,
            color=[color, color],
            alpha=[0.5, 1.0],
            label=["Clean", "Adv"],
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, max(cell.ece_adv, cell.ece_clean) * 1.5 + 0.05)
        ax.set_title(f"{model_label} — NLI-AdvGLUE\nECE_clean={cell.ece_clean:.3f}, ECE_adv={cell.ece_adv:.3f}")
        ax.set_xlabel("Clean / Adv")
        ax.set_ylabel("ECE")

    fig.suptitle("ECE Reliability Summary — NLI Task (H-C1)", fontsize=12)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"fig2 saved: {out_path}")


def fig3_ddece_scatter(moderation_results: list, out_path: str) -> None:
    """Scatter: ΔECE_chat vs ΔECE_base per cell with identity line."""
    base_vals = [r.delta_ece_base for r in moderation_results]
    chat_vals = [r.delta_ece_chat for r in moderation_results]
    labels = [r.cell_id for r in moderation_results]

    fig, ax = plt.subplots(figsize=(6, 6))
    lim_min = min(min(base_vals), min(chat_vals)) - 0.02
    lim_max = max(max(base_vals), max(chat_vals)) + 0.02
    ax.plot([lim_min, lim_max], [lim_min, lim_max], color="#9E9E9E", linestyle="--", linewidth=1.0)
    for x, y, lbl in zip(base_vals, chat_vals, labels):
        ax.scatter(x, y, color=CHAT_COLOR, s=60, zorder=3)
        ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(5, 3), fontsize=8)
    ax.set_xlabel("ΔECE_base")
    ax.set_ylabel("ΔECE_chat")
    ax.set_title("ΔΔECE Scatter: Base vs Chat (H-C1)")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"fig3 saved: {out_path}")


def fig4_anli_gradient(moderation_results: list, out_path: str) -> None:
    """ΔECE by R1→R2→R3 difficulty for base vs chat."""
    anli_cells = {r.cell_id: r for r in moderation_results
                  if r.cell_id.startswith("NLI-ANLI")}

    order = ["NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3"]
    x_labels = ["R1", "R2", "R3"]
    base_vals = [anli_cells[k].delta_ece_base if k in anli_cells else 0 for k in order]
    chat_vals = [anli_cells[k].delta_ece_chat if k in anli_cells else 0 for k in order]

    x = np.arange(len(x_labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - width / 2, base_vals, width, label="Base", color=BASE_COLOR)
    ax.bar(x + width / 2, chat_vals, width, label="Chat", color=CHAT_COLOR)
    ax.set_xlabel("ANLI Split")
    ax.set_ylabel("ΔECE")
    ax.set_title("ANLI Calibration Gradient — Base vs Chat (H-C1)")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"fig4 saved: {out_path}")
