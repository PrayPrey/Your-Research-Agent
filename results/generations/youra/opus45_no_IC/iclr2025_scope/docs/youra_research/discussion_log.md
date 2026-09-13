# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap1-eviction-vs-compression
**Gap Title:** Systematic Comparison of Eviction vs Compression Trade-offs

**Research Question:** How do different KV cache compression strategies (eviction vs quantization) compare under unified conditions, and what is the Pareto frontier between memory efficiency and task accuracy?

**Current State:** Individual methods evaluated in isolation (H2O on its benchmarks, quantization on others). No unified Pareto frontier mapping exists.

**Missing Piece:** Systematic comparison across eviction ratio, quantization level, and task accuracy under identical conditions.

**Potential Impact:** Enable principled method selection based on deployment constraints (memory budget, accuracy requirements, task type).

### Key Reference Papers

1. **H2O: Heavy-Hitter Oracle** (Zhang et al., 2023) - arXiv:2306.14048
   - Dynamic submodular KV eviction via Heavy-Hitter tokens
   - 20% retention achieves near-full accuracy; up to 29x throughput

2. **StreamingLLM** (Xiao et al., 2023) - arXiv:2309.17453
   - Attention sink phenomenon; initial tokens must be retained
   - Window attention + attention sinks for infinite streaming

3. **Ada-KV** (Feng et al., 2024) - arXiv:2407.11550
   - Head-wise adaptive budget allocation
   - Theoretical loss upper bound for eviction optimization

4. **RocketKV** (Behnam et al., 2025) - arXiv:2502.14051
   - Two-stage compression (coarse eviction + fine-grain sparse attention)
   - Up to 400x compression ratio, 3.7x speedup

5. **LongBench** (Bai et al., 2023) - arXiv:2308.14508
   - Standard benchmark: 21 datasets, 6 task categories
   - Average length 6,711 words

### Implementation Resources

- **NVIDIA/kvpress** (1,161 stars) - Production library with H2O, StreamingLLM, SnapKV
- **KVCache-Factory** (1,356 stars) - Unified interface for multiple methods

### MANDATORY FEASIBILITY CONSTRAINTS

- Reject ideas requiring **new benchmarks, rubrics, or scoring frameworks**
- Reject ideas requiring **synthetic/generated data or future data**
- Reject ideas requiring **human evaluation or subjective scoring**
- Accept only hypotheses testable **immediately using existing datasets and benchmarks**

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What excites me about this gap is the untapped synergy nobody's systematically explored! We have two mature compression paradigms operating in parallel universes: eviction methods like H2O that surgically remove "unimportant" KV pairs, and quantization methods that compress ALL pairs to lower precision. But here's the creative leap — what if the Pareto frontier isn't a single curve but a *surface* depending on task type?

Looking at the Phase 1 evidence, H2O achieves ~80% retention with <2% accuracy drop, while quantization methods typically offer 4-8x compression. RocketKV hints at multiplicative gains with two-stage approaches. But nobody has asked: *which tokens benefit from eviction versus which benefit from compression?* 

Imagine this: high-attention "heavy-hitter" tokens might degrade significantly under aggressive quantization because their precise values matter, while low-attention tokens could be quantized to INT4 with minimal impact since they contribute little to the output anyway. This suggests a **token-importance-aware hybrid** — evict the truly useless, quantize the moderately important, keep the critical ones full-precision.

What if we approached this as an *allocation* problem? Given a memory budget B, how do we optimally partition it across eviction ratio, quantization level, and retention policy?

**Key Points:**
- Existing methods operate in isolation; no unified comparison exists
- The Pareto frontier may be task-dependent, not universal
- Hybrid approach: importance-aware allocation across eviction + quantization
- Framing as constrained optimization over memory budget

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's enthusiasm is infectious, but let me ground this in testability. The claim that "heavy-hitter tokens degrade more under quantization" is intriguing but currently unfalsifiable without explicit operationalization.

The evidence suggests we need precise definitions. What *exactly* constitutes a "heavy-hitter" in quantization context? H2O defines it via cumulative attention scores, but attention scores themselves are 32-bit — if we quantize KV to INT4, the attention computation changes, potentially altering which tokens appear "heavy." This creates a measurement confound.

