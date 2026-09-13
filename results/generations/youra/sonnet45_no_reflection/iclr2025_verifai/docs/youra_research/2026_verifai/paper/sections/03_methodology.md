# Methodology

We designed a dual-metric gate to test whether baseline NeuroSAT generates heterogeneous near-solutions suitable for basin recovery. The key insight is that solution diversity has two independent dimensions: **distance from ground truth** (how far solutions are from correct assignments) and **structure of violations** (how constraints are violated). Prior work measured only overall satisfaction rates, conflating these dimensions. Our framework tests them separately.

## Dual-Metric Heterogeneity Framework

A solution to a SAT instance is represented as a binary variable assignment. For an instance with $n$ variables and ground truth assignment $x^*$, a generated assignment $\hat{x}$ has:

**Normalized Hamming distance**: 
$$d/n = \frac{1}{n} \sum_{i=1}^n \mathbb{1}[\hat{x}_i \neq x^*_i]$$

This measures how far the solution is from ground truth. Values range from 0 (perfect match) to 1 (complete disagreement).

**Violation entropy**:
$$H = -\sum_{j=1}^m p_j \log_2 p_j$$

where $p_j$ is the proportion of total violations occurring in clause $j$, and $m$ is the number of clauses. This measures how diffusely violations are distributed across the constraint space. High entropy ($H > 2.5$) indicates violations spread across many clauses; low entropy ($H < 1.5$) indicates concentrated violations.

Our dual-metric gate requires:
- **d/n range > 0.20**: Solutions must span at least 20 percentage points in distance from ground truth
- **Entropy range > 2.0**: Violations must exhibit at least 2.0 bits of structural variation across instances

If both criteria pass, the architecture generates heterogeneous near-solutions suitable for stratification-based refinement. If only one passes, we diagnose which dimension of diversity is missing.

## Baseline Architecture

We implement baseline NeuroSAT [Selsam et al., 2019] without modifications to establish foundation behavior before testing architectural variants. The architecture operates on a bipartite literal-clause graph:

**Message-passing rounds**: For $T = 32$ iterations:
1. **Literal-to-clause messages**: Each literal $\ell$ sends its embedding through an MLP to connected clauses
2. **Clause-to-literal messages**: Each clause $c$ aggregates literal messages, updates via LSTM, sends to connected literals
3. **Literal updates**: Each literal aggregates clause messages, updates via LSTM

**Initialization**: Literal and clause embeddings (128-dimensional) are learned parameters initialized with $\mathcal{N}(0, 0.1)$. Critically, this is a **single initialization point** shared across all instances—the same learned embedding initializes message-passing regardless of instance structure.

**Decoding**: After $T$ rounds, literal embeddings are thresholded to produce binary assignments. No explicit diversity mechanism, stochastic sampling, or ensemble exists in the baseline architecture.

**Training objective**: Unsupervised loss for SAT/UNSAT classification:
$$\mathcal{L} = -\log p(\text{label} \mid \text{final embeddings})$$

where label is 1 for satisfiable instances, 0 for unsatisfiable. This single-bit supervision does not directly optimize assignment quality or violation diversity.

## Why This Design Tests Our Hypothesis

The dual-metric gate directly tests whether deterministic LSTM message-passing with single initialization generates the diversity needed for basin recovery. If the architecture passes both metrics, the hypothesis proceeds to test Stage 2 refinement mechanisms (H-M1 through H-M4). If one metric fails, we diagnose the architectural limitation.

**Intuition**: Think of solutions as points in a two-dimensional space. The d/n axis measures "how wrong" solutions are; the entropy axis measures "how they are wrong." An architecture that spreads points along the d/n axis but clusters them on the entropy axis has distance diversity without structural diversity. This asymmetry would indicate that the model explores different solution qualities but uses uniform violation strategies.

## Dataset and Evaluation

**G4SATBench 3-SAT Easy**: We use 3-SAT instances with 10-40 variables, clause-to-variable ratio 4.2-4.3. This difficulty level enables controlled measurement with ground truth while maintaining realistic constraint satisfaction challenges.

**Training**: 20 instances (proof-of-concept scale, full dataset has 80k). Adam optimizer with learning rate $10^{-4}$, ReduceLROnPlateau scheduler, early stopping patience 20 epochs.

**Evaluation**: 8 satisfiable instances from the test set (2 UNSAT instances filtered because d/n and entropy are undefined without ground truth). For each instance, we:
1. Generate assignment via trained NeuroSAT
2. Compute d/n against ground truth
3. Compute violation entropy H from clause violation distribution
4. Measure d/n range (Q3 - Q1) and entropy range across instances

**Statistical Analysis**: We report distribution statistics (mean, std, quartiles, range) and compare against gate thresholds. With $n=8$ instances, we have limited statistical power for variance tests but sufficient signal to diagnose clear asymmetries where one metric passes decisively while the other fails decisively.
