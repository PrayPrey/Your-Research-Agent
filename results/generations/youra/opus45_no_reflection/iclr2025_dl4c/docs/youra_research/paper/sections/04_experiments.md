# Experimental Setup

## Research Question

We aim to answer: **Can EVAF produce filtered AI feedback with accept rate in the viable 20-60% range?** This is a proof-of-concept existence test. We do not compare EVAF to baselines—that requires first demonstrating the mechanism works.

## Dataset

**HumanEval** (Chen et al., 2021): 164 Python programming problems with function signatures, docstrings, and unit tests. Each problem includes approximately 7 test cases on average. We use the full test split via HuggingFace (`openai_humaneval`).

**Rationale**: HumanEval is the standard benchmark for code generation evaluation, with well-defined unit tests enabling execution-based verification. Its moderate size (164 problems) is tractable for proof-of-concept while providing sufficient statistical power.

## Models

### Baseline Generator

**CodeT5-770M** (Wang et al., 2021): Salesforce/codet5-large, 770M parameter encoder-decoder transformer pre-trained on code. Reference pass@1 on HumanEval: 15.5%. We use this model for baseline code generation.

**Configuration**: Deterministic generation with temperature=0.0, nucleus sampling disabled, random seed fixed at 42.

### Feedback Generator

**CodeLlama-7b-Instruct** (Rozière et al., 2023): codellama/CodeLlama-7b-Instruct-hf, 7B parameter decoder-only transformer fine-tuned for instruction following on code tasks.

**Configuration**: Temperature=0.2, max_tokens=512. Half-precision (float16) inference with automatic device placement.

**Prompt Template**:
```
The following code fails some tests:
```python
{failing_code}
```

Problem: {problem_prompt}

Explain what's wrong and provide a corrected version.
```

## Execution Environment

**Test Execution**: Subprocess isolation with 3.0-second timeout per test. Code is written to a temporary file and executed via `subprocess.run()` with restricted environment. No network access, limited filesystem access.

**Hardware**: Single NVIDIA GPU (specific model varies by available infrastructure). CPU fallback for CodeT5-770M if needed.

## Evaluation Protocol

### Pipeline Stages

1. **Baseline Generation**: Generate one code completion per HumanEval problem using CodeT5-770M.
2. **Failure Filtering**: Execute baseline code against unit tests. Filter to problems where baseline fails (expected: ~80-120 problems given 15.5% pass@1).
3. **EVAF Gating**: For each failing problem:
   - Generate AI critique using CodeLlama-7b-Instruct
   - Extract proposed fix from response
   - Execute fix against unit tests
   - Record accept/reject decision and reason
4. **Metrics Computation**: Aggregate results across all failing problems.

### Metrics

**Primary Metric**:
- **Accept Rate**: (suggestions passing tests) / (total suggestions)

**Secondary Metrics**:
- **Coverage**: (problems with extractable code) / (total failing problems)
- **Rejection Breakdown**: Distribution of rejection reasons (no code extracted, tests failed, timeout)

### Success Criteria

**Pass**: Accept rate between 20% and 60%
- Demonstrates EVAF filters meaningfully without discarding all AI feedback

**Fail (Low)**: Accept rate < 10%
- EVAF degenerates to pure execution feedback; AI provides no useful verified signal

**Fail (High)**: Accept rate > 90%
- Execution gating is unnecessary; AI feedback is already reliable

## Limitations of Experimental Design

This is an existence test with several limitations:

1. **Single model pair**: We test only CodeT5-770M + CodeLlama-7b-Instruct. Different models may yield different accept rates.

2. **No training**: We do not test whether verified feedback improves model learning—only whether the gating mechanism produces viable output.

3. **HumanEval only**: Results may not generalize to other benchmarks (MBPP, APPS) with different problem distributions.

4. **Inference-only**: Computational overhead of EVAF (2x inference + test execution) is not optimized.

These limitations are acceptable for a proof-of-concept. Comparative evaluation and training experiments are deferred to future work contingent on successful existence demonstration.
