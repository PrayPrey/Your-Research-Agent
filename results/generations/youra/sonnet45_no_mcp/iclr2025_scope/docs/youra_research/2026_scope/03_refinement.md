# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-19T06:32:15Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: Gap-1
- **Gap Title**: Unified Optimization Framework for Efficiency-Adaptability Trade-offs
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All criteria met — specific mechanism stated, testable predictions with quantitative success criteria, novelty articulated with differentiation, feasibility confirmed, objections addressed

### Key Insights
- Efficiency-adaptability trade-off can be formalized as a navigable optimization space rather than a fixed compromise
- Task heterogeneity is a necessary precondition; routing adds no value when H < H_crit
- Systems-level feasibility requires adapter-specific batching to maintain throughput efficiency
- Effect size must be grounded in empirically measured oracle ceiling, not assumed

### Breakthrough Moments
- **Exchange 5 (Dr. Ally)**: Refined claim from "strict Pareto dominance" to "expected hypervolume improvement over fixed configurations"
- **Exchange 6 (Prof. Vera)**: Formalized hypothesis as expectation over task distribution with statistical rigor
- **Exchange 10 (Prof. Vera)**: Introduced Wasserstein uncertainty sets for distributional robustness
- **Exchange 12 (Prof. Rex)**: Demanded oracle ceiling grounding and heterogeneity redefinition to avoid circular reasoning

---

## Final Hypothesis

### Title
**Pareto-Optimal Adaptation Routing (POAR) for Unified Foundation Model Deployment**

### Core Claim
Under persistent-task deployment regimes with batch amortization, if a meta-learned routing policy selects from pre-trained multi-rank adapter pathways based on task meta-features, then expected hypervolume on the performance-efficiency frontier improves by ≥60% of the oracle gap relative to best fixed-rank adapter, because routing exploits non-convex structure in task-conditional trade-off space that fixed configurations cannot navigate.

### Mechanism
During meta-training, K adapter pathways (LoRA ranks {4, 8, 16, 32}) and a lightweight routing classifier are trained jointly on source tasks. At inference time, the routing policy maps task meta-features (embeddings from frozen encoder, few-shot probe performance, domain shift estimates) to adapter selection with O(1) overhead per inference. Tasks are batched by predicted adapter to amortize routing cost and maintain serving efficiency.

**Causal Chain:**
1. **Pathway Diversity**: Multi-rank adapters create discrete points on performance-efficiency Pareto front (O(d·r) parameter scaling)
2. **Routing Learning**: Lightweight classifier (2-layer MLP) learns task-to-adapter mapping during meta-training
3. **Inference Navigation**: Dynamic adapter selection exploits non-convex structure in task-conditional Pareto space
4. **Hypervolume Improvement**: Expected trade-offs better than any single fixed configuration by matching adapters to task characteristics

---

## Predictions

### P1: Primary Effect (Hypervolume Recovery)
**Statement**: POAR recovers ≥60% of empirically measured oracle hypervolume gap G_o = HV(Oracle) - max_r HV(Fixed_r) across multi-domain benchmarks (GLUE, XTREME, domain adaptation) with 95% confidence intervals excluding zero.

**Success Criterion**: 95% CI of (HV(POAR) - max_r HV(Fixed_r)) / G_o includes or exceeds 0.60, with lower bound >0

**Prerequisite**: Pilot study confirms G_o ≥10% for practical significance

### P2: Structural Mechanism
**Statement**: Oracle gain G_o increases monotonically with task heterogeneity H = (P90(c*) - P10(c*)) / Median(c*), while routing regret R grows sublinearly, yielding positive net gain G_o - R over heterogeneity range H ≥ H_crit.

**Success Criterion**: 
- G_o monotonically increasing with p<0.05
- R sublinear growth (slope <1 with CI)
- Net gain positive over H ≥ H_crit
- Permutation test: regret scaling shifts from sublinear to linear when adapter geometry is destroyed

### P3: Robustness
**Statement**: POAR maintains positive worst-case hypervolume improvement over Wasserstein uncertainty ball (ε=0.2, 20% task reweighting) and exhibits Lipschitz-bounded degradation (≤20%) under embedding-space drift within 2σ Mahalanobis distance.

**Success Criterion**: Worst-case hypervolume difference >0 with 95% CI; degradation ≤20% at 2σ distance

---

## Novelty

**Key Innovation**: Task-conditioned inference-time routing over pre-trained adapter pathways (vs static selection at design time or expensive per-task NAS)

