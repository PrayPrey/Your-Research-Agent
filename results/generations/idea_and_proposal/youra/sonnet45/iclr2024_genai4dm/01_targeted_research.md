# Targeted Research Report: Generative Models for Decision Making

**Generated:** 2026-02-03
**Phase:** 1 - Targeted Research Gathering (Compact Version for Phase 2A)
**Researcher:** Pray

---

## Research Questions

### Primary
How can pretrained generative models serve as effective priors to improve sample efficiency, exploration strategies, and transfer learning in sequential decision-making tasks across reinforcement learning, planning, and robotic control domains?

### Sub-Questions
1. LLMs for planning/reward generation  
2. Diffusion models as physics-aware world models  
3. Sample efficiency via unlabeled data  
4. Exploration in sparse reward tasks  
5. Transfer learning comparison  
6. IRL/IL improvements  

---

## Key Academic Papers (Top 10)

1. **Survey on LLM-Enhanced RL** (2024, 156 cit) - c44471e846846bde281779405a3b5c132fd60b00
2. **TinyVLA** (2024, 226 cit) - dc62bc6536e9e3ad80242f10f44c046e4c7bd3d1
3. **Generative Skill Chaining** (2023, 99 cit) - 7090d35c316afe869440ede6ad61fdeec85b8bc8
4. **Prediction with Action (PAD)** (2024, 41 cit) - 3fbf40b6d2125b0593f34d8e5e597abc00c976eb
5. **Motion Planning with Generative Model** (2024, 38 cit) - bff0c3d026afc75f82833e90a58fdabcf92fc834
6. **Robot Motion Diffusion Model** (2024, 32 cit) - 44f763c847ca38b603640cb91c36d11a60a5599b
7. **Cooperative CAV Decision-Making** (2024, 28 cit) - 6204ad144980528b3579d6cfdec6104c5e6faa9b
8. **RL/LLM Taxonomy Tree** (2024, 24 cit) - c362015d426c90ec01e1ad02bf3fd66ab8fd0fd9
9. **Scale-free Active Inference** (2024, 20 cit) - 72cc98148b7c0092ce4babcb03d3c021753935bc
10. **WARPD** (2024, 1 cit) - e34cbe11bd3d900d831272643d53861f50773ddd

---

## 8. Research Gaps

### Gap 1: Physics-Informed Diffusion World Models for Sample-Efficient RL ⭐

**Current State:** Diffusion models used for action generation (Diffusion Policy) or general world models, but limited integration of physics constraints.

**Missing Piece:**
- Physics-aware inductive biases in diffusion dynamics models
- Sample efficiency evaluation vs model-free RL
- Continuous control benchmarks

**Impact:** HIGH - Enables data-efficient learning in robotics

**Evidence:**
- WARPD (2024): Policies not trajectories, but no explicit physics
- Robot Motion Diffusion (2024): Kinematic focus
- GIT-STORM (2024): MaskGIT priors improve world models (not physics-specific)

**Traceability:** ✅ Directly addresses Sub-Question 2

---

### Gap 2: LLM-Guided Exploration for Long-Horizon Sparse Reward Tasks ⭐

**Current State:** LLMs for high-level planning and rewards, but limited work on exploration bonuses/curiosity signals.

**Missing Piece:**
- LLM-derived intrinsic motivation
- Integration with exploration algorithms (ICM, RND)
- Open-ended task evaluation

**Impact:** HIGH - Enables RL where reward engineering is difficult

**Evidence:**
- Survey (156 cit): "Information processor" role but no exploration focus
- Goal-Guided RL (2025): Subgoal generation, not exploration bonuses
- RL/LLM Taxonomy (24 cit): No exploration category

**Traceability:** ✅ Directly addresses Sub-Question 4

---

### Gap 3: Benchmarking Generative Priors Across Decision-Making Modalities

**Current State:** Separate benchmarks for LLM-RL and diffusion policies, no unified comparison.

**Missing Piece:**
- Systematic comparison: LLMs vs Diffusion vs VAEs
- Multi-criteria evaluation (sample efficiency, transfer, interpretability)
- Cross-modality experiments

**Impact:** MEDIUM-HIGH - Standardizes evaluation, enables principled model selection

**Evidence:**
- Motion Planning Survey (2025): Reviews methods, no unified benchmark
- TinyVLA (226 cit): Compares vs OpenVLA only
- Trajectory Generation (2025): Contrasts models but trajectory-specific

**Traceability:** ✅ Workshop question + Sub-Question 5

---

### Gap Priority Matrix

| Gap | Impact | Difficulty | Evidence | Priority |
|-----|--------|------------|----------|----------|
| Gap 1: Physics-Informed Diffusion | High | High | 3 papers | **P0** |
| Gap 2: LLM Exploration | High | Medium | 3 papers | **P1** |
| Gap 3: Unified Benchmarking | Med-High | Medium | 3 papers | **P2** |

---

## Preliminary Answers to Sub-Questions

1. **LLMs for Planning:** ✅ YES (Survey 156 cit, RL/LLM Tax 24 cit)
2. **Diffusion World Models:** ⚠️ PARTIALLY (TinyVLA, WARPD show promise, **physics-aware gap**)
3. **Unlabeled Data:** ✅ YES (TinyVLA, PAD demonstrate visual pretraining)
4. **Exploration:** ⚠️ LIMITED (**gap identified**)
5. **Transfer Learning:** ❓ INCONCLUSIVE (**benchmarking gap**)
6. **IRL/IL:** 🔄 EMERGING (dVLA, TinyVLA show improvements)

---

## Phase 2A Readiness: ✅ READY

**Prerequisites Met:**
- ✅ 3 high-priority gaps identified
- ✅ 15 directly relevant papers (40+ total)
- ✅ Gaps traced to user questions
- ✅ Field maturity assessed (emerging, 2023-2025)
- ✅ Knowledge base gap confirmed (0 Archon results)

**Recommended Focus:**
1. **Primary:** Gap 1 (Physics-Informed Diffusion) - highest impact
2. **Secondary:** Gap 2 (LLM Exploration) - workshop alignment
3. **Cross-cutting:** Gap 3 (Benchmarking) - evaluation foundation

---

*Compact report for Phase 2A Hypothesis Generation*
*Full report: 01_targeted_research_full.md*
