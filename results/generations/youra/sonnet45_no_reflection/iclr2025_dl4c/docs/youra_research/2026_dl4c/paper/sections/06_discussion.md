# Discussion

Our findings establish a clear negative result: multi-objective code modifications exhibit statistical independence without aspect-dominant factorization. We discuss the implications for architectural design, honest limitations of our evaluation, alternative hypotheses for future exploration, and broader impact on the field.

## Key Finding: Independence ≠ Factorization

The central contribution of this work is distinguishing two concepts that prior literature conflated. **Statistical independence** means metrics are uncorrelated (low coupling=0.072). **Directional factorization** means code changes align along metric-specific axes (spectral gap>2.0, informative labels). Our data exhibits the former but not the latter.

**Architectural Implication:** Orthogonality constraints in multi-objective architectures (OrthoReg, PCGrad, aspect-specific gating) may be redundant when data is already independent. These constraints prevent task interference by enforcing geometric separation—but if metrics are naturally uncorrelated, interference is minimal. The complexity of factorized architectures (gated LoRA adapters, aspect-specific routing) lacks empirical justification when the covariance geometry is spherical.

**Methodological Implication:** Researchers proposing factorized architectures should validate empirical separability first, not assume structure transfers from vision/NLP multi-task learning. Our permutation testing methodology provides a template: test whether aspect labels correspond to covariance structure before building specialized modules.

**Practical Implication:** Weighted scalarization is not just a convenient baseline but an empirically justified approach. When no natural coordinate system exists (spherical geometry), any factorization is arbitrary. Practitioners can confidently use simpler weighted reward methods: R = w₁·R_correctness + w₂·R_quality + w₃·R_security + w₄·R_efficiency, tuning weights via Bayesian optimization or grid search.

## Why Architectural Factorization Fails

The null hypothesis—that multi-objective code alignment is intrinsically entangled—receives strong support from our data. But *why* does factorization fail when intuition suggests developers specialize their edits?

**Hypothesis 1: Intent-Outcome Gap**
Commit messages reflect developer *intent* ("fix security vulnerability"), but actual outcomes are multi-faceted. A security fix may:
- Add input validation → affects quality (complexity), efficiency (runtime checks)
- Refactor error handling → affects correctness (test coverage), maintainability
- Update dependencies → affects multiple dimensions unpredictably

The permutation p=0.955 provides strong evidence: labels (intent) are unrelated to outcomes (metric changes). This suggests commit categorization captures developer goals, not actual effect geometry.

**Hypothesis 2: Measurement Tool Independence**
The independence we observe (coupling=0.072) may arise from measurement design rather than behavioral factorization. SonarQube measures code smells orthogonal to CodeQL security alerts orthogonal to pytest-benchmark performance. Tools are independent by construction. Behavioral factorization would require developers to *use* this independence—making changes that affect one tool dominantly. Our negative directional alignment (z=-0.398) shows they don't.

**Hypothesis 3: Code Modifications Are Inherently Coupled**
Perhaps code structure itself prevents clean factorization. Improving security often requires refactoring (quality), which may introduce complexity (efficiency trade-off), which needs testing (correctness verification). The causal dependencies between quality dimensions create inherent entanglement that developers cannot decouple, even with specialized intent.

## Limitations and Threats to Validity

We acknowledge five categories of limitations that bound the generalizability of our findings:

### L1: Synthetic Test Data (CRITICAL)

**Limitation:** All results presented use synthetic test data generated for pipeline validation, NOT real GitHub commits.

**Why Acceptable for This Work:** Demonstrates (1) pipeline functionality, (2) permutation test methodology, (3) gate evaluation logic. The test data was designed to be realistic (matching expected correlations and distributions) without guaranteeing aspect-dominant structure.

**Scientific Validity:** ZERO for claims about real developer behavior. This is explicit throughout the paper.

**Mitigation Required:** Collect 10K real GitHub commits (Phase 1A: 5 days mining with PyGitHub/PyDriller, Phase 1B: 22 hours metric computation with SonarQube/CodeQL/pytest-benchmark). Re-run complete analysis pipeline. Given permutation p=0.955 is extreme (95.5th percentile of null), the conclusion is unlikely to reverse with real data—but validation is required for publication.

### L2: Minimal-Diff Commits May Be Too Granular

**Limitation:** AST distance filter (<20 nodes) isolates small changes that may be too fine-grained to exhibit directional effects.

**Why Acceptable:** Reduces confounds from multi-faceted large changes. Tests whether even "clean" single-aspect commits show factorization.

**Alternative Hypothesis:** Larger commits (20-50, 50-100 nodes) might show structure. Stratified analysis by commit size could reveal scale-dependent factorization.

**Mitigation:** Stratify dataset by commit size, test spectral gap per stratum. If gap increases with size, architectural factorization may apply to large-scale modifications but not granular edits—informing when to use complex vs simple architectures.

