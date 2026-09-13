# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** C:\Users\OWNER\Desktop\ResearchAgents_Integrated_0\ResearchAgents_5_4_0_YouRA_new_Yoon_experiment_sonnet45\tasks_youra_result_sh\neurips2024_crl\02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CATs-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under conditions of **transformer-based vision models (ViT) processing visual data (images)**, if **asymmetric causal attention with DAG constraints is integrated into multi-head attention layers via progressive training**, then **the model will learn sparse directed acyclic causal graphs over token representations that enable interpretable causal reasoning and counterfactual generation**, because **asymmetric attention masks with differentiable DAG penalties enforce directional causal relationships analogous to neuroscience effective connectivity measures (dDTF, gPDC)**.

**Alternative Hypothesis (H0):**
Asymmetric causal attention with DAG constraints does NOT enable transformers to learn meaningful causal representations. Either (1) the learned attention weights represent spurious correlations rather than causal structure, or (2) the hybrid architecture performs equivalently to standard ViT without causal constraints, or (3) the DAG penalties fail to converge at transformer scale (196+ tokens), making the approach infeasible for real vision models.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| **Causal Attention Mechanism** | Independent (Intervention) | Asymmetric attention masks (M_ij ≠ M_ji) with learnable weights, implemented as sigmoid transformations of weight matrices in k causal attention heads | Binary: WITH causal attention vs. WITHOUT (standard ViT baseline) |
| **DAG Structure Quality** | Dependent (Causal Discovery) | Structural Hamming Distance (SHD) between learned adjacency matrix and ground-truth DAG on synthetic datasets; F1 score for edge recovery | SHD: 0-100 (lower is better, 0 = perfect recovery); F1: 0.0-1.0 (higher is better, target: >0.7 on synthetic) |
| **Causal Identifiability** | Dependent (Representation Quality) | Mean Correlation Coefficient (MCC) between learned and true latent variables; Intervention prediction accuracy on held-out interventional data | MCC: 0.0-1.0 (target: >0.8 indicates identifiable representations); Intervention accuracy: 60-95% (target: >75%) |
| **Task Performance** | Dependent (Functional Quality) | ImageNet top-1 classification accuracy; MS-COCO object detection mAP | ImageNet: 75-85% (ViT-Base baseline ~81%, target: ≥80% to show no performance degradation); MS-COCO mAP: 35-45 |
| **Training Strategy** | Controlled | Progressive training: Stage 1 (pretrain standard ViT OR load pretrained weights), Stage 2 (gradual DAG penalty α: 0→1 over 20% of total epochs), Stage 3 (full optimization with α=1, λ=0.01-0.1) | 3-stage protocol, 125 epochs total (50 + 25 + 50), 8 GPUs, ~5 days |
| **Hybrid Architecture Ratio** | Controlled | Ratio k/h of causal attention heads to total heads | k/h ∈ {0.25, 0.5, 0.75} (default: 0.5 for ViT-Base with 12 heads = 6 causal + 6 full) |

### 1.3 Causal Mechanism

**Causal Chain (N=5 steps):**

The hypothesis proposes a 5-step causal mechanism transforming standard transformer attention into causal structure discovery:

**Step 1: Asymmetric Encoding** → Asymmetric attention masks (M_ij ≠ M_ji) enable directional information flow encoding (A→B distinct from B→A)

**Step 2: DAG Acyclicity Enforcement** → Differentiable DAG penalty h(M) = tr((I + αM⊙M)^d) - d prevents cycles

**Step 3: Sparsity Selection** → L1 regularization (λ||M||_1) selects true causal edges over spurious correlations

**Step 4: Progressive Optimization** → 3-stage training (pretrain → gradual DAG → full) prevents local minima

**Step 5: Hybrid Balance** → k causal heads + (h-k) full heads preserves global context while learning causal structure

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|----------------|-------------|----------|
| **Link 1** | Zheng & Liu 2025 (16 cites) | Asymmetric masking achieves 15.3% improvement in causal effect estimation | **High** |
| **Link 2** | phlippe/ENCO (88 stars) | Differentiable DAG penalty scales to ~100 nodes | **Medium** |
| **Link 3** | Xu et al. 2024 (22 cites) | Sparsity enables identifiability in partially observable CRL | **High** |
| **Link 4** | Standard DL practice | Warmup schedules prevent optimization instability | **Medium** |
| **Link 5** | Voita et al. 2019 (1200+ cites) | Transformer heads naturally specialize | **High** |

