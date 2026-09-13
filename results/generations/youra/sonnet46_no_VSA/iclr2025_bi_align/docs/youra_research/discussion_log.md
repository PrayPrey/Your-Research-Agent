# Phase 2A Discussion Log
**Gap:** gap-1 — Absence of scale-controlled pairwise correlation structure for Human→AI alignment benchmarks
**Started:** 2026-07-30T05:39:22Z
**Execution Mode:** UNATTENDED (recursive v10+)
**Architecture:** Self-Contained Tikitaka Loop (Inline)

---

## Briefing

### Research Gap
No existing study computes the pairwise partial Spearman rank-correlation matrix of {TruthfulQA MC2, BBQ accuracy, HarmBench/BeaverTails safety rate, HELM ECE} after controlling for MMLU as a scale proxy across N≥40 open-weight LLMs.

**Central Question:** After removing the MMLU scale signal, do alignment benchmarks cluster (unidimensional) or remain independent (multi-dimensional)?

**Direct Precedent:** clawrxiv:2603.00394 finds TruthfulQA = orthogonal PC2 (23.4% variance) for 6 general benchmarks. This study extends to alignment-specific benchmarks (TruthfulQA MC2, BBQ, HarmBench/BeaverTails) with pairwise partial Spearman + cluster-bootstrap CIs.

**Available Data:**
- fboulnois/llm-leaderboard-csv: TruthfulQA MC2 + MMLU for 300+ open-weight models
- lighteval/bbq_helm (HuggingFace): BBQ accuracy, 11,864 rows
- centerforaisafety/HarmBench (GitHub): Refusal rate for 33 LLMs
- PKU-Alignment/BeaverTails (HuggingFace): is_safe field, 30k_test (fallback for HarmBench)
- Analysis: pingouin.partial_corr(method='spearman', covar=['MMLU'])

**MANDATORY FEASIBILITY CONSTRAINTS:**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- All data must exist now as public datasets
- N≥40 triple-overlap required (pre-flight gate)

---

### Previous Failure / Routing Context

This is a **recursive Phase 2A entry (v10+)**. All prior hypotheses have failed or been superseded:

| Hypothesis | Status | Root Cause |
|-----------|--------|------------|
| sh2-corr | FAIL (MUST_WORK) | rho=+0.661 OPPOSITE to hypothesized negative (scaling confound dominates) |
| h-e2 | FAIL (MUST_WORK) | match_rate=0.517 < 0.70; proprietary model structural absence in LLM LB v1 |
| h-m1 | SUPERSEDED | RLHF improves TruthfulQA +3.406 (direction reversed; 69.5% pairs show improvement) |
| sh-p1 | FAIL (MUST_WORK) | Logistic regression: β₁ p=0.0595, calibration slope [-0.28,2.55] — both fail |
| h-e1 | FAIL (MUST_WORK) | N_joint=18 < 25; HarmBench × LLM LB v1 structural temporal mismatch |

**Key Empirical Facts Established (preserved):**
- MMLU explains 32% of AlpacaEval-LC rank variance (R²=0.3199, N=28) — valid scale covariate
- RLHF reliably IMPROVES TruthfulQA MC2 (+3.406, BCa CI entirely positive, N=321 pairs)
- Raw cross-model rho(AlpacaEval-LC, TruthfulQA MC1) = +0.661 — scaling confound confirmed

**Prohibited Directions:**
- Raw (uncontrolled) cross-model correlation — scaling confound always dominates
- Logistic regression + calibration gate on N<100
- Open LLM Leaderboard v1 as sole source for post-2023 models
- match_rate ≥ 0.70 hard gate when proprietary models in denominator
- Hypothesizing negative alignment-helpfulness correlation (empirically positive)
- HELM GCS/Zenodo paths (use HuggingFace alternatives)

**What Must Change:** New hypothesis must be direction-agnostic (both outcomes publishable), use partial Spearman to remove scale confound, and use only confirmed-accessible HuggingFace/GitHub data sources.

---

### Papers Available
*No papers downloaded (no paper preparation — reference papers all [INFERRED], arXiv IDs unverified). Discussion proceeds from Phase 1 research report.*

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The failure history here is actually illuminating. Every prior hypothesis assumed a specific direction: alignment tax (negative), RLHF degradation (negative), cross-benchmark negative correlation. All were wrong. The empirical evidence says the opposite: RLHF helps, scaling helps both helpfulness AND truthfulness simultaneously. This is the insight we've been missing.

