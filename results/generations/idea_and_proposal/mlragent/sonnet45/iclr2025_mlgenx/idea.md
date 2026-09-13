# Title
**Causal Gene Circuit Discovery via Differentiable Perturbation Masks and Counterfactual Reasoning**

# Motivation
Understanding causal gene regulatory relationships is crucial for identifying therapeutic targets, yet current methods struggle to distinguish correlation from causation in observational genomics data. While perturbation experiments (CRISPR screens, drug treatments) provide causal insights, they are expensive and cover limited perturbation spaces. We need methods that can learn causal structures from combined observational and sparse perturbational data, enabling more efficient experimental design and robust target identification.

# Main Idea
We propose a neural causal discovery framework that integrates:

1. **Differentiable Perturbation Masks**: A graph neural network with learnable adjacency matrices representing gene regulatory circuits, trained on both observational single-cell data and perturbation experiments. The masks enforce sparsity through structured regularization (e.g., DAG constraints).

2. **Counterfactual Prediction Module**: Given observed perturbation outcomes, the model learns to predict counterfactual gene expression under hypothetical interventions, validated against held-out perturbation screens.

3. **Active Learning Loop**: The framework recommends next-best perturbation experiments that maximally reduce uncertainty in the causal graph, optimizing experimental budget.

**Expected Outcomes**: Improved causal gene network recovery with 50% fewer perturbation experiments, validated on benchmark datasets (Perturb-seq, CROP-seq). This enables prioritization of high-confidence therapeutic targets while quantifying intervention uncertainty, accelerating early-stage drug discovery.