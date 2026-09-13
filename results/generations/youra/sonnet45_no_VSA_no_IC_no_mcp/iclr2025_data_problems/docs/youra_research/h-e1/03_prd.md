# Product Requirements Document (PRD): h-e1 Implementation

**Date:** 2026-08-24
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Author:** Phase 3 Planning Agent

---

## Executive Summary

**Goal:** Validate that pre-training data curation filters (deduplication, perplexity-based outlier removal) transfer robustly to instruction fine-tuning with ≤1% performance delta compared to stage-tuned thresholds.

**Core Question:** Do low-level quality filters address universal data hygiene properties independent of training stage objectives?

**Success Metric:** `|acc_transferred - acc_stage_tuned| ≤ 1%` on MMLU and HellaSwag benchmarks.

---

## Requirements

### Functional Requirements

**FR-1: Data Curation Pipeline**
- **FR-1.1:** Implement MinHash LSH deduplication with configurable threshold (default 0.8)
- **FR-1.2:** Implement KenLM perplexity filtering with configurable cutoff (default 100)
- **FR-1.3:** Support three curation variants:
  - Baseline: No filtering (raw Alpaca-52k)
  - Transferred: C4 thresholds (dedup=0.8, perplexity=100)
  - Stage-Tuned: Thresholds optimized on Alpaca validation perplexity
- **FR-1.4:** Generate curation statistics (dataset size reduction, perplexity distribution)

**FR-2: Model Training**
- **FR-2.1:** Load LLaMA-2-7B base model from HuggingFace (`meta-llama/Llama-2-7b-hf`)
- **FR-2.2:** Fine-tune on curated Alpaca variants using:
  - Optimizer: AdamW (lr=2e-5, betas=(0.9, 0.999), weight_decay=0.01)
  - Batch size: 128 (micro-batch=4, gradient_accumulation=32)
  - Epochs: 3
  - Loss: Causal LM (cross-entropy on response tokens only)
- **FR-2.3:** Save checkpoints for each variant
- **FR-2.4:** Log training curves (validation perplexity per epoch)

**FR-3: Evaluation**
- **FR-3.1:** Evaluate fine-tuned models on MMLU (0-shot)
- **FR-3.2:** Evaluate fine-tuned models on HellaSwag (0-shot)
- **FR-3.3:** Compute performance delta: `|acc_transferred - acc_stage_tuned|`
- **FR-3.4:** Verify gate condition: delta ≤ 1%

**FR-4: Visualization**
- **FR-4.1:** Generate gate metrics comparison (bar chart: MMLU/HellaSwag across variants)
- **FR-4.2:** Generate curation statistics (dataset size reduction)
- **FR-4.3:** Generate perplexity distribution histograms
- **FR-4.4:** Generate training curves (validation perplexity over epochs)
- **FR-4.5:** Save all figures to `h-e1/figures/`

**FR-5: Threshold Tuning (Stage-Tuned Variant)**
- **FR-5.1:** Grid search deduplication threshold: [0.6, 0.7, 0.8, 0.9]
- **FR-5.2:** Grid search perplexity cutoff: [50, 75, 100, 150, 200]
- **FR-5.3:** Evaluate each combination on Alpaca validation perplexity (5% holdout)
- **FR-5.4:** Select thresholds minimizing validation loss

### Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed random seed: 42
- Deterministic operations (CUDA deterministic mode)
- Checkpoint saving with full configuration

**NFR-2: Resource Constraints**
- Target: Single A100 GPU (40GB VRAM)
- Estimated runtime: 6 GPU-hours (3 variants × 2 hours)
- Memory optimization: Gradient checkpointing if needed

**NFR-3: Code Quality**
- Type hints for all functions
- Docstrings for public APIs
- Error handling for HuggingFace downloads
- Logging (INFO level) for pipeline stages

**NFR-4: Data Management**
- Cache downloaded models/datasets in `~/.cache/huggingface/`
- Store intermediate results in `h-e1/results/`
- Store generated figures in `h-e1/figures/`

---

## User Stories

**US-1:** As a researcher, I want to compare three curation strategies so I can measure filter transferability.

**US-2:** As a researcher, I want to see MMLU/HellaSwag accuracy for each variant so I can verify the gate condition.

**US-3:** As a researcher, I want visualizations of curation effects so I can understand dataset quality changes.

**US-4:** As a researcher, I want reproducible results so I can validate the hypothesis robustly.

---

## Technical Constraints

