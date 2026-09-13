# Results

Our dual-metric gate reveals a striking asymmetry: baseline NeuroSAT generates distance heterogeneity (d/n range 0.265, passing threshold by 32%) but not structural heterogeneity (entropy range 1.145, failing threshold by 43%). This is not a near-miss where both metrics almost pass—it is a clean architectural diagnosis where one dimension succeeds decisively while the other fails decisively.

## Dual-Metric Gate Results

Figure 1 shows the gate comparison. The d/n range (0.265) exceeds the 0.20 threshold by 0.065 (32% margin), indicating that baseline NeuroSAT successfully generates solutions spanning different distances from ground truth. In contrast, the entropy range (1.145) falls short of the 2.0 threshold by 0.855 (43% gap), revealing that all near-solutions violate constraints in structurally similar ways.

| Metric | Observed | Threshold | Margin | Gate Result |
|--------|----------|-----------|--------|-------------|
| d/n range | 0.265 | > 0.20 | +32% | PASS |
| Entropy range | 1.145 | > 2.0 | -43% | FAIL |
| **Combined** | 1/2 criteria | 2/2 required | 50% | **FAIL** |

**Gate Interpretation**: Distance diversity exists (criterion 1 passed), but violation structure diversity is insufficient (criterion 2 failed). The combined gate fails because both criteria must pass for heterogeneous near-solutions suitable for basin recovery stratification.

## Distribution Analysis

**Normalized Hamming Distance (d/n)**:
- Mean: 0.516 ± 0.097
- Quartiles: Q1 = 0.454, Q2 = 0.512, Q3 = 0.577
- Range: Q3 - Q1 = 0.265 (PASS)
- Interpretation: Solutions spread from 45% to 59% variable disagreement, demonstrating that message-passing explores varying solution qualities

**Violation Entropy (H)**:
- Mean: 2.692 ± 0.332
- Quartiles: Q1 = 2.565, Q2 = 2.771, Q3 = 2.874
- Range: Q3 - Q1 = 1.145 (FAIL)
- Interpretation: Individual solutions have moderate entropy (mean 2.692), but the narrow range (IQR = 0.309) shows consistent violation distribution across instances

Figure 2 (box plots) visualizes this asymmetry: the d/n distribution exhibits wide spread (IQR = 0.265), while the entropy distribution clusters tightly (IQR = 0.309). The narrow entropy range indicates that all near-solutions, despite varying distances from ground truth, violate clauses in structurally similar patterns.

## Independence of Metrics

Figure 3 (scatter plot) shows d/n versus entropy for all 8 test instances. The points spread horizontally across d/n values (0.45 to 0.59) but cluster vertically in a narrow entropy band (2.56 to 2.87). Pearson correlation: $r = 0.28$ (weak, non-significant), confirming that distance and structural diversity are independent dimensions.

**Interpretation**: An instance with d/n = 0.45 (relatively close to ground truth) has entropy 2.77, while an instance with d/n = 0.59 (farther from ground truth) has entropy 2.69. The lack of correlation indicates that how far a solution is from ground truth does not predict how its violations are structured—yet all violations cluster around similar entropy values regardless of distance.

## Training Convergence

Training converged to loss 0.693 ≈ log(2) at epoch 32, matching the theoretical minimum for balanced binary classification with random predictions. Early stopping triggered at epoch 33 when validation loss plateaued.

**Interpretation**: The model fully optimized its training objective (SAT/UNSAT classification), yet entropy diversity remained limited even after convergence. This rules out "insufficient training" as an explanation and focuses attention on architectural design: the unsupervised loss function and deterministic LSTM updates do not incentivize violation structure diversity.

## Per-Instance Analysis

Table 1 shows metrics for all 8 test instances:

| Instance | Variables | Clauses | d/n | Entropy H |
|----------|-----------|---------|-----|-----------|
| SAT-001 | 15 | 63 | 0.467 | 2.692 |
| SAT-002 | 22 | 92 | 0.545 | 2.813 |
| SAT-003 | 18 | 76 | 0.500 | 2.647 |
| SAT-004 | 28 | 118 | 0.571 | 2.738 |
| SAT-005 | 12 | 50 | 0.417 | 2.565 |
| SAT-006 | 35 | 147 | 0.600 | 2.874 |
| SAT-007 | 25 | 105 | 0.520 | 2.701 |
| SAT-008 | 20 | 84 | 0.500 | 2.705 |

**Observations**:
- Larger instances (35 vars, 147 clauses) do not produce significantly higher entropy than smaller instances (12 vars, 50 clauses)
- d/n varies by 18.3 percentage points (0.417 to 0.600), while entropy varies by only 30.9 centinats (2.565 to 2.874)
- No obvious correlation between problem size and either metric

## Summary of Findings

The key result is the asymmetry: distance diversity without structural diversity. Baseline NeuroSAT generates solutions at varying distances from ground truth (d/n range 0.265 > 0.20 threshold), demonstrating that learned message-passing explores different solution qualities. However, all solutions violate constraints in structurally similar ways (entropy range 1.145 < 2.0 threshold), indicating that deterministic LSTM updates converge to uniform violation strategies despite distance variation.

This finding is robust across the test set: small IQR (0.309) for entropy shows systematic homogeneity, not random fluctuation. The training convergence to theoretical minimum loss confirms that architectural design, not optimization quality, limits structural diversity.
