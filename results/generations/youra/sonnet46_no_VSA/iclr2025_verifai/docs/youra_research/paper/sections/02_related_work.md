# 2. Related Work

Our work sits at the intersection of three research streams: LLM code evaluation, property-based testing for code verification, and formal contract checking. We organize prior work to show how each stream is insufficient on its own — and how our approach fills the resulting gap.

## 2.1 LLM Code Evaluation: From Sparse to Dense Testing

The HumanEval benchmark [Chen2021HumanEval] established functional correctness via unit tests as the primary evaluation axis for LLM-generated code, measured by pass@k. Subsequent work recognized that sparse test suites allow test-gaming: LLM programs can pass by memorizing output patterns for common inputs rather than implementing correct logic.

EvalPlus [Liu2023EvalPlus] addressed this directly by expanding HumanEval by 80× and MBPP by 35×, reducing pass@1 by up to 23.1%. This dense differential testing approach — evaluating functional equivalence to a reference implementation on a large fixed input set — represents the current gold standard for test-based LLM code evaluation.

However, differential testing is fundamentally limited to checking *output equality on sampled inputs*. It cannot check whether a program satisfies properties that must hold for all valid inputs: relational invariants, quantified conditions, or semantic contracts that specify behavior beyond input-output pairs. Our work builds on EvalPlus as the strongest available test-based baseline and quantifies how much weaker it is than a formal contract oracle.

## 2.2 Property-Based Testing for LLM Code

Property-based testing (PBT) generates random inputs satisfying preconditions and verifies that postconditions hold — approaching specification checking without requiring explicit test cases.

Bose [Bose2025Prompts] applied PBT (Hypothesis-style) to StarCoder and CodeLlama on MBPP and HumanEval, finding that 18–32% of programs fail outright and 30–32% only partially adhere. This work demonstrates that PBT reveals violations missed by unit testing — the same direction as our hypothesis. However, it covers only two models, uses no formal contract annotations (postconditions are manually authored rather than benchmark-provided), and lacks the oracle isolation design needed to separate input-generation advantage from oracle semantic strength.

Newcomb et al. [Newcomb2025Preconditions] examined how pre/postcondition constraints provided as prompts affect LLM code generation quality, showing that structural constraints improve correctness. This complements our work: where they study contract-guided generation, we study contract-based evaluation of existing outputs.

**Limitation of prior PBT work:** None of these studies answer whether the additional violations PBT finds reflect *oracle semantic strength* (the contract checks something the differential oracle cannot) or *input exploration advantage* (PBT finds more failing inputs of the same kind). Our oracle isolation design (Section 3) resolves this directly.

## 2.3 Formal Contract Checking for LLM Code

ContractEval [Lim2025ContractEval] is the only publicly available benchmark pairing HumanEval+/MBPP+ tasks with formal Python pre/post-condition contracts (inline `assert` statements). Their evaluation found 0% contract satisfaction for 5 open-source models under standard prompting; even with explicit contracts in the prompt, satisfaction reaches only 23–41%.

Critically, ContractEval uses a neuro-symbolic pipeline for test synthesis: Z3 SMT checking of negated postconditions. This limits tractability to 25.82% of tasks (73.9% of ContractEval contracts use Python-native constructs — list comprehensions, string operations, complex data structures — outside Z3's efficiently decidable fragment). Our prior work (h-e1) confirmed this tractability ceiling: Z3 found violations in only 7.42% of the tractable subset. Execution-based checking removes this ceiling entirely.

The ContractEval paper does not measure oracle strength relative to differential testing, nor does it apply adaptive PBT. It answers "do models satisfy contracts?" — we answer "by how much do contracts exceed differential oracles?"

**Positioning:** Our work uniquely combines (1) formal contract annotations (ContractEval), (2) execution-based checking (100% tractable), (3) oracle isolation design (same inputs, different oracle), and (4) adaptive PBT contribution measurement — across 5 model families including closed-source models absent from all prior contract evaluation work.

## 2.4 Supporting Context

OpenAI's Code Monitor findings (2026) — that 52.9% of test-passing programs fail hidden correctness checks at production scale — provide external validation that the test-pass→specification-satisfaction gap exists at scale beyond benchmark settings [OAI2026Monitor].

Liguori et al. [Liguori2026Factors] showed that model size and data quality explain 83% of functional correctness variance, supporting our finding that after controlling for pass@1* and model size, model identity adds negligible variance to contract-satisfaction behavior (ΔR² = 0.004 in our regression).

## Summary

| Work | Oracle Type | Models | Oracle Isolation | Contract Annotations |
|------|-------------|--------|------------------|---------------------|
| EvalPlus [Liu2023EvalPlus] | Differential (dense) | Multiple | — | None |
| Bose [Bose2025Prompts] | PBT (no formal contracts) | 2 | No | Manual |
| ContractEval [Lim2025ContractEval] | SMT (25.82% tractable) | 5 (open) | No | Formal (benchmark) |
| Newcomb et al. [Newcomb2025Preconditions] | Test-based | Multiple | No | Prompt-provided |
| **This work** | **Execution-based contract (100% tractable)** | **5 (open+closed)** | **Yes (CVT design)** | **Formal (ContractEval)** |

No prior work combines formal contract annotations, execution-based tractability, oracle isolation design, and cross-model evaluation across open and closed LLM families.
