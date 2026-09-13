# Phase 2A Discussion Log
**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (Independent Controller Ablation — no orchestrate_exchange.py)  
**Execution Mode:** UNATTENDED  
**Date:** 2026-08-31  

---

## Briefing

### Selected Gap
**Gap ID:** gap1  
**Priority:** HIGH + PRIMARY (Critical)  
**Title:** Mechanistic Characterization of SGD-Driven Temporal Feature Learning Order

### Gap Description
The simplicity bias of neural networks trained with SGD/ERM is well-documented (Shah et al. 2020, Geirhos et al. 2020, Arpit et al. 2017). It is observed empirically that simpler/spurious features are learned earlier than core features. However, existing explanations remain at the level of "SGD has spectral bias toward low-frequency components" (Rahaman et al. 2019) or statistical characterizations of feature complexity, without a fine-grained mechanistic account of *how* gradient dynamics during specific training phases produce this ordering on realistic spurious correlation benchmarks.

**Missing Piece:** A mechanistic, gradient-level account of how the interplay between batch statistics, learning rate schedule, and loss landscape curvature determines the temporal ordering of spurious vs. core feature acquisition on benchmarks like Waterbirds and CelebA. Specifically: (a) what measurable gradient quantities predict which features are learned in which training epoch, and (b) whether intervening on these quantities can alter the ordering without requiring group labels.

### Research Papers Available
- P1: Geirhos et al. 2020 — Shortcut Learning in Deep Neural Networks (2004.07780)
- P2: Shah et al. 2020 — The Pitfalls of Simplicity Bias (2006.09081)
- P3: Arpit et al. 2017 — A Closer Look at Memorization (1706.05394)
- P4: Sagawa et al. 2020 — Distributionally Robust Neural Networks (1911.08731)
- P5: Rahaman et al. 2019 — On the Spectral Bias of Neural Networks (1806.08734)

### Feasibility Constraints (Pipeline-Enforced)
- ✅ Test on existing benchmarks only: Waterbirds, CelebA, MultiNLI, WILDS
- ❌ No new benchmarks or rubrics
- ❌ No synthetic/generated data
- ❌ No human annotation or evaluation
- ✅ Existing real datasets + existing benchmarks only

### Previous Failure / Routing Context
*None — First Phase 2A execution. No prior hypotheses have been tested.*

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is genuinely exciting — and I think we've been asking the wrong question. Everyone has been asking "do DNNs learn spurious features first?" (yes, they do) but nobody has asked "what is the *exact gradient-level signature* that distinguishes the spurious-feature-learning phase from the core-feature-learning phase, measured in real time during training?" 

Let me propose three unconventional angles:

**Angle A: Gradient Alignment as a Temporal Probe.** If batch A predominantly contains spurious-majority samples (e.g., landbirds on land in Waterbirds) and batch B contains spurious-minority samples (landbirds on water), then during the early training phase when the model is learning the spurious correlation, the gradients from batch A and batch B should be *misaligned* (they push in different directions — batch A reinforces the background feature, batch B contradicts it). As the model transitions to learning the core feature (bird morphology), gradient alignment between these two batch types should *increase*, because both batches agree on the bird shape signal. This is measurable without group labels at test time — you just need to track cosine similarity between mini-batch gradient vectors partitioned by spurious feature prevalence.

**Angle B: Hessian Eigenspectrum Shifts.** The loss landscape during spurious-feature learning should exhibit a characteristic sharpness profile — specifically, the dominant Hessian eigenvectors during early training should align with spurious feature directions in activation space. As learning transitions, these eigenvectors should rotate toward core feature directions. The spectral bias of Rahaman et al. 2019 predicts this, but it's never been measured directly on Waterbirds/CelebA.

**Angle C: Per-Sample Gradient Norm Dynamics.** Spurious-majority samples (which are easy for the spurious-feature detector) should exhibit rapidly decreasing gradient norms as the spurious feature is learned. Spurious-minority samples (which the spurious feature cannot explain) should maintain high gradient norms longer. This differential gradient norm trajectory is both a *diagnostic* (it identifies the transition point) and potentially an *intervention target* (upweight high-gradient-norm samples).

