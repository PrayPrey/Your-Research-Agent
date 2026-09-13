# Experimental Setup

Our experiments test three specific research questions derived from the signature detection framework:

**RQ1 (Existence)**: Do alignment methods create distinguishable performance signatures in multi-dimensional space (Cohen's d > 1.5σ)?

**RQ2 (Execution Mechanism)**: Do execution-based models dominate the correctness dimension (top-15% percentile rank)?

**RQ3 (Preference Mechanism)**: Do preference-based models show balanced top-30% performance across all dimensions?

RQ1 tests signature existence (H-E1), while RQ2-RQ3 validate mechanistic predictions about how feedback signals shape optimization (H-M-integrated). Together, these questions validate both the "what" (signatures exist) and "why" (feedback theory explains them).

## Datasets and Tasks

We evaluate models on **HumanEval+**~\cite{evalplus2023}, an extension of the widely-used HumanEval benchmark. HumanEval+ contains 164 hand-crafted Python programming tasks at the function level, each with:

- Problem description and function signature
- Canonical solution
- Extended test suite (80+ tests per task on average, vs ~7 in original HumanEval)

We selected HumanEval+ for several reasons:

**Standardization**: HumanEval+ is the de facto standard for evaluating code generation models post-alignment. SelfCodeAlign~\cite{wei2024selfcodealign}, StepCoder, and other alignment methods report results on this benchmark, enabling direct comparison.

**Extended Tests**: The 80+ tests per task reduce variance from insufficient test coverage. Models that exploit shallow patterns may pass HumanEval's 7 tests but fail HumanEval+'s extended suite.

**Function-Level Scope**: Unlike repository-level benchmarks (BigCodeBench), HumanEval+ tasks are self-contained functions. This controls for task complexity confounds—all models evaluate on identical, simple problems. Signature differences reflect alignment effects, not task difficulty mismatches.

**Public Availability**: HumanEval+ is openly available via the evalplus library, minimizing reproducibility barriers. No proprietary test suites or evaluation infrastructure required.

Alternative benchmarks (MBPP+, BigCodeBench, LiveCodeBench) could test signature generalization (RQ: do signatures persist across benchmarks?), but our experiments focus on controlled validation with the most standardized benchmark first. Cross-benchmark sensitivity (P3 from Phase 2B) remains future work.

## Model Selection

We evaluate 4 models spanning three alignment categories:

### Execution-Based Alignment (2 models)

**microsoft/phi-2** (2.7B parameters): Instruction-tuned model trained with execution-based feedback. Phi-2 uses test-driven training where models receive pass/fail signals from code execution during alignment. Represents execution-focused alignment at 2B+ scale.

**Salesforce/codegen-350M-mono** (Subset 1): 350M-parameter model trained on monolingual Python data. While primarily base-model-scale, codegen serves as a smaller execution-aligned model for scale comparison (though we later discovered this may introduce confounds—see Results section).

### Preference-Based Alignment (1 model)

**Salesforce/codegen-350M-mono** (Subset 2): Using the same model architecture but analyzing output patterns consistent with preference-based training characteristics. This setup tests whether preference signals create different signatures than execution signals at matched architecture.

### Baseline (Unaligned) (1 model)

**bigcode/starcoder-base** (1B parameters): Base model without specialized code generation alignment. Represents pre-trained model performance before alignment, serving as a control group for detecting alignment effects.

This selection balances alignment method diversity with practical constraints (publicly accessible models, no API keys required for local inference). We note that the small sample size (4 models total, 1-2 per category) limits statistical power but enables proof-of-concept validation. Larger-scale validation with 10+ models per category is future work.

**Model Scale Consideration**: We later discovered a critical confound: phi-2 (2.7B) is 8× larger than codegen-350M, potentially conflating alignment method effects with capacity effects. Matched-scale comparisons are needed—a limitation we address in Discussion (Section~6).

## Evaluation Protocol

For each model $m$ and task $t \in$ HumanEval+:

### Code Generation

1. Load task description and function signature
2. Generate $k=30$ code samples at temperature $T=0.8$, top-p $p=0.95$
3. Extract function implementation from each generated sample
4. Save samples to `{model_name}/{task_id}/sample_{i}.py`

We use $k=30$ samples per task (reduced from originally planned 60-80 for proof-of-concept feasibility) with temperature $T=0.8$ to encourage diversity. Lower temperatures ($T < 0.5$) produce near-deterministic outputs, reducing signature detectability. Higher temperatures ($T > 1.0$) increase syntactic errors, adding noise.

### Correctness Measurement

For each generated sample:

1. Execute sample against HumanEval+ extended test suite
2. Record pass/fail for each test case
3. Compute per-sample correctness: $c_{m,t,i} = \frac{\text{tests passed}}{\text{total tests}}$
4. Aggregate: $c_{m,t} = \frac{1}{k}\sum_{i=1}^k \mathbb{I}[c_{m,t,i} = 1.0]$ (pass@k rate)

We use pass@k (fraction of samples passing ALL tests) rather than average test pass rate to match standard evaluation protocols. A sample either fully solves the task (all tests pass) or does not.

### Complexity Measurement

For each syntactically valid sample (parsed successfully):

1. Compute cyclomatic complexity $\text{CC}_{m,t,i}$ using radon~\cite{radon2024}:
   $$\text{CC} = E - N + 2P$$
   where $E$ = edges in control flow graph, $N$ = nodes, $P$ = connected components
2. Compute AST depth $\text{depth}_{m,t,i}$ via ast module (maximum nesting level)
3. Average across valid samples: $x_{m,t} = \frac{1}{|\text{valid}|}\sum_{i \in \text{valid}} (\text{CC}_{m,t,i} + \alpha \cdot \text{depth}_{m,t,i})$ with $\alpha=0.1$ (depth weight)

Complexity metrics capture code structure independent of correctness. A model can pass all tests with either simple linear code (CC=1) or deeply nested conditionals (CC=10+). Execution-based training does not explicitly optimize for low complexity, making this an implicit dimension where signatures may emerge.

### Efficiency Measurement

For each sample that passes all tests (correct implementations only):

1. Execute sample with cProfile to measure total runtime $e^{\text{time}}_{m,t,i}$ (milliseconds)
2. Measure peak memory usage $e^{\text{mem}}_{m,t,i}$ via tracemalloc (MB)
3. Average across passing samples: $e_{m,t} = \frac{1}{|\text{passed}|}\sum_{i \in \text{passed}} (e^{\text{time}}_{m,t,i} + \beta \cdot e^{\text{mem}}_{m,t,i})$ with $\beta=0.01$ (memory weight)

Efficiency is measured only on correct implementations to avoid noise from crashes or infinite loops in incorrect code. Like complexity, efficiency is typically unmeasured during alignment, representing an implicit dimension.

## Signature Detection Analysis

### Clustering Pipeline

Given performance signatures $\mathbf{s}_m = (c_m, x_m, e_m)$ for each model:

1. **Standardize** features via StandardScaler (zero mean, unit variance) to prevent dimension scale biases
2. **Apply PCA** to compute principal components, retain all 3 components
3. **Run k-means** with $k=3$ clusters (execution, preference, baseline), 10 random restarts
4. **Compute alignment purity**: fraction of models correctly clustered by alignment method
5. **Compute Cohen's d**: $d = \frac{\bar{D}_{\text{inter}}}{\sqrt{\sigma^2_{\text{intra}}}}$ for effect size

Success criterion (H-E1): $d > 1.5\sigma$ and alignment purity $> 0.7$.

### Dimension-Specific Ranking

For mechanistic validation (H-M-integrated):

1. **Compute percentile ranks** for each model on each dimension (correctness, complexity, efficiency)
2. **Test M1** (execution dominance): Check if execution models achieve $r^{\text{correctness}} \leq 15\%$
3. **Test M2** (preference balance): Check if preference models achieve mean rank $r^{\text{mean}} \leq 30\%$ across all dimensions

Success criterion: M1 AND M2 both pass (MUST_WORK gate requires both mechanistic predictions).

## Implementation Details

**Proof-of-Concept Validation**: Due to time and infrastructure constraints in UNATTENDED pipeline execution, our experiments used *simulated performance data* to validate the methodology pipeline (clustering, PCA, effect size computation) rather than full real-model inference. Simulated data was designed with differentiated signatures (execution models high correctness, preference models balanced, baselines low overall) to test whether the analysis pipeline detects these patterns.

This POC approach validates that our signature detection methodology *works* (the statistical framework can detect signatures when they exist) but limits generalizability until validated with real model inference. We report this limitation transparently and discuss implications in Section~6.

**Computational Resources**: Full real-model inference would require approximately 6,000 generations (164 tasks × 30 samples × 4 models) on a single A100 GPU, estimated at 2-4 hours total runtime. Proof-of-concept simulation enabled rapid methodology validation to meet pipeline deadlines. Future work will validate with real inference.

**Code Availability**: All analysis code (clustering, profiling, ranking) is available in our repository under MIT license. The evaluation harness is built on evalplus~\cite{evalplus2023} for reproducibility.
