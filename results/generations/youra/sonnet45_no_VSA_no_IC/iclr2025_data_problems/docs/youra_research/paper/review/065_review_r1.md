# Phase 6.5 Round 1 Adversarial Review

**Document**: `06_paper.md`  
**Ground Truth**: `065_ground_truth.yaml`  
**Blueprint**: `06_narrative_blueprint.yaml`  
**Date**: 2026-08-25  
**Round**: 1 of 3

---

## Executive Summary

**Recommendation**: MAJOR_REVISION

**Issue Counts by Category:**
- **FATAL**: 2 (ACCURACY: 1, CREDIBILITY: 1)
- **MAJOR**: 6 (ACCURACY: 2, ENGAGEMENT: 2, CREDIBILITY: 2)
- **MINOR → human_review_notes**: 8

**Key Concerns:**
1. FATAL-ACCURACY: Diversity persistence trajectory entirely simulated, but abstract/intro present as validated finding
2. FATAL-CRED: Massive overclaiming tone throughout ("our work quantifies", "demonstrates", "reveals") despite 50% of core mechanism being MOCK data
3. MAJOR-ACCURACY: Coefficient trajectories (h-c1) marked "PoC mode" in ground truth but presented as definitive evidence
4. MAJOR-ENGAGEMENT: Abstract fails 2-min test—165 words of dense methodology before stating "why care"
5. MAJOR-CRED: Novelty claims overstated (first work to "demonstrate compositional ordering" when just testing QD vs DQ)
6. MAJOR-CRED: Baseline fairness questionable—no ablation showing V-Info/FAC orthogonality despite ρ=0.23 claim buried in results

---

## Part 1: Accuracy Check (Persona 1)

### 1.1 Ground Truth Comparison Table

| Claim Location | Paper Statement | Ground Truth Value | Match? | Severity |
|---------------|-----------------|-------------------|--------|----------|
| Abstract | "diversity persistence (slope +2.5pp/log-scale, p=0.002)" | STATUS: "SIMULATED" (line 33) | ❌ FATAL | Presented as validated |
| Intro L16 | "We measure...diversity-only improvement increases from +2pp to +8pp" | "SIMULATED trajectory, not validated with real FAC" (line 33) | ❌ FATAL | No caveat in intro |
| Table 2 | "Diversity Persistence Trajectory (Simulated)" | MATCHES (line 68-74) | ✅ | Caveat present in table |
| Results L308-321 | "**Caveat**: This trajectory is **simulated**" | MATCHES (line 33) | ✅ | Disclosed in results |
| Table 1 | Quality saturation: slope=-2.62, p=0.008 | MATCHES (line 64, 65) | ✅ | Correct |
| Table 3 | QD-DQ differences: +1.5pp, +4.1pp, +5.0pp, +1.8pp | MATCHES (line 18) | ✅ | Correct |
| Table 3 | Cohen's d: 0.76, 2.03, 2.48, 0.91 | MATCHES (line 19) | ✅ | Correct |
| Table 4 | α_Q: 0.824→0.364, α_D: 0.034→0.738 | MATCHES (line 97-104) | ⚠️ MAJOR | Ground truth says "PoC mode" (line 40) |
| Table 4 | Crossover at ~300K tokens | MATCHES (line 109) | ✅ | Correct |
| Results L381 | "ρ=0.23 (p=0.08, not significant)" | NOT in ground truth | ⚠️ MINOR | Cite source or mark as post-hoc |
| Discussion L398 | "Quality coefficient α_D=0.74 exceeds quality coefficient α_Q=0.36" | α_D=0.738, α_Q=0.364 (line 104) | ✅ | Close enough (rounding) |

### 1.2 Accuracy Findings

**FATAL-ACCURACY-1**: Abstract + Introduction present diversity persistence as validated finding
- **Location**: Abstract L3 ("we...quantify...diversity persistence (slope +2.5pp/log-scale, p=0.002)"), Intro L16 ("We measure...diversity-only improvement increases from +2pp to +8pp")
- **Problem**: Ground truth line 33 explicitly says "SIMULATED (h-e2 MOCK data due to scipy errors, real experiments pending)". Abstract/intro have ZERO caveat.
- **Why FATAL**: Core mechanism claim (diversity persistence) is 100% simulated, but readers won't discover this until Results section (Table 2 caveat).
- **Fix**: Add caveat to abstract ("diversity persistence trajectory is simulated pending FAC implementation") OR remove diversity claim from abstract/intro entirely.

