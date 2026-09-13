# Methodology

Our methodology directly tests the independence claim that underlies layered verification pipelines. We use Jaccard indices on improvement sets because this metric directly measures overlap between error classes—if two verification strategies improve largely disjoint sets of problems, they target independent error classes.

## Error Class Independence Measurement

### Problem Formulation

For a code generation benchmark with problems $P = \{p_1, ..., p_n\}$, each verification strategy $s$ produces an improvement set $I_s \subseteq P$ containing problems where strategy $s$ increases correctness.

We measure independence between strategies $s_1$ and $s_2$ using the Jaccard index:

$$J(s_1, s_2) = \frac{|I_{s_1} \cap I_{s_2}|}{|I_{s_1} \cup I_{s_2}|}$$

**Interpretation:**
- $J = 0$: Complete independence (disjoint improvement sets)
- $J = 1$: Complete overlap (identical improvement sets)
- $J < 0.30$: Largely independent (our threshold for multiplicative model)

### Strategy Definitions

We define three verification strategies corresponding to different error classes:

**Grammar Constraints ($s_g$):** Token-level logit masking via deterministic finite automaton (DFA). Uses SynCode in grammar_strict mode with Python grammar. Improvement: problem passes after constrained generation when it failed with unconstrained baseline.

**Static Analysis ($s_a$):** AST-level pattern matching using Bandit (security) and Pylint (reliability). Improvement: code has fewer static analysis issues after feedback-based refinement.

**SMT Verification ($s_m$):** Formal specification checking using Z3 on HumanEval-Verus problems (23 problems with Verus specifications). Improvement: code satisfies formal specification after SMT-guided repair.

### Evaluation Protocol

For each strategy pair, we compute:
1. Generate baseline code for all problems
2. Apply each strategy independently
3. Identify improvement sets $I_{s_g}$, $I_{s_a}$, $I_{s_m}$
4. Compute pairwise Jaccard indices

We test across two models (CodeLlama-7b-hf, GPT-4) to verify independence holds across capability levels.

## Pipeline Architecture

Building on the independence framework, we design a sequential pipeline ordered by abstraction level:

```
[Raw LLM Code]
    ↓
[Stage 1: Grammar Constraints]
    - Mechanism: Token-level logit masking via DFA
    - Targets: Syntax errors (compilation failures)
    ↓
[Stage 2: Static Analysis]
    - Mechanism: AST-based pattern matching + LLM repair
    - Targets: Semantic issues (security, reliability)
    ↓
[Stage 3: SMT Verification]
    - Mechanism: Z3 constraint solving + guided repair
    - Targets: Specification violations
```

**Rationale for ordering:** Lower abstraction levels (syntax) should be resolved before higher levels (semantics, specifications), as syntactically invalid code cannot be meaningfully analyzed for semantic issues.

## Hypothesis Testing

We decompose the main hypothesis (multiplicative error reduction) into testable sub-hypotheses:

**H-E1 (Existence):** Error classes are largely independent (Jaccard < 0.30 for all strategy pairs).

**H-M1 (Mechanism):** Grammar-constrained decoding reduces syntax errors by measurable margin through prefix automata enforcement.

**H-M2 (Mechanism):** Static analysis feedback reduces semantic issues when using instruction-tuned models.

**H-M3 (Mechanism):** SMT-guided repair enforces specification satisfaction on semantically-filtered code.

**H-M4 (Mechanism):** Pipeline composition achieves synergy coefficient $S \geq 0.8$, where:
$$S = \frac{\text{Combined improvement}}{\sum \text{Individual improvements}}$$

This decomposition allows partial validation—if one mechanism stage fails, we can identify the specific failure mode rather than rejecting the entire hypothesis.

## Experimental Design Choices

**Jaccard over raw counts:** Raw error counts confound strategy effectiveness with baseline error rates. Jaccard on improvement sets directly measures overlap.

**Sequential pipeline:** We test the natural ordering (syntax → semantics → specifications). Alternative orderings could be tested in future work.

**HumanEval + HumanEval-Verus:** HumanEval (164 problems) enables broad testing; HumanEval-Verus (23 problems with specifications) enables SMT stage evaluation.

**Two models:** CodeLlama-7b-hf (open-source, 7B parameters) and GPT-4 (frontier, API-based) span the capability spectrum, testing whether independence holds across model sizes.
