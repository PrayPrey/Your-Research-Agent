# 2. Related Work

Our work sits at the intersection of three active research areas: LLM calibration and uncertainty quantification, code generation evaluation, and difficulty-conditioned model analysis. Each area contributes essential context, but none combines them in the way our study requires.

## 2.1 LLM Calibration and Uncertainty Quantification

The foundational work on neural network calibration established Expected Calibration Error (ECE) as the canonical metric for measuring the discrepancy between confidence and accuracy [Guo et al., 2017]. Guo et al. showed that modern neural networks are systematically overconfident after temperature scaling can recover calibration, and they introduced temperature scaling as a post-hoc correction. However, this work measures calibration globally across all inputs — it does not ask whether calibration quality varies with input difficulty.

For LLMs specifically, Kadavath et al. [2022] introduced the P(True) logprob elicitation methodology: append "Is the following answer correct? (True/False)" to a model's own output and extract the logprob ratio as a confidence signal. They showed that P(True) scales with model capability (larger models are better calibrated) and achieves meaningful calibration on question-answering tasks. Critically for our work, the P(True) method is self-contained — it does not require a separate evaluator model. However, Kadavath et al. study P(True) calibration as a function of model scale, not as a function of problem difficulty. Whether P(True) signals degrade systematically on harder problems remains unaddressed.

More recent surveys [Liu et al., 2025; Shorinwa et al., 2024] identify code verification as an open challenge for LLM calibration methods, noting that code problems with binary correctness oracle create a cleaner calibration target than open-ended NLG tasks. These surveys confirm the gap we address but do not close it.

Yin et al. [2023] investigate LLM self-knowledge — whether models correctly identify the questions they cannot answer — finding substantial gaps. Their work focuses on factual questions, not code generation, and measures self-knowledge at the problem level rather than measuring ECE as a calibration property. Vanhoyweghen et al. [2025] find that CoT length is informative only at intermediate difficulty levels, suggesting that difficulty modulates the reliability of LLM reasoning signals; we study an analogous phenomenon for confidence signals.

**Our position:** We extend the P(True) methodology [Kadavath et al., 2022] from capability-scaling analysis to difficulty-stratified calibration. Whereas prior work treats difficulty as a background variable, we make it the primary axis of analysis.

## 2.2 Code Generation Evaluation

Chen et al. [2021] introduced HumanEval and the pass@k metric, establishing the standard for functional code generation evaluation. Austin et al. [2021] contributed MBPP (Mostly Basic Programming Problems) with a broader range of problem types. These benchmarks define the evaluation infrastructure we build on.

Liu et al. [2023] released EvalPlus, augmenting HumanEval and MBPP with substantially more test cases (HumanEval+: 80× more tests; MBPP+: 35× more tests), reducing pass@k inflation from 28.9% on the original benchmarks. EvalPlus is our correctness oracle of choice: the augmented tests provide a more reliable ground truth for computing ECE, reducing noise from false positives.

However, none of these benchmark papers analyze calibration quality. Pass@k measures whether a model can generate correct code; it does not measure whether the model's confidence in its generated code is calibrated. Our work adds a calibration dimension to EvalPlus evaluation.

Rozière et al. [2023] introduced Code Llama, a family of code-adapted models fine-tuned from Llama base weights. This is one of our three test models. Importantly, Code Llama's training data includes a large proportion of common Python utility patterns — a property that, as we find, affects its calibration direction in a non-obvious way.

**Our position:** We use EvalPlus [Liu et al., 2023] as our correctness oracle and supplement pass@k analysis with difficulty-stratified calibration measurement. Prior code evaluation work provides the evaluation infrastructure; we provide the calibration analysis layer.

## 2.3 Difficulty Estimation and Stratified Analysis

Several benchmarks study problem difficulty, but using external labels. BIG-bench [Srivastava et al., 2022] assigns task difficulty through expert annotation and human performance baselines. HELM [Liang et al., 2022] evaluates model capabilities across a spectrum of tasks. These approaches require labels that are not model-specific: a problem labeled "hard" is hard for all models.

Our self-contained difficulty approach — stratifying by each model's own k=5 pass@1 distribution — differs fundamentally. Hard problems are those where a specific model generates 0/5 correct solutions; easy problems are those where it generates 3–5/5 correct solutions. This model-relative definition lets each model reveal its own calibration fingerprint, which our cross-model Jaccard analysis (0.456–0.546) shows is nevertheless 45–55% consistent across architectures.

**Our position:** We propose self-contained difficulty stratification as a model-specific calibration characterization method that avoids the confound of external difficulty labels while still producing architecture-consistent findings.

## 2.4 Summary of Gaps

| Area | What Exists | What's Missing |
|------|-------------|----------------|
| LLM Calibration | P(True) methodology (Kadavath 2022); ECE metric (Guo 2017) | Difficulty-stratified calibration analysis for code |
| Code Evaluation | Pass@k benchmarks (EvalPlus, HumanEval, MBPP) | Calibration quality analysis per difficulty tier |
| Difficulty Analysis | External difficulty labels (BIG-bench, HELM) | Self-contained, model-specific difficulty-calibration fingerprint |
| Architecture Studies | Code-specialized vs. general model comparisons on pass@k | Architecture-stratified calibration direction analysis |

Our work fills the intersection of all four gaps simultaneously.
