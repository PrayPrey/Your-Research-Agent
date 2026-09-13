# Phase 2A Research Discussion Log

**Gap ID:** gap-3
**Gap Title:** Lack of Large-Scale Empirical Evidence Linking FAIR Compliance to ML Research Outcomes
**Initialized:** 2026-05-04
**Architecture:** Self-Contained Tikitaka Loop v9.0.0
**Execution Mode:** UNATTENDED

---

## Research Briefing

### Selected Research Gap

**Gap 3 (CRITICAL / PRIMARY):** No large-scale empirical study has linked FAIR compliance scores
to ML research outcomes (Sub-Q 4), despite FAIR tags existing in OpenML metadata.

**Current State:** FAIR principles well-defined (Wilkinson et al., 2016, ~20,000 citations);
F-UJI provides automated scoring for general scientific data; OpenML/HuggingFace contain
FAIR-related metadata. No ML-specific large-scale FAIR-outcome correlation study exists.

**Missing Piece:** Large-scale observational study:
(a) compute FAIR scores for ML datasets via automated scoring (adapting F-UJI),
(b) measure reuse frequency and downstream performance from existing OpenML/HuggingFace APIs,
(c) statistical comparison of high-FAIR vs. low-FAIR groups.
Natural quasi-experimental design already exists in OpenML metadata.

**Why this gap matters:** Directly actionable by OpenML, HuggingFace, UCI administrators;
provides empirical validation for FAIR investment in ML. Connects to ICLR 2025 Workshop
theme on "The Future of Machine Learning Data Practices and Repositories."

### Available Data Sources

- **OpenML Python API** (openml/openml-python, ~500 stars): FAIR metadata + task API,
  leaderboard-style task performance data, dataset usage statistics
- **HuggingFace Datasets API** (huggingface/datasets, ~19,000 stars): Dataset card metadata,
  download counts, likes, tags including FAIR-related fields
- **F-UJI Automated FAIR Scoring** (pangaea-data-publisher/fuji, ~200 stars):
  Automated FAIR scoring tool adaptable for ML repositories
- **Semantic Scholar API**: Citation context analysis for measuring research outcome
- **Papers With Code**: Leaderboard-style performance data for downstream model performance

### Key Papers in Context

- Wilkinson et al. (2016) — "The FAIR Guiding Principles" (~20,000 citations): foundational FAIR
- Vanschoren et al. (2014/2019) — "OpenML: Exploring ML Better" (arXiv:1407.7722, ~800 citations):
  Primary data source; FAIR-adjacent metadata available but no outcome correlation
- Gebru et al. (2021) — "Datasheets for Datasets" (arXiv:1803.09010, ~2,000 citations):
  Documentation dimensions relevant to FAIR compliance measurement
- Pineau et al. (2020) — "Improving Reproducibility in ML" (arXiv:2003.12206, ~500 citations):
  Reproducibility as outcome variable

### Feasibility Constraints (Pipeline-Enforced)

✅ ACCEPTED: Hypotheses testable with existing real datasets and existing benchmarks
❌ REJECTED: New benchmarks, rubrics, or scoring frameworks
❌ REJECTED: Synthetic/generated data or future follow-up data
❌ REJECTED: Human evaluation, annotation, or subjective scoring

### Research Questions to Address

1. Do FAIR-tagged ML datasets show measurably different reuse frequency, citation counts,
   or downstream model performance vs. non-FAIR-tagged datasets?
2. Which FAIR dimensions (Findable, Accessible, Interoperable, Reusable) most strongly
   predict better ML research outcomes?
3. Can automated FAIR scoring (F-UJI adapted for ML) serve as a proxy for ML research quality?

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been thinking about FAIR compliance entirely backwards? The existing literature treats FAIR as a normative framework — a checklist that datasets *should* satisfy. But what if we flip it into a *predictive instrument*? Here's what excites me: OpenML has tens of thousands of datasets, some tagged with FAIR-adjacent metadata, and we can observe their natural reuse trajectories over years. This isn't a controlled experiment — it's better. It's a natural experiment where FAIR compliance emerged organically, not by design, giving us variance we couldn't engineer.

The truly novel angle here is that we're not asking "does FAIR compliance *cause* better outcomes?" We're asking something sharper: "Does FAIR compliance, as *actually implemented* in ML repositories (not as idealized by Wilkinson et al., 2016), predict the empirical signals we care about — reuse frequency, citation counts, downstream model performance on OpenML tasks?"

What excites me most is the F-UJI tool angle. F-UJI was designed for general scientific data, but nobody has asked: does it transfer to ML datasets? The F-UJI scoring dimensions might not map cleanly onto ML-specific FAIR concerns. This is a hidden hypothesis within the main one — a cross-domain validity question about the instrument itself. What if F-UJI scores on ML datasets systematically diverge from the "true" FAIR compliance that predicts ML outcomes? That divergence itself would be a finding!

And here's my paradigm-shift proposal: instead of treating all 4 FAIR dimensions equally, we could ask which *specific* FAIR subdimensions have the strongest marginal predictive power for ML outcomes. "Reusable" might matter far more than "Findable" for citation impact. "Interoperable" might matter most for downstream model performance. Disaggregating FAIR into its constituent dimensions and testing each one's independent predictive power — that's the unexplored research direction that turns a correlation study into a mechanistic one.

