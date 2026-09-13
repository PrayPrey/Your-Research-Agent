---
title: "PRD: H-M1 — SFT Signal Void at Hard Difficulty"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
stepsCompleted:
  - prd-executive-summary
  - prd-problem-statement
  - prd-functional-requirements
  - prd-non-functional-requirements
  - prd-data-specification
  - prd-evaluation-metrics
  - prd-dependencies
  - prd-success-criteria
date: "2026-08-26"
author: yoon303@ust.ac.kr
source: 02c_experiment_brief.md
base_hypothesis: H-E1
---

# PRD: H-M1 — SFT Signal Void at Hard Difficulty

## 1. Executive Summary

This PRD defines the implementation requirements for **H-M1**, a MECHANISM hypothesis verifying that SFT trained on APPS creates a measurable "signal void" at hard difficulty levels: specifically that SFT pass@1 on LiveCodeBench-Hard is < 60%, and that APPS training loss is systematically higher on competition-tier problems than on introductory-tier problems.

**Core claim (gate condition):**
> SFT trained on APPS (DeepSeek-Coder-7B-base) achieves pass@1 < 60% on LiveCodeBench-Hard, confirmed via bigcode-evaluation-harness.

**Approach:** Reuse the SFT model checkpoint from H-E1 (no additional training). Execute two analysis tasks: (A) evaluate SFT on LiveCodeBench-Hard using bigcode-harness; (B) compute APPS difficulty-stratified training loss via forward pass; (C) measure APPS-Competition coverage (fraction of problems with ≥1 passing solution). Produce combined `signal_void_analysis.json` and 3–4 diagnostic figures.

**This is an analysis-only hypothesis.** No new model training is required. H-M1 reuses the H-E1 SFT checkpoint to characterize the signal void mechanism.

---

## 2. Problem Statement

### 2.1 Research Gap

H-E1 established that RLEF-Fraction yields disproportionate improvement on harder benchmarks. H-M1 asks: **why does SFT fail at hard difficulty?** The proposed mechanism is a "signal void" — near-zero coverage of hard problems in APPS training data, resulting in sparse gradient signal at competition difficulty levels.

### 2.2 What This Analysis Answers

**Question:** Does SFT trained on APPS create a measurable signal void at hard difficulty — both at evaluation time (pass@1 < 60% on LCB-Hard) and at training time (higher cross-entropy loss on competition problems)?

**Not answered here:** Whether RLEF-Fraction fixes this void (H-M2), whether the fraction reward specifically drives the improvement (H-M3), or how performance scales (H-M4).

### 2.3 Controlled Conditions

| Factor | Fixed Value |
|--------|-------------|
| Base model | DeepSeek-Coder-7B-base |
| Training data | APPS train split (5,000 problems) — from H-E1 |
| SFT checkpoint | H-E1 checkpoint (no re-training) |
| Evaluation harness | bigcode-evaluation-harness |
| Seed | 1 (matching H-E1) |

---

## 3. Functional Requirements

### FR-1: Checkpoint Availability (from H-E1)

**FR-1.1: H-E1 SFT Checkpoint**
- Source: `checkpoints/sft_baseline/` (H-E1 output)
- If checkpoint unavailable: re-run H-E1 SFT training before proceeding
- If H-E1 already evaluated LCB-Hard: extract results from `results/h-e1/sft_baseline_livecodebench.json`

**FR-1.2: Fallback — Base Model**
- If H-E1 checkpoint missing: use `deepseek-ai/deepseek-coder-7b-base` directly
- Document fallback in experiment log

### FR-2: Task A — LiveCodeBench-Hard Evaluation

**FR-2.1: Check H-E1 Results First**
- Check if `results/h-e1/sft_baseline_livecodebench.json` exists
- If exists AND contains LCB-Hard pass@1: extract directly (zero-cost)
- If missing or incomplete: run bigcode-harness evaluation

**FR-2.2: Bigcode-Harness Evaluation (if needed)**
- Model: H-E1 SFT checkpoint (`checkpoints/sft_baseline/`)
- Task: `livecodebench` with difficulty filter = "hard"
- Metric: pass@1, n_samples=1, temperature=0.0 (greedy, deterministic)
- Output: `results/h-m1/sft_lcb_hard.json`
- Command:
```bash
accelerate launch main.py \
  --model ./checkpoints/sft_baseline \
  --tasks livecodebench \
  --n_samples 1 \
  --temperature 0.0 \
  --metric_output_path results/h-m1/sft_lcb_hard.json
```

**FR-2.3: Signal Void Check**
- Extract `sft_pass1_lcb_hard` from results
- Check: `sft_pass1_lcb_hard < 0.60`
- Log result to `results/h-m1/signal_void_analysis.json`

### FR-3: Task B — APPS Difficulty-Stratified Loss Analysis

**FR-3.1: Forward Pass Computation**
- Load H-E1 SFT checkpoint in eval mode
- Iterate over APPS train split, computing per-example cross-entropy loss
- Stratify by difficulty bucket: `introductory`, `interview`, `competition`
- Use first reference solution from `example["solutions"]` for loss computation
- Tokenization: max_length=2048, truncate from right
- Output: `results/h-m1/apps_difficulty_loss.json`