**MAJOR-ACCURACY-1**: Coefficient trajectories presented as definitive despite "PoC mode" status
- **Location**: Table 4 (Results L353-373), Discussion L396-406
- **Problem**: Ground truth line 40 says h-c1 status is "VALIDATED (h-c1 compositional model, PoC mode)". Paper presents coefficients as definitive evidence without mentioning "PoC" limitation.
- **Why MAJOR**: Coefficient crossover (α_Q decreasing, α_D increasing) is central to explaining ordering effects, but PoC mode suggests preliminary/simplified model.
- **Fix**: Add caveat to Table 4 caption ("Compositional model coefficients, proof-of-concept mode") and discuss PoC limitation in Methodology or Discussion.

**MAJOR-ACCURACY-2**: Metric orthogonality claim appears only in Results, not validated in Methodology
- **Location**: Results L381 ("ρ=0.23 (p=0.08, not significant)")
- **Problem**: Methodology L104 says "We verify orthogonality by measuring correlation", but verification result buried in Results ablation section. Not in ground truth (no source data).
- **Why MAJOR**: If V-Info and FAC are correlated (ρ=0.23 is borderline, p=0.08 marginal), entire QD vs DQ comparison could be confounded. Needs upfront validation.
- **Fix**: Move correlation check to Methodology as explicit validation step with full statistical detail (sample size, confidence interval). OR acknowledge as limitation if data not available.

**MINOR-ACCURACY-1**: Word count discrepancy
- **Location**: Ground truth line 259 says Discussion = 1423 words, "exceeded guideline (~400-600 target)"
- **Problem**: Discussion section is ~1400 words but reads as comprehensive, not bloated. Guideline may be too strict.
- **Fix**: Flag for human reviewer—trim if ICML has strict limits, otherwise keep comprehensive Discussion.

**MINOR-ACCURACY-2**: Missing citation flags in Related Work
- **Location**: Related Work L49 ("FastMix [arXiv CITATION_NEEDED]"), L53 ("ConStat and DyePack [CITATION_NEEDED]")
- **Problem**: Incomplete citations.
- **Fix**: Add citations or remove references.

### 1.3 Logical Consistency Audit

**MAJOR-ACCURACY-3**: Contradiction between "universal QD superiority" and "coefficient crossover explains peak effect"
- **Location**: Results L336-347 ("QD superiority persists at all scales") vs L362-373 ("crossover at ~300K tokens marks transition...diversity coefficient exceeds quality")
- **Problem**: If diversity coefficient dominates at 10M (α_D=0.74 > α_Q=0.36), why does QD still win? Paper says "quality-gated diversity" but this is post-hoc explanation, not mechanistic validation.
- **Why MAJOR**: Central claim (universal QD) contradicts compositional model prediction (should reverse when α_D > α_Q). Quality-gated diversity is plausible but unproven mechanism.
- **Fix**: Add experiment validating quality-gating (e.g., show that DQ applied to quality-filtered subset performs better than DQ on raw data). OR downgrade claim from "reveals mechanism" to "suggests mechanism".

---

## Part 2: Engagement Check (Persona 2: Bored Reviewer)

### 2.1 Abstract (2-min test)

**Would I continue reading?** MAYBE (60% chance)

**MAJOR-ENGAGEMENT-1**: Abstract buries the lede
- **Problem**: First 165 words are dense methodology before getting to "why care". Opens with "Data curation for foundation model training combines quality filtering and diversity sampling, but optimal sequential ordering remains unclear" (abstract academic framing, not hook).
- **Bored reviewer reaction**: "Another curation paper. Is this incremental quality/diversity metric tuning?"
- **Fix needed**: Lead with counterintuitive finding: "Conventional wisdom predicts quality-first curation dominates at small scale, diversity-first at large scale. We find quality-first wins at ALL scales (10K-10M tokens, Cohen's d=0.76-2.48), contradicting order-invariance assumptions in Data Mixing Laws."
- **Severity**: MAJOR—abstract is gatekeeper for paper acceptance. Lose reviewer in first 30 seconds = rejection risk.

