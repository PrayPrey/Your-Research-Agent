# Dynamic Benchmark Renewal Framework (DBRF)

This code implements the experimental validation of the Dynamic Benchmark Renewal Framework (DBRF), which combats benchmark overfitting through continuous dataset renewal.

## Research Hypothesis

The DBRF effectively reduces benchmark overfitting while maintaining distributional fidelity and longitudinal comparability across benchmark versions, outperforming static and unstructured renewal baselines.

## Framework Components

1. **Contamination Detection Module** (`contamination_detection.py`): Statistically detects benchmark saturation using logistic growth curve fitting and Mann-Kendall trend test on the divergence between benchmark and shadow set performance.

2. **Dataset Evolution Protocol** (`dataset_evolution.py`): Generates new benchmark versions satisfying distributional fidelity (KL divergence < ε) and difficulty calibration (IRT-based matching).

3. **Cross-Version Performance Anchoring** (`performance_anchoring.py`): Maintains a held-out anchor set to calibrate scores across benchmark versions, enabling longitudinal comparisons.

## Running the Experiment

```bash
cd tasks_youra_result_sonnet46/iclr2025_mldpr/claude_code
python run_experiment.py
```

The script automatically:
1. Creates benchmark datasets for three domains (image classification, NLP, tabular)
2. Simulates model performance trajectories with controlled overfitting
3. Runs all three DBRF components
4. Evaluates three baseline methods (static, random renewal, adversarial)
5. Generates figures and saves results

## Output

Results are saved to `../results/`:
- `results.json`: Full results in JSON format
- `log.txt`: Experiment execution log
- `performance_trajectories.png`: Benchmark vs shadow performance over generations
- `overfitting_reduction_comparison.png`: DBRF vs baselines on overfitting reduction
- `kl_divergence.png`: Distributional fidelity across renewal cycles
- `detection_metrics.png`: Contamination detection precision/recall/F1
- `anchoring_metrics.png`: Cross-version calibration error and rank correlation
- `summary_comparison.png`: Comprehensive method comparison
- `results.md`: Summary report with tables and discussion

## Requirements

- Python 3.8+
- NumPy, SciPy, Matplotlib, scikit-learn, torch
