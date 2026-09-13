# Revision Log - Round 1

**Date**: 2026-08-05
**Input Paper**: docs/youra_research/paper/06_paper.md
**Review File**: docs/youra_research/paper/review/065_review_r1.md
**Output Paper**: docs/youra_research/paper/06_paper_r1.md
**Authoritative facts source**: h-e1-v2/04_validation.md gate grid (per the review, the ground-truth YAML's "3/6" adj_kl line is itself a typo; Table 1 and the gate grid both show 2/6)

---

## Issues Addressed

### FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| FATAL-ACC-001 | "adj. KL best signal in half of our cells" contradicted by Table 1 (actual 2/6) | ACCEPT | Corrected every occurrence to "two of six cells" with the even 2/2/2 three-way split stated: Intro contribution 3, §2 (Cross-layer shift paragraph), §5.3 first sentence, §7 Conclusion. Claim now carried by the surviving strong facts (top-three sweep in LLaMA-2/TriviaQA: 0.6522/0.6145/0.6062; no detection-time precedent). Anchored on the gate grid, not the ground-truth YAML's "3/6" typo. Abstract and Discussion contained no count claim (verified); no change needed there. |

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-001 | "Winning signal differs in 4 of 6 cells" — actual 6/6 by signal, 4/6 only by layer | ACCEPT | §3.4 and §5.3 now state the correct, stronger fact: the winning signal differs across datasets for every model, and the winning layer for two of the three. |
| MAJOR-ACC-002 | "Single-pass / zero inference cost / free byproducts" contradicted by the required teacher-forced re-forward | ACCEPT | Abstract: "training-free and sampling-free — one greedy generation plus one teacher-forced re-forward, roughly twice the monitored pass and an order of magnitude below multi-sample methods". Intro premise paragraph and contribution 1: "single-pass" replaced with the two-pass description / "sampling-free". §2 Multi-sample paragraph: "free byproducts of a forward pass the deployment already runs" replaced with the honest 2x cost statement. §2 Positioning: "single-pass" → "sampling-free". §3.1: added explicit note that the re-forward is a measured cost, capture-during-generation is an unmeasured engineering option, and all cost statements price the two-pass protocol. Algorithm 1 comment "single pass" → "greedy generation". §6 Broader impact: "zero additional inference cost" → "roughly one extra forward pass per monitored generation — far below the tenfold cost of sampling-based detection". §7: "single greedy pass" → "one greedy generation plus one teacher-forced re-forward". No "zero inference cost" claim remains anywhere. |
| MAJOR-ACC-003 | Two different "prior runs" conflated (archived v1 record vs protocol-identical donor sweep) | ACCEPT | Introduced two named referents: "the motivating record" (archived, protocol-different, source of 0.5186 / 0.66 / 0.52) defined at first use in Intro ¶2, and "the immediately preceding sweep" (protocol-identical, donor cache source). §3.1 now inherits protocol from the preceding sweep and explicitly distinguishes it from the motivating record with a pointer to §5.4. §3.4, §3.5 (intro + clause c), §4.4, §5.4 all updated to the correct referent. §4.5 already used "motivating record"; now consistent throughout. |
| MAJOR-CRED-001 | Zero-GPU test-split follow-up advertised three times but never run, with only procedural justification | ACCEPT | Adopted the review's option (a): Discussion limitation 1 now gives the scientific rationale — the split stays sealed because no analysis or writing decision has read it, preserving the deferred evaluation as an uncontaminated pre-registered confirmation — and explicitly frames the paper as the stage-one report of that pre-registered design. Intro ¶6 reinforces the same rationale in one clause. Conclusion follow-up rephrased as "the pre-registered confirmation this stage-one report was built to set up". |
| MAJOR-CRED-002 | Uncomputed statistical claims ("margins large relative to plausible sampling noise / CI widths") | ACCEPT (soften option) | Both sentences reduced to pure point-estimate language. §5.1: no distributional claim; only the point-estimate comparison that the thinnest gate margin is an order of magnitude larger than the thinnest depth margin. Discussion limitation 2: "as point estimates — we make no distributional claim for these margins either". Did not fabricate CIs (revision agent must not generate new results). The conservative self-deprecating uses of "within plausible noise" (§5.2, limitation 2) were not flagged and are retained. |
| MAJOR-ENG-001 | Pipeline-internal jargon leaks (REAL_MODEL, 37/37, session interruptions, undefined "rescue claim", "this program") | ACCEPT | §4.4: verification sentence rewritten in standard reproducibility language ("automated test suite (37 tests, all passing) ... every reported statistic derives from live forward passes of the actual checkpoints"); session-interruption anecdote deleted (resumable-cache sentence retained). "Rescue claim" removed from Discussion limitation 1 and Conclusion; the term now appears only in limitation 3, where it is defined in place by its own scare-quoted phrase. "This program" replaced everywhere with reader-facing phrasing ("this research line" / "this stage-one report"). |

### MINOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| (all Part 4 items) | 7 minor notes (bib venue/author, rescue ordering, abstract hedge, word_count drift, figure/blueprint notes) | NOT FIXED (per protocol) | Copied to review/065_human_review_notes.md for human review. Note: the limitation 1/3 "rescue" ordering item is resolved as a side effect of MAJOR-ENG-001; the word_count metadata was updated as required frontmatter maintenance (6528 → 6822), not as a fix of the drift convention. |

---

## Issues NOT Addressed (with justification)

| ID | Title | Reason for Rejection |
|----|-------|---------------------|
| — | none | All 1 FATAL and 6 MAJOR issues accepted and fixed. |

---

## Sections Modified

- Abstract: cost claim made precise (MAJOR-ACC-002)
- Section 1 Introduction: motivating-record referent defined (MAJOR-ACC-003, MAJOR-ENG-001); contribution 1 and premise paragraph cost language (MAJOR-ACC-002); contribution 3 count corrected to 2/6 (FATAL-ACC-001); sealed-split pre-registration clause (MAJOR-CRED-001)
- Section 2 Related Work: adj_kl count corrected (FATAL-ACC-001); "free byproducts" and "single-pass" cost language corrected (MAJOR-ACC-002)
- Section 3 Methodology: §3.1 prior-run disambiguation + measured-cost note (MAJOR-ACC-003, MAJOR-ACC-002); §3.4 signal/layer variation fact corrected (MAJOR-ACC-001) and motivating-record referent (MAJOR-ACC-003); §3.5 referents (MAJOR-ACC-003); Algorithm 1 comment (MAJOR-ACC-002)
- Section 4 Experimental Setup: §4.4 jargon removed, anecdote deleted, referent fixed (MAJOR-ENG-001, MAJOR-ACC-003)
- Section 5 Results: §5.1 distributional-claim removal (MAJOR-CRED-002); §5.3 count corrected + variation fact (FATAL-ACC-001, MAJOR-ACC-001); §5.4 referents (MAJOR-ACC-003)
- Section 6 Discussion: limitation 1 pre-registration rationale + rescue-term removal (MAJOR-CRED-001, MAJOR-ENG-001); limitation 2 distributional-claim removal (MAJOR-CRED-002); broader impact cost claim (MAJOR-ACC-002)
- Section 7 Conclusion: count corrected (FATAL-ACC-001); cost language (MAJOR-ACC-002); rescue/program phrasing (MAJOR-ENG-001, MAJOR-CRED-001)

---

## Word Count Changes

(whole-word counts per top-level section, `wc`-style; References counted with Conclusion)

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 163 | 180 | +17 |
| 1. Introduction | 994 | 1,063 | +69 |
| 2. Related Work | 791 | 803 | +12 |
| 3. Methodology | 1,358 | 1,450 | +92 |
| 4. Experimental Setup | 890 | 884 | -6 |
| 5. Results | 1,363 | 1,402 | +39 |
| 6. Discussion | 571 | 621 | +50 |
| 7. Conclusion (+refs) | 930 | 951 | +21 |
| **Total** | **7,060** | **7,354** | **+294** |

Frontmatter `word_count` updated 6528 → 6822 (original counting convention plus the +294 delta).

---

## Coherence Check (post-fix)

- adj_kl count is 2/6 at every mention; 2/2/2 split stated identically in Intro, §5.3; no "half"/"three of six" remains (grep-verified).
- No "single-pass", "zero inference cost", "zero additional inference cost", or "free byproducts" claim remains for our method; the one remaining "single-pass" describes Kossen et al.'s hidden states (their finding, accurate).
- "Motivating record" (7 occurrences) vs "preceding sweep" used consistently; §3.1's inheritance claim no longer contradicts §5.4's six protocol differences.
- "Rescue" appears only in limitation 3, self-defined; "this program" eliminated.
- "Four of six at L31" in §5.1 retained deliberately — it counts winning *layers*, which is correct per Table 1.
- Cross-references (§3.5, §5.4, §5.2, Section 1) all resolve; figures/tables untouched.

---

# Revision Log - Round 2

**Date**: 2026-08-05
**Input Paper**: docs/youra_research/paper/06_paper_r1.md
**Review File**: docs/youra_research/paper/review/065_review_r2.md
**Output Paper**: docs/youra_research/paper/06_paper_r2.md
**Authoritative facts source**: raw Phase 4 artifacts as verified by the R2 review (h-e1-v2/experiment_results.json retained_layers; 306-row results.csv = (20+20+15+16+15+16) x 3 signals; experiment.log 09:00:23-10:14:59). 065_ground_truth.yaml was already corrected for both R2 numerical findings before this revision (screen counts per cell; ~1.25 GPU-hours logged vs ~2.5h v1 budget); no further ground-truth edits were needed.

---

## Issues Addressed

### FATAL Issues

None received this round.

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-001 (R2) | Degeneracy-screen counts "20/15/15" contradicted by raw artifacts; screen is per cell (20/20/15/16/15/16) | ACCEPT | Section 3.3 rewritten to state the per-cell truth: screen applied "per model x dataset cell on that cell's selection split"; lens-viability restated per cell; retained counts now "15-20 layers per cell: 20 on LLaMA-2-7B (both datasets), 15 and 16 on Mistral-7B-v0.1, and 15 and 16 on LLaMA-3-8B-Instruct (TriviaQA and TruthfulQA respectively)". Figure 2 caption replaced with accurate per-cell numbers (LLaMA-2 20/20, Mistral 15/16, LLaMA-3 15/16) and the per-cell granularity statement — the figure image itself cannot be regenerated, so the caption carries the correction. Section 4.5 screen-health wording aligned: ">= 5 retained layers per model" -> "per cell". Algorithm 1 line 7 checked and left unchanged: it runs on a single (model, dataset) input, so "|L*| >= 5" is already a per-cell check. Grep confirms no "20/15/15" or "15 each" remains anywhere. |
| MAJOR-ACC-002 (R2) | "~2.5 GPU-hours" in Section 4.4 is the v1 budget figure, roughly double the ~1.25 GPU-hours logged for the v2 sweep | ACCEPT | Section 4.4 now reports the measured figure: "the remaining five cells were generated fresh, at ~1.25 GPU-hours of logged compute" (single-H100 context already present in the same paragraph; zero-GPU donor cell sentence retained). Section 5.4's "budgeted as a ~2.5-hour GPU campaign" kept verbatim — it correctly denotes the v1 budget, and "budgeted" already marks it as such. Grep confirms these are the only two GPU-time statements; Section 3.5 and the rest of the Methodology contain no "2.5" figure. |
| MAJOR-ACC-003 (R2) | Abstract's "an order of magnitude below multi-sample methods" fails strict arithmetic on the paper's own numbers (2x vs ~10x total = 5x) | ACCEPT | One-clause fix on the added-cost basis Section 6 already uses: "roughly twice the monitored pass, and an order of magnitude less added inference than multi-sample methods" (1 added re-forward vs ~10 added passes). Single cost basis per clause; consistent with Section 2 ("roughly twice the monitored pass, against the tenfold cost above" — raw quantities, no ratio claim) and Section 6 ("roughly one extra forward pass ... far below the tenfold cost"). The verified-correct "order of magnitude" uses in Section 2 (multi-sample vs monitored pass) and Section 5.1 (gate margin vs depth margin, 16.9x) are untouched. |

### MINOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| (all Part 4 items) | 5 minor notes (unhedged priority claims in Abstract/Conclusion, thinnest-margin signal in Abstract, "five clauses" wording, word_count drift, Chi2025Know venue) | NOT FIXED (per protocol) | Appended to review/065_human_review_notes.md as "## Round 2 Issues", Round 1 content intact. |

---

## Issues NOT Addressed (with justification)

| ID | Title | Reason for Rejection |
|----|-------|---------------------|
| — | none | All 3 MAJOR issues accepted and fixed. 0 FATAL received. |

---

## Sections Modified

- Abstract: cost-comparison clause moved to a single (added-cost) basis (MAJOR-ACC-003)
- Section 3.3 Degeneracy screen: per-cell granularity and correct retained counts (MAJOR-ACC-001)
- Figure 2 caption: accurate per-cell counts, per-cell granularity (MAJOR-ACC-001)
- Section 4.4 Implementation details: measured ~1.25 GPU-hours replaces the v1 budget figure (MAJOR-ACC-002)
- Section 4.5 Metrics and gate constants: screen health "per model" -> "per cell" (MAJOR-ACC-001 coherence)
- Frontmatter: word_count 6822 -> 6871 (maintenance, same convention as R1)

All R1 fixes preserved: no edits touched the 2/6 adj_kl claims, the 6/6 signal-variation fact, the motivating-record/preceding-sweep referents, the pre-registration rationale, the point-estimate language, or the reproducibility wording (grep-verified against the R1 regression list).

---

## Word Count Changes

(whole-file `wc -w`; edits confined to Abstract, Section 3.3 + Figure 2 caption, Section 4.4, Section 4.5)

| File | Before | After | Delta |
|------|--------|-------|-------|
| Paper body | 7,421 | 7,470 | +49 |

Frontmatter `word_count` updated 6822 -> 6871 (original counting convention plus the +49 delta).

---

## Coherence Check (post-fix)

- Screen granularity now consistent everywhere it appears: Section 3.3 (per cell), Figure 2 caption (per cell), Section 4.5 (per cell), Algorithm 1 line 7 (per (model, dataset) input — already per cell). No "20/15/15", "15 each", or per-model screen claim remains (grep-verified).
- "~2.5" survives only in Section 5.4, explicitly as the v1 budget ("budgeted as a ~2.5-hour GPU campaign"); Section 4.4 reports the logged ~1.25 GPU-hours. The two are now visibly different quantities, resolving the budget/actual conflation.
- All three "order of magnitude" uses now verify: Abstract (added inference, 1 vs ~10 added passes), Section 2 (multi-sample ~10x vs monitored pass), Section 5.1 (0.0592/0.0035 = 16.9x). Total-cost statements remain 2x vs 10x raw quantities with no ratio claim.
- Health-gate claim unaffected: minimum retained is 15 >= 5 under the corrected per-cell counts.
- Cross-references, Table 1, and all other figures untouched.

---

## Final Summary

**Total Revisions Made**: 10 (1 FATAL + 6 MAJOR in R1; 3 MAJOR in R2 — all accepted, 0 rejected)
**Sections Modified**: Abstract, Introduction, Related Work, Methodology (3.1/3.3/3.4/3.5, Algorithm 1 context), Experiments (4.4/4.5), Results (5.1/5.3/5.4), Discussion, Conclusion
**Word Count Change**: 6,528 → 6,871 (+343)

**Review Process**:
- Started: 2026-08-05T11:48:36+00:00
- Completed: 2026-08-05T12:25:00+00:00
- Rounds: 2 (R1 Accuracy & Engagement; R2 Numerical Verification & Credibility)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert
- R2 verification: 19 searches against raw Phase 4 artifacts; all surviving numbers reconcile exactly

**Files Generated**:
- 06_paper_final.md (final paper, from 06_paper_r2.md + review metadata)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (12 MINOR issues for human review)
- 065_changelog.md (this file)

**Side corrections**: 065_ground_truth.yaml fixed twice (adj_kl 3/6→2/6 typo; per-cell screen counts 20/20/15/16/15/16; logged ~1.25 GPU-hours vs ~2.5h v1 budget).

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
