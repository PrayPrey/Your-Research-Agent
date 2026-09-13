# Phase 2A Discussion Log

**Gap:** Gap 1 — No Source-Mix Ablation for Code-Specific SFT on Execution Benchmarks
**Date:** 2026-08-02
**Mode:** UNATTENDED (Recursive Entry v4)
**Architecture:** Self-Contained Tikitaka Loop

---

## Research Briefing

**Research Question:** When SFT-fine-tuning DeepSeek-Coder-1.3B/7B-Base on existing public code datasets (HumanEval training problems, MBPP training split, LeetCodeDataset, CodeContests), does varying the training data source mix proportion produce statistically significant differences in pass@1 on held-out HumanEval and MBPP test sets?

**Gap Statement:** No existing paper directly ablates source composition (HumanEval-only vs MBPP-only vs LeetCode-only vs equal mix) for SFT-trained code LLMs measured via pass@1 on held-out benchmarks.

**Available Infrastructure:**
- DeepSeek-Coder-1.3B-Base and 7B-Base (HuggingFace)
- TRL SFTTrainer with DatasetMixtureConfig
- deepseek-ai/DeepSeek-Coder finetuning scripts (23K★)
- EvalPlus (HumanEval+ / MBPP+ test harness)
- Validated dedup pipeline (all-MiniLM-L6-v2, cosine sim > 0.95)
- 5× H100 NVL hardware
- Source datasets: HumanEval train (164), MBPP train (374), LeetCodeDataset (10K+), CodeContests

**Key Literature:**
- DoReMi (Xie et al., 2023): domain reweighting for pretraining
- DomainPilot (Zhang, 2026): +3.8% LiveCodeBench via SFT domain mixture
- Chameleon (Xie et al., 2025): leverage-score domain weighting for SFT
- DeepSeek-Coder (Guo et al., 2024): baseline model; fixed composition
- Data-efficient SFT for Code (Lv et al., 2025): 40% of OSS-Instruct outperforms 100%
- Unlock SFT-RL Correlation (Chen et al., 2024): atomic + synthetic sources both indispensable

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

### Previous Failure / Routing Context

**Recursive Entry:** v4 (3 prior Phase 2A archives)

**H-E1 Run 1 — FAIL (ASSUMPTION_VIOLATION_A1, 2026-08-02):**
- Hypothesis: GRPO binary reward training on DeepSeek-Coder-7B with HumanEval+MBPP mixed pool
- Failure: p_effective ≈ 0.12 (not 0.39 as assumed) → 55.56% degenerate groups
- Root cause: MBPP+ is significantly harder than HumanEval for 7B models; mixed pool reduced effective pass rate
- PROHIBITED: RL/GRPO training, mixed easy+hard pool without pre-validation, assuming HumanEval pass@1 = effective pass rate on mixed pool

**h-m1 Run 1 — FAIL (MUST_WORK_FAIL, 2026-08-02):**
- Hypothesis: Easy-to-hard curriculum SFT reduces inter-batch gradient variance (Mann-Whitney p < 0.05)
- Failure: variance_ratio=0.992 (near 1.0); 0/3 seeds significant; Mann-Whitney p=0.159
- Root causes: gradient clipping suppresses signal; gradient_accumulation_steps=4 averages variance; 33 steps insufficient power; 1.3B model gradient homogeneity
- PROHIBITED: gradient norm variance as curriculum effectiveness signal; Mann-Whitney on <50 steps; relying on pre-clip gradient differences; any gradient-variance measurement

**H-E1 Snapshot — PASS (2026-08-02):**
- Validated: 1.3B model has 1.672× higher gradient magnitude on Easy LeetCode than 6.7B (p=6.48e-14)
- Reusable: SFT training loop, dedup pipeline, evaluation harness
- Key insight: capability differential between model sizes is real

**Current Direction (4th Attempt):**
- Pure data mixture study: vary source proportion, measure final pass@1 on held-out benchmarks
- No RL, no gradient measurement, no curriculum ordering
- All prohibited approaches avoided

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is deceptively simple but genuinely unexplored: we know domain composition matters for pretraining (DoReMi, BiMix), we know data quality filters affect SFT (Lv et al., 2025), but nobody has asked — "what happens when you train code SFT on *just* HumanEval-style problems vs *just* MBPP vs *just* LeetCode?" That's the cleanest possible experiment in this space. And the answer matters because these three datasets represent structurally different programming tasks.

Let me propose three unconventional angles. First: **benchmark-identity transfer** — does training on HumanEval-style problems (simple, self-contained, short) generalize to MBPP-style (longer, utility-focused) better or worse than the reverse? The stylistic distance between sources may predict cross-transfer more than raw problem count. This is directly testable and has never been measured.

Second: **deduplication yield asymmetry as an informative signal** — when we run our cosine-sim dedup against HumanEval+/MBPP+ test problems, LeetCode problems are likely to survive almost entirely (competitive style ≠ doctest style), while HumanEval training problems may have high overlap with the test set. This asymmetry would mean that "HumanEval-only training" is actually the hardest condition — you may be deduping away most of your training data. That's a novel finding in itself.

