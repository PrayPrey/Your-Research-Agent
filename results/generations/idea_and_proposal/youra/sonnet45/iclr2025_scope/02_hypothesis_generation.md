# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** C:\Users\OWNER\Desktop\ResearchAgents_Integrated_0\ResearchAgents_5_4_0_YouRA_new_Yoon_experiment_sonnet45\tasks_youra_result_sh\iclr2025_scope\02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ECAR-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under test-time multi-task serving conditions, if temperature-scaled calibration is applied to MoE routing logits with ensemble-based self-supervised updates, then routing accuracy and compute efficiency improve because calibrated confidence distributions enable adaptive expert activation based on routing certainty, reducing over-activation while maintaining performance on uncertain cases.

**Alternative Hypothesis (H0):**
There is no relationship between calibrated routing confidence and expert activation efficiency; routing accuracy and compute consumption remain unchanged regardless of temperature scaling or ensemble-based calibration updates.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| τ (temperature parameter) | Independent | Per-task-category scalar applied to routing logits via softmax(logits/τ); manipulated through calibration updates | τ ∈ [0.5, 2.0]; higher τ = more uncertainty |
| P_max (routing confidence) | Dependent | Maximum probability in calibrated routing distribution; measured as max(softmax(logits/τ)) | P_max ∈ [0.0, 1.0]; threshold at 0.8, 0.5 |
| K (ensemble size) | Controlled | Number of experts activated based on confidence tier | K ∈ {1, 3, 5}; fixed per confidence tier |
| H (expert output entropy) | Dependent | Shannon entropy H = -Σ p_i log p_i of expert output distributions; measures agreement | H ∈ [0, log(K)]; low = agreement |
| α (EMA smoothing) | Controlled | Exponential moving average parameter for online calibration updates | α = 0.9 (fixed); balances stability vs adaptation |

### 1.3 Causal Mechanism

**Step 1: Task Embeddings → Routing Logits**
Contrastive learning (MoELoRA-style) creates task-discriminative representations that map inputs to routing logits. When a new input arrives at test-time, the meta-router computes task embeddings and generates raw routing scores for each expert.

**Step 2: Routing Logits + Temperature → Calibrated Confidence**
Temperature scaling transforms raw routing logits into calibrated confidence distributions via softmax(logits/τ). Higher τ flattens the distribution (expressing uncertainty), while lower τ sharpens it (expressing confidence). This calibration step converts expert scores into probability distributions that accurately reflect routing certainty.

**Step 3: Calibrated Confidence + Ensemble Agreement → Online Updates**
When routing confidence is low (P_max < threshold), multiple experts (ensemble) are activated. The agreement among experts (measured by output entropy H) provides a self-supervised signal: low confidence + low entropy (experts agree) indicates miscalibration, triggering τ adjustment via EMA-smoothed updates. This online adaptation continuously improves calibration quality without requiring ground truth labels.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | MoELoRA (2024, 44 cites) | Contrastive learning for expert routing achieves 4.2% improvement over vanilla LoRA | Strong |
| Step2 → Step3 | Calibration Theory (Standard ML) | Temperature scaling via softmax(logits/τ) is proven technique for probability calibration | Strong |
| Step3 → Outcome | Ensemble Methods Literature | Ensemble agreement correlates with prediction confidence in uncertainty quantification | Medium |

**Key Tension:**
MoELoRA demonstrates that contrastive learning improves routing specialization during training, but there is no direct evidence that ensemble agreement (output entropy) reliably correlates with routing quality at test-time. Resolution: Phase 2B will include sub-hypothesis SH2 to empirically validate that low confidence + low entropy indicates miscalibration, establishing the core self-supervision mechanism.

### 1.4 Key Assumptions

1. **Ensemble Agreement Correlation**: Ensemble agreement (measured by output entropy H) correlates with routing calibration quality - when routing confidence is low but experts agree (low H), this indicates the routing was actually confident but miscalibrated.
   - *Evidence*: Ensemble uncertainty quantification literature
   - *Consequence if violated*: Self-supervision signal becomes noise, online calibration degrades routing quality instead of improving it

2. **Task Embedding Generalization**: Task embeddings generated via contrastive learning (MoELoRA-style) generalize across diverse task distributions without requiring task labels at test-time.
   - *Evidence*: MoELoRA (2024) achieves 4.2% improvement across 11 tasks
   - *Consequence if violated*: Task detection fails, routing defaults to uniform expert selection, losing specialization benefits

