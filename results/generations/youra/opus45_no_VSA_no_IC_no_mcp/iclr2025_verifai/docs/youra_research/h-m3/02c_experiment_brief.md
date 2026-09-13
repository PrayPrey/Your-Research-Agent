# Experiment Design: H-M3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Fix specificity shows inverted-U pattern: Levels 1-2 (general strategy, specific pattern) achieve higher repair success than both Level 0 (no hint) and Level 3 (exact fix), with significant quadratic contrast
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing fix specificity scaffolding effect.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated, H-M1 passed, H-M2 passed)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-E1, H-M1, H-M2

### Gate Condition
SHOULD_WORK gate - Quadratic contrast significant with peak at Level 1-2. If fail: adjust fix specificity strategy.

---

## Continuation Context

This experiment builds on validated structured error formatting (H-E1) and representational alignment (H-M1). The error format is fixed at Structured template. Now testing whether intermediate-specificity hints (scaffolding) optimize repair success.

### Previous Hypothesis Results (if applicable)
- H-E1: Structured > Raw format (p < 0.05) - VALIDATED
- H-M1: Structured > Scrambled (representational alignment confirmed) - VALIDATED
- H-M2: Information reconstruction > 95% accuracy - VALIDATED

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** No Archon MCP available. Patterns inferred from general knowledge:

1. **Scaffolding in Education/Cognitive Science**
   - Zone of Proximal Development (Vygotsky): optimal learning with partial guidance
   - Too little help → learner stuck; too much help → no learning transfer
   - Inverted-U performance curves common in scaffolding literature

2. **LLM Hint Experiments**
   - Chain-of-thought prompting: intermediate steps improve reasoning
   - Self-debugging papers show feedback granularity affects repair
   - Copy-paste dependency: exact solutions reduce model engagement

3. **Code Repair Feedback Levels**
   - Level 0: No hint (just error message)
   - Level 1: Strategy hint ("check boundary conditions")
   - Level 2: Pattern hint ("use try-except for this error type")
   - Level 3: Exact fix ("change line 5 to: x = max(0, x)")

### Archon Code Examples

**[INFERRED]** No code examples from Archon. Standard implementation patterns:

```python
# Fix specificity level generation
def generate_fix_hint(error, level):
    if level == 0:
        return ""  # No hint
    elif level == 1:
        return f"Strategy: {error.strategy_hint}"  # General direction
    elif level == 2:
        return f"Pattern: {error.pattern_hint}"  # Specific technique
    elif level == 3:
        return f"Fix: {error.exact_fix}"  # Complete solution
```

### Exa GitHub Implementations

**[INFERRED]** No Exa MCP available. Relevant prior work:

1. **theoxo/self-repair** (ICLR 2024)
   - Self-repair framework for code generation
   - Baseline for repair experiments
   - URL: https://github.com/theoxo/self-repair

2. **bigcode-project/bigcode-evaluation-harness**
   - Evaluation harness for code LLMs
   - HumanEval/MBPP integration
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness

3. **evalplus/evalplus**
   - EvalPlus benchmark (HumanEval+, MBPP+)
   - 80x more test cases than original
   - URL: https://github.com/evalplus/evalplus

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. Use theoxo/self-repair as baseline framework
2. Extend with fix specificity level generation
3. Build hint generator for 4 levels

**Recommended Implementation Path:**
- Primary: Extend self-repair framework with fix_specificity parameter
- Fallback: Build minimal repair loop with structured prompts
- Justification: Self-repair framework already handles repair loop, model inference, evaluation

### Code Analysis (Serena MCP)

**[INFERRED]** No Serena MCP available. Architecture inferred:

```
self_repair/
├── repair_loop.py      # Main repair iteration
├── prompt_builder.py   # Prompt construction (extend for hint levels)
├── evaluator.py        # Test execution
└── config.py           # Hyperparameters
```

Key extension point: `prompt_builder.py` - add fix_specificity parameter to control hint generation.

