# Hypothesis h-e1 Validation Report

## Hypothesis

**Later transformer layers (top-3 of 12) contribute >50% of total influence magnitude on BERT-base/MNLI**

## Gate Type

MUST_WORK

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Model | bert-base-uncased (12 layers, 110M params) |
| Dataset | MNLI (392K train, 9815 validation) |
| Fine-tuning | 1 epoch, lr=2e-5, batch_size=32 |
| Calibration size | 500 samples |
| Metric | Top-3 ratio = sum(layers[9:12]) / sum(layers[0:12]) |
| Success threshold | ratio > 0.50 |

## Results

| Statistic | Value |
|-----------|-------|
| Mean top-3 ratio | 0.2161 |
| Std | 0.0307 |
| 95% CI | [0.2134, 0.2188] |
| n | 500 |

## Verdict

**FALSIFIED**

Mean top-3 ratio (0.216) is substantially below the 0.50 threshold. The 95% confidence interval [0.213, 0.219] excludes the threshold by a wide margin. Top-3 layers contribute approximately 22% of total gradient influence, not >50%.

## Gate Result

**FAIL** (MUST_WORK gate not satisfied)

## Artifacts

- Checkpoint: `src/h-e1/outputs/fast_checkpoint.pt`
- Statistics: `src/h-e1/outputs/fast_summary_statistics.json`
- Layer data: `src/h-e1/outputs/fast_layer_contributions.json`
- Distribution plot: `src/h-e1/outputs/fast_layer_distribution.png`

## Date

2026-08-24
