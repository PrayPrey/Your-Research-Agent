# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (SPEI Architecture - Round 1)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SPEI-neurips2024-owa-v1
**Confidence Level:** 0.82 (High)

**Main Hypothesis:**
Under open-world agent scenarios requiring simultaneous reasoning and decision-making (C), if we implement synchronous prediction-error exchange at multiple temporal scales (0.1s, 1s, 10s) via dual-stream transformers with cross-attention (X), then agents will achieve better sample efficiency and adaptation speed compared to sequential reasoning-action approaches (Y) because continuous bidirectional information flow enables real-time plan adjustment based on execution feedback (Z).

**Alternative Hypothesis (H0):**
There is no significant difference in sample efficiency or adaptation speed between synchronous prediction-error exchange (SPEI) and sequential reasoning-action approaches. Any observed performance difference is due to confounding factors (architecture capacity, training time, hyperparameter tuning) rather than the bidirectional coupling mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Temporal scales | Independent | Three hierarchical scales: 0.1s (reactive), 1s (tactical), 10s (strategic) based on hierarchical RL literature (FuN, Options framework) | Fixed: {0.1s, 1s, 10s} |
| Cross-attention layers | Independent | 3 layers (one per temporal scale) enabling bidirectional prediction-error exchange between reasoning and decision streams | Fixed: 3 layers |
| Curriculum stages | Independent | 4-stage progression: (1) pre-train decision stream, (2) single-scale (0.1s), (3) dual-scale (0.1s+1s), (4) full 3-scale | Sequential: Stage 1 → 2 → 3 → 4 |
| Sample efficiency | Dependent | Number of environment steps required to reach threshold performance (e.g., 80% success rate) measured via RL training curves | Lower is better; expect 20-40% reduction vs baselines |
| Task success rate | Dependent | Percentage of successfully completed tasks on benchmarks (CivRealm, Minecraft, MuJoCo) measured at convergence | 0-100%; expect ≥75% on complex tasks |
| Adaptation speed | Dependent | Performance recovery rate after environment change (measured as time to regain 90% of pre-change performance) | Faster is better; expect 2-3x improvement vs sequential |
| Architecture type | Controlled | Dual-stream transformer (12 layers per stream) with identical hyperparameters across conditions | Fixed: 12-layer dual-stream |
| Training protocol | Controlled | Hierarchical curriculum with fixed stage transitions and loss weighting schedule (λ₁=0.7→0.3, λ₂=0.2→0.6) | Fixed schedule across conditions |
| Evaluation environments | Controlled | Standardized benchmarks: CivRealm (strategy), Minecraft (open-world), MuJoCo (continuous control) | Fixed: 3 environments |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

**Step 1 → Step 2: Multi-scale prediction generation → Cross-attention receives hierarchical predictions**
- **Mechanism:** Reasoning stream generates predictions at 0.1s/1s/10s temporal scales, creating structured forward models at multiple abstraction levels
- **Evidence:** Hierarchical RL (FuN uses 10-step hierarchy, Options framework validates temporal abstraction), OmniJARVIS demonstrates multi-horizon reasoning feasibility
- **Falsification point:** If temporal scales are misaligned with task structure (e.g., all predictions at 10s scale for sub-second reactive tasks) → predictions become irrelevant, no useful forward model

**Step 2 → Step 3: Action execution → Prediction error computation**
- **Mechanism:** Decision stream executes actions and compares outcomes with reasoning predictions, quantifying discrepancies at each temporal scale
- **Evidence:** OmniJARVIS demonstrates action tokenization feasibility; MuJoCo benchmarks show continuous action spaces are tractable; DINO-WM validates prediction-based planning
- **Falsification point:** If action space is too high-dimensional or stochastic → prediction errors become too noisy, signal-to-noise ratio drops below usability threshold

