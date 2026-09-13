# Experiment Design: h-e1

**Date:** 2026-04-15
**Author:** Anonymous
**Hypothesis Statement:** Under execution-based code benchmarks with 20+ model evaluations, if we extract standardized execution trace features (pass@k, runtime quartiles, error distributions), then these features will exist for all models across HumanEval, MBPP, and APPS benchmarks, because all three benchmarks provide programmatic test suites that produce execution outcomes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (Foundation hypothesis - no prerequisites)
**Gate Status:** MUST_WORK - Feature extraction must succeed for ≥95% of model-benchmark combinations

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition

**Gate Type:** MUST_WORK

**Pass Condition:** ≥95% of model-benchmark combinations have complete execution trace features (pass@k, runtime quartiles, error distributions)

**Fail Action:** Cannot proceed to dimensional analysis without data infrastructure - ABORT entire verification workflow

---

## Continuation Context

This is the **foundation hypothesis** - no previous hypothesis context.

All subsequent hypotheses (h-m1, h-m2, h-m3, h-m4) depend on h-e1 providing complete execution trace data infrastructure.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**⚠️ MCP Limitation:** Archon MCP not available. Using Phase 2B context and domain knowledge.

**From Phase 2B Analysis:**
- HumanEval, MBPP, and APPS are well-established execution-based benchmarks with documented evaluation protocols
- Pass@k metrics (k=1,10,100) are standard in code generation literature
- Runtime and error analysis require execution environment setup
- Benchmark papers provide reference implementations and evaluation scripts

**Key Insights:**
- HumanEval: 164 hand-crafted programming problems (algorithmic focus)
- MBPP: ~1,000 crowd-sourced Python problems (practical patterns)
- APPS: 10,000 competitive programming problems (difficulty range: introductory to competition)

### Archon Code Examples

**⚠️ MCP Limitation:** Archon code search not available.

**Standard Implementation Pattern (from benchmark documentation):**
- Use official benchmark repositories for evaluation
- Standard execution: timeout limits, sandbox environments
- Feature extraction: programmatic test execution + result parsing

### Exa GitHub Implementations

**⚠️ MCP Limitation:** Exa MCP not available.

**Known Reference Implementations:**
1. **HumanEval Official**: https://github.com/openai/human-eval
   - Provides evaluation harness and pass@k calculation
   - Standard for code generation benchmarks

2. **MBPP Official**: https://github.com/google-research/google-research/tree/master/mbpp
   - Includes test cases and evaluation protocol

3. **APPS Official**: https://github.com/hendrycks/apps
   - Comprehensive evaluation framework
   - Difficulty-stratified problems

### 🎯 Implementation Priority Assessment

**CRITICAL: For benchmark evaluation experiments, use official benchmark implementations**

**Implementation Context:**
This is a data extraction experiment, NOT a paper reproduction. We need to:
1. Collect published model evaluation results (pass@k scores)
2. Execute models on benchmarks to gather runtime/error data
3. Standardize features across benchmarks

**Recommended Implementation Path:**
- **Primary**: Official benchmark repositories (HumanEval, MBPP, APPS evaluation scripts)
- **Fallback**: Manual collection from published papers + selective re-execution
- **Justification**: Official implementations ensure consistency with published results. For EXISTENCE hypothesis, proving data infrastructure exists is sufficient - full re-evaluation of 20+ models is optional if published results are available.

### Code Analysis (Serena MCP)

**⚠️ MCP Limitation:** Serena MCP not available - code structure is clear from benchmark documentation.

---

## Experiment Specification

### Dataset

**Datasets (Multi-Benchmark):**

This experiment requires evaluation across **3 execution-based benchmarks**:

#### Dataset 1: HumanEval
- **Name:** HumanEval
- **Type:** standard
- **Source:** https://github.com/openai/human-eval
- **Size:** 164 hand-crafted programming problems
- **Test Coverage:** Unit tests per problem (avg 7.7 tests/problem)
- **Focus:** Algorithmic clarity and correctness

