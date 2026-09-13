# Phase 2A Discussion Log

**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Architecture:** Independent-Controller Ablation (Claude self-plays ALL personas)
**Gap:** Gap 2 — No Empirical Evidence of Bidirectional Tension
**Execution Mode:** UNATTENDED
**Initialized:** 2026-08-25

## Previous Failure / Routing Context

**Source:** .serena/memories/failure_h-m1_run1.md

| Field | Value |
|-------|-------|
| Hypothesis | h-m1 |
| Failure Type | synthetic_data_inversion |
| Status | FAIL → ROUTED_TO_PHASE_0 |
| Date | 2026-08-25 |

**Summary:** h-m1 tested RLHF embedding cohesion using AlpacaEval 2.0 data. HuggingFace API unavailable triggered synthetic fallback with inverted cohesion results. Routed to Phase 0 (full brainstorm restart), which produced the current bidirectional alignment research direction — a completely different question.

**Constraints for this Phase 2A:**
1. Do NOT use synthetic data — use only real existing published datasets
2. Do NOT propose hypotheses dependent on the AlpacaEval leaderboard fallback
3. Current research (bidirectional alignment) is a fresh direction, not a retry of h-m1

## Briefing Context

**Selected Gap:** Gap 2 — No Empirical Evidence of Bidirectional Tension (RLHF Improvement ↔ Human Calibration Trade-off)

**Core Question:** Does improving AI→Human alignment (RLHF reward scores, benchmark performance) systematically reduce Human→AI alignment (human calibration, over-reliance rate)?

**Key Papers:**
- P1: Ouyang et al. 2022 — InstructGPT (AI→Human RLHF signal)
- P2: Bai et al. 2022 — Constitutional AI (AI→Human harmlessness signal)
- P3: Coste et al. 2023 — Reward overoptimization (proxy-gold gap evidence)
- P4: Lai et al. 2021 — AI-assisted decisions (Human→AI appropriate reliance proxy)

**Feasibility Constraints:** No new benchmarks, no synthetic data, no human annotation — testable using existing published datasets only.

## Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The bidirectional tension hypothesis opens genuinely unexplored empirical territory. Coste et al. 2023 [P3] already demonstrated that RLHF overoptimization creates a proxy-gold divergence — RM scores keep climbing while actual human preference plateaus and reverses. This is structurally identical to what we're proposing at the bidirectional level: AI→Human alignment metrics may climb while Human→AI alignment (calibration, appropriate reliance) degrades.

The key novelty angle: no one has framed the Coste overoptimization result as a *bidirectional* alignment phenomenon. The proxy-gold gap IS the AI→Human direction diverging from the human behavioral response direction.

Three unconventional angles worth exploring:

1. **Cross-dataset correlation approach**: Use RLHF leaderboard scores (AlpacaEval 2.0, MT-Bench, HELM) as the AI→Human axis, and published over-reliance rates from Lai et al. [P4] as the Human→AI proxy. Compute Spearman correlation across model-condition pairs. No new data needed.

2. **Within-study decomposition**: In InstructGPT [P1], if labelers agreed with RLHF outputs at higher rates as training progressed, that agreement-rate trajectory IS a Human→AI signal hidden in the existing dataset.

3. **Constitutional AI contrast**: CAI [P2] reduces human labeler burden. Compare: does reduced human-AI interaction produce better-calibrated users than InstructGPT's high-interaction labeling?

**Key Points:**
- Coste 2023's proxy-gold gap is the mechanistic seed of the bidirectional tension hypothesis
- InstructGPT's labeler preference data may contain hidden Human→AI signals
- CAI vs. InstructGPT offers a natural experiment on human-AI interaction intensity

## Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is creative, but I must stress-test the falsifiability architecture. Three serious threats:

**Threat 1 — Temporal confounding.** If we correlate RLHF benchmark scores (improving over time) with over-reliance rates from Lai et al. (also changing over time), we get a spurious correlation driven by chronological co-movement. Need a within-model or cross-condition design.

**Threat 2 — Scale incommensurability.** AI→Human alignment (task-specific benchmark accuracy) and Human→AI alignment (behavioral appropriate reliance rate from Lai) don't share a common unit. Correlation without construct mapping is apples-to-oranges.

**Threat 3 — Missing counterfactual.** To demonstrate a trade-off, we need pairs: (AI→Human high, Human→AI measured) AND (AI→Human low, Human→AI measured) for the SAME system. InstructGPT gives us the high condition. Where is the low condition with Human→AI measured?

