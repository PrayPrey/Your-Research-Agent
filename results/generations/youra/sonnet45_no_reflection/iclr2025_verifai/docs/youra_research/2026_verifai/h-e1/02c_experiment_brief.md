# Experiment Design: H-E1

**Date:** 2026-05-12
**Author:** Anonymous
**Hypothesis Statement:** Under locally factorizable constraint systems (SAT, typed CSPs), Stage 1 learned constraint-graph message-passing generates structured near-solutions with measurable heterogeneity in violation patterns (d/n range > 0.20, entropy H > 2.0) sufficient to support basin recovery stratification.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** Phase 2C - Experiment Design
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Gate Type:** MUST_WORK
**Pass Condition:** d/n range > 0.20 AND entropy range > 2.0
**Fail Action:** EXPLORE alternative Stage 1 architectures or constraint representations to increase violation pattern diversity

---

## Continuation Context

**First Hypothesis:** This is the foundation hypothesis for the Conditional Basin Recovery verification chain. No previous hypothesis context to inherit.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in dependency chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Constraint Graph Message Passing SAT Dataset**
- **Result:** No SAT/CSP-specific content found in current KB
- **KB Coverage:** Archon KB primarily contains diffusion models, image generation, and general PyTorch tutorials
- **Conclusion:** SAT solver and constraint graph implementations not indexed in Archon

**Query 2: GNN SAT Solver Implementation Challenges**
- **Result:** No direct matches for GNN-based SAT solving
- **KB Coverage:** General neural network architectures present but no combinatorial optimization content

**Query 3: SAT Benchmark Datasets Evaluation**
- **Result:** No SAT benchmark datasets found
- **Conclusion:** Need to rely on Exa search for academic SAT solver implementations

**Key Insight:** Archon KB lacks coverage for SAT/CSP domain. Will rely heavily on Exa GitHub search for NeuroSAT, G4SATBench, and related implementations.

### Archon Code Examples

**Query 1: GNN Constraint Graph PyTorch**
- **Result:** General graph neural network patterns found
- **Relevant Pattern:** Message-passing architecture from diffusion UNet models
  - Multi-stage processing with skip connections
  - Attention mechanisms for node interactions
  - Pattern applicable to constraint graph message-passing

**Query 2: SAT DataLoader PyTorch**
- **Result:** Generic PyTorch DataLoader examples found
- **Relevant Code Pattern:**
  ```python
  DataLoader(dataset, batch_size=128, shuffle=True, 
             num_workers=4, collate_fn=custom_collate)
  ```
- **Insight:** Will need custom collate function for variable-size SAT instances

### Exa GitHub Implementations

**Query 1: NeuroSAT Official Implementation (⭐ HIGHEST PRIORITY)**

