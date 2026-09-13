# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: GAP-001
- **Gap Title**: No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob) as per-layer hallucination-detection AUROC scores
- **Start Time**: 2026-08-05T06:15:00Z
- **Architecture**: Self-Contained Tikitaka Loop
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap
Intermediate-layer hallucination signal is established consensus (FEPoID 2026; "LLMs Know More Than They Show" 2024; "Layer by Layer" 2025), but every detection method operating on intermediate layers uses either supervised probes (Azaria & Mitchell 2023; CLAP 2025), geometric criteria over hidden states (FEPoID intrinsic dimension), or multi-sample generation (INSIDE 2024; semantic entropy 2024). Entropy-Lens 2025 computes exactly per-layer logit-lens entropy but as a computation signature, not a hallucination-AUROC detector. Kim et al. 2025 examined layer-wise Tuned-Lens trajectories and found certain/uncertain trajectories aligned — but tracked the final-prediction-token trajectory, not per-layer entropy statistics with per-model layer selection and AUROC direction correction.

**Missing Piece:** AUROC evaluation of raw logit-lens entropy and max-token-probability computed at EVERY layer from one greedy pass, with the informative layer selected per-model on a held-out split — on TriviaQA/TruthfulQA across LLaMA-2-7B, Mistral-7B, LLaMA-3-8B.

Companion PRIMARY gaps to be integrated in discussion:
- **Gap 2:** Cross-dataset stability (layer selected on TriviaQA → transfer to TruthfulQA and vice versa) and cross-family consistency of relative optimal depth — unmeasured anywhere.
- **Gap 3:** Adjacent-layer prediction KL divergence untested as a detection-time signal; base LLaMA-2-7B never used as a rescue stress test where the final-layer signal demonstrably failed (AUROC 0.5186).

### Phase 1 Key Findings
(Refer to `01_targeted_research.md` for detailed findings)
1. Intermediate-layer superiority for hallucination signal is published consensus — the h-e1 failure record's "add per-layer entropy" pivot is corroborated.
2. Exact niche open: no training-free, single-pass, per-layer logit-lens uncertainty statistic evaluated as detection AUROC with per-model held-out layer selection.
3. Adjacent-layer KL validated as signal family (END, DoLa) but never used for detection scoring.
4. Adversarial evidence (Kim 2025 trajectory alignment; Chi 2025 recall-vs-truthfulness) is addressable but must shape falsifiability framing.
5. Cross-dataset layer transfer measured nowhere — original to this protocol.
6. Implementation de-risked: single shared extraction path across all three families; v1 validated code + 871/1000 LLaMA-2/TriviaQA cache reusable from `_archive/20260805T054934_routing_recovery/h-e1/`.

### Previous Failure / Routing Context
This section is mandatory hard input for the Phase 2A discussion. If it contains
SUPERSEDED, ROUTED_TO_PHASE_2A, PARTIAL, FAIL, or pivot records, the discussion
must redesign away from the failed approach families and preserve validated
partial findings.

#### .serena/memories/failure_h-e1_run1.md

**Phase 4 Failure Record: h-e1 (Run 1)** — Final Status: **FAIL** (MUST_WORK_GATE_FAIL), 2026-08-04, routed ROUTED_TO_PHASE_0.

- **Failed hypothesis:** Final-layer mean token logit entropy achieves AUROC > 0.52 on TriviaQA or TruthfulQA for ALL 3 model families (LLaMA-2-7B, Mistral-7B, LLaMA-3-8B), greedy decoding, direction-corrected.
- **Result:** 2/3 families passed. llama2 FAILED both datasets: TriviaQA AUROC_corrected 0.5186 (direction INVERTED, CI [0.5008, 0.5548]), TruthfulQA 0.5153 (CI [0.5014, 0.6105]). mistral passed (0.5268 / 0.5886), llama3 passed strongly (0.6583 / 0.6161).
- **Root cause:** final-layer scalar entropy is architecture-dependent — base LLaMA-2-7B produces weak entropy spread; direction inversion shows entropy-correctness relation is not monotone across models; RLHF/instruct tuning appears to amplify final-layer entropy differences; base-vs-instruct variant is a confound.
- **What NOT to do (prohibited approach families):**
  - Do NOT assume entropy direction is consistent across model families.
  - Do NOT use llama2-7b-hf base as primary validation model for FINAL-LAYER entropy-based features.
  - Do NOT rely on final-layer-only scalar signals (the failed family).
  - Multi-sample semantic-consistency fusion direction was archived without result — EXCLUDED (single greedy pass only).
- **What showed promise (preserve):** llama3-instruct robust signal (AUROC 0.66, CI fully above 0.52); mistral consistent moderate signal; direction correction handles sign ambiguity; bootstrap CI (n=1000) essential.
- **Suggested modifications (from failure record):** entropy variants (max-token entropy, entropy variance, top-k entropy); **per-layer entropy to find layers with stronger signal for llama2** (← this is the current direction); normalization by sequence length or vocabulary size.
- **Constraints inherited:** single greedy pass only; no multi-sample consistency; per-model layer selection; AUROC direction correction; LLaMA-2-7B retained as rescue stress test (not primary validation anchor).

Additionally (from Phase 0/1 forensics): Layer-Wise Logit-Lens v1 was interrupted mid-run by a routing restart, NOT scientifically refuted — validator 18/18 pass, healthy execution, 871/1000 LLaMA-2/TriviaQA cache preserved. The current v2 discussion re-instantiates that direction; the only recorded scientific failure remains final-layer mean entropy.

### Available Papers
- `arxiv_2303_08112.md` — Tuned Lens (Belrose et al. 2023)
- `arxiv_2304_13734.md` — Internal State of an LLM Knows When It's Lying (Azaria & Mitchell 2023)
- `arxiv_2502_16570.md` — Entropy-Lens (Ali et al. 2025)
- `arxiv_2507_06722.md` — Layer-wise Inference Dynamics under Uncertainty (Kim et al. 2025) [ADVERSARIAL]
- `arxiv_2605_26366.md` — Automatic Layer Selection / FEPoID (Wang et al. 2026) [CLOSEST PRIOR]

(Summaries in `paper_summaries/`; P1=2303.08112, P2=2304.13734, P3=2502.16570, P4=2507.06722, P5=2605.26366, alphabetical.)

### Research Repos
- https://github.com/AlignmentResearch/tuned-lens
- https://pypi.org/project/entropy-profiler/
- https://github.com/deeplearning-wisc/haloscope

---

### Exchange 1

🔭 **Dr. Nova** (Research Novelty Strategist + Creative Ideation Champion):