**What's New vs Prior Work**:
- **vs Static Adapters (LoRA, prefix tuning)**: Fixed configuration for all tasks → Dynamic routing per task context
- **vs Per-Task NAS**: Expensive search per task (hours-days) → Amortized meta-learned routing policy (O(1) per inference)
- **vs Multi-Objective Optimization**: Optimize fixed model at training → Optimize routing over multiple pre-trained pathways at inference

**Paradigm Contribution**: Shifts from "find best single configuration" to "learn to navigate trade-off space" — enables compositional deployment where single model serves multiple operating points.

---

## Experimental Design

### Datasets
- **GLUE** (9 tasks): Sentiment, NLI, QA, linguistic acceptability
- **XTREME** (40 languages × tasks): Cross-lingual transfer
- **Domain Adaptation**: DomainNet or Office-31 adapted to NLP

### Model
- **Primary**: LLaMA-2-7B
- **Cross-validation**: Mistral-7B, Phi-2

### Baselines
1. **Fixed-Rank LoRA**: Single rank {4,8,16,32} for all tasks (report best as primary baseline)
2. **Per-Task Oracle**: Upper bound with perfect hindsight (defines oracle gap G_o)
3. **Random Routing**: Ablation control (uniform random adapter selection)

### Measurement Protocol
**Phase 0: Pilot Study**
- Measure oracle gap G_o across 3+ multi-domain suites
- Gatekeeper: proceed only if G_o ≥10%

**Phase 1: Heterogeneity Validation**
- Compute heterogeneity H = (P90(c*) - P10(c*)) / Median(c*)
- Determine H_crit via segmented regression with uncertainty bands
- Gatekeeper: proceed only if sufficient tasks with H ≥ H_crit

**Phase 2: POAR Training**
- Meta-train routing on 60% tasks, validate 20%, test 20%
- Stratified splits ensure task diversity

**Phase 3: Hypervolume Evaluation**
- Compare POAR vs fixed-best vs oracle
- Bootstrap confidence intervals for hypervolume differences
- Power analysis: 20-25 tasks per condition (CV~0.2, 80% power, α=0.05)

**Phase 4: Robustness Tests**
- Wasserstein reweighting (ε=0.2)
- Embedding-space drift (Mahalanobis distances 1σ, 2σ, 3σ via cross-lingual tasks)
- Permutation ablation (destroy adapter geometry)

**Phase 5: Systems Profiling**
- Measure throughput (tokens/sec) and P99 latency under Poisson load
- Batch sizes {1,4,16,32}, underloaded to saturated regimes
- Compare static vs dynamic adapter batching

---

## Limitations

### Scope Boundaries

**Applies to**:
- Persistent-task deployments (SaaS, domain-specific services, enterprise ML)
- Heterogeneous task distributions with H ≥ H_crit (~0.25-0.30)
- Batch-serving infrastructure (vLLM, TensorRT-LLM)
- Adapter-based fine-tuning (LoRA, prefix, adapter layers)

**Does NOT apply to**:
- Ephemeral single-query scenarios (one-shot chatbot, isolated API calls)
- Low-heterogeneity distributions (all tasks prefer similar adapters)
- Zero-shot tasks beyond training convex hull (>2σ Mahalanobis distance)
- Strict latency SLAs intolerant of 10-30% P99 degradation

### Known Constraints
- Effectiveness depends on sufficient task heterogeneity (gatekeeper H ≥ H_crit)
- Generalization limited to interpolation regime; extrapolation may fail
- Systems benefits assume efficient dynamic batching infrastructure
- Current formulation focuses on LoRA rank; multi-axis scaling (rank × placement × sparsity) requires hierarchical routing

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met: specific mechanism, testable predictions, novelty, feasibility, objections addressed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (concerns mitigated through pre-registered experimental protocols) |

---

## Success Criteria Summary

✅ **Effect Size**: POAR recovers ≥60% of oracle gap G_o (pilot confirms G_o ≥10%)  
✅ **Heterogeneity**: Task distribution exhibits H ≥ H_crit (~0.25-0.30)  
✅ **Statistical Power**: 95% CI excludes zero; adequately powered (20-25 tasks)  
✅ **Routing Overhead**: ≤10% of lowest-rank adapter inference time  
✅ **Batching Efficiency**: ≤30% loss at P99 latency  
✅ **Throughput**: Statistically significant improvement (p<0.05, KS test)  
✅ **Robustness**: Positive worst-case over Wasserstein ball (ε=0.2); ≤20% degradation at 2σ drift  
✅ **Structural**: Sublinear regret growth; permutation test validates geometric mechanism  

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
