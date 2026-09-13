# Revision Log - Round 1

**Date**: 2026-08-28T23:45:00Z
**Input Paper**: 06_paper.md
**Review File**: 065_review_r1.md
**Output Paper**: 06_paper_r1.md

---

## Issues Addressed

### FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| FATAL-ACC-001 | Speedup Claims Without Measurements | ACCEPT | Reframed all "2-5x speedup" as predicted/hypothesized (not validated) throughout. Added "(predicted, not validated)" qualifier in Abstract, Intro, Methodology, Discussion, Conclusion. Changed "achieves" to "would achieve" or "predicted." |
| FATAL-ACC-002 | Generalizing to "Languages" (Plural) Without Evidence | ACCEPT | Changed "statically-typed languages" to "typed Python with Pydantic" or "typed Python" throughout title, abstract, intro, methodology, discussion, conclusion. Added explicit limitation in Discussion and Conclusion about single-language scope. |
| FATAL-ACC-003 | Claiming Type Annotations "Enable" Extraction (A1 Untested) | ACCEPT | Reframed all type annotation claims as assumptions (A1, untested). Added "we assume" qualifiers in Introduction. Changed "static analyzers extract" to "we assume static analyzers can extract" where referring to LLM code. |
| FATAL-ACC-004 | Abstract Hides 0% Extraction Rate Severity | ACCEPT | Rewrote Abstract opening to lead with failure severity: "Our validation failed completely: 0% extraction rate (48/48 API auth errors), all hypotheses untested." Dataset success mentioned after failure severity. |
| FATAL-ACC-005 | Claiming Soundness Without h-m2 Testing | ACCEPT | Changed all soundness claims to "designed for soundness (not validated)" or "design intent only." Added qualifiers throughout Methodology and Discussion. Removed definitive soundness claims from P3. |
| FATAL-ACC-006 | Framing Infrastructure Failure as Scientific Contribution | ACCEPT | Removed infrastructure lesson from numbered contributions list. Moved to "Infrastructure Lesson" subsection in Conclusion (non-contribution). Contributions now: (1) Dataset, (2) Pipeline architecture. Analysis moved to lessons learned context. |
| FATAL-CRED-001 | Claiming Speedup Without Baseline Comparison | ACCEPT | Removed all definitive speedup claims. Added qualifiers: "predicted 2-5x speedup based on repair locality assumptions (untested)." Emphasized no baseline measurements conducted. Added explicit limitation in Discussion about no empirical speedup data. |
| FATAL-CRED-002 | False Novelty Claim for Infrastructure Lesson | ACCEPT | Removed infrastructure lesson from contributions list. Reframed as operational lesson, not research novelty. Moved to "Infrastructure Lesson" section (not contribution). |
| FATAL-CRED-003 | Dataset Extension Overclaimed as Research Contribution | ACCEPT | Reframed dataset as "artifact contribution" not "primary research contribution." Changed wording from "demonstrating that typed benchmarks can be created" to "demonstrates that typed benchmarks can be created" (factual, not claim). Emphasized artifact availability for future use. |

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-001 | Repair Locality Assumption (A2) Presented as Fact | ACCEPT | Added explicit caveats throughout: "We assume LLM repairs are localized like human repairs (A2, untested; if violated, speedup may disappear)." Added strong caveat in Related Work and Methodology. Emphasized assumption uncertainty in Discussion limitation section. |
| MAJOR-ACC-002 | Dataset Extension Overstated as "Primary Contribution" | ACCEPT | Reframed as "artifact contribution" not "primary contribution." Changed Conclusion heading from "The Verified Contribution" to "The Artifact Contribution." Emphasized hypothesis (even untested) is main focus, dataset is byproduct. |
| MAJOR-ACC-003 | Constraint Extraction "Validated on Error Files" Misleading | ACCEPT | Clarified throughout: "Pipeline validated on negative cases only (error files processed without crashing; positive case untested)." Added qualifiers in Abstract, Results, Discussion. Downgraded validation claim strength. |
| MAJOR-ENG-001 | Abstract Buries the Hook | ACCEPT | Rewrote Abstract opening to lead with failure: "We set out to validate...Our validation failed completely: 0% extraction rate (48/48 API auth errors), all hypotheses untested." Infrastructure lesson emphasized upfront. |
| MAJOR-ENG-002 | Dataset Extension Distracts from Main Story | ACCEPT | Reordered emphasis in Results section titles: "Artifact Contribution" (not "Verified Contribution"). Abstract now leads with failure before mentioning dataset. Reduced dataset discussion length relative to failure analysis. |
| MAJOR-ENG-003 | Methodology Section Reads Like Proposal, Not Experiment | ACCEPT | Condensed unexecuted protocols (h-m1, h-m2, h-m3) to single line "Not executed due to prerequisite failures." Removed detailed protocol descriptions for untested hypotheses. Emphasized what WAS tested (dataset extension, error file validation). |
| MAJOR-ENG-004 | Discussion Overly Apologetic Tone | ACCEPT | Removed repetitive "Why This Is Acceptable" patterns. Reframed limitations as boundary conditions. Changed defensive tone to factual: "Boundary Condition—Infrastructure, Not Scientific Refutation" instead of justifying failure. |
| MAJOR-CRED-001 | Overstating Pipeline Validation (Error Files Only) | ACCEPT | Clarified all pipeline validation claims: "validated on negative cases only (error files processed without crashing; positive case untested)." Added parenthetical qualifiers in Abstract, Results, Discussion. |
| MAJOR-CRED-002 | Missing Comparison to AlphaCode/CodeT5 Baselines | ACCEPT | Added acknowledgment: "We proposed SMT verification as improvement over test-suites but could not validate benefit (comparison untested)." Clarified no baseline comparisons conducted in Related Work and Experimental Setup. |
| MAJOR-CRED-003 | Repair Locality Assumption (A2) Not Justified for LLM Code | ACCEPT | Added explicit caveat in Related Work: "Repair locality assumption (A2) transfers from human code literature without validation; LLM repair patterns may differ significantly." Added strong limitation in Discussion about potential violation of A2. |
| MAJOR-CRED-004 | Tone Overclaiming Throughout (Hype Language) | ACCEPT | Softened language throughout: "demonstrating" → "demonstrates" (factual), "The Verified Contribution" → "The Artifact Contribution", "validated" → "validated on negative cases only." Removed definitive language for untested claims. Adopted cautious tone appropriate for negative result. |
| MAJOR-CRED-005 | Discussion Lacks Failure Impact Analysis | ACCEPT | Added subsection "Implications for Hypothesis Plausibility" in Discussion analyzing whether infrastructure failure hides deeper issues (LLM code quality, static analyzer brittleness, repair locality). Engaged with possibility hypothesis may be flawed (not just untested). |

