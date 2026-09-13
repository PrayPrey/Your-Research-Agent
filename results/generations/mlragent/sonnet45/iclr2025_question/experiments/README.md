# Semantic Consistency Graphs for Hallucination Detection

This repository contains the implementation of the Semantic Consistency Graph (SCG) framework for detecting and quantifying hallucinations in multi-turn LLM conversations.

## Overview

The SCG framework addresses the critical gap in longitudinal hallucination detection by:
- Constructing dynamic graphs representing semantic relationships between claims across conversation history
- Detecting contradictions through graph-based anomaly detection
- Providing interpretable uncertainty scores with fine-grained explanations

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set up API keys (if using OpenAI API):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Project Structure

- `config.py` - Configuration parameters for experiments
- `data.py` - Conversational dataset generation with controlled contradictions
- `model.py` - SCG framework implementation
- `uncertainty.py` - Baseline uncertainty quantification methods
- `evaluation.py` - Evaluation metrics and visualization utilities
- `utils.py` - Helper functions for experiments
- `run_experiment.py` - Main experiment runner script

## Running Experiments

To run the complete experimental pipeline:

```bash
python run_experiment.py
```

This will:
1. Generate or load a synthetic conversational dataset
2. Evaluate the SCG method and baseline approaches
3. Compute performance metrics (Precision, Recall, F1, AUC)
4. Generate comprehensive visualizations
5. Save all results to the `results/` directory

## Dataset

The framework generates synthetic multi-turn conversations with:
- 100 conversations across medical, legal, and technical domains
- 5-15 turns per conversation
- 50% with programmatically injected contradictions
- Controlled temporal distances between contradictions (2-8 turns)

## Models Evaluated

1. **SCG (Proposed)**: Full semantic consistency graph framework with:
   - Atomic claim extraction
   - Hybrid edge weights (semantic similarity + NLI)
   - Graph-based anomaly detection
   - Multi-level uncertainty quantification

2. **Perplexity Baseline**: Semantic coherence-based detection

3. **SelfCheckGPT**: Self-consistency checking approach

4. **Semantic Embedding**: Embedding variance-based uncertainty

## Results

Results are saved in the `results/` directory:
- `metrics.json` - Performance metrics for all models
- `model_comparison.png` - Comprehensive model comparison
- `error_analysis.png` - Error type distribution
- `scg_roc_curve.png` - ROC curve for SCG
- `scg_pr_curve.png` - Precision-Recall curve for SCG
- `scg_confusion_matrix.png` - Confusion matrix
- `uncertainty_distribution.png` - Uncertainty score distributions
- `calibration_curves.png` - Calibration analysis
- `temporal_distance_analysis.png` - Detection vs temporal distance
- `domain_analysis.png` - Performance by domain
- `log.txt` - Detailed execution log

## Configuration

Key parameters in `config.py`:
- `NUM_SYNTHETIC_CONVERSATIONS`: Number of conversations to generate (default: 100)
- `ALPHA`: Balance between semantic similarity and NLI (default: 0.4)
- `CONTRADICTION_THRESHOLD`: Threshold for contradiction detection (default: 0.3)
- `TEMPORAL_DECAY_LAMBDA`: Temporal decay parameter (default: 5.0)

## Hardware Requirements

- GPU recommended for faster inference (automatic CUDA detection)
- Minimum 8GB RAM
- ~1-2GB disk space for models and results

## Citation

If you use this code, please cite:

```
Semantic Consistency Graphs for Detecting and Quantifying Hallucinations
in Multi-Turn LLM Conversations: A Graph-Based Framework for Longitudinal
Uncertainty Quantification
```
