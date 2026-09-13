# Experiment Brief: H-E1 Aspect-Dominant Structure Existence

**Generated:** 2026-05-11  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Brief Level:** 1.5 (Implementation-ready specification)

---

## 1. Executive Summary

**Objective:** Validate that human expert code modifications exhibit aspect-dominant directional structure across quality dimensions (correctness, quality, security, efficiency) through spectral decomposition of residual covariance matrices on GitHub commit data.

**Success Criteria:**
- Primary: Cross-aspect coupling ≤0.2× primary effect (95% CI), spectral gap λ₄/λ₅>2.0 (exceeds 95th percentile of permutation null), on-axis projection z-score >2.0
- Secondary: Commit purity >70%, metric validation passed (ICC≥0.8, r≥0.7 with expert judgment)

**Dataset:** 10,000 minimal-diff commits from GitHub repositories with aspect labels (security, refactor, performance, bugfix), filtered for AST distance <20

**Failure Response:** If spectral gap ≤2.0 or coupling >0.3×, ABORT entire pipeline → Publish negative result on intrinsic entanglement of multi-objective code alignment

---

## 2. Hypothesis Statement

**H-E1:** Under multi-objective code generation contexts with GitHub commit data (10K minimal-diff commits), if human expert modifications are analyzed via spectral decomposition of residual covariance matrices, then aspect-dominant directional structure will emerge with median cross-aspect coupling ≤0.2× primary effect and spectral gap λ₄/λ₅>2.0, because developers cognitively factorize programming concerns into separable dimensions.

**Rationale:** This hypothesis validates the foundational empirical assumption that human code modifications exhibit separable structure across quality aspects. Without this separability in real data, the entire architectural factorization approach (H-M-Integrated) lacks empirical grounding.

---

## 3. Dataset Specification

### 3.1 Primary Dataset

| Attribute | Specification |
|-----------|---------------|
| **Name** | GitHub Minimal-Diff Commit Corpus |
| **Type** | standard (real-world commit data) |
| **Source** | GitHub API (public repositories) |
| **Size** | 10,000 commits (target) |
| **Filters** | AST distance <20, aspect-labeled (security/refactor/performance/bugfix) |
| **Split** | Full corpus analysis (no train/val/test - this is analysis not training) |
| **Access** | GitHub REST API v3 + GraphQL API |

### 3.2 Data Collection Protocol

**Step 1: Repository Selection**
- Target: 500-1000 popular Python/JavaScript repositories
- Criteria: ≥1000 stars, active development (commits in last 6 months), non-tutorial projects
- Sources: GitHub trending, Awesome lists, top PyPI packages
- Tools: PyGitHub, PyDriller, GitHub GraphQL API

**Step 2: Commit Filtering**
- Time range: Last 3 years (2023-2026) to ensure contemporary practices
- Diff size: 1-20 AST nodes changed (minimal-diff constraint)
- File types: `.py`, `.js`, `.java` source files only
- Exclude: Merge commits, bot commits, documentation-only changes
- AST distance calculation: Use tree-sitter parsers to compute edit distance

**Step 3: Aspect Labeling**
- **Automatic labeling:** Commit message keyword matching
  - Security: "security", "vulnerability", "CVE", "XSS", "injection", "auth"
  - Refactor: "refactor", "cleanup", "rename", "restructure", "organize"
  - Performance: "performance", "optimize", "speed", "cache", "efficient"
  - Bugfix: "fix", "bug", "error", "crash", "issue #"
