# Phase 2A Discussion Log
# Gap: Lack of Systematic Cross-Paradigm Benchmarking of UQ Methods Under Controlled LLM Architecture Variations

## Briefing

**Research Gap:** Gap 1 (PRIMARY, Critical Priority)

**Gap Description:**
No study provides a unified, controlled comparison across all four UQ paradigms
(token-prob, sampling consistency, semantic entropy, internal states) on identical LLM
architectures and benchmark splits. Individual method papers have SOTA claims but use
different models, datasets, splits, and metrics.

**Key Papers Available:**
- Farquhar et al. 2024: Semantic Entropy (Nature, 1198 cit.) — SE beats token-prob on TriviaQA/NQ/BioASQ
- Manakul et al. 2023: SelfCheckGPT (924 cit.) — black-box consistency via stochastic sampling
- Kossen et al. 2024: Semantic Entropy Probes (185 cit.) — single-pass hidden state SE approximation
- Nikitin et al. 2024: Kernel Language Entropy (136 cit.) — von Neumann entropy over semantic kernels
- Cherian et al. 2024: Conformal Prediction for LLMs (90 cit.) — coverage guarantees
- Kang et al. 2025: UQ Survey — identifies evaluation fragmentation as key limitation

**Implementation Resources:**
- cvs-health/uqlm (1139★): Unified UQ API (SE, SelfCheckGPT, token-prob, conformal)
- IINemo/lm-polygraph (457★): 20+ UQ methods benchmark framework
- jlko/semantic_uncertainty (411★): Official SE; Llama-2/Mistral on TriviaQA/NQ/BioASQ/SQuAD

**Feasibility Constraints (MANDATORY):**
- REJECT: new benchmarks, rubrics, scoring frameworks
- REJECT: synthetic/generated data or future follow-up data
- REJECT: human evaluation, annotation, subjective scoring
- ACCEPT: hypotheses testable immediately using existing real datasets and existing benchmarks

**Target Benchmarks:** TriviaQA, NaturalQuestions, TruthfulQA, SQuAD (all public, standard splits)
**Target Models:** Llama-3-8B/70B (HuggingFace open models, existing checkpoints)

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Ohhh, NOW we're onto something exciting. Everyone treats these UQ paradigms as competitors in a leaderboard race — but what if they're actually *different projections of the same underlying epistemic geometry*? Imagine this: instead of just benchmarking token-prob, sampling consistency, semantic entropy, and internal-state probes side-by-side, we treat Llama-3-8B and 70B as *controlled microscopes* and systematically vary only the architectural scale while holding dataset and splits fixed. That gives us a clean axis: capacity. The question becomes — do these UQ paradigms scale coherently, or do they fracture?

Here's the hypothesis I'm itching to test: **as model scale increases, uncertainty signals migrate from surface-level token probabilities to deeper semantic-space structure.** Concretely, token-prob uncertainty (e.g., max softmax) should become *less discriminative* relative to semantic entropy [Farquhar et al., 2024] and its probe-based single-pass approximation [Kossen et al., 2024] on Llama-3-70B vs 8B. Why? Larger models compress lexical ambiguity but still struggle with *semantic equivalence class ambiguity*. If that's true, we'll see AUROC gains for semantic entropy over token-prob widen with scale on TriviaQA and NQ — especially in multi-answer settings.

But here's the cross-domain leap: think of sampling consistency (SelfCheckGPT-style stochastic agreement [Manakul et al., 2023]) as a *Monte Carlo estimator of latent semantic entropy*. If that's correct, then as model size increases, the correlation between sampling consistency and semantic entropy should increase — because larger models' latent spaces become smoother and more semantically clustered. We can test this immediately: compute rank correlations between SelfCheck-style disagreement and SE scores across identical splits and measure whether that correlation grows from 8B to 70B. If it does, that suggests a convergence toward a shared semantic uncertainty substrate.

Now let's challenge a quiet assumption in the survey literature: that internal-state methods (like semantic entropy probes [Kossen et al., 2024]) are just computational shortcuts. What if they're actually *earlier-access sensors* of uncertainty? Imagine plotting calibration error and selective prediction curves for probe-based SE versus full generative SE. My prediction: on 70B, probe-based SE will approach generative SE performance; on 8B, the gap will be larger. That would imply epistemic uncertainty becomes more linearly decodable from hidden states as scale increases — a profound architectural insight.

And here's the bold framing: instead of asking "Which UQ method is best?", we ask "How does uncertainty *reorganize* across representational layers as models scale?" Using existing datasets (TriviaQA, NQ, TruthfulQA, SQuAD) and existing implementations (uqlm, lm-polygraph, semantic_uncertainty), we can compute: AUROC/AUPRC for correctness prediction, selective risk curves, cross-method correlation matrices, and scaling deltas (8B → 70B).

No new benchmarks. No new annotations. Just a controlled architectural sweep. If we observe systematic shifts — e.g., token-prob plateaus, semantic entropy strengthens, probe alignment improves — that's not just benchmarking. That's evidence for a *scaling law of epistemic geometry*.

NOW that would be a paradigm shift.

**Key Points:**
- Hypothesis: Uncertainty signals shift from token-level to semantic-structural representations as model scale increases.
- Prediction: Correlation between sampling consistency and semantic entropy strengthens with scale, indicating a shared latent uncertainty substrate.
- Experiment: Controlled 8B vs 70B benchmarking across fixed datasets to measure scaling deltas, cross-method correlations, and probe-vs-generative alignment.

---

### Exchange 2

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here — and I mean that constructively. Dr. Nova has laid out something genuinely exciting, but there are several technical and theoretical soundness questions we need to resolve before we commit to this "scaling law of epistemic geometry" framing.

