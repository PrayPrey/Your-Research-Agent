# Related Work

## RLHF Evaluation and Benchmarks

Reinforcement Learning from Human Feedback has become the standard approach for aligning language models with human preferences. Ouyang et al. introduced InstructGPT using RLHF to improve helpfulness and safety. Evaluation typically relies on aggregate benchmark metrics—TruthfulQA measures factual accuracy, ETHICS assesses moral reasoning, and HHH evaluates helpfulness, harmlessness, and honesty.

However, these benchmarks report aggregate accuracy without task-level analysis. Lin et al. note that TruthfulQA tasks vary in difficulty and type, but evaluation proceeds uniformly. Our work differs by clustering tasks by behavioral signals (calibration patterns), enabling mechanism investigation at the task-type level rather than aggregate statistics.

## Model Calibration

Calibration measures alignment between model confidence and actual correctness. Guo et al. demonstrated that neural networks, especially after scaling, exhibit miscalibration—typically overconfidence. For language models, calibration is computed from output logprobs.

Prior work treats miscalibration as a general phenomenon. We show calibration inversion clusters systematically (silhouette = 0.6016), indicating specific task types trigger miscalibration rather than uniform overconfidence. This clustering enables mechanism investigation.

## Bidirectional Alignment Framework

Shen et al. proposed a theoretical framework distinguishing AI-to-Human alignment (model adapts to user) from Human-to-AI alignment (user adapts to model). Their review of 400+ papers established theoretical foundations but provided no empirical methodology.

Our work operationalizes this framework. We hypothesize that tasks requiring bidirectional adaptation correlate with calibration inversion, since RLHF training conflates correctness with user-state-modeling. While our keyword-based feature detection proved insufficient (2.3% prevalence), we verify the underlying mechanism chain, providing empirical grounding for the theoretical framework.

## Reward Model Analysis

Stiennon et al. analyzed reward model behavior, showing learned rewards correlate with human preferences. Bai et al. documented reward hacking where models exploit reward model weaknesses.

Our contribution is connecting reward model behavior to annotator behavior. We show annotators provide indistinguishable ratings for task types (rate_diff = 0.001), and this conflation propagates to reward models (overlap = 0.647) and model representations (separation = 0.024). This provides mechanism explanation for previously observed reward model limitations.

## Task Classification in Benchmarks

Existing benchmarks classify tasks by topic (TruthfulQA categories) or format (multiple choice vs open-ended) but not by directionality requirements. Perez et al. proposed task categorization for safety evaluation; Ganguli et al. examined task types for red-teaming.

We propose behavioral classification—grouping tasks by calibration patterns rather than surface features. This reveals structure invisible to topic-based classification and enables mechanism investigation.

## Positioning

Prior work either evaluates RLHF outcomes (benchmark accuracy) or analyzes mechanisms in isolation (reward model properties). We bridge these by using behavioral patterns (calibration clustering) to investigate training mechanisms (reward conflation). The negative result for keyword-based feature detection establishes methodological boundaries while the positive results for mechanism verification provide theoretical grounding.
