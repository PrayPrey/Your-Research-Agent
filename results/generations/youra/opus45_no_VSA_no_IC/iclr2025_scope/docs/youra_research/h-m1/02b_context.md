# Phase 2B Context: h-m1

## Hypothesis Information

- **ID**: h-m1
- **Type**: MECHANISM
- **Statement**: Attention entropy at optimal rank correlates positively with model size (Pearson r > 0.6, p < 0.05)
- **Gate**: SHOULD_WORK
- **Status**: IN_PROGRESS
- **Prerequisites**: None (independent hypothesis)

## Success Criteria

- Pearson correlation coefficient r > 0.6
- Statistical significance p < 0.05
- Measured across Pythia 1B, 2.8B, 6.9B, 12B models

## Experimental Setup

### Models
- EleutherAI/pythia-1b
- EleutherAI/pythia-2.8b  
- EleutherAI/pythia-6.9b
- EleutherAI/pythia-12b

### Datasets
- SQuAD-v2 (single-hop QA)
- HotpotQA (multi-hop QA)

### LoRA Configuration
- Ranks: 4, 8, 16, 32, 64, 128
- Alpha: 2 × rank
- Target modules: Q, V projections
- Training: 3 epochs, lr=1e-4

## Measurement Protocol

1. Train LoRA adapters at each rank for each model
2. Identify optimal rank (best validation F1)
3. Extract attention entropy at optimal rank configuration
4. Compute correlation between attention entropy and model size

## Dependencies

None - h-m1 is independent and can run in parallel with h-e1.

---
*Generated: 2026-08-24*
