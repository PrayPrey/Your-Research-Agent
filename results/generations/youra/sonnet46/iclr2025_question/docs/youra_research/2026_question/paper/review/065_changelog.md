# Revision Changelog — R1

**Paper:** Generation-Free Hallucination Detection via NLI Contradiction Scoring
**Source:** 06_paper.md
**Output:** 06_paper_r1.md
**Revision Date:** 2026-03-16
**Issues addressed:** 6 MAJOR (A1, A2, C1, C2, C3, E1)

---

## Summary

All 6 MAJOR issues identified in the adversarial review (065_review_r1.md) have been addressed. No numerical values, research findings, or core arguments were altered. Human review notes (HR-1 through HR-8) were collected but not applied to the paper (see 065_human_review_notes.md).

---

## Changes Applied

### Fix A1 — Abstract: Imprecise Wilcoxon p-value claim
**Issue ID:** MAJOR A1
**Location:** Abstract (paragraph 5, mechanistic analysis sentence)
**Original text:**
> "Wilcoxon rank-sum tests (p ≈ 0 on all tasks)"

**Revised text:**
> "Wilcoxon rank-sum tests (p ≤ 2.07e-13 on all tasks; p ≈ 0 for dialogue)"

**Rationale:** "p ≈ 0 on all tasks" implied uniform near-zero significance, misrepresenting QA (p = 1.52e-271) and summarization (p = 2.07e-13). The revised phrasing gives the bound value and preserves the dialogue-specific precision.

---

### Fix A2 — Section 5.1: Post-hoc spin on QA near-miss
**Issue ID:** MAJOR A2
**Location:** Section 5.1, first paragraph after Table 1

**Original text:**
> "QA AUROC = 0.644 falls just short of the original 0.65 target by 0.006 (within conservative threshold uncertainty)"

**Revised text:**
> "QA AUROC = 0.644 falls short of the original 0.65 pre-specified threshold by 0.006 — this near-miss is acknowledged as Limitation L2 (Section 6.3)"

**Rationale:** "Within conservative threshold uncertainty" was undefined and constituted post-hoc rationalization of a threshold miss. The revised text acknowledges the miss directly and cross-references the limitation. The Cohen's d evidence sentence following it was preserved intact.

---

### Fix C1 — Section 4.2: SelfCheckGPT baseline disclosure
**Issue ID:** MAJOR C1
**Location:** Section 4.2 (Baseline), after existing disclosure sentence

**Added text (new sentence appended to Section 4.2):**
> "Note: SelfCheckGPT was evaluated on base (non-instruction-tuned) Meta-Llama-3-8B, which produces near-uniform stochastic samples — likely a lower bound on SelfCheckGPT performance under intended deployment with instruction-tuned models. The generation-free advantage reported here should be interpreted with this context in mind."

**Rationale:** The +0.229 headline advantage was presented without disclosing that the baseline used a non-instruction-tuned model producing near-uniform outputs. Without this disclosure, a reviewer familiar with SelfCheckGPT's expected performance would likely challenge the comparison. The added sentence contextualizes the result without invalidating it.

---

### Fix C2 — Sections 1.1, 2.2, 2.4: Unqualified "first" novelty claims
**Issue ID:** MAJOR C2

**Change 1 — Section 1.1:**
- Original: "no prior work has: (1) established AUROC baselines..."
- Revised: "to our knowledge, no prior work has: (1) established AUROC baselines..."

**Change 2 — Section 2.2:**
- Original: "providing the first AUROC measurement for this configuration"
- Revised: "providing the first AUROC measurement for this configuration to our knowledge"

**Change 3 — Section 2.4:**
- Original: "Our work provides the first quantitative characterization of this boundary via AUROC and mechanistic statistics"
- Revised: "Our work provides the first explicit, multi-task AUROC-based quantitative characterization of this boundary"

**Rationale:** Claims 1 and 2 were defensible but vulnerable to reviewer challenge without standard hedging. Claim 3 was overstated since Maynez et al. (2020) and SummaC/TRUE implicitly quantified this boundary; the revised framing accurately captures the paper's incremental contribution (explicit + multi-task + AUROC-based) without "first quantitative" overreach.

---

### Fix C3 — Section 3: Unexecuted ablations not disclosed in methodology
**Issue ID:** MAJOR C3
**Location:** Added as new Section 3.6 "Design Scope and Ablation Status" (former Section 3.6 Dataset renumbered to 3.7; former Section 3.7 Evaluation renumbered to 3.8)

**Added text (new Section 3.6):**
> "Note on Ablations: The three design choices above (net-contradiction framing, sentence-level max aggregation, last-3-turn context window) represent the configuration validated in this study. Comparative ablation experiments (h-m2 through h-m4) evaluating alternative formulations were not executed and constitute a recognized limitation (Section 6.3, L3). The current results confirm the configuration *works* but cannot attribute performance to individual design choices vs. alternatives."

**Rationale:** The methodology presented three specific design choices with rationales but no indication that their comparative advantage had not been empirically validated. Moving the ablation disclosure from L3 in Section 6.3 (only) to an explicit note in Section 3 ensures readers of the main methodology do not assume these choices have been comparatively validated.

**Section renumbering:** Former 3.6 Dataset → 3.7; Former 3.7 Evaluation → 3.8.

---

### Fix E1 — Front matter: Page estimate note updated
**Issue ID:** MAJOR E1
**Location:** YAML front matter, `page_estimate` field

**Original:**
> "~15 pages (flagged for review: exceeds 8-page ICML limit; trim in Phase 6.5)"

**Revised:**
> "~15 pages (requires substantial trimming to meet 8-page ICML limit before submission; see human review notes)"

