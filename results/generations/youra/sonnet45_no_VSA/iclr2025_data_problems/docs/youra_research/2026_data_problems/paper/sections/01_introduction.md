# Introduction

Large language models achieve impressive accuracy on code generation benchmarks—yet their confidence scores are dramatically miscalibrated, with Expected Calibration Error (ECE) reaching 0.53 on MBPP, 3-6× higher than image classifiers (Guo et al., 2017). This extreme miscalibration prevents effective resource allocation in agentic code generation systems, where decisions about iteration, execution, and refinement depend on knowing when the model is likely correct.

Modern neural networks are known to produce overconfident predictions that do not reflect true correctness probabilities (Guo et al., 2017). This problem has been extensively studied for image classification, where post-hoc calibration methods like temperature scaling reduce ECE by 5-15%. However, **no prior work has quantified calibration quality for code generation tasks** or established ECE benchmarks for generative models in this domain.

This gap matters because code generation evaluation has focused exclusively on functional correctness metrics (pass@k) while ignoring probabilistic calibration. An agentic coding assistant that cannot distinguish high-confidence-correct from high-confidence-incorrect predictions will waste execution attempts on hopeless solutions while abandoning fixable ones. Without calibrated confidence, agents cannot make principled decisions about when to stop iterating, when to request execution feedback, or when to try alternative approaches—leading to either wasted compute or degraded accuracy.

We bridge this gap by treating code correctness as a binary classification problem and applying calibration metrics from the classification literature to generative code tasks. Our investigation reveals a surprising finding: **Code Llama 7B exhibits ECE of 0.53 on MBPP**—dramatically higher than the 0.08-0.15 typical for image classifiers. While this initially seemed problematic, we realized this creates an opportunity: temperature scaling achieves **84.8% ECE reduction** (vs. 5-15% for CNNs), demonstrating that generative tasks benefit more from calibration than discriminative ones.

Our work makes the following contributions:

**First ECE benchmark for code generation.** To our knowledge, we quantify baseline calibration quality for Code Llama 7B on MBPP, establishing ECE of 0.53—the first such measurement for code generation models. This is 3-6× higher than previously studied classification tasks, suggesting autoregressive generation amplifies miscalibration.

**Demonstration of larger calibration effects.** We show that standard temperature scaling reduces ECE by 84.8% (0.53 → 0.08), substantially exceeding both our MUST_WORK validation gate (≥30%) and prior work on CNNs (5-15%). This suggests calibration methods designed for classification transfer effectively to generation but produce proportionally larger improvements.

**Analysis of why generation amplifies miscalibration.** We provide theoretical and empirical analysis explaining why code generation exhibits worse calibration than classification: length-normalized log-probabilities aggregate overconfidence across tokens, and binary evaluation (correct/incorrect code) creates sharper confidence distributions than multi-class problems.

**Foundation for confidence-based iteration control.** By establishing calibrated confidence as a reliable signal, our work enables future research on adaptive resource allocation policies in agentic code generation systems—where confidence scores gate decisions about execution, self-critique, and iteration.

Our results suggest that calibration is not just a reliability problem—it's a foundational capability for agentic systems that must make resource allocation decisions under uncertainty. As code generation evolves from single-shot prediction to multi-step reasoning, calibrated confidence becomes essential for knowing when to iterate, when to execute, and when to stop.
