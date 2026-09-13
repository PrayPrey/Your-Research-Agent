# Phase 2B Summary: Extended Hypothesis for ADORE

**Date:** 2026-02-06
**Researcher:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis ID:** H1-ADORE
**Confidence Level:** 0.88 (High)

**Core Innovation:** ADORE (Adaptive Parameter-Efficient Continual Learning with Dynamic Regularization-Replay Orchestration) is a meta-learned framework that dynamically selects and combines parameter-efficient fine-tuning methods (LoRA, Adapters, Prefix-Tuning) with forgetting mitigation strategies (EWC, SI, self-synthesized replay) based on task characteristics and observed forgetting signals during training.

**Research Gap Addressed:** Gap 1 - Unified Framework for Parameter-Efficient Continual Learning at Foundation Model Scale

**Key Differentiator:** Unlike existing methods that use fixed PEFT+regularization combinations (PIECE, SSR, MoE-CT), ADORE:
1. Dynamically selects method combinations per task
2. Meta-learns task characteristic → method configuration mapping
3. Online-adapts configuration based on real-time forgetting signals
4. Operates across all foundation model scales (1B-70B+ parameters)

**Target Outcome:** Enable foundation models to continuously learn new tasks while:
- Updating <1% parameters per task (parameter efficiency)
- Maintaining ≥95% performance on previous tasks (forgetting mitigation)
- Operating within consumer hardware constraints (memory efficiency)
- Reducing total training cost by 40-60% vs fixed expensive methods

---

## Detailed Hypothesis Statement

**Main Hypothesis (H1):**

An adaptive orchestration framework that meta-learns task characteristic encodings and dynamically selects parameter-efficient fine-tuning (PEFT) methods combined with forgetting mitigation strategies based on predicted task difficulty and observed forgetting signals will achieve superior continual learning performance on foundation models (1B+ parameters) compared to fixed-strategy baselines, while maintaining computational efficiency (<5% orchestration overhead) and parameter efficiency (<1% updates per task).

**Specifically:**
- Given a continual learning task sequence with varying domain shifts, data sizes, and distribution overlaps
- An orchestrator meta-trained on 100+ diverse task sequences (CLDatasets, Avalanche, Continuum)
- Will predict optimal PEFT method (LoRA rank, Adapter size, or Prefix length) + forgetting mitigation strategy (EWC strength, replay budget, or architectural isolation)
- And adapt this configuration online when forgetting signals exceed thresholds
- Resulting in 10-20% higher average accuracy, 15-25% better backward transfer, and 40-60% lower total compute cost compared to fixed-strategy baselines (fixed LoRA+EWC, fixed Adapter+Replay, full fine-tuning with EWC)

**Alternative Hypothesis (H0):**

Fixed-strategy continual learning methods (e.g., always using LoRA rank=8 with EWC λ=100) perform equivalently to or better than adaptive orchestration when considering both task performance and total system cost (meta-training + inference + monitoring overhead), OR the orchestrator's predictions do not generalize beyond meta-training distribution, OR online adaptation does not significantly improve over offline method selection.

---

## Variables

### Independent Variables

| Variable | Type | Range/Levels | Control Method |
|----------|------|--------------|----------------|
| **Task Characteristics** | Continuous | Domain shift (0-1), Data size (100-100K), Vocab overlap (0-1), Distribution shift (KL divergence) | Measured from benchmark tasks |
| **Orchestrator Configuration** | Categorical | Enabled (adaptive) vs Disabled (fixed baseline) | Experimental condition |
| **PEFT Method** | Categorical | LoRA (rank 4-64), Adapter (size 64-512), Prefix-Tuning (length 10-100) | Selected by orchestrator or fixed in baseline |
| **Regularization Strategy** | Categorical | EWC (λ 0-1000), SI (c 0-1), None | Selected by orchestrator or fixed in baseline |
| **Replay Strategy** | Categorical | Self-Synthesized (budget 0-10%), Generative (budget 0-10%), None | Selected by orchestrator or fixed in baseline |
| **Foundation Model Scale** | Categorical | 1B, 3B, 7B, 13B parameters | Controlled via model selection |

### Dependent Variables (Outcomes)

