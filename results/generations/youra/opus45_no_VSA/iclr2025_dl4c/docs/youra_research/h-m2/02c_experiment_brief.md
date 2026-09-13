# Experiment Design: H-M2

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** DiD contrast [(A-C)_RL - (A-C)_CE] > 0 for semantic feedback sensitivity
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests whether RL training induces greater sensitivity to semantic content of feedback.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
DiD contrast [(A-C)_RL - (A-C)_CE] > 0 where:
- A = Actual feedback (real execution error messages)
- C = Control feedback (shuffled/random error messages)
- Positive contrast = RL model leverages semantic feedback content more than CE model

---

## Continuation Context

### Previous Hypothesis Results
**H-E1 PASS:** Confirmed superadditive interaction (Training×Refinement > 0).
- RL-Refine outperformed expectation from additive model
- Mechanism: RL training may induce feedback-conditioned edit policy

**Implication for H-M2:** Now test whether the mechanism is semantic sensitivity to feedback content.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for DiD in code generation. Key insight from perturbation guidance literature:
- Perturbations must preserve executability while disrupting semantics
- Control condition must match surface statistics (length, format)

### Exa GitHub Implementations

**Repository 1**: [amazon-science/recode](https://github.com/amazon-science/recode) (⭐ 58)
- **Relevance**: Robustness evaluation with 30+ perturbations on docstrings/code
- **Key Insight**: Semantic vs syntactic perturbation taxonomy
- **Usage**: Perturbation operators for controlled experiments

**Repository 2**: [CUHK-ARISE/CodeCrash](https://github.com/cuhk-arise/codecrash) (⭐ 17)
- **Relevance**: Perturbations exposing LLM sensitivity to misleading cues
- **Key Insight**: Structural perturbations (renaming, reformatting) vs semantic
- **Usage**: GBC (garbage code), PSC (misleading comments) operators

**Repository 3**: [ttrangnguyen/EMPICA](https://github.com/ttrangnguyen/EMPICA)
- **Relevance**: Evaluating code LLM understanding via transformations
- **Key Insight**: "Robust to equivalent, sensitive to non-equivalent" framework
- **Usage**: Semantic equivalence/non-equivalence transformation operators

**Repository 4**: [igerber/diff-diff](https://github.com/igerber/diff-diff) (⭐ 367)
- **Relevance**: Python DiD library with sklearn API
- **Key Insight**: Callaway-Sant'Anna estimators, sensitivity analysis
- **Usage**: Statistical framework for DiD contrast estimation

### Key Paper References

1. **ReCode** (ICLR 2023) - Robustness Evaluation of Code Generation
   - 30+ perturbations, semantic vs syntactic taxonomy
   
2. **CodeCrash** (NeurIPS 2025) - Exposing LLM Fragility
   - Controlled distractions, failure mode analysis

3. **EMPICA** (FSE 2024) - Code LLM Semantic Understanding
   - Transformation-based evaluation framework

---

## Experiment Specification

### Core Design: Difference-in-Differences

**Treatment Groups:**
- RL-trained model (from H-E1)
- CE-trained model (from H-E1)

**Feedback Conditions:**
- **A (Actual):** Real execution feedback from failed test runs
- **C (Control):** Shuffled feedback (matched length/format, wrong problem)

**DiD Contrast:**
```
DiD = (pass@1_RL_Actual - pass@1_RL_Control) - (pass@1_CE_Actual - pass@1_CE_Control)
```

If DiD > 0: RL model extracts more signal from semantic feedback content.

### Dataset

**Primary Dataset**: HumanEval+ (164 problems)
- **Type**: standard
- **Source**: evalplus/evalplus
- **Usage**: Same problems as H-E1 for comparability

**Perturbation Design:**
- For each problem with failing initial generation
- A condition: Provide actual execution feedback
- C condition: Provide feedback from different problem (matched format)

**Sample Size:**
- All 164 HumanEval+ problems
- Expect ~50-70% fail on single-shot (require refinement)
- Minimum 80 problems per condition for statistical power

**Loading Information:**
```python
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()

def get_control_feedback(problem_id, all_feedbacks):
    """Return feedback from a different problem, matched by error type."""
    actual_feedback = all_feedbacks[problem_id]
    # Select feedback from different problem with same error category
    candidates = [f for pid, f in all_feedbacks.items() 
                  if pid != problem_id and same_error_type(f, actual_feedback)]
    return random.choice(candidates) if candidates else shuffle_tokens(actual_feedback)
```

### Models

#### Models Under Test (from H-E1)

**RL-Trained Model:** CodeT5+-220M + RL fine-tuning
- Checkpoint from H-E1 RL training
- Expected: Higher sensitivity to feedback semantics

**CE-Trained Model:** CodeT5+-220M + CE fine-tuning
- Checkpoint from H-E1 CE training
- Expected: Lower sensitivity (treats feedback as generic signal)

**Loading Information:**
```python
# Load H-E1 trained checkpoints
rl_model = AutoModelForSeq2SeqLM.from_pretrained("./h-e1/checkpoints/rl_model")
ce_model = AutoModelForSeq2SeqLM.from_pretrained("./h-e1/checkpoints/ce_model")
```

### Feedback Perturbation Protocol

**Actual Feedback (A):**
```python
def get_actual_feedback(code: str, tests: List[str]) -> str:
    """Execute code and return real error message."""
    result = execute_code_with_tests(code, tests)
    if result.passed:
        return "All tests passed"
    return f"Error on test {result.failed_test}: {result.error_message}"
```

**Control Feedback (C):**
```python
def get_control_feedback(code: str, problem_id: str, feedback_bank: Dict) -> str:
    """Return feedback from different problem (semantic shuffle)."""
    # Get feedback from a different problem
    other_problems = [p for p in feedback_bank if p != problem_id]
    donor_problem = random.choice(other_problems)
    return feedback_bank[donor_problem]
```

**Matching Criteria for Control:**
1. Same error category (AssertionError, TypeError, etc.)
2. Similar length (±20%)
3. Different semantic content (wrong variable names, wrong expected values)

### Evaluation Protocol

**Per-Model, Per-Condition Evaluation:**
```python
def evaluate_condition(model, problems, feedback_fn, condition_name):
    results = []
    for problem in problems:
        # Single-shot generation
        code = model.generate(problem.prompt)
        single_shot_pass = execute_and_check(code, problem.tests)
        
        if not single_shot_pass:
            # Get feedback (actual or control)
            feedback = feedback_fn(code, problem)
            
            # Refinement with feedback
            refine_prompt = f"{problem.prompt}\n\nPrevious:\n{code}\n\nFeedback:\n{feedback}\n\nRefined:"
            refined_code = model.generate(refine_prompt)
            refined_pass = execute_and_check(refined_code, problem.tests)
        else:
            refined_pass = True
        
        results.append({
            "problem_id": problem.id,
            "condition": condition_name,
            "single_shot_pass": single_shot_pass,
            "refined_pass": refined_pass
        })
    return results
```

**DiD Computation:**
```python
def compute_did_contrast(results):
    """Compute DiD contrast for semantic sensitivity."""
    # Group by model and condition
    rl_actual = mean([r["refined_pass"] for r in results if r["model"]=="RL" and r["condition"]=="actual"])
    rl_control = mean([r["refined_pass"] for r in results if r["model"]=="RL" and r["condition"]=="control"])
    ce_actual = mean([r["refined_pass"] for r in results if r["model"]=="CE" and r["condition"]=="actual"])
    ce_control = mean([r["refined_pass"] for r in results if r["model"]=="CE" and r["condition"]=="control"])
    
    did_contrast = (rl_actual - rl_control) - (ce_actual - ce_control)
    return did_contrast
```

### Statistical Analysis

**Primary Test:** DiD contrast > 0
- Null hypothesis: DiD ≤ 0 (RL no more sensitive than CE)
- Alternative: DiD > 0 (RL more sensitive to semantic feedback)
- Test: Bootstrap confidence interval on DiD contrast

**Implementation:**
```python
from scipy import stats

def bootstrap_did_ci(results, n_bootstrap=1000, alpha=0.05):
    """Bootstrap confidence interval for DiD contrast."""
    did_samples = []
    for _ in range(n_bootstrap):
        boot_results = resample(results, replace=True)
        did_samples.append(compute_did_contrast(boot_results))
    
    ci_lower = np.percentile(did_samples, 100 * alpha / 2)
    ci_upper = np.percentile(did_samples, 100 * (1 - alpha / 2))
    did_point = compute_did_contrast(results)
    
    return {
        "did_contrast": did_point,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "significant": ci_lower > 0  # One-sided: entire CI > 0
    }
```

**Success Criteria (Gate):**
- DiD > 0 (point estimate)
- 95% CI lower bound > 0 preferred, but SHOULD_WORK gate tolerates p < 0.10

### Training Protocol

**No Additional Training Required**
- Uses checkpoints from H-E1
- Evaluation-only experiment

### Evaluation Configuration

- **Seeds:** 3 (for bootstrap stability)
- **Refinement iterations:** K=1 (single refinement step to isolate feedback effect)
- **Temperature:** 0 (greedy decoding)
- **Max tokens:** 512

### Visualization Requirements

#### Required Figures (Mandatory)

1. **DiD Bar Chart:** 2×2 grouped bar (Model × Feedback condition)
   - Y-axis: pass@1 after refinement
   - Groups: RL, CE
   - Bars: Actual, Control

2. **DiD Contrast with CI:** Single bar with error bars
   - Point estimate and 95% bootstrap CI
   - Reference line at 0

#### Additional Figures

3. **Per-Error-Type DiD:** Breakdown by error category (if sample size permits)
4. **Effect Size Distribution:** Histogram of per-problem RL-CE differences

---

## Success Check

**SHOULD_WORK Gate Pass Condition:**
1. Code runs without error (all 4 conditions evaluate successfully)
2. DiD contrast > 0 (point estimate)
3. Preferable: 95% CI excludes 0

**Mechanism Verification:**
- Pre-condition: Both models receive identical feedback format
- Activation indicator: RL model shows larger Actual-Control gap than CE
- Metric: DiD contrast magnitude

**Failure Modes:**
- DiD ≤ 0: RL not more sensitive (mechanism not confirmed)
- Large variance: Insufficient sample size for detection

---

## Appendix: Reference Implementations

### Primary References

1. **ReCode** (ICLR 2023)
   - Paper: https://arxiv.org/abs/2212.10264
   - Code: https://github.com/amazon-science/recode
   - Key: Perturbation taxonomy for robustness evaluation

2. **diff-diff** (Python DiD library)
   - Code: https://github.com/igerber/diff-diff
   - Key: Callaway-Sant'Anna estimators, sklearn API

3. **EMPICA** (FSE 2024)
   - Code: https://github.com/ttrangnguyen/EMPICA
   - Key: Semantic equivalence transformation framework

4. **CodeCrash** (NeurIPS 2025)
   - Code: https://github.com/cuhk-arise/codecrash
   - Key: Controlled perturbation operators

### Code Snippets

**Feedback Shuffling (from ReCode pattern):**
```python
def shuffle_feedback_semantic(feedback: str, seed: int = 42) -> str:
    """Shuffle semantic content while preserving format."""
    random.seed(seed)
    # Parse error structure
    lines = feedback.split('\n')
    # Shuffle variable names, expected values
    for i, line in enumerate(lines):
        if 'Expected:' in line or 'Got:' in line:
            # Swap with another line's value
            lines[i] = swap_values_with_donor(line)
    return '\n'.join(lines)
```

**Bootstrap DiD (from diff-diff pattern):**
```python
from sklearn.utils import resample

def bootstrap_test(data, statistic_fn, n_boot=1000):
    stats = [statistic_fn(resample(data)) for _ in range(n_boot)]
    return np.mean(stats), np.percentile(stats, [2.5, 97.5])
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design started
- 2026-08-08: Research completed (Archon, Exa: ReCode, EMPICA, diff-diff)
- 2026-08-08: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