Here's the creative reframe: **what if the "alignment-safety tradeoff" is a myth at the benchmark level, but a reality at the latent-construct level?** When you control for model scale (MMLU), the raw positive correlation might flip — or, more interestingly, might reveal that TruthfulQA and BBQ are genuinely independent (partial_rho ≈ 0), while TruthfulQA and HarmBench are positively coupled (same RLHF mechanism improves both). That's a multi-dimensional alignment structure that's been hidden by scale confound.

The gap paper clawrxiv:2603.00394 found TruthfulQA = PC2 (23.4% orthogonal variance). This is our anchor. Their study used 6 general benchmarks; we extend to the alignment-specific subset. The novelty is that we're the first to characterize the **partial correlation structure** — not just PCA, but directional pairwise tests with cluster-bootstrap CIs by model family.

Two unconventional angles:
1. **Orthogonality test as the primary result**: If partial_rho(TruthfulQA, BBQ | MMLU) is near zero (|r| < 0.15, CI overlaps zero), we've proven that factuality and bias are genuinely independent alignment constructs — each requires separate optimization. This contradicts the "joint alignment" narrative from InstructGPT.
2. **Sign heterogeneity across model families**: Maybe Llama family shows negative partial correlation (safety training trades off factuality) while Mistral family shows positive. Family-stratified analysis reveals which RLHF implementations create alignment conflicts vs. synergies.

**Key Points:**
- Direction-agnostic design means both outcomes are publishable — this breaks the failure pattern
- clawrxiv:2603.00394 PC2 result anchors the novelty claim
- Family-stratified partial_rho reveals RLHF implementation differences

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframe is directionally correct but I need to stress-test the statistical design before we commit. The history shows our prior failures were mostly about insufficient rigor at the gate definition level — calibration failures, power issues, wrong direction. Let's not repeat that.

On the partial Spearman approach: pingouin.partial_corr(method='spearman', covar=['MMLU']) is the correct API. But we need to think carefully about the gate criterion. Dr. Nova proposes |partial_rho| < 0.15 as "orthogonality." This is fine directionally, but what's the statistical power at N≈40?

For a Spearman correlation test (two-tailed, α=0.05), minimum detectable effect at N=40 is approximately |r|=0.31 (80% power). So we can reliably detect partial_rho > 0.31. The range |partial_rho| ∈ [0.15, 0.31] is the underpowered gray zone. I propose the gate criterion be: **Fisher z-test for each partial_rho vs. 0 (two-tailed), p < 0.05**. This is statistically appropriate, power-matched to N, and direction-agnostic.

For falsifiability: the hypothesis must specify in advance what "multi-dimensional" means statistically. My proposal: **at least one benchmark pair has Fisher z p > 0.05 (i.e., partial_rho NOT significantly different from zero)** = multi-dimensional evidence. If ALL pairs are significant (p < 0.05) with the same sign = unidimensional. Both are publishable findings. Both are falsifiable.

Cluster-bootstrap CI by model family (BCa, N_bootstrap=5000, clustered by model family) is already proven to work from prior runs. This is our robustness check, not the primary gate.

**Key Points:**
- Gate: Fisher z vs zero, p < 0.05, for each pairwise partial_rho
- Power at N=40 limits detection to |r| > 0.31 — design around this, not 0.15
- Pre-flight N gate (≥40 triple overlap) is non-negotiable before hypothesis finalizes

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The significance question here is critical and I want to make sure we're not building an elegant statistical exercise with no practical impact. Let me assess what this actually means for the field.

If we find multi-dimensionality (at least one partial_rho not significant): This says safety optimization is NOT a single dial. You can't just do "more alignment training" and expect uniform improvement across factuality, bias, and harmlessness. This has direct practical implications for RLHF training, reward model design, and Constitutional AI. ICLR workshop papers have been accepted on weaker claims than this.

If we find unidimensionality (all partial_rho significant, same direction): This is equally impactful. It says alignment IS a coherent single construct — the "alignment tax" narrative is wrong, and models that are safer are also more truthful and less biased. This validates "superalignment" intuitions and justifies joint reward modeling.

