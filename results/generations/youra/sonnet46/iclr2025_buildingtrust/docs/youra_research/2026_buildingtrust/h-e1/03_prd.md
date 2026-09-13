---
title: "PRD: H-E1 - Alignment-Induced Brier Reliability Overconfidence in Pythia LLMs"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
generated_by: Phase 3 Step 2 (BMAD PRD Workflow - Inline Execution)
date: 2026-03-14
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - dependencies
status: COMPLETE
---

# PRD: H-E1 — Alignment-Induced Brier Reliability Overconfidence in Pythia LLMs

## Executive Summary

This experiment validates the **existence** of alignment-induced overconfidence in Pythia LLMs — specifically, whether RLHF-aligned models (SFT, DPO, PPO) exhibit significantly higher Brier reliability (overconfidence) than their paired base counterparts on MMLU forced-choice evaluation. This is the **root hypothesis (FOUNDATION)** of a 5-hypothesis causal chain; if it fails, the entire H-M1 through H-M4 mechanistic chain is invalidated.

**Experiment Type:** Evaluation-only (no training). 9 pre-trained checkpoints evaluated via lm-eval-harness v0.4.11.

**Gate:** MUST_WORK — ΔBrier reliability > 0 with bootstrap 95% CI lower bound > 0 for PPO or DPO in ≥2/3 Pythia model sizes (1.4B, 2.8B, 6.9B).

---

## Problem Statement

### Research Question
Does alignment training (SFT, DPO, PPO) causally increase overconfidence (Brier reliability component) in Pythia LLMs when evaluated on MMLU forced-choice continuation tasks?

### Hypothesis Statement
Under forced-choice evaluation (lm-eval log-prob continuation on MMLU), alignment-trained LLMs (SFT, DPO, PPO) show higher Brier reliability (overconfidence) than their paired base counterparts, with bootstrap 95% CI lower bound > 0 for at least one alignment method (PPO or DPO) across at least 2/3 Pythia model sizes (1.4B, 2.8B, 6.9B).

### Context
- Prior work (Xie et al. 2024) shows pretrained LLMs have ECE < 0.15 on MMLU; aligned LLaMA-2-Chat has ECE ≈ 0.298
- Brier decomposition (Murphy 1973) separates overconfidence (reliability) from discriminability (resolution)
- This experiment isolates the reliability component to test whether alignment specifically increases overconfidence
- The Pythia alignment ladder (Li et al. 2024) provides causally-paired base/aligned checkpoints controlling for architecture and training data

### Gap / Motivation
No published study has systematically tested whether Brier reliability component (not just ECE) increases monotonically across SFT < DPO < PPO alignment methods using causally-paired Pythia checkpoints. This experiment provides the empirical foundation for downstream mechanistic analysis.

---

## Functional Requirements

### FR-1: Model Loading and Evaluation Framework

**FR-1.1 Model Checkpoint Loading**
- Load 9 pre-trained checkpoints via HuggingFace `transformers`:
  - Base: `EleutherAI/pythia-1.4b`, `EleutherAI/pythia-2.8b`, `EleutherAI/pythia-6.9b`
  - SFT variants: Li et al. 2024 Pythia-{1.4b|2.8b|6.9b}-SFT (verify HF IDs from paper Appendix B)
  - DPO variants: Li et al. 2024 Pythia-{1.4b|2.8b|6.9b}-DPO (verify HF IDs from paper Appendix B)
  - PPO variants: Li et al. 2024 Pythia-{1.4b|2.8b|6.9b}-PPO (verify HF IDs from paper Appendix B)
- **CRITICAL (Risk R1):** Verify exact HuggingFace model IDs from Li et al. 2024 Appendix B before running. If unavailable, fall back to LLaMA-2 family (document deviation).
- All models loaded in float16 or bfloat16 on single GPU

**FR-1.2 MMLU Evaluation via lm-eval-harness**
- Framework: `lm-eval-harness v0.4.11` (EleutherAI)
- Task: `--tasks mmlu` (all 57 subjects, full test set ~14,042 items)
- Evaluation mode: 0-shot (no few-shot examples), greedy decoding (temperature=1.0)
- Log extraction: `--log_samples` flag to capture per-item 4-option log-probability vectors
- Output: JSON results files per model in `results/{model_id}/`
- Command template:
  ```bash
  lm_eval --model hf \
    --model_args "pretrained={model_id},dtype=float16" \
    --tasks mmlu \
    --num_fewshot 0 \
    --output_path ./results/{model_id}/ \
    --log_samples \
    --device cuda:0 \
    --batch_size 8
  ```

### FR-2: Calibration Computation

**FR-2.1 Log-Probability Extraction**
- Parse lm-eval `--log_samples` JSON output to extract per-item 4-option log-probability vectors
- Apply softmax normalization: `probs = softmax(logprobs, axis=-1)` → (N, 4) probability matrices
- Extract ground-truth labels (0-indexed integer, 0=A, 1=B, 2=C, 3=D)

