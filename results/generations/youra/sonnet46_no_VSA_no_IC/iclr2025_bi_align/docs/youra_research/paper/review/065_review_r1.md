# Adversarial Review — Round 1

**Paper:** Directed Citation Asymmetry in the huashen218 Bidirectional Alignment Corpus: Pipeline Validation and Preliminary Measurement
**Reviewed:** 2026-08-21
**Reviewer:** Adversary Agent (3-Persona)
**Round:** R1 — Accuracy and Engagement

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 0 | CRITICAL |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **1** | **3** | **MAJOR_REVISION** |

**Recommendation:** MAJOR_REVISION (one fatal numerical error must be corrected; three major issues)

---

## Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| Tests passing | 23/23 | 23/23 | ✓ |
| S2AG resolution rate | 67.3% | 67.35% (33/49) | ✓ |
| Scheme 1 coverage | 12.1% (4/33) | 12.12% (4/33) | ✓ |
| Scheme 3 ML_NLP count | 27 | **28** | ✗ MISMATCH |
| Scheme 3 HCI count | 6 | **5** | ✗ MISMATCH |
| Scheme 3 coverage | 100% (33/33) | 100% (33/33) | ✓ |
| ML_NLP→HCI edges | 5 | 5 | ✓ |
| HCI→ML_NLP edges | 4 | 4 | ✓ |
| ML_NLP outgoing total | 47 | 47 | ✓ |
| Citation asymmetry ratio | 0.107 | 0.10638 | ✓ |
| Cross-group edges max | 9 (Scheme 3) | 9 (Scheme 3) | ✓ |
| Coverage gate | 70% | 70% | ✓ |
| Edge gate | 30 | 30 | ✓ |

---

## Part 1: Accuracy Check (Persona 1)

### FATAL Issues — Accuracy

#### FATAL-ACC-001: Scheme 3 ML_NLP/HCI Classification Count Mismatch

**Location:** Section 5.2, Table (Classification Coverage Results)
**Issue:** The paper's Table in Section 5.2 reports Scheme 3 as ML_NLP=27, HCI=6. Ground truth (04_validation.md) reports ML_NLP=28, HCI=5. Total = 33 in both cases, but the distribution is wrong.
**Evidence:**
- Paper Section 5.2 table row: `| **Scheme 3** | **FoS-primary** | **33 / 33** | **100.0%** | **27** | **6** | **0** |`
- 04_validation.md Classification table: `| Scheme3 (FoS-primary) | 28 | 5 | 0 | 33/33 (100%) |`
**Impact:** This is a factual error in a primary result table. If the directed edge matrix is correct (ML_NLP outgoing=47, ML_NLP papers in graph=28), then reporting ML_NLP=27 creates an internal inconsistency. A skeptical reviewer will immediately cross-check the classification counts against the directed edge matrix and find the discrepancy.
**Required Fix:** Correct the Scheme 3 row in the Section 5.2 table to ML_NLP=28, HCI=5.

---

### MAJOR Issues — Accuracy

None identified beyond FATAL-ACC-001.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Specific numbers (12%, 100%, 0.107) work well; "honest failure as discovery" framing is effective |
| Problem clear in 1 min? | ✓ | Intro paragraph 1 delivers: 49 IDs not ~400, asymmetric signal found |
| Novelty clear in 2 min? | ✓ | FoS-primary vs venue string framing is crisp by paragraph 5 of Introduction |
| Figure 1 self-explanatory? | ✓ | Caption describes gate evaluation clearly |
| Would continue reading? | ✓ | Yes |

**Attention Lost At:** Section 6.2 Limitation 4 — formulaic "corpus selection bias" framing is weaker than the rest.

### MAJOR Issues — Engagement

#### MAJOR-ENG-001: Conclusion Says "Three Things" But Paper Has Four Contributions

**Location:** Section 7 (Conclusion), first paragraph
**Issue:** "We contribute three things: a validated S2AG bibliometric pipeline (23/23 unit tests, fully cached), FoS-primary classification achieving 100% vs. 12% label coverage on interdisciplinary alignment corpora, and the first directional citation measurement in the huashen218 corpus."

The Introduction clearly enumerates FOUR numbered contributions (C1–C4). The Conclusion omits C4 (methodological finding on corpus proxy construction / reading list yield). A reviewer who read the Introduction carefully will notice this discrepancy and question whether C4 is a contribution or not.

**Evidence:** Introduction lists C1 (pipeline), C2 (FoS-primary), C3 (citation measurement), C4 (corpus proxy finding). Conclusion lists only C1, C2, C3.
**Reader Impact:** Signals carelessness; creates confusion about what the actual contribution set is.
**Required Fix:** Add C4 to the Conclusion list, changing "three things" to "four contributions" or restructure to include the corpus proxy finding.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| "No prior work has constructed a directed citation graph within the huashen218 corpus" | Section 2.1 | ✓ | Corpus is 2024; plausible |
| FoS-primary classification as a distinct formalizable scheme | Section 2.3 | ✓ | Framed modestly as "a three-line change" — honest |
| "first directional citation measurement" | Section 1, C3 | ✓ | Qualified with "within the huashen218 alignment corpus" — scoped appropriately |

