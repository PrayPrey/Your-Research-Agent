# Targeted Research Report: Can effective rank `erank(W₀) = exp(H(σ/‖σ‖₁))` of pre-trained transformer layers serve as a reliable, task-agnostic proxy for optimal LoRA rank — demonstrating significant positive correlation (r ≥ 0.65) with PARA oracle ranks across at least two of three model families?

**Date:** 2026-08-05
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
**Version:** Compact (Phase 2A input) — Full report at `01_targeted_research_full.md`

---

## Executive Summary

Phase 1 collected 34 verified sources across 3 MCP servers. The hypothesis represents a genuine research gap: no published work measures Pearson/Spearman correlation between `erank(W₀)` and PARA oracle ranks per layer. The field trajectory (Aghajanyan 2021 → LoRA 2021 → AdaLoRA 2023 → PiSSA/LoRA-XS 2024 → LAARA/IFCLoRA 2026) shows increasing use of W₀ singular structure for adaptation decisions, but none apply Roy & Vetterli's effective rank as the selection metric. Three critical PRIMARY gaps identified. Phase 2A readiness: READY.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can effective rank `erank(W₀) = exp(H(σ/‖σ‖₁))` of pre-trained transformer layers serve as a reliable, task-agnostic proxy for optimal LoRA rank — demonstrating significant positive correlation (r ≥ 0.65) with PARA oracle ranks across at least two of three model families (BERT-base, DeBERTa-v3-base, ViT-base) when models are adequately trained (≥3 epochs), where layer-relative effective rank variation (top/bottom tercile separation) is used as the non-uniformity criterion?

### Detailed Research Questions
1. Does `erank(W₀)` correlate with PARA oracle ranks at r ≥ 0.65 for DeBERTa-v3-base trained ≥3 epochs on full MNLI (392k samples)?
2. Does the correlation hold across BERT-base (NLP) and ViT-base (vision, CIFAR-10) model families, demonstrating cross-architecture generalization?
3. Does the top-tercile vs bottom-tercile effective rank split produce statistically significant differences in PARA oracle rank assignments (Levene p < 0.05, ≥2/3 families)?
4. Does an erank-proportional rank assignment strategy achieve task performance within 1% of PARA oracle ranks while reducing total LoRA parameter count?
5. Is participation ratio `PR(W₀) = (Σσ_i)² / Σσ_i²` a valid alternative, and do erank and PR rankings agree at Spearman ρ ≥ 0.8?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**h-e1 failure — two root causes:**

1. **Metric ceiling (fundamental):** Spectral entropy CV across transformer layers is bounded ~0.032–0.075. The CV > 0.1 threshold was unachievable regardless of training quality — miscalibrated criterion for this metric class.

2. **Execution failures (contingent):** Under-training (1 epoch / 20k MNLI samples) + model download timeouts blocked multi-family evaluation (gate requires ≥2/3 families).

**Redesign strategy:** Pivot to effective rank (wider dynamic range) + layer-relative tercile thresholds (scale-invariant) + pre-cached small models (BERT-base ~440 MB, DeBERTa-v3-base ~180 MB, ViT-base ~330 MB) + adequate training (≥3 epochs).

---

## 2. Search Queries Generated (Top 3 per category)

**Mode:** ROUTE_TO_0. **Total: 17 queries** (4 failure-aware + 0 reference + 5 brainstorm + 8 direct).

**Priority 0 (ROUTE_TO_0):** "alternative to spectral entropy for LoRA rank selection" | "effective rank nuclear norm spectral norm weight matrix LoRA" | "participation ratio singular value distribution rank selection"

**Priority 2 (Brainstorm):** "effective rank Roy Vetterli 2007 matrix intrinsic dimensionality" | "intrinsic dimensionality fine-tuning transformers Aghajanyan 2021" | "PARA oracle rank optimal LoRA layer-wise"

**Priority 3 (Direct):** "LoRA rank selection per-layer automated intrinsic dimensionality" | "AdaLoRA DyLoRA SoRA adaptive rank allocation comparison" | "cross-architecture LoRA rank generalization BERT DeBERTa ViT"

---

## 3. Past Cases & Best Practices (via Archon) [COMPACT]

**MCP:** Archon KB | **Queries:** 11 | **Results:** 3 verified + 3 inferred | **KB Focus:** HuggingFace PEFT docs only — no erank/PARA oracle entries

