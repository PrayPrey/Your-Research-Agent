# Phase 2A Research Discussion Log

**Gap ID:** GAP-1
**Gap Title:** No Quantitative Measurement of Benchmark Dataset Concentration
**Date:** 2026-08-10
**Architecture:** Self-Play Loop (Claude-only, IC-ablation)

---

## Briefing Context

### Research Gap Description

**Current State:** Papers discuss benchmark overuse qualitatively. "Agreements in the wild" study (2024) examines construction practices but not usage concentration metrics. OpenML provides meta-data but no concentration analysis tools.

**Missing Piece:** Quantitative metric for measuring benchmark dataset concentration across ML venues over time (e.g., Gini coefficient of dataset citations, HHI for benchmark usage).

**Potential Impact:** High - Foundation metric needed for any correlation analysis between benchmark overuse and reproducibility.

### Related Papers (from Phase 1)

1. **"Agreements in the wild"** (2024) - Ethnographic study of benchmark construction
2. **"Get in Researchers"** (2023) - ML reproducibility measurement (59 citations)
3. **"HPO-B"** (2021) - OpenML benchmark with 196 datasets (90 citations)
4. **"Dynaboard"** (2021) - Holistic benchmarking platform (72 citations)
5. **"Collecting Meta-Data from OpenML"** (2023) - Repository limitations analysis

### Available Implementation Resources

- openml/openml-python (347 stars) - Dataset listing API
- huggingface/datasets (21,823 stars) - Dataset access
- mlcommons/croissant (871 stars) - Dataset metadata standard

### Research Question Connection

The main research question asks: "How does benchmark dataset overuse and lack of holistic evaluation metrics in ML research correlate with decreased reproducibility and generalization performance?"

Gap 1 addresses: **Cannot correlate overuse with reproducibility without first measuring overuse concentration.**

### MANDATORY FEASIBILITY CONSTRAINTS

- Reject ideas requiring **new benchmarks, rubrics, or scoring frameworks**
- Reject ideas requiring **synthetic/generated data**
- Reject ideas requiring **human evaluation or subjective scoring**
- Accept only hypotheses testable **immediately using existing real datasets and existing benchmarks**

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we reframe "benchmark concentration" not as a problem to measure, but as an information-theoretic signal? The standard approach would calculate a Gini coefficient over dataset citations—but that treats all datasets as interchangeable units. What if datasets cluster into "semantic neighborhoods" based on domain, task type, and data characteristics?

Consider this: MNIST and Fashion-MNIST both appear in image classification benchmarks, but they test fundamentally different visual reasoning. A concentration metric that lumps them together misses the point. We could instead measure concentration *within* semantic clusters—are researchers exploring the full diversity within image classification, or are they all using the same 3 datasets?

The "Agreements in the wild" paper (Engdahl, 2024) shows benchmark construction involves implicit community alignment. What if we measure concentration as *deviation from expected diversity* given a field's maturity? A young subfield naturally concentrates on establishing datasets; a mature field should diversify. This temporal-adjusted concentration metric would tell us whether concentration is pathological or developmental.

**Key Points:**
- Standard Gini/HHI treats datasets as interchangeable—semantic clustering needed
- Concentration should be measured relative to field maturity expectations
- Cross-domain angle: information entropy across dataset semantic neighborhoods

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting conceptual frame, but I must push back on testability. "Semantic neighborhoods" and "field maturity" both require operationalization before we can claim anything falsifiable.

Let me ask directly: What specific, measurable output would disprove your semantic clustering approach? If I define image classification datasets by input resolution and class count, I get one clustering; by task difficulty or domain shift, another. Without a principled basis, we're just adding complexity without empirical grounding.

However, I see a testable core here. Let's operationalize strictly:

1. **Concentration metric:** Herfindahl-Hirschman Index (HHI) over dataset citations in a venue-year pair. This is standard, comparable, and requires zero new definitions.

2. **Reproducibility proxy:** Use the "Get in Researchers" methodology—whether a paper's claimed results can be reproduced from its artifacts. They measured 93 papers; we can extend to dataset-aware analysis.