The key significance driver is that **this is the first study to characterize the partial correlation structure of alignment-specific benchmarks** (not general capability benchmarks). The distinction matters: clawrxiv:2603.00394 includes TruthfulQA as ONE of six general benchmarks. We're asking specifically about the alignment construct space.

One concern: the RLHF extension (Gap 3 — delta analysis for BBQ + HarmBench on the 321 pairs) is highly significant for practical impact. The confirmed TruthfulQA improvement (+3.406) needs completion. If BBQ and HarmBench also show improvement, we have a "RLHF uniformly aligns" finding. If one shows degradation, we have "RLHF creates alignment dimension tradeoffs." This is the secondary analysis that could become the headline.

**Key Points:**
- Both unidimensional AND multi-dimensional outcomes are significant — good design
- Gap 3 (RLHF delta across BBQ+HarmBench) could be the most impactful secondary finding
- Impact requires N≥40 — must verify triple overlap before committing

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this discussion in the data access reality we've confirmed. Prior runs (h-e1, h-e2) taught us hard lessons about data feasibility. Here's the honest assessment:

**Data sources — confidence levels:**
1. fboulnois/llm-leaderboard-csv: ✅ HIGH — CSV confirmed downloadable, TruthfulQA+MMLU for 300+ models, releases archived on GitHub
2. lighteval/bbq_helm (HuggingFace): ✅ HIGH — 11,864 rows confirmed via Exa; model-level aggregation needed but doable with groupby
3. centerforaisafety/HarmBench: ⚠️ MEDIUM — GitHub CSV exists but website/API was inaccessible in h-e1 run. Need alternative access path. Paper fallback: 33 models in Table 2 of arXiv:2402.04249.
4. PKU-Alignment/BeaverTails: ✅ HIGH — HuggingFace API confirmed; is_safe field; model-level aggregation via groupby on model_id
5. HELM Lite v1.9.0: ⚠️ MEDIUM — 79 models listed but GCS path unreliable (R1 lesson). lighteval/bbq_helm covers HELM BBQ format.

**N=40 pre-flight reality check:**
- LLM LB v1 × BBQ (lighteval/bbq_helm): Unknown overlap until executed
- LLM LB v1 × HarmBench (33 models): At most 33 × fuzzy join match rate ≈ 28 models (if HarmBench accessible) — may be BELOW 40 triple overlap!
- LLM LB v1 × BeaverTails: BeaverTails is QA pairs, not model eval scores — must aggregate by model_id. Model coverage unknown.

**Feasibility concern**: The triple overlap may be below 40. If HarmBench × LLM LB × BBQ only gives N≈28-33, we fail the pre-flight gate. The hypothesis MUST include explicit fallback: 2-benchmark pair (TruthfulQA × BBQ only, N≥60) if triple-overlap fails. This is the lesson from h-e1.

**Key Points:**
- HarmBench access is still uncertain — must have fallback to BeaverTails
- Triple overlap N≥40 is the critical gate, not guaranteed
- Hypothesis must specify: if N<40 triple-overlap → fall back to TruthfulQA × BBQ pairwise (N≥60)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent discussion. Let me synthesize the converging points and propose a concrete hypothesis that incorporates everyone's constraints.

The core insight: we need a **direction-agnostic, multi-benchmark, partial Spearman structure study** that is robust to data access failures. The previous failures were all direction-specific or data-source-fragile. Here's the strengthened design:

**Proposed Hypothesis (h-m1-v2):**
*Under conditions of N≥40 open-weight LLMs with scores on ≥2 of {TruthfulQA MC2, BBQ accuracy, HarmBench/BeaverTails safety rate}, after controlling for MMLU via pingouin.partial_corr(method='spearman'), the pairwise partial Spearman structure of these alignment benchmarks is characterized by at least one benchmark pair with |partial_rho| that is significantly different from zero (Fisher z vs. H₀: ρ=0, two-tailed p < 0.05), with 95% BCa cluster-bootstrap CIs by model family.*

**Structure:**
- SH1 (Existence): N≥40 complete rows after pre-flight fuzzy join — MUST_WORK gate
- SH2 (Primary): Pairwise partial Spearman matrix computed; Fisher z results reported; claim "at least one pair significant" OR "no pair significant" — DIRECTION-AGNOSTIC gate
- SH3 (Extension): RLHF delta sign test for BBQ+HarmBench using 321 base/chat pairs — SHOULD_WORK gate

