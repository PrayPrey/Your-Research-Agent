# Research Idea

## Title
Distribution-Adaptive Representation Learning for Robust Decision-Focused Optimization Under Temporal Shift

## Motivation
Decision-focused learning (DFL) integrates machine learning with combinatorial optimization for sustainability applications like energy scheduling and resource allocation. However, these domains face temporal distribution shifts (seasonal, climate-driven, policy-induced) that degrade decision quality. Current approaches either ignore shifts (standard DFL), apply worst-case hedging (Gen-DFL, 3D-Learning), or enforce prediction-invariance that discards decision-relevant information. A critical gap exists: no method explicitly adapts decision mappings to distribution context while preserving decision-relevant features.

## Main Idea
We propose Distribution-Adaptive Representation Learning (DARL), which augments DFL with two components: (1) a distribution embedding network that captures shift characteristics from unlabeled data, and (2) a distribution-conditional decision head that adapts decisions based on detected context. The key insight is that explicit distribution conditioning enables principled adaptation rather than conservative hedging, preserving decision-relevant information while adjusting to distribution-specific optimal mappings.

**Methodology:** Train on multi-distribution sustainability data (Wild-Time benchmark adapted for decision tasks), comparing DARL against standard DFL, Gen-DFL, and 3D-Learning using decision regret degradation ratio as the primary metric.

**Expected Outcomes:** DARL achieves <15% regret degradation under shift (vs >20% for baselines), with >5% improvement over worst-case methods on gradual temporal shifts typical in sustainability domains. This enables more reliable deployment of optimization systems in changing environmental conditions.