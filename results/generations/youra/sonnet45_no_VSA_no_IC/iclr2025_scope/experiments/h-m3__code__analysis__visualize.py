"""Visualization and validation report generation."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_bar_chart(results: dict, output_path: str):
    """Bar chart: simple vs complex mean concentration."""
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Simple', 'Complex']
    means = [results['simple_mean'], results['complex_mean']]
    errors = [
        results['ci_95_simple'][1] - results['simple_mean'],
        results['ci_95_complex'][1] - results['complex_mean']
    ]

    ax.bar(categories, means, yerr=errors, capsize=5, alpha=0.7)
    ax.set_ylabel('Query-Token Attention Concentration')
    ax.set_title(f"H-M3: Simple > Complex (p={results['p_value']:.3f})")
    ax.set_ylim(0, max(means) * 1.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_distributions(dataset: pd.DataFrame, output_path: str):
    """Histogram overlay: simple vs complex distributions."""
    fig, ax = plt.subplots(figsize=(8, 4))
    simple = dataset[dataset['complexity'] == 'simple']['concentration']
    complex_data = dataset[dataset['complexity'] == 'complex']['concentration']

    ax.hist(simple, bins=30, alpha=0.5, label='Simple', color='blue')
    ax.hist(complex_data, bins=30, alpha=0.5, label='Complex', color='red')
    ax.legend()
    ax.set_xlabel('Attention Concentration')
    ax.set_ylabel('Count')
    ax.set_title('Attention Concentration Distributions')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_scatter(dataset: pd.DataFrame, output_path: str):
    """Entity density (x) vs concentration (y), color by word count."""
    fig, ax = plt.subplots(figsize=(8, 6))
    dataset['word_count'] = dataset['question'].apply(lambda q: len(q.split()))

    scatter = ax.scatter(
        dataset['entity_density'],
        dataset['concentration'],
        c=dataset['word_count'],
        alpha=0.6,
        cmap='viridis',
        s=50
    )
    plt.colorbar(scatter, label='Word Count')
    ax.set_xlabel('Entity Density')
    ax.set_ylabel('Attention Concentration')
    ax.set_title('Entity Density vs Attention Concentration')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_boxplots(dataset: pd.DataFrame, output_path: str):
    """Boxplot comparison of simple vs complex concentrations."""
    fig, ax = plt.subplots(figsize=(6, 6))
    data_for_plot = [
        dataset[dataset['complexity'] == 'simple']['concentration'].values,
        dataset[dataset['complexity'] == 'complex']['concentration'].values
    ]

    bp = ax.boxplot(data_for_plot)
    ax.set_xticklabels(['Simple', 'Complex'])
    ax.set_ylabel('Query-Token Attention Concentration')
    ax.set_title('Concentration Distribution Comparison')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def gate_decision(results: dict) -> tuple:
    """SHOULD_WORK gate: p < 0.05 AND simple > complex.

    Returns: (status, explanation)
    """
    if results['p_value'] < 0.05 and results['delta'] > 0:
        status = "PASS"
        explanation = f"Statistical significance achieved (p={results['p_value']:.4f}), simple > complex by {results['delta']:.3f}"
    else:
        status = "FAIL"
        explanation = f"No significance (p={results['p_value']:.4f}) or wrong direction (Δ={results['delta']:.3f})"

    return status, explanation


def write_validation_report(dataset: pd.DataFrame, results: dict, figures_dir: str, output_path: str):
    """Write 04_validation.md."""
    status, explanation = gate_decision(results)

    report = f"""# Validation Report: H-M3 Query Complexity Attention

**Hypothesis**: Simple queries show higher query-token attention concentration than complex queries.
**Date**: 2026-08-20

## Gate Decision

**Result**: {status}

{explanation}

## Results

| Metric | Simple | Complex | Difference |
|--------|--------|---------|------------|
| Mean Concentration | {results['simple_mean']:.3f} | {results['complex_mean']:.3f} | {results['delta']:.3f} |
| 95% CI | [{results['ci_95_simple'][0]:.3f}, {results['ci_95_simple'][1]:.3f}] | [{results['ci_95_complex'][0]:.3f}, {results['ci_95_complex'][1]:.3f}] | - |
| t-statistic | {results['t_statistic']:.3f} | - | - |
| p-value | {results['p_value']:.4f} | - | - |
| Cohen's d | {results['cohen_d']:.3f} | - | - |

## Sample Sizes

- Simple queries: {results['n_simple']}
- Complex queries: {results['n_complex']}

## Figures

### Bar Chart
![Bar Chart]({figures_dir}/bar_chart.png)

### Distributions
![Distributions]({figures_dir}/distributions.png)

### Scatter Plot
![Scatter]({figures_dir}/scatter.png)

### Boxplots
![Boxplots]({figures_dir}/boxplots.png)

## Interpretation

{"Hypothesis validated. Adaptive tiering justified based on query complexity." if status == "PASS" else "Hypothesis not validated. Fallback to uniform tiering recommended."}

## Implementation Notes

- Entity classification: spaCy NER en_core_web_sm
- Attention extraction: Llama-2-7B last layer, averaged across heads
- Statistical test: Two-sample t-test with alternative='greater'
- Effect size: Cohen's d = {results['cohen_d']:.3f}

## Next Steps

{"Proceed with adaptive tiering implementation in YouRA cache policy." if status == "PASS" else "Document uniform tiering as fallback. Core eviction mechanisms (H-M1, H-M4) remain valid."}
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✓ Validation report written to {output_path}")
