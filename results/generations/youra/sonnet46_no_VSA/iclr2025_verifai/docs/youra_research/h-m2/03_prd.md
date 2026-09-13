# PRD: h-m2 — Contract Richness Stratification Analysis

**stepsCompleted:** [PRD]
**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM (INCREMENTAL from h-m1)
**date:** 2026-08-03
**tier:** FULL

---

## Executive Summary

H-M2 is a post-hoc stratification analysis examining whether the oracle-isolation gap discovered in H-M1 (gap = 0.4012) scales with the structural complexity of ContractEval postconditions. The experiment computes AST-based richness tiers for 364 ContractEval tasks and tests whether richer contracts exhibit significantly larger oracle-isolation gaps (Spearman ρ ≥ 0.30, p < 0.05). **No new LLM inference is required** — all evaluation data is reused from H-M1.

---

## Problem Statement

H-M1 validated a large oracle-isolation gap (0.4012) across all ContractEval tasks, but treated all contracts uniformly. H-M2 asks: does the gap arise more strongly when postconditions contain richer universal properties (quantification, relational operators), or is the gap flat across structural complexity levels? The mechanism hypothesis is that contracts encoding harder-to-test universal properties (e.g., `all(...)`, chained comparisons) will show larger oracle-isolation gaps than simple equality/type-check contracts.

---

## Functional Requirements

### FR-1: Data Loading
- Load 364 per-task oracle-isolation gaps from `h-m1/results/per_task_oracle_gap.json`
- Load ContractEval task postcondition text from `ContractEval/data/contracteval_tasks.json`
- Validate: exactly 364 tasks, 0 quarantined, all task IDs match between sources
- **Fail early** if `per_task_oracle_gap.json` is missing: "Run H-M1 first"

### FR-2: AST-Based Richness Scoring
- Parse each task's postcondition assert clauses via `ast.parse()` (Python stdlib)
- Walk AST nodes to detect:
  - **Quantification:** `any()` / `all()` calls → `has_quantifier = True`
  - **Relational:** multi-arg `Compare` nodes, `BoolOp` chains → `has_relational = True`
  - **Node count:** total AST nodes across all assert clauses
- Assign 4-tier richness tier:
  - Tier 1 (simple): no quantifier, no relational
  - Tier 2 (structural): relational only
  - Tier 3 (relational): quantifier only
  - Tier 4 (compound): quantifier + relational
- Compute continuous richness score: `node_count + 3 * has_quantifier + 2 * has_relational`
- Output: `richness_df` with columns [task_id, tier, score, has_quantifier, has_relational, node_count]
- Validate: `richness_df.shape == (364, 6)`, all 4 tiers present

### FR-3: Primary Statistical Test
- Compute Spearman ρ between continuous richness score and per-task oracle-isolation gap (one-sided, H1: ρ > 0) using `scipy.stats.spearmanr`
- Compute exact p-value via permutation test (9999 resamples, `permutation_type='pairings'`, seed=42) using `scipy.stats.permutation_test`
- Compute Bootstrap 95% CI on ρ (10000 iterations, seed=42) using `numpy`
- Compute Kruskal-Wallis H-test across 4 richness tiers using `scipy.stats.kruskal`
- Report: ρ, p_asymptotic, p_exact, CI_lower, CI_upper, KW_stat, KW_p

### FR-4: Ablation Studies
- **Ablation 1:** Continuous score vs discrete tier — run Spearman ρ with integer tier as IV
- **Ablation 2:** Per-model gap — run ρ separately for each of 5 model families
- **Ablation 3:** Subset analysis — run on 258 HumanEval+ tasks and 106 MBPP+ tasks separately
- **Ablation 4:** Node count only — replace full richness score with raw node count as IV

### FR-5: Mechanism Verification
- Run `verify_mechanism_activated(richness_df, gap_df, results)` and assert all indicators pass
- Indicators: richness_computed (N=364), all_tiers_present ({1,2,3,4}), gap_loaded (N=364), gradient_direction (tier4_mean > tier1_mean), spearman_computed
- Log tier distribution: `"Richness scoring complete: N=364 tasks, tiers=[t1, t2, t3, t4]"`

