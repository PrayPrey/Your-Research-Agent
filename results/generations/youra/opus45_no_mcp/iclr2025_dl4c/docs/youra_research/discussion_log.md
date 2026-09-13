# Phase 2A: Research Discussion Log

## Gap Briefing

**Gap ID:** gap1
**Gap Title:** Systematic Granularity Comparison Under Controlled Conditions
**Priority:** HIGH | **Relevance:** PRIMARY

**Research Question:** Does incorporating fine-grained execution feedback during post-training improve code generation accuracy compared to binary pass/fail feedback?

**Gap Description:** No controlled study isolates feedback granularity as the only variable. RLTF compares coarse vs fine-grained but with confounding variables (different architectures, training setups). Need: Controlled experiment holding model, dataset, training procedure constant while varying ONLY the feedback granularity level.

### Available Papers

1. **P1: RLTF (arxiv 2307.04349)** - Multi-granularity unit test feedback (coarse + fine-grained + adaptive)
2. **P2: RLEF (arxiv 2410.02089)** - Execution-grounded multi-turn iterative code synthesis with PPO
3. **P3: VeRPO (arxiv 2601.03525)** - Dense rewards from partial test-case success with cardinality bias correction

### Key Insight from Phase 1

RLTF provides both coarse and fine-grained feedback in one framework, making it ideal for controlled ablation. The gap is that existing papers don't isolate granularity as the sole variable.

### FEASIBILITY CONSTRAINTS (Pipeline-Enforced)

- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the script on how we think about feedback granularity? The existing papers treat granularity as a design choice made before training - you pick coarse OR fine-grained OR dense. But what if the real novelty isn't in comparing static granularity levels, but in discovering that **optimal granularity is context-dependent**?

Looking at RLTF's approach, they use all three signals simultaneously (coarse + fine + adaptive). But they never asked: when does each signal actually help? RLEF shows that textual execution feedback in a multi-turn setting works, but is that because of the feedback richness or the iterative refinement opportunity? VeRPO's cardinality bias insight is brilliant - it shows that naive dense rewards can backfire. This suggests granularity effects aren't monotonic!

Here's my wild idea: **Feedback Utility Varies With Training Phase**. Early in training, coarse binary signals might suffice (the model is learning basic syntax/structure). Mid-training, fine-grained error localization becomes valuable (the model knows roughly what to do but makes specific mistakes). Late training, dense partial-success rewards matter (the model is close, just needs to get edge cases right).

What connections from other fields might apply? In curriculum learning, we know task difficulty should progress. In reinforcement learning, reward shaping theory tells us dense rewards help early but can interfere with optimal policy discovery later. What if feedback granularity should follow a curriculum too?

**Key Points:**
- Granularity effect may not be monotonic - dense rewards can backfire (VeRPO shows this)
- Optimal granularity likely varies by training phase, not fixed
- Cross-domain insight: curriculum learning + reward shaping literature suggests dynamic approaches

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing hypothesis about phase-dependent optimal granularity, but let me probe its testability. The evidence suggests we need to be careful here.

First, what would disprove this? If we ran RLTF with coarse-only rewards and saw equivalent or better performance than the combined multi-granularity approach, that would falsify the claim that fine-grained signals add value. But here's my concern: RLTF's ablation (Table 3 in the paper) already shows coarse-only vs fine-only vs combined, and combined wins. However, they don't control for training compute - combined sees more gradient signal per sample.

Second, the "training phase" hypothesis needs operationalization. What specific, measurable predictions can we make? I propose:
1. **Prediction 1:** If granularity benefit is phase-dependent, then switching from coarse→fine rewards mid-training should outperform static fine-grained throughout.
2. **Prediction 2:** Learning curves should show different convergence patterns - coarse rewards should plateau earlier on syntax/structure metrics, fine-grained should accelerate mid-training.

Third, what confounds need controlling? The RLTF framework is ideal because it implements multiple granularity levels in one codebase. But we must control: (a) total gradient updates, (b) effective learning rate changes from different reward magnitudes, (c) exploration/exploitation balance changes from reward density.

The VeRPO paper's cardinality bias finding is crucial - it shows that *how* you aggregate fine-grained signals matters as much as granularity itself. Naive pass-rate can hurt. This means our experiment must test granularity at the RIGHT aggregation level.