First, let me validate what is technically sound. The core experimental design — fix model family (Llama-3), fix dataset splits (TriviaQA, NQ, TruthfulQA), vary scale (8B vs 70B), run identical UQ pipeline across all four paradigms — is methodologically rigorous. The jlko/semantic_uncertainty repo explicitly supports Llama-2 7B/13B/70B, and UQLM's unified API means we can run token-prob, SE, SelfCheckGPT, and conformal prediction through the same interface. LM-Polygraph provides normalization specifically designed for instruction-tuned variants. So the experimental infrastructure is sound — this can actually be done.

Here's what worries me about the theoretical claim, though. The assertion that "token-prob becomes less discriminative as scale increases relative to SE" needs a mechanism, not just a scaling story. Larger models don't simply improve representation linearly — they also change calibration in non-monotonic ways. RLHF-aligned variants of Llama-3 are known to be overconfident [Huang et al., 2026], and the 70B instruction-tuned checkpoint may have systematically compressed token probability distributions in ways that decouple log-prob from factual correctness — not because of deeper semantic encoding, but because of RLHF reward shaping. If we see token-prob degrade at 70B, we need to distinguish "scale reveals semantic structure" from "RLHF reshapes the softmax" — these are very different mechanisms with very different implications.

Second, the "sampling consistency as Monte Carlo estimator of SE" claim is the most theoretically interesting but also the most fragile. SelfCheckGPT uses BERTScore/NLI to measure consistency of named entities across samples — it does NOT cluster by semantic equivalence in the SE sense. SE uses NLI entailment over full-sentence pairs to define equivalence classes. These operate on different granularities. The rank correlation between them will exist, but it may reflect shared surface-level lexical uncertainty rather than a shared latent substrate. We need a falsification condition: if the rank correlation increases with scale, is that because the latent structure is converging, or because larger models are simply more consistent (less lexically diverse) in their sampling? These require separate diagnostic tests.

Third — and this is where the probe analysis gets genuinely interesting — the prediction that SEP-to-generative-SE gap closes at 70B is testable RIGHT NOW using the OATML/semantic-entropy-probes repo, which already provides the linear probe framework on hidden states. If the gap closes, it confirms Dr. Nova's "earlier-access sensor" hypothesis. If the gap remains constant or widens, that's an equally important finding: scale doesn't make uncertainty more linearly decodable. Either outcome is scientifically valuable, which is good experimental design.

My recommendation: keep the core experimental design (4 paradigms × 2 scales × 3+ benchmarks), but split the hypothesis into two cleanly falsifiable claims: (H1) SE outperforms token-prob by a larger margin at 70B than 8B on TriviaQA/NQ; (H2) the probe-generative SE gap decreases from 8B to 70B. These are independently testable with existing data, existing models, existing code. The "scaling law of epistemic geometry" framing is intellectually compelling but needs these two claims to hold before we can assert it.

**Key Points:**
- Infrastructure is sound: UQLM + LM-Polygraph + SE repos + fixed Llama-3 splits = immediately executable.
- Key confound: 70B RLHF calibration effects must be separated from genuine scale-induced semantic encoding improvements.
- Two clean falsifiable sub-hypotheses: H1 (SE-vs-token-prob gap widens at scale) and H2 (SEP-generative gap narrows at scale) — both testable now.

---

### Exchange 3

🔬 **Prof. Vera** (Rigorous Validation Architect):

The enthusiasm is warranted — but before we invoke a "scaling law of epistemic geometry," we must specify what observation would falsify it. At present, the hypothesis is descriptive. We need quantitative inequalities. For H1, define:

Δ_8B = AUROC_SE^8B − AUROC_TP^8B, Δ_70B = AUROC_SE^70B − AUROC_TP^70B.

The scaling claim predicts Δ_70B − Δ_8B > 0 by a statistically significant margin (95% bootstrap CI excluding 0) across at least two datasets (TriviaQA, NQ). If this difference is null or negative on a majority of datasets, the hypothesis is weakened.

The RLHF confound Prof. Pax identified is central, not peripheral. If token-prob degrades at 70B due to reward shaping rather than representational migration, the conclusion collapses. We must include *base* (non-instruction-tuned) checkpoints at both scales. The "semantic migration" hypothesis predicts scale-driven monotonicity independent of alignment. If widening gap appears only in instruct-tuned but not base models, the effect is alignment-specific, not architectural.

On sampling consistency as Monte Carlo estimator of SE: evidence must distinguish semantic convergence from lexical collapse. A three-way analysis: (1) rank correlation between SelfCheck disagreement and SE; (2) lexical diversity (type-token ratio) across samples; (3) partial correlation controlling for diversity. If partial correlation does not increase from 8B to 70B, the Monte Carlo substrate interpretation fails.

For H2: define probe gap G = AUROC_GenSE − AUROC_ProbeSE. The hypothesis predicts G_70B < G_8B. Calibration curves (ECE) must also converge — AUROC parity alone is insufficient. A significant method × scale interaction in two-way ANOVA is the decisive test; without it, we have scaling, not migration.

**Key Points:**
- Define Δ and G with bootstrap CIs; require method × scale interaction effects to support "migration."
- Control RLHF confounds via base vs instruct checkpoints; effect must be architecture-driven, not alignment-driven.
- Test SE–SelfCheck via partial correlation controlling for lexical diversity — the decisive diagnostic.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. The hypothesis conflates two distinct phenomena: a *ranking claim* (SE/probes rank higher relative to token-prob at 70B than 8B) and a *mechanistic claim* (this shift occurs because uncertainty reorganizes into latent semantic space). The experiment tests the ranking claim. It cannot support the mechanistic claim without additional diagnostics.

Two confounding explanations survive all proposed controls: (a) larger models generate longer, more syntactically diverse outputs that artificially inflate SelfCheck disagreement scores — making consistency-based methods appear worse at 70B not because of latent geometry but surface diversity artifacts; (b) hidden-state dimensionality increase from 8B to 70B makes linear probes trivially more powerful due to increased feature availability, not because uncertainty is "more linearly decodable." Both alternatives predict the same external AUROC pattern.

