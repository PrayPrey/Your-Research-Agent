---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Bidirectional Alignment Gap — Within-Model Verbosity-Controlled"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-04
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Bidirectional Human-AI Alignment — Reflection 5: pivot from RLHF-specific mechanism hypothesis (h-m1 FAIL: training type does not predict Δ gap magnitude) to the capability-confounded gap structure. The AlpacaEval 2.0 Δ gap IS confirmed as a dataset-wide phenomenon (mean(Δ)≈-16pp). New direction: model capability as the true predictor of Δ, not training paradigm — test whether high-capability models show smaller |Δ| (less alignment asymmetry) than low-capability models using existing AlpacaEval 2.0 data.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Reflection 5)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This workshop focuses on bidirectional Human-AI alignment, a paradigm shift emphasizing the dynamic, complex, and evolving alignment process between humans and AI systems. Grounded in a systematic survey of over 400 interdisciplinary alignment papers across ML, HCI, and NLP, it defines two directions: (1) Aligning AI with Humans — integrating human specifications into training, steering, customizing, and monitoring AI; (2) Aligning Humans with AI — preserving human agency and empowering humans to critically evaluate, explain, and collaborate with AI systems.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Bidirectional Human-AI Alignment)

**Feasibility constraints enforced:** No new benchmarks, no synthetic data, no human annotation — all hypotheses must be testable immediately using existing real datasets and benchmarks.

**ROUTE_TO_0 context:** Reflection 5 — four prior attempts failed. The AlpacaEval 2.0 dual-annotation approach (Δ = LC_winrate − win_rate) was validated as structurally sound and produces a measurable population-level gap (mean(Δ)≈-16pp across N=58 typed models). However, h-m1 (MECHANISM) failed: the hypothesis that RLHF training type predicts Δ direction/magnitude was falsified — all training types (RLHF, SFT, DPO) show similar Δ, and Cohen's d=0.136 (negligible). New direction: use model capability (win_rate as proxy for overall human-assessed quality) as the predictor of Δ magnitude, testing whether the bidirectional gap is smaller for higher-quality models.

---

## Lessons from Previous Attempts

### Attempt 1 (H-E1 Run 1): AlpacaEval 2.0 × HumaneEval v1 — Model Generation Mismatch

- **What was tried:** AlpacaEval 2.0 leaderboard as AI→Human proxy × HumaneEval v1 as Human→AI proxy; fuzzy model name matching
- **Why it failed:** AlpacaEval 2.0 covers 2023–2024 era models; HumaneEval v1 covers exclusively 2025/2026 frontier models. Best fuzzy score = 73.9 (below threshold 85). N_intersection = 0.
- **Root cause:** HumaneEval v1 is a 2025/2026-era benchmark — incompatible with any pre-2025 leaderboard.

### Attempt 2 (H-E1 archived): Arena ELO × HumaneScore Aggregate — Proxy Collapse

- **What was tried:** Arena ELO as AI→Human proxy; HumaneScore aggregate as Human→AI proxy; BAI = (z_arena_elo − z_humane_score) / 2
- **Why it failed:** Arena ELO and HumaneScore aggregate both track general capability (Pearson r = 0.825). BAI ≈ 0 by construction.
- **Root cause:** Aggregate scores conflate alignment signal with capability signal. Arena ELO is an H→AI proxy (human preference for task capability), NOT an AI→H proxy.

### Attempt 3 (H-E1 Run 1, 6-pair): MT-Bench/WildBench/AlpacaEval × Arena ELO/RewardBench-Chat — Same Root Cause

- **What was tried:** 6 candidate proxy pairs {MT-Bench, WildBench, AlpacaEval 2.0} × {Arena ELO, RewardBench-Chat}; orthogonality pre-check r < 0.5; N ≥ 50
- **Why it failed:** Arena ELO is H→AI (r=0.9708 with MT-Bench, P2 FAIL). RewardBench-Chat naming incompatibility: max N=10 across all pairs, P1 FAIL.
- **Root cause:** Arena ELO misclassified as AI→H proxy. RewardBench-Chat model name format (HTML-wrapped HF paths) incompatible with chat LLM display names.

