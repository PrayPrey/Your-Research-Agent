# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-StigmaLLM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
In open urban environments with 8+ LLM-based embodied agents (**Condition**), if agents coordinate through stigmergic communication via Hierarchical Semantic Pheromone Fields on octree-based spatial memory (**Intervention**), then multi-agent navigation achieves scalable coordination with O(1) local perception, O(log d) hierarchical queries, and graceful degradation under 50%+ communication failures (**Outcome**), because indirect environment-mediated communication eliminates synchronization overhead and enables emergent collective behavior through local pheromone gradients (**Mechanism**).

**Alternative Hypothesis (H0):**
Stigmergic coordination via semantic pheromone fields provides no coordination advantage over direct peer-to-peer communication methods (CAMON, SAMALM) in multi-agent urban navigation, and performance degrades equivalently under communication failures.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Number of agents | Independent | Agent count in simulation | 2, 4, 8, 12, 16 agents |
| Communication reliability | Independent | Message drop rate percentage | 0%, 25%, 50%, 75% |
| Pheromone decay rate (τ) | Independent | Exponential decay time constant | τ ∈ {10s, 30s, 60s} |
| Pheromone type configuration | Independent | Active pheromone categories | 4 types: EXPLORE, OBSTACLE, CROWD, GOAL |
| Task completion rate | Dependent | % of navigation tasks completed within time limit | Target: >85% |
| Coordination efficiency | Dependent | 1 - (redundant work / total work) | Target: >80% |
| Per-agent communication load | Dependent | Pheromone read/write operations per timestep | Target: O(1) constant |
| Navigation success under failures | Dependent | Task completion at 50% communication drop | Target: <20% degradation |
| Urban environment | Controlled | EmbodiedCity simulator | Fixed map: 1km² urban area |
| LLM model | Controlled | Language model for agent reasoning | GPT-4 or Claude-3 (fixed) |
| Base spatial memory | Controlled | Octree architecture parameters | Depth=8, resolution=0.5m |

### 1.3 Causal Mechanism

**Causal Chain (N=4 Steps):**

```
[Pheromone Write] → [Local Map Update] → [Hierarchical Propagation] → [Pheromone-Augmented Prompt] → [Coordinated Action]
     Step 1              Step 2                  Step 3                      Step 4                    Outcome
```

**Step 1: Pheromone Write → Local Map Update**
Agent completes local action (explore, encounter obstacle, detect crowd, identify goal) and writes typed semantic pheromone to corresponding octree node. Pheromone includes: type, intensity, timestamp, agent_id.

**Step 2: Local Map Update → Hierarchical Propagation**
Octree stores pheromone at leaf node; parent nodes aggregate child statistics (max intensity, recent timestamp). Structure enables O(log d) multi-scale queries where d = octree depth.

**Step 3: Hierarchical Propagation → Pheromone-Augmented Prompt**
Nearby agents query local octree region (O(1) bounded perception window). Retrieved pheromone state formatted as structured prompt injection: `[PHEROMONE_CONTEXT: {type: EXPLORED, intensity: 0.8, age: 5s, direction: NE}]`.

**Step 4: Pheromone-Augmented Prompt → Coordinated Action**
LLM reasons about local pheromone gradients to produce navigation decision. High EXPLORED pheromone → avoid (already covered). High FRONTIER pheromone → attractive (unexplored). CROWD pheromone → social-aware avoidance.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Nature 2024 (Salman et al.) | Auto-designed pheromone behaviors achieve spatial organization and memory | Strong |
| Step2 → Step3 | Mem4Nav (2025) | Octree + topology achieves 7-13pp gains on Touchdown benchmark | Strong |
| Step3 → Step4 | SAMALM (2025) | LLM actors generate control signals from structured prompts | Strong |
| Step4 → Outcome | Swarm Intelligence (2025) | ACO/PSO gradient-following improves coordination, scalability, fault tolerance | Strong |

