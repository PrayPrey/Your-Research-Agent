# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12T08:26:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: Systematic Directional Asymmetry in Preference Dataset Coverage (AI→Human vs. Human→AI)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Hypothesis ID**: H-AIFS-AdaptationDetection-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Three-test empirical battery fully specified with pre-registered falsification criteria; construct validity and all major alternative explanations addressed through iterative persona dialogue.

### Key Insights

1. **Online vs. base splits as adaptation proxy**: HH-RLHF helpful-online (deployed annotators) vs. helpful-base (naive annotators) may encode human-to-AI adaptation signals as distributional preference shifts — detectable without new data.
2. **AI-idiomatic feature specificity is the key**: Generic covariate shift cannot explain preference shifts *specifically* in post-RLHF stylistic features (safety-prefaces, CoT scaffolds, structured lists) that exceed pre-LLM human expert baselines.
3. **BeaverTails dual-label entropy as independent probe**: The helpfulness-harmlessness disagreement rate, stratified by AIFS bin and harm category, provides a second independent test of preference normalization.
4. **Schema audit as measurement instrument**: The 0–4 bidirectionality index, validated by cross-dataset β₄ correlation, transforms from taxonomy to predictive measurement tool.
5. **Meta-finding may match empirical finding in impact**: The structural blindness of existing datasets (scoring 0–1/4) is as important as detecting the latent adaptation signal itself.

### Breakthrough Moments

- Prof. Rex's demand for "adaptation-specific signature tests" (AI-idiomatic features vs. generic covariate shift) sharpened the hypothesis from unfalsifiable to testable
- Prof. Vera's conditional logit formalization with β₄ interaction and pre-specified OR ≥ 1.10 threshold provided the precise falsification criterion
- Dr. Nova's PKU-SafeRLHF multi-turn trajectory idea expanded the battery to a third dataset
- Prof. Pax's construct validity challenge led to the discriminant validation design using StackOverflow 2018 + FLAN baselines

---

## Final Hypothesis

### Title
Latent Human-to-AI Adaptation Signatures in RLHF Preference Corpora

### Core Claim (Under-If-Then-Because)

Under RLHF preference annotation conditions, **if** annotators have prior exposure to deployed RLHF-aligned AI systems (online condition) versus naive annotators (base condition), **then** online annotators show a statistically significant increase in conditional selection preference for AI-idiomatic stylistic features (β₄ > 0, OR ≥ 1.10 at α = 0.01), **because** repeated exposure to RLHF-optimized outputs causes annotators to internalize AI-native discourse norms — a human-to-AI stylistic adaptation effect latent in existing preference corpora.

### Null Hypothesis

H₀: There is no significant difference in conditional preference for AI-idiomatic stylistic features between deployed (online) and naive (base) annotator conditions after controlling for marginal response supply, prompt complexity, and semantic cluster fixed effects. Formally: β₄ = 0 (OR = 1.0, 95% CI includes 1.0).

### Mechanism

1. RLHF training amplifies AI-idiomatic stylistic features (structured lists, safety-prefaces, CoT scaffolds) in model outputs, creating a distinctive post-RLHF distribution not present in pre-LLM human expert writing
2. Annotators exposed to deployed RLHF-aligned models develop increased preference weighting for these features in subsequent labeling tasks
3. This convergence is strongest in RLHF-normed harm categories (violence, illegality), consistent with normative learning
4. Existing dataset schemas structurally fail to capture this feedback loop (scoring 0–1 on 0–4 bidirectionality index)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | β₄ (ΔAIFS × split) > 0 in conditional logit on HH-RLHF | OR ≥ 1.10, p < 0.01, survives supply control | β₄ = 0 or reverses after supply covariate |
| P2 | BeaverTails: ΔD_high-AIFS > ΔD_low-AIFS in RLHF-normed harm categories | Rank ordering: violence/illegality > sycophancy/privacy in ≥ 4/6 categories | Uniform entropy reduction or wrong rank ordering |
| P3 | Ordinal bidirectionality: β₄(HH-RLHF) < β₄(BeaverTails) < β₄(PKU-SafeRLHF) | All three pairwise orderings in expected direction | Any reversal in ordinal ranking |

---

## Novelty