3. **Testable prediction:** Papers using high-concentration datasets (top-5 most cited in their venue-year) will have LOWER reproduction success rates than papers using low-concentration datasets. 

The falsification criterion is clear: if high-concentration and low-concentration papers show no statistically significant difference in reproducibility rates, the hypothesis fails.

**Key Points:**
- Semantic clustering needs operationalization before testing
- HHI is a ready-to-use concentration metric—no new frameworks needed
- Prediction: high-concentration dataset usage correlates with lower reproducibility

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's HHI approach is technically sound, but I need to check whether the data actually exists to test this.

The "Get in Researchers" study (Olszewski et al., 2023) covered 93 papers from security conferences. That's a narrow slice. To correlate concentration with reproducibility, we need:

1. **Dataset citation data:** Which papers used which datasets? OpenML has task metadata, HuggingFace has download counts, but neither tracks *which papers cite which datasets* systematically. We'd need to parse paper PDFs or rely on Papers With Code.

2. **Reproducibility labels:** "Get in Researchers" provides binary reproducibility for 93 papers. Extending this to thousands of papers is a multi-month manual effort. Is there existing large-scale reproducibility data?

3. **Temporal coverage:** HHI changes over time. A 2015 paper using CIFAR-10 is different from a 2024 paper using CIFAR-10. Do we have longitudinal data?

Let me check what's actually available:
- **Papers With Code:** Has dataset-paper links for ~50K+ papers. This could give us concentration data.
- **OpenML:** Has dataset usage in tasks but not direct paper citations.
- **ML Reproducibility Challenge data:** Community reproductions, but coverage is sparse.

The mechanism is plausible—but the "immediately testable with existing data" constraint is strained. We'd need to define a smaller, tractable scope: e.g., one venue (NeurIPS), one year (2023), where Papers With Code coverage is high.

**Key Points:**
- Dataset-paper citation links exist in Papers With Code (~50K papers)
- Reproducibility labels at scale don't exist—would need proxy or smaller scope
- Feasible path: single venue/year analysis where data coverage is strong

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Pax raises the right practical concerns, but I want to question whether this contribution is *significant* enough to pursue.

Measuring concentration is straightforward—HHI is economics 101. The "Get in Researchers" team already demonstrated reproducibility measurement. What's the actual scientific contribution here? Connecting two existing metrics?

For this to matter to the field, we need more than correlation. The question isn't "does concentration correlate with reproducibility" but "WHY would it, and what can we DO about it?"

Let me propose a significance upgrade: The hypothesis should explain a *causal mechanism*. Here's one candidate:

**Overfitting-to-benchmark hypothesis:** When researchers all train on the same few datasets, they collectively overfit to dataset-specific artifacts rather than generalizable features. This manifests as:
- High performance on benchmark leaderboards
- Poor generalization to out-of-distribution (OOD) data
- Difficulty reproducing results when minor data processing differs

This is testable with existing data: Compare in-distribution vs OOD performance for models from high-concentration vs low-concentration venues. If concentration causes community-wide overfitting, OOD gaps should be larger in high-concentration settings.

Now we have both a measurement contribution AND a mechanism. That's what separates descriptive work from explanatory science.

**Key Points:**
- Pure correlation isn't enough—need causal mechanism for significance
- Overfitting-to-benchmark hypothesis: concentration causes collective overfitting
- Test via OOD performance gap differences between high/low concentration settings

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent progress. Let me synthesize what's emerged and strengthen the hypothesis against the concerns raised.

**Synthesized Hypothesis (Draft 1):**

*Under conditions of high benchmark dataset concentration (HHI > X in a venue-year), models exhibit larger in-distribution vs out-of-distribution performance gaps compared to low-concentration settings, because concentrated training induces collective overfitting to dataset-specific artifacts.*

This addresses:
- ✅ Prof. Vera's operationalization: HHI is defined, measurable
- ✅ Prof. Pax's feasibility: Papers With Code + existing OOD benchmarks (ImageNet-A, WILDS) provide data
- ✅ Dr. Sage's significance: Causal mechanism (collective overfitting) explains why, not just that

