# Methodology

Our experimental design follows directly from our key insight: if execution feedback's advantage arises from counterfactual localization, then (1) traces should contain extractable counterfactual information, (2) this information should enable targeted rather than global edits, and (3) targeted edits should achieve higher fix rates. We design experiments to test each step of this causal chain.

## Overview

We conduct a controlled comparison across four feedback conditions, holding constant the base model, refinement protocol, and benchmark while varying only the feedback signal:

| Condition | Description |
|-----------|-------------|
| **Execution-Detailed** | Full error trace: line numbers, error type, expected/actual values |
| **Execution-Binary** | Pass/fail only, no diagnostic information |
| **AI-Critic** | Off-the-shelf LLM critique (CodeLlama-7B as critic) |
| **Random** | Shuffled feedback from other samples (control) |

All feedback is converted to natural language using standardized templates to control for format differences. This ensures any performance gap reflects information content, not presentation.

## Feedback Format Normalization

**Rationale:** Prior work confounds feedback content with feedback format. Execution traces are structured (line numbers, types), while AI critiques are prose. We normalize both to natural language.

**Execution-Detailed Template:**
```
The code failed with a [error_type] on line [line_number].
Expected: [expected_value]
Actual: [actual_value]
Suggestion: Check the logic at line [line_number].
```

**AI-Critic Template:**
```
The code has the following issues:
[critic_generated_text]
Suggestion: [critic_suggestion]
```

This normalization preserves information content—error type, location, expected versus actual—while controlling for surface form.

## Counterfactual Information Measurement

To quantify the localization information in execution traces, we define a Counterfactual Score (CF-score) based on the presence of diagnostic elements:

$$\text{CF-score} = \frac{1}{4}\sum_{i} \mathbf{1}[\text{element}_i \text{ present}]$$

where elements are: (1) line number, (2) error type, (3) expected value, (4) actual value.

We parse all execution traces and compute CF-score distributions. A trace with CF-score ≥ 0.4 contains enough counterfactual information for targeted editing—at minimum, line number and error type.

## Edit Scope Classification

To test whether localized feedback enables targeted edits, we classify model outputs by edit scope:

| Scope | Definition |
|-------|------------|
| **Targeted** | ≤5 lines changed, concentrated at error location |
| **Local** | 6-15 lines changed |
| **Global** | >15 lines changed or complete rewrite |

We compute edit scope using line-level diff between original and refined code, tracking whether edits concentrate at the diagnosed bug location.

## Refinement Protocol

For all conditions, we use the same iterative refinement loop:

```
for iteration in 1..k:
    feedback = get_feedback(code, condition)
    code = model.refine(code, feedback)
    if passes_tests(code):
        return SUCCESS
return FAILURE
```

We fix k=3 iterations, temperature=0.2, and use CodeLlama-7B-Instruct as the base model. This controls for refinement dynamics while isolating feedback effects.

## Hypotheses and Tests

Our experimental design maps to a sequential hypothesis chain:

| Hypothesis | Test | Success Criterion |
|------------|------|-------------------|
| **H-M1:** Traces contain CF info | Parse traces, compute CF-score | >70% traces have CF ≥ 0.4 |
| **H-M2:** CF info → targeted edits | Compare edit scope by condition | Detailed produces smaller diffs |
| **H-M3:** Targeted → higher fix | Correlate scope with fix rate | Targeted > global fix rate |
| **H-C1:** Complexity interaction | Compare effect across benchmarks | Effect size × complexity |

Each hypothesis builds on the previous, forming a complete mechanism test. H-M1 establishes information availability, H-M2 establishes behavioral effect, H-M3 establishes outcome effect.

## Datasets and Metrics

**Benchmarks:**
- **HumanEval** (164 problems): Standard function-level code completion [Chen et al., 2021]
- **MBPP** (500 problems): Higher complexity Python programming [Austin et al., 2021]

**Primary Metric:** pass@1 after k=3 refinement iterations

**Secondary Metrics:**
- Refinement efficiency: iterations to first success
- Edit scope distribution by condition
- CF-score distribution by error type

## Implementation

We implement the feedback collection and refinement loop in Python, using:
- Docker containers for sandboxed execution
- pytest with captured output for error traces
- Template-based NL conversion for format normalization
- AST-based diff analysis for edit scope classification

All code and experiments are reproducible with fixed random seeds.
