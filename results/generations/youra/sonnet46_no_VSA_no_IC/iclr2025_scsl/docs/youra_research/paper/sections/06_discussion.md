## 6. Discussion

### 6.1 Key Findings

**Finding 1: SSL shortcut encoding is severe and geometrically stable.**
The 73.4 pp WGA gap between DINO SSL (8.57%) and supervised training (81.93%) on Waterbirds is the primary empirical result of this work. More informative than the gap's magnitude is its stability: DINO's WGA does not improve as training progresses, despite converging average accuracy. This rules out the explanation that longer training would close the gap — the geometry of the SSL loss landscape fixes the shortcut at an early training stage and maintains it. This finding motivates the core proposition: if shortcut encoding is geometrically stable, the intervention must be geometric and must occur during pretraining.

**Finding 2: The average accuracy / WGA divergence is the diagnostic signature.**
DINO achieves 62% average accuracy and 8.6% WGA — a within-model gap of 53.5 pp. This divergence is larger than in any SSL model reported in the spurious correlation literature we surveyed. It suggests that DINO's self-distillation objective, combined with pretrained ViT-S/8 weights, is particularly effective at encoding background texture as a highly reliable predictor. Whether this is specific to ViT architectures or to the self-distillation loss will be resolved by the full 9-combination evaluation.

**Finding 3: The geometric hypothesis remains unverified but unmotivated.**
The sharpness anisotropy measurement (central to H-E1's mechanistic test) is pending the 200-epoch SimCLR/Waterbirds run. We can confirm the existence and severity of the SSL shortcut problem (RQ1 answered). We cannot yet confirm whether that problem is geometrically characterized by directional sharpness anisotropy (RQ2 pending), nor whether SAM during pretraining addresses it (RQ3 pending). This paper reports a partial result: the problem confirmation and the experimental protocol, with the mechanistic test ongoing.

### 6.2 Limitations

**Limitation 1: Anisotropy measurement pending.**
The core mechanistic claim — that SSL-SGD creates Hessian sharpness anisotropy along spurious feature directions — has not yet been empirically verified. The 10-epoch SimCLR fast run confirmed that SSL requires ≥100 epochs for meaningful feature development, and the full 200-epoch run is ongoing. This is the most significant limitation: the paper motivates and designs a geometric intervention without yet demonstrating the geometric phenomenon it seeks to address.

*Why acceptable:* The WGA gap data (73.4 pp) independently establishes that a geometric problem exists. The theoretical motivation (Gatmiry 2024, SCER 2025, G2-SAM 2025) is well-grounded. The measurement protocol is designed and validated at the code level. The full run is in progress.

**Limitation 2: Scope limited to DINO + Waterbirds.**
The confirmed results come from a single SSL method (DINO) on a single dataset (Waterbirds). The planned evaluation covers 9 combinations (3 SSL methods × 3 datasets). CelebA was excluded due to a WILDS download error (HTTP 500); CMNIST and MoCo-v2/SimCLR were excluded from the fast run due to speed constraints.

*Why acceptable:* Waterbirds is the canonical spurious correlation benchmark, and the 73.4 pp gap is large enough to be definitive for the existence question. The full 9-combination protocol is the intended evaluation scope.

**Limitation 3: Linear probe proxy precision/recall unvalidated.**
Assumption A2 — that the top-25% high-loss linear probe samples accurately identify spurious/minority group samples — has not been validated via precision/recall against held-out Waterbirds group labels. LFR [Ghaznavi 2023] validated an equivalent proxy in supervised ERM settings; transfer to SSL representations requires explicit verification.

*Mitigation:* Proxy precision/recall measurement is included in the full-run protocol and will be reported in the extended evaluation.

**Limitation 4: cuDNN disabled.**
Training was conducted with cuDNN disabled due to a torch+cu124 / CUDA 12.9 driver incompatibility. This slows training but does not affect numerical results.

**Limitation 5: SAM computational cost.**
SAM requires two forward-backward passes per batch (2× cost vs. SGD). For 200-epoch SSL pretraining on ResNet-50, this approximately doubles pretraining time. All results in this paper use SGD for pretraining; SAM-SSL results are pending.

### 6.3 Theoretical Implications

The central theoretical question this work raises — but cannot yet resolve — is whether Gatmiry et al.'s [2024] rank-1 simplicity bias result for supervised cross-entropy transfers to InfoNCE objectives. If it does, SAM would increase shortcut reliance in SSL (by promoting simpler/lower-rank features, which tend to be spurious). If the InfoNCE landscape prevents rank-1 dynamics (due to its uniform distribution pressure and multiple attractors), SAM's flattening effect would distribute more broadly and potentially reduce spurious anisotropy.

This is the key theoretical tension the anisotropy measurement will resolve. A finding that AR < 1.0 under SAM (SAM increases spurious anisotropy) would be a negative result of significant theoretical importance: it would demonstrate that the InfoNCE landscape responds to SAM differently than cross-entropy, with implications for all future geometry-aware SSL design.

### 6.4 Broader Impact

SSL pretraining is increasingly deployed in fairness-sensitive domains: medical image analysis, hiring, content moderation. If SSL representations systematically encode spurious correlations geometrically, practitioners relying on these representations — even with downstream fairness interventions — face a structural problem. This work provides both a diagnostic (anisotropy measurement) and a potential intervention (SAM during pretraining) that could be applied before downstream deployment.

The annotation-free design is critical for practical adoption: acquiring group labels is expensive and requires domain expertise that may be unavailable in deployment settings. A geometric intervention that requires only a linear probe and SAM perturbations can be applied without knowledge of the specific spurious features or group structure.
