# Product Requirements Document: H-E1
# Existence Verification — Canonical Channel Permutation Invariance & Orbit-PE Computability

**Hypothesis ID:** H-E1
**Date:** 2026-05-21
**Author:** Anonymous
**Phase 2C Source:** 02c_experiment_brief.md
**Hypothesis Type:** EXISTENCE (PoC)
**Tier:** LIGHT (max 15 tasks)
**Gate:** MUST_WORK

---

## 1. Executive Summary

This document specifies requirements for implementing and running the H-E1 existence verification experiment. The experiment answers a binary question: **does applying canonical input/output channel permutations to trained neural network checkpoints preserve model accuracy (|Δacc| < 0.1%) for both CNN and Transformer architectures, and is orbit-PE computable for all standard layer types?**

This is an evaluation-only experiment — no model training occurs. The implementation loads pre-trained checkpoints from two established model zoo benchmarks, applies systematic channel permutations, re-evaluates each permuted model on its validation set, and measures accuracy change. A secondary check verifies that orbit-PE encoding vectors can be computed without architecture-specific branching for Linear, Conv2d, and MultiheadAttention layers.

**Hypothesis Statement:** Under weight space learning for model property prediction, if canonical input/output channel permutations are applied to both CNN and Transformer checkpoints, then validation accuracy changes by <0.1% for both architecture families and orbit-PE is computable for all layer types, because the input/output channel permutation group is a functionally valid architecture-agnostic symmetry for any linear operator.

---

## 2. Problem Statement

### 2.1 Background

Weight space learning methods such as SANE (Sequential Autoencoder for Neural Embeddings, Andreis et al., ICML 2024) represent neural network weights as sequences of tokens with sequential positional encodings. Cross-architecture transfer is hindered because positional encodings are architecture-specific.

Orbit-PE (orbit-based positional encodings derived from the input/output channel permutation group) is a candidate replacement that could be architecture-agnostic. Before implementing orbit-PE in SANE (planned in H-M1 through H-M3), we must verify two foundational properties:
1. **Permutation invariance:** Applying channel permutations to checkpoints does not change model behavior (|Δacc| < 0.1%)
2. **Orbit-PE computability:** Orbit-PE encoding vectors can be computed for all linear operator types without architecture-specific code

### 2.2 Problem Scope

- **In scope:** Loading checkpoints, applying permutations, re-evaluating, measuring |Δacc|, computing orbit-PE membership vectors
- **Out of scope:** Training any model, modifying SANE architecture, cross-architecture prediction

---

## 3. Goals and Success Criteria

### 3.1 Primary Goals

| Goal | Metric | Target |
|------|--------|--------|
| Permutation invariance (CNN) | Mean \|Δacc\| across 500 CNNs × 10 permutations | < 0.001 (0.1%) |
| Permutation invariance (Transformer) | Mean \|Δacc\| across 500 Transformers × 10 permutations | < 0.001 (0.1%) |
| Orbit-PE computability | Fraction of layer types with successful orbit-PE | 1.0 (100%) |

### 3.2 Gate Condition (MUST_WORK)

**PASS:** Mean |Δacc| < 0.001 for BOTH CNN Zoo AND Transformer Zoo, AND orbit-PE success rate = 1.0

**FAIL:** Any mean |Δacc| ≥ 0.001 for either architecture family, OR orbit-PE fails for any layer type → investigate which symmetry is violated

### 3.3 Expected Outcome

Permutation symmetry in MLP/CNN is proven exact by NFN theory (Zhou et al., NeurIPS 2023). Transformer head permutation is proven by Transformer-NFN (Tran et al., ICLR 2025). Expected mean |Δacc| ≈ 0.000% (numerical precision only).

---

## 4. Data Specification

### 4.1 Dataset 1: Small CNN Zoo

| Property | Value |
|----------|-------|
| **Name** | Small CNN Zoo (NFN benchmark) |
| **Source** | AllanYangZhou/nfn (NeurIPS 2023) |
| **Type** | Real, established benchmark — NOT synthetic |
| **Size** | ~50,000 checkpoints total; sample ~1,000; H-E1 uses 500 |
| **Architecture** | Small CNNs (3–5 layers), CIFAR-10/SVHN/MNIST tasks |
| **Labels** | Validation accuracy (pre-computed, ground truth) |
| **Download** | `cd data/ && bash download_cifar10_cnn_sample.sh` (HSG-AIML/MultiZoo-SANE) |
| **Preprocessing** | Load state_dict → apply permutation → re-evaluate → compute \|Δacc\| |

**Sampling for H-E1:** 500 checkpoints sampled uniformly from the zoo. Seed=42 for reproducibility.

### 4.2 Dataset 2: Small Transformer Zoo

