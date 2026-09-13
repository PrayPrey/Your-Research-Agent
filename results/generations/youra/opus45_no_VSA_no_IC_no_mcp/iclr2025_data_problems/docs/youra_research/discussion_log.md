# Phase 2A Research Discussion Log

## Metadata
- **Gap ID:** Gap-1
- **Gap Title:** Causal Link Between Curation Strategy and Benchmark Score
- **Priority:** PRIMARY (Critical)
- **Generated:** 2026-08-28
- **Architecture:** Self-Contained Tikitaka Loop (Self-Play Mode)

---

## Research Gap Briefing

### Gap Description
**Current State:** Multiple curation pipelines exist (DataComp, Dolma, RedPajama) with reported benchmark scores, but each varies multiple factors simultaneously (data source, filtering threshold, mixing ratio).

**Missing Piece:** Controlled ablation studies that isolate individual curation parameters (e.g., perplexity threshold, dedup rate, domain ratio) while holding others constant.

**Potential Impact:** High - Without this, cannot attribute performance gains to specific curation decisions.

### Key Papers
1. **SELECT: Large-Scale Benchmark of Data Curation Strategies** (arXiv:2410.05057) - Benchmarks curation but image-focused
2. **How to Train Data-Efficient LLMs** (arXiv:2402.09668) - Perplexity filtering analysis
3. **Perplexed by Perplexity: Data Pruning With Small Reference Models** (arXiv:2405.20541) - Questions optimal perplexity thresholds

### Implementation Resources
- togethercomputer/RedPajama-Data - CCNet pipeline with mixed curation
- haolpku/Awesome-LLM-Data-Preparation - Survey companion

### Research Questions Addressed
- Q1: Data filtering/mixing effects on benchmarks
- Q2: Training data quality metrics vs downstream scores

### MANDATORY FEASIBILITY CONSTRAINTS
- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data that does not yet exist
- Reject ideas requiring human evaluation or subjective scoring
- Accept only hypotheses testable with existing real datasets and benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? Instead of asking "which curation strategy is best," we should ask "what is the *dose-response curve* of each curation parameter?" 

Consider this: the field treats perplexity filtering as binary—keep or remove—but what if there's a non-linear sweet spot? The "Perplexed by Perplexity" paper (arXiv:2405.20541) hints that small reference models give inconsistent thresholds. What if we designed a study that treats perplexity threshold as a *continuous variable* and maps its effect surface on downstream tasks?

Here's my wild idea: **Curation Parameter Dose-Response Mapping (CPDR)**. Instead of comparing Pipeline A vs Pipeline B, we:
1. Fix all parameters except ONE (say, perplexity threshold)
2. Train multiple small models (125M-1B) with that parameter varied across 10+ levels
3. Measure benchmark performance across the sweep
4. Repeat for dedup rate, domain ratio, and quality classifier threshold

This is essentially a pharmacological approach to data curation—finding the EC50 (half-maximal effective concentration) equivalent for each curation lever.

Cross-domain connection: This mirrors materials science "composition-property" studies where you vary alloy components systematically. The DataComp benchmark (image-focused) actually uses this approach—we'd be translating it to LLM training.

**Key Points:**
- Treat curation parameters as continuous variables, not discrete choices
- Map dose-response curves for each parameter independently
- Use small models (125M-1B) to make sweeps computationally tractable
- Borrow experimental design from pharmacology/materials science

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's dose-response framing is scientifically elegant, but let me stress-test it. The critical question: **What result would convince us this hypothesis is wrong?**

First, the falsifiability challenge. If we sweep perplexity thresholds and find monotonic improvement (higher threshold = better), the hypothesis of a "sweet spot" is falsified—but that's still useful knowledge. If we find no correlation at all, we've falsified the premise that perplexity filtering matters. Good—these are both informative outcomes.

But here's my methodological concern: **confound control**. When you change perplexity threshold, you implicitly change:
1. Dataset SIZE (stricter filter = fewer samples)
2. Domain DISTRIBUTION (different domains have different perplexity distributions)
3. Sample DIFFICULTY (high-perplexity samples may be harder/easier)

