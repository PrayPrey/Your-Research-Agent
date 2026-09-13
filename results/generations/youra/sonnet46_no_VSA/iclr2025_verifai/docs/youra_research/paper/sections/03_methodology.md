# 3. Methodology

Building on the insight that oracle semantics must be decoupled from input strategy, we design a dual-experiment framework to measure contract oracle strength independently and then quantify adaptive PBT's additional contribution. The framework operates on ContractEval's 364 HumanEval+/MBPP+ tasks across 5 LLM families.

## 3.1 Overview

Our methodology separates two sources of potential oracle advantage:

1. **Oracle semantic strength** — the contract oracle detects violations that the differential oracle *cannot* by construction, regardless of inputs used.
2. **Input exploration advantage** — adaptive PBT explores more of the input space than static test sets, finding violations of either oracle type.

We quantify (1) via **Experiment A** (oracle isolation) and (2) via **Experiment B** (adaptive PBT contribution beyond Experiment A). This decomposition allows us to attribute observed gaps to oracle type rather than input-generation differences.

## 3.2 Dataset: ContractEval

ContractEval [Lim2025ContractEval] provides 364 tasks from HumanEval+ and MBPP+ augmented with Python inline `assert` pre/post-conditions written by domain experts. Each task includes:
- A canonical solution with embedded contract assertions (`canonical_solution_with_contract`)
- Contract-violating test inputs (CVT inputs) — inputs specifically designed to trigger contract violations, averaging ~5 per task
- EvalPlus test inputs (764 per task via `base_input` + `plus_input`)

We scope all experiments to the 364 tasks with contract annotations. Tasks where soundness pre-check identifies reference contract violations are quarantined; in practice, zero tasks were quarantined, confirming approximate contract soundness.

## 3.3 LLM Corpus

We evaluate 5 model families representing diverse architectural and capability ranges:
- **Closed-source:** GPT-4o-mini, Claude-3-Haiku
- **Open-source:** DeepSeek-Coder-V2-Lite (16B), CodeLlama-13B, CodeLlama-34B

Code samples (n=10 per model per task) are drawn from the evalplus generation corpus [Liu2023EvalPlus], filtered to test-passing programs only (programs that pass all base EvalPlus unit tests).

## 3.4 Experiment A: Oracle Isolation via CVT Inputs

**Rationale:** ContractEval's inline `assert` contracts are precondition checks that fire only on invalid inputs. EvalPlus's 764 static inputs are valid by construction — running the contract oracle on them produces zero contract violations (preconditions pass trivially). To create a fair oracle comparison, we use CVT inputs as the controlled fixed input set.

**Design:**

- **Input set:** ContractEval CVT inputs per task (avg ~5 per task, fixed across all models)
- **Oracle A (differential):** For each (CVT input x, LLM program p), evaluate whether p(x) ≠ gt_plain(x), where gt_plain is the canonical solution *without* contract assertions. Returns FAIL if output differs from reference.
- **Oracle B (contract):** Execute canonical_solution_with_contract(x). Returns FAIL if an `AssertionError` is raised — the contract identifies x as violating a pre/post-condition.
- **Contract-unique (CU) classification:** A triple (x, p) is contract-unique if Oracle A returns PASS (p(x) = gt_plain(x)) but Oracle B returns FAIL (contract fires). This is the core measure of oracle semantic strength: the LLM returns the "correct" output, but the contract identifies the behavior as semantically wrong.

**Oracle isolation gap** = mean(Oracle B failure rate) − mean(Oracle A failure rate) over all (task, model, program) triples.

**Statistical test:** Wilcoxon signed-rank test on per-task oracle gap values, with Holm correction for multiple comparisons. Significance threshold: p < 0.01.

**Implementation:** Dual-oracle harness executed with 8-process multiprocessing pool. Execution timeout: 5s per input, 10s per program. Results streamed to JSONL for crash resilience.

## 3.5 Experiment B: Adaptive PBT Contribution

**Rationale:** Beyond the oracle semantic gap measured on static CVT inputs, adaptive property-based testing can explore additional input regions that static inputs do not cover. We measure this contribution as the *additional* violations found by adaptive PBT over static CVT oracle results.

**Design:**

- **Tool:** `icontract_hypothesis` — a library that infers Hypothesis search strategies from icontract-decorated function signatures, adapted to infer strategies from ContractEval's inline `assert` preconditions.
- **Budget:** 5,000 examples per (task, model, program) triple; 30s SIGALRM timeout per triple.
- **Adaptive contribution** per triple = PBT failure rate − static CVT failure rate (for the same program).
- **Aggregation:** Per-task mean adaptive contribution; Wilcoxon signed-rank test over tasks for statistical significance; 10,000-sample bootstrap CI.

**Compatibility:** icontract-hypothesis wrapping succeeds for 94.6% of triples (17,226/18,200); 5.4% errors from decorator wrapping incompatibility or timeout are excluded from contribution analysis.

## 3.6 Contract Richness Analysis (Experiment C)

**Rationale:** We hypothesize that richer contracts (encoding more complex universal properties) produce larger oracle gaps. To test this, we assign each task a 4-tier AST-based richness score.

**Tier system:**
| Tier | Name | AST Marker | Example |
|------|------|------------|---------|
| 1 | Simple | No BoolOp, any/all | `assert x > 0` |
| 2 | Structural | BoolOp chaining | `assert x > 0 and len(x) > 0` |
| 3 | Relational | `any()`/`all()` quantification | `assert all(y >= 0 for y in result)` |
| 4 | Compound | Both BoolOp and any/all | `assert all(a in b for a, b in pairs) and len(pairs) > 0` |

We compute Spearman rank correlation between richness tier and oracle-isolation gap per task, with 10,000-sample bootstrap CI and permutation test for significance.

## 3.7 Cross-Model Analysis (Experiment D)

**Rationale:** If contracts measure a qualitatively different property than pass@1*, model rankings on contract satisfaction should differ from pass@1* rankings.

**Design:**
- Compute per-model mean contract satisfaction rate (fraction of test-passing programs satisfying all contracts under adaptive PBT).
- Compute Kendall τ between contract-satisfaction ranking and published pass@1* rankings.
- Fit mixed linear model: `contract_rate ~ pass@1* + log(model_size) + model_type + model_id`, reporting partial ΔR² for model identity.
- Permutation test (type: pairings, n=10,000 bootstrap) for τ significance.

**Statistical note:** At n=5 models, the exact permutation test on Kendall τ has a structural minimum achievable p ≈ 0.017 (at |τ| = 1.0 only) for a two-sided test. Any τ < 1.0 is structurally unprovable significant at α = 0.05 with n=5. We report this constraint explicitly.

## 3.8 Connection to Narrative

The methodology is structured around the central insight: contracts are not just more tests — they are a different *kind* of oracle. Experiment A proves this directly by showing that differential and contract oracles disagree on 40% of evaluations even when given identical inputs. Experiment B shows that adaptive search adds a further independent layer of detection. Experiments C and D probe the mechanism and generalizability of the gap. Together, they build the evidence chain from existence (h-e1), to oracle strength (h-m1), to search contribution (h-m3), to richness mechanism (h-m2), to cross-model scope (h-m4).
