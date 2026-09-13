# Research Idea

## Title
Domain-Adaptive Machine Learning Interatomic Potentials via Shared-Private Representation Learning for Improved Surface and Interface Predictions

## Motivation
Universal machine learning interatomic potentials (MLIPs) like MACE show remarkable accuracy on bulk materials but exhibit systematic errors on surfaces and interfaces—critical structures for catalysis, batteries, and corrosion. This "domain shift" problem arises because bulk-dominated training data biases learned representations. Current approaches require expensive surface-specific fine-tuning or separate models. A principled method to learn transferable atomic representations across material domains while capturing domain-specific physics would significantly advance materials discovery for surface-sensitive applications.

## Main Idea
We propose augmenting MACE with a shared-private domain-adaptive architecture. The **shared encoder** uses domain adversarial training (gradient reversal) to learn domain-invariant atomic features transferable across bulk and surface configurations. The **private encoder**, conditioned on automatically computed domain embeddings (coordination numbers, local geometry statistics), captures domain-specific corrections. A learned gating mechanism adaptively fuses both representations for energy prediction.

**Key predictions:** (1) Surface energy MAE reduces >30% versus baseline MACE on OC20 benchmarks; (2) Bulk accuracy maintained within 3%; (3) Domain classifier accuracy drops from >90% to <60%, confirming invariant feature learning.

**Methodology:** Train on mixed Materials Project (bulk) and OC20 (surface) data with scheduled adversarial loss weighting. Validate via ablations (shared-only, private-only, no-gating) to verify the causal mechanism.

**Impact:** Enables accurate surface/interface predictions without domain-specific retraining, accelerating catalyst and interface materials design.