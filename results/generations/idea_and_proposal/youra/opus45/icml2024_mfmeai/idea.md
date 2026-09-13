## Title
CIPAM: Cerebellum-Inspired Predictive Anchoring for High-Frequency VLA Control in Contact-Rich Manipulation

## Motivation
Vision-Language-Action (VLA) models enable semantic understanding for robotic manipulation but operate at only ~5 Hz due to computational demands—far too slow for contact-rich tasks requiring reactive control. Existing acceleration methods sacrifice semantic grounding or require architectural changes to the VLA itself. Inspired by how the cerebellum enables fast motor responses while the cortex handles deliberation, we propose decoupling high-frequency control from semantic reasoning.

## Main Idea
We hypothesize that a lightweight predictive network (CIPAM) trained on VLA input-output pairs can achieve 50+ Hz control while maintaining ≥90% task success by learning to predict VLA outputs between periodic "semantic anchoring" updates.

**Core mechanism:** CIPAM (4-layer Transformer, 256-dim) encodes image embeddings, proprioceptive state, and the last VLA action to predict next actions at 50 Hz. The VLA runs in parallel at 5 Hz, providing ground-truth corrections that prevent prediction drift. Adaptive safety triggers invoke immediate VLA inference when prediction confidence drops below 0.7 or force anomalies occur.

**Methodology:** Train CIPAM on 10k+ VLA rollouts from ManiSkill3 simulation, then evaluate control frequency, task success rate, and semantic consistency (cosine similarity >95% with VLA outputs).

**Expected impact:** 10× latency reduction enabling real-time contact-rich manipulation while preserving VLA's semantic capabilities—bridging the gap between foundation model intelligence and embodied control requirements.