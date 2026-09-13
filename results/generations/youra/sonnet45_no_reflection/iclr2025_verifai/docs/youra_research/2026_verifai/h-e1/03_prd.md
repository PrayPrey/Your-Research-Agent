# Product Requirements Document: H-E1 Basin Entry Heterogeneity Validation

**Date:** 2026-05-12  
**Hypothesis ID:** H-E1  
**Type:** EXISTENCE  
**Author:** Anonymous
**Phase:** Phase 3 - Implementation Planning

---

## Executive Summary

Implement and validate baseline NeuroSAT architecture on G4SATBench 3-SAT dataset to measure heterogeneity in violation patterns from Stage 1 learned constraint-graph message-passing. Success requires demonstrating measurable diversity in near-solutions (d/n range > 0.20, entropy H > 2.0) sufficient for basin recovery stratification.

**Gate Type:** MUST_WORK  
**Success Criteria:** d/n range > 0.20 AND entropy range > 2.0  
**Hypothesis Statement:** Under locally factorizable constraint systems (SAT, typed CSPs), Stage 1 learned constraint-graph message-passing generates structured near-solutions with measurable heterogeneity in violation patterns (d/n range > 0.20, entropy H > 2.0) sufficient to support basin recovery stratification.

---

## Problem Statement

### Research Context

This is the foundation hypothesis (H-E1) in the Conditional Basin Recovery verification chain. It validates whether learned constraint-graph message-passing produces the diverse near-solution space required for subsequent basin recovery mechanisms.

### Technical Challenge

Validate that baseline NeuroSAT generates heterogeneous violation patterns across generated near-solutions, demonstrating sufficient diversity for stratification without requiring Stage 2 refinement mechanisms.

### Why This Matters

Foundation hypothesis for entire verification chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4). If baseline message-passing lacks heterogeneity, subsequent basin recovery mechanisms cannot be validated.

---

## Functional Requirements

### FR-1: Dataset Infrastructure

**Priority:** P0 (Blocking)  
**Description:** Implement G4SATBench 3-SAT dataset loading and preprocessing pipeline.