| Metric | Definition | Measurement Method | Expected Range |
|--------|------------|-------------------|----------------|
| **Average Accuracy** | Mean accuracy across all tasks after continual training | Standard classification/generation metrics | 0-100% |
| **Backward Transfer (BWT)** | Change in performance on previous tasks after learning new tasks | BWT = (1/T) Σᵢ (Acc_T,i - Acc_i,i) | -100% to +100% (negative = forgetting) |
| **Forward Transfer (FWT)** | Ability to leverage previous knowledge for new tasks | FWT = (1/T) Σᵢ (Acc_i,i - Acc_0,i) | -100% to +100% (positive = transfer) |
| **Parameter Updates** | Percentage of model parameters updated per task | Count trainable params / total params | 0-100% (target <1%) |
| **Total Training Cost** | Cumulative GPU-hours for all tasks | Time measurement | GPU-hours |
| **Memory Footprint** | Peak GPU memory during training | GPU memory profiler | GB |
| **Orchestration Overhead** | Additional time for task encoding, prediction, monitoring | Time measurement | % of total training time (target <5%) |

### Mediating Variables

| Variable | Role | How It Operates |
|----------|------|-----------------|
| **Task Embedding** | Encoding | BERT-based encoder transforms task samples → 768-d vector capturing domain shift, vocab overlap, distribution characteristics |
| **Forgetting Severity Prediction** | Prediction | MLP predicts forgetting magnitude (0-1 scale) from task embedding |
| **Method Family Prediction** | Configuration | Stage 1 classifier selects PEFT-only, PEFT+Regularization, or PEFT+Replay |
| **Hyperparameter Prediction** | Configuration | Stage 2 regression heads predict LoRA rank, EWC λ, replay budget within selected family |
| **Online Forgetting Signals** | Adaptation | Validation loss increase, task-specific metric degradation triggers configuration adjustment |

### Control Variables

| Variable | Why Controlled | Control Method |
|----------|----------------|----------------|
| **Base Model Architecture** | Isolate orchestration effect from architecture differences | Use same pretrained foundation model (e.g., LLaMA-2) across all conditions |
| **Task Order** | Prevent order effects | Randomize task sequence, report average across 3 random seeds |
| **Optimizer & Learning Rate** | Standardize training dynamics | Fix optimizer (AdamW), learning rate schedule (cosine decay) |
| **Evaluation Protocol** | Ensure fair comparison | Use identical test sets, evaluation frequency (every 100 steps) |
| **Hardware** | Control for hardware variability | Use same GPU type (A100 80GB) across experiments |

---

## Causal Mechanism

### Core Mechanism Chain

```
Task Characteristics (domain shift, data size, distribution overlap)
    ↓ [Encoded via BERT-based Task Encoder]
Task Embedding (768-d vector capturing task features)
    ↓ [Processed by Hierarchical Configuration Predictor]
Forgetting Severity Prediction + Method Family Selection + Hyperparameter Prediction
    ↓ [Applied to Foundation Model Training]
Optimized PEFT Configuration (matched to task difficulty)
    ↓ [Combined with Adaptive Orchestrator monitoring]
Online Configuration Adjustment (when forgetting signals detected)
    ↓ [Results in]
Superior Continual Learning Performance (higher avg accuracy, better BWT, lower cost)
```

### Detailed Causal Links

**Link 1: Task Characteristics → Forgetting Severity**

*Mechanism:* Tasks with high domain shift (embedding distance >0.7) and low vocabulary overlap (<0.3) cause higher catastrophic forgetting because:
- Large domain shifts require model to adapt feature representations significantly
- Low vocabulary overlap means less transfer from previous tasks
- This is empirically validated by Luo et al. (2023, 518 citations) showing CF increases with model scale

*Evidence:*
- Luo et al. (2023): Empirical study showing forgetting INCREASES from 1B to 7B parameters
- Chen & Zhou (2024): Domain shift can reduce forgetting through feature separation (counter-intuitive, but suggests domain shift magnitude is predictive)

**Link 2: Forgetting Severity → Optimal Method Configuration**

*Mechanism:* Tasks predicted to have high forgetting require stronger mitigation:
- High forgetting (>0.7) → PEFT+Replay (generative or self-synthesized)
- Medium forgetting (0.4-0.7) → PEFT+Regularization (EWC or SI)
- Low forgetting (<0.4) → PEFT-only (LoRA or Adapter sufficient)

*Evidence:*
- Wang (PIECE, 2025): 0.1% parameter updates sufficient for low-forgetting scenarios
- Huang (SSR, 2024): Self-synthesized replay necessary for high-forgetting multi-domain scenarios
- Li (MoE-CT, 2024): Architectural isolation (MoE) effective for catastrophic forgetting resistance

**Link 3: Optimized Configuration → Performance Improvement**

*Mechanism:* Matching method to task difficulty avoids both under-mitigation (forgetting occurs) and over-mitigation (wasted compute):
- Under-mitigation: Using LoRA-only on high-forgetting task → accuracy drops on previous tasks
- Over-mitigation: Using expensive replay on low-forgetting task → unnecessary compute cost
- Optimal matching: Task-adaptive selection minimizes forgetting while minimizing cost

