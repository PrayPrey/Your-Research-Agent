# Product Requirements Document: h-e1
# Semantic-Structural UQ Advantage Existence Verification

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Tier:** LIGHT (max 15 tasks)
**Date:** 2026-05-20
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Source:** h-e1/02c_experiment_brief.md

---

## 1. Executive Summary

This PRD defines implementation requirements for hypothesis h-e1: verifying that semantic-structural uncertainty quantification (UQ) methods (Semantic Entropy / SE, Kernel Language Entropy / KLE) achieve statistically higher AUROC for correctness prediction than token-probability (TP) baselines on Llama-3 base checkpoints at both 8B and 70B scales, evaluated on TriviaQA and NaturalQuestions benchmarks.

This is the **foundation EXISTENCE hypothesis** for the Epistemic Geometry Scaling Hypothesis (EGSH) pipeline. Its MUST_WORK gate must pass before H-M1–H-M4 can proceed.

**Scope:** Inference-only evaluation — no model training. Adapt official jlko/semantic_uncertainty pipeline for Llama-3 models. Compare 6 UQ methods across 2 model scales on 2 primary datasets.

---

## 2. Problem Statement

**Research Question:** Do semantic-structural UQ methods (SE, KLE) provide a measurable AUROC advantage over token-probability for correctness prediction in Llama-3 base models?

**Why this matters:** If SE/KLE do not outperform token-probability even at the base level, the EGSH (scale-dependent semantic advantage) cannot hold. This experiment establishes the prerequisite existence of the semantic-structural UQ advantage.

**Gate Condition (MUST_WORK):**
- SE AUROC > token-prob AUROC at **both 8B and 70B** scales
- 95% bootstrap CI excludes zero on **both TriviaQA AND NaturalQuestions** independently
- PASS → proceed to H-M1
- FAIL → reassess EGSH, route to Phase 2A

---

## 3. Goals and Non-Goals

### Goals
- G1: Implement SE computation pipeline adapted for Llama-3-8B and Llama-3-70B
- G2: Implement KLE (EigValLaplacian) via lm-polygraph or fallback
- G3: Compute token-probability baseline from greedy decode log-likelihood
- G4: Evaluate all UQ methods on full TriviaQA test set (17,944 questions) and NQ validation set (3,610 questions)
- G5: Compute AUROC with 95% bootstrap CI (1000 resamples)
- G6: Generate gate-check figures (AUROC bar chart, ROC curves, bootstrap distribution)
- G7: Verify SE mechanism activation (cluster count K < N)

### Non-Goals
- NG1: Model training or fine-tuning
- NG2: Layer-wise probe analysis (reserved for H-M1, H-M4)
- NG3: Instruction-tuned model comparison (Llama-3-70B-Instruct — H-M2 scope)
- NG4: TruthfulQA primary evaluation (scope boundary test only)
- NG5: Novel UQ method development

---

## 4. Data Specification

### 4.1 Primary Datasets

#### Dataset 1: TriviaQA rc.nocontext
| Field | Value |
|-------|-------|
| HuggingFace ID | `mandarjoshi/trivia_qa` |
| Config | `rc.nocontext` |
| Split | `test` |
| Size | 17,944 questions |
| Labels | Binary exact-match correctness |
| Preprocessing | 5-shot prompt format (Farquhar 2024); max_new_tokens=50 |
| Download | `load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="test")` |

#### Dataset 2: NaturalQuestions open-domain
| Field | Value |
|-------|-------|
| HuggingFace ID | `google-research-datasets/natural_questions` |
| Config | `default` |
| Split | `validation` |
| Size | 3,610 questions |
| Labels | Binary exact-match (short answer) |
| Preprocessing | Same few-shot format; extract short answer candidates |
| Download | `load_dataset("google-research-datasets/natural_questions", split="validation")` |