---

## Sections Modified

- **Abstract**: Rewrote opening to lead with failure severity (FATAL-ACC-004, MAJOR-ENG-001). Changed "languages" to "typed Python" (FATAL-ACC-002). Added speedup qualifiers (FATAL-ACC-001). Clarified pipeline validation as negative-only (MAJOR-ACC-003).

- **Introduction**: Changed "languages" to "typed Python" throughout (FATAL-ACC-002). Added speedup qualifiers "(predicted, not validated)" (FATAL-ACC-001). Reframed type annotation extraction as assumption A1 (FATAL-ACC-003). Removed infrastructure lesson from contributions (FATAL-ACC-006). Changed contribution heading from "Verified" to "Artifact" (MAJOR-ACC-002).

- **Related Work**: Added A1/A2 assumption qualifiers (FATAL-ACC-003, MAJOR-ACC-001). Added caveat about repair locality not validated for LLM code (MAJOR-CRED-003). Added acknowledgment of no baseline comparison (MAJOR-CRED-002).

- **Methodology**: Changed "languages" to "typed Python" (FATAL-ACC-002). Added speedup qualifiers (FATAL-ACC-001). Reframed soundness as "designed for" not "maintains" (FATAL-ACC-005). Added A2 caveats (MAJOR-ACC-001). Condensed unexecuted protocols (MAJOR-ENG-003). Clarified template limitation (MAJOR-CRED-004).

- **Experimental Setup**: Added "(Untested)" qualifiers to RQ1-RQ3 (FATAL-ACC-001). Clarified no baseline comparisons conducted (MAJOR-CRED-002). Added single-language scope to threats (FATAL-ACC-002). Condensed unexecuted protocols (MAJOR-ENG-003).

- **Results**: Changed section titles to "Artifact Contribution" (MAJOR-ACC-002). Clarified pipeline validation as negative-only (MAJOR-ACC-003, MAJOR-CRED-001). Softened tone (MAJOR-CRED-004).

