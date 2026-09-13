# Research Idea

## Title
Hierarchical Cross-Modal Consistency Learning for Text-to-Audio Generation Evaluation

## Motivation
Evaluating generated audio remains a critical bottleneck in audio generation research. Current metrics like Fréchet Audio Distance (FAD) capture distributional similarity but fail to assess semantic alignment with text prompts, while human evaluation is expensive and non-scalable. The lack of reliable automatic evaluation methods that measure both audio quality and text-audio correspondence hinders rapid iteration and fair comparison of generative models. This gap is particularly pronounced for complex compositional prompts (e.g., "a dog barking followed by thunder during rain").

## Main Idea
We propose **HierAudioEval**, a hierarchical evaluation framework that assesses text-to-audio generation across three levels: (1) **acoustic quality** via learned perceptual features, (2) **semantic alignment** through contrastive audio-language embeddings, and (3) **compositional consistency** using a novel temporal-semantic graph matching approach. 

The key innovation is a compositional evaluation module that parses text prompts into structured event graphs (capturing objects, actions, temporal relations) and matches them against detected audio events with their temporal boundaries. We will train a lightweight audio event detector and temporal relation classifier on AudioSet and custom annotations.

Expected outcomes include a unified evaluation score correlating better with human judgments than existing metrics, particularly for compositional prompts. This will accelerate audio generation research by providing reliable, interpretable, and scalable evaluation, directly benefiting model development and benchmarking efforts.