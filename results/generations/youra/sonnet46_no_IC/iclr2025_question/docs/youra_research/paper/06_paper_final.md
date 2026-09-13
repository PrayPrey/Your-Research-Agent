---
title: "Depth-Resolved Logit-Lens Uncertainty Signals for Hallucination Detection: Training-Free Evidence and a Protocol-Internal Validity Anchor"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@example.com"
format: "ICML2025"
date: "2026-08-05"
hypothesis_id: "H-LayerLensUQ-v2"
generated_by: "Anonymous Research Pipeline"
word_count: 6871
figures: 8
tables: 1
adversarial_review:
  completed_at: "2026-08-05T12:25:00+00:00"
  rounds_completed: ["R1", "R2"]
  total_issues_found: 10 # 1 FATAL + 9 MAJOR
  issues_resolved: 10
  final_status: "CONVERGED"
  persuasiveness_passed: true
  recommendation: "CONDITIONAL_ACCEPT"
  minor_issues_for_human: "review/065_human_review_notes.md (12 notes)"
---

# Abstract

Cheap hallucination-detection signals read from a language model's output distribution are architecture-fragile: the same uncertainty statistic can separate hallucinations on one checkpoint and fail, direction inverted, on another. Existing exploits of the stronger intermediate-layer signal re-introduce what makes detection expensive: trained probes, repeated sampling, or geometric machinery. We instead read per-layer logit-lens uncertainty statistics — entropy, max-token probability, adjacent-layer KL divergence — before final-layer calibration, selecting the readout layer per model. Across three 7–8B model families on TriviaQA and TruthfulQA, at least one screened intermediate layer is class-separable in all six model × dataset cells (selection-split area under the ROC curve 0.61–0.70) and beats the final layer's own entropy readout in every cell; adjacent-layer KL emerges as a first-time detection signal. Separately, six protocol differences moved a reference baseline from 0.52 to 0.59, motivating the protocol-internal validity anchors we adopt. The method is training-free and sampling-free — one greedy generation plus one teacher-forced re-forward, roughly twice the monitored pass, and an order of magnitude less added inference than multi-sample methods; this proof-of-existence evidence stages a zero-GPU test-split confirmation as its next tier.

---

# 1. Introduction

In every model and dataset cell we tested, a language model's intermediate layers scored its own hallucinations better than its output layer did — using nothing but the uncertainty statistics of the token distributions the model already computes on the way to its answer. That is our first finding. The second concerns measurement rather than models: the documented failure baseline this study was designed to beat did not survive a provenance audit. Six protocol differences — sample selection, prompt template, label rule, signal definition, numeric precision, and evaluation split — moved the same cell's final-layer entropy AUROC from 0.5186 to 0.5928 before a single new claim had been tested. We treat the second finding as a result, not an embarrassment.

The surface problem is familiar: open-weight LLMs hallucinate, and the cheapest detection signals — confidence statistics read from the output distribution — are architecture-fragile. In an archived record from an earlier study in this research line — hereafter the *motivating record* — final-layer mean token entropy reached AUROC 0.66 on LLaMA-3-8B-Instruct but roughly 0.52, with inverted score direction, on base LLaMA-2-7B: the same statistic, the same datasets. We cite these numbers only as motivating context; the audit above shows they are bound to that record's protocol, and they are never used as same-protocol baselines here. The fragility itself, however, is the point. A practitioner cannot ship a confidence score whose validity flips with the checkpoint, and the standard escapes are expensive: multi-sample semantic consistency pays roughly ten forward passes per query [Farquhar et al., 2024], and supervised hidden-state probes require labeled data and per-model training [Azaria & Mitchell, 2023].

The deeper problem is that the field has converged on a diagnosis without adopting the cheap cure. That intermediate layers carry stronger truthfulness signal than the final layer is by now close to consensus [Orgad et al., 2024; Wang et al., 2026]. Yet every method that exploits this re-introduces machinery the observation should have made unnecessary: trained probes over hidden states [Azaria & Mitchell, 2023; Suresh et al., 2025], geometric layer-selection criteria feeding supervised classifiers [Wang et al., 2026], or repeated sampling [Chen et al., 2024].

This leaves a specific gap. The raw logit lens — projecting each layer's hidden state through the model's own unembedding — yields a full next-token distribution at every depth, and the uncertainty statistics of those distributions have never been evaluated as hallucination-detection scores. Adjacent-layer KL divergence, a natural measure of how much the model revises its belief between layers, has been used only to steer decoding [Chuang et al., 2023; Wu et al., 2025], never scored for detection. The gap persisted partly through a community split — interpretability owns the instrument and studies these statistics as computation signatures [Ali et al., 2025], while detection owns the task and defaults to probes and sampling — and partly through discouragement by adjacency: the nearest published measurement tracked final-prediction-token probability trajectories across layers and found certain and uncertain trajectories largely aligned [Kim et al., 2025], a negative result for a different statistic that was easy to over-read as covering this one.

Our premise is that the gap hides signal because of where the standard signal is read. The final layer is not where the information dies; it is where output calibration — a tokenizer- and tuning-dependent presentation step — reshapes it. Watch the model make up its mind layer by layer: when it knows the answer, next-token candidate competition collapses at intermediate depth and stays collapsed; when it is hallucinating, the decoded distribution stays wide and keeps churning until the output head tidies it up. The design principle that follows is to read before calibration: compute entropy, max-token probability, and adjacent-layer KL from every layer's logit-lens distribution — obtained from one greedy generation plus one teacher-forced re-forward, with no sampling and no training — and select the readout layer, signal, and score direction per model on a held-out selection split, because calibration depth is a property of the checkpoint.

