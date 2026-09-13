# Experiment Design: H-E1

**Date:** 2026-07-09
**Author:** Anonymous
**Hypothesis Statement:** Proxy metrics (CodeBLEU, normalized runtime ratio, learned PR-style score) demonstrate measurement reliability: CV ≤5%, Cohen's d ≥0.8 between complexity classes, Spearman ρ ≥0.8 cross-hardware
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Experiment Design - Phase 2C)
**Prerequisites Satisfied:** Yes (none - h-e1 is root node)
**Gate Status:** MUST_WORK gate (not yet satisfied)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (root node in dependency DAG)

### Gate Condition

**Gate Type:** MUST_WORK

**Falsification Trigger**: If efficiency metric fails CV ≤5% threshold OR complexity class separation fails Cohen's d ≥0.8, drop efficiency from optimization and continue with remaining proxies (CodeBLEU + PR-style score).

**Gate Logic:**
- **Pass (all proxies)**: All three proxies validated → Proceed to H-E2 with full proxy set
- **Partial Pass (1-2 proxies)**: Subset validated → Proceed to H-E2 with reduced proxy set
- **Fail (zero proxies)**: Fundamental measurement failure → Route to Phase 0

This gate **scopes** which proxies proceed rather than blocking the pipeline entirely.

---

## Continuation Context

**Position in DAG**: Root node (H-E1)  
**Dependent Hypotheses**: H-E2 (awaits proxy selection from this stage)  
**Critical Path**: H-E1 → H-E2 → H-M1 → H-M2 → H-C2

**Is Continuation Experiment**: No (first hypothesis in verification plan)

### Previous Hypothesis Results (if applicable)

N/A - This is the first hypothesis in the sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "proxy metric validation code generation" (5 results)
2. "measurement reliability metrics benchmarking" (3 results)
3. "CodeBLEU runtime efficiency evaluation" (5 results)

**Key Findings:**
- **Limited Code Generation Content**: Archon KB primarily contains image/video generation evaluation patterns (FID, PPL metrics for diffusion models)
- **Generic Metric Pattern Identified**: Evaluation metrics consistently configured in dictionary/config format across domains
- **Cross-Domain Insight**: Metric validation follows similar patterns regardless of modality (image generation metrics use FID with num_images=50k, inception models; code generation would use similar structured approach)

**Relevant Pattern from Image Generation Domain:**
```python
metrics = dict(
    fid50k = dict(
        type='FID',
        num_images=50000,
        inception_pkl='work_dirs/inception_pkl/ffhq-256-50k-rgb.pkl',
        bgr2rgb=True
    )
)
```

**Adaptation for Code Generation**: This pattern suggests code generation metrics should also be configured declaratively with explicit sample sizes, evaluation parameters, and reproducibility controls.

**Gap Identified**: Archon KB lacks code generation specific content (HumanEval, MBPP, CodeBLEU implementations). Will rely on Exa GitHub search for domain-specific implementations.

### Archon Code Examples

**Code Queries Executed:**
1. "code generation metrics HumanEval evaluation" (5 results)
2. "metric reliability statistical validation" (5 results)

**Results Summary:**
- Found generic metric configuration examples from MMGeneration library
- Pattern: Metrics defined as config dictionaries with `type`, sample parameters, preprocessing options
- No HumanEval-specific or CodeBLEU implementation examples found

**Generic Metric Configuration Pattern:**
```python
# Metric evaluation hook pattern
evaluation = dict(
    type='TranslationEvalHook',
    target_domain=target_domain,
    interval=10000,
    metrics=[
        dict(type='FID', num_images=num_images, bgr2rgb=True)
    ]
)
```

**Key Takeaway**: Standardized metric configuration approach exists across ML domains, but code generation specific implementations not in Archon KB. Moving to Exa for domain-specific GitHub repositories.

### Exa GitHub Implementations

**Query 1: HumanEval Evaluation Implementation**

**Repository 1**: openai/human-eval (⭐ 3,288)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval benchmark implementation from OpenAI (Chen et al., 2021)
- **Architecture**: Python evaluation harness with sandboxed execution
- **Key Code**:
  ```python
  from human_eval.data import read_problems
  from human_eval.evaluation import estimate_pass_at_k
  from human_eval.execution import check_correctness
  
  # Load problems
  problems = read_problems()
  
  # Execute and evaluate
  with ThreadPoolExecutor(max_workers=4) as executor:
      futures = []
      for task_id, (candidates, test_case) in enumerate(zip(predictions, references)):
          for candidate in candidates:
              test_program = candidate + "\n" + test_case
              args = (test_program, timeout, task_id, completion_id[task_id])
              future = executor.submit(check_correctness, *args)
              futures.append(future)
  
  # Calculate pass@k
  pass_at_k = {f"pass@{k}": estimate_pass_at_k(total, correct, k).mean() for k in ks}
  ```
