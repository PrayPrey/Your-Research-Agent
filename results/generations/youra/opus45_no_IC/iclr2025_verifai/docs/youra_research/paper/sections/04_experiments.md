# Experimental Setup

We design experiments to answer three questions that directly test our hypothesis:

**RQ1:** Are error classes targeted by grammar constraints, static analysis, and SMT verification largely independent (Jaccard < 0.30)?

**RQ2:** Does grammar-constrained decoding measurably reduce syntax errors?

**RQ3:** Does static analysis feedback reduce semantic issues when applied iteratively?

## Datasets

**HumanEval** (Chen et al., 2021): 164 Python programming problems with function signatures and docstrings. Each problem includes test cases for functional correctness evaluation. We use HumanEval because it is the standard benchmark for code generation and enables comparison with prior work.

**HumanEval-Verus** (secure-foundations): 23 problems from HumanEval translated to include formal Verus specifications. This subset enables SMT verification stage evaluation—problems without specifications cannot be verified by SMT solvers.

| Dataset | Problems | With Specs | Use Case |
|---------|----------|------------|----------|
| HumanEval | 164 | No | Grammar + Static |
| HumanEval-Verus | 23 | Yes | SMT verification |

## Models

We evaluate across two models spanning the capability spectrum:

**CodeLlama-7b-hf** (Meta): 7B parameter open-source model trained on code. Represents accessible, locally-runnable code generation.

**GPT-4** (OpenAI): Frontier model accessed via API. Represents state-of-the-art capability.

For the grammar constraint experiments (H-M1), we use **StarCoder2-7b** (BigCode) to demonstrate the mechanism. For the static analysis feedback experiments (H-M2), we test **StarCoder2-3b** (BigCode) to investigate whether model instruction-tuning affects feedback loop effectiveness.

## Verification Strategy Implementations

**Grammar Constraints:** SynCode (structuredllm/syncode) with `grammar_strict` mode and Python grammar. Token-level logit masking via DFA ensures syntactic validity during generation.

**Static Analysis:** Bandit v1.7+ for security issues (SQL injection, command injection, hardcoded secrets) and Pylint for reliability issues (undefined variables, type errors). 

**SMT Verification:** Z3 solver with Verus specification checking. Applied only to HumanEval-Verus subset.

## Baselines

For each hypothesis, we compare against appropriate baselines:

**H-E1 (Independence):** No baseline—we measure absolute Jaccard values.

**H-M1 (Grammar):** Unconstrained generation with same model, temperature, and sampling.

**H-M2 (Static):** 
- Baseline: Code without feedback iterations
- Treatment: Code after up to 5 feedback iterations

## Evaluation Metrics

**Pass@k:** Proportion of problems solved within k attempts (k=1 for our PoC validation).

**Jaccard Index:** $J(s_1, s_2) = |I_{s_1} \cap I_{s_2}| / |I_{s_1} \cup I_{s_2}|$ for measuring error class overlap.

**Syntax Error Rate:** Proportion of generated samples that fail to compile.

**Security Issues:** Count of Bandit findings (high/medium severity).

**Reliability Issues:** Count of Pylint errors (E-codes).

## Implementation Details

**Generation Parameters:**
- Temperature: 0.2 (deterministic) for H-E1, 1.2 (elevated) for H-M1 to induce baseline errors
- Max tokens: 64-256 depending on problem
- Samples per problem: 10 for pass@k calculation

**Feedback Loop (H-M2):**
- Maximum iterations: 5
- Prompt format: Original prompt + generated code + static analysis issues
- Early termination: No remaining issues

**Compute Resources:** 
- H-M1/H-M2: Single NVIDIA GPU with 8-bit quantization
- H-E1: Simulated data for PoC (full execution deferred to Phase 5)

**PoC Scope:** Due to resource constraints, H-M1 validates on 5 prompts (not full HumanEval) and H-M2 on 8 prompts. This demonstrates mechanism effectiveness; full-scale validation is future work.
