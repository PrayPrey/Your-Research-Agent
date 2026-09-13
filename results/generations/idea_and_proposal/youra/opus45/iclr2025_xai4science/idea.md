# Research Idea

## Title
Hierarchical Ontology-Structured Concept Bottleneck Models for Scientifically Interpretable Predictions

## Motivation
Concept Bottleneck Models (CBMs) offer interpretable predictions through human-understandable concepts, but existing approaches like Label-Free CBM use flat, general-purpose concept sets that fail to capture how scientists actually organize domain knowledge. Scientific ontologies (e.g., Gene Ontology, ENVO for climate) encode hierarchical relationships (is-a, part-of) that mirror expert reasoning patterns—from coarse categories to fine-grained distinctions. This structural mismatch limits CBMs' utility for scientific knowledge discovery, a critical gap for XAI4Science applications.

## Main Idea
We propose Hierarchical Ontology-Structured CBM (HOS-CBM), which organizes concept bottleneck layers according to domain ontology hierarchies, creating multi-resolution concept representations. The core mechanism involves: (1) parsing OWL ontologies into hierarchical concept embeddings using OWL2Vec+, (2) aligning learned features to concepts at multiple hierarchy levels via contrastive loss, and (3) enforcing ontology consistency constraints (parent ≥ max(child) activations). 

We hypothesize this structure improves interpretability because it mirrors scientists' coarse-to-fine reasoning. Evaluation on climate science tasks (ERA5 dataset, ENVO ontology) will compare HOS-CBM against Label-Free CBM using expert interpretability ratings (target: Cohen's d > 0.5) while maintaining competitive accuracy (≤10% drop). Falsification occurs if experts cannot distinguish explanations or ontology consistency falls below 70%. Success would establish ontology-guided architecture as a principled approach for scientifically meaningful XAI.