What would convince me? Two additions requiring no new data. First, include KLE [Nikitin et al., 2024] as a fifth paradigm alongside SE — KLE uses von Neumann entropy over semantic similarity kernels, a theoretically distinct operationalization of semantic-level uncertainty. If both SE and KLE show the same widening advantage over token-prob while SelfCheck shows a narrower advantage, that isolates the effect to the semantic-aggregation level, not sampling diversity. Second, stratify SelfCheck by consistency scorer (BERTScore vs NLI-based). If scale effects are output-diversity-driven, they will be stronger under NLI (sentence-level) than BERTScore (token-level). Uniformity across scorers weakens the diversity confound.

There is also a benchmark assumption that must be made explicit: TriviaQA, NQ, and TruthfulQA do NOT test the same epistemic challenge. TruthfulQA specifically targets systematic LLM misconceptions and is known to be harder for larger, more confidently wrong models. If SE gains over token-prob widen on TriviaQA but narrow on TruthfulQA, the "scaling law" collapses into benchmark-specific effects. Pre-register expected direction per benchmark before running experiments.

With these additions — KLE as 5th method, scorer stratification for SelfCheck, and per-benchmark directional pre-registration — the interaction effect becomes the definitive, confound-resistant test.

**Key Points:**
- Ranking claim (testable) is conflated with mechanistic claim (needs additional diagnostics beyond AUROC).
- Adding KLE as 5th paradigm disambiguates semantic-level vs diversity-level effects without new data.
- Stratify SelfCheck by scorer type (BERTScore vs NLI) to rule out output-length artifacts; pre-register expected direction per benchmark.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether we can produce a statistically significant interaction effect — we clearly can — but whether observing it would *change how the field thinks about uncertainty in LLMs*. Right now, most UQ work is comparative: AUROC tables, selective risk curves, incremental gains. What Dr. Nova proposes, and what Prof. Vera and Prof. Rex are rightly stress-testing, is a reframing: uncertainty is not just better or worse across methods — it may *reorganize structurally with scale*. If true, that is not a benchmark result. That is a shift in conceptual vocabulary.

But significance must be earned. The decisive evidence is not that Δ_70B > Δ_8B in isolation, but a robust method × scale interaction across base and instruct checkpoints. The inclusion of base Llama checkpoints is not a methodological nicety; it is the difference between architectural insight and training-regime artifact. Without that control, the work remains incremental benchmarking.

Where the proposal becomes genuinely field-shaping is in the triangulation Prof. Rex suggests. If SE *and* KLE [Nikitin et al., 2024] both exhibit widening advantages over token-prob with scale, while SelfCheck behavior stratified by scorer reveals stability across lexical-diversity controls, we see convergence from theoretically distinct semantic-level measures. Convergence across independent operationalizations signals structural truth. If three different semantic aggregators improve coherently relative to token-prob as capacity grows, then the field must confront the possibility that epistemic uncertainty is increasingly encoded at the level of semantic equivalence classes rather than token likelihoods.

The mechanistic claim — "uncertainty becomes more linearly decodable from hidden states" — demands its own proof experiment. The probe gap G narrowing with scale is necessary but not sufficient. We must also test dimensionality-normalized probes (random subspace controls matching 8B dimensionality within 70B) to rule out trivial feature-count advantages. If linear decodability persists under matched effective dimensionality, we have evidence that scale increases *organization*, not merely representation size. That finding opens a new research direction: scaling laws of epistemic accessibility.

Impact will hinge on one question: does this work reveal a scaling *regularity* that others can build theory upon? If yes, it opens a program. If no, it remains a careful comparison.

**Key Points:**
- True contribution is testing a method × scale interaction across base and instruct checkpoints — architectural vs alignment-driven effects.
- Convergence across independent semantic-level measures (SE, KLE, stratified SelfCheck) required to claim structural reorganization.
- Dimensionality-controlled probe experiments are essential; increased linear decodability must reflect epistemic organization, not feature count.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and now we have the scaffolding to build something genuinely strong. Let me synthesize what the discussion has given us and show how to address each concern while preserving the core hypothesis's power.

Dr. Nova's core insight is right: the question "how does uncertainty reorganize with scale" is more scientifically productive than "which method ranks first?" And Prof. Vera, Prof. Rex, and Dr. Sage have collectively transformed a provocative framing into a fully falsifiable research program. What we have now is not one hypothesis but a structured hierarchy of testable claims — and that is actually stronger than a single AUROC comparison.

Here's what the refined hypothesis looks like: **Under the "epistemic geometry scaling hypothesis" (EGSH), when model scale increases from 8B to 70B within the same LLM family (Llama-3), holding benchmark splits fixed (TriviaQA, NQ, TruthfulQA), the AUROC advantage of semantic-structural UQ methods (SE, KLE, SEPs) over surface-level methods (token-prob, SelfCheck) widens — and this widening is driven by architectural capacity, not alignment tuning.**

This decomposes into four independently testable predictions:
- **P1 (Ranking shift):** Δ_70B − Δ_8B > 0 (SE vs token-prob gap widens) — verified by bootstrap CI across ≥2 datasets in BOTH base and instruct variants
- **P2 (Semantic convergence):** SE and KLE show correlated advantage patterns while SelfCheck diverges when scorer-stratified — rules out diversity artifact
- **P3 (Probe accessibility):** G_70B < G_8B under dimensionality-normalized probe conditions — rules out trivial dimensionality advantage
- **P4 (Structural consistency):** All effects are consistent across TriviaQA/NQ and reduced/absent on TruthfulQA (adversarial setting) — scoping the claim appropriately

