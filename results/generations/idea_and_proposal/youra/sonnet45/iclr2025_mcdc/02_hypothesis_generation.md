# Phase 2A Extended: Hypothesis Clarification - LoRA-MoE

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis ID:** H1-LoRA-MoE-2025
**Confidence Level:** 0.85 (High)

**Main Innovation:** First framework treating Parameter-Efficient Fine-Tuning (PEFT) modules as lightweight Mixture-of-Experts (MoE) specialists, enabling 100-1000 expert scaling (vs typical 8-64 FFN experts) through hierarchical routing optimized for LoRA's low-rank structure.

**Key Contribution:** Unifies PEFT and MoE paradigms to enable collaborative model development where independent teams train domain-specific LoRA experts that compose via learned routing—addressing ICLR 2025 MCDC Workshop's core challenge of modular collaborative deep learning.

**Phase 2B Readiness:** ✅ Variables operationalized, predictions testable, statistical design specified, contributions clarified.

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Main Hypothesis:**
Treating independently-trained LoRA (Low-Rank Adaptation) adapters as lightweight expert specialists in a hierarchical Mixture-of-Experts architecture enables scaling to 100+ experts with comparable task performance to standard FFN-based MoE while significantly reducing active parameter count (by 10-100×) and computational cost.

**Alternative Hypothesis (H0):**
LoRA-based experts cannot match the performance of standard FFN experts in MoE architectures because: (1) LoRA's low-rank constraint limits expert capacity, (2) independent training produces incompatible expert representations, or (3) routing overhead negates parameter efficiency gains.

### 1.2 Variables

| Variable | Type | Operationalization | Range/Values |
|----------|------|-------------------|--------------|
| **Number of LoRA experts (N)** | Independent | Count of LoRA modules in MoE layer | N ∈ {50, 100, 200, 500} |
| **Hierarchical routing levels** | Independent | Flat (1-level) vs Hierarchical (2-level: coarse group + fine expert) | Binary: {flat, hierarchical} |
| **LoRA rank (r)** | Controlled | Rank of low-rank decomposition matrices (A, B) | r ∈ {8, 16, 32} |
| **Top-K selection parameter** | Controlled | Number of experts activated per token | K ∈ {2, 4, 8} |
| **Task performance** | Dependent | Accuracy on MMLU (57 tasks), BigBench-Hard (23 tasks) | [0, 100]% |
| **Active parameter count** | Dependent | Parameters used per forward pass: base + K×LoRA experts | Measured in millions (M) |
| **Inference latency** | Dependent | Throughput in tokens/second on A100 GPU | Measured: tokens/sec |
| **Expert utilization rate** | Dependent | % of experts activated >1% across validation set | [0, 100]% |

### 1.3 Causal Mechanism

**Causal Chain:**

```
Independent LoRA Training on Diverse Tasks
    ↓ (produces)
Specialized Low-Rank Expert Representations in Task-Specific Subspaces
    ↓ (enables)
Hierarchical Router Learning Task-Family Groupings + Fine-Grained Selection
    ↓ (via rank-space projection features)
Dynamic Top-K Expert Activation Based on Input Tokens
    ↓ (results in)
Sparse Expert Utilization with Preserved Task Performance
    ↓ (achieves)
100+ Expert Scaling with 10-100× Parameter Efficiency vs FFN-MoE
```

**Evidence for Causal Links:**

1. **LoRA Training → Specialized Representations**
   - **Evidence:** SplitLoRA (Lin et al., 2024, 70 citations) demonstrates independent LoRA training produces effective task-specific adapters
   - **Mechanism:** LoRA's low-rank constraint forces learning in intrinsic task-relevant subspaces (Aghajanyan et al., 2020)

2. **Specialized Reps → Hierarchical Routing**
   - **Evidence:** LoraHub (2023) shows gradient-free LoRA composition works; we extend to learned routing
   - **Mechanism:** Task-family clustering in embedding space (Level 1) → fine expert selection (Level 2)

3. **Routing → Sparse Activation**
   - **Evidence:** Switch Transformer (Fedus et al., 2021) validates top-K expert selection effectiveness
   - **Mechanism:** Gating network outputs expert scores → softmax + top-K → weighted combination