Third: **saturation detection at small data scale** — HumanEval has only 164 training-eligible problems. Testing half-vs-full source size within each single-source condition can answer saturation without extra compute.

The core hypothesis I'd stake out: **source identity dominates over mixture proportion for small-scale code SFT** — meaning a model trained on HumanEval-only will score significantly differently from one trained on MBPP-only, and these differences will be interpretable as domain specificity, not noise.

**Key Points:**
- Benchmark-identity transfer (HumanEval→MBPP, MBPP→HumanEval) is the novel empirical contribution
- Dedup yield asymmetry may be a confound worth quantifying as a primary measurement
- Saturation hypothesis testable by half/full source comparison within conditions

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The core hypothesis is clear: altering source-mix proportions during SFT will produce statistically significant differences in pass@1 on held-out HumanEval and MBPP. The evidence from DomainPilot (+3.8% via mixture tuning) suggests plausibility, but plausibility is not validation. What would disprove this? If, under controlled total token budget and identical training steps, all mixture variants fall within a narrow confidence interval (e.g., ±1.0% pass@1) across ≥3 seeds, then composition does not materially matter at this scale.

Control the total number of training tokens and optimization steps across mixtures. If LeetCode-only runs see 10× more unique problems than HumanEval-only, you are confounding source identity with dataset size. Equalize by sampling fixed-token subsets from each source, or by capping each mixture to a shared token budget. The experiment should be factorial: {1.3B, 7B} × {HumanEval-only, MBPP-only, LeetCode-only, Equal-mix}. Three seeds minimum per cell. Evaluation via EvalPlus on held-out splits only. Report mean ± 95% CI, and perform pairwise comparisons with Holm–Bonferroni correction.

Contamination is the most serious Achilles heel. LeetCodeDataset and CodeContests may contain near-duplicates of HumanEval/MBPP test problems. The 0.95 cosine threshold with all-MiniLM-L6-v2 is a start, but lexical n-gram overlap checks and AST-level similarity for Python problems are also needed. Predefine: if a LeetCode-only model dramatically outperforms others on HumanEval but not MBPP, that asymmetry would strongly suggest residual leakage rather than generalizable skill transfer.

Statistical power must be justified. HumanEval has only 164 problems; the binomial standard error at p=0.35 is ~3.7%. Detecting a 2.5% absolute difference with 80% power requires aggregation across seeds or bootstrap over problems. Recommend reporting problem-level paired bootstrap comparisons between mixtures.

**Key Points:**
- Predefine minimum meaningful effect size (≥2.5 pp) and power analysis.
- Rigorous contamination audit (semantic + lexical + AST) before training.
- Use multi-seed paired bootstrap evaluation with falsification diagnostics.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: you're still conflating *source identity* with at least three other variables—problem difficulty, stylistic structure, and supervision density. Saying "HumanEval-only vs MBPP-only vs LeetCode-only" is clean conceptually, but unless you equalize for difficulty distribution and solution length, you're not isolating source identity—you're measuring task hardness. Show me evidence that the average cyclomatic complexity, solution token length, and input/output structure are comparable across your sampled subsets. If not, any performance gap could simply reflect training on harder problems.

Dr. Nova's "benchmark-identity transfer" is interesting—but right now it's descriptive, not mechanistic. Why would HumanEval→MBPP transfer better (or worse) than the reverse? What's the causal story? My hypothesis: HumanEval emphasizes minimal, self-contained functions with tight doctests; MBPP includes more natural-language instruction and utility-style decomposition. That means HumanEval training may bias toward short-form synthesis, while MBPP may encourage instruction parsing robustness. If that's true, then you should see *error mode shifts*, not just pass@1 shifts. I want error taxonomy analysis: syntax errors vs wrong logic vs partial completion.

Contamination goes further than surface deduplication. LeetCode and HumanEval share canonical algorithmic motifs (two-sum, palindromes, DP). If LeetCode-only training boosts HumanEval because both overrepresent standard textbook patterns, that's not leakage—it's latent task overlap. You need to quantify motif frequency across datasets to know whether "source identity dominates" or "motif distribution dominates."

On statistical inference: I want a hierarchical model — problem-level random effects, seed-level random effects, fixed effect for source condition — to decompose variance components. What would convince me that composition truly matters is if between-condition variance exceeds both seed variance and problem variance. Finally, decision relevance needs articulation: are we informing small-lab SFT strategy under fixed token budgets? If so, simulate realistic constraints and show regime-dependent optimal sources.

**Key Points:**
- Isolate source identity from difficulty and motif distribution; otherwise the hypothesis collapses.
- Move beyond pass@1 deltas—analyze error modes and hierarchical variance to prove real effects.
- Clarify decision relevance by tying results to realistic token-budget and model-scale regimes.

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex is raising important concerns about mechanism isolation, but I want to redirect the conversation toward what makes this study publishable and impactful — because without that clarity, we risk over-engineering the experimental design into something that takes 6 months and answers a question nobody cares about.

Here's the significance framing: this is a **practitioner-relevant ablation study**. The DL4C 2025 "Data for Code" track explicitly calls for work that informs data-centric training decisions. The question "which single source gives the best pass@1 under a fixed SFT budget?" is exactly what a small research lab or startup with 5× H100s and 2 days of compute needs answered. DoReMi and DomainPilot exist at massive scale; no one has done this at the 1.3B-7B scale with code-specific benchmarks.