**FR-2.2 Brier Score Decomposition (Murphy 1973)**
- Implement Murphy (1973) 3-component decomposition: `Brier = Reliability − Resolution + Uncertainty`
- **Reliability** (overconfidence): `REL = Σ_k Σ_i (n_ki/N)(f_ki − o_ki)²` across 15 bins × 4 options
- **Resolution**: `RES = Σ_k Σ_i (n_ki/N)(o_ki − ō_k)²`
- **Uncertainty**: `UNC = Σ_k ō_k(1 − ō_k)` (constant per dataset)
- N_bins = 15 (equal-width, [0,1])
- Primary output: `reliability` scalar per model

**FR-2.3 Expected Calibration Error (ECE)**
- Implement Guo et al. (2017) top-1 confidence ECE:
  ```
  ECE = Σ_i (|B_i|/N) |acc(B_i) − conf(B_i)|
  ```
- 15 equal-width bins on top-1 predicted probability
- Secondary supporting metric

**FR-2.4 Delta Computation with Bootstrap CI**
- Compute ΔBrier reliability = `reliability_aligned − reliability_base` for each (model_size, alignment_method) pair
- Bootstrap CI: 1,000 bootstrap samples, 95% CI via percentile method (2.5th, 97.5th percentiles)
- Output per pair: `(delta_rel, ci_lower, ci_upper)`

### FR-3: Gate Evaluation

**FR-3.1 MUST_WORK Gate Check**
- Evaluate gate condition: ΔBrier_reliability > 0 AND CI_lower > 0
- Check for PPO method: count Pythia sizes (1.4B, 2.8B, 6.9B) where condition holds
- Check for DPO method: same count
- Gate PASSES if: `(n_ppo_pass ≥ 2) OR (n_dpo_pass ≥ 2)` where n = count of sizes satisfying condition
- Gate FAILS if neither PPO nor DPO satisfies condition in ≥2/3 sizes

**FR-3.2 Gate Result Reporting**
- Produce structured gate result: `{gate: "PASS"|"FAIL", method: "PPO"|"DPO"|"BOTH"|"NONE", sizes_passing: [...]}`
- If FAIL: document failure mode (checkpoint not found / direction reversed / CI crosses zero / near-zero delta)

### FR-4: Visualization

**FR-4.1 Required Figure (Mandatory)**
- Bar chart of ΔBrier reliability with 95% CI error bars
- X-axis: Pythia sizes (1.4B, 2.8B, 6.9B)
- Grouped bars: SFT, DPO, PPO per size
- Error bars: bootstrap 95% CI
- Save to: `h-e1/figures/delta_reliability_bar.png`

**FR-4.2 Additional Figures (Recommended)**
- Calibration reliability diagrams (3×3 grid): base vs SFT/DPO/PPO per size → `calibration_curves.png`
- ECE heatmap (3 sizes × 4 conditions) → `ece_heatmap.png`
- Brier decomposition stacked bar (reliability / resolution / uncertainty per model) → `brier_decomposition.png`
- Bootstrap CI distribution plots → `bootstrap_ci_distributions.png`
- Save all to: `h-e1/figures/`

### FR-5: Results Output and Reporting

**FR-5.1 Results Persistence**
- Save all per-model metrics to `h-e1/results/calibration_results.json`:
  ```json
  {
    "pythia-1.4b-base": {"ece": ..., "brier_rel": ..., "brier_res": ..., "brier_unc": ...},
    "pythia-1.4b-sft": {"ece": ..., "brier_rel": ..., "delta_rel": ..., "ci_lower": ..., "ci_upper": ...},
    ...
  }
  ```
- Save gate result to `h-e1/results/gate_result.json`

**FR-5.2 Validation Report Generation**
- Generate `h-e1/04_validation.md` with:
  - Gate result (PASS/FAIL) with evidence
  - Per-model metrics table
  - Key findings (top 3)
  - Failure analysis (if applicable)
  - Mechanism activation indicators

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed: `np.random.seed(42)` for all bootstrap sampling
- Single run (PoC phase — no multi-run averaging)
- All intermediate results (per-model logprobs) saved to enable re-analysis

### NFR-2: Performance / Resource
- Single GPU execution: `CUDA_VISIBLE_DEVICES=<lowest_free_GPU>`
- Batch size: 8 (adjust down if OOM for 6.9B models)
- Memory: ~14GB VRAM for 6.9B float16 (verify before running)
- Storage: ~50GB for 9 model checkpoints + lm-eval output logs

### NFR-3: Code Quality
- LIGHT tier infrastructure: argparse + hardcoded paths acceptable (no YAML config required)
- Logging: print statements + CSV summary file
- Testing: smoke test on 1 model, 10 MMLU items before full run
- Code structure: single-file or minimal module (not production-grade)

### NFR-4: Error Handling
- Model load failure: log + skip (continue with remaining models); document in gate result
- lm-eval timeout/OOM: retry with batch_size=4; document if still fails
- Missing aligned checkpoint (Risk R1): fall back to LLaMA-2 family; document deviation in 04_validation.md

