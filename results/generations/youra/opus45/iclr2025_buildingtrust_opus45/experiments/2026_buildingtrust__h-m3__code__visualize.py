"""Visualization functions for H-M3 Brier decomposition experiment.

Generates publication-quality figures for validation report.
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

from config import FIGURES_DIR, N_BINS
from brier_decomp import margin_to_confidence


def plot_brier_decomposition_comparison(
    family_results: dict[str, dict],
    output_dir: Optional[Path] = None,
) -> Path:
    """Grouped bar chart: REL/RES/UNC for base vs instruct per family.

    Args:
        family_results: Analysis results from analyze_family
        output_dir: Output directory (default: FIGURES_DIR)

    Returns:
        Path to saved figure
    """
    output_dir = output_dir or FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    families = list(family_results.keys())
    n_families = len(families)

    components = ["reliability", "resolution", "uncertainty"]
    n_components = len(components)

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(n_families)
    width = 0.35

    for i, component in enumerate(components):
        base_vals = []
        inst_vals = []
        base_errs = []
        inst_errs = []

        for family in families:
            results = family_results[family]
            base_decomp = results["base"]["decomposition"]
            inst_decomp = results["instruct"]["decomposition"]
            base_ci = results["base"]["confidence_intervals"][component]
            inst_ci = results["instruct"]["confidence_intervals"][component]

            base_vals.append(base_decomp[component])
            inst_vals.append(inst_decomp[component])
            base_errs.append((base_ci[0] - base_ci[1], base_ci[2] - base_ci[0]))
            inst_errs.append((inst_ci[0] - inst_ci[1], inst_ci[2] - inst_ci[0]))

        offset = (i - 1) * (width * 2 + 0.1)

        # Base model bars
        ax.bar(
            x + offset - width / 2,
            base_vals,
            width,
            label=f"{component.title()} (Base)" if i == 0 else "",
            color=f"C{i}",
            alpha=0.7,
        )

        # Instruct model bars
        ax.bar(
            x + offset + width / 2,
            inst_vals,
            width,
            label=f"{component.title()} (Instruct)" if i == 0 else "",
            color=f"C{i}",
            alpha=0.4,
            hatch="//",
        )

    ax.set_xlabel("Model Family")
    ax.set_ylabel("Component Value")
    ax.set_title("Brier Score Decomposition: Base vs Instruct")
    ax.set_xticks(x)
    ax.set_xticklabels([f.title() for f in families])
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / "brier_decomposition_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return output_path


def plot_reliability_diagram(
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Optional[Path] = None,
    n_bins: int = N_BINS,
) -> Path:
    """Calibration curve: predicted probability vs observed frequency.

    Args:
        family_data: Raw data from load_all_families
        output_dir: Output directory
        n_bins: Number of calibration bins

    Returns:
        Path to saved figure
    """
    output_dir = output_dir or FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    families = list(family_data.keys())
    n_families = len(families)

    fig, axes = plt.subplots(1, n_families, figsize=(5 * n_families, 5))
    if n_families == 1:
        axes = [axes]

    for ax, family in zip(axes, families):
        data = family_data[family]

        for model_type, margins_key, correct_key, color, label in [
            ("Base", "base_margins", "base_correctness", "C0", "Base"),
            ("Instruct", "inst_margins", "inst_correctness", "C1", "Instruct"),
        ]:
            conf = margin_to_confidence(data[margins_key])
            correct = data[correct_key]

            # Compute calibration curve
            bin_edges = np.linspace(0, 1, n_bins + 1)
            bin_means = []
            bin_accs = []
            bin_counts = []

            for i in range(n_bins):
                mask = (conf >= bin_edges[i]) & (conf < bin_edges[i + 1])
                if i == n_bins - 1:  # Include right edge
                    mask = (conf >= bin_edges[i]) & (conf <= bin_edges[i + 1])

                if np.sum(mask) > 0:
                    bin_means.append(np.mean(conf[mask]))
                    bin_accs.append(np.mean(correct[mask]))
                    bin_counts.append(np.sum(mask))

            ax.plot(
                bin_means,
                bin_accs,
                "o-",
                color=color,
                label=label,
                markersize=6,
            )

        # Perfect calibration line
        ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect")

        ax.set_xlabel("Predicted Confidence")
        ax.set_ylabel("Observed Accuracy")
        ax.set_title(f"{family.title()}: Reliability Diagram")
        ax.legend()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)
        ax.set_aspect("equal")

    plt.tight_layout()
    output_path = output_dir / "reliability_diagram.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return output_path


def plot_refinement_delta_forest(
    family_results: dict[str, dict],
    output_dir: Optional[Path] = None,
) -> Path:
    """Forest plot of refinement delta (base - instruct) with 95% CIs.

    Args:
        family_results: Analysis results from analyze_family
        output_dir: Output directory

    Returns:
        Path to saved figure
    """
    output_dir = output_dir or FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    families = list(family_results.keys())

    fig, ax = plt.subplots(figsize=(8, 4))

    y_positions = np.arange(len(families))

    for i, family in enumerate(families):
        results = family_results[family]
        diff = results["refinement_difference"]

        delta = diff["delta_mean"]
        ci_lower = diff["delta_ci_lower"]
        ci_upper = diff["delta_ci_upper"]

        # Plot point estimate
        ax.scatter(
            delta,
            i,
            s=100,
            color="C0" if results["gate_pass"] else "C3",
            zorder=3,
        )

        # Plot CI
        ax.hlines(
            i,
            ci_lower,
            ci_upper,
            colors="C0" if results["gate_pass"] else "C3",
            linewidth=2,
        )

    # Zero reference line
    ax.axvline(0, color="k", linestyle="--", alpha=0.5)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f.title() for f in families])
    ax.set_xlabel("Δ Refinement (Base - Instruct)")
    ax.set_title("Refinement Degradation: Forest Plot\n(Positive = Base has higher refinement)")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / "refinement_delta_forest.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return output_path


def plot_decomposition_verification(
    family_results: dict[str, dict],
    output_dir: Optional[Path] = None,
) -> Path:
    """Scatter plot: BS_computed vs (REL - RES + UNC) for verification.

    Args:
        family_results: Analysis results
        output_dir: Output directory

    Returns:
        Path to saved figure
    """
    output_dir = output_dir or FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 6))

    bs_computed = []
    bs_reconstructed = []
    labels = []

    for family, results in family_results.items():
        for model_type in ["base", "instruct"]:
            decomp = results[model_type]["decomposition"]
            bs = decomp["brier_score"]
            rel = decomp["reliability"]
            res = decomp["resolution"]
            unc = decomp["uncertainty"]
            recon = rel - res + unc

            bs_computed.append(bs)
            bs_reconstructed.append(recon)
            labels.append(f"{family.title()} ({model_type.title()})")

    # Scatter plot
    ax.scatter(bs_computed, bs_reconstructed, s=100, c="C0")

    # Perfect decomposition line
    min_val = min(min(bs_computed), min(bs_reconstructed))
    max_val = max(max(bs_computed), max(bs_reconstructed))
    ax.plot([min_val, max_val], [min_val, max_val], "k--", alpha=0.5)

    # Labels
    for i, label in enumerate(labels):
        ax.annotate(
            label,
            (bs_computed[i], bs_reconstructed[i]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    ax.set_xlabel("BS (Computed)")
    ax.set_ylabel("REL - RES + UNC (Reconstructed)")
    ax.set_title("Decomposition Verification")
    ax.grid(alpha=0.3)
    ax.set_aspect("equal")

    plt.tight_layout()
    output_path = output_dir / "decomposition_verification.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return output_path


def save_all_figures(
    family_results: dict[str, dict],
    family_data: dict[str, dict[str, np.ndarray]],
    output_dir: Optional[Path] = None,
) -> list[Path]:
    """Generate all figures for the experiment.

    Args:
        family_results: Analysis results from analyze_family
        family_data: Raw data from load_all_families
        output_dir: Output directory

    Returns:
        List of saved figure paths
    """
    output_dir = output_dir or FIGURES_DIR

    paths = []
    paths.append(plot_brier_decomposition_comparison(family_results, output_dir))
    paths.append(plot_reliability_diagram(family_data, output_dir))
    paths.append(plot_refinement_delta_forest(family_results, output_dir))
    paths.append(plot_decomposition_verification(family_results, output_dir))

    return paths
