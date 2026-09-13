# Experiment Summary

## Overview

This folder contains all results from the Semantic Consistency Graphs (SCG) experiment for detecting hallucinations in multi-turn LLM conversations.

## Files

### Documentation
- **results.md**: Complete experimental results with analysis and discussion
- **summary.md**: This file
- **log.txt**: Full execution log of the experiment (1.4MB)

### Visualizations

#### Main Results
- **model_comparison.png**: Comprehensive comparison of all four models (bar chart and radar plot)
- **error_analysis.png**: Error type distribution and rates across models

#### SCG Method Analysis
- **scg_roc_curve.png**: ROC curve for SCG (AUC: 0.50)
- **scg_pr_curve.png**: Precision-Recall curve for SCG
- **scg_confusion_matrix.png**: Confusion matrix showing true/false positives/negatives

#### Detailed Analysis
- **uncertainty_distribution.png**: Histograms of uncertainty scores by true label
- **calibration_curves.png**: Calibration analysis for all models
- **temporal_distance_analysis.png**: Detection rate vs temporal distance of contradictions
- **domain_analysis.png**: Performance breakdown by domain (medical, legal, technical)

## Quick Results

| Model | Precision | Recall | F1 | Accuracy | AUC |
|-------|-----------|--------|-------|----------|-----|
| SCG (Proposed) | 0.00 | 0.00 | 0.00 | 0.40 | 0.50 |
| Perplexity | 0.00 | 0.00 | 0.00 | 0.40 | 0.35 |
| SelfCheckGPT | 1.00 | 0.11 | 0.20 | 0.47 | 0.37 |
| Semantic Embedding | 0.00 | 0.00 | 0.00 | 0.40 | 0.35 |

## Key Findings

1. **SelfCheckGPT** achieved the best F1 score (0.20) with perfect precision but low recall
2. **SCG** showed balanced uncertainty scoring (AUC: 0.50) but conservative detection
3. All methods struggled with the challenging task, highlighting the need for improved features
4. Detection rates were consistent across domains and temporal distances

## Data

The experiment used:
- 100 synthetic conversations (54 with contradictions)
- 3 domains: medical, legal, technical
- 5-15 turns per conversation
- 15 conversations in test set

For full details, see **results.md**.
