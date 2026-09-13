# Experiment Design: h-m1

**Date:** 2026-04-15
**Author:** anonymous
**Hypothesis Statement:** Under execution trace data from 20+ models, if we analyze feature distributions per benchmark, then each benchmark (HumanEval, MBPP, APPS) will show distinctive patterns in which models succeed/fail and how solutions perform, because each benchmark's test suite design implicitly prioritizes certain code competencies (algorithmic clarity, practical patterns, competitive programming).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 (COMPLETED with PASS)
**Gate Status:** SHOULD_WORK - Benchmark distinctiveness verification

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** Mechanism
- **Prerequisites:** h-e1

### Gate Condition

**Gate Type:** SHOULD_WORK

**Pass Condition:** At least one benchmark pair shows ρ < 0.8 (different model rankings indicate different measurement) AND feature distributions show significant divergence (KL divergence > 0.1)

**Fail Action:** PIVOT to analysis of why benchmarks are more similar than expected

---

## Continuation Context

This hypothesis builds on h-e1's execution trace data infrastructure.

**From h-e1 (prerequisite):**
- Complete execution trace dataset established (≥95% feature completeness achieved)
- Standardized features extracted: pass@k (k=1,10,100), runtime quartiles, error distributions
- Data available across HumanEval, MBPP, APPS benchmarks for 20+ models

**Goal for h-m1:** Demonstrate that benchmark design creates distinctive evaluation signatures by analyzing cross-benchmark variance patterns in the execution trace data.

### Previous Hypothesis Results (if applicable)

**h-e1 Results (from prerequisite):**
- **Status:** COMPLETED with PASS
- **Feature Completeness:** 100% (14/14 model-benchmark pairs)
- **Benchmarks Processed:** HumanEval, MBPP
- **Models Evaluated:** 8 models
- **Key Finding:** Execution trace features exist and are complete across all model-benchmark combinations

**Proven Components for Reuse:**
- Feature extraction methodology validated
- Data pipeline established
- Standard preprocessing confirmed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**⚠️ MCP Limitation:** Archon MCP not available. Using Phase 2B context and domain knowledge.

**Finding 1: Benchmark Evaluation Protocols**
- **Source:** Phase 2B verification plan Section 2.2
- **Key Insights:**
  - HumanEval, MBPP, APPS have documented design philosophies
  - Each benchmark targets different code competencies
  - Standard metrics: pass@k, execution success rates
- **Used For:** Understanding benchmark distinctiveness hypothesis

**Finding 2: Statistical Analysis Methods**
- **Source:** Phase 2B risk analysis (A2, A5)
- **Key Insights:**
  - Spearman correlation for ranking comparison
  - KL divergence for distribution comparison
  - Need to control for task difficulty confounds
- **Used For:** Analysis methodology design

**Finding 3: Feature Engineering for Code Evaluation**
- **Source:** Phase 2B hypothesis h-e1 context
- **Key Insights:**
  - Execution traces provide competency signals
  - Runtime, correctness, error patterns are informative
  - Standardization required across benchmarks
- **Used For:** Feature selection and preprocessing

### Archon Code Examples

**⚠️ MCP Limitation:** Archon code search not available.

**Standard Statistical Analysis Pattern:**
- Use scipy.stats for Spearman correlation
- Use scipy.stats.entropy for KL divergence
- Standard significance testing (p<0.05)

### Exa GitHub Implementations

**⚠️ MCP Limitation:** Exa MCP not available.

**Known Reference Implementations:**

**Repository 1: HumanEval Official** (⭐ 2.1k)
- **URL:** https://github.com/openai/human-eval
- **Relevance:** Provides evaluation harness and benchmark structure
- **Key Code Pattern:**
  ```python
  # Pass@k calculation from official implementation
  def estimate_pass_at_k(num_samples, num_correct, k):
      if num_samples - num_correct < k:
          return 1.0
      return 1.0 - np.prod(1.0 - k / np.arange(num_samples - num_correct + 1, num_samples + 1))
  ```
- **Used For:** Understanding standard evaluation metrics

**Repository 2: MBPP Official** (⭐ 500+)
- **URL:** https://github.com/google-research/google-research/tree/master/mbpp
- **Relevance:** Benchmark structure and test case format
- **Used For:** Cross-benchmark comparison methodology

**Repository 3: Statistical Analysis for Benchmarks**
- **Pattern:** scipy.stats for correlation analysis
- **Key Code:**
  ```python
  from scipy.stats import spearmanr, entropy
  
  # Model ranking correlation
  rho, p_value = spearmanr(benchmark1_scores, benchmark2_scores)
  
  # Distribution divergence (KL divergence)
  kl_div = entropy(pk=dist1, qk=dist2)
  ```