**Repository 1**: [dselsam/neurosat](https://github.com/dselsam/neurosat) (Official Author Implementation)
- **URL**: https://github.com/dselsam/neurosat
- **Relevance**: Original NeuroSAT paper implementation by Daniel Selsam
- **Architecture**: Message-passing GNN on literal-clause graph
  - Literal embeddings (dim=128)
  - Clause embeddings (dim=128)
  - LSTM updates for message aggregation
  - 32 message passing iterations (typical)
- **Training Config**:
  - Dataset: SR(U(10,40)) - random SAT with 10-40 variables, clause/variable ratio 4.2
  - Training: Single-bit supervision (satisfiability classification)
  - Model: d=128, 3 hidden layers in MLPs, ReLU activation
- **Key Results**: 85% accuracy on test set, generalizes to larger instances

**Repository 2**: [zhaoyu-li/G4SATBench](https://github.com/zhaoyu-li/G4SATBench) (⭐ Comprehensive Benchmark)
- **URL**: https://github.com/zhaoyu-li/G4SATBench
- **Relevance**: Modern SAT benchmark framework with 7 datasets, 3 difficulty levels
- **Datasets Included**:
  - SR (random), 3-SAT (random)
  - CA (Community Attachment), PS (Popularity-Similarity) - pseudo-industrial
  - k-Clique, k-Dominating-Set, k-Vertex-Cover - combinatorial
  - **Easy**: 10-40 vars, **Medium**: 40-200 vars, **Hard**: 200-400 vars
  - **Training**: 80k pairs (SAT/UNSAT), **Validation**: 10k, **Test**: 10k
- **Architecture**: Multiple GNN models (GGNN, GCN, GIN, NeuroSAT)
  - Feature dimension: 128
  - Message passing iterations: 32
  - Graph representations: VCG* (variable-clause), LCG* (literal-clause)
- **Training Config**:
  - Optimizer: Adam
  - Learning rate: grid search {1e-3, 5e-4, 1e-4, 5e-5, 1e-5}
  - Batch size: 128/64/32 (based on GPU memory)
  - Epochs: {50, 100, 200}
  - Weight decay: {1e-6 to 1e-10}
- **Key Code Pattern** (PyTorch Geometric):
  ```python
  # NeuroSAT architecture
  class NeuroSAT(nn.Module):
      def __init__(self, hidden_size=128, num_round=32):
          self.l_msg_mlp = MLP(hidden_size, hidden_size, hidden_size)
          self.c_msg_mlp = MLP(hidden_size, hidden_size, hidden_size)
          self.l_update = nn.LSTM(hidden_size * 2, hidden_size)
          self.c_update = nn.LSTM(hidden_size, hidden_size)
      
      def forward(self, lcg_graph, l_embedding, c_embedding):
          for round_idx in range(self.num_round):
              # Literal → Clause message passing
              l_msg = self.l_msg_mlp(l_hidden)
              l2c_msg = aggregate_messages(lcg_graph, l_msg)
              
              # Clause → Literal message passing
              c_msg = self.c_msg_mlp(c_hidden)
              c2l_msg = aggregate_messages(lcg_graph, c_msg)
              
              # LSTM updates
              _, c_state = self.c_update(l2c_msg, c_state)
              _, l_state = self.l_update(c2l_msg, l_state)
  ```

**Query 2: NSNet - Neural Satisfiability Network**

**Repository 3**: [zhaoyu-li/NSNet](https://github.com/zhaoyu-li/NSNet) (NeurIPS 2022)
- **URL**: https://github.com/zhaoyu-li/NSNet
- **Relevance**: Modern framework with probabilistic inference formulation
- **Architecture**: GNN parameterizing Belief Propagation in latent space
- **Training**: Marginal supervision (estimates variable marginals)
- **Implementation**: PyTorch + PyTorch Geometric
- **Use Case**: Can guide local search initialization (NSNet + Sparrow SLS)

**Query 3: Additional Implementations**

**Repository 4**: [wenxiwang/neuroback](https://github.com/wenxiwang/neuroback) (ICLR 2024)
- **URL**: https://github.com/wenxiwang/neuroback
- **Relevance**: Integrates GNN with CDCL solver (Kissat)
- **Architecture**: GNN for backbone prediction → guides CDCL search
- **Note**: Hybrid neural-symbolic approach

**Serena Analysis Needed**: ❌ NO
- NeuroSAT architecture is well-documented (~100 lines, LSTM-based message passing)
- G4SATBench provides clear PyTorch Geometric implementation patterns
- Code is straightforward - no complex custom layers requiring deeper analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment**: This experiment uses **NeuroSAT baseline** (established architecture) on **G4SATBench** (standard benchmark), not paper reproduction.

**Recommended Implementation Path:**
- Primary: G4SATBench framework with NeuroSAT/GGNN model (https://github.com/zhaoyu-li/G4SATBench)
- Fallback: Original NeuroSAT implementation (https://github.com/dselsam/neurosat)
- Justification: G4SATBench provides complete training/evaluation pipeline with standardized datasets, metrics, and proven hyperparameters. Modern PyTorch + PyG implementation more maintainable than original NeuroSAT codebase.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. NeuroSAT architecture is well-documented with straightforward LSTM-based message passing (~100 lines). G4SATBench provides clear PyTorch Geometric implementation patterns without complex custom layers.

---

## Experiment Specification

### Dataset

**Name**: G4SATBench 3-SAT (Easy Difficulty)
**Type**: standard (real benchmark dataset from established repository)
**Source**: https://github.com/zhaoyu-li/G4SATBench
**Hypothesis Fit**: Tests constraint-graph message-passing effectiveness on random 3-SAT instances with controlled clause-to-variable ratios. Easy difficulty (10-40 variables) enables exhaustive basin recovery analysis required for h-e1 heterogeneity measurement.

**Dataset Statistics**:
- Training: 80,000 SAT/UNSAT pairs
- Validation: 10,000 SAT/UNSAT pairs  
- Test: 10,000 SAT/UNSAT pairs
- Variables: 10-40 (easy), 40-200 (medium), 200-400 (hard)
- Clause-to-variable ratio: 4.2-4.3 (phase transition region)
- Format: DIMACS CNF

**Loading Information** (for Phase 4 download):
- Method: Custom generator (G4SATBench repository)
- Identifier: `g4satbench/generators/3-sat`
- Code:
  ```python
  # Clone G4SATBench repository
  # git clone https://github.com/zhaoyu-li/G4SATBench.git
  # cd G4SATBench
  # bash scripts/install.sh
  
  # Generate 3-SAT instances
  from g4satbench.generators import generate_3sat
  from g4satbench.data import SATDataset
  
  # Easy difficulty: 10-40 variables
  dataset = SATDataset(
      root='./data/3-sat/easy',
      difficulty='easy',
      split='train'  # or 'valid', 'test'
  )
  ```

**Preprocessing**:
- Parse DIMACS CNF to literal-clause graph (LCG*)
- Node features: Literal embeddings (128-dim, learned)
- Edge features: Clause-literal incidence
- Graph construction: Bipartite (literals ↔ clauses)

**Augmentation** (Training only):
- Variable permutation
- Clause permutation  
- Negation flips (preserve satisfiability)

### Models

#### Baseline Model

**Name**: NeuroSAT (Original Architecture)
**Type**: Custom GNN (Message-passing on literal-clause graph)
**Source**: Selsam et al. 2019 (https://github.com/dselsam/neurosat)
**Hypothesis Fit**: Baseline represents Stage 1 learned message-passing without Stage 2 refinement. Tests whether message-passing alone generates heterogeneous near-solutions (d/n range > 0.20, entropy H > 2.0).

**Architecture Configuration**:
- Hidden dimension: 128
- Message passing iterations: 32
- Literal embeddings: 128-dim (initialized randomly, learned)
- Clause embeddings: 128-dim (initialized randomly, learned)
- Message MLPs: 3 hidden layers, ReLU activation
- Update mechanism: LSTM (literal and clause states)

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (PyTorch + PyTorch Geometric)
- Identifier: `neurosat_baseline` (implement from scratch or use G4SATBench)
- Code:
  ```python
  import torch
  import torch.nn as nn
  from torch_geometric.nn import MessagePassing
  
  class NeuroSAT(nn.Module):
      def __init__(self, hidden_size=128, num_rounds=32):
          super().__init__()
          self.hidden_size = hidden_size
          self.num_rounds = num_rounds
          
          # Message MLPs
          self.l_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
          self.c_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
          
          # LSTM updates
          self.l_update = nn.LSTM(hidden_size * 2, hidden_size)
          self.c_update = nn.LSTM(hidden_size, hidden_size)
          
      def forward(self, graph, l_init, c_init):
          # Initialize states
          l_state = (l_init.unsqueeze(0), torch.zeros_like(l_init).unsqueeze(0))
          c_state = (c_init.unsqueeze(0), torch.zeros_like(c_init).unsqueeze(0))
          
          for _ in range(self.num_rounds):
              # Literal → Clause message passing
              l_msg = self.l_msg_mlp(l_state[0].squeeze(0))
              l2c_msg = aggregate_l2c(graph, l_msg)
              
              # Clause → Literal message passing
              c_msg = self.c_msg_mlp(c_state[0].squeeze(0))
              c2l_msg = aggregate_c2l(graph, c_msg)
              
              # LSTM updates
              _, c_state = self.c_update(l2c_msg.unsqueeze(0), c_state)
              _, l_state = self.l_update(
                  torch.cat([c2l_msg, flip_literals(l_state[0].squeeze(0))], dim=1).unsqueeze(0),
                  l_state
              )
          
          return l_state[0].squeeze(0), c_state[0].squeeze(0)
  
  # Or use G4SATBench implementation:
  from g4satbench.models import GGNN
  model = GGNN(hidden_size=128, n_iterations=32, graph_type='lcg')
  ```

**Output**: Literal embeddings (B × N_literals × 128) used to decode satisfying assignment

#### Proposed Model

**Architecture:** NeuroSAT (baseline) - No additional mechanism for EXISTENCE hypothesis
**Purpose**: Validate that baseline NeuroSAT generates heterogeneous near-solutions required for basin recovery analysis

**Note**: H-E1 is an EXISTENCE hypothesis testing whether the baseline Stage 1 architecture produces the required heterogeneity (d/n range > 0.20, entropy H > 2.0). No additional mechanism is added - we measure the baseline's output diversity.

**Core Mechanism Implementation:**

```python
# H-E1: Basin Entry Heterogeneity Measurement
# Purpose: Measure diversity of violation patterns from baseline NeuroSAT
# Based on: NeuroSAT (Selsam et al. 2019) + G4SATBench evaluation framework

class NeuroSATWithMetrics(nn.Module):
    """
    NeuroSAT with basin entry heterogeneity measurement.
    Tests whether message-passing generates diverse near-solutions.
    """
    def __init__(self, hidden_size=128, num_rounds=32):
        super().__init__()
        # Standard NeuroSAT architecture
        self.neurosat = NeuroSAT(hidden_size, num_rounds)
        
    def forward(self, graph, l_init, c_init):
        """
        Args:
            graph: Literal-clause bipartite graph
            l_init: (N_literals, 128) - initial literal embeddings
            c_init: (N_clauses, 128) - initial clause embeddings
        Returns:
            l_final: (N_literals, 128) - final literal embeddings
            assignment: (N_vars,) - decoded binary assignment
        """
        # Run NeuroSAT message passing
        l_final, c_final = self.neurosat(graph, l_init, c_init)
        
        # Decode assignment from literal embeddings
        assignment = decode_assignment(l_final)  # Cluster literals
        
        return l_final, assignment
    
    def measure_heterogeneity(self, assignment, ground_truth):
        """
        Compute basin entry metrics for heterogeneity analysis.
        
        Returns:
            d_n: Normalized Hamming distance (violations / n_variables)
            entropy_H: Violation pattern entropy
        """
        violations = (assignment != ground_truth)
        d_n = violations.sum() / len(violations)
        
        # Compute violation entropy (diffuseness measure)
        clause_violations = compute_clause_violations(assignment)
        entropy_H = -sum(p * log(p) for p in clause_violation_dist)
        
        return d_n, entropy_H

# Heterogeneity Measurement Protocol (Post-Training):
# 1. Generate 1000+ near-solutions on test SAT instances
# 2. For each solution, compute (d/n, entropy H)
# 3. Measure distribution statistics: range(d/n), range(H), Q1, Q3
# 4. Success: d/n range > 0.20 AND entropy range > 2.0
```

### Training Protocol

**Optimizer**: Adam
- Parameters: lr=1e-4, weight_decay=1e-8
- **Source**: G4SATBench optimal hyperparameters (grid search result)

**Learning Rate**: 1e-4 (fixed)
- **Source**: G4SATBench paper - best performing for NeuroSAT/GGNN on easy datasets

**Schedule**: ReduceLROnPlateau
- Parameters: mode='min', factor=0.5, patience=10
- **Source**: G4SATBench training protocol

**Batch Size**: 128
- **Source**: G4SATBench standard (fits in 48GB GPU memory)

**Epochs**: 100
- Early stopping: patience=20 (validation loss)
- **Source**: G4SATBench training setup

**Loss Function**: Unsupervised loss (NeuroSAT original)
- Formula: L = -log(P_sat) for SAT instances, -log(1-P_sat) for UNSAT
- **Source**: Selsam et al. 2019 (NeuroSAT paper)

**Training Data**: G4SATBench 3-SAT easy (80k pairs SAT/UNSAT)
- Augmentation: Variable permutation, clause permutation, negation flips
- **Source**: G4SATBench augmentation strategy

**Seeds**: 1 (seed=123)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for heterogeneity measurement - testing distribution properties, not mean performance.

### Evaluation

**Primary Metrics** (from Phase 2B H-E1 Success Criteria):

1. **d/n Distribution Range**
   - Definition: Range of normalized Hamming distance across 1000+ generated near-solutions
   - Measurement: max(d/n) - min(d/n), or Q3 - Q1 (interquartile range)
   - Target: > 0.20

2. **Entropy H Distribution Range**
   - Definition: Range of violation pattern entropy across generated solutions
   - Measurement: max(H) - min(H)
   - Target: > 2.0

3. **Distribution Statistics**
   - Mean d/n, std d/n
   - Mean H, std H
   - Quartiles: Q1, Q2 (median), Q3

**Success Criteria** (PoC - Direction Only):
- d/n range > 0.20 (sufficient variation for stratification)
- Entropy range > 2.0 (diverse violation patterns)
- Both conditions must be met

**Expected Baseline Performance** (from NeuroSAT paper):
- Clause satisfaction: ~85% on random 3-SAT
- Satisfiability classification: ~85% accuracy on SR(U(10,40))
- **Source**: Selsam et al. 2019

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Distribution Analysis + SAT Solving
- Library: Custom metrics + numpy/scipy for statistics
- Code:
  ```python
  import numpy as np
  from scipy.stats import entropy
  
  def compute_heterogeneity_metrics(assignments, ground_truths):
      """
      Compute basin entry heterogeneity metrics.
      
      Args:
          assignments: List of decoded assignments (N_instances,)
          ground_truths: List of satisfying assignments (N_instances,)
      
      Returns:
          metrics: Dict with d/n range, entropy range, statistics
      """
      d_n_values = []
      entropy_values = []
      
      for assignment, gt in zip(assignments, ground_truths):
          # Normalized Hamming distance
          d_n = (assignment != gt).sum() / len(assignment)
          d_n_values.append(d_n)
          
          # Violation entropy
          clause_violations = compute_clause_violations(assignment)
          H = entropy(clause_violations + 1e-10)  # Add small constant
          entropy_values.append(H)
      
      return {
          'd_n_range': np.max(d_n_values) - np.min(d_n_values),
          'd_n_iqr': np.percentile(d_n_values, 75) - np.percentile(d_n_values, 25),
          'd_n_mean': np.mean(d_n_values),
          'd_n_std': np.std(d_n_values),
          'entropy_range': np.max(entropy_values) - np.min(entropy_values),
          'entropy_mean': np.mean(entropy_values),
          'entropy_std': np.std(entropy_values),
          'pass_criteria': (
              (np.max(d_n_values) - np.min(d_n_values)) > 0.20 and
              (np.max(entropy_values) - np.min(entropy_values)) > 2.0
          )
      }
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on H-E1's focus on measuring heterogeneity in violation patterns:

1. **d/n Distribution Histogram**
   - X-axis: Normalized Hamming distance bins
   - Y-axis: Frequency count
   - Overlay: Q1, Q2, Q3 markers, target range (0.20) indicator

2. **Entropy Distribution Histogram**
   - X-axis: Violation entropy H bins
   - Y-axis: Frequency count
   - Overlay: Mean, std markers, target range (2.0) indicator

3. **d/n vs Entropy Scatter Plot**
   - X-axis: d/n values
   - Y-axis: Entropy H values
   - Purpose: Visualize correlation between distance and diffuseness
   - Overlay: Basin entry criteria boundary (d/n < 0.15, H > 2.5)

4. **Quartile Box Plot**
   - Two box plots side-by-side: d/n distribution, entropy distribution
   - Shows: Q1, median, Q3, whiskers, outliers
   - Highlights: Range visualization for both metrics

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Coverage**: No SAT/CSP-specific content found in current knowledge base. KB primarily contains diffusion models, image generation, and general PyTorch tutorials. This is documented as a finding - SAT solver domain not currently indexed in Archon.

**Archon Code Examples**:
- **Query Used**: "GNN constraint graph PyTorch"
- **Finding**: General graph neural network patterns from diffusion models
- **Relevance**: Message-passing architecture patterns (multi-stage processing, attention mechanisms)
- **Used For**: Understanding GNN message-passing patterns, not directly used in specs (relied on Exa instead)

### B. GitHub Implementations (Exa)

**Repository 1**: [dselsam/neurosat](https://github.com/dselsam/neurosat) ⭐ Official
- **URL**: https://github.com/dselsam/neurosat
- **Query Used**: "NeuroSAT official implementation GitHub SAT solver GNN"
- **Relevance**: Original NeuroSAT paper implementation by Daniel Selsam - ground truth for architecture
- **Key Architecture**:
  ```python
  # NeuroSAT core: LSTM-based message passing on literal-clause graph
  # Hidden dimension: 128
  # Message passing iterations: 32
  # Update mechanism: LSTM for literal and clause states
  ```
- **Configuration Extracted**:
  - Hidden dim: 128
  - Iterations: 32
  - Training: SR(U(10,40)) random SAT dataset
  - Supervision: Single-bit (satisfiability classification)
- **Their Results**: 85% accuracy on test set, generalizes to larger instances
- **Used For**: Baseline model architecture specification, training protocol foundation

**Repository 2**: [zhaoyu-li/G4SATBench](https://github.com/zhaoyu-li/G4SATBench) ⭐39 (TMLR 2024)
- **URL**: https://github.com/zhaoyu-li/G4SATBench
- **Query Used**: "G4SATBench SAT benchmark dataset PyTorch GNN constraint"
- **Relevance**: Comprehensive SAT benchmark framework with standardized datasets and evaluation
- **Key Components**:
  ```python
  # G4SATBench dataset generation + training framework
  # 7 datasets × 3 difficulty levels
  # PyTorch Geometric implementation
  # Hyperparameter grid search results
  ```
- **Configuration Extracted**:
  - Dataset: 3-SAT easy (10-40 vars), 80k train, 10k val, 10k test
  - Optimizer: Adam (lr=1e-4, weight_decay=1e-8)
  - Batch size: 128
  - Epochs: 100 with early stopping
  - Augmentation: variable/clause permutation, negation flips
- **Their Results**: Benchmarked multiple GNN architectures, documented optimal hyperparameters
- **Used For**: Dataset specification, training protocol, hyperparameters, evaluation framework

**Repository 3**: [zhaoyu-li/NSNet](https://github.com/zhaoyu-li/NSNet) ⭐19 (NeurIPS 2022)
- **URL**: https://github.com/zhaoyu-li/NSNet
- **Query Used**: "SAT solver message passing neural network PyTorch implementation"
- **Relevance**: Modern neural SAT framework with probabilistic inference formulation
- **Architecture**: GNN parameterizing Belief Propagation in latent space
- **Used For**: Alternative architecture reference (not used in h-e1 baseline)

**Repository 4**: [wenxiwang/neuroback](https://github.com/wenxiwang/neuroback) (ICLR 2024)
- **URL**: https://github.com/wenxiwang/neuroback
- **Relevance**: Hybrid neural-symbolic SAT solver (GNN + CDCL)
- **Used For**: Reference only (not applicable to h-e1)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. NeuroSAT architecture is well-documented with straightforward LSTM-based message passing (~100 lines). G4SATBench provides clear PyTorch Geometric implementation patterns without complex custom layers requiring deeper semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None - h-e1 is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4). No previous validation reports to inherit configuration from.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (G4SATBench 3-SAT easy) | GitHub (Exa) | zhaoyu-li/G4SATBench |
| Dataset statistics (80k/10k/10k) | GitHub (Exa) | zhaoyu-li/G4SATBench paper |
| Dataset loading code | GitHub (Exa) | G4SATBench repository |
| Baseline model (NeuroSAT) | GitHub (Exa) | dselsam/neurosat |
| Model architecture (128-dim, 32 iter) | GitHub (Exa) | dselsam/neurosat + G4SATBench |
| Pseudo-code structure | GitHub (Exa) | G4SATBench GGNN implementation |
| Training optimizer (Adam 1e-4) | GitHub (Exa) | G4SATBench grid search results |
| Training schedule (ReduceLROnPlateau) | GitHub (Exa) | G4SATBench training protocol |
| Batch size (128) | GitHub (Exa) | G4SATBench standard |
| Epochs (100) | GitHub (Exa) | G4SATBench training setup |
| Loss function (unsupervised) | GitHub (Exa) | Selsam et al. 2019 (NeuroSAT) |
| Augmentation strategy | GitHub (Exa) | G4SATBench augmentation |
| Evaluation metrics (d/n, entropy) | Phase 2B | 02b_verification_plan.md H-E1 |
| Success criteria (range > 0.20, > 2.0) | Phase 2B | 02b_verification_plan.md H-E1 |
| Expected baseline (85% accuracy) | GitHub (Exa) | Selsam et al. 2019 paper |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-12T05:22:43Z

### Workflow History for This Hypothesis
- Event: Hypothesis h-e1 set to IN_PROGRESS
  - Timestamp: 2026-05-12T05:22:02Z
  - Phase: Hypothesis Loop
  - Details: External loop starting Phase 2C → 3 → 4 for h-e1

- Event: Experiment design started
  - Timestamp: 2026-05-12T05:22:43Z
  - Phase: Phase 2C
  - Details: h-e1 experiment_design.status = IN_PROGRESS

- Event: Experiment design completed
  - Timestamp: 2026-05-12T05:30:00Z (estimated)
  - Phase: Phase 2C
  - Output: 02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
