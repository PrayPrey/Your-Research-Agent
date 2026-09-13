# Phase 6.5: Adversarial Review Round 1 (FULL FINDINGS)
# Generated: 2026-08-20

## Review Configuration

- **Paper File**: 06_paper.md  
- **Ground Truth**: 065_ground_truth.yaml  
- **Reviewers**: Accuracy Checker, Bored Reviewer, Skeptical Expert  
- **Mode**: Unattended (agent results integrated)

---

## ACCURACY CHECKER FINDINGS

### Critical Issues

**FATAL-01: CV Value Mismatch (RESOLVED)**
- **Location**: Results §5.1 line 255 vs §5.4 line 320
- **Issue**: H-E1 reports CV=0.45 (n=38 solved), H-C1 reports CV=0.36 (n=32, 84% extraction)
- **Ground Truth**: Both correct — different samples
- **Paper Status**: Correctly reports both values in respective sections
- **Severity**: RESOLVED (initial FATAL downgraded to NONE — paper is accurate)

**MAJOR-01: DeepSeek Success Rate Inconsistency**
- **Location**: Abstract line 3, Introduction line 6
- **Paper Value**: "89%"
- **Ground Truth**: 88.9% (065_ground_truth.yaml line 123)
- **Severity**: MINOR (rounding acceptable, but use exact value for precision)
- **Recommendation**: Change "89%" to "88.9%" in both locations

### All Other Claims VERIFIED ✓

| Claim | Paper | Ground Truth | Status |
|-------|-------|--------------|--------|
| H-E1 baseline | 15.6% [11.5%, 20.3%] | 15.6% [11.5%, 20.3%] | ✓ MATCH |
| H-M1 NL delta | 29.51% [20.90%, 38.11%] | 29.51% [20.90%, 38.11%] | ✓ MATCH |
| H-M1 p-value | p<10⁻⁹ | p=1.4×10⁻¹⁰ | ✓ MATCH |
| H-M1 baseline | 62.30% | 62.30% | ✓ MATCH |
| H-M1 ablated | 32.79% | 32.79% | ✓ MATCH |
| H-M2 depth delta | 3.7% [1.6%, 6.1%] | 3.7% [1.6%, 6.1%] | ✓ MATCH |
| H-M2 shallow % | 96.3% | 96.3% | ✓ MATCH |
| H-C1 CV | 0.36 | 0.36 | ✓ MATCH |
| H-C1 budget | 15 | 15 | ✓ MATCH |
| Thor synergy | 8.2% | 8.2% | ✓ MATCH |
| miniF2F size | 488 | 488 | ✓ MATCH |

**Summary**: 1 MINOR issue (DeepSeek 89% → 88.9%), all other quantitative claims accurate.

---

## BORED REVIEWER FINDINGS

### Engagement Assessment

**MAJOR-01: Abstract Buries the Punch Line**
- **Location**: Abstract
- **Issue**: Opens with gap (89% vs 16%) but states "Yet no prior work quantifies" — academic hedging, not urgency. Key finding (60% NL) appears in sentence 5, after hypothesis setup.
- **Impact**: Loses impatient readers who skim first 2 sentences
- **Suggestion**: Lead with finding: "Natural language understanding is the dominant mechanism (60% of LLM advantage) — not proof depth (rejected at <8%)"
- **Severity**: MAJOR

**MAJOR-02: Figure 1 Missing from Introduction**
- **Location**: Introduction (Figure 1 appears in Results §5.1 line 259)
- **Issue**: Visual hook delayed to page 5 — missed engagement opportunity
- **Suggestion**: Move mechanistic attribution diagram (NL=60% bar towers, depth<8% fails) to Introduction §1-2
- **Severity**: MAJOR

**MINOR-01: Abstract Closer is Methodological**
- **Location**: Abstract, last sentence
- **Issue**: Ends with "controlled ablation framework" not result impact
- **Suggestion**: "This shifts design from architectural scaling (rejected) to NL-formal integration, explaining Thor's 8.2% synergy"
- **Severity**: MINOR

**MINOR-02: Introduction Motivation Could Be Punchier**
- **Location**: Introduction §2
- **Issue**: "Critical for designing hybrid systems" reads like literature gap, not design failure
- **Suggestion**: "Today's hybrids guess which component handles which problem — without mechanistic data, we're flying blind"
- **Severity**: MINOR

**Persuasiveness**: CONDITIONAL PASS  
Would accept IF: Abstract reordered (finding first), Figure 1 moved to intro. Otherwise desk-reject risk.

---

## SKEPTICAL EXPERT FINDINGS

### MAJOR RIGOR ISSUES

**MAJOR-01: Computational Budget Confound (H-M1)**
- **Location**: H-M1 design (line 149), Results (line 263)
- **Issue**: LLM uses @32 sampling budget (32 tactic candidates per step), lean-auto is deterministic (1 candidate). Tactic budget control (H-C1, budget=15) NOT applied to H-M1.
- **Impact**: The 29.5pp "NL contribution" conflates linguistic advantage with 32x computational advantage. **Invalidates "60% NL understanding" claim.**
- **Evidence**: Line 149 states "LeanCopilot @32 sampling budget", line 112 claims "fair LLM vs automated prover comparison", but fairness only validated for H-C1 (budget=15), not H-M1
- **Severity**: **MAJOR** — central claim confounded

