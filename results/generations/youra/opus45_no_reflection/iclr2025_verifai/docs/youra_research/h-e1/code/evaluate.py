"""H-E1 Evaluation Pipeline: AS extraction, metrics, visualization, PoC gate"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List
import numpy as np

from config import CONFIG
from model import ASComponents, extract_all_components

def load_signal_dataset(path: str) -> List[Dict]:
    """Load signal dataset from JSON."""
    with open(path, 'r') as f:
        return json.load(f)

def extract_all_signals(signals: List[Dict]) -> List[Dict]:
    """Apply AS extraction to all signals."""
    results = []
    for sig in signals:
        components = extract_all_components(sig["signal_text"])
        results.append({
            "problem_id": sig["problem_id"],
            "source": sig.get("source", "unknown"),
            "error_type": sig.get("error_type", "unknown"),
            "condition": sig["condition"],
            "signal_text": sig["signal_text"],
            "AS_loc": components.AS_loc,
            "AS_state": components.AS_state,
            "AS_causal": components.AS_causal,
            "is_valid": components.is_valid()
        })
    return results

def compute_extraction_rate(results: List[Dict]) -> Dict[str, float]:
    """Compute extraction rate per component and overall."""
    n = len(results)
    if n == 0:
        return {"AS_loc": 0.0, "AS_state": 0.0, "AS_causal": 0.0, "overall": 0.0}

    # Per-component: fraction where component > 0
    as_loc_rate = sum(1 for r in results if r["AS_loc"] > 0) / n
    as_state_rate = sum(1 for r in results if r["AS_state"] > 0) / n
    as_causal_rate = sum(1 for r in results if r["AS_causal"] > 0) / n

    # Overall: at least one component extracted
    overall_rate = sum(1 for r in results if r["AS_loc"] > 0 or r["AS_state"] > 0 or r["AS_causal"] > 0) / n

    return {
        "AS_loc": as_loc_rate,
        "AS_state": as_state_rate,
        "AS_causal": as_causal_rate,
        "overall": overall_rate
    }

def results_by_condition(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group results by condition."""
    by_cond = {}
    for r in results:
        cond = r["condition"]
        by_cond.setdefault(cond, []).append(r)
    return by_cond

def verify_ordering(by_condition: Dict[str, List[Dict]]) -> bool:
    """Verify AS ordering: mean(C1) > C2 > C3 > C4 for AS_state."""
    means = {}
    for cond in ["C1", "C2", "C3", "C4"]:
        if cond in by_condition:
            values = [r["AS_state"] for r in by_condition[cond]]
            means[cond] = np.mean(values) if values else 0
        else:
            means[cond] = 0

    ordering = means["C1"] >= means["C2"] >= means["C3"] >= means["C4"]
    print(f"AS_state means: C1={means['C1']:.2f}, C2={means['C2']:.2f}, C3={means['C3']:.2f}, C4={means['C4']:.2f}")
    print(f"Ordering C1>=C2>=C3>=C4: {ordering}")
    return ordering

def compute_correlation_matrix(results: List[Dict]) -> np.ndarray:
    """Compute 3x3 Pearson correlation between AS components."""
    as_loc = [r["AS_loc"] for r in results]
    as_state = [r["AS_state"] for r in results]
    as_causal = [r["AS_causal"] for r in results]

    data = np.array([as_loc, as_state, as_causal])

    # Handle edge case of zero variance
    if np.std(data[0]) == 0 or np.std(data[1]) == 0 or np.std(data[2]) == 0:
        return np.eye(3)

    return np.corrcoef(data)

