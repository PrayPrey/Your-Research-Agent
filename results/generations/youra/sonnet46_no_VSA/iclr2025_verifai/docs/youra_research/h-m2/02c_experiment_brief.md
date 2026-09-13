# Experiment Design: h-m2

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** ContractEval tasks stratified by postcondition complexity (AST-based: quantification, relational, structural tiers), if oracle-isolation gap is regressed on contract richness tier, then higher-richness contracts exhibit significantly larger oracle-isolation gaps (Spearman ρ ≥ 0.30, p < 0.05), because universal properties with more complex quantification are less exhaustively sampled by finite equality-based tests.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests whether oracle-isolation gap scales with contract richness tier. Gate: SHOULD_WORK (flat gradient is publishable negative result).

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (oracle-isolation gap = 0.4012, p = 5.88e-38; 10,432 triples evaluated)
**Gate Status:** SHOULD_WORK — failure does not stop pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED)

### Gate Condition
SHOULD_WORK — Spearman ρ ≥ 0.30 (p < 0.05) between AST-based contract richness tier and per-task oracle-isolation gap. Failure (ρ < 0.15) is a publishable negative finding that weakens but does not invalidate H-M1.

---

## Continuation Context

**CRITICAL: H-M2 is a post-hoc stratification analysis — NO new LLM inference required.**

H-M1 computed per-task oracle-isolation gaps for all 364 ContractEval tasks across 5 models. H-M2 uses those per-task mean gaps as the dependent variable and adds:
1. AST-based postcondition complexity scoring (new computation on ContractEval source)
2. Spearman ρ regression analysis

**Reused from H-M1:**
- Per-task mean oracle-isolation gap (DV): 364 values, one per task
- Dataset: ContractEval 364 tasks (same 0 quarantined)
- 5 model families, n=10 samples per task

**New computation:**
- AST complexity score per task postcondition (IV)
- Richness tier assignment (4 tiers: simple/structural/relational/compound)
- Spearman ρ test with bootstrap CI

### Previous Hypothesis Results
- H-M1 oracle-isolation gap = 0.4012 (threshold ≥ 0.10 ✅)
- Mean contract-unique mass = 0.4023
- Wilcoxon p = 5.88e-38 after Holm correction
- Gap consistent across models (0.40–0.41) and task types (HumanEval+ 0.52, MBPP+ 0.35)
- **Key insight:** HumanEval+ tasks show 17% larger gap than MBPP+ — hints at structural complexity gradient already present

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB status:** No domain-relevant results found. All 5 queries returned diffusers/HuggingFace image generation content (similarity < 0.41). The Archon KB does not contain entries on contract verification, AST complexity analysis, or LLM code benchmark evaluation. Experiment design proceeds from Exa GitHub findings and domain knowledge.

### Archon Code Examples

**Status:** No relevant code examples found in Archon KB. Standard Python `ast` module (stdlib) and `scipy.stats.spearmanr` are used — no KB examples required.

### Exa GitHub Implementations

**Query 1: ContractEval postcondition AST complexity analysis**

**Repository 1:** suhanmen/ContractEval (Official, ACL 2026)
- **URL:** https://github.com/suhanmen/ContractEval
- **Relevance:** The ground-truth benchmark. Contracts are Python `assert` statements inserted immediately after the function header. Each task has 1–N assert clauses. Structure is parseable via `ast.parse()`.
- **Key insight:** Contracts use `isinstance`, `len`, `set`, `all`/`any` — directly categorizable by AST node type
- **Used for:** Defining richness tier vocabulary and AST traversal target

**Repository 2:** MatureModel/PostcondGen
- **URL:** https://github.com/MatureModel/PostcondGen
- **Relevance:** Postcondition generation and evaluation on EvalPlus; shows postcondition categorization patterns
- **Used for:** Confirming postcondition category taxonomy

**Repository 3:** AmGarfield/OracleGap
- **URL:** https://github.com/AmGarfield/OracleGap
- **Relevance:** Oracle gap stratification framework; per-task gap analysis with selector comparison
- **Key pattern:** Per-task gap stored as JSON, joined with task metadata for stratified analysis
- **Used for:** Data structure design for per-task gap × richness join

**Query 2: Spearman correlation oracle gap stratification**

**Source 1:** scipy.stats.spearmanr (SciPy official docs)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Key:** For N=364, asymptotic p-value is reliable (>500 recommended for full accuracy; 364 borderline — permutation test recommended as verification)
- **Code:**
  ```python
  from scipy.stats import spearmanr, permutation_test
  res = spearmanr(richness_scores, gap_values, alternative='greater')
  # rho = res.statistic, p = res.pvalue
  # For exact p: permutation_test with permutation_type='pairings'
  ```

