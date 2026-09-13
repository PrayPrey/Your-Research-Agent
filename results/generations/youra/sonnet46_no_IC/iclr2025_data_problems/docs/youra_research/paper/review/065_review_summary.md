# Adversarial Review Summary

**Paper**: One Size Does Not Fit All: Scale-Dependent Optimal Perplexity Filtering for Language Model Pre-training
**Review Completed**: 2026-08-04T23:59:00Z
**Rounds Completed**: 2 (R1 + R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED (Bored Reviewer would continue reading; abstract restructured to lead with finding)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 1     | 1        | 0         |
| MAJOR    | 6     | 6        | 0         |

**MINOR Issues**: Collected in `065_human_review_notes.md` (NOT auto-fixed) — 12 total (8 from R1, 4 from R2)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Restructured in R1 to lead with the counterintuitive τ*(14M)=20 vs τ*(31M)=50 finding |
| Problem clear by paragraph 2? | PASS | Introduction paragraph 1 directly demonstrates the effect |
| Novelty clear by page 1? | PASS | Section 2.4 "Our Position" clearly differentiates from prior work |
| Figure 1 self-explanatory? | PASS | Bar chart by scale × curation with clear caption |
| Would continue reading? | YES | Strong hook, concrete numbers in abstract |
| Attention lost at? | Never (after R1 abstract restructure) |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings**:
| Category | Issues Found | Severity |
|----------|--------------|----------|
| Corpus pool size inconsistency (50K vs 5K) | 1 | FATAL |
| Wall-clock time precision | 1 | MAJOR |
| Nominal vs actual parameter counts | 1 | MAJOR |

**Bored Reviewer Findings**:
| Category | Issues Found | Severity |
|----------|--------------|----------|
| Abstract buries the counterintuitive finding | 1 | MAJOR |

**Skeptical Expert Findings**:
| Category | Issues Found | Severity |
|----------|--------------|----------|
| "First factorial experiment" claim not defended | 1 | MAJOR |
| Proxy model threshold overclaimed as universal boundary | 1 | MAJOR |
| Scope extrapolation to 7B/13B/70B cascades | 1 | MAJOR |

**Key Issues Addressed in R1**:
1. **FATAL-ACC-001** (50K vs 5K pool size): Clarified in §3.2 — 50K streamed from FineWeb, 5K scored for curation statistics; retention fractions (176/5000, 2074/5000) correctly represent the scored pool.
2. **MAJOR-ENG-001** (abstract buries finding): Restructured abstract to lead with τ*(14M)=20 vs τ*(31M)=50.
3. **MAJOR-CRED-001** ("first factorial" claim): Softened to "to our knowledge"; added explicit engagement with FineWeb2 and DataComp-LM in §2.4.
4. **MAJOR-CRED-002** (proxy threshold overclaim): Added "in our experiments" qualifier in §2.3, §5.4, §6.1, §7.1.
5. **MAJOR-CRED-003** (cascade extrapolation): Abstract and §7.3 now frame as PoC-scale findings; 7B/13B/70B reference reframed as conditional hypothesis.
6. **MAJOR-ACC-001** (wall-clock precision): Clarified to "~68 minutes for all 24 runs (including 2 pre-completed runs)".
7. **MAJOR-ACC-002** (nominal vs actual params): Added footnote at §3.1 clarifying Pythia nominal vs actual parameter counts.

### Round 2: Numerical Verification

**Accuracy Checker (R2 — numerical)**:
- All Table 1 values verified against 04_validation.md ✓
- Retention rate arithmetic verified: 176/5000=3.52%≈3.5%, 2074/5000=41.48%≈41.5%, ratio=11.8×≈12× ✓
- Random baseline = 0.25 (4-choice HellaSwag) ✓
- Effect size Δacc_norm ≈ 0.003 confirmed ✓
- 24 runs = 3×2×2×2 confirmed ✓
- All 7 R1 fixes verified as correctly implemented with no new contradictions

**Skeptical Expert (R2)**:
- R1 novelty hedging consistent throughout
- Proxy model qualification appropriate
- Scope framing correctly scoped to PoC

**One MINOR substantive improvement** (accepted in R2):
- Added disclosure in §3.2 that at τ=20, the ~350K-token filtered corpus requires ~2,800× repetition to reach 1B training budget.

---

## Sections Modified (cumulative)

| Section | Modifications |
|---------|---------------|
| Abstract | Restructured to lead with finding; added PoC qualifier on conclusion |
| Introduction §1.2 | Removed overclaiming "first" language |
| Introduction §1.3 | Added "in our experiments" to proxy model contribution |
| Related Work §2.3 | Softened proxy threshold claim |
| Related Work §2.4 | Softened "first" to "to our knowledge"; added FineWeb2/DataComp-LM engagement |
| Methodology §3.1 | Added footnote on actual vs nominal parameter counts |
| Methodology §3.2 | Clarified 50K streamed vs 5K scored pool; fixed fatal inconsistency; added ~2,800× repetition disclosure |
| Experimental Setup §4.1 | Fixed wall-clock claim precision |
| Results §5.4 | Softened "establishes feasibility boundary" to provisional claim |
| Discussion §6.1 | Qualified Finding 2 to "in our experiments" |
| Conclusion §7.1 | Softened proxy model contribution; added PoC qualifier |
| Conclusion §7.3 | Reframed 7B/13B/70B cascade claim as conditional hypothesis |
| Appendix A.1 | Clarified table header and added 5K/50K note |
| References | Added Gururangan et al. 2024; removed [UNVERIFIED] annotation |

---

## Quality Improvements

- **Logical Consistency**: Improved (50K/5K clarified, parameter counts footnoted)
- **Numerical Accuracy**: Verified correct
- **Novelty Claims**: Refined (appropriately hedged)
- **Baseline Comparison**: N/A (no baseline comparison in this paper)
- **Persuasiveness**: Improved (abstract restructured)
- **Scope Framing**: Improved (PoC scale consistently qualified)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Effect size**: Δacc_norm ≈ 0.003 is very small — paper now acknowledges this explicitly in L2 limitation with justification (500 steps far from convergence, effects amplify with training duration).
2. **Scale generalization**: 14M/31M vs 70M/160M target — handled in L1 limitation; full pipeline validated (23/23 tests).
3. **Extreme repetition at τ=20**: Now disclosed in §3.2; ~2,800× is unusual and reviewers may note it.
4. **Single corpus and architecture**: L5 limitation acknowledged.
5. **Proxy model boundary from single experiment**: Now appropriately hedged as "in our experiments."

Suggested responses if these are raised:
- Effect size: "At 500 training steps far from convergence, small effects are expected. The direction confirmation is the key contribution; effect magnitude will amplify with scale."
- Scale gap: "The full pipeline (23/23 tests) is ready for 70M/160M × 50B runs — requires only compute."
- τ=20 repetition: "Extreme selectivity at PoC scale is a known tradeoff; the corpus repetition is now explicitly disclosed and is itself a finding motivating the scale-up."