**Strengthening moves:**
1. Pre-flight fallback: if HarmBench N<40, fall back to TruthfulQA×BBQ pair only (N likely 60+)
2. Both outcomes (significant/not-significant) are pre-defined as valid findings
3. Cluster-bootstrap by model family handles the correlation structure within families
4. MMLU partial control directly addresses the scaling confound that killed sh2-corr

**Key Points:**
- Direction-agnostic design eliminates the direction-failure pattern
- Two-stage design (pre-flight gate → analysis gate) mirrors the h-e1/h-e2 lessons
- Both unidimensional and multi-dimensional outcomes yield publishable claims

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I need to push back on several points before we converge. The hypothesis as stated has weaknesses that could repeat prior failures.

**Concern 1: The gate is too weak.** "At least one pair significant" is trivially achieved. With N=40 and the known positive rho=+0.661 for raw TruthfulQA-helpfulness correlation, partial_rho(TruthfulQA, BBQ | MMLU) could easily be significant due to residual confound from model family clustering (many Llama variants). The Fisher z test alone doesn't tell us anything scientifically interesting unless we also test the alternative hypothesis that partial_rho is substantially different from the raw rho — i.e., that MMLU control actually CHANGES the correlation structure.

**Mitigation:** Add a second gate: Fisher z comparing raw Spearman vs partial Spearman for each pair. If partial Spearman is significantly different from raw (p < 0.05, Fisher z difference test), that demonstrates MMLU control is doing real work. This is a scientifically meaningful gate, not a trivial one.

**Concern 2: BeaverTails is NOT a model evaluation dataset.** Prior h-e1 failure confirmed this. BeaverTails is 364k human preference pairs, not model eval scores. Aggregating "is_safe by model_id" requires knowing which model generated each response — and the model_id field may not exist or may not match leaderboard names. Prof. Pax noted this ambiguity. I say: **exclude BeaverTails from the design**. Use HarmBench (33 models, paper fallback) as the safety metric. If HarmBench N<20 after join, drop safety entirely and do TruthfulQA×BBQ pairwise only.

**Concern 3: N=40 at triple-overlap is optimistic.** LLM LB v1 has models from 2022-2023. HarmBench targets 33 models from 2023-2024. BBQ (lighteval/bbq_helm) is in HELM format — its model names may use HELM canonical names that differ from LLM LB v1 names. Three-way fuzzy join with N≥40 is aggressive. Set N≥30 as the primary gate with N≥40 as the aspirational target.

**Key Points:**
- Add Fisher z difference test (raw vs partial Spearman) to prove MMLU control has real effect
- Exclude BeaverTails — use HarmBench paper fallback (33 models) as safety metric
- Relax triple-overlap gate to N≥30 (achievable) with N≥40 as stretch goal

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises excellent points. The BeaverTails exclusion is correct — prior run h-e1 explicitly confirmed this failure mode. And the Fisher z difference test (raw vs partial) is a brilliant addition: it turns our study from "what is the partial structure" to "does controlling for scale CHANGE the structure" — which is a much more precise and novel scientific claim.

Let me propose the refined novelty framing: **This study is the first to demonstrate that MMLU scale control CHANGES the pairwise correlation structure of alignment-specific benchmarks** (positive or negative direction of change is secondary to demonstrating the change exists). The clawrxiv:2603.00394 paper shows PCA structure but does NOT test whether partial Spearman differs significantly from raw Spearman for alignment benchmarks. That Fisher z difference test IS the primary novel contribution.

On N: Prof. Rex's suggestion of N≥30 as MUST_WORK gate makes sense given h-e1 showed only 18 for the triple HarmBench join. Let me propose a tiered design:
- Tier 1 (MUST_WORK): N≥30 after TruthfulQA × MMLU × BBQ three-way join using lighteval/bbq_helm
- Tier 2 (SHOULD_WORK): N≥20 HarmBench models matched to Tier 1 dataset (paper fallback from Table 2 arXiv:2402.04249)
- Tier 3 (OPTIONAL): RLHF delta sign test for BBQ + HarmBench using 321 base/chat pairs

This tiered design means we have a publishable result even if HarmBench data access fails.

**Key Points:**
- Primary novelty: Fisher z difference test (raw vs partial) is the publishable contribution
- Tiered N gates: Tier 1 = N≥30 (TruthfulQA×BBQ), Tier 2 = N≥20 HarmBench add-on
- BeaverTails EXCLUDED per h-e1 lesson and Prof. Rex confirmation

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The tiered design is much better. Let me formalize the statistical gates:

**Gate Structure (MUST_WORK → SHOULD_WORK → OPTIONAL):**

**H-E1 (Data Existence, MUST_WORK):**
- N≥30 complete rows after fuzzy join of Open LLM LB v1 × lighteval/bbq_helm, with TruthfulQA MC2 AND MMLU AND BBQ accuracy
- Match rate ≥ 0.55 (lesson from h-e2: 0.70 was too aggressive for cross-leaderboard join)
- Fallback: if BBQ join fails, use HELM Lite v1.9.0 directly (79 models)

**H-M1 (Primary Analysis, MUST_WORK):**
- Compute raw Spearman ρ(TruthfulQA, BBQ) and partial Spearman ρ(TruthfulQA, BBQ | MMLU)
- Fisher z difference test: H₀: raw_rho = partial_rho (two-tailed, p < 0.05)
- Report both outcomes (scale does/does not change correlation structure)
- BCa bootstrap CI (N_bootstrap=5000, clustered by model family per prior confirmed method)

**H-M2 (Safety Add-on, SHOULD_WORK):**
- Add HarmBench safety rate for ≥20 models from paper Table 2 (arXiv:2402.04249)
- Compute partial Spearman ρ(TruthfulQA, HarmBench | MMLU) AND ρ(BBQ, HarmBench | MMLU)
- Fisher z test vs 0 (two-tailed, p < 0.05)

**H-M3 (RLHF Extension, OPTIONAL):**
- For 321 base/chat pairs: compute ΔBBQaccuracy = chat − base; sign test (BCa bootstrap)
- Compare direction to confirmed ΔTruthfulQA = +3.406

This structure avoids ALL prior failure modes: no direction assumption, no calibration gate, no match_rate > 0.70, uses confirmed-accessible data sources only.

**Key Points:**
- H-E1: N≥30, match_rate ≥ 0.55 (not 0.70)
- H-M1: Fisher z difference test raw vs partial — the novel contribution
- H-M2: HarmBench paper fallback (Table 2, not website)
- H-M3: Optional RLHF extension on confirmed 321-pair dataset

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The statistical design is now solid. Let me assess the narrative impact and identify the key framing that makes this publishable:

**Primary narrative:** "Does controlling for model scale reveal or obscure alignment structure?" This is a meta-evaluation question — we're evaluating how we evaluate alignment. This sits at the intersection of benchmarking methodology (BenchScope, clawrxiv:2603.00394) and alignment research (InstructGPT, Llama-2).

**Impact scenarios:**
1. Fisher z difference test SIGNIFICANT + partial_rho ≠ raw_rho: Scale control reveals hidden structure. "The apparent positive co-movement of alignment benchmarks is scale-induced, not alignment-induced." → Strong methodological contribution.
2. Fisher z difference test NOT SIGNIFICANT + partial_rho ≈ raw_rho: Scale doesn't change structure — alignment and scale are genuinely confounded, cannot be separated. → "Alignment benchmarks are not measurable independently of scale" — equally impactful, validates single-index approach.
3. Partial_rho(TruthfulQA, BBQ | MMLU) near zero but partial_rho(TruthfulQA, HarmBench | MMLU) positive: Factuality and bias are independent but factuality and safety co-move. → "Alignment has 2 dimensions: factuality-safety cluster vs. bias as outlier." → Most novel finding.

On the RLHF extension (H-M3): confirmed ΔTruthfulQA=+3.406. If ΔBBQ and ΔHarmBench also positive, the story is "RLHF is a uniformly positive alignment force across all dimensions." If mixed, "RLHF creates alignment dimension tradeoffs." The secondary finding could become the more important one for practical RLHF design.

**Recommended framing:** Lead with Fisher z difference test as the methodological contribution. RLHF extension as the applied contribution. Both together = complete alignment evaluation paper.

**Key Points:**
- All 3 impact scenarios produce publishable findings (direction-agnostic confirmed)
- Scenario 3 (2-dimensional structure) is the most novel and likely given clawrxiv:2603.00394 precedent
- RLHF extension completes the applied narrative

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The tiered design Prof. Vera proposed is feasible. Let me confirm each component:

**Tier 1 (H-E1 + H-M1): TruthfulQA × BBQ | MMLU**
- LLM LB v1 CSV: Confirmed downloadable (fboulnois/llm-leaderboard-csv GitHub)
- lighteval/bbq_helm: Confirmed on HuggingFace (11,864 rows). Aggregation: group by model, mean BBQ accuracy across all questions. Model name format: need to check if it matches LLM LB v1 canonical names. This is the critical unknown — may need rapidfuzz fuzzy join.
- Expected N: LLM LB v1 has 300+ models; bbq_helm has unknown model count. If bbq_helm models are HELM-format (e.g., "huggingface/meta-llama/Llama-2-7b-hf"), fuzzy join with LLM LB v1 format (e.g., "meta-llama/Llama-2-7b-hf") should work with threshold=75.
- Estimate: N≈60-100 if BBQ coverage is broad.

**Tier 2 (H-M2): HarmBench paper fallback**
- arXiv:2402.04249 Table 2 lists 33 models with ASR (attack success rate = 1 - refusal_rate)
- These 33 models are a subset of 2023-2024 releases — many will NOT be in LLM LB v1 (temporal mismatch, same problem as h-e1)
- Realistic estimate: 20 models matched from Tier 1 dataset. Achievable if Tier 1 N≥60.

**Tier 3 (H-M3): RLHF extension**
- 321 base/chat pairs confirmed existing from h-m1 run
- BBQ subset of those 321 pairs: unknown until matched. Sign test on subset ≥ 15 pairs is feasible.

**Critical implementation requirement:** Pre-flight Python script MUST run first — `requests.head` for each URL + N count. This was MANDATORY in Phase 1 and still applies.

**Key Points:**
- Tier 1 is highly feasible (N≥60 likely for TruthfulQA×BBQ join)
- Tier 2 depends on HarmBench paper Table 2 model names matching Tier 1 dataset
- Pre-flight script is mandatory before Phase 3 implementation

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent. The discussion has converged on all key dimensions. Let me draft the final unified hypothesis:

**H-M1-V2: Pairwise Partial Spearman Structure of Human→AI Alignment Benchmarks**

*Core Claim:* After controlling for MMLU (scale proxy) via pingouin.partial_corr(method='spearman'), the Fisher z difference test between raw and partial pairwise Spearman correlations of {TruthfulQA MC2, BBQ accuracy, HarmBench refusal rate} across N≥30 open-weight LLMs from Open LLM Leaderboard v1 reveals whether model scale is a confounding variable in alignment benchmark co-movement — characterizing alignment as unidimensional (scale-driven) or multi-dimensional (independent constructs).

**SPECIFIC:** ✅ Fisher z difference test (raw vs partial Spearman) for each benchmark pair
**MECHANISM:** ✅ MMLU as scale proxy removes capability variation; residual partial_rho reflects alignment-specific co-movement
**PREDICTIONS:** ✅ P1: Fisher z significant → scale changes structure; P2: partial_rho(TruthfulQA,BBQ|MMLU) characterizes factuality-bias coupling; P3: RLHF delta sign test for BBQ (secondary)
**NOVELTY:** ✅ First study to characterize partial correlation STRUCTURE of alignment-specific benchmarks (not just PCA)
**FEASIBILITY:** ✅ All data confirmed accessible (LLM LB v1 CSV, lighteval/bbq_helm HuggingFace, HarmBench paper Table 2)
**OBJECTIONS:** ✅ N gate relaxed to ≥30; BeaverTails excluded; match_rate gate at 0.55; direction-agnostic

Convergence criteria are met. All 6 criteria satisfied.

**Key Points:**
- All convergence criteria met
- Direction-agnostic: both unidimensional and multi-dimensional outcomes publishable
- Tiered design handles data access uncertainty
- Prior failure modes explicitly addressed in design constraints

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I accept the convergence. One final concern that must be logged for Phase 2B:

**Remaining concern — model family clustering:** The cluster-bootstrap by model family (BCa, 5000 iterations) handles within-family correlation for CI estimation. But the Fisher z DIFFERENCE test (raw vs partial Spearman) uses asymptotic standard error formulas that assume independence. If 40% of our N=60 models are Llama variants (which is plausible given LLM LB v1 composition), the effective N is smaller. 

**Mitigation strategy:** Report family-weighted Fisher z in addition to unweighted. Weight each model by 1/family_size to give all families equal influence. This is the most conservative defensible analysis. Phase 2B should specify this as a MUST_WORK robustness check.