**Source 2:** AAAI 2024 — CIRS (Complexity-Impacted Reasoning Score)
- **URL:** https://ojs.aaai.org/index.php/AAAI/article/download/29721/31237
- **Relevance:** Uses AST to encode structural info + cyclomatic complexity for code complexity scoring; validated that AST node counts correlate with reasoning difficulty
- **Key insight:** `ast.walk()` over AST node types is the standard approach for structural complexity; `all`/`any` calls signal quantification

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

**This is not a paper reproduction experiment** — it is an analytical post-hoc study on existing H-M1 data. No author implementation to prioritize.

**Recommended Implementation Path:**
- Primary: Custom Python analysis script using `ast` (stdlib) + `scipy.stats.spearmanr`
- Fallback: `complexipy` library for cognitive complexity scoring as richness proxy (if AST-tier approach fails)
- Justification: Python `ast` is stdlib (no new dependencies), perfectly suited for parsing ContractEval's assertion-level contracts. `scipy` already required for H-M1 statistics.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. ContractEval uses standard Python `assert` statements as contracts; `ast` module handles parsing; `scipy.stats` handles Spearman ρ. No complex custom architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** ContractEval (HumanEval+/MBPP+ subset)
**Type:** standard (real, established benchmark — ACL 2026)
**Source:** https://github.com/suhanmen/ContractEval
**Size:** 364 tasks (258 HumanEval+ + 106 MBPP+), 0 quarantined
**Splits:** All 364 tasks used (no train/val split — statistical analysis task)

**For H-M2 specifically:**
- **Input DV:** Per-task mean oracle-isolation gap from H-M1 output (364 float values)
- **Input IV:** ContractEval postcondition text (Python assert clauses) for AST parsing
- **Task:** Compute richness tier per task → correlate with gap

**Loading Information** (for Phase 4 download):
- Method: git clone + JSON/Python file reading
- Identifier: `suhanmen/ContractEval` (GitHub)
- Code:
  ```python
  # Clone once: git clone https://github.com/suhanmen/ContractEval.git
  # Load task contracts:
  import json
  tasks = json.load(open("ContractEval/data/contracteval_tasks.json"))
  # Each task has: task_id, prompt, contract_assertions (list of assert strings)
  ```
- **Also load H-M1 results:** `h-m1/results/per_task_oracle_gap.json` (output of H-M1 experiment)

### Models

#### Baseline Model

**No ML model required** — this is a statistical analysis experiment.

**"Baseline" for comparison purposes:**
- Null hypothesis: Spearman ρ = 0 (no correlation between richness and gap)
- Flat model: mean oracle-isolation gap regardless of tier (grand mean = 0.4012 from H-M1)

**Loading Information** (for Phase 4 download):
- Method: No download required
- Identifier: N/A — uses H-M1 output data
- Code: `gaps = json.load(open("h-m1/results/per_task_oracle_gap.json"))`

#### Proposed Model

**Architecture:** AST-based Contract Richness Scorer + Spearman Correlation Analysis

**Integration:** Standalone analysis script; no ML model

**Core Mechanism Implementation:**

```python
# Core Mechanism: AST-based Contract Richness Scoring
# Based on: Python ast module (stdlib) + CIRS (AAAI 2024) AST node approach
# Ref: suhanmen/ContractEval contract structure (assert clauses)

import ast
from dataclasses import dataclass
from typing import List

@dataclass
class RichnessScore:
    task_id: str
    tier: int            # 1=simple, 2=structural, 3=relational, 4=compound
    score: float         # continuous AST complexity score
    has_quantifier: bool # any/all present
    has_relational: bool # multi-arg comparison, set ops
    node_count: int      # total AST nodes in all postconditions

def score_postcondition(assert_clauses: List[str]) -> RichnessScore:
    """
    Input: list of assert strings from ContractEval task
    Output: RichnessScore with tier assignment
    """
    total_nodes = 0
    has_quantifier = False
    has_relational = False

    for clause in assert_clauses:
        # Parse the assert expression (strip 'assert' keyword)
        expr = clause.lstrip("assert").strip()
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            continue

        # Walk AST and count node types
        for node in ast.walk(tree):
            total_nodes += 1
            # Quantification: any(), all() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("any", "all"):
                        has_quantifier = True
            # Relational: set ops, multi-comparison, isinstance chain
            if isinstance(node, ast.Compare) and len(node.ops) > 1:
                has_relational = True
            if isinstance(node, ast.BoolOp):  # and/or chains
                has_relational = True

    # Tier assignment (4-tier taxonomy)
    if has_quantifier:
        tier = 4 if has_relational else 3  # compound vs relational
    elif has_relational:
        tier = 2  # structural
    else:
        tier = 1  # simple equality/type checks

    score = total_nodes + (3 * has_quantifier) + (2 * has_relational)
    return RichnessScore(..., tier=tier, score=score,
                         has_quantifier=has_quantifier,
                         has_relational=has_relational,
                         node_count=total_nodes)

# Integration: runs on ContractEval task JSON, outputs richness_scores.json
```

