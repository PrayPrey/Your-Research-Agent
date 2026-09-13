# Paper Summary: Do ImageNet Classifiers Generalize to ImageNet?
**Authors:** Recht, Roelofs, Schmidt, Shankar (2019)
**arXiv:** 1902.10811
**Venue:** ICML 2019

---

### Abstract & Core Claim
Demonstrates that ImageNet classifiers suffer significant accuracy drops (11–14 pp for top-1 accuracy) when evaluated on a new, independently-collected test set (ImageNet-v2) that follows the original ImageNet collection protocol as closely as possible. The drop is systematic across model families and cannot be explained by distribution shift alone — it reflects benchmark-specific overfitting accumulated via repeated model development against the original test set.

### Methodology
- Collected ImageNet-v2 by re-running the original ILSVRC data collection pipeline (Amazon Mechanical Turk, same categories, same instructions)
- Evaluated 69 trained ImageNet classifiers spanning 7 years of model development on both original ImageNet test set and ImageNet-v2
- Fitted linear regression on original accuracy vs. new-set accuracy; measured the systematic offset
- Decomposed gap into: (a) adaptive overfitting (models tuned against original test set indirectly), (b) distribution shift (small), (c) near-OOD generalization gap

### Key Results
- All 69 models show accuracy drop; drop is NOT explained by dataset shift (confirmed by human accuracy parity)
- Linear relationship between original and new-set accuracy (R² ≈ 0.98) — relative ranking preserved but absolute level drops
- Top models (ResNet-50, VGG variants) show ~11 pp drop; more recent models (EfficientNet-era) show similar proportional drop
- Saturated performance on original test (~91% top-5) does not translate to saturated performance on new set (~83%)

### Experiments & Results
- **Setup:** 69 classifiers × 2 test sets (ImageNet test + ImageNet-v2); 3 data collection variants (MatchedFrequency, Threshold0.7, TopImages)
- **Key finding:** Even MatchedFrequency variant (most conservative collection) shows 11.7 pp drop for top-1
- **Human baseline:** Human accuracy gap between the two sets is ≈ 1–2 pp (far smaller than model gaps)
- **Implication:** Benchmark saturation is a real empirical phenomenon, not merely Goodhart's Law speculation

### Relevance to Gap 1
- Provides the foundational empirical evidence that benchmark overfitting is real and measurable
- Methodology (collect independent test set, measure accuracy gap) is not directly reproducible for NLP benchmarks (cannot re-collect GLUE)
- **Key gap:** Recht et al. require a NEW test set; our research aims to detect saturation from EXISTING leaderboard timeseries WITHOUT a new test set
- The logistic-curve approach (fitting to temporal score progression) is not used here — Recht et al. use a cross-sectional snapshot, not temporal analysis

### Potential Relevance
Provides: empirical baseline for accuracy-gap magnitude expected under benchmark overfitting; statistical framing (linear regression on accuracy pairs); evidence that saturation is detectable from accuracy gap metrics.
Does NOT provide: temporal detection method; API-based automated approach; benchmark-agnostic scoring.