#### Dataset 3: TruthfulQA (Scope boundary — secondary)
| Field | Value |
|-------|-------|
| HuggingFace ID | `truthful_qa` |
| Config | `mc1_targets` |
| Split | `validation` |
| Size | 817 questions |
| Role | Scope boundary test; NOT primary evaluation for h-e1 |
| Download | `load_dataset("truthful_qa", "mc1_targets", split="validation")` |

### 4.2 Sample Sizes (Statistically Meaningful)
- TriviaQA: **full test set** (17,944) — no subsampling
- NaturalQuestions: **full validation set** (3,610) — no subsampling
- TruthfulQA: full validation set (817) — scope test only
- Minimum accepted: 500+ per dataset if GPU time is critically constrained

---

## 5. Functional Requirements

### FR1: Data Loading and Preprocessing
- FR1.1: Load TriviaQA rc.nocontext test split via HuggingFace datasets
- FR1.2: Load NaturalQuestions open-domain validation split
- FR1.3: Load TruthfulQA mc1_targets (secondary)
- FR1.4: Apply 5-shot few-shot prompt format consistent with Farquhar 2024
- FR1.5: Implement exact-match normalization for binary correctness labels

### FR2: Model Loading
- FR2.1: Load Llama-3-8B-Base (`meta-llama/Meta-Llama-3-8B`) in bfloat16
- FR2.2: Load Llama-3-70B-Base (`meta-llama/Meta-Llama-3-70B`) with 8-bit bitsandbytes quantization
- FR2.3: Load DeBERTa-large-mnli (`microsoft/deberta-large-mnli`) for SE entailment
- FR2.4: Preserve logit access for both 8-bit and bfloat16 loading
- FR2.5: Support `device_map="auto"` for multi-GPU distribution

### FR3: Answer Generation (Sampling)
- FR3.1: Generate N=10 samples per query at temperature=1.0, top_p=0.9, seed=42
- FR3.2: Generate 1 greedy decode per query for token-probability baseline
- FR3.3: Extract token-level log-likelihoods for all generated sequences
- FR3.4: Extract hidden states with `output_hidden_states=True` (for SEPs extension)
- FR3.5: Max new tokens: 50 (short-phrase generation)
- FR3.6: Batch processing: 16 queries/batch for 8B; 4–8 for 70B

### FR4: UQ Method Implementation
- FR4.1: **Token-Probability (TP)**: negative log-likelihood of greedy decode sequence
- FR4.2: **Semantic Entropy (SE)**: NLI-based semantic equivalence clustering (DeBERTa-large-mnli) + entropy over cluster distribution (jlko/semantic_uncertainty pipeline)
- FR4.3: **KLE (EigValLaplacian)**: via lm-polygraph `EigValLaplacian` estimator; verify Llama-3 support in Week 0 pilot
- FR4.4: **SelfCheckGPT-BERTScore**: BERTScore-based consistency across N=10 samples
- FR4.5: **SelfCheckGPT-NLI**: NLI-based consistency across N=10 samples
- FR4.6: **Semantic Entropy Probes (SEPs)**: linear probe on hidden states (optional, Week 0 pilot)
- FR4.7: Fallback: if KLE unavailable, SE alone satisfies primary gate; KLE is secondary

### FR5: AUROC Evaluation
- FR5.1: Compute AUROC for each UQ method using `sklearn.metrics.roc_auc_score`
- FR5.2: Compute 95% bootstrap CI with 1000 resamples for each AUROC
- FR5.3: Evaluate on TriviaQA and NQ independently
- FR5.4: Report AUROC ± CI for all methods at both 8B and 70B

### FR6: Gate Check
- FR6.1: Check SE AUROC > TP AUROC at 8B on TriviaQA (with CI excluding zero)
- FR6.2: Check SE AUROC > TP AUROC at 70B on TriviaQA (with CI excluding zero)
- FR6.3: Check SE AUROC > TP AUROC at 8B on NQ (with CI excluding zero)
- FR6.4: Check SE AUROC > TP AUROC at 70B on NQ (with CI excluding zero)
- FR6.5: PASS: all 4 checks pass → set gate.satisfied=true
- FR6.6: FAIL: any check fails → log failure mode; set gate.satisfied=false

