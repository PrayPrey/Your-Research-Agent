# Phase 2A Research Discussion Log

**Gap ID:** Gap1  
**Gap Title:** Quantitative Architecture-Temporal Correlation  
**Gap Relevance:** PRIMARY  
**Timestamp:** 2026-08-24T22:35:00Z  
**Execution Mode:** UNATTENDED (Self-Play Discussion, Independent Controller Ablation)  

---

## Research Gap Briefing

**Current State:** Literature shows architectures differ in spurious susceptibility (Geirhos 2020, Sagawa 2020), temporal dynamics exist (Toneva 2019), but no systematic comparison.

**Missing Piece:** Quantitative metrics mapping architectural properties (depth, width, normalization, attention) to temporal learning metrics (spurious-core gap, convergence timing).

**Potential Impact:** High — directly enables answering the core research question on how architectural properties influence temporal learning dynamics.

---

## Reference Papers

**P1: Shortcut Learning in Deep Neural Networks (Geirhos et al., 2020)**
- arXiv: 2004.07780 | Citations: ~800
- **Key Insight:** Simplicity bias causes preferential learning of spurious correlations. Architectures differ in susceptibility but no systematic quantitative comparison exists.
- **Evidence:** Waterbirds (97% avg, 72% worst-group), CelebA, texture-vs-shape bias in CNNs.
- **Limitation:** No architectural comparison across normalization/attention/skip connections.

**P2: Example Forgetting during DNN Learning (Toneva et al., 2019)**
- arXiv: 1812.05159 | Citations: ~300
- **Key Insight:** Temporal ordering — unforgettable examples (simple/spurious) learned first, forgettable examples (complex/core) learned later.
- **Evidence:** CIFAR-10 (30% unforgettable), ImageNet (texture unforgettable, shape forgettable).
- **Limitation:** Single architecture (ResNet), no architectural property linkage.

**P3: Group DRO for Worst-Case Generalization (Sagawa et al., 2020)**
- arXiv: 1911.08731 | Citations: ~1500
- **Key Insight:** Worst-group accuracy reveals spurious reliance. DRO training upweights minority groups to reduce shortcuts.
- **Evidence:** Waterbirds (ERM 72.6% → DRO 91.4% worst-group), CelebA (ERM 47.2% → DRO 88.9%).
- **Limitation:** Architectural comparison limited to ResNet variants, no temporal analysis.

---

## Previous Failure / Routing Context

No prior Phase 2A attempts found (first execution).

---

## MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced)

**REJECT:**
- New benchmarks, rubrics, or scoring frameworks
- Synthetic/generated data or future data that doesn't exist yet
- Human evaluation, annotation, or subjective scoring

**ACCEPT ONLY:**
- Hypotheses testable immediately using **existing real datasets** (Waterbirds, CelebA, CMNIST, CIFAR-10, ImageNet subsets)
- Hypotheses testable using **existing benchmarks** (worst-group accuracy, standard accuracy, forgetting events)

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the whole question on its head? Instead of asking "which architectures are more robust?" we ask: "what architectural properties create PREDICTABLE temporal learning signatures?" The gap here isn't just about characterization — it's about discovering quantitative invariants.

Here's the wild idea: **architectural components act as temporal filters** that determine when features emerge during training. Batch normalization might amplify early spurious features by normalizing batch-level statistics. Attention mechanisms might create different temporal ordering by globally aggregating features from the start. Skip connections might stabilize core feature learning by preserving gradient flow. Each component has a characteristic "temporal profile."

Toneva 2019 showed forgetting events track feature complexity, but they only tested ResNets. What if we measure forgetting dynamics across architectures with different components? Geirhos 2020 noted architectural differences but didn't quantify them temporally. Sagawa 2020 gave us worst-group accuracy as a snapshot metric, but what if we track it DURING training to see when spurious reliance emerges?

The paradigm shift: **temporal learning curves as architectural fingerprints**. Plot worst-group accuracy gap (spurious-core) vs epoch for ResNet-BN, ResNet-LN, ViT, pure CNN. Each architecture should show a characteristic curve shape — some might show early spurious dominance that never corrects, others might show late correction. The curve parameters (initial gap, correction rate, final gap) become our quantitative architectural properties.

**Key Points:**
- Measure temporal learning curves (worst-group gap vs epoch) as architectural signatures
- Test hypothesis: BN amplifies early spurious learning, LN reduces it, attention changes temporal ordering
- Use existing metrics (worst-group accuracy, forgetting events) but apply them TEMPORALLY across architectures
- No new benchmarks needed — Waterbirds/CelebA already have group labels

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's temporal fingerprint idea has merit, but we need precision. What EXACTLY would falsify the BN amplification hypothesis? Let's ground this.

