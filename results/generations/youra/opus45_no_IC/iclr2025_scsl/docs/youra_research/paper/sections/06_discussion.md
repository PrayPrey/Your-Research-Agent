# Discussion

## Interpreting the Detection Signal

The 8× loss difference between minority and majority samples at epoch 5 provides a statistically robust signal for minority detection. However, translating this distributional difference into individual sample identification is constrained by base rate mathematics.

With a 5% minority rate, any method predicting 5% of samples as minority can achieve at most ~33% precision if it perfectly ranks all minority samples above majority samples. Our method achieves this theoretical optimum, indicating the loss signal provides near-perfect ranking information despite modest absolute precision.

This distinction matters for practical applications:
- **Ranking tasks** (e.g., prioritizing samples for manual review): The method is highly effective
- **Classification tasks** (e.g., automatic minority labeling): Precision limits prevent high-confidence individual predictions

The appropriate use case is weighted training (as in JTT) rather than hard minority labeling.

## Magnitude vs. Timing Gap

Our timing hypothesis (H-M2)—that spurious features peak before core features—was not supported. Both peaked at epoch 81 with ImageNet-pretrained weights. This unexpected finding has theoretical implications.

**Why no timing gap?** ImageNet pretraining already encodes both background (spurious) and bird shape (core) features. During finetuning on Waterbirds, both feature types are refined simultaneously rather than learned sequentially. The simplicity bias manifests as a *magnitude* gap (spurious features are encoded ~10% more accurately throughout training) rather than a *temporal* gap.

**Implications**: 
1. Training from scratch may show different dynamics—the timing gap could emerge when features must be learned de novo
2. With pretrained features, early detection via loss magnitude is valid, but peak timing is not a discriminative signal
3. Theoretical models of simplicity bias should account for initialization effects

## Connections to Prior Work

Our finding that simplicity bias manifests as a magnitude gap is consistent with DFR's insight that "ERM learns good features." If representations encode core features with 80%+ accuracy by epoch 5, the problem is not *whether* core features are learned but *how* they are weighted in the classifier.

The 10.7% probe accuracy gap we measure provides the first quantitative characterization of this asymmetry. Prior work (SPARE, LA-SSL) demonstrated that learning speed differs between sample types; we extend this to show that feature encoding quality also differs systematically.

## Limitations

### Single Dataset

Experiments use only Waterbirds. While canonical, Waterbirds has specific properties (95% spurious correlation, 5% minority rate, vision domain) that may not generalize. CelebA and MultiNLI experiments are needed to establish broader applicability.

### Pretrained Features Only

We use ImageNet-pretrained weights, standard practice for Waterbirds benchmarks. Training from scratch may reveal different dynamics (potentially supporting the timing gap hypothesis). The magnitude gap findings are specific to the pretrained setting.

### No Intervention Evaluation

We characterize the detection signal but do not evaluate whether using this signal for weighted training improves worst-group accuracy. Our contribution is analysis, not intervention—though the signal could inform methods like JTT or SPARE.

### Statistical Detection vs. Individual Precision

The Mann-Whitney *p* < 10⁻¹⁴ demonstrates that distributions are separated, but 33% precision means two-thirds of flagged samples are false positives. This is not a failure of the method—it is the mathematical consequence of detecting a 5% minority. Users expecting high-precision individual detection will be disappointed; those seeking a ranking signal will find value.

## Broader Implications

The success of early-epoch loss as a detection signal suggests that training dynamics contain rich information about data substructure. Beyond spurious correlations, this principle could apply to:
- **Data curation**: Identifying annotation errors (persistently high loss)
- **Curriculum learning**: Sequencing samples by difficulty trajectory shape
- **Active learning**: Prioritizing samples with unusual learning dynamics

Our mechanistic analysis—showing that simplicity bias creates consistent feature encoding asymmetry—provides theoretical grounding for such applications.