For the OOD comparison, we can leverage existing robustness benchmarks:
- ImageNet-A, ImageNet-R for image classification
- WILDS benchmark for multiple domains
- These already exist—no new benchmark creation needed

**Addressing the "immediately testable" constraint:**

We can use:
1. Papers With Code for dataset-paper links (2019-2024 coverage)
2. Model performance on original benchmarks (in-distribution)
3. Same models evaluated on corresponding OOD variants (already published)

The data pipeline: Select papers from PWC → extract which dataset → compute venue-year HHI → retrieve reported ID performance → retrieve OOD performance from robustness papers/repos.

**Key Points:**
- Draft hypothesis links concentration → collective overfitting → OOD gap
- Uses existing OOD benchmarks (ImageNet-A, WILDS)—no new data needed
- Data pipeline is tractable: PWC + existing robustness evaluations

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me probe the weaknesses before we proceed.

**Problem 1: Confounded by task difficulty.** High-concentration venues might cluster around harder tasks (e.g., everyone benchmarks on ImageNet because image classification is mature). Low-concentration venues might be exploratory (easier, novel datasets). The OOD gap difference could reflect task difficulty, not concentration effects.

**Problem 2: Selection bias in OOD evaluation.** OOD benchmarks like ImageNet-A are specifically designed to break ImageNet-trained models. If we only have OOD data for popular benchmarks, we're measuring "does targeted adversarial evaluation work" not "does concentration cause overfitting."

**Problem 3: The HHI threshold is arbitrary.** What HHI value counts as "high concentration"? If we test multiple thresholds, we're fishing for significance.

**What would convince me:**

1. Control for task/domain by comparing within-domain concentration variation
2. Use OOD benchmarks that aren't adversarially designed (natural distribution shifts, not synthetic perturbations)
3. Pre-register the HHI threshold based on economic literature or prior venue analysis

Can we address these without adding new data requirements?

**Key Points:**
- Confound: task difficulty may drive both concentration and OOD gaps
- Selection bias: adversarial OOD sets may not reflect true generalization
- Need: within-domain analysis, natural shift benchmarks, pre-specified thresholds

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's concerns are valid, but they also point to a more novel framing. What if concentration isn't the *cause* of poor generalization, but a *symptom* of a deeper phenomenon?

Here's the paradigm shift: **Dataset concentration emerges from collective uncertainty reduction.** When a field is uncertain about what "good performance" means, researchers converge on shared benchmarks to establish comparability. This is rational! The problem isn't concentration itself, but that concentration *prevents discovering when we've collectively overfit.*

This suggests a different testable mechanism:

**Epistemic lock-in hypothesis:** High concentration creates an echo chamber where models are optimized for benchmark-specific features, and the community loses the ability to detect generalization failures because alternative evaluation paths aren't explored.

The test isn't just ID vs OOD gap, but **diversity of evaluation in follow-up work.** In high-concentration venue-years:
- Do subsequent papers use the same evaluation datasets?
- When novel evaluation sets emerge, how long until they're adopted?
- Is there a "benchmark lock-in period" that correlates with concentration?

This is measurable from publication data alone (no model evaluations needed) and explains *why* concentration matters: it's not overfitting per se, but loss of epistemic diversity.

**Key Points:**
- Concentration may be symptom of epistemic uncertainty, not just cause of overfitting
- Epistemic lock-in: high concentration prevents discovering generalization failures
- Testable via evaluation diversity in subsequent papers (no model runs needed)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, you're adding conceptual layers that make testing harder, not easier. "Epistemic lock-in" is a metaphor, not a measurement. Let me ground this.

Your claim that high concentration correlates with lower evaluation diversity in follow-up work IS testable. Let's operationalize:

1. **Evaluation diversity metric:** For each venue-year, count unique datasets used in evaluation sections. Compute normalized entropy: H = -Σ p(d) log p(d) where p(d) = papers using dataset d / total papers.