3. **EMA Stability**: EMA-smoothed online updates (α=0.9) provide sufficient stability to prevent divergence during test-time calibration adaptation.
   - *Evidence*: Standard online learning practice
   - *Consequence if violated*: Calibration oscillates or diverges, routing confidence becomes unreliable

4. **Pre-training Transfer**: Initial temperature parameters can be pre-trained on multi-task datasets and transfer to new tasks at deployment.
   - *Evidence*: Transfer learning assumptions from domain adaptation literature
   - *Consequence if violated*: Cold-start problem requires many samples before calibration converges, reducing practical utility

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Pre-trained sparse MoE models with frozen expert parameters (e.g., OLMoE, Mixtral)
- Multi-task serving scenarios where diverse downstream tasks share the same model
- Test-time inference without access to task labels or fine-tuning data
- Lightweight meta-router constraint (< 1% additional parameters)
- Tasks that exhibit distinguishable patterns in embedding space

**Where Hypothesis Does NOT Apply:**
- Dense (non-MoE) models: Mechanism requires expert specialization
- Single-task deployment: Adaptive routing provides no benefit over static optimal routing
- Tasks with full fine-tuning budget: Direct fine-tuning likely more effective than adaptive routing
- Extremely low-resource constraints: Meta-router (even <1%) may be prohibitive
- Tasks indistinguishable in embedding space: Contrastive learning cannot separate them

**Known Limitations:**
- Cold-start performance: Initial calibration may require warm-up samples
- Ensemble overhead: Low-confidence cases incur 3-5x compute cost
- Task distribution shift: Severe drift may break task embedding generalization
- Expert capacity: Assumes experts have sufficient capacity for task specialization

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Routing Accuracy Improvement)**:
ECAR will achieve task-expert matching accuracy > 75% on multi-task benchmarks, measured by alignment between predicted expert activations and expert specialization (determined by task-conditional performance analysis).

*Measurement*:
- Task-expert matching accuracy > 75% with p < 0.05
- Metric: Proportion of inputs routed to expert that performs best on that task type
- Statistical test: Paired t-test comparing ECAR vs static routing baseline, n ≥ 25 runs

*Basis*:
Standard for adaptive routing systems in multi-task learning (domain standard: meaningful improvement is 5-10% over static baselines). Target represents ability to correctly identify task type and route to specialized expert in 3 out of 4 cases.

**Secondary Predictions:**
**P2 (Compute Efficiency via Confidence-Based Activation)**:
ECAR will reduce average expert activations per input by 30-40% compared to fixed top-K routing, while maintaining task performance within 2% of full ensemble baseline.

*Measurement*:
- Average experts activated per input: ECAR vs baseline
- Task performance degradation: ≤ 2% vs full ensemble
- Compute savings: 30-40% reduction in FLOPs

*Basis*:
Confidence-based gating allows single-expert routing on high-confidence cases (expected 60-70% of inputs), reducing compute while ensemble handles hard cases.

**P3 (Online Calibration Convergence)**:
Calibration error (Expected Calibration Error - ECE) will decrease by ≥ 50% within 500 samples under online updates, demonstrating self-supervised calibration effectiveness.

*Measurement*:
- ECE reduction: (ECE_initial - ECE_final) / ECE_initial ≥ 0.5
- Convergence samples: n ≤ 500
- Statistical significance: p < 0.05 via bootstrap test

*Basis*:
Online learning literature suggests well-designed self-supervised signals converge within hundreds of samples; 50% reduction validates ensemble agreement as effective calibration signal.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Task-expert matching accuracy < 56%
   (= 75% × 0.75, >25% below target; indicates routing no better than random with 8 experts)

2. **Mechanism Failure**: Ensemble agreement (H) does not correlate with routing quality
   (measured by Spearman correlation ρ < 0.3; breaks core self-supervision assumption)

3. **Baseline Failure**: Performance worse than static uniform routing
   (indicates adaptive routing introduces harmful variance)

4. **Convergence Failure**: ECE does not decrease after 1000 samples
   (indicates online calibration mechanism is ineffective)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode (no SOTA comparison target)*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.5 (medium effect, conservative estimate)
