# H-E1 FAILURE: LLAE Hallucination Detection — 2026-03-15

## Result
MUST_WORK gate FAILED. LLAE AUROC near-chance on all conditions.

## AUROC Results
- LLaMA-3-8B / TriviaQA: 0.5653 (threshold: 0.60) — FAIL
- LLaMA-3-8B / NQ-Open: 0.4968 — FAIL
- Mistral-7B-v0.1 / TriviaQA: 0.4230 — FAIL
- Mistral-7B-v0.1 / NQ-Open: 0.5188 — FAIL
- All other signals (LE, SLP, SE) also below threshold

## Root Cause Analysis
1. **No explicit retrieved context**: LLAE measures context attention entropy, but for bare factual QA (no RAG), the "context" is just the question (8–15 tokens). Insufficient signal range.
2. **Label quality**: Exact-match substring correctness creates noisy near-uniform label distributions (most greedy answers partially match).
3. **GQA attention noise**: LLaMA-3-8B GQA structure (8 KV heads, 32 Q heads) produces degenerate fp16 attention in some heads → NaN in entropy computation (handled via nanmean but reduces signal).
4. **SE not computed**: SE was 0.50 everywhere because sampled_answers were not populated (greedy-only inference).

## Key Implementation Notes (for future hypotheses)
- Must use `attn_implementation="eager"` to get `output_attentions=True` to work with LLaMA-3-8B/Mistral-7B
- fp16 attention can produce NaN in entropy: compute in float32, use `.clamp(min=epsilon)` not `+ epsilon`
- Per-token attention format: `attn[token_step][layer_idx]` shape `(batch, n_heads, full_seq, full_seq)` — use last row `[-1, :]` for current token's attention
- NQ-Open dataset: use `nq_open` identifier (not `natural_questions`)
- CUDA_VISIBLE_DEVICES must be set at shell level before conda run

## Recommendations for Next Hypothesis
- Test LLAE with RAG setting (explicit retrieved context passages)
- Use HaluEval or SelfCheckGPT labels instead of exact-match proxy
- Consider sampling-based SE (temperature=0.7, 10 samples) for proper uncertainty labels
- Try layer-specific LLAE (e.g., last layer only vs. final 1/3) to find most discriminative layer

## Files
- Code: docs/youra_research/20260315_question/h-e1/code/ (all 8 modules + 35 tests)
- Results: docs/youra_research/20260315_question/h-e1/code/outputs/full_run/results/
- Validation: docs/youra_research/20260315_question/h-e1/04_validation.md
- Checkpoint: docs/youra_research/20260315_question/h-e1/04_checkpoint.yaml (hypothesis_failed=true)