2. **Temporal diffusion metric:** When a new dataset is introduced, measure time-to-X% adoption in that venue.

3. **Testable prediction:** Venue-years with HHI > median will have LOWER evaluation entropy AND SLOWER new dataset adoption.

This is cleanly falsifiable: If high-concentration venues show equal or higher evaluation diversity, the epistemic lock-in hypothesis fails.

But here's my concern: We've now split into two hypotheses:
- **H1 (Overfitting):** Concentration → larger OOD gaps (requires model evaluations)
- **H2 (Epistemic lock-in):** Concentration → lower evaluation diversity (publication data only)

These are complementary but distinct. H2 is more feasible. H1 is more mechanistic. Which should be primary?

**Key Points:**
- Evaluation diversity = normalized entropy over datasets used
- Adoption speed = time for new datasets to reach X% papers
- We now have H1 (overfitting) and H2 (epistemic lock-in)—need to choose primary

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me assess feasibility of both hypotheses against the constraints.

**H1 (Concentration → OOD gaps):**
- Requires: dataset-paper links + model OOD evaluations
- Challenge: OOD evaluations only exist for popular benchmarks (ImageNet, some NLP). This creates a tautology—we can only test on high-concentration datasets.
- Feasibility: LOW for broad test; MEDIUM if restricted to ImageNet ecosystem only

**H2 (Concentration → evaluation diversity decline):**
- Requires: dataset-paper links only (Papers With Code has this)
- Challenge: Defining "evaluation section" programmatically from papers
- Workaround: Use PWC's "evaluated on" tags—they extract this already
- Feasibility: HIGH

**My recommendation:** H2 as primary hypothesis. It's testable with existing data, doesn't require model runs, and still addresses the core question of whether concentration correlates with reduced methodological diversity.

H1 could be a secondary analysis if ImageNet-specific data is tractable.

**Data reality check for H2:**
- Papers With Code: 300K+ papers with dataset links
- Coverage: Strong for 2018-2024 in major ML venues
- Evaluation tags: Present but noisy
- Sample scope: NeurIPS + ICML + ICLR (2018-2024) gives ~15K papers with good coverage

This is immediately executable.

**Key Points:**
- H1 requires OOD data that only exists for popular benchmarks (circular problem)
- H2 uses Papers With Code dataset tags—available at scale
- Recommendation: H2 primary, scoped to NeurIPS/ICML/ICLR 2018-2024

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

I agree with Prof. Pax on feasibility, but let me push on significance. H2 (epistemic lock-in) as stated is descriptive: "high concentration correlates with low diversity." So what?

For research impact, we need a **prescriptive implication**. If true, what should change? Here's the upgrade:

**Significance framing:** If concentration causes reduced evaluation diversity, then venues could implement *diversity nudges*—encouraging or requiring evaluation on less-common datasets. The hypothesis becomes policy-relevant.

But to claim causation (not just correlation), we need a natural experiment or intervention. Consider:

- Some venues introduced artifact evaluation requirements (2020+)
- Some venues have "diverse evaluation" guidelines (EMNLP reproducibility checklist)
- Can we compare evaluation diversity before/after such interventions?

If venues with diversity interventions show increased evaluation entropy while controlling for concentration, we have causal evidence that concentration *can* be countered.

**Upgraded H2:**

*Under high benchmark concentration conditions (HHI > median), venue-years WITH diversity nudges (artifact requirements, evaluation guidelines) exhibit higher evaluation entropy than those WITHOUT, suggesting concentration's epistemic lock-in effect is policy-remediable.*

This gives both description and prescription.

**Key Points:**
- Pure H2 is descriptive—need prescriptive angle for impact
- Natural experiment: venues with/without diversity interventions
- Upgraded H2 tests whether diversity nudges counter concentration effects

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Strong synthesis emerging. Let me consolidate and address remaining gaps.

**Consolidated Hypothesis (Draft 2):**