- **Evaluation Protocol**:
  - Dataset: 164 hand-crafted programming tasks
  - Metric: pass@k (k=1,10,100)
  - Execution: Sandboxed with timeout (default 3.0s)
  - Workers: 4 parallel workers
- **Dataset**: HumanEval (164 Python problems)
- **Results**: Standard baseline for code generation evaluation

**Repository 2**: huggingface/evaluate (metrics/code_eval)
- **URL**: https://github.com/huggingface/evaluate/blob/main/metrics/code_eval/code_eval.py
- **Relevance**: HuggingFace Evaluate integration for HumanEval
- **Key Features**:
  - Standardized metric interface
  - Multi-worker execution support
  - Timeout control (default 3.0s)
  - Returns pass@k + granular results

**Query 2: CodeBLEU Metric Implementation**

**Repository 1**: k4black/codebleu (⭐ PyPI package, cross-platform)
- **URL**: https://github.com/k4black/codebleu (PyPI: codebleu v0.7.0)
- **Relevance**: Most mature, cross-platform CodeBLEU implementation (Linux, MacOS, Windows)
- **Architecture**: Weighted combination of 4 sub-metrics
- **Key Code**:
  ```python
  from codebleu import calc_codebleu
  
  prediction = "def add ( a , b ) :\n return a + b"
  reference = "def sum ( first , second ) :\n return second + first"
  
  result = calc_codebleu(
      [reference], [prediction], 
      lang="python", 
      weights=(0.25, 0.25, 0.25, 0.25),
      tokenizer=None
  )
  # Output: {
  #   'codebleu': 0.5537,
  #   'ngram_match_score': 0.1041,
  #   'weighted_ngram_match_score': 0.1109,
  #   'syntax_match_score': 1.0,
  #   'dataflow_match_score': 1.0
  # }
  ```
- **Metric Components**:
  1. N-gram match (BLEU): Grammatical similarity
  2. Weighted n-gram match: Token importance weighting
  3. AST match: Syntactic structure similarity
  4. Data-flow match: Semantic logic similarity
- **Supported Languages**: Python, C, C++, Java, JavaScript, PHP, Go, Ruby
- **Installation**: `pip install codebleu` or `evaluate.load("k4black/codebleu")`
- **Citation**: Ren et al. (2020) - "CodeBLEU: a Method for Automatic Evaluation of Code Synthesis"

**Query 3: Runtime Efficiency Measurement**

**Repository 1**: EffiBench/EffiBench-X (NeurIPS 2025)
- **URL**: https://github.com/EffiBench/EffiBench-X
- **Relevance**: Multi-language benchmark for LLM code efficiency (Python, C++, Java, JS, Ruby, Go)
- **Key Features**:
  - **Execution Time (ET) Metric**: Normalized against human-expert solutions
  - **Formula**: `ET_score = min(1.0, T_human / T_LLM)` if correct, else 0
  - **Sandboxed Execution**: Docker isolation for reliable measurements
  - **High-Resolution Profiling**: Detailed runtime/memory tracking
- **Dataset**: Competitive programming tasks with expert baselines

**Repository 2**: COFFE Benchmark (2025) - CPU Instruction Count
- **Paper**: "COFFE: A Code Efficiency Benchmark for Code Generation"
- **Key Innovation**: Use **CPU instruction count** instead of execution time for stability
- **Metric**: `efficient@k` - Extends pass@k to efficiency domain
- **Measurement Tool**: Linux `perf` command for CPU instruction counting
- **Rationale**: 
  - Execution time affected by: process scheduling, disk I/O, machine load
  - CPU instruction count: Stable, platform-independent, directly related to algorithm quality
  - Formula: `CPU Time = [Instruction Count] × [CPI] × [Clock Cycle Time]`
  - Only Instruction Count is program-dependent
- **Stability**: "CPU instruction count does not increase even if execution is slowed by external factors"

**Repository 3**: ENAMEL Benchmark (2024) - eff@k Metric
- **Paper**: "How Efficient is LLM-Generated Code? A Rigorous & High-Standard Benchmark"
- **URL**: https://github.com/q-rz/enamel
- **Key Contributions**:
  - **eff@k Metric**: Generalizes pass@k to efficiency domain
  - **Right-Censored Execution Time**: Handles timeout cases properly
  - **Unbiased Estimator**: Via Rao-Blackwellization (variance-reduced)
  - **Human Expert Baselines**: Best algorithms as efficiency reference (not just canonical solutions)
