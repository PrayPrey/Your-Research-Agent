# Phase 2A Convergence Checks — Audit Trail

**Architecture:** Self-Play Loop (Claude-only, IC-ablation)
**min_exchanges:** 15 | **max_exchanges:** 20

---

## Convergence Check @ Exchange 15

- SPECIFIC:    PASS — Exchange 15 (Dr. Ally synthesis): "GroupDRO-trained backbones encode less spurious background information (lower probe accuracy) than ERM-trained backbones, paired t-test one-sided p<0.05 n=3 seeds"
- MECHANISM:   PASS — Exchanges 4+8 (Prof. Pax): GroupDRO's group-balanced loss gradient signal propagates through all layers, forcing backbone to reduce reliance on spurious features; DFR frozen backbone explains DFR≡ERM probe accuracy (Exchange 4)
- PREDICTIONS: PASS — Exchange 13 (Prof. Vera): H-P0 (DFR backbone cosine similarity ≥ 0.9999), H-P1 (GroupDRO < ERM probe acc, p<0.05), H-P1b (SAM < ERM, exploratory), H-P2 (Pearson r < -0.5 across 9 checkpoints), H-P3 (core probe acc GroupDRO ≥ ERM); tiered success criteria (CONFIRMED/SUGGESTIVE/REJECTED) specified
- NOVELTY:     PASS — Exchange 1 (Dr. Nova): No existing paper reports per-method spurious attribute probe accuracy per seed; Exchange 5 (Dr. Nova): mechanistic distinction backbone-changing vs backbone-preserving methods is novel framing not previously articulated
- FEASIBILITY: PASS — Exchange 8 (Prof. Pax): Forward-pass extraction + sklearn L-BFGS C=1e9 on frozen D=2048 features, full Waterbirds test set; technically sound, mechanically plausible, sklearn convergence guaranteed; NOT computing gradients or Hessians (avoids h-e1, h-m2 failure patterns)
- OBJECTIONS:  PASS — Exchange 10 (Prof. Rex) raised confound (GroupDRO dilution vs suppression); addressed Exchange 11 (Dr. Ally: dilution IS the mechanism); DFR backbone identity concern (Exchange 12) addressed by making H-P0 an empirically testable prerequisite; n=3 power concern (Exchange 2, 10) addressed by tiered criteria + Cohen's d + bootstrap CI
- All personas spoke: PASS — Dr. Nova (1,5,15), Prof. Vera (2,6,13), Dr. Sage (3,7,14), Prof. Pax (4,8), Dr. Ally (9,11,15), Prof. Rex (10,12); all 6 confirmed
- Verdict: CONVERGED

**Convergence at exchange 15 (min_exchanges=15): NATURAL CONVERGENCE**
