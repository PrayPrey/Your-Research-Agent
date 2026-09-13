# Product Requirements Document: H-E1 Aspect-Dominant Structure Existence

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Generated:** 2026-05-11  
**Status:** Implementation Planning

---

## 1. Executive Summary

### 1.1 Problem Statement

Validate whether human expert code modifications exhibit aspect-dominant directional structure across quality dimensions (correctness, quality, security, efficiency) through spectral decomposition analysis of GitHub commit data. This is a foundational empirical validation that determines if the entire architectural factorization approach (H-M-Integrated) has empirical grounding.

### 1.2 Solution Overview

Implement a statistical analysis pipeline that:
1. Collects 10,000 minimal-diff commits from GitHub with aspect labels
2. Computes quality metrics (Δcorrectness, Δquality, Δsecurity, Δefficiency) for each commit
3. Performs spectral decomposition on residual covariance matrices
4. Validates separability through permutation tests and cross-validation

### 1.3 Success Criteria

**Primary (MUST_WORK Gate):**
- Spectral gap λ₄/λ₅ > 2.0 (exceeds 95th percentile of permutation null)
- Cross-aspect coupling ≤0.2× primary effect (95% CI)
- Permutation test p-value < 0.05
- On-axis projection z-score > 2.0

**Secondary (Quality Gates):**
- Commit purity > 70% (expert annotation)
- Metric reliability: ICC ≥ 0.8, construct validity r ≥ 0.7
- LORO cross-validation consistency ≥ 0.7

**Failure Response:** If primary criteria fail → ABORT entire pipeline → Publish negative result on intrinsic entanglement

---

## 2. Functional Requirements

### FR-1: Data Collection Pipeline

**FR-1.1: Repository Mining**
- **Description:** Mine 500-1000 popular Python/JavaScript repositories from GitHub
- **Acceptance Criteria:**
  - Repositories have ≥1000 stars
  - Active development (commits in last 6 months)
  - Non-tutorial projects only
  - Tools: PyGitHub, PyDriller, GitHub GraphQL API

**FR-1.2: Commit Filtering**
- **Description:** Filter commits to create minimal-diff corpus
- **Acceptance Criteria:**
  - Time range: 2023-2026 (last 3 years)
  - AST distance: 1-20 nodes changed
  - File types: `.py`, `.js`, `.java` only
  - Exclude: Merge commits, bot commits, doc-only changes
  - Target: 10,000 commits total

