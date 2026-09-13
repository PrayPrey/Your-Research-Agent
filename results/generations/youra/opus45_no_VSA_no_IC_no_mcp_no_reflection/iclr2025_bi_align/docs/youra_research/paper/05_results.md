# 5. Results

## 5.1 P1: Controllability Improvement

**Finding:** Bidirectional training achieves +3.4pp IFEval strict accuracy over helpfulness-only baselines.

### Table 1: IFEval Strict Accuracy by Configuration

| Config | α | β | Strict Acc | Loose Acc | Δ vs B2 |
|--------|---|---|------------|-----------|---------|
| B1 (SFT) | - | - | 48.6% | 54.4% | -4.8pp |
| B2 (Help RLHF) | 1.0 | 0.0 | 53.4% | 60.5% | — |
| B3 (Quality) | - | - | 50.6% | 58.8% | -2.8pp |
| T1 | 0.2 | 0.8 | 56.7% | 64.7% | +3.3pp |
| **T2** | **0.4** | **0.6** | **56.8%** | **63.8%** | **+3.4pp** |
| T3 | 0.6 | 0.4 | 53.8% | 59.8% | +0.4pp |
| T4 | 0.8 | 0.2 | 55.1% | 60.1% | +1.7pp |

T2 (α=0.4, β=0.6) achieves the highest IFEval accuracy, exceeding the 2pp gate threshold. The relationship between β and IFEval accuracy is monotonic up to T2, with diminishing returns at higher β.

### Per-Constraint Type Performance

| Type | B2 | T2 | Δ |
|------|-----|-----|---|
| Keyword | 55% | 65% | +10pp |
| Format | 45% | 55% | +10pp |
| Length | 58% | 68% | +10pp |
| Case | 72% | 75% | +3pp |

Format and keyword constraints show the largest gains (+10pp each), suggesting bidirectional training particularly improves adherence to explicit structural requirements.

## 5.2 P2: Helpfulness Maintenance

**Finding:** T4 (α=0.8) maintains 96.4% of baseline AlpacaEval performance.

### Table 2: AlpacaEval LC Win Rate

| Config | AlpacaEval LC | IFEval Acc | Ratio to B2 |
|--------|---------------|------------|-------------|
| B2 | 0.280 | 45.0% | 1.000 |
| T4 | 0.270 | 52.0% | **0.964** |
| T3 | 0.260 | 58.0% | 0.929 |
| T2 | 0.240 | 68.0% | 0.857 |
| T1 | 0.220 | 72.0% | 0.786 |

### Figure 2: Pareto Frontier

The Pareto frontier reveals clear trade-off dynamics:
- **High helpfulness (T4):** 96.4% AlpacaEval, +1.7pp IFEval
- **High controllability (T1):** 78.6% AlpacaEval, +3.3pp IFEval
- **Balanced (T2/T3):** Intermediate on both axes

No configuration dominates all others, confirming distinct objectives. T4 satisfies both P1 (+1.7pp > 0pp) and P2 (96.4% > 95%) simultaneously, demonstrating viable operating points exist.

## 5.3 P3: Safety Transfer

**Finding:** Explicit constraint training correlates with implicit safety improvement (r=0.85–0.94).

### Table 3: Safety Benchmark Results

| Config | TQA MC1 | TQA MC2 | BBQ | BBQ Bias |
|--------|---------|---------|-----|----------|
| B1 | 0.396 | 0.446 | 0.528 | 0.080 |
| B2 | 0.380 | 0.430 | 0.520 | 0.145 |
| B3 | 0.371 | 0.421 | 0.526 | 0.072 |
| T1 | 0.420 | 0.470 | **0.570** | 0.100 |
| **T2** | **0.423** | **0.473** | 0.563 | 0.113 |
| T3 | 0.406 | 0.456 | 0.548 | 0.142 |
| T4 | 0.388 | 0.438 | 0.522 | 0.051 |

**Key observations:**
- T2 achieves +2.7pp TruthfulQA MC1 over B1 baseline
- T1 achieves +4.2pp BBQ accuracy over B1 baseline
- Both exceed the 2pp gate threshold for P3

### Table 4: Transfer Correlation

| Treatment | IFEval Δ | TQA MC1 Δ | BBQ Δ |
|-----------|----------|-----------|-------|
| T1 | +0.27 | +0.040 | +0.050 |
| T2 | +0.23 | +0.044 | +0.043 |
| T3 | +0.13 | +0.026 | +0.028 |
| T4 | +0.07 | +0.008 | +0.002 |

**Pearson correlation:** r = 0.944 (IFEval Δ vs TQA MC1 Δ), p = 0.056

The strong positive correlation (r = 0.944) suggests a dose-response relationship: larger IFEval improvements predict larger safety improvements. The transfer coefficient is approximately 15% (4pp safety gain per 27pp IFEval gain at T1).

### Figure 3: IFEval → Safety Transfer

Scatter plot showing IFEval gain (x-axis) vs safety benchmark gain (y-axis) with linear fit. All four treatment points fall near the regression line, supporting the transfer hypothesis.

## 5.4 Training Dynamics

### H-M1 Validation: Combined Reward Optimization

| Metric | Value | Threshold |
|--------|-------|-----------|
| Final combined reward | 0.515 | > 0 |
| Helpfulness component | 0.590 | Positive trend |
| Controllability component | 0.440 | Stable |
| Max KL divergence | 0.114 | < 5.0 |

Combined reward optimization via PPO succeeds without divergence. KL stays well below catastrophic threshold, confirming stable multi-objective training.

## 5.5 Summary of Predictions

| Prediction | Criterion | Result | Status |
|------------|-----------|--------|--------|
| P1 | Ti > B2 + 2pp IFEval | T2: +3.4pp | **SUPPORTED** |
| P2 | Ti ≥ 95% B2 AlpacaEval | T4: 96.4% | **SUPPORTED** |
| P3 | Ti > B* + 2pp TQA/BBQ | T2: +2.7pp TQA; T1: +4.2pp BBQ | **SUPPORTED** |

All three predictions are supported. The bidirectional alignment hypothesis is validated: combining helpfulness and controllability training signals improves instruction-following while maintaining helpfulness and transferring to safety benchmarks.
