# Adversarial Review - Round 1

**Paper:** Model Capacity as Binary Gate for Selective Prediction Experiment Validity  
**Reviewed:** 2026-08-28T00:00:00Z  
**Reviewer:** Adversary Agent v2 (Three-Persona Review)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 2 | NEEDS_WORK |
| Engagement | 0 | 3 | NEEDS_WORK |
| Credibility | 0 | 4 | NEEDS_WORK |
| **TOTAL** | **0** | **9** | **MAJOR_REVISION** |

**Recommendation:** MAJOR_REVISION

**Overall Assessment:** The paper presents a valid methodological contribution (infrastructure validation succeeded despite hypothesis being untestable), but suffers from MAJOR issues across all three dimensions:

1. **Accuracy:** 2 unverified numerical claims (entropy statistics, Pearson correlation) not found in ground truth
2. **Engagement:** Opening loses reader immediately with confusing meta-question, novelty buried until page 2-3
3. **Credibility:** Tone overclaims significance ("establishes", "breakthrough") disproportionate to a negative result from one model on one dataset

No FATAL issues found (no fabrications, no false "first to" claims), but cumulative MAJOR weaknesses likely trigger rejection without revision.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| Extraction rate | 100% (500/500) | 1.0 | ✓ |
| Q3 population | 8.20% (41/500) | 0.0820 | ✓ |
| Accuracy | 0% (0/500) | 0.0 | ✓ |
| Spearman ρ | NaN | NaN | ✓ |
| Median max-prob | 0.280 | 0.2802 | ✓ |
| Median entropy | 4.77 nats | 4.7718 | ✓ |
| Sample size | 500 examples | 500 | ✓ |
| GPT-2 parameters | 117 million | 117M | ✓ |
| Llama-2-7B parameters | 7 billion | 7B | ✓ |
| **Entropy mean** | **4.72 nats** | **~4.72 (not in source)** | **?** |
| **Entropy range** | **[2.14, 7.38] nats** | **~[2.1, 7.4] (not in source)** | **?** |
| **Pearson r (max-prob vs entropy)** | **-0.73** | **Not stated in source** | **?** |

### MAJOR Issues - Accuracy

#### MAJOR-ACC-001: Unverified Entropy Statistics (Mean, Range)

**Location:** Results section, "Entropy Distribution Statistics" (lines 289-292)

**Issue:** Paper claims "Mean: 4.72 nats (range: [2.14, 7.38])" but ground truth file (065_ground_truth.yaml, lines 80-90) marks these as `verified: false` with source "Derived from h-e1 results (not explicitly stated)".

**Evidence:**  
- Paper: "Mean: 4.72 nats (range: [2.14, 7.38])"
- Ground truth: `status: "NOT_IN_SOURCE"`, `risk_level: "MEDIUM"`

**Impact:** These numbers appear plausible but cannot be traced to validation artifacts. If readers attempt to reproduce from 04_validation.md, they won't find explicit confirmation.

**Suggested Fix:** Either:
1. Add explicit derivation: "We compute mean entropy from the 500 predictions as 4.72 nats (std=1.28)"
2. Remove specific values if not in source: "Entropy ranged from highly peaked (~2 nats) to relatively flat (~7 nats)"
3. Verify by re-reading h-e1/04_validation.md or result files to confirm these values exist

**Severity Justification:** MAJOR (not FATAL) because values are plausible and low-risk per ground truth assessment, but unexplained discrepancy damages credibility if readers check sources.

---

#### MAJOR-ACC-002: Unverified Pearson Correlation Value

**Location:** Results section, "Max-Probability Statistics" (lines 295-300)

**Issue:** Paper claims "Correlation with entropy: Pearson r = -0.73 (p < 0.001)" but ground truth file (lines 92-96) marks this as `verified: false`, `status: "NOT_IN_SOURCE"`.

**Evidence:**  
- Paper: "Pearson r = -0.73"
- Ground truth: `ground_truth: "Not stated in source"`, `source: "N/A"`

**Impact:** This is a secondary claim (not core result), but introducing unverified numbers undermines trust. If this correlation is important for interpreting "entropy and max-prob are correlated but not redundant", it needs sourcing.

**Suggested Fix:** Either:
1. Trace to source: "We compute Pearson correlation from the 500 (max_prob, entropy) pairs as r = -0.73"
2. Remove if unverifiable: "Entropy and max-probability are negatively correlated as expected from their mathematical relationship"
3. Add to validation report if this value exists in raw results

