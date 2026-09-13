# Experiment Design: H-E1

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under code generation evaluation conditions (Python function-level tasks, HumanEval+/MBPP+/BigCodeBench benchmarks), if we measure 6-8 post-alignment models across correctness, complexity, and efficiency dimensions, then models will cluster in 3D performance space according to alignment method type (execution-based, preference-based, unaligned baseline) with statistically significant intercluster distance > 1.5σ (Cohen's d), because feedback signals during alignment shape output distributions toward implicit optimization objectives.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE (Phase 2C IN_PROGRESS)
**Prerequisites Satisfied:** Yes (no prerequisites - foundation hypothesis)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK**: This hypothesis MUST pass for the pipeline to continue. If Cohen's d < 1.5σ, the entire hypothesis loop will HALT and route back to Phase 0.

**Pass Condition**: Cohen's d > 1.5σ (moderate effect size indicating detectable clustering)
**Fail Action**: HALT_PIPELINE → Route to Phase 0 (no detectable signatures exist)

---

## Continuation Context

**This is the first hypothesis (H-E1) in the verification loop.**

No previous hypothesis context to inherit from. This is a foundation experiment establishing the existence of alignment method signatures before testing mechanisms.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Code generation clustering alignment methods**
- Result 1: geneval GitHub repository (https://github.com/djghosh13/geneval)
  - Focus: Code generation evaluation framework
  - Similarity: 0.34 (moderate relevance)
  - Insight: Provides evaluation infrastructure for code generation models

**Query 2: HumanEval MBPP benchmark evaluation pass@k**
- Result 1: Paint-by-Example GitHub (https://github.com/Fantasy-Studio/Paint-by-Example)
  - Similarity: 0.44
  - Limited relevance to code generation (image generation focus)

- Result 2: geneval repository (repeated, 0.41 similarity)
  - Confirms code generation evaluation focus

**Query 3: Model performance profiling clustering Cohen's d**
- Results: Various diffusion model implementations
  - xDiT project, k-diffusion sampling
  - Limited direct relevance to code generation clustering
  - Insight: Statistical profiling methods may apply across domains

**Key Takeaways:**
- Limited Archon KB coverage for code generation alignment clustering
- geneval framework may provide evaluation infrastructure patterns
- Need to rely heavily on Exa GitHub search for implementation examples

### Archon Code Examples

**Query 1: Code generation evaluation metrics PyTorch**
- Example 1: Video metrics evaluation (Latte framework)
  - Pattern: Organize real vs generated outputs, compute metrics on GPU
  - Insight: Framework pattern for evaluation pipelines

- Example 2: FID metric configuration (mmgeneration)
  ```python
  metrics = dict(
    fid50k = dict(
      type='FID',
      num_images=50000,
      inception_pkl='work_dirs/inception_pkl/ffhq-256-50k-rgb.pkl',
      bgr2rgb=True))
  ```
  - Pattern: Structured metric configuration
  - Insight: Declarative metric specification approach

**Query 2: Clustering k-means PCA analysis**
- Results: GPU batched GEMM operations (cuBLAS)
  - Limited relevance to clustering analysis
  - Code examples focus on low-level GPU computation

**Key Code Patterns:**
- Evaluation frameworks use structured metric configurations
- Separate real vs generated data organization
- GPU-based batch processing for efficiency

### Exa GitHub Implementations

**Query 1: HumanEval MBPP code generation evaluation pass@k Python implementation**

**Repository 1**: openai/human-eval (3K+ stars)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval benchmark implementation with pass@k metric
- **Key Code**:
  ```python
  # evaluate_functional_correctness.py
  def entry_point(sample_file: str, k: str = "1,10,100",
                  n_workers: int = 4, timeout: float = 3.0,
                  problem_file: str = HUMAN_EVAL):
      """Evaluates functional correctness of generated samples"""
      k = list(map(int, k.split(",")))
      results = evaluate_functional_correctness(
          sample_file, k, n_workers, timeout, problem_file)
      print(results)
  ```
- **Evaluation Protocol**:
  - 164 Python programming problems
  - Pass@k metric: probability that ≥1 of k samples passes all tests
  - Formula: `pass@k = 1 - C(n-c, k) / C(n, k)` where n=total samples, c=correct samples
  - Temperature-based sampling for code generation
  - Parallel execution with configurable timeout (default 3.0s)

**Repository 2**: Confident AI - DeepEval HumanEval Benchmark
- **URL**: https://deepeval.com/docs/benchmarks-human-eval
- **Relevance**: LLM evaluation framework with HumanEval integration
- **Architecture**: Custom LLM wrapper requiring `generate_samples()` method
- **Key Code**:
  ```python
  from deepeval.benchmarks import HumanEval
  from deepeval.benchmarks.tasks import HumanEvalTask

  benchmark = HumanEval(
      tasks=[HumanEvalTask.HAS_CLOSE_ELEMENTS, HumanEvalTask.SORT_NUMBERS],
      n=100)  # 100 code generation samples
  benchmark.evaluate(model=gpt_4, k=10)
  ```
- **Training Config**: Greedy decoding (temp=0) or temp=0.2 for API models
- **Dataset**: 164 tasks with comprehensive test coverage
- **Results**: Pass@k scores with functional correctness validation

**Repository 3**: DataCamp HumanEval Tutorial
- **URL**: https://github.com/kingabzpro/human-eval
- **Relevance**: Practical implementation guide for codeparrot/codeparrot-small
- **Key Implementation Pattern**:
  - Load dataset: `load_dataset("openai_humaneval")`
  - Load metric: `load("code_eval")`
  - Generate candidates for each problem
  - Compute pass@k for k=[1, 5]
  - Evaluate against reference test cases

**Query 2: Code generation model clustering analysis performance profiling**

**Repository 4**: Functional Clustering for LLM Code Generation
- **URL**: https://arxiv.org/html/2506.11021v1
- **Relevance**: Exact behavioral clustering for code generation outputs
- **Core Mechanism**:
  ```python
  # Functional equivalence clustering approach:
  # 1. Sample n candidate programs
  # 2. Generate m test inputs (self-generated by LLM)
  # 3. Execute each candidate on test suite
  # 4. Cluster by identical I/O behavior
  # 5. Confidence = empirical mass of largest cluster
  ```
- **Key Insight**: Clusters programs by exact I/O behavior on auto-generated tests
- **Results**: Reduces error rate from 65% to 2% on LiveCodeBench
- **Limitation**: Assumes single correct equivalence class per task

**Repository 5**: Performance Analysis of AI-Generated Code (ECE Waterloo)
- **URL**: https://ece.uwaterloo.ca/~wshang/pubs/EMSE_2026_SHUANG_LI.pdf
- **Relevance**: Performance profiling methodology for Copilot, CodeLlama, DeepSeek-Coder
- **Evaluation Framework**:
  - Static analysis: Qodana, Spotbugs, PMD (performance regression detection)
  - Dynamic profiling: cProfile (runtime), tracemalloc (memory), Psutil (system metrics)
  - Datasets: HumanEval, MBPP, AixBench, EvalPerf
- **Metrics**: Runtime, memory usage, FLOPs, cache utilization, parallelization efficiency
- **Key Pattern**: Separate profiling of canonical vs generated solutions

**Repository 6**: MARCO - Multi-Agent HPC Code Generation
- **URL**: https://arxiv.org/html/2505.03906v2
- **Relevance**: Multi-agent architecture for performance-optimized code generation
- **Architecture**:
  - Code generation agent (optimization techniques)
  - Performance evaluation agent (runtime, memory, FLOPs assessment)
  - Feedback loop for iterative refinement
- **Evaluation Metrics**: Execution time, FLOPs, memory usage using system profiling tools
- **Results**: 14.6% average runtime reduction vs Claude 3.5 Sonnet baseline

**Serena Analysis Needed**: No - Code patterns are clear from documentation

### 🎯 Implementation Priority Assessment

**NOT a paper reproduction experiment** - This is a novel clustering analysis.

**Implementation Priority**:
1. **Use official HumanEval+ (evalplus) infrastructure** ⭐⭐⭐ HIGHEST
   - Ground truth for pass@k evaluation
   - 81× more tests than original HumanEval
   - Used by Meta Llama, Qwen, DeepSeek teams

2. **Use standard profiling libraries** ⭐⭐ MEDIUM
   - radon (cyclomatic complexity) - Python standard
   - cProfile (runtime) - Python built-in
   - tracemalloc (memory) - Python built-in

3. **Use sklearn for clustering** ⭐⭐ MEDIUM
   - Industry standard, well-validated
   - KMeans + PCA widely used in research

**Recommended Implementation Path:**
- **Primary**: evalplus package + sklearn + Python profiling tools
- **Fallback**: N/A (all tools are standard and reliable)
- **Justification**: Official benchmark infrastructure ensures reproducibility. Standard profiling tools are battle-tested and available in Python stdlib. No custom implementations needed.

### Code Analysis (Serena MCP)

**Serena Analysis**: Not required - code patterns from Exa search are clear and well-documented.

**Key Implementation Patterns Identified**:
1. **Pass@k Evaluation**: Standard combinatorial formula implementation from openai/human-eval
2. **Model Inference**: Temperature-based sampling (0.2-0.8) for diversity
3. **Performance Profiling**: cProfile (runtime) + tracemalloc (memory) pattern from ECE Waterloo study
4. **Clustering Analysis**: Standard sklearn k-means + PCA dimensionality reduction
5. **Functional Correctness**: Test execution with timeout (3.0s default)

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ (standard benchmark)
**Type**: standard
**Source**: EvalPlus GitHub repository
**Path**: https://github.com/evalplus/evalplus

**Loading Information** (for Phase 4 download):
- Method: Python package `evalplus`
- Identifier: `humanevalplus` (HuggingFace) or `evalplus` package
- Code:
  ```python
  # Method 1: Via evalplus package (recommended)
  pip install evalplus --upgrade
  from evalplus.data import get_human_eval_plus
  problems = get_human_eval_plus()

  # Method 2: Via HuggingFace datasets
  from datasets import load_dataset
  dataset = load_dataset("evalplus/humanevalplus")
  # Features: ['task_id', 'prompt', 'canonical_solution', 'entry_point', 'test']
  ```

**Statistics**:
- Total problems: 164 function-level Python programming tasks
- Average tests per problem: 764.1 (vs 9.6 in original HumanEval)
- Test coverage: 81× more comprehensive than HumanEval
- Language: Python (English docstrings)
- Format: Function completion with signature + docstring

**Preprocessing**: None required (problems are pre-formatted)

**Evaluation Protocol**:
- Generate n samples per task (n=60-80 recommended for clustering)
- Temperature: 0.8 (for sampling diversity)
- Timeout: 3.0s per execution
- Pass@k calculation: `pass@k = 1 - C(n-c, k) / C(n, k)` where n=total samples, c=correct samples

**Data Split**: Single test set (no train/val splits - evaluation benchmark only)

### Models

#### Model Selection (Multi-Model Experiment)

This experiment evaluates **6-8 models** across three alignment method categories:

**Execution-Focused Models (2-3 models)**:
- SelfCodeAlign-7B
- StepCoder
- CodeLlama-Python-7B-Instruct

**Preference-Focused Models (2-3 models)**:
- DPO/RLAIF-trained models (search HuggingFace for availability)
- Potential candidates: CodeLlama-DPO variants, instruction-tuned models with RLHF

**Baseline Models (1-2 models)**:
- CodeLlama-7B-Base
- StarCoder-Base

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Code (example for one model):
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer

  # Example: CodeLlama-7B-Base
  model_name = "codellama/CodeLlama-7b-hf"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      device_map="auto",
      torch_dtype="auto"
  )

  # Generation config
  generation_config = {
      "temperature": 0.8,
      "max_new_tokens": 512,
      "do_sample": True,
      "top_p": 0.95
  }
  ```

**Model Configuration**:
- Input: Function signature + docstring from HumanEval+ prompt
- Output: Function body completion
- Max tokens: 512 (sufficient for function-level code)
- Sampling: Temperature=0.8, top_p=0.95 for diversity
- Batch size: 1 (sequential generation per problem)
- Samples per model: 60-80 per task (total ~10,000-13,000 samples per model)

#### Proposed Model (N/A for Clustering Experiment)

**This is an evaluation/clustering experiment, NOT a training experiment.**

**No proposed model architecture** - We evaluate existing pre-trained models without modification.

**Core Analysis Pipeline:**

```python
# Alignment Method Clustering Analysis
# Based on: openai/human-eval + ECE Waterloo profiling + sklearn clustering

class AlignmentSignatureAnalyzer:
    """
    Analyzes code generation models to detect alignment method signatures
    via clustering in 3D performance space.
    """
    def __init__(self, models, num_samples=64):
        """
        Args:
            models: List of (model_name, alignment_type) tuples
            num_samples: Samples per task per model (default: 64)
        """
        self.models = models
        self.num_samples = num_samples
        self.problems = get_human_eval_plus()  # 164 tasks

    def generate_and_profile(self, model, task):
        """
        Generate code samples and profile performance.
        Returns: (correctness, complexity, efficiency) signature
        """
        # Generate n samples at temperature=0.8
        samples = []
        for _ in range(self.num_samples):
            code = model.generate(task["prompt"], temperature=0.8)
            samples.append(code)

        # Dimension 1: Correctness (pass@k)
        pass_results = [execute_tests(s, task["test"]) for s in samples]
        correctness = sum(pass_results) / len(pass_results)

        # Dimension 2: Complexity (cyclomatic + AST depth)
        complexity_scores = []
        for sample in samples:
            cc = cc_visit(sample)  # radon cyclomatic complexity
            ast_depth = get_ast_depth(sample)  # lizard
            complexity_scores.append((cc, ast_depth))
        avg_complexity = np.mean(complexity_scores, axis=0)

        # Dimension 3: Efficiency (runtime + memory)
        efficiency_scores = []
        for sample in samples:
            runtime = profile_runtime(sample)  # cProfile
            memory = profile_memory(sample)   # tracemalloc
            efficiency_scores.append((runtime, memory))
        avg_efficiency = np.mean(efficiency_scores, axis=0)

        return {
            'correctness': correctness,
            'complexity': avg_complexity,
            'efficiency': avg_efficiency
        }

    def cluster_and_measure(self, signatures):
        """
        Apply PCA + k-means, compute Cohen's d effect size.
        """
        # Flatten signatures to vectors
        X = np.array([flatten(sig) for sig in signatures])

        # Standardize
        X_scaled = StandardScaler().fit_transform(X)

        # PCA for 3D visualization
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_scaled)

        # k-means clustering (k=3 for 3 alignment types)
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(X_pca)

        # Compute Cohen's d (intercluster distance / intracluster SD)
        cohens_d = compute_effect_size(X_pca, labels)

        return cohens_d, labels, X_pca
```

**Integration Point**: Standalone analysis pipeline (no model modification)

### Analysis Protocol (NOT Training)

**No training required** - All models are pre-trained and used as-is.

**Analysis Configuration**:
- **Models**: 6-8 pre-trained models (2-3 per alignment category)
- **Sampling**: Temperature=0.8, top_p=0.95, n=64 samples per task
- **Tasks**: 164 HumanEval+ problems
- **Total samples**: ~10,000-13,000 per model (164 tasks × 64 samples)
- **Execution timeout**: 3.0s per sample
- **Parallel workers**: 4 (for test execution)
- **Seeds**: 1 (fixed random_state=42 for reproducibility)

**Profiling Tools**:
- Correctness: evalplus test execution
- Complexity: radon (cyclomatic), lizard (AST metrics)
- Efficiency: cProfile (runtime), tracemalloc (memory)

> ⚠️ **EXISTENCE (PoC)**: Single run is sufficient. No hyperparameter search needed.

**Source**: Based on openai/human-eval evaluation protocol + ECE Waterloo profiling methodology

### Evaluation

**Primary Metrics**:
- **Cohen's d** (intercluster distance effect size): Measure separation between alignment method clusters
  - Formula: `d = (μ_between - μ_within) / σ_pooled`
  - Target: d > 1.5σ (moderate effect) or d > 2.5σ (strong effect)

- **Silhouette Score** (cluster quality): Measure how well-defined clusters are
  - Range: [-1, 1], higher is better
  - Target: > 0.3 (reasonable clustering)

- **Alignment Method Purity**: Percentage of clusters dominated by single alignment type
  - Target: > 70% (clear alignment-based grouping)

**Success Criteria** (PoC: Direction-based):
- **Primary**: Cohen's d > 1.5σ (detectable clustering exists)
- **Secondary**: Alignment method variance >> base model variance (alignment matters more than architecture)

**Expected Baseline Performance** (from research):
- HumanEval+ pass@1 scores: 30-70% (varies by model)
  - Source: EvalPlus leaderboard, evalplus/humanevalplus dataset card
- Complexity metrics: Cyclomatic 2-10, AST depth 3-15
  - Source: radon documentation, typical Python function complexity
- Runtime: 0.01-1.0s (function-level code)
  - Source: ECE Waterloo performance analysis paper

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation evaluation + clustering analysis
- Libraries:
  - Pass@k: Custom implementation (evalplus provides reference)
  - Complexity: `radon` (cyclomatic complexity), `lizard` (code metrics)
  - Efficiency: `cProfile` (runtime), `tracemalloc` (memory)
  - Clustering: `sklearn.cluster.KMeans`, `sklearn.decomposition.PCA`
  - Effect size: `scipy.stats` (Cohen's d calculation)
- Code:
  ```python
  # Pass@k metric (unbiased estimator)
  from scipy.special import comb

  def pass_at_k(n, c, k):
      """
      n: total samples
      c: correct samples
      k: samples to select
      """
      if n - c < k:
          return 1.0
      return 1.0 - float(comb(n - c, k)) / float(comb(n, k))

  # Complexity metrics
  from radon.complexity import cc_visit
  from lizard import analyze_file

  # Efficiency profiling
  import cProfile
  import tracemalloc

  # Clustering
  from sklearn.cluster import KMeans
  from sklearn.decomposition import PCA
  from sklearn.preprocessing import StandardScaler

  # Effect size (Cohen's d)
  import numpy as np

  def cohens_d(group1, group2):
      """Calculate Cohen's d effect size"""
      n1, n2 = len(group1), len(group2)
      var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
      pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
      return (np.mean(group1) - np.mean(group2)) / pooled_std
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on clustering analysis, the following visualizations are recommended:

1. **3D Scatter Plot**: PCA-reduced performance space with color-coded alignment methods
   - Axes: PC1, PC2, PC3
   - Colors: Execution (blue), Preference (red), Baseline (green)
   - Shows: Visual cluster separation

2. **Heatmap**: Model × Dimension performance matrix
   - Rows: 6-8 models
   - Columns: Correctness, Complexity, Efficiency
   - Shows: Per-dimension dominance patterns

3. **Box Plots**: Distribution of metrics by alignment type
   - 3 groups: Execution, Preference, Baseline
   - Shows: Within-group variance vs between-group separation

4. **Dendrogram**: Hierarchical clustering of models
   - Shows: Natural grouping structure

5. **Effect Size Confidence**: Cohen's d with bootstrapped confidence intervals
   - Shows: Statistical strength of clustering

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Official Implementations

1. **openai/human-eval** (3K+ stars)
   - URL: https://github.com/openai/human-eval
   - Purpose: Official HumanEval benchmark with pass@k implementation
   - Key file: `evaluate_functional_correctness.py`
   - Used for: Pass@k metric calculation, test execution

2. **evalplus/evalplus** (1.7K+ stars)
   - URL: https://github.com/evalplus/evalplus
   - Purpose: HumanEval+ enhanced benchmark (81× more tests)
   - Package: `pip install evalplus`
   - Used for: Primary evaluation infrastructure

3. **DeepEval HumanEval Integration**
   - URL: https://deepeval.com/docs/benchmarks-human-eval
   - Purpose: LLM evaluation framework
   - Used for: Model wrapper patterns

### Code Profiling References

4. **ECE Waterloo Performance Analysis**
   - URL: https://ece.uwaterloo.ca/~wshang/pubs/EMSE_2026_SHUANG_LI.pdf
   - Purpose: Performance regression analysis methodology
   - Models: Copilot, CodeLlama, DeepSeek-Coder
   - Used for: cProfile + tracemalloc profiling patterns

5. **MARCO - Multi-Agent HPC Code Generation**
   - URL: https://arxiv.org/html/2505.03906v2
   - Purpose: Performance evaluation agent architecture
   - Used for: Multi-metric evaluation framework (runtime, memory, FLOPs)

### Clustering Analysis References

6. **Functional Clustering for LLM Code**
   - URL: https://arxiv.org/html/2506.11021v1
   - Purpose: Behavioral clustering methodology
   - Used for: I/O-based equivalence class concept

7. **sklearn Clustering Documentation**
   - URL: https://scikit-learn.org/stable/modules/clustering.html
   - Purpose: Standard clustering algorithms
   - Used for: KMeans, PCA, StandardScaler implementations

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T17:38:00Z

### Workflow History for This Hypothesis

**2026-03-18T17:38:00Z**: Phase 2C started
- Status: experiment_design.status = IN_PROGRESS
- File: docs/youra_research/20260317_dl4c/h-e1/02c_experiment_brief.md

**Next Actions**:
1. Phase 3: Implementation Planning (PRD + Architecture + Logic + Config generation)
2. Phase 4: Coding + Validation
3. Gate evaluation: Check Cohen's d > 1.5σ

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
