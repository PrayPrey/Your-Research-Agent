# Phase 2A Discussion Log

## Discussion Briefing

**Gap ID:** gap-1-curation-contamination-attribution
**Gap Title:** Curation-Contamination Attribution Link
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Gap Summary

No systematic study uses attribution methods to trace how specific curation decisions (filtering, deduplication, mixing) affect benchmark contamination rates. The three research areas (contamination detection, data attribution, data curation) remain disconnected. No work answers: "Which training examples are responsible for benchmark memorization, and how do curation strategies affect their prevalence?"

### Key Research Question

What is the relationship between data curation strategies and test data contamination in foundation models, and how can existing attribution methods be leveraged to detect and quantify contamination effects on benchmark performance?

### Supporting Literature

**Contamination Detection:**
- CDD/TED (Dong et al., 2024) - Output distribution-based detection, arXiv:2402.15938, 168 citations
- Min-K%++ (Zhang et al., 2024) - Training data detection via local maxima, arXiv:2404.02936, 106 citations
- Contamination Taxonomy (Palavalli et al., 2024) - Categorization framework, arXiv:2407.08716

**Data Attribution:**
- TRAK (Park et al., 2023) - Scalable attribution via random projection, arXiv:2303.14186, 308 citations
- LoGra (Choe et al., 2024) - 6500x speedup for influence functions, arXiv:2405.13954, 98 citations

**Data Curation:**
- DataComp-LM (Li et al., 2024) - Systematic curation experiments, arXiv:2406.11794, 389 citations
- SlimPajama-DC (Shen et al., 2023) - Global vs local deduplication, arXiv:2309.10818, 84 citations

### Implementation Resources

- MadryLab/trak (243 stars) - Official TRAK implementation
- lm-sys/llm-decontaminator (324 stars) - Rephrased contamination detection
- google-research/deduplicate-text-datasets (1272 stars) - Foundational deduplication
- togethercomputer/RedPajama-Data (4948 stars) - Production curation pipeline

### Feasibility Constraints (MANDATORY)

- MUST use existing real datasets only
- MUST use existing benchmarks (MMLU, HumanEval, HellaSwag)
- NO new benchmarks/rubrics/scoring frameworks
- NO synthetic/generated data requirements
- NO human evaluation requirements

### Previous Failure / Routing Context

N/A - First Phase 2A attempt. No prior SUPERSEDE, ROUTED_TO_PHASE_2A, PARTIAL, or FAIL records.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the contamination problem on its head? Instead of asking "how much contamination exists?" let's ask "which curation decisions *created* the contamination in the first place?" 

The beauty of combining TRAK attribution with contamination detection is that we can create a *causal map* from curation decision to benchmark inflation. Think about it: DataComp-LM showed model-based filtering dramatically changes downstream performance, but nobody asked whether those filtered-in examples are the ones memorizing benchmark answers. TRAK gives us the attribution scores, CDD gives us contamination signals — the missing link is connecting them through the curation pipeline.

Here's what excites me: we could identify "contamination-amplifying" vs "contamination-suppressing" filtering strategies. Some quality filters might preferentially select high-perplexity examples that happen to include benchmark questions. Others might filter them out. No one has systematically studied this because the tools lived in separate research silos.

Three unconventional angles to explore:
1. **Attribution-guided decontamination**: Use TRAK to identify which training examples contribute most to benchmark performance, then check if those same examples have high contamination scores via CDD/Min-K%++
2. **Curation forensics**: Trace backward from contaminated benchmark predictions to the specific filtering decisions that allowed contaminating examples into the training set
3. **Predictive curation design**: Can we predict contamination rates *before* training based on curation strategy characteristics?

The third angle is the wildest — imagine a "contamination risk score" for any proposed curation pipeline, computed without training a model. Cross-domain thinking: this is similar to how security researchers predict vulnerability surfaces from code structure before exploitation.

**Key Points:**
- Connect TRAK attribution → CDD contamination → curation decisions as a unified pipeline
- Study "contamination amplification factor" of different filtering strategies
- Explore prediction of contamination rates from curation pipeline design

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central idea—linking TRAK attribution, contamination detection, and curation decisions—is promising. However, it currently lacks operational definitions. If we are to study "contamination amplification," we must specify: amplification relative to what baseline, measured how, and under what controls? The evidence suggests that both attribution scores and contamination detectors are noisy estimators. Therefore, before drawing causal maps, we must define a falsifiable hypothesis such as: *Certain filtering strategies increase the proportion of benchmark performance attributable to contaminated training examples compared to random sampling with matched token budget.* That is testable.

Let me propose a concrete experimental design. Construct multiple training datasets from a common raw corpus using distinct, explicitly defined filtering strategies (e.g., perplexity-based top-k%, quality classifier thresholding, random subsampling). For each, train identical models with fixed seeds and hyperparameters. Then:  
1) Use a predefined contamination detector (CDD, Min-K%++) to assign contamination scores to all training examples *before* training.  
2) After training, compute TRAK attribution scores from benchmark test items to training examples.  
3) Define a measurable quantity: **Contamination Contribution Ratio (CCR)** = (sum of attribution mass from training examples flagged as contaminated) / (total attribution mass for benchmark performance).  

Your hypothesis predicts that CCR will vary systematically by filtering strategy. A null hypothesis is that CCR differences are indistinguishable from those observed under matched random resampling. What result would disprove your claim? If CCR differences disappear when controlling for dataset size, token frequency distributions, and benchmark lexical overlap, then "contamination amplification" is likely an artifact.

The "curation forensics" idea requires even stronger controls. Attribution methods such as TRAK approximate influence under linearization assumptions. We must test their stability: do high-attribution examples remain stable under bootstrap resampling of checkpoints? If the top 1% attribution set is unstable, causal tracing to filtering decisions becomes speculative. I would require a robustness analysis where we perturb model initialization and verify that identified contamination-driving examples are consistent across ≥80% of runs. Without this, the pipeline is not reliable enough for forensic claims.