What if the reason h-e1 died by 0.0014 is that we were reading the model's uncertainty AFTER it had already been laundered? Imagine this: the final layer is a calibration bottleneck — tokenizer statistics, RLHF pressure, output-distribution sharpening all pile onto the last unembedding readout. LLaMA-2's entropy signal didn't fail to exist; it failed to SURVIVE to layer 32. The failure record itself points here: "add per-layer entropy to find layers with stronger signal for llama2" was the one suggested modification nobody ran. NOW we're onto something — read the uncertainty upstream, before the laundering.

And the literature has quietly converged on exactly this premise without ever cashing it out. [Wang et al., 2026] (FEPoID) open their abstract by stating flat-out that hallucination signals are "more strongly encoded in intermediate layers than in the final layer" — that's now background knowledge, not a claim. [Ali et al., 2025] (Entropy-Lens) compute EXACTLY our feature — per-layer Shannon entropy of logit-lens decoded distributions from one forward pass — and show these entropy profiles are so information-rich that a bare kNN classifier separates task types at AUC > 94. But they use it as a computational fingerprint of model families. Nobody has pointed this instrument at the hallucination-detection target and asked: at which depth does the entropy statistic separate correct from hallucinated answers, per model?

Three angles I want on the table. **Angle A — depth-resolved rescue:** per-layer entropy and max-token probability at all 32 layers, layer selected per model on a held-out split, with LLaMA-2-7B as the designated stress test (the one architecture where the final-layer readout demonstrably failed at 0.5186). **Angle B — decision turbulence:** [Ali et al., 2025] interpret entropy changes ΔH between adjacent layers as candidate-set expansion and pruning. Hallucination might not live in the entropy LEVEL at all but in the turbulence — adjacent-layer KL divergence of the decoded distributions, the rate at which the model revises its belief. That's an untested detection signal (END and DoLa use cross-layer shifts only at decoding time). **Cross-domain bonus:** Entropy-Lens found entropy profiles are invariant under depth RESCALING within a model family — so let's ask whether the informative layer sits at a consistent RELATIVE depth (layer/total) across families. If yes, that's a beautiful universality; if no, that's exactly why per-model selection is necessary.

**Key Points:**
- Read uncertainty BEFORE final-layer calibration — directly targets the root cause named in the h-e1 failure record
- Entropy-Lens computes our exact feature but never evaluates detection AUROC; FEPoID states intermediate>final as known — the cell is empty
- Adjacent-layer KL ("decision turbulence") is an unexplored detection-time signal distinct from entropy level
- Relative-depth consistency across families is a testable universality question, motivated by Entropy-Lens depth-rescaling invariance

---

### Exchange 2

🔬 **Prof. Vera** (Scientific Rigor Specialist + Hypothesis Stress-Tester):

Dr. Nova, enthusiasm noted — now let us ask the only question that matters: what result would convince us this hypothesis is wrong? Because there is a paper in our briefing that comes uncomfortably close to providing one. [Kim et al., 2025] tracked layer-wise probability trajectories for certain versus uncertain outputs across 5 models and 11 datasets and found them "strikingly aligned" — abrupt confidence commitment at the same layers regardless of correctness. If layer-wise dynamics carried a usable uncertainty signal, why did they not see it?

