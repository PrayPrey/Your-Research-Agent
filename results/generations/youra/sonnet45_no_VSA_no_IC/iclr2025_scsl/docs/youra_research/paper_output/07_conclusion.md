# 7. Conclusion

Gradient attribution methods fail to detect unknown spurious correlations [Adebayo et al., 2022], and existing robust learning methods require group annotations (GroupDRO) or operate in two stages (JTT). We proposed extending gradient abnormality detection (GAIA [Chen et al., 2023]) from distribution shift to subpopulation shift, combined with spatial gradient regularization for annotation-free spurious mitigation.

## 7.1 Contributions Summary

**Validated Contributions (Synthetic/PoC):**

1. **Detection Methodology (h-e1):** Gradient abnormality pipeline correctly differentiates minority (high gradient scattering) vs majority (low scattering) patterns when controlled synthetic gradients exhibit known near-zero rate differences (GAIA-Z divergence 0.30, p<0.0001, Cohen's d=198.75). Pipeline correctness validated via 7/7 unit tests and synthetic experiments.

2. **Causal Mechanism (h-m-integrated):** Synthetic validation supports 4-step causal chain (spurious learning → minority conflict → gradient scattering → GAIA detection). Background augmentation test shows 39.4% GAIA-Z reduction (p<0.001, Cohen's d=2.96), validating spurious conflict causality (Step 2). Correlation analysis demonstrates strong association (|ρ|=0.975, p<0.001) between GAIA divergence and worst-group accuracy.

3. **Mitigation Framework (h-m-mitigate):** Spatial gradient regularization methodology improves WGA by +23 percentage points on MNIST+Color toy dataset (2-epoch PoC: 78% vs 55% ERM baseline) without catastrophic average accuracy drop (95% vs 94%). Methodology validated; full statistical testing (5-seed, 50-epoch) deferred.

4. **Unified Approach:** First framework using gradient space for both detection (GAIA-Z abnormality) and mitigation (spatial regularization), complementing embedding-based methods (SCER) and operating in single training stage (unlike JTT's two-stage approach).

**Contribution Tier:**  
**Tier 3 — Methodology Validated.** Synthetic experiments prove pipeline correctness (code executes without errors, statistical tests accurate, gate logic sound). Empirical claims (real Waterbirds minority gradients exhibit abnormality, real WGA improvement) remain unvalidated, pending infrastructure resolution (PyTorch 2.1+ for H100 sm_90 support or CPU training ~70-90 GPU-hours).

## 7.2 Limitations

**Primary Limitations:**
- **L1 (Synthetic Only):** Detection and mechanism validation (h-e1, h-m-integrated) use controlled synthetic data. Real gradient extraction requires GPU compatibility fix (~30-50h CPU training fallback).
- **L2 (PoC Only):** Mitigation validated on MNIST toy dataset (simple color spurious) via smoke test (1 seed, 2 epochs). Waterbirds generalization (complex background spurious) and statistical rigor (5-seed bootstrap) deferred (~44 GPU hours total).
- **L3 (No SOTA Comparison):** Cannot claim to beat SCER (~90% WGA estimated) without GroupDRO baseline or SCER code reproduction (code unavailable).

**Addressable via:**
1. PyTorch 2.1+ upgrade (sm_90 support) or CPU parallel training
2. Full MNIST (5 seeds × 50 epochs, 4 hours) + Waterbirds (hyperparameter search + baselines, 40 hours)
3. GroupDRO comparison (official implementation available, 294 GitHub stars)

## 7.3 Future Work

**Immediate (Address Current Limitations):**

**FW1: Real Waterbirds Detection Validation**  
Upgrade PyTorch to 2.1+ (verify sm_90 support) or execute CPU training (~30h for h-e1, ~50h for h-m-integrated). Expected outcome: if GAIA divergence ≥0.2 on real gradients → detection claim validated. Fallback: if divergence <0.1 → gradient abnormality hypothesis false, pivot to detection-only or abandon approach.

**FW2: Full MNIST Experiment**  
Execute 5 seeds × 50 epochs on full MNIST+Color (~4 GPU hours). Expected outcome: confirm WGA improvement ≥10% with bootstrap significance (p<0.05). If improvement <5% → smoke test was outlier, methodology weaker than expected.

**FW3: Waterbirds Full Experiment + Baselines**  
Hyperparameter search (3×3 grid over λ_init, percentile) + 3 methods (ERM, GroupDRO, Spatial Reg) × 5 seeds × 300 epochs (~40 GPU hours). Expected outcome: if WGA ≥GroupDRO+5% → Tier 2 competitive method. If WGA <GroupDRO → detection-only contribution (Tier 3).

**Extensions (Build on Validated Methodology):**

**FW4: Multi-Dataset Generalization**  
Validate gradient abnormality on CelebA (hair color spurious), UrbanCars (co-occurrence), medical imaging (demographic bias). Research question: does GAIA-Z generalize to non-background spurious features? Hypothesis: divergence ≥0.15 on CelebA. Gate: if 2/3 datasets pass → general approach.

**FW5: Joint Gradient + Embedding Regularization**  
Combine spatial gradient regularization (ours) with SCER embedding regularization [Park et al., 2025]. Method: L_total = L_CE + λ_grad × L_spatial + λ_emb × L_SCER. Hypothesis: joint intervention outperforms individual methods by ≥3% WGA (complementary intervention points address different failure modes).

**FW6: Automatic Percentile Selection**  
Replace fixed percentile threshold (75th) with adaptive selection via validation WGA feedback. Method: grid search → RL-based optimization. Hypothesis: auto-selected percentile achieves WGA within 2% of oracle (manual grid search optimum), eliminating hyperparameter tuning.

**Theoretical Deepening:**

**FW7: Spurious Complexity vs Effectiveness Analysis**  
Controlled complexity sweep: MNIST+Color (simple) → MNIST+Texture → Waterbirds (complex). Hypothesis: gradient abnormality effectiveness inversely correlates with spurious feature complexity. Defines applicability boundary (simple spurious only vs general).

**FW8: Minority Accuracy Threshold Sensitivity (A1)**  
Experiment with varying minority classification accuracy (50%-70% via controlled correlation rates). Hypothesis: GradCAM spatial masking degrades gracefully (WGA improvement 10%→5% as accuracy drops 70%→55%). Defines robustness boundary for spatial masking approach.

## 7.4 Closing Remarks

We extended gradient abnormality detection (GAIA) from out-of-distribution samples to minority groups within the in-distribution, and proposed spatial gradient regularization to suppress spurious reliance without group annotations. Synthetic validation demonstrates methodology correctness: the detection pipeline differentiates gradient patterns when abnormality exists (GAIA-Z divergence 0.30, p<0.0001), background augmentation causally reduces abnormality (39.4% reduction, p<0.001), and spatial regularization improves toy-dataset WGA substantially (+23pp in MNIST PoC). These results validate the **approach's plausibility** (methodology works in controlled settings) but leave the **empirical question** unanswered: do real Waterbirds minority gradients exhibit this abnormality mechanism? Does spatial regularization improve real-world WGA?

Answering these questions requires infrastructure resolution (PyTorch 2.1+ upgrade for H100 sm_90 support or ~70-90 GPU-hours CPU training) and full-scale experiments. Until then, we position this work as a **methodology contribution** (Tier 3: pipeline validated, mechanism plausible) with a clear path to empirical validation (Tier 2: real experiments pending). Our gradient-based approach complements embedding methods (SCER), operates in a single training stage (unlike JTT), and provides a unified detection-mitigation framework — advancing spurious correlation research from annotation-dependent (GroupDRO) toward annotation-free robust learning.

**The gradient abnormality hypothesis:** minority samples exhibit gradient scattering when spurious shortcuts conflict with core features. Synthetic validation shows this mechanism CAN work (pipeline correct, causality test passes). Next: does real data exhibit this mechanism? That answer awaits Waterbirds.

---

**Code and Data Availability:** Implementation released at [anonymized for review], including synthetic validation scripts (h-e1, h-m-integrated), MNIST PoC (h-m-mitigate), unit tests, and configurations. Real Waterbirds code released upon infrastructure resolution. Datasets: Waterbirds via WILDS (pip install wilds==2.0.0), MNIST via torchvision.
