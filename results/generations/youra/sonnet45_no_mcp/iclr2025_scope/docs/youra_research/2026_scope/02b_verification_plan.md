---
stepsCompleted: [step-00, step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08, step-09, step-10]
pipeline_project_title: "Anonymous Pipeline: Scalable Optimization for Efficient Foundation Models"
hypothesis_id: H-POAR-v1
research_mode: incremental
date: 2026-04-19
total_hypotheses: 7
total_duration_weeks: 8
status: complete
completedAt: 2026-04-19T06:34:00Z
---

# Verification Plan: Pareto-Optimal Adaptation Routing (POAR)

**Date:** 2026-04-19
**Hypothesis ID:** H-POAR-v1
**Confidence:** 0.8
**Total Hypotheses:** 7

---

## 0. Established Facts & Scope Reduction

### Claims Registry

| Claim | Status | Evidence |
|-------|--------|----------|
| LoRA adapters with different ranks have fundamentally different expressiveness-efficiency profiles (O(d·r) parameters) | BUILD_ON | Well-established parameter efficiency scaling in adapter literature |
| Multi-domain benchmarks (GLUE, XTREME) exhibit heterogeneous task characteristics | BUILD_ON | Existing benchmark diversity in language, domain, complexity |
| Foundation model deployment currently requires choosing single fixed configuration at design time | BUILD_ON | Current practice: separate checkpoints for edge vs cloud vs specialized deployments |

**Scope Reduction:** 0% (all claims are BUILD_ON - focus verification on novel routing mechanism)

**Phase 2B-4 Instructions:** Focus experimental validation on the novel routing mechanism, not on re-proving adapter efficiency or benchmark diversity.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under persistent-task deployment regimes with batch amortization, if a meta-learned routing policy selects from pre-trained multi-rank adapter pathways based on task meta-features, then expected hypervolume on the performance-efficiency frontier improves by ≥60% of the oracle gap relative to best fixed-rank adapter, because routing exploits non-convex structure in task-conditional trade-off space that fixed configurations cannot navigate.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in expected hypervolume between POAR routing and the best single fixed-rank adapter configuration across heterogeneous task distributions.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-Domain Benchmark Suite (standard) | Provides heterogeneous task distribution with diverse domains, languages, and complexity levels needed to test heterogeneity-dependent routing |
| **Model** | LLaMA-2-7B | Standard foundation model with well-studied adapter behavior, sufficient capacity for multi-domain fine-tuning |

**Dataset Details:**
- Source: GLUE (9 tasks), XTREME (40 languages × tasks), Domain Adaptation (DomainNet/Office-31 adapted)
- Path: HuggingFace datasets: glue, xtreme, custom domain adaptation splits

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Llama-2-7b-hf

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| LoRA (Hu et al., 2021) | Efficient fine-tuning with rank-dependent capacity | Various NLP tasks | Fixed rank configuration cannot adapt to heterogeneous task requirements at deployment |
| Mixture of Experts (MoE) | Learned routing but within single forward pass | Language modeling | Routing during training, not inference-time adaptation across deployment scenarios |
| Neural Architecture Search (NAS) | Per-task optimal architectures | Vision and NLP | High per-task search cost (hours to days) prevents practical deployment-time adaptation |

**Best Baseline Performance:** Best fixed LoRA rank achieves max_r HV(Fixed_r); oracle per-task selection defines upper bound HV(Oracle)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Task heterogeneity H ≥ H_crit is statistically significant | Multi-domain benchmarks exhibit diverse domain shifts, dataset sizes, and task complexities | If H < H_crit, oracle gap G_o is negligible and routing cannot provide meaningful benefit |
| A2 | Task meta-features provide sufficient signal for routing (≥70% accuracy) | Sentence embeddings capture semantic content; few-shot performance correlates with task difficulty | If routing accuracy <70%, regret R dominates oracle gain G_o, yielding negative net benefit |
| A3 | Routing overhead <10% relative to adapter inference cost | 2-layer MLP routing (~1M FLOPs) vs rank-4 adapter (~100M FLOPs per token) is 1:100 ratio | If overhead >10%, efficiency gains are eroded especially in low-compute regime |
| A4 | Adapter-specific batching maintains throughput efficiency | Existing serving frameworks (vLLM, TensorRT-LLM) support dynamic batching with queueing | If batching efficiency loss >30% at P99, deployment throughput degrades despite hypervolume gains |
| A5 | Deployment tasks lie within interpolation regime (≤2σ Mahalanobis distance) | Foundation models typically deploy on tasks similar to training distribution | If extrapolation distance >2σ, routing may degrade catastrophically due to meta-overfitting |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Task-conditioned inference-time routing over pre-trained adapter pathways

**Key Innovation:** Shifts from static adapter selection (fixed at design time) to meta-learned navigation of efficiency-adaptability trade-off space, enabling unified deployment across operating points

**Differentiation:**
- vs. Static adapter selection (LoRA): Fixed configuration for all tasks vs dynamic routing per task
- vs. Per-task NAS: Expensive search per task vs amortized meta-learned routing policy
- vs. Multi-objective optimization in training: Optimize fixed model vs optimize routing policy over multiple pre-trained pathways

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | READY |
| H-M2 | Mechanism | MUST_WORK | H-M1 | READY |
| H-M3 | Mechanism | MUST_WORK | H-M2 | READY |
| H-M4 | Mechanism | DETERMINES_SUCCESS | H-M3 | READY |
| H-C1 | Condition | SHOULD_WORK | H-M4 | READY |
| H-C2 | Condition | SHOULD_WORK | H-M4 | READY |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Oracle Gap Existence

**Statement**: Under multi-domain benchmark evaluation, if tasks exhibit heterogeneous optimal adapter configurations, then oracle gap G_o ≥ 10% exists between per-task oracle and best fixed-rank baseline, because different tasks have fundamentally different performance-efficiency trade-offs.

**Rationale**: This hypothesis validates the fundamental premise that task heterogeneity creates opportunity for adaptive routing. Without sufficient oracle gap, routing cannot provide meaningful benefit over fixed configurations.

**Variables**:
- Independent: Task distribution (GLUE, XTREME, Domain Adaptation)
- Dependent: Oracle gap G_o = HV(Oracle) - max_r HV(Fixed_r)
- Controlled: Base model (LLaMA-2-7B), adapter ranks {4,8,16,32}, training procedure

**Verification Protocol**:
1. Train fixed-rank adapters (ranks 4, 8, 16, 32) on representative task sample (20-25 tasks).
2. Measure hypervolume HV(Fixed_r) for each fixed rank across all tasks.
3. Compute per-task oracle: select best adapter for each task, measure HV(Oracle).
4. Calculate oracle gap: G_o = HV(Oracle) - max_r HV(Fixed_r).
5. Verify G_o ≥ 10% with statistical significance (bootstrap CI).

**Success Criteria** (PoC: Direction-based):
- Primary: Oracle gap G_o ≥ 10% with 95% CI excluding zero
- Secondary: Task heterogeneity H ≥ 0.25 (normalized Pareto-front dispersion)

