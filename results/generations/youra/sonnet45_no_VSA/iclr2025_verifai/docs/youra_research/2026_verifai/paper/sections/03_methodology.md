# 3. Methodology

## 3.1 Three-Dimensional Feedback Decomposition

Verifier feedback naturally decomposes into three informational dimensions based on SMT solver output structure:

**Dimension 1: Witness Instantiation** provides concrete counterexamples from failed proofs, exposing specific input values violating assertions. These witnesses show *where* specifications fail with concrete repair targets (e.g., "precondition violated when x = -5").

**Dimension 2: Logical Structure** categorizes proof obligations by type—precondition failures, postcondition failures, loop invariant violations, bounds checks, null dereferences. This dimension shows *what* needs proving by localizing failure categories.

**Dimension 3: Dependency Preservation** extracts inter-specification dependencies and clause relationships from proof dependency graphs. This dimension shows *why* proofs fail by revealing causal chains (e.g., "postcondition P fails because loop invariant I is too weak, which depends on precondition Q").

These three dimensions encode complementary, non-redundant information validated by additive discharge rate gains (H-M1): RawError 31.9% → TagOnly 44.8% (+12.9pp) → ObligationSlice 55.1% (+10.3pp) → FullStructured 70.1% (+15.0pp).

## 3.2 Eight-Primitive Semantic Normalization

Program verifiers share semantic foundation rooted in first-order logic + theories (SMT-LIB), enabling minimal universal taxonomy:

1. MISSING_PRECONDITION: Under-specification of entry conditions
2. POSTCONDITION_FAILURE: Under-specification of exit guarantees
3. LOOP_INVARIANT_VIOLATION: Under-specification of inductive invariants
4. BOUNDS_CHECK_FAILURE: Array/memory safety violations
5. ARITHMETIC_OVERFLOW: Numeric safety violations
6. NULL_DEREFERENCE: Pointer safety violations
7. TERMINATION_FAILURE: Liveness violations
8. TYPE_MISMATCH: Type system violations

This taxonomy achieves 100% coverage across Frama-C, Dafny, and Why3 error categories (H-E2) because verifier differences are primarily syntactic (keywords, annotation styles) rather than semantic (proof obligation structures).

## 3.3 Iterative Refinement Algorithm

The refinement loop operates as follows:

```
1. LLM generates initial specification (zero-shot or few-shot)
2. Verifier attempts proof, returns structured feedback
3. Semantic normalization maps feedback to universal primitives
4. LLM refines specification using normalized feedback signals
5. Repeat 2-4 until proof discharge or iteration budget exhausted
```

Key design decision: **complete synthesis** (all components simultaneously) outperforms sequential staging (types→pre→post→inv) by 3.1pp with 4× fewer iterations (H-M2), because specification components have bidirectional dependencies requiring joint optimization.
