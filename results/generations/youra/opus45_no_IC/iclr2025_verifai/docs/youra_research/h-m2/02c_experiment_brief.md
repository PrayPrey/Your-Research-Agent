# Experiment Design: H-M2

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Static analysis identifies semantic patterns (security, reliability) in syntactically valid code, reducing issues after feedback
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** SHOULD_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Grammar constraints reduce compilation errors)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** Security/reliability issues decrease after static analysis feedback
- **Fail Action:** Document limitation, explore overlap with grammar constraints

---

## Continuation Context

H-M2 tests the second verification layer. H-M1 proved syntax filtering works (40% error reduction). H-M2 tests whether static analysis catches semantic errors orthogonal to syntax errors.

### Previous Hypothesis Results
- **H-M1:** PASS - SynCode grammar constraints reduced syntax errors from 100% to 60%
- **Implication:** Code entering H-M2 is syntactically valid but may contain security/reliability issues

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for Bandit/Pylint LLM integration. General static analysis patterns available.

### Archon Code Examples

No specific Bandit/Pylint feedback loop code in KB.

### Exa GitHub Implementations

**Primary Source:** Blyth et al. 2025 - "Static Analysis as a Feedback Loop"
- Paper: arxiv.org/abs/2508.14419
- Benchmark: PythonSecurityEval (s2e-lab/SecurityEval on GitHub)
- Results: Security 40%→13%, Reliability 50%→11% in 10 iterations

**Implementation References:**
1. **cyb3rlab/CodeEnhancer** - Two-stage framework with Pylint+Bandit validation loop
2. **Kamel773/LLM-code-refine** - FDSP approach with Bandit feedback
3. **s2e-lab/SecurityEval** - Dataset with 121 prompts for 69 CWEs

### Implementation Priority Assessment

**CRITICAL:** Use established PythonSecurityEval benchmark (NOT synthetic data)

**Recommended Implementation Path:**
- Primary: Adapt CodeEnhancer validation loop for PoC
- Fallback: Direct Bandit+Pylint subprocess integration
- Justification: Established benchmarks with real security-sensitive prompts

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze.

---

## Experiment Specification

### Dataset

**Name:** SecurityEval v2.2
**Source:** s2e-lab/SecurityEval (HuggingFace: s2e-lab/SecurityEval)
**Type:** standard
**Size:** 121 prompts covering 69 CWEs

| Split | Count | Purpose |
|-------|-------|---------|
| Full | 121 | All security-sensitive prompts |

**Preprocessing:**
1. Load from HuggingFace datasets or GitHub JSONL
2. Filter to Python-only prompts
3. Extract prompt text and expected CWE category

**Loading Information:**
- Method: huggingface_datasets
- Identifier: s2e-lab/SecurityEval
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("s2e-lab/SecurityEval")
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct (same as H-M1 for continuity)
**Source:** meta-llama/CodeLlama-7b-Instruct-hf
**Purpose:** Generate code from security prompts WITHOUT static analysis feedback

**Loading Information:**
- Method: huggingface_transformers
- Identifier: meta-llama/CodeLlama-7b-Instruct-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** Baseline + Static Analysis Feedback Loop

**Core Mechanism Implementation:**

```python
def static_analysis_feedback_loop(code: str, max_iterations: int = 5) -> dict:
    """
    Apply Bandit+Pylint feedback loop to LLM-generated code.
    Returns metrics before/after refinement.
    """
    import subprocess
    import json
    
    def run_bandit(code_path: str) -> list:
        result = subprocess.run(
            ["bandit", "-f", "json", code_path],
            capture_output=True, text=True
        )
        if result.stdout:
            return json.loads(result.stdout).get("results", [])
        return []
    
    def run_pylint(code_path: str) -> list:
        result = subprocess.run(
            ["pylint", "--output-format=json", code_path],
            capture_output=True, text=True
        )
        if result.stdout:
            return json.loads(result.stdout)
        return []
    
    def count_issues(bandit_results, pylint_results) -> dict:
        security_issues = len(bandit_results)
        reliability_issues = len([
            r for r in pylint_results 
            if r.get("type") in ["warning", "error"]
        ])
        return {"security": security_issues, "reliability": reliability_issues}
    
    # Initial analysis
    initial_issues = count_issues(run_bandit(code), run_pylint(code))
    
    # Feedback loop
    current_code = code
    for iteration in range(max_iterations):
        bandit_issues = run_bandit(current_code)
        pylint_issues = run_pylint(current_code)
        
        if not bandit_issues and not pylint_issues:
            break
        
        # Format feedback for LLM
        feedback = format_issues_for_prompt(bandit_issues, pylint_issues)
        
        # Generate refined code (LLM call)
        current_code = llm_refine(current_code, feedback)
    
    final_issues = count_issues(run_bandit(current_code), run_pylint(current_code))
    
    return {
        "initial": initial_issues,
        "final": final_issues,
        "iterations": iteration + 1
    }
```

### Training Protocol

**Not applicable** - This is an inference-time feedback loop experiment, not a training experiment.

**Inference Configuration:**
- Temperature: 0.2 (deterministic generation)
- Max tokens: 512
- Max feedback iterations: 5 (PoC) or 10 (full)

### Evaluation

**Primary Metrics:**
1. `security_issue_reduction`: (initial_security - final_security) / initial_security
2. `reliability_issue_reduction`: (initial_reliability - final_reliability) / initial_reliability

**Success Criteria (PoC):**
- `final_security < initial_security` (any measurable reduction)
- `final_reliability < initial_reliability` (any measurable reduction)

**Secondary Metrics:**
- Iterations to convergence
- Functional correctness preservation (unit tests if available)

**Metrics Loading Information:**
- Task Type: code_quality_assessment
- Library: bandit, pylint (via subprocess)
- Code:
```python
import subprocess
# Bandit: pip install bandit
# Pylint: pip install pylint
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing initial vs final security/reliability issue counts

#### Additional Figures (LLM Autonomous)
- Issue reduction over iterations (line plot)
- CWE category distribution of detected vulnerabilities (bar chart)

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `final_security_issues < initial_security_issues`
3. `final_reliability_issues < initial_reliability_issues`

---

## Appendix: Reference Implementations

### 1. Blyth et al. 2025 - SelectIssues Algorithm
- Paper: "Static Analysis as a Feedback Loop"
- Key insight: Inject issue descriptions at specific code lines
- Results: Security 40%→13%, Reliability 50%→11%

### 2. cyb3rlab/CodeEnhancer
- GitHub: https://github.com/cyb3rlab/CodeEnhancer
- Components: `code_validator.py` with Pylint+Bandit loop
- Iterations: 5 (configurable)

### 3. Kamel773/LLM-code-refine
- GitHub: https://github.com/Kamel773/LLM-code-refine
- Approach: FDSP (Feedback-Driven Security Patching)
- Dataset: PythonSecurityEval (original)

### 4. s2e-lab/SecurityEval
- GitHub: https://github.com/s2e-lab/SecurityEval
- Dataset: 121 prompts, 69 CWEs
- Format: JSONL with ID, prompt, CWE

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- 2026-08-12: H-M2 set to IN_PROGRESS
- 2026-08-12: Phase 2C experiment design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub/Papers)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
