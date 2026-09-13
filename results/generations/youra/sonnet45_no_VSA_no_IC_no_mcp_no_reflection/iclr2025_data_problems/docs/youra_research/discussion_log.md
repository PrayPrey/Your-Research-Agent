# Phase 2A Discussion Log - Self-Contained Tikitaka Loop

**Architecture:** Self-Contained Loop (Inline Self-Play - Independent Controller Ablation)  
**Workflow:** Phase 2A-Dialogue v9.0.0  
**Started:** 2026-08-28  
**Mode:** UNATTENDED (#batch-mode)

---

## Research Briefing

### Selected Gap

**Gap ID:** Gap 1  
**Title:** Theoretical Frameworks for FM-Specific Data Selection Scaling Laws  
**Relevance:** PRIMARY  
**Priority:** Critical

**Current State:** Neural scaling laws established for model size, compute, and total data quantity. Data-centric AI emphasizes quality over quantity but lacks formal scaling laws.

**Missing Piece:** Theoretical frameworks that predict how data selection quality (filtering, mixing strategies) affects FM performance at different scales. No unified theory connecting data curation decisions to downstream performance.

**Connection to Research Question:**
- Directly addresses Q3: "What theoretical frameworks can guide data selection decisions and inform scaling laws specific to foundation models?"
- Blocks main question: Research asks for "theoretically-grounded approaches" but current scaling laws focus on model/compute, not data selection quality

**Impact:** High - Without theoretical guidance, data curation remains trial-and-error at massive cost

### Related Research Papers

*No papers available for this gap (Phase 1 MCP unavailable)*

### Previous Failure / Routing Context

*No routing context - First Phase 2A attempt*

---

## Discussion Participants

🔭 **Dr. Nova** - Creative Novelty Explorer  
🔬 **Prof. Vera** - Rigorous Validation Architect  
🎯 **Dr. Sage** - Research Impact Evaluator  
⚙️ **Prof. Pax** - Feasibility & Reality Checker  
🛡️ **Dr. Ally** - Hypothesis Strengthening Champion  
🔍 **Prof. Rex** - Hypothesis Stress-Test Master

---

## Mandatory Feasibility Constraints (Pipeline-Enforced)

🚫 **REJECT:**
- New benchmarks, rubrics, or scoring frameworks
- Synthetic/generated data or future follow-up data that does not yet exist
- Human evaluation, annotation, or subjective scoring

✅ **ACCEPT ONLY:**
- Hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap between scaling laws and data curation quality is fascinating - we have predictive models for compute and model size, yet data quality remains this black box of heuristics. What if we approached this from information theory? Think of data curation as a compression problem: filtering removes redundancy, mixing balances information density across domains.

Here's a wild angle: existing scaling laws assume uniform data quality. But what if we modeled data curation decisions as a differentiable quality function Q(D) where D is the curated dataset? We could derive scaling relationships: Loss ~ (Model Size)^α × (Compute)^β × Q(D)^γ. The novel piece is treating data quality as a first-class scaling parameter with its own exponent.

Cross-domain inspiration: compressed sensing theory shows you need fewer high-quality measurements than low-quality ones. Could we adapt rate-distortion theory to formalize the quality-quantity tradeoff in FM pretraining? This would give us a theoretical foundation for answering: "Should I spend compute filtering 1T tokens to 100B high-quality ones, or just train on the full noisy 1T?"

**Key Points:**
- Model data quality Q(D) as differentiable function in scaling law framework
- Borrow from information theory: compression, rate-distortion, compressed sensing
- Novel scaling relationship: performance ~ model × compute × quality^γ
- Provides theoretical guidance for quality vs quantity tradeoff decisions

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's information-theoretic angle is creative, but let's ground this in testability. The claim that Q(D)^γ fits into scaling laws as a multiplicative term is interesting - but how do we measure Q(D) in a way that's reproducible across different domains?

Here's what worries me: existing scaling laws work because we can directly measure model size (parameter count) and compute (FLOPs). But "data quality" is notoriously domain-dependent. A perplexity-based filter works for language but not vision. So before we can test Q(D)^γ, we need operational definitions.

What would convince me this is testable: design experiments where we systematically vary one quality dimension while holding others constant. For example:
1. **Deduplication level:** Train identical models on {0%, 50%, 90%} deduplicated C4, measure convergence
2. **Domain mixing:** Vary mixing ratios across {web, books, code}, track downstream task performance
3. **Filtering threshold:** Apply quality classifiers at different cutoff scores, compare final loss

The prediction: if Q(D) truly follows a power law, we should see log-linear relationships when plotting quality metric vs performance. If not, the scaling law framework doesn't apply and we need a different theory.

**Key Points:**
- Q(D) must have operational, reproducible measurement across domains
- Testable prediction: systematic quality variations yield power-law performance curves
- Concrete experiments: deduplication levels, mixing ratios, filter thresholds
- Falsification criterion: non-power-law relationships invalidate the scaling framework

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This is where the significance lies: existing scaling laws tell us *how much* to scale, but give zero guidance on *what data* to scale with. If we establish that data quality follows predictable scaling relationships, we shift the paradigm from "bigger is better" to "smarter curation scales better."

The field impact potential is substantial. Current practice: teams spend millions on compute for massive pretraining runs, then discover their data was suboptimal only after the fact. A validated theory would enable *a priori* decisions: "This filtering strategy yields Q(D) = X, which predicts Y% performance gain - worth the compute cost."

But here's the contribution we must prove: Prof. Vera is right that we need operational Q(D) definitions. The genuine advance isn't just proposing Q(D)^γ - it's showing that *simple, measurable proxies* (deduplication ratio, domain diversity, perplexity) correlate with downstream performance in predictable ways.

What makes this more than incremental: we're not just optimizing within existing frameworks. We're proposing a theory that could fundamentally change how teams allocate resources between data curation and model scaling. That's a research direction opener, not just a performance improvement.

**Key Points:**
- Shifts paradigm: from "scale everything" to "scale smart with quality guidance"
- Practical impact: enables cost-benefit analysis of curation vs compute
- Must prove: simple measurable proxies predict downstream performance
- Opens research direction: quality-aware resource allocation theory

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's assess whether this quality scaling law is theoretically sound and measurable without creating new benchmarks. The information-theoretic foundation (rate-distortion, compression) is mathematically valid - these are established frameworks with proven properties. The mechanism is plausible in principle.

Here's what's feasible right now with existing infrastructure:
- **Measurement:** Use existing metrics (perplexity on held-out data, deduplication ratio, domain proportion) - no new benchmarks needed
- **Experiments:** C4, Pile, RedPajama datasets already exist with documented filtering pipelines. We can rerun ablations using existing compute budgets at smaller scales (1B-7B parameter models)
- **Validation:** Existing benchmarks (MMLU, HellaSwag, ARC) can measure downstream performance without creating new eval frameworks

But here's the fundamental challenge: the Q(D)^γ formulation assumes quality is a single scalar. Real data curation is multi-dimensional (toxicity, diversity, domain coverage, redundancy). Can we theoretically justify reducing this to one number, or do we need Q(D) = [q1, q2, ..., qn] with multiple exponents?

The measurement problem is solvable but non-trivial. We can use PCA or weighted combinations of existing metrics to derive a composite quality score, then validate whether it predicts performance. The theory supports this - but we must acknowledge this composite Q(D) is an approximation.

**Key Points:**
- Information-theoretic foundation is mathematically sound
- Measurement feasible using existing metrics and datasets (no new benchmarks)
- Can validate with existing evaluation frameworks
- Fundamental question: scalar Q(D) vs multi-dimensional quality requires theoretical justification

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by addressing Prof. Pax's multi-dimensional concern directly. Here's the refinement: we're not claiming data quality is truly one-dimensional - we're proposing that for *scaling law purposes*, there exists a learnable projection from multi-dimensional quality metrics onto a single scalar that predicts performance.

Think of it like model capacity: we know transformers have multiple dimensions (depth, width, attention heads), but we still use total parameter count as the primary scaling variable because it empirically predicts performance. The same logic applies to Q(D).

To address Prof. Vera's reproducibility concern: let's operationalize Q(D) as a weighted combination:
```
Q(D) = w1·dedup_ratio + w2·domain_diversity + w3·avg_quality_score + w4·token_efficiency
```
Weights learned from held-out validation performance. This makes it measurable, reproducible, and testable.

Dr. Sage's impact argument is strengthened by framing this as a *resource allocation theory*. The hypothesis isn't just "quality matters" - it's "quality has a quantifiable exchange rate with compute." That's actionable: "Improving Q(D) by 10% via better filtering is worth X additional training FLOPs."

**Key Points:**
- Learnable scalar projection from multi-dimensional quality (analogous to param count for model capacity)
- Operational Q(D): weighted combo of measurable metrics with validation-fitted weights
- Strengthened impact claim: quantifiable resource exchange rate between quality and compute
- Testable with existing infrastructure and benchmarks

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down if we're not careful: the weighted combination Q(D) = Σ wi·qi assumes the quality dimensions are *linearly combinable* and have *consistent exchange rates* across scales and domains. Show me evidence for that assumption.

What would disprove this hypothesis:
1. **Non-linear interactions:** If deduplication helps at 1B scale but hurts at 100B scale (due to memorization effects), the scalar Q(D) formulation fails
2. **Domain-specific weights:** If optimal weights for code (w_code) differ dramatically from weights for natural language (w_nlp), then Q(D) isn't generalizable
3. **Compute-quality coupling:** If the optimal Q(D) composition changes based on training compute budget, we have circular dependency

The assumption that needs validation: Q(D) is *stationary* across model scales, domains, and compute budgets. That's a strong claim requiring extensive ablation studies.

Alternative concern: existing scaling laws assume infinite data. But data curation *reduces* data quantity. So we're actually proposing a constrained optimization: maximize performance under data budget constraint, with quality as the optimization variable. This is a harder theoretical problem than just adding Q(D)^γ to the Chinchilla formula.

What would convince me: show that variance in performance explained by Q(D) is substantial (>20%) even after accounting for model size and compute. If quality explains <5% variance, it's not worth the theoretical complexity.

**Key Points:**
- Critical assumption: linear combinability and stationarity of Q(D) across scales/domains
- Falsifiers: non-linear interactions, domain-specific weights, compute-quality coupling
- Harder problem than stated: constrained optimization under data budget, not just adding term to scaling law
- Needs proof: Q(D) explains >20% performance variance beyond model size and compute

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's constrained optimization framing is brilliant - that's actually the MORE interesting theoretical contribution! Let's flip the narrative: instead of "adding Q(D) to existing laws," we're proposing a *data-compute tradeoff frontier*.

Think of it as the FM equivalent of Pareto optimality: for a fixed performance target, there's a frontier of (data quality, compute) combinations that achieve it. High Q(D) means less compute needed; low Q(D) requires more compute to compensate. The scaling law becomes:

```
Performance(L) = f(model_size, compute × g(Q(D)))
```

Where g(Q(D)) is an efficiency multiplier. High quality data makes compute more efficient.

This addresses the stationarity concern: we don't claim weights are universal - we claim the *existence of a tradeoff surface* that can be empirically mapped per domain. For code: map the surface. For language: map a different surface. The theory predicts the surfaces exist; empirical work finds their shapes.

Novel testable prediction: if you plot iso-performance curves in (compute, Q(D)) space, they should be convex (diminishing returns to both dimensions). This is testable with existing benchmarks by training models at different (compute budget, quality level) combinations.

**Key Points:**
- Reframe as data-compute tradeoff frontier (Pareto optimality analogy)
- Q(D) as compute efficiency multiplier, not additive term
- Theory predicts tradeoff surface exists; empirical work maps domain-specific shapes
- Testable: iso-performance curves in (compute, Q(D)) space should be convex

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Reframing data quality as compute efficiency multiplier and mapping tradeoff frontiers represents paradigm shift from traditional scaling laws. Information-theoretic foundation and Pareto optimality analogy bring fresh perspective to FM data curation theory.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Hypothesis generates clear testable predictions (convex iso-performance curves, >20% variance explained by quality, power-law relationships in ablation studies). Operational Q(D) definition via measurable proxies enables reproducible experiments with existing benchmarks.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Shifts field from "scale everything" to quality-aware resource allocation. Enables cost-benefit analysis of curation vs compute. Opens research direction for domain-specific tradeoff surface mapping. Addresses critical gap in theoretical guidance for billion-dollar pretraining decisions.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE
- **Assessment:** Information-theoretic foundation mathematically sound. Measurable using existing metrics (perplexity, dedup ratio, domain diversity) and testable with existing benchmarks (MMLU, HellaSwag). Challenge: requires extensive ablation studies across scales to validate stationarity assumption. Composite Q(D) is theoretically justified approximation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

Foundation model performance follows a data-compute tradeoff relationship where data quality Q(D) acts as a compute efficiency multiplier. For a fixed performance target, there exists a Pareto frontier of (data quality, compute) combinations, where higher Q(D) reduces required compute. Data quality can be operationalized as a learnable scalar projection from multi-dimensional metrics (deduplication ratio, domain diversity, perplexity-based scoring, token efficiency), with weights fitted from validation performance. The hypothesis predicts: (1) iso-performance curves in (compute, Q(D)) space are convex, showing diminishing returns; (2) quality variance explains >20% of performance beyond model size and compute; (3) systematic quality variations (dedup levels, mixing ratios, filter thresholds) yield power-law performance relationships. This framework transforms data curation from heuristic trial-and-error into theoretically-grounded resource allocation, enabling a priori cost-benefit analysis of filtering strategies vs training compute.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Stationarity assumption:** Q(D) composition may vary across model scales (1B vs 100B) and domains (code vs language). Needs cross-scale validation.
- **Linear combinability:** Assumes quality dimensions combine linearly without interactions. Non-linear effects (dedup helpful at small scale, harmful at large) could break scalar Q(D).
- **Domain generalization:** Optimal weights for Q(D) may be domain-specific, limiting universal applicability.
- **Mitigation Strategy:** Map domain-specific tradeoff surfaces empirically. Theory predicts surfaces exist; doesn't claim universal weights. Test stationarity explicitly by comparing Q(D) fits across 1B/7B/30B scales.

---