Let me propose what would disprove the hybrid hypothesis: if we find that **eviction-only at X% retention achieves the same Pareto point as quantization-only at Y-bit precision**, then hybrid approaches offer no additional benefit — just engineering complexity. The null hypothesis must be: "Optimal eviction and optimal quantization reach the same accuracy at the same memory footprint; combining them provides no Pareto improvement."

For rigorous testing, I'd require:
1. **Fixed memory budget constraint** (e.g., 1GB for KV cache)
2. **Identical model** (Llama-2-7B or similar)
3. **Same benchmark** (LongBench 6 categories)
4. **Sweep both axes independently** then test combinations

What specific, measurable predictions can we make? If hybrid outperforms pure methods, by what margin? I'd want a testable threshold: hybrid achieves ≥2% accuracy gain over best pure method at equal memory.

**Key Points:**
- Heavy-hitter definition may shift under quantization — measurement confound
- Null hypothesis: pure eviction ≈ pure quantization at same memory budget
- Success criterion: hybrid ≥2% better than best pure method
- Need fixed conditions: same model, benchmark, memory constraint

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: does this advance the field, or merely fill a documentation gap? I've seen many "systematic comparison" papers that amount to benchmark tables without insight. What makes this genuinely new vs incremental?

Here's where I see significance: the field currently operates on *intuition* about when to use eviction vs quantization. Practitioners choose H2O because someone blogged it works, not because of principled selection criteria. If we can establish **task-type-to-strategy mapping** — e.g., "for summarization tasks, eviction dominates; for QA, quantization preserves retrieval better" — that's actionable contribution.

Looking at LongBench's 6 categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code), I hypothesize that tasks requiring *broad context integration* (summarization) may tolerate eviction better because no single token is critical, while tasks requiring *precise retrieval* (QA) may need full-precision KV for specific answer tokens.

This matters because it shifts the research direction from "which method is best?" to "which method for which task?" — a paradigm shift from universal to conditional optimization.

However, I must challenge 🔭 Dr. Nova's "token-importance-aware hybrid" framing. The implementation complexity of per-token decisions during inference may exceed the accuracy gains. The contribution must be *practical*, not just theoretically optimal.

**Key Points:**
- Significance lies in task-type-to-strategy mapping, not just benchmark tables
- Hypothesis: broad-context tasks favor eviction; precise-retrieval tasks favor quantization
- Shifts field from "best method" to "best method for task" — paradigm contribution
- Practical implementability must be part of the contribution

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. 🔭 Dr. Nova's per-token hybrid is theoretically elegant but practically questionable. Let me assess technical feasibility, not cost.

**Is the mechanism scientifically sound?** Partially. Eviction decisions happen once per generation step based on accumulated attention. Quantization typically happens at prefill or is static. Combining them dynamically — deciding per-token whether to evict, quantize, or retain — requires a decision function that itself adds latency. The question is: can we make these decisions fast enough that the memory savings translate to actual speedup?

RocketKV [Behnam et al., 2025] achieves 3.7x speedup with two-stage coarse-then-fine. This suggests staged approaches are tractable. But their "coarse eviction" and "fine-grain sparse attention" are both eviction-family methods, not eviction+quantization.

**What's fundamentally possible?** 
- Eviction at prefill + static quantization of retained KV: Yes, straightforward
- Dynamic per-token quantization during generation: Challenging (requires requantizing each step)
- Task-aware strategy selection at inference start: Yes, this is just a router

Here's what worries me about the original framing: "Pareto frontier mapping" sounds like an empirical study, not a novel method. If the contribution is "we ran all combinations and here's the curve," that's useful but incremental. The method contribution needs to be the *strategy selector* that picks the right point on the frontier.

**Key Points:**
- Per-token dynamic decisions add latency — may negate memory savings
- Staged approach (eviction → quantization) is tractable
- Task-aware strategy selection at inference start is feasible
- Pure Pareto mapping is incremental; need a *selector mechanism* as contribution

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND I see the synthesis emerging! Let me integrate the valid points raised.

🔬 Prof. Vera's concern about heavy-hitter definition shift under quantization is valid — but addressable. We can compute heavy-hitter scores at full precision *before* applying quantization, using the first few generation steps as a calibration phase. H2O already does this with accumulated attention; we just freeze the importance ranking before compression kicks in.

