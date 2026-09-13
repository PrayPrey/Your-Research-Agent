#!/usr/bin/env python3
"""h-e2: AI response diversity correlates with query diversity."""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from datasets import load_dataset, Dataset
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


# --- Dataset Loading ---

def load_hh_rlhf() -> Dataset:
    """Load HH-RLHF. Returns: Dataset with 'chosen' field."""
    print("Loading HH-RLHF dataset...")
    dataset = load_dataset("Anthropic/hh-rlhf")
    # Concatenate train and test
    from datasets import concatenate_datasets
    combined = concatenate_datasets([dataset["train"], dataset["test"]])
    print(f"Loaded {len(combined)} conversations")
    return combined


# --- Conversation Parsing ---

def parse_conversation(text: str) -> Dict[str, List[str]]:
    """Parse multi-turn conversation. Returns: {'user': [...], 'assistant': [...]}."""
    turns = text.split("\n\n")
    user_turns = [t.replace("Human:", "").strip() for t in turns if "Human:" in t]
    ai_turns = [t.replace("Assistant:", "").strip() for t in turns if "Assistant:" in t]
    return {"user": user_turns, "assistant": ai_turns}


def extract_conversations(dataset: Dataset) -> List[Dict[str, List[str]]]:
    """Parse all conversations. Returns: list of parsed conversations."""
    print("Parsing conversations...")
    conversations = [parse_conversation(ex["chosen"]) for ex in dataset]
    # Filter: minimum 1 user turn and 1 AI turn
    valid = [c for c in conversations if len(c["user"]) >= 1 and len(c["assistant"]) >= 1]
    print(f"Valid conversations: {len(valid)}/{len(conversations)}")
    return valid


# --- Distinct-1 Metric ---

def distinct_1(texts: List[str]) -> float:
    """Compute distinct-1. texts: list of strings. Returns: unique unigrams / total unigrams."""
    all_tokens = []
    for text in texts:
        tokens = text.lower().split()
        all_tokens.extend(tokens)
    if len(all_tokens) == 0:
        return 0.0
    return len(set(all_tokens)) / len(all_tokens)


# --- Metric Computation ---

def compute_diversity_pairs(conversations: List[Dict[str, List[str]]]) -> Tuple[List[float], List[float]]:
    """Compute diversity for all conversations. Returns: (query_divs, response_divs)."""
    print("Computing diversity metrics...")
    query_divs = []
    response_divs = []
    for conv in conversations:
        qd = distinct_1(conv["user"])
        rd = distinct_1(conv["assistant"])
        query_divs.append(qd)
        response_divs.append(rd)
    print(f"Computed diversity for {len(query_divs)} conversations")
    return (query_divs, response_divs)


# --- Statistical Analysis ---

def compute_correlation(query_divs: List[float], response_divs: List[float]) -> Tuple[float, float, Tuple[float, float]]:
    """Compute Pearson correlation. Returns: (r, p_value, ci_95)."""
    r, p = pearsonr(query_divs, response_divs)
    n = len(query_divs)
    # Fisher z-transform for CI
    z = 0.5 * np.log((1 + r) / (1 - r))
    se_z = 1 / np.sqrt(n - 3)
    ci_z = (z - 1.96 * se_z, z + 1.96 * se_z)
    ci_r = (np.tanh(ci_z[0]), np.tanh(ci_z[1]))
    return (r, p, ci_r)


# --- Secondary Analyses ---

def stratify_by_length(conversations: List[Dict], query_divs: List[float], response_divs: List[float]) -> Dict[str, Tuple[float, float, int]]:
    """Stratify by conversation length. Returns: {length_bin: (r, p, n)}."""
    bins = {"2-3": [], "4-5": [], "6+": []}
    for i, conv in enumerate(conversations):
        turn_count = len(conv["user"]) + len(conv["assistant"])
        if turn_count <= 3:
            bins["2-3"].append(i)
        elif turn_count <= 5:
            bins["4-5"].append(i)
        else:
            bins["6+"].append(i)

    results = {}
    for bin_name, indices in bins.items():
        if len(indices) < 3:  # Skip bins with < 3 samples
            continue
        qd = [query_divs[i] for i in indices]
        rd = [response_divs[i] for i in indices]
        r, p = pearsonr(qd, rd)
        results[bin_name] = (r, p, len(indices))
    return results


# --- Visualization ---

