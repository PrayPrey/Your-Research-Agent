# Product Requirements Document: H-M3

**Hypothesis:** Models Learn Single Reward Signal Missing Bidirectional Nuance
**Date:** 2026-08-19
**Version:** 1.0
**Type:** MECHANISM
**Tier:** FULL

---

## Executive Summary

This experiment tests whether single scalar reward training causes models to miss bidirectional adaptation nuance. Building on H-M1 (models optimize for annotator approval) and H-M2 (annotators conflate correctness with user-state-modeling), H-M3 analyzes hidden state representations to determine if models learn separate representations for Type A (correctness) vs Type B (user-state-modeling) tasks.

**Core Question:** Do hidden state representations distinguish between correctness and user-state-modeling tasks, or does the single reward signal conflate them?

---

## Problem Statement

RLHF training uses single scalar rewards that may compress rich internal representations. If models show low representation separation between task types, this supports the hypothesis that scalar rewards miss bidirectional nuance.

**Gate Condition:** SHOULD_WORK
**Pass:** separation_score < 0.1 OR probe_accuracy < 0.6
**Fail:** separation_score > 0.3 AND probe_accuracy > 0.8

---

## Functional Requirements

### FR-1: Data Loading
- Load cached H-M1/H-M2 task classifications (Type A/B labels for 2212 tasks)
- Type A (Correctness): 1977 tasks
- Type B (User-State-Modeling): 235 tasks
- Source: TruthfulQA, ETHICS justice, HHH single-turn

### FR-2: Model Loading
- Load Llama-2-7B-Chat (primary) with `output_hidden_states=True`
- Load Llama-2-13B-Chat for cross-model validation
- Load Mistral-7B-Instruct for cross-model validation
- All models: HuggingFace transformers, float16, device_map="auto"

### FR-3: Hidden State Extraction
- Extract last layer, last token hidden states for all 2212 tasks
- Batch size: 8
- Output shape: (N, hidden_dim) where hidden_dim ~4096

### FR-4: Representation Separation Analysis
- Compute intra-type cosine similarity (within Type A, within Type B)
- Compute inter-type cosine similarity (between Type A and Type B)
- Calculate separation_score = (intra_mean - inter_mean)

### FR-5: Linear Probe Classification
- Train LinearSVC on hidden states with Type A/B labels
- 5-fold cross-validation
- Report mean probe accuracy

### FR-6: Visualization
- Gate metrics bar chart (separation score vs threshold)
- t-SNE/UMAP of hidden states colored by Type A/B
- Save to h-m3/figures/

### FR-7: Results Export
- Save metrics to h-m3/code/outputs/results.json
- Save figures to h-m3/figures/

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (float16)
- Batch processing for memory efficiency

### NFR-2: Reproducibility
- Fixed random seed: 42
- Deterministic hidden state extraction

### NFR-3: Compatibility
- HuggingFace transformers compatible
- Models must support output_hidden_states=True

---

## Success Criteria

| Metric | Pass Condition | Fail Condition |
|--------|----------------|----------------|
| Separation Score | < 0.1 | > 0.3 |
| Probe Accuracy | < 0.6 | > 0.8 |
| Gate Pass | Either condition | Both fail conditions |

**Expected:** Low separation (~0.0-0.1), modest probe accuracy (~0.55-0.65)

---

## Dependencies

- H-M1 results: Task type classifications
- H-M2 results: Confirmed annotator conflation
- HuggingFace: transformers, datasets
- sklearn: LinearSVC, cross_val_score
- scipy: cosine distance
- matplotlib/seaborn: visualization

---

## Data Specifications

### Input
- Task classifications from H-M1/H-M2 (cached)
- Task prompts for hidden state extraction

### Output
- results.json: separation_score, probe_accuracy, per-model metrics
- figures/: gate_metrics.png, tsne_representation.png

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Memory issues | Batch processing, float16 |
| Model access | Use open-source models only |
| Statistical power | Full 2212 task set (not small subset) |