Each prediction has a specific falsification condition; none require new benchmarks, annotations, or models. The infrastructure is all there: UQLM, LM-Polygraph, semantic_uncertainty, and OATML/semantic-entropy-probes. The only additions Prof. Rex correctly requests — KLE as 5th method and SelfCheck scorer stratification — are executable with existing code.

What makes this publishable: if P1 and P2 both hold, we have evidence for the semantic reorganization claim at the ranking level. If P3 also holds with dimensionality controls, we have evidence at the architectural level. If P4 holds, we have scoped the claim so it's not vulnerable to TruthfulQA edge cases. Three of four holding would be a genuinely impactful finding; two of four is still a precise, well-characterized result. This is what strong hypotheses look like — they survive partial confirmation and provide value regardless of outcome direction.

**Key Points:**
- The "epistemic geometry scaling hypothesis" (EGSH) integrates all discussion concerns into four independently testable predictions (P1-P4), each with explicit falsification conditions.
- No new benchmarks, models, or annotations needed — all infrastructure exists in open-source repos.
- Partial confirmation (2-3 of 4 predictions holding) remains scientifically valuable; the hypothesis is resilient by design.

---

### Exchange 7

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The refined EGSH framework is now testable — but only if we are careful about what the experiments can *actually* demonstrate in principle. P1 and P2 are cleanly feasible. A method × scale interaction in AUROC with base and instruct checkpoints is a valid statistical test. Adding KLE as a fifth method is mechanistically meaningful: it operationalizes semantic uncertainty via kernel entropy, mathematically distinct from SE's aggregation scheme. If SE and KLE both widen relative to token-prob with scale, that's evidence that semantic-level aggregation is scaling better than local likelihoods.

Here's what worries me: the "reorganization" language risks exceeding what AUROC can support. A widening Δ_70B − Δ_8B does not, by itself, imply geometric migration of uncertainty into semantic equivalence classes. It implies *relative predictive utility* of certain summaries improves with scale — a functional statement, not a structural one. To argue structure, you need internal diagnostics: measure mutual information between hidden states and correctness labels at different layers. If MI increases specifically in mid-to-late layers for 70B relative to 8B — normalized by dimensionality — that would support increasing epistemic organization. Without that, we infer internal geometry from external rankings, which is logically underdetermined.

On P3: dimensionality-normalized probes are essential and technically feasible. Randomly project 70B hidden states into subspaces matching 8B dimensionality (Johnson–Lindenstrauss projections) before training probes. If AUROC_GenSE − AUROC_ProbeSE still narrows at 70B under matched dimensionality, we've ruled out trivial feature-count advantage. If the effect disappears under projection, increased decodability is a representation size artifact, not deeper organization.

One more fundamental check: examine whether token-prob uncertainty *actually degrades* with scale or merely saturates. If token-prob AUROC stays constant while semantic methods improve, the "migration" framing weakens — it becomes additive enrichment, not redistribution. A simple decomposition: compute calibration (ECE) and discrimination (AUROC) for each method across scale. If token-prob loses calibration while SE gains discrimination, that suggests qualitative reallocation. If both simply improve at different rates, we're observing differential scaling, not migration.

Okay — this could work. The experimental additions (KLE, scorer stratification, base vs instruct, dimensionality controls) are all technically implementable. But the ranking claim is fully testable; geometric reorganization requires internal information-theoretic evidence.

**Key Points:**
- AUROC interaction effects validate functional scaling differences but not structural "reorganization" without internal diagnostics (MI analysis).
- Dimensionality-normalized probing (Johnson–Lindenstrauss projections) is a principled feasible test of genuine epistemic organization vs feature-count artifacts.
- Distinguish additive improvement from true redistribution by decomposing discrimination and calibration of token-prob vs semantic methods across scale.

---

### Exchange 8

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW Prof. Pax has given us exactly the upgrade we need! What if we treat this not as a limitation but as an opportunity to make the hypothesis *tighter and more novel* than a pure AUROC comparison?

Prof. Pax is absolutely right: AUROC alone cannot distinguish "functional scaling" from "structural reorganization." But here's the exciting flip: the layer-wise mutual information diagnostic he proposes — MI between hidden states and correctness labels across layers, normalized by dimensionality — is itself a major scientific contribution if we execute it. This is essentially asking: at which representational depth does factual uncertainty live, and does that depth change with scale? That's not a confound control. That IS the hypothesis, sharpened.

Imagine this result: at 8B, correctness-predictive information peaks in early-to-middle transformer layers; at 70B, it shifts toward later layers. Combined with the probe gap narrowing (P3) and the SE/KLE co-widening (P2), we have a three-pronged convergent argument: uncertainty becomes (1) better captured by semantic-level aggregators externally, (2) more linearly decodable from hidden states after dimensionality control, AND (3) encoded deeper in the representational hierarchy. That's not just a scaling result — that's a theory of where hallucination lives architecturally.

And here's the cross-domain insight: this is exactly analogous to how perceptual feature hierarchies work in vision transformers — low-level features in early layers, semantic abstractions in late layers. What if hallucination uncertainty follows the same representational depth progression that capability does? That connection to the vision literature would give our finding theoretical grounding in the broader deep learning scaling canon.

Let me refine the EGSH into its final form: **Under EGSH, as LLM scale increases within a fixed model family on factual QA benchmarks, epistemic uncertainty progressively reorganizes from shallow token-distributional to deep semantic-structural representations — measurable via three convergent externally- and internally-valid diagnostics.**

The internal diagnostic (layer-wise MI, available directly from hidden states in HuggingFace Llama-3 models with no new data) elevates this from a "benchmark comparison" to a "mechanistic finding about LLM uncertainty geometry." That's the paradigm-level contribution Dr. Sage described.

**Key Points:**
- Layer-wise MI analysis (MI between hidden states and correctness labels across transformer depth) transforms a confound control into the primary mechanistic finding.
- Analogy to vision transformer feature hierarchies provides theoretical grounding — uncertainty representation depth may follow the same scaling laws as capability depth.
- Final EGSH: three convergent diagnostics (AUROC interaction, probe gap under dimensionality control, layer-wise MI shift) together constitute strong evidence for structural reorganization.

