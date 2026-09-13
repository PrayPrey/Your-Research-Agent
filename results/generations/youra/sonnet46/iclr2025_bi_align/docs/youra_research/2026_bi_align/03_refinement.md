# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-14T21:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Free-Parse)
- **Gap ID**: gap-1-sbert-accommodation
- **Gap Title**: No Semantic Embedding-Based Measurement of Human Accommodation Across RLHF Alignment Tiers
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)

**Total Exchanges**: 15 (min=15 met; converged exactly at threshold)

**Convergence Reason**: Partner-specific semantic accommodation metric (C_sem) established with conditional-minus-baseline structure; epistemic uptake sensitivity mechanism formulated; robust Δ designs specified; abandonment criteria defined.

### Key Insights
1. **Metric design**: Raw SBERT cosine similarity across tiers is insufficient — requires conditional-minus-baseline (C_sem) and three-level partner-specificity validation (actual > topic-matched > random) to distinguish accommodation from topical coherence
2. **Directional asymmetry is non-negotiable**: C_sem^(H←A) > C_sem^(A←H) is the core test distinguishing accommodation from mutual semantic drift
3. **HH-RLHF chosen/rejected pairs** provide a built-in quasi-experimental probe for quality-conditioned accommodation within identical prompts
4. **Mechanism underspecification resolved**: "Epistemic uptake sensitivity" (RLHF quality → perceived reliability → accommodation) is testable via PM mediation regression; both positive and negative results are theoretically informative
5. **Prior failure integration**: All three prior failure modes (keyword features d=0.036/0.136, GPU training, surface lexical stats) are explicitly avoided by design

### Breakthrough Moments
- **Exchange 6**: Dr. Ally formulated the bilateral C_sem metric and mechanistic "epistemic authority" causal chain — transformed vague intuition into testable prediction structure
- **Exchange 8**: Prof. Vera specified three-level partner-specificity control (actual > topic-matched > random) with d ≥ 0.1 threshold — metric validation requirement
- **Exchange 12**: Dr. Ally proposed matched-shuffle synthetic control with formal C_sem formulation — isolated accommodation from coherence conceptually
- **Exchange 14**: Prof. Vera required three-operationalization Δ test (raw, length-matched, prompt-projected) — bulletproofed P3 against length confound

---

## Final Hypothesis

### Title
**Human Semantic Accommodation Sensitivity to RLHF Alignment Quality (H-SemAccom-v1)**

### Core Claim
Under conditions where human-AI conversations in the HH-RLHF dataset are stratified by RLHF alignment tier (helpful_base → helpful_rejection_sampling → helpful_online), if RLHF tier quality increases, then the baseline-adjusted semantic similarity between human follow-up turns and their preceding AI partner turns (C_sem = E[cos(H_{t+1}, A_t)] - E[cos(H_{t+1}, A_t^matched-shuffle)]) will increase monotonically with tier AND the human→AI accommodation coefficient will exceed the AI→human coefficient (directional asymmetry), because RLHF-optimized AI responses carry higher epistemic uptake signals that trigger greater adaptive semantic alignment in human responses.

### Mechanism
**RLHF training quality → Perceived epistemic reliability → Asymmetric human semantic accommodation**

1. RLHF training (SFT → RM → PPO) produces AI responses with progressively higher clarity, structure, and normative appropriateness [Bai et al. 2022; Ouyang et al. 2022]
2. Human interlocutors interpret higher-quality AI responses as carrying greater epistemic reliability ("epistemic uptake sensitivity")
3. This triggers greater adaptive semantic alignment in human follow-up turns — H embedding space shifts toward AI partner embedding space
4. Effect is asymmetric (H→AI > AI→H) and scales monotonically with tier quality — analogous to power-asymmetry coordination [Danescu-Niculescu-Mizil et al. 2011]

*Mechanism specificity tested via PM mediation regression (PM score explaining C_sem above length, structure, politeness)*

---

## Predictions

