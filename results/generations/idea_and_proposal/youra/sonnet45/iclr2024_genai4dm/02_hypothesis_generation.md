# Phase 2A Extended: Hypothesis Summary (Phase 2B Input)

**Generated:** 2026-02-06
**Hypothesis ID:** H1-NCIM
**Source:** Narrative Coherence Intrinsic Motivation - Round 1
**Confidence:** 0.78 (MEDIUM-HIGH)
**Status:** ✅ READY FOR PHASE 2B

---

## Executive Summary

**Research Question:** How can pretrained generative models serve as effective priors to improve exploration strategies in sequential decision-making tasks?

**Target Gap:** Gap 2 - LLM-Guided Exploration for Long-Horizon Sparse Reward Tasks

**Core Innovation:** Use LLM evaluation of narrative coherence (causal completeness + prediction violation) to generate exploration bonuses that guide RL agents toward resolving semantic storylines rather than purely novel states.

**Expected Impact:** 20-30% improvement in success rates for sparse-reward tasks with long causal dependencies (>50 steps) in semantically-rich environments.

---

## 1. Hypothesis Statement (Quantified)

**Main Hypothesis:**
In semantically-rich sparse-reward RL environments (NetHack, Crafter, TextWorld), augmenting RND with LLM-based narrative coherence scoring (r_intrinsic = α×r_RND + (1-α)×r_narrative, α∈[0.6,0.8]) will improve task success rate by 20-30% and discover 40-50% more unique causal sequences compared to pure RND baseline (α=1.0) within 10M training steps.

**Alternative Hypothesis (H0):**
LLM narrative coherence provides no significant improvement over state-novelty exploration; observed differences are due to hyperparameter tuning or environment bias, not semantic understanding.

**Falsification Criteria:**
- No significant improvement (p>0.05) in any environment after 10M steps
- NCIM underperforms RND by >10% in >50% of environments
- Coherence scores show no correlation (|r|<0.2) with trajectory value
- Computational overhead exceeds 20% threshold

---

## 2. Variables & Metrics

### Independent Variables
- **r_narrative**: LLM coherence score = w1×(dangling_refs/total_entities) + w2×cosine_distance(pred_embed, actual_embed)
- **α (alpha)**: Weighting parameter [0, 1]
- **W (window)**: Trajectory segment length = 50 steps

### Dependent Variables
- **Task success rate**: Proportion achieving goal in 100 eval episodes
- **Sample efficiency**: Steps to first success
- **Exploration coverage**: Unique causal sequences discovered

### Controlled Variables
- LLM: Llama-3-8B-Instruct (frozen)
- Environments: NetHack, Crafter, TextWorld, ALFWorld
- Base algorithm: PPO (standard hyperparams)
- State conversion: Template-based entity extraction

---

## 3. Causal Mechanism

```
Semantically-rich states
    ↓ (Template conversion)
Natural language trajectories
    ↓ (LLM few-shot prompting)
Narrative coherence scores
    ↓ (Weighted with RND)
Intrinsic rewards
    ↓ (Policy optimization)
Directed exploration toward causal resolution
    ↓ (Training accumulation)
Improved efficiency & success
```

**Critical Assumption:** LLM coherence scores correlate with exploration value for task progress (requires validation: r>0.4 in retrospective analysis).

---

## 4. Scope & Limitations

### ✅ Applicable
- Text-based games (NetHack, TextWorld, Zork)
- Vision-language tasks (Minecraft+MC-CLIP, ALFWorld)
- Semantic simulators (Crafter, BabyAI-Text)

### ❌ Excluded
- Continuous control (Mujoco, robotics)
- Pixel-only games (Atari, Procgen)
- Abstract state spaces (grid worlds)
- Real-time systems (<10ms latency)

**Task Requirements:** Sparse rewards, long-horizon (>50 steps), causal dependencies, goal-oriented

---

## 5. Testable Predictions

**Primary:** α∈[0.6,0.8] → 20-30% higher success rate vs RND in NetHack/Crafter within 10M steps (p<0.05)

**Secondary:**
1. NCIM discovers 40-50% more causal sequences than RND in first 5M steps
2. Degrading states to pixel coords → NCIM drops to within 5% of RND
3. Hyperparameters transfer NetHack→Crafter with <15% degradation

---

## 6. Key Assumptions (Validation Required)

1. **Semantic Describability**: States→text preserves causal info (validate: human rating study)
2. **Coherence-Value Correlation**: Narrative scores predict exploration value (validate: r>0.4 regression)
3. **Stable Prompting**: Few-shot coherence eval is consistent (validate: test-retest across 3 LLMs)
4. **Computational Feasibility**: Overhead <20% (validate: empirical timing)
5. **Domain Generalization**: Principle transfers across semantic environments (validate: cross-env eval)

