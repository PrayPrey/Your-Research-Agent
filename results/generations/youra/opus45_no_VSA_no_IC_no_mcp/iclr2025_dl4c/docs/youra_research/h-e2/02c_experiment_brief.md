# Experiment Design: h-e2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** AI-critic feedback (off-the-shelf instruction-tuned LLM critique) yields measurably higher pass@1 than random baseline after k=3 refinement iterations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** Yes (no prerequisites for h-e2)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e2
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
AI-critic feedback must yield measurably higher pass@1 than random baseline. This establishes that LLM critique provides meaningful signal for code refinement (not just noise).

---

## Continuation Context

**First Hypothesis:** No previous context - this is the foundation hypothesis for h-e2.

### Previous Hypothesis Results (if applicable)
N/A - First in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP Unavailable* - Used WebSearch fallback.

**Key Findings from Literature Search:**

1. **Self-Refine (Madaan et al., 2023)**
   - LLMs generate feedback on their own output, use it to refine iteratively
   - No supervised training data required
   - ~20% absolute improvement across tasks
   - Three-phase prompting: Init → Feedback → Iterate

2. **Natural Language Feedback for Code (2023)**
   - NL feedback improved CODEGEN-MONO 6.1B pass@1 on MBPP by 38% relative (10% absolute)
   - Human-written feedback outperforms LLM-generated feedback

3. **Complexity-Based Feedback (2025)**
   - GPT-4o pass@1 improved 6.74% vs 2.24% baseline on HumanEval
   - Llama 3.1 improved 10.29% vs 4.41%

### Archon Code Examples

*MCP Unavailable* - Used WebFetch on Self-Refine repo.

**Self-Refine Implementation Pattern:**
```python
# Three-phase prompting structure
# 1. INIT: Generate initial output
# 2. FEEDBACK: Model evaluates own output
# 3. ITERATE: Refine based on feedback until stopping criteria

# Key files: src/pie/run.py for code improvement task
# Uses temperature=0.7, max_attempts=4
```

### Exa GitHub Implementations

*MCP Unavailable* - Used WebSearch + WebFetch fallback.