**Failure Response**:
- IF G_o < 10%: PIVOT to different task distribution or ABANDON (insufficient heterogeneity)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Prediction P1, sh1_existence

---
#### H-M1: Adapter Pathway Diversity

**Statement**: Under meta-training on source tasks, if LoRA adapters with ranks {4,8,16,32} are trained simultaneously, then they create distinct performance-efficiency profiles with O(d·r) parameter scaling, because rank directly controls adapter capacity and computational cost.

**Rationale**: This validates the first causal mechanism step—that diverse adapter pathways exist as discrete points on the Pareto front, providing the substrate for routing decisions.

**Variables**:
- Independent: LoRA rank r ∈ {4, 8, 16, 32}
- Dependent: Performance-efficiency profile (accuracy, FLOPs, latency)
- Controlled: Base model, training procedure, source task distribution

**Verification Protocol**:
1. Train four LoRA adapters (ranks 4, 8, 16, 32) on source tasks using standardized protocol.
2. Measure each adapter's performance (accuracy/F1) and efficiency (FLOPs, latency).
3. Plot performance-efficiency Pareto front with four discrete points.
4. Verify non-linear capacity-cost trade-offs via parameter count O(d·r) analysis.
5. Confirm pathway diversity: coefficient of variation CV > 0.15 across ranks.

**Success Criteria** (PoC: Direction-based):
- Primary: Four adapters create visually distinct Pareto points with non-dominated profiles
- Secondary: Parameter scaling follows O(d·r) with R² > 0.95

**Failure Response**:
- IF adapters have similar profiles: EXPLORE alternative rank ranges or adapter architectures

**Dependencies**: H-E1 (oracle gap must exist)

**Source**: Phase 2A Causal Step 1

---
#### H-M2: Routing Policy Learning

**Statement**: Under meta-training with task meta-features, if a 2-layer MLP classifier maps task embeddings and few-shot probes to optimal adapter selection, then routing accuracy ≥70%, because task meta-features provide sufficient discriminative signal for adapter choice.

**Rationale**: This tests whether the routing mechanism can learn task-to-adapter mapping with acceptable accuracy, validating that meta-features capture relevant task characteristics.

**Variables**:
- Independent: Task meta-features (768-dim SBERT embeddings, few-shot accuracy, domain shift)
- Dependent: Routing classification accuracy
- Controlled: Routing architecture (2-layer MLP), training tasks (60%), validation tasks (20%)

**Verification Protocol**:
1. Extract task meta-features: SBERT embeddings, few-shot probe accuracy, domain shift estimates.
2. Train 2-layer MLP routing classifier on 60% of tasks with oracle labels.
3. Evaluate routing accuracy on held-out 20% validation tasks.
4. Verify routing accuracy ≥70% threshold.
5. Analyze feature importance to confirm meta-features are informative.

**Success Criteria** (PoC: Direction-based):
- Primary: Routing classification accuracy ≥70% on validation set
- Secondary: Feature ablation shows embeddings + few-shot probes are both necessary

**Failure Response**:
- IF accuracy <70%: EXPLORE richer meta-features or hierarchical routing architecture

**Dependencies**: H-M1 (adapter pathways must exist)

**Source**: Phase 2A Causal Step 2, Assumption A2

---
#### H-M3: Inference-Time Navigation with Low Overhead

**Statement**: Under deployment conditions, if routing selects adapters per task using the learned policy, then routing overhead <10% and adapter selection exploits task-conditional Pareto structure, because 2-layer MLP inference is O(1) relative to adapter computation.

**Rationale**: This validates that routing can operate efficiently at inference time without eroding the efficiency gains it aims to provide.

**Variables**:
- Independent: Routing policy activation (enabled vs disabled)
- Dependent: Routing overhead (FLOPs, latency), task-adapter matching quality
- Controlled: Hardware (A100), batch size, serving framework

**Verification Protocol**:
1. Measure baseline inference latency for fixed-rank adapters without routing.
2. Add routing policy inference (2-layer MLP) and measure incremental overhead.
3. Verify routing overhead <10% of total inference time.
4. Confirm adapter-specific batching maintains throughput (queueing simulation).
5. Validate routing exploits non-convex structure via permutation test (randomized adapter IDs should increase regret).

**Success Criteria** (PoC: Direction-based):
- Primary: Routing overhead <10% of adapter inference cost
- Secondary: Permutation test shows statistically significant regret increase (p<0.05)

**Failure Response**:
- IF overhead >10%: PIVOT to batch-level routing or cached meta-features

**Dependencies**: H-M2 (routing policy must be trained)

**Source**: Phase 2A Causal Step 3, Assumption A3

---
#### H-M4: Hypervolume Improvement via Dynamic Routing

**Statement**: Under heterogeneous task deployment, if POAR routing selects adapters dynamically based on task meta-features, then expected hypervolume improves by ≥60% of oracle gap with 95% CI excluding zero, because routing matches adapters to task characteristics better than any fixed configuration.

**Rationale**: This is the primary outcome hypothesis validating that the complete POAR mechanism delivers the claimed performance-efficiency trade-off improvement.

**Variables**:
- Independent: Routing policy (POAR vs best fixed-rank vs oracle)
- Dependent: Expected hypervolume on (performance, efficiency) Pareto front
- Controlled: Test task distribution (20%), base model, evaluation protocol

**Verification Protocol**:
1. Deploy POAR routing on held-out 20% test tasks.
2. Measure per-task performance and efficiency, compute hypervolume HV(POAR).
3. Compare against best fixed-rank baseline: compute improvement (HV(POAR) - max_r HV(Fixed_r)) / G_o.
4. Bootstrap 95% confidence intervals for improvement ratio.
5. Verify improvement ≥60% with CI lower bound >0.

**Success Criteria** (PoC: Direction-based):
- Primary: POAR recovers ≥60% of oracle gap G_o with 95% CI excluding zero
- Secondary: Paired t-test shows HV(POAR) > HV(best_fixed) with p<0.05

**Failure Response**:
- IF improvement <60% or CI includes zero: PIVOT to multi-task meta-learning or EXPLORE different meta-features

**Dependencies**: H-M3 (routing must operate with low overhead)

**Source**: Phase 2A Prediction P1 (primary), Causal Step 4

---
#### H-C1: Heterogeneity Threshold Boundary

**Statement**: Under controlled task distributions with varying heterogeneity H, if oracle gain G_o and routing regret R are measured separately, then net gain (G_o - R) is positive only when H ≥ H_crit, because routing benefits require sufficient task diversity to outweigh selection errors.

**Rationale**: This validates the boundary condition that routing effectiveness depends on task heterogeneity, documenting when the mechanism is applicable vs when fixed configurations suffice.

**Variables**:
- Independent: Task heterogeneity H (controlled via synthetic task mixtures)
- Dependent: Net gain (G_o - R)
- Controlled: Routing policy (trained), evaluation protocol