**Step 3 → Step 4: Prediction errors → Cross-attention modulates reasoning**
- **Mechanism:** Errors propagate through cross-attention layers, updating reasoning representations based on execution feedback within same forward pass
- **Evidence:** StreamDiffusion and Text2Video-Zero (Archon KB) show dual-stream architectures handle bidirectional flow; predictive coding theory (Rao & Ballard 1999, Millidge et al. 2021) formalizes error-driven updates
- **Falsification point:** If cross-attention layers saturate or diverge during training → error signals don't propagate, bidirectional coupling fails

**Step 4 → Outcome: Updated reasoning → Real-time plan adjustment**
- **Mechanism:** Modified reasoning representations immediately influence next prediction cycle, enabling adaptive planning without full recomputation
- **Evidence:** AgentGym-RL shows RL agents benefit from multi-turn reasoning; CivRealm demonstrates learning+reasoning synergy; Fine-Tuning VLMs shows CoT reasoning improves decisions
- **Falsification point:** If curriculum doesn't stabilize training → early-stage noise prevents convergence, no adaptive planning emerges

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Hierarchical RL (FuN, Options framework) | Multi-scale abstractions improve hierarchical task performance | Strong |
| Step2 → Step3 | DINO-WM (2024, 118 cites) | Patch feature prediction enables zero-shot planning via forward models | Strong |
| Step3 → Step4 | Predictive coding (Rao & Ballard 1999) + Archon KB dual-stream cases | Error signals drive representational updates in biological and artificial systems | Medium-Strong |
| Step4 → Outcome | AgentGym-RL (2025, 21 cites) + CivRealm (2024, 31 cites) | Multi-turn reasoning and learning+reasoning synergy enable adaptive behavior | Medium |

**Key Tension:**
- **Tension:** OmniJARVIS (2024) achieves strong performance with **sequential** reasoning→planning→acting phases, suggesting bidirectional coupling may not be necessary. DINO-WM (2024) demonstrates **unidirectional** prediction (state → future state) suffices for zero-shot planning.
- **Resolution:** This verification plan tests whether **real-time adaptation** scenarios (environment changes mid-task, unexpected outcomes) benefit from synchronous bidirectional coupling vs sequential replanning. Sequential approaches require full recomputation per adaptation; SPEI updates incrementally within single forward pass. Experiments will measure adaptation speed in dynamic environments to determine if bidirectional coupling provides efficiency gains beyond static planning tasks.

### 1.4 Key Assumptions

1. **Prediction errors contain actionable information for reasoning updates**
   - **Evidence:** Predictive coding in visual cortex (Rao & Ballard 1999) shows error signals drive representational changes; DINO-WM (2024) demonstrates prediction errors enable zero-shot planning by treating goal features as prediction targets
   - **Consequence if violated:** If errors are uninformative (e.g., random noise dominates signal), cross-attention updates will not improve reasoning quality → SPEI reduces to parallel single-stream models with no coupling benefit

2. **Cross-attention can implement bidirectional information exchange effectively**
   - **Evidence:** Transformer architectures use cross-attention for multi-modal fusion (CLIP, DALL-E); Fine-Tuning VLMs (2024, 142 cites) shows CoT reasoning benefits from grounding in observations; StreamDiffusion (Archon KB) validates dual-stream feasibility
   - **Consequence if violated:** If cross-attention saturates, vanishes, or creates training instability → bidirectional coupling mechanism fails, SPEI cannot synchronize prediction-error exchange

3. **Multi-scale temporal processing benefits hierarchical reasoning-action tasks**
   - **Evidence:** Hierarchical RL (FuN, HIRO) validates multi-scale abstractions improve performance; cognitive science shows human cognition operates at sensorimotor (sub-second), tactical (seconds), strategic (10s+) timescales
   - **Consequence if violated:** If single-scale predictions suffice or multi-scale adds overhead without benefit → simpler architectures would outperform SPEI, undermining the multi-horizon design rationale

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- **Task types:** Multi-step goal-directed tasks in dynamic environments requiring both reasoning (planning, goal decomposition) and decision-making (action selection, control)
- **Environments:** Interactive simulations with state transitions (games like CivRealm/Minecraft, robotic manipulation in MuJoCo, embodied AI scenarios)
- **Temporal scale:** Tasks with hierarchical structure spanning reactive (0.1s), tactical (1s), and strategic (10s) horizons
- **Complexity:** Open-world scenarios where plans must adapt to unexpected outcomes or environment changes

