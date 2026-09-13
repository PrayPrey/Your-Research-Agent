# Research Idea

## Title
Schema-Adaptive Column Transformers via Prototype-Based Encoding and Continual Regularization

## Motivation
Tables are ubiquitous in data management, yet table transformer models struggle with schema evolution—a critical real-world challenge where columns are added, deleted, or renamed over time. Current approaches like TAPAS and TaBERT require costly retraining after schema changes and suffer catastrophic forgetting. This gap limits deployment in production databases and data lakes where schemas evolve continuously. A robust solution would enable table models to maintain performance on existing tasks while generalizing to new schema elements without retraining.

## Main Idea
We propose Schema-Adaptive Column Table Transformers (SACTT), which decouple semantic concepts from schema-specific encodings through three mechanisms: (1) **Prototype Bank Learning**—clustering column representations from large table corpora to discover ~100-500 stable semantic anchors; (2) **Confidence-Aware Binding**—dynamically routing new columns to prototypes based on metadata similarity, triggering few-shot learning only for truly novel concepts; (3) **Continual Regularization**—applying EWC-style parameter protection during adaptation to prevent forgetting.

We hypothesize SACTT achieves >90% performance retention after schema changes and >70% zero-shot accuracy on new columns. Validation uses the EvoSchema benchmark with 10 perturbation types, comparing against TAPAS/TaBERT baselines. Success would establish a new paradigm for production-ready table models that gracefully handle schema evolution without catastrophic forgetting.