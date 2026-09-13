import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from analysis import GateResult


def plot_gate_metrics(
    errors_by_N: dict,
    gate_result: GateResult,
    out_dir: str,
) -> None:
    """Fig 1: bar chart pct90 per N + log-log curve with slope annotation."""
    Ns = sorted(errors_by_N.keys())
    pct90s = [float(np.percentile(errors_by_N[N], 90)) for N in Ns]
    mean_errors = [float(np.mean(errors_by_N[N])) for N in Ns]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart
    bars = ax1.bar([str(N) for N in Ns], pct90s, color="#2196F3", alpha=0.8)
    ax1.axhline(0.3, color="#F44336", linestyle="--", label="Threshold 0.3")
    ax1.set_xlabel("Sequence Length N")
    ax1.set_ylabel("90th Pct Frobenius Error")
    ax1.set_title("90th Percentile Error per N")
    ax1.legend()

    # Log-log plot
    ax2.plot(np.log(Ns), np.log(mean_errors), "o-", color="#2196F3", label="SSD")
    # Regression line
    log_Ns = np.log(Ns)
    log_Es = np.log([max(e, 1e-9) for e in mean_errors])
    slope, intercept = np.polyfit(log_Ns, log_Es, 1)
    ax2.plot(log_Ns, slope * log_Ns + intercept, "--", color="#888888",
             label=f"β={slope:.3f}")
    ax2.set_xlabel("log N")
    ax2.set_ylabel("log Mean Frobenius Error")
    ax2.set_title(f"Log-Log Scaling  (β={gate_result.log_slope:.3f}, {gate_result.decision})")
    ax2.legend()

    plt.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.savefig(str(Path(out_dir) / "fig1_gate_bar_loglog.png"), dpi=150)
    plt.close()


def plot_scaling_comparison(
    ssd_errors_by_N: dict,
    toeplitz_errors_by_N: dict,
    beta: float,
    out_dir: str,
) -> None:
    """Fig 2: log-log SSD vs Toeplitz with regression line."""
    Ns = sorted(ssd_errors_by_N.keys())
    ssd_means = [float(np.mean(ssd_errors_by_N[N])) for N in Ns]
    toep_means = [float(np.mean(toeplitz_errors_by_N[N])) for N in Ns]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(Ns, ssd_means, "o-", color="#2196F3", label="SSD")
    ax.loglog(Ns, toep_means, "s-", color="#FF5722", label="Toeplitz")

    log_Ns = np.log(Ns)
    log_Es = np.log([max(e, 1e-9) for e in ssd_means])
    slope, intercept = np.polyfit(log_Ns, log_Es, 1)
    fitted = np.exp(slope * log_Ns + intercept)
    ax.loglog(Ns, fitted, "--", color="#888888", label=f"β={slope:.3f}")

    ax.set_xlabel("Sequence Length N (log scale)")
    ax.set_ylabel("Mean Frobenius Error (log scale)")
    ax.set_title("SSD vs Toeplitz Scaling")
    ax.legend()
    plt.tight_layout()
    plt.savefig(str(Path(out_dir) / "fig2_scaling_ssd_vs_toeplitz.png"), dpi=150)
    plt.close()


def plot_violin_distribution(
    errors_by_N: dict,
    out_dir: str,
) -> None:
    """Fig 3: violin per N, 90th pct threshold line."""
    Ns = sorted(errors_by_N.keys())
    import pandas as pd
    records = []
    for N in Ns:
        for e in errors_by_N[N]:
            records.append({"N": str(N), "error": e})
    df = pd.DataFrame(records)

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.violinplot(data=df, x="N", y="error", palette="Blues", ax=ax)
    ax.axhline(0.3, color="#F44336", linestyle="--", label="Threshold 0.3")
    ax.set_xlabel("Sequence Length N")
    ax.set_ylabel("Frobenius Error")
    ax.set_title("Error Distribution per Sequence Length")
    ax.legend()
    plt.tight_layout()
    plt.savefig(str(Path(out_dir) / "fig3_violin_distribution.png"), dpi=150)
    plt.close()


def plot_layer_heatmap(
    layer_errors_8k: list,
    out_dir: str,
) -> None:
    """Fig 4: per-layer mean Frobenius error at N=8k."""
    fig, ax = plt.subplots(figsize=(10, 4))
    layer_indices = list(range(len(layer_errors_8k)))
    ax.bar(layer_indices, layer_errors_8k, color=plt.cm.viridis(
        np.array(layer_errors_8k) / max(layer_errors_8k + [1e-9])
    ))
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Mean Frobenius Error")
    ax.set_title("Per-Layer Frobenius Error at N=8192")
    plt.tight_layout()
    plt.savefig(str(Path(out_dir) / "fig4_layer_heatmap.png"), dpi=150)
    plt.close()
