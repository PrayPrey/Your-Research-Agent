# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap-1-cross-benchmark-transfer
**Gap Title:** Cross-Benchmark Domain Transfer of Uncertainty-Based Detectors
**Priority:** HIGH + PRIMARY

### Research Gap Description

Existing works (Kuhn 2023, Manakul 2023) evaluate semantic entropy and consistency methods on individual benchmarks. Cross-benchmark transfer is mentioned but not systematically tested. The missing piece is systematic evaluation of whether uncertainty thresholds calibrated on one benchmark (e.g., TriviaQA) transfer to other factual QA benchmarks (HaluEval, FEVER, NQ) without recalibration.

### Key Literature

| Paper | Year | Citations | Key Contribution |
|-------|------|-----------|------------------|
| Kuhn et al. "Semantic Uncertainty" | 2023 | 859 | Semantic entropy via bidirectional entailment; evaluated TriviaQA, SQuAD, BioASQ separately |
| Manakul et al. "SelfCheckGPT" | 2023 | 1115 | Consistency-based black-box detection |
| Kadavath et al. "LMs Know What They Know" | 2022 | 1856 | P(True) calibration improves with model size |
| Wang et al. "RACE" | 2025 | 19 | Reasoning + answer consistency; entropy-based uncertainty |
| Xue et al. "Verify when Uncertain" | 2025 | 16 | Cross-model consistency checking |

### Implementation Resources

| Repository | Stars | Key Feature |
|------------|-------|-------------|
| jlko/semantic_uncertainty | 411 | Official Nature paper implementation; supports TriviaQA, SQuAD, BioASQ, NQ |
| cvs-health/uqlm | 1183 | Unified UQ API for multiple methods |
| potsawee/selfcheckgpt | 628 | BERTScore, NLI, n-gram variants |

### Research Question

Can uncertainty-based hallucination detectors (semantic entropy, consistency methods) generalize across factual QA benchmarks without recalibration, and what factors determine transfer success?

### Feasibility Constraints (MANDATORY)

- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data or future follow-up data
- No human evaluation or subjective scoring
- Must use existing real datasets and existing benchmarks only

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this transfer problem all wrong? The current literature treats benchmark transfer as a calibration problem—tune thresholds on TriviaQA, hope they work on HaluEval. But what if the real insight is that uncertainty signals are *structurally different* across benchmark types?

Consider this: TriviaQA tests factual recall with clear-cut answers. HaluEval includes knowledge hallucinations, summarization errors, dialogue inconsistencies—fundamentally different error types. FEVER requires verification reasoning. The semantic entropy that captures "I'm uncertain about Napoleon's birth year" might be mechanistically different from the entropy of "I'm uncertain whether this claim contradicts this evidence."

What excites me is a potential paradigm shift: instead of asking "does the threshold transfer?", we should ask "what features of the uncertainty distribution transfer?" Maybe the raw AUROC doesn't transfer, but the *shape* of the uncertainty distribution (bimodality, tail behavior, entropy-accuracy correlation slope) is invariant. That would be a much more profound finding—invariant structural properties rather than threshold portability.

Cross-domain connection from domain adaptation literature: we don't expect classifiers trained on ImageNet to work on medical images without adaptation. Why would we expect uncertainty thresholds to transfer across fundamentally different QA tasks? The novelty could be in characterizing *what* transfers (structural properties) vs. *what* doesn't (absolute thresholds).

**Key Points:**
- Reframe from "threshold transfer" to "structural property transfer"
- Investigate distribution shape invariants (bimodality, correlation slopes)
- Draw parallel to domain adaptation—characterize what CAN transfer

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the creative reframing, but let me stress-test this. You propose studying "structural properties" of uncertainty distributions—bimodality, tail behavior, correlation slopes. These are measurable, which is good. But we need falsifiable predictions with precise criteria.

Here's my concern: "structural invariance" is vague without operationalization. Let me propose testable specifications:

