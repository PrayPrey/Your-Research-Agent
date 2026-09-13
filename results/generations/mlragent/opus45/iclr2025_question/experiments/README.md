# Semantic Entropy Decomposition (SED) for Hallucination Detection

This repository contains the implementation of the Semantic Entropy Decomposition (SED) method for efficient uncertainty quantification and hallucination detection in Large Language Models (LLMs).

## Overview

The SED framework decomposes uncertainty into:
- **Epistemic Uncertainty**: Model's lack of knowledge (indicates potential hallucinations)
- **Aleatoric Uncertainty**: Inherent ambiguity in the query

Key features:
- Single forward pass with lightweight probe networks (no expensive multi-sampling)
- Trained on intermediate layer representations
- Contrastive learning for uncertainty decomposition

## Requirements

```bash
pip install torch transformers datasets scikit-learn matplotlib numpy tqdm
```

## Project Structure

```
claude_code/
├── config.py           # Configuration settings
├── model.py            # SED model and loss functions
├── data.py             # Dataset loading and processing
├── uncertainty.py      # Uncertainty estimation methods
├── evaluation.py       # Evaluation metrics and plotting
├── run_experiment.py   # Main experiment script
└── README.md           # This file
```

## Running the Experiment

### Basic Usage

```bash
python run_experiment.py --epochs 10 --batch_size 8 --output_dir outputs
```

### Command Line Arguments

- `--epochs`: Number of training epochs (default: 10)
- `--batch_size`: Batch size for training (default: 8)
- `--lr`: Learning rate (default: 0.0001)
- `--device`: Device to use (default: cuda)
- `--output_dir`: Directory to save results (default: outputs)

### Example

```bash
# Full experiment with default settings
python run_experiment.py

# Custom configuration
python run_experiment.py --epochs 20 --batch_size 4 --lr 0.00005 --output_dir results
```

## Model Architecture

### Probe Networks
- Lightweight MLP probes attached to upper transformer layers
- Attention pooling for sequence aggregation
- Separate probes for epistemic and aleatoric uncertainty

### Loss Function
The training objective combines three components:
1. **Reconstruction Loss**: Total uncertainty approximates semantic entropy
2. **Contrastive Loss**: Separates epistemic from aleatoric uncertainty
3. **Consistency Loss**: Both uncertainties are low for confident predictions

## Datasets

The experiment uses:
- **TruthfulQA**: Hallucination-prone queries (epistemic uncertainty)
- **Synthetic Ambiguous Questions**: Inherently ambiguous queries (aleatoric uncertainty)
- **Simple Factual Questions**: Low uncertainty baseline

## Baselines

Compared methods:
1. **Token Entropy**: Average entropy of generated tokens
2. **Verbalized Confidence**: Model's self-reported confidence
3. **Semantic Entropy**: Multi-sample semantic clustering (expensive)

## Output

The experiment produces:
- `training_curves.png`: Training and validation loss curves
- `roc_curves.png`: ROC curves for hallucination detection
- `pr_curves.png`: Precision-Recall curves
- `calibration_curves.png`: Uncertainty calibration plots
- `confusion_matrices.png`: Binary classification performance
- `method_comparison.png`: Bar chart comparing all methods
- `results.json`: Complete experimental results

## Results

After training, the SED method achieves:
- Significant improvement in AUROC for hallucination detection
- Efficient single-pass inference (no multi-sampling required)
- Successful decomposition of epistemic vs aleatoric uncertainty