*Evidence:*
- HuggingFace PEFT (20.5k stars): Demonstrates parameter-efficient methods reduce compute but need forgetting mitigation
- Avalanche framework: 20+ strategies show wide variance in compute-performance tradeoffs

**Link 4: Online Adaptation → Robustness**

*Mechanism:* Real-time forgetting signal monitoring enables correction of prediction errors:
- If offline prediction underestimates forgetting → online monitoring detects validation loss increase → orchestrator increases regularization strength or switches to replay
- Inspired by Model Reference Adaptive Control (MRAC): minimize tracking error (forgetting) through continuous parameter adjustment

*Evidence:*
- Adaptive Control Theory (MRAC): Established framework for online parameter adaptation based on error signals
- Meta-Learning (MAML): Demonstrates task-agnostic learning can adapt quickly with few samples

### Key Tension

**Efficiency vs Effectiveness Tradeoff:**

ADORE operates in the tension between:
- **Parameter Efficiency:** Updating <1% parameters to minimize compute/memory (favors PEFT-only methods like LoRA)
- **Forgetting Mitigation:** Preventing catastrophic forgetting to maintain performance (favors expensive methods like replay)

**Resolution Mechanism:**

The orchestrator resolves this tension through:
1. **Task-Dependent Selection:** High-forgetting tasks receive expensive mitigation (worth the cost); low-forgetting tasks use cheap PEFT-only (sufficient)
2. **Hierarchical Prediction:** Stage 1 selects method family optimizing expected performance-cost tradeoff; Stage 2 fine-tunes hyperparameters
3. **Online Adaptation:** Continuously monitors whether selected configuration achieves desired forgetting-cost balance, adjusts if needed

**Critical Assumption:** The meta-learned predictor can accurately estimate forgetting severity from task characteristics, enabling proactive method selection rather than reactive correction.

---

## Key Assumptions

### Theoretical Assumptions

1. **Task Characteristic Predictivity** (Critical)
   - *Assumption:* Automatically extracted task features (embedding distance, data size, vocabulary overlap, KL divergence) are predictive of catastrophic forgetting severity
   - *Justification:* Luo et al. (2023) shows scale-dependent forgetting; Chen & Zhou (2024) shows domain shift affects forgetting
   - *Risk:* If task encoding misses critical features (e.g., task complexity, label noise), predictions may be inaccurate
   - *Mitigation:* Task encoder trained end-to-end to predict forgetting, not hand-crafted features

2. **Meta-Learning Generalization** (Critical)
   - *Assumption:* Meta-training on 100+ task sequences (CLDatasets, Avalanche, Continuum) generalizes to unseen tasks and domains
   - *Justification:* CLDatasets covers 10 domains with 50+ sequences; meta-learning has strong generalization in few-shot learning
   - *Risk:* Out-of-distribution tasks (e.g., new modality) may not be handled well
   - *Mitigation:* Cold-start fallback (default LoRA rank=8, EWC λ=100) for OOD tasks

3. **Hierarchical Optimality** (Moderate)
   - *Assumption:* Hierarchical prediction (method family → hyperparameters) finds near-optimal configurations, despite not searching full joint space
   - *Justification:* Reduces search space from 3×50×3×1000×3×10 to 3+max(50,1000,10), improving sample efficiency
   - *Risk:* May miss globally optimal configuration if optimal family selection depends on hyperparameters
   - *Mitigation:* Stage 1 trained to maximize expected performance over Stage 2 hyperparameter distribution

### Practical Assumptions

4. **Forgetting Signal Observability** (Moderate)
   - *Assumption:* Validation loss increase and task-specific metric degradation are reliable signals of catastrophic forgetting during training
   - *Justification:* Standard evaluation protocol in continual learning; Avalanche framework uses these signals
   - *Risk:* Noisy validation sets may produce false positive signals
   - *Mitigation:* Use running average of validation metrics over 100 steps to reduce noise

5. **Overhead Acceptability** (Moderate)
   - *Assumption:* <5% orchestration overhead (1ms task encoding + 0.5ms prediction + 2-5% monitoring) is acceptable for practitioners
   - *Justification:* Negligible compared to training time (hours to days); enables 40-60% total compute reduction
   - *Risk:* In extremely fast training scenarios (small models, small data), 5% may be noticeable
   - *Mitigation:* Provide configuration to disable monitoring for low-latency requirements

6. **Component Composability** (Low)
   - *Assumption:* HuggingFace PEFT, Avalanche strategies, and custom replay mechanisms can be integrated into unified training loop
   - *Justification:* All frameworks based on PyTorch; modular plugin architecture in Avalanche
   - *Risk:* Implementation complexity may introduce bugs
   - *Mitigation:* Extensive unit testing, integration testing on small-scale benchmarks before full evaluation