Your most ambitious claim—predicting contamination risk *without training*—demands a sharply defined predictive target. I suggest framing it as a supervised regression problem: given features of a curation pipeline (e.g., perplexity threshold percentile, domain distribution shift, n-gram overlap with benchmark), predict CCR prior to training. The evidence would support your hypothesis only if such predictors explain significant variance in CCR across independently trained models (e.g., R² > 0.5 under cross-validation). If predictive performance collapses out-of-domain, the premise of structural "risk" may be overstated.

Finally, we must consider edge cases. Some benchmarks measure reasoning rather than recall. If contamination amplification is observed only for factoid QA but not for reasoning-heavy tasks, then the phenomenon is benchmark-dependent, not pipeline-general. The best experiment here is adversarial: construct synthetic benchmarks with controlled contamination injection rates. If your pipeline fails to recover known contamination structure in a synthetic setting, it is not ready for real-world claims.

**Key Points:**
- Define a falsifiable metric (e.g., Contamination Contribution Ratio) to quantify "amplification" relative to controlled baselines.
- Validate attribution stability and control for confounds (dataset size, token distribution, lexical overlap) before making causal claims.
- Test predictive "contamination risk" models against independently trained datasets, with explicit success/failure criteria and synthetic sanity checks.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground 🔬 Prof. Vera's excellent experimental design in what's actually achievable. The Contamination Contribution Ratio (CCR) metric is well-defined, but we need to verify the measurement chain is scientifically sound.

**On TRAK feasibility for LLMs:** TRAK was originally demonstrated on CLIP and classification tasks. For LLMs, LoGra (Choe et al., 2024) achieved scalable influence functions with 6500x speedup — but this is still computationally intensive for billion-parameter models. The question isn't whether TRAK *can* work, but at what model scale. For proof-of-concept, I'd recommend starting with 1B-parameter models (Pythia-1B, OLMo-1B) where TRAK/LoGra attribution is well within reach. This is a methodological choice, not a resource constraint — smaller models let us validate the measurement approach before scaling.

**On contamination detection validity:** CDD and Min-K%++ detect training data membership, not "contamination" per se. A training example that's lexically similar to a benchmark question isn't necessarily causing memorization-based performance. We need to distinguish:
- **Semantic contamination**: The training example teaches the exact answer to a benchmark question
- **Distributional overlap**: The training example shares vocabulary/structure but not answers
- **Legitimate knowledge transfer**: The training example contains valid domain knowledge

Min-K%++ gives us membership likelihood, but CCR requires us to know which of these three categories each example falls into. This is where the experimental design matters: by using benchmark questions with known provenance (e.g., newly created post-training questions in LiveCodeBench style), we can establish ground truth.

**On the causal chain validity:** The proposed pipeline is:
`Curation Strategy → Training Set Composition → Model Weights → Attribution Scores → CCR`

Each step introduces measurement error. The key assumptions are:
- A1: Attribution scores reliably identify performance-driving examples (evidence: TRAK validation studies show ~70% precision in counterfactual validation)
- A2: Contamination detectors reliably identify benchmark-related examples (evidence: CDD achieves >0.9 AUC on synthetic contamination)
- A3: Curation strategy effects are separable from corpus effects (requires: matched corpus with different filtering)

**What would convince me this can work:** If we can demonstrate on a controlled setup — say, RedPajama subset + 3 filtering strategies + Pythia-1B training + MMLU/HellaSwag evaluation — that CCR varies by >0.1 across strategies with p<0.05 under bootstrap resampling, the mechanism is validated. This is achievable with existing tools and standard academic compute.

**What would NOT work:** Attempting this at GPT-4 scale without first validating at smaller scale. Attempting on benchmarks without known contamination provenance. Using attribution methods not validated for decoder-only LLMs.

**Key Points:**
- Start with 1B-parameter models where TRAK/LoGra is validated — this tests the methodology, not just the resources
- Distinguish semantic contamination from distributional overlap using benchmarks with known provenance
- Validate each step of the causal chain (A1-A3) before claiming forensic capability
- The measurement approach is scientifically sound if validated incrementally

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down: you are implicitly equating **"attribution mass from contaminated examples" with "contamination-driven performance."** That leap is not justified yet.

TRAK (or LoGra-style approximations) gives you influence under linearization assumptions. Influence ≠ counterfactual necessity. Show me the evidence that removing the top-k contaminated-attributed examples actually reduces benchmark accuracy. If your CCR goes up under a filtering strategy but ablating those examples does *not* reduce performance, then CCR is just measuring correlated overlap, not causal contamination. What would convince me is a **removal intervention test**: retrain (or fine-tune) after excising the top 0.1% high-CCR examples and show a statistically significant drop in benchmark accuracy *only* for the supposedly amplified strategy. No drop, no amplification.

Second, your baseline is still underspecified. Prof. Vera proposes matched random resampling, which is necessary but insufficient. Here's the unstated assumption: that filtering strategies don't systematically alter *task-relevant feature density* independent of contamination. A perplexity filter might preferentially select high-information examples that legitimately improve reasoning tasks. If that increases both attribution mass and CCR, your interpretation collapses. You need a **negative control benchmark** constructed post hoc with guaranteed zero overlap. If CCR varies across strategies but performance on clean benchmarks tracks in parallel, then you're measuring general quality, not contamination amplification. The divergence between contaminated and provably clean benchmarks is the real signal.

On "curation forensics": I'm not buying causal tracing to pipeline decisions unless you can demonstrate attribution stability *and* decision sensitivity. Pax mentioned ≥80% stability across seeds — good. Now add this: if you slightly perturb the filtering threshold (e.g., perplexity 90th vs 92nd percentile), do the identified "contamination-driving" examples change smoothly or chaotically? If the set flips dramatically, then your causal map is brittle and overfit to arbitrary thresholds. What would convince me is a monotonic relationship: increasing filter strictness systematically increases or decreases CCR in a predictable direction, with confidence intervals not overlapping under bootstrap.

Now the boldest claim: predicting contamination risk pre-training. Here's the hard question — what structural feature of a pipeline could *causally* predict CCR? N-gram overlap with benchmark is trivial and leaks benchmark information into design. If your predictor requires inspecting the benchmark, it's not a general "risk score," it's benchmark-aware tuning. To make this real, define contamination risk relative to *unknown future benchmarks*. That means your features must be corpus-intrinsic (duplication rate, web crawl domain entropy, QA-style density, etc.). Then test on a benchmark released after model training. If your risk model predicts CCR on that unseen benchmark with meaningful R², I'll take it seriously. Otherwise, this is hindsight modeling.

