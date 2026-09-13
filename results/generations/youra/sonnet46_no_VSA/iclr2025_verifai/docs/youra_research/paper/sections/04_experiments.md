# 4. Experimental Setup

We design four experiments to answer the following research questions:

**RQ1:** Does the execution-based contract oracle exceed the differential oracle on contract-violating inputs? (Experiment A — oracle isolation)

**RQ2:** Does adaptive PBT find additional violations beyond static CVT oracle inputs? (Experiment B — adaptive contribution)

**RQ3:** Does contract richness (AST-based tier) predict oracle-isolation gap magnitude? (Experiment C — mechanism gradient)

**RQ4:** Are model rankings on contract satisfaction orthogonal to pass@1*? (Experiment D — cross-model orthogonality)

Each RQ maps directly to a claim from the Introduction: RQ1 to the 40% oracle gap, RQ2 to the ~10pp adaptive contribution, RQ3 to the mechanism gradient, and RQ4 to the cross-model claim.

## 4.1 Dataset

All experiments use ContractEval [Lim2025ContractEval], comprising 364 tasks from HumanEval+ (117 tasks) and MBPP+ (247 tasks) with Python inline `assert` pre/post-condition contracts. We use the full benchmark without subsampling. Contract soundness was verified by a pre-check running Hypothesis PBT against reference implementations; zero tasks were quarantined.

| Dataset Component | Description | Size |
|------------------|-------------|------|
| ContractEval tasks | HumanEval+/MBPP+ with contracts | 364 |
| CVT inputs per task | Contract-violating test inputs | avg ~5/task |
| EvalPlus static inputs per task | base + plus inputs | 764/task |
| Total oracle evaluation triples | tasks × models × programs | 10,432 (3 models complete) |

## 4.2 Models

We evaluate five model families spanning open/closed architectures and a 7–34B parameter range:

| Model | Type | Parameters | API/Backend |
|-------|------|------------|-------------|
| GPT-4o-mini | Closed | ~8B equiv | OpenAI API |
| Claude-3-Haiku | Closed | ~7B equiv | Anthropic API |
| DeepSeek-Coder-V2-Lite | Open | 16B | vLLM |
| CodeLlama-13B-Instruct | Open | 13B | HuggingFace |
| CodeLlama-34B-Instruct | Open | 34B | HuggingFace |

Code samples (n=10 per model per task) are sourced from the evalplus generation corpus and filtered to test-passing programs only.

## 4.3 Baselines

We compare against the following oracle types, chosen to span the evaluation oracle design space:

**EvalPlus differential oracle [Liu2023EvalPlus]:** Ground-truth output equality on 764 static inputs per task. This is the strongest published test-based oracle; serves as the primary baseline for Experiment A.
*Why included:* State-of-the-art dense test evaluation; must beat this to demonstrate oracle-strength contribution.

**Static CVT contract oracle (Experiment A):** Reference contract executed on CVT inputs using output equality for Oracle A and contract assertion firing for Oracle B.
*Why included:* Isolates oracle semantic strength from adaptive input exploration.

**Adaptive PBT contract oracle (Experiment B):** icontract-hypothesis with 5,000 examples per triple; provides the adaptive input exploration component.
*Why included:* Measures search contribution beyond static oracle.

## 4.4 Implementation Details

**Oracle evaluation:** Dual-oracle harness with 8-process multiprocessing pool. Per-input timeout: 5s; per-program timeout: 10s. Results streamed to JSONL incrementally.

**Adaptive PBT:** icontract-hypothesis v3.x; 5,000 examples per triple; SIGALRM-based timeout of 30s per triple. Strategy inference from inline `assert` preconditions.

**Richness scoring:** AST parsing of contract clauses extracted via `# $_CONTRACT_$` marker; 4-tier scoring based on presence of BoolOp and `any()`/`all()` constructs.

**Mixed linear model (Experiment D):** `statsmodels.formula.api.mixedlm` with powell convergence; `scipy.stats.permutation_test` (type='pairings', n=10,000 bootstrap) for τ significance; 10,000-sample bootstrap CI for all aggregate metrics.

**Compute:** All experiments run on CPU (statistical analysis); oracle evaluation on an 8-core server; total experiment runtime < 8 hours across all 4 experiments.

## 4.5 Evaluation Metrics

| Metric | Definition | Experiment |
|--------|------------|------------|
| Oracle-isolation gap | mean(contract failure rate) − mean(differential failure rate) on CVT inputs | A |
| Contract-unique (CU) mass | Fraction of triples: Oracle A=PASS, Oracle B=FAIL | A |
| Wilcoxon p-value | Two-sided signed-rank test on per-task gap; Holm-corrected | A |
| Adaptive contribution | PBT failure rate − static CVT failure rate per triple | B |
| Spearman ρ | Rank correlation: richness tier vs. oracle gap per task | C |
| Kendall τ | Rank correlation: contract satisfaction vs. pass@1* across models | D |
| Partial ΔR² | Additional variance explained by model identity beyond pass@1* + log(size) | D |

Statistical significance threshold: p < 0.05 throughout (p < 0.01 for primary gate metrics).