**Key Points:**
- Treat FAIR compliance as a predictive instrument, not a normative checklist
- Natural quasi-experimental design in OpenML eliminates selection bias concerns
- F-UJI cross-domain validity is itself a testable sub-hypothesis
- Disaggregate FAIR dimensions to identify which ones drive ML research outcomes

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me immediately identify where this breaks down if we're not careful. The central methodological challenge is **confounding**. FAIR-compliant datasets in OpenML are not a random sample — they're systematically different from non-FAIR datasets in ways that independently predict reuse: older datasets have had more time to accumulate citations; larger, more prominent datasets are more likely to have been FAIRified by their curators; datasets from well-resourced institutions have both FAIR compliance AND better downstream documentation that drives reuse. Any correlation we observe could be entirely spurious.

The question we must ask is: what would convince us this hypothesis is *wrong*? The falsification criterion must be pre-registered. I propose two specific falsifiable predictions that would kill this hypothesis: (1) if high-FAIR datasets have higher citation counts but only because they are older (after controlling for age, FAIR effect disappears), then FAIR compliance has no independent predictive power; (2) if FAIR dimension scores are highly collinear (datasets that score high on one dimension score high on all), then the disaggregation analysis Dr. Nova proposes collapses into a single latent "institutional quality" factor.

The experimental design that would satisfy my standards: a matched observational study. For each high-FAIR dataset, find a propensity-score matched low-FAIR dataset with similar age, task type, and source institution. This controls for the most obvious confounders using entirely existing OpenML metadata — no new data collection needed. The matched design transforms a potentially confounded correlation study into a defensible quasi-experimental comparison.

What specific, measurable predictions can we make? I want to see effect sizes: FAIR compliance group should show ≥20% higher median reuse frequency, ≥15% higher citation counts, and ≥5% better mean downstream task accuracy on matched OpenML benchmarks. If we can't specify these thresholds in advance, we're doing exploratory fishing, not hypothesis testing.

**Key Points:**
- Confounding (age, institution, prominence) is the central threat to validity
- Propensity-score matching on OpenML metadata enables defensible quasi-experimental comparison
- Pre-registered effect size thresholds required: ≥20% reuse, ≥15% citations, ≥5% performance
- FAIR dimension collinearity must be tested — may collapse to single "institutional quality" factor

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why does this matter *now*, and what does it mean for the field beyond this paper? Prof. Vera's rigor is essential, but I want to zoom out to significance before we get lost in methodology.

The ICLR 2025 Workshop framing gives us a clear audience: repository administrators, dataset curators, and ML infrastructure teams. They are currently investing real effort in FAIR compliance without empirical evidence that it improves research outcomes. This is not a theoretical gap — it is an *operational decision-making gap*. Repository admins at OpenML, HuggingFace, and UCI cannot currently justify FAIR compliance initiatives with data. If we show that specific FAIR dimensions predict measurably better outcomes, we give them an evidence-based prioritization framework.

What makes this genuinely new versus incremental? Wilkinson et al. (2016) established FAIR theoretically. ML-specific FAIR adaptations (2019-2021) translated the framework. But nobody has closed the empirical loop: does FAIR compliance, as actually measured in the wild on ML datasets at scale, predict the outcomes ML researchers care about? The empirical closure is the contribution.

This matters because the field has a cargo-cult risk: repositories implement FAIR compliance because it sounds right, not because it demonstrably improves research. If our results show weak or null effects, that's equally important — it tells the community where *not* to invest effort. A null result here would be a major finding, not a failure.

The new research direction this opens: if specific FAIR dimensions predict outcomes, we have an empirical basis for automated repository quality scoring that doesn't require human annotation. That's the follow-on contribution that would make this paper a launching pad, not an endpoint.

**Key Points:**
- Bridges an operational decision-making gap for repository administrators at OpenML, HuggingFace, UCI
- Empirical closure on FAIR's ML research value is the genuine novelty — not theoretical extension
- Null results are equally valuable: tells community where not to invest FAIR compliance effort
- Opens path to automated, annotation-free repository quality scoring as follow-on contribution

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be realistic here about the technical validity of this proposal — not about costs, but about whether the measurement approaches are scientifically sound.

Here's what worries me most: **FAIR score computation validity**. F-UJI was designed and validated for general scientific repositories (like Zenodo, Pangaea). Its scoring rubric checks things like persistent identifiers (DOIs), metadata schema compliance, license clarity. These transfer reasonably to ML datasets. But the "Interoperable" dimension of F-UJI checks for standardized metadata vocabularies (Dublin Core, DataCite schema). ML repositories use their own schemas — HuggingFace cards have YAML front-matter, OpenML uses its own XML/JSON format. Will F-UJI even parse these correctly, or will it systematically score ML datasets as low-interoperability due to schema mismatch, not actual interoperability failure?