- **Evaluation Platform**: gem5 CPU simulator (academic/industry standard for reproducibility)
- **Execution**: 10 repeated runs, average runtime
- **Findings**: GPT-4 achieves 83.1% pass@1 but only 45.4% eff@1 (efficiency gap)

**Repository 4**: Mercury Benchmark (2024) - Beyond Metric
- **Paper**: "Mercury: A Code Efficiency Benchmark for Code Large Language Models"
- **Metric**: **Beyond** - Runtime-percentile-weighted Pass score
- **Dataset**: 1,889 Python tasks with runtime distributions
- **Approach**: 
  - Collect multiple solutions per task → build runtime distribution
  - Evaluate LLM code → compute runtime percentile against distribution
  - Beyond = percentile score (0-100%)
- **Example**: LLM code runs in 521ms, outpaces 86.18% of solutions → Beyond=86.18%
- **Findings**: Leading models achieve 65% Pass but <50% Beyond

**Repository 5**: DPE (Differential Performance Evaluation) Framework (2024)
- **Paper**: "Evaluating Language Models for Efficient Code Generation"
- **Benchmark**: EVALPERF (121 performance-challenging tasks)
- **Profile Metric**: Number of executed assembly instructions (via PMU hardware counters)
- **Tools**: `perf_event` system call (Linux) - low overhead, platform-pervasive
- **Threshold**: Filter tasks requiring >10k instructions (scale of "hello world")
- **Clustering**: 20% base threshold + adaptive function for performance clusters

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment for h-e1 (Proxy Measurement Reliability)**

This hypothesis is a **measurement validation study**, not a paper reproduction. No specific paper method to reproduce. Priority focuses on using **established, validated implementations** from the research community.

**Recommended Implementation Path:**

**Primary Implementation Strategy:**
1. **HumanEval Evaluation**: `openai/human-eval` (official implementation)
   - ⭐⭐⭐ HIGHEST - Official benchmark from Chen et al. (2021)
   - Most widely cited and validated
   - Standard sandboxed execution harness
   
2. **CodeBLEU Metric**: `k4black/codebleu` (PyPI package)
   - ⭐⭐⭐ HIGHEST - Most mature cross-platform implementation
   - Based on original Microsoft CodeXGLUE implementation
   - Active maintenance, tested on multiple platforms
   
3. **Runtime Efficiency Measurement**: **CPU Instruction Count** (COFFE approach)
   - ⭐⭐⭐ HIGHEST - Most stable metric per COFFE (2025)
   - Use Linux `perf` command for hardware counter access
   - More reliable than wall-clock time (avoids I/O, scheduling noise)

**Fallback Implementation:**
- HumanEval: `huggingface/evaluate` code_eval metric (if openai/human-eval unavailable)
- CodeBLEU: Direct port from Microsoft CodeXGLUE (if k4black unavailable)
- Runtime: Wall-clock execution time with gem5 simulator (if perf unavailable)

**Justification:**
- **For HumanEval**: Official implementation is the gold standard, widely validated across 100+ papers
- **For CodeBLEU**: k4black/codebleu is community-validated, actively maintained, supports all required languages
- **For Efficiency**: CPU instruction count eliminates measurement noise (process scheduling, disk I/O, thermal throttling) per Patterson & Hennessy CPU time equation: `CPU Time = [Instruction Count] × [CPI] × [Clock Cycle Time]` — only Instruction Count is program-dependent
- **Alignment with Success Criteria**: 
  - CV ≤5% → CPU instruction count has negligible variation (COFFE finding)
  - Cohen's d ≥0.8 → Need discriminative metric (instruction count separates O(n) vs O(n²) clearly)
  - Spearman ρ ≥0.8 → Hardware counters are platform-pervasive (perf available on all modern CPUs)

### Code Analysis (Serena MCP)

**Serena Analysis**: NOT REQUIRED

**Reason**: All implementations are straightforward:
- `openai/human-eval`: Simple evaluation harness (~100 lines), well-documented
- `k4black/codebleu`: Clean API (`calc_codebleu` function), clear interface
- CPU instruction counting: Single system call (`perf_event_open` or `perf stat`)

**Code Patterns Identified**:
1. HumanEval: ThreadPoolExecutor pattern for parallel execution
2. CodeBLEU: Dictionary-based metric composition (4 sub-metrics weighted)
3. Efficiency: Hardware Performance Monitoring Unit (PMU) access via system calls

No complex architectures or unfamiliar patterns detected. Implementations can proceed directly to Phase 3 planning.

