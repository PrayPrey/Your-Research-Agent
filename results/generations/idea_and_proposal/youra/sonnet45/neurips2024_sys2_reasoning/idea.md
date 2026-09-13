# Title
Specification-Driven Benchmark Generation: Eliminating Contamination in System-2 Reasoning Evaluation Through Meta-Diverse CSP Synthesis

# Motivation
Current LLM reasoning benchmarks suffer from 3-15% contamination rates, where models memorize training data rather than demonstrate genuine System-2 reasoning capabilities. Static datasets enable both training-time leakage and search-time retrieval contamination. Existing procedural generation (e.g., RandomCalculation) works only for narrow domains and remains vulnerable to abstraction-level pattern memorization. We need contamination-proof evaluation that distinguishes true reasoning from sophisticated pattern matching across diverse closed-domain tasks.

# Main Idea
We propose generating benchmarks from formal specifications using constraint satisfaction solvers (CSP) at evaluation time—after model training completes. The core innovation is **meta-generation**: systematically varying specification parameters, structural components, and cross-domain mixing to prevent models from adapting to specification-level patterns. 

The causal mechanism operates through three steps: (1) formal specifications (PDDL, SMT-LIB) define task constraints, (2) CSP solvers generate novel instances satisfying these constraints with meta-diverse variations, (3) temporal separation and meta-variation jointly eliminate contamination while process-based verification (reasoning trace validation) measures genuine capability.

We test across four closed domains (math, logic, planning, CSP), predicting zero contamination (vs. 3-15% baseline) and ≥0.75 correlation between automated process verification and human expert judgment. This enables reliable System-2 reasoning assessment immune to data leakage.