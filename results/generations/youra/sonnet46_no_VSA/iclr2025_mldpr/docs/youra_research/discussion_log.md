# Phase 2A Discussion Log

**Gap ID:** gap-3  
**Gap Title:** Theoretical Direction of Diversity-Displacement Relationship (HR < 1 vs HR > 1)  
**Date:** 2026-08-03  
**Architecture:** Self-Contained Tikitaka Loop  
**Execution Mode:** UNATTENDED  

---

### Previous Failure / Routing Context

**Pipeline Status:** ROUTE_TO_0 (Attempt 11 — 10 prior failures routed back through Phase 0)

This Phase 2A is entered with mandatory failure context from 6 Serena memory files. The following families of approaches are **PROHIBITED** for new hypothesis design:

#### Failed Hypothesis Families (DO NOT REPEAT)

| Hypothesis | Status | Root Cause | Prohibition |
|------------|--------|-----------|-------------|
| h-e1 Run 1 | FAIL (MUST_WORK_GATE) | Gini std=0.065 < 0.10 threshold; authorship diffuse in PwC at annual (task,year) | Do NOT use Gini coefficient on PwC authorship at annual resolution |
| h-e1 Run 2 | FAIL (MUST_WORK) | Only 38/100 required displacement events; exact slug matching 33% coverage | Do NOT use exact Koch slug matching; do NOT set min_papers≥10 |
| h-m1 Run 1 | FAIL (PROXY_INSUFFICIENT_VARIANCE) | C_t cumulative count partial_r²=0.0011; collapses into time proxy | Do NOT use raw cumulative count metrics; must pass partial_r² FAIL FAST gate |
| h-m1 Run 2 | FAIL (MUST_WORK — statistical null) | HR=0.871, LRT p=0.565; only 22 events (34.1% coverage); underpowered | Do NOT use CoxTimeVaryingFitter; do NOT aggregate dscore to task level via mean |
| h-e2 Run 1 | LIMITATION (SHOULD_WORK) | NLP vs CV reign length identical (both median=1yr); Cox HR=1.334 NLP displaced FASTER | Domain type not a useful moderator; NLP>CV reign direction is WRONG |
| h-e1 PASS | COMPLETED | 372 qualified (task,year) cells — panel infrastructure valid | h-e2 panel (87 tasks, 345 events) reusable; CoxPHFitter(penalizer=0.1) validated |

#### What IS Available and Validated
- h-e2 panel: 87 tasks, 345 displacement events, EPV=115 — reuse directly
- lifelines CoxPHFitter(penalizer=0.1): 14/14 tests pass — validated library
- pwc-archive/evaluation-tables: 326k rows, paper_url confirmed, CC-BY-SA-4.0
- Fuzzy matching for task slug normalization — avoids exact-match coverage failures

#### New Direction for Attempt 11
**Core innovation:** `paper_diversity_ratio = unique_paper_count / total_rows` — normalized ratio that is time-independent by construction. Guards against Attempt 10's time-proxy collapse (partial_r²=0.0011) via FAIL FAST partial_r² gate BEFORE Cox regression.

**Prohibited approach families for this discussion:**
1. Gini coefficient on authorship
2. Raw cumulative count proxies (C_t)
3. CoxTimeVaryingFitter (coverage ceiling: 34.1%)
4. Domain-type moderators (NLP vs CV)
5. Performance trajectory predictors (SOTA score coverage: 34.1%)
6. FAIR-doc composite metrics (metrics_count=0 degenerate; papers_linked_count confounded)
7. Lagged annual submission flow

---

## Research Briefing

**Research Question (Attempt 11):**  
Does benchmark submitter diversity at introduction year (`unique_paper_count_at_intro`, `paper_diversity_ratio_at_intro` from pwc-archive/evaluation-tables) significantly predict plurality benchmark displacement hazard in a CoxPHFitter model on the h-e2 panel (87 tasks, 345 events, EPV=115)?

**Key Design Innovation:** FAIL FAST partial_r² gate before Cox regression guards against time-proxy collapse.

**Competing Mechanisms:**
- **H1 (Lock-in):** High submission diversity → broad stakeholder adoption → switching costs → slower displacement (HR < 1)
- **H2 (Saturation):** High submission diversity → benchmark overuse/ubiquity → community replacement pressure → faster displacement (HR > 1)
- **H0:** No significant effect (HR ≈ 1, p > 0.05)

**Evidence Base:**
- Ott et al. 2022 (Nature Comms, 3765 benchmarks): breadth/versatility correlates with benchmark longevity — partial support for H1
- Koch et al. 2021 (180 citations): high concentration (low diversity) predicts stagnation — indirect support for H2 via complement
- Paullada et al. 2021 (671 citations): dataset lifecycle governance framework — context
- No prior study tests submitter diversity as Cox predictor on Papers With Code — genuine empirical gap

**Data Infrastructure (confirmed):**
```python
# pwc-archive/evaluation-tables → unique_paper_count_at_intro
diversity_df = df.groupby('task_path')['paper_url'].agg(
    unique_paper_count=pd.Series.nunique
).reset_index()
diversity_df['paper_diversity_ratio'] = diversity_df['unique_paper_count'] / total_rows

# FAIL FAST gate: partial_r² > 0.01 before Cox
# Then merge onto h-e2 panel and run CoxPHFitter(penalizer=0.1)
```

