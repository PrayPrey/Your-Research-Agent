# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-13T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Absence of Controlled LoRA Adapter Dataset with Verified Provenance
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 11

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 11

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

1. Previous failures (p=0.127) were due to statistical power issues, not methodology flaws
2. Cohen's d = 0.91 in uncontrolled setting suggests the effect is real and large
3. Model Zoo methodology [Schürholt 2022] is directly applicable to LoRA adapters
4. FLAN task taxonomy provides external ground truth for semantic similarity validation
5. Controlled provenance (identical base model, fixed hyperparameters) eliminates confounding

### Breakthrough Moments

1. **Dr. Nova's "LoRA Zoo" concept**: Adapting Model Zoo methodology specifically for LoRA adapters rather than fighting heterogeneity of public adapters
2. **Prof. Rex's control conditions**: Three-tier testing to rule out alternative explanations (vocabulary overlap, output format similarity, training stochasticity)
3. **Prof. Vera's falsification framework**: Clear numerical thresholds (p < 0.05, d > 0.5) with multiple paths to rejection

---

## Final Hypothesis

### Title
LoRA Adapter Geometric Signatures for Task Similarity Detection

### Hypothesis ID
H-LoRAGeo-v1

### Core Claim

Under controlled experimental conditions (single verified base model, identical LoRA hyperparameters, deterministic training), if we train LoRA adapters on semantically similar tasks and compute Grassmann distances between their B matrix column spaces, then within-category distances will be significantly smaller than between-category distances (p < 0.05, Cohen's d > 0.5), because fine-tuning induces task-specific geometric modifications to weight spaces that are constrained by LoRA's low-rank structure.

### Mechanism

1. **Step 1**: Fine-tuning on a specific task induces weight updates that encode task-relevant transformations
2. **Step 2**: LoRA constrains these updates to a low-rank subspace defined by the B matrix column space
3. **Step 3**: Semantically similar tasks require similar functional transformations, leading to similar B column spaces
4. **Step 4**: Similar B column spaces manifest as smaller Grassmann distances (mathematical property)

**Key Tension**: Step 3 assumes "similar tasks require similar transformations" - this is the core empirical claim to validate.

---

## Predictions

### P1: Primary Prediction (Existence)
- **Statement**: Within-cluster Grassmann distances are smaller than between-cluster distances
- **Test Method**: Mann-Whitney U test comparing within-cluster vs between-cluster distance distributions
- **Success Criterion**: p < 0.05 AND Cohen's d > 0.5
- **Falsification**: p > 0.10 OR Cohen's d < 0.3 with adequate sample size

### P2: Correlation Prediction
- **Statement**: Grassmann distance correlates with FLAN task taxonomy distance
- **Test Method**: Spearman rank correlation between pairwise Grassmann distances and task taxonomy distances
- **Success Criterion**: ρ > 0.3, p < 0.05
- **Falsification**: ρ < 0.1 OR p > 0.10

### P3: Control Prediction
- **Statement**: Within-task variance (different seeds) is much smaller than within-cluster variance
- **Test Method**: Compare mean within-task distance vs mean within-cluster distance
- **Success Criterion**: within-task distance < 0.5 × within-cluster distance
- **Falsification**: within-task distance ≥ within-cluster distance

---

## Novelty

### Key Innovation
First controlled validation of LoRA geometric signature hypothesis with adequate statistical power using Model Zoo methodology adapted for LoRA adapters.

### Differentiation from Prior Work

| Prior Work | Our Approach |
|------------|--------------|
| StelLA [Li 2025]: Stiefel manifold for LoRA optimization | We analyze trained adapters for task similarity, not optimize training |
| FL-TAC [Ping 2024]: Adapter clustering in federated setting | We validate with controlled experiments and adequate power |
| Model Zoos [Schürholt 2022]: Full model weight populations | We adapt methodology specifically for LoRA adapters |

---

## Experimental Design

### Base Models
- **Initial**: Llama-3.2-1B (faster iteration)
- **Replication**: Llama-2-7B (generalizability)

### Tasks (8 total from existing benchmarks)

**Reasoning Cluster (4 tasks)**:
- GSM8K (math reasoning)
- ARC-Challenge (science reasoning)
- LogiQA (logical reasoning)
- StrategyQA (multi-hop reasoning)

**NLU Cluster (4 tasks)**:
- MNLI (natural language inference)
- QQP (paraphrase detection)
- SST-2 (sentiment analysis)
- MRPC (paraphrase corpus)

### Adapters
- 20 adapters per task (8 tasks = 160 adapters)
- 5 seed variants per task for control condition (40 additional)
- **Total: 200 adapters**

### LoRA Configuration
- Rank: r=32 (ablation: {16, 32, 64})
- Alpha: 64
- Dropout: 0.05
- Target modules: q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj

### Training
- Learning rate: 2e-4
- Batch size: 8
- Epochs: 3
- Seed: 42 (deterministic)

---

## Limitations

### Scope Limitations (Acceptable)
1. **Base Model Specificity**: Results on Llama family may not transfer to other architectures (explicitly bounded scope)
2. **Task Selection**: 8 tasks is a sample from broader task space; negative results don't prove universal falsity
3. **Rank Dependency**: Effect may only appear at certain LoRA ranks (to be tested via ablation)

### What This Does NOT Explain
- Why certain layers cluster better than others (secondary finding)
- Whether results generalize to non-transformer architectures
- Multi-task or continual learning settings

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Acceptable scope limitations only |

### Persona Verdicts

| Persona | Verdict | Key Assessment |
|---------|---------|----------------|
| 🔭 Dr. Nova (Novelty) | STRONG | Methodologically novel; first controlled validation |
| 🔬 Prof. Vera (Falsifiability) | STRONG | Clear thresholds; multiple falsification paths |
| 🎯 Dr. Sage (Significance) | STRONG | Practical + theoretical + methodological impact |
| ⚙️ Prof. Pax (Feasibility) | STRONG | Technically achievable; ~100 GPU-hours |
| 🛡️ Dr. Ally (Synthesis) | STRONG | Addresses all previous failure modes |
| 🔍 Prof. Rex (Critique) | SATISFIED | All major concerns addressed |

---

## Phase 2B Readiness

| Criterion | Status |
|-----------|--------|
| Core hypothesis defined | ✅ |
| Variables specified (IV/DV/Controlled) | ✅ |
| Causal mechanism articulated | ✅ |
| Predictions with success criteria | ✅ |
| Falsification criteria defined | ✅ |
| Experimental design specified | ✅ |
| Feasibility constraints satisfied | ✅ |

**Status: READY FOR PHASE 2B**

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
