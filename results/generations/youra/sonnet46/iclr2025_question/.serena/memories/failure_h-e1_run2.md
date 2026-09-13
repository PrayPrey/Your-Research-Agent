# Failure Record: h-e1 Run 2 (SelfCheckGPT-NLI Cross-Task Transfer)

## Metadata
- hypothesis_id: h-e1
- phase: Phase 4
- gate_type: MUST_WORK
- gate_result: FAIL
- timestamp: 2026-03-16T13:30:00+00:00
- routed_to: Phase 0
- run: 2 (previous failures also recorded in failure_h-e1_run1, failure_h-e1-v2)

## Experiment Summary
- Dataset: pminervini/HaluEval (10,000 dialogue + 10,000 QA) — FULL SCALE
- Generator: meta-llama/Llama-3.1-8B (BASE, NOT instruction-tuned — substituted due to gated access failure)
- NLI scorer: cross-encoder/nli-deberta-v3-large (SelfCheckNLI)
- N samples: 5, temperature=0.7, seed=42
- Duration: ~18.5 hours on H100 NVL GPU 4 (95,320 MiB free)

## Results
- Dialogue AUROC: 0.4832 [CI: 0.4714, 0.4943] — BELOW CHANCE
- QA AUROC: 0.5326 [CI: 0.5228, 0.5439] — marginally above chance, but far below gate
- Mechanism activated: False (dialogue AUROC < 0.52)
- Gate: FAIL (0/4 criteria met; gate: AUROC>=0.65 and CI_lower>=0.60 on both splits)

## Critical Root Cause: BASE MODEL USED
- meta-llama/Meta-Llama-3-8B-Instruct requires HuggingFace gated access
- HF_TOKEN present but not authorized for gated access
- Substituted with Llama-3.1-8B BASE model (locally cached)
- **This substitution fundamentally breaks SelfCheckGPT-NLI:**
  - Base models generate repetitive continuations, not factual responses
  - No factual grounding → no systematic semantic divergence between hallucinated/factual examples
  - Dialogue AUROC BELOW chance = scores inversely correlated with labels

## Additional Root Causes
1. Smoke test warning was ignored (AUROC=0.535 < 0.55 threshold)
2. QA shows marginal signal (0.5326) — NLI mechanism partially works for QA
3. Score std exists (0.175/0.213) but no discriminative power

## Lessons for Phase 0 Redesign
1. **HARD REQUIREMENT**: Instruction-tuned model access must be verified BEFORE Phase 3
2. **Alternative models** (less restricted): 
   - mistralai/Mistral-7B-Instruct-v0.1 (open)
   - google/flan-t5-xxl (open)
   - meta-llama/Llama-3.1-8B-Instruct (same local cache, may be available)
3. **Alternative approach**: Use NLI directly on existing response pairs (no generation needed)
4. **Reformulate**: Test semantic entropy on existing HaluEval responses rather than generating new samples

## Cascade
- h-m1, h-m2, h-m3, h-m4: CASCADE_FAILED
