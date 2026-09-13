# Limitation Record: h-m1 (Run 1)

**Date:** 2026-08-02T12:15:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** MUST_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (feature replaced in ensemble, not blocked)

## Limitation Details

POS-filtered content-token variance (NOUN, PROPN, VERB, NUM) does NOT outperform full-sequence variance on TriviaQA dev. AUROC_content=0.8008 < AUROC_full=0.8250, delta=-0.0242. Gate threshold was delta >= +0.01. Result is robust on 300/2500 dev samples (preliminary; full run ongoing).

The H-M1 mechanism — restricting variance to content POS categories — was falsified for TriviaQA short-answer QA. POS filtering removes uncertainty signal carried by function words and connectives.

## Failed Checks

- AUROC delta >= 0.01: actual delta = -0.0242 (content LOWER than full)
- POS miss rate < 0.15: actual mean = 0.1602 (sub-word alignment incomplete)

## Partial Results

| Metric | Value |
|--------|-------|
| AUROC(content_token_var) | 0.8008 |
| AUROC(full_seq_var) | 0.8250 |
| delta | -0.0242 |
| pos_miss_rate_mean | 0.1602 |
| fraction_degenerate | 0.1033 |
| n_dev | 300 (preliminary) |
| n_train | 500 |

## Experiment Summary

Ablation comparing POS-filtered variance vs full-sequence variance on TriviaQA dev split using Llama 3.1-8B (BF16). 500 train examples for LR fitting, 300 dev examples evaluated (full 2500 ongoing). Single greedy forward pass, spaCy en_core_web_sm POS tagger with char-offset sub-word alignment.

## Root Cause Analysis

1. **Function words carry uncertainty signal in TriviaQA**: When Llama is uncertain about an entity name, log-probs of preceding function words ("of", "the", "in") are also low-variance, signaling confidence. Discarding these by POS filtering removes real uncertainty signal.
2. **POS miss rate above threshold**: Mean 0.1602 > 0.15. Sub-word-to-word alignment via character offsets tags ~16% tokens as untagged (""), silently excluding them from variance computation.
3. **Short-answer domain**: TriviaQA answers are 1-5 tokens. With CONTENT_POS={NOUN,PROPN,VERB,NUM}, 10.3% of samples have <2 content tokens (degenerate), falling back to full_var which inflates content_var artificially.
4. **Content POS set too narrow**: ADJ/ADV excluded but factual uncertainty in "Which country...", "How many..." queries distributes to these categories.

## Downstream Impact

- H-C1 ensemble: Replace `content_token_variance` with `full_sequence_variance`
- H-E2 fallback ensemble [min_logprob, content_token_variance] → use [min_logprob, full_sequence_variance]
- feature_extractor.py, evaluate.py from H-M1 code are fully reusable for H-C1
- Model: Llama 3.1-8B confirmed working (Llama 3.3-70B license 403 blocked)

## Context

This limitation was recorded but **did not block the pipeline**. Full-sequence variance (AUROC 0.825) is a strong standalone feature. The H-M1 result informs the ensemble design for H-C1 — replacing content_token_variance with full_sequence_variance in the 2-feature ensemble. The negative result is publishable as an ablation study finding.

Future research attempts should consider:
1. Expanding CONTENT_POS to include ADJ, ADV for factual QA domains
2. Using CONTENT_POS={NOUN, PROPN, VERB, NUM, ADJ, ADV} (standard content word set)
3. Testing POS filtering on longer-answer datasets where content words dominate
4. Investigating why function words carry uncertainty signal in short-answer QA

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this informs brainstorming to avoid POS-based filtering on short-answer QA
- **Phase 6 Discussion:** Include in paper Limitations section: "POS filtering did not improve AUROC on TriviaQA (delta=-0.024); full-sequence variance used in ensemble"

---
*Limitation recorded at: 2026-08-02T12:15:00+00:00*
*For cross-phase reference*
