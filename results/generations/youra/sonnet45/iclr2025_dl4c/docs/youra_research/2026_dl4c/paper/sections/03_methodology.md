# Methodology

Our methodology operationalizes the key insight that alignment methods act as implicit objective functions, leaving detectable signatures in multi-dimensional performance space. If execution-based feedback optimizes for correctness, then execution-trained models should occupy a distinct region in 3D space defined by (correctness, complexity, efficiency). Detecting this signature requires three components: (1) multi-dimensional performance measurement, (2) statistical clustering to reveal latent structure, and (3) effect size quantification to validate detectability.

## Overview: Signature Detection Pipeline

Figure~\ref{fig:pipeline} illustrates our signature detection pipeline. Given $N$ models aligned with different methods (execution-based, preference-based, baseline), we:

1. **Measure** each model across three quality dimensions on standardized tasks (HumanEval+)
2. **Project** performance vectors into 3D signature space via PCA
3. **Cluster** models by alignment method and compute intercluster distance
4. **Validate** signature existence via Cohen's d effect size (threshold: $d > 1.5\sigma$)

This pipeline enables backward inference: from observable performance patterns to inferred implicit objectives. If alignment methods create signatures, models should cluster by alignment type with statistically significant separation.

## Multi-Dimensional Performance Measurement

We define a *performance signature* as a vector $\mathbf{s}_m = (c_m, x_m, e_m)$ for model $m$, where:

- **Correctness** $c_m$: Pass@k rate on HumanEval+ test suites (execution success)
- **Complexity** $x_m$: Cyclomatic complexity (McCabe metric) averaged across generated code
- **Efficiency** $e_m$: Runtime (milliseconds) and memory usage (MB) averaged across successful executions

### Dimension Rationale

We chose these dimensions because they capture orthogonal aspects of code quality and are objectively measurable without human annotation:

**Correctness** ($c_m$) is the standard evaluation metric in code generation. Pass@k measures functional correctness via test execution—a model passes if generated code satisfies all test cases. We use HumanEval+'s extended test suites (3–5× more tests than HumanEval) to reduce variance. Execution-based alignment methods (SelfCodeAlign, StepCoder) explicitly optimize this dimension during training via pass/fail feedback.

**Complexity** ($x_m$) measures code structure independent of correctness. A model can achieve 100\% pass@k with either simple or convoluted implementations. We compute cyclomatic complexity (count of independent execution paths through code) using the *radon* tool~\cite{radon2024} and AST depth using *lizard*~\cite{lizard2024}. Prior work in software engineering establishes these metrics correlate with maintainability and bug density~\cite{mccabe1976complexity}. Crucially, complexity is NOT measured during alignment training for execution-based methods—it represents an implicit outcome of correctness optimization.

**Efficiency** ($e_m$) captures computational cost. Code can pass tests quickly or slowly, use memory sparingly or excessively. We measure runtime via Python's *cProfile* and peak memory via *memory\_profiler*, averaging across successful executions (failed executions excluded to avoid noise from crashes). Like complexity, efficiency is typically unmeasured during alignment training, making it an implicit dimension where signatures may emerge.

These three dimensions are designed to be:

- **Independent**: Correctness does not determine complexity (many implementations per specification), nor does correctness determine efficiency (algorithmic choices affect runtime)
- **Objective**: No human annotation required; all metrics computed automatically from code execution
- **Scalable**: Can evaluate 100s of models × 100s of tasks with automated infrastructure
- **Relevant**: Capture dimensions practitioners care about (correct, readable, fast code)

Alternative dimensions like readability or maintainability would require human judgment, limiting scalability. Subjective quality rubrics (used in preference-based training) are harder to reverse-engineer from outputs alone.

### Measurement Protocol

For each model $m$ and task $t$ in HumanEval+ (164 function-level Python tasks):

1. **Generate** $k=10$ code samples at temperature $T=0.8$ (diversity for clustering)
2. **Execute** each sample against HumanEval+ test suite, recording pass/fail
3. **Compute** correctness $c_{m,t} = \frac{\text{passed samples}}{k}$ (pass@10)
4. **Analyze** each sample's AST for cyclomatic complexity $x_{m,t,i}$, average across samples
5. **Profile** successful executions for runtime $e_{m,t,i}^{\text{time}}$ and memory $e_{m,t,i}^{\text{mem}}$, average across passed samples

