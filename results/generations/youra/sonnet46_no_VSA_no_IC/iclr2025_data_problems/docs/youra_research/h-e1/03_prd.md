---
stepsCompleted: ["Executive Summary", "Problem Statement", "Functional Requirements", "Non-Functional Requirements", "Success Criteria", "Data Specification", "Dependencies"]
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated_at: "2026-08-20"
phase: "Phase 3"
---

# Product Requirements Document: h-e1

## 1. Executive Summary

This PRD specifies the implementation of a domain exposure trajectory computation pipeline for the Pythia model family. The goal is to verify **h-e1**: that cumulative domain exposure fractions computed from official Pythia index maps are non-uniform across The Pile's 22 domains (std > 0.001 for ≥10 domains in ≥8 of 16 model sizes). This is an EXISTENCE hypothesis — it checks whether measurable within-family variation exists in training data composition, which is a prerequisite for using domain exposure as a covariate in downstream panel regressions (h-m1/h-m2/h-m3).

**Scope:** Read-only data analysis pipeline. No model training, no gradient descent. Pure numpy/scipy statistical analysis over official EleutherAI index map files.

---

## 2. Problem Statement

### 2.1 Research Question

Does the Pythia model family exhibit non-uniform domain exposure trajectories across training checkpoints? Specifically, does cumulative domain exposure fraction vary meaningfully (std > 0.001) for ≥10 of 22 The Pile domains, measured across 154 training checkpoints × 16 model sizes?

### 2.2 Hypothesis Statement

Under the Pythia model family trained on The Pile, domain exposure trajectories computed from exact dataloaders at 154 training checkpoints × 16 model sizes are non-uniform across domains (std > 0.001 for ≥10 of 22 domains), providing measurable within-family variation in cumulative domain exposure fractions that can serve as time-varying covariates in a panel regression.

### 2.3 Gate Condition

**MUST_WORK:** ≥10 of 22 The Pile domains must show std(cumulative_exposure_fraction) > 0.001 across 154 checkpoints in at least 8 of 16 Pythia model sizes.

**Failure consequence:** Cross-family fallback design activates; h-m1/h-m2/h-m3 are blocked.

---

## 3. Functional Requirements

### FR-1: Index Map Data Pipeline

**FR-1.1: Download Pythia Index Maps**
- Download `EleutherAI/pythia_deduped_pile_idxmaps` via `git lfs clone` from HuggingFace
- Unshard with `python utils/unshard_memmap.py --input_file ./pile_0.87_deduped_text_document-00000-of-00082.bin --num_shards 83`
- Verify files: `*_doc_idx.npy`, `*_sample_idx.npy`, `*_shuffle_idx.npy`
- Storage: ~32 GB

**FR-1.2: Load MMapIndexedDataset**
- Use `MMapIndexedDataset` from `EleutherAI/pythia/utils/mmap_dataset.py`
- Access `dataset.doc_idx` for document boundary indices
- Support all 154 checkpoint steps per model size

**FR-1.3: Build Domain Lookup Table**
- Load `EleutherAI/pile` HuggingFace dataset (streaming mode)
- Build lookup: `{global_doc_idx: pile_set_name}` from `meta.pile_set_name` field
- One-time preprocessing; cache to disk (pickle/numpy)
- 22 domains: Pile-CC, PubMed Central, Books3, OpenWebText2, ArXiv, GitHub, FreeLaw, StackExchange, USPTO Backgrounds, PubMed Abstracts, Gutenberg (PG-19), OpenSubtitles, Wikipedia (en), DM Mathematics, Ubuntu IRC, BookCorpus2, EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter, Enron Emails

### FR-2: Checkpoint Step Enumeration

**FR-2.1: Define 154 Checkpoint Steps**
- Log-spaced early: step0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
- Linear: step1000, step2000, ..., step143000 (143 steps)
- Total: 154 checkpoints per model size

**FR-2.2: Token Index Mapping**
- Tokens per step: 2,097,152 (Pythia batch size × sequence length)
- Sequence length: 2,049 tokens
- `target_sample = (step * tokens_per_step) // sequence_length`

### FR-3: Cumulative Domain Exposure Computation