### Training Protocol

**No training involved** — this is a statistical correlation analysis.

**Analysis Protocol:**

**Step 1: Data preparation**
- Load 364 per-task oracle-isolation gaps from H-M1 results
- Compute mean gap per task across all models × programs
- Load ContractEval task postconditions

**Step 2: Richness scoring**
- Apply `score_postcondition()` to all 364 tasks
- Assign richness tier (1–4) and continuous score

**Step 3: Statistical analysis**
```python
from scipy.stats import spearmanr, permutation_test
import numpy as np

richness_scores = [r.score for r in scored_tasks]
gap_values = [gaps[t.task_id] for t in scored_tasks]

# Primary test: Spearman ρ (continuous score vs gap)
res = spearmanr(richness_scores, gap_values, alternative='greater')
rho, p_asymptotic = res.statistic, res.pvalue

# Exact p-value via permutation (N=364, borderline for asymptotic accuracy)
def stat_fn(x):
    return spearmanr(x, gap_values).statistic
res_exact = permutation_test((richness_scores,), stat_fn,
                              permutation_type='pairings',
                              n_resamples=9999, alternative='greater')
p_exact = res_exact.pvalue

# Tier-level analysis: Kruskal-Wallis across 4 tiers
from scipy.stats import kruskal
tier_groups = [gaps_for_tier(t) for t in [1, 2, 3, 4]]
kw_stat, kw_p = kruskal(*tier_groups)
```

**Step 4: Bootstrap CI on ρ**
```python
# Bootstrap 95% CI on Spearman ρ
boot_rhos = []
rng = np.random.default_rng(42)
for _ in range(10000):
    idx = rng.integers(0, 364, size=364)
    boot_rhos.append(spearmanr(
        [richness_scores[i] for i in idx],
        [gap_values[i] for i in idx]
    ).statistic)
ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])
```

**Computational cost:** ~5 minutes (AST parsing + bootstrap 10k iterations on 364 tasks)

**Seeds:** 42 (fixed, for bootstrap and permutation test reproducibility)
- **Source:** Standard practice; scipy PermutationMethod seed convention

### Evaluation

**Primary Metric:** Spearman ρ between continuous AST richness score and per-task oracle-isolation gap
- **Success threshold:** ρ ≥ 0.30 with permutation p < 0.05 (one-sided, H1: ρ > 0)
- **Source:** Phase 2B H-M2 specification (02b_verification_plan.md)

**Secondary Metrics:**
1. Tier-level mean oracle-isolation gap (1 value per tier) — monotonic increase expected
2. Kruskal-Wallis H-test across 4 tiers (p < 0.05 indicates tier-level signal)
3. Contract-unique failure mass stratified by tier — expected: tier 3–4 higher than tier 1–2
4. Bootstrap 95% CI on ρ — report CI lower bound

**Expected Baseline Performance (from H-M1 + prior work):**
- Grand mean gap = 0.4012 (H-M1 validated)
- HumanEval+ gap (0.52) > MBPP+ gap (0.35) already suggests structural gradient exists
- Expected: tier 1 (simple) gap ~0.25–0.35; tier 4 (compound) gap ~0.50–0.65

**Flat Gradient Reporting:**
- IF ρ < 0.15: "Flat gradient — contracts uniformly encode difficult-to-test properties regardless of AST complexity"
- This is an honest negative finding; document as H-M2 FAIL (gate: SHOULD_WORK, non-blocking)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical correlation analysis
- Library: `scipy.stats` (spearmanr, kruskal, permutation_test), `numpy`, stdlib `ast`
- Code:
  ```python
  from scipy.stats import spearmanr, kruskal, permutation_test
  import ast
  import numpy as np
  # All stdlib or already-installed; no new pip installs needed
  ```

### Ablation Studies

**Ablation 1: Continuous score vs discrete tier**
- Compare ρ using continuous AST score vs 4-tier integer assignment
- Expected: continuous score gives stronger ρ (less information loss)
- Rationale: Validates tier taxonomy design

**Ablation 2: Per-model gap vs pooled mean gap**
- Run Spearman ρ separately for each of 5 model families
- Expected: ρ consistent across models (validates the mechanism is model-independent)

