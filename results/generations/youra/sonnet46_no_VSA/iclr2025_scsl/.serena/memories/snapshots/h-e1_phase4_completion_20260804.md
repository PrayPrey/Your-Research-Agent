# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-04T00:45:00+00:00
**Hypothesis:** h-e1
**Statement:** Per-sample CV of last-layer fc gradient norms across B=20 SGD micro-steps at epoch t*=1 (eval mode) achieves AUROC ≥ 0.80 for Waterbirds 4-group minority membership prediction
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)

## Results
- AUROC: 0.2828 (threshold: 0.80)
- Gate Type: MUST_WORK
- Gate Satisfied: false
- N samples: 4795
- B micro-steps: 20
- Minority mean CV: 0.5355
- Majority mean CV: 1.1981
- Signal direction: INVERTED (majority > minority)
- Train loss (epoch 1): 0.8479
- Train accuracy (epoch 1): 70.9%

## Reflection
- Outcome: ROUTED_TO_PHASE_0
- Root cause: Gradient CV at epoch t*=1 reflects dataset imbalance (73% majority), not sample difficulty
- Inverted signal confirmed: 1-CV gives AUROC≈0.72 (still below threshold)
- Core assumption violated: minority does NOT have higher gradient CV at epoch 1

## Key Lessons for Phase 2A Reference
- Do NOT use CV across mini-steps at epoch 1 — inverted for Waterbirds + pretrained ResNet50
- Gradient magnitude (not variability) may be the operative signal — see PGD methodology
- Later epoch (t*=10 or t*=40) may work where spurious correlation exploitation is established
- vmap+grad over direct FC linear computation works reliably (NOT functional_call)
- WaterbirdsDataset: group = 2*y + place (WILDS format, no explicit group column)
- ResNet50 pretrained initialization "solves" minority samples before fine-tuning starts

## Reusable Infrastructure
- code/dataset.py: WaterbirdsDataset + get_dataloader (validated)
- code/model.py: build_model + train_one_epoch (validated)
- code/gradient.py: _extract_features_no_grad + vmap+grad per-sample FC norm (validated)
- code/evaluate.py: compute_auroc + verify_mechanism_activated (validated)
- code/visualize.py: 5-figure generation pipeline (validated)

---
*Per-hypothesis snapshot for Phase 2A reference*