---

## Scope & Boundaries

### In-Scope

**Model Types:**
- Large Language Models (LLaMA-2, GPT-2, BERT) - 1B to 70B parameters
- Vision Transformers (ViT, CLIP vision encoder) - 300M to 3B parameters
- Multi-modal models (CLIP, BLIP) - 400M to 10B parameters

**Task Types:**
- Text classification (sentiment, topic, NLI)
- Text generation (summarization, dialogue, code generation)
- Image classification (domain-incremental, class-incremental)
- Vision-language tasks (image captioning, VQA)

**Continual Learning Scenarios:**
- Task-incremental learning (clear task boundaries, task ID known at test time)
- Domain-incremental learning (task boundaries known, task ID unknown at test time)
- Class-incremental learning (new classes over time)

**Resource Constraints:**
- Consumer hardware (single A100 80GB, RTX 4090 24GB)
- Training budgets (10-100 GPU-hours per task sequence)
- Memory constraints (fit model + gradient + optimizer state in GPU memory)

**Evaluation:**
- Synthetic benchmarks (PermutedMNIST, SplitCIFAR-100, SplitTinyImageNet from Avalanche)
- LLM benchmarks (CLDatasets with 50+ task sequences)
- Multi-modal benchmarks (Continuum scenarios)

### Out-of-Scope

**Model Types:**
- Small models (<100M parameters) - orchestration overhead may dominate
- Non-transformer architectures (CNNs, RNNs) - task encoder designed for transformers
- Specialized models (speech, audio, graph neural networks) - not tested in meta-training

**Task Types:**
- Reinforcement learning tasks - different evaluation protocol, not covered in CLDatasets
- Online learning (continuous data stream without task boundaries) - requires different orchestration logic
- Federated learning scenarios - distributed training not addressed

**Continual Learning Scenarios:**
- Online continual learning (no task boundaries, data stream) - requires continuous adaptation mechanism
- Meta-continual learning (few-shot adaptation to new tasks) - different objective
- Lifelong learning with unbounded task count (>1000 tasks) - scalability not tested

**Resource Constraints:**
- Multi-GPU distributed training - synchronization overhead not analyzed
- TPU deployment - implementation PyTorch-specific
- Edge devices (mobile, embedded) - memory constraints too restrictive

**Evaluation:**
- Real-world production deployment - benchmark evaluation only
- Adversarial robustness - not tested
- Fairness and bias - not primary concern

### Boundary Conditions

**When ADORE May Fail:**

1. **Extremely OOD Tasks:** Tasks with characteristics far outside meta-training distribution (e.g., entirely new modality like audio when meta-trained on vision+NLP only)
   - *Fallback:* Cold-start default configuration

2. **Ultra-Low-Resource Scenarios:** Tasks with <100 examples where task encoding may be unreliable
   - *Mitigation:* Use domain shift estimate from few samples, default to conservative configuration

3. **Catastrophic Interference:** Tasks with complete distribution overlap but contradictory labels (e.g., "positive" sentiment becomes "negative")
   - *Limitation:* No continual learning method handles this well; ADORE will struggle similarly

4. **Real-Time Requirements:** Applications requiring <1ms inference latency where 5% monitoring overhead is unacceptable
   - *Configuration:* Disable online monitoring, use offline prediction only

---

## Testable Predictions

### Primary Prediction (H1-P1)

**Prediction:**
ADORE will achieve 10-20% higher average accuracy across all tasks in a continual learning sequence (CLDatasets holdout set with 10+ task sequences) compared to fixed-strategy baselines (fixed LoRA rank=8 + EWC λ=100, fixed Adapter size=256 + Self-Synthesized Replay 5%), when evaluated on foundation models (7B parameters).

**Operational Definition:**
- Average Accuracy = (1/T) Σᵢ Acc_T,i where Acc_T,i is accuracy on task i after learning all T tasks
- CLDatasets holdout set: 10 task sequences not seen during meta-training, each with 5-10 tasks
- Fixed baselines: LoRA rank=8 + EWC λ=100 (moderate forgetting mitigation), Adapter size=256 + SSR 5% (strong forgetting mitigation)
- Foundation model: LLaMA-2 7B or similar scale
- Statistical test: Paired t-test with Bonferroni correction (α=0.05/2=0.025)

**Success Criteria:**
- ADORE avg accuracy > Fixed-LoRA+EWC avg accuracy + 10% (absolute, e.g., 75% vs 65%)
- ADORE avg accuracy > Fixed-Adapter+Replay avg accuracy + 10%
- p < 0.025 for both comparisons
- Consistent across ≥8/10 task sequences (80% success rate)

