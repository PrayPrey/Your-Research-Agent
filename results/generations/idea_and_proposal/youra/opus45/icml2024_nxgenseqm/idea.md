# Research Idea

## Title
Contextual State Reinstatement: Bridging Cognitive Memory Theory and State Space Models for Enhanced In-Context Learning

## Motivation
State space models (SSMs) like Mamba offer efficient O(n) sequence processing but underperform Transformers on in-context learning (ICL) tasks. Recent work by Ji-An et al. (2024) revealed that Transformer ICL emerges through mechanisms resembling the Context Maintenance and Retrieval (CMR) model from cognitive psychology. However, SSMs lack attention-based induction heads that implement these memory operations. This creates a critical gap: can CMR-inspired mechanisms be computationally translated into SSM state dynamics to unlock stronger ICL capabilities while preserving efficiency?

## Main Idea
We propose **Contextual State Reinstatement (CSR)**, a mechanism augmenting Mamba's selective scan with three components: (1) temporal context encoding via dedicated state channels, (2) cosine similarity-based retrieval gates that activate when current inputs match stored patterns, and (3) threshold-gated state reinstatement that restores relevant prior context. The causal mechanism mirrors CMR's "jump back in time" retrieval within SSM dynamics.

We will evaluate CSR-enhanced Mamba (370M-1.4B parameters) on GINC and MetaICL benchmarks, targeting >10% ICL accuracy improvement. Critically, we test whether CMR behavioral signatures (recency effects, temporal contiguity) emerge, validating the cognitive-computational bridge. Ablation studies will isolate each component's contribution. This work advances theoretical understanding of SSM learning mechanisms while potentially enabling efficient alternatives to attention-based ICL.