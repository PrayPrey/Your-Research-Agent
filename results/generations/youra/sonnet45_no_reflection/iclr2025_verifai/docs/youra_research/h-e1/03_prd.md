# Product Requirements Document: H-E1 Basin Entry Heterogeneity Validation

**Hypothesis ID:** H-E1  
**Type:** EXISTENCE  
**Date:** 2026-05-12  
**Author:** Anonymous
**Status:** Implementation Planning

---

## Executive Summary

This PRD defines requirements for implementing and validating H-E1: demonstrating that Stage 1 learned constraint-graph message-passing generates structured near-solutions with measurable heterogeneity in violation patterns (d/n range > 0.20, entropy H > 2.0) sufficient to support basin recovery stratification.

**Success Criteria:** PoC validation showing baseline NeuroSAT generates heterogeneous near-solutions on G4SATBench 3-SAT dataset.

---

## Problem Statement

The Conditional Basin Recovery approach requires Stage 1 (learned message-passing) to produce diverse near-solutions with heterogeneous violation patterns. Without sufficient heterogeneity (d/n range > 0.20, entropy H > 2.0), Stage 2 basin recovery cannot stratify solutions effectively.

**Hypothesis:** Under locally factorizable constraint systems (SAT, typed CSPs), Stage 1 learned constraint-graph message-passing generates structured near-solutions with measurable heterogeneity in violation patterns.

**Gate Type:** MUST_WORK - If this fails, the entire Conditional Basin Recovery approach needs redesign.

---

## Functional Requirements

### FR-1: Dataset Infrastructure
**Priority:** P0 (Blocking)  
**Description:** Load and preprocess G4SATBench 3-SAT dataset (easy difficulty)

**Specifications:**
- Dataset: G4SATBench 3-SAT Easy (10-40 variables, clause-to-variable ratio 4.2-4.3)
- Training: 80,000 SAT/UNSAT pairs
- Validation: 10,000 pairs
- Test: 10,000 pairs
- Format: DIMACS CNF → Literal-Clause Graph (LCG*)
- Graph construction: Bipartite (literals ↔ clauses)
- Node features: 128-dim learned literal embeddings
- Edge features: Clause-literal incidence

**Augmentation (Training only):**
- Variable permutation
- Clause permutation
- Negation flips (preserving satisfiability)

**Dependencies:**
- G4SATBench repository clone
- PyTorch Geometric for graph data structures

---

### FR-2: Baseline Model Implementation
**Priority:** P0 (Blocking)  
**Description:** Implement NeuroSAT baseline architecture for Stage 1 message-passing

**Architecture Specifications:**
- Model: NeuroSAT (Selsam et al. 2019)
- Hidden dimension: 128
- Message passing iterations: 32
- Literal embeddings: 128-dim (randomly initialized, learned)
- Clause embeddings: 128-dim (randomly initialized, learned)
- Message MLPs: 3 hidden layers, ReLU activation
- Update mechanism: LSTM (literal and clause states)

**Implementation Pattern:**
```python
class NeuroSAT(nn.Module):
    def __init__(self, hidden_size=128, num_rounds=32):
        # Message MLPs
        self.l_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
        self.c_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
        
        # LSTM updates
        self.l_update = nn.LSTM(hidden_size * 2, hidden_size)
        self.c_update = nn.LSTM(hidden_size, hidden_size)
```

**Dependencies:**
- PyTorch >= 1.12
- PyTorch Geometric >= 2.0

---

### FR-3: Training Pipeline
**Priority:** P0 (Blocking)  
**Description:** Train NeuroSAT with unsupervised loss for satisfiability classification

**Training Configuration:**
- Optimizer: Adam (lr=1e-4, weight_decay=1e-8)
- Schedule: ReduceLROnPlateau (mode='min', factor=0.5, patience=10)
- Batch size: 128
- Epochs: 100 (with early stopping patience=20)
- Loss: Unsupervised NeuroSAT loss
  - SAT instances: L = -log(P_sat)
  - UNSAT instances: L = -log(1 - P_sat)
- Seeds: 1 (seed=123) - sufficient for heterogeneity measurement

**Source:** G4SATBench optimal hyperparameters (grid search result)

**Dependencies:**
- FR-2 (Model Implementation)
- FR-1 (Dataset Infrastructure)

---

### FR-4: Heterogeneity Measurement
**Priority:** P0 (Blocking)  
**Description:** Measure basin entry heterogeneity metrics (d/n, entropy H) across generated near-solutions

**Metric Specifications:**

**Primary Metrics:**
1. **d/n Distribution Range**
   - Definition: Range of normalized Hamming distance across 1000+ generated near-solutions
   - Measurement: max(d/n) - min(d/n), or Q3 - Q1 (interquartile range)
   - Target: > 0.20

2. **Entropy H Distribution Range**
   - Definition: Range of violation pattern entropy across generated solutions
   - Measurement: max(H) - min(H)
   - Target: > 2.0

**Distribution Statistics:**
- Mean d/n, std d/n
- Mean H, std H
- Quartiles: Q1, Q2 (median), Q3