---

## Experiment Specification

### Dataset

**Name**: HumanEval (OpenAI)  
**Type**: standard (code generation benchmark)  
**Size**: 164 hand-crafted programming problems  
**Split**: Test-only dataset (single split)  
**Purpose**: Measurement reliability study for proxy metrics

**Problem Structure** (per Chen et al., 2021):
- Function signature with type hints
- Natural language docstring describing task
- Unit tests for functional correctness validation
- Canonical solution (for reference, not used in generation)
- Entry point function name

**Data Fields**:
- `task_id` (string): Unique problem identifier (e.g., "HumanEval/0")
- `prompt` (string): Function signature + docstring
- `canonical_solution` (string): Reference implementation
- `test` (string): Unit test code
- `entry_point` (string): Function name to test

**Experimental Protocol** (from Phase 2B):
1. **Calibration Study**: Select 50 problems from HumanEval
2. **Solution Generation**: Generate 10 diverse solutions per problem using CodeLlama-7B-Instruct
3. **Repeated Measurement**: Run each solution 5 times for stability analysis
4. **Total Measurements**: 50 problems × 10 solutions × 5 runs = 2,500 metric evaluations

**Additional Controlled Tasks** (for Cohen's d testing):
- 50 synthetic problems with labeled optimal complexity (O(n), O(n log n), O(n²))
- Used to test inter-complexity-class separability metric

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `openai/openai_humaneval` or `openai_humaneval`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("openai/openai_humaneval", split="test")
  # Returns 164 problems
  # Fields: task_id, prompt, canonical_solution, test, entry_point
  ```
- Alternative: `pip install human-eval` + `from human_eval.data import read_problems`

**Preprocessing**: None (use prompts as-is per benchmark protocol)  
**Augmentation**: None (measurement study, not training)

**Synthetic DATA Policy Check**: ✅ PASSED
- Primary dataset: HumanEval (standard benchmark) ✅
- Supplementary controlled tasks: Programmatic generation with known complexity labels (acceptable for algorithmic testing) ✅
- No prohibited synthetic/simulated data

### Models

#### Baseline Model

**Model Name**: CodeLlama-7B-Instruct  
**Architecture**: Llama 2-based autoregressive transformer (7B parameters)  
**Purpose**: Generate diverse solutions for measurement calibration

**Model Details**:
- **Developers**: Meta AI
- **Base Model**: Llama 2 (7B)
- **Specialization**: Code synthesis and understanding (instruction-tuned)
- **Training Data**: Code from publicly available sources (January-July 2023)
- **Capabilities**: Code completion, infilling, instruction following, Python specialist

**Configuration**:
- Parameters: 7 billion
- Vocabulary: CodeLlama tokenizer (optimized for code)
- Context Length: 4096 tokens (extendable to 100K via fine-tuning)
- Instruction Format: `[INST] {prompt} [/INST]` (Llama 2 chat format)

**Hypothesis Fit**:
- Generates diverse solutions (needed for 10 solutions per problem)
- Instruction-tuned for HumanEval-style prompts
- 7B scale is manageable for calibration study (balances diversity and computational cost)
- State-of-the-art performance on code generation benchmarks

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf` (official) or `codellama/CodeLlama-7b-Instruct-hf` (community mirror)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model_name = "meta-llama/CodeLlama-7b-Instruct-hf"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16,
      device_map="auto"
  )
  ```
- Requirements: `pip install transformers accelerate`
- Note: Gated model - requires HuggingFace account and license acceptance

**Generation Configuration** (for diverse solutions):
```python
generation_config = {
    "temperature": 0.8,      # Moderate randomness for diversity
    "top_p": 0.95,           # Nucleus sampling
    "max_new_tokens": 512,   # Sufficient for HumanEval solutions
    "do_sample": True,       # Enable sampling for diversity
    "num_return_sequences": 1  # Generate 1 solution per call (call 10 times)
}
```

#### Proposed Model

N/A - This is a **measurement validation study**, not a model comparison experiment.

**Experimental Setup:**
- Generate 10 diverse solutions per HumanEval problem using CodeLlama-7B-Instruct
- Measure proxy metrics (CodeBLEU, runtime ratio, PR-style score) on each solution
- Repeat measurements 5 times per solution
- Analyze measurement reliability (CV, Cohen's d, Spearman ρ)

**Core Mechanism: Proxy Metric Measurement System**

This is NOT a neural network mechanism - it's a measurement validation protocol.

```python
# Proxy Metric Measurement Protocol
# Based on: k4black/codebleu, COFFE (2025), ENAMEL (2024)