**Testable Prediction 1:** If BN amplifies early spurious learning, then ResNet-BN should show higher worst-group accuracy gap than ResNet-LN in the first 10 epochs on Waterbirds. Falsifier: If gaps are statistically indistinguishable (p > 0.05, paired t-test across 5 seeds), BN amplification is unsupported.

**Testable Prediction 2:** If attention changes temporal ordering, ViT should show different gap convergence rate than CNN on same dataset. Measure as slope of worst-group gap from epoch 20-50. Falsifier: If slopes overlap within confidence intervals, attention doesn't change temporal dynamics.

**Testable Prediction 3:** If architecture creates predictable signatures, gap curves should be reproducible across datasets with similar spurious structure. Test on Waterbirds + CelebA (both have binary spurious correlations). Falsifier: If curve rankings change between datasets (e.g., BN worst on Waterbirds, LN worst on CelebA), signatures are dataset-specific, not architectural.

The measurement protocol must be rigorous. Sagawa 2020 computed worst-group accuracy at convergence only. We need to log it EVERY epoch for ALL groups. Toneva 2019's forgetting events require tracking per-example predictions every epoch — computationally expensive but feasible on Waterbirds (5.9k examples).

Confounds to control: learning rate schedule (use constant LR for first experiment to isolate architectural effects), random seed variation (report mean ± std across 5 seeds), initialization scheme (He/Xavier can affect early dynamics).

What result would convince me this is wrong? If worst-group gap curves are dominated by random seed variance more than architectural differences. If the gap between BN and LN is smaller than the gap between two random BN runs.

**Key Points:**
- Three specific predictions with quantitative falsifiers
- Measurement: worst-group gap logged every epoch across 5 seeds
- Controls: constant LR, fixed init scheme, multiple datasets
- Failure mode: seed variance > architectural signal

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this contribute beyond incremental architectural analysis? Dozens of papers compare ResNet vs ViT on benchmarks. Why does the temporal dimension matter?

Here's the significance claim I see emerging: **temporal learning curves reveal WHEN architectural inductive biases cause failure, not just WHETHER they fail**. This is a fundamentally different kind of knowledge.

Geirhos 2020 told us CNNs learn texture bias. Sagawa 2020 quantified the damage at convergence (72% worst-group). But neither told us if this is an early-training inevitability or a correctable tendency. If BN-amplified spurious learning happens in epoch 1-10 but could be corrected with later interventions (learning rate warmup, curriculum), that's actionable. If it's baked in from random initialization, that's architectural determinism.

The field impact: this opens a new research direction in **temporal robustness**. Current work asks "which architecture is more robust?" This asks "when do architectures become robust?" That's a fundamentally different optimization problem. If we know ViT corrects spurious reliance at epoch 30 but ResNet-BN never does, we can design hybrid architectures or adaptive training schedules.

Related work positioning: Toneva 2019 studied temporal dynamics within one architecture. This systematizes it ACROSS architectures. Sagawa 2020 studied robustness at convergence. This studies robustness trajectories. The differentiation is clear: first systematic temporal comparison of architectural properties on spurious correlation learning.

What makes this genuinely new vs incremental? Existing work studies architecture OR temporal dynamics OR spurious correlations. This is the first to study all three simultaneously with quantitative metrics. The temporal fingerprint concept — treating learning curves as architectural signatures — is novel framing.

Potential limitation: if all architectures show identical temporal curves (just different final values), temporal dimension adds no information. But Toneva's forgetting results suggest temporal structure exists — we're just expanding it to architectural comparison.

**Key Points:**
- Significance: reveals WHEN failure happens, enables temporal interventions
- Field impact: opens temporal robustness as new research direction
- Differentiation: first systematic architectural comparison on temporal spurious learning dynamics
- Novel framing: temporal curves as architectural signatures

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what we can measure and what we can't. The temporal fingerprint idea is theoretically sound, but are the measurement methods scientifically valid?

**Measurement Validity Check 1: Worst-Group Gap as Temporal Metric**
Sagawa 2020 validated worst-group accuracy as a spurious correlation detector at convergence. Can we use it temporally? Yes — it's just applying the same metric every epoch instead of once. No new measurement assumption needed. Computationally: O(epochs × eval_size) — feasible on Waterbirds (5.9k examples × 100 epochs = 590k forward passes per run, trivial for modern GPUs).

