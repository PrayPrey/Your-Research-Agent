import matplotlib.pyplot as plt
import numpy as np

def plot_gate_metrics(metrics, output_path, thresholds=None):
    if thresholds is None:
        thresholds = {"extraction_rate": 0.95, "p_value": 0.05, "q3_fraction": 0.05}

    metric_names = ["extraction_rate", "p_value", "q3_fraction"]
    values = [metrics.get(k, 0) for k in metric_names]
    threshold_vals = [thresholds.get(k, 0) for k in metric_names]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(metric_names))
    bars = ax.bar(x, values, alpha=0.7)

    for i, (val, thresh) in enumerate(zip(values, threshold_vals)):
        if (metric_names[i] == "p_value" and val < thresh) or (metric_names[i] != "p_value" and val > thresh):
            bars[i].set_color("green")
        else:
            bars[i].set_color("red")
        ax.axhline(thresh, color="blue", linestyle="--", alpha=0.5, label=f"{metric_names[i]} threshold" if i == 0 else "")

    ax.set_xticks(x)
    ax.set_xticklabels(metric_names)
    ax.set_ylabel("Value")
    ax.set_title("Gate Metrics vs Thresholds")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_scatter(entropies, correctness, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    jittered_correctness = np.array(correctness) + np.random.normal(0, 0.02, len(correctness))

    ax.scatter(entropies, jittered_correctness, alpha=0.5)

    z = np.polyfit(entropies, correctness, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(entropies), max(entropies), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, label="Regression line")

    ax.set_xlabel("Entropy")
    ax.set_ylabel("Correctness (jittered)")
    ax.set_title("Entropy vs Correctness")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_histograms(entropies_correct, entropies_incorrect, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(entropies_correct, bins=30, alpha=0.5, label="Correct", color="green")
    ax.hist(entropies_incorrect, bins=30, alpha=0.5, label="Incorrect", color="red")

    ax.set_xlabel("Entropy")
    ax.set_ylabel("Count")
    ax.set_title("Entropy Distribution by Correctness")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_quadrant(max_probs, entropies, correctness, output_path):
    fig, ax = plt.subplots(figsize=(10, 8))

    median_maxprob = np.median(max_probs)
    median_entropy = np.median(entropies)

    colors = ["red" if c == 0 else "green" for c in correctness]
    ax.scatter(max_probs, entropies, c=colors, alpha=0.5)

    ax.axhline(median_entropy, color="blue", linestyle="--", alpha=0.5)
    ax.axvline(median_maxprob, color="blue", linestyle="--", alpha=0.5)

    q3_mask = (np.array(max_probs) > median_maxprob) & (np.array(entropies) > median_entropy)
    q3_fraction = np.sum(q3_mask) / len(entropies)

    ax.text(0.95, 0.95, f"Q3: {q3_fraction:.2%}", transform=ax.transAxes,
            verticalalignment="top", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    ax.set_xlabel("Max Probability")
    ax.set_ylabel("Entropy")
    ax.set_title("Quadrant Analysis: Max-Prob vs Entropy")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