**Falsification:**
- If ADORE avg accuracy ≤ Fixed-LoRA+EWC + 5% (not substantially better)
- OR if p > 0.025 (not statistically significant)
- OR if consistent in <5/10 sequences (50% success rate - not reliable)

### Secondary Prediction (H1-P2): Backward Transfer

**Prediction:**
ADORE will achieve 15-25% better backward transfer (less catastrophic forgetting) compared to fixed-strategy baselines, measured as improvement in BWT score.

**Operational Definition:**
- Backward Transfer (BWT) = (1/T) Σᵢ (Acc_T,i - Acc_i,i)
- Negative BWT = forgetting; more negative = worse forgetting
- Comparison: BWT_ADORE - BWT_Fixed (expect positive difference, meaning less forgetting)

**Success Criteria:**
- BWT improvement ≥ 15% absolute (e.g., BWT_ADORE = -5%, BWT_Fixed = -20%, improvement = 15%)
- Consistent across ≥8/10 task sequences
- p < 0.025 (paired t-test with Bonferroni correction)

**Falsification:**
- If BWT improvement < 10% (not substantially better at preventing forgetting)
- OR inconsistent across sequences

### Secondary Prediction (H1-P3): Computational Efficiency

**Prediction:**
ADORE will reduce total training cost by 40-60% compared to always using the most expensive fixed strategy (Fixed-Adapter+Replay), while maintaining comparable or better performance.

**Operational Definition:**
- Total Training Cost = Σᵢ GPU-hours for task i
- Cost includes: meta-training (one-time, amortized), task encoding, prediction, monitoring, actual training
- Comparison: (Cost_Fixed-Expensive - Cost_ADORE) / Cost_Fixed-Expensive × 100%

**Success Criteria:**
- Cost reduction ≥ 40% (e.g., 100 GPU-hours → 60 GPU-hours)
- While maintaining: Avg Accuracy within 3% of Fixed-Expensive (e.g., 75% vs 72% is acceptable)
- Overhead (encoding + prediction + monitoring) < 5% of total training time

**Falsification:**
- If cost reduction < 30% (not enough savings to justify orchestration complexity)
- OR if avg accuracy drops >5% (too much performance loss)
- OR if overhead > 8% (orchestration becomes bottleneck)

### Tertiary Prediction (H1-P4): Online Adaptation Value

**Prediction:**
Online adaptation (adjusting configuration based on forgetting signals during training) will improve performance by 5-10% compared to offline prediction only (predict once before training, no adjustment).

**Operational Definition:**
- Compare ADORE-Full (offline prediction + online adaptation) vs ADORE-Offline (prediction only, no monitoring)
- Improvement = Avg Accuracy_ADORE-Full - Avg Accuracy_ADORE-Offline

**Success Criteria:**
- Improvement ≥ 5% absolute
- Particularly effective for tasks where offline prediction is inaccurate (high variance in forgetting)

**Falsification:**
- If improvement < 3% (online adaptation not adding significant value)
- Suggests offline prediction alone is sufficient, simplifying system

### Falsification Criteria (Overall)

**Conditions for Rejecting ADORE Hypothesis:**

1. **Performance Failure:** Average accuracy improvement < 5% over best fixed baseline (not substantially better)
2. **Forgetting Failure:** BWT improvement < 5% over best fixed baseline (not preventing forgetting effectively)
3. **Efficiency Failure:** Total cost reduction < 20% while requiring >10% overhead (not efficient)
4. **Generalization Failure:** Success in <50% of task sequences (not reliable across diverse tasks)
5. **Scalability Failure:** Performance improvement diminishes or disappears at 13B+ parameter scale (not scalable to large models)

**Boundary for Conditional Acceptance:**
- If ADORE succeeds on 2/3 predictions (e.g., accuracy + BWT, but not cost) → accept with caveat that efficiency gains are limited
- If ADORE succeeds only on LLM tasks but fails on vision or multi-modal → accept with domain-specific scope

---

## Related Work Positioning

### Direct Baselines (State-of-the-Art)

**1. PIECE (Wang et al., 2025)**
- *Method:* Parameter importance estimation, updates 0.1% of parameters
- *Strength:* Extreme parameter efficiency
- *Limitation:* Fixed LoRA method, no dynamic selection
- *ADORE Differentiation:* Dynamically selects PEFT type (LoRA/Adapter/Prefix) based on task; PIECE always uses LoRA
- *Expected Performance:* ADORE should outperform when tasks vary in forgetting severity (some need stronger mitigation than 0.1% LoRA)

