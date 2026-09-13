# Round 1 Adversarial Review

## Accuracy Checker Findings

### FATAL Issues
None detected. Quantitative claims match ground truth validation reports.

### MAJOR Issues

**MAJOR-1: Contradictory perplexity filtering claims (Methods vs Results)**
- **Location:** Methodology L104-106 vs h-e1 Results L256, Discussion L379
- **Evidence:** 
  - Methodology: "Perplexity filtering: Remove samples with high language model perplexity... Uses GPT-2 or KenLM scores. Threshold range: 500-1500 perplexity cutoff"
  - h-e1 Results Table 1 L99: "Samples Filtered (Perplexity): 0 (proxy)"
  - Discussion L379: "PoC used length-based perplexity proxy (filtered 0 samples)"
  - Ground truth L498: "Perplexity proxy (length-based) filtered 0 samples"
- **Problem:** Methodology describes perplexity as active technique with specific cutoffs (500-1500), but Results/Discussion reveal it filtered ZERO samples. A reader cannot reconcile "perplexity filtering is a core low-level technique" with "perplexity removed nothing" until Section 6.
- **Fix:** Methodology must front-load the PoC proxy limitation: "PoC execution used length-based proxy (not KenLM); this filtered 0 samples, limiting perplexity validation to code infrastructure only."

**MAJOR-2: Dataset sample count inconsistency**
- **Location:** Abstract L3, Methodology L88, Results h-e1 L256
- **Evidence:**
  - Ground truth L75-82: C4 52,002 samples, Dolly 15,000 samples, Alpaca 52,002 samples
  - Methodology L88: "C4 [Raffel et al., 2020], 52k subset"
  - Results Table 1 footnote L103: "Alpaca-52k (52,002 samples)"
  - BUT Abstract L3: "C4 pre-training and Dolly/Alpaca fine-tuning" (no counts)
  - Experiment Setup Table L161: "C4 subset: 52,002", "Dolly-15k: 15,000", "Alpaca-52k: 52,002"
- **Problem:** Precision varies. Ground truth has exact counts (52,002 for C4/Alpaca, 15,000 for Dolly), paper uses "52k" (L88), "15k" (L167), exact counts in tables. Not FATAL but sloppiness signals uncalibrated writing.
- **Fix:** Standardize on exact counts first mention, "52k/15k" thereafter. Or use exact everywhere. Pick one.

**MAJOR-3: h-m3 validation mismatch (quality bound location)**
- **Location:** Results h-m3 L314-328 vs Ground truth L124
- **Evidence:**
  - Ground truth L124: "actual_quality_bound: 0.4%"
  - Results Table 5 L320: Shows k=5000 results (11.3s, -2.4% delta)
  - Results text L328: "Quality bound at k=10000 (0.4% < 1% threshold) confirms late-stage embeddings can match full-dataset performance"
  - Ground truth L174-179 Table: Late-k10000 shows 0.463 MMLU vs 0.465 Baseline = 0.4% delta ✓
- **Problem:** Quality bound (0.4%) is for LATE-k10000, but Table 5 only shows k=5000. Reader must infer k=10000 data from prose (L328) without seeing the number in a table. h-m3 claims "three thresholds" (>2% mismatch, <1% quality bound, >3× cost) but Table 5 only shows 2/3 metrics at k=5000.
- **Fix:** Add k=10000 row to Table 5 OR cite "see full results in supplementary" OR state upfront "Table 5 shows k=5000 working point; k=10000 achieves 0.4% quality bound."

**MAJOR-4: Cohen's d significance interpretation**
- **Location:** Results h-m2 L296, Discussion L349
- **Evidence:**
  - Results L296: "Welch's t-test t=-7.606, p=0.078 (marginal, acceptable for exploratory SHOULD_WORK gate). Cohen's d=10.76 indicates large effect"
  - Ground truth L143: "p_value_h_m2: 0.078", "significant: marginal (acceptable for SHOULD_WORK gate)", "effect_size: 10.76"
  - Discussion L349: "Cohen's d=10.76 demonstrates categorical—not gradual—separation"
