# Adaptive Confidence Calibration for Trustworthy LLM Responses

This project implements and evaluates a novel framework for calibrating confidence scores in Large Language Models (LLMs) using multi-model disagreement patterns.

## Overview

The framework addresses the critical problem of LLM overconfidence by:
1. Querying multiple diverse LLMs for each input
2. Analyzing disagreement patterns using semantic similarity
3. Training a calibration network to map disagreement to confidence scores
4. Providing interpretable uncertainty estimates

## Project Structure

```
claude_code/
├── config.py                      # Configuration settings
├── data_processing.py             # Dataset loading and preprocessing
├── multi_model_query.py           # Multi-model query system
├── disagreement_analysis.py       # Disagreement metrics computation
├── confidence_calibration.py      # Neural calibration network
├── evaluation.py                  # Evaluation metrics
├── baselines.py                   # Baseline methods
├── visualization.py               # Plotting functions
├── run_experiment.py              # Main experiment script
└── README.md                      # This file
```

## Requirements

### Python Packages

```bash
pip install torch numpy matplotlib seaborn scikit-learn
pip install sentence-transformers datasets
pip install openai anthropic
```

### API Keys

The experiment requires API keys for:
- OpenAI (for GPT models)
- Anthropic (for Claude models)

These should be set as environment variables:
```bash
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

## Running the Experiment

### Quick Start

Simply run:
```bash
python run_experiment.py
```

This will:
1. Load datasets (TriviaQA, CommonsenseQA)
2. Query multiple LLM APIs for each question
3. Analyze response disagreement patterns
4. Train a calibration network
5. Evaluate against baseline methods
6. Generate visualizations and save results

### Configuration

Edit `config.py` to modify:
- Number of samples to process
- Models in the ensemble
- Calibration hyperparameters
- Output directories

### Output

Results are saved to:
- `results/` - Final metrics, tables, and figures
- `log.txt` - Detailed execution log
- `*.json` - Intermediate data and results

## Experiment Pipeline

### Step 1: Data Loading
- Loads TriviaQA and CommonsenseQA datasets
- Splits into train/validation/test sets
- Prepares questions and ground truth answers

### Step 2: Model Querying
- Queries 3 diverse LLMs (GPT-4o-mini, Claude-3.5-Haiku, GPT-3.5-Turbo)
- Generates 2 responses per model per question
- Handles API rate limits with batching and delays

### Step 3: Disagreement Analysis
- Computes semantic embeddings using sentence transformers
- Calculates disagreement metrics:
  - Semantic dispersion (cosine similarity variance)
  - Cluster diversity (multi-cluster distribution)
  - Length variance (response length consistency)
- Computes composite uncertainty score

### Step 4: Ground Truth Labeling
- Extracts consensus answers from model responses
- Compares against ground truth using exact and fuzzy matching
- Creates binary correctness labels

### Step 5: Calibration Training
- Trains neural network to map disagreement features to confidence
- Uses BCE loss + entropy regularization
- Early stopping on validation set
- Saves trained model

### Step 6: Evaluation
- Evaluates proposed method and baselines on test set
- Computes metrics:
  - Expected Calibration Error (ECE)
  - Brier Score
  - AUROC and AUPRC
  - Selective prediction accuracy
- Compares all methods

### Step 7: Visualization
- Generates calibration curves
- Plots method comparisons
- Creates selective prediction curves
- Visualizes confidence distributions

## Baseline Methods

The experiment compares against:

1. **Constant Confidence**: Always predicts 0.5
2. **Majority Voting**: Confidence based on response agreement
3. **Length-Based**: Uses response length consistency
4. **Simple Semantic Similarity**: Based on semantic dispersion only
5. **Uncertainty Estimator**: Uses composite disagreement metrics

## Evaluation Metrics

### Calibration Quality
- **ECE (Expected Calibration Error)**: Measures alignment between confidence and accuracy
- **Brier Score**: Quadratic loss for probability predictions

### Discrimination
- **AUROC**: Area under ROC curve for correctness prediction
- **AUPRC**: Area under precision-recall curve

### Sharpness
- **Average Confidence**: How confident predictions are
- **Confidence Entropy**: Decisiveness of predictions

### Downstream Performance
- **Selective Accuracy**: Accuracy when abstaining on low-confidence predictions

## Results

After running, check:
- `results/metrics.json` - All numerical results
- `results/summary_table.md` - Comparison table
- `results/figures/` - All visualization figures
- `log.txt` - Full execution log

## Notes

- The experiment uses reduced sample sizes (200 samples) and smaller models for efficiency
- API calls may take significant time due to rate limits
- GPU acceleration is used if available (for calibration network training)
- Intermediate results are saved to allow resuming if interrupted

## Citation

If you use this code, please cite:

```
@article{adaptive_confidence_calibration_2025,
  title={Adaptive Confidence Calibration for Trustworthy LLM Responses via Multi-Model Disagreement},
  author={[Authors]},
  journal={[Venue]},
  year={2025}
}
```

## License

This project is provided for research purposes.