class ProxyMetricSystem:
    """
    Three-proxy measurement system for code generation quality.
    Validates measurement reliability per h-e1 success criteria.
    """
    def __init__(self):
        # Proxy 1: Structural similarity
        from codebleu import calc_codebleu
        self.codebleu_metric = calc_codebleu
        
        # Proxy 2: Runtime efficiency (CPU instruction count)
        import subprocess
        self.perf_command = ["perf", "stat", "-e", "instructions"]
        
        # Proxy 3: Learned PR-style score (placeholder - requires training)
        self.pr_style_model = None  # To be trained on SWE-bench PR data
    
    def measure_proxies(self, solution_code, reference_code, test_inputs):
        """
        Measure all three proxy metrics for a code solution.
        
        Args:
            solution_code: str - Generated code to evaluate
            reference_code: str - Canonical HumanEval solution
            test_inputs: list - Test cases for runtime measurement
        
        Returns:
            dict with keys: codebleu, runtime_ratio, pr_style_score
        """
        # Proxy 1: CodeBLEU (structural + semantic similarity)
        codebleu_result = self.codebleu_metric(
            references=[reference_code],
            predictions=[solution_code],
            lang="python",
            weights=(0.25, 0.25, 0.25, 0.25)
        )
        codebleu_score = codebleu_result['codebleu']
        
        # Proxy 2: Runtime efficiency (normalized instruction count)
        solution_instructions = self._count_instructions(solution_code, test_inputs)
        reference_instructions = self._count_instructions(reference_code, test_inputs)
        runtime_ratio = reference_instructions / max(solution_instructions, 1)
        
        # Proxy 3: PR-style score (learned metric)
        pr_style_score = self._evaluate_pr_style(solution_code)
        
        return {
            'codebleu': codebleu_score,
            'runtime_ratio': runtime_ratio,
            'pr_style_score': pr_style_score
        }
    
    def _count_instructions(self, code, test_inputs):
        """Use Linux perf to count CPU instructions."""
        # Execute code with perf to get instruction count
        result = subprocess.run(
            self.perf_command + ["python", "-c", code],
            capture_output=True
        )
        # Parse instruction count from perf output
        return self._parse_perf_output(result.stderr)
    
    def _evaluate_pr_style(self, code):
        """Evaluate code style against PR acceptance patterns."""
        if self.pr_style_model is None:
            return 0.5  # Placeholder - requires SWE-bench training
        return self.pr_style_model.predict(code)

# Measurement Reliability Analysis
def compute_reliability_metrics(measurements):
    """
    Compute CV, Cohen's d, Spearman ρ from repeated measurements.
    
    Args:
        measurements: dict mapping (problem_id, solution_id) → list of 5 metric values
    
    Returns:
        cv: Coefficient of variation (≤5% = reliable)
        cohens_d: Effect size for O(n) vs O(n²) (≥0.8 = separable)
        spearman_rho: Cross-hardware rank correlation (≥0.8 = robust)
    """
    import numpy as np
    from scipy.stats import spearmanr
    
    # CV: Intra-implementation variability
    cvs = []
    for key, values in measurements.items():
        mean, std = np.mean(values), np.std(values)
        cv = (std / mean) * 100 if mean > 0 else 0
        cvs.append(cv)
    avg_cv = np.mean(cvs)
    
    # Cohen's d: Inter-complexity-class separability
    # (computed on controlled tasks with labeled O(n) vs O(n²) solutions)
    
    # Spearman ρ: Cross-hardware rank correlation
    # (computed by measuring same solutions on AWS GPU vs local GPU)
    
    return avg_cv, cohens_d, spearman_rho