⚙️ Prof. Pax's feasibility critique of per-token decisions is spot-on. So let's refine: **not per-token, but per-strategy selection at task inference start**. This is a *router* that, given task type (detectable from prompt structure or explicitly labeled), selects from a menu of pre-validated compression configurations.

🎯 Dr. Sage's emphasis on task-type mapping is the real contribution. The hypothesis strengthens to:

**Refined Core Claim:** Different KV cache compression strategies (eviction, quantization, hybrid) exhibit task-dependent Pareto frontiers. A task-aware selector that routes to the optimal pre-validated configuration achieves ≥2% accuracy gain over task-agnostic defaults.

The selector is *not* a learned model requiring new training — it's a rule-based mapping derived from systematic Pareto analysis. This addresses the feasibility constraint (no new benchmarks/data needed) because we use LongBench's existing 6 task categories.

What if we addressed 🔬 Prof. Vera's null hypothesis directly? The prediction is: **for at least 3 of 6 LongBench task categories, the optimal compression strategy differs** (e.g., summarization prefers 40% eviction + FP16, while QA prefers 80% retention + INT8).

**Key Points:**
- Compute importance scores at full precision before compression (addresses measurement confound)
- Per-task selection at inference start, not per-token (addresses latency concern)
- Contribution: task-aware selector derived from Pareto analysis
- Testable prediction: optimal strategy differs across ≥3/6 task categories

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. The hypothesis claims "optimal strategy differs across task categories," but what evidence supports this assumption? Let me challenge the core premise.

**Unstated Assumption #1:** LongBench task categories are meaningfully distinct for KV compression. But "single-doc QA" and "multi-doc QA" may have similar attention patterns — both require retrieval. The 6-category split may not align with compression-relevant structure.

**Unstated Assumption #2:** Eviction and quantization are independent axes. But evicting tokens changes the quantization error distribution (fewer tokens = lower total error, but remaining tokens may be more critical). The interaction effect may dominate the main effects.

**Unstated Assumption #3:** A static selector is sufficient. But tasks within the same LongBench category vary — a 2K summarization vs 8K summarization may need different strategies. Task category may be too coarse.

What would convince me? Show me pilot data that the variance *between* task categories exceeds the variance *within* task categories for optimal compression configuration. If variance(within) ≥ variance(between), the selector adds noise, not signal.

I also challenge the 2% threshold. If the best pure method achieves 95% accuracy and hybrid achieves 97%, that's within measurement noise for many tasks. The effect size must exceed the benchmark's inherent variance.

**Key Points:**
- LongBench categories may not align with compression-relevant structure
- Eviction × quantization interaction may dominate main effects
- Task category may be too coarse (length/complexity varies within category)
- Effect size must exceed benchmark variance; 2% may be noise

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex raises sharp points, but I see an opportunity! The challenge about between-category vs within-category variance is empirically testable, and *that itself* could be the contribution.

What if we flipped the hypothesis? Instead of assuming task categories are meaningful, we **discover** the natural clustering of tasks based on their compression response profiles. Run all compression configurations on all LongBench tasks, measure (accuracy_drop, memory_saved) for each, then cluster tasks by their response patterns.

This is cross-domain thinking from recommendation systems: don't assume user demographics predict preferences; cluster users by actual behavior. Similarly: don't assume task categories predict compression preferences; cluster by observed response.

The paradigm shift becomes: **compression-response-based task embedding**. Each task gets a vector representing how it responds to [eviction ratio, quantization level, hybrid mix]. Tasks that cluster together share optimal strategies.

This addresses 🔍 Prof. Rex's concern directly — if LongBench categories align with discovered clusters, great; if not, we've found a more useful taxonomy. Either outcome is valuable.

Now we're onto something! The contribution isn't just "here's the Pareto frontier" but "here's a principled task taxonomy for compression selection."

**Key Points:**
- Flip from assuming to discovering compression-relevant task structure
- Cluster tasks by compression-response profiles, not a priori categories
- Contribution: data-driven task taxonomy for compression selection
- Either aligns with LongBench categories (validates them) or improves on them (novel insight)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's clustering idea is creative, but I must stress-test its testability. "Cluster by response profiles" requires running all configurations on all tasks — that's the full Pareto sweep anyway. The clustering is post-hoc analysis, not a predictive hypothesis.