**Repository 1**: [madaan/self-refine](https://github.com/madaan/self-refine)
- **URL**: https://github.com/madaan/self-refine
- **Relevance**: Official Self-Refine implementation with iterative feedback loop
- **Architecture**: Three-phase prompting (Init, Feedback, Iterate)
- **Key Code**:
  ```python
  # PIE task (code improvement) in src/pie/run.py
  # --max_attempts 4 for refinement iterations
  # Uses prompt-lib for prompt management
  ```
- **Training Config**: No training - inference only with API calls
- **Dataset**: CodeNet-Python for PIE task
- **License**: Apache-2.0

**Repository 2**: [evalplus/evalplus](https://github.com/evalplus/evalplus)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Rigorous HumanEval/MBPP evaluation framework
- **Used For**: Evaluation pipeline and pass@k computation

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, we compare AI feedback vs random baseline**

**Recommended Implementation Path:**
- Primary: Adapt Self-Refine feedback mechanism for HumanEval/MBPP
- Fallback: Simple prompt-based feedback generation
- Justification: Self-Refine is well-documented, Apache-2.0 licensed, and directly applicable

### Code Analysis (Serena MCP)

*Skipped* - Code from search results sufficiently clear for EXISTENCE-level PoC.

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval**
- **Type:** standard
- **Source:** https://github.com/openai/human-eval
- **Size:** 164 problems
- **Task:** Function completion with docstring → code
- **Evaluation:** Test case execution (pass/fail)

**Dataset 2: MBPP**
- **Type:** standard
- **Source:** https://github.com/google-research/mbpp
- **Size:** 500 problems (test split)
- **Task:** NL description → Python function
- **Evaluation:** Test case execution (pass/fail)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp", split="test")
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
**Type:** Instruction-tuned code LLM
**Source:** HuggingFace

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** Baseline + AI Critic Feedback Loop

**Core Mechanism Implementation:**

```python
# Core Mechanism: AI Critic Feedback for Code Refinement
# Based on: Self-Refine (Madaan et al., 2023)

class AICriticRefinement:
    """
    Iteratively refine code using LLM-generated critique.
    Tests h-e2: Does AI feedback beat random baseline?
    """
    def __init__(self, generator_model, critic_model, k=3):
        self.generator = generator_model  # CodeLlama-7B-Instruct
        self.critic = critic_model        # Same model or separate
        self.k = k                         # refinement iterations
    
    def generate_initial(self, prompt: str) -> str:
        """Step 1: Generate initial code from problem description."""
        return self.generator.generate(prompt)
    
    def generate_feedback(self, code: str, problem: str) -> str:
        """Step 2: AI critic generates natural language feedback."""
        critique_prompt = f"""Review this code for the problem:
Problem: {problem}
Code: {code}

Identify bugs, logic errors, edge cases missed. Be specific."""
        return self.critic.generate(critique_prompt)
    
    def refine_code(self, code: str, feedback: str, problem: str) -> str:
        """Step 3: Refine code based on feedback."""
        refine_prompt = f"""Fix the code based on this feedback:
Problem: {problem}
Current code: {code}
Feedback: {feedback}

Provide corrected code only."""
        return self.generator.generate(refine_prompt)
    
    def run(self, problem: str) -> str:
        """Full refinement loop for k iterations."""
        code = self.generate_initial(problem)
        for _ in range(self.k):
            feedback = self.generate_feedback(code, problem)
            code = self.refine_code(code, feedback, problem)
        return code

# Random baseline: replace generate_feedback with random text
```

### Training Protocol

**No Training Required** - This is an inference-only experiment.

**Inference Configuration:**
- **Temperature:** 0.7 (for generation diversity)
- **Max tokens:** 512 (sufficient for function-level code)
- **Refinement iterations (k):** 3
- **Seeds:** 1 (fixed for reproducibility)

**Source:** Self-Refine paper defaults

### Evaluation

**Primary Metrics:**
- **pass@1**: Fraction of problems solved on first attempt after k refinements

**Success Criteria (PoC):**
- `AI_critic_pass@1 > random_baseline_pass@1` (direction only)

**Expected Baseline Performance** (from research):
- Zero-shot CodeLlama-7B: ~30-35% pass@1 on HumanEval
- With Self-Refine style feedback: +5-10% improvement expected
- **Source:** Self-Refine paper, EvalPlus leaderboard

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation
- Library: evalplus or custom execution
- Code:
```python
def compute_pass_at_1(results: list[dict]) -> float:
    """Compute pass@1 from execution results."""
    passed = sum(1 for r in results if r["passed"])
    return passed / len(results)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing pass@1 for AI-critic vs random baseline

#### Additional Figures (LLM Autonomous)

1. **Per-iteration improvement curve**: pass@1 at k=0,1,2,3
2. **Error category breakdown**: Types of bugs fixed by AI critic vs random

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `AI_critic_pass@1 > random_baseline_pass@1`

**Mechanism Verification:**
- Log AI critic feedback at each iteration
- Verify feedback is meaningful (not empty/random)
- Track which problems improve with refinement

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon unavailable)

**Source 1**: Self-Refine paper and repository
- **Type**: Academic paper + GitHub
- **Query Used**: "Self-Refine LLM feedback code generation"
- **Key Insights**:
  - Three-phase prompting: Init → Feedback → Iterate
  - ~20% improvement across tasks
  - No training required
- **Used For**: Core mechanism design, pseudo-code

**Source 2**: Natural Language Feedback for Code
- **Type**: arXiv paper
- **Query Used**: "AI critic code generation feedback HumanEval MBPP"
- **Key Insights**:
  - 38% relative improvement on MBPP
  - LLM feedback less effective than human feedback
- **Used For**: Expected improvement bounds

### B. GitHub Implementations

**Repository 1**: [madaan/self-refine](https://github.com/madaan/self-refine)
- **URL**: https://github.com/madaan/self-refine
- **Relevance**: Official Self-Refine implementation
- **License**: Apache-2.0
- **Used For**: Feedback loop structure, PIE task reference

**Repository 2**: [evalplus/evalplus](https://github.com/evalplus/evalplus)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: HumanEval/MBPP evaluation framework
- **Used For**: Evaluation methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear for PoC.

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B | 02b_verification_plan.md |
| Feedback mechanism | GitHub | madaan/self-refine |
| Pseudo-code | WebSearch + WebFetch | Self-Refine repo |
| Evaluation metrics | Phase 2B | Success criteria |
| Expected baseline | Research | EvalPlus, Self-Refine paper |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - restated in conversation)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-28
- Experiment design: COMPLETED

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable), WebFetch*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