**Key Tension:**
Global Context vs. Causal Sparsity - Resolution via Hybrid Architecture (50% causal + 50% full attention heads)

### 1.4 Key Assumptions

1. **Multi-View Identifiability (Empirical):** Multiple causal attention heads learn different causal subgraphs (multi-view assumption) - Consequence if violated: non-identifiable representations

2. **Sparsity Induces True Structure:** L1 penalty selects true causal edges (assumes real systems are sparse ~10-20% density) - Consequence if violated: incomplete/incorrect causal graphs

3. **Attention Encodes Causality:** Attention weights can represent causal influence beyond correlation (validated by Mahesh 2024, Rohekar 2023) - Consequence if violated: learned graphs are meaningless

4. **Progressive Training Prevents Local Minima:** Gradual constraint introduction allows escape from poor minima - Consequence if violated: training converges to incorrect causal structure

### 1.5 Scope & Boundaries

**Domain:** Vision transformers (ViT) for image classification/detection on static images (NOT video/temporal)
**Scale:** ViT-Base to ViT-Large (86M-304M params), ImageNet/MS-COCO datasets (NOT LAION-5B web-scale)
**Identifiability:** Empirical identifiability (multi-view + sparsity), NOT provable CRL guarantees
**Compute:** 8 GPUs × 5 days (~$600), feasible for academic research

**Out-of-Scope:** Temporal CRL (video), multimodal (vision-language), diffusion models, web-scale validation, provable identifiability

### 1.6 Testable Predictions

**Primary Prediction (P1):**
H-CATs achieves **F1 > 0.70 for edge recovery** and **SHD < 20** on synthetic datasets with known ground-truth DAGs, while maintaining task performance within 2% of ViT baseline.

**Secondary Predictions:**
- **P2 (Mechanism):** Counterfactual images from do-operations achieve **>75% human agreement** vs. CausalVAE baseline (Amazon MTurk, N=100 raters × 50 pairs)
- **P3 (Performance):** Hybrid architecture (k/h=0.5) achieves **ImageNet accuracy ≥ 80%** (within 1% of ViT 81%) with **<30% edge density**

**Falsification Criteria:**
1. F1 < 0.50 on synthetic DAGs (causal structure failure)
2. ImageNet accuracy < 78% with k/h=0.5 (performance collapse)
3. DAG penalty h(M) > 10.0 after training (acyclicity failure)
4. Human agreement < 60% on counterfactuals (invalidity)
5. Attention becomes symmetric (mean |M_ij - M_ji| < 0.01) (mechanism collapse)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Mode:** Absolute Performance Validation (NOT SOTA comparison)

**Baselines:**
- Standard ViT-Base (81.0% ImageNet) - functional baseline
- CausalVAE (Yang 2020, 345 cites) - causal baseline
- PC/FCI (causal-learn) - classical causal discovery

**Not Targeting SOTA:** ViT-22B (90.5%), ConvNeXt-XL (87.8%) - H-CATs targets architectural innovation, not SOTA accuracy

### 1.8 Statistical Verification Design

**Primary Experiment:** 3 × 3 factorial (Architecture × Graph Complexity) on synthetic validation
- N=5 random seeds per cell (45 runs)
- DV: F1 score, SHD, task accuracy
- Test: Two-way ANOVA with Tukey HSD, α=0.05, power=0.80

**Secondary Experiments:**
- ImageNet: 2 × 3 factorial (Model × Training Strategy), N=3 seeds (18 runs), non-inferiority test (H-CATs ≥ 80%)
- Counterfactual: Paired comparison, N=100 MTurk raters × 50 pairs, binomial test (>75% preference)

**Ablations:** Asymmetric vs. symmetric, with vs. without DAG, sparsity levels, progressive vs. joint, head ratio sweep

**Reproducibility:** Code release (GitHub), pretrained weights (Zenodo), experiment logs (W&B)

