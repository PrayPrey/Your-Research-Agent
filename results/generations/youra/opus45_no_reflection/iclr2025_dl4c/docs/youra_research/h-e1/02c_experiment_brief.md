# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** EVAF mechanism can be implemented and produces filtered AI feedback with measurable accept rate between 20-60%
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - Pipeline stops if accept rate outside 20-60%

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Accept rate of AI suggestions passing execution verification must be between 20% and 60%. This range indicates selective filtering:
- <10%: EVAF degenerates to pure execution feedback (AI nearly always wrong)
- >90%: Gating unnecessary (AI nearly always correct)

---

## Continuation Context

This is the first hypothesis in the verification chain. No prior results to build on.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for EVAF-specific implementations. Key related work:
- CodeT5 encoder-decoder architecture widely used for code generation tasks
- HumanEval benchmark standard for evaluating code generation with unit tests
- Reinforcement learning from feedback approaches documented in RLTF paper

### Archon Code Examples

No direct EVAF implementations found. Related patterns:
- LoRA fine-tuning patterns for efficient model adaptation
- Diffusion model feedback loops (different domain but similar gating concept)

### Exa GitHub Implementations

**Primary Source: RLTF (Official Implementation)**
- Repository: https://github.com/Zyq-scut/RLTF
- License: BSD 3-Clause
- Key components:
  - Unit test execution harness (`script/run_unit_tests.sh`)
  - Online RL training with test feedback
  - CodeT5 and CodeGen model support
  - APPS/MBPP dataset integration

**Secondary Source: bigcode-evaluation-harness**
- Repository: https://github.com/bigcode-project/bigcode-evaluation-harness
- HumanEval evaluation with pass@k metrics
- Unit test execution framework
- Standard evaluation protocol for code generation

**Tertiary Source: CodeT5+ (Salesforce)**
- Repository: https://github.com/salesforce/CodeT5
- HumanEval evaluation scripts
- CodeT5-770M achieves 15.5% pass@1 (baseline reference)
- InstructCodeT5+ 16B achieves 36.1% pass@1

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Justification |
|----------|---------------|---------------|
| 1 | RLTF official repo | Same model (CodeT5), unit test framework, proven to work |
| 2 | bigcode-evaluation-harness | Standard HumanEval evaluation, widely validated |
| 3 | Custom implementation | Only if existing tools insufficient |

**Recommended Implementation Path:**
- Primary: Adapt RLTF's unit test execution framework for EVAF gating
- Fallback: Build minimal test harness using bigcode-evaluation-harness patterns
- Justification: RLTF already implements fine-grained unit test feedback on CodeT5; EVAF adds AI critique generation and gating layer

### Code Analysis (Serena MCP)

Not applicable - no local codebase to analyze for H-E1. Implementation will be new.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval |
| **Version** | openai_humaneval (HuggingFace) |
| **Type** | standard |
| **Size** | 164 problems |
| **Split** | Full test set (all 164 problems) |
| **Tests per Problem** | ~7 average |

**Preprocessing:**
1. Load via HuggingFace datasets
2. Extract function signature, docstring, canonical solution
3. Generate baseline (incorrect) solutions using CodeT5-770M
4. Filter to problems where baseline fails (target: ~80-120 problems)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("openai_humaneval", split="test")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | CodeT5-770M |
| **Source** | Salesforce/codet5-large |
| **Architecture** | Encoder-Decoder Transformer |
| **Parameters** | 770M |
| **HumanEval pass@1** | 15.5% (reference) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `Salesforce/codet5-large`
- Code:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-large")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-large")
```

#### AI Feedback Generator

| Attribute | Value |
|-----------|-------|
| **Name** | CodeLlama-Instruct |
| **Source** | codellama/CodeLlama-7b-Instruct-hf |
| **Purpose** | Generate code critiques for failing solutions |
| **Architecture** | Decoder-only Transformer |

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
feedback_model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
feedback_tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** EVAF Pipeline = AI Feedback Generator + Execution Gating

**Core Mechanism Implementation:**

```python
def evaf_pipeline(problem, failing_code, test_cases):
    """
    EVAF: Execution-Verified AI Feedback
    
    Returns:
        accepted: bool - whether AI suggestion passed verification
        suggestion: str - the AI-generated fix (if accepted)
        accept_rate: float - running accept rate
    """
    # Step 1: Generate AI critique
    prompt = f"""The following code fails some tests:
```python
{failing_code}
```

Problem: {problem['prompt']}

Explain what's wrong and provide a corrected version."""
    
    ai_suggestion = feedback_model.generate(prompt)
    
    # Step 2: Extract code fix from AI response
    fixed_code = extract_code_from_response(ai_suggestion)
    if fixed_code is None:
        return False, None, "no_code_extracted"
    
    # Step 3: Execution gating - run unit tests
    test_results = run_unit_tests(fixed_code, test_cases)
    
    # Step 4: Accept/reject based on test results
    if test_results['all_passed']:
        return True, fixed_code, "accepted"
    else:
        return False, None, "tests_failed"