**TC-1: Hardware**
- GPU: NVIDIA A100 (40GB VRAM) or equivalent
- RAM: 64GB minimum (for LSH index construction)
- Storage: 200GB for models, datasets, checkpoints

**TC-2: Software Dependencies**
- Python 3.10+
- PyTorch 2.0+
- Transformers 4.30+
- Datasets 2.12+
- datasketch 1.6+ (MinHash LSH)
- kenlm 0.2+ (perplexity filtering)
- lm-evaluation-harness 0.4+ (MMLU/HellaSwag)

**TC-3: External Resources**
- HuggingFace Hub access (model/dataset downloads)
- KenLM English language model (`en.arpa.bin`)

---

## Acceptance Criteria

**AC-1:** Code executes without errors on specified hardware.

**AC-2:** Three dataset variants generated with correct filtering logic:
- Baseline: 52,000 samples (no reduction)
- Transferred: ≥40,000 samples (dedup + perplexity filtering)
- Stage-Tuned: Varies based on tuned thresholds

**AC-3:** Three fine-tuned models produced with validation perplexity decreasing over epochs.

**AC-4:** MMLU and HellaSwag evaluation results obtained for all three variants.

**AC-5:** Gate condition verified:
- If `|acc_transferred - acc_stage_tuned| ≤ 1%`: PASS
- Otherwise: FAIL (PIVOT required)

**AC-6:** All required figures generated and saved.

---

## Out of Scope

**OOS-1:** Full pre-training → fine-tuning → RLHF pipeline (PoC tests only pre-training → fine-tuning)

**OOS-2:** Multi-seed statistical validation (single seed=42 for PoC)

**OOS-3:** Alternative models beyond LLaMA-2-7B

**OOS-4:** Curation filters beyond deduplication and perplexity (e.g., toxicity, language ID)

**OOS-5:** Few-shot evaluation (0-shot only)

---

## Dependencies

**External Systems:**
- HuggingFace Hub (model/dataset downloads)
- KenLM language model (perplexity computation)

**Phase 2C Outputs:**
- `02c_experiment_brief.md` (experiment specification)
- `02b_context.md` (hypothesis context)

**Phase 3 Outputs (This PRD Enables):**
- Architecture document (`03_architecture.md`)
- Logic specification (`03_logic.md`)
- Configuration schema (`03_config.md`)
- Implementation task list (`03_tasks.yaml`)

---

## Risks and Mitigations

**Risk 1:** HuggingFace model download fails
- **Mitigation:** Retry logic with exponential backoff, fallback to cached version

**Risk 2:** KenLM language model unavailable
- **Mitigation:** Download from standard sources (kenlm.org), provide fallback URL

**Risk 3:** GPU OOM during fine-tuning
- **Mitigation:** Enable gradient checkpointing, reduce micro-batch size to 2

**Risk 4:** Stage-tuned threshold optimization too expensive
- **Mitigation:** Coarse grid search (5 dedup × 5 perplexity = 25 combinations), evaluate on 5% validation split only

**Risk 5:** MMLU/HellaSwag evaluation OOM
- **Mitigation:** Reduce batch size to 4, use CPU offloading if needed

---

## Success Metrics

**Primary:** Gate condition satisfaction (`|acc_transferred - acc_stage_tuned| ≤ 1%`)

**Secondary:**
- Curation benefit: `acc_transferred > acc_baseline + 2%`
- Code execution time: ≤8 GPU-hours (6 planned + 2 buffer)
- All visualizations generated successfully

---

## Timeline Estimate

**Phase 4 Implementation:**
- Curation pipeline: 2 hours
- Training infrastructure: 3 hours
- Evaluation integration: 2 hours
- Visualization: 1 hour
- Testing/debugging: 2 hours
- **Total:** 10 hours (development)

**Execution Runtime:**
- Threshold tuning (stage-tuned variant): 30 minutes
- Fine-tuning (3 variants): 6 hours
- Evaluation: 1 hour
- **Total:** 7.5 hours (runtime)

---

## Stakeholder Sign-off

**Research Lead:** Hypothesis owner (h-e1 verification)
**Phase 3 Agent:** PRD author
**Phase 4 Coder:** Implementation executor
**Phase 4 Validator:** Code verification and hypothesis evaluation

---

**Next Steps:**
1. Generate Architecture document (03_architecture.md)
2. Generate Logic specification (03_logic.md)
3. Generate Configuration schema (03_config.md)
4. Allocate implementation budget and generate task list (03_tasks.yaml)
