---
name: "PRD: h-e1 Three-Tier Contamination Detection System"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-11
phase: Phase 3 - Implementation Planning
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
stepsCompleted: [initialization, requirements, dependencies, success-criteria]
---

# Product Requirements Document: h-e1

## Executive Summary

Implement a three-tier contamination detection system to validate that multi-layer detection achieves ≥80% combined detection power at <5% false positive rate for EAL-style paraphrased benchmark contamination (1-5% injection rates). This is the foundation hypothesis (EXISTENCE type) that validates the core detection architecture before mechanism-specific hypotheses.

**Success Gate:** MUST_WORK - Combined detection power ≥80% at <5% FPR

**Implementation Scale:** LIGHT tier (15 tasks max, 4-8 Epic tasks) - PoC validation focused on existence proof, not mechanism optimization.

## Problem Statement

Current contamination detection methods (MIA, semantic similarity) achieve near-random performance (AUC≈50%, TPR<2%) under EAL-style paraphrasing attacks. This hypothesis validates whether a multi-tier detection architecture can overcome this limitation by detecting contamination through learning-trajectory signatures rather than instance-level similarity.

## Functional Requirements

### FR-1: EAL Contamination Protocol Implementation

**Priority:** P0 (Critical)  
**Description:** Implement EAL-style paraphrasing contamination protocol for controlled experiments

**Requirements:**
- Load GSM8K test set (1,319 samples)
- Implement GPT-4 paraphrasing using eth-sri/malicious-contamination prompts
- Create three contamination conditions:
  * Clean baseline: 0% contamination (background MATH data only)
  * Low contamination: 1% injection rate
  * High contamination: 5% injection rate
- N=20 training runs per condition (60 total runs)
- Mix paraphrased GSM8K with background MATH dataset

**Dependencies:** Dataset access (GSM8K, MATH), GPT-4 API or cached paraphrases

**Acceptance Criteria:**
- Three contaminated datasets generated successfully
- Paraphrased samples validated (semantic preservation, solution correctness)
- Training data balanced (contaminated + background mix)

### FR-2: Model Training Infrastructure

**Priority:** P0 (Critical)  
**Description:** Finetune Llama-2-7B on contaminated/clean data mixes

**Requirements:**
- Base model: Llama-2-7B (meta-llama/Llama-2-7b-hf)
- Training configuration:
  * Optimizer: AdamW (lr=2e-5, weight_decay=0.01)
  * Batch size: 64 (per-device=4, grad_accum=16)
  * Epochs: ≤3
  * Warmup: 10% of steps
  * FP16 precision
  * Max sequence length: 512 tokens
- Seed control: Fixed seeds 0-19 for reproducibility
- Checkpoint saving: Per-epoch saves

**Dependencies:** GPU access (single GPU per run), HuggingFace transformers

**Acceptance Criteria:**
- 60 models trained successfully (20 per condition)
- Training logs saved (loss trajectories, probe metrics)
- GSM8K accuracy gains validated (contaminated > clean)

### FR-3: Tier 1 - Data-Layer Filters

**Priority:** P0 (Critical)  
**Description:** Implement temporal isolation + LSH-based structural fingerprinting

**Requirements:**
- Temporal isolation check:
  * Compare sample timestamps against GSM8K release date (2021-11-01)
  * Flag samples created after benchmark release
- LSH fingerprinting:
  * MinHash with 128 permutations
  * LSH index with 20 bands, 5 rows per band
  * Tokenize samples and compute MinHash signatures
  * Query LSH index for near-duplicate detection

**Dependencies:** `datasketch` library for LSH, sample metadata with timestamps

**Acceptance Criteria:**
- Temporal filter detects post-release samples
- LSH detects exact/near-duplicate matches
- False positive rate measured on clean runs
- Detector integrated into combined detection pipeline

### FR-4: Tier 2 - Task Signature Graph (TSG) Probes

**Priority:** P0 (Critical)  
**Description:** Implement probe-based differential alignment detection

**Requirements:**
- Probe generation:
  * Extract 1000 invariant probes (TSG-aligned with benchmark)
  * Generate 1000 neighbor probes (similar but off-manifold)
  * Generate 1000 broken-control probes (constraint violations)
- Probe loss tracking:
  * Evaluate probes at training checkpoints
  * Compute per-probe loss trajectories
- Differential alignment metric:
  * Δ = (ΔL_invariant - ΔL_neighbor)
  * Compare against clean baseline distribution
  * Threshold: Δ > 2σ of clean runs

**Dependencies:** Probe generation logic (TSG extraction from math problems), baseline statistics from clean runs

**Acceptance Criteria:**
- 3000 probes generated from GSM8K
- Probe losses tracked across training
- Differential alignment Δ computed correctly
- Detection threshold calibrated on clean runs (2σ)

### FR-5: Tier 3 - Geometric Trajectory Metrics