**Key Tension:**
- **Tension:** Nature 2024 demonstrates stigmergy for robots with simple behaviors, but LLM agents have complex reasoning that may not follow gradient signals reliably. SAMALM uses explicit actor-critic supervision, not emergent coordination.
- **Resolution:** This verification plan tests whether LLM pheromone reasoning produces coherent navigation via comparison with gradient-following vs. random/greedy baselines (Prediction P2).

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Agents have read/write access to shared spatial map (octree) with <500ms latency | Mem4Nav demonstrates efficient octree operations for urban VLN | Coordination delays cause stale pheromone state; mitigate via local caching |
| A2 | LLMs can emit structured pheromone tokens and reason about pheromone gradients | SAMALM (2025) shows LLM control signal generation; NaVILA mid-level actions | Hypothesis fails; would require RL-based pheromone policy instead |
| A3 | Pheromone temporal decay maintains information currency without premature expiration | Nature 2024 automatic stigmergy design validates decay mechanism | Incorrect decay rate causes either stale info (too slow) or amnesia (too fast); ablate τ |
| A4 | Urban environments have sufficient spatial structure for meaningful pheromone gradients | CityEQA benchmark design shows spatial task distribution | Hypothesis may not apply to uniform/sparse environments |

### 1.5 Scope & Boundaries

**Applies To:**
- Urban outdoor VLN with multiple mobile agents (2-16+)
- Search-and-rescue coordination in city environments
- Multi-robot delivery in urban areas
- Any spatially-structured task requiring decentralized coordination

**Does NOT Apply To:**
- Indoor navigation (different spatial structure, existing solutions)
- Non-spatial tasks (dialogue coordination, knowledge tasks)
- Single-agent scenarios (no coordination needed)
- Highly dynamic environments with <10s useful pheromone lifetime

**Known Limitations:**
- Pheromone decay rates (τ) may require task-specific tuning
- Emergent behaviors less predictable than explicit planning
- Discrete semantic pheromones differ from continuous biological gradients
- LLM inference latency may limit real-time responsiveness

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Scalability - O(1) Communication):**
If the number of agents increases from 2 to 16, then per-agent pheromone operations (reads + writes per timestep) remain constant O(1), while direct communication baselines show O(N) or O(N²) growth.

*Measurement:*
- Per-agent ops/timestep measured across agent counts {2, 4, 8, 12, 16}
- Linear regression slope < 0.1 for StigmaLLM (constant)
- Linear regression slope > 0.5 for baselines (linear growth)

*Success Criteria:*
- StigmaLLM: R² < 0.2 for ops vs agents (no correlation)
- Baselines: R² > 0.7 for ops vs agents (strong correlation)

**Secondary Predictions:**
**P2 (Coordination Efficiency):**
If stigmergic coordination is used, then coordination efficiency (1 - redundant work ratio) exceeds CAMON and SAMALM baselines by >15 percentage points.

*Measurement:*
- Redundant work = agent trajectory overlap / total trajectory length
- Efficiency = 1 - redundancy
- Compare: StigmaLLM vs CAMON vs SAMALM on identical tasks

**P3 (Failure Resilience):**
If communication failure rate increases to 50%, then StigmaLLM task completion degrades by <20%, while direct communication baselines degrade by >50%.

*Measurement:*
- Task completion rate at 0% vs 50% message drop
- Degradation = (Completion@0% - Completion@50%) / Completion@0%
- StigmaLLM: Degradation < 0.20
- Baselines: Degradation > 0.50

**Falsification Criteria:**
The hypothesis will be **REJECTED** if ANY of the following occur:

1. **Scalability Failure:** Per-agent operations show O(N) or worse scaling (slope > 0.5)
2. **Efficiency Failure:** Coordination efficiency ≤ SAMALM baseline (no improvement)
3. **Resilience Failure:** Task completion degradation > 40% at 50% communication failure
4. **Mechanism Failure:** LLM pheromone reasoning produces decisions no better than random baseline

### 1.7 SOTA Baseline (Comparison Mode)

**Comparison Methods (from Phase 2A):**

| Method | Type | Key Metric | Reference |
|--------|------|------------|-----------|
| CAMON (2024) | Centralized LLM | Task completion, dynamic leadership | Direct comm baseline |
| SAMALM (2025) | Decentralized LLM | Social compliance, multi-robot coordination | Actor-critic baseline |
| MMCNav (2025) | Multi-agent outdoor VLN | Perception-cognition-action loop | Outdoor VLN baseline |
| CityNav (2025) | Hierarchical LLM vehicles | City-scale navigation | Hierarchical baseline |

**Expected Performance Positioning:**
- StigmaLLM targets: Communication efficiency (O(1) vs O(N)), failure resilience (pheromone persistence vs message loss), scalability (8+ agents vs 2-4 typical)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size target: Cohen's d ≥ 0.8 (large effect for coordination improvement)
- Required runs: n ≥ 20 per configuration
- Total experiments: 5 agent counts × 4 failure rates × 3 decay rates × 20 runs = 1,200 runs

