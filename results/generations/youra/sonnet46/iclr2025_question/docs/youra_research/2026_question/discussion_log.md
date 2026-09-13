# Phase 2A: Research Discussion Log
# Gap: No AUROC Baseline for Generation-Free Post-Hoc NLI on Multi-Task HaluEval
# Architecture: Self-Contained Tikitaka Loop v9.0.0
# Generated: 2026-03-16

---

## Research Briefing

**Research Question:** Can generation-free post-hoc NLI factual consistency scoring — applying contradiction/entailment scores from DeBERTa-v3-large-mnli to existing (context, response) pairs in HaluEval — achieve AUROC ≥ 0.65 for hallucination detection on HaluEval-Dialogue, HaluEval-Summarization, and HaluEval-QA, operating purely on already-generated text without any LLM inference at experiment time?

**Gap:** No published AUROC baseline exists for applying `cross-encoder/nli-deberta-v3-large` directly to HaluEval's three tasks as a zero-shot hallucination detector without any LLM generation or retrieval augmentation at inference time.

**Sub-Gaps Integrated:**
- Gap 2: Which NLI framing achieves highest AUROC: contradiction alone vs 1−entailment vs contradiction−entailment?
- Gap 3: Does sentence-level NLI (max contradiction) outperform response-level NLI on HaluEval-Dialogue and QA?

**ROUTE_TO_0 Context (Attempt 5 — 4 prior failures):**
- H_token: AUROC 0.54/0.42 (fluent hallucinations ≠ high entropy)
- LLAE: AUROC 0.42–0.57 (no explicit context in non-RAG settings)
- P(True) PARTIAL/FAIL: Requires instruction-tuned model (gated, inaccessible)
- SelfCheckGPT-NLI: AUROC 0.48 (base model → uniform stochastic outputs)

**Hard Constraint:** Only `meta-llama/Llama-3.1-8B` (BASE, non-instruct) is locally cached. Zero LLM generation at experiment time.

**Reference Papers:**
- P1: SummaC (Laban et al., 2022) — arxiv_2111_09525 — sentence-level NLI achieves 74.4% balanced acc
- P2: TRUE (Honovich et al., 2022) — arxiv_2204_04991 — cross-task NLI evaluation framework
- P3: HaluEval (Li et al., 2023) — arxiv_2305_11747 — benchmark definition
- P4: FActScore (Min et al., 2023) — arxiv_2305_14251 — atomic fact-level NLI
- P5: SelfCheckGPT (Manakul et al., 2023) — arxiv_2303_08896 — NLI component (sampling-free reuse)

**Available Infrastructure:** DeBERTa-v3-large-mnli cached; HaluEval cached; no LLM generation required.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we completely flip the hallucination detection paradigm? Every previous attempt in this pipeline — H_token, LLAE, P(True), SelfCheckGPT — made the same fundamental assumption: we need to QUERY the language model at detection time. What if that assumption is simply wrong?

Consider what HaluEval gives us for free: *labeled (context, response) pairs that already exist*. The hallucination has already happened. The context is right there. What we need is a model that can ask: "Does this response logically follow from this context?" That is *literally* the NLI task. Not a proxy for it. The EXACT task. We've been overlooking a beautiful alignment between our detection problem and a 60-year-old logical inference framework.

The truly novel angle here isn't just "use NLI instead of generation" — it's the *decoupling* of the detector from the generator. Think about what that means for deployment: a hallucination detector that requires ZERO access to the generating model. No API, no logits, no instruct-tuning. You could apply it retroactively to any text corpus. That's a paradigm shift from introspective UQ (the model examines itself) to *extrospective NLI UQ* (an independent classifier examines the output). NOW we're onto something!

And here's what makes this publishable: SummaC [Laban et al., 2022] showed NLI works for summarization consistency at 74.4% balanced accuracy — but they never measured AUROC on HaluEval, never tested dialogue or QA formats, and never compared scoring framings (contradiction vs. 1−entailment vs. net contradiction). We're filling three simultaneous gaps with a single elegant experiment.

The creative angle I want to explore: what if different NLI framings work better for different task types? Dialogue (conversational contradiction) might favor net-contradiction scores because neutral utterances are pervasive. Summarization might favor entailment deficit. QA might be cleanest with raw contradiction. If we find task-specific optimal framings, that's a genuinely novel finding — not just "NLI works" but "NLI framing matters and here's why."

**Key Points:**
- Paradigm shift: extrospective NLI UQ decouples detector from generator — deployable with zero model access
- Three simultaneous gaps filled: AUROC baseline on HaluEval, framing ablation, aggregation strategy comparison
- Task-specific optimal framing hypothesis: dialogue favors net-contradiction, summarization favors entailment deficit, QA favors raw contradiction

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The core claim here is that hallucination detection can be reframed as extrospective NLI, fully decoupled from the generating model. The evidence from SUMMAC suggests this is plausible in summarization: a simple zero-shot aggregation (SUMMACZS) achieves 70.4 balanced accuracy, and a learned convolutional aggregation (SUMMACConv) reaches 74.4 with strong ROC-AUC across heterogeneous datasets [Laban et al., 2022]. However, plausibility is not proof. What would disprove your paradigm shift? If an NLI-based detector fails to generalize across task formats (QA, dialogue, summarization) or collapses under distribution shift, then the "universal extrospective UQ" claim is too strong.

Let us define precise, falsifiable predictions. **Prediction 1:** On HaluEval, an NLI-based detector using a pair-matrix approach and column-wise max aggregation (SUMMACZS-style) will achieve AUROC ≥ 0.75 overall, and ≥ 0.70 within each task type (QA, dialogue, summarization). **Failure criterion:** AUROC < 0.65 in any task slice. **Prediction 2:** Framing matters. Specifically, dialogue will show statistically significant AUROC improvement (Δ ≥ 0.03, p < 0.05 via DeLong test) when using net-contradiction (P(contradiction) − P(entailment)) versus raw contradiction alone. If no framing yields ≥ 0.02 improvement over the others across tasks, the "task-specific framing" hypothesis is unsupported.

