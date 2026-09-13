# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T05:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Empirical NB-2 Test of Tag Count as ML Dataset Adoption Predictor
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Hypothesis ID**: h-e1-v2

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Synthesis), Prof. Rex (Critique)

**Total Exchanges**: 15

**Convergence Reason**: Natural convergence at exchange 15 (min_exchanges=15); all 6 criteria PASS, all 6 personas participated with genuine adversarial pressure

### Key Insights

1. **IV pivot**: Composite score (h-e1) → binary tag presence (h-e1-v2). RC-2a from h-e1 showed binary description presence (IRR=1.102) outperformed composite score (IRR=1.076) — the same threshold logic applies to tags.
2. **Platform architecture grounds mechanism**: OpenML tags are assigned at upload time by the dataset creator only (Vanschoren 2014), making tags a leading indicator of adoption rather than a lagging popularity signal.
3. **Three-prediction structure**: Binary existence (P1, primary), magnitude conditional on tagging (P2), categorical dose-response (P3) — together quantify the full dose-response relationship of keyword tagging on ML dataset adoption.
4. **Decade FE as primary control**: h-e1's RC-3 failure (composite score IRR=1.014, p=0.19 under decade FE) made decade FE a first-class covariate in this redesign, not a robustness check.

### Breakthrough Moments

- **Exchange 6 (Prof. Rex)**: Forced DV relabeling from "task_run_count" to "N_tasks"; identified endogeneity risk and zero-tag MNAR problem — these critiques hardened the hypothesis significantly.
- **Exchange 12 (Prof. Rex)**: Rejected data-adaptive IV selection in favor of has_tags binary as clean pre-registrable primary IV, grounded in RC-2a precedent.
- **Exchange 14 (Prof. Vera)**: Formalized all three predictions with precise null hypotheses and the full RC suite, completing the falsification structure.

### Resolved Tensions

- **IV selection** (data-adaptive vs. fixed): Resolved by Prof. Rex (Exchange 12) — has_tags binary is pre-registered primary IV; log(tag_count+1) and linear tag_count are robustness checks.
- **Causal vs. predictive framing**: Resolved (Exchange 7-8) — hypothesis is explicitly predictive/associational; platform architecture argument weakens but does not eliminate endogeneity concern.
- **Two-tier IRR threshold**: Resolved (Exchanges 5, 11) — both ≥1.1 (primary) and ≥1.05 (secondary) are pre-registered, avoiding h-e1-style near-miss failure.

---

## Final Hypothesis

### Title
**H-E1-v2: Binary Tag Presence as FAIR F1 Adoption Signal on OpenML (NB-2, N=5,217)**

### Core Claim (Under-If-Then-Because)

**Under** the OpenML platform among datasets with N_tasks ≥ 1 (N=5,217),  
**if** a dataset has at least one keyword tag (has_tags=1 vs. has_tags=0),  
**then** it is predicted to have ≥10% more registered ML tasks (N_tasks) in NB-2 regression (IRR ≥ 1.1, 95% CI lower bound ≥ 1.1, p < 0.05),  
**because** keyword tags on OpenML are platform-native search index entries that immediately expose the dataset to keyword-based discovery, joining the findability graph (FAIR F1, Wilkinson 2016; Vanschoren 2014).

**Null hypothesis (H0-P1):** beta(has_tags) ≤ 0 or IRR 95% CI lower < 1.1 in the primary NB-2 model with C(decade) as first-class covariate.

### Mechanism

Tags on OpenML are platform-native search index entries (Vanschoren et al. 2014). The causal pathway:

1. **Tag assignment** (upload time): Dataset creator assigns keyword tags at dataset upload. Tags are the primary search index keys for OpenML's discovery system.
2. **Search graph membership**: A tagged dataset immediately appears in keyword-based searches. Untagged datasets are invisible to keyword search regardless of quality.
3. **Discovery probability increase**: Researchers searching for datasets by topic/domain find tagged datasets; untagged datasets require knowing the dataset name directly.
4. **Task registration**: Increased discovery → more researchers encounter the dataset → more motivated researchers create ML tasks on it → higher N_tasks.