**Acceptance Criteria:**
- Clone and install G4SATBench repository (https://github.com/zhaoyu-li/G4SATBench)
- Load 3-SAT Easy difficulty dataset (10-40 variables, clause/variable ratio 4.2-4.3)
- Parse DIMACS CNF format to literal-clause bipartite graph (LCG*)
- Support 80k training, 10k validation, 10k test SAT/UNSAT pairs
- Implement custom collate function for variable-size SAT instances
- Apply augmentation: variable permutation, clause permutation, negation flips (training only)

**Data Specifications:**
- **Format:** DIMACS CNF → PyTorch Geometric Data objects
- **Graph Representation:** Bipartite literal-clause graph (LCG*)
- **Node Features:** Literal embeddings (128-dim, learned), Clause embeddings (128-dim, learned)
- **Edge Features:** Clause-literal incidence matrix
- **Batch Size:** 128 instances per batch

---

### FR-2: NeuroSAT Baseline Model

**Priority:** P0 (Blocking)  
**Description:** Implement NeuroSAT architecture for constraint-graph message-passing.

**Acceptance Criteria:**
- Message-passing GNN on literal-clause graph
- Hidden dimension: 128
- Message passing iterations: 32
- LSTM-based state updates for literals and clauses
- Message MLPs: 3 hidden layers with ReLU activation
- Support forward pass: (graph, l_init, c_init) → (l_final, c_final)
- Decode assignment from literal embeddings via clustering

**Architecture Specifications:**
```python
class NeuroSAT(nn.Module):
    - hidden_size: 128
    - num_rounds: 32
    - l_msg_mlp: MLP(128, 128, 128, num_layers=3)
    - c_msg_mlp: MLP(128, 128, 128, num_layers=3)
    - l_update: LSTM(256, 128)  # 128*2 for concatenated input
    - c_update: LSTM(128, 128)
```

**Implementation Source:**
- Reference: Selsam et al. 2019 (https://github.com/dselsam/neurosat)
- Alternative: G4SATBench GGNN implementation (https://github.com/zhaoyu-li/G4SATBench)

---

### FR-3: Training Pipeline

**Priority:** P0 (Blocking)  
**Description:** Implement training loop with unsupervised loss for SAT/UNSAT classification.

**Acceptance Criteria:**
- Optimizer: Adam (lr=1e-4, weight_decay=1e-8)
- Learning rate schedule: ReduceLROnPlateau (mode='min', factor=0.5, patience=10)
- Loss function: Unsupervised loss from NeuroSAT paper
  - L = -log(P_sat) for SAT instances
  - L = -log(1-P_sat) for UNSAT instances
- Epochs: 100 with early stopping (patience=20 on validation loss)
- Single seed: 123 (EXISTENCE hypothesis - single run sufficient)
- Checkpoint best model by validation loss

**Training Data:**
- G4SATBench 3-SAT easy: 80k training pairs
- Augmentation: variable/clause permutation, negation flips
- Validation: 10k pairs (no augmentation)

---

### FR-4: Heterogeneity Measurement

**Priority:** P0 (Blocking)  
**Description:** Compute basin entry heterogeneity metrics from generated near-solutions.

**Acceptance Criteria:**
- Generate 1000+ near-solutions on test SAT instances (10k test set)
- For each solution, compute:
  - d/n: Normalized Hamming distance (violations / n_variables)
  - Entropy H: Violation pattern entropy (-Σ p_i log p_i)
- Measure distribution statistics:
  - d/n range: max(d/n) - min(d/n) OR Q3 - Q1 (IQR)
  - Entropy range: max(H) - min(H)
  - Mean, std, quartiles (Q1, Q2, Q3) for both metrics
- Gate evaluation: d/n range > 0.20 AND entropy range > 2.0

**Metrics Implementation:**
```python
def compute_heterogeneity_metrics(assignments, ground_truths):
    # Returns: {d_n_range, d_n_iqr, d_n_mean, d_n_std,
    #           entropy_range, entropy_mean, entropy_std,
    #           pass_criteria: bool}
```

---

### FR-5: Visualization Generation

**Priority:** P1 (Required for validation)  
**Description:** Generate figures for heterogeneity analysis and gate validation.

**Acceptance Criteria:**

**Mandatory Figure:**
1. **Gate Metrics Comparison**: Target vs actual metrics bar chart
   - X-axis: [d/n range, entropy range]
   - Y-axis: Metric values
   - Bars: Target threshold (red), Actual value (blue)
   - Pass/Fail annotation

**Additional Figures (Autonomous):**
2. **d/n Distribution Histogram**
   - X-axis: Normalized Hamming distance bins
   - Y-axis: Frequency count
   - Overlays: Q1, Q2, Q3 markers, target range (0.20) indicator

3. **Entropy Distribution Histogram**
   - X-axis: Violation entropy H bins
   - Y-axis: Frequency count
   - Overlays: Mean, std markers, target range (2.0) indicator

4. **d/n vs Entropy Scatter Plot**
   - X-axis: d/n values, Y-axis: Entropy H values
   - Purpose: Visualize correlation between distance and diffuseness
   - Overlay: Basin entry criteria boundary (d/n < 0.15, H > 2.5)

5. **Quartile Box Plot**
   - Two side-by-side box plots: d/n distribution, entropy distribution
   - Shows: Q1, median, Q3, whiskers, outliers

**Output Location:** `{hypothesis_folder}/figures/`

---

### FR-6: Experiment Execution Script

**Priority:** P0 (Blocking)  
**Description:** Main experiment script orchestrating training, evaluation, and measurement.

**Acceptance Criteria:**
- Command-line interface with arguments:
  - `--data_root`: Path to G4SATBench data
  - `--output_dir`: Path to save checkpoints and results
  - `--seed`: Random seed (default: 123)
  - `--epochs`: Training epochs (default: 100)
  - `--batch_size`: Batch size (default: 128)
- Logging: Training loss, validation loss, epoch times
- Save outputs:
  - `best_model.pt`: Best checkpoint by validation loss
  - `training_log.csv`: Epoch-wise metrics
  - `heterogeneity_metrics.json`: Final gate metrics
  - `figures/*.png`: All visualization figures

---

## Non-Functional Requirements

### NFR-1: Performance

- **Training Time:** Complete 100 epochs within 8 hours on single GPU (RTX 3090 or better)
- **Memory:** Fit batch size 128 within 24GB GPU memory
- **Inference:** Generate 1000 near-solutions within 30 minutes

### NFR-2: Reproducibility

- **Deterministic:** Fixed random seed (123) for reproducible results
- **Logging:** Complete training logs with hyperparameters, metrics, timestamps
- **Checkpointing:** Save best model, optimizer state, epoch number

### NFR-3: Code Quality

- **Minimal Infrastructure:** PoC-level (EXISTENCE hypothesis)
  - Hardcoded config or argparse (no YAML config files)
  - Print statements + CSV logging (no WandB/TensorBoard)
  - Smoke tests only (no unit test suite)
- **Documentation:** Docstrings for key functions (NeuroSAT forward, metrics computation)
- **Error Handling:** Basic error messages for file not found, OOM errors

### NFR-4: Dependencies

**Required Libraries:**
- PyTorch >= 2.0
- PyTorch Geometric >= 2.3
- NumPy >= 1.24
- SciPy >= 1.10 (for entropy computation)
- Matplotlib >= 3.7 (for visualization)

**Repository Dependency:**
- G4SATBench repository (https://github.com/zhaoyu-li/G4SATBench)

---

## Success Criteria

### Primary Metrics (Gate Validation)

1. **d/n Distribution Range**
   - **Target:** > 0.20
   - **Measurement:** max(d/n) - min(d/n) OR Q3 - Q1

2. **Entropy H Distribution Range**
   - **Target:** > 2.0
   - **Measurement:** max(H) - min(H)

**Gate Pass:** BOTH conditions must be met

### Secondary Metrics (Expected Baseline Performance)

From NeuroSAT paper (Selsam et al. 2019):
- Clause satisfaction: ~85% on random 3-SAT
- Satisfiability classification accuracy: ~85% on SR(U(10,40))

---

## Dependencies and Constraints

### External Dependencies

1. **G4SATBench Repository**
   - Source: https://github.com/zhaoyu-li/G4SATBench
   - Installation: `git clone` + `bash scripts/install.sh`
   - Required for: Dataset generation, baseline implementations

2. **NeuroSAT Reference Implementation**
   - Source: https://github.com/dselsam/neurosat (optional reference)
   - Used for: Architecture validation

### Hypothesis Dependencies

- **Prerequisites:** None (foundation hypothesis)
- **Dependent Hypotheses:** H-M1, H-M2, H-M3, H-M4 (blocked until H-E1 passes)

### Resource Constraints

- **GPU:** Single GPU required (RTX 3090, A100, or equivalent)
- **Storage:** ~5GB for G4SATBench 3-SAT easy dataset
- **Runtime:** ~8-10 hours for training + evaluation

---

## Technical Architecture

### Data Flow

```
DIMACS CNF Files
    ↓
[G4SATBench Loader]
    ↓
Literal-Clause Graph (LCG*)
    ↓
[NeuroSAT Forward Pass]
    ↓
Literal Embeddings → Assignment Decoder
    ↓
[Heterogeneity Measurement]
    ↓
{d/n, entropy} distributions
    ↓
[Gate Evaluation]
```

### Module Structure

```
experiment/
├── data/
│   ├── sat_dataset.py         # G4SATBench wrapper
│   └── collate.py             # Custom collate function
├── models/
│   ├── neurosat.py            # NeuroSAT implementation
│   └── mlp.py                 # MLP helper module
├── metrics/
│   └── heterogeneity.py       # d/n, entropy computation
├── visualization/
│   └── plots.py               # Figure generation
└── train.py                   # Main experiment script
```

---

## Verification and Validation

### Unit Testing (Minimal - EXISTENCE PoC)

1. **Smoke Test:** Model forward pass runs without error
2. **Data Test:** Dataset loader returns correct batch shapes
3. **Metrics Test:** Heterogeneity computation on synthetic data

### Integration Testing

1. **End-to-End:** Run 1 epoch training on subset (100 samples)
2. **Metrics Pipeline:** Generate metrics from pre-trained checkpoint

### Validation Protocol

1. Train model on G4SATBench 3-SAT easy (80k pairs)
2. Generate 1000+ near-solutions on test set
3. Compute heterogeneity metrics
4. Evaluate gate: d/n range > 0.20 AND entropy range > 2.0
5. Generate all required figures
6. Save results to `04_validation.md`

---

## Risks and Mitigation

### Risk 1: Insufficient Heterogeneity

**Risk:** Baseline NeuroSAT produces uniform near-solutions (low d/n or entropy range)  
**Impact:** MUST_WORK gate fails, blocks entire hypothesis chain  
**Mitigation:** 
- Fallback: Explore alternative Stage 1 architectures (GGNN, GCN)
- Fallback: Try different constraint representations or datasets

### Risk 2: G4SATBench Installation Issues

**Risk:** Repository installation fails or dependencies conflict  
**Impact:** Cannot load dataset, blocks implementation  
**Mitigation:**
- Use Docker container with pre-installed dependencies
- Fallback: Generate synthetic 3-SAT instances using simple generator

### Risk 3: Memory Constraints

**Risk:** Batch size 128 exceeds GPU memory (24GB)  
**Impact:** Training fails with OOM error  
**Mitigation:**
- Reduce batch size to 64 or 32
- Use gradient accumulation to maintain effective batch size

---

## Timeline and Milestones

**Note:** EXISTENCE hypothesis - focus on "does it work?" validation, not precise timing.

### Milestone 1: Dataset and Model Setup
- Install G4SATBench
- Implement NeuroSAT architecture
- Verify data loader and model forward pass

### Milestone 2: Training Pipeline
- Implement training loop with unsupervised loss
- Run 100 epochs on full 80k training set
- Checkpoint best model by validation loss

### Milestone 3: Heterogeneity Analysis
- Generate 1000+ near-solutions on test set
- Compute d/n and entropy distributions
- Evaluate gate criteria

### Milestone 4: Validation and Reporting
- Generate all figures
- Write 04_validation.md report
- Update verification_state.yaml

---

## Appendix A: Reference Implementations

### Primary Reference: G4SATBench

- **Repository:** https://github.com/zhaoyu-li/G4SATBench
- **Paper:** TMLR 2024
- **Use:** Dataset loading, baseline NeuroSAT/GGNN implementations
- **Hyperparameters:** Optimal from grid search (lr=1e-4, weight_decay=1e-8)

### Secondary Reference: NeuroSAT Original

- **Repository:** https://github.com/dselsam/neurosat
- **Paper:** Selsam et al. 2019
- **Use:** Architecture reference, loss function formulation
- **Expected Baseline:** 85% clause satisfaction, 85% classification accuracy

---

## Appendix B: Configuration Specifications

### Model Configuration

```yaml
model:
  architecture: NeuroSAT
  hidden_size: 128
  num_rounds: 32
  message_mlp_layers: 3
  activation: ReLU
  update_mechanism: LSTM
```

### Training Configuration

```yaml
training:
  optimizer: Adam
  learning_rate: 1e-4
  weight_decay: 1e-8
  batch_size: 128
  epochs: 100
  early_stopping_patience: 20
  lr_schedule:
    type: ReduceLROnPlateau
    mode: min
    factor: 0.5
    patience: 10
  seed: 123
```

### Dataset Configuration

```yaml
dataset:
  name: G4SATBench_3SAT
  difficulty: easy
  num_variables: 10-40
  clause_variable_ratio: 4.2-4.3
  splits:
    train: 80000
    valid: 10000
    test: 10000
  augmentation:
    - variable_permutation
    - clause_permutation
    - negation_flips
```

---

**Document Status:** READY FOR PHASE 4 IMPLEMENTATION  
**Next Phase:** Phase 4 - Coding & Validation  
**Gate Type:** MUST_WORK (d/n range > 0.20 AND entropy range > 2.0)