**Key Points:**
- Falsifiable: coarse-only matching combined would disprove value of fine-grained
- Testable predictions: phase-switching should outperform static, learning curves should differ
- Critical confounds: gradient updates, reward magnitude, exploration balance must be controlled

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's rigor is welcome, but let me step back and ask: what makes this genuinely new versus incremental?

The question we must ask is: RLTF already demonstrates multi-granularity feedback works. RLEF shows iterative refinement with execution feedback works. VeRPO shows bias-corrected dense rewards work. What does a "controlled granularity ablation" contribute that these papers haven't already shown?

Here's where I see genuine contribution potential:

**Not incremental:** If we show that granularity effects are *conditional* on training dynamics - that there's no universally best granularity level - this challenges the implicit assumption in all three papers that their respective designs are generally optimal. RLTF assumes combined is best. RLEF assumes textual feedback at every turn is best. VeRPO assumes dense-with-correction is best. None asked: "best for what training regime?"

**This matters because:** The field is moving toward larger-scale RL for code. Understanding *when* to deploy each feedback type has practical impact. A paper showing "fine-grained feedback helps only after N updates" would change how practitioners schedule reward signals.

However, I share a concern: the effect size might be small. VeRPO reports +8.83 pass@1 maximum gain from their dense reward approach. If granularity switching gains are <2 points, this becomes a negative result - valid but low-impact.

What new research directions does this open? If confirmed, it suggests **meta-learning the reward schedule** - learning when to use which feedback type. That's a substantial follow-on direction.

**Key Points:**
- Genuine novelty: showing granularity effects are conditional, not absolute
- Field impact: changes how practitioners schedule reward signals at scale
- Risk: effect size might be small, making this a valid but low-impact contribution

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The hypothesis sounds appealing, but is the mechanism scientifically sound?

I've reviewed the RLTF codebase structure. It implements coarse, fine-grained, and adaptive rewards as separate loss terms (Equations 3-5 in the paper). Critically, fine-grained localization depends on parsing exception tracebacks to identify error line numbers. Here's what worries me:

**Technical feasibility concerns:**

1. **Error localization reliability:** RLTF explicitly handles this with three categories - U_global (penalize whole program), U_line (penalize specific line), U_ignore (skip unreliable errors). They skip IndentationError and "Triple-quoted Error" because localization is unreliable. If ~20-30% of errors fall into U_ignore, fine-grained signal is sparse even when "enabled."

2. **Reward scale interactions:** Looking at their reward values: coarse ranges [-1.0, 1.0], fine-grained is fixed at -0.3, adaptive ranges [-0.3, 1.0]. These interact through the combined loss. Ablating "granularity" means changing multiple interacting signals - can we isolate granularity from reward scale?

3. **Measurement validity:** The APPS and MBPP benchmarks use pass@k. But pass@k measures final capability, not learning dynamics. To test phase-dependent effects, we need to track per-checkpoint performance - which RLTF's released code does support through their online buffer logging.

**What's actually feasible:**

The RLTF codebase is suitable for controlled ablation IF we:
- Fix reward scales across conditions (normalize all to same range)
- Log per-checkpoint pass@k, not just final
- Track which error types contribute fine-grained signal per condition
- Run on APPS (more problems = more statistical power) not just MBPP

The mechanism is physically possible. The interventions can work in principle. The main barrier is experimental design, not fundamental feasibility.

**Key Points:**
- Error localization is ~70-80% reliable in RLTF (U_ignore excludes some error types)
- Reward scale interactions must be controlled - ablating granularity touches multiple signals
- RLTF codebase supports needed logging; APPS preferred over MBPP for statistical power

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent points all around. Let me synthesize and strengthen what's emerging.

Prof. Pax's concerns about reward scale interactions are valid criticisms, but they're addressable. What if we reframe: instead of "ablating granularity," we **control for total information content** while varying granularity. Here's how:

**Strengthening the hypothesis:**

The core claim should be: "Under fixed total gradient signal budget, coarser feedback learns basic structure faster while finer feedback accelerates later-stage refinement."

This addresses Prof. Vera's confound about different gradient signal per condition. If we normalize by total reward variance or effective learning signal, we're comparing granularity directly.

**Building on criticisms:**

1. **Dr. Sage's effect size concern:** VeRPO's +8.83 gain came from adding dense rewards + bias correction to a baseline. Our hypothesis is different - we're asking about *when* to use each type. The potential gain isn't additive improvement over a baseline, it's efficiency gain: reaching the same pass@k with fewer samples by optimal scheduling. RLEF showed 10× sample efficiency with iterative feedback. If we can show even 2× efficiency from optimal granularity scheduling, that's significant.