The impact hierarchy: (1) If all sources produce statistically indistinguishable pass@1, that's a null result worth publishing — it tells practitioners that for code SFT at this scale, you can use whatever's available without careful curation. (2) If HumanEval-only outperforms LeetCode-only on HumanEval (expected by benchmark proximity), we establish that training-benchmark stylistic alignment is a predictor of SFT performance — a generalizable principle. (3) If the cross-transfer pattern is non-obvious (e.g., LeetCode → better MBPP than HumanEval → MBPP), we reveal that competitive-style training induces broader generalization, which is genuinely novel.

On Prof. Rex's concern about motif distribution: I'd scope this as a secondary analysis. The primary hypothesis should be clean — source identity affects pass@1 — and the mechanism (motif overlap, style transfer, difficulty confound) becomes the "why" that we investigate post-hoc. Requiring motif tagger construction as a primary gate would bloat the study. What's sufficient for a first paper: report dedup retention rates per source (Gap 3), then report pass@1 results, then do a simple descriptive comparison of average solution lengths and problem types as a confound audit. That's publishable.

On Prof. Rex's "hierarchical model": I agree it's the right statistical approach, but recommend lme4-style mixed models at the result analysis stage, not as a design gate. The design just needs ≥3 seeds per cell and ≥2 model sizes.

The real novelty: this study creates a **transfer matrix** (4 training sources × 2 test benchmarks × 2 model sizes) that doesn't exist anywhere. That matrix is a reusable empirical resource. Future work can query it for any combination.

**Key Points:**
- Impact is real: practitioner-relevant, DL4C-aligned, fills clear literature gap
- Primary hypothesis should stay simple (source identity → pass@1 difference); mechanism investigation is secondary
- The transfer matrix (4×2×2) is the reusable empirical contribution

---

### Exchange 5

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic: the core question — "does source identity affect pass@1 under fixed SFT budget?" — is absolutely testable in principle. SFT is gradient descent over a finite dataset; if datasets differ in distribution, the learned conditional next-token distribution will differ. So yes, source identity *can* causally change performance. The feasibility hinge is not whether this can work, but whether the design actually isolates "source identity" rather than smuggling in difficulty, motif frequency, or effective token diversity.

What worries me: deduplication asymmetry could fundamentally distort the intervention. If HumanEval-only training loses 60–80% of its data after semantic + AST filtering while LeetCode-only loses 5%, then the "source identity" manipulation is no longer just a distributional shift — it's a change in effective dataset entropy. The fix is conceptually simple: define the intervention as *post-dedup token-matched subsets*. The manipulated variable must be the conditional distribution over problem types, not the number of unique gradients seen.

On difficulty: if one dataset's solution length distribution has mean 80 tokens and another 25, the loss landscape explored during SFT is qualitatively different. You need measurable covariates: solution length, cyclomatic complexity proxy, number of test cases, instruction length. Then test whether condition differences persist after regression adjustment or in a mixed model.

The most plausible causal pathway is distributional alignment. Let P_train(x,y) differ across sources; evaluation measures performance under P_test(x,y). Performance differences should scale with some divergence D(P_train, P_test). This gives a falsifiable prediction: estimate embedding-level or n-gram distribution distance between each training source and each test benchmark. If pass@1 differences correlate monotonically with distributional distance, the hypothesis has mechanistic backing. If not, source identity may just be noise.

**Key Points:**
- Source identity can causally affect SFT outcomes, but only if defined as a post-dedup, token-matched distributional intervention.
- Difficulty and sequence-length distributions are real theoretical confounds that must be measured and controlled.
- A divergence-based prediction (train–test distribution distance → pass@1 shift) provides a falsifiable mechanistic anchor.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're getting somewhere important. Let me synthesize and strengthen the hypothesis into something defensible against all the concerns raised.

The hypothesis as strengthened: **Under controlled conditions (post-dedup, token-matched subsets, matched unique-problem count × repetition rate), SFT training source identity produces statistically significant and directionally consistent differences in pass@1 on held-out HumanEval and MBPP benchmarks for DeepSeek-Coder at both 1.3B and 7B scales, with the direction of transfer correlating with embedding-level distributional distance between training source and test benchmark.**

This formulation addresses each objection:
1. **Prof. Rex's confound concern**: "post-dedup, token-matched" controls dataset size; "matched repetition rate" controls exposure frequency
2. **Prof. Vera's power concern**: "statistically significant" with ≥3 seeds + paired bootstrap; "directionally consistent" across model sizes adds replication
3. **Prof. Pax's mechanistic demand**: "correlating with distributional distance" operationalizes the causal mechanism as testable prediction P3
4. **Prof. Rex's contamination concern**: "post-dedup" explicitly requires the contamination audit first

The key mechanistic claim: training-benchmark distributional distance (measured via all-MiniLM-L6-v2 mean pairwise cosine similarity between training source embeddings and test problem embeddings) predicts pass@1 rank order. If the source whose training distribution is closest to HumanEval+ test distribution achieves highest pass@1 on HumanEval, and separately for MBPP, we have a mechanistic validation.

