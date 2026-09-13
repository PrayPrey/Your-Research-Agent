# Experiment Design: H-M2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Section structure itself matters: structured format outperforms scrambled format (same content, random section order) with p < 0.05, indicating that representational alignment rather than information content alone drives improvement
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing representational alignment mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** SHOULD_WORK (pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
Structured format achieves higher repair success rate than Scrambled format with p < 0.05, controlling for identical information content.

---

## Continuation Context

Building on H-M1 validation which confirmed information preservation across format transformations. H-M2 tests whether the STRUCTURE of the format (section ordering) causally affects repair success, isolating representational alignment from pure information content.

### Previous Hypothesis Results
- **H-E1 VALIDATED:** Structured error format improves repair success over raw compiler output
- **H-M1 VALIDATED:** Information content preserved across format transformations (reconstruction accuracy >95%)

### Research Gap
This is the CRITICAL mechanistic test: if Structured = Scrambled performance, then information content alone drives improvement. If Structured > Scrambled, then representational alignment (how information is organized) is the causal mechanism.

---

## Implementation Research Summary

### Web Search Findings

**Self-Repair Literature (2024-2026):**
- ICLR 2024 self-repair paper (theoxo/self-repair) provides baseline framework
- Iterative self-repair yields +4.9% minimum improvement across models
- Chain-of-thought repair prompting yields gains comparable to 1-2 additional repair rounds
- Format structure impacts LLM reasoning by 10-15% in constrained settings

**Statistical Methodology:**
- Paired bootstrap testing standard for LLM ablation studies
- Wilcoxon signed-rank test with Bonferroni-Holm correction for multiple comparisons
- BCa bootstrap with 10,000 replicas for 95% confidence intervals

**Order Sensitivity in LLMs:**
- LLMs sensitive to option order in MCQ tasks (RoToR paper, Feb 2025)
- Shuffling experiments standard for isolating format vs content effects

### EvalPlus Framework
- HumanEval+ provides 80x more test cases than original HumanEval
- Standard benchmark for code generation evaluation
- EvalPlus v0.3.1 (Oct 2024) includes code efficiency evaluation

### Implementation Reference
- GitHub: theoxo/self-repair (ICLR 2024 framework)
- GitHub: evalplus/evalplus (benchmark infrastructure)
- Existing H-E1/H-M1 infrastructure for error formatting

---

## Experiment Specification

### Dataset

**Dataset:** EvalPlus (HumanEval+ and MBPP+)
**Type:** standard (established benchmark)
**Source:** https://github.com/evalplus/evalplus

| Attribute | Value |
|-----------|-------|
| Name | EvalPlus (HumanEval+ & MBPP+) |
| Size | HumanEval+: 164 problems, MBPP+: 378 problems |
| Test Cases | 80x more than original benchmarks |
| Evaluation Samples | 500+ failed code samples with errors |
| Splits | Full test set evaluation |
| Format | Code generation tasks with ground truth |

**Loading Information** (for Phase 4 download):
- Method: pip install evalplus
- Identifier: `evalplus/evalplus`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

# Load HumanEval+
humaneval_problems = get_human_eval_plus()

# Load MBPP+
mbpp_problems = get_mbpp_plus()
```

**Error Collection Protocol:**
1. Generate code with base model (CodeLlama-7B) on full benchmark
2. Collect all failures that produce static analysis errors
3. Filter to errors that have structured format representation
4. Minimum 500 error samples across error types

### Models

#### Base Model (Code Generator)

**Architecture:** CodeLlama-7B-Instruct
**Purpose:** Generate initial code and repair attempts

**Loading Information:**
- Method: HuggingFace Transformers or vLLM
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "codellama/CodeLlama-7b-Instruct-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
```

**Configuration:**
- Temperature: 0.8 (same as self-repair paper)
- Top-p: 0.95
- Max tokens: 512
- Repair iterations: 1 (single-turn comparison)

#### Self-Repair Framework

**Framework:** theoxo/self-repair (ICLR 2024)
**Adaptation:** Modify error format injection only

**Key Modification:**
```python
# Original: raw compiler output in prompt
# Condition A (Structured): Ordered sections [PROBLEM/LOCATION/CONTEXT/ROOT_CAUSE]
# Condition B (Scrambled): Same sections, random order per sample
```

### Experimental Conditions

#### Condition A: Structured Format
```
## PROBLEM
[Error type and brief description]

## LOCATION
[File, line, column information]

## CONTEXT
[Surrounding code snippet]

## ROOT CAUSE
[Analysis of what went wrong]
```

#### Condition B: Scrambled Format (Control)
Same four sections with IDENTICAL content, but section order randomly permuted per sample.

**Scrambling Protocol:**
```python
import random

def scramble_sections(structured_error: str, seed: int) -> str:
    """Randomly permute section order while preserving content."""
    sections = parse_sections(structured_error)  # Returns list of (header, content)
    random.seed(seed)  # Reproducible scrambling
    random.shuffle(sections)
    return format_sections(sections)
```

**Why Scrambling Works as Control:**
- Information content IDENTICAL between conditions
- Section headers preserved (no information loss)
- Only difference is ordering/structure
- Isolates representational alignment from pure information

### Training Protocol

**N/A** - This is an evaluation-only experiment (no training required)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Training | None | Comparison study only |
| Repair iterations | 1 | Single-turn isolates format effect |
| Temperature | 0.8 | Match self-repair paper |
| Seeds | 5 | Statistical robustness |
| Scramble seeds | Per-sample | Varied random orderings |

### Evaluation

**Primary Metric:** Repair Success Rate (pass@1)

| Metric | Definition | Target |
|--------|------------|--------|
| Repair Success Rate | % of failed samples successfully repaired | Higher for Structured |
| Effect Size | Cohen's d between conditions | d > 0.2 (small effect) |
| Statistical Significance | p-value from paired test | p < 0.05 |

**Statistical Analysis Protocol:**

```python
import numpy as np
from scipy import stats

def analyze_structure_effect(structured_results, scrambled_results):
    """
    Paired comparison: same samples, different format conditions.
    """
    n = len(structured_results)
    assert n == len(scrambled_results), "Must have paired samples"
    assert n >= 500, "Minimum 500 samples for statistical power"
    
    # Convert to binary success (1/0)
    structured_success = np.array([1 if r['passed'] else 0 for r in structured_results])
    scrambled_success = np.array([1 if r['passed'] else 0 for r in scrambled_results])
    
    # Primary metric: success rate difference
    structured_rate = structured_success.mean()
    scrambled_rate = scrambled_success.mean()
    delta = structured_rate - scrambled_rate
    
    # McNemar's test for paired binary outcomes
    # Contingency table for discordant pairs
    b = ((structured_success == 1) & (scrambled_success == 0)).sum()  # Structured wins
    c = ((structured_success == 0) & (scrambled_success == 1)).sum()  # Scrambled wins
    
    if b + c > 0:
        # McNemar's chi-squared
        chi2 = (abs(b - c) - 1) ** 2 / (b + c)
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
    else:
        p_value = 1.0  # No discordant pairs
    
    # Bootstrap confidence interval for effect size
    bootstrap_deltas = []
    for _ in range(10000):
        idx = np.random.choice(n, n, replace=True)
        boot_delta = structured_success[idx].mean() - scrambled_success[idx].mean()
        bootstrap_deltas.append(boot_delta)
    ci_lower, ci_upper = np.percentile(bootstrap_deltas, [2.5, 97.5])
    
    return {
        'structured_rate': structured_rate,
        'scrambled_rate': scrambled_rate,
        'delta': delta,
        'p_value': p_value,
        'ci_95': (ci_lower, ci_upper),
        'discordant_structured_wins': b,
        'discordant_scrambled_wins': c,
        'gate_pass': p_value < 0.05 and delta > 0
    }
```

**Success Criteria:**
- Structured success rate > Scrambled success rate
- p < 0.05 (McNemar's test for paired binary outcomes)
- 95% bootstrap CI excludes zero

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Side-by-side bar chart of Structured vs Scrambled repair success rates with error bars (95% CI)

#### Additional Figures (LLM Autonomous)
- Success rate by error type (syntax vs runtime vs type errors)
- Discordant pair analysis (Venn diagram of wins)
- Effect size distribution from bootstrap
- Learning curve: effect size vs sample size

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True - Representational alignment hypothesis
- `mechanism_isolatable`: True - Scrambled control isolates structure from content
- `baseline_measurable`: True - Scrambled format provides content-matched baseline

### Architecture Compatibility
- H-E1/H-M1 StructuredError format validated
- Section parsing and scrambling straightforward
- Self-repair framework (theoxo/self-repair) provides evaluation harness

### Activation Indicators
- `mechanism_log_message`: "Running structure vs scrambled comparison with {n} samples"
- `metric_delta_expected`: Positive delta if representational alignment matters

### Mechanism Verification Code
```python
def verify_representational_alignment(results):
    """Verify the structure vs scrambled comparison."""
    assert 'structured_rate' in results, "Missing structured rate"
    assert 'scrambled_rate' in results, "Missing scrambled rate"
    assert 'p_value' in results, "Missing p-value"
    
    if results['gate_pass']:
        print(f"✅ GATE PASS: Structured ({results['structured_rate']:.1%}) > "
              f"Scrambled ({results['scrambled_rate']:.1%}), p={results['p_value']:.4f}")
        print("   Representational alignment confirmed as causal mechanism")
        return True
    else:
        if results['delta'] <= 0:
            print(f"❌ GATE FAIL: Structured ({results['structured_rate']:.1%}) <= "
                  f"Scrambled ({results['scrambled_rate']:.1%})")
            print("   Information content alone drives effect, not structure")
        else:
            print(f"⚠️ GATE FAIL: Trend positive but not significant (p={results['p_value']:.4f})")
        return False
```

### Success Criteria
- `hypothesis_support_threshold`: p < 0.05
- `hypothesis_support_metric`: gate_pass
- `effect_direction`: structured_rate > scrambled_rate

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on full EvalPlus test set
2. Minimum 500 paired samples evaluated
3. Statistical analysis completed
4. Structured > Scrambled with p < 0.05

**Gate Result Interpretation:**
- PASS: Structure matters → Representational alignment is the mechanism
- FAIL (no difference): Information content alone sufficient → Revise theoretical model
- FAIL (scrambled better): Unexpected result → Investigate potential confounds

---

## Computational Requirements

| Resource | Estimate | Notes |
|----------|----------|-------|
| GPU | 1x A100 40GB | CodeLlama-7B inference |
| Time | ~4-6 hours | 500+ samples × 2 conditions × inference |
| Storage | ~10GB | Model weights + results |
| API Calls | 0 | All local inference |

**Efficiency Notes:**
- Batch inference for throughput
- Cache base model predictions
- Parallelize across conditions

---

## Appendix: Reference Implementations

### Primary Reference
- **theoxo/self-repair (ICLR 2024)**
  - Source: https://github.com/theoxo/self-repair
  - Components: Self-repair evaluation framework
  - Adaptation: Modify error format injection point

### EvalPlus Framework
- **evalplus/evalplus**
  - Source: https://github.com/evalplus/evalplus
  - Components: HumanEval+, MBPP+ datasets and evaluation
  - Version: v0.3.1 (Oct 2024)

### Statistical Methods
- McNemar's test for paired binary outcomes
- Bootstrap confidence intervals (BCa method, 10,000 replicas)
- Cohen's d for effect size interpretation

### Related Papers
- "Is Self-Repair a Silver Bullet?" (ICLR 2024) - Baseline framework
- "How Many Tries Does It Take?" (arXiv:2604.10508) - Extended analysis
- "RoToR: Order-Invariant Inputs" (arXiv:2502.08662) - Order sensitivity in LLMs

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- H-E1 completed and VALIDATED (2026-08-28)
- H-M1 completed and VALIDATED (2026-08-28)
- H-M2 experiment design COMPLETED

---

*Research Sources:*
- [Self-Repair ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/9ddc141bdbf9d1db510cefff56c586ad-Paper-Conference.pdf)
- [Iterative Self-Repair Study](https://arxiv.org/html/2604.10508v1)
- [EvalPlus Benchmarks](https://evalplus.github.io/)
- [A/B Testing LLM Prompts](https://futureagi.com/blog/ab-testing-llm-prompts-best-practices-2026/)

*Next Phase: Phase 3 - Implementation Planning*