Here's the critical weakness: **how do we validate the discovered clusters?** If we find 3 clusters, what experiment shows the clustering is *real* vs overfitting? Standard validation: hold out some tasks, predict their cluster from features, measure prediction accuracy. But with only 21 LongBench datasets, holdout is noisy.

Let me propose a tighter experimental design:

**Phase A (Characterization):** Run compression sweep on LongBench (6 configs × 21 datasets = 126 runs). Compute per-task response profile.

**Phase B (Clustering):** Discover natural task groupings via response similarity. Identify if clusters align with categories.

**Phase C (Prediction):** For each cluster, identify the *signature* (e.g., "long summarization with low entity density"). Test on a held-out benchmark (SCROLLS or custom).

The falsifiable prediction becomes: **cluster membership, derived from compression response, predicts optimal strategy on unseen tasks better than random (AUC > 0.7) or category-based (AUC improvement > 0.1).**

This satisfies 🔍 Prof. Rex's concern about effect size and gives us a concrete success threshold.

**Key Points:**
- Clustering is post-hoc; need predictive validation
- Three-phase design: characterization → clustering → prediction on held-out data
- Falsifiable: cluster membership predicts optimal strategy (AUC > 0.7)
- Comparison: cluster-based vs category-based selection

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground the scope. The three-phase design is sound, but let's verify it's technically achievable with *existing* resources.

**Phase A feasibility:** 6 compression configs × 21 datasets. Each LongBench task averages 6K words, so context ~8K tokens. Running Llama-2-7B with different compression settings — this is standard inference, no training. Using KVCache-Factory or kvpress, we can implement all configs. Estimate: ~50 GPU-hours on A100 (2-3 days single GPU).

**Phase B feasibility:** Response profiles are vectors of (accuracy, memory) per config. Standard clustering (k-means, hierarchical) on 21 × 6 = 126 measurements. This is trivial compute-wise.

**Phase C feasibility:** Here's the concern. Held-out validation requires *additional* benchmarks. SCROLLS exists but has different task definitions. We can do leave-one-category-out cross-validation within LongBench instead — train selector on 5 categories, test on 6th.

**What about the selector mechanism?** If the contribution is a task-aware router, what's the input feature? We can't use compression response (circular). Options:
1. Task category label (if categories align with clusters)
2. Prompt features (length, entity density, query structure)
3. First-100-token attention pattern (fast probe)

Option 3 is interesting: run a tiny probe inference to observe attention pattern, use that to predict optimal compression. This is technically feasible — adds <1% latency.

**Key Points:**
- Phase A/B feasible with existing tools (KVCache-Factory, kvpress)
- Phase C: use leave-one-category-out instead of held-out benchmark (avoids new data)
- Selector input: attention pattern probe (first 100 tokens) is feasible
- Probe adds <1% latency; worth investigating

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis is maturing. Let me synthesize the contribution structure and assess field impact.

**Core Contribution (if validated):**
1. **Empirical finding:** Task-dependent Pareto frontiers for KV compression exist and are measurable
2. **Taxonomy contribution:** Data-driven task clustering based on compression response differs from (or validates) LongBench categories
3. **Method contribution:** Attention-probe-based router that selects compression strategy at inference start

This matters for the field because it transforms KV compression from "pick one method" to "match method to task." Deployment teams get actionable guidance: "For your summarization workload, use this config; for QA, use that."

However, I must challenge the novelty claim. 🔭 Dr. Nova's clustering idea is standard data analysis — k-means on response profiles isn't novel. The novelty must come from either:
- **Surprising finding:** clusters don't align with categories (challenges conventional wisdom)
- **Surprising mechanism:** attention probe predicts compression preference (new connection)
- **Practical impact:** the selector achieves deployment-relevant gains (>5% memory reduction at iso-accuracy)

The research direction this opens: if attention patterns predict compression preference, future work can design *compression-aware attention mechanisms* that naturally produce compressible KV. That's the "new questions" part of significant contribution.

**Key Points:**
- Contribution: empirical finding + taxonomy + method (three-part structure)
- Novelty requires surprising finding or mechanism, not just systematic comparison
- If attention probe works, opens "compression-aware attention" research direction
- Impact threshold: >5% memory reduction at iso-accuracy for deployment relevance

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me crystallize the emerging consensus into a testable hypothesis statement.

**Core Hypothesis (Under-If-Then-Because):**

