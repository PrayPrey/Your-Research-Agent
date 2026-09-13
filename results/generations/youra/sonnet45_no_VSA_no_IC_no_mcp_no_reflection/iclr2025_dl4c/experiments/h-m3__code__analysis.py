"""Statistical analysis and visualization for h-m3."""
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random


def compute_slopes(results):
    slopes = {}

    for key in ["agent", "random", "revealed_only"]:
        if key not in results:
            continue

        all_points = []
        for pid, values in results[key].items():
            for i, val in enumerate(values):
                all_points.append((i, val))

        if not all_points:
            slopes[f"{key}_slope"] = 0.0
            continue

        x = np.array([p[0] for p in all_points])
        y = np.array([p[1] for p in all_points])

        if len(x) < 2:
            slopes[f"{key}_slope"] = 0.0
            continue

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        slopes[f"{key}_slope"] = slope
        slopes[f"{key}_r_squared"] = r_value ** 2

    return slopes


def permutation_test(agent_results, random_results, n_samples=1000):
    agent_points = []
    for pid, values in agent_results.items():
        for i, val in enumerate(values):
            agent_points.append((i, val))

    random_points = []
    for pid, values in random_results.items():
        for i, val in enumerate(values):
            random_points.append((i, val))

    def get_slope(points):
        if len(points) < 2:
            return 0.0
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        slope, _, _, _, _ = stats.linregress(x, y)
        return slope

    observed_agent = get_slope(agent_points)
    observed_random = get_slope(random_points)
    observed_diff = observed_agent - observed_random

    all_points = agent_points + random_points
    n_agent = len(agent_points)

    null_diffs = []
    for _ in range(n_samples):
        shuffled = all_points[:]
        random.shuffle(shuffled)

        agent_null = shuffled[:n_agent]
        random_null = shuffled[n_agent:]

        agent_slope_null = get_slope(agent_null)
        random_slope_null = get_slope(random_null)

        null_diffs.append(agent_slope_null - random_slope_null)

    p_value = sum(1 for d in null_diffs if d >= observed_diff) / len(null_diffs)

    return p_value


def transfer_efficiency(revealed_slope, held_out_slope):
    if revealed_slope == 0:
        return 0.0
    return held_out_slope / revealed_slope


def plot_held_out_curves(agent_results, baseline_results, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))

    for key, color, label in [("agent", "blue", "Agent (Pattern Memory)"),
                               ("random", "gray", "Random Baseline"),
                               ("revealed_only", "orange", "Revealed-Only Baseline")]:
        if key not in baseline_results and key != "agent":
            continue

        results = agent_results if key == "agent" else baseline_results[key]

        iterations = []
        pass_rates = []

        for pid, values in results.items():
            for i, val in enumerate(values):
                iterations.append(i)
                pass_rates.append(val * 100)

        if not iterations:
            continue

        iteration_bins = {}
        for it, pr in zip(iterations, pass_rates):
            if it not in iteration_bins:
                iteration_bins[it] = []
            iteration_bins[it].append(pr)

        x = sorted(iteration_bins.keys())
        y = [np.mean(iteration_bins[i]) for i in x]

        ax.plot(x, y, marker='o', color=color, label=label, linewidth=2)

    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Held-Out Test Pass Rate (%)", fontsize=12)
    ax.set_title("Transfer Learning to Held-Out Tests", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_pattern_usage(usage_log, output_path):
    if not usage_log:
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    total = len(usage_log)
    used = sum(1 for x in usage_log if x["used"])
    usage_rate = (used / total * 100) if total > 0 else 0

    ax.bar(["Pattern Usage Rate"], [usage_rate], color="steelblue")
    ax.set_ylabel("Usage Rate (%)", fontsize=12)
    ax.set_title("Pattern Memory Usage", fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_validation_report(analysis):
    slope_ratio = analysis["slope_ratio"]
    p_value = analysis["p_value"]
    transfer_eff = analysis["transfer_efficiency"]
    pattern_usage = analysis["pattern_usage_rate"]

    gate_pass = slope_ratio > 1.5 and p_value < 0.05 and transfer_eff > 0.5

    report = f"""# Validation Report - h-m3

## Hypothesis
Under revealed test failures (50%), if agents learn patterns, then held-out test pass slope > 1.5× baseline because pattern transfer works without error messages.

## Primary Metric: Slope Ratio

- **Agent Slope:** {analysis['agent_slope']:.4f}
- **Random Slope:** {analysis['random_slope']:.4f}
- **Slope Ratio:** {slope_ratio:.2f}
- **Target:** > 1.5

**Result:** {'✓ PASS' if slope_ratio > 1.5 else '✗ FAIL'}

## Statistical Significance

- **Permutation Test p-value:** {p_value:.4f}
- **Significance Level:** 0.05
- **Result:** {'✓ PASS' if p_value < 0.05 else '✗ FAIL'}

## Secondary Metrics

### Transfer Efficiency
- **Held-Out Slope / Revealed Slope:** {transfer_eff:.2f}
- **Target:** > 0.5
- **Result:** {'✓ PASS' if transfer_eff > 0.5 else '✗ FAIL'}

### Pattern Usage Rate
- **Usage Rate:** {pattern_usage * 100:.1f}%
- **Target:** > 60%
- **Result:** {'✓ PASS' if pattern_usage > 0.6 else '✗ FAIL'}

## Control Check

- **Revealed-Only Baseline Held-Out Slope:** {analysis.get('revealed_only_slope', 0.0):.4f}
- **Expected:** ≈ 0 (no transfer without memory)
- **Result:** {'✓ PASS' if abs(analysis.get('revealed_only_slope', 0.0)) < 0.01 else '✗ FAIL (unexpected transfer)'}

## Gate Decision (MUST_WORK)

**Overall Result:** {'PASS' if gate_pass else 'FAIL'}

"""

    if gate_pass:
        report += """
### Interpretation
Agent demonstrates statistically significant transfer learning to held-out tests via pattern memory. Slope ratio exceeds threshold, permutation test confirms significance, and transfer efficiency validates genuine pattern generalization.

**Hypothesis h-m3: VALIDATED**
"""
    else:
        report += """
### Interpretation
Agent fails to demonstrate sufficient transfer learning. Possible causes:
- Pattern extraction ineffective
- Insufficient pattern similarity matching
- Held-out tests too dissimilar from revealed tests
- Baseline stronger than expected

**Hypothesis h-m3: FAILED (requires PIVOT to Phase 2A)**
"""

    report += f"""
## Plots

![Held-Out Test Pass Rate Curves](results/plots/held_out_curves.png)

![Pattern Usage](results/plots/pattern_usage.png)

## Raw Data

```json
{analysis}
```

---

**Report Generated:** {analysis.get('timestamp', 'N/A')}
"""

    return report