**Measurement Validity Check 2: Forgetting Events Across Architectures**
Toneva 2019 defined forgetting event as: example correctly classified at epoch t, misclassified at epoch t+k, correctly classified again later. This is architecture-agnostic — just tracks per-example predictions. Validity: established. Computation: O(epochs × train_size × num_architectures). For Waterbirds train (4.8k examples × 100 epochs × 4 architectures = 1.92M forward passes total). Single GPU experiment, ~2 hours.

**Intervention Validity Check: BN vs LN Swap**
Can we swap normalization layers in ResNet without breaking training? Yes — architecturally equivalent (both normalize activations, different statistics). PyTorch implementation: replace `nn.BatchNorm2d` with `nn.LayerNorm`. No fundamental barrier. Prior work (Santurkar 2019) studied BN vs no-norm, LN is similar intervention.

**Reproducibility Across Datasets: Physical Constraint**
Prof. Vera proposed testing on Waterbirds + CelebA. Both have binary spurious correlations (background/foreground, gender/attribute). Structurally similar enough to test signature consistency. Constraint: signatures might be specific to correlation *strength*, not just architecture. CelebA has stronger spurious correlation (95% co-occurrence) than Waterbirds (85%). If correlation strength matters more than architecture, signatures won't transfer. This is a legitimate boundary condition, not a feasibility blocker.

**What Could Actually Break This (Fundamental Barriers, Not Budget):**
1. If worst-group accuracy has high epoch-to-epoch noise, temporal curves become uninterpretable. Mitigation: use validation set, smooth curves over 5-epoch windows.
2. If architectural differences are masked by optimization noise before epoch 20, temporal signatures won't emerge. Mitigation: use constant LR (no schedule) to isolate architectural effects.
3. If forgetting events are dominated by batch sampling randomness, not feature learning. Mitigation: average across multiple data orderings.

None of these are show-stoppers. This is technically feasible with existing tools and datasets.

**Key Points:**
- Measurement methods are scientifically valid (extensions of Sagawa/Toneva)
- Computational cost is feasible (~2 GPU-hours for full experiment)
- Architectural interventions (BN→LN swap) are valid
- Main risk: measurement noise, mitigable with smoothing and averaging

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! We're converging on something testable. Let me synthesize what's emerged and strengthen it against the concerns raised.

**Core Hypothesis (Under-If-Then-Because):**
Under standard supervised learning on datasets with known spurious correlations (Waterbirds, CelebA), if we compare ResNet with Batch Normalization vs Layer Normalization vs Vision Transformer architectures during training, then we will observe DISTINCT temporal learning curves characterized by worst-group accuracy gap trajectories, because different architectural components (normalization statistics, attention mechanisms, local vs global receptive fields) create different temporal priorities for spurious vs core feature learning.

**Addressing Prof. Vera's Rigor Demands:**
Taking your three predictions directly:
- **P1 (BN Amplification):** Measure mean worst-group gap for ResNet-BN vs ResNet-LN in epochs 1-10 on Waterbirds. Predict: BN gap > LN gap by ≥5 percentage points. Falsifier: p > 0.05 or effect < 3pp.
- **P2 (Attention Temporal Ordering):** Measure gap convergence slope (epochs 20-50) for ViT vs ResNet-BN on Waterbirds. Predict: ViT shows steeper correction slope (faster gap reduction). Falsifier: slopes within overlapping 95% CI.
- **P3 (Signature Consistency):** Rank architectures by average gap (epochs 10-30) on Waterbirds, repeat on CelebA. Predict: ranking preserved (Spearman ρ > 0.8). Falsifier: ρ < 0.6 or ranking reversal.

**Addressing Dr. Sage's Significance:**
The temporal dimension isn't just descriptive — it's actionable. If BN amplifies spurious learning early but this is correctable with LR warmup starting epoch 15, that's a design principle. If ViT's attention mechanism naturally corrects spurious reliance by epoch 30, hybrid architectures could use ViT-style attention only after epoch 20 to get correction without early-training cost.

**Addressing Prof. Pax's Feasibility:**
Accepting the measurement noise mitigation: 5-epoch smoothing window, 5 random seeds, constant LR=0.01 for first experiment. Accepting the correlation strength boundary: if signatures don't transfer from Waterbirds (85% spurious) to CelebA (95% spurious), we've discovered that temporal signatures are correlation-strength-dependent — that's still a finding, not a failure.

**The Strengthened Hypothesis:**
Architectural components act as temporal filters with characteristic time constants. BN (batch statistics) creates fast early adaptation to spurious batch-level correlations. LN (layer statistics) slows early spurious learning. Attention (global aggregation) enables mid-training correction. These effects are quantifiable via worst-group gap trajectories and reproducible across datasets with similar spurious structure.

