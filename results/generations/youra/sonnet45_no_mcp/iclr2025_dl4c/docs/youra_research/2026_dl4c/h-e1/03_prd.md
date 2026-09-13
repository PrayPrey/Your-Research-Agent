# Product Requirements Document: h-e1 Execution Trace Feature Extraction

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-15  
**Author:** Phase 3 Implementation Planning  
**Type:** Data Infrastructure Validation  

---

## 1. Executive Summary

### 1.1 Problem Statement
Validate that standardized execution trace features (pass@k, runtime quartiles, error distributions) can be extracted for 20+ code generation models across three major benchmarks (HumanEval, MBPP, APPS). This foundational data infrastructure is required for all downstream dimensional analysis hypotheses.

### 1.2 Success Criteria
- **Primary:** ≥95% of model-benchmark combinations have complete execution trace features
- **Secondary:** Features are standardized and comparable across benchmarks
- **Gate:** MUST_WORK - Failure blocks entire verification workflow

### 1.3 Scope
**In Scope:**
- Feature extraction from published benchmark results (pass@k scores)
- Runtime data collection for available model implementations
- Error categorization from execution logs
- Feature standardization across 3 benchmarks

**Out of Scope:**
- Model training or fine-tuning
- Novel benchmark development
- Benchmark reproduction from scratch (use published results where available)

---

## 2. Functional Requirements

### FR-1: Benchmark Dataset Access
**Priority:** HIGH  
**Description:** Access and load three execution-based benchmarks

**Acceptance Criteria:**
- HumanEval: 164 problems loaded from official source
- MBPP: ~1,000 problems loaded from HuggingFace datasets
- APPS: 10,000 problems loaded (subset for runtime evaluation)

**Implementation Notes:**
```python
# HumanEval
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")

# MBPP
mbpp = load_dataset("mbpp")

# APPS
apps = load_dataset("codeparrot/apps")
```

### FR-2: Published Results Collection
**Priority:** HIGH  
**Description:** Collect pass@k scores from published papers for 20+ models

**Acceptance Criteria:**
- Minimum 20 models with HumanEval results
- Minimum 15 models with MBPP results
- Minimum 10 models with APPS results

**Data Sources:**
- HumanEval leaderboard (Papers with Code)
- BigCode evaluation harness results
- Individual model papers (CodeLlama, StarCoder, etc.)

**Models to Include:**
- GPT-3.5, GPT-4 (published results)
- CodeLlama: 7B, 13B, 34B, 70B
- StarCoder: 15B, StarCoder2
- DeepSeek-Coder: 6.7B, 33B
- WizardCoder: 15B, 34B
- Phind-CodeLlama-34B-v2
- Codestral (Mistral)
- Claude-2, Claude-3 (published results)

### FR-3: Pass@k Feature Extraction
**Priority:** HIGH  
**Description:** Extract pass@1, pass@10, pass@100 metrics for each model-benchmark pair

**Acceptance Criteria:**
- All three pass@k values extracted for each combination
- Standard pass@k formula applied (Chen et al. 2021)
- Missing values documented with reasons

**Formula:**
```
pass@k = E[1 - (n-c choose k) / (n choose k)]
where n = total samples, c = correct samples
```

### FR-4: Runtime Quartile Extraction
**Priority:** MEDIUM  
**Description:** Compute runtime distribution for passing solutions

**Acceptance Criteria:**
- Runtime quartiles (25th, 50th, 75th percentile) for each model-benchmark
- Only computed for passing solutions
- Controlled execution environment (timeout limits)

**Implementation Requirements:**
- Sandboxed execution (Docker or isolated Python env)
- Timeout: 10-30 seconds per test case
- Record runtime in milliseconds

### FR-5: Error Distribution Extraction
**Priority:** MEDIUM  
**Description:** Categorize error modes from failed solutions

**Acceptance Criteria:**
- Three error categories: syntax, runtime, timeout
- Error distribution percentages for each model-benchmark
- Systematic categorization across all failures

**Error Categories:**
- **Syntax:** Code doesn't parse
- **Runtime:** Execution failures (exceptions, assertion errors)
- **Timeout:** Execution exceeds time limit

### FR-6: Feature Completeness Validation
**Priority:** HIGH  
**Description:** Verify ≥95% completeness across all model-benchmark combinations

**Acceptance Criteria:**
- Feature completeness rate calculated
- Missing data documented with reasons
- Validation report generated

**Validation Logic:**
```python
feature_completeness = (complete_model_benchmark_pairs / total_pairs) * 100
# Target: ≥ 95%
```

---

## 3. Non-Functional Requirements

### NFR-1: Data Quality
- All features must be standardized across benchmarks
- Missing values explicitly marked (not zero-filled)
- Reproducible extraction methodology

### NFR-2: Computational Resources
- No GPU required (data extraction only)
- Execution sandbox for runtime measurement
- Storage: ~10GB for benchmarks + model outputs

### NFR-3: Timeline
- Phase 1: Published results collection (1 week)
- Phase 2: Runtime data collection (1 week)
- Phase 3: Error categorization (3-5 days)
- Phase 4: Validation (1 day)
- **Total:** 2-3 weeks

### NFR-4: Documentation
- Feature extraction methodology documented
- Data sources cited
- Missing data patterns analyzed

---

## 4. Data Specifications

### 4.1 Input Data

