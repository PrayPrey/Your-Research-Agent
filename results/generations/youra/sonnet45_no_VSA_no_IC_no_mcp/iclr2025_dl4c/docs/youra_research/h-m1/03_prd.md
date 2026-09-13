# Product Requirements Document (PRD): h-m1

**Date:** 2026-08-25  
**Author:** Phase 3 Implementation Planning  
**Hypothesis:** h-m1 - MECHANISM hypothesis on specification completeness and test-intent capture  
**Source:** 02c_experiment_brief.md  

---

## Executive Summary

**Product Goal:** Validate the mechanism hypothesis that specification completeness determines test-intent capture gap through qualitative disagreement analysis across task types.

**Core Claim:** If task specifications are fully captured by tests (competitive programming), execution feedback captures human intent dimensions; if specifications are underspecified (realistic software), execution feedback misses critical intent dimensions only humans evaluate.

**Implementation Strategy:** Reuse h-e1 infrastructure (HumanEval/MBPP samples + feedback), extend with SWE-bench dataset loader, add disagreement extraction + qualitative coding framework, compare missed dimension rates by task type.

**Success Metrics:**
- SWE-bench missed dimension rate >2× HumanEval rate (effect size)
- Chi-square test p<0.05 (task type affects missed dimensions)
- Sufficient disagreement cases (>10 per dataset)

**Budget:** Tier 1 (~50 tasks)

---

## Problem Statement

### Research Context

**Prerequisite Hypothesis (h-e1):**
- Validated that execution-human correlation exists in code generation (HumanEval/MBPP)
- Correlation structure: exec-human r=0.68-0.71, ai-human r=0.45-0.52, exec-ai r=0.38-0.41
- Data: 50 samples each for HumanEval/MBPP with exec/ai/human feedback
- Missing: explanation of WHY correlations differ, data for realistic task type

**Current Gap:**
- h-e1 showed correlation structure exists but did NOT explain causal mechanism
- Need to test if specification completeness is the mechanism behind test-intent capture gap
- Need qualitative analysis to identify WHAT intent dimensions execution feedback misses

### Hypothesis Requirements

**MECHANISM Hypothesis:**
- Type: Qualitative validation of causal mechanism
- Gate: MUST_WORK (if mechanism invalid, PIVOT)
- Prerequisites: h-e1 COMPLETED (correlation structure validated)

**Research Question:**
Does specification completeness (fully-specified vs underspecified) determine whether execution feedback captures human intent dimensions?

**Experimental Approach:**
1. Compare three task types with varying specification completeness:
   - HumanEval: competitive programming (fully specified)
   - MBPP: basic programming (intermediate specification)
   - SWE-bench: realistic software (underspecified)
2. Extract disagreement cases (exec/human feedback mismatch)
3. Qualitative coding: identify missed intent dimensions per disagreement case
4. Statistical comparison: missed dimension rates by task type

---

## Scope

### In Scope

**Phase 4 Deliverables:**

1. **Data Infrastructure (Tier 1 - REUSE h-e1):**
   - Load h-e1 results (HumanEval/MBPP samples + exec/ai/human feedback)
   - SWE-bench dataset loader (100 samples from SWE-bench Lite)
   - Data format standardization across 3 datasets

2. **Code Generation (Tier 1 - REUSE h-e1):**
   - Reuse CodeGen-350M-mono model from h-e1
   - SWE-bench sample generation (100 new samples)
   - Inference pipeline for repo-level patches

3. **Feedback Collection (Tier 1 - EXTEND h-e1):**
   - Execution feedback: SWE-bench test harness integration
   - AI feedback: Reuse h-e1 reward model
   - Human feedback: Rating collection (simulated or MTurk) for SWE-bench

4. **Disagreement Analysis (Tier 1 - NEW):**
   - Extract disagreement cases (exec PASS/human LOW or exec FAIL/human HIGH)
   - Filter threshold: human rating difference >2 points (5-point scale)
   - Disagreement case export for qualitative coding

5. **Qualitative Coding Framework (Tier 1 - NEW):**
   - Intent dimension taxonomy (correctness, edge cases, readability, efficiency, maintainability, security)
   - Manual coding interface: load code sample + problem, assign missed dimensions
   - Coded results storage (JSON format)

