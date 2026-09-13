# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - S-DCCLs)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H1-SDCCL
**Confidence Level:** 0.83 (from Phase 2A Judge)

**Main Hypothesis:**
Transformer-based neural networks augmented with Soft Differentiable Cognitive Constraint Layers (S-DCCLs) that implement soft approximations of ACT-R's declarative memory activation equation (A_i = B_i + ΣW_jS_ji) and capacity-limited working memory (K slots with competitive inhibition) will demonstrate statistically significant improvements in sample efficiency (≥20% reduction in samples to reach 90% accuracy) on N-back working memory tasks compared to standard transformers with matched parameter counts, while producing error patterns that correlate positively (r > 0.5) with human behavioral data.

**Alternative Hypothesis (H0):**
S-DCCL augmentation provides no significant improvement in sample efficiency over standard transformers on N-back tasks, or produces error patterns uncorrelated with human behavioral data (r ≤ 0.5).

### 1.2 Variables

| Variable Type | Variable Name | Operationalization | Measurement |
|---------------|---------------|-------------------|-------------|
| **Independent** | S-DCCL Presence | Binary: Model with/without S-DCCL modules | Architecture configuration |
| **Independent** | S-DCCL Components | Which modules: DCCLMemory, DCCLWorkingMemory, DCCLProduction | Module ablation |
| **Dependent** | Sample Efficiency | Number of training samples to reach 90% accuracy | Learning curve analysis |
| **Dependent** | Behavioral Alignment | Pearson correlation between model and human error patterns | Statistical correlation |
| **Dependent** | Task Accuracy | Final accuracy on held-out test set | Percentage correct |
| **Controlled** | Model Parameters | Total trainable parameters (matched between conditions) | Parameter count |
| **Controlled** | Task Type | N-back working memory task (N=2, 3, 4) | Standardized benchmark |
| **Controlled** | Training Procedure | Same optimizer, learning rate schedule, batch size | Hyperparameters |
| **Moderating** | Temperature τ | Production selection temperature (annealed 1.0 → 0.1) | Softmax temperature |
| **Moderating** | Decay Rate λ | Exponential trace decay rate (0.9 - 0.99) | Decay constant |
| **Moderating** | WM Capacity K | Number of working memory slots (4, 7, 12) | Slot count |

### 1.3 Causal Mechanism

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CAUSAL MECHANISM DIAGRAM                         │
└─────────────────────────────────────────────────────────────────────────┘

[S-DCCL Modules Added]
        │
        ▼
┌───────────────────────────────────────┐
│ 1. Activation-Based Retrieval        │
│    A(t) = λA(t-1) + (1-λ)access(t)   │
│    (Exponential trace decay)          │
└───────────────────────────────────────┘
        │
        │ Creates recency/frequency bias
        ▼
┌───────────────────────────────────────┐
│ 2. Capacity-Limited Working Memory   │
│    K slots with competitive softmax  │
│    inhibition                         │
└───────────────────────────────────────┘
        │
        │ Forces selective retention
        ▼
┌───────────────────────────────────────┐
│ 3. Psychologically-Grounded          │
│    Inductive Bias                     │
│    (Human-like memory constraints)    │
└───────────────────────────────────────┘
        │
        ├──────────────────┬──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Improved     │  │ Human-Like   │  │ Interpretable│
│ Sample       │  │ Error        │  │ Cognitive    │
│ Efficiency   │  │ Patterns     │  │ States       │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Mechanistic Explanation:**

1. **Activation-Based Retrieval:** The exponential trace decay equation A(t+1) = λA(t) + (1-λ)access(t) creates a recency-weighted memory representation. Items accessed recently have higher activation, making them more retrievable. This mirrors ACT-R's base-level learning equation and provides a principled inductive bias for memory-dependent tasks.