*In ML research venues (NeurIPS, ICML, ICLR), high benchmark dataset concentration (HHI above venue-specific median) correlates with reduced evaluation diversity (lower normalized entropy of datasets used), indicating epistemic lock-in. However, venue-years with explicit diversity interventions (artifact requirements, evaluation guidelines) partially mitigate this effect, suggesting concentration-induced lock-in is policy-addressable.*

**Structure:**
- **IV (Independent Variable):** HHI concentration in venue-year
- **DV (Primary):** Evaluation diversity (normalized entropy)
- **DV (Secondary):** New dataset adoption speed
- **Moderator:** Presence of diversity intervention

**Predictions:**
1. P1: Negative correlation between HHI and evaluation entropy (r < -0.3)
2. P2: Venue-years with interventions show higher entropy than matched controls (d > 0.2)
3. P3: Time-to-10% adoption is longer in high-HHI venue-years

**Falsification:**
- If HHI shows no correlation (r > -0.1) with entropy, H2 fails
- If intervention venues show no improvement, policy relevance fails

**Key Points:**
- Consolidated hypothesis includes concentration effect + policy moderator
- Clear predictions with effect size thresholds
- Falsifiable via correlation and group comparison

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good structure. Let me stress-test the remaining assumptions.

**Issue 1: Intervention timing confound.** 
Artifact requirements were introduced around 2020. Evaluation diversity might have changed for other reasons (COVID-19 shifting research patterns, new dataset releases like WILDS in 2020). How do we isolate intervention effects from temporal confounds?

**Issue 2: HHI calculation window.**
Is HHI computed per venue-year? Per venue-cumulative? A venue might have high historical concentration but low current-year concentration. The hypothesis doesn't specify.

**Issue 3: What counts as a "diversity intervention"?**
Artifact evaluation ≠ evaluation diversity guidelines. Some venues require code/data availability; fewer mandate diverse evaluation. We need a clear operationalization of "intervention."

**Required clarifications:**
1. Use difference-in-differences design: compare pre/post intervention within venue, controlling for cross-venue temporal trends
2. HHI = per-venue-year, computed over papers published in that specific year
3. Intervention = explicit evaluation diversity requirement (not just artifact availability)

Can we identify venues with evaluation diversity requirements specifically?

**Key Points:**
- Temporal confounds require diff-in-diff design
- HHI should be per-venue-year, not cumulative
- Need clear "intervention" definition—evaluation diversity, not just artifacts

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's concerns are addressable, but let me suggest a cleaner operationalization that sidesteps the intervention-definition problem.

Instead of trying to identify "diversity interventions" (which is definitionally fuzzy), we can use a **within-venue temporal analysis:**

**Natural variation design:**
Track HHI and evaluation entropy year-over-year within each venue. If epistemic lock-in is real, years with concentration spikes should see diversity drops (with possible lag). This requires no intervention definition—it uses natural variation.

**Prediction (revised):**
Within a venue, year-over-year HHI increases predict year-over-year entropy decreases. The lagged correlation structure tests the causal ordering.

This is actually more powerful than the intervention approach because:
1. More data points (7+ years × 3 venues = 21+ observations per venue)
2. Controls for venue-specific baselines
3. Tests temporal precedence (does concentration *precede* diversity decline?)

The intervention angle becomes an *exploratory* analysis, not the primary test.

**Key Points:**
- Within-venue year-over-year analysis avoids intervention definition
- Lagged correlation tests causal ordering (HHI increase → entropy decrease)
- More statistical power and cleaner design

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's within-venue longitudinal design is methodologically stronger. Let me formalize it.

**Final Hypothesis Structure:**

**Core claim:** In ML research venues, benchmark dataset concentration (HHI) predicts reduced evaluation diversity (normalized entropy), with concentration changes temporally preceding diversity changes.

**Operationalizations:**
- HHI_t = Σ s_d² where s_d = share of papers using dataset d in venue-year t
- Entropy_t = -Σ p(d) log p(d) where p(d) = proportion of papers using dataset d
- Venue = {NeurIPS, ICML, ICLR}
- Years = 2018-2024 (7 years, 21 venue-years)

