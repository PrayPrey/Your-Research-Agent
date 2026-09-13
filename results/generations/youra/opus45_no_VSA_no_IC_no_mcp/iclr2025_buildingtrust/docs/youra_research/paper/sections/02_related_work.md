# Related Work

Our work connects three previously separate research areas: truthfulness evaluation, adversarial robustness, and model calibration. We review each and position our contribution.

## Truthfulness Evaluation

TruthfulQA [Lin et al., 2022] introduced a benchmark measuring whether language models generate truthful answers, finding that larger models are not necessarily more truthful and may actually reproduce misconceptions more fluently. Subsequent work examined truthfulness in specific domains [Evans et al., 2021] and explored interventions such as RLHF to improve truthful behavior [Ouyang et al., 2022]. However, these studies evaluate truthfulness in isolation, without examining relationships to other trust dimensions such as adversarial robustness.

## Adversarial Robustness

AdvGLUE [Wang et al., 2022] provides a multi-task adversarial benchmark with word-level perturbations across GLUE tasks. Earlier work established adversarial vulnerabilities through TextFooler [Jin et al., 2020] and BERT-Attack [Li et al., 2020], while RobustnessGym [Goel et al., 2021] unified robustness evaluation across slices. These studies characterize robustness vulnerabilities but do not examine whether robust models are also truthful, leaving the relationship between these capabilities unexplored.

## Calibration in Language Models

Guo et al. [2017] formalized Expected Calibration Error (ECE) showing modern neural networks are poorly calibrated. For language models, Zhao et al. [2021] demonstrated that contextual calibration improves few-shot performance, suggesting calibration reflects model uncertainty quality. Kadavath et al. [2022] examined whether models "know what they know," connecting calibration to epistemic uncertainty.

Calibration provides an intuitive hypothesis for why truthfulness and robustness might correlate: a well-calibrated model accurately estimates uncertainty, potentially enabling both refusal of uncertain claims (truthfulness) and detection of anomalous inputs (robustness). We directly test this hypothesis.

## Multi-Dimensional Trust

While individual trust dimensions have been studied extensively, systematic examination of their relationships is sparse. Liang et al. [2023] proposed HELM for holistic evaluation across multiple dimensions, but focused on coverage rather than inter-metric correlation. Our work fills this gap by quantifying the correlation between two specific trust dimensions and testing a mechanistic explanation.

## Our Position

Prior work evaluated truthfulness and robustness independently, leaving their relationship unknown. Calibration work suggested a potential mechanism but did not test it across trust dimensions. We contribute the first systematic correlation analysis between truthfulness and robustness across multiple model families, with direct mechanism testing via ECE moderation analysis.