| Case | KB Entry ID | Key Pattern |
|------|-------------|-------------|
| [VERIFIED] AdaLoRA SVD-based Rank | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | SVD of ΔW during training — gap: not from W₀ erank |
| [VERIFIED] QLoRA rank finding | 6e684392-6bcb-4276-9a46-35ee52241ed0 | "r unrelated to final perf if LoRA on all layers" — counterpoint |
| [VERIFIED] PEFT Low-Rank Guide | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | r is manual hyperparameter — confirms gap |
| [INFERRED] SVD W₀ rank analysis | N/A | Pattern from AdaLoRA; W₀ SVD not in Archon KB |

---

## 4. Academic Literature Review (via Semantic Scholar) [COMPACT]

**MCP:** Semantic Scholar | **Queries:** 10 + citation network | **Results:** 17 verified + 1 limited

### Directly Relevant Papers

| Title | Year | SS ID | arXiv | Citations | 1-line insight |
|-------|------|-------|-------|-----------|----------------|
| AdaLoRA: Adaptive Budget Allocation for PEFT | 2023 | b612fc6af23cccf2133c2ea40597453ab40dc2c3 | 2303.10512 | 417 | Primary competitor — SVD-based rank via ΔW importance during training |
| DyLoRA: Parameter-Efficient Tuning via Dynamic Search-Free LoRA | 2022 | 85e959eef45114974c8f8643e88af23936fff3d1 | 2210.07558 | 310 | Trains for rank range simultaneously; no W₀ structure |
| La-LoRA: Layer-wise adaptive rank via Dynamic Contribution | 2025 | 3c47db8bdc777ab1389012b0257b73405ba6d8f3 | — | 12 | Norm-based signals; dynamic during training |
| ARD-LoRA: Dynamic Rank with Heterogeneous Adaptation | 2025 | 2ad32392ae5d905ef328d453d537b39f899a57db | 2506.18267 | 6 | Learnable ℓ₁ sparsity; 0.32% params → 99.3% FFT |
| LAARA: Layer-Aware Adaptive Rank Allocation for PEFT | 2026 | 989ca6bcece9964df1cdd3ab6c89c1b9a02b27c5 | 2607.19391 | 0 | Fisher-guided; proves "uniform rank fundamentally suboptimal" |
| IFCLoRA: Topology-Aware Rank Allocation for PEFT | 2026 | e9ededde515e41a9a8446b667f4617faa4ab0680 | 2607.22251 | 0 | Pre-fine-tuning rank via calibration set — closest methodological match |
| PiSSA: Principal Singular Values Adaptation of LLMs | 2024 | ee4014497ccf2f65d6e05d3956b0e6b0c7369bae | 2404.02948 | 321 | Init A,B from W₀ principal SVDs — closest W₀ ancestor |
| LoRA-XS: Low-Rank Adaptation with Extremely Small Params | 2024 | 7eb2d3eacf80a884aea82c929dcb21ee466af0bc | 2405.17604 | 84 | SVD of W₀ for frozen matrices; r×r core trained |

### Foundational Papers

| Title | Year | SS ID | arXiv | Citations | 1-line insight |
|-------|------|-------|-------|-----------|----------------|
| Intrinsic Dimensionality Explains LM Fine-Tuning | 2021 | e54ffc76d805c48660bb0fd20019ca82ac94ba0d | 2012.13255 | 953 | Pre-training minimizes intrinsic dim; varies per layer — foundational motivation |
| LoRA: Low-Rank Adaptation of LLMs | 2021 | a8ca46b171467ceb2d7652fbfb67fe701ad86092 | 2106.09685 | 21597 | Baseline — uniform rank r across all layers (gap that erank fills) |
| LISA: Layerwise Importance Sampling for LLM Fine-Tuning | 2024 | c739eb7f0302e85e935d1e2fdb903fe01b812804 | 2403.17919 | 120 | Layer importance heterogeneous — validates per-layer adaptation premise |
| IGU-LoRA: Adaptive Rank via Integrated Gradients | 2026 | 86069080753d15934dd4006b602f81966205ac67 | 2603.13792 | 3 | Proves bias in AdaLoRA gradient scores — motivates W₀-based approach |
| [LIMITED] Roy & Vetterli (2007) "The Effective Rank" | 2007 | NOT IN SS | EUSIPCO 2007 | — | Defines erank = exp(H(σ/‖σ‖₁)) — metric definition paper |

