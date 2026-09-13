# H-M1 Validation Report

## Hypothesis
Token entropy from Llama-2-7B-chat correlates with answer correctness on TriviaQA.

## Gate Type
MUST_WORK

## Experiment Configuration
- **Model**: meta-llama/Llama-2-7b-chat-hf
- **Dataset**: TriviaQA (rc.nocontext, validation split)
- **Questions**: 100
- **Responses per question**: 10
- **Temperature**: 0.7
- **Entropy formula**: H = -Σ p(t) log p(t)
- **Correctness**: Exact-match with majority voting

## Results

### Gate Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| p-value | < 0.05 | 0.0246 | **PASS** |
| AUROC | > 0.55 | 0.6454 | **PASS** |
| Direction | mean_incorrect > mean_correct | 0.1342 > 0.1104 | **PASS** |

### Additional Statistics
- **t-statistic**: 2.28
- **Cohen's d**: 0.47 (medium effect)
- **Pearson r**: -0.22 (negative correlation as expected)
- **n_correct**: 60 (60%)
- **n_incorrect**: 40 (40%)

## Gate Verdict
**PASS**

All three MUST_WORK criteria satisfied:
1. Statistical significance achieved (p < 0.05)
2. AUROC exceeds target (0.6454 > 0.55)
3. Directional hypothesis confirmed (incorrect answers have higher entropy)

## Figures
- `figures/gate_metrics.png`: Target vs actual comparison
- `figures/entropy_distribution.png`: Entropy histograms by correctness
- `figures/roc_curve.png`: ROC curve with AUC annotation

## Interpretation
Token entropy reliably predicts answer correctness with medium effect size. Higher entropy indicates lower model confidence and correlates with incorrect answers. The signal is actionable for downstream abstention or routing decisions.

## Validation Date
2026-08-19