**Dataset 1: HumanEval**
- Source: `openai_humaneval` (HuggingFace datasets)
- Size: 164 hand-crafted problems
- Format: JSON with problem descriptions, test cases
- Auto-download: Yes

**Dataset 2: MBPP**
- Source: `mbpp` (HuggingFace datasets)
- Size: ~1,000 Python problems
- Format: JSON with 3 test cases per problem
- Auto-download: Yes

**Dataset 3: APPS**
- Source: `codeparrot/apps` (HuggingFace datasets)
- Size: 10,000 competitive programming problems
- Format: Difficulty-stratified (Introductory, Interview, Competition)
- Auto-download: Yes

### 4.2 Output Data Schema

**Feature Vector per Model-Benchmark:**
```python
{
    "model": str,
    "benchmark": str,  # "HumanEval" | "MBPP" | "APPS"
    "pass@1": float,
    "pass@10": float,
    "pass@100": float,
    "runtime_q25": float,  # milliseconds
    "runtime_q50": float,
    "runtime_q75": float,
    "error_syntax": float,  # percentage
    "error_runtime": float,
    "error_timeout": float
}
```

**Output Format:** CSV or Pandas DataFrame for analysis

---

## 5. Evaluation Metrics

### 5.1 Primary Metric: Feature Completeness Rate
```python
feature_completeness = (complete_model_benchmark_pairs / total_pairs) * 100
# Success: ≥ 95%
```

### 5.2 Expected Coverage
- HumanEval: ~100% (most widely benchmarked)
- MBPP: ~90% (less common but growing)
- APPS: ~70-80% (newer benchmark)
- **Overall Target:** ≥95% completeness

### 5.3 Validation Checks
- All required features present
- No systematic missing data patterns
- Feature standardization verified

---

## 6. Visualization Requirements

### 6.1 Required Figure (Gate Metric)
**Feature Completeness Comparison**
- Bar chart: Completeness % per benchmark
- Overall completeness across all combinations
- Target line at 95%

### 6.2 Additional Figures
1. **Feature Coverage Heatmap**
   - Rows: Models (20+)
   - Columns: Benchmarks (3)
   - Color: Feature completeness (0-100%)

2. **Feature Distribution Histograms**
   - Pass@k distributions
   - Runtime quartile distributions
   - Error type distributions

3. **Model-Benchmark Coverage Matrix**
   - Binary heatmap: complete vs incomplete
   - Annotate missing feature counts

**Output Location:** `h-e1/figures/`

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
transformers>=4.30.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
torch>=2.0.0  # for model loading if needed
```

### 7.2 External Resources
- HumanEval Official: https://github.com/openai/human-eval
- MBPP Official: https://github.com/google-research/google-research/tree/master/mbpp
- APPS Official: https://github.com/hendrycks/apps

### 7.3 Benchmark Papers
- Chen et al. (2021): "Evaluating Large Language Models Trained on Code"
- Austin et al. (2021): "Program Synthesis with Large Language Models"
- Hendrycks et al. (2021): "Measuring Coding Challenge Competence With APPS"

---

## 8. Risks and Mitigations

### Risk 1: Incomplete Published Results
**Impact:** May not reach 95% completeness target
**Mitigation:** Selective re-execution of open-source models to fill gaps

### Risk 2: Runtime Data Unavailable
**Impact:** Missing runtime quartile features
**Mitigation:** Focus on pass@k extraction (higher priority), runtime as secondary

### Risk 3: Benchmark API Changes
**Impact:** Dataset loading failures
**Mitigation:** Use stable HuggingFace dataset versions, fallback to direct downloads

---

## 9. Acceptance Criteria Summary

**Phase 3 → Phase 4 Handoff:**
- [ ] All 3 benchmark datasets accessible
- [ ] 20+ models identified with available results
- [ ] Feature extraction methodology defined
- [ ] Output schema specified
- [ ] Validation criteria established (≥95% completeness)

**Phase 4 Implementation Complete:**
- [ ] Feature extraction code implemented
- [ ] All features extracted for available model-benchmark pairs
- [ ] Feature completeness ≥ 95%
- [ ] Validation figures generated
- [ ] Results documented

---

## 10. Appendix

### A. Feature Extraction Pseudo-code
```python
class ExecutionTraceExtractor:
    def extract_passk(self, model_outputs, k_values=[1, 10, 100]):
        """Calculate pass@k using standard formula"""
        pass
    
    def extract_runtime_quartiles(self, passing_solutions):
        """Compute runtime distribution (25th, 50th, 75th percentile)"""
        pass
    
    def categorize_errors(self, failed_solutions):
        """Categorize errors: syntax, runtime, timeout"""
        pass
    
    def extract_all_features(self, model_name, benchmark_name, evaluation_results):
        """Extract complete feature vector for one model-benchmark pair"""
        return {
            "model": model_name,
            "benchmark": benchmark_name,
            "pass@1": ...,
            "pass@10": ...,
            "pass@100": ...,
            "runtime_q25": ...,
            "runtime_q50": ...,
            "runtime_q75": ...,
            "error_syntax": ...,
            "error_runtime": ...,
            "error_timeout": ...
        }
```

### B. Data Collection Protocol
1. Load benchmark datasets (HumanEval, MBPP, APPS)
2. Collect published pass@k scores from papers
3. For open-source models: execute on benchmarks to gather runtime/error data
4. Standardize features across benchmarks
5. Validate completeness (≥95% target)
6. Generate visualizations

---

**Document Status:** Draft for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)
