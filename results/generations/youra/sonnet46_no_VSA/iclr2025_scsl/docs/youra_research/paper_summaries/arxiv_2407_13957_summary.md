---
source_paper: "arxiv_2407_13957.md"
generated_at: "2026-08-04T03:11:13.676733"
model: "openai/gpt-5.2"
summary_chars: 12808
---

# The Group Robustness is in the Details: Revisiting Finetuning under Spurious Correlations

## Key Metadata
- **Authors:** Tyler LaBonte et al.
- **Year:** 2024
- **Venue:** NeurIPS 2024
- **Core Contribution:** A systematic re-evaluation of how *finetuning details*—especially the specific class-balancing implementation and model scaling—govern worst-group accuracy under spurious correlations, revealing failure modes (collapse), proposing a simple “mixture” balancing fix, and diagnosing group disparities via feature-spectrum statistics.

## Section Summaries

### Abstract
Modern machine learning models are prone to over-reliance on spurious corre-
lations, which can often lead to poor performance on minority groups. In this
paper, we identify surprising and nuanced behavior of finetuned models on worst-
group accuracy via comprehensive experiments on four well-established bench-
marks across vision and language tasks. We first show that the commonly used
class-balancing techniques of mini-batch upsampling and loss upweighting can
induce a decrease in worst-group accuracy (WGA) with training epochs, leading
to performance no better than without class-balancing. While in some scenar-
ios, removing data to create a class-balanced subset is more effective, we show
this depends on group structure and propose a mixture method which can outper-
form both techniques. Next, we show that scaling pretrained models is generally
beneficial for worst-group accuracy, but only in conjunction with appropriate
class-balancing. Finally, we identify spectral imbalance in finetuning features
as a potential source of group disparities — minority group covariance matri-
ces incur a larger spectral norm than majority groups once conditioned on the
classes. Our results show more nuanced interactions of modern finetuned mod-
els with group robustness than was previously known. Our code is available at
https://github.com/tmlabonte/revisiting-finetuning.

### Introduction & Motivation
- The paper studies robustness to **spurious correlations** that are predictive in training but fail at test time, disproportionately harming **minority groups**; robustness is quantified via **worst-group accuracy (WGA)**, the minimum test accuracy across groups.  
- While many robustness methods exist when **group annotations** are available (and variants without them exist), the authors argue it remains unclear how much WGA behavior is driven simply by **finetuning details** within standard ERM pipelines.  
- They therefore revisit “plain finetuning” on four standard spurious-correlation benchmarks, focusing on two practical knobs: **class-balancing strategy** (which does *not* require group labels) and **model scaling** (overparameterization).  
- Key motivation: prior narratives about whether overparameterization “helps or hurts” robustness appear inconsistent; this work shows those conclusions can flip depending on *exact* balancing implementation and training-to-convergence choices.

### Methodology
The paper formalizes spurious-correlation benchmarks via **groups** defined as the Cartesian product of target class and spurious feature, \(G = Y \times S\). Each training index set \(\Omega_g\) (resp. \(\Omega_y\)) denotes samples in group \(g\) (resp. class \(y\)). The primary metric is **worst-group accuracy** (WGA): minimum test accuracy over all \(g \in G\). They also define *majority/minority groups within each class* to analyze within-class disparities.

They study **ERM finetuning** from pretrained checkpoints, varying only **class-balancing mechanics** and model size. Three class-balancing techniques (no group labels required) are compared:  
1) **Subsetting:** downsample each class to the smallest class (uniform random removal), fixed once pre-training.  
2) **Upsampling:** sample balanced-by-class minibatches in expectation by first sampling \(y \sim \mathrm{Unif}(Y)\), then \(x \sim \hat p(\cdot\mid y)\).  
3) **Upweighting:** scale the per-example loss by the class imbalance ratio: for loss \(\ell(f(x),y)\), use \(\gamma \ell(f(x),y)\) where \(\gamma\) is the class-imbalance ratio for minority-class samples (and \(1\) for majority-class samples). (They note upweighting is equivalent to upsampling **in expectation** over sampling.)