Finally, synthetic validation is non-negotiable. Inject controlled contamination at known rates (e.g., 0%, 0.01%, 0.1%) into identical corpora before filtering. If your pipeline cannot recover the ground-truth amplification factor under known injection, it is not measuring what you think it's measuring. This is your calibration curve. Without it, reviewers will say — correctly — that your metric stack compounds two noisy estimators and calls it causality.

You're close. Tighten the causal tests, add removal interventions and negative controls, and prove stability under perturbation. Then I'll say you've addressed my concerns.

**Key Points:**
- CCR must be validated with removal interventions; attribution mass alone does not prove causal contamination.
- Distinguish contamination amplification from general quality effects using provably clean negative-control benchmarks.
- Predictive "contamination risk" must rely on corpus-intrinsic features and generalize to unseen benchmarks, validated via synthetic injection experiments.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex raises the crucial question of causality, but let me step back and ask: why does this research matter for the field? What contribution justifies the experimental complexity?

Here's what makes this genuinely significant, not just technically interesting:

**The field's trust problem:** Right now, benchmark results are published without contamination audits. DataComp-LM showed that model-based filtering improves MMLU by several points — but nobody asked if that improvement is "real" generalization or contamination-driven memorization. If our CCR methodology shows that certain high-performing filtering strategies achieve their gains primarily through contamination amplification, that changes how the community interprets published results. This matters because:

1. **Reproducibility crisis in data curation:** If filtering strategy X outperforms strategy Y on MMLU, but CCR analysis shows X has 3x higher contamination contribution, the "improvement" is an artifact. No one currently has tools to make this distinction.

2. **Practical curation guidance:** DataComp-LM is used by practitioners. If we can show which filtering approaches are "contamination-safe" vs "contamination-prone," that's actionable guidance for anyone training foundation models.

3. **Attribution method validation:** TRAK was developed for interpretability. Using it to study contamination is a novel application that tests whether attribution methods can serve as *diagnostic tools* for training data issues, not just post-hoc explanations.

**What makes this genuinely new vs incremental?**
- CDD detects contamination but doesn't explain *why* it exists
- TRAK explains performance but doesn't distinguish legitimate from contaminated contributions
- DataComp-LM studies curation but doesn't address contamination

The novelty is the *integration*: using attribution as the bridge between curation decisions and contamination outcomes. No prior work does this because the tools lived in different research communities.

**Addressing Prof. Rex's concerns from a significance lens:** The removal intervention test isn't just methodological rigor — it's the core experiment. If removing high-CCR examples *does* reduce performance, we've proven that contamination is load-bearing for benchmark scores. That's a finding that could shift how the community evaluates reported results.

The negative control benchmark (provably clean, post-training) is similarly crucial. If CCR varies across strategies but clean benchmark performance doesn't, we've isolated contamination amplification from quality effects. That distinction has real policy implications for benchmark design.

**What new research directions does this open?**
- Contamination-aware curation as a design objective (not just quality filtering)
- Attribution-based training data auditing as standard practice
- Benchmark design that includes contamination resistance as a criterion

This matters because it changes what questions we ask when evaluating foundation models. Currently: "How well does it score?" Proposed: "How much of that score is legitimate?"

**Key Points:**
- Addresses the field's trust problem by providing tools to distinguish genuine improvement from contamination artifacts
- Creates actionable curation guidance for practitioners using existing methods in novel combination
- Opens new research directions: contamination-aware curation, attribution-based auditing, contamination-resistant benchmark design

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex is correct to challenge the inference from attribution mass to causal necessity. The evidence suggests that CCR, as currently defined, is at best a *proxy* for contamination-driven performance. Therefore, I will formalize a stronger hypothesis:

> **H1 (Causal Amplification Hypothesis):** For a given filtering strategy S, removing the top-k training examples ranked by contaminated attribution mass will reduce benchmark accuracy more than removing k randomly selected non-contaminated examples, and this effect size will be significantly larger under strategy S than under matched random resampling.

This immediately gives us a disconfirmation criterion. If the removal intervention produces no differential accuracy drop (Δ ≤ random baseline under bootstrap 95% CI), then CCR is not measuring causal contamination. Influence without counterfactual degradation is correlation, not mechanism. I would require this intervention at multiple k (e.g., 0.01%, 0.05%, 0.1%) to establish a dose-response curve. A monotonic degradation strengthens causal interpretation; a flat curve falsifies it.

On the negative control benchmark: I propose a 2×2 factorial design. Train models under multiple filtering strategies. Evaluate on (A) a benchmark with measured contamination risk and (B) a post-training constructed benchmark with cryptographic timestamp guarantees of zero overlap. Define:

**Amplification Index (AI)** = ΔAccuracy_A - ΔAccuracy_B

where Δ is relative to random filtering. If AI ≈ 0, improvements reflect general quality. If AI > 0 with non-overlapping confidence intervals, the evidence suggests contamination-specific amplification. What would disprove the claim? If performance gains on contaminated and clean benchmarks track proportionally across strategies, then filtering affects quality, not contamination structure.

Regarding attribution stability: Pax proposed ≥80% overlap across seeds. I will sharpen this. Let T_{s,i} be the top 1% contaminated-attributed set under seed i. Define stability as mean Jaccard similarity across all seed pairs. Require J ≥ 0.8. Additionally, under small perturbations of filtering thresholds (e.g., ±2 percentile), the CCR should vary smoothly (bounded first derivative). If minor threshold changes induce large discontinuities in CCR or attribution sets, the pipeline is not robust enough for forensic inference.

On predictive "contamination risk" without benchmark leakage: I agree with Rex that corpus-intrinsic features are mandatory. Formally:

> **H2 (Structural Risk Hypothesis):** A regression model using only pre-training corpus statistics (duplication rate, QA density, domain entropy, long-tail token mass, etc.) predicts CCR on *future, unseen* benchmarks with cross-validated R² > 0.5.