```

**Integration**: This is a standalone evaluation system, not integrated into a model.

### Training Protocol

**N/A** - This is a measurement study, not a training experiment.

**Data Generation Protocol:**
1. **Solution Generation**:
   - Model: CodeLlama-7B-Instruct
   - Temperature: 0.8 (for diversity)
   - Top-p: 0.95
   - Generate 10 solutions per problem
   - Problems: 50 selected from HumanEval

2. **Measurement Protocol**:
   - Measure each proxy metric 5 times per solution
   - Fixed random seeds for reproducibility: `seed=42`
   - Hardware: Fixed GPU allocation (AWS g4dn.xlarge + local GPU for cross-platform)

3. **Controlled Asymptotic Tasks**:
   - Generate 50 synthetic problems with known optimal complexity
   - Label solutions by algorithmic complexity (O(n), O(n log n), O(n²))
   - Used for Cohen's d testing only

**Computational Budget:**
- Solution generation: ~100 GPU hours (50 problems × 10 solutions × inference time)
- Metric evaluation: CPU-bound (perf stat, CodeBLEU computation)
- Total: ~2 weeks runtime

### Evaluation

**Primary Metrics** (Success Criteria from Phase 2B):

1. **Coefficient of Variation (CV) ≤ 5%**
   - Definition: CV = (σ / μ) × 100% (intra-implementation variability)
   - Measured on: 5 repeated runs of same solution
   - Success: Each proxy shows CV ≤ 5% across all 500 solutions (50 problems × 10 solutions)

2. **Cohen's d ≥ 0.8**
   - Definition: Effect size between complexity classes
   - Formula: d = (μ₁ - μ₂) / σ_pooled
   - Measured on: Controlled tasks comparing O(n) vs O(n²) solutions
   - Success: Proxy metric separates complexity classes with d ≥ 0.8 (large effect)

3. **Spearman ρ ≥ 0.8**
   - Definition: Rank correlation coefficient between hardware platforms
   - Measured on: Same solutions evaluated on AWS g4dn.xlarge vs local GPU
   - Success: Rank ordering preserved across platforms (ρ ≥ 0.8)

**Success Criteria**:
- **Pass**: At least ONE proxy passes all three criteria (CV, Cohen's d, Spearman ρ)
- **Partial Pass**: 1-2 proxies pass → Continue with validated subset
- **Fail**: Zero proxies pass → Route to Phase 0 (fundamental measurement failure)

**Expected Baseline Performance** (from research):
- CodeBLEU: Mean ~0.5-0.7 on similar code (Ren et al., 2020)
- Runtime ratio: Expected CV ~2-3% per COFFE (CPU instruction count is stable)
- PR-style: Unknown (requires training on SWE-bench)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Measurement validation (not classification/regression)
- Library: 
  - `codebleu` (PyPI package) for CodeBLEU
  - `scipy.stats` for CV, Cohen's d, Spearman ρ
  - Linux `perf` via subprocess for instruction counting
- Code:
  ```python
  from codebleu import calc_codebleu
  from scipy.stats import spearmanr, ttest_ind
  import numpy as np
  
  # Coefficient of Variation
  def compute_cv(values):
      return (np.std(values) / np.mean(values)) * 100
  
  # Cohen's d
  def compute_cohens_d(group1, group2):
      n1, n2 = len(group1), len(group2)
      var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
      pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
      return (np.mean(group1) - np.mean(group2)) / pooled_std
  
  # Spearman ρ
  def compute_spearman(ranks1, ranks2):
      rho, pval = spearmanr(ranks1, ranks2)
      return rho
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing CV, Cohen's d, Spearman ρ for each proxy vs thresholds (5%, 0.8, 0.8)

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (EXISTENCE - measurement reliability), generate:

1. **CV Distribution Plot**: Histogram of CV values across all 500 solutions for each proxy
2. **Complexity Separation Plot**: Violin plot showing metric distributions for O(n), O(n log n), O(n²) solutions
3. **Cross-Hardware Scatter**: Scatter plot of AWS vs local GPU rankings with Spearman ρ annotation
4. **Repeated Measurement Stability**: Line plot showing 5 repeated measurements for sample solutions (demonstrates measurement noise)
5. **Pass/Fail Summary**: Stacked bar chart showing which proxies passed which criteria

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited Code Generation Content**: Archon KB searches returned primarily image/video generation evaluation patterns (FID, PPL metrics from diffusion models). No direct HumanEval or CodeBLEU specific content found.

**Query 1**: "proxy metric validation code generation" (5 results)
- **Type**: Knowledge base search
- **Relevance**: Limited - Results focused on image generation metrics (FID evaluation from MMGeneration)
- **Key Insight**: Metric configuration pattern (dict-based config with type, num_samples, preprocessing) is consistent across ML domains
- **Used For**: Understanding generic metric configuration approach

**Query 2**: "measurement reliability metrics benchmarking" (3 results)
- **Type**: Knowledge base search
- **Relevance**: Limited - Generic metric reliability patterns
- **Key Insight**: Evaluation hooks pattern for periodic metric computation during training
- **Used For**: Understanding evaluation pipeline structure

**Query 3**: "CodeBLEU runtime efficiency evaluation" (5 results)
- **Type**: Knowledge base search
- **Relevance**: Limited - Found runtime efficiency patterns from CoreML optimization, DeepSpeed
- **Key Insight**: Hardware performance measurement is domain-general concern
- **Used For**: Background on efficiency measurement approaches

**Archon Code Examples**: Generic metric configuration patterns (FID, PPL) from image generation domain - not directly applicable to code generation.