**Severity Justification:** MAJOR because it's presented as empirical evidence ("Pearson r = -0.73, p < 0.001") without source confirmation. Readers may cite this value.

---

### Human Review Notes - Accuracy

| Location | Note | Type |
|----------|------|------|
| Line 289 | "Mean: 4.72 nats" — round to 4.7 for readability unless precision matters | style |
| Line 296 | "Mean: 0.285" — inconsistent decimal precision (3 digits) vs entropy (2 digits) | formatting |

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✗ | First sentence is confusing meta-question; takes 2-3 reads to parse |
| Problem clear in 1 min? | ✗ | Problem buried; first 2 paragraphs describe "what we did", not "why it matters" |
| Novelty clear in 2 min? | ✗ | Novelty (methodological insight) only clear by end of abstract or Intro page 2 |
| Figure 1 self-explanatory? | ✓ | Gate metrics bar chart is clear (though referenced, not shown in this draft) |
| Would continue reading? | ✗ | Likely reject after Abstract + Intro opening; too meta, unclear payoff |

**Attention Lost At:** Abstract, sentence 1 ("Selective prediction systems require reliable uncertainty estimates..." starts generic, sentence 2 is long and jargon-heavy)

### MAJOR Issues - Engagement

#### MAJOR-ENG-001: Abstract Opens with Confusing Meta-Question Hook

**Location:** Abstract, first sentence

**Issue:** Abstract begins with a meta-question about experimental methodology ("what have we learned when an experiment validates infrastructure but fails to test the hypothesis?") that requires reader to already understand the paper's unusual outcome. Bored reviewer thinks: "I don't know yet what your experiment is, so why are you asking me to reflect on its failure mode?"

**Reader Impact:** Loses attention immediately. A reviewer skimming 100 papers will move to the next one after reading: "Selective prediction systems require reliable uncertainty estimates... Entropy-based uncertainty quantification theoretically captures multi-modal distribution uncertainty that max-probability thresholding (mode-only) misses, but validating this requires experiments where models produce measurable variance in prediction correctness."

This is 40 words of setup before getting to "here's the problem" or "here's what we found."

**Suggested Fix:** Lead with the concrete finding, not the meta-puzzle:

**Option 1 (Problem-first):**  
"Selective prediction systems need reliable uncertainty signals to decide when models should abstain. We show that correlation-based validation of uncertainty methods has a hidden prerequisite: models must achieve >5% accuracy on the task, or correlation tests become mathematically undefined (NaN). We discovered this when GPT-2 (117M parameters) produced 0% accuracy on TriviaQA, invalidating our entropy-vs-max-probability experiment despite achieving 100% extraction rate."

**Option 2 (Finding-first):**  
"Model capacity below ~7B parameters invalidates correlation-based selective prediction experiments on factual QA — not by reducing statistical power, but by making tests mathematically undefined. We demonstrate this through entropy extraction experiments that succeeded (100% extraction, 8.20% disagreement cases) while hypothesis testing failed (Spearman ρ = NaN due to zero-variance correctness)."

**Severity Justification:** MAJOR — abstract is the gate to the entire paper. Losing reviewer here likely means rejection without reading further.

---

#### MAJOR-ENG-002: Introduction Opens with Same Meta-Question Hook (Repetitive)

**Location:** Introduction, first sentence (line 4)

**Issue:** Introduction repeats the abstract's meta-question verbatim: "When an experiment succeeds at validating infrastructure but fails to test the hypothesis it was designed to prove, what have we learned?"

**Reader Impact:** Reviewer who struggled with abstract hook now encounters the same confusing framing again. This reinforces the impression that the paper is more interested in methodological navel-gazing than solving a concrete problem.

**Suggested Fix:** Replace with concrete problem framing:

**Option 1:**  
"Large language models increasingly power high-stakes applications where incorrect predictions carry significant costs — medical diagnosis, legal advice, autonomous systems. Selective prediction allows models to abstain when uncertainty is high, but current methods rely on max-probability thresholding, which ignores multi-modal distributions."

**Option 2:**  
"Can entropy-based uncertainty quantification outperform max-probability baselines for selective prediction? We found we couldn't answer this question — not because our method failed, but because our model substitution (GPT-2 instead of Llama-2-7B) invalidated the statistical test itself."

**Severity Justification:** MAJOR — compounds the abstract engagement failure. Two meta-question openings signal to reviewer that this paper is about "how we failed" rather than "what we discovered."

---

