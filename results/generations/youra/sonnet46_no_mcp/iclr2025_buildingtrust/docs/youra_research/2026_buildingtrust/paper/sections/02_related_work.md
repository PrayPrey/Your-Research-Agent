# 2. Related Work

Our work sits at the intersection of LLM calibration, hallucination measurement, adversarial robustness evaluation, and multi-dimensional trustworthiness benchmarking. We briefly survey each area, highlighting what each line of work contributes and where the gap we address lies.

## 2.1 LLM Calibration

The calibration of neural networks — the alignment between confidence scores and empirical accuracy — was formalized by Guo et al. [2017], who introduced Expected Calibration Error (ECE) as the standard metric and demonstrated that modern deep networks are systematically overconfident. Kadavath et al. [2022] extended calibration analysis to large language models, showing that P(True) probing can reveal well-calibrated self-knowledge in models like Claude, with calibration improving with scale but varying substantially by task domain. Zhao et al. [2023] demonstrated that generation-based ECE correlates with TruthfulQA hallucination rates across model families — the closest precursor to our work. However, their analysis is limited to specific model comparisons rather than a systematic cross-family correlation study with explicit capability controls, and does not apply factor analysis to test for latent structure.

## 2.2 Hallucination and Factual Reliability

Lin et al. [2021] introduced TruthfulQA, demonstrating that larger language models are not necessarily more truthful — a counterintuitive finding that established hallucination rate as a benchmark-measurable property independent of raw accuracy. Yin et al. [2023] showed that overconfidence and under-refusal are measurable failure modes correlated with model scale, establishing the practical measurability of epistemic failure. Together, these works show that hallucination and miscalibration are related phenomena, but the quantitative relationship across a diverse model population has not been characterized through partial correlation methodology controlling for capability.

## 2.3 Adversarial Robustness

Wang et al. [2021] introduced AdvGLUE, a multi-task adversarial NLP benchmark demonstrating that even high-accuracy models exhibit substantial accuracy drops under adversarial perturbations. Nie et al. [2020] developed ANLI, showing that iterative adversarial filtering reveals persistent brittleness. These works establish adversarial robustness as a distinct evaluation dimension, but do not analyze its correlation with calibration or hallucination across model populations — precisely the analysis we perform.

## 2.4 Multi-Dimensional Trustworthiness Evaluation

Liang et al. [2022] introduced HELM, evaluating language models across 42 scenarios and 7 metrics, explicitly noting that model rankings differ substantially by metric. HELM provides the most comprehensive multi-metric framework but explicitly declines to analyze cross-metric correlations — our work fills this gap. Wang et al. [2023] (DecodingTrust) provide a comprehensive trustworthiness assessment across toxicity, stereotype bias, adversarial robustness, privacy, ethics, and fairness for GPT-3.5/4. DecodingTrust's finding that trustworthiness properties are not uniformly correlated motivates the need for explicit latent structure analysis, but its GPT-only scope limits generalization to the diverse open-weight population we study. Sun et al. [2024] (TrustLLM) evaluate 6 trustworthiness dimensions across 16 LLMs, finding partial correlations between truthfulness and calibration while reporting robustness as largely orthogonal. TrustLLM's finding of "partial but not full" correlation is consistent with our own, but does not employ partial correlation with capability control or factor analysis to quantify the latent structure.

## 2.5 Psychometric Approaches to Model Evaluation

The framing of models-as-subjects and benchmarks-as-items is not new to psychometrics but is novel in the LLM evaluation context. Burnell et al. [2023] argue for more principled statistical approaches to LLM evaluation, and Polo et al. [2024] demonstrate that Item Response Theory can be applied to benchmark data to produce more informative model comparisons. Our application of factor analysis and partial Spearman correlation to cross-property trustworthiness structure extends this methodological thread in a new direction: discovering latent dimensions of *safety-relevant* properties rather than capability.

## 2.6 Positioning

The gap we address is specific: no prior work computes a capability-controlled cross-property correlation matrix across calibration (ECE, Brier), hallucination (TruthfulQA%), and adversarial robustness (AdvGLUE drop, ANLI drop) for a diverse population of open-weight models, followed by factor analysis to test for a coherent latent dimension. DecodingTrust approaches this for GPT models without capability control; TrustLLM approaches this without factor analysis or partial correlation; Zhao et al. approach the calibration–hallucination link without population-level factor analysis. Our work integrates these threads into a unified statistical framework, with the explicit acknowledgment that our current results are synthetic-data pipeline validation pending real-data replication.