- Required runs: n ≥ 25 per condition
- Statistical power: 0.8 (β = 0.2)
- Significance level: α = 0.05 (one-tailed for improvement claims)

**Test Specifications:**

*Primary Prediction (P1)*:
- Method: Paired t-test (ECAR vs static routing baseline, same random seeds)
- Null hypothesis: μ_ECAR ≤ μ_baseline
- Report format: Mean difference, 95% CI, Cohen's d, p-value

*Secondary Prediction (P2)*:
- Method: Paired t-test for compute savings, equivalence test for performance parity
- Equivalence margin: ±2% task performance
- Report format: FLOPs reduction %, performance difference, CI, p-value

*Secondary Prediction (P3)*:
- Method: Bootstrap test for ECE reduction significance
- Bootstrap samples: 1000 resamples
- Report format: ECE_initial, ECE_final, reduction %, 95% CI, p-value

**Control Measures:**
- Fixed random seeds across all experimental runs for reproducibility
- Identical model initialization and hyperparameters for fair comparison
- Stratified sampling across task types to ensure balanced evaluation
- Multiple base MoE architectures tested (OLMoE-7B, Mixtral-8x7B) for generalization

**Limitations:**
- Medium effect size assumption may require larger sample if true effect is smaller
- Multi-task benchmark choice affects generalization claims
- Calibration convergence speed may vary significantly across task distributions

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type**: Methodological
- **Statement**: We introduce a novel framework for test-time adaptive MoE routing that combines temperature-scaled calibration with ensemble-based self-supervised online updates, enabling single pre-trained MoE models to adaptively serve multiple tasks without fine-tuning. The core innovation is using ensemble agreement (output entropy) as a self-supervised calibration signal, which bypasses the supervision paradox that plagued prior counterfactual approaches.
- **Novelty**: Unlike prior work that applies calibration only to output predictions (not routing decisions) or requires ground truth for routing quality assessment, ECAR extends calibration theory to the routing mechanism itself and leverages expert consensus as a proxy for routing correctness. This enables online calibration adaptation at test-time without task labels.

**Secondary Contributions:**
- **Theoretical**: Establishes ensemble agreement as self-supervised signal for routing calibration quality without ground truth; formalizes confidence-based compute allocation for MoE inference optimization
- **Practical**: Reduces deployment costs by enabling single MoE model multi-task serving (vs per-task model variants); optimizes inference efficiency through adaptive expert activation (30-40% compute reduction on high-confidence cases)
- **Systems**: Lightweight meta-router design (<1% parameters) enables retrofitting to existing MoE models; EMA-stabilized online updates provide practical convergence guarantees

---

## 3. Key Related Work

**Foundation Sources (MUST CITE):**

1. **"MoELoRA: Contrastive Learning Guided Mixture of Experts on Parameter-Efficient Fine-Tuning for Large Language Models"** (2024)
   - Authors: Tongxu Luo, Jiahe Lei, Fangyu Lei, et al.
   - Semantic Scholar ID: af6aa336c25ead669da0df560376a32314e08006
   - Citations: 44
   - Key Finding: Contrastive learning mitigates random routing phenomenon in MoE, achieving 4.2% improvement over vanilla LoRA across 11 math/common-sense reasoning tasks
   - *How it supports ECAR*: Provides evidence that contrastive task embeddings enable effective routing specialization; ECAR extends this with calibration layer

2. **"OLMoE: Open Mixture-of-Experts Language Models"** (2024)
   - Authors: Niklas Muennighoff, Luca Soldaini, Dirk Groeneveld, et al. (Allen AI)
   - Semantic Scholar ID: 817632c42e735911e14b89e851ceaf54ba2ad25f
   - Citations: 164
   - Key Finding: First fully open MoE model (7B params, 1B active) demonstrating high expert specialization through routing analysis
   - *How it supports ECAR*: Establishes that expert specialization naturally emerges during training; ECAR leverages this for adaptive routing

3. **"FSMoE: A Flexible and Scalable Training System for Sparse Mixture-of-Experts Models"** (2025)
   - Authors: Xinglin Pan, Wen-Jing Lin, Lin Zhang, et al.
   - Semantic Scholar ID: 103294b4f375e30f34e7e5463f06499cce3346a6
   - Citations: 14
   - Key Finding: Systems optimization achieving 1.18×-3.01× speedup over DeepSpeed-MoE through task scheduling and adaptive pipelining
   - *How it supports ECAR*: Provides efficiency motivation; calibrated routing reduces over-activation, complementing systems-level optimizations