I'm most excited about Angle A — it's directly measurable on existing benchmarks, requires no new data, and the gradient alignment signal could become a drop-in diagnostic for any training run. The question for the group: which of these provides the most tractable mechanistic test?

**Key Points:**
- Gradient alignment between spurious-majority and spurious-minority batches as temporal probe of feature learning order
- Hessian eigenvector rotation as loss landscape signature of feature transition
- Per-sample gradient norm differential as diagnostic + intervention target

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framework is intriguing, but I need to push hard on operationalization before we proceed — the history of spurious correlation research is littered with elegant diagnostics that fail on realistic benchmarks.

**On Angle A (Gradient Alignment):** The core issue is that Waterbirds does not have a clean "spurious-majority batch" vs. "spurious-minority batch" split available without group labels at training time. To partition batches by spurious feature prevalence, you need to know which samples are spurious-majority vs. spurious-minority — which is exactly what group annotation provides. So Angle A as stated either (a) requires group labels to partition batches, which defeats the annotation-free constraint, or (b) must use a proxy partition based on some observable training signal. What proxy? This is the crux.

A falsifiable version: if we use the ERM model's own early predictions to partition batches (samples the model gets right early = spurious-majority, samples the model struggles with = spurious-minority), then measure gradient alignment between these proxy-partitioned batches across epochs — does alignment trajectory track the ERM model's eventual worst-group accuracy? This is testable on Waterbirds and CelebA using existing code (kohpangwei/group_DRO repository).

**On the Feasibility Constraint:** The pipeline has explicitly excluded synthetic data and human evaluation. Both Angles B and C are feasible under this constraint — CelebA and Waterbirds have existing group annotations that can serve as *evaluation ground truth* even if not used during training. We can train annotation-free, then use existing annotations only to validate whether our gradient-level signal correctly identifies the minority group.

**What I need to see for falsifiability:**
1. A specific gradient quantity (not "gradient dynamics" generally) measured at specific training epochs
2. A specific threshold or trajectory shape that constitutes success
3. A control condition — does the same quantity behave differently when we *remove* the spurious correlation (train on balanced data)?

**Key Points:**
- Angle A requires a proxy partition to avoid group labels — must be explicit about what proxy
- Falsifiability requires specific operationalized quantities, not "gradient dynamics"
- Existing group annotations on Waterbirds/CelebA can validate without being used for training

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me pull back and assess the significance landscape here. The mechanistic question (Gap 1) is important, but I want to make sure we're targeting the version that maximizes impact given the feasibility constraints.

**The significance hierarchy:**
1. **Highest impact:** A mechanistic account that *enables a new training intervention* improving worst-group accuracy on Waterbirds/CelebA/MultiNLI without group labels — beating JTT/LfF and approaching DFR performance
2. **High impact:** A mechanistic diagnostic that *predicts* which training runs will exhibit strong spurious correlation reliance (before evaluating on test set), enabling early stopping or hyperparameter selection
3. **Moderate impact:** A post-hoc mechanistic account that *explains* existing method performance but doesn't enable new interventions

The field has more than enough "explanations" (Angles A, B, C as pure diagnostics are option 3). To be a real contribution, we need option 1 or 2.

**My recommendation:** Focus on the *intervention* hypothesis, not the diagnostic. Specifically:

**Hypothesis candidate:** Gradient alignment between early-high-loss and early-low-loss samples (as a proxy for spurious-minority vs. spurious-majority without group labels) can serve as an importance weight signal. Upweighting samples with persistent high gradient norm or low gradient alignment with the average batch — without any group labels — should improve worst-group accuracy on Waterbirds and CelebA, measurably over JTT/LfF baselines on existing benchmarks.

This is directly testable, uses only existing benchmarks, requires no new data, and has clear success criteria: worst-group accuracy ≥ JTT on Waterbirds and CelebA.

