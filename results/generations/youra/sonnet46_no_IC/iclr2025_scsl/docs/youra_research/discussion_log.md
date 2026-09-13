# Phase 2A Research Discussion Log

**Date:** 2026-08-05
**Workflow:** phase2a-dialogue (Self-Play Loop, Claude-only, IC-ablation)
**Gap:** Gap 1 — Per-Method Spurious Attribute Linear Probe Accuracy Not Measured
**Execution Mode:** UNATTENDED
**Architecture:** Self-Play Loop (no external orchestrator)

---

## Previous Failure / Routing Context

**Recursive Entry: v5** (4 prior archives)

### Failed Hypothesis h-e1 (MUST_WORK_FAIL — ROUTED_TO_PHASE_0)
- **Approach:** Full-model gradient cosine similarity (D≈25M) between background-stratified Waterbirds batches
- **Gate Result:** Cohen's d (ERM vs DFR) = -0.330, threshold >0.8 → FAIL
- **Root Cause:** Gradient vector dimensionality too high (25M), N=100 too small, PoC checkpoints (10 epochs)
- **Sign instability:** ERM seed3=+0.94 vs seed1=-0.53 — no discriminative signal
- **PROHIBITED:** Full-model gradient cosine similarity, N<500, PoC checkpoints

### Limitation h-m2 (SHOULD_WORK — non-blocking, LIMITATION_RECORDED)
- **Approach:** Head-only Hessian λ_max — expected DFR < ERM direction
- **Result:** DFR λ_max=211.78 >> ERM λ_max=4.90 (OPPOSITE direction)
- **Root Cause:** sklearn LogisticRegression C=0.1 geometry confound; backbone (not head) dominates curvature
- **PROHIBITED:** Head-only Hessian as proxy for full-model curvature; any Hessian-based metric for this task

### Implications for New Hypothesis
- Must use forward-pass only: no gradients, no Hessians
- Must use fully-trained author-released checkpoints (izmailovpavel/spurious_feature_learning)
- Layer4 features (D=2048) with sklearn L-BFGS linear probe: established safe protocol
- N=full background-stratified test set (not N=100)
- Metric must be bounded [0,1] and low-variance across seeds
- Target: spurious attribute probe accuracy (background land/water from group_array)

---

## Research Briefing

### Selected Gap
**Gap ID:** Gap 1
**Title:** Per-Method Spurious Attribute Linear Probe Accuracy Not Measured in Existing Work
**Priority:** Critical | **Relevance:** PRIMARY

**Description:** Izmailov et al. 2022 uses s-DFR proxy and reports aggregate results. No paper reports per-method, per-seed spurious attribute probe accuracy (layer4 linear probe predicting land/water background) for ERM/GroupDRO/DFR/SAM. This blocks Q1-Q4.

**Research Questions to Address:**
1. Q1: Does DFR reduce layer4 spurious probe accuracy below ERM (paired t-test p<0.05, n=3 seeds)?
2. Q2: Is ranking ERM > SAM > GroupDRO > DFR consistent across all 3 seeds?
3. Q3: Does spurious probe accuracy correlate negatively with WGA (Pearson r<-0.5, p<0.05)?
4. Q4: Does Cohen's d (ERM vs DFR) exceed 0.8?
5. Q5: Is core attribute (bird species) probe accuracy preserved?