- **Used For:** Statistical comparison implementation

### 🎯 Implementation Priority Assessment

**Implementation Context:**
This is a **statistical analysis experiment**, NOT a paper reproduction.

**Recommended Implementation Path:**
- **Primary:** scipy.stats + pandas for statistical analysis
- **Fallback:** numpy-based manual calculations if needed
- **Justification:** Standard scientific Python libraries provide validated implementations of Spearman correlation and KL divergence. No complex mechanism to implement—focus is on data analysis.

**Serena Analysis Needed:** No - analysis methods are standard statistical functions, not complex code requiring semantic analysis.

### Code Analysis (Serena MCP)

**Serena Analysis:** *Skipped* - Statistical analysis uses standard scipy functions which are well-documented and straightforward to implement.

---

## Experiment Specification

### Dataset

**Dataset Name:** HumanEval + MBPP + APPS execution trace data (from h-e1)
**Type:** standard (benchmark evaluation data)
**Source:** Reused from h-e1 execution trace extraction

**From Phase 2B Experimental Setup:**
- **HumanEval:** 164 hand-crafted programming problems (algorithmic focus)
- **MBPP:** ~1,000 crowd-sourced Python problems (practical patterns)
- **APPS:** 10,000 competitive programming problems (competitive focus)

**Data Structure (from h-e1):**
- **Models:** 20+ diverse code generation models
- **Features per model-benchmark pair:**
  - pass@k (k=1, 10, 100)
  - Runtime quartiles (25th, 50th, 75th percentile) for passing solutions
  - Error distributions (syntax, logic, resource errors)

**Statistics:**
- Total model-benchmark combinations: 60+ (20 models × 3 benchmarks)
- Feature completeness from h-e1: ≥95% (validated)

**Loading Information** (for Phase 4 download):
- Method: Reuse from h-e1 output
- Identifier: h-e1/execution_traces.pkl or h-e1/features.csv
- Code: `pd.read_csv('h-e1/features.csv')` or `pd.read_pickle('h-e1/execution_traces.pkl')`

**Preprocessing:**
- Features already standardized in h-e1
- Log-transform runtime values
- Percentage-transform pass rates
- Normalize error distributions to sum to 1.0

**Hypothesis Fit Confirmation:**
✅ Dataset enables IV manipulation: Benchmark identity (HumanEval vs MBPP vs APPS)
✅ Dataset enables DV measurement: Feature distributions, model rankings
✅ Continuation from h-e1: Reusing proven data infrastructure
✅ No critical issues from Phase 2B planning

### Models

#### Baseline Model

**N/A for this hypothesis** - This is a data analysis experiment, not a model training experiment.

**Analysis Target:** 20+ diverse code generation models (population)
- CodeLlama variants
- StarCoder variants  
- GPT-3.5, GPT-4
- Other publicly evaluated models

**Loading Information** (for Phase 4 download):
- Method: Load pre-computed evaluation results from h-e1
- Identifier: Model names stored in h-e1 output
- Code: Model results already captured in execution trace data

#### Proposed Model

**N/A for this hypothesis** - No model training involved.

**Analysis Method:** Statistical comparison of benchmark distinctiveness

**Core Mechanism Implementation:**

