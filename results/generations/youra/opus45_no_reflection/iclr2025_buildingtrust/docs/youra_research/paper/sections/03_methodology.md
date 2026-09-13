# Methodology

We describe our approach to testing the calibration-mediation hypothesis. The methodology involves three phases: metric collection, correlation analysis, and mediation testing.

## Hypothesis and Predictions

**Core Hypothesis**: Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

This yields three testable predictions:

- **P1**: Cross-model correlation r > 0.5 between MC1 and (1-ASR)
- **P2**: ECE mediates ≥30% of the correlation
- **P3**: Temperature scaling improves both metrics

## Model Selection

We evaluate 12 open-weight LLMs spanning four families:

| Family | Models | Size Range |
|--------|--------|------------|
| Llama-2 | 7B, 13B, 70B | 7B-70B |
| Llama-3 | 8B, 70B | 8B-70B |
| Mistral | 7B-v0.1, 7B-Instruct | 7B |
| FLAN-T5 | base, large, xl | 250M-3B |
| Phi | Phi-2, Phi-3-mini | 2.7B-3.8B |

Diversity across architectures (encoder-decoder vs. decoder-only), scales, and training approaches enables testing correlation generalizability. All models are open-weight with accessible logits, enabling ECE computation.

## Metrics

### Factuality: TruthfulQA MC1

We use the multiple-choice single-answer (MC1) format from TruthfulQA \cite{lin2022truthfulqa}. Given a question with one correct and several incorrect answers, we compute accuracy based on highest log-probability selection. We evaluate the full validation set (817 questions) using lm-evaluation-harness.

### Robustness: TextFooler (1 - ASR)

We apply TextFooler \cite{jin2019textfooler} to SST-2 sentiment classification. For each model, we attack 500+ examples, measuring Attack Success Rate (ASR)—the fraction of successful attacks. Robustness is defined as (1 - ASR), ranging from 0 (all attacks succeed) to 1 (no attacks succeed).

### Calibration: ECE

Expected Calibration Error measures the gap between confidence and accuracy:

$$ECE = \sum_{b=1}^{B} \frac{|B_b|}{n} |acc(B_b) - conf(B_b)|$$

We use 10 equal-frequency bins computed from TruthfulQA predictions. Lower ECE indicates better calibration.

## Analysis Pipeline

### Phase 1: Correlation Analysis

1. Compute Pearson correlation between MC1 and (1-ASR) across all models
2. Generate bootstrap 95% confidence intervals (1000 resamples)
3. Test significance at α = 0.05

**Success criterion**: r > 0.5 with p < 0.05

### Phase 2: Confound Control

1. **Partial correlation**: Control for log(parameters) to exclude scale as confound
2. **Within-family analysis**: Test whether correlation holds within Llama, Mistral, etc.

**Success criterion**: Partial r > 0.3 after scale control

### Phase 3: Mediation Analysis

Baron-Kenny mediation with ECE as mediator:
1. Path c: MC1 → (1-ASR) (total effect)
2. Path a: MC1 → ECE
3. Path b: ECE → (1-ASR), controlling for MC1
4. Indirect effect: a × b
5. Sobel test for significance

**Success criterion**: Indirect effect accounts for >30% of total effect

### Phase 4: Intervention

Temperature scaling on 2-3 models:
1. Optimize temperature T on validation set to minimize ECE
2. Re-evaluate MC1 and ASR with calibrated model
3. Compare before/after

**Success criterion**: Both MC1 and (1-ASR) improve for ≥2/3 models

## Implementation

The evaluation pipeline is implemented in Python using:
- lm-evaluation-harness for TruthfulQA evaluation
- TextAttack for TextFooler attacks
- scipy and statsmodels for statistical analysis
- matplotlib for visualization

Code is structured as modular components (config.py, run_eval.py, analyze.py, visualize.py) enabling reproducibility.