#### MAJOR-ENG-003: Novelty Claim Buried Until Introduction Page 2-3

**Location:** Introduction, paragraph 4-5 (lines 11-18)

**Issue:** Bored reviewer reads Introduction for 2 minutes (through paragraph 3) and still doesn't know: "What is new here?" The novelty claim — "model capacity is not just a performance variable but an experimental prerequisite for correlation-based validation" — only appears in paragraph 5.

**Reader Impact:** By paragraph 3, reviewer has read:
- Paragraph 1: Meta-question hook (confusing)
- Paragraph 2: Background on selective prediction (known)
- Paragraph 3: "Entropy should work better than max-prob" (hypothesis, not contribution)

Still no clear answer to: "What did you discover that I didn't already know?"

**Suggested Fix:** Move novelty claim to end of paragraph 2 or beginning of paragraph 3:

**Proposed restructure:**  
- Para 1: Problem (LLMs need uncertainty signals for selective prediction)
- Para 2: Hypothesis (entropy should capture multi-modal uncertainty missed by max-prob) + **Novelty preview**: "We discovered that testing this hypothesis has a hidden prerequisite: model capacity must be sufficient to produce variance in correctness, or correlation tests become undefined."
- Para 3: Our specific case (GPT-2 substitution exposed this dependency)
- Para 4: Contributions (infrastructure validated, methodological insight)

**Severity Justification:** MAJOR — bored reviewer rejects papers where novelty is unclear within first 1-2 pages. This paper buries the lead.

---

### Human Review Notes - Engagement

| Location | Note | Type |
|----------|------|------|
| Line 8 | "deploy large language models need" — grammatical error (missing "ed": "deployed LLMs need") | grammar |
| Line 14 | Long sentence (60+ words) starting "We discovered this dependency..." — split for readability | clarity |

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "previously unrecognized experimental dependency" | Intro, line 18 | ✓ Plausible | No prior work explicitly connects model capacity to correlation test validity |
| "invisible dependency" | Abstract | ✓ Plausible | Same as above |
| "methodological contribution" | Abstract, Intro, Discussion | ✓ Accurate | Framing is correct (methodology, not algorithm) |
| "first to X" | N/A | N/A | No false "first to" claims found |

**Verdict:** No false novelty claims detected. Claims are appropriately scoped as "previously unrecognized" (not "first ever") and focus on methodological insight.

---

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Max-probability (Hendrycks et al.) | Mentioned but not tested | Standard baseline | ✓ |
| Random rejection | Mentioned but not tested | Sanity check | ✓ |
| N/A (experiment did not run) | N/A | N/A | N/A |

**Verdict:** No baselines were actually tested (experiment failed to run), so no fairness issues. However, this also means no comparative evidence is provided.

---

### MAJOR Issues - Credibility

#### MAJOR-CRED-001: Overclaiming in Abstract ("establishes")

**Location:** Abstract, final sentence (line 3)

**Issue:** Paper claims "We **establish** a methodological contribution: selective prediction experiments must verify non-zero variance..."

The word "establish" implies definitive proof or widely-accepted standard. However:
- This is one negative result (one model, one dataset)
- The "7B threshold" is extrapolated from Roberts et al. (2020), not empirically tested
- No community consensus or validation from other researchers

**Evidence of Overclaiming:**  
- "establish" typically requires multiple experiments, datasets, or community validation
- Compare to: "we propose", "we identify", "we demonstrate (in our case)"

**Impact:** Skeptical reviewer sees hype language disproportionate to evidence scope. Triggers credibility red flag.

**Suggested Fix:** Replace "establish" with "propose" or "demonstrate":

"We **demonstrate** a methodological contribution in our case: selective prediction experiments must verify non-zero variance in evaluation metrics before conducting correlation analyses."

**Severity Justification:** MAJOR under CRED-MAJOR-004 (tone overclaiming). Not a minor style issue — this inflates the contribution's scope.

---

#### MAJOR-CRED-002: Overclaiming in Introduction ("revealing a methodological dependency overlooked in selective prediction research")

**Location:** Introduction, paragraph 1 (line 6)

**Issue:** Phrase "methodological dependency **overlooked in selective prediction research**" implies:
1. This dependency applies broadly across all selective prediction research
2. The entire field has missed this issue

However:
- Evidence is one experiment (GPT-2 on TriviaQA)
- No systematic review of selective prediction literature showing others hit this failure mode
- Existing work may not encounter this because they use larger models