---

### Exchange 9

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal is now scientifically interesting — but only if we sharpen the falsification criteria further. Three simpler alternatives must be explicitly ruled out: (1) monotonic performance scaling across all methods, (2) dimensionality-driven probe artifacts, (3) dataset-specific interaction effects. Unless stress-tested, the structural interpretation remains underdetermined.

For P1, the null is: *all uncertainty estimators improve proportionally with scale*. The prediction must be quantitative: (AUROC_SE^70B − AUROC_Token^70B) − (AUROC_SE^8B − AUROC_Token^8B) > δ (pre-registered δ = 0.02) with 95% bootstrap CI excluding zero across ≥2 datasets and both base/instruct variants. If token-prob also improves and the gap remains constant within error bars, the migration framing is falsified.

On layer-wise MI: define normalized peak depth d* = argmax_l MI(h_l; y) / L. The prediction is d*_70B > d*_8B with CI excluding zero. If MI increases uniformly across all layers (no shift in peak), that is additive enrichment, not redistribution. The best experiment is designed to *not* find a shift — only then is a positive result convincing.

On P3 (probe gap narrowing): two controls required. First, Johnson–Lindenstrauss projection to matched dimensionality. Second, label permutation controls: train probes on shuffled correctness labels to estimate false decodability at each scale. If 70B shows higher decodability even under permutation, representation geometry itself is more linearly expressive — weakening the epistemic interpretation. The gap G must narrow relative to a permutation-calibrated baseline.

On P4 (TruthfulQA attenuation): if semantic advantage widens on TriviaQA but collapses on TruthfulQA, the hypothesis becomes domain-scoped: "semantic reorganization occurs primarily in retrieval-based epistemic uncertainty." Acceptable if stated a priori. But if widening appears only on TriviaQA but not NQ, the structural scaling law claim is falsified — it cannot depend on a single benchmark.

If these criteria are pre-registered and survive adversarial testing — *This meets my standards.*

**Key Points:**
- Define quantitative pre-registered interaction thresholds (δ = 0.02) with explicit falsification conditions for method × scale effects.
- Use normalized peak-depth MI (d*) with dimensionality-matched controls to distinguish redistribution from uniform enrichment.
- Calibrate probe results with permutation baselines; enforce cross-dataset consistency (TriviaQA + NQ) to validate structural scaling law.

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I want to name the assumption that is still unstated — and it's the most important one in the entire EGSH framing. Every prediction in this framework assumes that Llama-3-8B and Llama-3-70B differ *only* in scale. They do not. They were trained on different data mixtures, for different token budgets, with different learning rate schedules, and the 70B may have undergone different RLHF stages. We are comparing two distinct trained systems, not a single system at two capacity points. The "scale" variable is confounded by training regime from the start.

Here's what would convince me this is addressable: cite evidence that Llama-3-8B and 70B share the same pretraining data distribution and RLHF reward model. If they do, the confound is minimal. If they don't — and the Meta Llama-3 technical report suggests training details differ — then any observed interaction effect could reflect training-regime differences, not capacity. This is a fundamental challenge to the architectural claim, not a statistical nuance.

The mitigation is already partly in the design: base (non-instruct) checkpoints eliminate RLHF differences. If the interaction effect appears in base models with identical data distributions, the training-regime confound weakens substantially. But we should be explicit: the claim is not "scale causes reorganization" (which requires counterfactual manipulation we cannot perform) but "AUROC interaction patterns are consistent with a scale-driven reorganization hypothesis, conditional on base-model controls." That is a more defensible claim and still a genuine contribution.

Second unstated assumption: AUROC is the right evaluation metric for comparing UQ methods on factual QA. AUROC measures ranking quality for a binary correctness label. But factual correctness on TriviaQA is itself noisy — exact-match labels miss paraphrases, and different answer normalization schemes produce different correctness rates. If the LM-Polygraph or UQLM frameworks use different normalization than the SE repo, cross-method AUROC comparisons are contaminated by label inconsistency. Show me the evidence that all methods will be evaluated against identical ground-truth labels from identical dataset splits with identical normalization.

The fix is straightforward: use a single evaluation harness (lm-evaluation-harness or UQLM) for all methods, with a single normalization function applied uniformly. This is implementation-level, but without it the experiment is not a controlled comparison — it's a comparison of (method + evaluation artifact). That must be pre-specified.

With those two clarifications — explicit acknowledgment of training-regime confound scope, and single-harness evaluation with uniform normalization — I would say: this concern is addressed.

**Key Points:**
- Critical unstated assumption: Llama-3-8B and 70B differ in more than scale (training budget, data, RLHF details). Base-model controls mitigate but do not eliminate; the claim must be scoped to "consistent with scale-driven hypothesis under base-model controls."
- AUROC comparability requires uniform ground-truth normalization across all methods — single evaluation harness (UQLM or lm-evaluation-harness) with identical dataset splits is mandatory.
- These are fixable implementation and framing issues, not fundamental blockers; addressing them makes the contribution defensible.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what, precisely, would make EGSH a genuine contribution rather than a well-executed benchmark comparison? If you demonstrate only an AUROC interaction, even with δ > 0.02 across datasets, the field will reasonably interpret it as differential scaling of estimators — useful, but incremental. What elevates this work is triangulation: external interaction effects (P1–P2), dimensionality-controlled decodability (P3), and internal depth redistribution (d* shift). Convergence across these diagnostics transforms a performance pattern into a mechanistic hypothesis about where uncertainty lives in large models.