**Key Points:**
- Impact requires intervention, not just diagnosis
- Gradient-signal-based upweighting is the intervention target
- Success criterion: worst-group accuracy on Waterbirds/CelebA ≥ JTT without group labels

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

I appreciate Dr. Sage's impact framing, but I need to ground this in what's actually implementable with existing codebases in a reasonable compute budget.

**Feasibility assessment of the gradient-based intervention:**

*Computing per-sample gradient alignment across training:* Computing full gradient vectors for every training sample at every epoch is O(N × E × P) where P = parameter count. For ResNet-50 (25M params) on Waterbirds (11,788 samples), this is ~1.1TB of data per training run. Not feasible without approximation.

**But there are feasible approximations:**

1. **Last-layer gradient alignment only:** For ResNet-50, the last linear layer has 2048 × C parameters. For C=2 (binary classification), that's 4096 floats per sample. 11,788 × 4096 × 4 bytes ≈ 186MB total — entirely feasible. This is exactly what DFR (Kirichenko 2022) exploits: the last-layer features are sufficient.

2. **EMA gradient similarity:** Track exponential moving average of per-sample gradients across batches. Memory cost: N × last_layer_dim. Feasible.

3. **Forgetting events (Arpit 2017 pattern):** Track whether each sample's prediction flips between consecutive epochs. Binary flag per sample per epoch: 11,788 × 100 epochs × 1 bit ≈ 148KB. Trivially feasible.

**Concrete implementation path:**
- Fork kohpangwei/group_DRO or anniesch/jtt
- Add last-layer gradient tracking during training
- Compute cosine similarity between per-sample last-layer gradients and batch-average gradient
- Use this similarity score as inverse importance weight (low alignment = upweight)
- Evaluate on existing Waterbirds/CelebA splits (standard from group_DRO repo)
- Baseline comparisons: ERM, JTT, LfF (all have public implementations)

**Compute budget:** 3-4 GPU-hours per run on a single V100/A100. Completely standard.

**Key Points:**
- Full gradient tracking infeasible; last-layer gradient alignment feasible
- Forgetting events trivially feasible (binary flag)
- Existing repos (group_DRO, jtt) provide implementation base
- Single GPU run, standard compute budget

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — we're converging on something concrete. Let me synthesize the discussion so far into a strengthened hypothesis and identify what we still need to nail down.

**Emerging core hypothesis:** During ERM training, the gradient alignment between a sample's last-layer gradient and the current mini-batch average gradient is a reliable proxy for whether that sample belongs to the spurious-majority vs. spurious-minority group. Specifically:
- Spurious-majority samples (which the model learns to classify correctly via spurious features) exhibit *high* gradient alignment with the batch average (their gradient direction agrees with the majority)
- Spurious-minority samples (which the spurious feature cannot correctly classify) exhibit *low* gradient alignment with the batch average (their gradient direction conflicts with the majority rule)

**The intervention:** Use this misalignment signal to identify spurious-minority samples during training, and upweight them in the loss. This is implementable as a continuous online re-weighting scheme (no two-stage training required, unlike JTT).

**What this offers over JTT:**
- JTT uses misclassification after a full first-stage training run (two separate training runs, high compute)
- Our gradient alignment approach is online (computed during normal training, same compute as ERM)
- The signal is richer: gradient *alignment* vs. binary misclassification; captures degree of spurious-majority-ness

**Strengthening move:** The hypothesis should make a clear mechanistic prediction: gradient alignment between per-sample last-layer gradients and batch-mean gradient should be *negatively correlated* with spurious-minority group membership (as measured by existing group annotations on Waterbirds/CelebA). This is testable as a pure diagnostic (correlation analysis) before testing the intervention, giving us two levels of validation.