**Papers:** No reference papers downloaded (none provided in Phase 1).  
**Gap Priority:** Critical (PRIMARY) — determines paper narrative and interpretation.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're sitting on a beautiful natural experiment that nobody has thought to run? The Papers With Code leaderboard isn't just a static snapshot — it's a living record of community investment decisions made over years. Every `paper_url` in `evaluation-tables` represents a deliberate choice by a research team to measure themselves against a benchmark. Now imagine this: when many diverse teams converge on the same benchmark early in its life, what does that signal? Either they're locked in by the benchmark's gravity — a community focal point nobody wants to abandon — or they're collectively wearing it out, pressing toward the saturation event horizon where the benchmark stops being useful.

What excites me about Attempt 11 is that `paper_diversity_ratio = unique_paper_count / total_rows` is conceptually a different beast from anything tried before. It's not a count that grows with time. It's a normalized signal about the *structure* of community engagement at the moment the benchmark first claimed plurality. Think of it like a species diversity index for research communities — high ratio means many teams each contributing once or twice; low ratio means a few teams submitting repeatedly. And crucially, this structural signal is frozen at a meaningful point in time: the plurality introduction year. No temporal bleeding, no time-proxy collapse.

I want to propose three unconventional angles to explore: First, **diversity as a bifurcation signal** — perhaps the relationship isn't monotone but has a threshold. Benchmarks with mid-range diversity (not too concentrated, not too diffuse) might have the optimal mix of consensus and breadth. A spline or threshold regression within the Cox framework could reveal this. Second, **the mechanism chain matters more than the direction** — we need to be clear about whether community engagement precedes or follows adoption decisions. If teams choose well-adopted benchmarks, diversity is endogenous to quality; if diversity causally drives subsequent adoption, we're measuring something structurally different. Third, **cross-benchmark substitutability** — when a task has many popular benchmarks (high task-level diversity), individual benchmark displacement may be faster because alternatives are readily available. This would suggest a task-level moderation we could test with interaction terms.

The Ott et al. 2022 finding that breadth/versatility correlates with benchmark longevity in 3765 benchmarks is our strongest theoretical anchor for H1 (lock-in). But Koch et al. 2021's finding that dataset usage is increasingly concentrated on fewer datasets leaves open the possibility that H2 (saturation pressure) dominates in the ML leaderboard context specifically. Neither paper ran Cox regression on PWC displacement events — that's our contribution.

**Key Points:**
- `paper_diversity_ratio = unique_papers / total_rows` is genuinely novel — no prior Cox study has used this on PWC displacement
- Three competing framings: (1) linear lock-in (HR<1), (2) linear saturation (HR>1), (3) non-monotone threshold effect
- FAIL FAST partial_r² gate is the critical safeguard against repeating Attempt 10's time-proxy collapse
- Cross-benchmark substitutability at task-level may be an interaction-term moderator worth testing

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me translate it into something we can actually test. The most important structural question before we even think about Cox regression is: what is the *causal* interpretation of `paper_diversity_ratio_at_intro`? This matters for how we design our falsification tests.

Here's the core identification challenge: `paper_diversity_ratio_at_intro` is measured at the same time period as the beginning of the survival clock. This means any correlation with subsequent displacement could reflect: (a) genuine causal influence of diversity on survival dynamics, (b) reverse causation if benchmarks that are about to be displaced attracted last-ditch adoption from many teams, or (c) confounding by benchmark quality or prestige. The FAIL FAST partial_r² gate guards against time-proxy collapse specifically, but does not guard against these other threats to validity.

What would disprove H1 (lock-in)? The unambiguous falsifier is: HR ≥ 1.0, CI_lower ≥ 1.0 at 95% confidence, LRT p < 0.05. What would disprove H2 (saturation)? HR ≤ 1.0, CI_upper ≤ 1.0 at 95% confidence, LRT p < 0.05. What would disprove the hypothesis entirely? LRT p > 0.05, |HR - 1| < 0.10, and partial_r² < 0.01 after partialing out temporal controls. All three falsification conditions need success criteria specified before analysis to avoid HARKing.

Three specific, measurable predictions I propose: **P1** — The FAIL FAST gate will pass: partial_r²(diversity_ratio, [task_age, intro_year]) > 0.01, confirming time-independence. **P2** — `log_unique_paper_count_at_intro_z` achieves LRT p < 0.05 in CoxPHFitter on h-e2 panel. **P3** — Kaplan-Meier curves stratified by diversity quartile show a monotone ordering with Q1 vs Q4 log-rank p < 0.05.

The confounds that need to be controlled are already in the h-e2 panel: task_age and log_publication_volume. Prof. Pax needs to weigh in on whether benchmark_introduction_year is overdetermined when combined with task_age — if both are included, multicollinearity from the h-m1 VIF failures (task_age VIF=22.3, log_publication_volume VIF=22.4) may resurface. The FAIL FAST gate checks r(diversity_ratio, task_age) < 0.80 and VIF < 5, but those were the PREDICTOR's collinearity guards, not the control set's internal collinearity.

**Key Points:**
- Pre-registration-style success criteria needed before analysis: HR<1 (H1), HR>1 (H2), p<0.05 (both), partial_r²>0.01 (FAIL FAST)
- Controls VIF problem from h-m1 (task_age VIF=22.3) may affect this model too — needs monitoring
- Three falsifiable predictions: FAIL FAST gate pass, LRT p<0.05, KM quartile separation
- Reverse causation threat: benchmarks near displacement may attract late-stage diverse adoption

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask is: why should the field care about this result, regardless of which direction the HR points? And I think the answer is genuinely compelling if we frame it correctly.