*Under* the constraint of fixed memory budget and existing LongBench benchmark,
*If* we characterize KV compression response profiles across eviction and quantization strategies per task,
*Then* tasks will cluster into ≥3 distinct groups requiring different optimal strategies, and an attention-probe-based router will select strategies with ≥5% memory improvement over task-agnostic defaults at iso-accuracy,
*Because* attention patterns in early tokens encode task structure that correlates with compression tolerance.

**Variables:**
- **IV:** Compression strategy (eviction ratio: 20/40/60/80%, quantization: FP16/INT8/INT4)
- **DV:** Accuracy retention (%) and memory usage (GB) — Pareto coordinates
- **Moderator:** Task type (discovered via clustering, compared to LongBench categories)

**Testable Predictions:**
1. **P1 (Clustering):** ≥3 natural clusters emerge from compression response profiles, not aligned with 6 LongBench categories (measured by adjusted Rand index < 0.5)
2. **P2 (Selector):** Attention-probe router achieves ≥5% memory reduction vs best single strategy at iso-accuracy
3. **P3 (Mechanism):** First-100-token attention entropy correlates with eviction tolerance (r > 0.4)

**Null Hypotheses:**
- H0-1: All tasks respond identically to compression (no clusters)
- H0-2: Best single strategy ≈ router selection (≤2% difference)
- H0-3: Early attention features don't predict compression response

**Key Points:**
- Core claim: attention patterns predict compression tolerance
- Three testable predictions with quantitative thresholds
- Mechanism connects attention structure to compression-response
- All testable with existing benchmarks (no new data required)

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me stress-test the refined hypothesis. 🛡️ Dr. Ally's formulation is tighter, but I see remaining weaknesses.

**Challenge to P1 (Clustering):** The prediction "≥3 clusters, adjusted Rand < 0.5 vs LongBench categories" is arbitrary. Why 3? Why 0.5? These thresholds need justification or they're p-hacking targets. Propose: report the *full* cluster structure without pre-specifying count, then validate via held-out prediction accuracy.

**Challenge to P2 (Selector):** "5% memory reduction at iso-accuracy" conflates two metrics. Either:
- Fix accuracy threshold (e.g., 95% of baseline), measure memory saved, OR
- Fix memory budget, measure accuracy maintained

The current phrasing allows cherry-picking. Tighten to: "At 90% baseline accuracy, router uses ≤80% memory of best single strategy."

**Challenge to P3 (Mechanism):** "Attention entropy correlates with eviction tolerance" is plausible but post-hoc. We compute entropy, compute tolerance, correlate — this *will* find something with 21 tasks. Need preregistration or held-out validation.

**Remaining concern:** The "first-100-token attention" probe assumes attention patterns stabilize quickly. Some tasks may have front-loaded context (instructions), others distributed (conversations). The probe may work for some tasks but fail for others, undermining the router.

What would convince me is a **staged rollout:** (1) characterize on 14 tasks, (2) train router on those, (3) test on held-out 7 tasks, (4) report honest held-out accuracy.

**Key Points:**
- Cluster count and thresholds need justification, not arbitrary
- Tighten P2: "at X% accuracy, router uses ≤Y% memory of best single"
- P3 correlation is post-hoc; needs held-out validation
- Staged rollout with honest held-out testing required

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

I can address 🔍 Prof. Rex's methodological concerns with a tighter experimental protocol.

**On clustering thresholds:** Instead of pre-specifying "≥3 clusters," use gap statistic to determine optimal cluster count. The hypothesis becomes: "Gap statistic identifies a non-trivial clustering structure (k* > 1) with gap > standard error." This is principled, not arbitrary.

**On evaluation conflation:** Agree completely. Define the Pareto frontier, then measure **area under the Pareto curve** (AUPC) for each strategy. Compare:
- AUPC(task-agnostic best) vs AUPC(task-aware router)
- Success: AUPC(router) > 1.05 × AUPC(best-single)

This avoids cherry-picking any single operating point.

**On held-out validation:** Implement 3-fold cross-validation across LongBench's 21 datasets:
- Fold 1: train on 14, test on 7 (random split)
- Fold 2: train on 14, test on 7 (different split)
- Fold 3: train on 14, test on 7 (remaining)
- Report mean ± std held-out AUPC improvement