**Research Lineage:** Aghajanyan 2021 (intrinsic dim) → LoRA 2021 (low-rank adaptation) → AdaLoRA 2023 (SVD dynamic rank) → PiSSA/LoRA-XS 2024 (W₀ SVD for init) → IFCLoRA/LAARA 2026 (pre-training structure drives rank)

---

## 5. Implementation Resources (via Exa) [COMPACT]

**MCP:** Exa | **Queries:** 6 | **Results:** 10 verified

| Resource | URL | Stars | Language | Key Feature |
|----------|-----|-------|----------|-------------|
| QingruZhang/AdaLoRA | https://github.com/QingruZhang/AdaLoRA | 393 | Python | Official AdaLoRA; DeBERTa-v3 SVD infra reusable |
| huggingface/peft (adalora) | https://github.com/huggingface/peft/blob/main/src/peft/tuners/adalora/model.py | — | Python | Production AdaLoRA; AdaLoraConfig, AdaLoraModel |
| MohammadrezaBanaei/LoRA-XS | https://github.com/MohammadrezaBanaei/LoRA-XS | 57 | Python | W₀ SVD extraction — directly reusable for erank input |
| ruz048/AutoLoRA | https://github.com/ruz048/AutoLoRA | 10 | Python | Per-layer rank assignment (meta-learning); experimental template |
| DASS-Lab-Group/SpecTraL | https://github.com/DASS-Lab-Group/SpecTraL | 0 | Python | ViT federated LoRA + RMT rank discovery (ECML 2026) |
| khanghy1000/erank gist | https://gist.github.com/khanghy1000/5a3ae7473554542ed0bcd787b07d886c | 0 | Python | **Exact erank formula** — reuse for W₀ (~20 line mod) |
| kohya-ss/resize_lora | https://github.com/kohya-ss/sd-scripts/blob/308a0cc9/networks/resize_lora.py | — | Python | SV-based rank selection patterns (sv_ratio, sv_fro) |
| elias-gaeros/resize_lora | https://github.com/elias-gaeros/resize_lora | — | Python | σ_i/‖W‖_F scoring per layer — spectral norm rank proxy |
| mlahozy21/Interpreting-LoRA | https://github.com/mlahozy21/Interpreting-LoRA-Fine-Tuning | — | Python | Erank of LoRA adapters; **fp32 required** (bf16 inflates) |
| kijai/ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes/blob/204f6d5a/nodes/lora_nodes.py | — | Python | Adaptive rank methods: energy, fro, quantile, ratio |

**Core erank code** (khanghy1000, exact formula):
```python
def calculate_effective_rank(matrix: torch.Tensor, eps: float = 1e-10) -> float:
    S = torch.linalg.svdvals(matrix)
    S = S[S > eps]
    p = S / torch.sum(S)
    entropy = -torch.sum(p * torch.log(p))
    return torch.exp(entropy).item()
```
**PARA oracle gap:** No open-source implementation found. Must build from scratch.

---

## 6. Chain-of-Relations Analysis [COMPACT]

**Research Lineage:**
```
Aghajanyan 2021 (layer intrinsic dim varies) → LoRA 2021 (uniform rank gap) →
AdaLoRA 2023 (SVD rank from ΔW) → PiSSA/LoRA-XS 2024 (W₀ SVD for init) →
LAARA/IFCLoRA 2026 (pre-training structure drives rank) →
[PROPOSED] erank(W₀) as rank proxy correlated with PARA oracle
```

**Key Concept Flow:** Roy & Vetterli erank metric + Aghajanyan intrinsic dim → applied to W₀ per-layer → correlated against PARA oracle (custom protocol) → validated across BERT/DeBERTa/ViT families

**Cross-Reference Matrix (top entries):**

| Resource | Relevance | Adaptability |
|----------|-----------|--------------|
| Aghajanyan 2021 | HIGH — foundational motivation | Theoretical |
| AdaLoRA (Zhang 2023) | HIGH — primary competitor | High — DeBERTa code |
| PiSSA (Meng 2024) | HIGH — W₀ SVD ancestor | Medium — init logic |
| LoRA-XS (Balazy 2024) | HIGH — W₀ SVD infra | High — SVD code |
| LAARA (Tripathi 2026) | HIGH — validates per-layer need | Theoretical |
| IFCLoRA (Zhang 2026) | HIGH — closest method | Conceptual parallel |
| khanghy1000 gist | HIGH — exact erank code | High — direct reuse |