**Verification Protocol**:
1. Construct synthetic task mixtures with controlled heterogeneity variance σ_H.
2. Measure oracle gain G_o and routing regret R for each mixture.
3. Perform segmented regression to identify H_crit threshold.
4. Verify net gain (G_o - R) > 0 for H ≥ H_crit with statistical significance.
5. Confirm G_o increases monotonically with H (Spearman ρ > 0.7, p<0.05).

**Success Criteria** (PoC: Direction-based):
- Primary: Clear H_crit threshold identified via segmented regression with R² > 0.7
- Secondary: Net gain positive for H ≥ H_crit, negative for H < H_crit

**Failure Response**:
- IF no clear threshold: EXPLORE alternative heterogeneity metrics or DOCUMENT as continuous trade-off

**Dependencies**: H-M4 (routing performance must be measured)

**Source**: Phase 2A Prediction P2, Assumption A1, Scope boundaries

---
#### H-C2: Interpolation Regime Boundary

**Statement**: Under embedding-space drift from training distribution, if test tasks lie within 2σ Mahalanobis distance, then routing performance degrades ≤20%, because meta-learned routing generalizes within the interpolation regime but may fail under extrapolation.

**Rationale**: This validates the generalization boundary, documenting when routing can be safely deployed vs when retraining is required for distribution shift.

**Variables**:
- Independent: Mahalanobis distance from training centroid
- Dependent: Routing performance degradation (relative to in-distribution)
- Controlled: Base model, routing policy (trained), cross-lingual transfer tasks for controlled drift

**Verification Protocol**:
1. Compute training task meta-feature centroid and covariance for Mahalanobis distance.
2. Select cross-lingual transfer tasks at varying distances (0.5σ, 1σ, 1.5σ, 2σ).
3. Measure POAR hypervolume at each distance level.
4. Verify degradation ≤20% at 2σ boundary.
5. Confirm Lipschitz-bounded degradation: linear regression slope with 95% CI.

**Success Criteria** (PoC: Direction-based):
- Primary: Degradation ≤20% at 2σ Mahalanobis distance
- Secondary: No performance cliff within 1σ (degradation <10%)

**Failure Response**:
- IF cliff occurs <2σ: PIVOT to uncertainty-aware routing or DOCUMENT stricter deployment constraints

**Dependencies**: H-M4 (routing performance must be established)

**Source**: Phase 2A Prediction P3, Assumption A5, Scope boundaries

---

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Insufficient Task Heterogeneity | A1 | H-E1, H-C1 | High |
| R2: Weak Meta-Feature Signal | A2 | H-M2, H-M4 | High |
| R3: Excessive Routing Overhead | A3 | H-M3, H-M4 | Medium |
| R4: Batching Efficiency Loss | A4 | H-M3, H-M4 | Medium |
| R5: Distribution Shift Fragility | A5 | H-C2, All H-M | Medium |

### 3.2 Mitigation Strategies

**Risk R1: Insufficient Task Heterogeneity**

**Source Assumption:** A1 - Task heterogeneity H ≥ H_crit is statistically significant

**Description:** If the multi-domain benchmark tasks do not exhibit sufficient heterogeneity in optimal adapter configurations (H < H_crit), the oracle gap G_o will be negligible (<10%), eliminating the opportunity for routing to provide meaningful benefit over fixed configurations.

**Affected Hypotheses:** H-E1 (Oracle Gap Existence), H-C1 (Heterogeneity Threshold)

**Severity:** High (threatens fundamental premise)

**Mitigation Strategy:**
1. **Prevention:** Pre-screen task distribution with pilot oracle gap study before full experiments; ensure task mix includes diverse domains (GLUE sentence-level, XTREME cross-lingual, domain adaptation visual grounding)
2. **Detection:** Measure normalized Pareto-front dispersion H during H-E1 verification; flag if H < 0.25 or G_o < 10%
3. **Response:**
   - PIVOT: Expand to broader task distribution (add code generation, math reasoning, multi-modal tasks)
   - SCOPE: Focus on high-heterogeneity task subsets identified in pilot
   - ABORT: If even expanded distribution shows H < H_crit, document as negative result (routing not beneficial for this task family)

**Early Warning Indicators:**
- Pilot study shows G_o < 10% across multiple task samples
- Fixed-rank adapters achieve similar hypervolume (variance <5%)
- Per-task oracle selections show no clear pattern (entropy low)

---

**Risk R2: Weak Meta-Feature Signal**

**Source Assumption:** A2 - Task meta-features provide sufficient signal for routing (≥70% accuracy)

**Description:** If task meta-features (SBERT embeddings, few-shot probes, domain shift) lack discriminative power, routing classification accuracy will fall below 70%, causing routing regret R to dominate oracle gain G_o and yielding negative net benefit.

**Affected Hypotheses:** H-M2 (Routing Policy Learning), H-M4 (Hypervolume Improvement)

**Severity:** High (threatens mechanism viability)

**Mitigation Strategy:**
1. **Prevention:** Validate meta-feature quality with unsupervised clustering (silhouette score >0.3) and supervised probing (logistic regression baseline >60%) before training full routing policy
2. **Detection:** Monitor routing validation accuracy during H-M2; flag if accuracy plateaus <70% after hyperparameter search
3. **Response:**
   - PIVOT: Augment meta-features with task-specific probes (gradient norms, activation statistics, attention entropy)
   - EXPLORE: Hierarchical routing with coarse-to-fine decision tree
   - ABORT: If augmented features still yield <70% accuracy, document as insufficient signal for current feature set

**Early Warning Indicators:**
- Feature ablation shows no single feature contributes >10% accuracy
- Confusion matrix shows routing treats all adapters similarly (uniform distribution)
- Validation accuracy gap vs training accuracy >15% (overfitting to noise)

---

**Risk R3: Excessive Routing Overhead**

**Source Assumption:** A3 - Routing overhead <10% relative to adapter inference cost

**Description:** If 2-layer MLP routing inference, meta-feature computation, or adapter switching introduces >10% overhead, efficiency gains will be eroded especially in the low-compute regime (rank-4 adapters), undermining the performance-efficiency trade-off.

**Affected Hypotheses:** H-M3 (Inference-Time Navigation), H-M4 (Hypervolume Improvement)