**FR-3.2: Loss Gradient Verification**
- Check: `competition_loss > introductory_loss`
- Compute: `loss_gradient = competition_loss - introductory_loss`
- Report per-bucket: mean loss, std, sample count
- Success if gradient > 0 (competition harder than introductory)

**FR-3.3: Implementation**
```python
# SFTSignalVoidAnalyzer — see 02c_experiment_brief.md for full class definition
analyzer = SFTSignalVoidAnalyzer(sft_checkpoint_path)
loss_results = analyzer.compute_difficulty_stratified_loss(apps_train_split)
# Output: {"introductory": float, "interview": float, "competition": float}
```

### FR-4: Task C — APPS-Competition Coverage Check

**FR-4.1: Coverage Measurement**
- Load APPS train split, filter `difficulty == "competition"`
- For each problem: check if `len(example["solutions"]) > 0` (has reference solution)
- Compute: `coverage = count_with_solutions / total_competition_problems`
- Output: `results/h-m1/apps_hard_coverage.json`

**FR-4.2: Coverage Threshold**
- Success indicator: `coverage < 0.30` (signal void in reference solutions)
- Report: total competition problems, problems with solutions, coverage %

### FR-5: Evaluation Aggregation

**FR-5.1: Combined Results**
- Aggregate results from Tasks A, B, C into `results/h-m1/signal_void_analysis.json`
- Format:
```json
{
  "sft_lcb_hard_pass1": float,
  "signal_void_primary": bool,
  "apps_difficulty_loss": {"introductory": float, "interview": float, "competition": float},
  "loss_gradient_secondary": bool,
  "apps_competition_coverage": float,
  "gate_satisfied": bool
}
```

**FR-5.2: Gate Decision**
- Primary gate: `sft_lcb_hard_pass1 < 0.60`
- Print PASS/FAIL decision to stdout and log

### FR-6: Visualization

**FR-6.1: Gate Metrics Comparison (mandatory)**
- Bar chart: SFT pass@1 on LCB-Hard vs 60% threshold
- Include reference lines for HumanEval and LCB-Easy (difficulty gradient context)
- Save: `docs/youra_research/h-m1/figures/gate_metrics.png`

**FR-6.2: Difficulty-Performance Gradient (autonomous)**
- Line chart: SFT pass@1 across benchmarks (HumanEval → MBPP → LCB-Easy → LCB-Medium → LCB-Hard)
- Shows progressive degradation confirming signal void at hard difficulty
- Save: `docs/youra_research/h-m1/figures/difficulty_gradient.png`

**FR-6.3: APPS Difficulty-Bucket Loss (autonomous)**
- Bar chart: mean SFT training loss by difficulty bucket (introductory / interview / competition)
- Annotate with sample counts per bucket
- Include error bars (± 1 std)
- Save: `docs/youra_research/h-m1/figures/apps_difficulty_loss.png`

**FR-6.4: APPS Coverage Analysis (autonomous)**
- Stacked bar: % of APPS-Competition problems with ≥1 reference solution vs no solution
- Title: "APPS Competition-Level Coverage (Signal Void Evidence)"
- Save: `docs/youra_research/h-m1/figures/apps_coverage.png`

---

## 4. Data Specification

### 4.1 Training Data (Analysis-Only — No Training)

| Field | Value |
|-------|-------|
| Name | APPS (Automated Programming Progress Standard) |
| HuggingFace ID | `codeparrot/apps` |
| Split | `train` (5,000 problems) |
| Manual download? | **NO** — HuggingFace auto-download |
| Purpose | Forward-pass loss analysis only (no gradient updates) |
| Difficulty buckets | introductory / interview / competition |
| Difficulty distribution | intro: ~39% (~1,950), interview: ~49% (~2,450), competition: ~12% (~600) |

### 4.2 Evaluation Dataset

| Dataset | Source | Auto-managed |
|---------|--------|-------------|
| LiveCodeBench-Hard 2024-Q4 | `livecodebench/code_generation_lite` | ✓ (bigcode-harness) |
| HumanEval (reference) | `openai_humaneval` | ✓ (bigcode-harness) |

**LiveCodeBench-Hard size:** ~175 problems (temporally isolated post-training-cutoff; no contamination risk)

### 4.3 Model Checkpoint (from H-E1)

| Field | Value |
|-------|-------|
| Checkpoint | `checkpoints/sft_baseline/` (H-E1 output) |
| Base model | `deepseek-ai/deepseek-coder-7b-base` |
| Training | SFT on APPS train, cross-entropy, 3 epochs, AdamW lr=1e-5, seed=42 |
| Source | H-E1 Phase 4 output |

---

## 5. Evaluation Metrics

### 5.1 Primary Gate Metric

| Metric | Computation | Gate |
|--------|-------------|------|
| SFT pass@1 LCB-Hard | bigcode-harness output | < 0.60 |

