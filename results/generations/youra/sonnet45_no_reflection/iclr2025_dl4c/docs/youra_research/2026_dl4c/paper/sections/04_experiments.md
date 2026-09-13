# Experimental Setup

Our experiments are designed to test five specific claims about aspect-dominant structure in code modifications, each with pre-registered success criteria. We emphasize that this evaluation used **synthetic test data** for code validation purposes—real GitHub data collection is required for scientific publication, but the experimental design and statistical rigor demonstrated here provide a validated template for future work.

## Research Questions

We structure our evaluation around five complementary questions:

**RQ1: Do quality metrics exhibit statistical independence?**
- **Test:** Compute cross-aspect coupling from residual covariance matrix
- **Success Criterion:** Coupling ≤0.2 (median off-diagonal / diagonal ratio)
- **Rationale:** Independence is necessary (but not sufficient) for factorization

**RQ2: Does covariance exhibit 4D aspect-dominant structure?**
- **Test:** Eigendecomposition + spectral gap measurement (λ₄/λ₅)
- **Success Criterion:** Gap >2.0 indicating clear 4-dimensional structure
- **Rationale:** Tests whether eigenspectrum has sharp "cliff" after 4th dimension

**RQ3: Do aspect labels correspond to covariance structure?**
- **Test:** Permutation test with 1000 label shuffles
- **Success Criterion:** p<0.05 (observed gap exceeds 95% of null distribution)
- **Rationale:** Directly tests whether commit message labels are informative

**RQ4: Are eigenvectors aligned with aspect-specific directions?**
- **Test:** On-axis projection z-scores per aspect
- **Success Criterion:** z>2.0 for at least 3/4 aspects (2σ above random)
- **Rationale:** Even without gap, eigenvectors might correspond to aspects

**RQ5: Is structure robust across repositories?**
- **Test:** Leave-one-repo-out cross-validation, eigenspace alignment
- **Success Criterion:** Consistency ≥0.7 across data partitions
- **Rationale:** Ensures structure is universal, not domain-specific artifact

## Dataset Specification

### Synthetic Test Data (Current Evaluation)

For pipeline validation and proof-of-concept demonstration, we generated synthetic test data matching the structure of real commit data:

- **Size:** 10,000 commits
- **Dimensions:** 4 quality metrics (Δcorrectness, Δquality, Δsecurity, Δefficiency)
- **Aspect Labels:** Balanced distribution (2,500 per aspect: security, refactor, performance, bugfix)
- **Random Seed:** 42 (reproducible)
- **Generation Method:** Randomized covariance structure without guaranteed aspect-dominant geometry

**Purpose:** Demonstrate that analysis pipeline executes correctly, gate evaluation logic functions properly, and permutation testing detects lack of signal when present.

**Limitations:** Results demonstrate technical functionality but have **zero scientific validity** for claims about real developer behavior. Real GitHub data collection (Phase 1A: 5 days mining, 22 hours metric computation) is required before publication.

### Real Data Collection Protocol (Future Work)

For scientific publication, the following real data collection is required:

**Phase 1A: Commit Mining (5 days)**
- Source: GitHub API (PyGitHub, PyDriller)
- Target: 10,000 minimal-diff commits (AST distance <20 nodes)
- Filters: Python/JavaScript files, aspect-labeled commits, active repositories (2023-2026)
- Repository sampling: 500-1000 diverse repositories (popularity, domain, activity)

**Phase 1B: Metric Computation (22 hours)**
- Δcorrectness: pytest/jest test pass rate changes
- Δquality: SonarQube maintainability rating changes
- Δsecurity: CodeQL alert count changes
- Δefficiency: pytest-benchmark runtime changes
- Infrastructure: SonarQube Docker instance, CodeQL CLI, 16-core CPU for parallelization

**Phase 1C: Label Validation (2 days)**
- Expert annotation: n=500 commits with 3 annotators
- Measure: Inter-rater agreement (Fleiss' kappa >0.6), commit purity (>70% single-aspect)
- Mitigation: If purity 60-70%, apply mixture modeling with expert-weighted covariance correction

## Evaluation Protocol

### Preprocessing

1. **Confound Regression:** Remove variance explained by edit size and file entropy
2. **Residual Covariance:** Compute covariance matrix from regression residuals
3. **Normalization:** No normalization applied—preserve actual variance structure

### Primary Analysis

**Spectral Decomposition:**
```python
eigenvalues, eigenvectors = np.linalg.eigh(residual_covariance)
eigenvalues = np.sort(eigenvalues)[::-1]  # Descending order
spectral_gap = eigenvalues[3] / (eigenvalues[4] + 1e-2)  # λ₄/λ₅ with numerical stability
```

**Coupling Measurement:**
```python
diagonal = np.diag(residual_covariance)
off_diagonal = residual_covariance[np.triu_indices(4, k=1)]
coupling = np.median(np.abs(off_diagonal)) / np.median(np.abs(diagonal))
```

### Statistical Validation

**Permutation Test (1000 iterations):**
```python
null_gaps = []
for i in range(1000):
    shuffled_labels = np.random.permutation(aspect_labels)
    residual_cov_null = compute_residual_covariance(data, shuffled_labels)
    eigenvalues_null = np.linalg.eigvalsh(residual_cov_null)
    null_gaps.append(eigenvalues_null[3] / (eigenvalues_null[4] + 1e-2))

p_value = (np.sum(null_gaps >= observed_gap) + 1) / (1000 + 1)
```

**Directional Stability:**
```python
for aspect in ['security', 'refactor', 'performance', 'bugfix']:
    aspect_commits = data[labels == aspect]
    mean_direction = np.mean(aspect_commits, axis=0)
    projection = np.dot(mean_direction, eigenvectors[:, aspect_idx])
    z_score = (projection - null_mean) / null_std
```

**LORO Cross-Validation:**
```python
alignments = []
for repo in repositories:
    train_data = data[repos != repo]
    test_data = data[repos == repo]
    
    eigenvectors_train = compute_eigenvectors(train_data)
    eigenvectors_test = compute_eigenvectors(test_data)
    
    alignment = cosine_similarity(eigenvectors_train, eigenvectors_test)
    alignments.append(alignment)

consistency = np.mean(alignments)
```

## Baseline Comparisons

Since this is empirical validation rather than method comparison, we have **no baselines**. The permutation test provides the null distribution. However, we contextualize our findings against:

- **Multi-task learning expectations:** If code followed MTL patterns from vision/NLP, we'd expect gap >2.0
- **Random baseline:** Permutation null distribution (mean gap ≈1.5-1.6 for 4D data)
- **Independence-only hypothesis:** Diagonal-dominant covariance (coupling ≈0) without structure

## Computational Resources

- **Hardware:** Single NVIDIA GPU (for potential neural network baselines, not used in current analysis)
- **Software:** Python 3.9, NumPy 1.24, SciPy 1.10, scikit-learn 1.2
- **Runtime:** Spectral analysis: <1 minute, Permutation test: ~5 minutes (1000 iterations)
- **Storage:** Synthetic dataset: 80MB, Real dataset (future): ~500GB (commit diffs + metrics)

## Reproducibility

All code, synthetic test data generator, and analysis scripts are available in supplementary materials. Real GitHub data (when collected) will be released under CC-BY-4.0 license with:
- Commit metadata (SHA, repository, timestamp, message)
- Pre/post file pairs (anonymized)
- Computed metric values (Δcorrectness, Δquality, Δsecurity, Δefficiency)
- Excluded: Personally identifiable information (author names, emails)

Random seed 42 ensures deterministic results across runs.
