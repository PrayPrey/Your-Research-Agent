# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-21T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap2
- **Gap Title**: Controlled Comparison of Equivariant vs. Plain Architectures for Weight-Space Property Prediction on Shared Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 6

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 6 (all 6 personas participated, one exchange each)

**Convergence Reason**: All 6 convergence criteria met — specific core claim, causal mechanism, 3 testable predictions with quantitative criteria, novelty articulated, feasibility confirmed, major objections addressed with mitigations

### Key Insights

1. **Dayan et al. 2026 reframes the comparison**: Expressivity equivalence theorem proves all permutation-equivariant networks have the same ceiling — efficiency is the only remaining differentiator, making this empirical comparison theoretically urgent
2. **Low-data regime is the practically relevant regime**: Real-world model zoos (RNN zoo ~1000 models, custom architecture zoos) are small; the efficiency question matters most where data is limited
3. **Permutation augmentation as mechanistic ablation**: Training plain MLPs with random neuron permutation augmentation is the key ablation — isolates whether equivariant benefit is structural (irreplaceable) or data-level (reproducible with augmentation)
4. **Null result is publishable**: If augmentation closes the gap, the finding "structural equivariance is not required, just augment" is equally important to the field

### Breakthrough Moments

- Dr. Sage's framing — "when does equivariant inductive bias matter?" — transforms a methods comparison into an actionable practical question
- Prof. Pax confirming 15-20 GPU hours total: experiment is feasible as a single-machine study
- Prof. Rex's concern that null result (augmentation fully closes gap) is still publishable — removes hidden publication bias risk from experimental design

---

## Final Hypothesis

### Title
Equivariant Weight-Space Encoders Are More Sample-Efficient Than Plain Encoders for Model Property Prediction in the Low-Data Regime

### Hypothesis ID
H-EquivSampleEfficiency-v1

### Core Claim

Under the weight-space property prediction setting using ModelZooDataset MNIST and CIFAR-10 model zoos with standardized shared train/test splits, if equivariant encoders (DWSNets, GNN-NFN) are trained versus plain encoders (flat-MLP, flat-MLP + permutation augmentation) at matched parameter budget ranges across training set sizes {100, 250, 500, 1000, full}, then equivariant encoders reach ≥90% of their peak accuracy-prediction R² at ≤50% of the training set size required by plain encoders — because permutation equivariance constrains the hypothesis space to symmetry-consistent functions, reducing effective sample complexity.

### Mechanism

1. **Structural inductive bias**: DWSNets and GNN-NFN are mathematically constrained to produce outputs invariant to neuron permutation, matching the true symmetry of weight spaces
2. **Reduced hypothesis space**: This eliminates non-symmetric functions from the search space; gradient descent converges to the correct property-prediction function with fewer examples
3. **Data volume normalizes the advantage**: At high training volume, plain MLPs discover the symmetric solution from data alone; both methods converge to similar performance (Dayan 2026 expressivity equivalence)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | Equivariant encoders are more sample-efficient | Efficiency ratio ≥ 2.0 on both MNIST and CIFAR-10 zoos | Ratio < 1.5 on both datasets |
| **P2** | Permutation augmentation partially bridges but does not close the gap at ≤250 training models | Augmented MLP strictly intermediate; CIs don't overlap with equivariant | Augmented MLP matches equivariant (augmentation fully closes gap) |
| **P3** | All conditions converge at full training size | Max pairwise R² difference < 0.05 at full data; CIs overlap | Equivariant still >0.05 R² better at full data |

---

## Novelty

**What's new**: First controlled comparison of equivariant vs. plain weight-space encoders on shared ModelZooDataset splits; first empirical sample efficiency curve for this class of methods; permutation augmentation as mechanistic ablation condition.

**Key differentiator from prior work**:
- DWSNets 2023: own private splits, no plain comparison, no efficiency curve
- Schürholt SSL 2021: plain only, no equivariant comparison, no training size ablation
- GNN-NFN 2024: custom architecture-specific splits, no shared data comparison
- Dayan 2026: theoretical proof only, no empirical efficiency data
- **This work**: shared splits + training size ablation + permutation augmentation = first controlled comparison

---

## Experimental Design

**Datasets**: ModelZooDataset MNIST model zoo (~4,860 CNNs) + CIFAR-10 model zoo (~9,000 CNNs) — both publicly available at github.com/ModelZoos/ModelZooDataset

**Conditions** (4):
1. DWSNets (equivariant) — github.com/AvivNavon/DWSNets
2. GNN-NFN (equivariant) — github.com/mkofinas/neural-graphs
3. Flat-MLP (plain) — ~50 lines PyTorch, parameter-matched by count range
4. Flat-MLP + PermAug (plain + permutation augmentation)

**Training sizes**: {100, 250, 500, 1000, full} — subsamples of fixed train/test split

**Seeds**: 10 seeds for sizes ≤250; 5 seeds for larger sizes

**Primary metric**: R² for test accuracy prediction on fixed held-out set

**Secondary metric**: R² for generalization gap prediction

**Compute**: ~15-20 GPU hours total — feasible on single GPU machine

---

## Limitations

- Results apply to MLP/CNN weight spaces only (MNIST/CIFAR-10 model zoos)
- Transformer and RNN weight spaces have different symmetry structures; separate studies required
- ModelZooDataset "full data" (~4,860) is small by DL standards — not representative of HuggingFace scale
- Parameter matching by range (not exact) may introduce residual confounds
- Bootstrap CIs at very small training sizes (100 models) may still be wide despite 10+ seeds

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met in 6 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Bootstrap at small sizes; CIFAR-10 replication required |

**Proceed to Phase 2B**: READY

---

*Phase: 2A — Dialogue | Architecture: Self-Contained Tikitaka Loop*
*Gap selected: gap2 (HIGH+PRIMARY, 4 Scholar papers, 3 GitHub repos)*
*Hypothesis ID: H-EquivSampleEfficiency-v1*