### 5.2 Secondary Metrics

| Metric | Requirement |
|--------|-------------|
| APPS competition loss | > APPS introductory loss (gradient confirmed) |
| APPS coverage (competition) | < 30% (sparse signal confirmed) |
| SFT pass@1 HumanEval | Reported (reference only) |
| Loss gradient (competition − introductory) | > 0 nats |

### 5.3 Expected Values (from Phase 2C research)

| Metric | Expected | Source |
|--------|----------|--------|
| SFT pass@1 LCB-Hard | 10–35% | Literature (7B RL at 42–52%; SFT ~20–30pp lower) |
| Competition loss | Substantially > introductory loss | MapCoder + SFT-then-RL papers |
| APPS competition coverage | ~7.7% of APPS+ | APPS+ data: 572/7413 |

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All computations deterministic (eval mode, no dropout, greedy decoding for LCB)
- Random seed 1 (matching H-E1 configuration)
- APPS split access via HuggingFace (same version as H-E1)
- Results logged to JSON before plotting

### NFR-2: Computational Budget
- Task A: bigcode-harness on LCB-Hard — ~1–2h on single A100 (if not already in H-E1 results)
- Task B: Forward pass over 5,000 APPS problems — ~30–60min on A100
- Task C: Coverage check — CPU-only, minutes
- Total: 2–4h if Task A needed; < 1h if H-E1 results reusable

### NFR-3: Safety
- Forward pass only (no subprocess code execution in Task B and C)
- Task A uses bigcode-harness subprocess execution (same safety as H-E1)
- No in-process `exec()` calls

### NFR-4: Data Organization
```
docs/youra_research/h-m1/
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── figures/
│   ├── gate_metrics.png
│   ├── difficulty_gradient.png
│   ├── apps_difficulty_loss.png
│   └── apps_coverage.png
└── code/
    ├── analyze_sft_lcb.py       # Task A: extract/run LCB-Hard evaluation
    ├── analyze_sft_loss.py      # Task B: APPS difficulty-stratified loss
    ├── check_apps_coverage.py   # Task C: APPS competition coverage
    ├── aggregate_results.py     # Combine results + gate decision
    ├── make_figures.py          # Generate all 4 figures
    └── requirements.txt

results/h-m1/
├── sft_lcb_hard.json
├── apps_difficulty_loss.json
├── apps_hard_coverage.json
└── signal_void_analysis.json
```

---

## 7. Dependencies

### 7.1 Python Packages

```txt
# Inherited from H-E1 (same environment)
torch>=2.1.0
transformers>=4.40.0
trl>=0.8.6
accelerate>=0.27.0
datasets>=2.18.0
numpy>=1.26.0
scipy>=1.11.0
matplotlib>=3.8.0
seaborn>=0.13.0
pandas>=2.0.0
tqdm>=4.66.0
pyyaml>=6.0
```

### 7.2 External Repositories

| Repo | Purpose | Source |
|------|---------|--------|
| `bigcode-project/bigcode-evaluation-harness` | LCB-Hard evaluation (Task A) | git clone (same install as H-E1) |

**Note:** bigcode-harness already installed from H-E1. Use same pinned commit.

### 7.3 H-E1 Artifacts Required

| Artifact | Path | Purpose |
|---------|------|---------|
| SFT checkpoint | `checkpoints/sft_baseline/` | Task A evaluation, Task B loss analysis |
| H-E1 evaluation results | `results/h-e1/sft_baseline_livecodebench.json` | Task A (may avoid re-run) |

### 7.4 Hardware

| Resource | Minimum | Recommended |
|---------|---------|-------------|
| GPU | 1× A100 40GB | 1× A100 80GB |
| RAM | 64GB | 128GB |
| Storage | 20GB additional | 50GB |

---

## 8. Success Criteria

### PoC Pass Conditions (primary required)

1. **Code correctness:** All scripts run without error
2. **Gate condition:** `sft_pass1_lcb_hard < 0.60`

### Secondary Success (informational, not blocking)

3. APPS competition loss > APPS introductory loss
4. APPS-Competition coverage < 30%

### Fail Action

If `sft_pass1_lcb_hard >= 0.60`: EXPLORE — SFT signal void framing needs revision. H-M2, H-M3, H-M4 may not proceed as planned. Investigate whether LCB-Hard contamination or model scaling accounts for higher-than-expected performance.

### Phase 2C Completeness Check

| Item | Covered in FRs |
|------|---------------|
| SFT baseline model (H-E1 reuse) | FR-1 ✓ |
| LiveCodeBench-Hard evaluation | FR-2 ✓ |
| APPS difficulty-stratified loss | FR-3 ✓ |
| APPS-Competition coverage | FR-4 ✓ |
| Signal void gate check (< 60%) | FR-5.2 ✓ |
| Visualization (4 figures) | FR-6 ✓ |
| Signal void analysis JSON | FR-5.1 ✓ |
| Fallback checkpoint strategy | FR-1.2 ✓ |