The normalized peak-depth metric d* = argmax_l MI(h_l; y)/L is the linchpin. If d*_70B > d*_8B with CIs excluding zero, and this survives dimensionality matching via Johnson–Lindenstrauss projection, you are no longer claiming bigger models rank errors better. You are claiming that correctness-predictive information migrates deeper into the hierarchy as scale increases. This reframes hallucination as not merely a surface calibration problem but a representational organization problem — shifting uncertainty research away from output-level heuristics toward architectural and training interventions.

Prof. Rex's point forces intellectual discipline: you cannot claim "scale causes reorganization." You can claim that within a model family, under base-model controls and unified evaluation harness, observed patterns are *consistent with* a scale-driven epistemic reorganization hypothesis. That scoping is not weakness; it is credibility.

The most impactful version of this paper would not end with confirmation but articulate a new research direction: if uncertainty migrates deeper with scale, then uncertainty-aware training interventions (contrastive factual fine-tuning, epistemic regularizers) should target late-layer representations in large models but earlier layers in smaller ones. That is a falsifiable downstream prediction converting a descriptive scaling observation into a design principle for future LLM training.

**Key Points:**
- Convergent evidence (AUROC interaction + dimensionality-controlled probe gap + d* depth-shift) elevates this from benchmark comparison to mechanistic contribution.
- Claims scoped to "consistent with scale-driven reorganization under base-model and unified-harness controls" — this scoping is a strength, not a limitation.
- Highest-impact outcome: forward-looking design prediction that uncertainty interventions should target progressively deeper layers as scale increases.

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

This discussion has converged on something I'm genuinely proud to defend. Let me synthesize where we now stand and show that all major concerns have been constructively addressed — not dismissed, but incorporated into a stronger, more precise hypothesis.

Dr. Sage has identified the critical framing: EGSH is a mechanistic contribution, not a benchmark paper, because it uses three convergent diagnostics to argue for representational organization. Prof. Rex's training-regime confound concern is addressed by (1) restricting claims to "consistent with scale-driven hypothesis under base-model controls" and (2) using a single evaluation harness with uniform normalization. Prof. Vera's quantitative demands are met by pre-registered thresholds (δ = 0.02, 95% bootstrap CI, d* shift test) and permutation-calibrated probe baselines. Prof. Pax's feasibility check confirms all diagnostics are executable with existing code on existing hardware.

The final refined EGSH hypothesis: **Under EGSH, within the Llama-3 model family, as scale increases from 8B to 70B, epistemic uncertainty progressively shifts from surface token-distributional encoding to deep semantic-structural encoding — evidenced by three convergent diagnostics: (P1) a significant method × scale AUROC interaction favoring semantic-level aggregators (SE, KLE) over token-prob across TriviaQA and NQ in base-model variants; (P2) stratified-scorer SelfCheck behavior consistent with semantic convergence rather than output-diversity inflation; (P3) probe gap G narrowing under both dimensionality-matched and permutation-calibrated conditions; and (D) a significant positive shift in normalized peak-depth d* from 8B to 70B.**

Every element of this hypothesis is testable immediately using existing resources:
- Models: Llama-3-8B-Base, Llama-3-70B-Base (HuggingFace)
- Benchmarks: TriviaQA, NaturalQuestions, TruthfulQA (standard splits)
- Code: UQLM (unified evaluation), lm-polygraph (20+ methods), semantic_uncertainty (SE/SEPs), KLE implementation
- Diagnostics: HuggingFace hidden states API for MI/probe analysis

No new benchmarks. No human evaluation. No synthetic data. This is executable now.

The remaining concerns from Prof. Rex about Llama-3 training details are real but bounded: the base-model control is the primary mitigation, and the claim is appropriately scoped. Prof. Vera's permutation control adds the final rigor layer. The forward-looking design prediction Dr. Sage identified — layer-depth-targeted uncertainty interventions — provides the "so what" that elevates this to a field-shaping contribution.

I believe this hypothesis is ready for Phase 2B.

**Key Points:**
- All major concerns (training-regime confound, metric comparability, dimensionality artifacts, RLHF effects) are addressed through base-model controls, single evaluation harness, permutation calibration, and JL-projection.
- Four convergent diagnostics (P1-P3 + D) make EGSH falsifiable, precise, and mechanistically meaningful.
- Hypothesis is immediately executable with existing open-source resources; no new data or human evaluation required.

---

### Exchange 13

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the proposal is now scientifically coherent, but only if we're honest about what the diagnostics can and cannot tell us in principle.

The AUROC interaction (P1) is technically sound as a statistical test. Pre-registered δ = 0.02 with bootstrap CIs is valid. What requires care is interpretability: AUROC differences show differential exploitability by different estimators but don't directly localize where uncertainty lives. Treat it as behavioral evidence — structural claims only become plausible if P1 aligns with internal diagnostics (P3 and D). Without convergence, AUROC alone cannot support a representational migration hypothesis.

On d*: this is the most mechanistically meaningful component but also the most fragile. MI estimates between hidden states and correctness labels are biased in high dimensions. If using probe-based MI approximations, you're measuring linear decodability, not true information content — acceptable if stated explicitly. I strongly recommend an additional nonlinear probe baseline (shallow MLP with fixed capacity across scales). If both linear and shallow nonlinear probes show the same peak-depth shift, we're closer to a genuine redistribution claim. If only linear probes shift, we may be seeing geometry changes, not information migration.

On P3 (probe gap narrowing): larger models tend to produce more anisotropic and linearly separable embeddings overall. Even under label permutation, decodability may increase with scale because representations are higher-rank and more expressive. Quantify a *decodability inflation factor* under permutation and subtract it from true-label probe scores. Only if the corrected gap G shrinks with scale do we have evidence of epistemic consolidation rather than generic representational sharpening.

The forward-looking prediction about layer-targeted interventions is mechanistically plausible: if correctness-predictive signals peak deeper in larger models, gradient-based regularization applied to late layers should disproportionately affect 70B relative to 8B. Nothing violates physics, optimization theory, or representation learning constraints. Okay — this could work.