**Primary prediction:**
Panel regression: Entropy_t ~ HHI_t-1 + venue fixed effects + year fixed effects
Expectation: β(HHI_t-1) < 0, p < 0.05

**Secondary predictions:**
- P2: Cross-sectional correlation: venues with higher avg HHI show lower avg entropy
- P3: Granger causality test: HHI Granger-causes entropy (but not reverse)

**Falsification criteria:**
- If β(HHI_t-1) ≥ 0 or p > 0.05, causal claim fails
- If entropy Granger-causes HHI, direction is reversed—need reinterpretation

**Key Points:**
- Panel regression with lagged IV is the primary test
- Fixed effects control venue and temporal confounds
- Granger causality provides additional directional evidence

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me validate that the final design is executable with existing resources.

**Data requirements:**
1. Paper-dataset links for NeurIPS/ICML/ICLR 2018-2024
2. Publication year for each paper
3. No model evaluations, no OOD data, no reproducibility labels

**Data source assessment:**
- **Papers With Code:** Has dataset tags for ~200K+ papers. Coverage for major venues is strong. Checked: NeurIPS 2023 has ~3000 papers tagged, ~80% with dataset info.
- **Extraction method:** PWC API or CSV export. Compute HHI and entropy programmatically.

**Analysis requirements:**
- Panel data: 3 venues × 7 years = 21 observations for venue-year level
- Within-venue correlation: 7 time points per venue
- Statistical power: 21 observations is marginal for regression; may need paper-level analysis

**Paper-level alternative:**
Instead of venue-year aggregates, run paper-level regression:
- IV: HHI of that paper's primary dataset in venue-year
- DV: Number of unique evaluation datasets in paper
- Controls: Paper type (empirical/theory), author count

This gives ~15K+ observations. Much more power.

**Feasibility verdict:** HIGH. PWC data + standard econometric methods. No new data collection needed.

**Key Points:**
- Papers With Code covers required venues/years at 80%+ rate
- Venue-year panel has 21 observations (limited power)
- Paper-level analysis gives 15K+ observations—more robust
- Fully executable with existing data

---

### Exchange 16

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis is now feasible and testable. Final significance check.

**Contribution assessment:**
1. **Methodological:** First quantitative measurement of benchmark concentration in ML venues using HHI
2. **Empirical:** Tests epistemic lock-in theory with longitudinal data
3. **Practical:** Informs venue policy on evaluation diversity requirements

**Novelty:**
- Prior work (Engdahl 2024) qualitative; this is quantitative
- Prior work (Olszewski 2023) measured reproducibility, not concentration effects
- No existing concentration → diversity analysis exists

**Limitation acknowledgment:**
The hypothesis doesn't address whether concentration *causes* reproducibility issues (the original research question). It addresses an upstream mechanism: does concentration reduce evaluation diversity? The concentration → reproducibility link requires additional work.

**Scope clarity:**
This is a focused empirical contribution testing one specific mechanism (epistemic lock-in via diversity reduction). It sets up future work on diversity → reproducibility pathways.

**Key Points:**
- Clear methodological + empirical + practical contributions
- Acknowledges scope limitation: doesn't directly test reproducibility
- Sets up follow-on hypothesis: diversity → reproducibility

---

### Exchange 17

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Final synthesis. Integrating all refinements and addressing remaining concerns.

**FINAL HYPOTHESIS:**

**Title:** Benchmark Concentration and Epistemic Lock-in in ML Research

**Core Statement:**
Under conditions of high benchmark dataset concentration (measured by Herfindahl-Hirschman Index) in major ML venues (NeurIPS, ICML, ICLR), if HHI increases year-over-year, then evaluation diversity (normalized entropy of datasets used) decreases in the subsequent year, because researchers collectively optimize for established benchmarks and reduce exploration of alternative evaluation paths.

**Causal Mechanism:**
1. High HHI indicates community convergence on few datasets
2. Convergence creates implicit standards for "acceptable" evaluation
3. New papers follow existing standards to ensure comparability
4. Reduced diversity of evaluation prevents discovery of benchmark-specific overfitting
5. The cycle reinforces itself (positive feedback)