This is a fundamental validity question: if F-UJI's Interoperability scores on ML datasets are artifactual (measuring schema familiarity, not true interoperability), the entire disaggregated analysis collapses. What would convince me this is valid: we need to validate F-UJI scores on a small held-out sample of ML datasets against a reasonable ground truth. And here's the key — OpenML already has human-curated quality ratings for some datasets. That's existing data, no new annotation needed. Cross-validating F-UJI scores against OpenML's existing quality labels gives us an instrument validity check within the feasibility constraints.

The mechanism I believe could work: OpenML's API returns `qualities` for each dataset — number of missing values, class balance, feature types. These are machine-computed quality proxies that partially overlap with FAIR compliance concerns. We could use these as a validity anchor for F-UJI scores, testing whether F-UJI scores correlate with OpenML's own quality metrics on the same datasets.

Can the proposed interventions actually work in principle? Yes — OpenML API + F-UJI + HuggingFace metadata are all publicly accessible and programmatically queryable. The pipeline is technically sound.

**Key Points:**
- F-UJI Interoperability dimension may be artifactually low for ML datasets due to schema mismatch
- OpenML's existing machine-computed quality metrics (qualities API) can serve as validity anchor
- F-UJI instrument validity must be checked before using scores as independent variable
- Technical pipeline (OpenML API + F-UJI + HuggingFace metadata) is feasible in principle

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax has identified the critical vulnerability, and YES — we can address it by turning the F-UJI validation problem into a strength. Here's the refined approach: instead of applying F-UJI as a black box and hoping it's valid for ML datasets, we use it as a *feature extractor* and test which of its sub-criteria (not the aggregate score) actually predict ML outcomes. This transforms the validity concern into a research question.

Concretely: F-UJI produces scores on ~17 individual sub-criteria across 4 FAIR dimensions. We can use these 17 scores as features in a regression predicting reuse frequency and citation counts. The coefficients tell us which specific FAIR sub-criteria matter for ML research outcomes. If the "Interoperable" sub-criteria all have near-zero coefficients, Prof. Pax is right and we've discovered something important: ML datasets don't benefit from interoperability as F-UJI measures it. If "Reusable" sub-criteria dominate, we've identified the highest-value FAIR investment for ML.

To address Prof. Vera's confounding concern: the propensity-score matching approach is correct, but we can strengthen it further. OpenML provides `creation_date`, `creator`, and `source` fields for most datasets. We match on: (1) creation year quartile, (2) task type (classification/regression/clustering), and (3) dataset size decile. This creates matched pairs from entirely existing metadata — no new data collection, no human annotation. After matching, we run a Wilcoxon signed-rank test (nonparametric, robust to distribution violations) comparing reuse frequency between FAIR and non-FAIR matched pairs.

And I want to defend Dr. Sage's null result point: we should pre-register this as a two-sided test. A null result — FAIR compliance does not predict ML outcomes — is a publishable finding at ICLR Workshop level. It would be the first empirical evidence against FAIR's assumed value in ML, which is arguably more disruptive than confirmation.

