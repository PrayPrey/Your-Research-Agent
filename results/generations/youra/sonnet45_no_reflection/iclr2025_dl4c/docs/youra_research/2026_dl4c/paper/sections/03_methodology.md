# Methodology

Our methodology is designed to distinguish statistical independence from directional factorization in multi-objective code modifications. The key insight is that these are distinct properties requiring different validation approaches: covariance magnitude tests independence, while spectral analysis with permutation testing reveals geometric structure.

## Overview

To validate whether aspect-dominant structure exists in real code modifications, we conduct a multi-stage analysis pipeline:

1. **Data Collection:** Mine 10,000 minimal-difference commits from GitHub repositories with aspect labels (security, refactor, performance, bugfix)
2. **Metric Computation:** Measure quality changes across four dimensions (Δcorrectness, Δquality, Δsecurity, Δefficiency) for each commit
3. **Confound Regression:** Remove spurious structure from confounding variables (edit size, file entropy) to isolate outcome-space geometry
4. **Spectral Analysis:** Perform eigendecomposition of residual covariance to test for 4D aspect-dominant structure (spectral gap λ₄/λ₅>2.0)
5. **Statistical Validation:** Permutation testing (1000 shuffles) to rule out chance, directional stability analysis, and leave-one-repo-out cross-validation

This pipeline enables us to make precise claims: if spectral gap >2.0 and permutation p<0.05, aspect-dominant structure exists. If coupling ≤0.2 but gap ≤2.0, we have independence without factorization—the geometry is spherical, not aspect-aligned.

## Dataset Construction

### Commit Selection Criteria

We filter GitHub commits to isolate minimal-difference modifications that approximate single-aspect developer intent:

- **AST Distance <20 nodes:** Ensures changes are focused rather than multi-faceted refactors. Computed using tree-sitter parsers to measure syntactic edit distance.
- **Aspect Labels:** Commit messages must contain aspect-specific keywords: "security", "vulnerability", "CVE" (security); "refactor", "cleanup", "restructure" (quality); "performance", "optimize", "cache" (efficiency); "fix", "bug", "error" (correctness).
- **File Type Filter:** Python (`.py`) and JavaScript (`.js`) source files only. Excludes documentation, configuration, and test files to focus on production code.
- **Temporal Range:** Last 3 years (2023-2026) to capture contemporary development practices.
- **Exclusions:** Merge commits, bot-generated commits, and dependency updates.

**Rationale:** Minimal-difference commits reduce confounds from simultaneous multi-aspect changes. Commit message labels provide noisy but scalable aspect annotations. While expert validation (Phase 1B) would measure label purity, our permutation test design is robust to label noise—if labels are uninformative, the test will detect it.

### Repository Sampling

Target 500-1000 repositories with diverse characteristics:
- **Popularity Range:** Mix of high-star (>10K stars), medium (1K-10K), and emerging projects to avoid sampling bias toward mature codebases
- **Domain Coverage:** Web frameworks, data science libraries, system utilities, security tools to test cross-domain robustness
- **Activity Level:** Active development (commits within last 6 months) ensures relevance to current practices

## Quality Metric Computation

For each commit, we compute pre→post metric changes to isolate the causal effect of the modification:

### Δcorrectness (Test Pass Rate Change)
```
Δcorrectness = (tests_passing_post / tests_total) - (tests_passing_pre / tests_total)
```
Measures functional correctness via unit test execution (pytest for Python, jest for JavaScript). Range: [-1, 1].

**Rationale:** Execution-based correctness is standard in code generation evaluation [PPOCoder, HumanEval]. Direct measure of functional impact.

### Δquality (SonarQube Maintainability)
```
Δquality = maintainability_rating_post - maintainability_rating_pre
```
SonarQube computes maintainability from code smells, complexity, duplication. Rating scale: A (best) to E (worst), converted to numeric [-4, 4].

**Rationale:** Aggregates multiple quality dimensions (readability, complexity, technical debt) into single metric. Industry-standard tool ensures reproducibility.

### Δsecurity (CodeQL Alert Count Change)
```
Δsecurity = -(alerts_post - alerts_pre)
```
Negative sign ensures positive Δ means improvement. CodeQL detects vulnerabilities (SQL injection, XSS, path traversal, authentication issues).

**Rationale:** Static analysis provides scalable security assessment without requiring security expertise. Negative result (more alerts) reflects security degradation.

### Δefficiency (Runtime Performance Change)
```
Δefficiency = (runtime_pre - runtime_post) / runtime_pre
```
Percentage improvement in benchmark runtime via pytest-benchmark. Positive values indicate speedup.

**Rationale:** Captures computational efficiency—critical for production systems. Benchmark-based measurement is reproducible and objective.

## Residual Covariance Analysis

Raw covariance matrices conflate outcome-space structure with confounding factors. We regress out two primary confounds before spectral analysis:

### Confound Variables
- **Edit Size (AST nodes changed):** Large edits may affect multiple metrics mechanically (more code → more potential bugs, complexity increases)
- **File Entropy (H = -Σ p_i log p_i for token frequencies):** File complexity influences baseline metric values and change magnitudes

### Regression Model
For each metric dimension d ∈ {correctness, quality, security, efficiency}:
```
Δd = β₀ + β₁·edit_size + β₂·file_entropy + ε
Residual_d = ε (unexplained variance)
```

We compute residual covariance matrix Σ_residual from regression residuals ε. This isolates outcome-space geometry from edit-size and complexity artifacts.

