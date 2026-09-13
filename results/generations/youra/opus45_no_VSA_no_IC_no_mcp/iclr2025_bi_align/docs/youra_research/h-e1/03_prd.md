# Product Requirements Document: H-E1

**Date:** 2026-08-26
**Hypothesis:** Benchmark Independence Verification
**Type:** EXISTENCE (PoC)

## Overview

Verify TruthfulQA, HHH-helpful, HHH-harmless measure distinct alignment dimensions by computing pairwise correlations on Llama-2-7B base model.

## Functional Requirements

### FR-1: Model Loading
- Load meta-llama/Llama-2-7b-hf with HuggingFace transformers
- No fine-tuning, base weights only
- GPU inference (~14GB VRAM)

### FR-2: Dataset Loading
- TruthfulQA: 817 questions, multiple_choice split
- HHH-helpful: Full eval split from Anthropic/hh-rlhf
- HHH-harmless: Full eval split from Anthropic/hh-rlhf

### FR-3: Evaluation
- TruthfulQA: MC1 accuracy, per-sample binary scores
- HHH-helpful: Preference accuracy, per-sample binary scores
- HHH-harmless: Preference accuracy, per-sample binary scores

### FR-4: Correlation Analysis
- Compute 3 pairwise Pearson correlations
- Gate check: all |r| < 0.5

### FR-5: Visualization
- Correlation matrix heatmap
- Gate status visualization
- Save to h-e1/figures/

## Non-Functional Requirements

- Single seed (fixed=42)
- Reproducible evaluation
- Figures as PNG

## Success Criteria

- All pairwise |r| < 0.5
- Code runs without error

## Out of Scope

- Training
- Model modification
- Multiple seeds