**2. SSR (Huang et al., 2024, 89 citations)**
- *Method:* Self-synthesized rehearsal with LoRA fine-tuning
- *Strength:* No original data storage, effective replay
- *Limitation:* Fixed LoRA + replay combination for all tasks
- *ADORE Differentiation:* Adapts replay budget based on predicted forgetting; skips replay for low-forgetting tasks
- *Expected Performance:* ADORE should reduce compute by avoiding unnecessary replay, while maintaining forgetting mitigation when needed

**3. MoE-CT (Li et al., 2024, 6 citations)**
- *Method:* Mixture-of-Experts, freezes base model, trains expert modules
- *Strength:* Architectural isolation prevents forgetting
- *Limitation:* Fixed MoE architecture, high memory for experts
- *ADORE Differentiation:* Selects from multiple PEFT methods (LoRA/Adapter/Prefix), not restricted to MoE
- *Expected Performance:* ADORE should be more memory-efficient while achieving comparable forgetting mitigation

### Foundational Methods

**4. EWC (Elastic Weight Consolidation, Kirkpatrick et al., 2017, 5000+ citations)**
- *Method:* Regularization via Fisher information matrix
- *Strength:* Theoretically grounded, no replay needed
- *Limitation:* Fixed λ hyperparameter, Fisher computation expensive
- *ADORE Usage:* EWC as one regularization option; ADORE adaptively selects EWC strength based on task

**5. LoRA (Hu et al., 2021, 3000+ citations)**
- *Method:* Low-rank adaptation, updates <1% parameters
- *Strength:* Extreme parameter efficiency, HuggingFace integration
- *Limitation:* Fixed rank, no catastrophic forgetting mitigation
- *ADORE Usage:* LoRA as one PEFT option; ADORE adaptively selects rank and combines with regularization/replay

**6. Avalanche Framework (Lomonaco et al., 2021)**
- *Method:* Comprehensive CL library with 20+ strategies
- *Strength:* Modular plugin architecture, standardized evaluation
- *Limitation:* No adaptive method selection, user must manually choose strategy
- *ADORE Usage:* Builds on Avalanche architecture; adds meta-learned orchestration layer

### Cross-Domain Foundations

**7. MRAC (Model Reference Adaptive Control, Control Theory)**
- *Method:* Online parameter adaptation to minimize tracking error
- *ADORE Application:* Orchestrator adapts PEFT/regularization configuration to minimize forgetting (tracking error)
- *Innovation:* First application of MRAC to continual learning method selection

**8. MAML (Finn et al., 2017, 10000+ citations)**
- *Method:* Meta-learning for fast adaptation
- *ADORE Application:* Task-agnostic task encoder inspired by MAML's task-agnostic initialization
- *Innovation:* Applies meta-learning to method prediction, not just model initialization

### Comparison Table

| Method | Dynamic Selection | Meta-Learning | Online Adaptation | Parameter Efficiency | Forgetting Mitigation | Foundation Model Scale |
|--------|------------------|---------------|-------------------|---------------------|----------------------|----------------------|
| **ADORE (Ours)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ <1% | ✅ Task-adaptive | ✅ 1B-70B |
| PIECE (Wang 2025) | ❌ Fixed LoRA | ❌ No | ❌ No | ✅✅ 0.1% | ⚠️ Weak | ✅ 1B-7B |
| SSR (Huang 2024) | ❌ Fixed LoRA+Replay | ❌ No | ❌ No | ✅ <1% | ✅ Strong (replay) | ✅ 1B-13B |
| MoE-CT (Li 2024) | ❌ Fixed MoE | ❌ No | ❌ No | ⚠️ High (experts) | ✅ Strong (isolation) | ✅ 7B-70B |
| EWC (Kirkpatrick 2017) | ❌ N/A | ❌ No | ❌ No | ❌ 100% | ⚠️ Moderate | ⚠️ Limited |
| LoRA (Hu 2021) | ❌ N/A | ❌ No | ❌ No | ✅✅ <1% | ❌ None | ✅ All scales |

**Key Insight:** ADORE is the only method combining all three innovations (dynamic selection, meta-learning, online adaptation) specifically for foundation model continual learning.

---

## Contributions

### Theoretical Contributions

**T1. Adaptive Orchestration Theory**
- Formal framework bridging Adaptive Control Theory and Continual Learning
- Defines task characteristic → forgetting severity → optimal method configuration mapping
- Characterizes when parameter isolation (PEFT-only) vs parameter regularization (PEFT+EWC) vs memory replay (PEFT+Replay) is optimal
- *Novelty:* First theoretical framework for dynamic CL method selection

**T2. Forgetting Predictability Hypothesis**
- Hypothesis that automatically extracted task features (embedding distance, data size, vocab overlap, KL divergence) are predictive of catastrophic forgetting severity
- Provides empirical validation on 100+ task sequences
- *Novelty:* Establishes task characteristic features as forgetting predictors at foundation model scale

