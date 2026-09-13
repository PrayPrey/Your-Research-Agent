# Hypothesis Completion Snapshot: h-m3

**Date:** 2026-03-18T10:59:00+00:00
**Hypothesis:** h-m3
**Type:** MECHANISM (Step 3 of 4)
**Statement:** P(True) logprob elicitation produces non-degenerate confidence signals (std(c) > 0.05 for all 3 models)
**Final Status:** COMPLETED
**Gate Result:** PASS (MUST_WORK)

## Results

- Gate: PASS (3/3 models)
- llama3_8b: std(c)=0.0669, mean(c)=0.4989, n=1975 pairs
- codellama_7b: std(c)=0.0618, mean(c)=0.3682, n=1890 pairs
- deepseek_6.7b: std(c)=0.0781, mean(c)=0.6480, n=1865 pairs
- Total pairs: 5,730
- Duration: ~4 minutes (H100 GPU)

## Key Output Files

- `h-m3/results/ptrue_confidence_scores.json` — 697KB, per-model confidence scores for h-m4 ECE
- `h-m3/results/ptrue_hm3_verified.json` — FR-10.1 gate result
- `h-m3/figures/` — 5 figures (gate check, histograms, correlation, tier comparison, CDF)

## Technical Notes

- tier_assignments.csv from h-m2 is wide format (llama3_tier, codellama_tier, deepseek_tier columns)
- Solutions are in h-e1/results/ (not h-m1/results/)
- Leading space in " True"/" False" token encoding is critical
- output_logits=True, max_new_tokens=1, do_sample=False confirmed working

## Next

- h-m4 UNBLOCKED: ECE computation per difficulty tier using h-m3 confidence scores

---
*Per-hypothesis snapshot for Phase 2A reference*
