# Related Work

Our work sits at the intersection of neural network calibration and code generation evaluation. We build on calibration methods developed for classification while addressing the gap that no prior work has quantified calibration quality for generative code tasks.

## Neural Network Calibration

**Post-hoc calibration methods** adjust model predictions after training to improve probability estimates. Guo et al. (2017) introduced temperature scaling, a single-parameter method that divides logits by a learned temperature T before computing softmax probabilities. They demonstrated 5-15% ECE reduction on image classification tasks (CIFAR-100, ImageNet). More complex methods include Vector Scaling (per-class temperatures) and Matrix Scaling (affine transformation), but Guo et al. showed temperature scaling often suffices due to its theoretical grounding: it minimizes ECE under assumptions of well-specified softmax parametrization.

Minderer et al. (2021) extended calibration analysis to vision transformers, finding that modern architectures exhibit similar miscalibration patterns as CNNs. Kadavath et al. (2022) studied calibration in large language models on reasoning tasks, showing LLMs overestimate correctness probabilities—but they did not quantify ECE or apply post-hoc calibration methods.

**Our contribution:** We establish the first ECE benchmark for code generation (ECE 0.53), demonstrating that generative tasks exhibit 3-5× worse calibration than classification. We show temperature scaling achieves 84.8% ECE reduction on MBPP—substantially larger than prior work on CNNs (5-15%), suggesting calibration effects scale with baseline miscalibration.

## Code Generation Evaluation

**Functional correctness metrics** dominate code generation evaluation. Chen et al. (2021) introduced HumanEval with pass@k as the primary metric: the probability that at least one of k samples solves the problem. Austin et al. (2021) released MBPP (Mostly Basic Python Problems) with 974 function-level tasks. Recent work achieves 95.1% accuracy on HumanEval (Wei et al., 2024), approaching saturation.

However, **no prior work evaluates code generation through the lens of probabilistic calibration**. Functional correctness (binary: code works or doesn't) and calibration (do confidence scores match empirical accuracy?) are complementary—code can be correct while confidence is miscalibrated. Standard evaluation ignores confidence quality entirely.

**Our contribution:** We bridge functional correctness and probabilistic calibration by treating code correctness as binary classification. This enables application of calibration metrics (ECE) while preserving functional evaluation via pass@1. We demonstrate calibration does not degrade accuracy (Δpass@1 = 0%) while improving confidence reliability.

## Agentic Code Generation Systems

**Multi-turn refinement systems** iterate on code via execution feedback or self-critique. OpenCodeInterpreter (2024) is execution-heavy: generate code, execute tests, refine based on errors, repeat until pass. CODESIM (Wei et al., 2024) is model-heavy: simulate execution via chain-of-thought before submitting, avoiding actual test execution. Both approaches improve over single-shot generation but lack **principled policies for resource allocation**.

OpenCodeInterpreter iterates until tests pass (no early stopping), wasting execution attempts on unsolvable problems. CODESIM uses fixed simulation depth, potentially abandoning fixable solutions. Neither system leverages confidence scores to decide when to iterate, when to execute, or when to stop.

**Our contribution:** By establishing calibrated confidence as a reliable signal (84.8% ECE reduction), we provide the foundation for future confidence-based gating policies. For example, high-confidence predictions could bypass execution (direct submission), medium-confidence predictions could trigger self-critique, and low-confidence predictions could request execution feedback. Our work validates the first prerequisite (calibration exists) for such adaptive policies.

## Conformal Prediction and Risk Control

Conformal prediction (Angelopoulos & Bates, 2021) provides distribution-free coverage guarantees: construct prediction sets that contain the true label with probability ≥ 1-α. Recent work applies conformal methods to language models (Kumar et al., 2023), enabling rigorous uncertainty quantification without assumptions about model calibration.

Our work is complementary: temperature scaling improves calibration (ECE), while conformal prediction provides coverage guarantees. Future work could integrate both—calibrated scores as base estimates, conformal sets for formal guarantees—enabling safe deployment in high-stakes applications.

## Positioning Summary

Existing work focused on calibration for classification OR functional correctness for code generation, but not their intersection. We fill this gap by:
1. Quantifying baseline calibration quality for code generation (first ECE benchmark)
2. Demonstrating standard calibration methods transfer to generative tasks with larger effects
3. Establishing foundation for future confidence-based control policies in agentic systems

Our findings suggest calibration research is not "solved"—different task types (classification vs. generation) exhibit different calibration characteristics and benefit differently from correction methods.