**Key Points:**
- Core mechanism: per-sample last-layer gradient alignment as proxy for spurious-minority membership
- Intervention: online upweighting of low-alignment samples during training
- Advantage over JTT: single training run (online), richer continuous signal
- Two-level validation: (1) correlation between alignment and group membership, (2) worst-group accuracy improvement

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'm going to push hard on several potential failure modes that could sink this hypothesis.

**Objection 1: Gradient alignment at the last layer is dominated by the classification head, not feature representations.**
If the last layer has strong weight magnitude for the spurious feature direction, the gradient alignment will reflect the label → weight → output → loss gradient path, which is identical for spurious-majority and spurious-minority samples early in training (when the model uses spurious features for both). The alignment difference only appears *after* the model has already committed to the spurious feature. This means the signal arrives too late to intervene during the critical early phase. 

*Mitigation:* Test alignment at multiple layers (not just last layer). Or test alignment on a *penultimate* layer where feature representations are more separable.

**Objection 2: High-loss samples ≠ spurious-minority samples.**
Existing methods (JTT, LfF) use misclassification as a proxy for spurious-minority membership. This proxy has known failure modes: hard samples (noisy labels, ambiguous images) have high loss for reasons unrelated to spurious correlation. If gradient alignment is correlated with per-sample loss, then gradient alignment is just a continuous version of the JTT proxy with the same failure mode. The hypothesis must show gradient alignment provides *additional* information beyond per-sample loss.

*Mitigation:* In the experiments, compare information content of gradient alignment vs. per-sample loss for predicting group membership (using existing group annotations as gold standard). Show gradient alignment is a better proxy via ROC-AUC comparison.

**Objection 3: The intervention (upweighting low-alignment samples) may be unstable.**
If the weight assigned to each sample changes every batch based on a noisy gradient alignment estimate, training becomes unstable. The optimization landscape changes iteration-by-iteration, which may prevent convergence or introduce high variance.

*Mitigation:* Use exponential moving average of alignment scores (EMA with momentum β = 0.9-0.99) to smooth the signal. Clip weights to a maximum multiplier (e.g., 5×) to prevent extreme upweighting. These are standard techniques in importance weighting literature.

**After mitigations, my assessment:** The hypothesis is plausible but requires the alignment-vs-loss comparison (Objection 2) as a non-negotiable component of the experimental design. Without it, the work is incremental over JTT.

**Key Points:**
- Alignment at last layer may arrive too late — test penultimate layer
- Must show gradient alignment adds information beyond per-sample loss
- EMA smoothing needed for stable online upweighting
- Non-negotiable: alignment vs. loss ROC-AUC comparison using existing group annotations

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's objections are sharp. I want to address Objection 2 directly and propose what makes this *novel* relative to JTT/LfF.

The key novelty is *directional* vs. *magnitude* information. JTT and LfF use per-sample loss magnitude (how high is the loss?) as a proxy for spurious-minority membership. Gradient alignment uses the *direction* of the gradient vector — does this sample's gradient agree or disagree with the current model's update direction?

These are fundamentally different signals:
- **Magnitude (JTT/LfF):** Captures "how hard is this sample for the current model?" — conflates spurious-minority samples WITH hard/noisy samples
- **Direction (ours):** Captures "does this sample want the model to move in the same direction as everyone else?" — more specifically targets samples whose feature signal *conflicts* with the majority consensus, which is exactly the structure of spurious correlations

**Novel prediction:** Consider a sample that is spurious-majority but happens to have high loss early in training (e.g., an atypical landbird on land with an unusual pose). JTT would upweight this sample (high loss = minority proxy). Our gradient alignment approach would NOT upweight it, because its gradient still aligns with the majority direction (the background signal is correct, the pose is just hard). This is a differentiating prediction that can be tested on Waterbirds/CelebA by finding samples that are misclassified early but are actually from the spurious-majority group — JTT and our method would handle them differently.

**On Objection 1 (timing):** I agree the last-layer signal may arrive late. The interesting angle is: does the *penultimate layer* (ReLU activations of the second-to-last layer) gradient alignment signal provide *earlier* indication of group membership? We could track gradient alignment at both layers and measure which epoch the signal becomes predictive. This becomes a mechanistic finding in its own right.