4. **Sparse Activation → Parameter Efficiency**
   - **Mathematical:** 100 LoRA experts (rank 16) = 100 × 2 × d × 16 parameters vs 8 FFN experts = 8 × 4 × d² parameters. For d=4096: LoRA-MoE ≈ 13M active (K=4) vs FFN-MoE ≈ 537M active
   - **Efficiency gain:** ~40× fewer active parameters

**Key Tension:**

While LoRA's low-rank structure constrains individual expert capacity (potential weakness), it simultaneously enables:
- **Extreme scaling:** Parameter efficiency allows 100-1000 experts (vs 8-64 FFN experts)
- **Diverse specialization:** More experts = finer-grained task coverage
- **Capacity recovery:** Ensemble of 100 low-rank experts may exceed capacity of 8 full-rank experts through specialization diversity

**Resolution:** Hypothesis predicts diversity-via-quantity compensates for individual expert capacity constraints.

### 1.4 Key Assumptions

1. **Assumption:** Independently-trained LoRA modules on diverse tasks produce sufficiently diverse expert representations
   **Testability:** Measure inter-expert similarity via rank-space distance metrics; validate >70% expert pairs have cosine similarity <0.3
   **Risk if violated:** Expert collapse (all experts converge to similar representations)

2. **Assumption:** LoRA rank-space structure contains task-relevant features for routing decisions
   **Testability:** Ablation study comparing rank-space projection features vs standard hidden state features for routing
   **Risk if violated:** Router cannot effectively distinguish expert specializations

3. **Assumption:** Hierarchical grouping (2-level) preserves fine-grained specialization while reducing router complexity
   **Testability:** Compare task performance + router overhead between hierarchical vs flat routing
   **Risk if violated:** Either performance degradation (poor grouping) or no efficiency gain (grouping overhead too high)

4. **Assumption:** Load balancing auxiliary loss (λ=0.01) prevents expert collapse without performance degradation
   **Testability:** Measure expert utilization rate with/without load balancing; validate performance difference <1%
   **Risk if violated:** Unutilized experts waste capacity OR load balancing harms accuracy

### 1.5 Scope & Boundaries

**Applies To:**
- Large language models (7B-70B parameters, transformer architectures)
- Multi-task learning scenarios with 50+ diverse tasks
- Settings where independent task-specific training is feasible
- Collaborative development contexts (multiple teams, distributed training)

**Does NOT Apply To:**
- Single-task fine-tuning (no multi-task routing needed)
- Models without pre-training (LoRA requires base model)
- Non-transformer architectures initially (extension possible but not validated)
- Real-time systems with <10ms latency constraints (routing overhead may violate)

**Known Limitations:**
1. **Training Data Requirement:** Needs diverse task distribution for independent LoRA training (100 tasks minimum)
2. **Router Training Overhead:** Phase 2 router training requires mixed-task dataset (~10M tokens)
3. **Initial Validation Scale:** Experiments target 100-expert scale; 1000-expert scaling claimed but not yet validated
4. **Base Model Dependency:** Effectiveness may vary with base model architecture (validated on LLaMA-family only)

### 1.6 Testable Predictions

**Primary Prediction (P1):**
**IF** LoRA-MoE with N=100 experts (rank r=16, top-K=4) trained on diverse FLAN tasks,
**THEN** active parameter count <10% of 8-expert FFN-MoE baseline AND MMLU accuracy within ±2% of FFN-MoE baseline.
**Measurement:** Active params = base + 4×(2×4096×16) ≈ 7B + 0.5M vs FFN baseline ≈ 7B + 537M. Accuracy: MMLU 5-shot.

**Secondary Prediction (P2):**
**IF** hierarchical routing (2-level: 10 task-family groups → top-4 experts) vs flat routing (top-4 from all 100),
**THEN** hierarchical routing reduces router FLOPs by ≥60% AND maintains expert diversity (utilization >80%).
**Measurement:** Router FLOPs = (input_dim × num_experts) for flat vs (input_dim × num_groups + input_dim × K × group_size) for hierarchical.

