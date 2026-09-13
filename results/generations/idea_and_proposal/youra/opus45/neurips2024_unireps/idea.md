# Research Idea

## Title
Entropic Alignment Score: An Information-Theoretic Metric for Cross-Modal Representation Alignment

## Motivation
Recent theoretical advances (Platonic Representation Hypothesis, Neural Thermodynamics) demonstrate that neural networks converge toward shared representations through entropic forces during SGD training. However, existing alignment metrics (CKA, RSA) measure correlation rather than information-theoretic alignment, creating a gap between theory and practical measurement. This limits our ability to quantify and optimize cross-modal alignment in vision-language models.

## Main Idea
We propose the Entropic Alignment Score (EAS = 1 - H(X|Y)/H(X)), measuring how much one modality's embeddings reduce uncertainty about another's. The core hypothesis: SGD's entropic forces drive multimodal representations toward shared structure, manifested as reduced conditional entropy. Lower H(X|Y) means text embeddings are more predictive of image embeddings, directly enabling better cross-modal retrieval.

We will validate EAS across 15+ vision-language models (CLIP, BLIP, ALIGN variants), testing whether EAS correlates more strongly with retrieval performance (R@1) than CKA/RSA (target: r>0.7). Conditional entropy is estimated via InfoNCE with ensemble MINE networks on 1024-d embeddings.

Expected outcomes: (1) a theoretically-grounded metric bridging PRH theory with practical measurement, (2) demonstration that information-theoretic alignment outpredicts correlation-based metrics, and (3) potential use as an auxiliary training objective for improved multimodal alignment.