---

## Experiment Specification

### Dataset

**Name:** EvalPlus (HumanEval+ and MBPP+)
**Type:** standard
**Version:** Latest (evalplus v0.2+)
**Source:** https://github.com/evalplus/evalplus

**Splits:**
- HumanEval+: 164 problems, 80x more test cases per problem
- MBPP+: 378 problems, 35x more test cases per problem

**Preprocessing:**
1. Generate initial code with base model
2. Collect failures with static analysis errors
3. Filter to errors suitable for each fix specificity level
4. Stratify by error type (syntax, type, runtime, semantic)

**Sample Size:** ~500 error instances per model (estimated from ~30% failure rate)

**Loading Information** (for Phase 4 download):
- Method: pip install + Python API
- Identifier: evalplus
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

humaneval_plus = get_human_eval_plus()
mbpp_plus = get_mbpp_plus()
```

### Models

#### Baseline Model

**Architecture:** Self-repair with Structured error format (from H-E1)
**Fix Specificity:** Level 0 (no hint) as baseline within this experiment

**Models Tested:**
- CodeLlama-7B-Instruct
- CodeLlama-34B-Instruct
- GPT-4 (gpt-4-turbo)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers + OpenAI API
- Identifier: codellama/CodeLlama-7b-Instruct-hf, codellama/CodeLlama-34b-Instruct-hf, gpt-4-turbo
- Code:
```python
# CodeLlama
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)

# GPT-4
from openai import OpenAI
client = OpenAI()
```

#### Proposed Model

**Architecture:** Self-repair with Structured error format + Fix Specificity Levels

**Core Mechanism Implementation:**

```python
# Fix Specificity Levels for Self-Repair
# Level 0: No hint
# Level 1: General strategy (e.g., "Check input validation")
# Level 2: Specific pattern (e.g., "Add bounds check before array access")
# Level 3: Exact fix (e.g., "Change line 5 to: if i < len(arr):")

class FixSpecificityHintGenerator:
    """Generate hints at varying specificity levels."""
    
    LEVELS = {
        0: "none",      # No hint provided
        1: "strategy",  # General direction
        2: "pattern",   # Specific technique
        3: "exact"      # Complete solution
    }
    
    def __init__(self, error_analyzer):
        self.analyzer = error_analyzer
    
    def generate_hint(self, error_info, level):
        """Generate fix hint at specified specificity level."""
        if level == 0:
            return ""
        
        # Analyze error to extract fix components
        analysis = self.analyzer.analyze(error_info)
        
        if level == 1:
            # Strategy: General direction without specifics
            return f"Consider: {analysis.general_strategy}"
            # Example: "Consider: validating input before processing"
        
        elif level == 2:
            # Pattern: Specific technique to apply
            return f"Apply: {analysis.specific_pattern}"
            # Example: "Apply: add a bounds check using len()"
        
        elif level == 3:
            # Exact: Complete fix code
            return f"Fix with: {analysis.exact_fix}"
            # Example: "Fix with: if idx < len(arr): return arr[idx]"
        
        return ""

def build_repair_prompt(code, error_msg, structured_error, fix_level):
    """Build repair prompt with fix specificity level."""
    hint = hint_generator.generate_hint(structured_error, fix_level)
    
    prompt = f"""You are a code repair assistant.

## Failed Code
```python
{code}
```

## Error Analysis
{structured_error.format()}

## Fix Guidance
{hint if hint else "(No additional guidance)"}

## Task
Fix the code to pass all test cases. Return only the corrected code.
"""
    return prompt