**Priority:** P0 (Critical)  
**Description:** Implement four geometric detection metrics

**Requirements:**
- **Metric 1:** Gradient subspace overlap
  * Compute gradient on benchmark data
  * Compute parameter update direction
  * Measure cosine similarity
  * Threshold: >0.10
  
- **Metric 2:** Hessian spectral concentration
  * Use pytorch-hessian-eigenthings library
  * Compute top-10 eigenvalues via Lanczos
  * Measure eigenvalue concentration ratio
  * Threshold: >1.5
  
- **Metric 3:** CKA representational alignment
  * Extract model activations on clean vs benchmark data
  * Compute centered kernel alignment
  * Threshold: >0.15
  
- **Metric 4:** Information efficiency Z-score
  * Accuracy gain per token seen
  * Normalize by clean baseline mean/std
  * Threshold: >2.5

- **Detection logic:** ≥2 of 4 metrics exceed thresholds → detected

**Dependencies:** `pytorch-hessian-eigenthings`, CKA implementation, clean baseline statistics

**Acceptance Criteria:**
- All 4 metrics implemented correctly
- Thresholds calibrated on clean runs (<5% FPR)
- ≥2/4 threshold logic enforced
- Detector integrated into combined pipeline

### FR-6: Combined Detection System

**Priority:** P0 (Critical)  
**Description:** Integrate three tiers with OR logic

**Requirements:**
- Detection logic: Tier1 OR Tier2 OR Tier3 → contamination detected
- Per-tier detection rates tracked separately
- Combined detection power computed
- False positive rate measured on clean runs (must be <5%)

**Dependencies:** All three tiers implemented (FR-3, FR-4, FR-5)

**Acceptance Criteria:**
- OR logic correctly implemented
- Per-tier and combined metrics reported
- Detection power ≥80% for 5% contamination
- FPR <5% on clean runs

### FR-7: Evaluation and Metrics

**Priority:** P0 (Critical)  
**Description:** Comprehensive evaluation across all conditions

**Requirements:**
- **Primary Metrics:**
  * Combined detection power (contaminated runs detected / total contaminated)
  * False positive rate (clean runs flagged / total clean)
  * Per-tier detection rates
  
- **Secondary Metrics:**
  * GSM8K accuracy gain (validate contamination effectiveness)
  * Per-metric distributions for Tier 3
  * Differential alignment Δ distributions for Tier 2
  
- **Statistical Analysis:**
  * Aggregate over N=20 runs per condition
  * Compute means and 95% confidence intervals
  * Compare 1% vs 5% contamination rates

**Dependencies:** All detectors implemented, 60 training runs completed

**Acceptance Criteria:**
- All metrics computed correctly
- Results aggregated across replicates
- Statistical significance reported
- Visualizations generated

### FR-8: Visualization Generation

**Priority:** P1 (High)  
**Description:** Generate figures for results analysis

**Requirements:**
- **Mandatory Figure:** Gate metrics comparison (detection power vs 80% target)
- **Additional Figures:**
  * Per-tier detection heatmap (3 tiers × 3 conditions)
  * ROC curve (TPR vs FPR)
  * GSM8K accuracy vs contamination rate
  * Geometric metrics distributions (violin plots)
  * Differential alignment Δ over training time

**Dependencies:** Evaluation results (FR-7)

**Acceptance Criteria:**
- All figures generated and saved to `h-e1/figures/`
- Figures included in validation report
- Gate metric visualization clearly shows pass/fail status

### FR-9: Baseline Methods Comparison (Optional)

**Priority:** P2 (Nice-to-have)  
**Description:** Compare against MIA baseline for context

**Requirements:**
- Implement SPV-MIA from tsinghua-fib-lab/ANeurIPS2024_SPV-MIA
- Apply to same 60 training runs
- Report MIA detection AUC alongside three-tier results
- Demonstrates superiority of geometric detection

**Dependencies:** SPV-MIA implementation, reference model training

**Acceptance Criteria:**
- MIA detection rates reported
- Comparison shows geometric detection > MIA
- Results contextualized in validation report

## Non-Functional Requirements

### NFR-1: Reproducibility

- All random seeds fixed and documented
- Exact library versions specified (requirements.txt)
- Training configurations saved as JSON
- Results reproducible across runs

### NFR-2: Computational Efficiency

- Single GPU training (not multi-GPU required)
- Training time: ~3-5 hours per run (7B model, ≤3 epochs)
- Total compute: ~60 runs × 4 hours = 10 GPU-days
- Hessian computation optimized via Lanczos (linear memory)

### NFR-3: Code Quality

- Modular architecture (separate tier implementations)
- Unit tests for metric computations
- Integration tests for combined detection
- Clear documentation for each component

### NFR-4: Experiment Tracking