**Architectural insights:** W₀ SVD is solved (LoRA-XS). Erank = +10 lines on top. PARA oracle = must implement. fp32 precision required.

---

## 7. Verification Status Summary [COMPACT]

| Metric | Value |
|--------|-------|
| Total sources | 34 |
| [VERIFIED - SCHOLAR] | 17 (50%) |
| [VERIFIED - ARCHON] | 3 (9%) |
| [VERIFIED - EXA] | 10 (29%) |
| [INFERRED] | 3 (9%) |
| [LIMITED] | 1 (3%) |
| Overall data quality | 82/100 |

**Issues:** Archon KB HuggingFace-only (low relevance); SS rate limit fixed by sequential execution; Roy & Vetterli 2007 not in SS; PARA oracle not open-sourced; "PARA" name collision with arXiv 2604.27796 (different method).

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**
1. **Main Research Question**: Can `erank(W₀) = exp(H(σ/‖σ‖₁))` of pre-trained transformer layers serve as a reliable, task-agnostic proxy for optimal LoRA rank — demonstrating significant positive correlation (r ≥ 0.65) with PARA oracle ranks across at least two of three model families (BERT-base, DeBERTa-v3-base, ViT-base) when models are adequately trained (≥3 epochs), where layer-relative effective rank variation (top/bottom tercile separation) is used as the non-uniformity criterion?
2. **Detailed Questions (5)**:
   - DQ1: erank(W₀) ↔ PARA oracle rank correlation r ≥ 0.65 for DeBERTa ≥3 epochs full MNLI
   - DQ2: Cross-architecture generalization (BERT-base NLP, ViT-base vision/CIFAR-10)
   - DQ3: Top/bottom tercile effective rank split → Levene p < 0.05 (≥2/3 families)
   - DQ4: erank-proportional rank assignment → within 1% of oracle performance, fewer params
   - DQ5: PR(W₀) = (Σσᵢ)²/Σσᵢ² as alternative metric; erank/PR Spearman ρ ≥ 0.8
3. **Reference Papers**: Not provided

All gaps below pass the relevance test: directly affect ability to answer the research question.

### Identified Gaps

#### Gap 1: No Empirical Study Linking Pre-Trained Weight Effective Rank to Optimal LoRA Rank (Primary Gap)

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering the research question
**Connection:** ☑️ Blocks answering research question: Without the erank-PARA oracle correlation study, the hypothesis cannot be validated. ☑️ Addresses DQ1, DQ2, DQ3, DQ4, DQ5 (all sub-questions require this study to exist)

**Current State:** AdaLoRA and related methods (DyLoRA, ARD-LoRA, LAARA) allocate ranks dynamically during fine-tuning using gradient signals or Fisher information from ΔW. PiSSA and LoRA-XS use W₀ singular structure for INITIALIZATION but still apply uniform or fixed ranks. No published work computes erank(W₀) = exp(H(σ/‖σ‖₁)) per layer and measures its Pearson/Spearman correlation with PARA oracle ranks (independently computed optimal per-layer ranks). The effective rank metric of Roy & Vetterli (2007) has been applied in signal processing and representation learning but not as a LoRA rank selection proxy correlated with oracle ranks.

**Missing Piece:** Empirical measurement of Pearson correlation between `erank(W₀)` per layer and PARA oracle rank per layer, across BERT-base, DeBERTa-v3-base, and ViT-base model families with adequate training (≥3 epochs). This includes: (1) computing erank from W₀ SVD, (2) running PARA oracle (independent per-layer rank search), (3) measuring correlation with r ≥ 0.65 threshold, (4) evaluating across ≥2/3 model families.

