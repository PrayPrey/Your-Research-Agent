# Reflection Report: h-c1

**Date:** 2026-08-25
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** SELF_MODIFY
**Route To:** phase2c (retry)

---

## Summary

h-c1 failed due to environment dependency failure (httpx version incompatibility), not a hypothesis flaw. Only llama2-7b-base completed inference; chat/13B/Mistral models could not load.

**Failure cause:** `httpx Client.__init__() got unexpected keyword argument 'event_hooks'` — version mismatch between httpx and huggingface_hub/transformers.

## What Succeeded

- llama2-7b-base inference: all 4 splits completed
  - mnli_clean ECE=0.058, anli_r1 ECE=0.074, anli_r2 ECE=0.070, anli_r3 ECE=0.077
- ANLI adversarial ECE > mnli_clean (delta ~+0.014–0.019): directionally consistent with h-e1
- Data loading pipeline functional

## What Failed

- Llama-2-7b-chat-hf: httpx incompatibility on model load
- Llama-2-13b-chat-hf: same failure
- Mistral-7B-Instruct-v0.1: same failure
- Primary gate (paired t-test base vs chat, p<0.05): unevaluable
- Secondary gate (Spearman r>0.5 across model variants): unevaluable

## Root Cause

httpx version in environment incompatible with huggingface_hub's use of `event_hooks` parameter. Base model loaded before the HTTP call path that triggers the incompatibility; chat/instruction models hit it during authentication or model card fetch.

## Modification Plan (h-c1-v2)

**Fix:** Pin `httpx>=0.23,<0.24` or upgrade `huggingface_hub>=0.20` (which dropped `event_hooks` usage). Alternatively, pre-download all model weights offline and bypass HF Hub HTTP calls entirely.

**Specific changes:**
1. Add `pip install "httpx>=0.23,<0.24"` before model loading, or use `huggingface-cli download` offline
2. Test all 4 model loads before running inference
3. Re-run full inference pipeline with all 4 models
4. Compute paired t-test (base vs chat) and Spearman r across variants

## Lessons Learned

- Environment dependency checks must precede batch inference runs
- Chat/instruction model loading follows different HF Hub code paths than base models
- Future experiments: verify all model loads succeed in a dry-run before committing to full inference

## Disposition

SELF_MODIFY — retry with environment fix. Hypothesis validity unaffected by environment failure. Partial data (base model) directionally consistent with h-e1.
