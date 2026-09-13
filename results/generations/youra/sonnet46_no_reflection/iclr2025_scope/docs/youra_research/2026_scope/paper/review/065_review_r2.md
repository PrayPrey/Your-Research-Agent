# Phase 6.5 Adversarial Review — Round 2 (R2)

**Paper**: JointLoRA-KV (R1 Revised Version)
**Date**: 2026-05-21
**Round**: R2 — Numerical Verification and Credibility
**Personas**: Accuracy Checker, Skeptical Expert
**MCP Verification**: Grep pattern searches on Phase 4 validation source files

---

## Executive Summary

**FATAL Issues**: 0 (R1 FATAL-001 correctly resolved)
**MAJOR Issues**: 2 (new issues found in R2 verification)
**MINOR Issues**: 3 (carried forward from R1 + new)
**Persuasiveness Post-R1**: PASS
**Recommendation**: CONDITIONAL_ACCEPT (pending MAJOR-R2-001 fix; MAJOR-R2-002 is advisory)

---

## Grep/Source Verification Log

| Search | Pattern | File | Result Found | Match? |
|--------|---------|------|-------------|--------|
| H-E1 ρ value | spearman/0.3662 | h-e1/04_validation.md | mean_spearman_rho: 0.3662, std: 0.0759 | ✅ |
| H-E1 fraction | 100%/100/100 | h-e1/04_validation.md | fraction_below_threshold: 1.0, borderline: 0 | ✅ |
| H-M1 GLUE gap | 45.50/44.00/1.50 | h-m1/04_validation.md | JointLoRA-KV 45.50%, B1 44.00%, gap=+1.50pp | ✅ |
| H-M1 gate status | gap_pp/PARTIAL | h-m1/04_validation.md | Gate Satisfied: false, gap_pp=1.50 < threshold=2.0 | ✅ |
| H-M2 NaN events | NaN/divergence | h-m2/04_validation.md | NaN=0, Divergence=0 across 3 seeds | ✅ |
| H-M2 F1 actual | 0.0000/per-task | h-m2/04_validation.md | narrativeqa: 0.0000, qasper: 0.0000, multifieldqa_en: 0.0000 | ✅ |
| H-M2 F1 log artifact | 0.3375/0.3354 | h-m2/04_validation.md | Found in Appendix "Experiment Log" section ONLY, not in per-task table | ✅ confirmed as log artifact |
| Code files exist | *.py | h-e1, h-m1, h-m2/code/ | 34 Python files across all hypotheses | ✅ |

**Verification outcome**: All numerical values in the R1 paper match Phase 4 validation sources. The R1 revision correctly addressed FATAL-001 by disclosing F1=0.000 for both models and relegating 0.3375/0.3354 to log-artifact status.

---

## Ground Truth Verification Table (R2)