- Log all hyperparameters, metrics, and results
- Save checkpoints for analysis
- Track per-tier and combined metrics
- Enable post-hoc analysis and debugging

## Data Requirements

### Primary Dataset: GSM8K

- **Source:** HuggingFace `datasets` library
- **Identifier:** `gsm8k` (main split)
- **Splits:** Train (7,473), Test (1,319)
- **Format:** Question-answer pairs with step-by-step solutions
- **Usage:** Test set for contamination injection

### Background Dataset: MATH

- **Source:** HuggingFace `datasets` library
- **Identifier:** `hendrycks/competition_math`
- **Size:** ~12K training samples
- **Usage:** Clean background data for finetuning mix

### Paraphrased Data

- **Generation:** GPT-4 paraphrasing with eth-sri prompts
- **Validation:** Semantic preservation, solution correctness
- **Storage:** Cache paraphrases to avoid repeated API calls

## Model Requirements

### Base Model: Llama-2-7B

- **Source:** HuggingFace model hub
- **Identifier:** `meta-llama/Llama-2-7b-hf`
- **Parameters:** 7 billion
- **Rationale:** Standard scale for controlled experiments, gradient/Hessian computation feasible

## Dependencies and Integrations

### External Libraries

- `transformers` (HuggingFace) - Model loading and training
- `datasets` (HuggingFace) - Dataset loading
- `datasketch` - LSH/MinHash for Tier 1
- `pytorch-hessian-eigenthings` - Efficient Hessian computation for Tier 3
- `torch` - PyTorch framework
- `scikit-learn` - Evaluation metrics
- `matplotlib`/`seaborn` - Visualization

### External Resources

- GPT-4 API (or cached paraphrases from eth-sri repository)
- Single GPU with ≥24GB VRAM (for 7B model FP16 training)

### Reference Implementations

1. **EAL Attack:** eth-sri/malicious-contamination (paraphrasing prompts)
2. **DICE Detector:** THU-KEG/DICE (internal state detection reference)
3. **Hessian Computation:** noahgolmant/pytorch-hessian-eigenthings
4. **MIA Baseline:** tsinghua-fib-lab/ANeurIPS2024_SPV-MIA (optional comparison)

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)

✅ **Combined detection power ≥80% for 5% contamination**  
✅ **False positive rate <5% on clean runs**  
✅ **At least 2 of 3 tiers show >0% detection power** (validates complementary architecture)

### Secondary Success Criteria (Quality Validation)

- GSM8K accuracy gains validate contamination effectiveness (≥10% gain expected)
- All 60 training runs complete successfully
- Statistical significance demonstrated (p<0.05)
- Visualizations clearly show gate pass/fail status

### PoC Pass Conditions (Minimal)

- Code runs without error (all 60 runs complete)
- Combined detection power > 0% (at least one tier detects)
- Direction validated: detection_power_5% > detection_power_1% > detection_power_0%

## Out of Scope

- **Not included:** Optimization of individual tier performance (reserved for H-M1, H-M2, H-M3)
- **Not included:** Adaptive adversary evaluation (reserved for H-M4)
- **Not included:** Production deployment considerations
- **Not included:** Real-time detection capabilities

## Timeline and Milestones

This is an EXISTENCE hypothesis (LIGHT tier) with task budget ≤15 tasks, 4-8 Epic-level tasks.

**Estimated Phases:**
1. Data Preparation (contamination generation, dataset loading)
2. Training Infrastructure (model training loop, checkpoint management)
3. Tier 1 Implementation (data-layer filters)
4. Tier 2 Implementation (TSG probes)
5. Tier 3 Implementation (geometric metrics)
6. Evaluation and Visualization
7. Validation Report Generation

**Note:** No specific time estimates per BMAD v6 principles - focus on WHAT, not WHEN.

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| GPT-4 API costs for paraphrasing | High | Use cached paraphrases from eth-sri repository |
| Hessian computation OOM errors | High | Use pytorch-hessian-eigenthings (Lanczos, linear memory) |
| TSG probe generation complexity | Medium | Start with simple extraction, refine if needed |
| Training time exceeds budget | Medium | Use single GPU, FP16, small batch size |
| Clean runs flagged (high FPR) | Critical | Calibrate thresholds on clean baseline first |

## Appendix: Reference Implementations

See Phase 2C Experiment Brief (02c_experiment_brief.md) Section: "Appendix: Reference Implementations" for detailed links to:
- eth-sri/malicious-contamination (EAL attack)
- THU-KEG/DICE (detection approach)
- noahgolmant/pytorch-hessian-eigenthings (Hessian computation)
- tsinghua-fib-lab/ANeurIPS2024_SPV-MIA (MIA baseline)

---

*Generated by Phase 3 Step 2 | Source: Phase 2C Experiment Brief | Hypothesis: h-e1 (EXISTENCE) | Gate: MUST_WORK*
