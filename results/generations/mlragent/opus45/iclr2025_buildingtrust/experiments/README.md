# Confidence-Calibrated Dynamic Guardrails (CCDG) Experiment

## Overview

This repository contains the experimental implementation of **Confidence-Calibrated Dynamic Guardrails (CCDG)**, a framework that bridges uncertainty quantification research with practical guardrail deployment for Large Language Models.

## Research Hypothesis

CCDG proposes that modulating guardrail sensitivity based on real-time uncertainty estimation can:
1. Reduce harmful hallucinations by 30-40% compared to static guardrails
2. Improve user satisfaction by 20-25% through reduced over-blocking
3. Achieve Expected Calibration Error (ECE) below 0.05

## Framework Components

1. **Uncertainty Quantification Module (UQM)**: Estimates confidence from LLM hidden states
2. **Dynamic Threshold Controller (DTC)**: Maps uncertainty to guardrail zones (GREEN, YELLOW, ORANGE, RED)
3. **Graduated Response System (GRS)**: Executes zone-specific safety interventions

## Baselines

- **Static Guardrail**: Fixed-threshold content filtering
- **Uncertainty-Only**: Direct uncertainty thresholding without graduated responses
- **CCDG (Proposed)**: Full framework with calibrated thresholds and graduated responses

## Requirements

```bash
pip install torch transformers datasets scikit-learn matplotlib seaborn pandas tqdm
```

## Running the Experiment

```bash
cd claude_code
python run_experiment.py
```

## Output Files

- `log.txt`: Experiment execution log
- `results.json`: Detailed results in JSON format
- `results.csv`: Summary results in CSV format
- `training_curves.png`: Training and validation loss curves
- `method_comparison.png`: Performance comparison across methods
- `zone_distribution.png`: CCDG zone distribution
- `uncertainty_distribution.png`: Uncertainty scores by correctness
- `calibration_curve.png`: Calibration reliability diagram
- `safety_utility_tradeoff.png`: Safety vs utility tradeoff plot

## Evaluation Metrics

### Safety Metrics
- Harmful Output Rate (HOR)
- Hallucination Rate (HR)

### Utility Metrics
- Safe Content Blocking Rate (SCBR)
- Task Completion Rate (TCR)

### Calibration Metrics
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)

## Dataset

The experiment uses the TruthfulQA dataset for evaluating hallucination prevention under uncertainty.

## Citation

```bibtex
@article{ccdg2025,
  title={Uncertainty-Aware Guardrails: Dynamic Safety Boundaries Based on Model Confidence Calibration},
  year={2025}
}
```