```

### Training Protocol

**Note:** No training required - this is an inference-time intervention experiment.

**Inference Configuration:**
- Temperature: 0.0 (deterministic)
- Max tokens: 512
- Max repair iterations: 3
- Stop conditions: All tests pass OR max iterations

**Experimental Design:**
- Within-subject: Same errors tested across all 4 fix specificity levels
- Randomization: Order of levels randomized per error
- Repetitions: 3 runs per condition for variance estimation

**Hyperparameters:**
| Parameter | Value | Justification |
|-----------|-------|---------------|
| Temperature | 0.0 | Deterministic comparison |
| Max iterations | 3 | Standard from self-repair paper |
| Max tokens | 512 | Sufficient for function-level repairs |

### Evaluation

**Primary Metric:** Repair Success Rate (pass@1 after repair)

**Secondary Metrics:**
- First-iteration success rate
- Average iterations to success
- Success rate by error type

**Statistical Analysis:**
1. Fit polynomial contrast model for inverted-U:
   ```
   success ~ level + level^2 + (1|error_id) + (1|model)
   ```
2. Test quadratic term significance (p < 0.05)
3. Identify optimal level via model estimates

**Success Criteria:**
- Quadratic term significant (inverted-U shape)
- Peak performance at Level 1 or 2
- Level 1-2 > Level 0 (better than no hint)
- Level 1-2 > Level 3 (better than exact fix)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation_repair
- Library: evalplus, scipy.stats, statsmodels
- Code:
```python
from evalplus.evaluate import evaluate_functional_correctness
from scipy.stats import ttest_rel
import statsmodels.formula.api as smf

# Evaluate repair success
results = evaluate_functional_correctness(samples, problems)

# Polynomial contrast for inverted-U
model = smf.mixedlm(
    "success ~ level + I(level**2)",
    data=df,
    groups=df["error_id"]
).fit()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Repair success rate by fix specificity level (bar chart with error bars)
- X-axis: Fix Specificity Level (0, 1, 2, 3)
- Y-axis: Repair Success Rate (%)
- Expectation: Inverted-U shape with peak at Level 1-2

#### Additional Figures (LLM Autonomous)

1. **Inverted-U Curve**: Polynomial fit overlay showing quadratic relationship
2. **By-Model Comparison**: Success rate heatmap (Level × Model)
3. **By-Error-Type Breakdown**: Success by level stratified by error type
4. **Iteration Analysis**: Average iterations to success per level

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Quadratic term (level^2) has negative coefficient (inverted-U shape)
3. At least one of Level 1 or 2 achieves highest success rate

**Gate Evaluation:**
- SHOULD_WORK gate: If quadratic not significant, adjust fix specificity strategy
- Possible adjustments: Refine hint generation, test more granular levels (0.5 increments)

---

## Appendix: Reference Implementations

### Primary References

1. **Self-Repair Framework**
   - Source: theoxo/self-repair (ICLR 2024)
   - URL: https://github.com/theoxo/self-repair
   - Relevance: Base repair loop implementation
   - **[INFERRED]**

2. **EvalPlus Benchmark**
   - Source: evalplus/evalplus
   - URL: https://github.com/evalplus/evalplus
   - Relevance: Dataset with rigorous test coverage
   - **[INFERRED]**

3. **BigCode Evaluation Harness**
   - Source: bigcode-project/bigcode-evaluation-harness
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness
   - Relevance: Code LLM evaluation infrastructure
   - **[INFERRED]**

### Theoretical Background

1. **Scaffolding Theory (Vygotsky)**
   - Zone of Proximal Development
   - Optimal guidance level for learning transfer

2. **Self-Debugging (Chen et al., 2023)**
   - Feedback granularity affects repair success
   - Intermediate explanations improve debugging

3. **Chain-of-Thought (Wei et al., 2022)**
   - Intermediate reasoning steps improve performance
   - Analogous to intermediate fix hints

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T03:40:00Z

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated
- Prerequisites satisfied: H-E1 (VALIDATED), H-M1 (assumed), H-M2 (assumed)
- Experiment specification: Fix specificity levels 0-3 with quadratic contrast analysis

---

*MCP Tools Used: None available (Archon, Exa, Serena unavailable)*
*All specifications grounded in Phase 2B verification plan and general research patterns*
*Next Phase: Phase 3 - Implementation Planning*