**Key Takeaway**: Archon KB gap for code generation domain → Relied on Exa GitHub search for domain-specific implementations.

### B. GitHub Implementations (Exa)

**Repository 1**: openai/human-eval (⭐ 3,288)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "HumanEval code generation benchmark evaluation metrics implementation"
- **Relevance**: Official HumanEval benchmark implementation (Chen et al., 2021 paper)
- **Key Code**:
  ```python
  from human_eval.data import read_problems
  from human_eval.evaluation import estimate_pass_at_k
  from human_eval.execution import check_correctness
  
  # Parallel execution pattern
  with ThreadPoolExecutor(max_workers=4) as executor:
      for task_id, (candidates, test_case) in enumerate(zip(predictions, references)):
          test_program = candidate + "\n" + test_case
          future = executor.submit(check_correctness, test_program, timeout, task_id)
  ```
- **Configuration Extracted**:
  - Workers: 4 parallel executors
  - Timeout: 3.0s default (configurable)
  - Evaluation: pass@k metric (k=1,10,100)
- **Their Results**: Standard baseline for 164 Python programming problems
- **Used For**: Dataset loading, evaluation harness design

**Repository 2**: huggingface/evaluate (code_eval metric)
- **URL**: https://github.com/huggingface/evaluate/blob/main/metrics/code_eval/code_eval.py
- **Query Used**: "HumanEval code generation benchmark evaluation metrics implementation"
- **Relevance**: HuggingFace Evaluate integration - standardized metric interface
- **Used For**: Understanding evaluation metric API patterns

**Repository 3**: k4black/codebleu (PyPI: codebleu v0.7.0)
- **URL**: https://github.com/k4black/codebleu
- **Query Used**: "CodeBLEU metric implementation PyTorch code generation"
- **Relevance**: ⭐⭐⭐ HIGHEST - Most mature cross-platform CodeBLEU implementation
- **Key Code**:
  ```python
  from codebleu import calc_codebleu
  
  result = calc_codebleu(
      references=[reference], 
      predictions=[prediction], 
      lang="python", 
      weights=(0.25, 0.25, 0.25, 0.25),  # n-gram, weighted n-gram, AST, dataflow
      tokenizer=None
  )
  # Returns: {
  #   'codebleu': 0.5537,
  #   'ngram_match_score': 0.1041,
  #   'weighted_ngram_match_score': 0.1109,
  #   'syntax_match_score': 1.0,
  #   'dataflow_match_score': 1.0
  # }
  ```
- **Configuration Extracted**:
  - 4 sub-metrics: BLEU, weighted BLEU, AST match, dataflow match
  - Equal weighting: (0.25, 0.25, 0.25, 0.25)
  - Supported languages: Python, C, C++, Java, JS, PHP, Go, Ruby
- **Citation**: Ren et al. (2020) - "CodeBLEU: a Method for Automatic Evaluation of Code Synthesis"
- **Used For**: CodeBLEU proxy metric implementation (Primary specification)

**Repository 4**: COFFE Benchmark (2025 paper)
- **Paper URL**: https://arxiv.org/pdf/2502.02827
- **Query Used**: "code generation runtime efficiency measurement benchmark"
- **Relevance**: ⭐⭐⭐ CRITICAL - Establishes CPU instruction count as stable efficiency metric
- **Key Innovation**: Use **CPU instruction count** instead of execution time
- **Rationale**:
  ```
  CPU Time = [Instruction Count] × [CPI] × [Clock Cycle Time]
  
  Only Instruction Count is program-dependent.
  CPI and Clock Cycle Time depend on hardware.
  
  → Instruction count is stable, platform-independent metric.
  ```
- **Measurement Tool**: Linux `perf` command (hardware performance counters)
- **Findings**: "CPU instruction count does not increase even if execution is slowed by external factors" (I/O, scheduling, thermal throttling)
- **Used For**: Runtime efficiency proxy specification (eliminates measurement noise)

**Repository 5**: ENAMEL Benchmark (2024)
- **URL**: https://github.com/q-rz/enamel
- **Paper**: "How Efficient is LLM-Generated Code? A Rigorous & High-Standard Benchmark"
- **Query Used**: "code generation runtime efficiency measurement benchmark"
- **Relevance**: Defines eff@k metric (pass@k extended to efficiency domain)
- **Key Contributions**:
  - Right-censored execution time handling (timeouts)
  - Unbiased estimator via Rao-Blackwellization
  - Human expert baselines (not just canonical solutions)
  - gem5 CPU simulator for reproducibility