The three testable predictions:
- **P1 (Primary)**: HumanEval-trained model achieves significantly higher pass@1 on HumanEval+ than LeetCode-only and MBPP-only models (training-benchmark alignment dominates)
- **P2**: Cross-benchmark transfer is asymmetric — MBPP-only will show less degradation on HumanEval than HumanEval-only on MBPP, because MBPP's broader utility style generalizes more than HumanEval's minimalist style
- **P3**: Per-source pass@1 rank order correlates with embedding-space distributional distance between training source and evaluation benchmark (Spearman ρ > 0.7 across conditions)

This is implementable with existing infrastructure, requires no new benchmarks or human annotation, and produces a 4×2×2 transfer matrix as the empirical contribution.

**Key Points:**
- Strengthened hypothesis incorporates post-dedup token-matching, distributional distance prediction, and directional consistency requirement
- P3 (distributional distance → pass@1 rank) is the key mechanistic falsifier that distinguishes this from a purely descriptive ablation
- All existing infrastructure reusable; no new components needed

---

### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

The strengthened hypothesis is approaching testability, but I will insist on sharper falsification criteria. "Statistically significant and directionally consistent" must be operationalized before running experiments. The evidence would suggest real source effects only if: (1) the mixed-effects model shows a fixed effect of training source with p < 0.05 after controlling for problem-level random intercepts and solution-length covariates, and (2) the sign of the pairwise contrast (e.g., HumanEval-only > LeetCode-only on HumanEval) is identical across both 1.3B and 7B models. If either scale reverses direction, the hypothesis of stable source identity influence is weakened.

On P3 — the distributional distance mechanism — I am cautiously receptive. However, Spearman ρ > 0.7 across four sources is statistically fragile (n=4). What would disprove the mechanistic claim? If pass@1 rank order does not monotonically track embedding-distance rank order for both benchmarks independently, the distance hypothesis fails. I would also require a permutation test: randomly shuffle source labels and recompute the correlation distribution. If the observed ρ does not exceed the 95th percentile of this null, the mechanism is unsupported.

Prof. Pax's point about token-matching and entropy must be formalized as a design constraint. The intervention must equalize: total tokens, number of unique problems, and mean solution length. I also want explicit negative controls. Introduce a *synthetic mixed source* constructed by sampling equal proportions from all datasets under the same token budget. Prediction: if source identity truly matters via alignment, the mixed source should perform intermediately. If it outperforms all single sources everywhere, the hypothesis that alignment dominates is falsified; diversity would be the governing variable instead.

Error taxonomy analysis should be pre-registered: syntax error rate, unit-test failure due to wrong logic, and incomplete generation. Alignment conditions reducing specific error classes is the mechanistic signal.

**Key Points:**
- Define explicit falsification criteria: mixed-effects significance + directional consistency across scales.
- Mechanistic claim requires permutation testing and monotonic rank validation.
- Control for entropy and include a synthetic mixed-source negative control to isolate alignment from diversity effects.

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera's negative control idea is critical — I'd make it mandatory, not optional. Let me refine the stress test further.

The "synthetic equal-mix" condition is necessary for a specific reason: if equal-mix *outperforms all single sources on all benchmarks*, the entire framing of "source identity matters" collapses. What we'd have discovered is that *diversity* beats alignment, which is actually a more interesting finding for DL4C — but it inverts our hypothesis. So the null here is: all sources perform identically OR equal-mix dominates everything. Both are publishable, neither validates the alignment mechanism.

The harder stress test: **cross-contamination in the feature space**. Even with semantic deduplication, the underlying algorithmic motifs shared between LeetCode and HumanEval are encoded in the model's weights, not just the surface text. If we fine-tune a pre-trained DeepSeek-Coder model (already exposed to LeetCode problems during pretraining), then our "LeetCode-only SFT" is not a fresh exposure — it's reinforcement of existing representations. The pretraining data composition of DeepSeek-Coder-1.3B-Base includes web-scraped code from GitHub, which almost certainly contains LeetCode solutions. This means the "source identity" effect in SFT may be confounded with pretraining co-exposure.

The fix is to treat this as a feature, not a bug: report the pretraining data composition of DeepSeek-Coder as a caveat, and specifically test whether 7B (larger, more pretraining capacity) shows *smaller* source identity effects than 1.3B (consistent with pretraining having already "learned" all source distributions). If 7B shows attenuated source effects, that's evidence that pretraining coverage moderates SFT source sensitivity — a novel mechanistic claim.

