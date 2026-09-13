# Related Work

## LLM Calibration

Neural network calibration has been extensively studied since Guo et al. (2017) established Expected Calibration Error (ECE) as the standard metric and introduced temperature scaling as a post-hoc calibration method. For LLMs specifically, Kadavath et al. (2022) demonstrated that models possess intrinsic self-knowledge—they can predict whether their own answers are correct at above-chance rates. This suggests that calibration information exists within models but may not surface in standard prompting.

Subsequent work explored various approaches to elicit this calibration information. Lin et al. (2022) trained models to express uncertainty in natural language, while Xiong et al. (2023) provided a comprehensive evaluation of confidence elicitation methods, comparing direct prompting, multi-sample consistency, and linguistic confidence markers. Tian et al. (2023) specifically studied prompting strategies for calibration, demonstrating that "just asking" for confidence can yield reasonable estimates.

## Chain-of-Thought Prompting

Wei et al. (2022) introduced chain-of-thought prompting, showing that prompting models to reason step-by-step dramatically improves performance on reasoning tasks. Kojima et al. (2022) extended this to zero-shot settings with the simple prompt "Let's think step by step." Wang et al. (2023) introduced self-consistency, using multiple samples with majority voting to improve reliability.

These works focus primarily on accuracy rather than calibration. A key observation from this literature is that CoT produces visible reasoning traces, which could in principle reveal model uncertainty through linguistic markers like hedging words and qualifications.

## Uncertainty Quantification in NLP

The NLP literature has long recognized linguistic hedging as markers of epistemic uncertainty (Hyland, 1998). In the context of LLMs, Kuhn et al. (2023) proposed semantic uncertainty, clustering semantically equivalent responses to estimate uncertainty. This approach leverages response diversity as an implicit uncertainty signal.

Our work differs from prior approaches in systematically isolating the mechanism by which CoT might improve calibration. While Tian et al. (2023) tested various prompting strategies and Xiong et al. (2023) evaluated elicitation methods, neither decomposed the CoT+confidence combination into its component mechanisms. We provide the first systematic verification that (1) CoT produces hedging markers, (2) these markers are structurally positioned to influence confidence generation, and (3) they negatively correlate with verbalized confidence, supporting a "self-reading" interpretation.