def plot_extraction_rate_bar(rates: Dict[str, float], out_path: str) -> None:
    """Generate extraction rate bar chart."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    components = ["AS_loc", "AS_state", "AS_causal", "overall"]
    values = [rates.get(c, 0) for c in components]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(components, values, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'])
    ax.axhline(y=CONFIG["extraction_rate_target"], color='red', linestyle='--', label=f'Target ({CONFIG["extraction_rate_target"]*100:.0f}%)')

    ax.set_ylabel('Extraction Rate')
    ax.set_title('AS Component Extraction Rates')
    ax.set_ylim(0, 1.1)
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val*100:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_component_boxplots(by_condition: Dict[str, List[Dict]], out_path: str) -> None:
    """Generate AS component boxplots by condition."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    conditions = ["C1", "C2", "C3", "C4", "C5", "C6"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, component in enumerate(["AS_loc", "AS_state", "AS_causal"]):
        data = []
        labels = []
        for cond in conditions:
            if cond in by_condition:
                values = [r[component] for r in by_condition[cond]]
                data.append(values)
                labels.append(cond)

        axes[idx].boxplot(data, labels=labels)
        axes[idx].set_title(f'{component} by Condition')
        axes[idx].set_xlabel('Condition')
        axes[idx].set_ylabel(component)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_extraction_heatmap(by_condition: Dict[str, List[Dict]], out_path: str) -> None:
    """Generate extraction success heatmap (components x conditions)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    conditions = ["C1", "C2", "C3", "C4", "C5", "C6"]
    components = ["AS_loc", "AS_state", "AS_causal"]

    matrix = np.zeros((len(components), len(conditions)))

    for j, cond in enumerate(conditions):
        if cond in by_condition:
            results = by_condition[cond]
            n = len(results)
            if n > 0:
                matrix[0, j] = sum(1 for r in results if r["AS_loc"] > 0) / n
                matrix[1, j] = sum(1 for r in results if r["AS_state"] > 0) / n
                matrix[2, j] = sum(1 for r in results if r["AS_causal"] > 0) / n

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(matrix, cmap='YlGn', aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions)
    ax.set_yticks(range(len(components)))
    ax.set_yticklabels(components)

    for i in range(len(components)):
        for j in range(len(conditions)):
            ax.text(j, i, f'{matrix[i,j]*100:.0f}%', ha='center', va='center')

    ax.set_title('Extraction Success Rate (Components x Conditions)')
    plt.colorbar(im, ax=ax, label='Rate')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_correlation_matrix(corr: np.ndarray, out_path: str) -> None:
    """Generate correlation matrix heatmap."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    labels = ["AS_loc", "AS_state", "AS_causal"]

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)

    ax.set_xticks(range(3))
    ax.set_xticklabels(labels)
    ax.set_yticks(range(3))
    ax.set_yticklabels(labels)

    for i in range(3):
        for j in range(3):
            ax.text(j, i, f'{corr[i,j]:.2f}', ha='center', va='center')

    ax.set_title('AS Component Correlation Matrix')
    plt.colorbar(im, ax=ax, label='Pearson r')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def export_results_csv(results: List[Dict], out_path: str) -> None:
    """Export results to CSV."""
    fieldnames = ["problem_id", "source", "error_type", "condition",
                  "AS_loc", "AS_state", "AS_causal", "is_valid"]

    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in fieldnames})

    print(f"Saved: {out_path}")

def check_poc_gate(rates: Dict[str, float], ordering_ok: bool) -> bool:
    """Check PoC pass condition."""
    target = CONFIG["extraction_rate_target"]

    # Primary: overall extraction rate >= 95%
    rate_pass = rates["overall"] >= target

    print("\n" + "="*60)
    print("POC GATE CHECK")
    print("="*60)
    print(f"Extraction rate: {rates['overall']*100:.1f}% (target: {target*100:.0f}%)")
    print(f"Rate pass: {rate_pass}")
    print(f"Ordering pass: {ordering_ok}")

    gate_pass = rate_pass and ordering_ok

    if gate_pass:
        print("\n*** POC GATE: PASS ***")
    else:
        print("\n*** POC GATE: FAIL ***")
        if not rate_pass:
            print(f"  - Extraction rate {rates['overall']*100:.1f}% below target {target*100:.0f}%")
        if not ordering_ok:
            print("  - AS ordering not satisfied (C1>=C2>=C3>=C4)")

    print("="*60 + "\n")
    return gate_pass

def main():
    """Main evaluation pipeline."""
    code_dir = Path(__file__).parent
    output_dir = code_dir / CONFIG["output_dir"]
    figures_dir = code_dir / CONFIG["figures_dir"]

    output_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    # Load signal dataset
    signal_path = output_dir / "signal_dataset.json"
    if not signal_path.exists():
        print(f"Signal dataset not found at {signal_path}")
        print("Running train.py first...")
        import train
        train.main()

    signals = load_signal_dataset(signal_path)
    print(f"Loaded {len(signals)} signals")

    # Extract AS components
    print("Extracting AS components...")
    results = extract_all_signals(signals)

    # Compute metrics
    rates = compute_extraction_rate(results)
    print(f"\nExtraction rates:")
    for k, v in rates.items():
        print(f"  {k}: {v*100:.1f}%")

    # Group by condition
    by_cond = results_by_condition(results)

    # Verify ordering
    ordering_ok = verify_ordering(by_cond)

    # Correlation matrix
    corr = compute_correlation_matrix(results)
    print(f"\nCorrelation matrix:\n{corr}")

    # Generate figures
    print("\nGenerating figures...")
    plot_extraction_rate_bar(rates, str(figures_dir / "extraction_rate_bar.png"))
    plot_component_boxplots(by_cond, str(figures_dir / "component_boxplots.png"))
    plot_extraction_heatmap(by_cond, str(figures_dir / "extraction_heatmap.png"))
    plot_correlation_matrix(corr, str(figures_dir / "correlation_matrix.png"))

    # Export CSV
    export_results_csv(results, str(output_dir / "results.csv"))

    # PoC gate check
    gate_pass = check_poc_gate(rates, ordering_ok)

    # Save experiment results JSON
    experiment_results = {
        "hypothesis_id": "h-e1",
        "total_signals": len(signals),
        "extraction_rates": {k: float(v) for k, v in rates.items()},
        "ordering_satisfied": bool(ordering_ok),
        "correlation_matrix": corr.tolist(),
        "gate_result": "PASS" if gate_pass else "FAIL",
        "gate_details": {
            "rate_threshold": float(CONFIG["extraction_rate_target"]),
            "rate_achieved": float(rates["overall"]),
            "ordering_required": True,
            "ordering_achieved": bool(ordering_ok)
        }
    }

    results_json_path = code_dir.parent / "experiment_results.json"
    with open(results_json_path, 'w') as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Saved: {results_json_path}")

    return gate_pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
