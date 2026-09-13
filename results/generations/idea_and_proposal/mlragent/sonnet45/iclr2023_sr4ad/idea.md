# Research Idea: Uncertainty-Aware Hierarchical Scene Representations for Safe Autonomous Driving

## 1. Title
Hierarchical Uncertainty-Aware Scene Graphs for Joint Perception-Prediction with Safety Guarantees

## 2. Motivation
Current autonomous driving systems struggle with the perception-prediction interface, where errors cascade through the pipeline. Critical safety failures often occur when the system is overconfident about misperceived objects or their trajectories. We need intermediate representations that explicitly encode uncertainty and enable both joint reasoning across modules and interpretable safety assessments.

## 3. Main Idea
Develop a probabilistic hierarchical scene graph representation that:
- **Structure**: Represents scenes at multiple abstraction levels (raw detections → tracked objects → agent interactions → scene-level semantics)
- **Uncertainty Quantification**: Each node and edge maintains calibrated uncertainty estimates using evidential deep learning, propagating through the hierarchy
- **Joint Optimization**: Train perception and prediction modules end-to-end while maintaining the interpretable graph structure, enabling gradient flow between traditionally separate components
- **Safety Integration**: Implement conformal prediction techniques to provide finite-sample coverage guarantees, flagging high-uncertainty scenarios for fallback behaviors

**Expected Outcomes**: Improved prediction accuracy in complex scenarios, reduced cascading errors, interpretable uncertainty measures for safety validation, and quantifiable performance bounds. This bridges modular and end-to-end approaches while maintaining the interpretability required for safety certification.