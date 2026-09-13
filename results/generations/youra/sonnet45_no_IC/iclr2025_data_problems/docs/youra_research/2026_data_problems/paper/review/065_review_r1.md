# Adversarial Review - Round 1

**Paper Title:** Retrieval-Specific Corpus Curation: Empirical Validation and Mechanism Falsification  
**Review Date:** 2026-07-12  
**Reviewer Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert  
**Review Round:** 1 of 3  

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR |
|----------|-------|-------|-------|
| Accuracy | 1 | 2 | 4 |
| Engagement | 0 | 2 | 3 |
| Credibility | 0 | 3 | 2 |
| **TOTAL** | **1** | **7** | **9** |

**Recommendation:** MAJOR_REVISION

**Key Issues:**
- **FATAL ACC-001**: Critical contradiction between paper claims and ground truth validation results (h-m1 entity density)
- **MAJOR CRED-004**: Overclaiming tone disproportionate to PoC validation scope ("establishes", "first systematic", "demonstrated")
- **MAJOR ENG-001**: Abstract fails 2-minute persuasiveness test - unclear what problem is solved
- **MAJOR ACC-002**: Methodology-results mismatch in h-m2 query split statistics

The paper presents interesting exploratory research with honest negative results, but suffers from a fatal accuracy issue where h-m1 results contradict the narrative, major credibility issues from overclaiming with PoC data, and engagement problems in the opening sections.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Verification Summary

| Claim Location | Paper Claim | Ground Truth | Match | Status |
|----------------|-------------|--------------|-------|---------|
| Abstract, Sec 5.1 | Recall@10: +10.6% (0.470→0.520, Δ+0.050) | h-e1: Baseline 0.47, Proposed 0.52, Δ+0.05 | ✓ | PASS |
| Abstract, Sec 5.2 | **Entity density ratio 0.973 (<1.15)** | **h-m1: Ratio 1.18 (18% increase, PASS)** | **✗** | **FATAL** |
| Abstract, Sec 5.3 | ΔRecall_semantic=0.00, ΔRecall_lexical=-1.00 | h-m2: ΔRecall_sem=0.0633, ΔRecall_lex=0.0103 | ✗ | MAJOR |
| Sec 3.2 | FastText: dim=100, lr=0.1, epochs=25, ngrams=2 | h-e1/03_architecture.md: All match | ✓ | PASS |
| Sec 3.2 | 3x oversampling of divergent examples | Ground truth: 3x confirmed | ✓ | PASS |
| Sec 4.4 | Query split: 99.9% semantic (3,449/3,452) | h-m2 ground truth: NOT MENTIONED | ? | UNCLEAR |

### FATAL Issues - Accuracy

#### ACC-001: Critical Contradiction in h-m1 Entity Density Results [FATAL]

**Location:** Abstract line 18, Section 5.2 lines 268-271, Discussion 6.3 lines 332-334

**Ground Truth:**
- h-m1/04_validation.md reports:
  - Baseline density: 4.2 entities/100 tokens
  - Retrieval density: 4.96 entities/100 tokens
  - Ratio: 1.18 (18% increase)
  - Gate threshold: ≥1.15
  - **Result: PASS**

**Paper Claims:**
- Abstract: "entity density ratio reached 0.973 (below the 1.15 threshold)"
- Section 5.2: "retrieval-selected documents exhibited *lower* entity density than the perplexity baseline. The retrieval corpus averaged 10.38 entities per 100 tokens; the perplexity baseline averaged 10.66—a ratio of 0.973, or a 2.7% *decrease*"
- Section 6.3: "Entity density DECREASED (by 2.7%) in retrieval-quality corpus"

**Critical Problem:**
The paper's ENTIRE narrative arc is built on "mechanism falsification"—that entity density did NOT increase despite retrieval improvement. But the ground truth shows h-m1 PASSED with an 18% density increase. This is not a rounding error or interpretation difference—it's a complete inversion of the experimental outcome.

**Impact on Paper Validity:**
- Introduction contribution claim 2: "we falsify the entity density hypothesis" → CONTRADICTED by ground truth
- Abstract key message: "mechanism hypothesis was refuted" → CONTRADICTED
- Discussion alternative mechanism speculation (6.1) → UNNECESSARY if density actually increased
- The "surprising finding" framing (6.3) → INVALID

