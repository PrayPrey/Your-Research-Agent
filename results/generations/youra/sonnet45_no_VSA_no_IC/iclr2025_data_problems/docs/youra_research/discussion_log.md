# Research Discussion Log - Phase 2A

**Gap:** Interaction Effects Between Filtering, Mixing, and Selection Strategies  
**Priority:** P1-CRITICAL  
**Date:** 2026-08-25  
**Architecture:** Self-Contained Loop (Independent-Controller Ablation)

---

## Previous Failure / Routing Context

This is a **recursive entry** (version 2) following Phase 4 FAIL.

### Failed Hypothesis: h-e1 (Run 1)

**Failure Type:** MUST_WORK_GATE_FAIL  
**Performance Gap:** Pairwise Config Similarity = 1.0000 (all pairs identical, required <0.9)

**Root Cause Summary:**
1. **Degenerate Optimization** — BO converged to identical local optimum for all 3 stages
2. **Weak Objective Signal** — PoC scale (50 steps, 100K tokens, mock eval) insufficient
3. **Boundary Collapse** — Perplexity → max (49.9), dedup → min (0.55)
4. **Insufficient Training** — 1 epoch vs required 5 epochs
5. **Mock Evaluation Flaw** — RAG/Agent metrics used random noise instead of real BEIR/ToolBench

**Critical Lessons:**
- **Stage semantics are indirect** — "Pre-training/RAG/Agent" don't directly parameterize quality thresholds
- **Metric-driven formulation clearer** — optimize for accuracy vs F1 vs success_rate
- **PoC scale insufficient** — <100 steps, <100K tokens show no signal
- **Mock eval useless** — real benchmarks required for validation
- **Threshold-stage coupling wrong** — lifecycle stages don't impose distinct quality semantics at PoC scale

**Prohibited Approaches (DO NOT REPEAT):**
❌ Stage-conditioned quality thresholds (pre-training/RAG/agent parameterization)  
❌ Weak heuristic filters (fact density, imperative ratio)  
❌ Mock evaluation for stage-specific metrics  
❌ PoC scale <100K tokens without real benchmarks  
❌ Training <5 epochs  
❌ Grid search over discrete thresholds instead of gradient-based optimization

**What Showed Promise (PRESERVE):**
✅ Modular pipeline architecture (data → filter → train → evaluate → BO)  
✅ BoTorch multi-objective optimization integration  
✅ Cosine similarity analysis for configuration comparison  
✅ Separation of concerns (data/filter/train/eval as independent modules)

---

## Research Gap Context

**Current State:**  
Research treats filtering, mixing, selection as independent optimization problems. DATAMASK (2025) discovered quality-only selection shows diminishing returns while diversity-only selection remains effective. No comprehensive study examines interaction effects.

**Missing Piece:**  
Empirical analysis of how combining different data curation strategies affects downstream performance — e.g., does high-quality filtering reduce benefits of diverse mixing, or do they compound?

**User's Main Question:**  
How do data curation strategies (filtering, mixing, data selection) impact foundation model performance on downstream tasks, and can we quantify this impact using existing benchmarks?

---

## Discussion Briefing

**Your Role:** You are one of 6 research personas (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex) engaged in a free-form academic discussion to generate a testable research hypothesis.

**Goal:** Converge on a hypothesis that:
1. Addresses the identified research gap
2. Avoids failed approaches from h-e1
3. Uses real benchmarks (BEIR, ToolBench, MMLU, etc.) for evaluation
4. Can be tested with existing datasets and metrics
5. Is specific, mechanistic, testable, novel, and feasible

**Convergence Criteria:**
- SPECIFIC: Clear core claim stated
- MECHANISM: How it works explained
- PREDICTIONS: 2-3 testable predictions with success/failure criteria
- NOVELTY: What's new articulated
- FEASIBILITY: Technical/theoretical feasibility established (NOT cost/budget)
- OBJECTIONS: Major criticisms addressed