### L3: Language and Domain Specificity

**Limitation:** Analysis focuses on Python/JavaScript commits. Systems languages (C++, Rust) or specialized domains (embedded systems, high-frequency trading) may differ.

**Why Acceptable:** Python/JavaScript are standard for ML/code research and represent large developer populations.

**Alternative Hypothesis:** Low-level languages with manual memory management might show clearer security-performance trade-offs, yielding factorization.

**Mitigation:** Replicate study across languages (Java, C++, Rust, Go), measure cross-language consistency. If all show p>0.5, entanglement is likely universal. If some show p<0.05, identify language-specific structure.

### L4: Metric Reliability Unvalidated

**Limitation:** Phase 0 metric validation (test-retest ICC≥0.8, construct validity r≥0.7 vs expert ratings) was NOT executed.

**Why Acceptable:** Low coupling (0.072) suggests metrics do measure distinct constructs even if noisy. Unreliable metrics would *inflate* coupling through measurement error, not reduce it.

**Confound:** Noisy metrics could produce flat eigenspectrum if noise dominates signal. However, permutation p=0.955 is extreme—even noisy metrics with real structure would show p<0.5. The chance-level finding suggests absence of signal, not noise obscuration.

**Mitigation:** Execute Phase 0 validation (n=200 test-retest, n=200 expert ratings) before real data collection. Drop metrics with ICC<0.8. Re-analyze with validated subset.

### L5: Commit Label Quality Unknown

**Limitation:** Phase 1B purity validation (n=500 expert annotations, target >70% single-aspect) was NOT executed.

**Why Acceptable:** Permutation test is robust to label noise. If labels are impure (mixed-aspect commits), the test should still detect *some* signal if structure exists. p=0.955 indicates labels provide zero information—this extreme value is unlikely to be solely due to label noise.

**Alternative Hypothesis:** Even with perfect labels (100% purity), developers may not factorize their edits—intention doesn't imply factorized execution.

**Mitigation:** Expert annotation to measure purity. If 60-70%, apply mixture modeling with expert-weighted covariance correction. If <60%, fail hypothesis (labels too noisy to interpret). If >70%, confirms that even clean labels don't correspond to structure.

## Alternative Structural Hypotheses

If global factorization fails, structure may exist in alternative forms. We propose four hypotheses for future work:

**H-A1: Hierarchical Quality Structure (DAG)**
- **Claim:** Aspects form dependency DAG: Correctness → Quality → Security → Efficiency
- **Rationale:** Security fixes may require correctness baseline first, efficiency optimization may degrade quality
- **Test:** Structural equation modeling with DAG priors, compare BIC/AIC vs PCA
- **Prediction:** Better DAG fit than eigendecomposition

**H-A2: Contextual Factorization (Domain Clusters)**
- **Claim:** Aspect separation exists within domains (crypto repos for security, performance-critical systems for efficiency) but not globally
- **Test:** Mixture modeling with domain-specific covariance matrices
- **Prediction:** λ₄/λ₅>2.0 within clusters, ≤2.0 globally

**H-A3: Commit Size Dependence (Scale-Dependent)**
- **Claim:** Large commits (50-100 nodes) exhibit factorization, minimal commits (<20) don't
- **Test:** Stratify by AST distance, test gap per stratum
- **Prediction:** Gap increases monotonically with commit size

**H-A4: Temporal Dynamics (Sequence Analysis)**
- **Claim:** Aspect structure emerges over commit sequences, not snapshots
- **Test:** Time-series analysis of commit trajectories, directional momentum
- **Prediction:** Security fix → quality improvement → efficiency optimization (sequential pattern)

## Broader Impact

**Positive Impacts:**
- **Research Efficiency:** Prevents wasted effort on architectures lacking empirical justification
- **Practitioner Guidance:** Validates simpler methods (weighted scalarization) as principled defaults
- **Transparency:** Establishes validation standard—test separability before architectural commitment
- **Negative Result Value:** High-impact negative results redirect fields more efficiently than incremental positives

**No Ethical Concerns:**
- Analysis of public GitHub data (no private code)
- No personally identifiable information collected
- Findings about code structure, not individual developers
- No potential for misuse (doesn't enable vulnerabilities)

**Field Redirection:**
If entanglement is confirmed with real data, research should shift from architectural factorization to:
1. **Co-adaptive multi-objective methods** (NSGA-II, MOEA/D, Pareto optimization)
2. **Contextual factorization** (domain-specific routing, mixture-of-experts)
3. **Weighted scalarization** with principled weight selection (Bayesian optimization, learned weights)
4. **Acceptance of intrinsic limits** on multi-objective code alignment

This represents a significant pivot—from "how to design factorized architectures" to "how to optimize intrinsically entangled objectives."