**Secondary Prediction (P3):**
**IF** load balancing auxiliary loss with λ=0.01 applied during router training,
**THEN** expert utilization rate >80% (≥80/100 experts activated >1% of validation samples) AND task performance degradation <1% vs no load balancing.
**Measurement:** Count per-expert activation frequency across MMLU validation set; compare accuracy with/without λ term.

**Falsification Criteria:**
- **Efficiency claim falsified IF:** Active parameters ≥50% of FFN-MoE baseline
- **Performance claim falsified IF:** MMLU accuracy >5% below FFN-MoE baseline
- **Scalability claim falsified IF:** Expert utilization <60% (indicates expert collapse)

### 1.7 SOTA Baseline

**Primary Baseline:** Standard FFN-based MoE (Switch Transformer architecture)
- **Configuration:** 8 experts, 4096-dimensional FFN, top-2 routing, load balancing
- **Active Parameters:** Base (7B) + 2×FFN experts (2×4×4096²) ≈ 7.537B per forward pass
- **Performance:** MMLU ~65% (LLaMA-2 7B + MoE fine-tuning, estimated from LLaMA-MoE paper)

**Secondary Baseline:** Dense fine-tuned model
- **Configuration:** Single LLaMA-2 7B with full fine-tuning on mixed tasks
- **Active Parameters:** 7B (all parameters active)
- **Performance:** MMLU ~60% (zero-shot, from LLaMA-2 paper)

**Comparison Table:**

| Model | Total Params | Active Params | MMLU (Target) | Training Cost |
|-------|--------------|---------------|---------------|---------------|
| Dense Baseline | 7B | 7B | ~60% | 1× (reference) |
| FFN-MoE (8 experts) | ~11B | ~7.5B | ~65% | ~1.2× |
| **LoRA-MoE (100 experts)** | **~7.05B** | **~7.005B** | **~64%** | **~0.3×** |

**Target Performance:** Match FFN-MoE (65% MMLU) while using <10% active parameters of FFN-MoE and <30% training cost.

### 1.8 Statistical Verification Design

**Experimental Design:** 3×2 factorial with repeated measures
- **Factor 1 (Architecture):** LoRA-MoE, FFN-MoE, Dense (3 levels)
- **Factor 2 (Routing):** Hierarchical, Flat (2 levels, applies only to MoE conditions)
- **Replication:** 3 independent training runs per condition (different random seeds)

**Sample Size:**
- **Evaluation:** MMLU (57 tasks × 5-shot = 285 datapoints per run), BigBench-Hard (23 tasks)
- **Power Analysis:** N=3 runs sufficient to detect ≥3% accuracy difference with power=0.8, α=0.05 (based on typical LLM evaluation variance)

**Statistical Tests:**
1. **Performance Comparison:** Paired t-test comparing LoRA-MoE vs FFN-MoE accuracy across tasks (null: μ_diff = 0, alternative: |μ_diff| < 2%)
2. **Efficiency Validation:** One-sample t-test for active parameter ratio (null: ratio ≥ 0.5, alternative: ratio < 0.1)
3. **Expert Utilization:** One-sample proportion test (null: utilization ≤ 0.6, alternative: utilization > 0.8)

**Significance Threshold:** α = 0.05 with Bonferroni correction for multiple comparisons (3 tests → α_corrected = 0.0167)

**Confound Controls:**
- Same base model across conditions (LLaMA-2 7B)
- Same training data distribution (FLAN task mixture)
- Same evaluation protocol (5-shot MMLU, zero-shot BigBench)
- Same hardware (8×A100 80GB)

---

## 2. Contribution Summary

### Theoretical Contributions

**T1. Unified PEFT-MoE Framework**
First theoretical framework unifying Parameter-Efficient Fine-Tuning (PEFT) and Mixture-of-Experts (MoE) paradigms by treating low-rank adapters as expert specialists rather than full fine-tuning or standard FFN experts.

**Significance:** Bridges two previously separate efficiency paradigms—PEFT (parameter efficiency via low-rank) and MoE (computational efficiency via sparse activation)—into cohesive architecture enabling both simultaneously.