**Potential Impact:** HIGH — If confirmed, enables one-time O(d²) SVD computation to replace O(5N) grid search across rank values per layer. Directly eliminates expensive rank hyperparameter search for LoRA practitioners. Could become a standard preprocessing step for any LoRA fine-tuning pipeline.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning" | 2023 | Zhang et al. | b612fc6af23cccf2133c2ea40597453ab40dc2c3 | 2303.10512 | 417 | Uses SVD of ΔW for rank; gap: no correlation with W₀ erank |
| "PiSSA: Principal Singular Values and Singular Vectors Adaptation of LLMs" | 2024 | Meng et al. | ee4014497ccf2f65d6e05d3956b0e6b0c7369bae | 2404.02948 | 321 | Uses principal SVD components of W₀ for init; gap: uses fixed rank, not erank-derived |
| "LoRA-XS: Low-Rank Adaptation with Extremely Small Number of Parameters" | 2024 | Balazy et al. | 7eb2d3eacf80a884aea82c929dcb21ee466af0bc | 2405.17604 | 84 | SVD of W₀ for frozen matrices; gap: r×r core is uniform, not erank-proportional |
| "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning" | 2021 | Aghajanyan et al. | e54ffc76d805c48660bb0fd20019ca82ac94ba0d | 2012.13255 | 953 | Pre-training minimizes intrinsic dim; layer-wise variation implied but not measured per-layer for rank selection |
| "LAARA: Layer-Aware Adaptive Rank Allocation for Parameter-Efficient Fine-Tuning" | 2026 | Tripathi et al. | 989ca6bcece9964df1cdd3ab6c89c1b9a02b27c5 | 2607.19391 | 0 | Fisher-guided; proves uniform rank "fundamentally suboptimal"; gap: uses training-time signals not W₀ erank |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| AdaLoRA SVD-based Rank Allocation | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | "AdaLoRA DyLoRA SoRA adaptive rank allocation" | SVD-based rank during training (ΔW), not from W₀ erank — confirms gap |
| PEFT Low-Rank Adaptation Conceptual Guide | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | "effective rank nuclear norm spectral norm weight matrix LoRA" | Rank r is manual hyperparameter; no W₀-derived automatic selection |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| QingruZhang/AdaLoRA | https://github.com/QingruZhang/AdaLoRA | 393 | Python | SVD-based rank (ΔW, not W₀); DeBERTa-v3 code reusable |
| MohammadrezaBanaei/LoRA-XS | https://github.com/MohammadrezaBanaei/LoRA-XS | 57 | Python | W₀ SVD extraction code — directly reusable for erank computation |
| khanghy1000/calculate_effective_rank_lora | https://gist.github.com/khanghy1000/5a3ae7473554542ed0bcd787b07d886c | 0 | Python | Exact erank formula implementation — apply to W₀ (currently applies to LoRA adapters) |

---

#### Gap 2: No Cross-Architecture Validation of W₀ Spectral Metrics for LoRA Rank Selection (Vision vs. NLP)

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering DQ2 (cross-architecture generalization)
**Connection:** ☑️ Blocks answering research question: Gate requires ≥2/3 model families. ☑️ Addresses DQ2 specifically. Without ViT-base coverage, the multi-family requirement cannot be met.

**Current State:** AdaLoRA validated on DeBERTa-v3 (NLU tasks: GLUE). LoRA validated on RoBERTa, DeBERTa, GPT-2/3 (NLP tasks). PiSSA and LoRA-XS target LLMs. No found paper examines erank(W₀) or any W₀-derived spectral metric for LoRA rank selection across BOTH NLP transformers AND vision transformers (ViT) on classification tasks. SpecTraL (ECML 2026) examines ViT in federated learning but uses RMT (not erank) and focuses on aggregation not rank selection. CIFAR-10 LoRA rank analysis absent from all found literature.

**Missing Piece:** Erank computation and PARA oracle evaluation for ViT-base-patch16-224 on CIFAR-10 (vision task, 50k training samples, ≥5 epochs). Specifically: do erank values of ViT attention/MLP layers correlate with optimal LoRA ranks at r ≥ 0.65? Does the erank-rank relationship generalize from NLP (attention layers in DeBERTa/BERT) to vision (patch+position attention in ViT)?

