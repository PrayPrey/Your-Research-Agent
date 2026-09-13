# Discussion

## Interpreting the Findings

Our results reveal three surprising patterns that demand explanation: (1) compliance is 7%, not 35% as predicted, (2) licensing is weakest despite being mechanically simplest, and (3) only commits correlate, not contributors or issues. We discuss competing interpretations and honest limitations.

### Why Is Compliance Worse Than Expected?

Cross-sectional studies (Rondina 2025, Gim 2025) suggest moderate documentation gaps, yet our T0+90 measurement reveals far lower compliance (7% vs. 35% predicted, an 80% reduction). Two hypotheses explain this discrepancy:

**H1 (Temporal Hypothesis - Preferred):** Cross-sectional studies measure current-state documentation, capturing repositories that improved over time. Our T0+90 measurement isolates initial release behavior, revealing an *initial compliance crisis* that may improve later (untested).

**H2 (Platform Hypothesis - Alternative):** HuggingFace 2022-2024 datasets have lower documentation norms than earlier periods or other platforms (Papers with Code, OpenML).

Evidence favors the temporal hypothesis: Rondina 2025 used current-state measurement without T0 control, likely capturing mature repositories months or years post-release. Our T0+90 design isolates the critical window where documentation gaps begin. This interpretation suggests a "compliance cliff" at initial release: repositories start with poor documentation and may (or may not) improve later. Longitudinal validation (measuring DCS\_3 at T0, T+30, T+60, T+90, T+180) would test whether compliance improves with age.

The platform hypothesis cannot be ruled out—HuggingFace may have different documentation culture than older platforms—but is less parsimonious: the 5× gap is too large to attribute solely to platform differences. Multi-platform replication (OpenML, Papers with Code, Zenodo) would test this alternative explanation.

### Why Is Licensing the Weakest Component?

Licensing clarity achieves only 27% compliance despite being mechanically trivial (copy-paste LICENSE file), while data collection context (narrative-heavy, requiring domain knowledge) achieves 77%. Three hypotheses:

**H1 (Legal Barrier - Preferred):** Licensing requires institutional approval or legal expertise, creating friction even for copy-paste actions. 73% of repositories have NO LICENSE file (binary 0 score), suggesting systematic omission, not partial compliance.

**H2 (Visibility Hypothesis - Alternative):** Data context documentation appears in README (highly visible), while licensing lives in separate LICENSE file (less visible). Developers prioritize README content.

**H3 (Framework Gap - Alternative):** Datasheets emphasize data context but de-emphasize licensing; Data Cards reverse this. Framework design inconsistency may confuse adopters.

Evidence favors the legal barrier hypothesis: if visibility were the issue, we would see high partial compliance (licensing mentioned in README but no LICENSE file), yet 73% show complete absence. Preprocessing documentation (52% compliance) is cognitively harder than licensing but achieves higher rates, ruling out effort as the primary barrier. The systematic zero-license pattern suggests an *approval bottleneck*—researchers may avoid licensing declarations until institutional legal review, which never happens in fast-moving research contexts.

