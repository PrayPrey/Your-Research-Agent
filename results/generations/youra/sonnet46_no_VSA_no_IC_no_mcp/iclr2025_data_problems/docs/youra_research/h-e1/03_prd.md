# Product Requirements Document: H-E1
# Deduplication Benchmark Signature — Existence Verification

**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Phase 2C Source:** docs/youra_research/h-e1/02c_experiment_brief.md
**Tier:** LIGHT (≤15 tasks)

---

## 1. Executive Summary

H-E1 tests whether Pythia dedup-Pile models produce statistically significantly different benchmark accuracy profiles compared to Pile models at token-count-matched checkpoints. This is a foundational EXISTENCE check: if no per-benchmark difference exists, the entire mechanistic hypothesis chain is falsified.

The experiment is an evaluation study (no training) using publicly available Pythia checkpoints from EleutherAI and the official lm-evaluation-harness tool. The deliverable is a statistical test result confirming or refuting that deduplication produces a detectable accuracy signature on at least one of {MMLU, HellaSwag, ARC-Challenge, WinoGrande}.

---

## 2. Problem Statement

**Research Question:** Does training corpus deduplication produce a statistically significant per-benchmark accuracy difference in Pythia models?

**Null Hypothesis (H0):** No benchmark shows a Bonferroni-corrected significant accuracy difference (p ≥ 0.0125) between Pile and dedup-Pile Pythia variants at token-count-matched checkpoints.

**Alternative Hypothesis (H1):** At least one benchmark shows a Bonferroni-corrected significant accuracy difference (p < 0.0125) at ≥2 model sizes.

**Failure Consequence:** If H0 is supported → STOP; entire downstream mechanistic hypothesis chain (H-M1 through H-M4) is abandoned.

---

## 3. Goals and Non-Goals

### Goals
- Identify matched Pile checkpoints for each model size (step closest to 207B tokens)
- Evaluate all 8 model variants (4 sizes × 2 corpus) on all 4 benchmarks using lm-eval
- Apply paired t-test with Bonferroni correction per benchmark (α = 0.0125)
- Produce figures: differential bar chart, scaling plot, paired scatter, p-value heatmap
- Generate a validation report confirming or refuting H1

### Non-Goals
- Training any model from scratch
- Modifying the lm-evaluation-harness codebase
- Analyzing training dynamics (intermediate checkpoints beyond token-count-matched step)
- Estimating contamination levels (H-M1 scope)

---

## 4. Functional Requirements

### FR-1: Checkpoint Resolution Module
- Compute token-count-matched Pile checkpoint step for each model size
- Formula: `step × 2,097,152 tokens/step ≈ target_tokens`
- Target: dedup-Pile step 143,000 ≈ 207B tokens → Pile step ≈ 99,000
- Verify via Pythia HuggingFace checkpoint metadata
- Output: `checkpoint_map.json` with `{size: {pile_step, dedup_step, pile_tokens, dedup_tokens, token_mismatch_pct}}`

### FR-2: Model Evaluation Pipeline
- Evaluate 8 model variants: Pythia-{160m, 410m, 1b, 6.9b} × {Pile, dedup-Pile}
- Benchmarks: MMLU (5-shot), HellaSwag (0-shot), ARC-Challenge (25-shot), WinoGrande (5-shot)
- Tool: lm-evaluation-harness v0.4.x CLI
- Precision: float16
- Batch size: auto
- Output: per-model JSON results in `results/` directory

### FR-3: Results Parsing and Accuracy Extraction
- Parse lm-eval JSON output files for each model × benchmark
- Extract `acc,none` field (normalized accuracy, 0–1 scale)
- Construct accuracy matrix: `accuracy[size][corpus][benchmark]`
- Store as `results_matrix.json`

### FR-4: Statistical Testing Module
- Paired t-test per benchmark across 4 model sizes (n=4 pairs)
- Bonferroni correction: α_corrected = 0.05 / 4 = 0.0125 per benchmark
- Compute: mean differential, t-statistic, p-value, significant (bool)
- Output: `statistical_results.json`

### FR-5: Mechanism Verification Check
- Pre-flight check: confirm any |delta| > 0.001 (0.1 pp) across model pairs
- If all deltas < 0.001 → raise RuntimeError (checkpoint loading error)
- Confirm Pile and dedup-Pile models produce distinct outputs

### FR-6: Visualization Module
- Figure 1 (MANDATORY): Per-benchmark accuracy differential bar chart (dedup minus Pile, all 4 sizes, error bars, significance stars)
- Figure 2: Model-size scaling plot (differential vs log(model_params) per benchmark)
- Figure 3: Paired accuracy scatter (Pile x-axis, dedup y-axis; diagonal = no difference)
- Figure 4: P-value heatmap (benchmarks × model sizes, color = Bonferroni significance)
- Save all figures to `docs/youra_research/h-e1/figures/`

### FR-7: Validation Report Generation
- Summarize gate condition result (PASS / FAIL)
- List significant benchmarks (if any): p-value, mean_diff, direction
- Confirm mechanism verification pass/fail
- Output: `docs/youra_research/h-e1/04_validation.md`

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All evaluation is deterministic (greedy decoding, no sampling)
- Exact lm-eval version pinned in `requirements.txt`
- All random seeds fixed (seed=1 where applicable)

