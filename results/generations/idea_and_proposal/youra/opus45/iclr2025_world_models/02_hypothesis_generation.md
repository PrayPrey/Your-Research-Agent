# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - Duet Dynamics World Model)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-DuetDynamics-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of world model prediction tasks with varying dynamics uncertainty, **if** we route predictions through SSM (Mamba) for low-uncertainty states and Diffusion for high-uncertainty states using learned uncertainty gating, **then** the model achieves a superior efficiency-quality tradeoff (matching diffusion quality within 5% FVD while achieving 2-3x faster inference than pure diffusion), **because** deterministic dynamics are efficiently handled by linear-complexity SSM (O(n)) while stochastic/novel dynamics benefit from diffusion's generative capacity, inspired by dual prediction error signals in neuroscience's duet predictive coding.

**Alternative Hypothesis (H0):**
Functional separation of dynamics (SSM for deterministic, Diffusion for stochastic) provides no advantage over unified architectures. Specifically: (1) A pure diffusion model achieves equivalent or better quality-efficiency tradeoff, OR (2) A pure SSM model achieves equivalent quality, OR (3) The gating mechanism introduces overhead that negates efficiency benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture Type | Independent | Duet Dynamics (SSM+Diffusion+Gating) vs SSM-only vs Diffusion-only vs StateSpaceDiffuser | 4 conditions |
| Prediction Quality (FVD) | Dependent | Fréchet Video Distance on video prediction benchmarks (lower = better) | Target: <100 FVD on DMControl |
| Prediction Quality (LPIPS) | Dependent | Learned Perceptual Image Patch Similarity (lower = better) | Target: <0.15 |
| Computational Efficiency | Dependent | FLOPs per frame, inference latency (ms), throughput (frames/sec) | Target: 2-3x faster than diffusion-only |
| Diffusion Activation Rate | Dependent | Percentage of frames routed to diffusion pathway | Target: <30% |
| Gating Threshold | Controlled | Learnable threshold with entropy regularization, initialized at 70th percentile | Fixed per experiment |
| Model Capacity | Controlled | Total parameters matched across ablations | ~500M parameters |
| Training Budget | Controlled | Fixed compute budget for fair comparison | 8 A100 GPU-days |

### 1.3 Causal Mechanism

**4-Step Causal Chain (N=4):**

```
[Input State] → [Uncertainty Estimation] → [Pathway Routing] → [Dual Prediction] → [Efficient Quality Output]
     Step 1              Step 2                  Step 3              Step 4              Outcome
```

**Step 1: Input State → Uncertainty Estimation**
- Ensemble of K SSM heads (K=3-5) processes input state
- Epistemic uncertainty computed via ensemble variance: σ²(x) = Var({f₁(x), f₂(x), ..., fₖ(x)})
- High variance indicates stochastic/novel dynamics requiring diffusion

**Step 2: Uncertainty Estimation → Pathway Routing**
- Learned gating network g(x): σ²(x) → [0,1] with entropy regularization
- Threshold τ (learnable, initialized at 70th percentile) determines routing
- If g(x) > τ: route to diffusion; else: route to SSM

**Step 3: Pathway Routing → Dual Prediction**
- **SSM Pathway (g(x) ≤ τ):** Mamba-based encoder-decoder with O(n) complexity predicts next-state efficiently
- **Diffusion Pathway (g(x) > τ):** Lightweight DiT head (4-8 denoising steps) generates high-quality prediction for uncertain regions

**Step 4: Dual Prediction → Efficient Quality Output**
- Predictions merged via uncertainty-weighted combination
- Sparse diffusion activation (<30% frames) preserves efficiency
- Quality maintained by diffusion on high-uncertainty frames

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Mamba (Gu & Dao, 2023) | Ensemble variance effective for uncertainty; selective SSM enables content-based reasoning | Strong |
| Step2 → Step3 | MoE Literature + Duet Predictive Coding | Gating mechanisms proven effective; brain uses dual pathways for expected/unexpected | Strong |
| Step3 → Step4 | Video Diffusion (Ho et al., 2022) | Diffusion excels at stochastic generation; SSM matches quality on deterministic | Strong |
| Step4 → Outcome | StateSpaceDiffuser (2025) | SSM+Diffusion combination maintains context 10x longer; validates hybrid potential | Medium |