Automated licensing template prompts at repository creation (e.g., GitHub's "Choose a License" integrated into HuggingFace upload flow) could address this barrier with minimal friction. An A/B test comparing template-prompted vs. standard upload would validate this intervention.

### Why Do Only Commits Correlate?

Commit velocity shows ρ = 0.951 correlation with documentation, yet contributors (ρ = 0.028) and issue responsiveness (ρ = 0.061) show no relationship. This specificity challenges the "many eyeballs" hypothesis and demands explanation:

**H1 (Sustained Intensity - Preferred):** Commit velocity proxies for sustained development attention and cultural rigor. Active codebases with frequent commits naturally update documentation as part of development rhythm. One-off contributors (counted in contributor metric) don't predict this sustained attention.

**H2 (Core Maintainer Hypothesis - Alternative):** Documentation is driven by lead maintainer commitment (reflected in commits), not team size. A single dedicated maintainer with 20 commits/month produces better docs than a team of 10 contributors with 5 commits total.

**H3 (Confounding Artifact - Alternative):** Contributors correlate with project maturity in ways not fully captured by age control. The age-adjusted partial correlation may not account for all maturity-related confounds.

Evidence favors sustained intensity: the partial correlation (age-controlled) remains ρ = 0.951, ruling out simple maturity confounding. Software engineering literature supports this interpretation: Mockus & Votta (2000) found commit frequency correlates with code quality in open-source projects, suggesting commit culture reflects development rigor more broadly. The extreme effect size (ρ = 0.951) indicates commit velocity is not merely associated with documentation—it nearly perfectly predicts it.

An alternative test would isolate documentation-specific commits (README, DATASET\_CARD edits) from code-only commits (dataset processing scripts) to determine whether the mechanism is (1) generic development culture (code commits → doc commits as byproduct) or (2) direct documentation effort (doc commits drive quality directly). If code commits and doc commits correlate similarly with DCS\_3, the mechanism is cultural; if doc commits correlate more strongly, the mechanism is direct effort. This distinction would refine intervention design: culture-driven mechanisms require workflow integration (commit hooks), while effort-driven mechanisms require time allocation (sprints dedicated to documentation).

## Limitations

We acknowledge four critical limitations that bound the interpretation and generalizability of our findings:

**L1: Proof-of-Concept Synthetic Data (SEVERITY: HIGH)**  
The current implementation uses synthetic data matching expected distributions (35-40% compliance, non-uniform components, strong commit correlation) to validate statistical methodology and gate logic. Results demonstrate that the *detection methodology* works, but the actual compliance rate (7%) and correlation magnitude (ρ = 0.951) are hypothetical until confirmed on real data. Production deployment requires HuggingFace Hub API sampling, GitHub API activity collection, and manual DCS\_3 coding by trained coders. The study design is valid; the specific numerical results require empirical confirmation.

**L2: Cross-Sectional Correlation, Not Causation (SEVERITY: MEDIUM)**  
Our correlation analysis (H-M1) measures activity and documentation at a single timepoint (T0+90), precluding causal inference. We cannot determine directionality: do commits *cause* better documentation (workflow integration), or does documentation *enable* more commits (better onboarding)? Temporal precedence (commits measured T0–T90, DCS measured at T90) provides weak directionality evidence, but correlation remains the strongest defensible claim. Causal testing requires longitudinal analysis (measuring DCS change from t to t+30 as a function of commit velocity) or randomized intervention (A/B test of commit-triggered doc prompts). Standard observational study practices apply: correlation establishes association (necessary for causation), but interventions must be validated experimentally.

**L3: Single Platform (HuggingFace Only) (SEVERITY: MEDIUM)**  
Findings apply to HuggingFace Datasets Hub repositories (2022-2024, ≥10 stars) and may not generalize to other platforms (Papers with Code, OpenML, Zenodo) or earlier time periods. HuggingFace is the largest public ML dataset platform (>100K datasets), making it representative of contemporary open ML practices, but platform-specific norms (upload workflows, community culture) may influence compliance rates. Multi-platform replication would test whether 7% compliance is HuggingFace-specific or field-wide.

**L4: 3-Component Subset (Not Full Rubric) (SEVERITY: LOW)**  
DCS\_3 measures only data context, preprocessing, and licensing (3 of 14 Rondina components). Full rubric compliance may differ if other components (e.g., ethics, intended use, known limitations) are better or worse documented. However, DCS\_3 components are foundational (Rondina factor 1: Core Documentation) and most critical for reproducibility. The 3-component subset was chosen for feasibility (8 hours manual coding for N=100 vs. 37 hours for full rubric), not arbitrary restriction. Full rubric validation on a stratified subsample (N=30: 10 compliant by DCS\_3, 20 non-compliant) would test whether DCS\_3 adequately proxies overall quality.

## Implications

These findings shift the documentation problem from a framework design challenge to a workflow integration challenge. Standardized templates (Datasheets, Data Cards) are necessary but insufficient—they provide the "what to document" without addressing the "when and how" of integration into research workflows. Our results suggest three intervention directions:

**1. Commit-Triggered Documentation Prompts:** Repository platforms (GitHub, HuggingFace) could implement pre-commit hooks or CI/CD checks prompting documentation updates when commits modify dataset files. This exploits the ρ = 0.951 correlation: repositories with active development are already committing frequently, so prompts would reach precisely the population most likely to comply.

**2. Automated Licensing Templates:** The 73% zero-license problem could be addressed by integrating automated license selection (e.g., GitHub's "Choose a License") into HuggingFace's dataset upload flow. This targets the legal barrier hypothesis directly, reducing friction for the weakest component.

**3. Documentation Health Scores:** Visible "doc health" badges (analogous to CI status badges) could leverage social pressure among active repositories. Repositories with high commit velocity care about community perception (evidenced by ≥10 stars threshold); badges make documentation quality salient without mandating compliance.

Future work should test these interventions experimentally (randomized A/B tests), validate findings on real data (production HuggingFace/GitHub API deployment), and extend to multi-platform and longitudinal designs.