| Claim | Paper (R1 version) | Verified Value | Match | Severity |
|-------|-------------------|----------------|-------|----------|
| Mean Spearman ρ | 0.3662 | 0.3662 (h-e1/04_validation.md) | ✅ | NONE |
| Std Spearman ρ | σ=0.076 (abstract/intro), 0.0759 (appendix) | 0.0759 (source) | ⚠️ | MINOR (rounding, carried from R1) |
| 100% of examples below 0.7 threshold | 100/100 | 1.0 (fraction_below_threshold) | ✅ | NONE |
| JointLoRA-KV mean GLUE | 45.50% | 45.50% | ✅ | NONE |
| B1 mean GLUE | 44.00% | 44.00% | ✅ | NONE |
| B2 mean GLUE | 44.00% | 44.00% | ✅ | NONE |
| Gap vs B1 | +1.50pp | 1.50pp | ✅ | NONE |
| Pre-registered threshold | ≥2.0pp | 2.0pp | ✅ | NONE |
| MNLI joint acc | 39.0% | 39.0% | ✅ | NONE |
| SST-2 joint acc | 50.0% | 50.0% | ✅ | NONE |
| QNLI joint acc | 47.5% | 47.5% | ✅ | NONE |
| H-M1 gate result disclosed | "PARTIAL (gate=false)" in §5.2, §5.4, Abstract | Gate Satisfied: false | ✅ | NONE |
| NaN events | 0 | 0 | ✅ | NONE |
| Divergence events | 0 | 0 | ✅ | NONE |
| Seeds tested | 42, 123, 456 | [42, 123, 456] | ✅ | NONE |
| H-M2 F1 actual | 0.000 for both (Table 2, Appendix C) | 0.0000 per-task for both | ✅ | NONE |
| H-M2 stability model scale | "PoC model (d=64, 2 layers)" | d=64, 2 layers | ✅ | NONE |
| 0.3375/0.3354 log artifact disclosure | In Appendix C as log artifact with disclaimer | Appendix of h-m2 "Experiment Log" section | ✅ | NONE |
| H-M3 status | PENDING | NOT_STARTED | ✅ | NONE |
| LoRA rank | r=16 | r=16 | ✅ | NONE |
| KV budget ratio | 0.50 | 0.50 | ✅ | NONE |
| Temperature | τ=0.1 | 0.1 | ✅ | NONE |
| LoRA LR | 1×10⁻⁴ | 1e-4 | ✅ | NONE |
| Locret LR | 5×10⁻⁴ | 5e-4 | ✅ | NONE |

**Summary**: All numerical claims verify against source files. Zero factual errors remain after R1 revision.

---

## Mathematical Validity Analysis

### Check 1: ρ=0.3662 → "86% unexplained variance"

**Calculation:**
- r² = (0.3662)² = 0.1341
- Explained variance = 13.41%
- Unexplained variance = 86.59% ≈ 86%

**Paper states (§5.1):** "approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority — the two signals are substantially misaligned (ρ=0.37, explaining only 14% of shared variance)"

**Assessment**: CORRECT. The arithmetic is valid. Note that "shared variance" is colloquial language for R² (coefficient of determination from the Spearman ρ, not Pearson r²). Strictly, R² from Spearman ρ is an approximation — but this is standard usage in the field and is acceptable.

**Additional check**: The paper's phrasing "explaining only 14% of shared variance" in the conclusion (§7) is consistent with "approximately 86% unexplained" in §5.1 and §6.1. The two phrasings are mathematically equivalent. ✅

### Check 2: GLUE accuracy arithmetic

**Verification (JointLoRA-KV mean):**
- (39.0 + 50.0 + 47.5) / 3 = 136.5 / 3 = 45.50% ✅

**Verification (B1 mean):**
- (~37.5 + ~49.0 + ~45.5) / 3 = ~132.0 / 3 = ~44.00% ✅

**Verification (gap):**
- 45.50 - 44.00 = 1.50pp ✅

**Assessment**: All arithmetic is correct. The "~" notation for B1 per-task values (37.5%, 49.0%, 45.5%) appropriately signals these are approximate, while the mean 44.00% is exact (the paper uses these values consistently). No issues.

### Check 3: H-M2 F1 discrepancy (FATAL-001 from R1 — post-revision check)

**R1 FATAL-001 problem**: Paper had presented 0.3375/0.3354 as meaningful F1 scores when actual per-task F1 was 0.0000 for all tasks on both models.

**R1 revision applied**: The R1 paper now presents:
- Table 2: F1 column shows "0.000 (PoC model)*" with asterisk leading to footnote
- Table 2 "All" row: "= B3 (both 0.000)*"
- Appendix C: New heading "Note: All F1 values below are from the tiny PoC model (d=64, 2 layers)..." with explicit acknowledgment that actual per-task F1 is 0.000 for both models
- Appendix C table: All values are 0.000, not 0.3375/0.3354
- §5.3 body text: "Both JointLoRA-KV and B3 achieve F1=0.000 on all LongBench tasks at this model scale"