### NFR-2: Performance
- Full evaluation (8 models × 4 benchmarks) ≤ 24 GPU-hours on A100 40GB
- Models loaded in float16 to fit GPU memory (Pythia-6.9B ~13GB in fp16)

### NFR-3: Portability
- Code runs on single-GPU and multi-GPU configurations
- All HuggingFace artifacts cached locally to avoid re-download

### NFR-4: Statistical Rigor
- Paired t-test (not independent samples) — same 4 model sizes across both corpus conditions
- No correction inflation beyond Bonferroni (4 tests)
- Report exact p-values alongside significance flags

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Mechanism verification | Any |delta| > 0.001 | Required |
| Significant benchmarks | ≥1 benchmark p < 0.0125 at ≥2 sizes | Gate (MUST_WORK) |
| Direction consistency | Same sign of differential at ≥2 model sizes | Secondary |
| Code runs without error | All 8 evaluations complete | Required |

**Gate outcome:** PASS → proceed to H-M1 mechanism hypotheses. FAIL → terminate hypothesis chain.

---

## 7. Data Specification

### 7.1 Model Checkpoints

| Model ID | HuggingFace Identifier | Revision | Tokens |
|----------|----------------------|----------|--------|
| Pythia-160M Pile | EleutherAI/pythia-160m | step99000 | ~207B |
| Pythia-410M Pile | EleutherAI/pythia-410m | step99000 | ~207B |
| Pythia-1B Pile | EleutherAI/pythia-1b | step99000 | ~207B |
| Pythia-6.9B Pile | EleutherAI/pythia-6.9b | step99000 | ~207B |
| Pythia-160M dedup | EleutherAI/pythia-160m-deduped | step143000 | ~207B |
| Pythia-410M dedup | EleutherAI/pythia-410m-deduped | step143000 | ~207B |
| Pythia-1B dedup | EleutherAI/pythia-1b-deduped | step143000 | ~207B |
| Pythia-6.9B dedup | EleutherAI/pythia-6.9b-deduped | step143000 | ~207B |

- **Download**: HuggingFace `transformers` auto-download on first run
- **Cache**: `~/.cache/huggingface/` (or `HF_HOME` env var)
- **Manual download task required**: No (auto-downloaded by transformers)

### 7.2 Benchmark Datasets

| Benchmark | HuggingFace ID | Split | Items | Few-shot |
|-----------|---------------|-------|-------|----------|
| MMLU | cais/mmlu | test | 14,042 | 5 |
| HellaSwag | hellaswag | validation | 10,042 | 0 |
| ARC-Challenge | ai2_arc (ARC-Challenge) | test | 1,172 | 25 |
| WinoGrande | allenai/winogrande | validation | 1,267 | 5 |

- **Download**: Auto-downloaded by lm-evaluation-harness from HuggingFace datasets
- **Manual download task required**: No

### 7.3 Output Files

| File | Location | Description |
|------|----------|-------------|
| checkpoint_map.json | h-e1/ | Token-matched checkpoint steps |
| results/*.json | h-e1/results/ | lm-eval per-model output |
| results_matrix.json | h-e1/ | Parsed accuracy matrix |
| statistical_results.json | h-e1/ | Paired t-test outcomes |
| figures/*.png | h-e1/figures/ | 4 visualization figures |
| 04_validation.md | h-e1/ | Final validation report |

---

## 8. Dependencies

### 8.1 Python Packages (pip install)

```
lm-eval>=0.4.0
transformers>=4.38.0
accelerate>=0.27.0
torch>=2.1.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
statsmodels>=0.14.0
datasets>=2.16.0
```

### 8.2 External Repositories (reference only, no install)

| Repository | Purpose |
|------------|---------|
| EleutherAI/pythia | Checkpoint documentation and token-count metadata |
| EleutherAI/lm-evaluation-harness | Evaluation framework (installed via pip) |

### 8.3 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | 1× A100 40GB (or 2× 24GB) | 1× A100 80GB |
| VRAM | 24GB (Pythia-6.9B in fp16) | 40GB |
| Storage | ~50GB (HF cache + results) | 100GB |
| Time | 12–24 GPU-hours | 12 GPU-hours |

---

## 9. Experiment Directory Structure

```
docs/youra_research/h-e1/
├── 02b_context.md
├── 02c_experiment_brief.md
├── 03_prd.md                  ← this file
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 03_tasks.yaml
├── checkpoint_map.json
├── results/
│   └── pythia-{size}-{corpus}-step{N}.json
├── results_matrix.json
├── statistical_results.json
├── figures/
│   ├── differential_bar.png
│   ├── scaling_plot.png
│   ├── paired_scatter.png
│   └── pvalue_heatmap.png
└── 04_validation.md
```

---

## 10. Risk Register

| Risk | Severity | Mitigation |
|------|----------|-----------|
| R1: Token-count mismatch > 10% | High | Report both step-matched and token-count-matched results; flag as confound |
| R2: Checkpoint loading error (identical outputs) | Critical | verify_mechanism_activation() pre-flight check |
| R3: GPU OOM for 6.9B model | Medium | Use float16 + device_map="auto"; fall back to 2-GPU setup |
| R4: lm-eval version mismatch | Low | Pin version in requirements.txt; verify benchmark task names |
| R5: All-null statistical result | Medium | Report with exact p-values; confirm mechanism activation check passed |
