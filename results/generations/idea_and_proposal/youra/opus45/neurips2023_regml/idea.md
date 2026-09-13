# Research Idea

## Title
HUA-LoRA: Hierarchical Unlearning via Domain-Partitioned Adapters for Scalable GDPR Compliance in Large Language Models

## Motivation
GDPR's "right to be forgotten" requires ML systems to remove individual data influence on demand, yet current LLM unlearning methods face a critical tradeoff: full retraining is computationally prohibitive, while approximate methods either fail verification tests or degrade model utility. This gap between regulatory requirements and practical ML capabilities represents a significant barrier to compliant LLM deployment. Existing approaches lack both the scalability for billion-parameter models and rigorous verification of forgetting efficacy.

## Main Idea
We propose HUA-LoRA, a framework that achieves scalable machine unlearning through two key mechanisms: (1) **domain-partitioned LoRA adapters** that localize data influence to specific adapter modules during fine-tuning, and (2) **multiplicative weight decay** applied to targeted adapters to erase learned representations. The causal mechanism operates as follows: domain-specific training data is routed to dedicated low-rank adapters, compartmentalizing knowledge; when unlearning is requested, the relevant adapter is identified via domain labels and subjected to neuroscience-inspired decay that progressively weakens learned weights.

We will evaluate on LLaMA-7B using Membership Inference Attacks (MIA) as verification, targeting >90% MIA evasion, >95% utility retention, and <1% retraining compute cost. This bridges the regulatory-ML gap by providing verifiable, efficient unlearning that scales to production LLMs.