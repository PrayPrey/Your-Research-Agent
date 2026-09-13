# Phase 2B Context: h-c1

**Hypothesis ID:** h-c1
**Type:** CONDITION
**Gate:** SHOULD_WORK
**Status:** IN_PROGRESS

## Hypothesis Statement

Mode profiles are stable within methods: split-half reliability Cronbach's alpha > 0.8

## Prerequisites

- **h-m1** (VALIDATED, PASS): Different mathematical operations create systematically different sensitivities to influence modes

## Success Criteria

- **P2:** Cronbach's alpha > 0.8 for within-method stability

## Experimental Context

### Models
- LLaMA-2-7B
- Mistral-7B
- Qwen-7B
- CodeLLaMA-7B (control)

### Attribution Methods
- TRAK (gradient projection)
- TracIn (checkpoint proximity)
- Kronfluence (K-FAC approximation)

### Influence Modes
- Memorization
- Feature Transfer
- Spurious Association

### Probe Setup
- 1000 contrastive pairs per mode per model

## Previous Hypothesis Results (h-m1)

h-m1 validated that different mathematical operations (gradient projection, checkpoint proximity, K-FAC) create systematically different sensitivities to influence modes. This provides the foundation for testing whether those mode profiles are stable (h-c1).

## Key Research Questions for h-c1

1. How to measure split-half reliability for attribution mode profiles?
2. What constitutes appropriate random splits for Cronbach's alpha calculation?
3. How many splits are needed for robust reliability estimation?
