# Adaptive Alignment through Reciprocal Preference Learning

This repository contains the experimental implementation for testing the hypothesis that reciprocal preference learning enables better alignment with evolving human values compared to static alignment approaches.

## Overview

The experiments evaluate four alignment approaches:
1. **Static Alignment**: Baseline RLHF without temporal modeling
2. **CEVA Basic**: Context-Evolving Value Alignment with temporal modeling
3. **CEVA Full**: CEVA with bidirectional feedback (no meta-learning)
4. **Adaptive Alignment**: Full proposed method with meta-learning

## Project Structure

```
claude_code/
├── config.py              # Configuration and hyperparameters
├── value_evolution.py     # Simulated human preference evolution
├── alignment_models.py    # Model implementations
├── evaluation.py          # Evaluation metrics
├── visualization.py       # Plotting utilities
├── run_experiment.py      # Main experiment script
├── README.md             # This file
├── log.txt               # Experiment logs (generated)
├── results.json          # Numerical results (generated)
└── figures/              # Generated visualizations (created during run)
```

## Requirements

The code requires the following Python packages:
- torch >= 2.0.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- scikit-learn >= 1.0.0
- tqdm >= 4.62.0

Install dependencies:
```bash
pip install torch numpy matplotlib seaborn scikit-learn tqdm
```

## Running the Experiments

To run all experiments:

```bash
cd claude_code
python run_experiment.py
```

The script will:
1. Run experiments across 3 scenarios (gradual drift, rapid shift, value conflict)
2. Train and evaluate 4 models on each scenario
3. Generate visualizations in the `figures/` directory
4. Save numerical results to `results.json`
5. Log all output to `log.txt`

Expected runtime: ~10-20 minutes on CPU, ~5-10 minutes on GPU

## Experimental Design

### Scenarios

1. **Gradual Drift**: Human preferences slowly evolve over time
2. **Rapid Shift**: Sudden preference change at midpoint
3. **Value Conflict**: Periodic conflicting preference updates

### Evaluation Metrics

- **Accuracy**: Prediction accuracy on human actions
- **Alignment Score**: Average confidence on correct actions
- **Stability**: Consistency of predictions over time
- **User Satisfaction**: Combined accuracy and alignment
- **Agency Preservation**: Stability of preference tracking
- **Adaptation Accuracy**: Ratio of second-half to first-half accuracy

### Visualizations Generated

- Human value evolution patterns
- Model-specific tracking curves
- Training loss curves
- Alignment comparison across scenarios
- Aggregate performance metrics
- Radar charts for model comparison
- Scenario-wise metric comparisons

## Key Results

The experiments test the following hypotheses:

1. Temporal modeling (CEVA Basic) improves preference tracking over static alignment
2. Bidirectional feedback (CEVA Full) enhances user satisfaction and agency
3. Meta-learning (Adaptive Alignment) provides superior adaptation across scenarios

Results are saved in:
- `results.json`: Numerical metrics
- `log.txt`: Detailed execution log
- `figures/`: All generated plots

## Configuration

Key parameters can be adjusted in `config.py`:

- `NUM_USERS`: Number of simulated users (default: 50)
- `NUM_TIMESTEPS`: Interaction length (default: 100)
- `NUM_EPOCHS`: Training epochs (default: 50)
- `HIDDEN_DIM`: Model hidden dimension (default: 128)
- `LEARNING_RATE`: Optimizer learning rate (default: 1e-4)

## Output Files

After running experiments:

1. **figures/**: Contains all visualizations
   - `human_value_evolution_*.png`: Human preference patterns
   - `model_value_evolution_*.png`: Model tracking performance
   - `alignment_comparison_*.png`: Cross-model comparisons
   - `aggregate_metrics_comparison.png`: Overall performance
   - `scenario_comparison_*.png`: Metric-specific comparisons
   - `model_metrics_radar.png`: Radar chart comparison

2. **results.json**: Complete numerical results in JSON format

3. **log.txt**: Full experiment log with timestamps

## Interpreting Results

### Good Performance Indicators:
- Accuracy > 0.7 indicates strong preference prediction
- Alignment Score > 0.6 shows confident correct predictions
- Stability > 0.7 demonstrates consistent behavior
- Adaptive Alignment should show highest scores across scenarios

### Expected Improvements:
- CEVA Basic: ~10-15% over Static Alignment
- CEVA Full: ~20-25% over Static Alignment
- Adaptive Alignment: ~30-40% over Static Alignment

## Citation

If you use this code, please cite:

```
Adaptive Alignment through Reciprocal Preference Learning:
A Framework for Dynamic Human-AI Value Co-Evolution
```

## License

MIT License