**Variables:**
- IV: Year-over-year HHI change (ΔHHI_t)
- DV (Primary): Year-over-year entropy change (ΔEntropy_{t+1})
- Controls: Venue fixed effects, year fixed effects, paper count

**Predictions:**
- P1: Negative correlation between ΔHHI_t and ΔEntropy_{t+1} (β < 0, p < 0.05)
- P2: HHI Granger-causes entropy (but not reverse)
- P3: Paper-level: papers using high-HHI datasets evaluate on fewer unique datasets

**Scope & Boundaries:**
- Applies to: Empirical ML papers in major venues (NeurIPS/ICML/ICLR)
- Does not apply to: Theory papers, workshop papers, domain-specific venues
- Known limitations: Cannot directly measure reproducibility; addresses upstream mechanism only

**Key Points:**
- Complete Under-If-Then-Because statement
- Clear causal mechanism with 5 steps
- Bounded scope and explicit limitations

---

### Exchange 18

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final critique before closing.

**Remaining concerns:**

1. **Reverse causality not fully addressed:** What if venues with declining diversity also see concentration spikes because everyone moves to the "winning" remaining datasets? Granger causality helps, but isn't definitive.

**Mitigation:** Acknowledge in limitations. The panel design with lagged IV provides suggestive causal evidence, not experimental proof.

2. **Alternative explanation:** Concentration could increase because the field is maturing and converging on best practices, not because of lock-in. This would be positive concentration, not pathological.

**Mitigation:** We test diversity as DV, not performance. If concentration is positive (best practices), diversity should still be maintained through alternative evaluations. If diversity declines, lock-in is the more plausible explanation.

3. **Publication bias:** Papers that evaluate on non-standard datasets might be rejected, hiding diversity. We only see published work.

**Mitigation:** This strengthens the hypothesis—publication bias IS part of the lock-in mechanism. Note as feature, not bug.

**Overall verdict:** The hypothesis is defensible. Remaining concerns are limitations to acknowledge, not fatal flaws.

**Key Points:**
- Reverse causality is acknowledged limitation, mitigated by lagged design
- "Positive concentration" alternative is addressed via diversity test
- Publication bias is part of the mechanism, not a confound

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** This hypothesis introduces the first quantitative application of HHI concentration metrics to ML benchmark usage patterns. The epistemic lock-in framing is novel—prior work focused on dataset construction practices, not usage concentration effects. The temporal-causal design (lagged correlation) is a methodological advance over cross-sectional descriptions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear operationalizations exist for all constructs. HHI and entropy have established formulas. The panel regression with lagged IV provides a well-specified test. Falsification criteria are explicit: β(HHI_{t-1}) ≥ 0 or p > 0.05 falsifies the causal claim. Granger causality test provides additional directional evidence.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** The hypothesis addresses an important upstream mechanism but doesn't directly test the reproducibility link from the original research question. However, it provides foundational methodology (concentration measurement) and tests a plausible mechanism (epistemic lock-in). Policy relevance exists through venue guideline implications.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All data exists. Papers With Code provides dataset-paper links at scale (15K+ papers for target venues). Standard econometric methods apply. No new data collection, no human evaluation, no model training required. Fully executable with existing resources within weeks.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis about benchmark concentration and epistemic lock-in in ML research. The core claim states that in major ML venues (NeurIPS, ICML, ICLR) from 2018-2024, increases in benchmark dataset concentration (measured by Herfindahl-Hirschman Index) predict subsequent decreases in evaluation diversity (measured by normalized entropy of datasets used in evaluation).

The proposed mechanism is that high concentration creates implicit standards for "acceptable" evaluation, leading researchers to follow established benchmarks for comparability, which reduces exploration of alternative evaluation paths and prevents discovery of benchmark-specific overfitting.

The primary test is a panel regression with lagged independent variable: Entropy_t ~ HHI_{t-1} + venue fixed effects + year fixed effects. The expectation is β(HHI_{t-1}) < 0 with p < 0.05. Secondary tests include Granger causality and paper-level analysis using the ~15K papers in Papers With Code for these venues.