def compute_accept_rate(results):
    """Compute overall accept rate across all problems."""
    total = len(results)
    accepted = sum(1 for r in results if r['accepted'])
    return accepted / total if total > 0 else 0.0
```

### Training Protocol

**Note:** H-E1 is an EXISTENCE test - no training required. We measure accept rate on inference only.

| Parameter | Value |
|-----------|-------|
| **Phase** | Inference only (no training) |
| **Problems Evaluated** | 164 (full HumanEval) |
| **Samples per Problem** | 1 (deterministic for reproducibility) |
| **AI Generation** | Temperature 0.2, max_tokens 512 |
| **Test Timeout** | 3.0 seconds per test |

### Evaluation

| Metric | Description | Target |
|--------|-------------|--------|
| **Accept Rate** | (AI suggestions passing tests) / (total AI suggestions) | 20-60% |
| **Coverage** | (Problems with actionable AI suggestions) / (total failing problems) | >80% |
| **Rejection Reasons** | Distribution of why suggestions were rejected | Informational |

**Success Criteria (PoC: Direction-based):**
- **Primary:** Accept rate is between 20% and 60%
- **Secondary:** AI generates actionable suggestions for >80% of failing tests

**Failure Response:**
- IF accept rate <10%: PIVOT to relaxed gating (accept if any test improves)
- IF accept rate >90%: EXPLORE why AI is so accurate (may not need EVAF)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation with execution verification
- Library: Custom (unit test execution)
- Code:
```python
def evaluate_evaf(results):
    """Compute EVAF metrics from pipeline results."""
    total = len(results)
    accepted = sum(1 for r in results if r['accepted'])
    actionable = sum(1 for r in results if r['has_code_suggestion'])
    
    return {
        'accept_rate': accepted / total,
        'coverage': actionable / total,
        'rejection_breakdown': Counter(r['rejection_reason'] for r in results if not r['accepted'])
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Accept rate bar chart with 20-60% target zone highlighted

#### Additional Figures (LLM Autonomous)

1. **Accept Rate Distribution**: Histogram of per-problem accept rates
2. **Rejection Reason Breakdown**: Pie chart of why AI suggestions failed
3. **Problem Difficulty vs Accept Rate**: Scatter plot showing relationship

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Accept rate between 20% and 60%

**Gate Decision:**
- PASS (20% ≤ accept_rate ≤ 60%): Proceed to H-M1
- FAIL (accept_rate < 10%): STOP, EVAF mechanism not viable
- FAIL (accept_rate > 90%): STOP, gating unnecessary

---

## Appendix: Reference Implementations

### RLTF Official Repository
- **URL:** https://github.com/Zyq-scut/RLTF
- **Relevant Files:**
  - `script/run_unit_tests.sh` - Unit test execution
  - `script/generate_parallel.py` - Code generation
  - `compute_pass_at_k.py` - pass@k computation
- **Key Insight:** Uses CodeT5 with fine-grained test feedback; EVAF adds AI critique layer

### bigcode-evaluation-harness
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevant Files:**
  - `bigcode_eval/tasks/humaneval.py` - HumanEval task definition
  - `bigcode_eval/tasks/custom_metrics/code_eval.py` - Code evaluation
- **Key Insight:** Standard evaluation protocol; 3.0s timeout per test, pass@k estimation

### CodeT5+ Salesforce Repository
- **URL:** https://github.com/salesforce/CodeT5
- **Relevant Files:**
  - `CodeT5+/humaneval/run_generate.sh` - HumanEval generation
  - `CodeT5+/humaneval/run_eval.sh` - Evaluation script
- **Key Insight:** CodeT5-770M baseline: 15.5% pass@1

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
1. Phase 2B: Hypothesis defined with MUST_WORK gate
2. Phase 2C: Experiment design completed (this document)
3. Next: Phase 3 - Implementation Planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
