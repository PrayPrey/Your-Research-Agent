# Title
Causal Probing for Mechanistic Understanding of Hallucinations in Large Language Models

# Motivation
Hallucinations—instances where foundation models generate plausible but factually incorrect information—pose critical risks in high-stakes domains like healthcare and finance. While existing work detects hallucinations post-hoc, we lack fundamental understanding of *why* and *how* they emerge during generation. Understanding the causal mechanisms behind hallucinations is essential for developing principled interventions that improve reliability without sacrificing model capabilities. This research addresses the workshop's core question: "How can we pinpoint and understand the causes behind known sources of FM unreliability?"

# Main Idea
We propose a causal intervention framework to identify neural mechanisms responsible for hallucinations in LLMs. The methodology involves: (1) **Targeted ablation studies** that systematically deactivate specific attention heads and feed-forward layers during generation to establish causal links between components and factual errors; (2) **Activation patching experiments** that swap activations between factual and hallucinated completions to isolate critical computational pathways; (3) **Mechanistic analysis** of how models retrieve and compose factual knowledge versus confabulate information.

**Expected outcomes**: A taxonomy of hallucination types mapped to specific model components, interpretable indicators predictive of impending hallucinations, and targeted intervention points for reliability improvements.

**Potential impact**: This causal understanding enables surgical model editing, improved training objectives targeting hallucination-prone circuits, and runtime monitoring systems that flag unreliable outputs before deployment—advancing both theoretical foundations and practical reliability of FMs.