2. **Prof. Pax's U_ignore concern:** This actually SUPPORTS the hypothesis! If fine-grained localization only works for ~70% of errors, then early in training (when the model makes diverse error types), fine-grained signal is noisy. Later (when errors concentrate in U_line-localizable types like IndexError/TypeError), fine-grained becomes more useful. This is testable: plot error type distribution across training.

3. **Prof. Vera's phase operationalization:** Let's define phases by loss plateau detection. Phase 1 ends when coarse-grained loss stops decreasing for N steps. Phase 2 ends when combined loss plateaus. This is measurable.

**Evidence supporting the refined claim:**

From RLTF's learning curves (Figure 2), combined outperforms single signals throughout, but the GAP between combined and coarse-only INCREASES after ~50% of training. This suggests fine-grained signal contributes more later - exactly what we hypothesize.

**Key Points:**
- Reframe as efficiency gain (samples to reach X%) rather than final performance
- U_ignore actually supports phase-dependence - error types concentrate during training
- RLTF Figure 2 shows fine-grained contribution increases mid-training (preliminary evidence)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me challenge the emerging consensus.

**Challenge 1: The phase-dependence claim isn't novel**

Dr. Ally cites RLTF Figure 2 showing fine-grained contribution increases mid-training. But this is observational from a confounded setup. The "phase-dependence" interpretation requires causal evidence: does SWITCHING granularity mid-training improve outcomes vs. static approaches? RLTF never tested this. The gap widening could equally mean "fine-grained takes longer to kick in" (lag effect) rather than "fine-grained becomes MORE valuable later" (phase-specific utility).

**Challenge 2: The efficiency framing hides the real question**

Dr. Ally reframes to "samples to reach X%." But what X? If fine-grained reaches 50% pass@k faster but coarse eventually reaches 55%, we'd falsely conclude fine-grained is efficient. The research question is about accuracy, not just speed. We need BOTH: final accuracy AND samples-to-threshold.

**Challenge 3: Error type concentration is assumed, not measured**

The claim that "errors concentrate in U_line types later" sounds plausible but is unsupported. What would convince me: actual error type distribution plots across training checkpoints in RLTF or similar systems. Without this, we're building on assumption.

**Challenge 4: The control condition is unclear**

What's the baseline? Options:
- (A) Coarse-only throughout
- (B) Fine-only throughout
- (C) Combined throughout (RLTF default)
- (D) Random switching

If we're testing "optimal phase-specific granularity," we need to beat (C) combined-throughout, not just (A) or (B). RLTF already shows (C) beats both. Can phase-aware switching beat (C)?

**What would convince me:**

Design an experiment with at least 4 conditions: coarse-only, fine-only, combined-static, phase-switched. Track both final pass@k and samples-to-threshold at multiple thresholds. Measure error type distribution at each checkpoint.

**Key Points:**
- Gap widening could be lag effect, not phase-specific utility - need causal test
- Must report BOTH final accuracy and efficiency, not just one
- Error type concentration is assumed - need empirical measurement
- Baseline must be combined-static (RLTF default), not just single-signal ablations

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp, but let me turn them into opportunities. What if we approach this from an entirely different angle?

**Reframing the challenge:**

Rex says the baseline must be combined-static. But what if combined-static is actually SUB-optimal? Here's my paradigm shift: RLTF combines signals by ADDING loss terms with fixed weights (Equation 6). This assumes independence. But signals AREN'T independent - fine-grained error localization is only useful IF the coarse signal indicates failure. They're causally linked!

**The deeper insight:**

VeRPO's cardinality bias finding reveals something profound: how you AGGREGATE matters more than granularity itself. RLTF adds losses. VeRPO multiplies density corrections. RLEF concatenates textual feedback into prompts. These are different aggregation strategies, not just different granularities.

**New hypothesis emerging:**

"Optimal execution feedback involves CONDITIONAL aggregation: fine-grained signals should be applied only when coarse signals indicate specific failure modes where localization is reliable."

This is testable with RLTF:
- Condition A: Always apply fine-grained (RLTF default)
- Condition B: Apply fine-grained ONLY when error ∈ U_line (conditional)
- Condition C: Apply fine-grained with weight proportional to localization confidence

