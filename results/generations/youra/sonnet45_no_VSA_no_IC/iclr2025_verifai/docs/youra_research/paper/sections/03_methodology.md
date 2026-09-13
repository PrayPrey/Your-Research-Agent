# Methodology

Our mechanistic attribution approach tests the hypothesis that LLM advantage decomposes into distinct, quantifiable mechanisms via controlled ablation. We design five sub-hypotheses with falsification criteria: (H-E1) establish lean-auto baseline [10%, 25%], (H-M1) NL ablation drops success by ≥25pp, (H-M2) depth filtering drops success by ≥5pp, (H-M3) random Mathlib achieves 18-25%, (H-C1) tactic budget CV ≤ 100%. Each gate threshold enforces scientific rigor — effects below threshold reject the mechanistic claim.

## 3.1 Dataset and Evaluation Protocol

We use the **miniF2F Lean 4 test set** (N=244 Olympiad-level problems) with deterministic Lean 4 proof checker validation (binary outcome: valid/invalid). All experiments fix timeout=300s, Mathlib version (Lean 4 compatible), and evaluate on identical problem sets. Success rate is the primary metric (percentage of valid proofs); tactic count serves as a fairness control metric (H-C1).

The miniF2F Lean 4 subset provides three critical properties for mechanistic ablation: (1) **deterministic validation** — Lean proof checker eliminates custom extraction pipelines that confounded prior experiments (h-e1 failure in earlier work stemmed from 49.5% extraction accuracy, not prover capability), (2) **NL hint availability** — problems include informal docstrings/comments amenable to ablation, (3) **established difficulty** — Olympiad-level ensures non-trivial proof search (median depth=9 tactics in literature, challenging for automated provers).

## 3.2 H-E1: Baseline Measurement

**Objective:** Measure pure automated prover (lean-auto) success rate on miniF2F to establish reference for LLM comparison.

**Design:** Run lean-auto (Duper backend, deterministic hammer) on all N=244 problems with 300s timeout. Record success rate (primary), tactic count per solved problem (for H-C1), error sources (type elaboration failures, Mathlib API incompatibilities). Duper represents standard automated proving: breadth-first search over Mathlib premises, no LLM, no NL parsing.

**Predicted outcome:** 15% [10%, 25%] success rate, ~10 tactic evaluations per problem. Lower bound (10%) accounts for trivial problems solvable by `rfl` alone; upper bound (25%) conservative estimate for hammer capabilities.

**Fairness considerations:** Same Mathlib version as LLM configs, same timeout budget, no manual problem curation (full test set).

## 3.3 H-M1: Natural Language Understanding Mechanism

**Objective:** Test whether NL hint removal drops LLM success by ≥25pp (validates 60% contribution claim: 30pp / 50pp gap ≈ 60%).

**Design:** Controlled ablation with paired comparison. For each miniF2F problem, create two variants: (1) **NL-intact** — original formal statement + docstring/comment hints (e.g., `-- For all prime p, prove property X`), (2) **NL-ablated** — same formal statement, all docstrings/comments stripped. Run LLM on both variants, measure success drop via McNemar paired test (controls for problem difficulty). Gate threshold: Δ ≥ 25pp AND p < 0.05.

**Rationale:** NL ablation isolates linguistic contribution by eliminating natural language signals (docstrings like "for all prime p" → Nat.Prime lemmas) while preserving formal type signatures. If LLMs rely on NL understanding, success should drop significantly. If LLMs exploit only formal patterns, NL removal has minimal effect.

**Alternatives considered:** Paraphrase NL hints (tests semantic vs syntactic understanding) deferred to future work; removal gives cleaner attribution for first-order mechanism validation.