**Key Points:**
- Core claim: architectural components → distinct temporal gap trajectories
- Three predictions with quantitative thresholds from Prof. Vera
- Actionable outcome: temporal architecture design principles
- Feasibility confirmed with mitigation strategies from Prof. Pax

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is strong, but let me find the weak points. Where does this break down?

**Challenge 1: Confounding Explanation for BN Effect**
You claim BN amplifies early spurious learning via batch statistics. Alternative explanation: BN just speeds up training in general, so EVERYTHING (spurious and core) is learned faster. If BN shows higher gap at epoch 10, that might just be because BN-trained model has reached epoch-20-equivalent training. Falsifier needed: show BN gap is higher at SAME average accuracy level, not same epoch count. Otherwise epoch-based comparison is invalid.

**Challenge 2: Attention Mechanism Assumption**
You claim ViT's global attention enables mid-training correction. But ViT also has different inductive bias (no spatial locality), different optimization dynamics (requires different LR), different parameter count. How do you isolate attention effect from these confounds? What would convince me attention is causal: hybrid ResNet with multi-head self-attention layers shows ViT-like correction despite having CNN structure. Otherwise it's "ViT is different" not "attention causes correction."

**Challenge 3: Statistical Power on Small Gaps**
Sagawa 2020 showed 72% vs 97% worst-group gap (25pp difference). You're predicting 5pp difference between BN and LN. With 5 seeds and noisy validation curves, do you have statistical power to detect 5pp effect? Sketch the calculation: need std(gap) < 2pp to detect 5pp effect at 80% power (α=0.05, two-tailed). Waterbirds has 4 groups (2×2), smallest group ~600 examples. Binomial variance for 600 examples at 80% accuracy: sqrt(0.8×0.2/600) = 1.6%. With 5 seeds, SE = 1.6%/sqrt(5) = 0.7%. Detectable difference at 80% power: 0.7% × 2.8 = 2pp. Marginal but possible. Accepted, but increase to 10 seeds for safety.

**Challenge 4: Null Result Interpretation**
If all three predictions fail (no BN-LN difference, no ViT correction, no signature transfer), what have we learned? "Architectures don't have temporal signatures" is hard to publish. The hypothesis needs asymmetric outcomes: positive result = novel finding, negative result = still informative. Current framing achieves this IF you add: "Failure would show temporal dynamics are dominated by optimization, not architecture — challenging conventional architecture-centric view." That makes null result publishable.

**Challenge 5: Generalization Beyond Binary Spurious Correlations**
Waterbirds and CelebA both have binary spurious correlations (presence/absence of background, gender). What if temporal signatures only exist for this correlation type? Test case: CMNIST has deterministic spurious correlation (color perfectly predicts digit in 90% of training). If signatures don't appear on CMNIST, hypothesis is limited to stochastic spurious correlations. Add CMNIST as third dataset, accept narrower scope if needed.

What would convince me this is solid: address the epoch-vs-accuracy confound (Challenge 1), show attention isolation experiment or accept correlation-not-causation on ViT (Challenge 2), increase seeds to 10 (Challenge 3), frame null results as informative (Challenge 4), test CMNIST or accept binary-correlation scope (Challenge 5).

**Key Points:**
- Epoch-based comparison confounded by BN's training speed (use accuracy-matched comparison)
- Attention effect confounded with ViT's other differences (need ablation or weaken claim)
- Statistical power marginal at 5 seeds (increase to 10)
- Null result interpretation must be valuable (frame as optimization-dominance finding)
- Scope limited to binary spurious correlations unless CMNIST tested

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex found the cracks — let's turn them into design features! Challenge 1 (epoch vs accuracy confound) is brilliant. Instead of fixed epochs, we plot worst-group gap vs AVERAGE ACCURACY on x-axis. This gives us training-progress-matched comparison. If BN reaches 90% average accuracy with 20pp worst-group gap while LN reaches 90% average with 10pp gap, BN amplification is real regardless of epoch count.

Challenge 2 (attention isolation) — you're right, full ViT confounds everything. Here's the creative solution: use DeiT (Data-efficient image Transformer) which has CNN-comparable parameter count and training dynamics. Better yet, test ResNet + CBAM attention (Convolutional Block Attention Module) — it's attention grafted onto ResNet backbone. If ResNet-CBAM shows ViT-like correction curves, attention effect is isolated. If it doesn't, we weaken the claim to "ViT architecture (global receptive field + attention) enables correction" and acknowledge we can't decompose which component matters.

Challenge 3-5: Accepting all of them! 10 seeds (power), null result framing (optimization-dominance finding), CMNIST third dataset (test deterministic vs stochastic spurious correlations).

