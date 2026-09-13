# Adversarial Review Summary

**Paper**: Depth-Resolved Logit-Lens Uncertainty Signals for Hallucination Detection: Training-Free Evidence and a Protocol-Internal Validity Anchor
**Hypothesis**: H-LayerLensUQ-v2
**Review Completed**: 2026-08-05T12:25:00+00:00
**Rounds Completed**: 2 (R1: Accuracy & Engagement, R2: Verification & Credibility)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED
**Recommendation**: CONDITIONAL_ACCEPT

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert in R1; accuracy_checker + skeptical_expert in R2).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 1 | 1 | 0 |
| MAJOR | 9 | 9 | 0 |

**MINOR Issues**: 12 collected in `065_human_review_notes.md` (NOT auto-fixed, per protocol).

---

## Persuasiveness Assessment (Bored Reviewer, R1)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Concrete numbers, clear gap, honest scope flag |
| Problem clear in 1 minute? | PASS | Architecture-fragility of output-layer signals stated in first paragraphs |
| Novelty clear in 2 minutes? | PASS | Four contributions enumerated end of Introduction |
| Figure 1 self-explanatory? | PASS | Entropy heatmap conveys depth-separation intuition |
| Would continue reading? | PASS | Attention momentarily lost at §4.4 (pipeline-QA jargon; fixed in R1) |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (of 06_paper.md)

**Findings**: 1 FATAL, 6 MAJOR, 7 minor notes.

| Persona | FATAL | MAJOR |
|---------|-------|-------|
| Accuracy Checker | 1 | 3 |
| Bored Reviewer | 0 | 1 |
| Skeptical Expert | 0 | 2 |

**Key issues addressed**:
1. **FATAL-ACC-001** — Paper claimed adjacent-layer KL is "best signal in half of our cells" (3/6); its own Table 1 and the authoritative h-e1-v2 gate grid show **2/6** (even 2/2/2 split across signals). Fixed in Abstract, Intro contribution 3, §2, §5.3, §7. The `065_ground_truth.yaml` file itself carried the same 3/6 typo and was corrected.
2. **MAJOR-ACC-002** — "single-pass / zero inference cost / free byproducts" contradicted the protocol's mandatory teacher-forced re-forward (~2× the monitored pass). Cost language made precise throughout.
3. **MAJOR-ACC-001** — "winning signal differs across datasets in 4 of 6 cells": 4/6 holds for the winning *layer*; the signal identity differs 6/6. Corrected.
4. **MAJOR-ACC-003** — "prior run" conflated the protocol-different archived v1 record with the protocol-identical h-e1 donor run; referents disambiguated (§3.1 vs §5.4).
5. **MAJOR-CRED-001** — Test-split evaluation advertised as zero-GPU yet not performed; pre-registration rationale added.
6. **MAJOR-CRED-002** — Implicit statistical assertions ("margins large relative to plausible noise") without computed statistics; softened to point-estimate language.
7. **MAJOR-ENG-001** — Pipeline artifacts leaking into prose (REAL_MODEL check, 37/37 tests, "this program", undefined "rescue claim"); reworded for external readers.

**Revision**: all 7 accepted; output `06_paper_r1.md` (+294 words).

### Round 2: Numerical Verification (of 06_paper_r1.md)

**Verification**: 19 pattern searches against raw Phase 4 artifacts (h-e1-v2/04_validation.md, experiment_results.json, 306-row grid CSV, experiment.log, h-e1 anchor forensics). All Table 1 AUROCs, six depth margins, gate margins (+0.059/+0.151), splits (500/500, 408/409), scale (5,451 = 1,817 × 3), adj_kl 2/6, anchor arithmetic (0.5928 − 0.5186 = +0.0742), 47 s halt, six protocol differences, 4/6 direction consistency, FEPoID skyline framing — **all reconcile exactly at raw-artifact level**. All 7 R1 fixes verified as landed.

**Findings**: 0 FATAL, 3 MAJOR (all accuracy), 5 minor notes.