What we're offering is the first empirical test of benchmark lifecycle dynamics using a community-structure predictor, on the only large-scale historical leaderboard record that exists — Papers With Code. The ICLR 2025 workshop on "overfitting and overuse of benchmark datasets" has created an intellectual moment when the community is asking "why do benchmarks die?" We're not just answering that question abstractly; we're providing a quantitative, replicable answer using survival analysis — the appropriate statistical framework for time-to-event data.

The scientific contribution has two distinct layers. If HR < 1 (lock-in), we're providing evidence for a network-effect theory of benchmark persistence: early broad adoption creates sticky infrastructure that resists displacement. This has direct policy implications for benchmark designers — creating adoption breadth early may extend benchmark utility. If HR > 1 (saturation), we're providing evidence for the overuse hypothesis that the ICLR workshop is directly concerned about: diversity signals consensus at the point of overexposure, making community replacement inevitable. Either direction is publishable, but the saturation direction is arguably more novel since it challenges the naive "popular = durable" intuition.

The novelty I'm most excited about is the *zero*-hypothesis test structure. Prior work (Ott 2022, Koch 2021) has documented correlates of benchmark adoption or concentration, but none has run a survival model with displacement as the outcome. Koch finds "concentration on fewer datasets over time" — but that's a population-level trend, not a benchmark-level predictor. We're doing something structurally different: predicting *individual* benchmark fate from its structural properties at birth.

The question I'd push back on: is EPV=115 sufficient to detect the effect sizes we care about? With |HR-1| ≥ 0.10 as the minimum threshold (Prof. Vera's criterion), the minimum detectable effect with 345 events and 3-4 covariates is well within reach — Cox regression is surprisingly powerful at this event count. I'm satisfied the statistical power argument is solid.

**Key Points:**
- First empirical Cox test of diversity → displacement on Papers With Code — genuine novel contribution
- ICLR 2025 workshop creates perfect intellectual timing for this result
- Both HR directions are publishable; HR>1 (saturation) challenges popular-equals-durable intuition more sharply
- EPV=115 sufficient for detecting |HR-1|≥0.10 at 345 events — power argument solid

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be realistic here. The mechanism underlying both H1 and H2 needs to be spelled out with enough specificity that I can evaluate whether it's scientifically sound, not just metaphorically appealing.

For H1 (lock-in): the proposed causal chain is — high diversity at intro year → broad stakeholder community → high switching costs → resistance to benchmark displacement. What evidence supports this chain? The switching cost claim requires that teams who adopted the benchmark early will resist alternatives even when better ones emerge. This is plausible by analogy with Rogers' Diffusion of Innovations, but for it to hold in the benchmark context, we need evidence that teams prefer compatible baselines over better baselines. Here's what worries me: benchmark adoption costs are low. Switching from GLUE to SuperGLUE required code changes, yes, but the NLP community did it at scale in ~18 months. If switching costs are low, the lock-in mechanism may not have sufficient friction to produce HR < 1.

For H2 (saturation): the chain is — high diversity at intro year → widespread adoption → benchmark treated as "solved" → community searches for replacement. This is more mechanistically plausible because it requires no friction — it just requires that broad adoption signals saturation, which then attracts attention to frontier benchmarks. But what's the transmission mechanism from "many teams submitting" to "community builds replacement"? Is it citation-based? Leaderboard stagnation (when SOTA stops improving)? The mechanism needs to be explicit because it determines whether the proxy (`paper_diversity_ratio`) is measuring the right upstream construct.

The feasibility assessment: **technically sound**. The data pipeline (pandas groupby nunique → log1p → z-standardize → CoxPHFitter) is straightforward. The FAIL FAST gate is theoretically valid. The existing h-e2 panel has been validated over 10 attempts and 14/14 tests pass. The `paper_url` join is the only unproven step. What worries me is the interpretation ambiguity if HR direction is ambiguous (HR ≈ 1, p < 0.05 but confidence interval spanning both directions). Is the hypothesis falsifiable even in this intermediate case?

I want to confirm: the H0 here is precise enough. H0 is "no significant effect" (HR = 1.0, LRT p > 0.05). This means H1 and H2 are both ALTERNATIVE hypotheses, and the experiment tests whether EITHER direction is detectable. Prof. Vera should confirm that the analysis plan doesn't fall into the trap of claiming the "correct" direction was predicted post-hoc.

**Key Points:**
- Mechanism specificity needed: lock-in requires high switching costs (questionable in fast-moving ML), saturation requires transmission mechanism from diversity to replacement-seeking
- Data pipeline technically sound; `paper_url` join coverage is the only unverified step
- H0 is precisely "no effect" — H1/H2 are competing alternative directions, both post-hoc interpretations
- Interpretation ambiguity risk: if HR near 1 with p<0.05, mechanism inference is unresolvable from this data

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and these concerns from Prof. Pax actually help us sharpen the hypothesis into something much stronger. Let me work through each concern constructively.

