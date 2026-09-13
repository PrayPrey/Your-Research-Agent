# H-E1 Experiment: Confidence-Timeout Correlation

**Hypothesis:** Under neural theorem proving with LeanDojo ReProver, if we extract confidence derivatives (std dev of softmax entropy) from the first 15 proof steps, then these derivatives correlate with eventual timeout outcomes (r > 0.3).

**Type:** EXISTENCE (Proof of Concept)  
**Gate:** MUST_WORK (r > 0.3 OR ρ > 0.3)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set GPU (Optional but Recommended)

```bash
# Check available GPUs
nvidia-smi

# Use single GPU with lowest memory usage
export CUDA_VISIBLE_DEVICES=0
```

### 3. Run Experiment

```bash
python run_experiment.py
```

**Estimated Runtime:** ~8-10 hours (100 theorems × 300s timeout + overhead)

---

## Output Files

### Results Directory (`./results/`)

- **results_raw.csv**: Raw experimental data (100 rows)
  - Columns: theorem_id, confidence_derivative, outcome, execution_time, status
- **metrics_summary.json**: Correlation metrics and gate evaluation
  - Pearson r, Spearman ρ, p-values, AUC, gate result
- **experiment_metadata.json**: Full experiment configuration and metadata

### Figures Directory (`./figures/`)

- **gate_metrics.png** (MANDATORY): Bar chart comparing r, ρ vs target (0.3)
- **scatter_plot.png**: Confidence derivative vs outcome
- **distributions.png**: Histograms comparing success vs timeout groups
- **trajectory_examples.png**: Entropy trajectories for example theorems
- **roc_curve.png**: ROC curve for binary classification

---

## Configuration

Edit `config.py` to modify:

- `sample_size`: Number of theorems to test (default: 100)
- `timeout_seconds`: Timeout per theorem (default: 300s)
- `confidence_window`: Number of proof steps to monitor (default: 15)
- `random_seed`: For reproducibility (default: 42)
- `target_correlation`: Gate threshold (default: 0.3)

---

## Module Overview

```
code/
├── config.py                          # Hardcoded configuration
├── data/
│   └── loader.py                      # TheoremSampler - LeanDojo data loading
├── models/
│   └── confidence_extractor.py        # ConfidenceTrajectoryExtractor - Entropy calculation
├── experiment/
│   └── runner.py                      # ExtendedTimeoutRunner - Proof search with timeout
├── analysis/
│   └── analyzer.py                    # CorrelationAnalyzer - Pearson/Spearman/AUC
├── visualization/
│   └── visualizer.py                  # ExperimentVisualizer - 5 required figures
└── run_experiment.py                  # Main orchestrator
```

---

## Success Criteria

### Primary (MUST_WORK Gate)
- ✓ Pearson r > 0.3 **OR** Spearman ρ > 0.3
- ✓ p-value < 0.05 for statistical significance

### Secondary
- ✓ All 100 experiments complete (success or timeout)
- ✓ All 5 figures generated
- ✓ Results saved to CSV/JSON

### Failure Conditions
- r ≤ 0.3 **AND** ρ ≤ 0.3 → **STOP** hypothesis chain, reassess approach

---

## Troubleshooting

### LeanDojo Installation Issues
```bash
# If lean-dojo fails to install
pip install --upgrade pip setuptools wheel
pip install lean-dojo --no-cache-dir
```

### GPU Memory Issues
```bash
# Reduce batch size or use CPU
export CUDA_VISIBLE_DEVICES=""
```

### Timeout Too Long
```bash
# For quick testing, edit config.py:
EXPERIMENT_CONFIG["sample_size"] = 10
EXPERIMENT_CONFIG["timeout_seconds"] = 30
```

---

## References

- **LeanDojo Paper:** Yang et al., 2023 - https://arxiv.org/abs/2306.15626
- **LeanDojo Repository:** https://github.com/lean-dojo/LeanDojo
- **Experiment Brief:** h-e1/02c_experiment_brief.md
- **Architecture:** h-e1/03_architecture.md

---

*Generated for Phase 4 Implementation | Next: Run Experiment*