def plot_gate_metric(target_r: float, observed_r: float, ci: Tuple[float, float], p_value: float, output_path: Path):
    """Mandatory bar chart."""
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(["Target", "Observed"], [target_r, observed_r], color=['gray', 'steelblue'])
    # Error bar for observed
    yerr = [[observed_r - ci[0]], [ci[1] - observed_r]]
    ax.errorbar([1], [observed_r], yerr=yerr, fmt='none', color='black', capsize=5)
    ax.set_ylabel("Pearson r")
    ax.set_title(f"Gate Metric: r > 0.4 (p={p_value:.4f})")
    ax.axhline(y=0.4, color='red', linestyle='--', label='Threshold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved gate metric plot: {output_path}")


def plot_scatter(query_divs: List[float], response_divs: List[float], r: float, p: float, output_path: Path):
    """Scatter plot with regression."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(query_divs, response_divs, alpha=0.3, s=10)
    # Linear fit
    m, b = np.polyfit(query_divs, response_divs, 1)
    x_fit = np.linspace(min(query_divs), max(query_divs), 100)
    ax.plot(x_fit, m * x_fit + b, 'r-', linewidth=2, label=f'Linear fit: y={m:.3f}x+{b:.3f}')
    ax.set_xlabel("Query Diversity (distinct-1)")
    ax.set_ylabel("Response Diversity (distinct-1)")
    ax.set_title(f"Query vs Response Diversity (r={r:.3f}, p={p:.4f})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved scatter plot: {output_path}")


def plot_distributions(query_divs: List[float], response_divs: List[float], output_path: Path):
    """Overlaid histograms."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(query_divs, bins=50, alpha=0.5, label='Query Diversity', color='blue')
    ax.hist(response_divs, bins=50, alpha=0.5, label='Response Diversity', color='orange')
    ax.set_xlabel("Diversity (distinct-1)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Query and Response Diversity")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved distribution plot: {output_path}")


def plot_stratification(results: Dict[str, Tuple[float, float, int]], output_path: Path):
    """Grouped bar chart."""
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = list(results.keys())
    rs = [results[b][0] for b in bins]
    ns = [results[b][2] for b in bins]

    bars = ax.bar(bins, rs, color='steelblue')
    ax.set_ylabel("Pearson r")
    ax.set_xlabel("Conversation Length (turns)")
    ax.set_title("Correlation by Conversation Length")
    ax.axhline(y=0.4, color='red', linestyle='--', label='Threshold')

    # Annotate with n
    for i, (bar, n) in enumerate(zip(bars, ns)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'n={n}', ha='center', va='bottom', fontsize=8)

    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved stratification plot: {output_path}")


# --- Main Pipeline ---

def run_experiment():
    """Run full h-e2 experiment."""
    # Setup paths
    base_path = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_bi_align/experiments/h-e2")
    figures_path = base_path / "figures"
    results_path = base_path / "results"
    figures_path.mkdir(exist_ok=True, parents=True)
    results_path.mkdir(exist_ok=True, parents=True)

    # Load dataset
    dataset = load_hh_rlhf()
    conversations = extract_conversations(dataset)

    # Compute diversity
    query_divs, response_divs = compute_diversity_pairs(conversations)

    # Statistical analysis
    r, p, ci = compute_correlation(query_divs, response_divs)
    success = (r > 0.4) and (p < 0.05)

    print("\n=== PRIMARY RESULTS ===")
    print(f"Pearson r: {r:.4f}")
    print(f"p-value: {p:.4e}")
    print(f"95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
    print(f"Sample size: {len(conversations)} conversations")
    print(f"Gate (r > 0.4 AND p < 0.05): {'PASS' if success else 'FAIL'}")

    # Secondary analyses
    print("\n=== SECONDARY ANALYSES ===")
    length_strat = stratify_by_length(conversations, query_divs, response_divs)
    for bin_name, (r_bin, p_bin, n_bin) in length_strat.items():
        print(f"{bin_name} turns: r={r_bin:.4f}, p={p_bin:.4e}, n={n_bin}")

    # Visualizations
    print("\n=== GENERATING FIGURES ===")
    plot_gate_metric(0.4, r, ci, p, figures_path / "gate_metric.png")
    plot_scatter(query_divs, response_divs, r, p, figures_path / "scatter.png")
    plot_distributions(query_divs, response_divs, figures_path / "distributions.png")
    plot_stratification(length_strat, figures_path / "stratification.png")

    # Save results
    results = {
        "r": float(r),
        "p": float(p),
        "ci_95": [float(ci[0]), float(ci[1])],
        "success": bool(success),
        "n_conversations": len(conversations),
        "gate": "SHOULD_WORK",
        "gate_result": "PASS" if success else "FAIL",
        "stratification": {k: {"r": float(v[0]), "p": float(v[1]), "n": v[2]} for k, v in length_strat.items()}
    }

    results_file = results_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results: {results_file}")

    return results


if __name__ == "__main__":
    results = run_experiment()
    print("\nEXPERIMENT COMPLETE")