### P1 — Primary (Existence + Asymmetry)
- **Statement**: C_sem^(H←A) > C_sem^(A←H), monotonically increasing across tiers, Cohen's d ≥ 0.1 for primary tier contrast, consistent across ≥2/3 SBERT models
- **Test**: Compute C_sem for H→AI and AI→H directions; Mann-Whitney U + Jonckheere-Terpstra + bootstrap Cohen's d; replicate with 3 SBERT models
- **Success**: d ≥ 0.1, J-T p < 0.05, H→AI > AI→H, ≥2/3 models consistent
- **Falsification**: d < 0.1 OR asymmetry fails OR J-T non-significant

### P2 — Secondary (Partner-Specificity)
- **Statement**: cos(H_next, A_actual) > cos(H_next, A_topic-matched) > cos(H_next, A_random); d ≥ 0.1 between actual and topic-matched
- **Test**: KNN topic-matched (K=5 nearest-neighbor by prompt embedding from different conversations, same tier) vs random shuffle vs actual partner
- **Success**: Three-way ordering holds with d ≥ 0.1 between adjacent levels
- **Falsification**: Actual ≈ topic-matched → C_sem measures topical coherence, not accommodation

### P3 — Conditional Secondary (Within-Tier Quality)
- **Condition**: N_pairs ≥ 1000 per tier (verify before committing)
- **Statement**: Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) > 0; surviving all three length-control operationalizations
- **Test**: (a) raw cosine, (b) length-matched truncation, (c) prompt-vector projection; bootstrap CI n=1000
- **Success**: Δ > 0 with CI lower bound > 0 under ≥2/3 operationalizations; PM regression significant after surface controls
- **Falsification**: Δ ≈ 0 under length control → quality gradient not isolatable from length artifact

---

## Novelty
First semantic-embedding-level operational metric for human accommodation to RLHF alignment quality. Extends Danescu 2011 (function-word → semantic embedding; human-human → human-AI; Wikipedia/SCOTUS → RLHF tiers). Extends Chang & Wang 2025 (word-level → SBERT cosine; no tiers → three-tier quality gradient; no within-tier probe → PM chosen/rejected). Provides BiAlign [Shen et al. 2025] with the scalable technical metric they call for. Zero prior work on SBERT cos_sim across RLHF tiers.

---

## Experimental Design
- **Dataset**: Anthropic/hh-rlhf (helpful-base, helpful-rejection-sampled, helpful-online splits); ~273,617 conversation turns
- **Primary model**: all-MiniLM-L6-v2 (CPU; 14K sentences/sec)
- **Robustness**: paraphrase-MiniLM-L6-v2, all-mpnet-base-v2
- **Baselines**: KNN topic-matched (K=5 nearest-neighbor by prompt embedding), true random shuffle, length-matched truncation, prompt-vector projection, surface-feature residualization
- **Statistics**: Mann-Whitney U, Jonckheere-Terpstra, bootstrap Cohen's d (n=1000, seed=42), linear regression for PM mediation, KS test for prompt distribution equivalence
- **Runtime**: <2 hours total, CPU-only

---

## Limitations
- Cross-sectional design cannot establish within-user causal accommodation trajectories (HH-RLHF lacks user IDs)
- Psychological mechanism ("epistemic uptake sensitivity") is assumed, not directly measured; PM mediation is a proxy test
- HH-RLHF is helpfulness-focused; harmlessness split and open-ended conversations not covered
- SBERT embedding geometry encodes both content and style; baseline subtraction controls topical persistence but may not fully separate
- N_pairs for P3 (chosen/rejected Δ) must be verified before committing to that prediction
- Wikipedia admin counterexample [Danescu 2011] shows power → accommodation can be non-simple; asymmetry patterns require careful interpretation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | CONVERGED at Exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Mechanism specificity (pre-registered mediation test); N_pairs for P3 (empirical verification) |
| **Phase 2B Ready** | YES |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Hypothesis: H-SemAccom-v1*
*Gap: gap-1-sbert-accommodation*