**Loading Information** (for Phase 4 download):
- Method: Git clone + datasets library
- Identifier: `openai_humaneval`
- Code: 
  ```python
  from datasets import load_dataset
  humaneval = load_dataset("openai_humaneval")
  # Alternative: git clone https://github.com/openai/human-eval
  ```

#### Dataset 2: MBPP (Mostly Basic Python Problems)
- **Name:** MBPP
- **Type:** standard
- **Source:** https://github.com/google-research/google-research/tree/master/mbpp
- **Size:** ~1,000 crowd-sourced Python problems
- **Test Coverage:** 3 test cases per problem (visible during evaluation)
- **Focus:** Practical programming patterns

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `mbpp`
- Code:
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("mbpp")
  ```

#### Dataset 3: APPS (Automated Programming Progress Standard)
- **Name:** APPS
- **Type:** standard
- **Source:** https://github.com/hendrycks/apps
- **Size:** 10,000 competitive programming problems
- **Difficulty:** Introductory (2,000), Interview (5,000), Competition (3,000)
- **Test Coverage:** Multiple hidden test cases per problem
- **Focus:** Competitive programming competency

**Loading Information** (for Phase 4 download):
- Method: Git clone
- Identifier: `hendrycks/apps`
- Code:
  ```python
  # git clone https://github.com/hendrycks/apps
  from datasets import load_dataset
  apps = load_dataset("codeparrot/apps")
  ```

**Feature Extraction Target:**
For each model-benchmark combination, extract:
- `pass@1`, `pass@10`, `pass@100` (standard code generation metrics)
- Runtime quartiles (25th, 50th, 75th percentile) for passing solutions
- Error distributions (syntax errors, runtime errors, timeout)

### Models

#### Model Population (20+ Code Generation Models)

**⚠️ EXISTENCE Hypothesis Note:** This hypothesis does NOT train models. It collects/analyzes existing evaluation data.

**Target Model List (Diverse Population):**

| Model Family | Examples | Availability |
|--------------|----------|--------------|
| GPT Series | GPT-3.5, GPT-4 | Published results available |
| CodeLlama | CodeLlama-7B, 13B, 34B, 70B | Open-source |
| StarCoder | StarCoder-15B, StarCoder2 | Open-source |
| DeepSeek Coder | DeepSeek-Coder-6.7B, 33B | Open-source |
| WizardCoder | WizardCoder-15B, 34B | Open-source |
| Phind CodeLlama | Phind-CodeLlama-34B-v2 | Open-source |
| Mistral | Codestral | Open-source |
| Claude | Claude-2, Claude-3 | Published results available |

**Data Collection Strategy:**
1. **Primary:** Collect published benchmark results from papers (many models already evaluated on HumanEval/MBPP/APPS)
2. **Secondary:** Re-execute selected models to gather runtime/error data if needed
3. **Target:** ≥20 models with complete feature coverage across all 3 benchmarks

**Loading Information** (for Phase 4 implementation):
- Method: HuggingFace Transformers + published results collection
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  # Example for CodeLlama
  model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf")
  tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
  
  # For published results: manual collection from papers
  # See: HumanEval leaderboard, BigCode evaluation harness
  ```

#### Baseline Model

**N/A for EXISTENCE hypothesis** - This is a data infrastructure experiment, not a model training experiment.

The "baseline" is the **existence of published evaluation data**. Success = proving we can extract complete execution trace features.

#### Proposed Model

**N/A for EXISTENCE hypothesis** - No model architecture modification needed.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Execution Trace Feature Extraction
# Purpose: Extract standardized features from benchmark evaluations