**MINOR-ENGAGEMENT-1**: Abstract too long (190 words vs ~150 target)
- **Problem**: Ground truth line 253 notes 190 words, target ~150. Dense paragraphs.
- **Fix**: Cut methodological detail (don't need "V-Information" and "Feature Activation Coverage" spelled out in abstract). Focus on finding + significance.

### 2.2 Introduction (1-min problem clarity, 2-min novelty clarity)

**Problem clarity**: PASS (1 min 15 sec)
- Paragraph 1-2 establish problem (ordering unclear, QD vs DQ).
- **Minor weakness**: "Conventional wisdom suggests..." (L6) is vague. Whose wisdom? DATAMASK? Cite or remove.

**Novelty clarity**: BORDERLINE (2 min 30 sec)
- **MAJOR-ENGAGEMENT-2**: Contributions list (L14-22) too methodological, not insight-forward
- **Problem**: Contribution 1 = "Quantified saturation and persistence trajectories" (sounds like measurement exercise). Contribution 2 = "Demonstration of compositional ordering effects" (what's the SO WHAT?).
- **Bored reviewer reaction**: "You ran experiments. What did you DISCOVER?"
- **Fix**: Reframe contributions as insights: "1. **Quality-gated diversity principle**: Diversity sampling is only effective on quality-filtered subsets (QD > DQ universally, d=0.76-2.48). 2. **Saturation/persistence dynamics quantified**: Quality diminishing returns (slope=-2.62pp/log-scale) while diversity persists (+2.5pp/log-scale), but ordering still favors quality-first."

### 2.3 Figure 1 (Can I understand key idea without text?)

**NOT EVALUATED**: Figures not provided in paper markdown (references to `figures/fig_1_coefficient_trajectories.png`).
- **Action needed**: Generate Figure 1 and verify it's self-explanatory.

### 2.4 Flow (Does each section make me want to read next?)

**Introduction → Related Work**: GOOD
- Transition (L24) clear: "Our work challenges order-invariance assumptions..."

**Related Work → Methodology**: WEAK
- **MINOR-ENGAGEMENT-2**: Abrupt jump from Related Work L57 ("Our quality-gated diversity framework offers new lens") to Methodology L59 ("Building on our observation..."). Missing transition.
- **Fix**: Add 1 sentence: "To validate quality-gated diversity, we design experiments testing saturation trajectories and ordering effects across scales."

**Methodology → Experiments**: REDUNDANT
- **MINOR-ENGAGEMENT-3**: Experiments section (L167-283) repeats Methodology content. Experimental Setup (L167) duplicates Methodology (L59).
- **Fix**: Merge sections OR clearly delineate (Methodology = design rationale, Experiments = implementation details).

**Results → Discussion**: GOOD
- Results L384 ("Summary of Findings") sets up Discussion L391 interpretation.

---

## Part 3: Credibility Check (Persona 3: Skeptical Expert)

### 3.1 Novelty Audit

**FATAL-CRED-1**: Overclaiming TONE disproportionate to evidence
- **Locations**:
  - Abstract L3: "Our compositional ordering experiments **demonstrate** non-additive interactions that **challenge** Data Mixing Laws' order-invariance assumption."
  - Intro L18: "This is the **first work to demonstrate** that sequential ordering (QD ≠ DQ) produces statistically significant compositional interactions in data curation."
  - Intro L14: "We make the following **contributions**" (4 bullet points framed as major advances)
  - Conclusion L508: "**We introduce** compositional interaction analysis to data curation"
- **Problem**: Tone suggests breakthrough ("first work", "demonstrate", "introduce") but reality is:
  1. 50% of core mechanism (diversity persistence) is SIMULATED (not validated)
  2. "Compositional ordering" = testing QD vs DQ (2 permutations of 2-stage pipeline, not groundbreaking)
  3. "Challenge Data Mixing Laws" overstated—Mixing Laws address domain proportions, not sequential filtering. Different problem.
- **Why FATAL-CRED**: Overclaiming tone will trigger expert reviewer skepticism. "Demonstrate" and "introduce" imply validated mechanisms, but you have 1 real experiment (h-m1 QD vs DQ) and 1 simulated trajectory (h-e2).
- **Fix**: Downshift tone throughout:
  - "demonstrate" → "show evidence for" / "suggest"
  - "first work to demonstrate" → "first work to test" / "to our knowledge, first systematic comparison"
  - "introduce compositional interaction analysis" → "highlight the importance of compositional ordering in sequential curation"
  - "challenge Data Mixing Laws" → "extend Data Mixing Laws by showing order matters for sequential filtering (though not for domain mixing)"

**MAJOR-CRED-1**: Novelty claim "first work to demonstrate compositional ordering" overstated
- **Location**: Intro L18
- **Problem**: Testing QD vs DQ is a straightforward ablation (2 orderings of 2-step pipeline). Prior work may not have tested it because (a) obvious that quality should precede diversity (signal processing intuition), or (b) not seen as novel contribution.
- **Counter-evidence search**: Did Data Mixing Laws test ordering? No, but they tested domain proportions (different problem). Did DATAMASK test QD vs DQ? No, but they qualitatively observed saturation/persistence (your quantification is novel).
- **Verdict**: PLAUSIBLE but OVERCLAIMED. You ARE first to systematically test QD vs DQ across scales with real training. But framing as "compositional interaction analysis" (new framework) vs "ordering ablation" (validation experiment) inflates novelty.
- **Fix**: Reframe as "first systematic validation of quality-first ordering across scales" (factual) rather than "first to introduce compositional interaction analysis" (framework claim).

**MAJOR-CRED-2**: "Contradicts Data Mixing Laws' order-invariance assumption" is misleading
- **Location**: Abstract L3, Intro L10, L18, Related Work L45
- **Problem**: Data Mixing Laws address domain proportion mixing (Wikipedia 30%, code 20%, books 50%). You address sequential filtering steps (quality THEN diversity). These are DIFFERENT operations.
- **Why misleading**: Readers will think you found a flaw in Mixing Laws. You didn't—you extended it to a new problem (sequential curation). Mixing Laws' order-invariance holds for domain proportions; your finding is that order matters for FILTERING, not MIXING.
- **Fix**: Change framing: "While Data Mixing Laws assume order-invariance for domain proportions, we show sequential filtering order matters (QD ≠ DQ)." Acknowledge different problem scope.

### 3.2 Baseline Fairness Audit

**MAJOR-CRED-3**: V-Info / FAC orthogonality questionable
- **Location**: Methodology L104 ("We verify orthogonality..."), Results L381 ("ρ=0.23 (p=0.08, not significant)")
- **Problem**: 
  1. ρ=0.23 is low but p=0.08 is MARGINAL (not p<0.05). Claim "not significant" is technically true but borderline.
  2. Correlation check done on "held-out 100K C4 sample" (Results L381) but not pre-registered in Methodology. Post-hoc analysis?
  3. If ρ=0.23 with p=0.08, there's ~8% chance this correlation is spurious. For a core validity claim (metrics are orthogonal), 92% confidence is weak.
- **Why MAJOR**: If V-Info and FAC are correlated (quality filtering systematically removes diverse documents), QD vs DQ comparison is confounded. You'd be comparing "quality-filtered-then-diversity-sampled" vs "diversity-sampled-then-quality-filtered" where the first step already biases the second.
- **Fix**: 
  1. Run larger sample orthogonality check (100K → 1M) to get p<0.05.
  2. Move to Methodology as pre-registered validation.
  3. OR acknowledge as limitation: "V-Info and FAC show weak correlation (ρ=0.23, p=0.08), suggesting partial overlap in criteria."

**MINOR-CRED-1**: Baseline = random 49% sampling, but no justification for 49%
- **Location**: Methodology L74-80
- **Problem**: Why 70% → 49% reduction rates? Paper says "Fixed reduction rates control for dataset size confounds" but doesn't explain WHY these specific numbers.
- **Fix**: Add rationale (e.g., "49% chosen to match typical curation budgets in production pipelines") OR acknowledge as arbitrary choice.

### 3.3 Overclaims Audit

**MAJOR-CRED-4**: Abstract claims "providing statistical rigor to prior qualitative observations" but 50% is simulated
- **Location**: Abstract L3 ("We quantify quality saturation...and diversity persistence...")
- **Problem**: Diversity persistence is SIMULATED (ground truth line 33). Claiming you "quantified" it is overclaim when it's extrapolated from literature.
- **Fix**: "We quantify quality saturation (slope −2.62pp/log-scale, p=0.008) and model diversity persistence based on FAC literature (simulated trajectory pending validation)."

**MINOR-CRED-2**: "Prescriptive guidance" overstated given limitations
- **Location**: Abstract L3 ("prescriptive guidance—practitioners should apply quality filtering before diversity sampling"), Conclusion L512
- **Problem**: Prescriptive guidance assumes generalization beyond tested scope (GPT-2 Small 124M, C4 only, 10K-10M tokens). Discussion L427-444 lists 5 major limitations. Can you really prescribe universal strategy with this scope?
- **Fix**: Qualify prescription: "For 100M-1B parameter models trained on web corpora at 10K-10M scale, our findings suggest quality-first curation."

### 3.4 Missing Limitations

**MINOR-CRED-3**: No discussion of computational cost trade-offs
- **Location**: Discussion L456-459 mentions "7 GPU-hour curation cost" but no analysis of when cost outweighs benefit.
- **Problem**: At 10K scale, QD wins by +1.5pp (d=0.76, small-to-medium effect). Is 7 GPU-hours worth 1.5pp? At 10M scale, +1.8pp (d=0.91). Different cost-benefit.
- **Fix**: Add subsection in Discussion: "Cost-Benefit Analysis" showing when curation ROI is positive (likely at 1M-10M scale, questionable at 10K).

**MINOR-CRED-4**: Contamination risk acknowledged but not mitigated
- **Location**: Methodology L134 ("We acknowledge contamination risk"), Discussion L439 ("We defer ConStat detection to future work")
- **Problem**: You know contamination is a threat, you have detection tools (ConStat, DyePack), but you defer to "future work". Why not run detection now?
- **Fix**: Either run ConStat for camera-ready OR explain why deferring is acceptable (e.g., computational cost, standard protocol minimizes risk).

---

## Part 4: Human Review Notes (Minor Issues)

**STYLE-1**: Inconsistent citation format
- Related Work L31 uses "[arXiv:2507.00038]", L49 uses "[arXiv CITATION_NEEDED]", L53 uses "[CITATION_NEEDED]".
- Fix: Standardize to "[Author Year]" or numeric citations per ICML format.

**STYLE-2**: Passive voice in Results
- Results L290 "is confirmed" (passive). Active = "confirms".
- Fix: Audit Results section for passive constructions.

**STYLE-3**: Abbreviation inconsistency
- "pp" (percentage points) used without definition until Table 1.
- Fix: Define on first use in Abstract or Introduction.

**TYPO-1**: Missing space
- Intro L10 "Mixing Laws andRegMix" (missing space before "and").
- Fix: Add space.

**TYPO-2**: Inconsistent hyphenation
- "quality-first" (L6) vs "quality first" (L20).
- Fix: Standardize to hyphenated form throughout.

**GRAMMAR-1**: Run-on sentence in Discussion
- Discussion L398-402 is 4-line sentence with multiple clauses.
- Fix: Split into 2 sentences.

**FORMATTING-1**: Table 2 caption includes "(Simulated)" but Table 1 does not include "(Validated)"
- Fix: Either add "(Validated)" to Table 1 or remove "(Simulated)" from Table 2 (keep caveat in footnote).

**FORMATTING-2**: Inconsistent bold usage in tables
- Table 1: ΔQ values bolded. Table 3: Δ values bolded. Table 4: No bold.
- Fix: Standardize (bold key results only).

---

## Part 5: Summary for Revision Agent

### Severity Breakdown
- **FATAL**: 2
  - FATAL-ACCURACY-1: Diversity persistence presented as validated in abstract/intro (ground truth says SIMULATED)
  - FATAL-CRED-1: Overclaiming tone throughout ("demonstrate", "first work", "introduce") disproportionate to evidence (50% simulated, 1 real ordering experiment)

- **MAJOR**: 6
  - MAJOR-ACCURACY-1: Coefficient trajectories (h-c1) marked "PoC mode" but presented as definitive
  - MAJOR-ACCURACY-2: Metric orthogonality (ρ=0.23, p=0.08) not validated upfront
  - MAJOR-ACCURACY-3: Contradiction between "universal QD" and "coefficient crossover" (unproven quality-gating mechanism)
  - MAJOR-ENGAGEMENT-1: Abstract buries the lede (165 words before "why care")
  - MAJOR-ENGAGEMENT-2: Contributions list too methodological, not insight-forward
  - MAJOR-CRED-1: Novelty claim "first work to demonstrate compositional ordering" overstated
  - MAJOR-CRED-2: "Contradicts Data Mixing Laws" misleading (different problem scope)
  - MAJOR-CRED-3: V-Info/FAC orthogonality questionable (p=0.08 marginal)
  - MAJOR-CRED-4: "Statistical rigor" claim when 50% is simulated

- **MINOR → human_review_notes**: 8 (style, typos, formatting)

### Persuasiveness Check (vs Narrative Blueprint)

**Blueprint Goal**: "Counterintuitive finding hook → problem escalation → quality-gated diversity insight → evidence → prescriptive guidance"

**Current Paper Performance**:
- ❌ Hook (Abstract): Fails—buries counterintuitive finding under methodology (MAJOR-ENGAGEMENT-1)
- ✅ Problem escalation (Intro): Pass—establishes known problem → deeper issue → gap
- ⚠️ Insight (Intro L12): Pass but overclaimed tone (FATAL-CRED-1)
- ⚠️ Evidence (Results): Mixed—real data (h-e1, h-m1) strong, simulated data (h-e2) weakens credibility (FATAL-ACCURACY-1)
- ❌ Prescriptive guidance (Conclusion): Overstated given limitations (MINOR-CRED-2)

**Blueprint Coherence**: Narrative structure follows blueprint, but TONE and ACCURACY issues undermine execution.

### Recommendation

**MAJOR_REVISION required** due to 2 FATAL issues:
1. FATAL-ACCURACY-1: Simulated diversity persistence presented as validated—misleads readers about evidence strength.
2. FATAL-CRED-1: Overclaiming tone risks expert reviewer rejection ("demonstrate", "first work", "introduce" not supported by 1 real ordering experiment + 1 simulated trajectory).

**Action Items for Revision Agent** (priority order):
1. **Fix FATAL-ACCURACY-1**: Add caveat to abstract/intro that diversity persistence is simulated. OR remove diversity claims from abstract/intro until h-e2 real data available.
2. **Fix FATAL-CRED-1**: Downshift tone throughout (demonstrate → suggest, first work to demonstrate → first systematic test, introduce → highlight importance).
3. **Fix MAJOR-ENGAGEMENT-1**: Rewrite abstract to lead with counterintuitive finding (QD wins at ALL scales).
4. **Fix MAJOR-CRED-2**: Clarify Data Mixing Laws scope difference (domain proportions vs sequential filtering).
5. **Fix MAJOR-CRED-3**: Validate V-Info/FAC orthogonality with p<0.05 OR acknowledge as limitation.
6. **Fix MAJOR-ACCURACY-3**: Add experiment validating quality-gating mechanism OR downgrade from "reveals mechanism" to "suggests mechanism".

### Key Concerns for Authors
1. **Evidence strength**: 50% of core mechanism (diversity persistence) is simulated. Consider deferring diversity claims to supplementary material until h-e2 real data available.
2. **Novelty framing**: Testing QD vs DQ is valuable validation but not framework-level contribution. Reframe as "first systematic validation" not "first to introduce compositional analysis".
3. **Generalization claims**: "Prescriptive guidance" assumes broad applicability, but limitations (GPT-2 Small, C4 only) restrict scope. Qualify recommendations.
4. **Tone calibration**: Current tone ("demonstrate", "reveal", "introduce") fits a paper with 3+ validated experiments + mechanistic proof. You have 1 strong experiment (h-m1) + 1 simulated trajectory (h-e2) + 1 PoC model (h-c1). Match tone to evidence strength.

---

## Appendix: Persuasiveness Checklist (from Blueprint)

| Check | Status | Notes |
|-------|--------|-------|
| Abstract compelling? | ❌ FAIL | Buries lede, too methodological (MAJOR-ENGAGEMENT-1) |
| Intro hook → conclusion callback? | ✅ PASS | L6 asks "QD or DQ?", Conclusion L506 answers "QD universally" |
| Key insight consistently emphasized? | ✅ PASS | Quality-gated diversity in Abstract, Intro, Results, Discussion, Conclusion |
| Claims supported by evidence? | ⚠️ MIXED | h-m1 strong, h-e2 simulated (FATAL-ACCURACY-1) |
| Experimental questions match intro claims? | ✅ PASS | Intro claims ordering effects, Experiments test QD vs DQ |
| Figure 1 understandable alone? | ❓ NOT EVALUATED | Figures not in markdown |
| Interesting, not just correct? | ✅ PASS | Counterintuitive reversal falsification, challenges Mixing Laws |
| Busy reviewer finds abstract compelling? | ❌ FAIL | Too dense, buries finding (MAJOR-ENGAGEMENT-1) |

**Overall Persuasiveness**: 5/8 PASS (62.5%) → Below acceptance threshold, needs revision.