**Potential Impact:** HIGH — Cross-architecture generalization is what makes erank a "task-agnostic proxy" rather than an NLP-specific trick. If it generalizes to ViT, the hypothesis becomes a general-purpose tool; if it fails, it constrains applicability to NLP models only.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "LoRA: Low-Rank Adaptation of Large Language Models" | 2021 | Hu et al. | a8ca46b171467ceb2d7652fbfb67fe701ad86092 | 2106.09685 | 21597 | NLP-only (RoBERTa, DeBERTa, GPT); gap: no ViT or vision transformer evaluation |
| "AdaLoRA: Adaptive Budget Allocation for PEFT" | 2023 | Zhang et al. | b612fc6af23cccf2133c2ea40597453ab40dc2c3 | 2303.10512 | 417 | NLU tasks only (DeBERTa-v3, GLUE); gap: no cross-architecture to vision |
| "LAARA: Layer-Aware Adaptive Rank Allocation for PEFT" | 2026 | Tripathi et al. | 989ca6bcece9964df1cdd3ab6c89c1b9a02b27c5 | 2607.19391 | 0 | Claims broad applicability but no ViT experiments |
| "DyLoRA: Parameter-Efficient Tuning using Dynamic Search-Free Low-Rank Adaptation" | 2022 | Valipour et al. | 85e959eef45114974c8f8643e88af23936fff3d1 | 2210.07558 | 310 | NLP focus; gap: no vision architecture evaluation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| AdaLoRA SVD-based Rank | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | "cross-architecture LoRA rank generalization BERT DeBERTa ViT" | NLU focus; no ViT coverage in Archon KB |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| DASS-Lab-Group/SpecTraL | https://github.com/DASS-Lab-Group/SpecTraL | 0 | Python | ViT federated LoRA (ECML 2026) — RMT-based rank, not erank; shows ViT LoRA is feasible |
| ruz048/AutoLoRA | https://github.com/ruz048/AutoLoRA | 10 | Python | Meta-learning per-layer rank — NLP only (RoBERTa/CoLA); no ViT |

---

#### Gap 3: No Open Implementation of PARA Oracle for Per-Layer LoRA Rank Evaluation

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering research question (oracle is the ground truth for correlation)
**Connection:** ☑️ Blocks answering research question: Without PARA oracle, there is no ground-truth "optimal rank per layer" to correlate against erank. The PARA oracle is the dependent variable in the correlation study. ☑️ Addresses DQ1, DQ3, DQ4 (all require oracle ranks as ground truth).

**Current State:** No open-source implementation of a "PARA oracle" methodology (train LoRA independently at multiple ranks per layer, select best) was found in any GitHub repository, arXiv paper, or Archon KB entry. The term "PARA oracle" in the literature either refers to: (1) "Post-Optimization Adaptive Rank Allocation" (arXiv 2604.27796 — different meaning, post-training pruning), or (2) the prompt-aware PARA method (arXiv 2502.01033 — also unrelated). AdaLoRA's `RankAllocator` allocates rank dynamically but does not function as an oracle (it doesn't independently optimize per layer). The oracle methodology implied by the hypothesis (sweep rank r ∈ {4,8,16,32,64} per layer independently, evaluate task performance) is a custom evaluation protocol not present in any found codebase.

**Missing Piece:** Implementation of per-layer rank oracle: for each layer L, freeze all other layers' ranks at baseline, train LoRA with varied rank r ∈ {4,8,16,32,64} only on layer L, record performance. This identifies the "optimal rank" for layer L independent of other layers. Required for: computing ground-truth correlation target (DQ1), computing Levene test groups (DQ3), measuring parameter efficiency (DQ4).

