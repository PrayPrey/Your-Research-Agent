# Title
Causal Mechanistic Tracing: Component-Level Diagnosis of Causal Reasoning in Large Language Models

# Motivation
Large language models achieve only 57.6% accuracy on causal reasoning benchmarks, yet current evaluations provide only aggregate performance metrics without explaining *why* or *where* models fail. This diagnostic gap prevents targeted improvements and limits deployment in safety-critical domains requiring robust causal reasoning (healthcare, policy). Existing benchmarks cannot identify which model components process different types of causal reasoning (observation vs. intervention vs. counterfactual), hindering systematic enhancement of these capabilities.

# Main Idea
We propose integrating mechanistic interpretability techniques with structured causal reasoning evaluation. By applying activation patching to tasks stratified by Pearl's causal hierarchy (3 rungs), we localize causal reasoning capabilities to specific transformer components (attention heads, layers). The core hypothesis: different causal reasoning levels engage distinct computational circuits, detectable through differential performance drops when components are ablated. 

We test 150 components per model across 1,500 rung-stratified tasks, predicting: (1) task-relevant components show significantly larger performance drops than random patches (Cohen's d > 0.5), (2) component importance rankings differ across reasoning levels (Spearman ρ < 0.6), and (3) identified circuits predict held-out failures above chance (AUC > 0.65). This enables actionable diagnostics—identifying *which* components to enhance—rather than opaque aggregate scores, advancing both LLM interpretability and causal AI safety.