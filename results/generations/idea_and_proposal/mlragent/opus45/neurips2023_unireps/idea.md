# Title: Learning Dynamics-Guided Model Merging via Representation Trajectory Alignment

## Motivation
Current model merging techniques (e.g., weight averaging, task arithmetic) often fail when merging models that have diverged significantly during training, even when they share similar final representations. This occurs because these methods ignore *how* representations evolved during learning. Understanding the temporal dynamics of representation formation—when and why similarities emerge—could unlock more principled merging strategies. By aligning not just final representations but their developmental trajectories, we can identify optimal "merge points" and transformation strategies that respect the natural geometry of the loss landscape.

## Main Idea
We propose **Trajectory-Aligned Model Merging (TAMM)**, a framework that leverages learning dynamics to improve model merging. Our approach:

1. **Trajectory Logging**: During training, periodically save representation snapshots at each layer, creating a "representation trajectory" for each model.

2. **Trajectory Alignment Analysis**: Use representation similarity metrics (CKA, SVCCA) across training time to identify phases where models develop compatible representations—detecting natural "synchronization windows."

3. **Dynamics-Informed Merging**: Rather than merging final weights, merge models at identified synchronization points or apply learned transformations that respect the curvature of representation evolution.

4. **Evaluation**: Test on multi-task merging and federated learning scenarios, measuring task performance retention compared to standard merging baselines.

**Expected Outcomes**: Improved merged model performance, theoretical insights connecting linear mode connectivity to representation dynamics, and practical guidelines for when models are "merge-compatible."