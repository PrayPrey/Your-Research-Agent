## Name

uncertainty_aligned_hedging

## Title

Teaching Language Models to Hedge Honestly: Aligning Linguistic Uncertainty Expressions with Internal Model Confidence

## Short Hypothesis

Current LLMs exhibit a fundamental disconnect between their internal uncertainty (token probabilities, entropy) and their linguistic expressions of uncertainty (hedging language like 'I think', 'probably', 'I'm certain'). We hypothesize that by fine-tuning LLMs with a novel reward signal that penalizes mismatches between internal confidence and linguistic hedging intensity, we can produce models that naturally communicate appropriate uncertainty through language - reducing user overreliance on incorrect confident responses without requiring explicit confidence scores in the interface.

## Related Work

Zhou et al. (2023) showed LLMs are highly sensitive to epistemic markers in prompts but found their behavior reflects mimicking rather than true uncertainty. Leng et al. (2024) demonstrated RLHF causes verbalized overconfidence and proposed reward calibration, but focused on explicit numerical confidence rather than natural hedging language. Rathi et al. (2025) showed users overrely on overconfident generations across languages. Zhang et al. (2025) proposed aligning verbalized confidence with internal confidence but used explicit confidence scores rather than natural linguistic hedging. Tao et al. (2025) studied linguistic confidence and proposed mapping hedges to scores, but did not train models to generate appropriately hedged responses. Our work is distinct in that we directly train models to generate natural hedging language (not numerical scores) that reflects internal uncertainty, addressing the human-facing communication problem rather than just calibration metrics.

## Abstract

Large language models frequently express unwarranted certainty in their responses, even when their internal probability distributions indicate substantial uncertainty. This mismatch leads to user overreliance and eroded trust when errors occur. While prior work has focused on calibrating explicit confidence scores or studying how epistemic markers affect model behavior, we propose a fundamentally different approach: training LLMs to naturally express appropriate linguistic uncertainty through hedging language that reflects their true internal confidence. We introduce Uncertainty-Aligned Hedging (UAH), a fine-tuning framework that uses reinforcement learning with a novel reward function combining response correctness with hedging-confidence alignment. Specifically, we measure the intensity of hedging expressions in generated text (using a learned hedging classifier) and compare it against internal uncertainty metrics (entropy, token probability variance). The reward penalizes high-confidence language on uncertain predictions and uncertain language on confident correct predictions. We evaluate UAH on question-answering benchmarks across multiple domains, measuring both traditional calibration metrics and novel hedging-alignment metrics. Human studies assess whether UAH-trained models reduce overreliance compared to baseline models and models with explicit confidence displays. Our approach offers a more natural, human-centered path to trustworthy AI communication that integrates seamlessly into conversational interfaces without requiring additional UI elements for confidence display.

## Experiments

**Experiment 1: Hedging Classifier Development**
- Train a RoBERTa-based classifier to score hedging intensity (0-1) on a scale from certain ('definitely', 'I know') to uncertain ('maybe', 'I think', 'possibly')
- Use existing linguistic datasets of epistemic markers plus GPT-4 generated examples
- Validate against human annotations on 500 sentences
- Metrics: correlation with human hedging perception, F1 for categorical hedging detection

**Experiment 2: UAH Fine-tuning**
- Base models: Llama-3-8B, Mistral-7B
- Datasets: TriviaQA, Natural Questions, SciQ (diverse domains)
- Reward function: R = α*correctness + β*alignment_score, where alignment_score = -|hedging_intensity - normalized_entropy|
- Compare against: (1) base model, (2) standard RLHF, (3) PPO-M from Leng et al.
- Metrics: ECE (expected calibration error), hedging-uncertainty correlation, accuracy

**Experiment 3: Hedging-Confidence Alignment Analysis**
- Measure correlation between hedging intensity in responses and internal entropy/probability
- Analyze by question difficulty and domain
- Metrics: Pearson/Spearman correlation, alignment error across confidence bins

**Experiment 4: Human Reliance Study (n=150)**
- Between-subjects design: (1) base model, (2) UAH model, (3) base model + explicit confidence score
- Task: Answer trivia questions with AI assistance, decide whether to trust AI answer
- Measure: overreliance rate (trusting incorrect answers), underreliance rate, task accuracy, subjective trust ratings
- Hypothesis: UAH reduces overreliance comparably to explicit confidence while feeling more natural

## Risk Factors And Limitations

1. **Hedging classifier accuracy**: The quality of UAH depends on reliably measuring hedging intensity; errors in classification could introduce noise into training.
2. **Gaming the reward**: Models might learn superficial hedging patterns without true uncertainty reflection, adding hedges randomly.
3. **Cultural/linguistic variation**: Hedging norms vary across languages and cultures; our approach may not generalize globally without adaptation.
4. **Trade-off with helpfulness**: Excessive hedging could reduce perceived helpfulness; finding the right balance is crucial.
5. **Internal uncertainty validity**: Token-level entropy may not perfectly capture true model uncertainty, especially for reasoning tasks.
6. **Human study limitations**: Lab settings may not reflect real-world reliance patterns; effect sizes could differ in deployment.
7. **Computational cost**: RLHF training requires significant compute; we mitigate by using 7-8B parameter models and efficient implementations.

