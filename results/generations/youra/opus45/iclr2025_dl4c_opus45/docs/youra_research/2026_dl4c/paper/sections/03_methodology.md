# Methodology

Our methodology is designed to test whether alignment method choice creates predictable differences in error type distributions. We employ a hierarchical hypothesis structure: first establishing that differences exist (existence test), then validating specific mechanistic predictions (mechanism tests). This design ensures we do not pursue mechanism analysis without first confirming the phenomenon.

## Overview

Building on our observation that binary execution reward creates a zero-reward basin while preference optimization lacks execution feedback, we design experiments to test four predictions:

1. **Existence (H-E1):** Error type distributions differ significantly between RL and DPO aligned models
2. **Mechanism 1 (H-M1):** RL's zero-reward basin concentrates failures in assertion errors
3. **Mechanism 2 (H-M2):** RL produces deeper execution before failure (syntactic validity pressure)
4. **Mechanism 3 (H-M3):** The effect persists and amplifies at fine-grained taxonomy levels

Each hypothesis has a defined gate type: H-E1 is MUST_WORK (failure terminates the study), while mechanism hypotheses are SHOULD_WORK (failure informs but does not invalidate the existence finding).

## Models and Datasets

### Models

We compare two models representing distinct alignment approaches:

**RL-Aligned: CodeRL (770M parameters)**
- Architecture: CodeT5-large encoder-decoder [Wang et al., 2021]
- Alignment: Execution-based RL with binary pass/fail reward
- Training: Actor-critic approach on APPS benchmark
- Source: Salesforce/codet5-large-ntp-py

**DPO-Aligned: CodeLlama-Instruct (7B parameters)**
- Architecture: Llama 2 decoder-only [Touvron et al., 2023]
- Alignment: Instruction tuning with preference data (no execution feedback)
- Training: SFT + RLHF on general instruction-following
- Source: codellama/CodeLlama-7b-Instruct-hf

**Design Rationale:** We intentionally use existing models rather than controlled training from a shared base. This is a conservative test: if alignment-induced error divergence exists despite architecture and scale confounds, it represents a robust phenomenon. Model differences (encoder-decoder vs. decoder-only, 770M vs. 7B parameters) make our hypothesis harder to confirm, not easier.

### Datasets

We evaluate on HumanEval+ and MBPP+ from the EvalPlus benchmark [Liu et al., 2023]:

- **HumanEval+:** 164 programming problems with 80x augmented test coverage
- **MBPP+:** 378 programming problems with 35x augmented test coverage
- **Total:** 542 problems

The augmented test coverage is critical: it increases the likelihood of detecting assertion errors (code that passes original tests but fails augmented ones), which is central to our hypothesis about RL error concentration.

### Generation Protocol

For each model and problem, we generate n=10 samples at temperature T=0.8 with top-p=0.95, yielding 5,420 samples per model. We use greedy decoding seeds for reproducibility.

## Error Classification

We employ a two-tier classification scheme:

### Coarse Classification (3 categories)

Based on execution semantics:
- **Syntax Error:** Code fails to parse (SyntaxError, IndentationError)
- **Runtime Error:** Code parses but fails during execution (NameError, TypeError, ZeroDivisionError, etc.)
- **Assertion Error:** Code executes completely but produces incorrect output (AssertionError)

Classification is automated via error message parsing—each Python exception type maps deterministically to a category.

### Fine-Grained Classification (19 causes)

We apply the LlmFix taxonomy [Zhang et al., 2024] for detailed analysis:
- Syntax tier: indentation_error, syntax_error, incomplete_code, ...
- Runtime tier: name_error, type_error, attribute_error, index_error, ...
- Assertion tier: wrong_output, off_by_one, incorrect_algorithm, ...

The fine-grained classification tests effect persistence: a genuine alignment-induced signature should manifest at multiple granularities, not disappear under refinement.

## Statistical Framework

### H-E1: Chi-Square Test for Independence

We test whether error type distribution is independent of alignment method using Pearson's chi-square test on the 2×3 contingency table (alignment_method × error_type):

$$\chi^2 = \sum_{i,j} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$$

**Success criterion:** p < 0.05 (reject independence)

### Effect Size: Cramér's V

To quantify effect magnitude independent of sample size:

$$V = \sqrt{\frac{\chi^2}{n \cdot \min(k-1, r-1)}}$$

where n is total observations, k is number of columns, r is number of rows.

**Interpretation:** V < 0.1 (negligible), 0.1-0.3 (small), 0.3-0.5 (medium), > 0.5 (large)

**Success criterion:** V > 0.05 (non-negligible effect)

### H-M1: Fisher's Exact Test

For the 2×2 table (alignment × assertion/non-assertion), we use Fisher's exact test due to small expected cell counts:

**Success criterion:** p < 0.05, one-sided (RL > DPO assertion proportion)

### H-M2: Welch's t-Test on Execution Depth

Execution depth is measured as (lines executed before failure) / (total lines in solution). We trace execution using Python's sys.settrace() to count executed lines.

$$t = \frac{\bar{X}_{RL} - \bar{X}_{DPO}}{\sqrt{\frac{s_{RL}^2}{n_{RL}} + \frac{s_{DPO}^2}{n_{DPO}}}}$$

**Success criterion:** p < 0.05, one-sided (RL > DPO mean depth)

**Effect size:** Cohen's d for practical significance

$$d = \frac{\bar{X}_{RL} - \bar{X}_{DPO}}{s_{pooled}}$$

### H-M3: Multi-Granularity Cramér's V

We compute Cramér's V at both coarse (3-tier) and fine (19-cause) granularities to test effect persistence:

**Success criterion:** V > 0.03 at fine-grained level

## Hierarchical Dependency Structure

The hypotheses form a logical chain:

```
H-E1 (Existence) ──MUST_WORK──► Continue
        │
        ▼
H-M1 (Zero-reward basin) ──SHOULD_WORK──► H-M2
        │
        ▼
H-M2 (Execution depth) ──SHOULD_WORK──► H-M3
        │
        ▼
H-M3 (Taxonomy persistence) ──SHOULD_WORK──► Synthesis
```

If H-E1 fails, the entire study terminates—mechanism analysis is meaningless without an existence result. Mechanism hypothesis failures inform interpretation but do not invalidate prior results.