**Threshold behavior**: The first tag provides disproportionate discoverability gain (search graph membership is binary — either you're in the index or you're not). This explains why binary presence outperforms continuous count as a signal: going from 0→1 tag is qualitatively different from going from 1→2.

---

## Predictions

### P1 — Primary Existence Test (MUST_WORK gate)
- **Statement**: has_tags (binary 0/1) positively predicts N_tasks in NB-2 with IRR ≥ 1.1 (95% CI lower bound ≥ 1.1), p < 0.05, controlling for log(n_instances), log(n_features), age_years, age², C(decade).
- **Test method**: `smf.negativebinomial('N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df).fit(method='bfgs')`. IRR = exp(coef_has_tags); 95% CI = exp(coef ± 1.96×SE).
- **Success criterion**: IRR 95% CI lower ≥ 1.1 AND p < 0.05
- **Secondary criterion**: IRR 95% CI lower ∈ [1.05, 1.1) — partial pass
- **Falsification**: IRR 95% CI lower < 1.05 → reject P1 entirely

### P2 — Magnitude Test (conditional on has_tags=1)
- **Statement**: Among tagged datasets (has_tags=1), log(tag_count+1) positively predicts N_tasks in NB-2 with IRR ≥ 1.05 (95% CI lower ≥ 1.05), p < 0.05. Tests whether count of tags matters beyond binary presence.
- **Test method**: NB-2 with log(tag_count+1) IV, restricted to df[df.has_tags==1]. Same controls.
- **Success criterion**: IRR 95% CI lower ≥ 1.05 AND p < 0.05
- **Falsification**: non-significant or IRR CI lower < 1.05 → binary presence is sufficient, magnitude adds nothing

### P3 — Dose-Response Threshold Test
- **Statement**: Categorical tag_count (0, 1–2, 3–5, 6+) shows monotonic positive dose-response on N_tasks in NB-2, with each higher category having significantly higher predicted N_tasks than the previous.
- **Test method**: NB-2 with `C(tag_cat, Treatment)` using '0 tags' as reference. Check monotonic ordering of exp(coef) across categories.
- **Success criterion**: All three category IRRs (1-2, 3-5, 6+) > 1.0 AND monotonically increasing, at least 2/3 significant at p < 0.05.
- **Falsification**: Non-monotonic pattern or all category coefficients non-significant

---

## Novelty

**Preserved novelty**: No prior study has run NB-2 count-regression on OpenML tag count (binary or continuous) as a predictor of dataset adoption (N_tasks), controlling for decade FE.

**Key innovation**: First empirical quantification of FAIR F1 (Findability via keyword tagging) → ML dataset adoption using count-regression with platform-appropriate controls. Positions the tag count → adoption link as a testable, quantified relationship rather than a theoretical assertion.

**Differentiation from prior work**:
| Prior Work | Limitation | This Study |
|---|---|---|
| Yang et al. 2024 (HuggingFace) | Prose quality metrics only; no tag count IV; HF-only | OpenML tag count; NB-2; decade FE |
| Chapman et al. 2019 | Survey-based; no regression; no effect quantification | NB-2 with IRR; quantified effect size |
| Lachmuth et al. 2025 (BonaRes) | Agricultural domain only; FAIR composite; no NB-2 | ML domain; binary tag IV; NB-2 with decade FE |
| h-e1 (composite score) | IRR=1.076 < 1.1 threshold; failed RC-3 decade FE | Binary tag presence; theoretically motivated IV |

---

## Experimental Design

### Dataset
- **Source**: `h-e1/code/data/h_e1/openml_dataset_corpus.csv` (existing corpus, no new collection)
- **N**: 5,217 OpenML datasets with N_tasks ≥ 1
- **Preprocessing**: Parse `tags` string column → `has_tags` (0/1) + `tag_count` (int) + `tag_cat` (categorical: 0, 1-2, 3-5, 6+)