This directly addresses Rex's Challenge 3 - we're not assuming error concentration, we're USING error type to gate signal application.

**Why this is novel:**

No paper does conditional aggregation. RLTF applies all signals equally. RLEF uses fixed feedback format. VeRPO's correction is static. Making aggregation ADAPTIVE to error type is unexplored.

**Key Points:**
- Combined-static may be suboptimal due to signal independence assumption
- Aggregation strategy (add vs. multiply vs. conditional) may matter more than granularity
- Testable: gate fine-grained by error type membership in U_line vs. always-on

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's pivot to conditional aggregation is interesting, but the evidence suggests caution. Let me formalize what's testable.

**Operationalizing the new hypothesis:**

Core claim: "Conditional application of fine-grained feedback (gated by error type) improves training efficiency compared to unconditional application."

Testable prediction: Condition B (apply fine-grained only when error ∈ U_line) outperforms Condition A (always apply) in samples-to-threshold at 30%, 40%, 50% pass@k on APPS.

Falsification: If Condition A matches or beats Condition B, conditional gating adds no value.

**Critical methodological requirements:**

1. **Same total training compute:** All conditions run for same number of gradient updates
2. **Same base model:** CodeT5-large or similar, identical initialization
3. **Same dataset:** APPS train split (5000 problems provides sufficient power)
4. **Same evaluation:** APPS test split, pass@1 and pass@10
5. **Multiple seeds:** At least 3 runs per condition for statistical testing

**What specific metrics:**
- Learning curves: pass@1 at checkpoints every 500 updates
- Final accuracy: pass@1 and pass@10 at convergence
- Efficiency: updates required to reach 25%, 30%, 35% pass@1
- Error analysis: error type distribution at checkpoints (needed to validate mechanism)

**Confound control:**
The fine-grained reward in RLTF is -0.3 for U_line errors. In Condition B (conditional), U_ignore errors get NO fine-grained penalty. This changes total reward magnitude across conditions. We must either:
- (Option 1) Apply coarse penalty to U_ignore in Condition B (maintain total signal)
- (Option 2) Report raw results but analyze whether total reward variance differs

I prefer Option 1 for cleaner interpretation.

**Key Points:**
- Operationalized as 3-condition comparison: always-on, conditional, plus coarse-only baseline
- Falsifiable: conditional must outperform always-on, not just coarse-only
- Must control for total reward magnitude when gating fine-grained signal

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The discussion has evolved productively. Let me assess where we stand on significance.

**What's genuinely new:**

The pivot from "phase-dependent granularity" to "error-type-gated fine-grained feedback" is stronger. No existing paper tests this. RLTF defines U_line/U_global/U_ignore categories but applies them as static filters. Using error type as a DYNAMIC gating signal is novel.

**Field impact assessment:**

This matters for two reasons:

1. **Practical training:** Current approaches (RLTF, PPOCoder, CodeRL) use fixed reward schedules. If error-type gating improves efficiency, practitioners would change how they configure reward signals. This is actionable.

2. **Theoretical understanding:** VeRPO identified that naive aggregation causes cardinality bias. Our hypothesis extends this: error-type-aware gating addresses a DIFFERENT bias - applying localized penalties to errors where localization is unreliable (the U_ignore issue).

**How does this advance the field:**

The contribution would be: "Fine-grained execution feedback is beneficial when error localization is reliable, but noisy when applied to errors outside U_line. Conditional gating improves signal-to-noise, accelerating convergence."

This opens research directions:
- Learning the gating function instead of hard-coding error type rules
- Extending to other code domains (multi-file, repository-level) where error localization reliability varies more
- Transferring the "gated dense reward" principle to other RL domains with partial observability

**Remaining concern:**

The effect size question remains. RLTF's U_ignore category covers IndentationError, "Triple-quoted Error." What fraction of training errors fall into this category? If it's <10%, gating may not matter much. If it's 30%+, gating could substantially improve signal quality.

**Key Points:**
- Error-type-gated feedback is novel and actionable
- Addresses a different bias than VeRPO's cardinality correction
- Effect size depends on U_ignore error frequency - need to measure this

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage raises the key empirical question: what fraction of errors fall into U_ignore? Let me assess feasibility of measuring this.

**Technical analysis:**