**Where it does NOT apply:**
- **Static planning:** Offline planning tasks without execution feedback (e.g., pure search problems like chess without time pressure)
- **Single-scale tasks:** Purely reactive tasks (sub-second reflexes) or purely strategic tasks (long-term planning without intermediate execution) that don't benefit from multi-scale reasoning
- **Fully deterministic environments:** Scenarios where perfect forward models eliminate prediction errors (no learning signal for bidirectional coupling)
- **Extreme action spaces:** Very high-dimensional continuous action spaces (>100 dimensions) or highly stochastic environments where prediction errors are dominated by irreducible noise

**Known limitations:**
- **10s strategic horizon:** Current design limited to 10-second planning window; longer-term planning (minutes/hours) requires recursive hierarchy extension (future work)
- **Fixed temporal scales:** Scales (0.1s, 1s, 10s) are predetermined, not adaptive to task structure; learnable scale adaptation could improve generalization
- **Curriculum dependency:** Performance relies on careful curriculum design; poor stage transitions or loss weighting may cause training failure
- **Domain-specific tuning:** While architecture is general, loss weights and curriculum schedules may require per-domain adjustment

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Sample Efficiency):** SPEI will achieve 80% task success rate with **20-40% fewer environment steps** compared to sequential reasoning-action baselines (OmniJARVIS-style models) on CivRealm, Minecraft, and MuJoCo benchmarks.
- **Quantitative threshold:** SPEI sample efficiency ≥ 1.25x baseline (20% reduction in steps)
- **Statistical test:** Paired t-test comparing steps-to-threshold across 5 random seeds per environment (α=0.05)
- **Rationale:** Real-time plan adjustment via synchronous prediction-error exchange should reduce wasted exploration from incorrect plans, improving sample efficiency

**Secondary Predictions:**
**P2 (Adaptation Speed):** In environments with mid-task changes (e.g., goal relocation in Minecraft, physics parameter shifts in MuJoCo), SPEI will recover 90% of pre-change performance **2-3x faster** than sequential baselines.
- **Quantitative threshold:** SPEI adaptation time ≤ 0.5x baseline adaptation time
- **Statistical test:** Independent t-test comparing recovery time across 20 environment change events per task (α=0.05)
- **Rationale:** Synchronous updates enable incremental plan adjustments vs full replanning required by sequential approaches

**P3 (Ablation - Cross-Attention):** Removing cross-attention layers (blocking prediction-error exchange) will reduce SPEI performance by **≥15% in task success rate**, confirming bidirectional coupling is causal.
- **Quantitative threshold:** SPEI_full - SPEI_no_cross_attn ≥ 0.15
- **Statistical test:** Paired t-test across 3 environments × 5 seeds (α=0.05)
- **Rationale:** If bidirectional coupling drives benefits, removing it should significantly degrade performance

**P4 (Ablation - Multi-Scale):** Single-scale prediction (0.1s only) will underperform full 3-scale SPEI by **≥10% in complex strategic tasks** (CivRealm), validating multi-horizon reasoning benefit.
- **Quantitative threshold:** SPEI_3scale - SPEI_single_scale ≥ 0.10 on CivRealm
- **Statistical test:** Paired t-test on CivRealm success rate across 5 seeds (α=0.05)
- **Rationale:** Strategic tasks require long-horizon reasoning; single-scale should fail on complex planning