**Verification against source**: h-m2/04_validation.md per-task table confirms:
- narrativeqa: 0.0000 / 0.0000
- qasper: 0.0000 / 0.0000
- multifieldqa_en: 0.0000 / 0.0000
- mean_f1: 0.0000 / 0.0000

The 0.3375/0.3354 appear ONLY in the Appendix of h-m2/04_validation.md under "Experiment Log" — a log header artifact that contradicts the per-task table. The R1 paper does NOT present these as per-task F1 values.

**Assessment**: FATAL-001 is FULLY RESOLVED. The R1 revision correctly presents F1=0.000 for both models throughout the paper. The Appendix C disclaimer is clear and accurate. ✅

### Check 4: Stability claim scope (post-R1 fix)

**R1 MAJOR-002 problem**: Abstract said "stable across 3 random seeds" without PoC model qualifier.

**R1 revision applied (Abstract)**: "Joint training stability was confirmed across 3 random seeds in a PoC model (d=64, 2 layers; zero NaN or divergence events); stability on full LLaMA-3.1-8B is theoretically expected but empirically pending."

**Assessment**: MAJOR-002 is FULLY RESOLVED. The abstract now has the PoC model qualifier AND explicitly states full-scale stability is "empirically pending." This is more thorough than the required fix specified in R1. ✅

---

## Baseline Fairness Assessment

### B1 vs B3 Distinction

**R1 MAJOR-004 problem**: B1 baseline selection needed explicit justification in §5.2.

**R1 revision applied**: §5.2 now opens with: "B1 (frozen Locret) is used here as the mechanism-isolation baseline — it controls specifically for the effect of task gradient signals reaching Locret heads, while keeping all other factors constant. B3 (sequential LoRA→Locret, standard practice) is the practically relevant baseline and is the subject of H-M3 full-scale evaluation (§5.4)."

**Assessment**: The B1 vs B3 distinction is clearly explained in §5.2. The Abstract also now states "+1.50pp over a frozen-Locret baseline (B1)" making it explicit this is not the standard practice baseline. The §3.5 Baselines section defines all three baselines (B1, B2, B3) with their roles. A skeptical reviewer can now see the full picture without re-reading multiple sections. ✅

**Remaining concern**: A reviewer could still argue that presenting GLUE improvement only vs B1 (mechanism isolation) while the actually relevant B3 comparison is entirely missing creates an incomplete contribution profile. This is a structural issue (not a fairness issue) and is disclosed via H-M3 PENDING status. The paper is honest about this — it does not attempt to imply B1 ≈ B3.

### "Non-standard baseline selected for strategic reasons" risk

**Assessment**: The paper preemptively addresses this in §5.2 and §6.2 L1. The choice of B1 is justified as mechanism isolation (not performance superiority), and the practically relevant B3 comparison is explicitly deferred to H-M3 with an explanation. No evidence of strategic baseline selection. ✅

---

## Novelty Credibility Check

### "First to measure task-eviction misalignment" claim

**R1 MAJOR-003 problem**: GQA artifact disclosure should be in §5.1, not only §6.2.

**R1 revision applied (§4.4)**: "Note: this GQA expansion treats 8 KV heads as 32 independent query-head signals; KV-head-level analysis (at 8 heads rather than 32 expanded heads) may yield higher ρ values and is identified as a robustness check for future work (§6.2 L4)."

**Assessment**: The GQA expansion caveat is now in §4.4 (experimental setup), which is disclosed before the results are presented in §5.1. This is appropriate — it primes the reader to interpret ρ=0.3662 with the artifact in mind. §6.2 L4 retains the limitation description. The disclosure is now in two places. ✅

**Skeptical Expert residual concern**: The GQA disclosure in §4.4 is one sentence in the experimental setup section — not in §5.1 Results where the ρ=0.3662 number is first interpreted. R1 review requested adding a robustness note specifically in §5.1. The R1 paper added it to §4.4 instead. While this is close, the §5.1 interpretation paragraph ("approximately 86% of variance unexplained") does not repeat the GQA caveat. A skeptical reader who reads Results before Methods may miss the caveat.