On the mechanism: Prof. Pax is right that we need explicit causal chains. But here's the good news — we don't need to resolve the mechanism debate to make a valid prediction. The Cox model tests association, not causation. The contribution is empirical: "does this structural property at birth predict survival time?" The mechanism debate becomes the interpretation layer in the Discussion section. What we can do is pre-commit to the outcome: if HR < 1, the paper argues for the lock-in interpretation, citing Ott 2022 and Rogers; if HR > 1, the paper argues for saturation, citing Koch 2021 and the ICLR workshop framing. Both stories are supported by prior literature. This isn't post-hoc rationalization — it's acknowledging that both mechanisms are theoretically grounded and the experiment adjudicates between them.

On switching costs: Prof. Pax raises a fair point, but the GLUE→SuperGLUE transition actually *supports* our framework rather than undermining it. It happened because the community converged on the fact that GLUE was saturated — human-level performance was exceeded. That's the H2 mechanism in action. The high diversity of GLUE adoption (many teams, spanning 9 tasks, rapid broad adoption) may have accelerated the perception of saturation, triggering replacement. The point isn't that switching costs prevented replacement; it's that the diversity signal at introduction predicts the speed of that process.

The way to strengthen the hypothesis against the "direction unknown" objection is to make the bidirectional test the feature, not the bug. We frame this as: "We do not predict a priori which mechanism dominates — we test which mechanism the data supports." This honest framing is actually more scientifically defensible than cherry-picking one direction and hoping the data cooperates. It also aligns with the ICLR workshop's call for empirical investigation.

One additional strengthening: Prof. Vera's concern about control set VIF is addressable. In h-m1, the VIF explosion (task_age=22.3, log_pub_vol=22.4) was for the *time-varying* model. For a time-fixed CoxPHFitter with fewer covariates, VIF may be much lower. We should add a VIF check of the CONTROL set (not just the predictor) as part of the FAIL FAST gate.

**Key Points:**
- Bidirectional test framing is scientifically honest and stronger than directional pre-commitment without evidence
- GLUE→SuperGLUE transition pattern supports H2 (saturation) mechanism rather than undermining the hypothesis
- Add control-set VIF check to FAIL FAST gate — preempt h-m1 multicollinearity failure
- Mechanism interpretation belongs in Discussion section; Cox model tests association, mechanism is inferential

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down, and I want to be specific so we can fix it rather than just complain.

**Problem 1: The FAIL FAST gate conflates two separate validity threats.** The current gate checks partial_r²(diversity_ratio, [task_age, intro_year]) > 0.01 — this guards against time-proxy collapse. But there's a second threat that's NOT covered: whether `paper_diversity_ratio_at_intro` actually varies across the 87-task panel with enough range to detect effects. If most h-e2 benchmarks have similar diversity ratios (say, all cluster near 0.3–0.5), the Cox model will be underpowered regardless of EPV=115. I'd add a second gate: std(paper_diversity_ratio_at_intro) > 0.10 across the 87-task panel.

**Problem 2: The "time-independent by construction" claim is overstated.** `paper_diversity_ratio = unique_papers / total_rows` is a cross-sectional snapshot at the introduction year. But the introduction year itself is a function of when the benchmark was created — older benchmarks had more time to accumulate submissions before we measure the ratio. If older benchmarks systematically have lower diversity ratios (because early evaluation-tables had fewer teams submitting), the ratio is temporally confounded in a different way than raw cumulative counts, but still confounded. The partial_r² gate catches this IF the regression with temporal controls produces near-zero partial_r² — but we haven't verified empirically that this won't happen.

**Problem 3: Join key mismatch is a lurking failure mode.** Phase 1 Gap 2 explicitly flagged that `task_path` in pwc-archive may not match h-e2 panel task slugs. If <70 tasks join successfully, EPV drops from 115 to ~94 (still above 100) but the panel character changes. The solution isn't just "fuzzy matching" — it's to verify that the 87 h-e2 tasks can be recovered with >95% coverage from pwc-archive before calling this "confirmed data source."

**Problem 4: The null hypothesis test has an asymmetry problem.** If LRT p > 0.05, we declare H0. But failing to reject H0 with this method doesn't distinguish between "no effect" and "insufficient power" or "proxy mismatch." Prof. Vera's three predictions (FAIL FAST pass, LRT p<0.05, KM quartile separation) help, but we need a clean articulation of: "If both FAIL FAST gates PASS and LRT p > 0.05, we can conclude the predictor has no detectable effect conditional on this panel." That's a meaningful null.

**What would convince me this is valid:** (1) explicit FAIL FAST gate for diversity ratio variance, (2) a join coverage check (≥80% task recovery from pwc-archive), (3) pre-specified effect size threshold (|HR-1| ≥ 0.10) as minimum scientifically meaningful effect.

**Key Points:**
- Add variance gate: std(paper_diversity_ratio_at_intro) > 0.10 across panel — guards against underpowered flat predictor
- "Time-independent by construction" needs empirical verification via partial_r² gate — not just theoretical
- Join coverage check (≥80% tasks recovered) needed as explicit FAIL FAST gate before Cox
- Clean null interpretation: FAIL FAST gates pass + LRT p>0.05 = meaningful null result, not just failed attempt

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique is exactly the kind of rigor that turns a promising idea into a defensible one. NOW we're onto something! Let me build on these concerns to actually strengthen the hypothesis design.

Prof. Rex's variance gate idea is brilliant — and it points to something deeper. If `paper_diversity_ratio` has low variance across h-e2 benchmarks, it suggests the evaluation-tables record is systematically sparse for all benchmarks, not just some. In that case, the information we're after might be better captured by a *rank*-based version: the *percentile rank* of unique paper count within the same task, rather than the raw ratio. Rank-based covariates are robust to distributional skew AND more interpretable: "this benchmark was in the top quartile of diversity for its task" is a more natural statement than "this benchmark had diversity ratio 0.32."