class ExecutionTraceExtractor:
    """
    Extract execution trace features from code generation model evaluations.
    
    Features:
    - pass@k (k=1,10,100): Probability of generating correct solution in k attempts
    - runtime_quartiles: 25th, 50th, 75th percentile runtime for passing solutions
    - error_distributions: Categorized error modes (syntax, logic, resource)
    """
    
    def __init__(self, benchmark_name, test_cases):
        self.benchmark = benchmark_name
        self.test_cases = test_cases
        self.features = {}
    
    def extract_passk(self, model_outputs, k_values=[1, 10, 100]):
        """
        Calculate pass@k metric.
        
        Args:
            model_outputs: List of n generated solutions per problem
            k_values: Values of k to compute
        Returns:
            dict: {k: pass@k_score}
        """
        passk_scores = {}
        for k in k_values:
            # Standard pass@k formula from Chen et al. 2021
            passk_scores[f'pass@{k}'] = self.compute_passk(model_outputs, k)
        return passk_scores
    
    def extract_runtime_quartiles(self, passing_solutions):
        """
        Compute runtime distribution for passing solutions.
        
        Args:
            passing_solutions: List of (solution, runtime_ms)
        Returns:
            dict: {q25, q50, q75}
        """
        runtimes = [runtime for _, runtime in passing_solutions]
        return {
            'runtime_q25': np.percentile(runtimes, 25),
            'runtime_q50': np.percentile(runtimes, 50),
            'runtime_q75': np.percentile(runtimes, 75)
        }
    
    def categorize_errors(self, failed_solutions):
        """
        Categorize error modes.
        
        Args:
            failed_solutions: List of (solution, error_type, error_msg)
        Returns:
            dict: Error distribution
        """
        error_counts = {'syntax': 0, 'runtime': 0, 'timeout': 0}
        for _, error_type, _ in failed_solutions:
            if error_type in error_counts:
                error_counts[error_type] += 1
        
        total = len(failed_solutions)
        return {k: v/total for k, v in error_counts.items()}
    
    def extract_all_features(self, model_name, evaluation_results):
        """
        Extract complete feature set for one model-benchmark pair.
        
        Returns:
            dict: Complete feature vector
        """
        features = {
            'model': model_name,
            'benchmark': self.benchmark,
            **self.extract_passk(evaluation_results),
            **self.extract_runtime_quartiles(evaluation_results['passing']),
            **self.categorize_errors(evaluation_results['failing'])
        }
        return features

# Integration: Standalone data extraction pipeline
# No model architecture modification needed
```

### Training Protocol

**N/A for EXISTENCE hypothesis** - This is a data extraction experiment, not a training experiment.

**Data Collection Protocol:**

1. **Phase 1: Published Results Collection (1 week)**
   - Collect pass@k scores from published papers for 20+ models
   - Sources: ArXiv papers, HumanEval leaderboard, BigCode benchmarks
   - Organize in standardized CSV format

2. **Phase 2: Runtime Data Collection (1 week)**
   - For models with available code, execute on benchmark test cases
   - Measure runtime per solution (requires controlled environment)
   - Extract passing/failing solution distributions

3. **Phase 3: Error Categorization (3-5 days)**
   - Parse execution errors from failed solutions
   - Categorize into: syntax errors, runtime errors, timeout
   - Compute error distributions per model-benchmark pair

4. **Phase 4: Feature Completeness Check (1 day)**
   - Verify ≥95% of model-benchmark combinations have complete features
   - Document missing data with reasons
   - Validate feature standardization across benchmarks

**Computational Requirements:**
- No GPU needed (data extraction only)
- Execution sandbox for runtime measurement (Docker recommended)
- Storage: ~10GB for benchmark datasets + model outputs

### Evaluation

**Primary Metric: Feature Completeness Rate**

```python
feature_completeness = (complete_model_benchmark_pairs / total_model_benchmark_pairs) * 100
```

**Success Criteria:**
- **Primary:** ≥95% feature completeness across all model-benchmark combinations
- **Secondary:** Features are standardized and comparable across benchmarks

**Expected Baseline Performance:**
Based on literature, published pass@k results available for ~15-20 models on HumanEval/MBPP. APPS has fewer published results but covers 10+ major models.

**Expected Result:**
- HumanEval: ~100% coverage (most widely benchmarked)
- MBPP: ~90% coverage (less common but growing)
- APPS: ~70-80% coverage (newer benchmark)
- **Overall:** ~85-90% completeness achievable with published results + selective re-execution

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Data extraction and validation
- Library: pandas, numpy for feature computation
- Code:
  ```python
  import pandas as pd
  import numpy as np
  
  # Feature completeness calculation
  def calculate_feature_completeness(feature_df):
      total_combinations = len(feature_df)
      complete_combinations = feature_df.dropna().shape[0]
      return (complete_combinations / total_combinations) * 100
  
  # Validation: check feature standardization
  required_features = ['pass@1', 'pass@10', 'pass@100', 
                       'runtime_q25', 'runtime_q50', 'runtime_q75',
                       'error_syntax', 'error_runtime', 'error_timeout']
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Feature completeness rate (target: 95%, actual: measured)
  - Bar chart showing completeness % for each benchmark (HumanEval, MBPP, APPS)
  - Overall completeness across all model-benchmark combinations