**Key Points:**
- Directional gradient signal (alignment) vs. magnitude signal (JTT/LfF): fundamentally different information
- Novel prediction: gradient alignment correctly handles hard spurious-majority samples that JTT incorrectly upweights
- Multi-layer gradient tracking reveals when spurious feature learning is established

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

We've now iterated through enough perspectives that I can identify what must be in the experimental design for falsifiability. Let me lay out the complete validation structure.

**Experiment 1 (Diagnostic Validation):**
- Dataset: Waterbirds and CelebA (existing group annotations available but not used during training)
- Procedure: Train ERM (ResNet-50 on Waterbirds, ResNet-50 on CelebA)
- Measurement: At each training epoch, compute cosine similarity between per-sample last-layer and penultimate-layer gradients and the batch-mean gradient
- Ground truth: existing group annotations (spurious-majority vs. spurious-minority)
- Metric: ROC-AUC of gradient alignment score for predicting spurious-minority group membership
- Compare against: per-sample loss trajectory ROC-AUC (JTT proxy baseline)
- Success criterion: gradient alignment ROC-AUC > per-sample loss ROC-AUC at any training epoch

**Experiment 2 (Intervention Validation):**
- Method: Online upweighting with EMA-smoothed gradient alignment score (inverse alignment = upweight)
- Datasets: Waterbirds, CelebA (and optionally MultiNLI using BERT baseline from group_DRO repo)
- Baselines: ERM, JTT, LfF (all have public implementations)
- Metric: Worst-group accuracy (standard metric from Sagawa et al. 2020)
- Success criterion: worst-group accuracy ≥ JTT on both Waterbirds and CelebA

**Falsification condition:** If gradient alignment ROC-AUC ≤ per-sample loss ROC-AUC at ALL epochs on BOTH datasets, hypothesis is falsified. If intervention worst-group accuracy < JTT on both datasets, intervention hypothesis is falsified.

**Why this is feasible:** group_DRO codebase (kohpangwei/group_DRO) already computes per-sample losses. Adding gradient alignment tracking requires ~50 lines of PyTorch code. Compute: standard single-GPU training runs.

**Key Points:**
- Two-experiment structure: diagnostic validation + intervention validation
- Explicit success and falsification criteria
- Existing codebase (group_DRO) as implementation base
- ROC-AUC comparison vs. JTT proxy is the non-negotiable discriminating test

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me finalize the implementation feasibility assessment for Prof. Vera's experimental design.

**Experiment 1 timing:**
- 100 epochs on Waterbirds (ResNet-50): ~2 hours on one A100
- Per-sample gradient computation at penultimate layer: ~4096-dimensional vectors for 11,788 samples = 48M floats = 192MB per epoch
- Storing full gradient trajectories for 100 epochs: 19.2GB — feasible on a single GPU with disk offload
- Alternatively: compute only at epochs {1, 5, 10, 25, 50, 75, 100} — reduces to 1.34GB

**Experiment 2 timing:**
- EMA upweighting adds one momentum update per sample per batch — O(N) additional computation per epoch
- Overhead: <5% additional training time
- Three datasets × 3 seeds × 2 methods (ERM + our method) + baselines (JTT needs 2× training runs) = ~30 GPU-hours total

**Implementation sketch:**
```python
# During training, after loss.backward():
with torch.no_grad():
    batch_grad_mean = torch.mean(per_sample_grads, dim=0)  # last-layer
    alignment = F.cosine_similarity(per_sample_grads, batch_grad_mean.unsqueeze(0))
    ema_alignment[sample_idx] = beta * ema_alignment[sample_idx] + (1-beta) * alignment
    weights = 1.0 / (ema_alignment[sample_idx].clamp(min=0.1))  # inverse alignment = upweight
    weights = weights / weights.mean()  # normalize
    loss = (loss * weights).mean()
```