**FR-3.1: Core Trajectory Function**
- Input: `MMapIndexedDataset`, `doc_to_domain` lookup, `checkpoint_steps` list
- For each checkpoint: accumulate domain counts incrementally from last checkpoint
- Normalize: `cumulative_fraction[d, t] = count[d] / total_count` at checkpoint t
- Output: `trajectories` array, shape `(22, 154)` per model size

**FR-3.2: Multi-Model Processing**
- Process all 16 model sizes: 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B + deduped variants
- Each model size shares the same index map file (index maps are model-size-independent for Pythia)
- Save `trajectories_{model_size}.npy` for each model size

**FR-3.3: Representative PoC Subset**
- Fast validation on 3 sizes: 70M, 1B, 6.9B
- Sufficient to gate-check before full 16-size run

### FR-4: Statistical Analysis

**FR-4.1: Variance Computation**
- For each domain d: `std_d = np.std(trajectories[d, :])` across 154 checkpoints
- Count: `n_passing = np.sum(stds > 0.001)`
- Gate check: `gate_passed = (n_passing >= 10)`
- Per-model-size reporting

**FR-4.2: Spearman Correlation**
- For each pair of model sizes: `spearmanr(stds_A, stds_B)` over 22 domain-std values
- Expected: ρ > 0.7 if domain variance ordering is consistent across scales
- Report 16×16 correlation matrix

**FR-4.3: Logging**
- Per-checkpoint log: `"Checkpoint step{N}: domain_counts={...}, total_tokens={...}"`
- Shape assertion: `trajectories.shape == (22, 154)` for each model size

### FR-5: Ablation Variants

**FR-5.1: Deduped vs. Non-deduped Comparison**
- Run pipeline for both deduped and non-deduped Pythia variants (where available)
- Compare variance distributions

**FR-5.2: Threshold Sensitivity**
- Report n_passing at thresholds: 0.0001, 0.0005, 0.001, 0.005, 0.01
- If primary gate fails (< 10 domains at 0.001), document borderline behavior

### FR-6: Visualization

**FR-6.1: Gate Metrics Bar Chart (MANDATORY)**
- Per-domain std values as bar chart
- Horizontal threshold line at std = 0.001
- Bars colored: green (pass) / red (fail)
- Save: `h-e1/figures/gate_metrics.png`

**FR-6.2: Domain Exposure Trajectory Lines**
- Line plot: `cumulative_fraction[d, t]` vs checkpoint step
- Show top-5 and bottom-5 variance domains
- Save: `h-e1/figures/trajectories.png`

**FR-6.3: Variance Heatmap**
- 22 domains × 16 model sizes heatmap of std values
- Save: `h-e1/figures/variance_heatmap.png`

**FR-6.4: Spearman Correlation Matrix**
- 16×16 model-size pair correlation matrix
- Save: `h-e1/figures/spearman_matrix.png`

---

## 4. Data Specification

### 4.1 Primary Dataset: Pythia Index Maps

| Attribute | Value |
|-----------|-------|
| Name | EleutherAI/pythia_deduped_pile_idxmaps |
| Source | HuggingFace (LFS) |
| Access | `git lfs clone https://huggingface.co/datasets/EleutherAI/pythia_deduped_pile_idxmaps` |
| Size | ~32 GB |
| Format | Binary memmap + `.npy` index files |
| Download type | MANUAL (git LFS clone required) |
| Key files | `*_doc_idx.npy`, `*_sample_idx.npy`, `*_shuffle_idx.npy` |
| Preprocessing | Unshard: `python utils/unshard_memmap.py --num_shards 83` |

### 4.2 Secondary Dataset: The Pile Domain Labels

| Attribute | Value |
|-----------|-------|
| Name | EleutherAI/pile |
| Source | HuggingFace datasets |
| Access | `load_dataset("EleutherAI/pile", split="train", streaming=True)` |
| Domain field | `meta['pile_set_name']` |
| 22 Domains | Pile-CC, PubMed Central, Books3, OpenWebText2, ArXiv, GitHub, FreeLaw, StackExchange, USPTO Backgrounds, PubMed Abstracts, Gutenberg (PG-19), OpenSubtitles, Wikipedia (en), DM Mathematics, Ubuntu IRC, BookCorpus2, EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter, Enron Emails |
| Processing time | ~24h one-time to build doc→domain lookup |
| Download type | AUTO (HuggingFace streaming) |