**Key Tension:**

**Tension:** Mamba authors suggest SSM can handle most sequence modeling tasks efficiently, but Video Diffusion literature demonstrates diffusion superiority for high-fidelity visual generation. StateSpaceDiffuser uses SSM for memory/context rather than functional dynamics separation.

**Resolution:** This verification plan tests whether functional separation (routing based on uncertainty) outperforms memory-based integration (StateSpaceDiffuser). Key experiment: compare Duet Dynamics vs StateSpaceDiffuser on identical benchmarks to determine if dynamics-based routing provides advantage over context-based integration.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | If Violated |
|---|------------|---------------------|-------------|
| A1 | World dynamics decompose into deterministic (predictable) and stochastic (high-variance) components | Duet Predictive Coding (Meng et al., 2025): Brain uses dual prediction error signals for expected vs unexpected events | Gating becomes meaningless; unified architecture would suffice |
| A2 | SSM (Mamba) can efficiently model deterministic dynamics with linear complexity while maintaining prediction quality | Mamba paper (5,601 citations): 5x faster than Transformers with content-based reasoning capability | SSM pathway fails quality threshold; need larger SSM or alternative |
| A3 | Diffusion models excel at modeling stochastic, high-variance dynamics due to iterative denoising | Video Diffusion Models (2,274 citations): State-of-the-art video generation quality | Sparse diffusion insufficient; need higher activation rate |
| A4 | Ensemble-based uncertainty estimation can distinguish deterministic from stochastic dynamics | MoE routing literature + Deep Ensemble uncertainty methods | Gating mechanism fails; need alternative uncertainty method (MC Dropout, learned) |

### 1.5 Scope & Boundaries

**Applies To:**
- Video prediction tasks with temporal dynamics (DMControl, Atari, robotics simulation)
- World models for reinforcement learning (imagination-based policy learning)
- Sequential visual prediction with mixed deterministic/stochastic dynamics
- Real-time inference scenarios where efficiency matters (robotics, embodied AI)

**Does NOT Apply To:**
- Single-frame image generation (no temporal dynamics to separate)
- Static image tasks (no sequential prediction needed)
- Tasks with purely stochastic dynamics (pure diffusion would suffice)
- Tasks with purely deterministic dynamics (pure SSM would suffice)

**Known Limitations:**
- Ensemble SSM heads add ~20% parameter overhead compared to single SSM
- Two-phase training (SSM → Diffusion) requires careful hyperparameter tuning
- Gating threshold selection may need task-specific calibration
- Performance on extremely long sequences (>1000 frames) not yet validated

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Efficiency-Quality Tradeoff vs SOTA):**
Duet Dynamics will achieve **FVD within 5% of pure diffusion baseline** (quality parity) while achieving **2-3x faster inference** (efficiency gain).

*Measurement:*
- Quality: FVD ≤ 1.05 × Diffusion-only FVD with p < 0.05
- Efficiency: Latency ≤ 0.5 × Diffusion-only latency OR throughput ≥ 2× Diffusion-only
- Statistical test: Paired t-test, n ≥ 20 runs per condition

*Basis:*
- STORM achieves 126.7% human normalized score on Atari 100k (Transformer-based)
- DIAMOND achieves 1.46 HNS with diffusion world model
- StateSpaceDiffuser maintains 10x longer temporal context
- Mamba achieves 5x faster inference than Transformers

*Success Criteria for Phase 2B:*
- Primary: FVD ratio ≤ 1.05 AND Latency ratio ≤ 0.5 (p < 0.05 for both)
- Falsification: FVD ratio > 1.2 OR Latency ratio > 0.8 triggers rejection

**Secondary Predictions:**

