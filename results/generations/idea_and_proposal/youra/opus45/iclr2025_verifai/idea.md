# Research Idea

## Title
Step-Level Verification-Guided Generation for Formal Reasoning in LLMs

## Motivation
Large language models show promise in formal domains like theorem proving and verified code generation, but errors compound across sequential reasoning steps, causing cascading failures. Current approaches provide feedback only after complete generation (claim-level), missing opportunities for early error correction. While grammar-constrained decoding offers real-time guidance, it lacks semantic verification depth. This gap motivates exploring whether integrating step-level formal verification during generation can prevent error propagation and improve correctness in compounding-error domains.

## Main Idea
We propose Step-Level Verification-Guided Generation (SL-VGG), which integrates incremental formal verification (Lean 4 type checking, Z3 SMT solving) directly into LLM decoding. After each tactic or statement, the verification module provides a 3-part feedback signal (validity, error type, correction hints) that conditions subsequent generation via cross-attention. This enables dense reward signals for RL fine-tuning, catching errors before they propagate.

**Core hypothesis:** Step-level feedback will exceed claim-level approaches by ≥5% verification correctness because early detection prevents compounding errors.

**Key predictions:** (1) >75% correctness on miniF2F-Lean (vs. 70% SOTA), (2) ≥70% error recovery rate (vs. ≤50% claim-level), (3) generation time <2x unconstrained baseline.

**Falsification:** Correctness ≤60% or efficiency >3x baseline rejects the hypothesis. This bridges formal methods' guarantees with LLM scalability for trustworthy AI-generated proofs and code.