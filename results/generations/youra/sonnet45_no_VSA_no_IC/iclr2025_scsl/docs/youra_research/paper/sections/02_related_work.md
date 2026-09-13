# 2. Related Work

## 2.1 Spurious Correlation Benchmarks

**Waterbirds** [@sagawa2019distributionally] correlates bird species with background (waterbirds appear on water 90% of training samples). Standard ERM training achieves 95% average accuracy but 60% worst-group accuracy, demonstrating shortcut learning. **CelebA** [@liu2015faceattributes] exhibits gender-hair color correlation (blonde hair occurs predominantly in female training images). **Spawrious** [@lynch2023spawrious] provides synthetic benchmarks with controllable correlation rates (50%-95%).

These benchmarks demonstrate that spurious features harm minority group performance, but existing detection methods require knowing which feature is spurious. We address unknown spurious detection via gradient abnormality.

## 2.2 Robust Learning Methods

**GroupDRO** [@sagawa2019distributionally] minimizes worst-group loss via group annotations, achieving 80-85% WGA on Waterbirds (294 GitHub stars, widely reproduced). Requires explicit group membership during training.

**JTT** [@liu2021just] trains a two-stage model: (1) identify hard samples from initial ERM, (2) upsample and retrain. Achieves ~78% WGA on Waterbirds (72 GitHub stars). Requires no annotations but assumes initial model correctly identifies minority samples.

**SCER** [@park2025spurious] refines prototypes in embedding space to correct spurious predictions, reporting ~90% WGA (estimated, code unavailable for reproduction). Operates post-hoc and misses gradient-level training dynamics.

**Gap:** GroupDRO/JTT require annotations or two-stage training. SCER operates on embeddings, not gradients. We propose gradient-based detection + mitigation in a unified single-stage framework.

Table 1 summarizes key differences:

| Method | WGA (Waterbirds) | Requires Annotations? | Training Stages | Intervention Space |
|--------|------------------|----------------------|-----------------|-------------------|
| **GroupDRO** [@sagawa2019distributionally] | 80-85%* | Yes | Single | Loss reweighting |
| **JTT** [@liu2021just] | ~78%* | No | Two-stage | Sample upweighting |
| **SCER** [@park2025spurious] | ~90% (est.)* | No | Post-hoc | Embedding refinement |
| **Ours (PoC)** | 78% (MNIST)** | No | Single | Gradient regularization |

*Literature-reported ranges (Sagawa et al. 2019 report GroupDRO 80-85% across seeds, JTT 78% single-seed, SCER estimated from paper ~90%). **MNIST smoke test (1 seed, 2 epochs), not Waterbirds.

*Note: Our Waterbirds results pending real validation (synthetic only). MNIST PoC included for methodology demonstration.*

## 2.3 Gradient Attribution for Spurious Detection

**Grad-CAM** [@selvaraju2017grad] produces saliency maps via weighted activation gradients. Widely used for interpretability (10,000+ citations) but fails for unknown spurious: user must know where to look.

**Integrated Gradients** [@sundararajan2017axiomatic] computes attribution via path integral from baseline to input. Adebayo et al. (2022) [@adebayo2022post] showed via user study (109 cites) that practitioners cannot detect unknown spurious correlations using IG or Grad-CAM results. **Key insight:** Attribution explains *which* features matter (result interpretation), not *whether* the process is abnormal (mechanism detection).

**GAIA** (Gradient Abnormality for OOD) [@chen2023exploring] detects distribution shift via gradient zero-deflation (GAIA-Z) and channel variance (GAIA-A). Achieves FPR95 reduction of 45.41% on CIFAR100 for OOD detection (16 cites). Operates on gradient *process*, not *result*.

**SPROD** [@lee2025detecting] detects spurious-correlated OOD via prototype-based divergence (4 cites). Complements our approach (prototypes vs gradients).

**Gap:** GAIA applied to OOD only, not subpopulation shift. SPROD post-hoc detection only. Adebayo shows attribution fails for unknown spurious. We extend GAIA to minority group detection (subpopulation shift within ID distribution) and propose gradient regularization for mitigation.

## 2.4 Positioning Summary

Existing work addresses spurious correlations via (1) annotation-based reweighting (GroupDRO), (2) two-stage training (JTT), or (3) post-hoc embedding refinement (SCER). Attribution methods (Grad-CAM, IG) fail for unknown spurious [@adebayo2022post]. GAIA detects OOD via gradient abnormality but not minority groups.

**Our contribution:** Extend GAIA to subpopulation shift, validate spurious-conflict mechanism via synthetic causality tests, and propose spatial gradient regularization as annotation-free mitigation. Complements embedding-based methods (SCER) by operating on gradient space.