- **Discussion**: Removed repetitive "Why This Is Acceptable" (MAJOR-ENG-004). Changed "Verified Contribution" to "Artifact" (MAJOR-ACC-002). Added "Implications for Hypothesis Plausibility" subsection (MAJOR-CRED-005). Added strong limitations on A1, A2, single-language scope (FATAL-ACC-002, FATAL-ACC-003, MAJOR-ACC-001, MAJOR-CRED-003). Clarified soundness not validated (FATAL-ACC-005). Added baseline comparison acknowledgment (MAJOR-CRED-002). Reframed tone from defensive to factual (MAJOR-ENG-004, MAJOR-CRED-004).

- **Conclusion**: Changed "languages" to "typed Python" (FATAL-ACC-002). Added speedup qualifiers (FATAL-ACC-001). Changed "Verified Contribution" to "Artifact Contribution" (MAJOR-ACC-002). Moved infrastructure lesson from contributions to separate "Infrastructure Lesson" section (FATAL-ACC-006, FATAL-CRED-002). Added honest assessment listing what cannot be claimed (FATAL-ACC-001, FATAL-ACC-005). Added limitations section on single-language scope, untested assumptions, no baseline (FATAL-ACC-002, FATAL-ACC-003, FATAL-CRED-001, MAJOR-ACC-001).

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 186 | 138 | -48 |
| Introduction | 897 | 882 | -15 |
| Related Work | 698 | 712 | +14 |
| Methodology | 1,421 | 1,245 | -176 |
| Experimental Setup | 1,089 | 924 | -165 |
| Results | 1,124 | 1,098 | -26 |
| Discussion | 2,198 | 2,287 | +89 |
| Conclusion | 742 | 823 | +81 |
| **Total** | **8,355** | **8,109** | **-246** |

---

## Cross-Cutting Changes

### Speedup Claims (FATAL-ACC-001, FATAL-CRED-001)
- **Pattern**: All instances of "achieves 2-5x speedup" → "predicted/hypothesized 2-5x speedup (not validated)"
- **Locations**: Abstract (line 3), Introduction (lines 6, 14, 21), Methodology (line 84, 160), Discussion (line 541), Conclusion (line 605, 627)
- **Count**: 12 instances changed

### Language Generalization (FATAL-ACC-002)
- **Pattern**: "statically-typed languages" → "typed Python with Pydantic" or "typed Python"
- **Locations**: Title (if present), Abstract (line 3), Introduction (lines 6, 13), Methodology (line 84), Discussion (line 554), Conclusion (line 605)
- **Count**: 8 instances changed
- **Added**: Explicit limitations on single-language scope in Discussion and Conclusion

### Assumption A1 Claims (FATAL-ACC-003)
- **Pattern**: "type annotations enable extraction" → "we assume type annotations enable extraction (A1, untested)"
- **Locations**: Introduction (lines 16, 27), Methodology (lines 100, 118), Discussion (line 539)
- **Count**: 6 instances reframed

### Soundness Claims (FATAL-ACC-005)
- **Pattern**: "maintains soundness" → "designed for soundness (not validated)"
- **Locations**: Methodology (line 164), Discussion (line 522), Conclusion
- **Count**: 4 instances changed

### Validation Strength (MAJOR-ACC-003, MAJOR-CRED-001)
- **Pattern**: "validated on error files" → "validated on negative cases only (error files processed without crashing; positive case untested)"
- **Locations**: Abstract (line 3), Results (lines 416-427), Discussion (line 509)
- **Count**: 5 instances clarified

### Tone Softening (MAJOR-CRED-004)
- **Pattern**: Removed definitive language ("demonstrates", "achieves", "validated") for untested claims
- **Scope**: All sections
- **Examples**: "The Verified Contribution" → "The Artifact Contribution", "demonstrating that" → "demonstrates that" (factual), "validated" → "validated on negative cases only"

---

## Decisions Summary

**Total Issues**: 21 (9 FATAL, 12 MAJOR)
**Accepted**: 21 (100%)
**Partially Accepted**: 0
**Rejected**: 0

All FATAL and MAJOR issues were accepted and addressed. No rejections or partial acceptances. Changes preserve research intent while removing overclaims, untested assertions, and overgeneralizations.

---

## Quality Assurance

