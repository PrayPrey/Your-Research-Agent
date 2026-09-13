# Quadratic Influence Budgets for Democratic Multi-Modal Reward Aggregation in RLHF

## Motivation

Current RLHF systems fail to preserve minority preferences when aggregating heterogeneous human feedback, typically averaging annotations and silencing diverse viewpoints. While personalized approaches like P-RLHF preserve diversity, they require training separate models per annotator—computationally prohibitive at scale (1000+ annotators). This creates a critical trade-off: either sacrifice minority voices for efficiency or incur unsustainable costs. Existing strategyproof methods use simple mechanisms (median voting) that still collapse multi-modal preferences into single values, failing to capture the rich diversity needed for democratic AI alignment.

## Main Idea

We propose embedding **quadratic voting mechanisms** from participatory budgeting into neural reward aggregation. Each annotator receives a finite influence budget allocated across samples with quadratic cost (Σw²≤B), forcing strategic prioritization of strongly-held preferences. A learned Influence Allocation Network optimizes these weights while satisfying budget constraints via projected gradient descent. Budget-weighted preference embeddings are aggregated into Mixture-of-Gaussians distributions, enabling multi-modal reward learning that preserves minority clusters.

**Core mechanism:** Quadratic costs → strategic allocation → budget-weighted latent aggregation → multi-modal distributions → minority preservation.

**Expected outcomes:** >80% minority representation (vs. <50% vanilla RLHF), comparable alignment performance to P-RLHF with 10x lower computational cost, and robustness to strategic manipulation (<5% degradation). This enables democratic AI alignment at scale while maintaining interpretable preference clusters and flexible fairness-efficiency trade-offs.