**Falsification Criteria:**
- **Criterion 1 (Primary):** If SPEI sample efficiency is ≤1.10x baseline (≤10% improvement, below 20% threshold) across all 3 environments → **REJECT H1**: synchronous coupling does not provide meaningful sample efficiency gains
- **Criterion 2 (Adaptation):** If SPEI adaptation time is ≥0.75x baseline (≤33% improvement, below 2x threshold) → **REJECT H1**: bidirectional coupling does not enable faster adaptation
- **Criterion 3 (Mechanism):** If removing cross-attention causes ≤5% performance drop (below 15% threshold) → **REJECT causal mechanism**: bidirectional coupling is not driving benefits, some other factor is responsible
- **Criterion 4 (Convergence failure):** If SPEI fails to converge (training divergence or <50% success rate) on any benchmark while baselines succeed → **REJECT feasibility**: architecture is too unstable for practical use

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Not applicable** - This hypothesis focuses on architectural innovation (synchronous prediction-error exchange mechanism) rather than SOTA performance comparison. Goal is to demonstrate the mechanism works and provides benefits over sequential approaches, not to achieve state-of-the-art benchmark scores.

### 1.8 Statistical Verification Design

**Experiment Type:** Controlled comparison with ablation studies

**Sample Size Calculation:**
- **Primary outcome (P1 - Sample Efficiency):** Paired t-test, effect size d=0.8 (large), power=0.80, α=0.05 → n=15 paired observations
  - **Design:** 3 environments × 5 seeds = 15 observations (SPEI vs baseline per seed)
- **Secondary outcome (P2 - Adaptation):** Independent t-test, effect size d=1.0 (large), power=0.80, α=0.05 → n=17 per group
  - **Design:** 20 environment change events across 3 tasks ensures adequate power

**Experimental Conditions:**
1. **SPEI (treatment):** Full implementation with 3-scale cross-attention + curriculum
2. **Sequential baseline:** OmniJARVIS-style model (reasoning → planning → acting phases, no bidirectional coupling)
3. **Ablation 1:** SPEI without cross-attention (blocked prediction-error exchange)
4. **Ablation 2:** SPEI single-scale (0.1s only, no multi-horizon reasoning)

**Randomization:**
- Environment seeds randomized across 5 replications
- Curriculum stage transitions fixed across conditions (no randomization to isolate coupling mechanism)
- Task order counterbalanced across seeds

**Blinding:** Not applicable (computational experiment)

**Statistical Tests:**
- **P1 (Sample Efficiency):** Paired t-test (SPEI vs baseline, same seeds), α=0.05, two-tailed
- **P2 (Adaptation Speed):** Independent t-test (adaptation events), α=0.05, one-tailed (directional hypothesis)
- **P3 (Cross-Attention Ablation):** Paired t-test (SPEI_full vs SPEI_no_cross_attn), α=0.05, one-tailed
- **P4 (Multi-Scale Ablation):** Paired t-test (SPEI_3scale vs SPEI_single_scale on CivRealm), α=0.05, one-tailed
- **Correction:** Bonferroni correction for 4 tests: α_adjusted = 0.05/4 = 0.0125

**Confound Control:**
- Architecture capacity equalized (same total parameter count ~300M across conditions)
- Training time fixed (same number of gradient steps)
- Hyperparameters matched (learning rate, batch size, optimizer)
- Evaluation protocol standardized (same success criteria, episode length limits)

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type:** Methodological + Theoretical
- **Statement:** First architecture to implement synchronous prediction-error exchange at multiple temporal scales (0.1s, 1s, 10s) within a unified transformer model for agent reasoning-decision integration, enabling real-time bidirectional coupling via cross-attention mechanisms. Bridges neuroscience (predictive coding) and deep learning (transformer agents) with computationally tractable design.
- **Novelty:** Unlike sequential approaches (OmniJARVIS) that reason then act in separate phases, or unidirectional world models (DINO-WM) that predict forward only, SPEI maintains continuous prediction-error loops within single forward passes, enabling incremental plan adjustments based on execution feedback.

**Secondary Contributions:**
- **Hierarchical curriculum training protocol:** 4-stage progression (pre-training → single-scale → dual-scale → full 3-scale) with dynamic loss weighting (λ₁=0.7→0.3 prediction, λ₂=0.2→0.6 task reward) addresses training stability challenges in joint optimization
- **Evaluation framework:** Quantitative metrics for measuring bidirectional coupling strength (prediction accuracy, error utilization, adaptation speed) beyond standard RL benchmarks
- **Practical applicability:** Architecture generalizes across environments with state transitions (games, robotics, dialogue) using standard transformer components, no exotic hardware required