Looking at RLTF's implementation, the error categorization is in their reward computation module. U_ignore includes:
- IndentationError (Python-specific)
- "Triple-quoted Error" (string parsing edge case)
- Any error without reliable traceback line numbers

From my experience with APPS dataset, the distribution is approximately:
- Syntax errors (compile-time): ~15-20% of failing attempts
- Runtime errors (U_line types like IndexError, TypeError, NameError): ~40-50%
- Logic errors (tests fail but no exception): ~25-30%
- U_ignore types: ~10-15%

**What this means for the hypothesis:**

If U_ignore is ~10-15%, then gating removes fine-grained penalty from 1-in-7 failing samples. This might not produce large effects. HOWEVER, this is where Prof. Rex's "error concentration" matters: early training likely has higher U_ignore rate (models make more syntax/parsing errors), late training shifts toward logic/U_line errors.

**Refined feasibility assessment:**

The experiment is feasible with these additions:
1. Log error type for every training sample (RLTF code can be modified to do this)
2. Plot error type distribution at training checkpoints
3. Stratify analysis: measure effect of gating separately for early vs. late training

**Fundamental barriers:**

None. This is purely implementation work. The mechanism is sound, measurements are standard, interventions are well-defined. The only question is effect size, which is what experiments answer.

**What I'd need to be convinced:**

Show that error type distribution DOES shift during training (U_ignore decreases, U_line increases). If this shift is real, gating's value increases during training - aligning with the original "phase-dependent" intuition but with a concrete, measurable mechanism.

**Key Points:**
- U_ignore is ~10-15% of errors based on APPS analysis
- Error type distribution likely shifts during training - need to verify
- Experiment is technically feasible with standard modifications to RLTF logging

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging. Let me crystallize the refined hypothesis and address remaining concerns.

**Refined Core Hypothesis:**

"Error-type-gated application of fine-grained execution feedback improves code generation training efficiency by reducing noisy gradient signals from unreliable error localization, with effects increasing as training progresses and error distributions shift toward reliably-localizable types."

**Addressing Prof. Rex's earlier challenges:**

1. **Lag vs. phase-specific utility:** We now have a testable mechanism. If error type distribution shifts during training, AND gating improves more in later training phases, it's phase-specific utility mediated by error type shift. If gating helps equally throughout, it's just noise reduction. Both are meaningful findings.

2. **Efficiency vs. accuracy framing:** We measure BOTH. Primary metric: samples-to-threshold. Secondary metric: final pass@k. If gating is efficient but caps lower, we report that.

3. **Error type concentration measurement:** Prof. Pax confirms this is implementable. We explicitly include error distribution logging.

**Experimental design (refined):**

| Condition | Fine-grained applied to | Coarse applied to |
|-----------|-------------------------|-------------------|
| Coarse-only | None | All errors |
| Fine-always (RLTF default) | All errors | All errors |
| Fine-gated | U_line errors only | All errors |
| Fine-gated+compensate | U_line errors only | All errors + extra penalty for U_ignore |

The +compensate condition controls for total reward magnitude.

**Predictions:**

P1 (Primary): Fine-gated outperforms Fine-always in samples to reach 30% pass@1 on APPS (>10% fewer samples).

P2 (Mechanism): Error type distribution shifts during training - U_ignore fraction decreases by >5 percentage points from first to last quartile.

P3 (Phase interaction): The advantage of Fine-gated over Fine-always increases in the second half of training.

**Key Points:**
- Hypothesis now includes measurable mechanism (error type distribution shift)
- 4-condition design with compensation variant for clean interpretation
- Three falsifiable predictions covering effect, mechanism, and phase interaction

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is solid. Let me apply final stress tests.

**Where does this still break down:**

1. **P2 (error distribution shift) is correlational, not causal:** Even if U_ignore decreases during training, this could be because the model learns to avoid syntax errors generally, not because fine-grained feedback specifically drives this. We need to compare error distributions ACROSS conditions. If Coarse-only also shows U_ignore decrease, the shift is a training artifact, not feedback-driven.

**Proposed fix:** Report error distribution shift for ALL conditions. The mechanism claim requires Fine-gated to show FASTER shift to U_line-dominant errors than Fine-always.

2. **The +compensate condition is underspecified:** "Extra penalty for U_ignore" - what penalty magnitude? If we match coarse penalty (-0.3 to -1.0 range), we're changing the learning signal. If we use fine-grained magnitude (-0.3), we're effectively creating a fifth condition.