**T2. Capacity Scaling Laws for Lightweight Experts**
Derive theoretical relationship between expert count (N), rank (r), and model capacity:
```
Capacity(LoRA-MoE) ≈ N × r × expressivity_factor
vs
Capacity(FFN-MoE) ≈ M × d² × expressivity_factor
```
Where N >> M (100 vs 8) but r << d (16 vs 4096), predicting crossover point where quantity compensates for individual expert capacity.

**Significance:** Provides theoretical justification for extreme expert scaling (100-1000) despite low-rank constraints.

**T3. Rank-Space Routing Theory**
Formalize routing in low-rank parameter subspaces: router learns task-to-subspace mappings where LoRA matrices (A, B) span task-specific subspaces. Hierarchical decomposition groups related subspaces.

**Significance:** Novel routing mechanism exploiting LoRA's mathematical structure (not just treating experts as black boxes like standard MoE).

### Methodological Contributions

**M1. Hierarchical LoRA-Aware Routing Algorithm**
Two-level routing mechanism:
- **Level 1 (Coarse):** Task-family classifier selects top-M expert groups (M=4-8) from G groups (G=10)
- **Level 2 (Fine):** Expert selector chooses top-K LoRA experts (K=2-4) within selected groups
- **Feature Engineering:** Uses LoRA rank-space projections (U^T h, V^T h from SVD decomposition) as router features

**Novelty:** First routing mechanism leveraging LoRA's rank-space structure; reduces router complexity from O(d×N) to O(d×G + d×K×N/G).

**M2. Independent Expert Training Protocol**
Training pipeline enabling collaborative development:
1. **Phase 1 (Parallelizable):** Teams train domain-specific LoRA experts independently on diverse tasks (no coordination required)
2. **Phase 2 (Centralized):** Freeze all LoRA experts, train hierarchical router on mixed-task dataset with load balancing
3. **Phase 3 (Optional):** Fine-tune router + experts end-to-end (low compute, only adjusts routing)

**Novelty:** Decouples expert specialization (parallel) from routing optimization (sequential), enabling distributed collaborative training.

**M3. Load-Balanced Hierarchical Training**
Auxiliary loss combining standard MoE load balancing with hierarchical constraints:
```
L_total = L_task + λ₁ × L_group_balance + λ₂ × L_expert_balance
```
Ensures both group-level and expert-level utilization, preventing collapse at multiple hierarchy levels.

**Novelty:** Extends load balancing to hierarchical MoE with PEFT experts (standard load balancing designed for flat FFN-MoE).

### Practical Contributions

**P1. Extreme Expert Scaling (100-1000 experts)**
Enables 10-100× more experts than standard MoE (typical: 8-64 FFN experts) through LoRA's parameter efficiency:
- **100 LoRA experts (rank 16):** ~13M expert parameters vs ~537M for 8 FFN experts
- **Inference cost:** Comparable to 8-expert MoE despite 100 experts available

**Impact:** Supports finer-grained task specialization, collaborative development at scale, continual expert addition.

**P2. Collaborative Model Development Paradigm**
Architectural support for multi-team LLM development:
- **Independent Training:** Teams train LoRA experts on proprietary/specialized data without sharing
- **Decentralized Contribution:** Add new experts without retraining existing ones (continual learning)
- **Modular Composition:** Router learns to compose heterogeneous expert pool

**Impact:** Addresses ICLR MCDC Workshop's core challenge—enabling collaborative development without centralized training or data sharing.

**P3. Efficient Continual Learning via Expert Addition**
Continual learning protocol:
1. Train new LoRA expert on new task (no forgetting risk—existing experts frozen)
2. Add expert to pool, retrain router only (minimal compute)
3. Old task performance preserved (router learns when to activate new vs old experts)

**Impact:** Mitigates catastrophic forgetting through architectural modularity rather than regularization.

---

## 3. Key Related Work

### Foundational MoE Architectures

**[1] Sparse Expert Models Review (Fedus, Dean, Zoph, 2022)**
- **SS ID:** ca086f4c09cf8de705830ac2b70951737fab93ca | **Citations:** 196
- **Relation:** Foundation - Establishes sparse MoE theoretical framework; we extend to PEFT experts
- **Gap:** Uses FFN experts exclusively; no mention of PEFT modules as experts

