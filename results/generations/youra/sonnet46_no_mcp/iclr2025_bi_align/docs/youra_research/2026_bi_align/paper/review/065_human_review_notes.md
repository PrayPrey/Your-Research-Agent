# Human Review Notes — Phase 6.5 Adversarial Review
# Minor issues collected for human review (NOT auto-fixed by AI)
# Generated: 2026-05-03T14:20:00Z

> **Purpose:** Minor issues identified during adversarial review for human consideration.
> **v2.0 Policy:** These issues are NOT auto-fixed. Human reviewer decides whether to apply.

**Rounds completed:** R1 (R2 pending)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 1 |
| Formatting | 1 |
| **Total** | **4** |

---

## Round 1 Issues

### Style

1. **MINOR-003** — Abstract, sentence 1
   - **Issue:** Abstract opens with generic "Reinforcement Learning from Human Feedback assumes that human annotators provide a stable preference signal..." — this is a textbook setup sentence rather than the counterintuitive reversal the narrative blueprint intended.
   - **Narrative blueprint intent:** Lead with the sign flip itself: "Early-round annotators penalized verbose responses; later-round annotators rewarded them."
   - **Suggested revision:** Consider opening with: "When we analyze the Anthropic HH-RLHF dataset — 160,800 preference comparisons used to train some of the most widely deployed conversational AI systems — we find a striking pattern: annotators who penalized verbose responses in early rounds later rewarded them (Δβ_L = +0.080)."
   - **Note:** The Introduction paragraph 1 already opens with the reversal and numbers; the abstract trailing slightly behind is a minor issue. Current abstract is adequate.

2. **MINOR-005** — §6.3 Broader Impact, sentence 1
   - **Issue:** "The AAI framework provides a practical, low-cost quality gate" — "low-cost" is slightly vague. Cost relative to what?
   - **Suggested revision:** "The AAI framework provides a practical quality gate requiring only preference labels and response text — no additional annotation overhead."
   - **Note:** The rest of the sentence already says this, so the "low-cost" qualifier is redundant.

### Clarity

1. **MINOR-001** — §5.2, first sentence of results paragraph
   - **Issue:** "The between-group regression on WebGPT yields..." — reader at this point may have forgotten the §3.6 detail that the "between-group tercile design" substitutes for the planned within-annotator panel regression due to absent worker IDs.
   - **Suggested addition:** Add brief parenthetical: "The between-group regression on WebGPT (tercile proxy; worker IDs absent from public JSONL release) yields..."
   - **Status:** PARTIALLY addressed in R1 revision — the WebGPT sentence now reads "between-group regression on WebGPT (between-group tercile design; worker IDs absent from public release)."

### Formatting

1. **MINOR-002** — §5.1, §5.2 (original paper — resolved in R1)
   - **Issue:** Original paper body text contained informal figure path references like "(figures/fig1_coefficient_comparison.png)" embedded in prose.
   - **Status:** RESOLVED in R1 revision — figure paths moved to caption blocks. No further action needed.

---

## Round 2 Issues

*Pending R2 adversarial review.*

---

## Recommended Priority for Human Review

1. **Consider (Style MINOR-003):** Abstract opening sentence — minor opportunity to strengthen hook. Current version is acceptable; revision is optional.
2. **Consider (Style MINOR-005):** §6.3 "low-cost" qualifier — trivial cleanup.
3. **No action needed (Clarity MINOR-001):** Already addressed in R1.
4. **No action needed (Formatting MINOR-002):** Already resolved in R1.

---

*Note: These issues do not block paper acceptance. All FATAL and MAJOR issues have been addressed in the main revision pipeline.*