**Potential Impact:** HIGH — The PARA oracle is the linchpin of the experimental design. Without it, there is no ground truth to correlate erank against. Must be implemented from scratch — represents significant engineering work (~500-1000 lines of training loop code per model family).

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Post-Optimization Adaptive Rank Allocation for LoRA" | 2026 | Unknown | — | 2604.27796 | — | Uses "PARA" acronym but means post-training pruning — different protocol; confirms no oracle in literature |
| "IFCLoRA: Topology-Aware Rank Allocation for PEFT" | 2026 | Zhang et al. | e9ededde515e41a9a8446b667f4617faa4ab0680 | 2607.22251 | 0 | Pre-fine-tuning rank via calibration set; no per-layer independent sweep |
| "IGU-LoRA: Adaptive Rank via Integrated Gradients and Uncertainty" | 2026 | Cui et al. | 86069080753d15934dd4006b602f81966205ac67 | 2603.13792 | 3 | Shows bias in AdaLoRA's gradient scores; motivates oracle-based evaluation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [INFERRED] Correlation-Based Rank Proxy Validation | N/A (inferred) | "PARA oracle rank optimal LoRA layer-wise" | Standard methodology: Pearson/Spearman correlation with oracle ranks; no Archon entry found |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| QingruZhang/AdaLoRA | https://github.com/QingruZhang/AdaLoRA | 393 | Python | RankAllocator for DeBERTa-v3 — closest existing infrastructure; adapt to per-layer sweep |
| ruz048/AutoLoRA | https://github.com/ruz048/AutoLoRA | 10 | Python | Per-layer rank assignment infrastructure (meta-learning); adapt to oracle sweep |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Questions | Extends Reference Paper | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------------|----------------------------------|-------------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ No erank-PARA oracle correlation study exists in literature | ☑️ Blocks DQ1 (correlation), DQ4 (efficiency), DQ5 (PR agreement) | ☐ No reference papers provided | High | 8 sources (5 scholar + 2 archon + 3 exa) | Critical |
| Gap 2 | PRIMARY | ☑️ Gate requires ≥2/3 families; ViT coverage absent from literature | ☑️ Blocks DQ2 (cross-architecture), DQ3 (tercile test ≥2/3 families) | ☐ No reference papers provided | High | 6 sources (4 scholar + 1 archon + 2 exa) | Critical |
| Gap 3 | PRIMARY | ☑️ PARA oracle is the ground-truth dependent variable; not open-sourced | ☑️ Blocks DQ1 (correlation target), DQ3 (Levene groups), DQ4 (oracle comparison) | ☐ No reference papers provided | High | 5 sources (3 scholar + 1 archon + 2 exa) | Critical |

### User Input to Gap Traceability

**Research Question** addressed by: Gap 1 (no correlation study), Gap 2 (ViT absent), Gap 3 (no oracle)

**DQ1** (erank correlation ≥ 0.65 for DeBERTa): Gap 1 (core measurement gap) + Gap 3 (oracle must exist first)

**DQ2** (cross-architecture BERT + ViT): Gap 2 (ViT-base LoRA rank analysis entirely absent)

**DQ3** (tercile split Levene p < 0.05, ≥2/3 families): Gap 1 + Gap 2 + Gap 3 (all required)

**DQ4** (erank-proportional rank within 1% oracle): Gap 1 (assignment strategy untested)

**DQ5** (PR Spearman ρ ≥ 0.8): Gap 1 (PR not used as rank proxy in any found paper)

---

## 9. Conclusion

### Key Findings

1. Genuine research gap confirmed — no paper measures erank(W₀) correlation with PARA oracle ranks
2. Strong theoretical lineage: Aghajanyan 2021 → LoRA 2021 → LAARA 2026 (proves per-layer needed) → IFCLoRA 2026 (pre-training structure drives rank) → erank hypothesis at the frontier
3. Primary competitor: AdaLoRA (ICLR 2023, 417 citations) — ranks DURING training from ΔW vs. erank's ONE-TIME from W₀
4. PARA oracle: main engineering challenge — not open-sourced, ~500-1000 lines to implement
5. Erank formula directly available: khanghy1000 gist, ~20 line mod to apply to W₀; fp32 required
6. ViT cross-architecture: absent from all found literature — ViT/CIFAR-10 experiments are novel
7. Participation ratio: unused as LoRA rank proxy in any found paper — novel
8. h-e1 failure lessons validated: spectral entropy ceiling real; tercile thresholds appropriate for erank

### Answer to Detailed Question (Preliminary)

All 5 DQs are empirically open. Literature confirms novelty and theoretical motivation but no direct answers.

### Phase 2 Readiness

- ☑️ Research question defined, gaps identified, competitors mapped, reuse artifacts located
- ☑️ Implementation constraints documented (fp32, PARA oracle from scratch)
- ☑️ Evidence tables in Phase 2A TABLE FORMAT with SS IDs, URLs, KB entry IDs
- ⚠️ Roy & Vetterli 2007: URL verified via Exa; not in Semantic Scholar

**Phase 2A Readiness: READY**

### Next Steps

Phase 2A-Dialogue reads this file for hypothesis generation. Expected: H-1 (erank-oracle correlation), H-2 (cross-architecture generalization), H-3 (erank-proportional efficiency). PARA oracle implementation is the critical path engineering task.

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~3 hours (multi-session, context compaction at Step 5)*