**Comparison Baselines:**

4. **Static Top-K Routing** (Standard MoE Baseline)
   - Used in OLMoE, Mixtral-8x7B
   - Key Characteristics: Fixed number of experts (K) activated per input, no adaptation
   - *ECAR Comparison*: ECAR adapts K based on routing confidence (1, 3, or 5 experts)

5. **Uniform Routing** (Trivial Baseline)
   - Equal weight to all experts
   - Key Characteristics: No specialization, maximum compute cost
   - *ECAR Comparison*: ECAR tests if adaptive routing beats uniform distribution

**Gap Evidence:**

6. **"Adapted-MoE"** (2024) - Feature Calibration for Anomaly Detection
   - Demonstrates calibration applied to MoE input features, NOT routing decisions
   - *Gap*: ECAR fills gap by applying calibration directly to routing logits

7. **"Rewiring Experts"** (2025) - Continuous Expert Rerouting
   - Performs dynamic rerouting but lacks calibration framework
   - *Gap*: ECAR adds principled calibration with confidence quantification

8. **Ensemble Uncertainty Quantification Literature** (Multiple Sources)
   - Standard ML practice: ensemble agreement indicates prediction confidence
   - *Transfer to ECAR*: ECAR adapts this principle to routing quality assessment via output entropy

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Foundation):**
Does calibrated adaptive routing improve task-expert matching accuracy and compute efficiency in pre-trained MoE models under test-time multi-task serving conditions?
- Maps to: Primary prediction P1 (routing accuracy > 75%)
- Verification type: Empirical (multi-task benchmarks)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism - Core):**
Is the three-step causal mechanism (contrastive task embeddings → temperature-scaled calibration → ensemble-based online updates) the actual cause of improved routing quality and efficiency?
- Maps to: Causal mechanism with 3 steps
  - SH-M1: Contrastive task embeddings → Routing logits (MoELoRA evidence)
  - SH-M2: Temperature scaling → Calibrated confidence distributions (calibration theory)
  - SH-M3: Ensemble agreement → Online calibration updates (self-supervision mechanism)
- Verification type: Causal analysis + ablation studies
- Critical: Determines explanatory power
- **Note:** Phase 2B will create 3 separate sub-hypotheses (H-M1, H-M2, H-M3) for each causal link

**SH3 (Comparison - Validation):**
Does ECAR outperform static routing baselines (uniform routing, fixed top-K routing) on routing accuracy, compute efficiency, and calibration quality metrics?
- Maps to: Secondary predictions P2 (compute efficiency), P3 (calibration convergence)
- Verification type: Comparative empirical
- Baselines: Static top-K (OLMoE), uniform routing, no-calibration baseline
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-ECAR-v1)
- [x] Confidence level specified (0.78)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (5 variables: τ, P_max, K, H, α)
- [x] Causal mechanism has evidence at each step (N=3 steps with evidence table)
- [x] Causal chain length determined (N=3, stored)
- [x] Key tension identified (ensemble agreement correlation needs validation)
- [x] Key assumptions list consequences if violated (4 assumptions with consequences)
- [x] 3 testable predictions exist (P1 primary, P2 and P3 secondary)
- [x] Falsification criteria defined (4 failure conditions)
- [x] Baselines identified (static top-K, uniform routing)
- [x] SH1, SH2, SH3 are clear starting points

**Status**: ✅ ALL REQUIREMENTS MET - Ready for Phase 2B

### Open Questions

1. **Multi-Task Benchmark Selection**: Which multi-task benchmark provides sufficient task diversity to test routing specialization while maintaining evaluation tractability? Options: MMLU (57 tasks), BIG-Bench (200+ tasks), or custom multi-domain benchmark.

2. **Base MoE Model Selection**: Should verification prioritize OLMoE-7B (fully open, well-documented) or Mixtral-8x7B (higher performance, larger scale) as primary base model? Trade-off: reproducibility vs practical impact.

3. **Ensemble Agreement Ground Truth**: How to establish ground truth for validating Assumption 1 (ensemble agreement correlates with routing quality) without circular reasoning? Potential approach: synthetic tasks with known optimal routing patterns for initial validation before real-world deployment.

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
