# Phase 2A COMPLETE — H-C_p-v10 (Consensus Similarity → pass@k)

**Date:** 2026-03-20
**Pipeline:** Anonymous Pipeline: Solution consensus convergence as pass@k predictor
**Archon Project ID:** 61a1fc7c-30fc-4622-a9d9-3289cad6e6a2
**Pipeline Phase 2A Task:** d935d076 → done
**Research Folder:** docs/youra_research/20260316_verifia/

## Hypothesis Generated: H-C_p-v10

**Core Claim:** Mean pairwise normalized Levenshtein similarity C_p ∈ [0,1] among k=5 pre-execution LLM-generated code solutions positively predicts pass@k on EvalPlus (HumanEval+ 164 probs, MBPP+ 378 probs) via Spearman correlation, holding beyond first-attempt success (pass@1) in a LOO-decoupled mixed-effects model.

**Mechanism:** Distributional concentration in code-space — concentrated distributions → correct approaches; dispersed → uncertainty/failure. Code-space analog of Wang et al. 2022 self-consistency.

## Sub-Hypotheses (5)

| ID | Description | Gate | Threshold |
|----|-------------|------|-----------|
| H-E1 | C_p non-degenerate: IQR > 0.05, mean ∈ (0.05, 0.95) | MUST_WORK | ≥4/5 pairs |
| H-E2 | Spearman rho(C_p, pass@k) ≥ 0.10, bootstrap p < 0.05 | MUST_WORK | ≥3/5 pairs |
| H-M1 | LOO-decoupled mixed-effects: β > 0, ΔR² ≥ 0.02 | MUST_WORK | ≥3/5 pairs |
| H-M2 | Cross-model positive rho direction | MUST_WORK | ≥4/5 pairs |
| H-M3 | soft_pass@k rho differential ≥ 0.05 | SHOULD_WORK | ≥3/5 pairs |

**Dependency:** H-E1 → H-E2 → {H-M1, H-M2, H-M3}

## Key Refinements from Discussion (16 exchanges, converged)

- **LOO decoupling mandatory for H-M1**: C_p from k-1=4 solutions, pass@k from held-out solution
- **Mixed-effects model**: pass@k ~ C_p_LOO + pass@1 + (1|problem) + (1|model), ΔR² ≥ 0.02
- **Language precision**: "orthogonal to first-attempt success (pass@1)" not "intrinsic difficulty"
- **Two-tier cross-model stability**: ≥0.30 rho = correlated, ≥0.50 = structural property
- **AST sensitivity required**: report rank correlation between AST-normalized and raw Levenshtein C_p
- **Template dominance acknowledged**: competing mechanism, tested via H-M2 cross-model consistency
- **Three contribution layers**: Layer 1 (rho > 0) alone publishable; Layers 1+2 = strong paper

## Models & Data

- **5 pairs**: LLaMA3-8B × {HumanEval+, MBPP+}, DeepSeek-6.7B × {HumanEval+, MBPP+}, CodeLlama-7B × MBPP+
- **Data**: B_p matrices from h-m1/results/ + EvalPlus generation outputs (existing, no new inference)
- **Bootstrap**: n=1000, seed=42

## Output Files

- `discussion_log.md` — 16-exchange transcript (52KB)
- `03_refinement.yaml` — Primary Phase 2B input (29KB)
- `02_synthesis.yaml` — Synthesis details (9KB)
- `01_round_table/final_opinions.yaml` — 6 agent assessments (8KB)
- `03_refinement.md` — Human-readable summary (6KB)

## Next Phase

Phase 2B: `phase2b-planning` — Decompose H-C_p-v10 into verification sub-hypotheses roadmap.
