# Human Review Notes - Round 1

> Minor issues for human review during final polish (NOT auto-fixed)

## Typos and Grammar

*None identified in this round*

## Style and Clarity

- **Location:** Line 10 (Abstract)
  **Type:** style
  **Note:** "95th percentile error" → "P95 error" for consistency with rest of paper

- **Location:** Line 22 (Intro)
  **Type:** formatting
  **Note:** "factorization into model parameters (M_param), gradients (M_grad)..." → italics inconsistent, use math mode or remove

- **Location:** Line 54 (Related Work)
  **Type:** clarity
  **Note:** "VeritasEst's 2-iteration protocol samples memory after the first forward pass and again after the second full training iteration" → wordy, consider "samples memory after iteration 1 forward pass and iteration 2 completion"

- **Location:** Line 224 (Exp Setup)
  **Type:** formatting
  **Note:** "torch.cuda.max_memory_allocated()" → code formatting missing (should be monospace in some contexts)

- **Location:** Line 298 (Results, Table 1)
  **Type:** clarity
  **Note:** Table formatting: consider adding units (MB) to column headers instead of repeating in every cell

- **Location:** Appendix C
  **Type:** clarity
  **Note:** Code snippet missing comments explaining timing-critical steps beyond "CRITICAL" comment

## Formatting

- **Location:** Line 89 (Method)
  **Type:** formatting
  **Note:** "Iteration 1: Forward-Only Pass" heading style inconsistent with rest of section (bold vs sentence case)

- **Location:** Line 142 (Method)
  **Type:** formatting
  **Note:** Timeline bullets use em-dash, other lists use bullet points—pick one style

- **Location:** Line 266 (Results)
  **Type:** missing element
  **Note:** "Figure 1: Memory Accuracy Comparison" → Figure caption not provided, only described in text

- **Location:** Line 274 (Results)
  **Type:** missing element
  **Note:** "Figure 2: Post-Optimizer Memory Timeline" → Figure caption not provided

- **Location:** Line 287 (Results)
  **Type:** missing element
  **Note:** "Figure 3: Error Distribution" → Figure caption not provided

- **Location:** Line 375 (Conclusion)
  **Type:** formatting
  **Note:** "Key references:" section has inconsistent citation format vs main text

---

**Total notes:** 12
**All are MINOR issues for final human polish phase**
