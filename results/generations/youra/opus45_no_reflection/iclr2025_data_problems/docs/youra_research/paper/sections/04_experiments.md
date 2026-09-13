# Experiments

## Experimental Setup

### Dataset

We use SST-2 (Stanford Sentiment Treebank binary) from the GLUE benchmark via HuggingFace Datasets. The dataset contains 67,349 training examples and 872 validation examples for binary sentiment classification (positive/negative).

We inject 5% random label noise by flipping labels for ~3,367 randomly selected training examples (seed 42). This creates ground-truth for mislabeled detection evaluation.

### Models

| Model | Parameters | Layers | Hidden Dim | Attention | Source |
|-------|-----------|--------|------------|-----------|--------|
| BERT-base-uncased | 110M | 12 | 768 | Bidirectional | HuggingFace |
| GPT-2 | 124M | 12 | 768 | Causal | HuggingFace |

Both models are fine-tuned on SST-2 for 3 epochs with AdamW (lr=2e-5, batch_size=32).

### Attribution Methods and Compute Budgets

| Method | Library | Compute Budgets |
|--------|---------|-----------------|
| TRAK | MadryLab/trak | proj_dim: 64, 256, 1024 |
| EK-FAC | pomonam/kronfluence | proj_dim: 64, 256, 1024 |
| TracIn | captum | checkpoints: 1, 2, 3 |

### Baselines

- **Random**: Assign random influence scores
- **Loss-based**: Rank by training loss on the test example's class

## Hypothesis Verification Experiments

### H-E1: Existence of Architecture-Method Interaction

**Goal:** Verify that architecture-method interaction exists and is measurable.

**Procedure:** Run all 6 conditions (3 methods × 2 architectures) and compute mislabeled detection AUC for each.

**Success Criterion:** All conditions produce AUC > random baseline; measurable differences exist.

### H-M1: Attention Structure Difference

**Goal:** Quantify the fundamental structural difference between bidirectional and causal attention.

**Procedure:** Extract attention weights from both models on 100 validation examples. Compute upper-triangle sparsity (fraction of zero weights above diagonal).

**Metrics:**
- Upper-triangle sparsity (BERT vs GPT-2)
- Expected: BERT ~0%, GPT-2 100%

### H-M2: Hessian Curvature Patterns

**Goal:** Confirm that different attention structures create different loss landscape curvature.

**Procedure:** Compute top-20 Hessian eigenvalues for both fine-tuned models using pytorch-hessian-eigenthings on 500 training examples.

**Metrics:**
- Top eigenvalue (BERT vs GPT-2)
- Relative difference
- Expected: >10% difference

### H-M3: Attribution Method Comparison

**Goal:** Verify all three methods show measurable architecture effects.

**Procedure:** Run all methods at fixed compute budget (proj_dim=256 or 2 checkpoints). Compute cross-architecture AUC difference for each method.

**Metrics:**
- Per-method AUC (BERT vs GPT-2)
- Relative difference
- Success: Any method >10% difference

### H-M4: Pareto Frontier Analysis

**Goal:** Test specific predictions about architecture-method pairings across the full efficiency-accuracy trade-off.

**Procedure:** Run all methods at all compute budgets on both architectures with 2 random seeds. Construct Pareto curves plotting AUC vs compute.

**Predictions:**
- **P1:** EK-FAC GPT-2 > BERT (p<0.05, Cohen's d>0.3)
- **P2:** TracIn BERT > GPT-2 (p<0.05, Cohen's d>0.3)
- **P3:** TRAK |BERT-GPT-2| < 5%

## Statistical Analysis

All experiments use 2 random seeds (42, 123). We report mean AUC ± standard deviation. Statistical comparisons use paired t-tests with significance threshold p<0.05.

We acknowledge that 2 seeds provides directional evidence but limited statistical power for detecting moderate effect sizes. P3 (TRAK invariance) can be confirmed with <1% observed differences; P1/P2 require effect size estimates that inform future adequately-powered studies.

## Reproducibility

All experiments use:
- Python 3.10, PyTorch 2.0
- Fixed random seeds (42, 123)
- Identical hardware (A100 40GB)
- Published library versions (trak 0.2.0, kronfluence 0.2.1)

Code and checkpoints are available for full reproducibility.