### Attempt 4 (Reflection 3 brainstorm → h-e1 duplicate): MT-Bench/WildBench/AlpacaEval × Arena ELO/RewardBench — Same Root Cause Repeated

- **What was tried:** Identical 6-pair structure from Attempt 3; framed as "generation-mismatch fix" by dropping HumaneEval v1
- **Why it would have failed:** Exactly Attempt 3 again — Arena ELO as AI→H proxy flaw not corrected.

### Attempt 5 (Reflection 4 brainstorm → h-e1/h-m1): AlpacaEval 2.0 Dual Annotation Δ — MECHANISM Failure

- **What was tried:** Δ = length_controlled_winrate − win_rate per model; H-E1 (existence of Δ≠0) + H-M1 (mechanism: RLHF training type predicts Δ direction)
- **Why h-m1 failed:** mean(Δ|RLHF) = -16.72pp vs mean(Δ|SFT) = -18.24pp — SFT MORE negative than RLHF (wrong direction). Mann-Whitney p=0.662 (not significant). Cohen's d=0.136 (negligible). The gap is training-type-agnostic.
- **Root cause from h-m1 reflection:** Model capability/quality confound — high-quality RLHF models (GPT-4: Δ=-8.8pp) < low-quality SFT models (recycled-wizardlm: Δ=-32pp). Verbosity is dataset-driven, not RLHF-specific. Model capability is a stronger predictor of Δ than training paradigm.
- **H-E1 core finding preserved:** Population-level gap mean(Δ)≈-16.37pp is robust and statistically significant. The AlpacaEval 2.0 dual annotation approach is sound; only the MECHANISM hypothesis needs redesign.

### How THIS Direction Avoids Those Pitfalls

**Core pivot (Reflection 5):** The existence of Δ≠0 is confirmed. The mechanism is NOT training paradigm (h-m1 falsified). The h-m1 reflection explicitly identifies **model capability/quality** as the true confound. New hypothesis directly tests this: does higher win_rate (human-assessed quality) predict smaller |Δ| (less bidirectional asymmetry)?

**Specific fix — use win_rate as capability proxy, test its relationship with Δ:**

AlpacaEval 2.0 leaderboard CSV (same dataset, already working) contains:
1. `win_rate` — raw human win-rate; proxy for human-assessed model quality/capability
2. `length_controlled_winrate` — GPT-4 LC annotator preference
3. `avg_length` — model response verbosity
4. Δ = `length_controlled_winrate − win_rate` — bidirectional alignment gap

Hypotheses testable with existing data, zero new data required:

- **H-E2 (EXISTENCE):** Spearman ρ(win_rate, |Δ|) is significantly negative (p < 0.05) — higher capability models show smaller bidirectional asymmetry
- **H-M2 (MECHANISM):** Partial correlation ρ(win_rate, Δ | avg_length) remains significant after controlling for verbosity — capability effect is not entirely mediated by length
- **H-M3 (MECHANISM):** Model family Kruskal-Wallis on Δ/win_rate (already computed in h-m1 as h-m3 direction) — family variation in alignment asymmetry independent of training type

These are direct corollaries of h-m1's root cause finding: capability > training type. The data is already downloaded and loaded in h-e1/h-m1 code; only the regression/correlation analysis changes.

---

## Session Plan

ROUTE_TO_0 recovery plan (Reflection 5) — pivot mechanism hypothesis from training_type to model capability:

1. Reuse AlpacaEval 2.0 results CSV from `h-m1/code/` (already validated, N=58+ typed models; full leaderboard N=200+ also downloaded)
2. Compute Δ = `length_controlled_winrate − win_rate` per model (already done in prior code)
3. Compute |Δ| = abs(Δ) as measure of bidirectional asymmetry magnitude
4. Spearman ρ(win_rate, Δ): test direction (negative = higher quality → less AI-over-human bias)
5. Spearman ρ(win_rate, |Δ|): test magnitude relationship (negative = higher quality → less total asymmetry)
6. Partial correlation ρ(win_rate, Δ | avg_length): control for verbosity confound
7. OLS regression: Δ ~ win_rate + avg_length; report β_capability, β_length, R²
8. Robustness: split by win_rate quartiles, compare mean(Δ) across quartiles (Kruskal-Wallis)
9. Model family analysis already computed in h-m1 — use as secondary result

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode (Reflection 5). Five-failure root cause chain analysis:
- Attempts 1-4: cross-leaderboard intersection approach structurally broken (ceiling at N=10, proxy misclassification)
- Attempt 5 (h-m1): MECHANISM hypothesis (RLHF→Δ) falsified; h-m1 reflection explicitly flags model capability as the true predictor
- New direction: directly test the h-m1 root cause as the new mechanism hypothesis

**Failure-informed pivots applied:**
- Carry forward: AlpacaEval 2.0 dual annotation (Δ = LC_winrate − win_rate) — validated structural approach
- Carry forward: N=200+ full leaderboard dataset already downloaded in h-e1 code
- Drop: training_type as predictor (h-m1 falsified this)
- Drop: Arena ELO, RewardBench-Chat, HumaneEval (all three leaderboard-intersection failure modes)
- New: win_rate as capability proxy; |Δ| as asymmetry magnitude; partial correlation + OLS regression

**Feasibility filter re-applied:** All data in existing AlpacaEval 2.0 CSV. All statistics are standard (Spearman ρ, partial correlation, OLS, Kruskal-Wallis). Code reuse from h-e1/h-m1 modules. Constraint-compliant: **PASS**

---

## Research Question Development

### Initial Question

Does model capability (operationalized as raw human win_rate in AlpacaEval 2.0) predict the magnitude and direction of bidirectional alignment asymmetry (Δ = length_controlled_winrate − win_rate) across 200+ publicly evaluated LLMs, after controlling for response verbosity?

### Refined Question

Across all models in the publicly available AlpacaEval 2.0 leaderboard (N=200+), is Spearman ρ(win_rate, Δ) significantly negative (higher-capability models show less AI-over-human evaluation bias), and does this relationship persist after partial correlation control for response length (avg_length), providing evidence that bidirectional alignment asymmetry is capability-confounded rather than training-paradigm-determined?

### Detailed Sub-Questions

1. **Direction test:** Is Spearman ρ(win_rate, Δ) significantly negative (p < 0.05)? Higher win_rate models should show Δ closer to zero if capability reduces bidirectional asymmetry.
2. **Magnitude test:** Is Spearman ρ(win_rate, |Δ|) significantly negative (p < 0.05)? Tests whether high-capability models have smaller total alignment asymmetry regardless of direction.
3. **Verbosity confound:** Does partial correlation ρ(win_rate, Δ | avg_length) remain significant after controlling for response length? If capability effect disappears when controlling for length, verbosity (not capability) is the true mechanism.
4. **OLS decomposition:** In OLS Δ ~ win_rate + avg_length, what are β_capability and β_length? Which explains more variance (compare standardized betas)?
5. **Quartile robustness:** Do mean(Δ) values differ significantly across win_rate quartiles (Kruskal-Wallis, α=0.05)? Post-hoc Dunn test for Q1 vs Q4 (lowest vs highest capability).

---

## Reference Papers

Not provided - will discover in Phase 1