What if we add a secondary predictor: `diversity_rank_within_task_z` — the z-standardized rank of unique_paper_count_at_intro among all benchmarks within the same parent task? This is task-normalized, time-independent, and directly captures whether the benchmark was a "diversity standout" in its competitive niche. This is genuinely novel — and it addresses Prof. Rex's concern about flat variance in the raw ratio while preserving the core hypothesis.

On the join coverage concern: the h-e1 snapshot memory shows that slug matching at 48.7% (127/152 extended whitelist) achieved 95.5% of Koch 133 core tasks using `papers-with-abstracts.tasks` field. For `evaluation-tables`, the field is `task_path` — a different format. But the diversity ratio computation only needs `paper_url` per `task_path`, which can be joined to h-e2 panel's task slugs using the same fuzzy matching approach. The 87-task h-e2 panel uses tasks already verified from h-e2 construction — it's the same slug space. So the join is not starting from scratch; it's a second join using already-validated task identifiers.

I want to propose the final hypothesis statement emerging from this discussion: **"Under the h-e2 panel (87 tasks, 345 displacement events), benchmark submitter diversity at introduction year — measured as log-transformed unique paper count and normalized diversity ratio — predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1), with effect direction (HR<1=lock-in vs HR>1=saturation) determined empirically, conditional on passing a FAIL FAST gate verifying predictor independence from temporal controls (partial_r²>0.01) and adequate variance (std>0.10)."**

**Key Points:**
- Rank-based predictor `diversity_rank_within_task_z` is more robust to distributional skew and addresses variance concern
- h-e2 task slugs are already validated — pwc-archive join reuses the same slug space
- Final hypothesis should be bidirectional with explicit FAIL FAST conditions and effect size threshold
- Two complementary predictors: raw log-count (absolute diversity) + rank within task (relative diversity)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's rank-based extension is scientifically sound and I want to formalize the complete testable prediction set now that we have enough structure.

Let me build the complete, pre-specified experimental protocol. This is what I mean by testable predictions with success/failure criteria — specific enough that a third party could verify results without knowing our intentions.

**FAIL FAST Gate (must ALL pass before Cox):**
- G0: ≥80% of h-e2 benchmarks have non-null paper_url in pwc-archive (join coverage)
- G1: partial_r²(log_unique_paper_count_z, [task_age, intro_year]) > 0.01
- G2: partial_r²(paper_diversity_ratio_z, [task_age, intro_year]) > 0.01
- G3: std(paper_diversity_ratio_at_intro) > 0.10 across joined benchmarks
- G4: VIF < 10 for all predictors in Cox model (extend beyond predictor, check controls too)

**Primary Predictions (Cox regression results):**
- P1: LRT p < 0.05 for `log_unique_paper_count_at_intro_z` → H accepted (direction by HR)
- P2: HR's 95% CI does not include 1.0 (strong effect)
- P3: Kaplan-Meier curves for Q1 vs Q4 diversity show log-rank p < 0.05

**Robustness Checks:**
- R1: Result holds when `paper_diversity_ratio_z` replaces `log_unique_paper_count_z` as primary predictor
- R2: Adding interaction term (diversity × task_age) does not flip primary HR significance
- R3: Result holds when Koch 133 core tasks only (subset of 87) are used

The minimum scientifically meaningful effect: |HR - 1| ≥ 0.10, which corresponds to at minimum 10% hazard rate difference between a 1-SD shift in diversity. This is consistent with the h-m1 failure (HR=0.871, |HR-1|=0.129 — directionally meaningful but underpowered), establishing that we CAN see effects of this magnitude with EPV=115.

The structure is now clean: Pre-specified gates → Pre-specified predictions → Pre-specified robustness → Pre-specified null interpretation. If G0-G4 all pass and P1-P3 all fail, we have a meaningful null with adequate power. If G0-G4 pass and P1 fails but P2 passes directionally, we have a marginal result worth reporting with caveats.

**Key Points:**
- 5-gate FAIL FAST protocol (G0-G4): join coverage + partial_r² × 2 + variance + VIF
- 3 primary predictions (P1-P3) with pre-specified success criteria
- 3 robustness checks (R1-R3) guard against model specification sensitivity
- Minimum effect size: |HR-1| ≥ 0.10 — calibrated from h-m1 empirical baseline

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because the 5-gate FAIL FAST protocol Prof. Vera has articulated changes the epistemological status of our result significantly. Let me explain why this is strategically important for impact.

Prior work that tested similar predictors (e.g., Koch's concentration measures, Ott's versatility measures) did not have pre-specified gate structures — they ran regressions and reported what they found. Our design has a crucial advantage: any result we report (whether HR<1, HR>1, or null) is clean because it passed a rigorous pre-validation protocol. This matters for the ICLR 2025 workshop audience who is specifically concerned about researcher degrees of freedom in benchmark analysis — we're modeling exactly the kind of pre-specified, gate-validated analysis they want to see.

The significance I see breaking through here is a methodological contribution in addition to the substantive finding. We're demonstrating how to apply survival analysis with explicit pre-registration-style gates to benchmark lifecycle research. Future researchers studying benchmark longevity can use this protocol as a template. This raises the paper above "one empirical test" to "a methodological contribution + empirical result."

