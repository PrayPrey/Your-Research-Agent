# PRD: H-E1 — Effective Rank as Zero-Shot LoRA Rank Predictor (Existence Proof)

**Version**: 1.0
**Date**: 2026-08-05
**Author**: Anonymous
**Hypothesis**: H-E1 (EXISTENCE / MUST_WORK)
**Phase 2C Source**: h-e1/02c_experiment_brief.md

---

## 1. Executive Summary

This document specifies requirements for implementing the H-E1 existence proof experiment, which tests whether the effective rank `erank(W₀) = exp(H(σ/‖σ‖₁))` of pre-trained transformer weight matrices (computed in fp32 before fine-tuning) shows statistically significant positive Pearson correlation (r ≥ 0.65, one-tailed p < 0.05) with per-layer PARA oracle ranks across ≥2/3 model families {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224}.

**Success condition**: Pearson r ≥ 0.65, one-tailed p < 0.05, ≥2 of 3 model families.

---

## 2. Problem Statement

Current LoRA rank selection is ad-hoc (fixed uniform rank). The hypothesis proposes that `erank(W₀)` of pre-trained weight matrices can zero-shot predict optimal per-layer LoRA ranks without fine-tuning. This experiment validates the existence of this correlation using the PARA (Per-layer Absolute Rank Ablation) oracle as ground truth.

**Oracle Definition**: For each layer `l`, the PARA oracle rank is `argmax_{r ∈ {4,8,16,32,64}} val_acc(r)`, where only layer `l` is tuned at rank `r` and all other layers are frozen at baseline rank `r=8`.

---

## 3. Functional Requirements

### FR-1: erank Computation Module
- Compute `erank(W₀) = exp(-Σ p_i log p_i)` where `p_i = σ_i / ‖σ‖₁`
- Input: pretrained weight matrix W (2D tensor, fp32)
- Process: `torch.linalg.svdvals(W.float())`, filter `S[S > 1e-10]`, normalize, entropy, exp
- Output: scalar erank value per layer
- Coverage: all 2D weight matrices excluding embeddings and LayerNorm
- Expected layer counts: BERT ~60, DeBERTa ~72, ViT ~72

### FR-2: PARA Oracle Sweep
- For each model and each target layer `l`:
  - Train LoRA with target layer at rank `r ∈ {4,8,16,32,64}`, all others frozen at `r=8`
  - 2 seeds per (layer, rank) pair; use mean validation accuracy for argmax
  - Record `oracle_rank[l] = argmax_r mean_acc`
- Models: BERT-base-uncased (MNLI), DeBERTa-v3-base (MNLI), ViT-base-patch16-224 (CIFAR-10)
- **Scale**: ~5 ranks × ~72 layers × 3 models × 2 seeds = ~2,160 training runs; parallelization required

### FR-3: GLUE MNLI Fine-tuning (BERT + DeBERTa)
- Dataset: GLUE MNLI, 392,702 train / 9,815 validation-matched
- Auto-download via `load_dataset("glue", "mnli")` — no manual download required
- Preprocessing: tokenize, max_length=128, truncation=True, padding="max_length"
- Epochs: ≥3 (BERT), ≥3 (DeBERTa)
- Optimizer: AdamW, lr=2e-5, weight_decay=0.01
- Batch size: 32 (effective)
- LR schedule: linear warmup 6% + linear decay
- DeBERTa: FP32 mandatory (FP16 causes classifier overflow)
- BERT: FP16/BF16 acceptable
- Metric: validation-matched accuracy

### FR-4: CIFAR-10 Fine-tuning (ViT)
- Dataset: CIFAR-10, 50,000 train / 10,000 test
- Auto-download via `load_dataset("uoft-cs/cifar10")` or `torchvision.datasets.CIFAR10`
- Preprocessing: resize 224×224, normalize ImageNet mean/std
- Augmentation (train only): RandomHorizontalFlip + RandomCrop(32, padding=4)
- Epochs: ≥5
- Optimizer: AdamW, lr=1e-4, weight_decay=0.01
- Batch size: 128
- LR schedule: linear warmup 6% + linear decay
- Metric: test accuracy

### FR-5: Correlation Analysis
- Compute Pearson r between erank_vector and oracle_rank_vector per model family
- One-tailed p-value: `p_one_tailed = scipy.stats.pearsonr(x, y).pvalue / 2`
- Bootstrap 95% CI (n=1000 resamples) per model family
- Secondary metric: Participation Ratio `PR(W₀)` correlation (record, no gate)
- Success: r ≥ 0.65 AND one_tailed_p < 0.05 for ≥2/3 families

### FR-6: Result Reporting
- Save erank_map per model as JSON/CSV
- Save oracle_rank_map per model as JSON/CSV
- Save correlation results: {model: {r, p_one_tailed, p_two_tailed, ci_low, ci_high}}
- Save validation accuracy table (all oracle runs)
- Mandatory figure: scatter plot erank(W₀) vs oracle_rank per model family with Pearson r annotation