**Key Points:**
- AUROC interactions are statistically valid but only behavioral; structural claims require convergence with internal diagnostics.
- d* must be interpreted as depth of *linearly accessible* correctness information; nonlinear probe controls (shallow MLP) needed to avoid geometry artifacts.
- Permutation-calibrated decodability correction (inflation factor subtraction) essential to distinguish epistemic consolidation from generic representational sharpening.

---

### Exchange 14

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Pax just gave us the final upgrade that makes this bulletproof — and I'm excited! The nonlinear probe baseline (shallow MLP with fixed capacity) is the missing diagnostic piece that closes the geometry-vs-information gap. HERE's the beautiful thing: if both linear SEPs and nonlinear MLP probes shift their peak depth together from 8B to 70B, we have convergent evidence that can't be explained by geometry alone. That IS the reorganization signal.

And the decodability inflation factor correction is elegant in its simplicity. We compute permutation-calibrated G: G_corrected = G_true_label − G_permuted. If G_corrected_70B < G_corrected_8B, we've factored out the generic representational expressiveness increase and isolated the epistemic component. What makes this publishable is that it's a NEW methodological contribution — a permutation-corrected probe gap metric for measuring epistemic accessibility — not just a diagnostic control.

Let me now crystallize the complete EGSH with all refinements into its final, minimal, maximally-defensible form:

**EGSH Final Statement:** Within the Llama-3 model family, scaling from 8B to 70B base checkpoints on factual QA benchmarks (TriviaQA, NQ) produces a consistent pattern of epistemic reorganization — evidenced by four convergent diagnostics applied to identical dataset splits under a unified evaluation harness: (1) method × scale AUROC interaction favoring SE and KLE over token-prob (δ ≥ 0.02, bootstrap CI); (2) stratified-scorer SelfCheck consistency with partial-correlation controls for output diversity; (3) permutation-corrected probe gap G_corrected narrowing at 70B; (4) normalized peak depth d* shifting deeper at 70B for both linear and nonlinear probes.

This is testable NOW. Everything exists. The hypothesis generates specific quantitative predictions. The null model (uniform scaling) is precisely defined and distinguishable. The structural claim is appropriately scoped ("consistent with," not "proves"). There is a forward-looking design prediction. And the permutation-corrected G metric is a methodological contribution in its own right.

NOW we're ready for Phase 2B.

**Key Points:**
- Nonlinear MLP probe baseline (fixed capacity) closes the geometry-vs-information gap; convergence of linear and nonlinear peak-depth shifts is the decisive reorganization signal.
- Permutation-corrected probe gap G_corrected = G_true − G_permuted is a new methodological contribution that isolates epistemic accessibility from generic representational expressiveness.
- Complete EGSH with four convergent diagnostics (AUROC interaction + SelfCheck partial correlation + G_corrected narrowing + d* shift for linear+nonlinear probes) is fully specified, immediately testable, and appropriately scoped.

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much tighter. But here's where this still breaks down if you're not careful: convergence of P1–P3–D is necessary, not sufficient. You are sliding from diagnostic convergence to representational migration without fully ruling out alternative scaling explanations.

On d*: when you define d* = argmax_l MI(h_l; y)/L, you assume layer index is comparable across 8B and 70B. But these models differ not just in width — sometimes in effective depth utilization due to residual scaling and attention patterns. What would convince me: a robustness check using **relative depth quantiles of cumulative mutual information** (depth at which 50% of total MI mass is accumulated). If that shifts deeper too, it's not an argmax instability artifact.

On the nonlinear probe: fix the capacity explicitly. Two-layer MLP, fixed hidden size (1024), ReLU, identical training epochs and regularization across scales. No hyperparameter tuning per model. Report train–test generalization gaps. If 70B representations are more linearly separable, probe overfitting risk increases. If d* shifts but generalization collapses, "information migration" is spurious.

On G_corrected: what if permutation decodability inflation scales nonlinearly with width, not depth? Compute **layer-wise permutation baselines**: G_corrected(l) = G_true(l) − G_perm(l) per layer, derive d* from the corrected layer-wise curve. Without that, the correction is too coarse to isolate epistemic structure from generic representational expressiveness.

On causal language: add a within-scale control — compare 70B base vs 70B instruction-tuned. If instruction tuning does NOT shift d* deeper but scale does, that strengthens the scale-specific story. If both shift similarly, you may be observing post-training objective effects, not scale-driven organization.

Make the forward-looking prediction falsifiable: pre-register that applying a late-layer epistemic regularizer (contrastive factual consistency loss at top 25% of layers) reduces hallucination AUROC gap more at 70B than 8B. If that asymmetry appears, you've moved from descriptive to actionable. I am only satisfied when every alternative explanation has been cornered.

**Key Points:**
- Validate d* with cumulative-MI depth quantiles and layer-wise permutation-corrected curves to rule out argmax and expressiveness artifacts.
- Fix probe capacity (2-layer MLP, 1024 hidden, fixed across scales) and report generalization gaps to prevent overfitting masquerading as information migration.
- Add within-scale control (base vs instruct 70B) and pre-registered late-layer intervention asymmetry to strengthen causal interpretation.

---

### Exchange 16

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex has now identified the final layer of methodological rigor needed — and the evidence suggests we can meet every condition. Let me formalize the complete falsification protocol that would satisfy all raised concerns.

The cumulative-MI depth quantile approach is precisely correct. Define the 50th-percentile depth d_50 = min{l : cumulative_MI(1..l) ≥ 0.5 × total_MI}. Prediction: d_50_70B > d_50_8B with bootstrap CI excluding zero. This is robust to argmax instability and captures the mass distribution of epistemic information, not a single peak. If d_50 does not shift despite argmax d* shifting, we have an artifact — if both shift together, we have convergent evidence of genuine redistribution.