**Severity:** Medium (degrades but doesn't invalidate mechanism)

**Mitigation Strategy:**
1. **Prevention:** Profile routing components separately (meta-feature extraction, MLP inference, adapter loading); optimize hotspots before H-M3 verification
2. **Detection:** Measure end-to-end latency with vs without routing; calculate overhead percentage for each adapter rank
3. **Response:**
   - PIVOT: Cache meta-features for persistent tasks (assumption already scopes to persistent-task regimes)
   - SCOPE: Deploy routing only for medium/high-rank adapters (8-32) where overhead ratio is favorable
   - EXPLORE: Batch-level routing (select adapter per batch instead of per task) to amortize overhead

**Early Warning Indicators:**
- Meta-feature extraction takes >5ms per task (vs 50-100ms adapter inference)
- MLP inference >1ms (should be <0.5ms for 2-layer network)
- Adapter loading/switching introduces memory bottleneck (>10ms)

---

**Risk R4: Batching Efficiency Loss**

**Source Assumption:** A4 - Adapter-specific batching maintains throughput efficiency

**Description:** If dynamic adapter selection disrupts batching efficiency (tasks requiring different adapters cannot be batched together), P99 latency may increase >30% under load, degrading deployment throughput despite hypervolume gains on per-task basis.

**Affected Hypotheses:** H-M3 (Inference-Time Navigation), H-M4 (Hypervolume Improvement)

**Severity:** Medium (systems-level constraint, not mechanism failure)

**Mitigation Strategy:**
1. **Prevention:** Implement adapter-specific queueing with vLLM or TensorRT-LLM dynamic batching; validate queueing simulation shows <30% P99 degradation before deployment
2. **Detection:** Profile P99 latency under Poisson load with routing enabled vs disabled; measure queue depths per adapter
3. **Response:**
   - PIVOT: Hybrid policy—use routing for throughput-tolerant tasks, fixed adapter for latency-critical tasks
   - SCOPE: Document as SLA trade-off—routing improves average-case efficiency but relaxes P99 guarantees
   - EXPLORE: Predictive batching—group incoming tasks by predicted adapter before routing

**Early Warning Indicators:**
- Queue depth variance >3x between adapters (load imbalance)
- P99 latency increases >30% under 80% load
- Throughput degradation >20% compared to fixed-adapter baseline

---

**Risk R5: Distribution Shift Fragility**

**Source Assumption:** A5 - Deployment tasks lie within interpolation regime (≤2σ Mahalanobis distance)

**Description:** If deployment tasks fall outside the training meta-feature distribution (>2σ Mahalanobis distance), routing may degrade catastrophically due to meta-overfitting, selecting suboptimal adapters with high confidence.

**Affected Hypotheses:** H-C2 (Interpolation Regime Boundary), All H-M hypotheses

**Severity:** Medium (boundary condition, not core mechanism)

**Mitigation Strategy:**
1. **Prevention:** Validate deployment task distribution during initial rollout; compute Mahalanobis distances and flag outliers >2σ
2. **Detection:** Monitor routing confidence scores and performance metrics; detect degradation via online A/B test (POAR vs fixed baseline)
3. **Response:**
   - PIVOT: Implement uncertainty-aware routing—fall back to fixed best-rank adapter when meta-feature distance >2σ
   - SCOPE: Document deployment constraints—routing requires periodic retraining when distribution drifts
   - EXPLORE: Continual meta-learning—incrementally update routing policy with deployment feedback

**Early Warning Indicators:**
- Mahalanobis distance monitoring shows >10% of tasks exceed 2σ
- Routing confidence scores decrease but accuracy doesn't (calibration failure)
- Performance cliff detected in cross-lingual transfer tasks

---

### 3.3 Baseline Failure Patterns

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| LoRA: Fixed rank cannot adapt to heterogeneous tasks | Core premise validated by R1 mitigation | H-E1 verifies heterogeneity exists |
| MoE: Routing during training, not inference-time | Misalignment with deployment needs | H-M3 validates inference-time routing overhead is acceptable |
| NAS: High per-task search cost (hours-days) | Amortization assumption critical | Scope already limits to persistent-task regimes |

### 3.4 Risk Summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Insufficient Task Heterogeneity | A1 | High | H-E1, H-C1 | Pilot oracle gap study, expand task distribution |
| R2 | Weak Meta-Feature Signal | A2 | High | H-M2, H-M4 | Validate feature quality, augment with probes |
| R3 | Excessive Routing Overhead | A3 | Medium | H-M3, H-M4 | Profile and optimize, cache meta-features |
| R4 | Batching Efficiency Loss | A4 | Medium | H-M3, H-M4 | Adapter-specific queueing, hybrid policy |
| R5 | Distribution Shift Fragility | A5 | Medium | H-C2, All H-M | Monitor Mahalanobis distance, uncertainty-aware routing |

**Risk Distribution:**
- Critical: 0
- High: 2 (R1, R2)
- Medium: 3 (R3, R4, R5)
- Low: 0

**Critical Path Risks:** R1 and R2 must be mitigated in H-E1 and H-M2 respectively; failure triggers PIVOT/ABORT decisions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════════
           DEPENDENCY GRAPH (DAG) - 7 Hypotheses
═══════════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────────────────────────┐
    │  H-E1: Oracle Gap Existence                             │
    │  Gate: MUST_WORK                                        │
    │  Test: Verify G_o ≥ 10% across multi-domain benchmarks │
    └─────────────────────────────────────────────────────────┘
                           │
                           ▼
[Level 1 - Mechanism Chain Start]
    ┌─────────────────────────────────────────────────────────┐
    │  H-M1: Adapter Pathway Diversity                        │
    │  Gate: MUST_WORK                                        │
    │  Prerequisite: H-E1                                     │
    └─────────────────────────────────────────────────────────┘
                           │
                           ▼
[Level 2 - Routing Learning]
    ┌─────────────────────────────────────────────────────────┐
    │  H-M2: Routing Policy Learning                          │
    │  Gate: MUST_WORK                                        │
    │  Prerequisite: H-M1                                     │
    └─────────────────────────────────────────────────────────┘
                           │
                           ▼
[Level 3 - Inference Navigation]
    ┌─────────────────────────────────────────────────────────┐
    │  H-M3: Inference-Time Navigation with Low Overhead      │
    │  Gate: SHOULD_WORK                                      │
    │  Prerequisite: H-M2                                     │
    └─────────────────────────────────────────────────────────┘
                           │
                           ▼
[Level 4 - Primary Outcome]
    ┌─────────────────────────────────────────────────────────┐
    │  H-M4: Hypervolume Improvement via Dynamic Routing      │
    │  Gate: DETERMINES_SUCCESS                               │
    │  Prerequisite: H-M3                                     │
    └─────────────────────────────────────────────────────────┘
                           │
                     ┌─────┴─────┐
                     ▼           ▼
[Level 5 - Boundary Conditions]
    ┌──────────────────────────┐  ┌──────────────────────────┐
    │  H-C1: Heterogeneity     │  │  H-C2: Interpolation     │
    │  Threshold Boundary      │  │  Regime Boundary         │
    │  Gate: SHOULD_WORK       │  │  Gate: SHOULD_WORK       │
    │  Prerequisite: H-M4      │  │  Prerequisite: H-M4      │
    └──────────────────────────┘  └──────────────────────────┘

═══════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Optional Extensions: H-C1, H-C2 (document scope boundaries)
═══════════════════════════════════════════════════════════════════════
```

### 4.1 Verification Phases with Gate Conditions

**Phase 1 - Foundation (Level 0)**
| Hypothesis | Test | Gate | Failure Action |
|------------|------|------|----------------|
| H-E1 | Oracle gap G_o ≥ 10% exists | MUST_WORK | ABORT: Insufficient heterogeneity for routing benefit |

→ **Gate 1 Decision**: If H-E1 fails (G_o < 10%), STOP verification and reassess hypothesis premise.

---

**Phase 2 - Mechanism Chain (Levels 1-4)**
| Hypothesis | Dependencies | Gate | Failure Action |
|------------|--------------|------|----------------|
| H-M1 | H-E1 | MUST_WORK | PIVOT: Explore alternative adapter architectures |
| H-M2 | H-M1 | MUST_WORK | PIVOT: Augment meta-features or hierarchical routing |
| H-M3 | H-M2 | SHOULD_WORK | SCOPE: Batch-level routing or cache meta-features |
| H-M4 | H-M3 | DETERMINES_SUCCESS | PIVOT: Multi-task meta-learning or richer features |

→ **Gate 2 Decision Points**:
- H-M1 failure: Adapter pathways lack diversity → explore different rank ranges
- H-M2 failure: Meta-features insufficient → augment with task-specific probes
- H-M3 overhead >10%: Acceptable if H-M4 still shows net benefit
- H-M4 < 60% oracle gap recovery: Major concern, triggers PIVOT

---

**Phase 2.5 - Boundary Conditions (Level 5)** *Optional - scope documentation*
| Hypothesis | Dependencies | Gate | Failure Action |
|------------|--------------|------|----------------|
| H-C1 | H-M4 | SHOULD_WORK | DOCUMENT: Routing benefits continuous, not thresholded |
| H-C2 | H-M4 | SHOULD_WORK | SCOPE: Deployment requires <2σ drift monitoring |

→ **Gate 2.5 Decision**: Condition failures narrow applicability scope but don't invalidate core mechanism.

### 4.2 Dependency Hierarchy Table

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type | Parallel |
|-------|------------|---------------|-----------|----------|
| 0 | H-E1 | None | MUST_WORK | - |
| 1 | H-M1 | H-E1 | MUST_WORK | - |
| 2 | H-M2 | H-M1 | MUST_WORK | - |
| 3 | H-M3 | H-M2 | SHOULD_WORK | - |
| 4 | H-M4 | H-M3 | DETERMINES_SUCCESS | - |
| 5 | H-C1 | H-M4 | SHOULD_WORK | Yes (with H-C2) |
| 5 | H-C2 | H-M4 | SHOULD_WORK | Yes (with H-C1) |

**Parallelization Opportunities:**
- Level 5: H-C1 and H-C2 can be verified in parallel (both depend only on H-M4)

**Sequential Constraints:**
- Levels 0-4 must be strictly sequential (each depends on previous)
- Critical path length: 5 levels (H-E1 → H-M1 → H-M2 → H-M3 → H-M4)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 5. Timeline Planning (Gantt)

```
═══════════════════════════════════════════════════════════════════════════════════
                    VERIFICATION TIMELINE - 7 Hypotheses
═══════════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │ W8      │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1 (Oracle Gap) │ ████████│         │         │         │         │         │
  [Gate 1] ◆        │         │ ◆       │         │         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanism Chain
  H-M1 (Pathways)   │         │ ████████│         │         │         │         │
  H-M2 (Routing)    │         │         │ ████    │         │         │         │
  H-M3 (Navigation) │         │         │         │ ████    │         │         │
  H-M4 (Hypervolume)│         │         │         │         │ ████    │         │
  [Gate 2] ◆        │         │         │         │         │         │ ◆       │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2.5: Boundary Conditions
  H-C1 (Hetero Thr.)│         │         │         │         │         │ ████    │
  H-C2 (Interp Reg.)│         │         │         │         │         │ ████    │
  [Gate 2.5] ◆      │         │         │         │         │         │         │◆
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 (6 weeks minimum)
Parallel: H-C1 || H-C2 (Week 8, saves 1 week)
═══════════════════════════════════════════════════════════════════════════════════
```

### 5.1 Critical Path Analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Critical Path**: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration**: 8 weeks
  - Phase 1 (Foundation): 2 weeks (H-E1)
  - Phase 2 (Mechanism Chain): 4 weeks (H-M1: 2 weeks, H-M2/M3/M4: 1 week each)
  - Phase 2.5 (Boundary Conditions): 2 weeks (H-C1 || H-C2: 1 week parallel)

**Duration Formula**: 2 (H-E1) + 1 + (4-1) + 1 (H-C parallel) = 8 weeks

**Slack Available**: 
  - Critical path (H-E1 → H-M4): 0 weeks slack
  - H-C1, H-C2: Can execute in parallel, saving 1 week vs sequential

**Gate Decision Points**:
  - **Gate 1 (Week 2)**: MUST_WORK - If H-E1 fails (G_o < 10%), ABORT entire hypothesis
  - **Gate 2 (Week 6)**: DETERMINES_SUCCESS - If H-M4 < 60% oracle gap, PIVOT to alternative approaches
  - **Gate 2.5 (Week 8)**: SHOULD_WORK - If H-C fails, narrow scope but mechanism still valid

**Duration Comparison**:
  - Minimum viable path (H-E1 → H-M1 → H-M2): 4 weeks (PoC smoke test)
  - Full mechanism chain (H-E1 → H-M4): 6 weeks (core hypothesis validation)
  - Complete verification (including conditions): 8 weeks (comprehensive)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.2 Resource Summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total Hypotheses**: 7
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
  - Condition: 2 (H-C1, H-C2)

**Verification Phases**: 3
  1. Foundation (H-E1): Validates oracle gap exists
  2. Mechanisms (H-M1-4): Tests complete causal chain
  3. Boundary Conditions (H-C1-2): Documents scope limits

**Total Duration**: 8 weeks
**Critical Path Length**: 6 weeks (H-E1 → H-M4)
**Execution Mode**: Sequential chain with parallel conditions

**Computational Resources** (8×A100 GPU cluster):
  - H-E1: Pilot oracle study (20-25 tasks, 4 ranks) - 2 weeks
  - H-M1: Train adapter pathways - 2 weeks
  - H-M2: Meta-learn routing policy - 1 week
  - H-M3: Profile inference overhead - 1 week  
  - H-M4: Full evaluation on test set - 1 week
  - H-C1/C2: Controlled heterogeneity & drift tests - 1 week each (parallel)

**Checkpoint Strategy**:
  - After H-E1: Save oracle gap measurements, per-task optimal configs
  - After H-M1: Save trained adapters (4 ranks)
  - After H-M2: Save routing policy weights
  - After H-M4: Save final evaluation metrics for Phase 5 comparison

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.3 Execution Order

**Verification Roadmap** (Week-by-Week):

**Weeks 1-2: Foundation Phase**
  - **Step 1**: Execute H-E1 (Oracle Gap Existence)
    - Train fixed-rank adapters (ranks 4, 8, 16, 32) on 20-25 representative tasks
    - Measure per-task hypervolume for each rank
    - Compute oracle gap G_o = HV(Oracle) - max_r HV(Fixed_r)
    - Verify G_o ≥ 10% with bootstrap 95% CI
  - **Step 2**: Evaluate Gate 1 (MUST_WORK)
    - **If PASS**: Oracle gap exists, proceed to mechanism verification
    - **If FAIL**: ABORT - insufficient heterogeneity, hypothesis premise invalid

**Weeks 3-4: Mechanism Chain Start**
  - **Step 3**: Execute H-M1 (Adapter Pathway Diversity)
    - Meta-train four adapters with standardized protocol
    - Verify O(d·r) parameter scaling, non-dominated Pareto profiles
    - Confirm pathway diversity CV > 0.15

**Week 5: Routing Learning**
  - **Step 4**: Execute H-M2 (Routing Policy Learning)
    - Extract task meta-features (SBERT embeddings, few-shot probes, domain shift)
    - Train 2-layer MLP routing classifier on 60% source tasks
    - Validate routing accuracy ≥70% on 20% validation tasks
    - **If FAIL**: PIVOT to augmented meta-features

**Week 6: Inference Navigation**
  - **Step 5**: Execute H-M3 (Inference-Time Navigation)
    - Profile routing overhead (meta-feature extraction, MLP inference, adapter loading)
    - Verify overhead <10% of adapter inference cost
    - Test adapter-specific batching efficiency under load

**Week 7: Primary Outcome**
  - **Step 6**: Execute H-M4 (Hypervolume Improvement)
    - Deploy POAR on held-out 20% test tasks
    - Measure HV(POAR) and compare against best fixed-rank baseline
    - Verify (HV(POAR) - max_r HV(Fixed_r)) / G_o ≥ 0.60 with 95% CI
  - **Step 7**: Evaluate Gate 2 (DETERMINES_SUCCESS)
    - **If PASS**: Core mechanism validated, proceed to boundary conditions
    - **If FAIL**: PIVOT to multi-task meta-learning or richer meta-features

**Week 8: Boundary Conditions** (Parallel Execution)
  - **Step 8a**: Execute H-C1 (Heterogeneity Threshold) *in parallel*
    - Construct synthetic task mixtures with controlled heterogeneity H
    - Measure G_o and routing regret R separately
    - Identify H_crit via segmented regression
  - **Step 8b**: Execute H-C2 (Interpolation Regime) *in parallel*
    - Select cross-lingual transfer tasks at 0.5σ, 1σ, 1.5σ, 2σ distances
    - Measure performance degradation vs in-distribution
    - Verify degradation ≤20% at 2σ boundary
  - **Step 9**: Evaluate Gate 2.5 (SHOULD_WORK)
    - **If PASS**: Scope boundaries documented, deployment constraints clear
    - **If FAIL**: Narrow applicability scope but core mechanism remains valid

**Final**: Verification complete, proceed to Phase 4 (Implementation) or Phase 5 (Baseline Comparison)

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim**: Under persistent-task deployment regimes with batch amortization, meta-learned routing over pre-trained multi-rank adapter pathways improves expected hypervolume by ≥60% of oracle gap because routing exploits non-convex structure in task-conditional trade-off space that fixed configurations cannot navigate.

**Supporting Evidence:**
1. **Causal Mechanism**: Four-step mechanism validated through prior adapter literature (O(d·r) scaling), task embedding discriminability, serving framework capabilities, and multi-objective optimization theory
2. **Key Assumptions**: Grounded in empirical adapter behavior (A1-A2), computational analysis (A3), infrastructure capabilities (A4), and standard ML generalization theory (A5)
3. **Testable Predictions**: Quantitative thresholds with statistical rigor (60% oracle gap recovery, ≥70% routing accuracy, <10% overhead, 95% CI requirements)

**Strengths:**
- **Established Foundation**: Builds on well-validated LoRA adapter theory and multi-domain benchmark diversity (BUILD_ON claims)
- **Clear Causal Chain**: Four-step mechanism with specific falsifiers at each step, enabling precise failure diagnosis
- **Statistical Rigor**: Pre-registered thresholds, bootstrap confidence intervals, permutation tests for structural validation
- **Scope Honesty**: Explicitly documents applicability boundaries (persistent-task regimes, H ≥ H_crit, ≤2σ interpolation)
- **Gate-Based Validation**: Sequential hypothesis testing allows early detection of fundamental failures

**Expected Outcomes:**
- **Primary (P1)**: POAR recovers ≥60% of oracle gap G_o with 95% CI excluding zero (prerequisite: G_o ≥10%)
- **Secondary (P2)**: Oracle gain G_o increases monotonically with heterogeneity H; routing regret R grows sublinearly
- **Tertiary (P3)**: Worst-case hypervolume positive under Wasserstein perturbations (ε=0.2); degradation ≤20% at 2σ drift

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6.2 Antithesis Development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0)**: There is no significant difference in expected hypervolume between POAR routing and the best single fixed-rank adapter configuration across heterogeneous task distributions.

**Counter-Arguments:**

1. **Insufficient Task Heterogeneity**
   - Multi-domain benchmarks may exhibit homogeneous optimal adapter preferences despite surface-level diversity
   - Oracle gap G_o may be <10%, making routing benefit negligible relative to complexity cost
   - Fixed-rank adapters already near Pareto-optimal, leaving little room for improvement

2. **Meta-Feature Signal Weakness**
   - Task embeddings may capture superficial semantic similarity without predicting optimal adapter rank
   - Few-shot probes may be noisy indicators, leading to routing accuracy <70% and high regret
   - Routing errors compound: 30% misclassification rate × 4 adapters = significant performance degradation

3. **Systems-Level Overhead Dominates**
   - Routing overhead (meta-feature extraction, MLP inference, adapter switching) may exceed 10% especially for efficient rank-4 adapters
   - Adapter-specific batching may fragment workload, increasing P99 latency >30% and degrading serving throughput
   - Fixed configurations avoid overhead entirely, maintaining predictable SLAs

4. **Baseline Sufficiency**
   - Best fixed-rank adapter (e.g., rank-16) may already balance performance and efficiency adequately for most tasks
   - Per-task NAS cost (hours) amortizes over deployment lifetime if task distribution is stable
   - MoE already provides routing within training; inference-time routing adds little value

**Potential Failure Points:**
- **R1 (High Severity)**: If H < H_crit, oracle gap collapses and routing provides no benefit over fixed baseline
- **R2 (High Severity)**: If routing accuracy <70%, regret R > oracle gain G_o, yielding negative net benefit
- **R3-R4 (Medium Severity)**: If overhead >10% or batching loss >30%, efficiency gains eroded

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: Oracle gap G_o < 10% with 95% CI including zero
- H-M2 fails: Routing classification accuracy <70% despite meta-feature augmentation
- H-M4 fails: POAR recovers <60% of oracle gap, or 95% CI lower bound ≤0
- Permutation test shows no structural benefit: randomized adapter IDs yield similar regret to learned routing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6.3 Synthesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment:**

The hypothesis H-POAR-v1 presents a testable claim that meta-learned routing over pre-trained adapter pathways can improve performance-efficiency trade-offs by exploiting task heterogeneity. The thesis draws on established adapter theory and proposes a novel inference-time navigation mechanism. However, the null hypothesis raises valid concerns: task heterogeneity may be insufficient (G_o < 10%), meta-features may lack discriminative power (accuracy <70%), or systems overhead may dominate efficiency gains.

**Resolution Path:**

The verification plan addresses this dialectic through a gate-based sequential testing strategy:

1. **Foundation Verification (H-E1)**: Establishes oracle gap G_o ≥ 10% before investing in mechanism. If H-E1 fails, antithesis supported immediately—task heterogeneity insufficient for routing benefit.

2. **Sequential Mechanism Testing (H-M1-M4)**: Tests each causal step with specific falsifiers:
   - H-M1 validates adapter pathway diversity exists (Pareto non-dominance)
   - H-M2 validates meta-features provide routing signal (≥70% accuracy threshold)
   - H-M3 validates overhead is acceptable (<10% threshold)
   - H-M4 validates end-to-end benefit (≥60% oracle gap recovery)

3. **Structural Validation**: Permutation test distinguishes learned routing structure from random selection, directly addressing H0's claim of "no significant difference."

4. **Boundary Condition Documentation (H-C1-C2)**: Tests heterogeneity threshold and interpolation regime, defining applicability scope rather than claiming universal benefit.

**Conditions for Thesis Support:**
- H-E1 passes: G_o ≥ 10% (gatekeeper criterion)
- H-M1-M2 pass: Adapter diversity exists and routing learns task-to-adapter mapping accurately
- H-M4 passes: POAR recovers ≥60% of G_o with 95% CI excluding zero
- Permutation test confirms structural benefit (p<0.05)

**Conditions for Antithesis (H0) Support:**
- H-E1 fails: Oracle gap G_o < 10%, indicating insufficient heterogeneity
- H-M2 fails: Routing accuracy <70% despite meta-feature augmentation, indicating weak signal
- H-M4 fails: Improvement <60% of G_o or 95% CI includes zero, indicating no statistically significant benefit
- Permutation test shows no structural effect, indicating routing is no better than random selection

**Nuanced Outcome Possibilities:**

1. **Full Thesis Support** (All gates pass)
   - G_o ≥ 10%, routing accuracy ≥70%, overhead <10%, improvement ≥60% of G_o
   - → Mechanism validated, proceed to Phase 5 baseline comparison
   - → Publish as positive result with documented scope (persistent-task regimes, H ≥ H_crit)

2. **Partial Thesis Support** (Some H-M fail, but H-E1 + H-M1-M2 pass)
   - Oracle gap exists, routing learns task patterns, but overhead >10% or improvement <60%
   - → PIVOT to batch-level routing or cached meta-features to reduce overhead
   - → EXPLORE richer meta-features or multi-task meta-learning for better improvement
   - → Document as "proof of concept with efficiency limitations"

3. **Antithesis Support** (H-E1 or critical H-M1-M2 fail)
   - Oracle gap G_o < 10%: Task heterogeneity insufficient → antithesis supported
   - Routing accuracy <70%: Meta-features lack signal → antithesis supported
   - → Negative result: routing does not provide significant benefit for this task family
   - → Contribute as methodological validation: documents when routing fails (valuable negative result)

4. **Scope Narrowing** (H-M4 marginal, H-C fails)
   - Improvement 50-60% of G_o (below 60% target but positive)
   - H-C1 finds no clear H_crit threshold, or H-C2 shows degradation >20% at 2σ
   - → Document as "limited applicability": routing works but requires careful deployment constraints
   - → Refine hypothesis for narrower scope (e.g., high-heterogeneity task subsets only)

**Dialectical Resolution Strategy:**

The verification plan is deliberately designed to adjudicate between thesis and antithesis through empirical evidence with pre-registered thresholds. Rather than assuming the thesis is correct, the gate-based structure allows the data to support either position:

- **Early falsification**: H-E1 failure immediately supports H0 without wasting resources on mechanism testing
- **Granular diagnosis**: Sequential H-M testing identifies which specific mechanism step fails
- **Statistical rigor**: Bootstrap CIs and permutation tests provide objective decision criteria
- **Honest scope**: H-C tests document boundaries rather than over-claiming universal applicability

This approach respects both the thesis potential (worth testing if evidence supports) and the antithesis validity (null hypothesis is a legitimate scientific position that may be empirically supported).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6.4 Robustness Assessment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution Mechanism |
|--------|-----------------|----------------------|----------------------|
| **Existence** | Oracle gap G_o ≥ 10% exists across multi-domain benchmarks | May be measurement artifact; fixed rank-16 suffices | H-E1 pilot study with bootstrap CI; permutation baseline |
| **Mechanism** | Four-step causal chain: pathways → routing → navigation → improvement | Alternative: improvement due to better training, not routing | H-M1-M4 sequential testing with ablations; permutation test isolates routing structure |
| **Scope** | Applies to persistent-task regimes with H ≥ H_crit | Limited to narrow conditions; most deployments don't meet criteria | H-C1-C2 document boundaries empirically; scope documented not claimed universally |
| **Performance** | Recovers ≥60% of oracle gap, outperforms best fixed rank | Marginal improvement not worth complexity | Statistical test with 95% CI; practical significance threshold (60%) vs statistical |
| **Generalization** | Routing generalizes within 2σ interpolation regime | Fragile to distribution shift; requires frequent retraining | H-C2 tests degradation at 2σ boundary; documents deployment monitoring requirements |

**Overall Robustness Score**: **Medium-High**

**Rationale:**
- **Strengths**: Gate-based falsification, pre-registered thresholds, statistical rigor, scope honesty
- **Weaknesses**: Dependent on sufficient task heterogeneity (gatekeeper H-E1), meta-feature quality (H-M2), systems constraints (overhead/batching)
- **Mitigation**: Early gates detect fundamental failures before expensive mechanism testing; PIVOT/EXPLORE strategies for partial failures

**Confidence in Verification Plan**: **0.8** (from Phase 2A)

**Justification for Confidence Level:**
- **High confidence (0.8)** that verification plan can adjudicate thesis vs antithesis
- **High confidence** that gate-based structure prevents wasted effort if premise fails
- **Medium confidence** that thesis will be supported (depends on empirical G_o measurement)
- **High confidence** that negative result is publishable (documents when routing fails)

**Key Uncertainty Factors:**
1. **Empirical G_o magnitude**: Unknown until H-E1 pilot study; critical gatekeeper
2. **Meta-feature discriminability**: Unknown until H-M2 routing accuracy measurement
3. **Systems overhead**: Profiling required to validate <10% assumption (H-M3)

**Risk-Adjusted Expectations:**
- **Best case** (30% probability): All gates pass, full thesis support, ≥60% oracle gap recovery
- **Likely case** (50% probability): Partial support, some PIVOT/EXPLORE needed, 50-60% recovery or overhead >10%
- **Worst case** (20% probability): H-E1 fails (G_o < 10%) or H-M2 fails (accuracy <70%), antithesis supported

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 7. Executive Summary

**Main Hypothesis**: Meta-learned routing over pre-trained multi-rank adapter pathways improves expected hypervolume by ≥60% of oracle gap under persistent-task deployment regimes
- **ID**: H-POAR-v1, **Confidence**: 0.8

**Verification Structure**:
- **Mode**: Incremental (built on Phase 2A Dialogue)
- **Sub-Hypotheses**: 7 total (H-E: 1, H-M: 4, H-C: 2)
- **Phases**: 3 phases over 8 weeks (Foundation → Mechanism Chain → Boundary Conditions)
- **Critical Gates**: 3 decision points (Gate 1: MUST_WORK, Gate 2: DETERMINES_SUCCESS, Gate 2.5: SHOULD_WORK)

**Risk Assessment**: High (2 critical risks)
- **R1 (High)**: Insufficient task heterogeneity (G_o < 10%) → ABORT if H-E1 fails
- **R2 (High)**: Weak meta-feature signal (accuracy <70%) → PIVOT to augmented features if H-M2 fails

**Immediate Action**: Begin Phase 1 (Weeks 1-2) with H-E1 oracle gap pilot study

---

## 7.1 Key Achievements

**Verification Plan Deliverables**:
- **7 hypotheses** structured across 3 verification phases with gate-based decision points
- **H0 addressed**: Null hypothesis integrated into dialectical analysis (thesis-antithesis-synthesis)
- **Risk mitigation**: 5 risks identified from assumptions (A1-A5) with prevention/detection/response strategies
- **Execution roadmap**: 8-week timeline with critical path analysis and parallel optimization (H-C1 || H-C2)
- **Scope honesty**: Established facts documented (3 BUILD_ON claims), boundary conditions tested (H-C1-C2)

---

## 7.2 Verification Execution Order

**Phase 1: Foundation** (Weeks 1-2)
- **H-E1**: Oracle Gap Existence - Verify G_o ≥ 10% across multi-domain benchmarks
- **Gate 1**: MUST_WORK - If fail (G_o < 10%), ABORT entire hypothesis

**Phase 2: Mechanism Chain** (Weeks 3-7)
- **H-M1** (Weeks 3-4): Adapter Pathway Diversity - Four LoRA ranks create distinct Pareto profiles
- **H-M2** (Week 5): Routing Policy Learning - 2-layer MLP achieves ≥70% classification accuracy
- **H-M3** (Week 6): Inference-Time Navigation - Routing overhead <10%, batching maintains throughput
- **H-M4** (Week 7): Hypervolume Improvement - POAR recovers ≥60% of oracle gap with 95% CI
- **Gate 2**: DETERMINES_SUCCESS - If H-M4 fails, PIVOT to alternative approaches

**Phase 2.5: Boundary Conditions** (Week 8, Parallel)
- **H-C1**: Heterogeneity Threshold - Identify H_crit via segmented regression, verify net gain positive
- **H-C2**: Interpolation Regime - Test degradation ≤20% at 2σ Mahalanobis distance
- **Gate 2.5**: SHOULD_WORK - Failures narrow scope but don't invalidate core mechanism

---

## 7.3 Critical Decision Points

**1. Gate 1 (Week 2, Foundation)**
- **Criterion**: H-E1 oracle gap G_o ≥ 10% with 95% CI
- **PASS**: Oracle gap exists → Proceed to Phase 2 (mechanism verification)
- **FAIL**: G_o < 10% → **ABORT** - insufficient heterogeneity, hypothesis premise invalid

**2. Gate 2 (Week 7, Mechanisms)**
- **Criterion**: H-M4 recovers ≥60% of oracle gap with 95% CI excluding zero
- **PASS**: Mechanism validated → Proceed to Phase 2.5 (boundary conditions) or Phase 5 (baseline comparison)
- **FAIL**: Improvement <60% or CI includes zero → **PIVOT** to multi-task meta-learning or richer meta-features
- **Note**: H-M1-M2 failures trigger intermediate PIVOTs (adapter architectures, meta-feature augmentation)

**3. Gate 2.5 (Week 8, Boundary Conditions)**
- **Criterion**: H-C1-C2 document scope boundaries
- **PASS**: Deployment constraints clear (H ≥ H_crit, ≤2σ drift)
- **FAIL**: Narrow applicability scope but core mechanism remains valid

---

## 7.4 Open Questions

From Phase 2A phase2b_readiness.open_questions:
- **Q1**: What is the empirically determined H_crit threshold for representative benchmarks? → **H-C1 addresses**
- **Q2**: How does routing performance scale to hierarchical multi-axis configuration spaces (rank × placement × sparsity)? → **Beyond scope, future work**
- **Q3**: Can routing policies transfer across different foundation model families (encoder-only vs decoder-only)? → **Beyond scope, Phase 2A scoped to LLaMA-2-7B**

---

## 7.5 Recommendations

**Immediate Actions** (Pre-Phase 1):
1. Set up 8×A100 GPU cluster with vLLM/TensorRT-LLM serving framework
2. Prepare multi-domain benchmark suite: GLUE (9 tasks), XTREME (40 languages), domain adaptation splits
3. Implement checkpoint strategy: save oracle gap measurements, adapter weights, routing policy, evaluation metrics

**Resource Allocation**:
- **Critical path**: 6 weeks (H-E1 → H-M4), buffer 2 weeks for failures → **8 weeks total**
- **Parallel execution**: H-C1 || H-C2 saves 1 week vs sequential
- **Computational budget**: 2 weeks adapter training (H-M1), 1 week routing meta-learning (H-M2), 1 week evaluation (H-M4)

**Failure Management**:
- **H-E1 failure** (G_o < 10%): PIVOT to broader task distribution (add code generation, math reasoning) or ABORT
- **H-M2 failure** (accuracy <70%): EXPLORE augmented meta-features (gradient norms, activation stats, attention entropy)
- **H-M3 failure** (overhead >10%): SCOPE to medium/high-rank adapters (8-32) where overhead ratio is favorable
- **H-M4 failure** (improvement <60%): PIVOT to multi-task meta-learning or hierarchical routing architecture

**Phase 5 Preparation** (Post-Phase 2B):
- Document baseline comparison plan: POAR vs best fixed-rank LoRA, MoE, per-task NAS
- Define success criteria: statistical significance (p<0.05), practical significance (≥10% hypervolume improvement)

---

## 7.6 Appendices

### A. Phase 2A Reference
- **Source**: `/docs/youra_research/20260419_scope/03_refinement.yaml`
- **Hypothesis ID**: H-POAR-v1
- **Confidence**: 0.8
- **Established Facts**: 3 BUILD_ON claims (LoRA efficiency, benchmark diversity, fixed configuration practice)

### B. MCP Tool Usage Summary
- **Total MCP calls**: 0 (MCP services unavailable in execution environment)
- **Note**: Hypotheses generated based on Phase 2A causal structure (4-step mechanism) without MCP scientific method

### C. Hypothesis Count Justification
- **Dynamic generation**: 1 (H-E) + 4 (H-M, follows causal chain count) + 2 (H-C, user confirmed) = 7 total
- **Rationale**: Causal chain length from Phase 2A (4 steps) determines H-M count; condition hypotheses included to document scope boundaries

---

*Generated by YouRA Phase 2B v7.7.0 | 2026-04-19*