### NFR-5: Documentation
- Inline comments for Brier decomposition formula derivation
- README with: setup instructions, model ID list, run order, expected outputs

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| ΔBrier reliability > 0 | CI lower bound > 0 | `compute_delta_reliability()` output |
| Coverage | PPO or DPO satisfies condition in ≥2/3 Pythia sizes | `verify_experiment_validity()` gate check |
| All 9 models evaluated | 9/9 complete without fatal error | lm-eval completion log |

### Secondary Success (Informative)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| ΔECE > 0 | PPO in ≥2/3 sizes | `compute_ece()` output |
| Monotonic ordering | PPO ≥ DPO > SFT in ≥2/3 sizes | delta_rel ranking |
| Base ECE < 0.15 | Consistent with Xie et al. 2024 | Absolute ECE per base model |

### Failure Criteria
- **Hard Fail**: ΔBrier_reliability ≤ 0 for ALL alignment methods at ALL Pythia sizes
- **Gate Fail**: CI lower ≤ 0 for both PPO and DPO in ≥2/3 sizes
- **Infrastructure Fail**: <7/9 models evaluate successfully (>2 model load failures)

---

## Dependencies

### External Dependencies

| Dependency | Version | Source | Risk |
|------------|---------|--------|------|
| lm-eval-harness | v0.4.11 | EleutherAI/lm-evaluation-harness | Low — stable release |
| transformers | ≥4.35.0 | HuggingFace | Low — standard |
| PyTorch | ≥2.0 | pytorch.org | Low — standard |
| numpy | ≥1.24 | pip | Low |
| scipy | ≥1.10 | pip (for softmax) | Low |
| matplotlib | ≥3.7 | pip (figures) | Low |
| Pythia base checkpoints | latest | EleutherAI/pythia-{1.4b\|2.8b\|6.9b} | Low — publicly available |
| Pythia aligned checkpoints | Li et al. 2024 | HuggingFace (verify IDs from paper Appendix B) | **HIGH (Risk R1)** |

### Pipeline Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 2C experiment brief | ✅ COMPLETED | `h-e1/02c_experiment_brief.md` |
| MMLU dataset (cais/mmlu) | Auto-downloaded by lm-eval | No pre-download required |
| GPU availability | Phase 4 setup | CUDA_VISIBLE_DEVICES=<lowest_free> |

### Key Risk: R1 — Aligned Checkpoint Availability
- **Risk**: Li et al. 2024 Pythia-specific alignment checkpoints may not be on HuggingFace Hub
- **Mitigation**: Before running, search HuggingFace for `pythia-*-sft`, `pythia-*-dpo`, `pythia-*-ppo` models referencing Li et al. 2024
- **Fallback**: Use LLaMA-2-7b family (LLaMA-2-7b-base, LLaMA-2-7b-chat as SFT proxy) — document deviation

### Key Risk: R2 — Log-Prob Format Mismatch
- **Risk**: lm-eval `--log_samples` JSON format may vary by version
- **Mitigation**: Test on 1 model first (smoke test), inspect JSON structure before full run

---

## Scope

### In Scope
- 9 Pythia checkpoints (3 base + 6 aligned) evaluated on MMLU full test set
- Brier score decomposition (Murphy 1973) + ECE (Guo 2017)
- Bootstrap CI computation (n=1000)
- All required and recommended visualizations
- Gate evaluation and 04_validation.md report
- Fallback model family if Risk R1 materializes

### Out of Scope
- Training or fine-tuning any model
- Evaluating on datasets other than MMLU (TruthfulQA is H-M3 scope)
- Statistical significance testing beyond bootstrap CI
- Multi-GPU evaluation
- Comparison with published ECE values (qualitative reference only)
- Mechanistic analysis (logit margin analysis = H-M2 scope)

---

## Implementation Notes for Architecture Agent

### Code Structure (LIGHT Tier)
```
h-e1/
├── run_evaluation.sh          # lm_eval CLI runner (9 models)
├── calibration_analysis.py    # Brier decomp + ECE + bootstrap CI
├── plot_results.py             # Visualization (4 figures)
├── verify_gate.py              # Gate check + 04_validation.md generator
├── results/                    # lm-eval JSON outputs + calibration_results.json
└── figures/                    # PNG outputs
```

### Data Flow
```
lm_eval → results/{model}/samples_mmlu.jsonl
  → calibration_analysis.py → results/calibration_results.json
  → verify_gate.py → results/gate_result.json + 04_validation.md
  → plot_results.py → figures/*.png
```

### Key Algorithm: Brier Decomposition
Per Murphy (1973): Bin by predicted probability into 15 equal-width bins. For each bin-option pair, compute squared difference between mean predicted probability and empirical frequency. Weight by bin population fraction.

---

*Generated: Phase 3 Step 2 (PRD Workflow Inline Execution)*
*Source: h-e1/02c_experiment_brief.md*
*Hypothesis: H-E1 (EXISTENCE, FOUNDATION, MUST_WORK gate)*