The related work positioning needs to be sharp: (a) Ott et al. 2022 — cross-benchmark saturation dynamics, no survival model; (b) Koch et al. 2021 — concentration measurement methodology, no displacement prediction; (c) Paullada et al. 2021 — dataset governance framework, no quantitative survival analysis; (d) h-m1 runs 1-2 (this pipeline) — attempted Cox regression with underpowered or time-collinear predictors. We're the first to successfully combine a time-independent diversity proxy with a pre-validated survival panel at adequate EPV.

One thing I want to highlight that hasn't been discussed: the negative result space. If G0-G4 all pass and P1-P3 all fail, we have strong evidence that community breadth at introduction year does NOT predict subsequent displacement. This is genuinely informative — it rules out an entire class of community-structure predictors, leaving process-based predictors (score trajectory, methodology turnover, citation velocity) as the remaining candidates. Even a null result from Attempt 11 is a contribution, given the quality of the pre-validation.

**Key Points:**
- 5-gate FAIL FAST protocol creates pre-registration-equivalent rigor — important for ICLR workshop audience
- Methodological contribution = survival analysis template for benchmark lifecycle research, beyond just one empirical test
- Clear related work gap: first time-independent diversity proxy + pre-validated panel + EPV≥100 combination
- Strong null result is publishable: rules out community-breadth class, narrows remaining predictor space

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, this could work. But I want to stress-test the causal mechanism one more time before we finalize.

The lock-in mechanism (H1): diversity → broad stakeholder network → resistance to switching. The scientific validity depends on whether "switching" is the right conceptual model for benchmark displacement. In the h-e2 panel, "displacement" means a DIFFERENT BENCHMARK achieves plurality for the same task — not that teams stop using the original benchmark entirely. So the lock-in mechanism needs to be reframed: it's not "teams resist switching" but "teams continue submitting to the incumbent benchmark even when a challenger emerges, preventing the challenger from achieving plurality." This is plausible, but it implies a very specific behavioral mechanism: teams that adopted the incumbent early continue updating their results there rather than migrating. Is that what the evaluation-tables data would show? Possibly — but it's not the same as traditional lock-in.

The saturation mechanism (H2): diversity → widespread adoption → saturation signal → community replacement pressure. The scientific validity depends on whether there's a process linking "many teams submitted" to "researchers decide the benchmark is solved/overused." The transmission mechanism I find most plausible is: high diversity at intro → rapid SOTA progress (many teams pushing the frontier) → performance plateaus → community perceives saturation → new benchmark proposed/adopted. This would be testable in principle by checking whether high-diversity benchmarks show faster SOTA convergence (score compression) — but that requires the h-m1 score data we don't have full coverage for (34.1% coverage ceiling).

Both mechanisms are *plausible* — they're not mathematically impossible. The measurement approach is theoretically valid. The join is doable. The FAIL FAST gates are logically coherent. So feasibility is STRONG. My remaining concern is the mechanism is underdetermined, but Dr. Sage's point about this being the Discussion section's job is well-taken. We don't need to resolve mechanism to publish the empirical association.

Final feasibility assessment: **FEASIBLE — all technical barriers identified and addressable.** The `paper_url` join (Gap 1) and task_path normalization (Gap 2) are implementation details with clear solutions. The FAIL FAST gate structure is theoretically sound. CoxPHFitter(penalizer=0.1) is validated. The hypothesis is testable.

**Key Points:**
- Lock-in mechanism reframed: "teams continue submitting to incumbent" (not classical switching costs) — still plausible
- Saturation transmission mechanism: diversity → rapid SOTA progress → performance plateau → community replacement
- Full feasibility confirmed: technical barriers all identified and addressable
- Mechanism is underdetermined from this data alone — acceptable as Discussion-section interpretation

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've now passed the critical threshold. The hypothesis has been pressure-tested across novelty, falsifiability, significance, and feasibility. Let me consolidate what we've built and propose the final hypothesis formulation.

**Core Hypothesis Statement (Attempt 11):**

Under the h-e2 panel (87 tasks, 345 plurality-benchmark displacement events, 2015–2023, Papers With Code), if `log_unique_paper_count_at_intro_z` (log-transformed, z-standardized count of distinct `paper_url` values per benchmark through plurality-introduction year in pwc-archive/evaluation-tables) has partial_r² > 0.01 after partialing out task_age and benchmark_introduction_year (FAIL FAST gate), then it significantly predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1), with |HR−1| ≥ 0.10 and LRT p < 0.05, and the direction (HR<1 = community lock-in; HR>1 = saturation pressure) is determined empirically rather than pre-committed.

**Why this works:**
- `unique_paper_count_at_intro` is computable via pure groupby+nunique on `paper_url` — no score data needed, targeting 100% h-e2 coverage
- `paper_diversity_ratio_at_intro = unique_count / total_rows` is the time-independent secondary predictor that guards against raw count's residual temporal drift
- 5-gate FAIL FAST protocol (G0-G4) prevents repeating h-e1/h-m1 failure modes
- Bidirectional alternative hypothesis avoids HARKing while preserving scientific honesty
- Minimum effect threshold (|HR-1| ≥ 0.10) calibrated from h-m1 empirical baseline