**[2] Switch Transformer (Fedus et al., 2021)**
- **Relation:** Methodology - We adapt switch routing and load balancing for LoRA experts
- **Differentiation:** Switch uses single FFN expert per token (top-1); we use top-K LoRA experts with hierarchical selection

**[3] MoE Survey (Cai et al., 2024)**
- **SS ID:** b778fd5f23b91499e4186539e66596a0ac67a13b | **Citations:** 205
- **Relation:** Foundation - Comprehensive MoE taxonomy for LLMs
- **Gap:** PEFT-based experts not covered in taxonomy

### PEFT and Collaborative Training

**[4] SplitLoRA (Lin et al., 2024)**
- **SS ID:** 36f708fa17b9a096223d234565be16ad8ee83a35 | **Citations:** 70
- **Relation:** Inspiration - Demonstrates independent LoRA training for collaborative LLM fine-tuning
- **Differentiation:** SplitLoRA uses split learning (privacy focus); we use LoRA as MoE experts (capacity focus)

**[5] CoLLiE (Lv et al., 2023)**
- **SS ID:** 836b9658eb81f321de90423b6259b07a398ca79b | **Citations:** 7
- **Relation:** Methodology - Efficient collaborative LLM training library with PEFT support
- **Differentiation:** CoLLiE focuses on parallelism optimization; we introduce expert routing

**[6] LoraHub (2023)**
- **Relation:** Methodology - Demonstrates gradient-free LoRA composition via weighted selection
- **Differentiation:** LoraHub uses optimization-based selection; we use learned neural routing

### Model Upcycling and Expert Construction

**[7] LLaMA-MoE (Zhu et al., 2024)**
- **SS ID:** 05830547cfd19b734777b8546f4d606fd79ebd2b | **Citations:** 127
- **Relation:** Methodology - Dense-to-MoE conversion via FFN expert partitioning
- **Differentiation:** LLaMA-MoE partitions existing FFN into experts; we treat independent LoRA modules as experts

**[8] Drop-Upcycling (Nakamura et al., 2025)**
- **SS ID:** 8d64e47f23d383c4492f93fc17213cdc7ef3ec2a | **Citations:** 8
- **Relation:** Methodology - Addresses upcycling training slowdown via partial re-initialization
- **Differentiation:** Drop-Upcycling optimizes FFN expert initialization; our experts are pre-trained LoRA modules

**[9] Upcycling Instruction Tuning (Hui et al., 2024)**
- **SS ID:** a221623c866c89cb1ca1368e324e13069c8bddcd | **Citations:** 3
- **Relation:** Inspiration - Uses intermediate checkpoints as experts (closest to our approach)
- **Differentiation:** Hui uses full model checkpoints; we use lightweight LoRA modules (100× parameter reduction)

### Model Merging and Composition

**[10] Model Merging Survey (Yang et al., 2024)**
- **SS ID:** 1a638e5752e386612406d0479b7bad94877be8cb | **Citations:** 178
- **Relation:** Foundation - Comprehensive taxonomy of model merging methods
- **Positioning:** Our work extends merging to learned routing (vs fixed weight interpolation)

**[11] Sequential Model Merging (Tang et al., 2025)**
- **SS ID:** 111d019bc2559f43c6ca627704d59673adea7efb | **Citations:** 20
- **Relation:** Comparison - Training-free continual merging via projections
- **Differentiation:** Tang uses orthogonal projections (fixed); we use learned routing (adaptive)

### Decentralized and Communication-Efficient Training

**[12] DisPFL (Dai et al., 2022)**
- **SS ID:** 88c2326aaacffccfd9ffc78b8b87cab90b7a6110 | **Citations:** 153
- **Relation:** Extension - Decentralized sparse training with communication efficiency
- **Synergy:** DisPFL's sparse masks + our LoRA experts could enable fully decentralized LoRA-MoE training

**[13] Protocol Models (Ramasinghe et al., 2025)**
- **SS ID:** 9eb37366baaae813890b50c7976fec6396b2e678 | **Citations:** 0
- **Relation:** Extension - 99% compression for decentralized model parallelism
- **Synergy:** Extreme compression techniques applicable to our router training phase

