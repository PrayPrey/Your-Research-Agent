# Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Does a significant positive correlation exist between TruthfulQA MC1 and AdvGLUE accuracy after controlling for model size?

**RQ2:** Does model calibration (ECE) correlate with truthfulness and/or robustness?

**RQ3:** Does calibration moderate the truthfulness-robustness correlation?

## Models

We evaluate 14 decoder-only LLMs spanning four families and a range of scales:

| Family | Models | Parameters |
|--------|--------|------------|
| Pythia | pythia-70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b | 70M–12B |
| Llama-2 | llama-2-7b, 13b, 70b (base) | 7B–70B |
| Mistral | mistral-7b | 7B |
| Falcon | falcon-7b, falcon-40b | 7B–40B |

**Rationale:** Multiple families prevent family-specific artifacts. The size range (70M–70B) enables controlling for scale as a confounder.

## Benchmarks

**TruthfulQA MC1** [Lin et al., 2022]: 817 questions designed to elicit imitative falsehoods. MC1 format presents one correct answer among distractors; accuracy measures truthful response selection.

**AdvGLUE** [Wang et al., 2022]: Adversarial variants of GLUE tasks with word-level perturbations (character swaps, synonym replacements) that preserve semantics. We report average accuracy across subtasks.

**MMLU** [Hendrycks et al., 2021]: 57-subject multiple-choice benchmark used only for ECE computation on a neutral reference task.

## Evaluation Protocol

All evaluations use lm-evaluation-harness [Gao et al., 2023]:
- Batch size: automatically determined per model
- Prompt format: default harness templates
- Decoding: greedy (temperature=0) for reproducibility
- Seed: 42

## Metrics

**Primary Metric (RQ1):** Partial Pearson correlation between TruthfulQA MC1 and AdvGLUE accuracy, controlling for log(parameters).

**Mechanism Metrics (RQ2-3):**
- Expected Calibration Error (ECE): 15-bin ECE on MMLU predictions
- ECE-metric correlations: Pearson r between ECE and each trust metric
- Moderation test: Fisher's z-test comparing truthfulness-robustness correlation across ECE tertiles

**Statistical Thresholds:**
- Significance: p < 0.05
- Minimum effect size: |r| > 0.3
- Confidence intervals: 95% via bootstrap (1000 iterations)

## Hypotheses and Gates

| ID | Question | Success Criterion | Gate |
|----|----------|-------------------|------|
| h-e1 | Correlation exists? | r > 0.3, p < 0.05, CI > 0 | MUST_WORK |
| h-m1 | ECE predicts metrics? | r < -0.2 for both | SHOULD_WORK |
| h-m2 | ECE moderates correlation? | Low-ECE r > High-ECE r | SHOULD_WORK |
| h-c1 | Pattern holds across model types? | r > 0.2 for base and IT | SHOULD_WORK |

The MUST_WORK gate (h-e1) determines whether the core finding stands; SHOULD_WORK gates test the calibration mechanism.
