# Related Work

## Reward Model Evaluation

RewardBench (Lambert et al., 2024) established the first standardized benchmark for evaluating reward models, measuring accuracy across chat, safety, and reasoning categories. Top models achieve 80–85% aggregate accuracy. However, this aggregate view treats all errors equally and provides no decomposition of *where* failures occur. Our work complements RewardBench by introducing mode-based decomposition that stratifies performance by human-RM agreement patterns.

The Alignment Ceiling (Lambert & Calandra, 2023) identified objective mismatch in RLHF: reward models overoptimize proxy objectives that diverge from true human intent. This work demonstrated that reward model training contains systematic biases, but did not quantify the prevalence of overconfident misalignment in preference data. We build on this foundation by operationalizing "overconfident misalignment" as Mode 3 (high human entropy, low RM variance) and measuring its proportion in real data.

## LLM-as-Judge Evaluation

Wei et al. (2024) systematically evaluated LLM judges for alignment tasks, finding that prompt templates and judge models significantly affect reliability. Their analysis focused on agreement rates between LLM judges and human annotators. Our work differs by examining reward model confidence rather than LLM judge outputs, and by conditioning analysis on human disagreement (entropy) rather than treating human labels as ground truth.

## Bidirectional Alignment Frameworks

Shen et al. (2024) proposed the Bidirectional Human-AI Alignment framework, systematically reviewing 400+ papers spanning HCI, NLP, and ML. Their taxonomy distinguishes AI-to-human alignment (systems matching human specifications) from human-to-AI alignment (human ability to understand and evaluate AI). Our work contributes to AI-to-human alignment measurement by revealing that reward models exhibit systematic overconfidence on human-disagreement samples—a failure pattern invisible to aggregate metrics.

## Human Preference Analysis

Prior work on Chatbot Arena has analyzed win rates, model rankings, and voting patterns (Zheng et al., 2024). Studies have noted that human preferences depend on style, formatting, and presentation beyond semantic content. Our finding that Mode 3 response pairs have *higher* semantic similarity than Mode 1 pairs aligns with this literature: misalignment may stem from stylistic or structural features that embedding similarity fails to capture.

## Uncertainty in Reward Models

Research on epistemic uncertainty in neural networks (Gal & Ghahramani, 2016) provides foundations for RM variance estimation. Ensemble methods remain standard for uncertainty quantification. Our use of RM variance as a proxy for model confidence follows this tradition, though we note limitations from using a single RM with score difference rather than a full ensemble.

## Mode Decomposition Approach

Our 2×2 mode framework draws inspiration from signal detection theory and confusion matrix analysis but applies to preference data. Rather than true/false positive framing, we cross two continuous dimensions (entropy, variance) to identify four qualitatively distinct alignment modes. The near-uniform distribution across modes (23.7–26.3% per cell) suggests entropy and variance capture genuinely orthogonal information about preference battles, validating the decomposition approach.
