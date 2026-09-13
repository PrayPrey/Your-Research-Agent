# Title: Causal Intervention Probing: Discovering and Manipulating Causal Mechanisms in Large Language Model Representations

## Motivation
Understanding *how* large language models (LLMs) encode and utilize causal relationships internally remains largely unexplored. While existing work probes whether LLMs *possess* causal knowledge, we lack systematic methods to identify *where* causal reasoning mechanisms reside in model representations and *how* to intervene on them. This gap prevents us from (1) explaining why models succeed or fail at causal reasoning tasks, (2) correcting faulty causal inferences without full retraining, and (3) building trustworthy systems for safety-critical applications where causal understanding is paramount.

## Main Idea
We propose **Causal Intervention Probing (CIP)**, a framework that combines causal discovery with activation patching to localize and manipulate causal reasoning circuits in LLMs. Our methodology involves:

1. **Causal Circuit Discovery**: Apply interchange interventions across layers and attention heads while models perform causal reasoning tasks (e.g., identifying confounders, predicting intervention effects) to discover which components encode specific causal concepts.

2. **Structured Representation Analysis**: Use causal abstraction to map discovered circuits onto formal causal graphical model operations (d-separation, do-calculus rules).

3. **Targeted Editing**: Develop lightweight interventions (steering vectors, adapter modules) that correct identified causal reasoning failures without degrading general capabilities.

**Expected Outcomes**: Interpretable maps of causal reasoning mechanisms, targeted repair methods for causal errors, and insights into why scaling improves causal understanding. This directly addresses the "causality of large models" direction while enabling practical improvements in model trustworthiness.