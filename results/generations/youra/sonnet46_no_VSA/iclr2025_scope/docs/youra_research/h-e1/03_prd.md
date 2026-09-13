# Product Requirements Document: H-E1
<!-- stepsCompleted: [1,2,3,4,5,6,7] -->

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-03
**Author:** Anonymous
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

Implement a controlled distillation experiment comparing three conversion strategies (MOHAWK-SSM, LAWCAT-linear-attention, Hybrid-4) applied to LLaMA-3-8B within a fixed token budget (≤1B tokens). The experiment validates whether a statistically significant task-type × conversion-strategy interaction exists on LongBench v2 normalized accuracy degradation (Δ_norm): specifically that MOHAWK-SSM degrades ≥2× more on retrieval-heavy tasks compared to LAWCAT.

**PoC Gate:** Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0 with 95% bootstrap CI strictly above 1.0 AND interaction p<0.01 (Holm-corrected).

---

## 2. Problem Statement

Short-context distillation of large language models (LLMs) into subquadratic architectures (SSMs, linear attention) degrades long-context performance differently depending on the replacement mechanism. Understanding this interaction pattern is critical for selecting the right conversion strategy for downstream long-context tasks. No systematic comparison of MOHAWK-SSM vs LAWCAT-linear-attention exists for LLaMA-3-8B at ≤1B token distillation budget on LongBench v2.

---

## 3. Functional Requirements

### FR-1: Teacher Model Setup
- Load `meta-llama/Llama-3-8B` via HuggingFace transformers in bfloat16
- Run LongBench v2 evaluation to obtain Acc_teacher per category (6 categories × 503 questions)
- Store per-example predictions (category, judge, difficulty, length)

### FR-2: MOHAWK-SSM Student Distillation
- Clone and configure `goombalab/mohawk` with LLaMA-3-8B configs (`configs/Llama/8B/`)
- Replace all 32 attention layers with DiscreteMamba2 SSD mixer
- Execute 3-stage MOHAWK distillation on allenai/c4 (≤1B tokens total):
  - Stage 1 (matrix orientation): ~26M tokens, LR=1e-3, Frobenius loss
  - Stage 2 (hidden-state alignment): ~52M tokens, LR=5e-4
  - Stage 3 (weight-transfer + KD): ~920M tokens, LR=1e-4, KL divergence T=2
- Batch size: 32 sequences (Stage 3), 8 (Stage 1/2); seq_len=2048; 4×A100 80GB DDP
- Perplexity gate: Student PPL gap ≤5% vs teacher on C4 val
- Alignment gate: L2 hidden-state ratio ≤0.15 at midpoint checkpoint

### FR-3: LAWCAT Student Distillation
- Clone and configure `zeyuliu1037/LAWCAT` for LLaMA-3-8B (adapt from LLaMA-3.2-1B config)
- Replace all 32 attention layers with causal Conv1D (kernel=4) + normalized GLA
- Execute 2-phase distillation on allenai/c4 (≤1B tokens total):
  - Phase 1 (MSE alignment): ~50M tokens, LR=1e-2, MSE loss weight=1000, CE weight=0
  - Phase 2 (LoRA fine-tuning): LoRA r=16 α=32 on Q,K,V,O; LR=1e-4; remaining budget
- Seq_len=1024; 2×A100 80GB; seed=0

### FR-4: Hybrid-4 Student Distillation
- Retain 4 middle attention layers (layers 14–17) in LLaMA-3-8B; replace remaining 28 with DiscreteMamba2
- Run MOHAWK Stage 3 only from MOHAWK-SSM checkpoint (weight-transfer + KD fine-tuning)
- Budget: shares MOHAWK training infrastructure; Stage 3 only additional fine-tuning (~200M tokens)

### FR-5: LongBench v2 Evaluation (All Models)
- Evaluate all 4 models (teacher + 3 students) on full LongBench v2 (503 questions)
- Dataset: `load_dataset("THUDM/LongBench", "v2")` via HuggingFace
- Format: 0-shot MCQ (A/B/C/D); exact letter match judge
- Compute per-category accuracy: 6 categories (single_doc_qa, multi_doc_qa, long_in_context_learning, long_dialogue, code_repo, long_structured_data)
- Compute Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher per category per student

### FR-6: Statistical Analysis
- Compute interaction ratio: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval)
  - Retrieval-heavy = {multi_doc_qa, long_structured_data} (~174 questions)
  - Generation-heavy = {long_in_context_learning} (~83 questions)
- Compute 95% bootstrap CI (10,000 resamples) on the interaction ratio
- Fit mixed-effects model: Δ_norm ~ TaskType * Strategy + (1|Task) using statsmodels/pymer4
- Apply Holm correction to p-values; report interaction term p-value

### FR-7: Mechanism Verification
- Implement `verify_mechanism_activated()` checking:
  - MOHAWK Stage 1 Frobenius loss < 0.15 avg
  - SSM layers installed (no `self_attn` in student layers)
  - LAWCAT `conv_q` present in attention layers
  - Both students degrade vs teacher (Δ_norm_overall > 0.01)
  - Interaction direction correct (SSM retrieval > LAWCAT retrieval)

### FR-8: Visualization
- Mandatory: Bar chart — Δ_norm per category per strategy (MOHAWK-SSM, LAWCAT, Hybrid-4, Teacher=0)
- Additional:
  - Heatmap: Δ_norm [strategy × category] — 3×6 matrix
  - Error bar plot: Δ_norm^retrieval vs Δ_norm^generation per strategy with 95% bootstrap CIs
  - Ratio plot: Δ_norm^SSM(category) / Δ_norm^LAWCAT(category) across all 6 categories
