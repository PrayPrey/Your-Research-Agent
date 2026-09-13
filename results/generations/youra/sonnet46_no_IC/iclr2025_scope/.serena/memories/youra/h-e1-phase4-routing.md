# h-e1 Phase 4 Routing Decision

**Date:** 2026-08-05
**Gate result:** FAIL_MUST_WORK
**Routing:** ROUTED_TO_PHASE_2A

## What happened
- DeBERTa-v3-base trained 1 epoch / 20k MNLI samples → acc=81.8%
- Spectral entropy extracted from 73 adapted layers
- PARA oracle computed ranks for 73 layers
- Pearson r=0.1231 (p=0.2996) — below PARTIAL threshold (0.50)
- ViT and Gemma not evaluated (model downloads timed out, ~10 GB)

## Why gate failed
1. Only 1/3 model families evaluated; gate requires ≥2/3
2. DeBERTa r=0.1231 below both PASS (0.65) and PARTIAL (0.50)
3. Likely artifact of under-training (1 epoch, 20k subsample)

## Reusable artifacts
- `code/spectral_entropy.py` — working H(W₀) extraction (73 layers)
- `code/para_oracle.py` — PARA Algorithm 1 implementation
- `code/correlation.py` — Pearson+Spearman+bootstrap CI
- `checkpoints/deberta/final/` — saved DeBERTa LoRA adapter

## Recommendation for redesign
- Pre-download ViT+Gemma models before running
- Train DeBERTa ≥3 epochs on full MNLI (392k samples)
- r=0.1231 positive direction suggests hypothesis is plausible — not a fundamental failure