Key search targets for Phase 1:
- AlpacaEval 2.0 LC (Dubois et al. 2024) — primary dataset; Section on length-controlled evaluation and annotator divergence
- Length bias and verbosity in LLM evaluation (Saito et al. 2023; Wang et al. 2023)
- LLM capability and alignment relationship (prior work on capability-alignment scaling)
- Bidirectional human-AI alignment survey (400+ papers — workshop grounding paper, ICLR 2025)
- Reward hacking / sycophancy papers (Scheurer et al. 2023) — potential mechanism for capability × Δ relationship
- Human vs AI annotator divergence as function of model quality (any prior work)
- h-m1 failure directly cites: model quality confound in RLHF verbosity studies (check references in original h-m1 hypothesis)

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop on Bidirectional Human-AI Alignment) — significance pre-validated. This question directly extends the confirmed finding (Δ≠0 population-level) to explain WHY the asymmetry exists and for WHICH models. If ρ(win_rate, Δ) is significantly negative: this provides a practical implication — alignment asymmetry is not a fixed property of the field but scales with model capability, suggesting that capability improvements reduce bidirectional misalignment. If null: suggests asymmetry is systematic regardless of capability (equally important negative result). Both outcomes are publishable at the workshop level. Additionally, h-m1's explicit root cause finding (capability > training type) makes this hypothesis well-grounded in prior negative results from the same pipeline.

### Feasibility Check

All data sources are existing and publicly available:
- AlpacaEval 2.0 leaderboard CSV: already downloaded in h-e1/h-m1 code at `h-e1/code/` — `win_rate`, `length_controlled_winrate`, `avg_length`, `model` columns confirmed
- Δ computation: already implemented in h-m1 code, N=200+ full leaderboard confirmed
- win_rate as capability proxy: direct column from same CSV, no external data needed
- Statistical tests: Spearman ρ, partial correlation, OLS regression, Kruskal-Wallis — all standard scipy/statsmodels, no new dependencies

No new benchmark creation. No synthetic data. No human annotation. No fuzzy matching. No cross-leaderboard intersection. Code reuse from h-e1/h-m1 reduces implementation risk. Constraint-compliant: **PASS**

Critical structural advantage over h-m1: capability (win_rate) is a continuous variable with full range across N=200+ models; training_type was categorical with N_Unknown=20 and power issues. Regression on continuous predictor avoids the underpowering problem that compounded h-m1's failure.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Across all models in the publicly available AlpacaEval 2.0 leaderboard (N=200+), does model capability (operationalized as raw human win_rate) predict the direction and magnitude of bidirectional alignment asymmetry (Δ = length_controlled_winrate − win_rate) after controlling for response verbosity (avg_length)? This hypothesis is directly motivated by the h-m1 failure root cause: model quality/capability was identified as the true confound when training type (RLHF vs SFT) failed to predict Δ. All data is in the existing AlpacaEval 2.0 CSV; code reuse from h-e1/h-m1 eliminates implementation risk.

### detailed_question
1. Is Spearman ρ(win_rate, Δ) significantly negative (p < 0.05, two-tailed)? Higher-capability models should show less AI-over-human bias if capability reduces bidirectional asymmetry.
2. Is Spearman ρ(win_rate, |Δ|) significantly negative (p < 0.05)? Tests asymmetry magnitude regardless of direction.
3. Does partial correlation ρ(win_rate, Δ | avg_length) remain significant after controlling for response verbosity? Distinguishes capability effect from length confound.
4. In OLS regression Δ ~ win_rate + avg_length: what are standardized beta coefficients for capability vs verbosity? Which dominates?
5. Do win_rate quartiles show significantly different mean(Δ) distributions? (Kruskal-Wallis; post-hoc Dunn Q1 vs Q4)

### reference_papers
Not provided - will discover in Phase 1

Key targets:
- AlpacaEval 2.0 LC (Dubois et al. 2024) — primary dataset; annotator divergence sections
- Bidirectional human-AI alignment survey (ICLR 2025 workshop grounding paper, 400+ papers)
- Length bias in LLM evaluation (Saito et al. 2023; Wang et al. 2023)
- Capability-alignment scaling relationship prior work
- Sycophancy / reward hacking papers (Scheurer et al. 2023)
- LLM-as-judge reliability vs model quality (Zheng et al. 2023 MT-Bench)