---

## 2. Contribution Summary

**Primary:** First integration of causal representation learning into transformer attention mechanisms by reinterpreting multi-head attention as learnable DAGs with neuroscience-inspired asymmetric constraints - eliminates need for separate VAE-based causal modules

**Secondary:**
1. Hybrid architecture design pattern (50% causal + 50% full heads) balancing interpretability and performance
2. Progressive training protocol for constrained transformers (3-stage: pretrain → gradual constraint → full)
3. Empirical identifiability via multi-head attention (multi-view principle without interventional data)
4. Proxy task evaluation for real-world causal validation (PASCAL-Part object relationships)

---

## 3. Key Related Work

**Foundation Sources:**
1. **Zecevic et al. 2021** "Relating GNN to SCM" (67 cites) - Neural attention CAN represent causal structure
2. **Yang et al. 2020** "CausalVAE" (345 cites) - VAE + causal layer baseline, motivates integrated approach
3. **Yao et al. 2024** "Invariance Principle" (22 cites) - Multi-view identifiability theoretical basis

**Baselines:**
4. ViT (Dosovitskiy 2020) - Functional performance baseline (81.0%)
5. CausalVAE - Causal discovery quality baseline
6. PC/FCI (causal-learn) - Classical graph recovery baseline

**Gap Evidence:**
7. Phase 1 Gap 1: 60% VAE, 25% flow, minimal transformer CRL integration
8. Mahesh 2024 - Post-hoc Granger causality, not end-to-end training
9. Zheng & Liu 2025 (16 cites) - Asymmetric masking validation (15.3% improvement)

**Implementation:**
10. phlippe/ENCO (88 stars) - Differentiable DAG penalty code

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses:** 7 (SH1: 1, SH2: 5 mechanism links, SH3: 1)

**SH1 (Existence):**
"Transformers CAN learn sparse DAGs over tokens when trained with causal attention and DAG constraints on synthetic datasets"
- Maps to: P1 (F1 > 0.70, SHD < 20)
- Critical: MUST PASS for validation

**SH2 (Mechanism):**
"The 5-step mechanism (Asymmetric → DAG → Sparsity → Progressive → Hybrid) produces causal graphs enabling counterfactuals"
- Decomposes into: H-M1 (Asymmetric), H-M2 (DAG), H-M3 (Sparsity), H-M4 (Progressive), H-M5 (Hybrid)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"H-CATs (k/h=0.5) achieves ImageNet ≥ 80% with >75% counterfactual quality vs. CausalVAE"
- Maps to: P2, P3
- Critical: Determines practical value

### Readiness Checklist

- [✓] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [✓] Hypothesis ID: H-CATs-v1
- [✓] Confidence: 0.85
- [✓] Alternative H0 defined (3-part falsification)
- [✓] All variables operationalized (6 variables with measurement methods)
- [✓] Causal mechanism with N=5 steps + evidence table
- [✓] Causal chain length N=5 stored
- [✓] Key tension identified (Global vs. Sparse) with resolution
- [✓] 4 assumptions with consequences if violated
- [✓] 3 testable predictions (P1 primary, P2-P3 secondary)
- [✓] Falsification criteria (5 specific conditions)
- [✓] Baselines identified (ViT, CausalVAE, PC/FCI)
- [✓] SH1, SH2, SH3 defined with decomposition plan

**Readiness:** 14/14 (100%) ✅ **READY FOR PHASE 2B**

### Open Questions

1. **Optimal k/h ratio:** Is 0.5 best or task-dependent? → Phase 2B ablation k/h ∈ {0.25, 0.5, 0.75, 1.0}
2. **Scalability to 1024+ tokens:** Can DAG penalty scale beyond 256 tokens? → Phase 3 low-rank approximations
3. **Transfer to BERT/CLIP:** Does causal attention work in language/multimodal? → Phase 4 secondary validation
4. **Real image ground-truth:** Are PASCAL-Part proxies sufficient? → Phase 2B human annotation protocol
5. **Provable vs. empirical identifiability:** Can multi-head satisfy formal CRL conditions? → Theoretical analysis or empirical-only claims

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