**Test Specification:**
- Primary: Paired t-test (same seeds, different methods)
- Multiple comparison: Bonferroni correction (α = 0.05/k)
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

**Evaluation Protocol:**
1. Fix random seeds for reproducibility
2. Run all methods on identical task sequences
3. Record per-timestep metrics (ops, completion, efficiency)
4. Aggregate statistics and perform significance tests

---

## 2. Contribution Summary

**Theoretical Contribution:**
First formalization of stigmergic coordination principles for LLM-based embodied agents in urban VLN. Establishes paradigm shift from direct peer-to-peer communication to environment-mediated indirect coordination, grounded in swarm intelligence theory (Nature 2024) and adapted for semantic reasoning capabilities of LLMs.

**Methodological Contribution:**
Hierarchical Semantic Pheromone Field (H-SPF) architecture featuring:
1. Typed, decaying semantic pheromones (4 categories) on octree spatial memory
2. O(1) local perception + O(log d) hierarchical propagation complexity
3. Pheromone-augmented LLM prompting protocol for navigation decisions
4. Temporal decay mechanism for information currency management

**Practical Contribution:**
- Enables 8+ agent coordination in urban VLN (vs 2-4 typical)
- Achieves >50% communication failure tolerance (vs <25% for direct methods)
- Provides Multi-Agent CityEQA benchmark extension for evaluation
- Applicable to delivery robots, search-and-rescue, autonomous vehicle coordination

---

## 3. Key Related Work

| Source | Type | Relation to Hypothesis | Semantic Scholar ID |
|--------|------|----------------------|---------------------|
| Automatic design of stigmergy (Nature 2024) | Foundation | Validates stigmergy-based coordination feasibility | 2abcb58d48b38a9417cdd13e6b57dc32fc082fc3 |
| SAMALM (2025) | Comparison | Decentralized multi-agent LLM baseline | 58a4c3f8015865da42ba260676e193c93b3e8eb3 |
| MMCNav (2025) | Comparison | Multi-agent outdoor VLN precursor | dc18324d28b583ac74fec27a99378231b79308e7 |
| Swarm Intelligence (2025) | Inspiration | Bio-inspired coordination principles | 275c83159a59e402c30dbcc3ba7af048ae395486 |
| Mem4Nav (2025) | Methodology | Octree spatial memory architecture | (from Phase 1) |
| CityEQA (2025) | Evaluation | Urban EQA benchmark for experiments | (from Phase 1) |
| GNN-VAE Coordination (Amazon 2025) | Comparison | Centralized vs decentralized trade-offs | arxiv:2503.02954 |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Can LLM agents successfully read and write semantic pheromones to/from octree spatial memory with bounded latency (<500ms)?
- *Test:* Implement pheromone read/write API, measure latency distribution
- *Success:* 95th percentile latency < 500ms

**SH2 (Mechanism):**
Does pheromone-augmented LLM prompting produce gradient-following navigation behavior that exceeds random/greedy baselines?
- *Test:* Compare navigation decisions with/without pheromone context
- *Success:* Pheromone-guided decisions have lower redundancy than baselines

**SH3 (Comparison):**
Does H-SPF coordination outperform direct communication methods (CAMON, SAMALM) on scalability, efficiency, and failure resilience?
- *Test:* Full benchmark comparison on Multi-Agent CityEQA
- *Success:* Statistical significance on ≥2 of 3 primary metrics

### Readiness Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| Core hypothesis clarified | ✅ READY | If-Then-Because format with mechanism |
| Variables operationalized | ✅ READY | All IVs, DVs, CVs defined with ranges |
| Causal mechanism decomposed | ✅ READY | 4-step chain with evidence |
| Assumptions documented | ✅ READY | 4 assumptions with violation consequences |
| Testable predictions defined | ✅ READY | 3 predictions with quantitative thresholds |
| Falsification criteria set | ✅ READY | 4 rejection conditions |
| Related work mapped | ✅ READY | 7 key sources with relations |
| Sub-hypothesis candidates | ✅ READY | SH1 (Existence), SH2 (Mechanism), SH3 (Comparison) |

### Open Questions

1. **Pheromone Conflict Resolution:** What happens when multiple agents write to the same octree node simultaneously? (Propose: timestamp-based latest-write-wins or intensity aggregation)

2. **Decay Rate Generalization:** Can a single τ work across different urban environments, or is per-environment calibration required? (Propose: ablation study in Phase 2B)

3. **LLM Prompt Format:** What is the optimal pheromone context representation for LLM reasoning? (Propose: structured JSON vs natural language comparison)

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