**On probe stability:** Test probe variance. Run first-100-token probe 5 times per task (different random prefixes if applicable), measure probe feature stability. If variance(within-task) << variance(between-task), probe is reliable.

The revised falsification criteria:
1. Gap statistic k* = 1 (no clustering structure) → H0-1 holds
2. Mean held-out AUPC improvement < 5% → H0-2 holds
3. Probe feature stability < 0.8 correlation within-task → mechanism unreliable

**Key Points:**
- Use gap statistic for principled cluster count selection
- Compare AUPC (area under Pareto curve), not single-point accuracy
- 3-fold cross-validation for honest held-out evaluation
- Test probe stability: within-task vs between-task variance

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The methodology is solid. Let me verify implementation feasibility for each component.

**Gap statistic computation:** Standard scipy/sklearn, trivial.

**AUPC (Area Under Pareto Curve):** Need to define the Pareto computation carefully:
- X-axis: memory usage (normalized, 0 = minimum, 1 = full KV)
- Y-axis: accuracy retention (normalized, 0 = random, 1 = full accuracy)
- Compute convex hull of (memory, accuracy) points per strategy
- AUPC = area under the upper envelope

This is well-defined and standard in multi-objective optimization literature. Existing implementations: pymoo, scipy spatial.

**3-fold cross-validation on 21 tasks:** 7 held-out tasks per fold. With 6 compression configs, that's 42 measurements per fold — sufficient for AUPC comparison but tight for statistical significance. Consider bootstrap confidence intervals.

**Attention probe implementation:** Using HuggingFace transformers, we can extract attention weights from the first forward pass. Compute summary statistics (entropy, head-wise max, sparsity) in <10ms per sequence. Totally feasible.

**Compressed experiment matrix:**
- 21 tasks × 6 configs = 126 inference runs (Phase A)
- Each run: generate with compressed KV, score against LongBench reference
- Estimate: 4 hours on single A100 (batched inference)

Okay, this could work. The methodology is implementable with existing tools and reasonable compute.

**Key Points:**
- All components implementable with standard libraries
- AUPC well-defined via convex hull on (memory, accuracy) space
- Probe extraction adds <10ms latency — negligible
- Full experiment: ~4 hours single A100, feasible

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The methodology is converging. Let me synthesize the final hypothesis with the refined experimental design.

**FINAL HYPOTHESIS STATEMENT:**

*Core Claim:* Attention patterns in the first 100 tokens predict optimal KV cache compression strategy, enabling a lightweight router that selects task-appropriate configurations achieving ≥5% AUPC improvement over best single strategy.

*Mechanism:* Early attention entropy and head-wise activation sparsity encode task structure (e.g., retrieval-heavy vs synthesis-heavy), which correlates with differential tolerance to eviction vs quantization.

*Experimental Design:*
1. **Characterization (Phase A):** 21 LongBench tasks × 6 compression configs → 126 (accuracy, memory) measurements + attention probe features
2. **Clustering (Phase B):** Gap statistic determines cluster count k*; adjusted Rand index measures alignment with LongBench categories
3. **Router Training (Phase C):** 3-fold CV, train lightweight classifier (logistic regression) on attention features → predicted optimal config
4. **Evaluation:** AUPC improvement over best-single strategy, measured on held-out folds

*Predictions:*
- **P1:** k* > 1 (non-trivial clustering exists)
- **P2:** Mean held-out AUPC(router) > 1.05 × AUPC(best-single)
- **P3:** Attention entropy correlates with cluster membership (Spearman ρ > 0.5)

*Feasibility:* All testable with existing LongBench benchmark, kvpress library, and <5 GPU-hours compute.

*Novelty:* First systematic characterization of task-dependent KV compression frontiers; first attention-based compression router.

**Key Points:**
- Final hypothesis integrates all refinements
- Three quantitative predictions with clear thresholds
- Fully specified experimental protocol
- Feasible with existing resources; no new benchmarks needed

---

### Exchange 16

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is substantially stronger. Let me perform final stress-test.

**Remaining weaknesses addressed:**

✓ Arbitrary clustering threshold → gap statistic
✓ Evaluation conflation → AUPC metric
✓ Post-hoc correlation → 3-fold CV on held-out data
✓ Feasibility → ~5 GPU-hours, existing tools

**Residual concerns:**