This requires per-sample gradient computation, which torch.func.vmap enables efficiently.

**Risk:** torch.func.vmap has memory scaling issues at large batch sizes — must use batch size ≤ 32 for per-sample grad computation on last layer, or use gradient checkpointing.

**Key Points:**
- Implementation feasible: ~50 lines of PyTorch, vmap for per-sample gradients
- 30 GPU-hours total — single machine feasible
- Memory constraint: batch size ≤ 32 for per-sample grad tracking, or checkpoint

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We have reached the critical convergence point. Let me write the final synthesized hypothesis statement and address the remaining open question.

**Convergence assessment:**
- SPECIFIC ✅: Per-sample last-layer gradient alignment as spurious-minority proxy
- MECHANISM ✅: Low alignment = sample's feature signal conflicts with majority gradient direction = spurious-minority indicator
- PREDICTIONS ✅: P1: alignment ROC-AUC > loss ROC-AUC; P2: online upweighting ≥ JTT worst-group; P3: penultimate layer provides earlier signal than last layer
- NOVELTY ✅: Directional gradient signal vs. magnitude signal — handles hard-but-spurious-majority samples correctly
- FEASIBILITY ✅: ~50 lines PyTorch, 30 GPU-hours, existing repos
- OBJECTIONS ✅: Prof. Rex's three objections addressed (penultimate layer, alignment vs. loss comparison, EMA smoothing)

**Final hypothesis statement:**

Under standard ERM training on spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI), if we compute the cosine similarity between per-sample last-layer (or penultimate-layer) gradients and the batch-mean gradient during training, and use the EMA-smoothed inverse alignment score as an online importance weight, then the trained model will achieve better worst-group accuracy than JTT and LfF baselines, because gradient alignment direction specifically captures spurious-minority membership (conflicting gradient direction) in a way that magnitude-based proxies (JTT: misclassification, LfF: high loss relative to amplified-bias model) cannot distinguish from hard-but-spurious-majority samples.

**The single most important open question:** Does the alignment signal provide additional ROC-AUC for predicting group membership beyond what per-sample loss alone provides? This is Experiment 1 — it must be run first. If not, the whole mechanistic claim collapses to "we have a continuous version of JTT." If yes, we have a genuine new probe of spurious feature learning dynamics.

**Key Points:**
- All convergence criteria met
- Hypothesis is specific, mechanistic, testable, novel, feasible, and addresses all major objections
- Non-negotiable first experiment: gradient alignment ROC-AUC vs. per-sample loss ROC-AUC for group membership prediction

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

One final critical stress test before I endorse convergence. The hypothesis must survive this:

**The confound:** On Waterbirds, the spurious-majority group (landbirds on land, waterbirds on water) is 4.5× larger than the spurious-minority group. In any mini-batch, ~82% of samples will be spurious-majority. This means the batch-mean gradient is almost entirely dominated by spurious-majority samples. So:

- Spurious-majority gradient ≈ batch-mean gradient → high alignment (correct)
- Spurious-minority gradient ≠ batch-mean gradient → low alignment (correct)

But this just means alignment reflects *frequency in the batch*, not specifically the *gradient direction of the spurious feature*. If the minority group happened to be the spurious-majority group, alignment would flip. The mechanism is really "minority in batch → low alignment" not specifically "spurious-minority → low alignment."

**Is this a problem?** Only if the minority group in batches is frequently NOT the spurious-minority group. In practice on Waterbirds, the spurious-minority group IS the dataset minority, so these coincide. But the mechanistic claim "gradient alignment detects the spurious feature" is not entirely correct — it detects the *statistical minority in the batch*.

**Mitigation available:** This confound is acknowledged, not fatal. The claim must be restated more precisely: "On benchmarks where spurious-minority and dataset-minority coincide (as in Waterbirds and CelebA), per-sample gradient alignment detects the statistical minority, which proxies spurious-minority membership." The directional-vs-magnitude novelty claim still stands because magnitude methods also have this property implicitly.