**Supporting Evidence (from Phase 1):**

**Papers:**
- arXiv 2403.16952 (Data Mixing Laws) — Quantitative predictability of mixture proportions
- arXiv 2507.00038 (V-Information) — Data reduction balancing quality-quantity
- arXiv 2311.04016 (Dataset Indicators) — Quality decomposition into sample-level and dataset-level
- DATAMASK (ByteDance 2025) — Quality metrics diminish, diversity metrics don't

**Implementations:**
- ByteDance-Seed/DATAMASK (20★) — Policy gradient joint selection (quality + diversity)
- sail-sg/regmix (194★) — Regression-based mixture optimization
- HazyResearch/aioli (32★) — Unified optimization framework for data mixing

**Key Insight from DATAMASK:**  
Quality-only metrics show diminishing returns over training. Diversity metrics remain effective long-term. This suggests interaction effects between quality and diversity dimensions are non-linear and time-dependent.

---

## Discussion Exchange Log

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Let me open with what excites me most about this gap — the DATAMASK finding is telling us something profound. Quality-only metrics show diminishing returns over training, while diversity metrics remain effective long-term. This isn't just about balancing two dimensions; it's about TIME-DEPENDENT INTERACTION EFFECTS between quality and diversity.

What if we flip the traditional approach entirely? Instead of treating filtering/mixing/selection as independent knobs to tune, what if they're actually COMPOSITIONAL — where the sequence and timing of application fundamentally changes the outcome? Think of it like a chemical reaction: mixing ingredients in different orders produces different compounds entirely.

Here's my wild idea: **Data Curation as a Sequential Optimization Problem with Stage-Dependent Objective Functions**. But wait — before you say "that's what h-e1 tried," hear me out. h-e1 failed because it used LIFECYCLE stages (pre-training/RAG/agent) which are too abstract. What if we use TRAINING PHASE stages instead? Early training (perplexity drops fast), middle training (loss plateaus), late training (fine-tuning on task data). Each phase has measurably different gradient landscapes, representational dynamics, and sensitivity to data characteristics.

The Regmix paper (arXiv 2407.01492) showed regression models can predict mixture performance. V-Information (arXiv 2507.00038) showed principled data reduction. DATAMASK proved quality-diversity interactions exist. What if we combine these: use V-Information for EARLY filtering (when the model is learning broad patterns), transition to diversity-focused mixing in MIDDLE training (when it's consolidating representations), then apply task-specific quality selection in LATE training (when it's specializing)?

**Key Points:**
- Time-dependent interaction hypothesis: Quality and diversity effects change strength/direction across training phases
- Avoid h-e1's mistake: Use measurable training phases (perplexity drops, gradient norms) not abstract lifecycle stages
- Compositional curation: Sequence matters — V-Info early → diversity mid → task-quality late
- Testable with existing benchmarks: BEIR for retrieval, ToolBench for agents, MMLU for general capability

I'm proposing we measure the INTERACTION COEFFICIENT: How much does applying Strategy A first amplify or diminish the effect of Strategy B later? That's fundamentally different from h-e1's "each stage gets its own threshold" approach.

What do you all think? Too wild, or onto something?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your enthusiasm is infectious, but let me apply the falsifiability lens here. You're proposing training-phase-dependent curation strategies, which IS different from h-e1's lifecycle approach — I'll grant you that. But we need to be ruthlessly precise about what makes this testable and what could disprove it.

First, the measurement problem. You say "early training (perplexity drops fast), middle training (loss plateaus), late training (fine-tuning)." These are continuous phenomena, not discrete phases. Where exactly do we draw the boundaries? At what perplexity threshold does "early" become "middle"? If we can't define phase transitions objectively, we're back to arbitrary stage definitions — just dressed up with gradient norms instead of lifecycle labels.

