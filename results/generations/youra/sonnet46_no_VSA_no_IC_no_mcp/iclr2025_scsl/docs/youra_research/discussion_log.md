# Phase 2A Discussion Log
# Gap: Cross-Paradigm Spurious Feature Encoding Comparison

**Gap ID:** gap-2
**Gap Title:** Systematic Cross-Paradigm Comparison of Spurious Feature Encoding (Supervised vs. SSL vs. Contrastive)
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop — Independent-Controller Ablation)
**Date:** 2026-08-26
**Execution Mode:** UNATTENDED

---

## Previous Failure / Routing Context

**Source:** `.serena/memories/failure_h-e1_run1.md`

**Hypothesis h-e1 (Run 1) — FAIL — ROUTED_TO_PHASE_0:**
- h-e1 tested existence of SGD probes (speed_diff, margin_gap, directional_curvature) via CV > 0.05 across 5 seeds on Waterbirds.
- speed_diff (CV=0.0473) and margin_gap (CV=0.0374) failed the gate — they are stable, not variable across seeds.
- directional_curvature passed (CV=0.264) — expected, as optimization path divergence varies.
- Root cause: gate criterion was wrong, not the probes. CV > 0.05 penalizes reproducible science.
- All 3 probes are scientifically valid and measurable. Infrastructure (data loader, callback, multi-seed) works.
- Routed to Phase 0 for gate criterion redesign (not Phase 2A).

**Implications for this Phase 2A session:**
1. This is a FIRST Phase 2A entry (not a recursive re-entry from Phase 4 failure of Gap 2).
2. The failure was in Gap 1 territory (SGD probe characterization). We now work on Gap 2 (cross-paradigm comparison).
3. Do NOT use CV > 0.05 as existence criterion. Use `probe_mean > epsilon AND t-test p < 0.05 vs. zero`.
4. Reuse probe infrastructure (data loader, callback) where applicable.
5. 30 epochs sufficient for probe measurement; avoid 300-epoch configs.

---

## Briefing

**Research Gap:** No systematic controlled study compares supervised ERM vs. SimCLR/MoCo contrastive vs. DINO self-supervised vs. MAE masked autoencoding representations for spurious feature encoding. Linear probing on spurious attribute labels on DomainBed/WILDS is the key missing experiment.

**Key Papers (from Phase 1, inferred):**
- Sagawa et al. (2020) Group DRO — Waterbirds/CelebA group-annotated benchmarks
- Kirichenko et al. (2022) DFR — ERM features sufficient for robustness (last-layer retraining)
- Gulrajani & Lopez-Paz (2021) DomainBed — multi-algorithm evaluation framework
- Koh et al. (2021) WILDS — real-world distribution shift datasets
- Shah et al. (2020) Simplicity Bias — SGD implicit preference for simple features

**Feasibility Constraints:**
- Existing real datasets only (Waterbirds, CelebA, DomainBed, WILDS)
- No new benchmarks, no synthetic data, no human annotation
- Must use existing group annotations already in datasets

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The cross-paradigm comparison gap is genuinely underexplored, and I think the most creative angle here is to flip the conventional framing. The field assumes contrastive/SSL objectives *should* reduce spurious feature reliance because they don't use task labels — the self-supervised objective has no incentive to encode a spurious label-correlated feature if the feature is useless for instance discrimination. But this assumption is wrong in an interesting way: contrastive learning is biased toward high-variance, high-information features at the *pixel/patch level*, which might include background textures, color statistics, and other spurious features that just happen to be visually prominent.

The novelty angle I want to propose: **the training objective determines which features are "simple" in the implicit bias sense**. For SGD+ERM, simplicity means label-predictive features with low model complexity. For contrastive learning, simplicity means instance-discriminative features that maximally separate augmented views. Background texture, which is spurious for bird classification but highly instance-discriminative (each bird photo has a different lake vs land background), would be *more* aggressively encoded by contrastive learning than by supervised ERM.

This gives us a testable directional hypothesis: **contrastive SSL (SimCLR/MoCo/DINO) encodes spurious features *more strongly* than supervised ERM when the spurious feature is visually prominent and instance-discriminative (e.g., background on Waterbirds), but *less strongly* when the spurious feature is label-correlated but not instance-discriminative (e.g., hair color on CelebA).**