**My verdict:** ENDORSE with the precision caveat. The experimental design Prof. Vera laid out is sufficient to validate the restated claim.

**Key Points:**
- Core mechanism is "statistical minority in batch → low alignment," not specifically "spurious feature direction"
- On Waterbirds/CelebA, spurious-minority = statistical minority → confound is benign for empirical claims
- Mechanistic claim must be precisely stated to avoid overclaiming
- Endorse convergence with this caveat incorporated

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The directional gradient signal (alignment) vs. magnitude signal (JTT/LfF) distinction is genuinely novel. No existing annotation-free method exploits gradient cosine similarity as a training-time proxy for spurious-minority membership. The multi-layer temporal analysis (when does alignment become predictive?) is a secondary mechanistic contribution that advances understanding of shortcut learning dynamics.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The two-experiment structure (diagnostic ROC-AUC comparison + intervention worst-group accuracy) provides explicit falsification conditions. The primary falsifier is clear: gradient alignment ROC-AUC ≤ per-sample loss ROC-AUC at all epochs. The intervention falsifier is equally clear. The experimental protocol uses existing benchmarks, existing code, and existing group annotations as evaluation ground truth only.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The intervention hypothesis targets the exact performance gap the field cares about (JTT/LfF → DFR, no group labels). An online upweighting method that matches or exceeds JTT in a single training run (vs. JTT's two runs) would be immediately useful for practitioners. The mechanistic diagnostic (Experiment 1) contributes to scientific understanding of shortcut learning dynamics.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation is 50 lines of PyTorch using torch.func.vmap for per-sample gradients. Total compute: ~30 GPU-hours on existing hardware. All datasets (Waterbirds, CelebA) and baseline implementations (group_DRO, jtt, LfF) are publicly available. No new infrastructure required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The Phase 2A discussion converged on the following hypothesis: **Gradient Alignment Debiasing (GAD)** — a method that exploits the cosine similarity between per-sample last-layer gradients and the batch-mean gradient as an online proxy for spurious-minority group membership during standard ERM training on spurious correlation benchmarks.

The core claim is: spurious-minority samples (those which the spurious feature cannot correctly classify) produce gradient vectors that *conflict in direction* with the majority batch gradient (dominated by spurious-majority samples), while hard-but-spurious-majority samples produce gradients that *align in direction* with the batch. This directional distinction is not captured by existing magnitude-based proxies (JTT's misclassification proxy, LfF's high-loss relative to biased model). By upweighting low-alignment samples online (with EMA smoothing and weight clipping), the method performs debiasing in a single training run without requiring group annotations.

Key predictions: (P1) gradient alignment ROC-AUC for predicting spurious-minority membership exceeds per-sample loss ROC-AUC on Waterbirds and CelebA using existing group annotations as evaluation ground truth; (P2) worst-group accuracy of the online GAD method ≥ JTT on both datasets; (P3) penultimate-layer gradient alignment becomes predictive earlier in training than last-layer alignment, revealing the temporal structure of spurious feature acquisition. 

The experimental setup requires only existing implementations (kohpangwei/group_DRO, anniesch/jtt, alinlab/LfF), ~50 lines of PyTorch using torch.func.vmap, and ~30 GPU-hours. Prof. Rex's precision caveat is incorporated: the mechanism detects statistical minority-in-batch, which coincides with spurious-minority on Waterbirds/CelebA, so empirical claims are valid within these benchmark settings.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The mechanism "low alignment = spurious-minority" relies on spurious-minority = statistical minority in batch. Fails if minority-group class balance is enforced in batching strategy.
- torch.func.vmap per-sample gradient computation may have memory issues with large models (ResNet-50 is borderline; ViT-B would require gradient checkpointing).
- **Mitigation Strategy:** (1) Explicitly test with standard random sampling (no class-balanced batching) as primary condition; test with class-balanced batching as ablation to characterize failure mode. (2) Implement gradient checkpointing fallback and document memory budget table in paper.