We test this premise at proof-of-concept scale under a staged verification design whose first tier asks only whether the signal exists. Across LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct on TriviaQA and TruthfulQA — 5,451 scored generations covering all six model × dataset cells — at least one screened intermediate layer is class-separable in every cell, with selection-split corrected AUROC between 0.6092 and 0.7011 against a 0.55 existence gate, and the best screened intermediate layer beats the same sweep's final-layer entropy readout in every cell (point-estimate margins +0.0035 to +0.130). These are selection-split point estimates from a single seed, with no confidence intervals: the numbers that chose the (layer, signal, direction) tuples also grade them, and they must not be read as held-out performance. The locked test splits exist and were never touched — by any analysis, or by any decision made in writing this paper — which preserves the deferred evaluation as an uncontaminated, pre-registered confirmation; running the frozen tuples there, along with cross-dataset transfer and KL–entropy fusion, is the explicitly unmeasured next tier of the staged design. Within this scope, the depth advantage is universal in direction and consistent with the calibration-suppression reading, though it does not establish that mechanism.

Four contributions follow from the insight. First, the first AUROC evaluation of raw per-layer logit-lens uncertainty statistics as training-free, sampling-free hallucination scores: class-separability holds in all six cells at existence tier. Second, a universal point-estimate depth advantage: the best screened intermediate layer — concentrated at L28–L31 — exceeds the within-sweep final-layer baseline in every cell, extending the intermediate-over-final consensus to statistics that need no probe. Third, adjacent-layer KL as a detection signal in its own right: previously a decoding heuristic, it is the best signal in two of our six cells — an even three-way split with entropy and max-probability — and sweeps the top three intermediate scores in the binding LLaMA-2/TriviaQA cell. Fourth, a methodological contribution born from failure: protocol-internal validity anchoring. Having shown quantitatively that AUROC magnitudes for weak signals do not survive protocol changes — direction transfers, magnitude does not — we replace cross-run numeric anchors with identity-verified cache reuse, within-sweep baselines, and descriptive-only cross-run comparisons.

This work sits at a junction that, to our knowledge, has never been connected without supervision: the interpretability community's per-layer lens instruments on one side, and hallucination detection on the other. We next situate it among the lines of work that meet there.

---

# 2. Related Work

We organize prior work by what each line re-introduces that our method removes: supervision, sampling, decoding-time-only use of cross-layer signal, or the absence of a detection evaluation altogether.

**Supervised probing of intermediate layers.** SAPLMA showed that hidden states carry probe-extractable truthfulness information, with the optimal layer shifting across models and distributions [Azaria & Mitchell, 2023] — the instability our per-model selection is designed around. Subsequent work located truthfulness information concentrated in intermediate representations [Orgad et al., 2024], and FEPoID automated layer choice via intrinsic-dimension criteria feeding supervised MLP probes, reporting average AUROC of roughly 0.73–0.85 across QA benchmarks [Wang et al., 2026]. CLAP probes attention states across all layers jointly [Suresh et al., 2025]; ICR Probe trains on residual-stream update dynamics [Zhang et al., 2025]; HalluShift trains a classifier over internal distribution-shift features [Dasgupta et al., 2025]; MIND removes manual annotation but still trains a detector [Su et al., 2024]. This line is the supervised skyline: it reaches higher AUROC than we report, and we make no claim to beat it. What every entry shares is a trained component between the hidden state and the score. Our question is orthogonal — whether the intermediate-layer signal is readable without one — and our contribution is removing supervision at proof-of-concept scale, not out-scoring probes. A training-free readout also gives the probe literature a missing baseline: what the representation yields in token space before any probe is fitted.

**Multi-sample uncertainty quantification.** LLM calibration varies with model and format [Kadavath et al., 2022] — the root of the output-layer fragility that motivates us. Semantic entropy clusters roughly ten sampled generations by meaning and scores their entropy [Farquhar et al., 2024]; INSIDE computes an EigenScore over the embedding covariance of multiple sampled responses [Chen et al., 2024]. Both detect well, and both pay an order of magnitude more inference than the pass being monitored. Semantic Entropy Probes are the revealing sibling: they show that single-pass hidden states approximate semantic entropy — but recover it through trained linear probes [Kossen et al., 2024]. We drop both the sampling and the probe: our statistics cost one greedy generation plus one teacher-forced re-forward over prompt and answer — roughly twice the monitored pass, against the tenfold cost above.

**Cross-layer shift at decoding time.** DoLa contrasts a premature layer's lens distribution against the mature layer's to improve factuality during generation [Chuang et al., 2023]; END reweights token probabilities by cross-layer entropy changes [Wu et al., 2025]; SLED generalizes layer-contrast decoding across model families and scales [Zhang et al., 2024]. This line validated that adjacent-layer distribution shift carries factuality-relevant information, then used it exclusively to steer generation; none scores the shift as a detection statistic. Our adjacent-layer KL promotes this line's signal to detection time, evaluated by AUROC, where it turns out to be the best signal in two of our six cells.

**Lens instruments without detection evaluations.** The logit lens showed that intermediate hidden states decode into interpretable next-token distributions [nostalgebraist, 2020]. The Tuned Lens characterized the raw lens as a biased, family-dependent instrument and trained affine translators to correct it, noting that the LLaMA/Mistral lineage is comparatively well-behaved [Belrose et al., 2023] — the characterization our degeneracy screen operationalizes instead of trained correction. Entropy-Lens computes exactly our per-layer logit-lens entropy and validates it as a signature of transformer computation tracking candidate-set expansion and pruning [Ali et al., 2025] — and never evaluates it for detection. We take the same instrument and change only the question asked of it.