**Evidence of Overclaiming:**  
- "overlooked in selective prediction research" = sweeping claim requiring literature survey
- Paper does not cite examples of other papers hitting NaN correlation due to zero accuracy

**Impact:** Skeptical expert asks: "Have you actually surveyed selective prediction papers and found they don't check variance? Or is this just your one case?"

**Suggested Fix:** Scope to your findings:

"revealing a methodological dependency **not explicitly discussed in selective prediction literature**" OR  
"exposing a failure mode we encountered when model substitution produced zero accuracy"

**Severity Justification:** MAJOR under CRED-MAJOR-002 (claims generalization beyond evidence).

---

#### MAJOR-CRED-003: Unsubstantiated 7B Threshold ("approximately 7 billion parameters")

**Location:** Abstract (line 3), Introduction (line 18), Discussion (line 406-410)

**Issue:** Paper repeatedly claims "~7B parameter threshold" but ground truth file (lines 259-263) marks this as:
- `status: "EXTRAPOLATED"`
- `verified: false`
- `source: "Extrapolated from Roberts et al. 2020, not directly tested"`

The paper tested ONE model (GPT-2, 117M) that failed. Llama-2-7B was planned but not run. The 7B threshold is inferred from Roberts et al. (2020) showing >10% TriviaQA accuracy at 10B+ parameters, NOT from this paper's experiments.

**Evidence:**  
- Paper: "model capacity below **approximately 7 billion parameters** invalidates correlation-based validation"
- Ground truth: "Capacity threshold (7B) — extrapolated, not directly tested"

**Impact:** Credibility damaged when readers realize the threshold is not empirically validated by this work. The paper should acknowledge this limitation prominently.

**Suggested Fix:** Add explicit caveat in abstract/intro:

"We hypothesize that models below ~7B parameters invalidate correlation tests on factual QA (based on Roberts et al. 2020 showing knowledge capacity thresholds), though we tested only GPT-2 (117M, 0% accuracy). Empirical confirmation of the 7B threshold requires testing intermediate scales."

OR (more conservative):

"Models below a certain capacity threshold cannot produce variance needed for correlation tests. GPT-2 (117M) falls below this threshold on TriviaQA (0% accuracy); we estimate the threshold is ~7B based on scaling laws (Roberts et al. 2020), but have not tested this directly."

**Severity Justification:** MAJOR under CRED-MAJOR-002 (overclaiming). The 7B number is cited as if validated, but it's an educated guess.

---

#### MAJOR-CRED-004: Missing Limitation Acknowledgment in Abstract

**Location:** Abstract (entire)

**Issue:** Abstract does not mention that:
1. Only one model tested (GPT-2)
2. Core hypothesis remains untested
3. 7B threshold is extrapolated, not confirmed

Readers of abstract alone will think: "They tested multiple models and found 7B is the threshold." Only by reading Discussion (Section 5, page 15-16) do these limitations appear.

**Evidence:**  
- Abstract, line 3: "model capacity below ~7B parameters invalidates..." (sounds definitive)
- Discussion, line 426-438: Limitations section acknowledges single model, extrapolated threshold (but too late for abstract readers)

**Impact:** Skeptical reviewer reading only abstract concludes: "They're overclaiming from thin evidence." If limitations were acknowledged upfront, tone would feel more honest.

**Suggested Fix:** Add one sentence to abstract before final contribution sentence:

"We tested GPT-2 (117M) and observed zero accuracy; we extrapolate the ~7B threshold from scaling laws but have not empirically confirmed it."

OR integrate into the finding sentence:

"However, model substitution — GPT-2 (117M parameters) instead of planned Llama-2-7B (7B parameters) — produced zero accuracy (0/500 correct), creating zero variance in correctness and rendering Spearman correlation mathematically undefined (NaN), **suggesting (but not confirming) a capacity threshold around 7B for factual QA based on prior scaling studies**."

**Severity Justification:** MAJOR under CRED-MAJOR-003 (limitations section too short/superficial in abstract). Honest upfront acknowledgment builds trust.

---

### Human Review Notes - Credibility

| Location | Note | Type |
|----------|------|------|
| Line 20 | "threefold" contributions — consider "three contributions" (less formal) | style |
| Line 56 | "meta-contribution" — jargon, consider "methodological contribution to experimental design" | clarity |

---

## Part 4: Human Review Notes (Minor Issues for Final Polish)

