# Research Idea: Hierarchical Domain Bridging for LLM-Based Outdoor Embodied Agents

## Title
Hierarchical Domain Bridging for Weather-Robust LLM-Based Outdoor Navigation: Meta-Learning Perception with Zero-Shot Spatial Reasoning

## Motivation
Current LLM-based embodied agents excel indoors but struggle in outdoor urban environments due to weather/lighting variations and large sim-to-real gaps (≥25pp performance drops). Existing approaches either require expensive end-to-end fine-tuning or achieve only ~50-60% success rates. This research addresses the critical gap of enabling sample-efficient, weather-robust outdoor navigation by recognizing that perception and reasoning require fundamentally different adaptation strategies—perception needs domain adaptation while reasoning can leverage zero-shot prompting.

## Main Idea
We propose hierarchical domain bridging that separates perception adaptation from reasoning transfer. The core innovation combines: (1) **meta-learned perception** trained across 5-10 simulated weather conditions using MAML with controlled deployment gaps, enabling fast adaptation to real-world conditions with only 10-50 labeled samples per weather type; (2) **spatial prompting** for LLMs using reference objects and keyframes, achieving zero-shot reasoning transfer without fine-tuning; (3) **GAN-based progressive domain bridging** with 3-5 intermediate style-transfer steps to systematically reduce the sim-to-real gap. 

The causal mechanism flows through five links: meta-training diversity forces condition-invariant feature learning → few-shot real-world adaptation (≥70% perception accuracy) → reliable semantic understanding → zero-shot LLM spatial reasoning (≥90% of simulation performance) → hierarchical integration achieving ≥70% navigation success with ≤10pp reality gap. We validate against CityEQA's 60.7% simulation baseline through real-world deployment across multiple weather conditions, providing the first standardized outdoor sim-to-real benchmark for LLM agents while reducing data requirements 5-10× compared to standard fine-tuning.