- **Expert validation:** n=500 subset with 3 expert annotators
  - Measure inter-rater agreement (Fleiss' kappa >0.6)
  - Assess purity: % where one aspect dominates (target >70%)
  - Provide purity-weighted covariance correction if 60-70%

**Step 4: Metric Computation**
For each commit (pre→post file pair), compute:
- **Δcorrectness:** Test pass rate change (pytest/jest on affected test suite)
- **Δquality:** SonarQube maintainability rating change (A→B = -1, B→A = +1)
- **Δsecurity:** CodeQL alert count change (new alerts = negative)
- **Δefficiency:** pytest-benchmark runtime change (% improvement)

### 3.3 Validation Dataset

| Attribute | Specification |
|-----------|---------------|
| **Name** | Expert-Annotated Purity Validation Subset |
| **Type** | custom (expert-labeled) |
| **Size** | 500 commits |
| **Purpose** | Measure commit purity (single-aspect intent) and label quality |
| **Annotation** | 3 experts rate each commit's primary/secondary aspects (5-point scale) |
| **Output** | Purity score, inter-rater agreement, aspect confusion matrix |

### 3.4 Metric Reliability Dataset

| Attribute | Specification |
|-----------|---------------|
| **Name** | Metric Validation Corpus |
| **Type** | custom (test-retest reliability) |
| **Size** | 200 commits |
| **Purpose** | Validate ICC≥0.8, construct validity r≥0.7 vs expert judgment |
| **Protocol** | Run metrics twice (1 week apart), collect expert ratings on quality/security/efficiency |
| **Analysis** | Intraclass correlation, Pearson correlation with expert consensus |

---

## 4. Baseline Methods

**Note:** H-E1 is an empirical analysis experiment, not a model training task. No baselines are needed for hypothesis validation. The "baseline" is the null hypothesis H0 (flat eigenspectrum, no separability).

**Comparison Strategy:**
- **Permutation test baseline:** Shuffle aspect labels 1000 times, recompute spectral gap each time
- **Random geometry baseline:** Generate 1000 synthetic covariance matrices with same trace, compute spectral gaps
- **Success criterion:** Observed λ₄/λ₅ must exceed 95th percentile of both null distributions

---

## 5. Experimental Design

### 5.1 Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Metric Validation (Week 0, 2-3 days)              │
├─────────────────────────────────────────────────────────────┤
│  1. Collect n=200 commits for test-retest reliability       │
│  2. Run SonarQube/CodeQL/pytest-benchmark twice (1 week gap)│
│  3. Collect expert ratings (n=3 experts × 200 commits)      │
│  4. Compute ICC (target ≥0.8) and r vs experts (≥0.7)      │
│  5. DROP metrics that fail validation, proceed with ≥3/4     │
└─────────────────────────────────────────────────────────────┘
         ↓ (IF ≥3/4 metrics pass)
┌─────────────────────────────────────────────────────────────┐
│  Phase 1A: Data Collection (Week 1, ~5 days)                │
├─────────────────────────────────────────────────────────────┤
│  1. Mine 10K minimal-diff commits from GitHub API           │
│  2. Filter by AST distance <20, aspect labels               │
│  3. Download pre/post file pairs for each commit            │
│  4. Compute Δcorrectness, Δquality, Δsecurity, Δefficiency │
│  5. Build 10K × 4 outcome matrix Y                          │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1B: Purity Validation (Week 1, ~2 days)              │
├─────────────────────────────────────────────────────────────┤
│  1. Sample n=500 commits for expert annotation              │
│  2. 3 experts rate primary/secondary aspects (5-point scale)│
│  3. Compute purity % (one aspect rated major, others minor) │
│  4. IF purity ≥70%: proceed                                 │
│     IF 60-70%: apply mixture modeling                       │
│     IF <60%: FAIL hypothesis, report entanglement           │
└─────────────────────────────────────────────────────────────┘
         ↓ (IF purity ≥60%)
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Residual Covariance Analysis (Week 2, ~3 days)    │
├─────────────────────────────────────────────────────────────┤
│  1. Regress out confounds: edit size, file entropy          │
│  2. Compute residual covariance matrix Σ (4×4)              │
│  3. Eigendecomposition: λ₁, λ₂, λ₃, λ₄, v₁, v₂, v₃, v₄      │
│  4. Compute spectral gap: λ₄/λ₅ (where λ₅→0 for rank 4)    │
│  5. Measure cross-aspect coupling: median off-diagonal Σ    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Statistical Validation (Week 2, ~3 days)          │
├─────────────────────────────────────────────────────────────┤
│  1. Permutation test: shuffle aspect labels 1000×           │
│  2. Recompute λ₄/λ₅ for each permutation                   │
│  3. Compute p-value: P(λ₄/λ₅_perm ≥ λ₄/λ₅_obs)            │
│  4. Directional stability: on-axis projection z-scores      │
│  5. Leave-one-repo-out cross-validation of eigenstructure   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Gate Decision (Week 2, end)                       │
├─────────────────────────────────────────────────────────────┤
│  ✓ PASS: λ₄/λ₅>2.0 AND p<0.05 AND coupling≤0.2×          │
│     → Proceed to H-M-Integrated                             │
│  ✗ FAIL: Flat spectrum or failed permutation test          │
│     → ABORT pipeline, publish negative result               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Confound Regression

**Controlled Variables:**
- **Edit Size:** Number of AST nodes changed (may inflate variance for all metrics)
- **File Entropy:** Shannon entropy of token distribution (proxy for code complexity)
- **Repository:** Control for repo-level differences via mixed-effects model

**Regression Model:**
```
Y_residual = Y - (β₀ + β₁×edit_size + β₂×file_entropy + γ_repo)
```

Where:
- Y ∈ ℝ^(10000×4) is the outcome matrix (Δcorrectness, Δquality, Δsecurity, Δefficiency)
- γ_repo are random effects for each repository
- Y_residual is used for covariance computation

### 5.3 Spectral Analysis

**Covariance Matrix:**
```
Σ = (1/n) × Y_residual^T × Y_residual
```

**Eigendecomposition:**
```
Σ = V Λ V^T
where Λ = diag(λ₁, λ₂, λ₃, λ₄) sorted descending
```

**Key Metrics:**
1. **Spectral Gap:** λ₄/λ₅ where λ₅→0 (since rank=4). Use numerical stability: λ₄/(λ₅ + ε) with ε=1e-8
2. **Cross-Aspect Coupling:** median{|Σᵢⱼ|/√(Σᵢᵢ×Σⱼⱼ) : i≠j} (normalized off-diagonal covariance)
3. **On-Axis Projection:** For each aspect k, compute z_k = ⟨Δyₖ, vₖ⟩/std(⟨Δyₖ, vₖ⟩) (z-score of projection onto eigenvector)

### 5.4 Permutation Test

**Null Hypothesis:** Aspect labels are unrelated to outcome structure (no aspect-dominant geometry)

**Procedure:**
```python
observed_gap = lambda_4 / (lambda_5 + 1e-8)  # or lambda_4 / trace_residual if rank<4
null_gaps = []
for i in range(1000):
    Y_shuffled = shuffle_aspect_labels(Y_residual)
    Sigma_null = compute_covariance(Y_shuffled)
    lambdas_null = eigenvalues(Sigma_null)
    null_gaps.append(lambdas_null[3] / (lambdas_null[4] + 1e-8))

p_value = sum(null_gaps >= observed_gap) / 1000
PASS if p_value < 0.05
```

### 5.5 Directional Stability Test

**Goal:** Verify that eigenvectors correspond to aspect-specific directions (not arbitrary rotations)

**Method:**
For each eigenvector vₖ and aspect label j:
```
projection_score[k,j] = ⟨Δy_j, vₖ⟩ / ||Δy_j||  # cosine similarity
z_score[k,j] = projection_score[k,j] / std_null(projection_score)
```

**Success:** Each eigenvector should have z>2.0 for exactly one aspect (on-axis), z<1.0 for others (off-axis)

### 5.6 Cross-Validation

**Leave-One-Repo-Out (LORO) Protocol:**
1. For each repository r in dataset:
   - Train: Compute Σ_train on all commits except repo r
   - Test: Project repo r commits onto eigenvectors from Σ_train
   - Measure: Alignment consistency (cosine similarity of eigenspaces)
2. Success: Median alignment >0.7 across all folds

---

## 6. Implementation Stack

### 6.1 Data Collection Tools

| Tool | Purpose | Implementation |
|------|---------|----------------|
| **PyGitHub** | GitHub API access | `pip install PyGithub` |
| **PyDriller** | Git commit mining | `pip install pydriller` |
| **tree-sitter** | AST distance computation | Python bindings for JS/Python/Java parsers |
| **GitHub GraphQL API** | Batch commit queries | `requests` + GraphQL schema |

### 6.2 Metric Computation Tools

| Metric | Tool | Implementation |
|--------|------|----------------|
| **Δcorrectness** | pytest/jest | Run test suite on pre/post versions, diff pass rates |
| **Δquality** | SonarQube CLI | `sonar-scanner` with incremental analysis mode |
| **Δsecurity** | CodeQL | GitHub Actions API or local `codeql` CLI |
| **Δefficiency** | pytest-benchmark | Benchmark runtime on affected functions |

**Docker Setup:**
```bash
# SonarQube local instance
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# CodeQL CLI
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:$(pwd)/codeql
```

### 6.3 Analysis Tools

| Analysis | Library | Implementation |
|----------|---------|----------------|
| **Covariance** | NumPy/SciPy | `np.cov(Y_residual.T)` |
| **Eigendecomposition** | NumPy | `np.linalg.eigh(Sigma)` (symmetric matrix) |
| **Mixed-effects model** | statsmodels | `MixedLM` for confound regression |
| **Permutation test** | Custom | Shuffle + recompute 1000× |
| **Cross-validation** | scikit-learn | `LeaveOneGroupOut` with repo as group |

### 6.4 Compute Requirements

| Resource | Specification | Justification |
|----------|---------------|---------------|
| **CPU** | 16 cores | Parallel metric computation across commits |
| **RAM** | 64 GB | Hold 10K×4 outcome matrix + intermediate results |
| **Storage** | 500 GB | Store 10K commit diffs, pre/post files, metric reports |
| **GPU** | None | No deep learning, pure statistical analysis |
| **Time** | ~10 GPU-hours equivalent | Metric computation dominates (5-10 sec/commit × 10K) |

---

## 7. Success Criteria & Gates

### 7.1 Primary Criteria (Gate 1 - MUST_WORK)

| Criterion | Threshold | Measurement | Failure Response |
|-----------|-----------|-------------|------------------|
| **Spectral Gap** | λ₄/λ₅ > 2.0 | Eigenvalue ratio | ABORT pipeline if ≤2.0 |
| **Permutation Test** | p < 0.05 | 1000 shuffles | ABORT if fails |
| **Cross-Aspect Coupling** | ≤0.2× primary | Median normalized off-diagonal | ABORT if >0.3× |
| **On-Axis Projection** | z-score > 2.0 | Per-aspect alignment | Document weakness if <2.0 |

**Decision Rule:**
```
IF (spectral_gap > 2.0) AND (p_value < 0.05) AND (coupling <= 0.2):
    PASS Gate 1 → Proceed to H-M-Integrated
ELIF (spectral_gap <= 2.0) OR (p_value >= 0.05) OR (coupling > 0.3):
    FAIL Gate 1 → ABORT entire pipeline
    ACTION: Publish negative result on intrinsic entanglement
```

### 7.2 Secondary Criteria (Quality Gates)

| Criterion | Threshold | Measurement | Failure Response |
|-----------|-----------|-------------|------------------|
| **Metric Reliability** | ICC ≥ 0.8 | Intraclass correlation | Drop unreliable metrics if <0.8 |
| **Construct Validity** | r ≥ 0.7 | Correlation with expert ratings | Drop if <0.7 |
| **Commit Purity** | ≥ 70% | Expert annotation | Apply mixture modeling if 60-70%, FAIL if <60% |
| **Inter-Rater Agreement** | κ ≥ 0.6 | Fleiss' kappa | Re-annotate if <0.6 |
| **LORO Consistency** | Median ≥ 0.7 | Cross-validation alignment | Document generalization limits if <0.7 |

### 7.3 Reportable Outcomes

**Full Success (all primary + secondary criteria pass):**
- Empirical separability confirmed with strong statistical evidence
- Proceed to architectural exploitation (H-M-Integrated)
- Contribution: First systematic quantification of aspect-dominant structure in real code

**Partial Success (primary pass, some secondary issues):**
- Example: Purity 65%, applied mixture correction → Still valid but document limitation
- Example: LORO consistency 0.6 → Separability exists but generalizes weakly

**Full Failure (primary criteria fail):**
- Multi-objective code alignment is intrinsically entangled
- Redirect field toward co-adaptive methods, not architectural factorization
- High-impact negative result: "Developers do NOT cognitively factorize programming concerns"

---

## 8. Risk Mitigation

### 8.1 Risk R1: Metric Unreliability (High Severity)

**Mitigation:**
- **Prevention:** Run Phase 0 metric validation BEFORE full data collection
- **Detection:** ICC<0.8 or r<0.7 triggers metric dropout
- **Response:** Proceed with ≥3/4 validated metrics, ABORT if <3/4 pass

**Contingency Code:**
```python
valid_metrics = [m for m in metrics if ICC[m] >= 0.8 and r_expert[m] >= 0.7]
if len(valid_metrics) < 3:
    raise AbortExperiment("Insufficient metric reliability (<3/4 valid)")
Y_final = Y[:, valid_metrics]  # Use only validated metrics
```

### 8.2 Risk R2: Commit Label Impurity (High Severity)

**Mitigation:**
- **Prevention:** Expert annotation on n=500 BEFORE full analysis
- **Detection:** Purity score <70% triggers mixture modeling
- **Response:**
  - 60-70%: Apply expert-weighted covariance correction
  - <60%: FAIL hypothesis, publish negative result

**Mixture Modeling (if purity 60-70%):**
```python
# Estimate mixture proportions from expert ratings
p_primary = expert_ratings['primary_aspect_strength'].mean()  # ~0.65
p_secondary = 1 - p_primary

# Weighted covariance correction
Sigma_corrected = p_primary * Sigma_observed - p_secondary * Sigma_noise_model
```

### 8.3 Risk R5: Computational Budget Overrun

**Mitigation:**
- **Sampling Strategy:** If metric computation exceeds budget, sample 5K commits instead of 10K
- **Parallelization:** Use GNU parallel or multiprocessing.Pool for metric computation
- **Caching:** Cache SonarQube/CodeQL results to avoid recomputation

**Budget Monitoring:**
```python
estimated_time_per_commit = 8  # seconds (SonarQube + CodeQL)
total_time_hours = (10000 * estimated_time_per_commit) / 3600  # ~22 hours
if total_time_hours > budget_hours:
    n_commits_sample = int(budget_hours * 3600 / estimated_time_per_commit)
    commits = random.sample(commits, n_commits_sample)
```

---

## 9. Output Artifacts

### 9.1 Primary Outputs

| Artifact | Format | Content | Usage |
|----------|--------|---------|-------|
| **outcome_matrix.npy** | NumPy array | 10K×4 matrix of Δmetrics | Input to covariance analysis |
| **covariance_matrix.npy** | NumPy array | 4×4 Σ (residual covariance) | Eigendecomposition |
| **eigenvalues.json** | JSON | λ₁, λ₂, λ₃, λ₄, spectral gap | Gate decision |
| **eigenvectors.npy** | NumPy array | 4×4 matrix V | Directional stability test |
| **permutation_results.json** | JSON | 1000 null gaps, p-value | Statistical validation |

### 9.2 Validation Outputs

| Artifact | Format | Content | Usage |
|----------|--------|---------|-------|
| **metric_reliability.csv** | CSV | ICC, r_expert for each metric | Phase 0 validation report |
| **purity_validation.csv** | CSV | Expert ratings, purity %, κ | Commit label quality |
| **loro_results.json** | JSON | Alignment per fold, median | Generalization assessment |

### 9.3 Visualization Outputs

| Artifact | Type | Content |
|----------|------|---------|
| **eigenspectrum.png** | Bar plot | λ₁, λ₂, λ₃, λ₄ with error bars |
| **permutation_distribution.png** | Histogram | Null distribution + observed gap (red line) |
| **directional_stability_heatmap.png** | Heatmap | z-scores[eigenvector, aspect] |
| **covariance_heatmap.png** | Heatmap | Σ with off-diagonal coupling highlighted |

### 9.4 Final Report

**File:** `h-e1_validation_report.md`

**Sections:**
1. **Executive Summary:** Gate decision (PASS/FAIL), key metrics
2. **Dataset Description:** 10K commits, repositories, aspect distribution
3. **Metric Validation:** ICC, r_expert, dropped metrics (if any)
4. **Spectral Analysis:** λ values, gap, coupling, eigenvector interpretation
5. **Statistical Tests:** Permutation p-value, directional stability z-scores, LORO consistency
6. **Gate Decision:** Rationale for PASS/FAIL, next steps
7. **Limitations:** Purity issues, generalization caveats, confound coverage

---

## 10. Timeline & Milestones

| Week | Phase | Tasks | Deliverables | Gate |
|------|-------|-------|--------------|------|
| **Week 0** | Metric Validation | Run ICC, r_expert on n=200 | metric_reliability.csv | Phase 0 gate (≥3/4 pass) |
| **Week 1** | Data Collection | Mine 10K commits, compute metrics | outcome_matrix.npy | - |
| **Week 1** | Purity Validation | Expert annotation n=500 | purity_validation.csv | Purity gate (≥60%) |
| **Week 2** | Spectral Analysis | Confound regression, eigendecomposition | eigenvalues.json, eigenvectors.npy | - |
| **Week 2** | Statistical Tests | Permutation test, directional stability, LORO | permutation_results.json, loro_results.json | Gate 1 decision |
| **Week 2** | Reporting | Generate visualizations, final report | h-e1_validation_report.md, plots | - |

**Total Duration:** 2 weeks  
**Critical Path:** Phase 0 → Data Collection → Spectral Analysis → Gate 1  
**Bottleneck:** Metric computation (dominates with ~22 hours for 10K commits)

---

## 11. Phase 3 Readiness Checklist

**If H-E1 PASSES Gate 1, the following are ready for Phase 3 (Implementation Planning):**

- [x] **Empirical Foundation:** Aspect-dominant structure confirmed (λ₄/λ₅>2.0, p<0.05)
- [x] **Eigenvector Basis:** Natural axes V = [v₁, v₂, v₃, v₄] available for architectural alignment
- [x] **Validated Metrics:** 3-4 reliable metrics (ICC≥0.8, r≥0.7) for outcome measurement
- [x] **Purity-Corrected Data:** If 60-70% purity, mixture model applied; if ≥70%, clean labels
- [x] **Cross-Validation Evidence:** LORO consistency ≥0.7 (or documented if <0.7)

**Phase 3 will use:**
- **V (eigenvectors)** as natural axes for LoRA adapter initialization
- **Validated metrics** as training signals for aspect-specific adapters
- **10K commit corpus** as training data for adapter fine-tuning

**If H-E1 FAILS Gate 1:**
- STOP entire pipeline immediately
- Generate negative result paper: "Multi-Objective Code Alignment is Intrinsically Entangled"
- Redirect research toward co-adaptive methods (no architectural factorization)

---

## 12. References & Prior Work

### 12.1 Implementation References

**From Exa Search Results:**

1. **PyDriller** (ishepard/pydriller) - Python framework for Git repository analysis
   - Commit mining, diff extraction, author analysis
   - Used for: Data collection pipeline (10K commits)

2. **Git-of-Theseus** (erikbern/git-of-theseus) - Survival analysis on Git repos
   - Kaplan-Meier survival curves for code persistence
   - Inspiration for: Time-weighted covariance if needed in future work

3. **GitDelver** (nicolasriquet/GitDelver) - Bulk repository analysis tool
   - Processes commits, files, methods with various analyses
   - Used for: Batch processing pipeline design

4. **tree-sitter** (tree-hugger wrapper) - Universal code parser
   - AST extraction for Python/JS/Java
   - Used for: AST distance computation (<20 nodes filter)

### 12.2 Metric Validation References

**From Exa Search Results:**

1. **SonarQube Python Analyzer** (sonarsource/sonar-python)
   - 400+ static analysis rules, OWASP/CWE compliance
   - Achieves 92% TPR on Python SAST benchmarks
   - Used for: Δquality metric (maintainability rating)

2. **CodeQL Python Queries** (GitHub Docs)
   - Semantic analysis with taint tracking, data flow graphs
   - Detects SQL injection, XSS, insecure deserialization
   - Used for: Δsecurity metric (alert count)

3. **pytest-cov + Coverage.py** (Python test coverage documentation)
   - Cobertura XML format, branch coverage
   - Used for: Δcorrectness metric (test pass rate on pre/post)

4. **pytest-benchmark** (pytest plugin)
   - Function-level runtime benchmarking
   - Used for: Δefficiency metric (% runtime improvement)

### 12.3 Statistical Methods References

**From Archon KB Search (limited results):**

1. **PCA via Covariance Eigendecomposition** (Duke Computational Statistics)
   - Spectral decomposition: A = Q⁻¹ΛQ
   - Change of basis transformations for dimension reduction
   - Used for: Eigenanalysis of residual covariance Σ

2. **torch_pca** (valentingol/torch_pca) - PyTorch PCA implementation
   - Supports `covariance_eigh` solver for small feature spaces
   - Auto-selection between full SVD and covariance eigendecomposition
   - Reference for: Numerical stability in eigendecomposition

3. **scanpy sparse PCA** (scverse/scanpy #3263) - Dask-based covariance PCA
   - Implements sparse covariance_eigh with Dask for large datasets
   - Reference for: Scalable covariance computation if data grows beyond 10K

### 12.4 GitHub API Mining References

**From Exa Search Results:**

1. **gh-crawler** (AI-nstein/gh-crawler) - GitHub commit crawler
   - Downloads (buggy, fixed) file pairs from GH Archive
   - Used for: Data collection architecture (pre/post file pairs)

2. **commitgen** (epochx/commitgen) - Commit message generation dataset
   - crawl_commits.py: Systematic commit mining with rate limit handling
   - Used for: Rate limit management strategy (5000/hour)

3. **ghminer** (schnell18/ghminer) - MSR research toolkit
   - Solves 1000-limit issue via query partitioning
   - Rate-limit pooling across multiple tokens
   - Used for: Large-scale commit mining strategy

4. **gittensor** (entrius/gittensor) - Tree-diff scoring
   - Uses merge-base for accurate diff computation
   - Used for: AST distance calculation methodology

---

## 13. Experiment Execution Commands

### 13.1 Phase 0: Metric Validation

```bash
# Setup environment
conda create -n h-e1-validation python=3.10
conda activate h-e1-validation
pip install pydriller PyGithub tree-sitter pytest pytest-cov coverage \
            sonar-scanner codeql statsmodels scikit-learn numpy scipy pandas

# Start SonarQube
docker run -d --name sonarqube -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
    -p 9000:9000 sonarqube:latest

# Run metric validation (n=200)
python scripts/phase0_metric_validation.py \
    --n-commits 200 \
    --output metrics/metric_reliability.csv \
    --icc-threshold 0.8 \
    --construct-validity-threshold 0.7
```

### 13.2 Phase 1A: Data Collection

```bash
# Mine 10K commits
python scripts/phase1a_data_collection.py \
    --n-commits 10000 \
    --min-stars 1000 \
    --ast-distance-max 20 \
    --time-range 2023-01-01:2026-01-01 \
    --languages python,javascript,java \
    --output data/commits_10k.jsonl

# Compute metrics (parallel processing)
python scripts/phase1a_metric_computation.py \
    --commits data/commits_10k.jsonl \
    --metrics correctness,quality,security,efficiency \
    --n-workers 16 \
    --output data/outcome_matrix.npy
```

### 13.3 Phase 1B: Purity Validation

```bash
# Sample n=500 for expert annotation
python scripts/phase1b_sample_for_annotation.py \
    --commits data/commits_10k.jsonl \
    --n-sample 500 \
    --output data/annotation_subset.jsonl

# Expert annotation interface (3 experts)
python scripts/phase1b_annotation_interface.py \
    --commits data/annotation_subset.jsonl \
    --annotator-id expert1 \
    --output data/annotations_expert1.csv

# Compute purity and inter-rater agreement
python scripts/phase1b_purity_analysis.py \
    --annotations data/annotations_expert*.csv \
    --threshold 0.7 \
    --output data/purity_validation.csv
```

### 13.4 Phase 2: Spectral Analysis

```bash
# Confound regression
python scripts/phase2_confound_regression.py \
    --outcome-matrix data/outcome_matrix.npy \
    --commits data/commits_10k.jsonl \
    --confounds edit_size,file_entropy \
    --output data/outcome_residual.npy

# Eigendecomposition
python scripts/phase2_eigenanalysis.py \
    --residual-matrix data/outcome_residual.npy \
    --output-eigenvalues data/eigenvalues.json \
    --output-eigenvectors data/eigenvectors.npy \
    --output-covariance data/covariance_matrix.npy
```

### 13.5 Phase 3: Statistical Validation

```bash
# Permutation test (1000 shuffles)
python scripts/phase3_permutation_test.py \
    --residual-matrix data/outcome_residual.npy \
    --n-permutations 1000 \
    --observed-gap data/eigenvalues.json \
    --output data/permutation_results.json

# Directional stability test
python scripts/phase3_directional_stability.py \
    --residual-matrix data/outcome_residual.npy \
    --eigenvectors data/eigenvectors.npy \
    --commits data/commits_10k.jsonl \
    --output data/directional_stability.json

# Leave-one-repo-out cross-validation
python scripts/phase3_loro_cv.py \
    --residual-matrix data/outcome_residual.npy \
    --commits data/commits_10k.jsonl \
    --output data/loro_results.json
```

### 13.6 Phase 4: Gate Decision & Reporting

```bash
# Gate 1 decision logic
python scripts/phase4_gate_decision.py \
    --eigenvalues data/eigenvalues.json \
    --permutation data/permutation_results.json \
    --covariance data/covariance_matrix.npy \
    --thresholds spectral_gap=2.0,p_value=0.05,coupling=0.2 \
    --output reports/gate1_decision.json

# Generate visualizations
python scripts/phase4_visualizations.py \
    --eigenvalues data/eigenvalues.json \
    --permutation data/permutation_results.json \
    --covariance data/covariance_matrix.npy \
    --output-dir visualizations/

# Final report generation
python scripts/phase4_generate_report.py \
    --gate-decision reports/gate1_decision.json \
    --all-results data/ \
    --output reports/h-e1_validation_report.md
```

---

## 14. Appendix: Theoretical Background

### 14.1 Why Spectral Decomposition?

**Intuition:** If developers cognitively factorize programming concerns into separable dimensions (security ⊥ performance ⊥ quality ⊥ correctness), then the covariance matrix Σ of commit outcomes should have:
- **4 dominant eigenvalues** (one per aspect)
- **Small off-diagonal entries** (weak cross-aspect coupling)
- **Eigenvectors aligned with aspect labels** (directional stability)

**Null Hypothesis (H0):** Flat eigenspectrum (all λᵢ ≈ equal) indicates entanglement — no natural factorization exists.

### 14.2 Spectral Gap Interpretation

**Spectral Gap:** λ₄/λ₅ measures the "dimensionality cliff" between signal (4 aspects) and noise (λ₅→0 for rank 4 matrix).

- λ₄/λ₅ > 2.0: Clear 4-dimensional structure (aspect-dominant)
- λ₄/λ₅ ≤ 2.0: Gradual decay, suggests higher-dimensional entanglement

**Permutation Test Rationale:** Under H0 (no aspect structure), shuffling aspect labels should not change λ₄/λ₅. If observed gap exceeds 95% of shuffled gaps, reject H0.

### 14.3 Cross-Aspect Coupling

**Definition:** Median{|Σᵢⱼ|/√(Σᵢᵢ×Σⱼⱼ) : i≠j} measures normalized correlation between aspects.

- Coupling ≤ 0.2: Aspects are weakly correlated (factorizable)
- Coupling > 0.3: Strong interdependence (entangled)

**Threshold Justification:** 0.2 corresponds to ~4% shared variance (r²=0.04), standard threshold for "negligible correlation" in psychometrics.

### 14.4 Directional Stability

**Goal:** Verify that eigenvectors vₖ align with aspect-specific directions (not arbitrary rotations).

**Method:** For each aspect j, compute z-score of projection onto vₖ. If vₖ corresponds to aspect j, expect:
- z-score(j, k) > 2.0 (strong on-axis alignment)
- z-score(j', k) < 1.0 for j'≠j (weak off-axis)

**Failure Case:** If all z-scores ≈1.0, eigenvectors are arbitrary rotations — no aspect-specific structure.

---

**End of Experiment Brief**

*Generated by Anonymous Phase 2C | 2026-05-11*  
*Ready for Phase 3 Implementation Planning*