1. **Screen counts** — "20/15/15 per model" (§3.3, Fig. 2 caption) contradicted by raw artifacts: the degeneracy screen runs **per cell** — 20/20 (LLaMA-2), 15/16 (Mistral), 15/16 (LLaMA-3). Proven by `experiment_results.json` retained_layers and the 306-row grid CSV (102 layers × 3 signals). Error had propagated from the Phase 4 summary into the ground-truth file (also corrected).
2. **GPU-hours** — "~2.5 GPU-hours" was the v1 *budget* figure; the logged v2 sweep ran 09:00:23→10:14:59 ≈ **1.25 GPU-hours**. §4.4 now reports measured compute; §5.4's budget quote correctly retained.
3. **Abstract cost clause** — "an order of magnitude below multi-sample methods" fails strict arithmetic on the paper's own numbers (2× vs ~10× = 5×); restated on the added-cost basis (one added re-forward vs ~10 added passes).

**Revision**: all 3 accepted; output `06_paper_r2.md` (+49 words).

### Convergence

- After R1: FATAL=0, MAJOR=0 remaining, persuasiveness passed — but min_rounds=2 → continued to mandatory R2 numerical verification.
- After R2: FATAL=0, MAJOR=0, persuasiveness passed, rounds=2 ≥ 2 → **CONVERGED**. No issue repeated across rounds.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | adj_kl cell count (2/6 basis), cost claim on added-cost basis |
| Introduction | Contribution 3 count fix, cost language, referent disambiguation |
| Related Work | "half of our cells" fix in cross-layer + positioning paragraphs |
| Methodology | §3.1 referent fix, §3.3 per-cell screen counts + Fig. 2 caption, §3.5 clarifications |
| Experiments | §4.4 pipeline-jargon rewrite + measured ~1.25 GPU-hours, §4.5 per-cell health wording |
| Results | §5.1/§5.3 signal-count fixes, §5.4 referent naming |
| Discussion | Point-estimate language, pre-registration rationale |
| Conclusion | adj_kl count, "rescue claim" definition, cost phrasing |

**Word count**: 6,528 → 6,871 (+343).

---

## Quality Improvements

- **Logical Consistency**: improved (referent conflation resolved; per-cell vs per-model screen semantics)
- **Numerical Accuracy**: improved (2/6 signal count; per-cell screen counts; measured GPU-hours; cost arithmetic)
- **Novelty Claims**: verified accurate (0 false novelty claims found; hedge propagation left as minor note)
- **Baseline Comparison**: verified fair (within-sweep-only framing sound; FEPoID correctly a cited skyline; no implied external re-runs)
- **Persuasiveness**: passed R1 with all checks true; §4.4 engagement fix applied
- **Hook Quality**: strong (dual-finding opening retained)

---

## Reviewer Preparation Notes

Remaining attack surfaces a real reviewer may raise (all disclosed in the paper):

1. **Selection-split-only evidence** — the numbers that selected the tuples also grade them. *Response*: existence tier is pre-registered as a precondition; locked test splits + frozen tuples make confirmation a zero-GPU follow-up on published caches.
2. **Single seed, no CIs; +0.0035 thinnest margin** — *Response*: flagged plainly as within-noise and counted as direction-consistent only; 5/6 margins exceed 0.03; bootstrap machinery implemented on cached data.
3. **Familiarity-vs-truthfulness confound** (Chi et al. 2025) — *Response*: claims scoped to class-separation under standard correctness labels; confound explicitly listed as unaddressed limitation with frequency-stratified diagnostics staged.
4. **One instruct model; tuning-polarity hypothesis untested** — *Response*: stated descriptively only; base-vs-instruct pair study named as the deciding follow-up.

---

## Process Notes

- Serena MCP in this session exposed symbol/LSP tools only (no `find_file`/`search_for_pattern`/`list_dir`); equivalent Grep/Glob/Bash searches were used and logged in each review round (19 in R2).
- `065_ground_truth.yaml` was corrected twice during review (adj_kl 3/6→2/6; per-cell screen counts; logged vs budgeted GPU-hours) — later phases should use the corrected version.
- Phase 5 baseline comparison was SKIPPED by config; the paper correctly makes only within-sweep comparisons.

**Next Phase**: 6.5.1 (Overleaf LaTeX/PDF generation) on `06_paper_final.md`.
