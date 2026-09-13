# Phase 2A Discussion Log
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop — IC Ablation)
**Architecture:** paper-reading-round0-only-then-mcp-search
**Gap ID:** gap-2
**Gap Title:** Absence of Empirical Linkage Between Metadata-Observable Dataset Misuse and Reproducibility Failure Outcomes
**Execution Mode:** UNATTENDED
**Date:** 2026-08-31

---

## Briefing Context

### Selected Research Gap

**Gap 2:** No study has connected metadata-observable dataset misuse signals (task-type drift, documentation incompleteness, usage concentration) with labeled reproducibility failure outcomes at the paper-dataset level.

**Core Missing Piece:** A matched dataset of (paper, benchmark dataset) pairs from existing reproducibility studies (Raff 2019; ML Reproducibility Challenge) cross-referenced with metadata-observable misuse signals extracted programmatically from OpenML, HuggingFace Hub, and UCI APIs, plus a statistical test measuring whether misuse signals predict reproducibility failure.

**Feasibility Constraints (MANDATORY):**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- Only existing real datasets and benchmarks

### Available Paper Summaries

- P1: Raff 2019 — reproducibility labels for 255 papers (ground truth)
- P2: D'Amour et al. 2021 — underspecification / benchmark overuse mechanism
- P3: Gebru et al. 2021 — datasheets for datasets / HF card completeness scoring

### Previous Failure / Routing Context

No previous Phase 2A attempts. No Serena memory files found. First execution.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The most exciting angle here is that we're proposing something no one has done: use *repository metadata as a misuse signal proxy*, then ask whether that proxy predicts an independently-established ground truth (Raff's reproducibility labels). Let me propose three angles worth exploring.

**Angle A — Task-Type Drift as Primary Signal.** HuggingFace dataset cards carry `task_categories` (what the dataset was designed for) and `intended_use` free-text fields [Gebru et al., 2021]. When papers apply a dataset to tasks outside those declared categories — say, using a sentiment corpus as a factuality benchmark — that's operationalized misuse. We can extract paper-dataset pairs from Raff's 255-paper corpus, retrieve the HF card for each dataset, then compute a binary "task-type mismatch" flag and correlate with reproducibility outcome. This is fully automatable from existing APIs.

**Angle B — Documentation Completeness Score as Predictive Feature.** Rather than a binary mismatch, compute a continuous completeness score: how many of the standard Datasheets fields (motivation, intended use, out-of-scope use, limitations, provenance) are present in the HF/OpenML record? If low-completeness datasets systematically appear in non-reproducible papers, that's an actionable finding for platform administrators.

**Angle C — Concentration + Drift Combined Signal.** The HHI (Herfindahl-Hirschman Index) over dataset usage counts from OpenML measures overuse concentration. Pair this with task-type drift from HF cards to build a two-dimensional misuse space. Papers using high-concentration AND high-drift datasets should have the worst reproducibility.

The novelty is the *linkage* — connecting two previously-separate literatures (dataset documentation and reproducibility auditing) via programmatic metadata extraction. Raff's 255-paper corpus is our lucky break: it's the only labeled ground truth that's large enough and already published.

**Key Points:**
- Task-type drift operationalized from HF `task_categories` vs. paper's stated task
- Documentation completeness score from HF card field presence
- Concentration (HHI from OpenML run counts) + drift = 2D misuse signal
- Ground truth: Raff 2019 binary reproducibility labels (no new annotation needed)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's three angles are promising, but before we commit to any of them we need to be precise about what can actually be *measured* versus what requires inference or human judgment. Let me stress-test each angle.

**On Angle A (Task-Type Drift):** The fundamental problem is that "task-type mismatch" requires knowing what task the paper used the dataset *for* — which is paper-level information, not metadata-level. The HF card tells us the dataset's intended category; the paper tells us the actual application. Extracting paper-level task application from 255 PDFs without human annotation requires NLP over paper text. That's feasible (title/abstract often state the task), but we should be honest: it introduces parsing error. The *cleanest* operationalization is to use only the HF card's `task_categories` field and check whether the dataset appears in the Raff corpus at all — papers that re-used a dataset outside its primary domain will cluster in certain task-mismatch cells.