**Ablation 3: HumanEval+ vs MBPP+ subsets**
- Run analysis on 258 HumanEval+ tasks and 106 MBPP+ tasks separately
- Expected: HumanEval+ shows stronger ρ (more complex task distribution)

**Ablation 4: Node count only (no tier) as richness proxy**
- Replace full richness score with raw `ast.walk()` node count
- Expected: Similar ρ, validating that raw structural size also captures richness

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Spearman ρ (achieved vs threshold 0.30) and p-value

#### Additional Figures (LLM Autonomous)
Based on this hypothesis (contract richness gradient analysis), the following figures are most informative:

1. **Scatter plot:** Per-task AST richness score (x) vs oracle-isolation gap (y), color-coded by tier, with Spearman ρ annotated — PRIMARY FIGURE showing the gradient
2. **Box plot:** Oracle-isolation gap distribution per richness tier (tiers 1–4) — shows tier-level separation
3. **Heatmap:** Per-task richness tier × model family — shows whether richness effect is model-independent
4. **Violin plot:** Contract-unique failure mass by richness tier — secondary DV showing same gradient

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | ContractEval postconditions are parseable Python assert statements | TRUE — confirmed from suhanmen/ContractEval structure |
| Mechanism Isolatable | Per-task oracle-isolation gaps from H-M1 are available as input | TRUE — H-M1 validated, output available at `h-m1/results/` |
| Baseline Measurable | Null model (ρ = 0) and grand mean baseline are computable | TRUE — scipy.stats provides asymptotic and exact null distributions |

### Architecture Compatibility Check

**Required Components:**
- H-M1 output: `h-m1/results/per_task_oracle_gap.json` must exist with 364 task entries
- ContractEval repository: `suhanmen/ContractEval` cloned (contract assertions available)
- Python stdlib `ast` module: available in all Python 3.8+ environments
- `scipy >= 1.7.0`: required for `permutation_test` (added in SciPy 1.7)

**Incompatible Configurations:**
- H-M1 not completed: cannot proceed (per-task gaps unavailable)
- Quarantine > 50 tasks: reduces statistical power below useful threshold for ρ

> ⚠️ If H-M1 output missing, Phase 4 MUST fail early with clear error message!

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Richness scoring complete: N=364 tasks, tiers=[t1, t2, t3, t4]"` | `score_richness.py:main()` |
| Data Shape | `richness_df.shape == (364, 5)` — task_id, tier, score, has_quantifier, has_relational | `score_richness.py:build_df()` |
| Metric Delta | `tier4_mean_gap > tier1_mean_gap` (even if ρ < 0.30) | `analyze_correlation.py:tier_analysis()` |

**Activation Verification Code:**