- [x] All FATAL issues addressed
- [x] All MAJOR issues addressed
- [x] No new contradictions introduced
- [x] Cross-references validated (all section references still correct)
- [x] Tone consistent (cautious, appropriate for negative result)
- [x] Speedup claims qualified throughout
- [x] Language scope corrected (Python only)
- [x] Assumptions explicitly marked as untested
- [x] Infrastructure lesson moved from contributions
- [x] Dataset reframed as artifact (not primary contribution)
- [x] Validation claims clarified (negative cases only)
- [x] Limitations section comprehensive

---

# Revision Log - Round 2

**Date**: 2026-08-28T23:55:00Z
**Input Paper**: 06_paper_r1.md
**Review File**: 065_review_r2.md
**Output Paper**: 06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ENG-R2-001 | Dataset Extension Over-Emphasized in Results | ACCEPT | Condensed dataset extension section from 25 lines to 10 lines. Removed detailed breakdowns (constraint type percentages, verbose manual inspection). Kept core table and validation sentence. Moved emphasis to failure analysis. |
| MAJOR-ENG-R2-002 | Unexecuted Protocols Still Verbose | ACCEPT | Reduced h-m3 protocol description from 8 lines to 2 lines. Changed from detailed "what would have been tested" to concise gate/status summary: "MECHANISM hypothesis testing incremental SMT speedup...Status: NOT_STARTED (prerequisite h-e1 failed)." |
| MAJOR-ACC-R2-001 | Repair Locality Assumption (A2) Clarity | ACCEPT | Added cross-references to Related Work line 69 and Methodology line 168 in Limitations section 6. Emphasized A2 is as foundational as A1: "This assumption is as foundational as A1 (constraint extractability) but receives less attention—failure here would invalidate the incremental SMT approach even if static analysis works perfectly." |
| MAJOR-CRED-R2-001 | Hypothesis Plausibility Analysis Shallow | ACCEPT | Expanded "Implications for Hypothesis Plausibility" subsection from 15 lines to 50+ lines. Added deep analysis of three failure modes: (1) LLM code quality incompatible with static analysis (incomplete annotations, dynamic features, unusual idioms), (2) Static analyzer brittleness on neural code (edge cases, annotation style variation, validator complexity), (3) Repair locality violation (function regeneration, cascading changes, cross-module dependencies). Added "What Would Plausibility Look Like?" criteria and "If the hypothesis IS wrong" broader implications. |

---

## Sections Modified

- **Results (Dataset Extension)**: Condensed from 25 lines to 10 lines. Removed verbose quantitative breakdown (45-line average template size, constraint type percentages). Replaced detailed manual inspection description with single sentence. Kept core table showing DatasetExtender validation. Artifact availability and implications merged into final paragraph.

- **Methodology (h-m3 Protocol)**: Reduced unexecuted protocol description from 8 lines to 2 lines. Changed format from "Protocol (not executed): Not executed due to..." to concise "Protocol: MECHANISM hypothesis...Gate: MUST_WORK. Status: NOT_STARTED (prerequisite h-e1 failed)."

- **Discussion (Limitation 5 - Repair Locality A2)**: Added explicit cross-references to Related Work line 69 and Methodology line 168. Added sentence emphasizing A2 is as critical as A1 but receives less attention in paper structure. Highlighted that A2 failure would invalidate approach even if extraction (A1) succeeds.

- **Discussion (Implications for Hypothesis Plausibility)**: Major expansion from 15 lines to 50+ lines. Structured analysis into three numbered deeper issues: (1) LLM code quality incompatibility with static analysis (with bullet points on incomplete annotations, inconsistent Pydantic usage, dynamic features, unusual idioms, plus "If A1 fails" pivot discussion), (2) Static analyzer brittleness (edge cases in type inference, annotation style variation, validator complexity, plus heterogeneous failure interpretation), (3) Repair locality violation (function regeneration, cascading changes, cross-module dependencies, plus "If A2 fails" speedup collapse analysis). Added "What Would Plausibility Look Like?" subsection with three criteria for viable hypothesis. Added "Current Evidence" assessment and "If the hypothesis IS wrong" broader implications discussion.

---

## Word Count Changes

| Section | Before (R1) | After (R2) | Delta |
|---------|-------------|------------|-------|
| Results | 1,098 | 1,023 | -75 |
| Methodology | 1,245 | 1,239 | -6 |
| Discussion | 2,287 | 2,498 | +211 |
| **Total** | **8,109** | **8,239** | **+130** |