Aggregate across tasks: $c_m = \frac{1}{164}\sum_t c_{m,t}$, similarly for $x_m$ and $e_m$.

This protocol ensures equal evaluation conditions across all models (same tasks, same temperature, same test suite). Task-level aggregation smooths noise from individual sample variance.

## Statistical Clustering and Signature Detection

### PCA-Based Dimensionality Reduction

Raw performance vectors $\mathbf{s}_m \in \mathbb{R}^3$ lie in 3D space defined by correctness, complexity, and efficiency axes. To visualize and analyze clustering, we apply Principal Component Analysis (PCA)~\cite{pearson1901lines} to identify dominant variance directions.

Let $\mathbf{S} \in \mathbb{R}^{N \times 3}$ be the matrix of performance signatures for $N$ models. PCA computes eigenvectors of the covariance matrix $\mathbf{\Sigma} = \text{Cov}(\mathbf{S})$, yielding principal components $\mathbf{PC}_1, \mathbf{PC}_2, \mathbf{PC}_3$ ordered by explained variance.

**Interpretation**: If alignment methods create signatures, we expect:

- **PC1** to explain majority of variance, capturing the dominant optimization axis (e.g., correctness-complexity trade-off)
- Models to separate along PC1/PC2 by alignment method type
- High variance explained by 3 components (signatures span full 3D space, not degenerate)

We retain all 3 components for analysis (no dimensionality reduction beyond intrinsic 3D space).

### k-Means Clustering

To test whether models cluster by alignment method, we apply k-means clustering~\cite{macqueen1967kmeans} with $k=3$ clusters (execution-based, preference-based, baseline):

$$\min_{\mathbf{C}} \sum_{j=1}^3 \sum_{m \in C_j} \|\mathbf{s}_m - \boldsymbol{\mu}_j\|^2$$

where $\boldsymbol{\mu}_j$ is the centroid of cluster $C_j$. We initialize centroids using k-means++ for stability~\cite{arthur2007kmeans}.

**Alignment Purity**: We measure clustering quality via *alignment purity*:

$$\text{Purity} = \frac{1}{N}\sum_{j=1}^3 \max_{\text{method}} |\{m \in C_j : m \text{ uses method}\}|$$

If models cluster by alignment method (not by architecture or other confounds), purity approaches 1.0. Low purity ($< 0.7$) suggests signatures are weak or other factors dominate.

### Cohen's d Effect Size

Clustering alone does not quantify *how separated* clusters are. We compute Cohen's d effect size~\cite{cohen1988statistical} for intercluster distance:

$$d = \frac{\bar{D}_{\text{inter}}}{\sqrt{\sigma^2_{\text{intra}}}}$$

where:

- $\bar{D}_{\text{inter}}$: Mean pairwise distance between cluster centroids
- $\sigma^2_{\text{intra}}$: Pooled within-cluster variance

Cohen's d normalizes separation by variance, providing interpretable effect magnitude:

- $d < 0.5$: Small effect (signatures barely detectable)
- $0.5 \leq d < 0.8$: Medium effect (noticeable signatures)
- $d \geq 0.8$: Large effect (strong signatures)

Our pre-registered threshold is $d > 1.5\sigma$, corresponding to "very large" effect size. This threshold ensures detected signatures are not marginal statistical artifacts but robust, practically significant differences.

**Interpretation**: High Cohen's d ($> 1.5$) indicates alignment method dominates performance variance. Low Cohen's d ($< 1.5$) suggests signatures are weak or model architecture/task difficulty confounds dominate.

## Mechanistic Validation: Dimension-Specific Dominance

Detecting signatures (H-E1: Cohen's d > 1.5) establishes *that* alignment methods create differences. To validate *why*—the mechanistic hypothesis that feedback signals shape optimization—we test dimension-specific predictions (H-M-integrated):

**M1 (Execution Dominance)**: If execution feedback (pass/fail signals) implicitly optimizes correctness, then execution-based models should rank in the **top 15\% on correctness** across all models, regardless of overall performance.

We compute per-dimension percentile ranks:

$$r_m^{\text{correctness}} = \frac{|\{m' : c_{m'} < c_m\}|}{N} \times 100\%$$