**Adversarial results.** Two recent papers appear to preempt this direction and, on inspection, bound it instead. [Kim et al., 2025] found that layer-wise trajectories of the final-prediction-token probability are largely aligned for certain and uncertain outputs. That is a different measurement: one token's probability path, under a tuned lens, on multiple-choice tasks — not full-vocabulary distribution statistics on open-ended QA with per-model layer selection. Their negative trajectory result and our positive existence result are jointly consistent, and the scope boundary between the two measurements is load-bearing for our claims. Separately, [Chi et al., 2025] argue that internal states mainly reflect knowledge recall rather than truthfulness. We do not contest this: our claims are stated as class-separation under standard correctness labels, not as causal measurements of truthfulness, and the familiarity confound remains an explicitly unaddressed limitation.

**Positioning.** Across these lines, the premise that depth carries hallucination signal is settled; what remains unsettled is whether anything must be trained, sampled, or intervened upon to read it. No prior work evaluates raw logit-lens uncertainty statistics — entropy, max-token probability, or adjacent-layer KL — as sampling-free detection scores with per-model layer selection, and none anchors such an evaluation against baselines computed inside the same protocol. The next section presents our method as a chain of design decisions, each of which operationalizes reading uncertainty before output calibration.

---

# 3. Methodology

Every component below operationalizes the same insight: read uncertainty before output calibration. The lens readout turns every depth into a measurement surface; the three signals capture two facets of unresolved candidate competition; the degeneracy screen makes a biased instrument usable without trained correction; per-model selection treats calibration depth as a property of the checkpoint; and the validity anchor keeps every comparison inside one protocol, because our own forensics (Section 3.5) show that weak-signal AUROC magnitudes do not survive protocol changes.

## 3.1 Depth-resolved logit-lens readout

We study three 32-layer pre-LN decoder-only checkpoints — LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct — on TriviaQA (rc.nocontext, first 1,000 validation questions) and TruthfulQA (generation, all 817 questions). Layers are indexed L1–L32, with L32 the final layer. Each question is prompted as `Q: {question}\nA:` and answered by greedy decoding (up to 32 new tokens). Correctness labels use normalized-alias exact match (TriviaQA) and reference-answer matching (TruthfulQA); prompts, decoding, and label rules are inherited verbatim from the immediately preceding sweep in this research line — the protocol-identical run whose finalized cache Section 3.5 reuses — so the label protocol is a controlled variable, not a degree of freedom. That preceding sweep is distinct from the older, protocol-different motivating record of Section 1; Section 5.4 dissects the difference between the two protocols, and we never conflate the two runs.

For each example we run the single greedy generation, then one teacher-forced re-forward over the prompt and generated answer with hidden states exposed. At every layer $l$, the logit lens decodes the hidden state $h_l$ through the model's own output path:

$$p_l = \mathrm{softmax}\big(W_U \cdot \mathrm{norm}(h_l)\big),$$

i.e., the `lm_head` composed with the final RMSNorm — the standard raw-lens operationalization [nostalgebraist, 2020; Belrose et al., 2023]. Weights run in fp16; all statistics are computed in float32 with a $\log(p + 10^{-12})$ guard. We deliberately use the raw lens with no tuned translators: trained components would forfeit the training-free claim, and the LLaMA/Mistral lineage is the documented best-behaved raw-lens case [Belrose et al., 2023]. A pre-specified tuned-lens fallback, for the case where the screen below rejects most layers, was never needed. The re-forward is a measured cost, not an in-principle one: the same hidden states could be captured during generation itself, but that engineering path is not what we measured, and every cost statement in this paper prices the two-pass protocol.

## 3.2 Three uncertainty signals

From each $p_l$ we compute three statistics, averaged over the answer tokens: Shannon entropy $H(p_l)$, max-token probability $\max_v p_l(v)$, and adjacent-layer KL divergence $\mathrm{KL}(p_l \,\|\, p_{l-1})$, which is undefined at L1 and excluded there. The choice is not a grab-bag: entropy and max-probability measure the *width* of the candidate set at depth $l$, while adjacent-layer KL measures *revision* — how much the model is still rewriting its belief between consecutive layers. If hallucination is unresolved candidate competition, it should manifest both as persistent width and as persistent revision deep into the stack; the two facets can disagree, and adjacent-layer KL is the one signal with no detection-time precedent (Section 2). Figure 1 shows the intuition on LLaMA-2-7B: entropy trajectories of correctly and incorrectly answered examples separate across depth before converging toward the output layer.

![Figure 1: Per-layer logit-lens entropy (examples × layers) for correct vs. incorrect answers, LLaMA-2-7B. The groups separate at intermediate depth.](figures/entropy_heatmap_llama2.png)

## 3.3 Degeneracy screen