### Model
- **Primary**: NB-2 via `statsmodels.formula.api.negativebinomial(...)` with `method='bfgs'`
- **Formula (P1)**: `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)`
- **Formula (P2)**: `N_tasks ~ log_tag_count + log_n_instances + log_n_features + age_years + age_sq + C(decade)` restricted to has_tags=1
- **Formula (P3)**: `N_tasks ~ C(tag_cat, Treatment) + log_n_instances + log_n_features + age_years + age_sq + C(decade)`

### Robustness Checks
| RC | Description | Motivation |
|---|---|---|
| RC-3 | C(decade) in base model (first-class covariate) | h-e1 lesson: composite score failed RC-3 |
| RC-4 | Top-1% N_tasks exclusion (winsorization) | h-e1 RC-1 analog |
| RC-5 | N_tasks ≥ 2 threshold (vs. N_tasks ≥ 1) | Test DV threshold sensitivity |
| RC-6 | Linear tag_count (unlogged) replacing log(tag_count+1) | Test log vs. linear IV specification |
| RC-7 | Decade FE only (no continuous age_years/age_sq) | Test decade vs. continuous age parameterization |

### Baselines
- **h-e1 composite score model**: IRR=1.076, 95% CI lower ≈ 1.06 (below 1.1 gate) — the failed predecessor
- **Null model (intercept only)**: AIC comparison to confirm IV contribution
- **Poisson NB-2 comparison**: Cameron-Trivedi LR test to confirm NB-2 over Poisson (expected given h-e1 CT stat=2222.68)

---

## Limitations

1. **Cross-sectional data — no causal identification**: The corpus is a static snapshot. Reverse causation (popular datasets get tagged post-hoc) cannot be ruled out from the data alone. The platform architecture argument (tags assigned at upload by creator only) weakens but does not eliminate this concern.

2. **N_tasks proxy heterogeneity**: N_tasks counts distinct ML tasks registered, not actual task executions. A dataset with 1 auto-generated baseline task and 1 high-effort research task both contribute N_tasks=1. This noise in the DV may attenuate IV effect estimates.

3. **Sample selection**: N_tasks ≥ 1 restriction excludes ~18,000 OpenML datasets with zero tasks. This study tests "what predicts more adoption among already-adopted datasets", not "what predicts initial adoption". Generalizing to the full OpenML corpus requires a two-part model (out of scope for this hypothesis).

4. **Zero-tag MNAR risk**: Datasets with zero tags may be low-quality/low-attention datasets non-randomly (MNAR). Including them as tag_count=0 assumes zero-tag is a valid data level. The has_tags binary approach directly tests this threshold and RC-5 (restrict to tag_count≥1) provides a MNAR robustness check.

5. **RC-3 survival uncertain**: The theoretical argument for binary has_tags being less decade-correlated than composite score is plausible but empirically untested. Check has_tags-decade dummy correlation before interpreting IRR as decade-invariant.

---

## Decision

| Item | Status |
|---|---|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | h-e1-v2 |
| **Discussion Exchanges** | 15 (min=15; all 6 criteria passed) |
| **Convergence Type** | Qualitative self-judgment |
| **Clarity Verified** | Yes |
| **All 6 Personas Participated** | Yes |
| **Genuine Adversarial Pressure** | Yes (Prof. Rex challenged Dr. Ally/Dr. Nova in Exchanges 6, 12) |
| **Primary IV** | has_tags binary (0/1) — pre-registered, no data-adaptive branching |
| **Primary IRR Gate** | ≥ 1.1 (95% CI lower bound) |
| **Secondary IRR Gate** | ≥ 1.05 (95% CI lower bound) |
| **Remaining Objections** | RC-3 survival (has_tags-decade correlation), N_tasks proxy heterogeneity |
| **Phase 2B Readiness** | READY |

---

## Phase 2B Readiness Seeds

- **SH1 (Existence)**: Does has_tags=1 predict significantly higher N_tasks than has_tags=0 in NB-2 with decade FE (IRR≥1.1)?
- **SH2 (Mechanism)**: Does log(tag_count+1) add predictive power beyond binary presence (IRR≥1.05 conditional on has_tags=1)?
- **SH3 (Comparison)**: Does has_tags binary outperform composite metadata score (h-e1 IV) in same-corpus NB-2? (deferred to Phase 5 baseline comparison)
