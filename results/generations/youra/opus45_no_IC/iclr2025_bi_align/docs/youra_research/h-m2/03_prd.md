# Product Requirements Document: H-M2

**Date:** 2026-08-10
**Hypothesis:** H-M2 - AI Formality Response Varies
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

H-M2 tests whether AI formality varies as a function of human formality in immediate responses. Building on H-M1's validated user adaptation (r=0.0134, p=0.00113), this experiment examines the reverse direction: AI-to-human formality correlation.

**Success Criterion:** |r(formality_human_1, formality_AI_1)| > 0.1 with p < 0.001

---

## Problem Statement

While H-M1 demonstrated users adapt their complexity to AI patterns, the question remains whether AI models similarly accommodate to human formality levels. This is a core mechanism for validating bidirectional formality accommodation theory.

---

## Functional Requirements

### FR-1: Data Loading and Preprocessing

**FR-1.1:** Load Anthropic/hh-rlhf dataset from HuggingFace
- Parse Human:/Assistant: conversation format
- Filter conversations with ≥4 turns (2 human + 2 AI minimum)
- Extract (human_1, AI_1) message pairs
- Target: ~26,000+ valid pairs (consistent with H-E1, H-M1)

**FR-1.2:** Message Validation
- Minimum message length: 5 characters
- Non-empty content after stripping whitespace
- Valid UTF-8 encoding

### FR-2: Formality Scoring

**FR-2.1:** DeBERTa Formality Ranker Integration
- Model: s-nlp/deberta-large-formality-ranker
- Batch inference with GPU acceleration
- Max sequence length: 512 tokens
- Output: formality probability score [0, 1]

**FR-2.2:** Batch Processing
- Batch size: 32
- Progress tracking with tqdm
- Memory-efficient processing for ~52K messages

### FR-3: Correlation Analysis

**FR-3.1:** Primary Correlation
- Pearson correlation: r(human_formality, ai_formality)
- Statistical significance: p-value calculation
- Sample size validation: n ≥ 10,000

**FR-3.2:** Robustness Checks
- Spearman rank correlation (rho)
- Permutation test baseline (1000 shuffles)

### FR-4: Gate Evaluation

**FR-4.1:** SHOULD_WORK Gate Check
- Pass: |r| > 0.1 AND p < 0.001
- Fail action: Per-model analysis exploration

### FR-5: Visualization

**FR-5.1:** Required Figures
- Scatter plot: human_formality vs ai_formality with regression line
- Correlation bar: observed |r| vs threshold (0.1)

**FR-5.2:** Optional Figures
- Hexbin density plot
- QQ plot for normality
- Residual distribution

### FR-6: Ablation Studies (if gate fails)

**FR-6.1:** Per-model breakdown (if model info available)
**FR-6.2:** Turn position variation (human_2, AI_2)
**FR-6.3:** Extreme formality filtering
**FR-6.4:** Message length control (partial correlation)

---

## Non-Functional Requirements

### NFR-1: Performance
- Process 26K+ pairs within 6 hours
- GPU memory: ≤16GB VRAM
- System memory: ≤16GB RAM

### NFR-2: Reproducibility
- Random seed: 42
- Deterministic ordering
- Version-pinned dependencies

### NFR-3: Reusability
- Reuse H-M1 DeBERTa pipeline components
- Modular correlation analysis functions

---

## Dependencies

### From H-E1 (Completed)
- BCS computation validated (SD=0.569)
- Dataset access pattern established

### From H-M1 (Completed)
- DeBERTa scoring pipeline
- Conversation parsing logic
- Baseline null distribution methodology

### External
- HuggingFace transformers
- scipy.stats
- torch (CUDA optional)

---

## Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| Pearson r | \|r\| > 0.1 | PRIMARY |
| p-value | < 0.001 | PRIMARY |
| Sample size | n ≥ 10,000 | PRIMARY |
| Spearman agreement | Same direction as Pearson | SECONDARY |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low correlation | Gate fail | Per-model analysis |
| Model variance | Heterogeneous effects | Stratified analysis |
| DeBERTa noise | Signal attenuation | Validated 87.8% accuracy |

---

## Deliverables

1. `h-m2/04_validation.md` - Validation report with gate result
2. `h-m2/figures/` - Visualization outputs
3. Updated `verification_state.yaml` with H-M2 results
