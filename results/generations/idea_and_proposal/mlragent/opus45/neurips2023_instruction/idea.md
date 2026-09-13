# Title: Self-Calibrating Instruction Following via Uncertainty-Aware Synthetic Data Generation

## Motivation
Current instruction-tuned LLMs often exhibit overconfidence when following ambiguous or underspecified instructions, leading to hallucinations and unreliable outputs. While synthetic data generation has scaled instruction tuning, it typically lacks quality signals about instruction clarity. Models trained on such data cannot distinguish between instructions they can reliably follow versus those requiring clarification. This creates a critical gap: models confidently produce incorrect outputs rather than seeking clarification or expressing appropriate uncertainty.

## Main Idea
We propose a novel framework that jointly trains LLMs to follow instructions AND calibrate their confidence based on instruction quality. Our approach involves:

1. **Uncertainty-Annotated Synthetic Data**: Generate instruction-response pairs with automatically computed ambiguity scores using multiple LLM passes. Instructions with high response variance are labeled as "ambiguous."

2. **Dual-Head Training**: Extend instruction tuning with an auxiliary head that predicts instruction clarity, trained to output calibrated confidence scores alongside responses.

3. **Clarification-Seeking Behavior**: When confidence falls below a threshold, models are trained to generate targeted clarifying questions rather than potentially incorrect answers.

**Expected Outcomes**: Models that know when they don't know, reducing hallucinations by 20-30% on ambiguous queries while maintaining performance on clear instructions. This creates more trustworthy, deployable instruction-following systems.