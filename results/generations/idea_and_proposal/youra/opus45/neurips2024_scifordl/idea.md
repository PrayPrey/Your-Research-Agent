# Research Idea

## Title
Mechanistic Verification of Gradient Descent Theory in Transformer In-Context Learning via Circuit Analysis

## Motivation
Despite theoretical work suggesting transformers implement gradient descent during in-context learning (ICL), no empirical verification connects these mathematical predictions to actual neural circuit mechanisms. Prior interpretability work identified induction heads for ICL but did not validate gradient descent theories. This gap between elegant theory and mechanistic reality limits our understanding of how transformers truly learn from context. Bridging this gap would either validate foundational ICL theories or reveal alternative mechanisms, directly advancing deep learning science.

## Main Idea
We hypothesize that decoder-only transformers contain localizable "algorithm selection circuits" whose activation patterns quantitatively correlate with theoretical gradient descent predictions during ICL. Using TransformerLens activation patching on GPT-2 and Llama-7B, we will:

1. **Identify circuits**: Locate attention heads/MLPs (≤10% of parameters) whose ablation causes >50% ICL performance drop
2. **Track activation dynamics**: Measure circuit activation strength as context examples accumulate (0-32 demonstrations)
3. **Validate theory**: Test correlation (target: r>0.5, p<0.05) between circuit activation trajectories and gradient descent loss curves predicted by Ahn et al.

**Falsification criteria**: If correlations fall below r=0.3 or circuits are non-localizable, the gradient descent theory of ICL is falsified. Success would provide first mechanistic evidence linking ICL circuits to optimization theory, enabling theory-guided architecture improvements.