### FR-7: Visualization
- Scatter plots: erank(W₀) vs oracle_rank (3 subplots, color-coded by layer type)
- Layer-depth heatmaps: erank per depth per model
- Oracle rank distribution histograms per model
- Bootstrap CI bar plot: Pearson r ± 95% CI per family
- Save to `docs/youra_research/h-e1/figures/`

### FR-8: Target Modules per Model
- BERT-base-uncased: `query`, `key`, `value`, `dense` (all 2D Linear layers in attention + intermediate/output)
- DeBERTa-v3-base: `query_proj`, `key_proj`, `value_proj`, `pos_proj`, FFN layers
- ViT-base-patch16-224: `query`, `key`, `value`, `dense`, MLP linear layers

### FR-9: LoRA Configuration
- PEFT library (`pip install peft`)
- Non-target layers: LoRA frozen at baseline `r=8` (adapter weights not updated)
- Target layer: fresh LoRA adapter at candidate rank `r`
- LoRA alpha: `2*r` (standard doubling heuristic)
- Dropout: 0.0 (oracle measurement)

### FR-10: Mechanism Verification
- Verify `erank_map` has ≥60 entries per model
- Verify oracle_rank varies (>1 unique value) per model
- Verify positive direction (r > 0) before full correlation check
- Log all mechanism activation indicators

---

## 4. Data Specification

| Dataset | Type | Source | Train | Eval | Download |
|---------|------|--------|-------|------|----------|
| GLUE MNLI | NLU | HuggingFace `glue/mnli` | 392,702 | 9,815 (val-matched) | Auto |
| CIFAR-10 | Vision | HF `uoft-cs/cifar10` or torchvision | 50,000 | 10,000 | Auto |

Both datasets are auto-download. No manual preparation required.

---

## 5. Evaluation Metrics

| Metric | Threshold | Gate | Notes |
|--------|-----------|------|-------|
| Pearson r (per family) | ≥ 0.65 | MUST_WORK | one-tailed |
| One-tailed p-value | < 0.05 | MUST_WORK | = two-tailed p / 2 |
| Families passing | ≥ 2/3 | MUST_WORK | both r and p thresholds |
| Oracle acc (BERT MNLI) | 83–87% | Reference | uniform r=8 expected ~84.5% |
| Oracle acc (DeBERTa MNLI) | 89–91% | Reference | uniform r=8 expected ~90.0% |
| Oracle acc (ViT CIFAR-10) | 96–99% | Reference | uniform r=8 expected ~97% |
| PR correlation | record only | No gate | participation ratio fallback |

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|------------|
| Parallelization | Must parallelize oracle sweep across layers (GPU multi-process or sequential with checkpointing) |
| Checkpointing | Save oracle results after each (model, layer, rank) group; resume on failure |
| Reproducibility | Fixed seeds [42, 137] for all training runs |
| Precision | FP32 for DeBERTa, FP16/BF16 acceptable for BERT/ViT |
| Memory | Each oracle run: 1 model + LoRA adapters; estimate ~8GB VRAM per BERT run |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
peft>=0.6.0
datasets>=2.14.0
evaluate>=0.4.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
torchvision>=0.15.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference Only)

| Repo | URL | Usage |
|------|-----|-------|
| khanghy1000 gist | gist.github.com/khanghy1000/5a3ae7473554542ed0bcd787b07d886c | erank formula reference |
| microsoft/LoRA | github.com/microsoft/LoRA | GLUE baseline reference |
| QingruZhang/AdaLoRA | github.com/QingruZhang/AdaLoRA | DeBERTa hyperparameters |

---

## 8. Success Criteria

```
PASS: Pearson r ≥ 0.65 AND one-tailed p < 0.05 for ≥2 of {BERT, DeBERTa, ViT}
FAIL: Above condition not met → MUST_WORK gate fails → H-M1, H-M2, H-M3 blocked
```

**Validation output**: `h-e1/04_validation.md` with full correlation results table.

---

## 9. Out of Scope

- Task-agnostic generalization (H-M3 scope)
- Mechanism decomposition by layer type (H-M1 scope)
- Adaptation magnitude correlation (H-M2 scope)
- Comparison against AdaLoRA/FIM-LoRA methods (Phase 5 scope)

---

## Appendix: Phase 2C Traceability

| Requirement | Source |
|------------|--------|
| erank formula | 02c §Models, khanghy1000 gist |
| PARA oracle definition | 02c §Proposed Model |
| MNLI hyperparameters | 02c §Training Protocol |
| CIFAR-10 hyperparameters | 02c §Training Protocol |
| r ≥ 0.65 threshold | 02c §Evaluation, Phase 2B §2.2 |
| Target modules per model | 02c §Models table |
| Bootstrap CI | 02c §Evaluation, Phase 2B §A5 |