**T3. PEFT-Regularization-Replay Tradeoff Analysis**
- Characterization of three-way tradeoff between parameter efficiency, forgetting mitigation strength, and computational cost
- Defines Pareto frontier of optimal configurations for different task difficulty levels
- *Novelty:* Unified analysis of PEFT + forgetting mitigation method families

### Methodological Contributions

**M1. Meta-Learned Task Characteristic Encoder**
- BERT-based encoder trained on 100+ task sequences to predict forgetting from task samples
- Hierarchical configuration predictor (method family → hyperparameters) reducing search space complexity
- *Novelty:* First meta-learned task encoder for CL method prediction

**M2. Adaptive Method Orchestration Algorithm**
- MRAC-inspired online adaptation based on forgetting signals
- Cold-start fallback for out-of-distribution tasks
- Resource-aware configuration selection respecting memory/compute budgets
- *Novelty:* First online-adaptive CL method orchestrator

**M3. Unified PEFT+Regularization+Replay Training Framework**
- Integration of HuggingFace PEFT + Avalanche strategies + custom replay
- Efficient batched training with method-specific procedures (Fisher computation, replay buffer management)
- Modular plugin architecture for extending to new PEFT/regularization methods
- *Novelty:* First unified implementation framework for all three CL method families

### Practical Contributions

**P1. Open-Source Orchestrator**
- Production-ready implementation compatible with HuggingFace ecosystem
- Pre-trained orchestrator meta-trained on CLDatasets, ready for deployment
- Extensive documentation and tutorials
- *Impact:* Enables practitioners to apply adaptive CL without expertise in method selection

**P2. Computational Cost Reduction**
- 40-60% reduction in total training cost by avoiding expensive methods when unnecessary
- Enables foundation model continual learning on consumer hardware (single A100, RTX 4090)
- *Impact:* Democratizes continual learning for resource-constrained researchers

**P3. Performance Improvement**
- 10-20% higher average accuracy, 15-25% better backward transfer vs fixed baselines
- Robust across diverse task sequences (NLP, vision, multi-modal)
- *Impact:* Advances state-of-the-art in foundation model continual learning

**P4. Benchmark Evaluation Protocol**
- Standardized evaluation on CLDatasets holdout set (10+ sequences, 50+ tasks)
- Comprehensive ablation studies (meta-learning, online adaptation, hierarchical prediction)
- Open-source evaluation scripts for reproducibility
- *Impact:* Establishes evaluation standard for future adaptive CL research

---

## Phase 2B Decomposition Preview

### SH1 (Existence): Task Characteristic → Forgetting Prediction

**Sub-Hypothesis:**
A BERT-based task encoder can predict catastrophic forgetting severity (0-1 scale) from automatically extracted task features (embedding distance, data size, vocabulary overlap, KL divergence) with mean absolute error (MAE) < 0.15 when meta-trained on 100+ task sequences.

**Verification:**
- Train task encoder on CLDatasets (80% train, 20% val)
- Evaluate MAE on Avalanche holdout tasks (not seen during meta-training)
- Ablation: Compare automatic features vs hand-crafted features vs end-to-end learning

**Success Criteria:**
- MAE < 0.15 on holdout tasks
- Correlation (predicted vs actual forgetting) > 0.7

### SH2 (Mechanism): Configuration Selection → Performance

**Sub-Hypothesis:**
Given accurate forgetting prediction, selecting PEFT+regularization configuration based on predicted forgetting severity (via hierarchical predictor) achieves within 95% of oracle performance (perfect method selection with ground-truth forgetting).

**Verification:**
- Assume oracle has ground-truth forgetting severity for all tasks
- Oracle selects optimal configuration by exhaustive search
- Measure: Performance gap between hierarchical predictor and oracle

**Success Criteria:**
- ADORE performance ≥ 95% of oracle performance
- Oracle = upper bound (best possible with perfect prediction)

### SH3 (Comparison): ADORE vs Fixed Baselines

**Sub-Hypothesis:**
ADORE (offline prediction + online adaptation) achieves 10-20% higher average accuracy and 15-25% better backward transfer compared to fixed-strategy baselines (Fixed LoRA+EWC, Fixed Adapter+Replay, Fixed MoE) on CLDatasets holdout set (10+ sequences, 7B foundation model).

**Verification:**
- Run ADORE and 3 fixed baselines on same task sequences
- Measure average accuracy, BWT, total training cost
- Statistical test: Paired t-test with Bonferroni correction (α=0.05/3)

**Success Criteria:**
- Avg accuracy improvement ≥ 10% over best fixed baseline (p < 0.017)
- BWT improvement ≥ 15% (p < 0.017)
- Consistent across ≥8/10 sequences

