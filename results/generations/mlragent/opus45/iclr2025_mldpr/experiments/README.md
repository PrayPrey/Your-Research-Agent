# Dynamic Dataset Health Scores (DDHS) Experiment

This repository contains the implementation and experimental evaluation of the Dynamic Dataset Health Scores (DDHS) system for automated monitoring of ML dataset health in repositories.

## Overview

DDHS is a comprehensive automated monitoring system that continuously assesses dataset health across multiple dimensions:

1. **Usage Saturation Index (USI)**: Tracks citation/download patterns to identify benchmark overuse
2. **Freshness Score (FS)**: Assesses temporal drift and dataset currency
3. **Documentation Completeness Score (DCS)**: Evaluates documentation coverage
4. **Community Responsiveness Index (CRI)**: Measures maintainer engagement
5. **Ethical Alert System (EAS)**: Detects potential ethical concerns

## Project Structure

```
claude_code/
├── config.py              # Configuration settings
├── data_generator.py      # Synthetic dataset generator
├── health_scores.py       # DDHS health score modules
├── baselines.py           # Baseline methods for comparison
├── evaluation.py          # Evaluation metrics
├── visualization.py       # Plotting utilities
├── run_experiment.py      # Main experiment runner
└── README.md              # This file
```

## Requirements

- Python 3.8+
- NumPy
- Pandas
- Scikit-learn
- Matplotlib
- Seaborn
- SciPy

Install dependencies:
```bash
pip install numpy pandas scikit-learn matplotlib seaborn scipy
```

## Running the Experiment

To run the full experiment with default settings:

```bash
python run_experiment.py
```

### Command Line Options

- `--num-datasets`: Number of synthetic datasets to generate (default: 200)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output-dir`: Output directory for results (default: outputs)

Example:
```bash
python run_experiment.py --num-datasets 500 --seed 123 --output-dir my_results
```

## Experiment Details

### Synthetic Data Generation

The experiment uses synthetic dataset metadata that simulates realistic patterns observed in ML repositories:
- Multiple domains (CV, NLP, tabular, etc.)
- Various task types
- Realistic usage and citation patterns
- Documentation quality variation
- Maintainer responsiveness levels
- Ethical concerns (bias, privacy issues)

### Baseline Methods

DDHS is compared against five baseline approaches:
1. **Downloads-Only**: Uses only download counts to rank datasets
2. **Static-Weighted**: Fixed equal weights for all features
3. **Data-Shapley**: Simplified Shapley value-inspired approach
4. **Recency-Only**: Only considers dataset freshness
5. **Documentation-Only**: Only considers documentation completeness

### Evaluation Metrics

1. **Deprecation Prediction**:
   - AUC-ROC: Area under the ROC curve
   - Average Precision: Area under the precision-recall curve
   - F1 at optimal threshold
   - Precision/Recall at top 10%

2. **User Alignment** (with expert scores):
   - Kendall's τ (tau) correlation
   - Spearman's ρ (rho) correlation
   - Pearson's r correlation
   - MAE and RMSE

3. **Computational Efficiency**:
   - Total computation time
   - Time per dataset
   - Scalability across repository sizes

## Output Files

After running, results are saved in the output directory:

- `results.json`: Complete results in JSON format
- `deprecation_results.csv`: Deprecation prediction metrics
- `alignment_results.csv`: User alignment metrics
- `efficiency_results.csv`: Computational efficiency metrics
- `scalability_results.csv`: Scalability benchmark results
- `log.txt`: Experiment execution log
- `figures/`: Directory containing all generated plots

## Generated Figures

The experiment generates the following visualizations:
- Deprecation prediction comparison
- User alignment comparison
- Efficiency comparison
- Score distributions
- Score vs expert correlation plots
- Scalability benchmarks
- Deprecation rate by score bin
- Comprehensive summary

## Citation

If you use this code, please cite:

```bibtex
@article{ddhs2025,
  title={Dynamic Dataset Health Scores: Automated Monitoring for ML Repository Sustainability},
  author={...},
  journal={...},
  year={2025}
}
```

## License

MIT License