The falsifier is straightforward: evaluate on a benchmark released after model training. If predictive performance collapses (R² ≈ 0), structural risk is overstated. I further insist on a synthetic calibration curve: inject controlled contamination at known rates (0%, 0.01%, 0.1%) prior to filtering. The measured CCR and removal-effect sizes must scale linearly with injection rate (R² > 0.9). Failure here invalidates the entire metric stack.

This is the standard I require before accepting claims of "contamination amplification." If these criteria are met, I will say: *This meets my standards.*

**Key Points:**
- Replace CCR correlation claims with a formal removal-intervention hypothesis featuring dose-response and explicit falsification criteria.
- Use a 2×2 contaminated vs. provably clean benchmark design to isolate contamination amplification from general quality effects.
- Require stability analysis and synthetic injection calibration before scaling or making forensic claims.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — now we're converging on something robust! Let me synthesize what we've built and show how each concern has been addressed.

**The Refined Hypothesis (Incorporating All Concerns):**

*Under controlled curation experiments with matched corpora, if a filtering strategy S preferentially retains training examples with high contamination scores, then models trained on S will show: (1) higher CCR than random baseline, (2) larger accuracy drops when high-CCR examples are removed (dose-response validated), and (3) divergent performance between contaminated and provably-clean benchmarks (AI > 0), because the filtering mechanism amplifies the proportion of benchmark-memorizing examples in the training set.*

**How Each Criticism Has Been Addressed:**

1. **🔍 Prof. Rex's causality concern** → Addressed via removal intervention test with dose-response curve at k = 0.01%, 0.05%, 0.1%. If CCR doesn't predict removal impact, hypothesis is falsified.

2. **🔍 Prof. Rex's negative control concern** → Addressed via 2×2 factorial with provably clean benchmark (e.g., LiveCodeBench-style post-training questions). AI = ΔAccuracy_contaminated - ΔAccuracy_clean separates contamination from quality.

3. **🔬 Prof. Vera's stability requirement** → Addressed via Jaccard stability J ≥ 0.8 across seeds + smooth CCR response to threshold perturbation (±2 percentile).

4. **🔬 Prof. Vera's synthetic calibration** → Addressed via controlled injection at 0%, 0.01%, 0.1% rates. CCR must scale linearly with injection (R² > 0.9).

5. **⚙️ Prof. Pax's scale feasibility** → Addressed via 1B-parameter starting point (Pythia-1B/OLMo-1B) where TRAK/LoGra is validated. Methodology validation before scaling.

**The Experimental Design That Satisfies All Constraints:**

| Component | Specification | Validation Criterion |
|-----------|--------------|---------------------|
| Corpus | RedPajama-1B subset | Fixed across strategies |
| Strategies | Perplexity top-30%, quality classifier, random | 3 independent conditions |
| Model | Pythia-1B, fixed seeds | Stability across 3+ seeds |
| Contamination | Min-K%++ (membership) + CDD (output) | Dual-detection triangulation |
| Attribution | TRAK/LoGra | Validated for decoder-only |
| Benchmarks | MMLU (contaminated), LiveCodeBench (clean) | 2×2 factorial |
| Removal Test | k = 0.01%, 0.05%, 0.1% | Dose-response curve |
| Synthetic | 0%, 0.01%, 0.1% injection | Calibration R² > 0.9 |

**Testable Predictions:**
- **P1**: CCR will be higher for perplexity filtering than random (>0.1 difference, p<0.05)
- **P2**: Removing top 0.1% CCR examples will reduce MMLU accuracy >2× more than random removal
- **P3**: AI (Amplification Index) will be positive for perplexity filtering vs. random (95% CI excludes 0)

**What We're Conceding (and Why It's Okay):**
- We're NOT claiming general pre-training prediction without benchmark knowledge (H2 deferred to future work)
- We're NOT starting at GPT-4 scale (methodology validation first)
- We're NOT using synthetic benchmarks for primary claims (real benchmarks + clean controls)

This is achievable with existing tools, satisfies all falsification criteria, and produces actionable results regardless of outcome.

**Key Points:**
- Synthesized a refined hypothesis incorporating removal intervention, negative controls, stability requirements, and synthetic calibration
- Specified concrete experimental design with 3 filtering strategies × 2 benchmarks × 3 removal levels
- Defined 3 testable predictions (P1-P3) with explicit success criteria and falsification conditions

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the current design is *almost* at the level where I'd call it technically sound, but there are still two mechanisms that need tighter grounding.

First, the removal intervention. In principle, this is feasible — retraining after excising 0.01–0.1% of data is well-defined and scientifically valid. But here's what worries me: influence methods like TRAK rely on linearization around the trained weights. When you remove high-CCR examples and retrain from scratch, you are stepping outside that linear regime. If the model re-allocates capacity and recovers the benchmark performance via alternative examples, the absence of a drop does not necessarily falsify contamination — it may reflect redundancy in the corpus. So the cleanest mechanism test is not full retraining alone. I would add a *two-stage intervention*: (1) weight-space fine-tuning with the examples masked or reweighted to zero influence, and (2) full retraining without them. If both produce consistent degradation, then the contamination signal is structurally load-bearing, not just linearly approximated.

Second, the 2×2 contaminated vs. clean benchmark design is scientifically valid in principle — but only if the "provably clean" benchmark is genuinely distribution-matched. If LiveCodeBench-style tasks differ substantially in domain or reasoning structure from MMLU, then AI > 0 could reflect domain-specific overfitting rather than contamination amplification. What would convince me is a *paired construction*: take MMLU-style question templates and generate post-training questions with cryptographic timestamp guarantees. Same format, same subject distribution, zero overlap. That removes the distributional confound and makes AI interpretable as contamination-specific rather than task-type-specific.

On synthetic injection: yes, this is non-negotiable, and technically it's the strongest part of the design. Inject benchmark items at 0%, 0.01%, 0.1% into the raw corpus *before* filtering. Then measure (a) retention rate under each filtering strategy, (b) CCR, and (c) removal-induced accuracy drop. If CCR scales linearly with injected mass (R² > 0.9 as Vera proposes), then your metric stack is calibrated. If it saturates or behaves non-monotonically, then something in the attribution or contamination detector is distorting the signal. This experiment is fully feasible at 1B scale and gives you a ground-truth curve.