---

## Readiness Checklist

- ✅ **Hypothesis Statement:** Clear main hypothesis with measurable outcomes
- ✅ **Variables Defined:** Independent, dependent, mediating, control variables specified
- ✅ **Causal Mechanism:** 4-link chain from task characteristics to performance with evidence
- ✅ **Assumptions Identified:** 6 key assumptions (2 critical, 2 moderate, 2 low risk) with mitigations
- ✅ **Scope Defined:** In-scope (LLMs, ViTs, multi-modal 1B-70B params) vs out-of-scope (RL, federated, online CL)
- ✅ **Testable Predictions:** 4 predictions (1 primary, 3 secondary) with operational definitions and falsification criteria
- ✅ **Related Work:** 8 key methods positioned (PIECE, SSR, MoE-CT, EWC, LoRA, Avalanche, MRAC, MAML)
- ✅ **Contributions:** 3 theoretical, 3 methodological, 4 practical contributions
- ✅ **Sub-Hypotheses:** 3 sub-hypotheses (existence, mechanism, comparison) for Phase 2B decomposition
- ✅ **Statistical Design:** Paired t-test with Bonferroni correction, α=0.05, 3 random seeds
- ✅ **Evaluation Protocol:** CLDatasets holdout (10 sequences), Avalanche benchmarks, 7B foundation model

**Completeness Score:** 11/11 (100%)

---

## Open Questions for Phase 2B Planning

### High-Priority Questions

1. **Meta-Training Dataset Specification:**
   - Q: Which specific CLDatasets task sequences to use for meta-training vs validation vs test split?
   - Q: How to ensure meta-training distribution covers target deployment scenarios (NLP, vision, multi-modal)?
   - Needed for: SH1 (task encoder training)

2. **Task Encoding Sample Size:**
   - Q: How many task samples required for reliable task encoding (10, 100, 1000)?
   - Q: Trade-off between encoding accuracy and sample efficiency?
   - Needed for: SH1 (task encoder evaluation)

3. **Hierarchical Prediction Training:**
   - Q: Joint training of Stage 1 (method family) + Stage 2 (hyperparameters) or sequential?
   - Q: Loss function weighting between classification accuracy and downstream performance?
   - Needed for: SH2 (configuration predictor)

4. **Online Adaptation Rules:**
   - Q: Precise forgetting signal thresholds (validation loss increase >5%, >10%)?
   - Q: Adaptation step size (increase EWC λ by 10%, 50%, 100%)?
   - Q: Stopping criteria (max 3 adaptations per task? Early stopping when signal stabilizes)?
   - Needed for: H1-P4 (online adaptation value)

5. **Baseline Hyperparameter Tuning:**
   - Q: Should fixed baselines use best hyperparameters from validation set (oracle baseline) or typical defaults?
   - Q: Risk: Oracle baseline may overfit to validation set, but typical defaults may be unfair comparison
   - Needed for: SH3 (baseline comparison)

### Medium-Priority Questions

6. **Resource Budget Specification:**
   - Q: How to specify memory budget (GB GPU memory) and translate to configuration constraints?
   - Q: How to handle memory overflow (reduce batch size, use gradient checkpointing, switch to smaller PEFT method)?
   - Needed for: Practical deployment

7. **Scalability Testing:**
   - Q: Evaluate on 1B, 7B, 13B, 70B parameter models or focus on 7B?
   - Q: Meta-training on smaller scale (1B), test generalization to larger scale (13B)?
   - Needed for: Scalability claims

8. **Failure Mode Analysis:**
   - Q: Characterize when ADORE fails (e.g., extremely OOD tasks, ultra-low-resource scenarios)
   - Q: Design diagnostic metrics (task encoding confidence, prediction uncertainty)
   - Needed for: Robustness analysis

### Low-Priority Questions (Defer to Phase 3-4)

9. **Multi-Modal Task Encoding:**
   - Q: Use separate encoders for vision vs text vs multi-modal tasks, or unified encoder?
   - Can defer: Focus Phase 2B-2C on LLM tasks first, extend to multi-modal in Phase 3

10. **Open-Source Release Plan:**
   - Q: Repository structure, API design, documentation strategy
   - Can defer: Address in Phase 4 (implementation)

---

**Status:** ✅ Ready for Phase 2B Verification Planning

**Next Steps:**
1. Phase 2B: Decompose into detailed sub-hypotheses (SH1-SH5) with verification plans
2. Phase 2C: Design experiments for each sub-hypothesis with specific benchmarks, metrics, ablations
3. Phase 3: Create implementation plan (PRD, Architecture, Tasks) for Archon project
4. Phase 4: Execute implementation with Coder-Validator loop

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
