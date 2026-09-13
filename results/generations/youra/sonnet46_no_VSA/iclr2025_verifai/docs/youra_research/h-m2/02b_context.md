# H-M2: Per-Hypothesis Context (JIT Generated from Phase 2B)

**Generated:** 2026-08-03
**Source:** 02b_verification_plan.md
**Hypothesis ID:** H-M2

---

## Hypothesis Information

**ID:** H-M2
**Type:** MECHANISM
**Gate:** SHOULD_WORK

**Statement:**
Under ContractEval's 364 tasks stratified by postcondition complexity (AST-based: quantification, relational, structural tiers), if oracle-isolation gap is regressed on contract richness tier, then higher-richness contracts exhibit significantly larger oracle-isolation gaps (Spearman ρ ≥ 0.30, p < 0.05), because universal properties with more complex quantification are less exhaustively sampled by finite equality-based tests.

**Rationale:**
This mechanistic step tests whether the oracle strength finding (H-M1) is explained by contract semantic complexity. A richness gradient validates the universal-property mechanism and strengthens the contribution. A flat gradient weakens the mechanism claim but does not invalidate the oracle-strength finding (H-M1 can still pass independently).

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ContractEval (HumanEval+/MBPP+ subset) | Same 364 tasks as H-M1; postcondition AST parsed for richness scoring; no new data required |
| **DV Input** | Per-task oracle-isolation gaps from H-M1 output | H-M2 is a post-hoc stratification analysis — reuses H-M1 per-task gap values as dependent variable |

**Dataset Details:**
- **Name:** ContractEval + H-M1 per-task oracle gap output
- **Type:** standard (real, established benchmark — ACL 2026)
- **Source:** github.com/suhanmen/ContractEval + `h-m1/results/per_task_oracle_gap.json`
- **Path:** 364 tasks (258 HumanEval+ + 106 MBPP+), 0 quarantined
- **Hypothesis Fit:** AST richness scoring requires only postcondition text (Python assert clauses), available directly from ContractEval source; per-task gaps already computed in H-M1

### Model Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Model** | No ML model — statistical analysis only | H-M2 adds AST-based richness scoring + Spearman correlation; no new LLM inference required |

**Analysis Details:**
- **Tools:** Python stdlib `ast` + `scipy.stats` (spearmanr, kruskal, permutation_test)
- **Input:** Per-task mean oracle-isolation gap (364 float values) from H-M1
- **New computation:** AST complexity score per task postcondition → 4-tier richness assignment → Spearman ρ regression

---

## Variables

- **IV:** Contract richness tier (AST-parsed: quantified/relational/structural complexity score; 4 tiers: simple/structural/relational/compound)
- **DV:** Per-task oracle-isolation gap (from H-M1 Experiment A; mean across 5 models × n=10 programs)
- **CV:** Same 364 tasks, same LLM programs evaluated in H-M1; no new evaluation

---

## Verification Protocol (from Phase 2B)

1. AST-parse all 364 ContractEval postconditions; categorize by complexity: simple (equality), structural (list/string predicates), relational (all/any quantification), compound (nested quantification).
2. Assign richness score per task (4-tier integer + continuous AST complexity metric: node_count + 3×has_quantifier + 2×has_relational).
3. Load per-task oracle-isolation gaps from `h-m1/results/per_task_oracle_gap.json`.
4. Spearman ρ test (continuous score vs gap); permutation test for exact p-value (N=364 borderline for asymptotic accuracy).
5. Kruskal-Wallis H-test across 4 richness tiers.
6. Bootstrap 95% CI on ρ (10,000 iterations, seed=42).
7. Report flat-gradient result honestly if ρ < 0.15.

---

## Success Criteria

- **Primary:** Spearman ρ ≥ 0.30 with permutation p < 0.05 (one-sided, H1: ρ > 0)
- **Secondary:** Higher-richness tier tasks show systematically larger contract-unique failure mass; tier 4 mean gap > tier 1 mean gap

---

## Failure Response

IF fails (ρ < 0.15) → EXPLORE: flat gradient is a publishable finding ("contracts uniformly encode difficult-to-test properties regardless of AST complexity"); document as H-M2 FAIL with gate status SHOULD_WORK (non-blocking). Does not invalidate H-M1.

---

## Dependencies

- **H-M1** (VALIDATED): Per-task oracle-isolation gaps (364 float values) required as dependent variable. H-M1 result: gap = 0.4012, p = 5.88e-38 (Holm-corrected Wilcoxon), 10,432 triples evaluated.

---

## Key Assumptions Relevant to H-M2

| ID | Assumption | Mitigation |
|----|------------|------------|
| A3 | EvalPlus static inputs mapped to ContractEval tasks (inherited from H-M1) | Already verified in H-M1 — no new check needed |
| A-M2 | ContractEval postconditions are valid Python assert statements parseable by stdlib `ast` | Confirmed from suhanmen/ContractEval structure; assert clauses inserted after function header as contiguous block |
| A-M2b | All 4 richness tiers are represented in the 364 tasks | Verify post-scoring: if any tier absent, AST taxonomy is degenerate — check parser |

---

## Baseline & Comparison Targets

- **Null model:** Spearman ρ = 0 (no correlation between richness and gap)
- **Flat baseline:** Grand mean oracle-isolation gap = 0.4012 (H-M1), independent of tier
- **Prior signal:** HumanEval+ gap (0.52) > MBPP+ gap (0.35) already hints at structural complexity gradient — H-M2 formalizes this signal
