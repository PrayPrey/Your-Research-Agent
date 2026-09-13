## Title
Safety Binding Theory: Understanding Compositional Safety Failures in Vision-Language Models

## Motivation
Vision-Language Models (VLMs) exhibit a puzzling vulnerability: individually safe visual and textual components become unsafe when combined. Current research treats this as a modality gap problem, but fails to explain *why* safety specifically degrades at cross-modal integration points. This gap leaves multimodal AI systems vulnerable to compositional attacks that exploit the integration process itself, posing significant risks as these models are deployed in high-stakes applications.

## Main Idea
We propose **Safety Binding Theory (SBT)**, hypothesizing that compositional safety failures emerge from *binding interference* at cross-modal attention layers. When visual and textual representations merge, safety-trained patterns from text-only training receive out-of-distribution inputs, disrupting safety mechanism activation. We formalize this as: S_compose(v,t) = S(v) ⊗ S(t) + ε_bind, where ε_bind captures emergent interference.

**Methodology:** We measure attack success rates at integration layers versus unimodal layers, predicting ≥15% higher vulnerability at integration points. Cross-modal attention entropy will be correlated with safety degradation (r ≥ 0.5). We extend MMCoA with binding-aware training objectives targeting integration layers.

**Expected Outcomes:** A predictive diagnostic using attention entropy to identify high-risk modal combinations, and binding-aware defenses improving compositional safety by ≥10% on MMDT benchmarks. This provides the first mechanistic explanation for *where* and *why* multimodal safety fails.