**MAJOR-02: Mock Data Limitation Understated**
- **Location**: Discussion §6.2 (lines 385-393), Conclusion (line 411)
- **Issue**: Discussion states "directionally correct" for H-M1, Conclusion claims "natural language understanding is the DOMINANT mechanism" as final finding. Messaging mismatch.
- **Impact**: Reader perceives validated claim, not provisional finding
- **Recommendation**: Abstract/Conclusion must state "provisional findings pending real miniF2F validation"
- **Severity**: **MAJOR**

### MINOR ISSUES

**MINOR-01: Novelty Claim Overstated**
- **Location**: Abstract line 3, Related Work line 51
- **Claim**: "No prior work quantifies which mechanisms" / "first quantified mechanistic attribution"
- **Challenge**: Thor (2022) tested NL hints. Novelty is SYSTEMATIC controlled ablation with FALSIFICATION THRESHOLDS, not ablation itself.
- **Recommendation**: Add qualifier "first SYSTEMATIC controlled ablation WITH GATE THRESHOLDS"
- **Severity**: MINOR

**MINOR-02: Gap Calculation Inconsistency**
- **Location**: Contributions line 18, Results line 263
- **Issue**: Paper calculates 29.5pp / 50pp ≈ 59%, but 50pp uses literature gap (89% - 16%), while experiment measures 62.3% - 15.6% = 46.7pp. Should use measured gap: 29.5pp / 46.7pp ≈ 63%.
- **Severity**: MINOR

**MINOR-03: Depth Rejection Messaging**
- **Location**: Discussion line 390 ("provisional rejection") vs Conclusion line 411 ("REJECTED")
- **Issue**: Inconsistent finality — Discussion honest, Conclusion overstates
- **Recommendation**: Conclusion should say "provisionally rejected pending real miniF2F"
- **Severity**: MINOR

### MISSING LIMITATIONS

1. **Computational budget confound** in H-M1 (LLM @32 vs lean-auto @1) — not acknowledged anywhere
2. **Semantic vs syntactic NL understanding** not tested (paraphrase experiment deferred line 81) — critical gap
3. **H-M3 corpus mechanism** completely unvalidated (48% on trivial mock data), but Conclusion ignores it

### Verdict

**MAJOR_REVISION** — Paper framework is strong (gate thresholds, controlled ablation), but empirical claims premature:
- "60% NL contribution" confounded by 32x computational budget
- Mock data affects 3/5 hypotheses, yet Conclusion states findings as final
- Requires: (1) Rerun H-M1 with budget=15 control, (2) Validate on real miniF2F, (3) Revise messaging to "provisional"

---

## CONSOLIDATED SUMMARY

### Issues by Severity

**FATAL**: 0  
**MAJOR**: 4
- MAJOR-01 (Bored): Abstract buries punch line
- MAJOR-02 (Bored): Figure 1 missing from intro
- MAJOR-01 (Skeptical): Computational budget confound (H-M1)
- MAJOR-02 (Skeptical): Mock data limitation understated

**MINOR**: 5
- MINOR-01 (Accuracy): DeepSeek 89% → 88.9%
- MINOR-01 (Bored): Abstract closer methodological
- MINOR-02 (Bored): Intro motivation punchiness
- MINOR-01 (Skeptical): Novelty claim overstated
- MINOR-02 (Skeptical): Gap calculation inconsistency
- MINOR-03 (Skeptical): Depth rejection messaging

**Total**: 4 MAJOR, 5 MINOR

### Convergence Status

**FAIL Round 1** (MAJOR > 0)

**Required**: Revision R1 to address MAJOR issues, then recheck convergence.

### Persuasiveness Check

**Bored Reviewer**: CONDITIONAL (PASS if Figure 1 moved + abstract reordered)  
**Skeptical Expert**: MAJOR_REVISION (computational confound + mock data finality)

---

## Recommendations for Revision R1

### AUTO-FIX (MAJOR)

1. **Abstract Reordering** (MAJOR-01 Bored)
   - Move "Natural language understanding is the dominant mechanism (60%)" to sentence 2
   - Lead with finding, not gap justification

2. **Computational Confound Disclosure** (MAJOR-01 Skeptical)
   - Add limitation in Discussion §6.2: "H-M1 LLM @32 sampling vs lean-auto deterministic — tactic budget control not applied, 29.5pp effect may conflate linguistic advantage with computational advantage"

3. **Mock Data Finality** (MAJOR-02 Skeptical)
   - Change Conclusion line 411 from "natural language understanding is the DOMINANT mechanism" to "natural language understanding is the DOMINANT mechanism (provisional finding pending real miniF2F validation)"

### DEFER TO HUMAN (MINOR)

1. DeepSeek 89% → 88.9% (MINOR-01 Accuracy)
2. Abstract closer phrasing (MINOR-01 Bored)
3. Novelty claim qualifier (MINOR-01 Skeptical)
4. Gap calculation 50pp vs 46.7pp (MINOR-02 Skeptical)
5. Depth rejection "provisional" (MINOR-03 Skeptical)

### STRUCTURAL (MAJOR — REQUIRES MANUAL INTERVENTION)

1. **Figure 1 to Introduction** (MAJOR-02 Bored)
   - Move mechanistic attribution diagram from Results to Introduction §2
   - Cannot auto-fix (requires figure regeneration + section restructuring)
   - **DEFER TO HUMAN** with HIGH PRIORITY flag

---

## Next Steps

**Step 03**: Apply Revision R1 (auto-fix 3 MAJOR text issues)  
**Step 04**: Convergence check (expect MAJOR count reduced to 1 — Figure 1 move deferred)  
**Step 05**: If MAJOR > 0, proceed to Adversary R2 (numerical verification)  
**Step 07**: Finalize with remaining MAJOR flagged for human intervention