**What WOULD make this falsifiable:**
- Specify exact datasets providing both signals for the same model family
- Falsification criterion: if Spearman ρ(AI→Human, Human→AI) > 0, trade-off rejected; ρ < 0, supported
- At least 3 data points (model-condition pairs) where both signals are measured

The Coste et al. [P3] paper is closest: it measures RM score (AI→Human proxy) AND gold human preference (Human→AI-adjacent) at multiple KL budget levels for the SAME model family.

**Key Points:**
- Coste et al. [P3] KL-vs-gold-preference curve is the most falsifiable existing dataset
- Need within-study design to avoid confounders
- Define explicit Spearman ρ falsification criterion

## Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's concerns are valid but let me redirect toward impact. The field is saturated with alignment benchmarks; what's missing is a causal argument that current evaluation paradigm is actively harmful — that optimizing AI→Human metrics erodes human calibration.

**Impact argument — two layers:**

**Layer 1 — Descriptive (immediately testable):** Compute a coverage ratio R = (AI→Human metrics) / (Total metrics) across published alignment benchmark papers. If R > 0.90, we show 90% of evaluation is measuring only one direction. Computable purely from Phase 1 sources — no new data.

**Layer 2 — Inferential (mechanistic):** Use Coste et al. [P3] as the empirical anchor. The proxy-gold divergence IS empirical evidence that AI→Human proxy optimization can harm actual human alignment. Reframe: "We have direct published evidence that RLHF overoptimization degrades human preference satisfaction — this is the bidirectional tension in action."

**Feasibility-constrained approach (publishable):** Re-analyze Coste et al.'s gold preference data as a Human→AI calibration proxy. Gold human preference at different KL budgets = how well calibrated evaluators are to the model's actual quality. As RM score diverges from gold (overoptimization), interpret the proxy-gold gap as calibration error. No new data.

**Key Points:**
- Coverage ratio of AI→Human vs Human→AI benchmarks is immediately computable
- Coste et al.'s proxy-gold gap can be re-interpreted as calibration degradation metric
- Impact: first empirical evidence that alignment optimization metrics are anti-calibration

## Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Feasibility audit of proposed approaches:

**Approach A (cross-study correlation):**
- AI→Human: AlpacaEval, MT-Bench, HELM — YES, publicly available
- Human→AI: Lai et al. data — PARTIALLY; OSF availability unclear
- Fatal flaw: different models, domains, time periods — confounded; maybe 3-5 valid data points
- **Feasibility: LOW for correlation claim. HIGH for descriptive taxonomy.**

**Approach B (Coste proxy-gold reanalysis):**
- Coste et al. data: paper provides curves in figures, not raw tables. Need digitization or author contact.
- Re-interpretation as calibration metric: conceptually valid but a stretch — gold preference is aggregate preference, not individual calibration
- **Feasibility: MEDIUM.**

**Approach C (coverage ratio taxonomy):**
- Input: published alignment benchmark papers from Phase 1
- Classify each metric as AI→Human or Human→AI; count; compute ratio
- Tools: Python pandas, simple classification schema
- Data: ALL available now
- **Feasibility: VERY HIGH. Can execute immediately.**

**Recommendation:** Build hypothesis around Approach C (coverage ratio) as core testable claim, Coste et al. [P3] as mechanistic case study.

**Concrete hypothesis draft:** "AI alignment evaluation exhibits systematic measurement asymmetry (R > 0.90). Furthermore, Coste et al. overoptimization result demonstrates that maximizing AI→Human proxy metrics degrades actual human preference alignment — first mechanistic evidence for bidirectional tension."

**Key Points:**
- Coverage ratio taxonomy immediately feasible using Phase 1 sources
- Coste et al. data availability uncertain — check GitHub for raw data
- Coverage ratio + Coste reanalysis = the defensible two-part hypothesis

## Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize toward a robust, falsifiable, feasible hypothesis.

**Emerging consensus hypothesis:**

*The AI alignment evaluation literature exhibits a systematic measurement asymmetry (AI→Human coverage dominance), quantifiable via meta-analysis of published benchmarks. Furthermore, RLHF overoptimization studies (Coste et al. 2023) demonstrate that maximizing AI→Human proxy alignment metrics produces measurable degradation in actual human preference satisfaction — operationalizable as a bidirectional tension between proxy-metric optimization and human-behavioral calibration.*

