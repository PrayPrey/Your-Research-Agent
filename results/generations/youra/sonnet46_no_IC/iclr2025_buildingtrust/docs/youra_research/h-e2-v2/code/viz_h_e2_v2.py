"""H-E2-v2 gate bar chart visualization."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_gate_bar_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    topology_stability_h_e2: float,
    out_path: str,
    dpi: int = 300,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Left: primary gate — mst_min_set_size vs threshold 4
    ax = axes[0]
    color = "steelblue" if mst_min_set_size <= 4 else "firebrick"
    ax.bar(["min_set_size"], [mst_min_set_size], color=color)
    ax.axhline(4, color="red", linestyle="--", label="threshold=4")
    ax.set_title("Primary Gate: MST Min Set Size")
    ax.set_ylabel("# dimensions")
    ax.set_ylim(0, max(6, mst_min_set_size + 1))
    ax.legend()

    # Right: secondary gate — mean_per_edge_freq vs 0.90, overlay old topology_stability
    ax = axes[1]
    ax.bar(
        ["mean_per_edge_freq (v2)", "topology_stability (H-E2)"],
        [mean_per_edge_freq, topology_stability_h_e2],
        color=["steelblue" if mean_per_edge_freq >= 0.90 else "firebrick", "gray"],
    )
    ax.axhline(0.90, color="red", linestyle="--", label="threshold=0.90")
    ax.set_ylim(0, 1.1)
    ax.set_title("Secondary Gate: Bootstrap Frequency")
    ax.set_ylabel("frequency / stability")
    ax.legend()

    gate_str = "PASS" if (mst_min_set_size <= 4 and mean_per_edge_freq >= 0.90) else "FAIL"
    fig.suptitle(f"H-E2-v2 Gate: {gate_str}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    import os, tempfile
    tmp = os.path.join(tempfile.gettempdir(), "test_gate_v2.png")
    plot_gate_bar_v2(3, 0.917, 0.606, tmp)
    assert os.path.exists(tmp), f"File not created: {tmp}"
    print(f"OK: {tmp}")
