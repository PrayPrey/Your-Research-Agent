# Title: Bidirectional Consistency Training for Autoformalization via Round-Trip Translation

## Motivation
Autoformalization—translating natural language mathematics into formal proofs—remains challenging due to the scarcity of parallel corpora and the difficulty of measuring translation quality. Current approaches suffer from semantic drift and lack reliable feedback signals during training. Meanwhile, the dual task of auto-informalization (formal-to-natural) is often treated separately, missing opportunities for mutual improvement. By enforcing bidirectional consistency, we can create a self-supervised training signal that improves both directions without requiring extensive human annotation.

## Main Idea
We propose a round-trip consistency framework that jointly trains autoformalization and auto-informalization models. Given a natural language proof N, we formalize it to F, then informalize F back to N', enforcing semantic consistency between N and N' (and vice versa starting from formal proofs). 

The methodology involves: (1) training paired encoder-decoder models with a cycle-consistency loss measuring semantic similarity between original and reconstructed statements; (2) using formal proof checkers (e.g., Lean, Coq) as hard constraints—only accepting formalizations that type-check; (3) incorporating a learned semantic equivalence classifier trained on theorem-level paraphrases.

Expected outcomes include improved formalization accuracy without additional parallel data and a new evaluation metric based on round-trip fidelity. This approach could significantly reduce the human effort needed for building formal mathematics libraries while providing interpretable natural language explanations of formal proofs.