**Why this is strong:**

1. Two testable layers: (a) coverage ratio R > 0.90 and (b) proxy-gold divergence = calibration erosion
2. Existing data only: published benchmark papers for (a); Coste et al.'s figures for (b)
3. Avoids temporal confounders: within-study KL-budget variation, not cross-system time-series
4. Novel: no prior paper has computed a bidirectional coverage ratio for alignment literature

**Critical strengthening — Human→AI proxy definition:** *"Human calibration proxy = the gap between AI→Human proxy metric (RM score) and actual human preference agreement (gold label) at a given optimization level."* Directly computable from Coste et al.

**Testable predictions:**
- P1: Coverage ratio R > 0.90 in alignment benchmark literature
- P2: Proxy-gold gap increases monotonically with RLHF optimization pressure (Coste et al.)
- P3 (conditional): proxy-gold gap magnitude correlates with over-reliance rates from Lai et al.

**Key Points:**
- Two-layer hypothesis: descriptive + mechanistic
- Within-study designs avoid temporal confounding
- Human calibration proxy = proxy-gold gap in Coste et al.

## Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Adversarial pressure on remaining weak points:

**Weakness 1 — Coverage ratio is trivially confirmable.** ICLR 2025 survey already found 400 papers are asymmetric. Computing R > 0.90 is confirmatory, not discovery. Need to claim something SURPRISING: either a specific numeric threshold with theoretical meaning, or a novel classification scheme revealing structure the ICLR survey missed.

**Weakness 2 — Proxy-gold gap ≠ human calibration.** Coste's proxy-gold gap measures disagreement between two preference elicitation methods (RM vs. held-out human evaluator). This is NOT the same as Lai's appropriate reliance (human decision correctness conditional on AI correctness). Conflating these is a construct validity error — reviewers will catch it.

**Weakness 3 — P3 requires data we don't know is accessible.** If Lai et al. behavioral data unavailable in machine-readable form, P3 collapses. Scope as conditional.

**Required mitigations:**

1. Reframe coverage ratio as mechanism discovery: don't claim R > X as the hypothesis. Claim: "We identify a novel DUAL-AXIS classification scheme revealing previously uncharacterized structural patterns in how Human→AI dimensions are proxied or omitted."

2. Separate constructs: keep coverage ratio (meta-analysis) and Coste proxy-gold (reanalysis) as two independent claims; don't force unified theory requiring construct bridging.

3. Scope P3 as conditional: "IF Lai et al. data is accessible, we test P3; otherwise deferred to future work."

**Revised hypothesis (stress-tested):**
- Core: Alignment evaluation literature has R > 0.90 AI→Human coverage, AND the Human→AI dimension, where measured at all, uses proxy metrics conflating AI output quality with human behavioral calibration.
- Mechanism: Coste et al. proxy-gold divergence demonstrates AI→Human proxy optimization can produce outcomes anti-correlated with human behavioral satisfaction — first direct mechanistic evidence of bidirectional tension.
- Scope: NLP alignment benchmarks 2018-2024; no cross-domain generalization claimed.

**Key Points:**
- Coverage ratio needs stronger framing — "first quantification" not "confirmation"
- Proxy-gold gap ≠ human calibration — keep constructs separate
- P3 conditional on data access

## Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique of coverage ratio as confirmatory is the most important objection. Pivot that resolves it:

**Novel contribution: First empirical quantification of the calibration-alignment divergence curve.**