#### Additional Figures (LLM Autonomous)

Based on the data extraction nature of this experiment, the following visualizations will effectively communicate results:

1. **Feature Coverage Heatmap**
   - Rows: Models (20+)
   - Columns: Benchmarks (HumanEval, MBPP, APPS)
   - Color: Feature completeness (0-100%)
   - Purpose: Identify data gaps

2. **Feature Distribution Histograms**
   - Pass@1, pass@10, pass@100 distributions across models
   - Runtime quartile distributions
   - Error type distributions
   - Purpose: Validate feature extraction quality

3. **Model-Benchmark Coverage Matrix**
   - Binary heatmap showing which model-benchmark pairs have complete data
   - Annotate with missing feature counts
   - Purpose: Quality control visualization

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**EXISTENCE Hypothesis - PoC Pass Condition:**

1. **Code runs without error** - Data extraction pipeline executes successfully
2. **Feature completeness ≥ 95%** - At least 95% of model-benchmark combinations have complete execution trace features

**Specific Validation:**
```python
# Success check
feature_completeness_rate >= 95.0  # Primary success criterion

# Quality checks (should all pass)
assert all_benchmarks_have_data(['HumanEval', 'MBPP', 'APPS'])
assert feature_standardization_valid()
assert no_systematic_missing_data_patterns()
```

**Gate Satisfaction:**
- **MUST_WORK gate PASSES** if feature_completeness ≥ 95%
- **MUST_WORK gate FAILS** if feature_completeness < 95% → BLOCKS all dependent hypotheses (h-m1, h-m2, h-m3, h-m4)

---

## Appendix: Reference Implementations

### A. Benchmark Documentation Sources

**Source 1: HumanEval Official Repository**
- **Type:** Official benchmark implementation
- **URL:** https://github.com/openai/human-eval
- **Reference Paper:** Chen et al. (2021) "Evaluating Large Language Models Trained on Code"
- **Key Insights:**
  - Standard pass@k calculation methodology
  - 164 hand-written programming problems
  - Unit test-based evaluation
- **Used For:** Dataset specification, pass@k metric definition, evaluation protocol

**Source 2: MBPP Official Repository**
- **Type:** Official benchmark implementation
- **URL:** https://github.com/google-research/google-research/tree/master/mbpp
- **Reference Paper:** Austin et al. (2021) "Program Synthesis with Large Language Models"
- **Key Insights:**
  - ~1,000 crowd-sourced Python problems
  - 3 test cases per problem (visible during eval)
  - Focus on basic programming patterns
- **Used For:** Dataset specification, evaluation methodology

