# Experiment Design: H-M1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Information content is preserved across format transformations, verified by reconstruction test where a third-party LLM can extract original error details from structured format with >95% accuracy
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing information preservation mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** MUST_WORK (pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
Information reconstruction accuracy >95% via third-party LLM extraction test

---

## Continuation Context

Building on H-E1 validation which confirmed structured error format improves repair success. H-M1 tests whether the structured format preserves all diagnostic information from raw compiler output, ensuring fair comparison in H-E1.

### Previous Hypothesis Results
H-E1 VALIDATED: StructuredError parser and formatters implemented and working. Experiment infrastructure validated. All 8 code modules confirmed functional.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[LIMITED_RESULTS - MCP UNAVAILABLE]**
- Archon MCP server not available in this session
- Research based on domain knowledge and H-E1 validated infrastructure

**[INFERRED]** Information Extraction Evaluation Patterns:
- Standard approach: Use separate LLM as "judge" to extract structured fields from text
- Accuracy measured via exact match or fuzzy match on extracted fields
- Common practice in NLP evaluation (e.g., LLM-as-judge frameworks)

### Archon Code Examples

**[INFERRED]** Reconstruction Test Pattern:
```python
# Pattern: Transform → Extract → Compare
original_fields = extract_fields(raw_error)
transformed = apply_structured_format(raw_error)
reconstructed_fields = llm_extract(transformed)
accuracy = compare_fields(original_fields, reconstructed_fields)
```

### Exa GitHub Implementations

**[LIMITED_RESULTS - MCP UNAVAILABLE]**
- Exa MCP server not available in this session
- Leveraging H-E1 infrastructure already validated

**Relevant Patterns from H-E1:**
- StructuredError parser already implemented
- Error field extraction logic exists
- Format transformers validated

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse H-E1 validated infrastructure**

**[INFERRED]** Implementation approach based on H-E1 outputs:
1. Use existing StructuredError parser from H-E1
2. Add reconstruction extraction module
3. Use GPT-4 or Claude as third-party judge LLM

**Recommended Implementation Path:**
- Primary: Extend H-E1 StructuredError infrastructure with reconstruction test
- Fallback: Standalone reconstruction evaluator
- Justification: H-E1 infrastructure already validated; minimal new code needed

### Code Analysis (Serena MCP)

**[SKIPPED - MCP UNAVAILABLE]**
- Serena MCP not available
- H-E1 code structure already documented in 04_validation.md

---

## Experiment Specification

### Dataset

**Dataset:** Error samples from H-E1 experiment
**Type:** standard (derived from EvalPlus HumanEval+/MBPP+ failures)
**Source:** H-E1 collected error corpus

| Attribute | Value |
|-----------|-------|
| Name | H-E1 Error Corpus |
| Size | Full H-E1 error collection (500+ samples minimum) |
| Splits | All errors used for reconstruction test |
| Format | (raw_error, structured_error) pairs |

**Loading Information** (for Phase 4 download):
- Method: Load from H-E1 experiment outputs
- Identifier: `{h-e1_folder}/data/error_pairs.json`
- Code: 
```python
import json
with open("../h-e1/data/error_pairs.json") as f:
    error_pairs = json.load(f)
```

### Models

#### Baseline Model

**Architecture:** Third-party LLM (judge)
**Purpose:** Extract error fields from structured format

**Loading Information** (for Phase 4 download):
- Method: OpenAI API or Anthropic API
- Identifier: `gpt-4` or `claude-3-sonnet`
- Code:
```python
from openai import OpenAI
client = OpenAI()
# or
from anthropic import Anthropic
client = Anthropic()
```

**Configuration:**
- Temperature: 0 (deterministic extraction)
- Max tokens: 500
- System prompt: Field extraction instructions

#### Proposed Model

**Architecture:** N/A (this is a validation test, not a model comparison)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Information Reconstruction Test
# Based on: LLM-as-judge evaluation pattern

class ReconstructionTest:
    """
    Verify structured format preserves all diagnostic information
    from raw compiler output.
    """
    def __init__(self, judge_llm, field_list):
        self.judge = judge_llm
        self.fields = field_list  # ['error_type', 'line_number', 'message', 'context']
    
    def extract_from_raw(self, raw_error: str) -> dict:
        """Ground truth extraction from raw error."""
        # Parse raw compiler output
        return parse_compiler_output(raw_error)
    
    def extract_from_structured(self, structured_error: str) -> dict:
        """LLM extracts fields from structured format."""
        prompt = f"""Extract these fields from the error message:
        Fields: {self.fields}
        Error: {structured_error}
        Return JSON with field values."""
        return self.judge.extract(prompt)
    
    def compute_accuracy(self, original: dict, reconstructed: dict) -> float:
        """Field-level accuracy: exact match per field."""
        matches = sum(1 for f in self.fields 
                      if original.get(f) == reconstructed.get(f))
        return matches / len(self.fields)
    
    def run_test(self, error_pairs: list) -> dict:
        """Run reconstruction test on all pairs."""
        accuracies = []
        for raw, structured in error_pairs:
            original = self.extract_from_raw(raw)
            reconstructed = self.extract_from_structured(structured)
            acc = self.compute_accuracy(original, reconstructed)
            accuracies.append(acc)
        return {
            'mean_accuracy': sum(accuracies) / len(accuracies),
            'per_sample': accuracies,
            'pass': sum(accuracies) / len(accuracies) > 0.95
        }
```

### Training Protocol

**N/A** - This is an evaluation-only experiment (no training required)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Training | None | Reconstruction test only |
| Judge LLM | GPT-4 or Claude-3 | Third-party, not in main experiment |
| Temperature | 0 | Deterministic extraction |
| Samples | Full H-E1 corpus | Statistical validity |
| Seeds | 1 | Deterministic judge |

### Evaluation

**Primary Metric:** Field-level reconstruction accuracy

| Metric | Definition | Target |
|--------|------------|--------|
| Field Accuracy | (matched fields) / (total fields) | >95% |
| Sample Pass Rate | % samples with 100% field match | >90% |

**Success Criteria:**
- Mean field accuracy > 95%
- No systematic information loss by error type

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Information extraction evaluation
- Library: Custom (sklearn.metrics for aggregation)
- Code:
```python
from sklearn.metrics import accuracy_score
import numpy as np

def compute_reconstruction_metrics(original_list, reconstructed_list, fields):
    field_accuracies = []
    for orig, recon in zip(original_list, reconstructed_list):
        matches = [orig.get(f) == recon.get(f) for f in fields]
        field_accuracies.append(np.mean(matches))
    return {
        'mean_accuracy': np.mean(field_accuracies),
        'std': np.std(field_accuracies),
        'pass_rate': np.mean([a == 1.0 for a in field_accuracies])
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Reconstruction accuracy vs 95% threshold bar chart

#### Additional Figures (LLM Autonomous)
- Per-field accuracy breakdown (which fields are hardest to reconstruct)
- Accuracy by error type (syntax vs runtime vs type errors)
- Confusion matrix for field extraction errors

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True - Reconstruction test is the mechanism
- `mechanism_isolatable`: True - Test runs independently
- `baseline_measurable`: True - Raw error fields extractable

### Architecture Compatibility
- H-E1 StructuredError format already validated
- Field extraction from raw errors is standard parsing
- Third-party LLM API access required

### Activation Indicators
- `mechanism_log_message`: "Reconstruction test starting with {n} samples"
- `tensor_shape_change`: N/A (not tensor-based)
- `metric_delta_expected`: Accuracy should be >0.95

### Mechanism Verification Code
```python
def verify_reconstruction_mechanism(test_result):
    """Verify reconstruction test ran correctly."""
    assert 'mean_accuracy' in test_result, "Missing accuracy metric"
    assert len(test_result['per_sample']) > 0, "No samples processed"
    assert 0 <= test_result['mean_accuracy'] <= 1, "Invalid accuracy range"
    
    if test_result['mean_accuracy'] >= 0.95:
        print("✅ GATE PASS: Reconstruction accuracy >= 95%")
        return True
    else:
        print(f"❌ GATE FAIL: Reconstruction accuracy = {test_result['mean_accuracy']:.2%}")
        return False
```

### Success Criteria
- `hypothesis_support_threshold`: 0.95
- `hypothesis_support_metric`: mean_accuracy

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean reconstruction accuracy > 95%

**Gate Result Interpretation:**
- PASS: Structured format preserves information → H-E1 comparison is fair
- FAIL: Information loss detected → Review transformation, iterate

---

## Appendix: Reference Implementations

### Primary Reference
- **H-E1 Validated Infrastructure**
  - Source: `../h-e1/code/`
  - Components: StructuredError parser, format transformers
  - Status: VALIDATED in H-E1

### Evaluation Pattern References
- **[INFERRED]** LLM-as-Judge Pattern
  - Common in: MT-Bench, AlpacaEval, LLM evaluation frameworks
  - Key insight: Use separate LLM for extraction to avoid circular validation

### Field Extraction References
- **[INFERRED]** Compiler Error Parsing
  - Standard fields: error_type, line_number, column, message, context
  - Libraries: tree-sitter for AST, regex for simple parsing

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- H-E1 completed and VALIDATED (2026-08-28)
- H-M1 experiment design COMPLETED

---

*MCP Tools Used: None available (Archon, Exa, Serena unavailable)*
*Specifications based on H-E1 validated infrastructure and domain knowledge*
*Next Phase: Phase 3 - Implementation Planning*