**Novel component (proposed): Mixture balancing.** To interpolate between subsetting and upsampling, they first create a *partially balanced* subset achieving a chosen class ratio (by removing from larger classes), then apply **class-balanced upsampling** *within that subset*. The ratio \(1{:}1\) recovers subsetting; using the original dataset ratio recovers upsampling. This is designed to increase majority-class exposure without repeatedly oversampling a tiny minority group, mitigating overfitting-driven WGA collapse.

**Training protocol (as reported in excerpt):** finetune with **AdamW**; run **3 independent seeds**; **no early stopping** (models are trained “to completion” to expose overfitting effects). They report that they finetune (examples): ConvNeXt-V2 Base to training loss \(\approx 10^{-4}\) on Waterbirds and \(\approx 10^{-3}\) on CelebA; BERT Base to \(\approx 10^{-3}\) on CivilComments and \(\approx 10^{-2}\) on MultiNLI. (Learning rate, batch size, epochs/steps, and scheduler are not specified in the provided excerpt; they are said to be in Appendix A.2.)

**Spectral diagnostic:** Using penultimate-layer features \(z_i\), they compute per-group empirical covariance
\[
\Sigma_g = \frac{1}{|\Omega_g|}\sum_{i\in\Omega_g}(z_i-\bar z_g)(z_i-\bar z_g)^\top,
\]
with eigendecomposition \(\Sigma_g = V_g \Lambda_g V_g^{-1}\) and eigenvalues \(\lambda_1^{(g)} \ge \lambda_2^{(g)} \ge \dots\). They propose an **intra-class spectral norm ratio** for each class \(y\):
\[
\rho(y) := \frac{\lambda_1^{(g_{\min}(y))}}{\lambda_1^{(g_{\maj}(y))}},
\]
where \(g_{\min}(y)\) and \(g_{\maj}(y)\) are the minority/majority groups *within class \(y\)*, to quantify within-class group spectral imbalance.

### Experiments & Results
**Benchmarks (4):**  
- **Waterbirds** (vision): class = landbird vs waterbird; spurious feature = background (land vs water). Class imbalance ratio **3.31:1**; additionally known train–test group proportion shift (they report average accuracy weighted by training group proportions per [50]).  
- **CelebA** (vision): class = blond vs non-blond; spurious feature = gender. Class imbalance ratio **5.71:1**.  
- **CivilComments** (language): class = toxic vs non-toxic; spurious feature = presence of identity categories (male/female/LGBT/black/white/Christian/Muslim/other religion collapsed into a single spurious feature variant); class imbalance ratio **7.85:1**.  
- **MultiNLI** (language): class = contradiction/entailment/neutral; spurious feature = negation in hypothesis; **class-balanced a priori**.

**Models:** ImageNet-1K pretrained **ResNet**, **ConvNeXt-V2**, **Swin Transformer** for vision; BookCorpus+Wikipedia pretrained **BERT** for language. Scaling experiments cover **3.4M–101M parameters** using multiple ConvNeXt-V2 and BERT sizes.

**Evaluation metrics:** primary **WGA**; also track **average test accuracy** (with Waterbirds weighting caveat). For model selection without group labels, they test **worst-class accuracy** [69] and a **bias-unsupervised validation score** [60].

**Main phenomena (class balancing):**  
- **Catastrophic collapse:** On the more class-imbalanced datasets **CelebA** and **CivilComments**, **class-balanced upsampling** and **loss upweighting** lead to **decreasing WGA over epochs** (collapse), eventually “no better than without class-balancing.” Their hypothesis: long training causes **overfitting to the minority group within the minority class** because individual examples get sampled/weighted too often. Early stopping can mitigate (not their main setting).  
- **Subsetting nuance:** Subsetting can *help* WGA when it increases minority-group proportion, but can *hurt* when it removes data from a **small minority group inside the majority class** (their canonical counterexample: Waterbirds’ landbird-on-water-background group).

**Proposed fix (mixture balancing):** Mixture balancing substantially reduces collapse and can outperform the three standard options, notably on Waterbirds and CivilComments (per the qualitative statements around Fig. 2), by trading off majority exposure vs minority over-repetition.

