## Title
Neural-Symbolic Repair: Self-Correcting LLM Code Generation via Iterative Formal Feedback Synthesis

## Motivation
LLM-generated code often contains subtle bugs that pass basic tests but violate formal specifications or exhibit edge-case failures. While static analyzers and SMT solvers can detect these issues, they typically produce low-level error messages that LLMs struggle to interpret for effective self-correction. There's a critical gap in translating formal verification feedback into actionable, natural language repair guidance that LLMs can leverage for iterative improvement.

## Main Idea
We propose a neural-symbolic framework where formal verification tools (static analyzers, symbolic executors, SMT solvers) are augmented with a **feedback synthesis layer** that translates verification failures into structured repair prompts. The approach works as follows:

1. **Initial Generation**: LLM generates code from natural language specifications
2. **Formal Analysis**: Apply multiple verification tools to detect violations (type errors, null dereferences, contract violations)
3. **Feedback Synthesis**: A specialized smaller model trained on <error, repair> pairs converts formal checker outputs into: (a) natural language explanations, (b) counterexamples, (c) repair hints pointing to specific code locations
4. **Iterative Repair**: Feed synthesized feedback back to the LLM for targeted corrections

Expected outcomes include higher fix rates compared to raw error messages, reduced repair iterations, and a benchmark dataset of verification-guided repairs. This bridges formal methods' precision with LLMs' flexibility, making verification actionable for code generation.