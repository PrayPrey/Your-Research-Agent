# SpecBridge: Specification Inference from Natural Language for LLM Code Generation Verification

This repository contains the experimental implementation of SpecBridge, a two-stage framework that automatically infers formal specifications from natural language requirements and uses these specifications to guide and verify LLM-generated code.

## Overview

SpecBridge addresses a critical gap in verifying LLM-generated code: while formal verification tools require precise specifications, users typically describe their intent in ambiguous natural language. The framework consists of:

1. **Specification Inference Module**: Translates natural language requirements into formal specifications (pre/post-conditions)
2. **Consistency Checking Module**: Validates generated specifications using ensemble disagreement detection
3. **Guided Code Generation Module**: Uses specifications to guide LLM code generation
4. **Verification and Refinement Module**: Verifies code against test cases with counterexample-guided refinement

## Project Structure

```
claude_code/
├── config.py           # Configuration parameters
├── data.py             # Benchmark dataset with 30 coding problems
├── model_wrapper.py    # HuggingFace model wrapper
├── spec_inference.py   # Specification inference module
├── code_generation.py  # Code generation module (baseline and spec-guided)
├── verification.py     # Code verification module
├── run_experiment.py   # Main experiment runner
├── visualize.py        # Result visualization
├── outputs/            # Raw experiment outputs
└── README.md           # This file
```

## Requirements

- Python 3.8+
- PyTorch with CUDA support
- HuggingFace Transformers
- Required packages: `torch`, `transformers`, `matplotlib`, `numpy`

## Running the Experiment

1. **Set up environment**:
   ```bash
   pip install torch transformers matplotlib numpy
   ```

2. **Run the main experiment**:
   ```bash
   CUDA_VISIBLE_DEVICES=0 python run_experiment.py
   ```

3. **Generate visualizations**:
   ```bash
   python visualize.py outputs
   ```

## Methods Compared

1. **Baseline (Direct LLM)**: Standard LLM code generation without specifications
2. **SpecBridge Static**: Specification-guided generation without refinement
3. **SpecBridge Dynamic**: Specification-guided generation with counterexample-based refinement

## Evaluation Metrics

- **Success Rate**: Percentage of problems where generated code passes all test cases
- **Pass Rate**: Average percentage of test cases passed per problem
- **Specification Quality**: Accuracy of inferred specifications
- **Ambiguity Detection**: Effectiveness of ensemble disagreement in detecting ambiguous requirements

## Results Summary

| Method | Success Rate | Avg Pass Rate | Avg Time |
|--------|-------------|---------------|----------|
| Baseline | **43.3%** | **50.0%** | **0.90s** |
| SpecBridge Static | 26.7% | 32.5% | 3.94s |
| SpecBridge Dynamic | 30.0% | 38.3% | 13.00s |

Key findings:
- The baseline outperformed SpecBridge methods on our benchmark
- High ensemble disagreement (90% ambiguous) suggests specification inference challenges
- SpecBridge Dynamic showed marginal improvement over Static with significant time overhead

See `../results/results.md` for detailed analysis.

## Citation

This implementation is based on the research proposal:
"SpecBridge: Specification Inference from Natural Language for LLM Code Generation Verification"