Now, the Achilles' heel: dataset artifacts and leakage. HaluEval may encode lexical shortcuts—hallucinated responses could contain named entities absent from context, making NLI detection trivial via token mismatch rather than logical inconsistency. We must control for this. I propose a *lexical overlap–matched evaluation*: stratify examples by context-response token overlap and compute AUROC within overlap bins. If performance drops sharply in high-overlap bins, the detector is exploiting surface cues. Additionally, include a strong lexical baseline (e.g., NER overlap as in [Laban et al., 2022], which achieved only 53.0 balanced accuracy) to quantify incremental value beyond shallow heuristics.

On aggregation: SUMMACZS is sensitive to outliers because it uses column-wise maxima. SUMMACConv mitigates this via histogram binning and learned 1-D convolution [Laban et al., 2022]. Your proposal must test both fixed and learned aggregators. If a learned aggregator trained on HaluEval dramatically outperforms zero-shot NLI, then we are no longer evaluating "decoupled" detection but a task-specific classifier trained on hallucination artifacts. To preserve the paradigm shift claim, I recommend a strict zero-shot setting first, followed by a limited fine-tuning regime with held-out task types to test cross-task generalization. If training on summarization improves QA performance, that supports a task-agnostic inference signal; if not, the method may be format-bound.

Finally, we must compare against introspective baselines under identical evaluation conditions. If extrospective NLI matches or exceeds SelfCheckGPT or P(True) in AUROC without model access, the deployment advantage is real. If it underperforms by >0.05 AUROC, the cost of decoupling may outweigh its elegance. The evidence suggests NLI is robust across domains in SUMMAC's benchmark; what remains is to stress-test its limits under task heterogeneity and artifact control. Only then can we justify calling this a paradigm shift rather than a reframing.

**Key Points:**
- Define falsifiable AUROC thresholds and statistical tests to validate task-specific framing claims.
- Control for lexical and annotation artifacts via overlap-stratified evaluation and strong shallow baselines.
- Separate zero-shot NLI aggregation from learned task-specific models to preserve the "decoupled detector" claim.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I want to be precise about it because the mechanism Prof. Vera described is necessary but not sufficient. Let me stress-test three specific aspects.

**First: The NLI granularity problem is more severe in dialogue than SummaC suggests.** FActScore [Min et al., 2023] decomposed long-form text into *atomic facts* averaging 4.4 per sentence — and found that 40% were unsupported. The key finding is that factual errors are *localized*: a single false atomic claim appears within an otherwise accurate sentence. For dialogue in HaluEval, the "response" is often a full conversational turn of 2–4 sentences. If one sentence contradicts the context while three do not, a response-level NLI score will average down the contradiction signal. FActScore's methodology section explicitly demonstrates that sentence-level evaluation catching ~40% unsupported facts would be *missed* by document-level scoring [Min et al., 2023, Methodology]. This is the strongest argument for sentence-level max aggregation, but also reveals an assumption: that HaluEval's hallucinated responses contain *localized* rather than *pervasive* contradictions. What's the evidence for this? If hallucinations in HaluEval-Dialogue are pervasive (whole turns are fabricated), response-level NLI may be sufficient. If they're localized, sentence-level is essential. Show me the annotation distribution in HaluEval before claiming which aggregation strategy to prioritize.

**Second: The NLI premise construction for dialogue is underspecified.** Prof. Vera correctly flagged artifact risk. Here's a more fundamental issue: in HaluEval-Dialogue, the "context" is a *conversation history* — multi-turn dialogue. What gets fed to the NLI model as the premise? The full conversation history as a single string? The last assistant turn only? The last user query + last assistant response? The optimal premise window for dialogue NLI is completely unspecified in the proposal. SummaC worked on (document, summary) pairs — clean, structured, single-document. Dialogue has turn boundaries, speaker labels, and pragmatic implications that a single entailment score cannot handle. This isn't a minor detail — premise specification *is* the experimental design decision, and the hypothesis as stated hasn't made it.

**Third: AUROC ≥ 0.65 is too low a bar given SummaC's established 74.4% balanced accuracy on summarization.** If the approach only barely clears 0.65 on summarization (the easiest task for NLI), while SummaC already shows 74.4% balanced accuracy (roughly equivalent to ~0.74 AUROC under balanced conditions), then the contribution is that the approach *fails to reach the established state of the art*. The gate should be: "Does generation-free DeBERTa NLI on HaluEval approach SummaC's summarization performance (≥0.72 AUROC) while also achieving ≥0.65 on dialogue and QA?" That's a more defensible framing. What would convince me is a success criterion that differentiates success from "just good enough."

I'll grant what's strong: the feasibility is real, the infrastructure is available, and the decoupling claim has genuine deployment value. But the mechanism is underdetermined — until the dialogue premise construction and aggregation rationale are explicit and motivated by evidence, this is an experiment design sketch, not a hypothesis. Tighten the premise construction specification and I'll retract concern #2.

**Key Points:**
- FActScore's localized-error finding [Min et al., 2023] is the strongest evidence for sentence-level aggregation, but requires HaluEval annotation distribution evidence to justify design choice
- Dialogue premise construction (full history vs. last turn vs. last QA pair) is underspecified and is the critical design decision
- Success criterion (AUROC ≥ 0.65) may be too weak — calibrate against SummaC's established ≥0.74 balanced accuracy on summarization as the reference bar

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether NLI *can* detect hallucinations—we already know it can. SelfCheckGPT's NLI variant achieves a striking 93.42 AUC-PR at the sentence level and 0.78 passage-level Spearman on WikiBio [Manakul et al., 2023]. This matters because it establishes that contradiction-based signals are among the strongest extrospective indicators we currently have. So the bar for contribution is high. If your proposal merely shows that "NLI works on HaluEval," that is incremental. The genuine contribution would be to demonstrate that a **generation-free, zero-query, decoupled NLI detector** can *match or approach* generation-based methods like SelfCheckGPT-NLI—without access to the model or stochastic resampling. That is the paradigm shift.

