# Methodology

## Error Categorization

Python exceptions naturally partition into categories with different traceback reliability. Following RLTF's categorization, we distinguish:

**U_line errors** include SyntaxError, IndentationError, NameError, TypeError, AttributeError, KeyError, IndexError, ValueError, and ZeroDivisionError. These exceptions report the exact line where the error occurs—the traceback line matches the bug location with 100% accuracy in our measurements (Figure 1).

**U_ignore errors** include RuntimeError, RecursionError, MemoryError, TimeoutError, and AssertionError. These exceptions often report symptom lines rather than root causes. A RecursionError traceback shows the final recursive call, not the missing base case. Our measurements show only 20% localization accuracy for this category.

![Localization accuracy by error type](figures/accuracy_bar.png)
*Figure 1: Localization accuracy by error category. U_line errors have 100% traceback accuracy; U_ignore errors have only 20% accuracy (chi-square p=9.57×10⁻⁷⁴).*

## Gating Mechanism

Standard RLTF applies fine-grained penalties to all errors with traceback information. For a generated code sequence with error at line ℓ, tokens at line ℓ receive penalty -1.0 while other tokens receive -0.1:

```
r_fine(token_i) = -1.0 if line(token_i) == ℓ else -0.1
```

Our gated approach conditions this on error type:

```
r_gated(token_i, error_type) = 
    r_fine(token_i)   if error_type ∈ U_line
    r_coarse          if error_type ∈ U_ignore
```

For U_line errors, we preserve the standard fine-grained penalty. For U_ignore errors, we apply only the coarse reward signal, avoiding potentially misleading token-level penalties.

## Connection to Gradient Concentration

Fine-grained penalties create gradient concentration at penalized tokens. Figure 2 shows that under standard RLTF, gradient magnitude at error-line tokens is 16.11× higher than at other tokens—the mechanism works as intended.

![Gradient concentration at error line](figures/gradient_comparison.png)
*Figure 2: Gradient magnitude at error-line tokens vs non-error tokens. Fine-grained penalties create 16.11× concentration ratio (p<10⁻²⁷⁰).*

The problem arises when this concentration occurs at wrong locations. For U_ignore errors, the 16× gradient signal points to symptom tokens rather than cause tokens 80% of the time. This misdirected signal acts as noise relative to ground-truth error locations.

## Implementation

We modify the RLTF reward computation to check error type before applying fine-grained penalties:

1. Execute generated code in sandbox
2. If error occurs, parse traceback for exception type and line number
3. Classify exception type as U_line or U_ignore
4. Apply fine-grained penalty only if U_line; otherwise coarse-only

The categorization lookup is O(1)—a simple set membership check. The gating decision adds negligible overhead to training.

## Design Rationale

We chose binary gating (apply/don't apply) over continuous weighting for simplicity and interpretability. The 100% vs 20% accuracy gap suggests that U_line and U_ignore represent categorically different reliability levels rather than a smooth gradient. However, we note that continuous weighting based on per-exception-type accuracy estimates is a natural extension for future work.