1. **P2 threshold (5% AUPC):** This may be too aggressive. If AUPC(best-single) is 0.85, requiring 0.89 is a large jump. Consider reporting effect size with confidence interval rather than pass/fail threshold.

2. **Attention probe sensitivity:** What if optimal probe features differ by model architecture? The hypothesis should specify model (Llama-2-7B) and note that cross-model generalization is future work.

3. **Publication-readiness:** The "surprising finding" component depends on results. If clusters align with categories (Rand > 0.5), the story becomes "LongBench categories are meaningful" — useful but less novel. The hypothesis should pre-commit to what constitutes a positive result.

**Pre-commitment statement:** 
- If k* > 1 AND AUPC improvement > 5%: full positive result (novel router works)
- If k* > 1 AND AUPC improvement < 5%: clustering exists but router fails — publish as negative finding on routing
- If k* = 1: no task-dependent structure — important null result

This pre-commitment prevents p-hacking and establishes all outcomes as publishable.

**My verdict:** The hypothesis is now rigorous, testable, and feasible. I'm satisfied with the formulation.

**Key Points:**
- 5% threshold may be aggressive; report confidence intervals
- Specify model (Llama-2-7B); cross-model is future work
- Pre-commit to interpretation of all outcomes
- All three outcomes (positive, partial, null) are publishable

---

### Exchange 17

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess the final hypothesis against the significance criteria.

**Does this advance the field?**

✅ **Empirical contribution:** First systematic Pareto characterization across eviction + quantization + tasks
✅ **Methodological contribution:** AUPC-based comparison framework for multi-objective compression evaluation
✅ **Practical contribution:** Attention-probe router for deployment scenarios
✅ **Paradigm shift:** From "best method" to "best method per task"

**What's genuinely new?**

The integration is novel. Individual pieces exist (H2O eviction, INT4 quantization, LongBench benchmark), but their systematic comparison with task-conditioned routing is new. The attention-probe-as-router-input is a creative connection.

**Impact threshold:**

If the router achieves even 3-5% memory reduction at iso-accuracy, that's deployment-relevant for billion-parameter models where KV cache is the bottleneck. At 7B scale, 5% of KV memory is ~400MB — significant for edge deployment.

**Research directions opened:**

1. Compression-aware attention mechanisms (train attention to produce more evictable/quantizable patterns)
2. Dynamic compression switching mid-generation (if task structure changes)
3. Extension to vision-language models (HierKV, MMSep from citation network)

**My assessment:** This is a solid contribution. Not paradigm-shifting, but clearly advances the field with practical impact and opens follow-up research.

**Key Points:**
- Triple contribution: empirical, methodological, practical
- Novelty in integration and attention-probe router
- 5% memory reduction at 7B scale = ~400MB, deployment-relevant
- Opens research on compression-aware attention and VLM extension

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** MODERATE
- **Assessment:** The attention-probe router is a creative connection, and the task-clustering reframe adds novelty beyond pure benchmarking. However, the individual components (eviction, quantization, clustering) are established. The novelty lies in synthesis, not breakthrough.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable with gap statistic, AUPC comparison, and 3-fold CV. Specific quantitative thresholds (k* > 1, AUPC > 1.05×, ρ > 0.5) enable clear pass/fail evaluation. Pre-commitment to interpret all outcomes as publishable removes post-hoc flexibility.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Solid contribution with practical deployment impact (400MB savings at 7B scale). Advances the field from "pick one method" to "match method to task." Opens follow-up research on compression-aware attention. Not paradigm-shifting but clearly valuable.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully implementable with existing tools (kvpress, LongBench, sklearn). ~5 GPU-hours on A100. Attention probe adds <10ms latency. All methods have reference implementations. No novel infrastructure required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis: **Attention patterns in early tokens predict optimal KV cache compression strategy, enabling a lightweight router that achieves ≥5% AUPC improvement over best single strategy.**

The mechanism proposes that early attention entropy and head-wise sparsity encode task structure (retrieval vs synthesis), correlating with differential tolerance to eviction versus quantization. Tasks cluster into distinct groups by compression response profile, discoverable via gap statistic analysis of 126 (task × config) measurements on LongBench.

The experimental design follows three phases: (A) characterization sweep, (B) clustering validation, (C) router training with 3-fold CV. Success criteria are quantitative: k* > 1, AUPC improvement > 5%, attention-cluster correlation ρ > 0.5.