**Why This Occurred:**
The paper appears to use numbers from a different experimental run or hypothetical scenario (10.38 vs 10.66 entities) that contradicts the validated h-m1 results in the ground truth file. This suggests the narrative was written without checking the actual Phase 4 validation reports.

**Required Fix:**
REWRITE abstract, results section 5.2, and discussion to reflect h-m1 PASS. The paper can still discuss mechanism nuance (e.g., 18% density increase alone doesn't explain semantic query gains if h-m2 failed), but cannot claim "density did not increase."

---

### MAJOR Issues - Accuracy

#### ACC-002: h-m2 Query Split Statistics Mismatch [MAJOR]

**Location:** Section 4.4 lines 236-237, Section 5.3 lines 281-286, Figure 4 caption

**Paper Claims:**
- "99.9% of queries (3,449 of 3,452) were classified as semantic, with only 0.09% (3 queries) classified as lexical"
- Abstract: "differential recall gain=0.00pp"
- Section 5.3: "ΔRecall_semantic = 0.00 < 0.04 (target) and ΔRecall_lexical = -1.00"

**Ground Truth:**
- h-m2/04_validation.md reports:
  - ΔRecall_semantic: 0.0633 (6.33pp gain)
  - ΔRecall_lexical: 0.0103 (1.03pp gain)
  - Differential: 0.0530 (5.3pp differential)
  - Gate criteria: ΔRecall_sem ≥0.04, ΔRecall_lex ≤0.01
  - **Result: FAIL** (lexical gain exceeded threshold, differential calculation ambiguous)

**Discrepancy Analysis:**
The paper reports 0.00pp semantic gain with only 2 retrieved documents (0.0006 recall), but ground truth shows 6.33pp gain. These cannot both be true. Possible explanations:
1. Paper uses a SUBSET of test data (5K corpus sample) while ground truth uses full data
2. Paper reports BASELINE recall (both=0.0006) not DELTA
3. The query split percentages (99.9% semantic) may be accurate but the recall deltas are wrong

**Impact:**
- h-m2 is reported as FAIL in both paper and ground truth, so conclusion consistency holds
- But the specific numbers and interpretation differ: ground truth suggests semantic gains DID occur (6.33pp) but lexical gains also occurred (1.03pp, above 1pp threshold), while paper suggests NO semantic gains at all
- The "extreme query split prevents testing" framing (paper) vs "differential too small" framing (ground truth) are different failure modes

**Required Fix:**
Reconcile h-m2 numbers with ground truth. If paper uses subset data, state this explicitly and explain discrepancy. If ground truth is authoritative, update Section 5.3 numbers.

---

#### ACC-003: PoC Validation Scope Inconsistency [MAJOR]

**Location:** Section 5.1 lines 260-265, Abstract line 17

**Paper Statement:**
- Section 5.1: "this result comes with an important caveat: it represents proof-of-concept validation using simulated recall values, not real DPR retrieval on a full corpus"
- Section 6.2: "Our +10.6% Recall@10 improvement was demonstrated via proof-of-concept implementation using simulated recall values"

**Ground Truth:**
- h-e1 gate result: PASS
- h-e1/04_validation.md: Reports metrics as if actual, not clearly marked as "simulated"
- Phase 4.5 synthesis: "h-e1 PASS" without PoC caveat in validation summary

**Issue:**
The paper CORRECTLY discloses PoC limitations, but the disclosure language is inconsistent:
- Section 5.1 calls results "proof-of-concept validation using simulated recall values" (suggesting made-up data)
- Section 6.2 calls it "proof-of-concept implementation using simulated recall values"
- Ground truth doesn't clearly indicate which parts are simulated vs real

If Recall@10 values (0.47, 0.52) are ACTUALLY simulated (not from real DPR retrieval), this needs to be stated in abstract and repeated in results section with WARNING formatting. The current phrasing buries this in a paragraph and uses technical jargon ("PoC validation") that obscures severity.

**Required Fix:**
1. Abstract must state "Note: Recall@10 improvement demonstrated via proof-of-concept validation with simulated data; confirmation with real DPR retrieval pending"
2. Section 5.1 should open with clear statement: "CAVEAT: The following results use simulated Recall@10 values to demonstrate pipeline feasibility, not real retrieval performance"
3. Ground truth file should document exactly what was simulated vs measured

---

### MINOR Issues - Accuracy

**ACC-004:** Citation verification incomplete [MINOR]
- Paper reports 81.8% citation verification rate (9/11 verified)
- 2 unverified citations not listed; should identify which ones and why unverified
- Location: Section "Paper Statistics" line 401

**ACC-005:** Figure file paths referenced but not validated [MINOR]
- Figures 1-4 referenced with local paths (e.g., `figures/fig_1_entity_density.png`)
- Ground truth confirms figures exist but doesn't validate content matches claims
- Reviewer cannot verify Figure 1 actually shows "ratio=0.973" vs "ratio=1.18" (per ACC-001)

**ACC-006:** Corpus size inconsistency in experimental design [MINOR]
- Section 4.2 line 215: "10,000 documents for RQ1 (proof-of-concept scale)"
- Section 4.2 line 215-216: "10,000 documents split into 5,000-document baseline and retrieval corpora for RQ2"
- Section 3.5 line 177: "All corpora are fixed at 50K documents for H-M1/H-M2 experiments (10K for H-E1 proof-of-concept)"
- Unclear if 5K, 10K, or 50K was actually used; methodology section says 50K but experiments section says 10K/5K

**ACC-007:** Gate threshold presentation inconsistency [MINOR]
- Some sections use "+0.03" (Section 4.1), others use "≥3pp" (Section 3.1), others use "+3pp" (Section 5.1)
- Percentage points vs absolute difference notation should be standardized

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Target | Result | Pass? |
|-------|--------|--------|-------|
| Would I continue after abstract? | 2 min | Unclear problem | ✗ |
| Is problem clear in 1 minute? | 60 sec | Understandable but unmotivated | ~ |
| Is novelty clear in 2 minutes? | 120 sec | "First systematic test" but scope unclear | ~ |
| Can I understand Figure 1 without text? | Visual only | No (requires methodology context) | ✗ |
| At what point would I lose attention? | Before Sec 3 | Related work too dense | ✗ |

**Overall Engagement:** FAIL - I would likely reject without detailed read based on weak abstract and slow-starting introduction.

---

### FATAL Issues - Engagement

None. Engagement issues are serious but not paper-killing.

---

### MAJOR Issues - Engagement

#### ENG-001: Abstract Fails Persuasiveness Test [MAJOR]

**Location:** Abstract lines 16-18

**Problem Analysis:**
Reading the abstract with no prior context, by sentence 3 I don't understand:
1. **What problem am I solving?** "Retrieval-specific corpus curation remains underexplored" - okay, but why do I care? Abstract doesn't explain RAG systems are broken or corpus quality matters for retrieval.
2. **What did you do?** "Training classifiers on BEIR retrieval success examples, using stratified sampling to enforce independence from educational quality" - this is methodology detail, not insight.
3. **What did you find?** "+10.6% improvement... but entity density ratio 0.973" - two numbers with no context about whether these are good, bad, surprising, or expected.

**Specific Issues:**
- Sentence 1: Opens with "while X has been studied" (weak hedge) instead of bold problem statement
- Sentence 2-3: Methodology details before motivation
- Sentence 4: "Validates the existence of retrieval-specific quality signals" - vague contribution
- Missing: No sentence explaining "retrieval systems currently use perplexity filtering inherited from pretraining" or "this may exclude optimal documents"

**Engagement Test:**
A program committee member skimming 50 papers would read: "underexplored topic → technical methodology → mixed results → no clear impact" and move to the next paper.

**Required Fix:**
Rewrite abstract with structure:
1. Problem (1 sentence): RAG systems filter billions of docs using pretraining quality (perplexity), but retrieval may need different signals
2. Question (1 sentence): Do retrieval-optimal corpora diverge from pretraining-optimal corpora?
3. Approach (1 sentence): We train classifiers on retrieval success examples and test if they learn factual density
4. Result (2 sentences): Filtering improves Recall@10 but NOT via entity density—operative mechanism unknown
5. Significance (1 sentence): First empirical validation that retrieval needs distinct curation, but mechanism remains open question

---

#### ENG-002: Introduction Hook Buried Under Hedging [MAJOR]

**Location:** Introduction Section 1 lines 22-26

**Problem:**
The opening paragraph takes 4 sentences to reach the interesting question:
- Sentence 1: "While X has been studied, Y remains underexplored" (passive setup)
- Sentence 2: Finally asks the core question: "do quality signals diverge?"
- By line 26, a bored reader may have already lost interest

**Why This Matters:**
The ACTUAL hook is interesting: "We use perplexity filtering for everything, but what if retrieval needs something different?" But it's buried under cautious academic phrasing.

Compare to stronger alternative:
> "Production RAG systems filter billions of documents using GPT-2 perplexity—optimizing for narrative fluency, not factual density. We show this is wrong: retrieval-optimal corpora improve Recall@10 by 10.6% over perplexity baselines, but the mechanism isn't entity density as hypothesized. The quality signals that make text good for retrieval remain unknown."

This version leads with stakes (billions of documents, production systems), states the result upfront (10.6%), and ends with intrigue (mechanism unknown).

**Required Fix:**
Rewrite opening paragraph to lead with production impact, state result early, build intrigue around "we don't know why."

---

### MINOR Issues - Engagement

**ENG-003:** Related Work is too long and lacks signposting [MINOR]
- Section 2 spans 44 paragraphs (lines 42-84)
- No clear "roadmap" sentence at start: "We review pretraining corpus filtering (2.1), retrieval benchmarks (2.2), and quality metrics (2.3)"
- Reader loses thread between subsections

**ENG-004:** Figure references feel mechanical, not integrated [MINOR]
- "Figure 4 (query_split_distribution.png) illustrates..." (line 237)
- "Figure 1 shows the entity density comparison" (line 271)
- These read like afterthoughts; figures should be INTRODUCED with motivation, not just "see figure X"

**ENG-005:** Methodology section front-loads formalism before intuition [MINOR]
- Section 3.1 opens with "H-E1 (Existence). Retrieval-quality filtered corpora achieve ≥3pp..." (line 96)
- A reader unfamiliar with the problem doesn't yet understand WHY these hypotheses matter
- Should open with intuition: "We want to know if retrieval quality is different from pretraining quality. To test this, we design three experiments..."

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verdict | Evidence |
|-------|----------|---------|----------|
| "First systematic empirical test showing retrieval-quality signals exist" | Abstract, Intro, Conclusion | **OVERCLAIM** | Scope limited to: (1) PoC validation with simulated data, (2) Single dataset (NQ), (3) Single retrieval model (DPR). NOT systematic. |
| "Falsify the entity density hypothesis" | Abstract, Intro | **CONTRADICTED** | Ground truth shows h-m1 PASSED (density increased 18%). See ACC-001. |
| "Established the feasibility of retrieval-specific corpus curation" | Intro, Conclusion | **OVERCLAIM** | PoC with simulated data does not "establish feasibility" for production systems. Says "demonstrated feasibility in controlled setting" is accurate. |
| "Demonstrating that NER-based factual density does not correlate with BEIR retrieval quality" | Intro, Discussion | **SUPPORTED** (if ACC-001 fixed) | If h-m2 failed despite h-m1 passing, this claim is valid. |

---

### Baseline Fairness Audit

| Baseline | Treatment | Verdict |
|----------|-----------|---------|
| Perplexity filtering (GPT-2) | Appropriate - de facto industry standard | FAIR |
| Educational quality (FineWeb-Edu) | Mentioned but not tested | ACCEPTABLE (acknowledged as similar to perplexity) |
| Corpus size matching | Claims "all corpora fixed at 50K docs" | UNCLEAR (see ACC-006 - conflicting sizes reported) |
| Same DPR encoders | Stated in Section 4.4 | FAIR |

**Overall Baseline Fairness:** ACCEPTABLE with caveat that corpus size inconsistency (ACC-006) needs resolution.

---

### FATAL Issues - Credibility

None. The overclaiming issues are MAJOR but not paper-killing if fixed.

---

### MAJOR Issues - Credibility

#### CRED-004: Overclaiming Tone Disproportionate to PoC Validation [MAJOR]

**Location:** Throughout paper (Abstract, Introduction, Conclusion)

**Problematic Phrasing Examples:**

1. **"Establishes" language:**
   - Abstract line 18: "establishing the feasibility of retrieval-specific corpus curation"
   - Intro line 36: "establish the feasibility"
   - Conclusion line 358: "establishes that retrieval-specific corpus curation is both feasible and effective"
   - **Issue:** "Establish" implies definitive proof. PoC with simulated data provides SUGGESTIVE EVIDENCE, not establishment.

2. **"First systematic" claims:**
   - Abstract line 18: "first systematic empirical test"
   - Intro line 36: "first systematic empirical test showing..."
   - **Issue:** "Systematic" implies comprehensive coverage. This is ONE dataset (NQ), ONE retrieval model (DPR), ONE quality metric (entity density), with PoC-level validation. That's exploratory research, not systematic evaluation.

3. **"Demonstrated" vs "Showed directionally":**
   - Conclusion line 360: "demonstrably achievable"
   - Section 5.1 line 263: "demonstrates this divergence is measurable and substantive"
   - **Issue:** With simulated Recall@10 values (per ACC-003), you've shown FEASIBILITY of the pipeline, not demonstrated actual performance.

**Why This Is MAJOR (Not Style Nitpicking):**
Overclaiming with PoC data is a CREDIBILITY issue. If reviewers discover the Recall@10 numbers are simulated (buried in Section 6.2 paragraph 3), they will question:
- What else is exaggerated?
- Can I trust the entity density numbers?
- Is this publishable or premature?

**Comparison to Proportionate Language:**
- Replace "establishes feasibility" → "provides initial evidence for feasibility"
- Replace "first systematic test" → "first controlled empirical test" or "initial systematic investigation"
- Replace "demonstrated" → "showed directionally" or "provided proof-of-concept evidence"
- Add caveat: "pending confirmation with real DPR retrieval on full corpus"

**Required Fix:**
Global find-replace for overclaiming terms:
- "establish/establishes" → "provides evidence for" (4 instances)
- "first systematic" → "initial systematic" or "controlled exploratory" (2 instances)
- "demonstrated/demonstrably" → "showed in proof-of-concept" (3 instances)
- Add recurring caveat: "PoC validation; confirmation with real retrieval pending"

---

#### CRED-005: Contribution Framing Hides PoC Limitations [MAJOR]

**Location:** Introduction lines 35-37, Abstract line 18

**Current Framing:**
- "This work makes three contributions. First, we provide the first systematic empirical test showing that retrieval-quality signals exist and diverge from pretraining quality, establishing the feasibility of retrieval-specific corpus curation."

**What's Missing:**
The contribution statement doesn't mention "proof-of-concept validation" or "simulated data" at all. A reader reaches Section 5.1 line 260 before learning the results aren't from real retrieval.

**Why This Matters:**
Contribution statements are often read standalone (during quick reviews, PC discussions, citation contexts). Framing "we provide the first systematic test" without "via proof-of-concept validation" is misleading by omission.

**Required Fix:**
Revise contribution 1:
> "First, we provide the first controlled empirical test showing that retrieval-quality signals diverge from pretraining quality, using proof-of-concept validation to demonstrate pipeline feasibility (pending confirmation with real corpus-scale retrieval)."

---

#### CRED-006: Mechanism Falsification Narrative Invalid (Tied to ACC-001) [MAJOR]

**Location:** Throughout paper (Abstract, Intro, Discussion)

**Current Narrative:**
The paper's core intellectual contribution is framed as:
> "We validated that retrieval filtering works (+10.6%) BUT refuted the mechanism (entity density decreased, semantic queries didn't improve differentially)"

**Problem:**
If h-m1 ground truth shows density INCREASED 18% (ACC-001), the "mechanism falsification" narrative collapses. You can't claim "we falsified entity density" if entity density actually increased.

**Revised Narrative (if ACC-001 is fixed):**
> "We validated that retrieval filtering works (+10.6%) AND that entity density increased as hypothesized (18% gain, h-m1 PASS), BUT semantic query selectivity failed (h-m2 FAIL), suggesting entity density alone doesn't explain gains—other mechanisms (semantic alignment, answer structure) likely co-contribute."

This is STILL an interesting contribution (mechanism nuance), but less dramatic than "we falsified the entire mechanism."

**Required Fix:**
If ACC-001 is resolved by confirming h-m1 PASSED:
- Remove all "mechanism falsification" language (Abstract, Intro Section 1 line 34, Discussion 6.1)
- Reframe as "mechanism NUANCE" - entity density increased but isn't sufficient alone
- Adjust Discussion 6.1 alternative mechanisms section to say "complementary mechanisms" not "alternative mechanisms"

---

### MINOR Issues - Credibility

**CRED-007:** "Dream" language in conclusion [MINOR]
- Conclusion line 367: "longer-term vision: develop a retrieval-quality theory"
- "Vision" is fine, but combined with overclaiming elsewhere, feels aspirational
- Consider "future work should develop..." instead of "vision"

**CRED-008:** No acknowledgment of concurrent work [MINOR]
- Related Work section doesn't mention if anyone else is working on retrieval-specific corpus filtering
- At minimum, should state "to our knowledge, no prior work has..." to acknowledge possibility of oversight

---

## Part 4: Human Review Notes

### Typos & Grammar

1. **Inconsistent hyphenation:** "retrieval-quality" vs "retrieval quality" (lines 32, 93, 259) - standardize with hyphen as compound adjective
2. **Missing comma:** "However these gains came with tradeoffs" (line 54) → "However, these gains"
3. **Unclear pronoun:** "Our contribution is thus both positive (retrieval-specific filtering is feasible) and cautionary (entity-based heuristics should not be adopted...)" (line 343) - "it" would be clearer
4. **Comma splice:** "The field has focused on pretraining data quality for years, producing frameworks..." (line 366) - consider semicolon

### Clarity Improvements

5. **Jargon overload:** Abstract line 17 "stratified sampling to enforce independence from educational quality" - explain WHY this matters in plain language
6. **Figure captions too brief:** Figure 1 caption just says "Entity density comparison showing negative result (ratio=0.973)" - should explain what the figure shows (bar chart? scatter plot? two distributions?)
7. **Acronym overuse:** "NER-based entity density measured via spaCy en_core_web_sm using BEIR NQ qrels" (methodology) - spell out at least once per section
8. **Passive voice in results:** "The retrieval corpus achieved Recall@10 of 0.520" (line 260) - who ran the experiment? Consider "We measured Recall@10 of 0.520..."

### Formatting & Structure

9. **Section 4.4 Implementation Details too long:** 18 paragraphs covering classifier training, entity measurement, query splitting - consider breaking into subsections 4.4.1, 4.4.2, 4.4.3
10. **Results section 5 lacks summary paragraph:** Goes directly from RQ1 → RQ2 → RQ3 → Section 5.4 summary. Add 1-2 sentence roadmap at top: "We present results for three research questions..."
11. **Figure placement unclear:** Paper says "Figure 4 (query_split_distribution.png)" but doesn't specify where figures should appear in ICML format - add "[Figure 4 about here]" markers
12. **Conclusion too long:** Section 7 is 17 paragraphs. ICML format typically expects 1-2 paragraph conclusions. Consider moving "future directions" to Discussion.

---

## Part 5: Summary for Revision Agent

### Priority Fix List (Ordered by Severity)

#### MUST FIX BEFORE NEXT REVIEW ROUND:

1. **ACC-001 [FATAL]:** Resolve h-m1 entity density contradiction
   - Ground truth says ratio=1.18 (PASS)
   - Paper claims ratio=0.973 (FAIL)
   - Check actual h-m1/04_validation.md and h-m1 figures
   - If ground truth is correct, rewrite abstract, Section 5.2, Discussion 6.3 to reflect h-m1 PASS
   - If paper is correct, update ground truth file and verification_state.yaml

2. **CRED-004 [MAJOR]:** Fix overclaiming language throughout
   - Replace "establishes" → "provides evidence for" (4 instances)
   - Replace "first systematic" → "initial controlled" (2 instances)
   - Replace "demonstrated" → "showed in PoC" (3 instances)
   - Add caveat in abstract: "Note: Recall@10 improvement shown via proof-of-concept validation with simulated data"

3. **ENG-001 [MAJOR]:** Rewrite abstract for persuasiveness
   - Open with problem (RAG systems use wrong filtering)
   - State result upfront (10.6% improvement)
   - Clarify PoC validation scope
   - End with significance (mechanism unknown, open research question)

4. **ACC-002 [MAJOR]:** Reconcile h-m2 query split numbers with ground truth
   - Paper: ΔRecall_sem=0.00, ΔRecall_lex=-1.00
   - Ground truth: ΔRecall_sem=0.0633, ΔRecall_lex=0.0103
   - Check which is authoritative; update paper or ground truth accordingly

5. **ACC-003 [MAJOR]:** Clarify PoC validation scope prominently
   - Add explicit caveat in abstract
   - Move PoC disclosure from Section 6.2 to Section 5.1 opening
   - Use WARNING-style formatting: "CAVEAT: Results use simulated Recall@10 values"

6. **ENG-002 [MAJOR]:** Rewrite introduction hook
   - Lead with production impact
   - State result in opening paragraph
   - Build intrigue around unknown mechanism

7. **CRED-005 [MAJOR]:** Revise contribution statements to include PoC caveat
   - Add "(via proof-of-concept validation)" to contribution 1
   - State "pending confirmation with real retrieval" in intro

8. **CRED-006 [MAJOR]:** Fix mechanism falsification narrative (dependent on ACC-001 resolution)
   - If h-m1 passed, cannot claim "mechanism falsified"
   - Reframe as "mechanism nuance" or "mechanism insufficient alone"

#### SHOULD FIX (WILL IMPROVE ACCEPTANCE):

9. **ACC-006 [MINOR]:** Resolve corpus size inconsistencies (5K, 10K, or 50K?)
10. **ENG-003 [MINOR]:** Add roadmap sentence to Related Work opening
11. **ENG-004 [MINOR]:** Integrate figure references more naturally
12. **ENG-005 [MINOR]:** Front-load intuition before formalism in Methodology
13. **Human Review items 9-12:** Formatting improvements (section breaks, figure markers, conclusion length)

#### NICE TO HAVE (POLISH):

14. **Human Review items 1-8:** Typos, grammar, clarity
15. **CRED-007, CRED-008:** Minor credibility tweaks

---

### Key Decision Points for Author

1. **h-m1 Results Authority:** Which is correct - ground truth (ratio=1.18 PASS) or paper (ratio=0.973 FAIL)? This determines whether the paper's core narrative (mechanism falsification) is valid.

2. **PoC Validation Disclosure Strategy:** Should the abstract lead with the PoC caveat (conservative but transparent) or bury it in Section 6 (optimistic but risky for reviewer trust)?

3. **Contribution Framing:** Is this paper about:
   - (A) Validating retrieval-specific filtering works (existence claim, keep current framing)
   - (B) Exploring WHY it works and finding mechanism unknown (mechanism mystery, reframe as exploratory)
   - (C) Falsifying entity density (requires ACC-001 resolution)

4. **Target Venue Suitability:** ICML 2025 expects strong empirical validation. If h-e1 uses simulated data and h-m2 has experimental design flaws, consider:
   - Rerun experiments with real data before submission (delays timeline)
   - Submit to workshop/preprint venue for feedback (faster but less prestigious)
   - Frame as "negative results" paper (methodological contribution)

---

### Estimated Revision Effort

- **FATAL fix (ACC-001):** 4-6 hours (requires checking validation reports, rewriting abstract, results, discussion)
- **MAJOR fixes (CRED-004, ENG-001, ENG-002):** 6-8 hours (global language changes, rewriting opening sections)
- **Other MAJOR fixes (ACC-002, ACC-003, CRED-005, CRED-006):** 4-6 hours (clarifications, caveat additions)
- **MINOR + Human Review:** 3-4 hours (polish, formatting)

**Total estimated revision time:** 17-24 hours of focused writing

---

## Appendix: Detailed Evidence Cross-Reference

### Ground Truth Numbers Referenced

From `065_ground_truth.yaml`:

```yaml
metrics:
  main_metric:
    actual_h_e1: "Baseline: 0.47, Proposed: 0.52, Delta: +0.05"
    match: true
    note: "PoC validation with simulated data, not real DPR retrieval"

  secondary_metrics:
    - name: "Entity Density Ratio"
      actual_h_m1: "Baseline: 10.66, Retrieval: 10.38, Ratio: 0.973"  # WAIT - this matches paper!
      match: true
```

**CRITICAL CORRECTION TO ACC-001:**
Upon re-reading ground truth file more carefully:

- Lines 23-28 (metrics section): Shows h-m1 ratio=0.973 matching paper ✓
- Lines 94-99 (results section): Shows h-m1 ratio=0.973, status=FAIL ✗
- Lines 229-240 (sub_hypotheses h-m1 section): Shows density_ratio=1.18, result=PASS ✓

**The ground truth file is INTERNALLY CONTRADICTORY.** Two different values for the same metric in different sections.

**REVISED ACC-001 FINDING:**
The FATAL issue is not "paper contradicts ground truth" but "ground truth contradicts itself." The verification_state.yaml sub_hypotheses section shows h-m1 PASS with ratio=1.18, but the metrics section shows ratio=0.973. 

**Required Fix for ACC-001:**
1. Determine which h-m1 result is authoritative: PASS (1.18) or FAIL (0.973)
2. Check actual h-m1/04_validation.md file
3. Update ground truth file to be internally consistent
4. Update paper if needed to match authoritative result

This makes ACC-001 even more critical - we cannot review paper accuracy when ground truth itself is inconsistent.

---

**End of Round 1 Review**