### 4.3 Checkpoint Configuration

| Parameter | Value |
|-----------|-------|
| Total checkpoints | 154 per model size |
| Early log-spaced | step0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512 (11 steps) |
| Linear | step1000 to step143000, stride 1000 (143 steps) |
| Tokens per step | 2,097,152 |
| Sequence length | 2,049 tokens |

---

## 5. Non-Functional Requirements

### NFR-1: Correctness
- Index map reconstruction must match official Pythia training order exactly
- Domain lookup must cover all documents in index maps (unknown docs → "Unknown" label)
- `trajectories.shape == (22, 154)` enforced by assertion

### NFR-2: Performance
- Domain lookup table built once, cached to disk (`doc_to_domain.pkl`)
- Trajectory computation parallelizable across model sizes
- Representative subset (3 sizes) must complete in < 2h on CPU

### NFR-3: Reproducibility
- Seed: 1 (Pythia training order is deterministic given index maps)
- All random operations (none expected) must be seeded
- Results saved as `.npy` files for downstream use

### NFR-4: Storage
- Index maps: ~32 GB
- Domain lookup: ~few GB
- Trajectory outputs: ~22 × 154 × 16 × 8 bytes ≈ negligible
- Total budget: ~40 GB

---

## 6. Success Criteria

### 6.1 Primary Gate (MUST_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Domains with std > 0.001 | ≥10 of 22 | `n_passing = np.sum(stds > 0.001)` |
| Model sizes satisfying criterion | ≥8 of 16 | Count model sizes where `n_passing >= 10` |

### 6.2 Secondary Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Spearman ρ cross-scale consistency | > 0.7 | `spearmanr(stds_A, stds_B)` for any pair |
| Pipeline completes | No error | For ≥3 representative model sizes |
| Shape integrity | `(22, 154)` | `trajectories.shape` assertion per model |

### 6.3 PoC Pass Condition

1. Code runs without error for ≥3 model sizes (70M, 1B, 6.9B)
2. `n_domains_passing >= 10` in ≥2 of 3 representative sizes

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.24
scipy>=1.10
datasets>=2.14         # HuggingFace datasets (The Pile streaming)
matplotlib>=3.7
seaborn>=0.12
tqdm>=4.65
torch>=2.0             # Required by MMapIndexedDataset
pickle                 # stdlib — domain lookup caching
```

### 7.2 External Repositories

| Repository | Purpose | Access |
|-----------|---------|--------|
| EleutherAI/pythia | MMapIndexedDataset, unshard script, batch_viewer | `git clone https://github.com/EleutherAI/pythia` |
| EleutherAI/pythia_deduped_pile_idxmaps | Index map files (32 GB LFS) | `git lfs clone https://huggingface.co/datasets/EleutherAI/pythia_deduped_pile_idxmaps` |

### 7.3 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Storage | 40 GB | 60 GB |
| RAM | 16 GB | 32 GB |
| CPU | 4 cores | 8+ cores |
| GPU | Not required | Not required |

---

## 8. Out of Scope

- Model inference or weight loading (not needed for h-e1)
- Benchmark evaluation (MMLU, HellaSwag, ARC, WinoGrande) — required for h-m2/h-m3 only
- Cross-family analysis (only needed if h-e1 gate fails)
- Any neural network training

---

## 9. Implementation Notes

### 9.1 Critical Implementation Details

1. **Incremental accumulation**: Do NOT recount from step 0 at each checkpoint. Maintain running `cumulative_counts` and advance `step_ptr` between checkpoints.
2. **doc_idx mapping**: `dataset.doc_idx[sample_idx]` returns the global document index for sample `sample_idx`.
3. **Token boundary**: `target_sample = step * tokens_per_step // sequence_length`. Process samples `[step_ptr, target_sample)` for each checkpoint.
4. **Deduped vs non-deduped**: Both share the same `pythia_deduped_pile_idxmaps` dataset for the deduped family. Non-deduped uses separate index maps if available.

### 9.2 Fallback Strategy

If index map LFS download fails or `doc_idx` mapping is incomplete:
- Fallback: Direct JSONL parsing of `EleutherAI/pile` to reconstruct domain proportions from static Pile paper statistics (Gao et al., 2021)
- This provides coarser approximate domain fractions (not checkpoint-varying)