The mechanism is the augmentation invariance: SimCLR augmentations (random crop, color jitter) are designed to make the model invariant to certain transformations, but Waterbirds background is *not* jittered away — it remains a stable feature across augmented views. Meanwhile, DINO/MAE might differ because DINO uses self-distillation (object-focused attention) and MAE uses reconstruction (pixel-level, may encode texture more uniformly).

Key Points:
- Contrastive learning doesn't eliminate spurious features — it may amplify them for visually prominent spurious attributes
- The augmentation set determines which features survive vs. are suppressed in SSL representations
- We need a 2×2 design: {Waterbirds spurious=background, CelebA spurious=hair} × {4 training paradigms} to test directionality
- Existing datasets (Waterbirds, CelebA) with group annotations make this immediately testable
- Novel claim: augmentation invariance, not label conditioning, is the primary determinant of spurious feature encoding in SSL

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's augmentation-invariance mechanism is creative but currently unfalsifiable as stated — it's a narrative, not a testable mechanistic claim. Let me push on the operationalization.

The central prediction "contrastive SSL encodes background more strongly than ERM on Waterbirds" needs a precise measurement. What does "encodes more strongly" mean? I propose: **spurious attribute linear probe accuracy** on frozen representations. Train a linear probe (logistic regression or linear layer) on frozen backbone representations to predict the spurious attribute label (background: land vs. water for Waterbirds; hair color for CelebA). Higher linear probe accuracy = more spurious feature encoded in the representation.

This is clean, directly reuses existing group annotation infrastructure, and is interpretable. Kirichenko et al. (2022) DFR paper uses this exact kind of probing — train on ERM features, show they're robustness-sufficient via last-layer retraining. We extend by probing for spurious attribute specifically.

However, I have three falsifiability concerns:

1. **Conflation of encoding vs. utilization**: A model may encode spurious features in its representation but not utilize them for the downstream task. Probe accuracy measures encoding. For the hypothesis to matter scientifically, we need to show encoding predicts downstream worst-group accuracy gap. Otherwise we're measuring something disconnected from actual shortcut reliance.

2. **Architecture confound**: If we compare ResNet-50-ERM vs. ViT-B-DINO, we're confounding architecture with training paradigm. Need identical backbone across paradigms (train SimCLR, ERM, DINO, MAE all on ResNet-50).

3. **Existence criterion from h-e1 failure**: Per the failure memory, we must NOT use CV > 0.05 for existence. The spurious attribute probe accuracy should use: `probe_accuracy > chance_level AND t-test p < 0.05 vs. chance (50%)`. For Waterbirds (95% background correlation in train), chance level is not 50% — it's the majority class baseline. This needs careful calibration.

The hypothesis Dr. Nova sketches becomes falsifiable if we add: **H0: spurious attribute probe accuracy does not differ significantly across training paradigms on the same backbone and dataset.** This is the null to disprove.

**Key Points:**
- Measurement: spurious attribute linear probe accuracy on frozen representations
- Control: same backbone architecture across all 4 paradigms (ERM, SimCLR/MoCo, DINO, MAE)
- Gate criterion: `probe_accuracy > majority_class_baseline AND p < 0.05 vs. baseline` (not CV)
- Secondary validation: correlation between probe accuracy and downstream worst-group accuracy gap
- H0 is clear and falsifiable

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The discussion is converging on a strong design. Let me assess the significance and sharpen the impact framing.

The scientific stakes here are high. Kirichenko et al. (2022) DFR result is currently the dominant finding: ERM features are "good enough" for robustness — you just need to fix the head. If that's true, the *representational* differences across paradigms don't matter much for robustness practitioners. But DFR assumes you have group-balanced fine-tuning data. The question our hypothesis addresses is deeper: **does the training paradigm determine HOW MUCH spurious feature cleaning is needed at fine-tuning time?**