What would make this advance the field? A clear empirical separation between *introspective stochastic consistency* (SelfCheckGPT) and *extrospective logical consistency* (your method). SelfCheckGPT relies on multiple sampled generations and cross-comparisons—computationally expensive and tied to the generator. If you can show that a frozen DeBERTa-NLI with well-specified aggregation achieves ≥0.72 AUROC on summarization (approaching SummaC-level performance) and remains ≥0.70 on dialogue and QA—*without sampling or logits*—then the community should care. This matters because it reframes hallucination detection as a modular verification layer that can be applied retroactively to any model output, including proprietary APIs and archived corpora.

However, Prof. Rex is correct: the contribution hinges on mechanism specification. Dialogue premise construction cannot be an afterthought. I would formalize three explicit designs: (1) **Full-history premise**: concatenate all prior turns as premise, response as hypothesis. (2) **Last-user-window premise**: only the most recent user query (plus optionally last assistant turn). (3) **Turn-wise sliding premise**: compute NLI between each prior utterance and each response sentence, then aggregate via max-contradiction. You then pre-register a prediction: dialogue will favor design (3) with sentence-level max aggregation if hallucinations are localized, but full-history may suffice if errors are pervasive. The point is not which wins—it is that you transform an underspecified design choice into a falsifiable research question.

What does this mean for the field long-term? If framing and aggregation prove task-sensitive, then hallucination detection ceases to be a monolithic metric and becomes a structured inference problem. Dialogue may reward net-contradiction; summarization may reward entailment deficit; QA may be binary contradiction-dominant. This suggests we need **task-aware verification heads**, even within a unified NLI backbone. This would shift future research from "find a better scalar score" to "learn the right logical projection for each generation format."

Impact must be earned through comparison. Include SelfCheckGPT (NLI variant) as a reference ceiling. If your zero-shot NLI matches within 0.05 AUROC while eliminating sampling cost, that is a real systems-level advance. Answer convincingly whether decoupling costs us signal or whether logical consistency alone carries most of the weight, and this work shapes how we architect verification for the next generation of LLM systems.

**Key Points:**
- Contribution must exceed "NLI works" by showing generation-free NLI approaches SelfCheckGPT-level performance without model access.
- Dialogue premise construction and aggregation must be formalized as falsifiable design choices, not implementation details.
- Task-specific framing results could redefine hallucination detection as structured logical inference rather than a single scalar uncertainty metric.

---

### Exchange 5

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be realistic here about the technical soundness, because there are some genuine mechanism questions that need answering before we've earned the right to claim a paradigm shift.

First, let's address whether the mechanism is physically/mathematically possible: YES, unambiguously. DeBERTa-v3-large-mnli is a cross-encoder that takes (premise, hypothesis) pairs and outputs a 3-class softmax. The HaluEval (context, response, label) triples map directly to (premise=context, hypothesis=response). This is a valid inference problem — the mathematical operation is well-defined. What FActScore [Min et al., 2023] shows us in the Methodology section is that decomposing text into atomic units and verifying each independently catches 40% unsupported claims at 4.4 atomic facts per sentence. This tells us something fundamental: the NLI signal at sentence granularity is strong enough to detect individual atomic falsehoods, but only when properly aligned with the right granularity. The mechanism is sound; the question is operationalization.

Now, here's what *actually* worries me about the mechanism: the DeBERTa cross-encoder was trained on MNLI, SNLI, and similar datasets where premises and hypotheses are short, declarative sentences — typically 1–2 sentences each. HaluEval dialogue contexts can be 500–1500 tokens of conversational history. The model will truncate at max_length=512 tokens. What gets truncated? The *beginning* of the conversation — often the factual context that the hallucination violates. This isn't a resource concern — it's a fundamental measurement validity question: are we computing NLI over the right (premise, hypothesis) pair when we truncate the premise?

The fix is technically straightforward and preserves the generation-free claim: for long contexts, use the *last N sentences* of the context as premise (sliding window), rather than the full history. For HaluEval-Dialogue, the most recent 3–5 turns likely contain the factually relevant context. This is the "Last-user-window premise" that 🎯 Dr. Sage described. I'd go further: the most scientifically valid approach is to compare (a) full-context truncated, (b) last-3-turns window, (c) last-user-query only — and report AUROC for each. If (b) outperforms (a) on dialogue, that's evidence the truncation artifact suppresses signal. If (a) ≈ (b), truncation is benign. That comparison is the mechanism check, not a nice-to-have.

