# CARE: Calibrated Adaptive Rejection with Explanations

## Overview
This experiment implements and evaluates the CARE framework for LLM safety guardrails, combining:
1. **UQM** (Uncertainty Quantification Module): Conformal prediction for calibrated safety decisions
2. **EGM** (Explanation Generation Module): Natural language rationale generation for rejections
3. **DAPL** (Domain-Adaptive Policy Layer): Context-aware threshold adjustment

## Requirements
- Python 3.8+
- PyTorch (with CUDA for GPU acceleration)
- transformers, datasets, scikit-learn, matplotlib, anthropic

## Setup
```bash
pip install torch transformers datasets scikit-learn matplotlib anthropic
export ANTHROPIC_API_KEY="your-key"
```

## Running the Experiment
```bash
cd claude_code
python run_experiment.py
```

Outputs are saved to `outputs/` (figures and logs). After completion, results are moved to `../results/`.

## Structure
- `config.py`: Hyperparameters and settings
- `data_processing.py`: ToxiGen data loading and preprocessing
- `safety_classifier.py`: CARE base classifier + conformal prediction
- `baselines.py`: Baseline safety classifiers
- `explanation_generator.py`: Risk category classifier and LLM explanation generation
- `domain_adaptation.py`: Domain-adaptive policy layer
- `visualization.py`: Plotting functions
- `run_experiment.py`: Main experiment runner