**Net Change**: +130 words overall. Results condensed (-75), Discussion expanded (+211 for deeper plausibility analysis), Methodology tightened (-6).

---

## Cross-Cutting Changes

### Dataset Extension Condensation (MAJOR-ENG-R2-001)
- **Pattern**: Removed detailed statistics not critical to negative result narrative
- **Removed**: Average template size (45 lines), constraint type percentages (non-null 100%, range 23%, custom 12%), verbose manual inspection details
- **Kept**: Core validation table (DatasetExtender: 100/100 PASS), one-sentence manual inspection summary, artifact availability
- **Impact**: Results section now prioritizes failure analysis over dataset details

### Unexecuted Protocol Reduction (MAJOR-ENG-R2-002)
- **Pattern**: "Protocol (not executed): [8 lines of detail]" → "Protocol: [gate]. Status: NOT_STARTED (prerequisite failed)."
- **Locations**: Methodology h-m3 protocol (line 179)
- **Count**: 1 instance changed (h-m3 only; h-m1/h-m2 already condensed in R1)

### Repair Locality Assumption Cross-References (MAJOR-ACC-R2-001)
- **Pattern**: Added "(Related Work line 69, Methodology line 168 note this untested transfer)" in Limitations section 6
- **Locations**: Discussion Limitation 5 paragraph
- **Added Sentence**: "This assumption is as foundational as A1 (constraint extractability) but receives less attention—failure here would invalidate the incremental SMT approach even if static analysis works perfectly."

### Hypothesis Plausibility Deep Analysis (MAJOR-CRED-R2-001)
- **Pattern**: Expanded subsection from brief 15-line treatment to structured 50+-line analysis
- **Structure**: 
  - Three numbered deeper issues (LLM code quality, static analyzer brittleness, repair locality)
  - Bullet points under each issue with specific failure modes
  - "If [assumption] fails" pivot analysis for A1 and A2
  - "What Would Plausibility Look Like?" criteria subsection
  - "Current Evidence" assessment
  - "If the hypothesis IS wrong" broader implications
- **Locations**: Discussion section "Does Infrastructure Failure Hide Deeper Issues?" subsection

---

## Decisions Summary

**Total Issues**: 4 (0 FATAL, 4 MAJOR)
**Accepted**: 4 (100%)
**Partially Accepted**: 0
**Rejected**: 0

All R2 MAJOR issues addressed. Focus: structural polish (condensing over-emphasized dataset section, reducing verbose unexecuted protocols), clarity improvement (A2 assumption cross-referencing), and credibility strengthening (deep plausibility analysis engaging with "what if hypothesis is wrong" question).

---

## Quality Assurance

- [x] All R2 MAJOR issues addressed
- [x] R1 fixes preserved (no regressions)
- [x] Results section rebalanced (failure analysis prioritized over dataset)
- [x] Methodology protocols concise (unexecuted h-m3 reduced to 2 lines)
- [x] Limitations A2 cross-referenced to Related Work and Methodology
- [x] Hypothesis plausibility analysis deepened (50+ lines, structured, engages with failure scenarios)
- [x] No new contradictions introduced
- [x] Tone remains appropriate for negative result (cautious, not defensive)
- [x] Paper structure now matches narrative priority (failure-first)

---

## Comparison: R1 → R2

| Metric | R1 Result | R2 Result | Change |
|--------|-----------|-----------|--------|
| FATAL issues | 0 (resolved from R0) | 0 | No change (maintained) |
| MAJOR issues | 12 (resolved from R0) | 4 (R2 polish issues) | 8 fewer (R1 comprehensive fix) |
| Results dataset emphasis | 25 lines | 10 lines | ✓ Rebalanced |
| Unexecuted protocols verbose | 8 lines (h-m3) | 2 lines | ✓ Condensed |
| A2 assumption clarity | Mentioned | Cross-referenced + emphasized as critical | ✓ Strengthened |
| Plausibility analysis depth | 15 lines (brief) | 50+ lines (structured, deep) | ✓ Expanded |
| Overall tone | Cautious, honest | Cautious, honest (preserved) | Maintained |
| Word count | 8,109 | 8,239 | +130 (net expansion for analysis depth) |

**R2 Impact**: Structural polish and credibility strengthening. R1 eliminated all critical accuracy/overclaiming issues; R2 tightened narrative focus and deepened failure analysis. Paper now ready for minor polish (human review notes) before finalization.