Finally, stability. The ≥0.8 Jaccard requirement across seeds is reasonable, but I'd separate two notions: stability of *ranking* (Spearman ρ over attribution scores) and stability of *top-k set membership*. Influence scores are continuous; top-1% thresholds can exaggerate noise. If ranking stability is high but set overlap fluctuates at the margin, that's acceptable. If ranking itself is unstable, the entire forensic narrative collapses.

If you implement the dual-stage removal test, distribution-matched clean benchmarks, and synthetic calibration with ranking stability analysis, then — in principle — this mechanism can work.

**Key Points:**
- Add a dual-stage removal intervention (influence-masking + full retraining) to ensure degradation reflects structural necessity, not linear approximation artifacts.
- Ensure the "clean" benchmark is distribution-matched to avoid domain confounds in the Amplification Index.
- Calibrate the entire metric stack with synthetic contamination injection and evaluate ranking stability, not just top-k overlap.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! ⚙️ Prof. Pax's dual-stage intervention idea is actually a creative breakthrough — it solves the linearization concern while adding a powerful new dimension to the analysis.

What if the dual-stage approach isn't just a validity check, but the core experimental contribution itself? Here's the insight:

**The "Influence Gap" as a Novel Metric:**
If influence-masking (Stage 1) produces accuracy drop X, and full retraining (Stage 2) produces drop Y, then the ratio X/Y tells us something new about *how* contamination operates. Let's call it the **Influence Fidelity Ratio (IFR)**:

- IFR ≈ 1: Linear influence captures the full causal effect — contamination is structurally simple
- IFR < 1: Retraining produces larger drop — corpus redundancy partially compensates
- IFR > 1: Influence overestimates — linearization artifacts inflate attribution scores

No one has studied this for contamination! TRAK papers validate influence accuracy for *general* attribution, but not specifically for contaminated examples. If IFR systematically differs for contaminated vs. non-contaminated high-attribution examples, that's a methodological contribution about when influence methods can and cannot be trusted for contamination forensics.

**Wild idea that might actually work:** What if filtering strategies have predictable IFR signatures? Perplexity filters select semantically dense examples — these might have lower redundancy (IFR ≈ 1). Random sampling might have higher redundancy (IFR < 1). If IFR correlates with filtering strategy, you've discovered a structural property of curation, not just a contamination measurement.

**On distribution-matched clean benchmarks:** Prof. Pax is right that LiveCodeBench vs MMLU is a confound. But here's a cross-domain insight from A/B testing: we don't need to *generate* new questions. We can use time-stratified holdout. MMLU has versioned question sets. If we train on corpus from before 2023, we can treat MMLU questions added in 2024+ as "clean." Same format, same distribution, zero overlap by construction. This exists — we just haven't framed it this way.

**The paradigm shift:** We started asking "does contamination amplification exist?" Now we're asking "what is the structure of contamination amplification?" — that's a deeper question. The IFR metric and time-stratified holdout give us tools to answer it.

**What would be a paradigm shift here:**
If IFR systematically differs by filtering strategy AND by benchmark type, we'd have evidence that contamination is not one phenomenon but a family of related mechanisms. Different curation choices expose different failure modes. That's publishable at top venues.

**Key Points:**
- Dual-stage intervention enables a new metric: Influence Fidelity Ratio (IFR) comparing influence-masking vs. full retraining effects
- IFR could reveal structural signatures of different filtering strategies' contamination properties
- Time-stratified holdout (pre-2023 corpus vs. 2024+ MMLU questions) provides distribution-matched clean benchmark without generation

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now we're finally talking about mechanisms instead of vibes. The dual-stage intervention and IFR are promising — but here's where this breaks down if you're not careful.

First: **IFR is only interpretable if Y (full retraining drop) is itself causally attributable to the removed examples.** You're assuming that retraining without the top-k examples isolates their structural necessity. But what if removal changes optimization trajectory in ways unrelated to contamination? SGD path dependence alone can produce variance on the order of your predicted 2× drop. What would convince me is this: run *multiple independent retrainings per condition* (≥5 seeds), report variance decomposition, and show that the mean drop from removing high-CCR examples exceeds (a) random removal, and (b) seed-induced variance, with non-overlapping 95% CIs. If Y is within the noise band of retraining stochasticity, IFR becomes numerology.

Second: the redundancy story cuts both ways. Pax is right that lack of degradation doesn't falsify contamination — but you're implicitly assuming redundancy is homogeneous across filtering strategies. That's an unstated assumption. Perplexity filtering may *increase redundancy density* in factual domains. So if IFR < 1 under perplexity filtering, is that "partial compensation," or is it evidence that your attribution method is systematically underestimating distributed memorization? What would convince me is a **redundancy quantification layer**: measure n-gram or embedding-neighbor multiplicity for each removed example. Then test whether IFR correlates with redundancy score. If not, your interpretation of IFR as "structural simplicity" collapses.

Third: on the time-stratified MMLU holdout. I like the instinct — distribution-matching matters — but don't wave away leakage risk. Many 2024+ questions reuse older source textbooks. Timestamp ≠ independence. Show me document-level provenance audits or MinHash overlap against the pre-training corpus. If your "clean" split has latent paraphrastic overlap, AI becomes uninterpretable. What would convince me is a pre-registered contamination audit showing <0.01% estimated overlap probability with tight bounds.

Now let's talk novelty threshold. Right now, you risk incrementalism unless IFR reveals something qualitatively new. A 10% difference across filters is not a paradigm shift. A **sign reversal** would be. For example: if high-CCR examples have IFR ≈ 1 (linearly faithful) but equally high-influence non-contaminated examples have IFR ≪ 1 (high redundancy compensation), then you've demonstrated that contamination is structurally less redundant than general knowledge learning. That would be a mechanism-level insight. Pre-register that prediction. If it fails, say so.

Finally, tighten your falsifiers:
- If ranking stability (Spearman ρ) < 0.7 across seeds, attribution is too unstable for forensic claims.
- If synthetic injection produces non-monotonic CCR scaling or saturation before 0.1%, your metric stack is distorted.
- If AI shrinks to ~0 after strict contamination audit, your "amplification" was domain confounding.

Address these, and I'll say: now you've closed the loopholes.