</phase1-input>

---

## Session Insights

### Key Discoveries

- The AlpacaEval 2.0 dual-annotation approach (Δ = LC_winrate − win_rate) is structurally validated: population-level gap mean(Δ)≈-16.37pp is robust (preserved from h-m1 results). The dataset and code infrastructure from h-e1/h-m1 are fully reusable.
- h-m1 root cause analysis explicitly identifies model capability as the true predictor that was confounding the training-type effect: high-quality RLHF models (GPT-4: Δ=-8.8pp) vs low-quality SFT models (recycled-wizardlm: Δ=-32pp). This is a direct, explicit hypothesis derivation from a prior failure record — unusually well-grounded for a ROUTE_TO_0 brainstorm.
- win_rate (raw human win-rate) is already in the AlpacaEval 2.0 CSV and serves as a natural capability proxy without needing any external leaderboard or cross-dataset matching. This eliminates ALL intersection problems from Attempts 1-4.
- Partial correlation design cleanly separates the capability effect from the verbosity confound (avg_length). If both h-m1 (training type) and this reflection's hypothesis (capability) are considered together, the picture that emerges is: Δ is primarily driven by model quality, with verbosity as secondary mediator — a richer mechanism story than any single prior hypothesis captured.
- The N=200+ (full leaderboard) vs N=58 (training-type-labeled subset) distinction matters: regression on continuous win_rate uses all 200+ models, giving substantially more statistical power than h-m1's N=58 typed subsample.

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (Reflection 5). Five-failure chain analysis → h-m1 reflection root cause → direct hypothesis derivation from documented failure → capability-as-predictor mechanism → constraint verification → research question synthesized from prior negative results.

### Areas for Further Exploration

- Temporal capability trajectory: as model families release newer versions (GPT-3.5→GPT-4→GPT-4o→GPT-4.1), does Δ trend toward zero with each generation? (uses existing leaderboard history data within AlpacaEval 2.0)
- Sycophancy connection: models with large positive Δ (AI rates higher than humans) — do they also score higher on sycophancy benchmarks? Cross-reference with existing sycophancy evaluation datasets
- Verbosity mediation analysis: if partial correlation shows capability effect diminishes with avg_length control, explore whether length-control correction IS the alignment mechanism (LC annotation not just a bias correction but an actual alignment improvement)
- Cross-benchmark replication: MT-Bench provides both GPT-4 judge scores and human ratings for a smaller model set — does the capability-Δ relationship replicate?
- Policy implication: if high-capability models have smaller Δ, and if Δ represents the misalignment between AI self-evaluation and human preference, then capability-improving RLHF implicitly reduces bidirectional misalignment as a side effect

---

## Next Steps

Proceed to Phase 1 - Targeted Research: /phase1-targeted

Priority Phase 1 targets:
1. Verify AlpacaEval 2.0 results CSV structure from h-e1 code — confirm win_rate, length_controlled_winrate, avg_length columns and N=200+
2. Search for papers on model capability and alignment relationship (scaling laws for alignment)
3. Search for AlpacaEval 2.0 paper (Dubois et al. 2024) — read Section 3 on length-controlled annotation methodology and annotator comparison
4. Search for partial correlation / mediation analysis approaches in LLM evaluation papers
5. Verify: does the h-m1 result (mean Δ by training type) also appear correlated with capability in the raw data? (check h-m1/results/h-m1_results.json — win_rate values by group)
6. Search for sycophancy + capability interaction papers (if high-capability models are less sycophantic, this could explain the Δ relationship)
7. Search for ICLR 2025 Workshop on Bidirectional Human-AI Alignment grounding paper (400+ paper survey)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Recovery — Reflection 5)*
*Ready for: Phase 1 - Targeted Research*