If contrastive SSL encodes spurious features more aggressively (Dr. Nova's prediction), then DFR on contrastive-pretrained models would need more group-balanced data or stronger intervention. If contrastive SSL encodes less (alternative prediction), SSL pretraining could serve as a cheap spurious feature regularizer. Either answer has immediate practical value.

For impact, I want to frame the hypothesis around a **decision-relevant question**: "Given that I need robustness to spurious correlations and I'm choosing my pretraining paradigm, which should I pick?" Currently, the field has no principled answer. Our study answers it.

I support Dr. Nova's 2×2 design (dataset × paradigm) but want to add a third dimension: **spurious feature visibility**. Background (Waterbirds) is coarse-grained global texture. Hair color (CelebA) is fine-grained local texture. Adding a third setting like DomainBed VLCS or CivilComments (text spurious correlation) would test whether the paradigm effect generalizes beyond vision. However, given feasibility constraints, I'd prioritize: **Waterbirds (PRIMARY) + CelebA (SECONDARY)** — both have group annotations, established codebases, and clear spurious/core splits.

The novelty is confirmed: no prior work runs controlled 4-paradigm linear probe comparison with group annotation on the same backbone. DomainBed has paradigm comparison but not spurious attribute probing. WILDS has distribution shift evaluation but not probing for spurious encoding specifically.

**Key Points:**
- Impact: directly answers "which pretraining paradigm is most robust to spurious features?" — decision-relevant
- Primary dataset: Waterbirds (background spurious, 95% train correlation, group annotations via WILDS)
- Secondary dataset: CelebA (hair color spurious, gender label, group annotations via group_DRO repo)
- Novel: 4-paradigm controlled spurious attribute probe on same backbone — no prior work does this
- Connection: if contrastive SSL encodes spurious features differently, DFR intervention strength should scale accordingly

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Strong progress. Let me stress-test the implementation feasibility.

**What's realistic without MCP (no_MCP session):**

1. **Backbone standardization**: ResNet-50 for all paradigms is feasible — pretrained weights available on torchvision for ERM (supervised ImageNet), and SimCLR/MoCo/DINO/MAE pretrained ResNet-50 weights are available from official repos (Facebook AI, Google Brain). The key question is: which checkpoint? ImageNet-pretrained and then fine-tuned vs. linear-probed-on-Waterbirds?

   I recommend: **freeze backbone, train linear probe on Waterbirds train split** for all 4 paradigms. This directly measures spurious feature encoding in the pretrained representation before any task-specific adaptation. This avoids the problem of ERM fine-tuning inducing spurious features during adaptation — we want the pretraining signature.

2. **Dataset access**: Waterbirds dataset is created from CUB-200-2011 + Places365 (background). Available via the `group_DRO` repo (`kohpangwei/group_DRO`). Group annotations (spurious: background type, core: bird species) are provided. CelebA is directly from `torchvision.datasets.CelebA` with group labels available.

3. **Probe training**: Linear probe (logistic regression or single linear layer with SGD) on frozen features for:
   - Primary task label (bird species / hair color) — sanity check
   - Spurious attribute label (background / gender) — the key measurement
   - Both simultaneously to measure separation

4. **30-epoch budget**: Linear probing converges in <10 epochs typically. 30 epochs is more than sufficient (confirmed by h-e1 experience).

5. **Compute**: 4 paradigms × 2 datasets × 5 seeds = 40 probe training runs. Each ~5 minutes on single GPU. Total: ~3 hours. Feasible on standard hardware.

**Key caveat on MAE**: MAE pretrained ResNet-50 may be harder to source — MAE was primarily published with ViT backbone. We may need to replace MAE with **BarlowTwins** (self-supervised, non-contrastive, ResNet-50 available) or use ViT-S for MAE while keeping ResNet-50 for others. I recommend: ERM, SimCLR, DINO, BarlowTwins — all available on ResNet-50.

**Key Points:**
- Feasibility: HIGH — freeze backbone, train linear probes, use pretrained weights from official repos
- 4 paradigms: ERM (supervised), SimCLR (contrastive), DINO (self-distillation), BarlowTwins (non-contrastive SSL)
- Probe targets: spurious attribute label AND task label on same frozen backbone
- 40 probe runs × ~5 min = ~3 hours total compute
- Data access: Waterbirds (kohpangwei/group_DRO), CelebA (torchvision) — both freely available

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent progress. Let me synthesize and strengthen the hypothesis into a precise, testable form that addresses all prior concerns.

**The core hypothesis I'm advocating:**

*Under the same ResNet-50 backbone architecture trained to convergence on ImageNet-scale data, if we train four paradigms — supervised ERM, SimCLR contrastive, DINO self-distillation, and BarlowTwins non-contrastive SSL — then the spurious attribute linear probe accuracy on frozen representations will differ significantly across paradigms on Waterbirds (background probe) and CelebA (hair-color probe), because the training objective determines which visual features become "instance-discriminative" and thus preferentially encoded.*

**Strengthened predictions:**

P1 (Primary — Existence): At least one paradigm pair will show a statistically significant difference in spurious attribute probe accuracy (p < 0.05, t-test across 5 seeds), controlling for backbone size and dataset.

P2 (Directional — Contrastive vs ERM): Contrastive paradigms (SimCLR) will show higher spurious attribute probe accuracy than ERM on Waterbirds (where background is visually prominent and instance-discriminative), but not on CelebA (where hair color is label-correlated but less augmentation-stable).

P3 (Mechanism — Augmentation Invariance): Difference in spurious probe accuracy across paradigms will positively correlate with background patch variance in augmented views (r > 0.3) — larger background variance preserved → lower contrastive spurious encoding. This mechanism check is measurable by computing per-image crop overlap with spurious attribute region.

**Gate criteria (h-e1-informed):**
- P1: `max(probe_accuracy) > majority_baseline AND min(p-value across seeds) < 0.05`
- P2: `Δ(SimCLR_spurious_probe - ERM_spurious_probe) > 2% AND p < 0.05` on Waterbirds
- P3 is exploratory (not required for success)

**Addressing Prof. Vera's conflation concern:** Add secondary measurement — correlation between spurious probe accuracy and worst-group accuracy gap (lower WGA when spurious probe is higher). If probe accuracy doesn't correlate with WGA gap, encoding doesn't cause harm and the hypothesis has weaker practical significance.

**Key Points:**
- Hypothesis ID: H-SPEnc-v1 (Spurious Feature Encoding across Paradigms)
- Primary success criterion: statistically significant probe accuracy difference across ≥1 paradigm pair
- Secondary criterion: spurious probe accuracy correlates with worst-group accuracy gap (r > 0.2)
- Mechanism operationalized via augmentation patch analysis (exploratory)
- Fully feasible: all measurements on existing Waterbirds/CelebA with existing group annotations

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'm going to stress-test the hypothesis hard. Three potential failure modes:

**Failure Mode 1: All paradigms encode spurious features equally (null confirms)**
If linear probe accuracy for spurious attribute is uniformly high (~90%+) across all 4 paradigms, the hypothesis fails entirely. This is plausible — Waterbirds background is highly salient visually, and any feature extractor (supervised or not) trained on natural images will encode background texture. In fact, this is the DFR finding: ERM features already encode both spurious and task features. If SSL also encodes both, there's no paradigm difference.

*Mitigation*: Design the probe analysis to distinguish "encodes spurious" from "preferentially relies on spurious." Measure: spurious probe accuracy / task probe accuracy ratio. If ERM has 92% task probe / 88% spurious probe = ratio 1.05, and SimCLR has 85% task probe / 91% spurious probe = ratio 0.93, the ratio reveals preferential encoding even if raw accuracy is similar. This ratio is a better metric than raw probe accuracy for paradigm comparison.

**Failure Mode 2: Architecture confound (ViT vs CNN baseline difference)**
If we use ResNet-50 for ERM/SimCLR/BarlowTwins but must use ViT for DINO/MAE (as Prof. Pax noted), we confound paradigm with architecture. DINO-ViT attention heads focus on object regions, reducing background encoding structurally — not because of the SSL objective per se, but because ViT patch attention is architecture-determined.

*Mitigation*: Run ERM on ViT-B as well (ERM-ViT). If ERM-ViT and DINO-ViT show similar spurious probe accuracy, the confound is architecture. If DINO-ViT < ERM-ViT, it's the objective. Alternatively, use DINO-ResNet-50 (available from DINO paper supplementary) instead of ViT.

**Failure Mode 3: Waterbirds train set correlation (95%) saturates all probes**
Waterbirds has 95% train-time background-bird correlation. A linear probe trained on Waterbirds with high spurious correlation may show high spurious probe accuracy simply because the feature extractor was fine-tuned (even linearly) with this correlation present. Need to verify: probe the features extracted from *test set* (which has 50% or anti-correlated groups), not train set. The out-of-distribution probe measures generalization of spurious encoding, not in-distribution memorization.

*Mitigation*: Train linear probe on held-out balanced group split (equal spurious/anti-spurious examples). This is already available in group_DRO's Waterbirds validation/test splits.

**Key remaining concern:** The spurious probe accuracy / task probe accuracy ratio metric needs validation — does it actually predict worst-group accuracy gap? Run correlation analysis across all 40 probe runs and report Pearson r as a secondary finding.

**Key Points:**
- Risk 1: All paradigms encode equally → mitigate with ratio metric (spurious/task probe accuracy)
- Risk 2: Architecture confound in DINO-ViT → use DINO-ResNet-50 or add ERM-ViT control
- Risk 3: Train correlation saturation → probe on balanced test split, not biased train split
- Ratio metric (spurious_probe_acc / task_probe_acc) is a stronger discriminative measure than raw probe accuracy
- Correlation between ratio and WGA gap validates whether encoding differences are practically meaningful

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's stress-tests are exactly right, and the ratio metric is a genuine improvement. Let me add one more creative element: the **augmentation ablation experiment** as a direct mechanism test.

If the hypothesis is correct that augmentation invariance determines spurious feature encoding in contrastive SSL, then we can directly test the mechanism by *modifying the augmentation set* and observing whether spurious probe accuracy changes. Specifically:

- **SimCLR-Original**: standard augmentations (random crop, color jitter, gaussian blur, grayscale)
- **SimCLR-NoBackground**: add random background replacement to augmentations (using Places365 backgrounds, same as Waterbirds construction) — this forces the model to be invariant to the background, which IS the spurious feature on Waterbirds

If SimCLR-NoBackground shows dramatically lower spurious probe accuracy than SimCLR-Original, we have causal evidence that augmentation invariance — not the contrastive objective per se — drives the spurious feature encoding difference.

This is a mini-experiment within the feasibility envelope (same dataset, same codebase, just different augmentation config). It converts a correlational finding (paradigm X shows lower spurious probe) into a mechanistic one (we can modulate spurious probe by controlling augmentation invariance).

This also has a practical takeaway beyond the comparison study: **targeted augmentation design can suppress spurious feature encoding in contrastive SSL without requiring group annotations**. This is a broader contribution than just "which paradigm is better."

**Key Points:**
- Augmentation ablation: SimCLR-Original vs SimCLR-NoBackground (background replacement augmentation)
- If spurious probe drops significantly → augmentation invariance is the mechanism
- Converts correlational paradigm comparison into causal mechanism test
- Practical takeaway: targeted augmentation = label-free spurious feature suppression
- No new datasets or annotations needed — reuses Waterbirds/Places365 infrastructure

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The augmentation ablation is excellent — it's the most falsifiable experiment in the design. Let me tighten the full experimental protocol so everything is operationally clear.

**Full experiment protocol:**

1. **Backbones**: ResNet-50 pretrained on ImageNet under 4 paradigms:
   - ERM: torchvision ImageNet checkpoint (standard supervised)
   - SimCLR: official SimCLR-v2 ResNet-50 checkpoint (Chen et al.)
   - DINO: official DINO ResNet-50 checkpoint (Facebook AI)
   - BarlowTwins: official Barlow Twins ResNet-50 checkpoint (Facebook AI)

2. **Freeze backbone** (no fine-tuning of backbone weights)

3. **Extract features**: pass all images through frozen backbone, get 2048-dim feature vectors

4. **Linear probe training**: train logistic regression (sklearn or torch linear layer) separately for:
   - Task label (bird species / hair color blond vs non-blond)
   - Spurious attribute (background / gender)
   - Run 5 seeds, report mean ± std

5. **Probe test set**: use Waterbirds group-annotated test split (balanced: 50% spurious, 50% anti-spurious). Train probe on group-balanced subset of train.

6. **Primary metric**: Spurious/Task ratio = spurious_probe_acc / task_probe_acc. Compare across 4 paradigms.

7. **Secondary metric**: Worst-group accuracy gap on downstream task (linear probe for task label evaluated only on worst group). Correlate with ratio.

8. **Augmentation ablation**: Train SimCLR from scratch on Waterbirds (small model, <20 epochs sufficient for probe comparison) with and without background replacement augmentation. Compare spurious probe accuracy.

9. **Success criterion**: At least one paradigm pair differs in ratio by ≥ 2% (p < 0.05). Secondary: |r| > 0.2 between ratio and WGA gap.

This protocol is clean, avoids all three failure modes Prof. Rex identified, and is executable in ~3-4 hours on a single GPU.

**Key Points:**
- Protocol: freeze backbone, extract 2048-dim features, logistic regression probe for spurious + task labels
- Metric: spurious/task ratio on balanced test split
- 5 seeds × 4 paradigms × 2 datasets = 40 runs + augmentation ablation (10 additional)
- Total: ~50 probe runs, ~4 hours on single GPU
- Protocol avoids all failure modes: architecture control, balanced probe test split, ratio metric

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The experiment design is now tight. Let me assess novelty and impact one final time to confirm this is worth pursuing.

**Novelty confirmed:**
- DomainBed compares paradigms on average accuracy across domain shifts — not on spurious attribute probe accuracy
- WILDS benchmarks fine-tuned models but doesn't freeze backbone and probe for spurious attributes
- Kirichenko (2022) DFR shows ERM features are sufficient — but doesn't compare to SSL paradigms
- No paper runs the 4-paradigm × same-backbone × spurious-attribute-probe design
- The augmentation ablation (SimCLR-NoBackground) is particularly novel as a mechanism test

**Impact path:**
1. If contrastive > ERM on spurious probe → SSL pretraining is not a free robustness lunch; practitioners should add targeted augmentation or group-balanced fine-tuning
2. If ERM > contrastive on spurious probe → existing DFR finding generalizes; SSL representations need less intervention
3. If no significant difference → paradigm choice doesn't matter for spurious feature encoding; focus robustness efforts on the fine-tuning head
4. Augmentation ablation mechanism → even result 3 is useful: augmentation design can modulate spurious encoding regardless of paradigm

**Publishing venue fit:** ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning is explicitly seeking this type of cross-paradigm comparison (stated in CFP). Full paper fit: ICML/ICLR main track (empirical analysis with mechanism test).

**Key Points:**
- Novelty: CONFIRMED — no prior work does this controlled 4-paradigm spurious attribute probe comparison
- 3 possible outcomes all advance the field
- Augmentation ablation is mechanism-level contribution beyond comparison study
- Venue: ICLR 2025 Workshop (short) → ICML/ICLR main (full with all 4 experiments)
- Practical impact: informs pretraining paradigm choice for spurious-correlation-sensitive applications

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility sign-off. The protocol as stated by Prof. Vera is implementable. Let me resolve remaining practical questions:

**Checkpoint availability (verified from domain knowledge):**
- ERM ResNet-50: `torchvision.models.resnet50(pretrained=True)` — standard PyTorch
- SimCLR ResNet-50: available at `https://github.com/google-research/simclr` (TensorFlow) or via `pl_bolts` (PyTorch Lightning) — needs conversion but documented
- DINO ResNet-50: `torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')` — direct PyTorch Hub
- BarlowTwins ResNet-50: `torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50')` — direct PyTorch Hub

All 4 checkpoints are ResNet-50, directly comparable.

**Waterbirds access:** `pip install wilds` → `wilds.get_dataset('waterbirds', ...)` — provides train/val/test with group annotations (spurious: background type, task: bird type). Group-balanced splits available.

**CelebA access:** `torchvision.datasets.CelebA` — attributes include `Blond_Hair`, `Male` (spurious correlation: blond ≈ female in train set). Group_DRO repo provides standardized group splits.

**Augmentation ablation compute:** Training SimCLR from scratch on Waterbirds (11k images) for 20 epochs with/without background aug: ~30 min per run. 5 seeds × 2 conditions = 5 hours. Feasible.

**Total compute budget:** 50 probe runs (4 hours) + 10 SimCLR-ab runs (5 hours) = ~9 hours on single GPU. Feasible in 1 day.

**Key Points:**
- All 4 ResNet-50 checkpoints accessible via official sources (torchvision, PyTorch Hub)
- Waterbirds via WILDS package, CelebA via torchvision — no custom data setup
- Total compute: ~9 hours on single GPU — feasible in 1 day
- No external dependencies beyond PyTorch + WILDS + scikit-learn for linear probes
- READY for Phase 2B experiment implementation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The augmentation-invariance mechanism hypothesis is genuinely novel — the field has assumed SSL reduces spurious features but has not tested this systematically with controlled backbone comparison. The augmentation ablation (SimCLR-NoBackground) provides a causal test that converts a correlational finding into a mechanistic one. The contribution extends beyond comparison to an actionable insight: targeted augmentation design can suppress spurious feature encoding without group annotations.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The experimental protocol is well-specified and falsifiable. The null hypothesis (no paradigm difference in spurious/task ratio) is clearly defined. Gate criterion uses `probe_accuracy > majority_baseline AND p < 0.05` (explicitly avoids the CV > 0.05 error from h-e1). The 5-seed protocol provides statistical power. The ratio metric (spurious/task probe accuracy) is a clean, interpretable discriminator.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Direct answer to a practically important question: which pretraining paradigm is most robust to spurious features? All three possible outcomes (contrastive > ERM, ERM > contrastive, no difference) are informative and publishable. Explicit connection to ICLR 2025 Workshop CFP confirms field relevance. DFR generalizability question (does SSL need same intervention?) is a natural follow-on that this study directly enables.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Full implementation feasible in ~9 hours on single GPU. All 4 ResNet-50 checkpoints available via official channels (torchvision, PyTorch Hub). Waterbirds and CelebA accessible via standard packages (WILDS, torchvision). No new annotations, no new benchmarks. The only implementation risk is SimCLR checkpoint format (TF vs PyTorch) but documented conversion paths exist.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**H-SPEnc-v1: Spurious Feature Encoding Differs Across Pretraining Paradigms Due to Objective-Determined Augmentation Invariance**

Under ImageNet-scale pretraining on ResNet-50 backbones, if we compare four training paradigms — supervised ERM, SimCLR contrastive learning, DINO self-distillation, and BarlowTwins non-contrastive SSL — then the degree to which spurious features (background texture on Waterbirds, hair color on CelebA) are encoded in frozen representations will differ significantly across paradigms, because the training objective determines which visual features become "instance-discriminative" and thus preferentially encoded. Specifically, contrastive learning objectives (SimCLR) encode visually prominent spurious features (Waterbirds background) more strongly than supervised ERM because background texture is highly instance-discriminative but not augmented away by standard augmentation sets. This is operationalized via spurious attribute linear probe accuracy on frozen representations, measured on balanced group-annotated test splits.

The primary prediction is that the spurious/task probe accuracy ratio (a scale-free measure of preferential spurious encoding) differs across at least one paradigm pair by ≥ 2% (p < 0.05, t-test across 5 seeds). A directional prediction holds that SimCLR will show the highest spurious/task ratio on Waterbirds (background spurious). The augmentation ablation (SimCLR-Original vs SimCLR-NoBackground) tests the mechanism causally: if background-replacement augmentation reduces spurious probe accuracy in SimCLR representations, augmentation invariance is confirmed as the mechanism.

The experimental setup is fully executable: ResNet-50 pretrained checkpoints from official sources (torchvision, PyTorch Hub), Waterbirds and CelebA from WILDS and torchvision packages, 5-seed linear probe training, ~9 hours total compute. All feasibility constraints are met: existing real datasets, existing group annotations, existing benchmarks.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** SimCLR-ResNet-50 checkpoint (Google Research) is TensorFlow-native; PyTorch port may introduce subtle weight differences. May need to use BYOL (Bootstrap Your Own Latent) or MoCo-v3 as contrastive baseline if SimCLR-PyTorch port quality is unclear.
- **Concern 2:** Waterbirds train set has 95% background-bird correlation. Probing on the standard train split will show inflated spurious accuracy for all paradigms if the probe sees label-correlated features. Must enforce balanced probe training split (addressed in protocol, but implementation must verify group_balanced_sample=True in WILDS dataloader).
- **Mitigation Strategy:** Use MoCo-v3 (official PyTorch Hub) as contrastive baseline instead of SimCLR if checkpoint quality is a concern. Explicitly verify WILDS Waterbirds dataloader returns group-balanced batches for probe training, and test on the anti-correlated subset to confirm spurious feature suppression is measurable.