**P2 (Sparse Diffusion Activation):**
The uncertainty gating mechanism will route **<30% of frames** to the diffusion pathway, with activation concentrated on high-entropy/novel event frames.

*Measurement:* Mean diffusion activation rate across test set < 0.30

**P3 (Generalization Across Domains):**
Duet Dynamics will maintain efficiency-quality advantage across at least 2 of 3 domains: DMControl, Atari 100k, and video prediction benchmarks (RoboNet/Something-Something).

*Measurement:* Efficiency-quality advantage (P1 criteria) met on ≥2 domains

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Quality Failure:** FVD > 1.2 × Diffusion-only FVD (statistically worse quality)
   - Indicates SSM pathway degrades predictions unacceptably

2. **Efficiency Failure:** Latency > 0.8 × Diffusion-only latency (no meaningful speedup)
   - Indicates gating/ensemble overhead negates SSM efficiency

3. **Mechanism Failure:** Diffusion activation rate > 60% of frames
   - Indicates uncertainty gating fails to identify deterministic dynamics

4. **Baseline Failure:** Underperforms SSM-only on both quality AND efficiency
   - Indicates architectural complexity provides no benefit

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**SOTA Benchmark Summary (World Models - 2023-2025):**

| Method | Type | Performance | Efficiency | Year | Source |
|--------|------|-------------|------------|------|--------|
| STORM | Transformer WM | 126.7% HNS (Atari 100k) | Standard Transformer | 2023 | NeurIPS |
| DIAMOND | Diffusion WM | 1.46 HNS (Atari 100k) | Iterative denoising | 2024 | NeurIPS |
| StateSpaceDiffuser | SSM+Diffusion | 10x longer context | SSM for memory | 2025 | NeurIPS |
| Genie | Foundation WM | 11B params, controllable | Large-scale | 2024 | DeepMind |
| DreamerV3 | RSSM WM | 200+ Atari games solved | JAX optimized | 2023 | JMLR |