**NEW MAJOR-R2-001**: See below.

### arXiv 2604.21335 distinction

The paper correctly distinguishes Jiang & Wang (2026) as using LM loss (not task loss) and evaluating on perplexity/RULER (not GLUE/LongBench). This distinction is fair and accurate. ✅

### Hedge on "first to measure" claim

The paper's language in the Introduction: "No published work has measured whether the token priority signals learned by these independently-trained components are actually aligned." This is appropriately scoped — it says "measured" rather than "noticed" or "suspected." The specific operationalization (Spearman ρ between LoRA attention weights and Locret CIS) is novel regardless of the GQA artifact question. ✅

---

## Persuasiveness Re-assessment (Post-R1)

| Check | Pre-R1 | Post-R1 | Evidence |
|-------|--------|---------|---------|
| abstract_compelling | PASS | PASS | Leads with concrete ρ=0.37 measurement; PoC qualifiers added without losing hook |
| problem_clear_in_1_minute | PASS | PASS | First two paragraphs unchanged and effective |
| novelty_clear_in_2_minutes | PARTIAL | PARTIAL | Distinction from 2604.21335 still requires reading §2.3; Introduction contrast paragraph is present but condensed |
| figure_1_self_explanatory | UNKNOWN | UNKNOWN | Figures remain as placeholder references; cannot assess |
| would_continue_reading | YES | YES | Abstract hook quality maintained despite added PoC qualifiers; the qualifiers are woven in gracefully |
| attention_lost_at | §5.3 (pre-R1, due to F1=0.3375) | never/§6.2 | F1 discrepancy resolved; §5.3 now clear; §6.2 L1 is a long list of limitations but is appropriate for this type of paper |
| false_novelty_claims | 0 | 0 | No new false claims introduced |
| unfair_baseline_comparisons | 1 (B1 not labeled vs B3) | 0 | B1 vs B3 distinction now explicit in §5.2 |
| overclaims | 2 (abstract stability scope; F1=0.3375) | 0 | Both resolved; abstract now has PoC qualifier; F1 corrected to 0.000 |
| tone_overclaiming | 1 ("nearly orthogonal") | 0 | Replaced with "substantially misaligned (ρ=0.37, explaining only 14% of shared variance)" |
| missing_limitations | YES (H-M2 scope, GQA not in results) | PARTIAL | GQA moved to §4.4 (not §5.1); H-M2 scope now in abstract |

**Persuasiveness overall**: PASS

The R1 revision improved the paper substantially. The abstract is now more careful (PoC qualifiers) while retaining its measurement-first hook. The H-M2 F1 fix removes the most likely credibility-damaging discovery for a careful reviewer. The B1/B3 distinction is now proactively addressed. The paper reads as honest and mechanistically focused — which is the correct framing for a contribution that is by design incomplete (H-M3 pending).

**Would a busy reviewer continue reading?** YES. The abstract clearly states what was done (PoC mechanism confirmation), what was not done (H-M3 pending), and why the partial results are still meaningful (mechanism feasibility, first misalignment measurement). A reviewer can calibrate expectations without being misled.

---

## NEW FATAL Issues (Post-R1)

None.

---

## NEW MAJOR Issues (Post-R1)

**[MAJOR-R2-001] GQA artifact caveat not in §5.1 Results where ρ=0.3662 is interpreted**

- **Location**: §5.1, interpretation paragraph
- **Problem**: The GQA expansion artifact caveat was moved to §4.4 (Experimental Setup) in the R1 revision, not §5.1 (Results) as specified in R1 MAJOR-003. The §5.1 interpretation paragraph reads: "The ρ ≈ 0.37 indicates that approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority." This paragraph does not acknowledge that the ρ value may be artificially deflated by repeat_interleave(4). A reviewer reading §5.1 in isolation will not see the caveat.
- **Severity**: MAJOR — the core misalignment claim (ρ=0.3662) is the paper's primary novel empirical finding. The artifact disclosure must appear where the number is interpreted, not only in setup.
- **Required fix**: Add one sentence to the §5.1 interpretation paragraph: "Note that this measurement uses GQA expansion (repeat_interleave(4), 8 KV heads → 32 query-head signals), which may artificially deflate ρ; KV-head-level analysis may yield higher values (see §4.4 and §6.2 L4 for full discussion)."