**Rationale:** Without confound regression, large edits might show spurious factorization (edit size correlates with specific aspects). Residual analysis ensures we test structure in outcome space, not confound space.

## Spectral Decomposition

We perform eigendecomposition of the residual covariance matrix to test for aspect-dominant structure:

```
Σ_residual = VΛV^T
```
where V are eigenvectors (principal directions), Λ = diag(λ₁, λ₂, λ₃, λ₄) are eigenvalues (variance along each direction), sorted λ₁ ≥ λ₂ ≥ λ₃ ≥ λ₄.

### Spectral Gap Metric
```
spectral_gap = λ₄ / (λ₅ + ε)
```
For 4D data, λ₅ doesn't exist; we use ε=0.01 for numerical stability. The gap measures separation between signal (first 4 eigenvalues) and noise.

**Interpretation:**
- **Gap > 2.0:** Sharp 4D structure—first four directions dominate, suggesting aspect-aligned geometry
- **Gap ≈ 1.0-1.5:** Gradual decay—spherical geometry, no natural coordinate system
- **Gap < 1.0:** Underdetermined—less than 4 dimensions of variation

**Threshold Justification:** Gap > 2.0 is standard in spectral clustering literature [Ng et al., 2001; von Luxburg, 2007] for identifying clear dimensional structure. Lower thresholds (e.g., 1.5) would still fail in our data, so choice is conservative.

### Cross-Aspect Coupling Measurement
```
coupling = median(|Σ_ij|) / median(|Σ_ii|) for i ≠ j
```
Median ratio of off-diagonal (cross-aspect effects) to diagonal (primary effects) terms. Coupling ≤0.2 indicates independence.

**Rationale:** Tests whether metrics are uncorrelated. Necessary but not sufficient for factorization—can have low coupling with spherical geometry.

## Statistical Validation via Permutation Testing

To rule out chance findings, we test whether observed spectral gap is statistically significant:

### Permutation Procedure
```
FOR iteration k = 1 to 1000:
  1. Randomly shuffle aspect labels across commits
  2. Recompute residual covariance for shuffled data
  3. Compute spectral_gap_null[k]

p_value = (count(spectral_gap_null >= spectral_gap_observed)) / 1000
```

**Null Hypothesis:** Aspect labels are unrelated to covariance structure. Shuffling breaks label-outcome correspondence while preserving marginal distributions.

**Interpretation:**
- **p < 0.05:** Observed gap exceeds 95% of null distribution—labels are informative
- **p > 0.5:** Observed gap is typical of random null—labels provide zero information

**Rationale:** Non-parametric test robust to distributional assumptions. Directly tests our claim: do aspect labels correspond to eigenvector structure? If p>0.5, the answer is definitively no.

## Directional Stability Analysis

Even without significant spectral gap, eigenvectors might align with aspect-specific directions. We test this via on-axis projection:

### On-Axis Projection Test
For each aspect a and its corresponding eigenvector v_a:
```
z_score_a = (projection_observed_a - μ_null) / σ_null
```
where projection measures alignment between aspect-specific commit changes and eigenvector direction.

**Threshold:** z > 2.0 indicates significant alignment (2σ above random).

**Rationale:** Tests whether eigenvectors, even if not gap-separated, correspond to meaningful aspect directions. Negative or near-zero z-scores indicate arbitrary rotation, not natural axes.

## Cross-Validation for Robustness

To ensure structure isn't domain-specific artifact, we perform Leave-One-Repo-Out (LORO) cross-validation:

### LORO Protocol
```
FOR each repository R in dataset:
  1. Train eigendecomposition on all commits except R
  2. Compute eigenvectors V_train
  3. Test on repository R: compute V_test
  4. Measure alignment: cosine_similarity(V_train, V_test)

consistency = mean(alignment across all repositories)
```

**Threshold:** Consistency ≥0.7 indicates robust structure across domains.

**Rationale:** If eigenspace changes dramatically when excluding specific repositories, structure is domain-specific rather than universal. Low consistency (≈0.5) suggests overfitting to noise.

## Implementation Details

Our analysis pipeline is implemented in Python with the following key dependencies:
- **PyGitHub / PyDriller:** Repository mining and commit extraction
- **tree-sitter:** AST parsing for edit distance computation
- **SonarQube Scanner:** Quality metric computation via Docker instance
- **CodeQL CLI:** Security vulnerability detection
- **pytest-benchmark:** Runtime performance measurement
- **NumPy / SciPy:** Covariance estimation and eigendecomposition
- **scikit-learn:** Regression models for confound removal

All code is available in the supplementary materials for reproducibility. Random seed 42 is used throughout for deterministic results.

## Validation Criteria Summary

Our methodology produces five validation checks with pre-registered thresholds:

| Criterion | Metric | Threshold | Purpose |
|-----------|--------|-----------|---------|
| **C1: Independence** | Cross-aspect coupling | ≤0.2 | Confirm metrics measure distinct constructs |
| **C2: Spectral Gap** | λ₄/λ₅ | >2.0 | Test for 4D aspect-dominant structure |
| **C3: Label Informativeness** | Permutation p-value | <0.05 | Rule out chance / verify labels meaningful |
| **C4: Directional Alignment** | On-axis z-score | >2.0 | Test eigenvector-aspect correspondence |
| **C5: Robustness** | LORO consistency | ≥0.7 | Ensure structure generalizes across repos |

**Decision Rule:** If C1 passes (independence) but C2-C5 fail, we conclude: **independence without factorization**—metrics are uncorrelated but geometry is spherical. This would refute the architectural factorization assumption and support simpler methods (weighted scalarization).
