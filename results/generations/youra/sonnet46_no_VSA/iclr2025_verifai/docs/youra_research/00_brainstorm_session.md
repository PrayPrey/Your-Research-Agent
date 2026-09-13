---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Runtime Contract Verification for LLM Code Gen"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-03
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Bridging formal verification and LLM code generation — specifically how execution-based / runtime contract verification (avoiding SMT encoding bottlenecks) can reveal gaps between test-passing and specification-compliant LLM-generated code on existing benchmarks

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This workshop (VerifAI: AI Verification in the Wild, ICLR 2025) explores the intersection of scale-driven generative AI and correctness-focused formal verification. Formal analysis tools (theorem provers, satisfiability solvers, execution monitoring) have demonstrated success in software verification but face scaling challenges. LLMs offer scalable adaptability but are probabilistic — not correct by construction. The special theme focuses on LLMs for code generation and how programming language / formal methods techniques (context-free grammars, static analyzers, SMT-guided repair) can enhance LLM-driven code generation.

Source Type: Workshop CFP / Structured Input. **Retrying after previous failure** (h-e1: Z3+ContractEval tractability gate FAIL).

---

## Lessons from Previous Attempts

### What Was Tried Before

**Hypothesis h-e1 (Run 1):** Used Z3 SMT solver to check negated post-conditions of ContractEval contracts on HumanEval+/MBPP+ problems, seeking evidence that contracts are strictly stronger than test coverage (programs passing tests but failing contracts).

**Results:**
- Contract strength ratio: 7.42% (>0 ✓) — concept valid, contracts DO catch test-passing failures
- Z3 tractability rate: 25.82% (required ≥50% ✗) — fundamental encoding incompatibility
- 73.9% of ContractEval problems were unencodeable in Z3's linear arithmetic fragment

### Why It Failed

1. ContractEval contracts use Python-native constructs (list comprehensions, string ops, complex data structures) that fall outside Z3's efficiently decidable fragment
2. Tractability gap (25.82% vs 50%) reflects structural incompatibility, not just timeout tuning
3. Assumption mismatch: contracts were richer Python expressions than SMT-LIB can represent

### How THIS Direction Avoids Those Pitfalls

The new direction **abandons SMT as the primary verification mechanism** and uses **execution-based / runtime contract checking** instead:
- Python-native contract languages (ContractEval, icontract, CrossHair-style) are evaluated by Python execution, not SMT encoding → 100% tractability by construction
- Runtime fuzzing / property-based testing (Hypothesis library) natively handles complex Python types
- The core insight from h-e1 **is preserved**: strength ratio 7.42% confirmed contracts catch what tests miss — now we measure this efficiently via execution
- Avoids Z3, avoids tractability gates, avoids SMT encoding

---

## Session Plan

ROUTE_TO_0 Auto-extraction: applied lessons from h-e1 failure to current VerifAI CFP input. New direction pivots from SMT verification to execution-based contract verification while preserving the valid core finding (formal contracts > test coverage).

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Failure context synthesis applied.

---

## Research Question Development

### Initial Question

Do runtime / execution-based contract verification approaches (property-based testing, assertion checking, CrossHair-style symbolic execution) reveal larger gaps between test-passing and contract-compliant LLM-generated code than SMT-based approaches, on existing ContractEval / HumanEval+ / MBPP+ benchmarks?

### Refined Question

When LLM-generated code is evaluated against formal contracts using execution-based verification (property-based testing via Hypothesis, runtime assertion checking, CrossHair concolic execution) on existing benchmarks (ContractEval subset of HumanEval+/MBPP+), what fraction of test-passing programs fail at least one formal contract, and how does this contract-strength gap vary across LLM model families (open vs. closed, small vs. large)?

### Detailed Sub-Questions

1. On the ContractEval-encoded subset of HumanEval+/MBPP+, what fraction of LLM-generated programs pass all unit tests but violate at least one formal pre/post-condition when checked via Python runtime assertion execution (not Z3)?
2. Does property-based testing via Hypothesis (random input generation against contract assertions) find more contract violations per problem than direct unit-test execution alone on existing benchmarks?
3. Does the contract-strength gap (test-pass-but-contract-fail rate) differ significantly across model families — e.g., GPT-4o, Claude 3.5, DeepSeek-Coder, CodeLlama — on the same ContractEval problems?
4. Are certain contract types (pre-conditions, post-conditions, invariants) more commonly violated by LLM-generated code than others, using runtime checking on existing ContractEval annotations?
5. Does model size (7B vs 13B vs 70B) correlate with contract violation rate independent of test-pass rate on existing HumanEval+/MBPP+ benchmarks with ContractEval annotations?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 VerifAI workshop) — significance pre-validated. The question directly addresses the workshop's "AI as verifiers" and "formal methods for generative AI" tracks. The core finding (formal contracts reveal failures tests miss) is novel and practically important: if LLM-generated code systematically violates contracts even when tests pass, this motivates contract-aware training, sampling, and filtering. Results on existing benchmarks are immediately comparable to prior work. Previous h-e1 confirmed strength ratio 7.42% > 0, so the effect is real — this run just measures it efficiently.