This is the first study to:
1. Treat existing RLHF preference datasets as archives of human-to-AI adaptation rather than purely AI-to-human preference signals
2. Operationalize AI-idiomatic stylistic features (AIFS) as a measurable construct validated against pre-LLM baselines
3. Propose a schema bidirectionality index (0–4) for auditing alignment dataset design, with predictive validity via cross-dataset regression
4. Demonstrate that the human-to-AI adaptation direction is simultaneously *latent* in existing data AND *structurally absent* from existing measurement frameworks

**Differentiation from prior work:**
- Shen et al. (2024): identified conceptual gap → our work provides empirical measurement
- Vishwarupe et al. (2026): confirmed benchmark blindness → our work detects latent signals within blind datasets
- J.H. Shen et al. (2024): compared datasets on scale/noise → our work adds directionality coverage as a new dataset property

---

## Experimental Design

### Primary Dataset
- **HH-RLHF** (helpful-base + helpful-online, 160K+ pairs) — HuggingFace: anthropic/hh-rlhf
- Core test: conditional logit β₄ interaction

### Secondary Dataset
- **BeaverTails** (333K+ pairs, dual labels, 14 harm categories) — HuggingFace: PKU-Alignment/BeaverTails
- Core test: within-category AIFS-bin entropy differential

### Tertiary Dataset (conditional)
- **PKU-SafeRLHF** (265K+ pairs, multi-turn) — conditional on annotation protocol supporting sequential evaluation
- Core test: within-conversation AIFS trajectory + cross-dataset bidirectionality regression

### Baselines
- **StackOverflow 2018 dump** — pre-LLM human expert AIFS baseline
- **FLAN instruction templates** — pre-RLHF instruction-following AIFS baseline

### Model
- Conditional logistic regression (scikit-learn)
- Sentence-transformers all-MiniLM-L6-v2 (frozen, for prompt clustering at cosine ≥ 0.85)
- GPT-2 perplexity (automated complexity control)

### AIFS Operationalization (fully automated, no human annotation)
- Structured lists: Markdown bullet/numbered pattern regex
- Stepwise reasoning markers: "First,", "Therefore,", "Let me", "Step N:"
- Safety-prefaces: "I want to note", "I should mention", "It's important to"
- CoT scaffolds: "Let's think", "Let me break this down", explicit reasoning chains

---

## Limitations

- No annotator IDs in public HH-RLHF release — precludes within-annotator drift analysis (strongest causal evidence); study is limited to cross-sectional inference
- Only three RLHF datasets for cross-dataset regression — low statistical power; ordinal prediction more defensible than parametric
- StackOverflow 2018 and FLAN as pre-LLM baselines are imperfect proxies — some AI-idiomatic features (structured lists) were already present in expert human writing
- AIFS is a construct-validated proxy, not a direct measure of annotator cognitive state
- Causal interpretation bounded: "distributional asymmetry consistent with adaptation," not proven causal adaptation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 15 exchanges, all 6 personas participated |
| **Clarity Verified** | Yes |
| **Feasibility** | CONFIRMED — all tests executable on existing public data |
| **Remaining Objections** | 3 (manageable; pre-registration mitigates all) |

### Persona Verdicts Summary

| Persona | Role | Verdict |
|---------|------|---------|
| 🔭 Dr. Nova | Novelty | STRONG |
| 🔬 Prof. Vera | Falsifiability | STRONG |
| 🎯 Dr. Sage | Significance | STRONG |
| ⚙️ Prof. Pax | Feasibility | STRONG |
| 🛡️ Dr. Ally | Advocate | VALIDATED |
| 🔍 Prof. Rex | Critic | CONDITIONALLY_VALIDATED |

---

## Phase 2B Readiness

| Sub-Hypothesis | Probe | Status |
|----------------|-------|--------|
| SH1 (Existence) | Do RLHF corpora contain detectable AIFS preference shifts? | READY — logit β₄ test on HH-RLHF |
| SH2 (Mechanism) | Does shift reflect selection preference above supply, validated as AI-specific? | READY — supply-controlled logit + AIFS discriminant validation |
| SH3 (Comparison) | Does schema bidirectionality predict adaptation magnitude? | READY — ordinal cross-dataset β₄ comparison |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: YouRA Research — Bidirectional Human-AI Alignment*