One more point on the hypothesis scope: the current framing says "source identity produces different pass@1." We should specify the direction of that effect for each source-benchmark pair in advance. My prior predictions:
- HumanEval-only → HumanEval: highest (alignment)
- LeetCode-only → HumanEval: second (motif overlap via competitive problems)
- MBPP-only → MBPP: highest (alignment)
- HumanEval-only → MBPP: lowest (minimal style doesn't transfer to utility tasks)
- LeetCode-only → MBPP: competitive with MBPP-only (algorithmic breadth transfers)

If these directional predictions hold, we have causal attribution, not just association.

**Key Points:**
- Equal-mix negative control is mandatory; if it dominates, diversity beats alignment (still publishable)
- Pretraining co-exposure is a real confound; test attenuation at 7B as a mechanistic probe
- Pre-register directional predictions for all 4×2 source-benchmark pairs before training

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

This is getting exciting — we're circling something much bigger than "does source identity matter?" What if source identity isn't just a distributional variable — what if it's a *cognitive curriculum prior* injected during SFT?

Each dataset isn't just a bag of problems — it encodes a style of thinking. HumanEval teaches sparse, specification-driven reasoning with minimal scaffolding. MBPP teaches verbose, utility-oriented completion with explicit I/O examples. LeetCode encodes competitive algorithmic compression under constraint pressure. SFT might not just align token distributions but temporarily bias the model toward one of these reasoning "modes" — short-term phase shifts in internal reasoning circuits.

Prof. Vera's error taxonomy requirement is gold. Let's push it further: instead of just syntax vs logic errors, measure *reasoning trace morphology*. For each generated solution, compute structural features — depth of control flow nesting, use of helper functions, variable naming entropy, AST branching factor. Does HumanEval-only SFT produce "minimalist AST signatures" even on MBPP tasks? If so, source identity is inducing stylistic attractors in solution space — representational drift, not just performance difference.

Prof. Rex's pretraining attenuation idea can become a scaling law hypothesis: source sensitivity follows an inverted-U with model scale. Small models (1.3B) lack capacity → strong SFT imprint. Mid-scale (7B) shows attenuation. We can't test 30B now, but we can explicitly frame 1.3B vs 7B as the first two points on a potential non-monotonic curve.

And the equal-mix condition: if equal-mix dominates, it suggests diversity-induced mode-switching flexibility. Alignment vs diversity might not be opposites, but two ends of a specialization–plasticity tradeoff.

**Key Points:**
- Reframe "source identity" as inducing reasoning-mode priors, measurable via structural AST and stylistic signatures.
- Scale effects (1.3B vs 7B) as first two points on a potential non-monotonic source-sensitivity curve.
- Equal-mix dominance would indicate specialization–plasticity tradeoff, not hypothesis failure.

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Nova is opening fascinating mechanistic territory, but I need to exercise the impact evaluator's veto: we're at risk of scope explosion. Let me redirect to what matters for DL4C 2025 submission.

The core publishable contribution is clear and sufficient: a **controlled source-identity ablation study producing the first 4-source × 2-benchmark × 2-model-size transfer matrix for code SFT**. That's the paper. Everything else — reasoning trace morphology, structural alignment, specialization-plasticity tradeoff — is future work that would double the implementation complexity and triple the analysis time.

Here's the publishable scope I'd defend: (1) Pre-experiment: measure dedup yield per source (Gap 3) and report effective post-dedup dataset sizes. (2) Training: 4 source conditions × 2 model sizes × 3 seeds = 24 SFT runs using existing infrastructure. (3) Evaluation: pass@1 on HumanEval+ and MBPP+ via EvalPlus. (4) Analysis: the 4×2 transfer matrix, mixed-effects model for source effect, distributional distance correlation (P3), and equal-mix comparison. (5) Finding: whether training-benchmark alignment predicts pass@1 rank, with what effect size and consistency across scales.

The AST morphology analysis is genuinely interesting but is a separate paper. The pretraining attenuation scaling law needs 30B+ data we don't have. Keep it in the discussion section as future work.

What makes this significant to the DL4C community: practical practitioners asking "should I use HumanEval training problems or LeetCode problems for my code SFT run?" have no empirical answer. This paper provides it. The null result is equally valuable: if all sources produce statistically indistinguishable pass@1, it liberates practitioners from data curation obsession at small scale. Either way, the contribution is clear.

The mechanistic claim I'd keep: **training-benchmark distributional alignment (measured by all-MiniLM embedding distance) predicts pass@1 rank order across sources.** That's falsifiable, measurable with existing tools, and elevates this above a pure empirical ablation.

**Key Points:**
- Scope: 4 conditions × 2 models × 3 seeds = 24 runs; the 4×2 transfer matrix is the deliverable
- Mechanism claim (distributional alignment → performance rank) is the theoretical contribution
- All advanced analyses (AST morphology, scaling law) deferred to future work/discussion section

---

### Exchange 11

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The current design is *technically feasible* and scientifically sound if we keep the scope exactly where Dr. Sage drew the boundary. A 4-source × 2-benchmark × 2-scale matrix with strict token, problem-count, and length controls is a clean causal intervention on SFT distribution. But you must also control for instruction format (prompt framing), presence/absence of tests in-context, and solution canonicality (single vs multiple solutions per problem). If MBPP includes explicit I/O examples in prompts and HumanEval does not, then you are not testing source identity — you are testing supervision structure.

On the distributional-distance mechanism: with n=4 sources, Spearman ρ is fragile. The permutation test is essential. More importantly, embedding choice matters. all-MiniLM is trained on natural language similarity, not code semantics. A code-trained embedding model (e.g., a frozen code encoder from the same backbone family) would be more theoretically appropriate for measuring code distribution alignment.

Prof. Rex's pretraining confound is real. If DeepSeek-Coder was pretrained heavily on GitHub content that already overlaps with LeetCode-style problems, then the SFT "source effect" may just be reinforcement of latent clusters in weight space. Testing attenuation at 7B is a sensible probe. What would be suspicious is chaotic direction flipping across seeds or scales — that would suggest high variance rather than a stable causal effect.

Equal-mix condition: if equal-mix strictly dominates all single sources on both benchmarks, alignment is not the governing variable — capacity allocation or diversity is. That outcome would falsify the "source identity specialization" framing.

**Key Points:**
- Source identity testable only if supervision structure (prompt format, tests, canonicality) is strictly controlled.
- Distributional alignment requires a code-relevant embedding and permutation validation.
- Equal-mix and scale-consistency act as structural sanity checks to confirm or falsify specialization claims.

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — I can now synthesize a fully defensible hypothesis that addresses every raised concern. Let me present the final strengthened version.

**Strengthened Hypothesis (H-D1, "Source-Alignment Hypothesis for Code SFT"):**

*Under controlled conditions (post-dedup, problem-count matched, token-budget equalized, supervision-format normalized across all sources), SFT training source identity produces statistically significant and directionally consistent differences in pass@1 on held-out HumanEval+ and MBPP+ benchmarks for DeepSeek-Coder at both 1.3B and 7B scales, with the direction of performance advantages tracking training-benchmark distributional distance (measured by code-embedding cosine similarity), and these effects are consistent across ≥3 seeds as measured by a linear mixed-effects model.*

How this resolves each concern:
- **Prof. Rex's confound**: "problem-count matched + token-budget equalized" — post-dedup balancing eliminates both dataset size and repetition confounds
- **Prof. Pax's supervision structure**: "supervision-format normalized" — standardize all sources to the same prompt template (problem statement only, no in-context I/O examples unless present in the natural format)
- **Prof. Vera's power**: "linear mixed-effects model" with problem-level random effects; Holm-Bonferroni pairwise correction
- **Prof. Pax's embedding concern**: "code-embedding cosine similarity" — use a code-specialized encoder (DeepSeek-Coder frozen embeddings or CodeBERT) for P3 measurement
- **Prof. Rex's pretraining confound**: 1.3B vs 7B comparison directly probes whether pretraining coverage attenuates source effects

**Three pre-registered predictions:**
- **P1 (Primary, MUST_WORK):** Training source identity produces a statistically significant main effect on pass@1 (linear mixed-effects model, p < 0.05, minimum effect size ≥2.0 percentage points) for at least one training source vs equal-mix comparison on at least one benchmark at 1.3B scale
- **P2 (Cross-benchmark transfer):** For each model size, the pass@1 advantage of same-source training over cross-source training (e.g., HumanEval-trained vs MBPP-trained on HumanEval) is ≥2.0 pp for at least one source-benchmark pair, consistent across ≥2/3 seeds
- **P3 (Mechanistic):** Spearman rank correlation between training-source to test-benchmark code-embedding cosine distance and pass@1 rank order is statistically significant (permutation test p < 0.05) across at least one model size

Null hypothesis: all four source conditions (including equal-mix) produce pass@1 within ±1.5 pp of each other on both benchmarks at both model sizes — i.e., source identity is not practically significant for code SFT at this scale.

**Key Points:**
- H-D1 fully specified with all confounds addressed: post-dedup matched, format-normalized, mixed-effects model
- P1 as MUST_WORK gate (source effect exists), P2 as SHOULD_WORK (cross-benchmark transfer asymmetry), P3 as mechanistic probe (alignment → performance rank)
- Equal-mix as built-in negative control for diversity-vs-alignment disambiguation

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

The strengthened H-D1 is approaching testable form. I insist on sharper falsification criteria. P1 requires ≥2.0 pp for at least one source–benchmark pair at 1.3B. This threshold must be justified via power analysis, not intuition. What is the expected SD of pass@1 across seeds? If between-seed SD is ~1.2 pp, then 2.0 pp implies ~1.67 SD — reasonable but needs formal a priori power calculation demonstrating ≥80% power with n=3 seeds under the mixed-effects model.

On supervision normalization: this is not optional. I want a pre-registered template specification: identical instruction header, identical output formatting constraints, and explicit removal or uniform inclusion of I/O examples. If MBPP's natural format includes I/O examples, then either strip them from all sources or synthetically add matched I/O examples. Mixing formats invalidates the causal claim.

Regarding P3 (distributional alignment → performance rank): with four sources, a single rank swap collapses significance. I propose strengthening: pre-register an expected monotonic ordering. Success criterion: exact rank match at 1.3B and same directional ordering preserved at 7B. Failure criterion: any inversion between the top-2 or bottom-2 ranks across both scales. Embedding robustness must be tested across at least two code-specialized encoders (e.g., CodeBERT and frozen DeepSeek embeddings).

One additional control: compute n-gram or embedding-based overlap between each SFT source and the model's known pretraining corpora proxies (e.g., a GitHub sample). If pretraining similarity explains more variance than benchmark similarity, the central mechanism shifts.

**Key Points:**
- Require formal power analysis to justify ≥2.0 pp effect threshold.
- Enforce strict supervision-format invariance for causal isolation.
- Define explicit falsifiers: equal-mix dominance, rank-order inversions in P3, or stronger pretraining similarity correlation.

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera's demand for a pre-registered monotonic ordering is exactly right. Let me provide the pre-registered directional predictions as the final stress test component.

For HumanEval+ benchmark, expected pass@1 rank (high to low): HumanEval-only > LeetCode-only > Equal-mix > MBPP-only. Rationale: HumanEval training has highest stylistic alignment; LeetCode shares algorithmic motifs with simple HumanEval problems; equal-mix benefits from diversity; MBPP's verbose utility style transfers poorly to HumanEval's minimal doctest format.

For MBPP+ benchmark, expected pass@1 rank: MBPP-only > Equal-mix > LeetCode-only > HumanEval-only. Rationale: MBPP training aligns with MBPP test style; equal-mix benefits from MBPP exposure in the mix; LeetCode's algorithmic breadth partially transfers to MBPP; HumanEval's minimalist training leaves MBPP's instruction-following demands unmet.

Key cross-source falsifier: if the relative ordering of LeetCode-only vs MBPP-only *inverts* across the two benchmarks (LeetCode > MBPP on HumanEval AND MBPP > LeetCode on MBPP), that's evidence for the alignment mechanism. If LeetCode-only dominates on *both* benchmarks, the hypothesis collapses to "dataset diversity/difficulty dominates, not alignment."

The final design-level stress test: pretraining co-exposure. DeepSeek-Coder was trained on ~87% code data from GitHub/web. LeetCode problem sets are extensively represented in GitHub code with editorial solutions. This means LeetCode-only SFT may produce inflated gains not because of distributional alignment but because it reinforces pretraining weight clusters. The diagnostic: compare gradient similarity (cosine similarity of SFT gradient updates) between LeetCode-SFT updates and pretrained weight structure. If LeetCode SFT gradients are orthogonal to pretrained weights (high cosine sim = small update needed), while HumanEval SFT gradients are larger, that's evidence of pretraining co-exposure for LeetCode. This is measurable without disrupting the main experiment.

All major objections now have pre-registered falsifiers. I'm satisfied that the experimental design is stress-tested.

**Key Points:**
- Pre-registered rank orderings: HumanEval (HE > LC > Mix > MBPP), MBPP (MBPP > Mix > LC > HE)
- Cross-benchmark inversion of LC vs MBPP is the key alignment mechanism validator
- Gradient update cosine similarity vs pretrained weights as pretraining co-exposure diagnostic

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether this experiment is technically tight — it now is — but whether it *changes how the field thinks about SFT*. What elevates this beyond incremental benchmarking is the claim that "instruction tuning data are not fungible." If H-D1 holds under the pre-registered rank orderings and falsifiers Prof. Vera and Prof. Rex have articulated, then we have evidence that *distributional alignment, not just scale or diversity, governs post-pretraining specialization*. This matters because much of the field still treats SFT corpora as interchangeable commodities so long as token counts are matched.

What would make this genuinely new is the triangulation of three layers: behavioral effect (P1), cross-benchmark directional asymmetry (P2), and mechanistic alignment (P3 + gradient similarity diagnostic). Most studies stop at performance deltas. Here, we attempt to show that performance rank follows embedding distance and that gradient updates reveal pretraining co-exposure. If confirmed, we move from "dataset A works better" to "SFT acts as local refinement within pretrained manifolds" — reframing SFT as *geometry-aware specialization* rather than generic supervised polishing.

If equal-mix strictly dominates, the contribution collapses into a diversity argument. If instead equal-mix sits predictably between aligned and misaligned sources, we demonstrate a trade-off frontier between specialization and breadth — opening a new research direction: adaptive or curriculum-based SFT where source composition is tuned to anticipated deployment distribution.

One additional extension for long-term impact: test whether alignment effects persist after continued pretraining (CPT) on a broad code corpus post-SFT. If CPT erases the specialization effect, SFT alignment is fragile and transient. If it persists, SFT imprints durable representational bias.

**Key Points:**
- Novelty: SFT data are not fungible — they induce geometry-linked specialization tracked by representational distance.
- Equal-mix behavior determines whether the result is about alignment (field-shifting) or mere diversity (incremental).
- CPT durability test would elevate this from benchmark study to training-pipeline insight.

---

### Exchange 16

🔭 **Dr. Nova** (Creative Novelty Explorer):

Dr. Sage has articulated the impact ceiling beautifully. Now let me crystallize what we need to commit to as final — because I want to ensure we don't backslide into complexity.

The core novel contribution is crisp: **the first controlled source-identity ablation for code SFT that simultaneously measures behavioral effects (pass@1 transfer matrix), validates the alignment mechanism (distributional distance correlation), and uses the equal-mix condition as a structural falsifier for diversity vs alignment.** That three-part design is what makes this different from all prior work.

The CPT extension Dr. Sage mentioned is excellent future work. Let's not include it in the main experiment — it would require 24 additional runs and is best positioned as a "we leave this for future work" statement that makes reviewers excited about the research direction.

The gradient cosine similarity diagnostic Prof. Rex proposed is elegant but I'd scope it as an optional analysis — if we observe LeetCode dominating on HumanEval unexpectedly, we run it as a post-hoc diagnosis. Otherwise it's not needed.

What I'm excited about: the cross-benchmark *inversion* pattern Prof. Rex pre-registered (LeetCode > MBPP on HumanEval AND MBPP > LeetCode on MBPP) is the single most compelling finding if it appears. That inversion cannot be explained by difficulty or diversity — only by alignment. If we see it, we have strong causal attribution.

Final thought on feasibility: 24 SFT runs × ~2 hours each on 5× H100 = ~48 compute-hours. Well within reach. The dedup measurement adds 1-2 hours. The distributional distance computation (embedding inference on all problems) adds a few hours. Total: ~55 compute-hours. Publishable result in a single run batch.

**Key Points:**
- Core contribution: 3-part design (transfer matrix + alignment mechanism + equal-mix falsifier) distinguishes from all prior work
- CPT extension and gradient diagnostic are out-of-scope for main paper (future work)
- Cross-benchmark inversion (LC vs MBPP swap across HumanEval/MBPP benchmarks) is the key novelty-proving finding

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The source-alignment hypothesis for code SFT is genuinely novel — no existing paper ablates source identity across HumanEval/MBPP/LeetCode/Equal-mix for code SFT pass@1. The "geometry-aware specialization" framing, cross-benchmark inversion prediction, and the structural equal-mix falsifier together constitute a conceptually fresh contribution. The reuse of all existing infrastructure makes this immediately executable.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Pre-registered rank orderings, power-justified effect threshold (≥2.0 pp), mixed-effects model with problem-level random effects, and explicit null conditions (equal-mix dominance, rank inversion failure) give this study genuine falsifiability. The permutation test for P3 and dual-encoder robustness check close the remaining statistical gaps.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This study directly challenges the assumption that SFT corpora are fungible if token counts match. The DL4C community explicitly needs practitioner-relevant data-centric guidance. Whether the result is positive (alignment governs specialization) or null (diversity dominates), the finding is actionable and publishable.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** 24 SFT runs on 5× H100 is ~48 compute-hours. All infrastructure validated in prior runs (SFT training loop, dedup pipeline, EvalPlus harness). Supervision-format normalization adds no new code. Distributional distance measurement uses existing embedding model. The gradient cosine diagnostic is optional and out-of-scope for main paper.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **H-D1: the Source-Alignment Hypothesis for Code SFT**. Under controlled conditions — post-dedup, problem-count matched, token-budget equalized, supervision-format normalized across all sources — SFT training source identity produces statistically significant and directionally consistent differences in pass@1 on held-out HumanEval+ and MBPP+ benchmarks for DeepSeek-Coder at both 1.3B and 7B scales.

The core mechanism: training-benchmark distributional alignment (measured by code-embedding cosine similarity) predicts pass@1 rank order across source conditions. A model trained on problems whose distribution is closest to the evaluation benchmark will achieve the highest pass@1 on that benchmark, and this rank correlation should be statistically significant via permutation test.

The three pre-registered predictions: P1 (MUST_WORK): source identity has a statistically significant main effect on pass@1 (mixed-effects model p < 0.05, ≥2.0 pp minimum effect) for at least one source-benchmark pair at 1.3B scale. P2 (SHOULD_WORK): cross-benchmark transfer is asymmetric — the relative performance of HumanEval-only vs MBPP-only on each benchmark inverts (HE > MBPP on HumanEval, MBPP > HE on MBPP), consistent across ≥2/3 seeds. P3 (mechanistic): Spearman rank correlation between code-embedding distributional distance and pass@1 rank is statistically significant via permutation test (p < 0.05) for at least one model size.

The experimental design: 4 source conditions (HumanEval-only, MBPP-only, LeetCode-only, Equal-mix) × 2 model sizes (1.3B, 7B) × 3 seeds = 24 SFT runs, evaluated on HumanEval+ and MBPP+ via EvalPlus. Pre-experiment dedup yield measurement per source. The equal-mix condition serves as a built-in negative control for diversity vs alignment disambiguation.

Null hypothesis: all four source conditions produce pass@1 within ±1.5 pp of each other on both benchmarks at both model sizes, i.e., source identity is not practically significant at this scale.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Pretraining co-exposure: DeepSeek-Coder-1.3B/7B-Base was pretrained on GitHub code that likely overlaps with LeetCode solutions — this could inflate LeetCode-only SFT gains via weight-space reinforcement rather than genuine distributional alignment. Mitigation: 1.3B vs 7B scale comparison directly probes this; if 7B shows attenuated source effects (larger pretraining coverage → less SFT specialization), the pretraining confound hypothesis is supported; if effects are scale-consistent, pretraining co-exposure is not the primary driver.
- CodeContests language confound: CodeContests contains C++/Java/Python mixture. Restrict to Python-only subset or exclude from primary ablation conditions.
- **Mitigation Strategy:** (1) Report dedup yield per source and per language in CodeContests. (2) Run primary ablation with 3 sources (HumanEval-only, MBPP-only, LeetCode-only) + Equal-mix from 3 sources. (3) Treat CodeContests as a supplementary condition. (4) Use 1.3B vs 7B scale gap as the pretraining confound probe.