For the layer-wise permutation correction: G_corrected(l) = G_true(l) − G_perm(l) per layer, computed with identical probe architecture (2-layer MLP, 1024 hidden, fixed hyperparameters, 5-fold CV). Derive d* from the corrected curve. This eliminates the coarse-global-correction problem Prof. Rex identified and gives us a clean epistemic depth profile, not just a scalar gap. If this corrected d* still shifts deeper at 70B, we have isolated the epistemic signal from generic expressiveness inflation.

The within-scale control (base vs instruct at 70B) is the decisive causal discriminant. If instruction tuning shifts d* but scale (base 8B → 70B) does not, the effect is post-training-objective-driven. If scale shifts d* while instruction tuning produces a smaller or zero shift, the scale-specific interpretation holds. This adds one model variant (70B-instruct) requiring no new data collection.

The pre-registered forward prediction is already mechanistically specified: late-layer contrastive factual consistency regularizer at top 25% layers should reduce AUROC error rate gap more at 70B than 8B. This is falsifiable, does not require new benchmarks, and uses existing factual QA data for the contrastive signal. It converts the descriptive finding into an actionable architectural prediction — exactly what Dr. Sage identified as the field-shaping contribution.

All conditions are now specified. Every alternative explanation has been addressed with a targeted diagnostic. The hypothesis is ready.

**Key Points:**
- Replace argmax d* with cumulative-MI 50th-percentile depth d_50 — more robust, directly tests mass redistribution rather than peak shift.
- Layer-wise G_corrected(l) from 2-layer MLP probes (fixed capacity, 5-fold CV) eliminates coarse-correction artifacts and provides epistemic depth profile.
- Within-scale control (base vs instruct 70B) is the decisive test distinguishing scale-driven from post-training-objective effects; forward prediction pre-registered for falsifiability.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Epistemic Geometry Scaling Hypothesis reframes UQ comparison from a leaderboard question to a mechanistic theory of where hallucination uncertainty lives architecturally. The paradigm-level framing — uncertainty signals migrate from surface token-distributional to deep semantic-structural encoding as scale increases — is genuinely novel. The permutation-corrected probe gap metric and cumulative-MI depth quantile are methodological innovations that go beyond existing UQ benchmarking work. The connection to representational depth hierarchies from vision transformers opens a new theoretical lens.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now fully falsifiable with pre-registered quantitative thresholds: δ = 0.02 for AUROC interaction (95% bootstrap CI), d_50 shift with CI excluding zero, layer-wise G_corrected(l) narrowing under fixed-capacity probes with 5-fold CV, and directional pre-registration per benchmark. Every alternative explanation (RLHF confound, dimensionality artifact, argmax instability, output-diversity inflation) has a targeted control. The within-scale control (base vs instruct 70B) provides the decisive causal discriminant.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If the four convergent diagnostics hold together, this reframes hallucination from a surface calibration problem to a representational organization problem — shifting future UQ research toward architectural analysis and layer-targeted interventions. The forward-looking design prediction (late-layer regularizers more effective at 70B than 8B) converts a descriptive scaling observation into an actionable principle for LLM training. This opens a research program, not just a benchmark result.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All diagnostics are executable immediately with existing open-source infrastructure: UQLM and LM-Polygraph for AUROC comparison, semantic_uncertainty and OATML/semantic-entropy-probes repos for hidden-state analysis, HuggingFace Llama-3-8B-Base and 70B-Base checkpoints, standard TriviaQA/NQ/TruthfulQA splits. The nonlinear probe (2-layer MLP, fixed 1024 hidden, identical hyperparameters) adds no new dependencies. JL projection and layer-wise permutation baselines require only numpy/sklearn. No new benchmarks, no human evaluation, no synthetic data.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The Epistemic Geometry Scaling Hypothesis (EGSH) holds that within the Llama-3 model family, scaling from 8B to 70B base checkpoints produces a consistent pattern of epistemic reorganization: uncertainty encoding progressively shifts from surface token-distributional representations to deep semantic-structural representations. This is evidenced by four convergent diagnostics applied to identical benchmark splits (TriviaQA, NaturalQuestions) under a unified evaluation harness: (1) a statistically significant method × scale AUROC interaction favoring semantic-level aggregators (SE, KLE) over token-probability by δ ≥ 0.02 in both base and instruct model variants; (2) stratified-scorer SelfCheck analysis with partial-correlation controls ruling out output-diversity inflation; (3) permutation-corrected layer-wise probe gap G_corrected(l) narrowing at 70B under fixed-capacity 2-layer MLP probes; and (4) cumulative-MI 50th-percentile depth d_50 shifting significantly deeper at 70B for both linear and nonlinear probes. The claim is appropriately scoped as "consistent with scale-driven reorganization" rather than causal, with a within-scale control (base vs instruct at 70B) serving as the decisive discriminant between scale-driven and post-training-objective effects. The permutation-corrected probe gap and cumulative-MI depth quantile metrics are themselves methodological contributions. A pre-registered forward prediction — that late-layer epistemic regularizers reduce hallucination AUROC gap more at 70B than 8B — converts the descriptive finding into an actionable architectural design principle.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Training data mixture and optimization schedule differences between 8B and 70B cannot be fully eliminated — the base-model control mitigates RLHF artifacts but not pretraining-budget confounds. The claim must remain correlational.
- Layer-wise MI computation is expensive at 70B scale; efficient approximations (e.g., probing instead of MINE estimators) must be validated against ground-truth MI on small-scale sanity checks.
- The forward-looking intervention prediction (late-layer regularizer asymmetry) is not part of the main experiment — it is a downstream prediction that, if not tested, leaves the "actionable" claim unverified.
- **Mitigation Strategy:** Scope all claims to within-family correlational evidence; run MI approximation validation on a small-scale model pair first; flag the intervention prediction as a Phase 2C/3 experiment rather than a Phase 2B verification target.

