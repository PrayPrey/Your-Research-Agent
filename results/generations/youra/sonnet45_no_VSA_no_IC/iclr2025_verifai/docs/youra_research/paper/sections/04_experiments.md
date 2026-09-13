# Experimental Setup

We evaluate five sub-hypotheses (H-E1 baseline, H-M1 NL mechanism, H-M2 depth mechanism, H-M3 corpus mechanism, H-C1 tactic budget control) on miniF2F Lean 4 test set (N=244 Olympiad-level problems). All experiments use Lean 4 proof checker for deterministic validation, 300s timeout, and identical Mathlib version.

## 4.1 Baseline Configuration (H-E1)

**Prover:** lean-auto with Duper backend (deterministic hammer, breadth-first search over Mathlib premises)  
**Dataset:** miniF2F Lean 4 test set (N=244)  
**Timeout:** 300s per problem  
**Metrics:** Success rate (primary), tactic count per solved problem (for H-C1 analysis), error classification (type elaboration vs Mathlib API)

**Experimental questions:**
- What is pure automated prover baseline success rate on miniF2F?
- How many tactic evaluations do solved problems require?
- What error sources affect Lean 3→4 ported problems?

**Expected outcome:** 15% [10%, 25%] success, ~10 tactic evaluations/problem, <5% error rate.

## 4.2 NL Understanding Ablation (H-M1)

**Design:** Paired comparison with NL-intact vs NL-ablated variants  
**NL ablation method:** Strip all docstrings and inline comments preserving formal statement structure  
**Dataset:** miniF2F Lean 4 test set (N=244), both variants  
**LLM configuration:** LeanCopilot @32 sampling budget, 300s timeout  
**Statistical test:** McNemar χ² for paired binary outcomes, bootstrap 95% CI  
**Gate criterion:** Δ ≥ 25pp AND p < 0.05

**Experimental question:** Does removing natural language hints drop LLM success by ≥25pp, validating ~60% contribution to LLM advantage?

**Baseline vs ablated comparison:**
| Variant | NL Hints | Expected Success |
|---------|----------|------------------|
| NL-intact | Yes (original docstrings/comments) | 65% |
| NL-ablated | No (stripped, formal statement only) | 35% |
| **Δ (effect size)** | — | **30pp [25%, 35%]** |

**Example ablation:**
```lean
-- Before (NL-intact):
-- For all prime p, prove p² - 1 is divisible by 24
theorem prime_square_div (p : ℕ) (hp : Nat.Prime p) : ...

-- After (NL-ablated):
theorem prime_square_div (p : ℕ) (hp : Nat.Prime p) : ...
```

LLM loses linguistic hint "for all prime p" → `Nat.Prime` lemma suggestion pathway.

## 4.3 Proof Depth Filtering (H-M2)

**Design:** Post-hoc stratification by tactic count  
**Stratification:** Full dataset (all depths) vs Shallow subset (≤3 tactics)  
**Dataset:** LLM-solved problems from H-M1 (NL-intact variant)  
**Depth threshold:** 3 tactics (typical automated prover depth limit before timeout)  
**Statistical test:** McNemar χ² for paired comparison (same problem, different depth strata)  
**Gate criterion:** Δ ≥ 5pp AND p < 0.05

**Experimental question:** Does filtering to shallow proofs (≤3 tactics) drop LLM success by ≥5pp, validating proof depth as LLM-specific advantage?

**Stratified comparison:**
| Stratum | Depth Constraint | Expected Success |
|---------|------------------|------------------|
| Full | All depths | 65% |
| Shallow | ≤3 tactics only | 50% |
| **Δ (effect size)** | — | **15pp [5%, 30%]** |

**Rationale:** Olympiad problems require multi-step proofs (median=9 tactics in literature). If LLMs exploit long-range context (5-10 tactic chains), filtering to shallow proofs should drop success significantly.

## 4.4 Corpus Pattern Matching (H-M3)

**Design:** Random tactic sampling from Mathlib distribution  
**Sampler:** Draw tactics from Mathlib corpus with empirical frequency weights (e.g., `simp` 40%, `rw` 25%, `exact` 15%)  
**Budget:** 15 tactic evaluations/problem (from H-C1 recommendation)  
**Dataset:** miniF2F Lean 4 test set (N=244)  
**Timeout:** 300s  
**Statistical test:** Chi-squared for independent proportions (random Mathlib vs lean-auto H-E1)  
**Gate criterion:** Success ∈ [18%, 25%], Δ=+3pp to +10pp vs lean-auto

**Experimental question:** Does random Mathlib sampling achieve 18-25% success (3-10pp above lean-auto baseline), suggesting corpus frequency patterns contribute 10% of LLM advantage?

**Baseline comparison:**
| Prover | Tactic Selection | Expected Success |
|--------|------------------|------------------|
| lean-auto (H-E1) | Deterministic heuristics | 15% |
| Random Mathlib | Stochastic (human distribution) | 20% [18%, 25%] |
| **Δ (corpus contribution)** | — | **+5pp [+3%, +10%]** |

**Rationale:** LLMs trained on Mathlib learn implicit heuristics from human proof distributions (which tactics frequently succeed together). Random sampling from same distribution provides stochastic baseline — exceeding lean-auto suggests corpus frequency signals contribute, but remaining gap (random 20% → LLM 65%) requires semantic understanding.

## 4.5 Tactic Budget Control (H-C1)

**Design:** Post-hoc statistical analysis on H-E1 solved problems  
**Metrics:** Mean tactic count μ, standard deviation σ, coefficient of variation CV = σ/μ  
**Gate criterion:** CV ≤ 1.0 (low variance validates stable control metric)  
**Budget recommendation:** μ + 1σ (captures ~90% of baseline strategies)

**Experimental question:** Is tactic evaluation count a stable metric (low variance) for controlling computational confounds in LLM vs automated prover comparisons?

**Expected statistics:**
- Mean μ = 10 tactics/problem
- Std σ = 4 tactics
- CV = 0.40 << 1.0
- Recommended budget = 15 (μ+1σ)

**Fairness rationale:** Without tactic budget control, LLMs might appear better by evaluating more tactics (computational advantage) rather than smarter search (algorithmic advantage). Budget=15 equalizes computational resources across configs.

## 4.6 Implementation Details

**Infrastructure:** Lean 4.0 RC, Mathlib 4 (commit abc123...), miniF2F fork (Lean 4 port)  
**Compute:** 32-core CPU, 128GB RAM, no GPU (lean-auto, random Mathlib deterministic)  
**LLM (H-M1):** LeanCopilot with @32 sampling budget (generates 32 tactic candidates per step, beam search)  
**Tactic extraction:** Parse Lean proof checker output for tactic count (deterministic, no custom extraction)  
**Reproducibility:** All experiment configs, Lean code, random seeds published at [repository URL]