---

## 7. Contributions

### Theoretical
- **First** to operationalize narrative coherence as intrinsic motivation principle
- Bridges Information Gap Theory (cognitive science) with computational exploration
- Extends LLM-RL taxonomy with "exploration bonus generation" role

### Methodological
- Novel dual-metric coherence: causal completeness + prediction violation
- Hybrid architecture: LLM evaluation + traditional exploration (graceful degradation)
- State-to-narrative pipeline with template-based entity extraction

### Practical
- Enables exploration in long-causal-chain tasks without reward shaping
- Target: 20-30% improvement in sparse-reward semantically-rich environments
- Computational: Single RTX 3090, ~48hr per environment

---

## 8. Related Work Summary

**Foundation:**
- Loewenstein (1994): Information Gap Theory
- Burda et al. (2018): RND baseline
- Pathak et al. (2017): ICM baseline

**LLM-RL Context:**
- Survey (2024, 156 cit): Identified exploration gap
- Taxonomy (2024, 24 cit): No exploration category exists

**Differentiation:**
- vs Goal-Guided RL: Continuous rewards not discrete subgoals
- vs RND/ICM: Semantic coherence not syntactic novelty
- vs LLM Planning: Evaluation not generation

**Technique Sources:**
- TinyVLA (226 cit): State→text conversion feasibility
- PAD (41 cit): Semantic priors for RL

---

## 9. Statistical Design

**Design:** Between-subjects factorial (Method × Environment × α) with repeated measures
- 3 methods (NCIM, RND, ICM) × 3 environments × 4 α values × 5 seeds = 180 runs
- Primary metric: Task success rate (100 eval episodes)
- Test: Two-way ANOVA + Tukey HSD post-hoc
- Power: 0.80, effect size target: Cohen's d>0.5
- Significance: α=0.05 with Bonferroni correction

**Robustness:**
- Ablations: w1 vs w2 contribution, α sensitivity
- Cross-LLM: Llama-3 vs Mistral-7B vs GPT-3.5
- Human baseline: 50 segments, 3 raters (Krippendorff's α)

---

## 10. Phase 2B Decomposition Preview

**SH1 (Existence):** Narrative coherence ≠ state novelty
- Test: Correlation r_narrative vs r_RND (expect |r|<0.5)

**SH2 (Mechanism):** Narrative incompleteness → valuable exploration
- Test: Coherence scores vs trajectory value (expect r>0.4)

**SH3 (Comparison):** NCIM > Baselines
- Test: ANOVA on success rate (expect 20-30% improvement, p<0.05)

---

## 11. Open Questions for Phase 2B

1. **Priority validation**: Which assumption to test first? (Recommend: Coherence-value correlation)
2. **Metric choice**: Success rate or sample efficiency as primary? (Recommend: Success rate)
3. **Environment order**: Start with NetHack or Crafter? (Recommend: Crafter for fast iteration)
4. **Ablation depth**: Minimum (w1/w2, α) or extended (cross-LLM, prompts)?
5. **Budget**: Is 10M steps sufficient? (Crafter: yes, NetHack: may need 20-50M)
6. **Human ratings**: How many for coherence validation? (Recommend: 50 segments × 3 raters)
7. **Transfer priority**: Cross-environment or within-environment first? (Recommend: within-first)
8. **Failure diagnostics**: What to collect if fails? (Score distributions, attention analysis, ablations)

---

## 12. Phase 2B Readiness Checklist

- [x] Core hypothesis quantified with specific predictions
- [x] Variables operationalized with measurement protocols
- [x] Causal mechanism articulated with evidence
- [x] 5 key assumptions explicit with validation plans
- [x] Scope boundaries clearly defined
- [x] Falsification criteria specified
- [x] Statistical design complete
- [x] Baselines identified (RND, ICM)
- [x] Contributions expanded (theoretical, methodological, practical)
- [x] Related work mapped (10+ papers with relation types)

**Status:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

---

## Next Steps

### Immediate
1. **Phase 2B:** Decompose H1 into detailed sub-hypotheses (SH1-SH3)
2. **Phase 2B:** Establish verification experiments with success criteria
3. **Phase 2B:** Prioritize validation tasks (recommend: start with Assumption 2)

### Future
- Phase 2C: Design experiments based on Phase 2B verification plan
- Phase 3: Create implementation plan (PRD, architecture, PRP)
- Phase 4: Code and validate hypothesis

---

**Full Document:** `02a_extended_hypothesis_full.md`

*Generated via Phase 2A Extended Workflow (YOLO MODE)*
*YouRA Pipeline: Generative Models for Decision Making*
*2026-02-06*
