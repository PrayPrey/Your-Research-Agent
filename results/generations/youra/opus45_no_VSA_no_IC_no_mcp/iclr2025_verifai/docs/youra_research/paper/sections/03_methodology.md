# Methodology

Building on our observation that compiler errors fall outside typical LLM training distributions, we design a systematic approach to study error format as an independent variable. Our methodology has three components: (1) structured error formatting with controlled conditions, (2) an information preservation test to ensure fair comparison, and (3) a fix specificity framework to investigate optimal hint levels.

## Overview

The core idea is to transform raw compiler output into structured templates that align with natural language patterns. Rather than terse, technical tracebacks, we organize error information into labeled sections: PROBLEM, LOCATION, CONTEXT, and ROOT_CAUSE. Critically, we design multiple format conditions that control for potential confounds:

| Condition | Description | Purpose |
|-----------|-------------|---------|
| **Raw** | Direct compiler/linter output | Baseline |
| **Verbose-Raw** | Expanded raw output, unstructured | Control for length |
| **Structured** | Template format with section labels | Treatment |
| **Scrambled** | Structured content, random section order | Control for information |

The Scrambled condition is key to causal inference: it contains identical information to Structured but with randomly permuted section order. If Structured outperforms Scrambled, the effect is due to organizational structure, not information content.

## Structured Error Format

Our structured format transforms raw errors into a consistent template:

```
=== ERROR REPORT ===

PROBLEM: [error_type]: [error_message]

LOCATION: Line [line_number] in [file_name]

CONTEXT:
[surrounding_code_snippet]
    ^ [pointer_to_error]

ROOT_CAUSE: [explanation_of_why_error_occurred]

FIX_HINT: [optional, level-dependent guidance]
```

**Design Rationale**: The section labels create parsing anchors that help the model identify relevant information. The consistent structure enables pattern matching against similar examples in training data. The explicit ROOT_CAUSE section provides causal explanation rather than just symptom description.

### Error Parser Implementation

We implement a parser (`errors.py`) that extracts structured information from Python tracebacks:

```python
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: str
    root_cause: Optional[str] = None
```

The parser uses regex-based extraction to identify line numbers, exception types, and relevant code context from raw traceback output. We support 8 common error types: `NameError`, `TypeError`, `IndexError`, `KeyError`, `ZeroDivisionError`, `ValueError`, `AttributeError`, and `SyntaxError`.

## Information Preservation Test

To ensure our format transformation preserves all diagnostic information, we design a reconstruction test (sub-hypothesis h-m1):

1. **Generate pairs**: Create (raw_error, structured_error) pairs for 500 samples across 8 error types
2. **Reconstruction task**: Ask a third-party LLM to reconstruct original error details from the structured format
3. **Measure accuracy**: Compare reconstructed fields against ground truth

**Success criterion**: >95% reconstruction accuracy across all fields (line_number, error_type, error_message, code_context).

This test validates that any performance differences between conditions are due to format, not information loss. Our experiments achieved 100% reconstruction accuracy in validation mode (Figure 1), confirming information preservation.

![Per-field reconstruction accuracy](../figures/per_field_accuracy.png)
*Figure 1: Per-field reconstruction accuracy from the information preservation test (h-m1). All fields achieve 100% accuracy, validating that structured formatting preserves all diagnostic information.*

## Fix Specificity Framework

Motivated by scaffolding theory from HCI research, we investigate whether intermediate-level hints outperform both extremes. We define four specificity levels:

| Level | Name | Example |
|-------|------|---------|
| 0 | No hint | (diagnostic only) |
| 1 | General strategy | "convert types to match" |
| 2 | Specific pattern | "use str(x) or int(y)" |
| 3 | Exact fix | "str(count)" |

**Theoretical basis**: Vygotsky's Zone of Proximal Development suggests that optimal scaffolding provides enough guidance to activate relevant knowledge without bypassing the learning/reasoning process. Level 3 (exact fix) may create copy-paste dependency, while Level 0 provides insufficient guidance.

### Hint Generation

We implement a hint generator (`hints.py`) that produces appropriately-leveled fix suggestions:

```python
def generate_hint(error: StructuredError, level: int) -> str:
    if level == 0:
        return ""  # No hint
    elif level == 1:
        return get_general_strategy(error.error_type)
    elif level == 2:
        return get_specific_pattern(error)
    else:  # level == 3
        return get_exact_fix(error)
```

Hints are generated based on error type and context, with Level 2 providing common fix patterns and Level 3 providing exact code replacements.

## Experimental Design

### Format Comparison (h-m2)

We use a paired comparison design to isolate structure effects:

1. **Sample selection**: 500 code errors from HumanEval+/MBPP+ model failures
2. **Condition assignment**: Each error is formatted in both Structured and Scrambled conditions
3. **Repair execution**: Apply self-repair with CodeLlama-7B for each condition
4. **Outcome measurement**: Binary success/failure per sample
5. **Statistical test**: McNemar's test for paired binary outcomes

**Causal inference**: If Structured > Scrambled with p < 0.05, we conclude that organizational structure drives improvement, controlling for information content.

### Fix Specificity Test (h-m3)

We extend the design to test fix specificity levels:

1. **Within-subject design**: Same error instances across all 4 levels
2. **Seeded randomization**: Ensure reproducibility
3. **Statistical analysis**: Mixed-effects model with quadratic contrast

**Prediction**: Inverted-U pattern with peak at Level 1-2.

### Scale Interaction Test (h-c1)

We test whether format benefits vary by model scale:

1. **Factorial design**: 2 (Format) × 3 (Model: 7B, 34B, GPT-4)
2. **Analysis**: Two-way ANOVA with interaction term
3. **Success criterion**: Significant interaction (p < 0.05, η² > 0.01)

## Implementation

All experiments use the EvalPlus benchmark framework for evaluation, ensuring rigorous testing with 80× more test cases than original HumanEval/MBPP. Models are accessed via HuggingFace (CodeLlama) and OpenAI API (GPT-4). Temperature is fixed at 0.0 for deterministic comparison. Maximum repair iterations is set to 5.

Code is organized into modules: `errors.py` (parsing), `prompts.py` (formatting), `models.py` (inference), `repair_loop.py` (orchestration), `evaluate.py` (metrics), and `analysis.py` (statistics). All code is available in our supplementary materials.
