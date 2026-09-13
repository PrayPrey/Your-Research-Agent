# 4. Experiments

## 4.1 Research Questions

Our Stage 1 validation (measurement reliability) tests three experimental questions that operationalize the hypothesis that proxy metrics can be reliably measured before RL optimization:

**RQ1 (CodeBLEU Reliability):** Does structural similarity (CodeBLEU) demonstrate measurement reliability across all three criteria: intra-implementation stability (CV ≤5%), inter-complexity-class discriminability (Cohen's d ≥0.8), and cross-platform generalization (Spearman ρ ≥0.8)?

**RQ2 (Runtime Efficiency Threshold):** Does runtime efficiency measurement (normalized instruction count) achieve the CV ≤5% threshold required for stable RL optimization signals?

**RQ3 (Gate Logic Functionality):** Does the multi-criteria validation gate correctly discriminate between reliable and unreliable proxies, allowing partial validation (≥1 proxy passes) to proceed rather than imposing all-or-nothing failure?

These questions test the four-stage validation pipeline's foundational premise: that measurement reliability can be systematically validated *before* investing in multi-objective RL training. RQ1 and RQ2 test whether specific proxy dimensions meet construct validity criteria; RQ3 tests whether the validation framework itself functions as designed.

## 4.2 Experimental Design

### 4.2.1 Proof-of-Concept Scope

This Phase 4 implementation is a **proof-of-concept** demonstration validating the four-stage pipeline's methodology before infrastructure investment. The full implementation would require:

- **GPU Infrastructure:** CodeLlama-7B-Instruct (16GB+ VRAM)
- **Dataset:** HumanEval (164 programming problems)
- **Hardware Performance Tools:** Linux `perf` for CPU instruction counting
- **Cross-Platform Setup:** AWS g4dn.xlarge + local GPU

**PoC Strategy:** We validate the statistical framework, gate logic, and visualization pipeline using synthetic measurements (500 solutions × 5 repetitions × 3 metrics = 7,500 data points). This two-phase approach (PoC methodology validation → real infrastructure validation) reduces the risk of investing 1,000+ GPU hours in a potentially flawed framework.

**PoC Success Criteria:**
- Code executes without error
- Statistical computations (CV, Cohen's d, Spearman ρ) produce interpretable results
- Gate logic discriminates between passing and failing proxies
- At least ONE proxy validates (minimum threshold for continuation)

### 4.2.2 Datasets and Controlled Tasks

**Primary Evaluation Dataset:** We selected 50 problems from HumanEval (Chen et al., 2021), the standard benchmark for code generation comprising 164 hand-crafted Python programming tasks. Each problem provides:
- Function signature with type hints
- Natural language docstring describing the task
- Unit tests for functional correctness
- Canonical solution for reference

HumanEval was chosen because it represents the community standard for code generation evaluation, enabling comparison with prior work (CodeRL, CURE, CodeUltraFeedback) while providing well-defined test cases for execution correctness validation.

**Controlled Complexity Tasks:** To test inter-complexity-class discriminability (Cohen's d ≥0.8), we generated 51 synthetic programming problems with labeled optimal algorithmic complexity:
- 17 O(n) tasks (linear search, single-pass array processing)
- 17 O(n log n) tasks (merge sort, binary search variants)
- 17 O(n²) tasks (nested loops, pairwise comparisons)

These controlled tasks provide ground truth for complexity class separation. A reliable proxy metric should assign significantly different scores to O(n) vs O(n²) solutions, reflected in large effect size (Cohen's d ≥0.8).

**Cross-Platform Simulation:** We simulated cross-platform measurements by adding Gaussian noise (σ = 3% of mean) to model hardware-dependent variance. This tests whether rank orderings preserve across measurement conditions (Spearman ρ ≥0.8).

### 4.2.3 Proxy Metrics

**Proxy 1: Structural Similarity (CodeBLEU)**

CodeBLEU (Ren et al., 2020) is a weighted combination of four sub-metrics capturing different aspects of code similarity:
1. **N-gram match (BLEU):** Surface-level grammatical similarity
2. **Weighted n-gram match:** Token importance weighting via TF-IDF
3. **AST match:** Syntactic structure similarity (abstract syntax tree overlap)
4. **Dataflow match:** Semantic logic similarity (variable dependencies)

We use the `k4black/codebleu` implementation (PyPI v0.7.0) with equal weighting (0.25, 0.25, 0.25, 0.25) across sub-metrics. CodeBLEU was selected because:
- **Deterministic computation:** AST parsing and dataflow analysis have no randomness → expected CV ≈0-2%
- **Structural validation:** Prior work (Chen et al., 2021) validated correlation with human judgment; we extend to measurement reliability
- **Community adoption:** Used in code generation benchmarks (CodeXGLUE, HumanEval extensions)

**Proxy 2: Runtime Efficiency (Normalized Instruction Count)**

Runtime efficiency is measured as normalized CPU instruction count ratio:
```
efficiency_score = reference_instructions / max(solution_instructions, 1)
```

Following COFFE (2025), we use CPU instruction counting rather than wall-clock execution time. The Patterson & Hennessy CPU time equation shows:
```
CPU Time = [Instruction Count] × [CPI] × [Clock Cycle Time]
```

Only Instruction Count is program-dependent; CPI and Clock Cycle Time are hardware-dependent. By measuring instruction count directly via Linux `perf` hardware counters, measurement noise from OS scheduling, thermal throttling, and I/O latency is eliminated. COFFE reports instruction-count CV ~2-3% on real hardware.

**PoC Implementation Note:** Our PoC uses synthetic noise modeling (Gaussian σ = 5%) to simulate measurement variability, as hardware performance counters require physical infrastructure. Real validation would use `perf stat -e instructions` to achieve COFFE's reported 2-3% CV.

**Proxy 3: Learned PR-Style Score**

The PR-style proxy evaluates code style conformity against developer acceptance patterns, requiring:
- **Training Data:** SWE-bench dataset with PR acceptance labels
- **Model:** CodeBERT fine-tuned on accepted vs rejected PR diffs
- **Evaluation:** Style conformity score (0-1)

**PoC Implementation Note:** This proxy is implemented as a placeholder (random score generator) in the PoC, as training infrastructure exceeds PoC scope. Phase 2C verification plan documented this as deferred to future work. We include it in gate evaluation to demonstrate that the framework correctly handles expected failures (not all proxies must validate for continuation).

## 4.3 Measurement Reliability Criteria

### 4.3.1 Coefficient of Variation (CV ≤5%)

**Definition:** CV = (σ / μ) × 100%, measuring intra-implementation variability.

**Measurement Protocol:** Each of the 500 generated solutions is evaluated 5 times with the same proxy metric. CV quantifies measurement noise: how much does the metric score vary when applied repeatedly to identical code?

**Threshold Rationale:** CV ≤5% is standard in measurement theory for high-reliability instruments (e.g., laboratory equipment, psychometric scales). For RL optimization, higher CV introduces noise into the reward signal, slowing convergence or causing instability. Our threshold ensures that 95% of variance in proxy scores reflects actual code quality differences, not measurement noise.

**Statistical Framework:**
```
For each solution s:
    scores = [metric(s) for rep in 1..5]
    CV(s) = (std(scores) / mean(scores)) * 100
    
Aggregate: mean_CV = mean(CV over all solutions)
Gate criterion: mean_CV ≤ 5.0%
```

### 4.3.2 Cohen's d (≥0.8)

**Definition:** Effect size for inter-group separation, d = (μ₁ - μ₂) / σ_pooled, measuring discriminability between complexity classes.

**Measurement Protocol:** We evaluate proxy metrics on controlled O(n) vs O(n²) tasks (17 problems each). Cohen's d quantifies whether the metric assigns systematically different scores to different algorithmic complexities.

**Threshold Rationale:** Cohen's d ≥0.8 represents a "large effect" by conventional standards (Cohen, 1988). A reliable quality proxy should clearly distinguish efficient (O(n)) from inefficient (O(n²)) implementations. Smaller effect sizes (d < 0.8) indicate insufficient discriminability: the metric cannot reliably separate complexity classes, making it unsuitable for efficiency-aware optimization.

**Statistical Framework:**
```
O(n)_scores = [metric(s) for s in O(n) solutions]
O(n²)_scores = [metric(s) for s in O(n²) solutions]

pooled_std = sqrt(((n₁-1)*var₁ + (n₂-1)*var₂) / (n₁+n₂-2))
d = (mean(O(n)_scores) - mean(O(n²)_scores)) / pooled_std

Gate criterion: d ≥ 0.8
```

### 4.3.3 Spearman ρ (≥0.8)

**Definition:** Rank correlation coefficient, ρ = correlation(rank(X), rank(Y)), measuring cross-platform stability.

**Measurement Protocol:** We simulate two measurement platforms (AWS GPU vs local GPU) by adding independent Gaussian noise to metric scores. Spearman ρ tests whether the rank ordering of solutions is preserved across platforms.

**Threshold Rationale:** ρ ≥0.8 indicates strong monotonic relationship. A reliable proxy should produce consistent rankings regardless of hardware platform (within-architecture, e.g., NVIDIA A100 vs V100). Lower ρ suggests platform-specific artifacts (e.g., hardware-dependent timing variability) that would cause RL training to optimize for platform-specific rather than algorithmic properties.

**Statistical Framework:**
```
platform_A_scores = [metric(s, platform="A") for s in solutions]
platform_B_scores = [metric(s, platform="B") for s in solutions]

ρ, p_value = spearmanr(platform_A_scores, platform_B_scores)

Gate criterion: ρ ≥ 0.8 AND p < 0.01
```

## 4.4 Multi-Criteria Gate Logic

### 4.4.1 Scoped MUST_WORK Gate

**Gate Design:** Each proxy metric must pass ALL three criteria (CV ≤5% AND Cohen's d ≥0.8 AND Spearman ρ ≥0.8) to be considered validated. The gate evaluates N proxies × M criteria, producing a per-proxy validation matrix.

**Scoped Success Criterion:** ≥1 proxy fully validates → gate PASSES with reduced proxy set.

**Rationale:** This scoped design prevents all-or-nothing failure. If CodeBLEU validates but runtime efficiency fails due to hardware instrumentation limitations, we proceed with structural similarity optimization only. Partial validation is scientifically valid: downstream hypotheses (h-e2, h-m1) can test conditional independence and multi-objective RL with whatever proxies survive Stage 1.

**Gate Logic:**
```python
validated_proxies = []
for proxy in [CodeBLEU, Runtime, PR_style]:
    passes_cv = proxy.cv <= 5.0
    passes_cohens_d = proxy.cohens_d >= 0.8
    passes_spearman = proxy.spearman_rho >= 0.8
    
    if passes_cv AND passes_cohens_d AND passes_spearman:
        validated_proxies.append(proxy)

gate_verdict = "PASS" if len(validated_proxies) >= 1 else "FAIL"
```

**Failure Routing:** If zero proxies validate (gate FAILS), the hypothesis routes to Phase 0 (brainstorming) to explore alternative quality dimensions or measurement approaches.

### 4.4.2 Visualization Pipeline

To facilitate rapid assessment of gate results, we generate a **Gate Metrics Comparison** bar chart (Figure 1) showing:
- Three groups (CV, Cohen's d, Spearman ρ)
- Three bars per group (CodeBLEU, Runtime, PR-style)
- Threshold lines (CV: 5.0%, Cohen's d: 0.8, Spearman ρ: 0.8)
- Color coding: green bars indicate passing criteria, red bars indicate failures

This visualization makes the compositional validation insight immediately visible: different proxies have different measurement profiles.

## 4.5 Implementation and Reproducibility

**Programming Environment:**
- Python 3.10
- Libraries: `numpy`, `scipy`, `matplotlib`, `codebleu` (PyPI)
- Random seed: 42 (fixed for deterministic PoC results)

**Code Structure:**
```
h-e1/code/
├── config.py          # Configuration schema (thresholds, parameters)
├── main.py            # PoC implementation (ProxyMetricPoC class)
├── requirements.txt   # Dependencies
├── outputs/
│   └── results.json   # Experiment results
└── figures/
    └── gate_metrics.png  # Gate visualization
```

**Computational Cost:**
- PoC runtime: ~2 minutes (synthetic data generation + statistical computation)
- Memory: <1GB (500 solutions × 5 reps × 3 metrics)
- Hardware: CPU-only (no GPU required for PoC)

**Real Implementation Estimate:**
- Solution generation: ~100 GPU hours (50 problems × 10 solutions × CodeLlama-7B inference)
- Metric evaluation: ~10 CPU hours (CodeBLEU, perf measurements)
- Total timeline: 2-4 weeks
- Cost: ~$50-100 (AWS g4dn.xlarge spot pricing)

## 4.6 Ethical Considerations

This work evaluates measurement methodologies for code generation quality assessment. Key ethical considerations:

**No Human Subjects:** All evaluations use automated metrics on code artifacts. No human annotation or user studies.

**Computational Resources:** PoC uses minimal compute (~2 min CPU time). Real validation (~100 GPU hours) is small compared to typical RL training runs (1,000+ GPU hours). Early-stage proxy filtering *reduces* total compute waste by preventing optimization on unmeasurable signals.

**Open Science:** PoC code and synthetic data will be released to enable reproducibility and community extension to other proxy dimensions (modularity, maintainability, documentation coverage).

**Benchmark Data:** HumanEval is publicly available under MIT license. All problems are hand-crafted by OpenAI researchers, not scraped from GitHub (avoiding copyright concerns).
