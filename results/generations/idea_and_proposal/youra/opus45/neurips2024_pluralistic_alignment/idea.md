# Research Idea

## Title
Cluster-Aware Variational Disagreement (CAVD): Discovering Latent Value Systems from Preference Data via Voting-Based Reward Aggregation

## Motivation
Current AI alignment methods treat annotator disagreement as noise, discarding valuable signals about diverse human values. This creates AI systems that implicitly favor majority perspectives while lacking transparency about value trade-offs—a critical gap as regulations like the EU AI Act demand governance-auditable AI decisions. Existing pluralistic approaches (VPL, MODPO) require explicit annotator labels, limiting scalability. We need methods that discover latent value diversity from standard preference data while enabling transparent, auditable aggregation.

## Main Idea
We propose CAVD, which uses variational inference to discover K latent value clusters from unlabeled pairwise preference data, then aggregates per-cluster rewards via differentiable social choice voting (Borda/Condorcet with Gumbel-Softmax relaxation). The core insight is that disagreement patterns encode coherent moral frameworks discoverable without explicit labels.

**Methodology:** Train a VAE encoder on PERSONA benchmark (317K preference pairs) to produce soft cluster assignments, feed these to K specialized reward heads, then aggregate via transparent voting with full audit trails.

**Predictions:** (1) Discovered clusters will correlate (r>0.3) with Moral Foundations Questionnaire dimensions; (2) Per-cluster accuracy will reach ≥90% of label-requiring baselines; (3) Human evaluators will achieve substantial agreement (κ>0.6) identifying which values influenced decisions.

**Impact:** Enables governance-compliant pluralistic AI without costly annotator metadata collection.