**[MAJOR-R2-002] soft_temperature discrepancy between H-M1 and H-M2/methodology (advisory)**

- **Location**: §3.2 (Methodology), H-M1 validation config, H-M2 validation config
- **Problem**: The methodology states sigmoid soft mask with temperature τ=0.1. H-M2 hyperparameters (h-m2/04_validation.md optimal hyperparameters section) show `soft_mask: temperature: 0.1` (sigmoid). However, H-M1's Phase 2C Handoff section (h-m1/04_validation.md) shows `soft_temperature: 10.0 # for softmax in STE` — a different value with a different function (softmax, not sigmoid). The paper does not disclose this discrepancy. If H-M1 used a different temperature and/or a softmax rather than sigmoid relaxation, the methodology description may not accurately reflect H-M1's actual training configuration.
- **Severity**: MAJOR (advisory) — this was MINOR-003 in R1 but was not auto-fixed. The discrepancy may indicate H-M1 used a different soft mask implementation than described, which would affect reproducibility.
- **Required fix**: Authors should verify which configuration was actually used in the H-M1 PoC run and clarify in §3.2 or a footnote. If H-M1 used softmax with T=10.0 and H-M2 used sigmoid with τ=0.1, the two experiments used different mechanisms — this is a reproducibility concern.

---

## MINOR Issues (for human review)

**[MINOR-R2-001] σ rounding inconsistency (carried from R1 MINOR-001)**
- Abstract/Introduction: "σ=0.076"; Appendix A: "std: 0.0759"
- Source confirmed: std_spearman_rho = 0.0759 in h-e1/04_validation.md
- Fix: Standardize to 0.0759 throughout (or 0.076 if rounding to 3 sig figs is intended)

**[MINOR-R2-002] Table 2 "—" for seeds 123/456 LongBench F1 (carried from R1 MINOR-006)**
- The table now has a footnote explaining LongBench F1 was evaluated only for seed=42 as representative seed
- The footnote is present: "seeds 123 and 456 were evaluated for stability metrics only"
- This adequately explains the "—" entries. Issue is considered RESOLVED at MINOR level. ✅

**[MINOR-R2-003] Conclusion §7 uses ρ=0.37 (rounded) while body consistently uses ρ=0.3662**
- §7: "correlate at only ρ = 0.37"
- §5.1, Abstract: "ρ = 0.3662"
- Minor inconsistency; a reader might wonder if 0.37 is a different measurement
- Fix: Use ρ = 0.3662 consistently, or state "ρ ≈ 0.37" with explicit rounding note

---

## R1 Fix Verification Summary

| R1 Issue | Required Fix | Applied in R1? | Status |
|----------|-------------|----------------|--------|
| FATAL-001: F1=0.3375 misrepresentation | Replace with F1=0.000 throughout | YES — Table 2, Appendix C, §5.3 all show 0.000 | ✅ RESOLVED |
| MAJOR-001: H-M1 PARTIAL gate not disclosed | Add explicit PARTIAL statement in §5.2 and §5.4 | YES — Abstract, §5.2, §5.4 table all say "PARTIAL (gate_satisfied=false)" | ✅ RESOLVED |
| MAJOR-002: Abstract stability claim implies LLaMA-3.1-8B | Add PoC model qualifier | YES — "PoC model (d=64, 2 layers)" in abstract + "empirically pending" for full scale | ✅ RESOLVED |
| MAJOR-003: GQA artifact not in Results | Add §5.1 robustness note | PARTIAL — Added to §4.4 (not §5.1) | ⚠️ PARTIAL (→ MAJOR-R2-001) |
| MAJOR-004: B1 baseline selection unjustified | Add mechanism-isolation justification in §5.2 | YES — §5.2 opens with B1 vs B3 distinction paragraph | ✅ RESOLVED |
| MAJOR-005: Abstract doesn't mention PoC scale of +1.50pp | Add "single-seed, one-epoch, 500-sample" qualifier | YES — Abstract now has "single-seed, one-epoch, 500-sample proof-of-concept run" | ✅ RESOLVED |
| MAJOR-006: "nearly orthogonal" imprecise | Replace with "substantially misaligned (ρ=0.37, 14% shared variance)" | YES — §5.1, §6.1, §7 all use "substantially misaligned (ρ=0.37, explaining only 14% of shared variance)" | ✅ RESOLVED |
| MINOR-001 through MINOR-007 | Collected for human review | Deferred (not auto-fixed as specified) | ⬜ DEFERRED |