**Key Insights for Threshold Setting:**
- Atari 100k: STORM baseline at 126.7% HNS, DIAMOND at 1.46 HNS
- Video prediction: FVD ranges 50-200 depending on dataset complexity
- Efficiency: Pure diffusion typically 5-10x slower than pure SSM
- Our target: Match diffusion quality (FVD ratio ≤ 1.05) with SSM-like efficiency (2-3x speedup)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Target effect size (Cohen's d): 0.8 (large effect for efficiency gain)
- Required runs per condition: n ≥ 20 (α=0.05, power=0.8)
- Total experimental runs: 4 conditions × 20 runs × 3 datasets = 240 runs

**Test Specification:**
- Primary test: Paired t-test (same random seeds across conditions)
- Multi-comparison correction: Bonferroni for 3 primary metrics (FVD, LPIPS, Latency)
- Significance level: α = 0.05/3 = 0.017 (per-metric after correction)

**Report Format:**
- Mean ± Std Dev for each metric
- 95% Confidence Intervals
- Cohen's d effect size
- p-values (one-tailed for directional predictions)

**Ablation Studies:**
1. SSM-only vs Duet Dynamics (quality comparison)
2. Diffusion-only vs Duet Dynamics (efficiency comparison)
3. StateSpaceDiffuser vs Duet Dynamics (architecture comparison)
4. Gating threshold sensitivity (τ ∈ {50th, 70th, 90th percentile})
5. Ensemble size sensitivity (K ∈ {2, 3, 5})

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type:** Methodological
- **Statement:** We introduce *Duet Dynamics*, a novel dual-pathway world model architecture that functionally separates deterministic dynamics (handled by SSM) from stochastic dynamics (handled by Diffusion) using learned uncertainty gating, achieving an efficiency-quality tradeoff superior to both unified approaches.
- **Novelty:** Unlike StateSpaceDiffuser (SSM for memory/context) or DiS (SSM as diffusion backbone), our approach uses SSM for *functional dynamics separation* based on prediction uncertainty—directly inspired by duet predictive coding from neuroscience.

**Secondary Contributions:**
- **Theoretical:** First application of duet predictive coding (dual prediction error signals) principle to hybrid SSM-Diffusion architecture design
- **Practical:** Real-time capable world model achieving 2-3x faster inference than pure diffusion while maintaining quality parity, enabling robotics/RL deployment
- **Empirical:** Comprehensive ablation study demonstrating that uncertainty-gated routing outperforms fixed routing and unified architectures across multiple benchmarks

---

## 3. Key Related Work

### Foundation Sources (MUST CITE)

1. **"Mamba: Linear-Time Sequence Modeling with Selective State Spaces"** (2023)
   - Authors: Albert Gu, Tri Dao
   - URL: https://arxiv.org/abs/2312.00752
   - Semantic Scholar ID: 7bbc7595196a0606a07506c4fb1473e5e87f6082
   - Citations: 5,601
   - Key Finding: Selective SSM achieves 5x faster inference than Transformers with content-based reasoning; foundation for SSM pathway

2. **"Video Diffusion Models"** (2022)
   - Authors: Jonathan Ho, Tim Salimans, et al.
   - URL: https://arxiv.org/abs/2204.03458
   - Semantic Scholar ID: 3b2a675bb617ae1a920e8e29d535cdf27826e999
   - Citations: 2,274
   - Key Finding: First diffusion model for video with spatial-temporal extension; foundation for diffusion pathway

3. **"Duet model unifies diverse neuroscience experimental findings on predictive coding"** (2025)
   - Authors: J. Meng, Jordan M. Ross, Jordan P. Hamm, Xiao-Jing Wang
   - URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC12338523
   - Semantic Scholar ID: 88766801195c3c9584ee6688737da30a02f147b2
   - Key Finding: Brain uses dual prediction error signals (positive/negative) for deviance detection; inspiration for functional separation

### Comparison Baselines

4. **"StateSpaceDiffuser: Bringing Long Context to Diffusion World Models"** (2025)
   - Authors: INSAIT Research Team
   - URL: https://insait-institute.github.io/StateSpaceDiffuser/
   - Key Finding: SSM for memory/context in diffusion; baseline for architecture comparison (memory vs dynamics separation)

5. **"STORM: Efficient Stochastic Transformer based World Models"** (2023)
   - Authors: Weipu Zhang, Gang Wang, et al.
   - Semantic Scholar ID: c433c7f0a1c5fe3449274c7234ff5a8fc4f3c3ff
   - Citations: 101
   - Key Finding: 126.7% human performance on Atari 100k; Transformer-based baseline

6. **"DIAMOND: Diffusion for World Modeling"** (2024)
   - URL: https://proceedings.neurips.cc/paper_files/paper/2024
   - Key Finding: 1.46 HNS on Atari 100k with diffusion world model; diffusion-only baseline

### Gap Evidence

7. **"Vision Mamba: Efficient Visual Representation Learning"** (2024)
   - Authors: Lianghui Zhu, Bencheng Liao, et al.
   - Semantic Scholar ID: 38c48a1cd296d16dc9c56717495d6e44cc354444
   - Citations: 1,439
   - Key Finding: 2.8x faster than ViT, 86.8% memory reduction; validates SSM for visual understanding

8. **"Is Sora a World Simulator?"** (2024)
   - Authors: Zheng Zhu, Xiaofeng Wang, et al.
   - Semantic Scholar ID: d7fbdba317e195c3b49dbcdb14b7b52a05bfb3f4
   - Key Finding: Identifies physical simulation and causality as open challenges in video world models

### Implementation References

9. **state-spaces/mamba** (GitHub)
   - URL: https://github.com/state-spaces/mamba
   - Stars: 12,000+
   - Key Feature: Official Mamba implementation with hardware-aware selective scan

10. **huggingface/diffusers** (GitHub)
    - URL: https://github.com/huggingface/diffusers
    - Stars: 25,000+
    - Key Feature: Video diffusion pipelines, consistency models, DiT implementations

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does uncertainty-gated routing between SSM and Diffusion pathways achieve a measurable efficiency-quality tradeoff improvement in world model prediction tasks?"
- Maps to: Primary Prediction (P1)
- Verification type: Empirical measurement (FVD ratio, Latency ratio)
- Critical: MUST PASS for Phase 2B to proceed
- Success: FVD ≤ 1.05× AND Latency ≤ 0.5× diffusion-only

**SH2 (Mechanism) - 4 Sub-Hypotheses:**
"Is the proposed 4-step causal mechanism (Input → Uncertainty → Routing → Dual Prediction → Output) the actual cause of the efficiency-quality tradeoff?"

Phase 2B will decompose into:
- **H-M1:** Ensemble SSM heads accurately estimate prediction uncertainty (Step 1 → Step 2)
- **H-M2:** Learned gating correctly routes high/low uncertainty to appropriate pathway (Step 2 → Step 3)
- **H-M3:** SSM pathway achieves quality-equivalent predictions for low-uncertainty frames (Step 3 → Step 4, SSM branch)
- **H-M4:** Sparse diffusion activation (<30%) is sufficient for high-uncertainty frames (Step 3 → Step 4, Diffusion branch)

Verification type: Causal analysis (ablation studies, mechanism probing)
Critical: Determines explanatory power of functional separation

**SH3 (Comparison):**
"Does Duet Dynamics outperform both StateSpaceDiffuser (SSM for memory) and unified baselines (pure SSM, pure Diffusion) on the efficiency-quality tradeoff?"
- Maps to: Secondary Predictions (P2, P3)
- Verification type: Comparative empirical (head-to-head benchmarks)
- Critical: Determines practical value over existing approaches
- Success: Duet Dynamics achieves P1 criteria on ≥2 of 3 benchmark domains

### Readiness Checklist

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | Hypothesis in "Under [C], if [X], then [Y] because [Z]" format | ✅ | Section 1.1 Core Statement |
| 2 | Hypothesis ID assigned | ✅ | H-DuetDynamics-v1 |
| 3 | Confidence level specified (0.0-1.0) | ✅ | 0.85 |
| 4 | Alternative hypothesis (H0) defined | ✅ | Three specific counter-claims |
| 5 | All variables have operationalization from evidence | ✅ | 8 variables with measurements |
| 6 | Causal mechanism has evidence at each step | ✅ | 4 steps with evidence table |
| 7 | Causal chain length (N) determined | ✅ | N=4 (Step 3.2) |
| 8 | Key tension identified and resolution proposed | ✅ | Mamba vs Diffusion, test dynamics vs memory |
| 9 | Key assumptions list consequences if violated | ✅ | 4 assumptions with consequences |
| 10 | At least 2 testable predictions exist | ✅ | P1 (primary), P2, P3 |
| 11 | Falsification criteria defined | ✅ | 4 failure conditions |
| 12 | Baselines identified for comparison | ✅ | StateSpaceDiffuser, STORM, DIAMOND |
| 13 | SH1, SH2, SH3 are clear starting points | ✅ | 6 total sub-hypotheses (1+4+1) |

**Readiness Status: READY FOR PHASE 2B** ✅

### Open Questions

1. **Resource Requirements:**
   - Compute: 8 A100 GPU-days specified; is this sufficient for 240 experimental runs?
   - Data: Are DMControl, Atari 100k, and RoboNet/Something-Something accessible?
   - Storage: Video data storage requirements for 3 benchmark datasets?

2. **Technical Feasibility:**
   - Mamba + Diffusers integration: Are libraries compatible or need custom integration?
   - Ensemble overhead: Will K=3-5 SSM heads fit in GPU memory with diffusion head?
   - Two-phase training: How to balance SSM training with diffusion residual training?

3. **Priority Verification Order:**
   - Recommended: SH1 (Existence) → SH2-H-M1 (Uncertainty) → SH2-H-M2 (Gating) → SH3 (Comparison)
   - Rationale: If SH1 fails, no need to verify mechanism; if uncertainty fails, gating is ineffective

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
