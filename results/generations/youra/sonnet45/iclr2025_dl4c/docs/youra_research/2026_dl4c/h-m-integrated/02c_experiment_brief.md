# Experiment Design: H-M-integrated

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** If alignment methods shape model output distributions through implicit optimization (3-step causal chain: feedback signal selection → repeated training exposure → observable signatures), then we will observe: (M1) execution-focused models dominate correctness dimension (top 15% pass@k rank), (M2) preference-focused models show balanced performance (top 30% across all dimensions), (M3) training dynamics create consistent within-method clustering (intracluster variance < intercluster distance), because feedback signals define what models optimize during alignment training.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal explanations for observed phenomena.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS - Cohen's d = 7.835)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M-integrated
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (Alignment Method Clustering Existence)

### Gate Condition
MUST_WORK gate with failure response:
- IF M1 fails (execution models don't dominate correctness): EXPLORE - check if baseline model differences explain clustering
- IF M2 fails (preference models imbalanced): PIVOT - revise feedback signal theory
- IF M3 fails (high intracluster variance): ABANDON - clustering is noise, not signal

---

## Continuation Context

**Continuation from H-E1:** This hypothesis builds directly on H-E1's successful clustering demonstration. H-E1 established that alignment method signatures exist (EXISTENCE proof), and H-M-integrated now tests the mechanistic explanation for WHY those signatures exist (MECHANISM validation).

**Key Dependency:** All model performance data comes from H-E1. No new model inference or data collection required - this is purely a post-hoc analysis adding a mechanistic interpretation layer.

### Previous Hypothesis Results (if applicable)
**H-E1 Results:** Successfully demonstrated alignment method clustering with Cohen's d = 7.835 (threshold 1.5). Used 4 models (microsoft/phi-2 [execution], Salesforce/codegen-350M-mono [preference], 2 baselines) on HumanEval+ tasks. Clustering achieved 100% alignment purity with 85.4% variance explained by PC1 (correctness-complexity tradeoff).

**Proven Components:**
- HumanEval+ dataset loading (data_loader.py)
- Multi-dimensional profiling (profiler.py: correctness, cyclomatic, AST depth, runtime, memory)
- PCA + k-means clustering (clustering.py)
- Sequential model processing for GPU efficiency (model_manager.py)

**Lessons Learned:**
- Use smaller models for proof-of-concept (phi-2, codegen-350M series worked well)
- Sequential loading prevents GPU OOM issues
- Mock/POC versions enable fast validation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Alignment Method Code Generation**
- Limited direct matches for alignment method signatures in code generation
- Result 1: GenEval framework (https://github.com/djghosh13/geneval)
  - Focus: Evaluating generative models
  - Relevance: General evaluation framework, not specific to alignment method analysis

**Query 2: Model Ranking Performance Clustering**
- Low relevance results - mostly focused on GPU/distributed computing rather than model performance clustering
- No established patterns for ranking models by alignment method signatures

**Query 3: HumanEval Benchmark Evaluation**
- Result 1: GenEval (repeated from Q1)
- Key insight: HumanEval is widely used, but existing work focuses on pass@k metrics rather than multi-dimensional performance profiling

**Summary**: Archon KB has limited prior work on alignment method objective function signatures. This hypothesis explores novel ground - analyzing how different alignment methods create distinguishable performance profiles. H-E1 validation established the clustering infrastructure; this hypothesis extends it to mechanistic analysis.

### Archon Code Examples

**Query 1: Model Ranking and Percentile Analysis**
- Found general baseline comparison patterns (JSON format for model baselines)
- Example from Apple ML Stable Diffusion shows performance metric organization:
  ```python
  {
    "model_version": "stabilityai/stable-diffusion-xl-base-1.0",
    "baselines": {
      "original": 82.2,
      "linear_8bit": 66.025,
      # Multiple quantization recipes with different performance
    }
  }
  ```
  - Pattern: Structured baseline tracking with multiple variants
  - Insight: Can adapt for tracking execution-focused vs preference-focused model rankings

**Query 2: Clustering Variance Analysis**
- Low relevance - mostly CUDA linear algebra operations
- No direct examples for intracluster variance vs intercluster distance analysis

**Key Implementation Needs** (based on search gaps):
1. Percentile ranking per dimension (correctness, complexity, efficiency)
2. Within-method variance calculation (group models by alignment type)
3. Between-method variance comparison (Mann-Whitney U test)
4. Multi-dimensional ranking visualization

### Exa GitHub Implementations

**Query 1: Model Performance Ranking and Percentile Analysis**

**Repository 1**: promptstats (ianarawjo/promptstats) (⭐21)
- **URL**: https://github.com/ianarawjo/promptstats
- **Relevance**: Statistical analysis for comparing LLM performance with bootstrapped confidence intervals
- **Key Features**:
  - Percentile-based performance ranking
  - Bootstrapped confidence intervals for model comparison
  - Robustness metrics (mean, std, CV, IQR, percentiles)
  - Rank correlation analysis
- **Key Code Pattern**:
  ```python
  # Percentile-based ranking with bootstrap CI
  analysis = pstats.analyze(result, reference="grand_mean", n_bootstrap=5_000)
  # Robustness metrics per template
  metrics = robustness_metrics(scores)  # mean, std, CV, IQR, CVaR-10, percentiles
  ```
- **Insight**: Can adapt bootstrap CI approach for ranking execution vs preference models

**Repository 2**: ranky (Didayolo/ranky) (⭐37)
- **URL**: https://github.com/Didayolo/ranky
- **Relevance**: Comprehensive ranking computation and correlation analysis
- **Key Features**:
  - Rank correlation coefficients (Kendall Tau, Spearman)
  - Multiple ranking aggregation methods
  - Concordance measurement across judges
- **Key Code**:
  ```python
  import ranky as rk
  # Rank correlation
  correlation = rk.corr(r1, r2, method='spearman')
  # Concordance across multiple rankings
  concordance = rk.concordance(preference_matrix)
  ```

**Repository 3**: score-analysis (martinsbruveris/score-analysis) (MIT License)
- **URL**: https://github.com/martinsbruveris/score-analysis
- **Relevance**: ML model score analysis with confidence intervals
- **Key Features**:
  - Bootstrap confidence intervals for arbitrary metrics
  - Vectorized confusion matrix operations
  - Group-based metric computation
- **Insight**: Bootstrap CI methodology applicable to within-method variance analysis

**Query 2: HumanEval Implementation and Pass@k Metrics**

**Repository 4**: OpenAI HumanEval (standard benchmark)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval benchmark implementation
- **Pass@k Formula**:
  ```python
  from scipy.special import comb

  def pass_at_k(n: int, c: int, k: int) -> float:
      """
      n: Total number of samples generated
      c: Number of samples that pass all tests
      k: Number of top samples considered
      """
      return 1.0 - comb(n - c, k) / comb(n, k)
  ```
- **Evaluation Pattern**:
  ```python
  # Generate multiple samples per problem
  num_samples_per_task = 200
  samples = [
      dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
      for task_id in problems
      for _ in range(num_samples_per_task)
  ]
  # Calculate pass@1, pass@5, pass@10
  metrics = {
      "pass@1": estimate_pass_at_k(num_samples_list, num_correct_list, 1),
      "pass@5": estimate_pass_at_k(num_samples_list, num_correct_list, 5),
      "pass@10": estimate_pass_at_k(num_samples_list, num_correct_list, 10),
  }
  ```

**Implementation Patterns Identified**:
1. **Percentile Ranking**: Use scipy.stats.percentileofscore for dimension-wise ranking
2. **Variance Analysis**: Bootstrap-based within-group vs between-group variance comparison
3. **Statistical Testing**: Mann-Whitney U test for M3 (scipy.stats.mannwhitneyu)
4. **HumanEval Integration**: Reuse H-E1's data_loader.py and model_manager.py

**Serena Analysis Needed**: No - code patterns are clear and well-documented

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment for H-M-integrated:**
- **No paper reproduction needed** - This is novel mechanistic analysis
- **Priority 1**: H-E1 validated infrastructure (data already exists)
- **Priority 2**: Standard statistical libraries (scipy.stats, numpy - well-documented)
- **Priority 3**: Research repositories for methodology validation (promptstats, ranky - reference only)

**Recommended Implementation Path:**
- Primary: Reuse H-E1 profiling results + implement AlignmentSignatureAnalyzer class
- Fallback: If H-E1 data unavailable, re-run H-E1 experiment first
- Justification: H-E1 already validated the clustering infrastructure. This hypothesis extends with statistical analysis layer using standard scipy/numpy functions. No complex custom implementations needed.

### Code Analysis (Serena MCP)

**Serena Analysis:** Not performed (code patterns clear from documentation)

**Rationale:** The implementation uses standard statistical functions (scipy.stats.percentileofscore, mannwhitneyu) which are well-documented. The Exa search provided clear usage patterns from promptstats and ranky repositories. No complex architectural analysis needed.

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ (164 Python function-level problems)
**Type**: standard benchmark
**Source**: EvalPlus open-source framework
**Statistics**:
- Total problems: 164
- Test cases per problem: ~7-10 (extended from original HumanEval)
- Task types: String manipulation, algorithms, data structures

**Loading Information** (for Phase 4 download):
- Method: EvalPlus framework
- Identifier: `evalplus` library + HumanEval dataset
- Code:
  ```python
  # Install: pip install evalplus
  from evalplus.data import get_human_eval_plus
  problems = get_human_eval_plus()  # Returns dict of 164 problems
  ```

**Reuse from H-E1**:
- data_loader.py: HumanEval+ dataset loading already implemented
- Generated outputs from 4 models (microsoft/phi-2, Salesforce/codegen-350M-mono, Salesforce/codegen-350M-nl, microsoft/CodeGPT-small-py)
- Profiling results: correctness (pass@k), cyclomatic complexity, AST depth, runtime, memory

### Models

#### Model Set (Reused from H-E1)

**Models (4 total)**:
1. **microsoft/phi-2** (execution-focused alignment)
2. **Salesforce/codegen-350M-mono** (preference-based alignment)
3. **Salesforce/codegen-350M-nl** (baseline)
4. **microsoft/CodeGPT-small-py** (baseline)

**Alignment Method Classification**:
- Execution: microsoft/phi-2 (trained with execution feedback)
- Preference: Salesforce/codegen-350M-mono (trained with preference pairs)
- Baseline: codegen-350M-nl, CodeGPT-small-py (no alignment)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifiers: Model names as listed above
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer

  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      device_map="auto",
      torch_dtype=torch.float16
  )
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  ```

**Reuse Strategy**:
- Reuse H-E1's model_manager.py (sequential loading for GPU efficiency)
- Reuse H-E1's generated code samples (already available)
- Reuse H-E1's profiling results (correctness, complexity, efficiency metrics)

#### Proposed Analysis Pipeline

**Architecture:** H-E1 Clustering Infrastructure + Mechanistic Analysis Layer

**Components**:
1. **Data Reuse**: Load H-E1 profiling results (correctness, complexity, efficiency metrics)
2. **Ranking Module**: Compute percentile ranks per dimension
3. **Variance Analysis Module**: Within-method vs between-method variance comparison
4. **Statistical Testing Module**: Mann-Whitney U test for M3

**Core Mechanism Implementation:**

```python
# Core Mechanism: Alignment Method Signature Analysis via Ranking & Variance
# Based on: promptstats (percentile ranking), ranky (correlation), scipy.stats (statistical tests)

import numpy as np
from scipy.stats import percentileofscore, mannwhitneyu
from typing import Dict, List

class AlignmentSignatureAnalyzer:
    """
    Analyzes objective function signatures via dimension-wise ranking and variance analysis.
    Tests M1 (execution dominance), M2 (preference balance), M3 (within-method clustering).
    """
    def __init__(self, performance_data: Dict[str, Dict[str, float]]):
        """
        Args:
            performance_data: {model_name: {
                "correctness": float,
                "complexity": float,
                "efficiency": float,
                "alignment_method": str  # "execution" | "preference" | "baseline"
            }}
        """
        self.data = performance_data
        self.dimensions = ["correctness", "complexity", "efficiency"]

    def compute_percentile_ranks(self) -> Dict[str, Dict[str, float]]:
        """Compute percentile rank for each model on each dimension."""
        ranks = {}
        for dim in self.dimensions:
            scores = [self.data[m][dim] for m in self.data]
            for model in self.data:
                score = self.data[model][dim]
                # Lower percentile = better rank (top 15% = ≤15th percentile)
                percentile = percentileofscore(scores, score, kind='rank')
                ranks.setdefault(model, {})[dim] = percentile
        return ranks

    def test_m1_execution_dominance(self, ranks: Dict) -> bool:
        """M1: Execution models dominate correctness (top 15% = ≤15th percentile)."""
        execution_models = [m for m in self.data if self.data[m]["alignment_method"] == "execution"]
        mean_correctness_rank = np.mean([ranks[m]["correctness"] for m in execution_models])
        return mean_correctness_rank <= 15.0  # Top 15%

    def test_m2_preference_balance(self, ranks: Dict) -> bool:
        """M2: Preference models balanced across all dimensions (top 30%)."""
        preference_models = [m for m in self.data if self.data[m]["alignment_method"] == "preference"]
        mean_ranks = [np.mean([ranks[m][dim] for dim in self.dimensions]) for m in preference_models]
        overall_mean = np.mean(mean_ranks)
        return overall_mean <= 30.0  # Top 30% across all dimensions

    def test_m3_clustering_consistency(self) -> tuple:
        """M3: Within-method variance < between-method variance (Mann-Whitney U, p<0.05)."""
        # Group correctness scores by alignment method
        method_groups = {}
        for model, data in self.data.items():
            method = data["alignment_method"]
            method_groups.setdefault(method, []).append(data["correctness"])

        # Compare within-method vs between-method variance
        methods = list(method_groups.keys())
        if len(methods) < 2:
            return False, 1.0

        # Mann-Whitney U test between first two method groups
        stat, pvalue = mannwhitneyu(method_groups[methods[0]], method_groups[methods[1]], alternative='two-sided')
        return pvalue < 0.05, pvalue

    def analyze(self) -> Dict:
        """Run full mechanistic analysis."""
        ranks = self.compute_percentile_ranks()
        m1_pass = self.test_m1_execution_dominance(ranks)
        m2_pass = self.test_m2_preference_balance(ranks)
        m3_pass, m3_pvalue = self.test_m3_clustering_consistency()

        return {
            "ranks": ranks,
            "M1_execution_dominance": m1_pass,
            "M2_preference_balance": m2_pass,
            "M3_clustering_consistency": m3_pass,
            "M3_pvalue": m3_pvalue,
            "overall_pass": m1_pass and m2_pass and m3_pass
        }

# Integration: Use after H-E1 profiling results are loaded
# Input: performance_data from profiler.py
# Output: M1/M2/M3 test results for gate validation
```

### Training Protocol

**No Training Required** - This is a post-hoc analysis of H-E1 results.

**Reuse from H-E1**:
- Generated code samples (already available)
- Profiling results: correctness (pass@k), cyclomatic complexity, AST depth, runtime, memory
- Model outputs stored in H-E1 validation artifacts

**Analysis Configuration**:
- **Seeds**: Single analysis run (deterministic ranking computation)
- **Data Source**: H-E1 profiling results from `/docs/youra_research/20260317_dl4c/h-e1/code/` output files
- **Statistical Threshold**: p < 0.05 for M3 (Mann-Whitney U test)

### Evaluation

**Primary Metrics** (M1, M2, M3):

1. **M1: Execution Dominance** (correctness percentile rank ≤ 15%)
   - Metric: Mean percentile rank of execution-focused models on correctness dimension
   - Success: ≤ 15th percentile (top 15%)
   - Library: `scipy.stats.percentileofscore`
   - Code:
     ```python
     from scipy.stats import percentileofscore

     # Compute percentile for each execution model
     scores = [data[m]["correctness"] for m in models]
     exec_ranks = [percentileofscore(scores, data[m]["correctness"])
                   for m in execution_models]
     m1_pass = np.mean(exec_ranks) <= 15.0
     ```

2. **M2: Preference Balance** (mean rank across all dimensions ≤ 30%)
   - Metric: Mean percentile rank of preference-focused models across correctness, complexity, efficiency
   - Success: ≤ 30th percentile (top 30%) on average
   - Library: `scipy.stats.percentileofscore` + `numpy`
   - Code:
     ```python
     mean_ranks = []
     for pref_model in preference_models:
         ranks_per_dim = [percentileofscore(all_scores[dim], data[pref_model][dim])
                          for dim in dimensions]
         mean_ranks.append(np.mean(ranks_per_dim))
     m2_pass = np.mean(mean_ranks) <= 30.0
     ```

3. **M3: Clustering Consistency** (within-method variance < between-method variance, p < 0.05)
   - Metric: Mann-Whitney U test comparing method groups
   - Success: p-value < 0.05 (statistically significant separation)
   - Library: `scipy.stats.mannwhitneyu`
   - Code:
     ```python
     from scipy.stats import mannwhitneyu

     # Group scores by alignment method
     execution_scores = [data[m]["correctness"] for m in execution_models]
     baseline_scores = [data[m]["correctness"] for m in baseline_models]

     stat, pvalue = mannwhitneyu(execution_scores, baseline_scores, alternative='two-sided')
     m3_pass = pvalue < 0.05
     ```

**Gate Validation**:
- **MUST_WORK Gate**: M1 AND M2 must pass
- **Secondary Condition**: M3 should pass (clustering consistency)
- **Overall Success**: All three mechanisms validated

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Post-hoc statistical analysis (ranking, variance, hypothesis testing)
- Library: `scipy.stats` (percentileofscore, mannwhitneyu), `numpy`
- Code:
  ```python
  from scipy.stats import percentileofscore, mannwhitneyu
  import numpy as np

  # All ranking and statistical testing implemented in AlignmentSignatureAnalyzer class above
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: M1/M2/M3 pass/fail indicators

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Dimension-wise Percentile Ranks**: Bar chart showing each model's percentile rank on correctness, complexity, efficiency
2. **Alignment Method Comparison**: Grouped bar chart comparing execution vs preference vs baseline groups
3. **M1 Validation Plot**: Execution models' correctness ranks with 15th percentile threshold line
4. **M2 Validation Plot**: Preference models' mean ranks across dimensions with 30th percentile threshold
5. **M3 Variance Analysis**: Box plots showing within-method vs between-method score distributions
6. **Statistical Test Results**: P-value visualization for Mann-Whitney U test

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. M1 passes: execution models mean correctness rank ≤ 15th percentile
2. M2 passes: preference models mean rank ≤ 30th percentile across all dimensions
3. M3 passes: within-method variance < between-method variance (p < 0.05)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited Relevance**: Alignment method objective function signatures represent novel research ground. Archon KB had minimal direct matches.

**Source 1**: GenEval Framework
- **Type**: GitHub repository (https://github.com/djghosh13/geneval)
- **Query Used**: "alignment method code generation", "HumanEval benchmark evaluation"
- **Relevance**: General evaluation framework for generative models
- **Key Insights**:
  - HumanEval is widely used standard
  - Focus on pass@k metrics
- **Used For**: Confirming HumanEval+ as appropriate benchmark

**Archon Code Examples**: Low relevance (GPU/distributed computing focus rather than model ranking)

### B. GitHub Implementations (Exa)

**Repository 1**: promptstats (ianarawjo/promptstats) (⭐21)
- **URL**: https://github.com/ianarawjo/promptstats
- **Query Used**: "model performance ranking percentile analysis Python implementation"
- **Relevance**: Statistical analysis for LLM performance comparison with bootstrap CI
- **Key Features**:
  - Percentile-based ranking: `analysis = pstats.analyze(result, reference="grand_mean")`
  - Robustness metrics: mean, std, CV, IQR, percentiles per template
  - Bootstrap confidence intervals (n_bootstrap=5_000)
- **Used For**: M1/M2 percentile ranking methodology, statistical rigor patterns

**Repository 2**: ranky (Didayolo/ranky) (⭐37)
- **URL**: https://github.com/Didayolo/ranky
- **Query Used**: "model performance ranking percentile analysis"
- **Relevance**: Ranking computation and correlation analysis
- **Key Code**:
  ```python
  import ranky as rk
  # Rank correlation (Kendall Tau, Spearman)
  correlation = rk.corr(r1, r2, method='spearman')
  # Concordance measurement
  concordance = rk.concordance(preference_matrix)
  ```
- **Used For**: Ranking methodology reference, correlation analysis patterns

**Repository 3**: score-analysis (martinsbruveris/score-analysis) (MIT)
- **URL**: https://github.com/martinsbruveris/score-analysis
- **Query Used**: "model performance ranking"
- **Relevance**: Bootstrap CI for ML model metrics
- **Key Pattern**:
  ```python
  def metric(scores: Scores) -> np.ndarray:
      return np.mean(scores.pos)  # Custom metric

  ci = scores.bootstrap_ci(metric=metric, alpha=0.05)
  ```
- **Used For**: Bootstrap methodology for M3 variance analysis

**Repository 4**: OpenAI HumanEval (Official Benchmark)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "HumanEval code generation model evaluation metrics implementation"
- **Relevance**: Official pass@k implementation
- **Key Code**:
  ```python
  from scipy.special import comb

  def pass_at_k(n: int, c: int, k: int) -> float:
      """n: total samples, c: correct samples, k: top-k"""
      return 1.0 - comb(n - c, k) / comb(n, k)

  # Evaluation pattern
  metrics = {
      "pass@1": estimate_pass_at_k(num_samples, num_correct, 1),
      "pass@5": estimate_pass_at_k(num_samples, num_correct, 5),
      "pass@10": estimate_pass_at_k(num_samples, num_correct, 10),
  }
  ```
- **Used For**: Confirming H-E1's correctness metric calculation, pass@k formula validation

### C. Scipy/NumPy Statistical Functions

**Source**: scipy.stats documentation
- **Functions Used**:
  - `percentileofscore(a, score, kind='rank')`: Compute percentile rank (M1, M2)
  - `mannwhitneyu(x, y, alternative='two-sided')`: Non-parametric test (M3)
- **Used For**: Core statistical analysis implementation

### D. H-E1 Infrastructure (Reused Components)

**Source**: H-E1 Validation Report (`/docs/youra_research/20260317_dl4c/h-e1/04_validation.md`)
- **Reused Modules**:
  - `data_loader.py`: HumanEval+ dataset loading
  - `profiler.py`: Multi-dimensional profiling (correctness, cyclomatic, AST depth, runtime, memory)
  - `model_manager.py`: Sequential model loading for GPU efficiency
  - `clustering.py`: PCA + k-means (not used in H-M-integrated, but available)
- **Performance Data**: 4 models × 5 dimensions already profiled
- **Used For**: Input data for mechanistic analysis (no new model inference required)

### E. Implementation Priority Assessment

**Primary Source**: H-E1 validated infrastructure
- **Rationale**: H-E1 successfully demonstrated clustering (Cohen's d = 7.835)
- **Extension Strategy**: Add ranking/variance analysis layer on top of existing profiling results
- **Advantage**: No new data collection, GPU costs, or model inference needed

**Fallback**: If H-E1 data unavailable, re-run H-E1 experiment pipeline first

---

**Traceability Summary**:
- All percentile ranking methodology: promptstats, ranky, scipy.stats
- All statistical testing: scipy.stats (Mann-Whitney U)
- All HumanEval metrics: OpenAI HumanEval official implementation
- All infrastructure: H-E1 validated components
- Novel contribution: Integration of ranking + variance analysis to test mechanistic hypotheses (M1, M2, M3)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18

### Workflow History for This Hypothesis

**Phase 2B → Phase 2C Timeline:**
- 2026-03-18T17:29:00Z: Phase 2B completed - Generated verification plan with H-E1 and H-M-integrated
- 2026-03-18T20:15:44Z: Hypothesis h-m-integrated set to IN_PROGRESS
- 2026-03-18T20:22:44Z: Phase 2C completed - Experiment design with mechanistic analysis specification

**Status:**
- experiment_design.status: COMPLETED
- experiment_design.file: docs/youra_research/20260317_dl4c/h-m-integrated/02c_experiment_brief.md
- Next Phase: Phase 3 (Implementation Planning)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