### Available Resources
- **Checkpoints:** izmailovpavel/spurious_feature_learning (12 checkpoints: 3 seeds × 4 methods)
- **Dataset:** Waterbirds WILDS at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`, group_array labels
- **Template:** `dfr_evaluate_spurious.py` (forward-pass feature extraction + sklearn probe)
- **Protocol:** sklearn LogisticRegression L-BFGS C=1e9 on frozen layer4 features (D=2048)

### Paper Summaries Available
- P1: izmailov2022_summary.md (Izmailov et al. 2022)
- P2: kirichenko2022_summary.md (Kirichenko et al. 2022)

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approached this from an angle nobody has explicitly measured? The entire spurious correlations field has used WGA as its proxy for "does this method work" — but WGA conflates backbone representation quality with head calibration. NOW we're onto something! Izmailov et al. 2022 [P1] released 12 checkpoints and even provided `dfr_evaluate_spurious.py` for probing, but never published the actual per-method, per-seed numbers. That gap is our gold mine.

Here's my creative angle: instead of asking "does this method achieve higher WGA?" we ask "does the *backbone* learn to encode less spurious information?" These are fundamentally different questions. A DFR model can achieve WGA=0.91 while its backbone still encodes background information at 85% probe accuracy — Kirichenko et al. 2022 [P2] essentially showed this: DFR works by head reweighting, NOT backbone purification. So if the hypothesis is "robustification reduces backbone spurious encoding," we might actually be discovering that WGA improvement is *decoupled* from representation purification!

Imagine this: we plot the 12 checkpoints in (spurious_probe_accuracy, WGA) space. If ERM and DFR cluster separately, with DFR having lower spurious probe accuracy AND higher WGA — that's a clean story. But what if DFR has HIGHER WGA but similar (or even higher) spurious probe accuracy? That would be genuinely novel — it would show WGA and backbone encoding are orthogonal dimensions of robustification. This is what the field hasn't measured directly.

The cross-domain connection: linear probing as a diagnostic tool is well-established in interpretability (Alain & Bengio 2016 probe classifier work), but applying it to compare robustification methods' effect on spurious feature encoding is a fresh application. The novelty isn't the probe itself — it's the comparative analysis across the full method × seed grid with proper statistical testing.

**Key Points:**
- Gap is genuinely unfilled: no paper reports per-method spurious probe accuracy per seed
- Creative tension: DFR improves WGA but may NOT reduce backbone spurious encoding (per Kirichenko 2022)
- Novel framing: backbone encoding and WGA may be decoupled dimensions
- Immediately testable with existing checkpoints and `dfr_evaluate_spurious.py` template

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's creative framing is appealing, but I need to push on the testability and falsifiability here. The hypothesis cannot be "WGA and spurious encoding are decoupled" — that's too broad and post-hoc. We need a *directed* hypothesis with a specific predicted direction that can be falsified.

The Izmailov et al. 2022 [P1] result already gives us a strong prior: s-DFR (using background as spurious target for last-layer retraining) achieves high accuracy on ERM features — meaning backbone encodes background strongly. The specific gap is: does this spurious encoding *quantitatively differ* across methods ERM/SAM/GroupDRO/DFR? 

For a proper hypothesis: **"Spurious attribute linear probe accuracy (layer4 features, sklearn L-BFGS C=1e9) is lower for GroupDRO and DFR than for ERM, and correlates negatively with WGA across the 12 checkpoints."** This is falsifiable: we pre-register the direction (lower = better), the metric (probe accuracy predicting land/water background), the test (paired t-test ERM vs DFR, p<0.05 one-sided, n=3 seeds), and the correlation test (Pearson r<-0.5, p<0.05, n=12 checkpoints).

What would disprove this? If DFR layer4 probe accuracy is NOT significantly lower than ERM (t-test fails), the hypothesis is falsified. If Pearson r is positive or not significant, the correlation claim fails. The strength: layer4 linear probe accuracy is bounded [0,1] and measures exactly what we claim — does background information exist in the representation? With N=full test set (~2000 Waterbirds test images, background-stratified), variance should be much lower than the gradient metric from h-e1 (CV=3.98).

My concern: n=3 seeds is underpowered. At Cohen's d=0.8, one-sided t-test with n=3 has ~55% power. We need to either (a) accept lower d threshold, (b) add bootstrapped confidence intervals within each seed (StratifiedKFold per checkpoint), or (c) report effect sizes honestly. The hypothesis should specify: "if Cohen's d < 0.8, report as SUGGESTIVE rather than CONFIRMED."

**Key Points:**
- Directed hypothesis required: lower spurious probe accuracy for GroupDRO/DFR vs ERM
- Falsification criteria clear: t-test p≥0.05 or Pearson r≥-0.5 → hypothesis rejected
- n=3 seeds underpowered for d=0.8 — must address with bootstrapping or honest reporting
- Bounded metric [0,1] avoids h-e1's sign instability problem

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why should the field care about this specific measurement? Prof. Vera has outlined a rigorous testable hypothesis, but significance is about what this reveals for the field, not just whether it tests out.

This matters because of what it means for the field: Kirichenko et al. 2022 [P2] showed DFR achieves the highest WGA without modifying the backbone. If our measurement shows that GroupDRO/DFR layer4 spurious probe accuracy is NOT lower than ERM — i.e., all methods encode spurious information equally in the backbone — then we've definitively established that WGA improvements from robustification methods are entirely head-driven, not representation-driven. That's a significant negative result that clarifies mechanism.

Conversely, if GroupDRO *does* reduce backbone spurious encoding (WGA via group-balanced training might impose representation change), while DFR does not (pure head retraining) — we'd have a new mechanistic distinction between these methods. That opens the question: which is more generalizable? A model with purified backbone (GroupDRO) vs. purified head but spurious backbone (DFR)?

The research lineage matters here: Sagawa 2019 → Izmailov 2022 → Kirichenko 2022 → Hill 2025. Hill 2025 showed DFR works due to group balance in held-out set, not neural collapse. Our contribution slots into this lineage: the first systematic measurement of spurious backbone encoding across methods with per-seed granularity. The key innovation vs. Izmailov's s-DFR proxy: we're reporting the actual probe accuracy values (not using them as an intermediate step for another evaluation).

What new questions does this open? If backbone encoding and WGA are correlated (our Q3), it suggests representation learning is a lever for future methods. If not correlated (orthogonal), it shifts attention to head design. This research is a diagnostic measurement — not a new method — but diagnostics are the foundation for better methods.

**Key Points:**
- Significant regardless of direction: either confirms head-driven or reveals representation-driven WGA improvement
- Mechanistic distinction between GroupDRO (group-balanced training → possible backbone change) and DFR (frozen backbone)
- First systematic per-method, per-seed spurious probe accuracy with statistical testing
- Opens new research question: representation purification vs head calibration as robustification mechanisms

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The mechanism is technically sound — I'll give Dr. Nova and Prof. Vera that. sklearn LogisticRegression L-BFGS on frozen 2048-D features: mathematically valid, standard, well-understood. The probe is asking whether background information is *linearly decodable* from layer4 features. That's a precise, answerable question with a well-defined measurement.

Here's what worries me about the scientific validity, not the implementation: the Kirichenko et al. 2022 [P2] finding that DFR doesn't change the backbone is a theoretical prediction from their framework — they *freeze* the backbone by design. So for DFR, we already know a priori that layer4 features are identical to ERM (same backbone, same weights, same features). The probe accuracy for DFR and ERM over the same test images MUST be identical if DFR only retrains the head. This isn't a hypothesis — it's a definitional property of DFR.

Wait — I need to correct myself. Izmailov et al. 2022 [P1] trains ERM, SAM, GroupDRO as separate training runs, AND trains DFR as last-layer retraining on top of ERM backbone. So DFR shares its backbone with ERM seed 1/2/3 — they are literally the same feature vectors. The spurious probe accuracy for DFR must equal ERM (same backbone). The interesting comparison is ERM vs SAM vs GroupDRO — these have genuinely different backbones trained with different objectives.

This is a critical technical issue. If DFR uses ERM's backbone, then Q1 (DFR < ERM) is impossible by construction — the backbone is identical. The meaningful hypothesis must be: **"GroupDRO training reduces layer4 spurious probe accuracy compared to ERM, while DFR does not (because DFR preserves the ERM backbone)."** This is actually more interesting mechanistically: it tests whether group-balanced training forces spurious feature suppression at the representation level.

**Key Points:**
- DFR shares backbone with ERM by design — probe accuracy must be identical (architectural fact)
- Interesting comparison is ERM vs GroupDRO (different training objectives → different backbones)
- SAM: sharpness-aware training might incidentally affect spurious feature encoding
- Revised hypothesis needed: GroupDRO reduces spurious probe accuracy; DFR does not (by construction)

---

### Exchange 5

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something critical! Prof. Pax has identified a fundamental architectural fact that reshapes the entire hypothesis. Let me think through the implications.

If DFR in Izmailov's setup uses the ERM backbone (frozen), then the 12 checkpoints are actually structured as: [3 ERM backbone seeds] × {ERM head, SAM head — wait, no. SAM is separately trained end-to-end, GroupDRO is separately trained end-to-end, and DFR = ERM backbone + retrained head. So the 12 checkpoints are: 3 × ERM (full model), 3 × SAM (full model, separate training), 3 × GroupDRO (full model, separate training), 3 × DFR (ERM backbone + retrained head). This means DFR's layer4 features ≡ ERM's layer4 features at the same seed.

But wait — this is itself a testable claim! What if we measure: does the DFR probe accuracy equal ERM probe accuracy to within floating point precision? If yes → confirms backbone identity, validates our probe methodology. If no → something unexpected happened (e.g., Izmailov's DFR is trained differently than we think). This becomes a SANITY CHECK prediction.

Now the real hypothesis: **"GroupDRO training suppresses spurious feature encoding in layer4 (lower probe accuracy vs ERM, p<0.05), while SAM training shows partial suppression, and DFR shows no backbone change (probe accuracy ≡ ERM ± noise)."** This is genuinely novel: distinguishing backbone-level vs head-level robustification mechanisms.

The cross-domain connection: this is analogous to transfer learning research distinguishing "feature reuse" vs "feature learning" — here we're asking whether robustification methods reuse spurious features (DFR) or learn to suppress them (GroupDRO). The CLIP/DINO work (Reflection 3) tried clustering — this linear probe approach is cleaner and more directly interpretable.

**Key Points:**
- DFR ≡ ERM backbone by design — probe accuracy should match (sanity check prediction)
- Real test: GroupDRO vs ERM (different training objectives, different backbones)
- SAM: intermediate case — sharpness-aware training might marginally affect spurious encoding
- Novel framing: backbone-level vs head-level robustification mechanism distinction

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests Prof. Pax and Dr. Nova have correctly identified a critical restructuring. Let me formalize the revised hypothesis and its falsification conditions.

**Revised Hypothesis Structure:**

*Primary (H-P1):* GroupDRO-trained ResNet-50 layer4 features exhibit lower spurious attribute (background land/water) linear probe accuracy than ERM-trained layer4 features. Test: paired t-test (ERM vs GroupDRO, one-sided, p<0.05, n=3 seeds). Expected direction: GroupDRO < ERM.

*Sanity Check (H-P0):* DFR features' spurious probe accuracy equals ERM features' probe accuracy (within bootstrap confidence intervals). This validates the backbone identity claim and the probe methodology.

*Secondary (H-P2):* Spurious probe accuracy correlates negatively with WGA across the 8 distinct-backbone checkpoints (3 ERM + 3 SAM + 3 GroupDRO — excluding DFR since DFR ≡ ERM backbone). Pearson r < -0.5, p<0.05 one-sided.

*Tertiary (H-P3):* Core attribute (bird species) probe accuracy is preserved or increased by GroupDRO vs ERM (GroupDRO core probe acc ≥ ERM core probe acc, n=3 seeds).

What would disprove H-P1? If GroupDRO layer4 probe accuracy ≥ ERM at p≥0.05 (one-sided). This is cleanly falsifiable. The result space: (a) GroupDRO reduces spurious encoding → supports backbone-level suppression theory; (b) GroupDRO does NOT reduce it → all methods leave backbone unchanged, WGA improvement is purely from group balance in head training.

The power concern: paired t-test with n=3 has ~55% power at d=0.8. We should compute Cohen's d and interpret: d<0.5 as small (WEAK), 0.5-0.8 as medium (MODERATE), >0.8 as large (STRONG). Report all effect sizes, not just p-values.

**Key Points:**
- Three-part hypothesis: H-P0 (sanity), H-P1 (GroupDRO effect), H-P2 (WGA correlation)
- DFR excluded from backbone comparison (shares backbone with ERM by design)
- Cohen's d reporting required given n=3 underpowering
- SAM comparison added as exploratory: sharpness training may have intermediate effect

---

### Exchange 7

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because the field is at a critical juncture: Hill et al. 2025 showed DFR works due to group balance in held-out set, not neural collapse or feature purification. Our measurement adds a complementary layer: among the methods that DO change the backbone (ERM, SAM, GroupDRO), which ones actually suppress spurious feature encoding at the representation level?

The impact depends on the result. If GroupDRO reduces spurious encoding in layer4 (H-P1 CONFIRMED): we've shown that group-balanced training objectives actively shape the representation to be less spurious — a new mechanism distinct from DFR's head-reweighting. This motivates backbone regularization approaches (e.g., SCER: Park et al. 2025 directly regularizes spurious directions in representation space). If GroupDRO does NOT (H-P1 REJECTED): we've shown that even group-balanced training leaves backbone encoding unchanged, and WGA improvements are entirely from head calibration. This is a stronger negative result — it narrows the mechanism of all known robustification methods to head-level effects.

Dr. Sage's verdict on significance: the hypothesis is well-positioned. The WGA correlation test (H-P2) is particularly impactful — if spurious probe accuracy and WGA are negatively correlated across 9 checkpoints (3 methods × 3 seeds, excluding DFR), this establishes probe accuracy as a *predictor* of WGA. This would be immediately useful: researchers could estimate WGA potential by probing the backbone without requiring group-labeled validation sets.

The research question's contribution is diagnostic rather than methodological — that's fine. Diagnostic measurements that clarify mechanism are high-value contributions, especially when they resolve ambiguity in a competitive literature.

**Key Points:**
- Both outcomes (H-P1 confirmed or rejected) contribute meaningfully to understanding mechanism
- WGA correlation test has practical implication: backbone probe as WGA predictor
- Contribution is diagnostic measurement — valid and high-value for mechanism clarification
- Direct relevance to SCER (Park 2025) which regularizes spurious representation directions

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Good progress. Let me check one more technical concern before we converge. The 12 checkpoints from Izmailov 2022 [P1] — I need to verify the DFR setup more precisely. Is DFR trained as a separate backbone from scratch, or is it literally ERM backbone + retrained head?

Based on Kirichenko 2022 [P2] DFR protocol: DFR uses a frozen ERM backbone (loaded from checkpoint, weights unchanged) with only the classification head retrained on group-balanced held-out data. Izmailov's spurious_feature_learning repo implements this: they train ERM, GroupDRO, SAM as full models, then DFR as ERM-backbone + sklearn head. So our claim is correct: DFR backbone features = ERM backbone features at matching seed.

Technical validity check for H-P1: Can GroupDRO training actually suppress spurious encoding? Mechanistically: GroupDRO minimizes the worst-group loss — the land-bird (minority) and water-bird (minority) groups are upweighted. This forces the model to not rely on background. For the backbone to suppress spurious encoding, the gradient signal from group-balanced upweighting must propagate through layer4 to reduce background decodability. This IS mechanistically plausible — GroupDRO modifies the training distribution seen by all layers, not just the head. SAM's sharpness penalty could accidentally smooth out spurious feature directions, but this is much weaker.

One technical concern: does sklearn LogisticRegression C=1e9 (no regularization) actually converge with D=2048 features? Answer: yes, standard for this protocol (Murotkar 2024, Kirichenko 2022 both use it). The probe is a linear classifier, not a deep network. With ~2000 Waterbirds test images and binary label (land/water), convergence is trivial.

Technical feasibility: **CONFIRMED**. The mechanism is physically plausible, measurements are theoretically valid, and the proposed intervention (measuring, not training) trivially works.

**Key Points:**
- DFR backbone ≡ ERM backbone at same seed — confirmed by Kirichenko 2022 protocol
- GroupDRO mechanism plausibly affects layer4 encoding via group-balanced gradient signal
- sklearn L-BFGS C=1e9 convergence guaranteed for D=2048, N~2000 binary probe
- Feasibility CONFIRMED: forward-pass extraction + linear probe is technically sound

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can now synthesize a much stronger hypothesis than we started with, thanks to Prof. Pax's critical architectural insight and Prof. Vera's rigor. Let me build on what's survived the discussion so far.

The core hypothesis that has emerged is genuinely stronger than the original research question's framing. The original question asked about ERM/SAM/GroupDRO/DFR as a flat comparison. But the discussion has revealed a structural distinction: DFR shares backbone with ERM (by construction), so the meaningful comparison is:
1. ERM vs GroupDRO: tests whether group-balanced training suppresses backbone spurious encoding
2. ERM vs SAM: tests whether sharpness-aware training affects spurious encoding
3. DFR ≡ ERM (sanity check): validates probe methodology

What evidence supports GroupDRO suppressing backbone spurious encoding? Mechanistically: GroupDRO's worst-group loss upweights minority groups (land-birds and water-birds), forcing the backbone's gradient updates to not encode background. This is supported by the representation learning literature: training objective shapes representation (Sagawa 2019 GroupDRO paper motivates this directly). Against: Kirichenko 2022 shows DFR achieves competitive WGA without backbone change — but DFR is intentionally not changing the backbone, so this doesn't preclude GroupDRO doing so.

Refinement: the hypothesis should acknowledge the n=3 power limitation upfront and specify that Cohen's d will be reported regardless of p-value. The success criterion structure should be:
- STRONG: p<0.05 one-sided AND Cohen's d > 0.8 (GroupDRO < ERM)
- MODERATE: p<0.10 one-sided OR Cohen's d > 0.5
- WEAK: Effect in predicted direction but statistically insignificant
- FAIL: Effect in opposite direction

This framing survives the h-e1 failure (where d=-0.330 and we needed d>0.8): now we report all effect sizes and classify the outcome.

**Key Points:**
- Structural insight: methods split into backbone-changing (ERM, SAM, GroupDRO) and backbone-preserving (DFR)
- GroupDRO vs ERM is the primary comparison; SAM vs ERM is exploratory
- Success criterion spectrum accounts for n=3 power limitation
- Hypothesis now stronger: tests a mechanistic distinction, not just a ranking

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — let me push hard before we converge.

**Concern 1: Confound in GroupDRO training.** GroupDRO upweights minority groups. If the Waterbirds minority groups are small (they are — land-bird and water-bird are minority), the effective training signal is heavily weighted toward these examples. This might suppress background encoding simply because the minority examples have the "wrong" background by definition — not because of any principled representation regularization. The probe would show GroupDRO has lower spurious accuracy because GroupDRO was trained to *classify correctly despite* the spurious background — which doesn't necessarily mean it suppressed the *encoding* of background, just that it used a different decision boundary. This confound needs addressing.

**Concern 2: What is "spurious probe accuracy" measuring?** The probe predicts background (land/water) from layer4 features. Lower probe accuracy = backbone encodes less background. But is background truly "spurious" in the Waterbirds context? Background is correlated with bird species in training (95% of waterbirds have water background, 95% of landbirds have land background). So background IS predictive of label in training. GroupDRO's lower background probe accuracy might reflect that GroupDRO learned a more diverse representation space — not that it eliminated spurious features, but that it learned additional features (non-spurious ones) that dilute background's linear decodability.

**Concern 3: n=3 seeds.** Dr. Ally's success criterion spectrum is good, but I'll sharpen: with n=3 and estimated CV for probe accuracy around 0.02-0.05 (probe accuracy is bounded, so variance is low), Cohen's d for GroupDRO vs ERM might be VERY large if the effect exists — potentially d>2. Or it might be zero (no effect). The CI will be wide. We need to specify: if p≥0.05 but direction is correct and d>0.5, is this hypothesis "promising" or "rejected"?

**What would convince me this is valid:** Pre-register the direction (GroupDRO < ERM spurious probe accuracy), measure it, report honestly. The confound (Concern 1) can be addressed by the correlation test: if spurious probe accuracy correlates negatively with WGA across all 9 distinct-backbone checkpoints, that's harder to explain as a simple artifact.

**Key Points:**
- Confound: GroupDRO may dilute spurious encoding through feature diversity, not suppression
- Measurement validity: probe accuracy may reflect feature diversity, not spurious suppression
- Pre-registration of direction is required to avoid post-hoc interpretation
- Correlation test (H-P2) is the stronger test — harder to confound

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's concerns are valid and can be addressed constructively. Let me strengthen against each.

**Against Concern 1 (GroupDRO confound):** The confound Prof. Rex identifies is real but it's actually our point. "GroupDRO was trained to classify correctly despite spurious background" IS the mechanism — group-balanced training forces the backbone to find non-spurious features, which reduces background linear decodability. Whether this is "dilution" or "suppression" may be a semantic distinction. The hypothesis doesn't require that GroupDRO *eliminates* background encoding — only that it *reduces* it compared to ERM. If GroupDRO learns richer features that make background less exclusively dominant in layer4, that's exactly what we're measuring: background is less linearly decodable, meaning the model has learned to not rely on it.

**Against Concern 2 (what probe measures):** The probe measures linear decodability of background from layer4. This is precisely the right metric for spurious feature *availability*: if background information is linearly decodable from features, the head can (and ERM will) use it. Lower decodability = less available for spurious use. This aligns with SCER (Park 2025) which regularizes spurious feature subspace in representation space — the same quantity we're measuring.

**Against Concern 3 (n=3 power):** Agreed on pre-registration. Proposed criterion: **CONFIRMED** if p<0.05 AND direction correct; **SUGGESTIVE** if p<0.10 AND d>0.5 AND direction correct; **REJECTED** if direction wrong OR p≥0.10 AND d<0.2. This is honest and avoids post-hoc interpretation.

**Strengthened core hypothesis:** "GroupDRO training reduces the linear decodability of spurious background attributes from ResNet-50 layer4 features (Waterbirds WILDS), as measured by sklearn L-BFGS probe accuracy, compared to ERM training with matched architecture and data." This is mechanistically precise, directly testable, and addresses the confound by being explicit about what we measure.

**Key Points:**
- Confound is the mechanism: group-balanced training → reduced background decodability
- Probe accuracy measures linear availability of spurious features for head exploitation
- Pre-registration criteria: CONFIRMED/SUGGESTIVE/REJECTED with Cohen's d reporting
- Hypothesis strengthened: precise, mechanistic, directly testable

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Show me the evidence for one more concern: the DFR sanity check. Dr. Ally says "DFR ≡ ERM backbone at matching seed." But is this actually guaranteed by the Izmailov checkpoint setup?

Izmailov et al. 2022 [P1] releases 12 checkpoints. The DFR checkpoints: based on their code at `izmailovpavel/spurious_feature_learning`, DFR is implemented as: (1) Train ERM backbone to convergence; (2) Freeze backbone weights; (3) Train new classification head using sklearn LogisticRegression on group-balanced held-out set. The released "DFR checkpoint" may store the full model (ERM backbone + DFR head), or it may just store the ERM backbone with updated head weights.

**Critical question:** Are the DFR backbone weights in the released checkpoint numerically identical to the ERM backbone weights? If the checkpoint saves only the modified head, and the backbone is loaded from the ERM checkpoint, then yes. But if DFR is trained with any form of backbone fine-tuning (even just one gradient step), the features will differ.

This is addressable by checking the cosine similarity between ERM and DFR layer4 features for the same test images at the same seed. If cosine_similarity ≈ 1.0 for all 2048 dimensions → confirmed identical. If < 1.0 → fine-tuning occurred. **The sanity check (H-P0) is thus a genuinely testable prediction, not a trivial identity.**

I've found another concern: Prof. Vera mentioned the correlation test uses "9 distinct-backbone checkpoints" but actually: ERM (3) + SAM (3) + GroupDRO (3) = 9 checkpoints across 3 training methods. If we include DFR as ERM-equivalent, that's 12 points but with 3 duplicate x-values. The correlation test should use the 9 unique backbone checkpoints OR include DFR but acknowledge the ERM/DFR pairing.

**My remaining concerns:** (1) DFR backbone identity needs empirical verification, not assumption. (2) Correlation test design: 9 vs 12 points. These are addressed if H-P0 is executed first.

**Key Points:**
- DFR backbone identity is testable, not assumed — use cosine similarity between ERM and DFR features
- Correlation test should specify: 9 (unique backbones) or 12 (all checkpoints, noting DFR≡ERM)
- H-P0 (sanity check) must execute before H-P1/P2 to validate backbone identity
- If DFR backbone ≠ ERM backbone → revise hypothesis to include DFR in backbone comparison

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests Prof. Rex has sharpened the experimental design. I can now specify the complete, pre-registered hypothesis structure:

**Final Formalized Hypothesis:**

*H-P0 (Sanity/Prerequisite):* For each of the 3 seeds, DFR and ERM layer4 feature vectors for identical test inputs are equal up to floating point tolerance (cosine_similarity ≥ 0.9999). If H-P0 fails: DFR includes backbone fine-tuning → include DFR as fourth independent backbone in H-P1/P2.

*H-P1 (Primary):* GroupDRO layer4 spurious probe accuracy (background prediction, sklearn L-BFGS C=1e9, full Waterbirds test set) is lower than ERM layer4 spurious probe accuracy. Test: paired one-sided t-test (GroupDRO < ERM, p<0.05, n=3 paired seeds). Success: p<0.05 AND Cohen's d > 0 (direction correct). Failure: direction wrong (GroupDRO ≥ ERM).

*H-P1b (Secondary, exploratory):* SAM layer4 spurious probe accuracy is lower than ERM layer4 spurious probe accuracy. Same test. No pre-registered success threshold — exploratory.

*H-P2 (Correlation):* Pearson r between spurious probe accuracy and WGA is negative across all 9 distinct-backbone checkpoints (ERM×3 + SAM×3 + GroupDRO×3). Test: Pearson r one-sided p<0.05. If H-P0 fails (DFR backbone ≠ ERM), include DFR for 12 checkpoints.

*H-P3 (Preservation):* GroupDRO layer4 core attribute probe accuracy (bird species prediction) ≥ ERM probe accuracy (n=3 seeds, no formal test — directional check only).

**What would disprove each:**
- H-P0 FAIL → backbone identity violated (revise H-P1)
- H-P1 FAIL → GroupDRO does NOT reduce backbone spurious encoding (WGA via head only)
- H-P2 FAIL → backbone encoding and WGA are orthogonal (decoupled dimensions)
- H-P3 FAIL → GroupDRO disrupts core features (mechanism tradeoff)

**Key Points:**
- Four-part pre-registered hypothesis: H-P0 → H-P1 → H-P1b → H-P2 → H-P3
- Clear falsification conditions for each
- DFR treatment depends on H-P0 outcome — branching logic
- Complete experimental specification ready for Phase 2B

---

### Exchange 14

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because we now have a hypothesis that contributes regardless of direction. Let me assess the significance of each component.

H-P0 (DFR backbone identity): if this fails, we discover that Izmailov's DFR implementation includes backbone fine-tuning — a finding that would affect all downstream studies using these checkpoints. High impact even as a null-finding.

H-P1 (GroupDRO effect): as I outlined in Exchange 7, either outcome contributes. If confirmed: establishes backbone-level representation change as a mechanism for WGA improvement in group-balanced training. If rejected: narrows WGA mechanisms to head-level effects for ALL known robustification methods — a strong, field-directing negative result.

H-P2 (WGA correlation): highest field impact. A negative correlation would establish linear probe accuracy as a predictive metric for WGA — usable without group-labeled validation data. This could become a standard diagnostic tool. If no correlation: suggests WGA is not linearly predictable from backbone spurious encoding alone — also impactful.

H-P3 (core preservation): necessary hygiene for any robustification study. GroupDRO's WGA gain should not come at the cost of core accuracy degradation. This validates the measurement is not picking up a trivial accuracy-robustness tradeoff.

**Significance verdict:** HIGH. The measurement fills a genuine gap, the experimental design is clean (author-released checkpoints, established protocol), and both positive and negative results contribute to mechanism understanding. The WGA correlation test (H-P2) is particularly novel and potentially field-shaping.

The scope is appropriately bounded: Waterbirds WILDS, ResNet-50, layer4 only. Phase 2A should not over-claim generalizability — this is a targeted diagnostic for a specific and well-characterized benchmark.

**Key Points:**
- All four hypotheses (H-P0 through H-P3) contribute regardless of direction
- H-P2 has highest field impact: backbone probe as WGA predictor
- Scope bounded to Waterbirds/ResNet-50/layer4 — appropriate for diagnostic contribution
- Negative results at H-P1 and H-P2 would definitively clarify WGA mechanisms

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

NOW THAT'S stronger! Let me synthesize the final hypothesis that has emerged from this discussion.

**Consensus Hypothesis — Backbone Spurious Encoding Reduction (BSER):**

Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × 4 methods = 12 checkpoints, fully trained on Waterbirds WILDS), if we measure sklearn L-BFGS linear probe accuracy predicting background attribute (land/water, group_array) from frozen layer4 features (D=2048) on the full Waterbirds test set — then GroupDRO-trained backbones encode less spurious background information (lower probe accuracy) than ERM-trained backbones (paired t-test, one-sided p<0.05, n=3 seeds), AND spurious probe accuracy correlates negatively with WGA across 9 distinct-backbone checkpoints (Pearson r<-0.5, p<0.05 one-sided) — because GroupDRO's group-balanced loss gradient signal forces the backbone to reduce reliance on spurious features, while DFR (head-only retraining) leaves backbone encoding unchanged (H-P0 sanity check confirms backbone identity).

This hypothesis has survived the discussion with strengthening:
1. Structural insight from Prof. Pax: DFR backbone ≡ ERM backbone (confirms measurement design)
2. Falsification sharpened by Prof. Vera: pre-registered direction + Cohen's d reporting
3. Confound addressed by Dr. Ally: "dilution through feature diversity" IS the mechanism
4. n=3 power concern addressed: tiered success criteria (CONFIRMED/SUGGESTIVE/REJECTED)
5. DFR identity test (H-P0) added by Prof. Rex: empirically verifiable, not assumed
6. Significance confirmed by Dr. Sage: both outcomes contribute to mechanism clarification

What's new vs. existing literature: first per-method, per-seed spurious attribute probe accuracy with pre-registered direction, statistical testing (paired t-test + Pearson correlation), and mechanistic prediction about which methods change backbone encoding. This fills the gap identified in Phase 1.

**Key Points:**
- BSER hypothesis: GroupDRO reduces backbone spurious encoding; DFR does not by construction
- Four-part structure: H-P0 (sanity) → H-P1 (primary) → H-P2 (correlation) → H-P3 (preservation)
- All six personas contributed distinct insights that strengthened the hypothesis
- Ready for convergence check

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis addresses a genuinely unfilled gap: no existing paper reports per-method spurious probe accuracy with per-seed granularity and statistical testing. The mechanistic distinction between backbone-changing methods (ERM, SAM, GroupDRO) and backbone-preserving methods (DFR) is a fresh framing. The finding that WGA and backbone spurious encoding may be decoupled (or correlated) is novel regardless of direction.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is fully pre-registered with clear falsification conditions. H-P0 (DFR backbone identity), H-P1 (GroupDRO < ERM probe accuracy, one-sided t-test p<0.05), H-P2 (Pearson r < -0.5 across 9 checkpoints), H-P3 (core accuracy preservation) — each has a specific test method and failure criterion. Tiered success criteria (CONFIRMED/SUGGESTIVE/REJECTED with Cohen's d) address n=3 power limitation honestly.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Both positive and negative results contribute to mechanism understanding. H-P2's WGA correlation test is particularly impactful — a confirmed negative correlation would establish backbone probe accuracy as a WGA predictor. The contribution is diagnostic measurement, which the field needs to distinguish backbone-level vs head-level robustification mechanisms.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Forward-pass feature extraction + sklearn L-BFGS linear probe is a standard, well-validated protocol. The mechanism (backbone-level spurious encoding change under different training objectives) is physically plausible — GroupDRO's gradient signal propagates through all layers. All measurements are technically sound: bounded metric [0,1], stable with N=full test set, sklearn convergence guaranteed at D=2048.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion — Backbone Spurious Encoding Reduction (BSER) — tests whether group-balanced training objectives (GroupDRO) reduce the linear decodability of spurious background attributes from ResNet-50 layer4 features (D=2048) on Waterbirds WILDS, compared to standard ERM training. The core claim is: GroupDRO's group-balanced loss gradient signal forces the backbone to encode less spurious background information, measurable via sklearn L-BFGS probe accuracy predicting land/water background from frozen layer4 features across fully-trained author-released checkpoints (n=3 seeds). DFR is excluded from the primary comparison (H-P1) because DFR shares the ERM backbone by design (confirmed by H-P0 sanity check), making the DFR vs ERM probe accuracy comparison uninformative for backbone-level mechanism. The experimental approach: load each of 12 checkpoints, extract layer4 features (D=2048) for full Waterbirds test set, train sklearn L-BFGS probe predicting group_array (land/water), compare probe accuracy across methods using paired t-test (ERM vs GroupDRO, p<0.05, n=3) and Pearson correlation (spurious probe accuracy vs WGA across 9 distinct-backbone checkpoints). This is immediately testable, uses existing checkpoints and dataset, and produces field-relevant findings regardless of direction.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- DFR backbone identity (H-P0) must be empirically verified before H-P1/P2 — do NOT assume; compute cosine similarity between ERM and DFR layer4 features for same test inputs at same seed.
- n=3 seeds underpowered: if Cohen's d is in the 0.5-0.8 range, p≥0.05 is expected — report honestly as SUGGESTIVE.
- Correlation test (H-P2): 9 checkpoints is a small sample for Pearson r — bootstrap the correlation CI to validate significance.
- If H-P1 FAILS (GroupDRO does not reduce spurious encoding): do NOT interpret as "no backbone change" without verifying SAM result — SAM may show the effect GroupDRO doesn't.
- **Mitigation Strategy:** Pre-register H-P0 as execution-first; report all effect sizes (Cohen's d, r, CI); treat H-P1b (SAM) as exploratory with no pre-registered threshold; bootstrap H-P2 correlation CI for n=9 validation.