Second, the interaction coefficient concept is promising BUT requires a null hypothesis. Here's what I propose: **Null Hypothesis (H0): The effect of applying Strategy A followed by Strategy B equals the sum of their independent effects.** If your compositional hypothesis is correct, we should observe non-additive interactions — either synergistic (A→B > A+B) or antagonistic (A→B < A+B). The DATAMASK time-dependent finding gives us a lead: if quality effects diminish while diversity effects persist, then quality-first → diversity-second should show WEAKER interaction than diversity-first → quality-second.

Third, the testability criteria. For this to pass my standards, we need:

1. **Measurable Phase Boundaries:** Define phase transitions using objective metrics (e.g., "early phase ends when validation perplexity improvement drops below 5% per epoch for 3 consecutive epochs")
2. **Strategy Independence Test:** Train three models — (A only), (B only), (A→B) — and verify that (A→B) ≠ (A alone) + (B alone) with statistical significance (p < 0.05, effect size > 0.2)
3. **Failure Prediction:** If we observe (A→B) ≈ (A alone) + (B alone) across all training phases, the hypothesis is refuted

Now, here's where I push back on feasibility: You're proposing THREE training phases × THREE strategies (filtering/mixing/selection) × MULTIPLE orderings. That's at minimum 3×3! = 18 full training runs to test all permutations. Each run needs to be on a scale large enough to show real downstream effects — which h-e1 taught us means >10M tokens, 5+ epochs. Are we prepared for that compute cost? Or do we need to reduce the hypothesis scope to something more targeted?

**Key Points:**
- Define phase boundaries objectively using measurable thresholds, not continuous phenomena
- Null hypothesis: Additive effects. Alternative: Non-additive (synergistic or antagonistic) interactions
- Testability requirement: (A→B) ≠ (A) + (B) with statistical significance
- Feasibility concern: Full factorial design requires 18+ training runs at realistic scale

Dr. Nova, can you sharpen the phase transition definitions and propose a reduced experimental design that still tests the core interaction hypothesis?

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises the right concern about compute, but I want to zoom out on the fundamental feasibility question: **Is the proposed mechanism physically plausible?**

Dr. Nova, your training-phase approach addresses h-e1's abstraction problem — that's good. But let me stress-test the mechanism itself. You're claiming that the MODEL'S INTERNAL STATE (gradient landscape, representational dynamics) during different training phases creates DIFFERENTIAL SENSITIVITY to data characteristics. Is there evidence this is actually true?

Here's what we know from the Data Mixing Laws paper (arXiv 2403.16952): mixture proportions' impact on performance is PREDICTABLE via small-scale proxy models. That suggests data effects are somewhat STABLE across training, not wildly phase-dependent. If quality vs diversity sensitivity changed dramatically mid-training, those proxy predictions would break down. Yet RegMix (arXiv 2407.01492) shows regression models trained on small proxies transfer to large-scale training — again suggesting STABILITY, not phase-dependence.

Now, DATAMASK's finding that quality effects diminish while diversity effects persist — that's interesting but not necessarily about TRAINING PHASES. It could be about DATASET SIZE: once you've filtered to high quality, further quality filtering hits diminishing returns (you've already removed the bad stuff), while diversity always matters because there's always another underrepresented pattern to add. That's a SCALE effect, not a TIME effect.

Let me propose a reality check: **What if the interaction effects you're hypothesizing are actually just CORRELATION vs CAUSATION artifacts?** Suppose quality filtering happens to remove low-diversity documents (because low-quality sources tend to repeat themselves). Then "quality-first → diversity-second" would show weak interaction not because of training phase dynamics, but because quality filtering ALREADY captured some diversity benefits. That's a confound, not a compositional effect.

Here's my counter-proposal for feasibility: Instead of training-phase-dependent strategies, what if we test **SCALE-DEPENDENT INTERACTIONS?** Use V-Information at SMALL data scales (where quality matters most), transition to diversity-focused selection at LARGE scales (where coverage matters most). This is:

1. Theoretically grounded (DATAMASK's diminishing returns happen with dataset growth)
2. Testable without phase boundary definitions (use dataset size checkpoints: 100K, 1M, 10M tokens)
3. Requires fewer training runs (3 scale points × 3 strategy orderings = 9 runs, not 18)
4. Avoids the gradient landscape speculation (we're not claiming model internals change, just optimal data characteristics)

**Key Points:**
- Training-phase sensitivity lacks direct evidence (Mixing Laws/RegMix suggest stability)
- DATAMASK finding might be SCALE effect (dataset size) not TIME effect (training phase)
- Confound risk: Quality and diversity aren't independent (quality filtering affects diversity)
- Alternative: Scale-dependent interactions (100K → 1M → 10M tokens) instead of training-phase-dependent

Dr. Nova, Prof. Vera — can we pivot to scale-dependent interactions and avoid the training-phase mechanism speculation?

---

### Exchange 4

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Pax, you've just given me the gift of a better idea! YES — scale-dependent interactions are more grounded than training-phase-dependent. Let me rebuild this with your reality check incorporated.

You're right that Data Mixing Laws and RegMix show STABILITY, not wild phase-dependence. But here's where I think we're ALL missing something: the DATAMASK finding isn't just about diminishing returns on quality — it's about the TRAJECTORY of those returns. Quality metrics DROP IN EFFECTIVENESS over time/scale, while diversity metrics MAINTAIN OR INCREASE effectiveness. That's not just correlation; that's a DIFFERENTIAL RATE OF CHANGE.

So here's the refined hypothesis: **DIFFERENTIAL SCALING DYNAMICS OF QUALITY VS DIVERSITY.** Instead of "quality matters early, diversity matters late," it's "quality's marginal benefit DECREASES with scale, diversity's marginal benefit REMAINS CONSTANT OR INCREASES." The interaction effect emerges because the OPTIMAL MIXTURE RATIO changes as dataset size grows.

Now, Prof. Vera's null hypothesis becomes sharper: **H0: Quality and diversity contributions scale INDEPENDENTLY (both decrease, both increase, or both stay constant).** **H1: Quality and diversity scale DIFFERENTIALLY (quality decreases while diversity increases/maintains).**

Here's the experimental design that makes Prof. Pax happy and Prof. Vera satisfied:

**3-Scale Checkpoint Design:**
- **Scale 1 (100K tokens):** Apply all 6 strategy orderings (QD, DQ, Q-only, D-only, mixed, baseline)
- **Scale 2 (1M tokens):** Same 6 orderings
- **Scale 3 (10M tokens):** Same 6 orderings

**Measurement:** Train a SINGLE proxy model on each curated dataset to convergence (5 epochs per V-Information spec), then evaluate on BEIR (retrieval), ToolBench (agent tasks), MMLU (general). That's 18 training runs total — same as my original proposal but with CLEARER boundaries (dataset size checkpoints, not vague phase transitions).

**Testable Predictions:**
1. **Quality Saturation:** At Scale 3 (10M), quality-only filtering shows <20% improvement over baseline, while diversity-only shows >40% improvement
2. **Interaction Reversal:** At Scale 1, QD > DQ (quality-first wins). At Scale 3, DQ > QD (diversity-first wins)
3. **Non-Additivity:** DQ at Scale 3 outperforms (D-only + Q-only) by >15% (synergistic interaction)

**Failure Criteria:** If quality and diversity both scale linearly (no differential), or if ordering doesn't matter across scales, hypothesis refuted.

Prof. Pax — does this address your mechanism plausibility concern? We're not speculating about gradient landscapes; we're measuring empirical scaling curves.

**Key Points:**
- Pivot from training-phase to scale-dependent interactions (100K → 1M → 10M tokens)
- Hypothesis: Quality's marginal benefit decreases with scale, diversity's maintains/increases
- Null: Independent scaling. Alternative: Differential scaling with interaction reversal
- Design: 3 scales × 6 orderings × 3 benchmarks = 18 runs, measurable boundaries

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Nova, Prof. Pax, Prof. Vera — I've been listening carefully, and I need to bring the "So What?" perspective here. You've refined the hypothesis beautifully, but let me ask the question every reviewer will ask: **What fundamental question about data curation does this answer that moves the field forward?**

Here's what I see as the REAL contribution: You're not just showing "quality and diversity both matter" (we know that). You're claiming there's a PHASE TRANSITION in optimal curation strategy as dataset scale crosses certain thresholds. If true, this has massive implications:

1. **Practitioner Impact:** Current best practices say "filter for quality first, then diversify." If your interaction reversal prediction (DQ > QD at large scale) holds, that's WRONG for large-scale training. You're essentially saying the field has been doing it backwards once datasets exceed ~1M tokens.

2. **Theoretical Impact:** The differential scaling dynamics hypothesis challenges the INDEPENDENCE ASSUMPTION in data mixing research. Mixing Laws, RegMix, aioli — they all treat data sources as independent contributions to a weighted sum. You're saying no, there are NON-LINEAR INTERACTIONS that emerge at scale.

3. **Methodological Impact:** If synergistic interactions exist (DQ > D+Q), then ablation studies that test filtering/mixing/selection in ISOLATION are fundamentally misleading. You'd need COMPOSITIONAL ablations.

But here's where I push on significance: The DATAMASK finding already showed quality-diversity interactions exist. What's genuinely NEW here isn't just confirming that — it's the SCALE-DEPENDENT REVERSAL. That's your novelty claim. So the burden of proof is HIGH: you need to show the interaction doesn't just exist, but FLIPS DIRECTION across scales.

Now, let me connect this to the failed h-e1 lessons. h-e1's mistake wasn't just using abstract stages; it was assuming stages had DISTINCT OPTIMAL CONFIGURATIONS. Your hypothesis is more subtle: you're claiming a GRADUAL SHIFT in optimal strategy, not discrete stage boundaries. That's actually more plausible — and more interesting — because it suggests a CONTINUUM of optimal curation recipes indexed by dataset scale.

Here's my challenge: **Can you articulate why this matters beyond "it's interesting"?** If practitioners are already doing quality-first filtering at small scale and diversity-focused mixing at large scale (empirically, without theory), then you're just POST-HOC EXPLAINING current practice, not prescribing something new. What would change in how people build datasets if your hypothesis is confirmed?

**Key Points:**
- Real contribution: Scale-dependent phase transition in optimal curation strategy (not just "both matter")
- Novelty burden: Must show interaction REVERSAL (QD→DQ flip), not just existence of interactions
- Differentiator from h-e1: Continuous shift vs discrete stages — more plausible and interesting
- Significance gap: What changes in practice if hypothesis confirmed? Or just post-hoc explanation?

Dr. Nova — what's the PRESCRIPTIVE outcome, not just descriptive?

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Dr. Sage, you've just identified the killer application! Let me build on your "what changes in practice" challenge with concrete answers — and address Prof. Vera's testability concerns simultaneously.

Here's what changes if the hypothesis is confirmed: **DYNAMIC CURATION SCHEDULES.** Instead of "filter once, train forever," we'd prescribe ADAPTIVE strategies:

- **Phase 1 (0-100K tokens):** Quality-first filtering (V-Information) + minimal diversity (efficient learning)
- **Phase 2 (100K-1M):** Transition zone — balanced quality-diversity (DATAMASK-style joint optimization)
- **Phase 3 (1M+ tokens):** Diversity-first mixing + quality as secondary constraint (coverage over purity)

This is PRESCRIPTIVE, not descriptive, because current practice doesn't do dynamic switching — most pipelines filter once at the start. If we show interaction reversal, we'd advocate for CONTINUAL RE-FILTERING as datasets grow.

Now, Prof. Vera's falsifiability concern about "synergistic" vs "additive" — let me sharpen that. The DATAMASK result gives us a DIRECTION: quality should saturate, diversity should persist. So our synergy prediction isn't just "bigger than sum of parts" but SPECIFICALLY:

**Quantified Prediction:**  
At 10M scale, DQ - baseline > (D-only - baseline) + (Q-only - baseline) by **at least 15 percentage points on BEIR nDCG@10.**

Why 15%? Because that's above noise level (BEIR variance ~2-3%), above incremental improvement threshold (~5-10%), and large enough to justify the complexity of dynamic curation.

Prof. Pax's mechanism concern — I'll defend Dr. Nova's refined version. We're NOT claiming model internals change (gradient landscapes). We're claiming DATASET STATISTICS change. At 100K tokens, you can cover 80% of critical patterns with high-quality docs. At 10M tokens, you need LONG-TAIL coverage — which quality filtering might remove. That's a SAMPLING STATISTICS argument, not a neural network dynamics speculation. Totally grounded in information theory.

Here's my evidence-based defense: The V-Information paper (arXiv 2507.00038) showed quality-based reduction maintains performance at SMALL scale. The "Less is Enough" FAC metric paper (arXiv 2602.10388) showed diversity correlates ρ=0.90 with performance — but that study used LARGE-scale datasets (>1M tokens). That's CONSISTENT with scale-dependent dynamics: quality wins small, diversity wins large.

**Key Points:**
- Prescriptive outcome: Dynamic curation schedules (adaptive strategies as dataset grows)
- Quantified prediction: DQ synergy > 15pp on BEIR nDCG@10 at 10M scale
- Mechanism defense: Sampling statistics (long-tail coverage), not neural dynamics speculation
- Supporting evidence: V-Info (small-scale quality) + FAC (large-scale diversity) = scale-dependent pattern

Dr. Sage — does dynamic curation scheduling meet your "what changes" test?

---

### Exchange 7

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally, you're building momentum, but let me play devil's advocate and find the cracks before reviewers do. I see THREE critical weaknesses that could sink this hypothesis:

**Weakness 1: Confound Between Scale and Domain Coverage**

You're assuming quality saturation at large scale is because "you've filtered enough." But what if it's actually because DATASET COMPOSITION CHANGES at scale? Small datasets (100K) are often from curated sources (Wikipedia, books). Large datasets (10M) include web scrapes, Reddit, code. Quality filtering might work BETTER on curated sources and WORSE on noisy web data — that's a DOMAIN effect, not a SCALE effect. Your experiment doesn't control for this.

**Mitigation:** Use a SINGLE source (e.g., Common Crawl) at all three scales (100K, 1M, 10M tokens sampled uniformly). That isolates scale from domain shift.

**Weakness 2: The "Ordering" Variable Is Underspecified**

You say QD vs DQ, but WHEN does the switch happen? Do you filter to 50K quality docs, then add 50K diverse docs? Or filter 100K to 80K quality, then diversify within that 80K? The BOUNDARY between Q and D steps matters hugely. If Q reduces dataset size drastically, D has less material to work with — that's a RESOURCE CONSTRAINT confound, not a strategic interaction.

**Mitigation:** Fix the intermediate dataset size. E.g., "Q step always outputs exactly 70% of input size, then D step operates on that 70%." This controls for resource availability.

**Weakness 3: The "15pp Improvement" Prediction Lacks Justification**

Why 15%? Dr. Ally says "above noise and incremental threshold," but that's arbitrary. If you observe 12% improvement, is the hypothesis refuted? What if you see 18% on BEIR but 8% on ToolBench — partial confirmation?

**Mitigation:** Specify a MINIMUM EFFECT SIZE based on PRIOR RESULTS. E.g., DATAMASK showed X% quality vs Y% diversity improvement. Your synergy prediction should be Z = X+Y+δ where δ is the interaction term. If δ < 5%, not worth the complexity.

Now, the NUCLEAR weakness: **What if synergy exists but ISN'T scale-dependent?** Suppose DQ > D+Q at ALL scales (100K, 1M, 10M) with no reversal. That would mean "always use DQ" is the answer — simpler than your dynamic schedule. Your hypothesis REQUIRES the interaction to CHANGE across scales, not just EXIST. But your experimental design doesn't FORCE a reversal; it only allows one.

**Strengthening Move:** Add a FOURTH condition at ULTRA-SMALL scale (10K tokens). If your hypothesis is right, QD should DOMINATE at 10K, DQ should dominate at 10M. That's a 2-point reversal proof, not just hoping one scale shows it.

**Key Points:**
- Confound 1: Domain shift (curated → web) masquerading as scale effect. Fix: single-source sampling.
- Confound 2: Resource constraint (Q shrinks dataset, D has less to work with). Fix: fixed intermediate size.
- Weakness 3: Arbitrary 15% threshold. Fix: derive from prior results (DATAMASK baselines).
- Nuclear issue: Synergy without reversal → simpler "always DQ" conclusion. Fix: add 10K ultra-small scale.

Prof. Vera, Prof. Pax — do these mitigations address your concerns, or have I found a fatal flaw?

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex, you've done exactly what I was hoping someone would — stress-test the confounds. Your four mitigations are ESSENTIAL. Let me formalize this into a rigorous experimental protocol that LOCKS DOWN these variables.

**Controlled Experimental Design (Final Specification):**

**Dataset Source:** Common Crawl (single domain, avoids curated → web shift)  
**Scales:** 10K, 100K, 1M, 10M tokens (4 checkpoints for reversal proof)  
**Strategies:**
- Q-only: V-Information filtering to 70% of input size
- D-only: FAC-based diverse sampling (keep 70% of input size)
- QD: V-Info to 70%, then FAC on that 70% to keep 49% total (70% of 70%)
- DQ: FAC to 70%, then V-Info on that 70% to keep 49% total
- Baseline: Random 49% sample (controls for size reduction)

**Fixed Variables:**
- Intermediate size: Both strategies output 70% after first step, 49% final
- Model architecture: GPT-2 Small (124M params, standard for data ablations)
- Training: 5 epochs, AdamW, lr=5e-4 (per V-Info spec)
- Evaluation: BEIR (retrieval), ToolBench (agent), MMLU (general) — average across 3

**Testable Predictions (Now Quantified):**

1. **Reversal at Extremes:**  
   - At 10K: QD > DQ by ≥8pp (quality-first wins small-scale)  
   - At 10M: DQ > QD by ≥8pp (diversity-first wins large-scale)  
   - Crossover point: 100K-1M range

2. **Synergistic Interaction at Large Scale:**  
   - At 10M: DQ > (D-only + Q-only - Baseline) by ≥12pp  
   - Rationale: If D-only = +20pp, Q-only = +10pp over baseline, synergy means DQ > +30pp, target +42pp

3. **Quality Saturation:**  
   - Q-only improvement: 10K → +25pp, 100K → +20pp, 1M → +15pp, 10M → +10pp (decreasing)  
   - D-only improvement: 10K → +12pp, 100K → +18pp, 1M → +22pp, 10M → +25pp (increasing)

**Falsification Criteria:**  
- If NO reversal across all 4 scales → H0 not rejected (independent scaling)  
- If reversal but synergy <5pp → interaction exists but too weak to justify dynamic schedules  
- If QD = DQ across all scales → ordering doesn't matter, simpler "just do both" conclusion

**Confound Controls (Prof. Rex's mitigations):**
✅ Single-source sampling (Common Crawl only)  
✅ Fixed intermediate size (70% → 49%)  
✅ Derived thresholds (from DATAMASK/FAC prior results)  
✅ Ultra-small scale added (10K tokens)

Prof. Pax — does this experimental design pass your feasibility check? It's 5 strategies × 4 scales × 1 model architecture = 20 training runs. At 5 epochs each on GPT-2 Small (124M), that's ~40 GPU-hours total (assuming 2 hours per 10M token run). Feasible for a 3-month project with 8 GPUs.

**Key Points:**
- Locked experimental protocol: Common Crawl source, 4 scales, 5 strategies, fixed sizes
- Quantified predictions: Reversal (±8pp), synergy (≥12pp), saturation curves
- Falsification clear: No reversal = H0, weak synergy = not worth complexity
- Compute feasibility: 20 runs × 2 GPU-hours = 40 total (3 months with 8 GPUs)

Do we have convergence on the hypothesis and experimental design?

---



## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Scale-dependent interaction reversal is genuinely novel — prior work (DATAMASK, Mixing Laws) showed interactions exist but not that optimal strategy FLIPS across dataset scales. The differential scaling dynamics hypothesis (quality saturates, diversity persists) predicts a phase transition in curation practice.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Hypothesis is rigorously testable with clear falsification criteria. Quantified predictions (reversal ±8pp, synergy ≥12pp, saturation curves) allow statistical testing. Experimental design controls confounds (single-source, fixed sizes, 4-scale reversal proof). H0 clearly stated: independent scaling.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Prescriptive impact beyond descriptive: dynamic curation schedules would change current practice (filter-once-train-forever → adaptive re-filtering). Challenges independence assumption in data mixing research. If confirmed, invalidates ablation studies that test strategies in isolation.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Mechanism grounded in sampling statistics (long-tail coverage), not speculative neural dynamics. 20 training runs × 2 GPU-hours = 40 total compute — feasible for 3-month project. Uses existing benchmarks (BEIR, ToolBench, MMLU) and standard architecture (GPT-2 Small).

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Hypothesis:** Quality-based filtering and diversity-based sampling exhibit DIFFERENTIAL SCALING DYNAMICS — quality's marginal benefit decreases with dataset size while diversity's marginal benefit remains constant or increases. This produces SCALE-DEPENDENT INTERACTION EFFECTS where optimal curation strategy reverses across dataset scales.

**Mechanism:** At small scale (10K-100K tokens), high-quality documents efficiently cover critical patterns — quality filtering maximizes learning efficiency. At large scale (1M-10M tokens), coverage shifts to long-tail patterns that quality filtering may exclude — diversity sampling becomes more valuable. The interaction emerges from sampling statistics: quality-first (QD) removes low-quality but potentially diverse documents early, limiting later diversity gains. Diversity-first (DQ) preserves long-tail coverage while applying quality as a secondary constraint.

**Experimental Approach:** Train GPT-2 Small (124M) on 4 dataset scales (10K, 100K, 1M, 10M tokens) using 5 strategies (Q-only, D-only, QD, DQ, baseline). Sample from Common Crawl (single source) with fixed intermediate sizes (70% → 49%). Evaluate on BEIR (retrieval), ToolBench (agent tasks), MMLU (general capability).

**Key Predictions:**  
1. **Reversal:** QD > DQ at 10K by ≥8pp, DQ > QD at 10M by ≥8pp  
2. **Synergy:** DQ at 10M outperforms (D-only + Q-only - Baseline) by ≥12pp  
3. **Saturation:** Q-only improvement decreases across scales (+25 → +10pp), D-only improvement increases (+12 → +25pp)

**Novelty:** First work to demonstrate scale-dependent REVERSAL of optimal curation strategy ordering, moving beyond static "both matter" findings to prescriptive dynamic schedules.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Resource constraint confound if intermediate sizes aren't strictly controlled — mitigated by fixed 70% → 49% reduction
- **Concern 2:** Domain shift (curated → web) masquerading as scale effect — mitigated by single-source (Common Crawl) sampling
- **Concern 3:** Arbitrary thresholds (±8pp, ≥12pp) — should derive from DATAMASK/FAC baseline improvements as priors
- **Mitigation Strategy:** Run pilot at 100K scale first to calibrate thresholds from observed effect sizes before committing to full 4-scale experiment