Second mechanism concern: the NLI framing question (contradiction vs. 1−entailment vs. net-contradiction). Prof. Rex called this underspecified; I want to clarify why it's theoretically motivated. In NLI, `neutral` is the catch-all class — non-entailed statements that also aren't contradicted. Hallucinations often produce neutral scores (the model fabricates details not present in context, which aren't strictly *contradicted* either). Raw `contradiction` score may underweight these. `1 − entailment` captures any departure from entailment, including neutral. Net-contradiction (contradiction − entailment) amplifies the contrast. Each framing has a different theoretical relationship to the hallucination distribution. The framing experiment is mechanistically motivated, not arbitrary — and it's the key contribution beyond "DeBERTa NLI works."

Okay, this could work. If we nail the premise construction decision, specify the framing ablation clearly, and include truncation analysis, the mechanism is theoretically sound and empirically falsifiable. The core prediction: response-level DeBERTa NLI with the net-contradiction framing and appropriate premise window will achieve AUROC ≥ 0.70 on summarization and ≥ 0.65 on dialogue and QA — without any LLM generation.

**Key Points:**
- Max_length=512 truncation is a measurement validity concern, not a resource concern — must compare full-context vs. sliding-window premises
- Three NLI framings are theoretically motivated: each treats the `neutral` class differently, which matters because hallucinations often produce neutral rather than contradiction scores
- Core mechanism is sound and feasible; the critical experimental design decision is premise window specification for long dialogue contexts

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let us tighten this to the level where failure is informative. The TRUE benchmark demonstrates that NLI-style metrics, when standardized across 11 datasets, achieve ROC AUCs in the 80–81 range (ANLI: 81.5; Q2: 80.7), significantly outperforming n-gram baselines [Honovich et al., 2022]. The evidence suggests that cross-task factual consistency detection via NLI is viable. However, those models were fine-tuned (T5-11B, 3 epochs, lr=5e-5) and evaluated under controlled dataset harmonization. Your claim is stronger: a *generation-free, zero-shot* cross-encoder can generalize across heterogeneous generation formats. Therefore, we must separate two hypotheses:

- **H1 (Weak):** Fine-tuned NLI metrics can detect factual inconsistency across tasks. (Already supported by TRUE.)
- **H2 (Strong):** Zero-shot, frozen NLI models achieve ≥0.70 AUROC across QA, dialogue, and summarization without task-specific training.

What would disprove H2? Any task slice with AUROC < 0.65 under pre-registered framing and premise design. Not after tuning — under pre-registration.

Now to dialogue premise construction. Prof. Rex is correct: this is not an implementation detail but the independent variable. I propose a 3×3 factorial design:
- **Premise Window:** (A) full truncated context, (B) last-3-turn window, (C) last-user-only
- **Granularity:** (1) response-level, (2) sentence-level max, (3) sentence-level mean
- **Framing:** (i) contradiction, (ii) 1−entailment, (iii) contradiction−entailment

Primary outcome: ROC AUC with bootstrap 95% CI. Pre-register: dialogue AUROC maximized under (B,2,iii) — last-3-turn window, sentence-level max, net-contradiction — with ΔAUC ≥ 0.03 over full truncated context. Failure to observe any window effect (Δ < 0.01) would falsify the truncation-sensitivity concern raised by Prof. Pax.

Artifact control: Stratify by lexical overlap and named-entity introduction rate. If AUROC drops by >0.08 in high-overlap or low-new-entity bins, the detector likely exploits superficial cues. The incremental AUROC gain over a lexical baseline (entity overlap F1) must be ≥0.05 to claim genuine inferential reasoning.

Finally, comparison to introspective baselines. Define a non-inferiority margin: zero-shot NLI is competitive if its AUROC is within 0.05 of SelfCheckGPT-NLI under identical splits. If the gap exceeds 0.05 consistently, decoupling imposes measurable signal loss. The best experiments are designed to fail; failure here would mean NLI requires either fine-tuning or generation-based signals to compete.

**Key Points:**
- Pre-register strong zero-shot H2 (≥0.70 AUROC per task; failure <0.65) separate from fine-tuned TRUE-style results.
- Formalize dialogue design as factorial (premise window × granularity × framing) with explicit ΔAUC success criteria.
- Enforce non-inferiority (≤0.05 AUROC gap) relative to SelfCheckGPT to justify decoupled paradigm claim.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly by reframing the concern about the 0.65 threshold. Let me defend what's working here and propose refinements that address every criticism raised so far.

**On the 3×3 factorial design:** Prof. Vera's framework is exactly right, and I want to embrace it as an asset, not a constraint. FActScore's methodology [Min et al., 2023] established that atomic decomposition at sentence granularity catches ~40% unsupported facts — findings that remain robust across different LM architectures. The Discussion & Conclusion section of FActScore explicitly notes that performance is consistent "across model families" — the atomic fact evaluation generalizes. This supports our premise that NLI-based verification at sentence level will generalize across HaluEval's task types. The factorial design is our strength: if we find that (B,2,iii) consistently wins across tasks, that's a *principled finding* about the optimal verification architecture. If it doesn't — if full-context wins for some tasks and sentence-level wins for others — that's an even more interesting finding about task-specific verification requirements.

**Defending the AUROC threshold:** Prof. Rex raised that ≥0.65 may be "too low" given SummaC's 74.4%. But here's how we address this while preserving feasibility: we set a *primary threshold* (≥0.65 on all three tasks) for the existence proof that generation-free NLI is viable, AND a *secondary target* (≥0.70 on at least 2/3 tasks) for the stronger claim that approaches prior SOTA. Both are reportable. If we clear primary but miss secondary, the conclusion is "viable but suboptimal" — still publishable and informative. If we clear both, the paradigm shift claim stands fully. What if we address the concern by saying: the contribution is not "match SummaC" but "first systematic AUROC measurement across three HaluEval task types with framing ablation"?

**Resolving the dialogue premise construction:** Prof. Pax and Prof. Rex both flagged this, and I agree it's the central decision. Here's what I'd propose to strengthen the hypothesis: **make the premise window an explicit sub-hypothesis**. State: "Under the hypothesis that hallucinations in HaluEval-Dialogue are localized to the most recent conversational context, last-3-turn windowed premises will outperform full-context truncated premises by ΔAUC ≥ 0.03." If we find Δ < 0.01, we've falsified the localization assumption — which tells us something about HaluEval's annotation structure. Either result advances understanding.

**Consolidating the hypothesis:** The core claim is now clear:

*Under the setting of post-hoc, generation-free hallucination detection on HaluEval (Dialogue, Summarization, QA), if DeBERTa-v3-large-mnli is applied with optimal NLI framing (net-contradiction) and optimal premise window (last-3-turn for dialogue, full document for summarization/QA) with sentence-level max aggregation, then AUROC ≥ 0.65 will be achieved across all three task types, because the NLI contradiction signal captures factual inconsistency between context and response without requiring any LLM generation.*

The null: no NLI framing achieves AUROC ≥ 0.65 on all three tasks simultaneously. That's a clean, falsifiable, feasible hypothesis with existing infrastructure.

**Key Points:**
- Reframe the factorial design as an asset: either finding (optimal-window-wins OR full-context-sufficient) advances the field
- Two-tier threshold (primary ≥0.65/task; secondary ≥0.70 on 2/3 tasks) addresses the "bar too low" concern while preserving feasibility
- Core hypothesis now has Under-If-Then-Because structure with clean null hypothesis and clear AUROC gate

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally taking a shape I can stress-test properly. But here's where this still breaks down: you are treating "within 0.05 AUROC of SelfCheckGPT-NLI" as if that's a small concession. It isn't. Look at the numbers. SelfCheckGPT (NLI) hits **93.42 AUC-PR at sentence level and 0.78 passage-level Spearman** on WikiBio [Manakul et al., 2023]. And it achieves that by leveraging *stochastic self-contradiction across samples* — not just static context-response comparison. You are proposing to remove the very signal that drove their dominance. So show me the evidence that the *cross-sample variance signal* is redundant. If generation-based NLI is exploiting epistemic instability in the generator, and your method only sees logical mismatch with the prompt context, why should I believe the signal strength is comparable?

Here's the unstated assumption: that most hallucinations in HaluEval are *context-contradictory*, not merely *unsupported*. SelfCheckGPT's NLI variant doesn't compare response to prompt — it compares response sentences against other sampled generations. That captures internal inconsistency even when the prompt is underspecified. Your zero-shot cross-encoder cannot detect fabricated but non-contradictory additions unless the dataset annotates "unsupported" as hallucinated. So what would convince me? A label audit. Quantify the proportion of HaluEval positives that are (a) explicit contradictions of context vs. (b) unsupported but not contradicted. If >40% are unsupported-only, your reliance on contradiction-heavy framings may systematically cap performance.

Now, about the factorial design. Pre-register a *single* configuration per task as primary. Everything else is ablation. Define selection rules before seeing results. Otherwise reviewers will say you implicitly fine-tuned on the test set. Split HaluEval by source model (if available), tune framing on one subset, evaluate on another. If net-contradiction + sentence-max generalizes across model families, then we're talking about mechanism, not curve fitting.

The truncation issue is more serious than anyone is admitting. If dialogue contexts are 1k+ tokens and DeBERTa truncates to 512, then "full-context" is not full context — it's arbitrary prefix retention. Report mean retained-token percentage per task. Run a controlled experiment where you artificially truncate summarization documents to simulate dialogue-like loss. If AUROC drops by ≥0.05 under truncation, you've demonstrated sensitivity to premise loss.

Finally, your thresholds. ≥0.65 everywhere as existence proof? Fine. But the real architectural claim requires *stability across tasks*: variance across tasks ≤0.07 AUROC. If dialogue is 0.72 and QA is 0.58, you have a task-specific hack, not a paradigm.

**Key Points:**
- Zero-shot NLI must justify removal of stochastic self-consistency signal driving SelfCheckGPT's 93.42 AUC-PR [Manakul et al., 2023].
- Audit hallucination types (contradiction vs. unsupported) — core assumption underlying contradiction-based framing.
- Pre-register configuration selection and quantify truncation sensitivity to avoid post hoc tuning and measurement artifacts.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're having a real scientific conversation! Prof. Rex, you've hit exactly the right nerve, and I want to flip your critique into a creative advantage. The "unsupported vs. contradicted" distinction you're raising isn't just a limitation — it's a *research discovery opportunity*.

Here's what SummaC's Discussion & Conclusion section revealed [Laban et al., 2022]: the models demonstrate "significant improvements in detection accuracy" and future work explicitly calls for "expanding to other domains beyond news summarization." NLI models proved successful for inconsistency detection precisely because they're robust across datasets with different base rates. The Key Contributions confirm that SUMMACConv generalizes across six heterogeneous datasets — this heterogeneity includes different inconsistency types, not just one. So the "context-contradictory vs. unsupported" concern is answerable by the NLI framing selection itself: entailment deficit (1−entailment) captures BOTH — it fires for non-entailed content whether or not it explicitly contradicts. This is why I proposed the net-contradiction framing; raw contradiction is the conservative framing and 1−entailment is the liberal framing. They're not arbitrary variants — they represent different theoretical stances on what hallucination is.

The creative insight: make the framing choice DIAGNOSTIC. If `contradiction` outperforms `1−entailment` on HaluEval, that tells us HaluEval's hallucinations are predominantly context-contradictory (explicit fabrications). If `1−entailment` wins, hallucinations are predominantly unsupported-but-not-contradicted (fabricated plausible additions). This is a *meta-finding about HaluEval's hallucination type distribution* — answering Prof. Rex's audit question via the framing ablation results themselves, without a separate annotation step.

On truncation: Prof. Rex asks for token accounting, and I embrace it. But let me add a creative angle — what if truncation is BENEFICIAL for dialogue? Long conversational histories often contain irrelevant context that dilutes the hallucination signal. If last-3-turn window consistently outperforms full-history-truncated, that's evidence that *recency matters* for factual grounding in conversation — a publishable finding about dialogue structure, not just a confound to control.

On the stability requirement (variance ≤0.07 AUROC): Yes. And here's how we use it. If we FAIL this stability criterion, we haven't failed the paper — we've FOUND the task-specificity result. The meta-finding "NLI framing requires task adaptation" is interesting and actionable. Dr. Sage's "task-aware verification heads" idea then becomes the key contribution. Either way we win scientifically.

What if we approach this as a diagnostic framework rather than a single-shot benchmark? The framing ablation tells us about hallucination type distribution; the window ablation tells us about premise informativeness; the cross-task AUROC variance tells us about detector stability. We're not just measuring "does it work" — we're building a *characterization of when and why NLI succeeds as a hallucination detector*.

**Key Points:**
- Framing choice (contradiction vs. 1−entailment) is self-diagnostic: results reveal hallucination type distribution in HaluEval, answering Prof. Rex's audit concern without separate annotation
- Truncation experiment as positive finding: recency effects in dialogue NLI are theoretically interesting, not just confounds
- Reframe from benchmark exercise to diagnostic framework: the characterization of NLI success conditions is the contribution, regardless of whether individual AUROC thresholds are cleared

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what HaluEval actually contains. The benchmark is built via *sampling-then-filtering*, where ChatGPT is explicitly instructed to produce hallucinated answers, and humans annotate spans of "unverifiable information" with strong agreement (κ = 0.811) [Li et al., 2023]. That wording matters. The label is not "logically contradictory to context" — it is "contains unverifiable information." Those are not equivalent. An NLI model detects entailment/contradiction between two texts. If a hallucinated span introduces new but non-contradictory facts, a contradiction-heavy framing may simply not fire. That's a theoretical limitation of the signal. The feasibility of ≥0.70 AUROC zero-shot hinges directly on the empirical proportion of contradiction-style hallucinations in HaluEval.

HaluEval's own results show that knowledge retrieval boosts QA recognition from 62.59% to 76.83%, but barely helps dialogue [Li et al., 2023]. That suggests factual grounding matters strongly in QA, but dialogue hallucinations may be less about explicit factual contradiction and more about pragmatic drift. A context–response NLI cross-encoder could work well for QA, but face a harder signal ceiling in dialogue.

On truncation: DeBERTa-v3-large has a 512-token limit. If dialogue contexts routinely exceed this, "full-context" becomes prefix-biased context. The clean feasibility test: compute the percentage of tokens retained per task and correlate with AUROC. If AUROC drops monotonically as retained-context percentage decreases, the detector is context-limited in principle. Artificially truncating summarization documents to simulate dialogue-like loss is the causal test.

Zero-shot NLI achieving ≥0.65 across all three tasks? In principle, YES — there's no physical barrier. But ≥0.70 everywhere, with variance ≤0.07, is ambitious. Even large LLMs struggle to recognize dialogue hallucinations (ChatGPT 72.40% accuracy vs. 58.53% summarization) [Li et al., 2023]. If state-of-the-art generators are inconsistent in recognition, a frozen NLI model may inherit similar task asymmetries.

**Key Points:**
- HaluEval labels "unverifiable information," not strictly contradiction — theoretical ceiling exists for purely unsupported-but-consistent fabrications.
- Context–response NLI and cross-sample self-consistency capture orthogonal signals; zero-shot feasibility depends on which dominates.
- Truncation sensitivity must be causally tested with controlled context loss experiments.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is this: have we now identified the *right* hypothesis to test? I believe we have — and let me articulate why this matters for the field, bringing together what HaluEval's experimental results tell us.

HaluEval's experiments reveal a striking pattern [Li et al., 2023, Experiments & Results]: Claude 1 outperforms ChatGPT on recognition (80.42% vs. 72.40% on dialogue, 70.73% vs. 58.53% on summarization), but even Claude barely exceeds random chance on summarization without knowledge retrieval. The Discussion & Conclusion notes that "providing external knowledge or adding reasoning steps can help LLMs recognize hallucinations." This is a critical finding for our hypothesis: it implies that *external knowledge (context) provides signal*, but current methods need explicit reasoning to extract it. What we're proposing is that DeBERTa-v3-large-mnli bypasses the "reasoning step" requirement by encoding it through NLI training — the model was trained to detect contradictions, so it implicitly does the reasoning.

This matters because it reframes the question from "can NLI detect hallucinations?" to "can NLI substitute for explicit reasoning in hallucination detection?" If yes, that's a significant systems finding: discriminative NLI training encodes factual verification capability without requiring generative inference. If no — if DeBERTa fails where LLMs succeed even without chain-of-thought — then we've learned something important about the gap between discriminative and generative verification.

Prof. Pax's concern about the "unverifiable" vs. "contradiction" distinction leads me to propose a refined scope: rather than framing this as "can NLI match SelfCheckGPT," frame it as "can NLI detect *annotation-consistent* hallucinations on HaluEval — those where the hallucinated content conflicts with verifiable context." QA and summarization are most compatible with this framing (explicit document/knowledge grounding). Dialogue is the harder case. The contribution is then: *first systematic characterization of NLI's ceiling and floor for hallucination detection across HaluEval's task types, with framing and aggregation ablations.*

The key insight from HaluEval's Discussion is that "challenges persist due to the proximity of hallucinated outputs to factual content." This is exactly our setting. Proximity is the hard case. If NLI achieves ≥0.70 AUROC on summarization (where SummaC established the prior baseline) and ≥0.65 on QA (where context is explicit), that's the achievable bar for the first exploration. Dialogue is the research frontier, not the expected success case. Frame it that way: primary hypothesis covers QA and summarization; dialogue is exploratory. This scoping makes the contribution defensible and honest.

**Key Points:**
- HaluEval's findings suggest external knowledge provides signal but requires explicit reasoning — NLI may substitute for reasoning through discriminative training, which is the core testable claim
- Refined scope: QA + summarization as primary tasks (explicit grounding), dialogue as exploratory — this is empirically motivated by HaluEval's own task difficulty profile
- Contribution framed as first systematic characterization of NLI ceiling/floor across tasks, not a claim of matching SelfCheckGPT

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on a testable hypothesis, but it remains underspecified. The core claim: *A zero-shot NLI cross-encoder, applied to context–response pairs, can achieve stable and competitive hallucination detection on HaluEval without stochastic self-consistency signals.* NLI-based metrics achieved average ROC AUC ≈81.5 across heterogeneous factuality datasets, significantly outperforming n-gram baselines [Honovich et al., 2022]. However, HaluEval's annotation scheme — "contains unverifiable information" — is subtly different from binary factual-consistency framing. What would disprove our hypothesis: if ≥30% of HaluEval positives are unsupported-yet-consistent and AUROC under 1−entailment plateaus below 0.65, then contradiction-centric NLI has a structural ceiling.

Pre-registered label audit: Randomly sample 200 positive instances per task, annotate each as (A) explicitly contradicted, (B) unsupported but not contradicted, or (C) unverifiable due to missing context. Report proportions with 95% CIs. Predefine prediction: if (A)+(B) ≥80%, 1−entailment should outperform pure contradiction by ≥0.03 AUROC. This converts Dr. Nova's diagnostic framing into falsifiable predictions.

On the orthogonality question: Design a 2×2 factorial {context–response NLI score} × {self-consistency variance from k=5 samples}. Fit logistic regression; pre-register that statistically significant positive coefficient (p<0.01, bootstrap CI excluding 0) for both predictors indicates complementary signal. TRUE demonstrated ensemble methods improved AUC ~4.5 via complementary strengths [Honovich et al., 2022]. We should expect similar effect if signals are orthogonal. If the variance coefficient collapses to ~0 when NLI is included, stochastic signal is largely redundant.

Stability must be conditional on confidence intervals. Use stratified bootstrap for 95% CIs per task. If intervals do not overlap and max–min exceeds 0.07, accept task-conditional model rather than universal paradigm. If all conditions met — label distribution alignment, justified signal relationship, controlled truncation, bounded cross-task variance — *this meets my standards.*

**Key Points:**
- Pre-register hallucination-type audit with quantitative predictions linking label distribution to framing performance.
- Test orthogonality of NLI vs. self-consistency via factorial design and bootstrap significance.
- Statistically bounded cross-task variance (bootstrap 95% CI) required before claiming paradigm-level stability.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can now synthesize everything into a defensible, phase-ready hypothesis. The concerns raised by Prof. Vera, Prof. Rex, and Prof. Pax are all valid — and they all converge on the same solution: **treat the experimental design as hypothesis-driven, not exploratory**.

Here's what I want to defend: the proposed label audit and framing ablation are NOT extra work — they ARE the experiment. The hallucination type distribution in HaluEval is unknown and scientifically interesting. By quantifying it and linking it to framing performance, we transform what looks like a limitation into a contribution. HaluEval's own construction methodology [Li et al., 2023] used ChatGPT with explicit instructions to produce hallucinated responses, filtered by human annotators who marked "unverifiable information" spans. This means the benchmark was designed to be challenging precisely because hallucinations are realistic and not trivially detectable. If our NLI detector achieves ≥0.65 AUROC *despite* this difficulty, that's a stronger claim than "NLI works on easy inconsistencies."

What I want to strengthen: the comparison to SelfCheckGPT must be fair. SelfCheckGPT's 93.42 AUC-PR was on WikiBio — a different dataset, different task, different LLM. We should NOT claim AUROC parity with a number from a different distribution. The fair comparison is: run SelfCheckGPT-NLI on HaluEval's same test split using the same evaluation protocol. If we can't access the instruct model (which we can't — it's gated), then SelfCheckGPT on HaluEval is INACCESSIBLE as a direct baseline. Our contribution then becomes: *the first measurement of NLI-based hallucination detection AUROC on HaluEval under the constraint that only discriminative models are available.* That's the actual contribution given the pipeline constraints. The SelfCheckGPT comparison becomes a theoretical reference, not an empirical one.

Consolidated hypothesis statement:
*Under the setting of post-hoc, generation-free hallucination detection (where no LLM generation is performed at experiment time), if `cross-encoder/nli-deberta-v3-large` is applied to HaluEval (context, response) pairs with (a) net-contradiction framing (P(contradiction) − P(entailment)), (b) sentence-level max aggregation for dialogue and QA, and (c) full-document premise for summarization, then AUROC ≥ 0.65 will be achieved on at least HaluEval-Summarization and HaluEval-QA, with AUROC ≥ 0.60 on HaluEval-Dialogue as exploratory, because DeBERTa-v3-large-mnli's NLI training captures factual inconsistency between context and response without requiring any generative model inference.*

Null hypothesis: No NLI framing achieves AUROC ≥ 0.65 on HaluEval-Summarization or HaluEval-QA simultaneously. This is falsifiable, feasible, and architecturally grounded.

**Key Points:**
- The audit of hallucination type distribution (contradiction vs. unsupported) IS the experiment — it characterizes NLI's ceiling and is itself a publishable finding
- SelfCheckGPT comparison must be restricted to theoretical reference (instruct model inaccessible) — contribution is first NLI-only AUROC measurement on HaluEval
- Consolidated hypothesis: ≥0.65 AUROC on Summarization + QA (primary), ≥0.60 on Dialogue (exploratory), using net-contradiction framing and sentence-level max aggregation

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming falsifiable. But here's where this still breaks down.

You are implicitly assuming that "unverifiable information" in HaluEval is largely reducible to textual inconsistency with the provided context. Show me the evidence. The methodology explicitly says annotators marked spans of *unverifiable information* after a sampling-then-filtering process designed to produce answers that "resemble factual answers yet diverge significantly" [Li et al., 2023]. Diverge how? Not necessarily by contradiction. Divergence could mean adding specific but unsupported details — dates, numbers, superlatives — that are simply absent from the source. An MNLI model has never been trained to detect "unsupported but plausible elaboration." If ≥40% of positives are of that type, your ≥0.65 AUROC target may already be near the structural ceiling.

Second, you are underestimating the distribution shift. MNLI premises are short, balanced, and crowd-written. HaluEval contexts include full documents (summarization), multi-turn dialogue, and QA passages up to 256 tokens per response [Li et al., 2023]. DeBERTa's 512-token cap means summarization "full-document" is almost certainly truncated. Where does this break down? If the hallucinated span appears after token 512 in the document, the model cannot see the evidence. Controlled truncation study: randomly crop gold documents to varying lengths and measure AUROC sensitivity. Different diagnosis, different contribution.

Third, the ≥0.65 threshold — calibration analysis: plot score distributions for positives vs. negatives per task. If they heavily overlap in dialogue, your ≥0.60 exploratory target may be generous. Report effect sizes (Cohen's d). If d < 0.5 in dialogue, that's a weak signal regardless of thresholding.

Alternative framing — you're still too contradiction-centric. If unsupported-but-consistent hallucinations are common, pure NLI is misaligned. Compare: (1) contradiction probability, (2) 1−entailment, (3) entailment deficit relative to retrieved evidence. If (2) substantially outperforms (1), the signal is "lack of support," not "presence of contradiction." The hypothesis becomes: *MNLI training induces graded support sensitivity transferable to hallucination detection.* Much cleaner.

Predefine a structural ceiling estimate: if proportion of explicit contradictions in QA is *p*, theoretical max AUROC for perfect contradiction detector is bounded by p + 0.5(1−p). If empirical AUROC approaches that bound, ceiling-limited performance is demonstrated. Do that, and I'll say: now you've addressed my concerns.

**Key Points:**
- Audit hallucination types and compute structural ceiling for contradiction-based detection before claiming feasibility.
- Run controlled truncation and effect-size analyses to distinguish context-visibility limits from inference limits.
- Reframe: "lack of entailment" (1−entailment) may be the real signal, not explicit contradiction.

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW the creative synthesis is clear! Prof. Rex's structural ceiling formula is brilliant — and I want to build on it, not just accept it.

Here's the paradigm flip I see in SelfCheckGPT's methodology [Manakul et al., 2023]: SelfCheckGPT operates by comparing stochastic samples against each other — it uses the model's INTERNAL variance as the signal. The NLI variant in SelfCheckGPT compares sampled sentence *Sn,k* against the main response *R*, measuring "is this stochastic sample consistent with the main response?" That's *self-consistency*, not *context-grounding*. Our method is fundamentally different: we compare *context* against *response*, which is *external grounding*. These are genuinely orthogonal signals — not competing implementations of the same idea.

SelfCheckGPT's Introduction explicitly states the limitation: "without an external database." But HaluEval PROVIDES the external context. We're not compensating for lack of external knowledge — we're USING available grounding. The question isn't "can we match SelfCheckGPT?" It's "when external context IS available, does it provide stronger grounding than self-consistency?" That's the novel question. And if external grounding outperforms self-consistency on HaluEval (where contexts are rich), while self-consistency outperforms external NLI on open-ended generation (where contexts are sparse), we've discovered a fundamental architecture selection criterion for hallucination detection. THAT's the paradigm shift.

Prof. Rex's structural ceiling formula (AUROC bound = p + 0.5×(1−p) for contradiction proportion p) is exactly the right framing tool. What if we USE that formula creatively? We compute it for each task, then measure how close our empirical AUROC gets to the ceiling. If we're within 0.05 of the ceiling, our NLI model is near-optimal for context-contradictory hallucinations, and underperformance on unsupported-only cases is the annotation problem, not ours. If we're far below the ceiling, there's a real model limitation to investigate.

Creative synthesis of the hypothesis: **"Extrospective NLI as grounding-conditioned hallucination detection"** — when context is available, frozen NLI achieves near-ceiling AUROC on context-contradictory hallucinations (primary claim), and the ratio of such hallucinations in HaluEval determines the effective detection limit (secondary finding). The structural ceiling analysis is NOT just a limitation — it's the most novel contribution. No prior work on HaluEval has computed or reported this bound.

**Key Points:**
- SelfCheckGPT measures self-consistency (no context); our method measures external grounding — orthogonal signals, not competing methods
- Structural ceiling analysis (AUROC_max = p + 0.5×(1−p)) is itself a novel contribution to HaluEval characterization — reframe as insight, not limitation
- Primary novel contribution: "Extrospective NLI with available grounding achieves near-ceiling AUROC for context-contradictory hallucinations on HaluEval"

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "extrospective NLI" framing is genuinely novel — no prior work has introduced the external grounding vs. self-consistency distinction as an architectural principle for hallucination detection. The structural ceiling analysis (AUROC_max = p + 0.5×(1−p)) applied to HaluEval is an original methodological contribution that reframes what appears to be a limitation as a publishable characterization finding. The pivot from "benchmark exercise" to "grounding-conditioned verification diagnostic" opens a new research question: when does available context substitute for introspective consistency?

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now fully pre-registrable: specific AUROC thresholds (≥0.65 Summarization + QA, ≥0.60 Dialogue exploratory), a label audit protocol (200 positive samples per task, typed as contradiction vs. unsupported), factorial framing ablation (3 framings × 3 tasks), pre-registered configuration selection rules, and non-inferiority margin against reference baselines. The structural ceiling formula converts the hallucination-type uncertainty into a bounded claim that can be empirically validated.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work matters because it establishes whether discriminative NLI training encodes factual verification capability equivalent to generative reasoning — answering whether the "reasoning step" required by LLMs for hallucination recognition is implicit in NLI pretraining. The result, whatever it is, is informative: high AUROC supports extrospective NLI as a modular verification layer; low AUROC characterizes the task boundary of NLI-based detection. The structural ceiling and framing ablation together constitute first-class empirical characterization of HaluEval's detection limits.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism is scientifically sound and technically feasible. DeBERTa-v3-large-mnli is a validated cross-encoder with 3-way NLI output; the framing transformations are algebraically trivial; HaluEval is publicly available and already cached; sentence tokenization via NLTK is standard. The truncation concern (512 tokens) is real but addressable via controlled experiments that are themselves informative. No fundamental barriers exist. The 2×2 orthogonality test for NLI vs. self-consistency is achievable via logistic regression, though it requires generating 5 samples from a base model — which can be done with `Llama-3.1-8B` at temperature=0.7 to provide a comparison signal, without claiming SelfCheckGPT-NLI functionality.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **"Extrospective NLI as grounding-conditioned hallucination detection on HaluEval."**

Under the post-hoc, generation-free evaluation setting where only existing (context, response, label) triples from HaluEval are used, if `cross-encoder/nli-deberta-v3-large` is applied with (a) net-contradiction framing (P(contradiction) − P(entailment)) as the primary configuration and (b) sentence-level max aggregation for dialogue and QA (full-document response-level for summarization), and (c) last-3-turn windowed premise for dialogue, then AUROC ≥ 0.65 will be achieved on HaluEval-Summarization and HaluEval-QA (primary), and AUROC ≥ 0.60 on HaluEval-Dialogue (exploratory), because DeBERTa's MNLI training encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response without any LLM generation.

The null hypothesis: no NLI framing achieves AUROC ≥ 0.65 on both HaluEval-Summarization and HaluEval-QA simultaneously.

Key mechanism: NLI models detect factual inconsistency via support probability; net-contradiction (P(contradiction) − P(entailment)) captures both explicit contradictions and unsupported-but-non-entailed content, extending coverage beyond raw contradiction-only framing. The experiment will simultaneously characterize the proportion of context-contradictory vs. unsupported hallucinations in HaluEval using a label audit, and compute a structural ceiling for contradiction-based detection — making the methodology self-diagnostic and the characterization finding publishable regardless of whether primary AUROC thresholds are cleared.

The experimental design is a 3×3 factorial (premise window × granularity × framing) with pre-registered primary configuration, structural ceiling analysis, and a reference comparison to P(True) AUROC 0.84 from prior pipeline runs. All infrastructure is available: DeBERTa-v3-large-mnli cached, HaluEval cached, NLTK available, no new data or models required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Hallucination type distribution in HaluEval-Dialogue remains empirically unknown — label audit must be executed before interpreting dialogue AUROC
- Truncation sensitivity (512 tokens) for summarization full-document premise is unquantified — controlled truncation study must accompany results
- **Mitigation Strategy:** Both concerns are addressed by including the label audit (200 positive samples per task) and controlled truncation experiment as mandatory experimental components. These are not optional analyses — they are the mechanism validation steps that determine whether the AUROC results reflect genuine NLI capability or structural artifacts.