6. **Statistical Comparison (Tier 1 - NEW):**
   - Missed dimension rate calculation per task type
   - Chi-square contingency test (task type × missed dimensions)
   - Effect size calculation (SWE-bench rate / HumanEval rate)
   - Bootstrap confidence intervals (95% CI)

7. **Visualization (Tier 1):**
   - Bar chart: % disagreement cases with missed dimensions per task type
   - Stacked bar chart: disagreement type distribution (exec_pass/human_low vs exec_fail/human_high)
   - Intent dimension heatmap (dimension × task type)
   - Qualitative examples table (9 examples: 3 per task type)

8. **Results Export:**
   - 04_validation.md report with statistical results + qualitative examples
   - CSV export: disagreement cases + coded dimensions
   - Figure files (PNG + PDF for paper)

### Out of Scope

**Not Implemented (YAGNI for MECHANISM hypothesis):**
- Model fine-tuning (frozen model only)
- Automated qualitative coding (manual coding only for PoC)
- Inter-coder reliability validation (single coder for PoC)
- Full SWE-bench evaluation (100 samples sufficient for qualitative analysis)
- Correlation pattern comparison (that's h-m2)
- Additional task types beyond HumanEval/MBPP/SWE-bench

**Deferred to Later Hypotheses:**
- Quantitative correlation pattern testing (h-m2)
- Causality validation experiments (h-m3)
- Intervention testing (h-m4)

---

## User Stories & Requirements

### Functional Requirements

**FR1: Data Loading**
- System MUST load h-e1 results (HumanEval/MBPP samples + feedback)
- System MUST download SWE-bench Lite dataset (100 samples)
- System MUST standardize data format across 3 datasets
- Data fields: sample_id, problem, code, exec_result, ai_score, human_rating, task_type

**FR2: Code Generation**
- System MUST reuse CodeGen-350M-mono model from h-e1
- System MUST generate code for 100 SWE-bench samples
- Generation parameters: same as h-e1 (temperature=0.8, max_tokens=512)

**FR3: Feedback Collection**
- System MUST collect execution feedback for SWE-bench samples (test harness)
- System MUST collect AI feedback scores (reuse h-e1 reward model)
- System MUST collect human ratings (5-point scale) for SWE-bench samples
- Human rating protocol: same as h-e1 (rating dimensions documented)

**FR4: Disagreement Extraction**
- System MUST identify disagreement cases per dataset:
  - exec PASS (exec=1) AND human LOW (<3/5)
  - exec FAIL (exec=0) AND human HIGH (>3/5)
- System MUST export disagreement cases with sample metadata
- Minimum requirement: >10 disagreement cases per dataset

**FR5: Qualitative Coding**
- System MUST provide manual coding interface (load sample → assign missed dimensions)
- Intent dimension taxonomy: correctness, edge cases, readability, efficiency, maintainability, security
- System MUST store coded results (sample_id → missed_dimensions list)
- Output format: JSON with fields [sample_id, task_type, missed_dimensions, disagreement_type]

**FR6: Statistical Analysis**
- System MUST calculate missed dimension rate per task type
- System MUST run chi-square contingency test (task_type × has_missed_dimensions)
- System MUST calculate effect size (SWE-bench rate / HumanEval rate)
- System MUST compute 95% confidence intervals (bootstrap with 1000 samples)

**FR7: Visualization**
- System MUST generate 4 figures:
  1. Missed dimension comparison bar chart (task type × % disagreement cases)
  2. Disagreement type distribution stacked bar chart
  3. Intent dimension heatmap (dimension × task type)
  4. Qualitative examples table (9 examples)
- Figures saved to `h-m1/figures/` in PNG + PDF formats
- Figure annotations: sample counts, p-values, effect size

**FR8: Results Export**
- System MUST generate 04_validation.md report with:
  - Statistical results (chi-square, effect size, CI)
  - Qualitative examples (3 per task type)
  - Gate success/failure decision (effect size >2×, p<0.05)
- System MUST export disagreement cases CSV (all fields)
- System MUST save coded results JSON

### Non-Functional Requirements

**NFR1: Reproducibility**
- All random sampling MUST use seed=42
- Dataset versions MUST be pinned (h-e1 data snapshot, SWE-bench Lite)
- Model checkpoint MUST be frozen (Salesforce/codegen-350M-mono)

**NFR2: Performance**
- Total runtime MUST be <6 hours (GPU: 1×A100 40GB)
- SWE-bench generation: ~2 hours (100 samples)
- Feedback collection: ~1 hour
- Qualitative coding: ~2-3 hours (manual analysis)

**NFR3: Storage**
- Total storage MUST be <10GB
- SWE-bench clones: ~5GB
- Generated patches + feedback: ~2GB
- Figures + results: <100MB

**NFR4: Error Handling**
- Generation failures (model errors): log and skip sample
- Test harness failures (SWE-bench): mark as exec FAIL
- Missing human ratings: exclude from analysis (warn if <90% coverage)

**NFR5: Code Quality**
- Reuse h-e1 code modules (generators, feedback collectors, loaders)
- Modular qualitative coding framework (extensible to new dimensions)
- Type hints + docstrings for all new functions
- Unit tests for disagreement extraction + statistical functions

---

## Technical Specifications

### System Architecture

**Components (extending h-e1 codebase):**

```
h-m1/code/
├── data/
│   ├── load_h_e1_results.py        # Load h-e1 HumanEval/MBPP data (REUSE)
│   ├── load_swebench.py            # SWE-bench Lite loader (NEW)
│   └── standardize_format.py       # Unify data schema across datasets (NEW)
├── generation/
│   ├── codegen_model.py            # REUSE h-e1 model wrapper
│   └── generate_swebench.py        # SWE-bench generation pipeline (NEW)
├── feedback/
│   ├── exec_feedback.py            # REUSE h-e1 executor + add SWE-bench harness
│   ├── ai_feedback.py              # REUSE h-e1 reward model
│   └── human_feedback.py           # REUSE h-e1 rating collection + extend for SWE-bench
├── analysis/
│   ├── extract_disagreements.py    # Disagreement case extraction (NEW)
│   ├── qualitative_coding.py       # Manual coding interface (NEW)
│   ├── statistical_tests.py        # Chi-square + effect size (NEW)
│   └── bootstrap_ci.py             # Bootstrap confidence intervals (NEW)
├── visualization/
│   ├── plot_missed_dimensions.py   # Bar chart (NEW)
│   ├── plot_disagreement_types.py  # Stacked bar chart (NEW)
│   ├── plot_heatmap.py             # Intent dimension heatmap (NEW)
│   └── export_examples_table.py    # Qualitative examples (NEW)
├── main.py                         # Full pipeline orchestrator (NEW)
└── config.yaml                     # Experiment configuration (NEW)
```

### Data Schemas

**1. Unified Sample Format (across HumanEval/MBPP/SWE-bench):**
```python
{
    "sample_id": str,           # e.g., "humaneval_001", "swebench_django_12345"
    "task_type": str,           # "HumanEval" | "MBPP" | "SWE-bench"
    "problem": str,             # Problem statement
    "code": str,                # Generated code
    "exec_result": int,         # 0 (fail) | 1 (pass)
    "ai_score": float,          # Reward model score (0-1)
    "human_rating": float,      # Human rating (1-5 scale)
    "gold_solution": str        # (optional) Gold patch/solution
}
```

**2. Disagreement Case Schema:**
```python
{
    "sample_id": str,
    "task_type": str,
    "exec_result": int,
    "human_rating": float,
    "disagreement_type": str,   # "exec_pass_human_low" | "exec_fail_human_high"
    "problem": str,
    "code": str
}
```

**3. Coded Result Schema:**
```python
{
    "sample_id": str,
    "task_type": str,
    "disagreement_type": str,
    "missed_dimensions": List[str],  # e.g., ["readability", "edge_cases", "maintainability"]
    "notes": str                     # Qualitative notes
}
```

**4. Statistical Results Schema:**
```python
{
    "by_task_type": {
        "HumanEval": {
            "total_disagreements": int,
            "missed_dimension_count": int,
            "missed_dimension_rate": float,
            "ci_95_lower": float,
            "ci_95_upper": float
        },
        "MBPP": {...},
        "SWE-bench": {...}
    },
    "chi_square": {
        "statistic": float,
        "p_value": float,
        "dof": int
    },
    "effect_size": {
        "swebench_humaneval_ratio": float,
        "swebench_mbpp_ratio": float
    },
    "gate_decision": {
        "effect_size_pass": bool,     # >2
        "chi_square_pass": bool,       # p<0.05
        "overall_pass": bool
    }
}
```

### Algorithms & Pseudo-code

**Key Algorithm 1: Disagreement Extraction**

```python
def extract_disagreements(samples: List[Sample], threshold: float = 2.0) -> List[Disagreement]:
    """
    Extract cases where exec/human feedback disagree.
    
    Disagreement definition:
    - Type A: exec PASS (=1) AND human LOW (<3/5)
    - Type B: exec FAIL (=0) AND human HIGH (>3/5)
    
    Args:
        samples: List of samples with exec_result + human_rating
        threshold: Human rating threshold (default: 3.0 on 5-point scale)
    
    Returns:
        List of disagreement cases
    """
    disagreements = []
    
    for sample in samples:
        exec_pass = sample.exec_result == 1
        human_low = sample.human_rating < threshold
        human_high = sample.human_rating > threshold
        
        if exec_pass and human_low:
            disagreements.append(Disagreement(
                sample_id=sample.sample_id,
                task_type=sample.task_type,
                disagreement_type="exec_pass_human_low",
                exec_result=1,
                human_rating=sample.human_rating,
                problem=sample.problem,
                code=sample.code
            ))
        elif not exec_pass and human_high:
            disagreements.append(Disagreement(
                sample_id=sample.sample_id,
                task_type=sample.task_type,
                disagreement_type="exec_fail_human_high",
                exec_result=0,
                human_rating=sample.human_rating,
                problem=sample.problem,
                code=sample.code
            ))
    
    return disagreements
```

**Key Algorithm 2: Chi-Square Contingency Test**

```python
def compute_chi_square(coded_results: List[CodedResult]) -> ChiSquareResult:
    """
    Test if missed dimension rates differ by task type.
    
    Contingency table:
                    | Has Missed Dimensions | No Missed Dimensions |
    HumanEval       |        a              |         b            |
    MBPP            |        c              |         d            |
    SWE-bench       |        e              |         f            |
    
    Returns:
        Chi-square statistic, p-value, degrees of freedom
    """
    # Build contingency table
    task_types = ["HumanEval", "MBPP", "SWE-bench"]
    table = []
    
    for task_type in task_types:
        task_results = [r for r in coded_results if r.task_type == task_type]
        has_missed = sum(1 for r in task_results if len(r.missed_dimensions) > 0)
        no_missed = len(task_results) - has_missed
        table.append([has_missed, no_missed])
    
    # Chi-square test
    chi2, p_value, dof, expected = scipy.stats.chi2_contingency(table)
    
    return ChiSquareResult(
        statistic=chi2,
        p_value=p_value,
        dof=dof,
        observed=table,
        expected=expected
    )
```

**Key Algorithm 3: Bootstrap Confidence Intervals**

```python
def bootstrap_ci(coded_results: List[CodedResult], task_type: str, n_bootstrap: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
    """
    Compute 95% CI for missed dimension rate via bootstrap.
    
    Args:
        coded_results: Coded disagreement cases
        task_type: "HumanEval" | "MBPP" | "SWE-bench"
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level (default: 0.05 for 95% CI)
    
    Returns:
        (lower_bound, upper_bound) of CI
    """
    task_results = [r for r in coded_results if r.task_type == task_type]
    n = len(task_results)
    
    rates = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        bootstrap_sample = np.random.choice(task_results, size=n, replace=True)
        missed_count = sum(1 for r in bootstrap_sample if len(r.missed_dimensions) > 0)
        rate = missed_count / n
        rates.append(rate)
    
    # Percentile method
    lower = np.percentile(rates, alpha / 2 * 100)
    upper = np.percentile(rates, (1 - alpha / 2) * 100)
    
    return lower, upper
```

### Dependencies & Environment

**Python Version:** 3.10+

**Core Dependencies (extend h-e1 environment):**
```
# Model & Data
transformers==4.36.0
datasets==2.16.0
torch==2.1.0

# Feedback Collection
# (SWE-bench harness via Docker - installed separately)

# Analysis
pandas==2.1.4
numpy==1.26.2
scipy==1.11.4

# Visualization
matplotlib==3.8.2
seaborn==0.13.0

# Utilities
pyyaml==6.0.1
tqdm==4.66.1
```

**Hardware Requirements:**
- GPU: 1× A100 40GB (for SWE-bench generation)
- RAM: 64GB
- Storage: 10GB (SWE-bench clones + results)

**SWE-bench Test Harness:**
- Docker containers for repository-specific test execution
- Installation: `docker pull princeton-nlp/swe-bench:latest`
- Execution: `swebench.harness.test_spec.make_test_spec()` API

---

## Success Metrics

### Primary Metrics (Gate Success)

**M1: Effect Size (SWE-bench vs HumanEval)**
- **Definition:** Ratio of missed dimension rates (SWE-bench / HumanEval)
- **Target:** >2× (SWE-bench rate >2× HumanEval rate)
- **Rationale:** Mechanism predicts realistic tasks miss significantly more dimensions
- **Gate:** MUST_WORK - if <2×, PIVOT (mechanism invalid)

**M2: Chi-Square Statistical Significance**
- **Definition:** Chi-square contingency test p-value (task type × missed dimensions)
- **Target:** p < 0.05
- **Rationale:** Task type must significantly affect missed dimension rates
- **Gate:** MUST_WORK - if p≥0.05, PIVOT (task type doesn't matter)

### Secondary Metrics (Quality Check)

**M3: Disagreement Case Coverage**
- **Definition:** Number of disagreement cases per dataset
- **Target:** >10 per dataset (HumanEval, MBPP, SWE-bench)
- **Rationale:** Insufficient cases → qualitative analysis unreliable

**M4: Missed Dimension Rate Ranking**
- **Definition:** Ordering of missed dimension rates by task type
- **Target:** SWE-bench > MBPP > HumanEval
- **Rationale:** Specification completeness should rank: competitive > basic > realistic

**M5: Qualitative Example Diversity**
- **Definition:** Number of distinct intent dimensions observed across examples
- **Target:** ≥4 dimensions (out of 6 taxonomy dimensions)
- **Rationale:** Ensures missed dimensions are diverse, not clustered in one category

### Experiment Validation Metrics

**EV1: Data Integrity**
- h-e1 data loaded: 100 samples (50 HumanEval + 50 MBPP) with feedback
- SWE-bench generated: 100 samples with exec/ai/human feedback
- No missing feedback: <10% samples excluded

**EV2: Computational Budget**
- Runtime: <6 hours (target: 4-6 hours)
- GPU memory: <40GB peak
- Storage: <10GB total

**EV3: Code Reuse**
- h-e1 code reused: ≥70% of codebase (generators, feedback collectors, loaders)
- New code: <30% (disagreement analysis, qualitative coding, statistical tests)

---

## Open Questions & Risks

### Open Questions

**Q1: Human Rating Collection for SWE-bench**
- **Question:** Simulated ratings (LLM-as-judge) or MTurk crowdsourcing?
- **Options:**
  - Simulated: faster, cheaper, but may not capture true human judgment
  - MTurk: more realistic, but expensive (~$5/sample × 100 = $500) and time-consuming
- **Decision:** Start with simulated ratings for PoC, note limitation in 04_validation.md
- **Risk Mitigation:** If simulated ratings show weak disagreement signal, re-run with MTurk

**Q2: SWE-bench Test Harness Complexity**
- **Question:** Can we reliably run SWE-bench tests in 2 hours (100 samples)?
- **Context:** SWE-bench uses Docker containers with repo-specific test harnesses
- **Risk:** Docker setup/teardown overhead may exceed budget
- **Mitigation:** Use SWE-bench Lite (smaller repos), parallel Docker execution (4× containers)

**Q3: Qualitative Coding Time**
- **Question:** Can manual coding finish in 2-3 hours (~30-50 disagreement cases)?
- **Context:** Each case requires reading code + problem, assigning dimensions
- **Risk:** Underestimated complexity (repo-level SWE-bench code may be long)
- **Mitigation:** Pre-filter to shortest code samples (<50 lines), prioritize clear cases

### Risks & Mitigation

**R1: Insufficient Disagreement Cases**
- **Risk:** <10 disagreement cases per dataset → qualitative analysis underpowered
- **Likelihood:** Medium (h-e1 showed r=0.68-0.71 exec-human, few extreme disagreements)
- **Mitigation:** Lower disagreement threshold to 1.5 points (instead of 2.0) to capture more cases
- **Fallback:** If still insufficient, increase SWE-bench sample size to 200

**R2: SWE-bench Generation Failures**
- **Risk:** CodeGen-350M may fail on repo-level tasks (model designed for function-level)
- **Likelihood:** High (SWE-bench pass@1 <5% for small models)
- **Mitigation:** Accept low pass rate, focus on disagreement analysis (not absolute performance)
- **Impact:** High failure rate → more exec FAIL cases, but still analyzable

**R3: Null Result (Effect Size <2×)**
- **Risk:** SWE-bench and HumanEval show similar missed dimension rates → mechanism invalid
- **Likelihood:** Low (specification completeness is well-established in software engineering)
- **Mitigation:** PIVOT per MUST_WORK gate (documented in verification_state.yaml)
- **Fallback:** Investigate alternative mechanisms (h-e1 correlation patterns suggest mechanism exists)

**R4: Chi-Square Non-Significance (p≥0.05)**
- **Risk:** Missed dimension rates don't differ statistically by task type
- **Likelihood:** Low (sample size = 200, expected effect size large)
- **Mitigation:** Check power analysis, potentially increase sample size
- **Impact:** PIVOT per gate (mechanism not validated)

**R5: Code Reuse Failures**
- **Risk:** h-e1 codebase not compatible with SWE-bench data format
- **Likelihood:** Low (both use standard Python code generation pipeline)
- **Mitigation:** Standardize data schema early (data/standardize_format.py), adapt h-e1 code minimally
- **Impact:** Increased implementation time, but doesn't invalidate hypothesis

---

## Timeline & Milestones

**Phase 4 Implementation Timeline (Target: 1 week):**

| Day | Milestone | Deliverable |
|-----|-----------|-------------|
| 1 | Environment setup + h-e1 data loading | Load h-e1 results, verify 100 samples |
| 2 | SWE-bench infrastructure | Download SWE-bench Lite, Docker harness setup |
| 3 | SWE-bench generation (4 hours compute) | 100 generated patches |
| 4 | Feedback collection (SWE-bench exec/ai/human) | 100 samples with feedback |
| 5 | Disagreement extraction + qualitative coding | Coded disagreement cases (JSON) |
| 6 | Statistical analysis + visualization | Figures + statistical results |
| 7 | 04_validation.md report + review | Final validation report, gate decision |

**Critical Path:**
- SWE-bench generation (longest runtime: ~4 hours)
- Qualitative coding (manual work: 2-3 hours, not parallelizable)
- Docker harness setup (potential blocker if complex)

**Parallelizable Work:**
- Feedback collection (exec/ai can run in parallel)
- Figure generation (all 4 figures independent)

---

## Appendix

### Glossary

- **Disagreement Case:** Sample where execution feedback and human rating disagree (exec PASS/human LOW or exec FAIL/human HIGH)
- **Intent Dimension:** Aspect of code quality humans evaluate (correctness, edge cases, readability, efficiency, maintainability, security)
- **Missed Dimension:** Intent dimension NOT captured by execution feedback in a disagreement case
- **Specification Completeness:** Degree to which task tests encode all human intent requirements
- **Effect Size:** Ratio of missed dimension rates (SWE-bench / HumanEval), target >2×

### References

1. **h-e1 Validation Report:** `/h-e1/04_validation.md`
2. **SWE-bench Paper:** Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (2023)
3. **HumanEval:** Chen et al., "Evaluating Large Language Models Trained on Code" (2021)
4. **MBPP:** Austin et al., "Program Synthesis with Large Language Models" (2021)
5. **Qualitative Coding:** Saldaña, "The Coding Manual for Qualitative Researchers" (2015)
6. **Chi-Square Test:** Agresti, "Categorical Data Analysis" (2002)

### Contact & Escalation

- **Phase 3 Author:** Architecture/Logic/Config agents (parallel)
- **Phase 4 Implementer:** Coder agent (to be assigned)
- **Gate Decision Authority:** Verification workflow (verification_state.yaml)
- **Escalation:** If PIVOT triggered, return to Phase 2A for alternative hypotheses