NOW we're onto something even wilder: what if temporal signatures exist for stochastic spurious correlations but NOT deterministic ones? That would reveal mechanism: BN amplifies early learning of whatever provides *statistical* signal, but deterministic correlations (CMNIST color) are learned identically by all architectures because gradient is unambiguous. Stochastic correlations (Waterbirds background appears in 85% of landbirds) create gradient ambiguity, and THAT's where architectural components matter.

**Refined Hypothesis:**
Under stochastic spurious correlations (Waterbirds 85%, CelebA 95%), architectural components create distinct worst-group gap trajectories when plotted against training progress (average accuracy), because normalization and attention mechanisms differ in how they resolve gradient ambiguity from stochastic correlations.

**Key Points:**
- Plot gap vs average accuracy (not epochs) to eliminate training-speed confound
- Test ResNet-CBAM or DeiT to isolate attention effect, or weaken claim to "ViT architecture"
- 10 seeds for power, null result = optimization-dominance finding
- Add CMNIST to test scope boundary (stochastic vs deterministic spurious correlations)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** First systematic temporal comparison of architectural components on spurious learning dynamics. Novel framing of temporal curves as architectural signatures. Stochastic vs deterministic spurious correlation hypothesis is genuinely new angle. Cross-architecture temporal analysis hasn't been done before.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three specific predictions with quantitative thresholds and clear falsifiers. Accuracy-matched comparison eliminates training-speed confound. 10-seed design provides adequate statistical power (2pp detectable effect). Measurement protocol is rigorous and reproducible.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Opens temporal robustness as new research direction. Reveals WHEN architectural failures happen, enabling temporal interventions. Clear differentiation from prior work (Toneva: single architecture, Sagawa: convergence-only, Geirhos: qualitative). Positive and null results both informative (architecture-driven vs optimization-driven dynamics).

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Measurement methods validated (extensions of Sagawa/Toneva). Computational cost feasible (~2 GPU-hours). Architectural interventions valid (BN→LN swap, ResNet-CBAM). Noise mitigation strategies (smoothing, averaging) address main risks. Three existing datasets (Waterbirds, CelebA, CMNIST) provide complete test coverage.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

Under stochastic spurious correlations (Waterbirds 85% co-occurrence, CelebA 95% co-occurrence), different architectural components create DISTINCT worst-group accuracy gap trajectories when measured against training progress (average accuracy on x-axis). Specifically: (1) Batch Normalization amplifies early spurious learning because it normalizes batch-level statistics, making spurious batch correlations easier to learn than instance-level core features. (2) Layer Normalization reduces early spurious amplification by normalizing per-instance, eliminating batch-level spurious signal. (3) Attention mechanisms (ViT or ResNet-CBAM) enable mid-training correction by globally aggregating features, allowing core features to override early spurious patterns.

**Three testable predictions:** P1: ResNet-BN shows ≥5pp higher worst-group gap than ResNet-LN when both reach 90% average accuracy on Waterbirds (falsifier: p>0.05 or effect <3pp across 10 seeds). P2: ViT/ResNet-CBAM shows steeper gap reduction slope (epochs 20-50) than ResNet-BN on Waterbirds (falsifier: overlapping 95% CI). P3: Architecture ranking by gap (at 90% avg accuracy) preserved from Waterbirds to CelebA with Spearman ρ>0.8 (falsifier: ρ<0.6).

**Experimental approach:** Train ResNet-BN, ResNet-LN, ResNet-CBAM, ViT on Waterbirds/CelebA/CMNIST. Log worst-group accuracy every epoch. Plot gap vs average accuracy (training-progress-matched). 10 seeds, constant LR=0.01, He initialization. Report mean±std, paired t-tests, effect sizes. Total cost: ~6 GPU-hours.

**Novelty:** First temporal-architectural joint analysis of spurious correlations. **Significance:** Enables temporal architecture design. **Feasibility:** Validated measurements, existing datasets.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Attention effect still partially confounded (ViT has other differences), ResNet-CBAM ablation helps but doesn't fully isolate. Accept correlation not causation for attention claim.
- **Concern 2:** CMNIST deterministic spurious correlation might not show signatures, narrowing scope to stochastic correlations only. Accept scope limitation if confirmed.
- **Mitigation Strategy:** Report all results transparently. If CMNIST shows no signatures, conclusion is "temporal signatures specific to stochastic spurious correlations." If ResNet-CBAM doesn't match ViT, conclusion is "ViT architecture (global structure) not just attention." Both are valid scientific findings.

---

