# 2. Related Work

## Verification-in-Loop Systems

AutoSpec+ [1] demonstrated iterative refinement with LLMs and Frama-C achieves 96% proof ratio on 604 C programs, establishing verification-in-loop as state-of-practice. LeanDojo [2] showed theorem proving benefits from proof-assistant feedback in Lean. Our work extends these systems by decomposing *why* iteration works—quantifying information gradient across feedback dimensions (β=12.49, R²=0.89)—and *how* to generalize via cross-verifier semantic normalization (84.9% retention).

## LLM-Guided Formal Methods

PropertyGPT [3] uses retrieval-augmented generation to achieve 80% recall for smart contract property generation from natural language. Our approach provides complementary structured signal: PropertyGPT uses external knowledge (retrieved examples), we use internal constraints (verifier feedback). These are additive—RAG provides domain patterns, feedback provides program-specific constraints.

## Error Taxonomies and Cross-Tool Translation

FormalRx [4] introduced 28-category error taxonomy for proof assistants (Lean, Coq), demonstrating error classification generalizes across theorem provers. We adapt this insight to program verifiers with minimal taxonomy—8 primitives suffice for 100% coverage across Frama-C, Dafny, Why3—because SMT-based verifiers share narrower semantic core than proof assistants. Translation validation work [5,6] validated *soundness* of cross-verifier translations; we demonstrate *effectiveness* for practical synthesis (performance retention, not just correctness).

## Mutation Testing for Specification Quality

Mutation testing traditionally validates test suite quality [7]. We introduce first application to LLM-synthesized formal specifications, addressing concerns about "spec washing" (trivial or vacuous specifications). Our results (105% of gold baseline) demonstrate synthesized specs are semantically meaningful.
