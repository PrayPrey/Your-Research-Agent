# Title: Learning Grounded Reward Functions from Multimodal Implicit Feedback with Unknown Semantics

## Motivation
Current interactive learning systems typically require humans to provide explicit rewards or demonstrations, which is unnatural and burdensome. Humans naturally communicate intent through implicit signals—facial expressions, gaze patterns, speech prosody, and gestures—whose meanings may be context-dependent, ambiguous, or initially unknown to the learning agent. A critical open question is: *How can agents learn to ground and leverage these arbitrary implicit feedback signals without predefined reward mappings?* This is essential for deploying adaptive systems in naturalistic settings where explicit feedback is impractical.

## Main Idea
We propose **Implicit Feedback Grounding Networks (IFG-Net)**, a framework that jointly learns (1) a grounding model mapping multimodal implicit signals to latent reward representations, and (2) a policy optimizing these inferred rewards. The key insight is to use *self-supervised contrastive learning* across interaction episodes: temporally-aligned implicit signals following successful task completion should cluster similarly, while signals following failures should be distinguishable.

Our methodology involves: (a) collecting multimodal streams (facial expressions, gaze, speech tone) during human-agent interaction, (b) learning a shared embedding space using contrastive objectives without explicit labels, and (c) iteratively refining the grounding through active queries when uncertainty is high.

Expected outcomes include agents that autonomously discover feedback semantics and adapt to individual users' communication styles. This enables truly naturalistic interaction and personalized assistance without requiring users to learn artificial feedback mechanisms.