- **Problem:** p=0.078 is NOT significant at α=0.05 (standard threshold), yet paper leans hard on "categorical separation" (Discussion L349, Conclusion L404). A skeptical reviewer asks: "With p=0.078, how can you claim categorical vs continuous distinction?" The "exploratory SHOULD_WORK" gate justification (internal framework) won't persuade external readers.
- **Fix:** De-emphasize "categorical" language, strengthen "large effect size (d=10.76) suggests discrete categories, though p=0.078 is marginal; production validation with larger n needed."

---

## Bored Reviewer Findings

### 2-Minute Test: FAIL (loses attention at Introduction paragraph 3)

**Abstract (1 min): PASS**
- Clear problem (redundant curation optimization across stages)
- Clear insight (low-level = objective-independent → transfers)
- Clear result (0.38% vs 5.04%, Cohen's d=10.76)
- Would continue reading.

**Introduction paragraph 1-2 (1.5 min): PASS**
- Paragraph 1 hooks with specific waste example (C4 dedup threshold 0.7 re-tuned for Dolly, then RLHF)
- Paragraph 2 identifies gap (no systematic understanding of transfer)

**Introduction paragraph 3 (2 min): ATTENTION LOSS**
- **Location:** L10-11
- **Text:** "Our key insight is that **curation operations exist on a spectrum from objective-independent to objective-dependent**. Low-level quality filters like deduplication and perplexity-based outlier removal operate on surface statistics—n-gram overlap, token probability—that remain invariant across training objectives."
- **Problem:** This is JARGON without grounding. What does "objective-independent" mean to a reader who doesn't already know the answer? Why should I care about "I(filter_decision; stage_objective)" (L10, second sentence) when I don't yet understand the problem deeply?
- **Bored reviewer reaction:** "This sounds like the author is showing off terminology rather than explaining the idea. I'll skim to Results."

**Introduction paragraph 4 (validation paragraph): OKAY if reader survived para 3**
- Experiments listed (C4, Dolly, Alpaca), results previewed (≤1% vs >5%)
- But still no intuition for WHY deduplication is objective-independent

**Engagement diagnosis:**
- Paper frontloads mechanism (objective-independence) before building intuition
- Missing: "Deduplication removes exact copies—this doesn't depend on whether you're training for next-token prediction or instruction-following. Domain mixing optimizes for task distribution—this DOES depend on stage goal."
- Fix: Swap Introduction para 3 with intuitive example FIRST, formalism (I(filter; objective)) LATER

### Specific attention-loss points

**L10 (Introduction para 3):** "I(filter_decision; stage_objective)" → Unexplained notation scares off readers
**L23 (Related Work first sentence):** Jumps to DataComp/Pile without connecting back to taxonomy claim → feels like literature dump
**L48 (Methodology Overview para 2):** "four sub-hypotheses tested sequentially: (h-e1) transfer-stable categories exist..." → Why four? Why this structure? Feels arbitrary without motivation.
**L145 (Experimental Setup PoC section):** Buries "mock evaluation" at the END of setup. Skeptical reader who skipped to Methods sees real-sounding procedure (L193-204 hyperparameters), then L221 reveals "What's simulated: Model training, lm-eval execution." This feels like hiding the lede.

---

## Skeptical Expert Findings

### Novelty Overclaims

**CLAIM-1: "First empirically-grounded taxonomy" (Abstract L2, Intro L14, Conclusion L402)**
- **Challenge:** DataComp (Gadre et al. 2023) already tested filtering techniques across vision-language pre-training datasets. Alpagasus (Chen et al. 2023) tested instruction curation. What's "first" here—the transfer direction (pre-train→fine-tune) or the categorical framework?
- **Counter:** Related Work L46 acknowledges "Existing work optimizes curation per-stage without testing cross-stage transfer." So "first" = transfer testing, not curation taxonomy per se.
- **Verdict:** DEFENSIBLE but should clarify "first *cross-stage transfer* taxonomy" not "first curation taxonomy."

**CLAIM-2: "Categorical separation" with p=0.078 (Results L296, Discussion L349, Conclusion L404)**
- **Challenge:** p=0.078 > 0.05 standard threshold. Paper argues "Cohen's d=10.76 large effect justifies categorical claim despite marginal p-value," but this conflates effect size (how big is the difference) with statistical inference (is it real vs noise). A skeptical reviewer says: "d=10.76 with p=0.078 suggests you're underpowered (small n), not that the separation is categorical."
- **Counter:** Ground truth L139-140 shows non-overlapping 95% CIs [0.30%, 0.46%] vs [4.44%, 5.65%] → this is stronger evidence than p-value alone.
- **Verdict:** OVERSTATED. Should lead with CI non-overlap, de-emphasize p-value, add "production validation with n>5 seeds needed."

**CLAIM-3: "Practitioners can reuse C4 thresholds" (Abstract L3, Intro L20, Conclusion L404)**
- **Challenge:** h-e1 filtered 0.03% of Alpaca (17/52,002 samples), perplexity filtered ZERO. With such minimal filtering, how can you claim threshold transfer is validated? You demonstrated transfer of thresholds that *do almost nothing*.
- **Counter:** h-m1 showed 3.0% penalty when thresholds mismatch (C4→Dolly), validating that transfer matters even if absolute curation effect is small. Also Discussion L372-374 acknowledges "conservative results due to low duplicate burden."
- **Verdict:** DEFENSIBLE but should front-load caveat: "On already-curated datasets (Dolly/Alpaca), transferred thresholds match stage-tuned performance; web-scraped production data with higher noise would show larger absolute effects."

### Unfair Baseline Comparisons

**BASELINE-1: No external method comparison (Phase 5 skipped per L510)**
- **Challenge:** Paper compares Transferred vs Stage-Tuned vs No-Curation, but doesn't compare to existing curation methods (DataComp CLIP-score filtering, Alpagasus ChatGPT scoring, random sampling). How do we know 0.38% transfer delta is good without knowing if random filtering achieves 1% delta?
- **Counter:** Ground truth L513 justifies "Internal comparison (transferred vs. stage-tuned) sufficient for transfer stability measurement." The research question is "does X transfer" not "is X better than Y."
- **Verdict:** ACCEPTABLE for transfer taxonomy, but limits practical impact claims. Can't say "our method is best" only "our thresholds transfer."

**BASELINE-2: Mock evaluation undermines baseline validity**
- **Challenge:** All scores (Table 1, 3, 4, 5) are PREDICTED not measured (Experimental Setup L221-229, Discussion L361-366). How can you claim 0.1% transfer delta when you didn't actually run lm-eval? Predicted scores could be off by ±2%, making 0.38% vs 5.04% separation noise.
- **Counter:** Ground truth L223-226 grounds predictions in "Llama-2 technical report, DataComp results, literature-validated transfer patterns." Effect size d=10.76 is large enough that ±2% prediction error wouldn't erase the gap.
- **Verdict:** MAJOR WEAKNESS but disclosed (Discussion L361-366). Should add: "Predicted scores may vary ±X% from actual; production validation needed to confirm sub-1% precision."

### Missing Limitations

**LIMITATION-1: RLHF untested but claimed in Abstract**
- **Location:** Abstract L2 "Foundation model training pipelines span multiple stages—pre-training, fine-tuning, RLHF"
- **Problem:** Abstract implies all three stages tested, but Scope (Discussion L367-371) restricts to "pre-training → fine-tuning (RLHF untested)."
- **Fix:** Abstract should say "pre-training → fine-tuning pipeline" not list RLHF as if validated.

**LIMITATION-2: Distribution shift boundary untested**
- **Location:** Discussion L410-416 Future Work, but not in Limitations L360-383
- **Problem:** Paper validates C4 (web text) → Dolly (open-domain instructions), moderate shift. Doesn't test high-shift (biomedical, legal, code). Discussion L416 predicts "transfer delta increases with domain distance" but provides no evidence. A reviewer asks: "How do I know your thresholds work for MY domain (radiology reports)?"
- **Fix:** Add to Limitations: "Transfer validated on moderate distribution shift (web→instruction); high-shift domains (biomedical, legal) may require threshold re-tuning."

**LIMITATION-3: Single model scale (7B)**
- **Location:** Ground truth L414 Future Work "Model scale replication (13B, 70B)" but not in paper Limitations
- **Problem:** Llama-2-7B is mid-size. Optimal dedup threshold may vary for 70B models (more capacity → tolerates more duplicates?) or 1B models (less capacity → needs cleaner data?). Paper assumes scale-invariance without evidence.
- **Fix:** Add to Limitations: "Validated at 7B scale; optimal thresholds may vary for smaller (<3B) or larger (>70B) models."

### Tone Overclaiming Beyond Evidence

**TONE-1: "Transfer robustly" repeated without qualification**
- **Locations:** Abstract L2, Intro L12, Results L241, Conclusion L403
- **Problem:** "Robustly" implies tested across many conditions. Paper tests ONE pre-training corpus (C4), TWO fine-tuning datasets (Dolly, Alpaca), ONE model (Llama-2-7B). This is minimal validation, not robust.
- **Fix:** Replace "transfer robustly" with "transfer successfully on tested datasets" or "show stable transfer" (less absolute).

**TONE-2: "Enables practitioners to..." (Intro L20, Conclusion L404)**
- **Problem:** Prescriptive tone ("can reuse C4 thresholds") based on PoC mock evaluation. A practitioner reading this might skip re-tuning, get worse results, and blame the paper.
- **Fix:** Add hedging: "Our results suggest practitioners MAY reuse C4 thresholds for similar web→instruction shifts; high-shift domains require validation."

**TONE-3: Conclusion overstates impact**
- **Location:** L418 "As foundation models continue to scale across training stages—from trillion-token pre-training to specialized fine-tuning to human-aligned RLHF—understanding which data curation decisions transfer will become increasingly critical for efficient development."
- **Problem:** Grand vision paragraph disconnected from actual validation scope (52k samples, 7B model, PoC tier, pre-train→fine-tune only). This is the "future importance" argument that doesn't acknowledge current work is a limited first step.
- **Fix:** Temper with "Our taxonomy provides a first step toward transfer-aware curation design, with production validation needed for trillion-token scale and RLHF stages."

---

## Summary

**Fatal issues:** 0  
**Major issues:** 4
- MAJOR-1: Perplexity filtering methodology-results contradiction (filtered 0 samples but described as active technique)
- MAJOR-2: Dataset count inconsistencies (52k vs 52,002 precision varies)
- MAJOR-3: h-m3 quality bound table mismatch (k=10000 result cited but not shown)
- MAJOR-4: p=0.078 with "categorical separation" claim overstates statistical significance

**Persuasiveness:** CONDITIONAL PASS
- **Passes IF:** Reader accepts PoC tier validation (mock eval) as sufficient for mechanism direction
- **Fails IF:** Reader expects production-grade evidence for prescriptive claims ("practitioners can reuse thresholds")
- **Attention test:** FAILS at Introduction para 3 (jargon frontload), recovers if reader skips to Results
- **Credibility risks:** 
  - Perplexity filtered 0 samples but treated as validated technique
  - p=0.078 oversold as "categorical" separation
  - Mock evaluation disclosed late (Experimental Setup L221, should be in Abstract/Intro)
  - Prescriptive tone ("practitioners can...") exceeds PoC evidence strength

**Recommended fixes priority:**
1. MAJOR-1 (perplexity): Front-load PoC limitation in Methodology, downgrade perplexity from "validated" to "infrastructure-only"
2. MAJOR-4 (p-value): Reframe "categorical" claim as "large effect size suggests discrete categories (d=10.76), pending production validation"
3. Bored reviewer (Intro para 3): Add intuitive example before formalism (I(filter; objective))
4. Tone (Conclusion): Acknowledge limited scope, remove overclaims about "enabling practitioners" until production validation

**Overall verdict:** Mechanism direction is credible (4/4 hypotheses pass, large effect sizes), but prose oversells PoC evidence with prescriptive language. A careful reviewer will accept the taxonomy concept while questioning practical applicability. Fix MAJOR-1 and MAJOR-4 to avoid rejection; fix engagement issues to get past impatient reviewers.