A proper ablation needs to EITHER:
- Match dataset sizes by random subsampling the more permissive sets, OR
- Report metrics normalized by training tokens

Second, what specific, measurable predictions can we make? I propose:
- **Primary prediction:** There exists a non-monotonic (inverted-U) relationship between perplexity threshold and downstream accuracy, with a measurable peak.
- **Falsification criterion:** If monotonic across all 10+ threshold levels (R² > 0.9 for linear fit), the dose-response hypothesis is falsified.
- **Effect size:** The optimal threshold should outperform both extremes (no filtering, aggressive filtering) by >1% on aggregated benchmarks.

The experiment design must use held-out evaluation sets VERIFIED to have no contamination overlap with training variants—Min-K%++ should be run pre-experiment.

**Key Points:**
- Both monotonic and null results are informative falsifications
- Critical confounds: dataset size, domain shift, sample difficulty must be controlled
- Prediction: inverted-U dose-response with measurable peak
- Contamination check mandatory before any benchmark measurement

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: **What makes this genuinely new vs incremental?** Let me assess Dr. Nova's CPDR framework through the lens of scientific contribution.

The honest answer: this is NOT entirely novel. DataComp-LM already demonstrated the value of systematic curation sweeps for multimodal models. The "How to Train Data-Efficient LLMs" paper (arXiv:2402.09668) performed perplexity-based filtering studies. What would be new here?

The genuine contribution would be **transferring the dose-response framework to LLMs with proper confound control**—which Prof. Vera correctly identified as missing in existing work. The innovation isn't the sweep methodology; it's the *controlled* sweep methodology.

This matters because: Current LLM training is largely folk knowledge. Papers report "we filtered at perplexity threshold X" without explaining WHY that threshold. A dose-response study would provide **actionable calibration curves** that practitioners can consult.

However, I have a significance concern: Does this open new research directions, or just fill a gap? I'd argue this is primarily gap-filling—important, but not paradigm-shifting. To elevate impact, the study should:
1. Test whether dose-response curves TRANSFER across model scales (125M → 1B → 7B)
2. Identify INTERACTION effects between parameters (perplexity × dedup)
3. Provide open-source tools for practitioners to generate their own curves

The field impact: This would move data curation from "art" to "engineering"—a valuable but incremental contribution. Not a paradigm shift, but a solid B+ contribution.

**Key Points:**
- Systematic curation sweeps exist for vision (DataComp); LLM version with confound control is the actual novelty
- Significance: gap-filling rather than paradigm-shifting, but practically valuable
- Impact elevation: test cross-scale transfer and parameter interactions
- Contribution level: solid applied research, not breakthrough science

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova proposes training "multiple small models (125M-1B) with parameter varied across 10+ levels." Let me assess whether this can actually work in principle.

**Mechanism soundness:** Yes—sweeping one parameter while controlling others is scientifically valid. The question is whether the signal survives noise at small scales. Empirical evidence from scaling laws literature (Hoffmann et al., Chinchilla) suggests 125M models DO exhibit consistent benchmark behavior when controlled properly. The mechanism is sound.

**Measurement validity:** Here's what worries me. Small model benchmark scores are NOISY. A 125M model on MMLU might give ±3% variance across seeds. If the dose-response effect is <5%, you're buried in noise. The study MUST:
1. Use multiple seeds (≥3) per configuration
2. Report confidence intervals
3. Use benchmarks with high signal at small scales (HellaSwag, ARC-Easy, not MMLU)

**Fundamental barrier:** The confound Prof. Vera identified—dataset size changes with filtering threshold—is the real technical challenge. Two solutions:
- **Fixed-token design:** Train all configurations on exactly N tokens, sampling to fill when strict filtering produces fewer samples. Risk: introduces sampling bias.
- **Efficiency normalization:** Report benchmark/FLOP, not benchmark alone. Risk: adds analysis complexity.

I lean toward fixed-token design as the cleaner approach. It answers "given 10B tokens, what perplexity threshold maximizes performance?"

The proposed interventions CAN work in principle. The approach is feasible.