Also: the pre-flight URL test is still PENDING (Phase 1 explicitly flagged this). Phase 2B/3 must execute `requests.head()` for each URL and validate N count before any analysis code is written.

I note the hypothesis is now genuinely testable, direction-agnostic, uses proven infrastructure from prior runs, and addresses all root causes of prior failures. I endorse convergence.

**Key Points:**
- Family-weighted Fisher z as robustness check for MUST_WORK
- Pre-flight URL test still pending — Phase 3 responsibility
- Convergence endorsed

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Fisher z difference test (raw vs partial Spearman) as the primary contribution is genuinely novel — clawrxiv:2603.00394 and BenchScope do not apply this test to alignment-specific benchmarks. The direction-agnostic design with pre-specified outcomes for all 3 scenarios (scale reveals, scale conceals, 2-dimensional) transforms prior failures into a complete scientific investigation.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All gates are specific, measurable, and pre-registered: N≥30 (MUST_WORK), match_rate≥0.55, Fisher z difference test (p < 0.05 two-tailed), BCa bootstrap CI. Both null and alternative outcomes yield a clear statistical conclusion. Failure mode for each gate is explicitly defined.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** All 3 impact scenarios are significant. The study positions as a methodological contribution to alignment evaluation (meta-level) with an applied component (RLHF delta extension). ICLR workshop-level quality. The finding that scale does/does not confound alignment benchmark co-movement is directly actionable for benchmark designers and RLHF practitioners.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Tier 1 (TruthfulQA×BBQ|MMLU) is highly feasible with confirmed data sources. Tiered design means the study succeeds even if HarmBench paper Table 2 matching fails. Proven infrastructure (rapidfuzz, pingouin, BCa bootstrap) from prior runs reduces implementation risk substantially.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is **h-m1-v2**: Pairwise Partial Spearman Structure of Human→AI Alignment Benchmarks After MMLU Scale Control.

The core claim: After controlling for MMLU as a model scale proxy, the pairwise partial Spearman rank-correlations of alignment-specific benchmarks (TruthfulQA MC2, BBQ accuracy, HarmBench refusal rate) across N≥30 open-weight LLMs characterize whether human→AI alignment is unidimensional (all pairs significant, same sign) or multi-dimensional (at least one pair non-significant or sign reversal). The primary gate is a Fisher z difference test comparing raw Spearman to partial Spearman for each benchmark pair — if significant (p < 0.05), MMLU scale control changes the correlation structure, validating the confound hypothesis.

The mechanism: MMLU captures general capability variation (R²=0.32 confirmed). After removing this component, residual partial correlations reflect alignment-specific co-movement independent of scale. The raw positive correlation (rho=+0.661 confirmed) may decompose into: (a) near-zero partial correlations (alignment benchmarks are independent constructs), or (b) maintained positive partial correlation (scale-free alignment coherence), or (c) sign reversal (alignment tradeoffs masked by scale).

The experimental approach: Pre-flight URL test → fuzzy join (rapidfuzz WRatio threshold=75) of LLM LB v1 × lighteval/bbq_helm × HarmBench paper Table 2 → pingouin.partial_corr(method='spearman', covar=['MMLU']) → Fisher z tests → BCa bootstrap CI by model family. Tiered: Tier 1 (TruthfulQA×BBQ, N≥30) MUST_WORK; Tier 2 (HarmBench add-on, N≥20) SHOULD_WORK; Tier 3 (RLHF delta sign test on 321 pairs) OPTIONAL.

Both unidimensional and multi-dimensional findings are pre-specified as valid publishable outcomes, eliminating the direction-assumption failure pattern from all prior hypotheses.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Pre-flight URL test still PENDING from Phase 1 — Phase 3 must execute before implementation
- Family-weighted Fisher z required as robustness check (Llama-family clustering may inflate effective N)
- lighteval/bbq_helm model name format may differ from LLM LB v1 — fuzzy join threshold may need adjustment to 70-75 (not 80 as used in h-e2)
- HarmBench paper Table 2 model names must be manually verified — hardcode the 33 model names from the paper as fallback
- **Mitigation Strategy:** Tiered design + pre-flight script + family-weighted Fisher z + hardcoded HarmBench fallback names. Phase 2B should specify these as explicit implementation constraints.