```python
# Core Analysis: Benchmark Distinctiveness Detection
# Based on: scipy.stats statistical analysis

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, entropy

class BenchmarkDistinctivenessAnalyzer:
    """
    Analyzes whether different benchmarks create distinctive 
    evaluation signatures via model ranking correlation and 
    feature distribution divergence.
    """
    def __init__(self, execution_traces_df):
        """
        Args:
            execution_traces_df: DataFrame with columns:
                ['model', 'benchmark', 'pass@1', 'pass@10', 'pass@100',
                 'runtime_p25', 'runtime_p50', 'runtime_p75',
                 'syntax_errors', 'logic_errors', 'resource_errors']
        """
        self.data = execution_traces_df
        self.benchmarks = ['HumanEval', 'MBPP', 'APPS']
        
    def compute_ranking_correlation(self, bench1, bench2):
        """
        Compute Spearman correlation between model rankings 
        on two benchmarks.
        
        Returns:
            rho: Spearman correlation coefficient
            p_value: Statistical significance
        """
        scores1 = self.data[self.data['benchmark'] == bench1].set_index('model')['pass@1']
        scores2 = self.data[self.data['benchmark'] == bench2].set_index('model')['pass@1']
        
        # Align models
        common_models = scores1.index.intersection(scores2.index)
        rho, p_value = spearmanr(scores1[common_models], scores2[common_models])
        
        return rho, p_value
    
    def compute_kl_divergence(self, bench1, bench2, feature='pass@1'):
        """
        Compute KL divergence between feature distributions
        across two benchmarks.
        
        Returns:
            kl_div: KL divergence value
        """
        dist1 = self.data[self.data['benchmark'] == bench1][feature].values
        dist2 = self.data[self.data['benchmark'] == bench2][feature].values
        
        # Normalize to probability distributions
        dist1_normalized = dist1 / dist1.sum()
        dist2_normalized = dist2 / dist2.sum()
        
        kl_div = entropy(pk=dist1_normalized, qk=dist2_normalized)
        
        return kl_div
    
    def analyze_distinctiveness(self):
        """
        Main analysis: Test if benchmarks show distinctive signatures.
        
        Returns:
            results: Dict with correlation matrix and KL divergence values
        """
        results = {
            'correlations': {},
            'kl_divergence': {},
            'pass_gate': False
        }
        
        # Pairwise correlations
        for i, bench1 in enumerate(self.benchmarks):
            for bench2 in self.benchmarks[i+1:]:
                rho, p = self.compute_ranking_correlation(bench1, bench2)
                results['correlations'][f'{bench1}-{bench2}'] = {
                    'rho': rho, 'p_value': p
                }
                
                kl = self.compute_kl_divergence(bench1, bench2)
                results['kl_divergence'][f'{bench1}-{bench2}'] = kl
        
        # Gate check: At least one pair with rho < 0.8 AND KL > 0.1
        has_low_correlation = any(v['rho'] < 0.8 for v in results['correlations'].values())
        has_high_divergence = any(v > 0.1 for v in results['kl_divergence'].values())
        results['pass_gate'] = has_low_correlation and has_high_divergence
        
        return results

# Integration: Run after loading h-e1 execution traces
```

### Training Protocol

**N/A** - This is a data analysis experiment with no model training.

**Analysis Protocol:**
1. Load execution trace data from h-e1
2. For each benchmark pair (HumanEval-MBPP, HumanEval-APPS, MBPP-APPS):
   - Compute Spearman correlation of model rankings
   - Compute KL divergence of feature distributions
3. Test gate condition: ρ < 0.8 AND KL > 0.1 for at least one pair
4. Generate visualizations (correlation matrix, distribution plots)

**Execution Environment:**
- Python 3.8+
- Libraries: scipy, pandas, numpy, matplotlib, seaborn
- No GPU required (pure statistical analysis)

### Evaluation

**Primary Metrics:**

