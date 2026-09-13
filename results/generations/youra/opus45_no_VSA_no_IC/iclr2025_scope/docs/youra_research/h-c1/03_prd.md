# Product Requirements Document: h-c1

## Hypothesis

**ID**: h-c1  
**Type**: CONDITION  
**Gate**: SHOULD_WORK  
**Statement**: Scaling law α estimate is consistent (within 0.15) across single-hop (SQuAD-v2) and multi-hop (HotpotQA) QA tasks

---

## Executive Summary

Validate cross-task consistency of LoRA rank scaling law by replicating h-e1 methodology on HotpotQA (multi-hop QA). Compare fitted α exponents between SQuAD-v2 (from h-e1) and HotpotQA. Pass if |α_squad - α_hotpot| ≤ 0.15.

---

## Problem Statement

The h-e1 scaling law was established on single-hop QA (SQuAD-v2). If optimal rank scaling varies substantially across task types, the law has limited generalizability. Demonstrating consistency across single-hop and multi-hop reasoning would strengthen the scaling law's practical applicability.

---

## Functional Requirements

### FR-1: Data Loading - HotpotQA
- Load HotpotQA distractor setting from HuggingFace
- Train split: 90,447 examples
- Validation split: 7,405 examples (full set for evaluation)
- Preprocessing: multi-document QA tokenization with max_length=512

### FR-2: Load h-e1 Results
- Load `results/h-e1_scaling_fit.json`
- Extract: α_squad, ci_squad_low, ci_squad_high
- These serve as reference for cross-task comparison

### FR-3: Model Loading (Reuse h-e1)
- Load Pythia models: EleutherAI/pythia-{1b, 2.8b, 6.9b, 12b}
- Apply LoRA to query_key_value modules
- Identical configuration to h-e1

### FR-4: LoRA Configuration Sweep (Reuse h-e1)
- Ranks: [4, 8, 16, 32, 64, 128]
- Alpha: 2×rank (rsLoRA scaling)
- Dropout: 0.05
- Target modules: ["query_key_value"]

### FR-5: Training Protocol (Reuse h-e1)
- Epochs: 3
- Optimizer: AdamW, lr=1e-4
- Batch size: 8 (effective 32 via gradient accumulation 4)
- Warmup: 100 steps
- Scheduler: linear decay
- Seeds: [42, 1337, 2024]

### FR-6: Evaluation - HotpotQA
- Primary metric: Answer F1 (official HotpotQA evaluation)
- Secondary metric: Supporting Facts F1
- Evaluate on full validation set (7,405 examples)
- Record per-run metrics

### FR-7: Optimal Rank Determination
- For each (model, seed): r_opt = argmax_r(Answer_F1)
- Handle ties: geometric mean of tied ranks
- Output: (N, r_opt) pairs for HotpotQA (12 data points)

### FR-8: Statistical Analysis - HotpotQA
- Log-linear regression: log(r_opt) = α·log(N) + log(c)
- Bootstrap CI: B=1000 resamples
- Extract: α_hotpot, ci_hotpot_low, ci_hotpot_high

### FR-9: Cross-Task Comparison
- Calculate |α_squad - α_hotpot|
- Check CI overlap between datasets
- Generate comparison visualization

### FR-10: Pass/Fail Criteria
- Primary: |α_squad - α_hotpot| ≤ 0.15
- Secondary: 95% CIs overlap
- Sanity: α_hotpot ∈ (0, 1)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seeds for all random operations
- Identical training protocol to h-e1
- Log all hyperparameters

### NFR-2: Compute Budget
- ~79 GPU-hours (A100) for HotpotQA sweep
- h-e1 results already available

### NFR-3: Output Artifacts
- `results/h-c1_rank_sweep.csv`
- `results/h-c1_optimal_ranks.csv`
- `results/h-c1_scaling_fit.json`
- `results/h-c1_cross_task_comparison.json`
- `figures/h-c1_dual_scaling_plot.png`

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All 72 HotpotQA training runs complete | 100% |
| α_hotpot point estimate | 0 < α < 1 |
| Cross-task difference | |Δα| ≤ 0.15 |
| 95% CI overlap | Yes |

---

## Dependencies

### From h-e1
- `results/h-e1_scaling_fit.json` (required)
- LoRA training infrastructure
- Statistical analysis utilities

### New
- HotpotQA dataset loading
- Multi-document QA preprocessing
- Cross-task comparison module

---

## Ablation Studies

| Variant | Purpose |
|---------|---------|
| Distractor vs fullwiki | Check if IR noise affects α |
| Bridge vs comparison Qs | Check if question type affects α |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| h-e1 results unavailable | Verify h-e1 artifacts exist before starting |
| HotpotQA longer contexts | max_length=512, gradient checkpointing |
| Different optimal ranks | Expected - we're measuring α difference, not exact r_opt |

---

*Generated: 2026-08-24*
*Prerequisite: h-e1 (VALIDATED)*
