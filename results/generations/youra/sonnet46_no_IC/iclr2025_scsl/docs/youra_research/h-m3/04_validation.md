# H-M3 Validation Report: Background Linear Decodability

**Hypothesis**: ERM models encode more background information in layer4 features than GroupDRO models, as measured by linear probe accuracy on background label.

**Gate Type**: MUST_WORK (PoC validation)
**Date**: 2026-08-05

---

## Gate Verdict: CONFIRMED

**Gate Result: PASS**

Evidence:
- ERM mean probe accuracy: 0.9838
- GroupDRO mean probe accuracy: 0.9530
- Direction check: ERM > GroupDRO = True
- Paired t-test p-value (one-sided): 0.0039
- Cohen's d: 6.4759

---

## Probe Accuracy Table (All 9 Checkpoints)

| Method | Seed | Background Probe Accuracy |
|--------|------|--------------------------|
| ERM | 1 | 1.0000 |
| ERM | 2 | 0.9738 |
| ERM | 3 | 0.9776 |
| GroupDRO | 1 | 0.9741 |
| GroupDRO | 2 | 0.9427 |
| GroupDRO | 3 | 0.9422 |
| SAM | 1 | 0.9418 |
| SAM | 2 | 0.9688 |
| SAM | 3 | 0.9605 |

**ERM mean**: 0.9838
**GroupDRO mean**: 0.9530
**SAM mean**: 0.9570

---

## Statistical Test

| Metric | Value |
|--------|-------|
| Test | One-sided paired t-test (H1: ERM > GroupDRO) |
| p-value | 0.0039 |
| Cohen's d | 6.4759 |
| N checkpoints per method | 3 |
| N test samples | 5794 |

---

## Sanity Checks

- ERM mean > 0.6: **PASS** (0.9838)
- All probe accs in [0.5, 1.0]: **PASS**

---

## Verdict Determination

| Criterion | Threshold | Actual | Met |
|-----------|-----------|--------|-----|
| CONFIRMED: p < 0.05 | 0.05 | 0.0039 | YES |
| CONFIRMED: Cohen's d > 0 | 0.0 | 6.4759 | YES |
| SUGGESTIVE: p < 0.10 | 0.10 | 0.0039 | YES |
| SUGGESTIVE: Cohen's d > 0.5 | 0.5 | 6.4759 | YES |

**Final Verdict**: CONFIRMED
**Gate Result**: PASS

---

## Exploratory: SAM Analysis

| Metric | Value |
|--------|-------|
| SAM mean probe acc | 0.9570 |
| SAM vs ERM Cohen's d | 0.9600 |

---

## Figures Generated

1. `figures/gate_metrics.png` — ERM vs GroupDRO grouped bar + paired differences inset
2. `figures/all_probes.png` — All 9 checkpoints bar chart
3. `figures/paired_diff.png` — Paired differences scatter with mean±std
4. `figures/probe_vs_wga.png` — Probe accuracy vs WGA scatter (Pearson r=-0.626)

---

## Conclusion

H-M3 hypothesis is SUPPORTED: ERM models show significantly higher background decodability in layer4 features compared to GroupDRO models.