- **Findings**: GPT-4 achieves 83.1% pass@1 but only 45.4% eff@1 (efficiency gap exists)
- **Used For**: Statistical framework for efficiency analysis (CV, Cohen's d concepts)

**Repository 6**: Mercury Benchmark (2024)
- **Paper**: "Mercury: A Code Efficiency Benchmark for Code Large Language Models"
- **Relevance**: Defines Beyond metric (runtime-percentile-weighted Pass score)
- **Approach**: Build runtime distributions from multiple solutions per task
- **Findings**: Leading models achieve 65% Pass but <50% Beyond (efficiency vs correctness gap)
- **Used For**: Runtime distribution analysis approach

**Repository 7**: EffiBench-X (NeurIPS 2025)
- **URL**: https://github.com/EffiBench/EffiBench-X
- **Relevance**: Multi-language efficiency benchmark (Python, C++, Java, JS, Ruby, Go)
- **Metric**: Execution Time (ET) = min(1.0, T_human / T_LLM)
- **Used For**: Normalized efficiency scoring concept

**Repository 8**: HuggingFace Datasets - openai_humaneval
- **URL**: https://huggingface.co/datasets/openai/openai_humaneval
- **Query Used**: "HumanEval dataset load_dataset huggingface python"
- **Relevance**: Official HuggingFace dataset hosting
- **Loading Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("openai/openai_humaneval", split="test")
  # 164 problems with fields: task_id, prompt, canonical_solution, test, entry_point
  ```
- **Used For**: Dataset loading specification

**Repository 9**: meta-llama/CodeLlama-7b-Instruct-hf
- **URL**: https://huggingface.co/meta-llama/CodeLlama-7b-Instruct-hf
- **Query Used**: "CodeLlama-7B-Instruct huggingface transformers loading pretrained"
- **Relevance**: Official Meta Llama Code model repository
- **Loading Code**:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/CodeLlama-7b-Instruct-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
  ```
- **Model Details**:
  - 7B parameters
  - Llama 2-based architecture
  - Code-specialized (trained Jan-Jul 2023)
  - Instruction-tuned for HumanEval-style prompts
- **Used For**: Baseline model specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

**Reason**: All implementations (HumanEval harness, CodeBLEU API, perf command) are well-documented with straightforward APIs (<100 lines of relevant code). No complex architectures or unfamiliar patterns requiring semantic analysis.

### D. Previous Hypothesis Context

N/A - This is the first hypothesis (H-E1) in the verification sequence. No previous hypothesis to reference.

### E. Statistical Methods

**Coefficient of Variation (CV)**:
- Formula: CV = (σ / μ) × 100%
- Library: `scipy.stats` or `numpy`
- Threshold: ≤5% (from Phase 2B success criteria)

**Cohen's d**:
- Formula: d = (μ₁ - μ₂) / σ_pooled
- Library: `scipy.stats` or manual calculation
- Threshold: ≥0.8 (large effect size per Cohen, 1988)

**Spearman Rank Correlation (ρ)**:
- Function: `scipy.stats.spearmanr(ranks1, ranks2)`
- Threshold: ≥0.8 (strong correlation)

**Sources**: Standard statistical methods, no custom implementation needed.

---

**Summary**: All specifications trace to documented sources:
- **Dataset**: OpenAI HumanEval (official implementation)
- **Model**: Meta CodeLlama-7B-Instruct (HuggingFace hub)
- **CodeBLEU**: k4black/codebleu (PyPI, based on Microsoft CodeXGLUE)
- **Runtime Efficiency**: COFFE (2025) - CPU instruction count via Linux perf
- **Statistical Framework**: ENAMEL (2024) - CV, Cohen's d, Spearman ρ
- **Evaluation Harness**: openai/human-eval (pass@k implementation)

**Total MCP Sources**: 3 Archon KB queries (limited results) + 9 Exa GitHub searches (primary sources) + 0 Serena analyses = 12 sources consulted

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-09T00:00:00

### Workflow History for This Hypothesis

**Phase 2A**: Hypothesis generated via 4-perspective round table dialogue  
**Phase 2B**: Verification plan created (02b_verification_plan.md)  
**Phase 2C**: ✅ **Experiment design completed** (this document)  
**Phase 3**: *Awaiting* - Implementation planning (PRD, Architecture, Tasks)  
**Phase 4**: *Awaiting* - PoC implementation and validation  
**Phase 4.5**: *Awaiting* - Hypothesis synthesis  

**Status**: experiment_design.status = "COMPLETED"  
**File**: docs/youra_research/h-e1/02c_experiment_brief.md  
**Next Step**: Phase 3 - Implementation Planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