**Key Points:**
- 125M models do show consistent benchmark behavior when controlled
- High variance at small scales requires multiple seeds and appropriate benchmark selection
- Fixed-token experimental design preferred over efficiency normalization
- Feasibility: APPROVED with the caveats above

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this against the concerns raised! Let me synthesize and propose concrete refinements.

**Addressing Dr. Sage's incremental concern:** The contribution can be elevated from "systematic sweep" to "actionable calibration framework." The deliverable isn't just curves—it's a TOOL. Imagine: `curation-calibrator --model-size 1B --target-task reasoning --budget 10B-tokens` returns recommended parameter ranges. This transforms gap-filling into infrastructure.

**Addressing Prof. Vera's confound control:** The fixed-token design Prof. Pax endorsed solves this cleanly. Additionally, we should stratify analysis by domain to detect if optimal thresholds differ (code vs web text vs books). This turns a confound into a research finding.

**Addressing Prof. Pax's noise concern:** Beyond multiple seeds, I propose using BENCHMARK ENSEMBLES. Instead of single-metric optimization, use principal component of [HellaSwag, ARC-Easy, PIQA, WinoGrande]. This captures "general reasoning" and reduces benchmark-specific noise.

**What evidence supports this framework?** 
- Scaling laws (Chinchilla) show small models predict large-model behavior
- DataComp image studies successfully identified curation optima with similar methodology
- The "Data-Efficient LLMs" paper showed perplexity filtering effects exist—we're just mapping them precisely

**Refined hypothesis formulation:**

> **H1 (CPDR):** For LLM training, each curation parameter (perplexity threshold, deduplication rate, domain mixing ratio) exhibits a non-monotonic dose-response relationship with downstream benchmark performance, with a quantifiable optimal range that transfers across model scales (125M→1B).

**Key Points:**
- Elevate from curves to actionable calibration tool
- Fixed-token design + domain stratification addresses confounds
- Benchmark ensemble reduces noise while measuring generalization
- Evidence: scaling laws literature, DataComp precedent, prior filtering studies

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me find the flaws before reviewers do.