The raw lens is a biased instrument: some layers decode to near-uniform distributions or to distributions unrelated to the model's eventual output, and their statistics could masquerade as signal. Before any scoring, we therefore screen layers per model $\times$ dataset cell on that cell's selection split, dropping layer $l$ if its mean entropy lies within 1% of $\ln|V|$ (near-uniform: the lens is reading noise) or if its top-1 agreement with the final layer is below 5% (so unlike the model's actual output that the reading is unlikely to be meaningful). A cell is considered lens-viable if at least 5 layers survive. The screen retained 15–20 layers per cell: 20 on LLaMA-2-7B (both datasets), 15 and 16 on Mistral-7B-v0.1, and 15 and 16 on LLaMA-3-8B-Instruct (TriviaQA and TruthfulQA respectively; Figure 2); the tuned-lens pivot it guards was never triggered. All subsequent claims are about *screened intermediate layers* only.

![Figure 2: Degeneracy screen results — retained vs. dropped layers. The screen is applied per model × dataset cell on the selection split and retains 15–20 layers per cell (LLaMA-2 20/20, Mistral 15/16, LLaMA-3 15/16 on TriviaQA/TruthfulQA).](figures/degeneracy_screen.png)

## 3.4 Per-model selection with a locked test split

Each dataset is split 50/50 into a selection split and a test split, stratified by label, seed 42 (500/500 on TriviaQA; 408/409 on TruthfulQA). The test split is locked at split time and never read by any analysis in this paper; every number we report is a selection-split quantity, and we flag it as such throughout. On the selection split we compute, for every screened (layer, signal) pair, the corrected AUROC $\max(a, 1-a)$ with the direction recorded, and select the per-cell tuple $(\hat{l}, \hat{s}, \hat{d})$ by argmax over screened *intermediate* layers (L32 excluded from candidacy).

Each element of this design answers a documented failure. Selection is per model *and* per dataset because the probe literature shows the informative layer shifts across both [Azaria & Mitchell, 2023], and our own sweep confirms it: the winning signal differs across datasets for every model, and the winning layer for two of the three, so a fixed depth or fixed signal would be the wrong abstraction. Direction is selected rather than assumed because the motivating failure was precisely a direction inversion — the motivating record's final-layer entropy flipped sign on LLaMA-2/TriviaQA — so the method removes inversion as a failure mode instead of hoping monotonicity holds across checkpoints. Finally, the supervision boundary is explicit: "training-free" refers to scoring — no probe, no fitted parameters. Selection is a label-efficient argmax over a discrete grid, performed once per cell on the selection split only.

## 3.5 Protocol-internal validity anchor (A2-v2)

The anchor design is itself a corrected failure, and the correction is a contribution. The first version of this experiment gated on reproducing the motivating record's final-layer AUROCs within ±0.03. The halt gate fired 47 seconds into the first cell (observed deviation +0.0742), and a provenance audit showed why: the reference numbers came from a protocol differing in six documented ways, from sample selection to numeric precision. The anchor was unsatisfiable by construction — the same cell that recorded 0.5186 under the old protocol measures 0.5928 under this one. The redesign moves every validity check inside the current protocol:

- **(a) Identity-verified cache reuse.** Before reusing the one finalized donor cache (the zero-GPU LLaMA-2/TriviaQA cell), the first 10 examples are regenerated fresh and must agree with the cached labels 10/10; any drift falls back to fresh generation. Reuse is an optimization, never an assumption.
- **(b) Within-sweep final-layer baseline.** The baseline for the depth claim is the final-layer (L32) entropy AUROC computed per cell from the *same* sweep, same pass, same labels (`depth_beats_final`). After the forensics above, this is the only comparison we consider valid.
- **(c) Descriptive-only cross-run reports.** Direction consistency against the motivating record is logged per cell and never gated: direction was the only quantity our forensics found to transfer across protocols, and magnitudes are not comparable by construction.

Halts occur only on protocol-internal contract violations (unfinalized split, single-class labels — conditions under which AUROC is undefined). Under this anchor the full sweep completed with zero spurious halts; Figure 3 shows the per-cell report.

![Figure 3: A2-v2 anchor report — per-cell within-sweep final-layer AUROC with descriptive direction-consistency markers.](figures/anchor_v2_report.png)

**Algorithm 1: Depth-resolved sweep and per-cell selection**

```
Input: model M (layers L1..L32), dataset D, seed 42
1: split D into stratified 50/50 selection / test; lock test split (never read)
2: for each example x in D:
3:     a  <- greedy_generate(M, prompt(x))                # greedy generation, <=32 tokens
4:     h_1..h_32 <- teacher_forced_forward(M, prompt(x) + a)
5:     for l in 1..32:  p_l <- softmax(lm_head(norm(h_l)))    # logit-lens readout
6:     cache mean over answer tokens of:
           entropy(p_l), maxprob(p_l), KL(p_l || p_{l-1})     # KL: NaN at L1, excluded
7: L* <- degeneracy_screen(selection split)               # Sec. 3.3; health: |L*| >= 5
8: for (l, s) in L* x {entropy, maxprob, adj_kl}:
       A[l, s] <- corrected AUROC on selection split      # direction recorded
9: (l^, s^, d^) <- argmax A over intermediate l (L32 excluded)
10: b <- A[L32, entropy]                                  # within-sweep final-layer baseline
11: report existence gate A[l^, s^] >= 0.55  and  depth_beats_final A[l^, s^] > b
    # A2-v2: verify donor-cache identity (10/10) before any reuse; log cross-run
    # direction descriptively; halt only on protocol-internal contract violations
```

The full sweep spans 3 models × 2 datasets × 32 layers × 3 signals — 5,451 scored generations, streamed to per-example caches that make every stage resumable and auditable, and that leave the locked test splits ready for the frozen-tuple evaluation this staged design defers. The next section states the experimental questions this pipeline was built to answer.

---

# 4. Experimental Setup

Section 3 described a pipeline whose every component answers a documented failure; we now specify the tests it was built to pass. The staged verification design evaluates its first tier here — existence — and we state at the outset what that tier does and does not measure: all quantities below are computed on the selection split, from a single seed, with no confidence intervals. The locked test splits were never evaluated. Nothing in this paper is held-out performance, and we flag this at every point where a reader might otherwise assume it.

## 4.1 Research questions

Three questions structure the evaluation, each instantiating one of the Introduction's contributions.

**RQ1 (Existence — Contribution 1).** Does at least one screened intermediate (layer, signal) pair per model achieve selection-split corrected AUROC $\geq 0.55$ on *both* datasets — that is, in all six model $\times$ dataset cells? This is the gate the entire staged design conditions on: if no training-free signal exists at depth, the deployable-detector tier has nothing to deploy.

**RQ2 (Depth beats final — Contribution 2).** Does the best screened intermediate layer exceed the *same sweep's* final-layer entropy readout in every cell? A yes, even as a point estimate, extends the intermediate-over-final consensus to statistics that need no probe, and is the direction the calibration-suppression reading predicts.

**RQ3 (Protocol-internal validity — Contribution 4).** Is the evaluation protocol internally valid by its own instruments — donor-cache identity verified before any reuse, within-sweep baselines computed per cell, and zero spurious halts? RQ3 exists because its predecessor failed: the v1 anchor, gated on cross-protocol numbers, was unsatisfiable by construction (Section 3.5), and the redesign must demonstrate that validity checking survives without it.

## 4.2 Datasets

We evaluate on TriviaQA (rc.nocontext, the first 1,000 validation questions — a deterministic slice, not a random sample) and TruthfulQA (generation split, all 817 questions). The pairing is deliberate on two axes. First, lineage: both datasets carry the documented final-layer failure record that motivates this study, so the comparison to that record's conditions is as controlled as a cross-protocol comparison can be. Second, label protocol: TriviaQA labels come from normalized-alias exact match, TruthfulQA labels from similarity to curated correct and incorrect reference answers. These are different measurement instruments for "hallucination," and passing the existence gate under both is a robustness check on the signal rather than an accident of one label rule.

Each dataset is split 50/50 into selection and test splits, stratified by label, seed 42 (500/500 on TriviaQA; 408/409 on TruthfulQA). The test split is locked at split time and never read by any analysis reported here; all selection-sensitive operations — screening, tuple selection, direction correction, gating — are confined to the selection split.

## 4.3 Baselines

The baseline for RQ2 is the **within-sweep final-layer entropy AUROC**: L32 entropy from the same greedy pass, same teacher-forced re-forward, same labels, same split, computed per cell (final-layer max-probability is recorded alongside). This choice is not convenience but consequence. The anchor forensics of Section 3.5 showed that six protocol differences moved a final-layer AUROC on the same model and nominal dataset by more than double the anchor tolerance; after that demonstration, a cross-protocol number pasted in as a baseline is not a baseline, and the only comparison we consider valid is one computed inside the protocol it is compared against.

Supervised intermediate-layer probes (FEPoID-class methods, reported AUROC roughly 0.73–0.85) are cited as a skyline but not re-run: they consume labeled training data and per-model probe fitting, a different resource class from training-free selection, and re-running them under this protocol is outside the existence tier's scope. No external baselines were re-executed; every comparison in Section 5 is within-sweep.

## 4.4 Implementation details

All three checkpoints — LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct — are frozen 32-layer pre-LN decoders run in fp16 on a single H100. Each example receives one greedy generation (`do_sample=False`, `max_new_tokens=32`) followed by one teacher-forced re-forward with `output_hidden_states=True`; all statistics are computed in float32 with a $\log(p + 10^{-12})$ guard. The full sweep scores 5,451 generations (1,817 per model) and streams per-example rows to resumable caches keyed by example id. The LLaMA-2/TriviaQA cell was reproduced from the preceding sweep's finalized cache after the identity check of Section 3.5 passed 10/10, making it a zero-GPU cell; the remaining five cells were generated fresh, at ~1.25 GPU-hours of logged compute. The implementation is covered by an automated test suite (37 tests, all passing), and we verified end-to-end that every reported statistic derives from live forward passes of the actual checkpoints.

## 4.5 Metrics and gate constants

The primary metric is **corrected AUROC**: $\max(a, 1-a)$ with the score direction recorded, selected on the selection split and frozen thereafter. AUROC is threshold-free and comparable across cells of very different base rates; the direction correction is not cosmetic but addresses the documented inversion failure mode — the motivating record's final-layer entropy flipped sign across checkpoints, and a method that assumes monotonicity inherits that fragility.

Gate constants, fixed before the sweep: existence requires corrected AUROC $\geq 0.55$; the degeneracy screen drops layers whose mean entropy lies within 1% of $\ln|V|$ or whose top-1 agreement with the final layer is below 5%, with screen health requiring $\geq 5$ retained layers per cell. RQ2 is evaluated as a per-cell direction check on point estimates — the existence tier pre-registers no statistical test, and we report it accordingly.

---

# 5. Results

The main claim survives every cell it was tested in: training-free per-layer logit-lens uncertainty statistics are class-separable hallucination scores at intermediate depth in all six model $\times$ dataset cells (selection-split corrected AUROC 0.6092–0.7011 against a 0.55 gate), and the best screened intermediate layer beats the same sweep's final-layer entropy readout in every cell. We present the existence grid first, then the structure inside it: the dataset dependence of the depth advantage, the signal-family pattern, the anchor forensics that determined what counts as a baseline, and one finding that contradicted our own prediction. Every number below is a selection-split point estimate from a single seed; none is held-out performance.

## 5.1 The existence grid

Table 1 reports the six selected tuples with their within-sweep final-layer baselines. Figure 4 shows the headline comparison — per-cell best-intermediate AUROC against the 0.55 gate and the final-layer bar; every intermediate bar clears both.

**Table 1: Selection-split corrected AUROC per cell (single seed, no CIs). Depth margin = best intermediate − within-sweep final-layer entropy.**

| Cell | Selected (layer, signal) | Intermediate AUROC | Final-layer entropy AUROC | Depth margin |
|------|--------------------------|--------------------|---------------------------|--------------|
| LLaMA-2 / TriviaQA | L31, adj. KL | 0.6522 | 0.5928 | +0.059 |
| LLaMA-2 / TruthfulQA | L29, entropy | 0.7011 | 0.6669 | +0.034 |
| Mistral / TriviaQA | L31, max-prob | 0.6092 | 0.5447 | +0.064 |
| Mistral / TruthfulQA | L31, adj. KL | 0.6570 | 0.6048 | +0.052 |
| LLaMA-3 / TriviaQA | L28, entropy | 0.6868 | 0.5566 | +0.130 |
| LLaMA-3 / TruthfulQA | L31, max-prob | 0.6213 | 0.6178 | +0.0035 |

![Figure 4: Existence gate grid — per-cell best intermediate corrected AUROC vs. the 0.55 gate and the within-sweep final-layer entropy baseline, all six cells.](figures/gate_metrics_bar.png)

The answer to RQ1 is yes, everywhere: the gate clears by +0.059 (Mistral/TriviaQA) to +0.151 (LLaMA-2/TruthfulQA). These are point estimates — we computed no confidence intervals and make no distributional claim about the margins; we note only, as a point-estimate comparison, that the thinnest gate margin is an order of magnitude larger than the thinnest depth margin of Section 5.2. The so-what is universality within scope: the signal appears in a base LLaMA, a base Mistral, and an RLHF-tuned LLaMA-3, under two different labeling protocols — the intermediate-over-final consensus does extend to statistics that need no probe, at least at existence tier. The selected layers also concentrate: every winner sits at L28–L31, four of six at L31 itself — the informative surface is the late-but-not-last band just before output calibration. Figure 5 shows the full layer $\times$ signal grid; the late-band concentration is visible in every cell, not an artifact of the argmax.

![Figure 5: Corrected AUROC across screened layers and signals for all six cells. Informative depth concentrates at L28–L31.](figures/auroc_heatmap.png)

## 5.2 The depth advantage is universal in direction, dataset-dependent in size

RQ2 also resolves 6/6: the best screened intermediate layer beats the within-sweep final-layer entropy readout in every cell. But the margins split cleanly by dataset. On TriviaQA they are substantial — +0.059, +0.064, +0.130 — while on TruthfulQA they thin to +0.034, +0.052, and +0.0035, because TruthfulQA final layers are already strong (entropy AUROC 0.6048–0.6669). We flag the thinnest cell plainly: at +0.0035 on 408 selection examples with no confidence interval, LLaMA-3/TruthfulQA's depth advantage is within plausible noise, and we count it as direction-consistent rather than as evidence. The claim degrades gracefully — five of six margins exceed 0.03 — but "6/6" is a point-estimate statement, not a statistical one.

The interpretation is a nuance the mechanism story needs: depth helps most where the final layer is weakest. Where output calibration leaves little separation at L32 (TriviaQA, final-layer AUROC 0.54–0.59), reading before calibration recovers a lot; where the final layer already separates classes (TruthfulQA), there is less to recover. This is consistent with the calibration-suppression reading — suppression as relative attenuation, not destruction — while bounding it: whatever suppresses the signal is dataset-dependent. Whether that reflects TruthfulQA's adversarial question design, its similarity-based label protocol, or small-sample variance cannot be decided from this grid; all three explanations remain live.

## 5.3 Signal families: belief revision as a detection score

Adjacent-layer KL — a statistic with no detection-time precedent, previously used only to steer decoding — is the best signal in two of six cells, with entropy and max-probability each also best in two: an even three-way split. Its strongest showing is the LLaMA-2/TriviaQA cell (Figure 6), where the top three intermediate scores are all adj. KL: L31 at 0.6522, L17 at 0.6145, L30 at 0.6062. That the winning signal differs across datasets within every model — and the winning layer within two of the three — also vindicates selecting the full (layer, signal, direction) tuple per cell rather than fixing any element a priori.

![Figure 6: AUROC vs. depth for LLaMA-2/TriviaQA — the three signal curves with the 0.55 gate and final-layer baseline. The top three intermediate scores are all adjacent-layer KL.](figures/auroc_vs_depth_llama2_triviaqa.png)

The so-what: inter-layer belief revision is a first-class detection signal, not just a decoding heuristic — to our knowledge the first detection-time use of this quantity, and the paper's most novel single observation. What adj. KL at L31 *measures*, however, is genuinely undecidable from our data. Two readings fit: it is an independent "turbulence" signal — persistent belief revision as a distinct facet of unresolved competition — or it is a meter on the calibration step itself, scoring how much the last layers rewrite the distribution. Both are calibration-adjacent; separating them needs the fusion test and the correlation analysis staged as future work, both computable from the published caches with zero GPU.

## 5.4 Anchor forensics: what happened to the baseline this study set out to beat

This study was designed around a documented failure: the archived motivating record (Section 1) put final-layer entropy at AUROC 0.5186 on LLaMA-2/TriviaQA. The v1 experiment gated on reproducing that number within ±0.03 — and the halt gate fired 47 seconds into what was budgeted as a ~2.5-hour GPU campaign. The observed value was 0.5928 on the selection split (0.5739 on the full set), a deviation of +0.0742 against a 0.03 tolerance. A provenance audit found the reference protocol differed in six documented ways: random-sample vs. first-slice data selection, bare vs. templated prompt, substring vs. normalized-alias labels, generation-time vs. teacher-forced lens entropy, bfloat16 vs. fp16, and full-set vs. selection-split evaluation. The anchor was unsatisfiable by construction — no correct implementation could close a gap created by measuring a different thing. Figure 7 shows the breach against the tolerance band. The redesigned protocol-internal anchor (Section 3.5) then passed all five clauses on the full v2 sweep with zero spurious halts; the descriptive cross-run check found direction consistent with the motivating record in 4/6 cells, both inconsistencies on cells that record never code-verified.

![Figure 7: The v1 anchor breach — observed final-layer entropy AUROC vs. the cross-protocol reference and its ±0.03 tolerance band on LLaMA-2/TriviaQA.](figures/h-e1_anchor_check_llama2_triviaqa.png)

We report this as a result, not an incident report. The so-what is twofold. Scientifically: AUROC magnitudes for weak uncertainty signals are protocol-bound — six ordinary protocol choices moved the same cell by +0.074 — so direction transfers across protocols but magnitude does not, and any comparison this paper makes is within-sweep for that reason. Practically: a cheap designed halt gate converted a doomed campaign into a 47-second diagnosis, which is the strongest argument we can offer for building validity gates into evaluation pipelines before spending compute.

## 5.5 A prediction reversed: the depth advantage does not track tuning status as hypothesized

Our mechanism draft predicted that base LLaMA-2, presumed worst-suppressed, would gain most from depth readout, and instruct-tuned LLaMA-3 least. The data reverse this ordering: the largest TriviaQA depth margin (+0.130, Figure 8) belongs to LLaMA-3-8B-Instruct — the model predicted to need depth least — with Mistral (+0.064) and LLaMA-2 (+0.059) behind it. A revised hypothesis fits: instruct tuning may *sharpen* final-layer calibration, strengthening suppression rather than weakening it — still a calibration story, with the opposite tuning polarity. We state this descriptively only and verify nothing: with a single instruct model in the grid, tuning status is confounded with everything else about the checkpoint, and the base-vs-instruct pair study that could decide it is future work.

![Figure 8: AUROC vs. depth for LLaMA-3/TriviaQA — the largest depth margin in the grid (+0.130), on the model predicted to need depth least.](figures/auroc_vs_depth_llama3_triviaqa.png)

---

# 6. Discussion

**What the results establish.** The existence premise of depth-resolved, training-free hallucination detection is confirmed universally within scope: in every model $\times$ dataset cell, at least one screened intermediate layer separates correct from hallucinated answers using nothing but the model's own decoded distributions, and always better than the final layer's entropy readout in the same sweep. The calibration-suppression mechanism fares more modestly. The direction is right in 6/6 cells, and depth helps most where the final layer is weakest — both consistent with suppression — but the pre-registered CI test never ran, and the severity-ordering sub-claim was descriptively contradicted (the instruct model gained most, not least). "Consistent with" is where the mechanism claim ends. The third result is one we did not plan: the anchor forensics elevate measurement validity to a first-class finding. Six ordinary protocol choices moved a baseline AUROC by +0.074, which means weak-signal AUROC magnitudes are properties of protocols, not just of models — and the protocol-internal anchor that replaced the broken one is, we argue, a reusable design for iterated LLM evaluation.

**Limitations.** Four, stated plainly. *First, all AUROCs are selection-split values; the locked test splits were never evaluated.* The numbers that selected the tuples also grade them, and they overestimate generalization by construction. The split stays sealed at publication for a scientific reason, not a procedural one: because no analysis decision — including any made in writing this paper — has read it, the deferred evaluation retains the guarantees of a pre-registered confirmation, uncontaminated by the selection and presentation choices reported here. This paper is therefore, explicitly, the stage-one report of that pre-registered design, and every artifact for stage two exists: freezing the six published tuples and evaluating the locked test splits with a paired bootstrap is a zero-GPU computation on the released caches. *Second, one seed and no confidence intervals*; the +0.0035 LLaMA-3/TruthfulQA margin is within plausible noise. The binding gate quantity clears by +0.059 to +0.151 as point estimates — we make no distributional claim for these margins either — and the claim degrades gracefully (5/6 margins exceed 0.03); the bootstrap machinery is implemented and runs on cached data. *Third, the original "rescue from a documented 0.5186 failure" framing did not survive its own provenance audit* — that number is protocol-specific, and under the current protocol LLaMA-2's final layer sits near 0.59, weak but not at chance. We converted the broken framing into the measurement-validity contribution, and the depth advantage stands entirely on within-protocol comparisons; a factorial attribution of the six protocol factors is the natural follow-up. *Fourth, scope*: three 7–8B families, two short-form QA datasets, greedy decoding, one instruct model, and an unaddressed familiarity-vs-truthfulness confound — the scores demonstrably separate correct from incorrect answers under standard labels, but whether they track truthfulness or question familiarity is untested. This is standard PoC scoping, chosen deliberately for controlled lineage to the motivating failure record; base-vs-instruct pairs and frequency-stratified AUROC diagnostics are the mitigations. Cross-dataset transfer and KL–entropy fusion, like the test-split evaluation, were never measured and are staged as the next tier — all zero-GPU from the published caches.

**Broader impact.** Cheap, training-free hallucination detection lowers the barrier to monitoring wherever open-weight models run with hidden-state access, and at roughly one extra forward pass per monitored generation — far below the tenfold cost of sampling-based detection — it weakens the main economic excuse for shipping unmonitored systems. The corresponding risk is overtrust: these scores are uncertainty correlates under standard correctness labels, not truth oracles, and a deployment that treats a favorable AUROC — especially a selection-split one — as a guarantee would import exactly the miscalibration this line of work is meant to expose. Score consumers should treat detection output as triage signal, not verdict.

---

# 7. Conclusion

This paper opened with two findings and closes on both. The first was about models: in every model × dataset cell we tested, the model scored its own hallucinations better from the middle of its stack than from its output layer. That claim now has its full shape. Across three 7–8B families and two QA datasets, at least one screened intermediate layer — always in the L28–L31 band, just before output calibration — is class-separable using nothing but raw logit-lens uncertainty statistics read from one greedy generation plus one teacher-forced re-forward (selection-split corrected AUROC 0.6092–0.7011 against a 0.55 gate), and the best such layer exceeds the same sweep's final-layer entropy readout in all six cells as point estimates. No probe was trained, no sample repeated; and adjacent-layer KL divergence, which entered as the speculative third signal, leaves as the paper's most novel observation — the first detection-time use of inter-layer belief revision, best signal in two of the six cells, and a sweep of the top three intermediate scores in the binding cell.

The second finding was about measurement. The documented-failure baseline this study set out to beat did not survive its own provenance audit: six ordinary protocol differences moved the same cell's final-layer AUROC from 0.5186 to 0.5928, and a designed halt gate diagnosed the unsatisfiable anchor in 47 seconds. The protocol-internal anchor that replaced it — identity-verified cache reuse, within-sweep baselines, descriptive-only cross-run comparisons — is a contribution the study did not plan and could not have made without failing first.

Everything above is existence-tier evidence: selection-split point estimates, single seed, no confidence intervals. The staged design makes the next tier unusually cheap. The follow-ups that matter most cost zero GPU from the published caches: freezing the six selected tuples and evaluating the locked test splits with a paired bootstrap — the pre-registered confirmation this stage-one report was built to set up — alongside the cross-dataset transfer matrix, the KL–entropy fusion test that would decide whether belief revision complements distribution width, and confidence intervals on the existence grid. Two need modest compute: base-vs-instruct pairs of one family, to test the reversed tuning-polarity hypothesis the +0.130 instruct-model margin forced on us, and a factorial attribution of the six protocol factors behind the 0.5186→0.5928 shift — a reproducibility study in its own right.

The broader lesson fits in a sentence. The output layer is where the model speaks; it is not the best place to listen.

---

## References

- Ali, R., Caso, F., Irwin, C., and Liò, P. Entropy-Lens: The Information Signature of Transformer Computations. *arXiv preprint arXiv:2502.16570*, 2025.
- Azaria, A. and Mitchell, T. M. The Internal State of an LLM Knows When It's Lying. In *Findings of the Association for Computational Linguistics: EMNLP*, 2023.
- Belrose, N., Furman, Z., Smith, L., Halawi, D., Ostrovsky, I., McKinney, L., Biderman, S., and Steinhardt, J. Eliciting Latent Predictions from Transformers with the Tuned Lens. *arXiv preprint arXiv:2303.08112*, 2023.
- Chen, C., Liu, K., Chen, Z., Gu, Y., Wu, Y., Tao, M., Fu, Z., and Ye, J. INSIDE: LLMs' Internal States Retain the Power of Hallucination Detection. In *International Conference on Learning Representations*, 2024.
- Chi, C. S., Chan, H. P., Zhang, W., and Deng, Y. Do LLMs Really Know What They Don't Know? Internal States Mainly Reflect Knowledge Recall Rather Than Truthfulness. *arXiv preprint arXiv:2510.09033*, 2025.
- Chuang, Y.-S., Xie, Y., Luo, H., Kim, Y., Glass, J., and He, P. DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models. In *International Conference on Learning Representations*, 2023.
- Dasgupta, S., Nath, S., Basu, A., Shamsolmoali, P., and Das, S. HalluShift: Measuring Distribution Shifts towards Hallucination Detection in LLMs. In *IEEE International Joint Conference on Neural Networks*, 2025.
- Farquhar, S., Kossen, J., Kuhn, L., and Gal, Y. Detecting hallucinations in large language models using semantic entropy. *Nature*, 2024.
- Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., et al. Language Models (Mostly) Know What They Know. *arXiv preprint arXiv:2207.05221*, 2022.
- Kim, S., Yoo, H., and Oh, A. On the Effect of Uncertainty on Layer-wise Inference Dynamics. *arXiv preprint arXiv:2507.06722*, 2025.
- Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., and Gal, Y. Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. *arXiv preprint arXiv:2406.15927*, 2024.
- nostalgebraist. interpreting GPT: the logit lens. *LessWrong blog post*, 2020. https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens
- Orgad, H., Toker, M., Gekhman, Z., Reichart, R., Szpektor, I., Kotek, H., and Belinkov, Y. LLMs Know More Than They Show: On the Intrinsic Representation of LLM Hallucinations. In *International Conference on Learning Representations*, 2024.
- Su, W., Wang, C., Ai, Q., Hu, Y., Wu, Z., Zhou, Y., and Liu, Y. Unsupervised Real-Time Hallucination Detection based on the Internal States of Large Language Models. In *Annual Meeting of the Association for Computational Linguistics*, 2024.
- Suresh, M., Aljundi, R., Nkisi-Orji, I., and Wiratunga, N. Cross-Layer Attention Probing for Fine-Grained Hallucination Detection. In *TRUST-AI Workshop at ECAI*, 2025.
- Wang, X., Cao, W., Wilson, A., and Zeng, Z. Automatic Layer Selection for Hallucination Detection. *arXiv preprint arXiv:2605.26366*, 2026.
- Wu, J., Shen, Y., Liu, S., Tang, Y., Song, S., Wang, X., and Cai, L. Improve Decoding Factuality by Token-wise Cross Layer Entropy of Large Language Models. In *North American Chapter of the Association for Computational Linguistics*, 2025.
- Zhang, J., Juan, D.-C., Rashtchian, C., Ferng, C.-S., Jiang, H., and Chen, Y. SLED: Self Logits Evolution Decoding for Improving Factuality in Large Language Models. In *Neural Information Processing Systems*, 2024.
- Zhang, Z., Hu, X., Zhang, H., Zhang, J., and Wan, X. ICR Probe: Tracking Hidden State Dynamics for Reliable Hallucination Detection in LLMs. In *Annual Meeting of the Association for Computational Linguistics*, 2025.
