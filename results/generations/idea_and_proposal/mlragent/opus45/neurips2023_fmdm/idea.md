# Title: Action-Augmented Pretraining: Bridging the Action Gap in Foundation Models for Decision Making

## Motivation
Foundation models excel at perception and reasoning but are fundamentally trained on passive observation data (text, images) without action labels. This creates a critical gap when deploying them for sequential decision making, where understanding action-consequence relationships is essential. Current approaches either fine-tune foundation models on limited action-labeled data or use them merely as perception modules, failing to fully leverage their world knowledge for decision making. We need principled methods to inject action understanding into foundation models while preserving their generalization capabilities.

## Main Idea
We propose **Action-Augmented Contrastive Pretraining (AACP)**, a framework that retrofits action understanding into frozen foundation models through a lightweight action-prediction adapter trained on diverse interaction data.

**Methodology:**
1. Curate a large-scale dataset of state-action-outcome triplets from simulation environments, robotics datasets, gameplay videos with inferred actions, and instructional videos with action annotations
2. Train a modular action adapter network that takes foundation model embeddings and predicts: (a) feasible actions, (b) action effects on state, and (c) inverse dynamics (what action caused observed transition)
3. Use contrastive learning to align the action-augmented representations with the original foundation model's semantic space

**Expected Outcomes:** Models that maintain zero-shot generalization while exhibiting improved sample efficiency in downstream RL tasks (targeting 5-10x improvement) and better action grounding in embodied agents.

**Impact:** Enables systematic reuse of foundation models for control and planning without expensive end-to-end retraining.