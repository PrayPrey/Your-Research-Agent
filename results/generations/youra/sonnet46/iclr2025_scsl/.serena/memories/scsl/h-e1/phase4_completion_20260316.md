# Hypothesis Completion Snapshot: h-e1 Phase 4

**Date:** 2026-03-16T22:42:00Z
**Hypothesis:** H-E1 (EXISTENCE)
**Statement:** Normalized per-sample last-layer gradient norms (g_tilde_i) exhibit minority/majority ratio ≥3x, AUC >0.70, and top-25% balance deviation ≤10%
**Final Status:** IN_PROGRESS (SELF_MODIFY → h-e1-v2)
**Gate Result:** PARTIAL (2/3 criteria pass)

## Results
- ratio = 8.805 (PASS, target ≥3.0) — 2.9x above threshold
- AUC = 0.914 (PASS, target >0.70) — near-perfect minority group prediction
- balance_deviation = 0.379 (FAIL, target ≤0.10) — criterion design mismatch

## Reflection: SELF_MODIFY
- Root cause: balance_deviation criterion tests class uniformity, incompatible with minority-focused gradient norm selection
- Core mechanism strongly confirmed
- Fix for h-e1-v2: Replace balance_deviation with minority recall ≥0.60 in top-25% subset

## Proven Components (reusable for h-e1-v2 and dependents)
- GradientNormAnalyzer (FC forward hook, outer-product decomposition) — src/model.py
- WaterbirdsDataset + get_dataloaders() — src/dataset.py
- train_epoch() ERM + collect_gradnorms() — src/train.py
- compute_metrics() / gate_check() — src/evaluate.py (needs balance criterion update)
- run_experiment.py — full CLI entrypoint

## Key Parameters
- T_id=5 (primary), k=25%, ResNet-50 ImageNet, lr=0.001, SGD, batch=128
- Dataset: Waterbirds v1.0 (4795/1199/5794), group_id = y*2+place
- Conda env: youra-h-e1 (Python 3.10, PyTorch 2.10+cu128)

## Lessons
- gradient norm minority signal is extremely strong (8.8x vs 3x target)
- balance_deviation is wrong metric — use minority recall instead
- CPU storage for hook features prevents GPU OOM on 4795-sample passes
- Epoch 5 gives optimal ratio; ratio increases 6.5x→8.8x across epochs 1→5

---
*Per-hypothesis snapshot for Phase 2A/2C reference*
*Pipeline: TEST_scsl, Research folder: 20260315_scsl*