**Implementation Pattern:**
```python
def compute_heterogeneity_metrics(assignments, ground_truths):
    d_n_values = []
    entropy_values = []
    
    for assignment, gt in zip(assignments, ground_truths):
        # Normalized Hamming distance
        d_n = (assignment != gt).sum() / len(assignment)
        d_n_values.append(d_n)
        
        # Violation entropy
        clause_violations = compute_clause_violations(assignment)
        H = entropy(clause_violations + 1e-10)
        entropy_values.append(H)
    
    return {
        'd_n_range': np.max(d_n_values) - np.min(d_n_values),
        'd_n_iqr': np.percentile(d_n_values, 75) - np.percentile(d_n_values, 25),
        'entropy_range': np.max(entropy_values) - np.min(entropy_values),
        'pass_criteria': (d_n_range > 0.20 and entropy_range > 2.0)
    }
```

**Dependencies:**
- FR-3 (Trained model)
- numpy, scipy for statistics

---

### FR-5: Visualization Generation
**Priority:** P1 (High)  
**Description:** Generate visualization figures for heterogeneity analysis

**Required Figures:**

1. **Gate Metrics Comparison** (Mandatory)
   - Target vs actual metrics bar chart
   - Metrics: d/n range, entropy range

2. **d/n Distribution Histogram**
   - X-axis: Normalized Hamming distance bins
   - Y-axis: Frequency count
   - Overlay: Q1, Q2, Q3 markers, target range (0.20) indicator

3. **Entropy Distribution Histogram**
   - X-axis: Violation entropy H bins
   - Y-axis: Frequency count
   - Overlay: Mean, std markers, target range (2.0) indicator

4. **d/n vs Entropy Scatter Plot**
   - X-axis: d/n values
   - Y-axis: Entropy H values
   - Purpose: Visualize correlation between distance and diffuseness
   - Overlay: Basin entry criteria boundary (d/n < 0.15, H > 2.5)

5. **Quartile Box Plot**
   - Two box plots side-by-side: d/n distribution, entropy distribution
   - Shows: Q1, median, Q3, whiskers, outliers

**Output Location:** `{hypothesis_folder}/figures/`

**Dependencies:**
- FR-4 (Heterogeneity metrics)
- matplotlib, seaborn

---

## Non-Functional Requirements

### NFR-1: Computational Resources
- Single GPU execution (CUDA_VISIBLE_DEVICES=<empty_gpu_id>)
- GPU memory: < 48GB for batch_size=128
- Training time: ~2-4 hours for 100 epochs (G4SATBench easy)

### NFR-2: Reproducibility
- Fixed random seed (123) for consistency
- Deterministic operations where possible
- Save model checkpoints at best validation loss

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Unit tests for metric computation functions

### NFR-4: Output Organization
- All outputs in `{hypothesis_folder}/`
- Model checkpoints: `{hypothesis_folder}/checkpoints/`
- Figures: `{hypothesis_folder}/figures/`
- Metrics: `{hypothesis_folder}/metrics/`

---

## Success Criteria

**PoC Pass Condition:**
1. Code runs without error ✓
2. d/n range > 0.20 ✓
3. Entropy range > 2.0 ✓

**Gate Validation (MUST_WORK):**
- Both conditions must be met
- If failed: Explore alternative Stage 1 architectures or constraint representations

**Expected Baseline Performance:**
- Clause satisfaction: ~85% on random 3-SAT (from NeuroSAT paper)
- Satisfiability classification: ~85% accuracy on SR(U(10,40))

---

## Dependencies & External Systems

### External Dependencies
1. **G4SATBench Repository**
   - URL: https://github.com/zhaoyu-li/G4SATBench
   - Purpose: Dataset generation and benchmarking framework
   - Installation: `git clone` + `bash scripts/install.sh`

2. **NeuroSAT Reference Implementation**
   - URL: https://github.com/dselsam/neurosat
   - Purpose: Architecture reference (not directly used, implemented from scratch)

### Python Dependencies
- PyTorch >= 1.12
- PyTorch Geometric >= 2.0
- numpy >= 1.21
- scipy >= 1.7
- matplotlib >= 3.5
- seaborn >= 0.11

---

## Out of Scope

- Stage 2 basin recovery implementation (deferred to H-M2, H-M3)
- Multi-seed training (single seed sufficient for EXISTENCE hypothesis)
- Medium/Hard difficulty datasets (easy only for initial validation)
- Baseline comparison with other SAT solvers (deferred to Phase 5)
- Hyperparameter tuning (using G4SATBench optimal values)

---

## Implementation Notes

**Hypothesis Type:** EXISTENCE (PoC validation)  
**Task Budget:** LIGHT tier (≤15 tasks)  
**Epic Range:** 4-8 tasks  
**Infrastructure Level:** Minimal

**Development Strategy:**
1. Setup dataset infrastructure first
2. Implement and train baseline NeuroSAT
3. Generate near-solutions and compute heterogeneity metrics
4. Validate against gate criteria
5. Generate visualization figures

**Risk Mitigation:**
- If d/n range insufficient: Try alternative decoding strategies (clustering parameters)
- If entropy range insufficient: Analyze message-passing convergence patterns

---

## Appendix: Traceability

| Requirement | Source | Phase 2C Section |
|-------------|--------|------------------|
| Dataset (G4SATBench 3-SAT easy) | GitHub (Exa) | Appendix B, Repository 2 |
| Model (NeuroSAT architecture) | GitHub (Exa) | Appendix B, Repository 1 |
| Training config (Adam 1e-4) | GitHub (Exa) | Training Protocol |
| Metrics (d/n, entropy) | Phase 2B | Success Criteria |
| Gate criteria (>0.20, >2.0) | Phase 2B | Gate Condition |

---

*Generated for Phase 3 Implementation Planning | H-E1 EXISTENCE Hypothesis | Anonymous Pipeline v7.7.0*