**On Angle B (Documentation Completeness):** This is the most rigorous angle because it requires no paper-text parsing. We can compute completeness scores for all datasets in Raff's corpus purely from HF Hub API calls. The hypothesis becomes: *datasets with lower completeness scores at time of publication appear disproportionately in non-reproducible papers*. Testable with a Wilcoxon rank-sum test or logistic regression. The confound to control: older datasets (pre-2018) have lower completeness simply because the datasheet standard didn't exist yet — we need to include dataset age as a covariate.

**On Angle C (HHI Concentration):** OpenML's `list_datasets()` returns run counts per dataset. HHI is straightforward. But OpenML ≠ HuggingFace ≠ UCI — identity resolution across repos is non-trivial. For Raff's corpus specifically, we can manually look up the ~20-30 unique datasets he used and get their OpenML IDs. This makes the cross-repo problem tractable at the scale of Raff's corpus even if the general case is hard.

**My recommendation:** Focus the primary hypothesis on Angle B (documentation completeness predicts reproducibility failure) using Raff's 255-paper corpus as ground truth, with Angle C as a secondary variable. This is fully automatable, rigorous, and falsifiable. P-value threshold: 0.05 after Benjamini-Hochberg correction for multiple comparisons.

**Key Points:**
- Angle A requires paper-text NLP — adds noise, weakens rigor
- Angle B is fully automatable from HF Hub API — cleanest design
- Angle C requires identity resolution across repos — tractable at Raff's scale
- Control for dataset age as confound in completeness analysis
- Logistic regression with Benjamini-Hochberg correction is the statistical test

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both Dr. Nova and Prof. Vera have identified real tensions. Let me focus on *impact* — what finding would actually change practice?

The documentation completeness angle (Angle B) is clean and rigorous, but its policy implication is modest: "fill out your dataset cards better." That's already the message of Gebru et al. [2021] — we'd be providing empirical support for an existing recommendation, not a new one.

What would be genuinely impactful is showing that **concentration** — the fact that a small number of datasets dominate ML research — is a *measurable predictor of reproducibility failure*, independent of documentation quality. If we can show that papers using overused datasets (high HHI) fail to reproduce at higher rates even when controlling for documentation completeness, that's a structural argument: the problem isn't just bad documentation, it's monoculture in benchmark choice. That changes the conversation from "write better cards" to "use different datasets."

