# Title
**Adaptive Data Valuation for Continual Foundation Model Updates via Influence-Based Provenance Tracking**

## Motivation
As foundation models evolve through continual updates, understanding which training data contributes positively or negatively to model performance becomes critical for efficient curation and legal compliance. Current approaches lack mechanisms to systematically track data provenance and quantify individual data points' ongoing value across model versions. This gap hinders efficient data management, creates copyright attribution challenges, and prevents targeted removal of harmful or low-quality data without full retraining.

## Main Idea
We propose a lightweight influence-tracking framework that maintains provenance scores for training data across foundation model updates. The methodology involves:

1. **Incremental Influence Estimation**: Develop efficient approximations of data influence functions that scale to billion-parameter models, using gradient-based checkpointing and low-rank updates.

2. **Multi-dimensional Value Metrics**: Track data contributions across performance, safety, fairness, and efficiency dimensions simultaneously, creating comprehensive value profiles.

3. **Adaptive Curation Policy**: Design reinforcement learning-based policies that automatically prioritize high-value data for retention and identify low-value or harmful samples for removal during continual learning.

**Expected Outcomes**: A practical system enabling FM developers to (1) attribute model capabilities to specific data sources for copyright/licensing, (2) efficiently remove problematic data, and (3) optimize dataset composition for updated versions, reducing computational costs by 30-50% while improving alignment metrics.