| Property | Value |
|----------|-------|
| **Name** | Small Transformer Zoo (Transformer-NFN benchmark) |
| **Source** | MathematicalAI-NUS/Transformer-NFN (ICLR 2025); HuggingFace: anonymized-acamedia/Small-Transformer-Zoo |
| **Type** | Real, established benchmark — NOT synthetic |
| **Size** | 125,000 total checkpoints (MNIST-Transformers + AG-News-Transformers) |
| **Architecture** | Small 2–4 layer Transformers, encoder-only |
| **Tasks** | MNIST classification, AG-News text classification |
| **Labels** | Validation accuracy per checkpoint |
| **Download** | HuggingFace wget (MNIST-Transformers.zip + AG-News-Transformers.zip) |
| **Preprocessing** | Load checkpoint → apply head-permutation (S_h group) → re-evaluate → compute \|Δacc\| |

**Sampling for H-E1:** 500 checkpoints (250 MNIST + 250 AG-News). Seed=42.

### 4.3 Data Download Requirements

Both datasets require **manual download** before experiment execution.

**CNN Zoo Download:**
```bash
# Clone or navigate to HSG-AIML/MultiZoo-SANE
cd data/
bash download_cifar10_cnn_sample.sh
python3 preprocess_dataset_cnn_cifar10_sample.py
```

**Transformer Zoo Download:**
```bash
wget "https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/AG-News-Transformers.zip?download=true" -O AG-News-Transformers.zip
wget "https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/MNIST-Transformers.zip?download=true" -O MNIST-Transformers.zip
unzip MNIST-Transformers.zip -d data/
unzip AG-News-Transformers.zip -d data/
```

---

## 5. Functional Requirements

### FR-1: Data Loading

**FR-1.1 CNN Zoo Loader**
- Load 500 CNN checkpoints from the NFN Small CNN Zoo sample
- Each checkpoint: state_dict with known validation accuracy
- Use `state_dict_to_tensors` from `nfn.common` for weight extraction
- Validate: checkpoint has weights for all conv/linear layers

**FR-1.2 Transformer Zoo Loader**
- Load 500 Transformer checkpoints (250 MNIST + 250 AG-News)
- Each checkpoint: model weights + associated validation set reference
- Support loading from HuggingFace format (zip archives)
- Validate: MultiheadAttention layers present (in_proj_weight or q_proj/k_proj/v_proj)

### FR-2: Permutation Application

**FR-2.1 CNN Permutation**
- Implement `apply_canonical_channel_permutation(state_dict, perm_seed)` for CNN checkpoints
- Group action: G = S_{c_in} × S_{c_out} for each linear operator
- For Conv2d (c_out, c_in, H, W): permute output channels (π_out) then input channels (π_in)
- For Linear (c_out, c_in): permute output rows (π_out) then input columns (π_in)
- Propagate: bias permuted by π_out consistently
- Handle BatchNorm: permute running_mean, running_var, weight, bias by π_out of preceding layer
- Apply 10 different permutations per checkpoint (seeds 0–9)

**FR-2.2 Transformer Permutation**
- Implement `apply_transformer_head_permutation(state_dict, perm_seed)` for Transformer checkpoints
- Group action: S_h (head permutation, ICLR 2025 Transformer-NFN theory)
- For MultiheadAttention in_proj_weight (3×d_model, d_model): permute attention heads
- Handle separate Q, K, V projections if present
- Handle LayerNorm: permute γ, β by the same channel permutation as preceding layer
- Apply 10 different permutations per checkpoint (seeds 0–9)

### FR-3: Model Re-evaluation

**FR-3.1 CNN Accuracy Evaluation**
- Load original checkpoint → evaluate on validation set → record `acc_before`
- Load permuted checkpoint → evaluate on validation set → record `acc_after`
- Compute `delta_acc = abs(acc_before - acc_after)`
- Use eval mode (model.eval(), torch.no_grad())
- Batch size 256 for evaluation

**FR-3.2 Transformer Accuracy Evaluation**
- Same protocol as FR-3.1 for Transformer checkpoints
- Use the task-specific validation set (MNIST or AG-News)

### FR-4: Orbit-PE Computability Check

**FR-4.1 Orbit-PE Vector Computation**
- Implement `compute_orbit_pe(state_dict, layer_types)` that computes orbit membership vectors
- Must support: Linear, Conv2d, MultiheadAttention — without architecture-specific branching
- Orbit-PE encodes: (layer_index, orbit_size, position_in_orbit) for each weight token
- Log orbit vector shape per layer type
- Return: orbit_vectors dict, success_flags dict

**FR-4.2 Success Reporting**
- Report orbit-PE success for each layer type individually
- success_rate = num_successful_layer_types / total_layer_types
- PASS condition: success_rate = 1.0 (all layer types computable)
- Log mechanism activation: `"Orbit-PE computed for {layer_name} ({layer_type}): shape {orbit_vec.shape}"`

### FR-5: Metrics and Logging

**FR-5.1 Primary Metrics**
- `mean_delta_acc_cnn` = mean(|Δacc|) over 500 CNNs × 10 permutations = 5000 measurements
- `std_delta_acc_cnn` = std of above
- `max_delta_acc_cnn` = max of above
- `mean_delta_acc_transformer` = mean(|Δacc|) over 500 Transformers × 10 permutations = 5000 measurements
- `orbit_pe_success_rate` = fraction of layer types successfully encoded