**Model scaling (with/without balancing):** Scaling pretrained models is *generally beneficial* for WGA **only with appropriate class-balancing**. Reported gains reach **up to 12% WGA** for “interpolating” models and **up to 40% WGA** for “non-interpolating” models (where interpolation refers to hitting 100% training accuracy). Scaling under class imbalance or the “wrong” balancing method can be neutral or harmful (CivilComments highlighted as most severe). They also replicate [46] and show conclusions about scaling can look “overly pessimistic” when class-balancing is omitted.

**Spectral results:** Even after class-balancing with the best method per dataset, they observe that the **largest eigenvalue** \(\lambda_1^{(g)}\) often belongs to a **minority group**, and that **minority-group spectra are larger than majority-group spectra within the same class**. The intra-class ratio \(\rho(y)\) is reported as **\(\ge 1\)** for essentially all classes/datasets (with one noted exception for one seed/class on CelebA), and the class with largest \(\rho(y)\) often aligns with the class showing largest within-class accuracy gap.

**Compact table of explicitly reported numbers (from provided excerpt):**

| Dataset | Model selection metric (no group labels unless noted) | Selected balancing method | Test WGA (avg over 3 seeds) |
|---|---|---:|---:|
| Waterbirds | Bias-unsupervised score [60] | Upsampling | 79.9 |
| Waterbirds | Worst-class accuracy [69] | Mixture 2:1 | 81.1 |
| Waterbirds | Worst-group accuracy (uses group ann.) | Mixture 2:1 | 81.1 |
| CelebA | Bias-unsupervised score [60] | Subsetting | 74.1 |
| CelebA | Worst-class accuracy [69] | Mixture 3:1 | 77.6 |
| CelebA | Worst-group accuracy (uses group ann.) | Mixture 3:1 | 77.6 |

*Note:* The CivilComments column for Table 1 is not legible in the provided excerpt; other figures/tables contain additional results but are not numerically extractable here. The paper reports error bars as **±1 standard deviation** across **3 seeds**.

### Discussion & Conclusion
- Finetuned WGA behavior is highly sensitive to “minor” implementation choices: **upsampling/upweighting can collapse**, subsetting can help or harm depending on within-class group structure, and a simple **mixture** strategy often improves stability and WGA.  
- Scaling pretrained models tends to improve WGA, but only when combined with **appropriate class-balancing**; otherwise scaling can look neutral or harmful, helping reconcile conflicting prior narratives.  
- A limitation acknowledged implicitly is that some mechanisms remain not fully explained (e.g., why interpolation affects datasets differently); they point to theory work to explain empirical discrepancies and the role of spectral imbalance.

## Key Contributions
- Demonstrates two practical failure modes in finetuning under spurious correlations: **(i)** catastrophic WGA collapse for **class-balanced upsampling** and **loss upweighting** during long training, and **(ii)** **class-balanced subsetting** can harm WGA when it disproportionately removes a *small minority group within the majority class*.  
- Proposes **mixture balancing**, interpolating subsetting and upsampling, which can **mitigate collapse** and sometimes **outperform** standard balancing approaches; additionally shows viable **model selection without group annotations** via worst-class accuracy and a bias-unsupervised validation score.  
- Reassesses **model scaling** for group robustness in realistic pretrained-finetuning pipelines, showing scaling is **generally beneficial** for WGA with proper balancing, and introduces/uses **group-wise spectral diagnostics** (intra-class spectral norm ratio \(\rho(y)\)) suggesting minority groups exhibit larger conditional spectral norms.

## Potential Relevance
- For hypothesis development on robustness failures, the paper isolates a concrete, testable mechanism: **minority over-repetition over long finetuning** (upsampling/upweighting) can degrade WGA, suggesting interventions around sampling frequency, regularization, or stopping criteria.  
- The **mixture balancing** recipe is a lightweight baseline worth including in any robustness study that avoids group labels, and the **spectral imbalance metrics** (\(\lambda_1^{(g)}\), \(\rho(y)\)) provide a diagnostic lens for connecting representation geometry to within-class group performance gaps.