---

## 3. Key Related Work

**Foundation Sources (MUST CITE):**

1. **"Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects"** (1999)
   - Authors: Rao, R. P., & Ballard, D. H.
   - DOI: [https://www.nature.com/articles/nn0199_79](https://doi.org/10.1038/4580)
   - Key Finding: Foundational predictive coding theory - error signals drive representational updates in cortical hierarchy. Establishes biological plausibility of SPEI's error-driven mechanism.

2. **"DINO-WM: World Models on Pre-trained Visual Features enable Zero-shot Planning"** (2024)
   - Authors: Zhou, G., Pan, H., LeCun, Y., Pinto, L.
   - SS ID: badf5d00486111d936b056e52f13c26c1bbbd573 | Citations: 118
   - Key Finding: Patch feature prediction enables zero-shot planning via forward models. Validates prediction-based planning feasibility; SPEI extends to bidirectional prediction-error loops.

3. **"Fine-Tuning Large Vision-Language Models as Decision-Making Agents via Reinforcement Learning"** (2024)
   - Authors: Zhai, Y., Bai, H., Lin, Z., et al.
   - SS ID: f7749635a5fc0492ef4705bee963ffa887bb2865 | Citations: 142
   - Key Finding: CoT reasoning improves decision-making when grounded in observations. Shows reasoning benefits from execution feedback; SPEI makes this coupling synchronous rather than sequential.

4. **"Predictive Coding: A Theoretical and Experimental Review"** (2021)
   - Authors: Millidge, B., Seth, A., Buckley, C. L.
   - Key Finding: Modern computational perspective on predictive coding in DL. Provides theoretical framework for SPEI's error minimization objective.

**Comparison Baselines:**

5. **"OmniJARVIS: Unified Vision-Language-Action Tokenization Enables Open-World Instruction Following Agents"** (2024)
   - Authors: Wang, Z., Cai, S., Mu, Z., et al.
   - SS ID: 57da517dec2fd80ee86aa7c3fe6f4c356e139cd7 | Citations: 26
   - Key Finding: Unified tokenization for multimodal agents achieves strong performance. **Baseline:** Sequential reasoning→planning→acting phases; SPEI tests if synchronous coupling improves adaptation.

6. **"CivRealm: A Learning and Reasoning Odyssey in Civilization for Decision-Making Agents"** (2024)
   - Authors: Qi, S., et al.
   - SS ID: 0e3c90f70019f7c736e3abd762c652e3e2561fec | Citations: 31
   - Key Finding: Complex strategy game requiring both learning and reasoning. **Evaluation benchmark** for testing SPEI's multi-scale hierarchical reasoning on strategic tasks.

**Gap Evidence:**

7. **"FeUdal Networks for Hierarchical Reinforcement Learning (FuN)"** (2017)
   - Authors: Vezhnevets, A. S., et al.
   - Key Finding: Multi-scale temporal abstraction (10-step hierarchy) improves hierarchical RL. Justifies SPEI's 0.1s/1s/10s scale design; gap is lack of reasoning-action integration at these scales.

8. **"AgentGym-RL: Training LLM Agents for Long-Horizon Decision Making through Multi-Turn Reinforcement Learning"** (2025)
   - Authors: Xi, Z., et al.
   - SS ID: 30da58c425d4e2a5e3c0b774cf8302d2fcf9ce51 | Citations: 21
   - Key Finding: Multi-turn reasoning enables long-horizon tasks. Gap: Reasoning and action are separate turns, not synchronously coupled; SPEI addresses this.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses:** 2 + 4 (causal chain length) = **6 sub-hypotheses** for Phase 2B

**SH1 (Existence - Foundation):**
"Does synchronous prediction-error exchange at multiple temporal scales (0.1s, 1s, 10s) improve sample efficiency in open-world agent tasks compared to sequential reasoning-action approaches?"
- **Maps to:** Primary prediction (P1)
- **Verification type:** Empirical (controlled experiment on CivRealm, Minecraft, MuJoCo)
- **Critical:** MUST PASS (≥20% sample efficiency improvement) for Phase 2B to proceed to mechanism verification
- **Priority:** HIGH - Foundation hypothesis, validates phenomenon exists

**SH2 (Mechanism - Core):**
"Is synchronous prediction-error exchange via cross-attention the actual cause of improved sample efficiency and adaptation speed?"
- **Maps to:** 4-step causal mechanism (Step 1 → Step 2 → Step 3 → Step 4 → Outcome)
- **Verification type:** Causal analysis via ablation studies
- **Phase 2B decomposition:** Will become 4 mechanism sub-hypotheses:
  - **H-M1:** Multi-scale prediction generation enables structured forward models
  - **H-M2:** Action execution produces informative prediction errors
  - **H-M3:** Cross-attention propagates errors to modulate reasoning
  - **H-M4:** Updated reasoning enables real-time plan adjustment
- **Critical:** Determines explanatory power - if ablations fail, mechanism is not causal
- **Priority:** HIGH - Core contribution, validates architectural innovation

**SH3 (Comparison - Validation):**
"Does SPEI outperform established baselines (OmniJARVIS-style sequential models, DINO-WM-style world models) on adaptation speed in dynamic environments?"
- **Maps to:** Secondary predictions (P2 - Adaptation Speed)
- **Verification type:** Comparative empirical (controlled experiments with baselines)
- **Critical:** Determines practical value - if SPEI doesn't outperform baselines, contribution is limited
- **Priority:** MEDIUM - Validates practical benefit beyond existence

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format ✅
- [x] Hypothesis ID assigned: H-SPEI-neurips2024-owa-v1 ✅
- [x] Confidence level specified: 0.82 (High) ✅
- [x] Alternative hypothesis (H0) defined ✅
- [x] All variables have operationalization from evidence (9 variables operationalized) ✅
- [x] Causal mechanism has evidence at each step (4 steps, evidence table with sources) ✅
- [x] Causal chain length (N) determined: N=4 ✅
- [x] Key tension identified: Sequential vs synchronous approaches, resolved via adaptation speed experiments ✅
- [x] Key assumptions list consequences if violated (3 assumptions with consequences) ✅
- [x] At least 2 testable predictions exist: 4 predictions (P1-P4) with quantitative thresholds ✅
- [x] Falsification criteria are defined (4 criteria corresponding to predictions) ✅
- [x] Baselines are identified: OmniJARVIS-style sequential, DINO-WM world models ✅
- [x] SH1, SH2, SH3 are clear starting points ✅

**Status:** ✅ **READY FOR PHASE 2B** - All requirements met

### Open Questions

1. **Compute resource requirements:** What GPU compute budget is needed for training dual-stream transformers (~300M parameters) across 3 environments × 5 seeds × 4 conditions? Estimate: 50-100 A100 GPU-hours per condition; total ~400 GPU-hours. **Action:** Secure compute allocation before Phase 2C implementation.

2. **Dataset availability:** Are CivRealm, Minecraft (OpenAI VPT), and MuJoCo environments accessible with sufficient task diversity for testing adaptation speed? **Action:** Phase 2B will verify dataset access and design specific evaluation protocols.

3. **Curriculum hyperparameter sensitivity:** How sensitive is SPEI to curriculum stage transitions and loss weight schedules? Initial design uses fixed schedule (λ₁=0.7→0.3, λ₂=0.2→0.6), but robustness unclear. **Action:** Phase 2B should include sensitivity analysis in verification plan.

4. **Priority verification order:** Should Phase 2B verify SH1 (existence) → SH2 (mechanism) → SH3 (comparison) sequentially, or can SH2 ablations run in parallel with SH1? **Recommendation:** Sequential SH1 → SH2 (gates on SH1 PASS), parallel SH2 + SH3 if SH1 passes.

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-08*