**Predicted outcome:** Baseline (NL-intact) 65%, ablated 35%, Δ=30pp [25%, 35%]. Large effect size (Cohen's h ≈ 0.6) expected from linguistic pattern matching (e.g., "injective" text → `Function.Injective` tactics).

## 3.4 H-M2: Proof Depth Mechanism

**Objective:** Test whether proof depth filtering (≤3 tactics) drops LLM success by ≥5pp (validates 30% contribution claim: 15pp / 50pp ≈ 30%).

**Design:** Post-hoc filtering on LLM-solved problems. Measure success rate on: (1) **full dataset** — all solved problems regardless of tactic count, (2) **shallow subset** — only problems solvable with ≤3 tactics. Compute Δ via McNemar test (paired comparison: same problem, stratified by depth). Gate threshold: Δ ≥ 5pp (lower than H-M1's 25pp due to expected smaller effect).

**Rationale:** Proof depth filtering tests whether long-range context contributes to LLM advantage. Olympiad problems require multi-step reasoning (median=9 tactics in literature); if LLMs exploit context maintenance across steps, filtering to shallow proofs (≤3 tactics, typical hammer depth limit) should drop success significantly. Post-hoc filtering avoids confounding LLM training (depth penalties change search dynamics).

**Alternatives considered:** Train LLM with depth constraint (rejected — tests "LLM with depth limit" not "depth contribution to vanilla LLM"), explicit depth penalty (rejected — changes search strategy).

**Predicted outcome:** Full success 65%, shallow success 50%, Δ=15pp [5%, 30%]. Effect arises from problems requiring backtracking across 5-10 tactic steps (LLM strength, hammer timeout).

## 3.5 H-M3: Corpus Pattern Matching Mechanism

**Objective:** Test whether random Mathlib tactic sampling achieves 18-25% (Δ=3-10pp above lean-auto baseline, validates 10% contribution).

**Design:** Random sampler draws tactics from Mathlib corpus with human distribution frequency (e.g., `simp` appears 40%, `rw` 25%, `exact` 15% in training proofs). For each problem, sample tactics uniformly from distribution until timeout or success. Compare random sampler success vs lean-auto baseline (H-E1: 15.6%). Gate threshold: success ∈ [18%, 25%].

**Rationale:** If LLMs learn which tactics frequently succeed together from Mathlib training data (corpus pattern matching), random sampling from the same distribution provides stochastic baseline. Exceeding lean-auto by 3-10pp suggests corpus frequency signals contribute, but remaining gap (random 20% → LLM 65%) requires semantic understanding.

**Predicted outcome:** Random Mathlib 20% [18%, 25%], Δ=+5pp [+3%, +10%] vs lean-auto. Effect arises from implicit heuristics in human proof distributions (humans apply `simp` more often than `sorry`, random sampling inherits this bias).

## 3.6 H-C1: Tactic Budget Control

**Objective:** Validate tactic evaluation count as fairness metric for LLM vs automated prover comparison (CV ≤ 100%).

**Design:** Post-hoc analysis on H-E1 (lean-auto) solved problems. Extract tactic count per solved proof, compute coefficient of variation CV = σ / μ. If CV << 1.0, tactic count is stable metric (low variance). Recommend budget = μ + 1σ for future experiments (captures ~90% of baseline strategies without excluding valid deep proofs).

**Rationale:** Fair LLM vs automated prover comparison requires controlling computational confounds — LLMs might appear better by evaluating more tactics (computational advantage) rather than smarter search (algorithmic advantage). Tactic budget equalization isolates algorithmic differences. Low CV validates tactic count as stable control variable.

**Predicted outcome:** Mean tactic count μ=10, σ=4, CV=0.40 << 1.0. Recommended budget=15 (μ+1σ) for H-M1/M2/M3 LLM experiments.

## 3.7 Statistical Analysis

**Paired comparisons (H-M1, H-M2):** McNemar test for correlated binary outcomes (same problem, two conditions). Reports χ² statistic, p-value, 95% confidence interval via bootstrap (10,000 resamples). Effect size: Cohen's h for proportions.

**Independent comparisons (H-M3 vs H-E1):** Chi-squared test for two independent proportions. Reports p-value, 95% CI for difference.

**Gate decisions:** Mechanistic hypothesis PASS if effect exceeds threshold AND p < 0.05. FAIL if effect below threshold (regardless of significance). Example: H-M2 Δ=3.7% < 5% → FAIL even though p=0.0027 (statistically significant but effect too small to validate 30% contribution claim).

All experiments use α=0.05 significance level, two-tailed tests. Confidence intervals computed via bias-corrected bootstrap (BCa method).
