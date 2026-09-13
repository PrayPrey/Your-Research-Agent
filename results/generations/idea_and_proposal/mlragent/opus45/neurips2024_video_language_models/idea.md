# Research Idea

## Title
TouchLLM: Adapting Video-Language Models for Temporal Tactile Representation Learning

## Motivation
High-resolution tactile sensors generate sequential image-like data streams during object manipulation, sharing structural similarities with video. However, tactile data has unique properties: extreme locality, active sensing dependencies, and fine-grained temporal dynamics critical for understanding contact events. Current approaches either treat tactile frames independently or use generic temporal models, failing to capture touch-specific semantics. Video-Language Models (VLMs) have demonstrated remarkable success in learning temporal visual representations with language grounding, but their potential for tactile processing remains unexplored.

## Main Idea
We propose adapting pretrained Video-Language Models for tactile representation learning through a novel framework called TouchLLM. Our approach involves three key components: (1) **Tactile-Video Alignment**: We design a lightweight adapter module that maps tactile sensor outputs (e.g., GelSight, DIGIT) to the visual embedding space of frozen VLMs, preserving their learned temporal reasoning capabilities. (2) **Touch-Language Grounding**: We curate paired tactile-language descriptions capturing contact properties (texture, hardness, slip events) to enable zero-shot tactile understanding. (3) **Active Sensing Conditioning**: We incorporate proprioceptive signals (force, pose) as additional context tokens to model the active nature of touch. Expected outcomes include superior performance on tactile property recognition, slip detection, and cross-sensor generalization, while enabling language-guided tactile reasoning for robotic manipulation.