Novelty lies in the integration: systematic Pareto characterization + attention-based routing + task-conditioned compression selection. Practical impact: ~400MB KV memory savings at 7B scale for edge deployment.

The hypothesis is testable immediately using existing datasets (LongBench) and implementations (kvpress, KVCache-Factory). No new benchmarks, rubrics, or human evaluation required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- 5% AUPC threshold may be aggressive; report confidence intervals alongside pass/fail
- Cross-model generalization (beyond Llama-2-7B) is future work; state limitation explicitly
- If clusters align with LongBench categories (Rand > 0.5), novelty claim weakens — pre-commit to interpret this as validating existing taxonomy
- **Mitigation Strategy:** Report effect sizes with 95% CI; scope to single model architecture; pre-register interpretation of all outcome scenarios

---

## Emerged Hypothesis Summary

### Core Statement
Under the constraint of fixed memory budget and LongBench benchmark, if we characterize KV compression response profiles across eviction and quantization strategies per task, then an attention-probe-based router will select task-appropriate configurations achieving ≥5% AUPC improvement over best single strategy, because early attention patterns encode task structure that correlates with compression tolerance.

### Causal Mechanism
1. Early attention entropy reflects whether task requires broad integration (low entropy) or precise retrieval (high entropy)
2. High-entropy tasks tolerate eviction better (many tokens contribute equally)
3. Low-entropy tasks tolerate quantization better (few critical tokens need precision)
4. Router uses attention features to predict cluster → optimal config

### Variables
- **IV:** Compression strategy (eviction ratio × quantization level)
- **DV:** Pareto coordinates (accuracy retention %, memory usage %)
- **Moderator:** Task cluster (discovered via gap statistic)
- **Predictor:** Attention probe features (entropy, head-sparsity)

### Key Assumptions
- A1: Attention patterns stabilize within first 100 tokens
- A2: LongBench tasks adequately represent deployment workloads
- A3: Compression effects are model-dependent but probe features generalize within architecture family
- A4: AUPC captures deployment-relevant trade-offs
- A5: Lightweight router (logistic regression) is sufficient; no deep learning needed

### Null Hypothesis
There is no task-dependent structure in compression response (k* = 1) OR attention features do not predict optimal compression (AUPC(router) ≤ AUPC(best-single)).

### Predictions
- P1: Gap statistic identifies k* > 1 clusters
- P2: Router achieves AUPC > 1.05 × best-single on held-out tasks
- P3: Attention entropy correlates with cluster membership (ρ > 0.5)

### Novelty
First systematic task-conditioned Pareto characterization of KV compression; first attention-based compression router.

### Scope & Boundaries
- **Applies to:** Transformer-based LLMs with standard attention (Llama-2 family)
- **Does not apply to:** Non-attention architectures (Mamba), multimodal models (requires separate study)
- **Known limitations:** Single model architecture; English-primary benchmark; inference-only (no training integration)

### Experimental Setup
- **Dataset:** LongBench (21 tasks, 6 categories)
- **Model:** Llama-2-7B
- **Compression configs:** 6 (eviction: 40%/80% × quantization: FP16/INT8/INT4)
- **Baselines:** Best single strategy (task-agnostic), H2O default, StreamingLLM default

### Related Work & Baselines
- H2O [Zhang et al., 2023]: eviction baseline
- StreamingLLM [Xiao et al., 2023]: attention sink baseline
- Ada-KV [Feng et al., 2024]: adaptive budget baseline
- RocketKV [Behnam et al., 2025]: two-stage baseline

### Phase 2B Readiness Seeds
- **SH1 (Existence):** Task-dependent compression frontiers exist and are measurable
- **SH2 (Mechanism):** Attention entropy correlates with eviction tolerance
- **SH3 (Comparison):** Router outperforms best-single by ≥5% AUPC

### Established Facts
- Heavy-hitter eviction (H2O) achieves <2% accuracy drop at 20% retention [BUILD_ON]
- Attention sinks require initial token retention [BUILD_ON]
- LongBench provides 6-category task taxonomy [BUILD_ON]
- Quantization achieves 4-8x memory reduction [BUILD_ON]
- Task-dependent optimal compression [PROVE_NEW]
- Attention features predict compression preference [PROVE_NEW]

