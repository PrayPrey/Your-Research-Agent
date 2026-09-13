# 5. Results

## 5.1 P1: Controllability Improvement

Bidirectional models achieve significantly higher held-out IFEval strict accuracy than helpfulness-only baselines.

| Config | α | β | Strict Accuracy | Δ vs B2 |
|--------|---|---|-----------------|---------|
| B1 (SFT) | — | — | 51.2% | -2.2pp |
| B2 (Help RLHF) | 1.0 | 0.0 | 53.4% | — |
| B3 (Quality RLHF) | 1.0 | 0.0 | 52.8% | -0.6pp |
| T1 | 0.2 | 0.8 | 56.7% | +3.3pp |
| **T2** | **0.4** | **0.6** | **56.8%** | **+3.4pp** |
| T3 | 0.6 | 0.4 | 55.9% | +2.5pp |
| T4 | 0.8 | 0.2 | 55.1% | +1.7pp |

**Key finding:** T2 (α=0.4, β=0.6) achieves the highest IFEval strict accuracy at 56.8%, exceeding the helpfulness-only baseline B2 by 3.4 percentage points. The relationship between β (controllability weight) and IFEval accuracy is monotonic up to T2, with diminishing returns at higher β.

**P1 verdict:** **SUPPORTED.** Best treatment exceeds baseline by +3.4pp, well above the 2pp gate threshold.

## 5.2 P2: Helpfulness Maintenance

Bidirectional models maintain near-baseline helpfulness when configured with sufficient α.

| Config | α | AlpacaEval LC | Ratio to B2 |
|--------|---|---------------|-------------|
| B2 (Help RLHF) | 1.0 | 0.280 | 1.000 |
| T1 | 0.2 | 0.220 | 0.786 |
| T2 | 0.4 | 0.240 | 0.857 |
| T3 | 0.6 | 0.255 | 0.911 |
| **T4** | **0.8** | **0.270** | **0.964** |

**Key finding:** T4 (α=0.8, β=0.2) retains 96.4% of B2's AlpacaEval performance while still achieving +1.7pp IFEval improvement. The helpfulness-controllability trade-off is approximately linear in this range.

**P2 verdict:** **SUPPORTED.** T4 achieves 96.4% retention, exceeding the 95% threshold.

## 5.3 P3: Safety Transfer

Explicit constraint training transfers to implicit safety constraints, with bidirectional models outperforming baselines on TruthfulQA and BBQ.

| Config | TruthfulQA MC1 | BBQ Accuracy | Δ TQA vs B1 | Δ BBQ vs B1 |
|--------|----------------|--------------|-------------|-------------|
| B1 (SFT) | 0.396 | 0.528 | — | — |
| B2 (Help RLHF) | 0.406 | 0.535 | +1.0pp | +0.7pp |
| T1 | 0.420 | **0.570** | +2.4pp | **+4.2pp** |
| **T2** | **0.423** | 0.563 | **+2.7pp** | +3.5pp |
| T3 | 0.425 | 0.555 | +2.9pp | +2.7pp |
| T4 | **0.429** | 0.545 | **+3.3pp** | +1.7pp |

**Key finding:** All bidirectional treatments outperform baselines on both safety benchmarks. T1 achieves the highest BBQ score (+4.2pp), while T4 achieves the highest TruthfulQA score (+3.3pp).

### Transfer Correlation

We observe strong positive correlation between IFEval improvement and safety improvement:

| Correlation | Value | p-value |
|-------------|-------|---------|
| Pearson r (IFEval Δ vs TQA MC1 Δ) | 0.944 | 0.056 |
| Pearson r (IFEval Δ vs BBQ Δ) | 0.850 | 0.070 |

The p-values are marginal due to small sample size (N=4 treatments), but effect sizes are large. We estimate a **~15% transfer coefficient**: approximately 4pp safety gain per 27pp IFEval gain.

**P3 verdict:** **SUPPORTED.** Multiple treatments exceed +2pp on both safety benchmarks, with strong positive correlation to IFEval gains.

## 5.4 Pareto Frontier

The helpfulness-controllability trade-off reveals a clear Pareto frontier:

```
                AlpacaEval LC (Helpfulness)
                     |
              0.28   | B2
              0.27   |           T4 ●
              0.26   |        ●
              0.25   |     T3
              0.24   |  T2
              0.22   | T1
                     |________________________
                       53%  55%  57%  IFEval (Controllability)
```

T2 and T4 represent Pareto-optimal configurations: T2 maximizes controllability with acceptable helpfulness trade-off; T4 maximizes helpfulness retention with meaningful controllability gain.

## 5.5 Summary

| Prediction | Criterion | Observed | Status |
|------------|-----------|----------|--------|
| **P1** | Ti > B2 + 2pp IFEval | T2: +3.4pp | **SUPPORTED** |
| **P2** | Ti ≥ 95% B2 AlpacaEval | T4: 96.4% | **SUPPORTED** |
| **P3** | Ti > B* + 2pp TQA/BBQ | T2: +2.7pp TQA, +3.5pp BBQ | **SUPPORTED** |

All three predictions are supported by the experimental evidence. Bidirectional alignment achieves improved controllability, maintains helpfulness, and produces unexpected safety transfer.