### FR7: SE Mechanism Verification
- FR7.1: Log mean cluster count K per query batch (should be K < N=10)
- FR7.2: Assert entailment model loaded and returning non-degenerate predictions
- FR7.3: Raise warning if K == N (NLI clustering degenerate)

### FR8: Visualization
- FR8.1: Bar chart: AUROC per method × scale (8B/70B) × dataset (TriviaQA/NQ), error bars = 95% CI
  - Output: `h-e1/figures/auroc_comparison_bar.png`
- FR8.2: AUROC difference plot: `AUROC_SE - AUROC_TP` per scale per dataset with CI
  - Output: `h-e1/figures/auroc_difference.png`
- FR8.3: ROC curves: SE vs TP at 8B and 70B on TriviaQA (4 curves)
  - Output: `h-e1/figures/roc_curves.png`
- FR8.4: Bootstrap distribution: histogram of bootstrap AUROC for SE vs TP at each scale
  - Output: `h-e1/figures/bootstrap_distribution.png`

### FR9: Results Persistence
- FR9.1: Save raw AUROC results and CIs to `h-e1/results/auroc_results.json`
- FR9.2: Save per-query uncertainty scores to `h-e1/results/uncertainty_scores_{model}_{dataset}.pkl`
- FR9.3: Save correctness labels to `h-e1/results/correctness_labels_{dataset}.pkl`

---

## 6. Non-Functional Requirements

### NFR1: Hardware
- NFR1.1: Single GPU execution (CUDA_VISIBLE_DEVICES set before running)
- NFR1.2: Select GPU with lowest memory usage via `nvidia-smi`
- NFR1.3: Llama-3-8B: bfloat16 (~16GB VRAM)
- NFR1.4: Llama-3-70B: 8-bit quantization (~40GB VRAM; dual-GPU if needed)

### NFR2: Reproducibility
- NFR2.1: Fixed random seed=42 for all sampling
- NFR2.2: Single run (no multiple seeds for EXISTENCE PoC)
- NFR2.3: Log all hyperparameters and versions to `h-e1/results/run_config.json`

### NFR3: Performance
- NFR3.1: 70B inference: estimate time on 100-query pilot before full run
- NFR3.2: Checkpoint intermediate results every 500 queries to prevent data loss
- NFR3.3: N=5 fallback for 70B if GPU time severely constrained (verify stability first)