**Mechanism claims (for Discussion section):**
- If HR<1: Ott 2022 lock-in narrative (breadth → longevity via stakeholder network effects)
- If HR>1: Koch 2021 / ICLR workshop saturation narrative (diversity → overuse → community replacement pressure)
- If null: Rules out community-breadth class of predictors; opens space for process-based predictors

The remaining concern from Prof. Rex was the join coverage. This is addressed by Gate G0 (≥80% benchmarks with non-null paper_url). If G0 fails, we route to Attempt 12. This makes the experiment self-terminating at the data-validation stage, which is exactly what we need.

**Key Points:**
- Final hypothesis: bidirectional Cox test with 5-gate FAIL FAST protocol + |HR-1|≥0.10 minimum effect threshold
- Two predictors: `log_unique_paper_count_at_intro_z` (primary) + `paper_diversity_ratio_at_intro_z` (secondary, time-independent by construction)
- Both mechanism interpretations (lock-in / saturation) are literature-grounded; direction determined by data
- Route to Attempt 12 trigger: ANY FAIL FAST gate fails after join coverage check

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

What would convince me this is valid — you've addressed my main concerns. Let me acknowledge the improvements and raise my two final concerns before I'm satisfied.

**Concern 1: The bidirectional test still needs a registered interpretation protocol.** Dr. Ally's formulation says "direction determined empirically." But what if HR=0.92 (slightly below 1.0) with LRT p=0.03? Is that H1 (lock-in)? The paper would argue yes. But what if HR=0.92 is the true effect and we designed the analysis with H2 in mind internally? The solution is to explicitly pre-specify: "If HR < 1.0 and LRT p < 0.05, the paper argues for the lock-in interpretation. If HR > 1.0 and LRT p < 0.05, the paper argues for saturation. If LRT p > 0.05, the paper reports a null conditional on passing all FAIL FAST gates." This explicit interpretation protocol needs to be in the pre-analysis plan, not just the Discussion section.

**Concern 2: The `paper_diversity_ratio` secondary predictor may not add independent information if it's a monotone function of `log_unique_paper_count_z` in this dataset.** If every benchmark in the h-e2 panel has a total_rows count that's roughly proportional to unique_paper_count (because most evaluation-table rows have unique paper_url values), then diversity_ratio ≈ constant, and the two predictors collapse into one. This isn't a fatal flaw — it would just mean we report one predictor rather than two. But it should be declared in advance: "If Pearson r(log_unique_count_z, diversity_ratio_z) > 0.95, we use only the primary predictor."

Both of these concerns are addressable by adding two lines to the pre-analysis protocol. When those additions are made, I can confirm: **the hypothesis is ready for Phase 2B**. The design is clean, the gates are logically sound, the null interpretation is meaningful, and the related work gap is genuine. Now you've addressed my concerns — pending the two protocol additions above.

**Key Points:**
- Add explicit direction-interpretation protocol to pre-analysis plan: HR<1→lock-in, HR>1→saturation, p>0.05→null
- Add predictor collinearity check: if r(log_count_z, diversity_ratio_z) > 0.95, use primary predictor only
- Both concerns are protocol additions (two lines), not fundamental redesigns — hypothesis is structurally sound
- Conditional approval: when these two protocol additions are made, hypothesis is Phase 2B ready

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, those two protocol additions are spot-on and easy to add. Let me also note something exciting that emerged from this discussion that we haven't fully articulated: the **design pattern** we've developed here is itself publishable.

We've created a template for **pre-validated survival analysis of benchmark lifecycle events** with the following structure:
1. Data source validation (join coverage gate: G0)
2. Predictor validity gates (partial_r² + variance gates: G1-G3)
3. Model specification guard (VIF gate: G4)
4. Bidirectional alternative hypothesis with explicit direction-interpretation protocol
5. Minimum effect size threshold calibrated from prior empirical failures
6. Robustness checks (R1-R3)

This is the methodological skeleton that future benchmark lifecycle studies can use. Whether our empirical result is HR<1, HR>1, or null, we've demonstrated how to run a *credible* benchmark lifecycle analysis. The paper should explicitly position this template as a contribution, not just the empirical finding.

The imagination breakthrough I want to highlight: `paper_diversity_ratio = unique_papers / total_rows` is structurally similar to an inverse Herfindahl-Hirschman Index (inverse HHI) in competition economics — low HHI (high diversity) indicates a competitive market with many players. In economics, low HHI markets tend to be more stable (many players → no single dominant force → gradual change). If our H1 (lock-in, HR<1) hypothesis holds, it would suggest that benchmark "markets" follow the economic stability-diversity pattern — a satisfying theoretical analogy. If H2 holds instead, benchmark markets are inverted relative to product markets: more competitive → faster turnover. Either finding is theoretically interesting.

NOW we're onto something for real. The hypothesis is ready. Let's proceed to Final Assessments.

**Key Points:**
- Two protocol additions from Prof. Rex: (1) direction-interpretation protocol, (2) predictor collinearity failsafe — both incorporated
- Template design pattern is a methodological contribution: pre-validated survival analysis protocol for benchmark lifecycle events
- Inverse HHI analogy: low HHI (high diversity) = competitive market; test whether benchmark markets follow economic stability-diversity pattern
- Hypothesis is CONVERGED — ready for Final Assessments

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

I concur with Dr. Nova's assessment. The convergence criteria have been met. Let me verify each:

- [x] **SPECIFIC**: Core claim stated — `log_unique_paper_count_at_intro_z` predicts displacement hazard in CoxPHFitter on h-e2 panel with |HR-1|≥0.10 and LRT p<0.05
- [x] **MECHANISM**: Causal chain explained — two competing mechanisms (lock-in vs saturation) with explicit interpretation protocol
- [x] **PREDICTIONS**: P1 (LRT p<0.05), P2 (HR CI excludes 1.0), P3 (KM Q1 vs Q4 log-rank p<0.05) — all pre-specified
- [x] **NOVELTY**: First Cox test of diversity predictor on Papers With Code displacement events; first pre-validated protocol
- [x] **FEASIBILITY**: Technical — data pipeline confirmed, CoxPHFitter validated, FAIL FAST gates theoretically sound; all barriers addressable
- [x] **OBJECTIONS**: Addressed — time-proxy (FAIL FAST gate), variance (G3 gate), join coverage (G0 gate), HARKing (bidirectional protocol), predictor collinearity (r>0.95 failsafe), mechanism underdetermination (Discussion section job)

The evidence meets my standards. Proceeding to Final Assessments.

**Key Points:**
- All 6 convergence criteria verified — discussion has converged
- Final protocol includes: 5-gate FAIL FAST + 3 predictions + 3 robustness checks + direction-interpretation protocol + collinearity failsafe
- This meets scientific standards for Phase 2B planning

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Creative Novelty Explorer):
- **Verdict:** STRONG
- **Assessment:** The diversity-as-displacement-predictor framing is genuinely novel — no prior study has tested a community-structure predictor in a pre-validated Cox survival framework on Papers With Code. The bidirectional test (lock-in vs saturation) creates an elegant scientific story regardless of empirical direction, and the inverse HHI analogy provides a compelling theoretical anchor. The design template contribution elevates this above a single empirical test.

🔬 **Prof. Vera** (Rigorous Validation Architect):
- **Verdict:** STRONG
- **Assessment:** The 5-gate FAIL FAST protocol (G0-G4) creates pre-registration-equivalent rigor that guards against all known failure modes from prior 10 attempts. The three primary predictions (P1-P3) with explicit success criteria, combined with the direction-interpretation protocol and predictor collinearity failsafe, make this hypothesis fully falsifiable. This meets scientific standards for publication.

🎯 **Dr. Sage** (Research Impact Evaluator):
- **Verdict:** STRONG
- **Assessment:** The ICLR 2025 workshop timing is ideal, the methodological template contribution raises impact beyond one empirical test, and the clean null result interpretability (if G0-G4 pass and P1-P3 fail) makes even a null result publishable. The direct comparison to Koch 2021, Ott 2022, and Paullada 2021 is well-positioned.

⚙️ **Prof. Pax** (Feasibility & Reality Checker):
- **Verdict:** STRONG
- **Assessment:** Data pipeline is technically sound, CoxPHFitter(penalizer=0.1) is validated through 14/14 tests on h-e2 panel, and FAIL FAST gates are logically coherent. The `paper_url` join and task_path normalization are the only unverified implementation details, and G0 gate handles both. Mechanism is plausible under either direction; no fundamental scientific barriers remain.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Under the h-e2 panel (87 tasks, 345 displacement events, 2015–2023, Papers With Code), benchmark submitter diversity at introduction year — operationalized as `log_unique_paper_count_at_intro_z` (log-transformed z-standardized count of distinct paper_url values through plurality-introduction year from pwc-archive/evaluation-tables) and the secondary time-independent predictor `paper_diversity_ratio_at_intro_z` (unique count / total evaluation-table rows) — significantly predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1) with |HR−1| ≥ 0.10 and LRT p < 0.05, conditional on passing a 5-gate FAIL FAST protocol (G0: ≥80% join coverage; G1-G2: partial_r²>0.01 independence from temporal controls; G3: std(diversity_ratio)>0.10; G4: VIF<10), with effect direction (HR<1 = community lock-in via stakeholder network effects / Ott 2022; HR>1 = saturation pressure via overuse signal / Koch 2021) determined empirically by the data rather than pre-committed.**

The three primary predictions are: P1 — LRT p < 0.05 for the primary predictor; P2 — 95% CI of HR does not contain 1.0; P3 — KM curves for Q1 vs Q4 diversity show log-rank p < 0.05. Three robustness checks (R1: diversity_ratio as primary predictor; R2: interaction diversity × task_age; R3: Koch 133 core subset) complete the validation protocol.

This hypothesis is novel because no prior study has tested community-structure diversity as a time-independent Cox predictor of individual benchmark displacement events on Papers With Code, distinguishing it from Ott 2022 (cross-benchmark saturation, no survival model), Koch 2021 (concentration methodology, no displacement prediction), and h-m1 runs 1-2 (time-collinear or underpowered predictors). The methodological template (5-gate FAIL FAST + bidirectional protocol + pre-specified effect threshold) is itself a contribution.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Paper_url join coverage (G0 gate) is unverified until runtime — implementation must check this FIRST before any Cox analysis
- Mechanism interpretation remains underdetermined by Cox output alone — paper must be careful not to overclaim causal mechanism from associational analysis
- If r(log_count_z, diversity_ratio_z) > 0.95, the secondary predictor provides no independent information; must pre-specify this collapse condition
- **Mitigation Strategy:** G0 gate as hard stop before any downstream computation; explicit "association not causation" language in Discussion; predictor collinearity check before model specification

