"""Generate Phase 4 validation report for h-m2."""

import json
import os
from datetime import datetime

def generate_validation_report(results_path, output_path):
    """
    Generate 04_validation.md from experiment results.

    Args:
        results_path: Path to experiment_results.json
        output_path: Path to save 04_validation.md
    """
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)

    diversity_test = results['diversity_test']
    agreement_test = results['agreement_test']
    gate_pass = results['gate_pass']
    comparison = results['comparison']

    # Generate report
    report = f"""# Phase 4 Validation Report: h-m2

**Hypothesis:** Error Type Signature Analysis (MECHANISM)
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** {'PASS' if gate_pass else 'FAIL'}

---

## Executive Summary

This experiment compared uncertainty signatures between two error types:
- **NaturalQuestions (Knowledge Gaps):** Questions where the model lacks knowledge
- **TruthfulQA (Confident Misconceptions):** Questions where the model confidently gives wrong answers

**Key Finding:** {'Knowledge gaps show significantly higher semantic diversity than confident misconceptions.' if gate_pass else 'No significant difference in diversity between error types.'}

---

## Experimental Setup

### Datasets
- **NaturalQuestions:** 100 validation samples (knowledge gap errors)
- **TruthfulQA:** 100 validation samples (confident misconception errors)

### Model
- **Architecture:** Mistral-7B-v0.1
- **Sampling:** K=5 answers per question
- **Temperature:** 0.7

### Metrics
1. **Semantic Diversity:** Semantic entropy over answer clusters
2. **Sampling Agreement:** Majority vote agreement rate

---

## Results

### Diversity Comparison (Primary Metric)

| Dataset | Mean Diversity | Std Dev |
|---------|---------------|---------|
| NaturalQuestions (Knowledge Gaps) | {diversity_test['mean1']:.4f} | {diversity_test['std1']:.4f} |
| TruthfulQA (Misconceptions) | {diversity_test['mean2']:.4f} | {diversity_test['std2']:.4f} |

**Statistical Test:**
- t-statistic: {diversity_test['t_statistic']:.4f}
- p-value: {diversity_test['p_value']:.6f}
- Significant (p < 0.05): {'Yes' if diversity_test['p_value'] < 0.05 else 'No'}

### Agreement Comparison (Secondary Metric)

| Dataset | Mean Agreement | Std Dev |
|---------|---------------|---------|
| NaturalQuestions | {agreement_test['mean1']:.4f} | {agreement_test['std1']:.4f} |
| TruthfulQA | {agreement_test['mean2']:.4f} | {agreement_test['std2']:.4f} |

**Statistical Test:**
- t-statistic: {agreement_test['t_statistic']:.4f}
- p-value: {agreement_test['p_value']:.6f}

---

## Gate Evaluation

**Gate Type:** SHOULD_WORK

**Condition:** Knowledge gaps show higher diversity than misconceptions (statistically significant)
- `(p < 0.05) AND (NQ diversity mean > TQA diversity mean)`

**Evaluation:**
- ✓ p-value < 0.05: {diversity_test['p_value'] < 0.05}
- ✓ NQ diversity > TQA diversity: {diversity_test['mean1'] > diversity_test['mean2']}

**Result:** {'PASS ✓' if gate_pass else 'FAIL ✗'}

---

## Visualizations

Generated figures:
1. `gate_metrics_comparison.png` - Bar chart comparing diversity means
2. `diversity_distribution.png` - Box plots of diversity distributions
3. `agreement_distribution.png` - Box plots of agreement distributions
4. `signature_space_2d.png` - 2D scatter plot of error signatures

All figures saved to: `figures/`

---

## Interpretation

### Diversity Findings
{'Knowledge gap errors exhibit significantly more diverse model outputs than confident misconceptions. This supports the hypothesis that different error types have distinct uncertainty signatures.' if gate_pass else 'The diversity difference between error types was not statistically significant or in the expected direction.'}

### Agreement Findings
{'Agreement patterns show ' + ('higher' if agreement_test['mean2'] > agreement_test['mean1'] else 'lower') + f" agreement for misconceptions (mean={agreement_test['mean2']:.4f}) vs knowledge gaps (mean={agreement_test['mean1']:.4f})." if abs(agreement_test['mean2'] - agreement_test['mean1']) > 0.05 else 'Agreement rates are similar across both error types.'}

### Error Type Characterization
- **Knowledge Gaps:** {'High diversity, low agreement - model uncertain and exploring answer space' if diversity_test['mean1'] > diversity_test['mean2'] else 'Moderate diversity'}
- **Confident Misconceptions:** {'Low diversity, high agreement - model confident on wrong answer' if diversity_test['mean2'] < diversity_test['mean1'] and agreement_test['mean2'] > agreement_test['mean1'] else 'Moderate diversity'}

---

## Conclusion

**Hypothesis Status:** {'VALIDATED' if gate_pass else 'NOT VALIDATED'}

{'This experiment successfully demonstrates that error types can be distinguished by their uncertainty signatures. The significant difference in semantic diversity between knowledge gaps and confident misconceptions validates the core mechanism hypothesis.' if gate_pass else 'The hypothesis that error types show distinct uncertainty signatures was not validated at the required significance level.'}

**Next Steps:**
{'- Proceed to h-m3: Method-error matching analysis' if gate_pass else '- Consider alternative error type partitioning methods or larger sample sizes'}

---

## Validation Metadata

**Experiment Duration:** {'N/A - see experiment.log'}
**Code Location:** h-m2/code/
**Results Location:** h-m2/code/results/experiment_results.json
**Figures Location:** h-m2/code/figures/

---

*Generated by Phase 4 Validation*
"""

    # Write report
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Validation report saved to: {output_path}")
    return report


if __name__ == "__main__":
    results_path = "results/experiment_results.json"
    output_path = "../04_validation.md"

    if os.path.exists(results_path):
        generate_validation_report(results_path, output_path)
    else:
        print(f"Results file not found: {results_path}")
        print("Run the experiment first: python main.py")
