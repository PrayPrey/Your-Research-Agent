# Related Work

Our work connects to three research threads: model-based code evaluation metrics, LLM-as-judge for code correctness, and ensemble methods for evaluation. We position our contribution as the first scale-controlled analysis of error patterns in LLM code judges.

## Model-Based Code Evaluation

Traditional code evaluation relies on execution-based metrics such as pass@k (Chen et al., 2021), which measure functional correctness through test execution. While rigorous, execution requires infrastructure and compute that scales poorly with evaluation volume.

Model-based alternatives emerged to approximate execution signals. CodeBERTScore (Zhou et al., 2023) computes semantic similarity using code-pretrained embeddings, achieving higher correlation with human preference than BLEU. However, Naik (2024) demonstrates that CodeBERTScore has only **0.16 correlation** with functional correctness—useful for editing effort prediction (0.72 correlation) but unreliable for correctness judgment. This weak correlation motivates the shift toward LLM-as-judge approaches.

MATCH (Ghoummaid et al., 2025) uses contrastive learning for reference-free evaluation, achieving stronger correctness correlation than ICE-Score. However, MATCH requires task-specific training, limiting generalization.

## LLM-as-Judge for Code

The LLM-as-judge paradigm applies language models to evaluate outputs, originally developed for instruction-following (Zheng et al., 2023) and extended to code domains.

**Bias characterization.** Moon et al. (2025) identify six bias types in LLM code judges: sensitivity to variable names, comments, formatting, and other superficial features. Semantically equivalent code receives different verdicts based on surface presentation. Our work complements this by showing that bias *magnitude* varies by scale.

**Accuracy evaluation.** Crupi et al. (2025) evaluate eight LLMs as judges on 1,405 Java and 1,281 Python methods, finding GPT-4-turbo performs best but "frequently misjudges" correctness. Critically, their study does not control for scale—models differ in both scale and architecture—preventing isolation of the scale effect. Our work fills this gap with systematic 7B/70B/proprietary comparison under fixed evaluation settings.

**Test-time scaling.** Wang et al. (2025) introduce MCTS-Judge, applying System-2 thinking to improve single-model accuracy from 41% to 80%. This approach increases accuracy through test-time compute rather than model scale. Our findings are complementary: MCTS-Judge improves a single judge; we show that combining judges across scales without such compute is counterproductive.

**Ensemble approaches.** SE-Jury (Zhou et al., 2025) proposes an ensemble of five judge strategies with dynamic team selection, achieving 29.6-140.8% improvement over existing metrics. Their ensemble combines evaluation *strategies* within a single model; we test ensemble across model *scales*, finding that scale diversity does not confer similar benefits.

## Ensemble Methods for Evaluation

Ensemble methods assume component errors are approximately IID, enabling majority voting to improve accuracy. Recent work challenges this assumption.

Shu (2026) demonstrates that LLM judge panels share fundamental error modes even when architecturally diverse ("Blind to Pivotal Vote"). Our findings extend this: within scale-diverse panels, errors are not only correlated but systematically asymmetric (over-acceptance vs. under-acceptance), making majority voting actively harmful.

The assumption that disagreement signals uncertainty has been applied in selective prediction and abstention frameworks. Our finding that unanimous agreement correlates with *lower* accuracy inverts this assumption for scale-diverse code judges.

## Execution-Based Benchmarks

Our evaluation uses HumanEval+ (Liu et al., 2023), which augments HumanEval with 80× more test cases, revealing that pass@k drops 19.3-28.9% under rigorous evaluation. This stringent ground truth is essential for measuring judge reliability—weak test suites would mask judge errors that coincidentally match execution noise.

EvalPlus has become the industry standard for code evaluation, with adoption by Meta, DeepSeek, and others. We use its execution results as ground truth rather than participating in debates about test adequacy.

## Summary

Prior work establishes that LLM code judges are biased (Moon et al., 2025) and error-prone (Crupi et al., 2025), that test-time scaling can help single models (Wang et al., 2025), and that correlated errors limit ensemble benefit (Shu, 2026). Our contribution is the first scale-controlled analysis showing that error *types* are scale-dependent (FPR vs. FNR) and that this asymmetry explains ensemble failure—a finding that prior work could not detect without isolating the scale variable.