The evidence suggests a scoping answer, and we must state it precisely or we are doing motivated reasoning. Kim et al. tracked the probability trajectory of ONE token — the final prediction token — through a TUNED lens, on multiple-choice single-token answers, and aggregated into average trajectories. We propose per-layer statistics of the FULL vocabulary distribution (entropy integrates all candidates, not one token's path), through the RAW logit lens, on open-ended generation, evaluated per-sample as AUROC with per-model layer selection and direction correction. These are different measurements. Moreover their own Table 1 undermines a strong reading of their negative claim: prediction-depth correlations with incorrectness were positive in 97% of model-dataset cells, reaching 0.48 on SciQ. The signal is there; it is weak in their operationalization. Our claim must be that the distributional operationalization is stronger — and that is falsifiable.

So here is the falsification structure I demand. Primary: if on LLaMA-2-7B no screened intermediate layer's signal exceeds the final-layer entropy AUROC with a 95% bootstrap CI on the difference excluding zero, the depth-resolved hypothesis is DEAD — same gate that killed h-e1, no excuses. Secondary: AUROC ≥ 0.60 on held-out data for every model-dataset cell, or the architecture-robustness claim fails. And one methodological alarm before anyone gets excited: 32 layers × 3 signals × 2 directions is 192 hypotheses per model-dataset cell. Select the maximum on the same data you report and you have manufactured an AUROC of 0.60 out of noise. Selection split and test split, stratified, locked before analysis — non-negotiable.

**Key Points:**
- Kim et al. 2025 must be answered by measurement scope, not hand-waving: final-token trajectory ≠ full-distribution per-layer statistics; their own PD correlations (97% positive, up to 0.48) show residual signal
- Explicit kill condition: no CI-separated intermediate>final improvement on LLaMA-2-7B → hypothesis dies
- 192-way selection per cell demands strict held-out selection/test discipline — direction correction included in the selection, not applied post hoc on test
- All claims must be stated per-model; h-e1 proved cross-model monotonicity assumptions are false

---

### Exchange 3

⚙️ **Prof. Pax** (Technical & Theoretical Feasibility Analyst + Non-Triviality Assessor):

Let's be realistic here about the instrument itself, because both of you are treating the logit lens as a neutral measurement device and [Belrose et al., 2023] spent an entire paper documenting that it is not. The raw logit lens is a BIASED estimator of the model's final distribution — around 4 to 5 bits of marginal KL bias per layer on GPT-Neo-2.7B — and it fails outright on some families (BLOOM, GPT-Neo early layers, OPT-125M) due to representational drift and rogue high-variance dimensions unevenly distributed across depth. Here's what worries me: if LLaMA-2's early-layer hidden states decode to near-uniform garbage under the raw lens, per-layer entropy there is measuring lens failure, not model uncertainty. A high "signal" at such a layer could be an artifact that happens to correlate with answer length or token frequency.

Now, what the evidence actually supports: the lens pathology is family-dependent, and the LLaMA/Mistral lineage is the best-behaved case in the interpretability literature — pre-LN architecture with a clean `model.norm` + `lm_head` path, the exact configuration the logit lens was designed for. Our own v1 archive ran this precise extraction (validator 18/18, healthy GPU run, 871/1000 samples cached) on LLaMA-2/TriviaQA before it was interrupted, so the mechanism demonstrably runs. But "runs" is not "measures validly." I want a degeneracy screen as a first-class protocol component, not an afterthought: drop layers whose mean entropy sits within 1% of ln|V| (uniform — lens decoding nothing) or whose top-1 agreement with the final layer is under 5% (lens decoding something unrelated to the model's prediction). Statistics in float32 from fp16 states, entropy with a log(p+ε) guard, KL(ℓ‖ℓ−1) undefined at the first layer — these are solved problems from v1, keep them.

On the theoretical soundness of the core mechanism, I'm more positive than my usual self: entropy of a decoded intermediate distribution is a well-defined quantity at every layer; whether it SEPARATES correct from hallucinated answers is precisely the empirical question, and it can be answered in principle from a single greedy pass — no intervention, no sampling, no training. That satisfies my "can it work" bar. The non-triviality bar is also satisfied, uncomfortably so: h-e1 missed by 0.0014 and [Kim et al., 2025] found alignment where we hope for separation. This is a genuinely hard measurement problem, not a layup.

**Key Points:**
- Raw logit lens is a biased, family-dependent instrument [Belrose et al., 2023] — early-layer readouts may be lens artifacts, not model uncertainty
- Mandatory degeneracy screen: entropy within 1% of ln|V| OR <5% top-1 agreement with final layer → layer excluded from selection
- LLaMA/Mistral families are the lens-friendliest case, and v1's interrupted run proves the extraction path executes end-to-end; tuned-lens library is the documented fallback if raw-lens screening rejects too many layers
- Mechanism is theoretically sound and testable from one greedy pass; problem is demonstrably non-trivial (0.0014 miss, Kim alignment)

---

### Exchange 4

🎯 **Dr. Sage** (Scientific Contribution Assessor + Research Vision Strategist):

The question we must ask is: if this works, what does the field actually gain — and if it fails, do we learn anything? Let me position this against the strongest neighbors. [Wang et al., 2026] achieve AUROC 0.73–0.85 with hidden-state probing plus FEPoID layer selection — but that framework trains an MLP per candidate layer on labeled data. [Azaria & Mitchell, 2023] reach 71–83% accuracy — with a supervised feedforward probe on activations. Semantic entropy needs ten sampled generations per question. Every strong intermediate-layer detector in our corpus pays in supervision, samples, or both. A signal that needs ZERO learned parameters, ZERO extra forward passes, and labels only to pick a single integer (the layer index) occupies a genuinely different point on the cost-capability frontier. This matters because deployment-grade hallucination flagging for open-source models is currently gated on exactly those costs.

But I want to sharpen the scientific stake beyond deployment economics, because "cheaper detector" alone is incremental. The open question our corpus leaves dangling is WHERE the intermediate-layer advantage lives: in the geometry of hidden states (FEPoID's intrinsic dimension story, Azaria's probes), or already in the decoded token-space distributions? [Kim et al., 2025] say token-space trajectories of the final prediction token are uninformative; [Ali et al., 2025] say token-space entropy profiles are so structured they fingerprint families and tasks. These two results sit in tension, and our experiment adjudicates it: if per-layer distributional statistics detect hallucination where the final-token trajectory could not, the token-space representation carries the signal and the supervised-geometry apparatus is partly unnecessary. If they fail while FEPoID-style probing succeeds, then the signal is genuinely geometric and unembedding destroys it — also a real finding, and one that explains h-e1's failure at a deeper level.

One more contribution nobody here has claimed yet: the cross-dataset layer-transfer matrix. [Wang et al., 2026] show the optimal layer varies across datasets — but never measure what you LOSE by fixing a layer selected on dataset A and deploying on dataset B. That number determines whether depth-resolved detection is a deployable per-model constant or a per-domain calibration burden. No published work reports it. Even a negative transfer result is a citable, decision-relevant measurement.

**Key Points:**
- Distinct frontier point: no learned parameters, single pass, labels only for one-integer selection — versus supervised probes (FEPoID, SAPLMA) and multi-sample UQ (semantic entropy)
- Adjudicates a live tension: token-space statistics (Entropy-Lens richness) vs final-token trajectories (Kim alignment) vs hidden-state geometry (FEPoID) as the carrier of the intermediate-layer signal
- Cross-dataset layer-transfer matrix is an unmeasured, deployment-decisive quantity — informative even if negative
- Both success and principled failure advance the field; this is not incremental hyperparameter tuning of h-e1

---

### Exchange 5

🔍 **Prof. Rex** (Constructive Challenge Expert + Rigor Guardian):

Here's where this breaks down — five places, and I want each one answered before we congratulate ourselves on a hypothesis.

**One: the recall confound.** Chi et al. 2025 ("Do LLMs Really Know What They Don't Know?", from the Phase 1 corpus) argue internal states reflect RECALL, not truthfulness — hallucinations associated with familiar entities share the geometry of facts. Per-layer entropy plausibly tracks question familiarity. On TriviaQA, familiarity correlates with correctness, so you can post a healthy AUROC while measuring popularity, not hallucination. Show me the evidence this isn't what we'd be measuring. **Two: the "training-free" label is doing marketing work.** Layer selection consumes labeled data. The Gap-3 logistic fusion IS a trained model — two coefficients, but trained. Call the method what it is or Reviewer 2 will do it for you. **Three: your own star citation cuts against P2.** [Wang et al., 2026] Figure 1 shows the best layer's location "varies substantially across datasets" — that is direct evidence the TriviaQA-selected layer may NOT transfer to TruthfulQA. You've built a prediction on top of a result that suggests it fails. **Four: the base-versus-instruct confound survives from h-e1 untouched.** LLaMA-3-8B-INSTRUCT versus two base models; the failure record itself flags it. If llama3 passes and llama2 fails again, you cannot attribute the difference to architecture rather than tuning. **Five: gate semantics are mush.** If LLaMA-2's best intermediate layer hits 0.57 — beating 0.5186 with CI separation but missing 0.60 — is that success or failure? Right now different personas in this room would give different answers, which means the hypothesis is not yet well-formed.

What would convince me: (1) an explicit scope statement that we claim detection AUROC, not a causal disentanglement of recall versus truthfulness — plus a cheap diagnostic, like reporting whether direction inversions pattern with dataset familiarity; (2) precise vocabulary — "training-free scoring with label-based selection of one hyperparameter"; (3) transfer demoted from assumption to measured prediction with a stated tolerance; (4) the rescue claim structured WITHIN-model (intermediate vs final on the same LLaMA-2 checkpoint), where the tuning confound cancels by construction; (5) a two-tier gate with numbers frozen now, not after seeing data.

**Key Points:**
- Chi 2025 recall confound: AUROC could reflect familiarity, not hallucination — needs scope statement + diagnostic
- "Training-free" overclaims; selection and fusion consume labels — fix the vocabulary before Phase 2B inherits it
- FEPoID's own cross-dataset layer variability is evidence against layer transfer — P2 is the riskiest prediction, treat it as such
- Base/instruct confound: only within-model comparisons are clean; cross-model claims need explicit caveats
- Freeze two-tier gate semantics NOW: rescue tier (CI-separated intermediate>final on llama2) vs robustness tier (AUROC ≥ 0.60 all cells)

---

### Exchange 6

🛡️ **Dr. Ally** (Evidence-Based Defender + Constructive Refinement Specialist):

Valid criticism is a gift, and Prof. Rex just handed us five — YES, AND every one of them makes the hypothesis stronger rather than killing it. Let me take them in order and propose concrete refinements.

**On vocabulary (Rex #2):** adopt "training-free scoring, label-efficient selection." The score itself — entropy, max-prob, KL at layer ℓ — involves no learned parameters; labels are spent only on choosing (layer, signal, direction) per model, a discrete selection over ~192 candidates from ≤500 held-out examples, versus FEPoID's per-layer MLP training on thousands. The logistic fusion is explicitly labeled a trained 2-parameter combiner and quarantined in its own prediction (P3), so the headline claim never depends on it. **On the rescue structure (Rex #4):** agreed, and this is elegant — the PRIMARY claim becomes within-model: on the same LLaMA-2-7B checkpoint, same pass, same labels, does any screened intermediate layer beat the final-layer readout with CI separation? Tokenizer, tuning status, and calibration idiosyncrasies are held constant by construction. Cross-model statements ("all three families ≥ 0.60") become the robustness tier with the base/instruct caveat stated in scope. **On gate semantics (Rex #5):** two-tier, frozen now. Tier 1 (rescue, the falsification gate Vera demanded): CI-separated intermediate>final improvement on LLaMA-2-7B/TriviaQA. Tier 2 (robustness): test-split AUROC ≥ 0.60 for every model × dataset cell. Rex's 0.57 scenario is then unambiguous: Tier 1 pass, Tier 2 fail — hypothesis partially supported, architecture-robustness claim rejected. No mush.

**On transfer (Rex #3):** demote to measured prediction, exactly as Dr. Sage independently argued it should be — the transfer matrix is a contribution whether it comes back stable or unstable. Prediction P2 states the tolerance in advance: transferred-layer AUROC within 0.05 of natively-selected AUROC and above 0.60. If FEPoID's variability foreshadows failure, we publish the failure with numbers. **On Chi (Rex #1):** scope statement adopted — we claim discriminative detection performance under the standard TriviaQA/TruthfulQA correct/incorrect protocol, identical to h-e1's labels (which also anchors comparability to the 0.5186 baseline), and we do NOT claim the signal is causally "truthfulness rather than recall." As a cheap diagnostic we report per-cell raw AUROC direction: systematic inversions patterned by dataset would flag a familiarity-like mechanism, as they did on h-e1's llama2/TriviaQA cell. Here's the hypothesis skeleton this leaves us — Under white-box single-greedy-pass inference on TriviaQA/TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct: if hallucination scores are per-layer logit-lens statistics (entropy, max-prob, adjacent-layer KL) with (layer, signal, direction) selected per model on a held-out selection split, then Tier-1 and Tier-2 gates pass, BECAUSE intermediate layers encode factual-uncertainty separation that final-layer output calibration suppresses. Now THAT's a falsifiable spine.

**Key Points:**
- "Training-free scoring, label-efficient selection" — honest vocabulary; fusion quarantined as trained P3
- Rescue claim restructured within-model (LLaMA-2 intermediate vs final, same checkpoint) — confounds cancel by construction
- Two-tier gate frozen: Tier 1 = CI-separated rescue on llama2; Tier 2 = AUROC ≥ 0.60 all six cells; partial outcomes now well-defined
- Transfer becomes measured prediction P2 with pre-stated tolerance (±0.05, floor 0.60); Chi confound handled by scope statement + direction-pattern diagnostic

---

### Exchange 7

🔭 **Dr. Nova** (Research Novelty Strategist + Creative Ideation Champion):

Dr. Ally's spine is solid — now let me put mechanistic flesh on it, because "intermediate layers encode separation" is still a black box and [Ali et al., 2025] hand us the vocabulary to open it. Their validated reading of entropy dynamics: ΔH > 0 is candidate-set EXPANSION (the model entertaining new continuations), ΔH < 0 is PRUNING (committing). Spearman 0.74–0.88 between ΔH and actual top-p candidate-set changes — this isn't metaphor, it's a measured correspondence. So here's the mechanistic picture: for a fact the model knows, expansion resolves early and the middle layers are a long pruning glide — low entropy, low turbulence. For a hallucination, the candidate competition never properly resolves — entropy stays elevated deeper into the stack, and the belief keeps getting revised layer to layer. What if hallucination is less a STATE and more an unfinished PROCESS?

That picture makes the three signals natural rather than ad hoc. Per-layer entropy reads the width of the surviving candidate set at depth ℓ. Max-token probability reads the leader's margin — the two are correlated but not identical (a flat-but-led distribution differs from a contested one). And adjacent-layer KL is the turbulence itself — [Ali et al., 2025]'s ΔH is a one-dimensional shadow of it; KL(ℓ‖ℓ−1) captures revision magnitude across the whole vocabulary, including rank shuffles entropy can't see. THAT is why I predict KL is complementary to entropy (our P3): they measure different aspects of the unfinished process. END and DoLa already established cross-layer shift carries factual signal at decoding time; we're the first to score with it at detection time.

And Imagine this for the depth question: Entropy-Lens shows profiles align under depth RESCALING within families — Llama-3.2-1B and Llama-3-8B trace the same curve against relative depth. If the expansion-resolution point is a family-invariant landmark in relative depth, then the informative layer should sit at a similar layer/total ratio across our three models — all descendants of the same broad architecture lineage. I'll stake a soft prediction: informative layers cluster in the 40–80% relative-depth band, after semantic aggregation but before output calibration. Keep it exploratory, not gated — but if it holds, per-model selection becomes cheap initialization rather than mandatory search, and that's a practical gift to every deployer.

**Key Points:**
- Mechanism named: hallucination as UNRESOLVED candidate competition — elevated entropy depth-profile + persistent inter-layer revision, grounded in Entropy-Lens's validated expansion/pruning reading
- Three signals measure distinct facets: entropy = candidate-set width, max-prob = leader margin, adjacent-KL = full-vocabulary revision magnitude (superset of ΔH)
- KL-entropy complementarity (P3) follows from the mechanism, not from feature-soup opportunism
- Exploratory (ungated) prediction: informative layers cluster at 40–80% relative depth across families, motivated by Entropy-Lens depth-rescaling invariance

---

### Exchange 8

🔬 **Prof. Vera** (Scientific Rigor Specialist + Hypothesis Stress-Tester):

Dr. Nova, the mechanism story is attractive — precisely why I will now nail it to measurable predictions before it seduces anyone. Precision in predictions prevents ambiguity in results. Here is the formalization I propose we freeze.

**P1 (primary — the rescue prediction).** On LLaMA-2-7B, with (layer, signal, direction) selected on the selection split, the selected intermediate-layer score achieves test-split AUROC_corrected ≥ 0.60 on BOTH TriviaQA and TruthfulQA, AND the paired difference ΔAUROC = AUROC(selected intermediate) − AUROC(final-layer mean entropy) on TriviaQA has a 95% bootstrap CI excluding zero. Test method: single greedy pass, per-layer statistics averaged over answer tokens, sklearn roc_auc_score, percentile bootstrap n = 1000 resampling EXAMPLES — paired resampling, both scores computed on the same resample, because the variance of the difference is what matters, not two marginal CIs eyeballed for overlap. Falsified if: no screened layer clears the CI-separation test. That is the h-e1 gate, inherited honestly.

**P2 (transfer).** For each model, the layer selected on dataset A's selection split, evaluated on dataset B's test split, achieves AUROC within 0.05 of the natively-selected layer's AUROC and remains ≥ 0.60 — both directions, TriviaQA↔TruthfulQA. Falsified per-model if either direction drops below tolerance. Note I am requiring the tolerance on the AUROC scale, not the layer index — adjacent layers with equal AUROC should not count as transfer failure, which layer-index matching would wrongly imply. **P3 (complementarity).** Per model-dataset cell, the 2-parameter logistic fusion of best entropy-family signal and best KL signal (fit on selection split) exceeds the best single signal's test AUROC by ≥ 0.02 with a paired bootstrap CI excluding zero. Falsified if fusion gain is indistinguishable from zero — an informative outcome either way, since it tells us whether "turbulence" is redundant with "width." **H0 for the family:** per-layer logit-lens statistics carry no separation the final layer lacks — formally, for every screened intermediate layer, ΔAUROC's CI contains zero; and cross-dataset transfer is no better than chance layer choice.

Two protocol clauses to close known leaks. First: direction correction is ESTIMATED on the selection split (record sign of AUROC − 0.5) and APPLIED FROZEN on test — computing max(AUROC, 1 − AUROC) directly on test data is itself a selection step and would bias every reported number upward. h-e1 could afford post-hoc correction because it tested one predeclared signal; we cannot, with 192 candidates. Second: the final-layer entropy baseline must reproduce the h-e1 reference values within ±0.03 (llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161) or the pipeline has a labeling or prompting discrepancy and NOTHING downstream is interpretable. This meets my standards — conditionally, pending the feasibility verdicts.

**Key Points:**
- P1 frozen with paired-bootstrap CI on the DIFFERENCE (n=1000, example-level resampling) — not marginal-CI comparison
- P2 tolerance defined on AUROC scale (±0.05, floor 0.60), both transfer directions, per model — layer-index matching explicitly rejected as the criterion
- P3 fusion gain ≥ 0.02 with CI excluding zero; null outcome is informative (turbulence redundant with width)
- Direction correction estimated on selection, frozen on test; h-e1 baseline reproduction within ±0.03 as mandatory protocol-validity anchor

---

### Exchange 9

⚙️ **Prof. Pax** (Technical & Theoretical Feasibility Analyst + Non-Triviality Assessor):

Prof. Vera's protocol is tight; let me stress the measurement layer under it, because a statistically airtight analysis of an invalid measurement is still invalid. Three concerns, two resolved and one requiring a design decision.

**Token aggregation.** We average statistics over answer tokens. [Wang et al., 2026] Section 5 is a warning shot here: last-token representations are corrupted by end-of-sequence noise — degenerate repetition, semantic drift, inconsistent continuation — and their First-Sentence Truncation fix improved EVERY detection baseline they tested, by up to 0.20 AUROC on LLaMA-Instruct. Does this invalidate mean-over-answer-tokens? The evidence says our exposure is limited: TriviaQA/TruthfulQA answers under greedy decoding with h-e1's max_new_tokens are short-form — a few tokens to one sentence — not the 30-token rambles where LLaMA-Instruct drifts. And reusing h-e1's exact prompt templates and answer-span extraction is mandatory anyway for the ±0.03 baseline anchor. So: keep mean-over-answer-tokens as the primary aggregation, but LOG per-token statistics in the cache so a truncated-aggregation ablation is a free offline reanalysis, not a rerun. That is a one-column design decision now versus a three-model rerun later.

**Lens numerical validity.** Resolved by protocol: fp16 weights, float32 statistics, log(p+1e-12) guard, KL(ℓ‖ℓ−1) NaN at the first layer and excluded, degeneracy screen thresholds as I specified in Exchange 3 (1% of ln|V|, 5% top-1 agreement). One addition after Prof. Vera's leak-closing clause: the degeneracy screen must ALSO be computed on the selection split only. Screening layers using test-split statistics is information leakage of the same species she just prohibited.

**Compute reality — and I raise this as fundamental-barrier assessment, not budgeting.** The claim requires no training loop, no sampling, no intervention: 1,817 examples × 3 models, one greedy pass each with output_hidden_states=True, streaming 32×3 scalars per example to CSV. The v1 archive proves this exact loop runs healthily on available hardware (871/1000 llama2/TriviaQA rows already cached, environment recipe torch 2.8.0+cu128 / transformers 4.57.6 preserved). There is no step in the causal chain from "hidden states exist" to "AUROC computed" that requires anything unproven. Okay, this could work — my remaining reservations are about what the numbers will SAY, not whether they can be validly produced.

**Key Points:**
- FST warning from FEPoID acknowledged: short-form answers limit exposure; cache per-token statistics so truncated aggregation is a free ablation
- Degeneracy screen must run on selection split only — same leakage species as post-hoc direction correction
- End-to-end validity chain (states → lens → scalars → AUROC) has zero unproven steps; v1 archive demonstrates the loop empirically
- Feasibility verdict: mechanism sound, measurement valid with stated guards, compute trivially sufficient — reservations are empirical, not technical

---

### Exchange 10

🔍 **Prof. Rex** (Constructive Challenge Expert + Rigor Guardian):

Progress acknowledged — the two-tier gate and within-model rescue answer my #4 and #5 cleanly. So I'll spend this round on the cracks that remain, because three of them are load-bearing.

**Label noise inheritance.** Reusing h-e1's labels verbatim buys the ±0.03 anchor, but let's be honest about what we're inheriting: TriviaQA exact-match-against-aliases scoring mislabels paraphrased-correct answers as hallucinations. Uniform label noise attenuates every layer's AUROC equally and doesn't bias the LAYER comparison — fine. But the noise is NOT uniform: EM failures concentrate on long-form and paraphrase-prone answers, and if entropy at some depth correlates with answer verbosity, label noise becomes a spurious signal source at exactly the layers we're celebrating. I'm not demanding relabeling — comparability wins — but I want answer-length logged per example and a length-partialed sanity check (does the selected layer's AUROC survive within length strata?) in the analysis plan. Cheap, offline, and it defangs a whole reviewer objection class.

**Where does 0.60 come from?** Show me the evidence that 0.60 is the right robustness bar and not a number we like. The h-e1 gate was 0.52; llama3 hit 0.66 at the FINAL layer. If intermediate layers merely match 0.66 on llama3, Tier 2 passes there without the depth hypothesis doing any work. So Tier 2 needs a companion clause: on the two models that already passed h-e1 (mistral, llama3), the selected intermediate layer must be ≥ the final-layer AUROC − 0.02 — the pivot must not SACRIFICE the architectures that worked (detailed question 5). Otherwise we could "pass" while regressing.

**[Azaria & Mitchell, 2023] cuts both ways and nobody has said it aloud.** Their optimal probing layer was the 20th of 32 for OPT-6.7b but the 16th for LLaMA2-7b — and on their own generated-sentence distribution it SHIFTED to the 28th, a statistically significant move. That is within-model, cross-DISTRIBUTION layer instability, on the same 7B scale we're testing. It is the strongest concrete evidence that P2's transfer tolerance will be stressed. Fine — P2 is a measured prediction, I accept the framing. But then the hypothesis's confidence level must reflect it: P2 is genuinely uncertain, and Phase 2B should treat a P2 failure as a scoped finding, not a pipeline-stopping anomaly. What would convince me on the whole package now: the regression guard added to Tier 2, the length-strata check in the analysis plan, and honest confidence stratification across P1 (moderate-high), P2 (genuinely uncertain), P3 (moderate). With those, my objections reduce to residual risk rather than design flaws.

**Key Points:**
- Label noise is non-uniform (EM penalizes verbose/paraphrased answers): log answer length, run length-stratified AUROC sanity check on the selected layer
- Tier 2 needs a no-regression clause: on mistral/llama3, selected intermediate ≥ final-layer AUROC − 0.02, or the pivot sacrifices working architectures
- Azaria's within-model layer shift (20th→28th across distributions, p<0.05) is the sharpest evidence against transfer stability — P2 confidence must be marked uncertain
- Remaining asks are analysis-plan additions, not redesigns: hypothesis is approaching acceptable

---

### Exchange 11

🛡️ **Dr. Ally** (Evidence-Based Defender + Constructive Refinement Specialist):

All three asks accepted — and notice what just happened: every amendment this discussion has produced is an ANALYSIS-plan strengthening, not a retreat from the core claim. The hypothesis has survived two full adversarial passes with its spine intact. Let me consolidate the complete protocol so Vera can audit it against her checklist, then hand the significance question back to Dr. Sage.

**Consolidated protocol v2.** Data: TriviaQA rc.nocontext validation first 1000, TruthfulQA generation all 817; h-e1 prompts, max_new_tokens, and labels verbatim; answer length logged per example. Split: stratified 50/50 selection/test per dataset, seed 42, test split written and locked. Models: LLaMA-2-7b-hf (rescue stress test), Mistral-7B-v0.1, Meta-Llama-3-8B-Instruct — identical to h-e1, base/instruct status documented as scope limitation. Extraction: one greedy pass, output_hidden_states=True, per-layer lm_head(model.norm(h_ℓ)) in float32, three signals × 32 layers × mean-over-answer-tokens, per-token statistics cached for the FST-style ablation. Selection-split-only operations: degeneracy screen, (layer, signal, direction) selection, fusion fitting, direction-sign freezing. Test-split-only: all reported AUROCs with paired bootstrap n=1000. Gates: **Tier 1 (rescue, falsification gate):** LLaMA-2 CI-separated ΔAUROC > 0 vs final-layer entropy on TriviaQA + selected layer ≥ 0.60 both datasets. **Tier 2 (robustness):** all six model×dataset cells ≥ 0.60 AND no-regression clause (mistral/llama3 intermediate ≥ final − 0.02). Anchors: h-e1 final-layer references reproduced ±0.03. Diagnostics: raw-direction pattern report (Chi/familiarity flag), length-stratified AUROC on selected layers.

**Confidence stratification, as Rex demanded:** P1 moderate-high — it rests on the published intermediate>final consensus plus a mechanism (calibration suppression) that specifically explains the h-e1 failure pattern including the direction inversion; P2 genuinely uncertain — Azaria's layer shift and FEPoID's cross-dataset variability are real counter-evidence, and P2 failing is a publishable finding about deployment constraints; P3 moderate — mechanism motivates complementarity but the ΔH-KL redundancy question is open. What if we addressed the residual Chi concern by adding one sentence to scope? "Claims concern discriminative detection under standard correct/incorrect labels; the recall-vs-truthfulness causal question is explicitly out of scope but flagged for the direction-pattern diagnostic." Every weakness now has a home: quarantined, gated, diagnosed, or scoped. Now THAT's stronger than anything h-e1 shipped with.

**Key Points:**
- Complete protocol v2 consolidated: all leak-prone operations confined to selection split; all gates and anchors numeric and frozen
- Rex's three asks integrated: no-regression clause, length-stratified check, confidence stratification (P1 mod-high / P2 uncertain / P3 moderate)
- Chi confound handled via explicit scope sentence + retained direction-pattern diagnostic
- Core claim unchanged through two adversarial passes — refinements are additive, evidence of a robust spine

---

### Exchange 12

🎯 **Dr. Sage** (Scientific Contribution Assessor + Research Vision Strategist):

Taking Dr. Ally's handoff: with the protocol frozen, the question we must ask is whether the contribution SURVIVES the refinements — because scope statements and confounds acknowledged can quietly shrink a paper into a workshop note. Checking each claimed contribution against what remains: **First contribution — the empty cell is still empty and still worth filling.** Nothing in eleven exchanges surfaced prior work evaluating raw logit-lens uncertainty statistics as per-layer detection AUROC. The nearest misses remain near: [Ali et al., 2025] have the feature without the task; [Wang et al., 2026] have the task with a supervised probe and a geometric selector; HalluShift (flagged in Phase 1 for a novelty check in Phase 2B) measures internal distribution shifts but per its abstract not per-layer logit-lens statistics from a single greedy pass with per-model selection. The niche holds.

**Second — the adjudication stake sharpened.** I said in Exchange 4 this experiment arbitrates token-space versus geometry as the carrier of the intermediate-layer signal. The within-model rescue structure makes that arbitration cleaner than I initially credited: if a LLaMA-2 intermediate layer separates hallucinations where the FINAL layer of the SAME model on the SAME pass does not, the information demonstrably survives unembedding at depth ℓ but is destroyed by layer 32 — "calibration suppression" gets direct evidence, and [Kim et al., 2025]'s alignment result gets a principled boundary (their final-token trajectory measurement missed distributional information that entropy captures). That is a mechanistic finding wearing a detection-benchmark costume. **Third — this matters because the failure mode is informative too.** If Tier 1 fails, then combined with h-e1 we will have shown that NEITHER final-layer nor any intermediate-layer single-pass token-space statistic rescues LLaMA-2 — which forces the field's attention onto hidden-state geometry (FEPoID's story) and makes Chi et al.'s recall-not-truthfulness reading the leading explanation. Phase 4.5 can write that paper too. Research should open new questions: the transfer matrix (P2) and the relative-depth band (Nova's exploratory) each seed follow-ups regardless of sign.

My assessment: contribution intact, and honestly framed it is STRONGER post-refinement — a clean two-tier claim with a mechanism, an adversarial boundary, and a decision-relevant deployment measurement. This is not incremental to h-e1; it is the experiment h-e1's failure record was asking for.

**Key Points:**
- Novelty cell re-verified after refinements: feature-without-task (Entropy-Lens), task-without-this-method (FEPoID), HalluShift novelty check deferred to Phase 2B as planned
- Within-model rescue upgrades the contribution: direct evidence for/against calibration suppression, and a principled boundary on Kim et al.'s negative result
- Both gate outcomes are publishable: success = training-free architecture-robust detection; failure = token-space statistics exhausted, geometry/recall explanations promoted
- Significance verdict: genuine contribution, strengthened by the adversarial refinements

---

### Exchange 13

🔬 **Prof. Vera** (Scientific Rigor Specialist + Hypothesis Stress-Tester):

Final rigor audit. I will walk the six convergence criteria as an explicit checklist against the record, because "it feels converged" is not a standard.

**SPECIFIC:** the core claim exists in canonical Under-If-Then-Because form (Exchange 6, consolidated Exchange 11). It names models, datasets, signals, selection discipline, and two numeric gates. Pass. **MECHANISM:** unresolved-candidate-competition / calibration-suppression (Exchange 7), with three falsifiable steps — separation exists at intermediate depth; final-layer calibration suppresses it; suppression severity is architecture-dependent (worst on base LLaMA-2, mildest on RLHF-tuned llama3, which is exactly the h-e1 pass/fail pattern AND explains the direction inversion as calibration sign-flipping a residual signal). Pass. **PREDICTIONS:** P1/P2/P3 formalized with test methods, success criteria, and falsification conditions (Exchange 8), plus Rex's no-regression companion clause (Exchange 10) and Nova's explicitly ungated exploratory depth-band. Pass. **NOVELTY:** the empty cell held through two direct challenges (Exchanges 5, 12); differentiation from Entropy-Lens, FEPoID, Kim, SAPLMA, END/DoLa, and the h-e1 family is articulated per-work. Pass. **FEASIBILITY:** Prof. Pax's verdict (Exchange 9) — no unproven step in the validity chain, v1 archive as empirical existence proof of the loop; his residual concerns are empirical outcomes, not mechanisms. Pass. **OBJECTIONS:** Rex's ten distinct attacks across two waves each received a specific structural answer — vocabulary fix, within-model restructure, two-tier gate, measured-prediction demotion of transfer, scope sentence for Chi, length-stratified diagnostic, no-regression clause, confidence stratification. The record shows answers, not deflections. Pass.

One last sharpening and I am done: the hypothesis statement should carry its confidence honestly — I propose 0.72. High enough to commit Phase 2B resources; low enough to respect that P2 is genuinely uncertain and that Kim et al. found alignment in an adjacent measurement. And let the record state the null clearly: if per-layer statistics offer nothing beyond the final layer, every ΔAUROC CI on LLaMA-2 will straddle zero and Tier 1 will fail — the experiment cannot be talked past its own gate. This meets my standards.

**Key Points:**
- All six convergence criteria explicitly audited against exchange numbers — each passes on recorded evidence
- Mechanism upgraded to three falsifiable steps, and it retrodicts BOTH h-e1 anomalies (llama2 miss AND direction inversion)
- Confidence level proposed: 0.72 (P2 uncertainty and Kim adjacency priced in)
- Null hypothesis restated: all-CIs-straddle-zero on LLaMA-2 → Tier 1 fails → hypothesis dies at its own gate

---

### Exchange 14

⚙️ **Prof. Pax** (Technical & Theoretical Feasibility Analyst + Non-Triviality Assessor):

Closing feasibility statement for the record, since Prof. Vera's audit cites my verdict. Let's be precise about what has been established and what remains at risk — because a clean risk register now saves Phase 2C from rediscovering it.

**Established (fundamental level):** the mechanism requires nothing beyond a standard forward pass — no interventions, no auxiliary models, no training. The measurement (per-layer decoded-distribution statistics) is mathematically well-defined at every layer and numerically guarded (float32, ε-guards, NaN conventions). The measurement-validity threats have named mitigations: lens degeneracy → selection-split-only screen [Belrose et al., 2023 motivates it]; end-of-sequence noise → short-form answers plus cached per-token statistics for the truncation ablation [Wang et al., 2026]; selection bias with 192 candidates → split discipline and frozen direction signs [Exchange 8]. The pipeline as a whole has an empirical existence proof: v1 ran this exact extraction healthily to 87% of the first cell before an infrastructure interruption — not a scientific failure — and left a reusable cache plus environment recipe.

**Residual risks, honestly ranked.** (1) EMPIRICAL: LLaMA-2's intermediate layers may simply not carry recoverable separation — that is the hypothesis itself; if certainty existed we wouldn't need the experiment. (2) MEASUREMENT-EDGE: the degeneracy screen could reject most of LLaMA-2's early stack if raw-lens decoding is poor there; mitigation is documented (tuned-lens translators as fallback readout, at the cost of introducing trained components — which would need honest relabeling of the "training-free" claim for that variant). (3) MINOR: TruthfulQA's 817 examples give ~408 selection / ~409 test — CI widths on that split will be wide; h-e1's llama2/TruthfulQA CI [0.5014, 0.6105] shows exactly this. Predictions should not hinge on TruthfulQA-only margins, and P1's CI-separation clause correctly anchors on TriviaQA (n=1000). No fundamental barriers. Non-triviality confirmed — the 0.0014 h-e1 miss and Kim's alignment result mean a positive finding would be genuinely surprising to a well-informed skeptic, and that is the definition of an experiment worth running. Okay, this could work.

**Key Points:**
- Validity chain fully guarded; every named measurement threat has a selection-split-confined mitigation
- Risk register frozen for Phase 2C: empirical (signal absence) > measurement-edge (screen rejects llama2 layers → tuned-lens fallback with relabeled claims) > statistical (TruthfulQA CI width)
- TruthfulQA sample size argues for TriviaQA-anchored CI clauses — already reflected in P1
- Final verdict: no fundamental barriers; genuinely non-trivial; feasibility approved

---

### Exchange 15

🔍 **Prof. Rex** (Constructive Challenge Expert + Rigor Guardian):

Closing the stress-test ledger. I opened with five objections and added three asks in the second wave; the record shows eight structural answers. Vocabulary honesty — adopted ("training-free scoring, label-efficient selection," fusion quarantined). Within-model rescue — adopted, and it is the single best design decision in this discussion; the confound-cancellation is airtight. Two-tier gates with frozen numbers — adopted, including my no-regression clause. Transfer demoted to a measured prediction with honest uncertainty — adopted. Chi scoped with a live diagnostic rather than hand-waved — adopted. Length-stratified label-noise check — adopted. Now you've addressed my concerns — the ones that CAN be addressed at design time.

What remains, and must ship with the hypothesis as its permanent caveat list, because these are irreducible at this stage: **(R1) The recall shadow.** The direction-pattern diagnostic can FLAG a familiarity-like mechanism but cannot rule it out. If Tier 1 passes, the paper must not claim the signal is "truthfulness" — it is separation under standard labels, full stop. **(R2) Transfer fragility.** Azaria's within-model layer shift and FEPoID's cross-dataset variability make P2 the prediction most likely to fail. The pipeline must treat P2 failure as a finding (per-domain selection required) and not let it contaminate the P1 verdict — they are separable claims and must be reported separately. **(R3) The instruct asymmetry.** With llama3 the only instruct model, any cross-model pattern in WHERE the informative layer sits is confounded; the relative-depth exploratory (Nova's) is descriptive only, and I will object at Phase 6 if it appears with causal language. **(R4) Generalization ceiling.** Two QA datasets, three 7–8B models, one decoding regime. The architecture-robustness claim extends exactly that far; "architecture-robust" in any title needs the qualifier "across the three tested families."

Mitigation strategy on record: R1 → scope sentence plus diagnostic reporting; R2 → separable claim structure, both outcomes pre-interpreted; R3 → exploratory framing enforced; R4 → scope section in Phase 4.5 synthesis. With that ledger attached, I have no remaining design objections. The hypothesis is ready for structuring — and unlike its predecessor, it knows exactly which gate it can die at.

**Key Points:**
- All eight addressable objections resolved structurally; ledger closed
- Permanent caveats R1–R4 attached: recall shadow, transfer fragility, instruct asymmetry, generalization ceiling — each with a mitigation route
- P1 and P2 verdicts must be reported separably; P2 failure must not contaminate the rescue claim
- Final position: no remaining design objections; ready for structuring

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis occupies a verified empty cell: Entropy-Lens computes the exact feature but never for detection; FEPoID solves the task but with supervised probes and geometric selection; Kim 2025 tested a strictly narrower measurement (final-token trajectory) and its negative result is answered by scope, not ignored. The unresolved-candidate-competition mechanism plus the adjacent-layer-KL "turbulence" signal and the cross-dataset transfer matrix are each individually novel; together they make this the experiment the h-e1 failure record was asking for.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three predictions carry test methods, numeric success criteria, and explicit falsification conditions; the primary gate (CI-separated within-model improvement on LLaMA-2-7B) is inherited from the gate that killed h-e1, so the hypothesis cannot be talked past its own death condition. Selection-bias leaks (192 candidates, direction correction, degeneracy screen) are all confined to the selection split by protocol. Confidence 0.72 honestly prices P2's uncertainty.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The experiment adjudicates a live tension in the literature — whether the intermediate-layer hallucination signal survives into decoded token-space distributions or requires hidden-state geometry — and both gate outcomes are publishable. The zero-training, single-pass cost point is a genuinely different frontier position from supervised probing and multi-sample UQ, and the layer-transfer matrix is an unmeasured deployment-decisive quantity regardless of sign.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** No unproven step exists in the validity chain from forward pass to AUROC: extraction path is uniform across the three families, all numerical hazards have named guards, and the v1 archive provides an empirical existence proof (validated code, healthy run, 871/1000 cache). Residual risks are empirical (the signal may not exist on LLaMA-2) and edge-case (degeneracy screen may force the tuned-lens fallback), not fundamental. Non-triviality confirmed by the 0.0014 h-e1 miss and Kim's alignment result.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a depth-resolved rescue hypothesis: under white-box, single-greedy-pass inference on TriviaQA and TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, hallucination scores computed as per-layer logit-lens statistics — Shannon entropy, max-token probability, and adjacent-layer KL divergence of the decoded distributions, averaged over answer tokens — with (layer, signal, direction) selected per model on a held-out selection split, will detect hallucinations where the final-layer readout fails. The proposed mechanism is calibration suppression: intermediate layers preserve the separation between resolved (factual) and unresolved (hallucinated) candidate competition, and final-layer output calibration — tokenizer- and tuning-dependent — suppresses it, worst in base LLaMA-2-7B, which retrodicts both the h-e1 miss (0.5186) and its direction inversion. Success is judged by a two-tier frozen gate: Tier 1 (rescue/falsification) requires a CI-separated within-model improvement of the selected intermediate layer over the final-layer entropy baseline on LLaMA-2-7B plus AUROC ≥ 0.60 on both datasets; Tier 2 (robustness) requires all six model×dataset cells ≥ 0.60 with a no-regression clause on Mistral and LLaMA-3. Supporting predictions test cross-dataset layer transfer (P2, ±0.05 tolerance, honestly marked uncertain) and entropy-KL fusion complementarity (P3, ≥ 0.02 gain, trained combiner quarantined). The protocol reuses h-e1's prompts, labels, and reference values (±0.03 anchors) and v1's validated extraction code and partial cache, keeping every selection-sensitive operation on the selection split. The claim vocabulary is "training-free scoring with label-efficient selection," and scope explicitly excludes the recall-vs-truthfulness causal question while reporting a direction-pattern diagnostic for it.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **R1 — Recall shadow:** the diagnostic can flag but not exclude a familiarity-based mechanism (Chi et al. 2025); any positive result must claim separation under standard labels, never "truthfulness detection."
- **R2 — Transfer fragility:** Azaria's within-model layer shift and FEPoID's cross-dataset variability make P2 the most likely failure; P1 and P2 verdicts must be reported separably so a transfer failure cannot contaminate the rescue claim.
- **R3 — Instruct asymmetry:** with LLaMA-3 the only instruct model, cross-model depth patterns are confounded; the relative-depth observation stays descriptive.
- **R4 — Generalization ceiling:** claims extend to two QA datasets, three 7–8B families, greedy decoding — no further.
- **Mitigation Strategy:** R1 → scope sentence + mandatory direction-pattern reporting; R2 → separable claim structure with both P2 outcomes pre-interpreted; R3 → exploratory framing enforced through Phase 6; R4 → explicit scope section in the Phase 4.5 synthesis. Length-stratified AUROC sanity check and h-e1 baseline reproduction (±0.03) ship in the analysis plan as standing diagnostics.