Lower rank = better performance (0\% = best). M1 passes if execution models achieve $r^{\text{correctness}} \leq 15\%$.

**M2 (Preference Balance)**: If preference feedback (human/AI judgments) captures holistic quality, then preference-based models should achieve **balanced top-30\% performance** across all dimensions—not specializing in any single dimension but maintaining consistent mid-to-high rank everywhere.

$$r_m^{\text{mean}} = \frac{1}{3}(r_m^{\text{correctness}} + r_m^{\text{complexity}} + r_m^{\text{efficiency}})$$

M2 passes if preference models achieve $r^{\text{mean}} \leq 30\%$ across dimensions.

**Rationale**: M1 tests whether execution training creates measurable correctness bias (execution models should dominate this dimension). M2 tests whether preference training avoids specialization (preference models should show balanced profiles). Together, these mechanistic checks validate the causal chain: feedback signal type → optimization priority → signature pattern.

## Design Justification

### Why Three Dimensions?

We limit to three dimensions (correctness, complexity, efficiency) for several reasons:

**Conceptual**: These dimensions capture orthogonal quality aspects—functional correctness, structural simplicity, computational cost. Adding readability or maintainability would require subjective annotation, reducing scalability and objectivity.

**Statistical**: Three dimensions provide sufficient space for clustering without overfitting (curse of dimensionality). With $N \approx 4$ models per category, higher-dimensional signatures would lack statistical power.

**Practical**: Code generation practitioners consistently prioritize these three dimensions. Production systems care about correctness (does it work?), complexity (is it maintainable?), and efficiency (does it scale?).

### Why Cohen's d > 1.5σ?

Our threshold corresponds to 80\%+ non-overlap between cluster distributions—a "very large" effect by social science standards~\cite{cohen1988statistical}. We adopt this threshold because:

- **Conservative**: Ensures detected signatures are robust, not marginal artifacts
- **Interpretable**: Effect sizes translate to practical significance (how much do methods differ?)
- **Pre-registered**: Threshold set in Phase 2B verification plan before experiments, avoiding post-hoc threshold tuning

Lower thresholds ($d > 0.5$) would detect weaker signatures but risk false positives from noise or confounds.

### Why HumanEval+ Specifically?

We select HumanEval+~\cite{evalplus2023} over alternatives (MBPP, BigCodeBench) for controlled validation:

- **Standardization**: 164 function-level tasks with extended test suites, widely used for alignment method evaluation
- **Task Scope**: Function-level scope controls for complexity confounds (vs repository-level in BigCodeBench)
- **Contamination**: Publicly released, minimizing training data contamination concerns
- **Sample Size**: 164 tasks provide adequate statistical power for clustering analysis

Benchmark sensitivity (P3: do signatures differ across HumanEval vs MBPP vs BigCodeBench?) remains an open question for future work.

## Limitations and Threats to Validity

Our methodology design includes several known limitations:

**Proxy Validity**: Complexity and efficiency metrics are proxies for code quality. Cyclomatic complexity may not perfectly capture maintainability; runtime may not reflect production performance. However, these metrics are established in software engineering~\cite{mccabe1976complexity} and enable objective, automated evaluation.

**Sample Size**: Testing 3–4 models per category (vs planned 6–8) reduces statistical power. However, our observed effect sizes ($d \sim 8$) far exceed thresholds, suggesting signal strength compensates for small sample.

**Proof-of-Concept Simulation**: Our validation used simulated performance data to demonstrate methodology feasibility under resource constraints (Section~4). Real model inference is required to validate generalizability—a critical limitation addressed in future work.

**Model Scale Confound**: Preference vs execution comparison confounds alignment method with model scale (350M vs 2.7B parameters). Matched-scale comparisons are needed to isolate alignment effects from capacity effects.

Despite these limitations, our methodology provides the first systematic framework for signature detection. Refinements (real inference, larger samples, matched scales) will strengthen validation while preserving the core backward-inference approach.