**Flaw 1: Cross-scale transfer assumption is unvalidated.** H1 claims optimal thresholds "transfer across model scales (125M→1B)." Show me the evidence. Scaling laws show loss curves transfer, NOT that optimal curation parameters transfer. In fact, there's reason to believe larger models are more robust to data noise—meaning optimal thresholds might SHIFT with scale. The hypothesis must either:
- Remove cross-scale transfer as a core claim (test it as secondary hypothesis), OR
- Cite evidence that curation optima transfer (I don't see this in the literature)

**Flaw 2: "Non-monotonic" is a strong assumption.** Why assume inverted-U? The null hypothesis should be monotonic improvement with stricter filtering. The experiment should be designed to DETECT the shape, not assume it. Rephrase: "determine the functional form of the dose-response relationship."

**Flaw 3: No baseline comparison.** What would we compare CPDR-optimized curation to? The value proposition requires showing that CPDR-selected parameters outperform:
- Random baseline (no filtering)
- Literature baseline (thresholds from existing papers like RedPajama)
- Auto-selection baseline (let model pick its own data via influence functions)

Without these baselines, we just have curves—no actionable finding.

**What would convince me this is valid:**
1. At least one parameter shows non-monotonic response (proves dose-response concept)
2. Optimal parameters outperform at least one reasonable baseline by >2%
3. If cross-scale transfer is claimed, validate on at least 2 model sizes

**Key Points:**
- Cross-scale transfer is claimed but unvalidated—demote to secondary hypothesis
- Remove "non-monotonic" assumption—detect shape empirically instead
- Must include baselines: no-filter, literature values, potential auto-selection
- Success criterion: non-monotonic response for ≥1 parameter, >2% baseline improvement

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critiques are fair—and they've sparked a refinement that makes this STRONGER. Let me build on them.

**On cross-scale transfer:** Rex is right that this is unvalidated. But here's the creative pivot: instead of claiming transfer, we make **transfer itself the hypothesis**. 

New formulation: "At what model scale does the optimal curation threshold stabilize?" This is MORE novel—it addresses the scaling law community directly. We'd train at 125M, 350M, 1B and ask: do optima converge? This answers whether small-model calibration can guide large-model training.

**On functional form:** Agreed—we shouldn't assume inverted-U. The study becomes: "Characterize the dose-response functional form." Polynomial regression with model selection (AIC/BIC) can determine if it's linear, quadratic, or more complex. If it IS monotonic, we've falsified the "sweet spot" hypothesis but proven a valuable result: "more filtering is always better up to [threshold]."

**On baselines:** Prof. Rex is exactly right. Let me propose the baseline set:
1. **No filtering** (raw data)
2. **RedPajama defaults** (perplexity threshold from their paper)
3. **DataComp-LM defaults** (if available for text)
4. **CPDR-optimized** (our approach)

The action item is clear: CPDR must beat at least 2 of these to be useful.

**Emerging hypothesis (refined):**

> **H1v2:** For LLM pretraining, curation parameters (perplexity threshold, deduplication rate) exhibit quantifiable dose-response relationships with benchmark performance. The optimal parameter values (a) can be empirically determined via systematic sweep, (b) outperform literature defaults by a measurable margin (>1%), and (c) may or may not transfer across model scales—which itself is a testable secondary hypothesis.

This is now EMPIRICALLY GROUNDED, FALSIFIABLE, and PRACTICALLY ACTIONABLE.

**Key Points:**
- Pivot: make cross-scale transfer a TESTABLE question, not an assumption
- Functional form: use model selection to detect shape (linear/quadratic/other)
- Baseline set: no-filter, RedPajama, DataComp-LM, CPDR-optimized
- Refined hypothesis removes unvalidated assumptions

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The refined hypothesis H1v2 is substantially more rigorous. Let me formalize the experimental protocol to ensure it meets my standards.

**Experimental Design:**

**Independent Variables:**
1. Perplexity threshold (10 levels: no filter, p10, p20...p90)
2. Deduplication rate (5 levels: none, fuzzy 0.7, fuzzy 0.85, exact, exact+fuzzy)
3. Model size (3 levels: 125M, 350M, 1B) — for cross-scale analysis

**Dependent Variables:**
- Primary: Benchmark ensemble PC1 (HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Secondary: Individual benchmark scores for diagnostic

**Controls:**
- Fixed training token budget (10B tokens per configuration)
- Fixed training hyperparameters (lr schedule, batch size)
- Fixed evaluation sets verified no overlap via Min-K%++
- 3 seeds per configuration

**Protocol:**
1. Download base corpus (C4 or RedPajama-v2)
2. Pre-compute perplexity scores with KenLM 5-gram trained on Wikipedia
3. Pre-compute deduplication clusters with MinHash
4. For each (threshold, dedup) configuration: sample 10B tokens, train 125M model, evaluate
5. Repeat at 350M, 1B for promising configurations (cost-saving: not full factorial)

**Falsification Criteria:**
- If ALL parameter sweeps show R² > 0.9 for monotonic fit: "sweet spot" hypothesis falsified
- If NO configuration beats RedPajama defaults by >1%: CPDR value proposition falsified
- If 125M optima differ from 1B optima by >20% threshold units: cross-scale transfer falsified

**This meets my standards.** The experiment is designed to fail in informative ways.

**Key Points:**
- Full factorial for 125M; selective replication at larger scales
- Fixed 10B token budget eliminates dataset size confound
- Min-K%++ contamination check before evaluation
- Clear falsification criteria for each sub-hypothesis

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me reassess significance now that the hypothesis has been refined.

**Contribution upgrade:** H1v2 is now a METHODOLOGICAL contribution with practical deliverables. The novelty claims I can support:
1. **First controlled dose-response study for LLM curation parameters** (perplexity, deduplication)
2. **Actionable calibration curves** that practitioners can use
3. **Empirical test of cross-scale transfer** for curation optima

This IS more significant than my initial B+ assessment. Why? Because it addresses the reproducibility crisis in LLM training. Papers say "we filtered at threshold X" without justification. This study would provide the FIRST principled guidance.

**Field impact reassessment:**
- If dose-response is non-monotonic: changes how practitioners think about curation (they're currently guessing)
- If cross-scale transfer fails: changes methodology (can't use small models to calibrate large ones)
- Either outcome advances the field

**Remaining concern:** The study uses C4/RedPajama corpus. Results may not transfer to specialized domains (code, multilingual). The paper should explicitly scope to "English web text" and note domain extension as future work.

**My verdict: This opens new research directions.** Specifically:
- Domain-specific dose-response studies
- Automated curation optimization
- Interaction effects between parameters

**Upgraded assessment: A- contribution.** Not paradigm-shifting, but a genuine methodological advance that practitioners will cite.

**Key Points:**
- Contribution upgraded: first controlled LLM curation dose-response study
- Addresses reproducibility crisis in data preparation
- Both positive and null results advance the field
- Scope limitation: English web text; domain extension as future work

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility assessment on the refined protocol.

**Training budget check:** Prof. Vera's protocol calls for:
- 10 perplexity levels × 5 dedup levels × 3 seeds = 150 runs at 125M
- Say 5 configurations at 350M, 3 at 1B for validation
- At 10B tokens per run: ~1.5T tokens total training

This is feasible for a well-resourced academic group or industry lab, though it's a significant investment. The design is technically sound—this is implementation detail, not a fundamental barrier.

**Scientific soundness check:**
✅ Mechanism is valid (parameter sweeps reveal relationships)
✅ Measurement is valid (benchmark ensembles reduce noise)
✅ Interventions work in principle (filtering/dedup are standard operations)
✅ Controls are appropriate (fixed tokens, fixed hyperparams, contamination check)

**No fundamental barriers remain.** All Prof. Vera's confound controls are implementable. KenLM perplexity computation is standard. MinHash deduplication is standard. The benchmarks selected have sufficient signal at 125M scale.

**One refinement:** The study should report compute efficiency curves as supplementary analysis. Even if we control for token count, practitioners care about wall-clock efficiency. A Pareto frontier of (quality, filtering cost) would add practical value.

**Feasibility verdict: APPROVED.** The study is technically implementable and scientifically sound.

**Key Points:**
- ~150 training runs at 125M scale; validation at larger scales
- All components (KenLM, MinHash, benchmarks) are standard and available
- No fundamental barriers; implementation is straightforward
- Suggest adding Pareto efficiency analysis as supplementary

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've converged on a strong hypothesis. Let me synthesize the final formulation.

**FINAL HYPOTHESIS (H1-CPDR):**

**Core Claim:** For LLM pretraining on English web text, data curation parameters (perplexity filtering threshold, deduplication stringency) exhibit quantifiable dose-response relationships with downstream benchmark performance. These relationships can be empirically mapped through controlled ablation, and the resulting optimal parameter values outperform literature defaults.

**Mechanism:** 
1. Low perplexity thresholds include noisy/irrelevant data that dilutes learning signal
2. High perplexity thresholds exclude too much data, reducing coverage and diversity  
3. An optimal range exists that balances quality and diversity
4. This optimal range can be determined empirically through systematic sweep

**Testable Predictions:**
- P1: At least one curation parameter shows non-monotonic (concave) dose-response curve with measurable peak
- P2: CPDR-optimized parameters outperform RedPajama defaults by >1% on benchmark ensemble
- P3: Optimal parameters at 125M scale are within ±20% of optima at 1B scale (cross-scale transfer)

**Falsification:**
- P1 falsified if ALL parameters show R² > 0.9 monotonic fit
- P2 falsified if no configuration beats RedPajama by >1%
- P3 falsified if optima differ by >20% across scales

**Experimental Approach:**
- Fixed 10B token budget per configuration
- 10 perplexity × 5 deduplication × 3 seeds at 125M
- Validation at 350M, 1B
- Benchmark ensemble: HellaSwag, ARC-Easy, PIQA, WinoGrande
- Min-K%++ contamination verification

**Novelty:** First controlled dose-response study for LLM curation parameters with proper confound control.

**Scope:** English web text (C4/RedPajama-v2). Domain extension as future work.

**Key Points:**
- Core claim: quantifiable dose-response relationships exist and can be mapped
- Three testable predictions with clear falsification criteria
- Methodology: controlled ablation with fixed-token design
- Scope bounded to English web text

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress-test before I sign off.

**Remaining concerns addressed:**
✅ Cross-scale transfer now TESTABLE (P3), not assumed
✅ Non-monotonicity now DETECTABLE, not assumed
✅ Baselines included (RedPajama defaults)
✅ Confounds controlled (fixed tokens, multiple seeds)
✅ Falsification criteria clear for all predictions

**What would still convince me more:**
1. Adding a second baseline beyond RedPajama (e.g., "no filtering at all") would strengthen the value proposition
2. The effect size threshold (>1%) is conservative—this is good for publishability but may miss smaller effects worth knowing

**Accepted trade-offs:**
- Scope limitation to English web text is reasonable for a first study
- Focus on 2 parameters (perplexity, dedup) is manageable; 3+ parameters create combinatorial explosion

**My final assessment:** The hypothesis is now BULLETPROOF for its stated scope. The predictions are clear, falsifiable, and informative in all outcomes. The methodology is sound.

**Remaining objections:** None that would block proceeding. The two items above are "nice to haves."

**Verdict: APPROVED.** This hypothesis is ready for Phase 2B experimental design.

**Key Points:**
- All major concerns from previous exchanges have been addressed
- Minor suggestions: add no-filter baseline, note effect size conservatism
- Trade-offs accepted: scope to English web, 2 parameters
- Hypothesis approved for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** MODERATE
- **Assessment:** The dose-response framework itself is not novel—it exists in pharmacology and was adapted for vision models in DataComp. The novelty lies in (1) applying it to LLM curation parameters with proper confound control, and (2) testing cross-scale transfer as a hypothesis rather than assumption. This is methodological translation rather than conceptual innovation, but the resulting calibration tools would be genuinely new infrastructure for the field.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** H1-CPDR has exceptionally clear falsification criteria. Each of the three predictions (P1-P3) has quantitative thresholds for rejection. The experimental design includes appropriate controls (fixed tokens, multiple seeds, contamination checks) and the protocol is reproducible. Both positive and null results would be informative—this is exactly what rigorous science should look like.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE-STRONG
- **Assessment:** This addresses a genuine gap—the lack of principled guidance for LLM curation parameter selection. The field currently operates on folk wisdom ("RedPajama used threshold X"). However, the contribution is primarily practical/methodological rather than theoretical. Impact is high for practitioners but limited theoretical depth. A- contribution: solid, useful, will be cited, but not paradigm-shifting.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed methods are technically implementable with standard tools (KenLM, MinHash, standard benchmarks). The controlled ablation design is scientifically sound. No fundamental barriers exist. The main consideration is computational budget (~150 training runs at 125M), which is substantial but feasible for motivated groups. The study can definitely be executed.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **H1-CPDR (Curation Parameter Dose-Response)**, a hypothesis that data curation parameters for LLM pretraining exhibit quantifiable dose-response relationships with downstream performance. 

The core claim is that perplexity filtering threshold and deduplication stringency have optimal ranges that can be empirically determined through systematic ablation. The mechanism posits that too-permissive filtering includes noise that dilutes signal, while too-strict filtering loses diversity—creating an optimal balance point.

Three testable predictions emerged: (P1) at least one parameter shows non-monotonic response with a measurable peak, (P2) CPDR-optimized parameters beat RedPajama defaults by >1%, and (P3) optimal values at 125M scale are within ±20% of optima at 1B scale. Each has clear quantitative falsification criteria.

The experimental approach uses fixed 10B token budgets with 10 perplexity levels × 5 deduplication levels × 3 seeds at 125M scale, with validation at larger scales. Benchmark ensemble (HellaSwag, ARC-Easy, PIQA, WinoGrande) reduces noise. Min-K%++ verifies no contamination.

The hypothesis addresses the research gap of missing controlled ablations for LLM curation. It's scoped to English web text with domain extension as future work. The contribution is methodological—first controlled dose-response study for LLM curation—providing actionable calibration infrastructure for practitioners.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Adding a "no filtering" baseline would strengthen the value proposition beyond just beating RedPajama
- The >1% effect size threshold is conservative—smaller effects might still be worth documenting
- **Mitigation Strategy:** Include no-filter baseline in the experimental design; report full curves even if effect sizes are smaller than threshold