### Feasibility Check

All sub-questions testable immediately using:
- **Existing benchmarks:** ContractEval annotations on HumanEval+/MBPP+ (publicly available)
- **Existing tools:** Python `assert` execution, Hypothesis library (pip install), CrossHair (pip install)
- **Existing models:** GPT-4o API, Claude 3.5 API, DeepSeek-Coder (HuggingFace), CodeLlama (HuggingFace)
- **Metrics:** Contract violation rate, contract-strength ratio — fully automated, no human eval
- **No new benchmarks required** — ContractEval already annotates HumanEval+/MBPP+
- **No synthetic data** — uses existing ground-truth contracts
- **No human annotation** — runtime execution is deterministic
- Feasibility: **HIGH** (higher than h-e1 because execution-based checking has no tractability ceiling)

---

## Phase 1 Input Package

<phase1-input>

### research_question
When LLM-generated code is evaluated against formal contracts using execution-based verification (property-based testing via Hypothesis, runtime assertion checking, CrossHair concolic execution) on existing benchmarks (ContractEval subset of HumanEval+/MBPP+), what fraction of test-passing programs fail at least one formal contract, and how does this contract-strength gap vary across LLM model families (open vs. closed, small vs. large)?

### detailed_question
1. On the ContractEval-encoded subset of HumanEval+/MBPP+, what fraction of LLM-generated programs pass all unit tests but violate at least one formal pre/post-condition when checked via Python runtime assertion execution (not Z3)?
2. Does property-based testing via Hypothesis (random input generation against contract assertions) find more contract violations per problem than direct unit-test execution alone on existing benchmarks?
3. Does the contract-strength gap (test-pass-but-contract-fail rate) differ significantly across model families — e.g., GPT-4o, Claude 3.5, DeepSeek-Coder, CodeLlama — on the same ContractEval problems?
4. Are certain contract types (pre-conditions, post-conditions, invariants) more commonly violated by LLM-generated code than others, using runtime checking on existing ContractEval annotations?
5. Does model size (7B vs 13B vs 70B) correlate with contract violation rate independent of test-pass rate on existing HumanEval+/MBPP+ benchmarks with ContractEval annotations?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- h-e1 proved the core concept: formal contracts catch test-passing failures (7.42% strength ratio > 0). The effect is real.
- The failure was in the verification mechanism (Z3), not the research question — execution-based checking fixes this without changing the scientific question
- ContractEval already provides Python-native pre/post-conditions suitable for runtime assertion checking, so tractability is 100% by construction
- Cross-model comparison (open vs. closed, scale) adds contribution without extra benchmark cost and directly answers "which LLMs respect formal specs better"
- Hypothesis property-based testing as a sub-question is novel: it generates adversarial inputs against contracts, potentially finding more violations than fixed unit tests

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode: failure context synthesis from Serena Memory (h-e1 run1) + current VerifAI CFP input

### Areas for Further Exploration

- SMT-hybrid: use Z3 only for arithmetic-only contract subset (where tractability was 27%) — deferred, lower priority
- Grammar-constrained decoding for syntactic correctness — separate angle, not pursued here to avoid scope creep
- LLM-as-verifier (probabilistic soft assurance) — adjacent VerifAI angle, possible future work
- Formal specification generation from docstrings — orthogonal to current question

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Search for:
1. ContractEval paper and dataset access (existing annotations on HumanEval+/MBPP+)
2. Prior work on test-passing-but-specification-failing programs in LLM code gen
3. Property-based testing (Hypothesis) applied to LLM-generated code verification
4. CrossHair / concolic execution for Python contract checking
5. Cross-model comparisons on code correctness benchmarks (beyond pass@k)

Key gap to confirm in Phase 1: has execution-based contract strength been measured across multiple LLM families on ContractEval? If not, that's the contribution.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