**FR-1.3: Aspect Labeling**
- **Description:** Label commits by aspect type using commit messages
- **Acceptance Criteria:**
  - Automatic labeling via keyword matching:
    - Security: "security", "vulnerability", "CVE", "XSS", "injection", "auth"
    - Refactor: "refactor", "cleanup", "rename", "restructure"
    - Performance: "performance", "optimize", "speed", "cache"
    - Bugfix: "fix", "bug", "error", "crash", "issue #"
  - Expert validation subset (n=500)
  - Inter-rater agreement κ > 0.6 (Fleiss' kappa)

**FR-1.4: Commit Storage**
- **Description:** Download and store pre/post file pairs for each commit
- **Acceptance Criteria:**
  - Store commit metadata (hash, message, author, timestamp)
  - Store pre-commit and post-commit file contents
  - Store AST distance calculation
  - Format: JSONL for metadata, separate files for code

### FR-2: Metric Validation (Phase 0)

**FR-2.1: Test-Retest Reliability**
- **Description:** Validate metric reliability on n=200 commits
- **Acceptance Criteria:**
  - Run metrics twice with 1-week gap
  - Compute ICC (intraclass correlation) for each metric
  - Threshold: ICC ≥ 0.8
  - Drop metrics that fail validation

**FR-2.2: Construct Validity**
- **Description:** Validate metrics against expert judgment
- **Acceptance Criteria:**
  - 3 experts rate 200 commits on quality/security/efficiency
  - Compute Pearson correlation with metric values
  - Threshold: r ≥ 0.7 vs expert consensus
  - Proceed only if ≥3/4 metrics pass

### FR-3: Metric Computation Pipeline

**FR-3.1: Δcorrectness Metric**
- **Description:** Compute test pass rate change
- **Acceptance Criteria:**
  - Run pytest/jest on affected test suite (pre and post)
  - Metric: (pass_rate_post - pass_rate_pre)
  - Handle cases with no tests (exclude from analysis)

**FR-3.2: Δquality Metric**
- **Description:** Compute code maintainability change using SonarQube
- **Acceptance Criteria:**
  - Run SonarQube CLI on pre/post versions
  - Extract maintainability rating (A, B, C, D, E)
  - Metric: ordinal change (A→B = -1, B→A = +1)
  - Docker setup: `sonarqube:latest` container

**FR-3.3: Δsecurity Metric**
- **Description:** Compute security alert count change using CodeQL
- **Acceptance Criteria:**
  - Run CodeQL on pre/post versions
  - Count security alerts (SQL injection, XSS, etc.)
  - Metric: (alerts_pre - alerts_post) [negative if new alerts]
  - Use GitHub CodeQL CLI or Actions API

**FR-3.4: Δefficiency Metric**
- **Description:** Compute runtime performance change
- **Acceptance Criteria:**
  - Run pytest-benchmark on affected functions
  - Measure runtime (pre and post)
  - Metric: (runtime_pre - runtime_post) / runtime_pre [% improvement]
  - Minimum 10 benchmark runs for statistical significance

**FR-3.5: Outcome Matrix Construction**
- **Description:** Build 10K × 4 outcome matrix Y
- **Acceptance Criteria:**
  - Rows: 10,000 commits
  - Columns: [Δcorrectness, Δquality, Δsecurity, Δefficiency]
  - Handle missing values (exclude commits with incomplete metrics)
  - Save as NumPy array: `outcome_matrix.npy`

### FR-4: Purity Validation

**FR-4.1: Expert Annotation Interface**
- **Description:** Collect expert ratings on commit purity
- **Acceptance Criteria:**
  - Sample n=500 commits randomly from corpus
  - 3 experts rate each commit's primary/secondary aspects (5-point scale)
  - Web-based or CLI annotation tool
  - Save annotations in structured format (CSV)

**FR-4.2: Purity Computation**
- **Description:** Calculate commit purity score
- **Acceptance Criteria:**
  - Purity = % commits where one aspect rated major, others minor
  - Compute Fleiss' kappa for inter-rater agreement
  - Output: purity_validation.csv
  - Decision logic:
    - Purity ≥70%: Proceed
    - 60-70%: Apply mixture modeling
    - <60%: FAIL hypothesis

### FR-5: Statistical Analysis Pipeline

**FR-5.1: Confound Regression**
- **Description:** Regress out confounding variables
- **Acceptance Criteria:**
  - Confounds: edit_size, file_entropy, repository (random effect)
  - Model: Y_residual = Y - (β₀ + β₁×edit_size + β₂×file_entropy + γ_repo)
  - Use statsmodels MixedLM for mixed-effects model
  - Output: Y_residual matrix (10K × 4)

**FR-5.2: Covariance Computation**
- **Description:** Compute residual covariance matrix
- **Acceptance Criteria:**
  - Σ = (1/n) × Y_residual^T × Y_residual
  - Result: 4×4 symmetric matrix
  - Save as: covariance_matrix.npy

**FR-5.3: Eigendecomposition**
- **Description:** Perform spectral decomposition
- **Acceptance Criteria:**
  - Σ = V Λ V^T where Λ = diag(λ₁, λ₂, λ₃, λ₄)
  - Use `np.linalg.eigh()` for symmetric matrix
  - Sort eigenvalues descending
  - Output: eigenvalues.json, eigenvectors.npy

**FR-5.4: Spectral Gap Calculation**
- **Description:** Compute spectral gap metric
- **Acceptance Criteria:**
  - Metric: λ₄/(λ₅ + ε) where ε=1e-8 for numerical stability
  - Since rank=4, λ₅→0 (gap measures 4D structure vs noise)
  - Alternative: λ₄/trace_residual if rank < 4

**FR-5.5: Cross-Aspect Coupling**
- **Description:** Measure normalized off-diagonal covariance
- **Acceptance Criteria:**
  - Metric: median{|Σᵢⱼ|/√(Σᵢᵢ×Σⱼⱼ) : i≠j}
  - Represents correlation between aspects
  - Threshold: ≤0.2× (weak coupling)

### FR-6: Permutation Test

**FR-6.1: Null Distribution Generation**
- **Description:** Generate null distribution via label shuffling
- **Acceptance Criteria:**
  - Shuffle aspect labels 1000 times
  - Recompute Σ and λ₄/λ₅ for each shuffle
  - Store 1000 null gap values
  - Output: permutation_results.json

**FR-6.2: P-value Computation**
- **Description:** Calculate statistical significance
- **Acceptance Criteria:**
  - p-value = P(λ₄/λ₅_null ≥ λ₄/λ₅_observed)
  - Count: #{null gaps ≥ observed} / 1000
  - Threshold: p < 0.05 to reject H0

### FR-7: Directional Stability Test

**FR-7.1: On-Axis Projection**
- **Description:** Verify eigenvectors align with aspect directions
- **Acceptance Criteria:**
  - For each eigenvector vₖ and aspect j:
    - projection_score[k,j] = ⟨Δy_j, vₖ⟩ / ||Δy_j||
    - z_score[k,j] = projection_score / std_null
  - Each vₖ should have z>2.0 for one aspect, z<1.0 for others
  - Output: directional_stability.json with z-scores matrix

### FR-8: Cross-Validation

**FR-8.1: Leave-One-Repo-Out (LORO)**
- **Description:** Validate eigenstructure generalization
- **Acceptance Criteria:**
  - For each repo r:
    - Train: Compute Σ_train on all commits except repo r
    - Test: Project repo r onto eigenvectors from Σ_train
    - Measure: Cosine similarity of eigenspaces
  - Output: LORO consistency scores per fold
  - Threshold: Median ≥ 0.7

### FR-9: Gate Decision Logic

**FR-9.1: Primary Criteria Evaluation**
- **Description:** Evaluate MUST_WORK gate criteria
- **Acceptance Criteria:**
  - Check: spectral_gap > 2.0
  - Check: p_value < 0.05
  - Check: coupling ≤ 0.2
  - Output: gate1_decision.json with PASS/FAIL status

**FR-9.2: Failure Response**
- **Description:** Handle gate failure
- **Acceptance Criteria:**
  - If FAIL: Update verification_state.yaml
  - Set gate.satisfied = false
  - Status = FAIL_GATE
  - Generate negative result report
  - Stop pipeline execution

### FR-10: Visualization & Reporting

**FR-10.1: Eigenspectrum Plot**
- **Description:** Visualize eigenvalue distribution
- **Acceptance Criteria:**
  - Bar plot: λ₁, λ₂, λ₃, λ₄ with error bars (bootstrap)
  - Highlight spectral gap λ₄ vs λ₅
  - Output: eigenspectrum.png

**FR-10.2: Permutation Distribution Plot**
- **Description:** Visualize null vs observed
- **Acceptance Criteria:**
  - Histogram: 1000 null gap values
  - Red vertical line: observed gap
  - Mark 95th percentile threshold
  - Output: permutation_distribution.png

**FR-10.3: Directional Stability Heatmap**
- **Description:** Visualize eigenvector alignment
- **Acceptance Criteria:**
  - Heatmap: z-scores[eigenvector, aspect]
  - Annotate diagonal (on-axis) values
  - Output: directional_stability_heatmap.png

**FR-10.4: Covariance Heatmap**
- **Description:** Visualize covariance structure
- **Acceptance Criteria:**
  - Heatmap: 4×4 Σ matrix
  - Highlight off-diagonal (coupling) cells
  - Output: covariance_heatmap.png

**FR-10.5: Validation Report**
- **Description:** Generate comprehensive report
- **Acceptance Criteria:**
  - Sections: Executive Summary, Dataset, Metric Validation, Spectral Analysis, Statistical Tests, Gate Decision, Limitations
  - Include all visualizations
  - Output: h-e1_validation_report.md

---

## 3. Non-Functional Requirements

### NFR-1: Performance
- **Metric computation:** Parallel processing across 16 cores
- **Total runtime:** ≤3 days for full pipeline (metric validation + data collection + analysis)
- **Memory:** ≤64 GB RAM for 10K × 4 matrix operations

### NFR-2: Reliability
- **Metric validation:** ICC ≥ 0.8 (test-retest)
- **Data quality:** ≥3/4 metrics must pass validation
- **Reproducibility:** Random seed control for permutation tests

### NFR-3: Scalability
- **Fallback:** If budget exceeded, sample 5K commits instead of 10K
- **Caching:** SonarQube/CodeQL results cached to avoid recomputation
- **Parallelization:** GNU parallel or multiprocessing.Pool

### NFR-4: Usability
- **Progress tracking:** Log file with status updates
- **Checkpointing:** Save intermediate results (outcome_matrix, covariance)
- **Error handling:** Graceful degradation if metrics fail

### NFR-5: Maintainability
- **Code structure:** Modular pipeline (separate scripts per phase)
- **Documentation:** Inline comments for statistical methods
- **Configuration:** YAML config for thresholds and parameters

---

## 4. Data Requirements

### 4.1 Primary Dataset
- **Name:** GitHub Minimal-Diff Commit Corpus
- **Size:** 10,000 commits
- **Source:** GitHub API (public repositories)
- **Format:** JSONL for metadata, separate files for code
- **Storage:** 500 GB (commit diffs + pre/post files)

### 4.2 Validation Datasets
- **Metric Validation:** 200 commits (test-retest)
- **Purity Validation:** 500 commits (expert annotation)
- **Total unique commits:** ~10,200 (with some overlap)

### 4.3 Data Quality Filters
- **AST distance:** 1-20 nodes changed
- **Repository quality:** ≥1000 stars, active development
- **Commit quality:** Exclude merges, bot commits, doc-only
- **Aspect distribution:** Balanced across 4 aspects (±30%)

---

## 5. Dependencies & Infrastructure

### 5.1 External Tools
- **PyGitHub:** GitHub API access (`pip install PyGithub`)
- **PyDriller:** Git mining (`pip install pydriller`)
- **tree-sitter:** AST parsing (Python bindings)
- **SonarQube:** Code quality (Docker: `sonarqube:latest`)
- **CodeQL:** Security analysis (CLI from GitHub)
- **pytest/jest:** Test execution
- **pytest-benchmark:** Performance measurement

### 5.2 Python Libraries
- **Core:** NumPy, SciPy, pandas
- **Stats:** statsmodels (MixedLM), scikit-learn (cross-validation)
- **Visualization:** matplotlib, seaborn
- **Utils:** requests, tqdm, pyyaml

### 5.3 Compute Resources
- **CPU:** 16 cores (parallel metric computation)
- **RAM:** 64 GB
- **Storage:** 500 GB
- **GPU:** Not required (pure statistical analysis)
- **Runtime:** ~10 GPU-hours equivalent

### 5.4 Docker Services
- **SonarQube:** `docker run -d --name sonarqube -p 9000:9000 sonarqube:latest`
- **Optional:** PostgreSQL for SonarQube backend

---

## 6. Success Metrics & Validation

### 6.1 Primary Metrics (MUST_WORK)
| Metric | Threshold | Current | Status |
|--------|-----------|---------|--------|
| Spectral gap λ₄/λ₅ | > 2.0 | TBD | Pending |
| Permutation p-value | < 0.05 | TBD | Pending |
| Cross-aspect coupling | ≤ 0.2× | TBD | Pending |
| On-axis z-score | > 2.0 | TBD | Pending |

### 6.2 Secondary Metrics (Quality)
| Metric | Threshold | Current | Status |
|--------|-----------|---------|--------|
| Commit purity | ≥ 70% | TBD | Pending |
| Metric ICC | ≥ 0.8 | TBD | Pending |
| Construct validity r | ≥ 0.7 | TBD | Pending |
| LORO consistency | ≥ 0.7 | TBD | Pending |

### 6.3 Gate Decision
**IF** all primary metrics pass **THEN** PASS Gate 1 → Proceed to H-M-Integrated  
**ELSE** FAIL Gate 1 → ABORT pipeline → Publish negative result

---

## 7. Risk Assessment

### 7.1 High-Severity Risks
| Risk | Mitigation | Contingency |
|------|------------|-------------|
| R1: Metric unreliability (ICC<0.8) | Phase 0 validation first | Drop failing metrics, proceed if ≥3/4 pass |
| R2: Commit impurity (<60%) | Expert validation subset | Apply mixture modeling (60-70%) or FAIL (<60%) |
| R3: Computational budget overrun | Parallel processing + caching | Sample 5K commits instead of 10K |

### 7.2 Medium-Severity Risks
| Risk | Mitigation | Contingency |
|------|------------|-------------|
| R4: GitHub API rate limits | Token rotation, request batching | Extend collection time to 7 days |
| R5: SonarQube/CodeQL failures | Error handling, retry logic | Exclude problematic commits, proceed if >8K valid |

---

## 8. Timeline & Milestones

**Note:** Per BMAD guidelines, no time estimates provided. Focus on completion criteria.

| Phase | Deliverables | Completion Criteria |
|-------|--------------|---------------------|
| Phase 0 | metric_reliability.csv | ≥3/4 metrics pass ICC≥0.8, r≥0.7 |
| Phase 1A | outcome_matrix.npy (10K commits) | All metrics computed, <10% missing values |
| Phase 1B | purity_validation.csv | Purity ≥60%, κ≥0.6 |
| Phase 2 | eigenvalues.json, covariance_matrix.npy | Eigendecomposition complete |
| Phase 3 | permutation_results.json, loro_results.json | Statistical tests complete |
| Phase 4 | gate1_decision.json, validation_report.md | Gate decision made, report generated |

---

## 9. Acceptance Criteria

**Implementation Complete When:**
1. ✅ All FR-1 to FR-10 functional requirements implemented
2. ✅ All output artifacts generated (see Section 10)
3. ✅ Gate decision logic executed and documented
4. ✅ Validation report (h-e1_validation_report.md) written
5. ✅ verification_state.yaml updated with gate result

**Quality Criteria:**
1. ✅ Code passes basic smoke tests (can load data, run metrics on sample)
2. ✅ Permutation test reproducible with fixed random seed
3. ✅ All visualizations render correctly
4. ✅ No hardcoded paths (use config file)

---

## 10. Output Artifacts

### 10.1 Data Artifacts
- `commits_10k.jsonl` - Commit metadata
- `outcome_matrix.npy` - 10K × 4 metric values
- `outcome_residual.npy` - After confound regression
- `covariance_matrix.npy` - 4×4 Σ matrix
- `eigenvalues.json` - λ₁, λ₂, λ₃, λ₄, spectral_gap
- `eigenvectors.npy` - 4×4 V matrix

### 10.2 Validation Artifacts
- `metric_reliability.csv` - ICC, r_expert per metric
- `purity_validation.csv` - Expert ratings, purity score, kappa
- `permutation_results.json` - 1000 null gaps, p-value
- `directional_stability.json` - z-scores matrix
- `loro_results.json` - Cross-validation consistency per fold

### 10.3 Visualization Artifacts
- `eigenspectrum.png`
- `permutation_distribution.png`
- `directional_stability_heatmap.png`
- `covariance_heatmap.png`

### 10.4 Report Artifacts
- `h-e1_validation_report.md` - Final comprehensive report
- `gate1_decision.json` - Gate result with rationale

---

## 11. Appendix: Technical Specifications

### 11.1 AST Distance Calculation
```python
# Using tree-sitter for Python/JavaScript/Java
from tree_sitter import Language, Parser

def compute_ast_distance(pre_code, post_code, language):
    parser = Parser()
    parser.set_language(Language(f'tree-sitter-{language}'))
    tree_pre = parser.parse(bytes(pre_code, 'utf8'))
    tree_post = parser.parse(bytes(post_code, 'utf8'))
    return edit_distance(tree_pre.root_node, tree_post.root_node)
```

### 11.2 Metric Validation Protocol
```python
# Test-retest reliability
def compute_icc(metric_t1, metric_t2):
    # Two-way mixed effects, absolute agreement
    from statsmodels.stats.inter_rater import fleiss_kappa
    # Use ICC(3,1) formula
    return icc_score

# Construct validity
def compute_construct_validity(metric_values, expert_ratings):
    from scipy.stats import pearsonr
    r, p = pearsonr(metric_values, expert_ratings)
    return r, p
```

### 11.3 Mixed-Effects Model
```python
from statsmodels.regression.mixed_linear_model import MixedLM

# Confound regression
model = MixedLM(Y, X_fixed, groups=repo_ids)
result = model.fit()
Y_residual = Y - result.fittedvalues
```

### 11.4 Spectral Gap Calculation
```python
import numpy as np

# Eigendecomposition
Sigma = np.cov(Y_residual.T)
lambdas, V = np.linalg.eigh(Sigma)
lambdas = np.sort(lambdas)[::-1]  # Descending

# Spectral gap
epsilon = 1e-8
spectral_gap = lambdas[3] / (lambdas[4] + epsilon) if len(lambdas) > 4 else lambdas[3] / np.trace(Sigma)
```

---

**Document Status:** DRAFT - Implementation Planning  
**Next Phase:** Phase 3 Architecture Design  
**Owner:** Anonymous  
**Last Updated:** 2026-05-11