**Source 3: APPS Official Repository**
- **Type:** Official benchmark implementation
- **URL:** https://github.com/hendrycks/apps
- **Reference Paper:** Hendrycks et al. (2021) "Measuring Coding Challenge Competence With APPS"
- **Key Insights:**
  - 10,000 competitive programming problems
  - Difficulty-stratified (Introductory, Interview, Competition)
  - Hidden test cases for robust evaluation
- **Used For:** Dataset specification, difficulty-aware analysis

### B. Feature Extraction Methodology

**Source 4: Pass@k Calculation**
- **Type:** Standard metric definition
- **Reference:** Chen et al. (2021), Appendix A
- **Formula:** 
  ```
  pass@k = E[1 - (n-c choose k) / (n choose k)]
  where n = total samples, c = correct samples
  ```
- **Used For:** Primary evaluation metric implementation

**Source 5: Runtime Measurement Best Practices**
- **Type:** Domain knowledge (benchmark execution standards)
- **Key Practices:**
  - Timeout limits (typically 10-30 seconds per test case)
  - Sandboxed execution environment (Docker/isolated Python env)
  - Median runtime for stability (less sensitive to outliers)
- **Used For:** Runtime quartile feature extraction protocol

**Source 6: Error Categorization**
- **Type:** Standard software testing taxonomy
- **Categories:**
  - Syntax errors: Code doesn't parse
  - Runtime errors: Execution failures (exceptions, assertion errors)
  - Timeout: Execution exceeds time limit
- **Used For:** Error distribution feature extraction

### C. Model Evaluation Data Sources

**Source 7: Published Benchmark Results**
- **Type:** Aggregated leaderboard data
- **Sources:**
  - HumanEval Leaderboard (Papers with Code)
  - BigCode Evaluation Harness results
  - Individual model papers (CodeLlama, StarCoder, etc.)
- **Used For:** Primary data source for pass@k scores across models

**Source 8: Open-Source Model Repositories**
- **Type:** Model weights and evaluation code
- **Source:** HuggingFace Model Hub
- **Models:** CodeLlama, StarCoder, DeepSeek-Coder, WizardCoder, etc.
- **Used For:** Secondary data collection (re-execution if needed)

### D. Phase 2B Context

**Source 9: Verification Plan - H-E1 Specification**
- **File:** `02b_verification_plan.md` (Section 2.2.1)
- **Used For:**
  - Hypothesis statement and rationale
  - Success criteria (≥95% feature completeness)
  - Gate conditions (MUST_WORK)
  - Verification protocol (5-step data extraction process)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval, MBPP, APPS) | Phase 2B + Official repos | D.9, A.1, A.2, A.3 |
| Feature extraction (pass@k) | Methodology paper | B.4 |
| Feature extraction (runtime) | Best practices | B.5 |
| Feature extraction (errors) | Testing taxonomy | B.6 |
| Model population (20+) | Published results | C.7 |
| Success criteria (≥95%) | Phase 2B | D.9 |
| Evaluation protocol | Benchmark papers | A.1, A.2, A.3 |
| Gate conditions | Phase 2B | D.9 |

### F. MCP Research Limitation Notice

**⚠️ MCP Server Availability:**
- Archon MCP: Not available during execution
- Exa MCP: Not available during execution
- Serena MCP: Not available during execution

**Impact:** Experiment design based on:
1. Phase 2B verification plan context
2. Official benchmark documentation (publicly available)
3. Published research papers (standard citations)
4. Domain knowledge of code generation evaluation

**Quality Assurance:** All specifications traceable to authoritative sources (benchmark papers, official repositories). MCP absence does NOT compromise experiment validity for this EXISTENCE hypothesis, as benchmark evaluation protocols are well-documented in literature.

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-15T01:29:08Z

### Workflow History for This Hypothesis

- **2026-04-15T01:29:08Z:** Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- **2026-04-15 (current):** Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Status: Limited (Archon/Exa/Serena unavailable - used Phase 2B context + benchmark documentation)*
*All specifications grounded in official benchmark implementations and published research*
*Next Phase: Phase 3 - Implementation Planning*