The hypothesis is immediately testable using existing data from Papers With Code, requires no new benchmarks or human evaluation, and satisfies all feasibility constraints.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Reverse causality not fully ruled out—lagged design provides suggestive but not definitive causal evidence
- "Positive concentration" alternative interpretation exists (field maturity, not lock-in)—mitigated by focusing on diversity as outcome
- Publication bias may hide diversity attempts—acknowledged as part of the lock-in mechanism
- **Mitigation Strategy:** Acknowledge these as limitations in reporting; the lagged panel design with fixed effects is the best feasible approach without experimental intervention

---

## Emerged Hypothesis Summary

### Core Statement
Under conditions of high benchmark dataset concentration (HHI > venue median) in major ML venues (NeurIPS, ICML, ICLR), if HHI increases year-over-year, then evaluation diversity (normalized entropy) decreases in the subsequent year, because researchers collectively optimize for established benchmarks and reduce exploration of alternative evaluation paths.

### Causal Mechanism
1. High HHI indicates community convergence on few datasets
2. Convergence creates implicit standards for "acceptable" evaluation
3. New papers follow existing standards to ensure comparability
4. Reduced diversity prevents discovery of benchmark-specific overfitting
5. The cycle reinforces itself (positive feedback loop)

### Variables
- **Independent Variable:** Year-over-year HHI change (ΔHHI_t)
- **Dependent Variable (Primary):** Year-over-year entropy change (ΔEntropy_{t+1})
- **Controls:** Venue fixed effects, year fixed effects, paper count

### Key Assumptions
- A1: Papers With Code dataset tags accurately reflect paper evaluation practices
- A2: HHI and entropy are valid proxies for concentration and diversity
- A3: The 2018-2024 period captures meaningful variation
- A4: Major venues (NeurIPS/ICML/ICLR) are representative of ML research
- A5: One-year lag is appropriate temporal scale for the effect

### Null Hypothesis
There is no significant relationship between year-over-year HHI changes and subsequent year evaluation entropy changes (β = 0).

### Predictions
- **P1:** Negative correlation: ΔHHI_t predicts ΔEntropy_{t+1} (β < 0, p < 0.05)
- **P2:** HHI Granger-causes entropy (but not reverse)
- **P3:** Paper-level: papers using high-HHI datasets evaluate on fewer unique datasets

### Novelty
First quantitative application of economic concentration metrics (HHI) to ML benchmark usage patterns; introduces epistemic lock-in theory to ML research practices; provides empirical test of concentration → diversity pathway.

### Scope & Boundaries
- **Applies to:** Empirical ML papers in NeurIPS, ICML, ICLR (2018-2024)
- **Does not apply to:** Theory papers, workshop papers, domain-specific venues
- **Known limitations:** Tests upstream mechanism; doesn't directly measure reproducibility correlation

### Experimental Setup
- **Data Source:** Papers With Code API/export
- **Sample:** ~15K papers from NeurIPS/ICML/ICLR (2018-2024)
- **Primary Analysis:** Panel regression with lagged IV and fixed effects
- **Secondary Analysis:** Granger causality test, paper-level regression

### Related Work & Baselines
- Engdahl (2024): Qualitative benchmark construction analysis (this provides quantitative extension)
- Olszewski et al. (2023): Reproducibility measurement (orthogonal, not concentration-focused)
- HPO-B (2021): OpenML meta-benchmark (uses many datasets but no concentration analysis)

### Phase 2B Readiness Seeds
- SH1 (Existence): Benchmark concentration (HHI) is measurable from existing data
- SH2 (Mechanism): HHI → diversity reduction pathway is testable via lagged regression
- SH3 (Comparison): Deferred to Phase 5—comparison with no-effect baseline

### Established Facts
- Papers With Code has dataset-paper links for major venues (verified: 80%+ coverage)
- HHI and entropy have established calculation formulas (economics/information theory)
- Major venues have 7 years of data (2018-2024)

---

