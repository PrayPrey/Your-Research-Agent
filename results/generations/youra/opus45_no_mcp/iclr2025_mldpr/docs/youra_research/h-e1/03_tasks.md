# Tasks: H-E1

**Type:** EXISTENCE (PoC)
**Tier:** LIGHT (max 15 tasks)
**Generated:** 2026-08-19

## Epic Tasks

| ID | Task | Description | Complexity | Status |
|----|------|-------------|------------|--------|
| A-1 | Data pipeline | Load CIFAR-10, SVHN, SVHN-Extra, CINIC-10 with transforms/loaders | 8 | TODO |
| A-2 | Model module | ResNet-18 builder with 10-class head | 3 | TODO |
| A-3 | Training loop | SGD+MultiStepLR training loop for one condition, checkpointing | 7 | TODO |
| A-4 | Run both training conditions | Execute training for CIFAR-10 and SVHN, save checkpoints + loss/acc history | 6 | TODO |
| A-5 | Evaluation + gap computation | Evaluate models on in-domain/held-out sets, compute generalization gaps | 5 | TODO |
| A-6 | Statistical comparison | Cohen's d + t-test on gap_high vs gap_low | 4 | TODO |
| A-7 | Visualization | Gap bar chart, accuracy comparison, training curves | 5 | TODO |
| A-8 | End-to-end orchestration | run_experiment.py wiring all modules, results.json, PoC gate check | 6 | TODO |

**Total:** 8 tasks (within LIGHT budget of 15)

## Execution Order

1. A-2 (Model) - no dependencies
2. A-1 (Data) - no dependencies
3. A-3 (Training loop) - depends on A-1, A-2
4. A-4 (Run training) - depends on A-3
5. A-5 (Evaluation) - depends on A-4
6. A-6 (Statistics) - depends on A-5
7. A-7 (Visualization) - depends on A-5
8. A-8 (Orchestration) - depends on all above

## Gate Criteria

- Cohen's d > 0.3
- p < 0.05