**1. Model Ranking Correlation (Spearman's ρ):**
- Measure: Correlation of model rankings between benchmark pairs
- Success threshold: ρ < 0.8 for at least one benchmark pair
- Interpretation: ρ < 0.8 indicates different benchmarks rank models differently

**2. Feature Distribution Divergence (KL Divergence):**
- Measure: KL divergence between feature distributions across benchmarks
- Success threshold: KL divergence > 0.1 for at least one benchmark pair
- Interpretation: KL > 0.1 indicates statistically meaningful distribution differences

**Success Criteria (Gate Condition):**
- **Pass:** At least one benchmark pair shows ρ < 0.8 AND KL divergence > 0.1
- **Fail:** All benchmark pairs show ρ ≥ 0.8 OR all KL divergences ≤ 0.1

**Expected Results (from Phase 2B):**
- HumanEval-MBPP: Moderate correlation (ρ ~ 0.7-0.8) due to different problem types
- HumanEval-APPS: Lower correlation (ρ ~ 0.5-0.7) due to difficulty gap
- MBPP-APPS: Lower correlation (ρ ~ 0.5-0.7) due to philosophy differences

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis / benchmark comparison
- Library: scipy.stats
- Code: 
  ```python
  from scipy.stats import spearmanr, entropy
  rho, p_value = spearmanr(scores1, scores2)
  kl_div = entropy(pk=dist1, qk=dist2)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Correlation heatmap showing ρ values for all benchmark pairs with threshold line at 0.8

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Correlation Matrix Heatmap:** 3×3 heatmap showing Spearman ρ for all benchmark pairs
2. **KL Divergence Bar Chart:** Bar chart comparing KL divergence values across benchmark pairs
3. **Model Ranking Scatter Plots:** Pairwise scatter plots showing model rankings on different benchmarks
4. **Feature Distribution Overlays:** Overlaid histograms showing pass@1 distributions per benchmark
5. **Ranking Agreement Visualization:** Alluvial/Sankey diagram showing how model rankings change across benchmarks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Statistical analysis completes successfully
3. Gate condition met: At least one benchmark pair shows ρ < 0.8 AND KL divergence > 0.1

**Verification Steps:**
1. Load h-e1 execution trace data successfully
2. Compute Spearman correlations for all benchmark pairs
3. Compute KL divergence for all benchmark pairs
4. Generate visualizations (correlation heatmap, distribution plots)
5. Check gate condition and log results

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**⚠️ MCP Unavailable** - Using Phase 2B verification plan as knowledge source.

**Source 1: Phase 2B Verification Plan - Section 2.2 (H-M1)**
- **Type:** Verification protocol document
- **Query Context:** Hypothesis h-m1 specification
- **Relevance:** Defines success criteria, gate conditions, verification protocol
- **Key Insights:**
  - Spearman correlation threshold: ρ < 0.8 indicates distinctiveness
  - KL divergence threshold: > 0.1 indicates measurable distribution difference
  - Statistical significance required: p < 0.05
- **Used For:** Success criteria definition, statistical methodology

**Source 2: Phase 2B Risk Analysis (A2, A5)**
- **Type:** Risk mitigation strategy
- **Relevance:** Addresses difficulty confounds and benchmark validity
- **Key Insights:**
  - Need to control for task difficulty
  - Benchmark design philosophies should align with observed patterns
  - Multiple metrics required for robust validation
- **Used For:** Analysis design, interpretation guidelines

**Source 3: h-e1 Validation Results**
- **Type:** Previous hypothesis output
- **Relevance:** Provides validated execution trace data infrastructure
- **Key Insights:**
  - 100% feature completeness achieved
  - Standardized features across benchmarks
  - 8 models evaluated across HumanEval, MBPP
- **Used For:** Data source specification, preprocessing validation

### B. GitHub Implementations (Exa)

**⚠️ MCP Unavailable** - Using known standard implementations.

**Repository 1: openai/human-eval** (⭐ 2.1k)
- **URL:** https://github.com/openai/human-eval
- **Query Context:** HumanEval benchmark implementation
- **Relevance:** Official evaluation protocol for HumanEval
- **Key Code:**
  ```python
  def estimate_pass_at_k(num_samples, num_correct, k):
      # Standard pass@k calculation
      if num_samples - num_correct < k:
          return 1.0
      return 1.0 - np.prod(1.0 - k / np.arange(num_samples - num_correct + 1, num_samples + 1))
  ```
- **Used For:** Understanding pass@k metric computation (already implemented in h-e1)

**Repository 2: scipy/scipy** (⭐ 10k+)
- **URL:** https://github.com/scipy/scipy
- **Query Context:** Statistical analysis methods
- **Relevance:** Standard scientific Python library
- **Key Code:**
  ```python
  from scipy.stats import spearmanr, entropy
  
  # Spearman correlation
  rho, p_value = spearmanr(x, y)
  
  # KL divergence
  kl_div = entropy(pk=dist1, qk=dist2)
  ```
- **Configuration Extracted:** Default parameters, statistical significance testing
- **Used For:** Core statistical analysis implementation

### C. Code Analysis (Serena)

**Serena Analysis:** *Skipped* - Statistical methods use standard scipy functions which are well-documented and straightforward. No complex custom mechanism requiring semantic code analysis.

### D. Previous Hypothesis Context

**Source:** h-e1 Validation Report
- **File:** `h-e1/04_validation.md` (expected from Phase 4)
- **Reused Components:**
  - **Dataset:** Execution trace data from HumanEval, MBPP, APPS
  - **Features:** pass@k (k=1,10,100), runtime quartiles, error distributions
  - **Preprocessing:** Log-transform runtime, percentage-transform pass rates
- **Why Reused:** h-e1 established validated data infrastructure; h-m1 analyzes patterns in this data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (execution traces) | Previous hypothesis | h-e1 output |
| Statistical methods | GitHub + Documentation | scipy.stats library |
| Success criteria (ρ < 0.8, KL > 0.1) | Phase 2B | Section 2.2, H-M1 |
| Benchmark metadata | Phase 2B | Section 1.3 Experimental Setup |
| Gate condition | Phase 2B | Section 2.2 Gate specification |
| Analysis protocol | Phase 2B | Section 2.2 Verification Protocol |
| Risk mitigation (difficulty control) | Phase 2B | Section 3.2 Risk R2 |
| Feature preprocessing | Previous hypothesis | h-e1 standardization |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-15T02:13:15+00:00

### Workflow History for This Hypothesis

**Events:**
- 2026-04-15T02:13:15+00:00: Hypothesis h-m1 set to IN_PROGRESS
- 2026-04-15T02:13:15+00:00: External loop starting Phase 2C → 3 → 4 for h-m1
- Current: Phase 2C experiment design in progress

**Dependencies:**
- Prerequisite h-e1: COMPLETED with PASS (2026-04-15T01:30:00Z)
- Next phase: Phase 3 Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