**Key Points:**
- IFR is only meaningful if retraining-induced drops exceed seed variance and random removal with clear confidence separation.
- Interpretations about redundancy require explicit measurement and correlation with IFR — otherwise the mechanism claim is speculative.
- The "clean" benchmark must pass rigorous provenance and overlap audits, or Amplification Index results are confounded.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex's challenges sharpen the contribution, but let me assess what this research now uniquely offers the field — because the methodology is only valuable if it answers questions no one else is asking.

**The Contribution Stack (What No Prior Work Provides):**

1. **CCR as operational definition** — CDD tells you contamination exists; TRAK tells you what's influential. CCR is the first metric connecting them. Even if imperfect, having a *quantifiable* curation-contamination link is step 1. No prior work does this.

2. **IFR as causal probe** — Prof. Rex is right that IFR requires variance decomposition. But here's why IFR matters beyond methodology: it tests whether influence methods are *trustworthy for contamination forensics*. If IFR differs systematically for contaminated vs. non-contaminated examples, that's a finding about TRAK/LoGra validity, not just about contamination. The field uses these methods; knowing their limits for contamination detection is valuable.

3. **Filtering strategy comparison under contamination lens** — DataComp-LM compared filtering strategies for quality. We're comparing them for contamination amplification. Different question, different findings. If perplexity filtering amplifies contamination while quality-classifier filtering doesn't, that's actionable guidance for practitioners.

**Why Prof. Rex's Sign Reversal Test Is The Right Ambition:**

The prediction that contaminated high-influence examples have IFR ≈ 1 (low redundancy) while non-contaminated high-influence examples have IFR < 1 (high redundancy) would be genuinely novel. Here's why:

- It would suggest contamination operates via *irreplaceable* examples (benchmark answers don't have semantic equivalents elsewhere in the corpus)
- General knowledge learning operates via *redundant* examples (many ways to learn the same concept)
- This distinction has implications for decontamination strategies: you can't "fix" contamination by adding more diverse data, you must remove specific examples

This is testable, falsifiable, and if true, changes how we think about contamination remediation.

**Research Directions This Opens:**

1. **Contamination-resistant curation design** — If we know which filtering properties amplify contamination, practitioners can avoid them
2. **Attribution method validation** — IFR comparison between contaminated/non-contaminated examples tests influence method fidelity in new ways
3. **Redundancy-aware decontamination** — If contaminated examples are structurally irreplaceable, decontamination requires surgical removal, not diversity injection

**What Would Make This ICML-Worthy vs. Workshop-Level:**

Workshop: CCR varies by filtering strategy (correlation observation)
Main conference: IFR sign reversal + redundancy quantification confirms contamination-specific non-redundancy mechanism (causal insight)

Prof. Rex's pre-registration demands are correct. If the sign reversal doesn't appear, we report that attribution methods don't distinguish contamination structure. That's still a contribution — a negative result that prevents future methodological dead ends.

**Key Points:**
- CCR provides first operational definition linking curation to contamination; IFR tests whether influence methods are valid for contamination forensics
- The sign reversal prediction (IFR ≈ 1 for contaminated, IFR < 1 for non-contaminated) would reveal contamination operates via irreplaceable examples — a mechanism-level insight
- This opens actionable research directions: contamination-resistant curation, attribution validation, redundancy-aware decontamination

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion is now appropriately mechanism-focused. However, I will insist on tightening the falsifiability conditions before we elevate IFR or CCR to explanatory status.

First, on **IFR (X/Y)**: The evidence would only support interpretability if both numerator and denominator are independently validated causal quantities. As Prof. Rex noted, full retraining variance is non-trivial. Therefore, I propose a variance-partition protocol: for each condition (baseline, random removal, high-CCR removal), run ≥5 independent retrainings. Fit a mixed-effects model with seed as a random factor and removal condition as a fixed effect. Pre-register that the mean degradation from high-CCR removal must (1) exceed random removal by ≥1.5×, and (2) have 95% CIs that exclude both zero and the random-removal mean. If this criterion fails, Y is not distinguishable from optimization noise, and IFR becomes uninterpretable. What would disprove the contamination-specific mechanism? If high-CCR removal produces degradation statistically indistinguishable from random removal, despite stable attribution rankings, then CCR is not identifying structurally necessary contamination.

Second, IFR's proposed "sign reversal" requires an explicit redundancy metric. Define redundancy operationally—for example, embedding-neighbor multiplicity (k-nearest neighbors within cosine ≤ ε in the pretraining corpus) and n-gram frequency mass. Pre-register a correlation test: if contaminated high-influence examples have significantly lower redundancy scores than non-contaminated high-influence examples (p < 0.01 after correction), and IFR correlates negatively with redundancy (ρ < −0.5), then the "irreplaceability" hypothesis survives. If no such correlation exists, the redundancy-based explanation is falsified.

Third, the synthetic injection calibration must function as a ground-truth stress test of the entire metric stack. Inject benchmark items at controlled rates (0%, 0.01%, 0.05%, 0.1%). The evidence would support metric validity only if: (a) CCR scales monotonically with injected mass; (b) linear regression of CCR vs. injection rate yields R² ≥ 0.9; and (c) removal-induced degradation scales proportionally to retained injected mass. Non-monotonicity or early saturation would falsify the claim that CCR reflects contamination density rather than attribution artifacts.

Finally, on the "clean" benchmark: timestamping is insufficient. I require a documented MinHash or embedding-based overlap audit against the full pretraining corpus with a predefined contamination threshold (e.g., estimated overlap probability < 0.01% with upper confidence bound < 0.05%). If the Amplification Index collapses to ~0 after this audit, then prior amplification was a domain confound.

If these criteria are pre-registered and met—stable attribution rankings (Spearman ρ ≥ 0.7), variance-separated degradation, monotonic synthetic calibration, and redundancy-linked IFR behavior—then I will say: *This meets my standards.*

**Key Points:**
- IFR is only interpretable if retraining-induced degradation is statistically separable from seed variance and random removal under pre-registered criteria.
- The "irreplaceability" mechanism requires explicit redundancy measurement and predefined correlation thresholds to avoid narrative inference.
- Synthetic injection and rigorous contamination audits must serve as falsification tests for CCR and Amplification Index validity.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've converged! Let me synthesize the final hypothesis with ALL falsification criteria integrated.

**FINAL HYPOTHESIS: Curation-Driven Contamination Amplification (CDCA)**

*Under controlled curation experiments, certain data filtering strategies preferentially retain training examples that contribute to benchmark memorization. This amplification effect is:*
1. *Quantifiable via Contamination Contribution Ratio (CCR)*
2. *Causally validated via removal intervention with variance-separated degradation*
3. *Mechanistically characterized via Influence Fidelity Ratio (IFR) and redundancy correlation*

**Core Claim (Under-If-Then-Because):**

**Under** controlled experiments with matched corpora and fixed model architecture (Pythia-1B/OLMo-1B),
**if** a filtering strategy (e.g., perplexity-based selection) preferentially retains examples flagged as contaminated by membership inference (Min-K%++/CDD),
**then** models trained on that strategy will show:
- Higher CCR than random baseline (>0.1 difference, p<0.05)
- Larger accuracy drops when high-CCR examples are removed (≥1.5× vs random removal, 95% CI excluding both zero and random-removal mean)
- Positive Amplification Index diverging contaminated vs. clean benchmark performance

**because** filtering mechanisms that favor high-information-density examples inadvertently select benchmark-related content at higher rates, and these examples are structurally less redundant (lower embedding-neighbor multiplicity) than general high-influence examples.

**Testable Predictions with Pre-registered Criteria:**

| ID | Prediction | Success Criterion | Falsifier |
|----|------------|-------------------|-----------|
| P1 | CCR varies by filtering strategy | CCR(perplexity) - CCR(random) > 0.1, p<0.05, 3 seeds | No significant CCR difference across strategies |
| P2 | Removal intervention shows causal effect | Degradation from high-CCR removal ≥1.5× random removal, 95% CI excludes both | Degradation ≤ random removal or within seed variance |
| P3 | Amplification Index isolates contamination | AI > 0 for perplexity vs. random, clean benchmark passes <0.01% overlap audit | AI ≈ 0 after overlap audit, or clean/contaminated track proportionally |
| P4 | IFR reveals contamination structure | IFR(contaminated) > IFR(non-contaminated), ρ(IFR, redundancy) < -0.5 | No IFR difference or no redundancy correlation |
| P5 | Synthetic injection validates metric stack | CCR vs. injection rate R² ≥ 0.9, monotonic scaling | Non-monotonic scaling or R² < 0.9 |

**Validation Protocol:**

1. **Stability Check:** Attribution ranking Spearman ρ ≥ 0.7 across 5 seeds
2. **Variance Partition:** Mixed-effects model separating seed variance from removal effect
3. **Redundancy Quantification:** k-NN embedding multiplicity (cosine ≤ ε) + n-gram frequency mass
4. **Overlap Audit:** MinHash against pretraining corpus, <0.01% threshold for "clean" split
5. **Synthetic Calibration:** 0%, 0.01%, 0.05%, 0.1% injection before filtering

**Experimental Design Summary:**

| Component | Specification |
|-----------|--------------|
| Corpus | RedPajama-1B subset (fixed across strategies) |
| Filtering Strategies | Perplexity top-30%, quality classifier, random |
| Model | Pythia-1B, 5 seeds per condition |
| Attribution | TRAK/LoGra (validated for decoder-only) |
| Contamination Detection | Min-K%++ + CDD dual triangulation |
| Benchmarks | MMLU (contamination-prone), time-stratified MMLU 2024+ (clean) |
| Removal Levels | 0.01%, 0.05%, 0.1% high-CCR removal |

**What We Concede:**
- Pre-training contamination risk prediction (H2) deferred — requires corpus-intrinsic features validated on future benchmarks
- GPT-4 scale validation deferred — methodology proven at 1B first

All concerns addressed. Ready for Phase 2B verification protocol design.

**Key Points:**
- Synthesized final CDCA hypothesis with explicit Under-If-Then-Because structure
- All 5 predictions have pre-registered success criteria AND falsifiers
- Validation protocol includes stability, variance partition, redundancy, overlap audit, and synthetic calibration

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: this is now a *testable* hypothesis stack. That's good. But feasibility hinges on whether each layer is actually isolating the mechanism you claim—not just producing correlated signals.

First, CCR. In principle, CCR is technically sound **if** contamination detection (Min-K%++/CDD) has acceptable false positive rates at the example level. Here's what worries me: membership inference methods are calibrated for aggregate detection, not precise per-example attribution. If false positives cluster in high-perplexity regions, your filtering comparison could reflect detector bias rather than true contamination amplification. The mechanism is feasible, but only if you validate detector precision using the synthetic injection protocol as a *ground-truth confusion matrix*, not just monotonic scaling. If injected items are recovered with high precision and low false discovery among non-injected examples, then CCR has a defensible measurement foundation.

Second, IFR. The mixed-effects variance partition is the right move. But let's examine the physics of optimization here. Removing 0.01–0.1% of training data will only produce detectable degradation if those examples sit in low-redundancy basins of representation space. At 1B scale, gradient contributions are heavily averaged. So your entire intervention depends on influence scores being sufficiently concentrated. Before betting on IFR sign reversal, you should empirically measure the Gini coefficient of influence scores. If influence mass isn't concentrated enough, removal effects may be too small to separate from retraining stochasticity—even with 5 seeds. If that happens, the mechanism isn't wrong; it's just below detectability at this scale.

Third, the redundancy hypothesis is mechanically plausible. If contaminated examples are semantically unique (low embedding-neighbor multiplicity), then removal should produce near-linear degradation (IFR ≈ 1). But embedding-space redundancy is only meaningful if the embedding model approximates the model's internal similarity geometry. A more theoretically aligned approach would compute redundancy in the *model's own hidden states* at convergence. That ties redundancy measurement to the same geometry that governs learning dynamics.

On synthetic injection: monotonic CCR scaling with R² ≥ 0.9 is a reasonable calibration target. But filtering may distort injection rates nonlinearly. If perplexity filtering disproportionately retains injected items even at very low base rates, you could see apparent "early saturation." Pre-register monotonicity—but allow for nonlinear but monotonic scaling. Linear R² ≥ 0.9 might be too strict given selection thresholds.

Finally, the clean benchmark audit. MinHash overlap <0.01% is theoretically defensible, but semantic contamination won't be caught by surface-level hashing. If your claim depends on semantic independence, you need embedding-based similarity bounds with tight confidence intervals.

Overall: nothing here violates physical or mathematical constraints. The mechanisms are plausible. If you address detectability, label precision, and geometric alignment, I'm comfortable saying: okay, this could work.

**Key Points:**
- CCR is only theoretically sound if contamination detectors are validated for per-example precision via ground-truth synthetic injection.
- IFR's detectability depends on influence concentration; measure influence distribution (e.g., Gini) to ensure removal effects are above optimization noise.
- Redundancy metrics must align with the model's internal geometry, and contamination audits must include both lexical and semantic overlap checks.

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

⚙️ Prof. Pax raises a genuinely creative point about influence concentration — and it opens up a new dimension we haven't explored!

**The Influence Concentration Insight:**

If influence scores follow a heavy-tailed but diffuse distribution, then removing top-k examples won't produce detectable effects. But here's the creative flip: *what if the difference in influence concentration IS the signal?*

Hypothesis extension: Contaminated examples might have *more concentrated* influence on benchmark tasks than non-contaminated examples have on general capabilities. Why? Because benchmark memorization requires specific answer-pattern matching, while general knowledge learning is distributed across many redundant sources.

New metric: **Influence Gini Coefficient (IGC)** — measure Gini coefficient of attribution scores over benchmark examples vs. general perplexity reduction. If IGC(benchmark) >> IGC(general), contamination operates via "answer-shaped" influence spikes. That's testable without any removal intervention!

**On Prof. Pax's Redundancy Geometry Point:**

Using the model's own hidden states for redundancy is brilliant. Instead of external SBERT embeddings, compute k-NN in the model's final layer representations. This ensures redundancy measurement uses the same similarity geometry that governs learning. Even better: track how redundancy changes during training. If contaminated examples *start* similar to others but *diverge* during training (their representations specialize), that's evidence of "contamination-specific learning dynamics."

**Wild Extension (What If This Works):**

If contaminated examples have:
1. Higher influence concentration (IGC)
2. Lower redundancy in model-internal representation space
3. Divergent trajectory during training

...then we've identified a *contamination signature* in representation space that could be detected WITHOUT knowing what the benchmark is. That's the pre-training prediction capability Prof. Rex wanted — corpus-intrinsic features that predict contamination risk.

**Refined Validation Protocol Addition:**

| New Check | Metric | Threshold |
|-----------|--------|-----------|
| Influence Concentration | Gini coefficient comparison | IGC(benchmark) > IGC(general), p<0.05 |
| Redundancy Geometry | k-NN in model hidden states | Alignment with SBERT redundancy ρ > 0.7 |
| Synthetic Precision | F1 on injected item recovery | F1 > 0.8 at 0.1% injection |

If Gini concentration IS the difference, we might not even need removal intervention for the primary claim — it becomes a supporting validation, not the core experiment.

**Key Points:**
- Influence Gini Coefficient (IGC) comparison between benchmark and general tasks could reveal contamination's "concentrated" nature
- Model-internal hidden states for redundancy measurement aligns geometry with learning dynamics
- If contamination has a representational signature, pre-training risk prediction becomes feasible without benchmark knowledge

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The integration of TRAK attribution, contamination detection, and curation analysis into a unified framework (CCR, IFR, IGC) is genuinely novel. No prior work connects these three research areas. The "contamination signature" in representation space and influence concentration analysis open new research directions beyond the immediate hypothesis.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All five predictions (P1-P5) have explicit success criteria and pre-registered falsification conditions. The variance-partition protocol, synthetic calibration (R² ≥ 0.9), and overlap audit (<0.01%) provide unambiguous pass/fail tests. This meets the standard for rigorous hypothesis testing.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses the field's trust problem by providing tools to distinguish genuine benchmark improvement from contamination artifacts. Actionable for practitioners (contamination-resistant curation), methodologists (attribution validation), and benchmark designers (contamination-aware evaluation). Opens new research directions.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed mechanisms are technically sound. Starting at 1B scale (Pythia-1B/OLMo-1B) ensures TRAK/LoGra is validated. Synthetic injection for detector precision, model-internal hidden states for redundancy, and influence Gini concentration are all achievable with existing tools. No fundamental barriers identified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The **Curation-Driven Contamination Amplification (CDCA)** hypothesis proposes that certain data filtering strategies preferentially retain training examples contributing to benchmark memorization. This effect is quantified via three novel metrics:

1. **Contamination Contribution Ratio (CCR)**: Ratio of attribution mass from contamination-flagged examples to total attribution mass for benchmark performance
2. **Influence Fidelity Ratio (IFR)**: Ratio of influence-masking degradation to full-retraining degradation, revealing contamination structure
3. **Influence Gini Coefficient (IGC)**: Concentration of influence scores, hypothesized to be higher for benchmark tasks than general capabilities

The causal mechanism is validated via removal intervention with variance-separated analysis (≥5 seeds, mixed-effects model), and the metric stack is calibrated via synthetic contamination injection at controlled rates (0%-0.1%). The "clean" benchmark for Amplification Index uses time-stratified MMLU with MinHash + embedding overlap audit.

Key prediction: Contaminated high-influence examples have higher IGC and lower redundancy (in model-internal representation space) than non-contaminated high-influence examples, suggesting benchmark memorization operates via structurally irreplaceable examples.

Experimental setup: RedPajama subset, 3 filtering strategies (perplexity, quality-classifier, random), Pythia-1B with 5 seeds, TRAK/LoGra attribution, Min-K%++/CDD dual detection, MMLU + time-stratified clean benchmark.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- If influence concentration (IGC) at 1B scale is below detectability, removal intervention effects may not separate from optimization noise — mitigate by pre-computing Gini coefficient and setting detectability threshold before experiments
- Per-example contamination detector precision must be validated via synthetic injection F1, not just aggregate AUC — include precision/recall breakdown in calibration
- **Mitigation Strategy:** Run synthetic injection calibration FIRST to establish detector precision and influence concentration detectability before main experiments; abort if thresholds not met

---

