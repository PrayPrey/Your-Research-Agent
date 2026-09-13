# Experimental Setup

Our experiments test two complementary questions about baseline NeuroSAT's solution diversity: (1) Does it generate distance heterogeneity (d/n range > 0.20)? (2) Does it generate structural heterogeneity (entropy range > 2.0)?

## Experimental Questions

**Q1: Distance Heterogeneity**  
Does baseline NeuroSAT generate near-solutions with heterogeneous normalized Hamming distances from ground truth, spanning at least 20 percentage points (d/n range > 0.20)?

*Hypothesis*: Yes—message-passing learning should explore solutions at varying distances from ground truth, enabling stratification by solution quality.

**Q2: Structural Heterogeneity**  
Does baseline NeuroSAT generate near-solutions with diverse violation structures, exhibiting at least 2.0 bits of entropy variation (entropy range > 2.0)?

*Hypothesis*: Yes—if violations are diffusely distributed across constraint space with instance-specific patterns, entropy range should exceed threshold.

**Combined Gate**: Both questions must answer "yes" for the architecture to generate heterogeneous near-solutions suitable for basin recovery stratification. If only one passes, we diagnose which dimension of diversity is architecturally limited.

## Dataset: G4SATBench 3-SAT Easy

**Source**: G4SATBench [Li et al., 2024] provides a comprehensive SAT benchmark with ground truth satisfying assignments for each instance.

**Difficulty**: 3-SAT Easy (10-40 variables, clause-to-variable ratio $\alpha \in [4.2, 4.3]$)

**Rationale**: This difficulty level balances several considerations:
- **Ground truth availability**: All instances have known satisfying assignments, enabling d/n and entropy measurement
- **Controlled complexity**: Instances are solvable by baseline NeuroSAT (>85% clause satisfaction), avoiding conflation with fundamental hardness
- **Sufficient constraint space**: 10-40 variables provide enough clauses (42-172 clauses) for meaningful entropy distribution measurement

**Dataset Split**:
- Training: 20 instances (proof-of-concept scale; full dataset has 80k)
- Validation: 10 instances
- Test: 10 instances (8 SAT after filtering, 2 UNSAT removed)

**UNSAT Filtering Rationale**: Instances without satisfying assignments have undefined d/n (no ground truth to compare against) and undefined entropy (no violation distribution without attempted assignments). We filter UNSAT instances at evaluation time, focusing the gate on SAT instances where heterogeneity measurements are well-defined.

## Baseline: NeuroSAT Architecture

**Model**: Baseline NeuroSAT [Selsam et al., 2019] without modifications

**Architecture Details**:
- Hidden dimension: 128
- Message-passing rounds: 32
- LSTM-based state updates for literals and clauses
- Learned initialization: Single 128-dim parameter vector, shared across all instances
- No stochastic sampling, ensemble, or diversity regularization

**Training Configuration**:
- Optimizer: Adam ($\text{lr}=10^{-4}$, weight decay $10^{-8}$)
- Learning rate schedule: ReduceLROnPlateau (mode=min, factor=0.5, patience=10)
- Batch size: 32
- Maximum epochs: 100 (early stopped at 33)
- Early stopping patience: 20 epochs

**Loss Function**: Unsupervised SAT/UNSAT classification loss (single-bit supervision)

## Evaluation Metrics

**Primary Metrics** (Gate Criteria):
1. **d/n range**: $\text{Q3}_{d/n} - \text{Q1}_{d/n}$ across 8 test instances. Pass threshold: > 0.20
2. **Entropy range**: $\text{Q3}_H - \text{Q1}_H$ across 8 test instances. Pass threshold: > 2.0

**Secondary Metrics** (Distribution Analysis):
- Mean, standard deviation, median for d/n and entropy
- Interquartile range (IQR) to assess distribution consistency
- Correlation between d/n and entropy (Pearson $r$) to test independence

**Training Metrics** (Convergence Analysis):
- Training loss trajectory
- Validation loss plateau
- Final loss compared to theoretical minimum ($\log(2) \approx 0.693$ for balanced binary classification)

## Experimental Procedure

1. **Training Phase**:
   - Train baseline NeuroSAT on 20 SAT instances for up to 100 epochs
   - Monitor validation loss for early stopping
   - Save model checkpoint at best validation loss

2. **Evaluation Phase**:
   - Load best checkpoint
   - For each of 8 test SAT instances:
     - Generate assignment via forward pass
     - Compute d/n against ground truth
     - Compute violation entropy from clause violation counts
     - Record metrics

3. **Statistical Analysis**:
   - Compute distribution statistics (mean, std, Q1, Q2, Q3)
   - Calculate d/n range and entropy range
   - Compare against gate thresholds (0.20, 2.0)
   - Generate visualization (scatter plot, box plots, gate comparison chart)

## Hardware and Implementation

**Hardware**: NVIDIA H100 NVL GPU (95830 MiB memory available)

**Software Stack**:
- PyTorch 2.0+ with PyTorch Geometric for graph batching
- G4SATBench dataset utilities for DIMACS parsing
- Custom heterogeneity metrics implementation

**Reproducibility**: Single training seed (123) for proof-of-concept. Full validation would require multiple seeds ($n \geq 5$) to assess variance across training runs, deferred to future work after establishing baseline behavior.

## Expected Outcomes

If both metrics pass (d/n range > 0.20 AND entropy range > 2.0), we conclude that baseline NeuroSAT generates heterogeneous near-solutions suitable for basin recovery, and proceed to test Stage 2 refinement mechanisms (H-M1 through H-M4).

If one metric fails, we diagnose the architectural limitation. For example:
- d/n pass, entropy fail → Distance diversity exists but structural diversity missing
- d/n fail, entropy pass → Structural diversity exists but insufficient distance variation
- Both fail → Baseline architecture lacks heterogeneity in both dimensions