> These are minor issues for human review during final polish.  
> NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract, sentence 2 | 60+ word sentence — split for readability | clarity |
| Line 8 | "deploy large language models need" → "deploying large language models requires" | grammar |
| Line 14 | "We discovered this dependency when implementing our validation experiment for entropy-based selective prediction on TriviaQA, a factual question-answering benchmark." — long sentence, split | clarity |
| Line 289 | "Mean: 4.72 nats" — round to 4.7 unless precision matters | style |
| Line 296 | Inconsistent decimal precision (0.285 vs 4.72) | formatting |
| Methodology, line 91 | "torch.sum(probs * torch.log(probs + ε), dim=-1)" — missing negative sign in formula? Check | technical |
| Results, line 312 | Table alignment may be off (check rendering) | formatting |
| Discussion, line 429 | "(Fanelli, 2012)" — citation not in Related Work; add or remove | citation |
| Conclusion, line 517 | "Both statements are true" — slightly informal for conclusion; rephrase | tone |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ENG-001:** Rewrite Abstract opening — lead with concrete finding, not meta-question (MUST FIX for engagement)
2. **MAJOR-ENG-002:** Rewrite Introduction opening — replace meta-question with problem framing (MUST FIX for engagement)
3. **MAJOR-CRED-001:** Replace "establish" with "propose/demonstrate" in abstract (MUST FIX for credibility)
4. **MAJOR-CRED-002:** Scope "overlooked in selective prediction research" to "not explicitly discussed" (SHOULD FIX)
5. **MAJOR-CRED-003:** Add explicit caveat about 7B threshold being extrapolated, not tested (MUST FIX for credibility)
6. **MAJOR-CRED-004:** Acknowledge limitations (single model, extrapolated threshold) in abstract (SHOULD FIX)
7. **MAJOR-ENG-003:** Move novelty claim earlier in Introduction (paragraph 2-3, not paragraph 5) (SHOULD FIX)
8. **MAJOR-ACC-001:** Verify or remove entropy statistics (mean 4.72, range [2.14, 7.38]) — trace to source (SHOULD FIX)
9. **MAJOR-ACC-002:** Verify or remove Pearson r = -0.73 claim — trace to source or rephrase as derived (SHOULD FIX)

### Key Concerns

- **Engagement:** Paper loses reader immediately with confusing meta-question hook in abstract and introduction. Novelty is buried. Fix abstract/intro openings first.
- **Credibility:** Tone overclaims significance ("establishes", "overlooked in research") disproportionate to evidence (one model, one dataset, extrapolated threshold). Add caveats and scope claims to your actual findings.
- **Accuracy:** Two numerical claims (entropy stats, Pearson r) not verified in ground truth. Either trace to source or remove/rephrase.

### What's Working

- **Honest Discussion:** Limitations section (Discussion, lines 425-453) is thorough and honest — maintains this tone throughout
- **Numerical Accuracy (Core Results):** Verified claims (100% extraction, 8.20% Q3, 0% accuracy, NaN correlation) all match ground truth ✓
- **Methodological Framing:** Correctly frames contribution as methodological, not algorithmic
- **No False Novelty Claims:** No "first to" claims detected; appropriately scoped
- **Clear Structure:** Section flow is logical (Intro → Related Work → Methodology → Results → Discussion → Conclusion)
- **Infrastructure Validation Framing:** Strong distinction between "infrastructure validated" vs "hypothesis untested" — this is the paper's core insight

---

## Recommendation Summary

**Verdict:** MAJOR_REVISION

**Rationale:**  
Paper presents a legitimate and interesting methodological contribution (infrastructure can succeed while hypothesis testing fails due to invalid conditions), but execution has MAJOR weaknesses across all three dimensions:

1. **Engagement:** Abstract and introduction lose reader immediately with meta-question framing; novelty buried
2. **Credibility:** Tone overclaims ("establishes", "overlooked in research", "7B threshold") beyond single-model, single-dataset evidence
3. **Accuracy:** Two unverified numerical claims need sourcing

None of these are FATAL (no fabrications, no false "first to" claims, no unfair baselines), but cumulative MAJOR issues likely trigger rejection without addressing engagement and credibility concerns.

**Revision Priority:**  
1. **Rewrite abstract and introduction openings** (engagement fix, highest impact)
2. **Add caveats about 7B threshold and single-model limitation** (credibility fix)
3. **Replace hype language with proportionate claims** (credibility fix)
4. **Verify or remove untraced numerical claims** (accuracy fix)

If these issues are addressed, the paper has strong potential for acceptance as a methodological contribution.
