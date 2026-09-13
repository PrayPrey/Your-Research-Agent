# Product Requirements Document: h-e1

**Date:** 2026-08-28
**Hypothesis:** Structured error format achieves statistically significant higher repair success rate than raw compiler output on HumanEval+ and MBPP+ benchmarks across CodeLlama-7B, CodeLlama-34B, and GPT-4
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

---

## Executive Summary

Validate that parsing compiler errors into structured format (line number, error type, message, code context) improves LLM code repair success compared to raw compiler output. This is a proof-of-concept experiment requiring no model training.

---

## Problem Statement

Raw compiler output is unstructured and verbose. LLMs must parse error location and type from free text. Hypothesis: explicit structured format reduces parsing burden and improves repair accuracy.

---

## Functional Requirements

### FR-1: Error Parser Module
Parse raw Python compiler/runtime output into structured format:
- Line number extraction
- Error type classification (SyntaxError, TypeError, NameError, AttributeError, etc.)
- Error message normalization
- Code context extraction (3 lines before/after error)

### FR-2: Prompt Formatters
Two prompt generation functions:
- `format_structured_prompt()`: Uses parsed StructuredError
- `format_raw_prompt()`: Uses raw compiler output (baseline)

### FR-3: Model Integration
Support three models:
- CodeLlama-7B-Instruct (HuggingFace)
- CodeLlama-34B-Instruct (HuggingFace)
- GPT-4 (OpenAI API)

### FR-4: Benchmark Evaluation
Evaluate on:
- HumanEval+ (164 problems, 80x test coverage)
- MBPP+ (399 problems, 35x test coverage)
Use evalplus library for execution and pass@k computation.

### FR-5: Repair Loop
For each problem:
1. Generate initial code
2. Execute against tests
3. If fail: parse error, generate repair prompt, regenerate
4. Repeat up to 5 repair attempts
5. Record pass@1 after each attempt

### FR-6: Metrics Collection
Track per model, per benchmark, per format:
- Pass@1 rate
- Repair success rate
- Average repair attempts to success
- Error type breakdown

### FR-7: Visualization
Generate comparison figures:
- Bar chart: Pass@1 by model and format
- Grouped bar: Repair success rate
- Error type heatmap

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Temperature 0.0 (greedy decoding)
- Fixed random seeds
- Deterministic evaluation order

### NFR-2: Resource Efficiency
- CodeLlama models: float16, device_map="auto"
- Batch size 1 for sequential evaluation
- Timeout 3.0s per test execution

### NFR-3: API Rate Limits
GPT-4 calls with exponential backoff retry.

---

## Success Criteria

**PoC Pass Condition:**
1. Code runs without error
2. `structured_pass@1 > raw_pass@1` for majority of model/benchmark combinations (at least 4 of 6)

---

## Dependencies

### External Libraries
- evalplus (benchmark evaluation)
- transformers (CodeLlama loading)
- openai (GPT-4 API)
- torch (GPU inference)

### Data Sources
- evalplus/humanevalplus (HuggingFace)
- evalplus/mbppplus (HuggingFace)

### API Keys
- OPENAI_API_KEY (for GPT-4)

---

## Out of Scope

- Model fine-tuning
- Custom datasets
- Multi-language support
- Production deployment
