# Product Requirements Document: h-m1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis:** Attention entropy at optimal rank correlates positively with model size (Pearson r > 0.6, p < 0.05)
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

This PRD defines requirements for testing h-m1: whether attention entropy at optimal LoRA rank correlates with model size. The experiment trains LoRA adapters across 4 Pythia model sizes and 6 ranks, measures attention entropy at each optimal rank, and computes Pearson correlation.

---

## Problem Statement

Understanding why optimal LoRA rank scales with model size requires mechanistic insight. This hypothesis tests whether attention entropy—a measure of attention distribution complexity—explains the relationship.

---

## Functional Requirements

### FR-1: Data Preparation
- Load SQuAD v2.0 dataset from HuggingFace
- Extract train[:5000] for training, validation[:1000] for evaluation
- Tokenize with max sequence length 512

### FR-2: Model Loading
- Load Pythia models: 1B, 2.8B, 6.9B, 12B from EleutherAI
- Use float16 precision with device_map="auto"
- Cache models locally

### FR-3: LoRA Training
- Create LoRA adapters with ranks [4, 8, 16, 32, 64, 128]
- Target modules: query_key_value (fused QKV in Pythia)
- Alpha = 2 × rank, dropout = 0.05
- Train 3 epochs, lr=1e-4, batch=4 (grad accum 4)
- AdamW optimizer, linear warmup (10%) + cosine decay

### FR-4: Evaluation
- Compute validation F1 score for each (model, rank) combination
- Identify optimal rank per model (highest F1)
- Extract attention entropy at optimal configuration

### FR-5: Attention Entropy Computation
- Forward pass with output_attentions=True
- Compute Shannon entropy: -Σ(p * log(p)) per attention head
- Average across layers and positions
- Handle padding via attention mask

### FR-6: Correlation Analysis
- Collect (model_size, entropy_at_optimal_rank) pairs
- Compute Pearson correlation coefficient
- Report r value and p-value
- Pass criterion: r > 0.6 AND p < 0.05

### FR-7: Visualization
- Scatter plot: model size vs attention entropy with regression line
- Line plots: F1 vs rank for each model
- Heatmap: entropy across (model, rank) grid
- Bar chart: optimal rank per model

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Set random seeds for all operations
- Log all hyperparameters
- Save model checkpoints

### NFR-2: Resource Efficiency
- Use gradient checkpointing for large models
- Implement early stopping on validation plateau
- Target: complete within 48 GPU-hours (A100)

### NFR-3: Logging
- Log training loss, validation F1 per epoch
- Log attention entropy measurements
- Save results to JSON/YAML

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Pearson r | > 0.6 |
| p-value | < 0.05 |
| Code execution | Error-free |
| All 24 (model, rank) combinations | Completed |

---

## Data Specifications

### Input Data
- **Dataset**: SQuAD v2.0
- **Source**: HuggingFace datasets (`squad_v2`)
- **Train samples**: 5000
- **Validation samples**: 1000

### Model Specifications
| Model | Parameters | HuggingFace ID |
|-------|------------|----------------|
| Pythia-1B | 1.0B | EleutherAI/pythia-1b |
| Pythia-2.8B | 2.8B | EleutherAI/pythia-2.8b |
| Pythia-6.9B | 6.9B | EleutherAI/pythia-6.9b |
| Pythia-12B | 12B | EleutherAI/pythia-12b |

---

## Dependencies

- transformers >= 4.30
- peft >= 0.4
- datasets >= 2.0
- torch >= 2.0
- scipy >= 1.10
- matplotlib >= 3.5

---

## Out of Scope

- Comparison with other adapter methods (prefix tuning, adapters)
- Testing on other model families
- Multi-dataset validation (reserved for follow-up)

---

*Generated from Phase 2C experiment design*
*Next: Architecture design (03_architecture.md)*