This suggests the following study design for maximum impact:
1. Primary predictor: dataset concentration index (HHI over OpenML/HF usage counts for datasets in Raff's corpus)
2. Secondary predictor: documentation completeness score (HF card field presence)
3. Outcome: Raff's binary reproducibility label
4. Model: logistic regression with both predictors + dataset age covariate
5. Novel claim: concentration independently predicts failure (above and beyond documentation quality)

The "above and beyond" framing is critical for novelty — it means even well-documented, overused datasets are reproducibility risks. That's a structurally new claim.

**Key Points:**
- Concentration as independent predictor is the high-impact novel claim
- Documentation completeness as secondary predictor / control
- "Above and beyond documentation quality" framing maximizes novelty
- Logistic regression with both predictors tests the independent contribution of each
- Raff's 255 papers: ~N=255 obs, ~20-30 unique datasets — dataset-level clustering needed

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Good discussion. I need to bring this down to Earth before we over-commit.

**Feasibility reality check on sample size:** Raff's corpus has 255 papers, but each paper typically uses 1-3 datasets. The *unique datasets* in the corpus are likely 30-60 (many papers share MNIST, CIFAR-10, ImageNet, etc.). Our predictors (HHI, completeness score) are *dataset-level*, not *paper-level*. This creates a multilevel structure: papers nested within datasets. With 30-60 unique datasets, the dataset-level analysis has very low power for detecting dataset-level effects. We need to think carefully about whether we model at the paper level (N=255 with dataset-level predictors as covariates) or the dataset level (N=30-60).

**Paper-level modeling:** Each paper is an observation. Predictors are the dataset-level HHI and completeness score of the dataset(s) it uses (average if multiple). Outcome is Raff's reproducibility label. N=255 gives reasonable power (>80%) for detecting a moderate effect (OR>1.5) in logistic regression. This is feasible.

**HF API availability:** HuggingFace Hub API (`huggingface_hub.list_datasets(full=True)`) returns metadata for public datasets. But datasets in Raff's 2013-2018 corpus may not have HF cards at all — HuggingFace launched in 2020. Older datasets (UCI origins, custom Kaggle downloads) will have missing metadata. Missing data handling: use OpenML quality measures as fallback, or treat absence of HF card as completeness=0 (conservative assumption, defensible).

**OpenML run counts for HHI:** OpenML's `list_runs()` by dataset gives usage counts as of today, not as of paper publication date. This introduces temporal confound: a dataset popular today may not have been overused at time of paper writing. Mitigation: use OpenML's task creation timestamps to filter runs prior to paper publication year. Feasible but adds implementation complexity.

**My feasibility verdict:** The study is feasible at N=255 (paper-level) with completeness=0 imputation for missing HF cards and temporal filtering for OpenML run counts. Estimated implementation time: 2-3 weeks with Python (openml-python + huggingface_hub + scipy). No external dependencies beyond public APIs. **GREEN LIGHT** with these caveats documented.

**Key Points:**
- Model at paper level (N=255), dataset-level predictors as covariates — sufficient power
- Missing HF cards: treat as completeness=0 (conservative, defensible)
- OpenML temporal filtering needed: filter runs to pre-publication year
- Implementation: ~2-3 weeks, openml-python + huggingface_hub + scipy
- GREEN LIGHT for feasibility

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent. The discussion has converged on a clear design. Let me synthesize and strengthen it.

**Synthesized Hypothesis:**

Under the condition of published ML papers that use standard benchmark datasets, if a paper relies on a dataset with higher usage concentration (measured by HHI over OpenML run counts filtered to pre-publication period) and lower documentation completeness (measured by HF card field-presence score), then that paper is more likely to fail independent reproducibility verification (as labeled by Raff 2019), because high concentration signals that the dataset has accumulated dataset-specific artifacts that models overfit to (D'Amour et al. 2021), while low documentation completeness increases the risk that the dataset's scope boundaries were never clearly specified, enabling out-of-context application.

**Strengthening moves:**

1. **The "above and beyond" test** (Dr. Sage's framing): Use a hierarchical logistic regression — Model 1: completeness only; Model 2: completeness + concentration. If concentration adds significant predictive power beyond completeness (likelihood ratio test p<0.05), we have the novel claim.

2. **Operationalization of concentration:** HHI computed over OpenML run counts per dataset, filtered to runs created before the paper's publication year. Higher HHI = more concentrated. Normalize to [0,1] for interpretability.

3. **Operationalization of completeness:** Count presence of: `intended_use`, `out_of_scope_use`, `limitations`, `license`, `task_categories`, `dataset_info` (size/format), `provenance/source_datasets` in HF card. Score 0-7. Missing card = 0. Normalize to [0,1].

4. **Secondary validation:** Replicate the key finding on ML Reproducibility Challenge 2021 data (separate from Raff) if accessible from Papers with Code reproducibility entries — serves as out-of-sample validation.

5. **Causal mechanism citation:** D'Amour et al.'s underspecification framework provides the theoretical mechanism linking concentration to failure — cite it explicitly in the hypothesis justification.

**Key Points:**
- Hierarchical logistic regression: Model 1 (completeness) vs. Model 2 (completeness + concentration)
- HHI from OpenML filtered to pre-publication runs — temporal validity
- Completeness: 0-7 field-presence score from HF card, missing=0
- Secondary validation: ML Reproducibility Challenge 2021 data
- Mechanism grounded in D'Amour et al. 2021 underspecification theory

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Strong synthesis from Dr. Ally, but I have three concerns that could sink this if not addressed.

**Concern 1 — Confound: paper quality, not dataset misuse.** The most obvious alternative explanation for Raff's reproducibility findings is simply *paper quality*: well-written papers with clear methodology reproduce better, regardless of which dataset they use. If high-quality papers also tend to choose well-documented datasets (because quality researchers care about documentation), the completeness effect is spurious. Mitigation: include paper-level quality proxies as controls — number of equations, pseudocode presence, hyperparameter reporting (Raff already coded these features). We need to show the dataset-level misuse signals predict reproducibility *above and beyond* these paper-level controls.

**Concern 2 — Selection bias in Raff's corpus.** Raff selected 255 papers from top venues (NeurIPS, ICML, ICLR, JMLR). These are *already* high-quality papers. The range restriction in paper quality may attenuate the paper-quality confound — paradoxically making our dataset-level effects more visible, but also meaning results may not generalize to lower-quality venues. Acknowledge as a scope limitation.

**Concern 3 — Temporal validity of HHI.** Prof. Pax flagged this correctly. OpenML run counts today include years of post-publication runs. The "overuse" a paper experienced at time of writing is different from today's HHI. We need to either (a) filter OpenML runs to pre-publication year (as Prof. Pax proposed) or (b) use HF download counts filtered by year (HuggingFace dataset statistics API provides this). If neither is feasible, we can use the dataset's publication year as a proxy — datasets published many years before the paper have had longer to accumulate overuse.

**Mitigation Strategy:**
- Add Raff's paper-quality features (equations, pseudocode, hyperparameters) as controls in logistic regression
- Run robustness check: re-run analysis excluding papers where dataset-paper quality correlation r>0.3
- For HHI: use dataset publication year gap as proxy if temporal run filtering is infeasible
- Pre-register the analysis plan before running to prevent HARKing

**Key Points:**
- Paper quality confound: include Raff's existing quality features as controls
- Selection bias: acknowledge top-venue scope limitation
- Temporal HHI: filter pre-publication runs or use dataset age as proxy
- Pre-registration before analysis to prevent HARKing
- Falsification criterion: if paper-quality controls eliminate the misuse signal, hypothesis fails

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has sharpened the hypothesis significantly. The paper-quality control is exactly right — and crucially, it's already available in Raff's dataset (he coded equations, pseudocode, hyperparameter reporting). This makes the analysis design cleaner: we're adding *dataset-level* predictors to a model that already has *paper-level* quality predictors, so incremental R² directly measures the contribution of misuse signals.

One additional novelty angle I want to preserve: the **directionality of the documentation effect**. It's not just that low completeness predicts failure — it's that the *specific missing fields matter differently*. Hypothesis: `intended_use` and `out_of_scope_use` missing predicts failure more strongly than `license` or `provenance` missing, because the former fields directly encode whether the dataset was designed for the task the paper applied it to. This creates a feature importance analysis within the completeness score that is both novel and actionable (platform admins know which fields to prioritize).

This is testable with the same logistic regression: instead of a composite score, use each field as a separate binary indicator. The coefficient magnitudes reveal which fields matter most. No additional data collection needed.

**Key Points:**
- Field-level importance within completeness: `intended_use` and `out_of_scope_use` should dominate
- Testable via separate binary indicators in logistic regression (no composite score needed)
- Results are actionable: platform admins prioritize the fields that matter most
- Incremental R² from adding dataset-level predictors to Raff's paper-quality model = clean novelty test

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion has converged on a design that is rigorous, testable, and feasible. Let me formalize the falsification structure.

**Primary Prediction (P1):** In logistic regression predicting Raff's binary reproducibility label, documentation completeness score (HF card field presence, 0-7) will have a significant negative coefficient (β < 0, p < 0.05, BH-corrected) after controlling for paper-quality features from Raff's original coding scheme. Falsification: β ≥ 0 or p ≥ 0.05 after correction.

**Secondary Prediction (P2):** Dataset concentration (HHI over OpenML pre-publication run counts) will add significant predictive power above documentation completeness alone (likelihood ratio test between Model 1: completeness+controls vs. Model 2: completeness+concentration+controls, p < 0.05). Falsification: LRT p ≥ 0.05.

**Tertiary Prediction (P3):** Among completeness fields, `intended_use` and `out_of_scope_use` indicators will have larger coefficient magnitudes than `license` and `provenance` indicators in a field-level logistic regression. Falsification: `license` or `provenance` coefficient ≥ `intended_use` coefficient.

All three predictions are testable with existing data (Raff's labeled corpus + HF Hub API + OpenML API), require no human annotation, and use standard statistical tests. The study is pre-registerable.

**Key Points:**
- P1: completeness negative predictor of failure (primary)
- P2: concentration adds predictive power above completeness (novel contribution)
- P3: intended_use/out_of_scope_use dominate field-level importance
- All testable from existing APIs + Raff's labeled corpus — no new data collection
- Pre-registration: OSF or AsPredicted before data pull

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The linkage between metadata-observable misuse signals and Raff's reproducibility labels is genuinely novel — no prior study has made this connection. The field-level importance analysis (which specific datasheet fields predict failure) adds a second layer of novelty that is actionable for platform designers. The mechanism (via underspecification theory from D'Amour et al.) provides theoretical grounding that elevates this above purely correlational work.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three distinct falsifiable predictions with pre-specified significance thresholds and correction for multiple comparisons. All data sources are existing public APIs. The incremental predictive power framing (Model 1 vs. Model 2 LRT) is a well-established test of unique contribution. Prof. Rex's paper-quality confound is addressed by including Raff's original quality features as controls.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Two distinct policy audiences: (1) platform administrators can prioritize `intended_use` and `out_of_scope_use` fields in dataset cards; (2) journal editors and reproducibility reviewers can flag papers using high-concentration datasets as higher reproducibility risk. The "concentration independently predicts failure" claim (P2) would justify structural changes in how ML venues handle dataset diversity.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Paper-level analysis with N=255 provides sufficient power. Missing HF cards (older datasets) handled with completeness=0 imputation — a conservative, defensible choice. OpenML temporal filtering is implementable via task creation timestamps. Implementation uses three existing Python libraries (openml-python, huggingface_hub, scipy) with no novel tooling. Estimated 2-3 weeks.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on the following hypothesis: Among ML papers in Raff's 255-paper reproducibility audit corpus, papers that use benchmark datasets with lower documentation completeness scores (measured from HuggingFace dataset card field presence using the Datasheets for Datasets schema) and higher usage concentration (measured by Herfindahl-Hirschman Index over OpenML run counts filtered to pre-publication period) are significantly more likely to fail independent reproducibility verification, above and beyond the predictive effect of paper-level quality features already established in Raff's original study.

The mechanism is grounded in D'Amour et al.'s underspecification theory: high-concentration datasets accumulate dataset-specific artifacts that models overfit to, causing failure under novel conditions; while low documentation completeness increases out-of-context application risk by failing to specify scope boundaries. The study uses logistic regression with two nested models to test the independent contribution of concentration above completeness, with field-level importance analysis identifying which specific datasheet fields drive the effect. All analysis uses existing public APIs and labeled data — no new benchmarks, annotation, or synthetic data required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Paper-quality confound: high-quality papers both reproduce better AND choose better-documented datasets — must include Raff's quality features as controls (equations, pseudocode, hyperparameter reporting)
- Temporal HHI validity: OpenML run counts today ≠ overuse at time of paper writing — filter pre-publication runs or use dataset age as proxy
- Selection bias: Raff's corpus is top-venue papers only — results may not generalize to conference workshops or preprints
- **Mitigation Strategy:** Include paper-quality controls in all models; use task creation timestamps for temporal filtering; explicitly scope claims to top-venue ML papers; pre-register analysis plan before data pull to prevent HARKing