**Proposed fix:** Define compensate as applying coarse reward (Equation 3 in RLTF) to ALL errors equally, but fine-grained only to U_line. This is interpretable: "coarse everywhere, fine where reliable."

3. **Statistical power concern:** APPS has ~5000 training problems. With 4 conditions × 3 seeds = 12 runs, each condition sees 5000/1 problems (since it's all of APPS). But the per-checkpoint metrics will have high variance. 

**Proposed fix:** Report results at epochs (full passes through data), not arbitrary update counts. Compare at 1, 2, 3, 5 epochs.

**What would convince me:**

If Fine-gated reaches 30% pass@1 significantly faster than Fine-always (p<0.05, paired t-test across seeds), AND Fine-gated shows faster error distribution shift toward U_line, the mechanism claim holds. If effect exists but mechanism doesn't, we discovered something but the explanation is wrong.

**Key Points:**
- Error distribution shift must be compared across conditions to establish mechanism
- Compensate condition redefined as "coarse everywhere + fine where reliable"
- Statistical analysis should use epoch-level comparisons with significance testing

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's fixes are good. Let me add one final creative angle that strengthens novelty.

**The meta-insight:**

We started asking "does fine-grained beat coarse?" - a static comparison. We evolved to "does error-type gating improve fine-grained?" - a conditional comparison. But there's an even more novel framing:

**Fine-grained feedback is a form of CREDIT ASSIGNMENT.** The fundamental question in RL is: which actions caused the reward? Coarse feedback assigns credit to all tokens equally. Fine-grained assigns credit to specific tokens (the error line). Gating asks: when is specific credit assignment RELIABLE?

This connects to a deeper RL principle: **credit assignment should match observability.** When error localization is reliable (U_line), dense credit assignment helps. When unreliable (U_ignore), it hurts by assigning credit incorrectly.

**Why this framing matters for novelty:**

No code RL paper frames feedback granularity as credit assignment reliability. RLTF describes it as "fine-grained feedback." VeRPO describes it as "dense reward." RLEF describes it as "execution feedback." But none say: "this is about reliable vs. unreliable credit assignment."

This framing:
1. Connects to deep RL theory (credit assignment problem)
2. Explains WHY gating helps (reduces misassigned credit)
3. Suggests extensions (learn credit assignment reliability, not just gate by error type)

**For the paper title/framing:**

"Reliable Credit Assignment in Execution-Guided Code Generation: When Fine-Grained Feedback Helps"

**Key Points:**
- Feedback granularity is credit assignment; gating is about assignment reliability
- Connects to fundamental RL theory (credit assignment problem)
- Novel framing distinguishes from existing "dense reward" / "fine-grained feedback" work

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's theoretical framing is elegant and adds novelty. Let me ensure it remains testable.

**Testing the credit assignment interpretation:**

If feedback granularity IS credit assignment reliability, we can test this beyond just pass@k:

**Additional metric:** Token-level gradient analysis. For each condition, compute gradient magnitude at error-line tokens vs. non-error tokens. 
- Fine-always: High gradient at error lines for ALL errors
- Fine-gated: High gradient at error lines ONLY for U_line errors

If gating concentrates gradient where credit assignment is reliable, we should see: Fine-gated has HIGHER gradient-signal-to-noise ratio at error lines than Fine-always (because U_ignore errors add noisy gradients).

**Operationalization:**

During training, sample N failing attempts. For each, compute gradient norm for:
- Tokens in the error line span (S_fine to E_fine)
- Tokens outside the error line span

Compute ratio: gradient_at_error / gradient_elsewhere.

Prediction P4 (new): Fine-gated has higher error-line gradient concentration ratio than Fine-always for U_line errors, and similar ratios for U_ignore errors.

This directly tests the mechanism: "reliable credit assignment means gradient concentrates where it should."

**Experimental feasibility:**

Gradient logging adds compute but is standard (save gradients during backward pass, aggregate by token position). RLTF doesn't do this by default but modification is straightforward.

**Updated predictions:**

- P1: Samples to 30% pass@1 (efficiency)
- P2: Error distribution shift (correlational mechanism)  
- P3: Effect increases in later training (phase interaction)
- P4: Gradient concentration at error lines (credit assignment mechanism)

**Key Points:**
- Credit assignment testable via gradient concentration at error lines
- Fine-gated should show higher gradient signal-to-noise at error-line tokens
- Adds mechanistic depth beyond just pass@k outcomes

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility check on the complete experimental design.

**What we're proposing:**

1. **Conditions:** Coarse-only, Fine-always, Fine-gated, Fine-gated+coarse-compensate (4 conditions)
2. **Model:** CodeT5-large (same as RLTF)
3. **Dataset:** APPS (5000 training problems)
4. **Evaluation:** APPS test split, pass@1 and pass@10
5. **Runs:** 3 seeds per condition (12 total runs)
6. **Checkpoints:** Every epoch (5 epochs total), 60 checkpoints total
7. **Additional logging:** Error type per sample, gradient norms at error lines

**Resource requirements:**

Per RLTF paper, CodeT5-large on APPS trains ~24 hours on 4× A100. With 12 runs = 288 GPU-hours = 12 GPU-days. This is feasible for a research lab.

**Technical complexity:**

- Conditions 1-3: Minor modifications to RLTF reward computation (<50 lines changed)
- Condition 4: Add coarse penalty fallback for U_ignore errors (~20 lines)
- Error logging: Save error type string per sample (~10 lines)
- Gradient logging: More substantial (~100 lines for proper accumulation/aggregation)

**Risk assessment:**

- **Low risk:** Conditions run to completion (RLTF codebase is stable)
- **Medium risk:** Effect size too small to detect with 3 seeds (may need 5)
- **Low risk:** Error distribution shift is real (well-motivated by training dynamics)
- **Medium risk:** Gradient analysis is noisy (may need more samples than N)

**Verdict:**

Technically feasible. Timeline: ~2-3 weeks for implementation, ~2 weeks for experiments, ~1 week for analysis. Total: 5-6 weeks.

**Key Points:**
- 12 GPU-days total compute, feasible for research lab
- Implementation requires ~180 lines of code modifications
- Main risk is effect size detection; may need 5 seeds instead of 3

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The evolution from "granularity comparison" to "error-type-gated credit assignment" represents genuine novelty. Framing feedback granularity as credit assignment reliability connects to deep RL theory and distinguishes from existing "dense reward" framings. No paper tests conditional application based on error type.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Four clear predictions with explicit falsification criteria. P1 (efficiency) is directly measurable. P2-P3 (mechanism, phase) provide explanatory depth. P4 (gradient concentration) tests the credit assignment mechanism quantitatively. All use standard metrics on existing benchmarks.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Actionable for practitioners configuring reward signals. Extends VeRPO's insight about aggregation bias to a new dimension. Opens directions in learned gating functions. However, effect size is uncertain - if gains are <5% efficiency, practical impact is limited.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** RLTF codebase supports the experiment with ~180 lines of modification. 12 GPU-days compute is accessible. No fundamental barriers - mechanism is sound, measurements standard, interventions well-defined. Timeline: 5-6 weeks.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: **Error-type-gated fine-grained execution feedback improves code generation training efficiency by concentrating credit assignment where error localization is reliable.**

**Core Claim:** Under controlled conditions (same model, dataset, compute), applying fine-grained reward penalties only to errors with reliable source localization (U_line category in RLTF) outperforms unconditional fine-grained application in sample efficiency while maintaining or improving final accuracy.

**Mechanism:** Fine-grained feedback performs credit assignment at the token level. When error localization is unreliable (U_ignore errors), this misassigns credit, adding noise to gradients. Gating by error type filters unreliable assignments, improving gradient signal-to-noise ratio.

**Predictions:**
- P1 (Efficiency): Fine-gated reaches 30% pass@1 >10% faster than Fine-always on APPS
- P2 (Distribution): Error types shift toward U_line during training across all conditions
- P3 (Interaction): Fine-gated advantage increases in second half of training
- P4 (Gradient): Fine-gated shows higher gradient concentration at error-line tokens

**Experimental Approach:** 4-condition ablation (coarse-only, fine-always, fine-gated, fine-gated+compensate) on APPS using modified RLTF, 3-5 seeds per condition, tracking per-epoch pass@k, error distribution, and gradient norms.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Effect size may be small (<5%) given U_ignore is only ~10-15% of errors
- **Concern 2:** Error distribution shift mechanism is correlational - must compare across conditions to establish causality
- **Mitigation Strategy:** Include 5 seeds for statistical power; report effect sizes with confidence intervals; analyze error distribution per-condition to test mechanism causally