- All figures saved to `h-e1/figures/`

### FR-9: Failure Detection and Abort Criteria
- Stage 1 Frobenius loss > 0.5 after 10k steps → FAIL (check attention extraction)
- Student PPL gap > 5% vs teacher → ABORT (budget too small)
- L2 hidden-state ratio > 0.15 at midpoint → ABORT (hidden-state distillation issue)
- LAWCAT Conv1D non-causal (future tokens leak) → FAIL
- Δ_norm < 0.001 all categories (student identical to teacher) → FAIL
- No interaction (SSM/LAWCAT ratio ≈ 1.0) → PoC FAIL, trigger PIVOT

---

## 4. Data Specification

### 4.1 Distillation Dataset
| Dataset | Source | Load Method | Size |
|---------|--------|-------------|------|
| allenai/c4 (en) | HuggingFace | `load_dataset("allenai/c4", "en")` | Streaming; 1B tokens sampled |

- Sequence length: 2048 (MOHAWK), 1024 (LAWCAT)
- Preprocessing: BPE tokenization with LLaMA-3 tokenizer (vocab 128k)
- No special augmentation

### 4.2 Evaluation Dataset
| Dataset | Source | Load Method | Size |
|---------|--------|-------------|------|
| LongBench v2 | THUDM/LongBench | `load_dataset("THUDM/LongBench", "v2")` | 503 questions, 6 categories |

- Format: Multiple-choice (A/B/C/D), 0-shot
- Language: Bilingual (English + Chinese)
- Context length: 8k–2M words
- **Auto-download**: both datasets via HuggingFace — NO manual download task needed

### 4.3 Task Category Labels (H-E1)
| Category | H-E1 Label | Questions |
|----------|------------|-----------|
| single_doc_qa | neutral | ~80 |
| multi_doc_qa | retrieval-heavy | ~83 |
| long_in_context_learning | generation-heavy | ~83 |
| long_dialogue | neutral | ~83 |
| code_repo | neutral | ~83 |
| long_structured_data | retrieval-heavy | ~91 |

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **Δ_norm** = (Acc_teacher − Acc_student) / Acc_teacher per category per student
- **Interaction ratio** = Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0

### 5.2 Success Criteria
| Criterion | Threshold |
|-----------|-----------|
| Interaction ratio | ≥ 2.0 with 95% bootstrap CI strictly above 1.0 |
| Interaction p-value | < 0.01 (Holm-corrected) in mixed-effects model |
| Mechanism activated | Both MOHAWK SSD and LAWCAT GLA+Conv1D installed |
| Distillation converged | Stage 1 Frobenius < 0.15; Stage 3 KD loss < 2.0 |
| Perplexity gate | Student PPL gap ≤ 5% vs teacher on C4 val |

### 5.3 Expected Baselines
- LLaMA-3-8B teacher: ~35–42% overall on LongBench v2
- MOHAWK-SSM retrieval Δ_norm: 0.15–0.35 (expected)
- LAWCAT retrieval Δ_norm: 0.05–0.15 (expected)

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds: MOHAWK seed=42, LAWCAT seed=0
- All checkpoints saved at each training stage
- Full config YAML stored per experiment run

### NFR-2: Hardware
- MOHAWK: 4×A100 80GB (DDP); LAWCAT: 2×A100 80GB
- Precision: bfloat16 throughout
- Flash-attn 2.x for teacher inference

### NFR-3: Code Structure
- Modular: separate scripts for each distillation stage
- Official repos cloned (NOT reimplemented): goombalab/mohawk, zeyuliu1037/LAWCAT, THUDM/LongBench
- Results stored as JSON per model; visualizations as PNG

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.1
transformers>=4.40
datasets
mamba-ssm
causal-conv1d==1.4.0
flash-attn==2.6.3
flash-linear-attention  # fla-org
statsmodels
pymer4
scipy
numpy
matplotlib
seaborn
peft  # for LAWCAT LoRA
accelerate
bitsandbytes
```

### 7.2 External Repositories (clone, do not pip install)
- `goombalab/mohawk` — MOHAWK distillation framework
- `zeyuliu1037/LAWCAT` — LAWCAT official implementation
- `THUDM/LongBench` — evaluation scripts

### 7.3 Model Access
- `meta-llama/Llama-3-8B` — requires HuggingFace access token (Meta gated model)
- allenai/c4 — public, auto-download
- THUDM/LongBench v2 — public, auto-download

---

## 8. Out of Scope

- Training beyond 1B tokens (fixed budget constraint)
- Architectures other than MOHAWK-SSM, LAWCAT, Hybrid-4
- LongBench v1 evaluation
- Fine-tuning on long-context data after distillation
- Quantization experiments

---

## 9. Phase 2C Completeness Check

| Item | Present |
|------|---------|
| Baseline model (LLaMA-3-8B teacher) | ✓ FR-1 |
| MOHAWK-SSM conversion | ✓ FR-2 |
| LAWCAT conversion | ✓ FR-3 |
| Hybrid-4 ablation | ✓ FR-4 |
| LongBench v2 evaluation | ✓ FR-5 |
| Statistical analysis (interaction test) | ✓ FR-6 |
| Mechanism verification | ✓ FR-7 |
| Visualizations | ✓ FR-8 |
| Failure/abort criteria | ✓ FR-9 |
| allenai/c4 distillation dataset | ✓ Sec 4.1 |
| Custom Δ_norm metric | ✓ Sec 5.1 |