### Adaptive Computation and Continual Learning

**[14] Adaptive Computation Modules (Wójcik et al., 2023)**
- **SS ID:** 19fdbff53a9f1ee654a9bdb605b4b62d22588d13 | **Citations:** 7
- **Relation:** Comparison - Conditional computation for efficiency
- **Differentiation:** ACM uses progressive refinement; we use expert selection

**[15] Modular Dynamic Neural Network (Turner et al., 2021)**
- **SS ID:** 3314717102f1f89c6509d500c830b4fe1c3c6fd1 | **Citations:** 9
- **Relation:** Inspiration - Modular architecture for continual learning
- **Differentiation:** MDNN grows tree structure; we use fixed expert pool with routing

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): LoRA experts exhibit task-specific specialization**
- **Claim:** Independently-trained LoRA modules develop distinguishable task-specific representations in rank-space
- **Verification:** Measure inter-expert similarity, cluster experts by task family, validate diversity metrics
- **Experiment:** Train 100 LoRA experts on FLAN tasks → compute pairwise cosine similarity in rank-space → expect <0.3 for >70% pairs

**SH2 (Mechanism): Hierarchical routing effectively selects relevant experts**
- **Claim:** Two-level routing (task-family → expert) outperforms flat routing in efficiency while maintaining accuracy
- **Verification:** Compare hierarchical vs flat routing on FLOPs, latency, accuracy, expert utilization
- **Experiment:** Ablation study with same expert pool, different routing architectures

**SH3 (Comparison): LoRA-MoE matches FFN-MoE performance with fewer active parameters**
- **Claim:** 100 LoRA experts (rank 16, K=4) achieve ≥98% of 8-expert FFN-MoE accuracy with <10% active parameters
- **Verification:** Head-to-head comparison on MMLU, BigBench, measure active params, latency
- **Experiment:** Train both architectures, evaluate on same benchmarks, controlled comparison

### Readiness Checklist

- [x] **Variables Operationalized:** All 8 variables (4 independent/controlled, 4 dependent) have clear measurement protocols
- [x] **Predictions Testable:** 3 falsifiable predictions (P1-P3) with specific thresholds and measurement methods
- [x] **Statistical Design:** Experimental design specified (3×2 factorial, N=3 runs, power analysis complete)
- [x] **Assumptions Explicit:** 4 key assumptions listed with testability criteria and risk assessment
- [x] **Scope Defined:** Applicability conditions and limitations clearly bounded
- [x] **Baselines Identified:** SOTA comparison (FFN-MoE, Dense) with performance targets
- [x] **Contributions Clarified:** 3 theoretical + 3 methodological + 3 practical contributions articulated
- [x] **Related Work Mapped:** 15 key papers positioned with relation type and differentiation
- [x] **Sub-Hypotheses Outlined:** 3 decomposition targets (SH1-SH3) for Phase 2B
- [x] **Causal Mechanism:** Full causal chain specified with evidence links

### Open Questions

1. **Optimal Expert Grouping Strategy:** How to determine task-family groups for Level 1 routing?
   - **Options:** Manual domain clustering, K-means on task embeddings, learned clustering
   - **Resolution:** Phase 2B will include ablation study comparing strategies

2. **LoRA Rank Selection:** Trade-off between rank (capacity) and parameter efficiency
   - **Options:** r ∈ {8, 16, 32} tested in ablation
   - **Resolution:** Phase 2B will determine optimal rank via validation performance

3. **Load Balancing Weight:** Optimal λ for balancing task performance vs expert utilization
   - **Options:** λ ∈ {0.001, 0.01, 0.1} sweep
   - **Resolution:** Phase 2B hyperparameter tuning

4. **Scaling Beyond 100 Experts:** Will 500-1000 expert scaling maintain benefits?
   - **Risk:** Router complexity may grow prohibitively
   - **Resolution:** Phase 2C will design scaling experiments if 100-expert validation succeeds

5. **Cross-Domain Transfer:** Does approach generalize beyond language to vision, multimodal?
   - **Scope:** Initially out-of-scope (LLM-only validation)
   - **Resolution:** Phase 5 future work discussion

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-08*
