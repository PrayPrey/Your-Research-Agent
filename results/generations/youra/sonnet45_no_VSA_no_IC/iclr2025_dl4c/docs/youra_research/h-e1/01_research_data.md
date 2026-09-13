# Research Data: h-e1

**Generated:** 2026-08-19 (Phase 1 output stub)
**Hypothesis:** Binary feedback achieves dual-threshold sufficiency: ≥8 pp absolute improvement over SFT baseline AND ≥80% relative retention of error-type feedback gains on HumanEval for 350M-1B models

---

## Research Question

Can binary execution feedback (pass/fail) achieve sufficient training signal for small code language models (350M-1B parameters) compared to fine-grained error-type feedback?

---

## Literature Summary

### Key Papers

**1. RLVR for Small Models (2024)**
- **Finding:** Qwen3-0.6B + binary unit-test feedback achieved +13 pp pass@1 on MBPP using GRPO
- **Relevance:** Directly validates binary feedback effectiveness for <1B models

**2. MURPHY Multi-turn Feedback (2024)**
- **Finding:** Quantitative pass rate feedback + qualitative error messages achieved +8% relative gain over GRPO baseline on HumanEval
- **Relevance:** Establishes comparison baseline for error-type feedback

**3. LETI Textual Feedback Learning (2024)**
- **Finding:** Textual feedback (stack traces, error messages) achieved same performance as binary with <50% gradient steps
- **Relevance:** Shows feedback granularity trade-offs for training efficiency

**4. PRLCoder Process Supervision (2024)**
- **Finding:** Line-by-line process rewards improved stability +5.1% over outcome-supervised RL on MBPP+
- **Relevance:** Granular feedback baseline for comparison

**5. HumanEval (Austin et al. 2021)**
- **Finding:** 164 hand-written Python problems with comprehensive test suites
- **Relevance:** Standard benchmark for code generation with binary pass/fail evaluation

---

## Datasets

**Name:** HumanEval
**Source:** OpenAI (github.com/openai/human-eval)
**Size:** 164 problems
**Task:** Python function generation from docstrings
**Split:** Test only (no train split)
**Evaluation:** Binary pass/fail via unit test execution

---

## Models

**CodeGen-350M-mono** (Salesforce)
- 350M parameters
- Pre-trained on BigPython
- Context: 2048 tokens

**StarCoderBase-1B** (BigCode)
- 1B parameters
- Pre-trained on The Stack v1.2 (80+ languages)
- Context: 8192 tokens

---

## Research Gap

Existing work shows binary feedback works for small models (<1B), but no direct comparison quantifying retention percentage vs error-type feedback on same models/data.

---

*Phase 1 output stub - full research conducted in Phase 2C Exa searches*