**FR-5.2 Logging**
- Log per-permutation: `"Permutation {seed} applied to checkpoint {j}: Δacc = {val:.6f}"`
- Log orbit-PE per layer: `"Orbit-PE computed for {layer}: shape {shape}"`
- Log failures: if Δacc > threshold, log checkpoint ID, permutation, layers causing deviation

### FR-6: Visualization

**FR-6.1 Required Figure (Mandatory)**
- Bar chart comparing mean |Δacc| for CNN Zoo vs Transformer Zoo, with 0.1% threshold line
- Save to: `h-e1/figures/gate_metrics_comparison.png`

**FR-6.2 Distribution Plot**
- Histogram of |Δacc| across all 5000 CNN + 5000 Transformer measurements (log-scale x-axis)
- Save to: `h-e1/figures/delta_acc_distribution.png`

**FR-6.3 Layer-type Orbit-PE Table**
- Table/figure showing orbit-PE computability per layer type (Linear, Conv2d, MultiheadAttention)
- Save to: `h-e1/figures/orbit_pe_success_table.png`

**FR-6.4 Per-seed Stability Plot**
- Box plot of |Δacc| across 10 permutation seeds for CNN and Transformer
- Save to: `h-e1/figures/per_seed_stability.png`

### FR-7: Results Reporting

**FR-7.1 Results File**
- Save `results.json` to `h-e1/` with all primary metrics
- Include: mean, std, max for both architecture families
- Include: orbit-PE success per layer type, overall success rate
- Include: gate pass/fail determination

**FR-7.2 MUST_WORK Gate Evaluation**
- Evaluate `mean_delta_acc_cnn < 0.001 AND mean_delta_acc_transformer < 0.001 AND orbit_pe_success_rate == 1.0`
- Print clear PASS/FAIL verdict

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Requirement | Value |
|-------------|-------|
| Max runtime | ≤ 2 hours for full experiment (500 CNNs + 500 Transformers × 10 permutations each) |
| GPU usage | Single GPU (CUDA_VISIBLE_DEVICES=<empty_gpu_id>) |
| Memory | ≤ 16GB GPU VRAM |

### 6.2 Reproducibility

- All random operations seeded (permutation seeds 0–9, sampling seed=42)
- Results identical across runs with same seeds
- Environment: `requirements.txt` pinned versions

### 6.3 Code Quality

- Single entry-point script: `run_experiment.py`
- Modular: separate files for data loading, permutation, evaluation, orbit-PE
- All figures auto-saved without manual intervention

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
tqdm>=4.65.0
nfn  # pip install nfn (AllanYangZhou/nfn)
transformers>=4.30.0  # for Transformer checkpoint loading
datasets>=2.12.0  # for HuggingFace dataset handling
pillow>=9.5.0
```

### 7.2 External Repositories (Reference)

| Repository | Purpose | URL |
|-----------|---------|-----|
| HSG-AIML/SANE | SANE tokenization reference | https://github.com/HSG-AIML/SANE |
| HSG-AIML/MultiZoo-SANE | CNN Zoo download scripts | https://github.com/HSG-AIML/MultiZoo-SANE |
| AllanYangZhou/nfn | `nfn` library, orbit primitives | https://github.com/AllanYangZhou/nfn |
| MathematicalAI-NUS/Transformer-NFN | Transformer Zoo, S_h group theory | https://github.com/MathematicalAI-NUS/Transformer-NFN |

---

## 8. Implementation Constraints

- **No training:** H-E1 is evaluation-only — no gradient computation, no optimizer
- **LIGHT tier:** Maximum 15 implementation tasks total
- **Single GPU:** Always set CUDA_VISIBLE_DEVICES before running
- **Batch norm handling:** BN running statistics must be permuted consistently (running_mean, running_var, weight, bias all permuted by π_out of the preceding layer)
- **LayerNorm handling:** LayerNorm weight/bias permuted by the channel permutation of the input

---

## 9. Acceptance Criteria

| Criteria | Definition |
|----------|------------|
| Code runs without error | Full pipeline (500 CNN + 500 Transformer checkpoints) completes |
| Gate metrics computed | mean_delta_acc_cnn and mean_delta_acc_transformer reported |
| Orbit-PE checked | success_rate reported per layer type |
| Figures generated | All 4 figures saved to h-e1/figures/ |
| Results saved | results.json with all metrics |
| Gate evaluated | Clear PASS/FAIL verdict printed |

---

## 10. Out of Scope

- SANE model training (H-M3)
- Orbit-PE integration into SANE tokenizer (H-M1)
- Cross-architecture prediction tasks (H-M3, H-C1)
- Fine-tuning or dataset augmentation

---

*Generated by Phase 3 PRD Workflow | Hypothesis: H-E1 | EXISTENCE Type | LIGHT Tier*
*Phase 2C Source: 02c_experiment_brief.md | Date: 2026-05-21*