Instead of a static coverage ratio, propose a DYNAMIC measurement: across different RLHF optimization pressure levels (Coste et al.'s KL budget axis), compute at each level:
- AI→Human alignment: RM score (available in Coste figures)
- Human→AI alignment proxy: gold human preference rate (available in Coste figures)
- Bidirectional gap: RM score − gold preference rate

This gives a **calibration-alignment divergence curve** — a novel empirical construct not previously named or computed. The curve shows: as AI→Human optimization pressure increases, the gap between AI optimization target and human behavioral response grows. This is the bidirectional tension, empirically plotted for the first time.

**Why this is novel beyond ICLR 2025:**
- ICLR 2025 survey: qualitative taxonomy of 400 papers, no empirical measurement
- Coste et al. 2023: measures proxy-gold gap as reward hacking problem, not bidirectional alignment problem
- Our contribution: reframe Coste's proxy-gold curve as the first empirical calibration-alignment divergence curve; name the construct; compute slope; test whether slope is significantly positive

**Testable, falsifiable:**
- H0: slope of calibration-alignment divergence curve ≤ 0 (no tension)
- H1: slope > 0 (as AI→Human optimization increases, Human→AI calibration gap increases)
- Test: linear regression on Coste et al.'s digitized KL-vs-(RM_score − gold_preference) data points
- Success criterion: β > 0, p < 0.05, R² > 0.6

**Data requirements:** Coste et al.'s figure data (digitizable from published paper; no raw data needed). Completely feasible NOW.

**Key Points:**
- Calibration-alignment divergence curve is the novel empirical construct
- Directly reframes Coste et al. as bidirectional alignment evidence
- Testable with digitized figure data — no new experiments needed

## Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's divergence curve proposal resolves my falsifiability concerns substantially. Statistical rigor assessment:

**Strengths:**
- Within-experiment design (same model family, varying KL) eliminates temporal confounding
- Independent variable (KL budget) is continuous and monotonically varying
- Dependent variable (RM score − gold preference) computed from the same experimental setup
- Linear regression β > 0 test is clean and reproducible

**Remaining statistical concerns:**

1. **Sample size:** Coste et al. likely reports 5-10 KL budget levels. With n=5-10, regression has very low power. Mitigate by pooling across multiple curves (different model scales) or adding Gao et al. 2023 replication.

2. **Construct validity of gap metric:** "RM score − gold preference rate" mixes unbounded score (RM) with bounded probability (0-1 preference rate). Must normalize RM scores before computing gap, or use rank correlation.

3. **Generalizability:** One study insufficient to claim "bidirectional tension exists." Need replication in at least one other RLHF paper.

**Rigorous statistical protocol:**
- Digitize Coste et al. KL budget vs. RM score AND gold preference rate curves
- Normalize RM scores to [0,1] within each curve
- Compute normalized gap = RM_norm − gold_preference at each KL level
- Fit: gap ~ KL_budget; report β, SE, p-value, R², 95% CI
- Replicate on Gao et al. 2023 "Scaling Laws for Reward Model Overoptimization" (arXiv 2210.10760)

**Formalized predictions:**
- P1: β > 0, p < 0.05 — bidirectional tension confirmed
- P2: R² > 0.5 — linear divergence explains majority of variance
- P3 (replication): same positive trend in Gao et al. data

**Key Points:**
- Regression design valid; sample size is key limitation
- Normalization required before gap computation
- Gao et al. 2023 provides replication dataset

## Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis has crystallized. Impact argument made precise:

**Policy implications of confirmed divergence curve:**

1. **Benchmark inflation problem:** If RM score increases while gold human preference decreases, then AI systems with higher benchmark scores are LESS aligned to actual human calibration at high optimization pressures. AlpacaEval/MT-Bench leaderboards may be inversely correlated with real alignment beyond an inflection point.

2. **RLHF training budget decision:** Labs decide how long to RLHF-train based on RM score improvement. If divergence curve shows RM and gold decouple beyond a KL threshold, this identifies an optimal RLHF stopping criterion that current practice ignores.

3. **Evaluation reform argument:** Coverage ratio (95% AI→Human) + divergence curve = two-part argument: (a) we measure the wrong things, (b) optimizing for what we measure makes actual alignment worse.

**Research positioning:** Meta-science paper about AI alignment evaluation — similar to "Goodhart's Law in RL" (Krakovna et al. 2020) but applied to bidirectional human-AI alignment. Novel technical contribution (divergence curve) anchors a broader policy argument.

**Story arc:**
1. Alignment evaluation is asymmetric (coverage ratio — descriptive)
2. Asymmetric optimization creates divergence (Coste evidence — mechanistic)
3. Divergence has measurable positive slope (our computation — empirical)
4. Implication: optimal RLHF stopping point exists before inflection (practical)

**Key Points:**
- Divergence curve supports optimal RLHF stopping criterion argument
- Coverage ratio + divergence curve = two-part high-impact contribution
- Positions as meta-science about alignment evaluation

## Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility check. Concrete execution plan:

**Task 1: Coverage ratio meta-analysis**
- Input: Phase 1 paper list (TruthfulQA, BBQ, HELM, HHH-RLHF, WinoBias, InstructGPT, Constitutional AI, MACHIAVELLI, Sorensen 2024)
- Method: Classify each metric as AI→Human or Human→AI using dual-axis taxonomy
- Output: R, breakdown by year and domain
- Tools: Python + pandas, manual classification schema
- **IMMEDIATELY FEASIBLE ✅ (2-3 person-days)**

**Task 2: Calibration-Alignment Divergence Curve**
- Input: Coste et al. 2023 figures (KL budget vs. RM score, KL budget vs. gold preference)
- Method: Figure digitization using WebPlotDigitizer (free tool), extract tuples
- Output: Normalized gap curve, linear regression statistics
- **FEASIBLE ✅ (1-2 days)**
- Risk: Figure resolution may limit precision; mitigate with multiple figures

**Task 3: Replication**
- Input: Gao et al. 2023 "Scaling Laws for Reward Model Overoptimization" (arXiv 2210.10760)
- Method: Same digitization + regression on Gao et al.'s KL-vs-preference curves
- **FEASIBLE ✅ — published paper with similar figures**

**Task 4: Lai et al. correlation (conditional)**
- Input: Lai et al. decision-making datasets (OSF availability unknown)
- **CONDITIONAL ⚠️ — scope as future work if unavailable**

**Implementation sketch:**
```python
# Task 1: Coverage ratio
R = len(AI2H_metrics) / len(all_metrics)

# Task 2: Divergence curve
gap = normalize(rm_score) - gold_preference  # per KL level
beta, p_val, r2 = linregress(kl_budget, gap)
```

**Timeline: 3-5 days. Achievable.**

**Key Points:**
- Both main tasks feasible immediately with existing published data
- Gao et al. 2023 is the replication dataset
- P3 scoped conditional — protects hypothesis from data access risk

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The calibration-alignment divergence curve is a genuinely novel empirical construct. Reframing Coste et al.'s proxy-gold gap as the first measurement of bidirectional alignment tension is a creative contribution not made by the field. The coverage ratio + divergence curve approach provides multiple novelty entry points at different levels of contribution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The regression test (β > 0, p < 0.05) is a clean falsification criterion. Within-experiment design eliminates temporal confounding. Sample size limitation (n≈10 per curve) is mitigated by pooling across multiple figures and Gao et al. replication. Statistical protocol is rigorous and reproducible.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** High-impact framing as meta-science about alignment evaluation. Connects to practical decisions (optimal RLHF stopping criterion) and policy (benchmark inflation problem). NeurIPS/ICLR-worthy if divergence curve slope is confirmed positive.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Both main tasks immediately executable with existing published data. Gao et al. provides replication. Lai et al. correlation scoped as conditional. 3-5 day timeline is realistic. No new data collection needed.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged: **"Current AI alignment evaluation exhibits a systematic bidirectional asymmetry, quantifiable as an AI→Human coverage ratio (R > 0.90 in published literature), and RLHF overoptimization produces a calibration-alignment divergence curve where the gap between AI→Human proxy metrics (reward model score) and Human→AI calibration proxies (gold human preference) increases monotonically with optimization pressure (KL budget), with a significantly positive slope (β > 0, p < 0.05)."**

Core mechanism: RLHF trains against a proxy metric (RM score) that diverges from actual human behavioral response (gold preference) under sustained optimization pressure. This proxy-gold divergence is the first empirical instance of bidirectional alignment tension in published data. We name this the **calibration-alignment divergence curve** and provide its first quantitative characterization using Coste et al. 2023 and Gao et al. 2023 figure data.

Design: (1) meta-analysis of published alignment benchmarks to compute coverage ratio — immediate; (2) digitization of KL-budget curves from two RLHF overoptimization papers to fit the divergence curve and test the slope — immediate. No new data collection, no annotation, no synthetic data. Testable now and falsifiable by a non-positive regression slope.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Coverage ratio must be framed as "novel operationalization" not "confirmation" — ICLR 2025 identified asymmetry qualitatively; we quantify it with a specific metric schema
- Construct validity: proxy-gold gap ≠ human calibration in Lai et al. sense; must label it "evaluation calibration" distinct from "user calibration"
- Sample size (n≈5-10 per regression) limits power; report confidence intervals, not just p-values
- **Mitigation Strategy:** Pool data across multiple Coste et al. figures + add Gao et al. replication to increase n; explicitly discuss construct distinction in limitations; reframe coverage ratio as "first quantification using dual-axis schema" rather than "discovering the asymmetry"
