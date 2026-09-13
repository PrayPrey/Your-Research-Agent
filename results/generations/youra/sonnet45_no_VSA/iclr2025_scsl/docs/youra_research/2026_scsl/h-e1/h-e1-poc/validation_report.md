# H-E1 Validation Report (Proof-of-Concept)

## Experiment Summary
- **Hypothesis**: h-e1 (EXISTENCE)
- **Date**: 2026-07-10
- **Mode**: Simplified PoC with synthetic data

## Results

### Test Accuracies
| Method | Worst-Group Acc | Average Acc | Group 0 | Group 1 | Group 2 | Group 3 |
|--------|-----------------|-------------|---------|---------|---------|---------|
| SGD    | 0.0000 | 0.1800 | 0.0000 | 0.0000 | 0.6300 | 0.0675 |
| Joint  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### Gate Evaluation
- **Improvement**: 0.0000 (0.0%)
- **Gate Result**: FAIL

## Notes
This is a simplified proof-of-concept using:
- Synthetic data (1000 samples, 10-dimensional features)
- Simple 2-layer MLP model (not ResNet-50)
- Single training seed (no statistical testing)
- 50 training epochs (not full hyperparameter search)

**Next Steps**:
- Full implementation with Waterbirds dataset required for formal validation
- Multiple seeds for statistical significance testing
- Hyperparameter search for optimal configuration