### FR-6: Visualization
- **Required figure:** Bar chart — Spearman ρ achieved vs threshold (0.30), with p-value annotation
- **Figure 1:** Scatter plot — per-task richness score (x) vs oracle-isolation gap (y), colored by tier, with ρ annotated
- **Figure 2:** Box plot — oracle-isolation gap distribution per richness tier (tiers 1–4)
- **Figure 3:** Heatmap — per-task richness tier × model family gap matrix
- **Figure 4:** Violin plot — contract-unique failure mass by richness tier
- All figures saved to `h-m2/figures/`

### FR-7: Results Reporting
- Structured JSON output: `h-m2/results/h_m2_results.json`
- Richness scores CSV: `h-m2/results/richness_scores.csv`
- Flat gradient detection: if ρ < 0.15, output "FLAT_GRADIENT" flag with documentation

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed at 42 (bootstrap + permutation test)
- Results deterministic across runs

### NFR-2: Performance
- Full analysis completes in < 10 minutes on standard CPU (AST parsing + 10k bootstrap on 364 tasks is lightweight)

### NFR-3: Dependency Constraints
- **No new ML libraries required**
- Required: `scipy >= 1.7.0` (for `permutation_test`), `numpy`, `matplotlib`, `pandas`
- All packages already installed from H-M1 environment

### NFR-4: Error Handling
- Fail early if H-M1 output missing with actionable error
- Warn (not fail) if fewer than 300 valid tasks
- Handle `SyntaxError` on malformed assert clauses gracefully (skip clause, log)
- Fail if ρ = NaN (constant input detected)

---

## Data Specification

### 4.1 Primary Input: H-M1 Per-Task Gaps
- **Source:** `h-m1/results/per_task_oracle_gap.json`
- **Format:** `{task_id: float}` — 364 entries
- **Loading:** `gaps = json.load(open("h-m1/results/per_task_oracle_gap.json"))`
- **Auto-available:** Yes (H-M1 validated; no download needed)

### 4.2 Secondary Input: ContractEval Task Postconditions
- **Source:** `suhanmen/ContractEval` GitHub repository
- **Clone:** `git clone https://github.com/suhanmen/ContractEval.git`
- **Format:** `contracteval_tasks.json` — each entry has `task_id`, `contract_assertions` (list of assert strings)
- **Size:** 364 tasks (258 HumanEval+ + 106 MBPP+)
- **Manual download required:** YES (git clone)

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 5 verify checks pass | `verify_mechanism_activated()` |
| Gradient Direction | tier4_mean_gap > tier1_mean_gap | Tier-level analysis |
| **GATE: Hypothesis Supported** | Spearman ρ ≥ 0.30 AND permutation p < 0.05 (one-sided) | Primary test |
| Flat gradient documented | ρ < 0.15 → explicit FLAT_GRADIENT report | Negative finding |

**Gate type:** SHOULD_WORK — failure (ρ < 0.15) is a publishable negative finding, non-blocking for pipeline.

---

## Dependencies

### 7.1 Python Packages
```
scipy>=1.7.0
numpy
matplotlib
seaborn
pandas
```

### 7.2 External Repositories
- `suhanmen/ContractEval` — manual git clone required

### 7.3 Internal Dependencies
- `h-m1/results/per_task_oracle_gap.json` — MUST exist (H-M1 completed)
- H-M1 code infrastructure — NOT reused (H-M2 is pure analysis script)

---

## Architecture Notes

H-M2 is a **standalone analysis script**, not a training pipeline. The implementation consists of:
1. `score_richness.py` — AST scoring module
2. `analyze_correlation.py` — Spearman ρ + Kruskal-Wallis + ablations
3. `visualize.py` — Figure generation
4. `run_h_m2.py` — Orchestrator script

All outputs written to `h-m2/results/` and `h-m2/figures/`.