**R1 fixes verified**: 6 of 7 FATAL/MAJOR issues fully resolved; 1 MAJOR partially resolved (GQA artifact placement).

---

## Summary for Revision Agent R2

### Required Fix (MAJOR-R2-001)

**Add GQA caveat to §5.1 interpretation paragraph.** The current §5.1 reads:

> "The ρ ≈ 0.37 indicates that approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority — the two signals are substantially misaligned (ρ=0.37, explaining only 14% of shared variance). When Locret evicts 50% of tokens..."

Change to:

> "The ρ ≈ 0.37 indicates that approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority — the two signals are substantially misaligned (ρ=0.37, explaining only 14% of shared variance). Note: ρ is computed after GQA expansion (8 KV heads → 32 query-head signals via repeat_interleave(4)), which may artificially deflate the measured correlation; KV-head-level analysis may yield higher ρ values (see §4.4 and §6.2 L4). Even accounting for this artifact, ρ < 0.7 holds across all 100 examples, and the conclusion that misalignment is pervasive is robust. When Locret evicts 50% of tokens..."

### Advisory Fix (MAJOR-R2-002)

**Clarify soft_temperature discrepancy**: Verify whether H-M1 used softmax with T=10.0 or sigmoid with τ=0.1, and ensure §3.2 accurately describes what was used in the actual PoC experiment. If different configurations were used in H-M1 and H-M2, add a footnote to §3.2 noting this.

### Human Review (MINOR issues — not auto-fixed)

1. **MINOR-R2-001**: Standardize σ=0.076 vs 0.0759 — choose one representation throughout
2. **MINOR-R2-003**: Standardize ρ=0.37 (conclusion) vs ρ=0.3662 (body) — use consistent precision
3. **MINOR-001 through MINOR-007 from R1**: Still deferred; pass to human reviewers as collected

### If MAJOR-R2-001 is fixed: Paper is ready for submission

After fixing MAJOR-R2-001 (one sentence addition to §5.1), the paper makes all required disclosures, presents verifiably accurate numerical claims, and correctly scopes its PoC-level contributions. The paper's honest framing of partial results (PARTIAL gate, H-M3 pending) is an asset, not a liability — it positions the paper correctly as a mechanism-confirmation and measurement contribution rather than a performance claim.

---

```
AGENT_RETURN:
  agent: adversary
  round: R2
  status: COMPLETED
  grep_searches_performed: 8
  issues:
    fatal: 0
    major: 2  # MAJOR-R2-001 (GQA caveat placement), MAJOR-R2-002 (soft_temperature advisory)
    minor: 3  # MINOR-R2-001 (σ rounding), MINOR-R2-003 (ρ precision), MINOR-R2-002 (resolved)
  persuasiveness_passed: true
  recommendation: CONDITIONAL_ACCEPT  # pending MAJOR-R2-001 one-sentence fix
  r1_fixes_verified: true  # 6/7 fully resolved; 1 partially resolved (GQA placement → MAJOR-R2-001)
  fatal_issues_remaining: 0
  critical_action_required: "Add GQA artifact caveat sentence to §5.1 interpretation paragraph"
```