**Key Points:**
- Use F-UJI's 17 sub-criteria as features (not aggregate score) to identify which FAIR dimensions matter
- Propensity-score matching on OpenML's creation_date + task type + dataset size decile
- Wilcoxon signed-rank test on matched pairs: nonparametric, robust to distribution violations
- Pre-register as two-sided test — null result (FAIR doesn't predict ML outcomes) is equally publishable

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down if we don't address it head-on: **the reuse frequency measurement problem**. OpenML provides dataset download counts and task creation counts. But "reuse" in the ML sense means something richer — a dataset is meaningfully reused when it appears in a published paper's experiments, not just when someone downloads it. Download counts are a noisy proxy that conflates: (1) actual research use, (2) course project downloads, (3) automated scraping, (4) benchmark pipeline downloads. If we use OpenML download counts as our DV, we're not measuring what we claim.

Show me the evidence for this measurement approach being valid. The Semantic Scholar API provides citation context — we can check whether papers that cite OpenML also name specific datasets. This is a stronger signal. But extracting dataset names from citation contexts requires either exact string matching (fragile) or NLP processing (new methodology). Both have problems: exact matching misses paraphrasing; NLP introduces measurement error we can't validate without ground truth.

What would convince me: use *task performance data* from OpenML as the primary DV instead. When a researcher runs an ML experiment on OpenML, they create a "run" on a specific dataset + task + algorithm. OpenML stores these runs. The number of runs on a dataset is a cleaner measure of research use — it requires deliberate experimental engagement, not just downloading. It's already structured data, already in OpenML's API, and doesn't require citation parsing. This DV is unambiguous, directly reflects research engagement, and is immune to scraping noise.

The secondary DV for citation impact: use HuggingFace `downloads` plus `likes` plus number of models that list the dataset as their training data source (HuggingFace model cards have `datasets` field). This triangulation across download counts + likes + downstream model usage is more robust than any single signal.

**Key Points:**
- OpenML download counts are a noisy proxy — conflate research use with course projects and scraping
- Primary DV should be OpenML **run counts** (structured experimental engagement, already in API)
- Secondary DV: HuggingFace downloads + likes + downstream model usage (triangulated)
- Citation context parsing introduces NLP measurement error — avoid unless validated

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Rex has given us a gift — the run count insight. Let me amplify this and push it further into novel territory.

If OpenML run counts measure *research engagement* with a dataset, then we have a longitudinal measurement instrument hiding in plain sight. OpenML has been accumulating runs since 2014. Each run has a timestamp. This means we don't just have a cross-sectional snapshot of FAIR compliance vs. reuse — we can ask: *does FAIR compliance predict the trajectory of research engagement over time*? Do high-FAIR datasets accumulate runs faster after they're published? Do they sustain research interest longer? Do they show a "late bloom" effect where FAIR compliance becomes more valuable as researchers discover them through better findability?

This longitudinal angle transforms the study from a static correlation into a dynamic predictive model. And here's the paradigm-shift: we could model run accumulation as a survival analysis problem. Time-to-first-run, time-to-100-runs, hazard of "abandonment" (dataset goes X months without a new run). Survival analysis on OpenML run timestamps gives us a richer picture than any single-point comparison. And it's all existing data — OpenML has been collecting this since 2014, giving us up to 12 years of longitudinal data.

What if the true finding is not "FAIR datasets have more runs" but "FAIR datasets sustain research attention longer"? That's the paper-worthy insight for repository administrators: FAIR compliance isn't just about discoverability, it's about dataset longevity as a research resource. Longevity predicts cumulative impact better than peak reuse.

**Key Points:**
- OpenML run timestamps enable longitudinal survival analysis (time-to-first-run, hazard of abandonment)
- 12 years of existing run data (2014–2026) without any new data collection
- Research question refinement: does FAIR predict research attention *trajectory*, not just static reuse count?
- Survival analysis framing: "FAIR compliance extends dataset research longevity" is more actionable than simple correlation

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The survival analysis idea is intellectually appealing, but I must apply the evidence test immediately: what result would convince us this hypothesis is *wrong*?

Dr. Nova's survival analysis framing introduces a new identification problem: **left censoring**. Datasets created before FAIR principles existed (pre-2016) cannot have been FAIR-compliant at creation — they may have been retroactively tagged. If retroactive FAIR tagging is common in OpenML, the "treatment" (FAIR compliance) was applied *after* the outcome (run accumulation) had already started. This reverses the causal arrow. We would be measuring whether *high-reuse* datasets tend to get FAIRified, not whether FAIR compliance drives reuse.

The evidence suggests this is a real threat: OpenML's FAIR-adjacent metadata fields have been added and updated over the repository's history. We can test for this directly: if FAIR scores correlate with dataset creation date (older, well-established datasets are more FAIR-compliant), left censoring contamination is likely. This test uses only existing OpenML metadata.

The precision I require: the survival analysis is valid only for the cohort of datasets where FAIR compliance metadata was present *at the time the dataset was first published to OpenML*. This requires checking OpenML's dataset version history or changelog metadata. If that's available, we have a clean cohort. If not, we must restrict analysis to datasets created post-2018 (after FAIR became standard in ML) and use creation date as an instrument.

Testable prediction with falsification criterion: In the clean post-2018 cohort, high-FAIR datasets should show a Kaplan-Meier survival difference (log-rank p < 0.05) in time-to-50-runs. If the log-rank test is non-significant, the survival analysis fails to support the hypothesis.

**Key Points:**
- Left censoring threat: retroactive FAIR tagging may reverse causal arrow (high-reuse → FAIR, not FAIR → reuse)
- Test: FAIR score correlation with creation date detects retroactive tagging contamination
- Clean analysis cohort: restrict to datasets where FAIR metadata was present at publication (post-2018 if needed)
- Falsification criterion: Kaplan-Meier log-rank p < 0.05 in time-to-50-runs for post-2018 cohort

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's left censoring identification is exactly right, and it's testable. Let me assess whether the proposed measurement instruments are technically valid for the post-2018 cohort restriction.

OpenML's API returns `upload_date` for each dataset — this is when it was first added to OpenML. For the post-2018 cohort, we can retrieve all datasets with `upload_date >= 2018-01-01`. As of 2026, that's approximately 8 years of data with clean temporal ordering. The OpenML Python API supports filtered queries on upload_date, so cohort construction is technically straightforward.

The more fundamental question is whether F-UJI can be run programmatically at scale on 10,000+ datasets. F-UJI requires a dataset landing page URL as input. OpenML provides landing page URLs for each dataset. But F-UJI makes HTTP requests to those URLs to check persistence, accessibility, and metadata. At scale (10,000+ datasets), this creates two valid technical concerns: (1) rate limiting by OpenML's servers, and (2) runtime (F-UJI takes ~10-30 seconds per dataset). For 10,000 datasets, that's 28-83 hours of sequential processing.

Can this work in principle? Yes — with parallelization (asyncio or multiprocessing) and respectful rate limiting. The F-UJI source code is open and supports batch processing patterns. This is a matter of implementation, not fundamental impossibility. The parallelization approach is standard and well-understood.

What worries me more: the HuggingFace "downstream model usage" DV that Prof. Rex proposed. Extracting which models used which training dataset requires parsing HuggingFace model card YAML `datasets` fields at scale. HuggingFace's API supports this via `huggingface_hub` library. Technically valid, though completeness depends on how consistently model card authors fill in the `datasets` field — likely sparse for older models.

**Key Points:**
- OpenML `upload_date` enables clean post-2018 cohort construction via existing API filter
- F-UJI at scale (10,000+ datasets) requires parallelization but is technically feasible in principle
- HuggingFace downstream model usage DV is technically accessible but may be sparse for older models
- All proposed DVs are technically extractable from existing public APIs without new data collection

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've now stress-tested the hypothesis from five angles. Let me synthesize what's emerged and propose the refined, convergence-ready hypothesis statement.

The discussion has converged on a specific, mechanistically grounded hypothesis: **FAIR compliance, as measured by automated F-UJI sub-criteria scores applied to ML datasets in OpenML, predicts longitudinal research engagement (measured by OpenML run accumulation trajectories) and downstream model adoption (measured by HuggingFace model card dataset citations), independently of confounders (dataset age, task type, size), in a post-2018 cohort where FAIR metadata was present at publication time.**

This is stronger than the original gap statement in four ways:
1. **Instrument specificity**: F-UJI sub-criteria (not aggregate score) → identifies which FAIR dimensions matter
2. **DV precision**: run accumulation trajectories (not download counts) → measures deliberate research engagement
3. **Causal identification**: post-2018 cohort + propensity matching → addresses left censoring and confounding
4. **Longitudinal framing**: survival analysis → reveals trajectory effects, not just static snapshots

The null hypothesis is clean: no significant difference in run accumulation trajectories between high-FAIR and low-FAIR matched dataset pairs in the post-2018 OpenML cohort, controlling for task type and dataset size.

The three testable predictions are:
- P1: Kaplan-Meier log-rank p < 0.05 for time-to-50-runs between high-FAIR and low-FAIR matched cohort
- P2: Among F-UJI sub-criteria, "Reusable" dimension coefficients show largest effect on run counts (β > 0.15 in regression)
- P3: High-FAIR datasets show ≤30% hazard of research abandonment (no new runs in 24 months) vs. low-FAIR datasets

Everything uses existing OpenML data, existing HuggingFace metadata, and the existing F-UJI tool. No new benchmarks, no synthetic data, no human annotation.

**Key Points:**
- Refined hypothesis: FAIR sub-criteria scores predict longitudinal run accumulation trajectories in post-2018 OpenML cohort
- Three pre-registered predictions with specific numerical falsification thresholds
- All data sources are existing, public, and programmatically accessible
- Null hypothesis is statistically clean and pre-registerable

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally has done excellent synthesis work. Here's where it still breaks down — two remaining gaps I need addressed before I'm satisfied.

**Gap 1: The FAIR threshold definition problem.** To classify datasets as "high-FAIR" vs "low-FAIR" for the matched pairs analysis, we need a threshold. Where does it come from? If we use the median F-UJI score as the threshold, we've defined high/low relative to the sample — this is circular and creates sensitivity to sample composition. If we use F-UJI's own built-in thresholds (≥0.5 = compliant), we're accepting F-UJI's normative judgment without ML-specific validation. Either approach is defensible, but we must pre-commit to one and justify it. My requirement: the threshold must be defined before looking at the outcome data (pre-registration). Using F-UJI's built-in 0.5 threshold avoids circularity and is justifiable as "following the instrument's own standards." That's the approach I'd accept.

**Gap 2: The representativeness scope problem.** OpenML's dataset universe (~5,000 datasets) is not a representative sample of all ML datasets — it overrepresents tabular/structured data (classification, regression on UCI-style datasets) and underrepresents image/text/multimodal datasets that dominate modern ML. HuggingFace has millions of datasets, with different FAIR compliance cultures. Our findings may be internally valid for tabular OpenML datasets but not generalizable to the broader ML dataset ecosystem. This scope limitation must be explicit in the hypothesis statement and acknowledged as a boundary condition.

What would convince me this is addressed: stratify results by dataset modality (tabular vs. image vs. text vs. other) using OpenML's feature type metadata. If FAIR effects are consistent across modalities within OpenML, generalizability is at least partially supported within OpenML's scope.

**Key Points:**
- Pre-commit to F-UJI's built-in 0.5 threshold for high/low FAIR classification — avoids circular median-based thresholding
- OpenML overrepresents tabular data — scope limited to tabular/structured ML datasets
- Stratify by modality (tabular/image/text) to assess within-sample generalizability
- Both gaps are addressable without new data collection or new annotations

---

### Exchange 12

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has identified the scope limitation brilliantly, and I want to turn it into a feature rather than a bug. What if we design the study as a **multi-repository comparative analysis** from the start? OpenML for tabular data, HuggingFace for vision/language datasets. The comparison *across* repositories is itself a finding: do FAIR effects generalize across dataset modalities and repository cultures?

HuggingFace's dataset hub has metadata accessible via `huggingface_hub` Python library. The `datasets` library exposes card data including: tags (some are FAIR-adjacent), download counts, likes, linked model count. We can compute a HuggingFace-specific FAIR proxy score using available metadata fields: (1) has license tag (Reusable), (2) has task_categories tag (Findable/Interoperable), (3) has language/size_categories tags (Accessible metadata), (4) has citation information in README (Reusable). This 4-dimension proxy doesn't require F-UJI at all for HuggingFace — it uses native metadata fields.

The cross-repository design now has three contributions:
1. OpenML: F-UJI sub-criteria → run accumulation trajectories (survival analysis)
2. HuggingFace: metadata-derived FAIR proxy → downloads + likes + downstream model adoption
3. Cross-repository: are FAIR effects consistent across tabular (OpenML) and vision/NLP (HuggingFace)?

This is the paradigm shift: we're not just studying FAIR compliance effects — we're studying whether FAIR effects are a universal property of ML datasets or a repository-culture-specific artifact. That cross-repository comparison has never been done, and it's answerable with entirely existing public data.

**Key Points:**
- Multi-repository design: OpenML (F-UJI) + HuggingFace (metadata-derived FAIR proxy)
- HuggingFace FAIR proxy uses native card metadata fields — no F-UJI required for HuggingFace
- Cross-repository comparison tests whether FAIR effects generalize across modalities and repository cultures
- Three-contribution structure: OpenML study + HuggingFace study + cross-repository comparison

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

The multi-repository design Dr. Nova proposes is the right strategic choice for field impact. Let me assess what this means for the community.

The comparison across OpenML and HuggingFace is more than methodological diversity — it tests a fundamental question that repository administrators need answered: *Is investing in FAIR compliance universally valuable, or does it depend on the type of repository and the research community it serves?* OpenML serves a tabular data / AutoML community with strong structured practices. HuggingFace serves a deep learning community with more heterogeneous, fast-moving data practices. If FAIR effects are strong in OpenML but weak in HuggingFace (or vice versa), repository administrators get specific guidance: FAIR matters more for tabular/structured repositories than for vision/NLP repositories, or the reverse.

This matters because: HuggingFace has become the dominant repository for foundation model training data, a segment that ICLR 2025 Workshop explicitly identifies as under-documented. If FAIR compliance has weak effects on HuggingFace dataset reuse (perhaps because discoverability is driven by social network effects — likes, follows — rather than formal metadata quality), that's a finding with direct policy implications: the ML community needs repository design that matches its actual information-seeking behavior, not FAIR norms borrowed from general science.

The research directions this opens: if social signals (likes, follows, model adoption) predict HuggingFace reuse better than FAIR metadata quality, we've identified a new research agenda: *social infrastructure for ML data quality*, distinct from the FAIR framework. That's a genuine paradigm shift with 3-5 year follow-on impact.

**Key Points:**
- Cross-repository comparison answers policy question: is FAIR universally valuable or repository-culture-specific?
- HuggingFace social signals (likes, follows) may outperform FAIR metadata as reuse predictors
- Null FAIR effect on HuggingFace would identify "social infrastructure" as alternative data quality paradigm
- Direct policy relevance for ICLR 2025 Workshop audience: actionable guidance for each repository type

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

I need to stress-test the HuggingFace FAIR proxy that Dr. Nova proposed. The proxy uses: license tag (Reusable), task_categories tag (Findable/Interoperable), language/size_categories (Accessible metadata), citation in README (Reusable). This is a binary scoring approach — each criterion is either present or absent. My concern: this is a 4-bit score (0-4), not a continuous measure. With low variance, statistical power to detect FAIR effects on HuggingFace will be limited.

The evidence suggests HuggingFace dataset cards vary enormously in completeness. A more sensitive proxy: count the *number of filled metadata fields* in the HuggingFace dataset card YAML front-matter, normalized by the number of available fields. This is a continuous measure (0.0–1.0) that captures documentation completeness as a proxy for FAIR compliance. The `datasets` library exposes card data as a Python dict, so this is programmatically extractable.

Testable prediction for HuggingFace component: documentation completeness score (proportion of metadata fields filled) should correlate positively with both download counts (r > 0.15, Spearman) and downstream model adoption count (r > 0.10, Spearman) after controlling for dataset age and modality.

The cross-repository comparison must also be pre-specified: we must commit to what "consistent FAIR effects" means before looking at the data. I propose: effects are consistent if both OpenML and HuggingFace show statistically significant positive associations (same direction) between their respective FAIR measures and their primary DVs. If one shows positive and the other null, effects are inconsistent. If one shows negative, there's a reversal requiring mechanistic explanation.

**Key Points:**
- HuggingFace FAIR proxy: proportion of metadata fields filled (continuous 0–1) is more sensitive than 4-binary score
- Pre-specified cross-repository consistency criterion: both repositories must show same-direction significant associations
- HuggingFace DV predictions: documentation completeness r > 0.15 with downloads, r > 0.10 with model adoption
- `datasets` library exposes card YAML programmatically — continuous completeness score is technically feasible

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me do a final feasibility check on the complete integrated design that has emerged from this discussion.

**Technical validity assessment:**
1. OpenML component: F-UJI applied to post-2018 datasets (upload_date ≥ 2018) → survival analysis on run accumulation. **Valid** — OpenML API supports upload_date filtering; F-UJI is open source and accepts OpenML landing page URLs; run counts and timestamps are in OpenML API. Parallelizable. Cohort size: ~3,000-5,000 datasets estimated.

2. HuggingFace component: continuous documentation completeness score (proportion of filled card YAML fields) → Spearman correlation with download counts and downstream model adoption. **Valid** — HuggingFace Hub API + `datasets` library provide full card YAML; download counts in API; model adoption via search of model cards' `datasets` field. Potential sparsity in downstream model adoption field for older models, but mitigated by using download counts as primary DV.

3. Cross-repository comparison: meta-analysis of effect sizes (Cohen's d for OpenML survival difference, Spearman r for HuggingFace correlations) with pre-specified consistency criterion. **Valid** — comparing standardized effect sizes across repositories is methodologically sound.

4. F-UJI instrument validity check: cross-validate F-UJI sub-criteria scores against OpenML's existing machine-computed `qualities` metrics (correlation analysis). **Valid** — OpenML qualities API is publicly accessible.

Every component uses existing data, existing tools, existing APIs. The proposed interventions can work in principle. The measurement approaches are scientifically sound with the refinements discussed (continuous card completeness score, post-2018 cohort, propensity matching, pre-registered thresholds).

**Okay, this could work** — all six convergence criteria are now addressable. The hypothesis is specific, the mechanism is articulated, we have three pre-registered testable predictions, the novelty is clear, the feasibility is confirmed, and major objections have been addressed.

**Key Points:**
- OpenML component: technically valid with ~3,000-5,000 post-2018 dataset cohort, parallelizable F-UJI processing
- HuggingFace component: continuous card completeness score technically extractable, downloads as primary DV
- Cross-repository meta-analysis of standardized effect sizes is methodologically sound
- All six convergence criteria met: SPECIFIC ✅ MECHANISM ✅ PREDICTIONS ✅ NOVELTY ✅ FEASIBILITY ✅ OBJECTIONS ✅

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The multi-repository comparative design (OpenML + HuggingFace) is genuinely novel — no prior study has compared FAIR compliance effects across repository cultures at scale. The longitudinal survival analysis framing ("FAIR extends dataset research longevity") reframes FAIR compliance from a static checklist into a dynamic predictor of sustained research impact. The potential finding that social signals outperform FAIR metadata on HuggingFace would open an entirely new research agenda on social infrastructure for ML data quality.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three pre-registered predictions with numerical falsification thresholds meet scientific rigor standards. The Kaplan-Meier log-rank test (p < 0.05 for time-to-50-runs) and Spearman correlation thresholds (r > 0.15) are specific and unambiguous. The pre-specified cross-repository consistency criterion prevents post-hoc interpretation. Left censoring is addressed by restricting to post-2018 cohort.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The study closes an operational decision-making gap for repository administrators who currently invest in FAIR compliance without empirical justification. Both confirmatory and null results are publishable at ICLR 2025 Workshop level. The cross-repository comparison has 3-5 year follow-on impact by either validating FAIR as universal ML data infrastructure or redirecting attention to social infrastructure alternatives.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically valid and feasible: OpenML API with upload_date filtering for post-2018 cohort (~3,000-5,000 datasets), parallelizable F-UJI processing, HuggingFace Hub API for continuous card completeness score, cross-repository meta-analysis of standardized effect sizes. No new benchmarks, synthetic data, or human annotation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a well-specified, multi-repository observational study hypothesis: **FAIR compliance in ML datasets — measured by automated F-UJI sub-criteria scores for OpenML tabular datasets and continuous documentation completeness scores for HuggingFace datasets — predicts longitudinal research engagement and downstream adoption, independently of confounders (dataset age, task type, size), across both tabular and vision/NLP dataset repositories.**

The core mechanism: FAIR compliance reduces friction in dataset discovery, access, and integration, leading to higher rates of deliberate research engagement (OpenML run accumulation) and downstream model adoption (HuggingFace model card dataset citations). The causal pathway is mediated primarily through the "Reusable" FAIR dimension. Three pre-registered predictions with numerical thresholds: (P1) Kaplan-Meier log-rank p < 0.05 for time-to-50-runs in matched post-2018 OpenML cohort; (P2) "Reusable" F-UJI sub-criteria show largest coefficients (β > 0.15); (P3) HuggingFace documentation completeness correlates with downloads (r > 0.15) and model adoption (r > 0.10). Null results are equally valued — they would redirect community from FAIR investment toward social infrastructure alternatives. All data sources are existing, public, and programmatically accessible.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- HuggingFace downstream model adoption DV may be sparse for pre-2020 datasets (model cards' `datasets` field inconsistently filled)
- F-UJI Interoperability sub-criteria may produce artifactually low scores for ML datasets due to schema mismatch
- Statistical power depends on post-2018 cohort size — if matched pairs < 500, power insufficient for moderate effects (Cohen's d ≈ 0.3)
- **Mitigation Strategy:** Pre-register power analysis based on cohort size query before data collection; if matched pairs < 500, expand to post-2016 cohort and add FAIR tagging date as covariate to control for retroactive tagging without excluding datasets.

## Emerged Hypothesis Summary

### Core Statement
Under the conditions of ML dataset repositories (OpenML post-2018 cohort for tabular data; HuggingFace for vision/NLP), if a dataset has higher automated FAIR compliance scores (F-UJI sub-criteria ≥ 0.5 for OpenML; documentation completeness proportion for HuggingFace), then it will show significantly higher longitudinal research engagement (run accumulation trajectories on OpenML) and downstream model adoption (downloads + model card citations on HuggingFace), because FAIR compliance reduces friction in dataset discovery, access, and integration, making deliberate research engagement more likely and sustained.

### Causal Mechanism
1. FAIR compliance → reduced discovery friction (Findable dimension: persistent IDs, rich metadata → researchers find dataset via search)
2. Reduced discovery friction → increased first-use rate (Accessible: open license, standard format → lower barrier to initial use)
3. Increased first-use rate + high Reusable scores → sustained research engagement (Reusable: clear provenance, usage terms → confident continued use)
4. Sustained engagement → higher run counts, longer research longevity, more downstream model adoptions

### Variables
- **IV:** FAIR compliance score (F-UJI sub-criteria 0–1 per dimension for OpenML; proportion of filled card YAML fields for HuggingFace)
- **Primary DV (OpenML):** Time-to-50-runs (survival analysis), total run count
- **Primary DV (HuggingFace):** Download count, downstream model adoption count
- **Controlled:** Dataset creation year/quartile, task type, dataset size decile, data modality

### Key Assumptions
- A1: FAIR metadata in OpenML post-2018 was predominantly set at publication time (not retroactively)
- A2: OpenML run counts reflect deliberate research engagement rather than automated pipeline activity
- A3: F-UJI sub-criteria scores are sufficiently reliable for ML datasets (validated against OpenML qualities metrics)
- A4: HuggingFace card completeness is a valid proxy for FAIR compliance in the deep learning community
- A5: Propensity matching on creation year × task type × size adequately controls for major confounders

### Null Hypothesis
There is no significant difference in run accumulation trajectories between high-FAIR and low-FAIR matched OpenML dataset pairs, and no significant correlation between documentation completeness and download counts on HuggingFace, after controlling for dataset age, task type, and size.

### Predictions
- **P1 (Primary):** Kaplan-Meier log-rank p < 0.05 for time-to-50-runs between high-FAIR (F-UJI ≥ 0.5) and low-FAIR (F-UJI < 0.5) matched pairs in post-2018 OpenML cohort
- **P2:** Among F-UJI sub-criteria, "Reusable" dimension shows largest positive regression coefficient (β > 0.15) predicting total run count
- **P3:** HuggingFace documentation completeness score correlates positively with download count (Spearman r > 0.15) and downstream model adoption (r > 0.10)

### Novelty
- First large-scale empirical study comparing FAIR compliance effects across ML repositories (OpenML + HuggingFace)
- First application of survival analysis to model ML dataset research longevity as FAIR outcome
- First disaggregation of FAIR into sub-criteria to identify which dimensions most predict ML research outcomes
- Potential paradigm shift: if social signals outperform FAIR metadata on HuggingFace, establishes "social infrastructure" as alternative to FAIR for ML data quality

### Scope & Boundaries
- Applies to: ML datasets hosted on OpenML (tabular/structured, post-2018) and HuggingFace (vision/NLP, all dates with card metadata)
- Does not apply to: proprietary datasets, datasets not in public repositories, pretraining corpora without structured cards
- Known limitations: OpenML overrepresents tabular data; HuggingFace downstream model adoption DV sparse pre-2020; F-UJI Interoperability may be artifactually low for ML datasets

### Experimental Setup
- **Dataset:** OpenML post-2018 cohort (~3,000-5,000 datasets) + HuggingFace dataset hub (filtered by card availability)
- **Model:** No ML model training — observational study using Kaplan-Meier survival analysis, log-rank test, Spearman correlation, propensity-score matching, linear regression on F-UJI sub-criteria
- **Baselines:** Unadjusted correlation vs. propensity-matched analysis; F-UJI aggregate score vs. sub-criteria disaggregation; OpenML qualities metrics as F-UJI validity anchor

### Related Work & Baselines
- Wilkinson et al. (2016): foundational FAIR — no ML-specific outcome correlation
- Vanschoren et al. (2014/2019): OpenML — primary data source, no FAIR-outcome analysis
- Gebru et al. (2021): Datasheets for Datasets — documentation dimensions, no empirical correlation with outcomes
- Pineau et al. (2020): ML reproducibility checklist — links docs to outcomes but no FAIR framing or large-scale study

### Phase 2B Readiness Seeds
- **SH1 (Existence):** FAIR compliance variance exists in OpenML post-2018 cohort at sufficient scale for matched analysis
- **SH2 (Mechanism):** F-UJI sub-criteria scores reliably measure FAIR dimensions on ML datasets (cross-validated against OpenML qualities)
- **SH3 (Comparison):** FAIR effects are consistent across OpenML and HuggingFace repositories

### Established Facts
- FAIR principles are well-defined with 20,000+ citations (Wilkinson et al., 2016)
- OpenML Python API provides upload_date, run counts, and qualities for all datasets
- HuggingFace Hub API provides card YAML, download counts, and model card dataset fields
- F-UJI tool is open-source and accepts landing page URLs for automated FAIR scoring
- No ML-specific large-scale FAIR-outcome empirical study exists (confirmed by Phase 1 literature review)