2. **Capacity-Limited Working Memory:** The K-slot bottleneck with competitive inhibition (implemented as softmax over slot activations) forces the network to selectively maintain information. This constraint is derived from human working memory research (Cowan's 4±1 capacity limit) and prevents the network from memorizing arbitrary associations.

3. **Resulting Inductive Bias:** Together, these mechanisms create an inductive bias that aligns with human cognitive constraints. The model must (a) prioritize recent/frequent information, and (b) manage limited capacity. These are the same constraints that shape human learning on working memory tasks, potentially leading to faster convergence (sample efficiency) by restricting the hypothesis space to cognitively plausible solutions.

**Evidence for Causal Links:**

| Link | Evidence Source | Mechanism |
|------|-----------------|-----------|
| Decay → Recency Bias | ACT-R 40+ years validation (Anderson et al.) | Power-law forgetting |
| Capacity Limits → Selective Retention | Cowan (2001), Soni & Frank (2024) | 4±1 capacity limit |
| Constraints → Sample Efficiency | General inductive bias theory (Mitchell 1980) | Restricted hypothesis space |
| Human-like Constraints → Human-like Errors | Innerebner et al. (2025) | ACT-R predicts human behavior |

**Key Tension:**
The soft approximations (exponential decay instead of power-law, soft selection instead of discrete) may deviate from exact ACT-R semantics. The hypothesis assumes these approximations preserve the *qualitative* properties that matter for learning benefit, not the exact *quantitative* predictions of ACT-R.

### 1.4 Key Assumptions

| # | Assumption | Testability | Risk Level | Mitigation |
|---|------------|-------------|------------|------------|
| A1 | ACT-R's activation equation can be approximated with exponential decay while preserving qualitative memory effects | HIGH - Compare decay curves | LOW | Literature shows exponential is common approximation |
| A2 | Cognitive constraints that limit human performance are beneficial inductive biases for learning cognitive tasks | HIGH - Ablation studies | MEDIUM | Core hypothesis - if false, main claim fails |
| A3 | Working memory and N-back tasks are representative domains where ACT-R applies | HIGH - ACT-R validation literature | LOW | N-back is canonical ACT-R task |
| A4 | The parameters (λ, K, τ) can be learned from data or set from psychological literature | MEDIUM - Hyperparameter search | LOW | Literature provides principled ranges |
| A5 | Matched parameter count is sufficient control for fair comparison | MEDIUM - May need FLOP matching | LOW | Standard practice in DL comparisons |

### 1.5 Scope & Boundaries

**In Scope:**
- Working memory tasks: N-back (N=2,3,4), Sternberg item recognition
- Instruction-following tasks with memory requirements
- Transformer architectures (encoder, decoder, encoder-decoder)
- Standard PyTorch implementation
- Single-GPU training regime

**Out of Scope:**
- Perceptual tasks (vision, audition) - ACT-R not validated
- Motor control tasks - different cognitive module
- Language generation tasks without memory component
- Multi-GPU / distributed training
- Non-transformer architectures (CNNs, RNNs alone)

**Explicit Limitations:**
1. Soft approximations deviate from exact ACT-R predictions
2. Exponential decay is simpler than ACT-R's power-law forgetting
3. Only tests declarative memory module, not procedural learning
4. Does not claim to be a complete cognitive model, only borrowed constraints

**Boundary Conditions:**
- Task must require memory retention over multiple steps
- Task must have established human behavioral data for comparison
- Model must have sufficient capacity to benefit from constraints (very small models may be too constrained already)

### 1.6 Testable Predictions

**Primary Prediction:**
> **P1 (Sample Efficiency):** A transformer augmented with S-DCCL modules (DCCLMemory + DCCLWorkingMemory) will reach 90% accuracy on 2-back tasks using ≤80% of the training samples required by an equivalent-parameter standard transformer (i.e., ≥20% sample efficiency improvement).

**Quantification:** Sample efficiency ratio = Samples_baseline / Samples_SDCCL ≥ 1.25

**Secondary Predictions:**

> **P2 (Behavioral Alignment):** The S-DCCL model's error patterns on N-back tasks (proportion of misses, false alarms, lure confusions by serial position) will correlate positively with human behavioral data from published N-back studies (Pearson r > 0.5, p < 0.05).

> **P3 (Capacity Scaling):** As N increases in N-back tasks (2→3→4), the S-DCCL model with K=4 working memory slots will show accuracy degradation similar to human participants (Cohen's d for accuracy drop 2-back vs 4-back within 0.5 SD of human data), while baseline transformers will show flatter degradation curves.

> **P4 (Interpretable States):** The learned activation values in S-DCCL memory slots will be interpretable: items matching the target N positions back will have higher activation (measured by activation rank) than distractor positions in >80% of correct trials.

**Falsification Criteria:**

| Prediction | Falsified If |
|------------|--------------|
| P1 | Sample efficiency ratio < 1.10 (less than 10% improvement) across 3+ random seeds |
| P2 | Behavioral correlation r < 0.3 or p > 0.10 |
| P3 | S-DCCL shows >2x flatter capacity scaling than humans |
| P4 | Target activation rank is not higher than chance (50%) |

**Strong Falsification (Reject Hypothesis):**
If P1 AND P2 are both falsified, the main hypothesis is rejected. P3 and P4 provide additional support but are not individually sufficient for rejection.

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

This hypothesis focuses on **mechanism validation** rather than SOTA comparison. However, relevant baselines include:

| Baseline | Reference | Expected Behavior |
|----------|-----------|-------------------|
| Standard Transformer | Vaswani et al. (2017) | Full attention, no memory constraints |
| Transformer-XL | Dai et al. (2019) | Segment-level recurrence |
| DNC | Graves et al. (2016) | Differentiable external memory, generic |
| Universal Transformer | Dehghani et al. (2019) | Adaptive computation time |

**SOTA Benchmark (if applicable):**
N-back accuracy benchmarks vary by implementation. Human performance: 2-back ~85-90%, 3-back ~75-85%, 4-back ~65-75% (varies by population).

### 1.8 Statistical Verification Design

**Design Type:** Between-subjects factorial with repeated measures

**Experimental Design:**
```
Factor 1: Model Type (Between)
  - Baseline Transformer
  - S-DCCL Transformer

Factor 2: N-back Level (Within)
  - 2-back, 3-back, 4-back

Factor 3: Random Seed (Replication)
  - 5 seeds per condition
```

**Sample Size Justification:**
- 5 random seeds per condition (standard in DL experiments)
- Power analysis: With expected effect size d=0.8 for sample efficiency, n=5 provides >80% power for paired t-test (α=0.05)

**Statistical Tests:**
1. **P1 (Sample Efficiency):** One-tailed paired t-test, H1: μ_SDCCL < μ_baseline
2. **P2 (Behavioral Alignment):** Pearson correlation with Fisher z-transformation for CI
3. **P3 (Capacity Scaling):** 2×3 mixed ANOVA (Model × N-back level) for interaction effect
4. **P4 (Interpretability):** One-sample t-test against chance (50%)

**Multiple Comparison Correction:** Bonferroni correction for 4 primary predictions (α = 0.0125 per test)

**Effect Size Thresholds:**
- Small: Cohen's d = 0.2, r = 0.1
- Medium: Cohen's d = 0.5, r = 0.3
- Large: Cohen's d = 0.8, r = 0.5

---

## 2. Contribution Summary

### Theoretical Contribution
**First framework for translating cognitive architecture equations to differentiable neural modules while preserving psychological validity.** Establishes that ACT-R's mathematical equations can be approximated with differentiable operations (exponential trace decay for activation, softmax for production selection) while maintaining the qualitative properties that make them psychologically grounded. This bridges the symbolic-subsymbolic divide that has historically separated cognitive architectures from deep learning.

### Methodological Contribution
**S-DCCL module library as reusable PyTorch components.** Provides:
- `DCCLMemory`: Activation-based memory with exponential trace decay
- `DCCLWorkingMemory`: Capacity-limited K-slot memory with competitive inhibition
- `DCCLProduction`: Temperature-scaled soft production selection (if extended)

These modules can be composed with standard transformer layers and trained end-to-end with gradient descent.

### Practical Contribution
**Improved sample efficiency and interpretability on cognitive tasks.** Demonstrates that incorporating psychologically-grounded inductive biases improves learning efficiency on working memory tasks, with potential applications to:
- Intelligent tutoring systems (modeling student cognition)
- Assistive AI (human-compatible error patterns)
- Cognitive assessment tools (interpretable cognitive states)

---

## 3. Key Related Work

### Foundational Works

| Paper | Year | Relevance | How We Differ/Extend |
|-------|------|-----------|---------------------|
| Anderson et al. "ACT-R: A Theory of Higher Level Cognition" | 1998 | Defines ACT-R equations we implement | We make equations differentiable |
| Graves et al. "Neural Turing Machines" | 2014 | Differentiable external memory | Generic memory, not psychologically grounded |
| Graves et al. "Differentiable Neural Computers" | 2016 | Scalable differentiable memory | Generic, lacks cognitive constraints |

### Direct Precedents

| Paper | Year | Relevance | How We Differ/Extend |
|-------|------|-----------|---------------------|
| Innerebner et al. "Hybrid Personalization Using ACT-R" | 2025 | ACT-R + ML integration | We target working memory, not recommenders |
| Soni & Frank "Adaptive Chunking in PFC/BG Circuit" | 2024 | Neural basis for WM capacity | Computational inspiration, not direct use |
| Yang & Stocco "EVC in ACT-R" | 2023 | Motivation modeling in ACT-R | Informs production selection utility |

### Comparison Baselines

| System | Differentiable? | ACT-R Equations? | Cognitive Constraints? |
|--------|----------------|------------------|----------------------|
| pyactr | No (symbolic) | Yes | Yes |
| DNC | Yes | No (generic) | No |
| Transformer | Yes | No | No |
| **S-DCCL (Ours)** | **Yes** | **Yes (soft approx)** | **Yes** |

### Gap This Work Fills
No existing system combines (1) differentiability, (2) ACT-R-specific equations, and (3) cognitive constraints. S-DCCLs fill this gap by implementing soft approximations of ACT-R equations as differentiable PyTorch modules.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
S-DCCL modules (DCCLMemory implementing exponential trace decay, DCCLWorkingMemory implementing K-slot capacity limit) can be implemented as differentiable PyTorch modules that successfully augment transformer architectures and train end-to-end via backpropagation on N-back tasks.

*Verification:* Module implementation + successful training run + gradient flow validation

**SH2 (Mechanism):**
The exponential trace decay equation A(t+1) = λA(t) + (1-λ)access(t) creates recency-weighted memory representations such that items accessed more recently have higher activation values, and the K-slot capacity limit with competitive inhibition forces selective retention.

*Verification:* Activation analysis showing recency effect + slot usage analysis showing capacity constraint

**SH3 (Comparison):**
S-DCCL-augmented transformers demonstrate ≥20% sample efficiency improvement over matched-parameter standard transformers on N-back tasks and produce error patterns correlated (r > 0.5) with human behavioral data.

*Verification:* Learning curve comparison + behavioral correlation analysis

### Readiness Checklist

| Item | Status | Notes |
|------|--------|-------|
| Core hypothesis clarified with measurable predictions | ✅ | 4 testable predictions with falsification criteria |
| Variables operationalized | ✅ | IV, DV, CV, moderators defined |
| Causal mechanism specified | ✅ | 3-stage mechanism with evidence |
| Assumptions explicit and testable | ✅ | 5 assumptions with risk levels |
| Scope boundaries defined | ✅ | In/out scope explicit |
| Statistical design specified | ✅ | Tests, power, corrections defined |
| Baseline comparisons identified | ✅ | Transformer, DNC, pyactr |
| Sub-hypothesis decomposition preview | ✅ | SH1, SH2, SH3 outlined |

### Open Questions

1. **Decay Rate Selection:** Should λ be learned or fixed from ACT-R literature (typically d≈0.5 → λ≈0.95)? Current plan: Initialize from literature, allow fine-tuning.

2. **Working Memory Capacity K:** Should K=4 (Cowan's limit) or K=7 (Miller's magical number)? Current plan: Test K∈{4,7,12} as hyperparameter.

3. **Human Behavioral Data Source:** Which N-back dataset for behavioral alignment? Candidates: Jaeggi et al. (2010), Kane et al. (2007), or OpenNeuro N-back fMRI datasets.

4. **Transformer Base Architecture:** Which transformer variant? Options: vanilla encoder, GPT-style decoder, BERT-style. Current plan: Start with vanilla encoder for simplicity.

5. **Production Module Inclusion:** SH1-SH3 focus on memory modules. Should production selection (DCCLProduction) be included in initial experiments or deferred?

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