### NFR4: Code Quality
- NFR4.1: Modular Python scripts (data_loader.py, model_loader.py, uq_methods.py, evaluation.py, visualize.py)
- NFR4.2: Type hints on all public functions
- NFR4.3: Config via YAML dataclass (not hardcoded values)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.1.0
transformers>=4.40.0
datasets>=2.18.0
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
bitsandbytes>=0.41.0
accelerate>=0.27.0
matplotlib>=3.8.0
seaborn>=0.13.0
tqdm>=4.66.0
pyyaml>=6.0
lm-polygraph>=0.4.0  # for KLE/EigValLaplacian
```

### 7.2 External Reference Repositories
- **jlko/semantic_uncertainty** (MIT): Official Farquhar 2024 SE pipeline — primary SE reference
- **IINemo/lm-polygraph**: Unified UQ benchmark framework — KLE + unified evaluation
- **OATML/semantic-entropy-probes**: SEPs implementation reference
- **cvs-health/uqlm**: Fallback framework

### 7.3 HuggingFace Models
- `meta-llama/Meta-Llama-3-8B` — requires HF access token + Meta Llama license
- `meta-llama/Meta-Llama-3-70B` — requires HF access token + Meta Llama license
- `microsoft/deberta-large-mnli` — public, no license required

---

## 8. Success Criteria

### Primary Gate (MUST_WORK)
| Criterion | Threshold | Dataset |
|-----------|-----------|---------|
| AUROC_SE_8B > AUROC_TP_8B | CI excludes 0 | TriviaQA |
| AUROC_SE_70B > AUROC_TP_70B | CI excludes 0 | TriviaQA |
| AUROC_SE_8B > AUROC_TP_8B | CI excludes 0 | NQ |
| AUROC_SE_70B > AUROC_TP_70B | CI excludes 0 | NQ |

### Expected Performance (Literature)
- AUROC_SE on TriviaQA: ~0.72–0.79 (Farquhar 2024, Llama-2-70B)
- AUROC_TP on TriviaQA: ~0.67 (literature baseline)
- Expected SE advantage: 0.05–0.12 AUROC points

### Secondary Success
- KLE AUROC > TP AUROC at both scales (extends confidence in semantic-structural advantage)
- SE mechanism verified: mean cluster count K < N=10

### Failure Modes
| Mode | Detection | Action |
|------|-----------|--------|
| FAIL at 8B only | SE AUROC ≤ TP at 8B | Pivot: examine SE implementation, DeBERTa normalization |
| FAIL at both scales | SE AUROC ≤ TP at both | Abandon H-M*; route to Phase 2A |
| SE degenerate (K=N) | Mean clusters == N | Fix: DeBERTa loading issue |
| OOM on 70B | CUDA OOM | Reduce to N=5 or 4-bit quantization |

---

## 9. Experiment Configuration

```yaml
# h-e1 Experiment Configuration
hypothesis_id: "h-e1"
hypothesis_type: "EXISTENCE"

sampling:
  n_samples: 10
  temperature: 1.0
  top_p: 0.9
  seed: 42
  max_new_tokens: 50
  n_few_shot: 5

models:
  small:
    hf_id: "meta-llama/Meta-Llama-3-8B"
    dtype: "bfloat16"
    device_map: "auto"
  large:
    hf_id: "meta-llama/Meta-Llama-3-70B"
    quantization: "8bit"
    device_map: "auto"
  entailment:
    hf_id: "microsoft/deberta-large-mnli"

datasets:
  primary:
    - name: "trivia_qa"
      hf_id: "mandarjoshi/trivia_qa"
      config: "rc.nocontext"
      split: "test"
      size: 17944
    - name: "natural_questions"
      hf_id: "google-research-datasets/natural_questions"
      config: "default"
      split: "validation"
      size: 3610
  secondary:
    - name: "truthful_qa"
      hf_id: "truthful_qa"
      config: "mc1_targets"
      split: "validation"
      size: 817

evaluation:
  bootstrap_resamples: 1000
  alpha: 0.05
  batch_size_8b: 16
  batch_size_70b: 4
  checkpoint_every: 500

output:
  base_dir: "h-e1"
  figures_dir: "h-e1/figures"
  results_dir: "h-e1/results"
  code_dir: "h-e1/code"
```

---

## 10. Traceability

| Requirement | Source |
|-------------|--------|
| SE pipeline | jlko/semantic_uncertainty (Farquhar 2024, Nature) |
| KLE/EigValLaplacian | IINemo/lm-polygraph |
| N=10, temperature=1.0 | Farquhar et al. 2024 |
| Bootstrap CI (1000) | Phase 2B verification plan |
| TriviaQA rc.nocontext | Phase 2B hypothesis specification |
| NaturalQuestions | Phase 2B hypothesis specification |
| Expected AUROC values | Farquhar 2024 (0.72–0.79), literature |
| bitsandbytes 8-bit | HF bitsandbytes blog (Archon KB A.3) |

---

*Generated by Phase 3 PRD Workflow (inline execution)*
*Based on: h-e1/02c_experiment_brief.md*
*Next: Architecture Agent (step-03)*