```python
def verify_mechanism_activated(richness_df, gap_df, results):
    indicators = {
        "richness_computed": len(richness_df) == 364,
        "all_tiers_present": set(richness_df["tier"]) == {1, 2, 3, 4},
        "gap_loaded": len(gap_df) == 364,
        "gradient_direction": (
            gap_df[richness_df["tier"] == 4]["gap"].mean() >
            gap_df[richness_df["tier"] == 1]["gap"].mean()
        ),
        "spearman_computed": "rho" in results and "p_value" in results
    }
    passed = all(indicators.values())
    return passed, indicators

# Usage in Phase 4 experiment runner:
# passed, report = verify_mechanism_activated(richness_df, gap_df, results)
# if not passed: raise RuntimeError(f"Mechanism verification failed: {report}")
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| H-M1 output missing | FileNotFoundError on `per_task_oracle_gap.json` | FAIL EARLY: "Run H-M1 first" |
| All tasks same tier | `len(set(richness_df["tier"])) == 1` | FAIL: Richness taxonomy degenerate — check AST parser |
| ρ = NaN | `np.isnan(results["rho"])` | FAIL: Constant input — check gap values |
| Fewer than 300 valid tasks | `len(valid_tasks) < 300` | WARN: Report reduced N; proceed with warning |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all verify checks pass) | `verify_mechanism_activated()` |
| Gradient Direction | tier4_mean > tier1_mean | Tier-level analysis |
| Hypothesis Supported | Spearman ρ ≥ 0.30 AND permutation p < 0.05 (one-sided) | `scipy.stats.spearmanr` + `permutation_test` |
| Flat gradient reported | ρ < 0.15 explicitly documented | Negative finding section |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No domain-relevant results found in Archon KB (all results were diffusers/HuggingFace image generation content with similarity < 0.41). Three queries executed; zero matches in contract verification or code benchmark domains.

### B. GitHub Implementations (Exa)

**Repository 1:** suhanmen/ContractEval (Official — HIGHEST PRIORITY)
- **URL:** https://github.com/suhanmen/ContractEval
- **Query used:** "ContractEval postcondition AST complexity analysis Python GitHub"
- **Relevance:** Ground-truth benchmark; confirms contracts are Python assert statements parseable via `ast`
- **Architecture extracted:** Contract assertions inserted after function header as contiguous block; each is a valid Python expression
- **Used for:** Dataset loading design, AST parsing target definition

**Repository 2:** MatureModel/PostcondGen
- **URL:** https://github.com/MatureModel/PostcondGen
- **Query used:** Same as above
- **Relevance:** Postcondition evaluation on EvalPlus; confirms postcondition taxonomy approach
- **Used for:** Richness category taxonomy validation

**Repository 3:** AmGarfield/OracleGap
- **URL:** https://github.com/AmGarfield/OracleGap
- **Query used:** "Spearman correlation oracle gap stratification code benchmark"
- **Relevance:** Oracle gap analysis framework with per-task stratified analysis; shows how to join per-task gap data with metadata for stratification
- **Key pattern:** `registry.json` stores run provenance; per-task gap stored as float; joined with benchmark metadata
- **Used for:** Data pipeline design (per-task gap JSON + richness CSV join)

**Source 4:** scipy.stats.spearmanr (SciPy official documentation)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Query used:** "Spearman correlation oracle gap stratification code benchmark scipy"
- **Key insight:** For N=364 (borderline for asymptotic accuracy), permutation test recommended for exact p-value
- **Code extracted:**
  ```python
  from scipy.stats import spearmanr, permutation_test
  res = spearmanr(richness, gaps, alternative='greater')
  # permutation for exact p:
  res_exact = permutation_test((richness,), lambda x: spearmanr(x, gaps).statistic,
                                permutation_type='pairings', n_resamples=9999)
  ```
- **Used for:** Primary statistical test implementation

**Source 5:** AAAI 2024 — CIRS (Complexity-Impacted Reasoning Score)
- **URL:** https://ojs.aaai.org/index.php/AAAI/article/download/29721/31237
- **Query used:** "Python ast postcondition complexity score all any quantification"
- **Key insight:** AST structural encoding + cyclomatic complexity correlates with reasoning difficulty; validated that `any`/`all` nodes signal quantification complexity
- **Used for:** Richness scoring formula design (node count + quantification weight)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. ContractEval uses Python `assert` statements directly; `ast.parse()` and `ast.walk()` provide complete access to the expression structure. No custom layers or unfamiliar architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1
- **File:** `h-m1/04_validation.md`
- **Reused Components:**
  - Per-task oracle-isolation gaps (364 float values) — primary DV for H-M2
  - Dataset: ContractEval 364 tasks (0 quarantined) — same tasks, no new quarantine check needed
  - Model evaluation infrastructure — not reused (no new LLM inference in H-M2)
- **Why reused:** H-M2 is a mechanistic analysis of H-M1's outputs; reuse is mandatory (not a choice)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: ContractEval 364 tasks | GitHub (official) | Repo B.1 (suhanmen/ContractEval) |
| Per-task gap DV | H-M1 validation | D.1 (h-m1/04_validation.md) |
| AST richness scoring: `ast.walk()` | GitHub + AAAI paper | B.1, Source 5 (CIRS) |
| Quantifier detection: `any`/`all` | AAAI 2024 CIRS | Source 5 |
| Richness tier taxonomy (4-tier) | Phase 2B verification plan | 02b_verification_plan.md §H-M2 |
| Spearman ρ test | SciPy docs | Source 4 (scipy.stats.spearmanr) |
| Permutation p-value | SciPy docs | Source 4 (spearmanr N=364 note) |
| Bootstrap CI on ρ | Standard practice | Source 4 (numpy bootstrap) |
| Kruskal-Wallis tier test | Standard practice | scipy.stats.kruskal |
| Success threshold ρ ≥ 0.30 | Phase 2B | 02b_verification_plan.md §H-M2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in ```state block)
**Date:** 2026-08-03T00:00:00+00:00

### Workflow History for This Hypothesis
- H-M1 VALIDATED: oracle-isolation gap = 0.4012, contract-unique mass = 0.4023, 10,432 triples
- H-M2 set to IN_PROGRESS: 2026-08-03T15:07:33+00:00
- H-M2 experiment design: COMPLETED 2026-08-03

---

*MCP Tools Used: Archon (3 KB queries, 2 code queries — no domain matches), Exa (2 GitHub + 1 web search queries — high-relevance results)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