### Baseline Fairness Audit

N/A — this is a pipeline/measurement paper, not a comparative ML paper. No ML baselines to compare.

### FATAL Issues — Credibility

None.

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: Overclaiming Tone — "Striking" Used Three Times for N=9 Edge Result

**Location:** Abstract ("telling a striking story"), Introduction ("told a striking story"), Section 5.3 ("The directional signal is striking")
**Issue:** The word "striking" appears three times to describe a ratio (0.107) based on N=9 cross-group citation edges. The paper itself correctly states this is "not statistically confirmable at this corpus scale." Using "striking" three times for a non-statistically-confirmable preliminary observation inflates the rhetorical weight beyond what the evidence supports. A skeptical reviewer will note this as disproportionate to the N=9 basis.
**Evidence:** The paper correctly hedges elsewhere ("not yet statistically confirmable", "Important caveat: At N=9 cross-group edges, this ratio is not statistically confirmable"), but the word "striking" is used in both the hook and in the results without hedging.
**Impact:** Undermines credibility — the author says "striking" but then immediately says it's not statistically confirmable. Cognitive dissonance for the reader.
**Suggested Fix:** Replace at least two instances of "striking" with "directionally consistent" or "notable" or "preliminary." Keep one instance (in Section 5.3 Interpretation) but pair it with the hedge in the same sentence rather than separating them.

#### MAJOR-CRED-002: N=4 HCI Denominator Not Made Explicit in Ratio Discussion

**Location:** Section 5.3, ratio calculation
**Issue:** The paper states "HCI→ML_NLP proportion = 4/4 = 100%." This 100% is based on N=4 HCI papers that have any within-corpus outgoing citation at all. The denominator "4" is the number of HCI papers with outgoing within-corpus citations, not all 6 HCI papers (some have 0 outgoing edges within corpus). This denominator should be made explicit. A reviewer may ask: "Of the 6 HCI papers, how many had any within-corpus citations at all? If 2 of 6 had zero outgoing corpus edges, then the 100% applies to only 4 of them — is that framing honest?"
**Evidence:** Ground truth shows HCI total = 5 (28+5=33) or per correction 5 HCI papers. Directed edge matrix shows HCI→ML_NLP=4, HCI→HCI=0, HCI outgoing total=4.
**Suggested Fix:** In Section 5.3, add: "Note that 2 of the 6 HCI papers have no within-corpus outgoing citations; the 100% proportion applies to the 4 HCI papers with at least one within-corpus reference." (Adjust numbers if HCI=5 per ground truth correction.)

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Section 3.4, formula | `$r = ...` formula renders as display math; ensure consistent LaTeX rendering in ICML format | formatting |
| Section 6.2 Limitation 4 | "Corpus selection bias is fundamental" — slightly vague opening phrase | clarity |
| Abstract, sentence 2 | "Whether these communities actually cite each other's alignment work — and symmetrically — is an open empirical question" — the dash construction is slightly awkward | style |
| Section 5.3 | "No falsifier was triggered; full statistical testing requires the augmented corpus (h-e1-v2)." — parenthetical "(h-e1-v2)" may confuse readers unfamiliar with internal naming | clarity |

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-ACC-001:** Fix Scheme 3 classification count (ML_NLP: 27→28, HCI: 6→5) in Section 5.2 table — MUST FIX
2. **MAJOR-ENG-001:** Change "three things" to "four contributions" in Conclusion and add C4 — MUST FIX
3. **MAJOR-CRED-001:** Reduce "striking" to at most one instance, replace others with "directionally consistent" or similar — SHOULD FIX
4. **MAJOR-CRED-002:** Add explicit N=4 denominator note in Section 5.3 ratio discussion — SHOULD FIX

### Key Concerns

- Classification count table (Section 5.2) contradicts ground truth and will be caught by any careful reviewer cross-checking with the directed edge matrix.
- "Three things" vs. four enumerated contributions is an obvious internal inconsistency that undermines professionalism.
- Repeated use of "striking" for N=9 data without hedging creates credibility gap despite good hedging elsewhere.

### What's Working

- Abstract hook is excellent — "honest failure as discovery" with concrete numbers.
- INCONCLUSIVE framing is consistent and honest throughout.
- Limitations section is thorough (5 well-scoped limitations).
- Related Work is appropriate and correctly scoped.
- Ratio calculation (0.107) and directed edge matrix are internally consistent (even though classification count has an error).
- h-e1-v2 future work is concrete and implementable.