**Testable Prediction 1 (Correlation Invariance):** The Spearman correlation between semantic entropy and binary correctness (correct/hallucinated) remains within ±0.1 across TriviaQA → HaluEval-QA → NQ when computed on the same model. Falsification: correlation varies by more than 0.1 across benchmarks.

**Testable Prediction 2 (AUROC Degradation Bound):** When threshold τ is calibrated on TriviaQA to achieve 0.80 AUROC, applying τ directly to HaluEval-QA yields AUROC ≥ 0.70 (max 0.10 degradation). Falsification: degradation exceeds 0.10.

**Testable Prediction 3 (Distribution Shape):** The uncertainty distribution on correct answers vs. hallucinated answers shows bimodal separation (Cohen's d > 0.8) on all three benchmarks. Falsification: any benchmark shows d < 0.5.

What would disprove the structural invariance hypothesis entirely? If we see that correlation signs flip (positive on TriviaQA, negative on FEVER) or that AUROC degrades below random chance (0.50) on any transfer target. These are strong tests.

The methodology must control for model confounds: same model family, same sampling parameters, same number of generations per query.

**Key Points:**
- Operationalize "structural invariance" with Spearman correlation bounds
- Propose AUROC degradation bound (≤0.10) as practical threshold
- Cohen's d > 0.8 for distribution bimodality as shape invariant test
- Control confounds: same model, sampling, generation count

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why should the field care about cross-benchmark transfer? Let me anchor the significance.

Current state-of-the-art: Kuhn 2023 reports ~0.85 AUROC for semantic entropy on TriviaQA. SelfCheckGPT achieves similar on their WikiBio benchmark. But these are *in-distribution* results. No paper has systematically quantified the *deployment gap*—the performance drop when a detector tuned on one benchmark faces another.

This matters because practical deployment demands generalization. An LLM deployed in healthcare must detect hallucinations about drug interactions (similar to FEVER's verification) AND factual recall errors (similar to TriviaQA). If thresholds don't transfer, every new domain requires expensive recalibration.

What makes this genuinely new vs. incremental? Prior work assumes transfer works and doesn't measure it. We'd be providing the first systematic characterization. That's a contribution at the *methodology* level—establishing how to evaluate detector robustness—not just another benchmark result.

The field impact is substantial if we find that structural properties (Dr. Nova's point) transfer while thresholds don't. That would redirect the field from "better thresholds" toward "invariant features." If nothing transfers, that's equally important—it tells practitioners they must build benchmark-specific detectors.

However, I need 🔬 Prof. Vera's predictions tightened: ±0.1 correlation and ≤0.10 AUROC degradation are useful bounds, but we should specify effect sizes that practitioners would consider "acceptable" vs. "failure." Is 0.70 AUROC acceptable? That depends on application.

**Key Points:**
- First systematic quantification of "deployment gap" for uncertainty detectors
- Contribution at methodology level: how to evaluate detector robustness
- Field impact: redirect from "better thresholds" to "invariant features" (or prove nothing transfers)
- Need practitioner-meaningful success criteria

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. I need to assess whether the proposed mechanism—testing structural invariance of uncertainty distributions—is technically and theoretically sound.

**Mechanism Assessment:**

1. **Semantic entropy computation is well-defined:** Kuhn 2023's algorithm (generate N samples → cluster by bidirectional entailment → compute cluster assignment entropy) is mathematically specified. The jlko/semantic_uncertainty implementation handles TriviaQA, SQuAD, BioASQ, NQ already. ✓ Feasible.

2. **Cross-benchmark evaluation is tractable:** All proposed benchmarks exist with standardized splits:
   - TriviaQA: 87,622 train / 11,313 dev
   - Natural Questions (NQ): open-domain subset available
   - HaluEval: 5,000 QA + 10,000 summarization + 10,000 dialogue samples
   - FEVER: 185,445 claims with evidence labels
   
   These are publicly available. ✓ Feasible.

3. **The correlation/AUROC measurements are standard:** Spearman correlation, AUROC, Cohen's d are implemented in scipy/sklearn. No novel measurement needed. ✓ Feasible.

**Concerns:**

Here's what worries me about the "invariant structural property" mechanism. The hypothesis assumes that uncertainty distributions have transferable structure. But the *types of hallucinations* differ fundamentally:
- TriviaQA: factual recall errors (model doesn't know)
- FEVER: reasoning errors (model can't infer)
- HaluEval: generation errors (model produces incoherent text)

If uncertainty reflects *different cognitive processes* for these error types, there's no reason to expect structural invariance. The mechanism might be scientifically unsound because it conflates distinct phenomena.

**Recommendation:** We should explicitly test the "error type hypothesis"—that transfer success depends on error type similarity, not just benchmark similarity. FEVER may transfer poorly from TriviaQA because they test different capabilities, even though both are "factual."

**Key Points:**
- Computation and evaluation technically feasible with existing tools
- Benchmarks publicly available with standard splits
- Concern: "structural invariance" may conflate distinct error types (recall vs. reasoning vs. generation)
- Recommend adding "error type similarity" as mediating variable

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly. Prof. Pax raises a valid concern about error type conflation. Let me turn that weakness into our hypothesis's strength.

Instead of assuming universal structural invariance, let's hypothesize **conditional transfer**: uncertainty detectors transfer well within error-type families but poorly across them.

Proposed refinement of the core hypothesis:

**H1 (Conditional Transfer):** Semantic entropy-based hallucination detectors exhibit threshold transfer (AUROC degradation ≤ 0.10) *within* error-type families (e.g., TriviaQA → NQ, both factual recall) but not *across* families (e.g., TriviaQA → FEVER, recall vs. reasoning).

This is stronger because:
1. It makes a more nuanced, testable prediction
2. It explains *why* some transfers work and others don't
3. It provides actionable guidance: practitioners should match detector training to deployment error type

Evidence supporting this refinement:
- Kuhn 2023 evaluated separately on factual QA (TriviaQA, NQ) and math reasoning (SVAMP). They didn't report cross-type transfer, but their benchmarks cluster by error type.
- SelfCheckGPT was tested on WikiBio (generation-heavy), different from factual QA.

How do we operationalize "error type family"? I propose:
- **Factual Recall:** TriviaQA, NQ, PopQA
- **Verification/Reasoning:** FEVER, HotpotQA
- **Generation Quality:** WikiBio, HaluEval-Summarization

The experiment design becomes a 2×2: (train benchmark, test benchmark) × (same family, different family). We predict significant interaction: same-family transfer succeeds, cross-family fails.

**Key Points:**
- Refined to "conditional transfer" hypothesis—transfer within error-type families
- Explains mechanism: error type similarity mediates transfer
- Operationalized error type families: Recall / Reasoning / Generation
- Experiment design: 2×2 with predicted interaction effect

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's conditional transfer hypothesis is appealing, but I see several flaws that need addressing.

**Flaw 1: Error type categorization is post-hoc.** You've assigned benchmarks to families (TriviaQA→Recall, FEVER→Reasoning) based on intuition. But is this empirically validated? What if NQ contains significant reasoning questions, or TriviaQA has verification-style items? The categorization must be *grounded in benchmark analysis*, not assumed.

**Flaw 2: Confounding with dataset characteristics.** Transfer failure might stem from:
- Error type difference (your hypothesis)
- Question length distribution differences
- Answer format differences (single word vs. sentence)
- Annotation noise differences
- Domain vocabulary differences (history vs. science)

You're attributing transfer failure to error type without controlling these confounds. Show me evidence that error type, not question length, drives transfer.

**Flaw 3: "AUROC degradation ≤ 0.10" is arbitrary.** Why 0.10? Is this based on practitioner needs? Statistical power analysis? It feels like a convenient number. What would convince me: show that 0.10 degradation is detectable with practical sample sizes (power analysis) and meaningful for deployment (practitioners say 0.70 AUROC is usable).

**Flaw 4: The hypothesis is unfalsifiable as stated.** If cross-family transfer fails, you claim victory. If it succeeds, you might say "those error types were similar after all." You need to commit to which specific benchmark pairs are "same family" vs. "different family" *before* running experiments.

**What would convince me:** Pre-register the error type classification. Run confound analysis (question length, domain). Justify the 0.10 threshold empirically.

**Key Points:**
- Error type categorization needs empirical grounding, not intuition
- Must control confounds: question length, answer format, domain, annotation noise
- 0.10 degradation threshold needs justification (power analysis, practitioner input)
- Pre-register benchmark-to-family assignments to avoid post-hoc fitting

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique is sharp, but it opens an exciting possibility. What if, instead of *assuming* error type categories, we *discover* them from the data?

Here's the paradigm shift: we don't pre-specify which benchmarks are "same family." Instead, we compute the uncertainty distribution on each benchmark and cluster benchmarks by distribution similarity. This is empirical, not intuitive.

**Novel approach:** Use Jensen-Shannon divergence between uncertainty distributions across benchmarks. If TriviaQA and NQ have similar uncertainty distributions, they cluster together—regardless of our intuitions. If FEVER clusters alone, that tells us something.

This addresses Prof. Rex's Flaw 1 (post-hoc categorization) by making it data-driven. The categories emerge from empirical measurement.

Even more exciting: the clustering result *itself* is a finding. If benchmarks cluster by our intuited error types, that validates the error type theory. If they cluster differently (e.g., by answer format), that reveals something new about what drives uncertainty.

Cross-domain connection from computational biology: this is analogous to discovering gene families through sequence similarity rather than assuming them.

**Refined mechanism:** 
1. Compute uncertainty distributions on 6+ benchmarks
2. Cluster benchmarks by JS-divergence of uncertainty distributions
3. Test transfer *within* vs. *across* discovered clusters
4. Report whether discovered clusters align with intuited error types

**Key Points:**
- Discover error type families empirically via distribution clustering
- Use JS-divergence between uncertainty distributions
- Cluster alignment with intuited types is itself a testable finding
- Addresses post-hoc categorization concern

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's data-driven clustering is methodologically sound, but we need to operationalize it precisely.

**Operationalization of Distribution Clustering:**

1. **Uncertainty metric:** Semantic entropy (primary), predictive entropy (secondary), P(True) if available.
2. **Sample size per benchmark:** Minimum 1,000 queries with 10 generations each (10,000 samples per benchmark).
3. **Distribution representation:** Kernel density estimate or histogram (100 bins) of uncertainty scores.
4. **Distance metric:** Jensen-Shannon divergence (symmetric, bounded 0-1).
5. **Clustering algorithm:** Hierarchical agglomerative clustering with Ward linkage.
6. **Cluster quality:** Silhouette score > 0.5 required for meaningful clustering.

**Testable Predictions (refined):**

**P1 (Cluster Discovery):** Benchmarks will cluster into 2-4 groups with silhouette score > 0.5, demonstrating non-trivial structure.

**P2 (Transfer Within Cluster):** Within-cluster transfer shows AUROC degradation ≤ 0.08 (tighter than before).

**P3 (Transfer Across Cluster):** Cross-cluster transfer shows AUROC degradation > 0.15 (significantly worse).

**P4 (Cluster-Error Type Alignment):** Discovered clusters align with intuited error types (Recall/Reasoning/Generation) with Adjusted Rand Index > 0.6.

**Falsification criteria:**
- Silhouette < 0.3: no meaningful benchmark clusters exist
- Within-cluster degradation > 0.15: even "similar" benchmarks don't transfer
- Cross-cluster degradation < 0.08: error type doesn't matter for transfer
- ARI < 0.3: discovered clusters don't align with error type theory

This gives us clear go/no-go criteria.

**Key Points:**
- Operationalized clustering: KDE, JS-divergence, hierarchical clustering, silhouette > 0.5
- Tightened thresholds: within ≤ 0.08, across > 0.15 degradation
- Added ARI > 0.6 for cluster-theory alignment test
- Clear falsification criteria for each prediction

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify this is still technically feasible with the added complexity.

**Feasibility Assessment of Clustering Approach:**

1. **Compute capacity:** 6 benchmarks × 1,000 queries × 10 generations = 60,000 LLM generations. At 100 tokens/generation average, that's 6M tokens. With Llama-2-7B at ~50 tokens/second on single A100, that's ~33 hours. **Feasible but significant compute.**

2. **Entailment model overhead:** Semantic entropy requires pairwise NLI checks. 10 generations → 45 pairs per query → 45,000 NLI calls per benchmark → 270,000 total. DeBERTa-v3-large processes ~500 pairs/second → ~9 minutes. **Feasible.**

3. **Statistical validity:** 1,000 samples per benchmark for silhouette/clustering is adequate. JS-divergence on KDE is well-defined. **Methodologically sound.**

**Concern: Model selection interacts with findings.**

Here's what worries me. The clustering result might depend heavily on which LLM we use. Llama-2-7B might show different uncertainty distributions than GPT-4 or Mistral. This isn't a feasibility concern—it's a validity concern.

**Recommendation:** Run the full experiment on 2 model families minimum (e.g., Llama-2-7B, Mistral-7B). If clustering is robust across models, that strengthens the finding. If clustering differs by model, that's *also* a finding (model-dependent transfer properties).

This doubles compute but is still feasible (~66 hours total) and dramatically strengthens the contribution.

**Key Points:**
- Compute feasible: ~33 hours for single model, ~66 hours for two models
- NLI overhead minimal (~9 minutes total)
- 1,000 samples per benchmark statistically adequate
- Recommend 2+ model families to test clustering robustness

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

This is coming together. Let me evaluate whether the contribution level has risen.

**Initial contribution:** "Does threshold transfer?" — incremental, confirmatory.

**Current contribution:** "What structural properties of uncertainty determine transfer, and can we discover benchmark families empirically?" — methodology-level contribution.

This matters because we've moved from confirming/denying a simple claim to providing:
1. **A new evaluation framework** for detector robustness (distribution-based clustering)
2. **An empirical taxonomy** of benchmarks by uncertainty properties
3. **Actionable guidance** for practitioners (match benchmark family to deployment domain)

The field impact is now substantial. If the discovered clusters align with error types, we validate a theory. If they don't, we discover new structure. Either way, we contribute a reusable methodology.

**Remaining significance gap:** We haven't specified what practitioners *do* with this knowledge. Let me propose:

**Practical implication:** If you deploy a hallucination detector, measure your deployment domain's uncertainty distribution. If it's within 0.1 JS-divergence of a benchmark you've calibrated on, expect direct transfer. If > 0.3 divergence, expect significant degradation—either recalibrate or select a closer benchmark.

This is actionable and novel. No paper currently provides this guidance.

**Key Points:**
- Contribution elevated from "threshold confirmation" to "evaluation framework + empirical taxonomy"
- Three deliverables: clustering framework, benchmark taxonomy, transfer prediction rules
- Actionable practitioner guidance: JS-divergence threshold for transfer prediction
- Field impact: reusable methodology regardless of specific findings

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerged and address Prof. Rex's remaining concerns.

**Synthesis of Refined Hypothesis:**

**Core Claim:** Uncertainty-based hallucination detectors exhibit *conditional transfer*—successful transfer (AUROC degradation ≤ 0.08) within empirically-discovered benchmark clusters, but poor transfer (degradation > 0.15) across clusters. Benchmark clusters emerge from uncertainty distribution similarity (JS-divergence) and correlate with, but are not defined by, error type families.

**Mechanism:**
1. LLMs produce uncertainty signals that reflect error-generation processes
2. Similar error processes → similar uncertainty distributions
3. Thresholds calibrated on one distribution transfer to similar distributions
4. Dissimilar distributions require recalibration

**Addressing Prof. Rex's concerns:**

1. **Post-hoc categorization:** Solved. Categories emerge from data via clustering, not pre-specified.

2. **Confounds:** We should report question length, answer format, and domain distributions per cluster. If clusters correlate perfectly with question length, that's the explanation—not error type. This is a feature, not a bug: we learn what *actually* drives uncertainty structure.

3. **0.10 threshold:** Revised to 0.08 within-cluster, > 0.15 cross-cluster. Justification: 0.08 is approximately one standard error for AUROC on 1,000 samples; 0.15 exceeds 95% CI. We should also report bootstrap CIs.

4. **Pre-registration:** We commit to specific benchmarks (TriviaQA, NQ, HaluEval-QA, FEVER, PopQA, SQuAD) and let clustering discover families. No post-hoc family assignment.

**Evidence supporting the mechanism:** Kuhn 2023's ablation showing semantic entropy > lexical entropy suggests meaning-level structure matters. Our hypothesis extends this: meaning-level structure varies systematically by benchmark.

**Key Points:**
- Conditional transfer hypothesis fully operationalized
- All four Rex concerns addressed with concrete solutions
- Thresholds justified via statistical reasoning (SE, 95% CI)
- Mechanism grounded in prior semantic entropy findings

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Better. But I have two remaining challenges.

**Challenge 1: Circularity risk.**

You're clustering benchmarks by uncertainty distribution, then testing whether transfer works within clusters. By construction, benchmarks with similar uncertainty distributions will have similar AUROC. This might be tautological.

To avoid circularity: cluster on *train set* uncertainty distributions, then evaluate transfer on *held-out test sets*. The clustering must not see the test data that measures AUROC degradation.

**Challenge 2: Sample size for rare clusters.**

If one cluster contains only one benchmark (e.g., FEVER stands alone), you can't test within-cluster transfer. You need at least 2 benchmarks per cluster for meaningful within-cluster analysis.

**Mitigation:** Pre-specify that if any cluster has < 2 benchmarks, report this as "singleton cluster—transfer undefined within." This is honest methodology, not a failure.

**What would now convince me this is strong:**

1. Train/test split to avoid clustering-evaluation circularity
2. Explicit handling of singleton clusters
3. One additional stress test: check if a random baseline (randomly assigned clusters) achieves similar results. If random clustering shows similar within/cross patterns, our clustering adds nothing.

If you address these, I'm satisfied this is rigorous.

**Key Points:**
- Require train/test split to avoid circularity (cluster on train, evaluate on test)
- Singleton cluster handling must be pre-specified
- Add random baseline comparison (random clusters) to prove clustering adds value
- With these, hypothesis is rigorous

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

I'll incorporate Prof. Rex's final requirements into the experimental protocol.

**Final Experimental Protocol:**

**Phase 1: Distribution Estimation (Training Portion)**
- Use 70% of each benchmark (random stratified split) for uncertainty distribution estimation
- Compute semantic entropy on 700 queries per benchmark, 10 generations each
- Build KDE of uncertainty scores per benchmark

**Phase 2: Clustering**
- Compute JS-divergence matrix (6×6 benchmarks)
- Hierarchical agglomerative clustering (Ward linkage)
- Cut dendrogram at silhouette-maximizing threshold
- If any cluster has <2 benchmarks, label as singleton

**Phase 3: Transfer Evaluation (Held-Out Test Portion)**
- Use remaining 30% of each benchmark (300 queries) for AUROC evaluation
- For each benchmark pair (train, test):
  - Calibrate threshold on train benchmark to achieve τ_0.80 (threshold for 0.80 AUROC)
  - Apply τ_0.80 to test benchmark
  - Measure AUROC degradation

**Phase 4: Random Baseline**
- Randomly assign benchmarks to 2-3 clusters (100 permutations)
- Compute within/cross cluster degradation for each permutation
- Report: does discovered clustering significantly outperform random? (permutation test p < 0.05)

**Predictions (final):**

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Meaningful clusters exist | Silhouette > 0.5 | Silhouette < 0.3 |
| P2 | Within-cluster transfer | Degradation ≤ 0.08 | Degradation > 0.15 |
| P3 | Cross-cluster transfer fails | Degradation > 0.15 | Degradation < 0.08 |
| P4 | Clustering beats random | p < 0.05 (permutation test) | p > 0.10 |
| P5 | Clusters align with error types | ARI > 0.6 | ARI < 0.3 |

**Key Points:**
- Train/test split (70/30) avoids circularity
- Singleton clusters explicitly handled
- Random baseline with permutation test added
- Five testable predictions with clear success/falsification criteria

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility check with the complete protocol.

**Compute Budget (Revised):**
- 6 benchmarks × 1,000 queries × 10 generations = 60,000 generations
- 2 model families = 120,000 generations total
- At 50 tokens/sec, ~67 hours of LLM inference

**Statistical Validity:**
- 700 queries for clustering (70% split): adequate for KDE
- 300 queries for AUROC evaluation (30% split): yields SE ≈ 0.02 for AUROC, adequate for 0.08 threshold
- 100 random permutations: adequate for p-value precision

**Resource Requirements:**
- 1-2 A100 GPUs for ~3 days
- DeBERTa-v3-large for entailment (fits on same GPU)
- jlko/semantic_uncertainty codebase supports all proposed benchmarks except PopQA (minor modification needed)

**Remaining Concern:**

The 70/30 split reduces effective sample size for rare benchmarks. PopQA has ~14,000 questions—fine. But if any benchmark has <500 questions total, the 30% held-out set is statistically underpowered.

**Check:** 
- TriviaQA: 11,313 dev ✓
- NQ: ~8,000 open-domain ✓
- HaluEval-QA: 5,000 ✓
- FEVER: 185,445 ✓
- PopQA: 14,000 ✓
- SQuAD: 10,570 dev ✓

All benchmarks have adequate sample sizes. **Fully feasible.**

**Key Points:**
- 3-day compute on 1-2 A100s
- All benchmarks have adequate sample sizes (>5,000 each)
- Statistical power adequate with 300-sample held-out test sets
- Minor code modification needed for PopQA integration

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've converged. Let me provide the final synthesis.

**Emerged Hypothesis Summary:**

### Core Statement
Under the scope of factual QA and claim verification benchmarks, if a semantic entropy-based hallucination detector is calibrated on one benchmark and tested on another, then transfer success (AUROC degradation ≤ 0.08) depends on uncertainty distribution similarity between benchmarks, because similar error-generation processes produce similar uncertainty distributions, and thresholds calibrated on one distribution remain effective on statistically similar distributions.

### Causal Mechanism
1. LLMs generate uncertainty signals reflecting specific error-generation processes (factual recall vs. reasoning vs. generation)
2. Benchmarks testing similar processes exhibit similar uncertainty distributions (low JS-divergence)
3. Calibration thresholds effective for one distribution transfer to similar distributions
4. Dissimilar distributions (high JS-divergence) require recalibration

### Variables
- **Independent:** Benchmark pair relationship (within-cluster vs. cross-cluster; JS-divergence)
- **Dependent (Primary):** AUROC degradation when applying source-calibrated threshold to target
- **Controlled:** Model family, sampling temperature, generation count, train/test split

### Key Assumptions
- A1: Semantic entropy is a valid proxy for model uncertainty
- A2: Bidirectional entailment reliably clusters semantic equivalence
- A3: 10 generations per query adequately samples the uncertainty distribution
- A4: KDE accurately represents the uncertainty distribution for JS-divergence computation
- A5: AUROC is an appropriate metric for hallucination detection performance

### Null Hypothesis
H0: There is no significant difference in AUROC degradation between within-cluster and cross-cluster benchmark transfers (i.e., clustering does not predict transfer success).

### Predictions
- P1: Silhouette > 0.5 (meaningful clusters exist)
- P2: Within-cluster degradation ≤ 0.08
- P3: Cross-cluster degradation > 0.15
- P4: Discovered clustering beats random (permutation p < 0.05)
- P5: Clusters align with error types (ARI > 0.6)

### Novelty
First systematic investigation of cross-benchmark transfer for uncertainty-based detectors, introducing empirical benchmark taxonomy via distribution clustering.

### Scope & Boundaries
- Applies to: Factual QA, claim verification, short-form generation (< 100 tokens)
- Does not apply to: Long-form summarization, multi-turn dialogue, creative writing
- Limitations: Single-turn QA setting; English only; 7B-scale models

### Experimental Setup
- Datasets: TriviaQA, NQ, HaluEval-QA, FEVER, PopQA, SQuAD
- Models: Llama-2-7B, Mistral-7B
- Baselines: Random cluster assignment, single-benchmark AUROC

### Related Work & Baselines
- Kuhn 2023: In-distribution AUROC (no transfer analysis)
- SelfCheckGPT: Consistency-based baseline
- Within-cluster vs. cross-cluster transfer is the novel comparison

### Phase 2B Readiness Seeds
- Existence check (SH1): Uncertainty distributions cluster with silhouette > 0.5
- Mechanism test (SH2): Within-cluster degradation < cross-cluster degradation
- Comparison (SH3): Discovered clustering outperforms random baseline

### Established Facts
- Semantic entropy detects hallucinations with ~0.85 AUROC in-distribution [Kuhn 2023] — BUILD_ON
- Model calibration improves with scale [Kadavath 2022] — BUILD_ON
- Cross-benchmark transfer has not been systematically studied — PROVE_NEW

**Key Points:**
- Complete hypothesis with core statement, mechanism, variables, assumptions
- Five falsifiable predictions with quantitative criteria
- Clear scope, limitations, and Phase 2B readiness seeds
- Ready for Phase 2B verification protocol design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis transforms a simple threshold-transfer question into a methodological contribution—discovering benchmark families empirically via distribution clustering. This is paradigm-shifting: instead of assuming benchmark categories, we let the data reveal structure. The JS-divergence clustering approach is genuinely novel in this context.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Five testable predictions with quantitative success/falsification criteria. The train/test split avoids circularity, random baseline provides null comparison, and ARI > 0.6 tests theory alignment. Each prediction can be cleanly falsified with standard statistical methods.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This is the first systematic quantification of the "deployment gap" for uncertainty-based hallucination detectors. The contribution operates at the methodology level—providing a reusable evaluation framework—rather than just another benchmark result. Actionable practitioner guidance (JS-divergence thresholds for transfer prediction) ensures real-world impact.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully feasible with 3-day compute on standard hardware. All proposed benchmarks exist with adequate sample sizes (>5,000 each). The jlko/semantic_uncertainty codebase handles most benchmarks directly. No fundamental barriers—only implementation effort.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a "conditional transfer" hypothesis: semantic entropy-based hallucination detectors transfer successfully (AUROC degradation ≤ 0.08) between benchmarks with similar uncertainty distributions, but fail (degradation > 0.15) across dissimilar distributions. Rather than assuming benchmark categories a priori, we discover them empirically by clustering benchmarks via Jensen-Shannon divergence of their uncertainty distributions.

The core mechanism is that LLMs generate uncertainty signals reflecting specific error-generation processes. Benchmarks testing similar processes (e.g., factual recall) exhibit similar uncertainty distributions, enabling threshold transfer. The hypothesis makes five falsifiable predictions: meaningful clusters exist (silhouette > 0.5), within-cluster transfer succeeds, cross-cluster transfer fails, discovered clustering outperforms random baseline (permutation test), and clusters align with intuited error types (ARI > 0.6).

The experimental approach uses 6 benchmarks (TriviaQA, NQ, HaluEval-QA, FEVER, PopQA, SQuAD), 2 model families (Llama-2-7B, Mistral-7B), and a rigorous train/test split to avoid circularity. This is the first systematic investigation of cross-benchmark transfer for uncertainty detectors, introducing an empirical benchmark taxonomy methodology.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The 0.08/0.15 thresholds, while justified statistically, may not align with practitioner-defined "acceptable" performance. User studies or practitioner surveys could validate these thresholds.
- Model family generalization (Llama-2 vs. Mistral) is tested, but API-only models (GPT-4, Claude) would require different evaluation approaches (P(True) instead of semantic entropy).
- **Mitigation Strategy:** Report threshold sensitivity analysis (how results change at 0.05/0.10/0.15) and discuss API model limitations as future work in the paper.