**Rationale:** The original note was an internal pipeline flag. The revised note makes the submission-readiness status explicit and directs to the human review notes for trim targets. The structural trim itself (Section 7 partial duplication of 6.1, Figure consolidation) is logged in HR-8 of 065_human_review_notes.md for human review.

---

### Additional minor update — Revision footer
Added to paper end matter:
> "*Revised R1: 2026-03-16 — fixes A1, A2, C1, C2, C3, E1*"

Added `revision` field to YAML front matter:
> `revision: "R1 — 2026-03-16 (fixes: A1, A2, C1, C2, C3, E1)"`

---

## Unchanged Elements

- All AUROC, Cohen's d, KL divergence, Wilcoxon p-value, DeLong p-value, and delta figures
- Core claims about commission/omission boundary
- SelfCheckGPT performance figures (0.48 dialogue, 0.53 QA)
- Limitations L1–L5 in Section 6.3
- All references
- Section 7 Conclusion (no changes)
- Figures and figure captions
- Tables 1 and 2

---

## Issues NOT addressed (deferred to human review)

HR-1 through HR-8 — see 065_human_review_notes.md

---

# Revision Changelog — R2

**Paper:** Generation-Free Hallucination Detection via NLI Contradiction Scoring
**Source:** 06_paper_r1.md
**Output:** 06_paper_r2.md
**Revision Date:** 2026-03-16
**Issues addressed:** 1 MAJOR (NM-1), 1 PARTIAL (C2-partial)

---

## Summary

One new MAJOR issue (NM-1) identified in the R2 adversarial review has been fixed. Two remaining C2 hedge instances identified in R2 review (Sections 2.4 and 6.2) have also been applied. No numerical values, research findings, or core arguments were altered. Human review notes (HR-R2-1 through HR-R2-3) were collected but not applied to the paper (see 065_human_review_notes.md).

---

## Changes Applied

### Fix NM-1 — Section 4.3: Incorrect batch size
**Issue ID:** MAJOR NM-1
**Location:** Section 4.3 Implementation Details, bullet starting with "Batch size"

**Original text:**
> "Batch size: 64; Max sequence length: 512 tokens"

**Revised text:**
> "Batch size: 32 (OOM fallback: 16); Max sequence length: 512 tokens"

**Rationale:** The R1 paper stated batch_size=64, but experiment.log, config.py, and all design documents confirm the actual experiment ran with batch_size=32 (with OOM fallback to 16). This is a factual accuracy issue — the paper must reflect the actual experimental configuration.

---

### Fix C2-partial (1 of 2) — Section 2.4: Unqualified "first" novelty claim
**Issue ID:** MAJOR C2 (partial — two instances remaining from R1)
**Location:** Section 2.4, final sentence

**Original text:**
> "Our work provides the first explicit, multi-task AUROC-based quantitative characterization of this boundary."

**Revised text:**
> "Our work provides, to our knowledge, the first explicit, multi-task AUROC-based quantitative characterization of this boundary."

**Rationale:** The R1 fix updated the wording of Section 2.4 but did not include the epistemic hedge "to our knowledge." The R2 review identified this as a remaining unqualified "first" claim. Standard hedge applied.

---

### Fix C2-partial (2 of 2) — Section 6.2: Unqualified "first" novelty claim
**Issue ID:** MAJOR C2 (partial — two instances remaining from R1)
**Location:** Section 6.2, sentence beginning "We provide the first quantitative characterization"

**Original text:**
> "We provide the first quantitative characterization: AUROC 0.709/0.644 (commission) vs. 0.530 (omission)..."

**Revised text:**
> "We provide, to our knowledge, the first quantitative characterization: AUROC 0.709/0.644 (commission) vs. 0.530 (omission)..."

**Rationale:** Same as above — unqualified "first" claim without standard epistemic hedge.

---

### Front matter update — Revision field
**Location:** YAML front matter, `revision` field

**Original:**
> `revision: "R1 — 2026-03-16 (fixes: A1, A2, C1, C2, C3, E1)"`

**Revised:**
> `revision: "R2 — 2026-03-16 (fixes: NM-1, C2-partial)"`

---

### Footer update — Revision end matter
Added to paper end matter:
> `*Revised R2: 2026-03-16 — fixes NM-1, C2-partial*`

---

## Unchanged Elements

- All AUROC, Cohen's d, KL divergence, Wilcoxon p-value, DeLong p-value, and delta figures
- Core claims about commission/omission boundary
- SelfCheckGPT performance figures (0.48 dialogue, 0.53 QA)
- Limitations L1–L5 in Section 6.3
- All references
- Figures and figure captions
- Tables 1 and 2
- All R1 fixes preserved intact

---

## Issues NOT addressed (deferred to human review)

HR-R2-1 through HR-R2-3 — see 065_human_review_notes.md

---

*Revision Agent R2 | 2026-03-16*

---

## Final Summary (v2.0)

**Total Revisions Made:** 9 (6 in R1, 3 in R2)
**Sections Modified:** Abstract, Section 1.1, Section 2.2, Section 2.4, Section 3 (new 3.6), Section 4.2, Section 4.3, Section 5.1, Section 6.2, front matter
**Word Count Change:** ~5867 words original → ~5950 words final (net +83 words from disclosures)

**Review Process:**
- Started: 2026-03-16
- Completed: 2026-03-16
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert (R1); accuracy_checker, skeptical_expert (R2 via Serena MCP)

**Files Generated:**
- 06_paper_final.md (final paper, copy of 06_paper_r2.md with review metadata)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review — 11 items)
- 065_changelog.md (this file)
- 065_review_r1.md (Round 1 adversary report)
- 065_review_r2.md (Round 2 adversary report with Serena MCP verification log)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
